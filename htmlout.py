"""単体 HTML。Plotly.js はページに埋め込む。CDN には出さない。"""
from __future__ import annotations

import html
import json

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


def spec_from(html: str, div_id: str) -> dict:
    marker = f'id="{div_id}-data">'
    start = html.index(marker) + len(marker)
    end = html.index("</script>", start)
    return json.loads(html[start:end])


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
        "</script>\n"
    )


def standalone(title: str, body: str) -> str:
    js = get_plotlyjs()
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{_STYLE}</style>\n"
        f"<script>{js}</script>\n"
        "</head>\n"
        "<body>\n"
        f"<h1>{html.escape(title)}</h1>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )


def _field_table(caption: str, mapping) -> str:
    rows = []
    if isinstance(mapping, dict):
        pairs = list(mapping.items())
    else:
        pairs = [("value", mapping)]
    for key, value in pairs:
        rows.append(
            "<tr>"
            f"<th>{html.escape(str(key))}</th>"
            f"<td data-json=\"{json_attr(value)}\">{html.escape(json.dumps(value, ensure_ascii=False, allow_nan=False))}</td>"
            "</tr>"
        )
    body = "".join(rows)
    return f"<table class=\"{html.escape(caption)}\"><caption>{html.escape(caption)}</caption><tbody>{body}</tbody></table>"


def cards_html(item: dict) -> str:
    """C7. counterexamples の要素を 1 枚ずつ。枚数は配列の長さ。"""
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
                f'<article class="card" data-id="{html.escape(str(item.get("id") or ""))}" '
                f'data-form="{html.escape(form_name)}" data-unit="{html.escape(unit)}">',
                f"<h3>{html.escape(form_name)} · {html.escape(unit)}</h3>",
            ]
            if "question" in card:
                bits.append(f'<p class="question">question: {html.escape(str(card.get("question") or ""))}</p>')
            bits.append(_field_table("values", card.get("values") or {}))
            bits.append(_field_table("context", card.get("context") or {}))
            for key in ("season", "team", "team_name", "focus"):
                if key in card:
                    bits.append(
                        f'<p class="identity" data-key="{html.escape(key)}" data-json="{json_attr(card[key])}">'
                        f"{html.escape(key)}: {html.escape(json.dumps(card[key], ensure_ascii=False, allow_nan=False))}</p>"
                    )
            bits.append("</article>")
            blocks.append("".join(bits))
    head = f'<p class="card-count">counterexamples: {stored}</p>'
    return head + "\n".join(blocks)


def proposition_section(item: dict) -> str:
    ident = str(item.get("id") or "")
    figure = four_forms_figure(item)
    parts = [f'<section id="{html.escape(ident)}">', f"<h2>［{html.escape(figure.layout.meta['registration'])}］ {html.escape(ident)}</h2>"]
    if isinstance(item.get("statement"), str):
        parts.append(f'<p class="statement">statement: {html.escape(item["statement"])}</p>')
    parts.append(f"<pre>{html.escape(render_logic(item))}</pre>")
    parts.append(figure_block(figure, f"forms-{ident}"))
    parts.append(cards_html(item))
    parts.append("</section>")
    return "\n".join(parts), figure


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
            body.append(f'<td data-col="{html.escape(name)}" data-json="{json_attr(value)}">{html.escape(json.dumps(value, ensure_ascii=False, allow_nan=False))}</td>')
        rows.append(f'<tr data-unit="{html.escape(unit["unit"])}">' + "".join(body) + "</tr>")
    return '<table class="overlap-units"><caption>units</caption>' + "".join(rows) + "</table>"


def index_body(rows: list[dict], overlap: dict, column: str) -> tuple[str, dict]:
    trajectory = trajectory_figure(rows)
    heat = heatmap_figure(rows, column)
    venn = overlap_figure(overlap)
    body = "\n".join(
        [
            '<p class="provenance">入力ファイル: season.jsonl, propositions.jsonl。値は記録のまま。</p>',
            "<section>",
            "<h2>得点順位 × 失点順位</h2>",
            figure_block(trajectory, "trajectory"),
            "</section>",
            "<section>",
            f"<h2>球団 × 年（{html.escape(column)}）</h2>",
            figure_block(heat, "heatmap"),
            "</section>",
            "<section>",
            "<h2>条件集合の重なり</h2>",
            figure_block(venn, "overlap"),
            overlap_table(overlap),
            "</section>",
            '<p><a href="propositions.html">命題ごとの四つの形と反例カード</a></p>',
        ]
    )
    return body, {"trajectory": trajectory, "heatmap": heat, "overlap": venn}


def propositions_body(items: list[dict]) -> tuple[str, dict]:
    parts = ['<p class="provenance">入力ファイル: propositions.jsonl。値は記録のまま。</p>', '<p><a href="index.html">球団年の図へ</a></p>']
    figures = {}
    for item in items:
        section, figure = proposition_section(item)
        parts.append(section)
        figures[str(item.get("id"))] = figure
    return "\n".join(parts), figures
