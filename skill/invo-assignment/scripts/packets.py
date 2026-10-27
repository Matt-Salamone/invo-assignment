"""Preserved packet snapshots and explicit outstanding-packet lifecycle."""
import hashlib
import json
import uuid
from eligibility import context_ready
from uploads import build, mailbox, preserve, profile


def operation(root, state, command, payload, safe_path, save_state):
    packets = state.setdefault('packets', {})
    active = state.get('active_packet')
    if command in ('packet-resume', 'packet-abandon', 'packet-replace'):
        if not active or payload.get('packet_id') != active:
            raise ValueError('Operation must identify the outstanding packet')
        if command == 'packet-resume':
            active_lesson = next((lesson for lesson in state.get('plan', {}).get('lessons', []) if lesson['id'] == packets[active]['lesson_id']), None)
            if packets[active].get('review_required') or not active_lesson or not context_ready(state, active_lesson):
                raise ValueError('Outstanding packet requires review before continuation')
            packet = packets[active]
            if not packet.get('upload_files'):
                chosen = profile(state, payload)
                names = ['tutor.md', 'report-template.json', 'report-contract.json', 'manifest.json']
                names.extend(entry['path'] for entry in packet['included'])
                snapshot = {name: safe_path(root, packet['path'] + '/' + name).read_bytes() for name in names}
                outputs = build(packet, snapshot, chosen)
                preserve(root, packet, outputs, chosen, safe_path)
                state['upload_profile'] = chosen
            mailbox(root, packet, safe_path)
            save_state(root, state)
            return state
        if not isinstance(payload.get('decision_record'), str) or not payload['decision_record'].strip():
            raise ValueError('Replacement or abandonment needs an explicit student decision')
        if command == 'packet-abandon':
            packets[active].update(status='abandoned', decision_record=payload['decision_record'])
            state.update(active_packet=None, next_action='request-lesson')
            mailbox(root, None, safe_path)
            save_state(root, state)
            return state
    elif active:
        raise ValueError('Resume, replace or abandon the outstanding packet first')
    plan = state.get('plan', {})
    if plan.get('status') != 'approved' or not state.get('solution'):
        raise ValueError('Packet issuance requires approved plan and worked solution')
    if not isinstance(payload.get('request_record'), str) or not payload['request_record'].strip():
        raise ValueError('Issue a packet only on an actual student request')
    lesson = next((lesson for lesson in plan['lessons'] if lesson['id'] == payload.get('lesson_id')), None)
    if not lesson:
        raise ValueError('Unknown lesson')
    if not context_ready(state, lesson):
        raise ValueError('Review changed lesson context before issuing a packet')
    assessment = payload.get('size_assessment')
    if not isinstance(assessment, dict) or any(not isinstance(assessment.get(key), str) or not assessment[key].strip() for key in ('basis', 'relevance', 'uncertainty')) or not isinstance(assessment.get('limitations'), list):
        raise ValueError('Record size/relevance basis, uncertainty and limitations')
    if not isinstance(payload.get('assignment_context'), str) or not payload['assignment_context'].strip() or not isinstance(payload.get('context'), list):
        raise ValueError('A self-contained packet needs assignment context and selected source list')
    pid = str(uuid.uuid4())
    relative = 'packets/' + pid
    folder = safe_path(root, relative)
    if folder.exists():
        raise ValueError('Packet snapshot already exists')
    metadata = {'assignment_id': state['assignment_id'], 'lesson_id': lesson['id'], 'packet_id': pid, 'contract_version': 1, 'solution_revision': state['solution']['revision']}
    if any(not isinstance(item, dict) for item in payload['context']):
        raise ValueError('Selected source context needs path and provenance reference')
    selected = list(state['solution']['artifacts']) + payload['context']
    included = []
    outputs = {}
    for index, selection in enumerate(selected):
        # Context entries carry page/slide provenance; solution files carry their Git revision.
        original = selection if isinstance(selection, str) else selection.get('path')
        reference = ('Solution revision ' + metadata['solution_revision']) if isinstance(selection, str) else selection.get('reference')
        if not original or not reference:
            raise ValueError('Every selected source needs a path and reference')
        source = safe_path(root, original)
        content = source.read_bytes()
        copied = 'context/' + str(index) + '-' + source.name
        outputs[copied] = content
        included.append({'source': original, 'path': copied, 'reference': reference, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
        derivation = next((r for r in state.get('reductions', {}).values() if r['path'] == original), None)
        if derivation:
            if hashlib.sha256(content).hexdigest() != derivation['sha256']:
                raise ValueError('Derivative changed since retention verification; prepare a new reduction')
            included[-1]['derivation'] = derivation
    # Uncommitted solution edits must never masquerade as the recorded solution revision.
    import subprocess
    diff = subprocess.run(['git', '-C', str(root), 'diff', '--exit-code', metadata['solution_revision'], '--', *state['solution']['artifacts']], capture_output=True)
    if diff.returncode:
        raise ValueError('Save or revert working solution edits before issuing a versioned packet')
    report = dict(metadata, observations=[], remaining_gaps=[], suspected_errors=[])
    contract = {'version': 1, 'required': list(report), 'observation_fields': ['criterion', 'question', 'learner_response', 'assistance', 'evidence_level'], 'evidence_levels': ['covered', 'assisted', 'independent'], 'suspected_error_fields': ['claim', 'reasoning', 'source_reference']}
    from sidechat import instructions
    tutor = instructions(metadata) + '# Teach one lesson\n\n' + json.dumps(metadata, indent=2) + '\n\nAssignment: ' + payload['assignment_context']
    tutor += '\n\nLesson: ' + lesson['title'] + '\nObjectives:\n' + '\n'.join('- ' + o for o in lesson['objectives'])
    tutor += '''

## Present source material at the point of use

Before asking the learner to read, interpret, compare or explain source material, retrieve it from the attachments and present the relevant content in the chat. Show assignment requirements or prose as a readable excerpt, and code as a formatted code block. Decode notebook JSON into its relevant markdown or code cells. For an image, diagram or merged PDF, display the relevant visual if supported; otherwise give a faithful description and an exact attachment/page locator, explaining any details you cannot access.

Label each excerpt with the original source title and section, page or notebook cell when available. Use source boundaries, the manifest and the upload layout to locate bundled material yourself. Preserve exact requirement wording, numbers and constraints; distinguish source excerpts from your explanation. Include enough surrounding context to avoid changing the meaning, while keeping the material focused on the current checkpoint.

The learner should be able to engage with the question from the content you present, without searching combined source files or opening provenance paths. Ask them to open their own project when the exercise requires editing or running it, giving the relevant snippet and location first. Present the source before the question, and leave the reasoning or answer being assessed to the learner. If required material cannot be retrieved, identify the gap rather than inventing it.
'''
    tutor += '\n\nUse the included context and source manifest; this fresh chat has no planning history. Optionally begin with a short assessment. Ask the student to explain reasoning, justify choices and answer targeted follow-up questions. Adapt explanations and practice to actual responses. Distinguish covered topics, understanding with assistance and independent understanding.\n\nReturn JSON using report-template.json and report-contract.json. Each observation records criterion, actual question, learner_response, assistance, and evidence_level (covered/assisted/independent). Record remaining_gaps and suspected_errors with claim, reasoning and source_reference. Never invent learner responses or claim software-verified independence. The student manually returns the report to the planning agent.\n'
    outputs.update({'tutor.md': tutor.encode(), 'report-template.json': json.dumps(report, indent=2).encode(), 'report-contract.json': json.dumps(contract, indent=2).encode(), 'manifest.json': json.dumps(dict(metadata, included=included, size_assessment=assessment), indent=2).encode()})
    chosen = profile(state, payload)
    packet = dict(metadata, path=relative, status='outstanding', request_record=payload['request_record'], included=included, size_assessment=assessment, total_bytes=sum(len(content) for content in outputs.values()))
    upload_outputs = build(packet, outputs, chosen)
    # Resolve every destination before writing any packet file.
    destinations = [(safe_path(root, relative + '/' + name), content) for name, content in outputs.items()]
    for destination, content in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    preserve(root, packet, upload_outputs, chosen, safe_path)
    if active:
        packets[active].update(status='replaced', decision_record=payload['decision_record'], replaced_by=pid)
    packets[pid] = packet
    state.update(active_packet=pid, next_action='return-lesson-report')
    state['upload_profile'] = chosen
    mailbox(root, packet, safe_path)
    save_state(root, state)
    return state
