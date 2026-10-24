import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'skill/invo-assignment/scripts/workspace.py'

class WorkspaceTestCase(unittest.TestCase):
    def prepare_solution(self):
        self.run_cli(self.root / 'assignment', 'init')
        self.operation('intake-save', {'deliverables': ['Example'], 'constraints': [], 'grading_criteria': [], 'uncertainties': [], 'assumptions': [], 'sources': []})
        artifact = self.root / 'answer.txt'
        artifact.write_text('Synthetic worked example', encoding='utf-8')
        return self.operation('solution-save', {'artifacts': [{'source': str(artifact), 'path': 'answer.txt'}], 'checks': [{'deliverable': 'Example', 'result': 'passed', 'method': 'Inspect example', 'evidence': 'Complete example inspected', 'rubric_coverage': []}], 'limitations': []})

    def prepare_plan(self):
        self.prepare_solution()
        self.operation('plan-propose', {'scope': 'Explain example', 'pacing': 'Ten minutes', 'lessons': [{'id': 'instructions', 'kind': 'instructions', 'title': 'Understand the task', 'objectives': ['Explain required example'], 'prerequisites': [], 'minutes': 10}]})
        return self.operation('plan-approve', {'version': 1, 'decision_record': 'Student approved'})

    def packet_payload(self):
        return {'lesson_id': 'instructions', 'request_record': 'Student requested this lesson', 'assignment_context': 'Create one synthetic example and explain it.', 'context': [], 'size_assessment': {'basis': 'One short example and task description', 'relevance': 'All content addresses the objective', 'uncertainty': 'Chatbot limit unknown', 'limitations': []}}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='invo-synthetic-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, workspace, *args, ok=True):
        result = subprocess.run([sys.executable, str(CLI), '--workspace', str(workspace), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return json.loads(result.stdout) if ok else result.stderr


    def operation(self, command, payload, ok=True):
        file = self.root / 'payload.json'
        file.write_text(json.dumps(payload), encoding='utf-8')
        return self.run_cli(self.root / 'assignment', command, '--input', str(file), ok=ok)


