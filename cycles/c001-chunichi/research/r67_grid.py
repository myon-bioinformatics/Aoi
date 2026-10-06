"""R67: 独自の指標の4種類の線（r66 を使い回す）、得点 × 失点の状態の組、中日の4年と阪神 2015年（記述。判定はしない）。

    python cycles/c001-chunichi/research/r67_grid.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import r66_indicator_lines as r66  # noqa: E402

OWN = [  # (列, 中身, 向き, 中立)。計画で先に決めた
    ("sim_p_upper", "分布から見た A の確率", 1, 0.5), ("run_balance_t", "収支 ÷ 誤差", 1, 0.0),
    ("rf_def_total", "得点の不足", 1, 0.0), ("inn_dlog_freq", "得点した回の割合の差", 1, 0.0),
    ("inn_dlog_size", "得点した回の平均得点の差", 1, 0.0),
    ("opp_conv_top", "上の相手で点の差より勝った分", 1, 0.0), ("opp_conv_mid", "中の相手で同じ", 1, 0.0),
    ("opp_conv_low", "下の相手で同じ", 1, 0.0), ("q_wl_4", "最後の区間の勝−負", 1, 0.0),
    ("h2_live_wpct", "後半の効く試合の勝率", 1, 0.5), ("lg_bar", "越えるべき高さ", -1, 0.5),
    ("wave_limit_rank_h1", "前半の線の行き先（順位）", -1, 3.5),
]
EXCLUDED = {2020}
SCOPE = set(range(2013, 2026)) - EXCLUDED
CASES = [("d", 2014), ("d", 2015), ("d", 2018), ("d", 2019), ("t", 2015)]


def state(r, col, leagues):
    lg = sorted((x[col] for x in leagues[(r["season"], r["league"])]), reverse=True)
    v = r[col]
    return "A" if v > (lg[1] + lg[2]) / 2 else "B" if v < (lg[3] + lg[4]) / 2 else "AB"


def main(argv: list[str]) -> int:
    print("## 1. 独自の指標の4種類の線\n")
    r66.main([argv[0]], indicators=OWN)

    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE | {2012}]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    target = [r for r in rows if r["season"] in SCOPE]
    for r in rows:
        r["s_rf"], r["s_ra"] = state(r, "rf_adv", leagues), state(r, "ra_adv", leagues)

    print("\n## 2. 得点の側（行）× 失点の側（列）: 最後に A / 単位\n")
    print("| 得点 ＼ 失点 | A | AB | B |\n|---|---|---|---|")
    for a in ("A", "AB", "B"):
        cells = []
        for b in ("A", "AB", "B"):
            xs = [r for r in target if r["s_rf"] == a and r["s_ra"] == b]
            cells.append(f"{sum(r['upper_half'] for r in xs)}/{len(xs)}")
        print(f"| {a} | " + " | ".join(cells) + " |")
    d = [r for r in target if r["team"] == "d" and not r["upper_half"]]
    print("\n中日の B 12年の組: " + "、".join(f"{k}: {v}" for k, v in sorted(Counter(f"得点{r['s_rf']}×失点{r['s_ra']}" for r in d).items())))
    print("  " + "、".join(f"{r['season']} 得点{r['s_rf']}×失点{r['s_ra']}" for r in sorted(d, key=lambda r: r["season"])))

    print("\n## 3. 中日の4年と阪神 2015年\n")
    print("| 単位 | 順位 | 得点 × 失点 | 収支 | 収支 ÷ 誤差 | 点の差より勝った分 | 越えるべき高さ | 最後の区間 勝−負 | 勝率 |\n|---|---|---|---|---|---|---|---|---|")
    for t, s in CASES:
        r = next(x for x in target if (x["team"], x["season"]) == (t, s))
        same = [x for x in target if x["s_rf"] == r["s_rf"] and x["s_ra"] == r["s_ra"]]
        print(f"| {t}-{s} | {r['rank']} | {r['s_rf']}×{r['s_ra']}（同じ組で A {sum(x['upper_half'] for x in same)}/{len(same)}） "
              f"| {r['run_balance']:+.2f} | {r['run_balance_t']:+.2f} | {r['resid_fixed']:+.3f} | {r['lg_bar']:.3f} | {r['q_wl_4']:+d} | {r['wpct']:.3f} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
