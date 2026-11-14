"""research/epsilon-generality の検査（旧 9 本をまとめた。節の頭に旧ファイルの名前を書いた）。
"""

import csv
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import secrets
import sys
from pathlib import Path

import pytest


# ==== base（旧 test_epsilon_generality.py）
# research/epsilon-generality/eps_generality.py の確認。
#
# SYNTHETIC: 小さな合成の入力（実データではない）で、窓の作り方・正規化・基準の判定（境界の値ちょうどを含む）・
# 合成の系列・対照・書き出しを確かめる。結論には使わない。


ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
base_spec = importlib.util.spec_from_file_location("eps_generality", DIR / "eps_generality.py")
base_gen = importlib.util.module_from_spec(base_spec)
sys.modules["eps_generality"] = base_gen
base_spec.loader.exec_module(base_gen)
base_sa, base_trial = base_gen.load_modules(ROOT)


def month_rows(n, start=(2020, 1), key=("AAA", "staple_price:rice", "USD per kg", "https://github.com/tezamo/FPMA (x)", "market=m1"),
               values=None, day="01"):
    out, (y, m) = [], start
    for i in range(n):
        out.append({"country": key[0], "date": f"{y:04d}-{m:02d}-{day}", "year": str(y), "variable": key[1],
                    "value": str(values[i] if values else float(i + 1)), "unit": key[2], "source": key[3], "note": key[4],
                    "estimated_value": ""})
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def write_csv(path, rows):
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return path


# ---- 窓 ----------------------------------------------------------------------------------------------------------------
def test_month_index_roundtrip_and_validation():
    assert base_gen.month_text(base_gen.month_index("2020-12-15")) == "2020-12"
    assert base_gen.month_index("2021-01-01") - base_gen.month_index("2020-12-31") == 1
    for bad in ("2020-13-01", "2020-00-01", "20200101", "2020-1-1"):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            base_gen.month_index(bad)


def test_read_series_keeps_only_staple_prices_and_separates_series_by_note_and_ignores_the_day(tmp_path):
    rows = month_rows(3) + month_rows(3, key=("AAA", "staple_price:rice", "USD per kg", "https://github.com/tezamo/FPMA (x)", "market=m2"), day="15")
    rows += [dict(month_rows(1)[0], variable="bigmac_local_price")]
    s = base_gen.read_series(write_csv(tmp_path / "s.csv", rows))
    assert len(s) == 2 and all(len(v) == 3 for v in s.values())


def test_read_series_stops_on_a_repeated_month_or_a_non_finite_value(tmp_path):
    with pytest.raises(ValueError, match="同じ月が 2 つある"):
        base_gen.read_series(write_csv(tmp_path / "a.csv", month_rows(2) + [dict(month_rows(1)[0], date="2020-01-15")]))
    with pytest.raises(ValueError, match="有限でない"):
        base_gen.read_series(write_csv(tmp_path / "b.csv", month_rows(2, values=["1", "nan"])))


def test_tile_makes_non_overlapping_windows_inside_unbroken_runs_and_drops_the_remainder():
    series = {"k": {i: float(i) for i in range(0, 7)} | {i: float(i) for i in range(10, 14)}}       # 7 か月 + 4 か月（3 か月の空き）
    w = base_gen.tile(series, 3)
    assert [(x["start"], x["values"]) for x in w] == [(base_gen.month_text(0), [0.0, 1.0, 2.0]), (base_gen.month_text(3), [3.0, 4.0, 5.0]),
                                                      (base_gen.month_text(10), [10.0, 11.0, 12.0])]
    assert base_gen.tile(series, 8) == []
    assert base_gen.tile({"k": {0: 1.0, 2: 2.0, 4: 3.0}}, 2) == []            # 1 か月おきは「途切れている」


def test_tile_is_sorted_by_series_key_and_a_window_does_not_cross_series():
    series = {"b": {i: 1.0 for i in range(4)}, "a": {i: 2.0 for i in range(4)}}
    assert [w["key"] for w in base_gen.tile(series, 4)] == ["a", "b"]
    assert [w["si"] for w in base_gen.tile(series, 4)] == [0, 1] and [w["si"] for w in base_gen.tile(series, 2)] == [0, 0, 1, 1]


def test_normalize_puts_x_in_unit_interval_and_y_at_zero_start_with_range_five():
    xs, ys, s = base_gen.normalize([10.0, 14.0, 12.0, 20.0])
    assert xs == [0.0, 1 / 3, 2 / 3, 1.0] and ys[0] == 0.0 and s == 0.5
    assert max(ys) - min(ys) == 5.0 and ys == [0.0, 2.0, 1.0, 5.0]
    _, ys2, _ = base_gen.normalize([10.0, 4.0, 5.0])
    assert max(ys2) - min(ys2) == pytest.approx(5.0) and ys2[0] == 0.0 and min(ys2) == pytest.approx(-5.0)
    assert base_gen.normalize([3.0, 3.0, 3.0]) is None


def test_source_group_names():
    assert [base_gen.source_group(u) for u in (
        "https://github.com/tezamo/FPMA (all_commodity)", "https://data.humdata.org/dataset/wfp-food-prices (x)",
        "https://data.humdata.org/dataset/global-wfp-food-prices (x)", "https://www.bls.gov/data/", "https://www.e-stat.go.jp/", "x")] == [
        "FPMA", "WFP", "WFP-yearly", "BLS", "e-Stat", "other"]


# ---- 当てはめ ----------------------------------------------------------------------------------------------------------
def test_settle_tolerance_is_restored_even_when_the_body_fails():
    old = base_sa.WAVE_SETTLE
    with pytest.raises(RuntimeError):
        with base_gen.settle_tolerance(base_sa, 7.0):
            assert base_sa.WAVE_SETTLE == 7.0
            raise RuntimeError("x")
    assert base_sa.WAVE_SETTLE == old


def undamped_ys(period=1.0, phi=0.7, n=24, noise=0.0):
    xs = [i / (n - 1) for i in range(n)]
    v = [3.0 + 2.0 * math.cos(2 * math.pi * x / period + phi) for x in xs]
    xs, ys, s = base_gen.normalize(v)
    return xs, ys, s


def test_fit_row_on_an_undamped_wave_is_a_boundary_unit_and_epsilon_gives_finite_values_with_a_stable_coefficient():
    xs, ys, s = undamped_ys()
    bases = base_gen.make_bases(base_sa, base_trial, xs)
    r = base_gen.fit_row(base_sa, bases, ys, 0.5)
    assert r["boundary"] and r["decay"] == 0.0 and r["period"] == 1.0 and r["limit"] is None and r["settle_x"] is None
    for e in base_gen.EPS:
        f = r[base_gen.ekey(e)]
        assert f["decay"] == e and f["period"] == 1.0 and f["limit"] is not None and f["settle_x"] is not None and not f["at_start"]
        assert f["coefficient"] == f["settle_x"] * e                                       # 位置 = 係数 × 10^n
        assert 0.5 * math.exp(f["coefficient"]) == pytest.approx(2.0 * s, rel=1e-2)       # 戻した振幅 = 真の振幅
    c = [r[base_gen.ekey(e)]["coefficient"] for e in base_gen.EPS]
    assert abs(c[1] - c[2]) / c[2] < 1e-4 and abs(c[0] - c[2]) / c[2] < 2e-2


def test_fit_row_marks_a_wave_that_is_already_inside_tolerance_as_settled_at_start():
    xs, ys, _ = undamped_ys()
    bases = base_gen.make_bases(base_sa, base_trial, xs)
    r = base_gen.fit_row(base_sa, bases, ys, 1000.0)
    f = r[base_gen.ekey(1e-6)]
    assert r["boundary"] and f["at_start"] and f["coefficient"] is None and f["settle_x"] == 0.0 and r["settle_x"] == 0.0


def test_fit_row_leaves_a_damped_wave_alone():
    xs = [i / 23 for i in range(24)]
    v = [3.0 + 2.0 * math.exp(-3 * x) * math.cos(2 * math.pi * x / 0.5 + 0.4) for x in xs]
    xs, ys, _ = base_gen.normalize(v)
    r = base_gen.fit_row(base_sa, base_gen.make_bases(base_sa, base_trial, xs), ys, 0.5)
    assert not r["boundary"] and r["decay"] == 3.0 and r["period"] == 0.5
    assert all((r[base_gen.ekey(e)]["decay"], r[base_gen.ekey(e)]["period"]) == (3.0, 0.5) for e in base_gen.EPS)


def test_the_selected_form_does_not_depend_on_tau():
    xs, ys, _ = undamped_ys()
    bases = base_gen.make_bases(base_sa, base_trial, xs)
    forms = {(r["decay"], r["period"]) for r in (base_gen.fit_row(base_sa, bases, ys, t) for t in base_gen.TAUS)}
    assert len(forms) == 1


def test_tau_summary_reports_boundary_counts_and_that_forms_do_not_move():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": [3.0 + 2.0 * math.cos(2 * math.pi * x + p) for x in xs]} for p in (0.1, 0.7, 1.9)]
    t = base_gen.tau_summary(base_sa, base_gen.make_bases(base_sa, base_trial, xs), wins)
    assert list(t) == ["0.25", "0.5", "1"] and all(d["forms_same_as_first_tau"] for d in t.values())
    assert all(d["boundary"] == 3 for d in t.values())
    assert t["0.25"]["coefficient_min"] > t["0.5"]["coefficient_min"] > t["1"]["coefficient_min"]       # ln(振幅/τ): τ が大きいほど小さい


# ---- 合成の系列 --------------------------------------------------------------------------------------------------------
def test_synthetic_series_are_reproducible_and_differ_by_index_and_kind():
    sp = {s["id"]: s for s in base_gen.SYNTH}
    a = base_gen.synth_series(sp["undamped_p1"], 3)
    assert a == base_gen.synth_series(sp["undamped_p1"], 3) and a != base_gen.synth_series(sp["undamped_p1"], 4)
    assert a != base_gen.synth_series(sp["undamped_p0.5"], 3) and len(a) == base_gen.SYNTH_POINTS
    lin = base_gen.synth_series(sp["linear"], 0)
    assert lin[-1] - lin[0] == pytest.approx(2.0, abs=0.2)
    with pytest.raises(ValueError, match="合成の種類"):
        base_gen.synth_series({"id": "x", "kind": "zzz"}, 0)


def test_synthetic_undamped_series_come_out_as_boundary_units_with_the_true_amplitude():
    xs = [i / (base_gen.SYNTH_POINTS - 1) for i in range(base_gen.SYNTH_POINTS)]
    rows = base_gen.synth_rows(base_sa, base_gen.make_bases(base_sa, base_trial, xs), count=10)
    assert set(rows) == {s["id"] for s in base_gen.SYNTH} and all(len(v) == 10 for v in rows.values())
    assert all("true_amp" in r for sid in ("undamped_p1", "damped_l3") for r in rows[sid]) and "true_amp" not in rows["linear"][0]
    assert sum(r["boundary"] for r in rows["undamped_p1"]) == 10
    verdicts = base_gen.judge_synth(rows)
    assert [v["id"] for v in verdicts] == ["C5", "C5", "C3", "C3", "C3"] and verdicts[0]["ok"] is True and verdicts[1]["ok"] is True


# ---- 基準の判定（境界の値ちょうどを含む）------------------------------------------------------------------------------
def base_er(decay, period=1.0, coef=1.0, at_start=False, limit=1.0, settle=1.0):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": limit, "settle_x": settle, "coefficient": coef, "at_start": at_start}


def base_unit(boundary=True, overrides=None, **base):
    u = {"decay": 0.0 if boundary else 1.0, "period": 1.0, "rmse": 0.0, "limit": None, "settle_x": None, "boundary": boundary}
    u |= base
    for e in base_gen.EPS:
        u[base_gen.ekey(e)] = base_er(e if boundary else 1.0)
    for k, v in (overrides or {}).items():
        u[k] = base_er(**v) if isinstance(v, dict) else v
    return u


def crit(rows, tag="t"):
    return {(c["id"], c["text"][:14]): c for c in base_gen.judge_real(base_gen.stats(rows), tag)}


def get(verdicts, cid, needle):
    (c,) = [c for c in verdicts if c["id"] == cid and needle in c["text"]]
    return c


def test_c1_needs_98_percent_at_eps_1e3_and_all_at_the_smaller_epsilons():
    def case(n_bad, key):
        rows = [base_unit() for _ in range(100 - n_bad)] + [base_unit(overrides={key: {"decay": 1.0}}) for _ in range(n_bad)]
        return base_gen.judge_real(base_gen.stats(rows), "t")
    assert get(case(2, base_gen.ekey(1e-3)), "C1", "ε=0.001")["ok"] is True       # ちょうど 98%
    assert get(case(3, base_gen.ekey(1e-3)), "C1", "ε=0.001")["ok"] is False
    assert get(case(1, base_gen.ekey(1e-6)), "C1", "ε=1e-06")["ok"] is False
    assert get(case(1, base_gen.ekey(1e-9)), "C1", "ε=1e-09")["ok"] is False
    assert get(case(0, base_gen.ekey(1e-9)), "C1", "ε=1e-09")["ok"] is True
    for field, bad in (("period", None), ("limit", None), ("settle", None)):
        rows = [base_unit() for _ in range(99)] + [base_unit(overrides={base_gen.ekey(1e-9): {"decay": 1e-9, field: bad}})]
        assert get(base_gen.judge_real(base_gen.stats(rows), "t"), "C1", "ε=1e-09")["ok"] is False, field


def test_c2_compares_to_the_1e9_coefficient_and_counts_disagreement_about_settled_at_start():
    def case(key, coef, ref_coef=1.0, **extra):
        e = {base_gen.ekey(1e-3): 1e-3, base_gen.ekey(1e-6): 1e-6}[key]
        rows = [base_unit() for _ in range(30)] + [base_unit(overrides={key: dict(decay=e, coef=coef, **extra),
                                                              base_gen.ekey(1e-9): dict(decay=1e-9, coef=ref_coef)})]
        return base_gen.judge_real(base_gen.stats(rows), "t")
    assert get(case(base_gen.ekey(1e-3), 1.0199), "C2", "ε=0.001")["ok"] is True
    assert get(case(base_gen.ekey(1e-3), 1.0201), "C2", "ε=0.001")["ok"] is False
    assert get(case(base_gen.ekey(1e-3), 0.9801), "C2", "ε=0.001")["ok"] is True                # 下側も測る
    assert get(case(base_gen.ekey(1e-3), 0.9790), "C2", "ε=0.001")["ok"] is False
    assert get(case(base_gen.ekey(1e-6), 1.00009), "C2", "ε=1e-06")["ok"] is True
    assert get(case(base_gen.ekey(1e-6), 1.00011), "C2", "ε=1e-06")["ok"] is False
    assert get(case(base_gen.ekey(1e-6), 2.0, ref_coef=2.0002), "C2", "ε=1e-06")["ok"] is True       # 相対（基準の係数で割る）
    assert get(case(base_gen.ekey(1e-6), 2.0, ref_coef=2.0003), "C2", "ε=1e-06")["ok"] is False
    mism = case(base_gen.ekey(1e-3), None, at_start=True)
    c = get(mism, "C2", "ε=0.001")
    assert c["ok"] is False and "比べられない単位 1" in c["text"]


def test_c2_ignores_units_where_the_epsilon_wave_did_not_survive_because_c1_counts_them():
    rows = [base_unit() for _ in range(30)] + [base_unit(overrides={base_gen.ekey(1e-3): {"decay": 1.0, "coef": 500.0}})]
    v = base_gen.judge_real(base_gen.stats(rows), "t")
    assert get(v, "C2", "ε=0.001")["ok"] is True and get(v, "C1", "ε=0.001")["value"] == 30 / 31


def test_c3_counts_changed_forms_among_non_boundary_units_only():
    def case(n_bad, key, field="decay"):
        bad = {key: {"decay": 2.0 if field == "decay" else 1.0, "period": 0.5 if field == "period" else 1.0}}
        rows = [base_unit(False) for _ in range(200 - n_bad)] + [base_unit(False, overrides=bad) for _ in range(n_bad)]
        return base_gen.judge_real(base_gen.stats(rows), "t")
    assert get(case(4, base_gen.ekey(1e-3)), "C3", "ε=0.001")["ok"] is True          # 4/200 = 2%
    assert get(case(5, base_gen.ekey(1e-3)), "C3", "ε=0.001")["ok"] is False
    assert get(case(1, base_gen.ekey(1e-6)), "C3", "ε=1e-06")["ok"] is True          # 1/200 = 0.5%
    assert get(case(2, base_gen.ekey(1e-6)), "C3", "ε=1e-06")["ok"] is False
    assert get(case(2, base_gen.ekey(1e-9)), "C3", "ε=1e-09")["ok"] is False
    assert get(case(2, base_gen.ekey(1e-9), "period"), "C3", "ε=1e-09")["ok"] is False        # 周期の変化も数える
    boundary_change = [base_unit() for _ in range(30)] + [base_unit(overrides={base_gen.ekey(1e-3): {"decay": 2.0}})]
    c = get(base_gen.judge_real(base_gen.stats(boundary_change), "t"), "C3", "ε=0.001")
    assert c["value"] is None and c["ok"] is None                       # 境界の単位は C3 の母数に入らない


def test_small_sets_are_not_judged():
    rows = [base_unit() for _ in range(19)] + [base_unit(False) for _ in range(19)]
    assert all(c["ok"] is None for c in base_gen.judge_real(base_gen.stats(rows), "t"))
    rows = [base_unit() for _ in range(20)] + [base_unit(False) for _ in range(20)]
    assert all(c["ok"] is True for c in base_gen.judge_real(base_gen.stats(rows), "t"))
    only_nb = base_gen.judge_real(base_gen.stats([base_unit(False) for _ in range(25)]), "t")
    assert [c["ok"] for c in only_nb if c["id"] == "C3"] == [True] * 3 and all(c["ok"] is None for c in only_nb if c["id"] != "C3")
    assert base_gen.judge_real(base_gen.stats([]), "t")[0]["ok"] is None


def test_stats_reports_coefficient_range_and_settled_at_start_counts():
    rows = [base_unit(overrides={base_gen.ekey(1e-6): {"decay": 1e-6, "coef": c}}) for c in (0.5, 1.5)] + \
           [base_unit(overrides={base_gen.ekey(1e-6): {"decay": 1e-6, "coef": None, "at_start": True}})]
    st = base_gen.stats(rows)
    assert st["coefficient_range_eps6"] == [0.5, 1.5] and st["at_start"][base_gen.ekey(1e-6)] == 1 and st["boundary_share"] == 1.0


def synth_row(boundary=True, true_amp=2.5, coef=None, **over):
    r = base_unit(boundary) | {"true_amp": true_amp}
    if boundary:
        r[base_gen.ekey(1e-6)] = base_er(1e-6, coef=math.log(2.5 / 0.5) if coef is None else coef)
    return r | over


def test_c5_boundary_share_and_amplitude_error():
    def spec(n_boundary, n=100, **kw):
        return {"undamped_p1": [synth_row(True, **kw) for _ in range(n_boundary)] + [synth_row(False, **kw) for _ in range(n - n_boundary)]}
    assert base_gen.judge_synth(spec(90))[0]["ok"] is True and base_gen.judge_synth(spec(89))[0]["ok"] is False
    assert base_gen.judge_synth({"damped_l3": []})[0]["ok"] is None
    ok = base_gen.judge_synth(spec(100))[1]
    assert ok["ok"] is True and ok["value"] == pytest.approx(0.0, abs=1e-12)
    big = base_gen.judge_synth(spec(100, coef=math.log(2.5 * 1.049 / 0.5)))[1]
    small = base_gen.judge_synth(spec(100, coef=math.log(2.5 * 0.951 / 0.5)))[1]
    off = base_gen.judge_synth(spec(100, coef=math.log(2.5 * 1.051 / 0.5)))[1]
    assert big["ok"] is True and small["ok"] is True and off["ok"] is False
    assert base_gen.judge_synth(spec(100, coef=math.log(2.5 * 0.949 / 0.5)))[1]["ok"] is False                    # 小さいほうも測る
    unsettled = [synth_row(True, coef=None)]
    unsettled[0][base_gen.ekey(1e-6)] = base_er(1e-6, coef=None, at_start=True)
    c = base_gen.judge_synth({"undamped_p1": unsettled})[1]
    assert c["ok"] is False and c["value"] is None and "始まりの時点で決まったと出た系列 1" in c["text"]      # 幅が τ 以下に見えた = 外れ


def test_c5_damped_series_must_not_change_their_form():
    rows = [synth_row(False) for _ in range(200)]
    assert all(c["ok"] is True for c in base_gen.judge_synth({"damped_l3": rows})[2:])
    rows[0][base_gen.ekey(1e-6)] = base_er(2.0)
    v = base_gen.judge_synth({"damped_l3": rows})[2:]
    assert [c["ok"] for c in v] == [True, True, True]                          # 1/200 = 0.5% は ε=1e-6 で許容
    rows[1][base_gen.ekey(1e-6)] = base_er(2.0)
    assert base_gen.judge_synth({"damped_l3": rows})[3]["ok"] is False
    assert base_gen.judge_synth({"damped_l3": rows[:10]})[2]["ok"] is None


# ---- 対照・全体 ---------------------------------------------------------------------------------------------------------
def test_controls_pass_on_the_real_code_and_fail_when_the_basis_differs(monkeypatch):
    bases = {12: None, 24: None}
    c = base_gen.controls(base_sa, base_trial, bases)
    assert c["pass"] and set(c["eps0_basis_identical"]) == {"12", "24", f"synthetic{base_gen.SYNTH_POINTS}"}
    orig = base_trial.make_wave_basis

    def broken(sa_, eps):
        f = orig(sa_, eps)
        return lambda xs: [dict(b, uu=b["uu"] + 1e-9) for b in f(xs)]
    monkeypatch.setattr(base_trial, "make_wave_basis", broken)
    monkeypatch.setattr(base_trial, "self_check", lambda sa_: None)
    c2 = base_gen.controls(base_sa, base_trial, bases)
    assert not c2["pass"] and not any(c2["eps0_basis_identical"].values())


def base_small_csv(tmp_path):
    rows = []
    for j in range(3):
        vals = [3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5) for i in range(48)]
        rows += month_rows(48, key=("AAA", f"staple_price:c{j}", "USD per kg", "https://github.com/tezamo/FPMA (x)", f"market={j}"), values=vals)
    return write_csv(tmp_path / "s.csv", rows)


def test_cli_writes_the_summary_report_and_units_and_is_byte_reproducible(tmp_path):
    csv_path = base_small_csv(tmp_path)
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    assert base_gen.main(["--csv", str(csv_path), "--outdir", str(out1), "--repo", str(ROOT)]) == 0
    assert base_gen.main(["--csv", str(csv_path), "--outdir", str(out2), "--repo", str(ROOT)]) == 0
    names = sorted(p.name for p in out1.iterdir())
    assert names == ["eps_generality.json", "eps_generality.md", "eps_generality_units_n24.jsonl"]
    for n in names:
        assert (out1 / n).read_bytes() == (out2 / n).read_bytes()
    res = json.loads((out1 / "eps_generality.json").read_text(encoding="utf-8"))
    assert res["control"]["pass"] and res["repeat_identical"] and set(res["sets"]) == {"12", "24", "48"}
    assert res["sets"]["24"]["windows"] == 6 and res["sets"]["12"]["windows"] == 12 and res["sets"]["48"]["windows"] == 3
    assert list(res["sets"]["24"]["by_source"]) == ["FPMA"] and res["sets"]["24"]["by_source"]["FPMA"]["units"] == 6
    units = [json.loads(x) for x in (out1 / "eps_generality_units_n24.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(units) == 6 and {u["country"] for u in units} == {"AAA"} and "rows" not in res
    assert {u["unit"] for u in units} == {"USD per kg"} and sorted({u["series_index"] for u in units}) == [0, 1, 2]
    assert [u["series_index"] for u in units] == [0, 0, 1, 1, 2, 2] and [u["start"] for u in units[:2]] == ["2020-01", "2022-01"]
    md = (out1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "確かめられた" not in md.replace("「確かめられた」とは書かない", "")


def test_cli_stops_without_writing_when_the_control_fails(tmp_path, monkeypatch):
    csv_path = base_small_csv(tmp_path)
    monkeypatch.setattr(base_gen, "controls", lambda *a, **k: {"eps0_basis_identical": {"24": False}, "pass": False})
    out = tmp_path / "o"
    assert base_gen.main(["--csv", str(csv_path), "--outdir", str(out), "--repo", str(ROOT)]) == 2
    assert not out.exists()


def test_cli_stops_when_two_runs_differ(tmp_path, monkeypatch):
    csv_path = base_small_csv(tmp_path)
    real, calls = base_gen.compute, []

    def flaky(*a, **k):
        r = real(*a, **k)
        calls.append(1)
        if len(calls) == 2:
            r["seed"] += 1
        return r
    monkeypatch.setattr(base_gen, "compute", flaky)
    out = tmp_path / "o"
    assert base_gen.main(["--csv", str(csv_path), "--outdir", str(out), "--repo", str(ROOT)]) == 2
    assert not out.exists()


def test_render_wording_never_says_confirmed_and_names_the_failed_criteria():
    res = {"control": {"eps0_basis_identical": {"24": True}, "pass": True}, "repeat_identical": True, "sets": {}, "tau": {},
           "synthetic_forms": {}, "criteria": [base_gen._v("C1", "N=24", "テスト", 1.0, 1.0, ">=", True)]}
    res["sets"] = {str(n): {"windows": 1, "constant_windows": 0, "series": 1, "by_source": {}, "stats": {
        "units": 1, "boundary": 1, "boundary_share": 1.0, "coefficient_range_eps6": None,
        "at_start": {base_gen.ekey(e): 0 for e in base_gen.EPS}}} for n in base_gen.LENGTHS}
    ok = base_gen.render(res)
    assert "矛盾する材料はなかった" in ok and "確かめられた」とは書かない" in ok and "満たさなかった" not in ok
    res["criteria"].append(base_gen._v("C3", "N=24", "テスト3", 0.5, 0.1, "<=", False))
    res["criteria"].append(base_gen._v("C2", "N=12", "判定できない", None, 0.1, "<=", None))
    bad = base_gen.render(res)
    assert "満たさなかったのは 1 件" in bad and "C3（N=24" in bad and "矛盾する材料はなかった" not in bad
    res["control"]["pass"] = False
    assert "ほかの結果は読まない" in base_gen.render(res)


def test_readme_states_the_same_thresholds_as_the_script():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    for needle in ("98% 以上", "2% 以下", "0.01% 以下", "0.5% 以下", "90% 以上", "5% 以下", "20 未満", "SEED = 20261026", "N = 12, 24, 48"):
        assert needle in text, needle
    assert base_gen.CRIT == {"c1_eps3": 0.98, "c2_eps3": 0.02, "c2_eps6": 1e-4, "c3_eps3": 0.02, "c3_eps6": 0.005, "c3_eps9": 0.005,
                        "c5_boundary": 0.9, "c5_amp": 0.05}
    assert (base_gen.SEED, base_gen.LENGTHS, base_gen.PRIMARY, base_gen.TAUS, base_gen.PRIMARY_TAU, base_gen.EPS, base_gen.SCALE, base_gen.MIN_UNITS) == (
        20261026, (12, 24, 48), 24, (0.25, 0.5, 1.0), 0.5, (1e-3, 1e-6, 1e-9), 5.0, 20)
    assert (base_gen.N_SYNTH, base_gen.SYNTH_POINTS, base_gen.SYNTH_NOISE) == (200, 24, 0.02)
    for s in base_gen.SYNTH:
        assert f"`{s['id']}`" in text
    assert re.search(r"tests/test_epsilon_generality\.py", text)


# ---- 変異で見逃した部分の追加 -------------------------------------------------------------------------------------------
def _three_windows():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": [3.0 + 2.0 * math.cos(2 * math.pi * x + p) for x in xs]} for p in (0.1, 0.7, 1.9)]
    return base_gen.make_bases(base_sa, base_trial, xs), wins


def test_tau_summary_notices_when_the_selected_forms_depend_on_tau(monkeypatch):
    bases, wins = _three_windows()
    real = base_gen.fit_row

    def fake(sa_, b, ys, tau):
        r = real(sa_, b, ys, tau)
        return dict(r, decay=r["decay"] + 1.0) if tau == 1.0 else r
    monkeypatch.setattr(base_gen, "fit_row", fake)
    t = base_gen.tau_summary(base_sa, bases, wins)
    assert [t[k]["forms_same_as_first_tau"] for k in ("0.25", "0.5", "1")] == [True, True, False]


def test_tau_summary_counts_units_already_inside_the_tolerance(monkeypatch):
    bases, wins = _three_windows()
    monkeypatch.setattr(base_gen, "TAUS", (0.5, 1000.0))
    t = base_gen.tau_summary(base_sa, bases, wins)
    assert t["0.5"]["at_start"] == 0 and t["1000"]["at_start"] == 3 and t["1000"]["coefficient_min"] is None


def test_c5_amplitude_threshold_is_inclusive(monkeypatch):
    c = math.log(2.5 * 1.037 / 0.5)
    dev = abs(base_gen.PRIMARY_TAU * math.exp(c) / 2.5 - 1.0)
    rows = {"undamped_p1": [synth_row(True, coef=c) for _ in range(5)]}
    monkeypatch.setitem(base_gen.CRIT, "c5_amp", dev)
    assert base_gen.judge_synth(rows)[1]["ok"] is True
    monkeypatch.setitem(base_gen.CRIT, "c5_amp", dev * (1 - 1e-9))
    assert base_gen.judge_synth(rows)[1]["ok"] is False


def test_c3_for_damped_series_is_judged_from_exactly_20_series():
    assert base_gen.judge_synth({"damped_l3": [synth_row(False) for _ in range(20)]})[2]["ok"] is True
    assert base_gen.judge_synth({"damped_l3": [synth_row(False) for _ in range(19)]})[2]["ok"] is None


def test_render_says_not_to_read_the_rest_when_only_the_repeat_check_fails():
    bases = {"eps0_basis_identical": {"24": True}, "pass": True}
    res = {"control": bases, "repeat_identical": False, "sets": {str(n): {"windows": 1, "constant_windows": 0, "series": 1, "by_source": {}, "stats": {
        "units": 1, "boundary": 1, "boundary_share": 1.0, "coefficient_range_eps6": None,
        "at_start": {base_gen.ekey(e): 0 for e in base_gen.EPS}}} for n in base_gen.LENGTHS}, "tau": {}, "synthetic_forms": {}, "criteria": []}
    assert "ほかの結果は読まない" in base_gen.render(res)


def test_synthetic_noise_has_the_registered_size():
    sp = {s["id"]: s for s in base_gen.SYNTH}["undamped_p1"]
    diffs = [a - b for i in range(40) for a, b in zip(base_gen.synth_series(sp, i), base_gen.synth_series(sp, i, noise=0.0))]
    rms = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    assert 0.015 < rms < 0.025
    noise_spec = {s["id"]: s for s in base_gen.SYNTH}["noise"]
    vals = base_gen.synth_series(noise_spec, 0)
    assert max(vals) - min(vals) > 1.0


def test_compute_counts_five_field_identities_not_reporting_groups(tmp_path, monkeypatch):
    base = ("AAA", "staple_price:rice", "USD per kg", "https://github.com/tezamo/FPMA (a)", "market=a")
    keys = [base, base[:2] + ("USD per tonne",) + base[3:],
            base[:3] + ("https://github.com/tezamo/FPMA (b)", base[4]),
            base[:4] + ("market=b",)]
    # An earlier constant series leaves a gap in indices; another has no full window.
    constant = ("000",) + base[1:]
    short = ("ZZZ",) + base[1:]
    rows = [r for key in reversed(keys) for r in month_rows(96, key=key)]
    rows += month_rows(96, key=constant, values=[1.0] * 96)
    rows += month_rows(11, key=short)
    series = base_gen.read_series(write_csv(tmp_path / "identities.csv", rows))
    assert set(series) == set(keys + [constant, short])
    monkeypatch.setattr(base_gen, "SYNTH", ())
    result = base_gen.compute(base_sa, base_trial, series)
    for n in base_gen.LENGTHS:
        fitted = result["rows"]["real"][str(n)]
        assert {r["series_index"] for r in fitted} == {1, 2, 3, 4}
        assert len({(r["country"], r["variable"], r["source"]) for r in fitted}) == 1
        assert result["sets"][str(n)]["series"] == 4
        assert result["sets"][str(n)]["constant_windows"] == 96 // n
        for window in base_gen.tile(series, n):
            assert sorted(series)[window["si"]] == window["key"]


# ==== ladder（旧 test_epsilon_generality_ladder.py）
# research/epsilon-generality/eps_posthoc.py（旧 posthoc_eps_ladder.py）の確認。
#
# SYNTHETIC: 組み立てた行で、基準を超えた単位・ε の波が消えた単位の数え方、動いた単位の書き出し、梯子が定義域（0 < ε ≤ 1/100）に収まること、
# 小さな合成の入力での書き出し（同じ入力なら同じバイト）を確かめる。結論には使わない。


spec = importlib.util.spec_from_file_location("eps_posthoc", DIR / "eps_posthoc.py")
lad = importlib.util.module_from_spec(spec)
sys.modules["eps_posthoc"] = lad
spec.loader.exec_module(lad)
ladder_gen = lad.load_gen()


def ladder_er(decay, period=1.0, coef=1.0):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": False}


def ladder_row(boundary=True, over=None, lost=(), start="2020-01"):
    """梯子の ε すべてで基準の ε と同じ係数の単位。over の ε は係数を 1 倍ずらして基準を超えさせ、lost の ε は波を残さない。"""
    r = {"boundary": boundary, "country": "AAA", "variable": "v", "source": "s", "start": start, ladder_gen.ekey(ladder_gen.REF_EPS): ladder_er(ladder_gen.REF_EPS)}
    for e in lad.LADDER:
        r[ladder_gen.ekey(e)] = ladder_er(0.0 if e in lost else e, coef=2.0 if e in (over or ()) else 1.0)
    return r


def test_ladder_stays_inside_the_domain_and_every_epsilon_has_a_finite_threshold():
    assert all(0 < e <= 1e-2 for e in lad.LADDER) and list(lad.LADDER) == sorted(lad.LADDER) and 1e-2 in lad.LADDER and 1e-3 in lad.LADDER
    assert all(math.isfinite(ladder_gen.threshold("c2", e)) for e in lad.LADDER)


def test_dev_of_is_relative_to_the_reference_and_none_when_it_cannot_be_compared():
    r = ladder_row(over=(1e-3,))
    assert lad.dev_of(ladder_gen, r, 1e-3) == 1.0 and lad.dev_of(ladder_gen, r, 5e-4) == 0.0
    low = ladder_row(); low[ladder_gen.ekey(1e-3)] = ladder_er(1e-3, coef=0.25)
    assert lad.dev_of(ladder_gen, low, 1e-3) == 0.75 and lad.count_rows(ladder_gen, [low])["per_eps"][ladder_gen.ekey(1e-3)]["over"] == 1          # 小さいほうへのずれも数える
    assert lad.dev_of(ladder_gen, ladder_row(lost=(1e-3,)), 1e-3) is None
    r2 = ladder_row(); r2[ladder_gen.ekey(ladder_gen.REF_EPS)] = ladder_er(0.0)
    assert lad.dev_of(ladder_gen, r2, 1e-3) is None
    r3 = ladder_row(); r3[ladder_gen.ekey(1e-3)]["coefficient"] = None
    assert lad.dev_of(ladder_gen, r3, 1e-3) is None


def test_count_rows_counts_over_and_lost_for_boundary_units_only_and_lists_the_moved_ones():
    rows = [ladder_row() for _ in range(5)] + [ladder_row(over=(1e-3, 1e-2), start="2021-02"), ladder_row(lost=(1e-2,), start="2022-03"), ladder_row(boundary=False, over=(1e-3,))]
    c = lad.count_rows(ladder_gen, rows)
    assert c["boundary"] == 7 and c["moved_total"] == 2 and [m["start"] for m in c["moved"]] == ["2021-02", "2022-03"]
    over = {e: c["per_eps"][ladder_gen.ekey(e)]["over"] for e in lad.LADDER}
    lost = {e: c["per_eps"][ladder_gen.ekey(e)]["lost"] for e in lad.LADDER}
    assert over[1e-3] == 1 and over[1e-2] == 1 and sum(over.values()) == 2 and lost[1e-2] == 1 and sum(lost.values()) == 1
    assert [p["eps"] for p in c["moved"][0]["path"]] == list(lad.LADDER) and c["moved"][0]["path"][5]["dev"] == 1.0


def test_the_threshold_used_is_the_registered_one_at_1e_3_and_the_extension_above():
    ok = lambda dev, e: lad.count_rows(ladder_gen, [ladder_row() | {ladder_gen.ekey(e): ladder_er(e, coef=1.0 + dev)}])["per_eps"][ladder_gen.ekey(e)]["over"]
    t3, t2 = ladder_gen.threshold("c2", 1e-3), ladder_gen.threshold("c2", 1e-2)
    assert (t3, round(t2, 4)) == (0.02, 0.1170)
    assert ok(t3 * 0.99, 1e-3) == 0 and ok(t3 * 1.01, 1e-3) == 1                    # 登録した 0.02
    assert ok(t2 * 0.99, 1e-2) == 0 and ok(t2 * 1.01, 1e-2) == 1                    # 1/100 では延長した 11.7%


def test_count_rows_stops_listing_after_the_cap_but_keeps_the_total(monkeypatch):
    monkeypatch.setattr(lad, "MAX_LISTED", 3)
    c = lad.count_rows(ladder_gen, [ladder_row(over=(1e-3,)) for _ in range(5)])
    assert c["moved_total"] == 5 and len(c["moved"]) == 3 and c["per_eps"][ladder_gen.ekey(1e-3)]["over"] == 5
    assert "動いた単位は 5 個。上の 3 個だけ" in lad.eps_ladder_render(ladder_gen, {"ladder": list(lad.LADDER), "sets": {"12": c | {"units": 5}}})


def ladder_small_csv(tmp_path):
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = []
    for j in range(3):
        for i in range(48):
            y, m = 2020 + i // 12, i % 12 + 1
            v = 3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)
            rows.append({"country": "AAA", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": f"staple_price:c{j}", "value": str(v),
                         "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""})
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def test_main_writes_the_same_bytes_twice_and_clean_waves_do_not_move(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert lad.eps_ladder(["--csv", str(ladder_small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT)]) == 0
        outs.append(out)
    for n in ("posthoc_eps_ladder.json", "posthoc_eps_ladder.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    res = json.loads((outs[0] / "posthoc_eps_ladder.json").read_text(encoding="utf-8"))
    assert res["ladder"] == list(lad.LADDER) and list(res["sets"]) == [str(n) for n in ladder_gen.LENGTHS]
    assert all(s["units"] > 0 and s["moved_total"] == 0 and set(s["per_eps"]) == {ladder_gen.ekey(e) for e in lad.LADDER} for s in res["sets"].values())
    md = (outs[0] / "posthoc_eps_ladder.md").read_text(encoding="utf-8")
    assert "登録した基準の外" in md and "| 12 |" in md and "動いた単位" not in md


def test_ladder_readme_points_to_the_script():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    assert "eps_posthoc.py eps_ladder" in text and "tests/test_epsilon_generality.py" in text


# ==== physical（旧 test_epsilon_generality_physical.py）
# research/epsilon-generality/ の物理量の回（eps_generality.py の --profile、fetch_physical.py）の確認。
#
# SYNTHETIC: 小さな合成の入力（実データではない）で、日次の刻み・プロファイル・値の単位の報告・変換・固定したハッシュの確認・
# README の登録内容との一致を確かめる。結論には使わない。ネットワークは使わない。


def load(name):
    spec = importlib.util.spec_from_file_location(name, DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


physical_gen = load("eps_generality")
fp = load("fetch_physical")
physical_ph = load("eps_posthoc")
physical_sa, physical_trial = physical_gen.load_modules(ROOT)
PHYSICAL_COLS = fp.COLS


def physical_write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PHYSICAL_COLS)
        w.writeheader()
        w.writerows(rows)
    return path


def vrows(n, variable="physical:temp_max", country="Seattle", start=(2012, 1, 1), values=None, source="https://github.com/x/y@abcdefg (data/weather.csv)"):
    from datetime import date, timedelta
    d0 = date(*start)
    return [{"country": country, "date": (d0 + timedelta(days=i)).isoformat(), "year": str(d0.year), "variable": variable,
             "value": str(values[i] if values else float(i + 1)), "unit": "degC", "source": source, "note": "", "estimated_value": ""}
            for i in range(n)]


def physical_wave(n, phase, decay=0.0, period=1.0):
    return [3.0 + 2.0 * math.exp(-decay * (i / (n - 1))) * math.cos(2 * math.pi * (i / (n - 1)) / period + phase) + 0.001 * ((i * 7) % 5)
            for i in range(n)]


# ---- 日次の刻み ---------------------------------------------------------------------------------------------------------
def test_day_index_counts_consecutive_days_across_month_and_year_ends_and_validates():
    assert physical_gen.day_index("2020-03-01") - physical_gen.day_index("2020-02-29") == 1
    assert physical_gen.day_index("2021-01-01") - physical_gen.day_index("2020-12-31") == 1
    assert physical_gen.day_index("2020-03-01") - physical_gen.day_index("2020-01-31") == 30
    assert physical_gen.day_text(physical_gen.day_index("2012-01-01")) == "2012-01-01"
    for bad in ("2020-1-1", "20200101", "2020-02-30", "2020-13-01", "2020-00-10"):
        with pytest.raises(ValueError):
            physical_gen.day_index(bad)
    assert physical_gen.CADENCE["month"]["index"] is physical_gen.month_index and physical_gen.CADENCE["day"]["index"] is physical_gen.day_index


def test_read_series_takes_the_prefix_and_the_cadence_and_the_default_is_still_staple_by_month(tmp_path):
    rows = vrows(5) + vrows(1, variable="staple_price:rice", country="AAA") + vrows(3, variable="physical:wind_speed")
    p = physical_write_rows(tmp_path / "s.csv", rows)
    s = physical_gen.read_series(p, "physical:", "day")
    assert sorted(k[1] for k in s) == ["physical:temp_max", "physical:wind_speed"]
    assert sorted(len(v) for v in s.values()) == [3, 5]
    only = physical_gen.read_series(p)                                   # 既定 = staple_price:、月の刻み
    assert list(only) == [("AAA", "staple_price:rice", "degC", "https://github.com/x/y@abcdefg (data/weather.csv)", "")]
    assert list(only.values())[0] == {physical_gen.month_index("2012-01-01"): 1.0}


def test_read_series_stops_on_a_repeated_day_and_names_the_unit(tmp_path):
    dup = vrows(3) + [dict(vrows(1)[0])]
    with pytest.raises(ValueError, match="同じ日が 2 つある"):
        physical_gen.read_series(physical_write_rows(tmp_path / "a.csv", dup), "physical:", "day")
    with pytest.raises(ValueError, match="同じ月が 2 つある"):
        physical_gen.read_series(physical_write_rows(tmp_path / "b.csv", dup), "physical:", "month")
    with pytest.raises(ValueError, match="有限でない"):
        physical_gen.read_series(physical_write_rows(tmp_path / "c.csv", vrows(3, values=["1", "inf", "3"])), "physical:", "day")


def test_tile_labels_a_window_by_its_first_day_and_does_not_cross_a_missing_day():
    series = {"k": {physical_gen.day_index("2012-01-30") + i: float(i) for i in range(6)} | {physical_gen.day_index("2012-02-10") + i: float(i) for i in range(4)}}
    w = physical_gen.tile(series, 3, physical_gen.day_text)
    assert [(x["start"], x["values"]) for x in w] == [("2012-01-30", [0.0, 1.0, 2.0]), ("2012-02-02", [3.0, 4.0, 5.0]),
                                                     ("2012-02-10", [0.0, 1.0, 2.0])]
    assert physical_gen.tile(series, 3)[0]["start"] == physical_gen.month_text(physical_gen.day_index("2012-01-30"))      # 既定は月の書き方


def test_source_group_names_for_the_physical_files():
    assert [physical_gen.source_group(u) for u in (
        "https://github.com/vega/vega-datasets@5448e25 (data/weather.csv)", "https://github.com/vega/vega-datasets@5448e25 (data/co2-concentration.csv)",
        "https://github.com/datasets/global-temp@44571fe (data/monthly.csv)", "https://github.com/tezamo/FPMA (x)")] == [
        "NOAA-weather", "Scripps-CO2", "global-temp", "FPMA"]


# ---- 値の単位を変えたとき ------------------------------------------------------------------------------------------------
def three_windows_and_a_constant():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": physical_wave(24, p)} for p in (0.1, 0.7, 1.9)]
    wins.append({"key": "k", "start": "2022-01", "values": physical_wave(24, 0.3, decay=3.0, period=0.5)})
    wins.append({"key": "k", "start": "2024-01", "values": [4.0] * 24})
    return physical_gen.make_bases(physical_sa, physical_trial, xs), wins


def test_scale_summary_has_one_entry_per_scale_skips_constant_windows_and_scale_one_is_the_reference():
    bases, wins = three_windows_and_a_constant()
    out = physical_gen.scale_summary(physical_sa, bases, wins)
    assert list(out) == ["1e-06", "0.001", "1", "1000", "1e+06"] and physical_gen.SCALES == (1e-6, 1e-3, 1.0, 1e3, 1e6)
    assert {d["units"] for d in out.values()} == {4}
    ref = [physical_gen.fit_row(physical_sa, bases, physical_gen.normalize(w["values"])[1], physical_gen.PRIMARY_TAU) for w in wins[:4]]
    nb = sum(r["boundary"] for r in ref)
    one = out["1"]
    assert one["boundary"] == nb and 1 <= nb <= 3
    assert one["forms_changed"] == 0 and one["boundary_flag_changed"] == 0 and one["at_start_changed"] == 0
    assert one["eps_wave_kept"] == nb and one["coefficient_n"] == nb and one["coefficient_max_dev"] == 0.0


def test_scale_summary_counts_each_kind_of_change_separately(monkeypatch):
    bases, wins = three_windows_and_a_constant()
    wins = wins[:3]
    k6 = physical_gen.ekey(1e-6)
    calls = []

    def scale_of(tau):
        return min(physical_gen.SCALES, key=lambda s: abs(tau - physical_gen.PRIMARY_TAU * s))

    def fake(sa_, b, ys, tau):
        f, idx = scale_of(tau), len(calls) % 3                    # 倍率ごとに窓 0, 1, 2 の順に呼ばれる
        calls.append(1)
        assert max(ys) - min(ys) == pytest.approx(physical_gen.SCALE * f)        # y にも τ と同じ倍率がかかっている
        row = {"decay": 0.0, "period": 1.0, "rmse": 0.0, "limit": None, "settle_x": None, "boundary": True}
        for e in physical_gen.EPS:
            row[physical_gen.ekey(e)] = {"decay": e, "period": 1.0, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0,
                                "coefficient": 2.0 if f == 1.0 else 2.0 * (1 + 0.1 * (idx + 1)), "at_start": f == 1e3}
        if f == 1.0 and idx == 2:
            row.update(decay=0.5, boundary=False)
            row[k6]["decay"] = 0.5                                 # 境界でない単位では ε の波は選ばれない
        if f == 1e-6:
            row["period"] = 0.5                                    # 周期だけが変わる
        if f == 1e-3:
            row.update(decay=0.5, boundary=False)                  # 今のコードの式が変わる（境界でなくなる）
        if f == 1e6 and idx == 0:
            row[k6]["decay"] = 0.5                                 # ε の波が残らない
        return row
    monkeypatch.setattr(physical_gen, "fit_row", fake)
    out = physical_gen.scale_summary(physical_sa, bases, wins)
    cols = ("units", "boundary", "forms_changed", "boundary_flag_changed", "eps_wave_kept", "at_start_changed", "coefficient_max_dev", "coefficient_n")
    want = {"1e-06": (3, 3, 3, 1, 2, 0, 0.1 * 2, 2),            # 比べた単位は w0, w1。ずれは 2.2/2.0, 2.4/2.0 → 0.1, 0.2
            "0.001": (3, 0, 2, 2, 2, 0, None, 0),
            "1": (3, 2, 0, 0, 2, 0, 0.0, 2),
            "1000": (3, 3, 1, 1, 2, 2, 0.1 * 2, 2),
            "1e+06": (3, 3, 1, 1, 1, 0, 0.1 * 2, 2)}
    assert list(out) == list(want)
    for k, w in want.items():
        got = tuple(out[k][c] for c in cols)
        assert got == pytest.approx(w) if None not in w else got == w, k
    assert len(calls) == 15


# ---- プロファイル --------------------------------------------------------------------------------------------------------
def daily_csv(tmp_path):
    rows = []
    for j in range(3):
        rows += vrows(60, variable=f"physical:v{j}", values=physical_wave(60, 0.3 * j))
    rows += vrows(1, variable="staple_price:rice", country="AAA")
    return physical_write_rows(tmp_path / "d.csv", rows)


def test_cli_physical_daily_profile_writes_the_report_without_synthetic_series_and_is_byte_reproducible(tmp_path):
    p = daily_csv(tmp_path)
    o1, o2 = tmp_path / "o1", tmp_path / "o2"
    for o in (o1, o2):
        assert physical_gen.main(["--csv", str(p), "--outdir", str(o), "--repo", str(ROOT), "--profile", "physical-daily"]) == 0
    names = sorted(x.name for x in o1.iterdir())
    assert names == ["eps_generality.json", "eps_generality.md", "eps_generality_units_n24.jsonl"]
    for n in names:
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes()
    res = json.loads((o1 / "eps_generality.json").read_text(encoding="utf-8"))
    assert res["profile"] == "physical-daily" and res["control"]["pass"] and res["repeat_identical"]
    assert [res["sets"][n]["windows"] for n in ("12", "24", "48")] == [15, 6, 3]          # staple の行は読まない
    assert res["synthetic_forms"] == {} and not [c for c in res["criteria"] if c["id"] == "C5"]
    assert [c["set"] for c in res["criteria"] if c["id"] == "C1"] == [f"N={n}" for n in (12, 24, 48) for _ in range(3)]
    assert list(res["scales"]) == ["1e-06", "0.001", "1", "1000", "1e+06"] and res["scales"]["1"]["units"] == 6
    units = [json.loads(x) for x in (o1 / "eps_generality_units_n24.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(units) == 6 and [u["start"] for u in units[:2]] == ["2012-01-01", "2012-01-25"] and {u["source"] for u in units} == {"NOAA-weather"}
    md = (o1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "## 窓（物理量の日次）" in md and "| 24 日 |" in md and "| 24 か月 |" not in md
    assert "## 値の単位を変えたとき" in md and "合成の系列で今のコードが選んだ式" not in md
    assert "確かめられた" not in md.replace("「確かめられた」とは書かない", "")


def test_render_summary_names_the_physical_label_and_leaves_out_the_synthetic_series():
    res = {"control": {"eps0_basis_identical": {"24": True}, "pass": True}, "repeat_identical": True, "profile": "physical-daily", "tau": {},
           "synthetic_forms": {}, "criteria": [physical_gen._v("C1", "N=24", "テスト", 1.0, 1.0, ">=", True)],
           "scales": {"1": {"units": 5, "boundary": 2, "forms_changed": 0, "boundary_flag_changed": 0, "eps_wave_kept": 2, "at_start_changed": 0,
                            "coefficient_max_dev": 0.0, "coefficient_n": 2}}}
    res["sets"] = {str(n): {"windows": 1, "constant_windows": 0, "series": 1, "by_source": {}, "stats": {
        "units": 1, "boundary": 1, "boundary_share": 1.0, "coefficient_range_eps6": None,
        "at_start": {physical_gen.ekey(e): 0 for e in physical_gen.EPS}}} for n in physical_gen.LENGTHS}
    md = physical_gen.render(res)
    tail = md.split("## まとめ")[1]
    assert "物理量の日次で**矛盾する材料はなかった**" in tail and "合成の系列" not in tail
    assert "| 12 日 |" in md and "| 1 | 5 | 2 | 0 | 0 | 2 | 0 | 0 | 2 |" in md
    res["profile"] = "staple"
    del res["scales"]
    assert "主食価格の月次と合成の系列で**矛盾する材料はなかった**" in physical_gen.render(res).split("## まとめ")[1]


def test_cli_physical_monthly_profile_uses_months(tmp_path):
    rows = []
    y, m = 2000, 1
    vals = physical_wave(48, 0.2)
    for i in range(48):
        rows.append({"country": "Global", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": "physical:temp_anomaly", "value": str(vals[i]),
                     "unit": "degC (anomaly)", "source": "https://github.com/datasets/global-temp@44571fe (data/monthly.csv)", "note": "GCAG",
                     "estimated_value": ""})
        m += 1
        if m == 13:
            y, m = y + 1, 1
    p = physical_write_rows(tmp_path / "m.csv", rows)
    assert physical_gen.main(["--csv", str(p), "--outdir", str(tmp_path / "o"), "--repo", str(ROOT), "--profile", "physical-monthly"]) == 0
    res = json.loads((tmp_path / "o" / "eps_generality.json").read_text(encoding="utf-8"))
    assert [res["sets"][n]["windows"] for n in ("12", "24", "48")] == [4, 2, 1]
    assert list(res["sets"]["24"]["by_source"]) == ["global-temp"] and res["sets"]["24"]["by_source"]["global-temp"]["units"] == 2
    md = (tmp_path / "o" / "eps_generality.md").read_text(encoding="utf-8")
    assert "## 窓（物理量の月次）" in md and "| 24 か月 |" in md


def test_the_default_staple_profile_adds_no_keys_and_keeps_the_synthetic_part(tmp_path):
    rows = []
    for j in range(2):
        vals = physical_wave(48, 0.3 * j)
        rows += [{"country": "AAA", "date": f"{2020 + i // 12}-{i % 12 + 1:02d}-01", "year": str(2020 + i // 12), "variable": "staple_price:rice",
                  "value": str(vals[i]), "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}",
                  "estimated_value": ""} for i in range(48)]
    rows += vrows(5)                                           # physical: の行は読まない
    p = physical_write_rows(tmp_path / "s.csv", rows)
    assert physical_gen.main(["--csv", str(p), "--outdir", str(tmp_path / "o"), "--repo", str(ROOT)]) == 0
    res = json.loads((tmp_path / "o" / "eps_generality.json").read_text(encoding="utf-8"))
    assert list(res) == ["spec_version", "seed", "control", "sets", "criteria", "synthetic_forms", "tau", "repeat_identical"]
    assert [res["sets"][n]["windows"] for n in ("12", "24", "48")] == [8, 4, 2]
    assert len(res["synthetic_forms"]) == len(physical_gen.SYNTH) and any(c["id"] == "C5" for c in res["criteria"])


def test_profiles_are_registered_as_the_readme_says():
    assert sorted(physical_gen.PROFILES) == ["physical-daily", "physical-monthly", "staple"]
    assert physical_gen.PROFILES["staple"] == {"prefix": "staple_price:", "cadence": "month", "label": "主食価格の月次", "synth": True, "scales": False}
    assert physical_gen.PROFILES["physical-monthly"] == {"prefix": "physical:", "cadence": "month", "label": "物理量の月次", "synth": False, "scales": True}
    assert physical_gen.PROFILES["physical-daily"] == {"prefix": "physical:", "cadence": "day", "label": "物理量の日次", "synth": False, "scales": True}


# ---- fetch_physical.py -------------------------------------------------------------------------------------------------
WEATHER = "location,date,precipitation,temp_max,temp_min,wind,weather\nSeattle,2012-01-02,10.9,10.6,2.8,4.5,rain\nSeattle,2012-01-01,0.0,12.8,5.0,4.7,drizzle\n"
CO2 = "Date,CO2,adjusted CO2\n1958-03-01,315.70,314.44\n1958-04-01,317.46,315.16\n"
GT = "Source,Year,Mean\nGISTEMP,1880-01,-0.1\nGCAG,1850-02,-0.3604\nGCAG,1850-01,-0.7337\n"


def fixture_pins(raw_dir, texts=None):
    texts = texts or {"weather": WEATHER, "co2": CO2, "global-temp": GT}
    pins = {}
    for i, (name, text) in enumerate(texts.items()):
        (raw_dir / f"{name}.csv").write_text(text, encoding="utf-8")
        pins[name] = {"repo": f"o/r{i}", "commit": f"{i}abcdef0123456789abcdef0123456789abcdef"[:40].ljust(40, "0"), "path": f"data/{name}.csv",
                      "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "license": "L", "origin": "O"}
    return pins


def test_build_converts_the_three_files_into_sorted_vertical_rows(tmp_path):
    pins = fixture_pins(tmp_path)
    b = fp.build(tmp_path, pins)
    assert len(b["daily"]) == 8 and len(b["monthly"]) == 4 + 3
    d = b["daily"]
    assert [(r["variable"], r["date"]) for r in d[:2]] == [("physical:precipitation", "2012-01-01"), ("physical:precipitation", "2012-01-02")]   # 日付順
    assert {(r["variable"], r["unit"]) for r in d} == {("physical:precipitation", "mm"), ("physical:temp_max", "degC"),
                                                         ("physical:temp_min", "degC"), ("physical:wind_speed", "m/s")}
    r0 = next(r for r in d if r["variable"] == "physical:wind_speed" and r["date"] == "2012-01-01")
    assert r0 == {"country": "Seattle", "date": "2012-01-01", "year": "2012", "variable": "physical:wind_speed", "value": "4.7", "unit": "m/s",
                  "source": "https://github.com/o/r0@0abcdef (data/weather.csv)", "note": "", "estimated_value": ""}
    m = b["monthly"]
    gt = [r for r in m if r["variable"] == "physical:temp_anomaly"]
    assert [(r["note"], r["date"], r["value"]) for r in gt] == [("GCAG", "1850-01-01", "-0.7337"), ("GCAG", "1850-02-01", "-0.3604"),
                                                                 ("GISTEMP", "1880-01-01", "-0.1")]
    assert {r["unit"] for r in gt} == {"degC (anomaly)"} and {r["country"] for r in gt} == {"Global"}
    co2 = [r for r in m if r["variable"].startswith("physical:co2")]
    assert sorted({r["variable"] for r in co2}) == ["physical:co2", "physical:co2_seasonally_adjusted"] and {r["unit"] for r in co2} == {"ppm"}
    assert {(r["variable"], r["date"]): r["value"] for r in co2 if r["date"] == "1958-03-01"} == {
        ("physical:co2", "1958-03-01"): "315.70", ("physical:co2_seasonally_adjusted", "1958-03-01"): "314.44"}
    assert [r["country"] for r in m] == sorted(r["country"] for r in m)


def test_build_stops_when_a_file_differs_from_the_pinned_hash(tmp_path):
    pins = fixture_pins(tmp_path)
    (tmp_path / "co2.csv").write_text(CO2.replace("315.70", "315.71"), encoding="utf-8")
    with pytest.raises(ValueError, match="co2: sha256 が固定した値と違う"):
        fp.build(tmp_path, pins)


@pytest.mark.parametrize("name,text,msg", [
    ("weather", WEATHER.replace("10.9", ""), "値が空"),
    ("weather", WEATHER.replace("temp_min,wind", "tmin,wind"), "列が足りない"),
    ("co2", CO2.replace("315.70", "nan"), "有限でない"),
    ("global-temp", GT.replace("-0.1\n", "inf\n"), "有限でない"),
    ("global-temp", GT.replace("Source,", "Src,"), "列が足りない")])
def test_build_stops_on_blank_missing_or_non_finite_values(tmp_path, name, text, msg):
    texts = {"weather": WEATHER, "co2": CO2, "global-temp": GT} | {name: text}
    pins = fixture_pins(tmp_path, texts)
    with pytest.raises(ValueError, match=msg):
        fp.build(tmp_path, pins)


def test_main_writes_both_csvs_and_a_manifest_that_matches_the_files_and_the_harness_can_read_them(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    pins = fixture_pins(raw)
    monkeypatch.setattr(fp, "PINS", pins)
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    for o in (out1, out2):
        assert fp.main(["--raw-dir", str(raw), "--outdir", str(o)]) == 0
    names = sorted(x.name for x in out1.iterdir())
    assert names == ["physical_daily_vertical.csv", "physical_manifest.json", "physical_monthly_vertical.csv"]
    for n in names:
        assert (out1 / n).read_bytes() == (out2 / n).read_bytes()
    man = json.loads((out1 / "physical_manifest.json").read_text(encoding="utf-8"))
    for n in ("physical_daily_vertical.csv", "physical_monthly_vertical.csv"):
        data = (out1 / n).read_bytes()
        assert man["outputs"][n] == {"rows": data.count(b"\n") - 1, "sha256": hashlib.sha256(data).hexdigest()}
        assert b"\r" not in data
    assert set(man["inputs"]) == {"weather", "co2", "global-temp"} and man["inputs"]["co2"]["url"] == fp.raw_url(pins["co2"])
    s = physical_gen.read_series(out1 / "physical_daily_vertical.csv", "physical:", "day")
    assert len(s) == 4 and all(len(v) == 2 for v in s.values())
    s = physical_gen.read_series(out1 / "physical_monthly_vertical.csv", "physical:", "month")
    assert len(s) == 4 and sorted(len(v) for v in s.values()) == [1, 2, 2, 2]


def test_download_writes_only_files_whose_hash_matches_and_asks_the_pinned_urls(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    pins = fixture_pins(tmp_path / "src")
    bodies = {fp.raw_url(pins[n]): t.encode("utf-8") for n, t in (("weather", WEATHER), ("co2", CO2), ("global-temp", GT))}
    asked = []

    class Resp:
        def __init__(self, data):
            self.data = data

        def read(self):
            return self.data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_open(url, timeout=None):
        asked.append(url)
        return Resp(bodies[url])
    monkeypatch.setattr(fp.urllib.request, "urlopen", fake_open)
    dest = tmp_path / "dl"
    fp.download(dest, pins)
    assert asked == [fp.raw_url(p) for p in pins.values()] and sorted(x.name for x in dest.iterdir()) == ["co2.csv", "global-temp.csv", "weather.csv"]
    bodies[fp.raw_url(pins["co2"])] = b"tampered"
    dest2 = tmp_path / "dl2"
    with pytest.raises(ValueError, match="co2: sha256 が固定した値と違う"):
        fp.download(dest2, pins)
    assert (dest2 / "weather.csv").exists() and not (dest2 / "co2.csv").exists() and not (dest2 / "global-temp.csv").exists()


def test_the_real_pins_are_well_formed():
    assert set(fp.PINS) == {"weather", "co2", "global-temp"}
    for name, p in fp.PINS.items():
        assert re.fullmatch(r"[0-9a-f]{40}", p["commit"]) and re.fullmatch(r"[0-9a-f]{64}", p["sha256"]), name
        assert p["license"] and p["origin"] and p["path"].startswith("data/") and "/" in p["repo"]
        assert fp.raw_url(p) == f"https://raw.githubusercontent.com/{p['repo']}/{p['commit']}/{p['path']}"
        assert fp.source_text(p) == f"https://github.com/{p['repo']}@{p['commit'][:7]} ({p['path']})"
    assert fp.PINS["weather"]["commit"] == fp.PINS["co2"]["commit"]


# ---- 事後: 値の単位と絶対値の許容（eps_posthoc.py の scale_tolerance。旧 posthoc_scale_tolerance.py）------------------------------------------------------------
def synth_window(sid, i):
    spec = next(x for x in physical_gen.SYNTH if x["id"] == sid)
    return {"key": "k", "start": "2020-01", "values": physical_gen.synth_series(spec, i)}


def test_posthoc_unscaled_tolerance_moves_the_form_at_a_small_scale_and_a_scaled_tolerance_does_not():
    bases = physical_gen.make_bases(physical_sa, physical_trial, [i / 23 for i in range(24)])
    wins = [synth_window("undamped_p1", 7), synth_window("damped_l1", 10)]       # 探して固定した窓（倍率 1e-6 で式が動く）
    old_tie = physical_sa.EPS_WAVE_TIE
    for scale_tie, want_changed in ((False, 2), (True, 0)):
        with physical_ph.patched(physical_gen, physical_sa, (1e-6, 1.0), scale_tie):
            out = physical_gen.scale_summary(physical_sa, bases, wins)
        assert out["1"]["forms_changed"] == 0 and out["1e-06"]["forms_changed"] == want_changed, scale_tie
        if scale_tie:
            assert out["1e-06"]["boundary_flag_changed"] == 0 and out["1e-06"]["coefficient_max_dev"] < 1e-9
    assert physical_sa.EPS_WAVE_TIE == old_tie == physical_ph.TIE


def test_posthoc_analyse_runs_the_unchanged_tolerance_first_and_the_scaled_one_second():
    series = {("k", f"physical:{i}", "u", "s", ""): {j: v for j, v in enumerate(synth_window(sid, k)["values"])}
              for i, (sid, k) in enumerate((("undamped_p1", 7), ("damped_l1", 10)))}
    res = physical_ph.scale_tolerance_analyse(physical_gen, physical_sa, physical_trial, series, "month")
    assert res["windows"] == 2 and res["n"] == 24
    assert res["tolerance_unchanged"]["1e-06"]["forms_changed"] == 2 and res["tolerance_scaled"]["1e-06"]["forms_changed"] == 0
    assert res["tolerance_unchanged"]["1"] == res["tolerance_scaled"]["1"]


def test_posthoc_patched_restores_everything_even_when_the_body_fails():
    old = (physical_gen.SCALES, physical_gen.fit_row, physical_sa.EPS_WAVE_TIE)
    with pytest.raises(RuntimeError):
        with physical_ph.patched(physical_gen, physical_sa, (0.5, 1.0), True):
            assert physical_gen.SCALES == (0.5, 1.0) and physical_gen.fit_row is not old[1]
            raise RuntimeError("x")
    assert (physical_gen.SCALES, physical_gen.fit_row, physical_sa.EPS_WAVE_TIE) == old


def test_posthoc_patched_multiplies_the_tolerance_by_the_square_of_the_scale_only_while_fitting(monkeypatch):
    seen = []
    monkeypatch.setattr(physical_gen, "fit_row", lambda sa_, b, ys, tau: seen.append((tau, sa_.EPS_WAVE_TIE)) or {"x": 1})
    for scale_tie in (True, False):
        seen.clear()
        with physical_ph.patched(physical_gen, physical_sa, physical_gen.SCALES, scale_tie):
            for f in (1e-3, 1.0, 1e3):
                assert physical_gen.fit_row(physical_sa, None, [0.0], physical_gen.PRIMARY_TAU * f) == {"x": 1}
                assert physical_sa.EPS_WAVE_TIE == physical_ph.TIE                       # 当てはめの外では元の値
        want = [physical_ph.TIE * f * f if scale_tie else physical_ph.TIE for f in (1e-3, 1.0, 1e3)]
        assert [t for _, t in seen] == pytest.approx(want, rel=1e-9)
    assert physical_sa.EPS_WAVE_TIE == physical_ph.TIE and physical_gen.fit_row is not None


def test_posthoc_cli_writes_both_variants_for_both_cadences_and_is_reproducible(tmp_path):
    monthly = physical_write_rows(tmp_path / "m.csv", [dict(r, date=f"{2000 + i // 12}-{i % 12 + 1:02d}-01", variable="physical:temp_anomaly", note="GCAG")
                                               for i, r in enumerate(vrows(48, values=physical_wave(48, 0.2)))])
    daily = physical_write_rows(tmp_path / "d.csv", vrows(48, values=physical_wave(48, 0.5)))
    outs = []
    for name in ("a", "b"):
        o = tmp_path / name
        assert physical_ph.scale_tolerance(["--monthly-csv", str(monthly), "--daily-csv", str(daily), "--outdir", str(o), "--repo", str(ROOT)]) == 0
        outs.append(o)
    for n in ("posthoc_scale_tolerance.json", "posthoc_scale_tolerance.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes()
    res = json.loads((outs[0] / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))
    assert set(res) == {"monthly", "daily"} and all(res[k]["windows"] == 2 and res[k]["n"] == 24 for k in res)
    for k in res:
        for name in ("tolerance_unchanged", "tolerance_scaled"):
            assert list(res[k][name]) == ["1e-08", "1e-07", "1e-06", "1e-05", "0.0001", "0.001", "0.01", "1"]
            assert res[k][name]["1"]["forms_changed"] == 0 and res[k][name]["1"]["units"] == 2
    md = (outs[0] / "posthoc_scale_tolerance.md").read_text(encoding="utf-8")
    assert "## 月次（24 点の窓 2 個）" in md and "## 日次（24 点の窓 2 個）" in md and md.count("許容に倍率の2乗をかけた") == 2
    assert physical_gen.SCALES == (1e-6, 1e-3, 1.0, 1e3, 1e6) and physical_sa.EPS_WAVE_TIE == physical_ph.TIE                      # 呼んだあとも元のまま


def test_posthoc_states_its_prediction_before_the_run_and_the_fine_scales():
    doc = physical_ph.SCALE_TOLERANCE_DOC
    assert "予想（走らせる前に書く）" in doc and "(a)" in doc and "(b)" in doc and "EPS_WAVE_SOLVE" in doc
    assert physical_ph.FINE == (1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1.0) and physical_ph.TIE == 1e-12


def staple_csv(path, n=48, phase=0.3):
    rows = [dict(r, date=f"{2000 + i // 12}-{i % 12 + 1:02d}-01", variable="staple_price:rice", country="AAA", note="", unit="USD per kg")
            for i, r in enumerate(vrows(n, values=physical_wave(n, phase)))]
    return physical_write_rows(path, rows)


def test_posthoc_cli_takes_the_staple_input_alone_and_writes_only_that_kind_and_is_reproducible(tmp_path):
    staple = staple_csv(tmp_path / "s.csv")
    outs = []
    for name in ("a", "b"):
        o = tmp_path / name
        assert physical_ph.scale_tolerance(["--staple-csv", str(staple), "--outdir", str(o), "--repo", str(ROOT)]) == 0
        outs.append(o)
    for n in ("posthoc_scale_tolerance.json", "posthoc_scale_tolerance.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes()
    res = json.loads((outs[0] / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))
    assert list(res) == ["staple"] and res["staple"]["windows"] == 2 and res["staple"]["n"] == 24
    for name in ("tolerance_unchanged", "tolerance_scaled"):
        assert list(res["staple"][name]) == ["1e-08", "1e-07", "1e-06", "1e-05", "0.0001", "0.001", "0.01", "1"]
        assert res["staple"][name]["1"]["units"] == 2 and res["staple"][name]["1"]["forms_changed"] == 0
    md = (outs[0] / "posthoc_scale_tolerance.md").read_text(encoding="utf-8")
    assert "## 主食価格の月次（24 点の窓 2 個）" in md and "## 月次（" not in md and "## 日次（" not in md
    assert md.count("許容に倍率の2乗をかけた") == 1 and physical_gen.SCALES == (1e-6, 1e-3, 1.0, 1e3, 1e6) and physical_sa.EPS_WAVE_TIE == physical_ph.TIE


def test_posthoc_cli_with_all_three_inputs_keeps_the_order_monthly_daily_staple(tmp_path):
    monthly = physical_write_rows(tmp_path / "m.csv", [dict(r, date=f"{2000 + i // 12}-{i % 12 + 1:02d}-01", variable="physical:temp_anomaly", note="GCAG")
                                               for i, r in enumerate(vrows(48, values=physical_wave(48, 0.2)))])
    daily = physical_write_rows(tmp_path / "d.csv", vrows(48, values=physical_wave(48, 0.5)))
    staple = staple_csv(tmp_path / "s.csv")
    o = tmp_path / "o"
    assert physical_ph.scale_tolerance(["--staple-csv", str(staple), "--daily-csv", str(daily), "--monthly-csv", str(monthly), "--outdir", str(o), "--repo", str(ROOT)]) == 0
    res = json.loads((o / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))
    assert list(res) == ["monthly", "daily", "staple"]
    md = (o / "posthoc_scale_tolerance.md").read_text(encoding="utf-8")
    assert [md.index(h) for h in ("## 月次（", "## 日次（", "## 主食価格の月次（")] == sorted(md.index(h) for h in ("## 月次（", "## 日次（", "## 主食価格の月次（"))


def test_posthoc_cli_stops_when_no_input_is_given(tmp_path):
    with pytest.raises(SystemExit) as e:
        physical_ph.scale_tolerance(["--outdir", str(tmp_path / "o"), "--repo", str(ROOT)])
    assert e.value.code == 2 and not (tmp_path / "o").exists()


def test_posthoc_states_the_staple_prediction_before_the_run_and_what_was_already_seen():
    doc = physical_ph.SCALE_TOLERANCE_DOC
    assert "追記（2026-10-27。主食価格の月次に広げる。**走らせる前に書く**" in doc
    for needle in ("すでに見たもの", "まだ見ていないもの", "(a')", "(b')", "2104", "1056", "381", "3.83e-22", "8.52e-4"):
        assert needle in doc, needle
    assert [k for k, _, _ in physical_ph.KINDS] == ["monthly", "daily", "staple"] and physical_ph.KINDS[2][2] == "staple"


def staple_scale_result():
    return json.loads((DIR / "results-random" / "staple" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))


def test_staple_scale_result_follows_the_written_predictions_and_the_md_is_what_render_makes():
    res = staple_scale_result()
    assert list(res) == ["staple"] and res["staple"]["windows"] == 2212 and res["staple"]["n"] == 24
    u, sc = res["staple"]["tolerance_unchanged"], res["staple"]["tolerance_scaled"]
    assert list(u) == list(sc) == ["1e-08", "1e-07", "1e-06", "1e-05", "0.0001", "0.001", "0.01", "1"]
    changed = [u[k]["forms_changed"] for k in u]
    assert all(a >= b for a, b in zip(changed, changed[1:]))                          # (a') 倍率を大きくしていくと、増えない
    assert all(u[k]["forms_changed"] == 0 for k in ("0.001", "0.01", "1"))              # (a') 1e-3 以上では 0
    assert (u["1e-06"]["forms_changed"], u["1e-06"]["boundary"]) == (1056, 381)         # (a') 第 3 回と同じ
    for k, v in sc.items():                                                             # (b') 許容に倍率の2乗をかけると、どの倍率でも動かない
        assert v["forms_changed"] == 0 and v["boundary_flag_changed"] == 0 and v["coefficient_max_dev"] < 1e-9, k
    md = (DIR / "results-random" / "staple" / "posthoc_scale_tolerance.md").read_text(encoding="utf-8")
    assert md == physical_ph.scale_tolerance_render(res).replace("](../eps_posthoc.py)", "](../../eps_posthoc.py)")      # 置き場所が 1 階層深いリンクの 1 か所だけ違う


def test_staple_scale_result_tables_in_the_readmes_are_the_json_numbers():
    res = staple_scale_result()["staple"]
    u, sc = res["tolerance_unchanged"], res["tolerance_scaled"]
    text = (DIR / "results-random" / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("### 主食価格で、倍率の境目を細かく見た確認"):]
    sec = sec[:sec.index("## ε が動いた範囲")]
    for k in u:
        row = f"| {k} | {u[k]['boundary']} | {u[k]['forms_changed']} | {u[k]['boundary_flag_changed']} | {sc[k]['forms_changed']} | {sc[k]['boundary_flag_changed']} |"
        assert row in sec, row
    assert " → ".join(str(u[k]["forms_changed"]) for k in u) in sec
    main = (DIR / "README.md").read_text(encoding="utf-8")
    assert "2104 → 2103 → 1056（1e-6。第 3 回と同じ）→ 16（1e-5）→ 0" in main and (u["1e-05"]["forms_changed"], u["1e-07"]["forms_changed"]) == (16, 2103)


# ---- README の登録内容との一致 --------------------------------------------------------------------------------------------
def test_readme_announces_the_staple_scale_check_before_it_runs_and_points_to_the_prediction():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("#### 主食価格にも当てる（2026-10-27。**走らせる前に書く**）"):]
    sec = sec[:sec.index("### 再現と置き場所")]
    for needle in ("eps_posthoc.py scale_tolerance` の冒頭に書いた", "(a')", "(b')", "1056", "--staple-csv research/staple-price-survey/staple_survey_vertical.csv",
                   "results-random/staple/posthoc_scale_tolerance.json", "PR #24 は触らない"):
        assert needle in sec, needle


def test_readme_physical_section_states_the_pinned_inputs_the_scales_and_the_profiles():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("## 物理量の確認（第 2 回）: 事前登録"):]
    for p in fp.PINS.values():
        for needle in (p["commit"], p["sha256"], p["path"], p["repo"]):
            assert needle in sec, needle
    for needle in ("SCALES = (1e-6, 1e-3, 1, 1e3, 1e6)", "`physical-monthly`", "`physical-daily`", "444 / 221 / 110", "968 / 480 / 240",
                   "13 / 2 / 0", "5,353 行", "11,688 行", "4f18c60d52e26f1ec84496619ee2aa656ae0e3994373064c8be78fd150ceefc9",
                   "1d1ea18b501abc473a9e27bc388a0433fb89551bbbcef396648c15f41caa9824", "tests/test_epsilon_generality.py",
                   "基準は置かず、報告だけ", "矛盾する材料はなかった", "約 18% 未満", "results-physical/", "eps_posthoc.py scale_tolerance",
                   "走らせる前に", "EPS_WAVE_SOLVE", "直し方"):
        assert needle in sec, needle
    assert "98% 以上" in sec and "20 未満" in sec
    assert physical_gen.CRIT["c1_eps3"] == 0.98 and physical_gen.MIN_UNITS == 20                               # 第 1 回と同じ値のまま


# ==== posthoc（旧 test_epsilon_generality_posthoc.py）
# research/epsilon-generality/eps_posthoc.py（旧 posthoc_boundary_forms.py）の確認。
#
# SYNTHETIC: 小さな合成の入力で、周期が変わった単位の数え方・単式の誤差の2乗和・除いたときの係数のずれ・書き出しを確かめる。
# 野球の周期の数だけ、リポジトリに保存済みの行（wave_eps_rows_1e-06.jsonl）と照らす。結論には使わない。


posthoc_ph = importlib.util.module_from_spec(spec)
sys.modules["eps_posthoc"] = posthoc_ph
spec.loader.exec_module(posthoc_ph)
posthoc_gen = posthoc_ph.gen
posthoc_sa, posthoc_trial = posthoc_gen.load_modules(ROOT)
K3, K6, K9 = (posthoc_gen.ekey(e) for e in posthoc_gen.EPS)


def posthoc_er(period=1.0, coef=1.0):
    return {"decay": 0.0, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": False}


def posthoc_row(boundary=True, p3=1.0, p6=1.0, p9=1.0, c3=1.0, c6=1.0, c9=1.0):
    return {"boundary": boundary, K3: posthoc_er(p3, c3), K6: posthoc_er(p6, c6), K9: posthoc_er(p9, c9)}


def test_changed_period_lists_only_boundary_units_whose_period_differs_from_the_1e9_one():
    rows = [posthoc_row(), posthoc_row(p3=2.0), posthoc_row(p6=0.5), posthoc_row(False, p3=2.0), posthoc_row(p3=2.0, p6=2.0)]
    assert posthoc_ph.changed_period(rows) == {K3: [1, 4], K6: [2, 4]}
    assert posthoc_ph.changed_period([posthoc_row()]) == {K3: [], K6: []}


def test_corrected_c2_drops_the_skipped_units_and_divides_by_the_1e9_coefficient():
    rows = [posthoc_row(), posthoc_row(c3=1.5, c6=1.0001), posthoc_row(c3=1.002, c6=1.0), posthoc_row(False, c3=9.0), posthoc_row(c3=None)]
    rows[4][K3]["coefficient"] = None
    full = posthoc_ph.corrected_c2(rows, set())
    assert full[K3]["n"] == 3 and full[K3]["max"] == pytest.approx(0.5) and full[K6]["max"] == pytest.approx(1e-4)
    skipped = posthoc_ph.corrected_c2(rows, {1})
    assert skipped[K3] == {"max": pytest.approx(0.002), "n": 2}
    assert posthoc_ph.corrected_c2([], set())[K3] == {"max": None, "n": 0}
    two = posthoc_ph.corrected_c2([posthoc_row(c3=1.5, c9=2.0)], set())
    assert two[K3]["max"] == pytest.approx(0.25)                    # 基準の係数（2.0）で割る


def wave_ys(period=1.0, n=24):
    xs = [i / (n - 1) for i in range(n)]
    return posthoc_gen.normalize([3.0 + 2.0 * math.cos(2 * math.pi * x / period + 0.7) for x in xs])[1]


def test_sse_of_form_is_near_zero_for_the_true_period_and_large_for_another_and_checks_the_grid():
    ys = wave_ys(1.0)
    xs = [i / 23 for i in range(24)]
    assert posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 0.0, 1.0) < 1e-9
    assert posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 1e-6, 1.0) < 1e-6
    assert posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 0.0, 2.0) > 1.0
    assert posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 1e-3, 2.0) > 1.0
    with pytest.raises(ValueError, match="格子に周期 0.6"):
        posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 0.0, 0.6)


def test_tie_table_has_one_line_per_epsilon_including_zero_and_the_difference_is_second_minus_first():
    t = posthoc_ph.tie_table(posthoc_sa, posthoc_trial, wave_ys(1.0), 1.0, 2.0)
    assert [x["eps"] for x in t] == [0.0, 1e-3, 1e-6, 1e-9]
    for x in t:
        assert x["diff"] == x["sse_other_period"] - x["sse_small_eps_period"] and x["diff"] > 1.0
    assert t[0]["sse_small_eps_period"] < 1e-9 and t[3]["sse_small_eps_period"] < 1e-6        # x は窓の長さで [0, 1] を等分した点
    flipped = posthoc_ph.tie_table(posthoc_sa, posthoc_trial, wave_ys(1.0), 2.0, 1.0)
    assert all(x["diff"] < -1.0 for x in flipped)


def test_baseball_periods_match_the_saved_rows():
    b = posthoc_ph.baseball_periods(ROOT)
    assert b == {"units": 168, "boundary": 24, "periods": {0.75: 3, 1.0: 4, 2.0: 17}}


def posthoc_small_csv(tmp_path):
    rows = []
    for j in range(3):
        vals = [3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5) for i in range(48)]
        for i, v in enumerate(vals):
            y, m = 2020 + i // 12, i % 12 + 1
            rows.append({"country": "AAA", "date": f"{y}-{m:02d}-01", "year": str(y), "variable": f"staple_price:c{j}", "value": str(v),
                         "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""})
    import csv
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return p


def test_analyse_finds_nothing_in_a_clean_series_and_builds_the_table_for_a_forced_unit(tmp_path, monkeypatch):
    series = posthoc_gen.read_series(posthoc_small_csv(tmp_path))
    res = posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)
    assert res["units"] == [] and set(res["by_n"]) == {"12", "24", "48"} and res["baseball"]["boundary"] == 24
    assert res["by_n"]["24"]["changed_period"] == {K3: 0, K6: 0}
    monkeypatch.setattr(posthoc_ph, "changed_period", lambda rows: {K3: [0], K6: []})
    forced = posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)
    (u,) = [x for x in forced["units"] if x["n"] == 12]
    assert (u["eps"], u["series_index"], u["start"], u["unit"]) == (1e-3, 0, "2020-01", "USD per kg") and len(u["table"]) == 4
    assert forced["by_n"]["12"]["changed_period"] == {K3: 1, K6: 0}
    seen = []
    real_c2 = posthoc_ph.corrected_c2
    monkeypatch.setattr(posthoc_ph, "corrected_c2", lambda rows, skip: seen.append(set(skip)) or real_c2(rows, skip))
    posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)
    assert seen == [{0}, {0}, {0}]                                           # 周期が変わった単位は、窓の長さごとに除いて測る


def test_analyse_stops_when_windows_and_rows_do_not_line_up(tmp_path, monkeypatch):
    series = posthoc_gen.read_series(posthoc_small_csv(tmp_path))
    real = posthoc_gen.compute

    def short(*a, **k):
        r = real(*a, **k)
        r["rows"]["real"]["12"] = r["rows"]["real"]["12"][:-1]
        return r
    monkeypatch.setattr(posthoc_gen, "compute", short)
    with pytest.raises(ValueError, match="窓の数が合わない"):
        posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)
    monkeypatch.setattr(posthoc_gen, "compute", real)
    monkeypatch.setattr(posthoc_ph, "changed_period", lambda rows: {K3: [1], K6: []})

    def swapped(*a, **k):
        r = real(*a, **k)
        rows = r["rows"]["real"]["12"]
        rows[1]["series_index"] = 99
        return r
    monkeypatch.setattr(posthoc_gen, "compute", swapped)
    with pytest.raises(ValueError, match="窓と行が対応しない"):
        posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)


def test_render_and_cli_write_json_and_markdown_and_are_reproducible(tmp_path, monkeypatch):
    csv_path = posthoc_small_csv(tmp_path)
    o1, o2 = tmp_path / "o1", tmp_path / "o2"
    for o in (o1, o2):
        assert posthoc_ph.boundary_forms(["--csv", str(csv_path), "--outdir", str(o), "--repo", str(ROOT)]) == 0
    for n in ("posthoc_boundary_forms.json", "posthoc_boundary_forms.md"):
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes()
    md = (o1 / "posthoc_boundary_forms.md").read_text(encoding="utf-8")
    assert "登録した基準の外" in md and "なし。" in md and "24 単位" not in md and "3: " not in md
    assert json.loads((o1 / "posthoc_boundary_forms.json").read_text(encoding="utf-8"))["baseball"]["periods"]["2.0"] == 17
    monkeypatch.setattr(posthoc_ph, "changed_period", lambda rows: {K3: [0], K6: []})
    o3 = tmp_path / "o3"
    assert posthoc_ph.boundary_forms(["--csv", str(csv_path), "--outdir", str(o3), "--repo", str(ROOT)]) == 0
    md3 = (o3 / "posthoc_boundary_forms.md").read_text(encoding="utf-8")
    assert "### 12 か月・ε=0.001: FPMA AAA staple_price:c0（USD per kg、系列 0）2020-01 から" in md3 and "| 0 |" in md3 and "1e-12" in md3


# ---- 境界でない単位で式が変わった場合 ------------------------------------------------------------------------------------
def nrow(boundary, d0, p0, e3, e6=None):
    r = {"boundary": boundary, "decay": d0, "period": p0}
    r[K3] = {"decay": e3[0], "period": e3[1]}
    r[K6] = {"decay": (e6 or (d0, p0))[0], "period": (e6 or (d0, p0))[1]}
    r[K9] = {"decay": d0, "period": p0}
    return r


def test_nonboundary_changes_counts_decay_or_period_changes_of_non_boundary_units_only():
    rows = [nrow(False, 0.5, 2.0, (0.001, 2.0)), nrow(False, 0.5, 2.0, (0.5, 1.0)), nrow(False, 0.5, 2.0, (0.5, 2.0)),
            nrow(True, 0.0, 1.0, (0.001, 1.0)), nrow(False, 1.0, None, (1.0, None), e6=(1.0, 2.0))]
    assert posthoc_ph.nonboundary_changes(rows) == {K3: [0, 1], K6: [4]}
    assert posthoc_ph.nonboundary_changes([]) == {K3: [], K6: []}


def damped_ys(lam=0.5, period=2.0, n=24):
    xs = [i / (n - 1) for i in range(n)]
    return posthoc_gen.normalize([3.0 + 2.0 * math.exp(-lam * x) * math.cos(2 * math.pi * x / period + 0.4) for x in xs])[1]


def test_sse_of_form_can_pick_a_damped_form_by_its_decay():
    ys = damped_ys()
    xs = [i / 23 for i in range(24)]
    assert posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 1e-3, 2.0, lam=0.5) < 1e-9
    assert posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 1e-3, 2.0, lam=3.0) > 0.01
    with pytest.raises(ValueError, match="格子に周期 2.0・減衰 0.7"):
        posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 1e-3, 2.0, lam=0.7)
    with pytest.raises(ValueError, match="減衰 0.0 の式が 0 個"):
        posthoc_ph.sse_of_form(posthoc_sa, posthoc_trial, xs, ys, 1e-3, 2.0, lam=0.0)             # ε の格子には減衰 0 の式がない


def test_form_table_lists_the_current_form_the_undamped_one_and_each_epsilon_wave():
    t = posthoc_ph.form_table(posthoc_sa, posthoc_trial, damped_ys(), (0.5, 2.0), 1e-3, 2.0)
    assert [x["label"] for x in t] == ["今のコードで選ばれた式", "同じ周期の減衰しない波（減衰 0）", "同じ周期の ε の波（ε=0.001）",
                                       "同じ周期の ε の波（ε=1e-06）", "同じ周期の ε の波（ε=1e-09）"]
    assert [(x["decay"], x["period"]) for x in t] == [(0.5, 2.0), (0.0, 2.0), (1e-3, 2.0), (1e-6, 2.0), (1e-9, 2.0)]
    assert t[0]["sse"] < 1e-9 and all(x["sse"] > 1e-3 for x in t[1:])
    d3, d6, d9 = (abs(t[i]["sse"] - t[1]["sse"]) for i in (2, 3, 4))          # ε が小さいほど、減衰しない波の誤差に近づく（ε にほぼ比例）
    assert d3 > 1e-7 and 0 < d6 < 2e-3 * d3 and d9 < 2e-3 * d6


def test_analyse_builds_the_table_for_a_non_boundary_unit_whose_form_changed(tmp_path, monkeypatch):
    series = posthoc_gen.read_series(posthoc_small_csv(tmp_path))
    real = posthoc_gen.compute
    seen = {}

    def forced(*a, **k):
        r = real(*a, **k)
        row0 = r["rows"]["real"]["12"][0]
        seen["eps_period"] = row0[K3]["period"]
        seen["p"] = 0.25 if row0[K3]["period"] != 0.25 else 0.5
        row0["boundary"], row0["decay"], row0["period"] = False, 0.5, seen["p"]          # 今のコードは減衰 0.5 の式を選んだことにする
        row0[K6] = {"decay": 0.5, "period": seen["p"]}                                  # ε=1e-6 では変わらなかったことにする
        return r
    monkeypatch.setattr(posthoc_gen, "compute", forced)
    res = posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)
    (u,) = res["nonboundary_units"]
    p, ep = seen["p"], seen["eps_period"]
    assert (u["n"], u["eps"], u["unmodified"], u["epsilon_form"]) == (12, 1e-3, [0.5, p], [1e-3, ep])
    assert [x["period"] for x in u["table"]] == [p, ep, ep, ep, ep] and len(u["table"]) == 5
    assert u["series_index"] == 0 and u["start"] == "2020-01"
    assert res["by_n"]["12"]["nonboundary_changed"] == {K3: 1, K6: 0} and res["by_n"]["24"]["nonboundary_changed"] == {K3: 0, K6: 0}
    md = posthoc_ph.boundary_forms_render(res)
    assert "12 か月: 1 / 0、24 か月: 0 / 0、48 か月: 0 / 0" in md and "今のコードの式は 減衰 0.5・周期 " + format(p, "g") + "、" in md
    assert "同じ周期の減衰しない波（減衰 0）" in md and "ε の格子では 減衰 0.001・周期 " + format(ep, "g") in md
    # 窓と行が対応しないときは止まる
    def swapped(*a, **k):
        r = forced(*a, **k)
        r["rows"]["real"]["12"][0]["series_index"] = 99
        return r
    monkeypatch.setattr(posthoc_gen, "compute", swapped)
    with pytest.raises(ValueError, match="窓と行が対応しない"):
        posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, series, ROOT)


def test_render_without_changes_says_none_in_both_sections(tmp_path):
    res = posthoc_ph.boundary_forms_analyse(posthoc_sa, posthoc_trial, posthoc_gen.read_series(posthoc_small_csv(tmp_path)), ROOT)
    assert posthoc_ph.boundary_forms_render(res).count("なし。") == 2


# ==== random（旧 test_epsilon_generality_random.py）
# research/epsilon-generality/eps_generality.py の「乱数の ε と倍率」の確認。
#
# SYNTHETIC: 合成の入力で、乱数の選び方（A×10^-N の形・範囲・種で決まること）、基準値のつなぎ方、乱数の ε を足したときの判定と書き出しを確かめる。
# 結論には使わない。
#
# 乱数の種: 環境変数 EPS_COEF_SEED（省略すると実行ごとに変わる）。失敗したときは、メッセージの EPS_COEF_SEED=... を渡せば同じ値で再現する。
# どの種でも成り立つ性質だけを確かめている（種によって通ったり落ちたりする確認は置かない）。


random_spec = importlib.util.spec_from_file_location("eps_generality", DIR / "eps_generality.py")
random_gen = importlib.util.module_from_spec(random_spec)
sys.modules["eps_generality"] = random_gen
random_spec.loader.exec_module(random_gen)
random_sa, random_trial = random_gen.load_modules(ROOT)

COEF_SEED = os.environ.get("EPS_COEF_SEED") or str(secrets.randbelow(10**9))
WHY = f"EPS_COEF_SEED={COEF_SEED}"
SEEDS = (COEF_SEED, "1", "2", "20261026")          # 乱数の種（先頭だけ実行ごとに変わる）


# ---- 乱数の選び方 ----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("seed", SEEDS)
def test_random_eps_are_A_times_power_of_ten_with_three_digits_and_N_from_3(seed):
    d = random_gen.draw_coefficients(6, seed, "eps")
    assert len(d) == 6 and len({x["value"] for x in d}) == 6, WHY
    for x in d:
        assert 1.0 <= x["a"] <= 9.99 and abs(x["a"] * 100 - round(x["a"] * 100)) < 1e-9, WHY            # A は 1.00〜9.99（小数第 2 位まで）
        assert -307 <= x["exp"] <= -3 and x["value"] == float(f"{x['a']:.2f}e{x['exp']}"), WHY
        assert 0 < x["value"] <= 1e-2 and x["value"] not in random_gen.EPS and math.isfinite(x["value"]), WHY     # ε の条件は 0 < ε ≤ 1/100 だけ
    assert [x["value"] for x in d] == sorted((x["value"] for x in d), reverse=True), WHY


@pytest.mark.parametrize("seed", SEEDS)
def test_random_scales_are_A_times_power_of_ten_on_both_sides_of_one(seed):
    d = random_gen.draw_coefficients(8, seed, "scale")
    assert len(d) == 8 and len({x["value"] for x in d}) == 8, WHY
    for x in d:
        assert 1.0 <= x["a"] <= 9.99 and abs(x["a"] * 100 - round(x["a"] * 100)) < 1e-9, WHY
        assert abs(x["exp"]) <= 150 and x["value"] == float(f"{x['a']:.2f}e{x['exp']}") and x["value"] not in random_gen.SCALES, WHY
        assert 0 < x["value"] < math.inf, WHY


def test_draws_depend_only_on_the_seed_and_the_kind():
    a = random_gen.draw_coefficients(6, 7, "eps")
    assert a == random_gen.draw_coefficients(6, 7, "eps") and a != random_gen.draw_coefficients(6, 8, "eps")
    assert random_gen.draw_coefficients(6, 7, "eps") != random_gen.draw_coefficients(6, 7, "scale")
    assert random_gen.draw_coefficients(6, "7", "eps") == a                          # 整数でも文字列でも同じ種
    assert random_gen.draw_coefficients(0, 7, "eps") == []


def test_draws_are_not_a_grid_and_N_has_no_upper_bound_in_practice():
    seen_a, seen_exp, seen_scale = set(), set(), set()
    for seed in range(1, 41):
        for x in random_gen.draw_coefficients(6, seed, "eps"):
            seen_a.add(x["a"])
            seen_exp.add(x["exp"])
        seen_scale.update(x["exp"] for x in random_gen.draw_coefficients(6, seed, "scale"))
    assert len(seen_a) > 100 and -3 in seen_exp, "A が 1 つの値に偏らず、N = 3 も選ばれる"
    assert min(seen_exp) <= -20 and len({-e for e in seen_exp if e % 3}) >= 5, "N は 8 で切れず、3 刻みにも偏らない"
    assert min(seen_scale) < 0 < max(seen_scale), "倍率の指数は 0 の両側に出る"


def test_the_ends_of_A_and_N_can_be_drawn(monkeypatch):
    monkeypatch.setattr(random_gen, "A_MIN", 999)
    monkeypatch.setattr(random_gen, "P_STOP", 1.0)                                      # N = 3 で止まる
    assert [(x["a"], x["exp"], x["value"]) for x in random_gen.draw_coefficients(1, 1, "eps")] == [(9.99, -3, 9.99e-3)]
    monkeypatch.setattr(random_gen, "A_MIN", 100)
    monkeypatch.setattr(random_gen, "A_MAX", 100)
    monkeypatch.setattr(random_gen, "P_STOP", 0.0)                                      # 上限まで行く
    (x,) = random_gen.draw_coefficients(1, 1, "eps")
    assert (x["a"], x["exp"]) == (1.0, -random_gen.N_CAP) and x["value"] == float(f"1.00e-{random_gen.N_CAP}") > 0
    (y,) = random_gen.draw_coefficients(1, 1, "scale")
    assert y["a"] == 1.0 and abs(y["exp"]) == random_gen.E_CAP


def test_the_caps_are_where_float_stops_carrying_three_digits():
    assert float(f"1.00e-{random_gen.N_CAP}") >= sys.float_info.min > float(f"1.00e-{random_gen.N_CAP + 1}")      # N_CAP の次から A の 3 桁を保てない
    sse = lambda e: 48 * (5 * 9.99 * 10.0 ** e) * (5 * 9.99 * 10.0 ** e)                   # 48 点・y の幅 5 に倍率 9.99×10^e をかけた 2 乗の和
    assert sse(random_gen.E_CAP) < sys.float_info.max and sse(random_gen.E_CAP + 3) == math.inf


def test_asking_for_more_values_than_can_be_drawn_stops(monkeypatch):
    monkeypatch.setattr(random_gen, "A_MIN", 100)
    monkeypatch.setattr(random_gen, "A_MAX", 100)
    monkeypatch.setattr(random_gen, "N_CAP", 4)                                         # 選べるのは 1.00e-4 の 1 つだけ（1e-3 は決め打ち）
    assert [x["value"] for x in random_gen.draw_coefficients(1, 1, "eps")] == [1e-4]
    with pytest.raises(ValueError, match="2 個は選べない"):
        random_gen.draw_coefficients(2, 1, "eps")


def test_labels_show_A_times_power_of_ten_and_keep_the_registered_spelling():
    assert random_gen.pow10_text(3.07e-5) == "3.07×10^-5" and random_gen.pow10_text(9.99e-4) == "9.99×10^-4" and random_gen.pow10_text(1.1e-8) == "1.10×10^-8"
    assert random_gen.pow10_text(float("4.20e0")) == "4.20×10^0" and random_gen.pow10_text(float("1.00e-307")) == "1.00×10^-307"
    assert [random_gen.elabel(e) for e in random_gen.EPS] == ["0.001", "1e-06", "1e-09"] and random_gen.elabel(2.57e-7) == "2.57×10^-7"


# ---- 基準値のつなぎ方 --------------------------------------------------------------------------------------------------------
def test_registered_epsilons_keep_their_registered_thresholds():
    assert [random_gen.threshold("c1", e) for e in random_gen.EPS] == [0.98, 1.0, 1.0]
    assert [random_gen.threshold("c2", e) for e in random_gen.EPS[:2]] == [0.02, 1e-4]
    assert [random_gen.threshold("c3", e) for e in random_gen.EPS] == [0.02, 0.005, 0.005]


def test_thresholds_between_the_registered_points_follow_log10_eps():
    mid = 10 ** -4.5
    assert random_gen.threshold("c1", mid) == pytest.approx(0.99)                        # 割合の直線: 1.0 と 0.98 の中間
    assert random_gen.threshold("c2", mid) == pytest.approx(math.sqrt(0.02 * 1e-4))      # 値の対数の直線: 幾何平均
    assert random_gen.threshold("c3", mid) == pytest.approx(math.sqrt(0.02 * 0.005))
    f = (math.log10(2.5e-5) + 6) / 3
    assert random_gen.threshold("c2", 2.5e-5) == pytest.approx(1e-4 * (0.02 / 1e-4) ** f)
    assert random_gen.threshold("c3", 2.5e-5) == pytest.approx(0.005 * (0.02 / 0.005) ** f)
    assert random_gen.threshold("c1", 2.5e-5) == pytest.approx(1.0 + (0.98 - 1.0) * f)
    for e in (5e-7, 1.1e-8, 9.9e-7, 1e-9, 6.29e-11, 1e-100, 1e-307, 5e-324):          # 1e-6 以下は、どんな float でも 1e-6 の値のまま
        assert (random_gen.threshold("c1", e), random_gen.threshold("c2", e), random_gen.threshold("c3", e)) == (1.0, 1e-4, 0.005)


def test_thresholds_above_1e_3_extend_the_same_line_up_to_one_hundredth():
    f = (math.log10(5e-3) + 6) / 3                                                # 1.2333...（1e-3 で 1、1/100 で 4/3）
    assert random_gen.threshold("c1", 5e-3) == pytest.approx(1.0 + (0.98 - 1.0) * f) and random_gen.threshold("c1", 5e-3) < 0.98
    assert random_gen.threshold("c2", 5e-3) == pytest.approx(1e-4 * (0.02 / 1e-4) ** f) and random_gen.threshold("c2", 5e-3) > 0.02
    assert random_gen.threshold("c3", 5e-3) == pytest.approx(0.005 * (0.02 / 0.005) ** f) and random_gen.threshold("c3", 5e-3) > 0.02
    top = (random_gen.threshold("c1", 1e-2), random_gen.threshold("c2", 1e-2), random_gen.threshold("c3", 1e-2))                   # 1/100 ちょうども通る
    assert top == pytest.approx((1.0 - 0.02 * 4 / 3, 1e-4 * 200 ** (4 / 3), 0.005 * 4 ** (4 / 3)))
    ladder = [2e-3, 3e-3, 5e-3, 8e-3, 9.99e-3, 1e-2]
    assert [random_gen.threshold("c1", e) for e in ladder] == sorted((random_gen.threshold("c1", e) for e in ladder), reverse=True)
    assert [random_gen.threshold("c2", e) for e in ladder] == sorted(random_gen.threshold("c2", e) for e in ladder)


@pytest.mark.parametrize("seed", SEEDS)
def test_thresholds_of_drawn_epsilons_are_between_the_registered_ones_or_looser_above_1e_3(seed):
    es = sorted([x["value"] for x in random_gen.draw_coefficients(20, seed, "eps")] + [2.5e-3, 1e-2])
    for kind, lo, hi in (("c1", 1.0, 0.98), ("c2", 1e-4, 0.02), ("c3", 0.005, 0.02)):
        t = [random_gen.threshold(kind, e) for e in es]
        inside = [x for e, x in zip(es, t) if e <= 1e-3]
        beyond = [x for e, x in zip(es, t) if e > 1e-3]
        assert all(min(lo, hi) <= x <= max(lo, hi) for x in inside) and beyond, (kind, WHY)
        assert all((x < hi) if kind == "c1" else (x > hi) for x in beyond), (kind, WHY)        # 1e-3 より大きい側は、1e-3 の基準より緩い
        assert t == sorted(t, reverse=(kind == "c1")), (kind, WHY)               # ε が大きいほど許す幅が広い（C1 は必要な割合が下がる）


def test_thresholds_outside_the_condition_stop():
    for bad in (1.0000001e-2, 0.5, 1.0, 0.0, -1e-3):
        with pytest.raises(ValueError, match="0 < ε ≤ 1/100"):
            random_gen.threshold("c3", bad)
    random_gen.threshold("c3", 1e-2)                                                    # 1/100 ちょうどは通る
    with pytest.raises(ValueError):
        random_gen.threshold("c2", 2e-2)


# ---- 判定に乱数の ε を入れる -------------------------------------------------------------------------------------------------
def random_er(decay, period=1.0, coef=1.0, at_start=False, settle_x=1.0):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": settle_x, "coefficient": coef, "at_start": at_start}


def random_unit(eps, boundary=True, overrides=None):
    u = {"decay": 0.0 if boundary else 1.0, "period": 1.0, "rmse": 0.0, "limit": None, "settle_x": None, "boundary": boundary}
    for e in eps:
        u[random_gen.ekey(e)] = random_er(e if boundary else 1.0)
    for k, v in (overrides or {}).items():
        u[k] = random_er(**v)
    return u


def judged(rows, eps):
    return random_gen.judge_real(random_gen.stats(rows, eps), "t", eps)


def one(v, cid, e):
    (c,) = [c for c in v if c["id"] == cid and f"ε={random_gen.elabel(e)} " in c["text"]]            # どの基準の文でも ε の表記のあとに空白が来る
    return c


def drawn_eps(seed=COEF_SEED, k=6):
    return random_gen.EPS + tuple(x["value"] for x in random_gen.draw_coefficients(k, seed, "eps"))


def test_every_epsilon_gets_a_row_in_each_criterion_and_clean_data_passes_all():
    eps = drawn_eps()
    v = judged([random_unit(eps) for _ in range(30)] + [random_unit(eps, False) for _ in range(30)], eps)
    assert [c["id"] for c in v].count("C1") == 9 and [c["id"] for c in v].count("C2") == 8 and [c["id"] for c in v].count("C3") == 9, WHY
    assert all(c["ok"] is True for c in v), WHY
    assert len(judged([random_unit(random_gen.EPS) for _ in range(30)] + [random_unit(random_gen.EPS, False) for _ in range(30)], random_gen.EPS)) == 8      # 決め打ちだけなら従来どおり 8 行


def test_c2_for_a_drawn_epsilon_is_inclusive_at_its_own_threshold_on_both_sides():
    eps = drawn_eps()
    for e in eps[3:]:
        thr = random_gen.threshold("c2", e)
        for sign in (1, -1):
            def case(dev):
                rows = [random_unit(eps) for _ in range(30)] + [random_unit(eps, overrides={random_gen.ekey(e): dict(decay=e, coef=1.0 + sign * dev), random_gen.ekey(1e-9): dict(decay=1e-9, coef=1.0)})]
                return one(judged(rows, eps), "C2", e)
            assert case(thr * 0.99)["ok"] is True and case(thr * 1.01)["ok"] is False, (e, sign, WHY)
        assert one(judged([random_unit(eps) for _ in range(30)], eps), "C2", e)["threshold"] == thr


def test_c1_for_a_drawn_epsilon_needs_the_interpolated_share_and_counts_a_lost_wave():
    eps = drawn_eps()
    for e in eps[3:]:
        need = 1.0 + (0.98 - 1.0) * max(0.0, (math.log10(e) + 6) / 3)                  # 登録の 2 点を log10(ε) でつないだ式の延長（threshold とは別に書いた。1e-6 以下は 1e-6 の値）
        for lost in range(0, 4):
            rows = [random_unit(eps) for _ in range(100 - lost)] + [random_unit(eps, overrides={random_gen.ekey(e): dict(decay=1.0)}) for _ in range(lost)]
            c = one(judged(rows, eps), "C1", e)
            assert c["ok"] is (((100 - lost) / 100) >= need), (e, lost, need, WHY)
            assert c["threshold"] == pytest.approx(need), WHY


def test_c3_for_a_drawn_epsilon_counts_changed_forms_against_the_interpolated_share():
    eps = drawn_eps()
    for e in eps[3:]:
        f = max(0.0, (math.log10(e) + 6) / 3)
        thr = 0.005 * (0.02 / 0.005) ** f
        for changed in (0, 2, 5, 8, 20, 30, 40, 60):
            rows = [random_unit(eps, False) for _ in range(1000 - changed)] + [random_unit(eps, False, overrides={random_gen.ekey(e): dict(decay=2.0)}) for _ in range(changed)]
            c = one(judged(rows, eps), "C3", e)
            assert c["ok"] is ((changed / 1000) <= thr), (e, changed, thr, WHY)


def test_c1_does_not_count_a_wave_whose_settle_position_left_the_float_range():
    eps = drawn_eps(k=0) + (1.23e-12, 4.56e-3)
    for e in eps[3:]:
        lost = [dict(decay=e, settle_x=v) for v in (math.inf, math.inf, math.inf, math.nan, -math.inf)]
        rows = [random_unit(eps) for _ in range(95)] + [random_unit(eps, overrides={random_gen.ekey(e): o}) for o in lost]
        c = one(judged(rows, eps), "C1", e)
        assert c["ok"] is False and c["threshold"] > 0.95, e                       # 5 本が「残った」に入らない（95/100 は、どの ε の基準にも足りない）
        assert one(judged([random_unit(eps) for _ in range(100)], eps), "C1", e)["ok"] is True


def test_synthetic_damped_c3_also_covers_the_drawn_epsilons():
    eps = drawn_eps(k=2)
    rows = {"damped_l1": [dict(random_unit(eps, False), true_amp=2.5) for _ in range(25)], "undamped_p1": [dict(random_unit(eps), true_amp=2.5) for _ in range(25)]}
    texts = [c["text"] for c in random_gen.judge_synth(rows, eps) if c["id"] == "C3"]
    assert len(texts) == 5 and any("×10^-" in t for t in texts), WHY
    assert len(random_gen.judge_synth(rows)) == 5                                                   # 決め打ちだけなら C5 が 2 行と C3 が 3 行


# ---- 実際の当てはめ: どの乱数の ε でも、減衰しない波は ε の波が残って係数が基準の ε と合う -----------------------------------------------
def random_wave(period, phi, decay=0.0):
    xs = [i / 23 for i in range(24)]
    return [3.0 + 2.0 * math.exp(-decay * x) * math.cos(2 * math.pi * x / period + phi) for x in xs]


@pytest.mark.parametrize("seed", SEEDS)
def test_fits_with_drawn_epsilons_keep_the_wave_and_the_coefficient_for_undamped_waves_and_leave_damped_ones_alone(seed):
    eps = drawn_eps(seed)
    xs = [i / 23 for i in range(24)]
    bases = random_gen.make_bases(random_sa, random_trial, xs, eps)
    assert list(bases) == [None, *eps]
    for period, phi in ((1.0, 0.7), (0.5, 0.3), (0.25, 1.9)):
        r = random_gen.fit_row(random_sa, bases, random_gen.normalize(random_wave(period, phi))[1], 0.5)
        assert r["boundary"], WHY
        ref = r[random_gen.ekey(random_gen.REF_EPS)]["coefficient"]
        for e in eps[3:]:
            f = r[random_gen.ekey(e)]
            assert f["decay"] == e and f["limit"] is not None and f["settle_x"] is not None and not f["at_start"], (e, WHY)
            assert abs(f["coefficient"] - ref) / abs(ref) <= random_gen.threshold("c2", e), (e, WHY)
            assert f["coefficient"] == pytest.approx(f["settle_x"] * e)                  # 位置 = 係数 / ε（ε = A×10^-N なら 位置 = (係数 / A) × 10^N）
    d = random_gen.fit_row(random_sa, bases, random_gen.normalize(random_wave(0.5, 0.3, decay=3.0))[1], 0.5)
    assert not d["boundary"]
    assert all((d[random_gen.ekey(e)]["decay"], d[random_gen.ekey(e)]["period"]) == (d["decay"], d["period"]) for e in eps[3:]), WHY


def test_scale_summary_takes_the_scales_it_is_given_and_keeps_the_default():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": random_wave(1.0, p)} for p in (0.1, 0.7)]
    bases = random_gen.make_bases(random_sa, random_trial, xs)
    assert list(random_gen.scale_summary(random_sa, bases, wins, (3.07e-5, 1.0, 9.99e-120))) == ["3.07e-05", "1", "9.99e-120"]
    assert list(random_gen.scale_summary(random_sa, bases, wins)) == [f"{f:g}" for f in random_gen.SCALES]


# ---- 書き出し ----------------------------------------------------------------------------------------------------------------
def random_small_csv(tmp_path):
    import csv
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = []
    for j in range(3):
        for i in range(48):
            y, m = 2020 + i // 12, i % 12 + 1
            v = 3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)
            rows.append({"country": "AAA", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": f"staple_price:c{j}", "value": str(v),
                         "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""})
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def random_run(tmp_path, name, *flags):
    out = tmp_path / name
    assert random_gen.main(["--csv", str(random_small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT), *flags]) == 0
    return out, json.loads((out / "eps_generality.json").read_text(encoding="utf-8"))


def test_cli_adds_drawn_values_records_them_and_is_byte_reproducible(tmp_path):
    o1, r1 = random_run(tmp_path, "a", "--random-eps", "3", "--random-scales", "3", "--coef-seed", "11")
    o2, _ = random_run(tmp_path, "b", "--random-eps", "3", "--random-scales", "3", "--coef-seed", "11")
    for n in sorted(p.name for p in o1.iterdir()):
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes(), n
    rc = r1["random_coefficients"]
    assert rc == {"seed": 11, "eps": random_gen.draw_coefficients(3, 11, "eps"), "scales": random_gen.draw_coefficients(3, 11, "scale")}
    assert len(r1["criteria"]) == 3 * (6 + 5 + 6) + 2 + 6                                        # N=12,24,48 の C1・C2・C3 と、合成の C5 2 行・C3 6 行
    assert len(r1["scales"]) == len(random_gen.SCALES) + 3 and all(f"{x['value']:g}" in r1["scales"] for x in rc["scales"])
    units = [json.loads(x) for x in (o1 / "eps_generality_units_n24.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(random_gen.ekey(x["value"]) in u for u in units for x in rc["eps"])
    md = (o1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "## 乱数で選んだ ε と倍率" in md and "種 11" in md and all(random_gen.pow10_text(x["value"]) in md for x in rc["eps"] + rc["scales"])
    assert "確かめられた" not in md.replace("「確かめられた」とは書かない", "")


def test_cli_without_random_flags_is_unchanged_even_when_a_seed_is_given(tmp_path):
    o0, r0 = random_run(tmp_path, "d")
    o1, _ = random_run(tmp_path, "e", "--coef-seed", "5")
    o2, _ = random_run(tmp_path, "f", "--random-eps", "0", "--random-scales", "0", "--coef-seed", "5")
    for n in sorted(p.name for p in o0.iterdir()):
        assert (o0 / n).read_bytes() == (o1 / n).read_bytes() == (o2 / n).read_bytes(), n
    assert "random_coefficients" not in r0 and "scales" not in r0 and len(r0["criteria"]) == 3 * 8 + 2 + 3


def test_cli_auto_seed_is_recorded_so_the_same_values_can_be_drawn_again(tmp_path):
    o1, r1 = random_run(tmp_path, "g", "--random-eps", "2", "--coef-seed", "auto")
    seed = r1["random_coefficients"]["seed"]
    assert isinstance(seed, int) and 0 <= seed < 10**9 and r1["random_coefficients"]["scales"] == []
    o2, _ = random_run(tmp_path, "h", "--random-eps", "2", "--coef-seed", str(seed))
    assert (o1 / "eps_generality.json").read_bytes() == (o2 / "eps_generality.json").read_bytes()
    assert "scales" not in r1                                                                    # 倍率を足さなければ、主食価格の回に倍率の表は出ない


def test_cli_random_scales_alone_add_the_scale_table_without_new_epsilons(tmp_path):
    _, r = random_run(tmp_path, "i", "--random-scales", "2", "--coef-seed", "3")
    assert len(r["criteria"]) == 3 * 8 + 2 + 3 and len(r["scales"]) == len(random_gen.SCALES) + 2


def test_readme_states_the_random_ranges_and_the_threshold_rule():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    for needle in ("乱数の ε と倍率の確認", "A = 1.00〜9.99", "0 < ε ≤ 1/100", "N = 3", "上限は置かない", "log10(ε)", "--random-eps", "--coef-seed",
                   "tests/test_epsilon_generality.py", "EPS_COEF_SEED", "float"):
        assert needle in text, needle
    assert (random_gen.A_MIN, random_gen.A_MAX, random_gen.N_MIN, random_gen.N_CAP, random_gen.E_CAP, random_gen.EPS_LIMIT, random_gen.P_STOP) == (100, 999, 3, 307, 150, 1e-2, 1 / 6)


# ==== range（旧 test_epsilon_generality_range.py）
# research/epsilon-generality/eps_posthoc.py（旧 eps_range_profile.py）の確認。
#
# SYNTHETIC: 組み立てた行で、収まった単位・消えた単位・始まりで落ち着く単位の数え方、足し合わせ、すべてが収まる最大の ε、乱数の選び方の重み、
# 小さな合成の入力での書き出し（同じ入力なら同じバイト）を確かめる。結論には使わない。


range_rp = importlib.util.module_from_spec(spec)
sys.modules["eps_posthoc"] = range_rp
spec.loader.exec_module(range_rp)
range_gen = range_rp.load_gen()
REF = range_gen.ekey(range_gen.REF_EPS)


def range_er(decay, period=1.0, coef=1.0, at_start=False):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": at_start}


def range_row(boundary=True, devs=None, lost=(), start=(), ref_start=False, same=True):
    """格子の ε すべてで基準の ε と同じ係数 1.0 の単位。devs の ε は係数を 1+dev にずらし、lost の ε は波を残さず、start の ε は始まりで落ち着く。
    境界でない単位は、same なら選ばれる式が ε を入れる前と同じ、same=False なら周期が変わる。"""
    r = {"boundary": boundary, "decay": 0.0 if boundary else 1.0, "period": 1.0}
    for e in range_rp.GRID:
        if not boundary:
            r[range_gen.ekey(e)] = range_er(1.0, period=1.0 if same else 2.0)
        elif e == range_gen.REF_EPS:
            r[range_gen.ekey(e)] = range_er(e, at_start=ref_start)
        else:
            r[range_gen.ekey(e)] = range_er(0.0 if e in lost else e, coef=1.0 + (devs or {}).get(e, 0.0), at_start=e in start)
    return r


def test_grid_stays_inside_the_domain_and_includes_the_reference():
    assert all(0 < e <= 1e-2 for e in range_rp.GRID) and range_gen.REF_EPS in range_rp.GRID and list(range_rp.GRID) == sorted(range_rp.GRID, reverse=True)
    assert list(range_rp.DELTAS) == sorted(range_rp.DELTAS, reverse=True)


def test_coverage_counts_units_within_each_delta_and_the_reference_itself_is_always_inside():
    rows = [range_row(), range_row(devs={1e-3: 0.05}), range_row(devs={1e-3: 0.005}), range_row(devs={1e-3: -0.5})]
    c = range_rp.coverage_rows(range_gen, rows)
    ok = c["per_eps"][range_gen.ekey(1e-3)]["ok"]
    assert c["boundary"] == 4 and ok == {"0.1": 3, "0.01": 2, "0.001": 1, "0.0001": 1}
    assert c["per_eps"][REF]["ok"] == {"0.1": 4, "0.01": 4, "0.001": 4, "0.0001": 4}
    assert c["per_eps"][range_gen.ekey(1e-2)]["ok"] == {"0.1": 4, "0.01": 4, "0.001": 4, "0.0001": 4}


def test_lost_mismatched_and_at_start_units_are_kept_apart():
    rows = [range_row(lost=(1e-3,)), range_row(start=(1e-3,)), range_row(start=(1e-3,), ref_start=True), range_row(ref_start=True), range_row(), range_row(boundary=False)]
    c = range_rp.coverage_rows(range_gen, rows)
    k = c["per_eps"][range_gen.ekey(1e-3)]
    assert c["boundary"] == 5 and c["nonboundary"] == 1
    assert (k["lost"], k["mismatch"], k["at_start"]) == (1, 2, 1)                     # 片方だけ始まり（行 2 と 4）は比べない
    assert k["ok"]["0.0001"] == 2                                                     # 始まりで落ち着く単位（両方）と、ふつうの 1 単位
    assert c["per_eps"][range_gen.ekey(1e-2)]["lost"] == 0


def test_nonboundary_units_count_when_the_chosen_form_is_unchanged():
    rows = [range_row(boundary=False), range_row(boundary=False, same=False), range_row(boundary=False)]
    c = range_rp.coverage_rows(range_gen, rows)
    assert c["nonboundary"] == 3 and all(v["nonboundary_same"] == 2 for v in c["per_eps"].values()) and c["boundary"] == 0


def test_pool_adds_the_window_lengths():
    a = range_rp.coverage_rows(range_gen, [range_row(devs={5e-3: 0.5, 1e-3: 0.02}), range_row()])
    b = range_rp.coverage_rows(range_gen, [range_row(devs={7e-4: 0.005}), range_row(boundary=False)])
    t = range_rp.pool([a, b])
    assert t["boundary"] == 3 and t["nonboundary"] == 1
    assert t["per_eps"][range_gen.ekey(5e-3)]["ok"]["0.1"] == 2 and t["per_eps"][range_gen.ekey(7e-4)]["ok"] == {"0.1": 3, "0.01": 3, "0.001": 2, "0.0001": 2}
    assert t["per_eps"][range_gen.ekey(1e-3)]["nonboundary_same"] == 1 and t["per_eps"][range_gen.ekey(1e-3)]["eps"] == 1e-3


def test_pool_adds_the_lost_mismatched_and_at_start_counts_too():
    a = range_rp.coverage_rows(range_gen, [range_row(lost=(1e-3,)), range_row(start=(1e-3,))])
    b = range_rp.coverage_rows(range_gen, [range_row(start=(1e-3,), ref_start=True), range_row(lost=(1e-3,))])
    k = range_rp.pool([a, b])["per_eps"][range_gen.ekey(1e-3)]
    assert (k["lost"], k["mismatch"], k["at_start"]) == (2, 1, 1) and k["ok"]["0.1"] == 1


def test_largest_full_is_the_biggest_epsilon_before_the_first_one_that_fails():
    t = range_rp.pool([range_rp.coverage_rows(range_gen, [range_row(devs={5e-3: 0.5, 1e-3: 0.02}), range_row(devs={7e-4: 0.005}), range_row()])])
    assert [range_rp.largest_full(t, d) for d in range_rp.DELTAS] == [3e-3, 7e-4, 5e-4, 5e-4]


def test_largest_full_stops_at_a_failure_even_when_larger_epsilons_are_fine():
    t = range_rp.pool([range_rp.coverage_rows(range_gen, [range_row(devs={1e-7: 0.5}), range_row()])])
    assert t["per_eps"][range_gen.ekey(1e-2)]["ok"]["0.1"] == 2                            # 大きい ε は収まっている
    assert range_rp.largest_full(t, 0.1) == 1e-9                                           # でも途中の 1e-7 で外れたので、その手前まで


def test_largest_full_is_none_when_the_smallest_epsilon_fails_or_there_is_nothing_to_judge():
    assert range_rp.largest_full(range_rp.pool([range_rp.coverage_rows(range_gen, [range_row(lost=tuple(range_rp.GRID))])]), 0.1) is None     # 一番小さい ε が消える
    assert range_rp.largest_full(range_rp.pool([range_rp.coverage_rows(range_gen, [range_row(boundary=False)])]), 0.1) is None          # 境界の単位がない
    assert range_rp.largest_full(range_rp.pool([range_rp.coverage_rows(range_gen, [range_row()])]), 0.0001) == 1e-2                     # 全部収まれば格子の最大


def test_draw_share_is_a_probability_that_rises_with_epsilon_and_matches_the_decades():
    xs = [1e-308, 1e-300, 1e-100, 1e-13, 1e-9, 1e-6, 1e-4, 1e-3, 5e-3, 1e-2]
    s = [range_rp.share_le(range_gen, x) for x in xs]
    assert s == sorted(s) and s[0] == 0.0 and 0 < s[1] < 1e-20 and s[-1] == pytest.approx(1.0) and all(0 <= v <= 1 for v in s)
    assert range_rp.share_le(range_gen, 1e-2) == pytest.approx(1.0)
    assert range_rp.share_le(range_gen, 1e-3) == pytest.approx(5 / 6 + (1 / 6) / 900)             # N = 3 の十進の桁のうち A = 1.00 の 1 つだけが 1e-3 以下
    assert range_rp.share_le(range_gen, 9.99e-4) == pytest.approx(5 / 6)                          # N >= 4 の全部
    assert range_rp.share_le(range_gen, 9.99e-5) == pytest.approx((5 / 6) ** 2)                   # N >= 5 の全部


def test_draw_share_matches_a_simulation_of_the_same_rule():
    rng = random.Random(1)
    es = []
    for _ in range(20000):
        a = rng.randint(range_gen.A_MIN, range_gen.A_MAX)
        es.append(float(f"{a // 100}.{a % 100:02d}e-{range_gen.N_MIN + range_gen._steps(rng, range_gen.N_CAP - range_gen.N_MIN)}"))
    for x in (1e-2, 1e-3, 7e-4, 1e-5, 1e-9, 1e-13):
        assert sum(e <= x for e in es) / len(es) == pytest.approx(range_rp.share_le(range_gen, x), abs=0.012), x


def test_draw_share_follows_the_cap_and_the_stop_probability(monkeypatch):
    monkeypatch.setattr(range_gen, "P_STOP", 1.0)                                           # N = 3 だけ
    assert range_rp.share_le(range_gen, 1e-3) == pytest.approx(1 / 900) and range_rp.share_le(range_gen, 9.99e-3) == pytest.approx(1.0)
    monkeypatch.setattr(range_gen, "P_STOP", 0.0)                                           # N_CAP だけ
    assert range_rp.share_le(range_gen, 1e-308) == 0.0 and range_rp.share_le(range_gen, 1e-300) == pytest.approx(1.0) and range_rp.share_le(range_gen, 1e-13) == pytest.approx(1.0)
    assert range_rp.share_le(range_gen, 5e-307) == pytest.approx(401 / 900)                       # N = 307 で A = 1.00〜5.00 の 401 通り


RANGE_LO, RANGE_HI = 8.14e-13, 2.22e-3
REGION = {"mode": "inside", "lo": RANGE_LO, "hi": RANGE_HI}


def test_side_of_includes_both_ends_in_inside_and_leaves_them_out_of_above_and_below():
    assert [range_rp.side_of(REGION, e) for e in (1e-2, 2.23e-3, RANGE_HI, 1e-5, RANGE_LO, 8.13e-13, 1e-20)] == ["above", "above", "inside", "inside", "inside", "below", "below"]


def pooled(rows):
    return range_rp.pool([range_rp.coverage_rows(range_gen, rows)])


def test_region_summary_looks_only_at_the_grid_points_on_the_chosen_side():
    t = pooled([range_row(devs={5e-3: 0.5, 1e-3: 0.02, 1e-7: 0.2}), range_row(devs={5e-3: 0.05}), range_row()])
    above = range_rp.region_summary(range_gen, t, dict(REGION, mode="above"))
    assert above["eps"] == [1e-2, 5e-3, 3e-3] and above["worst_ok_share"] == {"0.1": pytest.approx(2 / 3), "0.01": pytest.approx(1 / 3), "0.001": pytest.approx(1 / 3), "0.0001": pytest.approx(1 / 3)}
    assert above["all_within"] == {"0.1": False, "0.01": False, "0.001": False, "0.0001": False}
    inside = range_rp.region_summary(range_gen, t, REGION)
    assert inside["eps"][0] == 2e-3 and inside["eps"][-1] == 1e-11 and 5e-3 not in inside["eps"]
    assert inside["worst_ok_share"]["0.1"] == pytest.approx(2 / 3) and inside["all_within"]["0.1"] is False        # 1e-7 で 0.2 ずれる行がある
    assert inside["worst_ok_share"]["0.01"] == pytest.approx(2 / 3)                                                    # 1e-3 の 0.02 と 1e-7 の 0.2 は、それぞれ別の点で 1 行だけ外れる
    assert range_rp.region_summary(range_gen, t, dict(REGION, mode="below"))["eps"] == [1e-13]
    below = range_rp.region_summary(range_gen, t, {"mode": "below", "lo": 1e-14, "hi": RANGE_HI})                                       # 1e-14 より小さい格子の ε はない
    assert below["eps"] == [] and below["worst_ok_share"]["0.1"] is None and below["all_within"]["0.1"] is False and below["max_lost"] is None
    ok = range_rp.region_summary(range_gen, pooled([range_row(), range_row()]), REGION)
    assert all(ok["all_within"].values()) and all(v == 1.0 for v in ok["worst_ok_share"].values())


def test_region_summary_counts_lost_and_changed_units_as_the_maximum_over_the_side():
    t = pooled([range_row(lost=(1e-2,)), range_row(boundary=False), range_row(boundary=False, same=False)])
    s = range_rp.region_summary(range_gen, t, dict(REGION, mode="above"))
    assert s["max_lost"] == 1 and s["max_nonboundary_changed"] == 1 and s["worst_ok_share"]["0.1"] == 0.0
    assert range_rp.region_summary(range_gen, t, REGION)["max_lost"] == 0


def test_region_summary_changed_units_is_the_largest_count_over_the_points_not_the_smallest():
    r = range_row(boundary=False)
    r[range_gen.ekey(5e-3)] = range_er(1.0, period=2.0)                                           # 5e-3 のときだけ式が変わる非境界の単位
    s = range_rp.region_summary(range_gen, pooled([range_row(), r]), dict(REGION, mode="above"))
    assert s["max_nonboundary_changed"] == 1 and s["eps"] == [1e-2, 5e-3, 3e-3]
    assert range_rp.region_summary(range_gen, pooled([range_row(), r]), REGION)["max_nonboundary_changed"] == 0


def test_region_summary_probabilities_of_the_three_sides_add_up_to_one_and_match_the_rule():
    t = pooled([range_row()])
    p = {m: range_rp.region_summary(range_gen, t, dict(REGION, mode=m))["draw_probability"] for m in range_gen.MODES}
    assert sum(p.values()) == pytest.approx(1.0, abs=1e-12) and p["inside"] == pytest.approx(0.70017, abs=1e-5)
    assert p["inside"] == pytest.approx(range_rp.share_le(range_gen, RANGE_HI) - range_rp.share_le(range_gen, 8.13e-13), abs=1e-12)


def test_region_summary_without_boundary_units_cannot_summarise():
    s = range_rp.region_summary(range_gen, pooled([range_row(boundary=False)]), REGION)
    assert s["eps"] and all(v is None for v in s["worst_ok_share"].values()) and not any(s["all_within"].values())


def test_render_with_a_range_lists_the_side_and_says_when_it_is_empty():
    def res_of(rows, region):
        t = pooled(rows)
        return {"grid": list(range_rp.GRID), "deltas": list(range_rp.DELTAS), "sets": {}, "total": t, "region": region, "region_summary": range_rp.region_summary(range_gen, t, region),
                "full_coverage_max_eps": {format(d, "g"): range_rp.largest_full(t, d) for d in range_rp.DELTAS}, "draw_share_le": {format(e, "g"): range_rp.share_le(range_gen, e) for e in range_rp.GRID}}
    md = range_rp.range_profile_render(range_gen, res_of([range_row()], dict(REGION, mode="above")))
    assert "## 指定した範囲: above（8.14×10^-13 〜 2.22×10^-3" in md and "この側にある格子の ε 3 個: 0.01, 0.005, 0.003。" in md and "| 10% | 100.00% | はい |" in md
    assert "| 0.01 | above |" in md and "| 0.002 | inside |" in md and "| 1e-13 | below |" in md and "ε がこの側に入る確率: 14.4%" in md
    empty = range_rp.range_profile_render(range_gen, res_of([range_row()], {"mode": "below", "lo": 1e-14, "hi": RANGE_HI}))
    assert "この側にある格子の ε 0 個: なし。" in empty and "まとめられません" in empty and "最悪の収まった割合" not in empty
    none = range_rp.range_profile_render(range_gen, res_of([range_row(boundary=False)], REGION))
    assert "まとめられません" in none


def range_small_csv(tmp_path):
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = []
    for j in range(3):
        for i in range(48):
            y, m = 2020 + i // 12, i % 12 + 1
            v = 3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)
            rows.append({"country": "AAA", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": f"mine:c{j}", "value": str(v),
                         "unit": "x", "source": "https://github.com/tezamo/FPMA (x)", "note": f"m={j}", "estimated_value": ""})
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def test_main_takes_another_variable_prefix_writes_the_same_bytes_twice_and_says_it_is_not_a_constant(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert range_rp.range_profile(["--csv", str(range_small_csv(tmp_path)), "--prefix", "mine:", "--cadence", "month", "--outdir", str(out), "--repo", str(ROOT)]) == 0
        outs.append(out)
    for n in ("eps_range_profile.json", "eps_range_profile.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    res = json.loads((outs[0] / "eps_range_profile.json").read_text(encoding="utf-8"))
    assert res["grid"] == list(range_rp.GRID) and list(res["sets"]) == [str(n) for n in range_gen.LENGTHS]
    assert res["total"]["boundary"] == sum(s["boundary"] for s in res["sets"].values()) > 0
    assert all(res["total"]["per_eps"][range_gen.ekey(e)]["ok"]["0.1"] == res["total"]["boundary"] for e in range_rp.GRID if e <= 1e-6)      # きれいな波は ε が小さければ動かない
    assert set(res["full_coverage_max_eps"]) == {"0.1", "0.01", "0.001", "0.0001"} and set(res["draw_share_le"]) == {format(e, "g") for e in range_rp.GRID}
    md = (outs[0] / "eps_range_profile.md").read_text(encoding="utf-8")
    assert "ε の範囲を決める値ではありません" in md and "| 0.01 |" in md and "乱数の選び方の重み" in md


def test_main_without_matching_variables_stops_with_an_error(tmp_path):
    with pytest.raises(SystemExit) as ei:
        range_rp.range_profile(["--csv", str(range_small_csv(tmp_path)), "--prefix", "nothing:", "--outdir", str(tmp_path / "o"), "--repo", str(ROOT)])
    assert "nothing:" in str(ei.value) and not (tmp_path / "o").exists()


def test_render_says_so_when_nothing_can_be_judged_or_the_smallest_epsilon_fails():
    def res_of(rows):
        t = range_rp.pool([range_rp.coverage_rows(range_gen, rows)])
        return {"grid": list(range_rp.GRID), "deltas": list(range_rp.DELTAS), "sets": {}, "total": t,
                "full_coverage_max_eps": {format(d, "g"): range_rp.largest_full(t, d) for d in range_rp.DELTAS},
                "draw_share_le": {format(e, "g"): range_rp.share_le(range_gen, e) for e in range_rp.GRID}}
    assert "境界の単位がないので判定できない" in range_rp.range_profile_render(range_gen, res_of([range_row(boundary=False)]))
    md = range_rp.range_profile_render(range_gen, res_of([range_row(lost=tuple(range_rp.GRID))]))
    assert "一番小さい ε でも外れた単位がある" in md and "境界の単位がないので" not in md
    assert "0.01（これ以下の格子の ε ではすべて収まった）" in range_rp.range_profile_render(range_gen, res_of([range_row()]))


def test_range_readme_points_to_the_script():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    assert "eps_posthoc.py range_profile" in text and "tests/test_epsilon_generality.py" in text
    assert "その側の格子の ε について、許容ごとの最悪の収まった割合などをまとめる" in text and "`--eps-range MODE LO HI`（`eps_generality.py` と同じ書き方" in text


def test_results_readme_and_files_match_the_json_and_say_it_is_not_a_constant():
    R = DIR / "results-random"
    res = {k: json.loads((R / k / "eps_range_profile.json").read_text(encoding="utf-8")) for k in ("staple", "monthly", "daily")}
    text = (R / "README.md").read_text(encoding="utf-8")
    assert "## ε が動いた範囲" in text and "定数ではない" in text and "決める値ではありません" in text
    total = range_rp.pool([r["total"] for r in res.values()])
    assert f"{total['boundary']:,}" in text and f"{total['nonboundary']:,}" in text
    for d in range_rp.DELTAS:
        row = f"| {d * 100:g}% | {range_rp.largest_full(total, d):g} |"
        assert row in text, row
    for k, r in res.items():
        assert r["grid"] == list(range_rp.GRID)
        assert (R / k / "eps_range_profile.md").read_text(encoding="utf-8") == range_rp.range_profile_render(range_gen, r), k


def test_main_with_a_range_adds_the_ends_and_random_points_and_a_summary(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert range_rp.range_profile(["--csv", str(range_small_csv(tmp_path)), "--prefix", "mine:", "--cadence", "month", "--outdir", str(out), "--repo", str(ROOT),
                        "--eps-range", "below", "8.14×10^-13", "2.22e-3", "--random-eps", "3", "--coef-seed", "7"]) == 0
        outs.append(out)
    for n in ("eps_range_profile.json", "eps_range_profile.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    res = json.loads((outs[0] / "eps_range_profile.json").read_text(encoding="utf-8"))
    drawn = [d["value"] for d in range_gen.draw_coefficients(3, 7, "eps", range_gen.make_region("eps", "below", RANGE_LO, RANGE_HI))]
    assert res["region"] == {"mode": "below", "lo": RANGE_LO, "hi": RANGE_HI} and len(drawn) == 3 and all(v < RANGE_LO for v in drawn)
    assert res["grid"] == sorted(set(range_rp.GRID) | {RANGE_LO, RANGE_HI} | set(drawn), reverse=True)
    sm = res["region_summary"]
    assert sm["eps"] == sorted([1e-13] + drawn, reverse=True) and sm["draw_probability"] == pytest.approx(0.15594, abs=2e-5)
    md = (outs[0] / "eps_range_profile.md").read_text(encoding="utf-8")
    assert "## 指定した範囲: below（8.14×10^-13 〜 2.22×10^-3" in md and "| ε | 範囲 |" in md and "| 8.14e-13 | inside |" in md and "| 0.0022200000000000002 |" not in md


def test_main_without_a_range_has_no_range_section_or_column(tmp_path):
    out = tmp_path / "plain"
    assert range_rp.range_profile(["--csv", str(range_small_csv(tmp_path)), "--prefix", "mine:", "--cadence", "month", "--outdir", str(out), "--repo", str(ROOT)]) == 0
    res = json.loads((out / "eps_range_profile.json").read_text(encoding="utf-8"))
    assert "region" not in res and "region_summary" not in res and res["grid"] == list(range_rp.GRID)
    md = (out / "eps_range_profile.md").read_text(encoding="utf-8")
    assert "指定した範囲" not in md and "| ε | δ=10%" in md


@pytest.mark.parametrize("flags", [
    ("--random-eps", "3"),                                                           # 範囲がない
    ("--eps-range", "sideways", "1e-5", "1e-3"),
    ("--eps-range", "inside", "1e-3", "1e-5"),                                       # LO > HI
    ("--eps-range", "inside", "abc", "1e-3"),
    ("--eps-range", "inside", "1e-5", "1"),                                          # ε は 1/100 まで
    ("--eps-range", "above", "1e-3", "9.99e-3", "--random-eps", "1"),                # その側に選べる値がない
    ("--eps-range", "inside", "1e-5"),                                               # 3 つ要る
])
def test_main_refuses_a_bad_range_before_doing_anything(tmp_path, flags):
    with pytest.raises(SystemExit) as e:
        range_rp.range_profile(["--csv", str(range_small_csv(tmp_path)), "--prefix", "mine:", "--outdir", str(tmp_path / "x"), "--repo", str(ROOT), *flags])
    assert e.value.code == 2 and not (tmp_path / "x").exists()


# ==== region（旧 test_epsilon_generality_region.py）
# eps_generality.py の範囲指定（--eps-range / --scale-range MODE LO HI）の確認。
#
# SYNTHETIC: 範囲に入る (A, 指数) の組、選ばれる確率、選んだ値、書き出し、README の説明を確かめる。結論には使わない。
# 指定しないときに、登録した乱数の値が変わらないことも確かめる。


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, DIR / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


region_gen = _load("eps_generality", "eps_generality.py")
region_rp = _load("eps_posthoc", "eps_posthoc.py")
REGION_LO, REGION_HI = 8.14e-13, 2.22e-3                          # 利用者が挙げた 2 つの値
REGION_SEED = 18750922
REGISTERED = [2.22e-3, 1.76e-3, 3.54e-4, 3.20e-4, 7.82e-5, 6.60e-6, 9.82e-9, 2.28e-9, 6.29e-11, 8.14e-13]


def table(kind, mode, lo=REGION_LO, hi=REGION_HI):
    return {x: (m, a) for x, m, a in region_gen.region_table(kind, region_gen.make_region(kind, mode, lo, hi))}


def p_inside(kind, region):
    """規則で選ばれる値が範囲に入る確率。"""
    return sum(m * len(a) for _, m, a in region_gen.region_table(kind, region)) / (region_gen.A_MAX - region_gen.A_MIN + 1)


def test_without_a_range_the_registered_values_are_unchanged():
    assert [d["value"] for d in region_gen.draw_coefficients(10, REGION_SEED, "eps")] == REGISTERED
    assert region_gen.draw_coefficients(10, REGION_SEED, "eps", None) == region_gen.draw_coefficients(10, REGION_SEED, "eps")
    assert region_gen.make_draws(10, 10, REGION_SEED) == {"seed": REGION_SEED, "eps": region_gen.draw_coefficients(10, REGION_SEED, "eps"), "scales": region_gen.draw_coefficients(10, REGION_SEED, "scale")}
    assert "regions" not in region_gen.make_draws(3, 3, REGION_SEED)


@pytest.mark.parametrize("text", ["2.22×10^-3", "2.22x10^-3", "2.22 X 10 ^ -3", "2.22*10^-3", "2.22e-3", "2.22E-3", "0.00222", " 2.22×10^-3 "])
def test_parse_pow10_reads_the_ways_a_value_is_written(text):
    assert region_gen.parse_pow10(text) == 2.22e-3                                       # 文字のまま float にするので、同じ値


def test_parse_pow10_keeps_exponents_and_large_values():
    assert region_gen.parse_pow10("8.14×10^-13") == 8.14e-13 and region_gen.parse_pow10("1×10^+2") == 100.0 and region_gen.parse_pow10("5") == 5.0
    assert region_gen.parse_pow10("9.99×10^-307") == 9.99e-307


@pytest.mark.parametrize("text", ["", "abc", "0", "-1", "-2.22×10^-3", "inf", "nan", "2.22×10^", "×10^-3", "2.22×10-3"])
def test_parse_pow10_refuses_what_is_not_a_positive_finite_number(text):
    with pytest.raises(ValueError):
        region_gen.parse_pow10(text)


def test_make_region_checks_the_range_and_the_epsilon_domain():
    assert region_gen.make_region("eps", "inside", REGION_LO, REGION_HI) == {"mode": "inside", "lo": REGION_LO, "hi": REGION_HI}
    assert region_gen.make_region("eps", "below", 1e-3, 1e-3)["hi"] == 1e-3 and region_gen.make_region("eps", "inside", 1e-3, 1e-2)["hi"] == 1e-2
    for bad in (("sideways", REGION_LO, REGION_HI), ("inside", REGION_HI, REGION_LO), ("inside", 0.0, REGION_HI), ("inside", -1.0, REGION_HI), ("inside", REGION_LO, float("inf")), ("inside", REGION_LO, float("nan"))):
        with pytest.raises(ValueError):
            region_gen.make_region("eps", *bad)
    with pytest.raises(ValueError):
        region_gen.make_region("eps", "inside", REGION_LO, 1.0000001e-2)                       # ε は 1/100 まで
    assert region_gen.make_region("scale", "above", 1.0, 1e9)["hi"] == 1e9              # 倍率にその上限はない


def test_inside_has_the_exponents_between_the_ends_and_keeps_both_ends():
    t = table("eps", "inside")
    assert sorted(t) == list(range(-13, -2))                                       # N = 3〜13
    assert t[-3][1] == list(range(100, 223)) and t[-13][1] == list(range(814, 1000))     # 2.22×10^-3 と 8.14×10^-13 は入る
    assert all(t[x][1] == list(range(100, 1000)) for x in range(-12, -3))


def test_above_and_below_leave_out_the_ends_and_the_three_regions_split_the_rule():
    up, down = table("eps", "above"), table("eps", "below")
    assert sorted(up) == [-3] and up[-3][1] == list(range(223, 1000))
    assert min(down) == -307 and max(down) == -13 and down[-13][1] == list(range(100, 814))
    assert all(down[x][1] == list(range(100, 1000)) for x in range(-306, -13))
    n = sum(len(a) for _, a in table("eps", "inside").values()) + sum(len(a) for _, a in up.values()) + sum(len(a) for _, a in down.values())
    assert n == 900 * (region_gen.N_CAP - region_gen.N_MIN + 1)                                  # 重ならず、抜けない
    ins = {(x, a) for x, (_, al) in table("eps", "inside").items() for a in al}
    assert not ins & {(x, a) for x, (_, al) in up.items() for a in al} and not ins & {(x, a) for x, (_, al) in down.items() for a in al}


def test_a_range_inside_one_decade_and_the_scale_kind_are_handled_the_same_way():
    t = table("eps", "inside", 1.5e-5, 2.5e-5)
    assert sorted(t) == [-5] and t[-5][1] == list(range(150, 251))
    s = table("scale", "inside", 1e-7, 1e-4)
    assert sorted(s) == [-7, -6, -5, -4] and s[-4][1] == [100] and s[-7][1] == list(range(100, 1000))
    assert table("scale", "above", 1e-4, 1e-4)[-4][1] == list(range(101, 1000)) and 0 in table("scale", "above", 1e-4, 1e-4)
    assert table("scale", "above", 1.0, 1.0)[0][1] == list(range(101, 1000)) and 0 not in table("scale", "below", 1.0, 1.0)     # 1.00 は above にも below にも入らない


def test_exponent_masses_follow_the_rule_including_the_ends():
    p, q = region_gen.P_STOP, 1 - region_gen.P_STOP
    e, s = region_gen.exponent_masses("eps"), region_gen.exponent_masses("scale")
    assert sorted(e) == list(range(-region_gen.N_CAP, -region_gen.N_MIN + 1)) and sorted(s) == list(range(-region_gen.E_CAP, region_gen.E_CAP + 1))
    assert e[-3] == p and e[-4] == q * p and e[-region_gen.N_CAP + 1] == q ** (region_gen.N_CAP - region_gen.N_MIN - 1) * p
    assert e[-region_gen.N_CAP] == q ** (region_gen.N_CAP - region_gen.N_MIN)                             # 上限 N_CAP は「止まる」を待たずに打ち切るので、q^(段の数) だけ
    assert s[0] == p and s[1] == s[-1] == 0.5 * q * p and s[region_gen.E_CAP] == s[-region_gen.E_CAP] == 0.5 * q ** region_gen.E_CAP
    assert sum(e.values()) == pytest.approx(1.0, abs=1e-12) and sum(s.values()) == pytest.approx(1.0, abs=1e-12)


def test_the_probabilities_of_the_three_regions_add_up_to_one_for_both_kinds():
    for kind, lo, hi in (("eps", REGION_LO, REGION_HI), ("scale", 1e-7, 1e-4), ("scale", 1.0, 3.0)):
        parts = [p_inside(kind, region_gen.make_region(kind, m, lo, hi)) for m in region_gen.MODES]
        assert sum(parts) == pytest.approx(1.0, abs=1e-12), kind
        assert all(p > 0 for p in parts)


def test_the_inside_probability_matches_the_draw_weights_of_the_profile_script():
    for x in (1e-2, 2.22e-3, 1e-4, 1e-9, 1e-13, 1e-100):
        assert p_inside("eps", region_gen.make_region("eps", "inside", 1e-308, x)) == pytest.approx(region_rp.share_le(region_gen, x), abs=1e-12), x
    assert p_inside("eps", region_gen.make_region("eps", "below", REGION_LO, REGION_HI)) == pytest.approx(0.15594, abs=2e-5)
    assert p_inside("eps", region_gen.make_region("eps", "above", REGION_LO, REGION_HI)) == pytest.approx(0.14389, abs=2e-5)


def test_drawn_values_are_in_the_region_distinct_sorted_and_not_the_fixed_ones():
    for mode, ok in (("inside", lambda v: REGION_LO <= v <= REGION_HI), ("above", lambda v: v > REGION_HI), ("below", lambda v: v < REGION_LO)):
        r = region_gen.make_region("eps", mode, REGION_LO, REGION_HI)
        d = region_gen.draw_coefficients(10, REGION_SEED, "eps", r)
        vals = [x["value"] for x in d]
        assert len(set(vals)) == 10 and vals == sorted(vals, reverse=True) and all(ok(v) for v in vals) and all(v not in region_gen.EPS for v in vals), mode
        assert all(x["value"] == float(f"{x['a']:.2f}e{x['exp']}") and 1.0 <= x["a"] <= 9.99 for x in d)
        assert d == region_gen.draw_coefficients(10, REGION_SEED, "eps", r) and d != region_gen.draw_coefficients(10, REGION_SEED + 1, "eps", r)
    sc = region_gen.draw_coefficients(10, REGION_SEED, "scale", region_gen.make_region("scale", "inside", 1e-7, 1e-4))
    assert all(1e-7 <= x["value"] <= 1e-4 for x in sc) and all(x["value"] not in region_gen.SCALES for x in sc)


def test_the_fixed_values_are_left_out_even_when_the_range_holds_them():
    r = region_gen.make_region("eps", "inside", 1e-9, 1e-9)
    with pytest.raises(ValueError):                                                  # 範囲に入る値は 1e-9 の 1 個だけで、それは決め打ちなので選べない
        region_gen.draw_coefficients(1, REGION_SEED, "eps", r)


def test_asking_for_more_values_than_the_range_holds_stops():
    r = region_gen.make_region("eps", "inside", 1.5e-5, 1.54e-5)                            # 1.50〜1.54 の 5 個
    assert len(region_gen.draw_coefficients(5, REGION_SEED, "eps", r)) == 5
    with pytest.raises(ValueError, match="に入る値は 5 個で、6 個は選べない"):
        region_gen.draw_coefficients(6, REGION_SEED, "eps", r)
    with pytest.raises(ValueError):
        region_gen.draw_coefficients(1, REGION_SEED, "eps", region_gen.make_region("eps", "above", 1e-3, 9.99e-3))     # 9.99×10^-3 より上は ε の定義域の外で空
    with pytest.raises(ValueError):
        region_gen.draw_coefficients(1, REGION_SEED, "eps", region_gen.make_region("eps", "below", 1e-307, 1e-300))    # 下は N_CAP の 1.00×10^-307 まで


def test_exponents_are_chosen_with_the_weights_of_the_rule_not_evenly():
    r = region_gen.make_region("eps", "inside", 1e-8, 9.99e-4)                              # N = 4〜8: 4 の確率は (5/6)^1 を (5/6)^1〜(5/6)^5 の和で割った 0.279（一様なら 0.2）
    n4 = sum(region_gen.draw_coefficients(1, s, "eps", r)[0]["exp"] == -4 for s in range(1500))
    assert n4 / 1500 == pytest.approx((5 / 6) / sum((5 / 6) ** k for k in range(1, 6)), abs=0.04)


def test_the_number_of_values_in_each_exponent_counts_not_only_the_rule_probability():
    r = region_gen.make_region("eps", "inside", 9.5e-5, 1.05e-4)                            # N = 5 の A = 9.50〜9.99（50 個）と N = 4 の A = 1.00〜1.05（6 個）
    t = {x: (m, a) for x, m, a in region_gen.region_table("eps", r)}
    assert sorted(t) == [-5, -4] and len(t[-5][1]) == 50 and len(t[-4][1]) == 6
    want = t[-4][0] * 6 / (t[-4][0] * 6 + t[-5][0] * 50)                             # 0.126（rule の確率だけで比べると 0.545）
    n4 = sum(region_gen.draw_coefficients(1, s, "eps", r)[0]["exp"] == -4 for s in range(1500))
    assert want == pytest.approx(0.126, abs=0.001) and n4 / 1500 == pytest.approx(want, abs=0.04)


def test_make_draws_records_the_regions_only_when_they_are_used():
    d = region_gen.make_draws(4, 3, REGION_SEED, ("below", REGION_LO, REGION_HI), None)
    assert d["regions"] == {"eps": {"mode": "below", "lo": REGION_LO, "hi": REGION_HI}} and all(x["value"] < REGION_LO for x in d["eps"])
    assert d["scales"] == region_gen.draw_coefficients(3, REGION_SEED, "scale")                    # 範囲を指定しない方は変わらない
    d2 = region_gen.make_draws(2, 2, REGION_SEED, None, ("inside", 1e-7, 1e-4))
    assert list(d2["regions"]) == ["scales"] and d2["eps"] == region_gen.draw_coefficients(2, REGION_SEED, "eps")
    with pytest.raises(ValueError):
        region_gen.make_draws(2, 2, REGION_SEED, ("inside", REGION_HI, REGION_LO), None)


def test_region_lines_say_which_range_the_values_were_chosen_from():
    rc = {"seed": REGION_SEED, "eps": [], "scales": []}
    assert region_gen.region_lines(rc) == [] and region_gen.region_lines(dict(rc, regions={})) == []
    lines = region_gen.region_lines(dict(rc, regions={"eps": {"mode": "above", "lo": REGION_LO, "hi": REGION_HI}}))
    assert len(lines) == 1 and lines[0].startswith("- εを選んだ範囲: above（8.14×10^-13 〜 2.22×10^-3")
    both = region_gen.region_lines(dict(rc, regions={"scales": {"mode": "inside", "lo": 1e-7, "hi": 1e-4}, "eps": {"mode": "below", "lo": REGION_LO, "hi": REGION_HI}}))
    assert [l.split(":")[0] for l in both] == ["- εを選んだ範囲", "- 倍率を選んだ範囲"]


def region_small_csv(tmp_path):
    import csv
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = [{"country": "AAA", "date": f"{2020 + i // 12:04d}-{i % 12 + 1:02d}-01", "year": str(2020 + i // 12), "variable": f"staple_price:c{j}",
             "value": str(3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)), "unit": "USD per kg",
             "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""} for j in range(3) for i in range(48)]
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def region_run(tmp_path, name, *flags):
    out = tmp_path / name
    assert region_gen.main(["--csv", str(region_small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT), *flags]) == 0
    return out


def test_cli_with_a_range_records_it_uses_it_and_is_byte_reproducible(tmp_path):
    import json
    flags = ("--random-eps", "3", "--eps-range", "below", "8.14×10^-13", "2.22×10^-3", "--random-scales", "2", "--scale-range", "inside", "1e-7", "1e-4", "--coef-seed", "11")
    o1, o2 = region_run(tmp_path, "a", *flags), region_run(tmp_path, "b", *flags)
    for n in sorted(p.name for p in o1.iterdir()):
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes(), n
    rc = json.loads((o1 / "eps_generality.json").read_text(encoding="utf-8"))["random_coefficients"]
    assert rc["regions"] == {"eps": {"mode": "below", "lo": REGION_LO, "hi": REGION_HI}, "scales": {"mode": "inside", "lo": 1e-7, "hi": 1e-4}}
    assert rc["eps"] == region_gen.draw_coefficients(3, 11, "eps", region_gen.make_region("eps", "below", REGION_LO, REGION_HI)) and all(d["value"] < REGION_LO for d in rc["eps"])
    assert all(1e-7 <= d["value"] <= 1e-4 for d in rc["scales"])
    md = (o1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "εを選んだ範囲: below（8.14×10^-13 〜 2.22×10^-3" in md and "倍率を選んだ範囲: inside（1.00×10^-7 〜 1.00×10^-4" in md


def test_cli_without_a_range_has_no_regions_in_the_output(tmp_path):
    import json
    o = region_run(tmp_path, "c", "--random-eps", "2", "--coef-seed", "11")
    assert "regions" not in json.loads((o / "eps_generality.json").read_text(encoding="utf-8"))["random_coefficients"]
    assert "を選んだ範囲" not in (o / "eps_generality.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("flags", [
    ("--eps-range", "inside", "1e-5", "1e-3"),                                       # --random-eps がない
    ("--random-eps", "0", "--eps-range", "inside", "1e-5", "1e-3"),
    ("--random-scales", "2", "--eps-range", "inside", "1e-5", "1e-3"),               # 倍率だけを足すのに ε の範囲
    ("--random-eps", "2", "--scale-range", "inside", "1e-5", "1e-3"),
    ("--random-eps", "2", "--eps-range", "sideways", "1e-5", "1e-3"),
    ("--random-eps", "2", "--eps-range", "inside", "1e-3", "1e-5"),                  # LO > HI
    ("--random-eps", "2", "--eps-range", "inside", "abc", "1e-3"),
    ("--random-eps", "2", "--eps-range", "inside", "1e-5", "1"),                     # ε は 1/100 まで
    ("--random-eps", "2", "--eps-range", "inside", "1e-5"),                          # 3 つ要る
])
def test_cli_refuses_a_bad_range_before_doing_anything(tmp_path, flags):
    with pytest.raises(SystemExit) as e:
        region_gen.main(["--csv", str(region_small_csv(tmp_path)), "--outdir", str(tmp_path / "x"), "--repo", str(ROOT), *flags])
    assert e.value.code == 2 and not (tmp_path / "x").exists()


def test_readme_describes_the_options_and_points_to_the_tests():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    for needle in ("--eps-range MODE LO HI", "--scale-range MODE LO HI", "**inside**", "**above**", "**below**", "tests/test_epsilon_generality.py", "2.22×10^-3", "範囲の既定値は置かない"):
        assert needle in text, needle


REGISTERED_4 = {
    "inside": [4.91e-4, 3.05e-5, 1.65e-5, 3.30e-6, 3.71e-7, 9.99e-8, 8.43e-8, 2.13e-8, 1.88e-8, 3.78e-12],
    "above": [9.66e-3, 7.79e-3, 6.14e-3, 5.01e-3, 4.94e-3, 4.53e-3, 4.28e-3, 3.36e-3, 3.11e-3, 2.88e-3],
    "below": [4.91e-13, 3.05e-15, 1.65e-15, 3.30e-16, 3.71e-18, 9.99e-19, 8.43e-19, 2.13e-19, 1.88e-19, 3.78e-29],
}


@pytest.mark.parametrize("mode", region_gen.MODES)
def test_fourth_round_values_come_from_the_seed_and_the_rule_and_are_listed_in_the_readme(mode):
    d = region_gen.draw_coefficients(10, 20261026, "eps", region_gen.make_region("eps", mode, REGION_LO, REGION_HI))
    assert [x["value"] for x in d] == REGISTERED_4[mode]
    text = (DIR / "README.md").read_text(encoding="utf-8")
    assert f"  - {mode}: " + ", ".join(region_gen.pow10_text(v) for v in REGISTERED_4[mode]) in text
    assert all(0 < v <= 1e-2 for v in REGISTERED_4[mode])


def test_fourth_round_registration_names_the_range_the_seed_and_the_counts():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("## 乱数の ε を範囲から選ぶ確認（第 4 回）"):]
    for needle in ("LO = 8.14×10^-13、HI = 2.22×10^-3", "種: `20261026`", "それぞれ ε を 10 個", "--eps-range <inside|above|below> 8.14e-13 2.22e-3 --coef-seed 20261026", "3 入力の合計 280 件（主食価格 100、物理量の月次 90、日次 90）", "予想（結果を見る前。判定には使わない）"):
        assert needle in sec, needle


@pytest.mark.parametrize("mode", region_gen.MODES)
def test_fourth_round_results_record_the_registered_values_and_range_and_match_the_readme(mode):
    import json
    R = DIR / "results-region"
    text = (R / "README.md").read_text(encoding="utf-8")
    rnd_total = rnd_bad = 0
    for k in ("staple", "monthly", "daily"):
        j = json.loads((R / mode / k / "eps_generality.json").read_text(encoding="utf-8"))
        rc = j["random_coefficients"]
        assert rc["seed"] == 20261026 and [d["value"] for d in rc["eps"]] == REGISTERED_4[mode] and rc["scales"] == []
        assert rc["regions"] == {"eps": {"mode": mode, "lo": REGION_LO, "hi": REGION_HI}}
        assert j["control"]["pass"] and j["repeat_identical"] and "regions" not in j
        for c in j["criteria"]:
            if any(f"ε={region_gen.elabel(e)} " in c["text"] for e in REGISTERED_4[mode]):
                rnd_total += 1
                rnd_bad += c["ok"] is not True
        md = (R / mode / k / "eps_generality.md").read_text(encoding="utf-8")
        assert f"- εを選んだ範囲: {mode}（8.14×10^-13 〜 2.22×10^-3" in md
    assert rnd_total == 280 and rnd_bad == {"inside": 0, "above": 11, "below": 0}[mode]
    assert f"| {mode} | 主食価格 |" in text and "全基準を満たした回はないので、「矛盾する材料はなかった」とは書きません" in text


# ==== scaleband（旧 test_epsilon_generality_scaleband.py）
# research/epsilon-generality/README.md の「倍率を帯から選ぶ確認（第 5 回）」の事前登録の確認。
#
# SYNTHETIC: 登録した倍率が種と規則から出ること、予想に書いた数が事後の格子の JSON と合うこと、実行の書式が README と同じであること、
# 小さな合成の入力で同じ書式が通り、帯の内側の倍率が書き出されることを確かめる。結果の当否は確かめない（結論には使わない）。


scaleband_gen = _load("eps_generality", "eps_generality.py")
SCALEBAND_SEED, SCALEBAND_LO, SCALEBAND_HI, COUNT = 20261027, 1e-7, 1e-4, 10
REGISTERED_5 = [9.57e-5, 5.98e-5, 3.16e-5, 8.91e-6, 5.00e-6, 1.92e-6, 9.50e-7, 8.63e-7, 7.66e-7, 1.03e-7]


def section():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    return text[text.index("## 倍率を帯から選ぶ確認（第 5 回）: 事前登録"):]


def test_the_registered_scales_come_from_the_seed_and_the_rule_and_are_listed_in_the_readme():
    d = scaleband_gen.draw_coefficients(COUNT, SCALEBAND_SEED, "scale", scaleband_gen.make_region("scale", "inside", SCALEBAND_LO, SCALEBAND_HI))
    assert [x["value"] for x in d] == REGISTERED_5 and all(SCALEBAND_LO <= v <= SCALEBAND_HI for v in REGISTERED_5)
    assert ", ".join(scaleband_gen.pow10_text(v) for v in REGISTERED_5) in section()
    assert scaleband_gen.make_draws(0, COUNT, SCALEBAND_SEED, None, ("inside", SCALEBAND_LO, SCALEBAND_HI))["scales"] == d                   # 実行と同じ呼び方


def test_the_seed_is_the_decision_date_and_differs_from_the_earlier_rounds():
    assert SCALEBAND_SEED == 20261027 and SCALEBAND_SEED != scaleband_gen.SEED


def test_the_registration_names_the_range_the_seed_the_count_and_the_command():
    sec = section()
    for needle in ("inside、LO = 1×10^-7、HI = 1×10^-4（両端を含む）", "倍率を 10 個", "種: `20261027`", "予想（結果を見る前。判定には使わない）",
                   "--random-scales 10 --scale-range inside 1e-7 1e-4 --coef-seed 20261027", "`eps_generality.py` は変えない",
                   "倍率は報告だけで基準はない"):
        assert needle in sec, needle
    assert "（1e-5 以上 3 個、1e-6 以上 1e-5 未満 3 個、1e-7 以上 1e-6 未満 4 個）" in sec
    assert "PR #24 は触らない" in sec and "「矛盾する材料はなかった」とは書かない" in sec


def test_the_numbers_in_the_predictions_are_the_numbers_of_the_posthoc_grid_json():
    st = json.loads((DIR / "results-random" / "staple" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))["staple"]
    ph = json.loads((DIR / "results-physical" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))
    sec = section()
    n_hi = sum(v >= 1e-5 for v in REGISTERED_5)
    n_mid = sum(1e-6 <= v < 1e-5 for v in REGISTERED_5)
    n_lo = sum(v < 1e-6 for v in REGISTERED_5)
    assert (n_hi, n_mid, n_lo) == (3, 3, 4)
    for name, d in (("主食価格", st), ("物理量の月次", ph["monthly"]), ("物理量の日次", ph["daily"])):
        c = {k: v["forms_changed"] for k, v in d["tolerance_unchanged"].items()}
        line = (f"- {name}: 1e-5 以上（{n_hi} 個）は {c['0.0001']}〜{c['1e-05']}、1e-6 以上 1e-5 未満（{n_mid} 個）は {c['1e-05']}〜{c['1e-06']}、"
                f"1e-7 以上 1e-6 未満（{n_lo} 個）は {c['1e-06']}〜{c['1e-07']}")
        assert line in sec, line
        assert c["0.0001"] <= c["1e-05"] <= c["1e-06"] <= c["1e-07"]                                    # 格子の値は倍率が小さいほど多い（予想 (a) の土台）
    assert ph["monthly"]["tolerance_unchanged"]["1e-05"]["forms_changed"] == 0                         # 予想 (c)


def scaleband_small_csv(tmp_path):
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = [{"country": "AAA", "date": f"{2020 + i // 12:04d}-{i % 12 + 1:02d}-01", "year": str(2020 + i // 12), "variable": f"staple_price:c{j}",
             "value": str(3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)), "unit": "USD per kg",
             "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""} for j in range(3) for i in range(48)]
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def test_the_registered_command_runs_writes_the_registered_scales_and_no_epsilons_and_is_byte_reproducible(tmp_path):
    flags = ("--random-scales", "10", "--scale-range", "inside", "1e-7", "1e-4", "--coef-seed", "20261027")
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert scaleband_gen.main(["--csv", str(scaleband_small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT), *flags]) == 0
        outs.append(out)
    for n in sorted(p.name for p in outs[0].iterdir()):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    j = json.loads((outs[0] / "eps_generality.json").read_text(encoding="utf-8"))
    rc = j["random_coefficients"]
    assert rc["seed"] == SCALEBAND_SEED and rc["eps"] == [] and [d["value"] for d in rc["scales"]] == REGISTERED_5
    assert rc["regions"] == {"scales": {"mode": "inside", "lo": SCALEBAND_LO, "hi": SCALEBAND_HI}}
    assert set(j["scales"]) >= {f"{v:g}" for v in REGISTERED_5} and j["control"]["pass"] and j["repeat_identical"]


# ---- 置いた結果（実データ）が、登録した値・予想・格子の JSON・READMEと合っている -----------------------------------------------
RES = DIR / "results-scale-band"
NAMES = (("staple", "主食価格の月次"), ("monthly", "物理量の月次"), ("daily", "物理量の日次"))


def result(k):
    return json.loads((RES / k / "eps_generality.json").read_text(encoding="utf-8"))


def grid_of(k):
    if k == "staple":
        return json.loads((DIR / "results-random" / "staple" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))["staple"]["tolerance_unchanged"]
    return json.loads((DIR / "results-physical" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))[k]["tolerance_unchanged"]


def bracket(v, d):
    n = lambda key: d[key]["forms_changed"]
    return (n("0.0001"), n("1e-05")) if v >= 1e-5 else (n("1e-05"), n("1e-06")) if v >= 1e-6 else (n("1e-06"), n("1e-07"))


@pytest.mark.parametrize("k", [k for k, _ in NAMES])
def test_results_record_the_registered_scales_seed_and_range_with_a_passed_control(k):
    j = result(k)
    rc = j["random_coefficients"]
    assert rc["seed"] == SCALEBAND_SEED and rc["eps"] == [] and [d["value"] for d in rc["scales"]] == REGISTERED_5
    assert rc["regions"] == {"scales": {"mode": "inside", "lo": SCALEBAND_LO, "hi": SCALEBAND_HI}} and "regions" not in j
    assert j["control"]["pass"] and j["repeat_identical"]
    assert "- 倍率を選んだ範囲: inside（1.00×10^-7 〜 1.00×10^-4" in (RES / k / "eps_generality.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("k", [k for k, _ in NAMES])
def test_the_registered_predictions_hold_in_the_results(k):
    j, d = result(k), grid_of(k)
    rows = [j["scales"][f"{v:g}"] for v in REGISTERED_5]                                               # 大きい順
    cnt = [r["forms_changed"] for r in rows]
    assert all(a <= b for a, b in zip(cnt, cnt[1:]))                                                    # (a)
    assert all(bracket(v, d)[0] <= r["forms_changed"] <= bracket(v, d)[1] for v, r in zip(REGISTERED_5, rows))          # (b)
    if k == "monthly":
        assert all(r["forms_changed"] == 0 for v, r in zip(REGISTERED_5, rows) if v >= 1e-5)           # (c)
    assert all(r["boundary_flag_changed"] == 0 for r in rows if r["forms_changed"] == 0)               # (d)


def table_rows(k):
    j, d = result(k), grid_of(k)
    out = []
    for v in REGISTERED_5:
        r = j["scales"][f"{v:g}"]
        lo, hi = bracket(v, d)
        dev = "-" if r["coefficient_max_dev"] is None else f"{r['coefficient_max_dev']:.2e}".replace("e-0", "e-").replace("e+0", "e+")
        out.append(f"| {scaleband_gen.pow10_text(v)} | {r['forms_changed']} | {lo}〜{hi} | {r['boundary_flag_changed']} | {r['boundary']} | {dev} |")
    return out


@pytest.mark.parametrize("k,name", NAMES)
def test_the_readme_tables_are_the_json_numbers(k, name):
    md = (RES / "README.md").read_text(encoding="utf-8")
    j = result(k)
    head = f"### {name}（24 点の窓 {j['scales']['1']['units']} 単位、倍率 1 で境界の単位 {j['scales']['1']['boundary']}）"
    block = md[md.index(head):]
    block = block[:block.index("\n\n###")] if "\n\n###" in block else block
    for row in table_rows(k):
        assert row in block, row


def test_the_readme_figures_in_the_text_are_the_json_numbers():
    md = (RES / "README.md").read_text(encoding="utf-8")
    c = {k: {v: result(k)["scales"][f"{v:g}"] for v in REGISTERED_5} for k, _ in NAMES}
    units = {k: result(k)["scales"]["1"]["units"] for k, _ in NAMES}
    boundary = {k: result(k)["scales"]["1"]["boundary"] for k, _ in NAMES}
    assert [c[k][9.57e-5]["forms_changed"] + c[k][5.98e-5]["forms_changed"] for k, _ in NAMES] == [0, 0, 0]
    assert [c[k][3.16e-5]["forms_changed"] for k, _ in NAMES] == [1, 0, 1]
    assert f"{c['staple'][8.91e-6]['forms_changed']} / {c['monthly'][8.91e-6]['forms_changed']} / {c['daily'][8.91e-6]['forms_changed']} 単位" in md
    assert f"{c['staple'][1.92e-6]['forms_changed']} / {c['monthly'][1.92e-6]['forms_changed']} / {c['daily'][1.92e-6]['forms_changed']} 単位" in md
    for k, _ in NAMES:                                                                                  # 半分を超えるのは 1.92e-6 と 9.50e-7 の間
        assert c[k][1.92e-6]["forms_changed"] < units[k] / 2 < c[k][9.5e-7]["forms_changed"]
    assert f"（主食価格 2192 単位の半分は 1096 で、1.92×10^-6 は {c['staple'][1.92e-6]['forms_changed']}、9.50×10^-7 は {c['staple'][9.5e-7]['forms_changed']}。" in md
    assert units == {"staple": 2192, "monthly": 221, "daily": 478}
    assert f"{boundary['staple']} / {boundary['monthly']} / {boundary['daily']} 単位" in md
    assert [c[k][1.03e-7]["boundary"] for k, _ in NAMES] == [0, 0, 0] and [c[k][1.03e-7]["boundary_flag_changed"] for k, _ in NAMES] == [boundary[k] for k, _ in NAMES]
    last = f"{c['staple'][1.03e-7]['forms_changed']} / {c['monthly'][1.03e-7]['forms_changed']} / {c['daily'][1.03e-7]['forms_changed']}"
    grid = " / ".join(str(grid_of(k)["1e-07"]["forms_changed"]) for k, _ in NAMES)
    assert f"式が変わった単位は {last} で、格子の 1×10^-7 の値（{grid}）" in md
    devs = [c["staple"][v]["coefficient_max_dev"] for v in (1.92e-6, 9.5e-7, 8.63e-7, 7.66e-7)]
    assert f"{min(devs):.2f}〜{max(devs):.2f}" in md and all(1.27 <= x <= 1.31 for x in devs)


def test_the_only_criterion_not_met_is_the_known_hand_set_epsilon_c2_in_the_staple_12_month_window():
    bad = [(k, c["id"], c["set"]) for k, _ in NAMES for c in result(k)["criteria"] if c["ok"] is not True]
    assert bad == [("staple", "C2", "N=12")]
    md = (RES / "README.md").read_text(encoding="utf-8")
    assert "主食価格の 12 か月の窓の C2（決め打ちの ε=1e-3、第 1 回から同じ）の 1 件だけ" in md


# ==== window（旧 test_epsilon_generality_window_crossing.py）
# research/epsilon-generality/eps_posthoc.py の window_crossing（旧 posthoc_window_crossing.py）の確認。
#
# SYNTHETIC: 組み立てた関数・小さな合成の系列で、二分・60 点の並び・許容の差し替えと戻し・窓の取り出し・誤差の2乗和・書き出しが
# 約束どおりに動くことを確かめる。実データの結果（予想に当たったか）はここでは確かめない（結論には使わない）。
# 窓の指定（梯子の 2 点）が、コミット済みの梯子の結果と合っていることだけは確かめる。


STAPLE = ROOT / "research" / "staple-price-survey" / "staple_survey_vertical.csv"


wc = load("eps_posthoc")
window_gen = wc.gen
window_sa, window_trial = window_gen.load_modules(ROOT)
WINDOW_COLS = ["country", "variable", "unit", "source", "note", "date", "value"]


def window_write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=WINDOW_COLS)
        w.writeheader()
        w.writerows(rows)


def series_rows(country, variable, start_month, values):
    return [{"country": country, "variable": variable, "unit": "u", "source": "s", "note": "",
             "date": f"{2020 + (start_month + i) // 12}-{(start_month + i) % 12 + 1:02d}-15", "value": v} for i, v in enumerate(values)]


WAVY = [0.0, 1.2, 2.9, 3.1, 2.2, 1.4, 1.9, 3.0, 3.4, 2.7, 2.1, 2.5]


# ---- 二分・並び -------------------------------------------------------------------------------------------------------
def test_bisect_brackets_the_switch_within_the_relative_width():
    a, b = wc.bisect(lambda e: "after" if e >= 6.3e-3 else "before", 5e-3, 7e-3)
    assert a < 6.3e-3 <= b and b / a - 1 < wc.REL_WIDTH


def test_bisect_handles_a_switch_that_sits_on_the_upper_end():
    a, b = wc.bisect(lambda e: "after" if e >= 7e-3 else "before", 5e-3, 7e-3)
    assert a < 7e-3 and b == 7e-3 and b / a - 1 < wc.REL_WIDTH


def test_bisect_refuses_when_the_two_ends_are_the_same_form():
    with pytest.raises(ValueError, match="挟めない"):
        wc.bisect(lambda e: "same", 5e-3, 7e-3)


def test_grid_is_geometric_from_lo_to_the_top_and_counts_the_points():
    g = wc.grid(7e-4)
    assert len(g) == wc.GRID_POINTS and g[0] == 7e-4 and math.isclose(g[-1], wc.EPS_TOP)
    ratios = [b / a for a, b in zip(g, g[1:])]
    assert all(math.isclose(r, ratios[0]) for r in ratios) and ratios[0] > 1


def test_changes_along_counts_each_switch_including_a_return():
    assert wc.changes_along(["a", "a", "b", "b"]) == 1
    assert wc.changes_along(["a", "b", "a", "a"]) == 2
    assert wc.changes_along(["a"]) == 0 and wc.changes_along([]) == 0


# ---- 許容の差し替え --------------------------------------------------------------------------------------------------
def test_tie_tolerance_sets_the_value_and_restores_it_even_when_the_body_fails():
    old = window_sa.EPS_WAVE_TIE
    with wc.tie_tolerance(window_sa, 5.0):
        assert window_sa.EPS_WAVE_TIE == 5.0
    assert window_sa.EPS_WAVE_TIE == old
    with pytest.raises(RuntimeError):
        with wc.tie_tolerance(window_sa, 5.0):
            raise RuntimeError("x")
    assert window_sa.EPS_WAVE_TIE == old


def test_form_at_uses_the_given_tolerance_and_the_current_one_by_default():
    ys = window_gen.normalize(WAVY)[1]
    now = wc.form_at(window_sa, window_trial, ys, 1e-3)
    assert wc.form_at(window_sa, window_trial, ys, 1e-3, window_sa.EPS_WAVE_TIE) == now
    huge = wc.form_at(window_sa, window_trial, ys, 1e-3, 1e6)                        # 許容が大きいと、先頭の式（波なし）から動かない
    assert huge[1] is None and huge[0] != "ε"
    assert window_sa.EPS_WAVE_TIE == 1e-12                                    # 差し替えたあと元に戻っている


def test_form_at_labels_a_wave_that_kept_the_epsilon_decay_and_sse_of_scores_it_at_zero():
    eps, per, n = 1e-3, 0.5, 12
    w, lim, bb = 2 * math.pi / per, 3.0, 2.0                          # 始まりが 0 で、減衰が ε の波そのもの（ノイズなし）
    ys = [lim + math.exp(-eps * i / (n - 1)) * ((0.0 - lim) * math.cos(w * i / (n - 1)) + bb * math.sin(w * i / (n - 1))) for i in range(n)]
    f = wc.form_at(window_sa, window_trial, ys, eps)
    # 浮動小数の足し算の丸めは Python のバージョンで違う（3.11 では 7e-15、3.12 以降はほぼ 0）。試した ほかの式（減衰 3 通り×周期 3 通りと ε 波の周期 5 通り）の誤差は 3.9 以上なので、1e-10 で足りる
    assert f == ("ε", per) and wc.sse_of(window_sa, window_trial, ys, eps, f) < 1e-10


def test_sse_of_equals_the_fitted_rmse_for_the_form_that_wave_fit_chose():
    ys = window_gen.normalize(WAVY)[1]
    n, eps = len(ys), 1e-3
    basis = window_trial.make_wave_basis(window_sa, eps)([i / (n - 1) for i in range(n)])
    with window_gen.settle_tolerance(window_sa, window_gen.PRIMARY_TAU):
        f = window_sa.wave_fit(ys, basis, 0.0, 1.0)
    form = wc.form_at(window_sa, window_trial, ys, eps)
    assert math.isclose(wc.sse_of(window_sa, window_trial, ys, eps, form), n * f["rmse"] ** 2, rel_tol=1e-9)


# ---- 窓の取り出し ----------------------------------------------------------------------------------------------------
def test_window_values_picks_the_named_window_and_normalizes_it(tmp_path):
    rows = series_rows("AAA", "staple_price:x", 0, WAVY) + series_rows("BBB", "staple_price:x", 0, [v * 2 for v in WAVY])
    window_write_rows(tmp_path / "a.csv", rows)
    series = window_gen.read_series(tmp_path / "a.csv")
    spec = {"id": "t", "n": 12, "country": "BBB", "variable": "staple_price:x", "start": "2020-01"}
    ys = wc.window_values(series, spec, window_gen.month_text)
    assert ys == window_gen.normalize([v * 2 for v in WAVY])[1] and max(ys) - min(ys) == pytest.approx(window_gen.SCALE)


@pytest.mark.parametrize("country,start", [("CCC", "2020-01"), ("AAA", "2021-01")])
def test_window_values_stops_when_the_window_is_missing(tmp_path, country, start):
    window_write_rows(tmp_path / "a.csv", series_rows("AAA", "staple_price:x", 0, WAVY))
    spec = {"id": "t", "n": 12, "country": country, "variable": "staple_price:x", "start": start}
    with pytest.raises(ValueError, match="0 個"):
        wc.window_values(window_gen.read_series(tmp_path / "a.csv"), spec, window_gen.month_text)


def test_window_values_stops_when_the_window_is_constant(tmp_path):
    window_write_rows(tmp_path / "a.csv", series_rows("AAA", "staple_price:x", 0, [3.0] * 12))
    spec = {"id": "t", "n": 12, "country": "AAA", "variable": "staple_price:x", "start": "2020-01"}
    with pytest.raises(ValueError, match="一定"):
        wc.window_values(window_gen.read_series(tmp_path / "a.csv"), spec, window_gen.month_text)


# ---- 組み立てた「式の選び方」で、表の数え方を確かめる ------------------------------------------------------------------------
SPEC = {"id": "fake", "n": 12, "start": "2020-01", "lo": 5e-3, "hi": 7e-3}
THRESHOLD = {None: 6e-3, 1e-12: 6e-3, 1e-15: 5.9e-3, 1e-9: 6.12e-3}          # 許容ごとの、式が切り替わる ε（許容に少し左右される）


def fake_form_at(sa_, mod_, ys, eps, tol=None):
    return ("ε", 1.0) if eps < THRESHOLD[tol] else ("ε", 0.75)


def fake_sse_of(sa_, mod_, ys, eps, form):
    near = 5.9e-3 < eps < 6.2e-3
    if form == ("ε", 1.0):
        return 1.0
    return (1.0 + (0.002 if eps < 6e-3 else -0.003)) if near else 1.5


def test_shift_is_taken_against_the_current_tolerance_and_is_the_largest_over_the_tolerances(monkeypatch):
    monkeypatch.setattr(wc, "form_at", fake_form_at)
    monkeypatch.setattr(wc, "sse_of", fake_sse_of)
    w = wc.analyse_window(window_sa, window_trial, [0.0, 1.0] * 6, SPEC)
    t = w["by_tolerance"]
    assert t["1e-12"]["eps_star"] == pytest.approx(6e-3, rel=1e-3) and t["1e-15"]["eps_star"] == pytest.approx(5.9e-3, rel=1e-3)
    assert w["rel_shift_of_eps_star"] == pytest.approx(0.02, abs=2e-3)         # 6.12/6 − 1。1e-15 側は −1.7%、基準を取り違えると 3.6% になる
    assert w["changes_along_grid"] == 1 and w["form_lo"] == ["ε", 1.0] and w["form_hi"] == ["ε", 0.75]


def test_the_edge_check_uses_only_the_two_points_next_to_the_switch(monkeypatch):
    monkeypatch.setattr(wc, "form_at", fake_form_at)
    monkeypatch.setattr(wc, "sse_of", fake_sse_of)
    w = wc.analyse_window(window_sa, window_trial, [0.0, 1.0] * 6, SPEC)
    assert w["gaps"][0]["eps"] < 6e-3 <= w["gaps"][1]["eps"]
    assert w["edge_rel_diff"] == pytest.approx(0.003 / 0.997, rel=1e-6) and w["edge_rel_diff"] < 1e-2
    assert max(abs(g["diff"]) for g in w["gaps"][2:]) == pytest.approx(0.5)     # 登録した ε の3点は大きく離れている（端の確認には入れない）


def test_main_stops_without_writing_when_two_runs_on_the_same_input_differ(tmp_path, monkeypatch):
    results = iter([{"windows": [], "skipped": ["a"]}, {"windows": [], "skipped": ["b"]}])
    monkeypatch.setattr(wc, "window_crossing_analyse", lambda *a, **k: next(results))
    out = tmp_path / "o"
    assert wc.window_crossing(["--staple-csv", str(STAPLE), "--outdir", str(out), "--repo", str(ROOT)]) == 2
    assert not out.exists()


# ---- 窓の指定は、コミット済みの梯子の結果と合っている ----------------------------------------------------------------
LADDERS = {"staple": DIR / "results-random" / "staple" / "posthoc_eps_ladder.json",
           "physical-monthly": DIR / "results-random" / "monthly" / "posthoc_eps_ladder.json"}


@pytest.mark.parametrize("spec", wc.WINDOWS, ids=lambda s: s["id"])
def test_each_window_spec_matches_the_committed_ladder(spec):
    moved = json.loads(LADDERS[spec["input"]].read_text(encoding="utf-8"))["sets"][str(spec["n"])]["moved"]
    hits = [m for m in moved if m["country"] == spec["country"] and m["variable"] == spec["variable"] and m["start"] == spec["start"]]
    assert len(hits) == 1
    path = {p["eps"]: p for p in hits[0]["path"]}
    lo, hi = path[spec["lo"]], path[spec["hi"]]
    ladder = json.loads(LADDERS[spec["input"]].read_text(encoding="utf-8"))["ladder"]
    assert ladder.index(spec["hi"]) == ladder.index(spec["lo"]) + 1                # 梯子で隣どうし
    assert (lo["decay"] == spec["lo"]) and ((hi["decay"], hi["period"]) != (spec["hi"], lo["period"]))     # 下は ε の波のまま、上は式が違う


# ---- 実データの入力（主食価格）での動き -----------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def staple_inputs():
    prof = window_gen.PROFILES["staple"]
    return {"staple": (window_gen.read_series(STAPLE, prof["prefix"], prof["cadence"]), window_gen.CADENCE["month"]["text"])}


@pytest.fixture(scope="module")
def staple_result(staple_inputs):
    return wc.window_crossing_analyse(window_sa, window_trial, staple_inputs)


def test_analyse_skips_the_windows_whose_input_is_absent_and_lists_them(staple_result):
    assert [w["id"] for w in staple_result["windows"]] == [s["id"] for s in wc.WINDOWS if s["input"] == "staple"]
    assert staple_result["skipped"] == [s["id"] for s in wc.WINDOWS if s["input"] != "staple"]


def test_analysis_fields_are_what_the_render_and_the_predictions_use(staple_result):
    for w in staple_result["windows"]:
        assert set(w["by_tolerance"]) == {"1e-15", "1e-12", "1e-09"}
        for v in w["by_tolerance"].values():
            assert v["below"] < v["eps_star"] < v["above"] and v["above"] / v["below"] - 1 < wc.REL_WIDTH
        assert [g["label"] for g in w["gaps"]] == ["ε* の下", "ε* の上", "1e-3", "1e-6", "1e-9"]
        assert all(math.isclose(g["diff"], g["sse_after"] - g["sse_before"], abs_tol=1e-15) for g in w["gaps"])
        assert w["changes_along_grid"] >= 1
        assert w["form_lo"] != w["form_hi"] and w["bracket"][0] < w["bracket"][1]


def test_the_form_just_below_and_above_the_switch_is_what_bisect_promised(staple_result):
    for w in staple_result["windows"]:
        base = w["by_tolerance"]["1e-12"]
        below, above = w["gaps"][0], w["gaps"][1]
        assert tuple(below["chosen"]) == tuple(w["form_lo"]) and tuple(above["chosen"]) != tuple(w["form_lo"])
        assert below["eps"] == base["below"] and above["eps"] == base["above"]


def test_render_has_one_row_per_window_a_section_per_window_and_the_skipped_ones(staple_result):
    md = wc.window_crossing_render(staple_result)
    for w in staple_result["windows"]:
        assert f"## {w['id']}" in md and f"| {w['id']}（{w['n']} 点、{w['start']} から）" in md
    assert "入力が無くて飛ばした窓: Mauna Loa CO2" in md and md.count("## ") == len(staple_result["windows"])


def test_main_writes_json_and_md_reproducibly_and_needs_an_input(tmp_path, capsys):
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    for out in (out1, out2):
        assert wc.window_crossing(["--staple-csv", str(STAPLE), "--outdir", str(out), "--repo", str(ROOT)]) == 0
    for name in ("posthoc_window_crossing.json", "posthoc_window_crossing.md"):
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()
    with pytest.raises(SystemExit) as e:
        wc.window_crossing(["--outdir", str(tmp_path / "o3")])
    assert e.value.code == 2


def test_the_prediction_is_written_before_the_run_and_names_what_is_not_claimed():
    doc = wc.WINDOW_CROSSING_DOC
    for tag in ("(a)", "(b)", "(c)", "(d)", "(e)"):
        assert tag in doc
    assert "走らせる前に書く" in doc and "ε の値をどうするかは決めない" in doc and "この 3 窓" in doc


# ---- 置いた結果（実データ）が、JSON・予想・READMEと合っている ------------------------------------------------------------
RESULTS = DIR / "results-random" / "window-crossing"
README_RANDOM = DIR / "results-random" / "README.md"
README_MAIN = DIR / "README.md"


def results_json():
    return json.loads((RESULTS / "posthoc_window_crossing.json").read_text(encoding="utf-8"))


def sci(x):
    m, e = f"{x:.2e}".split("e")
    return f"{m}×10^{int(e)}"


def form(f):
    return f"周期 {'なし' if f[1] is None else format(f[1], 'g')}" + ("" if f[0] == "ε" else f"（減衰 {f[0]:g}）")


def readme_row(w):
    t = w["by_tolerance"]["1e-12"]
    es = (t["below"] * t["above"]) ** 0.5
    g = {x["label"]: x for x in w["gaps"]}
    g9, g3 = g["1e-9"], g["1e-3"]
    chosen = " / ".join(form(g[k]["chosen"]) for k in ("1e-3", "1e-6", "1e-9"))
    return (f"| {w['id']}（{w['n']} 点、{w['start']} から） | {w['bracket'][0]:g} / {w['bracket'][1]:g} | {form(w['form_lo'])} → {form(w['form_hi'])} | "
            f"{sci(es)} | {chosen} | {w['changes_along_grid']} | {sci(w['edge_rel_diff'])} | {g9['diff'] / g9['sse_before'] * 100:.2f}% | "
            f"{g3['diff']:.3g} / {g9['diff'] * (1 - 1e-3 / es):.3g} |")


def test_the_md_in_the_results_is_what_render_makes_from_the_json():
    assert (RESULTS / "posthoc_window_crossing.md").read_text(encoding="utf-8") == wc.window_crossing_render(results_json())


def test_the_written_predictions_hold_in_the_results_json_as_the_readme_says():
    j = results_json()
    assert [w["id"] for w in j["windows"]] == [s["id"] for s in wc.WINDOWS] and j["skipped"] == []
    for w in j["windows"]:
        spec = next(s for s in wc.WINDOWS if s["id"] == w["id"])
        assert w["bracket"] == [spec["lo"], spec["hi"]] and w["form_lo"] != w["form_hi"]                              # (a)
        assert len({(v["below"], v["above"]) for v in w["by_tolerance"].values()}) == 1                                # (b) 0.1% の幅の中で動かない
        assert w["rel_shift_of_eps_star"] < wc.REL_WIDTH                                                               # (b)
        assert w["changes_along_grid"] == 1                                                                            # (c)
        assert w["edge_rel_diff"] < 1e-3                                                                               # (d)
    chosen = {w["id"]: {g["label"]: g["chosen"] for g in w["gaps"]} for w in j["windows"]}
    mda, nic, mlo = (chosen[s["id"]] for s in wc.WINDOWS)
    assert mda["1e-3"] != mda["1e-6"] == mda["1e-9"]                                                                   # (e) 登録した ε で変わるのは MDA の 1e-3 だけ
    assert nic["1e-3"] == nic["1e-6"] == nic["1e-9"] and mlo["1e-3"] == mlo["1e-6"] == mlo["1e-9"]


def test_the_readme_table_rows_and_figures_are_the_json_numbers():
    j, md = results_json(), README_RANDOM.read_text(encoding="utf-8")
    for w in j["windows"]:
        assert readme_row(w) in md
    edges = [w["edge_rel_diff"] for w in j["windows"]]
    assert f"誤差の2乗和の {sci(min(edges))}〜{sci(max(edges))} 倍" in md
    ratios = []
    for w in j["windows"]:
        t = w["by_tolerance"]["1e-12"]
        es = (t["below"] * t["above"]) ** 0.5
        g = {x["label"]: x for x in w["gaps"]}
        ratios.append(g["1e-3"]["diff"] / (g["1e-9"]["diff"] * (1 - 1e-3 / es)))
    assert "（比は " + "、".join(f"{r:.4f}" for r in ratios) + "）" in md
    main = README_MAIN.read_text(encoding="utf-8")
    for w, shown in zip(j["windows"], ("7.43×10^-4", "5.98×10^-3", "9.50×10^-3")):
        t = w["by_tolerance"]["1e-12"]
        assert sci((t["below"] * t["above"]) ** 0.5) == shown and shown in main and shown in md
