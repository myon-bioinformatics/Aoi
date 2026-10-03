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


# ---------- 配分効果（R1） ----------

def _brute(rf, ra):
    """全通りの組み合わせを数えた（勝 − 敗）の平均と分散。"""
    from itertools import permutations
    vals = [sum((a > b) - (a < b) for a, b in zip(rf, p)) for p in permutations(ra)]
    m = sum(vals) / len(vals)
    return m, sum((v - m) ** 2 for v in vals) / len(vals)


@pytest.mark.parametrize("rf,ra", [
    ([3, 1], [2, 2]),
    ([5, 0, 2, 2], [1, 3, 2, 0]),         # 引き分けを含む
    ([1, 1, 1, 1, 1], [0, 2, 1, 3, 1]),   # 同じ得点が並ぶ
    ([10, 0, 4, 3, 2, 7], [3, 3, 1, 9, 0, 2]),
    ([0, 0, 0], [0, 0, 0]),               # すべて引き分け → 分散 0
])
def test_allocation_matches_enumeration(rf, ra):
    from sakanalytics import allocation
    exp, var = allocation(rf, ra)
    bm, bv = _brute(rf, ra)
    assert exp == pytest.approx(bm) and var == pytest.approx(bv)


def test_allocation_random_small_cases_match_enumeration():
    import random
    from sakanalytics import allocation
    rnd = random.Random(1)
    for _ in range(60):
        n = rnd.randint(2, 6)
        rf, ra = [rnd.randint(0, 6) for _ in range(n)], [rnd.randint(0, 6) for _ in range(n)]
        exp, var = allocation(rf, ra)
        bm, bv = _brute(rf, ra)
        assert exp == pytest.approx(bm) and var == pytest.approx(bv), (rf, ra)


def test_allocation_edges():
    from sakanalytics import allocation
    assert allocation([], []) == (0.0, 0.0)
    assert allocation([3], [1]) == (1.0, 0.0)
    with pytest.raises(ValueError):
        allocation([1, 2], [1])


def test_allocation_effect_detects_concentrated_runs():
    # 総得点・総失点は同じ（得点 2,2,2,2,10 / 失点 3,3,3,3,0）。
    # 実際の組み合わせ: 大勝1つ・惜敗4つ → 1勝4敗。ランダムなら平均ではもっと勝てる
    from sakanalytics import allocation_table
    rows = [("2024-04-0%d" % (i + 1), "d", "g", hs, as_) for i, (hs, as_) in enumerate([(2, 3)] * 4 + [(10, 0)])]
    tg = to_team_games(games(rows), TEAMS)
    d = allocation_table(tg).filter(pl.col("team") == "d").row(0, named=True)
    exp_net = (4 * (-4 + 1) + 1 * 5) / 5  # 2点の試合: 0点の相手にだけ勝つ / 10点の試合: 全勝
    assert d["alloc_exp_net"] == pytest.approx(exp_net)
    assert d["alloc_net"] == pytest.approx(-3 - exp_net) and d["alloc_net"] < 0
    # 中日はすべてホームなので、ホームだけの基準＝全体、ビジターは試合なし
    assert d["alloc_net_home"] == pytest.approx(d["alloc_net"]) and d["alloc_var_away"] == 0.0
    assert d["alloc_z_away"] is None
    assert d["alloc_net_strat"] == pytest.approx(d["alloc_net_home"])


def test_allocation_next_season_and_same_sign():
    from sakanalytics import allocation_table
    rows = []
    for y in (2023, 2024, 2026):  # 2025 がない → 2024 の翌年は空
        rows += [(f"{y}-04-01", "d", "g", 2, 3), (f"{y}-04-02", "d", "g", 9, 0),
                 (f"{y}-04-03", "g", "d", 3, 2), (f"{y}-04-04", "g", "d", 0, 9)]
    t = allocation_table(to_team_games(games(rows), TEAMS)).filter(pl.col("team") == "d").sort("season")
    z = t["alloc_z"].to_list()
    assert t["alloc_z_next"].to_list() == [z[1], None, None]
    # Series の drop_nulls()/abs() は Python 3.15 ベータ + polars 1.44.2 で None を返すので、式で書く
    assert set(t.select(pl.col("alloc_same_sign").drop_nulls())["alloc_same_sign"].to_list()) <= {True, False}
    assert t["alloc_z_abs"].to_list() == [abs(v) for v in z]
