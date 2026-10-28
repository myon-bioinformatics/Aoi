#!/usr/bin/env python3
"""ε を 1e-4〜1/100 の梯子で動かし、C2 の基準を超える単位と、ε の波が消える単位を数える（事後。登録した基準の外）。

第 3 回で乱数の ε が 2 つ（1.76×10^-3、2.22×10^-3）、主食価格の 12 か月の窓の C2 を満たさなかった。外れたのが決め打ちの ε=1e-3 と同じ
1 単位かどうか、ε を動かすとどこで動くか、1/100 までのほかの単位ではどうかを見るための表で、判定ではない。
「超える」の基準は、登録した値と README の延長（eps_generality.threshold）。梯子は種に依らない固定の並び。

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/posthoc_eps_ladder.py \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir out/ladder/staple --repo .
  （物理量は --profile physical-monthly / physical-daily）
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LADDER = (1e-4, 3e-4, 5e-4, 7e-4, 8e-4, 1e-3, 2e-3, 3e-3, 5e-3, 7e-3, 9.99e-3, 1e-2)       # すべて 0 < ε ≤ 1/100
MAX_LISTED = 20                                                                           # 動いた単位を書き出す上限


def load_gen():
    spec = importlib.util.spec_from_file_location("eps_generality", HERE / "eps_generality.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["eps_generality"] = mod
    spec.loader.exec_module(mod)
    return mod


def dev_of(gen, r, e):
    """境界の単位 r の、ε と基準の ε の係数のずれ（相対）。ε の波が残っていない、比べられないなら None。"""
    a, b = r[gen.ekey(e)], r[gen.ekey(gen.REF_EPS)]
    if a["decay"] != e or b["decay"] != gen.REF_EPS or a["coefficient"] is None or b["coefficient"] is None:
        return None
    return abs(a["coefficient"] - b["coefficient"]) / abs(b["coefficient"])


def count_rows(gen, rows, ladder=LADDER):
    """境界の単位について、梯子の ε ごとに over（C2 の基準を超えた）と lost（ε の波が残らなかった）を数え、動いた単位の動きを返す。"""
    B = [r for r in rows if r["boundary"]]
    per = {gen.ekey(e): {"over": 0, "lost": 0} for e in ladder}
    moved = []
    for r in B:
        path, hit = [], False
        for e in ladder:
            k, d = gen.ekey(e), dev_of(gen, r, e)
            over, lost = d is not None and d > gen.threshold("c2", e), r[gen.ekey(e)]["decay"] != e
            per[k]["over"] += over
            per[k]["lost"] += lost
            hit = hit or over or lost
            path.append({"eps": e, "decay": r[k]["decay"], "period": r[k]["period"], "coefficient": r[k]["coefficient"], "dev": d})
        if hit:
            moved.append({"country": r["country"], "variable": r["variable"], "source": r["source"], "start": r.get("start"), "path": path})
    return {"boundary": len(B), "per_eps": per, "moved": moved[:MAX_LISTED], "moved_total": len(moved)}


def analyse(gen, sa, mod, series, cadence):
    eps = tuple(sorted(set(gen.EPS) | set(LADDER)))
    wins = {n: gen.tile(series, n, gen.CADENCE[cadence]["text"]) for n in gen.LENGTHS}
    bases = {n: gen.make_bases(sa, mod, [i / (n - 1) for i in range(n)], eps) for n in gen.LENGTHS}
    real = gen.real_rows(sa, bases, wins)
    return {"ladder": list(LADDER), "sets": {str(n): count_rows(gen, real[n]["rows"]) | {"units": len(real[n]["rows"])} for n in gen.LENGTHS}}


def render(gen, res) -> str:
    L = ["# ε の梯子（事後。登録した基準の外）", "",
         "C2 の基準（登録した値と、1e-3 より上・1e-6 より下は README の延長）を超えた境界の単位の数。`+N消` は ε の波が残らなかった単位の数。",
         "", "| 窓 | 境界の単位 | " + " | ".join(f"{e:g}" for e in res["ladder"]) + " |", "|---|---|" + "---|" * len(res["ladder"])]
    for n, s in res["sets"].items():
        cells = [f"{s['per_eps'][gen.ekey(e)]['over']}" + (f"+{s['per_eps'][gen.ekey(e)]['lost']}消" if s["per_eps"][gen.ekey(e)]["lost"] else "") for e in res["ladder"]]
        L.append(f"| {n} | {s['boundary']} / {s['units']} | " + " | ".join(cells) + " |")
    for n, s in res["sets"].items():
        for m in s["moved"]:
            L += ["", f"## 動いた単位（窓 {n}）: {m['country']} {m['variable']} {m['source']} {m['start']}", "",
                  "| ε | 残った波の減衰 | 周期 | 係数 | 基準の ε とのずれ |", "|---|---|---|---|---|"]
            L += [f"| {p['eps']:g} | {p['decay']:g} | {p['period']} | {p['coefficient']} | {'—' if p['dev'] is None else format(p['dev'], '.3g')} |" for p in m["path"]]
        if s["moved_total"] > len(s["moved"]):
            L += ["", f"（窓 {n}: 動いた単位は {s['moved_total']} 個。上の {len(s['moved'])} 個だけ書いた）"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--profile", default="staple")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    gen = load_gen()
    sa, mod = gen.load_modules(args.repo)
    p = gen.PROFILES[args.profile]
    res = analyse(gen, sa, mod, gen.read_series(args.csv, p["prefix"], p["cadence"]), p["cadence"])
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_eps_ladder.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_eps_ladder.md").write_text(render(gen, res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
