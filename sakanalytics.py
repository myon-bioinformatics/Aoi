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
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

import polars as pl

K_FIXED = 1.83
PATENPAT_EXP = 0.287
BINS = (1, 2, 3, 4)  # 4 は「4点以上」


def to_team_games(games: pl.DataFrame, teams: dict[str, dict]) -> pl.DataFrame:
    """1試合1行 → 両チーム視点の2行。teams = {code: {"name": .., "league": ..}}。"""
    unknown = (set(games["home"]) | set(games["away"])) - set(teams)
    if unknown:  # 黙って捨てない
        raise ValueError(f"teams に定義のないチーム: {sorted(unknown)}")
    home = games.select("date", team="home", opp="away", rf="hs", ra="as")
    away = games.select("date", team="away", opp="home", rf="as", ra="hs")
    return (
        pl.concat([home, away])
        .with_columns(
            season=pl.col("date").str.slice(0, 4).cast(pl.Int32),
            league=pl.col("team").replace_strict({k: v["league"] for k, v in teams.items()}),
            team_name=pl.col("team").replace_strict({k: v["name"] for k, v in teams.items()}),
        )
        .sort("date", "team")
    )


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
    )
    W, L, RF, RA, G = (pl.col(c) for c in ("W", "L", "RF", "RA", "G"))
    log_ratio = (RF / RA).log()
    logit = (pl.col("wpct") / (1 - pl.col("wpct"))).log()
    st = (
        base.with_columns(wpct=W / (W + L), k_var=((RF + RA) / G) ** PATENPAT_EXP,
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
    return add_explanatory(add_rank(st)).sort("season", "league", "rank", "team")


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
        .with_columns(rank_gap=pl.col("rank") - pl.col("rank_pythag"))
    )


def load_config(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="観測データセットからチーム×シーズンの指標を作る")
    ap.add_argument("--games", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True, help="分析設定（[teams] を含む TOML）")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    st = season_table(to_team_games(pl.read_ndjson(args.games), cfg["teams"]))
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
