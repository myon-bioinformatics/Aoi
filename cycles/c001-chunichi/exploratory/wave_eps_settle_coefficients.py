#!/usr/bin/env python3
"""波の減衰 0 → ε の試し: 落ち着く位置を ε の関数として書く（探索）。

減衰 λ = ε の波の「落ち着く位置」は settle_x = x0 + ln(振れ幅 / 0.5) / ε で、振れ幅も ε にわずかに依る。
ε を小さくした範囲では settle_x = K / ε + c（K, c は単位ごとの定数）と書ける。この式を、保存済みの行
（wave_eps_trial.py の wave_eps_rows_<ε>.jsonl、ε が 2 つ以上）の settle_x から、ε の小さい 2 つで K, c を決め、
残りの ε で当たるか確かめる。振れ幅が最初から 0.5 順位以下の単位は、落ち着く位置が ε によらず一定（settled_at_start）。

標準ライブラリのみ。ε の値は暫定の置き場所で、結論には使わない。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/wave_eps_settle_coefficients.py \\
      --rows cycles/c001-chunichi/exploratory/wave_eps_trial_results/wave_eps_rows_*.jsonl \\
      --out-json /tmp/coef.json --out-md /tmp/coef.md
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

SAME = 1e-9          # 2 つの ε で落ち着く位置が（相対で）これ以下しか違わなければ、ε によらない一定の位置とみなす
SETTLE = 0.5         # sakanalytics.WAVE_SETTLE（ゆれの幅が半順位を下回る位置）


def load(path: Path) -> tuple[float, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    eps = {r["eps_provisional"] for r in rows}
    if len(eps) != 1:
        raise ValueError(f"{path}: ε が 1 つに決まらない {sorted(eps)}")
    return eps.pop(), {(r["season"], r["team"]): r for r in rows}


def coefficients(by_eps: dict) -> list[dict]:
    """by_eps: {ε: {(season, team): 行}}。減衰 0 だった単位ごとに K, c と、残りの ε での当てはまりの悪さを返す。"""
    eps = sorted(by_eps)
    if len(eps) < 2:
        raise ValueError("ε が 2 つ以上いる")
    lo, mid = eps[0], eps[1]
    out = []
    for key in sorted(by_eps[lo]):
        if by_eps[lo][key]["committed_wave_decay"] != 0:
            continue
        s = {e: by_eps[e][key]["eps_wave_settle_x"] for e in eps}
        if any(v is None or by_eps[e][key]["eps_wave_decay"] != e for e, v in s.items()):
            raise ValueError(f"{key}: ε の波が選ばれていない行がある")
        if abs(s[lo] - s[mid]) <= SAME * max(1.0, abs(s[lo])):
            out.append({"season": key[0], "team": key[1], "settled_at_start": True, "K": 0.0, "c": s[lo], "amp": SETTLE, "residual": 0.0})
            continue
        k = (s[lo] - s[mid]) * lo * mid / (mid - lo)
        c = s[mid] - k / mid
        res = max(abs(s[e] - (c + k / e)) / max(1.0, abs(s[e])) for e in eps)
        out.append({"season": key[0], "team": key[1], "settled_at_start": False, "K": k, "c": c, "amp": SETTLE * math.exp(k), "residual": res})
    return out


def render(rows: list[dict], eps: list[float]) -> str:
    moving = [r for r in rows if not r["settled_at_start"]]
    lines = ["# 落ち着く位置 = K/ε + c（探索・暫定）", "",
             f"ε = {', '.join(f'{e:g}' for e in eps)} の行から。K, c は ε の小さい 2 つで決め、残りの ε で当たるか確かめた。ε の値は暫定で、結論には使わない。", "",
             f"- 減衰 0 だった単位: {len(rows)}。振れ幅が最初から {SETTLE} 順位以下（ε によらず一定）: {len(rows) - len(moving)}",
             f"- K = ln(振れ幅 / {SETTLE}): {min(r['K'] for r in moving):.4f} 〜 {max(r['K'] for r in moving):.4f}。c: {min(r['c'] for r in moving):.4f} 〜 {max(r['c'] for r in moving):.4f}",
             f"- 残りの ε での相対のずれ（最大）: {max(r['residual'] for r in moving):.2e}", "",
             "| 年 | 球団 | K | c | 振れ幅 | 残りの ε でのずれ |", "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['season']} | {r['team']} | " + ("（最初から一定）| " + f"{r['c']:.4f} | — | —" if r["settled_at_start"]
                                                          else f"{r['K']:.4f} | {r['c']:.4f} | {r['amp']:.3f} | {r['residual']:.1e}") + " |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=Path, nargs="+", required=True, help="wave_eps_rows_<ε>.jsonl（ε が 2 つ以上）")
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args(argv)
    by_eps = dict(load(p) for p in args.rows)
    if len(by_eps) != len(args.rows):
        print("同じ ε の行ファイルが重なっている", file=sys.stderr)
        return 2
    rows = coefficients(by_eps)
    args.out_json.write_text(json.dumps({"eps": sorted(by_eps), "units": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render(rows, sorted(by_eps)), encoding="utf-8")
    print(f"書き出し: {args.out_json}, {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
