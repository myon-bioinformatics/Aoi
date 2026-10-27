#!/usr/bin/env python3
"""連続年数の「前の年が不明」を 0 とせず、未知の定数 u（0 以上）として扱うと、P62〜P65 の判定が動くか（探索。確定した出力は変えない）。

宣言: [streak_unknown_results/streak_unknown_prelock_2026-10-27.md](streak_unknown_results/streak_unknown_prelock_2026-10-27.md)
（固定の時刻と sha256 は同じ場所の streak_unknown_prelock_timestamp.txt。定義・3 通りの評価・読み方は宣言どおり）

`streak()` は前の年が空のとき `(prev or 0) + 1` で 0 とみなしている。左端（旗が分かる最初の年）に届く連続の値 n は、
本当は n + u（u ≥ 0 は未知）。u は記号のままで、値を仮置きしない。同じ評価の仕組み（propositions.evaluate）に、
列の値だけを変えた 3 つの表を渡す。
  (a) そのまま（u = 0。確定済みの出力と同じ）
  (b) 左端に届く連続の値を十分大きい数にする（u が十分大きい）
  (c) その命題のどの条件でも真偽が (a) と (b) で違う行（不明な行）の値を空にする（判定できない単位に入る）
k = 2 の `>=` なら、n = 1 の行が真になるかは u ≥ 1 かどうかだけで決まるので、(a) と (b) で u のすべての値を尽くす。

予想（走らせる前に書いた。結果を見て変えない。判定には使わない。宣言 §5 と同じ）:
  (a) ゲート: P62〜P65 で、(a) の各形の n・hold・undetermined・終了コード・判例の単位が、保存された
      cycles/c001-chunichi/outputs/propositions.jsonl と同じ。命題ファイルの sha256 も保存された値と同じ
  (b) 不明な行は inn_size_low_streak で 4、rf_low_streak で 0。P64・P65 は 3 通りで完全に同じ。P62 は 4 行、P63 は d を除くので 3 行が影響する
  (c) P62 の原命題: (a) は n 16・hold 16・判例 0・終了コード 0。(b) は n 20・hold 19・判例 1 件（l-2013）。終了コードは (a) と違う
  (d) 「u しだい」になる命題は P62 と P63。P64 と P65 は「u によらない」
  ゲートが通らなければ、それ以降は出さずに止まる。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/streak_unknown.py --outdir cycles/c001-chunichi/exploratory/streak_unknown_results
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COLS = ("inn_size_low_streak", "rf_low_streak")
BIG = 10**6                                   # u が十分大きい: 条件のどの閾値よりずっと大きい
TREATMENTS = ("a", "b", "c")
TREATMENT_JA = {"a": "(a) u = 0（現状）", "b": "(b) u が十分大きい", "c": "(c) 不明な行を空にする"}
GATE_KEYS = ("n", "hold", "undetermined", "code")
EXIT_GATE = 65                                # pythdragoras の終了コード 65（データの誤り）に合わせる


def load_modules(repo: Path = ROOT):
    sys.path.insert(0, str(repo / "pythdragoras"))
    import polars as pl
    import propositions as P
    import pythdragoras as PD
    return pl, P, PD


def left_edge_runs(rows: list[dict], col: str) -> dict[tuple, int]:
    """左端に届く連続の行 {(team, season): n}。左端 = そのチームで列の値が空でない最初の年。連続の始まり = 年 − n + 1。"""
    first: dict[str, int] = {}
    for r in rows:
        if r[col] is not None:
            first[r["team"]] = min(first.get(r["team"], r["season"]), r["season"])
    return {(r["team"], r["season"]): r[col] for r in rows
            if r[col] is not None and r[col] > 0 and r["season"] - r[col] + 1 == first[r["team"]]}


def conditions_on(p: dict, col: str, P) -> list[dict]:
    """命題 p の前件・後件・範囲の where にある、col への条件。"""
    conds = [*P._if_conds(p), *p["then"], *(p.get("scope") or {}).get("where", [])]
    return [c for c in conds if c["col"] == col]


def unknown_rows(p: dict, col: str, edge: dict[tuple, int], P) -> set[tuple]:
    """n + u の真偽が、すべての u ≥ 0 で同じにならない行。真偽は u = 0 と u が十分大きいときで比べる（条件は単調か、1 点で変わる）。"""
    out = set()
    for key, n in edge.items():
        for c in conditions_on(p, col, P):
            if P.OPS[c["op"]](n, c["value"]) != P.OPS[c["op"]](BIG, c["value"]):
                out.add(key)
    return out


def treated(st, p: dict, edge_by_col: dict[str, dict], treatment: str, P, pl):
    """列の値だけを変えた表。(a) はそのまま。"""
    if treatment == "a":
        return st
    for col, edge in edge_by_col.items():
        if not conditions_on(p, col, P) or col not in st.columns:
            continue
        keys = pl.concat_str([pl.col("team"), pl.lit("|"), pl.col("season").cast(pl.Utf8)])
        if treatment == "b":
            hit, new = set(edge), pl.lit(BIG, dtype=pl.Int64)
        else:
            hit, new = unknown_rows(p, col, edge, P), pl.lit(None, dtype=pl.Int64)
        names = [f"{t}|{s}" for t, s in sorted(hit)]
        st = st.with_columns(pl.when(keys.is_in(names)).then(new).otherwise(pl.col(col)).alias(col))
    return st


def summarize(result: dict) -> dict[str, dict]:
    return {f["form"]: {**{k: f[k] for k in GATE_KEYS}, "units": sorted(c["unit"] for c in f["counterexamples"])}
            for f in result["forms"]}


def gate(p: dict, a_summary: dict, stored: dict) -> list[str]:
    """(a) が保存された結果と同じか。違う箇所を文字で返す（空なら再現できた）。"""
    problems = []
    got = a_summary
    want = {f["form"]: {**{k: f[k] for k in GATE_KEYS}, "units": sorted(c["unit"] for c in f["counterexamples"])}
            for f in stored["forms"]}
    if set(got) != set(want):
        problems.append(f"{p['id']}: 形の集合が違う（{sorted(got)} と {sorted(want)}）")
    for form in sorted(set(got) & set(want)):
        if got[form] != want[form]:
            problems.append(f"{p['id']} {form}: {got[form]} と保存された {want[form]}")
    return problems


def rel(path: Path, repo: Path) -> str:
    """リポジトリの中なら相対パス、外（テストの一時ファイルなど）ならそのまま。"""
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def stability(by_t: dict) -> dict:
    """1 つの形の (a)(b)(c) を比べる。終了コードが同じなら「u によらない」。数や判例の単位が動いたかも別に残す。"""
    cx = {t: set(by_t[t]["units"]) for t in TREATMENTS}
    same = [{k: by_t[t][k] for k in GATE_KEYS} == {k: by_t["a"][k] for k in GATE_KEYS} and cx[t] == cx["a"] for t in TREATMENTS]
    return {"code_stable": len({by_t[t]["code"] for t in TREATMENTS}) == 1, "counts_stable": all(same),
            "new_counterexamples_b": sorted(cx["b"] - cx["a"]), "gone_counterexamples_b": sorted(cx["a"] - cx["b"])}


def analyze(repo: Path = ROOT, season: Path | None = None, config: Path | None = None, props: Path | None = None,
            stored: Path | None = None) -> dict:
    pl, P, PD = load_modules(repo)
    base = repo / "cycles" / "c001-chunichi"
    season, config = season or base / "outputs" / "season.jsonl", config or base / "analysis.toml"
    props, stored = props or base / "propositions.toml", stored or base / "outputs" / "propositions.jsonl"
    full = pl.read_ndjson(season)
    cfg = tomllib.loads(config.read_text(encoding="utf-8"))
    included, exclusions = PD.apply_exclusions(full, cfg.get("exclude", []))
    excluded = full.filter(pl.col("season").is_in([int(e["season"]) for e in exclusions]))
    focus = cfg.get("focus", {}).get("team")
    plist, sha = P.load(props)
    stored_rows = {r["id"]: r for r in map(json.loads, stored.read_text(encoding="utf-8").splitlines())}
    rows = full.sort("team", "season").to_dicts()
    edge_by_col = {col: left_edge_runs(rows, col) for col in COLS if col in full.columns}
    used = [p for p in plist if any(conditions_on(p, c, P) for c in COLS)]

    out = {"inputs": {"season": rel(season, repo), "propositions": rel(props, repo),
                      "propositions_sha256": sha, "stored": rel(stored, repo),
                      "exclusions": [e["season"] for e in exclusions], "big": BIG},
           "left_edge_rows": {c: sorted(f"{t}-{s}" for t, s in e) for c, e in edge_by_col.items()},
           "gate": {"ok": True, "problems": []}, "propositions": []}
    stored_sha = {r["meta"]["sha256"] for r in stored_rows.values()}
    if sha not in stored_sha:
        out["gate"]["problems"].append(f"命題ファイルの sha256 {sha} が保存された値 {sorted(stored_sha)} にない")
    for p in used:
        per = {}
        for t in TREATMENTS:
            tab = treated(included, p, edge_by_col, t, P, pl)
            ex = treated(excluded, p, edge_by_col, t, P, pl)
            per[t] = summarize(P.evaluate(p, tab, ex, focus))
        out["gate"]["problems"] += gate(p, per["a"], stored_rows[p["id"]])
        unknown = {col: sorted(f"{t}-{s}" for t, s in unknown_rows(p, col, edge_by_col[col], P))
                   for col in COLS if col in edge_by_col and conditions_on(p, col, P)}
        out["propositions"].append({
            "id": p["id"], "statement": p["statement"], "unknown_units": unknown,
            "forms": {form: {t: per[t][form] for t in TREATMENTS} for form in per["a"]}})
    out["gate"]["ok"] = not out["gate"]["problems"]
    if not out["gate"]["ok"]:
        out["propositions"] = []                     # ゲートが通らなければ、3 通りの結果は出さない
        return out
    for q in out["propositions"]:
        for by_t in q["forms"].values():
            by_t.update(stability(by_t))
        q["u_dependent_forms"] = [f for f, v in q["forms"].items() if not v["code_stable"]]
        q["verdict_depends_on_u"] = bool(q["u_dependent_forms"])
    return out


def render(res: dict) -> str:
    L = ["# 連続年数の「前の年が不明」を記号 u にしたときの判定（探索・事後。確定した出力は変えない）", ""]
    g = res["gate"]
    L += [f"ゲート（(a) が保存された結果を再現するか）: {'通った' if g['ok'] else '通らなかった'}"]
    L += [f"- {x}" for x in g["problems"]]
    if not g["ok"]:
        return "\n".join(L) + "\n"
    L += ["", "各セルは「終了コード・hold/n（判定できない単位）」。", ""]
    for q in res["propositions"]:
        L += [f"## {q['id']} {q['statement']}", ""]
        unk = "、".join(f"{c}: {', '.join(v) or 'なし'}" for c, v in q["unknown_units"].items())
        L += [f"不明な行: {unk}", "", "| 形 | " + " | ".join(TREATMENT_JA[t] for t in TREATMENTS) + " | 終了コード |", "|---|---|---|---|---|"]
        for form, v in q["forms"].items():
            cells = [f"{v[t]['code']}・{v[t]['hold']}/{v[t]['n']}（{v[t]['undetermined']}）" for t in TREATMENTS]
            L += [f"| {form} | " + " | ".join(cells) + f" | {'u によらない' if v['code_stable'] else 'u しだい'} |"]
        for form, v in q["forms"].items():
            if not v["code_stable"]:
                codes = {t: v[t]["code"] for t in TREATMENTS}
                L += ["", f"- {form}: 終了コードは (a) {codes['a']}・(b) {codes['b']}・(c) {codes['c']}。"
                          f"(b) で新しく判例になる行: {', '.join(v['new_counterexamples_b']) or 'なし'}。"
                          f"(b) で判例でなくなる行: {', '.join(v['gone_counterexamples_b']) or 'なし'}"]
        L += [""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args(argv)
    res = analyze(args.repo)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "streak_unknown.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "streak_unknown.md").write_text(render(res), encoding="utf-8")
    if not res["gate"]["ok"]:
        print("ゲートが通らなかった:", *res["gate"]["problems"], sep="\n  ", file=sys.stderr)
        return EXIT_GATE
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
