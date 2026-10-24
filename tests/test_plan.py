from tests.support import WorkspaceTestCase


class PlanTests(WorkspaceTestCase):
    def test_plan_revision_needs_explicit_approval_of_current_version(self):
        self.prepare_solution()
        payload = {'scope': 'Understand this worked example', 'pacing': 'Optional deadline unknown', 'lessons': [{'id': 'instructions', 'kind': 'instructions', 'title': 'Interpret the task', 'objectives': ['Explain deliverables'], 'prerequisites': [], 'minutes': 15}]}
        first = self.operation('plan-propose', payload)['plan']
        self.assertEqual(first['status'], 'proposed')
        payload['lessons'][0]['minutes'] = 10
        second = self.operation('plan-propose', payload)['plan']
        self.operation('plan-approve', {'version': first['version'], 'decision_record': 'Student: approve'}, ok=False)
        self.operation('plan-approve', {'version': second['version']}, ok=False)
        approved = self.operation('plan-approve', {'version': second['version'], 'decision_record': 'Student: approve revised ten minute plan'})['plan']
        self.assertEqual(approved['status'], 'approved')
        self.assertEqual(self.run_cli(self.root / 'assignment', 'status')['plan'], approved)
        self.assertIn('Interpret the task', (self.root / 'assignment/teaching/plan.md').read_text())
