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
import sys
import tomllib
from collections import Counter
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


def _spread(col: pl.Expr, name: str) -> list[pl.Expr]:
    return [
        col.median().alias(f"{name}_median"),
        col.drop_nulls().mode().min().alias(f"{name}_mode"),
        (col.quantile(0.75, "linear") - col.quantile(0.25, "linear")).alias(f"{name}_iqr"),
    ]


def season_table(tg: pl.DataFrame) -> pl.DataFrame:
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
    st = season_table(to_team_games(pl.read_ndjson(args.games), cfg["teams"]))
    if args.innings:
        raw = pl.read_csv(args.innings)
        if "year" in raw.columns:  # PR #3 の形式: year, team, venue, role, window, ...
            raw = raw.filter(pl.col("role") == "off").rename({"year": "season"})
        st = inning_decomposition(st, raw.with_columns(pl.col("season").cast(pl.Int32)))
    if args.batting:
        st = batting_join(st, pl.read_ndjson(args.batting))
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
