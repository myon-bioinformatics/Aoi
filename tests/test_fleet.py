"""🌐 Fleet contracts: CI pins, vendor lock and dispatch, Node entries through the vendored py_launch.cjs, launcher regressions.

旧 test_sakanalytics_parent_workflow_pins.py・test_vendor_dispatch_workflow.py・test_annual_audit_node_entry.py・
test_synthetic_league_node_entry.py・test_node_launcher_regressions.py をここにまとめた（節の頭に旧ファイルの名前を書いた）。
名前は org の多数（tests/test_fleet.py）に合わせた。親の vendor/fleet_check.py はまだ取り込んでいないので、中身はこのリポジトリの検査のまま。

Node entry: `node vendor/py_launch.cjs --env-var <TOOL>_PYTHON -- npb/<tool>.py ARGS` (no per-tool wrapper).
"""
from __future__ import annotations

import hashlib, json, os, re, select, shutil, signal, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
# Node 入口: ツール名 -> 本体（トップには汎用版だけ。ツールは npb/ にいる）。環境変数は <TOOL>_PYTHON
TOOLS = {"annual_audit": "npb/annual_audit.py", "synthetic_league": "npb/synthetic_league.py"}
CASES = [{"id": "help", "args": ["--help"], "rc": 0}, {"id": "bogus", "args": ["--bogus"], "rc": 2}]


# ==== parent pins（旧 test_sakanalytics_parent_workflow_pins.py）: local rollout contract; adopted vendor locks are deliberately independent

PARENT = "myon-bioinformatics/myon-bioinformatics"
PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"


def test_parent_workflow_references_use_reviewed_rollout_commit():
    pins = []
    for path in sorted((ROOT / ".github/workflows").glob("*")):
        if path.suffix not in (".yml", ".yaml"):
            continue
        text = path.read_text(encoding="utf-8")
        # Capture mutable and shortened references too, rather than ignoring them.
        pins.extend(re.findall(r"uses:\s*['\"]?" + re.escape(PARENT) + r"/[^\s@'\"]+@([^\s'\"]+)", text))
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.fullmatch(r"\s+repository:\s*['\"]?" + re.escape(PARENT) + r"['\"]?\s*", line):
                refs = [re.fullmatch(r"\s+ref:\s*['\"]?([^\s'\"]+)['\"]?\s*", item) for item in lines[i + 1:i + 12]]
                pins.append(next((m.group(1) for m in refs if m), None))
    assert pins, "shared parent references must remain observable"
    assert set(pins) == {PARENT_WORKFLOW_PIN}, pins


# ==== action pins and vendor dispatch（旧 test_vendor_dispatch_workflow.py）: parent vendor dispatch in CI stays a verify of vendor.lock.json

AT = chr(64)

ACTION_PINS = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2",
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
}


def _uses_lines(text):
    return [
        line.strip()
        for line in text.splitlines()
        if re.match(r"(?:-\s+)?uses:", line.strip())
    ]


PARENT_REUSABLE = re.compile(r"(?:-\s+)?uses:\s+myon-bioinformatics/myon-bioinformatics/\.github/workflows/")


def _pin_ok(line):
    if PARENT_REUSABLE.match(line):
        # 親リポの reusable workflow はリリースタグがないので、40 桁 SHA だけを確認する
        return re.search(re.escape(AT) + r"[0-9a-f]{40}\s*$", line) is not None
    match = re.search(re.escape(AT) + r"([0-9a-f]{40})\s+#\s+v\d+\.\d+\.\d+\s*$", line)
    if not match:
        return False
    owner = line.split(AT, 1)[0].split()[-1]
    return ACTION_PINS.get(owner) == match.group(1)


def test_all_actions_are_pinned_to_full_shas():
    lines = _uses_lines(WORKFLOW.read_text(encoding="utf-8"))
    assert lines
    assert any(line.startswith("uses:") for line in lines)
    for line in lines:
        assert _pin_ok(line), line


def test_parent_reusable_workflow_passes_on_sha_alone():
    sha = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
    line = "uses: myon-bioinformatics/myon-bioinformatics/.github/workflows/x.yml" + AT + sha
    assert _pin_ok(line)


def test_other_repo_reusable_workflow_needs_more_than_sha():
    sha = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
    for line in (
        "uses: other-org/other-repo/.github/workflows/x.yml" + AT + sha,
        "uses: myon-bioinformatics/Aoi/.github/workflows/x.yml" + AT + sha,
    ):
        assert not _pin_ok(line), line


def test_vendor_dispatch_verifies_the_lock_without_record():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pilot/vendor_dispatch.py" in text
    assert "vendor.lock.json" in text
    assert 'PARENT_REPOSITORY_ID: "638801160"' in text
    assert "git ls-remote" in text
    assert "refs/heads/main" in text
    invocations = [
        line for line in text.splitlines()
        if "vendor_dispatch.py" in line and not line.lstrip().startswith("#")
    ]
    assert invocations
    for line in invocations:
        assert "--record" not in line
        assert "-S" not in line
    assert (ROOT / "vendor.lock.json").is_file()


def test_action_with_sha_but_no_version_comment_fails():
    line = "uses: actions/checkout" + AT + ACTION_PINS["actions/checkout"]
    assert not _pin_ok(line), line


def test_vendor_dispatch_node_floor_matches_setup_node():
    """Execute the defensive guard at the Node 26 boundary."""
    text = WORKFLOW.read_text(encoding="utf-8")
    job = text.split("\n  vendor-dispatch:", 1)[1]
    guard = re.search(r'if \[\[ "\$node_major" -lt \d+ \]\]; then\n.*?\n          fi', job, re.S)
    assert guard is not None
    assert 'node-version: "26"' in job
    for major, expected in ((24, 1), (25, 1), (26, 0), (27, 0)):
        result = subprocess.run(
            ["bash", "-c", f"node_major={major}\n" + guard.group()],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == expected, (major, result.stdout, result.stderr)


# ==== Node entry（旧 test_annual_audit_node_entry.py・test_synthetic_league_node_entry.py）: parity with npb/<tool>.py

def _node() -> str | None:
    node = os.environ.get("NODE") or shutil.which("node")
    if node:
        try:
            result = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return None
        match = re.match(r"v(\d+)", result.stdout.strip())
        if result.returncode == 0 and match and int(match[1]) >= 26:
            return node
    return None


NODE = _node()
needs_node = pytest.mark.skipif(NODE is None, reason="Node 26+ not available (set NODE)")


def _env(tool: str) -> dict[str, str]:
    env = dict(os.environ)
    env[f"{tool.upper()}_PYTHON"] = sys.executable
    env.pop("PY_LAUNCH_ERROR_FORMAT", None)
    return env


def _run(argv: list[str], cwd: Path, env: dict[str, str]) -> tuple[int, str, str]:
    p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    return p.returncode, p.stdout, p.stderr


def _direct(root: Path, tool: str, script: str, *args: str) -> list[str]:
    """The documented command: node vendor/py_launch.cjs --env-var <TOOL>_PYTHON -- <script> ARGS (no per-tool wrapper)."""
    return [NODE, str(root / "vendor" / "py_launch.cjs"), "--env-var", f"{tool.upper()}_PYTHON", "--",
            str(root / script), *args]


def _copy_launcher(tmp_path: Path, tool: str) -> dict[str, str]:
    (tmp_path / "vendor").mkdir()
    shutil.copyfile(ROOT / "vendor/py_launch.cjs", tmp_path / "vendor/py_launch.cjs")
    return _env(tool)


def test_ci_requires_node_for_node_entry_parity():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    job = workflow.split("\n  test:\n", 1)[1]
    # The test job must set up Node before running its pytest suite.
    job = job.split("\n  failure-identity:", 1)[0]
    assert "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1" in job
    assert "node-version: '26'" in job
    assert "Require supported Node in parity CI" in job
    if os.environ.get("GITHUB_ACTIONS") == "true":
        assert NODE is not None, "Node 26+ is required for the Node parity suite"


def test_vendored_launcher_matches_lock():
    lock = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))
    entry = next(f for f in lock["files"] if f["destination"] == "vendor/py_launch.cjs")
    assert entry["repository"] == "myon-bioinformatics/Aoi"
    assert entry["commit"] == entry["ref"] == "9e0147a17695ce63fa73daf75d8195a4f49095bb"
    assert entry["source"] == "vendor/py_launch.cjs"
    data = (ROOT / "vendor" / "py_launch.cjs").read_bytes()
    assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    assert blob == entry["blob_sha"]


@pytest.mark.parametrize("tool", TOOLS)
def test_no_per_tool_wrapper_and_readme_documents_the_direct_command(tool):
    assert not (ROOT / f"{tool}.cjs").exists()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"node vendor/py_launch.cjs --env-var {tool.upper()}_PYTHON -- {TOOLS[tool]}" in readme
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["engines"]["node"] == ">=26"


@needs_node
@pytest.mark.parametrize("args,expected_rc", [(c["args"], c["rc"]) for c in CASES],
                         ids=[c["id"] for c in CASES])
@pytest.mark.parametrize("tool", TOOLS)
def test_node_matches_python(tool, args, expected_rc):
    via_node = _run(_direct(ROOT, tool, TOOLS[tool], *args), ROOT, _env(tool))
    via_python = _run([sys.executable, "-S", str(ROOT / TOOLS[tool]), *args], ROOT, _env(tool))
    assert via_python[0] == expected_rc
    assert via_node == via_python


@needs_node
@pytest.mark.parametrize("tool", TOOLS)
def test_missing_interpreter_is_launcher_failure(tmp_path, tool):
    env = _env(tool)
    env[f"{tool.upper()}_PYTHON"] = str(tmp_path / "no-such-python")
    p = subprocess.run(_direct(ROOT, tool, TOOLS[tool], "--help"), env=env,
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == 2
    assert p.stdout == ""


@needs_node
@pytest.mark.parametrize("code", [0, 1, 3, 7])
@pytest.mark.parametrize("tool", TOOLS)
def test_entry_forwards_stdin_argv_and_exit_code(tmp_path, tool, code):
    env = _copy_launcher(tmp_path, tool)
    script = tmp_path / TOOLS[tool]
    script.parent.mkdir(exist_ok=True)
    script.write_text(
        "import json, sys\n"
        "sys.stdout.write(json.dumps({'argv': sys.argv[1:], 'stdin': sys.stdin.read(),"
        " 'nosite': sys.flags.no_site}))\n"
        f"sys.exit({code})\n", encoding="utf-8")
    p = subprocess.run(_direct(tmp_path, tool, TOOLS[tool], "a b", "--x=ü"), env=env,
                       input="こんにちは\n", capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert p.returncode == code
    assert json.loads(p.stdout) == {"argv": ["a b", "--x=ü"], "stdin": "こんにちは\n", "nosite": 1}


# ==== launcher regressions（旧 test_node_launcher_regressions.py）: real-process regressions for the launcher inherited only from Aoi

def _site_hook(tmp_path: Path, env: dict[str, str]) -> Path:
    marker = tmp_path / "site-hook-ran"
    (tmp_path / "sitecustomize.py").write_text(
        "import os\n"
        "with open(os.environ['PY_LAUNCH_SITE_MARKER'], 'w') as out:\n"
        "    out.write('ran')\n"
        "raise SystemExit(42)\n", encoding="utf-8",
    )
    env.update(PYTHONPATH=str(tmp_path), PY_LAUNCH_SITE_MARKER=str(marker))
    return marker


@needs_node
@pytest.mark.parametrize("tool", TOOLS)
def test_every_entry_suppresses_site_during_discovery(tmp_path, tool):
    env = _copy_launcher(tmp_path, tool)
    marker = _site_hook(tmp_path, env)
    (tmp_path / f"{tool}.py").write_text(
        "import sys\nprint(sys.flags.no_site)\n", encoding="utf-8",
    )
    result = subprocess.run(
        _direct(tmp_path, tool, f"{tool}.py"), cwd=tmp_path, env=env,
        capture_output=True, text=True, timeout=10,
    )
    assert not marker.exists(), "interpreter discovery must also use -S"
    assert (result.returncode, result.stdout, result.stderr) == (0, "1\n", "")


@needs_node
@pytest.mark.parametrize("mode", ["resolve", "run", "main"])
@pytest.mark.parametrize("flags", [{}, {"noSite": True}, {"isolated": True}, {"noSite": True, "isolated": True}],
                         ids=["default", "noSite", "isolated", "both"])
def test_library_discovery_flags_are_independent(tmp_path, mode, flags):
    env = dict(os.environ)
    env.pop("PY_LAUNCH_ERROR_FORMAT", None)
    marker = _site_hook(tmp_path, env)
    script = tmp_path / "echo.py"
    script.write_text("print('safe')\n", encoding="utf-8")
    options = json.dumps({"python": sys.executable, **flags})
    script_arg = json.dumps(str(script))
    calls = {
        "resolve": f"launcher.resolvePython({options}); console.log('safe');",
        "run": f"process.stdout.write(launcher.run({script_arg}, [], {options}).stdout);",
        "main": f"launcher.main({script_arg}, {options});",
    }
    program = f"const launcher = require({json.dumps(str(ROOT / 'vendor/py_launch.cjs'))}); {calls[mode]}"
    result = subprocess.run([NODE, "-e", program], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=10)
    if not flags:
        assert marker.exists(), "control must prove the hostile site hook is reachable"
        assert result.returncode != 0
        assert "not suitable" in result.stderr
    else:
        assert not marker.exists(), "startup flags must also protect the version probe"
        assert (result.returncode, result.stdout, result.stderr) == (0, "safe\n", "")


def _expect_line(process: subprocess.Popen, expected: bytes) -> None:
    ready, _, _ = select.select([process.stdout], [], [], 5)
    assert ready, f"timed out waiting for child acknowledgement: {expected!r}"
    actual = process.stdout.readline()
    assert actual == expected, (actual, expected, process.poll())


@needs_node
@pytest.mark.skipif(os.name == "nt", reason="requires POSIX signals and process groups")
@pytest.mark.parametrize("tool", TOOLS)
@pytest.mark.parametrize("ignored,terminal", [("SIGINT", "SIGTERM"), ("SIGTERM", "SIGINT")])
@pytest.mark.parametrize("repetitions", [0, 2], ids=["direct", "repeated"])
@pytest.mark.parametrize("error_format", ["text", "json"])
def test_every_entry_forwards_acknowledged_signals(tmp_path, tool, ignored, terminal, repetitions, error_format):
    env = _copy_launcher(tmp_path, tool)
    env["PY_LAUNCH_ERROR_FORMAT"] = error_format
    (tmp_path / f"{tool}.py").write_text(
        "import signal, time\n"
        "def acknowledge(_signal, _frame):\n"
        f"    print('IGNORED {ignored}', flush=True)\n"
        f"signal.signal(signal.{ignored}, acknowledge)\n"
        f"signal.signal(signal.{terminal}, signal.SIG_DFL)\n"
        "print('READY', flush=True)\n"
        "while True:\n"
        "    time.sleep(60)\n", encoding="utf-8",
    )
    process = subprocess.Popen(
        _direct(tmp_path, tool, f"{tool}.py"), cwd=tmp_path, env=env,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        _expect_line(process, b"READY\n")
        for _ in range(repetitions):
            # Only signal the launcher PID, never the Python child or its group.
            process.send_signal(getattr(signal, ignored))
            _expect_line(process, f"IGNORED {ignored}\n".encode())
            assert process.poll() is None
        process.send_signal(getattr(signal, terminal))
        stdout, stderr = process.communicate(timeout=5)
        assert process.returncode == 2
        assert stdout == b""
        assert stderr.count(b"\n") == 1
        if error_format == "json":
            payload = json.loads(stderr)
            assert payload["ok"] is False
            assert payload["code"] == "ESIGNAL"
            assert payload["exit_code"] == 2
            assert payload["message"].endswith(f"terminated by signal {terminal}")
        else:
            assert stderr.decode().strip().endswith(f"terminated by signal {terminal}")
    finally:
        # Also reap an orphaned Python process when testing a broken launcher.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate(timeout=5)
