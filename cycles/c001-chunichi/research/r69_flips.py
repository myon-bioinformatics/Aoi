"""R69: 9通りのます目で収支の符号が A・B を分けるか、勝ち方が収支をひっくり返した単位（記述。判定はしない）。

    python cycles/c001-chunichi/research/r69_flips.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r68_same_cell import SCOPE, state  # noqa: E402


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    for r in rows:
        r["cell"] = f"{state(r, 'rf_adv', leagues)}×{state(r, 'ra_adv', leagues)}"
        r["pred"] = r["run_balance"] > 0
    print("## 1. ます目ごと（得点 × 失点）: 収支 > 0 の A / 単位、収支 ≤ 0 の A / 単位、収支の符号が当たった数\n")
    print("| ます目 | 収支 > 0 → A | 収支 ≤ 0 → A | 当たり |\n|---|---|---|---|")
    hit_all = 0
    for a in ("A", "AB", "B"):
        for b in ("A", "AB", "B"):
            xs = [r for r in rows if r["cell"] == f"{a}×{b}"]
            pos, neg = [r for r in xs if r["pred"]], [r for r in xs if not r["pred"]]
            hit = sum(r["pred"] == bool(r["upper_half"]) for r in xs)
            hit_all += hit
            print(f"| 得点{a}×失点{b} | {sum(r['upper_half'] for r in pos)}/{len(pos)} | {sum(r['upper_half'] for r in neg)}/{len(neg)} | {hit}/{len(xs)} |")
    print(f"\n全体: 収支の符号が当たった {hit_all}/{len(rows)} = {hit_all / len(rows):.2f}（R66 の点の差で見込む勝率の 3.5位の線は 0.86）")

    flips = sorted((r for r in rows if r["pred"] != bool(r["upper_half"])), key=lambda r: (r["season"], r["league"], r["rank"]))
    print(f"\n## 2. 収支の符号で読み違えた単位: {len(flips)}\n")
    print("| 単位 | 順位 | 最後 | 収支 | 点の差より勝った数 | 1点差 | 組み合わせ方 | 勝率 − 越えるべき高さ | ます目 |\n|---|---|---|---|---|---|---|---|---|")
    agree = 0
    for r in flips:
        ok = (r["wins_vs_pythag"] < 0) if r["pred"] else (r["wins_vs_pythag"] > 0)
        agree += ok
        print(f"| {r['team']}-{r['season']} | {r['rank']} | {'A' if r['upper_half'] else 'B'} | {r['run_balance']:+.2f} | {r['wins_vs_pythag']:+.1f} "
              f"| {r['one_run_net']:+d} | {r['alloc_z_strat']:+.2f} | {r['wpct'] - r['lg_bar']:+.3f} | {r['cell']} |")
    print(f"\n勝ち方の向きが読み違いと合う（収支 > 0 で B なら点の差より負け、≤ 0 で A なら勝ち）: {agree}/{len(flips)}")
    print("中日: " + (", ".join(f"{r['season']}" for r in flips if r["team"] == "d") or "なし")
          + "　阪神: " + (", ".join(f"{r['season']}" for r in flips if r["team"] == "t") or "なし"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
