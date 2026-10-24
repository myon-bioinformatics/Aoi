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


res = json.load(open(HERE / "lag_results.json"))
bad = 0
for name, ws in (("extended", 2005), ("legacy", 2015)):
    rows = run(ws, dE0)
    for ex, key in ((False, "incl2025"), (True, "excl2025")):
        n, w0, wd = counts(rows, ex)
        t = res[name]["tests"][key]
        ok = (n, w0, wd) == (t["lag"]["n"], t["lag"]["w0"], t["lag"]["wd"])
        ok &= abs(sign_p(w0, n) - t["p_sign0"]) < 1e-12 and abs(sign_p(wd, n) - t["p_signd"]) < 1e-12
        # 順列: 別の乱数器で検算（一致は要求せず、モンテカルロ誤差内か見る）
        rnd = random.Random(1)
        keys = list(range(ws + 1, 2026))
        vals = [dE0[k] for k in keys]
        c0 = cd = 0
        B = 4000
        for _ in range(B):
            v = vals[:]
            rnd.shuffle(v)
            r = run(ws, dict(zip(keys, v)))
            _, a, b = counts(r, ex)
            c0 += a >= w0
            cd += b >= wd
        p0, pd = c0 / B, cd / B
        near = abs(p0 - t["p_perm0"]) < 0.03 and abs(pd - t["p_permd"]) < 0.03
        print(f"{name:8s} {key}: n={n} w0={w0} wd={wd} counts/sign={'OK' if ok else 'NG'} | "
              f"perm(alt RNG) p0={p0:.3f} (main {t['p_perm0']:.3f}) pd={pd:.3f} (main {t['p_permd']:.3f}) {'OK' if near else 'NG'}")
        bad += (not ok) + (not near)

h = hashlib.sha256(open(HERE / "lag_prelock_2026-10-24.md", "rb").read()).hexdigest()
print("prelock sha256:", h)
print("stamp file    :", open(HERE / "lag_prelock_timestamp.txt").read().strip().replace("\n", " | "))
print("VERIFY:", "ALL OK" if bad == 0 else f"{bad} NG")
