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


def persistence(st: pl.DataFrame, cols: list[str]) -> list[dict]:
    """同じチームの隣り合うシーズン（t, t+1）の相関。続く特徴か、毎年入れ替わる偶然かの目安。

    Pearson の r と、Fisher の z 変換による 95% 区間。列がなければ黙って飛ばさず、その旨を返す。
    """
    out = []
    for col in cols:
        if col not in st.columns:
            out.append({"column": col, "n": 0, "r": None, "ci": None, "note": "列がない"})
            continue
        a = st.select("team", "season", x=pl.col(col))
        pairs = a.join(a.select("team", season=pl.col("season") - 1, y=pl.col("x")), on=["team", "season"]).drop_nulls(["x", "y"])
        n = pairs.height
        if n < 4:
            out.append({"column": col, "n": n, "r": None, "ci": None, "note": "組が少なすぎる"})
            continue
        xs, ys = pairs["x"].to_list(), pairs["y"].to_list()
        mx, my = sum(xs) / n, sum(ys) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx, syy = sum((x - mx) ** 2 for x in xs), sum((y - my) ** 2 for y in ys)
        r = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None
        ci = None
        if r is not None and abs(r) < 1:
            z, h = math.atanh(r), 1.959963984540054 / math.sqrt(n - 3)
            ci = (math.tanh(z - h), math.tanh(z + h))
        out.append({"column": col, "n": n, "r": r, "ci": ci, "note": ""})
    return out


def allocation_cumulative(st: pl.DataFrame) -> pl.DataFrame:
    """配分効果の期間合計。z = Σ alloc_net / √Σ alloc_var（シーズンを独立とみなす）。"""
    if "alloc_net" not in st.columns:
        return pl.DataFrame()
    out = []
    for tag in ("", "_strat"):
        out.append(
            st.group_by("team", maintain_order=True)
            .agg(pl.first("team_name"), pl.len().alias("seasons"),
                 pl.col(f"alloc_net{tag}").sum().alias("alloc_net"), pl.col(f"alloc_var{tag}").sum().alias("var"))
            .with_columns(baseline=pl.lit("全試合" if not tag else "ホーム/ビジター別"),
                          z=pl.col("alloc_net") / pl.col("var").sqrt())
        )
    return pl.concat(out).drop("var").sort("baseline", "z")


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


def markov_run_tail(n: int, r: int, p_bb: float, p_tb: float, pi_b: float) -> float:
    """2状態マルコフ連鎖（下位/上位）で、n シーズン中に下位が r 回以上連続する確率。

    p_bb = P(翌年も下位 | 今年下位), p_tb = P(翌年下位 | 今年上位), pi_b = 最初の年に下位の確率。
    戦力の持ち越し（前年の順位が翌年に影響すること）を入れた帰無仮説。
    """
    if r <= 0:
        return 1.0
    if n == 0:
        return 0.0

    @lru_cache(maxsize=None)
    def no_run(i: int, cur: int, last_bottom: bool) -> float:  # 残り i 年、現在 cur 連続、直前が下位か
        if cur >= r:
            return 0.0
        if i == 0:
            return 1.0
        pb = p_bb if last_bottom else p_tb
        return pb * no_run(i - 1, cur + 1, True) + (1 - pb) * no_run(i - 1, 0, False)

    first = pi_b * no_run(n - 1, 1, True) + (1 - pi_b) * no_run(n - 1, 0, False)
    return 1 - first


def transitions(st: pl.DataFrame) -> dict:
    """全チームについて、隣り合う（含めた範囲で連続する）シーズンの下位/上位の移り変わりを数える。"""
    c = {"bb": 0, "bt": 0, "tb": 0, "tt": 0}
    for _, g in st.sort("season").group_by(["team"], maintain_order=True):
        flags = [r > s / 2 for r, s in zip(g["rank"].to_list(), g["league_size"].to_list())]
        for a, b in zip(flags, flags[1:]):
            c[("b" if a else "t") + ("b" if b else "t")] += 1
    p_bb = c["bb"] / (c["bb"] + c["bt"]) if c["bb"] + c["bt"] else None
    p_tb = c["tb"] / (c["tb"] + c["tt"]) if c["tb"] + c["tt"] else None
    pi_b = p_tb / (1 - p_bb + p_tb) if p_bb is not None and p_tb is not None and (1 - p_bb + p_tb) else None
    return {**c, "p_bb": p_bb, "p_tb": p_tb, "pi_b": pi_b}


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
    # 持ち越しを入れた基準: 全チームの移り変わりから推定したマルコフ連鎖
    tr = transitions(st)
    for r in rows:
        r["markov"] = {k: tr[k] for k in ("p_bb", "p_tb", "pi_b")}
        r["markov_p_run_at_least"] = (markov_run_tail(r["seasons"], r["longest_bottom_run"], tr["p_bb"], tr["p_tb"], tr["pi_b"])
                                      if tr["pi_b"] is not None else None)
    # 経験的基準: 同じ表に入っている全チームのうち、下位シーズン数がこのチーム以上だったチームの割合
    for r in rows:
        r["empirical_share_at_least_k"] = sum(o["bottom_seasons"] >= r["bottom_seasons"] for o in rows) / len(rows)
        r["empirical_share_run_at_least"] = sum(o["longest_bottom_run"] >= r["longest_bottom_run"] for o in rows) / len(rows)
    return sorted(rows, key=lambda r: (-r["bottom_seasons"], -r["longest_bottom_run"], r["team"]))


def _fz(x):
    return "-" if x is None else f"{x:+.2f}"


def _f(x):
    return "-" if x is None else f"{x:.3f}"


def summary_markdown(focus: str | None, exclusions: list[dict], cum: pl.DataFrame, ranks: list[dict],
                     hypotheses: list[dict], alloc: pl.DataFrame | None = None, pers: list[dict] | None = None) -> str:
    """観測（数えたもの）と解釈（ここでは書かない）を分けた要約。"""
    lines = ["# PythDRagoras 検証記録（自動生成）", "",
             "この記録は「説明できない部分がどれだけ偶然では起きにくいか」を示すだけで、原因は示さない。", ""]
    lines += ["## 除外したシーズン", ""]
    lines += [f"- {e['season']}: {e['reason']}（{e['rows_removed']} 行）" for e in exclusions] or ["- なし"]
    lines += ["", "## 順位の偏り", "",
              "| team | 期間 | 下位シーズン | 最長連続 | 独立: P(下位≥k) | 独立: P(連続≥r) | マルコフ: P(連続≥r) | 全球団中で下位≥kの割合 | 同率 |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in ranks:
        mark = " **(focus)**" if r["team"] == focus else ""
        lines.append(f"| {r['team_name']}{mark} | {r['first']}-{r['last']} ({r['seasons']}) | {r['bottom_seasons']} "
                     f"| {r['longest_bottom_run']} | {r['null_p_at_least_k']:.2e} | {r['null_p_run_at_least']:.2e} "
                     f"| {'-' if r['markov_p_run_at_least'] is None else format(r['markov_p_run_at_least'], '.2e')} "
                     f"| {r['empirical_share_at_least_k']:.2f} | {r['rank_ties']} |")
    if ranks:
        m = ranks[0]["markov"]
        lines += ["", f"マルコフ連鎖の推定値（含めた範囲の全チーム）: P(下位→下位)={_f(m['p_bb'])}, "
                      f"P(上位→下位)={_f(m['p_tb'])}, 定常的に下位の確率={_f(m['pi_b'])}"]
    lines += ["", "「独立」は各シーズンを独立とみなすため、前年からの戦力の持ち越しを無視し、珍しさを過大に見積もる。",
              "「マルコフ」は持ち越しを入れるが、推定に使える年数が短いと不安定になる。全球団との比較と並べて読むこと。", ""]
    lines += ["## 期待勝率からのずれの累積", "", "| model | team | seasons | excess_wins | z | p |", "|---|---|---|---|---|---|"]
    for r in cum.iter_rows(named=True):
        mark = " **(focus)**" if r["team"] == focus else ""
        lines.append(f"| {r['model']} | {r['team_name']}{mark} | {r['seasons']} | {r['excess_wins']:+.1f} | {r['z']:+.2f} | {r['p_two_sided']:.3f} |")
    if alloc is not None and alloc.height:
        lines += ["", "## 得点・失点の配分効果の累積（R1、探索的）", "",
                  "試合ごとの得点と失点の並びを保ち、組み合わせだけをランダムにした基準と比べた（勝 − 敗）の差。",
                  "", "| 基準 | team | seasons | 配分効果（勝−敗） | z |", "|---|---|---|---|---|"]
        for r in alloc.iter_rows(named=True):
            mark = " **(focus)**" if r["team"] == focus else ""
            lines.append(f"| {r['baseline']} | {r['team_name']}{mark} | {r['seasons']} | {r['alloc_net']:+.1f} | {_fz(r['z'])} |")
    if pers:
        lines += ["", "## 翌年にも続くか（隣り合うシーズンの相関、全チーム）", "",
                  "| 指標 | 組の数 | r | 95%区間 | 備考 |", "|---|---|---|---|---|"]
        for p in pers:
            ci = "-" if p["ci"] is None else f"{p['ci'][0]:+.2f}〜{p['ci'][1]:+.2f}"
            lines.append(f"| {p['column']} | {p['n']} | {_fz(p['r'])} | {ci} | {p['note']} |")
    if hypotheses:
        lines += ["", "## 競合仮説の状態", "", "| id | 仮説 | 状態 | 必要なデータ |", "|---|---|---|---|"]
        lines += [f"| {h['id']} | {h['statement']} | {h['status']} | {h.get('requires', '-')} |" for h in hypotheses]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    import hashlib

    from propositions import (DataError, PropositionError, check_claims, evaluate, judge, label, ledger_summary,
                              load, render, render_claims, update_ledger)

    ap = argparse.ArgumentParser(description="シーズン表から残差・順位の偏り・命題を検証する")
    ap.add_argument("--season", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--hypotheses", type=Path, help="競合仮説の一覧（TOML）")
    ap.add_argument("--propositions", type=Path, help="命題（TOML）。docs/propositions.md の形式")
    ap.add_argument("--claims", type=Path, help="外部の主張（TOML）")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args(argv)

    with args.config.open("rb") as f:
        cfg = tomllib.load(f)
    hyps = []
    if args.hypotheses:
        with args.hypotheses.open("rb") as f:
            hyps = tomllib.load(f).get("hypothesis", [])
    focus = cfg.get("focus", {}).get("team")

    full = pl.read_ndjson(args.season)
    included, exclusions = apply_exclusions(full, cfg.get("exclude", []))
    # 除外したシーズンを、除外の記録から直接取り出す
    # （Series.unique() は Python 3.15 ベータ + polars 1.44.2 で None を返すため使わない）
    excluded = full.filter(pl.col("season").is_in([int(e["season"]) for e in exclusions]))

    league = cfg.get("focus", {}).get("league")
    st = included.filter(pl.col("league") == league) if league else included
    cum, ranks = cumulative_test(st), rank_test(st)
    alloc = allocation_cumulative(st)
    pers = persistence(included, ["alloc_z", "alloc_z_strat", "resid_fixed", "wpct"])

    args.outdir.mkdir(parents=True, exist_ok=True)
    cum.write_ndjson(args.outdir / "cumulative.jsonl")
    _jsonl(args.outdir / "rank_test.jsonl", ranks)
    (args.outdir / "exclusions.json").write_text(json.dumps(exclusions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = summary_markdown(focus, exclusions, cum, ranks, hyps, alloc, pers)
    if alloc.height:
        alloc.write_ndjson(args.outdir / "allocation.jsonl")
    _jsonl(args.outdir / "persistence.jsonl", pers)

    if args.propositions:
        try:
            props, sha = load(args.propositions)
            meta = {"sha256": sha, "code_version": _code_version(), "file": str(args.propositions)}
            results = [{**evaluate(p, included, excluded, focus), "meta": meta} for p in props]
        except DataError as e:  # 判定の結果（異議）ではなく、仕組みの不具合は失敗にする
            print(f"[65] {e}", file=sys.stderr)
            return 65
        except PropositionError as e:
            print(f"[64] {e}", file=sys.stderr)
            return 64
        except AssertionError as e:
            print(f"[70] {e}", file=sys.stderr)
            return 70
        data_sha = hashlib.sha256(args.season.read_bytes()).hexdigest()
        ledger = update_ledger(args.outdir / "ledger.jsonl", results, data_sha, meta["code_version"])
        for r in results:  # 台帳を見たうえで最終の判定（同じ id の再定義は 6）
            r["judgement"] = judge(r, ledger_summary(ledger, r["id"])["definitions"])
        _jsonl(args.outdir / "propositions.jsonl", results)
        (args.outdir / "objections.md").write_text(render(results, meta, ledger=ledger), encoding="utf-8")
        md += "\n## 命題の判定\n\n" + "\n".join(
            f"- {r['id']} {r['statement']}: **exit {r['judgement']['code']} {label(r['judgement']['code'])}** "
            "（" + " / ".join(f"{_FORM.get(f['form'], f['form'])} {_VERD[f['verdict']]}" for f in r["forms"]) + "）"
            for r in results) + "\n\n詳細は objections.md。終了コードは `python pythdragoras/propositions.py judge` で確かめられる。\n"
    if args.claims:
        with args.claims.open("rb") as f:
            claims = check_claims(tomllib.load(f).get("claim", []), full)
        (args.outdir / "claims.json").write_text(json.dumps(claims, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md += "\n" + render_claims(claims)

    (args.outdir / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


_FORM = {"original": "元", "contrapositive": "対偶", "converse": "逆", "inverse": "裏"}
_VERD = {"Supported": "支持", "Rejected": "棄却", "Refined": "修正", "Inconclusive": "保留"}


def _jsonl(path: Path, rows) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows), encoding="utf-8")


def _code_version():
    import subprocess
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5,
                             cwd=Path(__file__).resolve().parent, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
