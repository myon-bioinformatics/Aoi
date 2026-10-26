#!/usr/bin/env python3
"""そのデータで、ε を動かしたとき結果がどこまで動かないかを記録する（事後。登録した基準の外）。

ε の範囲を定数として決めるためのものではない。「このデータでは、ε がこの範囲なら、これだけの単位が動かなかった」という観測を、
データごとに残して並べるためのもの。別のデータには別の数字が出る（出てよい）。

数えるもの（窓の長さ 12 / 24 / 48 ごと。合計も出す）:
  境界の単位（減衰 0 で当てはまる単位）: ε の波が残り、係数（落ち着く位置 × ε）が基準の ε=1e-9 と相対 δ 以内（δ = 10%, 1%, 0.1%, 0.01%）。
    両方とも始まりで落ち着く単位は、C2 と同じく比べず、収まったに数える（ε に依らない）
  境界でない単位: 選ばれる式が ε を入れる前と同じ
  乱数の選び方（eps_generality.draw_coefficients）の重みのうち、ε がその値以下になる割合

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/eps_range_profile.py \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir out/range/staple --repo .
  別のデータは --csv に縦持ちの CSV、--prefix に変数名の頭、--cadence に month か day（--profile の代わり）。
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = (1e-2, 5e-3, 3e-3, 2e-3, 1e-3, 7e-4, 5e-4, 3e-4, 2e-4, 1e-4, 1e-5, 1e-6, 1e-7, 1e-9, 1e-11, 1e-13)       # すべて 0 < ε ≤ 1/100
DELTAS = (0.1, 0.01, 0.001, 0.0001)


def load_gen():
    spec = importlib.util.spec_from_file_location("eps_generality", HERE / "eps_generality.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["eps_generality"] = mod
    spec.loader.exec_module(mod)
    return mod


def coverage_rows(gen, rows, grid=GRID, deltas=DELTAS):
    """窓の長さ 1 つ分の行から、格子の ε ごとに収まった単位の数などを数える。"""
    B = [r for r in rows if r["boundary"]]
    NB = [r for r in rows if not r["boundary"]]
    ref = gen.ekey(gen.REF_EPS)
    per = {}
    for e in grid:
        k = gen.ekey(e)
        ok, lost, mism, start = {format(d, "g"): 0 for d in deltas}, 0, 0, 0
        for r in B:
            a, b = r[k], r[ref]
            if a["decay"] != e or b["decay"] != gen.REF_EPS:
                lost += 1                                      # ε の波が残らなかった単位
                continue
            if a["at_start"] != b["at_start"]:
                mism += 1                                      # 片方だけ始まりで落ち着く単位
                continue
            if a["at_start"]:
                start += 1
                dev = 0.0
            else:
                dev = abs(a["coefficient"] - b["coefficient"]) / abs(b["coefficient"])
            for d in deltas:
                ok[format(d, "g")] += dev <= d
        same = sum(1 for r in NB if (r[k]["decay"], r[k]["period"]) == (r["decay"], r["period"]))
        per[k] = {"eps": e, "ok": ok, "lost": lost, "mismatch": mism, "at_start": start, "nonboundary_same": same}
    return {"boundary": len(B), "nonboundary": len(NB), "per_eps": per}


def pool(parts):
    """窓の長さごとの結果を足し合わせる。"""
    out = {"boundary": sum(p["boundary"] for p in parts), "nonboundary": sum(p["nonboundary"] for p in parts), "per_eps": {}}
    for k, first in parts[0]["per_eps"].items():
        out["per_eps"][k] = {"eps": first["eps"], "ok": {d: sum(p["per_eps"][k]["ok"][d] for p in parts) for d in first["ok"]}}
        for f in ("lost", "mismatch", "at_start", "nonboundary_same"):
            out["per_eps"][k][f] = sum(p["per_eps"][k][f] for p in parts)
    return out


def largest_full(res, delta):
    """格子の ε を小さい方から見て、境界の単位がすべて δ 以内に収まっている間の最大の ε（途中で外れたらそこで止める）。
    一番小さい ε で外れる、または境界の単位がないときは None。"""
    d, best = format(delta, "g"), None
    if not res["boundary"]:
        return None
    for v in sorted(res["per_eps"].values(), key=lambda v: v["eps"]):
        if v["ok"][d] != res["boundary"]:
            break
        best = v["eps"]
    return best


def share_le(gen, x):
    """乱数の選び方（draw_coefficients の ε）で ε <= x になる確率。N は N_MIN に、各段で確率 P_STOP で止まる回数を足したもの（N_CAP で止める）、
    A は百分の一の整数 A_MIN〜A_MAX を一様に。決め打ちの値と同じ値を除く効果は小さいので無視する。"""
    p, total = gen.P_STOP, 0.0
    for n in range(gen.N_MIN, gen.N_CAP + 1):
        steps = n - gen.N_MIN
        mass = (1 - p) ** steps * (1.0 if n == gen.N_CAP else p)
        m = math.floor(x * 10.0 ** n * 100 + 1e-9)                       # A × 100 が m 以下の個数を数える
        total += mass * min(max(m - gen.A_MIN + 1, 0), gen.A_MAX - gen.A_MIN + 1) / (gen.A_MAX - gen.A_MIN + 1)
    return total


def analyse(gen, sa, mod, series, cadence, grid=GRID):
    eps = tuple(sorted(set(gen.EPS) | set(grid)))
    wins = {n: gen.tile(series, n, gen.CADENCE[cadence]["text"]) for n in gen.LENGTHS}
    bases = {n: gen.make_bases(sa, mod, [i / (n - 1) for i in range(n)], eps) for n in gen.LENGTHS}
    real = gen.real_rows(sa, bases, wins)
    sets = {str(n): coverage_rows(gen, real[n]["rows"], grid) for n in gen.LENGTHS}
    total = pool(list(sets.values()))
    return {"grid": list(grid), "deltas": list(DELTAS), "sets": sets, "total": total,
            "full_coverage_max_eps": {format(d, "g"): largest_full(total, d) for d in DELTAS},
            "draw_share_le": {format(e, "g"): share_le(gen, e) for e in grid}}


def render(gen, res) -> str:
    t, B, NB = res["total"], res["total"]["boundary"], res["total"]["nonboundary"]
    ds = [format(d, "g") for d in res["deltas"]]
    L = ["# このデータで、ε がどこまで動かなかったか（事後。登録した基準の外）", "",
         "**このデータでの観測で、ε の範囲を決める値ではありません。** 別のデータには別の数字が出ます。",
         f"窓の長さ 12 / 24 / 48 の合計で、境界の単位 {B}、境界でない単位 {NB}。", "",
         "## ε ごとに収まった割合", "",
         "境界の単位が、基準の ε=1e-9 の係数と相対 δ 以内に収まった割合（δ ごと）。`消`は ε の波が残らなかった単位の数。右端は、境界でない単位で選ばれる式が変わらなかった割合。", "",
         "| ε | " + " | ".join(f"δ={float(d) * 100:g}%" for d in ds) + " | 消 | 式が変わらない（境界でない） |", "|---|" + "---|" * (len(ds) + 2)]
    for k, v in sorted(t["per_eps"].items(), key=lambda kv: -kv[1]["eps"]):
        L.append(f"| {v['eps']:g} | " + " | ".join(f"{v['ok'][d] / B * 100:.2f}%" if B else "—" for d in ds) + f" | {v['lost']} | "
                 + (f"{v['nonboundary_same'] / NB * 100:.3f}% ({NB - v['nonboundary_same']} 変わった)" if NB else "—") + " |")
    L += ["", "## 格子の小さい方から見て、すべての境界の単位が δ 以内に収まっていた最大の ε", ""]
    for d in ds:
        m = res["full_coverage_max_eps"][d]
        L.append(f"- δ = {float(d) * 100:g}%: " + ("境界の単位がないので判定できない" if not B else "なし（格子の一番小さい ε でも外れた単位がある）" if m is None
                                                else f"{m:g}（これ以下の格子の ε ではすべて収まった）"))
    L += ["", "## 乱数の選び方の重み", "",
          f"`draw_coefficients` が ε を選ぶとき、ε がその値以下になる確率（N = {gen.N_MIN} から、各段で確率 {gen.P_STOP:g} で止まる）。", "",
          "| ε 以下 | 確率 |", "|---|---|"]
    L += [f"| {e:g} | {res['draw_share_le'][format(e, 'g')] * 100:.1f}% |" for e in sorted(res["grid"], reverse=True)]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--profile", default="staple", help="eps_generality.PROFILES の名前。別のデータは --prefix / --cadence で上書き")
    ap.add_argument("--prefix", default=None, help="変数名の頭（省略は profile の値）")
    ap.add_argument("--cadence", default=None, choices=["month", "day"], help="刻み（省略は profile の値）")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    gen = load_gen()
    sa, mod = gen.load_modules(args.repo)
    p = gen.PROFILES[args.profile]
    prefix, cadence = args.prefix or p["prefix"], args.cadence or p["cadence"]
    series = gen.read_series(args.csv, prefix, cadence)
    if not series:
        raise SystemExit(f"変数名が {prefix!r} で始まる行が {args.csv} にない")
    res = analyse(gen, sa, mod, series, cadence)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "eps_range_profile.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "eps_range_profile.md").write_text(render(gen, res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
