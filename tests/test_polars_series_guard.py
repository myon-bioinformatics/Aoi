"""本体のコードで、列を取り出した直後に Series メソッドを繋いでいないか。

Python 3.15 ベータ + polars 1.44.2 では Series の abs / drop_nulls / unique / mode / is_null /
fill_null / round / is_in が None を返した。polars 2.0.0 + Python 3.15.0 では同じ呼び出しは Series を返す。
DataFrame 上の式（pl.col(...).abs() など）はどちらの版でも同じ結果なので、その書き方のままにする。
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
