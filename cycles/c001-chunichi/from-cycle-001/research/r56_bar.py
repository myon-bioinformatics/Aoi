"""R56: 帯の中（mix_zone = 0）の単位で、A・B を分けたのは自分の側か外の側（越えるべき高さ）か（記述。判定はしない）。

    python cycles/c001-chunichi/research/r56_bar.py cycles/c001-chunichi/outputs/season.jsonl

bar = 同じ年・同じリーグのほかの5球団の中で3番目の勝率（A に入るために上回るべき高さ）。2020年は除く。ネットワークを使わない。
比べ方: A と B のすべての組のうち、A の側が先に決めた「A らしい向き」になっている組の割合（同じ値は 0.5 と数える）。
"""

import json
import sys
from pathlib import Path

EXCLUDED = {2020}
WATCH = [("t", 2015), ("g", 2017), ("g", 2018)]
MEASURES = [  # (列, 中身, A らしい向き: +1 = A が高い, −1 = A が低い)。計画で先に決めた
    ("wpct", "勝率（自分）", 1), ("pythag_fixed", "点の差で見込む勝率（自分）", 1), ("resid_fixed", "点の差より勝った分（自分）", 1),
    ("bar", "越えるべき高さ（外）", -1), ("lg_rank_at_500", ".500 の位置（外）", -1),
]


def share(a: list[float], b: list[float], sign: int) -> float:
    pairs = [(x, y) for x in a for y in b]
    score = sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs)
    return score / len(pairs)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    for r in rows:
        others = sorted((o["wpct"] for o in rows if (o["season"], o["league"]) == (r["season"], r["league"]) and o["team"] != r["team"]),
                        reverse=True)
        r["bar"] = others[2]
    band = [r for r in rows if r["mix_zone"] == 0]
    a, b = [r for r in band if r["upper_half"]], [r for r in band if not r["upper_half"]]
    print(f"帯の中: {len(band)} 単位（A {len(a)}・B {len(b)}）、組 {len(a) * len(b)}")
    print("\n| 列 | 中身 | A らしい向きの組の割合 | A の中央値 | B の中央値 |\n|---|---|---|---|---|")
    import statistics
    for col, label, sign in MEASURES:
        av, bv = [r[col] for r in a], [r[col] for r in b]
        print(f"| `{col}` | {label} | {share(av, bv, sign):.2f} | {statistics.median(av):.3f} | {statistics.median(bv):.3f} |")
    print("\n| 単位 | 順位 | 勝率 | bar | 勝率 − bar | 帯 |\n|---|---|---|---|---|---|")
    for r in sorted(band, key=lambda r: r["wpct"] - r["bar"]):
        mark = " ←" if (r["team"], r["season"]) in WATCH else ""
        print(f"| {r['team']}-{r['season']}{mark} | {r['rank']} | {r['wpct']:.3f} | {r['bar']:.3f} | {r['wpct'] - r['bar']:+.3f} | {r['mix_zone']} |")
    for t, s in WATCH:
        r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
        print(f"{t}-{s}: 勝率 {r['wpct']:.3f}、bar {r['bar']:.3f}、帯 {r['mix_zone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
