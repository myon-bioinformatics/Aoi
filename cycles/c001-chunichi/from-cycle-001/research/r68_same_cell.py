"""R68: 得点が下2つ × 失点が上2つのます目で、阪神の4年（A）と中日の4年（B）を比べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r68_same_cell.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import statistics
import sys
from pathlib import Path

EXCLUDED = {2020}
SCOPE = set(range(2013, 2026)) - EXCLUDED
COLS = [  # (列, 中身, 向き +1 = 大きいほどよい)。計画で先に決めた
    ("rf_adv", "得点の優位", 1), ("ra_adv", "失点の優位", 1), ("run_balance", "収支", 1), ("run_balance_t", "収支 ÷ 誤差", 1),
    ("resid_fixed", "点の差より勝った分", 1), ("wins_vs_pythag", "点の差より勝った数", 1), ("one_run_net", "1点差 勝−負", 1),
    ("alloc_z_strat", "組み合わせ方", 1), ("vs_top_wpct", "上の相手との勝率", 1), ("vs_lower_wpct", "下の相手との勝率", 1),
    ("h2_live_wl_vs_upper", "後半の効く試合 上の相手 勝−負", 1), ("h2_live_wl_vs_lower", "後半の効く試合 下の相手 勝−負", 1),
    ("lg_bar", "越えるべき高さ", -1), ("course_wpct_h1", "前半の勝率", 1), ("course_wpct_h2", "後半の勝率", 1),
    ("q_wl_4", "最後の区間 勝−負", 1), ("lock_g", "落ち着いた試合数 N", 0),
    ("inn_dlog_freq", "得点した回の頻度", 1), ("inn_dlog_size", "得点した回の大きさ", 1),
    ("bat_d_obp", "出塁率の差", 1), ("bat_d_iso", "ISO の差", 1), ("bat_d_bb_pa", "四死球／打席の差", 1), ("fld_d_e_g", "失策／試合の差", -1),
]
HANSHIN = [2013, 2019, 2021, 2022]
CHUNICHI = [2014, 2019, 2021, 2022]


def state(r, col, leagues):
    lg = sorted((x[col] for x in leagues[(r["season"], r["league"])]), reverse=True)
    v = r[col]
    return "A" if v > (lg[1] + lg[2]) / 2 else "B" if v < (lg[3] + lg[4]) / 2 else "AB"


def f(v):
    return "-" if v is None else (f"{v:+.3f}" if isinstance(v, float) else f"{v:+d}")


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    cell = [r for r in rows if state(r, "rf_adv", leagues) == "B" and state(r, "ra_adv", leagues) == "A"]
    get = lambda t, s: next(r for r in cell if (r["team"], r["season"]) == (t, s))  # noqa: E731
    h = [get("t", s) for s in HANSHIN]
    d = [get("d", s) for s in CHUNICHI]
    others = [r for r in cell if r not in h and r not in d]
    print(f"ます目の単位: {len(cell)}（A {sum(r['upper_half'] for r in cell)}）。阪神 {HANSHIN}、中日 {CHUNICHI}、"
          f"ほか: " + ", ".join(f"{r['team']}-{r['season']}({'A' if r['upper_half'] else 'B'})" for r in others))

    print("\n| 列 | 中身 | 阪神 4年 | 中日 4年 | 阪神の中央値 | 中日の中央値 | 阪神の4年すべてが中日の4年すべてよりよい |\n|---|---|---|---|---|---|---|")
    split = []
    for col, label, sign in COLS:
        hv, dv = [r.get(col) for r in h], [r.get(col) for r in d]
        if None in hv + dv:
            print(f"| `{col}` | {label} | " + " ".join(map(f, hv)) + " | " + " ".join(map(f, dv)) + " | - | - | - |")
            continue
        all_better = sign and min(sign * x for x in hv) > max(sign * y for y in dv)
        if all_better:
            split.append(col)
        print(f"| `{col}` | {label} | " + " ".join(map(f, hv)) + " | " + " ".join(map(f, dv))
              + f" | {f(statistics.median(hv))} | {f(statistics.median(dv))} | {'**4対0**' if all_better else ''} |")
    print("\n4対0で分かれた列: " + (", ".join(split) or "なし"))

    print("\n| 同じ年の差（阪神 − 中日） | " + " | ".join(str(s) for s in (2019, 2021, 2022)) + " | 3年とも阪神がよい |\n|---|---|---|---|---|")
    same = []
    for col, label, sign in COLS:
        diffs = [get("t", s).get(col) - get("d", s).get(col) if None not in (get("t", s).get(col), get("d", s).get(col)) else None
                 for s in (2019, 2021, 2022)]
        if None in diffs:
            continue
        ok = sign and all(sign * x > 0 for x in diffs)
        if ok:
            same.append(col)
        print(f"| {label} | " + " | ".join(f(x) for x in diffs) + f" | {'はい' if ok else ''} |")
    print("\n同じ年の3組で、3年とも阪神がよい列: " + (", ".join(same) or "なし"))

    print("\n候補の列で、ほかの単位（西武 2022年とます目の残りの B）がどちら側か（阪神の最低・中日の最高と比べる）:")
    for col in sorted(set(split) | set(same)):
        sign = next(s for c, _, s in COLS if c == col)
        hmin, dmax = min(sign * r[col] for r in h), max(sign * r[col] for r in d)
        print(f"  {col}: " + ", ".join(
            f"{r['team']}-{r['season']}({'A' if r['upper_half'] else 'B'}) {r[col]:+.3f}"
            f"→{'阪神側' if sign * r[col] >= hmin else '中日側' if sign * r[col] <= dmax else '間'}" for r in others))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
