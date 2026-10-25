"""Flat, bounded upload views derived from preserved packet snapshots."""
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import uuid


DEFAULT_PROFILE = {
    'target_chatbot': 'ChatGPT',
    'max_files': 10,
    'max_file_bytes': 20 * 1024 * 1024,
    'max_text_bytes': 2_000_000,
}
TEXT_TYPES = {'.txt', '.md', '.json', '.py', '.ipynb', '.obj', '.csv', '.tsv',
              '.glsl', '.vert', '.frag', '.html', '.css', '.js', '.tex', '.yaml', '.yml'}
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tif', '.tiff'}


def profile(state, payload):
    chosen = dict(DEFAULT_PROFILE)
    for override in (state.get('upload_profile', {}), payload.get('upload_profile', {})):
        if not isinstance(override, dict):
            raise ValueError('Upload profile must be an object')
        chosen.update(override)
    if not isinstance(chosen['target_chatbot'], str) or not chosen['target_chatbot'].strip():
        raise ValueError('Upload profile requires a target chatbot')
    for key in ('max_files', 'max_file_bytes', 'max_text_bytes'):
        if type(chosen[key]) is not int or chosen[key] <= 0:
            raise ValueError('Upload profile requires positive integer ' + key)
    chosen['max_text_bytes'] = min(chosen['max_text_bytes'], chosen['max_file_bytes'])
    return chosen


def text_parts(content, limit):
    raw = content.encode('utf-8')
    parts = []
    while raw:
        end = min(limit, len(raw))
        while end:
            try:
                raw[:end].decode('utf-8')
                break
            except UnicodeDecodeError:
                end -= 1
        if not end:
            raise ValueError('Upload text budget cannot hold one UTF-8 character')
        parts.append(raw[:end])
        raw = raw[end:]
    return parts


def merge_visuals(entries):
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import (DecodedStreamObject, DictionaryObject, NameObject,
                                   NumberObject)
    except ImportError as error:
        raise ValueError('Combining PDFs requires pypdf; install it with python -m pip install pypdf') from error
    writer = PdfWriter()
    locations = []
    for entry, content in entries:
        start = len(writer.pages) + 1
        if Path(entry['path']).suffix.lower() == '.pdf':
            reader = PdfReader(BytesIO(content))
            if reader.is_encrypted:
                raise ValueError('Decrypt selected PDF before packaging: ' + entry['source'])
            if not reader.pages:
                raise ValueError('Selected PDF has no pages: ' + entry['source'])
            writer.append(reader, outline_item=entry['source'])
        else:
            try:
                from PIL import Image, ImageOps
            except ImportError as error:
                raise ValueError('Combining images requires Pillow; install it with python -m pip install Pillow') from error
            with Image.open(BytesIO(content)) as original:
                if getattr(original, 'n_frames', 1) != 1:
                    raise ValueError('Prepare a complete derivative for animated/multipage image: ' + entry['source'])
                image = ImageOps.exif_transpose(original).convert('RGBA')
                background = Image.new('RGBA', image.size, 'white')
                image = Image.alpha_composite(background, image).convert('RGB')
            width, height = image.size
            page_width = max(width, 300)
            page = writer.add_blank_page(width=page_width, height=height + 28)
            stream = DecodedStreamObject()
            stream.set_data(image.tobytes())
            stream.update({NameObject('/Type'): NameObject('/XObject'),
                           NameObject('/Subtype'): NameObject('/Image'),
                           NameObject('/Width'): NumberObject(width),
                           NameObject('/Height'): NumberObject(height),
                           NameObject('/ColorSpace'): NameObject('/DeviceRGB'),
                           NameObject('/BitsPerComponent'): NumberObject(8)})
            font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                     NameObject('/Subtype'): NameObject('/Type1'),
                                     NameObject('/BaseFont'): NameObject('/Helvetica')})
            page[NameObject('/Resources')] = DictionaryObject({
                NameObject('/XObject'): DictionaryObject({NameObject('/Im0'): writer._add_object(stream.flate_encode())}),
                NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
            label = entry['source'].encode('ascii', 'replace').decode()[:int((page_width - 12) / 6)]
            label = label.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            drawing = DecodedStreamObject()
            drawing.set_data((f'q {width} 0 0 {height} {(page_width - width) / 2} 0 cm /Im0 Do Q\n'
                              f'BT /F1 10 Tf 6 {height + 9} Td ({label}) Tj ET\n').encode('ascii'))
            page[NameObject('/Contents')] = writer._add_object(drawing)
            writer.add_outline_item(entry['source'], start - 1)
        locations.append({'source': entry['source'], 'snapshot_path': entry['path'],
                          'upload_file': 'visual-context.pdf', 'pages': [start, len(writer.pages)]})
    output = BytesIO()
    writer.write(output)
    return output.getvalue(), locations


def build(packet, snapshot, chosen):
    """Build everything in memory so an invalid replacement leaves the mailbox intact."""
    manifest = json.loads(snapshot['manifest.json'])
    sections, attachments, locations = [], {}, []
    visuals = []
    for index, entry in enumerate(manifest['included']):
        content = snapshot[entry['path']]
        if len(content) != entry['bytes'] or hashlib.sha256(content).hexdigest() != entry['sha256']:
            raise ValueError('Packet snapshot digest mismatch: ' + entry['path'])
        suffix = Path(entry['path']).suffix.lower()
        if suffix in TEXT_TYPES:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError as error:
                raise ValueError('Prepare a UTF-8 derivative for: ' + entry['source']) from error
            sections.append('\n\n=== BEGIN SOURCE ' + json.dumps(entry, ensure_ascii=False) + ' ===\n'
                            + text + '\n=== END SOURCE ' + entry['path'] + ' ===\n')
        elif suffix == '.pdf' or suffix in IMAGE_TYPES:
            visuals.append((entry, content))
        else:
            name = f'attachment-{index + 1:03d}' + suffix
            attachments[name] = content
            locations.append({'source': entry['source'], 'snapshot_path': entry['path'], 'upload_file': name})
    sources = ''.join(sections)
    source_files = {}
    for index, part in enumerate(text_parts(sources, chosen['max_text_bytes']), 1):
        source_files[f'source-context-{index:03d}.txt'] = part
    # Reserve one attachment for the tutor, embedded manifest and report contract.
    if len(attachments) + len(source_files) + len(visuals) + 1 > chosen['max_files'] and visuals:
        merged, mapped = merge_visuals(visuals)
        attachments['visual-context.pdf'] = merged
        locations.extend(mapped)
    else:
        for index, (entry, content) in enumerate(visuals, 1):
            name = f'visual-{index:03d}' + Path(entry['path']).suffix.lower()
            attachments[name] = content
            locations.append({'source': entry['source'], 'snapshot_path': entry['path'], 'upload_file': name})
    layout = {'profile': chosen, 'text_files_in_order': list(source_files),
              'visual_and_binary_sources': locations,
              'transformations': ['UTF-8 sources concatenated verbatim with source boundaries; original bytes and digests remain in the snapshot.',
                                  'Merged PDF pages retain PDF content. Images, when merged, retain full pixel dimensions, use lossless compression, and flatten transparency onto white.']}
    lesson = ('# START THIS LESSON\n\nRead this file and all attached source/visual context, then immediately begin the lesson below, '
              'one question at a time. All required instructions and reporting forms are embedded here. '
              'The learner only needs to attach the mailbox files and send Go. '
              'Snapshot paths in the manifest are provenance references, not additional uploads. '
              'Read source-context files in numeric order; boundaries can continue into the next file.\n\n'
              '## UPLOAD LAYOUT\n' + json.dumps(layout, indent=2, ensure_ascii=False) + '\n')
    for name in ('tutor.md', 'report-template.json', 'report-contract.json', 'manifest.json'):
        lesson += '\n=== BEGIN ' + name + ' ===\n' + snapshot[name].decode('utf-8') + '\n=== END ' + name + ' ===\n'
    if chosen['max_files'] <= 2 and source_files:
        lesson += '\n## SOURCE CONTEXT (inlined to fit the attachment budget)\n' + sources
        source_files = {}
        lesson = lesson.replace(json.dumps(layout, indent=2, ensure_ascii=False),
                                json.dumps(dict(layout, text_files_in_order=['lesson.txt (embedded)']), indent=2, ensure_ascii=False))
    outputs = dict({'lesson.txt': lesson.encode('utf-8')}, **source_files, **attachments)
    if len(outputs) > chosen['max_files']:
        raise ValueError(f'Packet needs {len(outputs)} uploads after combining; budget is {chosen["max_files"]}. Reduce context or combine remaining formats before issuance.')
    for name, content in outputs.items():
        limit = chosen['max_text_bytes'] if name.endswith('.txt') else chosen['max_file_bytes']
        if len(content) > limit:
            raise ValueError(f'Combined upload {name} exceeds its {limit}-byte budget; reduce/split context before issuance')
    return outputs


def preserve(root, packet, outputs, chosen, safe_path):
    relative = 'uploads/' + packet['packet_id']
    folder = safe_path(root, relative)
    if folder.exists():
        raise ValueError('Preserved upload view already exists')
    destinations = [(safe_path(root, relative + '/' + name), content) for name, content in outputs.items()]
    for destination, content in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    packet.update(upload_path=relative, upload_profile=chosen,
                  upload_files=[{'name': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
                                for name, content in outputs.items()],
                  upload_total_bytes=sum(map(len, outputs.values())))


def mailbox(root, packet, safe_path):
    outputs = {}
    if packet:
        for entry in packet['upload_files']:
            name = entry['name']
            if Path(name).name != name or '/' in name or '\\' in name:
                raise ValueError('Mailbox upload filename must be flat')
            content = safe_path(root, packet['upload_path'] + '/' + name).read_bytes()
            if len(content) != entry['bytes'] or hashlib.sha256(content).hexdigest() != entry['sha256']:
                raise ValueError('Preserved upload digest mismatch: ' + name)
            outputs[name] = content
    # Check the lexical mailbox too: replacing a symlink/junction is not a refresh.
    lexical = root / 'mailbox'
    if lexical.is_symlink() or getattr(lexical, 'is_junction', lambda: False)():
        raise ValueError('Mailbox must be a real workspace directory')
    target = safe_path(root, 'mailbox')
    if target.exists() and not target.is_dir():
        raise ValueError('Mailbox must be a directory')
    token = str(uuid.uuid4())
    stage = safe_path(root, '.invo/mailbox-stage-' + token)
    backup = safe_path(root, '.invo/mailbox-history/' + token)
    pointer = safe_path(root, '.invo/mailbox.json')
    stage.mkdir(parents=True)
    for name, content in outputs.items():
        safe_path(root, str(stage.relative_to(root) / name)).write_bytes(content)
    # Move the whole old directory without traversing or deleting its contents.
    if target.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        os.replace(target, backup)
    try:
        os.replace(stage, target)
    except OSError:
        if backup.exists():
            os.replace(backup, target)
        raise
    pointer.write_text(json.dumps({'packet_id': packet['packet_id'], 'upload_path': packet['upload_path'],
                                   'files': packet['upload_files']} if packet else None, indent=2) + '\n', encoding='utf-8')
