"""Hand-written fixtures for structures the original presets did not cover. No network."""
import json

import pytest

import blueprobe
from blueprobe import HtmlTree, classify_document, detect_pattern

NEW = ["social_timeline", "ecommerce_product", "forum_qa", "dashboard_grid"]

SOCIAL = """<main><div role="feed">
<article><p>first post body text</p></article><article><p>second post body text</p></article>
</div><ul class="comment-list"><li>nice comment here</li></ul></main>"""
PRODUCT = """<div itemscope itemtype="https://schema.org/Product">
<h1 itemprop="name">Blue Mug</h1><span itemprop="price" content="1200">¥1,200</span>
</div><ul class="product-grid"><li>Red Mug ¥900</li></ul>"""
FORUM = """<div itemscope itemtype="https://schema.org/QAPage"><div class="question" itemprop="mainEntity"
 itemscope itemtype="https://schema.org/Question"><h1 itemprop="name">How to parse HTML?</h1>
<div itemprop="acceptedAnswer" itemscope itemtype="https://schema.org/Answer" class="answer">Use html.parser.</div>
</div></div>"""
DASHBOARD = """<div class="dashboard"><div class="card-grid">
<div class="widget-card">Visitors 1,234</div><div class="widget-card">Sales 56</div></div></div>"""


def _top(html):
    return classify_document(html)["patterns"][0]["pattern"]["key"]


def test_new_presets_are_listed_and_resolvable(capsys):
    keys = [p["key"] for p in blueprobe.list_patterns()]
    cats = {c["key"] for c in blueprobe.list_categories()}
    for key in NEW:
        assert key in keys
        assert blueprobe.get_pattern(key)["category"] in cats
    assert blueprobe.main(["--list-patterns"]) == 0
    out = capsys.readouterr().out
    assert all(key in out for key in NEW)


def test_every_selector_part_stays_in_supported_grammar():
    tree = HtmlTree("<p>x</p>")
    for pattern in blueprobe.DOM_PATTERNS.values():
        for part in pattern["selector"].split(","):
            tree.css(part.strip())


@pytest.mark.parametrize("html,key", [(SOCIAL, "social_timeline"), (PRODUCT, "ecommerce_product"),
                                      (FORUM, "forum_qa"), (DASHBOARD, "dashboard_grid")])
def test_new_presets_classify_hand_written_fixtures(html, key):
    result = classify_document(html)
    assert result["status"] == "matched"
    assert _top(html) == key
    assert detect_pattern(html)[0]["pattern"]["key"] == key


def test_structured_data_signals_json_ld_microdata_opengraph():
    html = """<head><meta property="og:type" content="product"><meta property="og:title" content="Mug">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Product",
"offers":{"@type":"Offer","price":"1200"}}]}</script><script type="application/ld+json">{broken</script></head>
<body><div class="x"><p>A plain looking page with enough text to classify.</p></div></body>"""
    result = classify_document(html)
    sd = result["structured_data"]
    assert sd["json_ld_types"] == ["Product", "Offer"]
    assert sd["json_ld_invalid"] == 1
    assert sd["opengraph"] == {"og:type": "product", "og:title": "Mug"}
    assert {"json_ld", "json_ld_invalid", "opengraph"} <= set(result["signals"])
    # Structured data alone is a signal: ecommerce ranks, but no DOM node matched.
    top = result["patterns"][0]
    assert top["pattern"]["key"] == "ecommerce_product"
    assert top["matched_nodes"] == 0 and top["selector_used"] == "structured_data"
    assert result["status"] == "fallback"
    assert "microdata" in classify_document(FORUM)["signals"]
    assert classify_document(FORUM)["structured_data"]["microdata_types"][0] == "https://schema.org/QAPage"


def test_hashed_class_names_fall_back_to_semantic_tags_and_aria():
    html = """<div class="sc-1ab2cd3 css-9012af"><div class="Zx3k9q a8B7c6d"><nav class="css-77aa11">menu</nav>
<div role="main" class="sc-4ef5gh6"><p class="x3k9qz">Body text that matters for reading.</p></div></div></div>"""
    result = classify_document(html)
    assert "hashed_class_names" in result["signals"]
    assert result["hashed_class_ratio"] >= 0.5
    assert result["status"] == "fallback"
    assert "fallback:main_landmark" in result["signals"]
    assert result["patterns"][0]["selector_used"] == "[role='main']"
    # Ordinary utility classes are not counted as hashed.
    assert classify_document("<main class='col-md-6 mt-4 container'>enough text to read here ok</main>")[
        "hashed_class_ratio"] == 0.0


def test_declarative_shadow_dom_is_counted_and_its_text_is_seen():
    html = """<blog-post><template shadowrootmode="open"><article><p>Text inside a shadow root.</p></article>
</template></blog-post><x-card><template shadowrootmode="closed"><p>closed part</p></template></x-card>
<template><p>inert template must not count</p></template>"""
    result = classify_document(html)
    assert result["shadow_roots"] == {"open": 1, "closed": 1}
    assert "declarative_shadow_dom" in result["signals"]
    assert result["status"] == "matched"
    assert result["patterns"][0]["pattern"]["key"] == "article_body"
    assert "inert" not in json.dumps(result)


@pytest.mark.parametrize("html", [
    '<html><body><div id="app"></div><script type="module" src="/main.js"></script></body></html>',
    '<div id="root"></div><script src="/bundle.js"></script>',
    '<main id="__next"></main><script src="/_next/app.js"></script>',
])
def test_csr_empty_shell_is_client_rendered_not_a_false_match(html):
    result = classify_document(html)
    assert result["status"] == "client_rendered"
    assert result["patterns"] == []
    assert "empty_app_shell" in result["signals"]


def test_short_static_page_without_shell_is_insufficient_and_empty_is_empty():
    assert classify_document("<p>hi</p>")["status"] == "insufficient"
    assert classify_document("   ")["status"] == "empty"


def test_nested_and_multiple_articles_are_counted():
    html = """<main><article><h2>Post A body text</h2><article class="comment">reply one</article>
<article class="comment">reply two</article></article><article><h2>Post B body text</h2></article></main>"""
    result = classify_document(html)
    assert result["articles"] == {"total": 4, "top_level": 2, "nested": 2}
    assert {"multiple_articles", "nested_articles"} <= set(result["signals"])


def test_data_tables_and_layout_tables_are_distinguished():
    html = """<table role="presentation"><tr><td><div>sidebar</div></td><td>
<table><caption>Standings</caption><thead><tr><th scope="col">Team</th><th>W</th></tr></thead>
<tr><td>Dragons</td><td>70</td></tr></table></td></tr></table>
<table><tr><td><div><p>layout cell only</p></div></td></tr></table>"""
    tables = classify_document(html)["tables"]
    assert [t["kind"] for t in tables] == ["layout", "data", "layout"]
    assert "role=presentation" in tables[0]["reasons"] and "contains_table" in tables[0]["reasons"]
    assert tables[1]["nested"] is True and "caption" in tables[1]["reasons"]
    assert tables[1]["rows"] == 2


def test_classify_cli_prints_json(tmp_path, capsys):
    page = tmp_path / "p.html"
    page.write_text(PRODUCT, encoding="utf-8")
    assert blueprobe.main(["--classify", str(page)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["schema"] == "blueprobe-dom-classification/1"
    assert data["status"] == "matched"


@pytest.mark.parametrize("html", [SOCIAL, PRODUCT, FORUM, DASHBOARD])
def test_new_selectors_match_lexbor(html):
    lexbor = pytest.importorskip("selectolax.lexbor")
    lex = lexbor.LexborHTMLParser(html)
    tree = HtmlTree(html)
    for key in NEW:
        for part in blueprobe.DOM_PATTERNS[key]["selector"].split(","):
            part = part.strip()
            assert len(tree.css(part)) == len(lex.css(part)), (key, part)
