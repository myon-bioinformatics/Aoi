"""🧩 DOM pattern table, selector grammar and document classification (docs/dom-patterns.md). No network.

- patterns: the generic pattern registry, HtmlTree selectors and the explicit NPB presets (npb_patterns).
- classification: hand-written fixtures for structures the original presets did not cover.
"""

import json

import pytest

import blueprobe
from blueprobe import HtmlSource, HtmlTree, classify_document, detect_pattern


# ──── patterns ────────────────────────────────────────────────────

def test_dom_patterns_shim_is_gone():
    import importlib.util

    assert importlib.util.find_spec("dom_patterns") is None
    assert blueprobe.SCHEMA == "blueprobe-dom-patterns/1"


@pytest.mark.parametrize("selector", ["li + li", "li ~ li", "li:nth-child(2)", "[class^='foo']", "li:not(.a)", "a, b"])
def test_html_tree_rejects_selectors_outside_the_supported_grammar(selector):
    with pytest.raises(ValueError, match="unsupported selector"):
        HtmlTree("<ul><li class='a'>1</li><li class='b'>2</li></ul>").css(selector)


def test_list_patterns_and_categories_structure():
    patterns = blueprobe.list_patterns()
    assert isinstance(patterns, list)
    assert len(patterns) >= 8
    keys = [p["key"] for p in patterns]
    assert "github_readme" in keys
    assert "article_body" in keys
    assert "documentation_main" in keys
    assert "portfolio_profile" in keys
    assert "reader_page" in keys
    assert "npb_calendar" not in keys
    assert "npb_linescore" not in keys
    assert "generic_main" in keys

    for p in patterns:
        assert set(p.keys()) >= {"key", "label", "category", "selector", "description", "example_sites"}

    categories = blueprobe.list_categories()
    cat_keys = [c["key"] for c in categories]
    assert "repository_readme" in cat_keys
    assert "portfolio_bio" in cat_keys


def test_get_pattern_valid_and_invalid():
    readme_pattern = blueprobe.get_pattern("github_readme")
    assert readme_pattern["key"] == "github_readme"
    assert readme_pattern["category"] == "repository_readme"
    assert readme_pattern["selector"] == "article.markdown-body, .markdown-body"

    portfolio_pattern = blueprobe.get_pattern("PORTFOLIO_PROFILE")
    assert portfolio_pattern["key"] == "portfolio_profile"

    with pytest.raises(ValueError, match="unknown pattern key"):
        blueprobe.get_pattern("invalid_pattern_xyz")

    with pytest.raises(ValueError, match="must be a non-empty string"):
        blueprobe.get_pattern("")


def test_html_source_initialization_with_pattern():
    source = HtmlSource(pattern="github_readme")
    assert source.pattern == "github_readme"
    assert source.selector == "article.markdown-body, .markdown-body"

    override_source = HtmlSource(pattern="github_readme", selector="main")
    assert override_source.pattern == "github_readme"
    assert override_source.selector == "main"


def test_detect_pattern_classifies_github_readme():
    html = """
    <html>
      <body>
        <header>Header</header>
        <article class="markdown-body">
          <h1>Project Title</h1>
          <p>Description text for repo</p>
        </article>
      </body>
    </html>
    """
    matches = blueprobe.detect_pattern(html)
    assert matches
    top_match = matches[0]
    assert top_match["pattern"]["key"] == "github_readme"
    assert top_match["matched_nodes"] >= 1


def test_detect_pattern_classifies_portfolio_profile():
    html = """
    <html>
      <body>
        <nav>Navigation</nav>
        <section id="about" class="profile">
          <h2>About Me</h2>
          <p>Software Engineer & Portfolio Bio</p>
        </section>
      </body>
    </html>
    """
    matches = blueprobe.detect_pattern(html)
    assert matches
    top_match = matches[0]
    assert top_match["pattern"]["key"] == "portfolio_profile"


def test_detect_pattern_classifies_documentation_main():
    html = """
    <html>
      <body>
        <aside>Sidebar</aside>
        <main class="docs-content">
          <h1>API Documentation</h1>
          <p>Endpoints and guide</p>
        </main>
      </body>
    </html>
    """
    matches = blueprobe.detect_pattern(html)
    assert matches
    top_match = matches[0]
    assert top_match["pattern"]["key"] == "documentation_main"


def test_detect_pattern_empty_or_no_match():
    assert blueprobe.detect_pattern("") == []
    assert blueprobe.detect_pattern("   ") == []

    no_match_html = "<div><span>Just a simple div</span></div>"
    matches = blueprobe.detect_pattern(no_match_html)
    # Simple div shouldn't match specialized selectors like github_readme or portfolio_profile
    keys = [m["pattern"]["key"] for m in matches]
    assert "github_readme" not in keys
    assert "portfolio_profile" not in keys


def test_optional_npb_presets_preserved():
    import npb_patterns
    assert set(npb_patterns.DOM_PATTERNS) == {"npb_calendar", "npb_linescore"}
    for pattern in npb_patterns.DOM_PATTERNS.values():
        source = HtmlSource(selector=pattern["selector"])
        assert source.selector == pattern["selector"]


def test_isolated_generic_cli_has_no_npb(tmp_path):
    import subprocess, sys
    from pathlib import Path
    source = Path(blueprobe.__file__).read_bytes()
    assert b'npb' not in source.lower()
    entry = tmp_path / "blueprobe.py"
    entry.write_bytes(source)
    for args in (["--help"], ["--list-patterns"]):
        result = subprocess.run([sys.executable, "-I", "-S", str(entry), *args], cwd=tmp_path, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "npb" not in result.stdout.lower()


@pytest.mark.parametrize("args", [[], ["--classify", "page.html"], ["names", "page.html", "--json"], ["headings", "page.html", "--json"], ["emoji", "page.html", "--json"]])
def test_isolated_stdlib_default_and_local_html(tmp_path, args):
    import json, os, subprocess, sys
    from pathlib import Path
    entry = tmp_path / "blueprobe.py"
    entry.write_bytes(Path(blueprobe.__file__).read_bytes())
    (tmp_path / "page.html").write_text('<main><h1>Title</h1><button>Go</button><p>😀</p></main>', encoding="utf-8")
    # A sibling optional component must not be imported by generic local commands.
    (tmp_path / "cache_core.py").write_text("raise AssertionError('unexpected optional import')\n")
    # Empty PATH proves these commands do not need curl or sibling executables.
    result = subprocess.run([sys.executable, "-I", "-S", str(entry), *args], cwd=tmp_path,
                            env={**os.environ, "PATH": "", "PYTHONPATH": ""}, capture_output=True, text=True)
    if not args:
        assert result.returncode == 2
        assert "--source and --cache are required" in result.stderr
        assert "Traceback" not in result.stderr
    else:
        assert result.returncode == 0, result.stderr
        assert isinstance(json.loads(result.stdout), (dict, list))


def test_research_lookup_does_not_mutate_generic_registry():
    import npb_patterns
    before = blueprobe.list_patterns()
    assert npb_patterns.get_pattern("npb_linescore")["selector"] == "table.score_table, .linescore, #linescore"
    metadata = npb_patterns.get_pattern("npb_linescore")
    metadata["example_sites"].clear()
    assert npb_patterns.get_pattern("npb_linescore")["example_sites"]
    npb_patterns.html_source("npb_linescore")
    assert blueprobe.list_patterns() == before
    with pytest.raises(ValueError, match="unknown pattern key"):
        blueprobe.get_pattern("npb_linescore")


# ──── classification ──────────────────────────────────────────────

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
