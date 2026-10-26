#!/usr/bin/env python3
"""ε（波の減衰 0 の置き換え）が、野球以外の連続データでも使えるかの確認（探索）。

README.md に事前に書いた基準（C1〜C5）を、(1) リポジトリにある主食価格の月次の系列、(2) 答えが分かっている合成の系列、
に当てる。sakanalytics の wave_basis / wave_fit と、cycles/c001-chunichi/exploratory/wave_eps_trial.py の make_wave_basis
（減衰 0 の格子を ε に差し替える）をそのまま使う。野球の列（順位・試合・季節）には触れない。ε の値は暫定の置き場所で、結論には使わない。

使い方（リポジトリの直下から。polars が入った環境で）:
  uv run --locked python research/epsilon-generality/eps_generality.py \\
      --csv research/staple-price-survey/staple_survey_vertical.csv --outdir /tmp/eps-generality --repo .

物理量の回（README.md の「物理量の確認」）は --profile physical-monthly / physical-daily（入力は fetch_physical.py の出力）。
--profile を付けない主食価格の回の出力は、プロファイルを足す前とバイト単位で同じ。

乱数の ε と倍率（README.md の「乱数の ε と倍率の確認」）: --random-eps K / --random-scales K を付けると、決め打ちの ε（1e-3, 1e-6, 1e-9）と倍率に、
A×10^-N（ε。0 < ε ≤ 1/100）・A×10^e（倍率）の A（1.00〜9.99）と指数を乱数で選んだ値を K 個ずつ足す。--coef-seed に整数か auto を渡す（省略は SEED）。選んだ値と種は結果に書く。
これらを付けない出力は、足す前とバイト単位で同じ。
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import re
import secrets
import sys
from contextlib import contextmanager
from datetime import date
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
           ("BLS", "bls.gov"), ("e-Stat", "e-stat.go.jp"),
           ("NOAA-weather", "data/weather.csv"), ("Scripps-CO2", "co2-concentration.csv"), ("global-temp", "datasets/global-temp"))
# 物理量の回（README.md の「物理量の確認」）。基準は主食価格の回と同じ値で、合成の系列（C5）は入力によらないので省く。
SCALES = (1e-6, 1e-3, 1.0, 1e3, 1e6)   # 報告だけ（基準なし）: y と τ に同じ倍率をかけて、選ばれる式が動くかを見る
PROFILES = {
    "staple": {"prefix": "staple_price:", "cadence": "month", "label": "主食価格の月次", "synth": True, "scales": False},
    "physical-monthly": {"prefix": "physical:", "cadence": "month", "label": "物理量の月次", "synth": False, "scales": True},
    "physical-daily": {"prefix": "physical:", "cadence": "day", "label": "物理量の日次", "synth": False, "scales": True},
}
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


# ---- 乱数の ε と倍率（README.md の「乱数の ε と倍率の確認」。定義と基準値の置き方は走らせる前に決めた）-----------------------
REF_EPS = EPS[-1]                   # C2 の基準。乱数の ε を足しても変えない
EPS_LIMIT = 1e-2                    # ε の条件は 0 < ε ≤ 1/100 だけ。float でそのまま与えてもよい（A×10^-N は乱数で選ぶときの作り方）
A_MIN, A_MAX = 100, 999             # A = 1.00〜9.99（有効数字 3 桁。百分の一の整数で持つ）
N_MIN, N_CAP = 3, 307               # 乱数で選ぶ ε = A×10^-N は N = 3 から（A×10^-3 は 1/1000 以上 1/100 未満）。N に上限は置かず、A の 3 桁を保ったまま float で表せる 307 で止める（装置の限界）
E_CAP = 150                         # 倍率 = A×10^e の |e| の上限。y の2乗の和が float で表せる範囲（|e| が 153 を超えると桁あふれする）
P_STOP = 1 / 6                      # 指数を 1 つずつ増やし、各段で止まる確率（幾何分布、平均 5 段）。上限を置かずに、値が動きうる ε が大きい側に多く当たるようにする
ANCHOR_CRIT = {"c1": {1e-3: CRIT["c1_eps3"], 1e-6: 1.0, 1e-9: 1.0},          # 決め打ちの ε の基準値（登録した値そのまま）
               "c2": {1e-3: CRIT["c2_eps3"], 1e-6: CRIT["c2_eps6"]},
               "c3": {1e-3: CRIT["c3_eps3"], 1e-6: CRIT["c3_eps6"], 1e-9: CRIT["c3_eps9"]}}


def threshold(kind: str, e: float) -> float:
    """ε の基準値。決め打ちの ε は登録した値そのまま。それ以外は、1e-6 と 1e-3 の基準値を log10(ε) でつないだ直線（C1 は割合の直線、
    C2・C3 は値の対数の直線）。1e-3 より大きい ε（< 1/100）は同じ直線の延長、ε <= 1e-6 は 1e-6 の値のまま。定義域は 0 < ε ≤ 1/100（float ならどんな値でも通す）。"""
    t = ANCHOR_CRIT[kind]
    if e in t:
        return t[e]
    if not 0.0 < e <= EPS_LIMIT:
        raise ValueError(f"ε の定義域（0 < ε ≤ 1/100）の外: {e!r}")
    if e <= 1e-6:
        return t[1e-6]
    f = (math.log10(e) + 6.0) / 3.0                      # 1e-6 で 0、1e-3 で 1、1/100 で 4/3
    lo, hi = t[1e-6], t[1e-3]
    return lo + (hi - lo) * f if kind == "c1" else lo * (hi / lo) ** f


def pow10_text(x: float) -> str:
    """3.07e-05 → 3.07×10^-5"""
    m, ex = f"{x:.2e}".split("e")
    return f"{m}×10^{int(ex)}"


def elabel(e: float) -> str:
    return f"{e:g}" if e in EPS else pow10_text(e)


def _steps(rng: random.Random, cap: int) -> int:
    """各段で確率 P_STOP で止まる回数（0 から。cap まで）。"""
    n = 0
    while n < cap and rng.random() >= P_STOP:
        n += 1
    return n


def draw_coefficients(count: int, seed, kind: str) -> list[dict]:
    """A×10^x の A（1.00〜9.99）と指数 x を乱数で count 個選ぶ（値の重複なし。決め打ちの ε・倍率と同じ値は除く）。
    kind は "eps"（x = -N、N = 3 + 段の数。上限は置かず N_CAP まで）か "scale"（x = ±段の数。|x| は E_CAP まで）。
    {"a", "exp", "value"} のリストを値の大きい順で返す。同じ種なら同じ値。"""
    rng, out, tries = random.Random(f"{seed}/{kind}"), {}, 0
    while len(out) < count:
        tries += 1
        if tries > 10_000 + 100 * count:
            raise ValueError(f"{count} 個は選べない（{len(out)} 個で止まった）")
        a = rng.randint(A_MIN, A_MAX)
        x = -(N_MIN + _steps(rng, N_CAP - N_MIN)) if kind == "eps" else rng.choice((-1, 1)) * _steps(rng, E_CAP)
        v = float(f"{a // 100}.{a % 100:02d}e{x}")
        if v not in (EPS if kind == "eps" else SCALES) and v not in out:
            out[v] = {"a": a / 100, "exp": x, "value": v}
    return sorted(out.values(), key=lambda d: -d["value"])


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


def day_index(d: str) -> int:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        raise ValueError(f"日付が YYYY-MM-DD でない: {d!r}")
    return date.fromisoformat(d).toordinal()


def day_text(i: int) -> str:
    return date.fromordinal(i).isoformat()


# 刻み: 窓の長さの単位の語、日付 → 通し番号、通し番号 → 窓の最初の日付の文字
CADENCE = {"month": {"word": "月", "unit": "か月", "index": month_index, "text": month_text},
           "day": {"word": "日", "unit": "日", "index": day_index, "text": day_text}}


def read_series(path: Path, prefix: str = "staple_price:", cadence: str = "month") -> dict:
    """prefix で始まる変数の行から {(国, 変数, 単位, 出どころ, 注): {通し番号: 値}}。
    月の刻みでは日にちを無視して月を数え、同じ月（日の刻みなら同じ日）が 2 つあれば止まる。"""
    c = CADENCE[cadence]
    out: dict = {}
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if not r["variable"].startswith(prefix):
                continue
            v = float(r["value"])
            if not math.isfinite(v):
                raise ValueError(f"値が有限でない: {r}")
            s = out.setdefault((r["country"], r["variable"], r["unit"], r["source"], r["note"]), {})
            mi = c["index"](r["date"])
            if mi in s:
                raise ValueError(f"同じ{c['word']}が 2 つある: {(r['country'], r['variable'], r['date'])}")
            s[mi] = v
    return out


def tile(series: dict, n: int, text=month_text) -> list[dict]:
    """通し番号が途切れずに続く区間ごとに、先頭から n 点ずつ、互いに重ならない窓を並べる（余りは使わない）。"""
    out = []
    for si, key in enumerate(sorted(series)):
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
                out.append({"key": key, "si": si, "start": text(w[0][0]), "values": [v for _, v in w]})
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


def make_bases(sa, mod, xs: list[float], eps: tuple = EPS) -> dict:
    """{None: 今のコードの格子, ε: 減衰 0 を ε に差し替えた格子}。x が同じ窓では格子も同じなので、長さごとに 1 回作る。"""
    return {None: sa.wave_basis(xs)} | {e: mod.make_wave_basis(sa, e)(xs) for e in eps}


def fit_row(sa, bases: dict, ys: list[float], tau: float) -> dict:
    with settle_tolerance(sa, tau):
        res = {k: sa.wave_fit(ys, b, 0.0, 1.0) for k, b in bases.items()}
    u = res[None]
    row = {"decay": u["decay"], "period": u["period"], "rmse": u["rmse"], "limit": u["limit"], "settle_x": u["settle_x"],
           "boundary": u["decay"] == 0.0}
    for e in (k for k in bases if k is not None):                # 格子を作った ε すべて（乱数の ε を含む）
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
                         "unit": w["key"][2], "series_index": w["si"], "start": w["start"]}
                        | fit_row(sa, bases_by_n[n], ys, PRIMARY_TAU))
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
            forms.append((r["decay"], r["period"], r[ekey(REF_EPS)]["decay"], r[ekey(REF_EPS)]["period"]))
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


def scale_summary(sa, bases: dict, windows: list[dict], scales=None) -> dict:
    """報告だけ（基準なし）: 値の単位を変えたとき（y と τ に同じ倍率をかける）、選ばれる式・ε の波・係数が動くか。倍率 1 が基準。
    sakanalytics の絶対値の許容（EPS_WAVE_TIE など）は値の幅が 5 前後の尺度を前提にしているので、それが効く倍率を見る。
    scales を渡さなければ SCALES（乱数の倍率を足すときは、倍率 1 を含む値の列を渡す）。"""
    runs = {}
    for f in (SCALES if scales is None else scales):
        rows = []
        for w in windows:
            nm = normalize(w["values"])
            if nm is None:
                continue
            rows.append(fit_row(sa, bases, [y * f for y in nm[1]], PRIMARY_TAU * f))
        runs[f] = rows
    base, k = runs[1.0], ekey(1e-6)
    out = {}
    for f, rows in runs.items():
        pairs = list(zip(rows, base))
        both = [(r, b) for r, b in pairs if b["boundary"] and r["boundary"]]
        devs = [abs(r[k]["coefficient"] - b[k]["coefficient"]) / abs(b[k]["coefficient"]) for r, b in both
                if r[k]["coefficient"] is not None and b[k]["coefficient"] is not None]
        out[f"{f:g}"] = {
            "units": len(rows), "boundary": sum(r["boundary"] for r in rows),
            "forms_changed": sum((r["decay"], r["period"]) != (b["decay"], b["period"]) for r, b in pairs),
            "boundary_flag_changed": sum(r["boundary"] != b["boundary"] for r, b in pairs),
            "eps_wave_kept": sum(1 for r, b in pairs if b["boundary"] and r[k]["decay"] == 1e-6),
            "at_start_changed": sum(1 for r, b in both if r[k]["at_start"] != b[k]["at_start"]),
            "coefficient_max_dev": max(devs) if devs else None, "coefficient_n": len(devs)}
    return out


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
def stats(rows: list[dict], eps: tuple = EPS) -> dict:
    B = [r for r in rows if r["boundary"]]
    NB = [r for r in rows if not r["boundary"]]
    ref = ekey(REF_EPS)
    out = {"units": len(rows), "boundary": len(B), "nonboundary": len(NB),
           "boundary_share": len(B) / len(rows) if rows else None, "keep": {}, "c2": {}, "c3": {}, "at_start": {}}
    for e in eps:
        k = ekey(e)
        kept = [r for r in B if r[k]["decay"] == e and r[k]["period"] is not None and r[k]["limit"] is not None
                and r[k]["settle_x"] is not None and math.isfinite(r[k]["settle_x"])]   # 極小の ε で settle_x が float の範囲を超えたら「残った」に数えない
        out["keep"][k] = {"kept": len(kept), "of": len(B)}
        chg = [r for r in NB if (r[k]["decay"], r[k]["period"]) != (r["decay"], r["period"])]
        out["c3"][k] = {"changed": len(chg), "of": len(NB)}
        out["at_start"][k] = sum(1 for r in B if r[k]["at_start"])
        if k == ref:
            continue
        devs, mism = [], 0
        for r in B:
            a, b = r[k], r[ref]
            if a["decay"] != e or b["decay"] != REF_EPS:
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


def judge_real(st: dict, tag: str, eps: tuple = EPS) -> list[dict]:
    """窓（実データ）の C1〜C3。集合が MIN_UNITS 未満なら判定不能（ok = None）。基準値は threshold()（決め打ちの ε は登録した値）。"""
    out = []
    enough_b, enough_nb = st["boundary"] >= MIN_UNITS, st["nonboundary"] >= MIN_UNITS
    for e in eps:
        kp = st["keep"][ekey(e)]
        share = kp["kept"] / kp["of"] if kp["of"] else None
        need = threshold("c1", e)
        out.append(_v("C1", tag, f"境界の単位で ε={elabel(e)} の波が残る割合", share, need, ">=", (share >= need) if enough_b else None))
    for e in (e for e in eps if e != REF_EPS):
        thr = threshold("c2", e)
        c2 = st["c2"][ekey(e)]
        ok = None
        if enough_b and c2["max"] is not None:
            ok = c2["max"] <= thr and c2["mismatch"] == 0
        out.append(_v("C2", tag, f"係数のずれ（ε={elabel(e)} と 1e-9、相対）の最大。比べられない単位 {c2['mismatch']}", c2["max"], thr, "<=", ok))
    for e in eps:
        thr = threshold("c3", e)
        c3 = st["c3"][ekey(e)]
        share = c3["changed"] / c3["of"] if c3["of"] else None
        out.append(_v("C3", tag, f"境界でない単位で ε={elabel(e)} のとき選ばれる式が変わる割合", share, thr, "<=",
                      (share <= thr) if enough_nb else None))
    return out


def judge_synth(rows_by_spec: dict, eps: tuple = EPS) -> list[dict]:
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
    for e in eps:
        k, thr = ekey(e), threshold("c3", e)
        chg = sum(1 for r in nb if (r[k]["decay"], r[k]["period"]) != (r["decay"], r["period"]))
        share = chg / len(nb) if nb else None
        out.append(_v("C3", "合成・減衰する", f"減衰する波の系列（境界でないもの）で ε={elabel(e)} のとき選ばれる式が変わる割合", share,
                      thr, "<=", (share <= thr) if len(nb) >= MIN_UNITS else None))
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


def compute(sa, mod, series: dict, profile: str = "staple", draws: dict | None = None) -> dict:
    """draws = {"seed", "eps": [...], "scales": [...]}（draw_coefficients の結果）を渡すと、決め打ちの ε・倍率に乱数の値を足す。渡さなければ足す前と同じ。"""
    prof = PROFILES[profile]
    eps = EPS + tuple(d["value"] for d in (draws or {}).get("eps", ()))
    scales = None
    if (draws or {}).get("scales"):
        scales = tuple(sorted(set(SCALES) | {d["value"] for d in draws["scales"]}))
    windows_by_n = {n: tile(series, n, CADENCE[prof["cadence"]]["text"]) for n in LENGTHS}
    bases_by_n = {n: make_bases(sa, mod, [i / (n - 1) for i in range(n)], eps) for n in LENGTHS}
    ctrl = controls(sa, mod, bases_by_n)
    real = real_rows(sa, bases_by_n, windows_by_n)
    synth = synth_rows(sa, make_bases(sa, mod, [i / (SYNTH_POINTS - 1) for i in range(SYNTH_POINTS)], eps)) if prof["synth"] else {}
    sets = {}
    for n, d in real.items():
        st = stats(d["rows"], eps)
        by_src = {}
        for g in sorted({r["source"] for r in d["rows"]}):
            sub = [r for r in d["rows"] if r["source"] == g]
            by_src[g] = {"units": len(sub), "boundary": sum(r["boundary"] for r in sub)}
        sets[str(n)] = {"windows": d["windows"], "constant_windows": d["constant_windows"], "stats": st, "by_source": by_src,
                        "series": len({(r["country"], r["variable"], r["source"]) for r in d["rows"]})}
    criteria = [c for n in LENGTHS for c in judge_real(sets[str(n)]["stats"], f"N={n}", eps)] + (judge_synth(synth, eps) if prof["synth"] else [])
    res = {"spec_version": SPEC_VERSION, "seed": SEED, "control": ctrl, "sets": sets, "criteria": criteria,
           "synthetic_forms": reference_info(synth),
           "tau": tau_summary(sa, bases_by_n[PRIMARY], windows_by_n[PRIMARY])}
    if profile != "staple":                                  # 主食価格の回の出力にはキーを足さない（バイト単位で同じ）
        res["profile"] = profile
    if draws:
        res["random_coefficients"] = draws
    if prof["scales"] or scales:
        res["scales"] = scale_summary(sa, bases_by_n[PRIMARY], windows_by_n[PRIMARY], scales)
    res["rows"] = {"real": {str(n): d["rows"] for n, d in real.items()}, "synthetic": synth}
    return res


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
    prof = PROFILES[res.get("profile", "staple")]
    uw = CADENCE[prof["cadence"]]["unit"]
    L = ["# ε の汎用性の確認: 結果（探索）", "",
         "基準は [README.md](../README.md) に事前に書いたもの。結果を見て変えていない。ε の値は暫定で、結論には使わない。", ""]
    ctrl = res["control"]
    L += ["## 対照（C4）", "", f"- ε=0 に差し替えた格子が今のコードの格子と一致: {ctrl['eps0_basis_identical']}（{'通った' if ctrl['pass'] else '**通らなかった**'}）",
          f"- 同じ入力で 2 回走らせた結果の一致: {'一致' if res.get('repeat_identical') else '**一致しなかった**'}", ""]
    L += [f"## 窓（{prof['label']}）", "",
          "| 窓の長さ | 窓の数 | 幅 0 で除いた窓 | 系列の数 | 境界（減衰 0）の単位 | 割合 |", "|---|---|---|---|---|---|"]
    for n in LENGTHS:
        s = res["sets"][str(n)]
        st = s["stats"]
        L.append(f"| {n} {uw} | {s['windows']} | {s['constant_windows']} | {s['series']} | {st['boundary']} / {st['units']} | {fmt(st['boundary_share'])} |")
    L += ["", f"野球（2013〜2026年）の境界は {BASEBALL['boundary']} / {BASEBALL['units']}（約 0.143）。", "",
          f"出どころ別（{PRIMARY} {uw}）の境界の単位:", "", "| 出どころ | 単位 | 境界 |", "|---|---|---|"]
    for g, d in res["sets"][str(PRIMARY)]["by_source"].items():
        L.append(f"| {g} | {d['units']} | {d['boundary']} |")
    L += ["", "## 基準ごとの結果", "", "| 基準 | 対象 | 内容 | 値 | 基準値 | 読み |", "|---|---|---|---|---|---|"]
    for c in res["criteria"]:
        L.append(f"| {c['id']} | {c['set']} | {c['text']} | {fmt(c['value'])} | {c['op']} {fmt(c['threshold'])} | {verdict_text(c['ok'])} |")
    rc = res.get("random_coefficients")
    if rc:
        L += ["", "## 乱数で選んだ ε と倍率", "",
              f"種 {rc['seed']}。ε = A×10^-N（A = 1.00〜9.99、N = 3 から上限なし）と倍率 = A×10^e（A は同じ、e は 0 から両側へ上限なし）の A と指数を乱数で選び、"
              "決め打ちの値に足した。ε の条件は 0 < ε ≤ 1/100 だけ。乱数の ε の基準値は、登録した 1e-3 と 1e-6 の基準値を log10(ε) でつないだ直線（1e-3 より大きい側は延長、1e-6 以下は 1e-6 の値）。", "",
              "- ε: " + (", ".join(pow10_text(d["value"]) for d in rc["eps"]) or "なし"),
              "- 倍率: " + (", ".join(pow10_text(d["value"]) for d in rc["scales"]) or "なし")]
    L += ["", "## 係数の範囲（ε=1e-6、境界の単位）", "", "| 窓の長さ | 係数の最小〜最大 | ε で位置が決まった単位のうち「始まりの時点で決まっていた」数（1e-3 / 1e-6 / 1e-9）|", "|---|---|---|"]
    for n in LENGTHS:
        st = res["sets"][str(n)]["stats"]
        rg = st["coefficient_range_eps6"]
        a = st["at_start"]
        L.append(f"| {n} {uw} | {fmt(rg[0]) + ' 〜 ' + fmt(rg[1]) if rg else '—'} | {a[ekey(1e-3)]} / {a[ekey(1e-6)]} / {a[ekey(1e-9)]} |")
    L += ["", f"野球の係数の範囲は {BASEBALL['coefficient_range'][0]}〜{BASEBALL['coefficient_range'][1]}（24 単位）。", "",
          f"## τ（「決まった」とみなす幅）を変えたとき（{PRIMARY} {uw}、ε=1e-6）", "",
          "| τ | 境界の単位 | 始まりの時点で決まっていた | 係数の最小 | 係数の最大 | 式の選び方は最初の τ と同じ |", "|---|---|---|---|---|---|"]
    for t, d in res["tau"].items():
        L.append(f"| {t} | {d['boundary']} | {d['at_start']} | {fmt(d['coefficient_min'])} | {fmt(d['coefficient_max'])} | {d['forms_same_as_first_tau']} |")
    if res["synthetic_forms"]:
        L += ["", "## 合成の系列で今のコードが選んだ式（参考。基準ではない）", ""]
        for sid, forms in res["synthetic_forms"].items():
            L.append(f"- {sid}: " + "、".join(f"{k} × {n}" for k, n in list(forms.items())[:6]))
    if res.get("scales"):
        L += ["", f"## 値の単位を変えたとき（{PRIMARY} {uw}、報告だけで基準はない。倍率 1 が基準）", "",
              "y と τ に同じ倍率をかけて当てはめ直した。「式が変わった」は選ばれる（減衰, 周期）が倍率 1 と違う単位の数。", "",
              "| 倍率 | 単位 | 境界 | 式が変わった | 境界かどうかが変わった | ε=1e-6 の波が残った（倍率 1 の境界のうち） | 始まりの時点で決まっていたかが変わった | 係数のずれの最大（相対）| 比べた単位 |",
              "|---|---|---|---|---|---|---|---|---|"]
        for f, d in res["scales"].items():
            L.append(f"| {f if float(f) in SCALES else pow10_text(float(f))} | {d['units']} | {d['boundary']} | {d['forms_changed']} | {d['boundary_flag_changed']} | {d['eps_wave_kept']} | "
                     f"{d['at_start_changed']} | {fmt(d['coefficient_max_dev'])} | {d['coefficient_n']} |")
    judged = [c for c in res["criteria"] if c["ok"] is not None]
    failed = [c for c in judged if not c["ok"]]
    L += ["", "## まとめ", ""]
    if not res["control"]["pass"] or not res.get("repeat_identical"):
        L.append("- 対照（C4）が通らなかったので、ほかの結果は読まない。")
    elif failed:
        L.append(f"- 判定できた {len(judged)} 件のうち、満たさなかったのは {len(failed)} 件: "
                 + "、".join(f"{c['id']}（{c['set']}、{c['text'][:24]}…）" for c in failed))
    else:
        target = prof["label"] + ("と合成の系列" if prof["synth"] else "")
        L.append(f"- 判定できた {len(judged)} 件のすべてを満たした（判定不能 {len(res['criteria']) - len(judged)} 件）。ε の扱いについて、"
                 f"{target}で**矛盾する材料はなかった**、までしか言えない（「確かめられた」とは書かない）。")
    return "\n".join(L) + "\n"


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, allow_nan=False)


def jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, required=True, help="staple_survey_vertical.csv（物理量の回は fetch_physical.py の出力）")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="staple")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--random-eps", type=int, default=0, metavar="K", help="A×10^-N の ε を乱数で K 個足す")
    ap.add_argument("--random-scales", type=int, default=0, metavar="K", help="A×10^e の倍率を乱数で K 個足す（報告だけ）")
    ap.add_argument("--coef-seed", default=None, help="乱数の種。整数か auto（実行ごとに変わる）。省略は SEED。選んだ値と種は結果に書く")
    args = ap.parse_args(argv)
    draws = None
    if args.random_eps or args.random_scales:
        seed = SEED if args.coef_seed is None else (secrets.randbelow(10**9) if args.coef_seed == "auto" else int(args.coef_seed))
        draws = {"seed": seed, "eps": draw_coefficients(args.random_eps, seed, "eps"),
                 "scales": draw_coefficients(args.random_scales, seed, "scale")}
        print(f"乱数の種: {seed}", file=sys.stderr)
    sa, mod = load_modules(args.repo)
    prof = PROFILES[args.profile]
    series = read_series(args.csv, prof["prefix"], prof["cadence"])
    res = compute(sa, mod, series, args.profile, draws)
    again = compute(sa, mod, series, args.profile, draws)
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
