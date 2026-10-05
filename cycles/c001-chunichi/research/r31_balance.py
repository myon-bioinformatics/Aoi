"""R31: 中日の得点の不足を帯ごとに分け、失点の優位と並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r31_balance.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存の列だけを使う（rf_def_* は R3、得点・失点・試合数は観測）。ネットワークを使わない。
失点の優位 ra_adv = 同じ年・同じリーグの他球団の失点／試合の平均 − 自分の失点／試合（プラスほど抑えた）。
収支 balance = rf_def_total + ra_adv（得点の不足を、失点の優位で補えたか。プラスなら補えた）。
"""

import json
import sys
from pathlib import Path

BANDS = ("floor", "mid", "ceiling", "total")
EARLY, LATE = range(2013, 2020), range(2021, 2026)  # 計画で先に決めた2つの期間（2020年は除く）


def per_game(row: dict, col: str) -> float:
    return row[col] / row["G"]


def add_balance(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        others = [o for o in rows if o["season"] == r["season"] and o["league"] == r["league"] and o["team"] != r["team"]]
        ra_adv = sum(per_game(o, "RA") for o in others) / len(others) - per_game(r, "RA")
        out.append({**r, "ra_adv": ra_adv, "balance": r["rf_def_total"] + ra_adv})
    return out


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def main(argv: list[str]) -> int:
    rows = add_balance([json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()])
    d = sorted((r for r in rows if r["team"] == "d"), key=lambda r: r["season"])

    print("| 年 | 順位 | 失点の順位 | 床 | 中 | 天井 | 得点の不足 | 失点の優位 | 収支 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in d:
        mark = "（除外）" if r["season"] == 2020 else ""
        print(f"| {r['season']}{mark} | {r['rank']} | {r['rank_ra']} | " + " | ".join(f"{r['rf_def_' + b]:+.2f}" for b in BANDS)
              + f" | {r['ra_adv']:+.2f} | {r['balance']:+.2f} |")

    print("\n| 期間 | 年数 | 床 | 中 | 天井 | 得点の不足 | 失点の優位 | 収支 |")
    print("|---|---|---|---|---|---|---|---|")
    means = {}
    for name, years in (("2013〜2019", EARLY), ("2021〜2025", LATE)):
        xs = [r for r in d if r["season"] in years]
        means[name] = {k: mean([r[f"rf_def_{k}"] for r in xs]) for k in BANDS} | {
            "ra_adv": mean([r["ra_adv"] for r in xs]), "balance": mean([r["balance"] for r in xs])}
        m = means[name]
        print(f"| {name} | {len(xs)} | " + " | ".join(f"{m[k]:+.3f}" for k in [*BANDS, "ra_adv", "balance"]) + " |")
    a, b = means["2013〜2019"], means["2021〜2025"]
    change = b["total"] - a["total"]
    print(f"\n得点の不足の変化 {change:+.3f}。帯ごとの割合: " + "、".join(
        f"{k} {(b[k] - a[k]) / change:.0%}" for k in BANDS[:3]))

    # 失点だけ上位（失点3位以内・得点4位以下）の B クラス。2020年を除く
    one = [r for r in rows if r["season"] != 2020 and r["rank_ra"] <= 3 and r["rank_rf"] >= 4 and not r["upper_half"]]
    for name, xs in (("中日", [r for r in one if r["team"] == "d"]), ("中日以外", [r for r in one if r["team"] != "d"])):
        short = sum(r["balance"] < 0 for r in xs)
        print(f"\n失点だけ上位の B クラス・{name}: {len(xs)}単位、補えなかった（収支 < 0）{short}、"
              f"得点の不足 {mean([r['rf_def_total'] for r in xs]):+.3f}、失点の優位 {mean([r['ra_adv'] for r in xs]):+.3f}、"
              f"不足 ÷ 優位 {mean([-r['rf_def_total'] / r['ra_adv'] for r in xs if r['ra_adv'] > 0]):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
