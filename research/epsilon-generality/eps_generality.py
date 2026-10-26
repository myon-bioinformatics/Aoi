#!/usr/bin/env python3
"""ε（波の減衰 0 の置き換え）が、野球以外の連続データでも使えるかの確認（探索）。

README.md に事前に書いた基準（C1〜C5）を、(1) リポジトリにある主食価格の月次の系列、(2) 答えが分かっている合成の系列、
に当てる。sakanalytics の wave_basis / wave_fit と、cycles/c001-chunichi/exploratory/wave_eps_trial.py の make_wave_basis
（減衰 0 の格子を ε に差し替える）をそのまま使う。野球の列（順位・試合・季節）には触れない。ε の値は暫定の置き場所で、結論には使わない。

使い方（リポジトリの直下から。polars が入った環境で）:
  uv run --locked python research/epsilon-generality/eps_generality.py \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir /tmp/eps-generality --repo .
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import re
import sys
from contextlib import contextmanager
from pathlib import Path

# ---- 事前に決めた設定（README.md の「事前登録」と同じ。結果を見て変えない） --------------------------------------------
SPEC_VERSION = 1
SEED = 20261026
LENGTHS = (12, 24, 48)      # 窓の長さ（月）。互いに重ならない窓で並べる
PRIMARY = 24
TAUS = (0.25, 0.5, 1.0)     # 「決まった」とみなす幅（値の幅を 5 にそろえたあとの単位。0.5 は野球の半順位と同じ大きさ）
PRIMARY_TAU = 0.5
EPS = (1e-3, 1e-6, 1e-9)    # ε = 1 × 10^-n
SCALE = 5.0                 # 窓の値の幅（最大 − 最小）をこの値にそろえる（野球の順位 1〜6 の幅）
MIN_UNITS = 20              # これより少ない集合では、その基準は判定不能
N_SYNTH = 200               # 合成の系列の数（種類ごと）
SYNTH_POINTS = 24
SYNTH_NOISE = 0.02
CRIT = {"c1_eps3": 0.98,    # C1: 境界の単位のうち ε の波が残る割合（ε=1e-3 だけ。1e-6, 1e-9 は全部）
        "c2_eps3": 0.02, "c2_eps6": 1e-4,         # C2: 係数の相対のずれ（基準は ε=1e-9）
        "c3_eps3": 0.02, "c3_eps6": 0.005, "c3_eps9": 0.005,   # C3: 境界でない単位のうち選ばれる式が変わる割合
        "c5_boundary": 0.9, "c5_amp": 0.05}       # C5: 減衰しない合成の系列が境界になる割合 / 振幅の相対のずれ
# 野球（cycles/c001-chunichi/exploratory/wave_eps_2026_results/）での値。比べるための参考で、基準ではない
BASEBALL = {"units": 168, "boundary": 24, "coefficient_range": [0.0774, 1.7637], "c3_eps3": "1 単位（2024年ソフトバンク）"}

SOURCES = (("FPMA", "tezamo/FPMA"), ("WFP-yearly", "global-wfp-food-prices"), ("WFP", "wfp-food-prices"),
           ("BLS", "bls.gov"), ("e-Stat", "e-stat.go.jp"))
SYNTH = (
    {"id": "undamped_p1", "kind": "undamped", "period": 1.0, "decay": 0.0},
    {"id": "undamped_p0.5", "kind": "undamped", "period": 0.5, "decay": 0.0},
    {"id": "undamped_p0.25", "kind": "undamped", "period": 0.25, "decay": 0.0},
    {"id": "damped_l1", "kind": "damped", "period": 0.5, "decay": 1.0},
    {"id": "damped_l3", "kind": "damped", "period": 0.5, "decay": 3.0},
    {"id": "damped_l8", "kind": "damped", "period": 0.5, "decay": 8.0},
    {"id": "linear", "kind": "linear"},
    {"id": "noise", "kind": "noise"},
)


def ekey(e: float) -> str:
    return f"e{e:g}"


def load_modules(repo: Path):
    """sakanalytics と wave_eps_trial（make_wave_basis のため）を読む。"""
    sys.path.insert(0, str(repo / "sakanalytics"))
    import sakanalytics as sa
    path = repo / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps_trial.py"
    spec = importlib.util.spec_from_file_location("wave_eps_trial", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wave_eps_trial"] = mod
    spec.loader.exec_module(mod)
    return sa, mod


# ---- 窓を作る ---------------------------------------------------------------------------------------------------------
def month_index(d: str) -> int:
    m = re.fullmatch(r"(\d{4})-(\d{2})-\d{2}", d)
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise ValueError(f"日付が YYYY-MM-DD でない: {d!r}")
    return int(m.group(1)) * 12 + int(m.group(2)) - 1


def month_text(i: int) -> str:
    return f"{i // 12:04d}-{i % 12 + 1:02d}"


def read_series(path: Path) -> dict:
    """staple_price:* の行から {(国, 変数, 単位, 出どころ, 注): {月番号: 値}}。月は日にちを無視して数え、同じ月が 2 つあれば止まる。"""
    out: dict = {}
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if not r["variable"].startswith("staple_price:"):
                continue
            v = float(r["value"])
            if not math.isfinite(v):
                raise ValueError(f"値が有限でない: {r}")
            s = out.setdefault((r["country"], r["variable"], r["unit"], r["source"], r["note"]), {})
            mi = month_index(r["date"])
            if mi in s:
                raise ValueError(f"同じ月が 2 つある: {(r['country'], r['variable'], r['date'])}")
            s[mi] = v
    return out


def tile(series: dict, n: int) -> list[dict]:
    """月が途切れずに続く区間ごとに、先頭から n か月ずつ、互いに重ならない窓を並べる（余りは使わない）。"""
    out = []
    for key in sorted(series):
        pts = sorted(series[key].items())
        runs, run = [], []
        for mi, v in pts:
            if run and mi != run[-1][0] + 1:
                runs.append(run)
                run = []
            run.append((mi, v))
        if run:
            runs.append(run)
        for r in runs:
            for k in range(len(r) // n):
                w = r[k * n:(k + 1) * n]
                out.append({"key": key, "start": month_text(w[0][0]), "values": [v for _, v in w]})
    return out


def normalize(values: list[float]):
    """x を [0, 1] に、y を「始まりが 0、幅が SCALE」にそろえる。幅が 0 の窓は None。返り値: (xs, ys, 倍率)。"""
    lo, hi = min(values), max(values)
    if not hi > lo:
        return None
    n, s, v0 = len(values), SCALE / (hi - lo), values[0]
    return [i / (n - 1) for i in range(n)], [(v - v0) * s for v in values], s


def source_group(url: str) -> str:
    for name, frag in SOURCES:
        if frag in url:
            return name
    return "other"


# ---- 当てはめ ---------------------------------------------------------------------------------------------------------
@contextmanager
def settle_tolerance(sa, tau: float):
    old = sa.WAVE_SETTLE
    sa.WAVE_SETTLE = tau
    try:
        yield
    finally:
        sa.WAVE_SETTLE = old


def make_bases(sa, mod, xs: list[float]) -> dict:
    """{None: 今のコードの格子, ε: 減衰 0 を ε に差し替えた格子}。x が同じ窓では格子も同じなので、長さごとに 1 回作る。"""
    return {None: sa.wave_basis(xs)} | {e: mod.make_wave_basis(sa, e)(xs) for e in EPS}


def fit_row(sa, bases: dict, ys: list[float], tau: float) -> dict:
    with settle_tolerance(sa, tau):
        res = {k: sa.wave_fit(ys, b, 0.0, 1.0) for k, b in bases.items()}
    u = res[None]
    row = {"decay": u["decay"], "period": u["period"], "rmse": u["rmse"], "limit": u["limit"], "settle_x": u["settle_x"],
           "boundary": u["decay"] == 0.0}
    for e in EPS:
        f = res[e]
        at_start = f["settle_x"] == 0.0
        coef = None if f["settle_x"] is None or at_start else f["settle_x"] * e      # ε = 1×10^-n のとき 位置 = 係数 × 10^n
        row[ekey(e)] = {"decay": f["decay"], "period": f["period"], "rmse": f["rmse"], "limit": f["limit"],
                        "settle_x": f["settle_x"], "coefficient": coef, "at_start": at_start}
    return row


def real_rows(sa, bases_by_n: dict, windows_by_n: dict) -> dict:
    out = {}
    for n, wins in windows_by_n.items():
        rows, skipped = [], 0
        for w in wins:
            nm = normalize(w["values"])
            if nm is None:
                skipped += 1
                continue
            _, ys, _ = nm
            rows.append({"source": source_group(w["key"][3]), "country": w["key"][0], "variable": w["key"][1],
                         "start": w["start"]} | fit_row(sa, bases_by_n[n], ys, PRIMARY_TAU))
        out[n] = {"rows": rows, "constant_windows": skipped, "windows": len(wins)}
    return out


def tau_summary(sa, bases: dict, windows: list[dict]) -> dict:
    """τ を変えたときの変化。式の選び方は τ によらない（誤差の2乗和だけで決まる）はずなので、それも確かめる。"""
    per_tau, ref_forms = {}, None
    for tau in TAUS:
        forms, at_start, coefs, boundary = [], 0, [], 0
        for w in windows:
            nm = normalize(w["values"])
            if nm is None:
                continue
            r = fit_row(sa, bases, nm[1], tau)
            forms.append((r["decay"], r["period"], r[ekey(EPS[-1])]["decay"], r[ekey(EPS[-1])]["period"]))
            if r["boundary"]:
                boundary += 1
                c = r[ekey(1e-6)]
                at_start += c["at_start"]
                if c["coefficient"] is not None:
                    coefs.append(c["coefficient"])
        if ref_forms is None:
            ref_forms = forms
        coefs.sort()
        per_tau[f"{tau:g}"] = {"boundary": boundary, "at_start": at_start,
                               "coefficient_min": coefs[0] if coefs else None, "coefficient_max": coefs[-1] if coefs else None,
                               "forms_same_as_first_tau": forms == ref_forms}
    return per_tau


# ---- 合成の系列（答えが分かっている）----------------------------------------------------------------------------------
def synth_series(spec: dict, i: int, n: int = SYNTH_POINTS, noise: float = SYNTH_NOISE) -> list[float]:
    rng = random.Random(f"{SEED}/{spec['id']}/{i}")
    xs = [k / (n - 1) for k in range(n)]
    kind = spec["kind"]
    if kind in ("undamped", "damped"):
        phi = rng.uniform(0.0, 2 * math.pi)
        return [3.0 + 2.0 * math.exp(-spec["decay"] * x) * math.cos(2 * math.pi * x / spec["period"] + phi) + rng.gauss(0.0, noise)
                for x in xs]
    if kind == "linear":
        return [3.0 + 2.0 * x + rng.gauss(0.0, noise) for x in xs]
    if kind == "noise":
        return [3.0 + rng.gauss(0.0, 1.0) for _ in xs]
    raise ValueError(f"合成の種類が分からない: {kind!r}")


def synth_rows(sa, bases: dict, count: int = N_SYNTH) -> dict:
    out = {}
    for spec in SYNTH:
        rows = []
        for i in range(count):
            vals = synth_series(spec, i)
            nm = normalize(vals)
            _, ys, s = nm
            row = {"i": i} | fit_row(sa, bases, ys, PRIMARY_TAU)
            if spec["kind"] in ("undamped", "damped"):
                row["true_amp"] = 2.0 * s              # 正規化後の波の振幅（h0 − L, B の二乗和の平方根）
            rows.append(row)
        out[spec["id"]] = rows
    return out


# ---- 基準 -------------------------------------------------------------------------------------------------------------
def stats(rows: list[dict]) -> dict:
    B = [r for r in rows if r["boundary"]]
    NB = [r for r in rows if not r["boundary"]]
    ref = ekey(EPS[-1])
    out = {"units": len(rows), "boundary": len(B), "nonboundary": len(NB),
           "boundary_share": len(B) / len(rows) if rows else None, "keep": {}, "c2": {}, "c3": {}, "at_start": {}}
    for e in EPS:
        k = ekey(e)
        kept = [r for r in B if r[k]["decay"] == e and r[k]["period"] is not None and r[k]["limit"] is not None
                and r[k]["settle_x"] is not None]
        out["keep"][k] = {"kept": len(kept), "of": len(B)}
        chg = [r for r in NB if (r[k]["decay"], r[k]["period"]) != (r["decay"], r["period"])]
        out["c3"][k] = {"changed": len(chg), "of": len(NB)}
        out["at_start"][k] = sum(1 for r in B if r[k]["at_start"])
        if k == ref:
            continue
        devs, mism = [], 0
        for r in B:
            a, b = r[k], r[ref]
            if a["decay"] != e or b["decay"] != EPS[-1]:
                continue                                  # ε の波が残らなかった単位は C1 で数える
            if a["at_start"] != b["at_start"]:
                mism += 1
                continue
            if a["at_start"]:
                continue
            devs.append(abs(a["coefficient"] - b["coefficient"]) / abs(b["coefficient"]))
        out["c2"][k] = {"max": max(devs) if devs else None, "n": len(devs), "mismatch": mism}
    coefs = [r[ekey(1e-6)]["coefficient"] for r in B if r[ekey(1e-6)]["coefficient"] is not None]
    out["coefficient_range_eps6"] = [min(coefs), max(coefs)] if coefs else None
    return out


def _v(cid: str, tag: str, text: str, value, thr, op: str, ok) -> dict:
    return {"id": cid, "set": tag, "text": text, "value": value, "threshold": thr, "op": op, "ok": ok}


def judge_real(st: dict, tag: str) -> list[dict]:
    """窓（実データ）の C1〜C3。集合が MIN_UNITS 未満なら判定不能（ok = None）。"""
    out = []
    enough_b, enough_nb = st["boundary"] >= MIN_UNITS, st["nonboundary"] >= MIN_UNITS
    for e in EPS:
        k = ekey(e)
        kp = st["keep"][k]
        share = kp["kept"] / kp["of"] if kp["of"] else None
        need = CRIT["c1_eps3"] if e == 1e-3 else 1.0
        out.append(_v("C1", tag, f"境界の単位で ε={e:g} の波が残る割合", share, need, ">=", (share >= need) if enough_b else None))
    for e, thr in ((1e-3, CRIT["c2_eps3"]), (1e-6, CRIT["c2_eps6"])):
        c2 = st["c2"][ekey(e)]
        ok = None
        if enough_b and c2["max"] is not None:
            ok = c2["max"] <= thr and c2["mismatch"] == 0
        out.append(_v("C2", tag, f"係数のずれ（ε={e:g} と 1e-9、相対）の最大。比べられない単位 {c2['mismatch']}", c2["max"], thr, "<=", ok))
    for e, key in ((1e-3, "c3_eps3"), (1e-6, "c3_eps6"), (1e-9, "c3_eps9")):
        c3 = st["c3"][ekey(e)]
        share = c3["changed"] / c3["of"] if c3["of"] else None
        out.append(_v("C3", tag, f"境界でない単位で ε={e:g} のとき選ばれる式が変わる割合", share, CRIT[key], "<=",
                      (share <= CRIT[key]) if enough_nb else None))
    return out


def judge_synth(rows_by_spec: dict) -> list[dict]:
    out = []
    und = [r for sid, rows in rows_by_spec.items() if sid.startswith("undamped") for r in rows]
    bnd = [r for r in und if r["boundary"]]
    share = len(bnd) / len(und) if und else None
    out.append(_v("C5", "合成・減衰しない", "減衰しない波の系列が、今のコードで境界（減衰 0）になる割合", share, CRIT["c5_boundary"], ">=",
                  (share >= CRIT["c5_boundary"]) if und else None))
    devs, unsettled = [], 0
    for r in bnd:
        c = r[ekey(1e-6)]["coefficient"]
        if c is None:                                       # 幅が PRIMARY_TAU 以下に見えた = 真の振幅（約 2.5）から大きく外れる
            unsettled += 1
            continue
        devs.append(abs(PRIMARY_TAU * math.exp(c) / r["true_amp"] - 1.0))
    worst = max(devs) if devs and not unsettled else None
    out.append(_v("C5", "合成・減衰しない", f"境界になった系列で、ε=1e-6 から戻した振幅（τ·e^係数）の真の振幅からの相対のずれの最大。始まりの時点で決まったと出た系列 {unsettled}",
                  worst, CRIT["c5_amp"], "<=", (not unsettled and max(devs) <= CRIT["c5_amp"]) if (devs or unsettled) else None))
    dmp = [r for sid, rows in rows_by_spec.items() if sid.startswith("damped") for r in rows]
    nb = [r for r in dmp if not r["boundary"]]
    for e, key in ((1e-3, "c3_eps3"), (1e-6, "c3_eps6"), (1e-9, "c3_eps9")):
        k = ekey(e)
        chg = sum(1 for r in nb if (r[k]["decay"], r[k]["period"]) != (r["decay"], r["period"]))
        share = chg / len(nb) if nb else None
        out.append(_v("C3", "合成・減衰する", f"減衰する波の系列（境界でないもの）で ε={e:g} のとき選ばれる式が変わる割合", share,
                      CRIT[key], "<=", (share <= CRIT[key]) if len(nb) >= MIN_UNITS else None))
    return out


def reference_info(rows_by_spec: dict) -> dict:
    """基準ではなく、参考: 合成の系列で今のコードが選ぶ式。"""
    out = {}
    for sid, rows in rows_by_spec.items():
        forms = {}
        for r in rows:
            k = f"decay={r['decay']:g},period={r['period']}"
            forms[k] = forms.get(k, 0) + 1
        out[sid] = dict(sorted(forms.items(), key=lambda kv: (-kv[1], kv[0])))
    return out


# ---- 対照（C4）-------------------------------------------------------------------------------------------------------
def controls(sa, mod, bases_by_n: dict) -> dict:
    """C4: (a) ε=0 に差し替えた格子が、今のコードの格子と、使う x のすべてで一致する。"""
    mod.self_check(sa)
    same = {}
    for n in bases_by_n:
        xs = [i / (n - 1) for i in range(n)]
        a, b = sa.wave_basis(xs), mod.make_wave_basis(sa, 0.0)(xs)
        same[str(n)] = len(a) == len(b) and all(x == y for x, y in zip(a, b))
    xs = [i / (SYNTH_POINTS - 1) for i in range(SYNTH_POINTS)]
    a, b = sa.wave_basis(xs), mod.make_wave_basis(sa, 0.0)(xs)
    same[f"synthetic{SYNTH_POINTS}"] = len(a) == len(b) and all(x == y for x, y in zip(a, b))
    return {"eps0_basis_identical": same, "pass": all(same.values())}


def compute(sa, mod, series: dict) -> dict:
    windows_by_n = {n: tile(series, n) for n in LENGTHS}
    bases_by_n = {n: make_bases(sa, mod, [i / (n - 1) for i in range(n)]) for n in LENGTHS}
    synth_bases = make_bases(sa, mod, [i / (SYNTH_POINTS - 1) for i in range(SYNTH_POINTS)])
    ctrl = controls(sa, mod, bases_by_n)
    real = real_rows(sa, bases_by_n, windows_by_n)
    synth = synth_rows(sa, synth_bases)
    sets = {}
    for n, d in real.items():
        st = stats(d["rows"])
        by_src = {}
        for g in sorted({r["source"] for r in d["rows"]}):
            sub = [r for r in d["rows"] if r["source"] == g]
            by_src[g] = {"units": len(sub), "boundary": sum(r["boundary"] for r in sub)}
        sets[str(n)] = {"windows": d["windows"], "constant_windows": d["constant_windows"], "stats": st, "by_source": by_src,
                        "series": len({(r["country"], r["variable"], r["source"]) for r in d["rows"]})}
    criteria = [c for n in LENGTHS for c in judge_real(sets[str(n)]["stats"], f"N={n}")] + judge_synth(synth)
    return {"spec_version": SPEC_VERSION, "seed": SEED, "control": ctrl, "sets": sets, "criteria": criteria,
            "synthetic_forms": reference_info(synth),
            "tau": tau_summary(sa, bases_by_n[PRIMARY], windows_by_n[PRIMARY]),
            "rows": {"real": {str(n): d["rows"] for n, d in real.items()}, "synthetic": synth}}


# ---- 書き出し ---------------------------------------------------------------------------------------------------------
def verdict_text(ok) -> str:
    return "判定不能" if ok is None else ("満たした" if ok else "**満たさなかった**")


def fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.3g}" if abs(v) < 1e4 else f"{v:.3e}"
    return str(v)


def render(res: dict) -> str:
    L = ["# ε の汎用性の確認: 結果（探索）", "",
         "基準は [README.md](../README.md) に事前に書いたもの。結果を見て変えていない。ε の値は暫定で、結論には使わない。", ""]
    ctrl = res["control"]
    L += ["## 対照（C4）", "", f"- ε=0 に差し替えた格子が今のコードの格子と一致: {ctrl['eps0_basis_identical']}（{'通った' if ctrl['pass'] else '**通らなかった**'}）",
          f"- 同じ入力で 2 回走らせた結果の一致: {'一致' if res.get('repeat_identical') else '**一致しなかった**'}", ""]
    L += ["## 窓（主食価格の月次）", "",
          "| 窓の長さ | 窓の数 | 幅 0 で除いた窓 | 系列の数 | 境界（減衰 0）の単位 | 割合 |", "|---|---|---|---|---|---|"]
    for n in LENGTHS:
        s = res["sets"][str(n)]
        st = s["stats"]
        L.append(f"| {n} か月 | {s['windows']} | {s['constant_windows']} | {s['series']} | {st['boundary']} / {st['units']} | {fmt(st['boundary_share'])} |")
    L += ["", f"野球（2013〜2026年）の境界は {BASEBALL['boundary']} / {BASEBALL['units']}（約 0.143）。", "",
          "出どころ別（24 か月）の境界の単位:", "", "| 出どころ | 単位 | 境界 |", "|---|---|---|"]
    for g, d in res["sets"][str(PRIMARY)]["by_source"].items():
        L.append(f"| {g} | {d['units']} | {d['boundary']} |")
    L += ["", "## 基準ごとの結果", "", "| 基準 | 対象 | 内容 | 値 | 基準値 | 読み |", "|---|---|---|---|---|---|"]
    for c in res["criteria"]:
        L.append(f"| {c['id']} | {c['set']} | {c['text']} | {fmt(c['value'])} | {c['op']} {fmt(c['threshold'])} | {verdict_text(c['ok'])} |")
    L += ["", "## 係数の範囲（ε=1e-6、境界の単位）", "", "| 窓の長さ | 係数の最小〜最大 | ε で位置が決まった単位のうち「始まりの時点で決まっていた」数（1e-3 / 1e-6 / 1e-9）|", "|---|---|---|"]
    for n in LENGTHS:
        st = res["sets"][str(n)]["stats"]
        rg = st["coefficient_range_eps6"]
        a = st["at_start"]
        L.append(f"| {n} か月 | {fmt(rg[0]) + ' 〜 ' + fmt(rg[1]) if rg else '—'} | {a[ekey(1e-3)]} / {a[ekey(1e-6)]} / {a[ekey(1e-9)]} |")
    L += ["", f"野球の係数の範囲は {BASEBALL['coefficient_range'][0]}〜{BASEBALL['coefficient_range'][1]}（24 単位）。", "",
          f"## τ（「決まった」とみなす幅）を変えたとき（{PRIMARY} か月、ε=1e-6）", "",
          "| τ | 境界の単位 | 始まりの時点で決まっていた | 係数の最小 | 係数の最大 | 式の選び方は最初の τ と同じ |", "|---|---|---|---|---|---|"]
    for t, d in res["tau"].items():
        L.append(f"| {t} | {d['boundary']} | {d['at_start']} | {fmt(d['coefficient_min'])} | {fmt(d['coefficient_max'])} | {d['forms_same_as_first_tau']} |")
    L += ["", "## 合成の系列で今のコードが選んだ式（参考。基準ではない）", ""]
    for sid, forms in res["synthetic_forms"].items():
        L.append(f"- {sid}: " + "、".join(f"{k} × {n}" for k, n in list(forms.items())[:6]))
    judged = [c for c in res["criteria"] if c["ok"] is not None]
    failed = [c for c in judged if not c["ok"]]
    L += ["", "## まとめ", ""]
    if not res["control"]["pass"] or not res.get("repeat_identical"):
        L.append("- 対照（C4）が通らなかったので、ほかの結果は読まない。")
    elif failed:
        L.append(f"- 判定できた {len(judged)} 件のうち、満たさなかったのは {len(failed)} 件: "
                 + "、".join(f"{c['id']}（{c['set']}、{c['text'][:24]}…）" for c in failed))
    else:
        L.append(f"- 判定できた {len(judged)} 件のすべてを満たした（判定不能 {len(res['criteria']) - len(judged)} 件）。ε の扱いについて、"
                 "主食価格の月次と合成の系列で**矛盾する材料はなかった**、までしか言えない（「確かめられた」とは書かない）。")
    return "\n".join(L) + "\n"


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, allow_nan=False)


def jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True, help="staple_survey_vertical.csv")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    sa, mod = load_modules(args.repo)
    series = read_series(args.csv)
    res = compute(sa, mod, series)
    again = compute(sa, mod, series)
    res["repeat_identical"] = json.dumps(res, allow_nan=False) == json.dumps(again, allow_nan=False)
    if not res["control"]["pass"] or not res["repeat_identical"]:
        print("対照（C4）が通らない。結果は書かない:", res["control"], res["repeat_identical"], file=sys.stderr)
        return 2
    args.outdir.mkdir(parents=True, exist_ok=True)
    rows = res.pop("rows")
    summary = dumps(res)
    (args.outdir / "eps_generality.json").write_text(summary + "\n", encoding="utf-8")
    (args.outdir / "eps_generality.md").write_text(render(res), encoding="utf-8")
    (args.outdir / f"eps_generality_units_n{PRIMARY}.jsonl").write_text(jsonl(rows["real"][str(PRIMARY)]), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
