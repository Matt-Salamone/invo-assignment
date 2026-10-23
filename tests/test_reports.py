import json
from tests.support import WorkspaceTestCase


class ReportTests(WorkspaceTestCase):
    def prepare_report(self):
        self.prepare_plan()
        state = self.operation('packet-issue', self.packet_payload())
        packet = state['packets'][state['active_packet']]
        report = json.loads((self.root / 'assignment' / packet['path'] / 'report-template.json').read_text())
        report['observations'] = [{'criterion': 'Explain required example', 'question': 'What must you produce?', 'learner_response': 'One example with explanation', 'assistance': 'No hints', 'evidence_level': 'independent'}]
        return state, report

    def test_validate_preserve_and_deduplicate_actual_evidence(self):
        state, report = self.prepare_report()
        original = state['active_packet']
        self.operation('report-import', dict(report, assignment_id='other'), ok=False)
        status = self.run_cli(self.root / 'assignment', 'status')
        self.assertEqual(status['active_packet'], original)
        self.assertEqual(list(status['imports'].values())[0]['outcome'], 'rejected')
        for field in ('lesson_id', 'packet_id', 'contract_version', 'solution_revision'):
            self.operation('report-import', dict(report, **{field: 'wrong'}), ok=False)
        self.operation('report-import', dict(report, observations=[]), ok=False)
        valid = self.operation('report-import', report)
        self.assertIsNone(valid['active_packet'])
        self.assertEqual(valid['plan']['lessons'][0]['progress'], 'independent')
        duplicate = self.operation('report-import', report)
        self.assertEqual(len(duplicate['evidence']), 1)
        self.assertEqual(list(duplicate['imports'].values())[-1]['outcome'], 'duplicate')

    def test_malformed_and_missing_observations_preserved_for_repair(self):
        state, report = self.prepare_report()
        file = self.root / 'broken.json'
        file.write_text('{broken', encoding='utf-8')
        self.run_cli(self.root / 'assignment', 'report-import', '--input', str(file), ok=False)
        status = self.run_cli(self.root / 'assignment', 'status')
        rejected = list(status['imports'].values())[-1]
        self.assertEqual((self.root / 'assignment' / rejected['raw_path']).read_text(), '{broken')
        self.assertEqual(status['active_packet'], state['active_packet'])
        del report['observations'][0]['learner_response']
        self.operation('report-import', report, ok=False)
        self.assertNotIn('evidence', self.run_cli(self.root / 'assignment', 'status'))

    def test_inactive_packet_observations_require_explicit_relevance_review(self):
        state, report = self.prepare_report()
        self.operation('packet-replace', dict(self.packet_payload(), packet_id=state['active_packet'], decision_record='Student requests refreshed packet'))
        imported = self.operation('report-import', report)
        record = list(imported['imports'].values())[-1]
        self.assertEqual(record['outcome'], 'needs-review')
        self.assertNotIn('evidence', imported)
        reviewed = self.operation('report-review', {'import_id': record['id'], 'relevant_observations': [0], 'include_errors': True, 'reason': 'Task interpretation unchanged; observation still relevant'})
        self.assertEqual(len(reviewed['evidence']), 1)
        self.assertIsNotNone(reviewed['active_packet'])

    def test_evidence_backed_format_repair_links_original_rejection(self):
        state, report = self.prepare_report()
        file = self.root / 'broken.json'
        file.write_text(json.dumps(report) + ',', encoding='utf-8')
        self.run_cli(self.root / 'assignment', 'report-import', '--input', str(file), ok=False)
        rejected_id = list(self.run_cli(self.root / 'assignment', 'status')['imports'])[-1]
        file.write_text(json.dumps(report), encoding='utf-8')
        repaired = self.run_cli(self.root / 'assignment', 'report-import', '--input', str(file), '--repair-of', rejected_id, '--repair-note', 'Removed trailing comma; observations unchanged')
        record = list(repaired['imports'].values())[-1]
        self.assertEqual(record['repair_of'], rejected_id)
        self.assertEqual(record['outcome'], 'applied')

    def test_two_pending_reviews_cannot_apply_same_packet_twice(self):
        state, report = self.prepare_report()
        self.operation('packet-abandon', {'packet_id': state['active_packet'], 'decision_record': 'Student stopped lesson'})
        first = self.operation('report-import', report)
        first_id = list(first['imports'])[-1]
        report['observations'][0]['assistance'] = 'No hints; independently answered'
        second = self.operation('report-import', report)
        second_id = list(second['imports'])[-1]
        review = {'import_id': first_id, 'relevant_observations': [0], 'include_errors': True, 'reason': 'Task unchanged'}
        self.operation('report-review', review)
        review['import_id'] = second_id
        self.operation('report-review', review, ok=False)
        self.assertEqual(len(self.run_cli(self.root / 'assignment', 'status')['evidence']), 1)
