"""DOM Structure Pattern Collection & Classification Module.

Provides preset pattern definitions, categorizations, and matching helpers
for common HTML/DOM page layouts (e.g., GitHub README, Reader View, Documentation,
Portfolio/Profile sections, NPB tables, Generic Main).

Allows selecting CSS extraction selectors via dropdown choices or preset keys
rather than manually entering CSS rules.
"""
from __future__ import annotations

try:
    from selectolax.lexbor import LexborHTMLParser as HTMLParser
except ImportError:
    from selectolax.parser import HTMLParser

SCHEMA = "blueprobe-dom-patterns/1"

CATEGORIES = [
    {"key": "repository_readme", "label": "リポジトリ README / Markdown プレビュー"},
    {"key": "article_reader", "label": "記事・ブログ・ニュース本文 (Article / Reader)"},
    {"key": "documentation", "label": "技術ドキュメント・解説ページ (Documentation)"},
    {"key": "portfolio_bio", "label": "ポートフォリオ・自己紹介・Profile 領域"},
    {"key": "reader_view", "label": "テキスト重視リーダービュー (Reader View)"},
    {"key": "npb_sports", "label": "NPB（プロ野球）公式日程・成績表"},
    {"key": "generic", "label": "汎用メインコンテンツ領域 (Generic Main)"},
]

DOM_PATTERNS = {
    "github_readme": {
        "key": "github_readme",
        "label": "GitHub README / Markdown Body",
        "category": "repository_readme",
        "selector": "article.markdown-body, .markdown-body",
        "description": "GitHub や Git ホスティングサービスの README プレビュー・Markdown 描画領域",
        "example_sites": ["GitHub", "Forgejo / Gitea", "npm / PyPI README"],
    },
    "article_body": {
        "key": "article_body",
        "label": "Article / Blog Main Body",
        "category": "article_reader",
        "selector": "article, [role='main'] article, .article-body, .entry-content, .post-content",
        "description": "ニュース記事・技術ブログ・メディアサイトの主要記事本文領域",
        "example_sites": ["Tech Blogs", "News Articles", "WordPress Posts"],
    },
    "documentation_main": {
        "key": "documentation_main",
        "label": "Documentation Main Section",
        "category": "documentation",
        "selector": "main, [role='main'], article.doc-content, .docs-content, .md-content",
        "description": "技術ドキュメントやライブラリ解説ページのメインコンテンツ領域",
        "example_sites": ["Read the Docs", "Docusaurus", "MkDocs", "Sphinx"],
    },
    "portfolio_profile": {
        "key": "portfolio_profile",
        "label": "Portfolio / Profile Section",
        "category": "portfolio_bio",
        "selector": "section#about, #about, .profile, .portfolio, section.bio, #portfolio",
        "description": "ポートフォリオサイトや開発者・著者の自己紹介 (About/Profile) 領域",
        "example_sites": ["Personal Portfolio", "GitHub Pages Portfolio", "Resume Sites"],
    },
    "reader_page": {
        "key": "reader_page",
        "label": "Distraction-free Reader View",
        "category": "reader_view",
        "selector": "#reader-content, .reader-view, article, main",
        "description": "リーダーモードやノイズを除去したテキスト閲覧領域",
        "example_sites": ["Reader View", "Web Clipper", "Simplified Article"],
    },
    "npb_calendar": {
        "key": "npb_calendar",
        "label": "NPB Schedule Calendar Table",
        "category": "npb_sports",
        "selector": "#calendar, .calendar, table.calendar",
        "description": "プロ野球（NPB）公式戦の月別・チーム別日程カレンダー表",
        "example_sites": ["npb.jp bis calendar"],
    },
    "npb_linescore": {
        "key": "npb_linescore",
        "label": "NPB Game Linescore Table",
        "category": "npb_sports",
        "selector": "table.score_table, .linescore, #linescore",
        "description": "プロ野球（NPB）試合ページの得点表（ラン・ヒット・エラー）",
        "example_sites": ["npb.jp linescore"],
    },
    "generic_main": {
        "key": "generic_main",
        "label": "Generic Main Region",
        "category": "generic",
        "selector": "main, #main, #content, .main-content",
        "description": "HTML5 標準の main タグおよび一般的な主要コンテンツ領域",
        "example_sites": ["Generic Web Pages"],
    },
}


def list_patterns() -> list[dict]:
    """Return all pattern metadata dicts for dropdown UI choices or CLI selection."""
    return [dict(p) for p in DOM_PATTERNS.values()]


def list_categories() -> list[dict]:
    """Return category options."""
    return [dict(c) for c in CATEGORIES]


def get_pattern(pattern_key: str) -> dict:
    """Retrieve pattern metadata dict by key or alias.

    Raises ValueError if pattern_key is unknown.
    """
    if not isinstance(pattern_key, str) or not pattern_key.strip():
        raise ValueError("pattern_key must be a non-empty string")
    key = pattern_key.strip().lower()
    if key not in DOM_PATTERNS:
        valid_keys = ", ".join(sorted(DOM_PATTERNS.keys()))
        raise ValueError(f"unknown pattern key {pattern_key!r}. Valid keys: {valid_keys}")
    return dict(DOM_PATTERNS[key])


def get_selector_for_pattern(pattern_key: str) -> str:
    """Get the CSS selector corresponding to a pattern key."""
    return get_pattern(pattern_key)["selector"]


def detect_pattern(html: str) -> list[dict]:
    """Analyze DOM HTML and return candidate pattern matches ranked by match score.

    Score is based on selector presence and node matching count.
    Returns list of dicts:
      [{"pattern": pattern_dict, "score": int, "matched_nodes": int, "selector_used": str}, ...]
    """
    if not isinstance(html, str) or not html.strip():
        return []
    tree = HTMLParser(html)
    results = []
    for pattern in DOM_PATTERNS.values():
        selector = pattern["selector"]
        sub_selectors = [s.strip() for s in selector.split(",") if s.strip()]
        total_matched = 0
        best_sub_selector = None
        for sub in sub_selectors:
            try:
                nodes = tree.css(sub)
                if nodes:
                    count = len(nodes)
                    total_matched += count
                    if best_sub_selector is None:
                        best_sub_selector = sub
            except Exception:
                continue
        if total_matched > 0:
            # Score gives preference to specific selectors (e.g. github_readme) over broad ones (e.g. generic_main)
            specificity_bonus = 10 if pattern["key"] not in ("generic_main", "reader_page") else 2
            score = total_matched + specificity_bonus
            results.append({
                "pattern": dict(pattern),
                "score": score,
                "matched_nodes": total_matched,
                "selector_used": best_sub_selector or selector,
            })
    results.sort(key=lambda r: (r["score"], r["matched_nodes"]), reverse=True)
    return results
