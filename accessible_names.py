"""保存済み HTML の操作要素・画像に付く「名前」（アクセシブルネーム）を観測する。

ボタン・リンク・入力・タブ・画像などについて、名前とその出どころ（aria-labelledby /
aria-label / label / alt / title / 本文 / placeholder）、役割、絵文字だけの名前かどうか、
aria-hidden の中にあるかを記録する。判断はしない。数えるだけ。

名前の計算は W3C accname の**近似**で、ブラウザの計算と同じではない（ACCNAME_APPROXIMATION）。
CSS（::before / ::after の content、display:none）を評価しないため、CSS で付く装飾は名前に入らない。
ブラウザで採った aria スナップショットとの突き合わせは compare_aria_snapshot() で行い、
一致・CSS 由来の差・不一致を分けて数える。ネットワークには出ない。

    python accessible_names.py page.html [--json]
    python accessible_names.py capture.json          # btk-browser-dom/1（aria_snapshot があれば突き合わせる）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from blueprobe import new_report
from emoji_observations import emoji_sequences

__all__ = ["observe", "observe_capture", "parse_aria_snapshot", "compare_aria_snapshot", "summarize"]

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
_SKIP = {"script", "style", "template", "noscript"}
_ROLES = {"button", "link", "tab", "menuitem", "checkbox", "radio", "switch", "option", "combobox",
          "textbox", "img", "searchbox", "slider", "spinbutton", "treeitem"}
# type=file is a button in Chromium's accessibility tree (its name comes from the label).
_INPUT_ROLES = {"button": "button", "submit": "button", "reset": "button", "image": "button", "file": "button",
                "checkbox": "checkbox", "radio": "radio", "range": "slider", "number": "spinbutton",
                "search": "searchbox"}
_NAME_FROM_CONTENT = {"disclosure", "button", "link", "tab", "menuitem", "checkbox", "radio", "switch", "option", "treeitem"}


class _Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent


class _Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {}, None)
        self.current, self.skip = self.root, 0

    def handle_starttag(self, tag, attrs):
        if self.skip or tag in _SKIP:
            self.skip += tag in _SKIP
            return
        node = _Node(tag, {k: (v or "") for k, v in attrs}, self.current)
        self.current.children.append(node)
        if tag not in _VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        if not self.skip:
            self.current.children.append(_Node(tag, {k: (v or "") for k, v in attrs}, self.current))

    def handle_endtag(self, tag):
        if tag in _SKIP and self.skip:
            self.skip -= 1
            return
        if self.skip:
            return
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data):
        if not self.skip:
            self.current.children.append(data)


def _walk(node):
    for child in node.children:
        if isinstance(child, _Node):
            yield child
            yield from _walk(child)


def _flat(text):
    return " ".join(text.split())


def _hidden(node):
    return "hidden" in node.attrs or node.attrs.get("aria-hidden") == "true"


def _text(node, ids, depth=0):
    """Name from content: text, img alt, nested aria-label; hidden subtrees skipped."""
    parts = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif not _hidden(child) and depth < 30:
            label = child.attrs.get("aria-label", "").strip()
            if label:
                parts.append(" " + label + " ")
            elif child.tag == "img":
                parts.append(" " + child.attrs.get("alt", "") + " ")
            elif child.tag in ("br",):
                parts.append(" ")
            else:
                parts.append(" " + _text(child, ids, depth + 1) + " ")
    return _flat("".join(parts))


def _role(node):
    explicit = node.attrs.get("role", "").split()
    if explicit and explicit[0] in _ROLES:
        return explicit[0]
    tag = node.tag
    if tag == "a" and "href" in node.attrs:
        return "link"
    if tag == "button":
        return "button"
    if tag == "summary":
        return "disclosure"  # Chromium: DisclosureTriangle; not a "button" in aria snapshots
    if tag == "img":
        return "img" if node.attrs.get("alt", None) != "" else None
    if tag == "select":
        return "listbox" if "multiple" in node.attrs or node.attrs.get("size", "1") not in ("", "0", "1") else "combobox"
    if tag == "option":
        return "option"
    if tag == "textarea":
        return "textbox"
    if tag == "input":
        kind = node.attrs.get("type", "text").lower()
        if kind == "hidden":
            return None
        return _INPUT_ROLES.get(kind, "textbox")
    return None


def _name(node, role, ids, labels):
    attrs = node.attrs
    if attrs.get("aria-labelledby"):
        parts = [_text(ids[i], ids) for i in attrs["aria-labelledby"].split() if i in ids]
        if any(parts):
            return _flat(" ".join(parts)), "aria-labelledby"
    if attrs.get("aria-label", "").strip():
        return _flat(attrs["aria-label"]), "aria-label"
    if node.tag in ("input", "select", "textarea"):
        if node.tag == "input" and attrs.get("type", "").lower() in ("button", "submit", "reset") and attrs.get("value"):
            return _flat(attrs["value"]), "value"
        label = labels.get(attrs.get("id")) if attrs.get("id") else None
        wrapper = node.parent
        while label is None and wrapper is not None:
            if isinstance(wrapper, _Node) and wrapper.tag == "label":
                label = wrapper
            wrapper = wrapper.parent
        if label is not None and _text(label, ids):
            return _text(label, ids), "label"
    if node.tag == "img" and attrs.get("alt", "").strip():
        return _flat(attrs["alt"]), "alt"
    if role in _NAME_FROM_CONTENT or (node.tag == "button"):
        text = _text(node, ids)
        if text:
            return text, "content"
    if attrs.get("title", "").strip():
        return _flat(attrs["title"]), "title"
    if attrs.get("placeholder", "").strip():
        return _flat(attrs["placeholder"]), "placeholder"
    return "", None


def _path(node):
    parts = []
    while node is not None and node.tag != "#root" and len(parts) < 4:
        ident = ("#" + node.attrs["id"]) if node.attrs.get("id") else (
            "." + node.attrs["class"].split()[0] if node.attrs.get("class", "").split() else "")
        parts.append(node.tag + ident)
        node = node.parent
    return " > ".join(reversed(parts))


def _emoji_only(name):
    if not name:
        return False
    rest = name
    for seq in emoji_sequences(name):
        rest = rest.replace(seq, "")
    return bool(emoji_sequences(name)) and not re.sub(r"[\s\W_]", "", rest)


def observe(html: str, url: str | None = None) -> dict:
    """1ページの操作要素・画像の名前の観測。records は DOM の順。

    flags（判断ではなく観測の区分。docs/antipatterns.md に対応）:
      empty_name          名前が付かない操作要素・画像
      emoji_only_name     名前が絵文字（と記号）だけ
      aria_hidden_control aria-hidden="true" の中にある操作要素（hidden 属性や閉じた <details> の中は木から外れるので数えない）
      image_without_alt   alt 属性のない img（alt="" は装飾として role なし）
      placeholder_only    名前が placeholder からしか付かない入力
    """
    if not isinstance(html, str):
        raise TypeError("html must be str")
    tree = _Tree()
    tree.feed(html)
    tree.close()
    nodes = list(_walk(tree.root))
    ids = {n.attrs["id"]: n for n in nodes if n.attrs.get("id")}
    labels = {n.attrs["for"]: n for n in nodes if n.tag == "label" and n.attrs.get("for")}
    report = new_report()
    for index, node in enumerate(nodes):
        role = _role(node)
        if role is None:
            if node.tag == "img":
                report["counts"]["decorative_image"] += 1
            continue
        name, source = _name(node, role, ids, labels)
        hidden = aria_hidden = False
        cursor = node
        while cursor is not None and cursor.tag != "#root":
            hidden = hidden or "hidden" in cursor.attrs or (
                cursor is not node and cursor.tag == "details" and "open" not in cursor.attrs
                and not (node.tag == "summary" and node.parent is cursor))
            aria_hidden = aria_hidden or cursor.attrs.get("aria-hidden") == "true"
            cursor = cursor.parent
        flags = []
        if not name:
            flags.append("empty_name")
        if _emoji_only(name):
            flags.append("emoji_only_name")
        if aria_hidden and not hidden and role != "img":
            flags.append("aria_hidden_control")
        if node.tag == "img" and "alt" not in node.attrs:
            flags.append("image_without_alt")
        if source == "placeholder":
            flags.append("placeholder_only")
        record = {"key": f"{url or ''}#{index}", "url": url, "role": role, "name": name, "name_source": source,
                  "element": _path(node), "href": node.attrs.get("href") if role == "link" else None,
                  "emoji": emoji_sequences(name), "hidden": hidden or aria_hidden, "flags": flags}
        report["records"].append(record)
        for flag in flags:
            report["counts"][flag] += 1
    by_name = {}
    for record in report["records"]:
        if record["role"] == "link" and record["name"] and not record["hidden"]:
            by_name.setdefault(record["name"].casefold(), set()).add(record["href"])
    report["counts"]["ambiguous_link_name"] = sum(1 for hrefs in by_name.values() if len(hrefs) > 1)
    return report


def observe_capture(capture: dict) -> dict:
    """btk-browser-dom/1 または html-snapshot/1。aria_snapshot があれば突き合わせ結果も付ける。"""
    if capture.get("schema") not in ("btk-browser-dom/1", "html-snapshot/1") or not isinstance(capture.get("html"), str):
        raise ValueError("expected btk-browser-dom/1 or html-snapshot/1")
    report = observe(capture["html"], capture.get("url"))
    if isinstance(capture.get("aria_snapshot"), str):
        report["aria_comparison"] = compare_aria_snapshot(report, capture["aria_snapshot"])
    return report


_ARIA_LINE = re.compile(r'^\s*- (\w+)(?: "((?:[^"\\]|\\.)*)")?')


def parse_aria_snapshot(text: str) -> list[tuple[str, str]]:
    """Playwright aria_snapshot の (role, name) を出現順に。名前のない行は name=""。"""
    out = []
    for line in text.splitlines():
        match = _ARIA_LINE.match(line)
        if match and match.group(1) in _ROLES | {"listbox"}:
            out.append((match.group(1), json.loads('"' + (match.group(2) or "") + '"')))
    return out


def compare_aria_snapshot(report: dict, snapshot: str) -> dict:
    """静的な近似と、ブラウザが計算した名前を役割ごとの出現順で突き合わせる。

    match           名前が同じ（空白の詰め方の差は無視）
    css_generated   ブラウザの名前が静的な名前を含み、前後が記号だけ（::before/::after の装飾など）
    mismatch        それ以外。browser_only / static_only は対応する相手がない数
    """
    browser = parse_aria_snapshot(snapshot)
    roles = _ROLES | {"listbox"}
    ours = [(r["role"], r["name"]) for r in report["records"] if not r["hidden"] and r["role"] in roles]
    result = Counter()
    mismatches = []
    for role in sorted({r for r, _ in browser} | {r for r, _ in ours}):
        left = [n for r, n in ours if r == role]
        right = [n for r, n in browser if r == role]
        for mine, theirs in zip(left, right):
            a, b = _flat(mine), _flat(theirs)
            if a == b:
                result["match"] += 1
            elif a and a in b and not re.sub(r"[\W_]", "", b.replace(a, "", 1)):
                result["css_generated"] += 1
            else:
                result["mismatch"] += 1
                mismatches.append({"role": role, "static": mine, "browser": theirs})
        result["browser_only"] += max(0, len(right) - len(left))
        result["static_only"] += max(0, len(left) - len(right))
    keys = ("match", "css_generated", "mismatch", "browser_only", "static_only")
    return {"counts": {k: result[k] for k in keys}, "mismatches": mismatches[:50]}


def summarize(report: dict) -> dict:
    roles = Counter(r["role"] for r in report["records"])
    sources = Counter(r["name_source"] or "none" for r in report["records"])
    return {"controls": len(report["records"]), "roles": dict(roles), "name_sources": dict(sources),
            "flags": {k: v for k, v in report["counts"].items() if v}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="保存済み HTML の操作要素・画像の名前を観測する（近似・ネットワークに出ない）")
    ap.add_argument("path", type=Path, help="HTML、または btk-browser-dom/1 / html-snapshot/1 の JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
        report = observe_capture(json.loads(text)) if args.path.suffix == ".json" else observe(text)
    except (OSError, ValueError) as error:
        print(f"accessible_names: {error}", file=sys.stderr)
        return 2
    summary = summarize(report)
    if args.json:
        print(json.dumps({"summary": summary, "records": report["records"],
                          "aria_comparison": report.get("aria_comparison")}, ensure_ascii=False, indent=1))
        return 0
    print(f"controls {summary['controls']} roles {summary['roles']}")
    print(f"name sources {summary['name_sources']}")
    for flag, count in sorted(summary["flags"].items()):
        print(f"  {flag}: {count}")
    for record in report["records"]:
        if record["flags"]:
            print(f"  [{','.join(record['flags'])}] {record['role']} {record['name']!r} at {record['element']}")
    if "aria_comparison" in report:
        print(f"browser comparison {report['aria_comparison']['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
