"""One-off, fixed-ref genuine subtree repair. No credentials read or stored."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = 'https://github.com/myon-bioinformatics/Aoi.git'
BASE = '9f72b00e954cde61ab2c50cff4d5f41a709379ef'
BASE_BRANCH = 'research/shrink-index'
OUTPUT_BRANCH = 'repair/aoi-subtree-history-20261030'
STAGING_BRANCH = 'automation/aoi-history-sync-20261030'
UPSTREAM = {
    'dragowing': ('DRAgoWing', 'a71ad693e8a867bd5475095b66ba8998c5d9a556'),
    'nagoyaction': ('NagoyAction', 'c763cc80d3c18a11ae783dc1d8b890d5cbaaea29'),
}
OLD_NAGOY = 'dbd7bab6cf6ae2be60806898f5a9236439553d4b'
PARENT_FILES = {
    'child-heads.json', 'tests/test_child_registry.py',
    'tests/test_browser_startup_ci.py', 'tests/test_dragowing_browser_workflow.py',
    'distributions.json', 'docs/evidence/third-party-survey.json',
    'dist/blueprobe_min.py', 'dist/dragowing_min.py',
    'dist/pythdragoras_min.py', 'dist/sakanalytics_min.py',
}

def run(root, *args):
    return subprocess.check_output(args, cwd=root, text=True).strip()

def git(root, *args):
    return run(root, '/usr/bin/git', *args)

def require(value, message):
    if not value:
        raise RuntimeError(message)

def check_remote(root):
    current = git(root, 'ls-remote', REPO, 'refs/heads/' + BASE_BRANCH)
    require(current.split() == [BASE, 'refs/heads/' + BASE_BRANCH], 'base branch moved')
    require(not git(root, 'ls-remote', REPO, 'refs/heads/' + OUTPUT_BRANCH), 'repair branch already exists')

def validate(root):
    git(root, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    for prefix, (_, sha) in UPSTREAM.items():
        git(root, 'merge-base', '--is-ancestor', sha, 'HEAD')
        require(git(root, 'rev-parse', 'HEAD:' + prefix) == git(root, 'rev-parse', sha + '^{tree}'), 'subtree identity mismatch: ' + prefix)
    changed = set(git(root, 'diff', '--name-only', BASE, 'HEAD').splitlines())
    require(all(p.startswith('nagoyaction/') or p in PARENT_FILES for p in changed), 'unreviewed changed path')
    require(not git(root, 'status', '--porcelain'), 'dirty output')
    registry = json.loads((root / 'child-heads.json').read_text())
    for _, (name, sha) in UPSTREAM.items():
        require(registry['heads']['myon-bioinformatics/' + name]['sha'] == sha, 'registry mismatch')
    return git(root, 'rev-parse', 'HEAD')

def build(root, plan, scratch):
    require(git(root, 'rev-parse', 'HEAD') == BASE, 'checkout is not fixed base')
    require(not git(root, 'status', '--porcelain'), 'dirty input')
    check_remote(root)
    git(root, 'config', 'user.name', 'github-actions[bot]')
    git(root, 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    for prefix, (name, sha) in UPSTREAM.items():
        git(root, 'subtree', 'pull', '--prefix=' + prefix,
            'https://github.com/myon-bioinformatics/' + name + '.git', sha,
            '-m', 'Merge genuine ' + name + ' history without squash')
        require(git(root, 'rev-parse', 'HEAD^2') == sha, 'subtree merge did not retain upstream parent')
        require(git(root, 'rev-parse', 'HEAD:' + prefix) == git(root, 'rev-parse', sha + '^{tree}'), 'merge conflict or tree mismatch')
    source = git(root, 'rev-parse', 'HEAD')
    git(root, 'apply', '--check', str(plan / 'wrapper-contract.patch'))
    git(root, 'apply', str(plan / 'wrapper-contract.patch'))
    registry_path = root / 'child-heads.json'
    registry = json.loads(registry_path.read_text())
    registry['heads']['myon-bioinformatics/NagoyAction']['sha'] = UPSTREAM['nagoyaction'][1]
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    test_path = root / 'tests/test_child_registry.py'
    test_source = test_path.read_text()
    require(test_source.count(OLD_NAGOY) == 1, 'unexpected registry assertion')
    test_path.write_text(test_source.replace(OLD_NAGOY, UPSTREAM['nagoyaction'][1]))
    manifest_path = root / 'distributions.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['source'] = source
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    # Download only public, fixed Git objects; the compiler hash is mandatory.
    tool = scratch / 'compiler'
    sources = scratch / 'sources'
    tool.mkdir(parents=True)
    sources.mkdir()
    git(tool, 'init')
    git(tool, 'fetch', '--depth=1', 'https://github.com/myon-bioinformatics/myon-bioinformatics.git', manifest['tool']['commit'])
    compiler = tool / 'minpy.py'
    compiler.write_bytes(subprocess.check_output(['/usr/bin/git', 'show', 'FETCH_HEAD:' + manifest['tool']['source']], cwd=tool))
    require(hashlib.sha256(compiler.read_bytes()).hexdigest() == manifest['tool']['sha256'], 'compiler hash mismatch')
    queryu = sources / 'queryu'
    queryu.mkdir()
    git(queryu, 'init')
    git(queryu, 'fetch', '--depth=1', 'https://github.com/myon-bioinformatics/QueRyu.git', registry['heads']['myon-bioinformatics/QueRyu']['sha'])
    git(queryu, 'checkout', '--detach', 'FETCH_HEAD')
    distribution_args = ['-S', 'scripts/build_distributions.py', '--minpy', str(compiler), '--sources', str(sources)]
    run(root, sys.executable, *distribution_args)
    run(root, sys.executable, *distribution_args, '--check')
    run(root, sys.executable, '-S', 'scripts/survey_third_party.py', '--json', 'docs/evidence/third-party-survey.json')
    run(root, sys.executable, '-S', 'scripts/survey_third_party.py', '--check', 'docs/evidence/third-party-survey.json')
    git(root, 'diff', '--check')
    # Deterministic integration gates; real browser/full matrix remains mandatory on the Draft PR.
    run(root, sys.executable, '-m', 'pytest', '-q', 'nagoyaction/tests',
        'tests/test_child_registry.py', 'tests/test_browser_startup_ci.py',
        'tests/test_dragowing_browser_workflow.py',
        '--basetemp=' + str(scratch / 'pytest'), '--junitxml=' + str(scratch / 'focused.xml'))
    changed = set(git(root, 'diff', '--name-only').splitlines())
    require(changed <= PARENT_FILES, 'unexpected generated changes')
    git(root, 'add', '-u', '--', *sorted(changed))
    git(root, 'commit', '-m', 'Refresh parent records and preserve browser wrapper contracts after genuine subtree sync')
    head = validate(root)
    check_remote(root)
    (scratch / 'result.json').write_text(json.dumps({'base': BASE, 'head': head, 'tree': git(root, 'rev-parse', 'HEAD^{tree}'), 'branch': OUTPUT_BRANCH}) + '\n')
    return head

def publish(root):
    require(os.environ.get('GITHUB_REPOSITORY') == 'myon-bioinformatics/Aoi', 'wrong repository')
    require(os.environ.get('GITHUB_REF') == 'refs/heads/' + STAGING_BRANCH, 'wrong staging branch')
    require(os.environ.get('GITHUB_EVENT_NAME') == 'push', 'wrong event')
    require(os.environ.get('GITHUB_RUN_ATTEMPT') == '1', 'reruns prohibited')
    head = validate(root)
    check_remote(root)
    # Auth is injected ephemerally by the workflow through GIT_CONFIG_* only.
    # Empty expected value refuses any pre-existing destination, never rewrites it.
    git(root, 'push', '--force-with-lease=refs/heads/' + OUTPUT_BRANCH + ':', REPO,
        head + ':refs/heads/' + OUTPUT_BRANCH)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['build', 'publish'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--scratch', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.mode == 'build':
        require(args.scratch is not None, 'scratch required')
        build(root, Path(__file__).resolve().parent, args.scratch.resolve())
    else:
        publish(root)

if __name__ == '__main__':
    main()
