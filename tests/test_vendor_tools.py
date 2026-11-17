"""vendor/ の共通道具（親から配られたコピー）が Aoi で動くこと。

- 🧰 vendor/uv_tool_build.py: Aoi の子エントリで build できること、大文字のエントリを拒むこと
- 🚀 vendor/py_launch.cjs: Node から Python を安全に探して起動すること（site の抑止・シグナルの転送・CLI）。
  Node 26+ で JS の短い断片を実行し、判定は Python 側で行う（GitHub Actions では Node 26+ がなければ失敗）

バイトの一致は tests/test_vendor_lock.py と scripts/repo_checks.py shared_tools_lock が見る。
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "vendor" / "uv_tool_build.py"
LAUNCHER = ROOT / "vendor" / "py_launch.cjs"


# ---- 🧰 vendor/uv_tool_build.py ----------------------------------------------------


def _load():
    spec = importlib.util.spec_from_file_location("aoi_vendor_uv_tool_build", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builds_lowercase_child_entry(tmp_path):
    out = tmp_path / "nagoyaction-tool"
    # NagoyAction #58 で hub・localci も nagoyaction.py 1 本になった。--module は要らない
    result = _load().build([ROOT / "nagoyaction" / "nagoyaction.py"], out)
    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["name"] == "nagoyaction"
    assert data["project"]["dependencies"] == []
    assert data["project"]["scripts"] == {"nagoyaction": "nagoyaction:main"}
    assert result["scripts"] == {"nagoyaction": "nagoyaction:main"}
    assert (out / "nagoyaction.py").read_bytes() == (ROOT / "nagoyaction" / "nagoyaction.py").read_bytes()


def test_builds_blueprobe_entry_without_its_removed_local_builder(tmp_path):
    """BlueProbe #53 dropped build_stdlib_tool.py; the shared builder packages blueprobe.py."""
    out = tmp_path / "blueprobe-tool"
    result = _load().build([ROOT / "blueprobe" / "blueprobe.py"], out)
    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["name"] == "blueprobe"
    assert data["project"]["dependencies"] == []
    assert data["project"]["scripts"] == {"blueprobe": "blueprobe:main"}
    assert result["scripts"] == {"blueprobe": "blueprobe:main"}
    assert (out / "blueprobe.py").read_bytes() == (ROOT / "blueprobe" / "blueprobe.py").read_bytes()


def test_rejects_camelcase_entry_name(tmp_path):
    camel = tmp_path / "NagoyAction.py"
    camel.write_text("def main():\n    return 0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="lowercase"):
        _load().build([camel], tmp_path / "out")


def test_cli_runs_without_site(tmp_path):
    run = subprocess.run([sys.executable, "-S", str(BUILDER), str(ROOT / "nagoyaction" / "nagoyaction.py"),
                          *(arg for m in NAGOYACTION_MODULES for arg in ("--module", str(m))),
                          "--out", str(tmp_path / "o"), "--json"], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


# ---- 🚀 vendor/py_launch.cjs ------------------------------------------------------
USAGE = re.compile(r"usage: node py_launch\.cjs \[--env-var NAME\] \[--site\] \[--\] SCRIPT\.py")


@pytest.fixture(scope="module")
def node():
    exe = shutil.which("node")
    major = 0
    if exe:
        out = subprocess.run([exe, "-p", "process.versions.node"], capture_output=True, text=True, check=False).stdout
        major = int(out.split(".")[0] or 0)
    if major < 26:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            pytest.fail("py_launch のテストには Node 26+ が要る（CI では setup-node で入れる）")
        pytest.skip("Node 26+ がない（py_launch は古い Node へ戻らない）")
    return exe


def _js(node, code, **kw):
    """`launcher` に vendor/py_launch.cjs を入れて JS の断片を実行する。"""
    return subprocess.run([node, "-e", f"const launcher = require({json.dumps(str(LAUNCHER))});\n{code}"],
                          capture_output=True, text=True, timeout=10, check=False, **kw)


def _cli(node, argv, env=None, cwd=None):
    return subprocess.run([node, str(LAUNCHER), *argv], capture_output=True, text=True, timeout=10, check=False,
                          env=env, cwd=cwd)


def test_launcher_keeps_node_26_as_its_minimum(node):
    probe = _js(node, """
const codes = (vs) => vs.map((v) => { try { launcher.assertNodeVersion(v); return null; } catch (e) { return e.code; } });
console.log(JSON.stringify({ min: launcher.MIN_NODE, old: codes(["24.0.0", "24.99.0", "25.0.0", "25.99.0"]),
                             ok: codes(["26.0.0", "26.1.0", "27.0.0"]) }));""")
    assert probe.returncode == 0, probe.stderr
    assert json.loads(probe.stdout) == {"min": [26, 0], "old": ["ENODEVERSION"] * 4, "ok": [None] * 3}


def _run_with_site_hook(node, tmp_path, mode, flags):
    """sitecustomize が走ったら印を書いて 42 で落ちる。探索・実行のどちらかで site が読まれたかを印で見る。"""
    marker, script = tmp_path / "hook-ran", tmp_path / "echo.py"
    script.write_text("import sys\nprint(sys.argv[1])\n", encoding="utf-8")
    (tmp_path / "sitecustomize.py").write_text(
        f"with open({str(marker)!r}, 'w') as out:\n    out.write('ran')\nraise SystemExit(42)\n", encoding="utf-8")
    opts, arg = json.dumps({"python": sys.executable, **flags}), json.dumps(str(script))
    call = {"resolve": f'launcher.resolvePython({opts}); console.log("safe");',
            "run": f'process.stdout.write(launcher.run({arg}, ["safe"], {opts}).stdout);',
            "main": f'launcher.main({arg}, {{ ...{opts}, argv: ["safe"] }});'}[mode]
    result = _js(node, call, env={**os.environ, "PYTHONPATH": str(tmp_path)})
    return result, marker.exists()


def test_default_discovery_still_enables_site_startup(node, tmp_path):
    result, hook_ran = _run_with_site_hook(node, tmp_path, "resolve", {})
    assert hook_ran and result.returncode != 0
    assert "not suitable" in result.stderr


@pytest.mark.parametrize("mode", ["resolve", "run", "main"])
@pytest.mark.parametrize("flags", [{"noSite": True}, {"isolated": True}, {"noSite": True, "isolated": True}], ids=json.dumps)
def test_site_flags_suppress_sitecustomize_in_discovery_and_execution(node, tmp_path, mode, flags):
    result, hook_ran = _run_with_site_hook(node, tmp_path, mode, flags)
    assert not hook_ran, "the interpreter probe must also suppress sitecustomize"
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "safe"


def test_discovery_puts_startup_flags_after_prefixes_and_before_c(node, tmp_path):
    stub = tmp_path / "probe.cjs"   # 候補の「Python」として node を使い、受け取った引数を確かめる
    stub.write_text('require("node:assert/strict").deepEqual(process.argv.slice(2, -1), ["-S", "-I", "-c"]);\n'
                    'console.log("3.12");\n', encoding="utf-8")
    probe = _js(node, f"""
const candidate = {{ cmd: process.execPath, prefix: [{json.dumps(str(stub))}], label: "probe", strict: true }};
console.log(launcher.resolvePython({{ candidates: [candidate], noSite: true, isolated: true }}).cmd === process.execPath);""")
    assert probe.returncode == 0, probe.stderr
    assert probe.stdout.strip() == "true"


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX signals")
@pytest.mark.parametrize("json_errors", [False, True], ids=["text", "json"])
@pytest.mark.parametrize("interrupts", [0, 2])
def test_forwards_sigterm_after_ignored_sigints(node, tmp_path, interrupts, json_errors):
    script = tmp_path / "ignore_sigint.py"
    script.write_text("import signal, time\n"
                      "signal.signal(signal.SIGINT, lambda *_: print('IGNORED SIGINT', flush=True))\n"
                      "print('READY', flush=True)\n"
                      "while True:\n    time.sleep(60)\n", encoding="utf-8")
    opts = json.dumps({"python": sys.executable, "jsonErrors": json_errors, "noSite": True})
    proc = subprocess.Popen([node, "-e", f"require({json.dumps(str(LAUNCHER))}).main({json.dumps(str(script))}, {opts});"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                            env={**os.environ, "PY_LAUNCH_ERROR_FORMAT": ""})

    timed_out = threading.Event()

    def kill_group():
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    watchdog = threading.Timer(7.5, lambda: (timed_out.set(), kill_group()))   # 止まらなければ読み取りが空になり、下で落ちる
    watchdog.start()
    try:
        assert proc.stdout.readline() == "READY\n"
        for _ in range(interrupts):
            proc.send_signal(signal.SIGINT)
            assert proc.stdout.readline() == "IGNORED SIGINT\n"
        proc.send_signal(signal.SIGTERM)
        stdout, stderr = proc.communicate(timeout=10)
    finally:
        watchdog.cancel()
        kill_group()
    assert not timed_out.is_set(), f"launcher did not terminate; stdout={stdout}; stderr={stderr}"
    assert proc.returncode == 2, (stdout, stderr)
    assert "IGNORED SIGINT" not in stdout
    if json_errors:
        payload = json.loads(stderr)
        assert (payload["ok"], payload["code"], payload["exit_code"]) == (False, "ESIGNAL", 2)
        assert "SIGTERM" in payload["message"]
    else:
        assert "terminated by signal SIGTERM" in stderr


def test_cli_site_and_env_var_options(node, tmp_path):
    """--site は -S を外す。既定は -S。SCRIPT.py より前ならオプションの順は自由（親リポジトリ #185 から移植）。"""
    script = tmp_path / "flags.py"
    script.write_text("import sys\nprint(sys.flags.no_site, 'site' in sys.modules, ' '.join(sys.argv[1:]))\n", encoding="utf-8")
    default = _cli(node, [str(script), "x"])
    assert (default.returncode, default.stdout.strip()) == (0, "1 False x"), default.stderr
    site = _cli(node, ["--site", str(script), "x"])
    assert (site.returncode, site.stdout.strip()) == (0, "0 True x"), site.stderr
    env = {**os.environ, "MY_TOOL_PYTHON": sys.executable}
    for argv in (["--env-var", "MY_TOOL_PYTHON", "--site"], ["--site", "--env-var", "MY_TOOL_PYTHON"],
                 ["--site", "--env-var=MY_TOOL_PYTHON"]):
        r = _cli(node, [*argv, str(script)], env)
        assert (r.returncode, r.stdout.strip()) == (0, "0 True"), f"{argv}: {r.stderr}"
    strict = _cli(node, ["--site", "--env-var", "MY_TOOL_PYTHON", str(script)],
                  {**os.environ, "MY_TOOL_PYTHON": str(tmp_path / "no-such-python")})
    assert strict.returncode == 2 and "MY_TOOL_PYTHON" in strict.stderr
    assert _cli(node, [str(script), "--site"]).stdout.strip() == "1 False --site"
    unknown = _cli(node, ["--sites", str(script)])
    assert unknown.returncode == 2 and USAGE.search(unknown.stderr)
    missing = _cli(node, ["--site", "--env-var"])
    assert missing.returncode == 2 and "--env-var needs a variable name" in missing.stderr
    no_script = _cli(node, ["--site"])
    assert no_script.returncode == 2 and "usage:" in no_script.stderr


def test_cli_separator_repeats_and_site_packages(node, tmp_path):
    """単独の -- でオプションが終わる。繰り返しは後勝ち。--site で site-packages が sys.path に入る。"""
    script, dash, paths = tmp_path / "flags.py", tmp_path / "-dash.py", tmp_path / "paths.py"
    script.write_text("import sys\nprint(sys.flags.no_site, ' '.join(sys.argv[1:]))\n", encoding="utf-8")
    dash.write_text("print('dash')\n", encoding="utf-8")
    paths.write_text("import os, sys, site\nn = os.path.normcase\nroots = {n(sys.prefix), n(sys.base_prefix)}\n"
                     "print(sum(1 for d in site.getsitepackages() if d in sys.path and n(d) not in roots))\n", encoding="utf-8")
    sep = _cli(node, ["--site", "--", str(script), "--", "x"])
    assert (sep.returncode, sep.stdout.strip()) == (0, "0 -- x"), sep.stderr
    sep_default = _cli(node, ["--", str(script)])
    assert (sep_default.returncode, sep_default.stdout.strip()) == (0, "1"), sep_default.stderr
    dashed = _cli(node, ["--", "-dash.py"], cwd=tmp_path)
    assert (dashed.returncode, dashed.stdout.strip()) == (0, "dash"), dashed.stderr
    no_script = _cli(node, ["--site", "--"])
    assert no_script.returncode == 2 and USAGE.search(no_script.stderr)
    env = {**os.environ, "GOOD_PY": sys.executable, "BAD_PY": str(tmp_path / "no-such-python")}
    last_good = _cli(node, ["--env-var", "BAD_PY", "--env-var=GOOD_PY", str(script)], env)
    assert last_good.returncode == 0, last_good.stderr
    last_bad = _cli(node, ["--env-var", "GOOD_PY", "--env-var", "BAD_PY", str(script)], env)
    assert last_bad.returncode == 2 and "BAD_PY" in last_bad.stderr
    twice = _cli(node, ["--site", "--site", str(script)])
    assert (twice.returncode, twice.stdout.strip()) == (0, "0"), twice.stderr
    with_site = _cli(node, ["--site", str(paths)])
    assert with_site.returncode == 0 and int(with_site.stdout.strip()) >= 1, with_site.stderr
    without = _cli(node, [str(paths)])
    assert (without.returncode, without.stdout.strip()) == (0, "0"), without.stderr
