"""Keep the recovered F4 stdlib suite in the normal Aoi test run."""
from pathlib import Path
import subprocess
import sys


def test_stage_transition_research_suite():
    research = Path(__file__).resolve().parents[1] / "research/gpt-r001-score-allocation"
    result = subprocess.run(
        [sys.executable, "-E", "-BS", "-m", "unittest", "-q", "test_stage_transitions"],
        cwd=research,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
