"""R36: 中日 2019年を、同じ形（得点 −1・失点 +1、誤差の幅）のチームと並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r36_case.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存の列だけを使う。ネットワークを使わない。並べる指標と読み方は R36 の計画で先に決めた。
"""

import json
import statistics
import sys
from pathlib import Path

FOCUS = ("d", 2019)
MEASURES = [  # (列, 中身)。計画で先に決めた順
    ("wins_vs_pythag", "点の差から見込まれる勝ち数との差"),
    ("one_run_net", "1点差の勝ち − 負け"),
    ("blowout_net", "4点差以上の勝ち − 負け"),
    ("alloc_z_strat", "得点・失点の組み合わせ方（R1）"),
    ("vs_top_wpct", "上の相手との勝率"),
    ("vs_lower_wpct", "下の相手との勝率"),
    ("opp_conv_top", "上の相手との試合で、点の差では説明できない勝ち負け"),
    ("opp_conv_mid", "中位の相手との同じもの"),
    ("opp_conv_low", "下の相手との同じもの"),
    ("opp_net_gap_top_c", "上の相手との試合の点の差（見込みとの差）"),
    ("opp_env_gap_top_c", "上の相手との試合全体の点の多さ（見込みとの差）"),
    ("course_wpct_diff", "後半の勝率 − 前半の勝率"),
    ("series_lost_pct", "負け越したカードの多さ（力が一定のときとの比べ）"),
]


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    shape = [r for r in rows if r["season"] != 2020 and r["rf_zone_se"] == -1 and r["ra_zone_se"] == 1]
    focus = next(r for r in shape if (r["team"], r["season"]) == FOCUS)
    a = [r for r in shape if r["team"] != "d" and r["upper_half"]]
    b = [r for r in shape if r["team"] != "d" and not r["upper_half"]]
    other_d = [r for r in shape if r["team"] == "d" and r is not focus]
    name = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731

    print(f"同じ形の単位: 中日以外の A {len(a)}（{', '.join(map(name, a))}）、中日以外の B {len(b)}（{', '.join(map(name, b))}）、"
          f"中日 {', '.join(name(r) + ('(A)' if r['upper_half'] else '(B)') for r in [focus, *other_d])}\n")
    print("| 指標 | 中身 | 中日 2019 | A の範囲（中央値） | B の範囲（中央値） | 2019 は A の範囲の外 | A と B が重ならない |")
    print("|---|---|---|---|---|---|---|")
    for col, label in MEASURES:
        av, bv, f = [r[col] for r in a if r[col] is not None], [r[col] for r in b if r[col] is not None], focus[col]
        if f is None or not av or not bv:
            print(f"| `{col}` | {label} | - | - | - | - | - |")
            continue
        outside = "**外**（下）" if f < min(av) else "**外**（上）" if f > max(av) else "内"
        split = "重ならない" if max(av) < min(bv) or min(av) > max(bv) else "重なる"
        print(f"| `{col}` | {label} | {f:+.2f} | {min(av):+.2f}〜{max(av):+.2f}（{statistics.median(av):+.2f}） "
              f"| {min(bv):+.2f}〜{max(bv):+.2f}（{statistics.median(bv):+.2f}） | {outside} | {split} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
