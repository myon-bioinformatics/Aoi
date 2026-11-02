"""Parent vendor dispatch in CI stays a verify of vendor.lock.json."""
import re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows").is_dir())
WORKFLOW = ROOT / ".github/workflows/ci.yml"
AT = chr(64)

ACTION_PINS = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2",
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
}


def _uses_lines(text):
    return [
        line.strip()
        for line in text.splitlines()
        if re.match(r"(?:-\s+)?uses:", line.strip())
    ]


PARENT_REUSABLE = re.compile(r"(?:-\s+)?uses:\s+myon-bioinformatics/myon-bioinformatics/\.github/workflows/")


def _pin_ok(line):
    if PARENT_REUSABLE.match(line):
        # 親リポの reusable workflow はリリースタグがないので、40 桁 SHA だけを確認する
        return re.search(re.escape(AT) + r"[0-9a-f]{40}\s*$", line) is not None
    match = re.search(re.escape(AT) + r"([0-9a-f]{40})\s+#\s+v\d+\.\d+\.\d+\s*$", line)
    if not match:
        return False
    owner = line.split(AT, 1)[0].split()[-1]
    return ACTION_PINS.get(owner) == match.group(1)


def test_all_actions_are_pinned_to_full_shas():
    lines = _uses_lines(WORKFLOW.read_text(encoding="utf-8"))
    assert lines
    assert any(line.startswith("uses:") for line in lines)
    for line in lines:
        assert _pin_ok(line), line


def test_parent_reusable_workflow_passes_on_sha_alone():
    sha = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
    line = "uses: myon-bioinformatics/myon-bioinformatics/.github/workflows/x.yml" + AT + sha
    assert _pin_ok(line)


def test_other_repo_reusable_workflow_needs_more_than_sha():
    sha = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
    for line in (
        "uses: other-org/other-repo/.github/workflows/x.yml" + AT + sha,
        "uses: myon-bioinformatics/Aoi/.github/workflows/x.yml" + AT + sha,
    ):
        assert not _pin_ok(line), line


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


def test_action_with_sha_but_no_version_comment_fails():
    line = "uses: actions/checkout" + AT + ACTION_PINS["actions/checkout"]
    assert not _pin_ok(line), line


def test_vendor_dispatch_node_floor_matches_setup_node():
    """Execute the defensive guard at the Node 26 boundary."""
    import subprocess

    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    job = text.split("\n  vendor-dispatch:", 1)[1]
    guard = re.search(r'if \[\[ "\$node_major" -lt \d+ \]\]; then\n.*?\n          fi', job, re.S)
    assert guard is not None
    assert 'node-version: "26"' in job
    for major, expected in ((24, 1), (25, 1), (26, 0), (27, 0)):
        result = subprocess.run(
            ["bash", "-c", f"node_major={major}\n" + guard.group()],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == expected, (major, result.stdout, result.stderr)
