"""Local rollout contract; adopted vendor locks are deliberately independent."""
import json
import re
from pathlib import Path

PARENT = "myon-bioinformatics/myon-bioinformatics"
PARENT_WORKFLOW_PIN = "2192ff22acafdd09e80ac722df91ee937aaedd5e"
PARENT_REPOSITORY_ID = "638801160"
RESOLVED_PARENT_REF = "${{ steps.resolve.outputs.sha }}"
LATEST_SETUP = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0",
    "actions/setup-python": "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0",
    "astral-sh/setup-uv": "07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2",
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
    assert checkout_refs == [RESOLVED_PARENT_REF], checkout_refs


def test_vendor_dispatch_verifies_the_lock_without_recording():
    text = _workflow_text()
    assert "pilot/vendor_dispatch.py --manifest vendor.lock.json" in text
    assert "--record" not in text
    assert "vendor_sync.py" not in text
    assert "python -S" not in text
    assert 'EXPECTED_ID = "' + PARENT_REPOSITORY_ID + '"' in text
    assert '["git", "ls-remote", REMOTE, LABEL]' in text
    assert 'node-version: "24"' in text
    assert 'python-version: "3.12"' in text
    assert "uv run --locked --python" in text
    assert "pytest" in text
    lock = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))
    assert lock == {"schema": "vendor-lock/1", "files": []}


def test_setup_actions_use_latest_full_shas_and_other_actions_use_major_tags():
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
            assert re.fullmatch(r"actions/[A-Za-z0-9_-]+@v[0-9]+", action), action
