"""Managed CI browser provenance and strict first-launch ordering (no browser)."""
import ast
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = 'dragowing/tests/test_render.py::test_stalled_dbus_does_not_block_browser_get_version'
EXCLUDE = "--deselect=dragowing/tests/test_render.py::test_stalled_dbus_does_not_block_browser_get_version"
INSTALL = 'python3 dragowing/scripts/install_ci_chromium.py --destination "$RUNNER_TEMP/aoi-chromium"'
VERSION = 'Chromium 156.0.8078.0'


def job(text, name):
    return re.split(r'\n  [a-z][a-z0-9-]*:\n', text.split('\n  ' + name + ':\n', 1)[1], maxsplit=1)[0]


def step(text, name):
    return text.split('      - name: ' + name + '\n', 1)[1].split('\n      - ', 1)[0]


def validate(ci, validation):
    lanes = [job(ci, 'test'), job(ci, 'chrome-export'),
             job(validation, 'first-start-context'), job(validation, 'compare')]
    assert 'python: ["3.11", "3.12", "3.13", "3.14", "3.15"]' in lanes[0]
    assert 'context: [normal, offline]' in lanes[2]
    for lane in lanes:
        assert INSTALL in lane and lane.count(INSTALL) == 1
        assert '$RUNNER_TEMP/aoi-chromium/chrome-linux/chrome' in lane
        assert VERSION in lane
        assert 'command -v chromium' not in lane
        for forbidden in ('continue-on-error', '--no-sandbox', 'xargs -0 cat',
                          'cat "$chromium"', 'cat "$CHROME"', '--headless', '--remote-debugging'):
            assert forbidden not in lane
    for lane in lanes[:3]:
        assert 'command -v' not in lane  # no system-browser fallback
        assert "printf 'CHROME=%s\\nDRAGOWING_REQUIRE_CHROME=1\\n'" in lane
    firsts = ['Require first actual browser startup within eight seconds',
              'Require first offline browser startup within eight seconds']
    rests = ['Test with JUnit', 'Require Chromium and render without a network namespace interface']
    for lane, first, rest in zip(lanes[:2], firsts, rests):
        gate, remaining = step(lane, first), step(lane, rest)
        assert NODE in gate and gate.count(NODE) == 1
        assert EXCLUDE not in gate and 'test_export.py' not in gate
        assert EXCLUDE in remaining and remaining.count(NODE) == 1
        assert lane.index(INSTALL) < lane.index(first) < lane.index(rest)
        assert 'if:' not in gate and 'if:' not in remaining
        assert '|| true' not in gate and '|| true' not in remaining
    for name in firsts[:1] + rests[:1]:
        assert 'python -m pytest -c pyproject.toml' in step(lanes[0], name)
    # Offline retains the original privilege/network context; ordinary jobs do not gain it.
    assert 'sudo unshare --net -- env CHROME="$CHROME" DRAGOWING_REQUIRE_CHROME=1' in step(lanes[1], firsts[1])
    assert 'sudo' not in lanes[0]
    wrapper = step(lanes[2], 'Observe the actual tests without preceding browser launches')
    assert '-m scripts.run_browser_startup_ci --output build/startup-context' in wrapper
    assert 'offline) prefix=(sudo unshare --net --)' in wrapper and 'normal) ;;' in wrapper
    assert 'Unknown startup context' in wrapper and 'if:' not in wrapper
    assert lanes[2].index(INSTALL) < lanes[2].index('Observe the actual tests')
    compare = lanes[3]
    gate = step(compare, 'Require first full-suite browser startup within eight seconds')
    assert NODE in gate and 'if:' not in gate
    assert compare.index(INSTALL) < compare.index(NODE) < compare.index('Measure ten fresh profiles before the suite')
    for name in ('Measure ten fresh profiles before the suite', 'Run the full suite with explicit browser selection',
                 'Measure ten fresh profiles after the suite', 'Validate synthetic PNG and SVG exports in three sessions'):
        assert "steps.first.outcome == 'success'" in step(compare, name)
    assert EXCLUDE in step(compare, 'Run the full suite with explicit browser selection')
    # The manually requested Chrome lane is explicit; no catch-all fallback for unknown names.
    assert 'elif [[ "$BROWSER_NAME" == google-chrome ]]' in compare
    assert "if: matrix.browser == 'chromium'" in compare and 'Unknown browser family' in compare
    for version in ('3.11', '3.12', '3.13', '3.14', '3.15'):
        assert f'"junit-py{version}/first-start-{version}.xml"' in ci
        assert f'"junit-py{version}/pytest-{version}.xml"' in ci
    assert 'build/test-results/first-start-${{ matrix.python }}.xml' in lanes[0]
    for name in ('chrome-export', 'chrome-first-start'):
        assert f'"junit-chrome-export-py3.15/{name}-3.15.xml"' in ci
        assert f'build/test-results/{name}-3.15.xml' in lanes[1]
    assert 'path: build/startup-context/' in lanes[2] and 'if-no-files-found: error' in lanes[2]
    assert 'build/browser-startup/*.xml' in compare and 'build/browser-startup/*.json' in compare


def test_every_actual_browser_lane_installs_and_gates():
    validate((ROOT / '.github/workflows/ci.yml').read_text(),
             (ROOT / '.github/workflows/browser-startup-validation.yml').read_text())
    installer = ast.parse((ROOT / 'dragowing/scripts/install_ci_chromium.py').read_text())
    constants = {n.targets[0].id: ast.literal_eval(n.value) for n in installer.body
                 if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                 and n.targets[0].id in ('SHA256', 'ARCHIVE_BYTES')}
    assert constants == {'SHA256': '6b62846a868ea3ee675f77600790877a428dfb2428c940f8eff99db1038f9815',
                         'ARCHIVE_BYTES': 248486630}
    tree = ast.parse((ROOT / 'dragowing/tests/test_render.py').read_text())
    test = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == NODE.split('::')[1])
    launch = [kw.value.value for n in ast.walk(test) if isinstance(n, ast.Call)
              and isinstance(n.func, ast.Name) and n.func.id == 'Timeouts'
              for kw in n.keywords if kw.arg == 'launch' and isinstance(kw.value, ast.Constant)]
    assert launch == [8]
    assert any(isinstance(n, ast.Compare) and isinstance(n.ops[0], ast.Lt)
               and isinstance(n.comparators[0], ast.Constant) and n.comparators[0].value == 8
               for n in ast.walk(test))


@pytest.mark.parametrize('target,old,new', [
    ('ci', INSTALL, 'echo installation skipped'),
    ('ci', 'python -m pytest -c pyproject.toml', 'pytest -c pyproject.toml'),
    ('ci', 'python -m pytest -c pyproject.toml', 'python -m pytest'),
    ('validation', INSTALL, 'echo installation skipped'),
    ('ci', VERSION, 'Chromium 123'),
    ('validation', VERSION, 'Chromium 123'),
    ('ci', 'chromium="$RUNNER_TEMP/aoi-chromium/chrome-linux/chrome"', 'chromium="$(command -v chromium)"'),
    ('ci', EXCLUDE, '-k all'),
    ('validation', EXCLUDE, '-k all'),
    ('validation', " && steps.first.outcome == 'success'", ''),
    ('validation', 'context: [normal, offline]', 'context: [normal]'),
    ('ci', 'test -x "$chromium"', 'test -x "$chromium"\n          cat "$chromium" > /dev/null'),
    ('ci', 'name: Test with JUnit', 'name: Test with JUnit\n        if: always()'),
    ('ci', '"junit-py3.11/first-start-3.11.xml"', '"missing.xml"'),
    ('ci', '"junit-chrome-export-py3.15/chrome-first-start-3.15.xml"', '"missing.xml"'),
])
def test_contract_rejects_gate_and_provenance_weakening(target, old, new):
    ci = (ROOT / '.github/workflows/ci.yml').read_text()
    validation = (ROOT / '.github/workflows/browser-startup-validation.yml').read_text()
    original = ci if target == 'ci' else validation
    assert old in original
    changed = original.replace(old, new)
    with pytest.raises(AssertionError):
        validate(changed if target == 'ci' else ci, changed if target == 'validation' else validation)


@pytest.mark.parametrize('lane', ['matrix', 'offline', 'comparison'])
@pytest.mark.parametrize('returncode', [0, 17])
def test_first_gate_shell_runs_one_exact_node_and_propagates_failure(tmp_path, lane, returncode):
    """Exercise workflow Bash with fake launchers, never a browser or isolation change."""
    import json
    import os
    import subprocess
    import textwrap

    ci = (ROOT / '.github/workflows/ci.yml').read_text()
    validation = (ROOT / '.github/workflows/browser-startup-validation.yml').read_text()
    mapping = {
        'matrix': (job(ci, 'test'), 'Require first actual browser startup within eight seconds'),
        'offline': (job(ci, 'chrome-export'), 'Require first offline browser startup within eight seconds'),
        'comparison': (job(validation, 'compare'), 'Require first full-suite browser startup within eight seconds'),
    }
    block, title = mapping[lane]
    script = textwrap.dedent(step(block, title).split('        run: |\n', 1)[1])
    script = script.replace('${{ matrix.python }}', '3.14')
    binary = tmp_path / 'bin'
    binary.mkdir()
    fake = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
with Path('calls.jsonl').open('a') as out:
    out.write(json.dumps({'args':sys.argv[1:], 'chrome':os.environ['CHROME'], 'required':os.environ['DRAGOWING_REQUIRE_CHROME']}) + '\\n')
raise SystemExit(int(os.environ['FAKE_EXIT']))
'''
    for path in (binary / 'uv', tmp_path / '.venv/bin/python'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fake)
        path.chmod(0o755)
    sudo = binary / 'sudo'
    sudo.write_text('#!/bin/sh\ntest "$1 $2 $3" = "unshare --net --" || exit 99\nshift 3\nprintf offline > context.txt\nexec "$@"\n')
    sudo.chmod(0o755)
    result = subprocess.run(['/bin/bash', '-e', '-o', 'pipefail', '-c', script], cwd=tmp_path,
                            env={**os.environ, 'PATH': str(binary) + os.pathsep + os.environ['PATH'],
                                 'CHROME': '/managed/chromium', 'DRAGOWING_REQUIRE_CHROME': '1',
                                 'FAKE_EXIT': str(returncode)}, capture_output=True, text=True)
    assert result.returncode == returncode, result.stderr
    calls = [json.loads(line) for line in (tmp_path / 'calls.jsonl').read_text().splitlines()]
    assert len(calls) == 1
    call = calls[0]
    assert call['chrome'] == '/managed/chromium' and call['required'] == '1'
    assert call['args'].count(NODE) == 1
    assert call['args'][call['args'].index('-p') + 1] == 'scripts.observe_dragowing_startup'
    assert not any(arg in ('-k', 'dragowing/tests/test_export.py') for arg in call['args'])
    assert any(arg.startswith('--browser-startup-evidence=') for arg in call['args'])
    assert any(arg.startswith('--junitxml=') for arg in call['args'])
    assert (tmp_path / 'context.txt').exists() == (lane == 'offline')


def test_matrix_isolated_node_imports_observer_with_root_configuration(tmp_path):
    """Exercise the actual Python entry/config, collecting only: no browser launch."""
    import shlex
    import subprocess
    import sys
    ci = (ROOT / '.github/workflows/ci.yml').read_text()
    block = step(job(ci, 'test'), 'Require first actual browser startup within eight seconds')
    invocation = 'uv run' + block.split('uv run', 1)[1]
    argv = shlex.split(invocation.replace('${{ matrix.python }}', '3.14').replace('\\\n', ' '))
    assert argv[:10] == ['uv', 'run', '--locked', '--python', '3.14',
                        'python', '-m', 'pytest', '-c', 'pyproject.toml']
    args = [sys.executable, *argv[6:], '--collect-only']
    args = [f'--browser-startup-evidence={tmp_path / "observation.json"}' if arg.startswith('--browser-startup-evidence=')
            else f'--junitxml={tmp_path / "collected.xml"}' if arg.startswith('--junitxml=') else arg for arg in args]
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert NODE in result.stdout and '1 test collected' in result.stdout


def test_exact_deselection_retains_parameterized_gate_contracts():
    """Collect only: exclude one real gate, never substring-matching guard cases."""
    import subprocess
    import sys
    ci = (ROOT / '.github/workflows/ci.yml').read_text()
    assert EXCLUDE in step(job(ci, 'test'), 'Test with JUnit')
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-c', 'pyproject.toml', '--collect-only', '-q',
         'tests/test_dragowing_browser_managed.py', 'dragowing/tests/test_render.py', EXCLUDE],
        cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '1 deselected' in result.stdout
    selected = result.stdout.splitlines()
    assert NODE not in selected
    for lane in ('ci', 'validation'):
        assert any('test_contract_rejects_gate_and_provenance_weakening[' + lane + '-' + EXCLUDE in line
                   for line in selected)
