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


def test_opponent_strata_equal_home_away_strata_when_only_one_opponent():
    from sakanalytics import allocation_table
    rows = [("2024-04-01", "d", "g", 2, 3), ("2024-04-02", "d", "g", 9, 0), ("2024-04-03", "d", "g", 4, 4),
            ("2024-04-04", "g", "d", 3, 2), ("2024-04-05", "g", "d", 0, 9), ("2024-04-06", "g", "d", 1, 5)]
    d = allocation_table(to_team_games(games(rows), TEAMS)).filter(pl.col("team") == "d").row(0, named=True)
    for k in ("exp_net", "var", "net", "z"):
        assert d[f"alloc_{k}_opp"] == pytest.approx(d[f"alloc_{k}_strat"])


def test_opponent_strata_match_shuffle_of_runs_allowed_in_win_equivalents():
    # PR #3（R001）の方法: 得点を固定し、失点だけを（相手 × ホーム/ビジター）の中で並べ替え、
    # 勝相当 WE = W + 0.5·D の平均との差を取る。全通りを数えると、勝−敗の差 = 2 × WE の差になる（引き分けを含めて）
    from itertools import permutations
    from sakanalytics import allocation_table
    rows = [("2024-04-01", "d", "g", 2, 3), ("2024-04-02", "d", "g", 9, 0), ("2024-04-03", "d", "g", 4, 4),
            ("2024-04-04", "g", "d", 3, 2), ("2024-04-05", "g", "d", 0, 9),
            ("2024-04-06", "d", "t", 1, 5), ("2024-04-07", "d", "t", 5, 1), ("2024-04-08", "d", "t", 3, 3),
            ("2024-04-09", "t", "d", 6, 2), ("2024-04-10", "t", "d", 2, 2)]
    tg = to_team_games(games(rows), TEAMS).filter(pl.col("team") == "d")

    def we(rf, ra):
        return sum(1.0 if a > b else 0.5 if a == b else 0.0 for a, b in zip(rf, ra))

    excess_we = 0.0
    for _, cell in tg.group_by(["opp", "is_home"]):
        rf, ra = cell["rf"].to_list(), cell["ra"].to_list()
        perms = list(permutations(ra))
        excess_we += we(rf, ra) - sum(we(rf, p) for p in perms) / len(perms)
    d = allocation_table(tg).row(0, named=True)
    assert d["alloc_net_opp"] == pytest.approx(2 * excess_we)


def test_home_away_gap_against_other_teams_of_the_league():
    rows = [("2024-04-01", "d", "g", 5, 1), ("2024-04-02", "g", "d", 3, 1),   # d: ホーム +4、ビジター −2
            ("2024-04-03", "t", "g", 2, 2), ("2024-04-04", "g", "t", 0, 1)]   # g: ホーム +2/−1、ビジター −4/0
    st = season_table(to_team_games(games(rows), TEAMS))
    v = {r["team"]: r for r in st.iter_rows(named=True)}
    assert (v["d"]["rd_home_g"], v["d"]["rd_away_g"], v["d"]["home_away_gap"]) == (4.0, -2.0, 6.0)
    assert v["g"]["home_away_gap"] == pytest.approx(0.5 - (-2.0))
    assert v["t"]["home_away_gap"] == pytest.approx(0.0 - 1.0)
    # 他の2球団の平均との差
    assert v["d"]["home_away_gap_vs_league"] == pytest.approx(6.0 - (2.5 + -1.0) / 2)


def test_scoring_deficit_bands_by_hand():
    # d の得点 0, 7 / g の得点 2, 2 / t の得点 4, 4（3チームとも同じ年・同じリーグ）
    rows = [("2024-04-01", "d", "g", 0, 2), ("2024-04-02", "g", "d", 2, 7),
            ("2024-04-03", "t", "g", 4, 1), ("2024-04-04", "g", "t", 1, 4)]
    v = {r["team"]: r for r in season_table(to_team_games(games(rows), TEAMS)).iter_rows(named=True)}
    for t, r in v.items():
        others = [o for o in v.values() if o["team"] != t]
        mean_other = sum(o["RF"] / o["G"] for o in others) / len(others)
        assert r["rf_def_floor"] + r["rf_def_mid"] + r["rf_def_ceiling"] == pytest.approx(r["rf_def_total"])
        assert r["rf_def_total"] == pytest.approx(r["RF"] / r["G"] - mean_other)
    # d: P(≥1)=P(≥2)=.5, P(≥3..7)=.5。他: t(4,4) は P(≥1..4)=1、g(2,1,2,1) は P(≥1)=1, P(≥2)=.5
    assert v["d"]["rf_def_floor"] == pytest.approx((0.5 - 1.0) + (0.5 - 0.75))
    assert v["d"]["rf_def_mid"] == pytest.approx((0.5 - 0.5) * 2 + (0.5 - 0.0))
    assert v["d"]["rf_def_ceiling"] == pytest.approx(0.5 * 2)
    assert v["d"]["rf_def_floor_minus_ceiling"] == pytest.approx(-0.75 - 1.0)


def test_scoring_deficit_is_relative_within_season_and_league():
    from sakanalytics import scoring_deficit
    rows = [("2024-04-01", "d", "g", 3, 1), ("2024-04-02", "h", "f", 9, 0), ("2025-04-01", "d", "g", 1, 1)]
    teams = {**TEAMS, "f": {"name": "日本ハム", "league": "P"}}
    t = scoring_deficit(to_team_games(games(rows), teams))
    got = {(r["season"], r["team"]): r["rf_def_total"] for r in t.iter_rows(named=True)}
    assert got[(2024, "d")] == pytest.approx(3 - 1) and got[(2024, "h")] == pytest.approx(9 - 0)  # 他リーグと混ぜない
    assert got[(2025, "d")] == pytest.approx(0.0)


def _innings_rows(st, scoring):
    """st の G・RF に合わせたイニング集計。scoring: team -> (攻撃回数, 得点した回の数)"""
    rows = []
    for r in st.iter_rows(named=True):
        if r["team"] in scoring:
            i, s_ = scoring[r["team"]]
            for w in ("all", "first6"):
                rows.append({"season": r["season"], "team": r["team"], "window": w, "games": r["G"],
                             "innings": i, "runs": r["RF"], "scoring_innings": s_})
    return pl.DataFrame(rows, schema_overrides={"season": pl.Int32})


def test_inning_decomposition_identity_and_relative_to_league():
    from sakanalytics import inning_decomposition
    rows = [("2024-04-01", "d", "g", 2, 6), ("2024-04-02", "g", "t", 4, 3), ("2024-04-03", "t", "d", 5, 1)]
    st = season_table(to_team_games(games(rows), TEAMS))
    out = inning_decomposition(st, _innings_rows(st, {"d": (18, 2), "g": (17, 3), "t": (17, 4)}))
    v = {r["team"]: r for r in out.iter_rows(named=True)}
    for r in v.values():
        assert r["inn_dlog_freq"] + r["inn_dlog_size"] == pytest.approx(r["inn_dlog_rpi"])
        assert r["inn_freq_minus_size"] == pytest.approx(r["inn_dlog_freq"] - r["inn_dlog_size"])
    # d: 得点 3（2+1）、攻撃 18 回、得点した回 2。他の2球団の log の平均との差
    lf = lambda s_, i: math.log(s_ / i)  # noqa: E731
    assert v["d"]["inn_dlog_freq"] == pytest.approx(lf(2, 18) - (lf(3, 17) + lf(4, 17)) / 2)
    assert v["d"]["inn_dlog_size"] == pytest.approx(math.log(3 / 2) - (math.log(v["g"]["RF"] / 3) + math.log(v["t"]["RF"] / 4)) / 2)


def test_inning_decomposition_stops_on_mismatch_and_leaves_missing_seasons_empty():
    from sakanalytics import inning_decomposition
    rows = [("2024-04-01", "d", "g", 2, 6), ("2024-04-02", "g", "t", 4, 3), ("2024-04-03", "t", "d", 5, 1)]
    st = season_table(to_team_games(games(rows), TEAMS))
    bad = _innings_rows(st, {"d": (18, 2)}).with_columns(runs=pl.col("runs") + 1)
    with pytest.raises(ValueError, match="合わない"):
        inning_decomposition(st, bad)
    out = inning_decomposition(st, _innings_rows(st, {"d": (18, 2), "g": (17, 3)}))
    t = out.filter(pl.col("team") == "t").row(0, named=True)
    assert t["inn_I"] is None and t["inn_dlog_freq"] is None  # 集計のない単位は 0 ではなく空


def test_inning_venue_split_and_scoring_inning_shares():
    from sakanalytics import inning_decomposition
    rows = [("2024-04-01", "d", "g", 2, 6), ("2024-04-02", "g", "t", 4, 3), ("2024-04-03", "t", "d", 5, 1)]
    st = season_table(to_team_games(games(rows), TEAMS))
    base = []
    for r in st.iter_rows(named=True):
        # 全体: 攻撃 18 回・得点した回 3（1点の回 2、3点以上の回 1）。ホームとビジターに半分ずつ
        for venue, k in (("all", 1), ("home", 0.5), ("away", 0.5)):
            base.append({"season": r["season"], "team": r["team"], "venue": venue, "window": "all",
                         "games": r["G"] * k, "innings": 18 * k, "runs": r["RF"] * k, "scoring_innings": 3 * k,
                         "single_run_inning_rate": 2 / 18, "big_inning_rate": 1 / 18})
    out = inning_decomposition(st, pl.DataFrame(base, schema_overrides={"season": pl.Int32}))
    d = out.filter(pl.col("team") == "d").row(0, named=True)
    assert d["inn_single_share"] == pytest.approx(2 / 3) and d["inn_big_share"] == pytest.approx(1 / 3)
    assert d["inn_d_single_share"] == pytest.approx(0.0)              # 3球団とも同じ割合
    assert d["inn_dlog_size_home"] == pytest.approx(d["inn_dlog_size"])  # 半分ずつなので同じ
    broken = pl.DataFrame(base, schema_overrides={"season": pl.Int32}).with_columns(
        runs=pl.when(pl.col("venue") == "home").then(pl.col("runs") + 1).otherwise(pl.col("runs")))
    with pytest.raises(ValueError, match="ホーム＋ビジター"):
        inning_decomposition(st, broken)


def _batting(st, **over):
    rows = []
    for r in st.iter_rows(named=True):
        h, ab, bb, hbp, sf, tb = 30, 100, 10, 2, 1, 45
        if r["team"] == "d":
            tb = 39
        rows.append({"season": r["season"], "team": r["team"], "g": r["G"], "r": r["RF"], "pa": 115, "ab": ab, "h": h,
                     "b2": 5, "b3": 1, "hr": 3 if r["team"] == "d" else 4, "tb": tb, "bb": bb, "hbp": hbp, "sf": sf, "so": 20,
                     "ibb": 1 if r["team"] == "d" else 2,
                     "avg": round(h / ab, 3), "slg": round(tb / ab, 3),
                     "obp": round((h + bb + hbp) / (ab + bb + hbp + sf), 3), **over})
    return pl.DataFrame(rows)


def test_batting_join_rates_relative_and_no_raw_counts():
    from sakanalytics import batting_join
    rows = [("2024-04-01", "d", "g", 2, 6), ("2024-04-02", "g", "t", 4, 3), ("2024-04-03", "t", "d", 5, 1)]
    st = season_table(to_team_games(games(rows), TEAMS))
    out = batting_join(st, _batting(st))
    d = out.filter(pl.col("team") == "d").row(0, named=True)
    assert d["bat_iso"] == pytest.approx(0.39 - 0.30) and d["bat_d_iso"] == pytest.approx(0.09 - 0.15)
    assert d["bat_obp"] == pytest.approx(42 / 113) and d["bat_d_obp"] == pytest.approx(0.0)
    assert d["bat_walk_share"] == pytest.approx(12 / 42) and d["bat_ibb_bb"] == pytest.approx(0.1)
    assert d["bat_d_ibb_bb"] == pytest.approx(0.1 - 0.2)
    assert d["bat_r_runner"] == pytest.approx(d["RF"] / 42) and d["bat_r_pa"] == pytest.approx(d["RF"] / 115)
    assert not {"hr", "ab", "tb", "h", "bb", "ibb"} & set(out.columns)  # 原票の値は出力に入れない


@pytest.mark.parametrize("over,msg", [({"r": 999}, "得点"), ({"obp": 0.5}, "obp")])
def test_batting_join_stops_when_page_disagrees_with_our_numbers(over, msg):
    from sakanalytics import batting_join
    rows = [("2024-04-01", "d", "g", 2, 6), ("2024-04-02", "g", "t", 4, 3)]
    st = season_table(to_team_games(games(rows), TEAMS))
    with pytest.raises(ValueError, match=msg):
        batting_join(st, _batting(st, **over))


def test_equal_width_band_k67_is_part_of_ceiling_and_not_added_to_total():
    rows = [("2024-04-01", "d", "g", 0, 2), ("2024-04-02", "g", "d", 2, 7),
            ("2024-04-03", "t", "g", 4, 1), ("2024-04-04", "g", "t", 1, 4)]
    v = {r["team"]: r for r in season_table(to_team_games(games(rows), TEAMS)).iter_rows(named=True)}
    # d: P(≥6)=P(≥7)=.5、他の2球団は 0 → k=6,7 の差は .5 × 2。床（k=1,2）は (−.5) + (−.25)
    assert v["d"]["rf_def_k67"] == pytest.approx(1.0)
    assert v["d"]["rf_def_floor_minus_k67"] == pytest.approx(-0.75 - 1.0)
    assert v["d"]["rf_def_floor"] + v["d"]["rf_def_mid"] + v["d"]["rf_def_ceiling"] == pytest.approx(v["d"]["rf_def_total"])


def _tg(teams):
    """teams: {team: (rf の並び, ra の並び)}。同じ年・同じリーグ"""
    return pl.DataFrame([{"season": 2024, "team": t, "league": "C", "rf": a, "ra": b}
                         for t, (rf, ra) in teams.items() for a, b in zip(rf, ra)],
                        schema_overrides={"season": pl.Int32})


def test_rank_probability_matches_a_seeded_random_simulation():
    # 乱数でシーズンを何度も作り直した割合と、厳密な計算が一致する（4チーム・8試合、上位半分 = 2位以内）
    import random
    from sakanalytics import rank_probability
    teams = {"a": ([5, 1, 3, 0, 4, 2, 6, 2], [2, 3, 1, 4, 0, 2, 5, 3]), "b": ([2, 2, 3, 1, 0, 4, 2, 1], [3, 1, 2, 2, 4, 0, 1, 2]),
             "c": ([7, 0, 1, 3, 2, 2, 5, 0], [1, 6, 2, 3, 3, 0, 4, 2]), "d": ([1, 0, 2, 1, 3, 0, 1, 2], [2, 4, 1, 3, 2, 5, 1, 0])}
    exact = {r["team"]: r["sim_p_upper"] for r in rank_probability(_tg(teams)).iter_rows(named=True)}
    rnd, n, hits = random.Random(20261004), 40000, dict.fromkeys(teams, 0)
    for _ in range(n):
        wp = {}
        for t, (rf, ra) in teams.items():
            w = l_ = 0
            for _ in range(len(rf)):
                x, y = rnd.choice(rf), rnd.choice(ra)
                w, l_ = w + (x > y), l_ + (x < y)
            wp[t] = w / (w + l_) if w + l_ else None
        for t, v in wp.items():
            if v is None:
                continue
            above = sum(1 for o, ov in wp.items() if o != t and ov is not None and ov > v)
            hits[t] += above <= 1
    for t in teams:
        assert exact[t] == pytest.approx(hits[t] / n, abs=0.012), t


def test_rank_probability_identical_teams_and_dominant_team():
    from sakanalytics import rank_probability
    same = ([3, 1, 4, 1, 5, 2], [2, 7, 1, 8, 2, 8])
    p = {r["team"]: r["sim_p_upper"] for r in rank_probability(_tg({t: same for t in "dgt"})).iter_rows(named=True)}
    assert p["d"] == pytest.approx(p["g"]) == pytest.approx(p["t"])
    strong = ([9] * 6, [0] * 6)
    weak = ([0, 1, 0, 1, 0, 1], [3, 4, 3, 4, 3, 4])
    p = {r["team"]: r["sim_p_upper"] for r in rank_probability(_tg({"d": strong, "g": weak, "t": weak})).iter_rows(named=True)}
    assert p["d"] == pytest.approx(1.0) and p["g"] < 0.01


def test_streaks_ties_break_both():
    from sakanalytics import _streaks
    assert _streaks([1, 1, -1, -1, -1, 0, -1, 1, 1, 1, 1]) == (4, 3)
    assert _streaks([]) == (0, 0)


def test_boundary_features_by_hand():
    from sakanalytics import boundary_features
    teams = {**TEAMS, "c": {"name": "広島", "league": "C"}}
    # 4球団（セ）+ 交流戦1試合。d は c に2勝、t に1敗、g に1勝。最終順位は勝率で決まる
    rows = [("2024-04-01", "d", "c", 3, 1), ("2024-04-02", "c", "d", 0, 2), ("2024-04-03", "t", "d", 5, 1),
            ("2024-04-04", "d", "g", 4, 3), ("2024-04-05", "g", "c", 2, 1), ("2024-04-06", "t", "g", 6, 0),
            ("2024-04-07", "t", "c", 1, 0), ("2024-04-08", "h", "d", 9, 0)]
    st = season_table(to_team_games(games(rows), teams))
    rk = {r["team"]: r["rank"] for r in st.iter_rows(named=True)}
    v = {r["team"]: r for r in st.iter_rows(named=True)}
    assert rk == {"t": 1, "d": 2, "g": 3, "c": 4, "h": 1}  # d は交流戦の1敗を含めて 3勝2敗
    d = v["d"]
    assert d["vs_upper_wpct"] == pytest.approx(0.0)         # 上位半分（1・2位）の相手 = t。1敗（自分自身は除く）
    assert d["vs_lower_wpct"] == pytest.approx(1.0)         # g・c に3勝。交流戦（h）は数えない
    assert d["vs_near_net"] == 1 - 1                        # 1位 t に1敗、3位 g に1勝
    assert d["pair34_net"] is None and v["g"]["pair34_net"] == 1 and v["c"]["pair34_net"] == -1
    assert (d["max_win_streak"], d["max_lose_streak"]) == (2, 1)
    # 前半（最初の2試合）は2勝、期待勝利数は 2 × ピタゴラス(5, 1)
    assert d["half1_vs_pythag"] == pytest.approx(2 - 2 / (1 + (1 / 5) ** K_FIXED))


def test_battle_top_focus_and_pair_diffs_by_hand():
    teams = {k: {"name": k.upper(), "league": "C"} for k in ("a", "b", "c", "d", "e", "f")}
    # 上の文字の球団が下の文字の球団に1試合ずつ全勝。追加で c が a に1勝。
    # 成績: a 5-1, b 4-1, c 4-2, d 2-3, e 1-4, f 0-5 → 順位 a b c d e f
    pairs = [(x, y) for i, x in enumerate("abcdef") for y in "abcdef"[i + 1:]]
    rows = [(f"2024-04-{n + 1:02d}", x, y, 3, 1) for n, (x, y) in enumerate(pairs)] + [("2024-05-01", "c", "a", 2, 0)]
    v = {r["team"]: r for r in season_table(to_team_games(games(rows), teams)).iter_rows(named=True)}
    assert [v[t]["rank"] for t in "abcdef"] == [1, 2, 3, 4, 5, 6]
    c, d = v["c"], v["d"]
    # c（3位）: 上の相手（1・2位）に 1勝2敗、争う相手（3〜5位、自分を除く = d・e）に 2勝0敗
    assert (c["vs_top_wpct"], c["vs_battle_wpct"], c["focus_gap"]) == pytest.approx((1 / 3, 1.0, 2 / 3))
    # d（4位）: 上の相手に 0勝2敗、争う相手（c・e）に 1勝1敗
    assert (d["vs_top_wpct"], d["vs_battle_wpct"], d["focus_gap"]) == pytest.approx((0.0, 0.5, 0.5))
    assert c["pair34_vs_battle_wpct_diff"] == pytest.approx(0.5) and d["pair34_vs_battle_wpct_diff"] == pytest.approx(-0.5)
    assert c["pair34_focus_gap_diff"] == pytest.approx(2 / 3 - 0.5)
    assert c["pair34_vs_lower_wpct_diff"] == pytest.approx(0.0)  # 下位半分（4〜6位）の相手: c は d・e・f、d は e・f にどちらも全勝
    assert v["a"]["pair34_focus_gap_diff"] is None and v["e"]["pair34_vs_lower_wpct_diff"] is None


def test_streak_counts_consecutive_seasons_and_resets():
    from sakanalytics import streak
    st = pl.DataFrame({"team": ["d"] * 6 + ["g"] * 2, "season": [2013, 2014, 2015, 2017, 2018, 2019, 2013, 2014],
                       "x": [1, 1, 0, 1, 1, None, 1, 1]})
    out = streak(st, pl.col("x") == 1, "s").sort("team", "season")
    # 2016 がない → 2017 は数え直し。値が空なら空。チームごとに別々に数える
    assert out["s"].to_list() == [1, 2, 0, 1, 2, None, 1, 2]


def test_log5_properties():
    from sakanalytics import log5
    assert log5(0.5, 0.5) == pytest.approx(0.5)
    assert log5(0.6, 0.5) == pytest.approx(0.6)          # .500 の相手には自分の勝率どおり
    assert log5(0.6, 0.4) + log5(0.4, 0.6) == pytest.approx(1.0)
    assert log5(0.6, 0.4) == pytest.approx(0.6 * 0.6 / (0.6 * 0.6 + 0.4 * 0.4))


def test_opponent_adjusted_by_hand_and_excludes_own_games():
    from sakanalytics import K_FIXED, log5, opponent_adjusted
    rows = [("2024-04-01", "d", "g", 3, 1), ("2024-04-02", "g", "d", 2, 1), ("2024-04-03", "d", "t", 1, 4),
            ("2024-04-04", "g", "t", 5, 5), ("2024-04-05", "t", "g", 0, 2), ("2024-04-06", "h", "d", 9, 0)]
    tg = to_team_games(games(rows), TEAMS)
    st = season_table(tg)
    v = {r["team"]: r for r in opponent_adjusted(tg, st).iter_rows(named=True)}
    py = lambda rf, ra: 1 / (1 + (ra / rf) ** K_FIXED)  # noqa: E731
    # d 対 g: d の強さは g 戦を除く（t 戦 1-4、h 戦 0-9 → 1-13）。g の強さは d 戦を除く（t 戦 5-5、2-0 → 7-5）
    exp_g = 2 * log5(py(1, 13), py(7, 5))
    # d 対 t: d は t 戦を除く（g 戦 3-1, 1-2、h 戦 0-9 → 4-12）。t は d 戦を除く（g 戦 5-5, 0-2 → 5-7）
    exp_t = 1 * log5(py(4, 12), py(5, 7))
    assert v["d"]["opp_adj_total"] == pytest.approx((1 - exp_g) + (0 - exp_t))
    # 3球団なので相手は2チーム → どちらも「強いほうの2チーム」に入る
    assert v["d"]["opp_adj_top"] == pytest.approx(v["d"]["opp_adj_total"]) and v["d"]["opp_adj_mid"] is None
    assert v["h"]["opp_adj_total"] is None  # リーグ内の相手がいない（交流戦は数えない）


def test_opponent_run_gaps_by_hand():
    from sakanalytics import K_FIXED, opponent_adjusted
    rows = [("2024-04-01", "d", "g", 3, 1), ("2024-04-02", "g", "d", 2, 1), ("2024-04-03", "d", "t", 1, 4),
            ("2024-04-04", "g", "t", 5, 5), ("2024-04-05", "t", "g", 0, 2), ("2024-04-06", "h", "d", 9, 0)]
    tg = to_team_games(games(rows), TEAMS)
    v = {r["team"]: r for r in opponent_adjusted(tg, season_table(tg)).iter_rows(named=True)}
    lg = (5 + 10 + 9) / (4 + 4 + 3)  # セの3球団の得点 ÷ 試合数（交流戦も含む）
    # d 対 g（2試合、得点 4・失点 3）: d は g 戦を除いて 2試合で得点 1・失点 13、g は d 戦を除いて 2試合で得点 7・失点 5
    rf_g, ra_g = 4 - 2 * (1 / 2) * (5 / 2) / lg, 2 * (7 / 2) * (13 / 2) / lg - 3
    # d 対 t（1試合、得点 1・失点 4）: d は t 戦を除いて 3試合で得点 4・失点 12、t は d 戦を除いて 2試合で得点 5・失点 7
    rf_t, ra_t = 1 - 1 * (4 / 3) * (7 / 2) / lg, 1 * (5 / 2) * (12 / 3) / lg - 4
    d = v["d"]
    assert d["opp_rf_gap_top"] == pytest.approx(rf_g + rf_t) and d["opp_ra_gap_top"] == pytest.approx(ra_g + ra_t)
    assert d["opp_top_rf_minus_ra"] == pytest.approx((rf_g + rf_t) - (ra_g + ra_t))
    py = lambda r, a: 1 / (1 + (a / r) ** K_FIXED)  # noqa: E731
    assert d["opp_conv_top"] == pytest.approx((1 - 2 * py(4, 3)) + (0 - 1 * py(1, 4)))
    assert d["opp_rf_gap_mid"] is None and v["h"]["opp_rf_gap_top"] is None


def test_centered_run_gaps_average_zero_within_league_season():
    from sakanalytics import opponent_adjusted
    rows = [("2024-04-01", "d", "g", 3, 1), ("2024-04-02", "g", "d", 2, 1), ("2024-04-03", "d", "t", 1, 4),
            ("2024-04-04", "g", "t", 5, 5), ("2024-04-05", "t", "g", 0, 2), ("2024-04-06", "t", "d", 3, 2)]
    tg = to_team_games(games(rows), TEAMS)
    out = opponent_adjusted(tg, season_table(tg)).filter(pl.col("team").is_in(["d", "g", "t"]))
    for c in ("opp_rf_gap_top", "opp_ra_gap_top"):
        assert out.select(pl.col(f"{c}_c").sum()).item() == pytest.approx(0.0, abs=1e-9)
        v = out.select(c, f"{c}_c").rows()
        mean = sum(a for a, _ in v) / len(v)
        assert all(b == pytest.approx(a - mean) for a, b in v)


def test_net_and_env_are_a_rotation_of_scoring_and_prevention_gaps():
    from sakanalytics import opponent_adjusted
    rows = [("2024-04-01", "d", "g", 3, 1), ("2024-04-02", "g", "d", 2, 1), ("2024-04-03", "d", "t", 1, 4),
            ("2024-04-04", "g", "t", 5, 5), ("2024-04-05", "t", "g", 0, 2), ("2024-04-06", "t", "d", 3, 2)]
    tg = to_team_games(games(rows), TEAMS)
    for r in opponent_adjusted(tg, season_table(tg)).filter(pl.col("team").is_in(["d", "g", "t"])).iter_rows(named=True):
        rf, ra = r["opp_rf_gap_top_c"], r["opp_ra_gap_top_c"]
        assert r["opp_net_gap_top_c"] == pytest.approx(rf + ra) and r["opp_env_gap_top_c"] == pytest.approx(rf - ra)
        # 元に戻せる（回しただけで情報は増えも減りもしない）
        assert (r["opp_net_gap_top_c"] + r["opp_env_gap_top_c"]) / 2 == pytest.approx(rf)


def test_win_loss_split_by_hand():
    from sakanalytics import win_loss_split
    # 中日のホーム4試合: (1,0) 勝 (5,4) 勝 (0,3) 負 (2,6) 負。合計得点 1, 9, 3, 8 → 中央値 5.5
    tg = to_team_games(games([("2024-04-01", "d", "g", 1, 0), ("2024-04-02", "d", "g", 5, 4),
                              ("2024-04-03", "d", "g", 0, 3), ("2024-04-04", "d", "g", 2, 6)]), TEAMS)
    d = win_loss_split(tg).filter(pl.col("team") == "d").row(0, named=True)
    # 得点 {1,5,0,2} と失点 {0,4,3,6} の16通りの組: 勝ち5組（得点の和 1 + 5×3 + 2 = 18）、負け10組（和 1×3 + 5 + 0 + 2×3 = 14）、引き分け1組
    assert (d["wl_rf_win"], d["wl_rf_win_exp"], d["wl_rf_win_gap"]) == pytest.approx((3.0, 18 / 5, 3.0 - 18 / 5))
    assert (d["wl_rf_loss"], d["wl_rf_loss_exp"], d["wl_rf_loss_gap"]) == pytest.approx((1.0, 14 / 10, 1.0 - 14 / 10))
    # 合計 5.5 以下の組: 勝ち3・負け5（引き分け1を除く）、より多い組: 勝ち2・負け5。実際は低い側・高い側とも1勝1敗
    assert (d["wl_wpct_low"], d["wl_wpct_low_exp"]) == pytest.approx((0.5, 3 / 8))
    assert (d["wl_wpct_high"], d["wl_wpct_high_exp"], d["wl_wpct_high_gap"]) == pytest.approx((0.5, 2 / 7, 0.5 - 2 / 7))


def test_win_loss_split_pairs_runs_within_home_and_away_only():
    from sakanalytics import win_loss_split
    # ホームは点が入りにくく（1-0, 0-1）、ビジターは入りやすい（6-5, 5-6）。
    # ホームとビジターを混ぜて組み合わせると、勝ちの見込みの得点は 29/6 ≈ 4.83 になり、球場の違いが差に出てしまう
    tg = to_team_games(games([("2024-04-01", "d", "g", 1, 0), ("2024-04-02", "d", "g", 0, 1),
                              ("2024-04-03", "g", "d", 5, 6), ("2024-04-04", "g", "d", 6, 5)]), TEAMS)
    d = win_loss_split(tg).filter(pl.col("team") == "d").row(0, named=True)
    assert (d["wl_rf_win"], d["wl_rf_win_exp"], d["wl_rf_win_gap"]) == pytest.approx((3.5, 3.5, 0.0))


def test_season_course_by_hand():
    st = season_table(to_team_games(games([("2024-04-01", "d", "g", 3, 2), ("2024-04-02", "d", "g", 5, 1),
                                           ("2024-04-03", "d", "g", 1, 4), ("2024-04-04", "d", "g", 0, 2)]), TEAMS))
    v = {r["team"]: r for r in st.iter_rows(named=True)}
    d, g = v["d"], v["g"]
    assert (d["course_wpct_h1"], d["course_wpct_h2"], d["course_wpct_diff"]) == pytest.approx((1.0, 0.0, -1.0))
    assert (d["course_rank_h1"], g["course_rank_h1"]) == (1, 2)
    assert (d["course_rank_q1"], d["course_rank_q3"], g["course_rank_q3"]) == (1, 1, 2)  # 1試合目まで 1-0、3試合目まで 2-1
    assert (d["rank"], g["rank"], d["course_fade"], g["course_fade"]) == (1, 1, 0, -1)  # 2勝2敗どうしで同率1位
    # 得点／試合: d は前半 4 → 後半 0.5（−3.5）、g は 1.5 → 3（+1.5）。失点はその裏返し
    assert (d["course_rf_d"], d["course_ra_d"]) == pytest.approx((-5.0, 5.0))
    assert d["course_ra_h1_d"] == pytest.approx(1.5 - 4.0)     # 前半の失点／試合: d は (2+1)/2、g は (3+5)/2
    assert d["course_close_win_h1"] == pytest.approx(0.5)     # 前半の勝ち 1点差・4点差のうち2点差以内は1つ
    assert g["course_close_win_h1"] is None                    # 前半に勝ちがない
    assert d["course_close_win_h1_d"] is None                  # 比べる他球団の値がない（0 で割らない）


def test_cubic_fit_recovers_the_curve_and_its_peak_and_valley():
    from sakanalytics import cubic_extrema, cubic_projection
    xs = [i / 100 for i in range(101)]
    ys = [2 + 0.6 * x - 1.5 * x * x + x ** 3 for x in xs]     # f'(x) = 3x² − 3x + 0.6 → x = 0.276（山）, 0.724（谷）
    c = [sum(p * y for p, y in zip(row, ys)) for row in cubic_projection(xs)]
    assert c == pytest.approx([2, 0.6, -1.5, 1], abs=1e-9)
    (x1, k1), (x2, k2) = cubic_extrema(c, 0.0)
    assert (k1, k2) == ("peak", "valley")
    assert (x1, x2) == pytest.approx(((3 - math.sqrt(1.8)) / 6, (3 + math.sqrt(1.8)) / 6))
    assert cubic_extrema(c, 0.5) == [(pytest.approx(x2), "valley")]   # 線を引く範囲の外の山は数えない


def test_season_trajectory_finds_a_peak_in_the_wins_minus_losses_line():
    from sakanalytics import season_trajectory
    # d と g の2球団だけのリーグで1日1試合。d は最初の15試合に勝ち、後の15試合に負ける（貯金 +15 から 0 へ）
    rows = [(f"2024-04-{i + 1:02d}", "d", "g", 3, 1) if i < 15 else (f"2024-04-{i + 1:02d}", "d", "g", 1, 3) for i in range(30)]
    tg = to_team_games(games(rows), TEAMS)
    out = {r["team"]: r for r in season_trajectory(tg, sims=20).iter_rows(named=True)}
    d, g = out["d"], out["g"]
    # 線は両球団が10試合に届いた日（10日目、x = 9/29）から。貯金は 10日目の +10 から 15日目の +15 まで上がり、最後に 0
    assert d["traj_wl_peak"] and 0.4 < d["traj_wl_peak_x"] < 0.6 and "peak" in d["traj_wl_shape"]
    assert g["traj_wl_valley"] and not g["traj_wl_peak"]
    assert d["traj_wl_end_slope"] < 0
    assert d["traj_rank_shape"] == "flat"           # d は最後まで勝率5割以上で、順位は1位のまま（最後の日は同率1位）
    assert 0 <= d["traj_wl_peak_base"] <= 1 and d["traj_wl_peak_base"] == season_trajectory(tg, sims=20).filter(
        pl.col("team") == "d")["traj_wl_peak_base"][0]  # 乱数の種は年で固定
    assert season_trajectory(tg.filter(pl.col("date") <= "2024-04-05"), sims=5).height == 0  # 10試合に届かなければ線を引かない


def _damped(xs, h0, lim, lam, per, b):
    w = 2 * math.pi / per if per else 0.0
    return [lim + math.exp(-lam * (x - xs[0])) * ((h0 - lim) * math.cos(w * (x - xs[0])) + b * math.sin(w * (x - xs[0])))
            for x in xs]


def test_wave_fit_recovers_a_damped_wave_from_its_starting_value():
    from sakanalytics import wave_basis, wave_fit
    xs = [0.1 + 0.9 * i / 150 for i in range(151)]
    ys = _damped(xs, h0=5.0, lim=2.0, lam=3.0, per=0.5, b=1.0)   # 始まりは 5、収束する先は 2
    f = wave_fit(ys, wave_basis(xs), xs[0])
    assert (f["decay"], f["period"]) == (3.0, 0.5) and f["rmse"] == pytest.approx(0.0, abs=1e-9)
    assert f["limit"] == pytest.approx(2.0) and f["end"] == pytest.approx(ys[-1])
    # ゆれの幅 e^(−3t)·√(3² + 1²) が 0.5 を下回る位置
    assert f["settle_x"] == pytest.approx(0.1 + math.log(math.hypot(3, 1) / 0.5) / 3)


def test_wave_fit_reports_no_limit_for_an_undamped_wave_and_no_period_for_a_plain_approach():
    from sakanalytics import wave_basis, wave_fit
    xs = [0.1 + 0.9 * i / 150 for i in range(151)]
    basis = wave_basis(xs)
    f = wave_fit(_damped(xs, h0=3.0, lim=3.0, lam=0.0, per=0.5, b=2.0), basis, xs[0])
    assert (f["decay"], f["period"], f["limit"], f["settle_x"]) == (0.0, 0.5, None, None)   # 減衰しない波は決まらない
    g = wave_fit(_damped(xs, h0=1.0, lim=4.0, lam=5.0, per=None, b=0.0), basis, xs[0])
    assert (g["decay"], g["period"]) == (5.0, None) and g["limit"] == pytest.approx(4.0)


def test_season_trajectory_start_is_configurable_and_recorded():
    from sakanalytics import season_trajectory
    rows = [(f"2024-04-{i + 1:02d}", "d", "g", 3, 1) if i < 15 else (f"2024-04-{i + 1:02d}", "d", "g", 1, 3) for i in range(30)]
    tg = to_team_games(games(rows), TEAMS)
    a = season_trajectory(tg, sims=5, min_games=10).filter(pl.col("team") == "d").row(0, named=True)
    b = season_trajectory(tg, sims=5, min_games=5).filter(pl.col("team") == "d").row(0, named=True)
    assert (a["traj_start_games"], a["traj_start_date"], a["traj_start_x"]) == (10, "2024-04-10", pytest.approx(9 / 29))
    assert (b["traj_start_games"], b["traj_start_date"], b["traj_start_x"]) == (5, "2024-04-05", pytest.approx(4 / 29))
    # d は線を引く間ずっと1位（最後の日は同率1位）。動かない線は、いちばん簡単な「波なしで近づく」式で、収束する先も1位
    assert (a["wave_limit_rank"], a["wave_end_rank"], a["wave_period"]) == (pytest.approx(1.0), pytest.approx(1.0), None)
    assert a["wave_settle_x"] == pytest.approx(a["traj_start_x"]) and 0 <= a["wave_settle_pct"] <= 1
    assert a["wave_limit_rank_h1"] == pytest.approx(1.0)   # 前半（横軸 0.5 まで）だけから当てても1位に向かう


def test_series_split_by_opponent_venue_and_a_gap_of_three_days():
    from sakanalytics import _series_of
    gs = [(1, 0, "g", True), (3, 1, "g", True),   # 中1日（雨天中止など）は同じカード
          (6, 2, "g", True),                      # 3日あいたら別のカード
          (7, 3, "g", False),                     # 球場が変わったら別のカード
          (8, 4, "t", False)]                     # 相手が変わったら別のカード
    assert _series_of(gs) == [[0, 1], [2], [3], [4]]


def test_series_features_by_hand():
    from sakanalytics import series_features
    rows = [("2024-04-02", "d", "g", 3, 1), ("2024-04-03", "d", "g", 1, 2), ("2024-04-04", "d", "g", 4, 0),   # 2勝1敗
            ("2024-04-05", "g", "d", 5, 1), ("2024-04-06", "g", "d", 2, 0), ("2024-04-07", "g", "d", 3, 2),   # 0勝3敗
            ("2024-04-09", "d", "t", 2, 1), ("2024-04-10", "d", "t", 2, 2),                                    # 1勝1分
            ("2024-04-20", "d", "g", 6, 0), ("2024-04-21", "d", "g", 3, 1), ("2024-04-22", "d", "g", 0, 1)]   # 2勝1敗
    d = series_features(to_team_games(games(rows), TEAMS), sims=20).filter(pl.col("team") == "d").row(0, named=True)
    # 勝敗のついた試合が2つ以上のカードは3つ（t との2連戦は1勝1分で数えない）。負け越しは g との 0勝3敗の1つ
    assert (d["series_n"], d["series_lost"], d["series_lost_share"]) == (3, 1, pytest.approx(1 / 3))
    assert [d[f"series3_w{k}"] for k in range(4)] == [1, 0, 2, 0]
    # 1試合目 4つで3勝、2試合目以降（引き分けを除く）6つで2勝
    assert d["series_g1_minus_rest"] == pytest.approx(3 / 4 - 2 / 6)
    # 勝率: d 5勝5敗（.500）、g 5勝4敗。g との試合に勝つ見込み Log5(.5, 5/9) = 4/9。見込み 3 × 4/9、分散 3 × 4/9 × 5/9
    e, v = 3 * 4 / 9, 3 * 4 / 9 * 5 / 9
    assert d["series_disp"] == pytest.approx(((2 - e) ** 2 * 2 + (0 - e) ** 2) / (3 * v))
    b = [(5 / 9) ** 3, 3 * 4 / 9 * (5 / 9) ** 2, 3 * (4 / 9) ** 2 * 5 / 9, (4 / 9) ** 3]
    assert [d[f"series3_w{k}_exp"] for k in range(4)] == pytest.approx([3 * x for x in b])
    assert 0 <= d["series_lost_pct"] <= 1 and 0 <= d["series_disp_pct"] <= 1


def _four_team_season():
    teams = {**TEAMS, "c": {"name": "広島", "league": "C"}}
    # 4球団（上位半分 = 2位以内）。毎日2試合、6日で各球団6試合。g と t は互いの試合以外ほぼ全勝、d は全敗、c は d にだけ勝つ
    winners = [("g", "d", "t", "c"), ("t", "d", "g", "c"), ("c", "d", "g", "t"),
               ("g", "d", "t", "c"), ("t", "d", "g", "c"), ("c", "d", "t", "g")]
    rows = []
    for i, (w1, l1, w2, l2) in enumerate(winners):
        rows += [(f"2024-04-{i + 1:02d}", w1, l1, 3, 1), (f"2024-04-{i + 1:02d}", w2, l2, 2, 0)]
    return to_team_games(games(rows), teams)


def test_clinch_dates_by_hand():
    from sakanalytics import clinch_dates
    v = {r["team"]: r for r in clinch_dates(_four_team_season()).iter_rows(named=True)}
    # d: 4日目の終わり 0勝4敗・残り2 → 上限 2/6。g の下限 4/6、t の下限 3/6 がどちらも上 → 2位以内に入れない（x = 3/5）
    assert (v["d"]["clinch_out_x"], v["d"]["clinch_out_left"], v["d"]["clinch_in_x"]) == (pytest.approx(0.6), 2, None)
    # c: 5日目の終わり 1勝4敗・残り1 → 上限 2/6。g の下限 5/6、t の下限 4/6 → 入れない（x = 4/5）
    assert (v["c"]["clinch_out_x"], v["c"]["clinch_out_left"]) == (pytest.approx(0.8), 1)
    # g: 4日目の終わり 4勝0敗・残り2 → 下限 4/6。d の上限 2/6、c の上限 3/5 がどちらも下 → 入る。t は5日目
    assert (v["g"]["clinch_in_x"], v["g"]["clinch_in_left"], v["t"]["clinch_in_x"]) == (pytest.approx(0.6), 2, pytest.approx(0.8))
    assert [r["decided_x"] for r in v.values()] == pytest.approx([0.8] * 4)   # 4球団すべて決まったのは5日目



def test_rank_fixed_and_live_dead_split_by_hand():
    """R57: 最終順位が確かになった日と、A・B が決まる前（効く試合）・後（効かない試合）の分け方。"""
    from sakanalytics import clinch_dates
    v = {r["team"]: r for r in clinch_dates(_four_team_season()).iter_rows(named=True)}
    # 最終: g 5勝1敗、t 5勝1敗（同率）、c 2勝4敗、d 0勝6敗。d・c は最終日に4位・3位が確定。g・t は同率なので決まらない
    assert (v["d"]["rank_fixed_x"], v["d"]["rank_fixed_left"], v["d"]["rank_fixed"]) == (pytest.approx(1.0), 0, 4)
    assert (v["c"]["rank_fixed_x"], v["c"]["rank_fixed"]) == (pytest.approx(1.0), 3)
    assert v["g"]["rank_fixed"] is None and v["t"]["rank_fixed_x"] is None
    # g: 4日目に入るのが確定 → 1〜4日目が効く試合（4勝0敗、点の差 +2 ×4）、5・6日目が効かない試合（1勝1敗、+2 と −2）
    g = v["g"]
    assert (g["live_g"], g["live_wpct"], g["live_rd_g"]) == (4, pytest.approx(1.0), pytest.approx(2.0))
    assert (g["dead_g"], g["dead_wpct"], g["dead_rd_g"]) == (2, pytest.approx(0.5), pytest.approx(0.0))
    # t: 5日目に確定 → 4勝1敗（3日目に g に 0−2）、効かない試合は6日目の1つ
    t = v["t"]
    assert (t["live_g"], t["live_wpct"], t["live_rd_g"]) == (5, pytest.approx(0.8), pytest.approx(1.2))
    assert (t["dead_g"], t["dead_wpct"]) == (1, pytest.approx(1.0))
    # 効く試合 + 効かない試合 = 全試合
    assert all(r["live_g"] + r["dead_g"] == 6 for r in v.values())
    # 後半（4〜6試合目）のうち効く試合: g は4日目に確定 → 4試合目だけ（勝ち）。t は5日目 → 4・5試合目（勝ち・勝ち）
    assert (g["h2_live_g"], g["h2_live_wpct"]) == (1, pytest.approx(1.0))
    assert (t["h2_live_g"], t["h2_live_wpct"]) == (2, pytest.approx(1.0))
    # 最終の上位半分は g・t（5勝1敗で同率、どちらも上位側）。g の前半（1〜3日目）: d に勝ち(+2)・c に勝ち(+2)・t に勝ち(+2)
    assert (g["h1_rd_g"], g["h1_wl_vs_upper"], g["h1_wl_vs_lower"]) == (pytest.approx(2.0), 1, 2)
    # g の後半の効く試合は4日目の d 戦だけ（3−1）
    assert (g["h2_live_rd_g"], g["h2_live_wl_vs_upper"], g["h2_live_wl_vs_lower"]) == (pytest.approx(2.0), 0, 1)
    # d の前半: g・t・c に3連敗（−2, −2, −2）。上位 2敗、下位 1敗
    assert (v["d"]["h1_wl_vs_upper"], v["d"]["h1_wl_vs_lower"]) == (-2, -1)


def test_live_dead_when_never_decided():
    from sakanalytics import clinch_dates
    teams = {**TEAMS, "c": {"name": "広島", "league": "C"}}
    # 4球団で1日だけ。誰も確定しない → すべて効く試合、効かない試合は 0
    tg = to_team_games(games([("2024-04-01", "g", "d", 3, 1), ("2024-04-01", "t", "c", 2, 0)]), teams)
    v = {r["team"]: r for r in clinch_dates(tg).iter_rows(named=True)}
    assert all(r["dead_g"] == 0 and r["dead_wpct"] is None and r["live_g"] == 1 for r in v.values())

def test_season_trajectory_can_stop_when_the_top_half_is_decided():
    from sakanalytics import season_trajectory
    tg = _four_team_season()
    full = season_trajectory(tg, sims=5, min_games=1).filter(pl.col("team") == "g").row(0, named=True)
    cut = season_trajectory(tg, sims=5, min_games=1, end="decided").filter(pl.col("team") == "g").row(0, named=True)
    assert (full["traj_end"], full["traj_end_x"]) == ("season", pytest.approx(1.0))
    assert (cut["traj_end"], cut["traj_end_x"]) == ("decided", pytest.approx(0.8))   # 顔ぶれが決まった5日目まで
    # g は4日目（x = 0.6）に入るのが確定。その後の山かどうかと、力が一定のときの割合が出る
    assert full["traj_wl_peak_after_clinch"] is not None and 0 <= full["traj_wl_peak_after_clinch_base"] <= 1
    d = season_trajectory(tg, sims=5, min_games=1).filter(pl.col("team") == "d").row(0, named=True)
    assert d["traj_wl_peak_after_clinch"] is None                                   # 入らなかった球団は空


# ---------- R32: 得点・失点の優位（1試合あたり） ----------

def test_add_balance_is_relative_to_the_other_teams_and_share_stays_bounded():
    import polars as pl

    import sakanalytics as sa

    # 1リーグ3球団、10試合。他2球団の平均と比べる
    st = pl.DataFrame({"season": [2000] * 3, "league": ["C"] * 3, "team": ["a", "b", "c"], "G": [10] * 3,
                       "RF": [30, 40, 50], "RA": [30, 40, 50]})
    out = {r["team"]: r for r in sa.add_balance(st).iter_rows(named=True)}
    assert out["a"]["rf_adv"] == pytest.approx(3.0 - 4.5) and out["a"]["ra_adv"] == pytest.approx(4.5 - 3.0)
    assert out["b"]["rf_adv"] == pytest.approx(0.0) and out["b"]["ra_adv"] == pytest.approx(0.0)
    assert out["a"]["run_balance"] == pytest.approx(0.0)
    # a: 不足 1.5、優位 1.5 → 取り分 0.5。c: 不足なし・優位マイナス → 空。b: 不足も優位もない → 空
    assert out["a"]["short_share"] == pytest.approx(0.5)
    assert out["c"]["short_share"] is None and out["b"]["short_share"] is None


@pytest.mark.parametrize("rf,ra,expected", [
    ([40, 50, 50], [40, 50, 50], 0.5),        # 不足 1.0、優位 1.0 → 0.5
    ([40, 50, 50], [50, 50, 50], 1.0),        # 不足 1.0、優位 0 → 1（補えなかった）
    ([40, 50, 50], [55, 50, 50], 1.0),        # 不足 1.0、優位 −0.5 → 1 で止める
    ([50, 40, 40], [40, 50, 50], 0.0),        # 不足なし、優位 1.0 → 0
    ([40, 50, 50], [45, 50, 50], 1 / 1.5),    # 不足 1.0、優位 0.5 → 0.667
])
def test_short_share_edges(rf, ra, expected):
    import polars as pl

    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 3, "league": ["C"] * 3, "team": ["a", "b", "c"], "G": [10] * 3, "RF": rf, "RA": ra})
    r = sa.add_balance(st).row(0, named=True)
    d, a = max(0.0, -r["rf_adv"]), r["ra_adv"]
    assert 0.0 <= r["short_share"] <= 1.0
    assert r["short_share"] == pytest.approx(min(1.0, d / (d + a)) if d + a > 0 else 1.0)
    assert r["short_share"] == pytest.approx(expected)


def test_add_balance_z_scales_by_the_spread_of_all_units():
    import polars as pl

    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 3 + [2001] * 3, "league": ["C"] * 6, "team": ["a", "b", "c"] * 2,
                       "G": [10] * 6, "RF": [30, 40, 50, 35, 40, 45], "RA": [50, 40, 30, 40, 40, 40]})
    out = sa.add_balance(st)
    sd = out["ra_adv"].std()
    assert out["ra_adv_z"].to_list() == pytest.approx([x / sd for x in out["ra_adv"].to_list()])
    assert out["rf_adv_z"].std() == pytest.approx(1.0)
    for z, zone in zip(out["ra_adv_z"].to_list(), out["ra_zone"].to_list()):
        assert zone == (1 if z >= 1 else -1 if z <= -1 else 0)


def test_add_balance_standard_error_combines_own_and_others():
    import math

    import polars as pl

    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 3, "league": ["C"] * 3, "team": ["a", "b", "c"], "G": [100] * 3,
                       "RF": [300, 400, 500], "RA": [400, 400, 400],
                       "rf_sd_g": [2.0, 2.0, 2.0], "ra_sd_g": [3.0, 1.0, 1.0]})
    out = {r["team"]: r for r in sa.add_balance(st).iter_rows(named=True)}
    # 自分 4/100、他2球団の平均 (4/100 + 4/100) / 2² → 誤差 = √(0.04 + 0.02)
    assert out["a"]["rf_adv_se"] == pytest.approx(math.sqrt(0.04 + 0.02))
    # a の得点の優位 −1.5 は誤差 0.245 の6倍 → −1。b は 0 → 0
    assert out["a"]["rf_zone_se"] == -1 and out["b"]["rf_zone_se"] == 0 and out["c"]["rf_zone_se"] == 1
    # 失点: a の誤差は自分 9/100 と他 (1/100 + 1/100)/4
    assert out["a"]["ra_adv_se"] == pytest.approx(math.sqrt(0.09 + 0.005))


def test_add_balance_without_per_game_spread_skips_standard_error():
    import polars as pl

    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 3, "league": ["C"] * 3, "team": ["a", "b", "c"], "G": [10] * 3,
                       "RF": [30, 40, 50], "RA": [30, 40, 50]})
    assert "rf_zone_se" not in sa.add_balance(st).columns


def test_season_table_has_per_game_spread():
    results = [(3, 1), (5, 2), (1, 4), (7, 0)]
    st = season_table(to_team_games(games([("2024-04-01", "d", "g", rf, ra) for rf, ra in results]), TEAMS))
    d = st.filter(pl.col("team") == "d").row(0, named=True)
    rf = [r for r, _ in results]
    mean = sum(rf) / len(rf)
    assert d["rf_sd_g"] == pytest.approx(math.sqrt(sum((x - mean) ** 2 for x in rf) / (len(rf) - 1)))


# ---------- R39: 研究で使った読みを列にしたもの ----------

def test_add_composites_values_and_missing_inputs():
    import math

    import sakanalytics as sa

    st = pl.DataFrame({
        "rf_adv": [-0.6, 0.2, 0.0], "ra_adv": [0.3, -0.1, 0.0], "run_balance": [-0.3, 0.1, 0.0],
        "rf_adv_se": [0.2, 0.25, 0.3], "ra_adv_se": [0.3, 0.25, 0.3],
        "rf_zone_se": [-1, 0, None], "ra_zone_se": [1, 0, 0],
        "bat_d_bb_pa": [-0.01, 0.0, None], "bat_d_iso": [0.02, -0.01, 0.01],
        "vs_top_wpct": [0.45, 0.5, 0.4], "vs_lower_wpct": [0.48, 0.6, None],
    })
    out = sa.add_composites(st).to_dicts()
    assert out[0]["rf_adv_t"] == pytest.approx(-3.0) and out[0]["ra_adv_t"] == pytest.approx(1.0)
    assert out[0]["run_balance_t"] == pytest.approx(-0.3 / math.sqrt(0.04 + 0.09))
    assert [r["adv_shape_se"] for r in out] == ["-1/+1", "0/0", None]
    assert [r["bat_routes"] for r in out] == [1, 1, None]   # 四死球 −・長打 + → 1、四死球 0（以上）・長打 − → 1
    assert out[0]["vs_top_minus_lower"] == pytest.approx(-0.03) and out[2]["vs_top_minus_lower"] is None


def test_add_composites_skips_columns_whose_inputs_are_absent():
    import sakanalytics as sa

    st = pl.DataFrame({"rf_adv": [0.1], "ra_adv": [0.1], "run_balance": [0.2]})
    assert sa.add_composites(st).columns == st.columns


# ---------- R45: B に着く道筋の参考値 ----------

def test_add_b_paths_labels_and_nulls():
    import sakanalytics as sa

    st = pl.DataFrame({
        "rf_zone_se": [-1, 0, 0, 0, None],
        "ra_zone_se": [0, -1, 0, 0, None],
        "wins_vs_pythag": [-3.0, 0.0, 1.0, -0.5, None],
        "alloc_z_strat": [0.0, 0.0, -1.5, 0.0, None],
        "course_fade": [0, 0, 0, 3, None],
        "course_rf_d": [0.0, 0.0, 0.0, -0.3, None],
        "course_ra_d": [0.0, 0.0, 0.0, 0.4, None],
        "half2_vs_pythag": [0.0, 0.0, 0.0, -2.5, None],
    })
    out = sa.add_b_paths(st).to_dicts()
    assert [r["b_paths"] for r in out] == ["offense+convert", "defense", "convert", "collapse", None]
    assert out[1]["path_convert"] is False and out[4]["path_convert"] is None


def test_add_b_paths_none_when_no_rule_hits_and_skips_without_inputs():
    import sakanalytics as sa

    st = pl.DataFrame({"rf_zone_se": [1], "ra_zone_se": [1], "wins_vs_pythag": [0.0], "alloc_z_strat": [0.0],
                       "course_fade": [0], "course_rf_d": [0.1], "course_ra_d": [-0.1], "half2_vs_pythag": [0.0]})
    assert sa.add_b_paths(st)["b_paths"].to_list() == ["none"]
    assert sa.add_b_paths(pl.DataFrame({"x": [1]})).columns == ["x"]
    assert set(sa.B_PATHS) == {"offense", "defense", "convert", "collapse"}


# ---------- R46: リーグの順位の形 ----------

def test_add_league_shape_gaps_and_rest_spread():
    import statistics

    import sakanalytics as sa

    w = [0.65, 0.55, 0.52, 0.50, 0.45, 0.33]
    st = pl.DataFrame({"season": [2000] * 6, "league": ["C"] * 6, "team": list("abcdef"), "rank": [1, 2, 3, 4, 5, 6], "wpct": w})
    out = sa.add_league_shape(st).row(0, named=True)
    assert out["lg_lead_gap"] == pytest.approx(0.10) and out["lg_gap34"] == pytest.approx(0.02)
    assert out["lg_rest_sd"] == pytest.approx(statistics.stdev(w[1:]))
    # 同率で並んでも k 番目の勝率を使う
    tie = st.with_columns(rank=pl.Series([1, 2, 3, 3, 5, 6]), wpct=pl.Series([0.6, 0.55, 0.5, 0.5, 0.45, 0.4]))
    assert sa.add_league_shape(tie).row(0, named=True)["lg_gap34"] == pytest.approx(0.0)


def test_add_league_shape_with_few_teams_is_empty_not_an_error():
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 2, "league": ["C"] * 2, "team": ["a", "b"], "rank": [1, 2], "wpct": [0.6, 0.4]})
    out = sa.add_league_shape(st).row(0, named=True)
    assert out["lg_lead_gap"] == pytest.approx(0.2) and out["lg_gap34"] is None


def test_line_and_gap_decompose_win_pct_against_the_line():
    import sakanalytics as sa

    w = [0.65, 0.55, 0.52, 0.50, 0.45, 0.33]
    pyth = [0.60, 0.56, 0.49, 0.53, 0.46, 0.36]
    st = pl.DataFrame({"season": [2000] * 6, "league": ["C"] * 6, "team": list("abcdef"), "rank": [1, 2, 3, 4, 5, 6],
                       "wpct": w, "pythag_fixed": pyth})
    out = sa.add_league_shape(st).with_columns(resid_fixed=pl.col("wpct") - pl.col("pythag_fixed"))
    for r in out.iter_rows(named=True):
        assert r["lg_line"] == pytest.approx(0.51)
        # 勝率 − 線 = 点の差で見込む位置 + 点の差より勝った分
        assert r["wpct"] - r["lg_line"] == pytest.approx(r["line_gap_pythag"] + r["resid_fixed"])


@pytest.mark.parametrize("w,expected", [
    ([0.6, 0.52, 0.51, 0.49, 0.45, 0.43], 3.5),          # .51 と .49 のちょうど間
    ([0.6, 0.55, 0.50, 0.48, 0.45, 0.42], 3.0),          # 3位がちょうど .500
    ([0.6, 0.52, 0.48, 0.47, 0.46, 0.47], 2.5),          # 並びが乱れていても高い順に並べ直す
    ([0.6, 0.58, 0.56, 0.55, 0.53, 0.51], None),         # 全チームが .500 より上
])
def test_rank_at_500(w, expected):
    import sakanalytics as sa

    got = sa.rank_at(w, 0.5)
    assert got == (pytest.approx(expected) if expected is not None else None)


def test_league_shape_has_rank_at_500():
    import sakanalytics as sa

    w = [0.6, 0.52, 0.51, 0.49, 0.45, 0.43]
    st = pl.DataFrame({"season": [2000] * 6, "league": ["C"] * 6, "team": list("abcdef"), "rank": [1, 2, 3, 4, 5, 6], "wpct": w})
    assert sa.add_league_shape(st)["lg_rank_at_500"].to_list() == pytest.approx([3.5] * 6)


# ---------- R52: データの散らばりから引く線 ----------

def test_natural_breaks_and_tiers():
    import sakanalytics as sa

    w = [0.62, 0.60, 0.53, 0.52, 0.51, 0.40]       # 隙間: .02 .07 .01 .01 .11
    assert sa.natural_breaks(w, 1) == [5]          # 5位と6位の間
    assert sa.natural_breaks(w, 2) == [2, 5]       # 2位と3位の間、5位と6位の間
    assert [sa.tier_of(k, [2, 5]) for k in range(1, 7)] == [1, 1, 2, 2, 2, 3]
    assert sa.natural_breaks([0.6, 0.5, 0.4, 0.3], 1) == [1]   # 差が同じなら上位側


def test_league_shape_tiers_columns():
    import sakanalytics as sa

    w = [0.62, 0.60, 0.53, 0.52, 0.51, 0.40]
    st = pl.DataFrame({"season": [2000] * 6, "league": ["C"] * 6, "team": list("abcdef"), "rank": [1, 2, 3, 4, 5, 6], "wpct": w})
    out = {r["team"]: r for r in sa.add_league_shape(st).iter_rows(named=True)}
    assert out["a"]["lg_break_after"] == 5 and out["a"]["lg_break_gap"] == pytest.approx(0.11)
    assert [out[t]["lg_tier"] for t in "abcdef"] == [1, 1, 2, 2, 2, 3] and out["d"]["lg_tier_of_3rd"] == 2


# ---------- R53: A と B が混ざる帯（1年抜き） ----------

def test_mix_zone_leaves_own_season_out():
    import sakanalytics as sa

    rows = [(2000, .60, True), (2000, .49, True), (2000, .51, False), (2000, .40, False),
            (2001, .55, True), (2001, .47, False), (2001, .45, False),
            (2002, .30, True), (2002, .70, False)]          # 2002 は除外の年: 帯を引くのに使わない
    st = pl.DataFrame({"season": [r[0] for r in rows], "team": [str(i) for i in range(len(rows))],
                       "wpct": [r[1] for r in rows], "upper_half": [r[2] for r in rows]})
    out = sa.add_mix_zone(st, exclude=[2002]).sort("team")
    got = {(r["season"], r["wpct"]): r for r in out.iter_rows(named=True)}
    # 2001 の単位は 2000 だけから: A の最低 .49、B の最高 .51
    assert got[(2001, .55)]["mix_lo"] == pytest.approx(.49) and got[(2001, .55)]["mix_hi"] == pytest.approx(.51)
    assert [got[(2001, w)]["mix_zone"] for w in (.55, .47, .45)] == [1, -1, -1]
    # 2000 の単位は 2001 だけから: A の最低 .55、B の最高 .47 → 帯は開かない（lo > hi）が値はそのまま
    assert got[(2000, .49)]["mix_lo"] == pytest.approx(.55) and got[(2000, .49)]["mix_hi"] == pytest.approx(.47)
    assert got[(2000, .49)]["mix_zone"] == -1 and got[(2000, .60)]["mix_zone"] == 1
    # 除外の年の単位にも値は付く（ほかの年から引く）
    assert got[(2002, .30)]["mix_zone"] == -1


def test_mix_zone_edges_are_inside_and_missing_side_is_null():
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000, 2000, 2001], "team": ["a", "b", "c"], "wpct": [.50, .52, .50],
                       "upper_half": [True, False, True]})
    out = {r["team"]: r for r in sa.add_mix_zone(st).iter_rows(named=True)}
    assert out["c"]["mix_lo"] == pytest.approx(.50) and out["c"]["mix_zone"] == 0   # 帯の端ちょうどは中
    assert out["a"]["mix_hi"] is None and out["a"]["mix_zone"] is None              # 2001 に B がない
    assert sa.add_mix_zone(pl.DataFrame({"season": [1]})).columns == ["season"]


def test_league_bar_uses_only_the_other_teams():
    import sakanalytics as sa

    w = [0.62, 0.60, 0.53, 0.52, 0.51, 0.40]
    st = pl.DataFrame({"season": [2000] * 6, "league": ["C"] * 6, "team": list("abcdef"), "rank": [1, 2, 3, 4, 5, 6], "wpct": w})
    out = {r["team"]: r["lg_bar"] for r in sa.add_league_shape(st).iter_rows(named=True)}
    # 上位3球団（a・b・c）は、ほかの5球団の3番目 = d の .52 を越えれば入る。下位（d・e・f）は c の .53
    assert out == pytest.approx({"a": 0.52, "b": 0.52, "c": 0.52, "d": 0.53, "e": 0.53, "f": 0.53})
    assert all((wp > out[t]) == (t in "abc") for t, wp in zip("abcdef", w))



def test_mix_zone_on_another_column_with_prefix():
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000, 2000, 2001], "team": ["a", "b", "c"], "wpct": [.50, .52, .50],
                       "live_wpct": [.49, .51, None], "upper_half": [True, False, True]})
    out = {r["team"]: r for r in sa.add_mix_zone(st, col="live_wpct", prefix="live_mix").iter_rows(named=True)}
    assert out["c"]["live_mix_lo"] == pytest.approx(.49) and out["c"]["live_mix_hi"] == pytest.approx(.51)
    assert out["c"]["live_mix_zone"] is None            # 自分の値が空なら空
    assert "mix_zone" not in out["c"]                   # 元の列は作らない



# ---------- チーム守備成績 ----------

def _fld(team, g=143, po=3800, a=1500, e=50, dp=120, pb=5, fpct=None, tc=None):
    tc = po + a + e if tc is None else tc
    fpct = round((po + a) / tc, 3) if fpct is None else fpct
    return {"season": 2024, "team": team, "league": "C", "g": g, "tc": tc, "po": po, "a": a, "e": e,
            "dp_part": dp * 3, "dp": dp, "pb": pb, "fpct": fpct}


def test_fielding_join_rates_and_relative_to_others():
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2024] * 3, "league": ["C"] * 3, "team": ["a", "b", "c"], "G": [143] * 3})
    fld = pl.DataFrame([_fld("a", e=40), _fld("b", e=50), _fld("c", e=60)])
    out = {r["team"]: r for r in sa.fielding_join(st, fld).iter_rows(named=True)}
    assert out["a"]["fld_e_g"] == pytest.approx(40 / 143)
    assert out["a"]["fld_d_e_g"] == pytest.approx(40 / 143 - (50 + 60) / 2 / 143)   # 他球団より失策が少ない → マイナス
    assert out["b"]["fld_d_e_g"] == pytest.approx(0.0)
    assert out["a"]["fld_fpct"] == pytest.approx(5300 / 5340)
    assert "e" not in out["a"] and "po" not in out["a"]                               # 原票の数は結合しない


@pytest.mark.parametrize("bad,match", [
    ({"g": 142}, "試合数"),
    ({"tc": 9999}, "守備機会"),
    ({"fpct": 0.900}, "守備率"),
])
def test_fielding_join_stops_when_the_page_does_not_add_up(bad, match):
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2024], "league": ["C"], "team": ["a"], "G": [143]})
    with pytest.raises(ValueError, match=match):
        sa.fielding_join(st, pl.DataFrame([_fld("a", **bad)]))



# ---------- R60: 順位表で A・B の側が落ち着いた試合数 ----------

def test_standing_lock_by_hand():
    from sakanalytics import standing_lock
    teams = {**TEAMS, "c": {"name": "広島", "league": "C"}}
    # 4球団（上位半分 = 2位以内）。c は3日目まで上の側、4日目から下。g は初日だけ下
    rows = [("2024-04-01", "c", "g", 2, 1), ("2024-04-01", "t", "d", 2, 1),
            ("2024-04-02", "c", "t", 2, 1), ("2024-04-02", "g", "d", 2, 1),
            ("2024-04-03", "g", "c", 2, 1), ("2024-04-03", "t", "d", 2, 1),
            ("2024-04-04", "g", "c", 2, 1), ("2024-04-04", "t", "d", 2, 1),
            ("2024-04-05", "g", "d", 2, 1), ("2024-04-05", "t", "c", 2, 1)]
    v = {r["team"]: r for r in standing_lock(to_team_games(games(rows), teams)).iter_rows(named=True)}
    # 最後: g 4勝1敗、t 4勝1敗、c 2勝3敗、d 0勝5敗。c は 3日目（2勝1敗で3球団が並ぶ）まで上の側 → 4日目から落ち着く
    assert (v["c"]["lock_g"], v["c"]["lock_x"]) == (4, pytest.approx(0.75))
    assert (v["g"]["lock_g"], v["g"]["lock_x"]) == (2, pytest.approx(0.25))   # 初日 0勝1敗で下の側
    assert (v["t"]["lock_g"], v["d"]["lock_g"]) == (1, 1)                         # 一度も変わらない → 初日
    assert v["d"]["lg_set_lock_x"] == pytest.approx(0.75)                         # 上位2の顔ぶれ {g, t} は4日目から
    # 4つの区間（5試合 → 境 0・1・2・3・5）
    assert [v["g"][f"q_wl_{q}"] for q in range(1, 5)] == [-1, 1, 1, 2]
    assert [v["c"][f"q_wl_{q}"] for q in range(1, 5)] == [1, 1, -1, -2]
    assert all(r["lone_down_n"] == 0 for r in v.values())                          # どの区間も負け越しは2球団以上
    # c は4試合目の日に落ち着いた: それまで W W L L（.500）、その後 L（1試合 .000）。t は初日に落ち着き、以後 4試合 3勝1敗
    assert (v["c"]["pre_lock_wpct"], v["c"]["post_lock_g"], v["c"]["post_lock_wpct"]) == (pytest.approx(0.5), 1, pytest.approx(0.0))
    assert (v["t"]["post_lock_g"], v["t"]["post_lock_wpct"]) == (4, pytest.approx(0.75))
    # 4つ目の区間（5試合 → 4・5試合目）。最終の上位半分は {g, t}。すべて 2−1 の1点差
    # c: 4試合目 g に 1−2（上の相手）、5試合目 t に 1−2（上の相手）→ 上 −2、下 0、1点差 −2、点の差 −1/試合
    c = v["c"]
    assert (c["q4_g"], c["q4_rd_g"], c["q4_one_run_net"], c["q4_wl_vs_upper"], c["q4_wl_vs_lower"]) == (2, pytest.approx(-1.0), -2, -2, 0)
    # g: 4試合目 c に勝ち（下）、5試合目 d に勝ち（下）→ 下 +2
    assert (v["g"]["q4_wl_vs_upper"], v["g"]["q4_wl_vs_lower"]) == (0, 2)


def test_lone_down_counts_quarters_where_only_one_team_lost():
    from sakanalytics import standing_lock
    teams = {**TEAMS, "c": {"name": "広島", "league": "C"}}
    # 4日、各球団4試合。d だけが毎日負ける。ほかの3球団は、d に勝った球団以外は互いに 1勝1敗……にならないよう引き分けを使う
    rows = []
    for i, w in enumerate(["g", "t", "c", "g"]):
        others = [x for x in ("g", "t", "c") if x != w]
        rows += [(f"2024-04-{i + 1:02d}", w, "d", 3, 1), (f"2024-04-{i + 1:02d}", others[0], others[1], 2, 2)]
    v = {r["team"]: r for r in standing_lock(to_team_games(games(rows), teams)).iter_rows(named=True)}
    assert v["d"]["lone_down_n"] == 4 and v["g"]["lone_down_n"] == 0



# ---------- 試合ごとの得点表（R H E） ----------

def _ls(rows):
    return pl.DataFrame([{"date": d, "team": t, "r": r, "h": 5, "e": e} for d, t, r, e in rows])


def test_linescore_join_error_differences_by_game_type():
    import sakanalytics as sa

    tg = to_team_games(games([("2024-04-01", "d", "g", 3, 2), ("2024-04-02", "d", "g", 1, 5),
                              ("2024-04-03", "g", "d", 4, 3), ("2024-04-04", "d", "g", 6, 0)]), TEAMS)
    st = season_table(tg)
    ls = _ls([("2024-04-01", "d", 3, 0), ("2024-04-01", "g", 2, 1), ("2024-04-02", "d", 1, 2), ("2024-04-02", "g", 5, 0),
              ("2024-04-03", "g", 4, 0), ("2024-04-03", "d", 3, 1), ("2024-04-04", "d", 6, 0), ("2024-04-04", "g", 0, 0)])
    d = sa.linescore_join(st, tg, ls).filter(pl.col("team") == "d").row(0, named=True)
    # 中日: 自分の失策 0,2,1,0（計3）、相手 1,0,0,0（計1）
    assert d["ls_cov"] == pytest.approx(1.0) and d["ls_e_g"] == pytest.approx(3 / 4) and d["ls_opp_e_g"] == pytest.approx(1 / 4)
    assert d["ls_e_net_g"] == pytest.approx(2 / 4)
    assert d["ls_e_net_close"] == pytest.approx((-1 + 1) / 2)     # 1点差は 4/1（勝ち、−1）と 4/3（負け、+1）
    assert d["ls_e_net_win"] == pytest.approx((-1 + 0) / 2) and d["ls_e_net_loss"] == pytest.approx((2 + 1) / 2)
    assert d["ls_e_net_q4"] == pytest.approx(0.0)                  # 最後の区間は4試合目だけ（境 4 × 3 ÷ 4 = 3）


def test_linescore_join_stops_on_mismatch_and_leaves_missing_years_empty():
    import sakanalytics as sa

    tg = to_team_games(games([("2024-04-01", "d", "g", 3, 2), ("2023-04-01", "d", "g", 1, 0)]), TEAMS)
    st = season_table(tg)
    with pytest.raises(ValueError, match="R が"):
        sa.linescore_join(st, tg, _ls([("2024-04-01", "d", 4, 0), ("2024-04-01", "g", 2, 0)]))
    with pytest.raises(ValueError, match="2つ以上"):
        sa.linescore_join(st, tg, _ls([("2024-04-01", "d", 3, 0), ("2024-04-01", "d", 3, 0), ("2024-04-01", "g", 2, 0)]))
    out = {(r["season"], r["team"]): r for r in sa.linescore_join(
        st, tg, _ls([("2024-04-01", "d", 3, 0), ("2024-04-01", "g", 2, 1)])).iter_rows(named=True)}
    assert out[(2024, "d")]["ls_cov"] == pytest.approx(1.0) and out[(2023, "d")]["ls_cov"] == 0.0
    assert out[(2023, "d")]["ls_e_net_g"] is None                 # 取得していない年は空



def test_state2_two_lines_on_values():
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 6 + [2001] * 6, "league": ["C"] * 12, "team": list("abcdef") * 2,
                       "x": [6, 5, 4, 3, 2, 1, 6, 5, 4, 3, 2, None]})
    out = {(r["season"], r["team"]): r["xs"] for r in sa.add_state2(st, "x", "xs").iter_rows(named=True)}
    # 線は (5+4)/2 = 4.5 と (3+2)/2 = 2.5 → 6・5 は A、4・3 は AB、2・1 は B
    assert [out[(2000, t)] for t in "abcdef"] == ["A", "A", "AB", "AB", "B", "B"]
    assert all(out[(2001, t)] is None for t in "abcdef")   # 値のない球団があるリーグ年は空



def test_bar_from_run_differences_uses_only_the_other_teams():
    """R73: 点の差から見た越えるべき高さ。.500 のような固定の値を使わない。"""
    import sakanalytics as sa

    w = [0.62, 0.60, 0.53, 0.52, 0.51, 0.40]
    py = [0.70, 0.55, 0.52, 0.51, 0.47, 0.40]   # 1位が点の差で独走している年
    st = pl.DataFrame({"season": [2000] * 6, "league": ["C"] * 6, "team": list("abcdef"), "rank": [1, 2, 3, 4, 5, 6],
                       "wpct": w, "pythag_fixed": py})
    out = {r["team"]: r for r in sa.add_league_shape(st).iter_rows(named=True)}
    # c はほかの5球団の点の差で見込む勝率 .70・.55・.51・.47・.40 の3番目 = .51 を越えるべき。d は .70・.55・.52 の3番目 = .52
    assert out["c"]["lg_bar_pythag"] == pytest.approx(0.51) and out["c"]["pbar_gap"] == pytest.approx(0.01)
    assert out["d"]["lg_bar_pythag"] == pytest.approx(0.52) and out["d"]["pbar_gap"] == pytest.approx(-0.01)
    assert out["a"]["lg_bar_pythag"] == pytest.approx(0.51)



def test_bar_gaps_are_relative_to_the_seasons_own_bar():
    import sakanalytics as sa

    st = pl.DataFrame({"season": [2000] * 6 + [2001] * 6, "league": ["C"] * 12, "team": list("abcdefabcdef"),
                       "x": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]})
    out = {(r["season"], r["team"]): r["x_bgap"] for r in sa.add_bar_gaps(st, ["x"]).iter_rows(named=True)}
    # 2000年: c のほかの5球団の3番目は d の 3 → +1。d は c の 4 → −1。2001年は同じ並びで値が 1/10 → ±0.1
    assert out[(2000, "c")] == pytest.approx(1) and out[(2000, "d")] == pytest.approx(-1)
    assert out[(2001, "c")] == pytest.approx(0.1) and out[(2001, "d")] == pytest.approx(-0.1)
    assert sa.add_bar_gaps(st, ["missing"]).columns == st.columns


def test_vs_top_is_compared_with_the_seasons_bar():
    import sakanalytics as sa

    st = pl.DataFrame({"team": ["a", "b"], "vs_top_wpct": [0.45, None], "lg_bar": [0.47, 0.5]})
    out = sa.add_vs_top_bar_gap(st)
    assert out["vs_top_bar_gap"].to_list()[0] == pytest.approx(-0.02) and out["vs_top_bar_gap"].to_list()[1] is None
    assert sa.add_vs_top_bar_gap(st.drop("lg_bar")).columns == ["team", "vs_top_wpct"]
