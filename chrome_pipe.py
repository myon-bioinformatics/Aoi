"""Headless Chromium (or an explicitly selected Chrome) over --remote-debugging-pipe (POSIX, stdlib only).

NUL-delimited JSON on fds 3 and 4. Calls are serial; events received before a
command reply are retained for wait_event(). No preexec_fn runs after fork.
"""
from __future__ import annotations

import json
import math
import os
import queue
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from pathlib import Path

# Automatic discovery is Chromium-only. Legacy names and explicit Chrome
# paths remain supported through chrome=, CHROME, and CHROMIUM.
_NAMES = ("chromium", "chromium-browser")
# Only the two CDP pipe ends survive into this short-lived exec helper. Duplicate
# both before assigning 3/4, since either inherited end may already use 3 or 4.
_HANDOFF = """
import os, sys
r, w = map(int, sys.argv[1:3])
a, b = os.dup(r), os.dup(w)
os.dup2(a, 3, inheritable=True)
os.dup2(b, 4, inheritable=True)
os.set_inheritable(3, True)
os.set_inheritable(4, True)
for fd in {r, w, a, b} - {3, 4}:
    os.close(fd)
os.execv(sys.argv[3], sys.argv[3:])
"""


def frame_message(message: dict) -> bytes:
    return json.dumps(message, separators=(",", ":")).encode() + b"\0"


def pop_message(buffer: bytes):
    """Return (message, rest). message is None until a NUL ends the frame."""
    if b"\0" not in buffer:
        return None, buffer
    raw, rest = buffer.split(b"\0", 1)
    message = json.loads(raw)
    if not isinstance(message, dict):
        raise ValueError("Chrome pipe message must be an object")
    return message, rest


def _seconds(value: float) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError("timeout must be finite and positive")
    return value


def _no_bus_address(directory: str) -> str:
    """A dbus address whose connect fails immediately.

    ``disabled:`` is not a known address type. libdbus rejects it (``Unknown
    address type``), and Chrome writes that same value when
    ``DBUS_SESSION_BUS_ADDRESS`` is unset, then still opens the system bus.
    A ``unix:path=`` that was never created is a real address, so ``connect``
    returns ``ENOENT`` instead of waiting on a bus that accepts and does not
    reply.
    """
    return "unix:path=" + os.path.join(directory, "no-bus.sock")


def _browser_environment(directory: str) -> dict:
    """Environment for a headless browser that must not wait on D-Bus."""
    env = os.environ.copy()
    address = _no_bus_address(directory)
    env["DBUS_SESSION_BUS_ADDRESS"] = address
    env["DBUS_SYSTEM_BUS_ADDRESS"] = address
    # AT-SPI and GTK portals dial the session bus even after the address above
    # has failed. Rendering does not use them.
    env["NO_AT_BRIDGE"] = "1"
    env["GTK_USE_PORTAL"] = "0"
    return env


def find_chrome(chrome: str | None = None) -> str:
    if sys.platform == "win32":
        raise RuntimeError("Chrome over a debugging pipe is not supported on Windows")
    names = (chrome,) if chrome else (
        tuple(os.environ[key] for key in ("CHROME", "CHROMIUM") if os.environ.get(key)) or _NAMES
    )
    for name in names:
        found = name if os.path.isfile(name) else shutil.which(name)
        if found and os.access(found, os.X_OK):
            return os.path.abspath(found)
    hint = chrome or os.environ.get("CHROME") or os.environ.get("CHROMIUM")
    if hint:
        raise RuntimeError("Chrome executable not found or not executable: %s" % hint)
    raise RuntimeError(
        "Chromium was not found on PATH (chromium, chromium-browser). "
        "Install Chromium or set CHROMIUM to its executable. "
        "An explicit chrome= or CHROME override remains supported."
    )


class Chrome:
    """One browser process; a reader thread drains even large replies."""

    def __init__(self, chrome: str | None = None, timeout: float = 30):
        self.chrome = chrome
        self.timeout = _seconds(timeout)
        self._proc = self._w = self._r = self._err = self._tmp = None
        self._id = 0
        self._inbox: queue.Queue = queue.Queue()
        self._events: deque = deque()
        self._failure: str | None = None
        self._stop = threading.Event()
        self._reader: threading.Thread | None = None

    def __enter__(self) -> Chrome:
        self.start()
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def start(self) -> None:
        if self._proc is not None:
            return
        exe = find_chrome(self.chrome)
        self._stop.clear()
        self._failure = None
        self._tmp = tempfile.mkdtemp(prefix="chrome-pipe-")
        try:
            self._spawn(exe)
            self._start_reader()
            # Readiness gate: the command sits in the pipe until Chrome reads it.
            # The launch budget must not be spent inside D-Bus (see _no_bus_address).
            self.call("Browser.getVersion", timeout=self.timeout)
        except Exception:
            self.close()
            raise

    def call(self, method: str, params: dict | None = None, session: str | None = None,
             timeout: float | None = None) -> dict:
        deadline = time.monotonic() + _seconds(timeout if timeout is not None else self.timeout)
        mid = self._send(method, params, session, deadline=deadline)
        while True:
            message = self._recv(deadline)
            if message.get("id") == mid:
                if "error" in message:
                    err = message["error"]
                    raise RuntimeError(err.get("message") if isinstance(err, dict) else err)
                return message.get("result") or {}
            if "method" in message:
                self._events.append(message)

    def evaluate(self, expression: str, session: str, await_promise: bool = True,
                 timeout: float | None = None):
        result = self.call("Runtime.evaluate", {
            "expression": expression, "awaitPromise": await_promise, "returnByValue": True,
        }, session=session, timeout=timeout)
        if "exceptionDetails" in result:
            detail = result["exceptionDetails"]
            exc = detail.get("exception") or {}
            raise RuntimeError(exc.get("description") or detail.get("text") or "JavaScript failed")
        return (result.get("result") or {}).get("value")

    def wait_event(self, method: str, session: str | None = None, timeout: float | None = None,
                   *, params: dict | None = None) -> dict:
        deadline = time.monotonic() + _seconds(timeout if timeout is not None else self.timeout)
        def matches(message):
            return (message.get("method") == method
                    and (session is None or message.get("sessionId") == session)
                    and all(message.get("params", {}).get(key) == value for key, value in (params or {}).items()))
        for message in self._events:
            if matches(message):
                self._events.remove(message)
                return message
        while True:
            message = self._recv(deadline)
            if matches(message):
                return message
            if "method" in message:
                self._events.append(message)

    def forget_session(self, session: str | None, target: str | None = None) -> None:
        def keep(event):
            params = event.get("params", {})
            if session is not None and session in (event.get("sessionId"), params.get("sessionId")):
                return False
            return target is None or target not in (params.get("targetId"), params.get("targetInfo", {}).get("targetId"))
        self._events = deque(event for event in self._events if keep(event))

    def close(self) -> None:
        proc = self._proc
        if proc is not None and proc.poll() is None and self._w is not None:
            try:
                self._send("Browser.close", deadline=time.monotonic() + 0.2)
            except (OSError, RuntimeError, TimeoutError):
                pass
        self._stop.set()
        if self._w is not None:
            os.close(self._w)
            self._w = None
        if proc is not None:
            try:
                proc.wait(2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        if proc is not None:
            # Also reap a renderer/zygote left behind by a crashed browser. The
            # exec helper starts a dedicated session, so this is our group only.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if self._reader is not None:
            self._reader.join(timeout=2)
            self._reader = None
        if self._r is not None:
            os.close(self._r)
            self._r = None
        self._proc = None
        if self._err is not None:
            self._err.close()
            self._err = None
        if self._tmp:
            shutil.rmtree(self._tmp, ignore_errors=True)
            self._tmp = None
        self._events.clear()
        while True:
            try:
                self._inbox.get_nowait()
            except queue.Empty:
                break

    def _spawn(self, exe: str) -> None:
        self._err = open(os.path.join(self._tmp, "chrome.err"), "w", encoding="utf-8")
        # Keep ownership local until both pipes and the child are ready.
        allocated = []
        try:
            read_in, write_in = os.pipe()
            allocated.extend((read_in, write_in))
            read_out, write_out = os.pipe()
            allocated.extend((read_out, write_out))
            args = [exe, "--headless", "--no-sandbox", "--disable-gpu", "--remote-debugging-pipe",
                    "--disable-dev-shm-usage", "--disable-background-networking", "--no-first-run",
                    "--disable-extensions", "--disable-component-extensions-with-background-pages",
                    # Keyring, crashpad, portals, and the system bus all block startup
                    # when the bus accepts and then does not reply. Headless Ozone
                    # is requested so a missing X server is not required to start.
                    "--ozone-platform=headless",
                    "--password-store=basic", "--use-mock-keychain", "--disable-breakpad",
                    "--disable-sync", "--metrics-recording-only", "--no-default-browser-check",
                    "--disable-component-update",
                    "--disable-features=MediaRouter,GlobalMediaControls,HardwareMediaKeyHandling,WebAuthenticationLinux",
                    "--user-data-dir=" + os.path.join(self._tmp, "profile"),
                    "--allow-file-access-from-files", "about:blank"]
            self._proc = subprocess.Popen(
                [sys.executable, "-S", "-c", _HANDOFF, str(read_in), str(write_out), *args],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=self._err,
                close_fds=True, pass_fds=(read_in, write_out), start_new_session=True,
                env=_browser_environment(self._tmp))
        except BaseException:
            for fd in allocated:
                os.close(fd)
            raise
        else:
            os.close(read_in)
            os.close(write_out)
        self._w, self._r = write_in, read_out
        os.set_blocking(self._w, False)

    def _start_reader(self) -> None:
        def loop() -> None:
            try:
                # epoll/kqueue/poll support descriptors beyond select() FD_SETSIZE.
                with selectors.DefaultSelector() as selector:
                    selector.register(self._r, selectors.EVENT_READ)
                    self._read_messages(selector)
            except (OSError, ValueError) as exc:
                self._inbox.put({"__failure__": "Invalid Chrome pipe: " + str(exc)})

        self._reader = threading.Thread(target=loop, name="chrome-pipe-reader", daemon=True)
        self._reader.start()

    def _read_messages(self, selector) -> None:
        buf = b""
        while not self._stop.is_set():
            ready = selector.select(0.2)
            if not ready:
                continue
            chunk = os.read(self._r, 1 << 20)
            if not chunk:
                self._inbox.put({"__failure__": "Chrome closed the pipe"})
                return
            buf += chunk
            while True:
                message, buf = pop_message(buf)
                if message is None:
                    break
                self._inbox.put(message)

    def _send(self, method: str, params: dict | None = None, session: str | None = None,
              *, deadline: float | None = None) -> int:
        if self._failure:
            raise RuntimeError(self._failure)
        if self._w is None:
            raise RuntimeError("Chrome is not running")
        self._id += 1
        message = {"id": self._id, "method": method, "params": params or {}}
        if session:
            message["sessionId"] = session
        data = memoryview(frame_message(message))
        deadline = deadline if deadline is not None else time.monotonic() + self.timeout
        with selectors.DefaultSelector() as selector:
            selector.register(self._w, selectors.EVENT_WRITE)
            while data:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._failure = "Chrome pipe write timed out"
                    raise TimeoutError("Chrome pipe write timed out")
                writable = selector.select(remaining)
                if not writable:
                    self._failure = "Chrome pipe write timed out"
                    raise TimeoutError("Chrome pipe write timed out")
                try:
                    written = os.write(self._w, data)
                except BlockingIOError:
                    continue
                except BrokenPipeError as exc:
                    self._failure = "Chrome closed the pipe. " + self._diagnostic()
                    raise RuntimeError(self._failure) from exc
                if written == 0:
                    raise RuntimeError("Chrome pipe write returned zero bytes")
                data = data[written:]
        return self._id

    def _diagnostic(self) -> str:
        if self._tmp:
            try:
                return (Path(self._tmp) / "chrome.err").read_text(encoding="utf-8", errors="replace")[-800:]
            except OSError:
                pass
        return ""

    def _timeout_error(self, message: str) -> TimeoutError:
        # Capture stderr before start() cleans the temp dir on the way out.
        if self._proc is not None and self._proc.poll() is None:
            message += "; the browser process is still running and has not answered"
        detail = self._diagnostic().strip()
        if detail:
            message += "\n" + detail
        return TimeoutError(message)

    def _recv(self, deadline: float) -> dict:
        if self._failure:
            raise RuntimeError(self._failure)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise self._timeout_error("Chrome did not answer within the timeout")
        try:
            message = self._inbox.get(timeout=remaining)
        except queue.Empty as exc:
            raise self._timeout_error("Chrome did not answer within the timeout") from exc
        if "__failure__" in message:
            self._failure = message["__failure__"] + ". " + self._diagnostic()
            raise RuntimeError(self._failure)
        return message
