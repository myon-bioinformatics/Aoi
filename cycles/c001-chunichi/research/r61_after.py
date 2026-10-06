"""R61: 落ち着いた後の戦い方、近似の線と N、12球団ごとの同じ指標（記述。判定はしない）。

    python cycles/c001-chunichi/research/r61_after.py cycles/c001-chunichi/outputs/season.jsonl
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


def f(v, spec):
    return "-" if v is None else format(v, spec)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    a, b = [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]]
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    ob = [r for r in b if r["team"] != FOCUS]

    print("## 1. 落ち着いた後\n")
    for name, xs in (("A", a), ("B", b), ("中日以外の B", ob), ("中日の B", d)):
        print(f"- {name}（{len(xs)}）: 前 {f(med([r['pre_lock_wpct'] for r in xs]), '.3f')} → 後 {f(med([r['post_lock_wpct'] for r in xs]), '.3f')}、"
              f"後の試合数の中央値 {f(med([r['post_lock_g'] for r in xs]), '.0f')}")
    print("\n| 中日 | N | 前の勝率 | 後の試合 | 後の勝率 |\n|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['lock_g']} | {f(r['pre_lock_wpct'], '.3f')} | {r['post_lock_g']} | {f(r['post_lock_wpct'], '.3f')} |")
    for name, xs in (("中日の B", d), ("中日以外の B", ob)):
        ok = [r for r in xs if r["post_lock_wpct"] is not None]
        print(f"落ち着いた後 .500 以上: {name} {sum(r['post_lock_wpct'] >= 0.5 for r in ok)}/{len(ok)}")

    print("\n## 2. 近似の線と N\n")
    pair = [r for r in rows if r.get("wave_settle_x") is not None and r["lock_x"] is not None]
    diff = [r["wave_settle_x"] - r["lock_x"] for r in pair]
    print(f"波の決まった位置 − 順位表の落ち着いた位置: {len(pair)} 単位、中央値 {med(diff):+.2f}、"
          f"波が早い {sum(x < 0 for x in diff)}・同じ {sum(x == 0 for x in diff)}・遅い {sum(x > 0 for x in diff)}")
    h1 = [r for r in rows if r.get("wave_limit_rank_h1") is not None]
    hit = sum((r["wave_limit_rank_h1"] <= 3.5) == bool(r["upper_half"]) for r in h1)
    print(f"前半だけの波の行き先の側と最後の A・B の一致: {hit}/{len(h1)}（行き先なし {len(rows) - len(h1)}）")
    print("\n| 中日 | 前半の波の行き先 | 全体の波の行き先 | 波の決まった位置 | 順位表の落ち着いた位置 | 波の当てはまりの差 |\n|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {f(r.get('wave_limit_rank_h1'), '.1f')} | {f(r.get('wave_limit_rank'), '.1f')} | {f(r.get('wave_settle_x'), '.2f')} "
              f"| {r['lock_x']:.2f} | {f(r.get('wave_rmse'), '.2f')} |")

    print("\n## 3. 12球団ごと\n")
    print("| 球団 | B の年 | N の中央値（B） | 4区間とも負け越し | 自分だけ負け越した区間 | 3/4 で3〜4位 → A | 落ち着いた後の勝率（B） |\n|---|---|---|---|---|---|---|")
    teams = sorted({(r["team"], r["team_name"]) for r in rows})
    table = []
    for t, name in teams:
        xs = [r for r in rows if r["team"] == t]
        bs = [r for r in xs if not r["upper_half"]]
        allneg = sum(all(r[f"q_wl_{k}"] < 0 for k in range(1, 5)) for r in xs)
        mid = [r for r in xs if 3 <= r["course_rank_q3"] <= 4]
        row = (name, len(bs), med([r["lock_g"] for r in bs]), allneg, sum(r["lone_down_n"] for r in xs),
               f"{sum(r['upper_half'] for r in mid)}/{len(mid)}", med([r["post_lock_wpct"] for r in bs]))
        table.append(row)
        print(f"| {row[0]} | {row[1]} | {f(row[2], '.0f')} | {row[3]} | {row[4]} | {row[5]} | {f(row[6], '.3f')} |")
    me = next(r for r in table if r[0] == "中日")
    print(f"\n中日の位置: B の年 {sorted((r[1] for r in table), reverse=True).index(me[1]) + 1}番目に多い、"
          f"4区間とも負け越し {sorted((r[3] for r in table), reverse=True).index(me[3]) + 1}番目に多い（同数は上の順位）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
