"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py): locks, parent pins, action pins, Node entry, benchmark guard.

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
PARENT_WORKFLOW_PIN = "fbf433b296ec047f1c9acdf4d5d12c81ff7f59e8"
ACCEPTED = {
    "vendor/fleet_check.py": "64db25eb0fd9025dbe3cbcbced8b88a39ecb9266",
    "vendor/cli_args.py": "5ae22b1a1b808eca93e3c385a8db867fbeb8ee32",
    "vendor/cli_args-LICENSE": "5ae22b1a1b808eca93e3c385a8db867fbeb8ee32",
}
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
    sources = {
        "vendor/aoi-LICENSE": (AOI, "LICENSE"),
        "vendor/py_launch.cjs": (AOI, "vendor/py_launch.cjs"),
        "vendor/fleet_check.py": (fleet.PARENT, "fleet_check.py"),
        "vendor/cli_args.py": ("myon-bioinformatics/cli_args", "cli_args.py"),
        "vendor/cli_args-LICENSE": ("myon-bioinformatics/cli_args", "LICENSE"),
    }
    rows = fleet.check_lock(ROOT, commits=ACCEPTED, sources=sources)
    assert set(rows) == set(sources)  # no row from any other repository either
    launcher = rows["vendor/py_launch.cjs"]["commit"]
    assert rows["vendor/aoi-LICENSE"]["commit"] == launcher
    assert (ROOT / "vendor/aoi-LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
    assert not (ROOT / "vendor/uv_tool_build.py").exists()  # 📦 the root pyproject.toml is the uv tool (uv tool install .)


# ==== parent pins: local rollout contract; adopted vendor locks are deliberately independent

def test_parent_workflow_references_use_reviewed_rollout_commit():
    pins = fleet.parent_refs(ROOT)
    assert pins, "shared parent references must remain observable"
    assert set(pins) == {PARENT_WORKFLOW_PIN}, pins


# ==== action pins: full SHA + version comment on every uses: (fleet.check_actions); the reviewed pins stay here

def test_every_action_is_pinned_to_its_reviewed_commit():
    pins = {
        "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
        "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0",
        "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2",
        "astral-sh/setup-uv": "1db35dd8eee11c5894872e0b383ae6c406cf738d # v10.4.0",
    }
    assert {action for action, _, version in fleet.check_actions(ROOT, pins=pins) if version} == set(pins)


# ==== Node entry: the vendored shared py_launch.cjs, called directly (no per-tool wrapper)

def test_ci_requires_node_for_node_entry_parity():
    # The test job must set up Node 26 and guard its major before running its pytest suite. The separate local-ci job
    # deliberately samples the stdlib-only runner; fleet.node() fails in the Actions "test" job when Node 26+ is missing.
    assert "actions/setup-node@" in fleet.workflow_job(ROOT, "test", node_floor=26)


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


# 🧰 Scripts: 📝 each one describes itself and ⌨️ one that reads sys.argv declares its arguments (argparse /
# cli_args). Read with ast, never run; the portfolio's script catalog reads the same facts.

class ScriptsDescribeThemselves(unittest.TestCase):
    def test_every_script_has_a_description_and_declared_arguments(self):
        fleet.check_scripts(fleet.repo_root(__file__))
