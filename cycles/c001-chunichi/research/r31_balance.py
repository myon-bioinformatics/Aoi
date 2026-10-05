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
              f"不足 ÷ 優位（平均の比）{-mean([r['rf_def_total'] for r in xs]) / mean([r['ra_adv'] for r in xs]):.2f}")
    # 計画では「不足 ÷ 優位」の各単位の比の平均を使うと決めていたが、優位がほぼ 0 の単位で比が発散し、
    # 平均が意味をなさなかった（実行後に分かった）。R31 の結果に変更として記録し、平均の比に置き換えた

    # 0 の近くの割り算への対策を並べる（ユーザーの指摘から。どれが正しいかは決めず、読みが保たれるかを見る）
    print("\n| 失点だけ上位の B | 比の平均（計画） | 平均の比 | 比の中央値 | 対数で平均（幾何平均） | 取り分の平均 → 比 | 外した単位 |")
    print("|---|---|---|---|---|---|---|")
    for name, xs in (("中日", [r for r in one if r["team"] == "d"]), ("中日以外", [r for r in one if r["team"] != "d"])):
        v = ratio_variants([-r["rf_def_total"] for r in xs], [r["ra_adv"] for r in xs])
        print(f"| {name} | {v['mean_of_ratios']:.3g} | {v['ratio_of_means']:.2f} | {v['median_of_ratios']:.2f} "
              f"| {v['geometric_mean']:.2f} | {v['share_mean']:.2f} → {v['share_as_ratio']:.2f} | {v['dropped']} |")
    return 0


def ratio_variants(deficit: list[float], advantage: list[float]) -> dict:
    """不足 ÷ 優位 を、割る数が 0 に近い単位に強いかどうかの違う形で並べる。

    - mean_of_ratios: 単位ごとの比の平均（計画の形）。優位が 0 に近いと発散する
    - ratio_of_means: 平均の比。割る数は平均なので、範囲全体の優位が 0 に近くない限り発散しない
    - median_of_ratios: 単位ごとの比の中央値。発散した少数の単位に引っ張られない
    - geometric_mean: 自然対数をとって平均し、戻したもの（exp(平均 ln(不足/優位))）。大きな比を圧縮する。
      対数は正の値にしか定義できないので、優位 ≤ 0 の単位は外す（dropped に数える）
    - share_mean: 取り分 不足 ÷（不足 + 優位）の平均。0〜1 に収まり、優位が 0 なら 1（すべて補えなかった）。
      優位がマイナスの単位も 1 で止める。share_as_ratio = s ÷ (1 − s) で比の目盛りに戻す
    不足・優位はどちらもプラスの向き（不足 = 他球団より少ない得点の量）で渡す。
    """
    import math
    import statistics

    pos = [(d, a) for d, a in zip(deficit, advantage) if a > 0]
    ratios = [d / a for d, a in pos]
    logs = [math.log(d) - math.log(a) for d, a in pos if d > 0]
    shares = [1.0 if a <= 0 else min(1.0, max(0.0, d / (d + a))) for d, a in zip(deficit, advantage)]
    s = mean(shares)
    return {
        "mean_of_ratios": mean(ratios),
        "ratio_of_means": mean(deficit) / mean(advantage),
        "median_of_ratios": statistics.median(ratios) if ratios else float("nan"),
        "geometric_mean": math.exp(mean(logs)) if logs else float("nan"),
        "share_mean": s,
        "share_as_ratio": s / (1 - s) if s < 1 else float("inf"),
        "dropped": len(deficit) - len(logs),
    }


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
