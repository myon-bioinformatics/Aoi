"""research/epsilon-generality/posthoc_window_crossing.py の確認。

SYNTHETIC: 組み立てた関数・小さな合成の系列で、二分・60 点の並び・許容の差し替えと戻し・窓の取り出し・誤差の2乗和・書き出しが
約束どおりに動くことを確かめる。実データの結果（予想に当たったか）はここでは確かめない（結論には使わない）。
窓の指定（梯子の 2 点）が、コミット済みの梯子の結果と合っていることだけは確かめる。
"""
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
STAPLE = ROOT / "research" / "staple-price-survey" / "staple_survey_vertical.csv"


def load(name):
    spec = importlib.util.spec_from_file_location(name, DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wc = load("posthoc_window_crossing")
gen = wc.gen
sa, trial = gen.load_modules(ROOT)
COLS = ["country", "variable", "unit", "source", "note", "date", "value"]


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
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
    old = sa.EPS_WAVE_TIE
    with wc.tie_tolerance(sa, 5.0):
        assert sa.EPS_WAVE_TIE == 5.0
    assert sa.EPS_WAVE_TIE == old
    with pytest.raises(RuntimeError):
        with wc.tie_tolerance(sa, 5.0):
            raise RuntimeError("x")
    assert sa.EPS_WAVE_TIE == old


def test_form_at_uses_the_given_tolerance_and_the_current_one_by_default():
    ys = gen.normalize(WAVY)[1]
    now = wc.form_at(sa, trial, ys, 1e-3)
    assert wc.form_at(sa, trial, ys, 1e-3, sa.EPS_WAVE_TIE) == now
    huge = wc.form_at(sa, trial, ys, 1e-3, 1e6)                        # 許容が大きいと、先頭の式（波なし）から動かない
    assert huge[1] is None and huge[0] != "ε"
    assert sa.EPS_WAVE_TIE == 1e-12                                    # 差し替えたあと元に戻っている


def test_form_at_labels_a_wave_that_kept_the_epsilon_decay_and_sse_of_scores_it_at_zero():
    eps, per, n = 1e-3, 0.5, 12
    w, lim, bb = 2 * math.pi / per, 3.0, 2.0                          # 始まりが 0 で、減衰が ε の波そのもの（ノイズなし）
    ys = [lim + math.exp(-eps * i / (n - 1)) * ((0.0 - lim) * math.cos(w * i / (n - 1)) + bb * math.sin(w * i / (n - 1))) for i in range(n)]
    f = wc.form_at(sa, trial, ys, eps)
    assert f == ("ε", per) and wc.sse_of(sa, trial, ys, eps, f) < 1e-18


def test_sse_of_equals_the_fitted_rmse_for_the_form_that_wave_fit_chose():
    ys = gen.normalize(WAVY)[1]
    n, eps = len(ys), 1e-3
    basis = trial.make_wave_basis(sa, eps)([i / (n - 1) for i in range(n)])
    with gen.settle_tolerance(sa, gen.PRIMARY_TAU):
        f = sa.wave_fit(ys, basis, 0.0, 1.0)
    form = wc.form_at(sa, trial, ys, eps)
    assert math.isclose(wc.sse_of(sa, trial, ys, eps, form), n * f["rmse"] ** 2, rel_tol=1e-9)


# ---- 窓の取り出し ----------------------------------------------------------------------------------------------------
def test_window_values_picks_the_named_window_and_normalizes_it(tmp_path):
    rows = series_rows("AAA", "staple_price:x", 0, WAVY) + series_rows("BBB", "staple_price:x", 0, [v * 2 for v in WAVY])
    write_rows(tmp_path / "a.csv", rows)
    series = gen.read_series(tmp_path / "a.csv")
    spec = {"id": "t", "n": 12, "country": "BBB", "variable": "staple_price:x", "start": "2020-01"}
    ys = wc.window_values(series, spec, gen.month_text)
    assert ys == gen.normalize([v * 2 for v in WAVY])[1] and max(ys) - min(ys) == pytest.approx(gen.SCALE)


@pytest.mark.parametrize("country,start", [("CCC", "2020-01"), ("AAA", "2021-01")])
def test_window_values_stops_when_the_window_is_missing(tmp_path, country, start):
    write_rows(tmp_path / "a.csv", series_rows("AAA", "staple_price:x", 0, WAVY))
    spec = {"id": "t", "n": 12, "country": country, "variable": "staple_price:x", "start": start}
    with pytest.raises(ValueError, match="0 個"):
        wc.window_values(gen.read_series(tmp_path / "a.csv"), spec, gen.month_text)


def test_window_values_stops_when_the_window_is_constant(tmp_path):
    write_rows(tmp_path / "a.csv", series_rows("AAA", "staple_price:x", 0, [3.0] * 12))
    spec = {"id": "t", "n": 12, "country": "AAA", "variable": "staple_price:x", "start": "2020-01"}
    with pytest.raises(ValueError, match="一定"):
        wc.window_values(gen.read_series(tmp_path / "a.csv"), spec, gen.month_text)


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
    w = wc.analyse_window(sa, trial, [0.0, 1.0] * 6, SPEC)
    t = w["by_tolerance"]
    assert t["1e-12"]["eps_star"] == pytest.approx(6e-3, rel=1e-3) and t["1e-15"]["eps_star"] == pytest.approx(5.9e-3, rel=1e-3)
    assert w["rel_shift_of_eps_star"] == pytest.approx(0.02, abs=2e-3)         # 6.12/6 − 1。1e-15 側は −1.7%、基準を取り違えると 3.6% になる
    assert w["changes_along_grid"] == 1 and w["form_lo"] == ["ε", 1.0] and w["form_hi"] == ["ε", 0.75]


def test_the_edge_check_uses_only_the_two_points_next_to_the_switch(monkeypatch):
    monkeypatch.setattr(wc, "form_at", fake_form_at)
    monkeypatch.setattr(wc, "sse_of", fake_sse_of)
    w = wc.analyse_window(sa, trial, [0.0, 1.0] * 6, SPEC)
    assert w["gaps"][0]["eps"] < 6e-3 <= w["gaps"][1]["eps"]
    assert w["edge_rel_diff"] == pytest.approx(0.003 / 0.997, rel=1e-6) and w["edge_rel_diff"] < 1e-2
    assert max(abs(g["diff"]) for g in w["gaps"][2:]) == pytest.approx(0.5)     # 登録した ε の3点は大きく離れている（端の確認には入れない）


def test_main_stops_without_writing_when_two_runs_on_the_same_input_differ(tmp_path, monkeypatch):
    results = iter([{"windows": [], "skipped": ["a"]}, {"windows": [], "skipped": ["b"]}])
    monkeypatch.setattr(wc, "analyse", lambda *a, **k: next(results))
    out = tmp_path / "o"
    assert wc.main(["--staple-csv", str(STAPLE), "--outdir", str(out), "--repo", str(ROOT)]) == 2
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
    prof = gen.PROFILES["staple"]
    return {"staple": (gen.read_series(STAPLE, prof["prefix"], prof["cadence"]), gen.CADENCE["month"]["text"])}


@pytest.fixture(scope="module")
def staple_result(staple_inputs):
    return wc.analyse(sa, trial, staple_inputs)


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
    md = wc.render(staple_result)
    for w in staple_result["windows"]:
        assert f"## {w['id']}" in md and f"| {w['id']}（{w['n']} 点、{w['start']} から）" in md
    assert "入力が無くて飛ばした窓: Mauna Loa CO2" in md and md.count("## ") == len(staple_result["windows"])


def test_main_writes_json_and_md_reproducibly_and_needs_an_input(tmp_path, capsys):
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    for out in (out1, out2):
        assert wc.main(["--staple-csv", str(STAPLE), "--outdir", str(out), "--repo", str(ROOT)]) == 0
    for name in ("posthoc_window_crossing.json", "posthoc_window_crossing.md"):
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()
    with pytest.raises(SystemExit) as e:
        wc.main(["--outdir", str(tmp_path / "o3")])
    assert e.value.code == 2


def test_the_prediction_is_written_before_the_run_and_names_what_is_not_claimed():
    doc = wc.__doc__
    for tag in ("(a)", "(b)", "(c)", "(d)", "(e)"):
        assert tag in doc
    assert "走らせる前に書く" in doc and "ε の値をどうするかは決めない" in doc and "この 3 窓" in doc
