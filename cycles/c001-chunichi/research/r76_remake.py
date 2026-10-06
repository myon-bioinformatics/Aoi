"""R76: 判例のない式と、その年の高さで作り直した式の、入る単位の入れ替わりを並べる（記述。判定は sets.md）。

    python cycles/c001-chunichi/research/r76_remake.py cycles/c001-chunichi/outputs/season.jsonl \
        cycles/c001-chunichi/propositions.toml cycles/c001-chunichi/sets.toml

season.jsonl の既存のチームの列だけを使う。2020年は除く（判定と同じ [[exclude]]）。ネットワークを使わない。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "PythDRagoras"), str(ROOT / "PythDRagoras" / "logic")]

import polars as pl
import propositions as pr
import sets as st_

EXCLUDED = {2020}
PAIRS = [("E11", "E29"), ("E13", "E30"), ("E15", "E31"), ("E26", "E32")]
SETS = [("F96", "F96B"), ("TOP_WIN", "TOP_WIN_B"), ("BAL_NONPOS", "BALG_NONPOS")]


def members(df: pl.DataFrame, item: dict) -> set[str]:
    sub = pr.scope_filter(df, item.get("scope"))
    x = sub.select("unit", x=pr._antecedent(item, sub.columns)).filter(pl.col("x").fill_null(False))
    return set(x["unit"].to_list())


def main(argv: list[str]) -> int:
    df = pl.read_ndjson(argv[0], infer_schema_length=None).filter(~pl.col("season").is_in(sorted(EXCLUDED)))
    df = df.with_columns(unit=pl.col("team") + "-" + pl.col("season").cast(pl.Utf8))
    a = {r["unit"]: r["upper_half"] for r in df.select("unit", "upper_half").iter_rows(named=True)}
    props, _ = pr.load(Path(argv[1]))
    sets, exprs, _ = st_.load_sets(Path(argv[2]), props)
    by_e = {e["id"]: st_.compile_expr(e, sets) for e in exprs}

    def tag(u):
        return f"{u}（{'A' if a[u] else 'B'}）"

    print("## 集合の入れ替わり（元 → 作り直し）\n")
    for old, new in SETS:
        mo, mn = members(df, by_e_set(sets, old)), members(df, by_e_set(sets, new))
        print(f"- {old} {len(mo)} → {new} {len(mn)}。外れた: {', '.join(map(tag, sorted(mo - mn))) or 'なし'}。"
              f"入った: {', '.join(map(tag, sorted(mn - mo))) or 'なし'}")
    print("\n## 式の入れ替わり\n")
    for old, new in PAIRS:
        mo, mn = members(df, by_e[old]), members(df, by_e[new])
        print(f"- {old} {len(mo)} → {new} {len(mn)}。外れた: {', '.join(map(tag, sorted(mo - mn))) or 'なし'}。"
              f"入った: {', '.join(map(tag, sorted(mn - mo))) or 'なし'}")
    return 0


def by_e_set(sets: dict, sid: str) -> dict:
    """集合1つを、式として読める形にする（集合の式 = その集合だけ）。"""
    return st_.compile_expr({"id": sid, "expr": sid, "statement": sid}, sets)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
