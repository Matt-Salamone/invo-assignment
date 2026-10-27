"""Evidence-based adaptations, separate student decisions and final handoff."""
from copy import deepcopy
import uuid
from eligibility import context_ready, evidence_usable


def text(record, key):
    if not isinstance(record.get(key), str) or not record[key].strip():
        raise ValueError('Nonempty ' + key + ' required')
    return record[key]


def operation(root, state, command, payload, save_state, write_plan, safe_path):
    plan = state.get('plan')
    if not plan or plan['status'] != 'approved' or state.get('final_handoff'):
        raise ValueError('Teaching changes require an active approved plan')
    if command == 'teaching-adapt':
        text(payload, 'reason')
        if payload.get('kind') == 'routine':
            lesson = next((l for l in plan['lessons'] if l['id'] == payload.get('lesson_id')), None)
            evidence = next((e for e in state.get('evidence', []) if e['import_id'] == payload.get('import_id') and e['lesson_id'] == payload.get('lesson_id')), None)
            if not lesson or not evidence:
                raise ValueError('Routine adaptation requires relevant imported evidence')
            text(payload, 'action')
            lesson.setdefault('adaptations', []).append(dict(payload))
            state.setdefault('adaptations', []).append(dict(payload))
            state['next_action'] = 'request-lesson'
        elif payload.get('kind') == 'substantial':
            if state.get('pending_teaching'):
                raise ValueError('Decide the pending proposal first')
            proposed = deepcopy(payload.get('plan'))
            if not isinstance(proposed, dict):
                raise ValueError('Substantial adaptation needs a complete plan proposal')
            validate_plan(proposed)
            state['pending_teaching'] = {'id': str(uuid.uuid4()), 'reason': payload['reason'], 'plan': proposed, 'status': 'proposed'}
            state['next_action'] = 'decide-teaching-proposal'
        else:
            raise ValueError('Adaptation kind must be routine or substantial')
    elif command == 'teaching-decide':
        proposal = state.get('pending_teaching')
        text(payload, 'decision_record')
        if not proposal or proposal['id'] != payload.get('proposal_id') or payload.get('decision') not in ('approved', 'declined'):
            raise ValueError('Decide the current teaching proposal')
        if state.get('active_packet') and payload['decision'] == 'approved':
            raise ValueError('Finish or explicitly abandon outstanding packet before changing plan scope')
        proposal.update(status=payload['decision'], decision_record=payload['decision_record'])
        if payload['decision'] == 'approved':
            state.setdefault('plan_history', []).append(deepcopy(plan))
            new = deepcopy(proposal['plan'])
            previous = {l['id']: l for l in plan['lessons']}
            for lesson in new['lessons']:
                old = previous.get(lesson['id'], {})
                # Changed objectives require new evidence, even under an existing lesson ID.
                if old.get('objectives') == lesson['objectives']:
                    for field in ('progress', 'remaining_gaps', 'recommendation', 'adaptations', 'context_review_required'):
                        if field in old:
                            lesson[field] = deepcopy(old[field])
                else:
                    lesson['progress'] = 'not-started'
            state['plan'] = dict(new, version=plan['version'] + 1, status='approved', decision_record=payload['decision_record'])
        state.setdefault('teaching_decisions', []).append(deepcopy(proposal))
        state['pending_teaching'] = None
        state['next_action'] = 'request-lesson'
    elif command == 'progression-override':
        text(payload, 'decision_record')
        if payload.get('choice') not in ('continue', 'revisit') or not any(l['id'] == payload.get('lesson_id') for l in plan['lessons']):
            raise ValueError('Override requires a known lesson and continue/revisit choice')
        state.setdefault('progression_overrides', []).append(dict(payload, plan_version=plan['version']))
        state['next_action'] = 'request-lesson'
    elif command == 'final-handoff':
        mode = payload.get('mode')
        if mode == 'early':
            text(payload, 'decision_record')
        elif mode == 'complete':
            if state.get('pending_teaching') or state.get('active_packet'):
                raise ValueError('Resolve outstanding teaching before completion')
            overrides = {o['lesson_id']: o['choice'] for o in state.get('progression_overrides', []) if o['plan_version'] == plan['version']}
            for lesson in plan['lessons']:
                if not context_ready(state, lesson):
                    raise ValueError('Review changed lesson context before completing the plan; use explicit early handoff to finish with unresolved reviews')
                if overrides.get(lesson['id']) == 'revisit':
                    raise ValueError('Student chose to revisit a lesson')
                if overrides.get(lesson['id']) == 'continue':
                    continue
                from sidechat import effective_observations
                observed = [o['criterion'] for e in state.get('evidence', []) if e['lesson_id'] == lesson['id'] and evidence_usable(state, e) for o in effective_observations(state, e) if o['evidence_level'] == 'independent']
                if lesson.get('remaining_gaps') or not set(lesson['objectives']).issubset(observed) or lesson.get('recommendation') != 'continue':
                    raise ValueError('Plan has incomplete evidence; revisit or record student choice')
        else:
            raise ValueError('Handoff mode must be complete or early')
        if state.get('active_packet'):
            state['packets'][state['active_packet']].update(status='abandoned', decision_record=payload['decision_record'])
            state['active_packet'] = None
            from uploads import mailbox
            mailbox(root, None, safe_path)
        state['final_handoff'] = dict(payload, prompt='Create your own original version of the assignment.', plan_version=plan['version'])
        state.update(status='own-version', next_action='create-own-original-version')
    write_plan(root, state['plan'])
    save_state(root, state)
    return state


def validate_plan(plan):
    for key in ('scope', 'pacing'):
        text(plan, key)
    lessons = plan.get('lessons')
    if not isinstance(lessons, list) or not lessons or not isinstance(lessons[0], dict) or lessons[0].get('kind') != 'instructions':
        raise ValueError('Proposal must start with assignment instructions')
    ids = set()
    for lesson in lessons:
        if not isinstance(lesson, dict):
            raise ValueError('Lesson must be an object')
        for key in ('id', 'title', 'kind'):
            text(lesson, key)
        if lesson['id'] in ids or type(lesson.get('minutes')) is not int or lesson['minutes'] <= 0 or not isinstance(lesson.get('objectives'), list) or not lesson['objectives'] or any(not isinstance(o, str) or not o.strip() for o in lesson['objectives']) or not isinstance(lesson.get('prerequisites'), list):
            raise ValueError('Proposal lessons require unique IDs, positive minutes, objectives and prerequisites')
        ids.add(lesson['id'])
