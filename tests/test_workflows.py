"""Repository and workflow contracts: action uses, paths, vendor dispatch, DRAgoWing browser lanes and fonts, the lab lane, holdout parity, child entries and the shared tools lock.

旧 test_aoi_parent_workflow_pins.py もここにまとめた（節の頭に旧ファイルの名前を書いた）。
"""

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import aoi_paths  # noqa: E402
import pytest  # noqa: E402
import repo_checks as uses  # noqa: E402
import repo_checks as lock  # noqa: E402
from dragowing.figures import FONT  # noqa: E402


# ==== workflows（旧 test_workflows.py）

WORKFLOWS_ROOT = Path(__file__).resolve().parents[1]


SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"
OTHER = "1c37ad07a6a961277cf70c0d37d6f313000f5884"


def _write(root: Path, text: str) -> None:
    path = root / ".github" / "workflows" / "ci.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_live_workflows_match_parent_style():
    assert uses.style_problems(WORKFLOWS_ROOT) == []


def test_registered_children_workflows_are_checked(tmp_path):
    heads = {"heads": {"o/child": {"optional": {"subtree_prefix": "sub"}}}}
    (tmp_path / "child-heads.json").write_text(json.dumps(heads), encoding="utf-8")
    _write(tmp_path, f"jobs:\n  a:\n    steps:\n      - uses: actions/checkout@{SHA} # v7.0.1\n")
    assert uses.style_problems(tmp_path) == []
    child = tmp_path / "sub" / ".github" / "workflows"
    child.mkdir(parents=True)
    (child / "ci.yml").write_text("jobs:\n  a:\n    steps:\n      - uses: actions/checkout@v7\n", encoding="utf-8")
    problems = uses.style_problems(tmp_path)
    assert len(problems) == 1 and problems[0].startswith("sub/.github/workflows/ci.yml:4: ")


def test_live_scan_covers_every_registered_child():
    heads = json.loads((WORKFLOWS_ROOT / "child-heads.json").read_text(encoding="utf-8"))["heads"]
    scanned = {path.relative_to(WORKFLOWS_ROOT).parts[0] for path, *_ in uses._iter_uses(WORKFLOWS_ROOT)}
    assert {entry["optional"]["subtree_prefix"] for entry in heads.values()} <= scanned


def test_tag_refs_are_rejected_for_all_actions(tmp_path):
    _write(
        tmp_path,
        "\n".join(
            [
                "jobs:",
                "  a:",
                "    steps:",
                f"      - uses: actions/checkout@{SHA}",
                "      - uses: actions/setup-python@v7",
                "      - uses: astral-sh/setup-uv@v10.3.0",
                "      - uses: actions/upload-artifact@v7.0.2",
                "      - uses: actions/checkout@v7 # movable",
                "",
            ]
        ),
    )
    found = uses.style_problems(tmp_path)
    assert len(found) == 5
    assert all("actions/* と setup は 40 桁 SHA と # vX.Y.Z" in item for item in found)


def test_parent_style_refs_pass(tmp_path):
    _write(
        tmp_path,
        "\n".join(
            [
                "jobs:",
                "  call:",
                "    uses: myon-bioinformatics/myon-bioinformatics/.github/workflows/reusable-actionlint.yml@"
                + SHA
                + " # actionlint v1.7.12",
                "  local:",
                "    steps:",
                f"      - uses: actions/checkout@{OTHER} # v7.0.1",
                f"      - uses: actions/cache/restore@{SHA} # v6.1.0",
                f"      - uses: actions/setup-python@{SHA} # v7.0.0",
                f"      - uses: astral-sh/setup-uv@{OTHER} # v10.3.0",
                "      - uses: ./.github/actions/local",
                "      - uses: docker://alpine:3",
                "",
            ]
        ),
    )
    assert uses.style_problems(tmp_path) == []


def test_hash_mismatch_warns_on_pull_request_and_fails_when_strict(tmp_path, capsys):
    _write(tmp_path, f"steps:\n  - uses: actions/setup-python@{SHA} # v7.0.0\n")

    def resolve(repository, tag):
        assert repository == "actions/setup-python"
        assert tag == "v7.0.0"
        return OTHER

    assert uses.hash_problems(tmp_path, resolve)[0].endswith(f"commit {OTHER} と違う")
    assert uses.action_uses(["--root", str(tmp_path), "--check-hashes", "--warn"], resolve=resolve) == 0
    assert "::warning::" in capsys.readouterr().err
    assert uses.action_uses(["--root", str(tmp_path), "--check-hashes"], resolve=resolve) == 1


def test_matching_release_hash_passes(tmp_path, capsys):
    _write(
        tmp_path,
        "\n".join(
            [
                f"      - uses: actions/setup-python@{SHA} # v7.0.0",
                f"      - uses: actions/setup-python@{SHA} # v7.0.0",
                f"      - uses: astral-sh/setup-uv@{OTHER} # v10.3.0",
                "",
            ]
        ),
    )
    calls = []

    def resolve(repository, tag):
        calls.append((repository, tag))
        return {"actions/setup-python": SHA, "astral-sh/setup-uv": OTHER}[repository]

    assert uses.action_uses(["--root", str(tmp_path), "--check-hashes"], resolve=resolve) == 0
    assert calls == [
        ("actions/setup-python", "v7.0.0"),
        ("astral-sh/setup-uv", "v10.3.0"),
    ]
    assert "action uses ok" in capsys.readouterr().out


def test_annotated_tag_resolves_to_inner_commit(monkeypatch):
    seen = []

    def fake(url):
        seen.append(url)
        if url.endswith("/tags/v1"):
            return {"object": {"type": "tag", "sha": "b" * 40, "url": "https://example.test/tag"}}
        return {"object": {"type": "commit", "sha": "c" * 40}}

    monkeypatch.setattr(uses, "_github_json", fake)
    assert uses.github_tag_commit("anthropics/claude-code-action", "v1") == "c" * 40
    assert seen[0].endswith("/git/ref/tags/v1")


def test_api_failure_exits_two_unless_warn(tmp_path, capsys):
    _write(tmp_path, f"steps:\n  - uses: actions/setup-python@{SHA} # v7.0.0\n")

    def resolve(repository, tag):
        raise uses.HashCheckError("GitHub API HTTP 403 for tags")

    assert uses.action_uses(["--root", str(tmp_path), "--check-hashes"], resolve=resolve) == 2
    assert uses.action_uses(["--root", str(tmp_path), "--check-hashes", "--warn"], resolve=resolve) == 0
    err = capsys.readouterr().err
    assert "::error::" in err
    assert "::warning::" in err


def test_short_sha_is_rejected(tmp_path):
    _write(tmp_path, f"steps:\n  - uses: actions/checkout@{SHA[:7]} # v7.0.1\n")
    found = uses.style_problems(tmp_path)
    assert len(found) == 1
    assert "40 桁 SHA" in found[0]


def test_subactions_resolve_one_repository_tag(tmp_path):
    _write(tmp_path, f"steps:\n  - uses: actions/cache/restore@{SHA} # v6.1.0\n"
                    f"  - uses: actions/cache/save@{SHA} # v6.1.0\n")
    calls = []
    def resolve(repository, tag):
        calls.append((repository, tag))
        return SHA
    assert uses.hash_problems(tmp_path, resolve) == []
    assert calls == [("actions/cache", "v6.1.0")]


def test_resolve_aoi_root_from_subproject_anchor():
    anchor = Path(__file__).resolve().parent.parent / "queryu" / "ask" / "ask.py"
    root = aoi_paths.resolve_aoi_root(anchor=anchor)
    assert (root / "cycles" / aoi_paths.DEFAULT_CYCLE).is_dir()


def test_aoi_root_env_overrides_inference(monkeypatch, tmp_path):
    fake = tmp_path / "fake-aoi"
    (fake / "cycles" / "c9").mkdir(parents=True)
    monkeypatch.setenv("AOI_ROOT", str(fake))
    got = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
    assert got == fake.resolve()


def test_resolve_cycle_path_accepts_name_or_relative(tmp_path):
    root = tmp_path / "repo"
    (root / "cycles" / "c001-chunichi").mkdir(parents=True)
    assert aoi_paths.resolve_cycle_path(root, "c001-chunichi") == (root / "cycles" / "c001-chunichi").resolve()
    assert aoi_paths.resolve_cycle_path(root, Path("cycles/c001-chunichi")) == (root / "cycles" / "c001-chunichi").resolve()


def test_cycle_name_env(monkeypatch):
    monkeypatch.setenv("AOI_RESEARCH_CYCLE", "c9")
    assert aoi_paths.cycle_name() == "c9"
    monkeypatch.delenv("AOI_RESEARCH_CYCLE", raising=False)
    assert aoi_paths.cycle_name() == aoi_paths.DEFAULT_CYCLE


CI = WORKFLOWS_ROOT / ".github" / "workflows" / "ci.yml"


def _job(name: str) -> str:
    lines = CI.read_text(encoding="utf-8").splitlines(keepends=True)
    start = lines.index(f"  {name}:\n")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if len(line) > 2 and line.startswith("  ") and not line.startswith("   "):
            end = index
            break
    return "".join(lines[start:end])


def test_vendor_lock_job_still_runs_parent_sync_under_isolated_python():
    job = _job("vendor-lock")
    assert "python -S .vendor-sync-tools/vendor_sync.py check --manifest vendor.lock.json" in job
    assert "vendor_dispatch.py" not in job
    assert "pilot/" not in job


def test_vendor_dispatch_verifies_lock_without_recording():
    job = _job("vendor-dispatch")
    at = chr(64)
    assert f"actions/checkout{at}3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1" in job
    assert "actions/setup-python" not in job
    assert f"astral-sh/setup-uv{at}68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3" in job
    assert 'python-version: "3.15"' in job
    assert "activate-environment: true" in job
    assert "git ls-remote" in job
    assert 'PARENT_REPOSITORY_ID: "638801160"' in job
    assert 'echo "sha=${sha}" >> "$GITHUB_OUTPUT"' in job
    assert "sparse-checkout: pilot/vendor_dispatch.py" in job
    command = "python .vendor-dispatch-tools/pilot/vendor_dispatch.py --manifest vendor.lock.json"
    assert command in job
    assert "--record" not in job
    assert "python -S .vendor-dispatch-tools/pilot/vendor_dispatch.py" not in job
    assert "needs:" not in job


def _selection_step(path, title, job_name):
    text = path.read_text(encoding="utf-8")
    text = text.split("\n  " + job_name + ":\n", 1)[1]
    marker = "      - name: " + title + "\n"
    block = text.split(marker, 1)[1].split("\n      - ", 1)[0]
    script = block.split("        run: |\n", 1)[1]
    return "\n".join(line.removeprefix("          ") for line in script.splitlines()) + "\n"


def _select(tmp_path, job_name, *, installed=True, version="Chromium 156.0.8078.0"):
    tmp_path.mkdir()
    binary = tmp_path / "bin"
    binary.mkdir()
    # System browsers must never be a fallback, even if they exist.
    for name in ("chromium", "chromium-browser", "google-chrome"):
        path = binary / name
        path.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
        path.chmod(0o755)
    executable = tmp_path / "aoi-chromium/chrome-linux/chrome"
    if installed:
        executable.parent.mkdir(parents=True)
        executable.write_text("#!/bin/sh\ntest \"$1\" = --version || exit 98\necho '" + version + "'\n", encoding="utf-8")
        executable.chmod(0o755)
    output = tmp_path / "environment"
    env = {**os.environ, "PATH": str(binary), "RUNNER_TEMP": str(tmp_path), "GITHUB_ENV": str(output)}
    script = _selection_step(WORKFLOWS_ROOT / ".github/workflows/ci.yml", "Select required Chromium without Chrome fallback", job_name)
    result = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", script], env=env, capture_output=True, text=True)
    return result, output, executable


def test_ci_selects_only_the_managed_chromium(tmp_path):
    for job_name in ("test", "chrome-export"):
        result, output, executable = _select(tmp_path / job_name, job_name)
        assert result.returncode == 0, result.stderr
        assert output.read_text() == f"CHROME={executable}\nDRAGOWING_REQUIRE_CHROME=1\n"


def test_ci_rejects_wrong_installed_version(tmp_path):
    for job_name in ("test", "chrome-export"):
        result, output, _ = _select(tmp_path / job_name, job_name, version="Chromium 123.4")
        assert result.returncode != 0
        assert "does not match the reviewed snapshot" in result.stdout
        assert not output.exists()


def test_ci_rejects_system_browsers_when_managed_install_is_missing(tmp_path):
    for job_name in ("test", "chrome-export"):
        result, output, _ = _select(tmp_path / job_name, job_name, installed=False)
        assert result.returncode != 0
        assert not output.exists()


def test_offline_ci_keeps_isolation_and_report_contract():
    text = (WORKFLOWS_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    job = text.split("\n  chrome-export:\n", 1)[1].split("\n  failure-identity:\n", 1)[0]
    assert "runs-on: ubuntu-24.04" in job
    assert 'sudo unshare --net -- env CHROME="$CHROME" DRAGOWING_REQUIRE_CHROME=1' in job
    assert "--junitxml=build/test-results/chrome-export-3.15.xml" in job
    assert "name: junit-chrome-export-py3.15" in job
    assert "name: chrome-export-evidence" in job
    assert "name: Offline Chrome export (Python 3.15)" in job
    assert '"junit-chrome-export-py3.15/chrome-export-3.15.xml"' in text
    assert "needs: [changes, test, lab-integration, chrome-export]" in text


def test_diagnostics_use_chromium_by_default_with_manual_chrome_comparison():
    text = (WORKFLOWS_ROOT / ".github/workflows/browser-startup-validation.yml").read_text(encoding="utf-8")
    assert "compare-chrome:\n" in text
    assert "type: boolean\n        required: false\n        default: false" in text
    assert "fromJSON(github.event_name == 'workflow_dispatch' && inputs.compare-chrome && '[\"chromium\",\"google-chrome\"]' || '[\"chromium\"]')" in text
    assert "Installed Chromium version does not match the reviewed snapshot." in text
    assert "The requested Chrome comparison requires" in text
    assert text.count('--chrome "$CHROME"') == 3
    assert text.count('--runs 10 --timeout 30') == 2
    assert '--runs 3 --timeout 30' in text
    assert "DRAGOWING_REQUIRE_CHROME: '1'" in text
    assert "if: always()" in text
    assert "build/browser-startup/*.json" in text
    assert "build/browser-startup/diagnostic-exports/" in text


def test_python_matrix_pins_the_same_required_chromium_selection():
    text = (WORKFLOWS_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    job = text.split("\n  test:\n", 1)[1].split("\n  lab-integration:\n", 1)[0]
    assert "runs-on: ubuntu-24.04" in job
    assert 'chromium="$RUNNER_TEMP/aoi-chromium/chrome-linux/chrome"' in job
    assert "dragowing/scripts/install_ci_chromium.py" in job
    assert "command -v" not in job
    assert "command -v google-chrome" not in job
    assert "CHROMIUM=%s" not in job
    assert "DRAGOWING_REQUIRE_CHROME=1" in job
    assert "from dragowing.plotly_cdn import fetch_plotly_js" in job
    assert "DRAGOWING_PINNED_PLOTLY_JS: ${{ github.workspace }}/build/test-assets/plotly.min.js" in job


def test_first_start_context_uses_fresh_jobs_and_unchanged_test_order():
    text = (WORKFLOWS_ROOT / ".github/workflows/browser-startup-validation.yml").read_text(encoding="utf-8")
    job = text.split("\n  first-start-context:\n", 1)[1].split("\n  compare:\n", 1)[0]
    assert "context: [normal, offline]" in job
    assert "fail-fast: false" in job
    assert "runs-on: ubuntu-24.04" in job
    assert "python-version: '3.15'" in job
    assert "uv sync --locked --python 3.15" in job
    assert "sudo unshare --net --" in job
    assert "dragowing_browser.py diagnose" not in job
    assert "--runs" not in job and "--timeout" not in job
    assert '"$chromium" --version' in job
    assert "-m scripts.dragowing_browser startup_ci --output build/startup-context" in job
    # The wrapper's exact pytest/plugin/evidence command is executed and checked
    # in test_browser_startup_ci; the workflow must route through that wrapper.
    assert "'scripts/dragowing_browser.py'" in text
    modules = "dragowing/tests/test_chrome_pipe.py dragowing/tests/test_render.py dragowing/tests/test_export.py \\\n            dragowing/tests/test_plotly_cdn.py"
    assert modules in (WORKFLOWS_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "if: always()" in job and "if-no-files-found: error" in job
    assert "retention-days: 14" in job
    assert "'scripts/observe_dragowing_startup.py'" in text
    assert job.index("Observe the actual tests") < job.index("Preserve first and subsequent")


def test_first_start_shell_only_changes_execution_context(tmp_path):
    script = _selection_step(WORKFLOWS_ROOT / ".github/workflows/browser-startup-validation.yml",
                             "Observe the actual tests without preceding browser launches", "first-start-context")
    binary = tmp_path / "bin"
    binary.mkdir()
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$PWD/args"\nprintf "%s\\n" "$CHROME" "$DRAGOWING_REQUIRE_CHROME" "$DRAGOWING_PINNED_PLOTLY_JS" > "$PWD/env"\nexit "${TEST_EXIT:-0}"\n')
    python.chmod(0o755)
    for name, body in (("sudo", 'printf "%s\\n" "$@" > "$PWD/sudo-args"; exec "$@"'),
                       ("unshare", 'test "$1" = --net && test "$2" = --; shift 2; exec "$@"')):
        path = binary / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)
    results = []
    for context in ("normal", "offline"):
        result = subprocess.run(["/bin/bash", "-e", "-c", script], cwd=tmp_path, capture_output=True, text=True,
                                env={**os.environ, "STARTUP_CONTEXT": context, "CHROME": "/explicit/chromium",
                                     "PATH": str(binary) + ":/usr/bin:/bin"})
        assert result.returncode == 0, result.stderr
        results.append(((tmp_path / "args").read_text(), (tmp_path / "env").read_text()))
        assert (tmp_path / "sudo-args").exists() == (context == "offline")
    assert results[0] == results[1]
    assert results[0][0] == "-m\nscripts.dragowing_browser\nstartup_ci\n--output\nbuild/startup-context\n"
    assert results[0][1].startswith("/explicit/chromium\n1\n")
    assert (tmp_path / "sudo-args").read_text().startswith("unshare\n--net\n--\nenv\n")

    # Wrapper failure must propagate in both contexts, without an automatic retry.
    for context in ("normal", "offline"):
        result = subprocess.run(["/bin/bash", "-e", "-c", script], cwd=tmp_path,
                                capture_output=True, text=True,
                                env={**os.environ, "STARTUP_CONTEXT": context,
                                     "CHROME": "/explicit/chromium", "TEST_EXIT": "17",
                                     "PATH": str(binary) + ":/usr/bin:/bin"})
        assert result.returncode == 17, result.stderr
    (tmp_path / "args").unlink()
    result = subprocess.run(["/bin/bash", "-e", "-c", script], cwd=tmp_path,
                            capture_output=True, text=True,
                            env={**os.environ, "STARTUP_CONTEXT": "unknown",
                                 "CHROME": "/explicit/chromium",
                                 "PATH": str(binary) + ":/usr/bin:/bin"})
    assert result.returncode != 0
    assert "Unknown startup context" in result.stdout
    assert not (tmp_path / "args").exists()


TIGHT = FONT.replace(" ", "")


def test_committed_research_reports_use_the_font():
    pages = sorted(WORKFLOWS_ROOT.glob("research/*/outputs/*.html"))
    assert pages  # 検証が空振りしない
    for path in pages:
        text = path.read_text(encoding="utf-8")
        if "Plotly.newPlot" in text:  # DRAgoWing の研究用レポート（取得した原本の HTML は対象外）
            assert f"font:16px/1.65 {TIGHT}" in text and f"family:'{FONT}'" in text, path
            assert "system-ui" not in text, path


SPEC = importlib.util.spec_from_file_location('lab_nano_check', WORKFLOWS_ROOT / 'scripts/repo_checks.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class LabEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.lock = {'package': [{'name': name, 'version': '1.0'}
                                for name in CHECK.EXPECTED | CHECK.OMITTED]}
        self.installed = [(name, '1.0') for name in CHECK.EXPECTED]

    def test_matching_locked_environment(self):
        self.assertTrue(CHECK.inspect_environment(self.lock, self.installed)['valid'])

    def test_missing_plugin_fails(self):
        self.assertFalse(CHECK.inspect_environment(self.lock, [r for r in self.installed if r[0] != 'anyio'])['valid'])

    def test_newly_added_dependency_fails_even_when_locked(self):
        self.lock['package'].append({'name': 'future-runtime', 'version': '1.0'})
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed + [('future-runtime', '1.0')])['valid'])

    def test_restored_heavy_package_fails(self):
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed + [('numpy', '1.0')])['valid'])

    def test_unlocked_version_fails(self):
        self.installed = [(n, '2.0' if n == 'pytest' else v) for n, v in self.installed]
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed)['valid'])

    def test_duplicate_distribution_fails(self):
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed + [('pytest', '1.0')])['valid'])

    def test_package_name_normalization(self):
        rows = [('PyTest' if n == 'pytest' else n, v) for n, v in self.installed]
        self.assertTrue(CHECK.inspect_environment(self.lock, rows)['valid'])

    def test_removed_lock_omission_requires_review(self):
        self.lock['package'] = [p for p in self.lock['package'] if p['name'] != 'numpy']
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed)['valid'])

    def _run_cli(self, platform, python_version):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock = root / 'uv.lock'
            lock.write_text(''.join(
                f'[[package]]\nname = "{p["name"]}"\nversion = "{p["version"]}"\n'
                for p in self.lock['package']))
            output = root / 'evidence' / 'inventory.json'
            distributions = [SimpleNamespace(metadata={'Name': n}, version=v)
                             for n, v in self.installed]
            with patch.object(CHECK.metadata, 'distributions', return_value=distributions), \
                 patch.object(CHECK.sys, 'platform', platform), \
                 patch.object(CHECK.sys, 'version_info', python_version), \
                 patch.object(CHECK.sys, 'prefix', str(root / 'environment')), \
                 contextlib.redirect_stdout(io.StringIO()):
                status = CHECK.lab_nano_environment(['--lock', str(lock), '--output', str(output)])
            return status, json.loads(output.read_text())

    def test_cli_writes_success_evidence(self):
        status, report = self._run_cli('linux', (3, 15))
        self.assertEqual(status, 0)
        self.assertTrue(report['valid'])
        self.assertEqual(len(report['lock_sha256']), 64)
        self.assertEqual(report['environment_regular_file_bytes'], 0)

    def test_cli_rejects_unreviewed_runtime_with_evidence(self):
        for platform, version in [('darwin', (3, 15)), ('linux', (3, 14))]:
            with self.subTest(platform=platform, version=version):
                status, report = self._run_cli(platform, version)
                self.assertEqual(status, 1)
                self.assertFalse(report['valid'])
                self.assertTrue(report['errors'])

    def test_workflow_locks_once_then_runs_without_resync(self):
        text = (WORKFLOWS_ROOT / '.github/workflows/ci.yml').read_text()
        lane = text.split('  lab-integration:', 1)[1].split('  chrome-export:', 1)[0]
        omitted = re.findall(r'--no-install-package ([\w-]+)', lane)
        self.assertEqual(set(omitted), CHECK.OMITTED)
        self.assertEqual(len(omitted), len(CHECK.OMITTED))
        self.assertEqual(lane.count('uv sync --locked --python 3.15'), 1)
        self.assertEqual(lane.count('uv run --locked --no-sync --python 3.15 pytest'), 1)
        self.assertNotIn('uv run --locked --python', lane)
        self.assertIn('--require-blueprobe-lab-integration', lane)
        for node in ('test_optional_real_lab_extractor_reuses_all_calendar_rows',
                     'test_real_saved_npb_fixture_coverage_and_css',
                     'test_verified_cache_real_lab_snapshot_replay'):
            self.assertIn('::' + node, lane)
        self.assertIn('scripts/repo_checks.py lab_nano_environment --output', lane)
        self.assertIn('uv pip check --offline', lane)
        self.assertLess(lane.index('uv sync'), lane.index('repo_checks.py lab_nano_environment'))
        self.assertLess(lane.index('repo_checks.py lab_nano_environment'), lane.index('uv run'))
        self.assertIn('timeout-minutes: 10', lane)
        self.assertIn('AOI_LAB_SOURCE_ROOT', lane)
        self.assertIn('if-no-files-found: error', lane)


def test_holdout_job_provisions_node_before_parity_tests():
    workflow = (Path(__file__).resolve().parents[1] /
                '.github/workflows/littlebit-holdout-drift.yml').read_text()
    job = workflow.split('\n  provenance:\n', 1)[1]
    setup = job.index('uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1')
    version = job.index("node-version: '26'", setup)
    guard = job.index('run: node -e "if (+process.versions.node.split(\'.\')[0] < 26) process.exit(1)"', version)
    suite = job.index('uv run --locked --python 3.14.8 pytest')
    assert job.count("uses: actions/setup-node@") == 1
    assert setup < version < guard < suite
    assert 'pythdragoras/tests -k littlebit' in job[suite:]
    # Provisioning Node must not weaken the independent provenance guard.
    assert 'HOLDOUT_SOURCE_PROVENANCE:' not in job


# ═══ · child entries through aoi.py ══════════════════════════════════════════════════════════════════════
# `python aoi.py <name>` runs the child's same-named single file. AOI_ROOT and only that child's
# sibling directories come from aoi.py (appended after the caller's PYTHONPATH).

CHILDREN = ("blueprobe", "queryu", "nagoyaction", "sakanalytics", "pythdragoras", "dragowing")


class ChildEntriesThroughAoiTest(unittest.TestCase):
    def _root(self, temp: str) -> Path:
        root = Path(temp) / "aoi"
        root.mkdir()
        for name in ("aoi.py", "aoi_paths.py", "pyproject.toml"):
            shutil.copy2(WORKFLOWS_ROOT / name, root / name)
        return root

    def test_forwards_argv_cwd_exit_code_and_the_sibling_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._root(temp)
            work = Path(temp) / "work"
            work.mkdir()
            for name in CHILDREN:
                with self.subTest(child=name):
                    target = root / name / f"{name}.py"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text('import json, os, sys\nprint(json.dumps({"args": sys.argv[1:], "cwd": os.getcwd(), "AOI_ROOT": os.environ.get("AOI_ROOT"), "PYTHONPATH": os.environ.get("PYTHONPATH", ""), "path0": sys.path[0]}))\nsys.exit(7)\n')
                    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "PYTHONSAFEPATH")}
                    result = subprocess.run([sys.executable, str(root / "aoi.py"), name, "x y", "--option"],
                                            cwd=work, env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 7, result.stderr)
                    seen = json.loads(result.stdout)
                    self.assertEqual((seen["args"], seen["cwd"], seen["AOI_ROOT"]), (["x y", "--option"], str(work), str(root.resolve())))
                    import aoi
                    expect = [str((root / rel).resolve()) for rel in aoi.SIBLINGS[name]]
                    got = [entry for entry in seen["PYTHONPATH"].split(os.pathsep) if entry]
                    self.assertEqual(got, expect)
                    self.assertNotIn(str(root.resolve()), got)
                    self.assertNotIn(str((root / "dragowing").resolve()), got)
                    self.assertEqual(seen["path0"], str((root / name).resolve()))

    def test_missing_child_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._root(temp)
            result = subprocess.run([sys.executable, str(root / "aoi.py"), "blueprobe", "--help"], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("blueprobe.py", result.stderr)

    def test_import_aoi_adds_the_sibling_paths_after_what_is_already_first(self):
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "PYTHONSAFEPATH")}
        code = (
            "import sys\n"
            "first = sys.path[0]\n"
            "import aoi, blueprobe, propositions, dragowing.render\n"
            "import dragowing\n"
            "print(sys.path[0] == first, blueprobe.__file__)\n"
            "print(int(bool(getattr(dragowing, '__path__', None))))\n"
            f"print(int({str(WORKFLOWS_ROOT / 'dragowing')!r} in sys.path))\n"
        )
        run = subprocess.run([sys.executable, "-c", code], cwd=WORKFLOWS_ROOT, env=env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        same_first, blueprobe_file = run.stdout.splitlines()[0].split()
        self.assertEqual((same_first, Path(blueprobe_file)), ("True", WORKFLOWS_ROOT / "blueprobe" / "blueprobe.py"))
        self.assertEqual(run.stdout.splitlines()[1:], ["1", "0"])

    def test_caller_pythonpath_beats_the_sibling_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._root(temp)
            external = Path(temp) / "external"
            external.mkdir()
            (external / "blueprobe.py").write_text("ORIGIN = 'external'\n")
            (root / "blueprobe").mkdir()
            (root / "blueprobe" / "blueprobe.py").write_text("ORIGIN = 'aoi'\n")
            target = root / "queryu" / "queryu.py"
            target.parent.mkdir(parents=True)
            target.write_text("import blueprobe\nprint(blueprobe.ORIGIN)\n")
            work = Path(temp) / "work"
            work.mkdir()
            base = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "PYTHONSAFEPATH")}
            external_env = dict(base, PYTHONPATH=str(external))
            chosen = subprocess.run([sys.executable, str(root / "aoi.py"), "queryu"],
                                    cwd=work, env=external_env, capture_output=True, text=True)
            self.assertEqual(chosen.stdout.strip(), "external", chosen.stderr)
            fallback = subprocess.run([sys.executable, str(root / "aoi.py"), "queryu"],
                                      cwd=work, env=base, capture_output=True, text=True)
            self.assertEqual(fallback.stdout.strip(), "aoi", fallback.stderr)

    def test_isolated_flags_insert_siblings_without_applying_pythonpath(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self._root(temp)
            sentinel = Path(temp) / "caller"
            sentinel.mkdir()
            (sentinel / "sentinel_marker.py").write_text("MARKER = True\n")
            (root / "blueprobe").mkdir()
            (root / "blueprobe" / "blueprobe.py").write_text("ORIGIN = 'aoi'\n")
            target = root / "queryu" / "queryu.py"
            target.parent.mkdir(parents=True)
            target.write_text(
                "import importlib.util, json, os, sys\n"
                "print(json.dumps({"
                "'isolated': int(sys.flags.isolated), 'no_site': int(sys.flags.no_site), "
                "'ignore': int(sys.flags.ignore_environment), 'safe': bool(sys.flags.safe_path), "
                "'path0': sys.path[0], 'path': sys.path, 'AOI_ROOT': os.environ.get('AOI_ROOT'), "
                "'argv': sys.argv[1:], "
                "'sentinel': importlib.util.find_spec('sentinel_marker') is not None, "
                "'blueprobe': importlib.util.find_spec('blueprobe') is not None}))\n"
            )
            work = Path(temp) / "work"
            work.mkdir()
            base = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "AOI_RESEARCH_CYCLE", "PYTHONSAFEPATH")}
            base["PYTHONPATH"] = str(sentinel)
            script_dir = str((root / "queryu").resolve())
            sibling = str((root / "blueprobe").resolve())
            expect = {
                "-I": {"isolated": 1, "no_site": 0, "ignore": 1, "safe": True, "script_dir": False, "sentinel": False},
                "-S": {"isolated": 0, "no_site": 1, "ignore": 0, "safe": False, "script_dir": True, "sentinel": True},
                "-E": {"isolated": 0, "no_site": 0, "ignore": 1, "safe": False, "script_dir": True, "sentinel": False},
                "-P": {"isolated": 0, "no_site": 0, "ignore": 0, "safe": True, "script_dir": False, "sentinel": True},
            }
            for flag, wanted in expect.items():
                with self.subTest(flag=flag):
                    result = subprocess.run(
                        [sys.executable, flag, str(root / "aoi.py"), "queryu", "x"],
                        cwd=work, env=base, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    seen = json.loads(result.stdout)
                    self.assertEqual(seen["argv"], ["x"])
                    self.assertEqual(seen["AOI_ROOT"], str(root.resolve()))
                    self.assertEqual(
                        (seen["isolated"], seen["no_site"], seen["ignore"], seen["safe"]),
                        (wanted["isolated"], wanted["no_site"], wanted["ignore"], wanted["safe"]))
                    self.assertEqual(seen["path0"] == script_dir, wanted["script_dir"])
                    self.assertNotEqual(seen["path0"], str(root.resolve()))
                    self.assertNotIn("", seen["path"])
                    self.assertNotIn(str(root.resolve()), seen["path"])
                    self.assertNotIn(str((root / "dragowing").resolve()), seen["path"])
                    self.assertIn(sibling, seen["path"])
                    self.assertEqual(seen["sentinel"], wanted["sentinel"])
                    self.assertTrue(seen["blueprobe"])
                    if wanted["sentinel"]:
                        self.assertLess(seen["path"].index(str(sentinel)), seen["path"].index(sibling))


def test_lock_matches_shared_tool_bytes():
    assert lock.shared_tools_lock_problems(WORKFLOWS_ROOT) == []
    document = lock.load_lock(WORKFLOWS_ROOT)
    assert document["schema"] == "vendor-lock/1"
    paths = [entry["path"] for entry in document["files"]]
    assert paths == sorted(paths)
    assert paths == [
        "scripts/child_checks.py",
        "scripts/fetch_module.py",
        "scripts/shrink_module.py",
        "scripts/shrink_polars.py",
        "shrink/numpy_linalg_min.py",
        "shrink/numpy_min.py",
        "shrink/polars_min.py",
        "vendor/py_launch.cjs",
        "vendor/uv_tool_build.py",
    ]


def test_hash_mismatch_is_reported():
    document = lock.load_lock(WORKFLOWS_ROOT)
    document["files"][0]["sha256"] = "0" * 64
    found = lock.shared_tools_lock_problems(WORKFLOWS_ROOT, document)
    assert any("sha256 が違う" in item for item in found)


def test_warn_exits_zero_when_the_lock_disagrees(capsys):
    document = json.loads((WORKFLOWS_ROOT / "shared-tools.lock.json").read_text(encoding="utf-8"))
    document["files"][0]["sha256"] = "0" * 64
    original = lock.load_lock

    def fake(root):
        return document

    lock.load_lock = fake
    try:
        assert lock.shared_tools_lock(["--warn", "--root", str(WORKFLOWS_ROOT)]) == 0
    finally:
        lock.load_lock = original
    assert "sha256 が違う" in capsys.readouterr().err


def test_strict_exits_one_when_the_lock_disagrees(capsys):
    document = json.loads((WORKFLOWS_ROOT / "shared-tools.lock.json").read_text(encoding="utf-8"))
    document["schema"] = "other"
    original = lock.shared_tools_lock_problems

    def fake(root, parsed=None):
        return ["broken"]

    lock.shared_tools_lock_problems = fake
    try:
        assert lock.shared_tools_lock(["--root", str(WORKFLOWS_ROOT)]) == 1
    finally:
        lock.shared_tools_lock_problems = original
    assert "broken" in capsys.readouterr().err
    assert document["schema"] == "other"


def test_py_launch_is_shared_from_the_vendored_parent_copy():
    """vendor/py_launch.cjs は vendor.lock.json で親から取り込んだバイトを子へ配る。"""
    shared = {e["path"]: e for e in lock.load_lock(WORKFLOWS_ROOT)["files"]}
    vendored = json.loads((WORKFLOWS_ROOT / "vendor.lock.json").read_text(encoding="utf-8"))["files"]
    parent = [e for e in vendored if e["destination"] == "vendor/py_launch.cjs"]
    assert len(parent) == 1
    assert parent[0]["repository"] == "myon-bioinformatics/myon-bioinformatics"
    assert shared["vendor/py_launch.cjs"]["sha256"] == parent[0]["sha256"]
    assert "myon-bioinformatics/SakAnalytics" in shared["vendor/py_launch.cjs"]["consumers"]
    assert "myon-bioinformatics/PythDRagoras" in shared["vendor/py_launch.cjs"]["consumers"]


def test_vendor_path_mismatch_is_reported():
    document = lock.load_lock(WORKFLOWS_ROOT)
    for entry in document["files"]:
        if entry["path"] == "vendor/py_launch.cjs":
            entry["sha256"] = "0" * 64
    found = lock.shared_tools_lock_problems(WORKFLOWS_ROOT, document)
    assert any(item.startswith("vendor/py_launch.cjs: sha256 が違う") for item in found)


def test_consumers_outside_child_heads_or_unsorted_are_reported():
    import copy
    data = lock.load_lock(lock.ROOT)
    bad = copy.deepcopy(data)
    bad["files"][0]["consumers"] = ["myon-bioinformatics/NotAChild"]
    assert any("consumers" in p for p in lock.shared_tools_lock_problems(lock.ROOT, bad))
    bad["files"][0]["consumers"] = ["myon-bioinformatics/SakAnalytics", "myon-bioinformatics/DRAgoWing"]
    assert any("consumers" in p for p in lock.shared_tools_lock_problems(lock.ROOT, bad))
    bad["files"][0]["consumers"] = []
    assert not any(p.startswith(bad["files"][0]["path"]) for p in lock.shared_tools_lock_problems(lock.ROOT, bad))


# ==== pins（旧 test_aoi_parent_workflow_pins.py）
# Local rollout contract; adopted vendor locks are deliberately independent.


PARENT = "myon-bioinformatics/myon-bioinformatics"
PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
PINS_ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows").is_dir())


def test_parent_reusable_workflow_uses_are_one_full_sha():
    """Parent reusable-workflow uses refs are the reviewed 40-character SHA.

    Runtime tool checkouts are resolved separately and are outside this contract.
    """
    at = chr(64)
    pattern = re.compile(
        r"uses:\s*['\"]?"
        + re.escape(PARENT)
        + r"/\.github/workflows/[^\s'\"]+"
        + at
        + r"([^\s'\"]+)"
    )
    pins = []
    for path in sorted((PINS_ROOT / ".github/workflows").glob("*")):
        if path.suffix not in (".yml", ".yaml"):
            continue
        pins.extend(pattern.findall(path.read_text(encoding="utf-8")))
    assert pins, "parent reusable workflow uses must remain observable"
    assert set(pins) == {PARENT_WORKFLOW_PIN}, pins


@pytest.mark.parametrize("fault", [None, "repository", "source", "commit", "sha256", "identity", "payload"])
def test_frozen_distribution_compiler_checks_identity_before_saving(tmp_path, monkeypatch, fault):
    """Run the workflow adapter offline, including its refusal paths."""
    import hashlib
    import json
    import subprocess
    import textwrap

    text = (PINS_ROOT / ".github/workflows/min-distributions.yml").read_text()
    step = text.split("      - name: Restore approved frozen distribution compiler\n", 1)[1]
    program = textwrap.dedent(step.split("<<'PYCODE'\n", 1)[1].split("\n          PYCODE", 1)[0])
    payload = b"raise RuntimeError('compiler bytes must not execute while being fetched')\n"
    tool = {"repository": PARENT, "source": "tools/minpy.py", "commit": "a" * 40,
            "sha256": hashlib.sha256(payload).hexdigest()}
    if fault in {"repository", "source", "commit", "sha256"}:
        tool[fault] = "untrusted"
    manifest = json.dumps({"tool": tool})
    monkeypatch.chdir(tmp_path)
    (tmp_path / "distributions.json").write_text(manifest)
    (tmp_path / ".test-deps").mkdir()
    calls = []

    def fetch(argv, **kwargs):
        calls.append(argv)
        assert argv == ["git", "-C", ".test-deps/distribution-tools", "fetch", "--depth=1", "origin", "a" * 40]

    def observe(argv, **kwargs):
        if argv[-1] == "FETCH_HEAD":
            return ("b" * 40 if fault == "identity" else "a" * 40) + "\n"
        assert argv[-1] == "a" * 40 + ":tools/minpy.py"
        return b"changed" if fault == "payload" else payload

    monkeypatch.setattr(subprocess, "run", fetch)
    monkeypatch.setattr(subprocess, "check_output", observe)
    if fault:
        with pytest.raises(SystemExit):
            exec(compile(program, "min-distributions.yml", "exec"), {})
        assert not (tmp_path / ".test-deps/frozen-minpy.py").exists()
    else:
        exec(compile(program, "min-distributions.yml", "exec"), {})
        assert (tmp_path / ".test-deps/frozen-minpy.py").read_bytes() == payload
    assert (tmp_path / "distributions.json").read_text() == manifest
    if fault in {"repository", "source", "commit", "sha256"}:
        assert calls == []


def _distribution_step(name):
    """Read the actual shell adapter without adding a test-time YAML dependency."""
    import textwrap

    text = (PINS_ROOT / ".github/workflows/min-distributions.yml").read_text()
    step = text.split("      - name: " + name + "\n", 1)[1].split("\n      - ", 1)[0]
    return step, textwrap.dedent(step.split("        run: |\n", 1)[1])


@pytest.mark.parametrize("synced", [True, False])
def test_distribution_parent_resolution_does_not_use_frozen_compiler(tmp_path, monkeypatch, synced):
    """A conflict-free merge must still resolve live main, not tool.commit."""
    import json
    import os
    import subprocess
    import sys

    text = (PINS_ROOT / ".github/workflows/min-distributions.yml").read_text()
    # The checkout and provenance gate must consume the live resolver output.
    assert "ref: ${{ steps.resolved.outputs.parent_sha }}\n          path: .test-deps/distribution-tools" in text
    assert "PARENT_SHA: ${{ steps.resolved.outputs.parent_sha }}" in text
    name = next(line.removeprefix("      - name: ") for line in text.splitlines()
                if line.startswith("      - name: Resolve "))
    _, program = _distribution_step(name)
    live, frozen, queryu, queryu_head = "b" * 40, "a" * 40, "c" * 40, "d" * 40
    monkeypatch.chdir(tmp_path)
    manifest = json.dumps({"tool": {"commit": frozen}})
    (tmp_path / "distributions.json").write_text(manifest)
    tools = tmp_path / "bin"
    tools.mkdir()
    git = tools / "git"
    git.write_text("#!/bin/sh\n"
                   'printf "%s\\n" "$*" >> "$GIT_CALLS"\n'
                   'case "$*" in\n'
                   f'"ls-remote https://github.com/myon-bioinformatics/myon-bioinformatics.git refs/heads/main") printf "{live}\\trefs/heads/main\\n";;\n'
                   f'"ls-remote https://github.com/myon-bioinformatics/QueRyu.git refs/heads/main") printf "{queryu_head}\\trefs/heads/main\\n";;\n'
                   "*) exit 91;;\n"
                   "esac\n")
    git.chmod(0o755)
    # Mock only the repository-identity HTTP response; run the workflow's Python.
    python = tools / "python"
    python.write_text(f"#!{sys.executable}\n" + '''import io, json, os, sys, urllib.request

def response(request, timeout):
    assert request.full_url == "https://api.github.com/repos/myon-bioinformatics/myon-bioinformatics"
    return io.StringIO(json.dumps({"id": 638801160, "full_name": "myon-bioinformatics/myon-bioinformatics"}))

urllib.request.urlopen = response
assert sys.argv[1] == "-S"
if sys.argv[2] == "scripts/check_child_heads.py":
    # QueRyu の sha は子の履歴から導く。導出そのものは test_child_registry.py が確かめる。ここでは呼び方だけ記録する。
    with open(os.environ["PY_CALLS"], "a") as handle:
        handle.write(" ".join(sys.argv[1:]) + "\\n")
    if not os.environ["QUERYU_SYNCED"]:
        print("check-child-heads: no synced sha for myon-bioinformatics/QueRyu: no matching tree", file=sys.stderr)
        raise SystemExit(1)
    print(os.environ["QUERYU_SYNCED"])
    raise SystemExit(0)
if sys.argv[2] == "-":
    exec(compile(sys.stdin.read(), "workflow-identity", "exec"), {})
else:
    assert sys.argv[2] == "-c"
    exec(compile(sys.argv[3], "workflow-ref", "exec"), {})
''')
    python.chmod(0o755)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    for key, value in {"PARENT_REF": "", "QUERYU_REF": "", "GITHUB_TOKEN": "",
                       "PARENT_REPOSITORY_ID": "638801160", "GIT_CALLS": str(tmp_path / "git-calls"),
                       "GITHUB_OUTPUT": str(tmp_path / "output"),
                       "PY_CALLS": str(tmp_path / "py-calls"), "QUERYU_SYNCED": queryu if synced else "",
                       "GITHUB_STEP_SUMMARY": str(tmp_path / "summary")}.items():
        monkeypatch.setenv(key, value)
    result = subprocess.run(["bash", "-c", program], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text().splitlines() == [
        "parent_sha=" + live, "queryu_sha=" + (queryu if synced else queryu_head)]
    assert "refs/heads/main" in (tmp_path / "git-calls").read_text()
    assert (tmp_path / "py-calls").read_text().splitlines() == [
        "-S scripts/check_child_heads.py --print-synced myon-bioinformatics/QueRyu"]
    summary = (tmp_path / "summary").read_text()
    assert live in summary and "repository_id 638801160" in summary
    assert frozen not in summary
    assert (tmp_path / "distributions.json").read_text() == manifest


@pytest.mark.parametrize("event", ["pull_request", "push", "schedule", "workflow_dispatch"])
@pytest.mark.parametrize("mismatch", [False, True])
def test_distribution_live_provenance_event_policy(tmp_path, monkeypatch, event, mismatch):
    """Frozen bytes cannot mask live drift; PR warns, all other events fail."""
    import hashlib
    import json
    import os
    import subprocess
    import sys

    _, program = _distribution_step("Compare resolved parent tool provenance")
    frozen = b"approved compiler\n"
    live = b"different live compiler\n" if mismatch else frozen
    live_sha, frozen_sha = "b" * 40, "a" * 40
    manifest = json.dumps({"tool": {"repository": PARENT, "source": "tools/minpy.py",
        "commit": frozen_sha, "sha256": hashlib.sha256(frozen).hexdigest()}})
    monkeypatch.chdir(tmp_path)
    (tmp_path / "distributions.json").write_text(manifest)
    checkout = tmp_path / ".test-deps/distribution-tools/tools"
    checkout.mkdir(parents=True)
    (checkout / "minpy.py").write_bytes(live)
    (tmp_path / ".test-deps/frozen-minpy.py").write_bytes(frozen)
    tools = tmp_path / "bin"
    tools.mkdir()
    git = tools / "git"
    git.write_text("#!/bin/sh\n"
                   'test "$*" = "-C .test-deps/distribution-tools rev-parse HEAD" || exit 91\n'
                   f"printf '{live_sha}\\n'\n")
    git.chmod(0o755)
    (tools / "python").symlink_to(sys.executable)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("PARENT_SHA", live_sha)
    monkeypatch.setenv("EVENT_NAME", event)
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "summary"))
    result = subprocess.run(["bash", "-c", program], capture_output=True, text=True, timeout=10)
    strict = event != "pull_request"
    assert result.returncode == (1 if mismatch and strict else 0), result.stderr
    summary = (tmp_path / "summary").read_text()
    assert f"- resolved_sha: `{live_sha}`" in summary
    assert f"- approved_commit: `{frozen_sha}`" in summary
    assert f"- checkout_sha256: `{hashlib.sha256(live).hexdigest()}`" in summary
    assert "- mode: " + ("strict" if strict else "report-only") in summary
    assert "- result: " + ("mismatch" if mismatch else "match") in summary
    if mismatch:
        assert ("::error::" if strict else "::warning::") in result.stderr
    else:
        assert not result.stderr
    assert (checkout / "minpy.py").read_bytes() == live
    assert (tmp_path / ".test-deps/frozen-minpy.py").read_bytes() == frozen
    assert (tmp_path / "distributions.json").read_text() == manifest


@pytest.mark.parametrize("fault", [None, "repository", "commit", "identity"])
def test_frozen_queryu_is_separate_from_live_checkout(tmp_path, monkeypatch, fault):
    import json
    import subprocess
    import textwrap

    text = (PINS_ROOT / ".github/workflows/min-distributions.yml").read_text()
    step = text.split("      - name: Restore approved frozen QueRyu source\n", 1)[1]
    program = textwrap.dedent(step.split("<<'PYCODE'\n", 1)[1].split("\n          PYCODE", 1)[0])
    source = {"repository": "myon-bioinformatics/QueRyu", "commit": "a" * 40}
    if fault in {"repository", "commit"}:
        source[fault] = "untrusted"
    monkeypatch.chdir(tmp_path)
    manifest = json.dumps({"projects": {"queryu": source}})
    (tmp_path / "distributions.json").write_text(manifest)
    calls = []
    live = ".test-deps/distribution-sources/queryu"
    def run(argv, **kwargs):
        calls.append(argv)
        assert argv[:3] == ["git", "-C", live]
        if argv[3] == "fetch":
            assert argv[4:] == ["--depth=1", "origin", "a" * 40]
        else:
            assert argv[3:] == ["worktree", "add", "--detach",
                str(tmp_path / ".test-deps/frozen-distribution-sources/queryu"), "a" * 40]
    def observe(argv, **kwargs):
        assert argv == ["git", "-C", live, "rev-parse", "FETCH_HEAD"]
        return ("b" if fault == "identity" else "a") * 40 + "\n"
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(subprocess, "check_output", observe)
    if fault:
        with pytest.raises(SystemExit):
            exec(compile(program, "frozen-queryu", "exec"), {})
        assert len(calls) == (1 if fault == "identity" else 0)
    else:
        exec(compile(program, "frozen-queryu", "exec"), {})
        assert len(calls) == 2
    assert (tmp_path / "distributions.json").read_text() == manifest
    assert "--sources .test-deps/frozen-distribution-sources --check" in text
    assert "ref: ${{ steps.resolved.outputs.queryu_sha }}" in text


if __name__ == "__main__":
    unittest.main()
