"""Headless Chrome over --remote-debugging-pipe.

NUL-delimited JSON DevTools messages on fds 3 and 4. Kaleido and
choreographer (both MIT) use this approach; this file reimplements it
and does not copy their code. Standard library only, so the module can
move to another repo without the rest of this package.
"""

from __future__ import annotations

import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import time

_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")


def frame_message(message: dict) -> bytes:
    return json.dumps(message, separators=(",", ":")).encode() + b"\0"


def pop_message(buffer: bytes):
    """Return (message, rest). message is None until a NUL ends the frame."""
    if b"\0" not in buffer:
        return None, buffer
    raw, rest = buffer.split(b"\0", 1)
    return json.loads(raw), rest


def find_chrome(chrome: str | None = None) -> str:
    if sys.platform == "win32":
        raise RuntimeError("Chrome over a debugging pipe is not supported on Windows")
    if chrome:
        names = (chrome,)
    else:
        names = tuple(os.environ[key] for key in ("CHROME", "CHROMIUM") if os.environ.get(key)) or _NAMES
    for name in names:
        found = name if os.path.isfile(name) else shutil.which(name)
        if found:
            return found
    hint = chrome or os.environ.get("CHROME") or os.environ.get("CHROMIUM")
    if hint:
        raise RuntimeError("Chrome executable not found: %s" % hint)
    raise RuntimeError("Chrome/Chromium was not found on PATH. Set CHROME to the executable.")


class Chrome:
    """One browser process. call() and evaluate() reuse it."""

    def __init__(self, chrome: str | None = None, timeout: float = 60):
        self.chrome = chrome
        self.timeout = timeout
        self._proc = self._w = self._r = self._err = self._tmp = None
        self._buf = b""
        self._id = 0
        self._events: list[dict] = []

    def __enter__(self) -> Chrome:
        self.start()
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def start(self) -> None:
        if self._proc is not None:
            return
        exe = find_chrome(self.chrome)
        self._tmp = tempfile.mkdtemp(prefix="chrome-pipe-")
        try:
            self._spawn(exe)
        except Exception:
            self.close()
            raise

    def open(self, url: str) -> str:
        """Open url in a new page and return its flattened session id."""
        if self._proc is None:
            self.start()
        target = self.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = self.call("Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
        self.call("Page.enable", session=session)
        self._events.clear()
        self.call("Page.navigate", {"url": url}, session=session)
        self.wait_event("Page.loadEventFired")
        return session

    def evaluate(self, expression: str, session: str, await_promise: bool = True):
        result = self.call("Runtime.evaluate", {
            "expression": expression, "awaitPromise": await_promise, "returnByValue": True,
        }, session=session)
        if "exceptionDetails" in result:
            detail = result["exceptionDetails"]
            exc = detail.get("exception") or {}
            raise RuntimeError(exc.get("description") or detail.get("text") or "JavaScript failed")
        return (result.get("result") or {}).get("value")

    def call(self, method: str, params: dict | None = None, session: str | None = None) -> dict:
        mid = self._send(method, params, session)
        deadline = time.monotonic() + self.timeout
        while True:
            message = self._read(deadline)
            if message.get("id") == mid:
                if "error" in message:
                    err = message["error"]
                    raise RuntimeError(err.get("message") if isinstance(err, dict) else err)
                return message.get("result") or {}
            if "method" in message:
                self._events.append(message)

    def wait_event(self, method: str) -> dict:
        deadline = time.monotonic() + self.timeout
        while True:
            for index, message in enumerate(self._events):
                if message.get("method") == method:
                    return self._events.pop(index)
            message = self._read(deadline)
            if message.get("method") == method:
                return message
            if "method" in message:
                self._events.append(message)

    def close(self) -> None:
        proc, self._proc = self._proc, None
        if proc is not None and proc.poll() is None and self._w is not None:
            try:
                self._send("Browser.close")
            except OSError:
                pass
        for fd in (self._w, self._r):
            if fd is not None:
                os.close(fd)
        self._w = self._r = None
        if proc is not None:
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(5)
        if self._err is not None:
            self._err.close()
            self._err = None
        if self._tmp:
            shutil.rmtree(self._tmp, ignore_errors=True)
            self._tmp = None
        self._events.clear()

    def _spawn(self, exe: str) -> None:
        self._err = open(os.path.join(self._tmp, "chrome.err"), "w", encoding="utf-8")
        read_in, write_in = os.pipe()
        read_out, write_out = os.pipe()

        def handoff() -> None:
            # Dup above fd 4 first. dup2(3, 3) is a no-op and keeps close-on-exec.
            copies = []
            for src in (read_in, write_out):
                fd = os.dup(src)
                while fd < 5:
                    nxt = os.dup(fd)
                    os.close(fd)
                    fd = nxt
                copies.append(fd)
            os.dup2(copies[0], 3)
            os.dup2(copies[1], 4)
            os.set_inheritable(3, True)
            os.set_inheritable(4, True)
            for fd in copies + [read_in, write_in, read_out, write_out]:
                if fd not in (3, 4):
                    os.close(fd)

        try:
            self._proc = subprocess.Popen(
                [exe, "--headless", "--no-sandbox", "--disable-gpu", "--remote-debugging-pipe",
                 "--user-data-dir=" + os.path.join(self._tmp, "profile"),
                 "--allow-file-access-from-files", "about:blank"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=self._err,
                close_fds=False, preexec_fn=handoff)
        except Exception:
            for fd in (read_in, write_in, read_out, write_out):
                os.close(fd)
            raise
        os.close(read_in)
        os.close(write_out)
        self._w, self._r = write_in, read_out

    def _send(self, method: str, params: dict | None = None, session: str | None = None) -> int:
        self._id += 1
        message = {"id": self._id, "method": method, "params": params or {}}
        if session:
            message["sessionId"] = session
        os.write(self._w, frame_message(message))
        return self._id

    def _read(self, deadline: float) -> dict:
        while True:
            message, self._buf = pop_message(self._buf)
            if message is not None:
                return message
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self._r], [], [], max(0, remaining))[0]:
                raise TimeoutError("Chrome did not answer within %ss" % self.timeout)
            chunk = os.read(self._r, 1 << 20)
            if chunk:
                self._buf += chunk
                continue
            detail = ""
            try:
                detail = open(os.path.join(self._tmp, "chrome.err"), encoding="utf-8", errors="replace").read()[-800:]
            except OSError:
                pass
            raise RuntimeError("Chrome closed the pipe. " + detail)
