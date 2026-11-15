"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py): locks, parent pins, Node entry, benchmark guard.

旧 test_nagoyaction_parent_workflow_pins.py・test_nagoyaction_node_entry.py・test_benchmark_optimization_guard.py をここにまとめた。
検査の本体は親の fleet_check.py。ここに残すのは NagoyAction の期待値（pin・ケース・文言）だけ。
"""
import importlib.util, json, unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# Aoi は子を全部 1 回の pytest で回す。トップの vendor パッケージは子どうしでぶつかるので、ファイルの場所から固有の名前で読む。
_spec = importlib.util.spec_from_file_location("nagoyaction_fleet_check", ROOT / "vendor/fleet_check.py")
fleet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fleet)

AOI = "myon-bioinformatics/Aoi"
PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
ACCEPTED = {"vendor/fleet_check.py": "6c29503cf17eda856766ddfdf4d66a5b0965a8b1"}
TOOL, ENV_VAR = "nagoyaction.py", "NAGOYACTION_PYTHON"
CASES = [
    {"id": "help", "args": ["--help"], "rc": 0},
    {"id": "bogus", "args": ["--bogus"], "rc": 2},
    {"id": "show", "args": ["show", "pipelines/inbox.toml"], "rc": 0},
    {"id": "dry-run", "args": ["run", "pipelines/inbox.toml", "--dry-run", "--offline"], "rc": 0},
    {"id": "missing-pipeline", "args": ["show", "no-such.toml"], "rc": 2},
    {"id": "missing-pipeline-json", "args": ["--json", "show", "no-such.toml"], "rc": 2},
]
needs_node = pytest.mark.skipif(fleet.node() is None, reason="Node 26+ not available (set NODE)")


# ==== vendor lock: bytes and commits (fleet.check_lock); where each file comes from stays here

def test_vendor_lock_matches_checked_in_bytes_and_accepted_commits():
    rows = fleet.check_lock(ROOT, commits=ACCEPTED)
    assert {where: (row["repository"], row["source"]) for where, row in rows.items()} == {
        "vendor/aoi-LICENSE": (AOI, "LICENSE"),
        "vendor/py_launch.cjs": (AOI, "vendor/py_launch.cjs"),
        "vendor/uv_tool_build.py": (AOI, "vendor/uv_tool_build.py"),
        "vendor/fleet_check.py": (fleet.PARENT, "fleet_check.py"),
    }
    launcher = rows["vendor/py_launch.cjs"]["commit"]
    assert rows["vendor/aoi-LICENSE"]["commit"] == launcher
    assert (ROOT / "vendor/aoi-LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
    # The launcher and license stay on their own Aoi pin; the builder is a later first-parent commit.
    assert rows["vendor/uv_tool_build.py"]["commit"] != launcher


# ==== parent pins: local rollout contract; adopted vendor locks are deliberately independent

def test_parent_workflow_references_use_reviewed_rollout_commit():
    pins = fleet.parent_refs(ROOT)
    assert pins, "shared parent references must remain observable"
    assert set(pins) == {PARENT_WORKFLOW_PIN}, pins


# ==== Node entry: the vendored shared py_launch.cjs, called directly (no per-tool wrapper)

def test_ci_requires_node_for_node_entry_parity():
    # The test job must set up Node before running its pytest suite. The separate local-ci job deliberately
    # samples the stdlib-only runner; fleet.node() fails in the Actions "test" job when Node 26+ is missing.
    job = fleet.workflow_job(ROOT, "test")
    assert "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1" in job
    assert "node-version: '26'" in job
    assert "Require supported Node in parity CI" in job


def test_no_per_tool_wrapper_and_readme_documents_the_direct_command():
    assert not (ROOT / "nagoyaction.cjs").exists()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"node vendor/py_launch.cjs --env-var {ENV_VAR} -- {TOOL}" in readme
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["engines"]["node"] == ">=26"


@needs_node
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_node_matches_python(case):
    via_node, via_python = fleet.node_parity(ROOT, TOOL, ENV_VAR, *case["args"])
    assert via_python[0] == case["rc"]
    assert via_node == via_python


@needs_node
def test_vendored_launcher_keeps_its_contract():
    fleet.launcher_contract(ROOT, ENV_VAR)


# ==== benchmark guard: parity guards must execute without requiring git history, even under -O

class OptimizedBenchmarkTests(unittest.TestCase):
    def test_mismatch_stops_without_success_json(self):
        patch = ("g['subprocess'].check_output = lambda *a, **kw: b'def check_local(*a, **kw): return [1]'\n"
                 "g['linkcheck'].check_local = lambda *a, **kw: []")
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = fleet.run_main(ROOT, "scripts/benchmark_link_case_index.py", patch, optimized=optimized, timeout=30)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("link report mismatch", result.stderr)
                self.assertEqual(result.stdout, "")
