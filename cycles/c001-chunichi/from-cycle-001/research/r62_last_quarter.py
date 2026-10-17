"""R62: 3/4 で3〜4位から最後の区間で何が分けたか、行き先の出ない線、決まった区切りでの比べ（記述。判定はしない）。

    python cycles/c001-chunichi/research/r62_last_quarter.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

EXCLUDED = {2020}
FOCUS, FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED
MEASURES = [  # (列, 中身, A らしい向き: +1 = A が大きい, −1 = A が小さい, 0 = 決めない)。計画で先に決めた
    ("q4_rd_g", "最後の区間の点の差/試合", 1), ("q4_one_run_net", "最後の区間の1点差 勝−負", 1),
    ("q4_wl_vs_upper", "最後の区間の上の相手 勝−負", 1), ("q4_wl_vs_lower", "最後の区間の下の相手 勝−負", 1),
    ("q4_live_g", "最後の区間の効く試合", 0), ("lg_bar", "越えるべき高さ", -1), ("fld_d_e_g", "失策の差（シーズン合計）", -1),
]


def share(a, b, sign):
    pairs = [(x, y) for x in a for y in b]
    return sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs) / len(pairs)


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def f(v, spec):
    return "-" if v is None else format(v, spec)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    for r in rows:
        r["q4_live_g"] = max(0, r["q4_g"] - r["dead_g"])
    mid = [r for r in rows if 3 <= r["course_rank_q3"] <= 4]
    ma, mb = [r for r in mid if r["upper_half"]], [r for r in mid if not r["upper_half"]]

    print(f"## 1. 3/4 で3〜4位の {len(mid)} 単位（最後 A {len(ma)}・B {len(mb)}）\n")
    print("| 列 | 中身 | A らしい向きの組の割合 | A の中央値 | B の中央値 |\n|---|---|---|---|---|")
    for col, label, sign in MEASURES:
        av, bv = [r[col] for r in ma if r[col] is not None], [r[col] for r in mb if r[col] is not None]
        sh = f"{share(av, bv, sign):.2f}" if sign else "（向きなし）"
        print(f"| `{col}` | {label} | {sh} | {med(av):+.2f} | {med(bv):+.2f} |")
    cols = ["q4_rd_g", "q4_one_run_net", "q4_wl_vs_upper", "q4_wl_vs_lower", "q4_live_g", "lg_bar", "fld_d_e_g", "q_wl_4"]
    print("\n| 単位 | 最後 | " + " | ".join(cols) + " |\n|---|---|" + "---|" * len(cols))
    for r in sorted((r for r in mid if r["team"] in ("d", "db")), key=lambda r: (r["team"], r["season"])):
        print(f"| {r['team']}-{r['season']} | {'A' if r['upper_half'] else 'B'} | " + " | ".join(
            f(r[c], "+.2f" if isinstance(r[c], float) else "+d") for c in cols) + " |")

    print("\n## 2. 前半の線の行き先が出ない単位\n")
    no = [r for r in rows if r.get("wave_limit_rank_h1") is None]
    yes = [r for r in rows if r.get("wave_limit_rank_h1") is not None]
    for name, xs in (("出ない", no), ("出る", yes)):
        print(f"- {name} {len(xs)}: A {sum(r['upper_half'] for r in xs)}・B {sum(not r['upper_half'] for r in xs)}、"
              f"最後の順位 {dict(sorted(Counter(r['rank'] for r in xs).items()))}、全体の行き先あり {sum(r.get('wave_limit_rank') is not None for r in xs)}、"
              f"波あり {sum(bool(r.get('wave_osc')) for r in xs)}、減衰の中央値 {f(med([r.get('wave_decay') for r in xs]), '.2f')}、"
              f"N の中央値 {f(med([r['lock_g'] for r in xs]), '.0f')}")
    print("  中日: " + "、".join(f"{r['season']}（{r['rank']}位）" for r in no if r["team"] == FOCUS))

    print("\n## 3. 決まった区切りでの比べ\n")
    d = [r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]]
    ob = [r for r in rows if not r["upper_half"] and r["team"] != FOCUS]
    print("| 群 | 後半 − 前半の勝率 | 区間1 | 区間2 | 区間3 | 区間4 |\n|---|---|---|---|---|---|")
    for name, xs in (("A", [r for r in rows if r["upper_half"]]), ("B", [r for r in rows if not r["upper_half"]]),
                     ("中日以外の B", ob), ("中日の B", d)):
        print(f"| {name}（{len(xs)}） | {med([r['course_wpct_diff'] for r in xs]):+.3f} | "
              + " | ".join(f"{med([r[f'q_wl_{k}'] for r in xs]):+.1f}" for k in range(1, 5)) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
