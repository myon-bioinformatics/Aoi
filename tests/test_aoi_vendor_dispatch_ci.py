"""CI keeps the python -S vendor sync check and adds a verify-only dispatch job."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".github" / "workflows" / "ci.yml"


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
