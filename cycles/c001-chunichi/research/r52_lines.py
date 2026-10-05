"""R52: 勝率の散らばりから引く線を並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r52_lines.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の既存の列（wpct・rank・upper_half・lg_*）だけを使う。2020年は除く。ネットワークを使わない。
ばらつき最小の2つの塊（1次元の Jenks / 大津の方法）だけは列にせず、ここで計算する。
"""

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

EXCLUDED = {2020}
FOCUS = "d"
FOCUS_YEARS = set(range(2013, 2026)) - EXCLUDED


def jenks2(wpcts: list[float]) -> int:
    """勝率を高い順に並べ、2つに分けたときに塊の中の偏差平方和の合計が最小になる k（k 位と k+1 位の間）。同じなら上位側。"""
    w = sorted(wpcts, reverse=True)

    def ss(xs):
        m = sum(xs) / len(xs)
        return sum((x - m) ** 2 for x in xs)

    best = min(range(1, len(w)), key=lambda k: (round(ss(w[:k]) + ss(w[k:]), 12), k))
    return best


def unit(r: dict) -> str:
    return f"{r['team']}-{r['season']}"


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    jk = {key: jenks2([r["wpct"] for r in xs]) for key, xs in leagues.items()}
    for r in rows:
        r["jenks_after"] = jk[(r["season"], r["league"])]
    print(f"範囲: {len(leagues)} リーグ・年、{len(rows)} 単位（2020年を除く）")

    # 1・2. 切れ目の位置
    gap = Counter(xs[0]["lg_break_after"] for xs in leagues.values())
    jen = Counter(jk.values())
    agree = sum(xs[0]["lg_break_after"] == jk[key] for key, xs in leagues.items())
    print("\n| 切れ目（k 位と k+1 位の間） | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|")
    print("| いちばん大きな隙間 | " + " | ".join(str(gap.get(k, 0)) for k in range(1, 6)) + " |")
    print("| ばらつき最小の2つの塊 | " + " | ".join(str(jen.get(k, 0)) for k in range(1, 6)) + " |")
    inner = sum(gap.get(k, 0) for k in (2, 3, 4))
    print(f"\nいちばん大きな隙間が 3 に来た: {gap.get(3, 0)}/{len(leagues)}（素朴な目安 1/5 = {len(leagues) / 5:.1f}）。"
          f"端を除いた 2〜4 の中で 3: {gap.get(3, 0)}/{inner}（目安 1/3）")
    print(f"ばらつき最小の切れ目が 3 に来た: {jen.get(3, 0)}/{len(leagues)}。いちばん大きな隙間と一致: {agree}/{len(leagues)}")
    print("\n| 年 | リーグ | 隙間 k | 隙間の差 | 塊の切れ目（2つ）| ばらつき最小 k | 3位と4位の差 |\n|---|---|---|---|---|---|---|")
    for (season, lg), xs in sorted(leagues.items()):
        t = sorted(xs, key=lambda r: r["rank"])
        tiers = [r["lg_tier"] for r in t]
        cuts = [k for k in range(1, 6) if tiers[k] != tiers[k - 1]]
        print(f"| {season} | {lg} | {t[0]['lg_break_after']} | {t[0]['lg_break_gap']:.3f} | {'・'.join(map(str, cuts))} "
              f"| {jk[(season, lg)]} | {t[0]['lg_gap34']:.3f} |")

    # 3. A かどうかと、自然な塊の上下が一致するか
    for name, col in (("いちばん大きな隙間", "lg_break_after"), ("ばらつき最小", "jenks_after")):
        same = sum((r["rank"] <= 3) == (r["rank"] <= r[col]) for r in rows)
        print(f"\nA（3位以内）と「{name}より上」が一致: {same}/{len(rows)} 単位")

    # 4. 中日の B の年
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]),
               key=lambda r: r["season"])
    print(f"\n| 中日の B（{len(d)}年） | 順位 | 勝率 | A の線 | 自分の塊 / 3位の塊 | 隙間より上 | ばらつき最小で上 |\n|---|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['rank']} | {r['wpct']:.3f} | {r['lg_line']:.3f} | {r['lg_tier']} / {r['lg_tier_of_3rd']} "
              f"| {'上' if r['rank'] <= r['lg_break_after'] else '下'} | {'上' if r['rank'] <= r['jenks_after'] else '下'} |")
    print(f"3位と同じ塊: {sum(r['lg_tier'] == r['lg_tier_of_3rd'] for r in d)}/{len(d)}、"
          f"隙間より上（3位と同じ側）: {sum(r['rank'] <= r['lg_break_after'] for r in d)}/{len(d)}、"
          f"ばらつき最小で上: {sum(r['rank'] <= r['jenks_after'] for r in d)}/{len(d)}")

    # 5. 全体の四分位の線
    q1, med, q3 = statistics.quantiles([r["wpct"] for r in rows], n=4, method="inclusive")
    print(f"\n全体の四分位: Q1 {q1:.3f}、中央値 {med:.3f}、Q3 {q3:.3f}")
    band = Counter("Q1 未満" if r["wpct"] < q1 else "Q1〜中央値" if r["wpct"] < med else "中央値以上" for r in d)
    print("中日の B: " + "、".join(f"{k} {band.get(k, 0)}" for k in ("Q1 未満", "Q1〜中央値", "中央値以上")))
    for r in d:
        print(f"  {r['season']}: {r['wpct']:.3f}")
    off = sorted((r for r in rows if (r["wpct"] >= med) != bool(r["upper_half"])), key=lambda r: (r["season"], r["league"]))
    print(f"中央値と順位が食い違う単位 {len(off)}: " + ", ".join(
        f"{unit(r)}（{r['rank']}位 {r['wpct']:.3f}）" for r in off))
    above_q3_b = [unit(r) for r in rows if r["wpct"] >= q3 and not r["upper_half"]]
    below_q1_a = [unit(r) for r in rows if r["wpct"] < q1 and r["upper_half"]]
    print(f"Q3 以上の B: {above_q3_b or 'なし'}、Q1 未満の A: {below_q1_a or 'なし'}")

    # 6. 阪神 2015年
    h = next((r for r in rows if r["team"] == "t" and r["season"] == 2015), None)
    if h:
        print(f"\n阪神 2015年: {h['rank']}位 {h['wpct']:.3f}、A の線 {h['lg_line']:.3f}、塊 {h['lg_tier']} / 3位の塊 {h['lg_tier_of_3rd']}、"
              f"隙間 k {h['lg_break_after']}（{'上' if h['rank'] <= h['lg_break_after'] else '下'}）、"
              f"ばらつき最小 k {h['jenks_after']}（{'上' if h['rank'] <= h['jenks_after'] else '下'}）、"
              f"四分位: {'Q1 未満' if h['wpct'] < q1 else 'Q1〜中央値' if h['wpct'] < med else '中央値以上'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
