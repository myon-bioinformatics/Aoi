"""R65: 試合ごとの失策（2025年の得点表）を、勝ち・負け・1点差・最後の区間で並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r65_game_errors.py cycles/c001-chunichi/outputs/season.jsonl
"""

import json
import statistics
import sys
from pathlib import Path

SEASON = 2025
COLS = [("ls_e_net_g", "全試合"), ("ls_e_net_close", "1点差"), ("ls_e_net_win", "勝ち"), ("ls_e_net_loss", "負け"), ("ls_e_net_q4", "最後の区間")]


def share(a, b, sign):
    pairs = [(x, y) for x in a for y in b]
    return sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs) / len(pairs)


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = sorted((r for r in rows if r["season"] == SEASON), key=lambda r: (r["league"], r["rank"]))
    print(f"{SEASON}年: {len(rows)} 球団、得点表のある試合の割合 {[round(r['ls_cov'], 3) for r in rows]}")

    same = sum(abs(r["ls_e_g"] - r["fld_e_g"]) < 0.0005 for r in rows)
    print(f"1. 照合: 得点表の失策／試合と守備成績の失策／試合が一致 {same}/{len(rows)}")

    print("\n| 球団 | 順位 | 自分の失策/試合 | 相手の失策/試合 | " + " | ".join(f"差（{n}）" for _, n in COLS) + " |")
    print("|---|---|---|---|" + "---|" * len(COLS))
    for r in rows:
        print(f"| {r['team_name']} | {r['rank']} | {r['ls_e_g']:.3f} | {r['ls_opp_e_g']:.3f} | "
              + " | ".join(f"{r[c]:+.3f}" if r[c] is not None else "-" for c, _ in COLS) + " |")

    med = lambda xs: statistics.median(x for x in xs if x is not None)  # noqa: E731
    print(f"\n2. 12球団の中央値: 勝ち {med(r['ls_e_net_win'] for r in rows):+.3f}、負け {med(r['ls_e_net_loss'] for r in rows):+.3f}")
    a, b = [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]]
    print("3〜4. | 列 | A の中央値 | B の中央値 | A が小さい向きの組の割合 |\n|---|---|---|---|")
    for c, n in COLS:
        av, bv = [r[c] for r in a if r[c] is not None], [r[c] for r in b if r[c] is not None]
        print(f"| {n} | {statistics.median(av):+.3f} | {statistics.median(bv):+.3f} | {share(av, bv, -1):.2f} |")
    for t in ("d", "db"):
        r = next(x for x in rows if x["team"] == t)
        print(f"5. {r['team_name']}（{r['rank']}位）: " + "、".join(f"{n} {r[c]:+.3f}" for c, n in COLS if r[c] is not None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
