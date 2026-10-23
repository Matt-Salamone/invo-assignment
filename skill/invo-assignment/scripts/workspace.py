"""Explicit-root assignment operations. All successful commands emit JSON."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

SKILL_ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = '.invo/state.json'


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def inside(path, parent):
    return path == parent or parent in path.parents


def tooling_roots():
    roots = [SKILL_ROOT]
    for parent in SKILL_ROOT.parents:
        if (parent / 'AGENTS.md').exists() and (parent / 'skill/invo-assignment').exists():
            roots.append(parent)
            # A linked development worktree also protects its primary checkout.
            common = git(parent, 'rev-parse', '--git-common-dir')
            common = (parent / common).resolve()
            if common.name == '.git':
                roots.append(common.parent)
            break
    return roots


def safe_path(root, relative):
    path = (root / relative).resolve()
    if not inside(path, root) or path == root:
        raise ValueError('Workspace path escapes its root')
    return path


def validate_root(root):
    if any(inside(root, p) for p in tooling_roots()):
        raise ValueError('Assignment target is inside source or installed tooling')
    for parent in root.parents:
        if (parent / '.git').exists() or (parent / STATE_FILE).exists():
            raise ValueError('Assignment target is inside another repository; select a separate directory')
    if root.exists() and not root.is_dir():
        raise ValueError('Workspace must be a directory')


def load_state(root):
    path = safe_path(root, STATE_FILE)
    state = json.loads(path.read_text(encoding='utf-8'))
    if state.get('state_version') != 1 or not state.get('assignment_id'):
        raise ValueError('Unsupported or invalid assignment state')
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise ValueError('Assignment repository root does not match workspace')
    return state


def save_state(root, state):
    path = safe_path(root, STATE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = safe_path(root, '.invo/state.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def initialize(root, name):
    if safe_path(root, STATE_FILE).exists():
        return load_state(root)
    if (root / '.git').exists():
        raise ValueError('Existing repository has no assignment state; choose a new directory')
    root.mkdir(parents=True, exist_ok=True)
    git(root, 'init')
    state = {'state_version': 1, 'assignment_id': str(uuid.uuid4()),
             'name': name or root.name, 'skill_version': (SKILL_ROOT / 'VERSION').read_text().strip(),
             'status': 'intake', 'next_action': 'capture-requirements'}
    save_state(root, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Initialize or resume a separate local assignment')
    init.add_argument('--name')
    commands.add_parser('status', help='Recover assignment identity, saved status and next action')
    args = parser.parse_args()
    try:
        root = args.workspace.expanduser().resolve()
        validate_root(root)
        state = initialize(root, args.name) if args.command == 'init' else load_state(root)
        print(json.dumps(state, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
