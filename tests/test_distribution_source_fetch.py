"""A rewritten branch must still fetch the approved distribution snapshot."""
import json
from pathlib import Path
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args, check=True):
    result = subprocess.run(['git', '-C', str(root), *args],
                            capture_output=True, text=True)
    if check:
        assert result.returncode == 0, result.stderr
    return result


def test_frozen_source_fetch_survives_rewritten_shallow_history(tmp_path):
    origin = tmp_path / 'origin'
    origin.mkdir()
    git(origin, 'init', '-b', 'original')
    git(origin, 'config', 'user.email', 'test@example.invalid')
    git(origin, 'config', 'user.name', 'Test')
    (origin / 'snapshot').write_text('approved source\n')
    git(origin, 'add', '.')
    git(origin, 'commit', '-m', 'approved')
    approved = git(origin, 'rev-parse', 'HEAD').stdout.strip()
    git(origin, 'checkout', '--orphan', 'rewritten')
    git(origin, 'rm', '-f', 'snapshot')
    manifest = json.dumps({'source': approved})
    (origin / 'distributions.json').write_text(manifest)
    git(origin, 'add', '.')
    git(origin, 'commit', '-m', 'rewritten history retains approved pin')
    git(origin, 'branch', '-D', 'original')
    checkout = tmp_path / 'checkout'
    subprocess.run(['git', 'clone', '--depth=1', origin.as_uri(), str(checkout)],
                   check=True, capture_output=True)
    head = git(checkout, 'rev-parse', 'HEAD').stdout
    assert git(checkout, 'cat-file', '-e', approved, check=False).returncode != 0
    workflow = (ROOT / '.github/workflows/min-distributions.yml').read_text()
    step = workflow.split('      - name: Fetch approved frozen Aoi source\n', 1)[1]
    code = textwrap.dedent(step.split("python -S - <<'PYCODE'\n", 1)[1].split('          PYCODE', 1)[0])
    subprocess.run([sys.executable, '-S', '-c', code], cwd=checkout,
                   check=True, capture_output=True, text=True)
    assert git(checkout, 'show', approved + ':snapshot').stdout == 'approved source\n'
    assert git(checkout, 'rev-parse', 'HEAD').stdout == head
    assert (checkout / 'distributions.json').read_text() == manifest
    assert git(checkout, 'status', '--porcelain').stdout == ''

    snapshot = tmp_path / 'frozen-snapshot'
    subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout', str(checkout), str(snapshot)], check=True)
    git(snapshot, 'checkout', '--detach', approved)
    assert (snapshot / 'snapshot').read_text() == 'approved source\n'
