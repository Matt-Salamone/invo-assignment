"""Supplemental Q&A records and conservative assistance qualifications."""
from copy import deepcopy
import hashlib
import json
import uuid


def template(metadata):
    return dict(metadata, report_type='side-chat', report_id='side-' + uuid.uuid4().hex,
                discussions=[], remaining_questions=[], assessment_help=[])


def instructions(metadata):
    return '''# Select the chat role

Use this same complete upload set in both chats. If the learner's opening message
is "Side chat", use ONLY the side-chat role below. "Go" or a request to begin the
lesson selects the lesson role. Keep the selected role for this conversation.
The following lesson objectives, assessment directions and main report forms
apply only to the lesson role. Both roles use the same sources and identifiers.

## Shared visual guidance

Favor UML when it clarifies the technical explanation: class diagrams for
structures and relationships, sequence diagrams for calls and callbacks,
activity diagrams for algorithms/control flow, and state diagrams for lifecycles.
Accompany diagrams with code and prose. Use another representation when clearer.
Label tutor-authored diagrams separately from source figures; present the relevant
code or visual before a question and keep assessed reasoning for the learner.

## Side-chat role

Answer learner-initiated questions, tangents and requests for depth. Do not start
the assigned lesson, advance checkpoints, assess mastery, or fill the main report.
Use the same point-of-use source presentation rules as the lesson role. You may
give direct explanations or solutions when asked; record help related to an
assessment, with its question, what you supplied and whether it preceded the
answer, followed it, or its timing is unknown. Avoid inferring independence from
engagement or explanations. Record actual learner responses only when supplied.

On request, return ONE supplemental JSON report using the template below.
Each discussion is {question, explanation, source_reference}; an optional
learner_response preserves an actual response. remaining_questions is a list
of text descriptions. assessment_help entries are {question, help, timing},
where timing is "before-answer", "after-answer", or "unknown". Copy the exact
assessment question where possible. Use a distinct report_id for a new report;
reuse it when returning the same report. Keep all other identifiers exact.
The template's empty lists are placeholders, not evidence. If no side chat was
used, no supplemental report is required. The learner returns this separately
from the main report; either report may arrive first or the supplement later.

### Supplemental report template
```json
''' + json.dumps(template(metadata), indent=2) + '\n```\n\n# Lesson role only\n\n'


def accept(state, record, report):
    from reports import IDENTIFIERS
    packet = state.get('packets', {}).get(report.get('packet_id'))
    if not packet or any(report.get(k) != packet[k] for k in IDENTIFIERS) or type(report.get('contract_version')) is not int:
        raise ValueError('Supplemental report identifiers do not match an issued packet')
    rid = report.get('report_id')
    if not isinstance(rid, str) or not rid.strip():
        raise ValueError('Supplemental report needs report_id')
    discussions = report.get('discussions')
    if not isinstance(discussions, list) or not discussions:
        raise ValueError('Supplemental report needs actual discussions')
    for discussion in discussions:
        if not isinstance(discussion, dict) or any(not isinstance(discussion.get(k), str) or not discussion[k].strip() for k in ('question', 'explanation', 'source_reference')):
            raise ValueError('Discussion needs question, explanation and source_reference')
        if 'learner_response' in discussion and not isinstance(discussion['learner_response'], str):
            raise ValueError('Actual learner_response must be text')
    gaps = report.get('remaining_questions')
    if not isinstance(gaps, list) or any(not isinstance(g, str) or not g.strip() for g in gaps):
        raise ValueError('remaining_questions must be text descriptions')
    help_items = report.get('assessment_help')
    if not isinstance(help_items, list):
        raise ValueError('assessment_help must be a list')
    for item in help_items:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip() for k in ('question', 'help')) or item.get('timing') not in ('before-answer', 'after-answer', 'unknown'):
            raise ValueError('Assessment help needs question, help and timing')
    if 'observations' in report or 'objectives' in report:
        raise ValueError('Side-chat reports record supplemental discussion, not formal assessment')
    canonical = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
    collection = state.get('supplemental_reports', {})
    previous = collection.get(rid)
    record.update(canonical=canonical, packet_id=report['packet_id'], report_type='side-chat')
    if previous:
        if previous['canonical'] != canonical:
            raise ValueError('Supplemental report_id conflict; preserve the earlier report')
        record.update(outcome='duplicate', duplicate_of=previous['import_id'])
        return
    if any(r['canonical'] == canonical for r in collection.values()):
        record['outcome'] = 'duplicate'
        return
    state.setdefault('supplemental_reports', {})[rid] = {
        'import_id': record['id'], 'canonical': canonical, 'raw_path': record['raw_path'],
        'packet_id': report['packet_id'], 'report': deepcopy(report), 'evidence_level': 'covered'}
    record['outcome'] = 'supplemental-recorded'
    # Never close a packet, clear the mailbox, or import a second assessment.
    refresh(state, report['lesson_id'])


def effective_observations(state, evidence):
    """Project assistance without changing the archived tutor observations."""
    pid = state.get('imports', {}).get(evidence['import_id'], {}).get('packet_id')
    help_items = [h for r in state.get('supplemental_reports', {}).values()
                  if r['packet_id'] == pid for h in r['report']['assessment_help']
                  if h['timing'] != 'after-answer']
    result = deepcopy(evidence['observations'])
    for observation in result:
        matches = [h for h in help_items if h['question'] == observation['question']]
        if matches and observation['evidence_level'] == 'independent':
            observation['reported_evidence_level'] = 'independent'
            observation['evidence_level'] = 'assisted'
            observation['supplemental_assistance'] = matches
    return result


def refresh(state, lesson_id):
    lesson = next((l for l in state.get('plan', {}).get('lessons', []) if l['id'] == lesson_id), None)
    evidence = [e for e in state.get('evidence', []) if e['lesson_id'] == lesson_id]
    if not lesson or not evidence:
        return
    latest = evidence[-1]
    observations = effective_observations(state, latest)
    if observations:
        from reports import LEVELS
        lesson['progress'] = min((o['evidence_level'] for o in observations), key=LEVELS.index)
    latest_pid = state.get('imports', {}).get(latest['import_id'], {}).get('packet_id')
    related = [r for r in state.get('supplemental_reports', {}).values()
               if r['packet_id'] == latest_pid]
    if any(r['report']['assessment_help'] or r['report']['remaining_questions'] for r in related):
        lesson['recommendation'] = 'revisit'
        lesson['supplemental_follow_up'] = [r['import_id'] for r in related]
