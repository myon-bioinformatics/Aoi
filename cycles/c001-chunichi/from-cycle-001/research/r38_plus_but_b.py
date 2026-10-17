"""R38: 得失点差プラスなのに B の単位を、得失点差プラスで A の単位と並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r38_plus_but_b.py cycles/c001-chunichi/outputs/season.jsonl

1. 巨人 2017年を、同じ形（誤差の幅で得点 −1・失点 +1）の A と並べる（R36 の中日 2019年と同じ並べ方）
2. 得失点差プラス（rd > 0）の B（P1 の判例）を、得失点差プラスの A と13の指標で並べる
2020年は除く。指標は R36 と同じ13（r36_case.MEASURES）。ネットワークを使わない。
"""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r36_case import MEASURES  # noqa: E402


def quartiles(xs):
    q = statistics.quantiles(xs, n=4)
    return q[0], q[2]


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]
    key = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731

    print("### 1. 巨人 2017年と中日 2019年（同じ形の A の範囲の外か）\n")
    shape = [r for r in rows if r["rf_zone_se"] == -1 and r["ra_zone_se"] == 1]
    a = [r for r in shape if r["upper_half"]]
    g, d = next(r for r in shape if key(r) == "g-2017"), next(r for r in shape if key(r) == "d-2019")
    print(f"同じ形の A: {', '.join(map(key, a))}\n")
    print("| 指標 | 中身 | 巨人 2017 | 中日 2019 | A の範囲 | 巨人 2017 は外 | 中日 2019 は外 |")
    print("|---|---|---|---|---|---|---|")
    side = lambda v, xs: "**外**（上）" if v > max(xs) else "**外**（下）" if v < min(xs) else "内"  # noqa: E731
    for col, label in MEASURES:
        xs = [r[col] for r in a if r[col] is not None]
        print(f"| `{col}` | {label} | {g[col]:+.2f} | {d[col]:+.2f} | {min(xs):+.2f}〜{max(xs):+.2f} | {side(g[col], xs)} | {side(d[col], xs)} |")

    print("\n### 2. 得失点差プラスの B と A\n")
    plus = [r for r in rows if r["rd"] > 0]
    pb, pa = [r for r in plus if not r["upper_half"]], [r for r in plus if r["upper_half"]]
    print(f"得失点差プラスの B: {len(pb)}（{', '.join(map(key, sorted(pb, key=lambda r: (r['season'], r['team']))))}）、A: {len(pa)}\n")
    print("| 指標 | 中身 | B の中央値 | A の中央値 | A の四分位（25〜75%） | B のうち A の25%より下 | B のうち A の75%より上 |")
    print("|---|---|---|---|---|---|---|")
    for col, label in MEASURES:
        bv, av = [r[col] for r in pb if r[col] is not None], [r[col] for r in pa if r[col] is not None]
        lo, hi = quartiles(av)
        below, above = sum(v < lo for v in bv), sum(v > hi for v in bv)
        print(f"| `{col}` | {label} | {statistics.median(bv):+.2f} | {statistics.median(av):+.2f} | {lo:+.2f}〜{hi:+.2f} "
              f"| {below}/{len(bv)} | {above}/{len(bv)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
