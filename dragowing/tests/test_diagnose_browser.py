"""Diagnostic evidence with real pipes and a deterministic, local CDP peer."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from dragowing import diagnose_browser as diagnostic

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX debugging pipes")


@pytest.fixture
def peer(tmp_path):
    def create(mode="ok"):
        path = tmp_path / ("fake-browser-" + mode)
        path.write_text("#!" + sys.executable + "\nMODE = " + repr(mode) + r'''
import base64, json, os, re, struct, sys, time, zlib
from pathlib import Path
from urllib.parse import unquote, urlparse
if "--version" in sys.argv:
    if MODE == "version_timeout":
        time.sleep(60)
    if MODE == "version_failure":
        print("version probe failed", file=sys.stderr, flush=True)
        sys.exit(4)
    print(Path(sys.argv[0]).name if MODE == "identity" else "FakeChrome 123.4")
    sys.exit(0)
if MODE == "early_exit":
    print("synthetic startup exit", file=sys.stderr, flush=True)
    sys.exit(9)
if MODE == "timeout":
    print("x" * 10000 + " bounded-stderr-marker\nAPI_KEY=do-not-leak --token=secret-value", file=sys.stderr, flush=True)
buf = b""
pages = {"initial"}
page_id, figure = 0, 0

def send(obj):
    data = json.dumps(obj).encode() + b"\0"
    while data:
        data = data[os.write(4, data):]

def png(index):
    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body))
    raw = (b"\0" + bytes([20 + index * 60, 90, 180]) * 400) * 300
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 400, 300, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

while True:
    data = os.read(3, 65536)
    if not data:
        break
    buf += data
    while b"\0" in buf:
        raw, buf = buf.split(b"\0", 1)
        msg = json.loads(raw)
        method, params = msg["method"], msg.get("params", {})
        result = {}
        if method == "Browser.close":
            sys.exit(0)
        if method == "Browser.getVersion":
            if MODE == "timeout":
                continue
            if MODE == "malformed":
                os.write(4, b"not-json\0")
                continue
            result = {} if MODE == "missing_product" else {"product": "FakeChrome/123.4", "protocolVersion": "1.3"}
        if method == "Target.setDiscoverTargets" and MODE == "discovery_failure":
            send({"id": msg["id"], "error": {"message": "synthetic discovery failure"}})
            continue
        if method == "Target.getTargets":
            result = {"targetInfos": [{"type": "page", "targetId": p} for p in sorted(pages)]}
        if method == "Target.createTarget":
            page_id += 1
            target = "page-" + str(page_id)
            pages.add(target)
            result = {"targetId": target}
        if method == "Target.attachToTarget":
            result = {"sessionId": "session"}
        if method == "Page.navigate":
            text = Path(unquote(urlparse(params["url"]).path)).read_text()
            figure = int(re.search(r"diagnostic-figure-(\d+)", text).group(1))
            send({"method": "Page.loadEventFired", "sessionId": "session"})
        if method == "Runtime.evaluate":
            expr = params["expression"]
            if "getBoundingClientRect" in expr:
                value = {"x": 0, "y": 0, "width": 400, "height": 300, "scale": 1}
            elif "Plotly.toImage" in expr:
                value = ('<svg xmlns="http://www.w3.org/2000/svg"><text>diagnostic-figure-%s</text>'
                         '<text>diagnostic-series-%s</text></svg>') % (figure, figure)
            elif MODE == "ready_timeout":
                continue
            else:
                value = True
            result = {"result": {"value": value}}
        if method == "Page.captureScreenshot":
            if MODE == "capture_failure":
                send({"id": msg["id"], "error": {"message": "synthetic capture failure"}})
                continue
            image = b"invalid" if MODE == "invalid_png" else png(figure)
            result = {"data": base64.b64encode(image).decode()}
        if method == "Target.closeTarget":
            pages.discard(params["targetId"])
            send({"method": "Target.targetDestroyed", "params": {"targetId": params["targetId"]}})
            result = {"success": True}
        send({"id": msg["id"], "result": result})
''', encoding="utf-8")
        path.chmod(0o755)
        return str(path)
    return create


@pytest.fixture
def bundle(tmp_path):
    path = tmp_path / "plotly.min.js"
    # The fake peer never executes JS; no downloaded bundle or browser is used.
    path.write_text("/* local synthetic test bundle */", encoding="utf-8")
    return str(path)


def assert_clean(trial):
    assert trial["cleanup"]["profile_removed"] is True
    assert trial["cleanup"]["reader_stopped"] is True
    assert trial["cleanup"]["process"]["state"] == "exited"
    assert trial["cleanup"]["pipe_descriptors_released"] is True
    assert trial["cleanup"]["stderr_file_closed"] is True
    assert trial["resource_delta"]["threads"] == 0
    assert trial["resource_delta"]["file_descriptors"] in (None, 0)
    assert trial["close_elapsed_seconds"] >= 0


def test_repeated_startup_uses_explicit_resolved_binary(peer, monkeypatch, tmp_path):
    executable = peer()
    link = tmp_path / "explicit-link"
    link.symlink_to(executable)
    monkeypatch.setenv("CHROME", "/unrelated/should-not-be-selected")
    monkeypatch.setenv("CHROMIUM", "/unrelated/other-browser")
    report = diagnostic.diagnose(str(link), runs=3, timeout=2)
    assert report["ok"]
    assert report["chrome"]["resolved_path"] == executable
    assert report["chrome"]["executable_path"] == str(link)
    assert report["chrome"]["version"]["text"] == "FakeChrome 123.4"
    assert report["mode"] == "startup"
    assert report["passed_runs"] == 3 and report["failed_runs"] == 0
    assert report["runtime"]["python"]
    pids = set()
    for trial in report["trials"]:
        assert trial["cdp_product"] == "FakeChrome/123.4"
        assert trial["cdp_protocol_version"] == "1.3"
        assert trial["readiness_elapsed_seconds"] > 0
        assert trial["renders"] == [] and trial["render_elapsed_seconds"] is None
        pids.add(trial["cleanup"]["process"]["pid"])
        assert_clean(trial)
    assert len(pids) == 3
    assert "should-not-be-selected" not in json.dumps(report)


@pytest.mark.parametrize("mode, error", [("timeout", "TimeoutError"), ("early_exit", "RuntimeError"),
                                          ("malformed", "RuntimeError"), ("missing_product", "RuntimeError")])
def test_startup_failure_keeps_precleanup_evidence_and_repeats(peer, mode, error):
    report = diagnostic.diagnose(peer(mode), runs=2, timeout=0.25)
    assert not report["ok"] and report["failed_runs"] == 2
    for trial in report["trials"]:
        failure = trial["failure"]
        assert failure["type"] == error and failure["stage"] == "readiness"
        assert failure["last_cdp_method"] == "Browser.getVersion"
        assert failure["process"]["pid"] is not None
        assert_clean(trial)
        if mode == "timeout":
            assert failure["process"]["state"] == "running"
            assert failure["process"]["returncode"] is None
            assert failure["reader_alive"]
            assert "bounded-stderr-marker" in failure["stderr_tail"]
            assert len(failure["stderr_tail"]) <= diagnostic._TAIL_BYTES
            assert "do-not-leak" not in json.dumps(report)
            assert "secret-value" not in json.dumps(report)
        elif mode == "early_exit":
            assert "synthetic startup exit" in failure["stderr_tail"]
            assert trial["cleanup"]["process"]["returncode"] == 9


def test_spawn_failure_preserves_type_and_cleans_profile(peer, monkeypatch):
    def fail(self, exe):
        raise OSError("synthetic spawn failure")
    monkeypatch.setattr(diagnostic.Chrome, "_spawn", fail)
    report = diagnostic.diagnose(peer(), runs=1, timeout=1)
    trial = report["trials"][0]
    assert trial["failure"]["stage"] == "spawn"
    assert trial["failure"]["type"] == "OSError"
    assert trial["failure"]["process"]["state"] == "not_started"
    assert trial["cleanup"]["profile_removed"] is True
    assert trial["cleanup"]["reader_stopped"] is None


@pytest.mark.parametrize("mode", ["version_timeout", "version_failure"])
def test_version_probe_failure_is_not_confused_with_readiness(peer, mode):
    report = diagnostic.diagnose(peer(mode), runs=1, timeout=0.25)
    assert not report["ok"]
    assert report["chrome"]["version"]["failure"]["stage"] == "version"
    assert report["trials"][0]["ok"]
    assert_clean(report["trials"][0])


def test_missing_browser_and_no_path_fallback(tmp_path):
    report = diagnostic.diagnose(str(tmp_path / "missing"), runs=2)
    assert not report["ok"] and not report["trials"]
    assert report["preflight_failure"]["stage"] == "resolve_browser"
    assert diagnostic.diagnose("google-chrome")["preflight_failure"]["type"] == "ValueError"
    not_executable = tmp_path / "not-executable"
    not_executable.write_text("nothing")
    assert diagnostic.diagnose(str(not_executable))["preflight_failure"]["stage"] == "resolve_browser"


def test_missing_empty_or_unpaired_bundle_fails_before_launch(peer, tmp_path, monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("preflight failure must not launch the version probe")
    monkeypatch.setattr(diagnostic, "_version", unexpected)
    executable = peer()
    report = diagnostic.diagnose(executable, plotly_js=str(tmp_path / "missing.js"), evidence_dir=str(tmp_path / "images"))
    assert report["preflight_failure"]["stage"] == "bundle" and not report["trials"]
    empty = tmp_path / "empty.js"
    empty.touch()
    report = diagnostic.diagnose(executable, plotly_js=str(empty), evidence_dir=str(tmp_path / "images"))
    assert report["preflight_failure"]["type"] == "ValueError"
    for kwargs in ({"plotly_js": str(empty)}, {"evidence_dir": str(tmp_path / "images")}):
        assert diagnostic.diagnose(executable, **kwargs)["preflight_failure"]["stage"] == "arguments"


def test_six_exports_reuse_browser_and_only_local_bundle(peer, bundle, tmp_path, monkeypatch):
    def no_fetch(*args, **kwargs):
        pytest.fail("diagnostics must never fetch a bundle")
    monkeypatch.setattr("dragowing.export.fetch_plotly_js", no_fetch)
    report = diagnostic.diagnose(peer(), runs=2, timeout=2, plotly_js=bundle, evidence_dir=str(tmp_path / "images"))
    assert report["ok"] and report["mode"] == "plotly"
    assert report["plotly_js"]["bytes"] > 0 and len(report["plotly_js"]["sha256"]) == 64
    for trial in report["trials"]:
        assert_clean(trial)
        assert trial["cleanup"]["render_workdir_removed"]
        assert trial["render_elapsed_seconds"] > 0
        assert len(trial["renders"]) == 6
        pid = trial["cleanup"]["process"]["pid"]
        assert {render["pid"] for render in trial["renders"]} == {pid}
        assert all(render["ok"] and render["page_count_after"] == trial["baseline_page_count"] for render in trial["renders"])
        assert all(Path(render["artifact"]).is_file() for render in trial["renders"])


@pytest.mark.parametrize("mode, stage, method", [
    ("discovery_failure", "session_setup", "Target.setDiscoverTargets"),
    ("capture_failure", "render.figure-0.png", "Page.captureScreenshot"),
    ("ready_timeout", "render.figure-0.png", "Runtime.evaluate"),
    ("invalid_png", "render.figure-0.png", "Target.closeTarget"),
])
def test_render_failure_has_stage_and_cleans_resources(peer, bundle, tmp_path, mode, stage, method):
    report = diagnostic.diagnose(peer(mode), runs=1, timeout=0.25,
                                 plotly_js=bundle, evidence_dir=str(tmp_path / "images"))
    assert not report["ok"]
    trial = report["trials"][0]
    assert trial["failure"]["stage"] == stage
    assert trial["failure"]["last_cdp_method"] == method
    assert trial["cdp_product"] == "FakeChrome/123.4"
    assert_clean(trial)
    assert trial["cleanup"]["render_workdir_removed"]


def test_tail_reads_only_bounded_bytes(tmp_path, monkeypatch):
    import builtins
    path = tmp_path / "stderr"
    path.write_bytes(b"x" * 100000 + b"\nlast-stderr-marker")
    reads = []
    real_open = builtins.open
    class BoundedRead:
        def __init__(self):
            self.handle = real_open(path, "rb")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            self.handle.close()
        def seek(self, *args):
            return self.handle.seek(*args)
        def tell(self):
            return self.handle.tell()
        def read(self, length):
            reads.append(length)
            return self.handle.read(length)
    monkeypatch.setattr(diagnostic, "open", lambda *args, **kwargs: BoundedRead(), raising=False)
    assert diagnostic._tail(path).endswith("last-stderr-marker")
    assert reads == [diagnostic._TAIL_BYTES]


def test_cli_writes_json_and_returns_failure_without_browser(tmp_path):
    output = tmp_path / "report.json"
    assert diagnostic.main(["--chrome", str(tmp_path / "missing"), "--output", str(output)]) == 1
    assert json.loads(output.read_text())["preflight_failure"]["stage"] == "resolve_browser"


def test_cli_success_and_stdout(peer, capsys):
    assert diagnostic.main(["--chrome", peer(), "--runs", "1", "--timeout", "2", "--output", "-"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"]


@pytest.mark.parametrize("option, value", [("--runs", "0"), ("--runs", "-1"), ("--timeout", "0"),
                                           ("--timeout", "-1"), ("--timeout", "nan"), ("--timeout", "inf")])
def test_cli_rejects_invalid_limits_without_launch(option, value):
    with pytest.raises(SystemExit) as exc:
        diagnostic.main(["--chrome", "/not-used", "--output", "-", option, value])
    assert exc.value.code == 2


def test_cli_help_runs_without_site_packages():
    result = subprocess.run([sys.executable, "-S", "-m", "dragowing.diagnose_browser", "--help"],
                            cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "--plotly-js" in result.stdout


def test_symlink_invocation_is_not_replaced_with_realpath(peer, tmp_path):
    target = peer("identity")
    link = tmp_path / "keep-this-wrapper-name"
    link.symlink_to(target)
    report = diagnostic.diagnose(str(link), runs=1, timeout=2)
    assert report["ok"]
    assert report["chrome"]["version"]["text"] == link.name
    assert report["chrome"]["executable_path"] == str(link)
    assert report["chrome"]["resolved_path"] == target


def test_summary_on_stdout_with_file_output(peer, tmp_path, capsys):
    assert diagnostic.main(["--chrome", peer(), "--runs", "1", "--timeout", "2",
                            "--output", str(tmp_path / "evidence.json")]) == 0
    summary = capsys.readouterr().out
    assert "FakeChrome/123.4" in summary and "1 passed, 0 failed" in summary
    assert "readiness min/max" in summary and "failed stages: none" in summary


def test_timeout_never_calls_unbounded_parent_diagnostic(peer, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("production full-file diagnostic must not be called by the validation subclass")
    monkeypatch.setattr(diagnostic.Chrome, "_diagnostic", forbidden)
    report = diagnostic.diagnose(peer("timeout"), runs=1, timeout=0.25)
    assert report["trials"][0]["failure"]["type"] == "TimeoutError"
    assert "bounded-stderr-marker" in report["trials"][0]["failure"]["stderr_tail"]


def test_cleanup_failure_stops_trials_instead_of_multiplying_leaks(peer, monkeypatch):
    browsers = []
    def fail(self):
        browsers.append(self)
        raise OSError("synthetic cleanup failure")
    monkeypatch.setattr(diagnostic.DiagnosticChrome, "close", fail)
    try:
        report = diagnostic.diagnose(peer(), runs=3, timeout=2)
        assert not report["ok"]
        assert report["stopped_early_reason"] == "cleanup_left_resources"
        assert report["unattempted_runs"] == 2
        assert len(report["trials"]) == 1
        trial = report["trials"][0]
        assert trial["failure"]["stage"] == "cleanup"
        assert trial["cleanup_failure"]["stage"] == "cleanup"
        assert not trial["cleanup_complete"]
        assert trial["cleanup"]["process"]["state"] == "running"
        assert trial["recovery"]["process_after"]["state"] == "exited"
        assert trial["recovery"]["failure"] is None
    finally:
        # The fake failure deliberately bypassed normal cleanup. Restore it for
        # this test's owned process only; the diagnostic does not hide the leak.
        for browser in browsers:
            diagnostic.Chrome.close(browser)
