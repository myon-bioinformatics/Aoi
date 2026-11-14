"""c001 探索の wave_* の検査（旧 5 本をまとめた。節の頭に旧ファイルの名前を書いた）。
"""

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sakanalytics"))

import polars as pl  # noqa: E402
import pytest  # noqa: E402
import sakanalytics as sa  # noqa: E402


# ==== trial（旧 test_c001_wave_eps_trial.py）
# cycles/c001-chunichi/exploratory/wave_eps.py の trial（旧 wave_eps_trial.py）の確認。減衰 0 を ε に差し替える変換が、元の当てはめと整合するか。
#
# 合成の線（SYNTHETIC）を使う。実データではなく、変換の性質（ε = 0 で元と同一、ε → 0 で連続、落ち着く位置が 1/ε に比例）を確かめるだけで、結論には使わない。


trial_spec = importlib.util.spec_from_file_location("wave_eps_trial", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps.py")
trial = importlib.util.module_from_spec(trial_spec)
trial_spec.loader.exec_module(trial)

XS = [0.1 + 0.9 * i / 60 for i in range(61)]
# 減衰しない波 + ゆるい傾き（周期 2.0 の波が選ばれるはずの線）
YS = [3.5 + 1.2 * math.cos(math.pi * (x - XS[0])) + 0.6 * math.sin(math.pi * (x - XS[0])) for x in XS]


def test_swap_is_identity_at_eps_zero():
    trial.self_check(sa)


def test_original_has_no_limit_for_undamped_wave():
    f = sa.wave_fit(YS, sa.wave_basis(XS), XS[0])
    assert f["decay"] == 0.0 and f["limit"] is None and f["settle_x"] is None


def test_eps_restores_finite_limit_and_settle():
    f = sa.wave_fit(YS, trial.make_wave_basis(sa, 1e-6)(XS), XS[0])
    assert f["decay"] == 1e-6 and f["limit"] is not None and f["settle_x"] > 1


def test_limit_is_continuous_as_eps_goes_to_zero():
    lim = [sa.wave_fit(YS, trial.make_wave_basis(sa, e)(XS), XS[0])["limit"] for e in (1e-3, 1e-6, 1e-9)]
    assert abs(lim[1] - lim[2]) < 1e-5 and abs(lim[0] - lim[2]) < 1e-2


def test_settle_position_scales_with_inverse_eps():
    s = [sa.wave_fit(YS, trial.make_wave_basis(sa, e)(XS), XS[0]) for e in (1e-6, 1e-9)]
    a, b = ((f["settle_x"] - XS[0]) * e for f, e in zip(s, (1e-6, 1e-9)))
    assert abs(a - b) / b < 1e-3


def _row(**kw):
    return {"wave_limit_rank": 3.0, "wave_decay": 0.5, "wave_period": 1.0, "wave_settle_x": 0.4, **kw}


def test_gate_without_new_seasons_is_strict_as_before():
    ctrl = {(2023, "d"): _row(), (2024, "d"): _row()}
    assert trial.trial_cli_gate(ctrl, dict(ctrl), 5)["pass"] is True
    assert "new_seasons" not in trial.trial_cli_gate(ctrl, dict(ctrl), 5)
    g = trial.trial_cli_gate(ctrl, {(2023, "d"): _row()}, 5)                          # 確定済みに行がない単位 → 通さない
    assert g["pass"] is False and g["not_in_committed"] == 1
    g = trial.trial_cli_gate(ctrl, {(2023, "d"): _row(), (2024, "d"): _row(wave_decay=0.25)}, 5)   # 値が違う → 通さない
    assert g["pass"] is False and g["rows_differ"] == 1


def test_gate_leaves_a_new_season_out_of_the_comparison_and_counts_it():
    ctrl = {(2025, "d"): _row(), (2026, "d"): _row(), (2026, "g"): _row(wave_decay=0.0, wave_limit_rank=None)}
    g = trial.trial_cli_gate(ctrl, {(2025, "d"): _row()}, 200, new_seasons=[2026])
    assert g["pass"] is True and g["units"] == 3 and g["new_units"] == 2 and g["new_seasons"] == [2026]
    assert g["not_in_committed"] == 0 and g["rows_differ"] == 0
    # 新しい年を指定しても、それ以外の年の食い違いは今までどおり止める
    assert trial.trial_cli_gate(ctrl, {(2025, "d"): _row(wave_period=2.0)}, 200, new_seasons=[2026])["rows_differ"] == 1
    assert trial.trial_cli_gate(ctrl, {(2025, "d"): _row(wave_period=2.0)}, 200, new_seasons=[2026])["pass"] is False
    assert trial.trial_cli_gate(ctrl, {}, 200, new_seasons=[2026])["not_in_committed"] == 1
    assert trial.trial_cli_gate(ctrl, {}, 200, new_seasons=[2026])["pass"] is False


def test_gate_refuses_a_new_season_that_already_has_committed_rows_or_has_no_units():
    ctrl = {(2025, "d"): _row(), (2026, "d"): _row()}
    both = {(2025, "d"): _row(), (2026, "d"): _row()}
    g = trial.trial_cli_gate(ctrl, both, 200, new_seasons=[2026])                     # 確定済みがあるのに「新しい年」と呼ばせない
    assert g["pass"] is False and g["new_seasons_with_committed_rows"] == 1
    g = trial.trial_cli_gate(ctrl, {(2025, "d"): _row()}, 200, new_seasons=[2027])    # 年の指定まちがいで対照が静かに外れない
    assert g["pass"] is False and g["new_seasons_without_units"] == [2027]


# ==== sensitivity（旧 test_c001_wave_eps_sensitivity.py）
# cycles/c001-chunichi/exploratory/wave_eps.py の sensitivity（旧 wave_eps_sensitivity.py）の確認。
#
# 合成の試合（SYNTHETIC: 2 球団のリーグで、g が前半に負け続け後半に勝ち続ける線）を使う。実データではなく、読みの計算（境界の数え方、
# ε を振ったときの動き、線を動かしたときの入れ替わり、関門）が約束どおりに動くかを確かめるだけで、結論には使わない。


sensitivity_spec = importlib.util.spec_from_file_location("wave_eps_sensitivity", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps.py")
sens = importlib.util.module_from_spec(sensitivity_spec)
sys.modules["wave_eps_sensitivity"] = sens
sensitivity_spec.loader.exec_module(sens)

TEAMS = {"d": {"name": "中日", "league": "C"}, "g": {"name": "巨人", "league": "C"}}


def sensitivity_games_df() -> pl.DataFrame:
    rows = [{"key": str(i), "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g",
             "hs": 3 if i < 15 else 1, "as": 1 if i < 15 else 3} for i in range(30)]
    return pl.DataFrame(rows)


@pytest.fixture(scope="module")
def sensitivity_tg():
    return sa.to_team_games(sensitivity_games_df(), TEAMS)


@pytest.fixture(scope="module")
def report(sensitivity_tg):
    return sens.analyze(sa, sensitivity_tg, sims=5, grid=(1e-3, 1e-6, 1e-9), min_games=(5, 10), ends=("season", "decided"), variant_eps=1e-6)


def test_the_synthetic_wave_puts_exactly_g_on_the_boundary_and_a_tiny_eps_lifts_exactly_that_unit(report):
    row = report["grid"][-1]
    assert row["eps"] == 1e-9 and row["boundary_without_eps"] == 1
    assert (row["lifted"], row["still_boundary"], row["switched_in"], row["left"], row["other_changed"]) == (1, 1, [], [], 0)


def test_the_last_value_moves_by_about_eps_in_the_synthetic_season(report):
    by = {r["eps"]: r for r in report["grid"]}
    assert 0 < by[1e-6]["end_shift_over_eps"] < 10 and 0 < by[1e-9]["end_shift_over_eps"] < 10
    # the synthetic wave is small (two teams: ranks 1 and 2), so it is within half a rank from the start: nothing is settled late
    assert (by[1e-9]["settle_over_1"], by[1e-9]["settle_within_season"], by[1e-9]["settle_times_eps_median"]) == (0, 1, None)


def _wave_row(decay, settle_x=None, limit=None, end=2.0, start=0.1, period=2.0):
    return {"wave_decay": decay, "wave_period": period, "wave_end_rank": end, "wave_limit_rank": limit, "wave_settle_x": settle_x,
            "wave_limit_rank_h1": None, "traj_start_x": start, "wave_osc": True, "wave_rmse": 0.3, "wave_settle_pct": 0.5, "wave_osc_base": 0.5}


def test_grid_report_arithmetic_on_a_hand_made_fit():
    """境界の単位 (1, "a") は ε で 1/ε に比例して落ち着き、最後の値が ε だけずれる。(1, "b") は境界でない。"""
    amp_log = 0.7  # ln(振れ幅 / 0.5)

    def run(min_games, end, eps=None):
        if eps is None:
            return {(1, "a"): _wave_row(0.0), (1, "b"): _wave_row(3.0, limit=2.0)}
        return {(1, "a"): _wave_row(eps, settle_x=0.1 + amp_log / eps, limit=3.5 + eps, end=2.0 + 0.8 * eps),
                (1, "b"): _wave_row(3.0, limit=2.0)}

    rows = {r["eps"]: r for r in sens.grid_report(run, 10, "season", (1e-3, 1e-6))}
    for eps in (1e-3, 1e-6):
        r = rows[eps]
        assert (r["boundary_without_eps"], r["lifted"], r["still_boundary"], r["switched_in"], r["left"], r["other_changed"]) == (1, 1, 1, [], [], 0)
        assert r["settle_over_1"] == 1 and r["settle_within_season"] == 0
        assert r["settle_times_eps_median"] == pytest.approx(amp_log)
        assert r["end_shift_over_eps"] == pytest.approx(0.8)
    assert rows[1e-6]["limit_shift_vs_smallest_eps"] == 0
    assert rows[1e-3]["limit_shift_vs_smallest_eps"] == pytest.approx(1e-3 - 1e-6)


def test_grid_report_names_a_unit_that_switches_in_or_leaves():
    def run(min_games, end, eps=None):
        if eps is None:
            return {(1, "a"): _wave_row(0.0), (1, "b"): _wave_row(0.5, limit=2.0)}
        return {(1, "a"): _wave_row(0.5, limit=2.0), (1, "b"): _wave_row(eps, settle_x=50.0, limit=2.0)}  # a leaves, b switches in

    r = sens.grid_report(run, 10, "season", (1e-3,))[0]
    assert (r["boundary_without_eps"], r["lifted"], r["still_boundary"]) == (1, 1, 0)
    assert r["switched_in"] == ["1-b"] and r["left"] == ["1-a"]


def test_the_limit_shift_against_the_smallest_eps_vanishes_for_that_eps_and_shrinks_with_eps(report):
    by = {r["eps"]: r for r in report["grid"]}
    assert by[1e-9]["limit_shift_vs_smallest_eps"] == 0
    assert by[1e-3]["limit_shift_vs_smallest_eps"] >= by[1e-6]["limit_shift_vs_smallest_eps"] >= 0


def test_the_base_line_compared_with_itself_keeps_every_boundary_unit(report):
    base = next(r for r in report["variants"]["variants"] if (r["min_games"], r["end"]) == (10, "season"))
    assert (base["kept_from_base"], base["added"], base["dropped"], base["jaccard"]) == (1, 0, 0, 1.0)
    assert base["limit_shift_max"] == 0 and base["same_period"] == base["compared"] == 1 and base["lifted_equals_boundary"]


def test_every_variant_row_is_consistent_and_the_histogram_counts_the_base_boundary_units(report):
    v = report["variants"]
    assert len(v["variants"]) == 4 and report["units"] == 2
    for r in v["variants"]:
        assert r["kept_from_base"] + r["dropped"] == r["base_boundary_in_common_units"]
        assert r["kept_from_base"] + r["added"] == r["boundary_in_common_units"]
        assert r["lifted"] >= r["boundary"] or not r["lifted_equals_boundary"]
    assert sum(v["membership_histogram"].values()) == len(v["membership"]) == 1
    m = v["membership"][0]
    assert m["unit"] == "2024-g" and 1 <= m["on_boundary_in"] <= m["present_in"] <= 4


def test_render_names_the_three_readings_and_marks_eps_as_provisional(report):
    text = sens.sensitivity_cli_render(report)
    for part in ("## 1. ε を振る", "## 2. 線の始まり・終わりを動かす（ε = 1e-06）", "## 3. 基準の境界の単位は", "結論には使わない"):
        assert part in text
    assert text.count("\n| 1e-") >= 2


def _files(tmp_path):
    sensitivity_games_df().write_ndjson(tmp_path / "games.jsonl")
    cfg = ["[trajectory]", "min_games = 10", "sims = 5", "", "[teams]"] + [f'{t} = {{ name = "{v["name"]}", league = "{v["league"]}" }}' for t, v in TEAMS.items()]
    (tmp_path / "analysis.toml").write_text("\n".join(cfg) + "\n", encoding="utf-8")
    plain = sa.season_trajectory(sa.to_team_games(sensitivity_games_df(), TEAMS), sims=5, min_games=10, end="season")
    rows = [{"season": r["season"], "team": r["team"], **{c: r[c] for c in sens.WAVE_COLS}} for r in plain.to_dicts()]
    committed = tmp_path / "season.jsonl"
    committed.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return rows, committed


def _argv(tmp_path, committed):
    return ["--games", str(tmp_path / "games.jsonl"), "--config", str(tmp_path / "analysis.toml"), "--committed", str(committed),
            "--outdir", str(tmp_path / "out"), "--repo", str(ROOT), "--grid", "1e-3", "1e-6", "--min-games", "5", "10", "--ends", "season"]


def test_cli_writes_the_reports_when_the_control_matches(tmp_path):
    _, committed = _files(tmp_path)
    assert sens.sensitivity_cli(_argv(tmp_path, committed)) == 0
    out = tmp_path / "out"
    assert json.loads((out / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8"))["pass"] is True
    data = json.loads((out / "wave_eps_sensitivity.json").read_text(encoding="utf-8"))
    assert [r["eps"] for r in data["grid"]] == [1e-3, 1e-6] and data["units"] == 2
    assert (out / "wave_eps_sensitivity.md").read_text(encoding="utf-8").startswith("# 波の減衰 0 → ε")
    assert [json.loads(line)["unit"] for line in (out / "wave_eps_boundary_membership.jsonl").read_text(encoding="utf-8").splitlines()] == ["2024-g"]


def test_cli_stops_without_running_the_analysis_when_the_control_differs(tmp_path):
    rows, committed = _files(tmp_path)
    rows[0]["wave_rmse"] = (rows[0]["wave_rmse"] or 0.0) + 1.0
    committed.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    assert sens.sensitivity_cli(_argv(tmp_path, committed)) == 2
    out = tmp_path / "out"
    assert json.loads((out / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8"))["pass"] is False
    assert not (out / "wave_eps_sensitivity.json").exists()


def test_variant_report_counts_kept_added_and_dropped_units_against_the_base_line():
    """基準の線で境界は a・b。動かした線では b・c。a は外れ、c が加わり、b だけ残る（収束先は 0.25 動く）。"""
    def fit(boundary, eps, limit):
        return _wave_row(eps if boundary and eps else (0.0 if boundary else 3.0), limit=limit, settle_x=50.0 if boundary and eps else None)

    def run(min_games, end, eps=None):
        on = {"a", "b"} if (min_games, end) == (10, "season") else {"b", "c"}
        shift = 0.0 if (min_games, end) == (10, "season") else 0.25
        return {(1, t): fit(t in on, eps, 2.0 + (shift if t == "b" else 0.0)) for t in ("a", "b", "c")}

    v = sens.variant_report(run, [(10, "season"), (5, "season")], 1e-6, (10, "season"))
    base, moved = v["variants"]
    assert (base["kept_from_base"], base["added"], base["dropped"], base["jaccard"]) == (2, 0, 0, 1.0)
    assert (moved["kept_from_base"], moved["added"], moved["dropped"]) == (1, 1, 1)
    assert moved["jaccard"] == pytest.approx(1 / 3)
    assert (moved["limit_shift_median"], moved["limit_shift_max"], moved["same_period"], moved["compared"]) == (0.25, 0.25, 1, 1)
    # a is on the boundary of the base line only: 1 of 2 lines; b of both; membership counts the base boundary units
    members = {m["unit"]: (m["on_boundary_in"], m["present_in"]) for m in v["membership"]}
    assert members == {"1-a": (1, 2), "1-b": (2, 2)} and v["membership_histogram"] == {"1/2": 1, "2/2": 1}


def test_cli_accepts_a_new_season_without_committed_rows_and_records_it(tmp_path):
    _files(tmp_path)
    empty = tmp_path / "empty_season.jsonl"
    empty.write_text("", encoding="utf-8")
    assert sens.sensitivity_cli(_argv(tmp_path, empty) + ["--new-seasons", "2024"]) == 0
    g = json.loads((tmp_path / "out" / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8"))
    assert g["pass"] is True and g["new_seasons"] == [2024] and g["new_units"] == 2 and g["units"] == 2


def test_cli_still_stops_when_the_named_new_season_has_committed_rows_or_the_season_is_not_in_the_games(tmp_path):
    _, committed = _files(tmp_path)
    assert sens.sensitivity_cli(_argv(tmp_path, committed) + ["--new-seasons", "2024"]) == 2
    g = json.loads((tmp_path / "out" / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8"))
    assert g["pass"] is False and g["new_seasons_with_committed_rows"] == 2
    assert not (tmp_path / "out" / "wave_eps_sensitivity.json").exists()
    assert sens.sensitivity_cli(_argv(tmp_path, committed) + ["--new-seasons", "2027"]) == 2


# ==== settle（旧 test_c001_wave_eps_settle_coefficients.py）
# cycles/c001-chunichi/exploratory/wave_eps.py の settle_coefficients（旧 wave_eps_settle_coefficients.py）の確認。
#
# SYNTHETIC: 落ち着く位置が（係数 / ε）に小さな定数を足した形になるように作った行（実データではない）で、
# ε = a × 10^-n の書き方、「係数 × 10^n」の係数が ε を替えても動かないこと（a を替えれば 1/a 倍になること）、
# ε によらず一定の単位を分けること、最小の ε の係数で言い当てたときの外れ（絶対・相対）を出すことを確かめる。結論には使わない。


settle_spec = importlib.util.spec_from_file_location("wave_eps_settle_coefficients", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps.py")
coef = importlib.util.module_from_spec(settle_spec)
sys.modules["wave_eps_settle_coefficients"] = coef
settle_spec.loader.exec_module(coef)

EPS = (1e-3, 1e-6, 1e-9)
INVALID_EPS = (float("nan"), float("inf"), float("-inf"), 0.0, -1e-6)


def settle_row(eps, settle, *, committed_decay=0.0, decay=None):
    return {"season": 2024, "team": "x", "eps_provisional": eps, "committed_wave_decay": committed_decay,
            "eps_wave_decay": eps if decay is None else decay, "eps_wave_settle_x": settle}


def table(units, eps_list=EPS):
    """units: {(season, team): (係数 k, 上乗せ c) または 定数の位置}。位置は c + k / ε。"""
    out = {}
    for e in eps_list:
        out[e] = {}
        for key, v in units.items():
            s = v if isinstance(v, float) else v[1] + v[0] / e
            r = settle_row(e, s)
            r["season"], r["team"] = key
            out[e][key] = r
    return out


def write_rows(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("replacement_settle", [1.0, 2.0])
def test_load_rejects_identical_and_conflicting_duplicate_units(tmp_path, replacement_settle):
    path = write_rows(tmp_path / "rows.jsonl", [settle_row(1e-6, 1.0), settle_row(1e-6, replacement_settle)])
    with pytest.raises(ValueError, match="単位が重複") as exc:
        coef.load(path)
    assert f"{path}:2:" in str(exc.value) and "(2024, 'x')" in str(exc.value)


def test_load_preserves_distinct_seasons_and_teams_and_ignores_blank_lines(tmp_path):
    units = table({(2023, "x"): (0.1, 0.5), (2024, "x"): (0.2, 0.5), (2024, "y"): 0.062})[1e-6]
    path = write_rows(tmp_path / "rows.jsonl", units.values())
    path.write_text("\n" + path.read_text(encoding="utf-8") + " \n", encoding="utf-8")
    assert coef.load(path) == (1e-6, units)


@pytest.mark.parametrize("eps", INVALID_EPS + (True, None, "0.001"))
def test_load_rejects_invalid_eps_on_any_row(tmp_path, eps):
    invalid = settle_row(eps, 2.0)
    invalid["team"] = "y"
    path = write_rows(tmp_path / "rows.jsonl", [settle_row(1e-6, 1.0), invalid])
    with pytest.raises(ValueError, match="有限の正数") as exc:
        coef.load(path)
    assert f"{path}:2:" in str(exc.value)


@pytest.mark.parametrize("rows", [[], [settle_row(1e-6, 1.0), dict(settle_row(1e-3, 2.0), team="y")]])
def test_load_requires_exactly_one_eps(tmp_path, rows):
    with pytest.raises(ValueError, match="ε が 1 つに決まらない"):
        coef.load(write_rows(tmp_path / "rows.jsonl", rows))


@pytest.mark.parametrize("eps", INVALID_EPS)
def test_numeric_entry_points_reject_nonfinite_and_nonpositive_eps(eps):
    with pytest.raises(ValueError, match="有限の正数"):
        coef.eps_form(eps)
    # Validate the keys before sorting or looking up any wave data.
    with pytest.raises(ValueError, match="有限の正数"):
        coef.coefficients({1e-6: {}, eps: {}})


@pytest.mark.parametrize("eps", EPS)
@pytest.mark.parametrize("change", ["missing", "extra", "replacement"])
@pytest.mark.parametrize("committed_decay", [0.0, 0.5])
def test_all_eps_must_have_identical_unit_sets_even_for_nonboundary_units(eps, change, committed_decay):
    t = table({(2014, "b"): (0.1, 0.5), (2024, "x"): (0.2, 0.5)})
    for rows in t.values():
        rows[(2024, "x")]["committed_wave_decay"] = committed_decay
    if change in ("missing", "replacement"):
        del t[eps][(2024, "x")]
    if change in ("extra", "replacement"):
        t[eps][(2024, "y")] = dict(settle_row(eps, 1.0, committed_decay=committed_decay), team="y")
    with pytest.raises(ValueError, match="単位集合") as exc:
        coef.coefficients(t)
    assert "欠落=" in str(exc.value) and "余剰=" in str(exc.value)
    assert "2024" in str(exc.value)


def test_unit_sets_are_validated_before_computing_any_coefficient():
    with pytest.raises(ValueError, match="単位集合"):
        coef.coefficients({1e-9: {(2024, "x"): {}}, 1e-6: {}})


def test_eps_is_written_as_a_times_ten_to_the_minus_n_and_positions_as_mantissa_times_power_of_ten():
    assert coef.eps_form(1e-6) == (1.0, 6) and coef.eps_form(1e-9) == (1.0, 9) and coef.eps_form(0.1) == (1.0, 1)
    assert coef.eps_form(3e-2) == (3.0, 2) and coef.eps_form(5e-3) == (5.0, 3) and coef.eps_form(7e-2) == (7.0, 2)   # 0.07 * 100 は 7.000000000000001
    a, n = coef.eps_form(7.23e-4)
    assert a == pytest.approx(7.23, rel=1e-9) and n == 4
    assert coef.sci(81500.0) == "8.15×10^4" and coef.sci(0.0774) == "7.74×10^-2" and coef.sci(9.996e3) == "1.00×10^4"


def test_coefficient_stays_put_when_eps_gets_ten_times_smaller_and_the_miss_is_reported():
    rows = coef.coefficients(table({(2014, "b"): (0.0815, 0.54), (2022, "l"): (1.595, 0.28), (2013, "g"): 0.062}))
    by = {(r["season"], r["team"]): r for r in rows}
    b = by[(2014, "b")]
    assert b["coefficient"] == pytest.approx(0.0815, rel=1e-6)
    assert [p["n"] for p in b["by_eps"]] == [9, 6, 3] and all(p["a"] == 1.0 for p in b["by_eps"])
    assert [p["coefficient"] for p in b["by_eps"]] == pytest.approx([0.0815, 0.0815, 0.0815 + 0.54e-3], rel=1e-5)
    assert b["abs_miss"] == pytest.approx(0.54, abs=1e-6) and b["rel_miss"] == pytest.approx(0.54 / (0.54 + 81.5), rel=1e-5)
    assert by[(2022, "l")]["coefficient"] == pytest.approx(1.595, rel=1e-6)
    assert abs(by[(2022, "l")]["amp"] - 0.5 * math.exp(1.595)) < 1e-6 and abs(b["amp"] - 0.5 * math.exp(0.0815)) < 1e-6   # 振れ幅 = 0.5 × exp(係数)
    g = by[(2013, "g")]
    assert g["settled_at_start"] and g["position"] == 0.062 and g["coefficient"] is None and g["by_eps"] == []
    assert g["abs_miss"] is None and g["rel_miss"] is None and g["amp"] is None


def test_coefficient_is_one_over_a_when_eps_starts_with_a_five():
    eps = (5e-3, 5e-6, 5e-9)
    r = coef.coefficients(table({(2014, "b"): (0.0815, 0.54)}, eps))[0]
    assert [(p["a"], p["n"]) for p in r["by_eps"]] == [(5.0, 9), (5.0, 6), (5.0, 3)]
    assert r["coefficient"] == pytest.approx(0.0815 / 5, rel=1e-6)
    assert r["abs_miss"] == pytest.approx(0.54, abs=1e-6)       # a を掛け替えても、外れは位置の上乗せ分だけ


def test_float_noise_between_epsilons_does_not_turn_a_constant_position_into_a_huge_coefficient():
    t = table({(2013, "g"): 0.062})
    t[1e-9][(2013, "g")]["eps_wave_settle_x"] += 1e-12      # 丸めの差
    r = coef.coefficients(t)[0]
    assert r["settled_at_start"] and r["coefficient"] is None


def test_a_unit_that_is_not_on_the_boundary_is_left_out():
    t = table({(2014, "b"): (0.1, 0.5)})
    for e in EPS:
        t[e][(2024, "h")] = settle_row(e, 0.067, committed_decay=0.5, decay=0.001)
        t[e][(2024, "h")].update(season=2024, team="h")
    assert [(r["season"], r["team"]) for r in coef.coefficients(t)] == [(2014, "b")]


def test_the_miss_grows_when_the_largest_eps_row_does_not_follow_the_coefficient():
    t = table({(2014, "b"): (0.1, 0.5)})
    r0 = coef.coefficients(t)[0]
    assert (r0["abs_miss"], r0["rel_miss"]) == (pytest.approx(0.5, abs=1e-6), pytest.approx(0.5 / 100.5, rel=1e-5))
    t[1e-3][(2014, "b")]["eps_wave_settle_x"] += 5.0       # ε = 1e-3 の行だけ形から外す
    r = coef.coefficients(t)[0]
    assert (r["abs_miss"], r["rel_miss"]) == (pytest.approx(5.5, abs=1e-6), pytest.approx(5.5 / 105.5, rel=1e-5))


def test_refuses_one_eps_and_a_row_where_the_eps_wave_was_not_chosen():
    with pytest.raises(ValueError):
        coef.coefficients({1e-6: table({(2014, "b"): (0.1, 0.5)})[1e-6]})
    t = table({(2014, "b"): (0.1, 0.5)})
    t[1e-6][(2014, "b")]["eps_wave_decay"] = 0.5
    with pytest.raises(ValueError):
        coef.coefficients(t)


def test_cli_writes_json_and_markdown_without_a_separate_constant(tmp_path):
    t = table({(2014, "b"): (0.0815, 0.54), (2013, "g"): 0.062})
    files = []
    for e, rows in t.items():
        p = tmp_path / f"wave_eps_rows_{e:g}.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows.values()) + "\n", encoding="utf-8")
        files.append(str(p))
    assert coef.settle_cli(["--rows", *files, "--out-json", str(tmp_path / "c.json"), "--out-md", str(tmp_path / "c.md")]) == 0
    data = json.loads((tmp_path / "c.json").read_text(encoding="utf-8"))
    assert data["eps"] == [1e-9, 1e-6, 1e-3] and len(data["units"]) == 2
    md = (tmp_path / "c.md").read_text(encoding="utf-8")
    assert md.startswith("# 落ち着く位置 = 係数 × 10^n") and "ε = 1×10^-9" in md
    assert "| 2014 | b | 8.20×10^1 | 8.15×10^4 | 8.15×10^7 | 0.0815 | 0.542 |" in md       # 指数が 3 ずつ動き、係数は 8.15（ε = 1e-3 だけ上乗せ分で 8.20）
    assert "K" not in md and "K" not in json.dumps(data)
    assert coef.settle_cli(["--rows", files[0], files[0], "--out-json", str(tmp_path / "d.json"), "--out-md", str(tmp_path / "d.md")]) == 2


@pytest.mark.parametrize("existing_outputs", [False, True])
@pytest.mark.parametrize("defect", ["duplicate", "extra", "missing", "repeated_eps", *INVALID_EPS])
def test_cli_invalid_inputs_do_not_create_or_overwrite_outputs(tmp_path, capsys, defect, existing_outputs):
    t = table({(2014, "b"): (0.1, 0.5), (2024, "x"): (0.2, 0.5)})
    inputs = [list(rows.values()) for rows in t.values()]
    if defect == "duplicate":
        inputs[0].append(dict(inputs[0][0]))
    elif defect == "extra":
        inputs[0].append(dict(settle_row(EPS[0], 2.0), team="y"))
    elif defect == "missing":
        inputs[0].pop()
    elif defect == "repeated_eps":
        inputs[0] = inputs[1]
    else:
        for r in inputs[0]:
            r["eps_provisional"] = defect
    files = [str(write_rows(tmp_path / f"rows_{i}.jsonl", rows)) for i, rows in enumerate(inputs)]
    outputs = [tmp_path / "c.json", tmp_path / "c.md"]
    if existing_outputs:
        for path in outputs:
            path.write_text("unchanged\n", encoding="utf-8")
    assert coef.settle_cli(["--rows", *files, "--out-json", str(outputs[0]), "--out-md", str(outputs[1])]) == 2
    captured = capsys.readouterr()
    assert captured.err.strip() and not captured.out
    for path in outputs:
        if existing_outputs:
            assert path.read_text(encoding="utf-8") == "unchanged\n"
        else:
            assert not path.exists()


def test_committed_inputs_reproduce_existing_json_and_markdown_exactly(tmp_path):
    exploratory = ROOT / "cycles" / "c001-chunichi" / "exploratory"
    files = sorted((exploratory / "wave_eps_trial_results").glob("wave_eps_rows_*.jsonl"))
    by_eps = dict(coef.load(path) for path in files)
    assert len(files) == len(by_eps) == 3
    assert all(len(units) == 156 for units in by_eps.values())
    out_json, out_md = tmp_path / "c.json", tmp_path / "c.md"
    assert coef.settle_cli(["--rows", *map(str, files), "--out-json", str(out_json), "--out-md", str(out_md)]) == 0
    saved = exploratory / "wave_eps_sensitivity_results"
    assert out_json.read_bytes() == (saved / "wave_eps_settle_coefficients.json").read_bytes()
    assert out_md.read_bytes() == (saved / "wave_eps_settle_coefficients.md").read_bytes()


def test_2026_rows_added_to_the_committed_rows_reproduce_the_saved_coefficients_exactly(tmp_path):
    """2013〜2025年の 156 単位の行に、2026年の 12 単位の行（wave_eps_2026_results）を足すと、保存済みの 168 単位の表が再現できる。"""
    exploratory = ROOT / "cycles" / "c001-chunichi" / "exploratory"
    saved = exploratory / "wave_eps_2026_results"
    files = []
    for old in sorted((exploratory / "wave_eps_trial_results").glob("wave_eps_rows_*.jsonl")):
        new = saved / old.name
        assert {k[0] for k in coef.load(new)[1]} == {2026} and len(coef.load(new)[1]) == 12
        merged = tmp_path / old.name
        merged.write_text(old.read_text(encoding="utf-8") + new.read_text(encoding="utf-8"), encoding="utf-8")
        files.append(merged)
    by_eps = dict(coef.load(path) for path in files)
    assert len(files) == len(by_eps) == 3 and all(len(units) == 168 for units in by_eps.values())
    out_json, out_md = tmp_path / "c.json", tmp_path / "c.md"
    assert coef.settle_cli(["--rows", *map(str, files), "--out-json", str(out_json), "--out-md", str(out_md)]) == 0
    assert out_json.read_bytes() == (saved / "wave_eps_settle_coefficients.json").read_bytes()
    assert out_md.read_bytes() == (saved / "wave_eps_settle_coefficients.md").read_bytes()
    gate = json.loads((saved / "wave_eps_trial_gate.json").read_text(encoding="utf-8"))
    assert gate["pass"] and gate["units"] == 168 and gate["rows_differ"] == 0 and gate["new_seasons"] == [2026] and gate["new_units"] == 12
    assert json.loads((saved / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8")) == gate


def input_files(tmp_path, units):
    return [str(write_rows(tmp_path / f"rows_{e:g}.jsonl", rows.values())) for e, rows in table(units).items()]


@pytest.mark.parametrize("units", [{(2013, "g"): 0.062, (2019, "h"): 0.060}, {}])
def test_cli_handles_inputs_where_no_unit_moves_with_eps(tmp_path, units):
    """全単位が最初から一定（または境界の単位が 0）でも、集計対象が空だからといって落ちない。"""
    files = input_files(tmp_path, units or {(2024, "x"): 0.5})
    if not units:                                   # 境界の単位が 1 つもない入力
        for path in files:
            rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
            write_rows(Path(path), [dict(r, committed_wave_decay=0.5, eps_wave_decay=0.001) for r in rows])
    out_json, out_md = tmp_path / "c.json", tmp_path / "c.md"
    assert coef.settle_cli(["--rows", *files, "--out-json", str(out_json), "--out-md", str(out_md)]) == 0
    data = json.loads(out_json.read_text(encoding="utf-8"))
    md = out_md.read_text(encoding="utf-8")
    assert len(data["units"]) == len(units) and all(u["settled_at_start"] for u in data["units"])
    assert md.count(coef.NONE) == 2 and f"減衰 0 だった単位: {len(units)}。落ち着く位置が最初から ε によらず一定: {len(units)}" in md
    for r in units:
        assert f"| {r[0]} | {r[1]} | （最初から一定。位置" in md


def test_cli_builds_both_texts_before_writing_either_output(tmp_path, monkeypatch):
    files = input_files(tmp_path, {(2014, "b"): (0.1, 0.5)})
    outputs = [tmp_path / "c.json", tmp_path / "c.md"]
    for path in outputs:
        path.write_text("unchanged\n", encoding="utf-8")

    def broken(rows, eps):
        raise RuntimeError("render failed")

    monkeypatch.setattr(coef, "settle_cli_render", broken)
    with pytest.raises(RuntimeError, match="render failed"):
        coef.settle_cli(["--rows", *files, "--out-json", str(outputs[0]), "--out-md", str(outputs[1])])
    assert [p.read_text(encoding="utf-8") for p in outputs] == ["unchanged\n", "unchanged\n"]


# ==== tie_noise（旧 test_c001_wave_tie_noise.py）
# cycles/c001-chunichi/exploratory/wave_tie_noise.py の確認。
#
# 合成の線と合成の試合（SYNTHETIC: 2 球団のリーグ）を使う。実データではなく、float64 の再実装が今の wave_fit と一致すること、longdouble で選ぶ版が
# 丸めの影響を外した読みになっていること、数え方・表・終了コードが約束どおりに動くことを確かめるだけで、結論には使わない。


EXPL = ROOT / "cycles" / "c001-chunichi" / "exploratory"
sys.path.insert(0, str(EXPL))


def load(name):
    spec = importlib.util.spec_from_file_location(name, EXPL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wt = load("wave_eps")
tn = load("wave_tie_noise")

XS149 = [i / 148 for i in range(149)]
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


def tie_noise_games_df():
    return pl.DataFrame([{"key": str(i), "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g",
                          "hs": 3 if i < 15 else 1, "as": 1 if i < 15 else 3} for i in range(30)])


@pytest.fixture(scope="module")
def tie_noise_tg():
    return sa.to_team_games(tie_noise_games_df(), TEAMS)


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
def test_capture_line_returns_the_real_line_the_basis_and_restores_the_module(tie_noise_tg):
    old = (sa._season_paths, sa.wave_fit, sa.wave_basis)
    cap = tn.capture_line(sa, tie_noise_tg, "g", sa.wave_basis, 5, "season")
    assert (sa._season_paths, sa.wave_fit, sa.wave_basis) == old
    assert len(cap["ys"]) >= 5 and cap["x1"] == 1.0 and 0.0 <= cap["x0"] < 1.0
    assert len(cap["basis"]) == len(sa.wave_basis([0.0, 0.5, 1.0]))
    other = tn.capture_line(sa, tie_noise_tg, "d", sa.wave_basis, 5, "season")      # 線は順位の高さ（2 球団なら 1 位が 2、2 位が 1）。最初は中日が勝っている
    assert cap["ys"][0] == 1.0 and other["ys"][0] == 2.0 and cap["ys"] != other["ys"]


def test_analyze_runs_on_the_synthetic_league_and_is_reproducible(tie_noise_tg):
    kw = dict(sims=3, min_games=5, end="season", eps_osc=(1e-3, 1e-6), sb_grid=(1e-3, 1e-9), sb=(2024, "g"))
    a, b = tn.analyze(sa, wt, tie_noise_tg, **kw), tn.analyze(sa, wt, tie_noise_tg, **kw)
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


def test_a_constant_line_in_the_league_is_reported_as_flat(tie_noise_tg):
    flat = pl.DataFrame([{"key": str(i), "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g", "hs": 3, "as": 1} for i in range(30)])
    cap = tn.capture_line(sa, sa.to_team_games(flat, TEAMS), "d", sa.wave_basis, 5, "season")
    assert len(set(cap["ys"])) == 1 and len(cap["ys"]) >= 5
    assert tn.line_table(sa, cap)["candidates"] > 0


def tie_noise_row(**kw):
    return {c: None for c in wt.WAVE_COLS} | kw


def test_changed_units_lists_only_the_units_whose_named_column_differs():
    ref = {(2024, "h"): tie_noise_row(wave_osc_base=0.5), (2024, "g"): tie_noise_row(wave_osc_base=0.5), (2013, "d"): tie_noise_row(wave_osc_base=0.1)}
    other = {(2024, "h"): tie_noise_row(wave_osc_base=0.5), (2024, "g"): tie_noise_row(wave_osc_base=0.505), (2013, "d"): tie_noise_row(wave_osc_base=0.1, wave_decay=1.0)}
    assert tn.changed_units(ref, other, wt, "wave_osc_base") == ["2024-g"] and tn.changed_units(ref, other, wt, "wave_decay") == ["2013-d"]
    assert tn.label((2024, "h")) == "2024-h"


def test_analyze_puts_each_count_under_the_right_mode_and_the_right_epsilon(tie_noise_tg, monkeypatch):
    base = {(2024, "h"): tie_noise_row(wave_osc_base=0.5), (2024, "g"): tie_noise_row(wave_osc_base=0.5), (2023, "d"): tie_noise_row(wave_osc_base=0.2)}

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
    res = tn.analyze(sa, wt, tie_noise_tg, sims=1, min_games=5, end="season", eps_osc=(1e-3, 1e-6), sb_grid=(1e-9,), sb=(2024, "g"))
    assert res["osc_base"]["1e-06"] == {"f64": {"units": 1, "labels": ["2024-h"]}, "ld": {"units": 0, "labels": []}}
    assert res["osc_base"]["0.001"] == {"f64": {"units": 1, "labels": ["2024-g"]}, "ld": {"units": 1, "labels": ["2024-g"]}}
    assert res["control_f64_vs_ld"] == {"units_differ": 1, "by_column": {"wave_decay": {"units": 1, "labels": ["2023-d"]},
                                                                          "wave_osc_base": {"units": 1, "labels": ["2023-d"]}}}
    assert res["units"] == 3 and res["calls"]["calls"] == 1 and res["softbank"]["line"]["flat"] is True
    assert [r["eps"] for r in res["softbank"]["rows"]] == [None, 1e-9]


# ---- コマンドライン ---------------------------------------------------------------------------------------------------------
def write_inputs(tmp_path, tie_noise_tg, tweak=False):
    games = tmp_path / "games.jsonl"
    tie_noise_games_df().write_ndjson(games)
    cfg = tmp_path / "analysis.toml"
    cfg.write_text(TOML, encoding="utf-8")
    ctrl = wt.trajectory(sa, tie_noise_tg, sa.wave_basis, 3, 5, "season")
    committed = tmp_path / "season.jsonl"
    rows = [dict(r) for r in ctrl.values()]
    if tweak:
        rows[0]["wave_decay"] = 99.0
    committed.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return games, cfg, committed


def test_main_writes_json_and_markdown_and_is_byte_reproducible(tmp_path, tie_noise_tg):
    games, cfg, committed = write_inputs(tmp_path, tie_noise_tg)
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


def test_main_stops_when_the_control_does_not_match_the_committed_rows_or_the_unit_is_missing(tmp_path, tie_noise_tg):
    games, cfg, committed = write_inputs(tmp_path, tie_noise_tg, tweak=True)
    base = ["--games", str(games), "--config", str(cfg), "--unit", "2024", "g", "--repo", str(ROOT)]
    assert tn.main(base + ["--committed", str(committed), "--outdir", str(tmp_path / "bad")]) == 2
    assert not (tmp_path / "bad").exists()
    games, cfg, committed = write_inputs(tmp_path, tie_noise_tg)
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
TIE_NOISE_RESULTS = EXPL / "wave_tie_noise_results"


def results_json():
    return json.loads((TIE_NOISE_RESULTS / "wave_tie_noise.json").read_text(encoding="utf-8"))


def sci(x):
    m, e = f"{x:.3g}".split("e")
    return f"{m}×10^{int(e)}"


def test_the_md_in_the_results_is_what_render_makes_from_the_json():
    assert (TIE_NOISE_RESULTS / "wave_tie_noise.md").read_text(encoding="utf-8") == tn.render(results_json())


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
    j, md = results_json(), (TIE_NOISE_RESULTS / "README.md").read_text(encoding="utf-8")
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


# ==== flat（旧 test_c001_wave_flat_by_python.py）
# 一定の線に当てはめる式が Python のバージョンで変わるかの確認（cycles/c001-chunichi/exploratory/wave_flat_by_python.py）。


EXPLORATORY = ROOT / "cycles" / "c001-chunichi" / "exploratory"
FLAT_RESULTS = EXPLORATORY / "wave_tie_noise_results"


def _load():
    spec = importlib.util.spec_from_file_location("c001_wave_flat_by_python", EXPLORATORY / "wave_flat_by_python.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


flat = _load()


def results():
    return json.loads((FLAT_RESULTS / "wave_flat_by_python.json").read_text(encoding="utf-8"))


def test_sum_of_floats_changed_in_python_3_12_which_is_the_cause_named_in_the_readme():
    # 0.1 を 10 回足す: 3.11 は 0.9999999999999999、3.12 以降は 1.0（足し方が補正つきに変わった）
    assert (sum([0.1] * 10) == 1.0) == (sys.version_info >= (3, 12))


def test_flat_forms_covers_the_declared_lines_and_each_value_is_a_decay_and_a_period():
    forms = flat.flat_forms(flat.load_sa())
    assert len(forms) == len(flat.LENGTHS) * len(flat.LEVELS) == 32
    for k, (decay, period) in forms.items():
        assert k.startswith("n=") and decay > 0 and (period is None or period > 0)


def test_the_results_json_has_the_five_interpreters_and_the_same_32_lines():
    r = results()
    assert [v.split(".")[:2] for v in r["runs"]] == [["3", "11"], ["3", "12"], ["3", "13"], ["3", "14"], ["3", "15"]]
    assert r["lengths"] == list(flat.LENGTHS) and r["levels"] == list(flat.LEVELS)
    for forms in r["runs"].values():
        assert len(forms) == 32


def test_the_readme_table_is_the_json_comparison_against_3_12():
    r, md = results(), (FLAT_RESULTS / "README.md").read_text(encoding="utf-8")
    ref = next(f for v, f in r["runs"].items() if v.startswith("3.12."))
    diffs = {v: sorted(k for k in f if f[k] != ref[k]) for v, f in r["runs"].items()}
    assert {v.split(".")[1]: len(d) for v, d in diffs.items()} == {"11": 6, "12": 0, "13": 0, "14": 0, "15": 0}
    for v, d in diffs.items():
        assert f"| {v} | {len(d)}" in md or f"| {v} | {len(d)} 本" in md
    # 3.11 だけが違う線の名前を、n ごとにまとめた形（n=60 c=5、n=100 c=4・5・6、…）で README が書いている
    by_n = {}
    for k in diffs["3.11.17"]:
        n, c = (part.split("=")[1] for part in k.split())
        by_n.setdefault(int(n), []).append(float(c))
    text = "、".join(f"n={n} c={'・'.join(f'{c:g}' for c in sorted(cs))}" for n, cs in sorted(by_n.items()))
    assert f"6 本（{text}）" in md
    assert "3.12 以降の 4 つは 32 本すべてで同じ式を選び、3.11 だけが 6 本で違いました" in md
