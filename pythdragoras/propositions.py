"""命題・判例・異議あり。仕様は docs/propositions.md（ここと食い違ったら docs が正しい）。

  load()      : 命題ファイル（TOML）を読み、検証する。ファイルの SHA-256 を返す（事前登録の証拠）
  evaluate()  : 1つの命題を、元の命題・対偶・逆・裏の4つの形で判定する
  render()    : 「異議あり」形式の Markdown
  check_claims(): 外部の主張（記事・レポート・他のAI）を、パイプラインで再現できるか確かめる

単位（unit）は SakAnalytics のシーズン表の1行（チーム×シーズン）。
条件は「列 演算子 定数」の積だけ。任意のコードは評価しない。存在しない列はエラーにする。
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import operator
import tomllib
from pathlib import Path

import polars as pl

STRENGTH = {  # 言葉と基準の対応は固定。データに合わせて調整しない
    "always": ("universal", None),
    "almost_always": ("statistical", 0.90),
    "usually": ("statistical", 0.75),
    "more_often_than_not": ("statistical", 0.50),
}
STRENGTH_JA = {"always": "必ず", "almost_always": "ほとんど", "usually": "概ね", "more_often_than_not": "多くの場合"}
OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}
VERDICT_JA = {"Supported": "支持", "Rejected": "棄却", "Refined": "修正", "Inconclusive": "判断保留"}
FORM_JA = {"original": "元の命題", "contrapositive": "対偶", "converse": "逆", "inverse": "裏", "held_out": "きっかけ以外"}
Z95 = 1.959963984540054
UNIT_COLS = ("season", "team", "team_name")


class PropositionError(ValueError):
    """命題ファイルの誤り（終了コード 64）。"""


class DataError(PropositionError):
    """データの誤り。命題が参照する列がない、など（終了コード 65）。"""


# 判定の終了コード。論理上の異議は 1〜6、仕組みの不具合は 64 以上（sysexits の慣習）。
# 0 だけが「異議なし」。原因が分からないときも 0 にはしない。
EXIT = {
    0: ("異議なし", "No objection"),
    1: ("異議あり（例外あり）", "Objection! (counterexamples within the declared strength)"),
    2: ("異議あり（主張が強すぎる）", "Objection! (the claim is stronger than the evidence)"),
    3: ("異議あり（不成立）", "Objection! (not supported)"),
    4: ("待った！判断保留", "Hold it! (inconclusive)"),
    5: ("待った！判定できない単位がある", "Hold it! (undetermined units)"),
    6: ("事前登録の違反の疑い", "Pre-registration breach (redefined under the same ID)"),
    64: ("命題ファイルの誤り", "Invalid proposition file"),
    65: ("データの誤り", "Data error"),
    66: ("入力がない", "No input"),
    70: ("実装の誤り", "Internal error"),
}
STAGE_ORDER = ("original", "held_out", "contrapositive", "converse", "inverse")


# ---------- 読み込み ----------

def load(path: Path) -> tuple[list[dict], str]:
    raw = Path(path).read_bytes()
    props = tomllib.loads(raw.decode("utf-8")).get("proposition", [])
    ids = [p.get("id") for p in props]
    if len(set(ids)) != len(ids) or not all(ids):
        raise PropositionError(f"id は必須で一意: {ids}")
    seen: set[str] = set()
    by_signature: dict[str, str] = {}
    parent_of = {p["id"]: p.get("parent") for p in props}
    for p in props:
        validate(p)
        if p.get("parent") and p["parent"] not in seen:  # 親は先に定義されている必要がある（循環しない）
            raise PropositionError(f"{p['id']}: parent {p['parent']} がこのファイルの前の方にない")
        ident = identity(p)
        other = by_signature.get(ident["signature"])
        if other and other not in _ancestors(p["id"], parent_of):
            raise PropositionError(f"{p['id']}: {other} と同じ問い（{ident['key']}）。"
                                   f"作り直しなら parent に {other} を書き、change に何を変えたかを書く")
        by_signature.setdefault(ident["signature"], p["id"])
        seen.add(p["id"])
    return props, hashlib.sha256(raw).hexdigest()


def _ancestors(pid: str, parent_of: dict) -> set[str]:
    out, cur = set(), parent_of.get(pid)
    while cur:
        out.add(cur)
        cur = parent_of.get(cur)
    return out


def _canon(conds: list[dict]) -> list[str]:
    return sorted(f"{c['col']}{c['op']}{json.dumps(c['value'], ensure_ascii=False)}" for c in conds)


def identity(p: dict) -> dict:
    """命題が「何を問うているか」の識別子。番号・文言・強さ・注記には左右されない。

    key       : 読める形。[範囲] 条件 => 結論（条件の並び順は正規化する）
    signature : key の指紋。同じなら同じ問い（作り直しは parent で明示する。そうでなければ読み込みで止める）
    family    : 範囲と結論だけの指紋。同じなら「兄弟」（同じことを別の条件から問うている）
    """
    sc = p.get("scope") or {}
    scope = [f"{k}={sc[k]}" for k in ("league", "team", "seasons") if k in sc]
    scope += [f"where:{w}" for w in _canon(sc.get("where", []))]
    head = f"[{', '.join(scope) or 'all'}]"
    then = " & ".join(_canon(p["then"]))
    cond = " & ".join(_canon(p.get("if", [])))
    if p.get("if_any"):
        groups = sorted("(" + " & ".join(_canon(g)) + ")" for g in p["if_any"])
        cond = " & ".join(x for x in (cond, "(" + " | ".join(groups) + ")") if x)
    key = f"{head} {cond or '*'} => {then}"
    h = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]  # noqa: E731
    return {"key": key, "signature": h(key), "family": h(f"{head} => {then}")}


def definition_sha(p: dict) -> str:
    """命題1つの定義の指紋。同じ id のまま定義が変わったら台帳で分かる。"""
    keys = ("statement", "strength", "if", "then", "scope", "min_n", "alpha", "skip_forms", "parent", "motivated_by")
    body = {k: p.get(k) for k in keys}
    if p.get("if_any"):  # 後から加えた項目。使うときだけ入れる（既存の命題の指紋を変えない）
        body["if_any"] = p["if_any"]
    body = json.dumps(body, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def validate(p: dict) -> None:
    pid = p.get("id")
    for key in ("statement", "then", "strength"):
        if not p.get(key):
            raise PropositionError(f"{pid}: {key} が必要")
    if p["strength"] not in STRENGTH:
        raise PropositionError(f"{pid}: strength は {list(STRENGTH)} のどれか")
    scope = p.get("scope") or {}
    if set(scope) - {"league", "team", "seasons", "where"}:
        raise PropositionError(f"{pid}: scope に書けるのは league, team, seasons, where: {sorted(scope)}")
    any_ = p.get("if_any", [])
    if any_ and (not isinstance(any_, list) or not all(isinstance(g, list) and g for g in any_)):
        raise PropositionError(f"{pid}: if_any は条件の組（空でない配列）の配列")
    for c in [*_if_conds(p), *p["then"], *scope.get("where", [])]:
        if set(c) != {"col", "op", "value"} or c["op"] not in OPS:
            raise PropositionError(f"{pid}: 条件は {{col, op, value}}、op は {list(OPS)}: {c}")
    for key in ("falsifier", "note"):
        if key in p and not (isinstance(p[key], str) and p[key].strip()):
            raise PropositionError(f"{pid}: {key} は空でない文字列")
    skip = p.get("skip_forms", [])
    if skip:
        if set(skip) != {"converse", "inverse"}:
            raise PropositionError(f"{pid}: skip_forms で省けるのは逆と裏の組だけ（元の命題と対偶は省けない）")
        if not str(p.get("skip_reason", "")).strip():
            raise PropositionError(f"{pid}: skip_forms には skip_reason が必要")
    if p.get("parent") and not str(p.get("change", "")).strip():
        raise PropositionError(f"{pid}: parent があるときは change（何をなぜ変えたか）が必要")
    if p.get("motivated_by"):
        if not p.get("parent"):
            raise PropositionError(f"{pid}: motivated_by は作り直した命題（parent あり）にだけ書ける")
        bad = [u for u in p["motivated_by"] if not re.fullmatch(r"[a-z]+-\d{4}", str(u))]
        if bad:
            raise PropositionError(f"{pid}: motivated_by は 'team-season'（例: d-2019）: {bad}")


# ---------- 条件 ----------

def _cond(conds: list[dict], columns) -> pl.Expr:
    if not conds:
        return pl.lit(True)
    exprs = []
    for c in conds:
        if c["col"] not in columns:
            raise DataError(f"存在しない列: {c['col']}（黙って偽にはしない）")
        exprs.append(OPS[c["op"]](pl.col(c["col"]), pl.lit(c["value"])))
    out = exprs[0]
    for e in exprs[1:]:
        out = out & e
    return out


def text(conds: list[dict]) -> str:
    return " かつ ".join(f"{c['col']} {c['op']} {c['value']}" for c in conds) if conds else "（すべての単位）"


def _if_conds(p: dict) -> list[dict]:
    """前件に出てくる条件をすべて（if と if_any の各組）。"""
    return [*p.get("if", []), *(c for g in p.get("if_any", []) for c in g)]


def _antecedent(p: dict, columns) -> pl.Expr:
    """前件 = if のすべて かつ（if_any の組のどれか）。if_any の各組は「かつ」でつないだ条件。"""
    a = _cond(p.get("if", []), columns)
    if p.get("if_any"):
        any_ = _cond(p["if_any"][0], columns)
        for g in p["if_any"][1:]:
            any_ = any_ | _cond(g, columns)
        a = a & any_
    return a


def if_text(p: dict) -> str:
    parts = [text(p["if"])] if p.get("if") else []
    if p.get("if_any"):
        parts.append("（" + " または ".join(f"[{text(g)}]" for g in p["if_any"]) + "）")
    return " かつ ".join(parts) if parts else "（すべての単位）"


def scope_filter(st: pl.DataFrame, scope: dict | None) -> pl.DataFrame:
    scope = scope or {}
    out = st
    if "league" in scope:
        out = out.filter(pl.col("league") == scope["league"])
    if "team" in scope:
        out = out.filter(pl.col("team") == scope["team"])
    if "seasons" in scope:
        a, _, b = str(scope["seasons"]).partition("-")
        out = out.filter(pl.col("season").is_between(int(a), int(b or a)))
    if scope.get("where"):  # 条件で絞った範囲（例: 得点がリーグ5位以下のチームの間では）。値が空の単位は範囲に入れない
        out = out.filter(_cond(scope["where"], st.columns))
    return out


def scope_unknown(st: pl.DataFrame, scope: dict | None) -> int:
    """where の値が空で、範囲に入るか判定できない単位の数（黙って範囲の外にしない）。"""
    scope = scope or {}
    if not scope.get("where"):
        return 0
    base = scope_filter(st, {k: v for k, v in scope.items() if k != "where"})
    return base.select(w=_cond(scope["where"], st.columns)).filter(pl.col("w").is_null()).height


# ---------- 統計 ----------

def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    # 判定は区間の端と基準の比較なので、浮動小数点の誤差を端に残さない
    lo = 0.0 if k == 0 else round(max(0.0, c - h), 12)
    hi = 1.0 if k == n else round(min(1.0, c + h), 12)
    return (lo, hi)


def fisher_greater(a: int, b: int, c: int, d: int) -> float:
    """2×2表 [[a, b], [c, d]]（行: X/非X、列: Y/非Y）で、X が Y を起こりやすくするかの片側 p 値。"""
    r1, c1, n = a + b, a + c, a + b + c + d
    if n == 0 or r1 == 0 or c1 == 0:
        return 1.0
    denom = math.comb(n, c1)
    hi = min(r1, c1)
    return sum(math.comb(r1, i) * math.comb(n - r1, c1 - i) for i in range(a, hi + 1)) / denom


def verdict(kind: str, threshold: float | None, n: int, k: int, ci: tuple[float, float], p: float,
            min_n: int, alpha: float) -> str:
    """docs/propositions.md の判定表。上から順に最初に当てはまるもの。"""
    if n < min_n:
        return "Inconclusive"
    if kind == "universal":
        return "Supported" if k == n else "Rejected"
    lo, hi = ci
    if lo >= threshold:
        return "Supported"
    if lo < threshold <= hi:
        return "Inconclusive"
    return "Refined" if p < alpha else "Rejected"


# ---------- 判定 ----------

def form_code(verdict_: str, counterexamples: int, undetermined: int) -> int:
    """1つの形の終了コード。"""
    if verdict_ == "Inconclusive":
        return 4
    if counterexamples:
        return {"Supported": 1, "Refined": 2, "Rejected": 3}[verdict_]
    if verdict_ != "Supported":  # 判例なしで棄却・修正にはならないはず
        raise AssertionError(f"判例なしで {verdict_}（実装の誤り）")
    return 5 if undetermined else 0


def judge(result: dict, ledger_definitions: int = 1) -> dict:
    """形を決まった順に調べ、最初に 0 でなかったところで止まる。

    stage: none（元の命題で止まった）/ provisional（元の命題と対偶まで 0）/ confirmed（逆・裏まで 0）
    """
    if ledger_definitions > 1:
        j = {"code": 6, "stage": "none", "form": None}
        return {**j, "reason": reason_text(j, "ja")}
    forms = {f["form"]: f for f in result["forms"]}
    if result.get("held_out"):
        forms["held_out"] = result["held_out"]
    passed = []
    for name in STAGE_ORDER:
        f = forms.get(name)
        if f is None:
            continue
        cx = f["counterexamples"]
        code = form_code(f["verdict"], len(cx), f.get("undetermined", 0))
        if code:
            units = [c if isinstance(c, str) else c["unit"] for c in cx]
            stage = "provisional" if {"original", "contrapositive"} <= set(passed) else "none"
            j = {"code": code, "stage": stage, "form": name, "units": units, "n": f["n"], "min_n": result["min_n"],
                 "ci": list(f["ci"]), "undetermined": f.get("undetermined", 0)}
            return {**j, "reason": reason_text(j, "ja")}
        passed.append(name)
    full = {"converse", "inverse"} <= set(passed)
    j = {"code": 0, "stage": "confirmed" if full else "provisional", "form": None,
         "skip_reason": None if full else (result.get("skip_reason") or "")}
    return {**j, "reason": reason_text(j, "ja")}


FORM_EN = {"original": "original", "contrapositive": "contrapositive", "converse": "converse", "inverse": "inverse",
           "held_out": "held-out"}


def reason_text(j: dict, lang: str = "ja") -> str:
    """判定の構造（コード・形・判例の単位など）から、表示用の理由を作る。判定には使わない。"""
    en = lang == "en"
    if j["code"] == 0:
        if j.get("skip_reason") is None:
            return ""
        why = j["skip_reason"] or ("no condition" if en else "条件なしの命題")
        return f"converse and inverse skipped ({why})" if en else f"逆・裏は省略（{why}）"
    if j["code"] == 6:
        return "more than one definition under the same ID in the ledger" if en else "台帳に同じ id の定義が複数ある"
    units = j.get("units") or []
    if units:
        more = (" and more" if en else " ほか") if len(units) > 5 else ""
        return (f"{len(units)} counterexample(s): " if en else f"判例 {len(units)} 件: ") + ", ".join(units[:5]) + more
    if j["code"] == 4:
        lo, hi = j["ci"]
        return (f"n={j['n']} (min_n={j['min_n']}), interval {lo:.2f}-{hi:.2f}" if en
                else f"n={j['n']}（min_n={j['min_n']}）、成立率の区間 {lo:.2f}〜{hi:.2f}")
    return (f"{j['undetermined']} undetermined unit(s)" if en else f"判定できない単位 {j['undetermined']} 件")

def _forms(a: pl.Expr, b: pl.Expr, has_if: bool):
    forms = [("original", a, b), ("contrapositive", ~b, ~a)]
    if has_if:
        forms += [("converse", b, a), ("inverse", ~a, ~b)]
    return forms


def _unit_key(r: dict) -> str:
    return f"{r['team']}-{r['season']}"


def _counterexamples(df: pl.DataFrame, x: pl.Expr, y: pl.Expr, p: dict, form: str, focus: str | None) -> list[dict]:
    used = list(dict.fromkeys(c["col"] for c in [*_if_conds(p), *p["then"]]))
    context = [c for c in p.get("context", []) if c in df.columns and c not in used]
    surprise = p.get("surprise")
    if surprise and surprise not in df.columns:
        raise DataError(f"{p['id']}: surprise の列がない: {surprise}")
    a_text, b_text = if_text(p), text(p["then"])
    cond_x, cond_y = (a_text, b_text) if form in ("original", "contrapositive") else (b_text, a_text)
    rows = []
    for r in df.filter(x & ~y).iter_rows(named=True):
        rows.append({
            "unit": _unit_key(r), "season": r["season"], "team": r["team"], "team_name": r["team_name"],
            "focus": r["team"] == focus,
            "values": {c: r[c] for c in used}, "context": {c: r[c] for c in context},
            "surprise": r[surprise] if surprise else None,
            "question": f"{r['team_name']} {r['season']} は「{cond_x}」を満たすのに「{cond_y}」を満たさない。なぜか？",
            "links": p.get("links", []),
        })
    return sorted(rows, key=lambda c: (c["surprise"] is None, -abs(c["surprise"] or 0), c["season"], c["team"]))


def evaluate(p: dict, st: pl.DataFrame, excluded: pl.DataFrame | None = None, focus: str | None = None) -> dict:
    r = _evaluate(p, st, excluded, focus)
    r["judgement"] = judge(r)
    return r


def _evaluate(p: dict, st: pl.DataFrame, excluded: pl.DataFrame | None, focus: str | None) -> dict:
    kind, threshold = STRENGTH[p["strength"]]
    min_n, alpha = int(p.get("min_n", 10)), float(p.get("alpha", 0.05))
    df = scope_filter(st, p.get("scope"))
    outside = scope_unknown(st, p.get("scope"))
    a, b = _antecedent(p, df.columns), _cond(p["then"], df.columns)
    forms = []
    for name, x, y in _forms(a, b, bool(_if_conds(p)) and not p.get("skip_forms")):
        flags = df.select(x=x, y=y)
        undetermined = flags.filter(pl.col("x").is_null() | pl.col("y").is_null()).height + outside  # 空の値で判定できない行
        flags = flags.drop_nulls()
        xs, ys = flags["x"], flags["y"]
        n, k = int(xs.sum()), int((xs & ys).sum())
        c_, d_ = int((~xs & ys).sum()), int((~xs & ~ys).sum())
        ci = wilson(k, n)
        p_val = fisher_greater(k, n - k, c_, d_)
        base = float(ys.mean()) if len(ys) else 0.0
        forms.append({
            "form": name, "n": n, "hold": k, "undetermined": undetermined, "rate": k / n if n else None, "ci": ci,
            "base_rate": base, "lift": (k / n) / base if n and base else None, "fisher_p": p_val,
            "verdict": verdict(kind, threshold, n, k, ci, p_val, min_n, alpha),
            "counterexamples": _counterexamples(df, x, y, p, name, focus),
        })
        forms[-1]["code"] = form_code(forms[-1]["verdict"], len(forms[-1]["counterexamples"]), undetermined)
    by = {f["form"]: f for f in forms}
    # 論理から必ず成り立つこと: 元の命題と対偶、逆と裏は、判例が同じ
    for f1, f2 in (("original", "contrapositive"), ("converse", "inverse")):
        if f1 in by and {c["unit"] for c in by[f1]["counterexamples"]} != {c["unit"] for c in by[f2]["counterexamples"]}:
            raise AssertionError(f"{p['id']}: {f1} と {f2} の判例が一致しない（実装の誤り）")
    held_out = None
    if p.get("motivated_by"):
        keys = pl.concat_str([pl.col("team"), pl.lit("-"), pl.col("season").cast(pl.Utf8)])
        rest = df.filter(~keys.is_in(p["motivated_by"]))
        flags = rest.select(x=a, y=b).drop_nulls()
        n, k = int(flags["x"].sum()), int((flags["x"] & flags["y"]).sum())
        c_, d_ = int((~flags["x"] & flags["y"]).sum()), int((~flags["x"] & ~flags["y"]).sum())
        ci, p_val = wilson(k, n), fisher_greater(k, n - k, c_, d_)
        held_out = {"excluded_units": list(p["motivated_by"]), "n": n, "hold": k, "rate": k / n if n else None,
                    "ci": ci, "fisher_p": p_val, "verdict": verdict(kind, threshold, n, k, ci, p_val, min_n, alpha),
                    "counterexamples": [c["unit"] for c in _counterexamples(rest, a, b, p, "original", focus)]}
    excluded_cx = []
    if excluded is not None and excluded.height:
        ex = scope_filter(excluded, p.get("scope"))
        excluded_cx = _counterexamples(ex, a, b, p, "original", focus)
    return {
        "id": p["id"], "statement": p["statement"], "strength": p["strength"], "kind": kind, "threshold": threshold,
        "if": p.get("if", []), "if_any": p.get("if_any", []), "then": p["then"], "scope": p.get("scope", {}), "units": df.height,
        "min_n": min_n, "alpha": alpha, "links": p.get("links", []), "forms": forms,
        "objection": any(f["counterexamples"] for f in forms),
        "skipped_forms": p.get("skip_forms", []), "skip_reason": p.get("skip_reason"),
        "excluded_counterexamples": excluded_cx, "source": p.get("source"),
        "parent": p.get("parent"), "change": p.get("change"), "held_out": held_out,
        "falsifier": p.get("falsifier"), "note": p.get("note"),
        "conditions": len(_if_conds(p)) + len(p["then"]),
        "definition_sha256": definition_sha(p),
        **identity(p),
    } | {"judgement": None}


# ---------- 台帳 ----------

def update_ledger(path: Path, results: list[dict], data_sha: str, code_version: str | None) -> list[dict]:
    """評価ごとに1行を追記する。同じ（命題の定義, データ）の組は二度書かない。"""
    path = Path(path)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
    have = {(r["id"], r["definition_sha256"], r["data_sha256"]) for r in rows}
    now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
    for r in results:
        key = (r["id"], r["definition_sha256"], data_sha)
        if key in have:
            continue
        rows.append({
            "recorded_at": now, "id": r["id"], "definition_sha256": r["definition_sha256"], "data_sha256": data_sha,
            "code_version": code_version, "objection": r["objection"],
            "forms": {f["form"]: {"verdict": f["verdict"], "n": f["n"], "counterexamples": len(f["counterexamples"])}
                      for f in r["forms"]},
        })
        have.add(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return rows


def ledger_summary(rows: list[dict], pid: str) -> dict:
    """台帳から: 評価回数、元の命題への異議の回数（どれかの形への異議も別に）、
    直近の「元の命題に判例なし」の連続回数、同じ id の定義の数（2以上なら事前登録の違反の疑い）。"""
    mine = [r for r in rows if r["id"] == pid]
    streak = 0
    for r in reversed(mine):
        if r["forms"].get("original", {}).get("counterexamples", 1) == 0:
            streak += 1
        else:
            break
    orig = [r["forms"].get("original", {}).get("counterexamples", 0) > 0 for r in mine]
    return {"evaluations": len(mine), "objections": sum(orig), "objections_any_form": sum(r["objection"] for r in mine),
            "no_objection_streak": streak,
            "definitions": len(dict.fromkeys(r["definition_sha256"] for r in mine))}


# ---------- 外部の主張 ----------

def check_claims(claims: list[dict], st: pl.DataFrame) -> list[dict]:
    """claim = {id, statement, source, date, kind, ...}。kind:
         sum / mean / count : column を filter で絞って集計し、value ± tolerance と比べる
         ratio              : Σnum / Σden（例: 期間通算の1点差勝率 = Σw_1 / Σ(w_1+l_1)）。den は列名の配列
         interpretation     : 解釈。数で再現できないので、そのまま記録する
    """
    out = []
    for c in claims:
        r = {k: c.get(k) for k in ("id", "statement", "source", "date", "kind")}
        if c.get("kind") == "interpretation":
            r.update(status="interpretation", note="解釈の主張。観測では再現できない")
            out.append(r)
            continue
        try:
            scoped = scope_filter(st, c.get("scope"))
            df = scoped.filter(_cond(c.get("filter", []), st.columns))
            if c["kind"] == "ratio":
                missing = [x for x in [c["num"], *c["den"]] if x not in df.columns]
                if missing:
                    raise PropositionError(f"存在しない列: {missing}")
            elif c["kind"] != "count" and c["column"] not in df.columns:
                raise PropositionError(f"存在しない列: {c['column']}")
        except PropositionError as e:
            r.update(status="not-measurable", note=str(e))
            out.append(r)
            continue
        if scoped.height == 0:  # データ自体がない（取得範囲の外など）
            r.update(status="not-measurable", note="範囲内の単位がない（取得範囲を確認）")
        elif c["kind"] != "count" and df.height == 0:  # 主張の前提（filter）に当てはまる単位がない
            r.update(status="not-reproduced", claimed=c["value"], computed=None, units=0,
                     note="主張の条件に当てはまる単位がない")
        else:
            if c["kind"] == "count":
                got = float(df.height)
            elif c["kind"] == "ratio":
                den = sum(float(df[x].sum()) for x in c["den"])
                got = float(df[c["num"]].sum()) / den if den else None
            else:
                got = getattr(df[c["column"]], c["kind"])()
            if got is None:  # 分母が0、または値がすべて空
                r.update(status="not-measurable", note="値を計算できない（分母が0、または値がすべて空）")
                out.append(r)
                continue
            ok = abs(got - c["value"]) <= c.get("tolerance", 0)
            r.update(status="reproduced" if ok else "not-reproduced", claimed=c["value"],
                     computed=int(got) if c["kind"] == "count" else round(float(got), 3), tolerance=c.get("tolerance", 0), units=df.height)
        out.append(r)
    return out


# ---------- 出力 ----------

def _fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def label(code: int, lang: str = "ja") -> str:
    """終了コードを表示用の言葉に変える。判定はコードで行い、言葉は表示のためだけに使う。"""
    ja, en = EXIT[code]
    return en if lang == "en" else ja


def render(results: list[dict], meta: dict, limit: int = 10, ledger: list[dict] | None = None, lang: str = "ja") -> str:
    lines = ["# 異議あり — 命題の判定記録（自動生成）", "",
             "判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。",
             f"命題ファイル SHA-256: `{meta.get('sha256', '-')}` / コード: `{meta.get('code_version') or '測定なし'}`", "",
             "判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。", ""]
    family: dict[str, list[str]] = {}
    for r in results:
        if r.get("family"):
            family.setdefault(r["family"], []).append(r["id"])
    siblings = {i: [o for o in ids if o != i] for ids in family.values() for i in ids}
    children = {}
    for r in results:
        if r.get("parent"):
            children.setdefault(r["parent"], []).append(r)
    if children:
        lines += ["## 命題の系譜", ""]
        def walk(pid, depth):
            for c in children.get(pid, []):
                lines.append(f"{'  ' * depth}- {pid} → **{c['id']}**: {_cell(c['change'])}")
                walk(c["id"], depth + 1)
        for r in results:
            if not r.get("parent") and r["id"] in children:
                walk(r["id"], 0)
        lines.append("")
    for r in results:
        thr = "反例なし" if r["kind"] == "universal" else f"{r['threshold']:.2f}"
        j = r["judgement"]
        stage = {"none": "", "provisional": "（仮: 元の命題と対偶まで）", "confirmed": "（逆・裏まで）"}[j["stage"]]
        lines += [f"## {r['id']}: {_cell(r['statement'])}", "",
                  f"- **判定: exit {j['code']} {label(j['code'], lang)}**{stage}"
                  + (f" — {FORM_JA.get(j['form'], j['form'])}: {j['reason']}" if j["form"] else (f" — {j['reason']}" if j["reason"] else "")),
                  f"- もし: `{if_text(r)}` ならば: `{text(r['then'])}`",
                  f"- 識別子: `{r.get('key', '-')}`（指紋 `{r.get('signature', '-')}`）",
                  *([f"- 兄弟（範囲と結論が同じ、条件が違う）: {', '.join(siblings[r['id']])}"] if siblings.get(r["id"]) else []),
                  f"- 強さ: {STRENGTH_JA[r['strength']]}（{r['strength']}, 基準 {thr}）/ 範囲: {r['scope'] or '全体'} / 単位数: {r['units']}",
                  *([f"- 逆・裏は評価しない（理由: {r['skip_reason']}）"] if r.get("skipped_forms") else []),
                  *([f"- 親: {r['parent']}（変更: {_cell(r['change'])}）"] if r.get("parent") else []),
                  *([f"- 見直す条件（反証）: {_cell(r['falsifier'])}"] if r.get("falsifier") else []),
                  *([f"- 注記: {_cell(r['note'])}"] if r.get("note") else []),
                  f"- 条件の数: {r.get('conditions', '-')}（例外条件を増やしすぎていないかの目安）",
                  *_ledger_line(ledger, r["id"]),
                  "", "| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |", "|---|---|---|---|---|---|---|---|---|---|"]
        for f in r["forms"]:
            ci = f"{_fmt(f['rate'])} [{_fmt(f['ci'][0])}, {_fmt(f['ci'][1])}]"
            lines.append(f"| {FORM_JA[f['form']]} | {f['n']} | {f['hold']} | {ci} | {_fmt(f['base_rate'])} "
                         f"| {_fmt(f['lift'])} | {_fmt(f['fisher_p'], 3)} | {f['undetermined']} | {VERDICT_JA[f['verdict']]} | {f['code']} |")
        for f in r["forms"]:
            if f["form"] in ("contrapositive", "inverse") or not f["counterexamples"]:
                continue
            twin = "対偶" if f["form"] == "original" else "裏"
            cx = f["counterexamples"]
            lines += ["", f"**{label(f['code'], lang)}** {FORM_JA[f['form']]}に判例 {len(cx)} 件（{twin}の判例も同じ）", ""]
            for c in cx[:limit]:
                mark = " **(focus)**" if c["focus"] else ""
                vals = ", ".join(f"{k}={_v(v)}" for k, v in {**c["values"], **c["context"]}.items())
                sup = f" / surprise={_v(c['surprise'])}" if c["surprise"] is not None else ""
                links = f" → {', '.join(c['links'])}" if c["links"] else ""
                lines += [f"- {c['team_name']} {c['season']}{mark}: {vals}{sup}", f"  - {c['question']}{links}"]
            if len(cx) > limit:
                lines.append(f"- ほか {len(cx) - limit} 件（propositions.jsonl を参照）")
        h = r.get("held_out")
        if h:
            lines += ["", f"**きっかけ以外での判定**（作り直しのきっかけ {', '.join(h['excluded_units'])} を除く）: "
                          f"n={h['n']} 成立={h['hold']} 成立率={_fmt(h['rate'])} [{_fmt(h['ci'][0])}, {_fmt(h['ci'][1])}] "
                          f"→ **{VERDICT_JA[h['verdict']]}**"
                          + (f" / 判例: {', '.join(h['counterexamples'][:limit])}" if h["counterexamples"] else " / 判例なし")]
        if r["excluded_counterexamples"]:
            lines += ["", "**除外中の判例**（統計からは除いたが、判例としては残す）", ""]
            for c in r["excluded_counterexamples"]:
                vals = ", ".join(f"{k}={_v(v)}" for k, v in {**c["values"], **c["context"]}.items())
                lines.append(f"- {c['team_name']} {c['season']}{' **(focus)**' if c['focus'] else ''}: {vals}")
        lines.append("")
    return "\n".join(lines)


def _ledger_line(ledger, pid) -> list[str]:
    if not ledger:
        return []
    s = ledger_summary(ledger, pid)
    warn = "（**同じ id で定義が変わっている。事前登録の違反の疑い**）" if s["definitions"] > 1 else ""
    return [f"- 台帳: 評価 {s['evaluations']} 回、元の命題に異議あり {s['objections']} 回"
            f"（どれかの形に異議あり {s['objections_any_form']} 回）、"
            f"直近で元の命題に判例がない連続 {s['no_objection_streak']} 回{warn}"]


def render_claims(claims: list[dict]) -> str:
    if not claims:
        return ""
    lines = ["# 外部の主張との照合（自動生成）", "",
             "外部の主張は観測ではない。再現できても観測にはならず、再現できなければそれ自体が調べるべき矛盾になる。", "",
             "| id | 主張 | 出どころ | 状態 | 主張値 | 計算値 |", "|---|---|---|---|---|---|"]
    ja = {"reproduced": "再現", "not-reproduced": "**再現せず**", "not-measurable": "測定不能", "interpretation": "解釈（数では確かめない）"}
    for c in claims:
        lines.append(f"| {c['id']} | {_cell(c['statement'])} | {c.get('source')} {c.get('date') or ''} | {ja[c['status']]} "
                     f"| {_v(c.get('claimed'))} | {_v(c.get('computed'))} |")
    return "\n".join(lines) + "\n"


def _cell(x) -> str:
    return str(x).replace("|", "\\|")


def _v(v):
    """表示用。率など1未満の値は小数3桁、勝利数などは符号つき小数2桁。"""
    if isinstance(v, float):
        return f"{v:.3f}" if abs(v) < 1 else f"{v:+.2f}"
    return "-" if v is None else str(v)


# ---------- コマンド ----------

def run_judge(results: list[dict], ids: list[str] | None, ledger: list[dict] | None, keep_going: bool,
              lang: str, out=print) -> int:
    """命題を順に判定して表示し、最初に 0 でなかったコードを返す（keep_going でなければそこで止まる）。"""
    known = [r["id"] for r in results]
    for i in ids or []:
        if i not in known:
            out(f"[64] {i}: {label(64, lang)}（そんな id はない: {known}）")
            return 64
    first = 0
    for r in results:
        if ids and r["id"] not in ids:
            continue
        defs = ledger_summary(ledger, r["id"])["definitions"] if ledger else 1
        j = judge(r, defs)
        forms = FORM_EN if lang == "en" else FORM_JA
        where = f" {forms.get(j['form'], j['form'])}:" if j["form"] else ""
        out(f"[{j['code']}] {r['id']} {label(j['code'], lang)}{where} {reason_text(j, lang)}".rstrip())
        if j["code"] and not first:
            first = j["code"]
            if not keep_going:
                break
    return first


def main(argv=None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description="命題の判定結果を終了コードで返す（0 = 異議なし）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("judge", help="propositions.jsonl を順に判定する")
    j.add_argument("results", type=Path, help="pythdragoras.py が書いた propositions.jsonl")
    j.add_argument("--id", nargs="+", dest="ids")
    j.add_argument("--ledger", type=Path, help="台帳（既定: 同じディレクトリの ledger.jsonl）")
    j.add_argument("--keep-going", action="store_true", help="0 でない命題があっても最後まで表示する")
    j.add_argument("--report-only", action="store_true",
                   help="判定を表示するだけで、異議（1〜6）では失敗にしない。仕組みの不具合（64 以上）は失敗にする")
    j.add_argument("--lang", choices=["ja", "en"], default="ja")
    args = ap.parse_args(argv)

    if not args.results.exists():
        print(f"[66] {label(66, args.lang)}: {args.results}", file=sys.stderr)
        return 66
    results = [json.loads(line) for line in args.results.read_text(encoding="utf-8").splitlines()]
    ledger_path = args.ledger or args.results.with_name("ledger.jsonl")
    ledger = ([json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
              if ledger_path.exists() else None)
    code = run_judge(results, args.ids, ledger, args.keep_going or args.report_only, args.lang)
    return code if (code >= 64 or not args.report_only) else 0


if __name__ == "__main__":
    raise SystemExit(main())
