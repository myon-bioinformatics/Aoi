"""🌐 Fleet contracts through the parent's shared checks (vendor/fleet_check.py): vendor lock, parent pins, CI jobs,
Node entries through the vendored py_launch.cjs, the launcher contract and the benchmark -O guard.

共通の検査（ロックのバイト列・親のピン・ジョブの本文・Node 26 の解決・Node と Python の一致・ランチャーの契約・
アクションのピン・vendor-dispatch の中身・ベンチマークの -O ガード）は親の vendor/fleet_check.py を呼ぶ。
ここに残すのは、このリポジトリの期待値（ピン・ツール・ケース・文言）だけ。

Node entry: `node vendor/py_launch.cjs --env-var <TOOL>_PYTHON -- npb/<tool>.py ARGS` (no per-tool wrapper).
"""
from __future__ import annotations
import sys
import unittest

import importlib.util, json
from pathlib import Path

import pytest


def load_vendored(name, relpath):
    """Load a vendored file by path under a repo-unique name (cli_args README: Loading a vendored copy)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / relpath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


ROOT = Path(__file__).resolve().parents[1]
# Aoi は子をまとめて 1 回の pytest で動かす。トップの vendor パッケージは子どうしでぶつかるので、場所から固有の名前で読む
fleet = load_vendored("sakanalytics_fleet_check", "vendor/fleet_check.py")

PARENT_WORKFLOW_PIN = "27dedd9651efc816fa88d8922adb5f242725df69"
ACCEPTED = {
    "vendor/cli_args.py": "5ae22b1a1b808eca93e3c385a8db867fbeb8ee32",
    "vendor/py_launch.cjs": "9e0147a17695ce63fa73daf75d8195a4f49095bb",
    "vendor/fleet_check.py": "eee8c096fc753465a5d5a26264e64c12e555638f",
}
ACTION_PINS = {
    "actions/setup-node": "949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0",
    "astral-sh/setup-uv": "68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3",
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2",
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


# ==== action pins: 親の reusable workflow は 40 桁 SHA、ほかは SHA と版のコメント（ここの表と一字一句同じ）

def test_all_actions_are_pinned_to_reviewed_shas():
    used = {action for action, _sha, version in fleet.check_actions(ROOT, ACTION_PINS) if version}
    assert used == set(ACTION_PINS)


# ==== CI のジョブ: vendor-dispatch は vendor.lock.json の検証のまま、test は pytest の前に Node 26 を入れる

def test_vendor_dispatch_verifies_the_lock_behind_the_node_floor():
    # 親のリポジトリ ID・ls-remote・--manifest vendor.lock.json（--record と -S は無し）と、bash の Node ガードを 24〜27 で実行
    fleet.workflow_job(ROOT, "vendor-dispatch", node_floor=26, dispatch_lock="vendor.lock.json")


AT = chr(64)


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
    # 無いインタープリタは終了コード 2、argv・stdin・終了コードは -S のまま素通し、探索でも sitecustomize を読まない。
    # ライブラリの resolvePython / run / main のフラグと、両方向のシグナル（直接・繰り返し、text・JSON）も親が見る
    fleet.launcher_contract(ROOT, _env_var(tool))


# ==== -O ガード（旧 test_neighbor_retention.py の BenchmarkGuardTests）: assert を外す -O でも不一致の検査が効く

def test_benchmark_mismatch_exits_under_optimization_without_reporting_success():
    patch = ("g['subprocess'].check_output = lambda *args, **kwargs: b'def discover(rows): return {\"reference\": True}'\n"
             "g['neighbors'].discover = lambda rows: {}")
    result = fleet.run_main(ROOT, BENCHMARK, patch, optimized=True, timeout=30)
    assert result.returncode != 0, result.stdout
    assert "report mismatch" in result.stderr
    assert result.stdout == ""


# 🧰 Scripts: 📝 each one describes itself and ⌨️ one that reads sys.argv declares its arguments (argparse /
# cli_args). Read with ast, never run; the portfolio's script catalog reads the same facts.

class ScriptsDescribeThemselves(unittest.TestCase):
    def test_every_script_has_a_description_and_declared_arguments(self):
        fleet.check_scripts(fleet.repo_root(__file__))

    def test_pull_request_ci_stays_quick(self):
        # ⏱ push limited to branches, superseded PR runs cancelled, every job timed (fleet_check.check_ci)
        fleet.check_ci(fleet.repo_root(__file__))

    def test_root_scripts_import_only_the_standard_library(self):
        root = fleet.repo_root(__file__)
        for path in sorted(root.glob("*.py")):
            if path.name != "conftest.py":
                fleet.check_imports(root, path.name)

    def test_no_top_level_vendor_package_imports(self):
        assert fleet.check_no_vendor_package_imports(ROOT) == []
