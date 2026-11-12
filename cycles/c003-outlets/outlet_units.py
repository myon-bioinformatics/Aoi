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
FLOW_KINDS = ("flow", "combo", "chain3", "ring")  # エンジンの inflows（end・uniform_in）で進める組
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
    return out


def base(u: dict) -> str:
    """native の単位は、同じ条件の組（valve・mixed・gentle）の式で答えを出す。"""
    return u.get("base") or u["kind"]


def span(u: dict) -> float:
    if base(u) == "chain2":
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
    if base(u) in ("valve", "delay"):
        return V0 * math.exp(-k * t)
    if base(u) in ("chain", "chain2"):
        return chain_exact(u, t)
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
    if u["kind"] in ("combo", "chain3", "ring"):
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
    steps = max(1, int(round(span(u) / u["h"])))
    t = steps * dt
    k = 1.0 / TAU
    delay = DELAY if u["kind"] == "delay" else 0.0
    if u["method"] in ("uniform", "through"):
        return run_recurrence_q(u, ffs, steps, dt, t)
    if u["kind"] in FLOW_KINDS:
        return run_flow_engine(u, ffs, steps, dt, t)
    # 第1弾・第2弾の組は「別々に取る」エンジンで作る（エンジンの既定が厳密になった後も同じ値になるように）
    net = Network(dt=dt, outlets="exact" if u["kind"] == "native" else "independent")
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
        for m in ("independent", "joint", "affine", "uniform", "through"):
            u[m] = u["method"] == m
        u["equal_split"] = u["split"] == "eq"
        u["starved"] = bool(u.get("starved"))
        for col in ("err_pred", "fo_rel", "ceil_ratio", "corr_gain", "drop_from_fewer", "halving_ratio", "src_same",
                    "euler_ratio", "so_rel", "disc_gap", "joint_ratio", "first_err_abs", "chain_halving",
                    "chain_pred_rel", "fed_gap", "gain_vs_independent", "uniform_halving",
                    "native_gap", "chain3_pred_rel", "gain_vs_end", "flow_halving"):
            u[col] = None
        for col in ("tau2_ratio", "span_ratio", "tau3_ratio"):
            u.setdefault(col, None)
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
        if u["kind"] in ("combo", "chain3", "ring") and u["uniform_in"]:
            twin = by[(u["team"].replace("-uniform_in", "-end"), u["h"])]
            mine = u["err_abs"]
            if mine == 0.0:
                log(f"ε: {u['team_name']} の err が 0。ε = {EPS} に置く")
                mine = EPS
            u["gain_vs_end"] = twin["err_abs"] / mine
            half = by.get((u["team"], u["h"] / 2.0))
            if u["kind"] == "chain3" and half is not None and half["err"] != 0.0:
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
