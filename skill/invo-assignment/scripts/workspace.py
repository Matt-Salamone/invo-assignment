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


def solution_save(root, state, payload):
    required(payload, ('artifacts', 'checks', 'limitations'))
    if state.get('solution'):
        raise ValueError('Initial solution exists; use correction operations for later changes')
    if not state.get('intake') or not isinstance(payload['checks'], list) or not isinstance(payload['limitations'], list) or not payload['artifacts']:
        raise ValueError('Solution requires intake, artifacts, checks and limitations')
    checked = set()
    for check in payload['checks']:
        required(check, ('deliverable', 'result', 'method', 'evidence', 'rubric_coverage'))
        if check['result'] not in ('passed', 'failed', 'limited') or not check['method'] or not check['evidence'] or not isinstance(check['rubric_coverage'], list):
            raise ValueError('Checks need result, method, evidence and rubric coverage')
        checked.add(check['deliverable'])
    if not set(state['intake']['deliverables']).issubset(checked):
        raise ValueError('Every required deliverable needs a verification record')
    covered = {criterion for check in payload['checks'] for criterion in check['rubric_coverage']}
    if not set(state['intake']['grading_criteria']).issubset(covered):
        raise ValueError('Every grading criterion needs recorded coverage')
    if any(check['result'] != 'passed' for check in payload['checks']) and not payload['limitations']:
        raise ValueError('Failed or limited checks need explicit limitations')
    outputs = {}
    for artifact in payload['artifacts']:
        required(artifact, ('source', 'path'))
        destination = safe_path(root, 'solution/' + artifact['path'])
        if not inside(destination, safe_path(root, 'solution')) or destination.name == 'verification.json' or destination.exists() or destination in outputs:
            raise ValueError('Solution artifact must be a unique new file under solution')
        outputs[destination] = Path(artifact['source']).read_bytes()
    verification = safe_path(root, 'solution/verification.json')
    if verification.exists():
        raise ValueError('Existing solution verification must be preserved')
    outputs[verification] = (json.dumps({'checks': payload['checks'], 'limitations': payload['limitations']}, indent=2) + '\n').encode()
    if git(root, 'diff', '--cached', '--name-only'):
        raise ValueError('Unrelated staged changes must be committed or unstaged before saving solution')
    for destination, content in outputs.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    git(root, 'add', '--', 'solution')
    git(root, '-c', 'user.name=invo-assignment', '-c', 'user.email=invo-assignment@localhost', 'commit', '-m', 'Save initial worked solution and verification')
    state['solution'] = {'revision': git(root, 'rev-parse', 'HEAD'), 'artifacts': ['solution/' + a['path'] for a in payload['artifacts']], 'checks': payload['checks'], 'limitations': payload['limitations']}
    state.update(status='solution-ready', next_action='propose-teaching-plan')
    save_state(root, state)
    return state


def write_plan(root, plan):
    path = safe_path(root, 'teaching/plan.md')
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ['# Teaching plan', '', 'Status: ' + plan['status'], 'Version: ' + str(plan['version']), '', plan['scope'], '', 'Pacing: ' + plan['pacing']]
    if plan.get('decision_record'):
        lines += ['', 'Approval: ' + plan['decision_record']]
    for lesson in plan['lessons']:
        lines += ['', '## ' + lesson['title'], 'Lesson ID: ' + lesson['id'], 'Minutes: ' + str(lesson['minutes']), 'Progress: ' + lesson['progress'], 'Prerequisites: ' + ', '.join(lesson['prerequisites'])]
        lines += ['- ' + objective for objective in lesson['objectives']]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def plan_operation(root, state, operation, payload):
    if not state.get('solution'):
        raise ValueError('Save the worked solution before planning lessons')
    if operation == 'plan-propose':
        required(payload, ('scope', 'pacing', 'lessons'))
        if state.get('plan', {}).get('status') == 'approved':
            raise ValueError('Approved plans require adaptation operations')
        if not payload['scope'] or not payload['pacing'] or not isinstance(payload['lessons'], list) or not payload['lessons']:
            raise ValueError('Plan requires scope, pacing and lessons')
        ids = set()
        for lesson in payload['lessons']:
            required(lesson, ('id', 'kind', 'title', 'objectives', 'prerequisites', 'minutes'))
            if not isinstance(lesson['id'], str) or not lesson['id'] or lesson['id'] in ids or not lesson['title'] or not isinstance(lesson['objectives'], list) or not lesson['objectives'] or not isinstance(lesson['prerequisites'], list) or not isinstance(lesson['minutes'], int) or lesson['minutes'] <= 0:
                raise ValueError('Lessons require unique IDs, objectives, prerequisites and positive minutes')
            ids.add(lesson['id'])
            lesson['progress'] = 'not-started'
        if payload['lessons'][0]['kind'] != 'instructions':
            raise ValueError('First lesson must address assignment instructions')
        old = state.get('plan')
        if old:
            state.setdefault('plan_history', []).append(old)
        plan = dict(payload, version=(old['version'] + 1 if old else 1), status='proposed')
        state['plan'] = plan
        state['next_action'] = 'approve-teaching-plan'
    else:
        required(payload, ('version', 'decision_record'))
        plan = state.get('plan')
        if not plan or plan['status'] != 'proposed' or plan['version'] != payload['version'] or not isinstance(payload['decision_record'], str) or not payload['decision_record'].strip():
            raise ValueError('Approval requires current proposed version and actual student decision')
        plan.update(status='approved', decision_record=payload['decision_record'])
        state.update(status='teaching', next_action='request-lesson')
    write_plan(root, state['plan'])
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
    for name in ('conversion-propose', 'conversion-decide', 'conversion-complete', 'solution-save', 'plan-propose', 'plan-approve'):
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
        elif args.command == 'solution-save':
            state = solution_save(root, state, json.loads(args.input.read_text(encoding='utf-8')))
        elif args.command.startswith('plan-'):
            state = plan_operation(root, state, args.command, json.loads(args.input.read_text(encoding='utf-8')))
        print(json.dumps(state, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
