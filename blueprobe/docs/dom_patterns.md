# DOM structure patterns and preset design

The whole implementation is the single file [`blueprobe.py`](../blueprobe.py) (types are TypedDicts in the same file). At run time it uses only the standard library's `html.parser`; selectolax is only for cross-checking in tests.

When BlueProbe extracts specific main content from the DOM structure of saved HTML, instead of specifying CSS selectors directly,
it lets you select and classify DOM pattern identifiers that can be chosen from a dropdown/preset (`github_readme`, `portfolio_profile`, etc.).

## Defined DOM patterns

| Pattern key (`key`) | Category | Label | CSS selector (`selector`) | Example targets |
|---|---|---|---|---|
| `github_readme` | `repository_readme` | GitHub README / Markdown Body | `article.markdown-body, .markdown-body` | GitHub, Gitea, npm README |
| `article_body` | `article_reader` | Article / Blog Main Body | `article, [role='main'] article, .article-body, .entry-content, .post-content` | Blog and news article bodies |
| `documentation_main` | `documentation` | Documentation Main Section | `main, [role='main'], article.doc-content, .docs-content, .md-content` | Read the Docs, Docusaurus |
| `portfolio_profile` | `portfolio_bio` | Portfolio / Profile Section | `section#about, #about, .profile, .portfolio, section.bio, #portfolio` | Portfolios and self-introductions |
| `reader_page` | `reader_view` | Distraction-free Reader View | `#reader-content, .reader-view, article, main` | Reader mode and web clips |
| `npb_calendar` | `npb_sports` | NPB Schedule Calendar Table | `#calendar, .calendar, table.calendar` | NPB official game calendar tables |
| `npb_linescore` | `npb_sports` | NPB Game Linescore Table | `table.score_table, .linescore, #linescore` | NPB game line score tables |
| `generic_main` | `generic` | Generic Main Region | `main, #main, #content, .main-content` | main of general web pages |
| `social_timeline` | `social` | Social Timeline / Comment Thread | `[role='feed'], [role='feed'] > article, .timeline, .thread-comments, .comment-list` | Social media timelines and comment sections |
| `ecommerce_product` | `ecommerce` | E-commerce Product Detail / Grid | `[itemtype='https://schema.org/Product'], [itemtype='http://schema.org/Product'], [itemprop='price'], .product-detail, .product-grid` | Product details and product listings |
| `forum_qa` | `forum` | Q&A / Forum Question and Answers | `[itemtype='https://schema.org/Question'], [itemtype='https://schema.org/Answer'], [itemprop='acceptedAnswer'], [itemprop='suggestedAnswer'], .question, .answer` | Q&A sites and forums |
| `dashboard_grid` | `dashboard` | Dashboard Card / Widget Grid | `.dashboard, .widget-card, .grid-item, .card-grid` | Analytics and admin screens |

Every selector stays within what `HtmlTree` accepts (tags, `#id`, `.class`, `[attr]`, `[attr=value]`, descendants, `>`).
Partial matches like `[itemtype*=...]` aren't available, so schema.org URLs are listed as exact matches.

## Usage

### Specifying a preset in Python code (`HtmlSource`)

```python
from html_source import HtmlSource

# Specify by pattern key (selector is set automatically)
source = HtmlSource(pattern="github_readme")
report = source.parse(html, url)
```

### Automatic pattern detection (`detect_pattern`)

Analyzes the DOM structure and returns matching patterns in candidate order (by score).

```python
import blueprobe

matches = blueprobe.detect_pattern(html)
if matches:
    top_pattern = matches[0]["pattern"]
    print(f"Detected pattern: {top_pattern['key']} ({top_pattern['label']})")
```

### Listing and specifying from the CLI

```bash
# Show the available patterns
uv run python blueprobe.py --list-patterns

# Reparse with a specific pattern preset
uv run python blueprobe.py --source html_source --pattern github_readme --cache <QueRyu cache>
```

`--pattern` is only for `--source html_source`. Combining it with another source,
or an unknown or empty pattern name, is a CLI error (exit code 2) before the cache is read.
Case and surrounding whitespace are normalized the same way as `get_pattern()`.
`--list-patterns` needs no source or cache, and can't be combined with `--pattern`.
Reparsing uses saved bodies and verified snapshots and does not refetch over the network.

The default extractor requires a `mcp-toolcall-lab` that supports comma-separated selectors
and `[role='main']` ([compatibility fix PR #140](https://github.com/myon-bioinformatics/mcp-toolcall-lab/pull/140)).
CI pins a commit with that support and reparses all 8 presets with the real extractor.

## Document classification (`classify_document`) and output contract

`detect_pattern()` orders only by the number of selector hits (unchanged for existing compatibility).
`classify_document(html)` additionally doesn't count empty elements, and observes structured data, Shadow DOM, table kinds, and empty CSR shells.
**Observation and extraction only**; no conversion or formatting (conversion is a separate project; sorting and filtering are QueRyu's job).

CLI: `uv run python blueprobe.py --classify saved.html` (outputs JSON, no network)

### Shape of derived (`blueprobe-dom-classification/1`)

```json
{
  "schema": "blueprobe-dom-classification/1",
  "status": "matched | fallback | client_rendered | insufficient | empty",
  "patterns": [{"pattern": {"key": "...", "label": "...", "category": "...", "selector": "...",
                "description": "...", "example_sites": []},
                "score": 0, "matched_nodes": 0, "selector_used": "<partial selector> | structured_data"}],
  "signals": ["hashed_class_names", "declarative_shadow_dom", "multiple_articles", "nested_articles",
              "layout_tables", "json_ld", "json_ld_invalid", "microdata", "opengraph",
              "empty_app_shell", "fallback:main_landmark | fallback:article | fallback:body"],
  "landmarks": {"main": 1, "article": 2, "role=main": 1},
  "articles": {"total": 0, "top_level": 0, "nested": 0},
  "structured_data": {"json_ld_types": ["Product"], "json_ld_invalid": 0,
                      "microdata_types": ["https://schema.org/Product"], "itemprops": ["name", "price"],
                      "opengraph": {"og:type": "product"}},
  "shadow_roots": {"open": 0, "closed": 0},
  "tables": [{"index": 0, "kind": "data | layout", "reasons": ["th", "caption"], "rows": 2, "nested": false}],
  "text_chars": 0,
  "hashed_class_ratio": 0.0
}
```

Downstream depends only on this shape. Removing a key or changing its meaning bumps the `schema` version.

### Meaning of status

| status | Condition |
|---|---|
| `empty` | The input is empty |
| `client_rendered` | Fewer than 20 visible characters, with an empty mount point such as `#app` / `#root` / `#__next`, or a script with `src` or of type module (an empty CSR shell). `patterns` is left empty to avoid misclassification |
| `insufficient` | Fewer than 20 visible characters, and no sign of an empty shell |
| `matched` | A preset other than the generic ones (`generic_main` / `reader_page`) hit an element with text via a partial selector other than `main` / `[role='main']` / `#main` / `#content` |
| `fallback` | Anything else. When there are no named classes, e.g. due to obfuscated classes (`sc-…`, `css-…`, CSS Modules), the judgement relies only on hits from HTML5 semantic tags and ARIA roles |

### Observation rules

- **Structured data**: JSON-LD (`script[type=application/ld+json]`, also picking up `@graph` and nested `@type`), microdata (`itemscope` + `itemtype`, `itemprop`), OpenGraph (`meta[property^=og:]`). Types are used only as classification hints (score +5); if nothing hits in the DOM, it becomes `matched_nodes: 0`, `selector_used: "structured_data"`
- **Declarative Shadow DOM**: the contents of `<template shadowrootmode="open|closed">` count as visible text. A plain `<template>` doesn't
- **article**: nested (comments, etc.) and top-level are counted separately
- **Tables**: a data table if it has `th` / `caption` / `thead` / `scope`. A layout table if any of: `role=presentation|none`, contains a table, block elements in cells without headers, or one row or fewer without headers
- Visible text excludes `script` / `style` / `noscript` / plain `template`

### Not yet tried

- DOM after JS execution (CSR is only judged as an empty shell, not rendered)
- Imperative Shadow DOM created by `attachShadow()`, iframe contents
- Text drawn with Canvas / WebGL
- RDFa（`vocab` / `typeof`）
- Accuracy evaluation with saved HTML from real sites (all current fixtures are handwritten)
