"""Default-branch-only ADD/HOLD runner. Never removes labels or executes PR code."""
import json
import os
import re
import subprocess
from urllib.parse import urlsplit, parse_qs


# ---- 読み取りだけのページ送り（旧 ci_label_api.py。Strict read-only pagination shared by the ADD-only runner. No removal policy）
SHA = re.compile(r'[0-9a-f]{40}\Z')
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
BAD = {'failure', 'timed_out', 'action_required', 'startup_failure'}


def _repo(value):
    if not isinstance(value, str) or not REPO.fullmatch(value) or any(p in ('.', '..') for p in value.split('/')):
        raise ValueError('explicit owner/repository required')
    return 'repos/' + value


def pages(request, path, key=None):
    """Strict sequential Link pages; stable check totals and unique item IDs."""
    rows, ids, total, page = [], set(), None, 1
    stem = path + ('&' if '?' in path else '?') + 'per_page=100&page='
    while True:
        data, next_path = request(stem + str(page))
        batch = data.get(key) if key and isinstance(data, dict) else data if key is None else None
        if not isinstance(batch, list) or len(batch) > 100:
            raise ValueError('invalid page')
        if key:
            count = data.get('total_count')
            if type(count) is not int or count < 0 or total is not None and count != total:
                raise ValueError('unstable total')
            total = count
        for row in batch:
            if not isinstance(row, dict) or type(row.get('id')) is not int or row['id'] in ids:
                raise ValueError('invalid/duplicate record')
            ids.add(row['id']); rows.append(row)
        if next_path is None:
            if total is not None and len(rows) != total:
                raise ValueError('incomplete pagination')
            return rows
        if not batch or next_path != stem + str(page + 1):
            raise ValueError('unexpected/cyclic pagination link')
        page += 1
        if page > 1000:
            raise ValueError('pagination budget exhausted; never complete')


def open_pulls(repository, request):
    return pages(request, _repo(repository) + '/pulls?state=open')

def request(path, method='GET', payload=None):
    # gh supplies authentication; never print token or arbitrary response headers.
    if not path.startswith(_repo(os.environ['GH_REPO']) + '/'):
        raise ValueError('foreign repository request')
    args = ['gh', 'api', '--include', '--method', method, path]
    if payload is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, check=True)
    headers, body = result.stdout.replace('\r\n', '\n').split('\n\n', 1)
    links = []
    for line in headers.splitlines():
        if line.lower().startswith('link:'):
            links.extend(re.findall(r'<([^>]+)>; rel="next"', line))
    if len(links) > 1:
        raise ValueError('ambiguous pagination')
    next_path = None
    if links:
        u = urlsplit(links[0])
        if u.scheme != 'https' or u.netloc != 'api.github.com' or u.fragment:
            raise ValueError('foreign pagination')
        # GitHub may reorder query parameters; normalize without losing filters.
        q = parse_qs(u.query, strict_parsing=True)
        if any(len(v) != 1 for v in q.values()):
            raise ValueError('duplicate pagination parameter')
        original = parse_qs(urlsplit(path).query)
        if set(q) != set(original) or any(q[k] != original[k] for k in q if k != 'page'):
            raise ValueError('changed pagination filter')
        next_path = path.rsplit('page=', 1)[0] + 'page=' + q['page'][0]
        if u.path.lstrip('/') != urlsplit(path).path:
            raise ValueError('changed pagination endpoint')
    return json.loads(body), next_path


def confirmed_failure(repo, number, get):
    """Complete snapshot, known Actions provenance, stable PR head; else HOLD."""
    base = _repo(repo)
    before, _ = get(f'{base}/pulls/{number}')
    head = before.get('head', {}).get('sha')
    if before.get('state') != 'open' or not isinstance(head, str) or not SHA.fullmatch(head):
        return None
    checks = pages(get, f'{base}/commits/{head}/check-runs?filter=latest', 'check_runs')
    statuses = pages(get, f'{base}/commits/{head}/statuses')
    # Read legacy statuses completely, but no trusted creator inventory is
    # configured: legacy failures cannot authorize ADD in this initial policy.
    if any(not isinstance(s.get('context'), str) or not s['context'] or
           type(s.get('creator', {}).get('id')) is not int for s in statuses):
        return None
    if any(c.get('head_sha') != head for c in checks):
        return None
    evidence = []
    for c in checks:
        if c.get('status') != 'completed' or c.get('conclusion') not in BAD:
            continue
        app = c.get('app', {})
        suite = c.get('check_suite', {}).get('id')
        if app.get('id') != 15368 or app.get('slug') != 'github-actions' or type(suite) is not int:
            continue
        runs = pages(get, f'{base}/actions/runs?head_sha={head}', 'workflow_runs')
        for run in runs:
            if (run.get('check_suite_id') != suite or run.get('head_sha') != head or
                run.get('repository', {}).get('full_name') != repo or
                run.get('status') != 'completed' or run.get('conclusion') not in BAD or
                type(run.get('workflow_id')) is not int):
                continue
            workflow, _ = get(f"{base}/actions/workflows/{run['workflow_id']}")
            if (workflow.get('id') != run['workflow_id'] or
                not re.fullmatch(r'\.github/workflows/[^/]+\.ya?ml', workflow.get('path', ''))):
                continue
            evidence.append((c['id'], run['id'], run['workflow_id']))
    after, _ = get(f'{base}/pulls/{number}')
    if after.get('state') != 'open' or after.get('head', {}).get('sha') != head or not evidence:
        return None
    return head, evidence


def process(repo, number, get, write):
    # Two complete observations prevent adding from a failure superseded during
    # collection. A final head read narrows, but cannot atomically eliminate, race.
    first = confirmed_failure(repo, number, get)
    if first is None or confirmed_failure(repo, number, get) != first:
        return 'HOLD'
    current, _ = get(f'{_repo(repo)}/pulls/{number}')
    if current.get('state') != 'open' or current.get('head', {}).get('sha') != first[0]:
        return 'HOLD'
    write(f'{_repo(repo)}/issues/{number}/labels', 'POST', {'labels': ['status:ci-failing']})
    return 'ADD'


def scan(repo, get, write):
    pulls = open_pulls(repo, get)
    print(f'SCAN open_prs={len(pulls)}')
    for pr in pulls:
        try:
            print(pr['number'], process(repo, pr['number'], get, write))
        except (ValueError, TypeError, KeyError, AttributeError, OSError, subprocess.CalledProcessError):
            print(pr.get('number'), 'HOLD: incomplete or invalid evidence')


if __name__ == '__main__':
    scan(os.environ['GH_REPO'], request, request)
