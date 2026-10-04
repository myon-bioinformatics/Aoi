"""本体のコードで、Python 3.15 ベータ + polars 1.44.2 で None を返す Series メソッドを使っていないか。

確認した範囲（2026-10-03）: Series の abs / drop_nulls / unique / mode / is_null / fill_null / round / is_in は
None を返す。DataFrame 上の式（pl.col(...).abs() など）は正常に動く。
df["col"].abs() のような書き方を見つけたら、式（df.select(pl.col("col").abs())）に書き換える。
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBPROJECTS = ["blueprobe", "queryu", "sakanalytics", "pythdragoras", "nagoyaction"]
METHODS = "abs|drop_nulls|unique|mode|is_null|fill_null|round|is_in"
# 列を取り出した直後（df["x"].abs()）にこれらを呼んでいる形
PATTERN = re.compile(rf"\]\s*\.\s*({METHODS})\s*\(")


def test_no_affected_series_methods_in_production_code():
    hits = []
    for d in SUBPROJECTS:
        for f in (ROOT / d).glob("*.py"):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if PATTERN.search(line):
                    hits.append(f"{f.relative_to(ROOT)}:{i}: {line.strip()}")
    assert hits == []


def test_guard_pattern_catches_the_known_shapes():
    assert PATTERN.search('t["alloc_z"].abs()')
    assert PATTERN.search('df["season"] .unique()')
    assert not PATTERN.search('pl.col("alloc_z").abs()')
    assert not PATTERN.search('flags.drop_nulls()')  # DataFrame のメソッドは対象外
