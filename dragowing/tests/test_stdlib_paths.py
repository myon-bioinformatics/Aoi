"""代替の入口は、markdown と numpy が入った環境では動かない。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stdlib_paths.py"


def test_min_refuses_while_markdown_and_numpy_are_installed(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--deps", "min", str(tmp_path / "out.json")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "markdown" in proc.stderr
    assert "numpy" in proc.stderr
    assert not (tmp_path / "out.json").exists()
