"""R66: 順位ではなく指標の値に線を引き、A・AB・B に分ける（記述。判定はしない）。

    python cycles/c001-chunichi/research/r66_indicator_lines.py cycles/c001-chunichi/outputs/season.jsonl [--season 2012]

範囲は 2013〜2025年（2020年を除く）。--season を付けると、その年だけを確かめる（帯はほかの年から引く）。
"""

import argparse
import json
import statistics
from pathlib import Path

EXCLUDED = {2020}
SCOPE = set(range(2013, 2026)) - EXCLUDED
FOCUS = "d"
INDICATORS = [  # (列, 中身, 向き +1/−1, 中立の値 or None)。計画で先に決めた
    ("rf_g", "得点／試合", 1, None), ("ra_g", "失点／試合", -1, None),
    ("rf_adv", "得点の優位", 1, 0.0), ("ra_adv", "失点の優位", 1, 0.0), ("run_balance", "収支", 1, 0.0),
    ("pythag_fixed", "点の差で見込む勝率", 1, 0.5), ("resid_fixed", "点の差より勝った分", 1, 0.0),
    ("one_run_net", "1点差 勝−負", 1, 0.0), ("alloc_z_strat", "組み合わせ方", 1, 0.0),
    ("bat_d_obp", "出塁率の差", 1, 0.0), ("bat_d_slg", "長打率の差", 1, 0.0), ("bat_d_iso", "ISO の差", 1, 0.0),
    ("bat_d_bb_pa", "四死球／打席の差", 1, 0.0), ("bat_d_so_pa", "三振／打席の差", -1, 0.0),
    ("bat_d_r_runner", "走者あたり得点の差", 1, 0.0),
    ("fld_d_e_g", "失策／試合の差", -1, 0.0), ("fld_d_fpct", "守備率の差", 1, 0.0),
    ("vs_top_wpct", "上の相手との勝率", 1, 0.5), ("vs_lower_wpct", "下の相手との勝率", 1, 0.5),
    ("course_wpct_h1", "前半の勝率", 1, 0.5),
    ("wpct", "（基準）勝率", 1, 0.5),
]
OWN = [  # R67: このプロジェクトで作った独自の指標（向きと中立の値は R67 の計画で先に決めた）
    ("sim_p_upper", "分布から見た A の確率（R10）", 1, 0.5), ("run_balance_t", "収支 ÷ 誤差（R39）", 1, 0.0),
    ("rf_adv_t", "得点の優位 ÷ 誤差", 1, 0.0), ("ra_adv_t", "失点の優位 ÷ 誤差", 1, 0.0),
    ("rf_def_total", "得点の不足（帯の合計、R3）", 1, 0.0), ("short_share", "不足の取り分（R32）", -1, 0.5),
    ("line_gap_pythag", "点の差で A の線まで（R50）", 1, 0.0), ("lg_bar", "越えるべき高さ（R56、外）", -1, 0.5),
    ("wins_vs_pythag", "点の差より勝った数", 1, 0.0), ("alloc_z", "組み合わせ方（全体、R1）", 1, 0.0),
    ("opp_conv_top", "上の相手で点の差より勝った分", 1, 0.0), ("opp_conv_mid", "中位の相手で同じ", 1, 0.0),
    ("opp_conv_low", "下の相手で同じ", 1, 0.0), ("inn_dlog_freq", "得点した回の頻度（R4）", 1, 0.0),
    ("inn_dlog_size", "得点した回の大きさ（R4）", 1, 0.0), ("half1_vs_pythag", "前半に点の差より勝った数", 1, 0.0),
    ("course_wpct_diff", "後半 − 前半の勝率（R20）", 1, 0.0), ("series_lost_pct", "負け越したカードの多さ（R24）", -1, 0.5),
    ("max_lose_streak", "最長連敗", -1, None), ("q4_rd_g", "最後の区間の点の差（R62）", 1, 0.0),
    ("h2_live_rd_g", "後半の効く試合の点の差（R64）", 1, 0.0), ("vs_battle_wpct", "競り合う相手との勝率", 1, 0.5),
    ("wpct", "（基準）勝率", 1, 0.5),
]


def mid(a, b):
    return (a + b) / 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("season_jsonl", type=Path)
    ap.add_argument("--season", type=int, help="この年だけを確かめる（2012 など）")
    ap.add_argument("--set", choices=["base", "own"], default="base", help="base = R66 の20指標、own = R67 の独自指標")
    args = ap.parse_args(argv)
    indicators = OWN if args.set == "own" else INDICATORS
    rows = [json.loads(line) for line in args.season_jsonl.read_text(encoding="utf-8").splitlines()]
    for r in rows:
        r["rf_g"], r["ra_g"] = r["RF"] / r["G"], r["RA"] / r["G"]
    pool_all = [r for r in rows if r["season"] in SCOPE]
    target = [r for r in rows if r["season"] not in EXCLUDED and (r["season"] == args.season if args.season else r["season"] in SCOPE)]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    d = sorted((r for r in target if r["team"] == FOCUS and not r["upper_half"]), key=lambda r: r["season"])
    print(f"範囲: {len(target)} 単位（{'その年 ' + str(args.season) if args.season else '2013〜2025年、2020年を除く'}）、中日の B {len(d)}年\n")

    print("| 指標 | 3.5位の線で一致 | 中立の線で一致 | 2本線: A→A | AB→A | B→B | 帯の幅（AB の単位） | 帯: A→A・B→B | 中日の B: 2本線で B | 帯の下 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    out = []
    for col, label, sign, neutral in indicators:
        rs = [r for r in target if r.get(col) is not None]
        if not rs:
            continue
        agree35 = agreeN = 0
        st2, stb = {}, {}
        for r in rs:
            lg = sorted((sign * x[col] for x in leagues[(r["season"], r["league"])] if x.get(col) is not None), reverse=True)
            v = sign * r[col]
            if len(lg) >= 5:
                l35, l25, l45 = mid(lg[2], lg[3]), mid(lg[1], lg[2]), mid(lg[3], lg[4])
                agree35 += (v > l35) == bool(r["upper_half"])
                st2[id(r)] = "A" if v > l25 else "B" if v < l45 else "AB"
            if neutral is not None:
                agreeN += (v > sign * neutral) == bool(r["upper_half"])
            other = [x for x in pool_all if x["season"] != r["season"] and x.get(col) is not None]
            lo = min(sign * x[col] for x in other if x["upper_half"])      # ほかの年の A の最も悪い値
            hi = max(sign * x[col] for x in other if not x["upper_half"])  # ほかの年の B の最もよい値
            stb[id(r)] = "B" if v < lo else "A" if v > hi else "AB"

        def frac(states, s, final):
            xs = [r for r in rs if states.get(id(r)) == s]
            return f"{sum(bool(r['upper_half']) == final for r in xs)}/{len(xs)}"
        n = len(rs)
        a2 = frac(st2, "A", True)
        ab2 = frac(st2, "AB", True)
        b2 = frac(st2, "B", False)
        width = sum(stb[id(r)] == "AB" for r in rs)
        band = f"{frac(stb, 'A', True)}・{frac(stb, 'B', False)}"
        dd = [r for r in d if r.get(col) is not None]
        d_b2 = sum(st2.get(id(r)) == "B" for r in dd)
        d_bb = sum(stb.get(id(r)) == "B" for r in dd)
        out.append((agree35 / n, label))
        print(f"| `{col}` {label} | {agree35 / n:.2f} | {agreeN / n:.2f} | {a2} | {ab2} | {b2} | {width}/{n} | {band} "
              f"| {d_b2}/{len(dd)} | {d_bb}/{len(dd)} |" if neutral is not None else
              f"| `{col}` {label} | {agree35 / n:.2f} | - | {a2} | {ab2} | {b2} | {width}/{n} | {band} | {d_b2}/{len(dd)} | {d_bb}/{len(dd)} |")
    print("\n3.5位の線での一致の高い順: " + "、".join(f"{l} {a:.2f}" for a, l in sorted(out, reverse=True)))

    print("\n中日の B 12年の、2本線での状態（A・AB・B）:")
    for col, label, sign, _ in indicators:
        line = []
        for r in d:
            if r.get(col) is None:
                line.append("-")
                continue
            lg = sorted((sign * x[col] for x in leagues[(r["season"], r["league"])] if x.get(col) is not None), reverse=True)
            v = sign * r[col]
            if len(lg) < 5:   # 値のない球団があるリーグ年（short_share など）は状態を出さない
                line.append("-")
                continue
            line.append("A" if v > mid(lg[1], lg[2]) else "B" if v < mid(lg[3], lg[4]) else "AB")
        print(f"  {label}: " + " ".join(f"{r['season'] % 100:02d}{s}" for r, s in zip(d, line)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
