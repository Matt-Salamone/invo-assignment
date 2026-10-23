import json
import subprocess
from tests.support import WorkspaceTestCase


class RestorationTests(WorkspaceTestCase):
    def test_full_cycle_restore_preserves_later_history_reports_and_evidence(self):
        self.prepare_plan()
        issued = self.operation('packet-issue', self.packet_payload())
        initial = issued['solution']['revision']
        packet = issued['packets'][issued['active_packet']]
        report = json.loads((self.root / 'assignment' / packet['path'] / 'report-template.json').read_text())
        report['observations'] = [{'criterion': 'Task', 'question': 'What must you produce?', 'learner_response': 'An example and explanation', 'assistance': 'None', 'evidence_level': 'independent'}]
        imported = self.operation('report-import', report)
        recorded = self.operation('suspicion-record', {'source': 'student', 'claim': 'Explanation omitted', 'reasoning': 'Task asks for explanation', 'source_reference': 'Task'})
        eid = recorded['suspected_errors'][-1]['id']
        self.operation('investigation-record', {'error_id': eid, 'instructions_examined': ['Task'], 'sources_examined': ['Worked example'], 'reasoning': 'Explanation missing', 'conclusion': 'confirmed', 'affected_parts': ['solution/answer.txt']})
        artifact = self.root / 'corrected.txt'
        artifact.write_text('Corrected synthetic example with explanation', encoding='utf-8')
        corrected = self.operation('correction-apply', {'error_id': eid, 'artifacts': [{'source': str(artifact), 'path': 'answer.txt'}], 'checks': issued['solution']['checks'], 'limitations': [], 'announcement': 'Added explanation.'})
        self.operation('solution-restore', {'revision': 'not-a-recorded-revision', 'reason': 'Invalid test target'}, ok=False)
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['solution'], corrected['solution'])
        restored = self.operation('solution-restore', {'revision': initial, 'reason': 'Student explicitly requests original teaching reference'})
        self.assertNotEqual(restored['solution']['revision'], initial)
        self.assertEqual((self.root / 'assignment/solution/answer.txt').read_text(), 'Synthetic worked example')
        self.assertEqual(restored['evidence'], imported['evidence'])
        self.assertEqual(restored['imports'], imported['imports'])
        self.assertEqual(restored['restorations'][-1]['restored_from'], initial)
        self.assertEqual(restored['impact_reviews'][-1]['evidence'][imported['evidence'][0]['import_id']]['status'], 'pending')
        subprocess.run(['git', '-C', str(self.root / 'assignment'), 'merge-base', '--is-ancestor', corrected['solution']['revision'], restored['solution']['revision']], check=True)
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['restorations'], restored['restorations'])
