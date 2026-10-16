"""HTML。既定は出力先の plotly.min.js を1つ参照する。文章は Markdown から作る。"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

import markdown
from plotly.offline import get_plotlyjs

from .figures import four_forms_figure, heatmap_figure, overlap_figure, trajectory_figure
from .forms import render_logic

_STYLE = """
body { margin: 1.5rem auto; max-width: 1100px; color: #1a1a1a; background: #fff;
  font-family: "Noto Sans JP", "Yu Gothic", Meiryo, sans-serif; line-height: 1.5; }
h1, h2 { font-weight: 650; }
a { color: #0b57d0; }
pre { white-space: pre-wrap; background: #f7f7f7; padding: 0.8rem 1rem; }
article.card { border: 1px solid #ccc; padding: 0.75rem 1rem; margin: 0.7rem 0; }
table { border-collapse: collapse; margin: 0.4rem 0 1rem; }
td, th { border: 1px solid #ddd; padding: 0.15rem 0.45rem; vertical-align: top; text-align: left; }
caption { text-align: left; font-weight: 650; padding-bottom: 0.25rem; }
.figure { min-height: 480px; }
.provenance { color: #333; }
"""

_MD = ["tables", "fenced_code", "attr_list", "md_in_html"]
PLOTLY_JS_NAME = "plotly.min.js"

_INDEX_MD = """\
入力ファイル: `season.jsonl`, `propositions.jsonl`。値は記録のまま。
{: .provenance}

## 得点順位 × 失点順位

@@TRAJECTORY@@

## 球団 × 年（`@@COLUMN@@`）

@@HEATMAP@@

## 条件集合の重なり

@@OVERLAP@@

@@UNITS@@

[命題ごとの四つの形と反例カード](propositions.html)
"""

_PROPOSITIONS_MD = """\
入力ファイル: `propositions.jsonl`。値は記録のまま。
{: .provenance}

[球団年の図へ](index.html)
"""


def render_md(source: str) -> str:
    return markdown.markdown(source, extensions=_MD)


def plotlyjs_path() -> Path:
    import plotly

    path = Path(plotly.__file__).resolve().parent / "package_data" / PLOTLY_JS_NAME
    if not path.is_file():
        raise FileNotFoundError(f"plotly.min.js が無い: {path}")
    return path


def copy_plotlyjs(directory: Path) -> Path:
    """インストールされた Plotly の plotly.min.js を出力ディレクトリへコピーする。"""
    dest = Path(directory) / PLOTLY_JS_NAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copyfile(plotlyjs_path(), dest)
    return dest


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


def json_attr(value) -> str:
    return html.escape(json.dumps(value, ensure_ascii=False, allow_nan=False), quote=True)


def spec_from(page: str, div_id: str) -> dict:
    marker = f'id="{div_id}-data">'
    start = page.index(marker) + len(marker)
    end = page.index("</script>", start)
    return json.loads(page[start:end])


def figure_block(fig, div_id: str) -> str:
    payload = embed_json(fig.to_dict())
    return (
        f'<div id="{html.escape(div_id)}" class="figure"></div>\n'
        f'<script type="application/json" id="{html.escape(div_id)}-data">{payload}</script>\n'
        "<script>\n"
        "(function(){\n"
        f'  var spec = JSON.parse(document.getElementById("{div_id}-data").textContent);\n'
        f'  Plotly.newPlot("{div_id}", spec.data, spec.layout, {{responsive:true,displaylogo:false}});\n'
        "})();\n"
        "</script>"
    )


def standalone(title: str, body: str, *, embed: bool = False) -> str:
    """HTML 文書。embed のとき Plotly.js をこのファイルに入れる。"""
    if embed:
        script = f"<script>window.PlotlyConfig = {{MathJaxConfig: 'local'}};</script>\n<script>{get_plotlyjs()}</script>"
    else:
        script = (
            "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
            f'<script charset="utf-8" src="{PLOTLY_JS_NAME}"></script>'
        )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{_STYLE}</style>\n"
        f"{script}\n"
        "</head>\n"
        "<body>\n"
        f"<h1>{html.escape(title)}</h1>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


def _span(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, allow_nan=False)
    return f'<span data-json="{json_attr(value)}">{html.escape(raw)}</span>'


def _md_table(caption: str, mapping) -> str:
    pairs = list(mapping.items()) if isinstance(mapping, dict) else [("value", mapping)]
    lines = [caption, "", "| | |", "| --- | --- |"]
    for key, value in pairs:
        lines.append(f"| {key} | {_span(value)} |")
    return "\n".join(lines)


def cards_md(item: dict) -> str:
    """C7. カード1枚を Markdown の article にする。値は data-json のまま。"""
    blocks = []
    stored = 0
    for form in item.get("forms") or []:
        if not isinstance(form, dict):
            continue
        form_name = str(form.get("form") or "")
        for card in form.get("counterexamples") or []:
            if not isinstance(card, dict):
                continue
            stored += 1
            unit = str(card.get("unit", ""))
            bits = [
                (
                    f'<article class="card" markdown="1" data-id="{html.escape(str(item.get("id") or ""))}" '
                    f'data-form="{html.escape(form_name)}" data-unit="{html.escape(unit)}">'
                ),
                "",
                f"### `{form_name}` · `{unit}`",
                "",
            ]
            if "question" in card:
                bits.append(f'<p class="question">question: {html.escape(str(card.get("question") or ""))}</p>')
                bits.append("")
            bits.append(_md_table("values", card.get("values") or {}))
            bits.append("")
            bits.append(_md_table("context", card.get("context") or {}))
            for key in ("season", "team", "team_name", "focus"):
                if key in card:
                    bits.append("")
                    bits.append(
                        f'<p class="identity" data-key="{html.escape(key)}">{html.escape(key)}: {_span(card[key])}</p>'
                    )
            bits.append("")
            bits.append("</article>")
            blocks.append("\n".join(bits))
    return f"counterexamples: {stored}\n\n" + "\n\n".join(blocks)


def cards_html(item: dict) -> str:
    return render_md(cards_md(item))


def proposition_section(item: dict) -> tuple[str, object]:
    ident = str(item.get("id") or "")
    figure = four_forms_figure(item)
    label = figure.layout.meta["registration"]
    parts = [f"## ［{label}］ {ident} {{#{ident}}}", ""]
    if isinstance(item.get("statement"), str):
        parts.append(f'<p class="statement">statement: {html.escape(item["statement"])}</p>')
        parts.append("")
    parts.append("```")
    parts.append(render_logic(item))
    parts.append("```")
    parts.append("")
    parts.append(figure_block(figure, f"forms-{ident}"))
    parts.append("")
    parts.append(cards_md(item))
    return render_md("\n".join(parts)), figure


def overlap_table(overlap: dict) -> str:
    conds = overlap["conditions"]
    columns = overlap["columns"]
    head = ["unit", "team_name", "league", "season", "upper_half"]
    head += [f"in:{cond['label']}" for cond in conds]
    head += [f"value:{col}" for col in columns]
    rows = ["<tr>" + "".join(f"<th>{html.escape(name)}</th>" for name in head) + "</tr>"]
    for unit in overlap["units"]:
        cells = [
            unit["unit"],
            unit["team_name"],
            unit["league"],
            unit["season"],
            unit["upper_half"],
        ]
        cells.extend(unit["in_set"])
        cells.extend(unit["values"][col] for col in columns)
        body = []
        for name, value in zip(head, cells):
            body.append(
                f'<td data-col="{html.escape(name)}" data-json="{json_attr(value)}">{html.escape(json.dumps(value, ensure_ascii=False, allow_nan=False))}</td>'
            )
        rows.append(f'<tr data-unit="{html.escape(unit["unit"])}">' + "".join(body) + "</tr>")
    return '<table class="overlap-units"><caption>units</caption>' + "".join(rows) + "</table>"


def index_body(rows: list[dict], overlap: dict, column: str) -> tuple[str, dict]:
    trajectory = trajectory_figure(rows)
    heat = heatmap_figure(rows, column)
    venn = overlap_figure(overlap)
    source = (
        _INDEX_MD.replace("@@COLUMN@@", column)
        .replace("@@TRAJECTORY@@", figure_block(trajectory, "trajectory"))
        .replace("@@HEATMAP@@", figure_block(heat, "heatmap"))
        .replace("@@OVERLAP@@", figure_block(venn, "overlap"))
        .replace("@@UNITS@@", overlap_table(overlap))
    )
    return render_md(source), {"trajectory": trajectory, "heatmap": heat, "overlap": venn}


def propositions_body(items: list[dict]) -> tuple[str, dict]:
    parts = [render_md(_PROPOSITIONS_MD)]
    figures = {}
    for item in items:
        section, figure = proposition_section(item)
        parts.append(section)
        figures[str(item.get("id"))] = figure
    return "\n".join(parts), figures
