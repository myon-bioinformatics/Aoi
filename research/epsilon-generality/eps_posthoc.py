"""ε の一般性の、事後の確かめ（eps_generality.py の判定の後に、結果を見てから足した問い。判定は変えない）。

    uv run --locked python research/epsilon-generality/eps_posthoc.py <処理> [その処理の引数]

処理:
  boundary_forms   境の上の単位の式の形（旧 posthoc_boundary_forms.py）
  window_crossing  式が切り替わる ε を窓ごとに二分で探す（旧 posthoc_window_crossing.py）
  eps_ladder       ε の梯子（旧 posthoc_eps_ladder.py）
  scale_tolerance  尺度と許容（旧 posthoc_scale_tolerance.py）
  range_profile    ε の範囲の重みの形（旧 eps_range_profile.py）
説明・予想・引数は各関数の説明（旧ファイルの冒頭）にある。中心の判定は eps_generality.py（このファイルが読み込む）。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path


# ==== boundary_forms（旧 posthoc_boundary_forms.py）

BOUNDARY_FORMS_DOC = """事後の確認（登録した基準の外）: 境界の単位で、ε の大きさによって選ばれる周期が変わるか（探索）。

eps_generality.py を走らせたあと、基準 C2（窓 12 か月・ε=1e-3）を満たさなかった 1 窓の原因を調べるために足した。
結果を見たあとに書いたもので、基準ではない。eps_generality.py の出力は変更しない。

やること:
  1. 境界の単位（今のコードが減衰 0 を選んだ単位）のうち、ε=1e-3 または 1e-6 で選ばれる周期が ε=1e-9 のときと違う単位を数える
  2. その単位について、ε ごとに 2 つの周期の誤差の2乗和を、その周期の式だけで当てはめて比べる（差が EPS_WAVE_TIE = 1e-12 より大きいか）
  3. 周期ごとの境界の単位の数を、窓の長さごとに、野球の 24 単位と並べる
  4. 周期が変わった単位を除いたとき、C2 の相対のずれの最大がどうなるか
  5. 境界でない単位のうち ε=1e-3 / 1e-6 で選ばれる式が変わった単位について、今のコードで選ばれた式・ε の式・減衰しない式の誤差の2乗和を並べる

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/eps_posthoc.py boundary_forms \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir out --repo .
"""

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


def nonboundary_changes(rows: list[dict]) -> dict:
    """境界でない単位のうち、ε=1e-3 / 1e-6 で選ばれる式（減衰・周期）が今のコードと違うものの添字。"""
    out = {}
    for e in gen.EPS[:-1]:
        k = gen.ekey(e)
        out[k] = [i for i, r in enumerate(rows)
                  if not r["boundary"] and (r[k]["decay"], r[k]["period"]) != (r["decay"], r["period"])]
    return out


def sse_of_form(sa, mod, xs: list[float], ys: list[float], eps: float, period, lam=None) -> float:
    """周期 period・減衰 lam の式だけで当てはめたときの誤差の2乗和。格子は減衰 0 を eps に差し替えたもの（eps = 0 なら今のコードの格子）。
    lam を省くと lam = eps（差し替えた波、または eps = 0 の「減衰しない波」）。"""
    lam = eps if lam is None else lam
    basis = mod.make_wave_basis(sa, eps)(xs)
    cand = [b for b in basis if b["per"] == period and b["lam"] == lam]
    if len(cand) != 1:
        raise ValueError(f"格子に周期 {period}・減衰 {lam} の式が {len(cand)} 個ある")
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


def form_table(sa, mod, ys: list[float], unmod: tuple, eps: float, eps_period) -> list[dict]:
    """境界でない単位で式が変わったときの誤差の2乗和。unmod = (減衰, 周期) = 今のコードで選ばれた式。
    今のコードの式・同じ周期（eps_period）の減衰しない波・ε ごとの同じ周期の ε の波を、その式だけで当てはめて並べる。"""
    n = len(ys)
    xs = [i / (n - 1) for i in range(n)]
    rows = [{"label": "今のコードで選ばれた式", "decay": unmod[0], "period": unmod[1],
             "sse": sse_of_form(sa, mod, xs, ys, eps, unmod[1], lam=unmod[0])},
            {"label": "同じ周期の減衰しない波（減衰 0）", "decay": 0.0, "period": eps_period, "sse": sse_of_form(sa, mod, xs, ys, 0.0, eps_period)}]
    for e in gen.EPS:
        rows.append({"label": f"同じ周期の ε の波（ε={e:g}）", "decay": e, "period": eps_period, "sse": sse_of_form(sa, mod, xs, ys, e, eps_period)})
    return rows


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


def boundary_forms_analyse(sa, mod, series: dict, repo: Path) -> dict:
    res = gen.compute(sa, mod, series)
    out = {"by_n": {}, "baseball": baseball_periods(repo), "units": [], "nonboundary_units": []}
    for n in gen.LENGTHS:
        rows = res["rows"]["real"][str(n)]
        wins = [w for w in gen.tile(series, n) if gen.normalize(w["values"]) is not None]        # real_rows と同じ順・同じ除外
        if len(wins) != len(rows):
            raise ValueError(f"窓の数が合わない: {len(wins)} ≠ {len(rows)}")
        ch = changed_period(rows)
        nb = nonboundary_changes(rows)
        skip = set().union(*map(set, ch.values()))
        bd = [r for r in rows if r["boundary"]]
        out["by_n"][str(n)] = {
            "boundary": len(bd), "periods": dict(sorted(Counter(r["period"] for r in bd).items())),
            "changed_period": {k: len(v) for k, v in ch.items()}, "c2_without_changed": corrected_c2(rows, skip),
            "nonboundary_changed": {k: len(v) for k, v in nb.items()}}
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
        for k, idx in nb.items():
            for i in idx:
                r = rows[i]
                w = wins[i]
                if (w["si"], w["start"]) != (r["series_index"], r["start"]):
                    raise ValueError(f"窓と行が対応しない: {i}")
                ys = gen.normalize(w["values"])[1]
                out["nonboundary_units"].append({
                    "n": n, "eps": float(k[1:]), "source": r["source"], "country": r["country"], "variable": r["variable"],
                    "unit": r["unit"], "series_index": r["series_index"], "start": r["start"],
                    "unmodified": [r["decay"], r["period"]], "epsilon_form": [r[k]["decay"], r[k]["period"]],
                    "table": form_table(sa, mod, ys, (r["decay"], r["period"]), float(k[1:]), r[k]["period"])})
    return out


def boundary_forms_render(res: dict) -> str:
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
    L += ["## 境界でない単位で、選ばれる式が変わった単位", ""]
    cnt = "、".join(f"{n} か月: {d['nonboundary_changed'][gen.ekey(1e-3)]} / {d['nonboundary_changed'][gen.ekey(1e-6)]}"
                    for n, d in res["by_n"].items())
    L += [f"ε=1e-3 / 1e-6 のとき今のコードと違う式が選ばれた境界でない単位の数: {cnt}", ""]
    if not res["nonboundary_units"]:
        L.append("なし。")
    for u in res["nonboundary_units"]:
        L += [f"### {u['n']} か月・ε={u['eps']:g}: {u['source']} {u['country']} {u['variable']}（{u['unit']}、系列 {u['series_index']}）{u['start']} から", "",
              f"今のコードの式は 減衰 {u['unmodified'][0]:g}・周期 {u['unmodified'][1] if u['unmodified'][1] is None else format(u['unmodified'][1], 'g')}、"
              f"ε の格子では 減衰 {u['epsilon_form'][0]:g}・周期 {u['epsilon_form'][1] if u['epsilon_form'][1] is None else format(u['epsilon_form'][1], 'g')}。"
              "それぞれの式だけで当てはめた誤差の2乗和（小さいほどよく合う）:", "",
              "| 式 | 減衰 | 周期 | 誤差の2乗和 |", "|---|---|---|---|"]
        for x in u["table"]:
            per = "なし" if x["period"] is None else f"{x['period']:g}"
            L.append(f"| {x['label']} | {x['decay']:g} | {per} | {x['sse']:.9g} |")
        L.append("")
    return "\n".join(L) + "\n"


def boundary_forms(argv=None) -> int:
    ap = argparse.ArgumentParser(description=BOUNDARY_FORMS_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    sa, mod = gen.load_modules(args.repo)
    res = boundary_forms_analyse(sa, mod, gen.read_series(args.csv), args.repo)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_boundary_forms.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_boundary_forms.md").write_text(boundary_forms_render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== window_crossing（旧 posthoc_window_crossing.py）

WINDOW_CROSSING_DOC = """ε を上げたとき、すでに分かっている 3 つの窓で選ばれる式が変わる ε を、1 窓ずつ細かく探す（事後。登録した基準の外）。

背景: 事後の梯子（eps_posthoc.py eps_ladder）で、ε を 1e-4〜1/100 に動かしたとき選ばれる式が変わった単位は 3 つだけだった。
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
  uv run --locked python research/epsilon-generality/eps_posthoc.py window_crossing \\
      --staple-csv research/staple-price-survey/staple_survey_vertical.csv [--physical-monthly-csv physical_monthly_vertical.csv] \\
      --outdir out/crossing --repo .
"""

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
    return sse_of_form(sa, mod, [i / (n - 1) for i in range(n)], ys, eps, form[1], lam=lam)


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


def window_crossing_analyse(sa, mod, inputs: dict, specs=WINDOWS) -> dict:
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


def window_crossing_render(res: dict) -> str:
    L = ["# 式が変わる ε を窓ごとに細かく探す（事後。登録した基準の外）", "",
         "予想は [eps_posthoc.py の window_crossing](../../eps_posthoc.py) の冒頭に、走らせる前に書いたもの。"
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


def window_crossing(argv=None) -> int:
    ap = argparse.ArgumentParser(description=WINDOW_CROSSING_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
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
    res = window_crossing_analyse(sa, mod, inputs)
    again = window_crossing_analyse(sa, mod, inputs)
    if json.dumps(res, allow_nan=False) != json.dumps(again, allow_nan=False):
        print("同じ入力で 2 回走らせた結果が違う。書かない", file=sys.stderr)
        return 2
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_window_crossing.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_window_crossing.md").write_text(window_crossing_render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== eps_ladder（旧 posthoc_eps_ladder.py）

EPS_LADDER_DOC = """ε を 1e-4〜1/100 の梯子で動かし、C2 の基準を超える単位と、ε の波が消える単位を数える（事後。登録した基準の外）。

第 3 回で乱数の ε が 2 つ（1.76×10^-3、2.22×10^-3）、主食価格の 12 か月の窓の C2 を満たさなかった。外れたのが決め打ちの ε=1e-3 と同じ
1 単位かどうか、ε を動かすとどこで動くか、1/100 までのほかの単位ではどうかを見るための表で、判定ではない。
「超える」の基準は、登録した値と README の延長（eps_generality.threshold）。梯子は種に依らない固定の並び。

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/eps_posthoc.py eps_ladder \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir out/ladder/staple --repo .
  （物理量は --profile physical-monthly / physical-daily）
"""
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


def eps_ladder_analyse(gen, sa, mod, series, cadence):
    eps = tuple(sorted(set(gen.EPS) | set(LADDER)))
    wins = {n: gen.tile(series, n, gen.CADENCE[cadence]["text"]) for n in gen.LENGTHS}
    bases = {n: gen.make_bases(sa, mod, [i / (n - 1) for i in range(n)], eps) for n in gen.LENGTHS}
    real = gen.real_rows(sa, bases, wins)
    return {"ladder": list(LADDER), "sets": {str(n): count_rows(gen, real[n]["rows"]) | {"units": len(real[n]["rows"])} for n in gen.LENGTHS}}


def eps_ladder_render(gen, res) -> str:
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


def eps_ladder(argv=None) -> int:
    ap = argparse.ArgumentParser(description=EPS_LADDER_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--profile", default="staple")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    gen = load_gen()
    sa, mod = gen.load_modules(args.repo)
    p = gen.PROFILES[args.profile]
    res = eps_ladder_analyse(gen, sa, mod, gen.read_series(args.csv, p["prefix"], p["cadence"]), p["cadence"])
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_eps_ladder.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_eps_ladder.md").write_text(eps_ladder_render(gen, res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== scale_tolerance（旧 posthoc_scale_tolerance.py）

SCALE_TOLERANCE_DOC = """物理量の回で、値の単位を 1e-6 倍にしたときだけ選ばれる式が大きく動いた理由の確認（事後。登録した基準の外）。

仮説: sakanalytics の絶対値の許容 EPS_WAVE_TIE（誤差の2乗和の差がこれ以下なら、先に並べた式のままにする）が、
値を c 倍すると c² 倍になる誤差の2乗和の尺度に対して大きくなりすぎ、ほぼ同点でない式まで「同点」にしてしまう。
EPS_WAVE_SOLVE は基準の格子だけで決まり y によらないので、仮説の外。

予想（走らせる前に書く）:
  (a) 許容をそのままにして倍率を細かく動かすと、式が動き始める倍率が見つかる（README の 1e-3 以上では動かず、1e-6 では動いた）
  (b) 許容に倍率の2乗をかけると、どの倍率でも式は変わらない（係数は浮動小数点の誤差の範囲）
(b) で変わるなら、この仮説は足りない。(b) で変わらなくても、それは「この許容が原因の全部」を示すだけで、直し方は決めない。

追記（2026-10-27。主食価格の月次に広げる。**走らせる前に書く**。すでに見た部分とまだ見ていない部分を分ける）:
  すでに見たもの: 第 3 回の乱数の倍率（results-random/staple）。主食価格の N = 24 の窓（単位 2192）で、許容をそのままにしたとき、
    式が変わった単位は 倍率 3.83e-22 で 2104、1e-06 で 1056（境界の単位 381、係数の相対のずれの最大 1.27）、8.52e-4・1e-3・0.329・1・1.86・6.33・9.97 では 0。
    物理量の月次・日次と同じ向き（小さい倍率だけ動く）に見えている。
  まだ見ていないもの: 倍率 1e-8〜1e-2 の細かい格子（1e-5・1e-4 など）、許容に倍率の2乗をかけた場合。
  予想:
    (a') 許容をそのままにしたとき、倍率を 1e-8 → 1 と並べて「式が変わった単位」は増えない（単調に非増加）。1e-3 以上では 0。
         1e-06 は第 3 回と同じ値（式が変わった 1056、境界の単位 381）になる（同じ入力・同じ手順なので、再現の確認）
    (b') 許容に倍率の2乗をかけると、どの倍率でも式は変わらない（境界かどうかも変わらない。係数は浮動小数点の誤差の範囲）
  (b') で変わる倍率があれば、この仮説は主食価格では足りない。(a') の並びが単調でなければ、その理由は仮説の外にある。
  どちらも基準ではない。(b') が通っても言えるのは「この許容が、この入力で動きの原因の全部だった」までで、直し方は決めない。

使い方（リポジトリの直下から。3 つのうち 1 つ以上を指定する）:
  uv run --locked python research/epsilon-generality/eps_posthoc.py scale_tolerance \\
      --monthly-csv out/physical/physical_monthly_vertical.csv --daily-csv out/physical/physical_daily_vertical.csv \\
      --staple-csv research/staple-price-survey/staple_survey_vertical.csv \\
      --outdir out/posthoc --repo .
"""
KINDS = (("monthly", "月次", "physical-monthly"), ("daily", "日次", "physical-daily"), ("staple", "主食価格の月次", "staple"))
FINE = (1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1.0)        # 値の幅 5 にそろえたあとの y と τ にかける倍率。1 が基準


@contextmanager
def patched(gen, sa, scales, scale_tie: bool):
    """gen.SCALES を差し替え、scale_tie なら fit_row の間だけ EPS_WAVE_TIE を（倍率の2乗）倍にする。終わったら必ず元に戻す。"""
    old_scales, old_fit, old_tie = gen.SCALES, gen.fit_row, sa.EPS_WAVE_TIE      # 許容は wrapped が当てはめのたびに戻す

    def wrapped(sa_, bases, ys, tau):
        f = tau / gen.PRIMARY_TAU
        sa_.EPS_WAVE_TIE = old_tie * f * f if scale_tie else old_tie
        try:
            return old_fit(sa_, bases, ys, tau)
        finally:
            sa_.EPS_WAVE_TIE = old_tie
    gen.SCALES, gen.fit_row = scales, wrapped
    try:
        yield
    finally:
        gen.SCALES, gen.fit_row = old_scales, old_fit


def scale_tolerance_analyse(gen, sa, mod, series: dict, cadence: str, scales=FINE) -> dict:
    n = gen.PRIMARY
    windows = gen.tile(series, n, gen.CADENCE[cadence]["text"])
    bases = gen.make_bases(sa, mod, [i / (n - 1) for i in range(n)])
    out = {"windows": len(windows), "n": n}
    for name, scale_tie in (("tolerance_unchanged", False), ("tolerance_scaled", True)):
        with patched(gen, sa, scales, scale_tie):
            out[name] = gen.scale_summary(sa, bases, windows)
    return out


def fmt(v) -> str:
    return "—" if v is None else (f"{v:.3g}" if isinstance(v, float) else str(v))


def scale_tolerance_render(res: dict) -> str:
    L = ["# 値の単位を変えたときの許容の確認（事後。登録した基準の外）", "",
         "予想は [eps_posthoc.py の scale_tolerance](../eps_posthoc.py) の冒頭に、走らせる前に書いたもの。"
         "倍率 1 が基準。「式が変わった」は選ばれる（減衰, 周期）が倍率 1 と違う単位の数。", ""]
    for kind, label, _ in KINDS:
        if kind not in res:
            continue
        d = res[kind]
        L += [f"## {label}（{d['n']} 点の窓 {d['windows']} 個）", ""]
        for name, title in (("tolerance_unchanged", "許容 EPS_WAVE_TIE をそのまま（1e-12）"),
                            ("tolerance_scaled", "許容に倍率の2乗をかけた")):
            L += [f"### {title}", "", "| 倍率 | 単位 | 境界 | 式が変わった | 境界かどうかが変わった | 係数のずれの最大（相対）| 比べた単位 |", "|---|---|---|---|---|---|---|"]
            for f, s in d[name].items():
                L.append(f"| {f} | {s['units']} | {s['boundary']} | {s['forms_changed']} | {s['boundary_flag_changed']} | "
                         f"{fmt(s['coefficient_max_dev'])} | {s['coefficient_n']} |")
            L.append("")
    return "\n".join(L)


def scale_tolerance(argv=None) -> int:
    ap = argparse.ArgumentParser(description=SCALE_TOLERANCE_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--monthly-csv", type=Path, default=None)
    ap.add_argument("--daily-csv", type=Path, default=None)
    ap.add_argument("--staple-csv", type=Path, default=None, help="主食価格の縦持ちの CSV（research/staple-price-survey/staple_survey_vertical.csv）")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    paths = {"monthly": args.monthly_csv, "daily": args.daily_csv, "staple": args.staple_csv}
    if not any(paths.values()):
        ap.error("--monthly-csv / --daily-csv / --staple-csv のうち 1 つ以上を指定する")
    gen = load_gen()
    sa, mod = gen.load_modules(args.repo)
    res = {}
    for kind, _, profile in KINDS:
        if paths[kind] is None:
            continue
        p = gen.PROFILES[profile]
        res[kind] = scale_tolerance_analyse(gen, sa, mod, gen.read_series(paths[kind], p["prefix"], p["cadence"]), p["cadence"])
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_scale_tolerance.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_scale_tolerance.md").write_text(scale_tolerance_render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== range_profile（旧 eps_range_profile.py）

RANGE_PROFILE_DOC = """そのデータで、ε を動かしたとき結果がどこまで動かないかを記録する（事後。登録した基準の外）。

ε の範囲を定数として決めるためのものではない。「このデータでは、ε がこの範囲なら、これだけの単位が動かなかった」という観測を、
データごとに残して並べるためのもの。別のデータには別の数字が出る（出てよい）。

数えるもの（窓の長さ 12 / 24 / 48 ごと。合計も出す）:
  境界の単位（減衰 0 で当てはまる単位）: ε の波が残り、係数（落ち着く位置 × ε）が基準の ε=1e-9 と相対 δ 以内（δ = 10%, 1%, 0.1%, 0.01%）。
    両方とも始まりで落ち着く単位は、C2 と同じく比べず、収まったに数える（ε に依らない）
  境界でない単位: 選ばれる式が ε を入れる前と同じ
  乱数の選び方（eps_generality.draw_coefficients）の重みのうち、ε がその値以下になる割合

範囲を指定する（--eps-range MODE LO HI。eps_generality.py と同じ書き方）: LO・HI（2.22e-3 でも 2.22×10^-3 でも書ける）を格子に足し、
MODE（inside = LO 以上 HI 以下、above = HI より大きい、below = LO より小さい）の側にある格子の ε について、δ ごとの最悪の収まった割合などをまとめる。
--random-eps K を付けると、その側から ε を乱数で K 個選んで格子に足す（--coef-seed で種）。付けなければ出力は今までと同じ。

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/eps_posthoc.py range_profile \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir out/range/staple --repo .
  別のデータは --csv に縦持ちの CSV、--prefix に変数名の頭、--cadence に month か day（--profile の代わり）。
"""
GRID = (1e-2, 5e-3, 3e-3, 2e-3, 1e-3, 7e-4, 5e-4, 3e-4, 2e-4, 1e-4, 1e-5, 1e-6, 1e-7, 1e-9, 1e-11, 1e-13)       # すべて 0 < ε ≤ 1/100
DELTAS = (0.1, 0.01, 0.001, 0.0001)


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


def side_of(region, e):
    """ε が範囲 [lo, hi] のどちらの側か。"""
    return "inside" if region["lo"] <= e <= region["hi"] else "above" if e > region["hi"] else "below"


def region_summary(gen, total, region):
    """指定した範囲の region["mode"] の側にある格子の ε について、δ ごとの最悪の収まった割合（その側の格子のうち一番低いもの）、すべて収まったか、
    式が変わった境界でない単位と波が残らない単位の最大、乱数の選び方でその側に入る確率。"""
    B, NB = total["boundary"], total["nonboundary"]
    pts = [v for v in total["per_eps"].values() if side_of(region, v["eps"]) == region["mode"]]
    ds = sorted({d for v in total["per_eps"].values() for d in v["ok"]}, key=float, reverse=True)
    return {"eps": sorted((v["eps"] for v in pts), reverse=True),
            "worst_ok_share": {d: (min(v["ok"][d] for v in pts) / B if pts and B else None) for d in ds},
            "all_within": {d: bool(pts and B and all(v["ok"][d] == B for v in pts)) for d in ds},
            "max_nonboundary_changed": max((NB - v["nonboundary_same"] for v in pts), default=None),
            "max_lost": max((v["lost"] for v in pts), default=None),
            "draw_probability": sum(m * len(a) for _, m, a in gen.region_table("eps", region)) / (gen.A_MAX - gen.A_MIN + 1)}


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


def range_profile_analyse(gen, sa, mod, series, cadence, grid=GRID, region=None):
    eps = tuple(sorted(set(gen.EPS) | set(grid)))
    wins = {n: gen.tile(series, n, gen.CADENCE[cadence]["text"]) for n in gen.LENGTHS}
    bases = {n: gen.make_bases(sa, mod, [i / (n - 1) for i in range(n)], eps) for n in gen.LENGTHS}
    real = gen.real_rows(sa, bases, wins)
    sets = {str(n): coverage_rows(gen, real[n]["rows"], grid) for n in gen.LENGTHS}
    total = pool(list(sets.values()))
    res = {"grid": list(grid), "deltas": list(DELTAS), "sets": sets, "total": total,
           "full_coverage_max_eps": {format(d, "g"): largest_full(total, d) for d in DELTAS},
           "draw_share_le": {format(e, "g"): share_le(gen, e) for e in grid}}
    if region:
        res["region"] = region
        res["region_summary"] = region_summary(gen, total, region)
    return res


def range_profile_render(gen, res) -> str:
    t, B, NB = res["total"], res["total"]["boundary"], res["total"]["nonboundary"]
    ds = [format(d, "g") for d in res["deltas"]]
    rg = res.get("region")
    L = ["# このデータで、ε がどこまで動かなかったか（事後。登録した基準の外）", "",
         "**このデータでの観測で、ε の範囲を決める値ではありません。** 別のデータには別の数字が出ます。",
         f"窓の長さ 12 / 24 / 48 の合計で、境界の単位 {B}、境界でない単位 {NB}。", "",
         "## ε ごとに収まった割合", "",
         "境界の単位が、基準の ε=1e-9 の係数と相対 δ 以内に収まった割合（δ ごと）。`消`は ε の波が残らなかった単位の数。右端は、境界でない単位で選ばれる式が変わらなかった割合。", "",
         "| ε | " + ("範囲 | " if rg else "") + " | ".join(f"δ={float(d) * 100:g}%" for d in ds) + " | 消 | 式が変わらない（境界でない） |", "|---|" + "---|" * (len(ds) + 2 + bool(rg))]
    for k, v in sorted(t["per_eps"].items(), key=lambda kv: -kv[1]["eps"]):
        L.append(f"| {v['eps']:g} | " + (f"{side_of(rg, v['eps'])} | " if rg else "") + " | ".join(f"{v['ok'][d] / B * 100:.2f}%" if B else "—" for d in ds) + f" | {v['lost']} | "
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
    if rg:
        sm = res["region_summary"]
        L += ["", f"## 指定した範囲: {rg['mode']}（{gen.pow10_text(rg['lo'])} 〜 {gen.pow10_text(rg['hi'])}。inside は両端を含み、above は HI より大きく、below は LO より小さい）", "",
              f"この側にある格子の ε {len(sm['eps'])} 個: " + (", ".join(f"{e:g}" for e in sm["eps"]) or "なし") + "。", ""]
        if sm["eps"] and B:
            L += ["| δ | 最悪の収まった割合 | すべて収まった |", "|---|---|---|"]
            L += [f"| {float(d) * 100:g}% | {sm['worst_ok_share'][d] * 100:.2f}% | {'はい' if sm['all_within'][d] else 'いいえ'} |" for d in ds]
            L += ["", f"境界でない単位で式が変わった単位の最大: {sm['max_nonboundary_changed']} / {NB}。ε の波が残らない単位の最大: {sm['max_lost']}。"]
        else:
            L.append("この側に格子の ε がない、または境界の単位がないので、まとめられません。")
        L += ["", f"乱数の選び方（`draw_coefficients`）で、ε がこの側に入る確率: {sm['draw_probability'] * 100:.1f}%。"]
    return "\n".join(L) + "\n"


def range_profile(argv=None) -> int:
    ap = argparse.ArgumentParser(description=RANGE_PROFILE_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--profile", default="staple", help="eps_generality.PROFILES の名前。別のデータは --prefix / --cadence で上書き")
    ap.add_argument("--prefix", default=None, help="変数名の頭（省略は profile の値）")
    ap.add_argument("--cadence", default=None, choices=["month", "day"], help="刻み（省略は profile の値）")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--eps-range", nargs=3, metavar=("MODE", "LO", "HI"),
                    help="範囲 [LO, HI] と、見る側。MODE は inside（LO 以上 HI 以下）/ above（HI より大きい）/ below（LO より小さい）。LO・HI は 2.22e-3 でも 2.22×10^-3 でも書ける。省略は範囲なし")
    ap.add_argument("--random-eps", type=int, default=0, metavar="K", help="--eps-range の側から ε を乱数で K 個選んで格子に足す")
    ap.add_argument("--coef-seed", type=int, default=None, help="--random-eps の種（省略は eps_generality.SEED）")
    args = ap.parse_args(argv)
    if args.random_eps and not args.eps_range:
        ap.error("--random-eps は --eps-range MODE LO HI と一緒に使う")
    gen = load_gen()
    region, grid = None, GRID
    if args.eps_range:
        try:
            region = gen.make_region("eps", args.eps_range[0], gen.parse_pow10(args.eps_range[1]), gen.parse_pow10(args.eps_range[2]))
            drawn = [d["value"] for d in gen.draw_coefficients(args.random_eps, gen.SEED if args.coef_seed is None else args.coef_seed, "eps", region)]
        except ValueError as e:
            ap.error(str(e))
        grid = tuple(sorted(set(GRID) | {region["lo"], region["hi"]} | set(drawn), reverse=True))
    sa, mod = gen.load_modules(args.repo)
    p = gen.PROFILES[args.profile]
    prefix, cadence = args.prefix or p["prefix"], args.cadence or p["cadence"]
    series = gen.read_series(args.csv, prefix, cadence)
    if not series:
        raise SystemExit(f"変数名が {prefix!r} で始まる行が {args.csv} にない")
    res = range_profile_analyse(gen, sa, mod, series, cadence, grid, region)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "eps_range_profile.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "eps_range_profile.md").write_text(range_profile_render(gen, res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== 入口
COMMANDS = {
    "boundary_forms": boundary_forms,
    "window_crossing": window_crossing,
    "eps_ladder": eps_ladder,
    "scale_tolerance": scale_tolerance,
    "range_profile": range_profile,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="eps_posthoc.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"eps_posthoc.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
