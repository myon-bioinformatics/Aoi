#!/usr/bin/env python3
"""サイクル2 月次の命題（族 A: 予測のはしご、族 B: 恒等式の言い切り）。事前宣言: monthly_prelock_2026-11-13.md

  uv run --locked python -I cycles/c002-gohantrust/monthly/monthly_run.py count   # 条件の側の件数だけ（結論は計算しない）
  uv run --locked python -I cycles/c002-gohantrust/monthly/monthly_run.py judge   # 単位を作り、命題を判定して outputs/ に書く

単位は 1 か月。列 team は暦の月（m01〜m12）、season は年、family は族（A / B）。
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
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "research" / "staple-price-survey" / "phase2_archive"
RICE = ARCHIVE / "japan_retail_price_rice_panel.csv.gz"      # 小売物価統計調査 うるち米 銘柄 1002 都市平均（円/5kg）
ENGEL = ARCHIVE / "engel_food_panel_monthly.csv.gz"           # 家計調査 用途分類 二人以上 全国（円/月）
CPI = ARCHIVE / "japan_cpi_food_cereals_panel.csv.gz"         # 消費者物価指数 2025 年基準 全国（総合・食料・穀類）
PROPS = HERE / "monthly_propositions.toml"
OUT = HERE / "outputs"

# 宣言 §2・§3 の範囲（月は 12·年 + 月 − 1 の整数で持つ）
A_FIRST, A_LAST = 2006 * 12 + 1, 2025 * 12 + 11   # 族 A の目標月 2006-02 〜 2025-12
A_TRAIN0 = 2001 * 12 + 1                          # 族 A の訓練の最初の目標月 2001-02（x が E の 2000-01 から作れる最初）
A_MIN_TRAIN = 60
B_FIRST, B_LAST = 2001 * 12 + 0, 2025 * 12 + 11   # 族 B の月 2001-01 〜 2025-12
TICK = 0.001                                      # E の公表刻み（0.1 ポイント）

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
    with gzip.open(CPI, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["frequency"] == "monthly" and r["series_id"] in cpi:
                cpi[r["series_id"]][k_of(int(r["year"]), int(r["month"]))] = float(r["index_value"])
    return {"P": rice, "hh": hh, "cpi": cpi}


def engel(d: dict, k: int) -> float:
    h = d["hh"][k]
    return h["food_yen_month"] / h["ce_yen_month"]


# ---------- 族 A: 予測のはしご（宣言 §2）----------

def a_conditions(d: dict) -> list[dict]:
    """族 A の条件の側だけ（x と刻み）。結論（翌月の米価の変化）は計算しない。"""
    rows = []
    for t in range(A_FIRST, A_LAST + 1):
        e1 = engel(d, t - 1)
        x = math.log(e1 / engel(d, t - 13))
        tau = TICK / e1
        rows.append({"k": t, "x": x, "tau": tau, "ax": abs(x) / tau})
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
        watch(t, y=y, m=m, x=x)
        yy, mm = ym(t)
        out.append({
            "family": "A", "team": f"m{mm:02d}", "team_name": f"{yy}年{mm}月", "season": yy, "month": mm,
            "y": y, "m_prev": m, "x": x, "tau": c["tau"], "ax": c["ax"],
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
            row[f"c{i}"], row[f"ac{i}"] = c[f"c{i}"], c[f"ac{i}"]
            row[f"u{i}"] = ye - c[f"c{i}"]
            row[f"l{i}"] = u[i] < u[i - 1]          # 段 i の残りが段 i−1 より小さい
        row["u0"] = ye
        out.append(row)
    return out


# ---------- 件数（宣言 §4。条件の側だけ）----------

def count(d: dict) -> dict:
    a = a_conditions(d)
    res = {"A": {}, "B": {}}
    for label, last in (("incl2025", 2025), ("excl2025", 2024)):
        aa = [r for r in a if ym(r["k"])[0] <= last]
        res["A"][label] = {"units": len(aa), "say(ax>=1)": sum(r["ax"] >= 1 for r in aa),
                           "band(ax<1)": sum(r["ax"] < 1 for r in aa)}
        bb = [r for r in b_conditions(d) if ym(r["k"])[0] <= last]
        res["B"][label] = {"units": len(bb)}
        for i in range(1, 5):
            res["B"][label][f"step{i}"] = {
                "up(c>=tau)": sum(r[f"c{i}"] >= r["tau"] for r in bb),
                "down(c<=-tau)": sum(r[f"c{i}"] <= -r["tau"] for r in bb),
                "band": sum(abs(r[f"c{i}"]) < r["tau"] for r in bb)}
    return res


# ---------- 判定（PythDRagoras の仕組みで）----------

def judge(d: dict, outdir: Path = OUT) -> list[dict]:
    sys.path.insert(0, str(ROOT / "pythdragoras"))
    import polars as pl
    import propositions as pr

    units = a_units(d) + b_units(d)
    outdir.mkdir(parents=True, exist_ok=True)
    upath = outdir / "units.jsonl"
    upath.write_text("".join(json.dumps(u, ensure_ascii=False) + "\n" for u in units), encoding="utf-8")
    st = pl.DataFrame(units, infer_schema_length=None)
    props, sha = pr.load(PROPS)
    ver = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    meta = {"sha256": sha, "code_version": ver.stdout.strip() or None, "file": str(PROPS.relative_to(ROOT))}
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
