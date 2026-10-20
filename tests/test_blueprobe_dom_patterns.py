import pytest

import blueprobe
import dom_patterns
from blueprobe import HtmlTree
from html_source import HtmlSource


def test_dom_patterns_module_reexports_blueprobe():
    assert dom_patterns.detect_pattern is blueprobe.detect_pattern
    assert dom_patterns.get_pattern is blueprobe.get_pattern
    assert dom_patterns.get_selector_for_pattern is blueprobe.get_selector_for_pattern
    assert dom_patterns.list_patterns is blueprobe.list_patterns
    assert dom_patterns.DOM_PATTERNS is blueprobe.DOM_PATTERNS
    assert dom_patterns.SCHEMA == "blueprobe-dom-patterns/1"


@pytest.mark.parametrize("selector", ["li + li", "li ~ li", "li:nth-child(2)", "[class^='foo']", "li:not(.a)", "a, b"])
def test_html_tree_rejects_selectors_outside_the_supported_grammar(selector):
    with pytest.raises(ValueError, match="unsupported selector"):
        HtmlTree("<ul><li class='a'>1</li><li class='b'>2</li></ul>").css(selector)


def test_list_patterns_and_categories_structure():
    patterns = dom_patterns.list_patterns()
    assert isinstance(patterns, list)
    assert len(patterns) >= 8
    keys = [p["key"] for p in patterns]
    assert "github_readme" in keys
    assert "article_body" in keys
    assert "documentation_main" in keys
    assert "portfolio_profile" in keys
    assert "reader_page" in keys
    assert "npb_calendar" in keys
    assert "npb_linescore" in keys
    assert "generic_main" in keys

    for p in patterns:
        assert set(p.keys()) >= {"key", "label", "category", "selector", "description", "example_sites"}

    categories = dom_patterns.list_categories()
    cat_keys = [c["key"] for c in categories]
    assert "repository_readme" in cat_keys
    assert "portfolio_bio" in cat_keys


def test_get_pattern_valid_and_invalid():
    readme_pattern = dom_patterns.get_pattern("github_readme")
    assert readme_pattern["key"] == "github_readme"
    assert readme_pattern["category"] == "repository_readme"
    assert readme_pattern["selector"] == "article.markdown-body, .markdown-body"

    portfolio_pattern = dom_patterns.get_pattern("PORTFOLIO_PROFILE")
    assert portfolio_pattern["key"] == "portfolio_profile"

    with pytest.raises(ValueError, match="unknown pattern key"):
        dom_patterns.get_pattern("invalid_pattern_xyz")

    with pytest.raises(ValueError, match="must be a non-empty string"):
        dom_patterns.get_pattern("")


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
    matches = dom_patterns.detect_pattern(html)
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
    matches = dom_patterns.detect_pattern(html)
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
    matches = dom_patterns.detect_pattern(html)
    assert matches
    top_match = matches[0]
    assert top_match["pattern"]["key"] == "documentation_main"


def test_detect_pattern_empty_or_no_match():
    assert dom_patterns.detect_pattern("") == []
    assert dom_patterns.detect_pattern("   ") == []

    no_match_html = "<div><span>Just a simple div</span></div>"
    matches = dom_patterns.detect_pattern(no_match_html)
    # Simple div shouldn't match specialized selectors like github_readme or portfolio_profile
    keys = [m["pattern"]["key"] for m in matches]
    assert "github_readme" not in keys
    assert "portfolio_profile" not in keys
