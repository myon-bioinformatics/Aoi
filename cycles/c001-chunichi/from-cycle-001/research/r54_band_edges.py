"""R54: 帯の両端（巨人 2017年 = B の最高、巨人 2018年 = A の最低）を、その年のリーグの6球団と並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r54_band_edges.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存のチームの列だけを使う。2020年は植え替え先から除く。ネットワークを使わない。
"""

import json
import sys
from pathlib import Path

EDGES = [("g", 2017), ("g", 2018)]
EXCLUDED = {2020}
COLS = [  # (列, 見出し, 書式)。計画で先に決めた順
    ("rank", "順位", "d"), ("W", "勝", "d"), ("L", "負", "d"), ("T", "分", "d"), ("wl", "勝−負", "+d"), ("wpct", "勝率", ".3f"),
    ("lg_line", "A の線", ".3f"), ("to_line", "勝率−線", "+.3f"), ("line_gap_pythag", "点の差で線まで", "+.3f"),
    ("resid_fixed", "点の差より勝った分", "+.3f"),
    ("rf_adv", "得点の優位", "+.2f"), ("ra_adv", "失点の優位", "+.2f"), ("run_balance", "収支", "+.2f"), ("sim_p_upper", "分布から A の確率", ".2f"),
    ("wins_vs_pythag", "点の差より勝った数", "+.1f"), ("one_run_net", "1点差 勝−負", "+d"), ("alloc_z_strat", "組み合わせ方", "+.2f"),
    ("vs_top_wpct", "上の相手との勝率", ".3f"), ("vs_lower_wpct", "下の相手との勝率", ".3f"), ("pair34_net", "3位・4位の直接 勝−負", "+d"),
    ("course_wpct_h1", "前半の勝率", ".3f"), ("course_wpct_h2", "後半の勝率", ".3f"),
    ("clinch_in_x", "A 確定の位置", ".2f"), ("clinch_out_x", "B 確定の位置", ".2f"), ("decided_x", "リーグが決まった位置", ".2f"),
    ("b_paths", "道筋", "s"),
]
SHAPE = [("lg_lead_gap", "1位−2位"), ("lg_gap34", "3位−4位"), ("lg_rest_sd", "1位以外の散らばり"), ("lg_rank_at_500", ".500 の位置")]


def fmt(v, f: str) -> str:
    if v is None or v == "":
        return "-"
    return v if f == "s" else format(v, f)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    for r in rows:
        r["wl"], r["to_line"] = r["W"] - r["L"], r["wpct"] - r["lg_line"]
    leagues: dict = {}
    for r in rows:
        if r["season"] not in EXCLUDED:
            leagues.setdefault((r["season"], r["league"]), []).append(r)

    for team, season in EDGES:
        me = next(r for r in rows if (r["team"], r["season"]) == (team, season))
        lg = sorted(leagues[(season, me["league"])], key=lambda r: r["rank"])
        print(f"\n## {me['team_name']} {season}（{me['rank']}位 {me['wpct']:.3f}）\n")
        print("| 列 | " + " | ".join(f"{r['rank']}位 {r['team_name']}" for r in lg) + " |")
        print("|---|" + "---|" * len(lg))
        for col, label, f in COLS:
            print(f"| {label} | " + " | ".join(("**" + fmt(r.get(col), f) + "**") if r is me else fmt(r.get(col), f) for r in lg) + " |")
        print("\nリーグの形: " + "、".join(f"{label} {me[col]:.3f}" for col, label in SHAPE))
        print(f"恒等式: 勝率−線 {me['to_line']:+.3f} = 点の差で線まで {me['line_gap_pythag']:+.3f} + 点の差より勝った分 {me['resid_fixed']:+.3f}")

        # 植え替え: ほかのリーグ・年に置いたら
        others = [(k, v) for k, v in leagues.items() if k != (season, me["league"])]
        third = lambda v: sorted((r["wpct"] for r in v), reverse=True)[2]  # noqa: E731
        fourth = lambda v: sorted((r["wpct"] for r in v), reverse=True)[3]  # noqa: E731
        above_line = [k for k, v in others if me["wpct"] >= v[0]["lg_line"]]
        above_3rd = [k for k, v in others if me["wpct"] >= third(v)]
        below_4th = [k for k, v in others if me["wpct"] < fourth(v)]
        print(f"植え替え（ほかの {len(others)} リーグ・年）: A の線以上 {len(above_line)}、3位の勝率以上 {len(above_3rd)}、4位の勝率より下 {len(below_4th)}")
        side = above_line if not me["upper_half"] else [k for k, v in others if me["wpct"] < v[0]["lg_line"]]
        print(f"  反対側（{'A' if not me['upper_half'] else 'B'}）になる年: " + ", ".join(f"{s}{l}" for s, l in sorted(side)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
