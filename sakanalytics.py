"""SakAnalytics — データから、まだ見ぬ構造を。

観測データセット（1試合1行: key, date, home, away, hs, as）から、チーム×シーズンの指標を作る。
ここでは「測れるもの」を測るだけで、良し悪しの判断や除外はしない（PythDRagoras の仕事）。

チームの所属リーグと表示名は、分析設定（TOML の [teams]）で明示的に与える。
取得元に依存しないため、野球以外の「対戦の記録」にも使える形にしている。

主な列:
  W, L, T, RF, RA, wpct            引き分けは勝率の分母から除く
  pythag_fixed / pythag_var        ピタゴラス期待勝率（指数1.83固定 / Pythagenpat）
  resid_fixed / resid_var          実勝率 − 期待勝率
  logit_resid                      logit(W%) − 1.83·log(RF/RA)。比でなく差なので常に定義される
  k_eff                            得点比を勝ちに変える実効指数。RF≒RA（±2%未満）では空
  w_1..l_4plus                     1/2/3/4点以上差ごとの勝敗
  wpct_1run / wpct_2run            1点差・2点差の勝率（競合仮説の材料）
  *_median / *_mode / *_iqr        勝ち試合の点差・負け試合の点差・得点・失点の中央値・最頻値・IQR
  rank / rank_tie                  リーグ内の勝率順位（派生値）。同率は小さい順位にそろえ、rank_tie=True
  upper_half                       rank <= リーグの球団数/2（6球団なら3位以内）
  rd                               得失点差 RF − RA
  rank_pythag / rank_rf / rank_ra / rank_rd
                                   ピタゴラス期待勝率・得点・失点（少ない順）・得失点差のリーグ内順位
  rank_gap                         rank − rank_pythag（正なら、得失点から期待される順位より下）
  wins_vs_pythag                   W − (W+L)·pythag_fixed（期待勝利数との差。正なら期待以上）
  one_run_net / two_run_net        1点差・2点差の勝ち越し数（w − l）
  blowout_net                      4点以上差の勝ち越し数（w_4plus − l_4plus）
  rank_wpct_1run                   1点差勝率のリーグ内順位（高い順）
  rd_home_g / rd_away_g            ホーム・ビジターの試合での得失点差／試合
  home_away_gap                    rd_home_g − rd_away_g（観測した差。補正の係数には使わない）
  home_away_gap_vs_league          home_away_gap − 同じ年・同じリーグの他球団の home_away_gap の平均
  rf_def_floor / _mid / _ceiling   得点／試合の他球団平均との差を、得点帯（0〜2点 / 3〜5点 / 6点以上）に分けたもの（R3）
  rf_def_total                     3つの合計 = 得点／試合 − 同じ年・同じリーグの他球団の得点／試合の平均
  rf_def_floor_minus_ceiling       rf_def_floor − rf_def_ceiling（負なら、床の不足が天井の不足より大きい）
  vs_upper_wpct / vs_lower_wpct    リーグ内で上位半分・下位半分だった相手との勝率（R12。最終順位から逆にたどる面がある）
  vs_top_wpct / vs_battle_wpct     上の相手（6球団なら1・2位）、3位を争う相手（3〜5位、自分を除く）との勝率（R13）
  focus_gap                        vs_battle_wpct − vs_top_wpct（争う相手に重点を置けていたか、R13）
  vs_lower_wpct_d                  vs_lower_wpct − 同じ年・同じリーグの他球団の平均（R13）
  pair34_*_diff                    3位と4位の間で、相手チームとの差（vs_lower_wpct / vs_battle_wpct / focus_gap、R13）
  vs_near_net / pair34_net         順位が1つ違いの相手、3位と4位どうしの（勝 − 敗）（R12）
  half1_vs_pythag / half2_vs_pythag  前半・後半それぞれの（勝 − 期待勝利数）（R12）
  max_win_streak / max_lose_streak / max_lose_streak_d  最長連勝・最長連敗と、連敗の他球団平均との差（R12）
  opp_adj_top / mid / low / total  相手の強さ（自分との試合を除く）から見込まれる勝ち数との差を、相手のグループごとに足したもの（R15）
  pair34_opp_adj_*_diff            その3位と4位の間の差（R15）
  opp_rf_gap_* / opp_ra_gap_* / opp_conv_*  相手のグループごとの、得点・失点の見込みとの差と、点の差では説明できない勝ち負け（R16）
  opp_top_rf_minus_ra              強い相手に対する（得点の差 − 失点の差）。負なら得点の側に大きい（R16）
  opp_rf_gap_*_c / opp_ra_gap_*_c  同じ年・同じリーグの全球団の平均を引いた値（見込みの式の、相手グループごとの偏りを除く）
  opp_net_gap_*_c / opp_env_gap_*_c  上の2つを回した軸（R17）。net = 得点の差 + 失点の差（どちらが上回ったか）、
                                   env = 得点の差 − 失点の差（試合全体の点の多さ。負なら点の入りにくい試合）
  wl_rf_win / wl_rf_loss (+ _exp / _gap)  勝ち試合・負け試合の得点／試合と、得点・失点の組み合わせだけをランダムにしたときの見込み、その差（R20）
  wl_wpct_low / wl_wpct_high (+ _exp / _gap)  両チームの合計得点が、リーグの試合の中央値以下／より多い試合の勝率と、その見込み・差（R20）
  course_wpct_h1 / _h2 / _diff     前半・後半の勝率と、後半 − 前半（R20）
  course_rank_q1 / _h1 / _q3       試合数の 1/4・1/2・3/4 までの勝率での順位（R20）
  course_fade                      最終順位 − course_rank_h1（正なら前半の位置より下で終わった、R20）
  course_rf_d / course_ra_d        後半と前半の得点／試合・失点／試合の差の、他球団の平均との差（R20）
  course_ra_h1_d                   前半の失点／試合の、他球団の平均との差（R20）
  course_close_win_h1(_d)          前半の勝ちのうち2点差以内の割合と、その他球団の平均との差（R20）
  traj_rank_* / traj_wl_*          日付ごとの順位の高さ・貯金の線を3次式でならした形（山・谷・その位置・最後の傾き）と、
                                   力が一定でも山・谷ができる割合 *_base（R22。season_trajectory）。traj_start_* は線の始まり
  wave_*                           順位の線を、始まりの値から出発して減衰する波で表したもの（収束する先・決まった位置・周期、R23）
  inn_size_rank / inn_size_low_streak / rf_low_streak  低いままの状態が何年続いているか（R14。add_persistence）
  sim_p_upper / sim_wpct           得点・失点の分布だけからシーズンを作り直したときの、上位半分に入る確率・勝率の期待値（R10）
  rf_def_k67 / rf_def_floor_minus_k67  k = 6〜7 の帯（幅2）と、床（幅2）との差（R7。帯の幅をそろえた比較）
  inn_*（--innings があるとき）     イニング単位の集計からの列（R4）。inn_I/S/R: 攻撃回数・得点した回の数・得点
    inn_dlog_rpi/_freq/_size       log(得点/回)・log(得点した回の割合)・log(得点した回の平均得点) の、他球団平均との差
    inn_freq_minus_size            inn_dlog_freq − inn_dlog_size（負なら、頻度の不足が大きさの不足より大きい）
    *_6                            双方が6回まで攻撃した試合の1〜6回だけで同じ計算
    *_home / *_away                ホーム・ビジターの試合だけで同じ計算（球場の係数ではない。比べる範囲を分けるだけ）
  bat_*（--batting があるとき）     チーム打撃成績から計算した率（R6）。打数・本塁打数などの原票の値は出力しない
    bat_avg / obp / slg / iso      打率・出塁率・長打率・ISO（長打率 − 打率）
    bat_hr_pa / bb_pa / so_pa      本塁打・四死球・三振の、打席あたりの割合
    bat_xbh_h                      安打のうち長打（二塁打・三塁打・本塁打）の割合
    bat_walk_share                 出塁（安打＋四球＋死球）のうち、四球・死球の割合（R8）
    bat_ibb_bb                     四球のうち故意四球の割合（R8）
    bat_r_ab / r_pa                打数あたり・打席あたりの得点（R9）
    bat_r_runner                   走者（安打＋四球＋死球）1人あたりの得点（R9。本塁打の打者も走者に数える）
    bat_d_*                        それぞれの、同じ年・同じリーグの他球団の平均との差
    inn_single_share / big_share   得点した回のうち、1点の回・3点以上の回の割合（R5）
    inn_d_single_share / _big_share  それぞれの、同じ年・同じリーグの他球団の平均との差
  alloc_*                          得点・失点の配分効果（cycles/c001-chunichi/research/R1-score-allocation.md）
                                   試合ごとの得点の並びと失点の並びを保ち、組み合わせだけをランダムにした基準との差
    alloc_exp_net / alloc_var      基準の（勝 − 敗）の期待値と分散（Hoeffding の厳密な公式。乱数を使わない）
    alloc_net / alloc_z            実際の（勝 − 敗）− 期待値、その標準化
    *_home / *_away                ホームどうし・ビジターどうしの中だけで入れ替えた基準
    *_strat                        ホームとビジターを分けた基準の合計
    *_opp                          対戦相手 × ホーム/ビジターの組ごとに入れ替えた基準の合計（球場の係数ではない。比べる範囲を狭めるだけ）
    alloc_z_abs / alloc_same_sign  |alloc_z|、ホームとビジターで alloc_net の符号がそろうか
    alloc_z_next                   同じチームの翌シーズンの alloc_z（翌年がなければ空）
"""

from __future__ import annotations

import argparse
import math
import operator
import random
import sys
import tomllib
from collections import Counter
from datetime import date
from pathlib import Path

import polars as pl

K_FIXED = 1.83
PYTHAGENPAT_EXP = 0.287
BINS = (1, 2, 3, 4)  # 4 は「4点以上」


def to_team_games(games: pl.DataFrame, teams: dict[str, dict]) -> pl.DataFrame:
    """1試合1行 → 両チーム視点の2行。teams = {code: {"name": .., "league": ..}}。"""
    unknown = (set(games["home"]) | set(games["away"])) - set(teams)
    if unknown:  # 黙って捨てない
        raise ValueError(f"teams に定義のないチーム: {sorted(unknown)}")
    home = games.select("date", team="home", opp="away", rf="hs", ra="as", is_home=pl.lit(True))
    away = games.select("date", team="away", opp="home", rf="as", ra="hs", is_home=pl.lit(False))
    return (
        pl.concat([home, away])
        .with_columns(
            season=pl.col("date").str.slice(0, 4).cast(pl.Int32),
            league=pl.col("team").replace_strict({k: v["league"] for k, v in teams.items()}),
            team_name=pl.col("team").replace_strict({k: v["name"] for k, v in teams.items()}),
        )
        .sort("date", "team")
    )


def _sign(x: int) -> int:
    return (x > 0) - (x < 0)


def allocation(rf: list[int], ra: list[int]) -> tuple[float, float]:
    """得点の並び rf と失点の並び ra を、組み合わせだけランダムにしたときの（勝 − 敗）の期待値と分散。

    T = Σ_i c(i, π(i))、c = 符号(rf_i − ra_j)、π は一様な順列。Hoeffding (1951):
      E[T]   = (1/n) Σ_ij c_ij
      Var[T] = 1/(n−1) Σ_ij d_ij²,  d_ij = c_ij − 行平均_i − 列平均_j + 全体平均
    同じ値の試合はまとめて数える（結果は試合ごとの総当たりと同じ）。
    """
    n = len(rf)
    if n != len(ra):
        raise ValueError("rf と ra の試合数が違う")
    if n == 0:
        return 0.0, 0.0
    xs, ys = Counter(rf), Counter(ra)
    c = {(x, y): _sign(x - y) for x in xs for y in ys}
    row = {x: sum(ys[y] * c[x, y] for y in ys) / n for x in xs}
    col = {y: sum(xs[x] * c[x, y] for x in xs) / n for y in ys}
    total = sum(xs[x] * ys[y] * c[x, y] for x in xs for y in ys)
    mean = total / (n * n)
    expected = total / n
    if n == 1:
        return expected, 0.0
    ss = sum(xs[x] * ys[y] * (c[x, y] - row[x] - col[y] + mean) ** 2 for x in xs for y in ys)
    return expected, ss / (n - 1)


def allocation_table(tg: pl.DataFrame) -> pl.DataFrame:
    """チーム×シーズンごとの配分効果（全試合、ホームだけ、ビジターだけ、層別の合計）。"""
    rows = []
    for (season, team), g in tg.group_by(["season", "team"], maintain_order=True):
        out = {"season": season, "team": team}
        parts = {"": g, "_home": g.filter(pl.col("is_home")), "_away": g.filter(~pl.col("is_home"))}
        for tag, part in parts.items():
            rf, ra = part["rf"].to_list(), part["ra"].to_list()
            exp, var = allocation(rf, ra)
            net = sum(_sign(a - b) for a, b in zip(rf, ra))
            out |= {f"alloc_exp_net{tag}": exp, f"alloc_var{tag}": var, f"alloc_net{tag}": net - exp,
                    f"alloc_z{tag}": (net - exp) / math.sqrt(var) if var > 0 else None}
        exp = out["alloc_exp_net_home"] + out["alloc_exp_net_away"]
        var = out["alloc_var_home"] + out["alloc_var_away"]
        net = out["alloc_net_home"] + out["alloc_net_away"]  # すでに期待値を引いた値の合計
        out |= {"alloc_exp_net_strat": exp, "alloc_var_strat": var, "alloc_net_strat": net,
                "alloc_z_strat": net / math.sqrt(var) if var > 0 else None}
        exp = var = net = 0.0  # 対戦相手 × ホーム/ビジターの組ごとに入れ替えた基準の合計
        for _, cell in g.group_by(["opp", "is_home"]):
            rf, ra = cell["rf"].to_list(), cell["ra"].to_list()
            e, v = allocation(rf, ra)
            exp, var, net = exp + e, var + v, net + sum(_sign(a - b) for a, b in zip(rf, ra)) - e
        out |= {"alloc_exp_net_opp": exp, "alloc_var_opp": var, "alloc_net_opp": net,
                "alloc_z_opp": net / math.sqrt(var) if var > 0 else None}
        rows.append(out)
    floats = {k: pl.Float64 for k in rows[0] if k.startswith("alloc_")} if rows else {}
    t = pl.DataFrame(rows, schema_overrides={"season": pl.Int32, **floats})  # 値がすべて空でも型を決める
    t = t.with_columns(
        alloc_z_abs=pl.col("alloc_z").abs(),
        alloc_same_sign=(pl.col("alloc_net_home") * pl.col("alloc_net_away")) > 0,
    )
    nxt = t.select("team", season=pl.col("season") - 1, alloc_z_next=pl.col("alloc_z"))
    return t.join(nxt, on=["season", "team"], how="left")


# k の範囲（k 点以上取れたか）。k67 は floor と同じ幅（2段）で天井側を見るための帯（R7、P19 の異議から）
SCORING_BANDS = {"floor": (1, 2), "mid": (3, 5), "ceiling": (6, None), "k67": (6, 7)}


def scoring_deficit(tg: pl.DataFrame) -> pl.DataFrame:
    """得点の差を、どの得点帯で生まれたかに分ける（R3）。

    1試合の平均得点 = Σ_{k≥1} P(得点 ≥ k)。同じ年・同じリーグの他球団の P(得点 ≥ k) の平均との差を
    k ごとに取り、帯ごとに足す。帯の合計は「得点／試合 − 他球団の得点／試合の平均」にちょうど一致する。
      rf_def_floor   : k = 1〜2（0〜2点に抑えられる試合の多さ）
      rf_def_mid     : k = 3〜5
      rf_def_ceiling : k ≥ 6（大量得点の少なさ）
      rf_def_k67     : k = 6〜7（floor と同じ幅で天井側を見る。rf_def_ceiling の一部で、合計には足さない）
    """
    tails: dict[tuple, dict[int, float]] = {}
    league_of: dict[tuple, str] = {}
    for (season, team, league), g in tg.group_by(["season", "team", "league"]):
        rf = g["rf"].to_list()
        n = len(rf)
        tails[(season, team)] = {k: sum(r >= k for r in rf) / n for k in range(1, max(rf, default=0) + 1)}
        league_of[(season, team)] = league
    rows = []
    for (season, team), t in tails.items():
        others = [o for key, o in tails.items()
                  if key[0] == season and key[1] != team and league_of[key] == league_of[(season, team)]]
        if not others:
            continue
        ks = set(t).union(*others)
        diff = {k: t.get(k, 0.0) - sum(o.get(k, 0.0) for o in others) / len(others) for k in ks}
        out = {"season": season, "team": team}
        for band, (lo, hi) in SCORING_BANDS.items():
            out[f"rf_def_{band}"] = sum(v for k, v in diff.items() if k >= lo and (hi is None or k <= hi))
        out["rf_def_total"] = sum(diff.values())
        rows.append(out)
    schema = {"season": pl.Int32, "team": pl.Utf8, **{f"rf_def_{b}": pl.Float64 for b in [*SCORING_BANDS, "total"]}}
    t = pl.DataFrame(rows, schema=schema)
    return t.with_columns(rf_def_floor_minus_ceiling=pl.col("rf_def_floor") - pl.col("rf_def_ceiling"),
                          rf_def_floor_minus_k67=pl.col("rf_def_floor") - pl.col("rf_def_k67"))


def inning_decomposition(st: pl.DataFrame, innings: pl.DataFrame) -> pl.DataFrame:
    """イニング単位の集計（R4）を結合し、1イニングあたりの得点の差を「頻度」と「大きさ」に分ける。

    innings: 1行 = チーム×シーズン×window。列 season, team, window（"all" / "first6"）, games, innings, runs, scoring_innings
             （外部の集計を読む。最終スコア側の G・RF と1つでも合わなければ ValueError で止める）
    得点／イニング = 得点した回の割合 × 得点した回の平均得点。対数を取り、同じ年・同じリーグの他球団の平均との差にすると
      inn_dlog_rpi = inn_dlog_freq + inn_dlog_size  （ちょうど一致する）
    first6（双方が6回まで攻撃した試合の1〜6回）は、9回裏の省略・延長の影響を小さくした比較（列名の末尾 _6）。
    """
    over = ["season", "league"]
    out = st
    if "venue" not in innings.columns:
        innings = innings.with_columns(venue=pl.lit("all"))
    shares = {"single_run_inning_rate", "big_inning_rate"} <= set(innings.columns)
    parts = [("all", "all", ""), ("all", "first6", "_6"), ("home", "all", "_home"), ("away", "all", "_away")]
    for venue, window, tag in parts:
        sel = innings.filter((pl.col("venue") == venue) & (pl.col("window") == window))
        if sel.height == 0:
            continue
        w = sel.select(
            "season", "team", pl.col("games").alias("_g"), pl.col("innings").alias(f"inn_I{tag}"),
            pl.col("runs").alias("_r"), pl.col("scoring_innings").alias(f"inn_S{tag}"),
            *([(pl.col("single_run_inning_rate") * pl.col("innings") / pl.col("scoring_innings")).alias(f"inn_single_share{tag}"),
               (pl.col("big_inning_rate") * pl.col("innings") / pl.col("scoring_innings")).alias(f"inn_big_share{tag}")]
              if shares else []))
        if (venue, window) == ("all", "all"):
            chk = st.select("season", "team", "G", "RF").join(w, on=["season", "team"], how="inner")
            bad = chk.filter((pl.col("G") != pl.col("_g")) | (pl.col("RF") != pl.col("_r")))
            if bad.height:
                raise ValueError(f"イニング集計が最終スコアと合わない: {bad.select('season', 'team').rows()[:5]}")
        out = out.join(w.rename({"_r": f"inn_R{tag}"}).drop("_g"), on=["season", "team"], how="left")
        I, S, R = pl.col(f"inn_I{tag}"), pl.col(f"inn_S{tag}"), pl.col(f"inn_R{tag}")
        logs = {"rpi": (R / I).log(), "freq": (S / I).log(), "size": (R / S).log()}
        out = out.with_columns(**{f"_l{k}": v for k, v in logs.items()})
        out = out.with_columns(**{
            f"inn_dlog_{k}{tag}": pl.col(f"_l{k}")
            - (pl.col(f"_l{k}").sum().over(over) - pl.col(f"_l{k}")) / (pl.col(f"_l{k}").count().over(over) - 1)
            for k in logs
        }).drop([f"_l{k}" for k in logs])
        out = out.with_columns(**{f"inn_freq_minus_size{tag}": pl.col(f"inn_dlog_freq{tag}") - pl.col(f"inn_dlog_size{tag}")})
        if shares:  # 得点した回のうち 1点の回・3点以上の回の割合の、他球団平均との差（R5）
            out = out.with_columns(**{
                f"inn_d_{k}{tag}": pl.col(f"inn_{k}{tag}")
                - (pl.col(f"inn_{k}{tag}").sum().over(over) - pl.col(f"inn_{k}{tag}"))
                / (pl.col(f"inn_{k}{tag}").count().over(over) - 1)
                for k in ("single_share", "big_share")
            })
    if {"inn_R_home", "inn_R_away"} <= set(out.columns):  # ホームとビジターの和が全体と合うか
        bad = out.filter(pl.col("inn_R").is_not_null() & ((pl.col("inn_R_home") + pl.col("inn_R_away") != pl.col("inn_R"))
                                                          | (pl.col("inn_I_home") + pl.col("inn_I_away") != pl.col("inn_I"))))
        if bad.height:
            raise ValueError(f"イニング集計のホーム＋ビジターが全体と合わない: {bad.select('season', 'team').rows()[:5]}")
    return out


BATTING_RATES = {
    "avg": lambda: pl.col("h") / pl.col("ab"),
    "obp": lambda: (pl.col("h") + pl.col("bb") + pl.col("hbp")) / (pl.col("ab") + pl.col("bb") + pl.col("hbp") + pl.col("sf")),
    "slg": lambda: pl.col("tb") / pl.col("ab"),
    "iso": lambda: (pl.col("tb") - pl.col("h")) / pl.col("ab"),
    "hr_pa": lambda: pl.col("hr") / pl.col("pa"),
    "bb_pa": lambda: (pl.col("bb") + pl.col("hbp")) / pl.col("pa"),
    "so_pa": lambda: pl.col("so") / pl.col("pa"),
    "xbh_h": lambda: (pl.col("b2") + pl.col("b3") + pl.col("hr")) / pl.col("h"),
    # 出塁のうち、四球・死球による割合（R8）。安打で出たのか、四死球で出たのか
    "walk_share": lambda: (pl.col("bb") + pl.col("hbp")) / (pl.col("h") + pl.col("bb") + pl.col("hbp")),
    # 四球のうち故意四球の割合（勝負を避けられた分）
    "ibb_bb": lambda: pl.col("ibb") / pl.col("bb"),
    # 機会あたりの得点（R9）。打数あたり・打席あたり・走者（安打＋四球＋死球）1人あたり
    "r_ab": lambda: pl.col("r") / pl.col("ab"),
    "r_pa": lambda: pl.col("r") / pl.col("pa"),
    "r_runner": lambda: pl.col("r") / (pl.col("h") + pl.col("bb") + pl.col("hbp")),
}


def batting_join(st: pl.DataFrame, bat: pl.DataFrame) -> pl.DataFrame:
    """チーム打撃成績（R6）から率を計算して結合する。結合するのは率と、同じ年・同じリーグの他球団の平均との差だけ。

    照合（1つでも合わなければ ValueError）:
      - 試合数・得点が、最終スコア由来の G・RF と一致する
      - 打数などから計算し直した打率・長打率・出塁率が、ページの値と表示桁（小数3桁）で一致する
    率: bat_avg / obp / slg / iso（= 長打率 − 打率）/ hr_pa（本塁打／打席）/ bb_pa（四死球／打席）/ so_pa / xbh_h（長打／安打）
    """
    over = ["season", "league"]
    b = bat.with_columns(pl.col("season").cast(pl.Int32)).with_columns(
        **{f"bat_{k}": f() for k, f in BATTING_RATES.items()})
    chk = st.select("season", "team", "G", "RF").join(b, on=["season", "team"], how="inner")
    bad = chk.filter((pl.col("G") != pl.col("g")) | (pl.col("RF") != pl.col("r")))
    if bad.height:
        raise ValueError(f"打撃成績の試合数・得点が最終スコアと合わない: {bad.select('season', 'team').rows()[:5]}")
    for k in ("avg", "obp", "slg"):
        off = b.filter((pl.col(f"bat_{k}") - pl.col(k)).abs() > 0.0005 + 1e-9)
        if off.height:
            raise ValueError(f"打撃成績の {k} を計算し直すとページの値と合わない: {off.select('season', 'team').rows()[:5]}")
    cols = [f"bat_{k}" for k in BATTING_RATES]
    out = st.join(b.select("season", "team", *cols), on=["season", "team"], how="left")
    return out.with_columns(**{
        f"bat_d_{k}": pl.col(f"bat_{k}") - (pl.col(f"bat_{k}").sum().over(over) - pl.col(f"bat_{k}"))
        / (pl.col(f"bat_{k}").count().over(over) - 1)
        for k in BATTING_RATES
    })


def _season_wpct_pmf(rf: list[int], ra: list[int]) -> tuple[list[float], list[float]]:
    """1試合 = 自分の得点の分布から1つ、失点の分布から1つを独立に引く。それを試合数だけ繰り返したときの勝率の分布。

    返り値: (勝率の値（昇順）, その確率)。勝率 = 勝 / (勝 + 敗)。引き分けは数えない（全試合引き分けの組は除く）
    """
    n = len(rf)
    xs, ys = Counter(rf), Counter(ra)
    pw = sum(xs[x] * ys[y] for x in xs for y in ys if x > y) / (n * n)
    pt = sum(xs[x] * ys[x] for x in xs) / (n * n)
    pl_ = 1.0 - pw - pt
    logs = [math.log(q) if q > 0 else None for q in (pw, pt, pl_)]
    lg = [math.lgamma(k + 1) for k in range(n + 1)]
    dist: dict[float, float] = {}
    for w in range(n + 1):
        for t in range(n - w + 1):
            l_ = n - w - t
            if w + l_ == 0 or any(c > 0 and lq is None for c, lq in zip((w, t, l_), logs)):
                continue
            lp = lg[n] - lg[w] - lg[t] - lg[l_] + sum(c * lq for c, lq in zip((w, t, l_), logs) if c > 0)
            v = w / (w + l_)
            dist[v] = dist.get(v, 0.0) + math.exp(lp)
    vals = sorted(dist)
    total = sum(dist.values())
    return vals, [dist[v] / total for v in vals]


def rank_probability(tg: pl.DataFrame) -> pl.DataFrame:
    """R10: 各チームの得点・失点の分布だけからシーズンを作り直したとき、上位半分（A クラス）に入る確率。

    乱数で何度もシーズンを作る代わりに、その極限（作り直しを無限に繰り返したときの割合）を厳密に計算する。
    順位はリーグ内の勝率で、同率は上の順位に数える（rank "min" と同じ）。各チームは独立に作り直す。
      sim_p_upper : 上位半分に入る確率
      sim_wpct    : 勝率の期待値
    """
    from bisect import bisect_right

    pmf, league_of = {}, {}
    for (season, team, league), g in tg.group_by(["season", "team", "league"]):
        pmf[(season, team)] = _season_wpct_pmf(g["rf"].to_list(), g["ra"].to_list())
        league_of[(season, team)] = league
    tails = {}
    for key, (vals, probs) in pmf.items():  # P(勝率 > v) を引くための後ろからの累積
        acc, suffix = 0.0, [0.0] * (len(vals) + 1)
        for i in range(len(vals) - 1, -1, -1):
            acc += probs[i]
            suffix[i] = acc
        tails[key] = (vals, suffix)
    rows = []
    for (season, team), (vals, probs) in pmf.items():
        others = [k for k in pmf if k[0] == season and k[1] != team and league_of[k] == league_of[(season, team)]]
        allowed = (len(others) + 1) // 2 - 1  # 上位半分 = 自分より勝率の高いチームが allowed 以下
        p_up = 0.0
        for v, pv in zip(vals, probs):
            dp = [1.0] + [0.0] * (allowed + 1)  # dp[k] = 自分より上が k チーム（allowed+1 は「それより多い」）
            for k in others:
                ov, suf = tails[k]
                q = suf[bisect_right(ov, v)]
                nxt = [0.0] * (allowed + 2)
                for c, pc in enumerate(dp):
                    nxt[c] += pc * (1 - q)
                    nxt[min(c + 1, allowed + 1)] += pc * q
                dp = nxt
            p_up += pv * sum(dp[: allowed + 1])
        rows.append({"season": season, "team": team, "sim_p_upper": p_up,
                     "sim_wpct": sum(v * pv for v, pv in zip(vals, probs))})
    return pl.DataFrame(rows, schema={"season": pl.Int32, "team": pl.Utf8, "sim_p_upper": pl.Float64, "sim_wpct": pl.Float64})


def _streaks(results: list[int]) -> tuple[int, int]:
    """勝敗の並び（+1 勝 / −1 敗 / 0 引き分け）から、最長連勝・最長連敗。引き分けは連続を切る。"""
    best_w = best_l = cur = 0
    for r in results:
        cur = (cur + 1 if cur > 0 else 1) if r > 0 else (cur - 1 if cur < 0 else -1) if r < 0 else 0
        best_w, best_l = max(best_w, cur), max(best_l, -cur)
    return best_w, best_l


def _pythag_gap(rf: list[int], ra: list[int]) -> float | None:
    """その試合の集まりでの（勝 − 期待勝利数）。期待勝利数 = (勝 + 敗) × ピタゴラス（指数 K_FIXED）。"""
    w = sum(a > b for a, b in zip(rf, ra))
    l_ = sum(a < b for a, b in zip(rf, ra))
    r, a = sum(rf), sum(ra)
    if r == 0 or a == 0 or w + l_ == 0:
        return None
    return w - (w + l_) / (1 + (a / r) ** K_FIXED)


def boundary_features(tg: pl.DataFrame, st: pl.DataFrame) -> pl.DataFrame:
    """R12: 順位の境目（3位と4位）で効きそうな、試合の並びと相手から作る指標。st には最終順位（rank）が要る。

    対戦相手の指標は同じリーグの相手との試合だけで数える（交流戦の相手の順位は別のリーグの順位なので使わない）。
      vs_upper_wpct / vs_lower_wpct : 最終的に上位半分・下位半分だったリーグ内の相手との勝率（引き分けを除く）
      vs_near_net                    : 最終順位が1つ違いの相手との（勝 − 敗）
      pair34_net                     : 3位のチームは4位の相手と、4位のチームは3位の相手との（勝 − 敗）。他の順位は空
      half1_vs_pythag / half2_vs_pythag : シーズンを試合数で前後半に分け、それぞれの（勝 − 期待勝利数）
      max_win_streak / max_lose_streak : 最長連勝・最長連敗（引き分けで切れる）
      max_lose_streak_d              : 最長連敗 − 同じ年・同じリーグの他球団の平均
    最終順位を使う指標（vs_upper など）は、勝ち負けで決まった順位から逆にたどる面がある（相手の順位も自分との試合で決まる）。
    """
    rank = {(r["season"], r["team"]): (r["rank"], r["league"], r["upper_half"]) for r in st.iter_rows(named=True)}
    rows = []
    for (season, team), g in tg.sort("date").group_by(["season", "team"], maintain_order=True):
        my_rank, league, _ = rank[(season, team)]
        res = [(a > b) - (a < b) for a, b in zip(g["rf"].to_list(), g["ra"].to_list())]
        opps = g["opp"].to_list()
        same = [(r, rank[(season, o)]) for r, o in zip(res, opps) if rank[(season, o)][1] == league]
        def wpct(rs):
            w, l_ = sum(x > 0 for x in rs), sum(x < 0 for x in rs)
            return w / (w + l_) if w + l_ else None
        other34 = {3: 4, 4: 3}.get(my_rank)
        rf, ra = g["rf"].to_list(), g["ra"].to_list()
        half = len(rf) // 2
        win_s, lose_s = _streaks(res)
        near = [r for r, (rk, _, _) in same if abs(rk - my_rank) == 1]
        pair = [r for r, (rk, _, _) in same if rk == other34] if other34 else []
        size = sum(1 for k, v in rank.items() if k[0] == season and v[1] == league)
        cut = size // 2  # 上位半分の最後の順位（6球団なら3位）
        rows.append({
            "season": season, "team": team,
            "vs_top_wpct": wpct([r for r, (rk, _, _) in same if rk < cut]),
            "vs_battle_wpct": wpct([r for r, (rk, _, _) in same if cut <= rk <= cut + 2]),
            "vs_upper_wpct": wpct([r for r, (_, _, up) in same if up]),
            "vs_lower_wpct": wpct([r for r, (_, _, up) in same if not up]),
            "vs_near_net": sum(near) if near else None,   # 対戦がなければ 0 ではなく空
            "pair34_net": sum(pair) if pair else None,
            "half1_vs_pythag": _pythag_gap(rf[:half], ra[:half]),
            "half2_vs_pythag": _pythag_gap(rf[half:], ra[half:]),
            "max_win_streak": win_s, "max_lose_streak": lose_s,
        })
    schema = {"season": pl.Int32, "team": pl.Utf8, "vs_top_wpct": pl.Float64, "vs_battle_wpct": pl.Float64,
              "vs_upper_wpct": pl.Float64, "vs_lower_wpct": pl.Float64,
              "vs_near_net": pl.Int64, "pair34_net": pl.Int64, "half1_vs_pythag": pl.Float64, "half2_vs_pythag": pl.Float64,
              "max_win_streak": pl.Int64, "max_lose_streak": pl.Int64}
    out = st.select("season", "team", "league", "rank").join(pl.DataFrame(rows, schema=schema), on=["season", "team"], how="left")
    out = out.with_columns(focus_gap=pl.col("vs_battle_wpct") - pl.col("vs_top_wpct"))
    over = ["season", "league"]
    out = out.with_columns(**{f"{c}_d": pl.col(c) - (pl.col(c).sum().over(over) - pl.col(c)) / (pl.col(c).count().over(over) - 1)
                              for c in ("max_lose_streak", "vs_lower_wpct")})
    # 3位と4位の間で、相手（4位なら3位、3位なら4位。同率で複数いれば平均）との差
    is34 = pl.col("rank").is_in([3, 4])
    for c in ("vs_lower_wpct", "vs_battle_wpct", "focus_gap"):
        partner = out.filter(is34).group_by([*over, "rank"]).agg(pl.col(c).mean().alias("_m"))
        partner = partner.with_columns(rank=7 - pl.col("rank"))  # 3 ↔ 4
        out = out.join(partner, on=[*over, "rank"], how="left").with_columns(
            **{f"pair34_{c}_diff": pl.when(is34).then(pl.col(c) - pl.col("_m"))}).drop("_m")
    return out.drop("league", "rank")


def _vs_others(c: str, over=("season", "league")) -> pl.Expr:
    """同じ年・同じリーグの他球団の平均との差。比べる他球団がいなければ空（0 で割った値を残さない）。"""
    x, n = pl.col(c), pl.col(c).count().over(over)
    return pl.when(x.is_not_null() & (n > 1)).then(x - (x.sum().over(over) - x) / (n - 1))


def _wl_sums(pairs, cut: float) -> dict[str, float]:
    """(得点, 失点, 重み) の並びから、勝ち・負けの数と得点の和、点の少ない・多い試合の勝ち数と勝敗のついた数を足す。"""
    s = dict.fromkeys(("n_win", "rf_win", "n_loss", "rf_loss", "w_low", "d_low", "w_high", "d_high"), 0.0)
    for x, y, w in pairs:
        if x == y:
            continue
        side = "low" if x + y <= cut else "high"
        s[f"d_{side}"] += w
        if x > y:
            s["n_win"], s["rf_win"], s[f"w_{side}"] = s["n_win"] + w, s["rf_win"] + w * x, s[f"w_{side}"] + w
        else:
            s["n_loss"], s["rf_loss"] = s["n_loss"] + w, s["rf_loss"] + w * x
    return s


def win_loss_split(tg: pl.DataFrame) -> pl.DataFrame:
    """R20: 勝ち試合・負け試合の得点と、点の少ない試合・多い試合の勝率。

    見込みは、同じチーム・同じシーズンの得点と失点を、ホームとビジターそれぞれの中で組み合わせだけランダムにしたときの値
    （alloc_*_strat と同じ基準。球場の違いは組み合わせの中にとどまるので、係数は使わない）。点の数え上げで厳密に計算する。
      wl_rf_win / wl_rf_loss             : 勝ち試合・負け試合の得点／試合（実際）
      wl_rf_win_exp / wl_rf_loss_exp     : 同じ量の見込み（「この得点・失点の分布なら、勝つときは平均何点で勝つはずか」）
      wl_rf_win_gap / wl_rf_loss_gap     : 実際 − 見込み。勝ちで負なら勝ち試合は見込みより点が少ない（投手戦で勝った）、
                                           負けで正なら負け試合に見込みより多くの点が入った
      wl_wpct_low / wl_wpct_high         : 両チームの合計得点が、同じ年・同じリーグの試合の中央値以下／より多い試合の勝率
      wl_wpct_low_exp / _high_exp / _gap : その見込み（見込みの勝ち数 ÷ 見込みの勝敗のついた試合数）と、実際 − 見込み
    """
    tot = tg.with_columns(_t=pl.col("rf") + pl.col("ra")).group_by("season", "league").agg(pl.col("_t").median())
    cut = {(s, lg): m for s, lg, m in tot.iter_rows()}
    keys = (("rf_win", "rf_win", "n_win"), ("rf_loss", "rf_loss", "n_loss"),
            ("wpct_low", "w_low", "d_low"), ("wpct_high", "w_high", "d_high"))
    rows = []
    for (season, team), g in tg.group_by(["season", "team"], maintain_order=True):
        m = cut[(season, g["league"][0])]
        rf, ra, home = g["rf"].to_list(), g["ra"].to_list(), g["is_home"].to_list()
        exp_pairs = []
        for venue in (True, False):
            cx = Counter(x for x, h in zip(rf, home) if h == venue)
            cy = Counter(y for y, h in zip(ra, home) if h == venue)
            n = sum(cx.values())
            exp_pairs += [(x, y, cx[x] * cy[y] / n) for x in cx for y in cy]
        act, exp = _wl_sums([(x, y, 1.0) for x, y in zip(rf, ra)], m), _wl_sums(exp_pairs, m)
        row = {"season": season, "team": team}
        for name, num, den in keys:
            a = act[num] / act[den] if act[den] else None
            e = exp[num] / exp[den] if exp[den] else None
            row |= {f"wl_{name}": a, f"wl_{name}_exp": e, f"wl_{name}_gap": a - e if a is not None and e is not None else None}
        rows.append(row)
    schema = {"season": pl.Int32, "team": pl.Utf8,
              **{f"wl_{n}{s}": pl.Float64 for n, _, _ in keys for s in ("", "_exp", "_gap")}}
    return pl.DataFrame(rows, schema=schema)


def season_course(tg: pl.DataFrame, st: pl.DataFrame) -> pl.DataFrame:
    """R20: シーズンの前半と後半。各チームの試合数で半分に分ける（half1_vs_pythag と同じ分け方）。st には最終順位が要る。

      course_wpct_h1 / course_wpct_h2 : 前半・後半の勝率（引き分けを除く）。course_wpct_diff = 後半 − 前半（負なら後半に落ちた）
      course_rank_h1                  : 前半の勝率でのリーグ内の順位（ある日付の順位表ではなく、各チームの前半の試合だけで並べたもの）
      course_rank_q1 / course_rank_q3 : 同じく、各チームの試合数の 1/4・3/4 までの勝率での順位（順位の動きをたどるため）
      course_fade                     : 最終順位 − course_rank_h1（正なら、前半の位置より下で終わった）
      course_rf_d / course_ra_d       : （後半の得点／試合 − 前半の得点／試合）の、同じ年・同じリーグの他球団の平均との差。失点も同じ
                                        （季節による点の入りやすさの変化を他球団の平均で除く）
      course_ra_h1_d                  : 前半の失点／試合の、他球団の平均との差（後半の変化を、前半の水準からの戻りと分けて読むため）
      course_close_win_h1             : 前半の勝ちのうち、2点差以内の勝ちの割合
      course_close_win_h1_d           : その、他球団の平均との差（正なら、前半の勝ちが接戦に偏っていた）
    """
    def wpct(rf, ra):
        w, l_ = sum(x > y for x, y in zip(rf, ra)), sum(x < y for x, y in zip(rf, ra))
        return w / (w + l_) if w + l_ else None

    def change(v, half):
        return sum(v[half:]) / len(v[half:]) - sum(v[:half]) / len(v[:half]) if half and len(v) > half else None

    rows = []
    for (season, team), g in tg.sort("date").group_by(["season", "team"], maintain_order=True):
        rf, ra = g["rf"].to_list(), g["ra"].to_list()
        half = len(rf) // 2
        wins = [x - y for x, y in zip(rf[:half], ra[:half]) if x > y]
        q1, q3 = len(rf) // 4, len(rf) * 3 // 4
        rows.append({"season": season, "team": team, "_q1": wpct(rf[:q1], ra[:q1]), "_q3": wpct(rf[:q3], ra[:q3]),
                     "course_wpct_h1": wpct(rf[:half], ra[:half]), "course_wpct_h2": wpct(rf[half:], ra[half:]),
                     "_rf": change(rf, half), "_ra": change(ra, half), "_ra_h1": sum(ra[:half]) / half if half else None,
                     "course_close_win_h1": sum(m <= 2 for m in wins) / len(wins) if wins else None})
    schema = {"season": pl.Int32, "team": pl.Utf8, "_q1": pl.Float64, "_q3": pl.Float64,
              "course_wpct_h1": pl.Float64, "course_wpct_h2": pl.Float64,
              "_rf": pl.Float64, "_ra": pl.Float64, "_ra_h1": pl.Float64, "course_close_win_h1": pl.Float64}
    over = ["season", "league"]
    out = st.select("season", "team", "league", "rank").join(pl.DataFrame(rows, schema=schema), on=["season", "team"], how="left")
    rank = lambda c: pl.col(c).rank("min", descending=True).over(over).cast(pl.Int32)  # noqa: E731
    out = out.with_columns(course_wpct_diff=pl.col("course_wpct_h2") - pl.col("course_wpct_h1"),
                           course_rank_q1=rank("_q1"), course_rank_h1=rank("course_wpct_h1"), course_rank_q3=rank("_q3"))
    out = out.with_columns(course_fade=pl.col("rank") - pl.col("course_rank_h1"), course_rf_d=_vs_others("_rf"),
                           course_ra_d=_vs_others("_ra"), course_ra_h1_d=_vs_others("_ra_h1"),
                           course_close_win_h1_d=_vs_others("course_close_win_h1"))
    return out.drop("league", "rank", "_rf", "_ra", "_ra_h1", "_q1", "_q3")


TRAJ_MIN_GAMES = 10   # リーグの全球団がこの試合数に届いた日から線を引く（序盤の数試合の順位は揺れが大きすぎる）
TRAJ_SIMS = 200       # 力が一定のときの基準を作る、シーズンの作り直しの回数


def _inverse(a: list[list[float]]) -> list[list[float]]:
    """小さな正方行列の逆行列（部分ピボットつきのガウス・ジョルダン法）。"""
    n = len(a)
    m = [row[:] + [float(i == j) for j in range(n)] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        m[c] = [v / m[c][c] for v in m[c]]
        for r in range(n):
            if r != c and m[r][c]:
                f = m[r][c]
                m[r] = [v - f * w for v, w in zip(m[r], m[c])]
    return [row[n:] for row in m]


def cubic_projection(xs: list[float]) -> list[list[float]]:
    """3次式 y = c0 + c1·x + c2·x² + c3·x³ の最小二乗の係数を、y との掛け算1回で出す行列（4 × n）。"""
    pw = [[x ** k for x in xs] for k in range(4)]
    inv = _inverse([[sum(a * b for a, b in zip(pw[i], pw[j])) for j in range(4)] for i in range(4)])
    return [[sum(inv[i][k] * pw[k][t] for k in range(4)) for t in range(len(xs))] for i in range(4)]


def cubic_extrema(c: list[float], lo: float, hi: float = 1.0) -> list[tuple[float, str]]:
    """3次式の (lo, hi) の中の極大（peak）・極小（valley）を x の小さい順に。f'(x) = c1 + 2c2·x + 3c3·x² の根で、f'' の符号で分ける。"""
    a, b, d = 3 * c[3], 2 * c[2], c[1]
    if abs(a) > 1e-12:
        disc = b * b - 4 * a * d
        roots = sorted(((-b - math.sqrt(disc)) / (2 * a), (-b + math.sqrt(disc)) / (2 * a))) if disc > 0 else []
    else:
        roots = [-d / b] if abs(b) > 1e-12 else []
    return [(r, "peak" if 2 * c[2] + 6 * c[3] * r < 0 else "valley") for r in roots if lo < r < hi]


def _shape(c: list[float], lo: float) -> dict:
    ext = cubic_extrema(c, lo)
    mid = (lo + 1) / 2
    slope_mid = c[1] + 2 * c[2] * mid + 3 * c[3] * mid * mid
    shape = "-".join(k for _, k in ext) or ("flat" if abs(slope_mid) < 1e-9 else "rise" if slope_mid > 0 else "fall")
    peaks = [x for x, k in ext if k == "peak"]
    return {"shape": shape, "peak": bool(peaks), "peak_x": peaks[0] if peaks else None,
            "valley": any(k == "valley" for _, k in ext), "end_slope": c[1] + 2 * c[2] + 3 * c[3]}


WAVE_DECAYS = (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0)  # 減衰の速さ λ（横軸1つ分 = 1シーズンあたり）。0 は減衰しない
WAVE_PERIODS = (None, 2.0, 1.0, 0.75, 0.5, 1 / 3, 0.25)    # 波の周期（シーズンの何割で1周するか）。None は波なし
WAVE_SETTLE = 0.5                                          # ゆれの幅が半順位を下回ったら「順位が決まった」とみなす


def wave_basis(xs: list[float]) -> list[dict]:
    """減衰する波 h(x) = L + e^(−λt)·((h0 − L)·cos ωt + B·sin ωt)（t = x − 線の始まり）を当てるための、格子ごとの量。

    h0 は線の始まり（全球団が決めた試合数に届いた日）の値そのもので、当てはめで動かさない（切片を置かない）。
    λ と周期は格子から選び、L（収束する先）と B（始まりの傾きを決める量）は最小二乗で決める。どの格子でも連続で微分できる。
    """
    t = [x - xs[0] for x in xs]
    # 同じ当てはまりなら簡単なほうを選ぶ順: 波なしで近づく → 減衰する波 → 減衰しない波（始まりの値のまま動かない線は候補にしない）
    grid = ([(lam, None) for lam in WAVE_DECAYS if lam > 0]
            + [(lam, per) for lam in WAVE_DECAYS if lam > 0 for per in WAVE_PERIODS if per]
            + [(0.0, per) for per in WAVE_PERIODS if per])
    out = []
    for lam, per in grid:
        w = 2 * math.pi / per if per else 0.0
        ec = [math.exp(-lam * u) * math.cos(w * u) for u in t]
        es = [math.exp(-lam * u) * math.sin(w * u) for u in t]
        sec, sec2, sese = sum(ec), sum(e * e for e in ec), sum(a * b for a, b in zip(ec, es))
        out.append({"lam": lam, "per": per, "w": w, "ec": ec, "es": es, "sec": sec, "sec2": sec2, "sese": sese,
                    "uu": len(t) - 2 * sec + sec2, "uv": sum(es) - sese, "vv": sum(e * e for e in es)})
    return out


def wave_fit(ys: list[float], basis: list[dict], x0: float) -> dict:
    """wave_basis の格子から、誤差の2乗和が最も小さい減衰する波を選ぶ。

    返り値: limit（x → ∞ で収束する先 L。λ = 0 なら収束しないので空）、end（最後の日 x = 1 の値）、decay（λ）、
    period（周期。波がなければ空）、settle_x（ゆれの幅 e^(−λt)·√((h0 − L)² + B²) が WAVE_SETTLE を下回る位置。
    1 を超えればシーズン中には決まらない。減衰しなければ空）、rmse
    """
    h0, n = ys[0], len(ys)
    sy, sy2 = sum(ys), sum(y * y for y in ys)
    best = None
    for b in basis:
        ech = sum(map(operator.mul, b["ec"], ys))
        ur = sy - h0 * b["sec"] - ech + h0 * b["sec2"]          # Σ u·r（u = 1 − e·cos、r = y − h0·e·cos）
        rr = sy2 - 2 * h0 * ech + h0 * h0 * b["sec2"]            # Σ r²
        if b["per"] is None:
            if b["uu"] <= 1e-12:
                continue
            lim, bb = ur / b["uu"], 0.0
            sse = rr - lim * ur
        else:
            vr = sum(map(operator.mul, b["es"], ys)) - h0 * b["sese"]   # Σ v·r（v = e·sin）
            det = b["uu"] * b["vv"] - b["uv"] ** 2
            if det <= 1e-12:
                continue
            lim, bb = (b["vv"] * ur - b["uv"] * vr) / det, (b["uu"] * vr - b["uv"] * ur) / det
            sse = rr - lim * ur - bb * vr
        if best is None or sse < best[0] - 1e-12:
            best = (sse, b, lim, bb)
    sse, b, lim, bb = best
    amp, t1 = math.hypot(h0 - lim, bb), 1 - x0
    if amp <= WAVE_SETTLE:
        settle = x0
    else:
        settle = x0 + math.log(amp / WAVE_SETTLE) / b["lam"] if b["lam"] > 0 else None
    end = lim + math.exp(-b["lam"] * t1) * ((h0 - lim) * math.cos(b["w"] * t1) + bb * math.sin(b["w"] * t1))
    return {"limit": lim if b["lam"] > 0 else None, "end": end, "decay": b["lam"], "period": b["per"],
            "settle_x": settle, "rmse": math.sqrt(max(sse, 0.0) / n)}


def _season_paths(days: list[list[tuple]], grid: dict, winners: list) -> dict:
    """1シーズン分の試合（日付順。各日 [(試合の番号, ホーム, ビジター), ...]）と各試合の勝者（引き分けは None）から、
    各球団の「順位の高さ」（リーグの球団数 + 1 − 順位）と貯金（勝 − 敗）を、そのリーグの線を引く日ごとに並べる。"""
    w, l_ = Counter(), Counter()
    paths = {t: ([], []) for info in grid.values() for t in info["teams"]}
    for i, games in enumerate(days):
        for g, home, away in games:
            if winners[g] is not None:
                w[winners[g]] += 1
                l_[away if winners[g] == home else home] += 1
        for info in grid.values():
            if i in info["index"]:
                pct = {t: w[t] / (w[t] + l_[t]) if w[t] + l_[t] else 0.5 for t in info["teams"]}
                for t in info["teams"]:
                    paths[t][0].append(len(pct) - sum(p > pct[t] for p in pct.values()))  # 順位 = 1 + 上にいる球団の数
                    paths[t][1].append(w[t] - l_[t])
    return paths


def season_trajectory(tg: pl.DataFrame, sims: int = TRAJ_SIMS, min_games: int = TRAJ_MIN_GAMES) -> pl.DataFrame:
    """R22: シーズンの中の順位と貯金の線を3次式でならし、山（極大）と谷（極小）があるかを見る。

    横軸は日付（そのリーグの最初の試合の日 0 〜 最後の試合の日 1）。リーグの全球団が min_games 試合に届いた日から最後の日まで、
    そのリーグの試合のあった日ごとの値に3次式を最小二乗で当てる。カクカクした日ごとの線を、なめらかな式に置き換えて形を読むため。
      traj_start_games / traj_start_x / traj_start_date : 線の始まり（全球団が何試合に届いた日からか、その位置と日付）
      traj_rank_* : 順位の高さ（6球団なら 1位 = 6、6位 = 1。上がれば正）  traj_wl_* : 貯金（勝 − 敗）
      *_shape     : 線の形。rise / fall（山も谷もない）、peak（山）、valley（谷）、peak-valley / valley-peak（両方、起きた順）
      *_peak / *_peak_x : 線を引いた範囲の内側に山があるか / その位置（0〜1）。*_valley は谷があるか
      *_end_slope : 最後の日の傾き f'(1)（横軸1つ分 = 1シーズン分あたりの変化。順位の高さなら何位分、貯金なら何勝分）
      *_peak_base / *_valley_base : 力が一定（その年の勝率）でも山・谷ができる割合。実際の日程のまま、引き分けでない試合の勝敗を
                    両チームの勝率の Log5 で引き直したシーズンを sims 回作り、同じ線の引き方で数える（乱数の種は年で固定）
    山や谷は、力が一定でも順位や貯金のゆらぎだけでできる。読むときは必ず *_base と比べる。
      traj_rank_rmse : 順位の高さの線と3次式の差の大きさ（2乗平均の平方根、順位の単位）
    R23: 順位の高さの線に、始まりの値から出発して減衰する波（wave_fit）を当てる。順位の単位に直して:
      wave_limit_rank : 線が収束する先の順位（減衰しなければ空）  wave_end_rank : 最後の日の値  wave_decay : λ
      wave_period     : 波の周期（波がなければ空）  wave_osc : 波があるか  wave_rmse : 当てはまりの差の大きさ
      wave_settle_x   : 順位が決まった位置（ゆれの幅が半順位を下回る。1 を超えればシーズン中には決まっていない）
      wave_settle_pct : 力が一定のシーズンのうち、決まった位置が実際より早かった割合（同じなら半分数える。小さいほど実際が早い）
      wave_osc_base   : 力が一定のシーズンのうち、波のある式が選ばれた割合
    """
    league_of = {(s, t): lg for s, t, lg in tg.select("season", "team", "league").unique().iter_rows()}
    rows = []
    for (season,), sg in tg.filter(pl.col("is_home")).sort("date").group_by(["season"], maintain_order=True):
        dates = sorted(set(sg["date"].to_list()))
        day = {d: i for i, d in enumerate(dates)}
        days, winners, pairs = [[] for _ in dates], [], []
        for g, (d, home, away, hs, as_) in enumerate(sg.select("date", "team", "opp", "rf", "ra").iter_rows()):
            days[day[d]].append((g, home, away))
            winners.append(home if hs > as_ else away if as_ > hs else None)
            pairs.append((home, away))
        wins, losses = Counter(), Counter()
        for win, (home, away) in zip(winners, pairs):
            if win is not None:
                wins[win] += 1
                losses[away if win == home else home] += 1
        teams = sorted({t for pr in pairs for t in pr})
        pct = {t: wins[t] / (wins[t] + losses[t]) if wins[t] + losses[t] else 0.5 for t in teams}
        grid, proj, waves = {}, {}, {}
        for lg in sorted({league_of[(season, t)] for t in teams}):
            members = [t for t in teams if league_of[(season, t)] == lg]
            lg_days = [i for i, games in enumerate(days) if any(h in members or a in members for _, h, a in games)]
            played, start = Counter(), None
            for i, games in enumerate(days):
                for _, h, a in games:
                    played[h] += 1
                    played[a] += 1
                if all(played[t] >= min_games for t in members):
                    start = i
                    break
            if start is None or start >= lg_days[-1]:
                continue
            o = {i: date.fromisoformat(dates[i]).toordinal() for i in lg_days}
            idx = [i for i in lg_days if i >= start]
            xs = [(o[i] - o[lg_days[0]]) / (o[lg_days[-1]] - o[lg_days[0]]) for i in idx]
            grid[lg] = {"teams": members, "index": set(idx), "lo": xs[0], "xs": xs, "date": dates[idx[0]]}
            proj[lg], waves[lg] = cubic_projection(xs), wave_basis(xs)
        if not grid:
            continue

        def fit(paths):
            out = {}
            for lg, info in grid.items():
                for t in info["teams"]:
                    rk, wl = paths[t]
                    cr, cw = ([sum(map(operator.mul, row, path)) for row in proj[lg]] for path in (rk, wl))
                    out[t] = (_shape(cr, info["lo"]), _shape(cw, info["lo"]), wave_fit(rk, waves[lg], info["lo"]), cr)
            return out

        actual = fit(_season_paths(days, grid, winners))
        rng, base, settles = random.Random(season * 1000 + 22), Counter(), {t: [] for t in actual}
        for _ in range(sims):
            sim = [None if win is None else (h if rng.random() < log5(pct[h], pct[a]) else a)
                   for win, (h, a) in zip(winners, pairs)]
            for t, (rk, wl, wv, _) in fit(_season_paths(days, grid, sim)).items():
                for name, s_ in (("rank", rk), ("wl", wl)):
                    base[(t, name, "peak")] += s_["peak"]
                    base[(t, name, "valley")] += s_["valley"]
                base[(t, "wave", "osc")] += wv["period"] is not None
                settles[t].append(math.inf if wv["settle_x"] is None else wv["settle_x"])
        paths = _season_paths(days, grid, winners)
        for lg, info in grid.items():
            n_teams = len(info["teams"])
            for t in info["teams"]:
                rk, wl, wv, cr = actual[t]
                row = {"season": season, "team": t, "traj_start_games": min_games, "traj_start_x": info["lo"],
                       "traj_start_date": info["date"]}
                for name, s_ in (("rank", rk), ("wl", wl)):
                    row |= {f"traj_{name}_{k}": v for k, v in s_.items()}
                    row |= {f"traj_{name}_{k}_base": base[(t, name, k)] / sims if sims else None for k in ("peak", "valley")}
                fitted = [cr[0] + cr[1] * x + cr[2] * x * x + cr[3] * x ** 3 for x in info["xs"]]
                row["traj_rank_rmse"] = math.sqrt(sum((y - f) ** 2 for y, f in zip(paths[t][0], fitted)) / len(fitted))
                mine = math.inf if wv["settle_x"] is None else wv["settle_x"]
                row |= {"wave_limit_rank": None if wv["limit"] is None else n_teams + 1 - wv["limit"],
                        "wave_end_rank": n_teams + 1 - wv["end"], "wave_decay": wv["decay"], "wave_period": wv["period"],
                        "wave_osc": wv["period"] is not None, "wave_settle_x": wv["settle_x"], "wave_rmse": wv["rmse"],
                        "wave_settle_pct": (sum(v < mine for v in settles[t]) + 0.5 * sum(v == mine for v in settles[t]))
                        / sims if sims else None,
                        "wave_osc_base": base[(t, "wave", "osc")] / sims if sims else None}
                rows.append(row)
    schema = {"season": pl.Int32, "team": pl.Utf8, "traj_start_games": pl.Int64, "traj_start_x": pl.Float64,
              "traj_start_date": pl.Utf8}
    for name in ("rank", "wl"):
        schema |= {f"traj_{name}_shape": pl.Utf8, f"traj_{name}_peak": pl.Boolean, f"traj_{name}_peak_x": pl.Float64,
                   f"traj_{name}_valley": pl.Boolean, f"traj_{name}_end_slope": pl.Float64,
                   f"traj_{name}_peak_base": pl.Float64, f"traj_{name}_valley_base": pl.Float64}
    schema |= {"traj_rank_rmse": pl.Float64, "wave_limit_rank": pl.Float64, "wave_end_rank": pl.Float64,
               "wave_decay": pl.Float64, "wave_period": pl.Float64, "wave_osc": pl.Boolean, "wave_settle_x": pl.Float64,
               "wave_rmse": pl.Float64, "wave_settle_pct": pl.Float64, "wave_osc_base": pl.Float64}
    return pl.DataFrame(rows, schema=schema)


def log5(p: float, q: float) -> float:
    """勝率 p のチームが勝率 q のチームに勝つ見込み（Log5）。リーグ平均 .500 を基準にした形。"""
    d = p + q - 2 * p * q
    return 0.5 if d == 0 else (p - p * q) / d


def _pythag_wpct(rf: int, ra: int) -> float | None:
    if rf <= 0 and ra <= 0:
        return None
    return 1 / (1 + (ra / rf) ** K_FIXED) if rf > 0 else 0.0


def _pair34_diff(out: pl.DataFrame, cols: list[str]) -> pl.DataFrame:
    """3位と4位の間で、相手（4位なら3位、3位なら4位。同率で複数いれば平均）との差。他の順位は空。"""
    over = ["season", "league"]
    is34 = pl.col("rank").is_in([3, 4])
    for c in cols:
        partner = out.filter(is34).group_by([*over, "rank"]).agg(pl.col(c).mean().alias("_m"))
        partner = partner.with_columns(rank=7 - pl.col("rank"))  # 3 ↔ 4
        out = out.join(partner, on=[*over, "rank"], how="left").with_columns(
            **{f"pair34_{c}_diff": pl.when(is34).then(pl.col(c) - pl.col("_m"))}).drop("_m")
    return out


def opponent_adjusted(tg: pl.DataFrame, st: pl.DataFrame) -> pl.DataFrame:
    """R15・R16: 相手の強さから見込まれる勝ち数・得点・失点との差を、相手のグループごとに足す。

    リーグ内の相手だけ（交流戦は外す）。相手 O との試合の見込みは、
      自分の強さ  = O との試合を除いた自分の得点・失点からのピタゴラス勝率
      相手の強さ  = 自分との試合を除いた O の得点・失点からのピタゴラス勝率
      見込み      = Log5(自分の強さ, 相手の強さ)
    O との（勝 − 見込みの勝ち数 × (勝 + 敗)）を、O の強さ（自分との試合を除く）で並べたグループごとに足す。
      opp_adj_top : 強いほうから2チーム   opp_adj_mid : その次の2チーム   opp_adj_low : 残り（6球団なら1チーム）
      opp_adj_total : リーグ内の相手すべて
    相手の強さを最終順位で決めないので、自分との対戦結果が相手のグループ分けを動かすことはない。

    R16: 得点・失点の側に分ける（1試合あたりの得点の見込み = 自分の得点力 × 相手の失点の多さ ÷ リーグ平均）。
      opp_rf_gap_* : 実際の得点 − 見込みの得点（O との試合を除いた自分の得点/試合 × 自分との試合を除いた O の失点/試合 ÷ リーグ平均 × 試合数）
      opp_ra_gap_* : 見込みの失点 − 実際の失点（同じ形。正なら見込みより失点が少ない）
      opp_conv_*   : 勝 − (勝 + 敗) × ピタゴラス(その相手との実際の得点, 失点)。点の差では説明できない勝ち負け
      opp_top_rf_minus_ra : opp_rf_gap_top − opp_ra_gap_top（負なら、強い相手との差は得点の側に大きい）
      リーグ平均 = そのリーグの球団の得点の合計 ÷ 試合数の合計（交流戦も含む全試合。強さの計算と同じ）
    """
    league_of = {(r["season"], r["team"]): r["league"] for r in st.iter_rows(named=True)}
    tot: dict[tuple, list[int]] = {}  # (season, team) -> [rf, ra, games]
    vs: dict[tuple, list[int]] = {}  # (season, team, opp) -> [rf, ra, w, l, games]
    for r in tg.iter_rows(named=True):
        t = tot.setdefault((r["season"], r["team"]), [0, 0, 0])
        t[0], t[1], t[2] = t[0] + r["rf"], t[1] + r["ra"], t[2] + 1
        v = vs.setdefault((r["season"], r["team"], r["opp"]), [0, 0, 0, 0, 0])
        v[0] += r["rf"]
        v[1] += r["ra"]
        v[2] += r["rf"] > r["ra"]
        v[3] += r["rf"] < r["ra"]
        v[4] += 1
    lg: dict[tuple, list[int]] = {}
    for (season, team), (rf, _, g) in tot.items():
        a = lg.setdefault((season, league_of[(season, team)]), [0, 0])
        a[0], a[1] = a[0] + rf, a[1] + g
    groups = {"top": slice(0, 2), "mid": slice(2, 4), "low": slice(4, None)}
    rows = []
    for (season, team), (rf, ra, g) in tot.items():
        league = league_of[(season, team)]
        lg_rpg = lg[(season, league)][0] / lg[(season, league)][1]
        opps = [o for (s_, t_, o) in vs if s_ == season and t_ == team and league_of.get((season, o)) == league]
        parts = []
        for o in opps:
            orf, ora, w, l_, n = vs[(season, team, o)]
            o_rf, o_ra, o_g = tot[(season, o)]
            me = _pythag_wpct(rf - orf, ra - ora)
            them = _pythag_wpct(o_rf - ora, o_ra - orf)  # O の得点 − 自分から取った分、O の失点 − 自分が取った分
            if me is None or them is None or g == n or o_g == n:
                continue
            exp_rf = n * ((rf - orf) / (g - n)) * ((o_ra - orf) / (o_g - n)) / lg_rpg
            exp_ra = n * ((o_rf - ora) / (o_g - n)) * ((ra - ora) / (g - n)) / lg_rpg
            actual = _pythag_wpct(orf, ora)
            parts.append({"them": them, "adj": w - (w + l_) * log5(me, them), "rf_gap": orf - exp_rf, "ra_gap": exp_ra - ora,
                          "conv": w - (w + l_) * actual if actual is not None else 0.0})
        parts.sort(key=lambda x: -x["them"])
        row = {"season": season, "team": team, "opp_adj_total": sum(x["adj"] for x in parts) if parts else None}
        for name, sl in groups.items():
            sel = parts[sl]
            for key, col in (("adj", "opp_adj"), ("rf_gap", "opp_rf_gap"), ("ra_gap", "opp_ra_gap"), ("conv", "opp_conv")):
                row[f"{col}_{name}"] = sum(x[key] for x in sel) if sel else None
        rows.append(row)
    cols = ["opp_adj_total"] + [f"{c}_{g}" for c in ("opp_adj", "opp_rf_gap", "opp_ra_gap", "opp_conv") for g in groups]
    schema = {"season": pl.Int32, "team": pl.Utf8, **{c: pl.Float64 for c in cols}}
    out = st.select("season", "team", "league", "rank").join(pl.DataFrame(rows, schema=schema), on=["season", "team"], how="left")
    out = out.with_columns(opp_top_rf_minus_ra=pl.col("opp_rf_gap_top") - pl.col("opp_ra_gap_top"))
    # 見込みの式は相手のグループで偏る（強い相手には全球団平均で +7点ほど多く取れる形になる）。
    # 同じ年・同じリーグの全球団の平均を引いた値も出す（R16 の自分への異議から）
    over = ["season", "league"]
    out = out.with_columns(**{f"{c}_c": pl.col(c) - pl.col(c).mean().over(over)
                              for c in (f"opp_{k}_gap_{g}" for k in ("rf", "ra") for g in groups)})
    # 得点の差と失点の差を、2本の軸に回す（R17）。
    #   net : 得点の差 + 失点の差（どちらが多く取ったか。正なら自分が見込みより多く上回った）
    #   env : 得点の差 − 失点の差（試合全体の点の多さ。負なら両方とも点の入りにくい試合だった）
    out = out.with_columns(**{f"opp_net_gap_{g}_c": pl.col(f"opp_rf_gap_{g}_c") + pl.col(f"opp_ra_gap_{g}_c") for g in groups},
                           **{f"opp_env_gap_{g}_c": pl.col(f"opp_rf_gap_{g}_c") - pl.col(f"opp_ra_gap_{g}_c") for g in groups})
    return _pair34_diff(out, ["opp_adj_top", "opp_adj_mid", "opp_adj_low", "opp_adj_total"]).drop("league", "rank")


def streak(st: pl.DataFrame, cond: pl.Expr, name: str) -> pl.DataFrame:
    """条件が、そのシーズンまで何年続けて成り立っているか（同じチーム、連続した年）。成り立たなければ 0、値が空なら空。"""
    flags = st.select("team", "season", f=cond)
    by = {(r["team"], r["season"]): r["f"] for r in flags.iter_rows(named=True)}
    out = []
    for (team, season), f in sorted(by.items()):
        if f is None:
            n = None
        elif not f:
            n = 0
        else:
            prev = out[-1][2] if out and out[-1][0] == team and out[-1][1] == season - 1 else None
            n = (prev or 0) + 1
        out.append((team, season, n))
    tbl = pl.DataFrame(out, schema={"team": pl.Utf8, "season": pl.Int32, name: pl.Int64}, orient="row")
    return st.join(tbl, on=["team", "season"], how="left")


def add_persistence(st: pl.DataFrame) -> pl.DataFrame:
    """R14: 低いままの状態が何年続いているか。

      inn_size_rank        : 得点した回の大きさ（inn_dlog_size）のリーグ内の順位（小さいほうが 1）
      inn_size_low_streak  : inn_size_rank が 2 以下の年が、その年まで何年続いているか
      rf_low_streak        : 得点のリーグ順位が 5 位以下の年が、その年まで何年続いているか
    """
    if "inn_dlog_size" in st.columns:
        st = st.with_columns(inn_size_rank=pl.col("inn_dlog_size").rank("min").over(["season", "league"]).cast(pl.Int32))
        st = streak(st, pl.col("inn_size_rank") <= 2, "inn_size_low_streak")
    return streak(st, pl.col("rank_rf") >= 5, "rf_low_streak")


def _spread(col: pl.Expr, name: str) -> list[pl.Expr]:
    return [
        col.median().alias(f"{name}_median"),
        col.drop_nulls().mode().min().alias(f"{name}_mode"),
        (col.quantile(0.75, "linear") - col.quantile(0.25, "linear")).alias(f"{name}_iqr"),
    ]


def season_table(tg: pl.DataFrame, trajectory: dict | None = None) -> pl.DataFrame:
    m = pl.col("rf") - pl.col("ra")
    win, loss, margin = m > 0, m < 0, m.abs()
    bins = []
    for b in BINS:
        hit = margin >= b if b == BINS[-1] else margin == b
        tag = f"{b}plus" if b == BINS[-1] else str(b)
        bins += [(win & hit).sum().alias(f"w_{tag}"), (loss & hit).sum().alias(f"l_{tag}")]

    base = tg.group_by("season", "team", maintain_order=True).agg(
        pl.first("team_name"), pl.first("league"),
        pl.len().alias("G"), win.sum().alias("W"), loss.sum().alias("L"), (m == 0).sum().alias("T"),
        pl.sum("rf").alias("RF"), pl.sum("ra").alias("RA"),
        *bins,
        *_spread(margin.filter(win), "win_margin"), *_spread(margin.filter(loss), "loss_margin"),
        *_spread(pl.col("rf"), "rf"), *_spread(pl.col("ra"), "ra"),
        m.filter(pl.col("is_home")).mean().alias("rd_home_g"), m.filter(~pl.col("is_home")).mean().alias("rd_away_g"),
    )
    W, L, RF, RA, G = (pl.col(c) for c in ("W", "L", "RF", "RA", "G"))
    log_ratio = (RF / RA).log()
    logit = (pl.col("wpct") / (1 - pl.col("wpct"))).log()
    st = (
        base.with_columns(wpct=W / (W + L), k_var=((RF + RA) / G) ** PYTHAGENPAT_EXP,
                          wpct_1run=pl.col("w_1") / (pl.col("w_1") + pl.col("l_1")),
                          wpct_2run=pl.col("w_2") / (pl.col("w_2") + pl.col("l_2")))
        .with_columns(
            pythag_fixed=1 / (1 + (RA / RF) ** K_FIXED),
            pythag_var=1 / (1 + (RA / RF) ** pl.col("k_var")),
            logit_resid=logit - K_FIXED * log_ratio,
            k_eff=pl.when(log_ratio.abs() >= 0.02).then(logit / log_ratio),
        )
        .with_columns(resid_fixed=pl.col("wpct") - pl.col("pythag_fixed"),
                      resid_var=pl.col("wpct") - pl.col("pythag_var"))
    )
    st = add_explanatory(add_rank(st))
    st = st.join(allocation_table(tg), on=["season", "team"], how="left")
    st = st.join(scoring_deficit(tg), on=["season", "team"], how="left")
    st = st.join(rank_probability(tg), on=["season", "team"], how="left")
    st = st.join(boundary_features(tg, st), on=["season", "team"], how="left")
    st = st.join(opponent_adjusted(tg, st), on=["season", "team"], how="left")
    st = st.join(win_loss_split(tg), on=["season", "team"], how="left")
    st = st.join(season_course(tg, st), on=["season", "team"], how="left")
    traj = trajectory or {}  # 分析設定の [trajectory]（線の始まりの試合数・力が一定のシーズンの作り直しの回数）
    st = st.join(season_trajectory(tg, sims=int(traj.get("sims", TRAJ_SIMS)),
                                   min_games=int(traj.get("min_games", TRAJ_MIN_GAMES))), on=["season", "team"], how="left")
    return st.sort("season", "league", "rank", "team")


def add_rank(st: pl.DataFrame) -> pl.DataFrame:
    """リーグ内の勝率順位。公式の順位決定方法（同率時の規定）は再現しないので、同率には印をつける。"""
    over = ["season", "league"]
    out = st.with_columns(
        rank=pl.col("wpct").rank("min", descending=True).over(over).cast(pl.Int32),
        rank_tie=(pl.col("wpct").count().over([*over, "wpct"]) > 1),
        league_size=pl.len().over(over).cast(pl.Int32),
    )
    return out.with_columns(upper_half=pl.col("rank") <= pl.col("league_size") / 2)


def add_explanatory(st: pl.DataFrame) -> pl.DataFrame:
    """命題の判定に使う、得失点から見た「期待」の列。2列の比較は必ずここで列にして見える形にする。"""
    over = ["season", "league"]
    r = lambda col, desc: pl.col(col).rank("min", descending=desc).over(over).cast(pl.Int32)  # noqa: E731
    return (
        st.with_columns(rd=pl.col("RF") - pl.col("RA"))
        .with_columns(rank_pythag=r("pythag_fixed", True), rank_rf=r("RF", True),
                      rank_ra=r("RA", False), rank_rd=r("rd", True),
                      wins_vs_pythag=pl.col("W") - (pl.col("W") + pl.col("L")) * pl.col("pythag_fixed"))
        .with_columns(rank_gap=pl.col("rank") - pl.col("rank_pythag"),
                      one_run_net=pl.col("w_1").cast(pl.Int64) - pl.col("l_1").cast(pl.Int64),
                      two_run_net=pl.col("w_2").cast(pl.Int64) - pl.col("l_2").cast(pl.Int64),
                      blowout_net=pl.col("w_4plus").cast(pl.Int64) - pl.col("l_4plus").cast(pl.Int64),
                      rank_wpct_1run=r("wpct_1run", True),
                      home_away_gap=pl.col("rd_home_g") - pl.col("rd_away_g"))
        .with_columns(home_away_gap_vs_league=pl.col("home_away_gap")
                      - (pl.col("home_away_gap").sum().over(over) - pl.col("home_away_gap"))
                      / (pl.len().over(over) - 1))
    )


def load_config(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="観測データセットからチーム×シーズンの指標を作る")
    ap.add_argument("--games", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True, help="分析設定（[teams] を含む TOML）")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--innings", type=Path, help="イニング単位の集計（CSV / CSV.gz、R4）。あれば inn_* の列を加える")
    ap.add_argument("--batting", type=Path, help="チーム打撃成績の観測（JSONL、R6）。あれば bat_* の率を加える")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    st = season_table(to_team_games(pl.read_ndjson(args.games), cfg["teams"]), trajectory=cfg.get("trajectory"))
    if args.innings:
        raw = pl.read_csv(args.innings)
        if "year" in raw.columns:  # PR #3 の形式: year, team, venue, role, window, ...
            raw = raw.filter(pl.col("role") == "off").rename({"year": "season"})
        st = inning_decomposition(st, raw.with_columns(pl.col("season").cast(pl.Int32)))
    if args.batting:
        st = batting_join(st, pl.read_ndjson(args.batting))
    st = add_persistence(st)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    st.write_ndjson(args.out)
    focus = cfg.get("focus", {}).get("team")
    if focus:
        pl.Config.set_tbl_rows(40).set_tbl_cols(20).set_float_precision(3)
        print(st.filter(pl.col("team") == focus).select(
            "season", "rank", "rank_tie", "W", "L", "T", "wpct", "pythag_fixed", "resid_fixed",
            "logit_resid", "wpct_1run", "wpct_2run").sort("season"))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
