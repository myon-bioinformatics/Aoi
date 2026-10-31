"""Parent vendor dispatch in CI stays a verify of vendor.lock.json."""
import re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows").is_dir())
WORKFLOW = ROOT / ".github/workflows/ci.yml"
AT = chr(64)

SETUP_PINS = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1",
    "actions/setup-python": "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",
    "astral-sh/setup-uv": "07a047e608db84b3d8c06cd9a7c7dcc9c355c18e",
}


def _uses_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip().startswith("- uses:")]


def test_setup_actions_are_pinned_to_full_shas_and_other_actions_use_major_tags():
    lines = _uses_lines(WORKFLOW.read_text(encoding="utf-8"))
    assert lines
    for line in lines:
        if "actions/setup-" in line or "astral-sh/setup-" in line:
            match = re.search(re.escape(AT) + r"([0-9a-f]{40})\s+#\s+v\d+\.\d+\.\d+\s*$", line)
            assert match, line
            owner = line.split(AT, 1)[0].split()[-1]
            assert match.group(1) == SETUP_PINS[owner], line
        elif line.split(AT, 1)[0].strip().endswith("actions/checkout") or line.split()[-1].startswith("actions/"):
            assert re.search(re.escape(AT) + r"v\d+\s*$", line), line
        else:
            raise AssertionError(line)


def test_vendor_dispatch_verifies_the_lock_without_record():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pilot/vendor_dispatch.py" in text
    assert "vendor.lock.json" in text
    assert 'PARENT_REPOSITORY_ID: "638801160"' in text
    assert "git ls-remote" in text
    assert "refs/heads/main" in text
    invocations = [
        line for line in text.splitlines()
        if "vendor_dispatch.py" in line and not line.lstrip().startswith("#")
    ]
    assert invocations
    for line in invocations:
        assert "--record" not in line
        assert "-S" not in line
    assert (ROOT / "vendor.lock.json").is_file()
