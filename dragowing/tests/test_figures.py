"""図のデータは season.jsonl / propositions.jsonl の値と一致する。丸めない。"""
import ast
import html
import json
import operator
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dragowing.cli import PngUnavailable, main, write_png
from dragowing.figures import A_COLOR, B_COLOR, heatmap_figure, trajectory_figure
from dragowing.forms import FORM_LABEL, _cell, _form_cell, contingency, format_contingency_cell
from dragowing.htmlout import embed_json, figure_block, heatmap_note, overlap_md, proposition_section, propositions_body, render_md, spec_from, standalone
from vendor import web_ui
from dragowing.plotly_cdn import PLOTLY_JS_CDN, fetch_plotly_js, reset_plotly_js_cache
from dragowing.overlap import default_conditions, load_overlap
from dragowing.records import read_jsonl
from ask import registration_status

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "cycles" / "c001-chunichi" / "outputs"
OPS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


def spec_of(spec: dict) -> dict:
    return json.loads(embed_json(spec))


def shown(value) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return html.escape(text, quote=False)


def holds(row, cond) -> bool:
    value = row.get(cond["col"])
    if value is None:
        return False
    return bool(OPS[cond["op"]](value, cond["value"]))


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def proposition(**extra):
    base = {
        "id": "P9",
        "statement": "記録された文",
        "if": [{"col": "rd", "op": ">", "value": 0}],
        "if_any": [],
        "then": [{"col": "upper_half", "op": "==", "value": True}],
        "forms": [
            {
                "form": "original",
                "n": 5,
                "hold": 3,
                "rate": 0.6,
                "counterexamples": [
                    {
                        "unit": "d-2012",
                        "season": 2012,
                        "team": "d",
                        "team_name": "中日",
                        "focus": True,
                        "values": {"rd": 18, "upper_half": False},
                        "context": {"rank": 2, "rank_pythag": 2, "wins_vs_pythag": 8.4548548226457},
                        "surprise": 3,
                        "question": "中日 2012 は条件を満たすのに後件を満たさない。なぜか？",
                    }
                ],
            }
        ],
    }
    base.update(extra)
    return base


def season_row(**extra):
    base = {
        "season": 2012,
        "team": "d",
        "team_name": "中日",
        "league": "C",
        "rank_rf": 4,
        "rank_ra": 2,
        "upper_half": True,
        "wins_vs_pythag": 8.4548548226457,
        "rd": 18,
        "rank_pythag": 2,
    }
    base.update(extra)
    return base


def test_registration_labels_are_on_the_proposition_section():
    cases = [
        ({"posthoc": True}, "事後構成"),
        ({"preregistered": True}, "事前登録"),
        ({}, "不明"),
    ]
    for extra, label in cases:
        item = proposition(**extra)
        assert registration_status(item) == label
        page = proposition_section(item)
        assert f"［{label}］ P9" in page
        assert 'id="P9"' in page
        assert contingency(item) == {"P∧Q": 3, "P∧¬Q": 2, "¬P∧Q": None, "¬P∧¬Q": None}
        assert ">3<" in page and ">2<" in page
        assert "不明" in page


def test_disagreement_stays_a_string_and_listed_cards_are_not_the_count():
    item = proposition()
    item["forms"] = [
        {"form": "original", "n": 5, "hold": 3, "rate": 0.6, "counterexamples": [{"unit": "only-one", "values": {"rd": 1}, "context": {}, "question": "q"}]},
        {"form": "converse", "n": 9, "hold": 9, "rate": 1},
        {"form": "inverse", "n": 5, "hold": 4},
        {"form": "contrapositive", "n": 6, "hold": 4},
    ]
    assert str(contingency(item)["P∧Q"]).startswith("不一致")
    page = proposition_section(item)
    assert "不一致" in page
    assert "only-one" in page
    assert "3/5（反例 2）" in page
    assert "（1 行）" in page
    assert "同じ単位の並び" not in page
    assert "data-json" not in page
    summary = propositions_body([item])
    first = summary.split("</table>", 1)[0]
    assert '<a href="#P9">P9</a>' in first
    assert ">3<" in first and ">2<" in first and "0.6" in first
    assert "only-one" not in first
    assert summary.index("</table>") < summary.index("<h2")


def test_trajectory_and_heatmap_keep_source_values_including_a_gap():
    rows = [
        season_row(),
        season_row(season=2014, rank_rf=1, rank_ra=6, upper_half=False, wins_vs_pythag=-1.678984877580291),
        season_row(team="g", team_name="巨人", season=2012, rank_rf=1, rank_ra=1, upper_half=True, wins_vs_pythag=0),
    ]
    spec = spec_of(trajectory_figure(rows))
    traces = [trace for trace in spec["data"] if (trace.get("meta") or {}).get("role") == "trajectory"]
    dragons = next(trace for trace in traces if trace["meta"]["team"] == "d")
    assert dragons["x"] == [4, 1]
    assert dragons["y"] == [2, 6]
    assert dragons["line"]["shape"] == "linear"
    assert dragons["connectgaps"] is False
    assert [point["season"] for point in dragons["customdata"]] == [2012, 2014]
    assert [point["upper_half"] for point in dragons["customdata"]] == [True, False]
    assert dragons["marker"]["color"] == [A_COLOR, B_COLOR]
    assert "spline" not in json.dumps(spec)
    assert "trendline" not in json.dumps(spec)
    heat = spec_of(heatmap_figure(rows, "wins_vs_pythag"))
    payload = heat["data"][0]
    assert payload["zsmooth"] is False
    x, y, z = payload["x"], payload["y"], payload["z"]
    assert x == [2012, 2014]
    assert y[0] == "d"
    assert heat["layout"]["yaxis"]["categoryarray"][-1] == "d"
    assert heat["layout"]["title"]["text"] == "球団 × 年"
    i = y.index("d")
    assert z[i][x.index(2012)] == 8.4548548226457
    assert z[i][x.index(2014)] == -1.678984877580291
    assert z[y.index("g")][x.index(2014)] is None
    assert payload["text"][i][x.index(2012)] == "A"
    assert payload["text"][i][x.index(2014)] == "B"
    assert payload["text"][y.index("g")][x.index(2014)] == ""
    assert set("".join(cell for row in payload["text"] for cell in row)) <= set("AB")
    cell = payload["customdata"][i][x.index(2012)]
    assert cell["value"] == 8.4548548226457
    assert cell["value_text"] == "8.4548548226457"
    assert cell["class"] == "A"
    assert cell["team"] == "d"
    assert cell["season"] == 2012
    assert cell["rank_text"] == "null"
    assert "upper_half" not in payload["hovertemplate"]
    assert "8.4548548226457" not in "".join(payload["text"][i])
    assert heat["layout"]["meta"]["marks"][i][x.index(2014)] == "B"
    assert heat["layout"]["meta"]["marks"][i][x.index(2012)] == "A"
    assert heat["data"][0]["zmin"] == min(v for row in heat["data"][0]["z"] for v in row if v is not None)
    assert heat["data"][0]["zmax"] == max(v for row in heat["data"][0]["z"] for v in row if v is not None)


def test_overlap_file_uses_the_numpy_mask_without_filling_nulls(tmp_path):
    rows = [
        season_row(team="a", team_name="A", season=2012, rd=1, rank_pythag=1, upper_half=False),
        season_row(team="b", team_name="B", season=2012, rd=1, rank_pythag=5, upper_half=True),
        season_row(team="c", team_name="C", season=2012, rd=None, rank_pythag=1, upper_half=False),
        season_row(team="e", team_name="E", season=2012, rd=-3, rank_pythag=9, upper_half=True),
    ]
    path = tmp_path / "season.jsonl"
    dump_jsonl(path, rows)
    conds = [
        {"col": "rd", "op": ">", "value": 0},
        {"col": "rank_pythag", "op": "<=", "value": 3},
        {"col": "upper_half", "op": "==", "value": False},
    ]
    overlap = load_overlap(path, conds)
    import polars as pl
    import rule_search

    frame = pl.read_ndjson(path)
    matrix = rule_search._masks_to_matrix([rule_search._mask(frame, [cond]) for cond in conds], frame.height)
    assert overlap["matrix"] == [[bool(matrix[i, j]) for j in range(len(rows))] for i in range(3)]
    for unit in overlap["units"]:
        row = rows[unit["index"]]
        assert unit["in_set"] == [holds(row, cond) for cond in conds]
        assert unit["values"]["rd"] == row["rd"]
        assert unit["unit"] == f"{row['team']}-{row['season']}"
    assert sum(region["count"] for region in overlap["regions"]) == len(rows)
    named = {unit["unit"] for unit in overlap["units"] if unit["in_set"] == [True, True, True]}
    assert named == {"a-2012"}
    page = render_md(overlap_md(overlap))
    assert '"type":"circle"' not in page
    assert "円は描かない" in page
    for region in overlap["regions"]:
        assert shown(region["name"]) in page
        assert f"<td>{region['count']}</td>" in page
    assert "<td>null</td>" in page
    assert "a-2012" in page


def test_counterexample_table_copies_values_context_and_question():
    item = proposition(posthoc=True)
    card = item["forms"][0]["counterexamples"][0]
    page = proposition_section(item)
    assert "［事後構成］ P9" in page
    assert shown(card["question"]) in page
    assert shown(card["values"]) in page
    assert shown(card["context"]) in page
    assert "8.4548548226457" in page
    assert "rate=0.6" in page
    assert _form_cell(item["forms"][0]) in page
    assert "data-json" not in page
    assert "<article" not in page
    assert "<details>" in page
    assert "<details open" not in page
    assert "<th>links</th>" not in page
    assert "surprise" in page
    assert "Plotly.newPlot" not in page


def test_cli_writes_standalone_html_and_png_needs_chrome(tmp_path, monkeypatch):
    results = tmp_path / "results"
    results.mkdir()
    dump_jsonl(
        results / "season.jsonl",
        [season_row(), season_row(season=2013, team="g", team_name="巨人", rank_rf=2, rank_ra=3, upper_half=False, rd=-1, rank_pythag=4, wins_vs_pythag=-0.5)],
    )
    dump_jsonl(results / "propositions.jsonl", [proposition(posthoc=True)])
    out = tmp_path / "html"
    assert main(["--results", str(results), "--out", str(out), "--id", "P9"]) == 0
    index = (out / "index.html").read_text(encoding="utf-8")
    props = (out / "propositions.html").read_text(encoding="utf-8")
    assert not (out / "plotly.min.js").exists()
    assert web_ui.remote_script_tag(PLOTLY_JS_CDN) in index
    head = index.split("</head>", 1)[0]
    assert head.count("<script") == 2
    assert index.count("Plotly.newPlot") == 2
    assert '"type":"circle"' not in index
    assert "8.4548548226457" in index
    assert "zmin=" in index and "zmax=" in index
    assert "<h2>球団 × 年" in index
    assert "Plotly.newPlot" not in props
    assert "cdn.plot.ly" not in props
    assert "［事後構成］ P9" in props
    assert "なぜか？" in props
    assert '<a href="#P9">P9</a>' in props
    assert props.index("<table") < props.index("<h2")
    embedded = tmp_path / "embedded"
    reset_plotly_js_cache()
    embed_body = b"window.Plotly=" + b"e" * 200
    import hashlib
    monkeypatch.setattr(web_ui, "PLOTLY_JS_SHA256", hashlib.sha256(embed_body).hexdigest())
    embed_response = MagicMock()
    embed_response.read.return_value = embed_body
    embed_response.status = 200
    embed_response.getcode.return_value = 200
    embed_response.__enter__.return_value = embed_response
    embed_response.__exit__.return_value = False
    with patch("urllib.request.urlopen", return_value=embed_response):
        assert main(["--results", str(results), "--out", str(embedded), "--id", "P9", "--embed"]) == 0
    alone = (embedded / "index.html").read_text(encoding="utf-8")
    assert "src=\"plotly.min.js\"" not in alone
    assert PLOTLY_JS_CDN not in alone
    assert fetch_plotly_js()[:80] in alone
    assert not (embedded / "plotly.min.js").exists()
    embedded_props = (embedded / "propositions.html").read_text(encoding="utf-8")
    assert fetch_plotly_js()[:80] not in embedded_props
    proc = subprocess.run(
        [sys.executable, "-m", "dragowing", "--results", str(results), "--out", str(tmp_path / "mod"), "--id", "P9"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "mod" / "index.html").is_file()
    monkeypatch.setenv("CHROME", str(tmp_path / "missing-chrome"))
    with pytest.raises(PngUnavailable, match="Chrome"):
        write_png(heatmap_figure([season_row()], "wins_vs_pythag"), tmp_path / "x.png")
    assert not (tmp_path / "x.png").exists()
    missing = subprocess.run(
        [sys.executable, "-m", "dragowing", "--results", str(results), "--out", str(tmp_path / "png"), "--png"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**dict(__import__("os").environ), "CHROME": str(tmp_path / "missing-chrome")},
    )
    assert missing.returncode == 2
    assert "Chrome" in missing.stderr
    assert (tmp_path / "png" / "index.html").is_file()


def test_cli_refuses_a_missing_expression_file_and_a_text_column(tmp_path):
    results = tmp_path / "results"
    results.mkdir()
    dump_jsonl(results / "season.jsonl", [season_row()])
    dump_jsonl(results / "propositions.jsonl", [proposition()])
    assert main(["--results", str(results), "--out", str(tmp_path / "o"), "--id", "E25"]) == 1
    proc = subprocess.run(
        [sys.executable, "-m", "dragowing", "--results", str(results), "--out", str(tmp_path / "o2"), "--id", "E25"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "結果が読めない" in proc.stderr
    assert "結果にない" not in proc.stderr
    proc = subprocess.run(
        [sys.executable, "-m", "dragowing", "--results", str(results), "--out", str(tmp_path / "o3"), "--column", "team_name"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "数値ではない" in proc.stderr


def test_real_records_are_copied_into_the_figures():
    rows = read_jsonl(RESULTS / "season.jsonl")
    items = [json.loads(line) for line in (RESULTS / "propositions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    spec = spec_of(trajectory_figure(rows))
    traces = [trace for trace in spec["data"] if (trace.get("meta") or {}).get("role") == "trajectory"]
    seen = {}
    for trace in traces:
        assert trace["line"]["shape"] == "linear"
        for point, x, y, color in zip(trace["customdata"], trace["x"], trace["y"], trace["marker"]["color"]):
            seen[(point["league"], point["team"], point["season"])] = point
            assert point["rank_rf"] == x and point["rank_ra"] == y
            assert color == (A_COLOR if point["upper_half"] is True else B_COLOR)
    assert len(seen) == len(rows) == 168
    for row in rows:
        point = seen[(row["league"], row["team"], row["season"])]
        assert point["rank_rf"] == row["rank_rf"]
        assert point["rank_ra"] == row["rank_ra"]
        assert point["upper_half"] is row["upper_half"]
        assert point["team_name"] == row["team_name"]
    heat = spec_of(heatmap_figure(rows, "wins_vs_pythag"))
    payload = heat["data"][0]
    assert payload["zsmooth"] is False
    assert payload["y"][0] == "d"
    assert heat["layout"]["yaxis"]["categoryarray"][-1] == "d"
    assert heat["layout"]["title"]["text"] == "球団 × 年"
    assert payload["y"] == ["d", "g", "s", "db", "t", "c", "h", "f", "b", "e", "l", "m"]
    assert "upper_half" not in payload["hovertemplate"]
    index = {(row["league"], row["team"], row["season"]): row for row in rows}
    for i, team in enumerate(payload["y"]):
        for j, season in enumerate(payload["x"]):
            row = next(item for item in rows if item["team"] == team and item["season"] == season)
            assert index[(row["league"], team, season)] is row
            assert payload["z"][i][j] == row["wins_vs_pythag"]
            assert heat["layout"]["meta"]["z"][i][j] == row["wins_vs_pythag"]
            mark = "A" if row["upper_half"] is True else "B" if row["upper_half"] is False else ""
            assert payload["text"][i][j] == mark
            assert heat["layout"]["meta"]["marks"][i][j] == mark
            hover = payload["customdata"][i][j]
            assert hover["value"] == row["wins_vs_pythag"]
            assert hover["value_text"] == json.dumps(row["wins_vs_pythag"])
            assert hover["rank"] == row["rank"]
            assert hover["rank_text"] == json.dumps(row["rank"])
            assert hover["class"] == mark
            assert hover["team"] == row["team"]
            assert hover["season"] == row["season"]
            assert json.dumps(row["wins_vs_pythag"]) not in payload["text"][i][j]
    dragons = next(row for row in rows if row["team"] == "d" and row["season"] == 2012)
    assert dragons["wins_vs_pythag"] == 8.4548548226457
    assert round(dragons["wins_vs_pythag"], 4) != dragons["wins_vs_pythag"]
    conds = default_conditions(items, rows)
    assert conds == [
        {"col": "rd", "op": ">", "value": 0},
        {"col": "rank_pythag", "op": "<=", "value": 3},
        {"col": "upper_half", "op": "==", "value": False},
    ]
    overlap = load_overlap(RESULTS / "season.jsonl", conds)
    assert sum(region["count"] for region in overlap["regions"]) == 168
    for unit in overlap["units"]:
        row = rows[unit["index"]]
        assert unit["in_set"] == [holds(row, cond) for cond in conds]
        for col, value in unit["values"].items():
            assert value == row[col]
    p1 = items[0]
    assert p1["id"] == "P1"
    form = p1["forms"][0]
    cells = contingency(p1)
    assert cells["P∧Q"] == form["hold"]
    assert cells["P∧¬Q"] == form["n"] - form["hold"]
    assert registration_status(p1) == "不明"
    page = proposition_section(p1)
    assert _form_cell(form) in page
    assert "rate=" + json.dumps(form["rate"], ensure_ascii=False) in page
    card = form["counterexamples"][0]
    assert shown(card["question"]) in page
    assert shown(card["context"]) in page
    assert shown(card["values"]) in page
    assert "同じ単位の並び" in page
    assert "data-json" not in page
    p6 = next(row for row in items if row["id"] == "P6")
    assert "0（前件が空）" in proposition_section(p6)


def test_cli_on_the_recorded_cycle_writes_standalone_html(tmp_path):
    out = tmp_path / "out"
    assert main(["--results", str(RESULTS), "--out", str(out), "--id", "P1"]) == 0
    index = (out / "index.html").read_text(encoding="utf-8")
    props = (out / "propositions.html").read_text(encoding="utf-8")
    assert web_ui.remote_script_tag(PLOTLY_JS_CDN) in index
    assert not (out / "plotly.min.js").exists()
    assert index.count("Plotly.newPlot") == 2
    assert '"type":"circle"' not in index
    heat = spec_from(index, "heatmap")
    assert any(cell == 8.4548548226457 for row in heat["data"][0]["z"] for cell in row)
    assert 'id="P1"' in props
    assert 'id="P2"' not in props
    assert "［不明］ P1" in props
    assert '<a href="#P1">P1</a>' in props
    assert "Plotly.newPlot" not in props


def test_every_proposition_table_matches_the_file():
    items = [json.loads(line) for line in (RESULTS / "propositions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(items) == 114
    page = propositions_body(items)
    assert page.index("<table") < page.index("<h2")
    assert "<details open" not in page
    assert "data-json" not in page
    assert "<article" not in page
    assert "Plotly.newPlot" not in page
    assert "同じ単位の並び" in page
    assert "<th>links</th>" not in page
    assert "除外した反例" in page
    assert page.count("held_out の再確認") == 8
    assert "surprise" in page
    first = page.split("</table>", 1)[0]
    p1 = items[0]
    original = p1["forms"][0]
    assert shown(p1["statement"]) in first
    assert shown(original["hold"]) in first
    assert shown(original["n"] - original["hold"]) in first
    assert shown(original["rate"]) in first
    for item in items:
        assert f'id="{item["id"]}"' in page
        assert f'href="#{item["id"]}"' in page
        assert registration_status(item) in page
        if isinstance(item.get("statement"), str):
            assert shown(item["statement"]) in page
        for key in ("P∧Q", "P∧¬Q", "¬P∧Q", "¬P∧¬Q"):
            assert shown(format_contingency_cell(item, key)) in page
        for form in item["forms"]:
            assert _form_cell(form) in page
            if "rate" in form:
                assert "rate=" + json.dumps(form["rate"], ensure_ascii=False) in page
            for card in form.get("counterexamples") or []:
                if not isinstance(card, dict):
                    continue
                assert shown(card["unit"]) in page
                assert shown(card["question"]) in page
                assert shown(card["values"]) in page
                assert shown(card["context"]) in page
                if "surprise" in card:
                    assert shown(card["surprise"]) in page
        for card in item.get("excluded_counterexamples") or []:
            if isinstance(card, dict):
                assert shown(card["unit"]) in page


def test_sources_do_not_import_banned_plot_libraries():
    banned_roots = {"matplotlib", "seaborn", "statsmodels", "plotly"}
    for path in (ROOT / "dragowing").rglob("*.py"):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            for module in modules:
                root = module.split(".")[0]
                assert root not in banned_roots
                assert module != "kaleido"
        text = path.read_text(encoding="utf-8")
        for word in ("trendline", "lowess", "spline"):
            assert word not in text


def test_spec_from_html_roundtrip_matches_the_figure():
    fig = heatmap_figure([season_row()], "wins_vs_pythag")
    page = standalone("t", figure_block(fig, "heatmap"), plotly=True)
    parsed = spec_from(page, "heatmap")
    assert parsed["data"][0]["z"] == spec_of(fig)["data"][0]["z"]


def test_figure_script_keeps_ids_inside_a_javascript_string():
    fig = heatmap_figure([season_row()], "wins_vs_pythag")
    block = figure_block(fig, 'x");alert(1)</script><script>alert(2)')
    assert block.count("</script>") == 2
    assert "<script>alert" not in block
    assert "\\u003c/script" in block
