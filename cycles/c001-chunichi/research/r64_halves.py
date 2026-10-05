"""R64: 前半と後半の効く試合を、相手（上・下）と点の差で分ける。中日の見えた年の失点の優位（記述。判定はしない）。

    python cycles/c001-chunichi/research/r64_halves.py cycles/c001-chunichi/outputs/season.jsonl
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


def per_game(r, prefix, side):
    """勝 − 敗を、その半分の同じリーグの相手との試合数がわからないので、半分の試合数で割る（目安）。"""
    g = r["h2_live_g"] if prefix == "h2_live" else r["G"] // 2
    return r[f"{prefix}_wl_vs_{side}"] / g if g else None


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    groups = (("A", [r for r in rows if r["upper_half"]]), ("B", [r for r in rows if not r["upper_half"]]),
              ("中日以外の B", [r for r in rows if not r["upper_half"] and r["team"] != FOCUS]), ("中日の B", d))

    print("## 1. 前半 → 後半の効く試合\n")
    print("| 群 | 点の差/試合 | 上の相手 勝−負 | 下の相手 勝−負 | 上の相手 /試合 | 下の相手 /試合 |\n|---|---|---|---|---|---|")
    for name, xs in groups:
        cell = lambda k: f"{med([r['h1_' + k] for r in xs]):+.2f} → {med([r['h2_live_' + k] for r in xs]):+.2f}"  # noqa: E731
        pg = lambda side: f"{med([per_game(r, 'h1', side) for r in xs]):+.3f} → {med([per_game(r, 'h2_live', side) for r in xs]):+.3f}"  # noqa: E731
        print(f"| {name}（{len(xs)}） | {cell('rd_g')} | {cell('wl_vs_upper')} | {cell('wl_vs_lower')} | {pg('upper')} | {pg('lower')} |")
    print("\n| 中日 | 前半 点の差 | 後半 点の差 | 前半 上 | 後半 上 | 前半 下 | 後半 下 | 後半の効く試合 |\n|---|---|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['h1_rd_g']:+.2f} | {r['h2_live_rd_g']:+.2f} | {r['h1_wl_vs_upper']:+d} | {r['h2_live_wl_vs_upper']:+d} "
              f"| {r['h1_wl_vs_lower']:+d} | {r['h2_live_wl_vs_lower']:+d} | {r['h2_live_g']} |")
    up = sum(r["h2_live_wl_vs_upper"] < r["h1_wl_vs_upper"] for r in d)
    lo = sum(r["h2_live_wl_vs_lower"] < r["h1_wl_vs_lower"] for r in d)
    print(f"中日の B で後半に下がった年: 上の相手 {up}/{len(d)}、下の相手 {lo}/{len(d)}")

    print("\n## 2. 見えた年の失点の優位（プラスなら他球団より少ない）\n")
    for name, xs in (("見えた", [r for r in d if r.get("wave_limit_rank_h1") is not None]),
                     ("定まらない", [r for r in d if r.get("wave_limit_rank_h1") is None])):
        h1 = [-r["course_ra_h1_d"] for r in xs]
        h2 = [-(r["course_ra_h1_d"] + r["course_ra_d"]) for r in xs]
        print(f"- {name}（{len(xs)}）: 前半 {med(h1):+.2f} → 後半 {med(h2):+.2f}　"
              + "、".join(f"{r['season']} {a:+.2f}→{b:+.2f}" for r, a, b in zip(xs, h1, h2)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
