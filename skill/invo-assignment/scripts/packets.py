"""Preserved packet snapshots and explicit outstanding-packet lifecycle."""
import hashlib
import json
import uuid


def mailbox(root, packet, safe_path):
    path = safe_path(root, 'mailbox/current.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2) + '\n', encoding='utf-8')


def operation(root, state, command, payload, safe_path, save_state):
    packets = state.setdefault('packets', {})
    active = state.get('active_packet')
    if command in ('packet-resume', 'packet-abandon', 'packet-replace'):
        if not active or payload.get('packet_id') != active:
            raise ValueError('Operation must identify the outstanding packet')
        if command == 'packet-resume':
            if packets[active].get('review_required'):
                raise ValueError('Outstanding packet requires review before continuation')
            mailbox(root, packets[active], safe_path)
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
    # Uncommitted solution edits must never masquerade as the recorded solution revision.
    import subprocess
    diff = subprocess.run(['git', '-C', str(root), 'diff', '--exit-code', metadata['solution_revision'], '--', *state['solution']['artifacts']], capture_output=True)
    if diff.returncode:
        raise ValueError('Save or revert working solution edits before issuing a versioned packet')
    report = dict(metadata, observations=[], remaining_gaps=[], suspected_errors=[])
    contract = {'version': 1, 'required': list(report), 'observation_fields': ['criterion', 'question', 'learner_response', 'assistance', 'evidence_level'], 'evidence_levels': ['covered', 'assisted', 'independent'], 'suspected_error_fields': ['claim', 'reasoning', 'source_reference']}
    tutor = '# Teach one lesson\n\n' + json.dumps(metadata, indent=2) + '\n\nAssignment: ' + payload['assignment_context']
    tutor += '\n\nLesson: ' + lesson['title'] + '\nObjectives:\n' + '\n'.join('- ' + o for o in lesson['objectives'])
    tutor += '\n\nUse the included context and source manifest; this fresh chat has no planning history. Optionally begin with a short assessment. Ask the student to explain reasoning, justify choices and answer targeted follow-up questions. Adapt explanations and practice to actual responses. Distinguish covered topics, understanding with assistance and independent understanding.\n\nReturn JSON using report-template.json and report-contract.json. Each observation records criterion, actual question, learner_response, assistance, and evidence_level (covered/assisted/independent). Record remaining_gaps and suspected_errors with claim, reasoning and source_reference. Never invent learner responses or claim software-verified independence. The student manually returns the report to the planning agent.\n'
    outputs.update({'tutor.md': tutor.encode(), 'report-template.json': json.dumps(report, indent=2).encode(), 'report-contract.json': json.dumps(contract, indent=2).encode(), 'manifest.json': json.dumps(dict(metadata, included=included, size_assessment=assessment), indent=2).encode()})
    # Resolve every destination before writing any packet file.
    destinations = [(safe_path(root, relative + '/' + name), content) for name, content in outputs.items()]
    for destination, content in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    packet = dict(metadata, path=relative, status='outstanding', request_record=payload['request_record'], included=included, size_assessment=assessment, total_bytes=sum(len(content) for content in outputs.values()))
    if active:
        packets[active].update(status='replaced', decision_record=payload['decision_record'], replaced_by=pid)
    packets[pid] = packet
    state.update(active_packet=pid, next_action='return-lesson-report')
    mailbox(root, packet, safe_path)
    save_state(root, state)
    return state
