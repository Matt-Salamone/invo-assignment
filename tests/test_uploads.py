import hashlib
import importlib.util
from io import BytesIO
import json
import os
from pathlib import Path
import unittest
from tests.support import WorkspaceTestCase


class UploadTests(WorkspaceTestCase):
    def mailbox_bytes(self):
        folder = self.root / 'assignment/mailbox'
        self.assertTrue(folder.is_dir())
        self.assertTrue(all(path.is_file() for path in folder.iterdir()))
        return {path.name: path.read_bytes() for path in folder.iterdir()}

    def add_context(self, payload, name, content):
        path = self.root / 'assignment/materials' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        payload['context'].append({'path': 'materials/' + name, 'reference': 'Synthetic source ' + name})
        return path

    def test_mailbox_is_flat_complete_and_replaces_old_contents_without_loss(self):
        self.prepare_plan()
        old = self.root / 'assignment/mailbox/old/note.txt'
        old.parent.mkdir(parents=True)
        old.write_text('Original material to preserve')
        state = self.operation('packet-issue', self.packet_payload())
        packet = state['packets'][state['active_packet']]
        contents = self.mailbox_bytes()
        self.assertLessEqual(len(contents), 10)
        self.assertNotIn('current.json', contents)
        self.assertIn(b'Synthetic worked example', b'\n'.join(contents.values()))
        self.assertIn(b'Explain required example', contents['lesson.txt'])
        self.assertIn(packet['packet_id'].encode(), contents['lesson.txt'])
        self.assertIn(b'learner_response', contents['lesson.txt'])
        self.assertEqual(set(contents), {entry['name'] for entry in packet['upload_files']})
        for entry in packet['upload_files']:
            self.assertEqual(hashlib.sha256(contents[entry['name']]).hexdigest(), entry['sha256'])
        pointer = json.loads((self.root / 'assignment/.invo/mailbox.json').read_text())
        self.assertEqual(pointer['packet_id'], packet['packet_id'])
        backups = list((self.root / 'assignment/.invo/mailbox-history').glob('*/old/note.txt'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'Original material to preserve')

    def test_many_text_sources_are_combined_without_omission(self):
        self.prepare_plan()
        payload = self.packet_payload()
        originals = {}
        for index in range(20):
            content = f'Source {index}: denominator counts equal parts; café.\r\n'.encode('utf-8')
            path = self.add_context(payload, f'lecture-{index}.txt', content)
            originals[path] = content
        state = self.operation('packet-issue', payload)
        packet = state['packets'][state['active_packet']]
        content = b'\n'.join(self.mailbox_bytes().values())
        for path, original in originals.items():
            self.assertIn(original, content)
            self.assertEqual(path.read_bytes(), original)
            self.assertIn(path.name.encode(), content)
        self.assertLessEqual(len(packet['upload_files']), 3)

    def test_ten_file_budget_accepts_ten_and_rejects_eleven_unmergeable_uploads(self):
        self.prepare_plan()
        payload = self.packet_payload()
        for index in range(8):
            self.add_context(payload, f'data-{index}.bin', b'\x00\xff')
        state = self.operation('packet-issue', payload)
        expected = self.mailbox_bytes()
        self.assertEqual(len(expected), 10)
        self.assertEqual(state['upload_profile']['max_files'], 10)
        self.add_context(payload, 'data-8.bin', b'\x00\xff')
        payload.update(packet_id=state['active_packet'], decision_record='Student requests replacement')
        self.operation('packet-replace', payload, ok=False)
        self.assertEqual(self.mailbox_bytes(), expected)

    def test_resume_restores_same_view_despite_working_edits_and_stale_mailbox(self):
        self.prepare_plan()
        state = self.operation('packet-issue', self.packet_payload())
        packet_id = state['active_packet']
        expected = self.mailbox_bytes()
        (self.root / 'assignment/mailbox/stale.txt').write_text('Old upload')
        (self.root / 'assignment/solution/answer.txt').write_text('Later working edit')
        resumed = self.operation('packet-resume', {'packet_id': packet_id})
        self.assertEqual(resumed['active_packet'], packet_id)
        self.assertEqual(self.mailbox_bytes(), expected)
        self.assertEqual(len(resumed['packets']), 1)

    def test_legacy_resume_keeps_snapshot_and_identifiers(self):
        self.prepare_plan()
        state = self.operation('packet-issue', self.packet_payload())
        packet = state['packets'][state['active_packet']]
        snapshot = self.root / 'assignment' / packet['path']
        original = {str(p.relative_to(snapshot)): p.read_bytes() for p in snapshot.rglob('*') if p.is_file()}
        upload = self.root / 'assignment' / packet['upload_path']
        upload.rename(upload.with_name(upload.name + '-previous'))
        for key in ('upload_path', 'upload_profile', 'upload_files', 'upload_total_bytes'):
            packet.pop(key)
        (self.root / 'assignment/.invo/state.json').write_text(json.dumps(state))
        resumed = self.operation('packet-resume', {'packet_id': state['active_packet']})
        self.assertEqual(resumed['active_packet'], packet['packet_id'])
        self.assertEqual(original, {str(p.relative_to(snapshot)): p.read_bytes() for p in snapshot.rglob('*') if p.is_file()})
        self.assertLessEqual(len(self.mailbox_bytes()), 3)

    def test_budget_failure_keeps_active_packet_mailbox_and_snapshots(self):
        self.prepare_plan()
        state = self.operation('packet-issue', self.packet_payload())
        expected = self.mailbox_bytes()
        snapshots = list((self.root / 'assignment/packets').iterdir())
        payload = dict(self.packet_payload(), packet_id=state['active_packet'],
                       decision_record='Student requests a new packet', upload_profile={'max_files': 3})
        for index in range(4):
            self.add_context(payload, f'opaque-{index}.bin', b'\x00\xff')
        error = self.operation('packet-replace', payload, ok=False)
        self.assertIn('budget', error)
        current = self.run_cli(self.root / 'assignment', 'status')
        self.assertEqual(current['active_packet'], state['active_packet'])
        self.assertEqual(self.mailbox_bytes(), expected)
        self.assertEqual(list((self.root / 'assignment/packets').iterdir()), snapshots)

    def test_invalid_and_oversize_budgets_fail_before_issuance(self):
        self.prepare_plan()
        payload = self.packet_payload()
        for setting in ({'max_files': 0}, {'max_files': True}, {'max_text_bytes': 100}, {'max_file_bytes': -1}):
            self.operation('packet-issue', dict(payload, upload_profile=setting), ok=False)
        state = self.run_cli(self.root / 'assignment', 'status')
        self.assertIsNone(state.get('active_packet'))
        self.assertFalse((self.root / 'assignment/packets').exists())

    def test_one_file_text_profile_and_abandon_leave_no_mailbox_extras(self):
        self.prepare_plan()
        payload = dict(self.packet_payload(), upload_profile={'max_files': 1})
        state = self.operation('packet-issue', payload)
        contents = self.mailbox_bytes()
        self.assertEqual(set(contents), {'lesson.txt'})
        self.assertIn(b'Synthetic worked example', contents['lesson.txt'])
        self.operation('packet-abandon', {'packet_id': state['active_packet'], 'decision_record': 'Student stops'})
        self.assertEqual(self.mailbox_bytes(), {})
        self.assertIsNone(json.loads((self.root / 'assignment/.invo/mailbox.json').read_text()))

    def test_corrupt_upload_does_not_overwrite_current_mailbox(self):
        self.prepare_plan()
        state = self.operation('packet-issue', self.packet_payload())
        packet = state['packets'][state['active_packet']]
        expected = self.mailbox_bytes()
        (self.root / 'assignment' / packet['upload_path'] / 'lesson.txt').write_text('Tampered')
        self.operation('packet-resume', {'packet_id': state['active_packet']}, ok=False)
        self.assertEqual(self.mailbox_bytes(), expected)

    @unittest.skipUnless(importlib.util.find_spec('pypdf'), 'Optional pypdf is unavailable')
    def test_many_pdfs_merge_with_page_content_order_and_references(self):
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
        self.prepare_plan()
        payload = dict(self.packet_payload(), upload_profile={'max_files': 3})
        originals = []
        for index in range(4):
            writer = PdfWriter()
            page = writer.add_blank_page(width=200 + index, height=300)
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({
                NameObject('/F1'): DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                    NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})})})
            stream = DecodedStreamObject()
            stream.set_data(f'BT /F1 12 Tf 10 100 Td (Critical rule {index}) Tj ET'.encode())
            page[NameObject('/Contents')] = writer._add_object(stream)
            data = BytesIO()
            writer.write(data)
            originals.append((self.add_context(payload, f'lecture-{index}.pdf', data.getvalue()), data.getvalue()))
        state = self.operation('packet-issue', payload)
        contents = self.mailbox_bytes()
        self.assertEqual(len(contents), 3)
        reader = PdfReader(BytesIO(contents['visual-context.pdf']))
        self.assertEqual(len(reader.pages), 4)
        for index, page in enumerate(reader.pages):
            self.assertIn(f'Critical rule {index}', page.extract_text())
            self.assertEqual(float(page.mediabox.width), 200 + index)
            self.assertIn(f'lecture-{index}.pdf'.encode(), contents['lesson.txt'])
        for path, raw in originals:
            self.assertEqual(path.read_bytes(), raw)

    @unittest.skipUnless(importlib.util.find_spec('pypdf') and importlib.util.find_spec('PIL'), 'Optional PDF/image tools unavailable')
    def test_combined_images_retain_full_pixels_and_source_labels(self):
        from PIL import Image
        from pypdf import PdfReader
        self.prepare_plan()
        payload = dict(self.packet_payload(), upload_profile={'max_files': 3})
        for index in range(4):
            image = Image.new('RGB', (40 + index, 30), (index * 60, 100, 200))
            output = BytesIO()
            image.save(output, format='PNG')
            self.add_context(payload, f'figure-{index}.png', output.getvalue())
        self.operation('packet-issue', payload)
        contents = self.mailbox_bytes()
        self.assertEqual(len(contents), 3)
        reader = PdfReader(BytesIO(contents['visual-context.pdf']))
        self.assertEqual(len(reader.pages), 4)
        for index, page in enumerate(reader.pages):
            image = list(page.images)[0].image
            self.assertEqual(image.size, (40 + index, 30))
            self.assertEqual(image.getpixel((0, 0)), (index * 60, 100, 200))
            self.assertIn(f'figure-{index}.png', page.extract_text())

    def test_symlink_mailbox_cannot_redirect_refresh_outside_workspace(self):
        self.prepare_plan()
        outside = self.root / 'outside'
        outside.mkdir()
        marker = outside / 'keep.txt'
        marker.write_text('Keep')
        link = self.root / 'assignment/mailbox'
        try:
            os.symlink(outside, link, target_is_directory=True)
        except OSError:
            self.skipTest('Directory symlinks unavailable')
        self.operation('packet-issue', self.packet_payload(), ok=False)
        self.assertEqual(marker.read_text(), 'Keep')
