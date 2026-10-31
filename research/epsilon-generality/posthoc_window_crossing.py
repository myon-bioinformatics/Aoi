#!/usr/bin/env python3
"""ε を上げたとき、すでに分かっている 3 つの窓で選ばれる式が変わる ε を、1 窓ずつ細かく探す（事後。登録した基準の外）。

背景: 事後の梯子（posthoc_eps_ladder.py）で、ε を 1e-4〜1/100 に動かしたとき選ばれる式が変わった単位は 3 つだけだった。
  MDA の高品質小麦粉（2024-01 からの 12 か月）: 周期 1 → 2、梯子で 7×10^-4（動かない）→ 8×10^-4（動く）
  NIC の低品質の米（2017-10 からの 12 か月）: 周期 1 → 0.75、梯子で 5×10^-3（動かない）→ 7×10^-3（動く）
  Mauna Loa の CO2（1980-05 からの 48 か月）: ε の波（周期 0.25）→ 減衰 5・周期 2 の式、梯子で 7×10^-3 → 9.99×10^-3
登録した基準は ε = 1e-3, 1e-6, 1e-9 でしか見ない。NIC と Mauna Loa は 1e-3 より上でしか動かないので、登録した基準では
NIC の窓は他の窓と分けられない（MDA の窓が 8×10^-4 から動くので、集合の数え方では隠れる）。この確認は、動く ε が
窓ごとにどこにあるかを細かく見るためのもので、基準を決めない。ε の値をどうするかは決めない。

やること（窓ごとに）:
  1. 梯子の 2 点（lo: 動かない / hi: 動く）の間を、ε の対数で二分して、選ばれる式が変わる ε* を 0.1% の幅で挟む
  2. その二分を、許容 EPS_WAVE_TIE を 1e-15 / 1e-12（今の値）/ 1e-9 にして繰り返す（許容を ×10^±3）
  3. lo から 1/100 まで ε の対数で 60 点を取り、選ばれる式が隣どうしで変わる回数を数える（戻って変わるなら 2 以上）
  4. ε* を挟む 2 点と、登録した ε（1e-3, 1e-6, 1e-9）で、変わる前の式と変わった後の式を、それぞれの式だけで当てはめた
     誤差の2乗和を並べる（差 = 後 − 前。正なら前の式のほうがよく合う）

予想（走らせる前に書く。結果を見て変えない）:
  (a) 3 窓とも、梯子の 2 点で式が違う（lo は前の式、hi は後の式）という梯子の結果が、この実行で再現する。再現しない窓があれば二分は止まる。
  (b) 3 窓とも、許容を ×10^±3 にしても ε* は 1% も動かない（相対）。動くのは許容に決まる切り替えではなく、2 つの式の
      誤差の2乗和が入れ替わる点だから。
  (c) 3 窓とも、60 点の並びで式が変わる回数は 1 回（戻って変わることはない）。
  (d) ε* を挟む 2 点（下と上）で、前の式と後の式の誤差の2乗和の差の絶対値は、小さいほうの誤差の2乗和の 1e-3 倍より小さい
      （切り替わりは 2 つの式のなめらかな入れ替わりで、飛びではない）。差の符号や、許容 1e-12 との大小には予想を置かない
      （どちらの式が候補の並びで先かによって、入れ替わりの点が許容の分だけ前後する）。
  (e) 登録した ε では、MDA は 1e-3 で式が変わっている（8×10^-4 より上）。NIC と Mauna Loa は 3 つとも変わらない。
  すでに見たもの: 梯子の表（上記の 3 窓のどの ε で式が変わったか）。細かい二分はまだ見ていない。

結論の範囲: この 3 窓（主食価格 2 つ、物理量 1 つ）についてだけ。ε の上限や EPS_WAVE_TIE の値は決めない。

使い方（リポジトリの直下から。入力が無い窓は飛ばす）:
  uv run --locked python research/epsilon-generality/posthoc_window_crossing.py \\
      --staple-csv research/staple-price-survey/staple_survey_vertical.csv [--physical-monthly-csv physical_monthly_vertical.csv] \\
      --outdir out/crossing --repo .
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("posthoc_boundary_forms", HERE / "posthoc_boundary_forms.py")
pbf = importlib.util.module_from_spec(_spec)
sys.modules["posthoc_boundary_forms"] = pbf
_spec.loader.exec_module(pbf)
gen = pbf.gen

WINDOWS = (
    {"id": "MDA 小麦粉（高品質）", "input": "staple", "n": 12, "country": "MDA", "variable": "staple_price:wheat_flour_high_quality_kg",
     "start": "2024-01", "lo": 7e-4, "hi": 8e-4},
    {"id": "NIC 米（低品質）", "input": "staple", "n": 12, "country": "NIC", "variable": "staple_price:rice_low_quality_46_kg",
     "start": "2017-10", "lo": 5e-3, "hi": 7e-3},
    {"id": "Mauna Loa CO2", "input": "physical-monthly", "n": 48, "country": "Mauna Loa", "variable": "physical:co2",
     "start": "1980-05", "lo": 7e-3, "hi": 9.99e-3},
)
TOLS = (1e-15, 1e-12, 1e-9)          # 1e-12 は今の EPS_WAVE_TIE
REL_WIDTH = 1e-3                     # 二分で挟む幅（hi / lo − 1）
GRID_POINTS = 60
EPS_TOP = 1e-2


def window_values(series: dict, spec: dict, text) -> list[float]:
    """series（read_series の結果）から、spec の窓の値を取り出し、値の幅を SCALE にそろえた y を返す。ちょうど 1 つ見つからなければ止める。"""
    hits = [w for w in gen.tile(series, spec["n"], text)
            if w["key"][0] == spec["country"] and w["key"][1] == spec["variable"] and w["start"] == spec["start"]]
    if len(hits) != 1:
        raise ValueError(f"窓が {len(hits)} 個見つかった（1 個のはず）: {spec['id']}")
    nm = gen.normalize(hits[0]["values"])
    if nm is None:
        raise ValueError(f"窓の値が一定: {spec['id']}")
    return nm[1]


@contextmanager
def tie_tolerance(sa, tol: float):
    old = sa.EPS_WAVE_TIE
    sa.EPS_WAVE_TIE = tol
    try:
        yield
    finally:
        sa.EPS_WAVE_TIE = old


def form_at(sa, mod, ys: list[float], eps: float, tol: float | None = None) -> tuple:
    """ε の格子で wave_fit が選ぶ式: ("ε", 周期)（減衰が ε のまま残った波）か (減衰, 周期)。tol を渡すと EPS_WAVE_TIE をその値にして当てはめる。"""
    n = len(ys)
    basis = mod.make_wave_basis(sa, eps)([i / (n - 1) for i in range(n)])
    with gen.settle_tolerance(sa, gen.PRIMARY_TAU):
        if tol is None:
            f = sa.wave_fit(ys, basis, 0.0, 1.0)
        else:
            with tie_tolerance(sa, tol):
                f = sa.wave_fit(ys, basis, 0.0, 1.0)
    return ("ε", f["period"]) if f["decay"] == eps else (f["decay"], f["period"])


def sse_of(sa, mod, ys: list[float], eps: float, form: tuple) -> float:
    """その式だけで当てはめた誤差の2乗和（格子は ε の格子）。"""
    n = len(ys)
    lam = eps if form[0] == "ε" else form[0]
    return pbf.sse_of_form(sa, mod, [i / (n - 1) for i in range(n)], ys, eps, form[1], lam=lam)


def bisect(fn, lo: float, hi: float, rel: float = REL_WIDTH) -> tuple[float, float]:
    """fn(lo) と fn(hi) が違うとき、ε の対数で二分して、fn が lo の値と同じ最大の点と違う最小の点を hi/lo − 1 < rel の幅で挟む。"""
    base = fn(lo)
    if fn(hi) == base:
        raise ValueError("lo と hi で式が同じ: 挟めない")
    while hi / lo - 1 >= rel:
        mid = math.sqrt(lo * hi)
        if fn(mid) == base:
            lo = mid
        else:
            hi = mid
    return lo, hi


def grid(lo: float, top: float = EPS_TOP, points: int = GRID_POINTS) -> list[float]:
    return [lo * (top / lo) ** (i / (points - 1)) for i in range(points)]


def changes_along(forms: list) -> int:
    return sum(1 for a, b in zip(forms, forms[1:]) if a != b)


def analyse_window(sa, mod, ys: list[float], spec: dict) -> dict:
    lo, hi = spec["lo"], spec["hi"]
    before, after = form_at(sa, mod, ys, lo), form_at(sa, mod, ys, hi)
    out = {"id": spec["id"], "n": spec["n"], "start": spec["start"], "bracket": [lo, hi], "form_lo": list(before), "form_hi": list(after),
           "by_tolerance": {}}
    for tol in TOLS:
        a, b = bisect(lambda e: form_at(sa, mod, ys, e, tol), lo, hi)
        out["by_tolerance"][f"{tol:g}"] = {"below": a, "above": b, "eps_star": math.sqrt(a * b)}
    base = out["by_tolerance"]["1e-12"]
    out["rel_shift_of_eps_star"] = max(abs(v["eps_star"] / base["eps_star"] - 1) for v in out["by_tolerance"].values())
    forms = [form_at(sa, mod, ys, e) for e in grid(lo)]
    out["changes_along_grid"] = changes_along(forms)
    out["gaps"] = [{"eps": e, "label": lab, "sse_before": sse_of(sa, mod, ys, e, before), "sse_after": sse_of(sa, mod, ys, e, after),
                    "chosen": list(form_at(sa, mod, ys, e))}
                   for lab, e in (("ε* の下", base["below"]), ("ε* の上", base["above"]), ("1e-3", 1e-3), ("1e-6", 1e-6), ("1e-9", 1e-9))]
    for g in out["gaps"]:
        g["diff"] = g["sse_after"] - g["sse_before"]
    out["edge_rel_diff"] = max(abs(g["diff"]) / min(g["sse_before"], g["sse_after"]) for g in out["gaps"][:2])
    return out


def analyse(sa, mod, inputs: dict, specs=WINDOWS) -> dict:
    res = {"windows": [], "skipped": []}
    for spec in specs:
        if spec["input"] not in inputs:
            res["skipped"].append(spec["id"])
            continue
        series, text = inputs[spec["input"]]
        res["windows"].append(analyse_window(sa, mod, window_values(series, spec, text), spec))
    return res


def fmt_form(f) -> str:
    return f"減衰 {f[0] if f[0] == 'ε' else format(f[0], 'g')}・周期 {'なし' if f[1] is None else format(f[1], 'g')}"


def render(res: dict) -> str:
    L = ["# 式が変わる ε を窓ごとに細かく探す（事後。登録した基準の外）", "",
         "予想は [posthoc_window_crossing.py](../../posthoc_window_crossing.py) の冒頭に、走らせる前に書いたもの。"
         "二分は ε の対数で、0.1% の幅で挟む。許容は EPS_WAVE_TIE（今は 1e-12）を ×10^±3 に変えて繰り返したもの。", ""]
    if res["skipped"]:
        L += [f"入力が無くて飛ばした窓: {'、'.join(res['skipped'])}", ""]
    L += ["| 窓 | 梯子の2点 | 変わる前 → 後 | ε*（許容 1e-15 / 1e-12 / 1e-9） | ε* の相対の動き（最大） | 60 点で式が変わる回数 | ε* を挟む 2 点の差 / 誤差の2乗和（大きいほう） |", "|---|---|---|---|---|---|---|"]
    for w in res["windows"]:
        t = w["by_tolerance"]
        L.append(f"| {w['id']}（{w['n']} 点、{w['start']} から） | {w['bracket'][0]:g} / {w['bracket'][1]:g} | "
                 f"{fmt_form(w['form_lo'])} → {fmt_form(w['form_hi'])} | "
                 f"{t['1e-15']['eps_star']:.4g} / {t['1e-12']['eps_star']:.4g} / {t['1e-09']['eps_star']:.4g} | {w['rel_shift_of_eps_star']:.2g} | "
                 f"{w['changes_along_grid']} | {w['edge_rel_diff']:.2g} |")
    for w in res["windows"]:
        L += ["", f"## {w['id']}", "", "変わる前の式と後の式を、それぞれの式だけで当てはめた誤差の2乗和（差 = 後 − 前。正なら前の式のほうがよく合う）:", "",
              "| 場所 | ε | 前の式 | 後の式 | 差 | wave_fit が選んだ式 |", "|---|---|---|---|---|---|"]
        for g in w["gaps"]:
            L.append(f"| {g['label']} | {g['eps']:.6g} | {g['sse_before']:.9g} | {g['sse_after']:.9g} | {g['diff']:.3g} | {fmt_form(g['chosen'])} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staple-csv", type=Path)
    ap.add_argument("--physical-monthly-csv", type=Path)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    if not (args.staple_csv or args.physical_monthly_csv):
        ap.error("--staple-csv か --physical-monthly-csv のどちらかが要る")
    inputs = {}
    for name, path in (("staple", args.staple_csv), ("physical-monthly", args.physical_monthly_csv)):
        if path:
            prof = gen.PROFILES[name]
            inputs[name] = (gen.read_series(path, prof["prefix"], prof["cadence"]), gen.CADENCE[prof["cadence"]]["text"])
    sa, mod = gen.load_modules(args.repo)
    res = analyse(sa, mod, inputs)
    again = analyse(sa, mod, inputs)
    if json.dumps(res, allow_nan=False) != json.dumps(again, allow_nan=False):
        print("同じ入力で 2 回走らせた結果が違う。書かない", file=sys.stderr)
        return 2
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_window_crossing.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_window_crossing.md").write_text(render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
