"""Tests for QueRyu pattern_extractor module."""

import json
from pathlib import Path

import pytest

from pattern_extractor import (
    DOM_PATTERNS,
    detect_pattern,
    extract_from_har,
    extract_from_snapshot,
    extract_pattern,
    main,
    normalize_whitespace,
)


def test_normalize_whitespace():
    raw = "  Hello   \n\n   world!  \t\n\n\n  Third line  "
    expected = "Hello\n\nworld!\n\nThird line"
    assert normalize_whitespace(raw) == expected


def test_extract_pattern_github_readme():
    html = """
    <html>
      <head><title>Test README</title></head>
      <body>
        <article class="markdown-body">
          <h1>Project Title</h1>
          <p>This is a <a href="https://example.test">link</a> in the README.</p>
          <script>console.log("ignore me");</script>
          <h2>Features</h2>
          <ul>
            <li>Feature 1</li>
            <li>Feature 2</li>
          </ul>
        </article>
      </body>
    </html>
    """
    res = extract_pattern(html, pattern_key="github_readme")
    assert res["schema"] == "queryu-extracted-pattern/1"
    assert res["pattern_key"] == "github_readme"
    assert res["matched_node_count"] == 1
    assert res["title"] == "Test README"
    assert "Project Title" in res["text"]
    assert "console.log" not in res["text"]
    assert "console.log" not in res["clean_html"]
    assert len(res["headings"]) == 2
    assert res["headings"][0] == {"level": 1, "text": "Project Title"}
    assert res["headings"][1] == {"level": 2, "text": "Features"}
    assert res["links"] == [{"text": "link", "href": "https://example.test"}]
    assert "article" in res["tags"]
    assert "h1" in res["tags"]
    assert res["metadata"]["heading_count"] == 2
    assert res["metadata"]["link_count"] == 1


def test_extract_pattern_npb_calendar_tables():
    html = """
    <div id="calendar">
      <h2>2026年3月</h2>
      <table class="calendar">
        <tr><th>日</th><th>月</th><th>火</th></tr>
        <tr><td>1</td><td>2</td><td>3</td></tr>
      </table>
    </div>
    """
    res = extract_pattern(html, pattern_key="npb_calendar")
    assert res["pattern_key"] == "npb_calendar"
    assert len(res["tables"]) == 1
    assert res["tables"][0] == [
        ["日", "月", "火"],
        ["1", "2", "3"],
    ]
    assert res["metadata"]["table_count"] == 1


def test_extract_pattern_npb_linescore_tables():
    html = """
    <table class="score_table">
      <tr><th>チーム</th><th>1</th><th>2</th><th>R</th></tr>
      <tr><td>ドラゴンズ</td><td>0</td><td>1</td><td>1</td></tr>
    </table>
    """
    res = extract_pattern(html, pattern_key="npb_linescore")
    assert res["pattern_key"] == "npb_linescore"
    assert len(res["tables"]) == 1
    assert res["tables"][0] == [
        ["チーム", "1", "2", "R"],
        ["ドラゴンズ", "0", "1", "1"],
    ]


def test_extract_pattern_custom_selector():
    html = """
    <section class="custom-sec">
      <h3>Custom Heading</h3>
      <p>Custom content</p>
    </section>
    """
    res = extract_pattern(html, custom_selector="section.custom-sec")
    assert res["selector_used"] == "section.custom-sec"
    assert res["headings"] == [{"level": 3, "text": "Custom Heading"}]
    assert "Custom content" in res["text"]


def test_extract_pattern_auto_detection():
    html = '<article class="markdown-body"><h1>Auto README</h1></article>'
    res = extract_pattern(html, pattern_key="auto")
    assert res["pattern_key"] == "github_readme"


def test_extract_pattern_empty():
    res = extract_pattern("")
    assert res["matched_node_count"] == 0
    assert res["text"] == ""
    assert res["headings"] == []


def test_extract_from_snapshot(tmp_path):
    snapshot = {
        "schema": "html-snapshot/1",
        "html": "<main><h1>Docs</h1><p>Documentation page.</p></main>",
        "url": "https://docs.example.test/page",
        "fetched_at": "2026-03-01T12:00:00Z",
        "content_sha256": "abcdef1234567890",
    }

    # Dict test
    res = extract_from_snapshot(snapshot, pattern_key="documentation_main")
    assert res["url"] == "https://docs.example.test/page"
    assert res["snapshot_sha256"] == "abcdef1234567890"
    assert res["headings"] == [{"level": 1, "text": "Docs"}]

    # File path test
    snap_path = tmp_path / "snapshot.json"
    snap_path.write_text(json.dumps(snapshot), encoding="utf-8")
    res_f = extract_from_snapshot(snap_path, pattern_key="documentation_main")
    assert res_f["url"] == "https://docs.example.test/page"


def test_extract_from_har(tmp_path):
    har_data = {
        "log": {
            "entries": [
                {
                    "request": {"url": "https://example.test/article1"},
                    "response": {
                        "status": 200,
                        "content": {
                            "mimeType": "text/html",
                            "text": "<article><h1>Article 1</h1><p>First post</p></article>",
                        },
                    },
                },
                {
                    "request": {"url": "https://example.test/api/data.json"},
                    "response": {
                        "status": 200,
                        "content": {
                            "mimeType": "application/json",
                            "text": '{"key": "value"}',
                        },
                    },
                },
            ]
        }
    }

    # All entries
    results = extract_from_har(har_data, pattern_key="article_body")
    assert len(results) == 1
    assert results[0]["url"] == "https://example.test/article1"
    assert results[0]["extracted"]["headings"] == [{"level": 1, "text": "Article 1"}]

    # URL filter test
    results_filtered = extract_from_har(har_data, pattern_key="article_body", url_pattern=r"/article\d+")
    assert len(results_filtered) == 1

    results_no_match = extract_from_har(har_data, pattern_key="article_body", url_pattern=r"/nomatch")
    assert len(results_no_match) == 0

    # HAR File path test
    har_path = tmp_path / "archive.har"
    har_path.write_text(json.dumps(har_data), encoding="utf-8")
    results_f = extract_from_har(har_path, pattern_key="article_body")
    assert len(results_f) == 1


def test_cli_html_input(tmp_path):
    html_file = tmp_path / "index.html"
    out_file = tmp_path / "extracted.json"
    html_file.write_text('<main><h1>CLI Test</h1><p>Hello CLI</p></main>', encoding="utf-8")

    code = main(["--input", str(html_file), "--pattern", "generic_main", "--out", str(out_file)])
    assert code == 0
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["pattern_key"] == "generic_main"
    assert data["headings"] == [{"level": 1, "text": "CLI Test"}]


def test_cli_har_input(tmp_path):
    har_data = {
        "log": {
            "entries": [
                {
                    "request": {"url": "https://example.test/main"},
                    "response": {
                        "status": 200,
                        "content": {
                            "mimeType": "text/html",
                            "text": "<main><h1>HAR Main</h1></main>",
                        },
                    },
                }
            ]
        }
    }
    har_file = tmp_path / "sample.har"
    out_file = tmp_path / "har_extracted.json"
    har_file.write_text(json.dumps(har_data), encoding="utf-8")

    code = main(["--har", str(har_file), "--pattern", "generic_main", "--out", str(out_file)])
    assert code == 0
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["url"] == "https://example.test/main"
    assert data[0]["extracted"]["headings"] == [{"level": 1, "text": "HAR Main"}]
