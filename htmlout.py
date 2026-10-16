"""HTML。文章と表は Markdown から作る。Plotly は軌跡と球団×年だけ。"""
from __future__ import annotations

import html
import json
import re

import markdown

from .figures import heatmap_figure, trajectory_figure
from .forms import (
    FORM_LABEL,
    FORM_ORDER,
    _counts,
    _cell,
    _form_cell,
    _forms,
    contingency,
    registration_status,
    render_logic,
)

_STYLE = """
body { margin: 1.5rem auto; max-width: 1100px; color: #1a1a1a; background: #fff;
  font-family: "Noto Sans JP", "Yu Gothic", Meiryo, sans-serif; line-height: 1.5; }
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
"""

_MD = ["tables", "fenced_code", "attr_list", "md_in_html"]
_SAFE_ANCHOR = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
_CARD_FIELDS = ("unit", "season", "team", "team_name", "focus", "surprise", "question", "links", "values", "context")
_SUMMARY_FORMS = (("original", "元"), ("converse", "逆"), ("inverse", "裏"), ("contrapositive", "対偶"))

_INDEX_MD = """\
入力ファイル: `season.jsonl`, `propositions.jsonl`。値は記録のまま。
{: .provenance}

## 得点順位 × 失点順位

@@TRAJECTORY@@

## 球団 × 年（`@@COLUMN@@`）

@@HEATMAP@@

## 条件集合の重なり

@@OVERLAP@@

[命題の一覧](propositions.html)
"""

_AFTER_SUMMARY = """\
入力ファイル: `propositions.jsonl`。`hold` と反例（`n - hold`）は記録の `n` と `hold` から数える。`rate` はファイルの数のまま置く。反例の表の行数は `counterexamples` の長さで、`n - hold` とは別に置く。
{: .provenance}

[球団年の図へ](index.html)
"""


def render_md(source: str) -> str:
    return markdown.markdown(source, extensions=_MD)


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


def figure_block(fig, div_id: str) -> str:
    payload = embed_json(fig.to_dict())
    attr = html.escape(div_id, quote=True)
    js_id = _js_string(div_id)
    return (
        f'<div id="{attr}" class="figure"></div>\n'
        f'<script type="application/json" id="{attr}-data">{payload}</script>\n'
        "<script>\n"
        "(function(){\n"
        f"  var id = {js_id};\n"
        '  var spec = JSON.parse(document.getElementById(id + "-data").textContent);\n'
        "  Plotly.newPlot(id, spec.data, spec.layout, {responsive:true,displaylogo:false});\n"
        "})();\n"
        "</script>"
    )


def plotly_script(*, embed: bool) -> str:
    """軌跡と球団×年用。既定は CDN。embed のとき index.html に Plotly.js を入れる。"""
    from plotly.offline import get_plotlyjs_version

    config = "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
    if embed:
        from plotly.offline import get_plotlyjs

        return config + f"<script>{get_plotlyjs()}</script>"
    src = html.escape(f"https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js", quote=True)
    return config + f'<script charset="utf-8" src="{src}"></script>'


def standalone(title: str, body: str, *, plotly: bool = False, embed: bool = False) -> str:
    """HTML 文書。plotly は軌跡と球団×年のページだけ。"""
    script = plotly_script(embed=embed) + "\n" if plotly else ""
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


def _form_line(name: str, form) -> str:
    text = f"{FORM_LABEL[name]}: {_form_cell(form)}"
    if isinstance(form, dict) and "rate" in form:
        text += " rate=" + exact_json(form.get("rate"))
    return text


def forms_table_md(item: dict) -> str:
    """四つの形。上は P/¬P × Q/¬Q、下は元・逆・裏・対偶の 2×2。どちらも Markdown の表。"""
    cells = contingency(item)
    forms = _forms(item)
    grid = _table(
        ["", "Q", "¬Q"],
        [
            ["P", md_cell(_cell(cells["P∧Q"])), md_cell(_cell(cells["P∧¬Q"]))],
            ["¬P", md_cell(_cell(cells["¬P∧Q"])), md_cell(_cell(cells["¬P∧¬Q"]))],
        ],
    )
    pair = _table(
        ["", ""],
        [
            [md_cell(_form_line("original", forms.get("original"))), md_cell(_form_line("converse", forms.get("converse")))],
            [md_cell(_form_line("inverse", forms.get("inverse"))), md_cell(_form_line("contrapositive", forms.get("contrapositive")))],
        ],
    )
    return grid + "\n\n" + pair


def _card_columns(cards: list[dict]) -> list[str]:
    return [key for key in _CARD_FIELDS if any(key in card for card in cards)]


def counterexamples_md(item: dict) -> str:
    """形ごとに 1 表。1 行が 1 単位。既定では details で畳む。"""
    forms = _forms(item)
    blocks = []
    for name in FORM_ORDER:
        form = forms.get(name)
        cards = [card for card in (form.get("counterexamples") if isinstance(form, dict) else None) or [] if isinstance(card, dict)]
        if not cards:
            continue
        columns = _card_columns(cards)
        rows = []
        for card in cards:
            rows.append([md_cell(card[key]) if key in card else "" for key in columns])
        table = _table(columns, rows)
        blocks.append(
            "\n".join(
                [
                    '<details markdown="1">',
                    f"<summary>{html.escape(FORM_LABEL[name], quote=False)}（{len(cards)} 行）</summary>",
                    "",
                    table,
                    "",
                    "</details>",
                ]
            )
        )
    return "\n\n".join(blocks)


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
    parts.append(forms_table_md(item))
    listed = counterexamples_md(item)
    if listed:
        parts.extend(["", listed])
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


def index_body(rows: list[dict], overlap: dict, column: str) -> tuple[str, dict]:
    trajectory = trajectory_figure(rows)
    heat = heatmap_figure(rows, column)
    source = (
        _INDEX_MD.replace("@@COLUMN@@", md_inline(column))
        .replace("@@TRAJECTORY@@", figure_block(trajectory, "trajectory"))
        .replace("@@HEATMAP@@", figure_block(heat, "heatmap"))
        .replace("@@OVERLAP@@", overlap_md(overlap))
    )
    return render_md(source), {"trajectory": trajectory, "heatmap": heat}
