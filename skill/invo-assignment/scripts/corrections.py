"""Investigated solution changes and durable teaching-context impact review."""
import copy
import json
import uuid


def text_fields(record, names):
    if any(not isinstance(record.get(name), str) or not record[name].strip() for name in names):
        raise ValueError('Required explanation fields: ' + ', '.join(names))


def mark_impact(state, before, after, reason):
    impact = {'id': str(uuid.uuid4()), 'before': before, 'after': after, 'reason': reason,
              'lessons': {lesson['id']: {'status': 'pending'} for lesson in state.get('plan', {}).get('lessons', [])},
              'evidence': {e['import_id']: {'status': 'pending'} for e in state.get('evidence', [])},
              'packet_id': state.get('active_packet'), 'packet_review': 'pending' if state.get('active_packet') else 'none'}
    state.setdefault('impact_reviews', []).append(impact)
    for lesson in state.get('plan', {}).get('lessons', []):
        lesson['context_review_required'] = True
    if state.get('active_packet'):
        state['packets'][state['active_packet']]['review_required'] = True
    state['next_action'] = 'review-solution-impact'
    return impact


def commit_solution(root, git, message):
    git(root, 'add', '--', 'solution')
    git(root, '-c', 'user.name=invo-assignment', '-c', 'user.email=invo-assignment@localhost', 'commit', '--allow-empty', '-m', message)
    return git(root, 'rev-parse', 'HEAD')


def ensure_clean_solution(root, git):
    if git(root, 'diff', '--cached', '--name-only') or git(root, 'diff', 'HEAD', '--', 'solution'):
        raise ValueError('Commit or preserve staged changes and working solution edits before revision operations')


def operation(root, state, command, payload, safe_path, save_state, git):
    if not state.get('solution'):
        raise ValueError('A saved solution is required')
    if command == 'solution-restore':
        text_fields(payload, ('revision', 'reason'))
        target = next((s for s in state.get('solution_history', []) if s['revision'] == payload['revision']), None)
        if not target or target['revision'] == state['solution']['revision']:
            raise ValueError('Restore requires a recorded earlier solution revision')
        ensure_clean_solution(root, git)
        import subprocess
        outputs = {}
        for part in [*target['artifacts'], 'solution/verification.json']:
            if not part.startswith('solution/'):
                raise ValueError('Invalid recorded solution path')
            path = safe_path(root, part)
            if not path.is_relative_to(safe_path(root, 'solution')):
                raise ValueError('Invalid recorded solution destination')
            outputs[path] = subprocess.run(['git', '-C', str(root), 'show', target['revision'] + ':' + part], capture_output=True, check=True).stdout
        removed = [safe_path(root, part) for part in state['solution']['artifacts'] if part not in target['artifacts']]
        for path in removed:
            if not path.is_relative_to(safe_path(root, 'solution')):
                raise ValueError('Invalid current solution artifact')
        previous = copy.deepcopy(state['solution'])
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        for path in removed:
            path.unlink()
        revision = commit_solution(root, git, 'Restore worked solution ' + target['revision'] + ': ' + payload['reason'])
        state.setdefault('solution_history', []).append(previous)
        state['solution'] = copy.deepcopy(target)
        state['solution']['revision'] = revision
        impact = mark_impact(state, previous['revision'], revision, payload['reason'])
        state.setdefault('restorations', []).append({'revision': revision, 'restored_from': target['revision'], 'before': previous['revision'], 'reason': payload['reason'], 'impact_id': impact['id']})
        state.setdefault('notifications', []).append({'kind': 'solution-restoration', 'revision': revision, 'message': 'Restored earlier solution ' + target['revision'] + ': ' + payload['reason']})
    elif command == 'suspicion-record':
        text_fields(payload, ('source', 'claim', 'reasoning', 'source_reference'))
        record = dict(payload, id=str(uuid.uuid4()), status='uninvestigated', solution_revision=state['solution']['revision'])
        state.setdefault('suspected_errors', []).append(record)
    elif command == 'investigation-record':
        error = next((e for e in state.get('suspected_errors', []) if e['id'] == payload.get('error_id')), None)
        if not error or error['status'] == 'corrected':
            raise ValueError('Identify an uncorrected suspicion')
        text_fields(payload, ('reasoning', 'conclusion'))
        for field in ('instructions_examined', 'sources_examined', 'affected_parts'):
            if not isinstance(payload.get(field), list) or not payload[field] or any(not isinstance(v, str) or not v.strip() for v in payload[field]):
                raise ValueError('Investigation must record instructions, sources and affected parts')
        if payload['conclusion'] not in ('confirmed', 'unconfirmed'):
            raise ValueError('Conclusion must be confirmed or unconfirmed')
        for part in payload['affected_parts']:
            if part not in state['solution']['artifacts']:
                raise ValueError('Affected parts must identify saved solution artifacts')
        investigation = dict(payload, solution_revision=state['solution']['revision'])
        error.setdefault('investigations', []).append(investigation)
        error.update(status=payload['conclusion'], investigation=investigation)
    elif command == 'correction-apply':
        error = next((e for e in state.get('suspected_errors', []) if e['id'] == payload.get('error_id')), None)
        if not error or error['status'] != 'confirmed' or error['investigation']['solution_revision'] != state['solution']['revision']:
            raise ValueError('Correction requires a confirmed investigation against the current solution')
        text_fields(payload, ('announcement',))
        if not isinstance(payload.get('artifacts'), list) or not payload['artifacts'] or not isinstance(payload.get('checks'), list) or not isinstance(payload.get('limitations'), list):
            raise ValueError('Correction needs artifacts, actual verification checks and limitations')
        checks = payload['checks']
        for check in checks:
            text_fields(check, ('deliverable', 'result', 'method', 'evidence'))
            if check['result'] not in ('passed', 'failed', 'limited') or not isinstance(check.get('rubric_coverage'), list):
                raise ValueError('Invalid correction verification')
        if not set(state['intake']['deliverables']).issubset({c['deliverable'] for c in checks}) or not set(state['intake']['grading_criteria']).issubset({r for c in checks for r in c['rubric_coverage']}):
            raise ValueError('Correction must verify every deliverable and grading criterion')
        if any(c['result'] != 'passed' for c in checks) and not payload['limitations']:
            raise ValueError('Failed checks require limitations')
        outputs = {}
        for artifact in payload['artifacts']:
            text_fields(artifact, ('path', 'source'))
            part = 'solution/' + artifact['path']
            if part not in error['investigation']['affected_parts']:
                raise ValueError('Correction artifacts must match investigated affected parts')
            path = safe_path(root, part)
            if path in outputs:
                raise ValueError('Duplicate correction artifact')
            outputs[path] = __import__('pathlib').Path(artifact['source']).read_bytes()
        if not any(path.read_bytes() != content for path, content in outputs.items()):
            raise ValueError('Correction must change an investigated solution artifact')
        ensure_clean_solution(root, git)
        previous = copy.deepcopy(state['solution'])
        for path, content in outputs.items():
            path.write_bytes(content)
        safe_path(root, 'solution/verification.json').write_text(json.dumps({'checks': checks, 'limitations': payload['limitations']}, indent=2) + '\n', encoding='utf-8')
        reason = error['investigation']['reasoning']
        revision = commit_solution(root, git, 'Correct worked solution: ' + reason)
        state.setdefault('solution_history', []).append(previous)
        state['solution'].update(revision=revision, checks=checks, limitations=payload['limitations'])
        impact = mark_impact(state, previous['revision'], revision, reason)
        error.update(status='corrected', corrected_revision=revision)
        state.setdefault('corrections', []).append({'error_id': error['id'], 'before': previous['revision'], 'revision': revision, 'reason': reason, 'announcement': payload['announcement'], 'impact_id': impact['id']})
        state.setdefault('notifications', []).append({'kind': 'solution-correction', 'revision': revision, 'message': payload['announcement']})
    elif command == 'solution-impact-review':
        impact = next((r for r in state.get('impact_reviews', []) if r['id'] == payload.get('impact_id')), None)
        if not impact:
            raise ValueError('Unknown solution impact review')
        for section in ('lessons', 'evidence'):
            assessments = payload.get(section)
            if not isinstance(assessments, dict) or set(assessments) != set(impact[section]):
                raise ValueError('Review every affected lesson and evidence record')
            for assessment in assessments.values():
                text_fields(assessment, ('status', 'reason'))
                if assessment['status'] not in ('retained', 'revisit', 'pending'):
                    raise ValueError('Review status must be retained, revisit or pending')
            impact[section] = assessments
        if impact['packet_id']:
            assessment = payload.get('packet')
            if not isinstance(assessment, dict):
                raise ValueError('Review affected outstanding packet')
            text_fields(assessment, ('status', 'reason'))
            if assessment['status'] not in ('safe-to-resume', 'replace', 'pending'):
                raise ValueError('Packet review requires safe-to-resume, replace or pending')
            impact['packet_review'] = assessment
            state['packets'][impact['packet_id']]['review_required'] = assessment['status'] != 'safe-to-resume'
        for lesson in state.get('plan', {}).get('lessons', []):
            lesson['context_review_required'] = any(r['lessons'].get(lesson['id'], {}).get('status') in ('pending', 'revisit') for r in state['impact_reviews'])
        state['next_action'] = 'request-lesson' if not state.get('active_packet') else 'resume-or-replace-packet'
    save_state(root, state)
    return state
