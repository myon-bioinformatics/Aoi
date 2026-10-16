"""R53: 線の引き方の一覧（分位・等幅・塊・平均 ± SD）と、1年抜きで複数年で使えるか（記述。判定はしない）。

    python cycles/c001-chunichi/research/r53_line_catalog.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の wpct・upper_half だけを使う。2020年は除く。ネットワークを使わない。
"""

import json
import statistics
import sys
from pathlib import Path

EXCLUDED = {2020}
FOCUS, FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def quantile_lines(w: list[float], k: int) -> list[float]:
    return list(statistics.quantiles(w, n=k, method="inclusive"))


def equal_width_lines(w: list[float], k: int) -> list[float]:
    lo, hi = min(w), max(w)
    return [lo + (hi - lo) * i / k for i in range(1, k)]


def jenks_lines(w: list[float], k: int) -> list[float]:
    """1次元で、k 個の塊の偏差平方和の合計が最小になる分け方の境（隣り合う2つの値の中間）。動的計画法。"""
    x = sorted(w)
    n = len(x)
    s1, s2 = [0.0], [0.0]
    for v in x:
        s1.append(s1[-1] + v)
        s2.append(s2[-1] + v * v)

    def ss(i, j):  # x[i:j]
        m = j - i
        return s2[j] - s2[i] - (s1[j] - s1[i]) ** 2 / m

    inf = float("inf")
    cost = [[inf] * (n + 1) for _ in range(k + 1)]
    back = [[0] * (n + 1) for _ in range(k + 1)]
    cost[0][0] = 0.0
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            for i in range(c - 1, j):
                v = cost[c - 1][i] + ss(i, j)
                if v < cost[c][j] - 1e-15:
                    cost[c][j], back[c][j] = v, i
    cuts, j = [], n
    for c in range(k, 0, -1):
        i = back[c][j]
        if c > 1:
            cuts.append((x[i - 1] + x[i]) / 2)
        j = i
    return sorted(cuts)


def sd_lines(w: list[float], _k: int) -> list[float]:
    m, s = statistics.mean(w), statistics.stdev(w)
    return [m - s, m + s]


FAMILIES = [("分位", quantile_lines, (4, 5, 7)), ("等幅", equal_width_lines, (4, 5, 7)),
            ("塊", jenks_lines, (2, 3, 4, 5, 7)), ("平均±SD", sd_lines, (1,))]


def side(rows: list[dict], line: float) -> tuple[int, int]:
    """（線より下の A の数, 線以上の B の数）"""
    return (sum(1 for r in rows if r["wpct"] < line and r["upper_half"]),
            sum(1 for r in rows if r["wpct"] >= line and not r["upper_half"]))


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    seasons = sorted({r["season"] for r in rows})
    d = [r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]]
    h = next(r for r in rows if r["team"] == "t" and r["season"] == 2015)
    w = [r["wpct"] for r in rows]
    print(f"範囲: {len(rows)} 単位、{len(seasons)} 年（2020年を除く）。中日の B {len(d)}年")
    print("\n| 種類 | k | 番号 | 線 | 下の A | 上の B | 側 | 1年抜きで外れた年 | 中日の B が下 | 阪神 2015 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    usable = []
    for name, f, ks in FAMILIES:
        for k in ks:
            lines = f(w, k)
            held = {s: f([r["wpct"] for r in rows if r["season"] != s], k) for s in seasons}
            for i, line in enumerate(lines):
                a_below, b_above = side(rows, line)
                kind = "B 側" if a_below == 0 else "A 側" if b_above == 0 else "混ざる"
                miss = []
                mixed = 0
                for s in seasons:
                    test = [r for r in rows if r["season"] == s]
                    if len(held[s]) != len(lines):
                        miss.append(f"{s}(線の数が違う)")
                        continue
                    ab, ba = side(test, held[s][i])
                    if kind == "B 側" and ab:
                        miss.append(str(s))
                    elif kind == "A 側" and ba:
                        miss.append(str(s))
                    mixed += ab + ba
                if kind == "混ざる":
                    held_txt = f"混ざり計 {mixed}"
                else:
                    held_txt = f"{len(miss)}（{'・'.join(miss)}）" if miss else "0"
                    if not miss:
                        usable.append(f"{name}{k}-{i + 1} {kind} {line:.3f}")
                below = sum(r["wpct"] < line for r in d)
                print(f"| {name} | {k} | {i + 1} | {line:.3f} | {a_below} | {b_above} | {kind} | {held_txt} "
                      f"| {below}/{len(d)} | {'下' if h['wpct'] < line else '上'} |")
    print(f"\n1年抜きで外れた年が 0 の線（複数年で使える）: {len(usable)}")
    for u in usable:
        print(f"- {u}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
