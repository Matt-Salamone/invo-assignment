"""Shared eligibility of teaching context and previously observed evidence."""


def context_ready(state, lesson):
    relevant = {e['import_id'] for e in state.get('evidence', []) if e['lesson_id'] == lesson['id']}
    return not lesson.get('context_review_required') and all(
        review.get('lessons', {}).get(lesson['id'], {}).get('status', 'retained') == 'retained'
        and all(assessment.get('status') != 'pending' for iid, assessment in review.get('evidence', {}).items() if iid in relevant)
        for review in state.get('impact_reviews', []))


def evidence_usable(state, evidence):
    return all(review.get('evidence', {}).get(evidence['import_id'], {}).get('status', 'retained') == 'retained' for review in state.get('impact_reviews', []))
