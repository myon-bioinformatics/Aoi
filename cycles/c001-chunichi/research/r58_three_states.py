"""R58: 2本の線で3つの状態（A・AB・B）と、時期をまたぐ動き（記述。判定はしない）。

    python cycles/c001-chunichi/research/r58_three_states.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の wpct・live_wpct・upper_half・course_rank_* だけを使う。線は1年抜き（自分の年を除いたほかの年）。2020年は除く。
"""

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r53_line_catalog import jenks_lines  # noqa: E402

EXCLUDED = {2020}
FOCUS, FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def band(pool, col):
    a = [r[col] for r in pool if r["upper_half"] and r[col] is not None]
    b = [r[col] for r in pool if not r["upper_half"] and r[col] is not None]
    return min(a), max(b)


SCHEMES = [  # (名前, 値の列, 線を引く関数)。計画で先に決めた
    ("帯", "wpct", lambda pool: band(pool, "wpct")),
    ("塊3", "wpct", lambda pool: tuple(jenks_lines([r["wpct"] for r in pool], 3))),
    ("三分位", "wpct", lambda pool: tuple(statistics.quantiles([r["wpct"] for r in pool], n=3, method="inclusive"))),
    ("平均±SD", "wpct", lambda pool: (statistics.mean(w := [r["wpct"] for r in pool]) - statistics.stdev(w),
                                      statistics.mean(w) + statistics.stdev(w))),
    ("効く試合の帯", "live_wpct", lambda pool: band(pool, "live_wpct")),
]


def state_of(v, lo, hi):
    return "B" if v < lo else "A" if v > hi else "AB"


def rank_state(k):
    return "A" if k <= 2 else "AB" if k <= 4 else "B"   # 2.5位と 4.5位の2本の線


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    seasons = sorted({r["season"] for r in rows})
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    unit = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731

    print("## 1. 2本の線で3つの状態\n")
    print("| 組 | 線（中央値） | A の状態: A / 計 | AB の状態: A / 計 | B の状態: B / 計 | 中日の B（A・AB・B） |\n|---|---|---|---|---|---|")
    states = {}
    for name, col, lines in SCHEMES:
        cut = {s: lines([r for r in rows if r["season"] != s]) for s in seasons}
        st = {unit(r): state_of(r[col], *cut[r["season"]]) for r in rows}
        states[name] = st
        c = Counter((st[unit(r)], r["upper_half"]) for r in rows)
        dd = Counter(st[unit(r)] for r in d)
        lo, hi = statistics.median(v[0] for v in cut.values()), statistics.median(v[1] for v in cut.values())
        print(f"| {name} | {lo:.3f}〜{hi:.3f} | {c[('A', True)]}/{c[('A', True)] + c[('A', False)]} "
              f"| {c[('AB', True)]}/{c[('AB', True)] + c[('AB', False)]} | {c[('B', False)]}/{c[('B', True)] + c[('B', False)]} "
              f"| {dd['A']}・{dd['AB']}・{dd['B']} |")
        if name == "効く試合の帯":
            print("\n効く試合の帯の年ごとの線: " + "、".join(f"{s} {v[0]:.3f}〜{v[1]:.3f}" for s, v in cut.items()))
            wrong = [f"{unit(r)}（{r['rank']}位 {r['live_wpct']:.3f}）" for r in rows
                     if (st[unit(r)] == "A" and not r["upper_half"]) or (st[unit(r)] == "B" and r["upper_half"])]
            print(f"状態と最後が食い違う単位: {', '.join(wrong) or 'なし'}")
            moved = [f"{unit(r)}（全試合 {states['帯'][unit(r)]} → 効く試合 {st[unit(r)]}）" for r in rows
                     if states["帯"][unit(r)] != st[unit(r)]]
            print(f"全試合の帯と状態が変わった単位 {len(moved)}: {', '.join(moved)}")
            for t, s in (("g", 2017), ("g", 2018), ("t", 2015)):
                r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
                print(f"  {t}-{s}: 全試合 {r['wpct']:.3f}（{states['帯'][unit(r)]}）、効く試合 {r['live_wpct']:.3f}（{st[unit(r)]}）")

    print("\n## 2. 時期をまたぐ動き（順位の 2.5位・4.5位の線）\n")
    print("| 時点 | A の状態 → 最後 A | AB の状態 → 最後 A | B の状態 → 最後 A |\n|---|---|---|---|")
    for col, label in (("course_rank_q1", "1/4"), ("course_rank_h1", "1/2"), ("course_rank_q3", "3/4")):
        c = Counter((rank_state(r[col]), r["upper_half"]) for r in rows)
        print(f"| {label} | " + " | ".join(f"{c[(s, True)]}/{c[(s, True)] + c[(s, False)]}" for s in ("A", "AB", "B")) + " |")
    print("\n| 1/2 の時点の順位 | 1 | 2 | 3 | 4 | 5 | 6 |\n|---|---|---|---|---|---|---|")
    c = Counter((r["course_rank_h1"], r["upper_half"]) for r in rows)
    print("| 最後 A / 計 | " + " | ".join(f"{c[(k, True)]}/{c[(k, True)] + c[(k, False)]}" for k in range(1, 7)) + " |")

    path = lambda r: " → ".join(rank_state(r[c]) for c in ("course_rank_q1", "course_rank_h1", "course_rank_q3")) \
        + f" ⇒ {'A' if r['upper_half'] else 'B'}"  # noqa: E731
    paths = Counter(path(r) for r in rows)
    print("\n動きの型（多い順）: " + "、".join(f"{p}: {n}" for p, n in paths.most_common()))
    print("\n中日の B 12年: " + "、".join(f"{r['season']} {path(r)}" for r in d))
    a_to_b = [r for r in rows if not r["upper_half"] and "A" in [rank_state(r[c]) for c in ("course_rank_q1", "course_rank_h1", "course_rank_q3")]]
    print(f"\nA の状態を通って B で終わった（A から B）: {len(a_to_b)} 単位: " + ", ".join(f"{unit(r)}（{path(r)}）" for r in a_to_b))
    b_to_a = [r for r in rows if r["upper_half"] and "B" in [rank_state(r[c]) for c in ("course_rank_q1", "course_rank_h1", "course_rank_q3")]]
    print(f"B の状態を通って A で終わった（B から A）: {len(b_to_a)} 単位: " + ", ".join(f"{unit(r)}（{path(r)}）" for r in b_to_a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
