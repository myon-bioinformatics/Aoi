"""R35: 2020年を参考として同じ物差し（誤差の幅）で並べ、中日の「失点だけ上位」の年を誤差の内側・外側に分ける（記述）。

    python cycles/c001-chunichi/research/r35_reference.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存の列だけを使う（*_adv・*_adv_se・*_zone_se は R32〜R34）。ネットワークを使わない。判定はしない。
"""

import json
import sys
from pathlib import Path

SHORTFALL = 0.6  # R32〜R34 の境（1試合あたりの得点の不足）


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def fmt(r: dict) -> str:
    return (f"| {r['team_name']} {r['season']} | {r['G']} | {r['rank']} | {r['rf_adv']:+.2f} | {r['rf_adv_se']:.2f} | {r['rf_zone_se']:+d} "
            f"| {r['ra_adv']:+.2f} | {r['ra_adv_se']:.2f} | {r['ra_zone_se']:+d} | {r['run_balance']:+.2f} |")


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    head = ("| 単位 | 試合 | 順位 | 得点の優位 | 誤差 | 区分 | 失点の優位 | 誤差 | 区分 | 収支 |\n"
            "|---|---|---|---|---|---|---|---|---|---|")

    print("## 1. 2020年（参考）\n")
    y20 = [r for r in rows if r["season"] == 2020 and r["league"] == "C"]
    print(head)
    for r in sorted(y20, key=lambda r: r["rank"]):
        print(fmt(r))
    rest = [r for r in rows if r["season"] != 2020]
    print(f"\n誤差の中央値: 2020年 得点 {sorted(r['rf_adv_se'] for r in y20)[len(y20) // 2]:.3f}、"
          f"他の年 {sorted(r['rf_adv_se'] for r in rest)[len(rest) // 2]:.3f}")
    big = [r for r in rows if r["rf_adv"] < -SHORTFALL]
    print(f"\n不足 > {SHORTFALL} の単位: 全 {len(big)}、うち A {sum(r['upper_half'] for r in big)}"
          f"（{', '.join(f'{r['team']}-{r['season']}' for r in big if r['upper_half'])}）")
    for r in big:
        if r["upper_half"]:
            print(f"  {r['team']}-{r['season']}: 不足 ÷ 誤差 = {-r['rf_adv'] / r['rf_adv_se']:.2f}、"
                  f"不足 − 0.6 = {-r['rf_adv'] - SHORTFALL:.2f}（誤差 {r['rf_adv_se']:.2f} の {(-r['rf_adv'] - SHORTFALL) / r['rf_adv_se']:.2f} 倍）")

    print("\n## 2. 中日の「失点だけ上位」（順位: 失点3位以内・得点4位以下）の年\n")
    d = [r for r in rows if r["team"] == "d" and r["rank_ra"] <= 3 and r["rank_rf"] >= 4]
    print(head)
    for r in sorted(d, key=lambda r: r["season"]):
        print(fmt(r))
    for name, xs in (("失点が誤差の外側（+1）", [r for r in d if r["ra_zone_se"] == 1]),
                     ("失点が誤差の内側（0）", [r for r in d if r["ra_zone_se"] == 0])):
        print(f"\n{name}: {', '.join(str(r['season']) for r in xs)}。A {sum(r['upper_half'] for r in xs)}／{len(xs)}、"
              f"得失点差の平均 {mean(r['rd'] for r in xs):+.1f}、得点の優位の平均 {mean(r['rf_adv'] for r in xs):+.2f}、"
              f"失点の優位の平均 {mean(r['ra_adv'] for r in xs):+.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
