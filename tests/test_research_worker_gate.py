"""Keep Actions activation deferred while NagoyAction's offline worker is reviewed.

No live Actions entry point is restored before exact-head CI, independent review
and a separate canary decision. The question inbox remains independent.
"""
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_worker_has_no_actions_entry_point_before_canary_review():
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


def test_research_cli_requires_explicit_enablement():
    import os
    for enabled in ("", "0"):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "nagoyaction/inbox/inbox.py"), "worker", "--seconds", "1"],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=False,
            env={**os.environ, "AOI_RESEARCH_ENABLED": enabled, "AOI_INBOX_ISSUE": "1"},
        )
        assert completed.returncode == 1
        assert "worker disabled" in completed.stderr


def test_owner_pipeline_is_offline_and_bounded():
    with (ROOT / "nagoyaction/pipelines/research.toml").open("rb") as source:
        pipeline = tomllib.load(source)
    assert len(pipeline["step"]) == 1
    assert pipeline["step"][0]["network"] is False
    assert "18000" not in pipeline["step"][0]["run"]
