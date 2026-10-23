from tests import test_reports
from tests.support import WorkspaceTestCase


class TeachingTests(WorkspaceTestCase):
    prepare_report = test_reports.ReportTests.prepare_report

    def test_incomplete_plan_can_only_finish_with_explicit_early_choice(self):
        state, report = self.prepare_report()
        self.operation('final-handoff', {'mode': 'complete'}, ok=False)
        self.operation('final-handoff', {'mode': 'early'}, ok=False)
        handed = self.operation('final-handoff', {'mode': 'early', 'decision_record': 'Student chooses own version now'})
        self.assertIsNone(handed['active_packet'])
        self.assertEqual(handed['packets'][state['active_packet']]['status'], 'abandoned')
        self.assertTrue((self.root / 'assignment' / state['packets'][state['active_packet']]['path']).exists())

    def test_complete_plan_handoff_follows_observed_objectives(self):
        state, report = self.prepare_report()
        self.operation('report-import', report)
        state = self.operation('final-handoff', {'mode': 'complete'})
        self.assertEqual(state['status'], 'own-version')

    def test_adapt_approve_and_override_keep_evidence_distinct(self):
        state, report = self.prepare_report()
        report['observations'][0]['evidence_level'] = 'assisted'
        state = self.operation('report-import', report)
        imported = state['evidence'][0]['import_id']
        adapted = self.operation('teaching-adapt', {'kind': 'routine', 'lesson_id': 'instructions', 'import_id': imported, 'reason': 'Needed hints', 'action': 'Extra practice explaining task'})
        self.assertEqual(adapted['plan']['lessons'][0]['adaptations'][0]['action'], 'Extra practice explaining task')
        lesson = dict(adapted['plan']['lessons'][0], minutes=30)
        pending = self.operation('teaching-adapt', {'kind': 'substantial', 'reason': 'Student needs broader practice', 'plan': {'scope': 'More practice', 'pacing': 'Thirty minutes', 'lessons': [lesson]}})
        self.assertEqual(pending['plan']['lessons'][0]['minutes'], 10)
        approved = self.operation('teaching-decide', {'proposal_id': pending['pending_teaching']['id'], 'decision': 'approved', 'decision_record': 'Student approves thirty minutes'})
        self.assertEqual(approved['plan']['lessons'][0]['minutes'], 30)
        overridden = self.operation('progression-override', {'lesson_id': 'instructions', 'choice': 'continue', 'decision_record': 'Student chooses to proceed'})
        self.assertEqual(overridden['plan']['lessons'][0]['progress'], 'assisted')
        self.assertEqual(overridden['evidence'][0]['observations'][0]['evidence_level'], 'assisted')
        handed = self.operation('final-handoff', {'mode': 'complete'})
        self.assertEqual(handed['status'], 'own-version')
        self.assertIn('own original', handed['final_handoff']['prompt'])
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['final_handoff'], handed['final_handoff'])
