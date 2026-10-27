"""cycles/c001-chunichi/exploratory/wave_tie_noise.py の確認。

合成の線と合成の試合（SYNTHETIC: 2 球団のリーグ）を使う。実データではなく、float64 の再実装が今の wave_fit と一致すること、longdouble で選ぶ版が
丸めの影響を外した読みになっていること、数え方・表・終了コードが約束どおりに動くことを確かめるだけで、結論には使わない。
"""
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import polars as pl
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sakanalytics"))
import sakanalytics as sa  # noqa: E402

EXPL = ROOT / "cycles" / "c001-chunichi" / "exploratory"
sys.path.insert(0, str(EXPL))


def load(name):
    spec = importlib.util.spec_from_file_location(name, EXPL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wt = load("wave_eps_trial")
tn = load("wave_tie_noise")

XS149 = [i / 148 for i in range(149)]
TEAMS = {"d": {"name": "中日", "league": "C"}, "g": {"name": "巨人", "league": "C"}}
TOML = """[trajectory]
sims = 3
min_games = 5
end = "season"

[teams.d]
name = "中日"
league = "C"

[teams.g]
name = "巨人"
league = "C"
"""


def games_df():
    return pl.DataFrame([{"key": str(i), "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g",
                          "hs": 3 if i < 15 else 1, "as": 1 if i < 15 else 3} for i in range(30)])


@pytest.fixture(scope="module")
def tg():
    return sa.to_team_games(games_df(), TEAMS)


def wavy(xs, seed, noise=0.05, decay=1.0, period=0.5):
    rng = random.Random(seed)
    return [3.5 + 1.5 * math.exp(-decay * (x - xs[0])) * math.cos(2 * math.pi * (x - xs[0]) / period) + rng.gauss(0, noise) for x in xs]


# ---- 再実装と longdouble 版 ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("n", [20, 61, 149])
def test_float64_reimplementation_equals_wave_fit_exactly_on_varied_lines(n):
    xs = [0.07 + 0.93 * i / (n - 1) for i in range(n)]
    basis = sa.wave_basis(xs)
    lines = [wavy(xs, s) for s in range(4)] + [[6.0] * n, [1.0] * n, [3.5] * n, [2.0] * (n // 2) + [5.0] * (n - n // 2),
                                                [float(i) / 10 for i in range(n)]]
    for ys in lines:
        assert tn.fit_f64(sa, ys, basis, xs[0]) == sa.wave_fit(ys, basis, xs[0])


def test_longdouble_agrees_with_float64_on_well_separated_lines():
    xs = [0.07 + 0.93 * i / 99 for i in range(100)]
    basis = sa.wave_basis(xs)
    ld = tn.LdBasis(basis)
    for seed in range(6):
        ys = wavy(xs, seed, noise=0.02, decay=2.0, period=0.75)
        a, b = sa.wave_fit(ys, basis, xs[0]), tn.fit_ld(sa, ld, ys, xs[0])
        assert (a["decay"], a["period"]) == (b["decay"], b["period"]) == (2.0, 0.75)
        for k in ("end", "rmse", "limit"):
            assert a[k] == pytest.approx(b[k], rel=1e-9, abs=1e-12)


def test_a_flat_line_of_six_is_decided_by_rounding_in_float64_but_not_in_longdouble():
    basis = sa.wave_basis(XS149)
    t = tn.line_table(sa, {"ys": [6.0] * 149, "basis": basis, "x0": 0.0, "x1": 1.0})
    assert t["candidates"] == 55
    assert t["f64"]["sse_spread"] > sa.EPS_WAVE_TIE                          # 丸めのばらつきが許容より大きい
    assert t["ld"]["sse_spread"] < sa.EPS_WAVE_TIE / 100
    assert t["ld"]["choice"] == [0.5, None]                                  # 全部が同点なら、候補の並びで最初の式
    assert t["ld"]["within_tie_of_best"] == 55


def test_a_flat_line_of_one_is_below_the_tolerance_and_picks_the_first_form_in_float64_too():
    basis = sa.wave_basis(XS149)
    t = tn.line_table(sa, {"ys": [1.0] * 149, "basis": basis, "x0": 0.0, "x1": 1.0})
    assert t["f64"]["sse_spread"] < sa.EPS_WAVE_TIE and t["f64"]["choice"] == t["ld"]["choice"] == [0.5, None]


def test_the_first_form_wins_ties_and_a_clearly_better_form_still_wins():
    c = lambda sse, name: {"b": {"lam": name, "per": None}, "sse": sse, "lim": 0.0, "bb": 0.0}      # noqa: E731
    assert tn.select(sa, [c(1.0, "first"), c(1.0 - 0.5 * sa.EPS_WAVE_TIE, "second")])["b"]["lam"] == "first"
    assert tn.select(sa, [c(1.0, "first"), c(1.0 - 2 * sa.EPS_WAVE_TIE, "second")])["b"]["lam"] == "second"
    assert tn.select(sa, [c(1.0, "first"), c(1.0 - 2 * sa.EPS_WAVE_TIE, "second"), c(1.0 - 2.5 * sa.EPS_WAVE_TIE, "third")])["b"]["lam"] == "second"


# ---- 差し替えと数え方 ------------------------------------------------------------------------------------------------------
def test_patched_restores_wave_fit_even_when_the_body_fails():
    old = sa.wave_fit
    with pytest.raises(RuntimeError):
        with tn.patched(sa, "ld"):
            assert sa.wave_fit is not old
            raise RuntimeError("x")
    assert sa.wave_fit is old


def test_patched_returns_the_float64_result_in_f64_mode_and_the_longdouble_result_in_ld_mode():
    basis = sa.wave_basis(XS149)
    ys = [6.0] * 149
    want64, wantld = sa.wave_fit(ys, basis, 0.0), tn.fit_ld(sa, tn.LdBasis(basis), ys, 0.0)
    assert want64["decay"] != 0.5 or want64["period"] is not None            # この線では、float64 は先頭の式ではない（丸めで決まる）
    assert (wantld["decay"], wantld["period"]) == (0.5, None)
    for mode, want in (("f64", want64), ("ld", wantld)):
        with tn.patched(sa, mode):
            assert sa.wave_fit(ys, basis, 0.0) == want


def test_stats_count_flat_lines_and_differing_choices_and_reimplementation_mismatches():
    basis = sa.wave_basis(XS149)
    stats = tn.Stats()
    with tn.patched(sa, "f64", stats):
        sa.wave_fit([6.0] * 149, basis, 0.0)
        sa.wave_fit([1.0] * 149, basis, 0.0)
        sa.wave_fit(wavy(XS149, 3, noise=0.02, decay=2.0, period=0.75), basis, 0.0)
    s = stats.summary()
    assert s["calls"] == 3 and s["flat_lines"] == 2
    assert s["decision_differs"] == 1 and s["decision_differs_on_flat_lines"] == 1       # 値 6 の線だけ、float64 と longdouble で違う
    assert s["float64_reimplementation_mismatch"] == 0


def test_stats_add_counts_each_kind_of_difference_separately():
    same, other = {"decay": 0.5, "period": None}, {"decay": 0.5, "period": 0.75}
    s = tn.Stats()
    s.add([1.0, 2.0], same, other, same)                    # 動く線で、周期だけ違う（減衰は同じ）
    assert (s.calls, s.flat, s.differ, s.differ_flat, s.reimpl_mismatch) == (1, 0, 1, 0, 0)
    s.add([6.0, 6.0], same, other, same)                    # 一定の線で違う
    assert (s.calls, s.flat, s.differ, s.differ_flat, s.reimpl_mismatch) == (2, 1, 2, 1, 0)
    s.add([6.0, 6.0], same, same, other)                    # 選びは同じだが、float64 の再実装が今の関数と合わない
    assert (s.calls, s.flat, s.differ, s.differ_flat, s.reimpl_mismatch) == (3, 2, 2, 1, 1)


def test_within_tie_of_best_counts_a_candidate_exactly_at_the_tolerance_edge(monkeypatch):
    tol = 0.25                                              # 2 のべき乗なので、足し算が丸めずに端ちょうどになる
    cands = [{"b": {"lam": 0.5, "per": None}, "sse": s, "lim": 0, "bb": 0} for s in (1.0, 1.0 + tol, 1.0 + 2 * tol)]
    monkeypatch.setattr(sa, "EPS_WAVE_TIE", tol)
    monkeypatch.setattr(tn, "LdBasis", lambda basis: None)
    monkeypatch.setattr(tn, "cands_f64", lambda sa_, basis, ys: cands)
    monkeypatch.setattr(tn, "cands_ld", lambda sa_, ld, ys: cands)
    t = tn.line_table(sa, {"ys": [1.0, 2.0], "basis": [], "x0": 0.0, "x1": 1.0})
    assert t["candidates"] == 3 and t["ld"]["choice"] == [0.5, None] and t["ld"]["within_tie_of_best"] == 2


# ---- 球団の線を取り出して分析 --------------------------------------------------------------------------------------------
def test_capture_line_returns_the_real_line_the_basis_and_restores_the_module(tg):
    old = (sa._season_paths, sa.wave_fit, sa.wave_basis)
    cap = tn.capture_line(sa, tg, "g", sa.wave_basis, 5, "season")
    assert (sa._season_paths, sa.wave_fit, sa.wave_basis) == old
    assert len(cap["ys"]) >= 5 and cap["x1"] == 1.0 and 0.0 <= cap["x0"] < 1.0
    assert len(cap["basis"]) == len(sa.wave_basis([0.0, 0.5, 1.0]))
    other = tn.capture_line(sa, tg, "d", sa.wave_basis, 5, "season")      # 線は順位の高さ（2 球団なら 1 位が 2、2 位が 1）。最初は中日が勝っている
    assert cap["ys"][0] == 1.0 and other["ys"][0] == 2.0 and cap["ys"] != other["ys"]


def test_analyze_runs_on_the_synthetic_league_and_is_reproducible(tg):
    kw = dict(sims=3, min_games=5, end="season", eps_osc=(1e-3, 1e-6), sb_grid=(1e-3, 1e-9), sb=(2024, "g"))
    a, b = tn.analyze(sa, wt, tg, **kw), tn.analyze(sa, wt, tg, **kw)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["units"] == 2 and a["calls"]["calls"] > 0 and a["calls"]["float64_reimplementation_mismatch"] == 0
    assert list(a["osc_base"]) == ["0.001", "1e-06"] and set(a["osc_base"]["0.001"]) == {"f64", "ld"}
    sb = a["softbank"]
    assert sb["unit"] == "2024-g" and [r["eps"] for r in sb["rows"]] == [None, 1e-3, 1e-9] and sb["line"]["flat"] is False
    md = tn.render(a)
    assert "## ソフトバンク 2024（2024-g）" in md and "## wave_osc_base が対照と違う単位" in md and "| なし |" in md
    assert sa.wave_fit.__name__ == "wave_fit" and sa.wave_basis.__name__ == "wave_basis"          # 呼んだあとも元のまま


def test_capture_line_takes_the_basis_of_the_teams_own_league_when_leagues_play_different_numbers_of_days():
    teams = TEAMS | {"h": {"name": "ソフトバンク", "league": "P"}, "l": {"name": "ロッテ", "league": "P"}}
    rows = [{"key": f"c{i}", "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g", "hs": 3 if i < 15 else 1, "as": 1 if i < 15 else 3}
            for i in range(30)]
    rows += [{"key": f"p{i}", "date": f"2024-04-{i + 1:02d}", "home": "h", "away": "l", "hs": 3 if i < 8 else 1, "as": 1 if i < 8 else 3}
             for i in range(16)]
    tgx = sa.to_team_games(pl.DataFrame(rows), teams)
    caps = {t: tn.capture_line(sa, tgx, t, sa.wave_basis, 5, "season") for t in ("d", "h")}
    assert len(caps["d"]["ys"]) != len(caps["h"]["ys"])
    for cap in caps.values():
        assert all(len(b["ec"]) == len(cap["ys"]) for b in cap["basis"])           # 取り出した基準は、その球団の線の長さに合っている


def test_a_constant_line_in_the_league_is_reported_as_flat(tg):
    flat = pl.DataFrame([{"key": str(i), "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g", "hs": 3, "as": 1} for i in range(30)])
    cap = tn.capture_line(sa, sa.to_team_games(flat, TEAMS), "d", sa.wave_basis, 5, "season")
    assert len(set(cap["ys"])) == 1 and len(cap["ys"]) >= 5
    assert tn.line_table(sa, cap)["candidates"] > 0


def row(**kw):
    return {c: None for c in wt.WAVE_COLS} | kw


def test_changed_units_lists_only_the_units_whose_named_column_differs():
    ref = {(2024, "h"): row(wave_osc_base=0.5), (2024, "g"): row(wave_osc_base=0.5), (2013, "d"): row(wave_osc_base=0.1)}
    other = {(2024, "h"): row(wave_osc_base=0.5), (2024, "g"): row(wave_osc_base=0.505), (2013, "d"): row(wave_osc_base=0.1, wave_decay=1.0)}
    assert tn.changed_units(ref, other, wt, "wave_osc_base") == ["2024-g"] and tn.changed_units(ref, other, wt, "wave_decay") == ["2013-d"]
    assert tn.label((2024, "h")) == "2024-h"


def test_analyze_puts_each_count_under_the_right_mode_and_the_right_epsilon(tg, monkeypatch):
    base = {(2024, "h"): row(wave_osc_base=0.5), (2024, "g"): row(wave_osc_base=0.5), (2023, "d"): row(wave_osc_base=0.2)}

    def fake_basis(sa_, eps):
        return ("eps", eps)

    def fake_run(sa_, wt_, tg_, basis_fn, mode, sims, min_games, end, stats=None):
        if stats is not None:
            stats.add([6.0, 6.0], {"decay": 0.5, "period": None}, {"decay": 0.5, "period": None}, {"decay": 0.5, "period": None})
        out = {k: dict(v) for k, v in base.items()}
        if mode == "ld":
            out[(2023, "d")]["wave_decay"] = 3.0                              # longdouble だけ違う単位（2 列）。対照との差は ε ごとの表に混ぜない
            out[(2023, "d")]["wave_osc_base"] = 0.25
        if basis_fn == ("eps", 1e-6) and mode == "f64":
            out[(2024, "h")]["wave_osc_base"] = 0.505                         # ε = 1e-6 で float64 だけ動く単位
        if basis_fn == ("eps", 1e-3):
            out[(2024, "g")]["wave_osc_base"] = 0.51                          # ε = 1e-3 では両方動く
        return out

    monkeypatch.setattr(tn, "run", fake_run)
    monkeypatch.setattr(wt, "make_wave_basis", fake_basis)
    monkeypatch.setattr(tn, "capture_line", lambda *a, **k: {"ys": [6.0, 6.0], "basis": [], "x0": 0.0, "x1": 1.0})
    monkeypatch.setattr(tn, "line_table", lambda sa_, cap: {"candidates": 1, "f64": {"choice": [0.5, None], "sse_spread": 0.0},
                                                            "ld": {"choice": [0.5, None], "sse_spread": 0.0, "within_tie_of_best": 1}})
    res = tn.analyze(sa, wt, tg, sims=1, min_games=5, end="season", eps_osc=(1e-3, 1e-6), sb_grid=(1e-9,), sb=(2024, "g"))
    assert res["osc_base"]["1e-06"] == {"f64": {"units": 1, "labels": ["2024-h"]}, "ld": {"units": 0, "labels": []}}
    assert res["osc_base"]["0.001"] == {"f64": {"units": 1, "labels": ["2024-g"]}, "ld": {"units": 1, "labels": ["2024-g"]}}
    assert res["control_f64_vs_ld"] == {"units_differ": 1, "by_column": {"wave_decay": {"units": 1, "labels": ["2023-d"]},
                                                                          "wave_osc_base": {"units": 1, "labels": ["2023-d"]}}}
    assert res["units"] == 3 and res["calls"]["calls"] == 1 and res["softbank"]["line"]["flat"] is True
    assert [r["eps"] for r in res["softbank"]["rows"]] == [None, 1e-9]


# ---- コマンドライン ---------------------------------------------------------------------------------------------------------
def write_inputs(tmp_path, tg, tweak=False):
    games = tmp_path / "games.jsonl"
    games_df().write_ndjson(games)
    cfg = tmp_path / "analysis.toml"
    cfg.write_text(TOML, encoding="utf-8")
    ctrl = wt.trajectory(sa, tg, sa.wave_basis, 3, 5, "season")
    committed = tmp_path / "season.jsonl"
    rows = [dict(r) for r in ctrl.values()]
    if tweak:
        rows[0]["wave_decay"] = 99.0
    committed.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return games, cfg, committed


def test_main_writes_json_and_markdown_and_is_byte_reproducible(tmp_path, tg):
    games, cfg, committed = write_inputs(tmp_path, tg)
    outs = []
    for name in ("a", "b"):
        o = tmp_path / name
        assert tn.main(["--games", str(games), "--config", str(cfg), "--committed", str(committed), "--unit", "2024", "g",
                        "--outdir", str(o), "--repo", str(ROOT)]) == 0
        outs.append(o)
    for n in ("wave_tie_noise.json", "wave_tie_noise.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes()
    res = json.loads((outs[0] / "wave_tie_noise.json").read_text(encoding="utf-8"))
    assert res["gate"]["pass"] is True and res["softbank"]["unit"] == "2024-g" and res["sims"] == 3


def test_main_stops_when_the_control_does_not_match_the_committed_rows_or_the_unit_is_missing(tmp_path, tg):
    games, cfg, committed = write_inputs(tmp_path, tg, tweak=True)
    base = ["--games", str(games), "--config", str(cfg), "--unit", "2024", "g", "--repo", str(ROOT)]
    assert tn.main(base + ["--committed", str(committed), "--outdir", str(tmp_path / "bad")]) == 2
    assert not (tmp_path / "bad").exists()
    games, cfg, committed = write_inputs(tmp_path, tg)
    assert tn.main(["--games", str(games), "--config", str(cfg), "--committed", str(committed), "--unit", "2024", "zz",
                    "--repo", str(ROOT), "--outdir", str(tmp_path / "nounit")]) == 2
    assert not (tmp_path / "nounit").exists()


# ---- 予想を先に書いたこと -------------------------------------------------------------------------------------------------
def test_the_prediction_is_written_before_the_run_and_names_the_noise_floor_and_the_tolerance():
    doc = tn.__doc__
    assert "予想（走らせる前に書く。結果を見て変えない）" in doc
    for needle in ("(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "0.03・0.001・1e-12", "EPS_WAVE_TIE", "5.2e-12", "2.7e-15", "longdouble", "sakanalytics は変更しない"):
        assert needle in doc, needle
    assert tn.SB_GRID == (0.1, 0.03, 0.01, 0.003, 1e-3, 1e-4, 1e-6, 1e-9, 1e-12) and tn.EPS_OSC == (1e-3, 1e-6, 1e-9)


# ---- 置いた結果（実データの走らせた結果）が、JSON・予想・READMEと合っている -------------------------------------------------------
RESULTS = EXPL / "wave_tie_noise_results"


def results_json():
    return json.loads((RESULTS / "wave_tie_noise.json").read_text(encoding="utf-8"))


def sci(x):
    m, e = f"{x:.3g}".split("e")
    return f"{m}×10^{int(e)}"


def test_the_md_in_the_results_is_what_render_makes_from_the_json():
    assert (RESULTS / "wave_tie_noise.md").read_text(encoding="utf-8") == tn.render(results_json())


def test_the_results_gate_passed_and_the_float64_reimplementation_matched_every_call():
    j = results_json()
    assert j["gate"]["pass"] is True and j["gate"]["rows_differ"] == 0 and j["gate"]["units"] == j["units"] == 168
    assert j["calls"]["float64_reimplementation_mismatch"] == 0


def test_the_written_predictions_hold_in_the_results_json_as_the_readme_says():
    j, rows = results_json(), results_json()["softbank"]["rows"]
    assert j["softbank"]["line"]["flat"] is True and j["softbank"]["line"]["min"] == j["softbank"]["line"]["max"] == 6 and j["softbank"]["line"]["points"] == 149   # (a)
    assert all(r["f64"]["sse_spread"] > 1e-12 > r["ld"]["sse_spread"] for r in rows)                                                                                   # (b)
    assert all(r["ld"]["choice"] == [0.5, None] and r["ld"]["within_tie_of_best"] == r["candidates"] == 55 for r in rows)                                              # (b)
    control = rows[0]
    assert control["eps"] is None and [r["eps"] for r in rows if r["f64"]["choice"] != control["f64"]["choice"]] == [0.03, 0.001, 1e-12]                                # (c)
    assert all(v["ld"]["units"] == 0 for v in j["osc_base"].values())                                                                                                   # (d)
    c = j["calls"]
    assert c["decision_differs"] > 0 and c["decision_differs_on_flat_lines"] == c["decision_differs"] and c["flat_lines"] < c["calls"]                                 # (e)


def test_the_readme_numbers_are_the_json_numbers():
    j, md = results_json(), (RESULTS / "README.md").read_text(encoding="utf-8")
    c, rows = j["calls"], j["softbank"]["rows"]
    for want in (f"{c['calls']:,}", f"{c['flat_lines']:,}", f"{c['decision_differs']}", f"{c['flat_lines'] / c['calls']:.1%}",
                 f"{c['decision_differs_on_flat_lines'] / c['flat_lines']:.1%}", f"{c['calls'] - c['flat_lines']:,}",
                 f"{j['units']} 球団年", f"{j['control_f64_vs_ld']['by_column']['wave_osc_base']['units']} 単位",
                 sci(min(r["f64"]["sse_spread"] for r in rows)), sci(max(r["f64"]["sse_spread"] for r in rows)),
                 sci(min(r["ld"]["sse_spread"] for r in rows)), sci(max(r["ld"]["sse_spread"] for r in rows))):
        assert want in md, want
    osc = j["osc_base"]
    assert f"{osc['0.001']['f64']['units']}（1e-3）/ {osc['1e-06']['f64']['units']}（1e-6）/ {osc['1e-09']['f64']['units']}（1e-9）" in md
    cols = j["control_f64_vs_ld"]["by_column"]
    assert cols["wave_osc"]["labels"] == cols["wave_period"]["labels"] == ["2018-l", "2024-h"] and cols["wave_rmse"]["labels"] == ["2018-l"]
    assert "2018-l、2024-h" in md and "`wave_rmse` 1 単位（2018-l）" in md
