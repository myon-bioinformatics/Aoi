import math

import polars as pl
import pytest

from sakanalytics import K_FIXED, add_rank, season_table, to_team_games

TEAMS = {"d": {"name": "中日", "league": "C"}, "g": {"name": "巨人", "league": "C"},
         "t": {"name": "阪神", "league": "C"}, "h": {"name": "ソフトバンク", "league": "P"}}


def games(rows):
    return pl.DataFrame([{"key": str(i), "date": d, "home": h, "away": a, "hs": hs, "as": as_}
                         for i, (d, h, a, hs, as_) in enumerate(rows)])


def chunichi(results):
    """results: [(rf, ra), ...] を中日のホーム試合として1シーズン分作る。"""
    st = season_table(to_team_games(games([("2024-04-01", "d", "g", rf, ra) for rf, ra in results]), TEAMS))
    return st.filter(pl.col("team") == "d").row(0, named=True)


def test_unknown_team_is_an_error_not_a_silent_drop():
    with pytest.raises(ValueError, match="x"):
        to_team_games(games([("2024-04-01", "d", "x", 1, 0)]), TEAMS)


def test_counts_bins_and_spread():
    st = chunichi([(3, 2), (2, 1), (4, 2), (6, 1), (1, 2), (0, 8), (2, 2)])
    assert (st["W"], st["L"], st["T"], st["G"]) == (4, 2, 1, 7)
    assert (st["w_1"], st["w_2"], st["w_3"], st["w_4plus"]) == (2, 1, 0, 1)
    assert (st["l_1"], st["l_4plus"]) == (1, 1)
    assert st["win_margin_median"] == 1.5 and st["win_margin_mode"] == 1
    assert st["loss_margin_median"] == 4.5
    assert st["wpct"] == pytest.approx(4 / 6)
    assert st["wpct_1run"] == pytest.approx(2 / 3) and st["wpct_2run"] == pytest.approx(1.0)


def test_pythag_and_logit_resid():
    st = chunichi([(5, 3), (2, 4), (6, 1)])  # RF=13, RA=8
    rf, ra, wp = 13, 8, 2 / 3
    assert st["pythag_fixed"] == pytest.approx(1 / (1 + (ra / rf) ** K_FIXED))
    assert st["pythag_var"] == pytest.approx(1 / (1 + (ra / rf) ** (((rf + ra) / 3) ** 0.287)))
    assert st["logit_resid"] == pytest.approx(math.log(wp / (1 - wp)) - K_FIXED * math.log(rf / ra))
    assert st["k_eff"] == pytest.approx(math.log(2) / math.log(rf / ra))


def test_k_eff_null_when_runs_equal():
    st = chunichi([(3, 2), (1, 2)])
    assert st["k_eff"] is None and st["logit_resid"] == pytest.approx(0.0)


def test_rank_within_league_with_tie_flag():
    st = pl.DataFrame({
        "season": [2024] * 5, "team": ["a", "b", "c", "d", "e"], "league": ["C", "C", "C", "C", "P"],
        "wpct": [0.6, 0.5, 0.5, 0.4, 0.3],
    })
    r = add_rank(st).sort("team")
    assert r["rank"].to_list() == [1, 2, 2, 4, 1]  # 同率は小さい順位にそろえ、次は飛ばす
    assert r["rank_tie"].to_list() == [False, True, True, False, False]
    assert r["league_size"].to_list() == [4, 4, 4, 4, 1]


def test_interleague_games_count_for_both_leagues():
    st = season_table(to_team_games(games([("2024-06-01", "d", "h", 2, 1)]), TEAMS))
    assert st.select("team", "league", "W", "L").sort("team").rows() == [("d", "C", 1, 0), ("h", "P", 0, 1)]


def test_explanatory_columns():
    # 中日 3勝2敗(3-20)、巨人 2勝4敗(22-6)、阪神 1勝0敗(3-2)
    rows = [("2024-04-01", "d", "g", 1, 0)] * 3 + [("2024-04-02", "g", "d", 10, 0)] * 2 + [("2024-04-03", "t", "g", 3, 2)]
    st = season_table(to_team_games(games(rows), TEAMS)).filter(pl.col("league") == "C")
    got = {r["team"]: r for r in st.iter_rows(named=True)}
    cols = ("rank", "upper_half", "rd", "rank_pythag", "rank_gap", "rank_rf", "rank_ra", "rank_rd")
    assert {t: tuple(r[c] for c in cols) for t, r in got.items()} == {
        "t": (1, True, 1, 2, -1, 2, 1, 2),
        "d": (2, False, -17, 3, -1, 2, 3, 3),   # 得点は阪神と同数 → 同順位2
        "g": (3, False, 16, 1, 2, 1, 2, 1),     # 得失点はリーグ最良なのに最下位 = 典型的な判例
    }
    d = got["d"]
    assert d["wins_vs_pythag"] == pytest.approx(3 - 5 * d["pythag_fixed"])


def test_margin_net_columns_can_be_negative():
    # 中日: 1点差 1勝2敗、4点以上差 0勝1敗（u32 の引き算で桁あふれしないこと）
    rows = [("2024-04-01", "d", "g", 2, 1), ("2024-04-02", "d", "g", 1, 2), ("2024-04-03", "d", "g", 3, 4),
            ("2024-04-04", "d", "g", 0, 9)]
    d = season_table(to_team_games(games(rows), TEAMS)).filter(pl.col("team") == "d").row(0, named=True)
    assert (d["one_run_net"], d["two_run_net"], d["blowout_net"]) == (-1, 0, -1)
    assert d["rank_wpct_1run"] == 2  # 中日 1/3、巨人 2/3
