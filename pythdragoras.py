"""PythDRagoras — 本当にその説明で十分か？

SakAnalytics のシーズン表を受け取り、「説明」と「現実」のずれを検証する。
答えを出すのではなく、ずれ（残差）と、その珍しさを記録し、次の問いの材料にする。

  apply_exclusions() : 分析から除くシーズンを適用し、何を・なぜ除いたかを結果に残す
  cumulative_test()  : Σ(実勝 − 期待勝) / sqrt(Σ n·p·(1−p))。期待勝率からのずれの累積
  rank_test()        : 順位が下位に偏る珍しさ。2つの基準を並べる
                       A. 帰無仮説: 各シーズンの順位は独立に一様（下位になる確率 = 下位の枠 / 球団数）
                       B. 経験的基準: 同じ期間の全球団の実際の記録と比べる
                       A は前年からの戦力の持ち越しを無視するので珍しさを過大に見積もる。B はそれを補う

検定の結果は「説明できない部分がどれだけ偶然では起きにくいか」を示すだけで、原因は示さない。
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tomllib
from functools import lru_cache
from pathlib import Path

import polars as pl


def apply_exclusions(st: pl.DataFrame, exclude: list[dict]) -> tuple[pl.DataFrame, list[dict]]:
    """exclude = [{"season": 2020, "reason": "..."}]。理由のない除外は受け付けない。"""
    for e in exclude:
        if not str(e.get("reason", "")).strip():
            raise ValueError(f"除外には理由が必要: {e}")
    seasons = [int(e["season"]) for e in exclude]
    removed = st.filter(pl.col("season").is_in(seasons))
    record = [{**e, "rows_removed": removed.filter(pl.col("season") == int(e["season"])).height} for e in exclude]
    return st.filter(~pl.col("season").is_in(seasons)), record


def _p_two_sided(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2))


def cumulative_test(st: pl.DataFrame) -> pl.DataFrame:
    out = []
    for label in ("fixed", "var"):
        p, n = pl.col(f"pythag_{label}"), pl.col("W") + pl.col("L")
        out.append(
            st.group_by("team", maintain_order=True)
            .agg(pl.first("team_name"), pl.len().alias("seasons"),
                 (pl.col("W") - n * p).sum().alias("excess_wins"), (n * p * (1 - p)).sum().alias("var"))
            .with_columns(model=pl.lit(label), z=pl.col("excess_wins") / pl.col("var").sqrt())
        )
    res = pl.concat(out)
    return res.with_columns(
        p_two_sided=pl.col("z").map_elements(_p_two_sided, return_dtype=pl.Float64)
    ).drop("var").sort("model", "z")


def binom_tail(n: int, k: int, p: float) -> float:
    """P(X >= k), X ~ Binomial(n, p)。"""
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def run_tail(n: int, r: int, p: float) -> float:
    """独立な n 回の試行で、確率 p の事象が r 回以上連続する確率。"""
    if r <= 0:
        return 1.0

    @lru_cache(maxsize=None)
    def no_run(i: int, cur: int) -> float:  # 残り i 回で、現在 cur 連続中のとき、r 連続に達しない確率
        if cur >= r:
            return 0.0
        if i == 0:
            return 1.0
        return p * no_run(i - 1, cur + 1) + (1 - p) * no_run(i - 1, 0)

    return 1 - no_run(n, 0)


def _longest(flags: list[bool]) -> int:
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def rank_test(st: pl.DataFrame) -> list[dict]:
    """各チームについて、下位（順位 > 球団数/2）になったシーズン数と最長連続を数え、2つの基準と比べる。

    連続はシーズンの並び（除外したシーズンは飛ばした並び）で数える。
    """
    rows = []
    for (team,), g in st.sort("season").group_by(["team"], maintain_order=True):
        size = g["league_size"].to_list()
        bottom = [r > s / 2 for r, s in zip(g["rank"].to_list(), size)]
        p = sum((s - s // 2) / s for s in size) / len(size)  # 下位の枠の割合（6球団なら 3/6）
        n, k, run = len(bottom), sum(bottom), _longest(bottom)
        rows.append({
            "team": team, "team_name": g["team_name"][0], "seasons": n,
            "first": int(g["season"][0]), "last": int(g["season"][-1]),
            "ranks": g["rank"].to_list(), "rank_ties": int(g["rank_tie"].sum()),
            "bottom_seasons": k, "longest_bottom_run": run, "p_bottom_null": p,
            "null_p_at_least_k": binom_tail(n, k, p), "null_p_run_at_least": run_tail(n, run, p),
        })
    # 経験的基準: 同じ表に入っている全チームのうち、下位シーズン数がこのチーム以上だったチームの割合
    for r in rows:
        r["empirical_share_at_least_k"] = sum(o["bottom_seasons"] >= r["bottom_seasons"] for o in rows) / len(rows)
        r["empirical_share_run_at_least"] = sum(o["longest_bottom_run"] >= r["longest_bottom_run"] for o in rows) / len(rows)
    return sorted(rows, key=lambda r: (-r["bottom_seasons"], -r["longest_bottom_run"], r["team"]))


def summary_markdown(focus: str | None, exclusions: list[dict], cum: pl.DataFrame, ranks: list[dict],
                     hypotheses: list[dict]) -> str:
    """観測（数えたもの）と解釈（ここでは書かない）を分けた要約。"""
    lines = ["# PythDRagoras 検証記録（自動生成）", "",
             "この記録は「説明できない部分がどれだけ偶然では起きにくいか」を示すだけで、原因は示さない。", ""]
    lines += ["## 除外したシーズン", ""]
    lines += [f"- {e['season']}: {e['reason']}（{e['rows_removed']} 行）" for e in exclusions] or ["- なし"]
    lines += ["", "## 順位の偏り", "",
              "| team | 期間 | 下位シーズン | 最長連続 | 帰無: P(下位≥k) | 帰無: P(連続≥r) | 全球団中で下位≥kの割合 | 同率 |",
              "|---|---|---|---|---|---|---|---|"]
    for r in ranks:
        mark = " **(focus)**" if r["team"] == focus else ""
        lines.append(f"| {r['team_name']}{mark} | {r['first']}-{r['last']} ({r['seasons']}) | {r['bottom_seasons']} "
                     f"| {r['longest_bottom_run']} | {r['null_p_at_least_k']:.2e} | {r['null_p_run_at_least']:.2e} "
                     f"| {r['empirical_share_at_least_k']:.2f} | {r['rank_ties']} |")
    lines += ["", "帰無仮説は各シーズンを独立とみなすため、前年からの戦力の持ち越しを無視し、珍しさを過大に見積もる。",
              "全球団との比較（経験的基準）と並べて読むこと。", ""]
    lines += ["## 期待勝率からのずれの累積", "", "| model | team | seasons | excess_wins | z | p |", "|---|---|---|---|---|---|"]
    for r in cum.iter_rows(named=True):
        mark = " **(focus)**" if r["team"] == focus else ""
        lines.append(f"| {r['model']} | {r['team_name']}{mark} | {r['seasons']} | {r['excess_wins']:+.1f} | {r['z']:+.2f} | {r['p_two_sided']:.3f} |")
    if hypotheses:
        lines += ["", "## 競合仮説の状態", "", "| id | 仮説 | 状態 | 必要なデータ |", "|---|---|---|---|"]
        lines += [f"| {h['id']} | {h['statement']} | {h['status']} | {h.get('requires', '-')} |" for h in hypotheses]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="シーズン表から残差と順位の偏りを検証する")
    ap.add_argument("--season", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--hypotheses", type=Path, help="競合仮説の一覧（TOML）")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args(argv)

    with args.config.open("rb") as f:
        cfg = tomllib.load(f)
    hyps = []
    if args.hypotheses:
        with args.hypotheses.open("rb") as f:
            hyps = tomllib.load(f).get("hypothesis", [])

    st = pl.read_ndjson(args.season)
    league = cfg.get("focus", {}).get("league")
    if league:
        st = st.filter(pl.col("league") == league)
    st, exclusions = apply_exclusions(st, cfg.get("exclude", []))
    cum, ranks = cumulative_test(st), rank_test(st)

    args.outdir.mkdir(parents=True, exist_ok=True)
    cum.write_ndjson(args.outdir / "cumulative.jsonl")
    (args.outdir / "rank_test.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ranks), encoding="utf-8")
    (args.outdir / "exclusions.json").write_text(json.dumps(exclusions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = summary_markdown(cfg.get("focus", {}).get("team"), exclusions, cum, ranks, hyps)
    (args.outdir / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
