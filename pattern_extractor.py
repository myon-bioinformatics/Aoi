"""QueRyu — Clean Pattern Extractor for DOM Structures and HAR Archives.

Extracts cleaned text, structural HTML, headings, tags, links, and tabular data
from HTML content, QueRyu html-snapshot/1 objects, or HAR archives based on
high-utility DOM structure patterns (e.g., GitHub README, article body, docs,
portfolio profile, sports calendar/linescore, generic main).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from selectolax.lexbor import LexborHTMLParser as HTMLParser
except ImportError:
    try:
        from selectolax.parser import HTMLParser
    except ImportError:
        HTMLParser = None  # Fallback for systems without selectolax


SCHEMA = "queryu-extracted-pattern/1"

DOM_PATTERNS = {
    "github_readme": {
        "key": "github_readme",
        "label": "GitHub README / Markdown Body",
        "selector": "article.markdown-body, .markdown-body",
    },
    "article_body": {
        "key": "article_body",
        "label": "Article / Blog Main Body",
        "selector": "article, [role='main'] article, .article-body, .entry-content, .post-content",
    },
    "documentation_main": {
        "key": "documentation_main",
        "label": "Documentation Main Section",
        "selector": "main, [role='main'], article.doc-content, .docs-content, .md-content",
    },
    "portfolio_profile": {
        "key": "portfolio_profile",
        "label": "Portfolio / Profile Section",
        "selector": "section#about, #about, .profile, .portfolio, section.bio, #portfolio",
    },
    "reader_page": {
        "key": "reader_page",
        "label": "Distraction-free Reader View",
        "selector": "#reader-content, .reader-view, article, main",
    },
    "npb_calendar": {
        "key": "npb_calendar",
        "label": "NPB Schedule Calendar Table",
        "selector": "#calendar, .calendar, table.calendar",
    },
    "npb_linescore": {
        "key": "npb_linescore",
        "label": "NPB Game Linescore Table",
        "selector": "table.score_table, .linescore, #linescore",
    },
    "generic_main": {
        "key": "generic_main",
        "label": "Generic Main Region",
        "selector": "main, #main, #content, .main-content",
    },
}

NOISE_TAGS = {"script", "style", "noscript", "svg", "iframe", "form", "input", "button", "meta", "link"}


def _get_pattern_selector(pattern_key: str) -> str:
    key = (pattern_key or "").strip().lower()
    if key in DOM_PATTERNS:
        return DOM_PATTERNS[key]["selector"]
    return pattern_key  # Assume custom selector if not a known pattern key


def detect_pattern(html: str) -> str:
    """Detect candidate pattern key automatically using BlueProbe or built-in selector matching."""
    try:
        from blueprobe.dom_patterns import detect_pattern as bp_detect
        results = bp_detect(html)
        if results and results[0].get("pattern"):
            return results[0]["pattern"].get("key", "generic_main")
    except Exception:
        pass

    if HTMLParser is not None and html.strip():
        try:
            tree = HTMLParser(html)
            for pkey, pdata in DOM_PATTERNS.items():
                if pkey == "generic_main":
                    continue
                sub_selectors = [s.strip() for s in pdata["selector"].split(",") if s.strip()]
                for sub in sub_selectors:
                    if tree.css(sub):
                        return pkey
        except Exception:
            pass
    return "generic_main"


def normalize_whitespace(text: str) -> str:
    """Normalize text whitespace collapsing spaces while preserving line breaks."""
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    non_empty = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                non_empty.append("")
                prev_blank = True
        else:
            non_empty.append(line)
            prev_blank = False
    return "\n".join(non_empty).strip()


def extract_pattern(
    html: str,
    pattern_key: str = "generic_main",
    *,
    custom_selector: str | None = None,
) -> dict[str, Any]:
    """Extract clean content and metadata from HTML using a DOM structure pattern or selector."""
    if not isinstance(html, str) or not html.strip():
        return {
            "schema": SCHEMA,
            "pattern_key": pattern_key,
            "selector_used": custom_selector or _get_pattern_selector(pattern_key),
            "matched_node_count": 0,
            "title": "",
            "text": "",
            "clean_html": "",
            "headings": [],
            "tags": [],
            "links": [],
            "tables": [],
            "metadata": {"char_count": 0, "word_count": 0, "link_count": 0, "heading_count": 0, "table_count": 0},
        }

    if pattern_key == "auto" or (not pattern_key and not custom_selector):
        pattern_key = detect_pattern(html)

    selector = custom_selector or _get_pattern_selector(pattern_key)

    title = ""
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_m:
        title = normalize_whitespace(re.sub(r"<[^>]+>", "", title_m.group(1)))

    if HTMLParser is not None:
        return _extract_with_selectolax(html, pattern_key, selector, title)
    else:
        return _extract_with_stdlib(html, pattern_key, selector, title)


def _extract_with_selectolax(html: str, pattern_key: str, selector: str, title: str) -> dict[str, Any]:
    tree = HTMLParser(html)

    # Find matching container nodes
    nodes = []
    sub_selectors = [s.strip() for s in selector.split(",") if s.strip()]
    for sub in sub_selectors:
        try:
            matched = tree.css(sub)
            if matched:
                nodes.extend(matched)
                break  # Pick the first matching selector rule
        except Exception:
            continue

    if not nodes:
        # Fallback to body or entire parser root
        nodes = tree.css("body") or [tree.root] if tree.root else []

    matched_count = len(nodes)

    # Strip noise from target nodes
    for node in nodes:
        for noise_sel in list(NOISE_TAGS):
            for noise_node in node.css(noise_sel):
                noise_node.decompose()

    collected_text_parts = []
    collected_clean_html_parts = []
    headings = []
    tags_set = set()
    links = []
    tables = []

    for node in nodes:
        collected_text_parts.append(node.text(deep=True, separator=" "))
        collected_clean_html_parts.append(node.html or "")

        # Extract tags
        for el in node.css("*"):
            if el.tag and el.tag.lower() not in NOISE_TAGS:
                tags_set.add(el.tag.lower())

        # Extract headings (h1..h6)
        for h_level in range(1, 7):
            for h_node in node.css(f"h{h_level}"):
                htext = normalize_whitespace(h_node.text(deep=True))
                if htext:
                    headings.append({"level": h_level, "text": htext})

        # Extract links
        for a_node in node.css("a"):
            href = a_node.attributes.get("href", "").strip()
            atext = normalize_whitespace(a_node.text(deep=True))
            if href or atext:
                links.append({"text": atext, "href": href})

        # Extract tables
        for t_node in node.css("table"):
            table_grid = []
            for tr_node in t_node.css("tr"):
                row = []
                for cell in tr_node.css("th, td"):
                    row.append(normalize_whitespace(cell.text(deep=True)))
                if row:
                    table_grid.append(row)
            if table_grid:
                tables.append(table_grid)

    raw_text = "\n".join(collected_text_parts)
    clean_text = normalize_whitespace(raw_text)

    # Basic clean HTML tag whitelist filter
    clean_html_str = "\n".join(collected_clean_html_parts)
    clean_html = _sanitize_html_string(clean_html_str)

    return {
        "schema": SCHEMA,
        "pattern_key": pattern_key,
        "selector_used": selector,
        "matched_node_count": matched_count,
        "title": title,
        "text": clean_text,
        "clean_html": clean_html,
        "headings": headings,
        "tags": sorted(tags_set),
        "links": links,
        "tables": tables,
        "metadata": {
            "char_count": len(clean_text),
            "word_count": len(clean_text.split()),
            "link_count": len(links),
            "heading_count": len(headings),
            "table_count": len(tables),
        },
    }


def _extract_with_stdlib(html: str, pattern_key: str, selector: str, title: str) -> dict[str, Any]:
    """Fallback HTML extractor using stdlib regex and string manipulations."""
    clean_html_str = re.sub(r"<(script|style|svg|iframe|noscript)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    clean_html_str = re.sub(r"<!--.*?-->", "", clean_html_str, flags=re.DOTALL)
    raw_text = re.sub(r"<[^>]+>", " ", clean_html_str)
    clean_text = normalize_whitespace(raw_text)

    headings = []
    for h_match in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", html, re.DOTALL | re.IGNORECASE):
        level = int(h_match.group(1))
        htext = normalize_whitespace(re.sub(r"<[^>]+>", "", h_match.group(2)))
        if htext:
            headings.append({"level": level, "text": htext})

    links = []
    for a_match in re.finditer(r'<a[^>]*href=["\']?([^"\'>\s]+)["\']?[^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE):
        href = a_match.group(1).strip()
        atext = normalize_whitespace(re.sub(r"<[^>]+>", "", a_match.group(2)))
        links.append({"text": atext, "href": href})

    tags = sorted(set(m.lower() for m in re.findall(r"<([a-zA-Z1-6]+)[\s/>]", clean_html_str)))
    tags = [t for t in tags if t not in NOISE_TAGS]

    clean_html = _sanitize_html_string(clean_html_str)

    return {
        "schema": SCHEMA,
        "pattern_key": pattern_key,
        "selector_used": selector,
        "matched_node_count": 1,
        "title": title,
        "text": clean_text,
        "clean_html": clean_html,
        "headings": headings,
        "tags": tags,
        "links": links,
        "tables": [],
        "metadata": {
            "char_count": len(clean_text),
            "word_count": len(clean_text.split()),
            "link_count": len(links),
            "heading_count": len(headings),
            "table_count": 0,
        },
    }


def _sanitize_html_string(html_str: str) -> str:
    """Strip script, style, and comments from HTML string."""
    clean = re.sub(r"<(script|style|svg|iframe|noscript)[^>]*>.*?</\1>", "", html_str, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL)
    return clean.strip()


def extract_from_snapshot(
    snapshot: dict[str, Any] | str | Path,
    pattern_key: str = "generic_main",
    *,
    custom_selector: str | None = None,
) -> dict[str, Any]:
    """Extract clean pattern content from an html-snapshot/1 object, file path, or JSON string."""
    if isinstance(snapshot, (str, Path)):
        p = Path(snapshot)
        if p.exists() and p.is_file():
            snapshot_data = json.loads(p.read_text(encoding="utf-8"))
        else:
            snapshot_data = json.loads(str(snapshot))
    else:
        snapshot_data = dict(snapshot)

    html = snapshot_data.get("html", "")
    extracted = extract_pattern(html, pattern_key=pattern_key, custom_selector=custom_selector)

    return {
        **extracted,
        "url": snapshot_data.get("url"),
        "fetched_at": snapshot_data.get("fetched_at"),
        "snapshot_sha256": snapshot_data.get("content_sha256") or snapshot_data.get("response_sha256"),
    }


def extract_from_har(
    har_source: dict[str, Any] | str | Path,
    pattern_key: str = "generic_main",
    *,
    url_pattern: str | None = None,
    custom_selector: str | None = None,
) -> list[dict[str, Any]]:
    """Extract pattern content from entries within a HAR (HTTP Archive) source."""
    if isinstance(har_source, (str, Path)):
        p = Path(har_source)
        if p.exists() and p.is_file():
            har_data = json.loads(p.read_text(encoding="utf-8"))
        else:
            har_data = json.loads(str(har_source))
    else:
        har_data = dict(har_source)

    entries = har_data.get("log", {}).get("entries", [])
    results = []

    for entry in entries:
        req = entry.get("request", {})
        res = entry.get("response", {})
        url = req.get("url", "")
        status = res.get("status", 0)

        if url_pattern and not re.search(url_pattern, url):
            continue

        content_info = res.get("content", {})
        mime_type = content_info.get("mimeType", "").lower()
        text = content_info.get("text", "")

        # Target HTML responses or 200 OK
        if "html" in mime_type or not mime_type or text.strip().startswith("<"):
            extracted = extract_pattern(text, pattern_key=pattern_key, custom_selector=custom_selector)
            results.append({
                "url": url,
                "status": status,
                "mime_type": mime_type,
                "extracted": extracted,
            })

    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="QueRyu Clean Pattern Extractor for DOM structures & HAR archives")
    ap.add_argument("--input", "-i", type=Path, help="Input HTML file, snapshot JSON, or HAR JSON file")
    ap.add_argument("--har", type=Path, help="Explicit HAR archive JSON file path")
    ap.add_argument("--pattern", "-p", default="generic_main", help="Pattern key (e.g., github_readme, article_body, npb_calendar, auto)")
    ap.add_argument("--selector", help="Custom CSS selector override")
    ap.add_argument("--url-filter", help="URL regex filter when extracting from HAR archive")
    ap.add_argument("--out", "-o", type=Path, help="Output destination JSON file")

    args = ap.parse_args(argv)

    input_path = args.har or args.input
    if not input_path:
        ap.error("--input または --har を指定してください")

    if not input_path.exists():
        ap.error(f"ファイルが存在しません: {input_path}")

    raw_content = input_path.read_text(encoding="utf-8")

    try:
        data = json.loads(raw_content)
        if isinstance(data, dict) and "log" in data and "entries" in data["log"]:
            # HAR Archive
            result = extract_from_har(data, pattern_key=args.pattern, url_pattern=args.url_filter, custom_selector=args.selector)
        elif isinstance(data, dict) and "schema" in data and "snapshot" in data.get("schema", ""):
            # HTML Snapshot
            result = extract_from_snapshot(data, pattern_key=args.pattern, custom_selector=args.selector)
        else:
            # HTML
            result = extract_pattern(raw_content, pattern_key=args.pattern, custom_selector=args.selector)
    except Exception:
        # Fallback to HTML string parsing
        result = extract_pattern(raw_content, pattern_key=args.pattern, custom_selector=args.selector)

    out_json = json.dumps(result, ensure_ascii=False, indent=2) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out_json, encoding="utf-8")
        print(f"Extraction saved to {args.out}")
    else:
        print(out_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
