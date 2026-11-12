"""サイクル3の単位を作る・検算する。

    作る:   python cycles/c003-outlets/outlet_units.py make --ffs <FluidFullSpeedSimulation の場所>
    検算:   python cycles/c003-outlets/outlet_units.py check        （エンジンを使わない素の漸化式）

単位 = 1 回の計算（槽 1 つ・出口の組・刻み・方式）。作るほうは FluidFullSpeedSimulation のエンジン（固定小数点 Q48）で
進め、検算は float の漸化式で同じ err を出し直して比べる。列の意味は README.md。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNITS = HERE / "units.jsonl"
PROVENANCE = HERE / "units_provenance.json"

V0 = 128.0  # 最初の量
TAU = 32.0  # 合計の時定数（K = 1/TAU）
SPAN = 2.0  # 測る時刻 t ≈ SPAN·TAU（ステップ数は round(SPAN/h)）
H_DYADIC = [1 / 128, 1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2]  # h = dt/TAU
H_SEED = 3  # 2 の累乗でない刻み 3 つ（A×10^-N、N = 1〜2）の種
COUNTS = [1, 2, 3, 4, 8, 16]
PUMP_SHARE = 1 / 8  # 混ざる槽・足りているポンプ: q = V0·K·PUMP_SHARE
GENTLE_SHARE, GENTLE_SPAN = 1 / 64, 0.5  # 第2弾 gentle: 弱いポンプを t ≈ τ/2 で測る（厳密な残りが大きい）
CHAIN_RATIOS = [0.25, 0.5, 0.75, 2.0, 4.0]  # 第2弾 chain: 2 段目の時定数 τ2 / τ
CHAIN2_RATIOS, CHAIN2_SPANS = [1 / 3, 1.5, 3.0, 8.0], [1.0, 3.0]  # 第3弾 chain2: 別の τ2 と別の時刻
FED_RATIOS = [0.25, 1.0, 4.0]  # 第3弾 fed: ポンプ（速さ V0/TAU）→ 槽（弁 1 本、τ2）
COMBO_IN, COMBO_OUT = 1 / 4, 1 / 8  # 第4弾 combo: 入るポンプ・出るポンプの速さ（V0·K の何倍か）
CHAIN3_RATIOS = [(0.5, 1 / 3), (2.0, 0.5), (1 / 3, 3.0), (3.0, 5.0)]  # 第4弾 chain3: (τ2/τ, τ3/τ)
RING_RATIOS, RING_SPANS = [0.25, 0.5, 2.0, 4.0], [2.0, 40.0]  # 第4弾 ring: τ2/τ と、測る時刻 / T（T = τ·τ2/(τ + τ2)）
H_FINE = [1 / 256]  # 第5弾で足す刻み
CHAIN3B_PAIRS = [(0.25, 0.75), (0.75, 0.25), (1.5, 4.0), (4.0, 1.5), (0.4, 2.5), (6.0, 0.2)]  # 第5弾 chain3b: (τ2/τ, τ3/τ)
CHAIN3B_SPANS = [1.0, 3.0]
CHAIN4_SETS = [(0.5, 1 / 3, 0.25), (2.0, 0.5, 3.0), (1 / 3, 3.0, 0.5), (3.0, 5.0, 2.0)]  # 第5弾 chain4: (τ2/τ, τ3/τ, τ4/τ)
EDGE3_FLIP = [(1.5, 4.0), (4.0, 1.5), (0.4, 2.5)]  # 第6弾 edge3: end のずれが 0 を横切る時刻のある組
EDGE3_AROUND = [0.8, 0.9, 0.95, 0.98, 1.02, 1.05, 1.1, 1.2]  # 横切る時刻の何倍で測るか
EDGE3_PLAIN, EDGE3_SPANS = [(0.25, 0.75), (6.0, 0.2)], [1.0, 2.0, 3.0]  # 横切らない組と、測る時刻 / τ
EDGE2_RATIOS, EDGE2_SPAN = [0.2, 0.6, 1.25, 5.0], 1.5  # 第6弾 edge2: τ2/τ と、測る時刻 / τ
CROSS3_PAIRS = [(5.0, 2.0), (0.3, 2.0), (3.0, 1.25), (0.5, 3.0), (0.6, 2.5)]  # 第7弾 cross3: (τ2/τ, τ3/τ)
CROSS3_H = [1 / 256, 1 / 128, 1 / 64, 1 / 32, 0.0478, 1 / 16, 1 / 8]  # 粗い刻みは使わない
CROSS3_OFFSETS, CROSS3_FAR = (-2, -1, 0, 1, 2), (0.7, 1.3)  # 0 を横切るステップ n0 からのずれと、n0 の何倍か
CROSS3C_H = [1 / 4, 0.343, 1 / 2, 0.74]  # 第8弾 cross3c: 粗い刻み（組と測り方は cross3 と同じ）
CROSS4_SETS = [(0.3, 2.0, 0.6), (4.0, 1.5, 0.6), (2.5, 0.6, 1.5), (0.6, 5.0, 2.0)]  # 第8弾 cross4: (τ2/τ, τ3/τ, τ4/τ)
VARY_SETS = [((2.0, 0.75), [1.0, 2.0, 3.0]), ((0.4, 1.5), [1.0, 2.0, 3.0]), ((4.0, 0.3), [1.0, 2.0, 3.0]),
             ((1.25, 2.5), [1.0, 2.0, 3.0]), ((0.5, 2.0, 0.75), [1.5, 3.0]), ((3.0, 0.4, 1.5), [1.5, 3.0])]  # 第8弾 vary
VARY_METHODS = ("uniform_in", "cascade", "ramp")  # cascade・ramp は整数の漸化式（エンジンには入れていない）
PIPE_SETS = {  # 第9弾 pipe: 形ごとの組と、測る時刻 / τ
    "branch": ([(0.5, 2.0, 0.75), (0.25, 0.4, 1.5), (0.7, 1.25, 2.5)], [1.0, 2.5]),  # (B へ行く割合, τB/τ, τC/τ)
    "merge": ([(2.0, 0.5, 1.5), (0.4, 3.0, 0.75), (1.5, 0.6, 2.5)], [1.0, 2.5]),  # (τB/τ, τC/τ, τD/τ)
    "pumpfed": ([(2.0, 0.75), (0.4, 1.5), (1.25, 2.5)], [1.0, 2.5]),  # (τB/τ, τC/τ)
    "ring": ([(0.4,), (2.0,), (1.25,)], [0.5, 1.5]),  # (τ2/τ,)
}
CROSS_KINDS = ("cross3", "cross3c", "cross4")  # 式で end のずれが 0 を横切るステップの前後を測る組
LADDER_SETS = [((0.4,), 1.5), ((0.75,), 1.5), ((2.0,), 1.5), ((3.0,), 1.5), ((2.0, 0.75), 2.0), ((0.4, 1.5), 2.0)]  # 第10弾 ladder
LADDER_ORDER = {"end": 1, "uniform_in": 2, "ramp": 3, "quad": 4}  # 入る速さの見なし方と、見込みのずれの次数
OLAD_SHARES = [(1.0,), (0.5, 0.5), (1 / 3, 1 / 3, 1 / 3), (0.2,) * 5, (0.7, 0.3), (0.9, 0.1), (0.5, 0.3, 0.2),
               (0.4, 0.3, 0.2, 0.1)]  # 第11弾 olad: 出口の割合の組
OLAD_SPANS = [1.5, 3.0]  # 測る時刻 / τ（第1弾の 2τ と重ならない）
OLAD_LEVELS = (0, 1, 2, 3)  # 他の出口がステップの中で取る速さを、s の何次まで知っているか（0 は知らない）
ILAD_SETS = [((0.5,), 1.0), ((0.5,), 2.5), ((1.25,), 1.0), ((1.25,), 2.5), ((2.5,), 1.0), ((2.5,), 2.5), ((4.0,), 1.0),
             ((4.0,), 2.5), ((3.0, 0.5), 2.5), ((0.6, 2.5), 2.5), ((0.3, 1.25), 1.5)]  # 第11弾 ilad: 入口のはしごの新しい組
PIPE2_SETS = {  # 第12弾 pipe2: 第9弾と同じ形の、新しい組
    "branch": ([(0.6, 3.0, 0.5), (0.35, 0.6, 2.5), (0.45, 1.5, 0.4)], [1.0, 2.5]),
    "merge": ([(0.5, 3.0, 0.4), (2.5, 0.6, 1.5), (3.0, 1.25, 0.5)], [1.0, 2.5]),
    "pumpfed": ([(3.0, 0.5), (0.6, 2.5), (1.5, 0.4)], [1.0, 2.5]),
    "ring": ([(0.6,), (3.0,), (1.5,)], [0.5, 1.5]),
}
PIPE_KINDS = ("pipe", "pipe2")
COARSE2_X = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]  # 第12弾 coarse2: x = dt/τ1
COARSE2_Y = [0.4, 0.9, 1.8, 2.7, 3.6, 5.5, 7.0, 11.0]  # y = dt/τ2
COARSE2_STEPS = 6
TLAD_RATIOS, TLAD_SPANS = [0.6, 1.5, 3.0], [1.0, 2.0]  # 第12弾 tlad: 2 段の τ2/τ と、測る時刻 / τ
TLAD_ORDER = {"tay1": 2, "tay2": 3, "tay3": 4, "uniform_in": 2, "ramp": 3, "quad": 4}  # tay は「最初の値だけを知る」入れ方
TOTAL_COEF = {1: 1.0 / 12.0, 2: 1.0 / 72.0, 3: 1.0 / 720.0}  # 合計も知る入れ方の、2 段目のずれの係数
VARIANT_METHODS = ("cascade", "ramp", "quad", "tay1", "tay2", "tay3")  # 整数の漸化式で進める入れ方（エンジンには入れていない）
CHAIN_KINDS = ("chain3b", "chain4", "edge3", "edge2", *CROSS_KINDS, "vary", "ladder", "ilad", "coarse2", "tlad")  # 1 列につながった槽（stages に τ_i/τ）
FLOW_KINDS = ("flow", "combo", "chain3", "ring", *CHAIN_KINDS, *PIPE_KINDS, "olad")  # エンジンの inflows（end・uniform_in）で進める組
DELAY = TAU / 4
EPS = 1e-15  # 割る数が 0 のときに置く値（置いたら log に残す）
TOL_CHECK = 1e-9  # 検算で許す err の差


def skew_shares(n: int) -> list[float]:
    """等分でない割合（種は本数で固定）。"""
    rng = random.Random(1000 + n)
    w = [rng.uniform(0.05, 1.0) for _ in range(n)]
    return [x / sum(w) for x in w]


def plan(h_extra: list[float]) -> list[dict]:
    """作る単位の一覧（計算の前に決まる部分）。"""
    hs = H_DYADIC + h_extra
    out = []

    def add(kind, split, n, method, h, **more):
        shares = [1.0 / n] * n if split == "eq" else skew_shares(n)
        out.append({"kind": kind, "split": split, "n": n, "method": method, "h": h, "shares": shares, **more})

    for method in ("independent", "joint"):
        for n in COUNTS:
            for split in ("eq", "skew"):
                if n == 1 and split == "skew":
                    continue
                for h in hs:
                    add("valve", split, n, method, h)
        for n in (1, 2, 4):
            for h in (1 / 32, 1 / 8):
                add("delay", "eq", n, method, h)
    for method in ("independent", "joint", "affine"):
        for n in (1, 2, 4):
            for h in hs:
                add("mixed", "eq", n, method, h)
    for n in (1, 2, 4, 8):
        for h in (1 / 32, 1 / 8):
            for starved in (False, True):
                add("pump", "eq", n, "independent", h, starved=starved)
    for method in ("independent", "joint", "affine"):  # 第2弾
        for n in (1, 2, 4):
            for h in hs:
                add("gentle", "eq", n, method, h)
    for ratio in CHAIN_RATIOS:
        for h in hs:
            add("chain", "eq", 1, "independent", h, tau2_ratio=ratio)
    for h in hs:  # 第3弾
        for n in (2, 3, 4, 8, 16):
            for split in ("eq", "skew"):
                add("native", split, n, "exact", h, base="valve")
        for base_kind in ("mixed", "gentle"):
            for n in (1, 2, 4):
                add("native", "eq", n, "exact", h, base=base_kind)
    for method in ("independent", "uniform", "through"):
        for ratio in CHAIN2_RATIOS:
            for sp in CHAIN2_SPANS:
                for h in hs:
                    add("chain2", "eq", 1, method, h, tau2_ratio=ratio, span_ratio=sp)
    for method in ("independent", "uniform"):
        for ratio in FED_RATIOS:
            for h in hs:
                add("fed", "eq", 1, method, h, tau2_ratio=ratio)
    for h in hs:  # 第4弾
        for ratio in FED_RATIOS:
            add("flow", "eq", 1, "uniform_in", h, base="fed", tau2_ratio=ratio)
        for ratio in CHAIN2_RATIOS:
            for sp in CHAIN2_SPANS:
                add("flow", "eq", 1, "uniform_in", h, base="chain2", tau2_ratio=ratio, span_ratio=sp)
    for method in ("end", "uniform_in"):
        for h in hs:
            for n in (1, 2, 4):
                for split in ("eq", "skew"):
                    if n > 1 or split == "eq":
                        add("combo", split, n, method, h)
            for r2, r3 in CHAIN3_RATIOS:
                add("chain3", "eq", 1, method, h, tau2_ratio=r2, tau3_ratio=r3)
            for ratio in RING_RATIOS:
                for sp in RING_SPANS:
                    add("ring", "eq", 1, method, h, tau2_ratio=ratio, span_ratio=sp)
    for h in hs + H_FINE:  # 第5弾
        for method in ("end", "uniform_in"):
            for r2, r3 in CHAIN3B_PAIRS:
                for sp in CHAIN3B_SPANS:
                    add("chain3b", "eq", 1, method, h, stages=[r2, r3], tau2_ratio=r2, tau3_ratio=r3, span_ratio=sp)
        for r2, r3, r4 in CHAIN4_SETS:
            add("chain4", "eq", 1, "end", h, stages=[r2, r3, r4], tau2_ratio=r2, tau3_ratio=r3, tau4_ratio=r4)
    for h in hs + H_FINE:  # 第6弾
        for method in ("end", "uniform_in"):
            for pair, spans in [(pr, [round(flip_time(pr) * a, 6) for a in EDGE3_AROUND]) for pr in EDGE3_FLIP] + \
                    [(pr, EDGE3_SPANS) for pr in EDGE3_PLAIN]:
                for sp in spans:
                    add("edge3", "eq", 1, method, h, stages=list(pair), tau2_ratio=pair[0], tau3_ratio=pair[1],
                        span_ratio=sp)
        for ratio in EDGE2_RATIOS:
            add("edge2", "eq", 1, "uniform_in", h, stages=[ratio], tau2_ratio=ratio, span_ratio=EDGE2_SPAN)
    for pair in CROSS3_PAIRS:  # 第7弾: 式で end のずれが 0 を横切るステップの前後を測る
        for h in CROSS3_H:
            n0 = crossing_step(pair, h)
            wanted = {max(1, n0 + d) for d in CROSS3_OFFSETS} | {max(1, round(f * n0)) for f in CROSS3_FAR}
            for steps in sorted(wanted):
                for method in ("end", "uniform_in"):
                    add("cross3", "eq", 1, method, h, stages=list(pair), tau2_ratio=pair[0], tau3_ratio=pair[1],
                        span_ratio=steps * h, fixed_steps=steps)
    for kind, sets, grid in (("cross3c", CROSS3_PAIRS, CROSS3C_H), ("cross4", CROSS4_SETS, CROSS3_H)):  # 第8弾
        for st in sets:
            for h in grid:
                n0 = crossing_step(st, h)
                wanted = {max(1, n0 + d) for d in CROSS3_OFFSETS} | {max(1, round(f * n0)) for f in CROSS3_FAR}
                for steps in sorted(wanted):
                    for method in ("end", "uniform_in"):
                        add(kind, "eq", 1, method, h, stages=list(st), tau2_ratio=st[0], tau3_ratio=st[1],
                            tau4_ratio=st[2] if len(st) > 2 else None, span_ratio=steps * h, fixed_steps=steps)
    for st, spans in VARY_SETS:
        for sp in spans:
            for h in hs + H_FINE:
                for method in VARY_METHODS:
                    add("vary", "eq", 1, method, h, stages=list(st), tau2_ratio=st[0], tau3_ratio=st[1],
                        tau4_ratio=st[2] if len(st) > 2 else None, span_ratio=sp)
    for shape, (sets, spans) in PIPE_SETS.items():  # 第9弾
        for idx, params in enumerate(sets):
            for sp in spans:
                for h in hs + H_FINE:
                    for method in ("uniform_in", "ramp"):
                        add("pipe", "eq", 1, method, h, shape=shape, pipe_set=idx + 1, pipe_params=list(params), span_ratio=sp)
    for st, sp in LADDER_SETS:  # 第10弾
        for h in hs + H_FINE:
            for method in LADDER_ORDER:
                add("ladder", "eq", 1, method, h, stages=list(st), tau2_ratio=st[0],
                    tau3_ratio=st[1] if len(st) > 1 else None, span_ratio=sp)
    hs11 = hs + H_FINE + [x / 2.0 for x in h_extra]  # 第11弾: 2 の累乗でない刻みにも、半分の刻みの相手を作る
    for idx, shares in enumerate(OLAD_SHARES):
        for sp in OLAD_SPANS:
            for h in hs11:
                for level in OLAD_LEVELS if len(shares) > 1 else (0,):  # 1 本の組は段で計算が変わらない
                    add("olad", "eq" if len(set(shares)) == 1 else "skew", len(shares), f"known{level}", h,
                        shares=list(shares), share_set=idx + 1, level=level, span_ratio=sp)
    for st, sp in ILAD_SETS:
        for h in hs11:
            for method in LADDER_ORDER:
                add("ilad", "eq", 1, method, h, stages=list(st), tau2_ratio=st[0],
                    tau3_ratio=st[1] if len(st) > 1 else None, span_ratio=sp)
    for shape, (sets, spans) in PIPE2_SETS.items():  # 第12弾
        for idx, params in enumerate(sets):
            for sp in spans:
                for h in hs11:
                    for method in ("end", "uniform_in", "ramp"):
                        add("pipe2", "eq", 1, method, h, shape=shape, pipe_set=idx + 1, pipe_params=list(params), span_ratio=sp)
    for x in COARSE2_X:
        for y in COARSE2_Y:
            add("coarse2", "eq", 1, "ramp", x, stages=[x / y], tau2_ratio=x / y, span_ratio=COARSE2_STEPS * x,
                fixed_steps=COARSE2_STEPS)
    for ratio in TLAD_RATIOS:
        for sp in TLAD_SPANS:
            for h in hs11:
                for method in TLAD_ORDER:
                    add("tlad", "eq", 1, method, h, stages=[ratio], tau2_ratio=ratio, span_ratio=sp)
    return out


def crossing_step(pair, h: float) -> int:
    """刻み h のとき、end の 3 段目のずれ（2 次までの式）が 0 を横切るステップ。式だけから二分法で出す。"""
    rates = [1.0 / TAU] + [1.0 / (TAU * r) for r in pair]
    dt = h * TAU

    def value(sp: float) -> float:
        return end_prediction2(rates, dt, sp * TAU)

    a, b = 0.5, 4.0
    if value(a) * value(b) > 0:
        raise ValueError(f"no sign change for {pair} at h = {h}")
    for _ in range(60):
        c = (a + b) / 2.0
        a, b = (c, b) if value(a) * value(c) > 0 else (a, c)
    return int(round((a + b) / 2.0 / h))


def flip_time(pair) -> float:
    """3 段目の end のずれ（G_eff の式の 1 次の項）が 0 を横切る時刻 / τ。式だけから二分法で出す。"""
    rates = [1.0 / TAU, 1.0 / (TAU * pair[0]), 1.0 / (TAU * pair[1])]

    def lead(sp: float) -> float:
        return stage_prediction(rates, TAU * 1e-4, sp * TAU)

    a, b = 0.5, 4.0
    if lead(a) * lead(b) > 0:
        raise ValueError(f"no sign change for {pair}")
    for _ in range(60):
        c = (a + b) / 2.0
        a, b = (c, b) if lead(a) * lead(c) > 0 else (a, c)
    return (a + b) / 2.0


def stage_rates(u: dict) -> list[float]:
    """1 列につながった槽の速さ k_1 … k_m（1 段目は 1/TAU）。"""
    return [1.0 / TAU] + [1.0 / (TAU * r) for r in u["stages"]]


def bateman_last(rates: list[float], t: float) -> float:
    """最後の段の量（最初の量 V0 が 1 段目にある。速さは全部違う前提）。"""
    m = len(rates)
    total = sum(math.exp(-rates[i] * t) / math.prod(rates[j] - rates[i] for j in range(m) if j != i) for i in range(m))
    return V0 * math.prod(rates[:-1]) * total


def _matmul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def _expm(a):
    """小さい行列の指数関数（半分ずつに割って 2 乗で戻す。テイラー 18 項）。"""
    n = len(a)
    norm = max(sum(abs(v) for v in row) for row in a)
    halvings = max(0, math.ceil(math.log2(norm)) + 4) if norm > 0 else 0
    scaled = [[v / (1 << halvings) for v in row] for row in a]
    out = [[float(i == j) for j in range(n)] for i in range(n)]
    term = [row[:] for row in out]
    for k in range(1, 19):
        term = [[v / k for v in row] for row in _matmul(term, scaled)]
        out = [[x + y for x, y in zip(r1, r2)] for r1, r2 in zip(out, term)]
    for _ in range(halvings):
        out = _matmul(out, out)
    return out


def stage_prediction(rates: list[float], dt: float, t: float) -> float:
    """end の扱いで最後の槽に出るずれの予想。1 ステップ x ← (I + dt·G̃)·x を連続の式に読み替えた
    G_eff = G − (dt/2)·(D + G²)（D は G の k_i を k_i² に替えた行列）で進めた量 / 厳密な量 − 1。"""
    m = len(rates)

    def chain(ks):
        g = [[0.0] * m for _ in range(m)]
        for i, k in enumerate(ks):
            g[i][i] = -k
            if i + 1 < m:
                g[i + 1][i] = k
        return g

    g, d = chain(rates), chain([k * k for k in rates])
    g2 = _matmul(g, g)
    eff = [[g[i][j] - dt / 2.0 * (d[i][j] + g2[i][j]) for j in range(m)] for i in range(m)]
    exact = _expm([[v * t for v in row] for row in g])[m - 1][0]
    return _expm([[v * t for v in row] for row in eff])[m - 1][0] / exact - 1.0


def end_prediction2(rates: list[float], dt: float, t: float) -> float:
    """end の扱いで最後の槽に出るずれの予想（dt の 2 次まで）。G_eff = G + dt·H1 + dt²·H2。
    H1: 次の槽へ k_i·k_{i+1}/2、2 つ先へ −k_i·k_{i+1}/2。
    H2: 次の槽へ k_i·k_{i+1}·(k_i + k_{i+1})/12、2 つ先へ −k_i·k_{i+1}·(k_i + k_{i+1} + 4·k_{i+2})/12、3 つ先へ k_i·k_{i+1}·k_{i+2}/3。"""
    m = len(rates)
    g = [[0.0] * m for _ in range(m)]
    eff = [[0.0] * m for _ in range(m)]
    for i, k in enumerate(rates):
        g[i][i] = eff[i][i] = -k
        if i + 1 < m:
            nxt = rates[i + 1]
            g[i + 1][i] = k
            eff[i + 1][i] = k + dt * k * nxt / 2.0 + dt * dt * k * nxt * (k + nxt) / 12.0
        if i + 2 < m:
            nxt = rates[i + 1]
            eff[i + 2][i] = -dt * k * nxt / 2.0 - dt * dt * k * nxt * (k + nxt + 4.0 * rates[i + 2]) / 12.0
        if i + 3 < m:
            eff[i + 3][i] = dt * dt * k * rates[i + 1] * rates[i + 2] / 3.0
    exact = _expm([[v * t for v in row] for row in g])[m - 1][0]
    return _expm([[v * t for v in row] for row in eff])[m - 1][0] / exact - 1.0


def uniform_prediction(rates: list[float], dt: float, t: float) -> float:
    """uniform の扱いで最後の槽に出るずれの予想。G_eff = G + dt²·H（dt の 1 次の項は無い）。
    H: 次の槽へ k_i²·k_{i+1}/12、2 つ先へ −k_i·k_{i+1}·(k_i − 2·k_{i+2})/12、3 つ先へ −k_i·k_{i+1}·k_{i+2}/6。"""
    m = len(rates)
    g = [[0.0] * m for _ in range(m)]
    eff = [[0.0] * m for _ in range(m)]
    for i, k in enumerate(rates):
        g[i][i] = eff[i][i] = -k
        if i + 1 < m:
            g[i + 1][i] = k
            eff[i + 1][i] = k + dt * dt * k * k * rates[i + 1] / 12.0
        if i + 2 < m:
            eff[i + 2][i] = -dt * dt * k * rates[i + 1] * (k - 2.0 * rates[i + 2]) / 12.0
        if i + 3 < m:
            eff[i + 3][i] = -dt * dt * k * rates[i + 1] * rates[i + 2] / 6.0
    exact = _expm([[v * t for v in row] for row in g])[m - 1][0]
    return _expm([[v * t for v in row] for row in eff])[m - 1][0] / exact - 1.0


def _shifted_prediction(rates: list[float], t: float, shift) -> float:
    """G_eff = G + (shift(i, d) を i 段目から d 段先への項に足した行列) で進めた最後の槽の量 / 厳密な量 − 1。"""
    m = len(rates)
    g = [[0.0] * m for _ in range(m)]
    eff = [[0.0] * m for _ in range(m)]
    for i, k in enumerate(rates):
        g[i][i] = eff[i][i] = -k
        if i + 1 < m:
            g[i + 1][i] = k
        for d in (1, 2, 3):
            if i + d < m:
                eff[i + d][i] = g[i + d][i] + shift(i, d)
    exact = _expm([[v * t for v in row] for row in g])[m - 1][0]
    return _expm([[v * t for v in row] for row in eff])[m - 1][0] / exact - 1.0


def cascade_prediction(rates: list[float], dt: float, t: float) -> float:
    """cascade の予想。G_eff = G + dt²·Hc。
    Hc: 次の槽へ k_i²·k_{i+1}/12、2 つ先へ −k_i·k_{i+1}·(k_i + k_{i+2})/12、3 つ先へ k_i·k_{i+1}·k_{i+2}/12。"""
    def shift(i, d):
        k, k1 = rates[i], rates[i + 1]
        if d == 1:
            return dt * dt * k * k * k1 / 12.0
        if d == 2:
            return -dt * dt * k * k1 * (k + rates[i + 2]) / 12.0
        return dt * dt * k * k1 * rates[i + 2] / 12.0

    return _shifted_prediction(rates, t, shift)


def ramp_prediction(rates: list[float], dt: float, t: float) -> float:
    """ramp の予想。G_eff = G + dt³·Hr。
    Hr: 次の槽へ −k_i³·k_{i+1}/72、2 つ先へ k_i·k_{i+1}·(k_i² + k_i·k_{i+2} + k_{i+1}·k_{i+2})/72、
    3 つ先へ −k_i·k_{i+1}·k_{i+2}·(k_i + k_{i+1} + k_{i+3})/72。"""
    def shift(i, d):
        k, k1 = rates[i], rates[i + 1]
        if d == 1:
            return -dt ** 3 * k ** 3 * k1 / 72.0
        if d == 2:
            return dt ** 3 * k * k1 * (k * k + k * rates[i + 2] + k1 * rates[i + 2]) / 72.0
        return -dt ** 3 * k * k1 * rates[i + 2] * (k + k1 + rates[i + 3]) / 72.0

    return _shifted_prediction(rates, t, shift)


def _quad_series(x: float, weights) -> float:
    """Σ_j (−x)^j·Σ_n w_n·n!/(n + 1 + j)!（E_n/dt^(n+1) の級数を、打ち消し合う定数項を分数で先に引いてから足す）。"""
    total, power = 0.0, 1.0
    for j in range(60):
        coeff = sum(Fraction(w) * math.factorial(n) / math.factorial(n + 1 + j) for n, w in weights)
        total += float(coeff) * power
        power *= -x
    return total


def variant_coeffs(rates: list[float], dt: float, method: str) -> list[tuple[float, float, float]]:
    """槽 i（i ≥ 1）が同じステップに出す分 = a·I + b·V_{i−1} + c·V'_{i−1}（I は届く量、V_{i−1}・V'_{i−1} は上の槽のステップ最初・最後の量）。
    cascade: a = 1 − (1 − e^(−x))/x、b = c = 0。ramp: a = 1 − 2·E1/dt²、b = −k_{i−1}·(E0 − 2·E1/dt)（b は 0 以上）、c = 0。
    quad: 残る分 = I·(6·E1/dt² − 6·E2/dt³) + r0·(E0 − 4·E1/dt + 3·E2/dt²) + r1·(−2·E1/dt + 3·E2/dt²)。"""
    out = [(0.0, 0.0, 0.0)]
    for i in range(1, len(rates)):
        k = rates[i]
        x = k * dt
        if method == "cascade":
            out.append((1.0 + math.expm1(-x) / x, 0.0, 0.0))
            continue
        if method.startswith("tay"):  # 最初の値だけを知る: 同じステップに出る分 = F[r~]（届く量の合計 I は使わない。2 段だけ）
            if i != 1:
                raise ValueError("tay は上の槽に入る量が無い 2 段だけ")
            up = rates[0] * dt
            out.append((0.0, -sum(up * (-up) ** n / math.factorial(n) * (_quad_series(x, [(n, 1)]) - 1.0 / (n + 1))
                                  for n in range(int(method[-1]))), 0.0))
            continue
        if method == "quad":
            up = rates[i - 1] * dt
            out.append((1.0 - _quad_series(x, [(1, 6), (2, -6)]),
                        -up * _quad_series(x, [(0, 1), (1, -4), (2, 3)]), -up * _quad_series(x, [(1, -2), (2, 3)])))
            continue
        e0 = -math.expm1(-x) / k
        e1 = (x + math.expm1(-x)) / (k * k)
        out.append((1.0 - 2.0 * e1 / (dt * dt), -rates[i - 1] * (e0 - 2.0 * e1 / dt), 0.0))
    return out


def variant_recurrence(u: dict, steps: int, dt: float) -> float:
    """cascade・ramp の検算（float）。上の槽から順に出る量を決め、増やした分も下の槽の入る量に数える。"""
    rates = stage_rates(u)
    gains = [-math.expm1(-r * dt) for r in rates]
    coeffs = variant_coeffs(rates, dt, u["method"])
    x = [V0] + [0.0] * (len(rates) - 1)
    for _ in range(steps):
        out = [x[0] * gains[0]]
        for i in range(1, len(rates)):
            a, b, c = coeffs[i]
            end_up = x[i - 1] - out[i - 1] + (out[i - 2] if i >= 2 else 0.0)
            extra = min(max(out[i - 1] * a + x[i - 1] * b + end_up * c, 0.0), out[i - 1])
            out.append(x[i] * gains[i] + extra)
        x = [x[i] - out[i] + (out[i - 1] if i else 0.0) for i in range(len(rates))]
    return x[-1]


def pipe_spec(u: dict) -> dict:
    """pipe の配管。tanks は上から順、links は (元, 先, 速さ)、pumps は (先, 速さ)（外から入る）。"""
    k, p = 1.0 / TAU, u["pipe_params"]
    if u["shape"] == "branch":
        return {"tanks": ["a", "b", "c", "side", "sink"], "vol": {"a": V0}, "watch": "c", "pumps": [],
                "links": [("a", "b", k * p[0]), ("a", "side", k * (1.0 - p[0])), ("b", "c", k / p[1]), ("c", "sink", k / p[2])]}
    if u["shape"] == "merge":
        return {"tanks": ["a", "b", "c", "d", "sink"], "vol": {"a": V0, "b": V0}, "watch": "d", "pumps": [],
                "links": [("a", "c", k), ("b", "c", k / p[0]), ("c", "d", k / p[1]), ("d", "sink", k / p[2])]}
    if u["shape"] == "pumpfed":
        return {"tanks": ["b", "c", "sink"], "vol": {}, "watch": "c", "pumps": [("b", V0 * k)],
                "links": [("b", "c", k / p[0]), ("c", "sink", k / p[1])]}
    return {"tanks": ["a", "b"], "vol": {"a": V0}, "watch": "b", "pumps": [], "ring": True,
            "links": [("a", "b", k), ("b", "a", k / p[0])]}


def pipe_exact(u: dict, t: float) -> float:
    k, p = 1.0 / TAU, u["pipe_params"]
    if u["shape"] == "branch":  # 割合 s だけが B → C へ進む 3 段
        return p[0] * bateman_last([k, k / p[1], k / p[2]], t)
    if u["shape"] == "merge":  # 2 本の 3 段の足し算
        return bateman_last([k, k / p[1], k / p[2]], t) + bateman_last([k / p[0], k / p[1], k / p[2]], t)
    if u["shape"] == "pumpfed":  # C = q·[1/kC − e^(−kB·t)/(kC − kB) + kB·e^(−kC·t)/(kC·(kC − kB))]
        kb, kc = k / p[0], k / p[1]
        return V0 * k * (1.0 / kc - math.exp(-kb * t) / (kc - kb) + kb * math.exp(-kc * t) / (kc * (kc - kb)))
    k2 = k / p[0]
    return V0 * k / (k + k2) * -math.expm1(-(k + k2) * t)


def _ramp_ab(rate: float, dt: float) -> tuple[float, float]:
    """同じステップに出る分 = a·I + b·r0（I は届く量、r0 は届く速さのステップ最初の値）。b は 0 以上で、時間の単位を持つ。"""
    x = rate * dt
    e0 = -math.expm1(-x) / rate
    e1 = (x + math.expm1(-x)) / (rate * rate)
    return 1.0 - 2.0 * e1 / (dt * dt), -(e0 - 2.0 * e1 / dt)


def pipe_run(spec: dict, method: str, steps: int, dt: float, conv=float, mul=lambda a, b: a * b) -> dict:
    """pipe を進める。conv・mul を替えると、float（検算）でも固定小数点の整数でも同じ手順で進む。
    uniform_in: エンジンの入れ方（入る量は一定の速さ。増やした分は下の槽の入る量に数えない）。
    ramp: 入る速さは直線。上の槽から順に決め、増やした分も下の槽の入る量に数える。輪は 2 つの槽を同時に解く。"""
    tanks, links = spec["tanks"], spec["links"]
    v = {name: conv(spec["vol"].get(name, 0.0)) for name in tanks}
    zero = conv(0.0)
    plan_, clamped, pumped_in = {}, 0, zero
    for name in tanks:
        outs = [ln for ln in links if ln[0] == name]
        if not outs:
            continue
        total = sum(ln[2] for ln in outs)
        a, b = _ramp_ab(total, dt)
        x = total * dt
        plan_[name] = {"outs": outs, "gain": conv(-math.expm1(-x)), "theta": conv(1.0 + math.expm1(-x) / x), "a": conv(a),
                       "b": {ln: conv(b * ln[2]) for ln in links if ln[1] == name},
                       "pump": sum((conv(q * dt) for dst, q in spec["pumps"] if dst == name), zero),
                       "pump_b": sum((conv(b * q) for dst, q in spec["pumps"] if dst == name), zero),
                       "shares": [conv(ln[2] / total) for ln in outs[:-1]], "ins": [ln for ln in links if ln[1] == name]}

    def split(name, total):
        left, out = total, {}
        for ln, share in zip(plan_[name]["outs"][:-1], plan_[name]["shares"]):
            out[ln] = mul(total, share)
            left -= out[ln]
        out[plan_[name]["outs"][-1]] = left
        return out

    ring_scale = None
    if spec.get("ring") and method == "ramp":
        ring_scale = conv(1.0 / (1.0 - _ramp_ab(links[0][2], dt)[0] * _ramp_ab(links[1][2], dt)[0]))
    for _ in range(steps):
        flow, counted = {}, {}
        if ring_scale is not None:  # out_a = base_a + a_a·out_b + b_a·V_b、out_b = base_b + a_b·out_a + b_b·V_a を同時に解く
            (la, lb), pa, pb = links, plan_["a"], plan_["b"]
            base_a, base_b = mul(v["a"], pa["gain"]), mul(v["b"], pb["gain"])
            rhs_a = base_a + mul(v["b"], pa["b"][lb])
            rhs_b = base_b + mul(v["a"], pb["b"][la])
            out_a = mul(rhs_a + mul(rhs_b, pa["a"]), ring_scale)
            raw_b = mul(out_a, pb["a"]) + mul(v["a"], pb["b"][la])
            extra_b = min(max(raw_b, zero), out_a)
            out_b = base_b + extra_b
            extra_a = min(max(out_a - base_a, zero), out_b)
            clamped += (extra_b != raw_b) + (extra_a != out_a - base_a)
            flow = {la: base_a + extra_a, lb: out_b}
        else:
            if method == "uniform_in":  # エンジンは先に全部の槽の今までどおりの量を決める
                for name, pl in plan_.items():
                    counted.update(split(name, mul(v[name], pl["gain"])))
            for name in tanks:
                pl = plan_.get(name)
                if pl is None:
                    continue
                base_out = mul(v[name], pl["gain"])
                if method == "end":  # 入る量はステップの終わりに入る。同じステップには出ない
                    flow.update(split(name, base_out))
                    continue
                arrive = sum(((counted if method == "uniform_in" else flow)[ln] for ln in pl["ins"]), pl["pump"])
                if method == "uniform_in":
                    extra = mul(arrive, pl["theta"])
                else:
                    raw = mul(arrive, pl["a"]) + sum((mul(v[ln[0]], pl["b"][ln]) for ln in pl["ins"]), pl["pump_b"])
                    extra = min(max(raw, zero), arrive)
                    clamped += extra != raw
                flow.update(split(name, base_out + extra))
        for dst, _ in spec["pumps"]:
            v[dst] += plan_[dst]["pump"]
            pumped_in += plan_[dst]["pump"]
        for (src, dst, _), amount in flow.items():
            v[src] -= amount
            v[dst] += amount
    return {"v": v, "clamped": clamped, "pumped_in": pumped_in}


def olad_coeffs(rates: list[float], dt: float, level: int) -> list[float]:
    """出口のはしご: 弁 i が 1 ステップに取る割合。
    弁 i は自分の減り方 e^(−k_i·s) を厳密に知り、他の出口が取る速さ (K − k_i)·V·e^(−K·s) を s の level − 1 次まで知っている。
    割合 = (1 − e^(−k_i·dt)) + (K − k_i)·dt·Σ_{n<level} ((−K·dt)^n/n!)·W_n、W_n = E_n/dt^(n+1) − 1/(n+1)。"""
    total = sum(rates)
    out = []
    for r in rates:
        x = r * dt
        c = -math.expm1(-x)
        for n in range(level):
            w = _quad_series(x, [(n, 1)]) - 1.0 / (n + 1)
            c += (total - r) * dt * (-total * dt) ** n / math.factorial(n) * w
        out.append(c)
    return out


def base(u: dict) -> str:
    """native の単位は、同じ条件の組（valve・mixed・gentle）の式で答えを出す。"""
    return u.get("base") or u["kind"]


def span(u: dict) -> float:
    if base(u) == "chain2" or u["kind"] in ("chain3b", "edge3", "edge2", *CROSS_KINDS, "vary", *PIPE_KINDS, "ladder", "ilad", "olad", "coarse2", "tlad"):
        return u["span_ratio"]
    if u["kind"] == "ring":  # T = τ·τ2/(τ + τ2) の何倍か
        return u["span_ratio"] * u["tau2_ratio"] / (1.0 + u["tau2_ratio"])
    return GENTLE_SPAN if base(u) == "gentle" else SPAN


def pump_rate(u: dict) -> float:
    k = 1.0 / TAU
    if u["kind"] == "pump":
        return V0 * k * (1.0 if u["starved"] else PUMP_SHARE)
    return V0 * k * {"mixed": PUMP_SHARE, "gentle": GENTLE_SHARE, "fed": 1.0, "combo": COMBO_OUT}.get(base(u), 0.0)


def chain_exact(u: dict, t: float) -> float:
    """2 段目の量（Bateman）: V0·k1/(k2 − k1)·(e^(−k1·t) − e^(−k2·t))。"""
    k1, k2 = 1.0 / TAU, 1.0 / (TAU * u["tau2_ratio"])
    return V0 * k1 / (k2 - k1) * (math.exp(-k1 * t) - math.exp(-k2 * t))


def exact_left(u: dict, t: float) -> float:
    k = 1.0 / TAU
    if u["kind"] in PIPE_KINDS:
        return pipe_exact(u, t)
    if base(u) in ("valve", "delay", "olad"):
        return V0 * math.exp(-k * t)
    if base(u) in ("chain", "chain2"):
        return chain_exact(u, t)
    if u["kind"] in CHAIN_KINDS:
        return bateman_last(stage_rates(u), t)
    if u["kind"] == "combo":  # V∞ + (V0 − V∞)·e^(−K·t)、V∞ = (入る速さ − 出る速さ)/K
        settle = V0 * (COMBO_IN - COMBO_OUT)
        return settle + (V0 - settle) * math.exp(-k * t)
    if u["kind"] == "chain3":  # 3 段の Bateman
        k2, k3 = k / u["tau2_ratio"], k / u["tau3_ratio"]
        rates = (k, k2, k3)
        return V0 * k * k2 * sum(math.exp(-rates[i] * t) / math.prod(rates[m] - rates[i] for m in range(3) if m != i)
                                 for i in range(3))
    if u["kind"] == "ring":  # 槽 B の量 V0·k1/(k1 + k2)·(1 − e^(−(k1 + k2)·t))
        k2 = k / u["tau2_ratio"]
        return V0 * k / (k + k2) * -math.expm1(-(k + k2) * t)
    q = pump_rate(u)
    if base(u) == "fed":  # 槽の量 q·τ2·(1 − e^(−t/τ2))
        tau2 = TAU * u["tau2_ratio"]
        return q * tau2 * -math.expm1(-t / tau2)
    if u["kind"] == "pump":
        return max(0.0, V0 - q * t)
    return max(0.0, (V0 + q / k) * math.exp(-k * t) - q / k)  # 空になった後は 0


def recurrence_left(u: dict, steps: int, dt: float) -> float:
    """エンジンを使わない検算: 槽の残りだけを float の漸化式で進める（遅れは槽の残りに効かない）。"""
    k = 1.0 / TAU
    if u["kind"] in PIPE_KINDS:
        spec = pipe_spec(u)
        return pipe_run(spec, u["method"], steps, dt)["v"][spec["watch"]]
    if u["kind"] == "olad":  # 抑えが起きなければ、残りは V0·(1 − Σ割合)^N（漸化式でなく累乗で検算する）
        return V0 * (1.0 - sum(olad_coeffs([s * k for s in u["shares"]], dt, u["level"]))) ** steps
    if u["method"] in VARIANT_METHODS:
        return variant_recurrence(u, steps, dt)
    if u["kind"] in ("combo", "chain3", "ring", *CHAIN_KINDS):
        return flow_recurrence(u, steps, dt)
    if base(u) in ("chain", "chain2", "fed"):  # 入る量 → 槽 B（弁 1 本）
        k2 = 1.0 / (TAU * u["tau2_ratio"])
        g1, g2 = -math.expm1(-k * dt), -math.expm1(-k2 * dt)
        a, b = V0, 0.0
        for _ in range(steps):
            inflow = pump_rate(u) * dt if base(u) == "fed" else a * g1
            out = b * g2 + inflow * through_share(u, k, k2, dt, a)
            a, b = a - a * g1, b + inflow - min(out, b + inflow)
        return b
    rates = [s * k for s in u["shares"]]
    q = pump_rate(u)
    if u["kind"] == "pump":
        rates = []
    v = V0
    for _ in range(steps):
        if u["method"] == "independent":
            take = v * sum(-math.expm1(-r * dt) for r in rates)
        else:
            take = v * -math.expm1(-k * dt) if rates else 0.0
        if u["method"] in ("affine", "exact"):
            v = max(0.0, (v + q / k) * math.exp(-k * dt) - q / k)
        else:
            v = max(0.0, v - take - q * dt)
    return v


def through_share(u: dict, k1: float, k2: float, dt: float, upstream: float) -> float:
    """このステップに入った量のうち、同じステップの中で出ていく割合（independent は 0）。"""
    if u["method"] in ("uniform", "uniform_in"):  # 一定の速さで入ると見なす
        x = k2 * dt
        return 1.0 + math.expm1(-x) / x
    if u["method"] == "through":  # 2 段の閉じた式: 入った量 A·(1 − e^(−k1·dt)) のうち槽に残るのは A·k1/(k2 − k1)·(e^(−k1·dt) − e^(−k2·dt))
        stays = k1 / (k2 - k1) * (math.exp(-k1 * dt) - math.exp(-k2 * dt))
        return max(0.0, 1.0 - stays / -math.expm1(-k1 * dt))
    return 0.0


def flow_recurrence(u: dict, steps: int, dt: float) -> float:
    """第4弾の検算（float）。エンジンの入れ方どおり: まず今までどおりの量を決め、次に「このステップに届く量 I」の
    うち弁から同じステップに出る分を足す。足した分は下の槽の I に数えない。"""
    k = 1.0 / TAU
    uniform = u["method"] == "uniform_in"

    def through(rate: float) -> float:
        x = rate * dt
        return 1.0 + math.expm1(-x) / x if uniform else 0.0

    if u["kind"] in CHAIN_KINDS:  # 何段でも: 入った量のうち同じステップに出る分は、下の槽の入る量に数えない
        rates = stage_rates(u)
        gains = [-math.expm1(-r * dt) for r in rates]
        x = [V0] + [0.0] * (len(rates) - 1)
        for _ in range(steps):
            base_out = [v * g for v, g in zip(x, gains)]
            extra = [0.0] + [base_out[i - 1] * through(rates[i]) for i in range(1, len(rates))]
            x = [x[i] - base_out[i] - extra[i] + (base_out[i - 1] + extra[i - 1] if i else 0.0) for i in range(len(rates))]
        return x[-1]
    if u["kind"] == "combo":
        v, big_l = V0, k * dt
        phi = -math.expm1(-big_l)
        inflow, pumped = V0 * k * COMBO_IN * dt, V0 * k * COMBO_OUT * dt
        for _ in range(steps):
            out = max(0.0, (v + pumped / big_l) * phi - pumped)
            target = v * phi + (inflow - pumped) * (1.0 - phi / big_l)
            extra = min(max(max(target, 0.0) - out, 0.0), inflow) if uniform else 0.0
            v = v - out - extra - min(pumped, v - out) + inflow
        return v
    k2 = k / u["tau2_ratio"]
    g1, g2 = -math.expm1(-k * dt), -math.expm1(-k2 * dt)
    if u["kind"] == "ring":
        a, b = V0, 0.0
        for _ in range(steps):
            fa, fb = a * g1, b * g2
            ea, eb = fb * through(k), fa * through(k2)
            a, b = a - fa - ea + fb + eb, b - fb - eb + fa + ea
        return b
    k3 = k / u["tau3_ratio"]
    g3 = -math.expm1(-k3 * dt)
    a, b, c = V0, 0.0, 0.0
    for _ in range(steps):
        fa, fb, fc = a * g1, b * g2, c * g3
        eb, ec = fa * through(k2), fb * through(k3)
        a, b, c = a - fa, b - fb - eb + fa, c - fc - ec + fb + eb
    return c


def _err(left: float, exact: float) -> float:
    return left / exact - 1.0 if exact else left - exact


def label(u: dict) -> tuple[str, str]:
    kind = {"valve": "弁", "delay": "弁+遅れ", "mixed": "弁+ポンプ", "pump": "ポンプ", "gentle": "弁+弱いポンプ",
            "chain": "2 段"}.get(u["kind"], u["kind"])
    split = "" if u["split"] == "eq" else " 偏り"
    tail = " 不足" if u.get("starved") else ""
    family = f"{u['kind']}-{u['split']}-n{u['n']}-{u['method']}" + ("-short" if u.get("starved") else "")
    if u["kind"] == "chain":
        return f"chain-r{u['tau2_ratio']:g}", f"{kind} τ2/τ={u['tau2_ratio']:g} h={u['h']:.6g}"
    if u["kind"] == "chain2":
        return (f"chain2-r{u['tau2_ratio']:.3g}-s{u['span_ratio']:g}-{u['method']}",
                f"2 段 τ2/τ={u['tau2_ratio']:.3g} t={u['span_ratio']:g}τ {u['method']} h={u['h']:.6g}")
    if u["kind"] == "fed":
        return f"fed-r{u['tau2_ratio']:g}-{u['method']}", f"ポンプ → 槽 τ2/τ={u['tau2_ratio']:g} {u['method']} h={u['h']:.6g}"
    if u["kind"] == "flow":
        tail = f"-s{u['span_ratio']:g}" if u["base"] == "chain2" else ""
        return (f"flow-{u['base']}-r{u['tau2_ratio']:.3g}{tail}",
                f"エンジン uniform {u['base']} τ2/τ={u['tau2_ratio']:.3g}{tail} h={u['h']:.6g}")
    if u["kind"] == "combo":
        return (f"combo-{u['split']}-n{u['n']}-{u['method']}",
                f"入るポンプ + 弁{split} {u['n']} 本 + 出るポンプ {u['method']} h={u['h']:.6g}")
    if u["kind"] == "chain3":
        return (f"chain3-r{u['tau2_ratio']:.3g}-r{u['tau3_ratio']:.3g}-{u['method']}",
                f"3 段 τ2/τ={u['tau2_ratio']:.3g} τ3/τ={u['tau3_ratio']:.3g} {u['method']} h={u['h']:.6g}")
    if u["kind"] == "olad":
        return (f"olad-g{u['share_set']}-n{u['n']}-s{u['span_ratio']:g}-known{u['level']}",
                f"出口 {u['n']} 本（組 {u['share_set']}）t={u['span_ratio']:g}τ 段 {u['level']} h={u['h']:.6g}")
    if u["kind"] in PIPE_KINDS:
        return (f"{u['kind']}-{u['shape']}-p{u['pipe_set']}-s{u['span_ratio']:g}-{u['method']}",
                f"{u['shape']} 組 {u['pipe_set']} t={u['span_ratio']:g}τ {u['method']} h={u['h']:.6g}")
    if u["kind"] in CHAIN_KINDS:
        ratios = "-".join(f"r{r:.3g}" for r in u["stages"])
        tail = f"-s{u['span_ratio']:.6g}" if u["kind"] in ("chain3b", "edge3") else ""
        if u["kind"] in CROSS_KINDS:
            tail = f"-n{u['fixed_steps']}"
        if u["kind"] in ("vary", "ladder", "ilad", "tlad"):
            tail = f"-s{u['span_ratio']:g}"
        return (f"{u['kind']}-{ratios}{tail}-{u['method']}",
                f"{len(u['stages']) + 1} 段 τ比 {'・'.join(f'{r:.3g}' for r in u['stages'])}{tail} {u['method']} h={u['h']:.6g}")
    if u["kind"] == "ring":
        return (f"ring-r{u['tau2_ratio']:g}-s{u['span_ratio']:g}-{u['method']}",
                f"輪 τ2/τ={u['tau2_ratio']:g} t={u['span_ratio']:g}T {u['method']} h={u['h']:.6g}")
    if u["kind"] == "native":
        return (f"native-{u['base']}-{u['split']}-n{u['n']}",
                f"エンジン既定 {u['base']}{split} {u['n']} 本 h={u['h']:.6g}")
    return family, f"{kind}{split} {u['n']} 本{tail} {u['method']} h={u['h']:.6g}"


def run_engine(u: dict, ffs: dict) -> dict:
    """FluidFullSpeedSimulation のエンジンで 1 単位を進める。"""
    Network, to_q, lag_gain = ffs["Network"], ffs["to_q"], ffs["lag_gain"]
    dt = u["h"] * TAU
    steps = u.get("fixed_steps") or max(1, int(round(span(u) / u["h"])))
    t = steps * dt
    k = 1.0 / TAU
    delay = DELAY if u["kind"] == "delay" else 0.0
    if u["method"] in ("uniform", "through"):
        return run_recurrence_q(u, ffs, steps, dt, t)
    if u["kind"] in PIPE_KINDS:
        return run_pipe(u, ffs, steps, dt, t)
    if u["kind"] == "olad":
        return run_olad(u, ffs, steps, dt, t)
    if u["method"] in VARIANT_METHODS:
        return run_variant_q(u, ffs, steps, dt, t)
    if u["kind"] in FLOW_KINDS:
        return run_flow_engine(u, ffs, steps, dt, t)
    # 第1弾・第2弾の組は「別々に取る」エンジンで作る（エンジンの既定が厳密になった後も同じ値になるように）
    # inflows も今までの扱い（end）を指定する（エンジンの既定が uniform になった後も同じ値になるように）
    net = Network(dt=dt, outlets="exact" if u["kind"] == "native" else "independent", inflows="end")
    net.tank("pool", 1.0, volume=1024.0 * V0 if u["kind"] == "fed" else V0)
    q = pump_rate(u)
    if u["kind"] in ("chain", "chain2", "fed"):
        net.tank("second", 1.0).tank("sink", 1.0)
        if u["kind"] == "fed":
            net.pump("pool", "second", rate=q)
        else:
            net.valve("pool", "second", tau=TAU)
        net.valve("second", "sink", tau=TAU * u["tau2_ratio"])
        res = net.run(t)
        return {"steps": steps, "dt": dt, "t": t, "left_q": res["volumes_q"]["second"],
                "left": res["volumes_q"]["second"] / ffs["one"], "first_left": res["volumes_q"]["pool"] / ffs["one"],
                "conservation_q": res["conservation_error_q"], "lag_err_steps": None}
    if u["kind"] == "pump":
        for i in range(u["n"]):
            net.tank(f"out-{i}", 1.0)
            net.pump("pool", f"out-{i}", rate=q / u["n"])
    else:
        if base(u) in ("mixed", "gentle"):
            net.tank("pumped", 1.0)
            pump = net.pump("pool", "pumped", rate=q)
        for i, share in enumerate(u["shares"]):
            net.tank(f"out-{i}", 1.0)
            if u["method"] in ("independent", "exact"):
                net.valve("pool", f"out-{i}", tau=TAU / share, delay=delay)
            elif u["method"] == "joint":
                net.link("valve_joint", "pool", f"out-{i}", delay=delay, k_total=lag_gain(dt, TAU), share_q=to_q(share))
            else:
                net.link("valve_affine", "pool", f"out-{i}", k_total=lag_gain(dt, TAU), share_q=to_q(share),
                         q_over_k=to_q(q / k), pump_amount=pump["amount"])
    res = net.run(t)
    lag = None
    if delay:
        lag = max(abs(round((ln["first_arrival"] - ln["first_flow"]) / dt) - round(delay / dt)) for ln in res["links"])
    return {"steps": steps, "dt": dt, "t": t, "left_q": res["volumes_q"]["pool"], "left": res["volumes_q"]["pool"] / ffs["one"],
            "conservation_q": res["conservation_error_q"], "lag_err_steps": lag}


def run_flow_engine(u: dict, ffs: dict, steps: int, dt: float, t: float) -> dict:
    """第4弾: エンジン本体の inflows（end・uniform）で進める。outlets は既定（exact）。"""
    k = 1.0 / TAU
    net = ffs["Network"](dt=dt, inflows="uniform" if u["method"] == "uniform_in" else "end")
    watch = "second"
    if u["kind"] in CHAIN_KINDS:
        names = [f"t{i}" for i in range(len(u["stages"]) + 1)]
        watch = names[-1]
        net.tank(names[0], 1.0, volume=V0)
        for name in names[1:] + ["sink"]:
            net.tank(name, 1.0)
        for src, dst, rate in zip(names, names[1:] + ["sink"], stage_rates(u)):
            net.valve(src, dst, tau=1.0 / rate)
        res = net.run(t)
        return {"steps": steps, "dt": dt, "t": t, "left_q": res["volumes_q"][watch],
                "left": res["volumes_q"][watch] / ffs["one"], "first_left": res["volumes_q"][names[0]] / ffs["one"],
                "conservation_q": res["conservation_error_q"], "lag_err_steps": None}
    if u["kind"] == "combo":
        watch = "pool"
        net.tank("sea", 1.0, volume=1024.0 * V0).tank("pool", 1.0, volume=V0).tank("pumped", 1.0)
        net.pump("sea", "pool", rate=V0 * k * COMBO_IN)
        for i, share in enumerate(u["shares"]):
            net.tank(f"out-{i}", 1.0)
            net.valve("pool", f"out-{i}", tau=TAU / share)
        net.pump("pool", "pumped", rate=V0 * k * COMBO_OUT)
    elif u["kind"] == "ring":
        net.tank("pool", 1.0, volume=V0).tank("second", 1.0)
        net.valve("pool", "second", tau=TAU)
        net.valve("second", "pool", tau=TAU * u["tau2_ratio"])
    elif u["kind"] == "chain3":
        watch = "third"
        net.tank("pool", 1.0, volume=V0).tank("second", 1.0).tank("third", 1.0).tank("sink", 1.0)
        net.valve("pool", "second", tau=TAU)
        net.valve("second", "third", tau=TAU * u["tau2_ratio"])
        net.valve("third", "sink", tau=TAU * u["tau3_ratio"])
    else:  # flow: 第3弾の fed・chain2 と同じ配管
        net.tank("pool", 1.0, volume=1024.0 * V0 if u["base"] == "fed" else V0).tank("second", 1.0).tank("sink", 1.0)
        if u["base"] == "fed":
            net.pump("pool", "second", rate=pump_rate(u))
        else:
            net.valve("pool", "second", tau=TAU)
        net.valve("second", "sink", tau=TAU * u["tau2_ratio"])
    res = net.run(t)
    return {"steps": steps, "dt": dt, "t": t, "left_q": res["volumes_q"][watch],
            "left": res["volumes_q"][watch] / ffs["one"], "first_left": res["volumes_q"]["pool"] / ffs["one"],
            "conservation_q": res["conservation_error_q"], "lag_err_steps": None}


def run_recurrence_q(u: dict, ffs: dict, steps: int, dt: float, t: float) -> dict:
    """uniform・through: エンジンと同じ固定小数点（Q48、床）の整数で、入る量 → 槽 B → 受け を進める。
    エンジンは出る量をステップ最初の量までに抑えるので、この 2 つは法則を足すだけでは入らない。"""
    to_q, qmul, lag_gain = ffs["to_q"], ffs["qmul"], ffs["lag_gain"]
    k1, k2 = 1.0 / TAU, 1.0 / (TAU * u["tau2_ratio"])
    g1, g2 = lag_gain(dt, TAU), lag_gain(dt, TAU * u["tau2_ratio"])
    a, b, sink = (0 if u["kind"] == "fed" else to_q(V0)), 0, 0  # fed は槽 A を使わない（入る量はポンプ）
    start = a
    pump_amount = qmul(to_q(pump_rate(u)), to_q(dt))
    share_q = to_q(through_share(u, k1, k2, dt, 0.0))
    for _ in range(steps):
        if u["kind"] == "fed":
            inflow, start = pump_amount, start + pump_amount  # 外から入った分を総量に数える
        else:
            inflow = qmul(a, g1)
            a -= inflow
        out = min(qmul(b, g2) + qmul(inflow, share_q), b + inflow)
        b += inflow - out
        sink += out
    total = a + b + sink
    return {"steps": steps, "dt": dt, "t": t, "left_q": b, "left": b / ffs["one"], "first_left": a / ffs["one"],
            "conservation_q": total - start, "lag_err_steps": None}


def run_variant_q(u: dict, ffs: dict, steps: int, dt: float, t: float) -> dict:
    """cascade・ramp: エンジンと同じ固定小数点（Q48、床）の整数で、1 列の槽を進める。抑えた回数も数える。"""
    to_q, qmul, lag_gain = ffs["to_q"], ffs["qmul"], ffs["lag_gain"]
    rates = stage_rates(u)
    gains = [lag_gain(dt, 1.0 / r) for r in rates]
    coeffs = [tuple(to_q(v) for v in row) for row in variant_coeffs(rates, dt, u["method"])]
    x = [to_q(V0)] + [0] * len(rates)  # 最後は受け
    start, clamped = x[0], 0
    for _ in range(steps):
        out = [qmul(x[0], gains[0])]
        for i in range(1, len(rates)):
            a, b, c = coeffs[i]
            end_up = x[i - 1] - out[i - 1] + (out[i - 2] if i >= 2 else 0)
            raw = qmul(out[i - 1], a) + qmul(x[i - 1], b) + qmul(end_up, c)
            extra = min(max(raw, 0), out[i - 1])
            clamped += extra != raw
            out.append(qmul(x[i], gains[i]) + extra)
        for i, amount in enumerate(out):
            x[i] -= amount
            x[i + 1] += amount
    return {"steps": steps, "dt": dt, "t": t, "left_q": x[-2], "left": x[-2] / ffs["one"], "first_left": x[0] / ffs["one"],
            "conservation_q": sum(x) - start, "lag_err_steps": None, "clamped": clamped}


def run_pipe(u: dict, ffs: dict, steps: int, dt: float, t: float) -> dict:
    """第9弾: uniform はエンジン本体、ramp はエンジンと同じ固定小数点（Q48、床）の整数の漸化式。"""
    spec = pipe_spec(u)
    one = ffs["one"]
    if u["method"] == "ramp":
        res = pipe_run(spec, "ramp", steps, dt, conv=ffs["to_q"], mul=ffs["qmul"])
        start = sum(ffs["to_q"](x) for x in spec["vol"].values()) + res["pumped_in"]
        return {"steps": steps, "dt": dt, "t": t, "left_q": res["v"][spec["watch"]], "left": res["v"][spec["watch"]] / one,
                "first_left": res["v"][spec["tanks"][0]] / one, "conservation_q": sum(res["v"].values()) - start,
                "lag_err_steps": None, "clamped": res["clamped"]}
    net = ffs["Network"](dt=dt, inflows="uniform" if u["method"] == "uniform_in" else "end")
    for name in spec["tanks"]:
        net.tank(name, 1.0, volume=spec["vol"].get(name, 0.0))
    if spec["pumps"]:
        net.tank("sea", 1.0, volume=1024.0 * V0)
    for dst, q in spec["pumps"]:
        net.pump("sea", dst, rate=q)
    for src, dst, rate in spec["links"]:
        net.valve(src, dst, tau=1.0 / rate)
    res = net.run(t)
    return {"steps": steps, "dt": dt, "t": t, "left_q": res["volumes_q"][spec["watch"]],
            "left": res["volumes_q"][spec["watch"]] / one, "first_left": res["volumes_q"][spec["tanks"][0]] / one,
            "conservation_q": res["conservation_error_q"], "lag_err_steps": None}


def run_olad(u: dict, ffs: dict, steps: int, dt: float, t: float) -> dict:
    """第11弾: 段 0 はエンジン本体（別々に取る）、段 1〜3 はエンジンと同じ固定小数点（Q48、床）の整数の漸化式。"""
    one = ffs["one"]
    if u["level"] == 0:
        net = ffs["Network"](dt=dt, outlets="independent", inflows="end")
        net.tank("pool", 1.0, volume=V0)
        for i, share in enumerate(u["shares"]):
            net.tank(f"out-{i}", 1.0)
            net.valve("pool", f"out-{i}", tau=TAU / share)
        res = net.run(t)
        return {"steps": steps, "dt": dt, "t": t, "left_q": res["volumes_q"]["pool"], "left": res["volumes_q"]["pool"] / one,
                "conservation_q": res["conservation_error_q"], "lag_err_steps": None, "clamped": 0}
    coeffs = [ffs["to_q"](c) for c in olad_coeffs([s / TAU for s in u["shares"]], dt, u["level"])]
    v = start = ffs["to_q"](V0)
    taken, clamped = 0, 0
    for _ in range(steps):
        raw = [ffs["qmul"](v, c) for c in coeffs]
        takes = [max(x, 0) for x in raw]
        if sum(takes) > v:  # 合計が槽の量を超えたら、順に取れるだけ取る
            left, takes = v, []
            for x in raw:
                takes.append(min(max(x, 0), left))
                left -= takes[-1]
        clamped += takes != raw
        v -= sum(takes)
        taken += sum(takes)
    return {"steps": steps, "dt": dt, "t": t, "left_q": v, "left": v / one, "conservation_q": v + taken - start,
            "lag_err_steps": None, "clamped": clamped}


def load_ffs(path: Path) -> dict:
    sys.path.insert(0, str(path))
    import fixedq
    import network

    @network.register_law("valve_joint")
    def _joint(net, ln, n):  # 同じ槽の弁をまとめる: 合計で 1 − e^(−K·dt) を取り、速さの比で分ける
        return fixedq.qmul(fixedq.qmul(net.nodes[ln["src"]]["v"], ln["k_total"]), ln["share_q"])

    @network.register_law("valve_affine")
    def _affine(net, ln, n):  # dV/dt = −K·V − q の 1 ステップの解。弁の合計 = (V + q/K)(1 − e^(−K·dt)) − q·dt
        total = fixedq.qmul(net.nodes[ln["src"]]["v"] + ln["q_over_k"], ln["k_total"]) - ln["pump_amount"]
        return fixedq.qmul(max(total, 0), ln["share_q"])

    return {"Network": network.Network, "one": fixedq.ONE, "qmul": fixedq.qmul, "to_q": fixedq.to_q, "lag_gain": fixedq.lag_gain,
            "random_scales": fixedq.random_scales}


def derive(units: list[dict], log=print) -> None:
    """err と、単位どうしを比べる列を足す。"""
    k = 1.0 / TAU
    by = {}
    for u in units:
        exact = exact_left(u, u["t"])
        u["exact"] = exact
        u["err"] = _err(u["left"], exact)
        u["err_abs"] = abs(u["err"])
        for flag in ("valve", "pump", "mixed", "delay", "gentle", "chain", "native", "chain2", "fed", *FLOW_KINDS):
            u[{"valve": "valve_only", "pump": "pump_only", "delay": "has_delay"}.get(flag, flag)] = u["kind"] == flag
        for m in ("independent", "joint", "affine", "uniform", "through", "cascade", "ramp", "quad"):
            u[m] = u["method"] == m
        u["equal_split"] = u["split"] == "eq"
        u["starved"] = bool(u.get("starved"))
        for col in ("err_pred", "fo_rel", "ceil_ratio", "corr_gain", "drop_from_fewer", "halving_ratio", "src_same",
                    "euler_ratio", "so_rel", "disc_gap", "joint_ratio", "first_err_abs", "chain_halving",
                    "chain_pred_rel", "fed_gap", "gain_vs_independent", "uniform_halving",
                    "native_gap", "chain3_pred_rel", "gain_vs_end", "flow_halving", "stage_fit", "sign_ok",
                    "uni_fit", "uni_fit2", "h_star", "h_ratio", "end2_fit", "pred_margin",
                    "gain_vs_uniform", "casc_fit", "ramp_fit", "ramp_clamped", "ramp_halving",
                    "order_expected", "order_est", "order_gap", "quad_fit2", "gain_vs_ramp", "quad_clamped",
                    "order_round", "olad_pred_abs", "olad_fit", "olad_clamped", "level_even",
                    "is_best", "clamp_margin", "clamp_pred", "was_clamped", "start_only", "coef_start", "coef_total"):
            u[col] = None
        for col in ("tau2_ratio", "span_ratio", "tau3_ratio", "tau4_ratio", "level"):
            u.setdefault(col, None)
        for shape, col in (("branch", "p_branch"), ("merge", "p_merge"), ("pumpfed", "p_pump"), ("ring", "p_ring")):
            u[col] = u["kind"] == "pipe" and u.get("shape") == shape  # pipe2 は第9弾の命題の範囲に入れない
        u["two_stage"] = u["kind"] == "ladder" and len(u["stages"]) == 1
        u["uniform_in"] = u["method"] == "uniform_in"
        u["from_pump"] = u["kind"] == "flow" and u["base"] == "fed"
        u["settled"] = u["kind"] == "ring" and u["span_ratio"] == RING_SPANS[-1]
        u["has_half"] = False
        by[(u["team"], u["h"])] = u
        if u["kind"] != "valve":
            continue
        rates = [s * k for s in u["shares"]]
        pred = -u["t"] * u["dt"] * (k * k - sum(r * r for r in rates)) / 2.0
        u["err_pred"] = pred
        u["ceil_ratio"] = u["err_abs"] / (u["t"] * u["dt"] * k * k / 2.0)
        # 第2弾の列: 離散の閉じた式・前進オイラーの形・2 次の式
        s2, s3 = sum(r * r for r in rates), sum(r ** 3 for r in rates)
        factor = 1.0 - sum(-math.expm1(-r * u["dt"]) for r in rates)
        u["disc_gap"] = abs(u["err"] - (factor ** u["steps"] / math.exp(-k * u["t"]) - 1.0))
        u["euler_ratio"] = u["err_abs"] / abs((1.0 - k * u["dt"]) ** u["steps"] / math.exp(-k * u["t"]) - 1.0)
        err2 = math.expm1(pred - u["t"] * u["dt"] ** 2 * (k ** 3 / 3.0 - k * s2 / 2.0 + s3 / 6.0))
        if u["n"] >= 2:
            u["so_rel"] = abs(u["err"] - err2) / abs(err2)
        if u["n"] >= 2:
            u["fo_rel"] = abs(u["err"] - pred) / abs(pred)
            fixed = abs(_err(u["left"] * math.exp(-pred), exact))
            if fixed == 0.0:
                log(f"ε: {u['team_name']} の直した後の err が 0。ε = {EPS} に置く")
                fixed = EPS
            u["corr_gain"] = u["err_abs"] / fixed
    for u in units:
        if u["kind"] == "valve":
            half = by.get((u["team"], u["h"] / 2.0))
            if half is not None and half["err"] != 0.0:
                u["has_half"], u["halving_ratio"] = True, u["err"] / half["err"]
            if u["split"] == "eq" and u["n"] >= 2:
                fewer = COUNTS[COUNTS.index(u["n"]) - 1]
                prev = by[(f"valve-eq-n{fewer}-{u['method']}", u["h"])]
                u["drop_from_fewer"] = u["err"] - prev["err"]
        if u["kind"] == "delay":
            twin = by[(f"valve-eq-n{u['n']}-{u['method']}", u["h"])]
            u["src_same"] = u["left_q"] == twin["left_q"]
        if u["kind"] == "gentle" and u["method"] == "joint":
            twin = by[(f"gentle-eq-n{u['n']}-independent", u["h"])]
            u["joint_ratio"] = u["err"] / twin["err"]
        if u["kind"] in ("chain2", "fed") and u["method"] == "independent":
            x = u["dt"] / (TAU * u["tau2_ratio"])
            if u["kind"] == "chain2":
                u["chain_pred_rel"] = abs(u["err"] - x / 2.0) / (x / 2.0)
            else:
                u["fed_gap"] = abs(u["err"] - (x / -math.expm1(-x) - 1.0))
        if u["method"] == "uniform":
            twin = by[(u["team"].replace("-uniform", "-independent"), u["h"])]
            mine = u["err_abs"]
            if mine == 0.0:
                log(f"ε: {u['team_name']} の err が 0。ε = {EPS} に置く")
                mine = EPS
            u["gain_vs_independent"] = twin["err_abs"] / mine
            half = by.get((u["team"], u["h"] / 2.0))
            if u["kind"] == "chain2" and half is not None and half["err"] != 0.0:
                u["has_half"], u["uniform_halving"] = True, u["err"] / half["err"]
        if u["kind"] == "flow":  # 第3弾の整数の漸化式（uniform）と比べる
            twin = by[(u["team"].replace("flow-", "") + "-uniform", u["h"])]
            u["native_gap"] = abs(u["err"] - twin["err"])
        if u["kind"] == "chain3" and not u["uniform_in"]:
            pred = u["dt"] / (2.0 * TAU * u["tau2_ratio"]) + u["dt"] / (2.0 * TAU * u["tau3_ratio"])
            u["chain3_pred_rel"] = abs(u["err"] - pred) / pred
        if u["kind"] in ("chain3b", "chain4") and not u["uniform_in"]:  # 第5弾: G_eff の式と比べる
            rates = stage_rates(u)
            pred = stage_prediction(rates, u["dt"], u["t"])
            u["stage_fit"] = abs(u["err"] - pred) / (u["dt"] / 2.0 * sum(rates[1:]))
            u["sign_ok"] = u["err"] * pred > 0.0
        if u["kind"] == "vary" and u["method"] in ("cascade", "ramp"):  # 第8弾: uniform と比べる・式と比べる
            rates = stage_rates(u)
            twin = by[(u["team"].replace("-" + u["method"], "-uniform_in"), u["h"])]
            mine = u["err_abs"]
            if mine == 0.0:
                log(f"ε: {u['team_name']} の err が 0。ε = {EPS} に置く")
                mine = EPS
            u["gain_vs_uniform"] = twin["err_abs"] / mine
            scale = u["dt"] * max(rates)
            if u["method"] == "cascade":
                u["casc_fit"] = abs(u["err"] - cascade_prediction(rates, u["dt"], u["t"])) / (scale ** 2 / 12.0)
            else:
                u["ramp_fit"] = abs(u["err"] - ramp_prediction(rates, u["dt"], u["t"])) / (scale ** 3 / 72.0)
                u["ramp_clamped"] = u.pop("clamped")
        if u["kind"] == "pipe" and u["method"] == "ramp":  # 第9弾
            twin = by[(u["team"].replace("-ramp", "-uniform_in"), u["h"])]
            mine = u["err_abs"]
            if mine == 0.0:
                log(f"ε: {u['team_name']} の err が 0。ε = {EPS} に置く")
                mine = EPS
            u["gain_vs_uniform"] = twin["err_abs"] / mine
            u["ramp_clamped"] = u.pop("clamped")
            half = by.get((u["team"], u["h"] / 2.0))
            if half is not None and half["err"] != 0.0:
                u["has_half"], u["ramp_halving"] = True, u["err"] / half["err"]
        if u["kind"] == "olad":  # 第11弾: 出口のはしご
            rates = [s * k for s in u["shares"]]
            total, p = sum(rates), u["level"]
            pred = -u["t"] * u["dt"] ** (p + 1) * (-total) ** p * (total * total - sum(r * r for r in rates)) / math.factorial(p + 2)
            u["olad_pred_abs"] = abs(pred)
            u["olad_fit"] = abs(u["err"] - pred) / abs(pred) if pred != 0.0 else None
            u["olad_clamped"] = u.pop("clamped")
            u["level_even"] = p % 2 == 0
        if u["kind"] == "pipe2":  # 第12弾: 同じ条件の 3 つの入れ方のうち、ずれが最小か
            stem = u["team"][: -len(u["method"])]
            u["is_best"] = u["err_abs"] == min(by[(stem + m, u["h"])]["err_abs"] for m in ("end", "uniform_in", "ramp"))
            if u["method"] == "ramp":
                u["ramp_clamped"] = u.pop("clamped")
        if u["kind"] == "coarse2":  # 第12弾: 抑える条件の式
            x, y = u["h"], u["h"] / u["stages"][0]
            f0, f1 = -math.expm1(-y) / y, (y + math.expm1(-y)) / (y * y)
            u["clamp_margin"] = (x / -math.expm1(-x)) / (2.0 * f1 / abs(f0 - 2.0 * f1))
            u["clamp_pred"] = u["clamp_margin"] > 1.0
            u["ramp_clamped"] = u.pop("clamped")
            u["was_clamped"] = u["ramp_clamped"] > 0
        if u["kind"] == "tlad":  # 第12弾: 2 段目のずれの係数
            rates, p = stage_rates(u), TLAD_ORDER[u["method"]] - 1
            scale = rates[1] * rates[0] ** p * u["dt"] ** (p + 1)
            u["start_only"] = u["method"].startswith("tay")
            u["coef_start"] = u["err_abs"] / (scale / math.factorial(p + 2))
            u["coef_total"] = u["err_abs"] / (scale * TOTAL_COEF[p])
        if u["kind"] in ("ladder", "ilad", "olad", "pipe2", "tlad"):  # 第10弾〜第12弾: 次数の見積もり
            u["order_expected"] = (u["level"] + 1 if u["kind"] == "olad" else
                                   TLAD_ORDER[u["method"]] if u["kind"] == "tlad" else LADDER_ORDER[u["method"]])
            half = by.get((u["team"], u["h"] / 2.0))
            if half is not None:
                u["has_half"] = True
                ratio = u["err"] / half["err"] if half["err"] != 0.0 else 0.0
                if ratio > 0.0:
                    u["order_est"] = math.log2(ratio)
                    u["order_gap"] = abs(u["order_est"] - u["order_expected"])
                    u["order_round"] = round(u["order_est"])
                else:
                    u["order_gap"], u["order_round"] = 99.0, -1
        if u["kind"] in ("ladder", "ilad"):
            if u["method"] in ("ramp", "quad"):
                u[u["method"] + "_clamped"] = u.pop("clamped")
            if u["method"] == "quad":
                twin = by[(u["team"].replace("-quad", "-ramp"), u["h"])]
                mine = u["err_abs"]
                if mine == 0.0:
                    log(f"ε: {u['team_name']} の err が 0。ε = {EPS} に置く")
                    mine = EPS
                u["gain_vs_ramp"] = twin["err_abs"] / mine
                if u["two_stage"]:
                    rates = stage_rates(u)
                    pred = rates[0] ** 3 * rates[1] * u["dt"] ** 4 / 720.0
                    u["quad_fit2"] = abs(u["err"] + pred) / pred
        u.pop("clamped", None)
        if u["kind"] in CROSS_KINDS:  # 第7弾・第8弾: end の 2 次までの式と、2 つの式の予想の比
            rates = stage_rates(u)
            pred_end = end_prediction2(rates, u["dt"], u["t"])
            if u["uniform_in"]:
                if pred_end == 0.0:
                    log(f"ε: {u['team_name']} の end の式の予想が 0。ε = {EPS} に置く")
                    pred_end = EPS
                u["pred_margin"] = abs(uniform_prediction(rates, u["dt"], u["t"])) / abs(pred_end)
            else:
                u["end2_fit"] = abs(u["err"] - pred_end) / ((u["dt"] * max(rates)) ** 2 / 12.0)
        if u["kind"] == "edge2":  # 第6弾: 2 段目の uniform のずれ k1·k2·dt²/12
            rates = stage_rates(u)
            pred = rates[0] * rates[1] * u["dt"] ** 2 / 12.0
            u["uni_fit2"] = abs(u["err"] - pred) / pred
        if u["kind"] == "edge3" and u["uniform_in"]:  # 第6弾: G_eff(uniform) の式と、式から出した境目
            rates = stage_rates(u)
            u["uni_fit"] = abs(u["err"] - uniform_prediction(rates, u["dt"], u["t"])) / ((u["dt"] * max(rates)) ** 2 / 12.0)
            tiny = TAU * 1e-4
            lead_end = stage_prediction(rates, tiny, u["t"]) / tiny
            lead_uni = uniform_prediction(rates, tiny, u["t"]) / tiny ** 2
            if lead_uni == 0.0:
                log(f"ε: {u['team_name']} の uniform の 2 次の係数が 0。ε = {EPS} に置く")
                lead_uni = EPS
            u["h_star"] = abs(lead_end / lead_uni) / TAU
            u["h_ratio"] = u["h"] / u["h_star"] if u["h_star"] else None
        if u["kind"] in ("combo", "chain3", "ring", "chain3b", "edge3", *CROSS_KINDS) and u["uniform_in"]:
            twin = by[(u["team"].replace("-uniform_in", "-end"), u["h"])]
            mine = u["err_abs"]
            if mine == 0.0:
                log(f"ε: {u['team_name']} の err が 0。ε = {EPS} に置く")
                mine = EPS
            u["gain_vs_end"] = twin["err_abs"] / mine
            half = by.get((u["team"], u["h"] / 2.0))
            if u["kind"] in ("chain3", "chain3b") and half is not None and half["err"] != 0.0:
                u["has_half"], u["flow_halving"] = True, u["err"] / half["err"]
        if u["kind"] == "chain":
            u["first_err_abs"] = abs(u["first_left"] / (V0 * math.exp(-k * u["t"])) - 1.0)
            half = by.get((u["team"], u["h"] / 2.0))
            if half is not None and half["err"] != 0.0:
                u["has_half"], u["chain_halving"] = True, u["err"] / half["err"]


def make(ffs_path: Path) -> int:
    ffs = load_ffs(ffs_path)
    extra = [item["value"] for item in ffs["random_scales"](H_SEED, 3, n_min=1, n_max=2)]
    units, season = [], {}
    for u in plan(extra):
        u["team"], u["team_name"] = label(u)
        season[u["team"]] = season.get(u["team"], 0) + 1
        u["season"] = season[u["team"]]  # 組の中の通し番号（PythDRagoras の単位の名前は team-season）
        u.update(run_engine(u, ffs))
        units.append(u)
    derive(units)
    UNITS.write_text("".join(json.dumps(u, ensure_ascii=False, sort_keys=True) + "\n" for u in units), encoding="utf-8")
    sha = subprocess.run(["git", "-C", str(ffs_path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    prov = {"engine": "myon-bioinformatics/FluidFullSpeedSimulation", "engine_commit": sha,
            "engine_files_sha256": {f: hashlib.sha256((ffs_path / f).read_bytes()).hexdigest()
                                    for f in ("fixedq.py", "network.py")},
            "h_extra": extra, "h_seed": H_SEED, "units": len(units),
            "units_sha256": hashlib.sha256(UNITS.read_bytes()).hexdigest()}
    PROVENANCE.write_text(json.dumps(prov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(units)} 単位 → {UNITS.name}（エンジン {sha[:7]}）")
    return 0


def read_units(path: Path = UNITS) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def check(path: Path = UNITS) -> int:
    """エンジンの残りを、素の漸化式で出し直した残りと比べる。違えば 65（データの誤り）。"""
    worst, bad = 0.0, []
    for u in read_units(path):
        again = _err(recurrence_left(u, u["steps"], u["dt"]), exact_left(u, u["t"]))
        gap = abs(again - u["err"])
        worst = max(worst, gap)
        if gap > TOL_CHECK:
            bad.append((u["team_name"], u["err"], again))
    for name, err, again in bad:
        print(f"[65] {name}: エンジン {err:.6g} / 検算 {again:.6g}")
    print(f"検算: {len(read_units(path))} 単位、err の差の最大 {worst:.3g}（許す差 {TOL_CHECK}）")
    return 65 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    mk = sub.add_parser("make", help="エンジンで単位を作る", allow_abbrev=False)
    mk.add_argument("--ffs", type=Path, required=True, help="FluidFullSpeedSimulation の作業ツリー")
    sub.add_parser("check", help="エンジンを使わずに検算する", allow_abbrev=False)
    args = ap.parse_args(argv)
    return make(args.ffs) if args.cmd == "make" else check()


if __name__ == "__main__":
    raise SystemExit(main())
