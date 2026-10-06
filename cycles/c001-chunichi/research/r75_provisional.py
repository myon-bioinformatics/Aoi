"""R74: 2026年の暫定データ（消化した試合だけ）で、結果を見た後に立てた命題と式を判定する（記述）。

    python cycles/c001-chunichi/research/r75_provisional.py cycles/c001-chunichi/outputs/provisional/season.jsonl \
        cycles/c001-chunichi/propositions.toml cycles/c001-chunichi/sets.toml --out cycles/c001-chunichi/outputs/provisional/check.md

2026年の12単位だけで判定する。暫定なので、全日程の後に R18 の手順でもう一度判定する。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "PythDRagoras"), str(ROOT / "PythDRagoras" / "logic")]

import polars as pl  # noqa: E402
import propositions as pr  # noqa: E402
import sets as st_  # noqa: E402

SEASON = 2026
PROPS = [f"P{i}" for i in range(181, 211)]
EXPRS = ["E11", "E13", "E15", *(f"E{i}" for i in range(19, 33))]   # R76: 判例のない式と、その作り直し


def cell(v):
    return "-" if v is None else str(v)


def classify(flags):
    unknown = flags.filter(pl.col("x").is_null() | pl.col("y").is_null())
    known = flags.filter(pl.col("x").is_not_null() & pl.col("y").is_not_null())
    ins = known.filter(pl.col("x"))
    hold = ins.filter(pl.col("y"))
    cx = ins.filter(~pl.col("y"))["team"].to_list()
    dx = flags.filter(pl.col("team") == "d").rows(named=True)
    d = "-" if not dx else "判定不能" if dx[0]["x"] is None or dx[0]["y"] is None else "入る" if dx[0]["x"] else "入らない"
    return ins.height, hold.height, sorted(cx), unknown.height, d


def main(argv: list[str]) -> int:
    import contextlib
    import io

    if "--out" in argv:
        i = argv.index("--out")
        out, argv = Path(argv[i + 1]), argv[:i] + argv[i + 2:]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(argv)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(buf.getvalue(), encoding="utf-8")
        print(buf.getvalue())
        return code
    season, props_path, sets_path = map(Path, argv[:3])
    df = pl.read_ndjson(season, infer_schema_length=None)
    d26 = df.filter(pl.col("season") == SEASON)
    props, _ = pr.load(props_path)
    by_id = {p["id"]: p for p in props}
    sets, exprs, _ = st_.load_sets(sets_path, props)
    print(f"# 2026年の暫定の判定（消化した試合だけ、{d26.height} 単位）\n")
    print("暫定。R18 の手順（全球団が143試合を終えてから）で取り込んだ後、もう一度判定する。\n")
    print("| 球団 | 試合 | 勝率 | 順位 | A |\n|---|---|---|---|---|")
    for r in d26.sort("league", "rank").iter_rows(named=True):
        print(f"| {r['team_name']} | {r['G']} | {r['wpct']:.3f} | {r['rank']} | {'A' if r['upper_half'] else 'B'} |")

    def judge_rows(items):
        print("\n| id | 前件に入った | 後件も当たり | 判例 | 判定不能 | 中日 |\n|---|---|---|---|---|---|")
        for p in items:
            try:
                sub = pr.scope_filter(d26, p.get("scope"))
                flags = sub.select("team", x=pr._antecedent(p, sub.columns), y=pr._cond(p["then"], sub.columns))
                scope = p.get("scope") or {}
                if scope.get("where"):
                    base = pr.scope_filter(d26, {k: v for k, v in scope.items() if k != "where"})
                    unknown_scope = base.filter(pr._cond(scope["where"], base.columns).is_null())
                    flags = pl.concat([flags, unknown_scope.select("team", x=pl.lit(None, dtype=pl.Boolean), y=pl.lit(None, dtype=pl.Boolean))])
            except Exception as e:  # noqa: BLE001  列がない（暫定で測れない列）なども記録する
                print(f"| {p['id']} | 判定できない: {type(e).__name__} | | | | |")
                continue
            n, hold, cx, unknown, d = classify(flags)
            print(f"| {p['id']} | {n} | {hold} | {', '.join(cx) or 'なし'} | {unknown} | {d} |")

    print("\n## 命題（P181〜P210）")
    judge_rows([by_id[i] for i in PROPS if i in by_id])
    print("\n## 式（E11・E13・E15・E19〜E32）")
    judge_rows([st_.compile_expr(e, sets) for e in exprs if e["id"] in EXPRS])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
