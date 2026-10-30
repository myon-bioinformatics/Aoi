"""Contract tests for the one-command cold-start CI wrapper (no real browser)."""
import os
import sys
from pathlib import Path

from scripts import run_browser_startup_ci


def test_runner_invokes_real_tests_once_without_warmup(tmp_path, monkeypatch):
    output = tmp_path / "startup evidence"
    calls = []

    def fake_call(command, *, env):
        calls.append((command, env))
        return 17

    monkeypatch.setenv("CHROME", "/usr/bin/chromium")
    monkeypatch.setenv("DRAGOWING_PINNED_PLOTLY_JS", "/tmp/plotly.js")
    monkeypatch.setattr(run_browser_startup_ci.subprocess, "call", fake_call)
    assert run_browser_startup_ci.main(["--output", str(output)]) == 17
    assert output.is_dir()
    assert len(calls) == 1
    command, env = calls[0]
    assert command[:7] == [
        sys.executable, "-m", "pytest", "-c", "pyproject.toml", "-q",
        "-p",
    ]
    assert "scripts.observe_dragowing_startup" in command
    assert f"--browser-startup-evidence={output / 'actual-tests.json'}" in command
    assert f"--junitxml={output / 'actual-tests.xml'}" in command
    assert command.index("dragowing/tests/test_chrome_pipe.py") < command.index("dragowing/tests/test_render.py")
    assert env["CHROME"] == "/usr/bin/chromium"
    assert env["DRAGOWING_REQUIRE_CHROME"] == "1"
    assert env["DRAGOWING_EXPORT_EVIDENCE_DIR"] == str(output / "export-evidence")
    assert env["DRAGOWING_PINNED_PLOTLY_JS"] == "/tmp/plotly.js"


def test_runner_rejects_implicit_browser_selection(tmp_path, monkeypatch):
    monkeypatch.delenv("CHROME", raising=False)
    try:
        run_browser_startup_ci.main(["--output", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("CHROME must be explicitly configured")
