"""Exercise real POSIX pipes with a deterministic CDP peer, without Chrome."""
import os
import sys
import time
from pathlib import Path

import pytest

from dragowing.chrome_pipe import Chrome
from dragowing.render import RenderSession, Timeouts

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX pipe transport")


@pytest.fixture
def peer(tmp_path):
    def create(prefix="", after_handshake=""):
        path = tmp_path / "cdp-peer"
        path.write_text("#!" + sys.executable + "\n" + prefix + '''
import json, os, sys, time
buf = b""
def send(obj):
    data = json.dumps(obj, ensure_ascii=False).encode() + b"\\0"
    while data:
        data = data[os.write(4, data):]
while True:
    chunk = os.read(3, 65536)
    if not chunk:
        break
    buf += chunk
    while b"\\0" in buf:
        raw, buf = buf.split(b"\\0", 1)
        msg = json.loads(raw)
        method = msg["method"]
        if method == "Browser.close":
            sys.exit(0)
        if method == "Crash":
            print("peer crashed", file=sys.stderr, flush=True)
            sys.exit(7)
        if method == "Malformed":
            os.write(4, b"not-json\\0")
            continue
        if method == "Never":
            continue
        if method == "Page.navigate":
            send({"method":"Page.loadEventFired", "sessionId":"other"})
            send({"method":"Page.loadEventFired", "sessionId":"page"})
        send({"id": msg["id"], "result": msg.get("params", {})})
        if method == "Browser.getVersion":
''' + ("            " + after_handshake if after_handshake else "            pass") + "\n")
        path.chmod(0o755)
        return str(path)
    return create


def test_large_frames_short_writes_and_early_events(peer, monkeypatch):
    write = os.write
    with Chrome(peer(), timeout=5) as browser:
        monkeypatch.setattr(os, "write", lambda fd, data: write(fd, data[:997]))
        payload = {"blob": "large-" * 200000}
        assert browser.call("Echo", payload) == payload
        browser.call("Page.navigate", session="page")
        assert browser.wait_event("Page.loadEventFired", "page")["sessionId"] == "page"
        assert browser.wait_event("Page.loadEventFired", "other")["sessionId"] == "other"


@pytest.mark.parametrize("method, message", [("Crash", "closed the pipe"), ("Malformed", "Invalid Chrome pipe")])
def test_midstream_failure_is_immediate_and_persistent(peer, method, message):
    with Chrome(peer(), timeout=2) as browser:
        with pytest.raises(RuntimeError, match=message):
            browser.call(method)
        with pytest.raises(RuntimeError, match=message):
            browser.call("Echo")


def test_reply_timeout_and_restart(peer):
    browser = Chrome(peer(), timeout=1)
    with browser:
        with pytest.raises(TimeoutError, match="timeout"):
            browser.call("Never", timeout=0.05)
        assert browser.call("Echo", {"after": "timeout"}) == {"after": "timeout"}
    with browser:
        assert browser.call("Echo", {"restarted": True}) == {"restarted": True}
    browser.close()  # Idempotent.
    assert browser._proc is browser._reader is browser._w is browser._r is browser._tmp is None


def test_blocked_write_obeys_deadline(peer):
    browser = Chrome(peer(after_handshake="time.sleep(60)"), timeout=1)
    with browser:
        started = time.monotonic()
        with pytest.raises(TimeoutError, match="write timed out"):
            browser.call("Echo", {"blob": "x" * 1000000}, timeout=0.05)
        assert time.monotonic() - started < 2


@pytest.mark.parametrize("prefix, error", [
    ("import sys; print('startup failed',file=sys.stderr,flush=True); sys.exit(9)\n", RuntimeError),
    ("import time; time.sleep(60)\n", TimeoutError),
])
def test_startup_failure_cleans_process_thread_and_tempdir(peer, prefix, error, monkeypatch):
    created = []
    from dragowing import chrome_pipe
    mkdtemp = chrome_pipe.tempfile.mkdtemp
    def record(*args, **kwargs):
        directory = mkdtemp(*args, **kwargs)
        created.append(Path(directory))
        return directory
    monkeypatch.setattr(chrome_pipe.tempfile, "mkdtemp", record)
    session = RenderSession(chrome=peer(prefix=prefix), timeouts=Timeouts(launch=0.1))
    with pytest.raises(error):
        session.start()
    assert created and all(not path.exists() for path in created)
    assert session._workdir is None
    assert session.browser._proc is session.browser._reader is None


def test_spawn_disables_dbus_even_if_the_parent_bus_is_stalled(peer, monkeypatch):
    from dragowing import chrome_pipe
    captured = {}

    def record(argv, **kwargs):
        captured["argv"] = argv
        captured["env"] = kwargs.get("env")
        raise OSError("cannot spawn")

    monkeypatch.setenv("DBUS_SESSION_BUS_ADDRESS", "unix:path=/tmp/stalled-session-bus")
    monkeypatch.setenv("DBUS_SYSTEM_BUS_ADDRESS", "unix:path=/tmp/stalled-system-bus")
    monkeypatch.setattr(chrome_pipe.subprocess, "Popen", record)
    browser = Chrome(peer())
    with pytest.raises(OSError, match="cannot spawn"):
        browser.start()
    env = captured["env"]
    session = env["DBUS_SESSION_BUS_ADDRESS"]
    system = env["DBUS_SYSTEM_BUS_ADDRESS"]
    assert session == system
    assert session.startswith("unix:path=")
    socket_path = session.split("=", 1)[1]
    assert socket_path.endswith(os.path.join("no-bus.sock"))
    assert not os.path.exists(socket_path)
    assert "disabled:" not in session
    assert session != "unix:path=/tmp/stalled-session-bus"
    assert env["NO_AT_BRIDGE"] == "1"
    assert "--ozone-platform=headless" in captured["argv"]
    assert "--password-store=basic" in captured["argv"]
    assert "--use-mock-keychain" in captured["argv"]
    assert "--disable-breakpad" in captured["argv"]


def test_popen_failure_closes_descriptors(peer, monkeypatch):
    from dragowing import chrome_pipe
    pipe, descriptors = os.pipe, []
    def record():
        pair = pipe()
        descriptors.extend(pair)
        return pair
    def fail(*args, **kwargs):
        raise OSError("cannot spawn")
    monkeypatch.setattr(chrome_pipe.os, "pipe", record)
    monkeypatch.setattr(chrome_pipe.subprocess, "Popen", fail)
    browser = Chrome(peer())
    with pytest.raises(OSError, match="cannot spawn"):
        browser.start()
    for fd in descriptors:
        with pytest.raises(OSError):
            os.fstat(fd)
    assert browser._tmp is browser._err is None


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
def test_invalid_timeout(value):
    with pytest.raises(ValueError, match="finite and positive"):
        Timeouts(ready=value)


def test_stderr_pressure_before_readiness_does_not_block(peer):
    # Exceeds a pipe's capacity before the peer reads Browser.getVersion.
    # This must remain a regular file, not an undrained subprocess.PIPE.
    prefix = (
        "import os, stat\n"
        "assert stat.S_ISREG(os.fstat(2).st_mode)\n"
        "data = b'x' * (2 * 1024 * 1024) + b'\\nstderr-pressure-marker\\n'\n"
        "while data:\n"
        "    data = data[os.write(2, data):]\n"
    )
    with Chrome(peer(prefix=prefix), timeout=5) as browser:
        assert browser.call("Echo", {"ready": True}) == {"ready": True}
        assert "stderr-pressure-marker" in browser._diagnostic()


def test_fragmented_utf8_replies_preserve_frames_and_events(peer):
    # Split JSON, multi-byte UTF-8, and the NUL delimiter at arbitrary reads.
    prefix = (
        "import os\n"
        "original_write = os.write\n"
        "def fragmented_write(fd, data):\n"
        "    return original_write(fd, data[:1] if fd == 4 else data)\n"
        "os.write = fragmented_write\n"
    )
    with Chrome(peer(prefix=prefix), timeout=5) as browser:
        payload = {"text": "日本語 / café / \u0000"}
        assert browser.call("Echo", payload) == payload
        browser.call("Page.navigate", session="page")
        assert browser.wait_event("Page.loadEventFired", "page")["sessionId"] == "page"
        assert browser.wait_event("Page.loadEventFired", "other")["sessionId"] == "other"


def test_delayed_readiness_is_accepted_within_launch_budget(peer):
    with Chrome(peer(prefix="import time; time.sleep(0.1)\n"), timeout=3) as browser:
        assert browser.call("Echo", {"delayed": True}) == {"delayed": True}


def test_startup_timeout_retains_stderr_before_cleanup(peer):
    executable = peer(prefix=(
        "import sys, time\n"
        "print('startup-stalled-marker', file=sys.stderr, flush=True)\n"
        "time.sleep(60)\n"
    ))
    browser = Chrome(executable, timeout=0.3)
    with pytest.raises(TimeoutError) as failure:
        browser.start()
    assert "still running" in str(failure.value)
    assert "startup-stalled-marker" in str(failure.value)
    assert browser._proc is browser._reader is browser._w is browser._r is None
    assert browser._tmp is browser._err is None


@pytest.mark.skipif(not Path('/proc/self/fd').is_dir(), reason="Linux descriptor accounting")
def test_repeated_sessions_do_not_accumulate_descriptors_or_profiles(peer):
    executable = peer()
    before = len(list(Path('/proc/self/fd').iterdir()))
    directories = []
    browser = Chrome(executable, timeout=3)
    for index in range(12):
        with browser:
            directories.append(Path(browser._tmp))
            assert browser.call("Echo", {"round": index}) == {"round": index}
        assert browser._proc is browser._reader is browser._w is browser._r is None
    assert all(not path.exists() for path in directories)
    assert len(list(Path('/proc/self/fd').iterdir())) == before
