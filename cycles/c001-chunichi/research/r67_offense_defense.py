"""R67: 得点の側と失点の側の2本線の状態（A・AB・B）を組にした9通りで、最後に A になった割合（記述。判定はしない）。

    python cycles/c001-chunichi/research/r67_offense_defense.py cycles/c001-chunichi/outputs/season.jsonl

状態は R66 と同じ: 同じ年・同じリーグの6球団の値を並べ、2番目と3番目の真ん中・4番目と5番目の真ん中の2本線で分ける。
得点の側 = rf_adv（得点の優位）、失点の側 = ra_adv（失点の優位、大きいほど失点が少ない）。範囲は 2013〜2025年（2020年を除く）。
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

SCOPE = set(range(2013, 2026)) - {2020}
STATES = ("A", "AB", "B")


def state(rows, r, col):
    lg = sorted((x[col] for x in rows if (x["season"], x["league"]) == (r["season"], r["league"])), reverse=True)
    v = r[col]
    return "A" if v > (lg[1] + lg[2]) / 2 else "B" if v < (lg[3] + lg[4]) / 2 else "AB"


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    cells = defaultdict(list)
    for r in rows:
        r["off"], r["def"] = state(rows, r, "rf_adv"), state(rows, r, "ra_adv")
        cells[(r["off"], r["def"])].append(r)
    print(f"範囲: {len(rows)} 単位\n")
    print("| 得点の側 ＼ 失点の側 | A | AB | B |\n|---|---|---|---|")
    for o in STATES:
        print(f"| **{o}** | " + " | ".join(
            f"{sum(r['upper_half'] for r in cells[(o, d)])}/{len(cells[(o, d)])}" for d in STATES) + " |")
    print("\n各ます目の中日の B（年）・中日の A（年）:")
    for o in STATES:
        for dd in STATES:
            dB = [r["season"] for r in cells[(o, dd)] if r["team"] == "d" and not r["upper_half"]]
            dA = [r["season"] for r in cells[(o, dd)] if r["team"] == "d" and r["upper_half"]]
            if dB or dA:
                print(f"  得点 {o} × 失点 {dd}: B {dB}、A {dA}")
    print("\n五分に近います目（A の割合 0.3〜0.7、3単位以上）の単位:")
    for (o, dd), xs in sorted(cells.items()):
        if len(xs) >= 3 and 0.3 <= sum(r["upper_half"] for r in xs) / len(xs) <= 0.7:
            print(f"  得点 {o} × 失点 {dd}: " + ", ".join(f"{r['team']}-{r['season']}（{'A' if r['upper_half'] else 'B'}）" for r in xs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
