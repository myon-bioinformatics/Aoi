"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py):
🔒 vendor lock · 📌 parent pins · ⏱️ benchmark guards (-S / -O) · 🧾 CI jobs (vendor-lock, vendor-dispatch, Chromium).

検査の本体は親の fleet_check.py。ここに残すのは DRAgoWing の期待値（pin・ケース・文言）だけ。
Aoi は子を subtree で持ち、全部の子のテストを1回の pytest で動かす。最上位の `vendor` パッケージは子どうしで
ぶつかるので、fleet_check はファイルの場所から固有の名前で読み込む。
"""
import importlib.util, tempfile, unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("dragowing_fleet_check", ROOT / "vendor/fleet_check.py")
fleet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fleet)

WORKFLOWS = fleet.repo_root(__file__)  # 単独では ROOT。Aoi の中では、ワークフローを持つ一番近い親
PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
ACCEPTED = {"vendor/fleet_check.py": "6c29503cf17eda856766ddfdf4d66a5b0965a8b1"}
# destination -> (repository, source)。Aoi の写しは vendor/aoi/<source>。使わない shrink_module.py・polars_min.py などは置かない
SOURCES = {where: ("myon-bioinformatics/Aoi", where.removeprefix("vendor/aoi/")) for where in (
    "vendor/aoi/scripts/fetch_module.py", "vendor/aoi/shrink/numpy_min.py", "vendor/aoi/vendor/uv_tool_build.py")}
SOURCES["vendor/fleet_check.py"] = (fleet.PARENT, "fleet_check.py")
SETUP_NODE = "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0"
SETUP_UV = "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3"


# ==== 🔒 vendor lock（旧 test_vendor_lock.py の写しの照合。scripts/check_vendor_lock.py の検査は test_vendor_lock.py）

def test_vendor_lock_matches_vendored_copy():
    rows = fleet.check_lock(ROOT, commits=ACCEPTED)
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
records = types.ModuleType('dragowing.records')
records.read_jsonl = lambda *args: []
mock.patch.dict(sys.modules, {{'dragowing.overlap': overlap, 'dragowing.records': records}}).start()
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


def _assert_required_managed_chromium(job):
    install = 'python3 scripts/install_ci_chromium.py --destination "$RUNNER_TEMP/dragowing-chromium"'
    selection = 'chromium="$RUNNER_TEMP/dragowing-chromium/chrome-linux/chrome"'
    assert install in job and selection in job
    assert job.index(install) < job.index(selection) < job.index('"$chromium" --version')
    assert 'command -v chromium' not in job
    assert 'Chromium 156.0.8078.0' in job
    assert 'exit 1' in job
    assert 'continue-on-error' not in job
    assert 'command -v google-chrome' not in job
    assert 'Installed Chromium version does not match the reviewed snapshot.' in job
    assert 'DRAGOWING_REQUIRE_CHROME=1' in job
    assert 'DRAGOWING_PINNED_PLOTLY_JS: ${{ github.workspace }}/build/test-assets/plotly.min.js' in job
    assert 'from plotly_cdn import fetch_plotly_js' in job
    assert 'CHROMIUM=%s' not in job
    assert '"$chromium" --version' in job
    assert '>> "$GITHUB_ENV"' in job


def test_python_matrix_requires_chromium_without_implicit_chrome_fallback():
    _assert_required_managed_chromium(fleet.workflow_job(WORKFLOWS, "test"))


@pytest.mark.parametrize("old,new", [
    ("python3 scripts/install_ci_chromium.py", "python3 missing-installer.py"),
    ('chromium="$RUNNER_TEMP/dragowing-chromium/chrome-linux/chrome"', 'chromium=/usr/bin/chromium'),
    ('Chromium 156.0.8078.0', 'Chromium 155.0.8059.0'),
    ('DRAGOWING_REQUIRE_CHROME=1', 'DRAGOWING_REQUIRE_CHROME=0'),
    ('shell: bash', 'continue-on-error: true\n        shell: bash'),
    ('test -x "$chromium"', 'command -v google-chrome'),
])
def test_managed_chromium_contract_rejects_missing_or_weakened_setup(old, new):
    job = fleet.workflow_job(WORKFLOWS, "test")
    assert old in job
    with pytest.raises(AssertionError):
        _assert_required_managed_chromium(job.replace(old, new))
