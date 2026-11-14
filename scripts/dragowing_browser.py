"""DRAgoWing のブラウザ（Chromium）の起動の診断と、その周りの道具。ブラウザを自動では選ばない。標準ライブラリだけ（python -S で走る）。

    python -S scripts/dragowing_browser.py <処理> [その処理の引数]

処理:
  diagnose         起動の証跡を取る（旧 diagnose_dragowing_browser.py）
  startup_ci       新しい CI のジョブで、本物の Chromium の初回起動の回帰を 1 回で走らせる（旧 run_browser_startup_ci.py。python -m scripts.dragowing_browser startup_ci）
  render_fixtures  合成の 3 つの図を一度だけ描き、ブラウザの要らない検査の素材にする（旧 render_static_fixtures.py）
実際の検査の起動を記録する pytest のプラグインは scripts/observe_dragowing_startup.py（pytest を読むので別のファイル）、
描いた結果の検査（ブラウザを起動しない）は scripts/rendered_output_checks.py にある。
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import math
import os
import platform
import re
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import xml.etree.ElementTree as ET
import zlib
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:                    # dragowing/ と scripts/ を、リポジトリの直下から読む
    sys.path.insert(0, str(_ROOT))

from dragowing.chrome_pipe import Chrome, find_chrome  # noqa: E402
from dragowing.export import export_draw, PLOTLY, plotly_figure_content  # noqa: E402
from dragowing.render import RenderSession, Timeouts  # noqa: E402
from scripts.rendered_output_checks import check_png, check_svg, figures_digest  # noqa: E402


# ==== diagnose（旧 diagnose_dragowing_browser.py）

DIAGNOSE_CLI_DOC = """Validation-only browser startup evidence; no automatic browser selection.

Run from Aoi's root with ``python scripts/dragowing_browser.py diagnose --help``.
This module deliberately leaves the production transport and its budgets alone.
"""

_TAIL_BYTES = 4096
_TEXT_LIMIT = 4096


def _safe_text(value: object, limit: int = _TEXT_LIMIT) -> str:
    """Keep logs bounded and redact credential, environment and argv-shaped text."""
    text = str(value)
    text = re.sub(r"(?i)\b(?:bearer|basic)\s+\S+", "[redacted authorization]", text)
    text = re.sub(
        r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|"
        r"token|authorization|cookie)\s*[:=]\s*[^\s,;]+", "[redacted credential]", text)
    text = re.sub(r"\b[A-Z][A-Z0-9_]*=[^\s,;]+", "[redacted environment]", text)
    text = re.sub(r"--[a-zA-Z][\w-]*(?:=[^\s]+|\s+[^\s]+)?", "[redacted argument]", text)
    text = re.sub(r"\b(?:https?|wss?)://[^\s]+", "[redacted URL]", text)
    return text[-limit:]


def _tail(path: str | Path | None) -> str:
    if path is None:
        return ""
    try:
        with open(path, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            handle.seek(max(0, handle.tell() - _TAIL_BYTES))
            return _safe_text(handle.read(_TAIL_BYTES).decode("utf-8", "replace"))
    except OSError:
        return ""


def _counts() -> dict:
    try:
        descriptors = len(os.listdir("/proc/self/fd"))
    except OSError:
        descriptors = None
    return {"threads": threading.active_count(), "file_descriptors": descriptors}


def _process(proc: subprocess.Popen | None) -> dict:
    if proc is None:
        return {"pid": None, "state": "not_started", "returncode": None, "os_state": None}
    code = proc.poll()
    state = None
    # Read only the state letter, not cmdline, environ, file targets or page data.
    try:
        state = Path(f"/proc/{proc.pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        pass
    return {"pid": proc.pid, "state": "running" if code is None else "exited",
            "returncode": code, "os_state": state}


def _error(exc: Exception, stage: str) -> dict:
    return {"stage": stage, "type": type(exc).__name__, "message": _safe_text(exc)}


def _proc_text(pid: int, name: str, limit: int = 4096) -> str | None:
    """Bounded reads of fixed, caller-selected files for our unreaped child."""
    try:
        with open(f"/proc/{pid}/{name}", encoding="utf-8") as handle:
            return handle.read(limit)
    except (OSError, UnicodeError):
        return None


def _kernel_stack_observation(proc: subprocess.Popen | None) -> dict:
    """One data-bounded, existing-permission read of our unreaped child's stack.

    Only symbol names survive parsing; addresses, offsets, module annotations
    and unknown lines never enter evidence. This is not a hard wall-time bound
    on the kernel read, so call only after readiness has already failed.
    """
    result = {"status": "not_running", "symbols": None, "truncated": False,
              "omitted_lines": 0}
    if proc is None or proc.poll() is not None:
        return result
    if sys.platform != "linux":
        result["status"] = "unsupported"
        return result
    try:
        with open(f"/proc/{proc.pid}/stack", "rb", buffering=0) as handle:
            raw = handle.read(4097)  # One overflow byte; never an unbounded read.
    except OSError as exc:
        result["status"] = ("permission_denied" if isinstance(exc, PermissionError)
                            or exc.errno in (errno.EACCES, errno.EPERM) else "unavailable")
        return result
    result["truncated"] = len(raw) > 4096
    raw = raw[:4096]
    if result["truncated"]:
        # Do not accept a partial frame cut at the byte limit.
        raw = raw[:raw.rfind(b"\n") + 1]
    try:
        text = raw.decode("ascii")
    except UnicodeError:
        result["status"] = "invalid_encoding"
        return result
    symbols = []
    for line in text.splitlines():
        match = re.fullmatch(
            r"\[<[0-9A-Fa-f]+>\] ([A-Za-z_][A-Za-z0-9_.$]{0,127})"
            r"\+0x[0-9A-Fa-f]+/0x[0-9A-Fa-f]+(?: \[[A-Za-z0-9_]+\])?", line)
        if match is None:
            result["omitted_lines"] += 1
        elif len(symbols) < 32:
            symbols.append(match[1])
        else:
            result["truncated"] = True
    result["symbols"] = symbols
    result["status"] = "ok" if symbols else ("unparseable" if text or result["truncated"] else "empty")
    return result


def _pipe_observation(pid: int | None, child_fd: int, parent_fd: int | None) -> dict:
    result = {"parent_inode": None, "child_inode": None, "matches": None,
              "queued_bytes": None}
    if parent_fd is None:
        return result
    try:
        info = os.fstat(parent_fd)
        if not stat.S_ISFIFO(info.st_mode):
            return result
        result["parent_inode"] = info.st_ino
    except OSError:
        return result
    try:
        # Query only the owned endpoint; never read or consume CDP payloads.
        import array
        import fcntl
        import termios
        count = array.array("i", [0])
        fcntl.ioctl(parent_fd, termios.FIONREAD, count, True)
        result["queued_bytes"] = max(0, count[0])
    except (ImportError, AttributeError, OSError, ValueError, OverflowError):
        pass
    if pid is not None:
        try:
            target = os.readlink(f"/proc/{pid}/fd/{child_fd}")
        except OSError:
            target = ""
        # Do not retain a file path or any other non-pipe link target.
        match = re.fullmatch(r"pipe:\[(\d+)\]", target)
        if match:
            result["child_inode"] = int(match[1])
            result["matches"] = result["child_inode"] == result["parent_inode"]
    return result


def _thread_wait_observation(proc: subprocess.Popen | None) -> dict:
    """Bounded Linux thread states at the *failed* readiness deadline only.

    Capture no arguments, environment, filenames, or stacks. A thread's state
    and wait channel describe one instant and do not establish causality.
    """
    result = {"status": "not_running", "sampled": 0, "truncated": False,
              "states": {}, "wait_channels": {}}
    if proc is None or proc.poll() is not None:
        return result
    if sys.platform != "linux":
        result["status"] = "unsupported"
        return result
    try:
        with os.scandir(f"/proc/{proc.pid}/task") as entries:
            for entry in entries:
                if not entry.name.isascii() or not entry.name.isdecimal():
                    continue
                if result["sampled"] >= 64:
                    result["truncated"] = True
                    break
                raw = _proc_text(proc.pid, f"task/{entry.name}/stat")
                if not raw:
                    continue
                fields = raw.rsplit(")", 1)
                if len(fields) != 2:
                    continue
                parts = fields[1].split()
                if not parts or parts[0] not in "RSDZTtXxKWPI":
                    continue
                state = parts[0]
                wchan = _proc_text(proc.pid, f"task/{entry.name}/wchan", 128)
                channel = wchan.strip() if wchan is not None else ""
                if not re.fullmatch(r"[A-Za-z0-9_]{1,127}", channel):
                    channel = "unavailable"
                result["states"][state] = result["states"].get(state, 0) + 1
                result["wait_channels"][channel] = result["wait_channels"].get(channel, 0) + 1
                result["sampled"] += 1
    except OSError:
        result["status"] = "unavailable"
        return result
    result["status"] = "ok" if result["sampled"] else "empty"
    result["states"] = dict(sorted(result["states"].items()))
    result["wait_channels"] = dict(sorted(result["wait_channels"].items()))
    return result


def _startup_wait_snapshot(proc: subprocess.Popen | None, write_fd: int | None,
                           read_fd: int | None) -> dict:
    """Allowlisted counters, wait symbol and owned pipe identities, never contents.

    poll() returning None leaves this child unreaped, so its PID cannot be
    recycled during the reads. If it exited/reaped, do not inspect that PID.
    There is no ptrace, new process, retry, sleep or permission adjustment.
    """
    alive = proc is not None and proc.poll() is None
    pid = proc.pid if proc is not None else None
    result = {"pid": pid, "alive": alive, "state": None, "minor_faults": None,
              "major_faults": None, "user_ticks": None, "system_ticks": None,
              "wchan": None, "read_bytes": None, "write_bytes": None}
    if alive and sys.platform == "linux":
        raw = _proc_text(pid, "stat")
        if raw and raw.partition(" ")[0] == str(pid):
            try:
                fields = raw.rsplit(")", 1)[1].split()
                if fields[0] in tuple("RSDZTtXxKWPI"):
                    result["state"] = fields[0]
                for key, index in (("minor_faults", 7), ("major_faults", 9),
                                   ("user_ticks", 11), ("system_ticks", 12)):
                    if re.fullmatch(r"[0-9]+", fields[index]):
                        result[key] = int(fields[index])
            except IndexError:
                pass
        wchan = _proc_text(pid, "wchan", 128)
        if wchan is not None and re.fullmatch(r"[A-Za-z0-9_]{1,127}", wchan.strip()):
            result["wchan"] = wchan.strip()
        io = _proc_text(pid, "io")
        if io:
            for key in ("read_bytes", "write_bytes"):
                match = re.search(r"^" + key + r":\s*([0-9]+)\s*$", io, re.MULTILINE)
                if match:
                    result[key] = int(match[1])
    child_pid = pid if alive and sys.platform == "linux" else None
    result["pipes"] = {"request": _pipe_observation(child_pid, 3, write_fd),
                       "response": _pipe_observation(child_pid, 4, read_fd)}
    return result


class DiagnosticChrome(Chrome):
    """Observe the existing transport before start() can discard evidence."""

    def __init__(self, chrome: str, timeout: float):
        super().__init__(chrome=chrome, timeout=timeout)
        self._reset_observation()

    def _reset_observation(self) -> None:
        self.failure: dict | None = None
        self.product: str | None = None
        self.protocol_version: str | None = None
        self.readiness_elapsed_seconds: float | None = None
        self.close_elapsed_seconds = 0.0
        self.spawn_elapsed_seconds: float | None = None
        self.stage = "startup"
        self.method: str | None = None
        self.stderr_tail = ""
        self._started_at: float | None = None
        self._profile_root: str | None = None
        self._process_ref: subprocess.Popen | None = None
        self._reader_ref: threading.Thread | None = None
        self._observing_readiness = False
        self.readiness_transport = {"phase": "not_started", "send_elapsed_seconds": None,
                                    "received_messages": 0}
        self.wait_observations: list[dict] = []

    def _observe_wait(self, phase: str) -> None:
        # Two snapshots only: after sending and at the first reply/failure.
        # They run under the original deadline, without a sampling thread.
        if len(self.wait_observations) >= 2:
            return
        started = time.monotonic()
        elapsed = None if self._started_at is None else started - self._started_at
        observed_at = datetime.now(timezone.utc).isoformat()
        snapshot = _startup_wait_snapshot(self._proc, self._w, self._r)
        if phase == "readiness_failure":
            snapshot["kernel_stack"] = _kernel_stack_observation(self._proc)
            snapshot["thread_waits"] = _thread_wait_observation(self._proc)
        self.wait_observations.append({"phase": phase, "elapsed_seconds": elapsed,
                                       "observed_at": observed_at, **snapshot,
                                       "sample_duration_seconds": time.monotonic() - started})

    def record_failure(self, exc: Exception, stage: str | None = None) -> None:
        if self.failure is not None:
            return
        if self._observing_readiness:
            self._observe_wait("readiness_failure")
        self.failure = _error(exc, stage or self.stage)
        self.failure.update({"last_cdp_method": self.method, "process": _process(self._proc),
                             "reader_alive": bool(self._reader and self._reader.is_alive()),
                             "resources": _counts(), "stderr_tail": self._stderr(),
                             "readiness_transport": dict(self.readiness_transport)})

    def _stderr(self) -> str:
        return _tail(Path(self._tmp) / "chrome.err") if self._tmp else self.stderr_tail

    def _diagnostic(self) -> str:
        # The production exception formatter calls this hook. Keep that path
        # bounded as well, without changing Chrome._diagnostic itself.
        return self._stderr()

    def start(self) -> None:
        if self._proc is not None:
            return
        self._reset_observation()
        self._started_at = time.monotonic()
        try:
            super().start()
        except Exception as exc:
            self.record_failure(exc)
            raise

    def _spawn(self, exe: str) -> None:
        self.stage = "spawn"
        self._profile_root = self._tmp
        started = time.monotonic()
        try:
            super()._spawn(exe)
        except Exception as exc:
            self.record_failure(exc)
            raise
        finally:
            self.spawn_elapsed_seconds = time.monotonic() - started
            self._process_ref = self._proc
        self.stage = "readiness"

    def _start_reader(self) -> None:
        super()._start_reader()
        self._reader_ref = self._reader

    def call(self, method: str, *args, **kwargs) -> dict:
        self.method = method
        if method == "Target.setDiscoverTargets":
            self.stage = "session_setup"
        first_readiness = method == "Browser.getVersion" and self.readiness_elapsed_seconds is None
        self._observing_readiness = first_readiness
        try:
            result = super().call(method, *args, **kwargs)
        except Exception as exc:
            if first_readiness and self._started_at is not None:
                self.readiness_elapsed_seconds = time.monotonic() - self._started_at
            self.record_failure(exc)
            raise
        else:
            if first_readiness:
                if self._started_at is not None:
                    self.readiness_elapsed_seconds = time.monotonic() - self._started_at
                self.readiness_transport["phase"] = "response_received"
                self.product = _safe_text(result.get("product", ""), 256) or None
                self.protocol_version = _safe_text(result.get("protocolVersion", ""), 128) or None
                self._observe_wait("response_received")
            return result
        finally:
            if first_readiness and self._started_at is not None and self.readiness_elapsed_seconds is None:
                self.readiness_elapsed_seconds = time.monotonic() - self._started_at
            self._observing_readiness = False

    def _send(self, *args, **kwargs):
        if not self._observing_readiness:
            return super()._send(*args, **kwargs)
        self.readiness_transport["phase"] = "sending_request"
        started = time.monotonic()
        try:
            result = super()._send(*args, **kwargs)
        finally:
            self.readiness_transport["send_elapsed_seconds"] = time.monotonic() - started
        self.readiness_transport["phase"] = "waiting_reply"
        self._observe_wait("request_sent")
        return result

    def _recv(self, *args, **kwargs):
        result = super()._recv(*args, **kwargs)
        if self._observing_readiness:
            self.readiness_transport["received_messages"] += 1
        return result

    def close(self) -> None:
        # Chrome.start invokes close in its except block. Snapshot now, not after
        # the profile, stderr file, process and reader references have vanished.
        pending = sys.exc_info()[1]
        if isinstance(pending, Exception):
            self.record_failure(pending)
        self.stderr_tail = self._stderr()
        started = time.monotonic()
        try:
            super().close()
        finally:
            self.close_elapsed_seconds += time.monotonic() - started

    def cleanup(self) -> dict:
        return {
            "profile_removed": None if self._profile_root is None else not Path(self._profile_root).exists(),
            "reader_stopped": None if self._reader_ref is None else not self._reader_ref.is_alive(),
            "process": _process(self._process_ref),
            "pipe_descriptors_released": self._r is None and self._w is None,
            "stderr_file_closed": self._err is None,
        }


class _DiagnosticSession(RenderSession):
    def __init__(self, browser: DiagnosticChrome, timeout: float):
        super().__init__(chrome=browser.chrome, offline=True,
                         timeouts=Timeouts(launch=timeout, load=timeout, ready=timeout, capture=timeout))
        self.browser = browser
        self.workdir: str | None = None

    def close(self) -> None:
        if self._workdir:
            self.workdir = self._workdir
        super().close()


def _version(executable: str, timeout: float) -> dict:
    """Probe --version once, without retaining argv, environment or unbounded output."""
    started = time.monotonic()
    result = {"text": "", "stderr_tail": "", "returncode": None, "failure": None}
    proc = None
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            proc = subprocess.Popen([executable, "--version"], stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=err, start_new_session=True)
            proc.wait(timeout=timeout)
            result["returncode"] = proc.returncode
            if proc.returncode != 0:
                raise RuntimeError("Browser --version exited unsuccessfully")
        except Exception as exc:
            result["failure"] = _error(exc, "version")
            result["failure"]["process"] = _process(proc)
        finally:
            if proc is not None:
                # Terminate only this probe's dedicated process group, including
                # children of an executable wrapper, after success or failure.
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
                result["returncode"] = proc.returncode
            for key, handle in (("text", out), ("stderr_tail", err)):
                handle.seek(0, os.SEEK_END)
                handle.seek(max(0, handle.tell() - _TAIL_BYTES))
                result[key] = _safe_text(handle.read(_TAIL_BYTES).decode("utf-8", "replace")).strip()
    if not result["text"] and result["failure"] is None:
        result["failure"] = {"stage": "version", "type": "RuntimeError", "message": "Browser --version returned no version text"}
    result["elapsed_seconds"] = time.monotonic() - started
    return result


def _figures() -> list[dict]:
    return [{"data": [{"type": "scatter", "x": [1, 2, 3], "y": [index, 1, 4 + index],
                       "mode": "lines+markers", "name": f"diagnostic-series-{index}",
                       "marker": {"color": ["red", "blue", "green"][index], "size": 12}}],
             "layout": {"width": 400, "height": 300, "showlegend": True,
                        "title": {"text": f"diagnostic-figure-{index}"}}} for index in range(3)]


def _page_targets(browser: Chrome) -> set[str]:
    return {target["targetId"] for target in browser.call("Target.getTargets")["targetInfos"]
            if target.get("type") == "page"}


def _validate_image(data: bytes, fmt: str, figure: dict) -> None:
    if fmt == "png":
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Captured PNG has no valid signature/header")
        offset, compressed, header, ended = 8, [], None, False
        while offset < len(data):
            if offset + 12 > len(data):
                raise ValueError("Captured PNG has a truncated chunk")
            length = int.from_bytes(data[offset:offset + 4], "big")
            end = offset + length + 12
            if end > len(data):
                raise ValueError("Captured PNG has a truncated chunk")
            tag, body = data[offset + 4:offset + 8], data[offset + 8:end - 4]
            if zlib.crc32(tag + body) != int.from_bytes(data[end - 4:end], "big"):
                raise ValueError("Captured PNG has an invalid chunk CRC")
            if tag == b"IHDR":
                if header is not None or offset != 8 or len(body) != 13:
                    raise ValueError("Captured PNG has an invalid IHDR")
                header = body
            elif tag == b"IDAT":
                compressed.append(body)
            elif tag == b"IEND":
                if length != 0 or end != len(data):
                    raise ValueError("Captured PNG has an invalid IEND")
                ended = True
            offset = end
        if header is None or not ended or not compressed:
            raise ValueError("Captured PNG is incomplete")
        if int.from_bytes(header[:4], "big") != 400 or int.from_bytes(header[4:8], "big") != 300:
            raise ValueError("Captured PNG dimensions differ from the synthetic figure")
        if header[8] != 8 or header[9] not in (2, 6) or header[10:] != b"\0\0\0":
            raise ValueError("Captured PNG uses an unexpected pixel format")
        expected = (400 * (3 if header[9] == 2 else 4) + 1) * 300
        inflater = zlib.decompressobj()
        pixels = inflater.decompress(b"".join(compressed), expected + 1)
        if len(pixels) != expected or not inflater.eof or inflater.unused_data:
            raise ValueError("Captured PNG has incomplete or oversized pixel data")
    else:
        root = ET.fromstring(data)
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Captured SVG has no SVG root")
        text = "".join(root.itertext())
        if figure["layout"]["title"]["text"] not in text or figure["data"][0]["name"] not in text:
            raise ValueError("Captured SVG is missing its synthetic title or legend")


def _render_figures(browser: DiagnosticChrome, session: RenderSession, bundle: Path,
                    directory: Path, trial: dict) -> None:
    config = replace(PLOTLY, local_scripts=(lambda: bundle,))
    pid = browser._proc.pid
    baseline = _page_targets(browser)
    png_hashes: set[str] = set()
    trial["baseline_page_count"] = len(baseline)
    for index, figure in enumerate(_figures()):
        for fmt in ("png", "svg"):
            browser.stage = f"render.figure-{index}.{fmt}"
            started = time.monotonic()
            record = {"figure": index, "format": fmt, "ok": False}
            trial["renders"].append(record)
            try:
                path = directory / f"figure-{index}.{fmt}"
                data = export_draw(config, plotly_figure_content(figure), path, fmt, session=session)
                _validate_image(data, fmt, figure)
                if browser._proc is None or browser._proc.pid != pid:
                    raise RuntimeError("Render unexpectedly replaced the browser process")
                remaining = _page_targets(browser)
                if remaining != baseline:
                    raise RuntimeError("Render leaked or removed a page target")
                digest = hashlib.sha256(data).hexdigest()
                if fmt == "png":
                    png_hashes.add(digest)
                record.update({"ok": True, "bytes": len(data), "sha256": digest,
                               "artifact": str(path), "pid": pid, "page_count_after": len(remaining)})
            finally:
                record["elapsed_seconds"] = time.monotonic() - started
    if len(png_hashes) != 3:
        raise RuntimeError("The three distinct figures produced indistinguishable PNGs")


def _trial(executable: str, timeout: float, index: int, bundle: Path | None, evidence: Path | None) -> dict:
    browser = DiagnosticChrome(executable, timeout)
    session = _DiagnosticSession(browser, timeout) if bundle else None
    before = _counts()
    started = time.monotonic()
    trial = {"run": index, "ok": False, "failure": None, "renders": [],
             "resources_before": before, "render_elapsed_seconds": None}
    try:
        if session is None:
            browser.start()
        else:
            session.start()
        if not browser.product:
            raise RuntimeError("Browser.getVersion returned no CDP product")
        if session is not None:
            browser.stage = "render"
            rendering = time.monotonic()
            try:
                _render_figures(browser, session, bundle, evidence / f"run-{index:03d}", trial)
            finally:
                trial["render_elapsed_seconds"] = time.monotonic() - rendering
    except Exception as exc:
        browser.record_failure(exc)
    finally:
        browser.stage = "cleanup"
        try:
            (session or browser).close()
        except Exception as exc:
            browser.record_failure(exc, "cleanup")
        trial["cleanup"] = browser.cleanup()
        if session is not None:
            trial["cleanup"]["render_workdir_removed"] = None if session.workdir is None else not Path(session.workdir).exists()
        after = _counts()
        trial["resources_after"] = after
        trial["resource_delta"] = {key: None if before[key] is None or after[key] is None else after[key] - before[key]
                                   for key in before}
        trial.update({"cdp_product": browser.product, "cdp_protocol_version": browser.protocol_version,
                      "readiness_elapsed_seconds": browser.readiness_elapsed_seconds,
                      "spawn_elapsed_seconds": browser.spawn_elapsed_seconds,
                      "readiness_transport": dict(browser.readiness_transport),
                      "wait_observations": list(browser.wait_observations),
                      "close_elapsed_seconds": browser.close_elapsed_seconds,
                      "total_elapsed_seconds": time.monotonic() - started,
                      "stderr_tail": browser.stderr_tail})
    cleanup = trial["cleanup"]
    remaining = (any(value is False for key, value in cleanup.items() if key != "process")
                 or cleanup["process"]["state"] == "running"
                 or any(value is not None and value > 0 for value in trial["resource_delta"].values()))
    trial["cleanup_complete"] = not remaining
    trial["cleanup_failure"] = None
    if remaining:
        exc = RuntimeError("Browser cleanup left owned resources active or increased process resource counts")
        trial["cleanup_failure"] = _error(exc, "cleanup")
        browser.record_failure(exc, "cleanup")
    trial["failure"] = browser.failure
    trial["recovery"] = None
    if remaining and browser._process_ref is not None and browser._process_ref.poll() is None:
        # Preserve the normal cleanup evidence above. Do not leave a known,
        # owned browser running just because that cleanup failed. Untracked
        # descriptors are never guessed or closed by number.
        recovery_started = time.monotonic()
        recovery = {"failure": None}
        try:
            try:
                os.killpg(browser._process_ref.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            browser._process_ref.wait(timeout=2)
            Chrome.close(browser)
        except Exception as exc:
            recovery["failure"] = _error(exc, "recovery")
        recovery.update({"process_after": _process(browser._process_ref),
                         "resources_after": _counts(),
                         "elapsed_seconds": time.monotonic() - recovery_started})
        trial["recovery"] = recovery
    trial["total_elapsed_seconds"] = time.monotonic() - started
    trial["ok"] = browser.failure is None and not remaining
    return trial


def diagnose(chrome: str, *, runs: int = 5, timeout: float = 30.0,
             plotly_js: str | None = None, evidence_dir: str | None = None) -> dict:
    """Run independent trials and return JSON-compatible evidence, including errors."""
    report = {"schema_version": 1, "ok": False, "mode": "plotly" if plotly_js else "startup",
              "requested_runs": runs, "timeout_seconds": timeout,
              "runtime": {"python": platform.python_version(), "platform": sys.platform,
                          "machine": platform.machine(), "kernel_release": platform.release()},
              "created_at": datetime.now(timezone.utc).isoformat(),
              "chrome": {"requested_path": chrome, "executable_path": None, "resolved_path": None, "version": None},
              "plotly_js": None, "preflight_failure": None, "stopped_early_reason": None, "trials": []}
    stage = "arguments"
    try:
        if not isinstance(runs, int) or isinstance(runs, bool) or runs < 1:
            raise ValueError("runs must be a positive integer")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be finite and positive")
        if bool(plotly_js) != bool(evidence_dir):
            raise ValueError("--plotly-js and --evidence-dir must be provided together")
        stage = "resolve_browser"
        if not Path(chrome).is_absolute():
            raise ValueError("--chrome must be an absolute executable path; no PATH fallback is used")
        # Preserve the invocation path: wrappers can depend on argv[0] or the
        # symlink location. The canonical target is evidence, never substituted.
        executable = find_chrome(chrome)
        report["chrome"]["executable_path"] = executable
        report["chrome"]["resolved_path"] = str(Path(executable).resolve(strict=True))
        bundle, evidence = None, None
        if plotly_js:
            stage = "bundle"
            bundle = Path(plotly_js).resolve(strict=True)
            with bundle.open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
            if bundle.stat().st_size == 0:
                raise ValueError("Plotly.js bundle is empty")
            report["plotly_js"] = {"resolved_path": str(bundle), "sha256": digest, "bytes": bundle.stat().st_size}
            stage = "evidence_directory"
            evidence = Path(evidence_dir).resolve()
            evidence.mkdir(parents=True, exist_ok=True)
        stage = "version"
        report["chrome"]["version"] = _version(executable, timeout)
        for index in range(1, runs + 1):
            trial = _trial(executable, timeout, index, bundle, evidence)
            report["trials"].append(trial)
            if not trial["cleanup_complete"]:
                # Do not multiply observed leaks, and do not repair the baseline
                # silently: the normal cleanup result is the evidence we need.
                report["stopped_early_reason"] = "cleanup_left_resources"
                break
        report["ok"] = (report["chrome"]["version"]["failure"] is None
                        and len(report["trials"]) == runs
                        and all(trial["ok"] for trial in report["trials"]))
    except Exception as exc:
        report["preflight_failure"] = _error(exc, stage)
    report["unattempted_runs"] = runs - len(report["trials"]) if isinstance(runs, int) and runs > 0 else None
    report["passed_runs"] = sum(trial["ok"] for trial in report["trials"])
    report["failed_runs"] = len(report["trials"]) - report["passed_runs"]
    return report


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _positive_seconds(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return parsed


def diagnose_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=DIAGNOSE_CLI_DOC)
    parser.add_argument("--chrome", required=True, help="absolute executable path (required; no automatic selection)")
    parser.add_argument("--runs", type=_positive_int, default=5)
    parser.add_argument("--timeout", type=_positive_seconds, default=30.0,
                        help="seconds per startup/CDP stage, not a whole-trial deadline (default: 30)")
    parser.add_argument("--output", required=True, help="JSON output path, or - for stdout")
    parser.add_argument("--plotly-js", help="trusted local Plotly.js bundle; never downloaded")
    parser.add_argument("--evidence-dir", help="synthetic PNG/SVG outputs; requires --plotly-js")
    args = parser.parse_args(argv)
    report = diagnose(args.chrome, runs=args.runs, timeout=args.timeout,
                      plotly_js=args.plotly_js, evidence_dir=args.evidence_dir)
    body = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output == "-":
        sys.stdout.write(body)
    else:
        try:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(body, encoding="utf-8")
        except OSError as exc:
            print("Could not write diagnostic JSON: " + _safe_text(exc), file=sys.stderr)
            return 1
    if args.output != "-":
        products = sorted({trial["cdp_product"] for trial in report["trials"] if trial["cdp_product"]})
        elapsed = [trial["readiness_elapsed_seconds"] for trial in report["trials"]
                   if trial["readiness_elapsed_seconds"] is not None]
        readiness = f"{min(elapsed):.3f}..{max(elapsed):.3f}s" if elapsed else "not reached"
        failures = [trial["failure"]["stage"] for trial in report["trials"] if trial["failure"]]
        if any(trial["cleanup_failure"] for trial in report["trials"]):
            failures.append("cleanup")
        if report["preflight_failure"]:
            failures.append(report["preflight_failure"]["stage"])
        version = report["chrome"]["version"]
        if version and version["failure"]:
            failures.append("version")
        print("Browser diagnostic: " + (", ".join(products) or "CDP product unavailable")
              + f"; {report['passed_runs']} passed, {report['failed_runs']} failed"
              + f" of {report['requested_runs']} requested; readiness min/max {readiness}"
              + "; failed stages: " + (", ".join(sorted(set(failures))) or "none"))
    return 0 if report["ok"] else 1


# ==== startup_ci（旧 run_browser_startup_ci.py）

STARTUP_CI_DOC = """One-command runner for the real Chromium first-start regression.

Run inside a fresh CI job. Network isolation is established by the caller,
not by this wrapper, so normal and offline jobs stay independent.
"""


def startup_ci(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=STARTUP_CI_DOC)
    parser.add_argument("--output", type=Path, default=Path("build/startup-context"))
    args = parser.parse_args(argv)
    if not os.environ.get("CHROME"):
        parser.error("CHROME must identify the selected Chromium executable")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["DRAGOWING_REQUIRE_CHROME"] = "1"
    env["DRAGOWING_EXPORT_EVIDENCE_DIR"] = str(output / "export-evidence")
    env.setdefault("DRAGOWING_PINNED_PLOTLY_JS", str(Path("build/test-assets/plotly.min.js").resolve()))
    common = [sys.executable, "-m", "pytest", "-c", "pyproject.toml", "-q",
              "-p", "scripts.observe_dragowing_startup"]
    # The strict existing regression is the first full browser launch. Do not
    # retry it in the remainder, or run export tests after a failed gate.
    first = common + [
        f"--browser-startup-evidence={output / 'first-start.json'}",
        "dragowing/tests/test_render.py::test_stalled_dbus_does_not_block_browser_get_version",
        f"--junitxml={output / 'first-start.xml'}",
    ]
    result = subprocess.call(first, env=env)
    if result != 0:
        return result
    remaining = common + [
        f"--browser-startup-evidence={output / 'actual-tests.json'}",
        "dragowing/tests/test_chrome_pipe.py",
        "dragowing/tests/test_render.py",
        "dragowing/tests/test_export.py",
        "dragowing/tests/test_plotly_cdn.py",
        "--deselect=dragowing/tests/test_render.py::test_stalled_dbus_does_not_block_browser_get_version",
        f"--junitxml={output / 'actual-tests.xml'}",
    ]
    return subprocess.call(remaining, env=env)


# ==== render_fixtures（旧 render_static_fixtures.py）

RENDER_FIXTURES_DOC = """Draw the three synthetic diagnostic figures once and save them as the browser-free test fixtures.

    python scripts/dragowing_browser.py render_fixtures --chrome /path/to/chromium --plotly-js /path/to/plotly.min.js

The output (PNG and SVG per figure plus ``manifest.json``) goes to ``tests/fixtures/rendered_plotly``.
It is a saved observation, not a reference to reproduce byte for byte: the PNG bytes depend on the
Chromium build and the SVG on the Plotly.js version. ``tests/test_rendered_output_static.py`` only
compares them with the figure spec (``scripts/rendered_output_checks.py``), so regenerate them when
the synthetic figures change or the checks need a newer Plotly, and review the manifest diff.
"""

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = ROOT / "tests" / "fixtures" / "rendered_plotly"


def render_fixtures(argv=None) -> int:
    parser = argparse.ArgumentParser(description=RENDER_FIXTURES_DOC.splitlines()[0])
    parser.add_argument("--chrome", required=True, help="absolute path of Chrome or Chromium")
    parser.add_argument("--plotly-js", required=True, type=Path, help="local plotly.min.js to draw with")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    bundle = args.plotly_js.resolve()
    version = re.search(r"plotly\.js v([0-9][0-9A-Za-z.\-]*)", bundle.read_text(encoding="utf-8")[:2000])
    browser = subprocess.run([args.chrome, "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
    figures = _figures()
    config = replace(PLOTLY, local_scripts=(lambda: bundle,))
    args.out.mkdir(parents=True, exist_ok=True)
    files = {}
    with RenderSession(chrome=args.chrome) as session:
        for index, figure in enumerate(figures):
            for fmt, check in (("png", check_png), ("svg", check_svg)):
                name = "figure-%d.%s" % (index, fmt)
                data = export_draw(config, plotly_figure_content(figure), args.out / name, fmt, session=session)
                check(data, figure)  # never save output the checks would reject
                files[name] = hashlib.sha256(data).hexdigest()
    manifest = {
        "schema": "aoi-rendered-plotly-fixtures/1",
        "figures_sha256": figures_digest(figures),
        "plotly_js": version.group(1) if version else None,
        "browser": browser,
        "files": files,
        "regenerate": "python scripts/dragowing_browser.py render_fixtures --chrome <chromium> --plotly-js <plotly.min.js>",
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote %d files to %s" % (len(files) + 1, args.out))
    return 0


# ==== 入口
COMMANDS = {
    "diagnose": diagnose_cli,
    "startup_ci": startup_ci,
    "render_fixtures": render_fixtures,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dragowing_browser.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"dragowing_browser.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
