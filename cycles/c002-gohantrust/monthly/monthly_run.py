#!/usr/bin/env python3
"""サイクル2 月次の命題（族 A: 予測のはしご、族 B: 恒等式の言い切り）。
事前宣言: monthly_prelock_2026-11-13.md（第1弾）、monthly_prelock_r2_2026-11-13.md（第2弾: 帯を標本誤差に）、
monthly_prelock_r3_2026-11-13.md（第3弾: 族 A の E を米・穀類の寄与に、族 B を年の単位で＝族 Y）、
monthly_prelock_r4_2026-11-13.md（第4弾: 族 Y に量の段＝国全体の実質の消費の伸びと、食料の支出弾力性）、
monthly_prelock_r5_2026-11-13.md（第5弾: 2013 年の判例・言い切れなかった 3 年・2025 年の初めての確かめ）

  uv run --locked python -I cycles/c002-gohantrust/monthly/monthly_run.py count   # 条件の側の件数だけ（結論は計算しない）
  uv run --locked python -I cycles/c002-gohantrust/monthly/monthly_run.py judge   # 単位を作り、命題を判定して outputs/ に書く

単位は 1 か月（族 A・B）か 1 年（族 Y）。列 team は暦の月（m01〜m12）か y、season は年、family は族（A / B / Y）。
ゼロ・NaN が出たときは、値を変えずにログに出す（ε の方針。置き換えはしない）。
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "research" / "staple-price-survey" / "phase2_archive"
RICE = ARCHIVE / "japan_retail_price_rice_panel.csv.gz"      # 小売物価統計調査 うるち米 銘柄 1002 都市平均（円/5kg）
ENGEL = ARCHIVE / "engel_food_panel_monthly.csv.gz"           # 家計調査 用途分類 二人以上 全国（円/月）
ENGEL_YEAR = ARCHIVE / "engel_food_panel_annual.csv"          # 同じ長期時系列の年平均（族 Y）
MACRO = ARCHIVE.parent / "staple_survey_B_C_bigmac.csv"       # 世界銀行 家計最終消費支出（名目）・人口（族 Y の量の段）
REINF = ARCHIVE.parent / "reinforcement" / "reinforcement_vertical.csv.gz"   # USDA ERS の所得弾力性（日本の食料）
FAO_KCAL = ARCHIVE / "fao_fbsh_kcal_supply_panel.csv.gz"     # 第5弾: FAO 食料需給表（旧）1 人 1 日の供給熱量（日本は 2013 年まで）
ESRI = HERE / "esri_private_consumption.csv"                  # 第5弾: 内閣府 国民経済計算の暦年 民間最終消費支出（名目）。2025 年の確かめ用
CPI = ARCHIVE / "japan_cpi_food_cereals_panel.csv.gz"         # 消費者物価指数 2025 年基準 全国（総合・食料・穀類）
PROPS = (HERE / "monthly_propositions.toml", HERE / "monthly_propositions_r2.toml",
         HERE / "monthly_propositions_r3.toml", HERE / "monthly_propositions_r4.toml",
         HERE / "monthly_propositions_r5.toml")   # 事前登録の順。後の弾は前の id を parent に持てる
OUT = HERE / "outputs"

# 宣言 §2・§3 の範囲（月は 12·年 + 月 − 1 の整数で持つ）
A_FIRST, A_LAST = 2006 * 12 + 1, 2025 * 12 + 11   # 族 A の目標月 2006-02 〜 2025-12
A_TRAIN0 = 2001 * 12 + 1                          # 族 A の訓練の最初の目標月 2001-02（x が E の 2000-01 から作れる最初）
A_MIN_TRAIN = 60
B_FIRST, B_LAST = 2001 * 12 + 0, 2025 * 12 + 11   # 族 B の月 2001-01 〜 2025-12
TICK = 0.001                                      # E の公表刻み（0.1 ポイント）
# 第2弾の帯: 家計調査の標本誤差から作る ln E の前年比の標準誤差（宣言 r2 §1・§2）。
# 消費支出の月の標準誤差率 1.5 %（家計調査の概要 2025 年 表3 の中央値）、食料はその 0.9/1.7 倍（平成16年10月の表の比）。
# F と C の相関を 0 とした上限、12 か月離れた月は別の世帯（6 か月で交替）なので √2 倍
SE_CE, SE_FOOD_RATIO = 0.015, 0.9 / 1.7
SIGMA = math.sqrt(2) * math.hypot(SE_CE, SE_CE * SE_FOOD_RATIO)
# 第3弾の族 Y の帯: 年平均の標準誤差率（家計調査の概要 2025 年 表2: 消費支出 0.4 %、食料 0.2 %）から同じ作り方（宣言 r3 §2）
SIGMA_YEAR = math.sqrt(2) * math.hypot(0.004, 0.002)
Y_FIRST, Y_LAST = 2001, 2025

LOG: list[str] = []


def ym(k: int) -> tuple[int, int]:
    return k // 12, k % 12 + 1


def k_of(y: int, m: int) -> int:
    return y * 12 + m - 1


def note(kind: str, k: int, name: str, v: float) -> None:
    """ゼロ・NaN を見つけたら記録する（値は変えない）。"""
    y, m = ym(k)
    LOG.append(f"{kind}: {y}-{m:02d} {name} = {v!r}（値は変えない）")


def watch(k: int, **vals: float) -> None:
    for name, v in vals.items():
        if v is None or (isinstance(v, float) and math.isnan(v)):
            note("NaN", k, name, v)
        elif v == 0:
            note("ゼロ", k, name, v)


# ---------- 入力 ----------

def load() -> dict:
    """3 つの一次資料のパネルを読む。月の欠けは、使うときに KeyError で止まる（黙って埋めない）。"""
    rice = {}
    with gzip.open(RICE, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["variable"] == "japan_rps_uruchi_rice_mean_city_yen_per_5kg" and r["item_code"] == "1002":
                rice[k_of(int(r["year"]), int(r["month"]))] = float(r["value"])
    hh = {}
    with gzip.open(ENGEL, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hh[k_of(int(r["year"]), int(r["month"]))] = {
                c: float(r[c]) for c in ("food_yen_month", "ce_yen_month", "rice_yen_month", "cereals_yen_month")}
    cpi = {"all_items": {}, "food": {}, "cereals": {}}
    cpi_year = {"all_items": {}, "food": {}, "cereals": {}}
    with gzip.open(CPI, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["series_id"] not in cpi:
                continue
            if r["frequency"] == "monthly":
                cpi[r["series_id"]][k_of(int(r["year"]), int(r["month"]))] = float(r["index_value"])
            elif r["frequency"] == "annual_calendar_mean" and r["n_months"] == "12":   # 12 か月そろった年だけ
                cpi_year[r["series_id"]][int(r["year"])] = float(r["index_value"])
    hh_year = {}
    with open(ENGEL_YEAR, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hh_year[int(r["year"])] = {
                c: float(r[c]) for c in ("food_yen_month", "ce_yen_month", "rice_yen_month", "cereals_yen_month")}
    macro = {"hfce": {}, "pop": {}}                      # 第4弾: 量の段。家計調査とは別の出所（国民経済計算・人口）
    with open(MACRO, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["country"] == "JPN" and r["variable"] in ("household_consumption_total_lcu", "population_total"):
                macro["hfce" if r["variable"].startswith("household") else "pop"][int(r["year"])] = float(r["value"])
    eta_food = None
    with gzip.open(REINF, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["country"] == "JPN" and r["variable"] == "income_elasticity_food_broad_usda2005":
                eta_food = float(r["value"])
    esri = {}                                           # 世界銀行の値がまだない年（2025 年）だけ、同じ公表の前の年との比で使う（宣言 r5 §5）
    if ESRI.exists():
        with open(ESRI, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                esri[int(r["year"])] = float(r["value_billion_yen"])
    macro["esri"] = esri
    kcal = {}
    with gzip.open(FAO_KCAL, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["iso3"] == "JPN" and r["variable"] == "fbsh_kcal_cap_day_total":
                kcal[int(r["year"])] = float(r["value"])
    return {"P": rice, "hh": hh, "cpi": cpi, "cpi_year": cpi_year, "hh_year": hh_year,
            "macro": macro, "eta_food": eta_food, "kcal": kcal}


def engel(d: dict, k: int) -> float:
    h = d["hh"][k]
    return h["food_yen_month"] / h["ce_yen_month"]


# ---------- 族 A: 予測のはしご（宣言 §2）----------

def a_conditions(d: dict) -> list[dict]:
    """族 A の条件の側だけ（x と刻み）。結論（翌月の米価の変化）は計算しない。
    xr・xc は第3弾: E の動きのうち、起点の月の米（c1）・穀類（c2）の寄与だけ（族 B の式。宣言 r3 §3）。"""
    bc = {r["k"]: r for r in b_conditions(d)}
    rows = []
    for t in range(A_FIRST, A_LAST + 1):
        e1 = engel(d, t - 1)
        x = math.log(e1 / engel(d, t - 13))
        tau = TICK / e1
        xr, xc = bc[t - 1]["c1"], bc[t - 1]["c2"]
        rows.append({"k": t, "x": x, "tau": tau, "ax": abs(x) / tau, "axs": abs(x) / SIGMA,
                     "xr": xr, "xc": xc, "axr": abs(xr) / tau, "axc": abs(xc) / tau})
    return rows


def _a_pair(d: dict, s: int) -> tuple[float, float, float]:
    """目標月 s の (y, m, x)。m・x は起点 s−1 までの値で作る。"""
    P = d["P"]
    y = math.log(P[s] / P[s - 1])
    m = math.log(P[s - 1] / P[s - 2])
    x = math.log(engel(d, s - 1) / engel(d, s - 13))
    return y, m, x


def a_units(d: dict) -> list[dict]:
    pairs = {s: _a_pair(d, s) for s in range(A_TRAIN0, A_LAST + 1)}
    bc = {r["k"]: r for r in b_conditions(d)}
    xrc = {s: (bc[s - 1]["c1"], bc[s - 1]["c2"]) for s in range(A_TRAIN0, A_LAST + 1)}   # 第3弾の x の替わり
    out = []
    for c in a_conditions(d):
        t = c["k"]
        tr = [pairs[s] for s in range(A_TRAIN0, t)]       # 起点 t−1 で結果が分かっている目標月だけ
        if len(tr) < A_MIN_TRAIN:
            raise ValueError(f"訓練が {A_MIN_TRAIN} 点に満たない: {ym(t)}")
        Y = np.array([p[0] for p in tr])
        M = np.array([p[1] for p in tr])
        X = np.array([p[2] for p in tr])
        one = np.ones(len(Y))
        y, m, x = pairs[t]
        f1 = float(Y.mean())
        b2 = np.linalg.lstsq(np.column_stack([one, M]), Y, rcond=None)[0]
        b3 = np.linalg.lstsq(np.column_stack([one, M, X]), Y, rcond=None)[0]
        f2 = float(b2[0] + b2[1] * m)
        f3 = float(b3[0] + b3[1] * m + b3[2] * x)
        e0, e1, e2, e3 = abs(y), abs(y - f1), abs(y - f2), abs(y - f3)
        alt = {}
        for j, name in ((0, "r"), (1, "c")):                # 第3弾: 段 3 の x を米・穀類の寄与に替える
            XA = np.array([xrc[s][j] for s in range(A_TRAIN0, t)])
            bb = np.linalg.lstsq(np.column_stack([one, M, XA]), Y, rcond=None)[0]
            fa = float(bb[0] + bb[1] * m + bb[2] * xrc[t][j])
            alt |= {f"f3{name}": fa, f"gamma_{name}": float(bb[2]),
                    f"a3{name}": abs(y - fa) < e2, f"gain3{name}": e2 - abs(y - fa)}
        watch(t, y=y, m=m, x=x)
        yy, mm = ym(t)
        out.append({
            "family": "A", "team": f"m{mm:02d}", "team_name": f"{yy}年{mm}月", "season": yy, "month": mm,
            "y": y, "m_prev": m, "x": x, "tau": c["tau"], "ax": c["ax"], "axs": c["axs"],
            "xr": c["xr"], "xc": c["xc"], "axr": c["axr"], "axc": c["axc"], **alt,
            "f1": f1, "f2": f2, "f3": f3, "rho": float(b2[1]), "gamma": float(b3[2]), "n_train": len(tr),
            "a1": e1 < e0, "a2": e2 < e1, "a3": e3 < e2,
            "gain1": e0 - e1, "gain2": e1 - e2, "gain3": e2 - e3,
        })
    return out


# ---------- 族 B: 恒等式の言い切り（宣言 §3）----------

def _contrib(share: float, g: float, e0: float) -> float:
    """量を固定し、その分類の値段だけが 1+g 倍になったときの ln E の動き（厳密な形）。
    F は 1 + share·g 倍、C は 1 + e0·share·g 倍になる。"""
    return math.log1p(share * g) - math.log1p(e0 * share * g)


def b_conditions(d: dict) -> list[dict]:
    """族 B の条件の側だけ（式の見込み c1〜c4 と刻み）。結論（E の前年比）は計算しない。"""
    rows = []
    P, cpi = d["P"], d["cpi"]
    for t in range(B_FIRST, B_LAST + 1):
        h0 = d["hh"][t - 12]
        e0 = h0["food_yen_month"] / h0["ce_yen_month"]
        s_r = h0["rice_yen_month"] / h0["food_yen_month"]
        s_c = h0["cereals_yen_month"] / h0["food_yen_month"]
        g_r = P[t] / P[t - 12] - 1
        g_c = cpi["cereals"][t] / cpi["cereals"][t - 12] - 1
        g_f = cpi["food"][t] / cpi["food"][t - 12] - 1
        g_a = cpi["all_items"][t] / cpi["all_items"][t - 12] - 1
        c = [_contrib(s_r, g_r, e0), _contrib(s_c, g_c, e0), _contrib(1.0, g_f, e0),
             math.log1p(g_f) - math.log1p(g_a)]
        tau = TICK / e0
        row = {"k": t, "e0": e0, "s_rice": s_r, "s_cereals": s_c, "tau": tau}
        for i, v in enumerate(c, 1):
            row[f"c{i}"] = v
            row[f"ac{i}"] = abs(v) / tau
            row[f"acs{i}"] = abs(v) / SIGMA
        rows.append(row)
    return rows


def b_units(d: dict) -> list[dict]:
    out = []
    for c in b_conditions(d):
        t = c["k"]
        ye = math.log(engel(d, t) / engel(d, t - 12))
        yy, mm = ym(t)
        u = [abs(ye)] + [abs(ye - c[f"c{i}"]) for i in range(1, 5)]
        watch(t, yE=ye, **{f"c{i}": c[f"c{i}"] for i in range(1, 5)})
        row = {"family": "B", "team": f"m{mm:02d}", "team_name": f"{yy}年{mm}月", "season": yy, "month": mm,
               "yE": ye, "tau": c["tau"], "e0": c["e0"], "s_rice": c["s_rice"], "s_cereals": c["s_cereals"]}
        for i in range(1, 5):
            row[f"c{i}"], row[f"ac{i}"], row[f"acs{i}"] = c[f"c{i}"], c[f"ac{i}"], c[f"acs{i}"]
            row[f"u{i}"] = ye - c[f"c{i}"]
            row[f"l{i}"] = u[i] < u[i - 1]          # 段 i の残りが段 i−1 より小さい
        row["u0"] = ye
        out.append(row)
    return out


# ---------- 族 Y: 族 B を年の単位で（宣言 r3 §2・§4）----------

def y_conditions(d: dict) -> list[dict]:
    """族 Y の条件の側だけ（年の式の見込み c1〜c4 と帯）。結論（E の前年比）は計算しない。
    重みは前の年の年平均、値段は年平均（P は 12 か月の平均、物価指数は暦年の平均）。"""
    rows = []
    hy, cy, P = d["hh_year"], d["cpi_year"], d["P"]

    def p_year(y):
        return math.fsum(P[k_of(y, m)] for m in range(1, 13)) / 12

    for t in range(Y_FIRST, Y_LAST + 1):
        h0 = hy[t - 1]
        e0 = h0["food_yen_month"] / h0["ce_yen_month"]
        s_r = h0["rice_yen_month"] / h0["food_yen_month"]
        s_c = h0["cereals_yen_month"] / h0["food_yen_month"]
        rel = {s: cy[s][t] / cy[s][t - 1] for s in ("cereals", "food", "all_items")}
        c = [_contrib(s_r, p_year(t) / p_year(t - 1) - 1, e0), _contrib(s_c, rel["cereals"] - 1, e0),
             _contrib(1.0, rel["food"] - 1, e0), math.log(rel["food"]) - math.log(rel["all_items"])]
        # 第4弾（宣言 r4 §2）: 量の段。q = 国全体の 1 人当たり実質の消費の伸び（名目 ÷ 総合の物価指数 ÷ 人口）。
        # 段 5 は食料の量が一定、段 6 は食料の量が支出弾力性 η のぶん付いていく。年がそろわない（2025 年）ときは None
        mac = d["macro"]
        if t in mac["hfce"] and t - 1 in mac["hfce"]:
            nominal = mac["hfce"][t] / mac["hfce"][t - 1]
        elif t in mac["esri"] and t - 1 in mac["esri"]:   # 第5弾: 世界銀行にない年は、内閣府の同じ公表の 2 年の比
            nominal = mac["esri"][t] / mac["esri"][t - 1]
        else:
            nominal = None
        if nominal is not None:
            q = math.log(nominal) - math.log(rel["all_items"]) - math.log(mac["pop"][t] / mac["pop"][t - 1])
            c += [c[3] - q, c[3] - (1 - d["eta_food"]) * q]
        else:
            q = None
            c += [None, None]
        # 第5弾（宣言 r5 §3）: 段 7 = 段 5 の「食料の量は一定」を、FAO の 1 人当たり供給熱量の伸び qf に替える
        kc = d["kcal"]
        qf = math.log(kc[t] / kc[t - 1]) if (t in kc and t - 1 in kc) else None
        c.append(c[4] + qf if (qf is not None and c[4] is not None) else None)
        row = {"k": t, "e0": e0, "s_rice": s_r, "s_cereals": s_c, "q": q, "qf": qf}
        for i, v in enumerate(c, 1):
            row[f"c{i}"], row[f"acy{i}"] = v, (abs(v) / SIGMA_YEAR if v is not None else None)
        rows.append(row)
    return rows


def y_units(d: dict) -> list[dict]:
    hy = d["hh_year"]
    out = []
    for c in y_conditions(d):
        t = c["k"]
        ye = math.log((hy[t]["food_yen_month"] / hy[t]["ce_yen_month"]) / c["e0"])
        watch(k_of(t, 1), yE_year=ye, **{f"c{i}_year": c[f"c{i}"] for i in range(1, 5)})
        row = {"family": "Y", "team": "y", "team_name": f"{t}年", "season": t, "month": 0,
               "yE": ye, "ayE": abs(ye) / SIGMA_YEAR, "e0": c["e0"], "s_rice": c["s_rice"], "s_cereals": c["s_cereals"],
               "q": c["q"]}
        for i in range(1, 8):
            v = c[f"c{i}"]
            row[f"c{i}"], row[f"acy{i}"], row[f"u{i}"] = v, c[f"acy{i}"], (ye - v if v is not None else None)
        row["qf"] = c["qf"]
        if c["qf"] is not None:
            watch(k_of(t, 1), qf_year=c["qf"])            # FAO の熱量が前の年と同じならゼロ（値は変えずに記録）
        # 第5弾 §4 の診断（判定に使わない）: 段 5 の残り yE − c5 = (家計調査の実質の食料の伸び) − (家計調査と国全体の実質の消費の伸びの差)。恒等式
        h0, h1 = hy[t - 1], hy[t]
        rel_f, rel_a = d["cpi_year"]["food"][t] / d["cpi_year"]["food"][t - 1], d["cpi_year"]["all_items"][t] / d["cpi_year"]["all_items"][t - 1]
        row["qF_hh"] = math.log(h1["food_yen_month"] / h0["food_yen_month"]) - math.log(rel_f)
        row["qC_hh"] = math.log(h1["ce_yen_month"] / h0["ce_yen_month"]) - math.log(rel_a)
        row["gap"] = row["qC_hh"] - c["q"] if c["q"] is not None else None
        for i in (4, 5, 6, 7):                          # 第4弾: 見込みの向きと E の向きが同じか（上げ・下げをまとめた形）
            v = c[f"c{i}"]
            row[f"agree{i}"] = ((v > 0) == (ye > 0)) if v is not None else None
        if c["c5"] is None:
            watch(k_of(t, 1), q_year=None)                 # 量の段が作れない年（国民経済計算の値がまだない）を記録する
            row["l5"] = row["l6"] = None
        else:                                           # 段 5 は段 4 より、段 6 は段 5 より残りが小さいか
            row["l5"] = abs(row["u5"]) < abs(row["u4"])
            row["l6"] = abs(row["u6"]) < abs(row["u5"])
        out.append(row)
    return out


# ---------- 件数（宣言 §4。条件の側だけ）----------

def count(d: dict) -> dict:
    a = a_conditions(d)
    res = {"A": {}, "B": {}}
    for label, last in (("incl2025", 2025), ("excl2025", 2024)):
        aa = [r for r in a if ym(r["k"])[0] <= last]
        res["A"][label] = {"units": len(aa), "say(ax>=1)": sum(r["ax"] >= 1 for r in aa),
                           "band(ax<1)": sum(r["ax"] < 1 for r in aa),
                           "say(axs>=1)": sum(r["axs"] >= 1 for r in aa), "band(axs<1)": sum(r["axs"] < 1 for r in aa)}
        bb = [r for r in b_conditions(d) if ym(r["k"])[0] <= last]
        res["B"][label] = {"units": len(bb)}
        for i in range(1, 5):
            res["B"][label][f"step{i}"] = {
                "up(c>=tau)": sum(r[f"c{i}"] >= r["tau"] for r in bb),
                "down(c<=-tau)": sum(r[f"c{i}"] <= -r["tau"] for r in bb),
                "band": sum(abs(r[f"c{i}"]) < r["tau"] for r in bb),
                "up(c>=sigma)": sum(r[f"c{i}"] >= SIGMA for r in bb),
                "down(c<=-sigma)": sum(r[f"c{i}"] <= -SIGMA for r in bb),
                "band_sigma": sum(abs(r[f"c{i}"]) < SIGMA for r in bb)}
    res["sigma"] = SIGMA
    # 第3弾（宣言 r3 §5）。族 A は x の替わり（米・穀類の寄与）の言い切る月、族 Y は年の帯の件数
    for label, last in (("incl2025", 2025), ("excl2025", 2024)):
        aa = [r for r in a if ym(r["k"])[0] <= last]
        res["A"][label] |= {f"say(ax{j}>=1)": sum(r[f"ax{j}"] >= 1 for r in aa) for j in ("r", "c")}
        yy = [r for r in y_conditions(d) if r["k"] <= last]
        res.setdefault("Y", {})[label] = {"units": len(yy)} | {
            f"step{i}": {"up(c>=sigmaY)": sum(r[f"c{i}"] >= SIGMA_YEAR for r in yy),
                         "down(c<=-sigmaY)": sum(r[f"c{i}"] <= -SIGMA_YEAR for r in yy),
                         "band": sum(abs(r[f"c{i}"]) < SIGMA_YEAR for r in yy)} for i in range(1, 5)}
    res["sigma_year"] = SIGMA_YEAR
    # 第4弾（宣言 r4 §4）。量の段は国民経済計算の値がそろう 2001〜2024 年だけ
    yy = [r for r in y_conditions(d) if r["c5"] is not None and r["k"] <= 2024]   # 宣言 r4 の範囲（2025 年は第5弾）
    res["Y"]["quantity"] = {"units": len(yy), "years": [yy[0]["k"], yy[-1]["k"]], "eta_food": d["eta_food"]} | {
        f"step{i}": {"up(c>=sigmaY)": sum(r[f"c{i}"] >= SIGMA_YEAR for r in yy),
                     "down(c<=-sigmaY)": sum(r[f"c{i}"] <= -SIGMA_YEAR for r in yy),
                     "band": sum(abs(r[f"c{i}"]) < SIGMA_YEAR for r in yy)} for i in (4, 5, 6)}
    y7 = [r for r in y_conditions(d) if r["c7"] is not None]   # 第5弾 §3: FAO の熱量がそろう年
    res["Y"]["food_kcal"] = {"units": len(y7), "years": [y7[0]["k"], y7[-1]["k"]]} | {
        f"step{i}": {"up(c>=sigmaY)": sum(r[f"c{i}"] >= SIGMA_YEAR for r in y7),
                     "down(c<=-sigmaY)": sum(r[f"c{i}"] <= -SIGMA_YEAR for r in y7),
                     "band": sum(abs(r[f"c{i}"]) < SIGMA_YEAR for r in y7)} for i in (5, 7)}
    return res


# ---------- 判定（PythDRagoras の仕組みで）----------

def judge(d: dict, outdir: Path = OUT) -> list[dict]:
    sys.path.insert(0, str(ROOT / "pythdragoras"))
    import polars as pl
    import propositions as pr

    units = a_units(d) + b_units(d) + y_units(d)
    outdir.mkdir(parents=True, exist_ok=True)
    upath = outdir / "units.jsonl"
    upath.write_text("".join(json.dumps(u, ensure_ascii=False) + "\n" for u in units), encoding="utf-8")
    st = pl.DataFrame(units, infer_schema_length=None)
    with tempfile.TemporaryDirectory() as tmp:          # 事前登録のファイルを順につないで 1 つとして読む（parent と同じ問いの検査を全体で）
        joined = Path(tmp) / "propositions.toml"
        joined.write_text("\n".join(p.read_text(encoding="utf-8") for p in PROPS), encoding="utf-8")
        props, sha = pr.load(joined)
    ver = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    meta = {"sha256": sha, "code_version": ver.stdout.strip() or None,
            "file": " + ".join(str(p.relative_to(ROOT)) for p in PROPS)}
    results = [{**pr.evaluate(p, st), "meta": meta} for p in props]
    data_sha = hashlib.sha256(upath.read_bytes()).hexdigest()
    ledger = pr.update_ledger(outdir / "ledger.jsonl", results, data_sha, meta["code_version"])
    for r in results:
        r["judgement"] = pr.judge(r, pr.ledger_summary(ledger, r["id"])["definitions"])
    (outdir / "propositions.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in results), encoding="utf-8")
    (outdir / "objections.md").write_text(pr.render(results, meta, ledger=ledger), encoding="utf-8")
    (outdir / "index.md").write_text(pr.render_index(results, meta), encoding="utf-8")
    (outdir / "zero_nan_log.txt").write_text("\n".join(LOG) + ("\n" if LOG else "（なし）\n"), encoding="utf-8")
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="サイクル2 月次の命題（族 A・族 B）")
    ap.add_argument("mode", choices=("count", "judge"),
                    help="count: 条件の側の件数だけ（結論は計算しない） / judge: 単位を作って判定し outputs/ に書く")
    a = ap.parse_args(argv)
    d = load()
    if a.mode == "count":
        print(json.dumps(count(d), ensure_ascii=False, indent=1))
        return 0
    res = judge(d)
    for r in res:
        j = r["judgement"]
        print(f"{r['id']:8s} code={j['code']} {r['statement']}")
    print(f"ゼロ・NaN のログ: {len(LOG)} 件（outputs/zero_nan_log.txt）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
