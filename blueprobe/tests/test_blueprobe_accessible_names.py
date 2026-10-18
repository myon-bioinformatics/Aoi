"""accessible_names: approximate names of controls and images in saved HTML, checked against Chromium."""
import json
from pathlib import Path

import pytest

import accessible_names as an

PAGES = Path(__file__).resolve().parent / "cases" / "pages"

# Synthetic (SYNTHETIC_FIXTURE_AS_REAL): one example per observation category.
PAGE = """<html><body><main>
<button>\U0001F5D1\ufe0f</button>
<button aria-label="Delete">\U0001F5D1\ufe0f</button>
<span id="t">Search</span><input aria-labelledby="t">
<label for="q">Query</label><input id="q" placeholder="type">
<label>Wrapped <input type="checkbox"></label>
<input placeholder="Only a placeholder">
<input type="file" id="f"><label for="f">Upload</label>
<input type="submit" value="Send"><input type="hidden" name="x">
<div aria-hidden="true"><a href="/a">Hidden link</a></div>
<div hidden><button>Not in the tree</button></div>
<details><summary>More</summary><a href="/inside">Inside closed</a></details>
<a href="/one">Read more</a><a href="/two">Read more</a>
<a href="/img"><img src="x.png" alt="Logo"></a>
<img src="y.png"><img src="z.png" alt="">
<div role="button" title="Settings"></div><button></button>
<select aria-label="Mode"><option>A</option></select>
<script>document.write('<button>ignored</button>')</script>
</main></body></html>"""


def test_names_sources_and_flags():
    report = an.observe(PAGE, "https://example.test/")
    got = [(r["role"], r["name"], r["name_source"], r["flags"]) for r in report["records"]]
    assert got == [
        ("button", "\U0001F5D1\ufe0f", "content", ["emoji_only_name"]),
        ("button", "Delete", "aria-label", []),
        ("textbox", "Search", "aria-labelledby", []),
        ("textbox", "Query", "label", []),
        ("checkbox", "Wrapped", "label", []),
        ("textbox", "Only a placeholder", "placeholder", ["placeholder_only"]),
        ("button", "Upload", "label", []),
        ("button", "Send", "value", []),
        ("link", "Hidden link", "content", ["aria_hidden_control"]),
        ("button", "Not in the tree", "content", []),
        ("disclosure", "More", "content", []),
        ("link", "Inside closed", "content", []),
        ("link", "Read more", "content", []),
        ("link", "Read more", "content", []),
        ("link", "Logo", "content", []),
        ("img", "Logo", "alt", []),
        ("img", "", None, ["empty_name", "image_without_alt"]),
        ("button", "Settings", "title", []),
        ("button", "", None, ["empty_name"]),
        ("combobox", "Mode", "aria-label", []),
        ("option", "A", "content", [])]
    hidden = {r["name"]: r["hidden"] for r in report["records"]}
    assert hidden["Not in the tree"] and hidden["Inside closed"] and hidden["Hidden link"] and not hidden["More"]
    assert report["counts"]["ambiguous_link_name"] == 1 and report["counts"]["decorative_image"] == 1
    assert report["records"][0]["emoji"] == ["\U0001F5D1\ufe0f"]
    summary = an.summarize(report)
    assert summary["flags"]["empty_name"] == 2 and summary["roles"]["link"] == 5
    with pytest.raises(TypeError):
        an.observe(b"<a></a>")


def test_aria_snapshot_parser_and_comparison_categories():
    snapshot = '- link "[GitHub]":\n  - /url: x\n- button "Save"\n- button\n- heading "Title" [level=1]\n- textbox "Esc \\"q\\""'
    assert an.parse_aria_snapshot(snapshot) == [("link", "[GitHub]"), ("button", "Save"), ("button", ""),
                                                ("textbox", 'Esc "q"')]
    report = {"records": [{"role": "link", "name": "GitHub", "hidden": False},
                          {"role": "button", "name": "Save", "hidden": False},
                          {"role": "button", "name": "Other", "hidden": False},
                          {"role": "textbox", "name": "x", "hidden": True}]}
    result = an.compare_aria_snapshot(report, snapshot)
    assert result["counts"] == {"css_generated": 1, "match": 1, "mismatch": 1, "browser_only": 1, "static_only": 0}
    assert result["mismatches"] == [{"role": "button", "static": "Other", "browser": ""}]


# Real pages rendered in Chromium from repository commits (provenance inside each capture).
EXPECTED = {
    "myon-bioinformatics-github-io-index": {"match": 21, "css_generated": 6},
    "github-io-mcp-toolcall-lab": {"match": 11},
    "github-io-html-import": {"match": 12},
    "web-ui-examples-index": {"match": 3},
    "web-ui-examples-github-like": {"match": 2},
}


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_real_pages_agree_with_chromium(name):
    capture = json.loads((PAGES / f"{name}.json").read_text(encoding="utf-8"))
    assert capture["schema"] == "btk-browser-dom/1" and len(capture["provenance"]["commit"]) == 40
    counts = an.observe_capture(capture)["aria_comparison"]["counts"]
    assert counts == {"match": 0, "css_generated": 0, "mismatch": 0, "browser_only": 0, "static_only": 0,
                      **EXPECTED[name]}


def test_css_generated_names_are_reported_separately():
    capture = json.loads((PAGES / "myon-bioinformatics-github-io-index.json").read_text(encoding="utf-8"))
    report = an.observe_capture(capture)
    first = next(r for r in report["records"] if r["role"] == "link")
    assert first["name"] == "GitHub"
    assert ("link", "[GitHub]") in an.parse_aria_snapshot(capture["aria_snapshot"])


def test_capture_validation_and_cli(tmp_path, capsys):
    with pytest.raises(ValueError):
        an.observe_capture({"schema": "other", "html": ""})
    page = tmp_path / "page.html"
    page.write_text(PAGE, encoding="utf-8")
    assert an.main([str(page)]) == 0
    out = capsys.readouterr().out
    assert "  empty_name: 2" in out and "[emoji_only_name] button" in out
    assert an.main([str(PAGES / "web-ui-examples-index.json"), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["aria_comparison"]["counts"]["match"] == 3 and data["summary"]["controls"] == 3
    assert an.main([str(tmp_path / "missing.html")]) == 2
