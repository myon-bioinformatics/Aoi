#!/usr/bin/env python3
"""2026年の確かめ（R18）の部分実行: 試合の記録だけから作れる列で、事前登録した読み方を当てる（探索）。

[research/R18-confirmation-2026.md](../research/R18-confirmation-2026.md) の手順 2〜3 は、npb.jp からの取得（イニング集計・チーム打撃を含む）を
前提にしている。ここでは取得をせず、リポジトリに保存済みの試合（2013〜2025年と、確定した 2026年の 858 試合）から
sakanalytics で作れる列だけで、`[confirm].detail` の命題を 2026年の単位に当てる。**これは正規の `outputs/confirmation.md` の代わりではない。**

  - 試合の記録から作れない列（`inn_*` = イニング集計、`bat_*` = チーム打撃など。確定済み season.jsonl にあって、ここで作った表にない列）は、
    2026年の単位では空にする。その列を使う命題（P62 など）は「判定不能」になる（R18 が先に書いたとおり）。
  - 2012年の試合は入力にない。2026年の単位の値には、`rf_low_streak` などの「何年続いているか」が 2013年から数え始めた値になる違いがありうる
    （2026年の判定に使う「2年以上」では結果が変わらない）。
  - 先に対照: 同じ処理を確定済みの season.jsonl の年（2012〜2025年、2020年を除く 156 単位）に当てて、R18 に登録された学習データの数
    （P52 の逆の判例 5・判例 10、P64 の前件 26 のうち B 22 など）が再現できなければ、2026年の結果を出さずに止まる。
  - 読み方は R18 の登録のまま（P52: 逆の判例 2 件以上 / 判例 3 件以上 / それ以外は「学習データと矛盾しない」。P79: 成立が半分を超えるか）。
    単位が 12 しかないので統計の判定はせず、「確かめられた」とは書かない。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/r18_partial_confirmation.py --games games.jsonl \\
      --config cycles/c001-chunichi/analysis.toml --propositions cycles/c001-chunichi/propositions.toml \\
      --committed cycles/c001-chunichi/outputs/season.jsonl --out-md /tmp/r18.md --out-json /tmp/r18.json [--out-panel-2026 /tmp/p.jsonl]
  games.jsonl は games_table_from_observed.py で作る。作った 2026年の行（--out-panel-2026）は --panel で渡せば、試合から作り直さずに読み方だけ当て直せる。
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
import tempfile
import tomllib
from collections import Counter
from pathlib import Path

STATUSES = ("成立", "判例", "逆の判例", "どちらも当たらない", "判定不能")
# R18 に登録された学習データ（2012〜2025年、2020年を除く 156 単位）の数。{id: {状態: 単位数}}。R18 の表の「学習データの率」の欄から。
# P62 は登録が 2013〜2025年の 16 単位中 16（2012年はイニング集計がなく判定不能）、P78・P76・P80 は「きっかけを除いて」の数なので、
# きっかけの単位（P78 は 2014 中日、P76・P80 は 2019 中日）が成立の側に 1 つ入った数を登録値にする。
REGISTERED = {
    "P52": {"逆の判例": 5, "判例": 10, "B": 78, "A": 78},
    "P50": {"逆の判例": 10, "判例": 9, "A": 78, "B": 78},
    "P64": {"成立": 22, "判例": 4},
    "P62": {"成立": 16, "判例": 0},
    "P78": {"成立": 7, "判例": 1},
    "P76": {"成立": 5, "判例": 7},
    "P80": {"成立": 6, "判例": 6},
    "P79": {"成立": 52, "判例": 27},
    "P51": {"成立": 10, "判例": 3},
}
CHUNICHI = "d"
WEAK = {"P52": "中日は前件の一部（得点と失点の比に近い量）を先に知っている", "P51": "中日は前件の一部を先に知っている"}


def counts(check: dict) -> Counter:
    return Counter(u["status"] for u in check["units"])


def control(checks: dict) -> list[str]:
    """学習データ側の数を、登録した値と比べる。違いを文字で返す（空なら再現できた）。"""
    problems = []
    for pid, want in REGISTERED.items():
        c = counts(checks[pid])
        got = {k: c.get(k, 0) for k in want if k not in ("A", "B")}
        for k, v in got.items():
            if v != want[k]:
                problems.append(f"{pid} {k}: 手元 {v} ≠ 登録 {want[k]}")
        if pid == "P52":                           # 後件が B: B = 成立 + 逆の判例、A = 判例 + どちらも当たらない
            ys = (c["成立"] + c["逆の判例"], c["判例"] + c["どちらも当たらない"])
            problems += [f"{pid} {n}クラスの単位数: 手元 {v} ≠ 登録 {want[n]}" for n, v in zip("BA", ys) if v != want[n]]
        if pid == "P50":                           # 後件が A: A = 成立 + 逆の判例、B = 判例 + どちらも当たらない
            ys = (c["成立"] + c["逆の判例"], c["判例"] + c["どちらも当たらない"])
            problems += [f"{pid} {n}クラスの単位数: 手元 {v} ≠ 登録 {want[n]}" for n, v in zip("AB", ys) if v != want[n]]
    return problems


def expected(train: Counter, new: Counter) -> dict:
    """学習データの率を 2026年の単位数に当てた期待値。逆の判例 = 後件に当たる単位のうち前件に当たらない率 × 2026年の後件に当たる単位数、
    判例 = 後件に当たらない単位のうち前件に当たる率 × 2026年の後件に当たらない単位数。"""
    y_tr, n_tr = train["成立"] + train["逆の判例"], train["判例"] + train["どちらも当たらない"]
    y_new, n_new = new["成立"] + new["逆の判例"], new["判例"] + new["どちらも当たらない"]
    if not y_tr or not n_tr:
        raise ValueError("学習データに、後件に当たる単位か当たらない単位がない（期待値を出せない）")
    return {"converse": train["逆の判例"] / y_tr * y_new, "exception": train["判例"] / n_tr * n_new}


def read_p52(c: Counter) -> str:
    """R18 に登録された P52 の読み方。"""
    out = []
    if c["逆の判例"] >= 2:
        out.append("2026年の B クラスを学習データほどは拾えていない（逆の判例が 2 件以上）")
    if c["判例"] >= 3:
        out.append("A クラスを誤って拾いすぎ（判例が 3 件以上）")
    return "、".join(out) if out else "学習データと矛盾しない（逆の判例 2 件未満、判例 3 件未満）"


def read_p79(c: Counter) -> str:
    """R18: 前件に当たった単位のうち成立が半分を超えるかを記録する。超えなくても鏡の形は取り下げない。"""
    n = c["成立"] + c["判例"]
    if n == 0:
        return "前件に当たる単位がない"
    word = "半分を超える" if c["成立"] * 2 > n else "半分を超えない" + ("（ちょうど半分）" if c["成立"] * 2 == n else "")
    return f"前件に当たる {n} 単位のうち成立 {c['成立']}、{word}。単位が少ないので鏡の形は取り下げない"


def names(check: dict, status: str, team_names: dict) -> str:
    found = [f"{team_names.get(u['unit'].split('-')[0], u['unit'])}（{u['unit']}）" for u in check["units"] if u["status"] == status]
    return "、".join(found) if found else "なし"


def read_record(pid: str, tr: Counter, nw: Counter, check: dict, team_names: dict) -> str:
    """読み方が登録されていない命題の記録。R18 が記録を求めたもの（P64 の前件に当たった単位と判例、P78・P76・P80 の範囲に入った単位）を書く。"""
    defined = sum(nw[s] for s in STATUSES if s != "判定不能")
    if pid == "P64":
        rate = (tr["成立"] + tr["判例"]) / sum(tr[s] for s in STATUSES if s != "判定不能")
        ant = nw["成立"] + nw["判例"]
        return (f"記録のみ: 前件に当たる {ant} 単位（学習データの率なら {rate * defined:.1f}）、成立 {nw['成立']}（{names(check, '成立', team_names)}）、"
                f"判例 {nw['判例']}（{names(check, '判例', team_names)}）")
    if pid in ("P78", "P76", "P80"):
        inside = [u for u in check["units"] if u["status"] != "判定不能"]
        if not inside:
            return "記録のみ: 範囲に入る単位なし（R18 の期待値は 0〜2）"
        return "記録のみ: 範囲に入る単位 " + "、".join(f"{team_names.get(u['unit'].split('-')[0], u['unit'])}（{u['unit']}）{u['status']}" for u in inside)
    return "記録のみ（R18 は読み方を決めていない）"


def build_result(train_checks: dict, new_checks: dict, team_names: dict) -> dict:
    result = {}
    for pid in REGISTERED:
        tr, nw = counts(train_checks[pid]), counts(new_checks[pid])
        entry = {"train": {s: tr.get(s, 0) for s in STATUSES}, "2026": {s: nw.get(s, 0) for s in STATUSES},
                 "units": {u["unit"]: u["status"] for u in new_checks[pid]["units"]},
                 "weak": WEAK.get(pid)}
        if pid in ("P52", "P50"):
            e = expected(tr, nw)
            entry["expected"] = {"逆の判例": round(e["converse"], 2), "判例": round(e["exception"], 2)}
            entry["exceptions"] = {"判例": names(new_checks[pid], "判例", team_names), "逆の判例": names(new_checks[pid], "逆の判例", team_names)}
        if pid == "P52":
            entry["reading"] = read_p52(nw)
        elif pid == "P79":
            entry["reading"] = read_p79(nw)
        elif pid == "P62":
            entry["reading"] = ("判定不能（2026年のイニング単位の集計がこの実行にない）" if nw["判定不能"] == sum(nw.values()) else "記録のみ")
        else:
            entry["reading"] = read_record(pid, tr, nw, new_checks[pid], team_names)
        result[pid] = entry
    return result


def render(result: dict, team_names: dict, missing: list[str]) -> str:
    prefixes = ", ".join(f"{p}*" for p in sorted({c.split("_")[0] for c in missing}))
    lines = ["# 2026年の確かめ（R18）の部分実行（探索）", "",
             "**正規の `outputs/confirmation.md` の代わりではない。** 試合の記録（保存済み）から sakanalytics で作れる列だけで、"
             "R18 の `[confirm].detail` の命題を 2026年の 12 単位に当てた。2026年の行は、試合の表から sakanalytics を走らせて作ったもの"
             "（`r18_partial_panel_2026.jsonl`）。", "",
             f"- 作れなかった列（確定済み season.jsonl にあって、ここで作った表にない列）: {len(missing)} 列（{prefixes}）。2026年の単位では空にした。"
             "その列を使う命題は判定不能になる",
             "- 先に対照: 同じ処理を確定済み season.jsonl の 156 単位に当てて、R18 に登録された学習データの数が全部再現できることを確かめてから出した",
             "- 読み方は [R18](../../research/R18-confirmation-2026.md) の登録のまま。12 単位なので統計の判定はせず、**「確かめられた」とは書かない**",
             "- 2026年の A・B は全球団すでに知られていた。中日は前件の一部も先に知っていた（弱い単位）", "",
             "## 命題ごとの数", "",
             "| id | 学習データ（成立 / 判例 / 逆の判例 / どちらも当たらない / 判定不能） | 2026年（同） | 期待値（逆の判例 / 判例） | 読み方 |",
             "|---|---|---|---|---|"]
    for pid, e in result.items():
        exp = "—" if "expected" not in e else f"{e['expected']['逆の判例']:.2f} / {e['expected']['判例']:.2f}"
        lines.append(f"| {pid} | {' / '.join(str(e['train'][s]) for s in STATUSES)} | {' / '.join(str(e['2026'][s]) for s in STATUSES)} | {exp} | {e['reading']} |")
    lines += ["", "## 単位ごとの状態", "", "判定不能: 値が空。範囲外: その命題の範囲（チーム・条件）に入らない単位。", "",
              "| 単位 | " + " | ".join(result) + " |", "|---|" + "---|" * len(result)]
    units = sorted({u for e in result.values() for u in e["units"]} | {f"{t}-2026" for t in team_names})
    for u in units:
        lines.append(f"| {team_names.get(u.split('-')[0], u)}（{u}） | " + " | ".join(e["units"].get(u, "範囲外") for e in result.values()) + " |")
    notes = [f"- {pid}: {e['weak']}" for pid, e in result.items() if e["weak"]]
    notes += [f"- {pid}: 判例 {e['exceptions']['判例']}、逆の判例 {e['exceptions']['逆の判例']}（出た単位は、まず問いとして記録する。R18 の限界）"
              for pid, e in result.items() if "exceptions" in e and (e["2026"]["判例"] or e["2026"]["逆の判例"])]
    lines += ["", "## 注意", ""] + notes + [
        "- P62 は 2026年のイニング単位の集計（PR #3 の形）が手元になく判定不能のまま。2026年の試合の得点表は保存済みだが、"
        "PR #3 の集計をここで作り直してはいない",
        "- ここで作った表と正規のパイプラインの違い: 2012年の試合がない、イニング・打撃の列がない。"
        "正規の実行（pipeline.toml の `years` を 2012-2026 にする）でどう変わるかは、その実行を待つ", ""]
    return "\n".join(lines)


def load_panel(pl, path: Path):
    return pl.read_ndjson(path, infer_schema_length=None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", type=Path, help="2013〜2026年の試合表（games_table_from_observed.py の出力）。--panel があれば要らない")
    ap.add_argument("--panel", type=Path, help="2026年の行（--out-panel-2026 で書き出したもの）。あれば試合から作り直さない")
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--propositions", type=Path, required=True)
    ap.add_argument("--committed", type=Path, required=True, help="確定済みの season.jsonl（対照の相手、2026年の列の並びの基準）")
    ap.add_argument("--out-md", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-panel-2026", type=Path)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    if bool(args.games) == bool(args.panel):
        print("--games か --panel のどちらか 1 つが要る", file=sys.stderr)
        return 2
    if args.panel and args.out_panel_2026:
        print("--out-panel-2026 は --games から作るときだけ（--panel は読むだけ）", file=sys.stderr)
        return 2

    sys.path.insert(0, str(args.repo / "pythdragoras"))
    sys.path.insert(0, str(args.repo / "sakanalytics"))
    import polars as pl
    import propositions as P
    import pythdragoras as PD
    import sakanalytics as sa

    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    confirm = cfg.get("confirm") or {}
    seasons = [int(y) for y in confirm.get("seasons", [])]
    detail = list(confirm.get("detail", []))
    if sorted(detail) != sorted(REGISTERED) or seasons != [2026]:
        print(f"[confirm] が想定と違う: seasons={seasons}, detail={detail}", file=sys.stderr)
        return 2
    props, _ = P.load(args.propositions)
    by_id = {p["id"]: p for p in props}
    committed, _ = PD.apply_exclusions(load_panel(pl, args.committed), cfg.get("exclude", []))
    train_seasons = sorted(committed["season"].unique().to_list())

    if args.panel:
        new = load_panel(pl, args.panel)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "season.jsonl"
            with contextlib.redirect_stdout(io.StringIO()):
                if sa.main(["--games", str(args.games), "--config", str(args.config), "--out", str(out)]) != 0:
                    print("sakanalytics が失敗した", file=sys.stderr)
                    return 2
            new = load_panel(pl, out)
        if args.out_panel_2026:
            new.filter(pl.col("season") == 2026).write_ndjson(args.out_panel_2026)
    new = new.filter(pl.col("season") == 2026)
    if new.height != 12:
        print(f"2026年の行が 12 でない: {new.height}", file=sys.stderr)
        return 2
    missing = sorted(c for c in committed.columns if c not in new.columns)       # 読み込みごとに列の並びが変わりうるので、並べ替えて固定する
    new = new.with_columns([pl.lit(None).alias(c) for c in missing])

    train_checks = {pid: P.confirm_units(by_id[pid], committed, train_seasons) for pid in detail}
    problems = control(train_checks)
    if problems:
        print("対照が合わない（学習データの数が R18 の登録と違う）。2026年の結果は出さない:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 2
    new_checks = {pid: P.confirm_units(by_id[pid], new, [2026]) for pid in detail}
    team_names = {t: v["name"] for t, v in cfg["teams"].items()}
    result = build_result(train_checks, new_checks, team_names)
    md = render(result, team_names, missing)
    js = json.dumps({"missing_columns": missing, "result": result}, ensure_ascii=False, indent=2) + "\n"
    args.out_md.write_text(md, encoding="utf-8")
    args.out_json.write_text(js, encoding="utf-8")
    print(f"書き出し: {args.out_md}, {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
