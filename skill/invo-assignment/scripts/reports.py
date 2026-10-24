"""Report preservation, association validation, relevance review and evidence import."""
import hashlib
import json
import uuid

IDENTIFIERS = ('assignment_id', 'lesson_id', 'packet_id', 'contract_version', 'solution_revision')
LEVELS = ('covered', 'assisted', 'independent')


def validate(report, state):
    if not isinstance(report, dict) or any(key not in report for key in (*IDENTIFIERS, 'observations', 'remaining_gaps', 'suspected_errors')):
        raise ValueError('Missing report fields; ask for actual missing evidence rather than inventing it')
    if report['assignment_id'] != state['assignment_id']:
        raise ValueError('Wrong assignment')
    packet = state.get('packets', {}).get(report['packet_id'])
    if not packet or any(report[key] != packet[key] for key in IDENTIFIERS) or type(report['contract_version']) is not int:
        raise ValueError('Report identifiers or solution revision do not match an issued packet')
    if not isinstance(report['observations'], list) or not report['observations']:
        raise ValueError('Report needs actual observed questions and responses')
    for observation in report['observations']:
        if not isinstance(observation, dict) or any(not isinstance(observation.get(key), str) or not observation[key].strip() for key in ('criterion', 'question', 'learner_response', 'assistance')) or observation.get('evidence_level') not in LEVELS:
            raise ValueError('Observation needs criterion, actual question/response, assistance and evidence level')
    if not isinstance(report['remaining_gaps'], list) or any(not isinstance(gap, str) or not gap.strip() for gap in report['remaining_gaps']):
        raise ValueError('Remaining gaps must be a list of descriptions')
    if not isinstance(report['suspected_errors'], list):
        raise ValueError('Suspected errors must be a list')
    for error in report['suspected_errors']:
        if not isinstance(error, dict) or any(not isinstance(error.get(key), str) or not error[key].strip() for key in ('claim', 'reasoning', 'source_reference')):
            raise ValueError('Suspected error needs claim, reasoning and source reference')
    return packet


def apply(root, state, record, report, indices, include_errors, safe_path):
    observations = [report['observations'][index] for index in indices]
    state.setdefault('evidence', []).append({'import_id': record['id'], 'lesson_id': report['lesson_id'], 'solution_revision': report['solution_revision'], 'observations': observations, 'remaining_gaps': report['remaining_gaps'], 'qualification': 'Chatbot observations, not verified retention or correctness'})
    if include_errors:
        for error in report['suspected_errors']:
            state.setdefault('suspected_errors', []).append(dict(error, import_id=record['id'], packet_id=report['packet_id'], solution_revision=report['solution_revision'], status='uninvestigated', id=str(uuid.uuid4())))
    lesson = next((l for l in state['plan']['lessons'] if l['id'] == report['lesson_id']), None)
    if lesson and observations:
        lesson['progress'] = min((o['evidence_level'] for o in observations), key=LEVELS.index)
        lesson['remaining_gaps'] = report['remaining_gaps']
        lesson['recommendation'] = 'revisit' if report['remaining_gaps'] or lesson['progress'] != 'independent' else 'continue'
    record['outcome'] = 'applied'
    record['applied_observations'] = indices
    if state.get('active_packet') == report['packet_id']:
        state['packets'][report['packet_id']]['status'] = 'completed'
        state['active_packet'] = None
        pointer = safe_path(root, 'mailbox/current.json')
        pointer.write_text('null\n', encoding='utf-8')
    state['next_action'] = 'review-progress'


def import_report(root, state, raw, safe_path, save_state, repair_of=None, repair_note=None):
    if repair_of and (repair_of not in state.get('imports', {}) or not repair_note or not repair_note.strip()):
        raise ValueError('Repair needs an existing import and description of evidence-backed changes')
    rid = str(uuid.uuid4())
    relative = 'reports/' + rid + '/returned.json'
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    record = {'id': rid, 'raw_path': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'outcome': 'received', 'repair_of': repair_of, 'repair_note': repair_note}
    imports = state.setdefault('imports', {})
    imports[rid] = record
    try:
        report = json.loads(raw)
        packet = validate(report, state)
        # Canonical JSON makes whitespace-only resubmission idempotent.
        canonical = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
        record.update(canonical=canonical, packet_id=report['packet_id'])
        previous = next((r for r in imports.values() if r['id'] != rid and r.get('canonical') == canonical and r['outcome'] in ('applied', 'needs-review')), None)
        if previous:
            record.update(outcome='duplicate', duplicate_of=previous['id'])
        elif any(r['id'] != rid and r.get('packet_id') == report['packet_id'] and r['outcome'] == 'applied' for r in imports.values()):
            raise ValueError('Evidence for this packet already applied; review existing evidence rather than applying another report')
        elif report['solution_revision'] != state['solution']['revision'] or packet['status'] != 'outstanding' or packet.get('review_required'):
            record.update(outcome='needs-review', reason='Review stale solution or inactive/affected packet for relevance')
            state['next_action'] = 'review-stale-report'
        else:
            apply(root, state, record, report, list(range(len(report['observations']))), True, safe_path)
    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as error:
        record.update(outcome='rejected', reason=str(error))
        save_state(root, state)
        raise ValueError('Report preserved as ' + rid + ': ' + str(error)) from error
    save_state(root, state)
    return state


def review(root, state, payload, safe_path, save_state):
    record = state.get('imports', {}).get(payload.get('import_id'))
    if not record or record['outcome'] != 'needs-review':
        raise ValueError('Identify an import awaiting relevance review')
    indices = payload.get('relevant_observations')
    if not isinstance(indices, list) or not isinstance(payload.get('reason'), str) or not payload['reason'].strip() or type(payload.get('include_errors')) is not bool:
        raise ValueError('Relevance review requires observation indices, include_errors and reason')
    report = json.loads(safe_path(root, record['raw_path']).read_bytes())
    validate(report, state)
    if any(type(i) is not int or i < 0 or i >= len(report['observations']) for i in indices) or len(set(indices)) != len(indices):
        raise ValueError('Invalid relevant observation index')
    if indices and any(other['id'] != record['id'] and other.get('packet_id') == report['packet_id'] and other['outcome'] == 'applied' for other in state.get('imports', {}).values()):
        record.update(outcome='rejected', reason='Evidence for this packet was applied while relevance review was pending')
        save_state(root, state)
        raise ValueError(record['reason'])
    record['relevance_review'] = payload
    if indices:
        apply(root, state, record, report, indices, payload['include_errors'], safe_path)
    else:
        record.update(outcome='reviewed-no-evidence')
        state['next_action'] = 'request-lesson'
    save_state(root, state)
    return state
