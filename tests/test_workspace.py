import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / 'skill/invo-assignment/scripts/workspace.py'


from tests.support import CLI, WorkspaceTestCase

class WorkspaceTests(WorkspaceTestCase):
    def test_initialize_and_resume_without_losing_work(self):
        target = self.root / 'assignment'
        initial = self.run_cli(target, 'init', '--name', 'Synthetic fractions')
        self.assertEqual(initial['name'], 'Synthetic fractions')
        self.assertEqual(initial['next_action'], 'capture-requirements')
        self.assertTrue(initial['assignment_id'])
        self.assertTrue(initial['skill_version'])
        (target / 'student-notes.txt').write_text('Keep this observation', encoding='utf-8')
        self.assertEqual(self.run_cli(target, 'init'), initial)
        self.assertEqual(self.run_cli(target, 'status'), initial)
        self.assertEqual((target / 'student-notes.txt').read_text(), 'Keep this observation')
        git = subprocess.run(['git', '-C', str(target), 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True)
        self.assertEqual(Path(git.stdout.strip()).resolve(), target.resolve())

    def test_reject_tooling_and_nested_repositories_without_changes(self):
        before = {p: p.read_bytes() for p in CLI.parents[1].rglob('*') if p.is_file()}
        self.run_cli(CLI.parents[1] / 'synthetic-assignment', 'init', ok=False)
        self.run_cli(CLI.parents[3] / 'synthetic-assignment', 'init', ok=False)
        enclosing = self.root / 'unrelated'
        enclosing.mkdir()
        subprocess.run(['git', '-C', str(enclosing), 'init'], check=True, capture_output=True)
        self.run_cli(enclosing, 'init', ok=False)
        self.run_cli(enclosing / 'nested', 'init', ok=False)
        self.assertFalse((enclosing / 'nested').exists())
        self.assertEqual(before, {p: p.read_bytes() for p in CLI.parents[1].rglob('*') if p.is_file()})

    def test_refuse_escaping_state_directory(self):
        target = self.root / 'assignment'
        target.mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        try:
            (target / '.invo').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('Directory symlinks unavailable')
        self.run_cli(target, 'init', ok=False)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()

