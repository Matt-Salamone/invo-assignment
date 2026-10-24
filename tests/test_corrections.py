import json
import subprocess
from tests.support import WorkspaceTestCase


class CorrectionTests(WorkspaceTestCase):
    def test_investigation_required_and_correction_flags_pending_context(self):
        self.prepare_plan()
        issued = self.operation('packet-issue', self.packet_payload())
        packet = issued['packets'][issued['active_packet']]
        report = json.loads((self.root / 'assignment' / packet['path'] / 'report-template.json').read_text())
        report['observations'] = [{'criterion': 'Task', 'question': 'What is required?', 'learner_response': 'An example', 'assistance': 'None', 'evidence_level': 'independent'}]
        suspicion = self.operation('suspicion-record', {'source': 'planning-agent', 'claim': 'Example omitted its explanation', 'reasoning': 'Required deliverable includes explanation', 'source_reference': 'Assignment task'})
        eid = suspicion['suspected_errors'][-1]['id']
        changed = self.root / 'corrected.txt'
        changed.write_text('Synthetic worked example with complete explanation', encoding='utf-8')
        payload = {'error_id': eid, 'artifacts': [{'source': str(changed), 'path': 'answer.txt'}], 'checks': issued['solution']['checks'], 'limitations': [], 'announcement': 'Added the missing explanation required by the task.'}
        self.operation('correction-apply', payload, ok=False)
        self.operation('investigation-record', {'error_id': eid, 'instructions_examined': ['Required explanation'], 'sources_examined': ['Synthetic task'], 'reasoning': 'Current example lacks the requested explanation', 'conclusion': 'confirmed', 'affected_parts': ['solution/answer.txt']})
        corrected = self.operation('correction-apply', payload)
        self.assertNotEqual(corrected['solution']['revision'], issued['solution']['revision'])
        self.assertTrue(corrected['packets'][issued['active_packet']]['review_required'])
        self.operation('packet-resume', {'packet_id': issued['active_packet']}, ok=False)
        self.assertIn('missing explanation', corrected['notifications'][-1]['message'])
        stale = self.operation('report-import', report)
        self.assertEqual(list(stale['imports'].values())[-1]['outcome'], 'needs-review')
        self.assertTrue((self.root / 'assignment' / packet['path'] / 'tutor.md').exists())
        old = subprocess.run(['git', '-C', str(self.root / 'assignment'), 'show', issued['solution']['revision'] + ':solution/answer.txt'], check=True, capture_output=True, text=True)
        self.assertEqual(old.stdout, 'Synthetic worked example')
        impact = corrected['impact_reviews'][-1]
        reviewed = self.operation('solution-impact-review', {'impact_id': impact['id'], 'lessons': {'instructions': {'status': 'retained', 'reason': 'Task interpretation remains unchanged'}}, 'evidence': {}, 'packet': {'status': 'replace', 'reason': 'Old example lacks required explanation'}})
        self.assertTrue(reviewed['packets'][issued['active_packet']]['review_required'])

    def test_unconfirmed_suspicion_cannot_change_solution(self):
        original = self.prepare_solution()
        recorded = self.operation('suspicion-record', {'source': 'student', 'claim': 'Possible typo', 'reasoning': 'Unsure about wording', 'source_reference': 'Example'})
        eid = recorded['suspected_errors'][-1]['id']
        self.operation('investigation-record', {'error_id': eid, 'instructions_examined': ['Task'], 'sources_examined': ['Example'], 'reasoning': 'No discrepancy found', 'conclusion': 'unconfirmed', 'affected_parts': ['solution/answer.txt']})
        self.operation('correction-apply', {'error_id': eid}, ok=False)
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['solution']['revision'], original['solution']['revision'])
