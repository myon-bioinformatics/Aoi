"""R44: 大きく落ちた7単位と、大きさは上位なのに B の単位を、1単位ずつ並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r44_cases.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存のチームの列だけを使う。分け方の規則は R44 の計画で先に決めた（下の classify_*）。
"""

import json
import sys
from pathlib import Path


def classify_fade(r: dict) -> list[str]:
    """大きく落ちた単位を、計画で決めた規則で分ける（複数に当たってよい）。"""
    tags = []
    if (r["half1_vs_pythag"] or 0) > 3 or (r["course_ra_h1_d"] or 0) < -0.5:
        tags.append("前半が出来すぎ")
    if (r["course_rf_d"] or 0) < 0 and (r["course_ra_d"] or 0) > 0 and (r["half2_vs_pythag"] or 0) < -2:
        tags.append("後半の崩れ")
    return tags or ["どちらでもない"]


def classify_big_inning_b(r: dict) -> list[str]:
    """大きさは上位なのに B の単位を、計画で決めた規則で分ける。"""
    tags = []
    if r["ra_zone_se"] == -1:
        tags.append("失点がはっきり劣る")
    if (r["wins_vs_pythag"] or 0) < -2 or (r["alloc_z_strat"] or 0) < -1:
        tags.append("点の差を勝ちに変えられない")
    return tags or ["どちらでもない"]


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]

    print("### 大きく落ちた単位（前半の順位より3つ以上下で終わった）\n")
    print("| 単位 | 1/4 → 前半 → 3/4 → 最終 | 前半、点の差より | 前半の失点（他球団比） | 後半の得点 | 後半の失点 | 後半、点の差より | 分け方 |")
    print("|---|---|---|---|---|---|---|---|")
    for r in sorted((r for r in rows if (r["course_fade"] or 0) >= 3), key=lambda r: (r["season"], r["team"])):
        print(f"| {r['team_name']} {r['season']} | {r['course_rank_q1']} → {r['course_rank_h1']} → {r['course_rank_q3']} → {r['rank']} "
              f"| {r['half1_vs_pythag']:+.1f} | {r['course_ra_h1_d']:+.2f} | {r['course_rf_d']:+.2f} | {r['course_ra_d']:+.2f} "
              f"| {r['half2_vs_pythag']:+.1f} | {'・'.join(classify_fade(r))} |")

    print("\n### 得点した回の大きさが上位2位以内なのに B（2013〜2025年）\n")
    print("| 単位 | 順位 | 得点の順位 | 形 | 点の差より | 組み合わせ方 | 上の相手 − 下の相手 | 分け方 |")
    print("|---|---|---|---|---|---|---|---|")
    big = [r for r in rows if r["season"] >= 2013 and (r["inn_size_rank"] or 0) >= 5 and not r["upper_half"]]
    for r in sorted(big, key=lambda r: (r["season"], r["team"])):
        print(f"| {r['team_name']} {r['season']} | {r['rank']} | {r['rank_rf']} | {r['adv_shape_se']} | {r['wins_vs_pythag']:+.1f} "
              f"| {r['alloc_z_strat']:+.2f} | {r['vs_top_minus_lower']:+.2f} | {'・'.join(classify_big_inning_b(r))} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
