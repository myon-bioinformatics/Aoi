"""保存済み HTML の見出し階層（<h1>〜<h6>）とランドマーク構造（<main>, <nav>, <header> 等）を観測する。

見出しのレベル、テキスト、要素の位置、包含するランドマーク、非表示状態、
構造上の不連続（階層のスキップ、空の見出し、複数の h1、メインランドマークの欠落、
未ラベルのランドマーク等）を記録する。判断はしない。数えるだけ。

ネットワークには出ない。

    python heading_observations.py page.html [--json]
    python heading_observations.py capture.json          # btk-browser-dom/1 または html-snapshot/1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from accessible_names import _Tree, _flat, _name, _path, _text, _walk  # one shared tree and name logic
from blueprobe import new_report

__all__ = ["observe", "observe_capture", "summarize"]

_HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
_LANDMARK_ROLES = {"main", "navigation", "banner", "contentinfo", "complementary", "region", "search"}
_SECTIONING_TAGS = {"article", "aside", "main", "nav", "section"}


def _is_inside_sectioning(node):
    cursor = node.parent
    while cursor is not None and cursor.tag != "#root":
        if cursor.tag in _SECTIONING_TAGS:
            return True
        cursor = cursor.parent
    return False


def _landmark_role(node, ids):
    explicit = node.attrs.get("role", "").split()
    if explicit and explicit[0] in _LANDMARK_ROLES:
        return explicit[0]
    tag = node.tag
    if tag == "main":
        return "main"
    if tag == "nav":
        return "navigation"
    if tag == "aside":
        return "complementary"
    if tag == "header":
        return "banner" if not _is_inside_sectioning(node) else None
    if tag == "footer":
        return "contentinfo" if not _is_inside_sectioning(node) else None
    if tag == "section":
        return "region" if _landmark_label(node, ids) else None
    return None


def _heading_level(node):
    """A valid aria-level (integer >= 1) wins. A missing, non-integer, zero or negative
    aria-level falls back to the HTML level (h1-h6), or to ARIA's default 2 for role=heading."""
    fallback = _HEADINGS.get(node.tag, 2)
    raw = node.attrs.get("aria-level", "").strip()
    if not raw:
        return fallback
    try:
        level = int(raw)
    except ValueError:
        return fallback
    return level if level >= 1 else fallback


def _landmark_label(node, ids):
    """Same name computation as accessible_names (aria-labelledby, aria-label, then title)."""
    return _name(node, None, ids, {})[0]


def _find_enclosing_landmark(node, ids):
    cursor = node.parent
    while cursor is not None and cursor.tag != "#root":
        role = _landmark_role(cursor, ids)
        if role is not None:
            label = _landmark_label(cursor, ids)
            return {"tag": cursor.tag, "role": role, "label": label, "element": _path(cursor)}
        cursor = cursor.parent
    return None


def observe(html: str, url: str | None = None) -> dict:
    """1 ページの見出し階層とランドマーク構造の観測。

    flags (構造的な状態の観測区分):
      empty_heading            テキストが空の見出し
      skipped_heading_level    例: h1 の直後に h3 が出現（レベル2をスキップ）
      multiple_h1              ページ内に複数の h1 が存在
      missing_main_landmark    コンテンツが存在するのに <main> / role="main" が存在しない
      unlabelled_landmark      ラベルが付けられていないランドマーク（section / nav 等）
      heading_outside_landmark ランドマーク外にある見出し
    """
    if not isinstance(html, str):
        raise TypeError("html must be str")
    tree = _Tree()
    tree.feed(html)
    tree.close()
    nodes = list(_walk(tree.root))
    ids = {n.attrs["id"]: n for n in nodes if n.attrs.get("id")}
    report = new_report()

    last_visible_level = 0
    h1_count = 0
    has_main_landmark = False

    for index, node in enumerate(nodes):
        hidden = aria_hidden = False
        cursor = node
        while cursor is not None and cursor.tag != "#root":
            hidden = hidden or "hidden" in cursor.attrs or (
                cursor is not node and cursor.tag == "details" and "open" not in cursor.attrs
                and not (node.tag == "summary" and node.parent is cursor))
            aria_hidden = aria_hidden or cursor.attrs.get("aria-hidden") == "true"
            cursor = cursor.parent
        is_hidden = hidden or aria_hidden

        # Check if node is a landmark
        role = _landmark_role(node, ids)
        if role is not None:
            if role == "main" and not is_hidden:
                has_main_landmark = True
            label = _landmark_label(node, ids)
            landmark_flags = []
            if role in ("region", "navigation") and not label:
                landmark_flags.append("unlabelled_landmark")
            record = {"key": f"{url or ''}#landmark-{index}", "type": "landmark", "url": url,
                      "tag": node.tag, "role": role, "label": label, "element": _path(node),
                      "hidden": is_hidden, "flags": landmark_flags}
            report["records"].append(record)
            for flag in landmark_flags:
                report["counts"][flag] += 1

        # Check if node is a heading
        if node.tag in _HEADINGS or node.attrs.get("role") == "heading":
            level = _heading_level(node)
            text = _text(node, ids)
            enclosing = _find_enclosing_landmark(node, ids)
            heading_flags = []
            if not text:
                heading_flags.append("empty_heading")
            if not is_hidden:
                if level == 1:
                    h1_count += 1
                    if h1_count > 1:
                        heading_flags.append("multiple_h1")
                if last_visible_level > 0 and level > last_visible_level + 1:
                    heading_flags.append("skipped_heading_level")
                last_visible_level = level
            if enclosing is None and not is_hidden:
                heading_flags.append("heading_outside_landmark")

            record = {"key": f"{url or ''}#heading-{index}", "type": "heading", "url": url,
                      "level": level, "tag": node.tag, "text": text, "element": _path(node),
                      "landmark": enclosing, "hidden": is_hidden, "flags": heading_flags}
            report["records"].append(record)
            for flag in heading_flags:
                report["counts"][flag] += 1

    headings = [r for r in report["records"] if r.get("type") == "heading" and not r["hidden"]]
    if headings and not has_main_landmark:
        report["counts"]["missing_main_landmark"] = 1
        report["records"].append({"key": f"{url or ''}#page", "type": "page", "url": url,
                                  "visible_headings": len(headings), "flags": ["missing_main_landmark"]})

    return report


def observe_capture(capture: dict) -> dict:
    """btk-browser-dom/1 または html-snapshot/1 の JSON キャプチャを観測する。"""
    if capture.get("schema") not in ("btk-browser-dom/1", "html-snapshot/1") or not isinstance(capture.get("html"), str):
        raise ValueError("expected btk-browser-dom/1 or html-snapshot/1")
    return observe(capture["html"], capture.get("url"))


def summarize(report: dict) -> dict:
    headings = [r for r in report["records"] if r.get("type") == "heading"]
    landmarks = [r for r in report["records"] if r.get("type") == "landmark"]
    levels = Counter(f"h{r['level']}" for r in headings)
    return {"headings": len(headings), "landmarks": len(landmarks), "levels": dict(sorted(levels.items())),
            "flags": {k: v for k, v in report["counts"].items() if v}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="保存済み HTML の見出し階層とランドマーク構造を観測する（ネットワークに出ない）")
    ap.add_argument("path", type=Path, help="HTML、または btk-browser-dom/1 / html-snapshot/1 の JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
        report = observe_capture(json.loads(text)) if args.path.suffix == ".json" else observe(text)
    except (OSError, ValueError) as error:
        print(f"heading_observations: {error}", file=sys.stderr)
        return 2
    summary = summarize(report)
    if args.json:
        print(json.dumps({"summary": summary, "records": report["records"]}, ensure_ascii=False, indent=1))
        return 0
    print(f"headings {summary['headings']} levels {summary['levels']} landmarks {summary['landmarks']}")
    for flag, count in sorted(summary["flags"].items()):
        print(f"  {flag}: {count}")
    for record in report["records"]:
        if record.get("type") == "heading":
            lm = f" in {record['landmark']['role']}" if record.get("landmark") else " (outside landmark)"
            flags_str = f" [{','.join(record['flags'])}]" if record["flags"] else ""
            print(f"  {flags_str} h{record['level']} {record['text']!r}{lm} at {record['element']}")
        elif record.get("type") == "landmark":
            flags_str = f" [{','.join(record['flags'])}]" if record["flags"] else ""
            label_str = f" ({record['label']!r})" if record.get("label") else ""
            print(f"  {flags_str} landmark {record['role']}{label_str} at {record['element']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
