"""R70: 勝ち方（点の差より勝った数）は球団に付いているか・得点も失点も真ん中のます目（記述。判定はしない）。

    python cycles/c001-chunichi/research/r70_club.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r68_same_cell import SCOPE, state  # noqa: E402

COL = "wins_vs_pythag"
PERMS, SEED = 10_000, 20261006
CELL_COLS = [("lg_bar", "越えるべき高さ", -1), ("q_wl_4", "最後の区間 勝−負", 1), ("wins_vs_pythag", "点の差より勝った数", 1),
             ("one_run_net", "1点差 勝−負", 1), ("vs_lower_wpct", "下の相手との勝率", 1), ("vs_top_wpct", "上の相手との勝率", 1),
             ("run_balance", "収支", 1)]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5


def share(a, b, sign):
    pairs = [(x, y) for x in a for y in b]
    return sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs) / len(pairs)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    by = {(r["team"], r["season"]): r for r in rows}
    seasons = sorted({r["season"] for r in rows})

    print("## 1. 勝ち方は球団に付いているか\n")
    pairs = [(by[(t, s)][COL], by[(t, s + 1)][COL]) for (t, s) in by if (t, s + 1) in by]
    print(f"続く2年の組: {len(pairs)}、順位相関 {spearman([a for a, _ in pairs], [b for _, b in pairs]):+.3f}")

    teams = sorted({r["team"] for r in rows})
    def spread(values):  # values[(team, season)] -> 球団の平均の分散
        means = [statistics.mean(values[(t, s)] for s in seasons if (t, s) in values) for t in teams]
        return statistics.pvariance(means)
    actual = {k: r[COL] for k, r in by.items()}
    obs = spread(actual)
    rng = random.Random(SEED)
    ge = 0
    for _ in range(PERMS):
        perm = {}
        for s in seasons:
            for lg in ("C", "P"):
                ks = [k for k in actual if k[1] == s and by[k]["league"] == lg]
                vs = [actual[k] for k in ks]
                rng.shuffle(vs)
                perm.update(zip(ks, vs))
        ge += spread(perm) >= obs
    print(f"球団の平均の分散: {obs:.3f}。年とリーグの中で入れ替えたとき、それ以上になった割合 {ge / PERMS:.4f}（{PERMS} 回、種 {SEED}）")
    means = sorted(((statistics.mean(actual[(t, s)] for s in seasons if (t, s) in actual), t) for t in teams), reverse=True)
    names = {r["team"]: r["team_name"] for r in rows}
    print("球団の平均（勝ち数、多い順）: " + "、".join(f"{names[t]} {m:+.2f}" for m, t in means))

    print("\n## 2. 得点も失点も真ん中のます目（AB × AB）\n")
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    cell = [r for r in rows if state(r, "rf_adv", leagues) == "AB" and state(r, "ra_adv", leagues) == "AB"]
    a, b = [r for r in cell if r["upper_half"]], [r for r in cell if not r["upper_half"]]
    print(f"{len(cell)} 単位（A {len(a)}・B {len(b)}）。B: " + ", ".join(f"{r['team_name']} {r['season']}（{r['rank']}位）" for r in b))
    print("\n| 列 | 中身 | A らしい向きの組の割合 | A の中央値 | B の中央値 |\n|---|---|---|---|---|")
    for col, label, sign in CELL_COLS:
        av, bv = [r[col] for r in a], [r[col] for r in b]
        print(f"| `{col}` | {label} | {share(av, bv, sign):.2f} | {statistics.median(av):+.3f} | {statistics.median(bv):+.3f} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
