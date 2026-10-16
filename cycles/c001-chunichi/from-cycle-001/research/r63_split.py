"""R63: 中日の B の「前半から見えた6年」と「形が定まらなかった6年」、後半の下がりを効く試合で分ける（記述。判定はしない）。

    python cycles/c001-chunichi/research/r63_split.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import statistics
import sys
from pathlib import Path

EXCLUDED = {2020}
FOCUS, FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def route(r):
    big = r["run_balance_t"] <= -1
    return ("大きな不足" if big else "不足は誤差の内") + "・" + ("点の差より勝った" if r["resid_fixed"] > 0 else "点の差より負けた")


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    seen = [r for r in d if r.get("wave_limit_rank_h1") is not None]
    unformed = [r for r in d if r.get("wave_limit_rank_h1") is None]

    print("## 1. 前半から見えた年と、形が定まらなかった年\n")
    print("| 組 | 年 | 順位 | 道 | 収支 ÷ 誤差 | 点の差より勝った分 | 得点の優位 | 失点の優位 |\n|---|---|---|---|---|---|---|---|")
    for name, xs in (("見えた", seen), ("定まらない", unformed)):
        for r in xs:
            print(f"| {name} | {r['season']} | {r['rank']} | {route(r)} | {r['run_balance_t']:+.2f} | {r['resid_fixed']:+.3f} "
                  f"| {r['rf_adv']:+.2f} | {r['ra_adv']:+.2f} |")
    for name, xs in (("見えた", seen), ("定まらない", unformed)):
        print(f"- {name}（{len(xs)}）: 収支 ÷ 誤差 {med([r['run_balance_t'] for r in xs]):+.2f}、点の差より勝った分 {med([r['resid_fixed'] for r in xs]):+.3f}、"
              f"得点の優位 {med([r['rf_adv'] for r in xs]):+.2f}、失点の優位 {med([r['ra_adv'] for r in xs]):+.2f}、"
              f"大きな不足 {sum(r['run_balance_t'] <= -1 for r in xs)}、点の差より勝った {sum(r['resid_fixed'] > 0 for r in xs)}")

    print("\n## 2. 後半の下がりは効く試合か\n")
    print("| 中日 | 前半 | 後半 | 後半の効く試合だけ | 後半の効く試合の数 |\n|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['course_wpct_h1']:.3f} | {r['course_wpct_h2']:.3f} | {r['h2_live_wpct']:.3f} | {r['h2_live_g']} |")
    ob = [r for r in rows if not r["upper_half"] and r["team"] != FOCUS]
    for name, xs in (("中日の B", d), ("中日以外の B", ob), ("A", [r for r in rows if r["upper_half"]])):
        h1, h2, lv = med([r["course_wpct_h1"] for r in xs]), med([r["course_wpct_h2"] for r in xs]), med([r["h2_live_wpct"] for r in xs])
        print(f"- {name}（{len(xs)}）: 前半 {h1:.3f}、後半 {h2:.3f}（{h2 - h1:+.3f}）、後半の効く試合だけ {lv:.3f}（{lv - h1:+.3f}）、"
              f"後半の効く試合の数 {med([r['h2_live_g'] for r in xs]):.0f}")
    lower = sum(r["h2_live_wpct"] < r["course_wpct_h1"] for r in d)
    print(f"中日の B で、後半の効く試合だけでも前半より低い年: {lower}/{len(d)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
