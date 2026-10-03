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
