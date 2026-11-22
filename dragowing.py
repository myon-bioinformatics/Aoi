"""🐉 DRAgoWing: 記録 → 図の JSON と HTML（標準ライブラリだけの単一ファイル）。

    python dragowing.py RESULTS [--out DIR] [--svg]     # 📈 index.html・propositions.html（と svg/）
    python dragowing.py RESULTS --forms [--id P1]       # 🧾 四つの形の 2×2（文字）
    python dragowing.py --ffss RECORDS [--out DIR]      # 📊 FFSS の図（ffss.html と svg/F<NN>_*.svg）
    python dragowing.py PAGE.html [--tag div]           # 🔢 HTML の要素を数える（ブラウザなし）

判定はやり直さない。図は plotly の figure JSON で、HTML はブラウザの plotly.js、SVG は親の
``plotly_min``（vendor/tools/stdlib_min、Chrome なし）が描く。ページの文章は自作の ``markdown.py``
（vendor/markdown）。PNG は書かない（スクショは browser-test-kit の持ち物）。

α（このファイルの外）: ``overlap.py`` は重なりの native の経路（numpy・polars と PythDRagoras の
rule_search、dev グループ）。``__main__.py`` は ``python -m dragowing`` の入口。
Python からも Node（py_launch）からも、関数の名前で呼べる（main・count_elements・load_overlap・
heatmap_figure・write_ffss・render_report など）。
"""
from __future__ import annotations

import argparse, html, http.client, importlib, importlib.util, json, math, operator, re, sys, tempfile, types
import urllib.error, urllib.request
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
from math import ceil
from pathlib import Path


# ====================================================================================================
# 🔢 HTML の要素を数える（html.parser、ブラウザなし）
# ====================================================================================================

class _Counter(HTMLParser):
    def __init__(self, names: set[str] | None):
        super().__init__()
        self.names = names
        self.counts: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.names is not None and tag not in self.names:
            return
        self.counts[tag] = self.counts.get(tag, 0) + 1


def count_elements(html: str, tag_names: tuple[str, ...] | None = None) -> dict[str, int]:
    """Return a map of tag name to open-tag count. ``tag_names`` limits which tags are counted."""
    names = set(tag_names) if tag_names else None
    parser = _Counter(names)
    parser.feed(html)
    parser.close()
    return parser.counts


def _alpha(name: str):
    """α の同じディレクトリのモジュール（overlap.py）。パッケージの中ならその一員として、単独なら仮のパッケージで読む。"""
    if __package__:
        return importlib.import_module(f"{__package__}.{name}")
    package = "_dragowing_alpha"
    if package not in sys.modules:
        module = types.ModuleType(package)
        module.__path__ = [str(Path(__file__).resolve().parent)]
        sys.modules[package] = module
    return importlib.import_module(f"{package}.{name}")


# ====================================================================================================
# 📒 記録（結果ディレクトリの JSONL を記録の順のまま読む）（旧 records.py）
# 結果ディレクトリの JSONL を、記録の順のまま読む。
# ====================================================================================================

def read_jsonl(path: Path) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"結果が読めない: {path.name}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def select_items(items: list[dict], present: dict[str, bool], ids: list[str] | None) -> list[dict]:
    """--id の順。式 ID で sets.jsonl が無いときは、結果に無いとは書かない。"""
    if not ids:
        return list(items)
    chosen = []
    # Index only conventional string IDs, and only for batches of at least eight lookups.
    # Unusual record IDs keep the original equality-based behavior.
    index = None
    if len(ids) >= 8 and all(type(item.get("id")) in (str, type(None)) for item in items):
        index = {}
        for item in items:
            index.setdefault(item.get("id"), []).append(item)
    for ident in ids:
        needed = "sets.jsonl" if ident.startswith("E") else "propositions.jsonl" if ident.startswith("P") else None
        if needed and not present.get(needed):
            raise FileNotFoundError(f"結果が読めない: {needed}")
        hit = index.get(ident, []) if index is not None else [item for item in items if item.get("id") == ident]
        if not hit:
            raise ValueError(f"{ident} は判定済みの結果にない")
        chosen.extend(hit)
    return chosen


def read_ffss(path) -> dict[tuple[str, str], list[dict]]:
    """FFSS の ``run`` / ``verify --jsonl`` の記録を (実験 ID, run) ごとの行に（記録の順のまま）。"""
    out: dict[tuple[str, str], list[dict]] = {}
    for index, row in enumerate(read_jsonl(path), 1):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) for k in ("id", "run")):
            raise ValueError(f"FFSS record {index}: id and run must be strings")
        out.setdefault((row["id"], row["run"]), []).append(row)
    return out


# ====================================================================================================
# 🌐 Plotly.js（jsDelivr の CDN、埋め込み用の取得）（旧 plotly_cdn.py）
# Plotly.js for DRAgoWing HTML (jsDelivr, no SRI/hash pin).
#
# Figure JSON/initialization remains DRAgoWing-owned. web-ui alignment is tracked
# separately; this module uses the versionless jsDelivr dist URL directly.
# ====================================================================================================

# BEGIN DRAgoWing Plotly runtime
PLOTLY_JS_URL = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min/plotly.min.js"
PLOTLY_JS_MAX_BYTES = 8 * 1024 * 1024


def verify_plotly_js(raw: bytes) -> bytes:
    """Return CDN bytes or fail before any decoding, caching or execution."""
    if not isinstance(raw, bytes):
        raise TypeError("Plotly.js payload must be bytes")
    if not raw:
        raise RuntimeError("Plotly.js CDN returned an empty body")
    if len(raw) > PLOTLY_JS_MAX_BYTES:
        raise RuntimeError(f"Plotly.js exceeds {PLOTLY_JS_MAX_BYTES} byte limit")
    return raw


def _fetch_plotly_bytes(*, timeout: float, user_agent: str) -> bytes:
    """Explicitly fetch the allowlisted jsDelivr bundle with a bounded read.

    Rendering helpers do not call this function. Consumers own successful-byte
    caching; cached/local bytes can be checked with verify_plotly_js().
    """
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be finite and positive")
    request = urllib.request.Request(
        PLOTLY_JS_URL, headers={"User-Agent": user_agent},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status is None:
                status = getattr(response, "getcode", lambda: 200)()
            if status != 200:
                raise RuntimeError(f"Plotly.js CDN returned HTTP {status} for {PLOTLY_JS_URL}")
            raw = response.read(PLOTLY_JS_MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Plotly.js CDN request failed: HTTP {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Plotly.js CDN request failed: {exc.reason}") from exc
    except (OSError, http.client.HTTPException) as exc:
        raise RuntimeError(f"Plotly.js CDN request failed: {exc}") from exc
    return verify_plotly_js(raw)


def _plotly_initializer(div_id: str, spec_expression: str, config_expression: str) -> str:
    """Build the initializer from caller-serialized JS expressions."""
    identity = json.dumps(div_id, ensure_ascii=True).replace("<", "\\u003c")
    return (
        f'(function(){{var s={spec_expression};var el=document.getElementById({identity});'
        f'if(el&&window.Plotly){{window.Plotly.newPlot(el,s.data,s.layout,{config_expression});}}}})();'
    )
# END DRAgoWing Plotly runtime

PLOTLY_JS_CDN = PLOTLY_JS_URL
_PLOTLY_JS_CACHE: bytes | None = None


def reset_plotly_js_cache() -> None:
    """Clear the in-process embed cache (tests only)."""
    global _PLOTLY_JS_CACHE
    _PLOTLY_JS_CACHE = None


def _classic_script(source: str) -> str:
    if re.search(r"</script(?=[\s/>])", source, re.IGNORECASE):
        raise ValueError("script contains HTML script end tag")
    return "<script>%s</script>" % source


def fetch_plotly_js() -> str:
    """Fetch Plotly.js bytes from jsDelivr and cache successful responses only."""
    global _PLOTLY_JS_CACHE
    if _PLOTLY_JS_CACHE is None:
        raw = _fetch_plotly_bytes(timeout=60.0, user_agent="dragowing/plotly_cdn (Plotly embed)")
        _classic_script(raw.decode("utf-8"))
        _PLOTLY_JS_CACHE = raw
    return _PLOTLY_JS_CACHE.decode("utf-8")


def plotly_script_tags(*, embed: bool) -> str:
    config = "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
    if embed:
        return config + _classic_script(fetch_plotly_js())
    return (
        config
        + '<script src="%s" crossorigin="anonymous"></script>' % escape(PLOTLY_JS_CDN, quote=True)
    )


# ====================================================================================================
# 🧾 四つの形の 2×2 と条件の論理記号（旧 forms.py）
# 四つの形の 2×2 と、条件の論理記号。
#
# 数は propositions.jsonl / sets.jsonl の forms[].n と forms[].hold だけから数える。
# 判定はやり直さない。図の文は観測で、成立の理由は書かない。
#
#   python dragowing.py <結果フォルダ> --forms --id P1
# ====================================================================================================

FORM_ORDER = ("original", "converse", "inverse", "contrapositive")


def _sibling(module: str, project: str):
    """Aoi の兄弟（QueRyu の ask、PythDRagoras の propositions / rule_search）を import する。

    場所は呼び出し側が入れる（Aoi の aoi.py: ``python aoi.py dragowing/__main__.py``、``import aoi``、
    ``eval "$(python aoi.py)"``）。DRAgoWing は自分では探さない。
    """
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError as error:
        if error.name != module:
            raise
        raise ModuleNotFoundError(
            f"{module}（{project}）が見つからない。Aoi の aoi.py から動かす: python aoi.py dragowing/__main__.py RESULTS"
            f'（単独の checkout では先に eval "$(python <Aoi>/aoi.py)"）', name=module) from None


def registration_status(item: dict) -> str:
    """QueRyu ``ask`` (its path comes from the caller, e.g. Aoi's aoi.py)."""
    return _sibling("ask", "QueRyu").registration_status(item)

FORM_LABEL = {
    "original": "元 P→Q",
    "converse": "逆 Q→P",
    "inverse": "裏 ¬P→¬Q",
    "contrapositive": "対偶 ¬Q→¬P",
}


def _forms(item: dict) -> dict[str, dict]:
    return {f.get("form"): f for f in item.get("forms") or [] if isinstance(f, dict)}


def _counts(form: dict | None) -> tuple[int, int] | None:
    if not form:
        return None
    n, hold = form.get("n"), form.get("hold")
    if type(n) is not int or type(hold) is not int or n < 0 or hold < 0 or hold > n:
        return None
    return n, hold


def _agree(values: list[int]) -> int | str | None:
    if not values:
        return None
    if any(v != values[0] for v in values):
        return "不一致:" + "/".join(str(v) for v in values)
    return values[0]


def contingency(item: dict) -> dict[str, int | str | None]:
    """P∧Q, P∧¬Q, ¬P∧Q, ¬P∧¬Q from n and hold.

    Two forms that imply different counts stay as ``不一致`` rather than one of them being picked.
    An empty antecedent (no if and no if_any) makes the ¬P cells 0, because every unit is P.
    """
    forms = _forms(item)
    original, converse = _counts(forms.get("original")), _counts(forms.get("converse"))
    inverse, contra = _counts(forms.get("inverse")), _counts(forms.get("contrapositive"))
    pq, p_not_q, not_p_q, not_p_not_q = [], [], [], []
    if original:
        pq.append(original[1])
        p_not_q.append(original[0] - original[1])
    if converse:
        pq.append(converse[1])
        not_p_q.append(converse[0] - converse[1])
    if contra:
        not_p_not_q.append(contra[1])
        p_not_q.append(contra[0] - contra[1])
    if inverse:
        not_p_not_q.append(inverse[1])
        not_p_q.append(inverse[0] - inverse[1])
    empty_if = not item.get("if") and not item.get("if_any")
    if empty_if:
        not_p_q.append(0)
        not_p_not_q.append(0)
    return {
        "P∧Q": _agree(pq),
        "P∧¬Q": _agree(p_not_q),
        "¬P∧Q": _agree(not_p_q),
        "¬P∧¬Q": _agree(not_p_not_q),
    }


def _cell(value) -> str:
    if value is None:
        return "不明"
    return str(value)


def empty_antecedent(item: dict) -> bool:
    return not item.get("if") and not item.get("if_any")


def format_contingency_cell(item: dict, key: str) -> str:
    """2×2 のマス。空の前件で ¬P 行に置く 0 は注釈付き。"""
    value = contingency(item)[key]
    if empty_antecedent(item) and key in ("¬P∧Q", "¬P∧¬Q") and value == 0:
        return "0（前件が空）"
    return _cell(value)


COUNTEREXAMPLE_PAIR_LABELS = (
    ("original", "contrapositive"),
    ("converse", "inverse"),
)


def _form_cell(form: dict | None) -> str:
    counts = _counts(form)
    if counts is None:
        return "不明"
    n, hold = counts
    return f"{hold}/{n}（反例 {n - hold}）"


def _form_line(name: str, form: dict | None) -> str:
    text = f"{FORM_LABEL[name]}: {_form_cell(form)}"
    if isinstance(form, dict) and "rate" in form:
        text += " rate=" + json.dumps(form.get("rate"), ensure_ascii=False)
    return text


def render_forms_table(item: dict, *, heading: bool = True) -> str:
    """C1. Contingency 2×2, then the four forms as a 2×2. Both carry the registration label."""
    label = registration_status(item)
    forms = _forms(item)
    ident = item.get("id", "")
    lines = []
    if heading:
        lines.extend([f"［{label}］ {ident}", ""])
    lines.extend(
        [
            "|  | Q | ¬Q |",
            "|---|---|---|",
            f"| P | {format_contingency_cell(item, 'P∧Q')} | {format_contingency_cell(item, 'P∧¬Q')} |",
            f"| ¬P | {format_contingency_cell(item, '¬P∧Q')} | {format_contingency_cell(item, '¬P∧¬Q')} |",
            "",
            "|  |  |",
            "|---|---|",
            f"| {_form_line('original', forms.get('original'))} | {_form_line('converse', forms.get('converse'))} |",
            f"| {_form_line('inverse', forms.get('inverse'))} | {_form_line('contrapositive', forms.get('contrapositive'))} |",
        ]
    )
    return "\n".join(lines)


def counterexample_lists_equal(left, right) -> bool:
    """反例配列が同じ単位の並びか。記録の順をそのまま比べる。"""
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    a = left.get("counterexamples") or []
    b = right.get("counterexamples") or []
    if len(a) != len(b):
        return False
    return [row.get("unit") for row in a if isinstance(row, dict)] == [
        row.get("unit") for row in b if isinstance(row, dict)
    ]


def _value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _atom(cond: dict) -> str:
    return f"{cond['col']}{cond['op']}{_value(cond['value'])}"


def _and(conds: list, *, group: bool) -> str | None:
    if not conds:
        return None
    parts = [_atom(c) for c in conds]
    body = " ∧ ".join(parts)
    if group and len(parts) > 1:
        return f"({body})"
    return body


def antecedent(item: dict) -> str | None:
    parts = []
    if item.get("if"):
        text = _and(item["if"], group=False)
        if text:
            parts.append(text)
    groups = []
    for group in item.get("if_any") or []:
        text = _and(group, group=True)
        if text:
            groups.append(text)
    if len(groups) == 1:
        parts.append(groups[0])
    elif groups:
        parts.append("(" + " ∨ ".join(groups) + ")")
    if not parts:
        return None
    return " ∧ ".join(parts)


def consequent(item: dict) -> str | None:
    return _and(item.get("then") or [], group=False)


def _negate(expr: str) -> str:
    return f"¬({expr})"


def logic_lines(item: dict) -> list[str]:
    """C2. if / if_any / then as ∧ ∨ ¬ →. Empty antecedent stays 「条件なし」."""
    ant, cons = antecedent(item), consequent(item)
    if cons is None:
        return ["（then がない）"]
    if ant is None:
        return [
            f"元: ⊤（条件なし） → {cons}",
            f"逆: {cons} → ⊤（条件なし）（未評価）（if も if_any も空）",
            f"裏: ⊥（条件なしの否定） → ¬({cons})（未評価）（if も if_any も空）",
            f"対偶: ¬({cons}) → ⊥（条件なしの否定）",
        ]
    return [
        f"元: {ant} → {cons}",
        f"逆: {cons} → {ant}",
        f"裏: {_negate(ant)} → {_negate(cons)}",
        f"対偶: {_negate(cons)} → {_negate(ant)}",
    ]


def render_logic(item: dict) -> str:
    label = registration_status(item)
    body = "\n".join(logic_lines(item))
    return f"［{label}］ {item.get('id', '')}\n{body}"


def render_item(item: dict) -> str:
    return render_forms_table(item) + "\n\n" + render_logic(item)


def load_items(results: Path) -> tuple[list[dict], dict[str, bool]]:
    present, out = {}, []
    for name in ("propositions.jsonl", "sets.jsonl"):
        path = Path(results) / name
        present[name] = path.is_file()
        if present[name]:
            out += [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(present.values()):
        raise FileNotFoundError(f"結果が読めない: {results}")
    return out, present


def forms_text(results: Path, ident: str | None = None) -> str:
    """🧾 四つの形の 2×2 と条件の論理記号（文字だけ）。ident は P1 / E25 など、省略すると読み込んだ順に全部。"""
    items, present = load_items(results)
    if ident:
        needed = "sets.jsonl" if ident.startswith("E") else "propositions.jsonl" if ident.startswith("P") else None
        if needed and not present.get(needed):
            raise FileNotFoundError(f"結果が読めない: {needed}")
        items = [item for item in items if item.get("id") == ident]
        if not items:
            raise ValueError(f"{ident} は判定済みの結果にない")
    return "\n\n".join(render_item(item) for item in items)


def forms_main(argv=None) -> int:
    """``python dragowing.py RESULTS --forms [--id P1]`` と同じ。旧 ``python dragowing/forms.py --results … --id …``。"""
    parser = argparse.ArgumentParser(description="四つの形の 2×2 と条件の論理記号を出す")
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--id", help="この ID だけ。省略すると読み込んだ順")
    args = parser.parse_args(argv)
    try:
        print(forms_text(args.results, args.id))
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


# ====================================================================================================
# 🔀 重なりの行評価（標準ライブラリの経路）（旧 _overlap_stdlib.py）
# load_overlap 専用の行評価。numpy/polars の代用品や import の差し替えではない。
#
# Polars read_ndjson の先頭100行の型推論で結果が変わらない、同型のスカラー列だけ。
# 未対応の入力は native を明示的に選び直す。暗黙のフォールバックはしない。
# ====================================================================================================

_OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}


def read_rows(path: Path) -> list[dict]:
    """重複キーは標準 JSON decoder と NDJSON parser で解釈が違いうるので拒否。"""
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"stdlib overlap は重複キーを扱わない: {key}")
            obj[key] = value
        return obj

    return [json.loads(line, object_pairs_hook=unique)
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _kind(value):
    if value is None:
        return None
    if type(value) not in (bool, int, float, str):
        raise ValueError("stdlib overlap は bool/int/float/str/null の列だけ")
    if type(value) is str and any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError("stdlib overlap は Unicode surrogate を扱わない")
    if type(value) is int and not -(1 << 63) <= value < (1 << 63):
        raise ValueError("stdlib overlap の整数は Int64 の範囲だけ")
    if type(value) is float and not math.isfinite(value):
        raise ValueError("stdlib overlap は有限の数だけ")
    return type(value)


def _schema(rows):
    if not rows:
        raise ValueError("空の season.jsonl から型を推論できない")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("stdlib overlap は JSON オブジェクトの行だけ")
    schema = {}
    # native の既定 infer_schema_length=100 を越えて新しい列・型を受け入れない。
    for index, row in enumerate(rows):
        for col, value in row.items():
            if col not in schema:
                _kind(col)
            kind = _kind(value)
            if index < 100:
                kinds = schema.setdefault(col, set())
                if kind is not None:
                    kinds.add(kind)
            elif col not in schema or (kind is not None and kind not in schema[col]):
                raise ValueError(f"stdlib overlap の先頭100行以降で列・型が変わる: {col}")
    for col, kinds in schema.items():
        if not (len(kinds) <= 1 or kinds <= {int, float}):
            raise ValueError(f"stdlib overlap の列に異なる型がある: {col}")
    # native の team/season 順序確認が型変換で不一致にならない範囲。
    for row in rows:
        if type(row.get("team")) is not str or type(row.get("season")) is not int:
            raise ValueError("stdlib overlap は team が文字列、season が整数の行だけ")
    return schema


def condition_bits(rows: list[dict], conds: list[dict]) -> list[list[bool]]:
    """null / 欠損セルとの比較は全演算子で偽（!= null も偽）。"""
    schema = _schema(rows)
    bits = []
    for cond in conds:
        col, op, value = cond["col"], cond["op"], cond["value"]
        if col not in schema:
            raise ValueError(f"存在しない列: {col}（黙って偽にはしない）")
        if op not in _OPS:
            raise ValueError(f"演算子が条件にない: {op}")
        literal = _kind(value)
        kinds = schema[col]
        if literal is not None and kinds and not (
            kinds <= {int, float} and literal in (int, float)
            or kinds == {bool} and literal is bool
            or kinds == {str} and literal is str
        ):
            raise ValueError(f"stdlib overlap は比較の型変換を扱わない: {col}")
        floating = float in kinds or literal is float
        values = [row.get(col) for row in rows]
        if floating:
            # Float64 に丸めた巨大整数の境界は限定経路では扱わない。
            if any(type(v) is int and abs(v) > 2**53 for v in [value, *values]):
                raise ValueError("stdlib overlap の浮動小数比較は整数の絶対値が 2**53 以下だけ")
            values = [float(v) if v is not None else None for v in values]
            value = float(value) if value is not None else None
        compare = _OPS[op]
        bits.append([False if v is None or value is None else compare(v, value) for v in values])
    return bits


# ====================================================================================================
# 🔀 条件集合と B クラスの重なり（旧 overlap.py）
# 条件集合と B クラスの重なり。マスクは rule_search のビット行列。
#
# 空の比較（JSON の null）は真に数えない。rule_search._mask と同じである。
# 件数は bool 行列の和で、丸めない。
# ====================================================================================================

OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}


B_COND = {"col": "upper_half", "op": "==", "value": False}
# 領域は 2^n 個。8 個で 256 領域（格子 16×16）が、図で読める上限。計算はもっと多くても動く。
MAX_SETS = 8


def _check_count(conds: list[dict]) -> None:
    if not 2 <= len(conds) <= MAX_SETS:
        raise ValueError(f"条件集合は 2 個から {MAX_SETS} 個にする（B クラスを含む）。受け取った数: {len(conds)}")


def _engines():
    # PythDRagoras の propositions と rule_search。場所は呼び出し側（Aoi の aoi.py）が入れる
    propositions = _sibling("propositions", "PythDRagoras")
    rule_search = _sibling("rule_search", "PythDRagoras")
    return rule_search, propositions


def is_b(cond: dict) -> bool:
    return cond.get("col") == "upper_half" and cond.get("op") == "==" and cond.get("value") is False


def label_of(cond: dict) -> str:
    if is_b(cond):
        return "B (upper_half==false)"
    return _atom(cond)


def _key(cond: dict) -> tuple:
    return (cond["col"], cond["op"], json.dumps(cond["value"], ensure_ascii=False, sort_keys=True))


def parse_cond(text: str) -> dict:
    try:
        col, op, raw = text.split(",", 2)
    except ValueError:
        raise ValueError(f"条件の書き方は col,op,値（JSON）。例: rd,>,0 。受け取ったもの: {text}") from None
    if op not in OPS:
        raise ValueError(f"演算子が条件にない: {op}")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"値は JSON: {text}") from exc
    return {"col": col, "op": op, "value": value}


def default_conditions(items: list[dict], rows: list[dict]) -> list[dict]:
    """propositions の if をファイル順に見て、列がある原子を 2 個まで。最後に B クラスを足す。"""
    have = set(rows[0]) if rows else set()
    chosen: list[dict] = []
    seen = set()
    for item in items:
        for cond in item.get("if") or []:
            if not isinstance(cond, dict) or cond.get("col") not in have or cond.get("op") not in OPS:
                continue
            if "value" not in cond:
                continue
            key = _key(cond)
            if key in seen:
                continue
            seen.add(key)
            chosen.append({"col": cond["col"], "op": cond["op"], "value": cond["value"]})
            if len(chosen) == 2:
                break
        if len(chosen) == 2:
            break
    if not any(is_b(cond) for cond in chosen):
        if "upper_half" not in have:
            raise ValueError("upper_half が season.jsonl にない")
        chosen.append(dict(B_COND))
    _check_count(chosen)
    return chosen


def finalize_conditions(user: list[dict] | None, items: list[dict], rows: list[dict]) -> list[dict]:
    if not user:
        return default_conditions(items, rows)
    chosen = [{"col": c["col"], "op": c["op"], "value": c["value"]} for c in user]
    if not any(is_b(cond) for cond in chosen):
        if not rows or "upper_half" not in rows[0]:
            raise ValueError("upper_half が season.jsonl にない")
        chosen.append(dict(B_COND))
    _check_count(chosen)
    return chosen


def _patterns(n_sets: int):
    for bits in range(2**n_sets):
        yield tuple(bool(bits & (1 << i)) for i in range(n_sets))


def _overlap_region(pattern: tuple, labeled: list[dict], indexes: list[int]) -> dict:
    name = "外" if not any(pattern) else " ∧ ".join(
        labeled[i]["label"] if on else f"¬({labeled[i]['label']})" for i, on in enumerate(pattern)
    )
    return {"name": name, "bits": list(pattern), "count": len(indexes), "unit_index": indexes}


def _overlap_result(rows: list[dict], labeled: list[dict], bits: list[list[bool]], regions: list[dict]) -> dict:
    columns = []
    for cond in labeled:
        if cond["col"] not in columns:
            columns.append(cond["col"])
    if "upper_half" not in columns:
        columns.append("upper_half")
    units = []
    for index, row in enumerate(rows):
        units.append(
            {
                "index": index,
                "unit": f"{row['team']}-{row['season']}",
                "league": row["league"],
                "team": row["team"],
                "team_name": row["team_name"],
                "season": row["season"],
                "upper_half": row["upper_half"],
                "in_set": [bits[i][index] for i in range(len(labeled))],
                "values": {col: row.get(col) for col in columns},
            }
        )
    if sum(region["count"] for region in regions) != len(rows):
        raise ValueError("領域の件数の和が行数と合わない")
    return {"conditions": labeled, "columns": columns, "units": units, "regions": regions, "matrix": bits}


def load_overlap(path: Path, conds: list[dict], *, backend: str = "stdlib") -> dict:
    """条件行列と領域の件数。既定は標準ライブラリの経路（限定の入力、docs/overlap-stdlib.md）。

    backend="native" は α の overlap.py（numpy・polars と PythDRagoras の rule_search、dev グループ）に渡す。
    ``dragowing.overlap.load_overlap`` は今までどおり native が既定。
    """
    if backend == "native":
        return _alpha("overlap").load_overlap(path, conds, backend="native")
    if backend != "stdlib":
        raise ValueError(f"overlap backend は native か stdlib: {backend}")
    path = Path(path)
    labeled = [{**cond, "label": label_of(cond)} for cond in conds]
    rows = read_rows(path)
    bits = condition_bits(rows, labeled)
    regions = [
        _overlap_region(pattern, labeled, [j for j in range(len(rows)) if all(bits[i][j] == on for i, on in enumerate(pattern))])
        for pattern in _patterns(len(labeled))
    ]
    return _overlap_result(rows, labeled, bits, regions)


# ====================================================================================================
# 📈 図の JSON（軌跡・球団×年）、📊 FFSS の図、🖼️ SVG（plotly_min）（旧 figures.py）
# 記録された値の Plotly 図 JSON（data / layout）。あてはめ、平滑化、階級への丸めはしない。
# ====================================================================================================

A_COLOR = "#1f77b4"
B_COLOR = "#d62728"
LINE_COLOR = "#9aa0a6"
# 図とページで共通。メイリオが無い環境（Mac・iPhone・Linux）では OS 既定の sans-serif になる。
# メイリオは再配布できないので、フォントファイルは同梱しない。
FONT = "Meiryo, メイリオ, sans-serif"

# Plotly の Viridis を ``to_dict()`` したときと同じ段。
_VIRIDIS_SCALE = [
    [0.0, "#440154"],
    [0.1111111111111111, "#482878"],
    [0.2222222222222222, "#3e4989"],
    [0.3333333333333333, "#31688e"],
    [0.4444444444444444, "#26828e"],
    [0.5555555555555556, "#1f9e89"],
    [0.6666666666666666, "#35b779"],
    [0.7777777777777778, "#6ece58"],
    [0.8888888888888888, "#b5de2b"],
    [1.0, "#fde725"],
]


def class_mark(upper) -> tuple[str, str]:
    """upper_half の true/false を A/B と色にする。null は B にしない。"""
    if upper is True:
        return A_COLOR, "A"
    if upper is False:
        return B_COLOR, "B"
    return "#888888", ""


def _base_layout(**extra):
    layout = dict(
        template={},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family=FONT, size=13, color="#1a1a1a"),
        margin=dict(l=60, r=30, t=88, b=50),
    )
    layout.update(extra)
    return layout


def _team_label(league: str, team_name: str, team: str) -> str:
    return f"{league} {team_name} ({team})"


def _subplot_domains(ncols: int, spacing: float = 0.08) -> list[tuple[float, float]]:
    if ncols < 1:
        raise ValueError("ncols")
    width = (1.0 - spacing * (ncols - 1)) / ncols
    return [(index * (width + spacing), index * (width + spacing) + width) for index in range(ncols)]


def _axis_names(col_index: int) -> tuple[str, str]:
    """1-based column index → trace xaxis/yaxis refs and layout axis keys."""
    if col_index == 1:
        return "x", "y"
    suffix = str(col_index)
    return f"x{suffix}", f"y{suffix}"


def _layout_axis_key(axis_ref: str) -> str:
    """trace の軸の名前 → layout のキー: x → xaxis、x2 → xaxis2（plotly.js が読むのはこの形。x2axis は読まれない）。"""
    return f"{axis_ref[0]}axis{axis_ref[1:]}"


def trajectory_figure(rows: list[dict]) -> dict:
    """C3. 得点順位 × 失点順位。点の色は upper_half。線は記録の順をつなぐだけ。"""
    for key in ("league", "team", "team_name", "season", "rank_rf", "rank_ra", "upper_half"):
        if rows and key not in rows[0]:
            raise ValueError(f"列がない: {key}")
    grouped: dict[tuple, list] = {}
    for index, row in enumerate(rows):
        if row.get("rank_rf") is None or row.get("rank_ra") is None:
            continue
        grouped.setdefault((row["league"], row["team"]), []).append((row["season"], index, row))
    leagues = sorted({league for league, _ in grouped})
    if not leagues:
        raise ValueError("軌跡にする行がない")
    domains = _subplot_domains(len(leagues))
    traces: list[dict] = []
    points = []
    layout = _base_layout(
        title=dict(
            text="得点順位 rank_rf × 失点順位 rank_ra<br>点の色: A は upper_half==true、B は upper_half==false<br>線は同じ league・team の記録を season の昇順につないだもの"
        ),
        height=640,
        width=1040,
        legend=dict(font=dict(size=11)),
        meta={"kind": "trajectory", "source": "season.jsonl", "points": points},
    )
    annotations = []
    for col, league in enumerate(leagues, start=1):
        x_ref, y_ref = _axis_names(col)
        x_key = _layout_axis_key(x_ref)
        y_key = _layout_axis_key(y_ref)
        lo, hi = domains[col - 1]
        layout[x_key] = dict(
            anchor=y_ref,
            domain=[lo, hi],
            title=dict(text="得点順位 rank_rf"),
            dtick=1,
        )
        layout[y_key] = dict(
            anchor=x_ref,
            domain=[0.0, 1.0],
            title=dict(text="失点順位 rank_ra"),
            dtick=1,
            scaleanchor=x_ref,
            scaleratio=1,
        )
        annotations.append(
            dict(
                font=dict(size=16),
                showarrow=False,
                text=f"league={league}",
                x=(lo + hi) / 2,
                xanchor="center",
                xref="paper",
                y=1.0,
                yanchor="bottom",
                yref="paper",
            )
        )
        teams = sorted(team for lg, team in grouped if lg == league)
        for team in teams:
            series = sorted(grouped[(league, team)], key=lambda item: (item[0], item[1]))
            team_name = series[0][2]["team_name"]
            custom, colors, xs, ys = [], [], [], []
            for season, _index, row in series:
                color, klass = class_mark(row.get("upper_half"))
                xs.append(row["rank_rf"])
                ys.append(row["rank_ra"])
                colors.append(color)
                custom.append(
                    {
                        "season": row["season"],
                        "league": row["league"],
                        "team": row["team"],
                        "team_name": row["team_name"],
                        "rank_rf": row["rank_rf"],
                        "rank_ra": row["rank_ra"],
                        "upper_half": row["upper_half"],
                        "class": klass,
                    }
                )
                points.append(custom[-1])
            trace = dict(
                type="scatter",
                x=xs,
                y=ys,
                mode="lines+markers",
                name=_team_label(league, team_name, team),
                line=dict(color=LINE_COLOR, width=1, shape="linear"),
                marker=dict(color=colors, size=10, line=dict(width=0)),
                customdata=custom,
                connectgaps=False,
                hovertemplate=(
                    "season=%{customdata.season}<br>"
                    "league=%{customdata.league} %{customdata.team_name} (%{customdata.team})<br>"
                    "rank_rf=%{customdata.rank_rf}<br>"
                    "rank_ra=%{customdata.rank_ra}<br>"
                    "upper_half=%{customdata.upper_half}<br>"
                    "class=%{customdata.class}<extra></extra>"
                ),
                meta={"role": "trajectory", "league": league, "team": team, "team_name": team_name},
            )
            trace["xaxis"] = x_ref
            trace["yaxis"] = y_ref
            traces.append(trace)
    layout["annotations"] = annotations
    traces.extend(
        [
            dict(
                type="scatter",
                x=[],
                y=[],
                mode="markers",
                marker=dict(color=A_COLOR, size=10),
                name="A (upper_half==true)",
                meta={"role": "legend"},
            ),
            dict(
                type="scatter",
                x=[],
                y=[],
                mode="markers",
                marker=dict(color=B_COLOR, size=10),
                name="B (upper_half==false)",
                meta={"role": "legend"},
            ),
        ]
    )
    return {"data": traces, "layout": layout}


def _numeric_column(rows: list[dict], column: str) -> None:
    if not rows or column not in rows[0]:
        raise ValueError(f"列がない: {column}")
    for row in rows:
        value = row.get(column)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"列 {column} は数値ではない")


def _exact_text(value) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def _heatmap_order(teams: list[tuple], team_order=()) -> list[tuple]:
    """``team_order`` の記号を上から順に。載っていない球団はその下に記号順で並べる。"""
    rank = {code: index for index, code in enumerate(team_order)}

    def key(item):
        code = item[1]
        if code in rank:
            return (0, rank[code], item[0])
        return (1, code, item[0])

    return sorted(teams, key=key)


def heatmap_figure(rows: list[dict], column: str = "wins_vs_pythag", team_order=()) -> dict:
    """C4. 球団 × 年。色は列の値。マスの文字は A/B だけ。数はホバー。

    ``team_order`` は上から並べる球団の記号（呼び出し側の設定。省略すると記号順）。
    """
    _numeric_column(rows, column)
    teams = _heatmap_order(list({(row["league"], row["team"], row["team_name"]) for row in rows}), team_order)
    seasons = sorted({row["season"] for row in rows})
    index = {(row["league"], row["team"], row["season"]): row for row in rows}
    codes = [team for _league, team, _name in teams]
    clash = len(codes) != len(set(codes))
    labels = [f"{league}:{team}" if clash else team for league, team, _name in teams]
    z, text, marks, records, custom = [], [], [], [], []
    for (league, team, name), label in zip(teams, labels):
        z_row, text_row, mark_row, custom_row = [], [], [], []
        for season in seasons:
            row = index.get((league, team, season))
            if row is None:
                value, upper, rank = None, None, None
            else:
                value, upper = row.get(column), row.get("upper_half")
                rank = row.get("rank") if "rank" in row else None
            _color, klass = class_mark(upper)
            z_row.append(value)
            text_row.append(klass)
            mark_row.append(klass)
            custom_row.append(
                {
                    "league": league,
                    "team": team,
                    "team_name": name,
                    "season": season,
                    "class": klass,
                    "rank": rank,
                    "rank_text": _exact_text(rank),
                    "value": value,
                    "value_text": _exact_text(value),
                }
            )
            records.append(custom_row[-1] | {"column": column, "upper_half": upper, "mark": klass})
        z.append(z_row)
        text.append(text_row)
        marks.append(mark_row)
        custom.append(custom_row)
    finite = [value for row in z for value in row if isinstance(value, (int, float))]
    zmin = min(finite) if finite else None
    zmax = max(finite) if finite else None
    layout = _base_layout(
        title=dict(text="球団 × 年"),
        height=640,
        width=980,
        meta={
            "kind": "heatmap",
            "source": "season.jsonl",
            "column": column,
            "x": seasons,
            "y": labels,
            "z": z,
            "marks": marks,
            "records": records,
        },
        xaxis=dict(type="category", title=dict(text="season"), automargin=True),
        yaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=list(reversed(labels)),
            title=dict(text="team"),
            automargin=True,
        ),
    )
    trace = dict(
        type="heatmap",
        x=seasons,
        y=labels,
        z=z,
        text=text,
        texttemplate="%{text}",
        textfont=dict(family=FONT, size=14, color="#1a1a1a"),
        customdata=custom,
        colorscale=_VIRIDIS_SCALE,
        zmin=zmin,
        zmax=zmax,
        zsmooth=False,
        hoverongaps=False,
        showlegend=False,
        colorbar=dict(title=dict(text=column)),
        hovertemplate=(
            "team=%{customdata.team} %{customdata.team_name}<br>"
            "season=%{customdata.season}<br>"
            "class=%{customdata.class}<br>"
            "rank=%{customdata.rank_text}<br>"
            f"{column}=%{{customdata.value_text}}<extra></extra>"
        ),
    )
    return {"data": [trace], "layout": layout}


# FFSS experiment records: values are plotted without re-running the experiments.
# (F<NN> identifier, the FFSS (experiment, run) rows it reads). The order is the F number.
FFSS_FIGURES = (("energy-coal", (("E31", "energy:coal"),)), ("energy-gtcc", (("E31", "energy:lng"),)),
                ("losses", (("E31", "energy:coal"), ("E31", "energy:lng"))), ("pinch-tq", (("E31", "tq"),)),
                ("balance-point", (("E32", "balance"),)), ("startup", (("E31", "startup"),)),
                ("sensitivity", (("E31", "sensitivity"),)), ("rate-window", (("E31", "rate-window"),)),
                ("blood-flow", (("E30", "blood"),)))
_COLORS = {"heat": "#FFA15A", "water": "#19d3f3", "power": "#00cc96", "loss": "#9aa0a6", "heart": "#EF553B",
           "organ": "#FF6692", "vein": "#636efa", "lung": "#ab63fa"}
_PLANT = {"coal": "🪨", "lng": "🌀"}


def _rgba(color: str, alpha: float) -> str:
    h = color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha:g})"


def _fig(title: str, data: list, **layout) -> dict:
    """720×448 px（8 の倍数）、余白も 8 の倍数。文字は plotly_min の既定（メイリオ）。"""
    layout = {"title": {"text": title}, "width": 720, "height": 448,
              "margin": layout.pop("margin", {"l": 72, "r": 32, "t": 64, "b": 64}), **layout}
    return {"data": data, "layout": layout}


def _sankey(title: str, rows: list[dict]) -> dict:
    """リンクの行（source・target・組・value・unit）からサンキー図。ノードは出てきた順、ラベルは 名前 + 入りと出の大きい方。"""
    names: dict[str, str] = {}
    for r in rows:
        names.setdefault(r["source"], r["source_group"])
        names.setdefault(r["target"], r["target_group"])
    order = list(names)
    size = {n: max(sum(r["value"] for r in rows if r["source"] == n), sum(r["value"] for r in rows if r["target"] == n))
            for n in order}
    return _fig(title, [{"type": "sankey",  # 単位（% ・L/min）は題に書く
                         "node": {"label": [f"{n} {size[n]:.1f}" for n in order],
                                  "color": [_COLORS[names[n]] for n in order], "pad": 16, "thickness": 16},
                         "link": {"source": [order.index(r["source"]) for r in rows],
                                  "target": [order.index(r["target"]) for r in rows],
                                  "value": [r["value"] for r in rows],
                                  "color": [_rgba(_COLORS[r["target_group"]], 0.35) for r in rows]}}],
                margin={"l": 16, "r": 16, "t": 64, "b": 24})


def _losses(coal: list[dict], lng: list[dict]) -> dict:
    data = []
    for icon, rows in (("🪨", coal), ("🌀", lng)):
        loss = [r for r in rows if r["target_group"] == "loss"]
        grid = next(r["value"] for r in rows if r["target"] == "送電端")
        steps = [100.0, *(-r["value"] for r in loss), grid]
        data.append({"type": "waterfall", "name": icon, "x": [f"{icon} {n}" for n in ("燃料", *(r["target"] for r in loss), "送電端")],
                     "y": steps, "measure": ["absolute", *["relative"] * len(loss), "total"],
                     "text": [f"{abs(v):.1f}" for v in steps]})
    return _fig("🪜 燃料 100 から送電端まで（損を順に引く）", data, showlegend=False, yaxis={"title": {"text": "燃料 100 に対する割合"}, "range": [0, 112]},
                xaxis={"tickangle": -30}, margin={"l": 72, "r": 32, "t": 64, "b": 104})


def _pinch(rows: list[dict]) -> dict:
    gas = [r for r in rows if r["stream"] == "gas"]
    water = [r for r in rows if r["stream"] == "water"]
    fig = _fig("🌡️ 🌀 排熱回収ボイラの T–Q 線図（3 圧・再熱）", [
        {"type": "scatter", "mode": "lines", "name": "ガス（GT の排気）", "x": [r["q_mw"] for r in gas],
         "y": [r["t_c"] for r in gas], "line": {"color": "#EF553B", "width": 3}},
        {"type": "scatter", "mode": "lines", "name": "水・蒸気（3 圧の合成）", "x": [r["q_mw"] for r in water],
         "y": [r["t_c"] for r in water], "line": {"color": "#636efa", "width": 3}}],
        xaxis={"title": {"text": "煙突の側から渡した熱 [MW]"}}, yaxis={"title": {"text": "温度 [°C]"}, "range": [0, 650]})
    names = {"lp": "低圧", "ip": "中圧", "hp": "高圧"}
    for r in (r for r in rows if r["stream"] == "pinch"):
        fig["layout"].setdefault("shapes", []).append({"type": "line", "x0": r["q_mw"], "x1": r["q_mw"], "y0": r["t_c"],
                                                       "y1": r["t_gas_c"], "line": {"color": "#444", "width": 1, "dash": "dot"}})
        fig["layout"].setdefault("annotations", []).append({"x": r["q_mw"], "y": r["t_gas_c"] + 28, "showarrow": False,
                                                            "text": f"{names[r['drum']]} ΔT {r['dt_k']:.1f} K"})
    return fig


def _balance(rows: list[dict]) -> dict:
    curve = [r for r in rows if r["kind"] == "curve"]
    cat = [r for r in rows if r["kind"] == "catalog"]
    bal = next(r["t_out"] for r in rows if r["kind"] == "balance" and not r["iso"])
    ts = [r["t_out"] for r in curve]
    fig = _fig("✖️ 🏠 最大暖房出力と家の暖房負荷（交点 = バランス点）", [
        {"type": "scatter", "mode": "lines", "name": "最大暖房出力（× 除霜）", "x": ts, "y": [r["max_kw"] for r in curve],
         "line": {"color": "#EF553B", "width": 3}},
        {"type": "scatter", "mode": "lines", "name": "家の負荷（JIS）", "x": ts, "y": [r["load_jis_kw"] for r in curve],
         "line": {"color": "#636efa"}},
        {"type": "scatter", "mode": "lines", "name": "家の負荷（ISO 16358-2）", "x": ts, "y": [r["load_iso_kw"] for r in curve],
         "line": {"color": "#636efa", "dash": "dash"}},
        {"type": "scatter", "mode": "markers", "name": "カタログの低温の最大能力", "x": [r["t_out"] for r in cat],
         "y": [r["max_kw"] for r in cat], "marker": {"color": "#444", "size": 10, "symbol": "diamond"}}],
        xaxis={"title": {"text": "外気 [°C]"}}, yaxis={"title": {"text": "暖房 [kW]"}, "range": [0, 10]})
    fig["layout"]["shapes"] = [{"type": "line", "x0": bal, "x1": bal, "xref": "x", "y0": 0, "y1": 1, "yref": "y domain",
                                "line": {"color": "#444", "width": 1, "dash": "dot"}}]
    fig["layout"]["annotations"] = [{"x": bal, "y": 9.3, "showarrow": False, "xanchor": "left",
                                     "text": f"バランス点 {bal:.1f} °C".replace("-", "−")}]
    return fig


def _startup(rows: list[dict]) -> dict:
    keys = [(p, s) for p in ("lng", "coal") for s in ("cold", "hot")]
    labels = [f"{_PLANT[p]} {s}" for p, s in keys]
    phase = {(r["plant"], r["start"], r["phase"]): r for r in rows}
    names = {"steps": ("手順", _COLORS["loss"]), "warmup": ("🧱 暖機", "#EF553B"), "ramp": ("負荷上げ", _COLORS["power"])}
    data = [{"type": "bar", "orientation": "h", "name": name, "y": labels, "marker": {"color": color},
             "base": [phase[(p, s, k)]["from_min"] for p, s in keys],
             "x": [phase[(p, s, k)]["to_min"] - phase[(p, s, k)]["from_min"] for p, s in keys]}
            for k, (name, color) in names.items()]
    for i, (p, s) in enumerate(keys):
        r = phase[(p, s, "steps")]
        data.append({"type": "scatter", "mode": "markers", "name": "Agora の起動時間（並列まで）", "showlegend": i == 0,
                     "x": [r["agora_lo_min"], r["agora_hi_min"]], "y": [labels[i]] * 2,
                     "marker": {"color": "#444", "size": 10, "symbol": "diamond"}})
    at = rows[0]["at"] if rows else 0.5
    return _fig(f"📅 🌅 起動の手順と時間（出典の範囲の at = {at:g}）", data, barmode="overlay",
                xaxis={"title": {"text": "止めてからの時間 [分]"}})


def _assumption(r: dict) -> str:
    icon, name = {"pinch": ("📍", "pinch"), "metal-rate": ("🧱", "温め直し"), "metal-tau": ("🧱", "τ"),
                  "compressor-eta": ("🫧", "圧縮機の効率"), "boiler": ("🪨", "ボイラ")}.get(r["assumption"], ("🎚️", r["assumption"]))
    lo, hi, unit = r["lo"], r["hi"], r["unit"]
    span = f"{lo * 100:g}〜{hi * 100:g} %" if r["assumption"] == "boiler" else f"{lo:g}〜{hi:g}" + (f" {unit}" if unit else "")
    return f"{icon} {name} {span}" + ("" if r["source_range"] else "（幅は仮）")


def _tornado(rows: list[dict]) -> dict:
    spans: dict[str, list[dict]] = {}
    for r in rows:
        spans.setdefault(r["assumption"], []).append(r)
    items = sorted(spans.values(), key=lambda v: max(r["metric"] for r in v) - min(r["metric"] for r in v))
    names = [_assumption(v[0]) for v in items]
    lo = [min(r["metric"] for r in v if not r["use"]) for v in items]
    hi = [max(r["metric"] for r in v if not r["use"]) for v in items]
    use = [next(r["metric"] for r in v if r["use"]) for v in items]
    fig = _fig("🌪️ 🎚️ 仮定を振ったときの 🔮 のずれ（1 を超えると外れる）", [
        {"type": "bar", "orientation": "h", "name": "幅の中", "y": names, "base": lo, "x": [b - a for a, b in zip(lo, hi)],
         "marker": {"color": [_COLORS["power"] if b <= 1.0 else _COLORS["heat"] for b in hi]}},
        {"type": "scatter", "mode": "markers", "name": "使った値", "x": use, "y": names,
         "marker": {"color": "#444", "size": 10, "symbol": "diamond"}}],
        xaxis={"title": {"text": "ずれ ÷ 許容"}}, showlegend=False, margin={"l": 216, "r": 32, "t": 64, "b": 64})
    fig["layout"]["shapes"] = [{"type": "line", "x0": 1.0, "x1": 1.0, "xref": "x", "y0": 0, "y1": 1, "yref": "y domain",
                                "line": {"color": "#EF553B", "width": 2, "dash": "dash"}}]
    return fig


def _window(rows: list[dict], use: tuple[float, float] | None = None) -> dict:
    rates = sorted({r["rate_k_min"] for r in rows})
    taus = sorted({r["tau_h"] for r in rows})
    z = {(r["tau_h"], r["rate_k_min"]): r["metric"] for r in rows}
    if len(z) != len(rows) or len(z) != len(rates) * len(taus):
        raise ValueError("rate-window must be a complete grid without duplicate coordinates")
    return _fig("🧱 cold の起動が Agora の範囲に入る窓（1 以下 = 中）", [
        {"type": "heatmap", "x": rates, "y": taus, "z": [[z[(t, x)] for x in rates] for t in taus], "zmin": 0.0, "zmax": 3.0,
         "colorbar": {"title": {"text": "ずれ ÷ 半幅"}},
         "colorscale": [[0.0, "#2166ac"], [1 / 3, "#f7f7f7"], [1.0, "#b2182b"]]}] + ([
        {"type": "scatter", "mode": "markers", "name": "使った値", "x": [use[0]], "y": [use[1]],
         "marker": {"color": "#444", "size": 12, "symbol": "diamond"}}] if use is not None else []),
        xaxis={"title": {"text": "温め直しの速さ [K/min]"}}, yaxis={"title": {"text": "τ [h]"}}, showlegend=False,
        margin={"l": 72, "r": 96, "t": 64, "b": 64})


def ffss_figures(records: dict[tuple[str, str], list[dict]]) -> dict[str, dict]:
    """F<NN>_<識別子> → plotly の図 JSON（data・layout）。記録の値を並べるだけで、判定はやり直さない。"""
    get = records.get
    # The grid itself does not record a chosen point. Use the sensitivity
    # records when supplied, and omit that marker when they are absent.
    used = {r["assumption"]: r["x"] for r in get(("E31", "sensitivity"), []) if r.get("use")}
    point = (used["metal-rate"], used["metal-tau"]) if {"metal-rate", "metal-tau"} <= used.keys() else None
    build = {"energy-coal": lambda: _sankey("🔀 🪨 石炭火力（USC）: 燃料 100 の行き先（1 段目の割合）", get(("E31", "energy:coal"))),
             "energy-gtcc": lambda: _sankey("🔀 🌀 LNG 複合（GTCC）: 燃料 100 の行き先（1 段目の割合）", get(("E31", "energy:lng"))),
             "losses": lambda: _losses(get(("E31", "energy:coal")), get(("E31", "energy:lng"))),
             "pinch-tq": lambda: _pinch(get(("E31", "tq"))), "balance-point": lambda: _balance(get(("E32", "balance"))),
             "startup": lambda: _startup(get(("E31", "startup"))), "sensitivity": lambda: _tornado(get(("E31", "sensitivity"))),
             "rate-window": lambda: _window(get(("E31", "rate-window")), point),
             "blood-flow": lambda: _sankey("🔀 🫀 心拍出量の行き先（L/min）", get(("E30", "blood")))}
    out = {}
    for n, (name, needs) in enumerate(FFSS_FIGURES, 1):
        if all(records.get(k) for k in needs):  # 記録に無い図は描かない（run E31 だけの記録でもよい）
            try:
                for key in needs:
                    for row in records[key]:
                        if any(isinstance(v, float) and not math.isfinite(v) for v in row.values()):
                            raise ValueError("numeric fields must be finite")
                out[f"F{n:02d}_{name}"] = build[name]()
            except (KeyError, StopIteration, TypeError, ValueError) as exc:
                raise ValueError(f"FFSS F{n:02d}_{name}: incomplete or invalid records ({exc})") from exc
    return out


# --- 🖼️ 図の JSON → SVG（親の plotly_min、Chrome なし） -----------------------------------------------

@lru_cache(maxsize=1)
def plotly_min():
    """vendor/tools/stdlib_min/plotly_min.py（親の stdlib_min を vendor.lock.json で固定）。名前は子どうしでぶつからないように。"""
    path = Path(__file__).resolve().parent / "vendor" / "tools" / "stdlib_min" / "plotly_min.py"
    if not path.is_file():
        raise FileNotFoundError(f"plotly_min が無い: {path}（DRAgoWing のリポジトリから動かす）")
    spec = importlib.util.spec_from_file_location("dragowing_plotly_min", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def series_figure(x, y, *, name="", title="", x_title="", y_title="", mode="lines+markers") -> dict:
    """📈 分野を問わない系列の図。順序と欠け（None）をそのまま残す（connectgaps=False）。旧 Aoi の plot_specs。"""
    x, y = list(x), list(y)
    if len(x) != len(y):
        raise ValueError("aligned x and y required")
    if mode not in ("lines", "markers", "lines+markers"):
        raise ValueError("unsupported mode")
    spec = {"data": [{"type": "scatter", "x": deepcopy(x), "y": deepcopy(y),
                      "name": name, "mode": mode, "connectgaps": False}],
            "layout": {"template": {}, "font": {"family": FONT}, "title": {"text": title},
                       "xaxis": {"title": {"text": x_title}},
                       "yaxis": {"title": {"text": y_title}}}}
    json.dumps(spec, allow_nan=False)
    return spec


def matrix_figure(x, y, z, *, title="", x_title="", y_title="") -> dict:
    """🟦 分野を問わない行列の図（ヒートマップ）。ラベルの順と欠けを残し、呼び出し側のデータは写す。旧 Aoi の plot_specs。"""
    x, y, z = list(x), list(y), [list(row) for row in z]
    if len(z) != len(y) or any(len(row) != len(x) for row in z):
        raise ValueError("matrix shape must match axis labels")
    spec = {"data": [{"type": "heatmap", "x": deepcopy(x), "y": deepcopy(y),
                      "z": deepcopy(z), "zsmooth": False, "hoverongaps": False}],
            "layout": {"template": {}, "font": {"family": FONT}, "title": {"text": title},
                       "xaxis": {"type": "category", "title": {"text": x_title}},
                       "yaxis": {"type": "category", "categoryorder": "array",
                                 "categoryarray": deepcopy(y), "title": {"text": y_title}}}}
    json.dumps(spec, allow_nan=False)
    return spec


def figure_svg(spec: dict) -> bytes:
    """🖼️ 図の JSON を SVG に。野球の図（サブプロット・積み上げ・マスの文字）も FFSS の図も同じ道。"""
    return plotly_min().Figure(spec).to_image("svg")


def write_ffss(records_path, out_dir, *, svg: bool = True) -> list[Path]:
    """📊 FFSS の記録から ffss.html（plotly.js）と svg/F<NN>_<識別子>.svg（plotly_min、Chrome なし）を書く。"""

    pm = plotly_min()
    figs = ffss_figures(read_ffss(records_path))
    if not figs:
        raise ValueError("FFSS の図にする記録が無い（run E30・E31・E32 か verify の --jsonl）")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blocks = "".join(f'<section><h2>{escape(name)}</h2>{pm.Figure(spec).to_html(include_plotlyjs=False, full_html=False, div_id=name)}</section>'
                     for name, spec in figs.items())
    page = (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>📊 FFSS の図</title>'
            f'<script src="https://cdn.plot.ly/plotly-{pm.PLOTLY_JS}.min.js" charset="utf-8"></script>'
            f'<style>body{{font-family:{pm.FONT};margin:16px}}h2{{font-size:16px}}</style></head>'
            f'<body><h1>📊 FFSS の図（記録から）</h1>{blocks}</body></html>\n')
    written = [out / "ffss.html"]
    written[0].write_text(page, encoding="utf-8")
    if svg:
        (out / "svg").mkdir(exist_ok=True)
        for name, spec in figs.items():
            path = out / "svg" / f"{name}.svg"
            path.write_bytes(figure_svg(spec))
            written.append(path)
    return written


# ====================================================================================================
# ⭕ 2〜8 個の条件の重なりの格子と内訳（旧 venn.py）
# 条件の重なり（load_overlap の結果）の図。マスの格子と、領域ごとの内訳の積み上げ棒。
#
# n 個の集合の 2^n 領域を 1 つずつ置く。空の領域も 0 のまま格子に置く。円は描かない。面積は件数と無関係。
# 返すのは Plotly の JSON 仕様（data / layout）だけ。plotly パッケージも numpy も使わない。
# ====================================================================================================

GAP = 8  # 枠どうし・マスどうしの間隔（px）。px の値は 8 の倍数にしている
LABEL = 24  # 集合の番号ラベルの高さ（px）
BAR_ROW = 24  # 内訳の棒 1 本の高さ（px）
MAX_SERIES = 7  # 内訳で色を付ける値の数。残りは「その他」にまとめる
BY_KEYS = ("team", "team_name", "league", "season", "upper_half")  # 内訳に使える列（unit の項目）
# 集合の枠と内訳の値の色。先頭から固定の順（値の昇順・集合の番号順）で割り当てる。
SERIES_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
OTHER_COLOR = "#898781"
# 件数は一つの色相（青）の薄い→濃い。
COUNT_SCALE = [[0.0, "#cde2fb"], [0.25, "#86b6ef"], [0.5, "#3987e5"], [0.75, "#1c5cab"], [1.0, "#0d366b"]]
INK = "#1a1a1a"
TITLE_LEFT = dict(x=0, xref="container", xanchor="left", font=dict(size=14))  # 図が題より狭くても左が切れない


def _esc(text) -> str:
    """Plotly の文字は HTML の一部を解釈する。条件式の < > & をそのまま見せる。"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _bits_text(bits) -> str:
    return "".join("1" if bit else "0" for bit in bits)


def _gray(width: int) -> list[int]:
    """0 .. 2^width-1 をグレイ符号の順に。先頭の集合（最上位ビット）が 1 の側から始める。"""
    return [k ^ (k >> 1) for k in range(1 << width)][::-1]


def _pattern(value: int, width: int) -> tuple:
    return tuple(bool(value >> (width - 1 - j) & 1) for j in range(width))


def karnaugh(n: int) -> tuple[list[tuple], list[tuple]]:
    """行と列の並び。行は前半 n//2 個の集合、列は残りの集合の入る/入らないの組。

    隣り合う行どうし・列どうしは 1 つの集合だけが違う。マス (r, c) の領域は rows[r] + cols[c]。
    """
    if n < 2:
        raise ValueError("格子にする集合は 2 個以上")
    rows = n // 2
    return (
        [_pattern(v, rows) for v in _gray(rows)],
        [_pattern(v, n - rows) for v in _gray(n - rows)],
    )


def _runs(flags: list[bool]) -> list[tuple[int, int]]:
    """True が続く区間（開始, 終了）。"""
    runs, start = [], None
    for index, flag in enumerate([*flags, False]):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            runs.append((start, index - 1))
            start = None
    return runs


def _set_label(index: int, cond: dict) -> str:
    return f"S{index + 1}: {_esc(cond['label'])}"


def grid_figure(overlap: dict) -> dict:
    """2^n 領域を、カルノー図の並びの格子に置く。マスの数は件数、色は件数（濃いほど多い）。

    集合は枠で示す（行の集合は横長、列の集合は縦長の長方形）。
    """
    conds = overlap["conditions"]
    n = len(conds)
    rows, cols = karnaugh(n)
    row_sets = len(rows[0])
    region = {tuple(r["bits"]): r for r in overlap["regions"]}
    cell = 64 if len(cols) <= 8 else 40
    gap = GAP / cell
    z = [[region[rp + cp]["count"] for cp in cols] for rp in rows]
    custom = [
        [
            {"name": _esc(region[rp + cp]["name"]), "bits": _bits_text(rp + cp), "count": region[rp + cp]["count"]}
            for cp in cols
        ]
        for rp in rows
    ]
    # 枠は格子の外へはみ出す。軸の座標だとはみ出しが切られるので、paper 座標（格子 = 0..1）にする。
    px = lambda x: (x + 0.5) / len(cols)  # noqa: E731
    py = lambda y: 1 - (y + 0.5) / len(rows)  # noqa: E731
    shapes, notes, legend = [], [], []
    for i in range(n):
        by_row = i < row_sets
        axis, k = (rows, i) if by_row else (cols, i - row_sets)
        color = SERIES_COLORS[i % len(SERIES_COLORS)]
        out = (k + 1) * gap  # 同じ側の集合どうしで枠が重ならないよう、外へ GAP ずつずらす
        for a, b in _runs([p[k] for p in axis]):
            if by_row:
                x0, x1, y0, y1 = -0.5 - out, len(cols) - 0.5 + out, a - 0.5 + gap, b + 0.5 - gap
            else:
                x0, x1, y0, y1 = a - 0.5 + gap, b + 0.5 - gap, -0.5 - out, len(rows) - 0.5 + out
            shapes.append(
                dict(type="rect", name=f"S{i + 1}", xref="paper", yref="paper",
                     x0=px(x0), x1=px(x1), y0=py(y0), y1=py(y1),
                     line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)", layer="above")
            )
            at = dict(showarrow=False, text=f"<b>S{i + 1}</b>", font=dict(size=12, color=INK),
                      bgcolor="#ffffff", bordercolor=color, borderwidth=2, borderpad=2, xref="paper", yref="paper")
            # 入れ子の枠は中心が同じになりやすい。ラベルは集合ごとに LABEL px ずつずらして重ならないようにする
            # （枠の区間からは出さない）。
            spread = (k - (len(axis[0]) - 1) / 2) * LABEL
            room = max(0, (b - a + 1) * cell / 2 - LABEL / 2)
            spread = max(-room, min(room, spread))
            if by_row:  # 右の外側
                at.update(x=px(x1), y=py((y0 + y1) / 2), xanchor="left", yanchor="middle", xshift=4, yshift=-spread)
            else:  # 下の外側
                at.update(x=px((x0 + x1) / 2), y=py(y1), xanchor="center", yanchor="top", yshift=-4, xshift=spread)
            notes.append(at)
        # 空の配列だと Plotly はトレースを非表示にして凡例にも出さない。[None] なら線の見本だけ出る。
        legend.append(
            dict(type="scatter", x=[None], y=[None], mode="lines", name=_set_label(i, conds[i]),
                 line=dict(color=color, width=2), meta={"role": "legend", "set": i + 1})
        )
    col_sets = n - row_sets
    plot_w, plot_h = len(cols) * cell, len(rows) * cell
    longest = max(len(_set_label(i, c)) for i, c in enumerate(conds))
    legend_w = 8 * ceil((longest * 8 + 48) / 8)
    side = row_sets * GAP + 48  # 行の集合の枠とラベルが外へ出る分
    margin = dict(l=48 + 16 * row_sets, r=side + legend_w, t=136 + 16 * col_sets, b=48 + 16 * col_sets)
    heat = dict(
        type="heatmap", x=list(range(len(cols))), y=list(range(len(rows))), z=z,
        texttemplate="%{z}", textfont=dict(family=FONT, size=16 if cell == 64 else 12),
        customdata=custom, colorscale=COUNT_SCALE, zmin=0, zsmooth=False, xgap=2, ygap=2,
        showscale=False, showlegend=False,
        hovertemplate="領域 %{customdata.name}<br>桁 %{customdata.bits}<br>件数 %{customdata.count}<extra></extra>",
    )
    hidden = dict(ticks="outside", tickcolor="rgba(0,0,0,0)", showgrid=False, zeroline=False, tickfont=dict(size=12))
    span = lambda a, b: f"S{a}" if a == b else f"S{a}–S{b}"  # noqa: E731
    layout = _base_layout(
        title=dict(
            text=(f"条件の重なり: {n} 集合・{2 ** n} 領域<br>"
                  f"行は {span(1, row_sets)}、列は {span(row_sets + 1, n)} に入る(1)・入らない(0)<br>"
                  "隣のマスは 1 つの集合だけ違う。空の領域も 0 で置く"),
            **TITLE_LEFT,
        ),
        width=max(640, margin["l"] + plot_w + margin["r"]),  # 題が切れない最小幅
        height=margin["t"] + plot_h + margin["b"],
        margin=margin,
        xaxis=dict(tickvals=list(range(len(cols))), ticktext=[_bits_text(c) for c in cols], side="top",
                   range=[-0.5, len(cols) - 0.5], ticklen=col_sets * GAP + 8, **hidden),
        yaxis=dict(tickvals=list(range(len(rows))), ticktext=[_bits_text(r) for r in rows],
                   range=[len(rows) - 0.5, -0.5], ticklen=row_sets * GAP + 8, **hidden),
        shapes=shapes,
        annotations=notes,
        legend=dict(x=1 + side / plot_w, xanchor="left", y=1, yanchor="top", font=dict(size=12)),
        meta={
            "kind": "overlap_grid",
            "source": "season.jsonl",
            "sets": [{"index": i + 1, "label": c["label"]} for i, c in enumerate(conds)],
            "rows": [_bits_text(r) for r in rows],
            "cols": [_bits_text(c) for c in cols],
            "z": z,
        },
    )
    return {"data": [heat, *legend], "layout": layout}


def _label(value) -> str:
    return value if isinstance(value, str) else _exact_text(value)


def breakdown_figure(overlap: dict, by: str = "team", keep: tuple = ()) -> dict:
    """領域ごとの件数を、`by` の値で分けた積み上げ棒。長さが件数、色が値。

    色は値の昇順で割り当てる。MAX_SERIES を超える値は「その他」にまとめ、中身はホバーに出す。
    `keep` の値（文字列で書く）は件数にかかわらず別の色で残す。件数 0 の領域は棒にせず、数を題に書く
    （格子とページの表には出ている）。
    """
    if by not in BY_KEYS:
        raise ValueError(f"内訳の列は {', '.join(BY_KEYS)} のどれか: {by}")
    units = overlap["units"]
    if not units:
        raise ValueError("内訳にする行がない")
    totals = Counter(unit[by] for unit in units)
    order = sorted(totals, key=lambda v: (v is None, v))
    forced = [v for v in order if _label(v) in keep]
    if len(forced) > MAX_SERIES:
        raise ValueError(f"breakdown-keep で別の色に残せる値は {MAX_SERIES} 個まで")
    rest = sorted((v for v in order if v not in forced), key=lambda v: -totals[v])
    shown = set(forced + rest[: max(0, MAX_SERIES - len(forced))])
    kept = [v for v in order if v in shown]
    folded = [v for v in order if v not in shown]

    regions = sorted((r for r in overlap["regions"] if r["count"]), key=lambda r: -r["count"])
    empty = len(overlap["regions"]) - len(regions)
    labels = [f"{_bits_text(r['bits'])}  ({r['count']})" for r in regions]
    members = [Counter(units[i][by] for i in r["unit_index"]) for r in regions]
    traces = []
    for slot, value in enumerate(kept):
        traces.append(
            dict(type="bar", orientation="h", name=_esc(_label(value)), y=labels,
                 x=[m[value] for m in members],
                 marker=dict(color=SERIES_COLORS[slot % len(SERIES_COLORS)], line=dict(color="#ffffff", width=2)),
                 hovertemplate="領域 %{y}<br>" + _esc(_label(value)) + " %{x}<extra></extra>",
                 meta={"role": "series", "value": value})
        )
    if folded:
        inside = [", ".join(f"{_esc(_label(v))} {m[v]}" for v in folded if m[v]) for m in members]
        traces.append(
            dict(type="bar", orientation="h", name="その他", y=labels,
                 x=[sum(m[v] for v in folded) for m in members],
                 marker=dict(color=OTHER_COLOR, line=dict(color="#ffffff", width=2)),
                 customdata=inside,
                 hovertemplate="領域 %{y}<br>その他 %{x}<br>%{customdata}<extra></extra>",
                 meta={"role": "other", "values": folded})
        )
    biggest = max(r["count"] for r in regions) if regions else 0
    count_axis = dict(title=dict(text="件数"), rangemode="tozero", tickformat="d")
    if biggest <= 10:
        count_axis["dtick"] = 1  # 少ないときに 2.5 件の目盛りが出ない
    plot_h = max(len(regions), 1) * BAR_ROW
    longest = max([len(t["name"]) for t in traces] + [3])
    layout = _base_layout(
        title=dict(
            text=(f"領域ごとの内訳（{by}）<br>棒の長さは件数、左の括弧の数は領域の件数。"
                  f"空の領域 {empty} 個は棒にしない"
                  + (f"。{len(folded)} 個の値は「その他」" if folded else "")),
            **TITLE_LEFT,
        ),
        width=1040,
        height=plot_h + 160,
        margin=dict(l=168, r=8 * ceil((longest * 8 + 56) / 8), t=96, b=64),
        barmode="stack",
        bargap=0.2,
        xaxis=count_axis,
        yaxis=dict(type="category", categoryorder="array", categoryarray=labels, autorange="reversed", automargin=True),
        legend=dict(x=1.02, xanchor="left", y=1, yanchor="top", font=dict(size=12), traceorder="normal"),
        meta={
            "kind": "overlap_breakdown",
            "source": "season.jsonl",
            "by": by,
            "empty_regions": empty,
            "folded": folded,
            "regions": [
                {"bits": _bits_text(r["bits"]), "count": r["count"], "by": {_label(v): c for v, c in m.items()}}
                for r, m in zip(regions, members)
            ],
        },
    )
    return {"data": traces, "layout": layout}


def venn_figures(overlap: dict, by: str = "team", keep: tuple = ()) -> dict[str, dict]:
    """Python から呼ぶ入口。load_overlap の結果から二つの図の仕様を返す。"""
    return {"overlap_grid": grid_figure(overlap), "overlap_breakdown": breakdown_figure(overlap, by, keep)}


# ====================================================================================================
# 📄 HTML（Markdown は自作の markdown.py）（旧 htmlout.py）
# HTML。文章と表は Markdown から作る。Plotly は index.html の図（軌跡、球団×年、条件の重なり）だけ。
# ====================================================================================================

_STYLE = """
body { margin: 1.5rem auto; max-width: 1100px; color: #1a1a1a; background: #fff;
  font-family: @@FONT@@; line-height: 1.5; }
h1, h2 { font-weight: 650; }
a { color: #0b57d0; }
pre { white-space: pre-wrap; background: #f7f7f7; padding: 0.8rem 1rem; }
table { border-collapse: collapse; margin: 0.4rem 0 1rem; }
td, th { border: 1px solid #ddd; padding: 0.15rem 0.45rem; vertical-align: top; text-align: left; }
caption { text-align: left; font-weight: 650; padding-bottom: 0.25rem; }
.figure { min-height: 480px; }
.provenance { color: #333; }
details { margin: 0.75rem 0 1.1rem; }
summary { cursor: pointer; }
""".replace("@@FONT@@", FONT)

_SAFE_ANCHOR = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
_CARD_FIELDS = ("unit", "season", "team", "team_name", "focus", "surprise", "question", "values", "context")
_COUNTEREXAMPLE_ORDER = (
    "反例の並びは記録の順である。`surprise` の絶対値の降順。同点は `season`、次に `team`。"
)
_SUMMARY_FORMS = (("original", "元"), ("converse", "逆"), ("inverse", "裏"), ("contrapositive", "対偶"))

_INDEX_MD = """\
入力ファイル: `season.jsonl`, `propositions.jsonl`。値は記録のまま。
{: .provenance}

## 得点順位 × 失点順位

@@TRAJECTORY@@

## 球団 × 年（`@@COLUMN@@`）

@@HEATMAP@@

## 条件集合の重なり

@@OVERLAP_NOTE@@

@@OVERLAP_GRID@@

@@OVERLAP_BREAKDOWN@@

@@OVERLAP@@

[命題の一覧](propositions.html)
"""

_AFTER_SUMMARY = """\
入力ファイル: `propositions.jsonl`。`hold` と反例（`n - hold`）は記録の `n` と `hold` から数える。`rate` はファイルの数のまま置く。反例の表の行数は `counterexamples` の長さで、`n - hold` とは別に置く。除外した反例は全命題で 145 行。`held_out` の再確認は 8 命題にある。
{: .provenance}

[球団年の図へ](index.html)
"""


@lru_cache(maxsize=1)
def _markdown_library():
    """📝 自作の markdown.py（myon-bioinformatics/markdown を vendor/markdown に写し、vendor.lock.json で固定）。

    名前は子どうしでぶつからないように dragowing_markdown。Python-Markdown（PyPI）は使わない。
    """
    path = Path(__file__).resolve().parent / "vendor" / "markdown" / "markdown.py"
    if not path.is_file():
        raise FileNotFoundError(f"markdown.py が無い: {path}（DRAgoWing のリポジトリから動かす）")
    spec = importlib.util.spec_from_file_location("dragowing_markdown", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclass が自分のモジュールを引く
    spec.loader.exec_module(module)
    return module


def render_md(source: str) -> str:
    """ページは Python で組んだ Markdown。図の <div>・<details> は HTML のまま通し、{: .class} を読む。"""
    return _markdown_library().markdown_to_html(source, raw_html=True, attr_list=True)


def to_builtin(obj):
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int) and not isinstance(obj, bool):
        return int(obj)
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            raise ValueError("非有限の数は置かない")
        return float(obj)
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {str(key): to_builtin(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_builtin(value) for value in obj]
    module = type(obj).__module__
    if module == "numpy":
        if hasattr(obj, "tolist"):
            return to_builtin(obj.tolist())
        return to_builtin(obj.item())
    raise TypeError(f"JSON にできない型: {type(obj)!r}")


def embed_json(obj) -> str:
    raw = json.dumps(to_builtin(obj), ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    return raw.replace("<", "\\u003c")


def exact_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def md_inline(value) -> str:
    """表の外。Markdown に渡す前に HTML の区切りだけを逃がす。"""
    text = value if isinstance(value, str) else exact_json(value)
    return html.escape(text, quote=False)


def md_cell(value) -> str:
    return md_inline(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def spec_from(page: str, div_id: str) -> dict:
    marker = f'id="{div_id}-data">'
    start = page.index(marker) + len(marker)
    end = page.index("</script>", start)
    return json.loads(page[start:end])


def _js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def structure_figure(graph):
    """Display measured XYZ coordinates and the contact candidates supplied by SSIS."""
    if graph.get("schema") != "structure-graph/1" or graph.get("unit") != "angstrom":
        raise ValueError("expected structure-graph/1 in angstrom")
    atom_nodes = [n for n in graph["nodes"] if n["type"] == "Atom"]
    atoms = {n["id"]: n for n in atom_nodes}
    if len(atoms) != len(atom_nodes):
        raise ValueError("duplicate atom ID")
    if not atoms or any(not math.isfinite(a[k]) for a in atoms.values() for k in "xyz"):
        raise ValueError("expected finite atom coordinates")
    traces = []
    contacts = [e for e in graph["edges"] if e["relation"] == "nearAtom"]
    if contacts:
        lines = {axis: [] for axis in "xyz"}
        hover = []
        for edge in contacts:
            hover.extend([escape(", ".join(edge["labels"])) + f" · {edge['distance_angstrom']:.3f} Å"] * 2 + [""])
            a, b = atoms[edge["source"]], atoms[edge["target"]]
            for axis in lines:
                lines[axis].extend((a[axis], b[axis], None))
        traces.append(dict(type="scatter3d", mode="lines", name="接触候補", **lines,
                           line=dict(color="#7794a0", width=3), text=hover, hovertemplate="%{text}<extra></extra>"))
    colors = {"C": "#626d7c", "N": "#3c66ae", "O": "#c84d52", "P": "#a0539f", "S": "#b98b16"}
    for element in sorted({a["element"] for a in atoms.values()}):
        group = [a for a in atoms.values() if a["element"] == element]
        labels = [escape(" ".join(str(a[k]) for k in ("chain", "residue", "residue_id", "name", "altloc")).strip())
                  for a in group]
        traces.append(dict(type="scatter3d", mode="markers", name=escape(element), text=labels,
                           marker=dict(size=4, color=colors.get(element, "#408878")),
                           hovertemplate="%{text}<br>(%{x}, %{y}, %{z}) Å<extra></extra>",
                           **{axis: [a[axis] for a in group] for axis in "xyz"}))
    scene = {axis + "axis": {"title": {"text": axis.upper() + " (Å)"}} for axis in "xyz"}
    title = f"モデル {escape(str(graph['model']))} · {len(atoms)} 原子 · 接触候補 {len(contacts)}/{graph['contact_count']}"
    return {"data": traces, "layout": {"title": {"text": title}, "scene": {**scene, "aspectmode": "data"}, "height": 570}}


def figure_block(spec: dict, div_id: str) -> str:
    payload = embed_json(spec)
    attr = html.escape(div_id, quote=True)
    data_id = _js_string(div_id + "-data")
    initializer = _plotly_initializer(
        div_id, f"JSON.parse(document.getElementById({data_id}).textContent)",
        "{responsive:true,displaylogo:false}",
    )
    return (
        f'<div id="{attr}" class="figure"></div>\n'
        f'<script type="application/json" id="{attr}-data">{payload}</script>\n'
        f'<script>{initializer}</script>'
    )


def standalone(title: str, body: str, *, plotly: bool = False, embed: bool = False) -> str:
    """HTML 文書。plotly は軌跡と球団×年のページだけ。"""
    script = plotly_script_tags(embed=embed) + "\n" if plotly else ""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{_STYLE}</style>\n"
        f"{script}"
        "</head>\n"
        "<body>\n"
        f"<h1>{html.escape(title)}</h1>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


def _anchors(items: list[dict]) -> list[str]:
    used = set()
    anchors = []
    for index, item in enumerate(items, start=1):
        ident = str(item.get("id") or "")
        anchor = ident if _SAFE_ANCHOR.fullmatch(ident) else f"row-{index}"
        if anchor in used:
            anchor = f"row-{index}"
        while anchor in used:
            anchor = f"row-{index}-{len(anchors)}"
        used.add(anchor)
        anchors.append(anchor)
    return anchors


def _hold_against_rate(form):
    counts = _counts(form) if isinstance(form, dict) else None
    if counts is None:
        hold, against = "不明", "不明"
    else:
        n, held = counts
        hold, against = held, n - held
    if not isinstance(form, dict) or "rate" not in form:
        rate = "不明"
    else:
        rate = form.get("rate")
    return hold, against, rate


def _summary_table(items: list[dict], anchors: list[str]) -> str:
    headers = ["ID", "statement"]
    for _name, short in _SUMMARY_FORMS:
        headers.extend((f"{short} hold", f"{short} 反例", f"{short} rate"))
    rows = []
    for item, anchor in zip(items, anchors):
        ident = str(item.get("id") or "")
        label = html.escape(ident, quote=False).replace("|", "\\|")
        cells = [f"[{label}](#{anchor})", md_cell(item["statement"]) if isinstance(item.get("statement"), str) else ""]
        forms = _forms(item)
        for name, _short in _SUMMARY_FORMS:
            hold, against, rate = _hold_against_rate(forms.get(name))
            cells.extend((md_cell(hold), md_cell(against), md_cell(rate)))
        rows.append(cells)
    return _table(headers, rows)


def _table(headers, row_cells) -> str:
    head = "| " + " | ".join(md_cell(header) for header in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(cells) + " |" for cells in row_cells]
    return "\n".join([head, sep, *body])


def _card_columns(cards: list[dict]) -> list[str]:
    return [key for key in _CARD_FIELDS if any(key in card for card in cards)]


def _example_table(cards: list[dict]) -> str:
    columns = _card_columns(cards)
    rows = [[md_cell(card[key]) if key in card else "" for key in columns] for card in cards]
    return _table(columns, rows)


def _details_block(summary: str, body: str) -> str:
    return "\n".join(['<details markdown="1">', f"<summary>{html.escape(summary, quote=False)}</summary>", "", body, "", "</details>"])


def counterexamples_md(item: dict) -> str:
    """反例。元と対偶、逆と裏が同じ単位の並びなら 1 表にまとめる。"""
    forms = _forms(item)
    shown = set()
    blocks = [f"<p>{md_inline(_COUNTEREXAMPLE_ORDER)}</p>"]
    for left, right in COUNTEREXAMPLE_PAIR_LABELS:
        lf, rf = forms.get(left), forms.get(right)
        lc = [c for c in (lf.get("counterexamples") if isinstance(lf, dict) else None) or [] if isinstance(c, dict)]
        rc = [c for c in (rf.get("counterexamples") if isinstance(rf, dict) else None) or [] if isinstance(c, dict)]
        if not lc and not rc:
            continue
        if lc and rc and counterexample_lists_equal(lf, rf):
            note = f"{FORM_LABEL[left]} と {FORM_LABEL[right]} は同じ単位の並びである。"
            blocks.append(_details_block(f"{FORM_LABEL[left]} / {FORM_LABEL[right]}（{len(lc)} 行）", f"{note}\n\n{_example_table(lc)}"))
            shown.update({left, right})
        else:
            mismatch = bool(lc and rc)
            for name, cards in ((left, lc), (right, rc)):
                if not cards or name in shown:
                    continue
                summary = f"{FORM_LABEL[name]}（{len(cards)} 行）"
                if mismatch:
                    summary = f"{FORM_LABEL[name]}（不一致、{len(cards)} 行）"
                blocks.append(_details_block(summary, _example_table(cards)))
                shown.add(name)
    for name in FORM_ORDER:
        if name in shown:
            continue
        form = forms.get(name)
        cards = [c for c in (form.get("counterexamples") if isinstance(form, dict) else None) or [] if isinstance(c, dict)]
        if not cards:
            continue
        blocks.append(_details_block(f"{FORM_LABEL[name]}（{len(cards)} 行）", _example_table(cards)))
    return "\n\n".join(blocks[1:]) if len(blocks) > 1 else ""


def excluded_counterexamples_md(item: dict) -> str:
    cards = [c for c in item.get("excluded_counterexamples") or [] if isinstance(c, dict)]
    if not cards:
        return ""
    return "\n".join(
        [
            "### 除外した反例",
            "",
            _details_block(f"除外した反例（{len(cards)} 行）", _example_table(cards)),
        ]
    )


def held_out_md(item: dict) -> str:
    held = item.get("held_out")
    if not isinstance(held, dict):
        return ""
    lines = ["### held_out の再確認", ""]
    if "excluded_units" in held:
        lines.append(f"excluded_units: {md_inline(held['excluded_units'])}")
    for key in ("n", "hold", "rate", "verdict", "fisher_p", "sigma", "sigma_band", "p_above", "p_below"):
        if key in held:
            lines.append(f"{key}: {md_inline(held[key])}")
    cards = [c for c in held.get("counterexamples") or [] if isinstance(c, dict)]
    if cards:
        lines.extend(["", _details_block(f"held_out の反例（{len(cards)} 行）", _example_table(cards))])
    return "\n".join(lines)


def section_md(item: dict, anchor: str) -> str:
    ident = str(item.get("id") or "")
    label = registration_status(item)
    shown = ident if re.fullmatch(r"[A-Za-z0-9_-]+", ident) else md_inline(ident)
    parts = [f"## ［{label}］ {shown} {{#{anchor}}}", ""]
    if isinstance(item.get("statement"), str):
        parts.append(f"statement: {md_inline(item['statement'])}")
        parts.append("")
    parts.append("```")
    parts.append(render_logic(item))
    parts.append("```")
    parts.append("")
    parts.append(render_forms_table(item, heading=False))
    listed = counterexamples_md(item)
    if listed:
        parts.extend(["", listed])
    excluded = excluded_counterexamples_md(item)
    if excluded:
        parts.extend(["", excluded])
    held = held_out_md(item)
    if held:
        parts.extend(["", held])
    return "\n".join(parts)


def proposition_section(item: dict) -> str:
    anchor = _anchors([item])[0]
    return render_md(section_md(item, anchor))


def propositions_md(items: list[dict]) -> str:
    anchors = _anchors(items)
    parts = [_summary_table(items, anchors), "", _AFTER_SUMMARY.rstrip(), ""]
    for item, anchor in zip(items, anchors):
        parts.extend(["", section_md(item, anchor)])
    return "\n".join(parts)


def propositions_body(items: list[dict]) -> str:
    return render_md(propositions_md(items))


def overlap_md(overlap: dict) -> str:
    """領域の件数と単位。円は描かない。"""
    regions = _table(
        ["領域", "count"],
        [[md_cell(region["name"]), md_cell(region["count"])] for region in overlap["regions"]],
    )
    conds = overlap["conditions"]
    columns = overlap["columns"]
    headers = ["unit", "team_name", "league", "season", "upper_half"]
    headers += [f"in:{cond['label']}" for cond in conds]
    headers += [f"value:{col}" for col in columns]
    rows = []
    for unit in overlap["units"]:
        values = [unit["unit"], unit["team_name"], unit["league"], unit["season"], unit["upper_half"]]
        values.extend(unit["in_set"])
        values.extend(unit["values"][col] for col in columns)
        rows.append([md_cell(value) for value in values])
    note = "件数は領域の整数である。円は描かない。単位は `team-season`。値は記録のまま。"
    return note + "\n\n" + regions + "\n\n" + _table(headers, rows)


def heatmap_note(spec: dict, column: str) -> str:
    z = spec["layout"]["meta"]["z"]
    finite = [value for row in z for value in row if isinstance(value, (int, float))]
    zmin = min(finite) if finite else None
    zmax = max(finite) if finite else None
    return (
        f"色は `{column}` の値（`sigma_band` ではない）。"
        f"zmin={exact_json(zmin)}, zmax={exact_json(zmax)}。"
        "マスの文字は A（`upper_half==true`）と B（`upper_half==false`）。"
    )


def overlap_note(grid: dict, breakdown: dict) -> str:
    n = len(grid["layout"]["meta"]["sets"])
    meta = breakdown["layout"]["meta"]
    other = "「その他」の中身はホバーに出る。" if meta["folded"] else ""
    return (
        f"集合は {n} 個（S1–S{n}、条件は凡例）。格子のマスは領域で、数は件数（丸めない）、色は件数（濃いほど多い）。"
        "枠は集合を示す。円は描かない。面積は件数と関係しない。"
        f"内訳は領域ごとの件数を `{md_inline(meta['by'])}` の値で分けたもので、色は値の昇順で割り当てる。{other}"
    )


def index_body(
    rows: list[dict], overlap: dict, column: str, team_order=(), by: str = "team", keep: tuple = ()
) -> tuple[str, dict]:
    trajectory = trajectory_figure(rows)
    heat = heatmap_figure(rows, column, team_order)
    venn = venn_figures(overlap, by, keep)
    source = (
        _INDEX_MD.replace("@@COLUMN@@", md_inline(column))
        .replace("@@TRAJECTORY@@", figure_block(trajectory, "trajectory"))
        .replace("@@HEATMAP@@", heatmap_note(heat, column) + "\n\n" + figure_block(heat, "heatmap"))
        .replace("@@OVERLAP_NOTE@@", overlap_note(venn["overlap_grid"], venn["overlap_breakdown"]))
        .replace("@@OVERLAP_GRID@@", figure_block(venn["overlap_grid"], "overlap_grid"))
        .replace("@@OVERLAP_BREAKDOWN@@", figure_block(venn["overlap_breakdown"], "overlap_breakdown"))
        .replace("@@OVERLAP@@", overlap_md(overlap))
    )
    return render_md(source), {"trajectory": trajectory, "heatmap": heat, **venn}


# ====================================================================================================
# 📝 研究レポート（集計の Plotly の図）（旧 research_report.py）
# DRAgoWing: render aggregate Plotly figures, without doing research statistics.
#
# render_report。使う側: reports/research.py、Aoi の research/gpt-r001-score-allocation/render_*.py、
# research_loop/feedback.py（research.build 経由）。Plotly.js の URL（3.6.0、SRI なし）は当時のまま。
# 文字は FONT と同じ（メイリオ先頭）。テンプレートの中に書いてあり、tests/test_figures.py で一致を確かめる。
# ====================================================================================================

PLOTLY_URL = 'https://cdn.plot.ly/plotly-3.6.0.min.js'


def render_report(spec):
    """Return a portable HTML report. Spec contains options and keyed figure frames."""
    if not spec['frames'] or spec['default'] not in spec['frames']:
        raise ValueError('Missing default frame')
    payload = json.dumps(spec, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return TEMPLATE.replace('@@TITLE@@', html.escape(spec['title'])).replace('@@URL@@', PLOTLY_URL).replace('@@DATA@@', payload)


TEMPLATE = '''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#182b43;font:16px/1.65 Meiryo,メイリオ,sans-serif}main{max-width:1180px;margin:auto;padding:32px 20px}h1{font-size:clamp(25px,4vw,38px);line-height:1.3}h2{font-size:20px}.eyebrow{color:#1669a5;font-weight:750;letter-spacing:.12em}.controls{display:flex;gap:24px;flex-wrap:wrap;padding:18px 0}select{font:inherit;padding:8px;border:1px solid #8193a9;border-radius:6px;background:white}section{background:white;padding:20px;margin:22px 0;border:1px solid #dce4ed;border-radius:12px}.plot{height:390px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:right;border-bottom:1px solid #ddd;padding:7px}th:first-child,td:first-child{text-align:left}.scroll{overflow-x:auto}details{margin-top:14px}summary{cursor:pointer;color:#176197}footer{font-size:13px;overflow-wrap:anywhere}.notice{border-left:4px solid #c08125;padding:10px 15px;background:#fff6e6}#status{font-weight:650}@media(max-width:600px){main{padding:20px 10px}section{padding:12px}.plot{height:380px}}
</style>
<main><div class="eyebrow">AOI / DRAgoWing</div><h1>@@TITLE@@</h1><p id="intro"></p><div class="controls" id="controls"></div><p id="status" aria-live="polite"></p><div class="notice" id="notes"></div><div id="panels"></div><footer id="provenance"></footer></main>
<script id="report-data" type="application/json">@@DATA@@</script>
<script src="@@URL@@"></script>
<script>
const spec=JSON.parse(document.getElementById('report-data').textContent);
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
document.getElementById('intro').textContent=spec.intro;
document.getElementById('notes').textContent=spec.notes;
document.getElementById('provenance').textContent=spec.provenance;
const choices=[];
spec.controls.forEach((c,i)=>{const label=el('label',c.label+' '),s=el('select');s.id=c.id;c.options.forEach(o=>{const opt=el('option',o.label);opt.value=o.value;s.append(opt)});s.value=spec.default.split('|')[i];s.addEventListener('change',draw);label.append(s);document.getElementById('controls').append(label);choices.push(s)});
let generation=0;
async function draw(){
 const current=++generation;
 const key=choices.map(s=>s.value).join('|'),frame=spec.frames[key];
 document.getElementById('status').textContent=frame.caption;
 const host=document.getElementById('panels');host.querySelectorAll('.plot').forEach(p=>{if(window.Plotly)Plotly.purge(p)});host.replaceChildren();
 for(const p of frame.panels){if(current!==generation)return;const sec=el('section');sec.append(el('h2',p.title),el('p',p.note));const plot=el('div');plot.className='plot';sec.append(plot);
 const details=el('details'),summary=el('summary','数値と分母を表示');details.append(summary);const sc=el('div');sc.className='scroll';const table=el('table'),head=el('thead'),hr=el('tr');p.headers.forEach(h=>hr.append(el('th',h)));head.append(hr);table.append(head);const body=el('tbody');p.rows.forEach(r=>{const tr=el('tr');r.forEach(v=>tr.append(el('td',v)));body.append(tr)});table.append(body);sc.append(table);details.append(sc);sec.append(details);host.append(sec);
 if(window.Plotly){await Plotly.newPlot(plot,p.data,{margin:{l:60,r:20,t:20,b:85},legend:{orientation:'h',y:-.20},paper_bgcolor:'white',plot_bgcolor:'white',...p.layout,font:{family:'Meiryo, メイリオ, sans-serif',color:'#182b43',...(p.layout||{}).font}},{responsive:true,displaylogo:false});}else{plot.textContent='グラフを読み込めません。インターネット接続を確認してください。数値表は利用できます。';plot.style.height='auto'}
 }if(current===generation)window.reportReady=key;
}
draw();
</script></html>'''


# ====================================================================================================
# 🖥️ レポートを書く（python -m dragowing RESULTS）（旧 cli.py）
# python -m dragowing RESULTS
#
# HTML を --out（省略時は新しい一時ディレクトリ）に書き、書いたものをリンクで1行ずつ表示する。
# 重なりは既定で標準ライブラリの経路を使う。--overlap-backend native で従来の経路を選べる。SVG は --svg で、親の plotly_min が描く（Chrome なし）。
# ====================================================================================================

def write_svg(spec: dict, path: Path) -> None:
    """🖼️ 図の JSON を SVG に。描くのは親の plotly_min（標準ライブラリ、Chrome なし）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(figure_svg(spec))


def team_order(text: str) -> tuple[str, ...]:
    codes = tuple(code.strip() for code in text.split(",") if code.strip())
    if len(codes) != len(set(codes)):
        raise ValueError("--team-order に同じ記号が2回ある")
    return codes


PALETTE = ('#440154', '#3B528B', '#21918C', '#5EC962', '#FDE725')


def heat_color(value, low, high, levels=0):
    """Viridis-like five-stop display scale; source value is never modified."""
    if value is None:
        return None
    if not all(type(v) in (int, float) and math.isfinite(v) for v in (value, low, high)) or low > high:
        raise ValueError('finite value and ordered range required')
    if type(levels) is not int or (levels != 0 and not 2 <= levels <= 256):
        raise ValueError('levels must be 0 (continuous) or 2..256')
    t = 0.5 if high == low else max(0, min(1, (value - low) / (high - low)))
    if levels:
        t = math.floor(t * (levels - 1) + 0.5) / (levels - 1)
    p = t * (len(PALETTE) - 1)
    i = min(len(PALETTE) - 2, int(p))
    a, b = (bytes.fromhex(c[1:]) for c in PALETTE[i:i + 2])
    return '#' + ''.join(f'{math.floor(x + (y-x)*(p-i) + 0.5):02X}' for x, y in zip(a, b))


def heatmap_scene(source):
    """Import a numeric matrix or ONE Plotly heatmap trace; row zero is at top.

    This imports data, not Plotly layout/axis rendering. Keep source metadata so
    the scene is an editable composition, never a replacement research result.
    """
    if isinstance(source, list):
        trace = {'z': source}
    elif isinstance(source, dict) and isinstance(source.get('data'), list):
        traces = [t for t in source['data'] if isinstance(t, dict) and t.get('type') == 'heatmap']
        if len(traces) != 1:
            raise ValueError('exactly one heatmap trace required')
        trace = traces[0]
    else:
        trace = source
    if not isinstance(trace, dict):
        raise ValueError('matrix or heatmap object required')
    z = trace.get('z')
    if (not isinstance(z, list) or not z or not isinstance(z[0], list) or not z[0]
            or len(z) * len(z[0]) > 4096 or any(not isinstance(r, list) or len(r) != len(z[0]) for r in z)):
        raise ValueError('rectangular matrix of 1..4096 cells required')
    finite = [v for row in z for v in row if v is not None]
    def safe(v):
        if type(v) is int:
            return abs(v) <= 2**53-1
        return type(v) is float and math.isfinite(v) and (not v.is_integer() or abs(v) <= 2**53-1)
    if any(not safe(v) for v in finite):
        raise ValueError('finite JavaScript-safe numbers or null required')
    low, high = trace.get('zmin'), trace.get('zmax')
    low = min(finite, default=0) if low is None else low
    high = max(finite, default=1) if high is None else high
    if not safe(low) or not safe(high):
        raise ValueError('finite JavaScript-safe color range required')
    heat_color(low, low, high)
    x, y = trace.get('x', list(range(len(z[0])))), trace.get('y', list(range(len(z))))
    if not isinstance(x, list) or not isinstance(y, list) or len(x) != len(z[0]) or len(y) != len(z):
        raise ValueError('axis label counts do not match matrix')
    return {'schema': 'ironmate-image-studio/1', 'width': 1280, 'height': 720, 'background': '#FFFFFF',
            'layers': [{'id': 'heatmap', 'kind': 'heatmap', 'name': 'Heatmap', 'x': 80, 'y': 90,
                        'w': 1120, 'h': 520, 'rotation': 0, 'opacity': 1,
                        'z': z, 'xlabels': x, 'ylabels': y, 'low': low, 'high': high,
                        'levels': 0, 'labels': True}], 'source': source}


HEATMAP_JS = r"""  function heatColor(v, lo, hi, levels = 0) {
    if (v === null) return "none";
    if (
      ![v, lo, hi].every(Number.isFinite) ||
      lo > hi ||
      !Number.isInteger(levels) ||
      (levels !== 0 && (levels < 2 || levels > 256))
    )
      fail("色の範囲または段階数が不正です");
    let t = hi === lo ? 0.5 : Math.max(0, Math.min(1, (v - lo) / (hi - lo)));
    if (levels) t = Math.round(t * (levels - 1)) / (levels - 1);
    const p = t * 4,
      i = Math.min(3, Math.floor(p));
    const a = PALETTE[i].match(/\w\w/g).map((x) => parseInt(x, 16));
    const b = PALETTE[i + 1].match(/\w\w/g).map((x) => parseInt(x, 16));
    return (
      "#" +
      a
        .map((x, j) =>
          Math.round(x + (b[j] - x) * (p - i))
            .toString(16)
            .padStart(2, "0"),
        )
        .join("")
        .toUpperCase()
    );
  }
  function matrix(source) {
    let t;
    if (Array.isArray(source)) t = { z: source };
    else if (Array.isArray(source?.data)) {
      const traces = source.data.filter((t) => t?.type === "heatmap");
      if (traces.length !== 1) fail("heatmapトレースは1つにしてください");
      t = traces[0];
    } else t = source;
    const z = t?.z,
      cols = z?.[0]?.length;
    if (
      !Array.isArray(z) ||
      !cols ||
      z.length * cols > 4096 ||
      z.some((r) => !Array.isArray(r) || r.length !== cols)
    )
      fail("1〜4096セルの長方形の数値行列が必要です");
    const values = z.flat().filter((v) => v !== null);
    if (
      values.some(
        (v) =>
          !Number.isFinite(v) ||
          (Number.isInteger(v) && !Number.isSafeInteger(v)),
      )
    )
      fail("有限の数値またはnullを指定してください（巨大な整数は非対応）");
    const low = t.zmin ?? (values.length ? Math.min(...values) : 0),
      high = t.zmax ?? (values.length ? Math.max(...values) : 1);
    if (
      [low, high].some(
        (v) =>
          !Number.isFinite(v) ||
          (Number.isInteger(v) && !Number.isSafeInteger(v)),
      )
    )
      fail("色の範囲には有限の安全な数値を指定してください");
    heatColor(low, low, high);
    const xlabels = t.x ?? Array.from({ length: cols }, (_, i) => i),
      ylabels = t.y ?? Array.from({ length: z.length }, (_, i) => i);
    if (
      !Array.isArray(xlabels) ||
      !Array.isArray(ylabels) ||
      xlabels.length !== cols ||
      ylabels.length !== z.length
    )
      fail("軸ラベルの数が一致しません");
    return {
      z: clone(z),
      xlabels: clone(xlabels),
      ylabels: clone(ylabels),
      low,
      high,
      levels: 0,
      labels: true,
    };
  }
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="📈 記録された結果を HTML（と SVG）にする。判定はやり直さない。"
                    " RESULTS がディレクトリでなければ 🔢 HTML の要素を数える（ブラウザなし）。",
    )
    parser.add_argument("--structure-graph", metavar="JSON", help="SSIS原子座標の回転可能な3D HTMLを標準出力へ。- は標準入力")
    parser.add_argument("--heatmap", metavar="JSON", help="行列またはPlotly JSONを編集用シーンとして標準出力に書く。- は標準入力")
    parser.add_argument("results", nargs="?",
                        help="📂 season.jsonl と propositions.jsonl があるディレクトリ。🔢 HTML ファイルか - なら要素を数える（省略は標準入力）")
    parser.add_argument("--results", dest="legacy_results", type=Path, help="RESULTS の旧形式（互換用）")
    parser.add_argument("--overlap-backend", choices=("stdlib", "native"), default=None,
                        help="既定は RESULTS なら stdlib、旧 --results なら native（NumPy/Polars が必要）")
    parser.add_argument("--out", type=Path,
                        help="出力ディレクトリ。省略時は新しい一時ディレクトリ（--ffss は build/ffss）")
    parser.add_argument("--id", action="append", dest="ids", help="この命題だけ。繰り返せる。省略すると全部")
    parser.add_argument("--column", default="wins_vs_pythag", help="球団×年に置く数値列。既定は wins_vs_pythag")
    parser.add_argument(
        "--team-order",
        default="",
        help="球団×年で上から並べる球団の記号（カンマ区切り）。例: d,g,s 。省略すると記号順",
    )
    parser.add_argument(
        "--cond",
        action="append",
        dest="conds",
        help="重なりの条件。col,op,値（JSON）。例: rd,>,0 。繰り返せる（B クラスを含めて 2〜8 個）。省略すると if の先頭2件と B クラス",
    )
    parser.add_argument(
        "--breakdown",
        default="team",
        help="重なりの内訳を分ける列。team、team_name、league、season、upper_half のどれか。既定は team",
    )
    parser.add_argument(
        "--breakdown-keep",
        action="append",
        default=[],
        help="内訳で「その他」にまとめず別の色で残す値。繰り返せる。例: d（件数にかかわらず残す）",
    )
    parser.add_argument("--svg", action="store_true", help="🖼️ SVG も書く（親の plotly_min、Chrome なし）。既定では HTML だけ")
    parser.add_argument(
        "--embed",
        action="store_true",
        help="index.html に Plotly.js を埋め込む。既定は CDN。propositions.html は Plotly を使わない",
    )
    parser.add_argument("--forms", action="store_true", help="🧾 HTML の代わりに四つの形の 2×2 を文字で出す（--id は 1 つまで）")
    parser.add_argument("--tag", action="append", default=[], help="🔢 数えるタグを絞る。繰り返せる")
    parser.add_argument("--ffss", type=Path, metavar="RECORDS",
                        help="📊 FFSS の --jsonl の記録から ffss.html と svg/F<NN>_*.svg を書く（Chrome なし）")
    parser.add_argument("--no-svg", action="store_true", help="📊 --ffss で HTML だけ")
    return parser


def _write_reports(args) -> int:
    items, present = load_items(args.results)
    season_path = Path(args.results) / "season.jsonl"
    rows = read_jsonl(season_path)
    chosen = select_items(items, present, args.ids)
    conds = finalize_conditions([parse_cond(text) for text in args.conds] if args.conds else None, items, rows)
    overlap = load_overlap(season_path, conds, backend=args.overlap_backend)
    index_html, index_figures = index_body(
        rows, overlap, args.column, team_order(args.team_order), args.breakdown, tuple(args.breakdown_keep)
    )
    prop_html = propositions_body(chosen)
    out = args.out or Path(tempfile.mkdtemp(prefix="dragowing-"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        standalone("DRAgoWing", index_html, plotly=True, embed=args.embed), encoding="utf-8"
    )
    (out / "propositions.html").write_text(standalone("命題の一覧", prop_html), encoding="utf-8")
    print("📦 markdown.py（vendor/markdown）")
    for name, note in (("index.html", f"📊 {', '.join(index_figures)}"), ("propositions.html", f"🧾 {len(chosen)}")):
        print(f"📄 {(out / name).resolve().as_uri()} {(out / name).stat().st_size} B · {note}")
    if args.svg:
        for name, fig in index_figures.items():
            write_svg(fig, out / "svg" / f"{name}.svg")
        print(f"🖼️ {(out / 'svg').resolve().as_uri()} {len(index_figures)} svg")
    return 0


def main(argv=None) -> int:
    """📈 RESULTS → HTML（--svg で SVG）、🧾 --forms、📊 --ffss RECORDS、🔢 HTML ファイル（か標準入力）の要素数。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.structure_graph is not None:
        try:
            raw = sys.stdin.read() if args.structure_graph == "-" else Path(args.structure_graph).read_text(encoding="utf-8")
            figure = structure_figure(json.loads(raw))
            print(standalone("分子の原子座標", figure_block(figure, "structure"), plotly=True, embed=args.embed))
        except (ValueError, KeyError, TypeError, AttributeError, RuntimeError, OSError) as exc:
            parser.exit(1, f"Cannot draw structure graph: {exc}\n")
        return 0
    if args.heatmap is not None:
        try:
            source = sys.stdin.read() if args.heatmap == "-" else Path(args.heatmap).read_text(encoding="utf-8")
            print(json.dumps(heatmap_scene(json.loads(source)), ensure_ascii=False, allow_nan=False))
        except (ValueError, OSError) as exc:
            parser.exit(1, f"{exc}\n")
        return 0
    if args.ffss is not None:
        try:
            written = write_ffss(args.ffss, args.out or Path("build/ffss"), svg=not args.no_svg)
        except (OSError, ValueError, KeyError) as exc:
            parser.exit(1, f"Cannot draw FFSS records: {exc}\n")
        for path in written:
            print(f"{'🖼️' if path.suffix == '.svg' else '📄'} {path.resolve().as_uri()} {path.stat().st_size} B")
        return 0
    counting = args.results == "-" or (
        args.results is not None and Path(args.results).suffix.lower() in (".html", ".htm", ".xhtml")
    ) or (args.results is None and args.legacy_results is None and bool(args.tag))
    if counting:
        try:
            html_text = sys.stdin.read() if args.results in (None, "-") else Path(args.results).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            parser.exit(1, f"Cannot read HTML: {exc}\n")
        print(json.dumps(count_elements(html_text, tuple(tag.lower() for tag in args.tag)), ensure_ascii=False, sort_keys=True))
        return 0
    if args.results is not None and args.legacy_results is not None:
        parser.error("RESULTS と --results は同時に指定できません")
    if args.results is None and args.legacy_results is None:
        parser.error("RESULTS または --results が必要です（🔢 HTML を数えるなら PAGE.html か -、📊 FFSS は --ffss）")
    if args.legacy_results is not None and args.overlap_backend is None:
        args.overlap_backend = "native"
    args.results = Path(args.results) if args.results is not None else args.legacy_results
    if args.overlap_backend is None:
        args.overlap_backend = "stdlib"
    try:
        if args.forms:
            if args.ids and len(args.ids) > 1:
                parser.error("--forms の --id は 1 つまで")
            print(forms_text(args.results, args.ids[0] if args.ids else None))
            return 0
        return _write_reports(args)
    except (FileNotFoundError, ValueError, TypeError, ModuleNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
