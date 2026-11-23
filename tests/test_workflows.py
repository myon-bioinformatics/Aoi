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
import repo_checks as uses  # noqa: E402
import repo_checks as lock  # noqa: E402
from dragowing.dragowing import FONT  # noqa: E402


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


def test_no_workflow_installs_a_browser_for_dragowing():
    """🖼️ DRAgoWing の SVG は親の plotly_min が描く。Chromium の取得・起動の検査はどのワークフローにも無い。"""
    for path in sorted((WORKFLOWS_ROOT / ".github/workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for word in ("install_ci_chromium", "DRAGOWING_REQUIRE_CHROME", "DRAGOWING_PINNED_PLOTLY_JS",
                     "observe_dragowing_startup", "dragowing_browser"):
            assert word not in text, (path.name, word)
    assert not (WORKFLOWS_ROOT / ".github/workflows/browser-startup-validation.yml").exists()


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
        lane = text.split('  lab-integration:', 1)[1].split('  failure-identity:', 1)[0]
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


def test_junit_identity_labels_the_event_commit_checked_out_by_both_producers():
    workflow = (WORKFLOWS_ROOT / '.github/workflows/ci.yml').read_text()
    jobs = dict(re.findall(r'^  ([a-z][\w-]*):\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)',
                           workflow, flags=re.MULTILINE | re.DOTALL))
    collector = jobs['failure-identity']
    assert 'needs: [changes, test, lab-integration]' in collector
    assert re.findall(r'^      commit-sha: (.+)$', collector, re.MULTILINE) == ['${{ github.sha }}']
    for producer in ('test', 'lab-integration'):
        # These are current-repository checkouts; lab-integration's later
        # checkout of a pinned external fixture must not determine the SHA.
        checkout = re.search(r'^      - uses: actions/checkout@.*\n((?:        .*\n)*)',
                             jobs[producer], re.MULTILINE)
        assert checkout is not None
        assert not re.search(r'^          (?:ref|repository|path):', checkout[1], re.MULTILINE)


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
                    # Aoi 直下は NagoyAction にだけ渡す（annual_scope と aoi_npb が根のファイル）
                    self.assertEqual(str(root.resolve()) in got, name == "nagoyaction")
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
            "import aoi, blueprobe, propositions, dragowing.overlap\n"
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


if __name__ == "__main__":
    unittest.main()
