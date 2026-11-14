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

第5弾（宣言は kind_reask_results/README.md の「第5弾」の節。計算の前のコミットで固定。新しい命題もファイルも足さない）:
  1. win_loss_split の 4 つの「実際 − 見込み」の列を、そのまま・9 回まで・8 回までの表で見る（正の単位が 35〜65 % の外なら片寄り）
  2. その列を使う命題（P85・P86・P87・K85・K86・D86）に、列の値だけを替えた表を渡し、終了コードが変わるものを数える
     (a) そのまま / (b) 2012年を空にする / (c) 9 回までの値 / (d) 8 回までの値。変わる = どれかの形の終了コードが (b) と違う

第6弾（宣言は kind_reask_results/kind_reask_r6_propositions.toml の冒頭。刻印は同じ timestamp ファイル）:
  A. 8 回までの得点で作り直した wl_*8 の列（sakanalytics.win_loss_split_eighth。games_table_from_observed の --with-eighth の表から）で、E85・KE85・DE85 を評価し直し、
     E86・KE86・DE86 を足す。2026年の 858 試合からも同じ列を作り、6 命題を confirm_units で数える（記録のみ）
  B. 配分の効果（allocation_table）と作り直し（rank_probability）を、そのまま・9 回まで・8 回までの表で作り直す。
     読み: 正の単位が 35〜65 % の外なら片寄り、A クラスで正の割合 − B クラスで正の割合 が 0.30 以上なら強さに沿った寄り。
     その列を使う命題に、列の値だけを替えた表を渡し、終了コードが変わるものを数える（第5弾と同じ）

第7弾（宣言は kind_reask_results/README.md の「第7弾」の節。計算の前のコミットで固定）:
  配分の効果の強さに沿った寄りを、ホーム・ビジター別（alloc_net_home・away）と、9 回裏が無かった試合のホームの得点に
  同じリーグ・同じ年の 9 回表の得点の分布を補った見込み（imputed_allocation）で分ける。
  読み（判定ではない）: 補った表で alloc_net_strat の A − B が 0.20 以下なら 1（主に道具の側）、0.30 以上なら 3（9 回裏が無いことでは
  説明できない）、間は 2（両方）

第8弾（宣言は kind_reask_results/README.md の「第8弾」の節。計算の前のコミットで固定）:
  配分の効果の強さに沿った寄りの 9 回の分を、勝ち越し（8 回終了時か 9 回終了時か）と見込み（8 回までか 9 回までの得点か）の
  4 通りで分ける。読み: (9, 8) で A − B が 0.30 以上かつ (8, 9) で 0.20 以下なら 1（勝ち負けの側）、逆なら 3（得点の分布の側）、ほかは 2

第10弾（宣言は kind_reask_results/kind_reask_r10_propositions.toml の冒頭。刻印は同じ timestamp ファイル）:
  A. 境界を動かす。つまみ 1: 得点を「1〜N 回の点 + ε × (N+1) 回の点」にする（x = N + ε。9 + ε は延長の点に ε）。
     つまみ 2: 見込みの中の同点の組を、重み θ で半分は勝ち（1 点足す）・半分は負けに数える。片寄りの線を 0.60・0.65・0.70 にずらす
  B. 式1（P52）の結論を、翌年の B クラス・得失点差の順位に替えた命題（N0・N52・N52A・N52S・R52A）。
     読み（判定ではない）: 元の命題の fisher_p が 0.05 未満なら 1（条件が結論の割合を上げている）、そうでなければ 2

第11弾（宣言は kind_reask_results/kind_reask_r11_propositions.toml の冒頭。刻印は同じ timestamp ファイル）:
  A. 列を直す形を決める。θ = 1 の列（T85・KT85・DT85）と 8 回までの列（第4弾の E85・KE85・DE85）を同じ形で並べる。
     使える = 片寄りなし（負の割合 0.35〜0.65）・揺らしても同じ（θ = 1 − ε、8 + ε。小さい ε の 5 つで各形の終了コードが同じ）・
     元の並びを保つ（元の列との順位相関 0.80 以上）。両方使えて結論が同じなら θ = 1、違えば未決、片方だけならその列
  B. 配分が不利 ⇒ 翌年 A クラス（M52A）。その年の B クラス・A クラスに分けた形（M52B・M52U）。
     読みは第10弾 B のまま。条件に当たる単位が min_n 未満なら 5（保留）

第12弾（宣言は kind_reask_results/kind_reask_r12_propositions.toml の冒頭。刻印は同じ timestamp ファイル）:
  「B クラスの中で、配分が不利 ⇒ 翌年 A に戻る」（M52B）を、配分（不利か）と分布（sim_p_upper が 0.32 以上か）の 4 つのマスに分ける。
  G52H・G52L は分布をそろえて配分を、G52U・G52N は配分をそろえて分布を問う。読み: fisher_p が 0.05 未満の命題が
  配分の側だけなら 1、分布の側だけなら 3、両方なら 2、どちらにも無ければ 4（分けられない）

第13弾（宣言は kind_reask_results/README.md の「第13弾」の節。計算の前のコミットで固定）:
  見込みの同点を決めるときの、負け試合の側の置き方。つまみ 1: 延長で負けた側が足す点 λ。つまみ 2: 負けの側だけの重み θ負。
  4 つの列（勝ち・負けの得点の差、勝率の 2 つ）がどれも 0.35〜0.65 なら「通る」。決め方: λ > 0 で通る最小の値、
  無ければ θ負 = 0（通っていれば）、どちらも無ければ勧めない

ゲート（通らなければ、命題の結果は出さずに止まる）:
  正本の命題ファイルの sha256 が保存された値と同じ。つなげたファイルが読み込める。
  K・D の命題が branch 側（from-cycle-001/propositions.toml）のどれとも同じ問いでない。

年次シミュレーションの GIF（c1 の成果発表用。判定ではない）:
  各年のリーグごとに、最終順位の順に 6 球団を並べ、得点・失点の分布だけからシーズンを作り直したときに A クラスに入る確率
  （sim_p_upper）を棒にする。左の 3 本が A クラス。第1弾の K51（B クラス ⇔ この確率が 0.5 未満）が、年ごとにどれだけ成り立ったかを
  下の帯に積む。2012〜2025年は確定済みの season.jsonl、2026年（まだ使っていない年）は R18 の部分実行の表から。
  GIF の書き出し・読み戻し・名前の付け方は FluidFullSpeedSimulation の pixelwater（_gif・file_stem）を、作業ツリーの場所を
  --ffs で渡して使う（サイクル3 の outlet_units.py と同じ持ち込み方。リポジトリをまたいで再利用し、ここでは書かない）。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/kind_reask.py --outdir cycles/c001-chunichi/exploratory/kind_reask_results
  python cycles/c001-chunichi/exploratory/kind_reask.py --gif-dir cycles/c001-chunichi/exploratory/kind_reask_results \
      --ffs <FluidFullSpeedSimulation の作業ツリー>
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
import statistics
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
                       overlay: Path | None = None, columns=None) -> dict:
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
    if columns is not None:                      # 第6弾 A: 試合の記録から作った列を、同じ球団・同じ年の行に入れる
        cs = [c for c in columns.columns if c not in ("season", "team")]
        new = new.drop([c for c in cs if c in new.columns]).join(
            columns.cast({"season": new.schema["season"]}), on=["team", "season"], how="left")
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
        for team, opp, rf, ra, f8, r8, f9, r9, is_home in ((gm["home"], gm["away"], gm["hs"], gm["as"], h8, a8, h9, a9, True),
                                                            (gm["away"], gm["home"], gm["as"], gm["hs"], a8, h8, a9, h9, False)):
            rows.append({"season": season, "team": team, "opp": opp, "league": league[(season, team)], "rf": rf, "ra": ra,
                         "rf8": f8, "ra8": r8, "rf9": f9, "ra9": r9, "is_home": is_home})
    tg = pl.DataFrame(rows, schema_overrides={"season": pl.Int32})
    whole = tg.filter(pl.col("rf8").is_not_null() & pl.col("ra8").is_not_null())
    tables = {"full": tg, "home": tg.filter(pl.col("is_home")), "away": tg.filter(~pl.col("is_home")),
              "eight": whole.with_columns(rf=pl.col("rf8"), ra=pl.col("ra8")), "nine": tg.with_columns(rf=pl.col("rf9"), ra=pl.col("ra9"))}
    out = {"units": 0, "games": len(games), "games_short_of_eight": len(games) - whole.height // 2, "variants": {}}
    more = {"endings": endings, "tables": {k: tables[k] for k in ("full", "nine", "eight")}}   # 第6弾 B が同じ表を使う
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
        if name in ("full", "nine", "eight"):
            more.setdefault("units", {})[name] = got                         # 第5弾の材料: 単位ごとの 4 つの列
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


def summarize_props(fs: list[dict], evaluated: dict[str, dict]) -> dict[str, dict]:
    """命題ごとの結果のまとめ。きっかけ以外があれば第1弾の読み、逆・裏を省いた形なら第2弾 B の読みを添える。"""
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
    return props


def round_four(fs: list[dict], evaluated: dict[str, dict], confirm: dict, third: dict, more: dict) -> dict:
    """第4弾のまとめ。A: 打撃を足した 2026年の数、B: 8 回までの列での 3 命題、C: 片寄りを延長と 9 回の終わり方に分ける。"""
    by = {r["id"]: r for r in confirm["rows"]}
    props = summarize_props(fs, evaluated)
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


def swap_judge(props: list[dict], schema: dict, units: dict, stored: dict, tables: tuple, focus, P, pl) -> tuple[list[dict], list[str]]:
    """列（schema のキー）を使う命題に、列の値だけを替えた表を渡して判定し直す（第5弾・第6弾 B）。

    units は {表の名前: {(年, 球団): 行}}。(a) そのまま / (b) "full" / (c) "nine" / (d) "eight" の値に替える。記録の無い年は空になる。
    戻り値は（命題ごとの結果, ゲートの問題）。ゲート: 正本の命題は (a) が保存された判定と同じ。
    """
    cols = tuple(schema)

    def swapped(df, name):                       # 列の値だけを替えた表。記録の無い年（2012年）は空になる
        if name is None:
            return df
        rows = [{"season": k[0], "team": k[1], **{c: r[c] for c in cols}} for k, r in sorted(units[name].items())]
        new = pl.DataFrame(rows, schema_overrides=schema).cast({"season": df.schema["season"]})
        return df.drop(cols).join(new, on=["season", "team"], how="left")

    treatments = {"a": None, "b": "full", "c": "nine", "d": "eight"}
    used = [p for p in props if {c["col"] for c in [*P._if_conds(p), *p["then"], *(p.get("scope") or {}).get("where", [])]} & set(cols)]
    rows, problems = [], []
    for p in used:
        per = {}
        for t, name in treatments.items():
            r = P.evaluate(p, *(swapped(df, name) for df in tables), focus)
            per[t] = {"forms": {f["form"]: {k: f[k] for k in ("n", "hold", "undetermined", "code")} for f in r["forms"]},
                      "fisher_p": r["forms"][0]["fisher_p"], "judgement": r["judgement"]["code"],
                      "held_out": {k: r["held_out"][k] for k in ("n", "hold", "verdict")} if r["held_out"] else None}
        if p["id"] in stored:                    # ゲート: 正本の命題は、(a) が保存された判定と同じ
            want = {f["form"]: {k: f[k] for k in ("n", "hold", "undetermined", "code")} for f in stored[p["id"]]["forms"]}
            if per["a"]["forms"] != want:
                problems.append(f"{p['id']}: (a) が保存された判定と違う")
        diff = lambda t: sorted(f for f, v in per[t]["forms"].items() if v["code"] != per["b"]["forms"][f]["code"])  # noqa: E731
        rows.append({"id": p["id"], "statement": p["statement"], "key": P.identity(p)["key"], "treatments": per,
                     "changed_forms_c": diff("c"), "changed_forms_d": diff("d")})
    return rows, problems


def round_five(props: list[dict], stored: dict, tables: tuple, focus, units: dict, skip: list[int], P, pl) -> dict:
    """第5弾: 「実際 − 見込み」の 4 つの列の片寄りと、列の値だけを替えたときに終了コードが変わる命題。

    units は {表の名前: {(年, 球団): win_loss_split の行}}。tables は（分析に入る単位, 除外した年の単位）。
    """
    cols = ("wl_rf_win_gap", "wl_rf_loss_gap", "wl_wpct_low_gap", "wl_wpct_high_gap")
    bias = {}
    for col in cols:
        bias[col] = {}
        for name in ("full", "nine", "eight"):
            vals = sorted(r[col] for k, r in units[name].items() if k[0] not in skip and r[col] is not None)
            share = sum(x > 0 for x in vals) / len(vals)
            bias[col][name] = {"units": len(vals), "positive": sum(x > 0 for x in vals), "share_positive": round(share, 9),
                               "median": round((vals[(len(vals) - 1) // 2] + vals[len(vals) // 2]) / 2, 9),
                               "one_sided": not 0.35 <= share <= 0.65}

    rows, problems = swap_judge(props, dict.fromkeys(cols, pl.Float64), units, stored, tables, focus, P, pl)
    by = {r["id"]: r for r in rows}
    summary = {"propositions": [r["id"] for r in rows], "changed_c": [r["id"] for r in rows if r["changed_forms_c"]],
               "changed_d": [r["id"] for r in rows if r["changed_forms_d"]],
               "one_sided_full": [c for c in cols if bias[c]["full"]["one_sided"]],
               "one_sided_nine": [c for c in cols if bias[c]["nine"]["one_sided"]],
               "one_sided_eight": [c for c in cols if bias[c]["eight"]["one_sided"]]}
    loss9, p86 = bias["wl_rf_loss_gap"]["nine"]["share_positive"], by["P86"]["treatments"]["d"]["forms"]["original"]
    preds = [
        {"id": "F1", "text": "ゲート: (a) で P85・P86・P87 の各形の数と終了コードが、保存された値と同じ", "ok": not problems, "got": problems},
        {"id": "F2", "text": "負け試合の得点: 9 回までで正の単位は 45〜60 %", "ok": 0.45 <= loss9 <= 0.60, "got": loss9},
        {"id": "F3", "text": "勝率の 2 つの列は、そのままで片寄っていない",
         "ok": not bias["wl_wpct_low_gap"]["full"]["one_sided"] and not bias["wl_wpct_high_gap"]["full"]["one_sided"],
         "got": {c: bias[c]["full"]["share_positive"] for c in cols[2:]}},
        {"id": "F4", "text": "P86: 8 回までの値でも、中日の 12 単位のうち 8 以上で成り立つ", "ok": p86["n"] == 12 and p86["hold"] >= 8,
         "got": {k: p86[k] for k in ("hold", "n")}},
        {"id": "F5", "text": "D86: 8 回までの値で、fisher_p は 0.05 以上", "ok": by["D86"]["treatments"]["d"]["fisher_p"] >= ALPHA,
         "got": by["D86"]["treatments"]["d"]["fisher_p"]},
        {"id": "F6", "text": "6 件のうち、(d) で判定が変わるのは 3 件以上", "ok": len(summary["changed_d"]) >= 3, "got": summary["changed_d"]},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "bias": bias, "propositions": rows, "summary": summary, "predictions": preds}


PAIRED = ("alloc_net", "alloc_net_strat", "alloc_net_opp", "wpct_minus_sim")   # 第6弾 B で寄りを見る量（実際 − 見込み）


def lean(units: dict, col: str, upper: dict, skip: list[int]) -> dict:
    """正の単位の割合を、全体・A クラス・B クラスで。全体が 35〜65 % の外なら片寄り、A − B が 0.30 以上なら強さに沿った寄り（第6・7弾）。"""
    vals = [(r[col], upper[k]) for k, r in units.items() if k[0] not in skip and r[col] is not None]
    share = lambda xs: sum(x > 0 for x in xs) / len(xs)  # noqa: E731
    all_, a_, b_ = share([v for v, _ in vals]), share([v for v, u in vals if u]), share([v for v, u in vals if not u])
    xs = sorted(v for v, _ in vals)
    return {"units": len(vals), "share_positive": round(all_, 9), "share_positive_a": round(a_, 9),
            "share_positive_b": round(b_, 9), "a_minus_b": round(a_ - b_, 9),
            "median": round((xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2, 9),
            "one_sided": not 0.35 <= all_ <= 0.65, "strength_sided": a_ - b_ >= 0.30}


def paired_columns(t, pl, SA) -> dict:
    """第6弾 B: 1 つの試合の表から、配分の効果（alloc_*）と作り直し（sim_*）の列、実際の勝率 − sim_wpct を単位ごとに作る。"""
    a = SA.allocation_table(t).join(SA.rank_probability(t), on=["season", "team"], how="left")
    wl = t.group_by("season", "team").agg(w=(pl.col("rf") > pl.col("ra")).sum(), l_=(pl.col("rf") < pl.col("ra")).sum())
    a = a.join(wl, on=["season", "team"], how="left").with_columns(
        wpct_minus_sim=pl.col("w") / (pl.col("w") + pl.col("l_")) - pl.col("sim_wpct")).drop("w", "l_")
    return {(r["season"], r["team"]): r for r in a.to_dicts()}


def round_six(repo: Path, config: Path, full, tables: tuple, focus, fs: list[dict], gs: list[dict], evaluated: dict,
              round4: dict, more: dict, props: list[dict], stored: dict, skip: list[int], panel: Path, P, pl) -> dict:
    """第6弾。A: 試合の表から作り直した wl_*8 の列（sakanalytics.win_loss_split_eighth）で E85〜DE86、2026年は記録のみ。
    B: 配分の効果と作り直しの列の、延長による寄りと、その列を使う命題の判定の変化。"""
    import games_table_from_observed as GT
    import sakanalytics as SA
    base = repo / "cycles/c001-chunichi"
    teams = SA.load_config(config)["teams"]
    raw = json.loads((base / "recovered-inputs/observed/games_raw.json").read_text(encoding="utf-8"))
    g = GT.games_per_team(full.select("season", "team", "G").to_dicts())
    # sakanalytics の win_loss_split_eighth（SakAnalytics #43 を取り込んだ後は、道具の関数をそのまま使う）
    hist = SA.win_loss_split_eighth(SA.to_team_games(pl.DataFrame(GT.from_games_raw(raw, g, eighth=True)), teams))
    rows26 = [json.loads(x) for x in (base / "season-2026/observed/games.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    new26 = SA.win_loss_split_eighth(SA.to_team_games(pl.DataFrame(GT.from_season_games(rows26, eighth=True)), teams))

    # ---- A: ゲート（第4弾の、別の道筋で作った値と同じか）と、6 命題
    mine = {(r["season"], r["team"]): r["wl_rf_win_gap8"] for r in more["gap8"]}
    tool = {(r["season"], r["team"]): r["wl_rf_win_gap8"] for r in hist.to_dicts()}
    diffs = [abs(tool[k] - v) for k, v in mine.items() if v is not None]
    problems = [] if set(mine) == set(tool) and max(diffs) <= 1e-9 else ["試合の表から作った wl_rf_win_gap8 が第4弾の値と合わない"]
    w8 = hist.cast({"season": full.schema["season"]})
    with8 = [t.join(w8, on=["season", "team"], how="left") for t in tables]
    ev = dict(evaluated) | {p["id"]: P.evaluate(p, *with8, focus) for p in [*fs, *gs]}
    six = summarize_props([*fs, *gs], ev)
    old = {q["id"]: q for q in round4["propositions"]}
    for i, q in old.items():                     # 第4弾の E85・KE85・DE85 と、数・終了コードが同じ
        if {f: (v["n"], v["hold"], v["code"]) for f, v in q["forms"].items()} != {f: (v["n"], v["hold"], v["code"]) for f, v in six[i]["forms"].items()}:
            problems.append(f"{i}: 試合の表から作った列で評価し直すと、第4弾の結果と違う")
    trained = {i: {f: {"n": v["n"], "hold": v["hold"]} for f, v in q["forms"].items()} for i, q in six.items()}
    confirm = confirm_new_season([*fs, *gs], trained, [], full.join(w8, on=["season", "team"], how="left"), panel, P, pl,
                                 columns=new26)
    by26 = {r["id"]: r for r in confirm["rows"]}

    # ---- B: 配分の効果と作り直しの列
    units = {k: paired_columns(more["tables"][k], pl, SA) for k in ("full", "nine", "eight")}
    names = sorted(c for c in units["full"][next(iter(units["full"]))] if c.startswith(("alloc_", "sim_")))
    stored_rows = {(r["season"], r["team"]): r for r in full.select("season", "team", "upper_half", *names).to_dicts()}
    worst = 0.0
    for k, r in units["full"].items():           # ゲート: 「そのまま」の表から作った値が、保存された値と同じ
        for c in names:
            a, b = r[c], stored_rows[k][c]
            if (a is None) != (b is None) or (isinstance(a, bool) and a != b):
                problems.append(f"{k} {c}: 保存された値と違う（{a} と {b}）")
            elif a is not None and not isinstance(a, bool):
                worst = max(worst, abs(a - b))
    if worst > 1e-9:
        problems.append(f"alloc_*・sim_* の差の最大が {worst:.1e}")
    upper = {k: r["upper_half"] for k, r in stored_rows.items()}
    bias = {col: {name: lean(units[name], col, upper, skip) for name in ("full", "nine", "eight")} for col in PAIRED}
    schema = {c: (pl.Boolean if c == "alloc_same_sign" else pl.Float64) for c in names}
    rows, swap_problems = swap_judge(props, schema, units, stored, tables, focus, P, pl)
    problems += swap_problems
    changed_c, changed_d = [r["id"] for r in rows if r["changed_forms_c"]], [r["id"] for r in rows if r["changed_forms_d"]]

    ke = lambda i: by26[i]["counts"]  # noqa: E731
    preds = [
        {"id": "A1", "text": "ゲート: 試合の表から作った wl_rf_win_gap8 が第4弾の値と差 0、E85・KE85・DE85 は第4弾と同じ",
         "ok": not [x for x in problems if "第4弾" in x], "got": round(max(diffs), 12)},
        {"id": "A2", "text": "E86 は 12 中 8・終了コード 4、KE86 は 72 中 35・終了コード 3、DE86 の fisher_p は 0.146",
         "ok": (six["E86"]["forms"]["original"]["hold"], six["E86"]["forms"]["original"]["n"], six["E86"]["judgement"]["code"]) == (8, 12, 4)
         and (six["KE86"]["forms"]["original"]["hold"], six["KE86"]["forms"]["original"]["n"], six["KE86"]["judgement"]["code"]) == (35, 72, 3)
         and round(six["DE86"]["fisher_p"], 3) == 0.146,
         "got": {"E86": six["E86"]["forms"]["original"]["hold"], "KE86": six["KE86"]["forms"]["original"]["hold"], "DE86": six["DE86"]["fisher_p"]}},
        {"id": "A3", "text": "2026年の B クラス 6 単位で、8 回までの勝ち試合の得点が負なのは 2〜4、負け試合の得点が正なのも 2〜4",
         "ok": all(2 <= ke(i)["hold"] <= 4 and ke(i)["hold"] + ke(i)["counter"] == 6 for i in ("KE85", "KE86")),
         "got": {i: ke(i) for i in ("KE85", "KE86")}},
        {"id": "B1", "text": "ゲート: 「そのまま」の alloc_*・sim_* が保存された値と同じ", "ok": worst <= 1e-9 and not swap_problems,
         "got": {"max_abs_diff_below_1e-12": worst < 1e-12}},   # 差そのものは集計の順で最後の桁が揺れるので残さない
        {"id": "B2", "text": "「そのまま」で、4 つの量はどれも全体では片寄っていない", "ok": not any(bias[c]["full"]["one_sided"] for c in PAIRED),
         "got": {c: bias[c]["full"]["share_positive"] for c in PAIRED}},
        {"id": "B3", "text": "「そのまま」で、alloc_net_strat と「勝率 − sim_wpct」は強さに沿った寄り（A − B が 0.30 以上）",
         "ok": bias["alloc_net_strat"]["full"]["strength_sided"] and bias["wpct_minus_sim"]["full"]["strength_sided"],
         "got": {c: bias[c]["full"]["a_minus_b"] for c in ("alloc_net_strat", "wpct_minus_sim")}},
        {"id": "B4", "text": "「9 回まで」で、alloc_net_strat の A − B は「そのまま」より小さい",
         "ok": bias["alloc_net_strat"]["nine"]["a_minus_b"] < bias["alloc_net_strat"]["full"]["a_minus_b"],
         "got": [bias["alloc_net_strat"][k]["a_minus_b"] for k in ("full", "nine")]},
        {"id": "B5", "text": "13 件のうち、(c) で判定が変わるのは 2 件以上", "ok": len(rows) == 13 and len(changed_c) >= 2, "got": changed_c},
        {"id": "B6", "text": "P52（式1）は (c) でも終了コードが変わらない", "ok": "P52" not in changed_c, "got": "P52" in changed_c},
    ]
    return {"gate": {"ok": not problems, "problems": problems},
            "eighth": {"columns": sorted(c for c in hist.columns if c.startswith("wl_")), "units": hist.height,
                       "units_2026": new26.height, "max_abs_diff_vs_round_four": round(max(diffs), 12)},
            "propositions": [six[p["id"]] for p in [*fs, *gs]], "confirm_2026": confirm,
            "paired": {"columns": names, "bias": bias, "propositions": rows, "changed_c": changed_c, "changed_d": changed_d},
            "predictions": preds}


def _sign(x) -> int:
    return (x > 0) - (x < 0)


def imputed_allocation(games: list[dict], innings: dict, teams: dict, impute: bool = True) -> dict:
    """第7弾: 9 回裏が無かった試合（ホームの 9 回裏が X）で、ホームの得点に 9 回裏の点を補った配分の効果。

    補う点の分布は、同じリーグ（ホームのチームのリーグ）・同じ年の 9 回表の得点の分布。勝ち負けは変わらないので、
    実際の勝ち越しはそのまま。見込み（組み合わせだけランダム。sakanalytics.allocation と同じ式）に、点ごとの重みを入れる。
    impute=False なら補わない（保存された alloc_net_* と同じになるはず。ゲート）。サヨナラの試合は補わない。
    戻り値: {(年, 球団): {"alloc_net_home", "alloc_net_away", "alloc_net_strat"}} と、補った試合の数・9 回表の平均。
    """
    top9: dict[tuple, Counter] = {}
    for gm in games:
        a = innings[gm["key"]]["away"]
        if len(a) >= 9 and type(a[8]) is int:
            top9.setdefault((int(gm["date"][:4]), teams[gm["home"]]["league"]), Counter())[a[8]] += 1
    dist = {k: {v: c / sum(cnt.values()) for v, c in cnt.items()} for k, cnt in top9.items()}
    parts: dict[tuple, dict] = {}                # (年, 球団, "home"/"away") → {"rf": Counter, "ra": Counter, "net": int, "n": int}
    imputed = 0
    for gm in games:
        season, h = int(gm["date"][:4]), innings[gm["key"]]["home"]
        cut = impute and len(h) == 9 and h[8] == "X"                         # ホームは 9 回表の時点で勝っていて、9 回裏に入らなかった
        imputed += cut
        add = dist[(season, teams[gm["home"]]["league"])] if cut else {0: 1.0}
        for team, rf, ra, side in ((gm["home"], gm["hs"], gm["as"], "home"), (gm["away"], gm["as"], gm["hs"], "away")):
            q = parts.setdefault((season, team, side), {"rf": Counter(), "ra": Counter(), "net": 0, "n": 0})
            q["net"] += _sign(rf - ra)
            q["n"] += 1
            for k, w in add.items():             # 補う点はホームの得点に入る（ホームから見れば得点、ビジターから見れば失点）
                q["rf"][rf + (k if side == "home" else 0)] += w
                q["ra"][ra + (k if side == "away" else 0)] += w
    out = {}
    for (season, team, side), q in parts.items():
        exp = sum(wx * wy * _sign(x - y) for x, wx in q["rf"].items() for y, wy in q["ra"].items()) / q["n"]
        out.setdefault((season, team), {})[f"alloc_net_{side}"] = q["net"] - exp
    for r in out.values():                       # 試合の無い側は 0（sakanalytics.allocation の空の場合と同じ）
        r["alloc_net_strat"] = r.setdefault("alloc_net_home", 0.0) + r.setdefault("alloc_net_away", 0.0)
    means = {f"{s}-{lg}": round(sum(v * w for v, w in d.items()), 9) for (s, lg), d in sorted(dist.items())}
    return {"units": out, "imputed_games": imputed, "top9_mean": means}


def games_with_innings(repo: Path, full) -> tuple[list[dict], dict, dict]:
    """2013〜2025年の公式戦の試合の表と、試合ごとの回ごとの得点（{key: {"home": [...], "away": [...]}}）、球団の定義。"""
    import games_table_from_observed as GT
    import sakanalytics as SA
    base = repo / "cycles/c001-chunichi"
    teams = SA.load_config(base / "analysis.toml")["teams"]
    raw = json.loads((base / "recovered-inputs/observed/games_raw.json").read_text(encoding="utf-8"))
    games = GT.from_games_raw(raw, GT.games_per_team(full.select("season", "team", "G").to_dicts()))
    lit = lambda v: ast.literal_eval(v) if isinstance(v, str) else v  # noqa: E731
    innings = {x["url"].rsplit("/", 1)[-1].removesuffix(".html"): {"home": lit(x["home_inn"]), "away": lit(x["away_inn"])}
               for x in raw if GT.FIRST <= x["year"] <= GT.LAST}
    return games, innings, teams


def round_seven(repo: Path, full, more: dict, skip: list[int], pl) -> dict:
    """第7弾: 配分の効果の強さに沿った寄りを、ホーム・ビジター別と、9 回裏を補った見込みで分ける。"""
    import sakanalytics as SA
    games, innings, teams = games_with_innings(repo, full)
    cols = ("alloc_net_home", "alloc_net_away", "alloc_net_strat")
    stored = {(r["season"], r["team"]): r for r in full.select("season", "team", "upper_half", *cols).to_dicts()}
    upper = {k: r["upper_half"] for k, r in stored.items()}
    plain, filled = imputed_allocation(games, innings, teams, impute=False), imputed_allocation(games, innings, teams)
    worst = max(abs(plain["units"][k][c] - stored[k][c]) for k in plain["units"] for c in cols)
    problems = [] if worst <= 1e-9 and set(plain["units"]) <= set(stored) else [f"補わない見込みが保存された値と合わない（差の最大 {worst:.1e}）"]
    tables = {k: {(r["season"], r["team"]): r for r in SA.allocation_table(more["tables"][k]).to_dicts()} for k in ("full", "nine", "eight")}
    home_away = {c: {k: lean(tables[k], c, upper, skip) for k in ("full", "nine", "eight")} for c in cols}
    filled_lean = {c: lean(filled["units"], c, upper, skip) for c in cols}
    ab = filled_lean["alloc_net_strat"]["a_minus_b"]
    reading = 1 if ab <= 0.20 else 3 if ab >= 0.30 else 2
    ha = lambda c, k: home_away[c][k]["a_minus_b"]  # noqa: E731
    preds = [
        {"id": "G1", "text": "ゲート: 補わない見込みが、保存された alloc_net_home・away・strat と 1e-9 以内で一致", "ok": not problems,
         "got": {"max_abs_diff_below_1e-9": worst <= 1e-9}},
        {"id": "G2", "text": "そのままの表で、alloc_net_home と alloc_net_away の A − B はどちらも 0.20 以上",
         "ok": ha("alloc_net_home", "full") >= 0.20 and ha("alloc_net_away", "full") >= 0.20,
         "got": {c: ha(c, "full") for c in cols[:2]}},
        {"id": "G3", "text": "8 回までの表で、alloc_net_home と alloc_net_away の A − B はどちらもそのままより小さい",
         "ok": all(ha(c, "eight") < ha(c, "full") for c in cols[:2]), "got": {c: [ha(c, "full"), ha(c, "eight")] for c in cols[:2]}},
        {"id": "G4", "text": "補った表で、alloc_net_strat の A − B は 0.14 より大きく 0.35 より小さい", "ok": 0.14 < ab < 0.35, "got": ab},
        {"id": "G5", "text": "読みは「両方」", "ok": reading == 2, "got": reading},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "imputed_games": filled["imputed_games"], "games": len(games),
            "top9_mean": filled["top9_mean"], "home_away": home_away, "imputed": filled_lean, "reading": reading, "predictions": preds}


def round_eight(full, more: dict, skip: list[int], pl, upper: dict | None = None) -> dict:
    """第8弾: 配分の効果（ホーム・ビジター別の合計）を、勝ち越しと見込みを別々の回までの得点で作った 4 通りで並べる。

    8 回に届いた試合だけを使う。(r, d) = 勝ち越しを r 回終了時、見込みを d 回までの得点の分布で。
    8 回終了時の状態（リード・同点・ビハインド）ごとの 9 回終了時の結果も、A・B クラスで数える。
    upper は {(年, 球団): 上の群か}。渡さなければ最終順位（upper_half）。第9弾は、ここに別の群の決め方を渡す。
    """
    import sakanalytics as SA
    t = more["tables"]["full"].filter(pl.col("rf8").is_not_null() & pl.col("ra8").is_not_null())
    upper = upper or {(r["season"], r["team"]): r["upper_half"] for r in full.select("season", "team", "upper_half").to_dicts()}
    cells = {k: {} for k in ("8,8", "8,9", "9,8", "9,9")}
    states = {c: {s: Counter() for s in ("lead", "tie", "behind")} for c in ("A", "B")}
    for (season, team), g in t.group_by(["season", "team"], maintain_order=True):
        net, exp = {"8": 0, "9": 0}, {"8": 0.0, "9": 0.0}
        for venue in (True, False):
            part = g.filter(pl.col("is_home") == venue)
            for n in ("8", "9"):
                rf, ra = part[f"rf{n}"].to_list(), part[f"ra{n}"].to_list()
                net[n] += sum(_sign(a - b) for a, b in zip(rf, ra))
                exp[n] += SA.allocation(rf, ra)[0]
        for k in cells:
            cells[k][(season, team)] = {"alloc_net_strat": net[k[0]] - exp[k[2]]}
        if season not in skip:
            cls = "A" if upper[(season, team)] else "B"
            for a8, b8, a9, b9 in zip(g["rf8"].to_list(), g["ra8"].to_list(), g["rf9"].to_list(), g["ra9"].to_list()):
                states[cls][("behind", "tie", "lead")[_sign(a8 - b8) + 1]][("loss", "tie", "win")[_sign(a9 - b9) + 1]] += 1
    eight = {(r["season"], r["team"]): r["alloc_net_strat"] for r in SA.allocation_table(more["tables"]["eight"]).to_dicts()}
    worst = max(abs(cells["8,8"][k]["alloc_net_strat"] - v) for k, v in eight.items())
    problems = [] if worst <= 1e-9 and set(eight) == set(cells["8,8"]) else [f"(8, 8) が第6弾の 8 回までの値と合わない（差の最大 {worst:.1e}）"]
    leans = {k: lean(v, "alloc_net_strat", upper, skip) for k, v in cells.items()}
    ab = {k: v["a_minus_b"] for k, v in leans.items()}
    reading = 1 if ab["9,8"] >= 0.30 and ab["8,9"] <= 0.20 else 3 if ab["8,9"] >= 0.30 and ab["9,8"] <= 0.20 else 2
    rates = {}
    for cls, by in states.items():
        rates[cls] = {"lead_games": sum(by["lead"].values()), "lead_held": round(by["lead"]["win"] / sum(by["lead"].values()), 9),
                      "tie_games": sum(by["tie"].values()), "tie_decided": by["tie"]["win"] + by["tie"]["loss"],
                      "tie_won": round(by["tie"]["win"] / (by["tie"]["win"] + by["tie"]["loss"]), 9),
                      "behind_games": sum(by["behind"].values()), "behind_won": round(by["behind"]["win"] / sum(by["behind"].values()), 9),
                      "counts": {s: dict(sorted(c.items())) for s, c in by.items()}}
    preds = [
        {"id": "H1", "text": "ゲートが通る。(9, 9) の A − B は 0.30 以上", "ok": not problems and ab["9,9"] >= 0.30, "got": ab["9,9"]},
        {"id": "H2", "text": "(9, 8) の A − B は 0.30 以上", "ok": ab["9,8"] >= 0.30, "got": ab["9,8"]},
        {"id": "H3", "text": "(8, 9) の A − B は 0.20 以下", "ok": ab["8,9"] <= 0.20, "got": ab["8,9"]},
        {"id": "H4", "text": "読みは「勝ち負けの側」", "ok": reading == 1, "got": reading},
        {"id": "H5", "text": "A クラスは B クラスより、リードを守った割合も、同点から勝った割合も高い",
         "ok": rates["A"]["lead_held"] > rates["B"]["lead_held"] and rates["A"]["tie_won"] > rates["B"]["tie_won"],
         "got": {c: [rates[c]["lead_held"], rates[c]["tie_won"]] for c in rates}},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "games": t.height // 2, "cells": leans, "reading": reading,
            "states": rates, "predictions": preds}


def round_nine(full, more: dict, skip: list[int], pl, eighth: dict) -> dict:
    """第9弾: 第8弾の 4 通りを、最終順位を使わない群（得失点差でリーグ 3 位以内・前の年の A クラス）で分け直す。"""
    rows = full.select("season", "team", "upper_half", "rank_rd").to_dicts()
    final = {(r["season"], r["team"]): r["upper_half"] for r in rows}
    groups = {"final": final, "run_diff": {(r["season"], r["team"]): r["rank_rd"] <= 3 for r in rows},
              "previous": {(s, t): final[(s - 1, t)] for (s, t) in final if (s - 1, t) in final}}
    out = {}
    for name, upper in groups.items():
        r = round_eight(full, more, skip, pl, upper)
        out[name] = {"upper_units": sum(upper[k] for k in upper if k[0] not in skip and k[0] >= 2013),
                     "cells": r["cells"], "states": r["states"]}
    same = out["final"]["cells"] == eighth["cells"] and out["final"]["states"] == eighth["states"]
    problems = [] if same else ["最終順位で分けた値が第8弾と違う"]
    ab = {g: out[g]["cells"]["9,9"]["a_minus_b"] for g in ("run_diff", "previous")}
    reading = 1 if min(ab.values()) >= 0.30 else 3 if max(ab.values()) <= 0.15 else 2
    held = out["run_diff"]["states"]
    preds = [
        {"id": "I1", "text": "ゲートが通る", "ok": same, "got": same},
        {"id": "I2", "text": "得失点差で分けると、(9, 9) の上 − 下は 0.15 以下", "ok": ab["run_diff"] <= 0.15, "got": ab["run_diff"]},
        {"id": "I3", "text": "前の年で分けると、(9, 9) の上 − 下は 0.15 以下", "ok": ab["previous"] <= 0.15, "got": ab["previous"]},
        {"id": "I4", "text": "読みは「群の決め方」", "ok": reading == 3, "got": reading},
        {"id": "I5", "text": "リードを守った割合は、得失点差で分けても、上の群のほうが 1 ポイント以上高い",
         "ok": held["A"]["lead_held"] - held["B"]["lead_held"] >= 0.01, "got": [held["A"]["lead_held"], held["B"]["lead_held"]]},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "groups": out, "reading": reading, "predictions": preds}


def score_upto(gm: dict, inn: dict, n: int, eps: float = 0.0):
    """x = n + eps 回までの得点（ホーム, ビジター）。作れない試合は None。

    n = 1〜8: 1〜n 回の点 + eps × (n+1) 回の点（9 回裏が無ければ 0）。n 回に届かない試合は None。
    n = 9: 延長に入った試合だけ 9 回終了時の点 + eps × 延長の点。9 回以内に終わった試合は最終の得点。n = 10: 最終の得点。
    """
    h, a = inn["home"], inn["away"]
    if n >= 10:
        return gm["hs"], gm["as"]
    if n == 9:
        if len(a) <= 9:
            return gm["hs"], gm["as"]
        h9, a9 = sum(x for x in h[:9] if type(x) is int), sum(x for x in a[:9] if type(x) is int)
        return (h9 + eps * (gm["hs"] - h9), a9 + eps * (gm["as"] - a9)) if eps else (h9, a9)
    if len(h) < n or len(a) < n or not all(type(x) is int for x in (*h[:n], *a[:n])):
        return None
    nxt = lambda v: v[n] if len(v) > n and type(v[n]) is int else 0  # noqa: E731
    return (sum(h[:n]) + eps * nxt(h), sum(a[:n]) + eps * nxt(a)) if eps else (sum(h[:n]), sum(a[:n]))


def tie_weighted_gap(t, theta: float) -> dict:
    """つまみ 2: 最終の得点のまま、見込みの中の同点の組を重み theta で「半分は勝ち（1 点足す）・半分は負け」に数えた
    「勝ち試合の得点 − 見込み」。theta = 0 は sakanalytics.win_loss_split の wl_rf_win_gap と同じ。{(年, 球団): 差}。"""
    out = {}
    for (season, team), g in t.group_by(["season", "team"], maintain_order=True):
        rf, ra, home = g["rf"].to_list(), g["ra"].to_list(), g["is_home"].to_list()
        n_win = rf_win = 0.0
        for venue in (True, False):
            cx = Counter(x for x, h in zip(rf, home) if h == venue)
            cy = Counter(y for y, h in zip(ra, home) if h == venue)
            n = sum(cx.values())
            for x in cx:
                for y in cy:
                    w = cx[x] * cy[y] / n
                    if x > y:
                        n_win, rf_win = n_win + w, rf_win + w * x
                    elif x == y and theta:
                        n_win, rf_win = n_win + theta * w / 2, rf_win + theta * w / 2 * (x + 1)
        wins = [x for x, y in zip(rf, ra) if x > y]
        out[(season, team)] = sum(wins) / len(wins) - rf_win / n_win
    return out


def upto_gaps(games: list[dict], innings: dict, teams: dict, n: int, eps: float, pl) -> tuple[dict, int]:
    """x = n + eps 回までの得点（score_upto）で作り直した「勝ち試合の得点 − 見込み」。({(年, 球団): 差}, 使った試合の数)。"""
    import sakanalytics as SA
    rows = []
    for gm in games:
        sc = score_upto(gm, innings[gm["key"]], n, eps)
        if sc is None:
            continue
        for team, rf, ra, home in ((gm["home"], sc[0], sc[1], True), (gm["away"], sc[1], sc[0], False)):
            rows.append({"season": int(gm["date"][:4]), "team": team, "league": teams[team]["league"], "rf": rf, "ra": ra, "is_home": home})
    got = SA.win_loss_split(pl.DataFrame(rows, schema_overrides={"season": pl.Int32}))
    return {(r["season"], r["team"]): r["wl_rf_win_gap"] for r in got.to_dicts()}, len(rows) // 2


def next_year_rows(ps: list[dict], full, tables: tuple, focus, P, pl) -> tuple[list[tuple[dict, dict]], list]:
    """翌年の A/B クラス（upper_half_next）の列を足した表で命題を判定する（第10弾 B・第11弾 B）。
    戻り値は（[(まとめの行, evaluate の結果)], 列を足した表）。読み: 元の命題の fisher_p が ALPHA 未満なら 1、そうでなければ 2。"""
    nxt = {(r["season"] - 1, r["team"]): r["upper_half"] for r in full.select("season", "team", "upper_half").to_dicts()}
    add = pl.DataFrame([{"season": s, "team": t, "upper_half_next": v} for (s, t), v in nxt.items()]).cast({"season": full.schema["season"]})
    with_next = [t.join(add, on=["season", "team"], how="left") for t in tables]
    rows = []
    for p in ps:
        r = P.evaluate(p, *with_next, focus)
        o = r["forms"][0]
        rows.append(({"id": p["id"], "statement": p["statement"], "key": r["key"], "signature": r["signature"],
                      "definition_sha256": r["definition_sha256"], "parent": p.get("parent"), "units": r["units"],
                      "forms": {f["form"]: form_summary(f) for f in r["forms"]}, "fisher_p": o["fisher_p"],
                      "reading": 1 if o["fisher_p"] < ALPHA else 2, "judgement": {k: r["judgement"][k] for k in ("code", "stage", "form")}}, r))
    return rows, with_next


def round_ten(repo: Path, full, tables: tuple, focus, ns: list[dict], more: dict, third: dict, fourth: dict, skip: list[int],
              P, pl) -> dict:
    """第10弾。A: 境界を動かす（x 回まで・同点の重み θ・線をずらす）。B: 式1 を翌年・得失点差で問い直す。"""
    import random

    import epsilon as EPS
    games, innings, teams = games_with_innings(repo, full)
    rng = random.Random(20261113)
    drawn = [float(f"{rng.uniform(1, 10):.3f}e-{rng.randint(1, 6)}") for _ in range(5)]
    eps_all = sorted({EPS.check_eps(e) for e in (*drawn, 0.25, 0.5, 0.75)})
    assert all(0 < e < 1 for e in eps_all)

    def share(gaps: dict) -> dict:
        v = sorted(x for k, x in gaps.items() if k[0] not in skip and x is not None)
        return {"units": len(v), "negative": sum(x < 0 for x in v), "share_negative": round(sum(x < 0 for x in v) / len(v), 9),
                "median_gap": round((v[(len(v) - 1) // 2] + v[len(v) // 2]) / 2, 9)}

    def dial_one(n: int, eps: float = 0.0) -> dict:
        gaps, used = upto_gaps(games, innings, teams, n, eps, pl)
        return {"x": n + eps, "label": f"{n}+{eps:g}" if eps else str(n), "games": used, **share(gaps)}

    points = [(n, 0.0) for n in range(1, 9)] + [(8, e) for e in eps_all] + [(9, 0.0)] + [(9, e) for e in eps_all] + [(10, 0.0)]
    one = [dial_one(n, e) for n, e in points]
    two = [{"theta": th, **share(tie_weighted_gap(more["tables"]["full"], th))} for th in (0.0, *eps_all, 1.0)]
    by_x = {r["x"]: r["negative"] for r in one}
    want = (third["variants"]["eight"]["negative"], fourth["split"]["nine"]["negative"], third["variants"]["full"]["negative"])
    problems = [] if (by_x[8.0], by_x[9.0], by_x[10.0]) == want and two[0]["negative"] == want[2] else ["x = 8・9・10 か θ = 0 が、第3〜5弾の数と違う"]
    lines = {}
    for line in (0.60, 0.65, 0.70):              # 線をずらす: 負の割合が線を超える最初の x、線の内側に戻る最初の θ
        lines[str(line)] = {"first_x_above": next((r["label"] for r in one if r["share_negative"] > line), None),
                            "first_theta_within": next((r["theta"] for r in two if r["share_negative"] <= line), None)}

    # ---- B: 式1 を、翌年の B クラス・得失点差の順位で問い直す
    props = [row for row, _ in next_year_rows(ns, full, tables, focus, P, pl)[0]]
    q = {x["id"]: x for x in props}
    mid, late = [r for r in one if 8 < r["x"] < 9], [r for r in one if 9 < r["x"] < 10]
    th65 = lines["0.65"]["first_theta_within"]
    preds = [
        {"id": "J1", "text": "ゲートが通る", "ok": not problems, "got": [by_x[8.0], by_x[9.0], by_x[10.0], two[0]["negative"]]},
        {"id": "J2", "text": "N = 1〜7 は、どれも負の割合が 0.35〜0.65", "ok": all(0.35 <= r["share_negative"] <= 0.65 for r in one[:7]),
         "got": [r["share_negative"] for r in one[:7]]},
        {"id": "J3", "text": "8 + ε は、どの ε でも 0.65 以下", "ok": all(r["share_negative"] <= 0.65 for r in mid),
         "got": [r["share_negative"] for r in mid]},
        {"id": "J4", "text": "9 + ε は、どの ε > 0 でも 0.80 以上", "ok": all(r["share_negative"] >= 0.80 for r in late),
         "got": [r["share_negative"] for r in late]},
        {"id": "J5", "text": "θ = 1 で 0.35〜0.65 に入り、0.65 を下回るのは θ が 0.3〜0.8 のどこか",
         "ok": 0.35 <= two[-1]["share_negative"] <= 0.65 and th65 is not None and 0.3 <= th65 <= 0.8,
         "got": {"theta_1": two[-1]["share_negative"], "first_theta_within_0.65": th65}},
        {"id": "K1", "text": "N52A（配分が不利 ⇒ 翌年 B）: fisher_p は 0.05 以上", "ok": q["N52A"]["reading"] == 2, "got": q["N52A"]["fisher_p"]},
        {"id": "K2", "text": "N52S（作り直しで A の確率 4 割未満 ⇒ 翌年 B）: fisher_p は 0.05 未満", "ok": q["N52S"]["reading"] == 1,
         "got": q["N52S"]["fisher_p"]},
        {"id": "K3", "text": "R52A（配分が不利 ⇒ 得失点差で B）: fisher_p は 0.05 以上", "ok": q["R52A"]["reading"] == 2, "got": q["R52A"]["fisher_p"]},
        {"id": "K4", "text": "N0（B クラス ⇒ 翌年も B）: 成立率は 0.60〜0.75", "ok": 0.60 <= q["N0"]["forms"]["original"]["rate"] <= 0.75,
         "got": q["N0"]["forms"]["original"]["rate"]},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "eps": {"seed": 20261113, "drawn": drawn, "all": eps_all},
            "dial_innings": one, "dial_ties": two, "lines": lines, "propositions": props, "predictions": preds}


SHAPES = (("T85", "E85"), ("KT85", "KE85"), ("DT85", "DE85"))   # 第11弾 A: 同じ形の命題の組（θ = 1 の列, 8 回までの列）


def round_eleven(repo: Path, full, tables: tuple, focus, es: list[dict], ts: list[dict], ms: list[dict], more: dict, third: dict,
                 fourth: dict, tenth: dict, evaluated: dict, skip: list[int], P, pl) -> dict:
    """第11弾。A: 列を直す形（θ = 1 と 8 回まで）を同じ命題で並べ、先に決めた線で決める。B: 配分が不利 ⇒ 翌年 A クラス。"""
    games, innings, teams = games_with_innings(repo, full)
    small, eps_all = sorted(tenth["eps"]["drawn"]), tenth["eps"]["all"]
    cands = {"t1": ("wl_rf_win_gap_t1", ts, lambda e: tie_weighted_gap(more["tables"]["full"], 1.0 - e)),
             "eight": ("wl_rf_win_gap8", es, lambda e: upto_gaps(games, innings, teams, 8, e, pl)[0])}
    orig = {k: r["wl_rf_win_gap"] for k, r in more["units"]["full"].items()}
    keys = sorted(k for k in orig if k[0] not in skip)

    def judged(name: str, gaps: dict) -> dict[str, dict]:
        col, ps, _ = cands[name]
        add = pl.DataFrame([{"season": k[0], "team": k[1], col: v} for k, v in sorted(gaps.items())],
                           schema_overrides={"season": pl.Int32, col: pl.Float64}).cast({"season": full.schema["season"]})
        ev = dict(evaluated)
        for p in ps:
            ev[p["id"]] = P.evaluate(p, *(t.join(add, on=["season", "team"], how="left") for t in tables), focus)
        return summarize_props(ps, ev)

    def codes(rows: dict[str, dict]) -> dict:
        return {i: {"forms": {f: v["code"] for f, v in q["forms"].items()}, "judgement": q["judgement"]["code"], "reading": q.get("reading")}
                for i, q in rows.items()}

    def spearman(a: dict, b: dict) -> float:
        return round(pl.DataFrame({"a": [a[k] for k in keys], "b": [b[k] for k in keys]}).select(pl.corr("a", "b", method="spearman")).item(), 6)

    base, rows, cand = {}, {}, {}
    for name, (col, ps, moved) in cands.items():
        base[name] = moved(0.0)
        rows[name] = judged(name, base[name])
        was = codes(rows[name])
        shakes = []
        for e in eps_all:                         # 境界をわざとずらす: θ = 1 − ε、x = 8 + ε
            g = moved(e)
            got = codes(judged(name, g))
            shakes.append({"eps": e, "small": e in small, "negative": sum(g[k] < 0 for k in keys),
                           "sign_flips": sum((g[k] < 0) != (base[name][k] < 0) for k in keys),
                           "changed_forms": sorted(f"{i}:{f}" for i, q in got.items() for f, c in q["forms"].items() if c != was[i]["forms"][f]),
                           "changed_readings": sorted(i for i, q in got.items()
                                                      if (q["judgement"], q["reading"]) != (was[i]["judgement"], was[i]["reading"]))})
        neg = sum(base[name][k] < 0 for k in keys)
        c = {"column": col, "units": len(keys), "negative": neg, "share_negative": round(neg / len(keys), 9),
             "rho_original": spearman(base[name], orig), "shakes": shakes}
        c |= {"unbiased": 0.35 <= c["share_negative"] <= 0.65, "stable": not any(x["changed_forms"] for x in shakes if x["small"]),
              "keeps_order": c["rho_original"] >= 0.80}
        cand[name] = c | {"usable": c["unbiased"] and c["stable"] and c["keeps_order"]}
    agree = round(sum((base["t1"][k] < 0) == (base["eight"][k] < 0) for k in keys) / len(keys), 9)
    between = {"sign_agreement": agree, "rho": spearman(base["t1"], base["eight"])}
    between["same_thing"] = agree >= 0.75 and between["rho"] >= 0.80
    was = {n: codes(rows[n]) for n in rows}
    shapes = [{"t1": a, "eight": b, "judgement": [was["t1"][a]["judgement"], was["eight"][b]["judgement"]],
               "reading": [was["t1"][a]["reading"], was["eight"][b]["reading"]],
               "same": (was["t1"][a]["judgement"], was["t1"][a]["reading"]) == (was["eight"][b]["judgement"], was["eight"][b]["reading"])}
              for a, b in SHAPES]
    usable = [n for n in cand if cand[n]["usable"]]
    if len(usable) == 2:                          # 決め方 2・3
        decision = {"rule": 2, "choice": "t1"} if all(x["same"] for x in shapes) else {"rule": 3, "choice": None}
    else:                                         # 決め方 4
        decision = {"rule": 4, "choice": usable[0] if usable else None}
    saved = {q["id"]: {f: (v["n"], v["hold"], v["code"]) for f, v in q["forms"].items()} for q in fourth["propositions"]}
    again = {i: {f: (v["n"], v["hold"], v["code"]) for f, v in q["forms"].items()} for i, q in rows["eight"].items()}
    gap8 = {(r["season"], r["team"]): r["wl_rf_win_gap8"] for r in more["gap8"]}
    problems = []
    if cand["t1"]["negative"] != tenth["dial_ties"][-1]["negative"] or cand["eight"]["negative"] != third["variants"]["eight"]["negative"]:
        problems.append("第11弾: θ = 1 か 8 回までの負の数が、第10弾・第3弾と違う")
    if max(abs(base["eight"][k] - gap8[k]) for k in keys) > 1e-9 or again != saved:
        problems.append("第11弾: 8 回までの列か、その 3 命題が、第4弾と違う")

    # ---- B: 配分が不利 ⇒ 翌年 A クラス
    got, with_next = next_year_rows(ms, full, tables, focus, P, pl)
    props = [row | {"reading": 5 if row["forms"]["original"]["n"] < r["min_n"] else row["reading"]} for row, r in got]
    q = {x["id"]: x for x in props}
    cond = with_next[0].filter((pl.col("alloc_z_strat") < -1) & pl.col("upper_half_next").is_not_null()
                               & pl.col("season").is_between(2012, 2024))
    mine = [{"unit": f"{r['team']}-{r['season']}", "upper_half": r["upper_half"], "upper_half_next": r["upper_half_next"]}
            for r in cond.filter(pl.col("team") == focus).sort("season").select("season", "team", "upper_half", "upper_half_next").to_dicts()]
    t85, m = rows["t1"]["T85"]["forms"]["original"], {i: q[i]["forms"] for i in q}
    sm = {n: [x for x in cand[n]["shakes"] if x["small"]] for n in cand}
    preds = [
        {"id": "Q1", "text": "ゲート: θ = 1 の列の負の数は 76、8 回までは 71", "ok": not problems and (cand["t1"]["negative"], cand["eight"]["negative"]) == (76, 71),
         "got": [cand["t1"]["negative"], cand["eight"]["negative"]]},
        {"id": "Q2", "text": "θ = 1 の列は元の列との順位相関が 0.80 以上で、8 回までの列より高い",
         "ok": cand["t1"]["rho_original"] >= 0.80 and cand["t1"]["rho_original"] > cand["eight"]["rho_original"],
         "got": {n: cand[n]["rho_original"] for n in cand}},
        {"id": "Q3", "text": "2 つの候補で符号が同じ球団年の割合は 0.65〜0.85", "ok": 0.65 <= agree <= 0.85, "got": agree},
        {"id": "Q4", "text": "T85: 中日の 12 単位のうち負は 4〜8。終了コードは 0・1 にならない",
         "ok": t85["n"] == 12 and 4 <= t85["hold"] <= 8 and t85["code"] not in (0, 1), "got": {k: t85[k] for k in ("hold", "n", "code")}},
        {"id": "Q5", "text": "DT85 の fisher_p は 0.05 以上。KT85 の読みは 1 にならない",
         "ok": rows["t1"]["DT85"]["fisher_p"] >= ALPHA and rows["t1"]["KT85"]["reading"] != 1,
         "got": {"DT85": rows["t1"]["DT85"]["fisher_p"], "KT85": rows["t1"]["KT85"]["reading"]}},
        {"id": "Q6", "text": "揺らし: θ = 1 − ε は 5 つとも終了コードが変わらない。8 + ε は、どれかで変わる",
         "ok": cand["t1"]["stable"] and not cand["eight"]["stable"],
         "got": {n: [x["changed_forms"] for x in sm[n]] for n in cand}},
        {"id": "L1", "text": "M52A: 元 27 中 18・対偶 72 中 63・逆 72 中 18・裏 117 中 63。fisher_p は 0.10 未満",
         "ok": [(m["M52A"][f]["hold"], m["M52A"][f]["n"]) for f in FORM_ORDER] == [(18, 27), (63, 72), (18, 72), (63, 117)] and q["M52A"]["fisher_p"] < 0.10,
         "got": {"forms": [[m["M52A"][f]["hold"], m["M52A"][f]["n"]] for f in FORM_ORDER], "fisher_p": q["M52A"]["fisher_p"]}},
        {"id": "L2", "text": "M52B: 条件に当たる単位は 15 以上で、成立率は 0.50 以上。fisher_p は 0.05 未満",
         "ok": m["M52B"]["original"]["n"] >= 15 and m["M52B"]["original"]["rate"] >= 0.50 and q["M52B"]["fisher_p"] < ALPHA,
         "got": {"hold": m["M52B"]["original"]["hold"], "n": m["M52B"]["original"]["n"], "fisher_p": q["M52B"]["fisher_p"]}},
        {"id": "L3", "text": "M52U: 条件に当たる単位は 10 未満（保留）", "ok": m["M52U"]["original"]["n"] < 10,
         "got": {"hold": m["M52U"]["original"]["hold"], "n": m["M52U"]["original"]["n"]}},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "eps": {"small": small, "all": eps_all}, "candidates": cand,
            "between": between, "column_propositions": {n: list(rows[n].values()) for n in rows}, "shapes": shapes, "decision": decision,
            "propositions": props, "chunichi_condition_units": mine, "predictions": preds}


def round_twelve(full, tables: tuple, focus, ws: list[dict], eleventh: dict, P, pl) -> dict:
    """第12弾: B クラスの中で翌年 A に戻るのは、配分の巡り合わせか、分布がもともと良かったからか。4 つのマスに分けて問う。"""
    got, with_next = next_year_rows(ws, full, tables, focus, P, pl)
    props = [row | {"reading": 5 if row["forms"]["original"]["n"] < r["min_n"] else row["reading"]} for row, r in got]
    q = {x["id"]: x for x in props}
    line = next(c["value"] for c in ws[0]["scope"]["where"] if c["col"] == "sim_p_upper")       # 宣言の線（0.32）は命題から読む
    b = with_next[0].filter(~pl.col("upper_half") & pl.col("upper_half_next").is_not_null() & pl.col("season").is_between(2012, 2024))
    cells = {}
    for at in (0.30, line, 0.35):                # 線を前後にずらして同じ表を数える（読むのは line だけ）
        t = b.group_by((pl.col("alloc_z_strat") < -1).alias("unfav"), (pl.col("sim_p_upper") >= at).alias("high")).agg(
            n=pl.len(), next_upper=pl.col("upper_half_next").sum())
        got_cells = {(r["unfav"], r["high"]): r for r in t.to_dicts()}
        cells[format(at, ".2f")] = [{"unfav": u, "high": h, "n": got_cells[(u, h)]["n"], "next_upper": got_cells[(u, h)]["next_upper"],
                                    "rate": round(got_cells[(u, h)]["next_upper"] / got_cells[(u, h)]["n"], 9)}
                                   for u in (False, True) for h in (False, True)]
    main = cells[format(line, ".2f")]
    m52b = {x["id"]: x for x in eleventh["propositions"]}["M52B"]["forms"]
    side = lambda u: (sum(c["next_upper"] for c in main if c["unfav"] == u), sum(c["n"] for c in main if c["unfav"] == u))  # noqa: E731
    problems = []
    if [c["n"] for c in main] != [38, 10, 12, 12]:
        problems.append("第12弾: マスの単位の数が、宣言の前に数えた 38・10・12・12 と違う")
    if side(True) != (m52b["original"]["hold"], m52b["original"]["n"]) or side(False)[1] != m52b["inverse"]["n"]:
        problems.append("第12弾: マスを足した数が、第11弾の M52B と違う")
    hit = lambda i: q[i]["reading"] == 1         # noqa: E731  fisher_p が ALPHA 未満（単位が足りない命題は数えない）
    alloc, dist = hit("G52H") or hit("G52L"), hit("G52U") or hit("G52N")
    reading_ = 2 if alloc and dist else 1 if alloc else 3 if dist else 4
    rate = {(c["unfav"], c["high"]): c["rate"] for c in main}
    preds = [
        {"id": "R1", "text": "翌年 A の割合は、「不利・高い」が最も高く、「不利でない・低い」が最も低い",
         "ok": rate[(True, True)] == max(rate.values()) and rate[(False, False)] == min(rate.values()), "got": [c["rate"] for c in main]},
        {"id": "R2", "text": "G52N の fisher_p は 0.05 未満", "ok": q["G52N"]["fisher_p"] < ALPHA, "got": q["G52N"]["fisher_p"]},
        {"id": "R3", "text": "G52L の fisher_p は 0.05 以上", "ok": q["G52L"]["fisher_p"] >= ALPHA, "got": q["G52L"]["fisher_p"]},
        {"id": "R4", "text": "読みは 3（分布がもともと良かった）", "ok": reading_ == 3, "got": reading_},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "line": line, "cells": cells, "propositions": props,
            "sides": {"allocation": alloc, "distribution": dist}, "reading": reading_, "predictions": preds}


WL_GAPS = ("wl_rf_win_gap", "wl_rf_loss_gap", "wl_wpct_low_gap", "wl_wpct_high_gap")


def tie_split(t, win: float, loss: float, extra: float = 0.0) -> dict:
    """sakanalytics.win_loss_split の 4 つの差を、見込みの中の同点の組（x 対 x、重み w）の置き方を替えて作る（第13弾）。
    勝ちに win × w / 2（x+1+extra 対 x+extra）、負けに loss × w / 2（x+extra 対 x+1+extra）。win = loss = 0 は道具と同じ。{(年, 球団): 行}。"""
    import sakanalytics as SA
    totals: dict[tuple, list] = {}
    for season, league, rf, ra in t.select("season", "league", "rf", "ra").iter_rows():
        totals.setdefault((season, league), []).append(rf + ra)
    cut = {k: statistics.median(v) for k, v in totals.items()}                # 同じ年・同じリーグの試合の合計得点の中央値（道具と同じ）
    keys = (("rf_win", "rf_win", "n_win"), ("rf_loss", "rf_loss", "n_loss"), ("wpct_low", "w_low", "d_low"), ("wpct_high", "w_high", "d_high"))
    out = {}
    for (season, team), g in t.group_by(["season", "team"], maintain_order=True):
        m = cut[(season, g["league"][0])]
        rf, ra, home = g["rf"].to_list(), g["ra"].to_list(), g["is_home"].to_list()
        pairs = []
        for venue in (True, False):
            cx = Counter(x for x, h in zip(rf, home) if h == venue)
            cy = Counter(y for y, h in zip(ra, home) if h == venue)
            n = sum(cx.values())
            for x in cx:
                for y in cy:
                    w = cx[x] * cy[y] / n
                    pairs += [(x, y, w)] if x != y else [(x + 1 + extra, y + extra, win * w / 2), (x + extra, y + 1 + extra, loss * w / 2)]
        act, exp = SA._wl_sums([(x, y, 1.0) for x, y in zip(rf, ra)], m), SA._wl_sums(pairs, m)
        out[(season, team)] = {f"wl_{name}_gap": act[num] / act[den] - exp[num] / exp[den] for name, num, den in keys}
    return out


def round_thirteen(more: dict, tenth: dict, eleventh: dict, skip: list[int], pl) -> dict:
    """第13弾: 見込みの同点を決めるときの、負け試合の側の置き方。つまみ 1（λ）とつまみ 2（θ負）で、4 つの列が線の内側に入るか。"""
    t, orig = more["tables"]["full"], more["units"]["full"]
    keys = sorted(k for k in orig if k[0] not in skip)
    values = [0.0, *tenth["eps"]["all"], 1.0]

    def shares(g: dict) -> dict:
        r = {"win_negative": sum(g[k]["wl_rf_win_gap"] < 0 for k in keys), **{f"{c[3:-4]}_positive": sum(g[k][c] > 0 for k in keys) for c in WL_GAPS[1:]}}
        inside = {k: 0.35 <= v / len(keys) <= 0.65 for k, v in r.items()}
        return r | {"inside": inside, "passes": all(inside.values())}

    base = tie_split(t, 0.0, 0.0)
    now = tie_split(t, 1.0, 1.0)
    one = [{"lambda": v, **shares(tie_split(t, 1.0, 1.0, v))} for v in values]
    two_g = {v: tie_split(t, 1.0, v) for v in values}
    two = [{"theta_loss": v, **shares(two_g[v])} for v in values]
    problems = []
    if max(abs(base[k][c] - orig[k][c]) for k in keys for c in WL_GAPS) > 1e-9:
        problems.append("第13弾: 重み 0・0 が、道具の 4 つの列と違う")
    if (one[0]["win_negative"], one[0]["rf_loss_positive"]) != (eleventh["candidates"]["t1"]["negative"], 49) or one[0] != {"lambda": 0.0, **shares(now)}:
        problems.append("第13弾: いまの置き方（重み 1・1、λ 0）の数が、第11弾の 76・SakAnalytics #44 の 49 と違う")
    ok1 = [r["lambda"] for r in one if r["lambda"] > 0 and r["passes"]]
    ok2 = [r["theta_loss"] for r in two if r["passes"]]
    if ok1:                                      # 決め方 1〜3
        decision, chosen = {"rule": 1, "dial": "lambda", "value": min(ok1)}, tie_split(t, 1.0, 1.0, min(ok1))
    elif ok2:
        decision = {"rule": 2, "dial": "theta_loss", "value": 0.0 if 0.0 in ok2 else None}
        chosen = two_g[0.0] if 0.0 in ok2 else None
    else:
        decision, chosen = {"rule": 3, "dial": None, "value": None}, None
    rho = None
    if chosen:                                   # 決め方 4: 勧める形の負け試合の列が、元の並びを保つか
        rho = round(pl.DataFrame({"a": [chosen[k]["wl_rf_loss_gap"] for k in keys], "b": [orig[k]["wl_rf_loss_gap"] for k in keys]})
                    .select(pl.corr("a", "b", method="spearman")).item(), 6)
    lam_loss = [r["rf_loss_positive"] for r in one]
    preds = [
        {"id": "S1", "text": "ゲートが通る", "ok": not problems, "got": problems},
        {"id": "S2", "text": "つまみ 1: λ を上げると負け試合の正の数は 49 より減る。通る λ は無い",
         "ok": not ok1 and all(v <= 49 for v in lam_loss) and lam_loss[-1] < 49, "got": lam_loss},
        {"id": "S3", "text": "つまみ 2: θ負 が 0.75 以下なら通り、線の外に出るのは 1 だけ", "ok": ok2 == values[:-1], "got": ok2},
        {"id": "S4", "text": "勝率の 2 つの列は、どのつまみのどの値でも線の内側",
         "ok": all(r["inside"]["wpct_low_positive"] and r["inside"]["wpct_high_positive"] for r in (*one, *two)),
         "got": [[r["wpct_low_positive"], r["wpct_high_positive"]] for r in (*one, *two)]},
        {"id": "S5", "text": "決め方 2 で θ負 = 0 を勧めることになる", "ok": decision == {"rule": 2, "dial": "theta_loss", "value": 0.0}, "got": decision},
    ]
    return {"gate": {"ok": not problems, "problems": problems}, "units": len(keys), "values": values, "dial_lambda": one, "dial_theta_loss": two,
            "passing": {"lambda": ok1, "theta_loss": ok2}, "decision": decision, "rho_loss_original": rho, "predictions": preds}


def analyze(repo: Path = ROOT, season: Path | None = None, config: Path | None = None, props: Path | None = None,
            extra: Path | None = None, stored: Path | None = None, branch: Path | None = None,
            second: Path | None = None, panel: Path | None = None, fourth: Path | None = None,
            central: Path | None = None, sixth: Path | None = None, tenth: Path | None = None,
            eleventh: Path | None = None, twelfth: Path | None = None) -> dict:
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
    sixth = sixth or HERE / "kind_reask_results" / "kind_reask_r6_propositions.toml"
    tenth = tenth or HERE / "kind_reask_results" / "kind_reask_r10_propositions.toml"
    eleventh = eleventh or HERE / "kind_reask_results" / "kind_reask_r11_propositions.toml"
    twelfth = twelfth or HERE / "kind_reask_results" / "kind_reask_r12_propositions.toml"
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
                      "central": rel(central, repo), "central_sha256": hashlib.sha256(central.read_bytes()).hexdigest(),
                      "sixth_propositions": rel(sixth, repo),
                      "sixth_propositions_sha256": hashlib.sha256(sixth.read_bytes()).hexdigest(),
                      "tenth_propositions": rel(tenth, repo),
                      "tenth_propositions_sha256": hashlib.sha256(tenth.read_bytes()).hexdigest(),
                      "eleventh_propositions": rel(eleventh, repo),
                      "eleventh_propositions_sha256": hashlib.sha256(eleventh.read_bytes()).hexdigest(),
                      "twelfth_propositions": rel(twelfth, repo),
                      "twelfth_propositions_sha256": hashlib.sha256(twelfth.read_bytes()).hexdigest()},
           "gate": {"ok": True, "problems": []}, "propositions": [], "predictions": [], "summary": {}, "second": {}, "third": {},
           "fourth": {}, "fifth": {}, "sixth": {}, "seventh": {}, "eighth": {}, "ninth": {}, "tenth": {}, "eleventh": {}, "twelfth": {}, "thirteenth": {}}
    problems = out["gate"]["problems"]
    stored_sha = {r["meta"]["sha256"] for r in stored_rows.values()}
    if sha not in stored_sha:
        problems.append(f"命題ファイルの sha256 {sha} が保存された値 {sorted(stored_sha)} にない")
    try:
        ks, ds, fs, gs, ns, vs, ws = load_joined(props, [extra, second, fourth, sixth, tenth, eleventh, twelfth], P)
    except P.PropositionError as e:
        problems.append(f"つなげた命題ファイルが読み込めない: {e}")
        ks, ds, fs, gs, ns, vs, ws = [], [], [], [], [], [], []
    branch_sig = {P.identity(p)["signature"]: p["id"] for p in P.load(branch)[0]} if branch.exists() else {}
    for p in [*ks, *ds, *fs, *gs, *ns, *vs, *ws]:
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
    out["fifth"] = round_five([*P.load(props)[0], *ks, *ds], stored_rows, (included, excluded), focus, more["units"],
                              [int(e["season"]) for e in exclusions], P, pl)
    out["sixth"] = round_six(repo, config, full, (included, excluded), focus, fs, gs, evaluated, out["fourth"], more,
                             [*P.load(props)[0], *ks, *ds], stored_rows, [int(e["season"]) for e in exclusions], panel, P, pl)
    out["seventh"] = round_seven(repo, full, more, [int(e["season"]) for e in exclusions], pl)
    out["eighth"] = round_eight(full, more, [int(e["season"]) for e in exclusions], pl)
    out["ninth"] = round_nine(full, more, [int(e["season"]) for e in exclusions], pl, out["eighth"])
    out["tenth"] = round_ten(repo, full, (included, excluded), focus, ns, more, out["third"], out["fourth"],
                             [int(e["season"]) for e in exclusions], P, pl)
    ts = [p for p in vs if p["then"][0]["col"] == "wl_rf_win_gap_t1"]       # 第11弾 A の命題（θ = 1 の列）。残りが B
    out["eleventh"] = round_eleven(repo, full, (included, excluded), focus, fs, ts, [p for p in vs if p not in ts], more,
                                   out["third"], out["fourth"], out["tenth"], evaluated, [int(e["season"]) for e in exclusions], P, pl)
    out["twelfth"] = round_twelve(full, (included, excluded), focus, ws, out["eleventh"], P, pl)
    out["thirteenth"] = round_thirteen(more, out["tenth"], out["eleventh"], [int(e["season"]) for e in exclusions], pl)
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

    f5 = res["fifth"]
    col_ja = {"wl_rf_win_gap": "勝ち試合の得点", "wl_rf_loss_gap": "負け試合の得点", "wl_wpct_low_gap": "点の少ない試合の勝率",
              "wl_wpct_high_gap": "点の多い試合の勝率"}
    L += ["", "# 第5弾 1: 「実際 − 見込み」の 4 つの列の片寄り", "",
          "各セルは「正の単位 / 単位（割合）・中央値」。割合が 35〜65 % の外なら片寄り（★）。", "",
          "| 列 | そのまま | 9 回まで | 8 回まで |", "|---|---|---|---|"]
    for col, by_table in f5["bias"].items():
        cell = lambda v: f"{v['positive']}/{v['units']}（{v['share_positive']:.2f}）・{v['median']:+.3f}{' ★' if v['one_sided'] else ''}"  # noqa: E731
        L += [f"| {col_ja[col]} `{col}` | " + " | ".join(cell(by_table[k]) for k in ("full", "nine", "eight")) + " |"]
    L += ["", "# 第5弾 2: 列の値だけを替えたときの判定", "",
          f"ゲート（(a) が保存された判定と同じか）: {'通った' if f5['gate']['ok'] else '通らなかった'}。",
          "各セルは元の命題の「終了コード・hold/n（判定できない単位）」と、［総合の終了コード］。"
          "(a) そのまま、(b) 2012年を空にする、(c) 9 回までの値、(d) 8 回までの値。", "",
          "| 命題 | (a) | (b) | (c) | (d) | (c) で変わる形 | (d) で変わる形 |", "|---|---|---|---|---|---|---|"]
    for r in f5["propositions"]:
        cell = lambda t: (lambda o, j: f"{o['code']}・{o['hold']}/{o['n']}（{o['undetermined']}）［{j}］")(  # noqa: E731
            r["treatments"][t]["forms"]["original"], r["treatments"][t]["judgement"])
        names = lambda fs_: "、".join(FORM_JA[f] for f in fs_) or "なし"  # noqa: E731
        L += [f"| {r['id']} {r['statement']} | " + " | ".join(cell(t) for t in "abcd")
              + f" | {names(r['changed_forms_c'])} | {names(r['changed_forms_d'])} |"]
    s5 = f5["summary"]
    L += ["", f"判定が変わる命題: (c) 9 回までで {len(s5['changed_c'])}/{len(s5['propositions'])} 件（{'、'.join(s5['changed_c']) or 'なし'}）、"
          f"(d) 8 回までで {len(s5['changed_d'])}/{len(s5['propositions'])} 件（{'、'.join(s5['changed_d']) or 'なし'}）。", "",
          f"## 第5弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f5['predictions'])}/{len(f5['predictions'])}", ""]
    for x in f5["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f6 = res["sixth"]
    e8 = f6["eighth"]
    L += ["", "# 第6弾 A: 試合の表（games_table_from_observed --with-eighth）から作った 8 回までの列で P85・P86 を問い直す", "",
          f"ゲート: {'通った' if f6['gate']['ok'] else '通らなかった'}。作った wl_rf_win_gap8 と第4弾の値の差の最大 {e8['max_abs_diff_vs_round_four']:.1e}"
          f"（{e8['units']} 単位）。足した列: {'、'.join(e8['columns'])}。", ""]
    for q in f6["propositions"]:
        L += [f"- **{q['id']}** {q['statement']}（親 {q['parent']}。総合の終了コード {q['judgement']['code']}）: "
              + "、".join(f"{FORM_JA[k]} {_cell(v)}" for k, v in q["forms"].items())
              + (f"。中日以外 {q['held_out']['hold']}/{q['held_out']['n']}（{q['held_out']['rate']:.2f}）、読み **{q['reading']}** {READING_JA[q['reading']]}"
                 if "held_out" in q else "")
              + (f"。中日 {q['chunichi']['hold']}/{q['chunichi']['n']}、中日以外の同じ種類 {q['others']['hold']}/{q['others']['n']}、fisher_p {q['fisher_p']:.3f}"
                 if "chunichi" in q else "")]
    L += ["", f"2026年（記録のみ。{e8['units_2026']} 単位の 8 回までの列を、2026年の 858 試合から同じ手順で作った）:", "",
          "| 命題 | 成立 | 判例 | 逆の判例 | どちらも当たらない | 判定不能 |", "|---|---|---|---|---|---|"]
    for r in f6["confirm_2026"]["rows"]:
        n, u = r["counts"], r["units"]
        nm = lambda k: f"{n[k]}{'（' + '・'.join(u[k]) + '）' if u[k] else ''}"  # noqa: E731
        L += [f"| {r['id']} | {nm('hold')} | {nm('counter')} | {nm('converse_counter')} | {n['neither']} | {n['undetermined']} |"]
    pb = f6["paired"]
    qty = {"alloc_net": "配分の効果（全試合）", "alloc_net_strat": "配分の効果（ホーム・ビジター別の合計）",
           "alloc_net_opp": "配分の効果（相手別）", "wpct_minus_sim": "実際の勝率 − 作り直しの勝率"}
    L += ["", "# 第6弾 B: 配分の効果と作り直しの列に、延長による寄りがあるか", "",
          "各セルは「正の単位の割合（A クラス・B クラス）」と、A − B。全体が 35〜65 % の外なら片寄り（★）、A − B が 0.30 以上なら強さに沿った寄り（▲）。", "",
          "| 量 | そのまま | 9 回まで | 8 回まで |", "|---|---|---|---|"]
    for col, by_table in pb["bias"].items():
        cell = lambda v: (f"{v['share_positive']:.2f}（A {v['share_positive_a']:.2f}・B {v['share_positive_b']:.2f}）・A − B {v['a_minus_b']:+.2f}"  # noqa: E731
                          f"{' ★' if v['one_sided'] else ''}{' ▲' if v['strength_sided'] else ''}")
        L += [f"| {qty[col]} | " + " | ".join(cell(by_table[k]) for k in ("full", "nine", "eight")) + " |"]
    L += ["", "列の値だけを替えたときの判定（各セルは元の命題の「終了コード・hold/n」と［総合の終了コード］）:", "",
          "| 命題 | (a) | (b) | (c) 9 回まで | (d) 8 回まで | (c) で変わる形 | (d) で変わる形 |", "|---|---|---|---|---|---|---|"]
    for r in pb["propositions"]:
        cell = lambda t: (lambda o, j: f"{o['code']}・{o['hold']}/{o['n']}［{j}］")(  # noqa: E731
            r["treatments"][t]["forms"]["original"], r["treatments"][t]["judgement"])
        names = lambda fs_: "、".join(FORM_JA[f] for f in fs_) or "なし"  # noqa: E731
        L += [f"| {r['id']} {r['statement']} | " + " | ".join(cell(t) for t in "abcd")
              + f" | {names(r['changed_forms_c'])} | {names(r['changed_forms_d'])} |"]
    L += ["", f"判定が変わる命題: (c) {len(pb['changed_c'])}/{len(pb['propositions'])} 件（{'、'.join(pb['changed_c']) or 'なし'}）、"
          f"(d) {len(pb['changed_d'])}/{len(pb['propositions'])} 件（{'、'.join(pb['changed_d']) or 'なし'}）。", "",
          f"## 第6弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f6['predictions'])}/{len(f6['predictions'])}", ""]
    for x in f6["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f7 = res["seventh"]
    names7 = {"alloc_net_home": "ホームの試合", "alloc_net_away": "ビジターの試合", "alloc_net_strat": "合計（ホーム + ビジター）"}
    cell7 = lambda v: (f"{v['share_positive']:.2f}（A {v['share_positive_a']:.2f}・B {v['share_positive_b']:.2f}）・A − B {v['a_minus_b']:+.2f}"  # noqa: E731
                       f"{' ★' if v['one_sided'] else ''}{' ▲' if v['strength_sided'] else ''}")
    L += ["", "# 第7弾: 配分の効果の強さに沿った寄りを分ける", "",
          f"ゲート（補わない見込みが保存された値と同じ）: {'通った' if f7['gate']['ok'] else '通らなかった'}。"
          f"9 回裏が無かった {f7['imputed_games']} 試合（{f7['games']} 試合中）に、同じリーグ・同じ年の 9 回表の得点の分布を補った。", "",
          "各セルは「正の単位の割合（A クラス・B クラス）」と A − B。★ は全体の片寄り、▲ は強さに沿った寄り。", "",
          "| 配分の効果 | そのまま | 9 回まで | 8 回まで | 9 回裏を補う |", "|---|---|---|---|---|"]
    for c, name in names7.items():
        L += [f"| {name} `{c}` | " + " | ".join(cell7(f7["home_away"][c][k]) for k in ("full", "nine", "eight")) + f" | {cell7(f7['imputed'][c])} |"]
    L += ["", f"読み（判定ではない）: **{f7['reading']}** "
          + {1: "主に道具の側（9 回裏が無いことによる打ち切り）", 2: "両方", 3: "9 回裏が無いことでは説明できない（チームの側か、サヨナラ）"}[f7["reading"]], "",
          f"## 第7弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f7['predictions'])}/{len(f7['predictions'])}", ""]
    for x in f7["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f8 = res["eighth"]
    L += ["", "# 第8弾: 配分の効果に残った寄りを、勝ち負けの側と得点の分布の側に分ける", "",
          f"ゲート（(8, 8) が第6弾の 8 回までの値と同じ）: {'通った' if f8['gate']['ok'] else '通らなかった'}。8 回に届いた {f8['games']} 試合。", "",
          "各セルは alloc_net_strat の「正の単位の割合（A クラス・B クラス）」と A − B。", "",
          "| | 見込みを 8 回までの得点で | 見込みを 9 回までの得点で |", "|---|---|---|",
          f"| 勝ち越しを 8 回終了時で | {cell7(f8['cells']['8,8'])} | {cell7(f8['cells']['8,9'])} |",
          f"| 勝ち越しを 9 回終了時で | {cell7(f8['cells']['9,8'])} | {cell7(f8['cells']['9,9'])} |", "",
          f"読み（判定ではない）: **{f8['reading']}** " + {1: "勝ち負けの側", 2: "両方", 3: "得点の分布の側"}[f8["reading"]], "",
          "8 回終了時の状態ごとの、9 回終了時の結果:", "",
          "| クラス | リードの試合 | 守った割合 | 同点の試合（9 回で決まった数） | 決まった中で勝った割合 | ビハインドの試合 | 勝った割合 |", "|---|---|---|---|---|---|---|"]
    for cls, v in f8["states"].items():
        L += [f"| {cls} | {v['lead_games']} | {v['lead_held']:.3f} | {v['tie_games']}（{v['tie_decided']}） | {v['tie_won']:.3f} "
              f"| {v['behind_games']} | {v['behind_won']:.3f} |"]
    L += ["", f"## 第8弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f8['predictions'])}/{len(f8['predictions'])}", ""]
    for x in f8["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f9 = res["ninth"]
    gname = {"final": "最終順位（第8弾）", "run_diff": "得失点差でリーグ 3 位以内", "previous": "前の年の A クラス"}
    L += ["", "# 第9弾: 最終順位を使わない強さで群を分ける", "",
          f"ゲート（最終順位で分けた値が第8弾と同じ）: {'通った' if f9['gate']['ok'] else '通らなかった'}。", "",
          "各セルは alloc_net_strat の、正の単位の割合の「上の群 − 下の群」。(勝ち越しの回, 見込みの回)。", "",
          "| 群の決め方 | 上の群の単位 | (8, 8) | (8, 9) | (9, 8) | (9, 9) | リードを守った（上・下） | ビハインドから勝った（上・下） |", "|---|---|---|---|---|---|---|---|"]
    for g, v in f9["groups"].items():
        st = v["states"]
        L += [f"| {gname[g]} | {v['upper_units']} | " + " | ".join(f"{v['cells'][k]['a_minus_b']:+.2f}" for k in ("8,8", "8,9", "9,8", "9,9"))
              + f" | {st['A']['lead_held']:.3f}・{st['B']['lead_held']:.3f} | {st['A']['behind_won']:.3f}・{st['B']['behind_won']:.3f} |"]
    L += ["", f"読み（判定ではない）: **{f9['reading']}** " + {1: "力", 2: "両方、または決まらない", 3: "群の決め方"}[f9["reading"]], "",
          f"## 第9弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f9['predictions'])}/{len(f9['predictions'])}", ""]
    for x in f9["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f10 = res["tenth"]
    L += ["", "# 第10弾 A: 境界を動かす", "",
          f"ゲート（x = 8・9・10 と θ = 0 が第3〜5弾の数と同じ）: {'通った' if f10['gate']['ok'] else '通らなかった'}。"
          f"ε・θ の値: {'、'.join(format(e, 'g') for e in f10['eps']['all'])}（乱数で選んだのは {'、'.join(format(e, 'g') for e in f10['eps']['drawn'])}。種 {f10['eps']['seed']}）。", "",
          "つまみ 1（x 回まで。x = N + ε）: 「勝ち試合の得点 − 見込み」が負の球団年", "",
          "| x | 試合 | 負の単位 | 割合 | 差の中央値 |", "|---|---|---|---|---|"]
    for r in f10["dial_innings"]:
        L += [f"| {r['label']} | {r['games']} | {r['negative']}/{r['units']} | {r['share_negative']:.2f} | {r['median_gap']:+.3f} |"]
    L += ["", "つまみ 2（θ。見込みの中の同点の組を、重み θ で半分は勝ち・半分は負けに数える。得点は最終のまま）", "",
          "| θ | 負の単位 | 割合 | 差の中央値 |", "|---|---|---|---|"]
    for r in f10["dial_ties"]:
        L += [f"| {r['theta']:g} | {r['negative']}/{r['units']} | {r['share_negative']:.2f} | {r['median_gap']:+.3f} |"]
    L += ["", "線をずらす:", "", "| 片寄りの線 | 負の割合が線を超える最初の x | 線の内側に戻る最初の θ |", "|---|---|---|"]
    for line, v in f10["lines"].items():
        fmt = lambda z: "なし" if z is None else z if isinstance(z, str) else format(z, "g")  # noqa: E731
        L += [f"| {line} | {fmt(v['first_x_above'])} | {fmt(v['first_theta_within'])} |"]
    L += ["", "# 第10弾 B: 式1 を、翌年の B クラス・得失点差の順位で問い直す", "",
          "| 命題 | 元 | 対偶 | 逆 | 裏 | fisher_p | 読み | 総合 |", "|---|---|---|---|---|---|---|---|"]
    for x in f10["propositions"]:
        L += [f"| {x['id']} {x['statement']} | " + " | ".join(_cell(x["forms"][f]) for f in FORM_ORDER)
              + f" | {x['fisher_p']:.2g} | **{x['reading']}** {'割合を上げている' if x['reading'] == 1 else '上げていない'} | {x['judgement']['code']} |"]
    L += ["", f"## 第10弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f10['predictions'])}/{len(f10['predictions'])}", ""]
    for x in f10["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f11 = res["eleventh"]
    cname, yes = {"t1": "θ = 1（延長を残す）", "eight": "8 回まで"}, lambda b: "○" if b else "×"  # noqa: E731
    L += ["", "# 第11弾 A: 列を直す形を決める（θ = 1 と 8 回まで）", "",
          f"ゲート（負の数が第10弾・第3弾と同じ。8 回までの 3 命題が第4弾と同じ）: {'通った' if f11['gate']['ok'] else '通らなかった'}。", "",
          "| 候補 | 負の単位 | 片寄りなし（0.35〜0.65） | 揺らしても同じ（小さい ε の 5 つ） | 元の列との順位相関 | 元の並びを保つ（0.80 以上） | 使える |",
          "|---|---|---|---|---|---|---|"]
    for n, c in f11["candidates"].items():
        L += [f"| {cname[n]} | {c['negative']}/{c['units']}（{c['share_negative']:.2f}） | {yes(c['unbiased'])} | {yes(c['stable'])} | "
              f"{c['rho_original']:.2f} | {yes(c['keeps_order'])} | **{yes(c['usable'])}** |"]
    b = f11["between"]
    L += ["", f"2 つの候補どうし: 符号が同じ球団年 {b['sign_agreement']:.2f}、順位相関 {b['rho']:.2f} → "
          f"{'同じものを見ている' if b['same_thing'] else '同じものを見ているとは言えない'}。", "",
          "揺らし（θ = 1 − ε、x = 8 + ε）: 負の単位・符号が変わった単位・終了コードが変わった形", "",
          "| ε | θ = 1 − ε | 8 + ε |", "|---|---|---|"]
    for a, e in zip(f11["candidates"]["t1"]["shakes"], f11["candidates"]["eight"]["shakes"]):
        cell = lambda x: f"{x['negative']}・{x['sign_flips']}・{'、'.join(x['changed_forms']) or 'なし'}"  # noqa: E731
        L += [f"| {a['eps']:g}{'' if a['small'] else '（見るだけ）'} | {cell(a)} | {cell(e)} |"]
    L += ["", "同じ形の命題:", "", "| 命題 | 元 | 対偶 | 逆 | 裏 | 中日以外 | fisher_p | 読み | 総合 |", "|---|---|---|---|---|---|---|---|---|"]
    for n in ("t1", "eight"):
        for x in f11["column_propositions"][n]:
            h = x.get("held_out")
            L += [f"| {x['id']} {x['statement']} | " + " | ".join(_cell(x["forms"][f]) if f in x["forms"] else "省いた" for f in FORM_ORDER)
                  + f" | {str(h['hold']) + '/' + str(h['n']) if h else '-'} | {format(x['fisher_p'], '.2g') if x.get('fisher_p') is not None else '-'}"
                  + f" | {x.get('reading') or '-'} | {x['judgement']['code']} |"]
    d = f11["decision"]
    L += ["", "組ごとの総合の終了コードと読み: " + "、".join(f"{x['t1']}・{x['eight']} {'同じ' if x['same'] else '違う'}" for x in f11["shapes"]) + "。", "",
          f"決め方 {d['rule']}: **" + {2: "どちらでも結論は同じ。勧めるのは θ = 1", 3: "列の形で結論が変わる。未決",
                                     4: f"使えるのは片方だけ。勧めるのは {cname.get(d['choice'], 'なし')}"}[d["rule"]] + "**", "",
          "# 第11弾 B: 配分が不利 ⇒ 翌年 A クラス", "",
          "| 命題 | 元 | 対偶 | 逆 | 裏 | fisher_p | 読み | 総合 |", "|---|---|---|---|---|---|---|---|"]
    for x in f11["propositions"]:
        L += [f"| {x['id']} {x['statement']} | " + " | ".join(_cell(x["forms"][f]) for f in FORM_ORDER)
              + f" | {x['fisher_p']:.2g} | **{x['reading']}** {({1: '割合を上げている', 2: '上げていない', 5: '保留（単位が少ない）'})[x['reading']]} | {x['judgement']['code']} |"]
    L += ["", "条件に当たる中日の単位（その年 → 翌年）: "
          + ("、".join(f"{u['unit']}（{'A' if u['upper_half'] else 'B'} → {'A' if u['upper_half_next'] else 'B'}）" for u in f11["chunichi_condition_units"]) or "なし") + "。",
          "", f"## 第11弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f11['predictions'])}/{len(f11['predictions'])}", ""]
    for x in f11["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f12 = res["twelfth"]
    L += ["", "# 第12弾: B クラスの中で翌年 A に戻るのは、配分の巡り合わせか、分布がもともと良かったからか", "",
          f"ゲート（マスの単位の数が宣言と同じ。足すと第11弾の M52B と同じ）: {'通った' if f12['gate']['ok'] else '通らなかった'}。", "",
          "マスごとの「翌年 A クラス / 単位」（B クラスの 72 単位。高い = sim_p_upper が線以上）", "",
          "| 分布の線 | 不利でない・低い | 不利でない・高い | 不利・低い | 不利・高い |", "|---|---|---|---|---|"]
    for at, cs in f12["cells"].items():
        L += [f"| {at}{'（宣言の線）' if float(at) == f12['line'] else '（並べるだけ）'} | "
              + " | ".join(f"{c['next_upper']}/{c['n']}（{c['rate']:.2f}）" for c in cs) + " |"]
    L += ["", "| 命題 | 元 | 対偶 | 逆 | 裏 | fisher_p | 読み | 総合 |", "|---|---|---|---|---|---|---|---|"]
    for x in f12["propositions"]:
        L += [f"| {x['id']} {x['statement']} | " + " | ".join(_cell(x["forms"][f]) for f in FORM_ORDER)
              + f" | {x['fisher_p']:.2g} | **{x['reading']}** {({1: 'そろえても効く', 2: '効くとは言えない', 5: '保留（単位が少ない）'})[x['reading']]} | {x['judgement']['code']} |"]
    L += ["", f"読み（判定ではない）: **{f12['reading']}** "
          + {1: "配分の巡り合わせ", 2: "両方", 3: "分布がもともと良かった", 4: "分けられない"}[f12["reading"]], "",
          f"## 第12弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f12['predictions'])}/{len(f12['predictions'])}", ""]
    for x in f12["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]

    f13 = res["thirteenth"]
    mark = lambda r, k: f"{r[k]}{'' if r['inside'][k] else ' ✗'}"  # noqa: E731
    cols = ("win_negative", "rf_loss_positive", "wpct_low_positive", "wpct_high_positive")
    L += ["", "# 第13弾: 見込みの同点を決めるとき、負け試合の側をどう置くか", "",
          f"ゲート（重み 0・0 が道具と同じ。いまの置き方が 76・49）: {'通った' if f13['gate']['ok'] else '通らなかった'}。"
          f"{f13['units']} 球団年。✗ は線（0.35〜0.65）の外。", ""]
    for title, key, rows in (("つまみ 1: λ = 延長で負けた側が足す点（重みは勝ち・負けとも 1）", "lambda", f13["dial_lambda"]),
                             ("つまみ 2: θ負 = 負けの側だけの重み（勝ちの側は 1、λ = 0）", "theta_loss", f13["dial_theta_loss"])):
        L += [title, "", "| 値 | 勝ち試合の得点の差が負 | 負け試合の得点の差が正 | 勝率（点の少ない試合）の差が正 | 勝率（点の多い試合）の差が正 | 通る |",
              "|---|---|---|---|---|---|"]
        L += [f"| {r[key]:g} | " + " | ".join(mark(r, k) for k in cols) + f" | {'○' if r['passes'] else '×'} |" for r in rows] + [""]
    d = f13["decision"]
    L += [f"通る値: λ は {'、'.join(format(v, 'g') for v in f13['passing']['lambda']) or 'なし'}、"
          f"θ負 は {'、'.join(format(v, 'g') for v in f13['passing']['theta_loss']) or 'なし'}。", "",
          f"決め方 {d['rule']}: **" + ("勧めない" if d["value"] is None else f"{'λ' if d['dial'] == 'lambda' else 'θ負'} = {d['value']:g} を勧める") + "**"
          + (f"（負け試合の列の、元の並びとの順位相関 {f13['rho_loss_original']:.2f}）" if f13["rho_loss_original"] is not None else ""), "",
          f"## 第13弾の予想の当たり外れ（判定には使わない）: {sum(x['ok'] for x in f13['predictions'])}/{len(f13['predictions'])}", ""]
    for x in f13["predictions"]:
        L += [f"- ({x['id']}) {x['text']}: {'当たり' if x['ok'] else '外れ'}（{json.dumps(x['got'], ensure_ascii=False)}）"]
    return "\n".join(L) + "\n"


# ---- 年次シミュレーションの GIF -----------------------------------------------------------------------------------------
GIF_RECEIPT_SCHEMA = "aoi-c001-season-sim-gif/1"
GLYPHS = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
          "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001010010010",
          "8": "111101111101111", "9": "111101111001111", "+": "000010111010000", "C": "111100100100111", "P": "111101111100100"}   # 3×5 のドットの字
# 色番号: 0 地 / 1 墨 / 2 A クラス / 3 B クラス / 4 中日 / 5 K51 が成り立つ / 6 成り立たない / 7 補助線・除外の年
GIF_PALETTE = [(255, 255, 255), (51, 51, 51), (99, 179, 255), (176, 176, 176), (11, 60, 140), (91, 189, 62), (204, 61, 0),
               (221, 221, 221)]


def season_sim_years(repo: Path, pl) -> list[dict]:
    """GIF の材料: 年ごと・リーグごとに、最終順位の順の 6 球団（作り直しで A に入る確率・A クラスか・K51 が成り立つか）。"""
    base = repo / "cycles" / "c001-chunichi"
    cols = ("season", "team", "league", "rank", "upper_half", "sim_p_upper")
    full = pl.read_ndjson(base / "outputs" / "season.jsonl").select(cols)
    new = pl.read_ndjson(HERE / "r18_partial_results" / "r18_partial_panel_2026.jsonl").select(cols).cast(full.schema)
    excluded = {int(e["season"]) for e in tomllib.loads((base / "analysis.toml").read_text(encoding="utf-8")).get("exclude", [])}
    rows = pl.concat([full, new]).sort("season", "league", "rank", "team").to_dicts()
    years = []
    for season in sorted({r["season"] for r in rows}):
        leagues = {lg: [{"team": r["team"], "rank": r["rank"], "upper": r["upper_half"], "p": round(r["sim_p_upper"], 9),
                         "ok": (r["sim_p_upper"] < 0.5) == (not r["upper_half"])}
                        for r in rows if r["season"] == season and r["league"] == lg] for lg in ("C", "P")}
        units = [t for ts in leagues.values() for t in ts]
        years.append({"season": season, "excluded": season in excluded, "leagues": leagues,
                      "consistent": sum(t["ok"] for t in units), "units": len(units)})
    return years


def season_sim_grid(years: list[dict], i: int) -> list[bytearray]:
    """i 年目のコマ（256×160 の色番号）。上に年、左がセ・右がパ、下に K51 が成り立った球団の数を年ごとに積む帯。"""
    W, TOP, BASE = 256, 32, 128
    g, rect, text = _canvas()

    yr = years[i]
    text(str(yr["season"]), (W - 45) // 2, 6, 3)
    text("C", 8, 8, 2)
    text("P", W - 8 - 6, 8, 2)                                               # 年の数字と重ならないように右の端へ
    for x0, lg in ((8, "C"), (136, "P")):
        for n, t in enumerate(yr["leagues"][lg]):
            bx, h = x0 + 5 + n * 18, round(t["p"] * (BASE - TOP))
            rect(bx, BASE - h, bx + 12, BASE, 4 if t["team"] == "d" else 2 if t["upper"] else 3)
            if not t["ok"]:                                                  # K51 が成り立たない球団は、棒の頭を赤に
                rect(bx, BASE - max(h, 3), bx + 12, BASE - max(h, 3) + 3, 6)
            if t["team"] == "d":
                rect(bx + 3, BASE + 3, bx + 9, BASE + 6, 4)
        rect(x0, BASE, x0 + 112, BASE + 1, 1)                                # 地の線
        for x in range(x0, x0 + 112, 2):                                     # 0.5 の線
            g[(TOP + BASE) // 2][x] = 1
        for y in range(TOP, BASE, 2):                                        # A クラスと B クラスの境
            g[y][x0 + 56] = 1
    for n, past in enumerate(years):                                         # 下の帯: 年ごとに、K51 が成り立った球団の数
        cx = (W - (len(years) * 12 - 4)) // 2 + n * 12
        if n > i:
            rect(cx, 151, cx + 8, 152, 7)
            continue
        if past["excluded"]:
            rect(cx, 140, cx + 8, 152, 7)
        else:
            rect(cx, 152 - past["consistent"], cx + 8, 152, 5)
            rect(cx, 152 - past["units"], cx + 8, 152 - past["consistent"], 6)
        if n == i:
            rect(cx, 154, cx + 8, 155, 1)
    return g


def _canvas():
    """256×160 の色番号の盤と、四角・ドットの字を描く関数。"""
    W, H = 256, 160
    g = [bytearray(W) for _ in range(H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(max(y0, 0), min(y1, H)):
            g[y][max(x0, 0):min(x1, W)] = bytes([c]) * (min(x1, W) - max(x0, 0))

    def text(s, x, y, k, c=1):
        for ch in s:
            for n, bit in enumerate(GLYPHS[ch]):
                if bit == "1":
                    rect(x + n % 3 * k, y + n // 3 * k, x + (n % 3 + 1) * k, y + (n // 3 + 1) * k, c)
            x += 4 * k
    return g, rect, text


def summary_grids(years: list[dict], res: dict) -> list[list[bytearray]]:
    """年のコマの後に切り替わる、まとめの 2 コマ。

    1 枚目（中日の 15 年）: 年ごとの中日の「作り直しで A クラスに入る確率」の棒と、その下に最終順位。A クラスの年は水色、
      分析から除いた年は灰色、K51 が成り立たない年は棒の頭が赤。
    2 枚目（列の片寄り）: 「勝ち試合の得点 − 見込み」が負になった球団年の数（144 中）を、そのまま（9+）・延長を外す（9）・
      9 回も外す（8）で。点線が半分（72）。棒の下の 12 個の点は、同じ作り方で中日が「見込みより少ない」になった年の数。
    """
    TOP, BASE = 32, 120
    g1, rect, text = _canvas()
    text(str(years[0]["season"]), 8, 8, 2)
    text(str(years[-1]["season"]), 256 - 8 - 30, 8, 2)
    for x in range(8, 248, 2):
        g1[(TOP + BASE) // 2][x] = 1
    rect(8, BASE, 248, BASE + 1, 1)
    for n, yr in enumerate(years):
        t = next(t for ts in yr["leagues"].values() for t in ts if t["team"] == "d")
        bx, h = 10 + n * 16, round(t["p"] * (BASE - TOP))
        rect(bx, BASE - h, bx + 12, BASE, 7 if yr["excluded"] else 2 if t["upper"] else 4)
        if not t["ok"] and not yr["excluded"]:
            rect(bx, BASE - max(h, 3), bx + 12, BASE - max(h, 3) + 3, 6)
        text(str(t["rank"]), bx + 3, BASE + 6, 2, 2 if t["upper"] else 1)
    g2, rect, text = _canvas()
    third, units = res["third"], res["third"]["units"]
    p85 = {r["id"]: r for r in res["fifth"]["propositions"]}["P85"]["treatments"]
    bars = (("9+", third["variants"]["full"]["negative"], p85["b"]["forms"]["original"]),
            ("9", res["fourth"]["split"]["nine"]["negative"], p85["c"]["forms"]["original"]),
            ("8", third["variants"]["eight"]["negative"], p85["d"]["forms"]["original"]))
    for x in range(24, 232, 2):
        g2[BASE - (BASE - TOP) // 2][x] = 1
    rect(24, BASE, 232, BASE + 1, 1)
    for n, (label, neg, d) in enumerate(bars):
        bx, h = 40 + n * 64, round(neg / units * (BASE - TOP))
        rect(bx, BASE - h, bx + 48, BASE, 6 if neg / units > 0.65 else 5)
        text(str(neg), bx + 24 - len(str(neg)) * 4 + 1, BASE - h - 14, 2)
        text(label, bx + 24 - len(label) * 4 + 1, BASE + 5, 2)
        for i in range(d["n"]):                                              # 中日の年: 成り立った年を紺で
            rect(bx + i * 4, BASE + 20, bx + i * 4 + 3, BASE + 26, 4 if i < d["hold"] else 7)
    return [g1, g2]


def season_sim_gif(repo: Path, ffs: Path, out_dir: Path, file_prefix: str = "", file_suffix: str = "", scale: int = 2) -> dict:
    """年次シミュレーションの GIF と、隣に受領記録 <name>.json を書く（FluidFullSpeedSimulation の pixelwater で）。"""
    import subprocess
    pl, _, _ = load_modules(repo)
    if str(ffs) not in sys.path:
        sys.path.insert(0, str(ffs))
    import pixelwater as PW
    years = season_sim_years(repo, pl)
    res = json.loads((HERE / "kind_reask_results" / "kind_reask.json").read_text(encoding="utf-8"))
    # 切り替わる契機: 年のコマは 1.5 秒ずつ。最後の年（まだ使っていない 2026年）で 4 秒止まり、まとめの 2 コマ（5 秒ずつ）へ切り替わって、先頭に戻る
    delays = [150] * (len(years) - 1) + [400, 500, 500]
    grids = [season_sim_grid(years, i) for i in range(len(years))] + summary_grids(years, res)
    data = PW._gif(grids, GIF_PALETTE, scale=scale, delays=delays)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = PW.file_stem("c001", "sim-p-upper", None, 0, out_dir, file_prefix, file_suffix,
                        conditions=f"y{years[0]['season']}-{years[-1]['season']}")
    gif = stem.with_name(f"{stem.name}.gif")
    gif.write_bytes(data)
    train = [y for y in years if not y["excluded"] and y["season"] <= 2025]
    sha = lambda f: hashlib.sha256(Path(f).read_bytes()).hexdigest()  # noqa: E731
    commit = subprocess.run(["git", "-C", str(ffs), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or None
    receipt = {
        "schema": GIF_RECEIPT_SCHEMA, "files": {"gif": {"name": gif.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}},
        "frames": len(grids), "canvas": f"{256 * scale}x{160 * scale}",
        "scenes": [{"name": "years", "frames": len(years)}, {"name": "chunichi", "frames": 1}, {"name": "win_runs_gap", "frames": 1}],
        "plan": {"years": [years[0]["season"], years[-1]["season"]], "scale": scale, "delays_cs": delays, "palette": GIF_PALETTE},
        "inputs": {"season": sha(repo / "cycles/c001-chunichi/outputs/season.jsonl"),
                   "panel_2026": sha(HERE / "r18_partial_results/r18_partial_panel_2026.jsonl"),
                   "results": sha(HERE / "kind_reask_results/kind_reask.json")},
        "ffs": {"commit": commit, "pixelwater_sha256": sha(Path(PW.__file__))},
        "summary": {"k51_2012_2025": [sum(y["consistent"] for y in train), sum(y["units"] for y in train)],
                    "k51_2026": [years[-1]["consistent"], years[-1]["units"]],
                    "win_runs_gap_negative": [res["third"]["variants"]["full"]["negative"], res["fourth"]["split"]["nine"]["negative"],
                                              res["third"]["variants"]["eight"]["negative"], res["third"]["units"]]},
        "years": [{"season": y["season"], "excluded": y["excluded"], "consistent": y["consistent"], "units": y["units"],
                   "chunichi": next(t for ts in y["leagues"].values() for t in ts if t["team"] == "d")} for y in years],
    }
    js = stem.with_name(f"{stem.name}.json")
    js.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"gif": str(gif), "json": str(js), "frames": len(grids), "summary": receipt["summary"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=ROOT)
    ap.add_argument("--outdir", type=Path, help="判定の結果（kind_reask.json・kind_reask.md）の書き出し先")
    ap.add_argument("--gif-dir", type=Path, help="年次シミュレーションの GIF と受領記録の書き出し先（--ffs が要る）")
    ap.add_argument("--ffs", type=Path, help="FluidFullSpeedSimulation の作業ツリー（GIF の書き出しに pixelwater を使う）")
    ap.add_argument("--gif-file-prefix", default="", help="GIF の名前の前に付ける文字")
    ap.add_argument("--gif-file-suffix", default="", help="GIF の名前の後ろ（_r<NN> の後）に付ける文字")
    args = ap.parse_args(argv)
    if not args.outdir and not args.gif_dir:
        ap.error("--outdir か --gif-dir のどちらかが要る")
    if args.gif_dir and not args.ffs:
        ap.error("--gif-dir には --ffs が要る")
    if args.gif_dir:
        made = season_sim_gif(args.repo, args.ffs, args.gif_dir, args.gif_file_prefix, args.gif_file_suffix)
        print(f"🎞️ {made['gif']}（{made['frames']} コマ）")
    if not args.outdir:
        return 0
    res = analyze(args.repo)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "kind_reask.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "kind_reask.md").write_text(render(res), encoding="utf-8")
    problems = res["gate"]["problems"] + [x for k in ("sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth") for x in (res[k].get("gate") or {}).get("problems", [])]
    if problems:
        print("ゲートが通らなかった:", *problems, sep="\n  ", file=sys.stderr)
        return EXIT_GATE
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
