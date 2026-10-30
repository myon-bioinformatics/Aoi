"""Resource regressions ported from Aoi PR #121; no real browser required."""
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from dragowing import chrome_pipe
from dragowing.chrome_pipe import Chrome


pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX pipe transport")


def _is_open(fd):
    try:
        os.fstat(fd)
    except OSError as exc:
        if exc.errno == errno.EBADF:
            return False
        raise
    return True


def test_second_pipe_allocation_failure_closes_first_pair(monkeypatch):
    from dragowing import chrome_pipe

    real_pipe = os.pipe
    allocated = []
    calls = 0
    error = None
    leaked = []
    browser = Chrome(sys.executable, timeout=1)

    def fail_second_pipe():
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError(errno.EMFILE, "injected second pipe allocation failure")
        pair = real_pipe()
        allocated.extend(pair)
        return pair

    try:
        with monkeypatch.context() as patch:
            patch.setattr(chrome_pipe.os, "pipe", fail_second_pipe)
            try:
                browser.start()
            except OSError as exc:
                error = exc
        leaked = [fd for fd in allocated if _is_open(fd)]
    finally:
        # The transport does not retain these descriptors on this failure path.
        # Release them ourselves before the leak assertion below.
        for fd in allocated:
            if _is_open(fd):
                os.close(fd)
        browser.close()

    assert calls == 2 and len(allocated) == 2
    assert error is not None and error.errno == errno.EMFILE
    assert all(not _is_open(fd) for fd in allocated)
    assert browser._proc is browser._tmp is browser._err is None
    assert not leaked, f"second pipe failure left descriptors open: {leaked}"


_HIGH_FD_PROBE = r"""
import errno, importlib.util, json, os, resource, select, signal, sys, tempfile

spec = importlib.util.spec_from_file_location("chrome_pipe_resource_probe", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tempfile.tempdir = sys.argv[3]
browser = module.Chrome(sys.argv[2], timeout=1)
held = []
outcome = {}
proc = None
profile = None

def error_record(exc):
    return {"type": type(exc).__name__, "message": str(exc)}

def alarm(_signum, _frame):
    raise TimeoutError("high-FD resource probe exceeded its own ten-second budget")

signal.signal(signal.SIGALRM, alarm)
signal.alarm(10)
try:
    soft, _hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if soft != resource.RLIM_INFINITY and soft < 1100:
        outcome["skip"] = "soft descriptor limit below 1100; no resource limit is changed"
    else:
        try:
            while not held or held[-1] < 1030:
                held.append(os.open(os.devnull, os.O_RDONLY))
        except OSError as exc:
            if exc.errno not in (errno.EMFILE, errno.ENFILE):
                raise
            outcome["skip"] = "insufficient descriptors for the bounded high-FD probe"
        if "skip" not in outcome:
            try:
                select.select([held[-1]], [], [], 0)
            except ValueError:
                pass
            else:
                outcome["skip"] = "this platform's select accepts the bounded probe descriptor"
        if "skip" not in outcome:
            outcome["highest_held_fd"] = held[-1]
            outcome["start_error"] = None
            try:
                browser.start()
                outcome["pipe_fds"] = [browser._w, browser._r]
                payload = {"blob": "high-fd-" * 200000}
                outcome["echo_ok"] = browser.call("Echo", payload, timeout=5) == payload
            except Exception as exc:
                outcome["start_error"] = error_record(exc)
            proc, profile = browser._proc, browser._tmp
            outcome["close_error"] = None
            try:
                browser.close()
            except Exception as exc:
                outcome["close_error"] = error_record(exc)
            outcome["returncode_after_close"] = proc.poll() if proc is not None else None
            outcome["process_alive_after_close"] = proc is not None and proc.poll() is None
            outcome["profile_exists_after_close"] = profile is not None and os.path.exists(profile)
finally:
    # Do not depend on the broken graceful-close path for harness cleanup.
    # The deterministic peer has no descendants. Reap it before asking close()
    # to dispose of descriptors, its reader, stderr and the temporary profile.
    proc = browser._proc or proc
    if proc is not None:
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=3)
    browser.close()
    for fd in held:
        os.close(fd)
    signal.alarm(0)

outcome["cleanup_complete"] = (
    browser._proc is browser._reader is browser._w is browser._r is browser._tmp is None
    and (proc is None or proc.poll() is not None)
    and (profile is None or not os.path.exists(profile))
)
print(json.dumps(outcome))
"""


def test_high_descriptors_support_startup_and_close(tmp_path):
    peer = tmp_path / "resource-cdp-peer"
    peer.write_text("#!" + sys.executable + "\n" + textwrap.dedent(r"""
        import json, os, signal
        signal.alarm(10)
        pending = b""
        while True:
            chunk = os.read(3, 65536)
            if not chunk:
                break
            pending += chunk
            while b"\0" in pending:
                raw, pending = pending.split(b"\0", 1)
                message = json.loads(raw)
                if message["method"] == "Browser.close":
                    raise SystemExit(0)
                reply = json.dumps({"id": message["id"], "result": message.get("params", {})}).encode() + b"\0"
                while reply:
                    reply = reply[os.write(4, reply):]
    """), encoding="utf-8")
    peer.chmod(0o755)
    source = Path(chrome_pipe.__file__).resolve()
    completed = subprocess.run(
        [sys.executable, "-I", "-S", "-c", _HIGH_FD_PROBE, str(source), str(peer), str(tmp_path)],
        capture_output=True, text=True, timeout=20, check=False,
    )
    # Harness errors are regular failures, never absorbed by the xfail marker.
    assert completed.returncode == 0, completed.stderr
    outcome = json.loads(completed.stdout)
    assert outcome["cleanup_complete"], outcome
    if "skip" in outcome:
        pytest.skip(outcome["skip"])
    assert outcome["highest_held_fd"] >= 1030
    start_error = outcome["start_error"]
    close_error = outcome["close_error"]
    assert start_error is None, outcome
    assert min(outcome["pipe_fds"]) >= 1024, outcome
    assert outcome["echo_ok"], outcome
    assert outcome["returncode_after_close"] == 0, outcome
    assert outcome["close_error"] is None, outcome
    assert not outcome["process_alive_after_close"], outcome
    assert not outcome["profile_exists_after_close"], outcome
