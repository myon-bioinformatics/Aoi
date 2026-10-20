"""polars_min covers research_digest.collect and matches polars on that surface.

AST sees DataFrame and col only. explode, filter, join, iter_rows, and is_not_null are checked
by running collect: once through a proxy over real polars, and once with polars absent, reading
AttributeError tracebacks. Equivalence is the fixture judgements plus the frame chain, and the
real c001 collect bytes under python -S (polars not on sys.path).
"""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

import research_digest as digest


NAGOYA = Path(__file__).resolve().parents[1]
AOI = NAGOYA.parent
CYCLE = AOI / "cycles" / "c001-chunichi"
SCRIPTS = NAGOYA / "scripts"
MIN_PATH = NAGOYA / "shrink" / "polars_min.py"
RUN_COLLECT = NAGOYA / "shrink" / "run_collect.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shrink_polars = _load("shrink_polars", SCRIPTS / "shrink_polars.py")
shrink_module = _load("shrink_module", SCRIPTS / "shrink_module.py")
run_collect = _load("run_collect", RUN_COLLECT)
polars_min = _load("polars_min_under_test", MIN_PATH)


def _run(args: list[str], *, isolated: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-S"] if isolated else [sys.executable]
    return subprocess.run(
        cmd + args, cwd=AOI, capture_output=True, text=True, check=False,
    )


def _rows(mod, links, props):
    prop = mod.DataFrame({
        "proposition_id": [key for key, _ in props],
        "exit_code": [value for _, value in props],
    })
    link = mod.DataFrame(links).explode("proposition_id").filter(
        mod.col("proposition_id").is_not_null()
    )
    return list(link.join(prop, on="proposition_id", how="left").iter_rows(named=True))


def test_ast_of_collect_sees_only_dataframe_and_col():
    used, visited = shrink_module.analyze("polars", ["research_digest.py:collect"], NAGOYA)
    assert used == Counter({"DataFrame": 2, "col": 1})
    assert "research_digest.py:collect" in visited
    survey = shrink_module.survey("polars", NAGOYA)
    assert survey["research_digest.py"] == Counter({"DataFrame": 2, "col": 1})
    production = [
        name for name in survey
        if not name.startswith(("scripts/", "tests/", "shrink/", "vendor/"))
    ]
    assert production == ["research_digest.py"]


def test_generated_file_matches_analyze_and_imports_nothing():
    proc = _run([
        str(SCRIPTS / "shrink_polars.py"), "generate",
        "--out", str(MIN_PATH), "--check",
    ])
    assert proc.returncode == 0, proc.stderr
    tree = ast.parse(MIN_PATH.read_text(encoding="utf-8"))
    assert [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))] == []
    assert polars_min.__all__ == ["DataFrame", "col"]
    assert set(shrink_polars.METHOD_SURFACE) == {
        "DataFrame.explode", "DataFrame.filter", "DataFrame.join",
        "DataFrame.iter_rows", "Expr.is_not_null",
    }


def test_proxy_trace_reads_collect_frames():
    proc = _run([str(SCRIPTS / "shrink_polars.py"), "trace"])
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert (
        "missed by ast: DataFrame.explode, DataFrame.filter, "
        "Expr.is_not_null, DataFrame.join, DataFrame.iter_rows"
    ) in proc.stdout
    for name in shrink_polars.DISCOVERY_ORDER:
        assert name in proc.stdout
    assert "research_digest.py:" in proc.stdout
    assert ":collect" in proc.stdout


def test_absent_polars_tracebacks_discover_the_same_surface():
    proc = _run([str(SCRIPTS / "shrink_polars.py"), "absent"], isolated=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    lines = [line for line in proc.stdout.splitlines() if line.startswith("step ")]
    found = [line.split("AttributeError: ", 1)[1] for line in lines]
    assert tuple(found) == shrink_polars.DISCOVERY_ORDER
    assert "discovered: " + ", ".join(shrink_polars.DISCOVERY_ORDER) in proc.stdout
    for line in proc.stdout.splitlines():
        if line.startswith("step "):
            assert "research_digest.py:" in proc.stdout
    # Every traceback step cites collect, not only the proxy.
    blocks = proc.stdout.split("step ")[1:]
    assert blocks
    for block in blocks:
        assert "research_digest.py:" in block
        assert ":collect" in block


def test_min_rejects_any_other_polars_name():
    for name in ("Series", "Expr", "LazyFrame", "read_csv", "read_ndjson", "lit", "concat", "scan_csv", "Config"):
        with pytest.raises(AttributeError):
            getattr(polars_min, name)
    frame = polars_min.DataFrame({"proposition_id": ["P1"], "exit_code": [1]})
    for name in ("select", "with_columns", "group_by", "height", "columns", "to_dicts", "unique"):
        with pytest.raises(AttributeError):
            getattr(frame, name)
    expr = polars_min.col("proposition_id")
    for name in ("is_null", "sum", "alias", "cast", "fill_null", "abs"):
        with pytest.raises(AttributeError):
            getattr(expr, name)
    with pytest.raises(TypeError):
        bool(expr)
    with pytest.raises(NotImplementedError):
        frame.join(frame, on="proposition_id", how="inner")
    with pytest.raises(NotImplementedError):
        frame.filter(polars_min.col("proposition_id"))
    with pytest.raises(NotImplementedError):
        list(frame.iter_rows())
    with pytest.raises(TypeError):
        polars_min.DataFrame({"exit_code": [1, True]})


def test_frame_chain_matches_polars():
    pl = importlib.import_module("polars")
    links = [
        {"id": "R1", "proposition_id": ["P2", "P10", "P999"]},
        {"id": "R2", "proposition_id": []},
        {"id": "R3", "proposition_id": [None, "P2"]},
    ]
    props = [("P10", 4), ("P2", 1)]
    assert _rows(polars_min, links, props) == _rows(pl, links, props)

    null_list = [
        {"id": "R1", "proposition_id": ["P1"]},
        {"id": "R2", "proposition_id": None},
    ]
    assert _rows(polars_min, null_list, [("P1", 3)]) == _rows(pl, null_list, [("P1", 3)])

    # Every list is empty, so the exploded key has no scalar type. Polars keeps dtype
    # Null and refuses to join it to a string key.
    empty = [{"id": "R1", "proposition_id": []}, {"id": "R2", "proposition_id": []}]
    for mod in (polars_min, pl):
        with pytest.raises(Exception):
            _rows(mod, empty, [("P1", 1)])

    def joined(mod):
        left = mod.DataFrame({
            "id": ["a", "b", "c"],
            "proposition_id": [None, "P1", "P1"],
        })
        right = mod.DataFrame({
            "proposition_id": [None, "P1", "P1"],
            "exit_code": [9, 1, 2],
        })
        return list(left.join(right, on="proposition_id", how="left").iter_rows(named=True))

    assert joined(polars_min) == joined(pl)
    assert joined(pl) == [
        {"id": "a", "proposition_id": None, "exit_code": None},
        {"id": "b", "proposition_id": "P1", "exit_code": 1},
        {"id": "b", "proposition_id": "P1", "exit_code": 2},
        {"id": "c", "proposition_id": "P1", "exit_code": 1},
        {"id": "c", "proposition_id": "P1", "exit_code": 2},
    ]


def test_two_note_fixture_judgements_match_polars(tmp_path):
    cycle = shrink_polars.build_fixture(tmp_path)
    notes, _, _ = digest.collect(cycle)
    by_id = {row["id"]: row["current_judgements"] for row in notes}
    assert by_id["R2"] == []
    assert by_id["R18"] == [
        {"id": "P52", "exit_code": 1},
        {"id": "P999", "exit_code": None},
    ]
    out = tmp_path / "min.json"
    proc = _run([
        str(RUN_COLLECT), "--deps", "min", "--cycle", str(cycle), str(out),
    ], isolated=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    real = run_collect.canonical(*digest.collect(cycle))
    assert out.read_bytes() == real


def test_real_cycle_collect_bytes_match_with_polars_absent_from_sys_path(tmp_path):
    if not (CYCLE / "research").is_dir():
        pytest.skip("c001 cycle is on the Aoi checkout this test runs inside")
    out = tmp_path / "min.json"
    proc = _run([str(RUN_COLLECT), "--deps", "min", str(out)], isolated=True)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert out.read_bytes() == run_collect.canonical(*digest.collect(CYCLE))
    assert "deps=min" in proc.stdout


def test_string_explode_and_short_columns_fail_like_polars():
    pl = importlib.import_module("polars")
    for mod in (pl, polars_min):
        with pytest.raises(Exception):
            mod.DataFrame({"id": ["a"], "proposition_id": ["P1"]}).explode("proposition_id")
        with pytest.raises(Exception):
            mod.DataFrame({"proposition_id": ["P1"], "exit_code": [1, 2]})
