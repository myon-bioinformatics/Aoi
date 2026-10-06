"""本体のコードで、Python 3.15 ベータ + polars 1.44.2 で None を返す Series メソッドを使っていないか。

確認した範囲（2026-10-03）: Series の abs / drop_nulls / unique / mode / is_null / fill_null / round / is_in は
None を返す。DataFrame 上の式（pl.col(...).abs() など）は正常に動く。
df["col"].abs() のような書き方を見つけたら、式（df.select(pl.col("col").abs())）に書き換える。
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBPROJECTS = ["BlueProbe", "QueRyu", "SakAnalytics", "PythDRagoras", "NagoyAction"]


def production_files(d):
    """サブプロジェクトの本体の .py（トップのメインファイルと、用途のフォルダの中。tests/ は除く）。"""
    return [f for f in sorted((ROOT / d).rglob("*.py")) if "tests" not in f.relative_to(ROOT / d).parts]
METHODS = "abs|drop_nulls|unique|mode|is_null|fill_null|round|is_in"
# 列を取り出した直後（df["x"].abs()）にこれらを呼んでいる形
PATTERN = re.compile(rf"\]\s*\.\s*({METHODS})\s*\(")


def test_no_affected_series_methods_in_production_code():
    hits = []
    for d in SUBPROJECTS:
        for f in production_files(d):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if PATTERN.search(line):
                    hits.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")
    assert hits == []


def test_guard_pattern_catches_the_known_shapes():
    assert PATTERN.search('t["alloc_z"].abs()')
    assert PATTERN.search('df["season"] .unique()')
    assert not PATTERN.search('pl.col("alloc_z").abs()')
    assert not PATTERN.search('flags.drop_nulls()')  # DataFrame のメソッドは対象外


def test_ndjson_reads_infer_the_schema_from_every_row(tmp_path):
    """season.jsonl の取得した年だけ埋まる列（ls_* は 2025年だけ）は、最初の100行が空。型を最初の行から推測すると止まる
    （2026-10-05、Actions の question で ComputeError）。本体のコードの read_ndjson は infer_schema_length=None で読む。"""
    import polars as pl

    hits = []
    for d in SUBPROJECTS:
        for f in production_files(d):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if "pl.read_ndjson(" in line and "infer_schema_length=None" not in line:
                    hits.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")
    assert hits == []
    # 止まった形の再現: 101行の空のあとに値
    p = tmp_path / "s.jsonl"
    p.write_text("".join('{"x":null}\n' for _ in range(101)) + '{"x":-0.05}\n', encoding="utf-8")
    assert pl.read_ndjson(p, infer_schema_length=None)["x"].to_list()[-1] == -0.05
