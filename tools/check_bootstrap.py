"""Project Backlog conventions, Gate 0 handoff, and PR change size."""

import argparse
from functools import cache
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from openharness.backlog import authorize, local_corpus
from openharness.repository import Repository
from check_gitflow import route, ai_review


EXPERIMENTS = {f'g0-{i}' for i in range(1, 7)}
GATE = 'g0-7'
LINE_LIMIT = 400
FILE_LIMIT = 10
STATUS = {'Blocked', 'To Do', 'In Progress', 'Done'}
CONFIG = '.harness/config.json'
REPORTS = 'docs/verification/gate0/'


def run(*argv):
    return subprocess.run(argv, check=True, capture_output=True, timeout=60).stdout.decode('utf-8')


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def production(path):
    return not (path.startswith('tests/') or path.endswith('.md'))


def read_blob(ref, path):
    return run('git', 'show', f'{ref}:{path}')


def gate_report(ref, item):
    report = read_blob(ref, f'{REPORTS}{item}.md')
    require(re.findall(r'^Result: (.+)$', report, re.M) == ['PASS'],
            f'{item}: the platform report must record exactly one PASS result')
    require(re.search(r'^Platform evidence: https://[^\s]+$', report, re.M),
            f'{item}: a platform evidence URL is required')
    return report


def report_pr(report, config):
    origin = f'https://github.com/{config["repository"]}/pull/'
    markers = re.findall(r'^Verification pull request: ' + re.escape(origin) + r'([1-9][0-9]*)$', report, re.M)
    require(len(markers) == 1, 'Each Gate 0 report must name exactly one verification PR')
    return int(markers[0])


def check_experiment_hashes(ref):
    summary = gate_report(ref, GATE)
    recorded = re.findall(r'^Experiment evidence: (.+)$', summary, re.M)
    expected = {f'{item} {sha256(gate_report(ref, item).encode()).hexdigest()}' for item in EXPERIMENTS}
    require(len(recorded) == len(expected) and set(recorded) == expected,
            'G0-VERIFY must record the SHA-256 of each of its six experiment reports')


def validate(repo, ref, config):
    observation = local_corpus(repo, ref, config['work'])
    tasks = observation['tasks']
    require({item for item, task in tasks.items() if task.get('milestone') == 'G0'}
            == EXPERIMENTS | {GATE}, 'Gate 0 must contain its six experiments and G0-VERIFY')
    require(set(tasks[GATE]['dependencies']) == EXPERIMENTS, 'G0-VERIFY must directly depend on all six experiments')
    require('G0-VERIFY' in tasks[GATE]['title'], 'The g0-7 title must identify G0-VERIFY')

    @cache
    def ancestors(item):
        direct = tasks[item]['dependencies']
        return set(direct).union(*(ancestors(parent) for parent in direct))

    scope = {}
    largest_budget = (0, 0)
    for item, task in tasks.items():
        milestone = task['milestone']
        require(milestone in {'G0', 'M0', 'M1', 'M2'} and item.startswith(milestone.lower() + '-'),
                f'{item}: unsupported milestone or ID')
        require(task.get('type') and task.get('priority') in {'high', 'medium', 'low'},
                f'{item}: type and priority required')
        require(task['status'] in STATUS, f'{item}: unsupported status')
        if milestone != 'G0':
            require(GATE in ancestors(item), f'{item}: must depend on G0-VERIFY')
        if task['status'] == 'Done':
            require(all(tasks[p]['status'] == 'Done' for p in ancestors(item)), f'{item}: unfinished prerequisite')
            if milestone == 'G0':
                report_pr(gate_report(ref, item), config)

        files = task.get('modified_files', [])
        require(files and len(files) == len(set(files)), f'{item}: unique exclusive paths required')
        if milestone == 'G0':
            require(f'{REPORTS}{item}.md' in files and all(
                p == f'{REPORTS}{item}.md' or item != GATE and p.startswith('experiments/gate0/') for p in files),
                f'{item}: Gate 0 may own only its evidence and minimal experiment files')
        for path in files:
            f = PurePosixPath(path)
            require(str(f) == path and not f.is_absolute() and '..' not in f.parts and
                    not re.search(r'[*?\[\]\\\s]', path), f'{item}: use exact repository-relative paths')
            for other in scope.get(path, []):
                require(other in ancestors(item) or item in ancestors(other),
                        f'{path}: {item} and {other} can be active at the same time')
            scope.setdefault(path, []).append(item)

    for name in run('git', 'ls-tree', '-rz', '--name-only', ref, '--', 'backlog/tasks').split('\0'):
        if not name.endswith('.md') or PurePosixPath(name).name.lower() == 'readme.md':
            continue
        item = PurePosixPath(name).name.split(' - ', 1)[0].lower()
        document = read_blob(ref, name)
        budget = re.search(r'^生产改动预算（变更行 / 文件） ([0-9]+) / ([0-9]+)$', document, re.M)
        require(budget and re.search(r'^## Acceptance criteria\n\n- \[[ x]\] \S', document, re.M)
                and re.search(r'^## Verification evidence\n\n- \S', document, re.M),
                f'{item}: budget, acceptance criteria, and verification evidence required')
        lines, files = map(int, budget.groups())
        owned_count = sum(map(production, tasks[item]['modified_files']))
        require(lines <= LINE_LIMIT and files <= FILE_LIMIT and files == owned_count,
                f'{item}: budget exceeds limits or does not match owned production paths')
        require(bool(lines) == bool(files), f'{item}: line and file budgets disagree')
        largest_budget = max(largest_budget[0], lines), max(largest_budget[1], files)
    print(f'Backlog: {len(tasks)} tasks, {sum(len(t["dependencies"]) for t in tasks.values())} dependencies, '
          f'{len(scope)} owned paths; largest budget {largest_budget[0]} lines / {largest_budget[1]} files')
    if tasks[GATE]['status'] == 'Done':
        check_experiment_hashes(ref)
    return observation


def changes(base, head):
    changed = {}
    for entry in run('git', 'diff', '--numstat', '-z', '--no-renames', base, head, '--').split('\0'):
        if entry:
            added, deleted, path = entry.split('\t', 2)
            require(not production(path) or added != '-', f'{path}: keep production binary artifacts out of these PRs')
            changed[path] = int(added) + int(deleted) if added != '-' else 0
    counted = [lines for path, lines in changed.items() if production(path)]
    require(len(counted) <= FILE_LIMIT and sum(counted) <= LINE_LIMIT,
            f'Production limit exceeded: {sum(counted)} lines / {len(counted)} files')
    print(f'PR: {sum(counted)} production lines / {len(counted)} files; {len(changed)} changed paths total')
    return set(changed)


def verify_report_merge(repo, base, config, item):
    report = gate_report(base, item)
    number = report_pr(report, config)
    endpoint = f'repos/{config["repository"]}/pulls/{number}'
    pull = json.loads(run('gh', 'api', endpoint))
    require(pull['merged'] and pull['base']['ref'] == config['target'] and
            re.findall(r'^Work-Item: (\S+)$', pull['body'] or '', re.M) == [item],
            f'{item}: PR #{number} must be merged on the target branch for this task')
    merge = pull['merge_commit_sha']
    require(re.fullmatch(r'[0-9a-f]{40}', merge or ''), f'{item}: merge SHA unavailable')
    run('git', 'merge-base', '--is-ancestor', merge, base)
    before = local_corpus(repo, f'{merge}^1', config['work'])['tasks']
    after = local_corpus(repo, merge, config['work'])['tasks']
    require(before[item]['status'] != 'Done' and after[item]['status'] == 'Done',
            f'{item}: PR #{number} must be the merge that completed this task')
    require(gate_report(merge, item) == report, f'{item}: the report changed after its PR merged')
    return number, endpoint, pull, merge


def verify_merged_gate(repo, base, config, require_main=True):
    number, endpoint, pull, merge = verify_report_merge(repo, base, config, GATE)
    require(all(gate_report(merge, item) == gate_report(base, item) for item in EXPERIMENTS | {GATE}),
            'Gate 0 evidence changed after review; resolve the discrepancy before proceeding')
    ai_review(config, pull)
    if require_main:
        main = json.loads(run('gh', 'api', f'repos/{config["repository"]}/git/ref/heads/main'))['object']['sha']
        run('git', 'merge-base', '--is-ancestor', merge, main)
        require(all(gate_report(main, item) == gate_report(base, item) for item in EXPERIMENTS | {GATE}),
                'First Gate 0 evidence must be released into main before M0–M2')
    print(f'G0-VERIFY: PR #{number}, merged at {merge}, independent AI review observed')


def validate_pr(repo, base, head, candidate, config, event):
    if event:
        pr = event['pull_request']
        require(run('git', 'rev-parse', f'{head}^1', f'{head}^2').splitlines() ==
                [base, pr['head']['sha']], 'Test the exact GitHub PR merge candidate')
        if route(base, head, config, event):
            if pr['head']['ref'] != 'main':
                verify_merged_gate(repo, head, config, require_main=pr['head']['ref'].startswith('hotfix/'))
                if not pr['head']['ref'].startswith('release/'):
                    changes(base, head)
            ai_review(config, pr)
            return
    changed = changes(base, head)
    tracks_tasks = run('git', 'ls-tree', '--name-only', base, '--', CONFIG).strip()
    tasks = candidate['tasks']
    pr = event['pull_request'] if event else None
    matches = re.findall(r'^Work-Item: (\S+)$', pr['body'] or '', re.M) if pr else []
    if pr:
        require(run('git', 'rev-parse', f'{head}^1', f'{head}^2').splitlines() ==
                [base, pr['head']['sha']], 'Test the exact GitHub PR merge candidate')
    require(len(matches) <= 1, 'Use one Work-Item line')
    item = matches[0].lower() if matches else None
    maintenance = {'.gitattributes', '.gitignore', 'README.md', 'AGENTS.md', 'BACKLOG.md', 'tools/check_bootstrap.py', 'tools/check_gitflow.py',
                   'docs/architecture/gitflow.md', 'docs/plans/2026-11-20-gitflow.md',
                   'docs/architecture/community-implementations.md', 'docs/architecture/product-baseline.md',
                   'docs/architecture/release-roadmap.md', 'docs/architecture/ui-art-direction.md',
                    'docs/architecture/requirements-and-gaps.md', 'docs/verification/bootstrap.md'}
    maintenance |= {p for p in changed if p.startswith(('.github/', '.harness/', 'backlog/tasks/', 'tests/'))}
    if not tracks_tasks:
        require(not any(t['status'] == 'Done' for t in tasks.values()) and all(
            path in maintenance or path.startswith(('docs/architecture/', 'docs/verification/bootstrap'))
            for path in changed), 'Initial bootstrap must only stage the plan and controls')
        return

    baseline_config = json.loads(read_blob(base, CONFIG))
    baseline = local_corpus(repo, base, baseline_config['work'])
    old = baseline['tasks']
    finished = {k for k in tasks if tasks[k]['status'] == 'Done' and old.get(k, {}).get('status') != 'Done'}
    active_paths = changed - maintenance
    downstream = {p for p in active_paths if not p.startswith(('experiments/gate0/', REPORTS))}
    if downstream or finished - EXPERIMENTS - {GATE}:
        require(all(old[k]['status'] == 'Done' for k in EXPERIMENTS | {GATE}),
                'G0-VERIFY and all six passes must already be on target before downstream work')
        if event:
            verify_merged_gate(repo, base, baseline_config)
    if not event:
        return
    if not item:
        require(not finished and not active_paths, 'Work or completion changes require one Work-Item')
        ai_review(config, pr)
        return

    authorize(baseline, baseline_config['work'], item, pr['user']['login'])
    require(item in tasks, 'A task PR must preserve its own Backlog record')
    require(pr['base']['ref'] == 'develop' and pr['head']['ref'] == f'task/{item}' and
            pr['head']['repo']['full_name'] == config['repository'], 'Use same-repository task/<id> into develop')
    task_path_prefix = f'backlog/tasks/{item} - '
    require(all(path in old[item]['modified_files'] or path.startswith(task_path_prefix) for path in changed),
            f'{item}: PR includes a path outside its baseline ownership')
    require(finished <= {item}, 'A task PR can close only its own task')
    ai_review(config, pr)
    if item in finished and item in EXPERIMENTS | {GATE}:
        require(report_pr(gate_report(head, item), config) == pr['number'], f'{item}: evidence must bind this PR')
        if item == GATE:
            for experiment in sorted(EXPERIMENTS):
                verify_report_merge(repo, base, baseline_config, experiment)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Exact target commit for PR-size and Gate 0 checks')
    parser.add_argument('--event', type=Path, help='GitHub pull_request event payload; enables native checks')
    args = parser.parse_args()
    repo = Repository('.')
    head = repo.revision('HEAD')
    config = repo.config()
    candidate = validate(repo, head, config)
    if args.base:
        event = json.loads(args.event.read_text(encoding='utf-8')) if args.event else None
        validate_pr(repo, repo.revision(args.base), head, candidate, config, event)
    elif args.event:
        parser.error('--event requires --base')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc)) from exc
