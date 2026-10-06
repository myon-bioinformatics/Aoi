"""R60: 順位表で A・B の側が落ち着いた試合数（N）と、区間ごとの勝 − 敗の並び（記述。判定はしない）。

    python cycles/c001-chunichi/research/r60_settle.py cycles/c001-chunichi/outputs/season.jsonl

season.jsonl の lock_*・lg_set_lock_x・q_wl_*・lone_down_n・clinch_*・course_rank_q3 だけを使う。2020年は除く。
"""

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

EXCLUDED = {2020}
FOCUS, FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def q(xs):
    xs = sorted(xs)
    a, m, b = statistics.quantiles(xs, n=4, method="inclusive")
    return f"{a:.0f}・{m:.0f}・{b:.0f}"


def sign(v):
    return "+" if v > 0 else "−" if v < 0 else "0"


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    a, b = [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]]
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    pat = lambda r: " ".join(sign(r[f"q_wl_{k}"]) for k in range(1, 5))  # noqa: E731

    print(f"1. N（lock_g）の四分位（Q1・中央値・Q3）: 全体 {q([r['lock_g'] for r in rows])}、A {q([r['lock_g'] for r in a])}、B {q([r['lock_g'] for r in b])}")
    print("   落ち着いていた単位の割合: " + "、".join(
        f"{n}試合 {sum(r['lock_g'] <= n for r in rows) / len(rows):.0%}" for n in range(10, 150, 10)))
    sets = {(r["season"], r["league"]): r["lg_set_lock_x"] for r in rows}
    print(f"   リーグの上位半分の顔ぶれが落ち着いた位置の中央値: {statistics.median(sets.values()):.2f}（{len(sets)} リーグ・年）")

    print("\n2. | 中日 | 順位 | N（試合） | 落ち着いた位置 | 数の上で B が決まった位置 | 間（位置） | 区間の並び |\n|---|---|---|---|---|---|---|")
    for r in d:
        gap = r["clinch_out_x"] - r["lock_x"] if r["clinch_out_x"] is not None else None
        print(f"| {r['season']} | {r['rank']} | {r['lock_g']} | {r['lock_x']:.2f} | {r['clinch_out_x']:.2f} | {gap:+.2f} | {pat(r)} |")
    ob = [r for r in b if r["team"] != FOCUS]
    print(f"   中日以外の B の N の中央値 {statistics.median(r['lock_g'] for r in ob):.0f}、中日の B の N の中央値 {statistics.median(r['lock_g'] for r in d):.0f}")

    mid = [r for r in rows if 3 <= r["course_rank_q3"] <= 4]
    ma, mb = [r for r in mid if r["upper_half"]], [r for r in mid if not r["upper_half"]]
    print(f"\n3. 3/4 の時点で AB の状態: {len(mid)}（最後 A {len(ma)}・B {len(mb)}）")
    print(f"   N の中央値: 最後 A {statistics.median(r['lock_g'] for r in ma):.0f}、最後 B {statistics.median(r['lock_g'] for r in mb):.0f}")
    pairs = [(x, y) for x in ma for y in mb]
    sh = sum(1.0 if x["q_wl_4"] > y["q_wl_4"] else 0.5 if x["q_wl_4"] == y["q_wl_4"] else 0.0 for x, y in pairs) / len(pairs)
    print(f"   最後の区間の勝 − 敗が A の側で大きい組の割合: {sh:.2f}")
    for name, xs in (("最後 A", ma), ("最後 B", mb)):
        c = Counter(pat(r) for r in xs)
        print(f"   {name} の区間の並び: " + "、".join(f"{p}: {n}" for p, n in c.most_common()))
    print("   最後の区間の符号 × 最後: " + "、".join(
        f"{s} → A {sum(sign(r['q_wl_4']) == s for r in ma)}・B {sum(sign(r['q_wl_4']) == s for r in mb)}" for s in "+0−"))

    lone = [r for r in rows if r["lone_down_n"] >= 1]
    print(f"\n4. 自分だけ負け越した区間がある単位: {len(lone)}（A {sum(r['upper_half'] for r in lone)}・B {sum(not r['upper_half'] for r in lone)}）")
    print("   中日: " + ("、".join(f"{r['season']}（{r['lone_down_n']}区間、{pat(r)}）" for r in rows if r["team"] == FOCUS and r["lone_down_n"]) or "なし"))

    for t, s in (("t", 2015), ("g", 2017), ("g", 2018)):
        r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
        print(f"5. {t}-{s}: N {r['lock_g']}（位置 {r['lock_x']:.2f}）、区間 {pat(r)}（{', '.join(str(r[f'q_wl_{k}']) for k in range(1, 5))}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
