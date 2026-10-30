"""Opt-in pytest observation of actual browser tests, without warmup launches.

Load with ``-p scripts.observe_dragowing_startup --browser-startup-evidence PATH``.
Only tests requesting chrome_executable are observed. Assertions, test order,
launch parameters, deadlines, and production cleanup remain unchanged.
"""
from __future__ import annotations

import json
import os
import platform
import socket
import sys
from pathlib import Path

import pytest

from dragowing import render
from scripts.diagnose_dragowing_browser import DiagnosticChrome, _safe_text

_STATE = pytest.StashKey[dict]()


def runtime_context() -> dict:
    """A bounded allowlist, not an environment, address, or command-line dump."""
    try:
        network_namespace = Path("/proc/self/ns/net").stat().st_ino
    except OSError:
        network_namespace = None
    try:
        interfaces = socket.if_nameindex()
        interface_count = len(interfaces)
        loopback_present = any(name == "lo" for _, name in interfaces)
    except OSError:
        interface_count = loopback_present = None
    return {"python": platform.python_version(), "platform": sys.platform,
            "machine": platform.machine(), "kernel_release": platform.release(),
            "uid": os.getuid() if hasattr(os, "getuid") else None,
            "euid": os.geteuid() if hasattr(os, "geteuid") else None,
            "network_namespace_inode": network_namespace,
            "network_interface_count": interface_count,
            "loopback_present": loopback_present}


def pytest_addoption(parser):
    parser.addoption("--browser-startup-evidence", help="write actual-test startup JSON; no extra launches")


def pytest_configure(config):
    if config.getoption("--browser-startup-evidence"):
        config.stash[_STATE] = {"schema_version": 1, "runtime": runtime_context(),
                               "launch_count": 0, "tests": {}}


@pytest.fixture(autouse=True)
def observe_browser_startup(request):
    output = request.config.getoption("--browser-startup-evidence")
    if not output or "chrome_executable" not in request.fixturenames:
        yield
        return
    state = request.config.stash[_STATE]
    instances = []

    class ObservedChrome(DiagnosticChrome):
        def __init__(self, chrome=None, timeout=30):
            super().__init__(chrome, timeout)
            self.observed_launch = None
            self.start_calls = 0
            self.previous_launches = []
            instances.append(self)

        def start(self):
            if self._proc is not None:
                self.start_calls += 1
                return
            if self.observed_launch is not None:
                self.previous_launches.append(_browser_record(self))
            state["launch_count"] += 1
            self.observed_launch = state["launch_count"]
            self.start_calls = 1
            self.observed_executable = self.chrome
            self.observed_timeout = self.timeout
            return super().start()

    patch = pytest.MonkeyPatch()
    patch.setattr(render, "Chrome", ObservedChrome)
    try:
        yield
    finally:
        patch.undo()
        # File IO is after the test, outside its existing 8-second wall-clock
        # assertion. Do not call close, retry, --version, or another CDP probe.
        browsers = []
        for browser in instances:
            if browser.observed_launch is None:
                continue
            browsers.extend(browser.previous_launches)
            browsers.append(_browser_record(browser))
        browsers.sort(key=lambda entry: entry["launch_ordinal"])
        record = state["tests"].setdefault(request.node.nodeid, {})
        record["browsers"] = browsers


def _browser_record(browser):
    return {
        "launch_ordinal": browser.observed_launch,
        "position": "first_in_pytest" if browser.observed_launch == 1 else "subsequent_in_pytest",
        "start_calls": browser.start_calls,
        "executable_path": browser.observed_executable,
        "timeout_seconds": browser.observed_timeout,
        "cdp_product": browser.product,
        "cdp_protocol_version": browser.protocol_version,
        "readiness_elapsed_seconds": browser.readiness_elapsed_seconds,
        "spawn_elapsed_seconds": browser.spawn_elapsed_seconds,
        "readiness_transport": dict(browser.readiness_transport),
        "wait_observations": list(browser.wait_observations),
        "close_elapsed_seconds": browser.close_elapsed_seconds,
        "failure": browser.failure,
        "stderr_tail": browser.stderr_tail,
        "cleanup": browser.cleanup(),
    }


def _write(config):
    state = config.stash[_STATE]
    report = {**state, "tests": [{"nodeid": _safe_text(nodeid), **record}
                                  for nodeid, record in state["tests"].items()]}
    path = Path(config.getoption("--browser-startup-evidence"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if not item.config.getoption("--browser-startup-evidence") or "chrome_executable" not in item.fixturenames:
        return
    report = outcome.get_result()
    record = item.config.stash[_STATE]["tests"].setdefault(item.nodeid, {})
    record.setdefault("pytest_outcomes", {})[report.when] = report.outcome
    if report.when == "teardown":
        _write(item.config)


def pytest_sessionfinish(session, exitstatus):
    if session.config.getoption("--browser-startup-evidence"):
        session.config.stash[_STATE]["pytest_exitstatus"] = int(exitstatus)
        _write(session.config)
