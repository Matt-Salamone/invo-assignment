import json
from tests.support import WorkspaceTestCase


class EligibilityTests(WorkspaceTestCase):
    def test_revision_reviews_gate_issuance_and_historical_completion(self):
        self.prepare_plan()
        issued = self.operation('packet-issue', self.packet_payload())
        packet = issued['packets'][issued['active_packet']]
        report = json.loads((self.root / 'assignment' / packet['path'] / 'report-template.json').read_text())
        report['observations'] = [{'criterion': 'Explain required example', 'question': 'What is needed?', 'learner_response': 'Example and explanation', 'assistance': 'None', 'evidence_level': 'independent'}]
        imported = self.operation('report-import', report)
        suspicion = self.operation('suspicion-record', {'source': 'student', 'claim': 'Missing explanation', 'reasoning': 'Only example present', 'source_reference': 'Task'})
        eid = suspicion['suspected_errors'][-1]['id']
        self.operation('investigation-record', {'error_id': eid, 'instructions_examined': ['Task'], 'sources_examined': ['Example'], 'reasoning': 'Explanation missing', 'conclusion': 'confirmed', 'affected_parts': ['solution/answer.txt']})
        file = self.root / 'corrected.txt'
        file.write_text('Example and explanation', encoding='utf-8')
        corrected = self.operation('correction-apply', {'error_id': eid, 'artifacts': [{'source': str(file), 'path': 'answer.txt'}], 'checks': issued['solution']['checks'], 'limitations': [], 'announcement': 'Added explanation'})
        self.operation('final-handoff', {'mode': 'complete'}, ok=False)
        self.operation('packet-issue', self.packet_payload(), ok=False)
        impact = corrected['impact_reviews'][-1]
        iid = imported['evidence'][0]['import_id']
        payload = {'impact_id': impact['id'], 'lessons': {'instructions': {'status': 'retained', 'reason': 'Task objectives unchanged'}}, 'evidence': {iid: {'status': 'revisit', 'reason': 'Answer may rely on missing explanation'}}}
        self.operation('solution-impact-review', payload)
        self.operation('final-handoff', {'mode': 'complete'}, ok=False)
        payload['evidence'][iid] = {'status': 'retained', 'reason': 'Task-only response remains useful after inspection'}
        self.operation('solution-impact-review', payload)
        self.assertEqual(self.operation('final-handoff', {'mode': 'complete'})['status'], 'own-version')

    def test_initial_plan_rejects_empty_objectives_and_boolean_duration(self):
        self.prepare_solution()
        payload = {'scope': 'Example', 'pacing': 'Short', 'lessons': [{'id': 'instructions', 'kind': 'instructions', 'title': 'Task', 'objectives': [''], 'prerequisites': [], 'minutes': 10}]}
        self.operation('plan-propose', payload, ok=False)
        payload['lessons'][0].update(objectives=['Explain task'], minutes=True)
        self.operation('plan-propose', payload, ok=False)
