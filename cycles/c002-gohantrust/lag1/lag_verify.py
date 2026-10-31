#!/usr/bin/env python3
"""lag_run.py とは別実装（標準ライブラリのみ・手書きループ）で遅れ版を再計算し、結果 JSON と照合する。"""
import hashlib
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

P = [(2005, 2224.2), (2006, 2138.7), (2007, 2104.0), (2008, 2078.3), (2009, 2090.4),
     (2010, 1996.7), (2011, 1896.3), (2012, 2082.7), (2013, 2157.5), (2014, 2006.5),
     (2015, 1833.1), (2016, 1913), (2017, 2033), (2018, 2158), (2019, 2151), (2020, 2163),
     (2021, 2097), (2022, 1996), (2023, 2069.1), (2024, 2686.9), (2025, 4599.7)]
E = [(2005, .229), (2006, .231), (2007, .230), (2008, .232), (2009, .234), (2010, .233),
     (2011, .236), (2012, .235), (2013, .236), (2014, .240), (2015, .250), (2016, .258),
     (2017, .257), (2018, .257), (2019, .257), (2020, .275), (2021, .272), (2022, .266),
     (2023, .278), (2024, .283), (2025, .286)]
yrs = [a for a, _ in P]
y = {yrs[i]: math.log(P[i][1] / P[i - 1][1]) for i in range(1, len(P))}
dE0 = {E[i][0]: math.log(E[i][1] / E[i - 1][1]) for i in range(1, len(E))}


def run(ws, dE):
    """lag=1。訓練ペア s=ws+2..t-1、最初のテスト年は ws+2+5。"""
    rows = {}
    for t in range(ws + 7, 2026):
        sxy = sxx = 0.0
        ys = []
        for s in range(ws + 2, t):
            sxy += dE[s - 1] * y[s]
            sxx += dE[s - 1] ** 2
            ys.append(y[s])
        g = sxy / sxx
        yh = g * dE[t - 1]
        dr = sum(ys) / len(ys)
        rows[t] = (abs(y[t] - yh) < abs(y[t]), abs(y[t] - yh) < abs(y[t] - dr), g)
    return rows


def counts(rows, ex):
    ts = [t for t in rows if not (ex and t == 2025)]
    return len(ts), sum(rows[t][0] for t in ts), sum(rows[t][1] for t in ts)


def sign_p(k, n):
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


class Reads(dict):
    """run() が読んだ ΔlogE の年を覚える。順列の母集団を、式ではなく実際の読み取りから決める。"""

    def __init__(self, *args):
        super().__init__(*args)
        self.read = set()

    def __getitem__(self, key):
        self.read.add(key)
        return super().__getitem__(key)


def used_keys(ws):
    rec = Reads(dE0)
    run(ws, rec)
    return sorted(rec.read)


B = 4000


def perm_p(ws, keys, obs):
    """別の乱数器（random.Random(1)）で、keys の年の ΔlogE をシャッフルして順列 p を数える。
    obs = {(ex, i): 観測の勝ち数}（i=0: 基準 A=ゼロ変化、i=1: 基準 B=ドリフト）。"""
    rnd = random.Random(1)
    vals = [dE0[k] for k in keys]
    cnt = {k: 0 for k in obs}
    for _ in range(B):
        v = vals[:]
        rnd.shuffle(v)
        r = run(ws, dict(zip(keys, v)))
        for (ex, i) in obs:
            cnt[(ex, i)] += counts(r, ex)[1 + i] >= obs[(ex, i)]
    return {k: cnt[k] / B for k in cnt}


res = json.load(open(HERE / "lag_results.json"))
bad = 0
for name, ws in (("extended", 2005), ("legacy", 2015)):
    rows = run(ws, dE0)
    obs = {(ex, i): counts(rows, ex)[1 + i] for ex in (False, True) for i in (0, 1)}
    # 順列の契約: 統計が読む年だけをシャッフルする。最終年（2025）は lag=1 では読まれない
    used, declared = used_keys(ws), list(range(ws + 1, 2026))
    contract = (2025 not in used) and set(declared) - set(used) == {2025}
    contract &= res[name]["perm_scope"]["years_used"] == used and res[name]["perm_scope"]["years_declared"] == declared
    print(f"{name:8s} perm years read by the statistic: {used[0]}-{used[-1]} ({len(used)} yrs), "
          f"2025 read: {2025 in used}, results.json agrees: {'OK' if contract else 'NG'}")
    bad += not contract
    pu = perm_p(ws, used, obs)           # 主: 読まれる年だけ
    pdc = perm_p(ws, declared, obs)      # 宣言 §7.2 の文面どおり（窓内の全年）
    for ex, key in ((False, "incl2025"), (True, "excl2025")):
        n, w0, wd = counts(rows, ex)
        t = res[name]["tests"][key]
        ok = (n, w0, wd) == (t["lag"]["n"], t["lag"]["w0"], t["lag"]["wd"])
        ok &= abs(sign_p(w0, n) - t["p_sign0"]) < 1e-12 and abs(sign_p(wd, n) - t["p_signd"]) < 1e-12
        # 順列: 別の乱数器で検算（一致は要求せず、モンテカルロ誤差内か見る）
        near = abs(pu[(ex, 0)] - t["p_perm0"]) < 0.03 and abs(pu[(ex, 1)] - t["p_permd"]) < 0.03
        near_d = (abs(pdc[(ex, 0)] - t["p_perm0_declared"]) < 0.03
                  and abs(pdc[(ex, 1)] - t["p_permd_declared"]) < 0.03)
        print(f"{name:8s} {key}: n={n} w0={w0} wd={wd} counts/sign={'OK' if ok else 'NG'} | "
              f"perm used (alt RNG) p0={pu[(ex, 0)]:.3f} (main {t['p_perm0']:.3f}) "
              f"pd={pu[(ex, 1)]:.3f} (main {t['p_permd']:.3f}) {'OK' if near else 'NG'} | "
              f"declared p0={pdc[(ex, 0)]:.3f} (main {t['p_perm0_declared']:.3f}) "
              f"pd={pdc[(ex, 1)]:.3f} (main {t['p_permd_declared']:.3f}) {'OK' if near_d else 'NG'}")
        bad += (not ok) + (not near) + (not near_d)

h = hashlib.sha256(open(HERE / "lag_prelock_2026-10-24.md", "rb").read()).hexdigest()
print("prelock sha256:", h)
print("stamp file    :", open(HERE / "lag_prelock_timestamp.txt").read().strip().replace("\n", " | "))
print("VERIFY:", "ALL OK" if bad == 0 else f"{bad} NG")
