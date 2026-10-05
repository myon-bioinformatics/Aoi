"""R59: チームの失策と、勝ち方・帯の中・中日の B を並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r59_fielding.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の fld_*・resid_fixed・mix_zone・run_balance_t だけを使う。2020年は除く。ネットワークを使わない。
"""

import json
import statistics
import sys
from pathlib import Path

EXCLUDED = {2020}
FOCUS, FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED
COLS = ["fld_d_e_g", "fld_d_fpct", "fld_d_dp_g", "fld_d_pb_g"]


def share(a, b, sign):
    """a と b のすべての組のうち sign * (a − b) > 0 の割合（同じ値は 0.5）。"""
    pairs = [(x, y) for x in a for y in b]
    return sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs) / len(pairs)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED and r.get("fld_e_g") is not None]
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    print(f"範囲: {len(rows)} 単位")

    print("\n1. | 中日 | 順位 | 失策/試合 | 他球団との差 | 守備率の差 | 併殺/試合の差 |\n|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['rank']} | {r['fld_e_g']:.3f} | {r['fld_d_e_g']:+.3f} | {r['fld_d_fpct']:+.4f} | {r['fld_d_dp_g']:+.3f} |")
    print(f"他球団より失策が少ない年: {sum(r['fld_d_e_g'] < 0 for r in d)}/{len(d)}")

    print("\n| 比べ | 群 | 失策が少ない向きの割合（fld_d_e_g） | 守備率が高い向き | 併殺が多い向き |\n|---|---|---|---|---|")
    groups = [
        ("2. 勝ち方", [r for r in rows if r["resid_fixed"] > 0], [r for r in rows if r["resid_fixed"] < 0], "点の差より勝った / 負けた"),
        ("3. 帯の中", [r for r in rows if r["mix_zone"] == 0 and r["upper_half"]],
         [r for r in rows if r["mix_zone"] == 0 and not r["upper_half"]], "A / B"),
        ("参考: 全体", [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]], "A / B"),
    ]
    for name, a, b, label in groups:
        print(f"| {name} | {label}（{len(a)} / {len(b)}） | {share([r['fld_d_e_g'] for r in a], [r['fld_d_e_g'] for r in b], -1):.2f} "
              f"| {share([r['fld_d_fpct'] for r in a], [r['fld_d_fpct'] for r in b], 1):.2f} "
              f"| {share([r['fld_d_dp_g'] for r in a], [r['fld_d_dp_g'] for r in b], 1):.2f} |")

    big = [r for r in d if r["run_balance_t"] <= -1]
    small = [r for r in d if r["run_balance_t"] > -1]
    print(f"\n4. 中日の大きな不足 {len(big)}年: 失策の差の中央値 {statistics.median(r['fld_d_e_g'] for r in big):+.3f}、"
          f"勝ち方で落とした（不足は誤差の内）{len(small)}年: {statistics.median(r['fld_d_e_g'] for r in small):+.3f}"
          f"（{', '.join(str(r['season']) + ' ' + format(r['fld_d_e_g'], '+.3f') for r in small)}）")
    for t, s in (("t", 2015), ("g", 2017), ("g", 2018)):
        r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
        print(f"5. {t}-{s}: 失策/試合 {r['fld_e_g']:.3f}、他球団との差 {r['fld_d_e_g']:+.3f}、守備率の差 {r['fld_d_fpct']:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
