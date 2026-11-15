"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py): vendor lock, parent pins, CI jobs,
Node entries through the vendored py_launch.cjs, the launcher contract and the benchmark -O guard.

共通の検査（ロックのバイト列・親のピン・ジョブの本文・Node 26 の解決・Node と Python の一致・ランチャーの契約・
ベンチマークの -O ガード）は親の vendor/fleet_check.py を呼ぶ。ここに残すのは、このリポジトリの期待値（ピン・ツール・
ケース・文言）と、fleet_check にまだ無い検査（アクションのピン、vendor-dispatch の中身、ライブラリの run / main、
両方向のシグナル）だけ。

Node entry: `node vendor/py_launch.cjs --env-var <TOOL>_PYTHON -- npb/<tool>.py ARGS` (no per-tool wrapper).
"""
from __future__ import annotations

import importlib.util, json, os, re, select, shutil, signal, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# Aoi は子をまとめて 1 回の pytest で動かす。トップの vendor パッケージは子どうしでぶつかるので、場所から固有の名前で読む
_spec = importlib.util.spec_from_file_location("sakanalytics_fleet_check", ROOT / "vendor/fleet_check.py")
fleet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fleet)

PARENT_WORKFLOW_PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
ACCEPTED = {
    "vendor/py_launch.cjs": "9e0147a17695ce63fa73daf75d8195a4f49095bb",
    "vendor/uv_tool_build.py": "f15063440ee7f5f869cef1546ae651fa32a07505",
    "vendor/fleet_check.py": "6c29503cf17eda856766ddfdf4d66a5b0965a8b1",
}
ACTION_PINS = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2",
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
}
# Node 入口: ツール名 -> 本体（トップには汎用版だけ。ツールは npb/ にいる）。環境変数は <TOOL>_PYTHON
TOOLS = {"annual_audit": "npb/annual_audit.py", "synthetic_league": "npb/synthetic_league.py"}
CASES = [{"id": "help", "args": ["--help"], "rc": 0}, {"id": "bogus", "args": ["--bogus"], "rc": 2}]
BENCHMARK = "scripts/benchmark_neighbor_retention.py"
# GitHub Actions の test ジョブでは、Node 26 が無いと fleet.node() が AssertionError で止める（skip にしない）
NODE = fleet.node()
needs_node = pytest.mark.skipif(NODE is None, reason="Node 26+ not available (set NODE)")


def _env_var(tool: str) -> str:
    return f"{tool.upper()}_PYTHON"


# ==== vendor lock と親のピン: local rollout contract; adopted vendor locks are deliberately independent

def test_vendor_lock_matches_checked_in_bytes_and_accepted_commits():
    rows = fleet.check_lock(ROOT, commits=ACCEPTED)
    launcher = rows["vendor/py_launch.cjs"]
    assert (launcher["repository"], launcher["source"]) == ("myon-bioinformatics/Aoi", "vendor/py_launch.cjs")


def test_parent_workflow_references_use_reviewed_rollout_commit():
    assert set(fleet.parent_refs(ROOT)) == {PARENT_WORKFLOW_PIN}


# ==== action pins（fleet_check にまだ無い）: 親の reusable workflow は 40 桁 SHA、ほかは SHA と版のコメント

AT = chr(64)
PARENT_REUSABLE = re.compile(r"(?:-\s+)?uses:\s+" + re.escape(fleet.PARENT) + r"/\.github/workflows/")


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
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if re.match(r"(?:-\s+)?uses:", line.strip())]
    assert lines
    assert any(line.startswith("uses:") for line in lines)
    for line in lines:
        assert _pin_ok(line), line


def test_parent_reusable_workflow_passes_on_sha_alone():
    assert _pin_ok(f"uses: {fleet.PARENT}/.github/workflows/x.yml" + AT + PARENT_WORKFLOW_PIN)


def test_other_repo_reusable_workflow_needs_more_than_sha():
    for line in (
        "uses: other-org/other-repo/.github/workflows/x.yml" + AT + PARENT_WORKFLOW_PIN,
        "uses: myon-bioinformatics/Aoi/.github/workflows/x.yml" + AT + PARENT_WORKFLOW_PIN,
    ):
        assert not _pin_ok(line), line


def test_action_with_sha_but_no_version_comment_fails():
    line = "uses: actions/checkout" + AT + ACTION_PINS["actions/checkout"]
    assert not _pin_ok(line), line


# ==== CI のジョブ: vendor-dispatch は vendor.lock.json の検証のまま、test は pytest の前に Node 26 を入れる

def test_vendor_dispatch_verifies_the_lock_without_record():
    job = fleet.workflow_job(ROOT, "vendor-dispatch")
    assert "pilot/vendor_dispatch.py" in job
    assert "vendor.lock.json" in job
    assert 'PARENT_REPOSITORY_ID: "638801160"' in job
    assert "git ls-remote" in job
    assert "refs/heads/main" in job
    invocations = [line for line in job.splitlines()
                   if "vendor_dispatch.py" in line and not line.lstrip().startswith("#")]
    assert invocations
    for line in invocations:
        assert "--record" not in line
        assert "-S" not in line
    assert (ROOT / "vendor.lock.json").is_file()


def test_vendor_dispatch_node_floor_matches_setup_node():
    """Execute the defensive guard at the Node 26 boundary."""
    job = fleet.workflow_job(ROOT, "vendor-dispatch")
    guard = re.search(r'if \[\[ "\$node_major" -lt \d+ \]\]; then\n.*?\n          fi', job, re.S)
    assert guard is not None
    assert 'node-version: "26"' in job
    for major, expected in ((24, 1), (25, 1), (26, 0), (27, 0)):
        result = subprocess.run(
            ["bash", "-c", f"node_major={major}\n" + guard.group()],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == expected, (major, result.stdout, result.stderr)


def test_ci_requires_node_for_node_entry_parity():
    job = fleet.workflow_job(ROOT, "test")
    assert "actions/setup-node" + AT + ACTION_PINS["actions/setup-node"] in job
    assert "node-version: '26'" in job
    assert "Require supported Node in parity CI" in job


# ==== Node entry: parity with npb/<tool>.py, and the vendored launcher's contract

@pytest.mark.parametrize("tool", TOOLS)
def test_no_per_tool_wrapper_and_readme_documents_the_direct_command(tool):
    assert not (ROOT / f"{tool}.cjs").exists()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"node vendor/py_launch.cjs --env-var {_env_var(tool)} -- {TOOLS[tool]}" in readme
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert pkg["engines"]["node"] == ">=26"


@needs_node
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
@pytest.mark.parametrize("tool", TOOLS)
def test_node_matches_python(tool, case):
    via_node, via_python = fleet.node_parity(ROOT, TOOLS[tool], _env_var(tool), *case["args"])
    assert via_python[0] == case["rc"]
    assert via_node == via_python


@needs_node
@pytest.mark.parametrize("tool", TOOLS)
def test_vendored_launcher_keeps_its_contract(tool):
    # 無いインタープリタは終了コード 2、argv・stdin・終了コードは -S のまま素通し、探索でも sitecustomize を読まない
    fleet.launcher_contract(ROOT, _env_var(tool))


# ==== launcher regressions（fleet_check にまだ無い）: ライブラリの run / main と、両方向のシグナル

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
    (tmp_path / "vendor").mkdir()
    shutil.copyfile(ROOT / "vendor/py_launch.cjs", tmp_path / "vendor/py_launch.cjs")
    env = {**os.environ, _env_var(tool): sys.executable, "PY_LAUNCH_ERROR_FORMAT": error_format}
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
        [NODE, str(tmp_path / "vendor/py_launch.cjs"), "--env-var", _env_var(tool), "--", str(tmp_path / f"{tool}.py")],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
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


# ==== -O ガード（旧 test_neighbor_retention.py の BenchmarkGuardTests）: assert を外す -O でも不一致の検査が効く

def test_benchmark_mismatch_exits_under_optimization_without_reporting_success():
    patch = ("g['subprocess'].check_output = lambda *args, **kwargs: b'def discover(rows): return {\"reference\": True}'\n"
             "g['neighbors'].discover = lambda rows: {}")
    result = fleet.run_main(ROOT, BENCHMARK, patch, optimized=True, timeout=30)
    assert result.returncode != 0, result.stdout
    assert "report mismatch" in result.stderr
    assert result.stdout == ""
