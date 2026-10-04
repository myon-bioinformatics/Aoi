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
