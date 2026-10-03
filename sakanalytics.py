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
  inn_*（--innings があるとき）     イニング単位の集計からの列（R4）。inn_I/S/R: 攻撃回数・得点した回の数・得点
    inn_dlog_rpi/_freq/_size       log(得点/回)・log(得点した回の割合)・log(得点した回の平均得点) の、他球団平均との差
    inn_freq_minus_size            inn_dlog_freq − inn_dlog_size（負なら、頻度の不足が大きさの不足より大きい）
    *_6                            双方が6回まで攻撃した試合の1〜6回だけで同じ計算
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


SCORING_BANDS = {"floor": (1, 2), "mid": (3, 5), "ceiling": (6, None)}  # k の範囲（k 点以上取れたか）


def scoring_deficit(tg: pl.DataFrame) -> pl.DataFrame:
    """得点の差を、どの得点帯で生まれたかに分ける（R3）。

    1試合の平均得点 = Σ_{k≥1} P(得点 ≥ k)。同じ年・同じリーグの他球団の P(得点 ≥ k) の平均との差を
    k ごとに取り、帯ごとに足す。帯の合計は「得点／試合 − 他球団の得点／試合の平均」にちょうど一致する。
      rf_def_floor   : k = 1〜2（0〜2点に抑えられる試合の多さ）
      rf_def_mid     : k = 3〜5
      rf_def_ceiling : k ≥ 6（大量得点の少なさ）
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
    return t.with_columns(rf_def_floor_minus_ceiling=pl.col("rf_def_floor") - pl.col("rf_def_ceiling"))


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
    for window, tag in (("all", ""), ("first6", "_6")):
        w = innings.filter(pl.col("window") == window).select(
            "season", "team", pl.col("games").alias("_g"), pl.col("innings").alias(f"inn_I{tag}"),
            pl.col("runs").alias("_r"), pl.col("scoring_innings").alias(f"inn_S{tag}"))
        if window == "all":
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
    return out


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
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    st = season_table(to_team_games(pl.read_ndjson(args.games), cfg["teams"]))
    if args.innings:
        raw = pl.read_csv(args.innings)
        if "year" in raw.columns:  # PR #3 の形式: year, team, venue, role, window, ...
            raw = raw.filter((pl.col("venue") == "all") & (pl.col("role") == "off")).rename({"year": "season"})
        st = inning_decomposition(st, raw.with_columns(pl.col("season").cast(pl.Int32)))
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
