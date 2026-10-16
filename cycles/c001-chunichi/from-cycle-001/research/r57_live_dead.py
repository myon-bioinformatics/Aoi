"""R57: A・B に効く試合（live）と、決まった後の試合（dead）を並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r57_live_dead.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の rank_fixed_*・live_*・dead_*・clinch_*・mix_* の列だけを使う。2020年は除く。ネットワークを使わない。
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
    a = [r for r in rows if r["upper_half"]]
    b = [r for r in rows if not r["upper_half"]]
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])

    # 1. 効かない試合の量
    dg = [r["dead_g"] for r in rows]
    print(f"1. 効かない試合: 全 {len(rows)} 単位の中央値 {med(dg)}、最大 {max(dg)}、0 の単位 {sum(x == 0 for x in dg)}。"
          f"A の中央値 {med([r['dead_g'] for r in a])}、B の中央値 {med([r['dead_g'] for r in b])}")
    print("\n| 中日 | 順位 | B 確定の位置 | 残り | 効く試合 | 効かない試合 | 効く試合の勝率 | 効かない試合の勝率 | 順位確定の位置 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['rank']} | {f(r['clinch_out_x'], '.2f')} | {f(r['clinch_out_left'], 'd')} | {r['live_g']} | {r['dead_g']} "
              f"| {f(r['live_wpct'], '.3f')} | {f(r['dead_wpct'], '.3f')} | {f(r['rank_fixed_x'], '.2f')} |")

    # 2. 最終順位の確定
    print("\n2. | 順位 | 単位 | 確定した単位 | 確定の位置の中央値 | 確定した日の残り試合の中央値 |\n|---|---|---|---|---|")
    for k in range(1, 7):
        xs = [r for r in rows if r["rank"] == k]
        fx = [r for r in xs if r["rank_fixed_x"] is not None]
        print(f"| {k} | {len(xs)} | {len(fx)} | {f(med([r['rank_fixed_x'] for r in fx]), '.2f')} | {f(med([r['rank_fixed_left'] for r in fx]), '')} |")

    # 3. 決まった後に勝ち方が変わるか
    print("\n3. | 決まった側 | 単位（効かない試合あり） | 勝率の差（後 − 前）の中央値 | 点の差/試合の差の中央値 | 後のほうが勝率が高い単位 |\n|---|---|---|---|---|")
    for name, xs in (("A が確定", [r for r in a if r["dead_g"]]), ("B が確定", [r for r in b if r["dead_g"]]),
                     ("中日の B", [r for r in d if r["dead_g"]])):
        dw = [r["dead_wpct"] - r["live_wpct"] for r in xs if r["dead_wpct"] is not None and r["live_wpct"] is not None]
        dr = [r["dead_rd_g"] - r["live_rd_g"] for r in xs if r["dead_rd_g"] is not None and r["live_rd_g"] is not None]
        print(f"| {name} | {len(xs)} | {f(med(dw), '+.3f')} | {f(med(dr), '+.2f')} | {sum(x > 0 for x in dw)}/{len(dw)} |")

    # 4. 効く試合だけの勝率で、中日の B は帯のどこか
    lo, hi = med([r["mix_lo"] for r in rows]), med([r["mix_hi"] for r in rows])
    zone = lambda w: "下" if w < lo else "上" if w > hi else "中"  # noqa: E731
    print(f"\n4. 帯（全試合の勝率で引いた値の中央値）{lo:.3f}〜{hi:.3f}。中日の B の効く試合だけの勝率: "
          + "、".join(f"{r['season']} {r['live_wpct']:.3f}（{zone(r['live_wpct'])}）" for r in d))
    print("   帯の下 {} / 中 {} / 上 {}".format(*(sum(zone(r["live_wpct"]) == z for r in d) for z in "下中上")))

    # 5. 効かない試合が多い単位
    top = sorted(rows, key=lambda r: -r["dead_g"])[:12]
    print("\n5. 効かない試合が多い順: " + ", ".join(
        f"{r['team']}-{r['season']}（{r['rank']}位、{r['dead_g']}試合、前 {f(r['live_wpct'], '.3f')} → 後 {f(r['dead_wpct'], '.3f')}）" for r in top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
