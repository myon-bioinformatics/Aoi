"""selectolax.lexbor.LexborHTMLParser の、このリポジトリが実際に呼ぶ分だけ（実験）。

木は標準ライブラリの html.parser（blueprobe.HtmlTree と同じ組み方）で作る。
研究コードが動的に触ったのは css / css_first / attributes / parent / prev / text /
decompose / html だけ。HTML5 が補うタグ（tbody、欠落した tr、入れ子の a、template の中）は
lexbor と一致しない。そこを使う呼び出しは置き換えられない。
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for _path in (_ROOT, _ROOT / "blueprobe"):
    _text = str(_path)
    if _text not in sys.path:
        sys.path.insert(0, _text)

from blueprobe import HtmlTree, _Element, _parse_selector, _selector_matches  # noqa: E402

_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def _lower_attrs(node) -> None:
    attrs = getattr(node, "attributes", None)
    if attrs:
        node.attributes = {str(key).lower(): value for key, value in attrs.items()}
    for child in getattr(node, "children", ()):
        _lower_attrs(child)


def _elements(node, include_self: bool):
    if include_self and isinstance(node, _Element) and node.tag != "#document":
        yield node
    for child in getattr(node, "children", ()):
        if isinstance(child, _Element):
            yield from _elements(child, True)


def _query(node, query: str, include_self: bool):
    compounds, combinators = _parse_selector(query)
    found = []
    for element in _elements(node, include_self):
        if _selector_matches(element, compounds, combinators):
            found.append(Node(element))
    return found


def _pieces(element, deep: bool) -> list[str]:
    parts: list[str] = []
    for child in element.children:
        if child.tag == "-text":
            parts.append(child.data)
        elif deep:
            parts.extend(_pieces(child, True))
    return parts


def _serialize(node) -> str:
    parts: list[str] = []
    for child in getattr(node, "children", ()):
        if child.tag == "-text":
            parts.append(html.escape(child.data))
            continue
        attrs = ""
        for key, value in child.attributes.items():
            attrs += f" {key}" if value is None else f' {key}="{html.escape(str(value), quote=True)}"'
        if child.tag in _VOID:
            parts.append(f"<{child.tag}{attrs}>")
        else:
            parts.append(f"<{child.tag}{attrs}>{_serialize(child)}</{child.tag}>")
    return "".join(parts)


class Node:
    """LexborNode のうち、研究コードが属性アクセスした分。"""

    def __init__(self, element):
        self._el = element

    @property
    def tag(self) -> str:
        return self._el.tag

    @property
    def attributes(self) -> dict:
        return self._el.attributes

    @property
    def parent(self):
        parent = self._el.parent
        if parent is None or parent.tag == "#document":
            return None
        return Node(parent)

    @property
    def prev(self):
        prev = self._el.prev
        return None if prev is None else Node(prev)

    def text(self, deep: bool = True, separator: str = "", strip: bool = False, skip_empty: bool = False) -> str:
        if self._el.tag == "-text":
            data = self._el.data.strip() if strip else self._el.data
            if skip_empty and data.strip() == "":
                return ""
            return data
        parts = _pieces(self._el, deep)
        if strip:
            parts = [part.strip() for part in parts]
        if skip_empty:
            parts = [part for part in parts if part.strip()]
        return separator.join(parts)

    def css(self, query: str):
        return _query(self._el, query, True)

    def css_first(self, query: str):
        found = self.css(query)
        return found[0] if found else None

    def decompose(self) -> None:
        element = self._el
        parent = element.parent
        if parent is None:
            return
        children = parent.children
        try:
            index = children.index(element)
        except ValueError:
            return
        if index + 1 < len(children):
            children[index + 1].prev = children[index - 1] if index else None
        del children[index]
        element.parent = None
        element.prev = None


class LexborHTMLParser:
    def __init__(self, html: str):
        if not isinstance(html, str):
            raise TypeError(f"html は str: {type(html).__name__}")
        tree = HtmlTree(html)
        _lower_attrs(tree.root)
        self._root = tree.root

    def css(self, query: str):
        return _query(self._root, query, False)

    @property
    def html(self) -> str:
        return _serialize(self._root)

