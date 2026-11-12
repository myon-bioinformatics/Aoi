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
    return out


def exact_left(u: dict, t: float) -> float:
    k = 1.0 / TAU
    if u["kind"] in ("valve", "delay"):
        return V0 * math.exp(-k * t)
    q = V0 * k * (1.0 if u.get("starved") else PUMP_SHARE)
    if u["kind"] == "pump":
        return max(0.0, V0 - q * t)
    return max(0.0, (V0 + q / k) * math.exp(-k * t) - q / k)  # 空になった後は 0


def recurrence_left(u: dict, steps: int, dt: float) -> float:
    """エンジンを使わない検算: 槽の残りだけを float の漸化式で進める（遅れは槽の残りに効かない）。"""
    k = 1.0 / TAU
    rates = [s * k for s in u["shares"]]
    q = 0.0
    if u["kind"] == "pump":
        q, rates = V0 * k * (1.0 if u["starved"] else PUMP_SHARE), []
    elif u["kind"] == "mixed":
        q = V0 * k * PUMP_SHARE
    v = V0
    for _ in range(steps):
        if u["method"] == "independent":
            take = v * sum(-math.expm1(-r * dt) for r in rates)
        else:
            take = v * -math.expm1(-k * dt) if rates else 0.0
        if u["method"] == "affine":
            v = max(0.0, (v + q / k) * math.exp(-k * dt) - q / k)
        else:
            v = max(0.0, v - take - q * dt)
    return v


def _err(left: float, exact: float) -> float:
    return left / exact - 1.0 if exact else left - exact


def label(u: dict) -> tuple[str, str]:
    kind = {"valve": "弁", "delay": "弁+遅れ", "mixed": "弁+ポンプ", "pump": "ポンプ"}[u["kind"]]
    split = "" if u["split"] == "eq" else " 偏り"
    tail = " 不足" if u.get("starved") else ""
    family = f"{u['kind']}-{u['split']}-n{u['n']}-{u['method']}" + ("-short" if u.get("starved") else "")
    return family, f"{kind}{split} {u['n']} 本{tail} {u['method']} h={u['h']:.6g}"


def run_engine(u: dict, ffs: dict) -> dict:
    """FluidFullSpeedSimulation のエンジンで 1 単位を進める。"""
    Network, to_q, lag_gain = ffs["Network"], ffs["to_q"], ffs["lag_gain"]
    dt = u["h"] * TAU
    steps = int(round(SPAN / u["h"]))
    t = steps * dt
    k = 1.0 / TAU
    delay = DELAY if u["kind"] == "delay" else 0.0
    net = Network(dt=dt)
    net.tank("pool", 1.0, volume=V0)
    q = 0.0
    if u["kind"] == "pump":
        q = V0 * k * (1.0 if u["starved"] else PUMP_SHARE)
        for i in range(u["n"]):
            net.tank(f"out-{i}", 1.0)
            net.pump("pool", f"out-{i}", rate=q / u["n"])
    else:
        if u["kind"] == "mixed":
            q = V0 * k * PUMP_SHARE
            net.tank("pumped", 1.0)
            pump = net.pump("pool", "pumped", rate=q)
        for i, share in enumerate(u["shares"]):
            net.tank(f"out-{i}", 1.0)
            if u["method"] == "independent":
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

    return {"Network": network.Network, "one": fixedq.ONE, "to_q": fixedq.to_q, "lag_gain": fixedq.lag_gain,
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
        for flag in ("valve", "pump", "mixed", "delay"):
            u[{"valve": "valve_only", "pump": "pump_only", "mixed": "mixed", "delay": "has_delay"}[flag]] = u["kind"] == flag
        for m in ("independent", "joint", "affine"):
            u[m] = u["method"] == m
        u["equal_split"] = u["split"] == "eq"
        u["starved"] = bool(u.get("starved"))
        for col in ("err_pred", "fo_rel", "ceil_ratio", "corr_gain", "drop_from_fewer", "halving_ratio", "src_same"):
            u[col] = None
        u["has_half"] = False
        by[(u["team"], u["h"])] = u
        if u["kind"] != "valve":
            continue
        rates = [s * k for s in u["shares"]]
        pred = -u["t"] * u["dt"] * (k * k - sum(r * r for r in rates)) / 2.0
        u["err_pred"] = pred
        u["ceil_ratio"] = u["err_abs"] / (u["t"] * u["dt"] * k * k / 2.0)
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
