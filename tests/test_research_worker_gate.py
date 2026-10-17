"""Guard the question inbox from the not-yet-connected autonomous research worker.

The research_loop modules have offline tests, but inbox.py intentionally has
no "worker" CLI entry point. Until there is an end-to-end implementation, the
old scheduled workflow must not call its stale research.toml pipeline.
"""
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_unimplemented_worker_has_no_actions_entry_point():
    # Check all live workflows, not only the former research-worker filename:
    # otherwise a renamed cron job could reproduce the failure.
    assert not (WORKFLOWS / "research-worker.yml").exists()
    for workflow in (*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")):
        assert "nagoyaction/pipelines/research.toml" not in workflow.read_text(
            encoding="utf-8"
        ), workflow.name


def test_inbox_schedule_and_intake_pipeline_are_preserved():
    workflow = (WORKFLOWS / "research-inbox.yml").read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "vars.AOI_INBOX_ISSUE" in workflow
    assert "nagoyaction/pipelines/inbox.toml" in workflow
    assert "nagoyaction/pipelines/research.toml" not in workflow

    with (ROOT / "nagoyaction/pipelines/inbox.toml").open("rb") as source:
        pipeline = tomllib.load(source)
    assert len(pipeline["step"]) == 1
    assert pipeline["step"][0]["name"] == "intake"
    assert pipeline["step"][0]["run"] == [
        "python", "nagoyaction/inbox/inbox.py", "intake"
    ]


def test_research_cli_is_explicitly_not_connected():
    # This test should be revised *together with* the new worker and its
    # bounded checkpoint/restart tests, before re-enabling any schedule.
    completed = subprocess.run(
        [sys.executable, str(ROOT / "nagoyaction/inbox/inbox.py"), "worker", "--seconds", "1"],
        cwd=ROOT, capture_output=True, text=True, timeout=10, check=False
    )
    assert completed.returncode == 2
    assert "invalid choice: 'worker'" in completed.stderr
