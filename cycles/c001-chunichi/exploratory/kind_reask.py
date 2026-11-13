#!/usr/bin/env python3
"""保留 57 件のうち、条件を「単位の種類」に置き直せる 22 件を問い直す（探索。確定した出力は変えない）。

宣言: [kind_reask_results/kind_reask_prelock_2026-11-13.md](kind_reask_results/kind_reask_prelock_2026-11-13.md)
（固定の時刻と sha256 は同じ場所の kind_reask_prelock_timestamp.txt。選び方・先に数えた件数・読み方・予想は宣言どおり）

正本の `propositions.toml`（P1〜P114）の後ろに `kind_reask_results/kind_reask_propositions.toml`（K17〜K110）を
つなげて、同じ読み込み（propositions.load）に通す。親があること、正本と同じ問いでないことは、その読み込みが確かめる。
評価も同じ仕組み（propositions.evaluate / judge）で、データは正本の `outputs/season.jsonl` と `analysis.toml`。

読み方（判定ではない。宣言 §4）: きっかけ以外（中日以外の 11 球団）の元の命題で分ける。
  1 種類の性質       支持で fisher_p < 0.05
  2 どこでも多い     支持で fisher_p ≥ 0.05
  3 弱い関係         修正
  4 種類では言えない 棄却
  5 保留             判断保留

ゲート（通らなければ、命題の結果は出さずに止まる）:
  正本の命題ファイルの sha256 が保存された値と同じ。つなげたファイルが読み込める。
  K の命題が branch 側（from-cycle-001/propositions.toml）のどれとも同じ問いでない。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/kind_reask.py --outdir cycles/c001-chunichi/exploratory/kind_reask_results
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FORM_ORDER = ("original", "contrapositive", "converse", "inverse")
FORM_JA = {"original": "元", "contrapositive": "対偶", "converse": "逆", "inverse": "裏"}
READING = {"Supported": None, "Refined": 3, "Rejected": 4, "Inconclusive": 5}   # 支持は fisher_p で 1 と 2 に分ける
READING_JA = {1: "種類の性質", 2: "どこでも多い", 3: "弱い関係", 4: "種類では言えない", 5: "保留"}
ALPHA = 0.05                                  # 読み 1 と 2 の分かれ目（docs/propositions.md の既定の alpha）
EXIT_GATE = 65                                # pythdragoras の終了コード 65（データの誤り）に合わせる
# 宣言 §5: ほかの命題の件数から、先に読めていた元の命題の値（hold, n）
KNOWN_ORIGINAL = {"K31": (45, 52), "K40": (32, 52), "K46": (47, 52)}
LOW_SCORING = ("K17", "K25", "K26", "K27", "K28", "K29", "K31", "K32", "K40", "K45", "K46")   # 宣言 §6 (c)


def load_modules(repo: Path = ROOT):
    sys.path.insert(0, str(repo / "pythdragoras"))
    import polars as pl
    import propositions as P
    import pythdragoras as PD
    return pl, P, PD


def rel(path: Path, repo: Path) -> str:
    """リポジトリの中なら相対パス、外（テストの一時ファイルなど）ならそのまま。"""
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def load_joined(canon: Path, extra: Path, P) -> tuple[list[dict], list[dict]]:
    """正本の後ろに追加の命題をつなげて、正本と同じ読み込みに通す。戻り値は（正本の命題, 追加の命題）。"""
    canon_ids = [p["id"] for p in tomllib.loads(canon.read_text(encoding="utf-8")).get("proposition", [])]
    with tempfile.TemporaryDirectory() as tmp:
        joined = Path(tmp) / "joined.toml"
        joined.write_bytes(canon.read_bytes() + b"\n" + extra.read_bytes())
        props, _ = P.load(joined)
    return [p for p in props if p["id"] in set(canon_ids)], [p for p in props if p["id"] not in set(canon_ids)]


def form_summary(f: dict) -> dict:
    return {"n": f["n"], "hold": f["hold"], "undetermined": f.get("undetermined", 0), "rate": f["rate"],
            "ci": [round(x, 6) for x in f["ci"]], "base_rate": f.get("base_rate"), "fisher_p": f["fisher_p"],
            "verdict": f["verdict"], "code": f.get("code"),
            "units": sorted(c if isinstance(c, str) else c["unit"] for c in f["counterexamples"])}


def reading(held: dict) -> int:
    r = READING[held["verdict"]]
    if r is None:
        r = 1 if held["fisher_p"] < ALPHA else 2
    return r


def predictions(rows: dict[str, dict]) -> list[dict]:
    """宣言 §6 の予想 (b)〜(g) の当たり外れ。判定には使わない。"""
    def original(k):
        f = rows[k]["forms"]["original"]
        return (f["hold"], f["n"])

    def conv_ok(k):
        return rows[k]["forms"]["converse"]["code"] in (0, 1)

    out = [
        {"id": "b1", "text": "K31・K40・K46 の元の命題は 52 中 45・32・47",
         "ok": all(original(k) == v for k, v in KNOWN_ORIGINAL.items()),
         "got": {k: list(original(k)) for k in KNOWN_ORIGINAL}},
        {"id": "b2", "text": "K46 の元の命題は支持、K40 は支持にならない",
         "ok": rows["K46"]["forms"]["original"]["verdict"] == "Supported" and rows["K40"]["forms"]["original"]["verdict"] != "Supported",
         "got": {k: rows[k]["forms"]["original"]["verdict"] for k in ("K46", "K40")}},
        {"id": "c", "text": "低得点の 11 件は、逆がどれも終了コード 0・1 にならない",
         "ok": not any(conv_ok(k) for k in LOW_SCORING), "got": {k: rows[k]["forms"]["converse"]["code"] for k in LOW_SCORING}},
        {"id": "d", "text": "K85 は、元の命題は支持だが、読みは 2（どこでも多い）",
         "ok": rows["K85"]["forms"]["original"]["verdict"] == "Supported" and rows["K85"]["reading"] == 2,
         "got": {"original": rows["K85"]["forms"]["original"]["verdict"], "reading": rows["K85"]["reading"]}},
        {"id": "e", "text": "K32 と K46 は読み 1（種類の性質）",
         "ok": rows["K32"]["reading"] == 1 and rows["K46"]["reading"] == 1, "got": {k: rows[k]["reading"] for k in ("K32", "K46")}},
        {"id": "f", "text": "K88 と K110 は読み 1 にならない",
         "ok": rows["K88"]["reading"] != 1 and rows["K110"]["reading"] != 1, "got": {k: rows[k]["reading"] for k in ("K88", "K110")}},
        {"id": "g", "text": "K51 は読み 1 で、逆も終了コード 0 か 1",
         "ok": rows["K51"]["reading"] == 1 and conv_ok("K51"),
         "got": {"reading": rows["K51"]["reading"], "converse": rows["K51"]["forms"]["converse"]["code"]}},
    ]
    return out


def analyze(repo: Path = ROOT, season: Path | None = None, config: Path | None = None, props: Path | None = None,
            extra: Path | None = None, stored: Path | None = None, branch: Path | None = None) -> dict:
    pl, P, PD = load_modules(repo)
    base = repo / "cycles" / "c001-chunichi"
    season, config = season or base / "outputs" / "season.jsonl", config or base / "analysis.toml"
    props, stored = props or base / "propositions.toml", stored or base / "outputs" / "propositions.jsonl"
    extra = extra or HERE / "kind_reask_results" / "kind_reask_propositions.toml"
    branch = branch or base / "from-cycle-001" / "propositions.toml"
    stored_rows = {r["id"]: r for r in map(json.loads, stored.read_text(encoding="utf-8").splitlines())}
    sha = hashlib.sha256(props.read_bytes()).hexdigest()
    out = {"inputs": {"season": rel(season, repo), "propositions": rel(props, repo), "propositions_sha256": sha,
                      "kind_propositions": rel(extra, repo),
                      "kind_propositions_sha256": hashlib.sha256(extra.read_bytes()).hexdigest(),
                      "stored": rel(stored, repo), "branch": rel(branch, repo)},
           "gate": {"ok": True, "problems": []}, "propositions": [], "predictions": [], "summary": {}}
    problems = out["gate"]["problems"]
    stored_sha = {r["meta"]["sha256"] for r in stored_rows.values()}
    if sha not in stored_sha:
        problems.append(f"命題ファイルの sha256 {sha} が保存された値 {sorted(stored_sha)} にない")
    try:
        _, ks = load_joined(props, extra, P)
    except P.PropositionError as e:
        problems.append(f"つなげた命題ファイルが読み込めない: {e}")
        ks = []
    branch_sig = {P.identity(p)["signature"]: p["id"] for p in P.load(branch)[0]} if branch.exists() else {}
    for p in ks:
        other = branch_sig.get(P.identity(p)["signature"])
        if other:
            problems.append(f"{p['id']}: branch 側の {other} と同じ問い（{P.identity(p)['key']}）")
        if not p.get("motivated_by") or not p.get("parent"):
            problems.append(f"{p['id']}: parent と motivated_by が必要（中日の単位を見て書いた命題）")
    out["gate"]["ok"] = not problems
    if not out["gate"]["ok"]:
        return out

    full = pl.read_ndjson(season)
    cfg = tomllib.loads(config.read_text(encoding="utf-8"))
    included, exclusions = PD.apply_exclusions(full, cfg.get("exclude", []))
    excluded = full.filter(pl.col("season").is_in([int(e["season"]) for e in exclusions]))
    focus = cfg.get("focus", {}).get("team")
    out["inputs"]["exclusions"] = [e["season"] for e in exclusions]
    rows = {}
    for p in ks:
        r = P.evaluate(p, included, excluded, focus)
        forms = {f["form"]: form_summary(f) for f in r["forms"]}
        held = form_summary(r["held_out"])
        parent = stored_rows[p["parent"]]
        pf = {f["form"]: f for f in parent["forms"]}
        rows[p["id"]] = {
            "id": p["id"], "statement": p["statement"], "strength": p["strength"], "threshold": r["threshold"],
            "key": r["key"], "signature": r["signature"], "definition_sha256": r["definition_sha256"],
            "parent": p["parent"], "parent_original": {"n": pf["original"]["n"], "hold": pf["original"]["hold"],
                                                      "code": pf["original"]["code"]},
            "units": r["units"], "forms": forms, "held_out": held, "reading": reading(held),
            "converse_supported": forms["converse"]["code"] in (0, 1),
            "all_forms_ge_min_n": all(forms[f]["n"] >= r["min_n"] for f in FORM_ORDER),
            "judgement": {k: r["judgement"][k] for k in ("code", "stage", "form")},
            "excluded_counterexamples": sorted(c["unit"] for c in r["excluded_counterexamples"]),
        }
    out["propositions"] = [rows[p["id"]] for p in ks]
    out["predictions"] = predictions(rows)
    by_reading = {str(k): sorted((q["id"] for q in rows.values() if q["reading"] == k), key=lambda s: int(s[1:]))
                  for k in READING_JA}
    out["summary"] = {
        "count": len(rows), "by_reading": by_reading,
        "all_forms_ge_min_n": sum(q["all_forms_ge_min_n"] for q in rows.values()),
        "original_and_contrapositive_both_held": sorted(
            (q["id"] for q in rows.values() if q["forms"]["original"]["code"] == 4 and q["forms"]["contrapositive"]["code"] == 4),
            key=lambda s: int(s[1:])),
        "converse_supported": sorted((q["id"] for q in rows.values() if q["converse_supported"]), key=lambda s: int(s[1:])),
        "predictions_ok": sum(x["ok"] for x in out["predictions"]), "predictions": len(out["predictions"]),
    }
    return out


def _cell(f: dict) -> str:
    rate = "-" if f["rate"] is None else format(f["rate"], ".2f")
    return f"{f['code']}・{f['hold']}/{f['n']}（{rate}）"


def render(res: dict) -> str:
    L = ["# 保留の命題を、条件を単位の種類に置き直して問い直した結果（探索・事後。確定した出力は変えない）", ""]
    g = res["gate"]
    L += [f"ゲート（正本の命題ファイルが保存された値と同じ・つなげて読み込める・branch 側と同じ問いが無い）: {'通った' if g['ok'] else '通らなかった'}"]
    L += [f"- {x}" for x in g["problems"]]
    if not g["ok"]:
        return "\n".join(L) + "\n"
    s = res["summary"]
    L += ["", f"問い直した命題は {s['count']} 件。4 つの形すべてに 10 単位以上入ったのは {s['all_forms_ge_min_n']} 件。",
          (f"元の命題と対偶がどちらも保留のままなのは {len(s['original_and_contrapositive_both_held'])} 件"
           f"（{'、'.join(s['original_and_contrapositive_both_held']) or 'なし'}）。"), "",
          "各セルは「終了コード・hold/n（成立率）」。きっかけ以外 = 中日以外の 11 球団での元の命題。読みは判定ではない（宣言 §4）。", "",
          "| 命題 | 親（中日） | 元 | 対偶 | 逆 | 裏 | きっかけ以外 | fisher_p | 読み |", "|---|---|---|---|---|---|---|---|---|"]
    for q in res["propositions"]:
        h, po = q["held_out"], q["parent_original"]
        held_code = {"Supported": "支持", "Refined": "修正", "Rejected": "棄却", "Inconclusive": "保留"}[h["verdict"]]
        L += [f"| {q['id']} {q['statement']} | {q['parent']} {po['hold']}/{po['n']} | "
              + " | ".join(_cell(q["forms"][f]) for f in FORM_ORDER)
              + f" | {held_code}・{h['hold']}/{h['n']}（{h['rate']:.2f}） | {h['fisher_p']:.2g} | **{q['reading']}** {READING_JA[q['reading']]}"
              + ("・逆も言える" if q["converse_supported"] else "") + " |"]
    L += ["", "## 読みごとの命題", ""]
    for k, name in READING_JA.items():
        L += [f"- {k} {name}: {'、'.join(s['by_reading'][str(k)]) or 'なし'}"]
    L += ["", f"## 予想の当たり外れ（宣言 §6。判定には使わない）: {s['predictions_ok']}/{s['predictions']}", ""]
    for x in res["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args(argv)
    res = analyze(args.repo)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "kind_reask.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "kind_reask.md").write_text(render(res), encoding="utf-8")
    if not res["gate"]["ok"]:
        print("ゲートが通らなかった:", *res["gate"]["problems"], sep="\n  ", file=sys.stderr)
        return EXIT_GATE
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
