import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_parent_ci_pins.py"
EXPECTED_PIN = "9cc33f08f225eaf67d9a00489a1bf15977ebee25"


def test_workflow_parent_pins_match_canonical() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert EXPECTED_PIN in proc.stdout


def test_parent_pr_ref_json_is_not_tracked() -> None:
    for rel in ("templates/parent-pr.ref.json", "parent-pr.ref.json"):
        assert not (ROOT / rel).is_file(), rel
