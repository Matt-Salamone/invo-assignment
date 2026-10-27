import copy
import json
from tests import test_reports as support
from tests.support import WorkspaceTestCase


class SideChatTests(WorkspaceTestCase):
    prepare_report = support.ReportTests.prepare_report

    def side_report(self, state):
        p = state['packets'][state['active_packet']]
        return {**{k: p[k] for k in ('assignment_id', 'lesson_id', 'packet_id', 'contract_version', 'solution_revision')},
                'report_type': 'side-chat', 'report_id': 'side-test',
                'discussions': [{'question': 'Why?', 'explanation': 'A synthetic clarification', 'source_reference': 'Synthetic example'}],
                'remaining_questions': [], 'assessment_help': []}

    def test_supplement_before_main_preserves_packet_and_applies_help(self):
        state, main = self.prepare_report()
        side = self.side_report(state)
        side['assessment_help'] = [{'question': main['observations'][0]['question'], 'help': 'Explained the target answer', 'timing': 'before-answer'}]
        state = self.operation('report-import', side)
        self.assertEqual(state['active_packet'], main['packet_id'])
        self.assertNotIn('evidence', state)
        self.assertTrue((self.root/'assignment/mailbox/lesson.txt').exists())
        state = self.operation('report-import', main)
        self.assertEqual(state['plan']['lessons'][0]['progress'], 'assisted')
        self.assertEqual(state['evidence'][0]['observations'], main['observations'])
        self.assertIsNone(state['active_packet'])

    def test_late_supplement_and_duplicates_do_not_add_assessments(self):
        state, main = self.prepare_report()
        side = self.side_report(state)
        state = self.operation('report-import', main)
        before = copy.deepcopy(state['evidence'])
        state = self.operation('report-import', side)
        self.assertEqual(state['evidence'], before)
        self.assertEqual(state['plan']['lessons'][0]['progress'], 'independent')
        state = self.operation('report-import', side)
        self.assertEqual(len(state['supplemental_reports']), 1)
        side['discussions'][0]['explanation'] = 'Conflicting report ID'
        self.operation('report-import', side, ok=False)

    def test_bad_identity_is_preserved_without_closing_packet(self):
        state, _ = self.prepare_report()
        side = self.side_report(state)
        side['solution_revision'] = 'wrong'
        self.operation('report-import', side, ok=False)
        state = self.run_cli(self.root/'assignment', 'status')
        self.assertIsNotNone(state['active_packet'])
        self.assertNotIn('supplemental_reports', state)

    def test_both_roles_and_side_template_are_embedded_without_extra_uploads(self):
        state, _ = self.prepare_report()
        packet = state['packets'][state['active_packet']]
        text = (self.root/'assignment/mailbox/lesson.txt').read_text()
        self.assertIn('"report_type": "side-chat"', text)
        self.assertIn('Side chat', text)
        self.assertLessEqual(len(packet['upload_files']), packet['upload_profile']['max_files'])

    def test_after_answer_help_does_not_downgrade_prior_answer(self):
        state, main = self.prepare_report()
        side = self.side_report(state)
        side['assessment_help'] = [{'question': main['observations'][0]['question'], 'help': 'Explained afterward', 'timing': 'after-answer'}]
        self.operation('report-import', main)
        state = self.operation('report-import', side)
        self.assertEqual(state['plan']['lessons'][0]['progress'], 'independent')

    def test_fresh_later_packet_is_not_downgraded_by_old_help(self):
        state, main = self.prepare_report()
        side = self.side_report(state)
        side['assessment_help'] = [{'question': main['observations'][0]['question'], 'help': 'Target answer', 'timing': 'unknown'}]
        self.operation('report-import', side)
        self.operation('report-import', main)
        state = self.operation('packet-issue', self.packet_payload())
        packet = state['packets'][state['active_packet']]
        later = json.loads((self.root/'assignment'/packet['path']/'report-template.json').read_text())
        later['observations'] = copy.deepcopy(main['observations'])
        later['observations'][0]['question'] = 'A fresh task'
        state = self.operation('report-import', later)
        self.assertEqual(state['plan']['lessons'][0]['progress'], 'independent')
