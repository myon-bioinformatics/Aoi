"""Headless Chrome over --remote-debugging-pipe (stdlib only, no package imports).

NUL-delimited JSON on fds 3 and 4. Kaleido and choreographer (MIT) use this
pattern; this file reimplements it and does not copy their code.
"""

from __future__ import annotations

import json
import os
import queue
import select
import shutil
import subprocess
import sys
import tempfile
import threading
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
    """One browser process. A reader thread drains the pipe so large replies cannot deadlock."""

    def __init__(self, chrome: str | None = None, timeout: float = 30):
        self.chrome = chrome
        self.timeout = timeout
        self._proc = self._w = self._r = self._err = self._tmp = None
        self._id = 0
        self._inbox: queue.Queue = queue.Queue()
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
        self._tmp = tempfile.mkdtemp(prefix="chrome-pipe-")
        try:
            self._spawn(exe)
            self._start_reader()
        except Exception:
            self.close()
            raise

    def call(self, method: str, params: dict | None = None, session: str | None = None,
             timeout: float | None = None) -> dict:
        limit = timeout if timeout is not None else self.timeout
        mid = self._send(method, params, session)
        deadline = time.monotonic() + limit
        while True:
            message = self._recv(deadline)
            if message.get("id") == mid:
                if "error" in message:
                    err = message["error"]
                    raise RuntimeError(err.get("message") if isinstance(err, dict) else err)
                return message.get("result") or {}

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

    def wait_event(self, method: str, session: str | None = None, timeout: float | None = None) -> dict:
        limit = timeout if timeout is not None else self.timeout
        deadline = time.monotonic() + limit
        while True:
            message = self._recv(deadline)
            if message.get("method") == method:
                if session is None or message.get("sessionId") == session:
                    return message

    def close(self) -> None:
        proc, self._proc = self._proc, None
        self._stop.set()
        if self._reader is not None:
            self._reader.join(timeout=2)
            self._reader = None
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
        while not self._inbox.empty():
            try:
                self._inbox.get_nowait()
            except queue.Empty:
                break

    def _spawn(self, exe: str) -> None:
        self._err = open(os.path.join(self._tmp, "chrome.err"), "w", encoding="utf-8")
        read_in, write_in = os.pipe()
        read_out, write_out = os.pipe()

        def handoff() -> None:
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

    def _start_reader(self) -> None:
        def loop() -> None:
            buf = b""
            while not self._stop.is_set():
                ready, _, _ = select.select([self._r], [], [], 0.2)
                if not ready:
                    continue
                chunk = os.read(self._r, 1 << 20)
                if not chunk:
                    self._inbox.put({"__eof__": True})
                    return
                buf += chunk
                while True:
                    message, buf = pop_message(buf)
                    if message is None:
                        break
                    self._inbox.put(message)

        self._reader = threading.Thread(target=loop, name="chrome-pipe-reader", daemon=True)
        self._reader.start()

    def _send(self, method: str, params: dict | None = None, session: str | None = None) -> int:
        self._id += 1
        message = {"id": self._id, "method": method, "params": params or {}}
        if session:
            message["sessionId"] = session
        os.write(self._w, frame_message(message))
        return self._id

    def _recv(self, deadline: float) -> dict:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Chrome did not answer within the timeout")
            try:
                message = self._inbox.get(timeout=min(0.25, remaining))
            except queue.Empty:
                continue
            if message.get("__eof__"):
                detail = ""
                try:
                    detail = open(os.path.join(self._tmp, "chrome.err"), encoding="utf-8", errors="replace").read()[-800:]
                except OSError:
                    pass
                raise RuntimeError("Chrome closed the pipe. " + detail)
            return message
