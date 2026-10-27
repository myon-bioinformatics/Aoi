#!/usr/bin/env python3
"""波の当てはめの「ほぼ同点」の選ばれ方が、計算の丸めで決まっていないかの確認（探索・事後。確定した出力は変えない）。

きっかけ（結果を見たあとに気づいたこと）:
  - 2024年のソフトバンクは「ε = 1e-3 のときだけ選ばれる式が変わる単位」と記録してあるが、ε の格子（wave_eps_sensitivity）では
    0.03・0.001・1e-12 でだけ乗り換え、0.01・0.003・1e-4・1e-6・1e-9 では乗り換えない。ε の影響が滑らかなら、こうは並ばない
  - 疑似シーズン側の wave_osc_base が、ε を入れると 3〜9 単位で動く。ε の大きさに比例せず、ε が小さくても動く
  - 構造だけ先に見た: ソフトバンク 2024 の順位の線は、全期間で値が一定（wave_rmse = 0.0）。一定の線は、どの式を当てても誤差の2乗和がちょうど 0
  - 合成の一定の線（値 6 を 149 点。実データではない）で、wave_fit の閉じた式の誤差の2乗和は、float64 では候補 55 個の間で幅 5.2e-12
    （約 -2.7e-12〜2.5e-12）ばらつき、許容 EPS_WAVE_TIE = 1e-12 より大きい。longdouble では幅 2.7e-15。値 1 の線では float64 でも幅 2e-13 で許容より小さい

仮説: 当てはめの式の選び方（誤差の2乗和が先の式より EPS_WAVE_TIE を超えて小さいときだけ乗り換える）は、誤差の2乗和が候補の間でほぼ同点のとき、
閉じた式の引き算の丸め（float64 で 1e-12 前後。順位の線は値が 1〜6、点が 100 以上で 2乗和が大きいほど大きい）に負ける。
そのとき選ばれる式は「当てはまりの良さ」ではなく丸めで決まり、基準の格子を ε の波に差し替える（格子の値が 1 ulp 動く）だけで入れ替わる。

予想（走らせる前に書く。結果を見て変えない）:
  (a) ソフトバンク 2024 の実線は、全期間で最大 − 最小 = 0（一定）
  (b) その線で、float64 の誤差の2乗和の候補間の幅（最大 − 最小）は EPS_WAVE_TIE（1e-12）より大きく、longdouble では 1e-12 より小さい。
      longdouble で選ばれる式は、候補の並びで最初の式（減衰 0.5・波なし）で、ε を入れても（格子の 9 個すべてで）変わらない
  (c) float64 では 0.03・0.001・1e-12 で乗り換え（記録済み）、longdouble では格子の 9 個のどれでも乗り換えない
  (d) wave_osc_base が対照（ε なし）と違う単位の数は、ε = 1e-6 と 1e-9 では longdouble で 0。ε = 1e-3 は予想しない
      （ε が大きいと、丸めによらない本当の入れ替わりもありうるため）。float64 の数は、同じ実行で記録して並べる
  (e) 全部の当てはめ呼び出しのうち、float64 と longdouble で選ばれる式が違うものの数を数える（予想は「0 ではない」だけ）。
      そのうち一定の線（最大 − 最小 = 0）の数と割合を並べる（予想は置かない）
  (f) 対照（ε なし）の wave_* 列が、確定済み（float64）と longdouble で違う単位の数を数える（予想は置かない。
      0 でなければ、確定済みの値のうち丸めで決まっているものがある、という材料）
  (c) が外れる ε があれば、その乗り換えは丸めだけでは説明できない。(d) が外れれば、wave_osc_base の動きには丸め以外の原因がある。
  どれも基準ではなく、EPS_WAVE_TIE の直し方は決めない（sakanalytics は変更しない。PR #24 は触らない）。ここで示せるのは、この入力での説明の当否まで

使い方（試合ごとのデータ games.jsonl がある環境で。リポジトリの直下から）:
  uv run --locked python cycles/c001-chunichi/exploratory/wave_tie_noise.py \\
      --games <2013〜2025年の games.jsonl> <2026年の games.jsonl> \\
      --config cycles/c001-chunichi/analysis.toml --committed cycles/c001-chunichi/outputs/season.jsonl \\
      --new-seasons 2026 --outdir out/wave-tie-noise --repo .
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import operator
import sys
import tomllib
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LD = np.longdouble
EPS_OSC = (1e-3, 1e-6, 1e-9)                                              # wave_osc_base を見る ε
SB_SEASON, SB_TEAM = 2024, "h"                                            # ソフトバンク 2024
SB_GRID = (0.1, 0.03, 0.01, 0.003, 1e-3, 1e-4, 1e-6, 1e-9, 1e-12)        # wave_eps_sensitivity と同じ ε の格子


def load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class LdBasis:
    """基準の格子（wave_basis の戻り値）を longdouble にして、y によらない量を一度だけ求める。"""

    def __init__(self, basis: list[dict]):
        self.rows = []
        for b in basis:
            ec, es = np.array(b["ec"], dtype=LD), np.array(b["es"], dtype=LD)
            sec, sec2, sese = ec.sum(), (ec * ec).sum(), (ec * es).sum()
            self.rows.append({"b": b, "ec": ec, "es": es, "sec": sec, "sec2": sec2, "sese": sese,
                              "uu": len(ec) - 2 * sec + sec2, "uv": es.sum() - sese, "vv": (es * es).sum()})


def cands_f64(sa, basis: list[dict], ys: list[float]) -> list[dict]:
    """wave_fit と同じ式・同じ演算順（float64）で、候補ごとの誤差の2乗和などを並べる。"""
    h0 = ys[0]
    sy, sy2 = sum(ys), sum(y * y for y in ys)
    out = []
    for b in basis:
        ech = sum(map(operator.mul, b["ec"], ys))
        ur = sy - h0 * b["sec"] - ech + h0 * b["sec2"]
        rr = sy2 - 2 * h0 * ech + h0 * h0 * b["sec2"]
        if b["per"] is None:
            if b["uu"] <= sa.EPS_WAVE_SOLVE:
                continue
            lim, bb = ur / b["uu"], 0.0
            sse = rr - lim * ur
        else:
            vr = sum(map(operator.mul, b["es"], ys)) - h0 * b["sese"]
            det = b["uu"] * b["vv"] - b["uv"] ** 2
            if det <= sa.EPS_WAVE_SOLVE:
                continue
            lim, bb = (b["vv"] * ur - b["uv"] * vr) / det, (b["uu"] * vr - b["uv"] * ur) / det
            sse = rr - lim * ur - bb * vr
        out.append({"b": b, "sse": sse, "lim": lim, "bb": bb})
    return out


def cands_ld(sa, ld: LdBasis, ys: list[float]) -> list[dict]:
    """同じ式を longdouble で。基準の格子の値（float64）は同じものを使うので、違うのは足し引きの丸めだけ。"""
    y = np.array(ys, dtype=LD)
    h0, sy, sy2 = y[0], y.sum(), (y * y).sum()
    out = []
    for r in ld.rows:
        b = r["b"]
        ech = (r["ec"] * y).sum()
        ur = sy - h0 * r["sec"] - ech + h0 * r["sec2"]
        rr = sy2 - 2 * h0 * ech + h0 * h0 * r["sec2"]
        if b["per"] is None:
            if r["uu"] <= sa.EPS_WAVE_SOLVE:
                continue
            lim, bb = ur / r["uu"], LD(0)
            sse = rr - lim * ur
        else:
            vr = (r["es"] * y).sum() - h0 * r["sese"]
            det = r["uu"] * r["vv"] - r["uv"] ** 2
            if det <= sa.EPS_WAVE_SOLVE:
                continue
            lim, bb = (r["vv"] * ur - r["uv"] * vr) / det, (r["uu"] * vr - r["uv"] * ur) / det
            sse = rr - lim * ur - bb * vr
        out.append({"b": b, "sse": sse, "lim": lim, "bb": bb})
    return out


def select(sa, cands: list[dict]) -> dict:
    """wave_fit と同じ規則: 先の式より誤差の2乗和が EPS_WAVE_TIE を超えて小さいときだけ乗り換える。"""
    best = None
    for c in cands:
        if best is None or c["sse"] < best["sse"] - sa.EPS_WAVE_TIE:
            best = c
    return best


def finish(sa, c: dict, ys: list[float], x0: float, x1: float) -> dict:
    """選んだ式から wave_fit の戻り値を作る（以降は float64）。"""
    b, lim, bb, h0 = c["b"], float(c["lim"]), float(c["bb"]), ys[0]
    amp, t1 = math.hypot(h0 - lim, bb), x1 - x0
    if amp <= sa.WAVE_SETTLE:
        settle = x0
    else:
        settle = x0 + math.log(amp / sa.WAVE_SETTLE) / b["lam"] if b["lam"] > 0 else None
    end = lim + math.exp(-b["lam"] * t1) * ((h0 - lim) * math.cos(b["w"] * t1) + bb * math.sin(b["w"] * t1))
    return {"limit": lim if b["lam"] > 0 else None, "end": end, "decay": b["lam"], "period": b["per"],
            "settle_x": settle, "rmse": math.sqrt(max(float(c["sse"]), 0.0) / len(ys))}


def fit_f64(sa, ys, basis, x0, x1=1.0) -> dict:
    return finish(sa, select(sa, cands_f64(sa, basis, ys)), ys, x0, x1)


def fit_ld(sa, ld: LdBasis, ys, x0, x1=1.0) -> dict:
    return finish(sa, select(sa, cands_ld(sa, ld, ys)), ys, x0, x1)


class Stats:
    """呼び出しごとに、float64（今の関数）と longdouble で選ばれる式を比べて数える。float64 の再実装が今の関数と一致するかも数える。"""

    def __init__(self):
        self.calls = self.flat = self.differ = self.differ_flat = self.reimpl_mismatch = 0

    def add(self, ys, r64, rld, r64b):
        self.calls += 1
        flat = max(ys) == min(ys)
        self.flat += flat
        if (r64["decay"], r64["period"]) != (rld["decay"], rld["period"]):
            self.differ += 1
            self.differ_flat += flat
        if r64b != r64:
            self.reimpl_mismatch += 1

    def summary(self) -> dict:
        return {"calls": self.calls, "flat_lines": self.flat, "decision_differs": self.differ,
                "decision_differs_on_flat_lines": self.differ_flat, "float64_reimplementation_mismatch": self.reimpl_mismatch}


@contextmanager
def patched(sa, mode: str, stats: Stats | None = None):
    """sa.wave_fit を差し替える。mode: "f64"（今の関数のまま）/ "ld"（longdouble で選ぶ）。stats があれば呼び出しごとに比べる。終わったら必ず戻す。"""
    orig, cache = sa.wave_fit, {}

    def ld_of(basis):
        k = id(basis)
        if k not in cache:
            cache[k] = (basis, LdBasis(basis))                              # 基準の格子を生かしておいて id の使い回しを防ぐ
        return cache[k][1]

    def fit(ys, basis, x0, x1=1.0):
        r64 = orig(ys, basis, x0, x1) if (mode == "f64" or stats is not None) else None
        rld = fit_ld(sa, ld_of(basis), ys, x0, x1) if (mode == "ld" or stats is not None) else None
        if stats is not None:
            stats.add(ys, r64, rld, fit_f64(sa, ys, basis, x0, x1))
        return rld if mode == "ld" else r64

    sa.wave_fit = fit
    try:
        yield
    finally:
        sa.wave_fit = orig


def run(sa, wt, tg, basis_fn, mode, sims, min_games, end, stats=None) -> dict:
    with patched(sa, mode, stats):
        return wt.trajectory(sa, tg, basis_fn, sims, min_games, end)


def capture_line(sa, tg_season, team: str, basis_fn, min_games, end) -> dict:
    """sims = 0 でその年だけ season_trajectory を走らせ、球団の実線（順位の高さの線）と、当てはめに使った基準の格子・始まり・終わりを取り出す。"""
    paths_seen, calls = {}, []
    orig_paths, orig_fit, orig_basis = sa._season_paths, sa.wave_fit, sa.wave_basis

    def paths(days, grid, winners):
        r = orig_paths(days, grid, winners)
        paths_seen.setdefault("actual", r)                                 # 最初の呼び出しが実際の勝敗
        return r

    def fit(ys, basis, x0, x1=1.0):
        calls.append((list(ys), basis, x0, x1))
        return orig_fit(ys, basis, x0, x1)

    sa._season_paths, sa.wave_fit, sa.wave_basis = paths, fit, basis_fn
    try:
        sa.season_trajectory(tg_season, sims=0, min_games=min_games, end=end)
    finally:
        sa._season_paths, sa.wave_fit, sa.wave_basis = orig_paths, orig_fit, orig_basis
    ys = list(paths_seen["actual"][team][0])
    hit = next(c for c in calls if c[0] == ys)
    return {"ys": ys, "basis": hit[1], "x0": hit[2], "x1": hit[3]}


def line_table(sa, cap: dict) -> dict:
    """1 本の線について、候補の誤差の2乗和の幅と、選ばれる式（float64 / longdouble）。"""
    ys, basis = cap["ys"], cap["basis"]
    c64, cld = cands_f64(sa, basis, ys), cands_ld(sa, LdBasis(basis), ys)
    s64, sld = [c["sse"] for c in c64], [float(c["sse"]) for c in cld]
    p64, pld = select(sa, c64), select(sa, cld)
    return {"candidates": len(c64),
            "f64": {"choice": [p64["b"]["lam"], p64["b"]["per"]], "sse_spread": max(s64) - min(s64)},
            "ld": {"choice": [pld["b"]["lam"], pld["b"]["per"]], "sse_spread": max(sld) - min(sld),
                   "within_tie_of_best": sum(1 for c in cld if float(c["sse"]) <= float(pld["sse"]) + sa.EPS_WAVE_TIE)}}


def label(key) -> str:
    return f"{key[0]}-{key[1]}"


def changed_units(ref: dict, other: dict, wt, col: str) -> list[str]:
    return [label(k) for k, cols in wt.diff_rows(ref, other).items() if col in cols]


def analyze(sa, wt, tg, sims, min_games, end, eps_osc=EPS_OSC, sb_grid=SB_GRID, sb=(SB_SEASON, SB_TEAM)) -> dict:
    import polars as pl

    stats = Stats()
    ctrl64 = run(sa, wt, tg, sa.wave_basis, "f64", sims, min_games, end, stats)
    ctrl_ld = run(sa, wt, tg, sa.wave_basis, "ld", sims, min_games, end)
    cols = {}
    for k, c in wt.diff_rows(ctrl64, ctrl_ld).items():
        for col in c:
            cols.setdefault(col, []).append(label(k))
    res = {"sims": sims, "units": len(ctrl64), "calls": stats.summary(),
           "control_f64_vs_ld": {"units_differ": len({u for v in cols.values() for u in v}),
                                 "by_column": {c: {"units": len(u), "labels": sorted(u)} for c, u in sorted(cols.items())}}}
    osc = {}
    for eps in eps_osc:
        basis_fn = wt.make_wave_basis(sa, eps)
        r64 = run(sa, wt, tg, basis_fn, "f64", sims, min_games, end)
        rld = run(sa, wt, tg, basis_fn, "ld", sims, min_games, end)
        u64, uld = changed_units(ctrl64, r64, wt, "wave_osc_base"), changed_units(ctrl_ld, rld, wt, "wave_osc_base")
        osc[f"{eps:g}"] = {"f64": {"units": len(u64), "labels": u64}, "ld": {"units": len(uld), "labels": uld}}
    res["osc_base"] = osc
    season, team = sb
    tg_s = tg.filter(pl.col("season") == season)
    rows = []
    for eps in (None, *sb_grid):
        fn = sa.wave_basis if eps is None else wt.make_wave_basis(sa, eps)
        cap = capture_line(sa, tg_s, team, fn, min_games, end)
        rows.append({"eps": eps, **line_table(sa, cap)})
        if eps is None:
            line = {"points": len(cap["ys"]), "min": min(cap["ys"]), "max": max(cap["ys"]), "flat": max(cap["ys"]) == min(cap["ys"]),
                    "first": cap["ys"][0]}
    res["softbank"] = {"unit": label(sb), "line": line, "rows": rows}
    return res


def fmt(v) -> str:
    return f"{v:.3g}" if isinstance(v, float) else str(v)


def render(res: dict) -> str:
    s, c = res["softbank"], res["calls"]
    L = ["# 波の当てはめの「ほぼ同点」と計算の丸め（探索・事後。確定した出力は変えない）", "",
         "予想は [wave_tie_noise.py](../wave_tie_noise.py) の冒頭に、走らせる前に書いたもの。float64 は今の `wave_fit`、longdouble は同じ式を"
         "足し引きだけ longdouble で計算して選んだもの（基準の格子の値は同じ）。", "",
         f"- 単位数: {res['units']}、sims: {res['sims']}",
         f"- 当てはめの呼び出し: {c['calls']}。一定の線（最大 − 最小 = 0）: {c['flat_lines']}。float64 と longdouble で選ばれる式が違う: "
         f"{c['decision_differs']}（そのうち一定の線 {c['decision_differs_on_flat_lines']}）。float64 の再実装が今の関数と合わなかった: "
         f"{c['float64_reimplementation_mismatch']}", ""]
    d = res["control_f64_vs_ld"]
    L += ["## 対照（ε なし）: 確定済み（float64）と longdouble で wave_* が違う単位", "", f"- 違う単位の数: {d['units_differ']}"]
    for col, v in d["by_column"].items():
        L.append(f"- {col}: {v['units']} 単位（{', '.join(v['labels'][:20])}{' …' if len(v['labels']) > 20 else ''}）")
    L += ["", "## wave_osc_base が対照と違う単位（疑似シーズン側）", "", "| ε | float64 | longdouble |", "|---|---|---|"]
    for eps, v in res["osc_base"].items():
        L.append(f"| {eps} | {v['f64']['units']}（{', '.join(v['f64']['labels'])}） | {v['ld']['units']}（{', '.join(v['ld']['labels'])}） |")
    ln = s["line"]
    L += ["", f"## ソフトバンク 2024（{s['unit']}）", "",
          f"実線: {ln['points']} 点、最小 {fmt(ln['min'])}、最大 {fmt(ln['max'])}、始まり {fmt(ln['first'])}、一定: {'はい' if ln['flat'] else 'いいえ'}", "",
          "| ε | 候補の数 | float64 で選ばれた式（減衰, 周期） | float64 の誤差の2乗和の幅 | longdouble で選ばれた式 | longdouble の幅 | 最良から 1e-12 以内の候補（longdouble） |",
          "|---|---|---|---|---|---|---|"]
    for r in s["rows"]:
        L.append(f"| {'なし' if r['eps'] is None else fmt(r['eps'])} | {r['candidates']} | {tuple(r['f64']['choice'])} | {fmt(r['f64']['sse_spread'])} | "
                 f"{tuple(r['ld']['choice'])} | {fmt(r['ld']['sse_spread'])} | {r['ld']['within_tie_of_best']} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", type=Path, nargs="+", required=True)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--committed", type=Path, required=True, help="確定済みの season.jsonl（対照の相手）")
    ap.add_argument("--new-seasons", type=int, nargs="*", default=[])
    ap.add_argument("--unit", nargs=2, metavar=("SEASON", "TEAM"), default=[str(SB_SEASON), SB_TEAM], help="線の表を出す単位（既定はソフトバンク 2024）")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--sims", type=int, help="設定の sims と違う値で走らせる（対照が合わなくなるので、動作確認用）")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(args.repo / "sakanalytics"))
    import sakanalytics as sa

    wt = load_sibling("wave_eps_trial")
    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    traj = cfg.get("trajectory") or {}
    sims = args.sims or int(traj.get("sims", sa.TRAJ_SIMS))
    min_games, end = int(traj.get("min_games", sa.TRAJ_MIN_GAMES)), str(traj.get("end", "season"))
    tg = sa.to_team_games(sa.read_games(args.games), cfg["teams"])
    committed = {}
    for line in args.committed.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        committed[(r["season"], r["team"])] = r
    ctrl = wt.trajectory(sa, tg, sa.wave_basis, sims, min_games, end)
    g = wt.gate(ctrl, committed, sims, args.new_seasons)
    if not g["pass"]:
        print(f"対照が合わない（{g}）。走らせない。", file=sys.stderr)
        return 2
    unit = (int(args.unit[0]), args.unit[1])
    if unit not in ctrl:
        print(f"単位 {label(unit)} がない。走らせない。", file=sys.stderr)
        return 2
    res = analyze(sa, wt, tg, sims, min_games, end, sb=unit)
    res["gate"] = g
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "wave_tie_noise.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "wave_tie_noise.md").write_text(render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
