"""Exercise real POSIX pipes with a deterministic CDP peer, without Chrome."""
import os
import sys
from pathlib import Path

import pytest

from dragowing.chrome_pipe import Chrome

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
