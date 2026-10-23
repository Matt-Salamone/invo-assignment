import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'skill/invo-assignment/scripts/workspace.py'

class WorkspaceTestCase(unittest.TestCase):
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


