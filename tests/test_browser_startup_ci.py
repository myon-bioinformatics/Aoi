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


def test_timeout_thread_snapshot_is_bounded_and_redacted(monkeypatch):
    from contextlib import nullcontext
    from types import SimpleNamespace
    from scripts import diagnose_dragowing_browser as diagnostic

    class Child:
        pid = 42

        def poll(self):
            return None

    def fake_stat(pid, path, limit=4096):
        if path == "task/101/stat":
            return "101 (browser thread) S 1 0"
        if path == "task/102/stat":
            return "102 (other thread) D 1 0"
        if path == "task/101/wchan":
            return "futex_wait_queue"
        if path == "task/102/wchan":
            return "filemap_fault"
        return None

    monkeypatch.setattr(diagnostic.sys, "platform", "linux")
    monkeypatch.setattr(diagnostic.os, "scandir", lambda path: nullcontext([
        SimpleNamespace(name="101"), SimpleNamespace(name="102"),
    ]))
    monkeypatch.setattr(diagnostic, "_proc_text", fake_stat)
    result = diagnostic._thread_wait_observation(Child())
    assert result == {
        "status": "ok", "sampled": 2, "truncated": False,
        "states": {"D": 1, "S": 1},
        "wait_channels": {"filemap_fault": 1, "futex_wait_queue": 1},
    }
