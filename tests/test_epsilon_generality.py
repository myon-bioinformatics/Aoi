"""research/epsilon-generality/eps_generality.py の確認。

SYNTHETIC: 小さな合成の入力（実データではない）で、窓の作り方・正規化・基準の判定（境界の値ちょうどを含む）・
合成の系列・対照・書き出しを確かめる。結論には使わない。
"""
import csv
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
spec = importlib.util.spec_from_file_location("eps_generality", DIR / "eps_generality.py")
gen = importlib.util.module_from_spec(spec)
sys.modules["eps_generality"] = gen
spec.loader.exec_module(gen)
sa, trial = gen.load_modules(ROOT)


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
    assert gen.month_text(gen.month_index("2020-12-15")) == "2020-12"
    assert gen.month_index("2021-01-01") - gen.month_index("2020-12-31") == 1
    for bad in ("2020-13-01", "2020-00-01", "20200101", "2020-1-1"):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            gen.month_index(bad)


def test_read_series_keeps_only_staple_prices_and_separates_series_by_note_and_ignores_the_day(tmp_path):
    rows = month_rows(3) + month_rows(3, key=("AAA", "staple_price:rice", "USD per kg", "https://github.com/tezamo/FPMA (x)", "market=m2"), day="15")
    rows += [dict(month_rows(1)[0], variable="bigmac_local_price")]
    s = gen.read_series(write_csv(tmp_path / "s.csv", rows))
    assert len(s) == 2 and all(len(v) == 3 for v in s.values())


def test_read_series_stops_on_a_repeated_month_or_a_non_finite_value(tmp_path):
    with pytest.raises(ValueError, match="同じ月が 2 つある"):
        gen.read_series(write_csv(tmp_path / "a.csv", month_rows(2) + [dict(month_rows(1)[0], date="2020-01-15")]))
    with pytest.raises(ValueError, match="有限でない"):
        gen.read_series(write_csv(tmp_path / "b.csv", month_rows(2, values=["1", "nan"])))


def test_tile_makes_non_overlapping_windows_inside_unbroken_runs_and_drops_the_remainder():
    series = {"k": {i: float(i) for i in range(0, 7)} | {i: float(i) for i in range(10, 14)}}       # 7 か月 + 4 か月（3 か月の空き）
    w = gen.tile(series, 3)
    assert [(x["start"], x["values"]) for x in w] == [(gen.month_text(0), [0.0, 1.0, 2.0]), (gen.month_text(3), [3.0, 4.0, 5.0]),
                                                      (gen.month_text(10), [10.0, 11.0, 12.0])]
    assert gen.tile(series, 8) == []
    assert gen.tile({"k": {0: 1.0, 2: 2.0, 4: 3.0}}, 2) == []            # 1 か月おきは「途切れている」


def test_tile_is_sorted_by_series_key_and_a_window_does_not_cross_series():
    series = {"b": {i: 1.0 for i in range(4)}, "a": {i: 2.0 for i in range(4)}}
    assert [w["key"] for w in gen.tile(series, 4)] == ["a", "b"]
    assert [w["si"] for w in gen.tile(series, 4)] == [0, 1] and [w["si"] for w in gen.tile(series, 2)] == [0, 0, 1, 1]


def test_normalize_puts_x_in_unit_interval_and_y_at_zero_start_with_range_five():
    xs, ys, s = gen.normalize([10.0, 14.0, 12.0, 20.0])
    assert xs == [0.0, 1 / 3, 2 / 3, 1.0] and ys[0] == 0.0 and s == 0.5
    assert max(ys) - min(ys) == 5.0 and ys == [0.0, 2.0, 1.0, 5.0]
    _, ys2, _ = gen.normalize([10.0, 4.0, 5.0])
    assert max(ys2) - min(ys2) == pytest.approx(5.0) and ys2[0] == 0.0 and min(ys2) == pytest.approx(-5.0)
    assert gen.normalize([3.0, 3.0, 3.0]) is None


def test_source_group_names():
    assert [gen.source_group(u) for u in (
        "https://github.com/tezamo/FPMA (all_commodity)", "https://data.humdata.org/dataset/wfp-food-prices (x)",
        "https://data.humdata.org/dataset/global-wfp-food-prices (x)", "https://www.bls.gov/data/", "https://www.e-stat.go.jp/", "x")] == [
        "FPMA", "WFP", "WFP-yearly", "BLS", "e-Stat", "other"]


# ---- 当てはめ ----------------------------------------------------------------------------------------------------------
def test_settle_tolerance_is_restored_even_when_the_body_fails():
    old = sa.WAVE_SETTLE
    with pytest.raises(RuntimeError):
        with gen.settle_tolerance(sa, 7.0):
            assert sa.WAVE_SETTLE == 7.0
            raise RuntimeError("x")
    assert sa.WAVE_SETTLE == old


def undamped_ys(period=1.0, phi=0.7, n=24, noise=0.0):
    xs = [i / (n - 1) for i in range(n)]
    v = [3.0 + 2.0 * math.cos(2 * math.pi * x / period + phi) for x in xs]
    xs, ys, s = gen.normalize(v)
    return xs, ys, s


def test_fit_row_on_an_undamped_wave_is_a_boundary_unit_and_epsilon_gives_finite_values_with_a_stable_coefficient():
    xs, ys, s = undamped_ys()
    bases = gen.make_bases(sa, trial, xs)
    r = gen.fit_row(sa, bases, ys, 0.5)
    assert r["boundary"] and r["decay"] == 0.0 and r["period"] == 1.0 and r["limit"] is None and r["settle_x"] is None
    for e in gen.EPS:
        f = r[gen.ekey(e)]
        assert f["decay"] == e and f["period"] == 1.0 and f["limit"] is not None and f["settle_x"] is not None and not f["at_start"]
        assert f["coefficient"] == f["settle_x"] * e                                       # 位置 = 係数 × 10^n
        assert 0.5 * math.exp(f["coefficient"]) == pytest.approx(2.0 * s, rel=1e-2)       # 戻した振幅 = 真の振幅
    c = [r[gen.ekey(e)]["coefficient"] for e in gen.EPS]
    assert abs(c[1] - c[2]) / c[2] < 1e-4 and abs(c[0] - c[2]) / c[2] < 2e-2


def test_fit_row_marks_a_wave_that_is_already_inside_tolerance_as_settled_at_start():
    xs, ys, _ = undamped_ys()
    bases = gen.make_bases(sa, trial, xs)
    r = gen.fit_row(sa, bases, ys, 1000.0)
    f = r[gen.ekey(1e-6)]
    assert r["boundary"] and f["at_start"] and f["coefficient"] is None and f["settle_x"] == 0.0 and r["settle_x"] == 0.0


def test_fit_row_leaves_a_damped_wave_alone():
    xs = [i / 23 for i in range(24)]
    v = [3.0 + 2.0 * math.exp(-3 * x) * math.cos(2 * math.pi * x / 0.5 + 0.4) for x in xs]
    xs, ys, _ = gen.normalize(v)
    r = gen.fit_row(sa, gen.make_bases(sa, trial, xs), ys, 0.5)
    assert not r["boundary"] and r["decay"] == 3.0 and r["period"] == 0.5
    assert all((r[gen.ekey(e)]["decay"], r[gen.ekey(e)]["period"]) == (3.0, 0.5) for e in gen.EPS)


def test_the_selected_form_does_not_depend_on_tau():
    xs, ys, _ = undamped_ys()
    bases = gen.make_bases(sa, trial, xs)
    forms = {(r["decay"], r["period"]) for r in (gen.fit_row(sa, bases, ys, t) for t in gen.TAUS)}
    assert len(forms) == 1


def test_tau_summary_reports_boundary_counts_and_that_forms_do_not_move():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": [3.0 + 2.0 * math.cos(2 * math.pi * x + p) for x in xs]} for p in (0.1, 0.7, 1.9)]
    t = gen.tau_summary(sa, gen.make_bases(sa, trial, xs), wins)
    assert list(t) == ["0.25", "0.5", "1"] and all(d["forms_same_as_first_tau"] for d in t.values())
    assert all(d["boundary"] == 3 for d in t.values())
    assert t["0.25"]["coefficient_min"] > t["0.5"]["coefficient_min"] > t["1"]["coefficient_min"]       # ln(振幅/τ): τ が大きいほど小さい


# ---- 合成の系列 --------------------------------------------------------------------------------------------------------
def test_synthetic_series_are_reproducible_and_differ_by_index_and_kind():
    sp = {s["id"]: s for s in gen.SYNTH}
    a = gen.synth_series(sp["undamped_p1"], 3)
    assert a == gen.synth_series(sp["undamped_p1"], 3) and a != gen.synth_series(sp["undamped_p1"], 4)
    assert a != gen.synth_series(sp["undamped_p0.5"], 3) and len(a) == gen.SYNTH_POINTS
    lin = gen.synth_series(sp["linear"], 0)
    assert lin[-1] - lin[0] == pytest.approx(2.0, abs=0.2)
    with pytest.raises(ValueError, match="合成の種類"):
        gen.synth_series({"id": "x", "kind": "zzz"}, 0)


def test_synthetic_undamped_series_come_out_as_boundary_units_with_the_true_amplitude():
    xs = [i / (gen.SYNTH_POINTS - 1) for i in range(gen.SYNTH_POINTS)]
    rows = gen.synth_rows(sa, gen.make_bases(sa, trial, xs), count=10)
    assert set(rows) == {s["id"] for s in gen.SYNTH} and all(len(v) == 10 for v in rows.values())
    assert all("true_amp" in r for sid in ("undamped_p1", "damped_l3") for r in rows[sid]) and "true_amp" not in rows["linear"][0]
    assert sum(r["boundary"] for r in rows["undamped_p1"]) == 10
    verdicts = gen.judge_synth(rows)
    assert [v["id"] for v in verdicts] == ["C5", "C5", "C3", "C3", "C3"] and verdicts[0]["ok"] is True and verdicts[1]["ok"] is True


# ---- 基準の判定（境界の値ちょうどを含む）------------------------------------------------------------------------------
def er(decay, period=1.0, coef=1.0, at_start=False, limit=1.0, settle=1.0):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": limit, "settle_x": settle, "coefficient": coef, "at_start": at_start}


def unit(boundary=True, overrides=None, **base):
    u = {"decay": 0.0 if boundary else 1.0, "period": 1.0, "rmse": 0.0, "limit": None, "settle_x": None, "boundary": boundary}
    u |= base
    for e in gen.EPS:
        u[gen.ekey(e)] = er(e if boundary else 1.0)
    for k, v in (overrides or {}).items():
        u[k] = er(**v) if isinstance(v, dict) else v
    return u


def crit(rows, tag="t"):
    return {(c["id"], c["text"][:14]): c for c in gen.judge_real(gen.stats(rows), tag)}


def get(verdicts, cid, needle):
    (c,) = [c for c in verdicts if c["id"] == cid and needle in c["text"]]
    return c


def test_c1_needs_98_percent_at_eps_1e3_and_all_at_the_smaller_epsilons():
    def case(n_bad, key):
        rows = [unit() for _ in range(100 - n_bad)] + [unit(overrides={key: {"decay": 1.0}}) for _ in range(n_bad)]
        return gen.judge_real(gen.stats(rows), "t")
    assert get(case(2, gen.ekey(1e-3)), "C1", "ε=0.001")["ok"] is True       # ちょうど 98%
    assert get(case(3, gen.ekey(1e-3)), "C1", "ε=0.001")["ok"] is False
    assert get(case(1, gen.ekey(1e-6)), "C1", "ε=1e-06")["ok"] is False
    assert get(case(1, gen.ekey(1e-9)), "C1", "ε=1e-09")["ok"] is False
    assert get(case(0, gen.ekey(1e-9)), "C1", "ε=1e-09")["ok"] is True
    for field, bad in (("period", None), ("limit", None), ("settle", None)):
        rows = [unit() for _ in range(99)] + [unit(overrides={gen.ekey(1e-9): {"decay": 1e-9, field: bad}})]
        assert get(gen.judge_real(gen.stats(rows), "t"), "C1", "ε=1e-09")["ok"] is False, field


def test_c2_compares_to_the_1e9_coefficient_and_counts_disagreement_about_settled_at_start():
    def case(key, coef, ref_coef=1.0, **extra):
        e = {gen.ekey(1e-3): 1e-3, gen.ekey(1e-6): 1e-6}[key]
        rows = [unit() for _ in range(30)] + [unit(overrides={key: dict(decay=e, coef=coef, **extra),
                                                              gen.ekey(1e-9): dict(decay=1e-9, coef=ref_coef)})]
        return gen.judge_real(gen.stats(rows), "t")
    assert get(case(gen.ekey(1e-3), 1.0199), "C2", "ε=0.001")["ok"] is True
    assert get(case(gen.ekey(1e-3), 1.0201), "C2", "ε=0.001")["ok"] is False
    assert get(case(gen.ekey(1e-3), 0.9801), "C2", "ε=0.001")["ok"] is True                # 下側も測る
    assert get(case(gen.ekey(1e-3), 0.9790), "C2", "ε=0.001")["ok"] is False
    assert get(case(gen.ekey(1e-6), 1.00009), "C2", "ε=1e-06")["ok"] is True
    assert get(case(gen.ekey(1e-6), 1.00011), "C2", "ε=1e-06")["ok"] is False
    assert get(case(gen.ekey(1e-6), 2.0, ref_coef=2.0002), "C2", "ε=1e-06")["ok"] is True       # 相対（基準の係数で割る）
    assert get(case(gen.ekey(1e-6), 2.0, ref_coef=2.0003), "C2", "ε=1e-06")["ok"] is False
    mism = case(gen.ekey(1e-3), None, at_start=True)
    c = get(mism, "C2", "ε=0.001")
    assert c["ok"] is False and "比べられない単位 1" in c["text"]


def test_c2_ignores_units_where_the_epsilon_wave_did_not_survive_because_c1_counts_them():
    rows = [unit() for _ in range(30)] + [unit(overrides={gen.ekey(1e-3): {"decay": 1.0, "coef": 500.0}})]
    v = gen.judge_real(gen.stats(rows), "t")
    assert get(v, "C2", "ε=0.001")["ok"] is True and get(v, "C1", "ε=0.001")["value"] == 30 / 31


def test_c3_counts_changed_forms_among_non_boundary_units_only():
    def case(n_bad, key, field="decay"):
        bad = {key: {"decay": 2.0 if field == "decay" else 1.0, "period": 0.5 if field == "period" else 1.0}}
        rows = [unit(False) for _ in range(200 - n_bad)] + [unit(False, overrides=bad) for _ in range(n_bad)]
        return gen.judge_real(gen.stats(rows), "t")
    assert get(case(4, gen.ekey(1e-3)), "C3", "ε=0.001")["ok"] is True          # 4/200 = 2%
    assert get(case(5, gen.ekey(1e-3)), "C3", "ε=0.001")["ok"] is False
    assert get(case(1, gen.ekey(1e-6)), "C3", "ε=1e-06")["ok"] is True          # 1/200 = 0.5%
    assert get(case(2, gen.ekey(1e-6)), "C3", "ε=1e-06")["ok"] is False
    assert get(case(2, gen.ekey(1e-9)), "C3", "ε=1e-09")["ok"] is False
    assert get(case(2, gen.ekey(1e-9), "period"), "C3", "ε=1e-09")["ok"] is False        # 周期の変化も数える
    boundary_change = [unit() for _ in range(30)] + [unit(overrides={gen.ekey(1e-3): {"decay": 2.0}})]
    c = get(gen.judge_real(gen.stats(boundary_change), "t"), "C3", "ε=0.001")
    assert c["value"] is None and c["ok"] is None                       # 境界の単位は C3 の母数に入らない


def test_small_sets_are_not_judged():
    rows = [unit() for _ in range(19)] + [unit(False) for _ in range(19)]
    assert all(c["ok"] is None for c in gen.judge_real(gen.stats(rows), "t"))
    rows = [unit() for _ in range(20)] + [unit(False) for _ in range(20)]
    assert all(c["ok"] is True for c in gen.judge_real(gen.stats(rows), "t"))
    only_nb = gen.judge_real(gen.stats([unit(False) for _ in range(25)]), "t")
    assert [c["ok"] for c in only_nb if c["id"] == "C3"] == [True] * 3 and all(c["ok"] is None for c in only_nb if c["id"] != "C3")
    assert gen.judge_real(gen.stats([]), "t")[0]["ok"] is None


def test_stats_reports_coefficient_range_and_settled_at_start_counts():
    rows = [unit(overrides={gen.ekey(1e-6): {"decay": 1e-6, "coef": c}}) for c in (0.5, 1.5)] + \
           [unit(overrides={gen.ekey(1e-6): {"decay": 1e-6, "coef": None, "at_start": True}})]
    st = gen.stats(rows)
    assert st["coefficient_range_eps6"] == [0.5, 1.5] and st["at_start"][gen.ekey(1e-6)] == 1 and st["boundary_share"] == 1.0


def synth_row(boundary=True, true_amp=2.5, coef=None, **over):
    r = unit(boundary) | {"true_amp": true_amp}
    if boundary:
        r[gen.ekey(1e-6)] = er(1e-6, coef=math.log(2.5 / 0.5) if coef is None else coef)
    return r | over


def test_c5_boundary_share_and_amplitude_error():
    def spec(n_boundary, n=100, **kw):
        return {"undamped_p1": [synth_row(True, **kw) for _ in range(n_boundary)] + [synth_row(False, **kw) for _ in range(n - n_boundary)]}
    assert gen.judge_synth(spec(90))[0]["ok"] is True and gen.judge_synth(spec(89))[0]["ok"] is False
    assert gen.judge_synth({"damped_l3": []})[0]["ok"] is None
    ok = gen.judge_synth(spec(100))[1]
    assert ok["ok"] is True and ok["value"] == pytest.approx(0.0, abs=1e-12)
    big = gen.judge_synth(spec(100, coef=math.log(2.5 * 1.049 / 0.5)))[1]
    small = gen.judge_synth(spec(100, coef=math.log(2.5 * 0.951 / 0.5)))[1]
    off = gen.judge_synth(spec(100, coef=math.log(2.5 * 1.051 / 0.5)))[1]
    assert big["ok"] is True and small["ok"] is True and off["ok"] is False
    assert gen.judge_synth(spec(100, coef=math.log(2.5 * 0.949 / 0.5)))[1]["ok"] is False                    # 小さいほうも測る
    unsettled = [synth_row(True, coef=None)]
    unsettled[0][gen.ekey(1e-6)] = er(1e-6, coef=None, at_start=True)
    c = gen.judge_synth({"undamped_p1": unsettled})[1]
    assert c["ok"] is False and c["value"] is None and "始まりの時点で決まったと出た系列 1" in c["text"]      # 幅が τ 以下に見えた = 外れ


def test_c5_damped_series_must_not_change_their_form():
    rows = [synth_row(False) for _ in range(200)]
    assert all(c["ok"] is True for c in gen.judge_synth({"damped_l3": rows})[2:])
    rows[0][gen.ekey(1e-6)] = er(2.0)
    v = gen.judge_synth({"damped_l3": rows})[2:]
    assert [c["ok"] for c in v] == [True, True, True]                          # 1/200 = 0.5% は ε=1e-6 で許容
    rows[1][gen.ekey(1e-6)] = er(2.0)
    assert gen.judge_synth({"damped_l3": rows})[3]["ok"] is False
    assert gen.judge_synth({"damped_l3": rows[:10]})[2]["ok"] is None


# ---- 対照・全体 ---------------------------------------------------------------------------------------------------------
def test_controls_pass_on_the_real_code_and_fail_when_the_basis_differs(monkeypatch):
    bases = {12: None, 24: None}
    c = gen.controls(sa, trial, bases)
    assert c["pass"] and set(c["eps0_basis_identical"]) == {"12", "24", f"synthetic{gen.SYNTH_POINTS}"}
    orig = trial.make_wave_basis

    def broken(sa_, eps):
        f = orig(sa_, eps)
        return lambda xs: [dict(b, uu=b["uu"] + 1e-9) for b in f(xs)]
    monkeypatch.setattr(trial, "make_wave_basis", broken)
    monkeypatch.setattr(trial, "self_check", lambda sa_: None)
    c2 = gen.controls(sa, trial, bases)
    assert not c2["pass"] and not any(c2["eps0_basis_identical"].values())


def small_csv(tmp_path):
    rows = []
    for j in range(3):
        vals = [3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5) for i in range(48)]
        rows += month_rows(48, key=("AAA", f"staple_price:c{j}", "USD per kg", "https://github.com/tezamo/FPMA (x)", f"market={j}"), values=vals)
    return write_csv(tmp_path / "s.csv", rows)


def test_cli_writes_the_summary_report_and_units_and_is_byte_reproducible(tmp_path):
    csv_path = small_csv(tmp_path)
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    assert gen.main(["--csv", str(csv_path), "--outdir", str(out1), "--repo", str(ROOT)]) == 0
    assert gen.main(["--csv", str(csv_path), "--outdir", str(out2), "--repo", str(ROOT)]) == 0
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
    csv_path = small_csv(tmp_path)
    monkeypatch.setattr(gen, "controls", lambda *a, **k: {"eps0_basis_identical": {"24": False}, "pass": False})
    out = tmp_path / "o"
    assert gen.main(["--csv", str(csv_path), "--outdir", str(out), "--repo", str(ROOT)]) == 2
    assert not out.exists()


def test_cli_stops_when_two_runs_differ(tmp_path, monkeypatch):
    csv_path = small_csv(tmp_path)
    real, calls = gen.compute, []

    def flaky(*a, **k):
        r = real(*a, **k)
        calls.append(1)
        if len(calls) == 2:
            r["seed"] += 1
        return r
    monkeypatch.setattr(gen, "compute", flaky)
    out = tmp_path / "o"
    assert gen.main(["--csv", str(csv_path), "--outdir", str(out), "--repo", str(ROOT)]) == 2
    assert not out.exists()


def test_render_wording_never_says_confirmed_and_names_the_failed_criteria():
    res = {"control": {"eps0_basis_identical": {"24": True}, "pass": True}, "repeat_identical": True, "sets": {}, "tau": {},
           "synthetic_forms": {}, "criteria": [gen._v("C1", "N=24", "テスト", 1.0, 1.0, ">=", True)]}
    res["sets"] = {str(n): {"windows": 1, "constant_windows": 0, "series": 1, "by_source": {}, "stats": {
        "units": 1, "boundary": 1, "boundary_share": 1.0, "coefficient_range_eps6": None,
        "at_start": {gen.ekey(e): 0 for e in gen.EPS}}} for n in gen.LENGTHS}
    ok = gen.render(res)
    assert "矛盾する材料はなかった" in ok and "確かめられた」とは書かない" in ok and "満たさなかった" not in ok
    res["criteria"].append(gen._v("C3", "N=24", "テスト3", 0.5, 0.1, "<=", False))
    res["criteria"].append(gen._v("C2", "N=12", "判定できない", None, 0.1, "<=", None))
    bad = gen.render(res)
    assert "満たさなかったのは 1 件" in bad and "C3（N=24" in bad and "矛盾する材料はなかった" not in bad
    res["control"]["pass"] = False
    assert "ほかの結果は読まない" in gen.render(res)


def test_readme_states_the_same_thresholds_as_the_script():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    for needle in ("98% 以上", "2% 以下", "0.01% 以下", "0.5% 以下", "90% 以上", "5% 以下", "20 未満", "SEED = 20261026", "N = 12, 24, 48"):
        assert needle in text, needle
    assert gen.CRIT == {"c1_eps3": 0.98, "c2_eps3": 0.02, "c2_eps6": 1e-4, "c3_eps3": 0.02, "c3_eps6": 0.005, "c3_eps9": 0.005,
                        "c5_boundary": 0.9, "c5_amp": 0.05}
    assert (gen.SEED, gen.LENGTHS, gen.PRIMARY, gen.TAUS, gen.PRIMARY_TAU, gen.EPS, gen.SCALE, gen.MIN_UNITS) == (
        20261026, (12, 24, 48), 24, (0.25, 0.5, 1.0), 0.5, (1e-3, 1e-6, 1e-9), 5.0, 20)
    assert (gen.N_SYNTH, gen.SYNTH_POINTS, gen.SYNTH_NOISE) == (200, 24, 0.02)
    for s in gen.SYNTH:
        assert f"`{s['id']}`" in text
    assert re.search(r"tests/test_epsilon_generality\.py", text)


# ---- 変異で見逃した部分の追加 -------------------------------------------------------------------------------------------
def _three_windows():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": [3.0 + 2.0 * math.cos(2 * math.pi * x + p) for x in xs]} for p in (0.1, 0.7, 1.9)]
    return gen.make_bases(sa, trial, xs), wins


def test_tau_summary_notices_when_the_selected_forms_depend_on_tau(monkeypatch):
    bases, wins = _three_windows()
    real = gen.fit_row

    def fake(sa_, b, ys, tau):
        r = real(sa_, b, ys, tau)
        return dict(r, decay=r["decay"] + 1.0) if tau == 1.0 else r
    monkeypatch.setattr(gen, "fit_row", fake)
    t = gen.tau_summary(sa, bases, wins)
    assert [t[k]["forms_same_as_first_tau"] for k in ("0.25", "0.5", "1")] == [True, True, False]


def test_tau_summary_counts_units_already_inside_the_tolerance(monkeypatch):
    bases, wins = _three_windows()
    monkeypatch.setattr(gen, "TAUS", (0.5, 1000.0))
    t = gen.tau_summary(sa, bases, wins)
    assert t["0.5"]["at_start"] == 0 and t["1000"]["at_start"] == 3 and t["1000"]["coefficient_min"] is None


def test_c5_amplitude_threshold_is_inclusive(monkeypatch):
    c = math.log(2.5 * 1.037 / 0.5)
    dev = abs(gen.PRIMARY_TAU * math.exp(c) / 2.5 - 1.0)
    rows = {"undamped_p1": [synth_row(True, coef=c) for _ in range(5)]}
    monkeypatch.setitem(gen.CRIT, "c5_amp", dev)
    assert gen.judge_synth(rows)[1]["ok"] is True
    monkeypatch.setitem(gen.CRIT, "c5_amp", dev * (1 - 1e-9))
    assert gen.judge_synth(rows)[1]["ok"] is False


def test_c3_for_damped_series_is_judged_from_exactly_20_series():
    assert gen.judge_synth({"damped_l3": [synth_row(False) for _ in range(20)]})[2]["ok"] is True
    assert gen.judge_synth({"damped_l3": [synth_row(False) for _ in range(19)]})[2]["ok"] is None


def test_render_says_not_to_read_the_rest_when_only_the_repeat_check_fails():
    bases = {"eps0_basis_identical": {"24": True}, "pass": True}
    res = {"control": bases, "repeat_identical": False, "sets": {str(n): {"windows": 1, "constant_windows": 0, "series": 1, "by_source": {}, "stats": {
        "units": 1, "boundary": 1, "boundary_share": 1.0, "coefficient_range_eps6": None,
        "at_start": {gen.ekey(e): 0 for e in gen.EPS}}} for n in gen.LENGTHS}, "tau": {}, "synthetic_forms": {}, "criteria": []}
    assert "ほかの結果は読まない" in gen.render(res)


def test_synthetic_noise_has_the_registered_size():
    sp = {s["id"]: s for s in gen.SYNTH}["undamped_p1"]
    diffs = [a - b for i in range(40) for a, b in zip(gen.synth_series(sp, i), gen.synth_series(sp, i, noise=0.0))]
    rms = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    assert 0.015 < rms < 0.025
    noise_spec = {s["id"]: s for s in gen.SYNTH}["noise"]
    vals = gen.synth_series(noise_spec, 0)
    assert max(vals) - min(vals) > 1.0
