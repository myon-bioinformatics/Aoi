#!/usr/bin/env python3
"""遅れ版（ΔlogE_{t-1}）ローリング検証。事前宣言: lag_prelock_2026-10-24.md

使い方:
  python3 lag_run.py gate   # 同年版で Grok の結果を再現できるか確認（再現ゲート）
  python3 lag_run.py lag    # ゲートを通った場合のみ、遅れ版を実行
  python3 lag_run.py lag --inputs estat   # L1r: 入力を一次資料の値に差し替えて再走（lag_reverify_prelock_2026-11-13.md）
"""
import argparse
import csv
import gzip
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent  # 出力はこのスクリプトの隣に書く（実行場所に依らない）

# Grok 報告書から転記（P_yen, E）。2016–2022 の P は整数丸め。既定の入力（L1）。
P = {2005: 2224.2, 2006: 2138.7, 2007: 2104.0, 2008: 2078.3, 2009: 2090.4,
     2010: 1996.7, 2011: 1896.3, 2012: 2082.7, 2013: 2157.5, 2014: 2006.5,
     2015: 1833.1, 2016: 1913, 2017: 2033, 2018: 2158, 2019: 2151, 2020: 2163,
     2021: 2097, 2022: 1996, 2023: 2069.1, 2024: 2686.9, 2025: 4599.7}
E = {2005: 0.229, 2006: 0.231, 2007: 0.230, 2008: 0.232, 2009: 0.234,
     2010: 0.233, 2011: 0.236, 2012: 0.235, 2013: 0.236, 2014: 0.240,
     2015: 0.250, 2016: 0.258, 2017: 0.257, 2018: 0.257, 2019: 0.257,
     2020: 0.275, 2021: 0.272, 2022: 0.266, 2023: 0.278, 2024: 0.283,
     2025: 0.286}
P_TRANSCRIBED, E_TRANSCRIBED = dict(P), dict(E)
LAST = 2025
MIN_TRAIN = 5
B = 2000
SEED = 20261024

# L1r（入力差し替え）の一次資料。宣言 §1
ARCHIVE = HERE.parents[2] / "research" / "staple-price-survey" / "phase2_archive"
RICE_PANEL = ARCHIVE / "japan_retail_price_rice_panel.csv.gz"
ENGEL_PANEL = ARCHIVE / "engel_food_panel_annual.csv"
INPUTS = ("transcribed", "estat", "estat_p", "estat_e")   # estat_p / estat_e は分解（宣言 §4）用


def logdiff(d):
    return {t: math.log(d[t] / d[t - 1]) for t in sorted(d) if t - 1 in d}


Y = logdiff(P)
DE = logdiff(E)


def estat_inputs():
    """一次資料から P と E を作る（L1r 宣言 §1）。
    P: 小売物価統計調査うるち米 銘柄 1002 都市平均（円/5kg）の、暦年 12 か月の単純平均。
    E: 家計調査 用途分類 二人以上 全国の 食料 ÷ 消費支出（年平均 1 か月、丸めない）。"""
    months = {}
    with gzip.open(RICE_PANEL, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["variable"] == "japan_rps_uruchi_rice_mean_city_yen_per_5kg" and r["item_code"] == "1002":
                months.setdefault(int(r["year"]), {})[int(r["month"])] = float(r["value"])
    food_ce = {}
    with open(ENGEL_PANEL, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            food_ce[int(r["year"])] = (float(r["food_yen_month"]), float(r["ce_yen_month"]))
    p, e = {}, {}
    for t in P_TRANSCRIBED:
        m = months.get(t, {})
        if sorted(m) != list(range(1, 13)):     # 12 か月そろわない年は作らない（宣言 §1）
            raise ValueError(f"P_{t}: 月次が 12 か月そろわない（{sorted(m)}）")
        p[t] = math.fsum(m[k] for k in range(1, 13)) / 12   # 版によらず同じ値（3.12 から sum の足し方が変わった）
        food, ce = food_ce[t]
        e[t] = food / ce
    return p, e


def set_inputs(name):
    """P・E と、そこから作る Y・DE を差し替える。既定は "transcribed"（L1 の転記値）。"""
    global P, E, Y, DE
    if name not in INPUTS:
        raise ValueError(name)
    p_src, e_src = (estat_inputs() if name != "transcribed" else (None, None))
    P = dict(p_src if name in ("estat", "estat_p") else P_TRANSCRIBED)
    E = dict(e_src if name in ("estat", "estat_e") else E_TRANSCRIBED)
    Y, DE = logdiff(P), logdiff(E)


def rolling(win_start, lag, dE=None):
    """原点通過 OLS で γ を訓練期間のペア (dE[s-lag], y_s) から推定し、t を予測する。"""
    dE = DE if dE is None else dE
    first_s = win_start + 1 + lag
    out = []
    for t in range(first_s + MIN_TRAIN, LAST + 1):
        tr = list(range(first_s, t))
        x = np.array([dE[s - lag] for s in tr])
        y = np.array([Y[s] for s in tr])
        den = float((x * x).sum())
        if den == 0.0:      # 訓練年の ΔlogE がすべて 0。numpy は警告だけで nan を返し、その年が「負け」に数えられてしまう。値は置き換えず、理由を書いて止める
            raise ValueError(f"分母ゼロ: 訓練年の ΔlogE がすべて 0 で γ が決まらない（win_start={win_start}, lag={lag}, t={t}）")
        g = float((x * y).sum()) / den
        yh = g * dE[t - lag]
        drift = float(y.mean())
        yt = Y[t]
        e_m, e0, ed = abs(yt - yh), abs(yt), abs(yt - drift)
        out.append(dict(t=t, gamma=g, yhat=yh, y=yt, drift=drift,
                        win0=bool(e_m < e0), wind=bool(e_m < ed),
                        sign_ok=bool(yt != 0 and yh != 0),
                        signmatch=bool(np.sign(yt) == np.sign(yh)),
                        m0=e0 - e_m, md=ed - e_m))
    return out


class _Reads(dict):
    """ΔlogE を読んだ年を覚える辞書。検定の母集団を「統計が実際に読む年」から導くために使う。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read = set()

    def __getitem__(self, key):
        self.read.add(key)
        return super().__getitem__(key)


def used_years(win_start, lag):
    """rolling(win_start, lag) が実際に読む ΔlogE の年（参照 index 集合）。式から手で書かず、読んだ年を数える。"""
    rec = _Reads(DE)
    rolling(win_start, lag, dE=rec)
    return sorted(rec.read)


def summarize(res, excl2025):
    r = [x for x in res if not (excl2025 and x["t"] == LAST)]
    sm = [x for x in r if x["sign_ok"]]
    return dict(n=len(r), w0=sum(x["win0"] for x in r), wd=sum(x["wind"] for x in r),
                sm_n=len(sm), sm=sum(x["signmatch"] for x in sm),
                mean_m0=float(np.mean([x["m0"] for x in r])) if r else None,
                mean_md=float(np.mean([x["md"] for x in r])) if r else None)


def sign_p(k, n):
    """片側符号検定 P(X >= k), X ~ Bin(n, 0.5)"""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def perm_keys(win_start, lag, scope):
    """順列でシャッフルする年。
    "declared": 宣言 §7.2 の文面どおり、窓内で ΔlogE が定義される全年（win_start+1..LAST）。
    "used": 統計が実際に読む年だけ。lag=0 では declared と同じ集合、lag=1 では最終年 LAST を含まない。"""
    if scope == "declared":
        return list(range(win_start + 1, LAST + 1))
    if scope == "used":
        return used_years(win_start, lag)
    raise ValueError(scope)


def perm_test(win_start, lag, scope="used"):
    rng = np.random.default_rng(SEED)
    keys = perm_keys(win_start, lag, scope)
    vals = np.array([DE[k] for k in keys])
    obs = rolling(win_start, lag)
    o = {(ex, base): summarize(obs, ex)[base] for ex in (False, True) for base in ("w0", "wd")}
    cnt = {k: 0 for k in o}
    for _ in range(B):
        d = dict(zip(keys, rng.permutation(vals)))
        res = rolling(win_start, lag, dE=d)
        for (ex, base) in o:
            if summarize(res, ex)[base] >= o[(ex, base)]:
                cnt[(ex, base)] += 1
    return {k: cnt[k] / B for k in cnt}


def corr(win_start):
    ts = range(win_start + 2, LAST + 1)  # 両方の ΔlogE が窓内で定義される年
    y = np.array([Y[t] for t in ts])
    c0 = float(np.corrcoef([DE[t] for t in ts], y)[0, 1])
    c1 = float(np.corrcoef([DE[t - 1] for t in ts], y)[0, 1])
    return dict(n=len(list(ts)), r_same=c0, r_lag=c1)


def gate():
    ok, lines = True, []
    leg = rolling(2015, 0)
    ext = rolling(2005, 0)
    sl_i, sl_e = summarize(leg, False), summarize(leg, True)
    se_i, se_e = summarize(ext, False), summarize(ext, True)
    g_exp = {2021: 0.262, 2022: 0.316, 2023: 0.468, 2024: 0.552, 2025: 1.081}
    checks = [
        ("legacy incl w0=5/5", (sl_i["w0"], sl_i["n"]) == (5, 5)),
        ("legacy excl w0=4/4", (sl_e["w0"], sl_e["n"]) == (4, 4)),
        ("legacy incl drift=3/5", (sl_i["wd"], sl_i["n"]) == (3, 5)),
        ("legacy excl drift=3/4", (sl_e["wd"], sl_e["n"]) == (3, 4)),
        ("ext incl w0=6/15", (se_i["w0"], se_i["n"]) == (6, 15)),
        ("ext excl w0=5/14", (se_e["w0"], se_e["n"]) == (5, 14)),
    ]
    for x in leg:
        c = abs(x["gamma"] - g_exp[x["t"]]) <= 0.01
        checks.append((f"legacy gamma {x['t']} {x['gamma']:.3f} vs {g_exp[x['t']]}", c))
    pp = perm_test(2015, 0)
    p_inc, p_exc = pp[(False, "w0")], pp[(True, "w0")]
    checks.append((f"perm p incl {p_inc:.4f} vs 0.0065±0.004", abs(p_inc - 0.0065) <= 0.004))
    checks.append((f"perm p excl {p_exc:.4f} vs 0.021±0.004", abs(p_exc - 0.021) <= 0.004))
    for name, c in checks:
        lines.append(f"{'PASS' if c else 'FAIL'}  {name}")
        ok &= c
    lines.append("GATE: " + ("PASS" if ok else "FAIL"))
    return ok, lines, dict(legacy=leg, ext=ext, perm=pp)


def run_lag():
    out = {}
    for name, ws in (("extended", 2005), ("legacy", 2015)):
        res = rolling(ws, 1)
        same = rolling(ws, 0)
        pp = perm_test(ws, 1)                       # 主: 統計が実際に読む年だけをシャッフル
        pp_decl = perm_test(ws, 1, scope="declared")  # 宣言 §7.2 の文面どおり（窓内の全年）。比較のために残す
        blk = dict(years=[x["t"] for x in res], rows=res, corr=corr(ws), perm=None, tests={})
        for ex in (False, True):
            s = summarize(res, ex)
            sm = summarize(same, ex)
            key = "excl2025" if ex else "incl2025"
            blk["tests"][key] = dict(
                lag=s, same=sm,
                p_sign0=sign_p(s["w0"], s["n"]), p_signd=sign_p(s["wd"], s["n"]),
                p_perm0=pp[(ex, "w0")], p_permd=pp[(ex, "wd")],
                p_perm0_declared=pp_decl[(ex, "w0")], p_permd_declared=pp_decl[(ex, "wd")])
        blk["perm_scope"] = dict(main="used", years_used=perm_keys(ws, 1, "used"),
                                 years_declared=perm_keys(ws, 1, "declared"))
        out[name] = blk
    return out


def reverify_gate():
    """L1r 宣言 §2 のゲート。G1: 既定の入力で、置いてある lag_results.json と L1 の再現ゲートが再現する。
    G2: 差し替え入力が転記値と、P は各年 0.05 % 以内、E は 0.0005 以内で合う。"""
    lines, ok = [], True
    set_inputs("transcribed")
    g_ok, _, _ = gate()
    committed = json.loads((HERE / "lag_results.json").read_text(encoding="utf-8"))
    same = json.loads(json.dumps(run_lag(), default=float)) == committed
    checks = [("G1 L1 replication gate (transcribed inputs)", g_ok),
              ("G1 committed lag_results.json values reproduced", same)]
    p, e = estat_inputs()
    for t in sorted(P_TRANSCRIBED):
        dp, de = abs(p[t] / P_TRANSCRIBED[t] - 1), abs(e[t] - E_TRANSCRIBED[t])
        checks.append((f"G2 {t} P {p[t]:.2f} vs {P_TRANSCRIBED[t]} ({dp:.5%}) E {e[t]:.6f} vs {E_TRANSCRIBED[t]}",
                       dp <= 0.0005 and de <= 0.0005))
    for name, c in checks:
        lines.append(f"{'PASS' if c else 'FAIL'}  {name}")
        ok &= c
    lines.append("L1r GATE: " + ("PASS" if ok else "FAIL"))
    return ok, lines


def run_reverify():
    """L1r: 入力を差し替えて L1 と同じ手順を走らせる（宣言 §3）。分解（§4）と同年版の記録（§2）を添える。
    終わったら既定の入力に戻す。"""
    try:
        set_inputs("estat")
        out = dict(inputs=dict(P=P, E=E), main=run_lag(),
                   same_year_record={name: rolling(ws, 0) for name, ws in (("extended", 2005), ("legacy", 2015))},
                   decomposition={})
        for name in ("estat_p", "estat_e"):
            set_inputs(name)
            rows = rolling(2005, 1)
            out["decomposition"][name] = dict(
                rows=rows, incl2025=summarize(rows, False), excl2025=summarize(rows, True))
        return out
    finally:
        set_inputs("transcribed")


def main(argv=None):
    ap = argparse.ArgumentParser(description="遅れ版（ΔlogE_{t-1}）ローリング検証")
    ap.add_argument("mode", nargs="?", default="gate", choices=("gate", "lag"),
                    help="gate: ゲートだけ / lag: ゲートを通ったら本計算")
    ap.add_argument("--inputs", default="transcribed", choices=("transcribed", "estat"),
                    help="transcribed: L1 の転記値（既定） / estat: L1r の一次資料の値")
    a = ap.parse_args(argv)
    if a.inputs == "estat":
        ok, lines = reverify_gate()
        print("\n".join(lines))
        if a.mode == "lag":
            if not ok:
                print("ゲート不合格のため L1r は実行しない（L1r 宣言 §2）")
                return 2
            res = dict(gate_ok=ok, gate_lines=lines, **run_reverify())
            json.dump(res, open(HERE / "lag_results_estat.json", "w"), indent=1, ensure_ascii=False, default=float)
            print("lag_results_estat.json を書き出した")
        return 0
    ok, lines, detail = gate()
    print("\n".join(lines))
    for x in detail["legacy"]:
        print(f"  legacy same-year t={x['t']} gamma={x['gamma']:.3f} yhat={x['yhat']:+.4f} y={x['y']:+.4f}"
              f" drift={x['drift']:+.4f} win0={x['win0']} wind={x['wind']}")
    json.dump(dict(gate_ok=ok, lines=lines), open(HERE / "gate_result.json", "w"), indent=1, ensure_ascii=False)
    if a.mode == "lag":
        if not ok:
            print("ゲート不合格のため遅れ版は実行しない（事前宣言 §3）")
            return 2
        res = run_lag()
        json.dump(res, open(HERE / "lag_results.json", "w"), indent=1, ensure_ascii=False, default=float)
        print("lag_results.json を書き出した")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
