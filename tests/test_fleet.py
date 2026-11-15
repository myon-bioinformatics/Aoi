"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py): vendor lock, parent pins, benchmark guard.

旧 test_blueprobe_parent_workflow_pins.py と旧 test_benchmark_optimization_guard.py をここに集めた。
共通の処理は親の fleet_check.py が持ち、ここには BlueProbe 固有の期待値（pin・メッセージ）だけを置く。
"""
import importlib.util, re
from pathlib import Path

# Aoi は子を subtree で並べて 1 回の pytest で回すので、`from vendor import …` は子同士でぶつかる。ファイルパスで読む。
_spec = importlib.util.spec_from_file_location(
    "blueprobe_fleet_check", Path(__file__).resolve().parents[1] / "vendor/fleet_check.py")
fleet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fleet)

ROOT = fleet.repo_root(__file__)
PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
ACCEPTED = {"vendor/fleet_check.py": "6c29503cf17eda856766ddfdf4d66a5b0965a8b1"}
LATEST_SETUP = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3",
}
ACTION_PINS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2"
}


def _workflow_text():
    return (ROOT / ".github/workflows" / "ci.yml").read_text(encoding="utf-8")


# ==== vendor lock: 親の共通検査 1 本だけを持つ（旧 test_no_vendor_lock_is_kept は「lock が無いこと」を見ていた）

def test_vendor_lock_matches_checked_in_bytes_and_accepted_commits():
    rows = fleet.check_lock(ROOT, commits=ACCEPTED)
    assert set(rows) == set(ACCEPTED)
    row = rows["vendor/fleet_check.py"]
    assert (row["repository"], row["source"]) == (fleet.PARENT, "fleet_check.py")


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
    for line in _workflow_text().splitlines():
        stripped = line.strip()
        if not stripped.startswith("- uses:") and not stripped.startswith("uses:"):
            continue
        use = stripped.split("uses:", 1)[1].strip()
        action = use.split()[0]
        if "setup-" in action:
            name, pin = action.split("@", 1)
            comment = use[len(action):].strip()
            assert LATEST_SETUP[name] == pin + " " + comment, use
            assert re.fullmatch(r"[0-9a-f]{40}", pin)
        elif action.startswith("actions/"):
            name, pin = use.split("@", 1)
            assert ACTION_PINS[name] == pin, use


# ==== benchmark guard（旧 test_benchmark_optimization_guard.py）: mismatch checks stay active when Python removes assert statements

def test_mismatch_exits_under_optimization_without_reporting_success():
    result = fleet.run_main(ROOT, "scripts/benchmark_accessible_walk.py",
                            "g['names']._walk = lambda root: iter(())", optimized=True, timeout=30)
    assert result.returncode != 0, result.stdout
    assert "traversal mismatch" in result.stderr
    assert result.stdout == ""
