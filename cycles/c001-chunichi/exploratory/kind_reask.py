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

第2弾（宣言は kind_reask_results/kind_reask_r2_propositions.toml の冒頭。刻印は同じ timestamp ファイル）:
  A. 22 命題を、まだ使っていない 2026年の 12 単位で照らす（R18 と同じ propositions.confirm_units。統計の判定はしない）。
     確かめとして読むのは第1弾の読み 1 の命題だけ。学習データの率で、判例がその数以上になる確率が 0.05 未満なら
     「学習データほどは成り立っていない」、そうでなければ「学習データと矛盾しない」。残りは記録のみ
  B. 「範囲 = 種類、もし = 中日」の形の命題（D40・D86・D102）。差は元の命題の fisher_p で読む
     （0.05 未満なら「同じ種類の中でも、中日は多い」、0.05 以上なら「差は偶然の幅の中」）

第3弾（宣言は kind_reask_results/README.md の「第3弾」の節。計算の前のコミットで固定）:
  K85 の結論の列 wl_rf_win_gap（勝ち試合の得点 − 見込み）が、ほぼ全単位で負になる理由。保存済みの試合の記録から試合の表を作り、
  同じ sakanalytics.win_loss_split に、そのまま・ホームだけ・ビジターだけ・8 回まで、の 4 通りを渡す。
  読み（判定ではない）: 8 回までで負の単位が 65 % 以下なら 1（打ち切りが主な理由）、80 % 以上なら 3（打ち切りでは説明できない）、間は 2

第4弾（宣言は kind_reask_results/kind_reask_r4_propositions.toml の冒頭。刻印は同じ timestamp ファイル）:
  A. 2026年の表に、references/season-2026-central-summary.jsonl にある打撃の列（セ・リーグ 6 球団）を入れて、第2弾 A と同じ数え方をする
  B. 8 回までの得点で作り直した列 wl_rf_win_gap8 で、P85 を問い直す（E85・KE85・DE85。読み方は第1弾・第2弾 B と同じ）
  C. 「9 回まで」（延長に入った試合だけ 9 回終了時の得点に替えた表）を足して、片寄りを延長の分と 9 回の終わり方の分に分ける
     読み（判定ではない）: 9 回までで負の単位が 80 % 以上なら 1（主に 9 回の終わり方）、65 % 以下なら 3（主に延長）、間は 2（両方）

ゲート（通らなければ、命題の結果は出さずに止まる）:
  正本の命題ファイルの sha256 が保存された値と同じ。つなげたファイルが読み込める。
  K・D の命題が branch 側（from-cycle-001/propositions.toml）のどれとも同じ問いでない。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/kind_reask.py --outdir cycles/c001-chunichi/exploratory/kind_reask_results
"""
from __future__ import annotations

import argparse
import ast
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


def load_joined(canon: Path, extras: list[Path], P) -> list[list[dict]]:
    """正本の後ろに追加の命題ファイルを順につなげて、正本と同じ読み込みに通す。戻り値は、追加のファイルごとの命題。"""
    ids = [[p["id"] for p in tomllib.loads(f.read_text(encoding="utf-8")).get("proposition", [])] for f in extras]
    with tempfile.TemporaryDirectory() as tmp:
        joined = Path(tmp) / "joined.toml"
        joined.write_bytes(b"\n".join(f.read_bytes() for f in (canon, *extras)))
        by_id = {p["id"]: p for p in P.load(joined)[0]}
    return [[by_id[i] for i in group] for group in ids]


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


def confirm_new_season(props: list[dict], trained: dict[str, dict], targets: list[str], full, panel: Path, P, pl,
                       overlay: Path | None = None) -> dict:
    """第2弾 A: 学習データに無い年の単位（panel）で、命題ごとに 成立／判例／逆の判例／どちらも当たらない／判定不能 を数える。

    trained は学習データでの各形の数（{id: {form: {n, hold}}}）。そこからの見込みと、判例がその数以上になる確率を添える。
    読み（targets だけ。判定ではない）: 0 判定不能 / 1 学習データと矛盾しない / 2 学習データほどは成り立っていない。
    """
    new = pl.read_ndjson(panel)
    missing = sorted(c for c in full.columns if c not in new.columns)   # 試合の記録だけでは作れない列。空にして、判定不能に数える
    new = new.with_columns([pl.lit(None).alias(c) for c in missing])
    filled = None
    if overlay is not None:                      # 第4弾 A: 別に保存された年成績にある列だけを、同じ球団・同じ年の行に入れる
        extra = [json.loads(x) for x in overlay.read_text(encoding="utf-8").splitlines() if x.strip()]
        cols = sorted(c for c in missing if all(c in r for r in extra))
        same = ("G", "W", "L", "T", "RF", "RA", "rank", "upper_half")
        base = {(r["team"], r["season"]): r for r in new.select("team", "season", *same).to_dicts()}
        agree = all((r["team"], r["season"]) in base and all(base[(r["team"], r["season"])][k] == r[k] for k in same) for r in extra)
        filled = {"teams": sorted(r["team"] for r in extra), "columns": cols, "agrees_with_panel": agree}
        if agree and cols:                       # 勝敗・得点・順位が 2026年の表と合わなければ入れない
            add = pl.DataFrame([{"team": r["team"], "season": r["season"], **{c: float(r[c]) for c in cols}} for r in extra])
            new = new.drop(cols).join(add.cast({"season": new.schema["season"]}), on=["team", "season"], how="left")
    seasons = sorted(new["season"].unique().to_list())
    key = {"成立": "hold", "判例": "counter", "逆の判例": "converse_counter", "どちらも当たらない": "neither", "判定不能": "undetermined"}
    rows = []
    for p in props:
        check = P.confirm_units(p, new, seasons)
        units = {v: sorted(u["unit"] for u in check["units"] if u["status"] == k) for k, v in key.items()}
        c = {k: len(v) for k, v in units.items()}
        sides = {}
        for side, form, got, n in (("counter", "original", c["counter"], c["hold"] + c["counter"]),
                                   ("converse_counter", "inverse", c["converse_counter"], c["converse_counter"] + c["neither"])):
            f = trained[p["id"]].get(form)
            rate = None if f is None or not f["n"] else 1 - f["hold"] / f["n"]      # 学習データでの判例の率
            tail = None if rate is None else P.sigma_stats(got, n, rate)["p_above"]
            # 浮動小数の和は Python の版で最後の桁が変わる（3.12 から sum が補正つき）。保存する値は 9 桁に丸める
            sides[side] = {"n": n, "got": got, "trained_rate": rate, "expected": None if rate is None else round(n * rate, 9),
                           "p_at_least": None if tail is None else round(tail, 9),
                           "new_where_none_trained": bool(got) and rate == 0}
        row = {"id": p["id"], "role": "confirm" if p["id"] in targets else "record", "in_scope": len(check["units"]),
               "counts": c, "units": units, "sides": sides, "reading": None}
        if row["role"] == "confirm":
            decided = c["hold"] + c["counter"] + c["converse_counter"] + c["neither"]
            low = [x["p_at_least"] for x in sides.values() if x["p_at_least"] is not None and x["got"]]
            worse = any(x < ALPHA for x in low) or any(x["new_where_none_trained"] for x in sides.values())
            row["reading"] = 0 if not decided else 2 if worse else 1
        rows.append(row)
    out = {"seasons": seasons, "units": sorted(f"{t}-{s}" for t, s in new.select("team", "season").iter_rows()),
           "missing_columns": len(missing), "missing_prefixes": sorted({c.split("_")[0] for c in missing}), "rows": rows}
    return out if filled is None else {**out, "overlay": filled}


def difference_row(p: dict, r: dict, stored_parent: dict) -> dict:
    """第2弾 B: 「範囲 = 種類、もし = 中日」の命題の結果。中日と、中日以外の同じ種類の数を並べ、差は元の命題の fisher_p で読む。"""
    forms = {f["form"]: form_summary(f) for f in r["forms"]}
    m = r["forms"][0]["metrics"]                 # 元の命題: tp・fp が中日、fn・tn が中日以外の同じ種類
    others = {"hold": m["fn"], "n": m["fn"] + m["tn"]}
    pf = {f["form"]: f for f in stored_parent["forms"]}
    return {"id": p["id"], "statement": p["statement"], "strength": p["strength"], "key": r["key"], "signature": r["signature"],
            "definition_sha256": r["definition_sha256"], "parent": p["parent"],
            "parent_original": {"n": pf["original"]["n"], "hold": pf["original"]["hold"]},
            "units": r["units"], "forms": forms, "skipped_forms": r["skipped_forms"],
            "chunichi": {"hold": forms["original"]["hold"], "n": forms["original"]["n"]}, "others": others,
            "fisher_p": forms["original"]["fisher_p"], "reading": 1 if forms["original"]["fisher_p"] < ALPHA else 2,
            "judgement": {k: r["judgement"][k] for k in ("code", "stage", "form")}}


def predictions_r2(confirm: dict, diff: list[dict]) -> list[dict]:
    """第2弾の宣言の予想 (A1)〜(A4)・(B1)・(B2) の当たり外れ。判定には使わない。"""
    by = {r["id"]: r for r in confirm["rows"]}
    ks = [r for r in confirm["rows"] if r["id"].startswith("K")]
    blank = sorted((r["id"] for r in ks if r["counts"]["undetermined"] == r["in_scope"]), key=lambda s: int(s[1:]))
    k85 = by["K85"]["counts"]
    ps = {d["id"]: d["fisher_p"] for d in diff}
    return [
        {"id": "A1", "text": "K51: 成立 6・判例 0・逆の判例 0・どちらも当たらない 6。読みは 1（学習データと矛盾しない）",
         "ok": [by["K51"]["counts"][k] for k in ("hold", "counter", "converse_counter", "neither")] == [6, 0, 0, 6] and by["K51"]["reading"] == 1,
         "got": {**by["K51"]["counts"], "reading": by["K51"]["reading"]}},
        {"id": "A2", "text": "K32: 12 単位とも判定不能", "ok": by["K32"]["counts"]["undetermined"] == 12, "got": by["K32"]["counts"]},
        {"id": "A3", "text": "全単位が判定不能なのは K25〜K29・K31・K32・K40・K45・K46 の 10 件。残り 12 件は判定できる",
         "ok": blank == ["K25", "K26", "K27", "K28", "K29", "K31", "K32", "K40", "K45", "K46"]
         and all(r["counts"]["undetermined"] == 0 for r in ks if r["id"] not in blank), "got": blank},
        {"id": "A4", "text": "K85: 結論は 12 単位のうち 10 以上で成り立ち、A クラスと B クラスで 1 単位より大きくは違わない",
         "ok": k85["hold"] + k85["converse_counter"] >= 10 and abs(k85["hold"] - k85["converse_counter"]) <= 1, "got": k85},
        {"id": "B1", "text": "D40・D86・D102 の fisher_p は、3 件とも 0.05 に届かない", "ok": all(v >= ALPHA for v in ps.values()), "got": ps},
        {"id": "B2", "text": "0.05 に最も遠いのは D40", "ok": max(ps, key=ps.get) == "D40", "got": max(ps, key=ps.get)},
    ]


def win_runs_gap(repo: Path, full, skip: list[int], pl) -> tuple[dict, dict]:
    """第3弾: 勝ち試合の得点 − 見込み（wl_rf_win_gap）を、4 通りの試合の表で作り直す。skip は分析から除く年。

    2 つ目の戻り値は第4弾の材料: 「9 回まで」の表の集計、試合の終わり方の件数、単位ごとの「8 回まで」の値。
    """
    for d in (HERE, repo / "sakanalytics"):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    import games_table_from_observed as GT
    import sakanalytics as SA
    raw = json.loads((repo / "cycles/c001-chunichi/recovered-inputs/observed/games_raw.json").read_text(encoding="utf-8"))
    table = full.select("season", "team", "league", "G", "wl_rf_win_gap").to_dicts()
    league = {(r["season"], r["team"]): r["league"] for r in table}
    games = GT.from_games_raw(raw, GT.games_per_team(table))                 # 2013〜2025年の公式戦（試合数は確定済みの G と一致）
    by_key = {x["url"].rsplit("/", 1)[-1].removesuffix(".html"): x for x in raw if GT.FIRST <= x["year"] <= GT.LAST}

    def innings(v):
        return ast.literal_eval(v) if isinstance(v, str) else v

    def first8(v):                                                           # 1〜8 回の得点。8 回に届かない試合は空
        return sum(v[:8]) if len(v) >= 8 and all(isinstance(x, int) for x in v[:8]) else None

    def upto9(v):                                                            # 9 回終了時の得点（X は 0）
        return sum(x for x in v[:9] if isinstance(x, int))

    rows, endings = [], dict.fromkeys(("no_bottom9", "walkoff9", "extra", "other"), 0)
    for gm in games:
        x, season = by_key[gm["key"]], int(gm["date"][:4])
        hi, ai = innings(x["home_inn"]), innings(x["away_inn"])
        h8, a8, extra = first8(hi), first8(ai), len(ai) > 9
        h9, a9 = (upto9(hi), upto9(ai)) if extra else (gm["hs"], gm["as"])   # 延長に入った試合だけ、9 回終了時の得点に替える
        nine = len(ai) == 9 and len(hi) == 9
        endings["extra" if extra else "no_bottom9" if nine and hi[8] == "X" else
                "walkoff9" if nine and h8 is not None and gm["hs"] > gm["as"] and h8 <= gm["as"] else "other"] += 1
        for team, rf, ra, f8, r8, f9, r9, is_home in ((gm["home"], gm["hs"], gm["as"], h8, a8, h9, a9, True),
                                                       (gm["away"], gm["as"], gm["hs"], a8, h8, a9, h9, False)):
            rows.append({"season": season, "team": team, "league": league[(season, team)], "rf": rf, "ra": ra,
                         "rf8": f8, "ra8": r8, "rf9": f9, "ra9": r9, "is_home": is_home})
    tg = pl.DataFrame(rows, schema_overrides={"season": pl.Int32})
    whole = tg.filter(pl.col("rf8").is_not_null() & pl.col("ra8").is_not_null())
    tables = {"full": tg, "home": tg.filter(pl.col("is_home")), "away": tg.filter(~pl.col("is_home")),
              "eight": whole.with_columns(rf=pl.col("rf8"), ra=pl.col("ra8")), "nine": tg.with_columns(rf=pl.col("rf9"), ra=pl.col("ra9"))}
    out = {"units": 0, "games": len(games), "games_short_of_eight": len(games) - whole.height // 2, "variants": {}}
    more = {"endings": endings}
    for name, t in tables.items():
        got = {(r["season"], r["team"]): r for r in SA.win_loss_split(t).to_dicts()}
        if name == "full":                                                   # ゲート: 保存された値を作り直せるか（除く年も含めて比べる）
            diffs = [abs(got[k]["wl_rf_win_gap"] - r["wl_rf_win_gap"]) for r in table
                     if (k := (r["season"], r["team"])) in got and r["wl_rf_win_gap"] is not None]
            out["gate"] = {"compared": len(diffs), "max_abs_diff": round(max(diffs), 12), "ok": max(diffs) <= 1e-9}
        win = sorted(v["wl_rf_win_gap"] for k, v in got.items() if k[0] not in skip)
        loss = [v["wl_rf_loss_gap"] for k, v in got.items() if k[0] not in skip]
        out["units"] = len(win)
        mid = (win[(len(win) - 1) // 2] + win[len(win) // 2]) / 2
        stats = {"negative": sum(x < 0 for x in win), "share_negative": round(sum(x < 0 for x in win) / len(win), 9),
                 "median_gap": round(mid, 9), "min_gap": round(win[0], 9), "max_gap": round(win[-1], 9),
                 "loss_gap_positive": sum(x > 0 for x in loss)}
        if name == "nine":                                                   # 第4弾 C の表。第3弾の出力には入れない
            more["nine"] = stats
            continue
        out["variants"][name] = stats
        if name == "eight":
            more["gap8"] = [{"season": k[0], "team": k[1], "wl_rf_win_gap8": v["wl_rf_win_gap"]} for k, v in sorted(got.items())]
    v = out["variants"]
    share = v["eight"]["share_negative"]
    out["reading"] = 1 if share <= 0.65 else 3 if share >= 0.80 else 2
    out["predictions"] = [
        {"id": "C1", "text": "保存された wl_rf_win_gap（2013〜2025年の 156 単位）を 1e-9 以内で作り直せる",
         "ok": out["gate"]["ok"] and out["gate"]["compared"] == 156, "got": out["gate"]},
        {"id": "C2", "text": "ホームだけ: 負の単位が 85 % 以上", "ok": v["home"]["share_negative"] >= 0.85, "got": v["home"]["share_negative"]},
        {"id": "C3", "text": "ビジターだけ: 負の単位は 70 % 未満", "ok": v["away"]["share_negative"] < 0.70, "got": v["away"]["share_negative"]},
        {"id": "C4", "text": "8 回まで: 負の単位は 35〜65 %", "ok": 0.35 <= share <= 0.65, "got": share},
    ]
    return out, more


def round_four(fs: list[dict], evaluated: dict[str, dict], confirm: dict, third: dict, more: dict) -> dict:
    """第4弾のまとめ。A: 打撃を足した 2026年の数、B: 8 回までの列での 3 命題、C: 片寄りを延長と 9 回の終わり方に分ける。"""
    by = {r["id"]: r for r in confirm["rows"]}
    props = {}
    for p in fs:
        r = evaluated[p["id"]]
        q = {"id": p["id"], "statement": p["statement"], "key": r["key"], "signature": r["signature"],
             "definition_sha256": r["definition_sha256"], "parent": p["parent"], "units": r["units"],
             "forms": {f["form"]: form_summary(f) for f in r["forms"]}, "judgement": {k: r["judgement"][k] for k in ("code", "stage", "form")}}
        if r["held_out"]:                                                    # 第1弾の形: 中日以外で読む
            q |= {"held_out": form_summary(r["held_out"]), "reading": reading(r["held_out"])}
        if r["skipped_forms"]:                                               # 第2弾 B の形: 差は fisher_p で読む
            q |= difference_row(p, r, evaluated[p["parent"]]) | {"forms": q["forms"]}
        props[p["id"]] = q
    full, nine, eight = third["variants"]["full"], more["nine"], third["variants"]["eight"]
    span = full["median_gap"] - eight["median_gap"]
    split = {"units": third["units"], "endings": more["endings"], "nine": nine,
             "share_of_gap_from_extras": round((full["median_gap"] - nine["median_gap"]) / span, 9),
             "share_of_gap_from_ninth": round((nine["median_gap"] - eight["median_gap"]) / span, 9),
             "reading": 1 if nine["share_negative"] >= 0.80 else 3 if nine["share_negative"] <= 0.65 else 2}
    e85 = props["E85"]["forms"]["original"]
    counts = lambda i: [by[i]["counts"][k] for k in ("hold", "counter", "converse_counter", "neither", "undetermined")]  # noqa: E731
    preds = [
        {"id": "A1", "text": "K32: 成立 2・判例 0・逆の判例 2・どちらも当たらない 2・判定不能 6。読みは 1",
         "ok": counts("K32") == [2, 0, 2, 2, 6] and by["K32"]["reading"] == 1, "got": {**by["K32"]["counts"], "reading": by["K32"]["reading"]}},
        {"id": "A2", "text": "K31: 成立 2・判例 0・逆の判例 1・どちらも当たらない 3・判定不能 6", "ok": counts("K31") == [2, 0, 1, 3, 6],
         "got": by["K31"]["counts"]},
        {"id": "B1", "text": "E85: 中日の 12 単位のうち負は 4〜8。元の命題の終了コードは 0・1 にならない",
         "ok": e85["n"] == 12 and 4 <= e85["hold"] <= 8 and e85["code"] not in (0, 1), "got": {k: e85[k] for k in ("hold", "n", "code")}},
        {"id": "B2", "text": "DE85: fisher_p は 0.05 以上", "ok": props["DE85"]["fisher_p"] >= ALPHA, "got": props["DE85"]["fisher_p"]},
        {"id": "B3", "text": "KE85: 読みは 1 にならない", "ok": props["KE85"]["reading"] != 1, "got": props["KE85"]["reading"]},
        {"id": "C1", "text": "9 回まで: 負の単位は 80 % 以上", "ok": nine["share_negative"] >= 0.80, "got": nine["share_negative"]},
        {"id": "C2", "text": "9 回まで: 差の中央値は −0.25〜−0.10 点", "ok": -0.25 <= nine["median_gap"] <= -0.10, "got": nine["median_gap"]},
    ]
    return {"confirm": confirm, "propositions": list(props.values()), "split": split, "predictions": preds}


def analyze(repo: Path = ROOT, season: Path | None = None, config: Path | None = None, props: Path | None = None,
            extra: Path | None = None, stored: Path | None = None, branch: Path | None = None,
            second: Path | None = None, panel: Path | None = None, fourth: Path | None = None,
            central: Path | None = None) -> dict:
    pl, P, PD = load_modules(repo)
    base = repo / "cycles" / "c001-chunichi"
    season, config = season or base / "outputs" / "season.jsonl", config or base / "analysis.toml"
    props, stored = props or base / "propositions.toml", stored or base / "outputs" / "propositions.jsonl"
    extra = extra or HERE / "kind_reask_results" / "kind_reask_propositions.toml"
    branch = branch or base / "from-cycle-001" / "propositions.toml"
    second = second or HERE / "kind_reask_results" / "kind_reask_r2_propositions.toml"
    panel = panel or HERE / "r18_partial_results" / "r18_partial_panel_2026.jsonl"
    fourth = fourth or HERE / "kind_reask_results" / "kind_reask_r4_propositions.toml"
    central = central or base / "references" / "season-2026-central-summary.jsonl"
    stored_rows = {r["id"]: r for r in map(json.loads, stored.read_text(encoding="utf-8").splitlines())}
    sha = hashlib.sha256(props.read_bytes()).hexdigest()
    out = {"inputs": {"season": rel(season, repo), "propositions": rel(props, repo), "propositions_sha256": sha,
                      "kind_propositions": rel(extra, repo),
                      "kind_propositions_sha256": hashlib.sha256(extra.read_bytes()).hexdigest(),
                      "stored": rel(stored, repo), "branch": rel(branch, repo),
                      "second_propositions": rel(second, repo),
                      "second_propositions_sha256": hashlib.sha256(second.read_bytes()).hexdigest(),
                      "panel": rel(panel, repo), "panel_sha256": hashlib.sha256(panel.read_bytes()).hexdigest(),
                      "fourth_propositions": rel(fourth, repo),
                      "fourth_propositions_sha256": hashlib.sha256(fourth.read_bytes()).hexdigest(),
                      "central": rel(central, repo), "central_sha256": hashlib.sha256(central.read_bytes()).hexdigest()},
           "gate": {"ok": True, "problems": []}, "propositions": [], "predictions": [], "summary": {}, "second": {}, "third": {},
           "fourth": {}}
    problems = out["gate"]["problems"]
    stored_sha = {r["meta"]["sha256"] for r in stored_rows.values()}
    if sha not in stored_sha:
        problems.append(f"命題ファイルの sha256 {sha} が保存された値 {sorted(stored_sha)} にない")
    try:
        ks, ds, fs = load_joined(props, [extra, second, fourth], P)
    except P.PropositionError as e:
        problems.append(f"つなげた命題ファイルが読み込めない: {e}")
        ks, ds, fs = [], [], []
    branch_sig = {P.identity(p)["signature"]: p["id"] for p in P.load(branch)[0]} if branch.exists() else {}
    for p in [*ks, *ds, *fs]:
        other = branch_sig.get(P.identity(p)["signature"])
        if other:
            problems.append(f"{p['id']}: branch 側の {other} と同じ問い（{P.identity(p)['key']}）")
    for p in ks:
        if not p.get("motivated_by") or not p.get("parent"):
            problems.append(f"{p['id']}: parent と motivated_by が必要（中日の単位を見て書いた命題）")
    for p in ds:
        if not p.get("parent") or not p.get("skip_forms") or p.get("motivated_by"):
            problems.append(f"{p['id']}: parent と skip_forms が必要で、motivated_by は書かない（見た単位そのもので作った形）")
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

    # ---- 第2弾: A（2026年の単位で照らす）と B（中日と、中日以外の同じ種類の差）
    diff_results = {p["id"]: P.evaluate(p, included, excluded, focus) for p in ds}
    diff = [difference_row(p, diff_results[p["id"]], stored_rows[p["parent"]]) for p in ds]
    trained = {q["id"]: {f: {"n": v["n"], "hold": v["hold"]} for f, v in q["forms"].items()} for q in [*rows.values(), *diff]}
    targets = [q["id"] for q in rows.values() if q["reading"] == 1]
    confirm = confirm_new_season([*ks, *ds], trained, targets, full, panel, P, pl)
    preds = predictions_r2(confirm, diff)
    out["second"] = {"confirm": confirm, "difference": diff, "predictions": preds,
                     "summary": {"confirm_targets": targets,
                                 "confirm_readings": {r["id"]: r["reading"] for r in confirm["rows"] if r["role"] == "confirm"},
                                 "difference_readings": {d["id"]: d["reading"] for d in diff},
                                 "predictions_ok": sum(x["ok"] for x in preds), "predictions": len(preds)}}
    out["third"], more = win_runs_gap(repo, full, [int(e["season"]) for e in exclusions], pl)

    # ---- 第4弾: 打撃を足した 2026年の数・8 回までの列での命題・片寄りの分け方
    gap8 = pl.DataFrame(more["gap8"]).cast({"season": full.schema["season"]})
    with8 = [t.join(gap8, on=["season", "team"], how="left") for t in (included, excluded)]
    evaluated = {r["id"]: r for r in map(json.loads, stored.read_text(encoding="utf-8").splitlines())}   # 親が正本の命題のとき
    evaluated |= {p["id"]: P.evaluate(p, *with8, focus) for p in fs}
    confirm4 = confirm_new_season([*ks, *ds], trained, targets, full, panel, P, pl, overlay=central)
    out["fourth"] = round_four(fs, evaluated, confirm4, out["third"], more)
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

    two = res["second"]
    c = two["confirm"]
    num = lambda x, fmt: "-" if x is None else format(x, fmt)  # noqa: E731
    L += ["", f"# 第2弾 A: まだ使っていない年（{'、'.join(map(str, c['seasons']))}年）の {len(c['units'])} 単位で照らす", "",
          f"試合の記録だけから作った表を使う。この表に無い {c['missing_columns']} 列（{'、'.join(p + '_*' for p in c['missing_prefixes'])}）は空で、"
          "その列を使う命題は判定不能。統計の判定はしない。見込みは、学習データでの判例の率を当てたもの。", "",
          "| 命題 | 扱い | 成立 | 判例（見込み・その数以上の確率） | 逆の判例（見込み・その数以上の確率） | どちらも当たらない | 判定不能 | 読み |",
          "|---|---|---|---|---|---|---|---|"]
    reading_ja = {None: "—", 0: "0 判定不能", 1: "1 学習データと矛盾しない", 2: "2 学習データほどは成り立っていない"}
    for r in c["rows"]:
        n, sd = r["counts"], r["sides"]
        side = lambda k: (f"{sd[k]['got']}{'（' + '・'.join(r['units'][k]) + '）' if r['units'][k] else ''}"  # noqa: E731
                          f"（{num(sd[k]['expected'], '.2f')}・{num(sd[k]['p_at_least'], '.2f')}）")
        L += [f"| {r['id']} | {'確かめ' if r['role'] == 'confirm' else '記録のみ'} | {n['hold']} | {side('counter')} | {side('converse_counter')} "
              f"| {n['neither']} | {n['undetermined']} | {reading_ja[r['reading']]} |"]
    L += ["", "# 第2弾 B: 中日と、中日以外の同じ種類の差", "",
          "形は「範囲 = 種類、もし = 中日」。逆・裏は省く。差は元の命題の fisher_p で読む（判定ではない）。", "",
          "| 命題 | 親 | 中日 | 中日以外の同じ種類 | 元 | 対偶 | fisher_p | 読み |", "|---|---|---|---|---|---|---|---|"]
    for d in two["difference"]:
        a, b = d["chunichi"], d["others"]
        L += [f"| {d['id']} {d['statement']} | {d['parent']} | {a['hold']}/{a['n']}（{a['hold'] / a['n']:.2f}） | {b['hold']}/{b['n']}（{b['hold'] / b['n']:.2f}） "
              f"| {_cell(d['forms']['original'])} | {_cell(d['forms']['contrapositive'])} | {d['fisher_p']:.4f} "
              f"| **{d['reading']}** {'同じ種類の中でも、中日は多い' if d['reading'] == 1 else '差は偶然の幅の中'} |"]
    ts = two["summary"]
    L += ["", f"## 第2弾の予想の当たり外れ（判定には使わない）: {ts['predictions_ok']}/{ts['predictions']}", ""]
    for x in two["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    t = res["third"]
    names = {"full": "そのまま", "home": "ホームだけ", "away": "ビジターだけ", "eight": "8 回まで"}
    L += ["", "# 第3弾: 勝ち試合の得点 − 見込み（wl_rf_win_gap）が片側に寄る理由", "",
          f"保存済みの試合の記録 {t['games']} 試合（8 回に届かない {t['games_short_of_eight']} 試合は「8 回まで」から外す）。単位は {t['units']} 球団年。",
          f"ゲート（保存された値を作り直せるか）: {t['gate']['compared']} 単位、差の最大 {t['gate']['max_abs_diff']:.1e}。", "",
          "| 表 | 負の単位 | 割合 | 差の中央値 | 最小 | 最大 | 負け試合の差が正の単位 |", "|---|---|---|---|---|---|---|"]
    for k, name in names.items():
        v = t["variants"][k]
        L += [f"| {name} | {v['negative']}/{t['units']} | {v['share_negative']:.2f} | {v['median_gap']:+.3f} | {v['min_gap']:+.3f} | {v['max_gap']:+.3f} "
              f"| {v['loss_gap_positive']}/{t['units']} |"]
    L += ["", f"読み（判定ではない）: **{t['reading']}** "
          + {1: "打ち切りが主な理由", 2: "打ち切りは理由の一部", 3: "打ち切りでは説明できない"}[t["reading"]], "",
          f"## 第3弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in t['predictions'])}/{len(t['predictions'])}", ""]
    for x in t["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f4 = res["fourth"]
    c4 = f4["confirm"]
    ov = c4["overlay"]
    L += ["", "# 第4弾 A: 2026年の表に、セ・リーグの打撃の列を足して数え直す", "",
          f"入れた列: {'、'.join(ov['columns'])}（{len(ov['teams'])} 球団。勝敗・得点・順位は 2026年の表と{'一致' if ov['agrees_with_panel'] else '不一致'}）。"
          "パ・リーグの 6 球団は空のまま。第2弾 A と値が変わる命題だけを並べる。", "",
          "| 命題 | 扱い | 成立 | 判例（見込み・その数以上の確率） | 逆の判例（見込み・その数以上の確率） | どちらも当たらない | 判定不能 | 読み |",
          "|---|---|---|---|---|---|---|---|"]
    before = {r["id"]: r["counts"] for r in c["rows"]}
    for r in c4["rows"]:
        if r["counts"] == before[r["id"]]:
            continue
        n, sd = r["counts"], r["sides"]
        side = lambda k: (f"{sd[k]['got']}{'（' + '・'.join(r['units'][k]) + '）' if r['units'][k] else ''}"  # noqa: E731
                          f"（{num(sd[k]['expected'], '.2f')}・{num(sd[k]['p_at_least'], '.2f')}）")
        L += [f"| {r['id']} | {'確かめ' if r['role'] == 'confirm' else '記録のみ'} | {n['hold']}{'（' + '・'.join(r['units']['hold']) + '）' if r['units']['hold'] else ''} "
              f"| {side('counter')} | {side('converse_counter')} | {n['neither']} | {n['undetermined']} | {reading_ja[r['reading']]} |"]
    L += ["", "# 第4弾 B: 8 回までの得点で作り直した列（wl_rf_win_gap8）で P85 を問い直す", ""]
    for q in f4["propositions"]:
        L += [f"- **{q['id']}** {q['statement']}（親 {q['parent']}。総合の終了コード {q['judgement']['code']}）: "
              + "、".join(f"{FORM_JA[k]} {_cell(v)}" for k, v in q["forms"].items())
              + (f"。中日以外 {q['held_out']['hold']}/{q['held_out']['n']}（{q['held_out']['rate']:.2f}）、fisher_p {q['held_out']['fisher_p']:.2g}、"
                 f"読み **{q['reading']}** {READING_JA[q['reading']]}" if "held_out" in q else "")
              + (f"。中日 {q['chunichi']['hold']}/{q['chunichi']['n']}、中日以外の同じ種類 {q['others']['hold']}/{q['others']['n']}、fisher_p {q['fisher_p']:.3f}、"
                 f"読み **{q['reading']}** {'同じ種類の中でも、中日は多い' if q['reading'] == 1 else '差は偶然の幅の中'}" if "chunichi" in q else "")]
    sp = f4["split"]
    e = sp["endings"]
    L += ["", "# 第4弾 C: 片寄りを、延長の分と 9 回の終わり方の分に分ける", "",
          f"試合の終わり方: 9 回裏なし {e['no_bottom9']}、9 回のサヨナラ {e['walkoff9']}、延長 {e['extra']}、そのほか {e['other']}。", "",
          "| 表 | 負の単位 | 割合 | 差の中央値 |", "|---|---|---|---|"]
    for name, v in (("そのまま", t["variants"]["full"]), ("9 回まで（延長を外す）", sp["nine"]), ("8 回まで（9 回も外す）", t["variants"]["eight"])):
        L += [f"| {name} | {v['negative']}/{sp['units']} | {v['share_negative']:.2f} | {v['median_gap']:+.3f} |"]
    L += ["", f"差の中央値で見た内訳: 延長の分 {sp['share_of_gap_from_extras']:.0%}、9 回の終わり方の分 {sp['share_of_gap_from_ninth']:.0%}。",
          f"読み（判定ではない）: **{sp['reading']}** " + {1: "主に 9 回の終わり方", 2: "両方", 3: "主に延長"}[sp["reading"]], "",
          f"## 第4弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f4['predictions'])}/{len(f4['predictions'])}", ""]
    for x in f4["predictions"]:
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
