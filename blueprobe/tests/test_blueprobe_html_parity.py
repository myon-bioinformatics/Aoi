"""selectolax is the oracle. Runtime parsing stays on html.parser."""

import json
from pathlib import Path

from selectolax.lexbor import LexborHTMLParser

import npb_calendar
import npb_game_linescore
import npb_schedule_current
import npb_team_annual
import npb_team_batting
from blueprobe import DOM_PATTERNS, HtmlTree, detect_pattern

ROOT = Path(__file__).resolve().parents[1]
LINE_URL = "https://npb.jp/bis/2024/games/s2024040201097.html"
SCHEDULE_URL = "https://npb.jp/games/2026/schedule_09_detail.html"
BATTING_URL = "https://npb.jp/bis/2024/stats/tmb_c.html"


def _saved_documents():
    fixtures = ROOT / "tests" / "fixtures"
    for path in sorted(fixtures.rglob("*.html")):
        yield path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")
    pages = ROOT / "tests" / "cases" / "pages"
    for path in sorted(pages.glob("*.json")):
        yield path.relative_to(ROOT).as_posix(), json.loads(path.read_text(encoding="utf-8"))["html"]


def _subselectors():
    found = []
    for pattern in DOM_PATTERNS.values():
        for part in pattern["selector"].split(","):
            part = part.strip()
            if part and part not in found:
                found.append(part)
    found.extend(["a", "tr", "table", "td", "th"])
    return found


def _sig(node):
    attrs = node.attributes or {}
    return (
        node.tag,
        attrs.get("id") or "",
        " ".join((attrs.get("class") or "").split()),
        node.text(deep=True),
    )


def _rank(css):
    results = []
    for pattern in DOM_PATTERNS.values():
        total = 0
        best = None
        for part in [item.strip() for item in pattern["selector"].split(",") if item.strip()]:
            nodes = css(part)
            if nodes:
                total += len(nodes)
                if best is None:
                    best = part
        if total:
            bonus = 2 if pattern["key"] in {"generic_main", "reader_page"} else 10
            results.append({
                "pattern": dict(pattern),
                "score": total + bonus,
                "matched_nodes": total,
                "selector_used": best or pattern["selector"],
            })
    results.sort(key=lambda item: (item["score"], item["matched_nodes"]), reverse=True)
    return results


def _with_lexbor(module, html, url=""):
    previous = module.HtmlTree
    module.HtmlTree = LexborHTMLParser
    try:
        return module.parse(html, url)
    finally:
        module.HtmlTree = previous


def test_saved_documents_match_lexbor_selectors_and_pattern_rank():
    selectors = _subselectors()
    for name, html in _saved_documents():
        std = HtmlTree(html)
        lex = LexborHTMLParser(html)
        for selector in selectors:
            assert [_sig(node) for node in std.css(selector)] == [_sig(node) for node in lex.css(selector)], (
                name, selector)
        assert detect_pattern(html) == _rank(lex.css), name


def test_npb_reports_match_lexbor_on_saved_and_representative_pages():
    calendar = (ROOT / "tests" / "fixtures" / "npb_calendar_sample.html").read_text(encoding="utf-8")
    calendar_url = "https://npb.jp/bis/2024/calendar/index_04.html"
    labelled = (
        "<div class='stvsteam'><div class='tescheaten'>CS ファーストS</div>"
        "<div><a href='/bis/2013/games/s2013101200001.html'>神 2 - 1 広</a></div></div>"
        "<div class='stvsteam'><div><a href='/bis/2013/games/s2013101200002.html'>楽 3 - 2 オ</a></div></div>"
    )
    cases = [
        (npb_calendar, calendar, calendar_url),
        (npb_calendar, labelled, "https://npb.jp/bis/2013/calendar/index_10.html"),
        (npb_calendar,
         '<table><tr><td><a href="/bis/2024/games/s2024040201097.html">中 4 - 3 巨<td>次のセル',
         calendar_url),
        (npb_schedule_current, '<tr><td>巨人 <a href="https://npb.jp/scores/2026/0901/g-db-20/">4 - 3</a> DeNA</td></tr>',
         SCHEDULE_URL),
        (npb_game_linescore,
         "<table><tr>" + "".join(f"<td>{cell}</td>" for cell in ["読 売", "0", "0", "0", "3", "0", "0", "0", "0", "0", "0", "0", "-", "3", "11", "0"])
         + "</tr><tr>" + "".join(f"<td>{cell}</td>" for cell in ["中 日", "0", "0", "0", "0", "0", "1", "2", "0", "0", "0", "1X", "-", "4", "9", "1"])
         + "</tr></table>",
         LINE_URL),
        (npb_team_batting,
         "<table><tr><th>チーム</th><th>打率</th><th>試合</th></tr>"
         "<tr><td>中日</td><td>.250</td><td>143</td></tr></table>",
         BATTING_URL),
    ]
    provenance = json.loads((ROOT / "tests" / "fixtures" / "npb_annual" / "provenance.json").read_text(encoding="utf-8"))
    for row in provenance:
        html = (ROOT / "tests" / "fixtures" / "npb_annual" / row["file"]).read_text(encoding="utf-8")
        cases.append((npb_team_annual, html, row["source_url"]))
    for module, html, url in cases:
        assert module.parse(html, url) == _with_lexbor(module, html, url), module.__name__


def test_implied_tbody_differs_but_row_text_matches():
    html = "<table><tr><td>A</td></tr></table>"
    assert [node.text(deep=True) for node in HtmlTree(html).css("tr")] == ["A"]
    assert [node.text(deep=True) for node in LexborHTMLParser(html).css("tr")] == ["A"]
    assert HtmlTree(html).css("tbody") == []
    assert len(LexborHTMLParser(html).css("tbody")) == 1


def test_missing_tr_is_invisible_to_the_stdlib_tree():
    html = "<table><td>cell</td></table>"
    assert HtmlTree(html).css("tr") == []
    assert [node.text(deep=True) for node in HtmlTree(html).css("td")] == ["cell"]
    assert [node.text(deep=True) for node in LexborHTMLParser(html).css("tr")] == ["cell"]


def test_nested_anchor_text_includes_the_inner_anchor():
    html = '<a href="1">A<a href="2">B</a></a>'
    std = [(node.attributes.get("href"), node.text(deep=True)) for node in HtmlTree(html).css("a")]
    lex = [(node.attributes.get("href"), node.text(deep=True)) for node in LexborHTMLParser(html).css("a")]
    assert std == [("1", "AB"), ("2", "B")]
    assert lex == [("1", "A"), ("2", "B")]


def test_template_contents_stay_in_the_stdlib_tree():
    html = "<template><main id='hidden'>H</main></template><main id='shown'>S</main>"
    std = [(node.attributes.get("id"), node.text(deep=True)) for node in HtmlTree(html).css("main")]
    lex = [(node.attributes.get("id"), node.text(deep=True)) for node in LexborHTMLParser(html).css("main")]
    assert std == [("hidden", "H"), ("shown", "S")]
    assert lex == [("shown", "S")]
    std_rank = {item["pattern"]["key"]: item["matched_nodes"] for item in detect_pattern(html)}
    lex_rank = {item["pattern"]["key"]: item["matched_nodes"] for item in _rank(LexborHTMLParser(html).css)}
    assert std_rank["documentation_main"] == 2
    assert lex_rank["documentation_main"] == 1
