"""Explicit-root assignment operations. All successful commands emit JSON."""
import argparse
import json
import hashlib
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


def required(record, fields):
    if not isinstance(record, dict) or any(field not in record for field in fields):
        raise ValueError('Missing required fields: ' + ', '.join(fields))


def intake_save(root, state, payload):
    fields = ('deliverables', 'constraints', 'grading_criteria', 'uncertainties', 'assumptions', 'sources')
    required(payload, fields)
    if any(not isinstance(payload[f], list) for f in fields) or not payload['deliverables']:
        raise ValueError('Intake fields must be lists, with at least one deliverable')
    if state.get('intake'):
        raise ValueError('Intake already saved; retain the original intake record')
    ids = set()
    copies = []
    for source in payload['sources']:
        required(source, ('id', 'kind', 'status', 'reference'))
        sid = source['id']
        if not isinstance(sid, str) or not sid or not all(c.isalnum() or c in '-_' for c in sid) or sid in ids:
            raise ValueError('Source IDs must be unique letters, numbers, hyphens or underscores')
        ids.add(sid)
        if source['kind'] not in ('course', 'external') or source['status'] not in ('usable', 'conversion-needed', 'unavailable', 'unreadable'):
            raise ValueError('Invalid source kind or status')
        if not source['reference']:
            raise ValueError('Source reference is required')
        if source.get('path'):
            content = Path(source['path']).read_bytes()
            relative = 'materials/originals/' + sid + Path(source['path']).suffix
            destination = safe_path(root, relative)
            if destination.exists():
                raise ValueError('Original destination already exists')
            copies.append((destination, content))
            source['original'] = relative
            source['sha256'] = hashlib.sha256(content).hexdigest()
        elif source['status'] in ('usable', 'conversion-needed') and source['kind'] == 'course':
            raise ValueError('Available course material requires an original file')
    for destination, content in copies:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    state['intake'] = payload
    state['next_action'] = 'create-worked-solution'
    save_state(root, state)
    return state


def conversion(root, state, operation, payload):
    required(payload, ('id',))
    records = state.setdefault('conversions', {})
    cid = payload['id']
    if not isinstance(cid, str) or not cid:
        raise ValueError('Conversion ID required')
    if operation == 'conversion-propose':
        required(payload, ('source_id', 'tool', 'output', 'fidelity_limits', 'source_reference'))
        if cid in records or not all(isinstance(v, str) and v.strip() for v in payload.values()):
            raise ValueError('Conversion needs unique ID and nonempty explanation fields')
        sources = state.get('intake', {}).get('sources', [])
        if not any(s['id'] == payload['source_id'] and s.get('original') for s in sources):
            raise ValueError('Conversion must identify a preserved original')
        output = safe_path(root, payload['output'])
        if not inside(output, safe_path(root, 'materials/derived')) or output.exists():
            raise ValueError('Conversion output must be a new file in materials/derived')
        records[cid] = dict(payload, status='proposed')
    else:
        if cid not in records:
            raise ValueError('Unknown conversion')
        record = records[cid]
        if operation == 'conversion-decide':
            required(payload, ('decision', 'decision_record'))
            if record['status'] != 'proposed' or payload['decision'] not in ('approved', 'declined', 'unavailable') or not isinstance(payload['decision_record'], str) or not payload['decision_record'].strip():
                raise ValueError('A proposed conversion requires an actual decision record')
            record.update(status=payload['decision'], decision_record=payload['decision_record'])
        else:
            required(payload, ('artifact',))
            if record['status'] != 'approved':
                raise ValueError('Conversion requires approval before execution and registration')
            content = Path(payload['artifact']).read_bytes()
            output = safe_path(root, record['output'])
            if output.exists():
                raise ValueError('Preserve existing derivative; propose another conversion')
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            record.update(status='complete', sha256=hashlib.sha256(content).hexdigest())
    save_state(root, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Initialize or resume a separate local assignment')
    init.add_argument('--name')
    commands.add_parser('status', help='Recover assignment identity, saved status and next action')
    commands.add_parser('intake-save', help='Persist requirements and preserve source originals').add_argument('--input', required=True, type=Path)
    for name in ('conversion-propose', 'conversion-decide', 'conversion-complete'):
        commands.add_parser(name).add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    try:
        root = args.workspace.expanduser().resolve()
        validate_root(root)
        state = initialize(root, args.name) if args.command == 'init' else load_state(root)
        if args.command == 'intake-save':
            state = intake_save(root, state, json.loads(args.input.read_text(encoding='utf-8')))
        elif args.command.startswith('conversion-'):
            state = conversion(root, state, args.command, json.loads(args.input.read_text(encoding='utf-8')))
        print(json.dumps(state, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
