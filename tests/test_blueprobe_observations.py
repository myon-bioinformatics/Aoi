"""👀 Saved-observation tools (`python blueprobe.py names | emoji | headings | web`), offline.

pytest only: the uv group `observation-test` runs exactly this file (docs/nano-observation-tests.md, 49 tests).
`python -S -m unittest discover -s tests -p test_blueprobe_observations.py` runs the stdlib walk tests
(docs/accessible-walk.md).

- names: approximate names of controls and images in saved HTML, checked against Chromium.
- emoji: where and how emoji appear in saved HTML (offline, observation only).
- headings: document outline, heading hierarchy, and landmark structure observations.
- snapshot: the saved-page supplier contract (SnapshotSupplier, QueRyuCacheSource, inspect_snapshots).
- web: saved Web observation receipts and source inventories.
- walk: stdlib deep-DOM regression and preorder parity.
"""

import copy
import hashlib
import json
import os
import random
import subprocess
import sys
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch

import importlib.util as _importlib_util
import sys as _sys

_cli_spec = _importlib_util.spec_from_file_location("blueprobe_cli_args", Path(__file__).resolve().parents[1] / "vendor" / "cli_args.py")
_cli_args = _importlib_util.module_from_spec(_cli_spec)
_sys.modules[_cli_spec.name] = _cli_args
_cli_spec.loader.exec_module(_cli_args)
run_cli = _cli_args.run_cli

try:
    import pytest
except ImportError:  # `python -S` (no site-packages): only the unittest.TestCase classes below run.
    class _NoPytest:  # pytest-style tests stay defined but are never collected by unittest
        def __getattr__(self, name): return self
        def __call__(self, *args, **kwargs):
            return args[0] if len(args) == 1 and not kwargs and callable(args[0]) else self
    pytest = _NoPytest()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # `python -S -m unittest discover -s tests`
import blueprobe  # noqa: E402
from blueprobe import (
    QueRyuCacheSource, SNAPSHOT_SCHEMA, SnapshotSupplier, emoji as eo, headings as ho, inspect_cache,
    inspect_queryu_cache, inspect_snapshots, names, names as an, new_report, source_inventory, web,
)


# ──── names ───────────────────────────────────────────────────────

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
    assert an.main([str(PAGES / "web-ui-examples-index.json"), "--format", "json"]) == 0  # --json is shorthand for this
    assert json.loads(capsys.readouterr().out) == data
    assert an.main([str(tmp_path / "missing.html")]) == 2


# ──── emoji ───────────────────────────────────────────────────────

CASES = Path(__file__).resolve().parent / "cases"

HOME, MAP, MAP_VS = "\U0001F3E0", "\U0001F5FA", "\U0001F5FA\ufe0f"

# Synthetic page (not a real site; see SYNTHETIC_FIXTURE_AS_REAL): every place emoji can hide.
EMOJI_PAGE = (
    f"<html><head><title>{HOME} Home</title><meta name='description' content='map {MAP_VS}'>"
    "<meta name='viewport' content='width=device-width'>"
    "<style>.x:before{content:'\U0001F389'}</style></head><body>"
    f"<nav><a href='#/' aria-label='Home'>{HOME}</a><button>{MAP}</button>"
    "<span aria-hidden='true'>\u2728</span><img alt='\U0001F44D\U0001F3FD ok'><br>"
    "<div role='button' title='Settings'>\u2699\ufe0f</div></nav>"
    "<p>\u00a9\ufe0f and \u00a9 and \U0001F469\u200d\U0001F4BB coder \u3030 wave</p>"
    "<script>'\U0001F6AB'</script><template>\U0001F6AB</template>"
    "<input placeholder='\U0001F50D search' value='\U0001F6AB typed'></body></html>")


def rows(report):
    return [(r["emoji"], r["where"], r["element"], r["in_control"], r["control_label"], r["aria_hidden"])
            for r in report["records"]]


def test_records_every_visible_place_with_context():
    report = eo.observe(EMOJI_PAGE, "https://example.test/")
    assert rows(report) == [
        (HOME, "title", "html > head > title", None, None, False),
        (MAP_VS, "meta:description", "html > head > meta", None, None, False),
        (HOME, "text", "html > body > nav > a", "a", "Home", False),
        (MAP, "text", "html > body > nav > button", "button", None, False),
        ("\u2728", "text", "html > body > nav > span", None, None, True),
        ("\U0001F44D\U0001F3FD", "attr:alt", "html > body > nav > img", None, None, False),
        ("\u2699\ufe0f", "text", "html > body > nav > div", "div", "Settings", False),
        ("\u00a9\ufe0f", "text", "html > body > p", None, None, False),
        ("\U0001F469\u200d\U0001F4BB", "text", "html > body > p", None, None, False),
        ("\U0001F50D", "attr:placeholder", "html > body > input", None, None, False)]
    first = report["records"][0]
    assert first["key"] == "https://example.test/#0" and first["identity"] == HOME and first["raw_text"] == f"{HOME} Home"
    assert report["counts"][MAP] == 2 and report["unknown"] == []
    assert "\U0001F6AB" not in report["counts"] and "\U0001F389" not in report["counts"]  # script/style/template/value


def test_summary_forms_places_and_unlabelled_controls():
    summary = {row["identity"]: row for row in eo.summarize(eo.observe(EMOJI_PAGE))}
    assert summary[MAP]["forms"] == {MAP_VS: 1, MAP: 1}
    assert summary[MAP]["where"] == {"meta:description": 1, "text": 1}
    assert summary[MAP]["unlabelled_control"] == 1 and summary[HOME]["unlabelled_control"] == 0
    assert summary["\u2728"]["aria_hidden"] == 1 and summary["\u2699"]["unlabelled_control"] == 0
    assert list(summary)[:2] == [HOME, MAP]


def test_contract_with_xprobe_sequences():
    expected = json.loads((CASES / "emoji_corpus.expected.json").read_text(encoding="utf-8"))
    assert expected["source"]["repository"] == "myon-bioinformatics/xprobe"
    assert eo.emoji_sequences((CASES / "emoji_corpus.txt").read_text(encoding="utf-8")) == expected["sequences"]


def test_truncation_is_recorded_not_silent():
    report = eo.observe("<p>" + HOME * 5 + "</p>", "u", max_records=3)
    assert len(report["records"]) == 3 and report["unknown"] == [{"url": "u", "reason": "truncated after 3 emoji"}]


def test_snapshot_provenance_is_carried():
    snapshot = {"schema": "html-snapshot/1", "html": f"<p>{HOME}</p>", "url": "https://example.test/",
                "response_sha256": "a" * 64, "fetched_at": "2026-10-18T00:00:00+00:00", "encoding": "utf-8"}
    record = eo.observe_snapshot(snapshot)["records"][0]
    assert record["response_sha256"] == "a" * 64 and record["fetched_at"].startswith("2026") and record["url"]
    with pytest.raises(ValueError):
        eo.observe_snapshot({"schema": "other", "html": ""})
    with pytest.raises(TypeError):
        eo.observe(b"<p></p>")


def test_cli(tmp_path, capsys):
    page = tmp_path / "page.html"
    page.write_text(EMOJI_PAGE, encoding="utf-8")
    assert eo.main([str(page)]) == 0
    out = capsys.readouterr().out
    assert f"{MAP}\t2\t{MAP_VS}x1 {MAP}x1\tmeta:descriptionx1 textx1 unlabelled_control=1" in out
    assert out.rstrip().endswith("emoji: 8 distinct, 10 occurrence(s)")
    assert eo.main([str(page), "--json", "--url", "https://example.test/"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["records"][0]["url"] == "https://example.test/" and data["summary"][0]["identity"] == HOME
    assert eo.main([str(tmp_path / "missing.html")]) == 2


def test_raw_text_is_anchored_to_each_occurrence():
    filler = "x" * 40
    html = f"<p>first {HOME} {filler} second {HOME} later</p>"
    records = [r for r in eo.observe(html)["records"] if r["identity"] == HOME]
    assert [r["raw_text"] for r in records] == [f"first {HOME} " + "x" * 29, "x" * 22 + f" second {HOME} later"]


# ──── headings ────────────────────────────────────────────────────

HEADING_PAGE = """<html><body>
<h1>Top Level</h1>
<p>Outside landmarks</p>
<main>
  <header>Site Banner</header>
  <nav aria-label="Main Navigation">
    <a href="/">Home</a>
  </nav>
  <h2>Section One</h2>
  <section aria-labelledby="sec2-title">
    <h2 id="sec2-title">Section Two</h2>
    <h4>Skipped Level Subheading</h4>
    <h2></h2>
  </section>
  <div role="heading" aria-level="3">ARIA Heading</div>
  <div hidden><h1>Hidden H1</h1></div>
  <div aria-hidden="true"><h2>Aria Hidden H2</h2></div>
  <details><summary>Details Summary</summary><h2>Inside closed details</h2></details>
</main>
<nav></nav>
<h1>Second H1</h1>
</body></html>"""


def test_heading_and_landmark_observations():
    report = ho.observe(HEADING_PAGE, "https://example.test/")
    headings = [r for r in report["records"] if r["type"] == "heading"]
    landmarks = [r for r in report["records"] if r["type"] == "landmark"]

    # Landmark checks
    lm_roles = [(r["role"], r["label"], r["flags"]) for r in landmarks]
    assert lm_roles == [
        ("main", "", []),
        ("navigation", "Main Navigation", []),
        ("region", "Section Two", []),
        ("navigation", "", ["unlabelled_landmark"]),
    ]

    # Heading checks
    h_got = [(r["level"], r["tag"], r["text"], r["landmark"]["role"] if r["landmark"] else None, r["hidden"], r["flags"])
             for r in headings]
    assert h_got == [
        (1, "h1", "Top Level", None, False, ["heading_outside_landmark"]),
        (2, "h2", "Section One", "main", False, []),
        (2, "h2", "Section Two", "region", False, []),
        (4, "h4", "Skipped Level Subheading", "region", False, ["skipped_heading_level"]),
        (2, "h2", "", "region", False, ["empty_heading"]),
        (3, "div", "ARIA Heading", "main", False, []),
        (1, "h1", "Hidden H1", "main", True, []),
        (2, "h2", "Aria Hidden H2", "main", True, []),
        (2, "h2", "Inside closed details", "main", True, []),
        (1, "h1", "Second H1", None, False, ["multiple_h1", "heading_outside_landmark"]),
    ]

    summary = ho.summarize(report)
    assert summary["headings"] == 10
    assert summary["landmarks"] == 4
    assert summary["levels"] == {"h1": 3, "h2": 5, "h3": 1, "h4": 1}
    assert summary["flags"]["skipped_heading_level"] == 1
    assert summary["flags"]["multiple_h1"] == 1
    assert summary["flags"]["empty_heading"] == 1
    assert summary["flags"]["unlabelled_landmark"] == 1
    assert summary["flags"]["heading_outside_landmark"] == 2


def test_missing_main_landmark_detection():
    html = "<html><body><h1>Title</h1><section><h2>Sub</h2></section></body></html>"
    report = ho.observe(html)
    assert report["counts"]["missing_main_landmark"] == 1
    page = [r for r in report["records"] if r["type"] == "page"]
    assert page == [{"key": "#page", "type": "page", "url": None, "visible_headings": 2,
                     "flags": ["missing_main_landmark"]}]


def test_real_page_captures_run_without_errors():
    capture_file = PAGES / "web-ui-examples-index.json"
    capture = json.loads(capture_file.read_text(encoding="utf-8"))
    report = ho.observe_capture(capture)
    summary = ho.summarize(report)
    assert summary["headings"] == 4
    assert summary["landmarks"] == 1
    assert summary["levels"] == {"h1": 1, "h2": 3}


def test_type_and_schema_validation_errors():
    with pytest.raises(TypeError):
        ho.observe(123)
    with pytest.raises(ValueError, match="expected btk-browser-dom/1 or html-snapshot/1"):
        ho.observe_capture({"schema": "invalid/1"})


def test_cli_execution_and_json_output(tmp_path, capsys):
    page_file = tmp_path / "page.html"
    page_file.write_text(HEADING_PAGE, encoding="utf-8")

    assert ho.main([str(page_file)]) == 0
    out = capsys.readouterr().out
    assert "headings 10" in out
    assert "skipped_heading_level: 1" in out

    assert ho.main([str(page_file), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["headings"] == 10
    assert len(data["records"]) == 14

    assert ho.main([str(tmp_path / "nonexistent.html")]) == 2


def test_native_landmarks_require_correct_scope_and_name():
    html = '<header>Site</header><main><header>Section</header><section><h2>A</h2></section><section aria-label="Named"><h2>B</h2></section><article><h2>C</h2></article><footer>Section</footer></main><footer>Site</footer>'
    records = ho.observe(html)["records"]
    assert [(r["tag"], r["role"]) for r in records if r["type"] == "landmark"] == [
        ("header", "banner"), ("main", "main"), ("section", "region"), ("footer", "contentinfo")]
    assert [(r["text"], r["landmark"]["role"]) for r in records if r["type"] == "heading"] == [
        ("A", "main"), ("B", "region"), ("C", "main")]


@pytest.mark.parametrize("label", ['aria-label="Named"', 'aria-labelledby="label"', 'title="Named"'])
def test_named_sections_are_regions(label):
    records = ho.observe(f'<span id="label">Named</span><section {label}><h2>Child</h2></section>')["records"]
    assert [(r["role"], r["label"]) for r in records if r["type"] == "landmark"] == [("region", "Named")]


@pytest.mark.parametrize("level", ["0", "-1", "invalid"])
def test_invalid_aria_heading_level_defaults_to_two(level):
    records = ho.observe(f'<main><div role="heading" aria-level="{level}">Heading</div></main>')["records"]
    assert [r["level"] for r in records if r["type"] == "heading"] == [2]


@pytest.mark.parametrize("level,expected", [("0", 3), ("-2", 3), ("x", 3), ("", 3), ("5", 5)])
def test_html_heading_aria_level_falls_back_to_html_level(level, expected):
    records = ho.observe(f'<main><h3 aria-level="{level}">Heading</h3></main>')["records"]
    assert [r["level"] for r in records if r["type"] == "heading"] == [expected]


def test_landmark_label_and_tree_are_shared_with_accessible_names():
    # 見出しと名前は同じ木（blueprobe._Tree）と同じ名前計算を使う
    assert blueprobe.names.observe.__globals__ is ho.observe.__globals__
    html = '<span id="l">From <b aria-hidden="true">x</b>id</span><section aria-labelledby="l"><h2>A</h2></section>'
    records = ho.observe(html)["records"]
    assert [(r["role"], r["label"]) for r in records if r["type"] == "landmark"] == [("region", "From id")]


# ──── snapshot ────────────────────────────────────────────────────

class MemorySupplier:
    """QueRyu 以外の供給元の最小例。契約だけ満たせば inspect_snapshots で読める。"""

    def __init__(self, pages):
        self.pages = pages

    def entries(self):
        return [{"key": k, "url": u, "group": g} for k, u, g, _ in self.pages]

    def _html(self, entry):
        return next(h for k, _, _, h in self.pages if k == entry["key"])

    def body(self, entry):
        return self._html(entry)

    def snapshot(self, entry):
        return {"schema": SNAPSHOT_SCHEMA, "html": self._html(entry), "url": entry["url"],
                "fetched_at": None, "response_sha256": None, "content_sha256": None,
                "encoding": "utf-8", "cache_entry": None}


class Html:
    def parse(self, html, url):
        r = new_report()
        r["records"].append({"key": url, "raw": html})
        return r


class Snap:
    def parse_snapshot(self, snapshot):
        r = new_report()
        r["records"].append({"key": snapshot["url"], "schema": snapshot["schema"]})
        return r


SNAPSHOT_PAGES = [("a", "u:a", "g1", "<p>a</p>"), ("b", "u:b", "g1", ""), ("c", "u:c", "g2", "<p>c</p>")]


def test_generic_supplier_body_and_snapshot():
    supplier = MemorySupplier(SNAPSHOT_PAGES)
    assert isinstance(supplier, SnapshotSupplier)
    rows = inspect_snapshots(Html(), supplier)
    assert [(r["group"], r["pages"], r["empty_pages"]) for r in rows] == [("g1", 1, 1), ("g2", 1, 0)]
    out = []
    inspect_snapshots(Snap(), supplier, records_out=out)
    assert [r["schema"] for r in out] == [SNAPSHOT_SCHEMA] * 2


class FakeCache:
    def latest(self):
        return {k: {"key": k, "url": u, "group": g} for k, u, g, _ in SNAPSHOT_PAGES}

    def body(self, entry):
        return MemorySupplier(SNAPSHOT_PAGES).body(entry)

    def snapshot(self, entry):
        return MemorySupplier(SNAPSHOT_PAGES).snapshot(entry)


def test_queryu_adapter_and_deprecated_alias_agree():
    assert isinstance(QueRyuCacheSource(FakeCache()), SnapshotSupplier)
    new = inspect_queryu_cache(Html(), FakeCache())
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        old = inspect_cache(Html(), FakeCache())
    assert old == new
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


# ──── web ─────────────────────────────────────────────────────────

observe = web.observe


def receipt():
    return {"schema": "flutter-web-observation/1", "build_sha": "a" * 40,
        "url": "https://example.test/#/tools/media/photo-studio", "status": "passed",
        "capture_errors": [], "extra_provenance": {"keep": True},
        "runtime": {"display": {"viewport": {"width": 800, "height": 600},
            "controls": [{"label": "📷 写真", "visible": True,
                          "box": {"x": -1, "y": 20, "width": 80, "height": 30}}]}}}


def save(root, data, name="page"):
    directory = root / name
    directory.mkdir()
    (directory / "web-observation.json").write_text(json.dumps(data), encoding="utf-8")
    return directory


def test_preserves_raw_geometry_actions_and_reports_missing_capabilities(tmp_path):
    raw = receipt()
    page = save(tmp_path, raw)
    actions = {"schema": "flutter-web-exploration/1", "actions": [
        {"kind": "press", "label": "📷 写真", "after_url": raw["url"]}]}
    (page / "exploration.json").write_text(json.dumps(actions), encoding="utf-8")
    result = observe(tmp_path)
    record = result["report"]["records"][0]
    assert record["raw"] == raw and record["raw_exploration"] == actions
    assert record["derived"]["controls"][0]["box"]["x"] == -1
    assert record["derived"]["actions"] == actions["actions"]
    assert result["report"]["counts"]["invalid"] == 0
    assert not result["current_code_executed"] and not result["native_equivalence_verified"]
    assert "backend" in result["unobserved"][0]


@pytest.mark.parametrize("bad", [None, True, float("nan"), "20"])
def test_invalid_coordinates_are_retained_as_unknown(tmp_path, bad):
    raw = receipt()
    raw["runtime"]["display"]["controls"][0]["box"]["x"] = bad
    save(tmp_path, raw)
    result = observe(tmp_path)["report"]
    assert not result["records"] and result["counts"]["invalid"]
    assert result["unknown"][0]["key"] == "page/web-observation.json"


def test_mixed_builds_are_incomplete_and_missing_actions_not_invented(tmp_path):
    raw = receipt()
    save(tmp_path, raw)
    other = copy.deepcopy(raw)
    other["build_sha"] = "b" * 40
    save(tmp_path, other, "other")
    result = observe(tmp_path)["report"]
    assert result["counts"]["invalid"] == 1
    assert result["unknown"][0]["reason"] == "mixed reported build SHAs"
    assert result["counts"]["missing_action_receipts"] == 2
    assert all(row["derived"]["actions"] is None for row in result["records"])


def test_empty_directory_never_becomes_successful_evidence(tmp_path):
    assert observe(tmp_path)["report"]["counts"]["invalid"]


def test_failed_producer_receipt_is_observed_without_becoming_a_pass(tmp_path):
    raw = receipt()
    raw.update(status="failed", capture_errors=["screenshot unavailable"])
    save(tmp_path, raw)
    result = observe(tmp_path)["report"]
    assert result["counts"]["producer_failed_or_incomplete"] == 1
    assert result["records"][0]["derived"]["producer_status"] == "failed"


def test_cli_preserves_unicode_on_legacy_console(tmp_path):
    save(tmp_path, receipt())
    script = Path(__file__).resolve().parents[1] / "blueprobe.py"
    result = subprocess.run([sys.executable, "-S", str(script), "web", str(tmp_path)],
        text=True, capture_output=True, encoding="ascii",
        env={**os.environ, "PYTHONIOENCODING": "cp1252"})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["report"]["records"][0]["derived"]["controls"][0]["label"] == "📷 写真"


def test_source_inventory_hashes_bytes_without_claiming_route_binding(tmp_path):
    for name in ("view.dart", "View.kt", "View.swift", "ignored.py", "build/cached.dart", "pubspec.lock"):
        path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"// source\r\n")
    rows = source_inventory(tmp_path)
    assert {row["language"] for row in rows if row["kind"] == "source"} == {"dart", "kotlin", "swift"}
    assert len(rows) == 4
    assert next(row for row in rows if row["path"] == "pubspec.lock")["kind"] == "build-config"
    assert all(row["sha256"] == hashlib.sha256(b"// source\r\n").hexdigest() for row in rows)


def test_documented_directory_cli_with_source_root(tmp_path):
    observations = tmp_path / "saved pages"
    observations.mkdir()
    save(observations, receipt())
    sources = tmp_path / "flutter sources"
    sources.mkdir()
    (sources / "view.dart").write_text("// inventory only\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "blueprobe.py"
    result = run_cli(script, "web", str(observations),
        "--source-root", str(sources), python_options=("-S",))
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert len(report["report"]["records"]) == 1
    assert report["sources"][0]["path"] == "view.dart"
    assert not report["current_code_executed"]


# ──── walk ────────────────────────────────────────────────────────

def recursive(node):
    for child in node.children:
        if isinstance(child, blueprobe._Node):
            yield child
            yield from recursive(child)


class WalkTests(unittest.TestCase):
    def test_shuffled_trees_preorder_and_full_report_parity(self):
        rng = random.Random(20261104)
        for _ in range(30):
            depths = [rng.randrange(8) for _ in range(10)]
            html = ''.join('<div>' * depth + '<button aria-label="go">x</button>'
                           + '</div>' * depth for depth in depths)
            html += '<label for="input">label</label><input id="input"><a href="a">same</a><a href="b">same</a>'
            tree = blueprobe._Tree()
            tree.feed(html)
            self.assertEqual(list(blueprobe._walk(tree.root)), list(recursive(tree.root)))
            got = names.observe(html)
            with patch.object(blueprobe, '_walk', recursive):
                expected = names.observe(html)
            self.assertEqual(got, expected)

    def test_dom_beyond_recursion_limit(self):
        depth = sys.getrecursionlimit() + 100
        html = '<div>' * depth + '<button aria-label="go">go</button>' + '</div>' * depth
        tree = blueprobe._Tree()
        tree.feed(html)
        self.assertEqual(len(list(blueprobe._walk(tree.root))), depth + 1)
        with self.assertRaises(RecursionError):
            list(recursive(tree.root))
        report = names.observe(html)
        self.assertEqual(len(report['records']), 1)
        self.assertEqual(report['records'][0]['name'], 'go')
        self.assertEqual(report['records'][0]['key'], '#' + str(depth))
