"""Synthetic public-operation checks for preserved neutral coding references."""
import hashlib
import json
from tests.support import WorkspaceTestCase


SHEET = "# Syntax reference\n\n`len(value)` returns the number of items.\n"


class SyntaxReferenceTests(WorkspaceTestCase):
    def content(self):
        return {p.name: p.read_bytes() for p in (self.root / 'assignment/mailbox').iterdir()}

    def coding_payload(self):
        return dict(self.packet_payload(), coding=True, syntax_cheatsheet=SHEET)

    def test_coding_sheet_survives_combining_budget_and_resume(self):
        self.prepare_plan()
        payload = self.coding_payload()
        # Only two uploads fit: the source context must move into lesson.txt,
        # while the neutral reference remains a distinct attachment.
        payload['upload_profile'] = {'max_files': 2}
        state = self.operation('packet-issue', payload)
        pid = state['active_packet']
        packet = state['packets'][pid]
        folder = self.root / 'assignment' / packet['path']
        expected = {p.relative_to(folder).as_posix(): p.read_bytes()
                    for p in folder.rglob('*') if p.is_file()}
        contents = self.content()
        self.assertEqual(set(contents), {'lesson.txt', 'syntax-cheatsheet.md'})
        self.assertEqual(contents['syntax-cheatsheet.md'], SHEET.encode())
        self.assertIn(b'Synthetic worked example', contents['lesson.txt'])
        tutor = expected['tutor.md'].decode()
        self.assertLess(tutor.index('Permitted syntax reference'), tutor.index('Select the chat role'))
        self.assertIn('Neutral lookup does not count as assistance', tutor)
        manifest = json.loads(expected['manifest.json'])
        reference = next(e for e in manifest['included'] if e.get('role') == 'syntax-reference')
        self.assertEqual(reference['sha256'], hashlib.sha256(SHEET.encode()).hexdigest())
        (self.root / 'assignment/mailbox/syntax-cheatsheet.md').write_text('Mailbox edit')
        self.operation('packet-resume', {'packet_id': pid})
        self.assertEqual(self.content(), contents)
        self.assertEqual(expected, {p.relative_to(folder).as_posix(): p.read_bytes()
                                   for p in folder.rglob('*') if p.is_file()})
        # A smaller budget fails before replacing the current packet or mailbox.
        replacement = dict(payload, packet_id=pid, decision_record='Synthetic replacement',
                           upload_profile={'max_files': 1})
        self.operation('packet-replace', replacement, ok=False)
        self.assertEqual(self.content(), contents)
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['active_packet'], pid)

    def test_invalid_reference_fails_without_issuing_or_changing_mailbox(self):
        self.prepare_plan()
        state = self.operation('packet-issue', self.coding_payload())
        pid = state['active_packet']
        before = self.content()
        for changes in ({'coding': True}, {'coding': 'yes'},
                        {'coding': True, 'syntax_cheatsheet': '  '},
                        {'coding': False, 'syntax_cheatsheet': SHEET}):
            payload = dict(self.packet_payload(), packet_id=pid,
                           decision_record='Synthetic replacement', **changes)
            self.operation('packet-replace', payload, ok=False)
            self.assertEqual(before, self.content())
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['active_packet'], pid)

    def test_noncoding_and_legacy_packets_omit_reference(self):
        self.prepare_plan()
        for changes in ({}, {'coding': False}):
            state = self.operation('packet-issue', dict(self.packet_payload(), **changes))
            self.assertNotIn('syntax-cheatsheet.md', self.content())
            self.operation('packet-abandon', {'packet_id': state['active_packet'],
                                            'decision_record': 'Synthetic test completed'})
