#!/usr/bin/env python3
"""事後の確認（登録した基準の外）: 境界の単位で、ε の大きさによって選ばれる周期が変わるか（探索）。

eps_generality.py を走らせたあと、基準 C2（窓 12 か月・ε=1e-3）を満たさなかった 1 窓の原因を調べるために足した。
結果を見たあとに書いたもので、基準ではない。eps_generality.py の出力は変更しない。

やること:
  1. 境界の単位（今のコードが減衰 0 を選んだ単位）のうち、ε=1e-3 または 1e-6 で選ばれる周期が ε=1e-9 のときと違う単位を数える
  2. その単位について、ε ごとに 2 つの周期の誤差の2乗和を、その周期の式だけで当てはめて比べる（差が EPS_WAVE_TIE = 1e-12 より大きいか）
  3. 周期ごとの境界の単位の数を、窓の長さごとに、野球の 24 単位と並べる
  4. 周期が変わった単位を除いたとき、C2 の相対のずれの最大がどうなるか

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/posthoc_boundary_forms.py \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir out --repo .
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("eps_generality", HERE / "eps_generality.py")
gen = importlib.util.module_from_spec(_spec)
sys.modules["eps_generality"] = gen
_spec.loader.exec_module(gen)

TIE = 1e-12          # sakanalytics.EPS_WAVE_TIE
BASEBALL_ROWS = ("cycles/c001-chunichi/exploratory/wave_eps_trial_results/wave_eps_rows_1e-06.jsonl",
                 "cycles/c001-chunichi/exploratory/wave_eps_2026_results/wave_eps_rows_1e-06.jsonl")


def changed_period(rows: list[dict]) -> dict:
    """境界の単位のうち、ε=1e-3 / 1e-6 で選ばれる周期が ε=1e-9 のときと違うものの添字。"""
    ref = gen.ekey(gen.EPS[-1])
    out = {}
    for e in gen.EPS[:-1]:
        k = gen.ekey(e)
        out[k] = [i for i, r in enumerate(rows) if r["boundary"] and r[k]["period"] != r[ref]["period"]]
    return out


def sse_of_form(sa, mod, xs: list[float], ys: list[float], eps: float, period: float) -> float:
    """周期 period・減衰 eps（0 なら今のコードの「減衰しない波」）の式だけで当てはめたときの誤差の2乗和。"""
    basis = mod.make_wave_basis(sa, eps)(xs)
    cand = [b for b in basis if b["per"] == period and b["lam"] == eps]
    if len(cand) != 1:
        raise ValueError(f"格子に周期 {period}・減衰 {eps} の式が {len(cand)} 個ある")
    f = sa.wave_fit(ys, cand, 0.0, 1.0)
    return len(ys) * f["rmse"] ** 2


def tie_table(sa, mod, ys: list[float], p_small: float, p_large: float) -> list[dict]:
    """ε ごとの、2 つの周期の誤差の2乗和（xs は窓の長さから決まる）。diff = p_large の式 − p_small の式。"""
    n = len(ys)
    xs = [i / (n - 1) for i in range(n)]
    out = []
    for eps in (0.0,) + gen.EPS:
        a = sse_of_form(sa, mod, xs, ys, eps, p_small)
        b = sse_of_form(sa, mod, xs, ys, eps, p_large)
        out.append({"eps": eps, "sse_small_eps_period": a, "sse_other_period": b, "diff": b - a})
    return out


def corrected_c2(rows: list[dict], skip: set) -> dict:
    """周期が変わった単位を除いたときの、係数の相対のずれの最大（ε=1e-3 / 1e-6 と 1e-9）。"""
    ref = gen.ekey(gen.EPS[-1])
    out = {}
    for e in gen.EPS[:-1]:
        k = gen.ekey(e)
        devs = []
        for i, r in enumerate(rows):
            if not r["boundary"] or i in skip:
                continue
            a, b = r[k], r[ref]
            if a["coefficient"] is None or b["coefficient"] is None:
                continue
            devs.append(abs(a["coefficient"] - b["coefficient"]) / abs(b["coefficient"]))
        out[k] = {"max": max(devs) if devs else None, "n": len(devs)}
    return out


def baseball_periods(repo: Path) -> dict:
    rows = []
    for p in BASEBALL_ROWS:
        rows += [json.loads(line) for line in (repo / p).read_text(encoding="utf-8").splitlines() if line.strip()]
    b = [r for r in rows if r["committed_wave_decay"] == 0]
    return {"units": len(rows), "boundary": len(b), "periods": dict(sorted(Counter(r["committed_wave_period"] for r in b).items()))}


def analyse(sa, mod, series: dict, repo: Path) -> dict:
    res = gen.compute(sa, mod, series)
    out = {"by_n": {}, "baseball": baseball_periods(repo), "units": []}
    for n in gen.LENGTHS:
        rows = res["rows"]["real"][str(n)]
        wins = [w for w in gen.tile(series, n) if gen.normalize(w["values"]) is not None]        # real_rows と同じ順・同じ除外
        if len(wins) != len(rows):
            raise ValueError(f"窓の数が合わない: {len(wins)} ≠ {len(rows)}")
        ch = changed_period(rows)
        skip = set().union(*map(set, ch.values()))
        bd = [r for r in rows if r["boundary"]]
        out["by_n"][str(n)] = {
            "boundary": len(bd), "periods": dict(sorted(Counter(r["period"] for r in bd).items())),
            "changed_period": {k: len(v) for k, v in ch.items()}, "c2_without_changed": corrected_c2(rows, skip)}
        for k, idx in ch.items():
            for i in idx:
                r = rows[i]
                ref = r[gen.ekey(gen.EPS[-1])]["period"]
                other = r[k]["period"]
                w = wins[i]
                if (w["si"], w["start"]) != (r["series_index"], r["start"]):
                    raise ValueError(f"窓と行が対応しない: {i}")
                ys = gen.normalize(w["values"])[1]
                out["units"].append({"n": n, "eps": float(k[1:]), "source": r["source"], "country": r["country"], "variable": r["variable"],
                                     "unit": r["unit"], "series_index": r["series_index"], "start": r["start"], "period_at_1e-9": ref, "period_at_eps": other,
                                     "table": tie_table(sa, mod, ys, ref, other)})
    return out


def render(res: dict) -> str:
    L = ["# 事後の確認: 境界の単位で、ε の大きさによって周期が変わるか", "",
         "**登録した基準の外**。[eps_generality.py](../eps_generality.py) の結果で C2（窓 12 か月、ε=1e-3）を満たさなかった 1 窓の原因を、結果を見たあとに調べたもの。", "",
         "## 境界の単位の周期", "", "| 窓の長さ | 境界の単位 | 周期ごとの数 | 周期が ε=1e-9 と違う（ε=1e-3 / 1e-6） | その単位を除いた係数のずれの最大（ε=1e-3 / 1e-6） |", "|---|---|---|---|---|"]
    for n, d in res["by_n"].items():
        per = "、".join(f"{p:g}: {c}" for p, c in d["periods"].items())
        ch = d["changed_period"]
        c2 = d["c2_without_changed"]
        L.append(f"| {n} か月 | {d['boundary']} | {per} | {ch[gen.ekey(1e-3)]} / {ch[gen.ekey(1e-6)]} | "
                 f"{c2[gen.ekey(1e-3)]['max']:.3g} / {c2[gen.ekey(1e-6)]['max']:.3g} |")
    b = res["baseball"]
    L += ["", f"野球（2013〜2026年）の境界の単位 {b['boundary']} / {b['units']} の周期: " + "、".join(f"{p:g}: {c}" for p, c in b["periods"].items()), ""]
    L += ["## 周期が変わった単位", ""]
    if not res["units"]:
        L.append("なし。")
    for u in res["units"]:
        L += [f"### {u['n']} か月・ε={u['eps']:g}: {u['source']} {u['country']} {u['variable']}（{u['unit']}、系列 {u['series_index']}）{u['start']} から", "",
              f"周期は ε=1e-9 で {u['period_at_1e-9']:g}、{u['eps']:g} で {u['period_at_eps']:g}。周期は 2 → 1 → 0.75 → … の順に並んでいて、"
              f"あとに並んだ式が、先の式より誤差の2乗和で {TIE:g} を超えて小さいときだけ入れ替わる。2 つの周期の式だけで当てはめた誤差の2乗和:", "",
              "| ε（0 は今のコード） | ε=1e-9 で選ばれた周期の式 | ε で選ばれた周期の式 | 差（後者 − 前者） |", "|---|---|---|---|"]
        for t in u["table"]:
            L.append(f"| {t['eps']:g} | {t['sse_small_eps_period']:.9g} | {t['sse_other_period']:.9g} | {t['diff']:.3g} |")
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    sa, mod = gen.load_modules(args.repo)
    res = analyse(sa, mod, gen.read_series(args.csv), args.repo)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_boundary_forms.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_boundary_forms.md").write_text(render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
