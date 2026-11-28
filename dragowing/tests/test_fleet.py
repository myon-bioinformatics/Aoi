"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py):
🔒 vendor lock · 📌 parent pins · ⏱️ benchmark guards (-S / -O) · 🧾 CI jobs (vendor-lock, vendor-dispatch, no browser).

検査の本体は親の fleet_check.py。ここに残すのは DRAgoWing の期待値（pin・ケース・文言）だけ。
Aoi は子を subtree で持ち、全部の子のテストを1回の pytest で動かす。最上位の `vendor` パッケージは子どうしで
ぶつかるので、fleet_check はファイルの場所から固有の名前で読み込む。
"""
import sys
import importlib.util, tempfile, unittest
from pathlib import Path

import pytest


def load_vendored(name, relpath):
    """Load a vendored file by path under a repo-unique name (cli_args README: Loading a vendored copy)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / relpath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


ROOT = Path(__file__).resolve().parents[1]
fleet = load_vendored("dragowing_fleet_check", "vendor/fleet_check.py")

WORKFLOWS = fleet.repo_root(__file__)  # 単独では ROOT。Aoi の中では、ワークフローを持つ一番近い親
PARENT_WORKFLOW_PIN = "main"  # 🔁 own sources follow main (2026-11-28)
ACCEPTED = {"vendor/fleet_check.py",
            # 📊 親の stdlib_min の plotly_min（静止の図の SVG を Chrome なしで描く）
            "vendor/tools/stdlib_min/plotly_min.py",
            # 📝 自作の markdown.py（ページの文章。Python-Markdown の代わり）
            "vendor/markdown/markdown.py",
            "vendor/cli_args/cli_args.py",
            "vendor/cli_args/LICENSE"}  # 🔁 locked destinations; they follow main
# destination -> (repository, source)。Aoi の写しは vendor/aoi/<source>。使わない shrink_module.py・polars_min.py などは置かない
SOURCES = {"vendor/aoi/shrink/numpy_min.py": ("myon-bioinformatics/Aoi", "shrink/numpy_min.py")}
SOURCES["vendor/fleet_check.py"] = (fleet.PARENT, "fleet_check.py")
SOURCES["vendor/tools/stdlib_min/plotly_min.py"] = (fleet.PARENT, "tools/stdlib_min/plotly_min.py")
SOURCES["vendor/markdown/markdown.py"] = ("myon-bioinformatics/markdown", "markdown.py")
SOURCES["vendor/cli_args/cli_args.py"] = ("myon-bioinformatics/cli_args", "cli_args.py")
SOURCES["vendor/cli_args/LICENSE"] = ("myon-bioinformatics/cli_args", "LICENSE")
# 🌡️ the heatmap page (scripts/build_heatmap_page.py) builds its sheet, controls and browser modules from it under python -S
SETUP_NODE = "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0"
SETUP_UV = "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3"


# ==== 🔒 vendor lock（旧 test_vendor_lock.py の写しの照合。scripts/check_vendor_lock.py の検査は test_vendor_lock.py）

def test_vendor_lock_matches_vendored_copy():
    rows = fleet.check_lock(ROOT)
    assert {where: (row["repository"], row["source"]) for where, row in rows.items()} == SOURCES
    for row in rows.values():
        assert set(row) == {"repository", "ref", "commit", "source", "destination", "blob_sha", "sha256"}


# ==== 📌 parent pins（旧 test_dragowing_parent_workflow_pins.py）: local rollout contract; adopted vendor locks are deliberately independent

def test_parent_workflow_references_use_reviewed_rollout_commit():
    pins = fleet.parent_refs(WORKFLOWS)
    assert pins, "shared parent references must remain observable"
    assert set(pins) == {PARENT_WORKFLOW_PIN}, pins


# ==== ⏱️ benchmark guards: parity checks run without git history and survive -O

# scripts/benchmark_overlap.py の worker: 2 回目の load_overlap が違う答えを返す
WORKER = """from pathlib import Path
overlap = types.ModuleType('dragowing.overlap')
overlap.default_conditions = lambda *args: []
answers = iter([{{'regions': []}}, {{'regions': [1] if {mismatch} else []}}])
overlap.load_overlap = lambda *args, **kwargs: next(answers)
records = types.ModuleType('dragowing.dragowing')
records.read_jsonl = lambda *args: []
mock.patch.dict(sys.modules, {{'dragowing.overlap': overlap, 'dragowing.dragowing': records}}).start()
g['main'] = lambda: g['worker'](types.SimpleNamespace(results=Path({tmp!r}), worker='stdlib', warm_repeats=1))
"""
# scripts/benchmark_overlap.py の controller: 2 つの backend の JSON が違う
CONTROLLER = """import json
g['platform'].platform()
def report(backend, digest):
    return types.SimpleNamespace(stdout=json.dumps(dict(
        backend=backend, canonical_sha256=digest,
        cold_seconds=1, warm_median_seconds=1, python_peak_bytes=1, process_peak_rss_bytes=1)))
mock.patch.object(g['subprocess'], 'run', side_effect=[report('native', 'same'), report('stdlib', 'other' if {mismatch} else 'same')]).start()
sys.argv = [sys.argv[1], '--results', {tmp!r}, '--repeats', '1']
"""


class OptimizedBenchmarkTests(unittest.TestCase):
    """旧 test_benchmark_optimization_guard.py（scripts/benchmark_record_selection.py）。"""

    def test_mismatch_stops_without_success_json(self):
        patch = ("g['subprocess'].check_output = lambda *a, **kw: b'def select_items(*a, **kw): return [1]'\n"
                 "g['records'].select_items = lambda *a, **kw: []\n")
        result = fleet.run_main(ROOT, "scripts/benchmark_record_selection.py", patch, optimized=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('selection mismatch', result.stderr)
        self.assertEqual(result.stdout, '')


class BenchmarkValidationTests(unittest.TestCase):
    """旧 test_benchmark_validation.py（scripts/benchmark_overlap.py の controller と worker）。"""

    def test_parity_in_both_interpreter_modes(self):
        for optimized in (False, True):
            for worker in (False, True):
                for mismatch in (False, True):
                    with self.subTest(optimized=optimized, worker=worker, mismatch=mismatch), \
                         tempfile.TemporaryDirectory() as tmp:
                        for name in ('season.jsonl', 'propositions.jsonl'):
                            (Path(tmp) / name).write_text('[]')
                        patch = (WORKER if worker else CONTROLLER).format(mismatch=mismatch, tmp=tmp)
                        result = fleet.run_main(ROOT, "scripts/benchmark_overlap.py", patch, optimized=optimized)
                        if mismatch:
                            self.assertEqual(result.returncode, 1, result.stderr)
                            self.assertEqual(result.stdout, '')
                            self.assertIn('result mismatch' if worker else 'backend JSON differs', result.stderr)
                        else:
                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertTrue(result.stdout.startswith('{'))


# ==== 🧾 CI jobs（旧 test_vendor_dispatch_ci.py）: parent vendor_dispatch verify job stays beside the existing vendor-lock check

def test_vendor_lock_check_stays_on_python_s():
    job = fleet.workflow_job(WORKFLOWS, "vendor-lock")
    assert "python -S scripts/check_vendor_lock.py --aoi .test-deps/aoi" in job
    assert "python -S scripts/check_vendor_lock.py --aoi .test-deps/aoi --warn" in job
    assert "vendor_dispatch.py" not in job
    assert "--record" not in job


def test_vendor_dispatch_verifies_the_lock_without_record():
    text = (WORKFLOWS / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python -m pytest" not in text
    assert 'uv run --locked --python "${{ matrix.python }}" pytest' in text
    job = fleet.workflow_job(WORKFLOWS, "vendor-dispatch")
    assert "needs: changes" in job
    assert "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1" in job
    assert SETUP_NODE in job
    assert "actions/setup-python" not in text
    assert SETUP_UV in job
    assert 'node-version: "26"' in job
    assert 'python-version: "3.15"' in job
    assert "git ls-remote https://github.com/myon-bioinformatics/myon-bioinformatics refs/heads/main" in job
    assert 'PARENT_REPOSITORY_ID: "638801160"' in job
    assert "python -S" not in job
    assert "python .test-deps/parent/pilot/vendor_dispatch.py --manifest vendor.lock.json" in job
    assert "--record" not in job
    assert "repository: myon-bioinformatics/myon-bioinformatics" not in job


def test_python_matrix_installs_no_browser():
    """🖼️ SVG は plotly_min が描くので、テストの行列に Chrome / Chromium を入れない。"""
    job = fleet.workflow_job(WORKFLOWS, "test")
    for word in ("chromium", "chrome", "DRAGOWING_PINNED_PLOTLY_JS", "install_ci_chromium"):
        assert word.lower() not in job.lower(), word


# 🧰 Scripts: 📝 each one describes itself and ⌨️ one that reads sys.argv declares its arguments (argparse /
# cli_args). Read with ast, never run; the portfolio's script catalog reads the same facts.

class ScriptsDescribeThemselves(unittest.TestCase):
    def test_every_script_has_a_description_and_declared_arguments(self):
        fleet.check_scripts(fleet.repo_root(__file__))

    def test_pull_request_ci_stays_quick(self):
        # ⏱ push limited to branches, superseded PR runs cancelled, every job timed (fleet_check.check_ci)
        fleet.check_ci(fleet.repo_root(__file__))

    def test_root_scripts_import_only_the_standard_library(self):
        root = fleet.repo_root(__file__)
        for path in sorted(root.glob("*.py")):
            if path.name != "conftest.py":
                fleet.check_imports(root, path.name)

    def test_no_top_level_vendor_package_imports(self):
        assert fleet.check_no_vendor_package_imports(ROOT) == []
