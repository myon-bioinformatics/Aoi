"""R47: 同じ年・同じリーグの3位と4位を1組ずつ並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r47_third_vs_fourth.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存のチームの列だけを使う。2020年は除く。同率で3位・4位が決まらない年は、その年を外して数える。
並べる指標と、「3位のほうが上」の向きは R47 の計画で先に決めた（MEASURES）。
"""

import json
import math
import sys
from pathlib import Path

# (列, 中身, 大きいほうが3位らしい向きなら +1、小さいほうなら −1)
MEASURES = [
    ("run_balance", "収支（得点の優位 + 失点の優位）", 1),
    ("rf_adv", "得点の優位", 1),
    ("ra_adv", "失点の優位", 1),
    ("wins_vs_pythag", "点の差から見込まれる勝ち数との差", 1),
    ("alloc_z_strat", "得点・失点の組み合わせ方", 1),
    ("one_run_net", "1点差の勝ち − 負け", 1),
    ("vs_top_wpct", "上の相手との勝率", 1),
    ("vs_lower_wpct", "下の相手との勝率", 1),
    ("course_wpct_diff", "後半の勝率 − 前半の勝率", 1),
    ("wave_limit_rank_h1", "前半の線から当てた行き先（小さいほど上）", -1),
    ("sim_p_upper", "得点・失点の分布から見た A の確率", 1),
]


def sign_test_p(k: int, n: int) -> float:
    """両側の符号検定（二項分布、p = 0.5）。"""
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]
    pairs = []
    for key in sorted({(r["season"], r["league"]) for r in rows}):
        lg = [r for r in rows if (r["season"], r["league"]) == key]
        third, fourth = [r for r in lg if r["rank"] == 3], [r for r in lg if r["rank"] == 4]
        if len(third) == 1 and len(fourth) == 1:
            pairs.append((third[0], fourth[0]))
    print(f"組: {len(pairs)}（3位・4位が1球団ずつ決まる年）\n")

    print("| 年 | リーグ | 3位 | 4位 | 勝ち数の差（ゲーム差） | 3位の道筋 | 4位の道筋 |")
    print("|---|---|---|---|---|---|---|")
    for t, f in pairs:
        gb = ((t["W"] - t["L"]) - (f["W"] - f["L"])) / 2
        mark = lambda r: f"**{r['team_name']}**" if r["team"] == "d" else r["team_name"]  # noqa: E731
        print(f"| {t['season']} | {t['league']} | {mark(t)} | {mark(f)} | {gb:+.1f} | {t['b_paths']} | {f['b_paths']} |")

    print("\n| 指標 | 中身 | 3位のほうが上の組 | 4位のほうが上 | 同じ・空 | 符号検定 p |")
    print("|---|---|---|---|---|---|")
    for col, label, direction in MEASURES:
        up = down = other = 0
        for t, f in pairs:
            a, b = t[col], f[col]
            if a is None or b is None or a == b:
                other += 1
            elif (a - b) * direction > 0:
                up += 1
            else:
                down += 1
        print(f"| `{col}` | {label} | {up} | {down} | {other} | {sign_test_p(up, up + down):.3f} |")

    print("\n中日が4位の年と、その年の3位:\n")
    print("| 年 | 3位 | ゲーム差 | " + " | ".join(c for c, _, _ in MEASURES[:8]) + " |")
    print("|---|---|---|" + "---|" * 8)
    for t, f in pairs:
        if f["team"] != "d":
            continue
        gb = ((t["W"] - t["L"]) - (f["W"] - f["L"])) / 2
        cells = []
        for col, _, direction in MEASURES[:8]:
            a, b = t[col], f[col]
            cells.append("-" if a is None or b is None else f"{b:+.2f}（3位 {a:+.2f}）")
        print(f"| {f['season']} | {t['team_name']} | {gb:+.1f} | " + " | ".join(cells) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
