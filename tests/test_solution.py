from tests.support import WorkspaceTestCase


class SolutionTests(WorkspaceTestCase):
    def test_solution_requires_all_deliverables_and_records_git_revision(self):
        target = self.root / 'assignment'
        self.run_cli(target, 'init')
        self.operation('intake-save', {'deliverables': ['Fractions'], 'constraints': [], 'grading_criteria': ['Reasoning'], 'uncertainties': [], 'assumptions': [], 'sources': []})
        artifact = self.root / 'answer.txt'
        artifact.write_text('1/2 + 1/4 = 3/4', encoding='utf-8')
        payload = {'artifacts': [{'source': str(artifact), 'path': 'answer.txt'}], 'checks': [], 'limitations': []}
        self.operation('solution-save', payload, ok=False)
        payload['checks'] = [{'deliverable': 'Fractions', 'result': 'passed', 'method': 'Exact arithmetic', 'evidence': '2/4 + 1/4 = 3/4', 'rubric_coverage': ['Reasoning']}]
        state = self.operation('solution-save', payload)
        solution = state['solution']
        self.assertTrue(solution['revision'])
        self.assertEqual((target / 'solution/answer.txt').read_text(), '1/2 + 1/4 = 3/4')
        self.assertEqual(self.run_cli(target, 'status')['solution'], solution)
        import subprocess
        historic = subprocess.run(['git', '-C', str(target), 'show', solution['revision'] + ':solution/answer.txt'], check=True, capture_output=True, text=True)
        self.assertEqual(historic.stdout, '1/2 + 1/4 = 3/4')

