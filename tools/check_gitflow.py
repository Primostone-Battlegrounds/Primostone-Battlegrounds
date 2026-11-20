"""PR routing and release provenance for the project's GitFlow contract."""
import json
import re
import subprocess


def run(*argv):
    return subprocess.run(argv, check=True, capture_output=True, timeout=60).stdout.decode('utf-8').strip()


def require(value, detail):
    if not value:
        raise ValueError(detail)


def api(config, path):
    return json.loads(run('gh', 'api', f'repos/{config["repository"]}/{path}'))


def ancestor(older, newer):
    run('git', 'merge-base', '--is-ancestor', older, newer)


def review_record(review, head):
    body = review.get('body') or ''
    fields = {key: re.findall(r'^' + key + r': (\S+)$', body, re.M)
              for key in ('AI-Review', 'Reviewed-Head', 'Reviewer-Agent', 'Implementer-Agent')}
    return (review.get('commit_id') == head and review.get('state') in {'COMMENTED', 'APPROVED'}
            and all(len(values) == 1 for values in fields.values())
            and fields['AI-Review'] == ['PASS'] and fields['Reviewed-Head'] == [head]
            and fields['Reviewer-Agent'] != fields['Implementer-Agent']
            and bool(re.search(r'^## Findings\n\S', body, re.M))
            and bool(re.search(r'^## Verification\n\S', body, re.M)))


def ai_review(config, pr):
    pages = json.loads(run('gh', 'api', '--paginate', '--slurp',
                         f'repos/{config["repository"]}/pulls/{pr["number"]}/reviews'))
    records = [r for page in pages for r in page if r.get('submitted_at') and
               (not pr.get('merged_at') or r['submitted_at'] <= pr['merged_at'])]
    observed = [(r.get('commit_id'), r.get('state'), r.get('author_association'),
                 review_record(r, pr['head']['sha'])) for r in records]
    records = [r for r in records if r.get('commit_id') == pr['head']['sha'] and
               r.get('author_association') in {'OWNER', 'MEMBER', 'COLLABORATOR'} and
               re.search(r'^AI-Review: ', r.get('body') or '', re.M)]
    require(records and review_record(max(records, key=lambda r: (r['submitted_at'], r['id'])), pr['head']['sha']),
            f'PR #{pr["number"]} needs independent AI review for {pr["head"]["sha"]}; observed {observed}')


def reviewed(config, pr):
    require(pr['merged_at'], 'Release provenance requires actually merged PRs')
    ai_review(config, pr)


def release(base, head, config, pr):
    branch = pr['head']['ref']
    version = branch.removeprefix('release/') if branch.startswith('release/') else None
    if version is None:
        markers = re.findall(r'^Release-Version: (\S+)$', pr['body'] or '', re.M)
        require(len(markers) == 1, 'Hotfix requires one Release-Version')
        version = markers[0]
    require(re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version), 'Use stable SemVer X.Y.Z')
    path = f'docs/releases/{version}.json'
    manifest = json.loads(run('git', 'show', f'{head}:{path}'))
    require(isinstance(manifest, dict) and {'version', 'source', 'candidate', 'artifacts', 'task_prs',
            'fix_prs', 'validation_evidence'} <= manifest.keys(), 'Incomplete release manifest')
    require(manifest['version'] == version and re.fullmatch(r'https://\S+', manifest['validation_evidence']),
            'Release version and validation evidence must match')
    source, candidate = manifest['source'], manifest['candidate']
    pr['_release_source'] = source
    require(all(re.fullmatch('[0-9a-f]{40}', sha) for sha in (source, candidate)), 'Use exact release SHAs')
    ancestor(base, source)
    ancestor(source, candidate)
    ancestor(candidate, pr['head']['sha'])
    require(run('git', 'diff', '--name-only', candidate, pr['head']['sha']).splitlines() == [path],
            'Release head must contain only its manifest after the exact tested candidate')
    artifacts = manifest['artifacts']
    require(artifacts and all(set(a) == {'name', 'sha256', 'url'} and a['name'] and
            re.fullmatch('[0-9a-f]{64}', a['sha256']) and re.fullmatch(r'https://\S+', a['url'])
            for a in artifacts), 'Release artifacts require names, SHA-256 and immutable evidence URLs')
    if branch.startswith('hotfix/'):
        latest = api(config, 'releases/latest')
        tag = latest['tag_name']
        require(re.fullmatch(r'v\d+\.\d+\.\d+', tag), 'Hotfix requires an existing stable release')
        x, y, z = map(int, tag[1:].split('.'))
        require(version == f'{x}.{y}.{z + 1}', 'Hotfix must increment the published patch version')
        require(run('git', 'rev-list', '-n', '1', tag) == base,
                'Hotfix base must be the exact latest published main release')
        require(source == base and not manifest['task_prs'], 'Hotfix starts from the released main baseline')
    else:
        ancestor(source, api(config, 'git/ref/heads/develop')['object']['sha'])
        require(not manifest['task_prs'] or len(set(manifest['task_prs'])) == len(manifest['task_prs']),
                'Duplicate task provenance')
        observed = []
        for sha in run('git', 'rev-list', '--first-parent', f'{base}..{source}').splitlines():
            pulls = api(config, f'commits/{sha}/pulls')
            matches = [p for p in pulls if p['merge_commit_sha'] == sha and p['base']['ref'] == 'develop']
            require(len(matches) == 1, f'{sha}: release source requires reviewed develop PR merges')
            pull = api(config, f'pulls/{matches[0]["number"]}')
            reviewed(config, pull)
            if re.search(r'^Work-Item: \S+$', pull['body'] or '', re.M):
                observed.append(pull['number'])
        require(set(observed) == set(manifest['task_prs']) and observed,
                'Release manifest must enumerate all newly merged task PRs')
    fixes = set()
    for number in manifest['fix_prs']:
        pull = api(config, f'pulls/{number}')
        require(pull['base']['ref'] == branch, 'Release fixes must be reviewed on this release branch')
        reviewed(config, pull)
        fixes.add(pull['merge_commit_sha'])
    if branch.startswith('release/'):
        require(set(run('git', 'rev-list', '--first-parent', f'{source}..{candidate}').splitlines()) == fixes,
                'Every release correction must be a reviewed fix PR merge')
    print(f'Release {version}: source {source}, tested candidate {candidate}, {len(artifacts)} artifact digests')


def route(base, head, config, event):
    pr = event['pull_request']
    branch, target = pr['head']['ref'], pr['base']['ref']
    require(pr['head']['repo']['full_name'] == config['repository'], 'Use the same repository')
    items = re.findall(r'^Work-Item: (\S+)$', pr['body'] or '', re.M)
    if pr['number'] == 2 and branch == 'codex/backlog-release-planning' and target == 'main' and not items:
        ancestor('ae8910510b1c90c866c3b6f59ba704268d98e5b7', pr['head']['sha'])
        return False
    # Explicit one-time governance exception. It cannot authorize task completion.
    if pr['number'] == 3 and branch == 'chore/gitflow-migration' and target == 'main' and not items:
        return False
    if target == 'develop':
        if branch == 'main' and not items:
            require(pr['head']['sha'] == api(config, 'git/ref/heads/main')['object']['sha'],
                    'Synchronization must use current main')
            print('Synchronization: exact main to develop; independent AI review required')
            return True
        if items:
            require(len(items) == 1 and branch == f'task/{items[0]}', 'Use task/<id> for task PRs')
        else:
            require(branch.startswith('chore/'), 'develop accepts task/<id>, chore/* or current main')
        return False
    if target.startswith('release/') and branch.startswith('chore/release-fix-') and not items:
        return True
    require(target == 'main' and branch.startswith(('release/', 'hotfix/')) and not items,
            'main accepts release/* and hotfix/* PRs only')
    release(base, head, config, pr)
    return True
