"""図のデータは season.jsonl / propositions.jsonl の値と一致する。丸めない。"""
import ast
import html
import json
import operator
import subprocess
import sys
from pathlib import Path

import pytest

from dragowing.cli import PngUnavailable, main, write_png
from dragowing.figures import A_COLOR, B_COLOR, four_forms_figure, heatmap_figure, overlap_figure, trajectory_figure
from dragowing.forms import _cell, _form_cell, contingency
from dragowing.htmlout import cards_html, embed_json, json_attr, proposition_section, spec_from
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


def spec_of(fig) -> dict:
    return json.loads(embed_json(fig.to_dict()))


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


def test_registration_labels_are_on_the_four_forms_figure():
    cases = [
        ({"posthoc": True}, "事後構成"),
        ({"preregistered": True}, "事前登録"),
        ({}, "不明"),
    ]
    for extra, label in cases:
        item = proposition(**extra)
        spec = spec_of(four_forms_figure(item))
        meta = spec["layout"]["meta"]
        assert meta["registration"] == label == registration_status(item)
        assert spec["layout"]["title"]["text"].startswith(f"［{label}］")
        assert meta["cells"] == contingency(item)
        assert meta["cells"] == {"P∧Q": 3, "P∧¬Q": 2, "¬P∧Q": None, "¬P∧¬Q": None}
        shown = spec["data"][0]["cells"]["values"]
        assert shown[1][0] == _cell(3)
        assert shown[2][0] == _cell(2)
        assert "不明" in shown[1][1]


def test_disagreement_stays_a_string_and_listed_cards_are_not_the_count():
    item = proposition()
    item["forms"] = [
        {"form": "original", "n": 5, "hold": 3, "rate": 0.6, "counterexamples": [{"unit": "only-one", "values": {"rd": 1}, "context": {}, "question": "q"}]},
        {"form": "converse", "n": 9, "hold": 9, "rate": 1},
        {"form": "inverse", "n": 5, "hold": 4},
        {"form": "contrapositive", "n": 6, "hold": 4},
    ]
    spec = spec_of(four_forms_figure(item))
    assert str(spec["layout"]["meta"]["cells"]["P∧Q"]).startswith("不一致")
    assert "不一致" in json.dumps(spec["data"][0]["cells"]["values"], ensure_ascii=False)
    original = next(row for row in spec["layout"]["meta"]["forms"] if row["form"] == "original")
    assert original["n"] == 5 and original["hold"] == 3 and original["counterexample_count"] == 2
    assert original["rate"] == 0.6
    page, _fig = proposition_section(item)
    assert "counterexamples: 1" in page
    assert "only-one" in page
    assert "3/5（反例 2）" in page


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
    i = y.index("C 中日 (d)")
    assert z[i][x.index(2012)] == 8.4548548226457
    assert z[i][x.index(2014)] == -1.678984877580291
    assert z[y.index("C 巨人 (g)")][x.index(2014)] is None
    assert heat["layout"]["meta"]["marks"][i][x.index(2014)] == "B"
    assert heat["layout"]["meta"]["marks"][i][x.index(2012)] == ""
    assert "8.4548548226457" in payload["text"][i][0]
    assert payload["text"][i][1].endswith(" B")


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
    fig = spec_of(overlap_figure(overlap))
    texts = [ann["text"] for ann in fig["layout"]["annotations"]]
    for region, text in zip(overlap["regions"], texts):
        if not any(region["bits"]):
            assert text == f"外 {region['count']}"
        else:
            assert text == str(region["count"])
    assert len(fig["layout"]["shapes"]) == 3
    assert {shape["type"] for shape in fig["layout"]["shapes"]} == {"circle"}


def test_cards_copy_values_context_and_question():
    item = proposition(posthoc=True)
    card = item["forms"][0]["counterexamples"][0]
    page, fig = proposition_section(item)
    assert "［事後構成］ P9" in page
    assert "question: 中日 2012 は条件を満たすのに後件を満たさない。なぜか？" in page
    assert f'data-json="{json_attr(card["context"]["wins_vs_pythag"])}"' in page
    assert f'data-json="{json_attr(card["values"]["rd"])}"' in page
    assert f'data-json="{json_attr(True)}"' in page
    spec = spec_of(fig)
    assert spec["layout"]["meta"]["forms"][0]["rate"] == 0.6
    assert "rate=0.6" in spec["data"][1]["cells"]["values"][0][0]
    assert _form_cell(item["forms"][0]) in spec["data"][1]["cells"]["values"][0][0]


def test_cli_writes_standalone_html_and_png_needs_kaleido(tmp_path, monkeypatch):
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
    assert "<script src=" not in index
    assert "plotly.js" in index
    assert index.count("Plotly.newPlot") == 3
    assert "8.4548548226457" in index
    assert "cdn.plot.ly/plotly" not in index
    assert "［事後構成］ P9" in props
    assert "なぜか？" in props
    proc = subprocess.run(
        [sys.executable, "-m", "dragowing", "--results", str(results), "--out", str(tmp_path / "mod"), "--id", "P9"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "mod" / "index.html").is_file()
    builtins = __import__("builtins")
    real_import = builtins.__import__

    def block(name, *args, **kwargs):
        if name == "kaleido" or name.startswith("kaleido."):
            raise ImportError("no kaleido")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block)
    with pytest.raises(PngUnavailable):
        write_png(four_forms_figure(proposition()), tmp_path / "x.png")
    assert not (tmp_path / "x.png").exists()
    missing = subprocess.run(
        [sys.executable, "-m", "dragowing", "--results", str(results), "--out", str(tmp_path / "png"), "--png"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        import kaleido  # noqa: F401
    except ImportError:
        assert missing.returncode == 2
        assert "kaleido" in missing.stderr
        assert (tmp_path / "png" / "index.html").is_file()
    else:
        assert missing.returncode in (0, 1)


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
    index = {(row["league"], row["team"], row["season"]): row for row in rows}
    for i, label in enumerate(payload["y"]):
        for j, season in enumerate(payload["x"]):
            league, rest = label.split(" ", 1)
            team = rest.rsplit("(", 1)[1][:-1]
            row = index[(league, team, season)]
            assert payload["z"][i][j] == row["wins_vs_pythag"]
            assert heat["layout"]["meta"]["z"][i][j] == row["wins_vs_pythag"]
            mark = "B" if row["upper_half"] is False else ""
            assert heat["layout"]["meta"]["marks"][i][j] == mark
            assert json.dumps(row["wins_vs_pythag"]) in payload["text"][i][j]
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
    spec = spec_of(four_forms_figure(p1))
    cells = spec["layout"]["meta"]["cells"]
    assert cells == contingency(p1)
    assert cells["P∧Q"] == form["hold"]
    assert cells["P∧¬Q"] == form["n"] - form["hold"]
    assert spec["layout"]["meta"]["registration"] == "不明"
    recorded = spec["layout"]["meta"]["forms"][0]
    assert recorded["n"] == form["n"] and recorded["hold"] == form["hold"]
    assert recorded["rate"] == form["rate"]
    assert recorded["counterexample_count"] == form["n"] - form["hold"]
    page, _fig = proposition_section(p1)
    card = form["counterexamples"][0]
    assert html.escape(card["question"]) in page
    assert f'data-json="{json_attr(card["context"]["wins_vs_pythag"])}"' in page
    assert f'data-json="{json_attr(card["values"])}"' in page or f'data-json="{json_attr(card["values"]["rd"])}"' in page


def test_cli_on_the_recorded_cycle_writes_standalone_html(tmp_path):
    out = tmp_path / "out"
    assert main(["--results", str(RESULTS), "--out", str(out), "--id", "P1"]) == 0
    index = (out / "index.html").read_text(encoding="utf-8")
    props = (out / "propositions.html").read_text(encoding="utf-8")
    assert "<script src=" not in index
    assert "plotly.js" in index
    heat = spec_from(index, "heatmap")
    assert any(cell == 8.4548548226457 for row in heat["data"][0]["z"] for cell in row)
    assert 'id="P1"' in props
    assert 'id="P2"' not in props
    assert "［不明］ P1" in props


def test_every_proposition_figure_and_card_matches_the_file():
    items = [json.loads(line) for line in (RESULTS / "propositions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(items) == 114
    for item in items:
        spec = spec_of(four_forms_figure(item))
        assert spec["layout"]["meta"]["cells"] == contingency(item)
        assert spec["layout"]["meta"]["registration"] == registration_status(item)
        page = cards_html(item)
        stored = 0
        for form in item["forms"]:
            meta = next(row for row in spec["layout"]["meta"]["forms"] if row["form"] == form["form"])
            assert meta["n"] == form["n"] and meta["hold"] == form["hold"]
            assert meta["counterexample_count"] == form["n"] - form["hold"]
            if "rate" in form:
                assert meta["rate"] == form["rate"]
            for card in form.get("counterexamples") or []:
                stored += 1
                assert html.escape(card["question"]) in page
                assert f'data-unit="{card["unit"]}"' in page
                for value in card["values"].values():
                    assert f'data-json="{json_attr(value)}"' in page
                for value in card["context"].values():
                    assert f'data-json="{json_attr(value)}"' in page
        assert f"counterexamples: {stored}" in page


def test_sources_do_not_import_banned_plot_libraries():
    banned = {"matplotlib", "seaborn", "statsmodels", "plotly.express"}
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
                assert module.split(".")[0] not in {"matplotlib", "seaborn", "statsmodels"}
                assert not module.startswith("plotly.express")
                assert module != "kaleido"
        text = path.read_text(encoding="utf-8")
        for word in ("trendline", "lowess", "spline"):
            assert word not in text
        assert not any(name in text for name in banned if name != "plotly.express")


def test_spec_from_html_roundtrip_matches_the_figure(tmp_path):
    # spec_from is used if present; the helper below parses the script tag.
    item = proposition()
    _page, fig = proposition_section(item)
    html = __import__("dragowing.htmlout", fromlist=["standalone"]).standalone("t", _page)
    parsed = spec_from(html, "forms-P9")
    assert parsed["layout"]["meta"]["cells"] == spec_of(fig)["layout"]["meta"]["cells"]
