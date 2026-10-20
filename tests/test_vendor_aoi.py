"""Vendored Aoi shrink tools match the lock, and research_digest.collect still runs.

The copies under vendor/aoi/ are byte-identical to Aoi. This tree keeps the polars
tools research_digest.collect uses, not the numpy or fetch_module tools.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

import research_digest as digest


NAGOYA = Path(__file__).resolve().parents[1]
AOI = NAGOYA.parent
CYCLE = AOI / "cycles" / "c001-chunichi"
RUN = NAGOYA / "scripts" / "collect_with_polars_min.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load("check_vendor_aoi", NAGOYA / "scripts" / "check_vendor_aoi.py")
shrink_module = _load("vendored_shrink_module", NAGOYA / "vendor" / "aoi" / "scripts" / "shrink_module.py")
shrink_polars = _load("vendored_shrink_polars", NAGOYA / "vendor" / "aoi" / "scripts" / "shrink_polars.py")
run_collect = _load("collect_with_polars_min", RUN)


def _run(args: list[str], *, isolated: bool) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-S"] if isolated else [sys.executable]
    return subprocess.run(cmd + args, capture_output=True, text=True, check=False)


def test_lock_lists_only_the_polars_tools_this_tree_uses():
    assert checker.problems(NAGOYA) == []
    document = checker.load_lock(NAGOYA)
    assert document["schema"] == "vendor-lock/1"
    assert [set(entry) for entry in document["files"]] == [
        {"path", "sha256", "source"}
    ] * len(document["files"])
    assert {entry["source"] for entry in document["files"]} == {"myon-bioinformatics/Aoi"}
    assert [entry["path"] for entry in document["files"]] == [
        "vendor/aoi/scripts/shrink_module.py",
        "vendor/aoi/scripts/shrink_polars.py",
        "vendor/aoi/shrink/polars_min.py",
    ]


def test_collect_ast_uses_dataframe_and_col():
    used, visited = shrink_module.analyze("polars", ["research_digest.py:collect"], NAGOYA)
    assert used == Counter({"DataFrame": 2, "col": 1})
    assert "research_digest.py:collect" in visited
    survey = shrink_module.survey("polars", NAGOYA)
    assert survey["research_digest.py"] == Counter({"DataFrame": 2, "col": 1})
    production = [
        name for name in survey
        if not name.startswith(("scripts/", "tests/", "vendor/"))
    ]
    assert production == ["research_digest.py"]
    for name in (
        "DataFrame.explode",
        "DataFrame.filter",
        "DataFrame.join",
        "DataFrame.iter_rows",
        "Expr.is_not_null",
    ):
        assert name in shrink_polars.METHOD_SURFACE


def test_hash_mismatch_is_reported_and_warn_exits_zero(tmp_path, capsys):
    document = checker.load_lock(NAGOYA)
    document["files"][0]["sha256"] = "0" * 64
    found = checker.problems(NAGOYA, document)
    assert any("sha256 が違う" in item for item in found)

    original = checker.load_lock

    def fake(root):
        return document

    checker.load_lock = fake
    try:
        assert checker.main(["--warn", "--root", str(NAGOYA)]) == 0
        assert checker.main(["--root", str(NAGOYA)]) == 1
    finally:
        checker.load_lock = original
    err = capsys.readouterr().err
    assert "::warning::" in err
    assert "sha256 が違う" in err


def test_upstream_byte_mismatch_is_reported(tmp_path):
    aoi = tmp_path / "aoi"
    for entry in checker.load_lock(NAGOYA)["files"]:
        relative = entry["path"].removeprefix("vendor/aoi/")
        dest = aoi / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((NAGOYA / entry["path"]).read_bytes())
    assert checker.problems(NAGOYA, aoi=aoi) == []
    target = aoi / "shrink" / "polars_min.py"
    target.write_bytes(target.read_bytes() + b"\n")
    found = checker.problems(NAGOYA, aoi=aoi)
    assert any("バイトが違う" in item for item in found)


def _fixture(tmp_path: Path) -> Path:
    cycle = tmp_path / "cycle"
    (cycle / "research").mkdir(parents=True)
    (cycle / "outputs").mkdir()
    (cycle / "research" / "R2-plain.md").write_text(
        "# R2: 表のない記録\n\n記録: 2026-10-01\n\n本文だけ。\n",
        encoding="utf-8",
    )
    (cycle / "research" / "R18-example.md").write_text(
        "# R18: 2026年での確かめ（手順の事前登録）\n\n"
        "記録: 2026-10-04。計算を始める前に書いた。\n\n"
        "## 主に見る命題と、読み方（先に決める）\n\n"
        "| 命題 | 内容 | 読み方 |\n"
        "|---|---|---|\n"
        "| **P52**（式1） | 条件 | 逆の判例が**2件以上**、判例が**3件以上** |\n"
        "| P999 | unknown | 判例を記録 |\n",
        encoding="utf-8",
    )
    (cycle / "propositions.toml").write_text('[[proposition]]\nid = "P52"\n', encoding="utf-8")
    (cycle / "outputs" / "propositions.jsonl").write_text(
        '{"id": "P52", "judgement": {"code": 1}}\n',
        encoding="utf-8",
    )
    (cycle / "FINDINGS.md").write_text("# Findings\n\nP52: exit 1\n", encoding="utf-8")
    return cycle


def test_fixture_collect_matches_polars_when_polars_is_absent(tmp_path):
    cycle = _fixture(tmp_path)
    out = tmp_path / "min.json"
    proc = _run(
        [str(RUN), "--deps", "min", "--cycle", str(cycle), str(out)],
        isolated=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert out.read_bytes() == run_collect.canonical(*digest.collect(cycle))
    payload = json.loads(out.read_text(encoding="utf-8"))
    by_id = {row["id"]: row["current_judgements"] for row in payload["notes"]}
    assert by_id["R2"] == []
    assert by_id["R18"] == [
        {"id": "P52", "exit_code": 1},
        {"id": "P999", "exit_code": None},
    ]


def test_real_cycle_collect_matches_polars_when_polars_is_absent(tmp_path):
    if not (CYCLE / "research").is_dir():
        pytest.skip("c001 cycle is on the Aoi checkout this test runs inside")
    out = tmp_path / "min.json"
    proc = _run([str(RUN), "--deps", "min", str(out)], isolated=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert out.read_bytes() == run_collect.canonical(*digest.collect(CYCLE))
    assert "deps=min" in proc.stdout
