"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py): vendor lock, parent pins, benchmark guard.

旧 test_blueprobe_parent_workflow_pins.py と旧 test_benchmark_optimization_guard.py をここに集めた。
共通の処理は親の fleet_check.py が持ち、ここには BlueProbe 固有の期待値（pin・メッセージ）だけを置く。
"""
import unittest
import importlib.util, re
from pathlib import Path

# Aoi は子を subtree で並べて 1 回の pytest で回すので、`from vendor import …` は子同士でぶつかる。ファイルパスで読む。
_spec = importlib.util.spec_from_file_location(
    "blueprobe_fleet_check", Path(__file__).resolve().parents[1] / "vendor/fleet_check.py")
fleet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fleet)

ROOT = fleet.repo_root(__file__)
PARENT_WORKFLOW_PIN = "fbf433b296ec047f1c9acdf4d5d12c81ff7f59e8"
ACCEPTED = {"vendor/fleet_check.py": "64db25eb0fd9025dbe3cbcbced8b88a39ecb9266"}
ACTION_PINS = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3",
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2",
}


def _workflow_text():
    return (ROOT / ".github/workflows" / "ci.yml").read_text(encoding="utf-8")


# ==== vendor lock: 親の fleet_check（旧 test_no_vendor_lock_is_kept は「lock が無いこと」を見ていた。uv tool はルートの pyproject）

def test_vendor_lock_matches_checked_in_bytes_and_accepted_commits():
    rows = fleet.check_lock(ROOT, commits=ACCEPTED)
    assert set(rows) == set(ACCEPTED)
    row = rows["vendor/fleet_check.py"]
    assert (row["repository"], row["source"]) == (fleet.PARENT, "fleet_check.py")
    assert not (ROOT / "vendor/uv_tool_build.py").exists()


# ==== parent pins: local rollout contract; adopted vendor locks are deliberately independent

def test_parent_workflow_references_use_reviewed_rollout_commit():
    refs = fleet.parent_refs(ROOT)  # mutable and shortened references are captured too
    assert refs, "shared parent references must remain observable"
    assert set(refs) == {PARENT_WORKFLOW_PIN}, refs
    # 親を checkout して lock を照合するジョブは持たない（lock はこのテストがオフラインで照合する）。
    workflows = "\n".join(p.read_text(encoding="utf-8") for p in sorted((ROOT / ".github/workflows").glob("*.y*ml")))
    assert not re.search(r"repository:\s*['\"]?" + re.escape(fleet.PARENT) + r"['\"]?\s*$", workflows, re.M)


def test_no_vendor_dispatch_job_remains():
    text = _workflow_text()
    assert "vendor-dispatch" not in text
    assert "vendor_dispatch.py" not in text
    assert "vendor.lock.json" not in text
    assert "--record" not in text
    assert "vendor_sync.py" not in text
    assert "python -S" not in text
    assert "uv run --locked --python" in text
    assert "pytest" in text
    assert "actions/setup-python" not in text


def test_actions_use_reviewed_full_shas_and_version_comments():
    assert fleet.check_actions(ROOT, ACTION_PINS)  # 全 uses: が 40 桁 SHA + 版コメント、かつレビュー済みの pin


# ==== benchmark guard（旧 test_benchmark_optimization_guard.py）: mismatch checks stay active when Python removes assert statements

def test_mismatch_exits_under_optimization_without_reporting_success():
    result = fleet.run_main(ROOT, "scripts/benchmark_accessible_walk.py",
                            "g['names']._walk = lambda root: iter(())", optimized=True, timeout=30)
    assert result.returncode != 0, result.stdout
    assert "traversal mismatch" in result.stderr
    assert result.stdout == ""


# 🧰 Scripts: 📝 each one describes itself and ⌨️ one that reads sys.argv declares its arguments (argparse /
# cli_args). Read with ast, never run; the portfolio's script catalog reads the same facts.

class ScriptsDescribeThemselves(unittest.TestCase):
    def test_every_script_has_a_description_and_declared_arguments(self):
        fleet.check_scripts(fleet.repo_root(__file__))
