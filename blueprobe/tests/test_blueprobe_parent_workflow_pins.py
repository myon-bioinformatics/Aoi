"""Local rollout contract; adopted vendor locks are deliberately independent."""
import re
from pathlib import Path

PARENT = "myon-bioinformatics/myon-bioinformatics"
PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
LATEST_SETUP = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3",
}
ACTION_PINS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2"
}
ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows").is_dir())


def _workflow_text():
    return (ROOT / ".github/workflows" / "ci.yml").read_text(encoding="utf-8")


def test_parent_workflow_references_use_reviewed_rollout_commit():
    uses_pins = []
    checkout_refs = []
    for path in sorted((ROOT / ".github/workflows").glob("*")):
        if path.suffix not in (".yml", ".yaml"):
            continue
        text = path.read_text(encoding="utf-8")
        # Capture mutable and shortened references too, rather than ignoring them.
        uses_pins.extend(re.findall(r"uses:\s*['\"]?" + re.escape(PARENT) + r"/[^\s@'\"]+@([^\s'\"]+)", text))
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.fullmatch(r"\s+repository:\s*['\"]?" + re.escape(PARENT) + r"['\"]?\s*", line):
                refs = [re.fullmatch(r"\s+ref:\s*(.+?)\s*", item) for item in lines[i + 1:i + 12]]
                checkout_refs.append(next((m.group(1).strip("'\"") for m in refs if m), None))
    assert uses_pins, "shared parent references must remain observable"
    assert set(uses_pins) == {PARENT_WORKFLOW_PIN}, uses_pins
    # 空の vendor.lock.json を消したので、親を checkout して lock を照合するジョブもない。
    assert checkout_refs == [], checkout_refs


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


def test_no_vendor_lock_is_kept():
    # The lock had no rows, so it was removed together with the Vendor dispatch job.
    assert not (ROOT / "vendor.lock.json").exists()


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
