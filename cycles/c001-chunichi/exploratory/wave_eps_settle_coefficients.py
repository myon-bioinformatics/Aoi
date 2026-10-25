#!/usr/bin/env python3
"""波の減衰 0 → ε の試し: 落ち着く位置を「係数 × 10^n」で書く（探索）。

ε を ε = a × 10^-n（1 ≤ a < 10）と書くと、減衰 λ = ε の波の落ち着く位置は、ε を小さくした範囲で
「係数 × 10^n」の形になる（ε を 10 倍小さくすると指数 n が 1 上がり、係数はほとんど動かない）。
係数は決めた数ではなく、保存済みの行（wave_eps_trial.py の wave_eps_rows_<ε>.jsonl、ε が 2 つ以上）の
settle_x を 10^n で割って出てきた数で、a を替えれば 1/a 倍になる。
ここでは単位ごとに、ε ごとの落ち着く位置を「仮数 × 10^指数」で並べ、最小の ε の行の係数を基準に、
ほかの ε の位置がこの形からどれだけ外れるか（絶対・相対の最大）を出す。振れ幅は、落ち着く位置の式
（x0 + ln(振れ幅 / 0.5) / λ）に a = 1 の係数を入れて戻した値（0.5 × exp(係数)）。振れ幅が最初から小さい単位は、
落ち着く位置が ε によらず一定（settled_at_start）で、係数の形には載せない。

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


def validate_eps(eps: float) -> None:
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) or not math.isfinite(eps) or eps <= 0:
        raise ValueError(f"ε は有限の正数でなければならない: {eps!r}")


def load(path: Path) -> tuple[float, dict]:
    eps, units = set(), {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        try:
            validate_eps(r["eps_provisional"])
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        key = (r["season"], r["team"])
        if key in units:
            raise ValueError(f"{path}:{line_number}: 単位が重複している: {key}")
        eps.add(r["eps_provisional"])
        units[key] = r
    if len(eps) != 1:
        raise ValueError(f"{path}: ε が 1 つに決まらない {sorted(eps)}")
    return eps.pop(), units


def eps_form(eps: float) -> tuple[float, int]:
    """ε = a × 10^-n（1 ≤ a < 10）の (a, n)。"""
    validate_eps(eps)
    n = -math.floor(math.log10(eps) + 1e-12)
    return round(eps * 10 ** n, 12), n


def sci(x: float) -> str:
    """x を「仮数×10^指数」（仮数は有効数字 3 桁）で書く。"""
    m, e = f"{x:.2e}".split("e")
    return f"{m}×10^{int(e)}"


def coefficients(by_eps: dict) -> list[dict]:
    """by_eps: {ε: {(season, team): 行}}。減衰 0 だった単位ごとに、ε ごとの落ち着く位置と係数（位置 / 10^n）、
    最小の ε の係数を基準にしたときの外れ（与えた ε のうち最大）を返す。"""
    if len(by_eps) < 2:
        raise ValueError("ε が 2 つ以上いる")
    for e in by_eps:
        validate_eps(e)
    eps = sorted(by_eps)
    lo, mid = eps[0], eps[1]
    units = set(by_eps[lo])
    for e in eps[1:]:
        actual = set(by_eps[e])
        if actual != units:
            raise ValueError(f"ε={e:g}: 単位集合が ε={lo:g} と一致しない: "
                             f"欠落={sorted(units - actual)}, 余剰={sorted(actual - units)}")
    a_lo, n_lo = eps_form(lo)
    out = []
    for key in sorted(by_eps[lo]):
        if by_eps[lo][key]["committed_wave_decay"] != 0:
            continue
        s = {e: by_eps[e][key]["eps_wave_settle_x"] for e in eps}
        if any(v is None or by_eps[e][key]["eps_wave_decay"] != e for e, v in s.items()):
            raise ValueError(f"{key}: ε の波が選ばれていない行がある")
        if abs(s[lo] - s[mid]) <= SAME * max(1.0, abs(s[lo])):
            out.append({"season": key[0], "team": key[1], "settled_at_start": True, "position": s[lo], "coefficient": None,
                        "amp": None, "by_eps": [], "abs_miss": None, "rel_miss": None})
            continue
        ref = s[lo] * a_lo / 10 ** n_lo              # a = 1 に揃えた係数（a を替えると 1/a 倍になる）
        per, miss = [], []
        for e in eps:
            a, n = eps_form(e)
            predicted = ref / a * 10 ** n            # 最小の ε の係数を、この ε の a と n に置き直した位置
            per.append({"eps": e, "a": a, "n": n, "settle": s[e], "coefficient": s[e] / 10 ** n})
            miss.append((abs(s[e] - predicted), abs(s[e] - predicted) / abs(s[e])))
        out.append({"season": key[0], "team": key[1], "settled_at_start": False, "position": None, "coefficient": per[0]["coefficient"],
                    "amp": SETTLE * math.exp(ref), "by_eps": per, "abs_miss": max(m[0] for m in miss), "rel_miss": max(m[1] for m in miss)})
    return out


def _head(e: float) -> str:
    a, n = eps_form(e)
    return f"ε = {a:g}×10^-{n}"


def render(rows: list[dict], eps: list[float]) -> str:
    moving = [r for r in rows if not r["settled_at_start"]]
    lines = ["# 落ち着く位置 = 係数 × 10^n（ε = a × 10^-n）（探索・暫定）", "",
             f"ε = {', '.join(f'{e:g}' for e in eps)} の行から。ε を 10 倍小さくすると落ち着く位置は約 10 倍遠くなり（指数 n が 1 上がる）、"
             "係数（落ち着く位置 / 10^n）はほとんど動かない。係数は決めた数ではなく行から出てきた数で、a を替えれば 1/a 倍になる。"
             "ε の値は暫定で、結論には使わない。", "",
             f"- 減衰 0 だった単位: {len(rows)}。落ち着く位置が最初から ε によらず一定: {len(rows) - len(moving)}",
             f"- 係数（最小の ε の行、a = {eps_form(eps[0])[0]:g}）: {min(r['coefficient'] for r in moving):.4f} 〜 {max(r['coefficient'] for r in moving):.4f}",
             f"- 最小の ε の係数で、ほかの ε の位置を言い当てたときの外れ（最大）: 絶対 {max(r['abs_miss'] for r in moving):.3f}（シーズン 1 つぶんが 1）、"
             f"相対 {max(r['rel_miss'] for r in moving):.2e}", "",
             "| 年 | 球団 | " + " | ".join(_head(e) for e in reversed(eps)) + " | 係数（最小の ε） | 振れ幅 | 外れ（絶対 / 相対） |",
             "|---|---|" + "---|" * (len(eps) + 3)]
    for r in rows:
        if r["settled_at_start"]:
            lines.append(f"| {r['season']} | {r['team']} | （最初から一定。位置 {r['position']:.4f}）" + " | —" * (len(eps) + 2) + " |")
        else:
            by = {p["eps"]: p for p in r["by_eps"]}
            cells = " | ".join(sci(by[e]["settle"]) for e in reversed(eps))
            lines.append(f"| {r['season']} | {r['team']} | {cells} | {r['coefficient']:.4f} | {r['amp']:.3f} | {r['abs_miss']:.3f} / {r['rel_miss']:.1e} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=Path, nargs="+", required=True, help="wave_eps_rows_<ε>.jsonl（ε が 2 つ以上）")
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args(argv)
    try:
        by_eps = dict(load(p) for p in args.rows)
        if len(by_eps) != len(args.rows):
            raise ValueError("同じ ε の行ファイルが重なっている")
        rows = coefficients(by_eps)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    args.out_json.write_text(json.dumps({"eps": sorted(by_eps), "units": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render(rows, sorted(by_eps)), encoding="utf-8")
    print(f"書き出し: {args.out_json}, {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
