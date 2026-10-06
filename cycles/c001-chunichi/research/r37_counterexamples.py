"""R37: 精度の高い命題の判例を、同じ形の反対の結果のチームと並べる（記述。判定はしない）。

    python cycles/c001-chunichi/research/r37_counterexamples.py cycles/c001-chunichi/outputs/season.jsonl t-2015 g-2016

形は誤差の幅での区分（rf_zone_se, ra_zone_se）。同じ形で結果（A・B）が逆の単位を比べる相手にする。
並べる指標は R36 と同じ13（r36_case.MEASURES）。2020年は除く。ネットワークを使わない。
"""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r36_case import MEASURES  # noqa: E402


def main(argv: list[str]) -> int:
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]
    key = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731
    by = {key(r): r for r in rows}
    for unit in argv[1:]:
        f = by[unit]
        shape = (f["rf_zone_se"], f["ra_zone_se"])
        same = [r for r in rows if (r["rf_zone_se"], r["ra_zone_se"]) == shape and r is not f]
        opp = [r for r in same if r["upper_half"] != f["upper_half"]]
        alike = [r for r in same if r["upper_half"] == f["upper_half"]]
        cls = "A" if f["upper_half"] else "B"
        print(f"\n### {f['team_name']} {f['season']}（{f['rank']}位、{cls}、形: 得点 {shape[0]:+d}・失点 {shape[1]:+d}、得失点差 {f['rd']:+d}）\n")
        print(f"同じ形: 結果が逆 {len(opp)}、同じ結果 {len(alike)}（{', '.join(map(key, alike)) or 'なし'}）\n")
        print("| 指標 | 中身 | この単位 | 結果が逆の範囲（中央値） | 範囲の外 |")
        print("|---|---|---|---|---|")
        for col, label in MEASURES:
            v, ov = f[col], [r[col] for r in opp if r[col] is not None]
            if v is None or not ov:
                print(f"| `{col}` | {label} | - | - | - |")
                continue
            out = "**外**（上）" if v > max(ov) else "**外**（下）" if v < min(ov) else "内"
            print(f"| `{col}` | {label} | {v:+.2f} | {min(ov):+.2f}〜{max(ov):+.2f}（{statistics.median(ov):+.2f}） | {out} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
