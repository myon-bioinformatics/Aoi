"""cycles/c001-chunichi/exploratory/wave_eps_sensitivity.py の確認。

合成の試合（SYNTHETIC: 2 球団のリーグで、g が前半に負け続け後半に勝ち続ける線）を使う。実データではなく、読みの計算（境界の数え方、
ε を振ったときの動き、線を動かしたときの入れ替わり、関門）が約束どおりに動くかを確かめるだけで、結論には使わない。
"""
import importlib.util
import json
import sys
from pathlib import Path

import polars as pl
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sakanalytics"))
import sakanalytics as sa  # noqa: E402

spec = importlib.util.spec_from_file_location("wave_eps_sensitivity", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps_sensitivity.py")
sens = importlib.util.module_from_spec(spec)
sys.modules["wave_eps_sensitivity"] = sens
spec.loader.exec_module(sens)

TEAMS = {"d": {"name": "中日", "league": "C"}, "g": {"name": "巨人", "league": "C"}}


def games_df() -> pl.DataFrame:
    rows = [{"key": str(i), "date": f"2024-04-{i + 1:02d}", "home": "d", "away": "g",
             "hs": 3 if i < 15 else 1, "as": 1 if i < 15 else 3} for i in range(30)]
    return pl.DataFrame(rows)


@pytest.fixture(scope="module")
def tg():
    return sa.to_team_games(games_df(), TEAMS)


@pytest.fixture(scope="module")
def report(tg):
    return sens.analyze(sa, tg, sims=5, grid=(1e-3, 1e-6, 1e-9), min_games=(5, 10), ends=("season", "decided"), variant_eps=1e-6)


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
    text = sens.render(report)
    for part in ("## 1. ε を振る", "## 2. 線の始まり・終わりを動かす（ε = 1e-06）", "## 3. 基準の境界の単位は", "結論には使わない"):
        assert part in text
    assert text.count("\n| 1e-") >= 2


def _files(tmp_path):
    games_df().write_ndjson(tmp_path / "games.jsonl")
    cfg = ["[trajectory]", "min_games = 10", "sims = 5", "", "[teams]"] + [f'{t} = {{ name = "{v["name"]}", league = "{v["league"]}" }}' for t, v in TEAMS.items()]
    (tmp_path / "analysis.toml").write_text("\n".join(cfg) + "\n", encoding="utf-8")
    plain = sa.season_trajectory(sa.to_team_games(games_df(), TEAMS), sims=5, min_games=10, end="season")
    rows = [{"season": r["season"], "team": r["team"], **{c: r[c] for c in sens.trial.WAVE_COLS}} for r in plain.to_dicts()]
    committed = tmp_path / "season.jsonl"
    committed.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return rows, committed


def _argv(tmp_path, committed):
    return ["--games", str(tmp_path / "games.jsonl"), "--config", str(tmp_path / "analysis.toml"), "--committed", str(committed),
            "--outdir", str(tmp_path / "out"), "--repo", str(ROOT), "--grid", "1e-3", "1e-6", "--min-games", "5", "10", "--ends", "season"]


def test_cli_writes_the_reports_when_the_control_matches(tmp_path):
    _, committed = _files(tmp_path)
    assert sens.main(_argv(tmp_path, committed)) == 0
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
    assert sens.main(_argv(tmp_path, committed)) == 2
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
    assert sens.main(_argv(tmp_path, empty) + ["--new-seasons", "2024"]) == 0
    g = json.loads((tmp_path / "out" / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8"))
    assert g["pass"] is True and g["new_seasons"] == [2024] and g["new_units"] == 2 and g["units"] == 2


def test_cli_still_stops_when_the_named_new_season_has_committed_rows_or_the_season_is_not_in_the_games(tmp_path):
    _, committed = _files(tmp_path)
    assert sens.main(_argv(tmp_path, committed) + ["--new-seasons", "2024"]) == 2
    g = json.loads((tmp_path / "out" / "wave_eps_sensitivity_gate.json").read_text(encoding="utf-8"))
    assert g["pass"] is False and g["new_seasons_with_committed_rows"] == 2
    assert not (tmp_path / "out" / "wave_eps_sensitivity.json").exists()
    assert sens.main(_argv(tmp_path, committed) + ["--new-seasons", "2027"]) == 2
