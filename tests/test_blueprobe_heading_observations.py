"""heading_observations: document outline, heading hierarchy, and landmark structure observations."""
import json
from pathlib import Path

import pytest

import heading_observations as ho

PAGES = Path(__file__).resolve().parent / "cases" / "pages"

PAGE = """<html><body>
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
    report = ho.observe(PAGE, "https://example.test/")
    headings = [r for r in report["records"] if r["type"] == "heading"]
    landmarks = [r for r in report["records"] if r["type"] == "landmark"]

    # Landmark checks
    lm_roles = [(r["role"], r["label"], r["flags"]) for r in landmarks]
    assert lm_roles == [
        ("main", "", []),
        ("banner", "", []),
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
    assert summary["landmarks"] == 5
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


def test_real_page_captures_run_without_errors():
    capture_file = PAGES / "web-ui-examples-index.json"
    capture = json.loads(capture_file.read_text(encoding="utf-8"))
    report = ho.observe_capture(capture)
    summary = ho.summarize(report)
    assert summary["headings"] == 4
    assert summary["landmarks"] == 5
    assert summary["levels"] == {"h1": 1, "h2": 3}


def test_type_and_schema_validation_errors():
    with pytest.raises(TypeError):
        ho.observe(123)
    with pytest.raises(ValueError, match="expected btk-browser-dom/1 or html-snapshot/1"):
        ho.observe_capture({"schema": "invalid/1"})


def test_cli_execution_and_json_output(tmp_path, capsys):
    page_file = tmp_path / "page.html"
    page_file.write_text(PAGE, encoding="utf-8")

    assert ho.main([str(page_file)]) == 0
    out = capsys.readouterr().out
    assert "headings 10" in out
    assert "skipped_heading_level: 1" in out

    assert ho.main([str(page_file), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["headings"] == 10
    assert len(data["records"]) == 15

    assert ho.main([str(tmp_path / "nonexistent.html")]) == 2
