"""命題・判例・異議あり。仕様は docs/propositions.md（ここと食い違ったら docs が正しい）。

  load()      : 命題ファイル（TOML）を読み、検証する。ファイルの SHA-256 を返す（事前登録の証拠）
  evaluate()  : 1つの命題を、元の命題・対偶・逆・裏の4つの形で判定する
  render()    : 「異議あり」形式の Markdown
  check_claims(): 外部の主張（記事・レポート・他のAI）を、パイプラインで再現できるか確かめる

単位（unit）は SakAnalytics のシーズン表の1行（チーム×シーズン）。
条件は「列 演算子 定数」の積だけ。任意のコードは評価しない。存在しない列はエラーにする。
"""

from __future__ import annotations

import hashlib
import math
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
FORM_JA = {"original": "元の命題", "contrapositive": "対偶", "converse": "逆", "inverse": "裏"}
Z95 = 1.959963984540054
UNIT_COLS = ("season", "team", "team_name")


class PropositionError(ValueError):
    pass


# ---------- 読み込み ----------

def load(path: Path) -> tuple[list[dict], str]:
    raw = Path(path).read_bytes()
    props = tomllib.loads(raw.decode("utf-8")).get("proposition", [])
    ids = [p.get("id") for p in props]
    if len(set(ids)) != len(ids) or not all(ids):
        raise PropositionError(f"id は必須で一意: {ids}")
    for p in props:
        validate(p)
    return props, hashlib.sha256(raw).hexdigest()


def validate(p: dict) -> None:
    pid = p.get("id")
    for key in ("statement", "then", "strength"):
        if not p.get(key):
            raise PropositionError(f"{pid}: {key} が必要")
    if p["strength"] not in STRENGTH:
        raise PropositionError(f"{pid}: strength は {list(STRENGTH)} のどれか")
    for c in [*p.get("if", []), *p["then"]]:
        if set(c) != {"col", "op", "value"} or c["op"] not in OPS:
            raise PropositionError(f"{pid}: 条件は {{col, op, value}}、op は {list(OPS)}: {c}")
    skip = p.get("skip_forms", [])
    if skip:
        if set(skip) != {"converse", "inverse"}:
            raise PropositionError(f"{pid}: skip_forms で省けるのは逆と裏の組だけ（元の命題と対偶は省けない）")
        if not str(p.get("skip_reason", "")).strip():
            raise PropositionError(f"{pid}: skip_forms には skip_reason が必要")


# ---------- 条件 ----------

def _cond(conds: list[dict], columns) -> pl.Expr:
    if not conds:
        return pl.lit(True)
    exprs = []
    for c in conds:
        if c["col"] not in columns:
            raise PropositionError(f"存在しない列: {c['col']}（黙って偽にはしない）")
        exprs.append(OPS[c["op"]](pl.col(c["col"]), pl.lit(c["value"])))
    out = exprs[0]
    for e in exprs[1:]:
        out = out & e
    return out


def text(conds: list[dict]) -> str:
    return " かつ ".join(f"{c['col']} {c['op']} {c['value']}" for c in conds) if conds else "（すべての単位）"


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
    return out


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

def _forms(a: pl.Expr, b: pl.Expr, has_if: bool):
    forms = [("original", a, b), ("contrapositive", ~b, ~a)]
    if has_if:
        forms += [("converse", b, a), ("inverse", ~a, ~b)]
    return forms


def _unit_key(r: dict) -> str:
    return f"{r['team']}-{r['season']}"


def _counterexamples(df: pl.DataFrame, x: pl.Expr, y: pl.Expr, p: dict, form: str, focus: str | None) -> list[dict]:
    used = list(dict.fromkeys(c["col"] for c in [*p.get("if", []), *p["then"]]))
    context = [c for c in p.get("context", []) if c in df.columns and c not in used]
    surprise = p.get("surprise")
    if surprise and surprise not in df.columns:
        raise PropositionError(f"{p['id']}: surprise の列がない: {surprise}")
    cond_x, cond_y = (p.get("if", []), p["then"]) if form in ("original", "contrapositive") else (p["then"], p.get("if", []))
    rows = []
    for r in df.filter(x & ~y).iter_rows(named=True):
        rows.append({
            "unit": _unit_key(r), "season": r["season"], "team": r["team"], "team_name": r["team_name"],
            "focus": r["team"] == focus,
            "values": {c: r[c] for c in used}, "context": {c: r[c] for c in context},
            "surprise": r[surprise] if surprise else None,
            "question": f"{r['team_name']} {r['season']} は「{text(cond_x)}」を満たすのに「{text(cond_y)}」を満たさない。なぜか？",
            "links": p.get("links", []),
        })
    return sorted(rows, key=lambda c: (c["surprise"] is None, -abs(c["surprise"] or 0), c["season"], c["team"]))


def evaluate(p: dict, st: pl.DataFrame, excluded: pl.DataFrame | None = None, focus: str | None = None) -> dict:
    kind, threshold = STRENGTH[p["strength"]]
    min_n, alpha = int(p.get("min_n", 10)), float(p.get("alpha", 0.05))
    df = scope_filter(st, p.get("scope"))
    a, b = _cond(p.get("if", []), df.columns), _cond(p["then"], df.columns)
    forms = []
    for name, x, y in _forms(a, b, bool(p.get("if")) and not p.get("skip_forms")):
        flags = df.select(x=x, y=y)
        undetermined = flags.filter(pl.col("x").is_null() | pl.col("y").is_null()).height  # 空の値で判定できない行
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
    by = {f["form"]: f for f in forms}
    # 論理から必ず成り立つこと: 元の命題と対偶、逆と裏は、判例が同じ
    for f1, f2 in (("original", "contrapositive"), ("converse", "inverse")):
        if f1 in by and {c["unit"] for c in by[f1]["counterexamples"]} != {c["unit"] for c in by[f2]["counterexamples"]}:
            raise AssertionError(f"{p['id']}: {f1} と {f2} の判例が一致しない（実装の誤り）")
    excluded_cx = []
    if excluded is not None and excluded.height:
        ex = scope_filter(excluded, p.get("scope"))
        excluded_cx = _counterexamples(ex, a, b, p, "original", focus)
    return {
        "id": p["id"], "statement": p["statement"], "strength": p["strength"], "kind": kind, "threshold": threshold,
        "if": p.get("if", []), "then": p["then"], "scope": p.get("scope", {}), "units": df.height,
        "min_n": min_n, "alpha": alpha, "links": p.get("links", []), "forms": forms,
        "objection": any(f["counterexamples"] for f in forms),
        "skipped_forms": p.get("skip_forms", []), "skip_reason": p.get("skip_reason"),
        "excluded_counterexamples": excluded_cx, "source": p.get("source"),
    }


# ---------- 外部の主張 ----------

def check_claims(claims: list[dict], st: pl.DataFrame) -> list[dict]:
    """claim = {id, statement, source, date, kind, ...}。kind:
         sum / mean / count : column を filter で絞って集計し、value ± tolerance と比べる
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
            if c["kind"] != "count" and c["column"] not in df.columns:
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
            got = float(df.height) if c["kind"] == "count" else getattr(df[c["column"]], c["kind"])()
            ok = abs(got - c["value"]) <= c.get("tolerance", 0)
            r.update(status="reproduced" if ok else "not-reproduced", claimed=c["value"],
                     computed=int(got) if c["kind"] == "count" else round(float(got), 3), tolerance=c.get("tolerance", 0), units=df.height)
        out.append(r)
    return out


# ---------- 出力 ----------

def _fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def render(results: list[dict], meta: dict, limit: int = 10) -> str:
    lines = ["# 異議あり — 命題の判定記録（自動生成）", "",
             "判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。",
             f"命題ファイル SHA-256: `{meta.get('sha256', '-')}` / コード: `{meta.get('code_version') or '測定なし'}`", "",
             "判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。", ""]
    for r in results:
        thr = "反例なし" if r["kind"] == "universal" else f"{r['threshold']:.2f}"
        lines += [f"## {r['id']}: {_cell(r['statement'])}", "",
                  f"- もし: `{text(r['if'])}` ならば: `{text(r['then'])}`",
                  f"- 強さ: {STRENGTH_JA[r['strength']]}（{r['strength']}, 基準 {thr}）/ 範囲: {r['scope'] or '全体'} / 単位数: {r['units']}",
                  *([f"- 逆・裏は評価しない（理由: {r['skip_reason']}）"] if r.get("skipped_forms") else []),
                  "", "| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 |", "|---|---|---|---|---|---|---|---|---|"]
        for f in r["forms"]:
            ci = f"{_fmt(f['rate'])} [{_fmt(f['ci'][0])}, {_fmt(f['ci'][1])}]"
            lines.append(f"| {FORM_JA[f['form']]} | {f['n']} | {f['hold']} | {ci} | {_fmt(f['base_rate'])} "
                         f"| {_fmt(f['lift'])} | {_fmt(f['fisher_p'], 3)} | {f['undetermined']} | {VERDICT_JA[f['verdict']]} |")
        for f in r["forms"]:
            if f["form"] in ("contrapositive", "inverse") or not f["counterexamples"]:
                continue
            twin = "対偶" if f["form"] == "original" else "裏"
            cx = f["counterexamples"]
            lines += ["", f"**異議あり！** {FORM_JA[f['form']]}に判例 {len(cx)} 件（{twin}の判例も同じ）", ""]
            for c in cx[:limit]:
                mark = " **(focus)**" if c["focus"] else ""
                vals = ", ".join(f"{k}={_v(v)}" for k, v in {**c["values"], **c["context"]}.items())
                sup = f" / surprise={_v(c['surprise'])}" if c["surprise"] is not None else ""
                links = f" → {', '.join(c['links'])}" if c["links"] else ""
                lines += [f"- {c['team_name']} {c['season']}{mark}: {vals}{sup}", f"  - {c['question']}{links}"]
            if len(cx) > limit:
                lines.append(f"- ほか {len(cx) - limit} 件（propositions.jsonl を参照）")
        if r["excluded_counterexamples"]:
            lines += ["", "**除外中の判例**（統計からは除いたが、判例としては残す）", ""]
            for c in r["excluded_counterexamples"]:
                vals = ", ".join(f"{k}={_v(v)}" for k, v in {**c["values"], **c["context"]}.items())
                lines.append(f"- {c['team_name']} {c['season']}{' **(focus)**' if c['focus'] else ''}: {vals}")
        lines.append("")
    return "\n".join(lines)


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
    if isinstance(v, float):
        return f"{v:+.2f}" if abs(v) >= 0.005 or v == 0 else f"{v:.3g}"
    return "-" if v is None else str(v)
