"""DRAgoWing のブラウザーの管の検査（POSIX の管を使う。旧 3 本をまとめた。節の頭に旧ファイルの名前を書いた）。
"""

import errno
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from dragowing.chrome_pipe import Chrome
from scripts import dragowing_browser as diagnostic


# ==== diagnostics（旧 test_dragowing_browser_diagnostics.py）
# Diagnostic evidence with real pipes and a deterministic, local CDP peer.


pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX pipe transport")


@pytest.fixture
def diagnostics_peer(tmp_path):
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


def test_repeated_startup_uses_explicit_resolved_binary(diagnostics_peer, monkeypatch, tmp_path):
    executable = diagnostics_peer()
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
def test_startup_failure_keeps_precleanup_evidence_and_repeats(diagnostics_peer, mode, error):
    report = diagnostic.diagnose(diagnostics_peer(mode), runs=2, timeout=0.25)
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


def test_spawn_failure_preserves_type_and_cleans_profile(diagnostics_peer, monkeypatch):
    def fail(self, exe):
        raise OSError("synthetic spawn failure")
    monkeypatch.setattr(diagnostic.Chrome, "_spawn", fail)
    report = diagnostic.diagnose(diagnostics_peer(), runs=1, timeout=1)
    trial = report["trials"][0]
    assert trial["failure"]["stage"] == "spawn"
    assert trial["failure"]["type"] == "OSError"
    assert trial["failure"]["process"]["state"] == "not_started"
    assert trial["cleanup"]["profile_removed"] is True
    assert trial["cleanup"]["reader_stopped"] is None


@pytest.mark.parametrize("mode", ["version_timeout", "version_failure"])
def test_version_probe_failure_is_not_confused_with_readiness(diagnostics_peer, mode):
    report = diagnostic.diagnose(diagnostics_peer(mode), runs=1, timeout=0.25)
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


def test_missing_empty_or_unpaired_bundle_fails_before_launch(diagnostics_peer, tmp_path, monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("preflight failure must not launch the version probe")
    monkeypatch.setattr(diagnostic, "_version", unexpected)
    executable = diagnostics_peer()
    report = diagnostic.diagnose(executable, plotly_js=str(tmp_path / "missing.js"), evidence_dir=str(tmp_path / "images"))
    assert report["preflight_failure"]["stage"] == "bundle" and not report["trials"]
    empty = tmp_path / "empty.js"
    empty.touch()
    report = diagnostic.diagnose(executable, plotly_js=str(empty), evidence_dir=str(tmp_path / "images"))
    assert report["preflight_failure"]["type"] == "ValueError"
    for kwargs in ({"plotly_js": str(empty)}, {"evidence_dir": str(tmp_path / "images")}):
        assert diagnostic.diagnose(executable, **kwargs)["preflight_failure"]["stage"] == "arguments"


def test_six_exports_reuse_browser_and_only_local_bundle(diagnostics_peer, bundle, tmp_path, monkeypatch):
    def no_fetch(*args, **kwargs):
        pytest.fail("diagnostics must never fetch a bundle")
    monkeypatch.setattr("dragowing.export.fetch_plotly_js", no_fetch)
    report = diagnostic.diagnose(diagnostics_peer(), runs=2, timeout=2, plotly_js=bundle, evidence_dir=str(tmp_path / "images"))
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
def test_render_failure_has_stage_and_cleans_resources(diagnostics_peer, bundle, tmp_path, mode, stage, method):
    report = diagnostic.diagnose(diagnostics_peer(mode), runs=1, timeout=0.25,
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
    assert diagnostic.diagnose_cli(["--chrome", str(tmp_path / "missing"), "--output", str(output)]) == 1
    assert json.loads(output.read_text())["preflight_failure"]["stage"] == "resolve_browser"


def test_cli_success_and_stdout(diagnostics_peer, capsys):
    assert diagnostic.diagnose_cli(["--chrome", diagnostics_peer(), "--runs", "1", "--timeout", "2", "--output", "-"]) == 0
    assert json.loads(capsys.readouterr().out)["ok"]


@pytest.mark.parametrize("option, value", [("--runs", "0"), ("--runs", "-1"), ("--timeout", "0"),
                                           ("--timeout", "-1"), ("--timeout", "nan"), ("--timeout", "inf")])
def test_cli_rejects_invalid_limits_without_launch(option, value):
    with pytest.raises(SystemExit) as exc:
        diagnostic.diagnose_cli(["--chrome", "/not-used", "--output", "-", option, value])
    assert exc.value.code == 2


def test_cli_help_runs_without_site_packages_from_other_directory(tmp_path):
    result = subprocess.run([sys.executable, "-S", str(Path(diagnostic.__file__).resolve()), "diagnose", "--help"],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "--plotly-js" in result.stdout


def test_symlink_invocation_is_not_replaced_with_realpath(diagnostics_peer, tmp_path):
    target = diagnostics_peer("identity")
    link = tmp_path / "keep-this-wrapper-name"
    link.symlink_to(target)
    report = diagnostic.diagnose(str(link), runs=1, timeout=2)
    assert report["ok"]
    assert report["chrome"]["version"]["text"] == link.name
    assert report["chrome"]["executable_path"] == str(link)
    assert report["chrome"]["resolved_path"] == target


def test_summary_on_stdout_with_file_output(diagnostics_peer, tmp_path, capsys):
    assert diagnostic.diagnose_cli(["--chrome", diagnostics_peer(), "--runs", "1", "--timeout", "2",
                            "--output", str(tmp_path / "evidence.json")]) == 0
    summary = capsys.readouterr().out
    assert "FakeChrome/123.4" in summary and "1 passed, 0 failed" in summary
    assert "readiness min/max" in summary and "failed stages: none" in summary


def test_timeout_never_calls_unbounded_parent_diagnostic(diagnostics_peer, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("production full-file diagnostic must not be called by the validation subclass")
    monkeypatch.setattr(diagnostic.Chrome, "_diagnostic", forbidden)
    report = diagnostic.diagnose(diagnostics_peer("timeout"), runs=1, timeout=0.25)
    assert report["trials"][0]["failure"]["type"] == "TimeoutError"
    assert "bounded-stderr-marker" in report["trials"][0]["failure"]["stderr_tail"]


def test_cleanup_failure_stops_trials_instead_of_multiplying_leaks(diagnostics_peer, monkeypatch):
    browsers = []
    def fail(self):
        browsers.append(self)
        raise OSError("synthetic cleanup failure")
    monkeypatch.setattr(diagnostic.DiagnosticChrome, "close", fail)
    try:
        report = diagnostic.diagnose(diagnostics_peer(), runs=3, timeout=2)
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


def test_first_readiness_is_not_overwritten_by_later_version_calls(diagnostics_peer):
    browser = diagnostic.DiagnosticChrome(diagnostics_peer(), 2)
    try:
        browser.start()
        elapsed = browser.readiness_elapsed_seconds
        transport = dict(browser.readiness_transport)
        browser.call("Browser.getVersion")
        assert browser.readiness_elapsed_seconds == elapsed
        assert browser.readiness_transport == transport
        assert transport["phase"] == "response_received"
        assert transport["received_messages"] == 1
    finally:
        browser.close()


def test_readiness_timeout_retains_send_vs_receive_stage(diagnostics_peer):
    report = diagnostic.diagnose(diagnostics_peer("timeout"), runs=1, timeout=0.2)
    trial = report["trials"][0]
    assert trial["failure"]["readiness_transport"] == trial["readiness_transport"]
    assert trial["readiness_transport"]["phase"] == "waiting_reply"
    assert trial["readiness_transport"]["send_elapsed_seconds"] < 0.2
    assert trial["readiness_transport"]["received_messages"] == 0


def _run_observed_pytest(tmp_path, source, *, enabled=True):
    root = Path(__file__).resolve().parents[1]
    testfile = tmp_path / "test_observed.py"
    testfile.write_text(source, encoding="utf-8")
    output = tmp_path / "actual-tests.json"
    args = [sys.executable, "-m", "pytest", "-c", str(root / "pyproject.toml"),
            "-q", "-p", "scripts.observe_dragowing_startup", str(testfile)]
    if enabled:
        args += ["--browser-startup-evidence", str(output)]
    result = subprocess.run(args, cwd=root, capture_output=True, text=True,
                            env={**os.environ, "PYTHONPATH": str(root)}, timeout=30)
    return result, json.loads(output.read_text()) if output.exists() else None


def test_pytest_observer_is_inert_without_explicit_output(tmp_path):
    result, report = _run_observed_pytest(tmp_path, '''
from dragowing import chrome_pipe, render
import pytest
@pytest.fixture
def chrome_executable():
    return "/not-executed"
def test_unmodified(chrome_executable):
    assert render.Chrome is chrome_pipe.Chrome
''', enabled=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert report is None


def test_pytest_observer_tracks_actual_launches_and_expected_failures(diagnostics_peer, tmp_path):
    executable, timeout_executable = diagnostics_peer(), diagnostics_peer("timeout")
    result, report = _run_observed_pytest(tmp_path, f'''
from dragowing import chrome_pipe, render
import pytest
@pytest.fixture
def chrome_executable():
    return {executable!r}
def test_first_and_next(chrome_executable):
    for _ in range(2):
        with render.RenderSession(chrome=chrome_executable, timeouts=render.Timeouts(launch=2)) as session:
            elapsed = session.browser.readiness_elapsed_seconds
            session.start()
            session.browser.start()
            session.browser.call("Browser.getVersion")
            assert session.browser.readiness_elapsed_seconds == elapsed
def test_expected_failure(chrome_executable):
    with pytest.raises(TimeoutError):
        with render.RenderSession(chrome={timeout_executable!r}, timeouts=render.Timeouts(launch=0.2)):
            pass
def test_fake_only_is_not_patched():
    assert render.Chrome is chrome_pipe.Chrome
''')
    assert result.returncode == 0, result.stdout + result.stderr
    assert report["launch_count"] == 3
    assert report["pytest_exitstatus"] == 0
    assert len(report["tests"]) == 2
    records = [b for test in report["tests"] for b in test["browsers"]]
    assert [b["launch_ordinal"] for b in records] == [1, 2, 3]
    assert [b["position"] for b in records] == ["first_in_pytest", "subsequent_in_pytest", "subsequent_in_pytest"]
    assert [b["timeout_seconds"] for b in records] == [2, 2, 0.2]
    assert all(b["cleanup"]["profile_removed"] for b in records)
    assert all(0 <= b["spawn_elapsed_seconds"] < b["readiness_elapsed_seconds"] for b in records)
    assert records[2]["failure"]["stage"] == "readiness"
    assert records[2]["readiness_transport"]["phase"] == "waiting_reply"
    assert [[s["phase"] for s in b["wait_observations"]] for b in records] == [
        ["request_sent", "response_received"], ["request_sent", "response_received"],
        ["request_sent", "readiness_failure"],
    ]
    assert report["tests"][1]["pytest_outcomes"] == {"setup": "passed", "call": "passed", "teardown": "passed"}
    assert "do-not-leak" not in json.dumps(report)
    assert set(report["runtime"]) == {"python", "platform", "machine", "kernel_release", "uid", "euid",
                                       "network_namespace_inode", "network_interface_count", "loopback_present"}


def test_pytest_observer_preserves_failed_test_and_skipped_setup(diagnostics_peer, tmp_path):
    result, report = _run_observed_pytest(tmp_path, f'''
from dragowing import chrome_pipe, render
import pytest
@pytest.fixture
def chrome_executable(request):
    if request.node.name == "test_skipped":
        pytest.skip("synthetic fixture unavailable")
    return {diagnostics_peer("timeout")!r}
def test_failed(chrome_executable):
    with render.RenderSession(chrome=chrome_executable, timeouts=render.Timeouts(launch=0.2)):
        pass
def test_skipped(chrome_executable):
    assert False
def test_restored():
    assert render.Chrome is chrome_pipe.Chrome
''')
    assert result.returncode == 1, result.stdout + result.stderr
    assert report["pytest_exitstatus"] == 1
    assert report["launch_count"] == 1
    assert report["tests"][0]["pytest_outcomes"]["call"] == "failed"
    assert report["tests"][0]["browsers"][0]["failure"]["stage"] == "readiness"
    assert report["tests"][1]["pytest_outcomes"]["setup"] == "skipped"
    assert report["tests"][1]["browsers"] == []


def test_observer_preserves_restarts_of_one_closed_instance(diagnostics_peer, tmp_path):
    executable, second_executable = diagnostics_peer(), diagnostics_peer("identity")
    result, report = _run_observed_pytest(tmp_path, f'''
from dragowing import render
import pytest
@pytest.fixture
def chrome_executable():
    return {executable!r}
def test_restart(chrome_executable):
    session = render.RenderSession(chrome=chrome_executable, timeouts=render.Timeouts(launch=2))
    for executable, timeout in [({executable!r}, 2), ({second_executable!r}, 3)]:
        session.browser.chrome = executable
        session.timeouts = render.Timeouts(launch=timeout)
        with session:
            assert session.browser.product
''')
    assert result.returncode == 0, result.stdout + result.stderr
    records = report["tests"][0]["browsers"]
    assert report["launch_count"] == 2
    assert [b["launch_ordinal"] for b in records] == [1, 2]
    assert [b["executable_path"] for b in records] == [executable, second_executable]
    assert [b["timeout_seconds"] for b in records] == [2, 3]
    assert records[0]["cleanup"]["process"]["pid"] != records[1]["cleanup"]["process"]["pid"]
    assert all(b["readiness_transport"]["received_messages"] == 1 for b in records)
    assert all(b["readiness_elapsed_seconds"] > 0 for b in records)
    assert all(b["failure"] is None for b in records)


def test_startup_wait_observations_do_not_send_extra_cdp_requests(diagnostics_peer, monkeypatch):
    sent = []
    original = diagnostic.Chrome._send

    def observe_send(self, method, *args, **kwargs):
        sent.append(method)
        return original(self, method, *args, **kwargs)

    monkeypatch.setattr(diagnostic.Chrome, "_send", observe_send)
    browser = diagnostic.DiagnosticChrome(diagnostics_peer(), 2)
    try:
        browser.start()
        assert sent == ["Browser.getVersion"]
        snapshots = browser.wait_observations
        assert [s["phase"] for s in snapshots] == ["request_sent", "response_received"]
        assert all(s["pid"] == browser._proc.pid for s in snapshots)
        assert all(s["alive"] is True for s in snapshots)
        assert 0 <= snapshots[0]["elapsed_seconds"] <= snapshots[1]["elapsed_seconds"]
        assert all(s["observed_at"] for s in snapshots)
        assert all(s["sample_duration_seconds"] >= 0 for s in snapshots)
        before = json.loads(json.dumps(snapshots))
        browser.start()
        browser.call("Browser.getVersion")
        assert browser.wait_observations == before
        assert sent == ["Browser.getVersion", "Browser.getVersion"]
    finally:
        browser.close()
    assert sent == ["Browser.getVersion", "Browser.getVersion", "Browser.close"]


def test_startup_wait_failure_is_captured_before_cleanup_without_retry(diagnostics_peer):
    report = diagnostic.diagnose(diagnostics_peer("timeout"), runs=1, timeout=0.2)
    assert report["failed_runs"] == 1
    trial = report["trials"][0]
    snapshots = trial["wait_observations"]
    assert [s["phase"] for s in snapshots] == ["request_sent", "readiness_failure"]
    assert all(s["alive"] is True for s in snapshots)
    assert snapshots[-1]["elapsed_seconds"] >= 0.2
    assert trial["failure"]["stage"] == "readiness"
    assert trial["cleanup"]["process"]["state"] == "exited"
    assert trial["cleanup"]["process"]["pid"] == snapshots[-1]["pid"]
    assert trial["cleanup"]["pipe_descriptors_released"] is True
    assert "do-not-leak" not in json.dumps(snapshots)


def test_startup_wait_observer_keeps_existing_deadline_and_reports_its_cost(monkeypatch):
    clock = [0.0]
    deadlines = []
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])

    def send(self, method, params=None, session=None, *, deadline=None):
        deadlines.append(("send", deadline))
        return 1

    def recv(self, deadline):
        deadlines.append(("recv", deadline))
        return {"id": 1, "result": {"product": "FakeChrome/123.4"}}

    def snapshot(*args):
        clock[0] += 3
        return {}

    monkeypatch.setattr(diagnostic.Chrome, "_send", send)
    monkeypatch.setattr(diagnostic.Chrome, "_recv", recv)
    monkeypatch.setattr(diagnostic, "_startup_wait_snapshot", snapshot)
    browser = diagnostic.DiagnosticChrome("unused", 8)
    browser._started_at = 0
    browser.call("Browser.getVersion")
    assert deadlines == [("send", 8), ("recv", 8)]
    assert browser.timeout == 8
    assert browser.readiness_elapsed_seconds == 3  # excludes terminal snapshot cost
    assert [s["sample_duration_seconds"] for s in browser.wait_observations] == [3, 3]


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux procfs evidence")
def test_startup_wait_snapshot_matches_only_owned_cdp_pipes(diagnostics_peer):
    browser = diagnostic.DiagnosticChrome(diagnostics_peer(), 2)
    try:
        browser.start()
        snapshot = diagnostic._startup_wait_snapshot(browser._proc, browser._w, browser._r)
        assert snapshot["alive"] is True
        assert snapshot["state"] in {"R", "S", "D", "Z", "T", "t", "I"}
        for direction in ("request", "response"):
            pipe = snapshot["pipes"][direction]
            assert pipe["matches"] is True
            assert pipe["parent_inode"] == pipe["child_inode"]
            assert pipe["queued_bytes"] == 0
        for field in ("minor_faults", "major_faults", "user_ticks", "system_ticks"):
            assert isinstance(snapshot[field], int) and snapshot[field] >= 0
    finally:
        browser.close()


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux FIONREAD evidence")
def test_startup_wait_queued_byte_observation_does_not_consume_pipe_data(diagnostics_peer, tmp_path):
    browser = diagnostic.DiagnosticChrome(diagnostics_peer(), 2)
    read_fd, write_fd = os.pipe()
    try:
        browser.start()
        payload = b"private synthetic bytes\x00"
        os.write(write_fd, payload)
        snapshot = diagnostic._startup_wait_snapshot(browser._proc, write_fd, read_fd)
        for direction in ("request", "response"):
            assert snapshot["pipes"][direction]["queued_bytes"] == len(payload)
            assert snapshot["pipes"][direction]["matches"] is False
        assert payload.decode() not in json.dumps(snapshot)
        assert os.read(read_fd, len(payload)) == payload
        with (tmp_path / "private-local-file").open("wb") as regular:
            regular.write(payload)
            not_pipe = diagnostic._startup_wait_snapshot(browser._proc, regular.fileno(), regular.fileno())
        for direction in ("request", "response"):
            assert not_pipe["pipes"][direction]["parent_inode"] is None
            assert not_pipe["pipes"][direction]["queued_bytes"] is None
    finally:
        os.close(read_fd)
        os.close(write_fd)
        browser.close()


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux procfs evidence")
def test_startup_wait_snapshot_discards_non_pipe_child_target(diagnostics_peer, monkeypatch):
    browser = diagnostic.DiagnosticChrome(diagnostics_peer(), 2)
    try:
        browser.start()
        with monkeypatch.context() as patch:
            patch.setattr(diagnostic.os, "readlink", lambda path: "/private/secret-browser-content")
            snapshot = diagnostic._startup_wait_snapshot(browser._proc, browser._w, browser._r)
        for direction in ("request", "response"):
            assert snapshot["pipes"][direction]["child_inode"] is None
            assert snapshot["pipes"][direction]["matches"] is None
        assert "secret-browser-content" not in json.dumps(snapshot)
    finally:
        browser.close()


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux FIONREAD evidence")
def test_startup_wait_unavailable_pipe_evidence_is_null_without_permission_retry(diagnostics_peer, monkeypatch):
    import fcntl

    browser = diagnostic.DiagnosticChrome(diagnostics_peer(), 2)
    calls = []

    def denied(*args, **kwargs):
        calls.append(args)
        raise PermissionError("private denial details")

    try:
        browser.start()
        with monkeypatch.context() as patch:
            patch.setattr(fcntl, "ioctl", denied)
            patch.setattr(diagnostic.os, "readlink", denied)
            snapshot = diagnostic._startup_wait_snapshot(browser._proc, browser._w, browser._r)
        assert len(calls) == 4  # Once per endpoint for ioctl and link; no retries.
        for direction in ("request", "response"):
            pipe = snapshot["pipes"][direction]
            assert isinstance(pipe["parent_inode"], int)
            assert pipe["child_inode"] is None
            assert pipe["matches"] is None
            assert pipe["queued_bytes"] is None
        assert "private denial" not in json.dumps(snapshot)
    finally:
        browser.close()


class _SnapshotProcess:
    pid = 123

    def __init__(self, returncode=None):
        self.returncode = returncode

    def poll(self):
        return self.returncode


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux procfs evidence")
def test_startup_wait_snapshot_extracts_only_fixed_numeric_fields(monkeypatch):
    fields = ["0"] * 13
    fields[0] = "D"
    for index, value in ((7, "12"), (9, "34"), (11, "56"), (12, "78")):
        fields[index] = value
    files = {"stat": "123 (private ) process-name) " + " ".join(fields),
             "wchan": "folio_wait_bit_common\n",
             "io": "read_bytes: 4096\nwrite_bytes: 8192\nrchar: private-data\n"}
    calls = []

    def text(pid, name, limit=4096):
        calls.append((pid, name, limit))
        return files[name]

    monkeypatch.setattr(diagnostic, "_proc_text", text)
    snapshot = diagnostic._startup_wait_snapshot(_SnapshotProcess(), None, None)
    assert {name for _, name, _ in calls} == {"stat", "wchan", "io"}
    assert all(pid == 123 and limit <= 4096 for pid, _, limit in calls)
    assert snapshot["state"] == "D"
    assert [snapshot[k] for k in ("minor_faults", "major_faults", "user_ticks", "system_ticks")] == [12, 34, 56, 78]
    assert snapshot["wchan"] == "folio_wait_bit_common"
    assert snapshot["read_bytes"] == 4096 and snapshot["write_bytes"] == 8192
    assert "private" not in json.dumps(snapshot)


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux procfs evidence")
@pytest.mark.parametrize("stat_text", [None, "123 malformed", "456 (unrelated process) D",
                                      "123 (private) S bad", "123 (private) S " + "² " * 12])
def test_startup_wait_unavailable_or_malformed_fields_are_null(monkeypatch, stat_text):
    files = {"stat": stat_text, "wchan": "private/path", "io": "read_bytes: invalid\nwrite_bytes: -1\n"}
    monkeypatch.setattr(diagnostic, "_proc_text", lambda pid, name, limit=4096: files[name])
    snapshot = diagnostic._startup_wait_snapshot(_SnapshotProcess(), None, None)
    assert all(snapshot[k] is None for k in ("minor_faults", "major_faults", "user_ticks", "system_ticks",
                                             "wchan", "read_bytes", "write_bytes"))
    assert "private" not in json.dumps(snapshot)


def test_startup_wait_dead_or_absent_child_does_not_read_proc(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("an exited/reaped child's PID must not be inspected")

    monkeypatch.setattr(diagnostic, "_proc_text", forbidden)
    monkeypatch.setattr(diagnostic.os, "readlink", forbidden)
    for proc in (None, _SnapshotProcess(returncode=0)):
        snapshot = diagnostic._startup_wait_snapshot(proc, None, None)
        assert snapshot["alive"] is False
        assert snapshot["state"] is None
        assert snapshot["wchan"] is None
        assert snapshot["read_bytes"] is None


def test_proc_text_is_bounded_and_does_not_retain_permission_errors(monkeypatch):
    class Handle:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def read(self, limit):
            assert limit == 17
            return "x" * limit

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: Handle())
    assert diagnostic._proc_text(123, "stat", 17) == "x" * 17

    def denied(*args, **kwargs):
        raise PermissionError("private denial details")

    monkeypatch.setattr("builtins.open", denied)
    assert diagnostic._proc_text(123, "stat") is None


def _mock_kernel_stack(monkeypatch, raw):
    calls = []

    class Handle:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def read(self, limit):
            calls.append(("read", limit))
            return raw[:limit]

    def open_stack(path, mode, *, buffering):
        calls.append(("open", path, mode, buffering))
        return Handle()

    monkeypatch.setattr("builtins.open", open_stack)
    monkeypatch.setattr(diagnostic.sys, "platform", "linux")
    return calls


def test_kernel_stack_keeps_only_bounded_function_symbols(monkeypatch):
    raw = (b"[<ffffffff81234567>] folio_wait_bit_common+0x19/0x20\n"
           b"[<0>] filemap_fault.isra.0+0x1a/0x2b [test_module]\n"
           b"[<0>] do_user_addr_fault+0x10/0x200\n"
           b"[<ffffffffdeadbeef>] ffffffffdeadbeef\n"
           b"/private/secret-page API_KEY=do-not-leak --token=private\n"
           b"[<0>] /private/path+0x1/0x2\n"
           b"[<0>] innocent+0x1/0x2 /private/path\n"
           + b"[<0>] " + b"s" * 129 + b"+0x1/0x2\n")
    calls = _mock_kernel_stack(monkeypatch, raw)
    observation = diagnostic._kernel_stack_observation(_SnapshotProcess())
    assert calls == [("open", "/proc/123/stack", "rb", 0), ("read", 4097)]
    assert observation == {"status": "ok", "symbols": ["folio_wait_bit_common", "filemap_fault.isra.0",
                                                        "do_user_addr_fault"],
                           "truncated": False, "omitted_lines": 5}
    encoded = json.dumps(observation)
    for excluded in ("ffffffff", "0x", "test_module", "/private", "do-not-leak", "API_KEY", "--token"):
        assert excluded not in encoded


def test_kernel_stack_limits_frame_count_without_additional_reads(monkeypatch):
    raw = b"".join(f"[<0>] frame_{index}+0x1/0x2\n".encode() for index in range(40))
    calls = _mock_kernel_stack(monkeypatch, raw)
    observation = diagnostic._kernel_stack_observation(_SnapshotProcess())
    assert observation["status"] == "ok"
    assert observation["symbols"] == [f"frame_{index}" for index in range(32)]
    assert observation["truncated"] is True
    assert calls == [("open", "/proc/123/stack", "rb", 0), ("read", 4097)]


def test_kernel_stack_byte_limit_discards_incomplete_final_line(monkeypatch):
    first = b"[<0>] folio_wait_bit_common+0x1/0x2\n"
    # The last syntactically valid frame is cut before its newline. It must not
    # be retained as a complete frame merely because its prefix parses.
    last = b"[<0>] incomplete_frame+0x1/0x2"
    padding = b"x" * (4096 - len(first) - len(last) - 1) + b"\n"
    calls = _mock_kernel_stack(monkeypatch, first + padding + last + b"more-private-data\n")
    observation = diagnostic._kernel_stack_observation(_SnapshotProcess())
    assert observation["status"] == "ok"
    assert observation["symbols"] == ["folio_wait_bit_common"]
    assert observation["truncated"] is True
    assert "incomplete_frame" not in json.dumps(observation)
    assert calls == [("open", "/proc/123/stack", "rb", 0), ("read", 4097)]


@pytest.mark.parametrize("raw,status", [(b"", "empty"),
                                         (b"private unavailable frame\n", "unparseable"),
                                         (b"x" * 4097, "unparseable"),
                                         (b"[<0>] function+0x1/0x2\xff\n", "invalid_encoding")])
def test_kernel_stack_distinguishes_empty_unparseable_and_encoding(monkeypatch, raw, status):
    _mock_kernel_stack(monkeypatch, raw)
    observation = diagnostic._kernel_stack_observation(_SnapshotProcess())
    assert observation["status"] == status
    assert observation["symbols"] == (None if status == "invalid_encoding" else [])
    assert observation["truncated"] is (len(raw) > 4096)
    assert "private" not in json.dumps(observation)


@pytest.mark.parametrize("failure,status", [(PermissionError("private permission detail"), "permission_denied"),
                                             (FileNotFoundError("private missing path"), "unavailable"),
                                             (OSError("private kernel detail"), "unavailable")])
@pytest.mark.parametrize("at_read", [False, True])
def test_kernel_stack_permission_and_io_errors_are_not_retried(monkeypatch, failure, status, at_read):
    calls = []

    class Handle:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def read(self, limit):
            calls.append(("read", limit))
            raise failure

    def open_stack(path, mode, *, buffering):
        calls.append(("open", path, mode, buffering))
        if at_read:
            return Handle()
        raise failure

    monkeypatch.setattr("builtins.open", open_stack)
    monkeypatch.setattr(diagnostic.sys, "platform", "linux")
    observation = diagnostic._kernel_stack_observation(_SnapshotProcess())
    assert observation == {"status": status, "symbols": None, "truncated": False, "omitted_lines": 0}
    assert calls == [("open", "/proc/123/stack", "rb", 0)] + ([("read", 4097)] if at_read else [])
    assert "private" not in json.dumps(observation)


def test_kernel_stack_does_not_inspect_absent_reaped_or_unsupported_child(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("must not inspect absent, reaped or unsupported child")

    monkeypatch.setattr("builtins.open", forbidden)
    monkeypatch.setattr(diagnostic.sys, "platform", "linux")
    for proc in (None, _SnapshotProcess(returncode=0)):
        observation = diagnostic._kernel_stack_observation(proc)
        assert observation["status"] == "not_running"
        assert observation["symbols"] is None
    monkeypatch.setattr(diagnostic.sys, "platform", "darwin")
    observation = diagnostic._kernel_stack_observation(_SnapshotProcess())
    assert observation["status"] == "unsupported"
    assert observation["symbols"] is None


def test_kernel_stack_is_not_read_on_request_or_success(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("kernel stack must only be observed after readiness failure")

    monkeypatch.setattr(diagnostic, "_startup_wait_snapshot", lambda *args: {})
    monkeypatch.setattr(diagnostic, "_kernel_stack_observation", forbidden)
    browser = diagnostic.DiagnosticChrome("unused", 8)
    browser._observe_wait("request_sent")
    browser._observe_wait("response_received")
    assert all("kernel_stack" not in snapshot for snapshot in browser.wait_observations)


def test_kernel_stack_failure_read_keeps_deadline_exception_and_reports_cost(monkeypatch):
    clock = [0.0]
    deadlines = []
    stack_calls = []
    original = TimeoutError("original readiness timeout")
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])

    def send(self, method, params=None, session=None, *, deadline=None):
        deadlines.append(("send", deadline))
        return 1

    def recv(self, deadline):
        deadlines.append(("recv", deadline))
        clock[0] = deadline
        raise original

    def snapshot(*args):
        clock[0] += 3
        return {}

    def stack(proc):
        stack_calls.append(proc)
        clock[0] += 5
        return {"status": "permission_denied", "symbols": None, "truncated": False, "omitted_lines": 0}

    monkeypatch.setattr(diagnostic.Chrome, "_send", send)
    monkeypatch.setattr(diagnostic.Chrome, "_recv", recv)
    monkeypatch.setattr(diagnostic, "_startup_wait_snapshot", snapshot)
    monkeypatch.setattr(diagnostic, "_kernel_stack_observation", stack)
    browser = diagnostic.DiagnosticChrome("unused", 8)
    browser._started_at = 0
    with pytest.raises(TimeoutError) as captured:
        browser.call("Browser.getVersion")
    assert captured.value is original
    assert deadlines == [("send", 8), ("recv", 8)]
    assert browser.timeout == 8
    assert browser.readiness_elapsed_seconds == 8  # terminal evidence does not change the outcome
    assert clock[0] == 16
    assert [item["sample_duration_seconds"] for item in browser.wait_observations] == [3, 8]
    assert [item["phase"] for item in browser.wait_observations] == ["request_sent", "readiness_failure"]
    assert "kernel_stack" not in browser.wait_observations[0]
    assert browser.wait_observations[1]["kernel_stack"]["status"] == "permission_denied"
    browser.record_failure(original)
    browser._observe_wait("readiness_failure")
    assert stack_calls == [None]  # no repeated read during failure handling / cleanup


@pytest.mark.parametrize("fails", [False, True])
def test_spawn_timing_preserves_single_handoff_and_original_error(monkeypatch, fails):
    browser = diagnostic.DiagnosticChrome("/explicit/browser", timeout=8)
    calls = []
    clock = iter([10.0, 10.125])
    failure = OSError("synthetic spawn failure")

    def spawn(self, exe):
        calls.append((self, exe))
        if fails:
            raise failure

    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(diagnostic.Chrome, "_spawn", spawn)
    # Failure recording is tested separately; isolate the handoff measurement.
    monkeypatch.setattr(browser, "record_failure", lambda exc: None)
    if fails:
        with pytest.raises(OSError) as caught:
            browser._spawn("/explicit/browser")
        assert caught.value is failure
    else:
        browser._spawn("/explicit/browser")
    assert calls == [(browser, "/explicit/browser")]
    assert browser.spawn_elapsed_seconds == 0.125
    assert browser.timeout == 8


# ==== resources（旧 test_dragowing_browser_resources.py）
# Known pipe-resource defects, independent of any real-browser CI failure.
#
# These strict expected failures describe healthy behavior. Remove the matching
# xfail when the production transport is fixed; an unexpected pass must not hide it.


class _KnownResourceLimitation(AssertionError):
    """Only the reproduced defect, not a harness/setup failure, may xfail."""


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
        # Release them ourselves before the expected-failure assertion below.
        for fd in allocated:
            if _is_open(fd):
                os.close(fd)
        browser.close()

    assert calls == 2 and len(allocated) == 2
    assert error is not None and error.errno == errno.EMFILE
    assert all(not _is_open(fd) for fd in allocated)
    assert browser._proc is browser._tmp is browser._err is None
    if leaked:
        raise _KnownResourceLimitation(f"second pipe failure left descriptors open: {leaked}")


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
            except Exception as exc:
                outcome["start_error"] = error_record(exc)
            proc, profile = browser._proc, browser._tmp
            outcome["close_error"] = None
            try:
                browser.close()
            except Exception as exc:
                outcome["close_error"] = error_record(exc)
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
                reply = json.dumps({"id": message["id"], "result": {}}).encode() + b"\0"
                while reply:
                    reply = reply[os.write(4, reply):]
    """), encoding="utf-8")
    peer.chmod(0o755)
    source = Path(__file__).resolve().parents[1] / "dragowing" / "chrome_pipe.py"
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
    assert close_error is None or (
        close_error["type"] == "ValueError"
        and "filedescriptor out of range" in close_error["message"]
    ), outcome
    if (start_error is not None and start_error["type"] == "ValueError"
            and "filedescriptor out of range" in start_error["message"]):
        raise _KnownResourceLimitation(json.dumps(outcome, sort_keys=True))
    assert start_error is None, outcome
    assert outcome["close_error"] is None, outcome
    assert not outcome["process_alive_after_close"], outcome
    assert not outcome["profile_exists_after_close"], outcome


# ==== transport（旧 test_dragowing_browser_transport.py）
# Exercise real POSIX pipes with a deterministic CDP peer, without Chrome.


@pytest.fixture
def transport_peer(tmp_path):
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


def test_stderr_pressure_before_readiness_does_not_block(transport_peer):
    # Exceeds a pipe's capacity before the peer reads Browser.getVersion.
    # This must remain a regular file, not an undrained subprocess.PIPE.
    prefix = (
        "import os, stat\n"
        "assert stat.S_ISREG(os.fstat(2).st_mode)\n"
        "data = b'x' * (2 * 1024 * 1024) + b'\\nstderr-pressure-marker\\n'\n"
        "while data:\n"
        "    data = data[os.write(2, data):]\n"
    )
    with Chrome(transport_peer(prefix=prefix), timeout=5) as browser:
        assert browser.call("Echo", {"ready": True}) == {"ready": True}
        assert "stderr-pressure-marker" in browser._diagnostic()


def test_fragmented_utf8_replies_preserve_frames_and_events(transport_peer):
    # Split JSON, multi-byte UTF-8, and the NUL delimiter at arbitrary reads.
    prefix = (
        "import os\n"
        "original_write = os.write\n"
        "def fragmented_write(fd, data):\n"
        "    return original_write(fd, data[:1] if fd == 4 else data)\n"
        "os.write = fragmented_write\n"
    )
    with Chrome(transport_peer(prefix=prefix), timeout=5) as browser:
        payload = {"text": "日本語 / café / \u0000"}
        assert browser.call("Echo", payload) == payload
        browser.call("Page.navigate", session="page")
        assert browser.wait_event("Page.loadEventFired", "page")["sessionId"] == "page"
        assert browser.wait_event("Page.loadEventFired", "other")["sessionId"] == "other"


def test_delayed_readiness_is_accepted_within_launch_budget(transport_peer):
    with Chrome(transport_peer(prefix="import time; time.sleep(0.1)\n"), timeout=3) as browser:
        assert browser.call("Echo", {"delayed": True}) == {"delayed": True}


def test_startup_timeout_retains_stderr_before_cleanup(transport_peer):
    executable = transport_peer(prefix=(
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
def test_repeated_sessions_do_not_accumulate_descriptors_or_profiles(transport_peer):
    executable = transport_peer()
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
