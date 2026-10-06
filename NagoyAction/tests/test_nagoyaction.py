import json
import subprocess
import sys
from pathlib import Path

import pytest

import nagoyaction as na

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "cycles" / "c001-chunichi" / "pipeline.toml"


def write(tmp_path, text):
    p = tmp_path / "pipeline.toml"
    p.write_text(text, encoding="utf-8")
    return p


BASIC = """
name = "t"
[requires]
python = "3.11"
tools = ["git"]
optional = ["gh"]
[vars]
x = "hello"
[[step]]
name = "net"
run = ["fetch", "{x}"]
network = true
outputs = ["out.txt"]
[[step]]
name = "local"
run = ["echo", "{x}"]
"""


class Done:
    def __init__(self, rc):
        self.returncode = rc


def test_cycle_pipeline_is_valid():
    p = na.load(CYCLE)
    assert [s["name"] for s in p["step"]] == ["fetch", "observe", "inspect", "fetch_batting", "observe_batting",
                                              "inspect_batting", "fetch_fielding", "observe_fielding", "inspect_fielding",
                                              "fetch_linescore", "observe_linescore", "inspect_linescore",
                                              "measure", "question", "search", "search_r21", "sets", "judge",
                                              "fetch_2026", "preview_2026", "provisional_measure", "provisional_check"]
    assert [s["name"] for s in p["step"] if s.get("network")] == ["fetch", "fetch_batting", "fetch_fielding", "fetch_linescore", "fetch_2026"]  # 外に出るのは取得だけ
    # 守備成績は形を確かめた後に measure へ渡す（構造の確認は --strict、下の一般の確認）
    measure = next(s for s in p["step"] if s["name"] == "measure")
    assert any("npb_team_fielding" in a for a in measure["run"])
    assert any("npb_game_linescore" in a for a in measure["run"])   # 試合ごとの得点表も形を確かめた後に渡す
    names = [s["name"] for s in p["step"]]
    for s in p["step"]:  # 構造の確認は --strict で、測る前に止まれる位置にある
        if s["name"].startswith("inspect"):
            assert "--strict" in s["run"] and names.index(s["name"]) < names.index("measure")
    assert p["_root"] == ROOT
    for s in p["step"]:
        na._expand(s["run"], {k: str(v) for k, v in p["vars"].items()})  # 未定義の変数がない


@pytest.mark.parametrize("text,msg", [
    ('name="t"', "step"),
    ('[[step]]\nname="a"\nrun=["x"]\n[[step]]\nname="a"\nrun=["y"]', "一意"),
    ('[[step]]\nrun=["x"]', "一意"),
    ('[[step]]\nname="a"\nrun="echo x"', "配列"),
])
def test_invalid_pipelines(tmp_path, text, msg):
    with pytest.raises(na.PipelineError, match=msg):
        na.load(write(tmp_path, text))


def test_doctor_reports_missing_required_and_optional(tmp_path):
    p = na.load(write(tmp_path, BASIC))
    checks = {c["check"]: c["level"] for c in na.doctor(p, which=lambda t: None)}
    assert checks == {"python": "ok", "git": "fail", "gh": "warn"}


def test_doctor_offline_needs_outputs_of_network_steps(tmp_path):
    p = na.load(write(tmp_path, BASIC))
    assert {c["check"]: c["level"] for c in na.doctor(p, offline=True, which=lambda t: "/bin/" + t)}["offline:net"] == "fail"
    (tmp_path / "out.txt").write_text("x")
    assert {c["check"]: c["level"] for c in na.doctor(p, offline=True, which=lambda t: "/bin/" + t)}["offline:net"] == "ok"


def test_doctor_python_version_gate(tmp_path):
    p = na.load(write(tmp_path, BASIC.replace('python = "3.11"', 'python = "99.0"')))
    assert na.doctor(p, which=lambda t: "/x")[0]["level"] == "fail"


def test_run_expands_vars_records_receipt_and_skips_network_offline(tmp_path):
    p = na.load(write(tmp_path, BASIC))
    calls = []
    rc = na.run(p, offline=True, receipt=tmp_path / "r.jsonl",
                runner=lambda argv, cwd, check: calls.append((argv, cwd)) or Done(0))
    assert rc == 0 and calls == [(["echo", "hello"], tmp_path)]
    rec = [json.loads(line) for line in (tmp_path / "r.jsonl").read_text().splitlines()]
    assert [(r["step"], r.get("skipped", False), r.get("returncode")) for r in rec] == [("net", True, None), ("local", False, 0)]


def test_run_stops_at_first_failure(tmp_path):
    p = na.load(write(tmp_path, BASIC))
    calls = []
    assert na.run(p, runner=lambda argv, cwd, check: calls.append(argv) or Done(3)) == 3
    assert calls == [["fetch", "hello"]]


def test_only_from_and_unknown_step(tmp_path):
    p = na.load(write(tmp_path, BASIC))
    calls = []
    runner = lambda argv, cwd, check: calls.append(argv[0]) or Done(0)  # noqa: E731
    na.run(p, only=["local"], runner=runner)
    na.run(p, start="local", runner=runner)
    assert calls == ["echo", "echo"]
    with pytest.raises(na.PipelineError):
        na.run(p, only=["nope"], runner=runner)


def test_undefined_variable_is_an_error(tmp_path):
    p = na.load(write(tmp_path, BASIC.replace("{x}", "{y}")))
    with pytest.raises(na.PipelineError, match="y"):
        na.run(p, dry_run=True)


def test_cli_is_stdlib_only_and_runs_from_another_directory(tmp_path):
    # 1ファイルをコピーすれば使える: 別ディレクトリから python -S（site-packages なし）で実行できる
    out = subprocess.run([sys.executable, "-S", str(ROOT / "NagoyAction" / "nagoyaction.py"), "run",
                          str(CYCLE), "--dry-run"], capture_output=True, text=True, cwd=tmp_path)
    assert out.returncode in (0, 1), out.stderr  # 1 = 手元に uv がない環境では doctor が止める
    assert ("[dry-run] fetch" in out.stdout) or ("uv" in out.stdout and "✗" in out.stdout)


def test_optional_docker_hooks_cleanup_after_failure(monkeypatch, tmp_path):
    p = na.load(ROOT / "NagoyAction/pipelines/inbox.toml")
    monkeypatch.setenv("AOI_USE_LOCAL_LLM", "1")
    calls = []
    def runner(argv, cwd, check):
        calls.append(argv)
        return Done(9 if argv[-1] == "intake" else 0)
    assert na.run(p, runner=runner, receipt=tmp_path / "receipt.jsonl") == 9
    assert calls[-1][-1] == "down"
    assert [r["step"] for r in map(json.loads, (tmp_path / "receipt.jsonl").read_text().splitlines())] == [
        "model", "llama-start", "llama-ready", "intake", "llama-stop"]
    monkeypatch.delenv("AOI_USE_LOCAL_LLM")
    calls.clear()
    assert na.run(p, runner=runner) == 9
    assert len(calls) == 1 and calls[0][-1] == "intake"


def test_cleanup_also_runs_after_missing_executable(monkeypatch):
    p = na.load(ROOT / "NagoyAction/pipelines/inbox.toml")
    monkeypatch.setenv("AOI_USE_LOCAL_LLM", "1")
    calls = []
    def runner(argv, cwd, check):
        calls.append(argv)
        if argv[-1] == "prepare":
            raise FileNotFoundError("missing")
        return Done(0)
    assert na.run(p, runner=runner) == 127
    assert len(calls) == 2 and calls[-1][-1] == "down"
