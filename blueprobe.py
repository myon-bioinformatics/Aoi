"""BlueProbe — 観測する。解釈はあとで。

取得元（source）に依存しない部分だけを置く。
  - normalize(): 表記揺れの吸収。何をしたかは記録単位で残す
  - Report: 1ページを読んだ結果の契約。採用したもの以外も必ず数える
  - inspect(): 取得済みのページを再解析して集計する。ネットワークには出ない

取得元ごとの読み方は別モジュールに置き、次の2つを持たせる:
  pages(scope)        -> [(key, url, group)]   取得すべきページの一覧
  parse(html, url)    -> Report               1ページの観測結果
汎用の取得元 html_source（HtmlSource）と、保存済みページの供給元の契約（SnapshotSupplier）はここにある。

標準ライブラリだけで動く観測ツールも同じファイルにある（Python からは blueprobe.<tool>.observe(...)）:
  \U0001f50e python blueprobe.py URL | --classify HTML | --source NAME --cache DIR   ページの構造
  \U0001f3f7️ python blueprobe.py names PAGE      操作要素・画像の名前（accname の近似）
  \U0001f9ed python blueprobe.py headings PAGE   見出し階層とランドマーク
  \U0001f600 python blueprobe.py emoji PAGE      絵文字の位置と表記
  \U0001f310 python blueprobe.py web DIR         保存済み Web 観測とソース一覧
  \U0001f419 python blueprobe.py github SNAPSHOT REPOSITORY   親の監査から Issue・CI の観測

DOM パターン表と、その判定に使う HTML 木もここにある。木は html.parser で組み立てる。

Aoi の原則との対応:
  Observe Before Explaining  … 原文(raw)と読み取った値(derived)を同じ記録に並べる
  Never Hide Unknowns        … unknown は件数と原文を残す
  Separate Facts From Explanations … ここでは勝敗も点差も計算しない
"""

from __future__ import annotations

import argparse, datetime, hashlib, importlib, json, math, re, sys, unicodedata
from collections import Counter; from collections.abc import Iterable, Iterator; from html.parser import HTMLParser; from pathlib import Path
from types import SimpleNamespace; from typing import Protocol, TypedDict, runtime_checkable

NORMALIZATION = "nul->U+FFFD, NFKC, collapse-whitespace"


def normalize(text: str) -> str:
    """NUL は U+FFFD に置き換え（黙って消さない）、NFKC、連続空白を1つに。"""
    text = unicodedata.normalize("NFKC", text.replace("\x00", "�"))
    return " ".join(text.split())


def new_report() -> dict:
    """1ページ（または複数ページの合計）の観測結果。

    records : 採用した観測。key で一意
    counts  : 採用しなかったものの区分ごとの件数（例: cancelled, non_regular）
    unknown : どの区分にも当たらなかったもの。原文を残す
    """
    return {"records": [], "counts": Counter(), "unknown": []}


def merge(total: dict, part: dict, key: str = "key") -> dict:
    """結果を足し合わせる。同じ key の記録は最初のものを残す。"""
    seen = {r[key] for r in total["records"]}
    total["records"] += [r for r in part["records"] if r[key] not in seen]
    total["counts"].update(part["counts"])
    total["unknown"] += part["unknown"]
    return total


def load_source(name: str):
    """取得元を名前で読み込む。html_source はこのファイルの HtmlSource、ほかは <name>.py。"""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(f"invalid source name: {name!r}")
    return HtmlSource() if name == "html_source" else importlib.import_module(name)


def mask_digits(text: str) -> str:
    """docs に未知表記の「形」だけ残すため、数字を # に伏せる。"""
    return re.sub(r"[0-9０-９]", "#", text)


def inspect(source, pages: Iterable[tuple[str, str, str, str]], records_out: list | None = None) -> list[dict]:
    """取得済みページ (key, url, group, html) を再解析し、group ごとに集計する。

    ネットワークには出ない。解析ルールを直したら、これだけを何度でも回す。
    """
    return _inspect(source.parse, pages, records_out)


def inspect_snapshots(source, supplier, entries=None, records_out=None) -> list[dict]:
    """供給元（SnapshotSupplier）の保存済み本文を、オフラインで再解析する。

    entries を省くと supplier.entries()（既定の行）を読む。指定すれば、その取得時点の行を読む。
    parse_snapshot を持つ source には html-snapshot/1 の記録を、それ以外には本文を渡す。
    照合の失敗は parser を呼ぶ前に止まり、再取得で置き換えない。
    """
    snapshot_parser = getattr(source, 'parse_snapshot', None)
    if entries is None:
        entries = list(supplier.entries())

    def pages():
        for entry in entries:
            if snapshot_parser is not None:
                snapshot = supplier.snapshot(entry)
                payload = snapshot if snapshot['html'] else ''
            else:
                payload = supplier.body(entry)
            yield entry['key'], entry['url'], entry['group'], payload

    parser = (lambda snapshot, url: snapshot_parser(snapshot)) if snapshot_parser is not None else source.parse
    return _inspect(parser, pages(), records_out)


def inspect_queryu_cache(source, cache, entries=None, records_out=None) -> list[dict]:
    """QueRyu の Cache を供給元として再解析する（QueRyuCacheSource 経由）。"""
    return inspect_snapshots(source, QueRyuCacheSource(cache), entries, records_out)


def inspect_cache(source, cache, entries=None, records_out=None) -> list[dict]:
    """非推奨: inspect_queryu_cache の旧名。Aoi/QueRyu 側の互換のために残す（契約 v1 の間は削除しない）。"""
    import warnings
    warnings.warn("inspect_cache is deprecated; use inspect_queryu_cache", DeprecationWarning, stacklevel=2)
    return inspect_queryu_cache(source, cache, entries, records_out)


def _inspect(parser, pages, records_out):
    groups: dict[str, dict] = {}
    for key, url, group, html in pages:
        g = groups.setdefault(group, {"pages": 0, "empty": 0, "report": new_report()})
        if not html:
            g["empty"] += 1
            continue
        g["pages"] += 1
        merge(g["report"], parser(html, url))
    rows = []
    for group, g in sorted(groups.items()):
        r = g["report"]
        if records_out is not None:
            records_out += r["records"]
        rows.append({
            "group": group, "pages": g["pages"], "empty_pages": g["empty"],
            "records": len(r["records"]), **{f"n_{k}": v for k, v in sorted(r["counts"].items())},
            "unknown": len(r["unknown"]),
            "unknown_shapes": sorted({mask_digits(u["raw"]) for u in r["unknown"]})[:5],
        })
    return rows


def to_markdown(rows: list[dict], title: str, checks: list[dict] | None = None) -> str:
    """checks は source.check() の返り値（{"group", "ok", "text"} の並び）。"""
    cols = sorted({k for r in rows for k in r if k != "unknown_shapes"}, key=lambda k: (k != "group", k))
    lines = [f"# {title}", "", "取得済みページの再解析結果（自動生成）。ネットワークには出ていない。", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(r.get(c, 0)) for c in cols) + " |" for r in rows]
    if checks:
        lines += ["", "## 取りこぼしの確認（既知値との照合）", "", *[f"- {c['text']}" for c in checks]]
    shapes = [(r["group"], r["unknown_shapes"]) for r in rows if r["unknown_shapes"]]
    if shapes:
        lines += ["", "## 未知の表記（数字は # に伏せた形）", ""]
        lines += [f"- {g}: " + ", ".join(f"`{s!r}`" for s in ss) for g, ss in shapes]
    return "\n".join(lines) + "\n"


_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class DomCategory(TypedDict):
    key: str
    label: str


class DomPattern(TypedDict):
    key: str
    label: str
    category: str
    selector: str
    description: str
    example_sites: list[str]


class PatternMatch(TypedDict):
    pattern: DomPattern
    score: int
    matched_nodes: int
    selector_used: str


class TableObservation(TypedDict):
    index: int
    kind: str  # "data" | "layout"
    reasons: list[str]
    rows: int
    nested: bool


class StructuredData(TypedDict):
    json_ld_types: list[str]
    json_ld_invalid: int
    microdata_types: list[str]
    itemprops: list[str]
    opengraph: dict[str, str]


class DocumentClassification(TypedDict):
    schema: str
    status: str  # "matched" | "fallback" | "client_rendered" | "insufficient" | "empty"
    patterns: list[PatternMatch]
    signals: list[str]
    landmarks: dict[str, int]
    articles: dict[str, int]
    structured_data: StructuredData
    shadow_roots: dict[str, int]
    tables: list[TableObservation]
    text_chars: int
    hashed_class_ratio: float


class _TextNode:
    __slots__ = ("tag", "attributes", "parent", "prev", "data")

    def __init__(self, data: str, parent: "_Element") -> None:
        self.tag = "-text"
        self.attributes: dict[str, str | None] = {}
        self.parent = parent
        self.prev: _Element | _TextNode | None = None
        self.data = data

    def text(self, deep: bool = True) -> str:
        return self.data


class _Element:
    __slots__ = ("tag", "attributes", "parent", "prev", "children")

    def __init__(self, tag: str, attrs: dict[str, str | None], parent: "_Element | None") -> None:
        self.tag = tag
        self.attributes = attrs
        self.parent = parent
        self.prev: _Element | _TextNode | None = None
        self.children: list[_Element | _TextNode] = []

    def iter(self) -> Iterator["_Element"]:
        """Direct element children. Text nodes stay on .prev for sibling walks."""
        for child in self.children:
            if isinstance(child, _Element):
                yield child

    def text(self, deep: bool = True) -> str:
        parts: list[str] = []

        def walk(node: _Element) -> None:
            for child in node.children:
                if isinstance(child, _TextNode):
                    parts.append(child.data)
                elif deep:
                    walk(child)

        walk(self)
        return "".join(parts)


class _HtmlBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Element("#document", {}, None)
        self._current = self.root

    def _append(self, node: _Element | _TextNode) -> None:
        if self._current.children:
            node.prev = self._current.children[-1]
        self._current.children.append(node)

    def _close_through(self, tags: set[str], stop: set[str]) -> None:
        """Close an open table cell or row. Do not invent a missing ``tr``."""
        node: _Element | None = self._current
        while node is not None and node is not self.root:
            if node.tag in tags:
                if node.parent is not None:
                    self._current = node.parent
                return
            if node.tag in stop:
                return
            node = node.parent

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"td", "th"}:
            self._close_through({"td", "th"}, {"table", "template"})
        elif tag == "tr":
            self._close_through({"td", "th"}, {"table", "template"})
            self._close_through({"tr"}, {"table", "template"})
        node = _Element(tag, {key: value for key, value in attrs}, self._current)
        self._append(node)
        if tag not in _VOID:
            self._current = node

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._append(_Element(tag, {key: value for key, value in attrs}, self._current))

    def handle_endtag(self, tag: str) -> None:
        node: _Element | None = self._current
        while node is not None and node is not self.root and node.tag != tag:
            node = node.parent
        if node is not None and node is not self.root and node.parent is not None:
            self._current = node.parent

    def handle_data(self, data: str) -> None:
        self._append(_TextNode(data, self._current))


class HtmlTree:
    """html.parser tree with the CSS subset the pattern table and source readers use.

    Supported: a tag, ``#id``, ``.class``, ``[attr]``, ``[attr=value]``,
    descendant whitespace, and the child combinator ``>``. Anything else raises
    ValueError, including selector lists (``a, b``), ``+``, ``~``, and pseudos.

    An open ``td``/``th``/``tr`` closes when the next cell or row starts, which
    is the markup variant the calendar reader already accepts. A missing ``tr``
    is not invented.
    """

    def __init__(self, html: str) -> None:
        builder = _HtmlBuilder()
        builder.feed(html)
        builder.close()
        self.root = builder.root

    def css(self, selector: str) -> list[_Element]:
        compounds, combinators = _parse_selector(selector)
        return [node for node in _walk_elements(self.root) if _selector_matches(node, compounds, combinators)]

    def css_first(self, selector: str) -> _Element | None:
        found = self.css(selector)
        return found[0] if found else None


def _walk_elements(node: _Element) -> Iterator[_Element]:
    for child in node.children:
        if isinstance(child, _Element):
            yield child
            yield from _walk_elements(child)


def _parse_selector(selector: str) -> tuple[list[tuple], list[str]]:
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError(f"unsupported selector: {selector!r}")
    _reject_unsupported(selector)
    compounds: list[tuple] = []
    combinators: list[str] = []
    expect = "compound"
    for part in _selector_parts(selector):
        if part in {" ", ">"}:
            if expect != "combinator":
                raise ValueError(f"unsupported selector: {selector!r}")
            combinators.append(part)
            expect = "compound"
        else:
            if expect != "compound":
                raise ValueError(f"unsupported selector: {selector!r}")
            compounds.append(_compound(part, selector))
            expect = "combinator"
    if expect != "combinator" or not compounds:
        raise ValueError(f"unsupported selector: {selector!r}")
    return compounds, combinators


def _reject_unsupported(selector: str) -> None:
    quote = ""
    i = 0
    while i < len(selector):
        ch = selector[i]
        if quote:
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "'\"":
            quote = ch
            i += 1
            continue
        if ch == "[":
            end = selector.find("]", i)
            if end < 0:
                raise ValueError(f"unsupported selector: {selector!r}")
            _attribute(selector[i + 1:end], selector)
            i = end + 1
            continue
        if ch in ":+~*,":
            raise ValueError(f"unsupported selector: {selector!r}")
        i += 1


def _attribute(body: str, selector: str) -> None:
    for operator in ("*=", "^=", "$=", "~=", "|="):
        if operator in body:
            raise ValueError(f"unsupported selector: {selector!r}")
    if body.count("=") > 1 or not body.strip():
        raise ValueError(f"unsupported selector: {selector!r}")
    name = body.split("=", 1)[0].strip()
    if not name:
        raise ValueError(f"unsupported selector: {selector!r}")


def _selector_parts(selector: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(selector):
        ch = selector[i]
        if ch in " \t\r\n":
            if buf:
                parts.append("".join(buf))
                buf = []
            i += 1
            while i < len(selector) and selector[i] in " \t\r\n":
                i += 1
            if i < len(selector) and selector[i] == ">":
                parts.append(">")
                i += 1
                while i < len(selector) and selector[i] in " \t\r\n":
                    i += 1
                continue
            if not parts or parts[-1] not in {" ", ">"}:
                parts.append(" ")
            continue
        if ch == ">":
            if buf:
                parts.append("".join(buf))
                buf = []
            parts.append(">")
            i += 1
            while i < len(selector) and selector[i] in " \t\r\n":
                i += 1
            continue
        if ch == "[":
            end = selector.find("]", i)
            buf.append(selector[i:end + 1])
            i = end + 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        parts.append("".join(buf))
    return parts


def _compound(text: str, selector: str) -> tuple:
    tag: str | None = None
    ident: str | None = None
    classes: list[str] = []
    attrs: list[tuple[str, str | None]] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "#":
            j = i + 1
            while j < len(text) and text[j] not in ".#[":
                j += 1
            ident = text[i + 1:j]
            if not ident:
                raise ValueError(f"unsupported selector: {selector!r}")
            i = j
        elif ch == ".":
            j = i + 1
            while j < len(text) and text[j] not in ".#[":
                j += 1
            name = text[i + 1:j]
            if not name:
                raise ValueError(f"unsupported selector: {selector!r}")
            classes.append(name)
            i = j
        elif ch == "[":
            body = text[i + 1:text.find("]", i)].strip()
            if "=" in body:
                raw_name, value = body.split("=", 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                    value = value[1:-1]
                attrs.append((raw_name.strip(), value))
            else:
                attrs.append((body, None))
            i = text.find("]", i) + 1
        else:
            if tag is not None or ident is not None or classes or attrs:
                raise ValueError(f"unsupported selector: {selector!r}")
            j = i
            while j < len(text) and text[j] not in ".#[":
                j += 1
            tag = text[i:j].lower()
            if not tag or not tag.replace("-", "").isalnum():
                raise ValueError(f"unsupported selector: {selector!r}")
            i = j
    if tag is None and ident is None and not classes and not attrs:
        raise ValueError(f"unsupported selector: {selector!r}")
    return tag, ident, tuple(classes), tuple(attrs)


def _compound_match(node: _Element, compound: tuple) -> bool:
    tag, ident, classes, attrs = compound
    if tag is not None and node.tag != tag:
        return False
    have = node.attributes
    if ident is not None and have.get("id") != ident:
        return False
    if classes:
        got = set((have.get("class") or "").split())
        if any(name not in got for name in classes):
            return False
    for name, value in attrs:
        if name not in have:
            return False
        if value is not None and have.get(name) != value:
            return False
    return True


def _selector_matches(node: _Element, compounds: list[tuple], combinators: list[str]) -> bool:
    current: _Element | None = node
    if not _compound_match(current, compounds[-1]):
        return False
    for index in range(len(compounds) - 2, -1, -1):
        assert current is not None
        current = current.parent
        if combinators[index] == ">":
            if current is None or current.tag == "#document" or not _compound_match(current, compounds[index]):
                return False
        else:
            while current is not None and current.tag != "#document" and not _compound_match(current, compounds[index]):
                current = current.parent
            if current is None or current.tag == "#document":
                return False
    return True


SCHEMA = "blueprobe-dom-patterns/1"

CATEGORIES: list[DomCategory] = [
    {"key": "repository_readme", "label": "リポジトリ README / Markdown プレビュー"},
    {"key": "article_reader", "label": "記事・ブログ・ニュース本文 (Article / Reader)"},
    {"key": "documentation", "label": "技術ドキュメント・解説ページ (Documentation)"},
    {"key": "portfolio_bio", "label": "ポートフォリオ・自己紹介・Profile 領域"},
    {"key": "reader_view", "label": "テキスト重視リーダービュー (Reader View)"},
    {"key": "social", "label": "SNS・タイムライン・コメントスレッド (Feed / Thread)"},
    {"key": "ecommerce", "label": "EC 商品詳細・商品一覧 (Product)"},
    {"key": "forum", "label": "Q&A・フォーラム (Question / Answer)"},
    {"key": "dashboard", "label": "ダッシュボード・カード／ウィジェット格子 (Dashboard Grid)"},
    {"key": "generic", "label": "汎用メインコンテンツ領域 (Generic Main)"},
]

DOM_PATTERNS: dict[str, DomPattern] = {
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
    "generic_main": {
        "key": "generic_main",
        "label": "Generic Main Region",
        "category": "generic",
        "selector": "main, #main, #content, .main-content",
        "description": "HTML5 標準の main タグおよび一般的な主要コンテンツ領域",
        "example_sites": ["Generic Web Pages"],
    },
    "social_timeline": {
        "key": "social_timeline",
        "label": "Social Timeline / Comment Thread",
        "category": "social",
        "selector": "[role='feed'], [role='feed'] > article, .timeline, .thread-comments, .comment-list",
        "description": "投稿カードが繰り返すタイムライン（ARIA feed）やコメントスレッド",
        "example_sites": ["SNS Timeline", "Mastodon", "Blog Comments"],
    },
    "ecommerce_product": {
        "key": "ecommerce_product",
        "label": "E-commerce Product Detail / Grid",
        "category": "ecommerce",
        "selector": "[itemtype='https://schema.org/Product'], [itemtype='http://schema.org/Product'], "
                    "[itemprop='price'], .product-detail, .product-grid",
        "description": "商品名・価格を持つ商品詳細（microdata Product）や商品一覧グリッド",
        "example_sites": ["EC Product Page", "Shop Category Grid"],
    },
    "forum_qa": {
        "key": "forum_qa",
        "label": "Q&A / Forum Question and Answers",
        "category": "forum",
        "selector": "[itemtype='https://schema.org/Question'], [itemtype='https://schema.org/Answer'], "
                    "[itemprop='acceptedAnswer'], [itemprop='suggestedAnswer'], .question, .answer",
        "description": "質問と回答の組（microdata Question/Answer、.question/.answer）",
        "example_sites": ["Stack Overflow", "Q&A Forums"],
    },
    "dashboard_grid": {
        "key": "dashboard_grid",
        "label": "Dashboard Card / Widget Grid",
        "category": "dashboard",
        "selector": ".dashboard, .widget-card, .grid-item, .card-grid",
        "description": "分析ツールや管理画面のカード・ウィジェットが並ぶ格子",
        "example_sites": ["Analytics Dashboard", "Admin Console"],
    },
}


def _pattern_copy(pattern: DomPattern) -> DomPattern:
    return {
        "key": pattern["key"],
        "label": pattern["label"],
        "category": pattern["category"],
        "selector": pattern["selector"],
        "description": pattern["description"],
        "example_sites": list(pattern["example_sites"]),
    }


def list_patterns() -> list[DomPattern]:
    """Return all pattern metadata dicts for dropdown UI choices or CLI selection."""
    return [_pattern_copy(pattern) for pattern in DOM_PATTERNS.values()]


def list_categories() -> list[DomCategory]:
    """Return category options."""
    return [DomCategory(key=category["key"], label=category["label"]) for category in CATEGORIES]


def get_pattern(pattern_key: str) -> DomPattern:
    """Retrieve pattern metadata dict by key or alias.

    Raises ValueError if pattern_key is unknown.
    """
    if not isinstance(pattern_key, str) or not pattern_key.strip():
        raise ValueError("pattern_key must be a non-empty string")
    key = pattern_key.strip().lower()
    if key not in DOM_PATTERNS:
        valid_keys = ", ".join(sorted(DOM_PATTERNS.keys()))
        raise ValueError(f"unknown pattern key {pattern_key!r}. Valid keys: {valid_keys}")
    return _pattern_copy(DOM_PATTERNS[key])


def get_selector_for_pattern(pattern_key: str) -> str:
    """Get the CSS selector corresponding to a pattern key."""
    return get_pattern(pattern_key)["selector"]


def detect_pattern(html: str) -> list[PatternMatch]:
    """Analyze DOM HTML and return candidate pattern matches ranked by match score.

    Score is based on selector presence and node matching count.
    Returns list of dicts:
      [{"pattern": pattern_dict, "score": int, "matched_nodes": int, "selector_used": str}, ...]
    """
    if not isinstance(html, str) or not html.strip():
        return []
    tree = HtmlTree(html)
    results: list[PatternMatch] = []
    for pattern in DOM_PATTERNS.values():
        selector = pattern["selector"]
        sub_selectors = [part.strip() for part in selector.split(",") if part.strip()]
        total_matched = 0
        best_sub_selector = None
        for sub in sub_selectors:
            nodes = tree.css(sub)
            if nodes:
                total_matched += len(nodes)
                if best_sub_selector is None:
                    best_sub_selector = sub
        if total_matched > 0:
            # Specific presets outrank broad ones (generic_main, reader_page).
            specificity_bonus = 10 if pattern["key"] not in ("generic_main", "reader_page") else 2
            results.append({
                "pattern": _pattern_copy(pattern),
                "score": total_matched + specificity_bonus,
                "matched_nodes": total_matched,
                "selector_used": best_sub_selector or selector,
            })
    results.sort(key=lambda item: (item["score"], item["matched_nodes"]), reverse=True)
    return results


CLASSIFICATION_SCHEMA = "blueprobe-dom-classification/1"
_BROAD = ("generic_main", "reader_page")
_SKIP_TEXT = {"script", "style", "noscript", "template"}
_MOUNT_IDS = {"app", "root", "__next", "__nuxt", "svelte", "main-app"}
_HASHED = (
    re.compile(r"^(?:css|sc|jsx|emotion|tw|svelte)-[A-Za-z0-9_-]{4,}$"),
    re.compile(r"^[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9]+__[A-Za-z0-9_-]{5,}$"),  # CSS Modules
    re.compile(r"^(?=(?:[^0-9]*[0-9]){2})[A-Za-z_][A-Za-z0-9_]{5,9}$"),  # e.g. "x3k9qz"
)
# schema.org / OpenGraph type -> pattern key. Only a classification signal.
_TYPE_HINTS = {
    "product": "ecommerce_product", "offer": "ecommerce_product", "productgroup": "ecommerce_product",
    "qapage": "forum_qa", "question": "forum_qa", "answer": "forum_qa",
    "article": "article_body", "newsarticle": "article_body", "blogposting": "article_body",
    "techarticle": "documentation_main",
    "socialmediaposting": "social_timeline", "discussionforumposting": "social_timeline", "comment": "social_timeline",
    "profilepage": "portfolio_profile", "person": "portfolio_profile",
}
_MIN_TEXT = 20
# Bare landmarks shared by several presets; a match through them alone is a fallback.
_LANDMARK_PARTS = {"main", "[role='main']", "#main", "#content"}


def _visible_text(node: _Element) -> str:
    parts: list[str] = []

    def walk(current: _Element) -> None:
        for child in current.children:
            if isinstance(child, _TextNode):
                parts.append(child.data)
            elif child.tag not in _SKIP_TEXT or (child.tag == "template" and _shadow_mode(child)):
                walk(child)

    walk(node)
    return normalize("".join(parts))


def _shadow_mode(node: _Element) -> str | None:
    if node.tag != "template":
        return None
    mode = node.attributes.get("shadowrootmode") or node.attributes.get("shadowroot")
    return mode.strip().lower() if mode else None


def _type_name(value: str) -> str:
    return value.rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1].strip().lower()


def _json_ld_types(data, out: list[str]) -> None:
    if isinstance(data, list):
        for item in data:
            _json_ld_types(item, out)
    elif isinstance(data, dict):
        kind = data.get("@type")
        for name in kind if isinstance(kind, list) else [kind]:
            if isinstance(name, str) and name not in out:
                out.append(name)
        for key, value in data.items():
            if key != "@type" and isinstance(value, (dict, list)):
                _json_ld_types(value, out)


def _structured_data(tree: HtmlTree) -> StructuredData:
    import json
    found: StructuredData = {"json_ld_types": [], "json_ld_invalid": 0, "microdata_types": [],
                             "itemprops": [], "opengraph": {}}
    for node in _walk_elements(tree.root):
        attrs = node.attributes
        if node.tag == "script" and (attrs.get("type") or "").strip().lower() == "application/ld+json":
            try:
                _json_ld_types(json.loads(node.text()), found["json_ld_types"])
            except ValueError:
                found["json_ld_invalid"] += 1
        if "itemscope" in attrs and attrs.get("itemtype"):
            for name in (attrs.get("itemtype") or "").split():
                if name not in found["microdata_types"]:
                    found["microdata_types"].append(name)
        if attrs.get("itemprop"):
            for name in (attrs.get("itemprop") or "").split():
                if name not in found["itemprops"]:
                    found["itemprops"].append(name)
        if node.tag == "meta":
            prop = (attrs.get("property") or "").strip().lower()
            if prop.startswith("og:") and attrs.get("content") is not None:
                found["opengraph"].setdefault(prop, attrs.get("content") or "")
    return found


def _table_observation(index: int, table: _Element) -> TableObservation:
    reasons: list[str] = []
    nested = False
    node = table.parent
    while node is not None:
        if node.tag == "table":
            nested = True
            break
        node = node.parent
    cells = [n for n in _walk_elements(table) if n.tag in {"td", "th"} and _nearest_table(n) is table]
    rows = [n for n in _walk_elements(table) if n.tag == "tr" and _nearest_table(n) is table]
    role = (table.attributes.get("role") or "").strip().lower()
    if role in {"presentation", "none"}:
        reasons.append(f"role={role}")
    contains_table = any(n.tag == "table" for n in _walk_elements(table))
    if contains_table:
        reasons.append("contains_table")
    data_hints = [hint for hint, ok in (
        ("th", any(c.tag == "th" for c in cells)),
        ("caption", any(n.tag == "caption" for n in table.iter())),
        ("thead", any(n.tag == "thead" for n in table.iter())),
        ("scope", any("scope" in c.attributes for c in cells)),
    ) if ok]
    blocky = any(n.tag in {"div", "section", "article", "nav", "form", "ul"} for c in cells for n in _walk_elements(c))
    if blocky and not data_hints:
        reasons.append("block_content_in_cells")
    if len(rows) <= 1 and not data_hints:
        reasons.append("single_row")
    if reasons and not (data_hints and not role):
        kind = "layout"
    elif data_hints:
        kind, reasons = "data", data_hints
    else:
        kind, reasons = "data", ["grid_without_headers"]
    return {"index": index, "kind": kind, "reasons": reasons, "rows": len(rows), "nested": nested}


def _nearest_table(node: _Element) -> _Element | None:
    current = node.parent
    while current is not None and current.tag != "table":
        current = current.parent
    return current


def _is_hashed_class(name: str) -> bool:
    return any(rx.match(name) for rx in _HASHED)


def classify_document(html: str) -> DocumentClassification:
    """Classify a saved HTML document without converting it.

    Only observes: candidate patterns (nodes with visible text only), landmarks,
    structured-data signals, declarative shadow roots, and table kinds.
    Downstream converters consume this dict (see docs/dom-patterns.md).
    """
    empty_sd: StructuredData = {"json_ld_types": [], "json_ld_invalid": 0, "microdata_types": [],
                                "itemprops": [], "opengraph": {}}
    result: DocumentClassification = {
        "schema": CLASSIFICATION_SCHEMA, "status": "empty", "patterns": [], "signals": [],
        "landmarks": {}, "articles": {"total": 0, "top_level": 0, "nested": 0},
        "structured_data": empty_sd, "shadow_roots": {"open": 0, "closed": 0}, "tables": [],
        "text_chars": 0, "hashed_class_ratio": 0.0,
    }
    if not isinstance(html, str) or not html.strip():
        return result
    tree = HtmlTree(html)
    elements = list(_walk_elements(tree.root))
    body_text = _visible_text(tree.root)
    result["text_chars"] = len(body_text)

    classes = [name for node in elements for name in (node.attributes.get("class") or "").split()]
    hashed = sum(1 for name in classes if _is_hashed_class(name))
    result["hashed_class_ratio"] = round(hashed / len(classes), 3) if classes else 0.0
    if classes and hashed / len(classes) >= 0.5:
        result["signals"].append("hashed_class_names")

    for node in elements:
        mode = _shadow_mode(node)
        if mode in {"open", "closed"}:
            result["shadow_roots"][mode] += 1
    if any(result["shadow_roots"].values()):
        result["signals"].append("declarative_shadow_dom")

    landmarks: Counter = Counter()
    for node in elements:
        if node.tag in {"main", "article", "nav", "aside", "header", "footer", "section"}:
            landmarks[node.tag] += 1
        role = (node.attributes.get("role") or "").strip().lower()
        if role:
            landmarks[f"role={role}"] += 1
    result["landmarks"] = dict(sorted(landmarks.items()))

    articles = [node for node in elements if node.tag == "article"]
    nested = sum(1 for node in articles if _nearest(node, "article") is not None)
    result["articles"] = {"total": len(articles), "top_level": len(articles) - nested, "nested": nested}
    if len(articles) - nested > 1:
        result["signals"].append("multiple_articles")
    if nested:
        result["signals"].append("nested_articles")

    tables = [node for node in elements if node.tag == "table"]
    result["tables"] = [_table_observation(i, node) for i, node in enumerate(tables)]
    if any(t["kind"] == "layout" for t in result["tables"]):
        result["signals"].append("layout_tables")

    sd = _structured_data(tree)
    result["structured_data"] = sd
    if sd["json_ld_types"]:
        result["signals"].append("json_ld")
    if sd["json_ld_invalid"]:
        result["signals"].append("json_ld_invalid")
    if sd["microdata_types"] or sd["itemprops"]:
        result["signals"].append("microdata")
    if sd["opengraph"]:
        result["signals"].append("opengraph")

    mounts = [node for node in elements
              if (node.attributes.get("id") or "") in _MOUNT_IDS or "data-reactroot" in node.attributes]
    scripts = [node for node in elements if node.tag == "script" and
               (node.attributes.get("src") or (node.attributes.get("type") or "").lower() == "module")]
    if result["text_chars"] < _MIN_TEXT:
        result["status"] = "client_rendered" if (mounts or scripts) and all(
            not _visible_text(node) for node in mounts) else "insufficient"
        if result["status"] == "client_rendered":
            result["signals"].append("empty_app_shell")
        return result

    hinted: dict[str, list[str]] = {}
    for name in sd["json_ld_types"] + sd["microdata_types"] + [sd["opengraph"].get("og:type", "")]:
        key = _TYPE_HINTS.get(_type_name(name)) if name else None
        if key:
            hinted.setdefault(key, []).append(name)

    matches: list[PatternMatch] = []
    distinctive: set[str] = set()
    for pattern in DOM_PATTERNS.values():
        total = 0
        best = None
        for sub in [part.strip() for part in pattern["selector"].split(",") if part.strip()]:
            nodes = [node for node in tree.css(sub) if _visible_text(node)]
            if nodes:
                total += len(nodes)
                best = best or sub
                if sub not in _LANDMARK_PARTS:
                    distinctive.add(pattern["key"])
        hint = hinted.get(pattern["key"])
        if total or hint:
            bonus = 2 if pattern["key"] in _BROAD else 10
            matches.append({
                "pattern": _pattern_copy(pattern),
                "score": total + (bonus if total else 0) + (5 if hint else 0),
                "matched_nodes": total,
                "selector_used": best or "structured_data",
            })
    matches.sort(key=lambda item: (item["score"], item["matched_nodes"]), reverse=True)
    result["patterns"] = matches
    specific = [m for m in matches if m["pattern"]["key"] not in _BROAD and m["pattern"]["key"] in distinctive]
    if specific:
        result["status"] = "matched"
    else:
        # Obfuscated classes: fall back to semantic tags / ARIA landmarks.
        result["status"] = "fallback"
        if landmarks.get("main") or landmarks.get("role=main"):
            result["signals"].append("fallback:main_landmark")
        elif articles:
            result["signals"].append("fallback:article")
        else:
            result["signals"].append("fallback:body")
    return result


def _nearest(node: _Element, tag: str) -> _Element | None:
    current = node.parent
    while current is not None and current.tag != tag:
        current = current.parent
    return current


def _observe_url(url: str, cache: Path | None = None, out: Path | None = None) -> int:
    """Fetch one HTTP(S) page with curl and classify its saved HTML."""
    import hashlib
    import json
    import shutil
    import subprocess
    import tempfile
    from urllib.parse import urlsplit

    try:
        parsed = urlsplit(url)
    except ValueError:
        print("invalid URL", file=sys.stderr)
        return 2
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username is not None:
        print("URL must be HTTP(S) without embedded credentials", file=sys.stderr)
        return 2
    if not shutil.which("curl"):
        print("curl is required to fetch a URL", file=sys.stderr)
        return 127
    if cache is not None:
        try:
            from cache_core import Cache
        except ModuleNotFoundError as error:
            if error.name != "cache_core":
                raise
            print("--cache requires QueRyu cache_core.py: run from Aoi (python aoi.py blueprobe …; aoi.py puts queryu/ "
                  "on the path) or put cache_core.py on PYTHONPATH", file=sys.stderr)
            return 2
    with tempfile.TemporaryDirectory(prefix="blueprobe-") as tmp:
        body = Path(tmp) / "body"
        try:
            result = subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location",
                                     "--proto", "=http,https", "--proto-redir", "=http,https",
                                     "--max-time", "30", "--max-filesize", "10485760", "--output", str(body),
                                     "--write-out", "%{http_code}", "--", url], capture_output=True, text=True, timeout=35)
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"curl failed: {error}", file=sys.stderr)
            return 1
        if result.returncode:
            print(f"curl failed (exit {result.returncode}): {result.stderr.strip()}", file=sys.stderr)
            return result.returncode
        if result.stdout.strip() != "200":
            print(f"expected HTTP 200, got {result.stdout.strip() or 'unknown'}", file=sys.stderr)
            return 1
        raw = body.read_bytes()
        if len(raw) > 10485760:
            print("response exceeds 10 MiB", file=sys.stderr)
            return 1
        try:
            html = raw.decode("utf-8")
        except UnicodeDecodeError:
            print("response is not UTF-8 HTML", file=sys.stderr)
            return 1
        report = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                  "classification": classify_document(html)}
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        try:
            if cache is not None:
                # Cache integrity and provenance are owned by QueRyu's standalone cache component.
                Cache(cache).put(url, url, "url", 200, raw, {})
            if out is not None:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(rendered, encoding="utf-8")
        except (OSError, ValueError) as error:
            print(f"failed to save observation: {error}", file=sys.stderr)
            return 1
        print(rendered, end="")
    return 0

# ──── snapshot supplier ───────────────────────────────────────────────────────────────────────────────────
# 保存済みページの供給元（snapshot supplier）の契約と、QueRyu 用アダプタ。
#
# この snapshot 供給元の経路では取得もキャッシュもしない。保存済みの本文を受け取り、
# 読むだけにする。QueRyu はその供給元の一つ。契約は docs/contract/v1/snapshot.md。
#
# 供給元（SnapshotSupplier）が持つもの:
#   entries()        -> [entry]  既定で読む行。各 entry は少なくとも key / url / group を持つ
#   body(entry)      -> str      照合済みの本文（HTML）。照合できなければ例外で止める
#   snapshot(entry)  -> dict     html-snapshot/1 の記録（下の SNAPSHOT_FIELDS）
#
# 供給元は再取得で失敗を隠してはならない。ネットワークにも出ない。

SNAPSHOT_SCHEMA = "html-snapshot/1"
# 必須: schema, html, url, encoding。任意だが値を推測で埋めない: fetched_at, response_sha256, content_sha256, cache_entry
SNAPSHOT_FIELDS = ("schema", "html", "url", "fetched_at", "response_sha256",
                   "content_sha256", "encoding", "cache_entry")
ENTRY_FIELDS = ("key", "url", "group")


@runtime_checkable
class SnapshotSupplier(Protocol):
    def entries(self) -> Iterable[dict]: ...
    def body(self, entry: dict) -> str: ...
    def snapshot(self, entry: dict) -> dict: ...


class QueRyuCacheSource:
    """QueRyu の `Cache`（Aoi/queryu）を供給元として包む。

    既定の entries() は key ごとの最新行（key の昇順）。照合は Cache 側が行う
    （sha256 と bytes の照合、失敗は CacheIntegrityError）。
    """

    def __init__(self, cache):
        self.cache = cache

    def entries(self) -> list[dict]:
        return [entry for _, entry in sorted(self.cache.latest().items())]

    def body(self, entry: dict) -> str:
        return self.cache.body(entry)

    def snapshot(self, entry: dict) -> dict:
        return self.cache.snapshot(entry)


# ──── HTML source ─────────────────────────────────────────────────────────────────────────────────────────
# Bridge saved HTML observations to a trusted, offline extractor.
#
# The extractor is supplied by application code, never loaded from request data.
# The optional default is mcp-toolcall-lab's stdlib HTML extraction module.
# No acquisition, asset loading, or network operation is owned here.

class HtmlSource:
    def __init__(self, *, selector=None, pattern=None, extractor=None, include_css=False, stylesheets=None,
                 snapshot_extractor=None):
        if pattern is not None and selector is None:
            selector = get_selector_for_pattern(pattern)
        self.pattern = pattern
        self.selector = selector
        self.extractor = extractor
        self.include_css = include_css
        self.stylesheets = stylesheets
        self.snapshot_extractor = snapshot_extractor

    def parse(self, html, url):
        extractor = self.extractor
        if extractor is None:
            try:
                from mcp_toolcall_lab.adapters.html_snapshot import extract
            except ImportError as exc:
                raise RuntimeError(
                    'provide an offline extractor or install the source-access version of mcp-toolcall-lab'
                ) from exc
            extractor = extract
        report = new_report()
        try:
            options = {'selector': self.selector}
            if self.include_css or self.stylesheets is not None:
                options.update(include_css=self.include_css, stylesheets=self.stylesheets)
            result = extractor(html, url, **options)
        except ValueError as exc:
            report['counts']['extraction_failed'] += 1
            report['unknown'].append({'raw': html, 'url': url, 'reason': str(exc)})
            return report
        report['records'].append({'key': url, 'url': url, 'raw': html, 'derived': result})
        return report

    def parse_snapshot(self, snapshot):
        """Use lab's existing snapshot validation, preserving acquisition provenance.

        Cache.snapshot verifies persisted bytes first. The lab validator checks
        the snapshot envelope and decoded content, not response authenticity or
        the truth of its URL/acquisition time. A raw extractor is not a substitute
        for this separate snapshot-extractor contract.
        """
        extractor = self.snapshot_extractor
        if extractor is None:
            try:
                from mcp_toolcall_lab.source_access import extract_snapshot
            except ImportError as exc:
                raise RuntimeError(
                    'provide an offline snapshot extractor or install the source-access version of mcp-toolcall-lab'
                ) from exc
            extractor = extract_snapshot
        report = new_report()
        options = {'selector': self.selector}
        if self.include_css or self.stylesheets is not None:
            options.update(include_css=self.include_css, stylesheets=self.stylesheets)
        try:
            result = extractor(snapshot, **options)
        except ValueError as exc:
            report['counts']['extraction_failed'] += 1
            saved = snapshot if isinstance(snapshot, dict) else {}
            raw = saved.get('html', '')
            report['unknown'].append({'raw': raw if isinstance(raw, str) else '',
                                      'url': saved.get('url'), 'reason': str(exc),
                                      'snapshot': snapshot})
            return report
        report['records'].append({
            'key': snapshot['url'], 'url': snapshot['url'], 'raw': snapshot['html'],
            'derived': result['extraction'], 'snapshot': result['snapshot'],
            'cache_entry': snapshot.get('cache_entry'),
        })
        return report


# ──── emoji ───────────────────────────────────────────────────────────────────────────────────────────────
# 保存済み HTML に出てくる絵文字を観測する。意味づけ・良し悪しの判断はしない。
#
# どこに（本文・属性・要素）、どの表記で（U+FE0F の有無）、どの文脈で（ボタン・リンク・
# aria-hidden・ラベルの有無）出ているかを、原文の抜粋とともに記録する。ネットワークにも
# キャッシュにも触れない。保存本文は QueRyu などの供給元から受け取る（docs/contract/v1/snapshot.md）。
#
# 判定の文法は UTS #51 の形（ZWJ・肌の色・国旗・キーキャップ・タグ）と Extended_Pictographic
# （Unicode 16.0）。xprobe の emoji_sequences と同じ契約で、tests/cases/emoji_corpus の期待値で揃える
# （他リポジトリのコードは import しない）。identity は U+FE0F を除いた形。
#
#     python emoji_observations.py page.html [--url URL] [--json]

EXT_PICT_UNICODE = "16.0"
_EXT_PICT = ("a9 ae 203c 2049 2122 2139 2194-2199 21a9-21aa 231a-231b 2328 2388 23cf 23e9-23f3 "
             "23f8-23fa 24c2 25aa-25ab 25b6 25c0 25fb-25fe 2600-2605 2607-2612 2614-2685 2690-2705 "
             "2708-2712 2714 2716 271d 2721 2728 2733-2734 2744 2747 274c 274e 2753-2755 2757 "
             "2763-2767 2795-2797 27a1 27b0 27bf 2934-2935 2b05-2b07 2b1b-2b1c 2b50 2b55 3030 303d "
             "3297 3299 1f000-1f0ff 1f10d-1f10f 1f12f 1f16c-1f171 1f17e-1f17f 1f18e 1f191-1f19a "
             "1f1ad-1f1e5 1f201-1f20f 1f21a 1f22f 1f232-1f23a 1f23c-1f23f 1f249-1f3fa 1f400-1f53d "
             "1f546-1f64f 1f680-1f6ff 1f774-1f77f 1f7d5-1f7ff 1f80c-1f80f 1f848-1f84f 1f85a-1f85f "
             "1f888-1f88f 1f8ae-1f8ff 1f90c-1f93a 1f93c-1f945 1f947-1faff 1fc00-1fffd")


def _emoji_class():
    parts = []
    for item in _EXT_PICT.split():
        lo, _, hi = item.partition("-")
        parts.append("\\U%08x" % int(lo, 16) + ("-\\U%08x" % int(hi, 16) if hi else ""))
    return "[" + "".join(parts) + "]"


_EMOJI_ELEMENT = _emoji_class() + "(?:\uFE0F|[\U0001F3FB-\U0001F3FF])?"
_EMOJI = re.compile("[\U0001F1E6-\U0001F1FF]{2}|[0-9#*]\uFE0F?\u20E3"
                    "|\U0001F3F4[\U000E0020-\U000E007E]+\U000E007F"
                    "|" + _EMOJI_ELEMENT + "(?:\u200D" + _EMOJI_ELEMENT + ")*")
_EMOJI_TEXT_ATTRIBUTES = ("aria-label", "title", "alt", "placeholder", "aria-description", "data-tooltip")
_EMOJI_META = ("description", "og:title", "og:description", "twitter:title", "twitter:description")
_EMOJI_SKIP = {"script", "style", "template", "noscript", "svg", "math"}
_EMOJI_CONTROLS = {"a", "button", "summary", "label", "option"}


def emoji_sequences(text: str) -> list[str]:
    """Emoji sequences in text. A single text-default symbol counts only with U+FE0F
    (below U+2190, or not a So symbol below U+1F000), as xprobe."""
    out = []
    for match in _EMOJI.finditer(text):
        seq = match.group()
        if len(seq) == 1 and (ord(seq) < 0x2190 or (ord(seq) < 0x1F000
                                                     and not unicodedata.category(seq).startswith("So"))):
            continue
        out.append(seq)
    return out


class _EmojiObserver(HTMLParser):
    def __init__(self, limit):
        super().__init__(convert_charrefs=True)
        self.stack, self.rows, self.limit, self.truncated, self.skip = [], [], limit, False, 0

    def _path(self):
        parts = []
        for tag, attrs in self.stack[-4:]:
            ident = ("#" + attrs["id"]) if attrs.get("id") else (
                "." + attrs["class"].split()[0] if attrs.get("class", "").split() else "")
            parts.append(tag + ident)
        return " > ".join(parts)

    def _context(self):
        control = next(((t, a) for t, a in reversed(self.stack)
                        if t in _EMOJI_CONTROLS or a.get("role") in ("button", "link", "tab", "menuitem")), None)
        return {"aria_hidden": any(a.get("aria-hidden") == "true" for _, a in self.stack),
                "in_control": control[0] if control else None,
                "control_label": (control[1].get("aria-label") or control[1].get("title")) if control else None}

    def _add(self, where, text):
        cursor = 0
        for seq in emoji_sequences(text):
            if len(self.rows) >= self.limit:
                self.truncated = True
                return
            start = text.find(seq, cursor)  # sequences come in text order; anchor each one to its own place
            cursor = start + len(seq)
            snippet = " ".join(text[max(0, start - 30):start + len(seq) + 30].split())
            self.rows.append({"emoji": seq, "identity": seq.replace("\ufe0f", ""), "where": where,
                              "element": self._path(), "raw_text": snippet, **self._context()})

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v or "") for k, v in attrs}
        if tag in _EMOJI_SKIP:
            self.skip += tag not in _VOID
        if not self.skip or tag in _EMOJI_SKIP:
            if tag == "meta" and (attrs.get("name") or attrs.get("property")) in _EMOJI_META:
                self.stack.append((tag, attrs))
                self._add("meta:" + (attrs.get("name") or attrs.get("property")), attrs.get("content", ""))
                self.stack.pop()
            elif not self.skip:
                self.stack.append((tag, attrs))
                for name in _EMOJI_TEXT_ATTRIBUTES:
                    if attrs.get(name):
                        self._add("attr:" + name, attrs[name])
                if tag in _VOID:
                    self.stack.pop()

    def handle_endtag(self, tag):
        if tag in _EMOJI_SKIP and self.skip:
            self.skip -= 1
            return
        if self.skip:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not self.skip and data.strip():
            title = self.stack and self.stack[-1][0] == "title"
            self._add("title" if title else "text", data)


def _emoji_observe(html: str, url: str | None = None, *, max_records: int = 5000) -> dict:
    """1ページの絵文字観測。records は 1 出現 1 行、counts は identity ごとの出現数。

    raw_text は前後30文字の抜粋（空白は詰める）。script・style・template・noscript・svg の
    中身は読まない（表示される文字ではないため）が、読まなかったことは数えない。
    max_records を超えたら unknown に truncated を1件残す（黙って捨てない）。
    """
    if not isinstance(html, str):
        raise TypeError("html must be str")
    parser = _EmojiObserver(max_records)
    parser.feed(html)
    parser.close()
    report = new_report()
    for index, row in enumerate(parser.rows):
        report["records"].append({"key": f"{url or ''}#{index}", "url": url, **row})
        report["counts"][row["identity"]] += 1
    if parser.truncated:
        report["unknown"].append({"url": url, "reason": f"truncated after {max_records} emoji"})
    return report


def _emoji_observe_snapshot(snapshot: dict, **kwargs) -> dict:
    """html-snapshot/1（QueRyu Cache.snapshot など）を観測する。来歴は records に引き継ぐ。"""
    if snapshot.get("schema") != "html-snapshot/1" or not isinstance(snapshot.get("html"), str):
        raise ValueError("expected an html-snapshot/1 record")
    report = _emoji_observe(snapshot["html"], snapshot.get("url"), **kwargs)
    for row in report["records"]:
        row["response_sha256"] = snapshot.get("response_sha256")
        row["fetched_at"] = snapshot.get("fetched_at")
    return report


def _emoji_summarize(report: dict) -> list[dict]:
    """identity ごとの要約: 件数、表記（U+FE0F 有無）、場所、ラベルなしの操作要素の中かどうか。"""
    rows = {}
    for record in report["records"]:
        row = rows.setdefault(record["identity"], {"identity": record["identity"], "count": 0,
                                                    "forms": Counter(), "where": Counter(),
                                                    "unlabelled_control": 0, "aria_hidden": 0})
        row["count"] += 1
        row["forms"][record["emoji"]] += 1
        row["where"][record["where"]] += 1
        row["unlabelled_control"] += bool(record["in_control"] and not record["control_label"]
                                          and not record["aria_hidden"])
        row["aria_hidden"] += record["aria_hidden"]
    return [dict(r, forms=dict(r["forms"]), where=dict(r["where"]))
            for r in sorted(rows.values(), key=lambda r: (-r["count"], r["identity"]))]


def _emoji_main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="blueprobe.py emoji", description="\U0001f600 保存済み HTML の絵文字を観測する（ネットワークに出ない）")
    ap.add_argument("html", type=Path)
    ap.add_argument("--url")
    ap.add_argument("--json", action="store_true", help="records と summary を JSON で出す")
    args = ap.parse_args(argv)
    try:
        report = _emoji_observe(args.html.read_text(encoding="utf-8"), args.url)
    except (OSError, UnicodeDecodeError) as error:
        print(f"emoji_observations: {error}", file=sys.stderr)
        return 2
    summary = _emoji_summarize(report)
    if args.json:
        print(json.dumps({"records": report["records"], "summary": summary, "unknown": report["unknown"]},
                         ensure_ascii=False, indent=1))
    else:
        for row in summary:
            forms = " ".join(f"{k}x{v}" for k, v in row["forms"].items())
            where = " ".join(f"{k}x{v}" for k, v in row["where"].items())
            extra = f" unlabelled_control={row['unlabelled_control']}" if row["unlabelled_control"] else ""
            print(f"{row['identity']}\t{row['count']}\t{forms}\t{where}{extra}")
        print(f"emoji: {len(summary)} distinct, {len(report['records'])} occurrence(s)"
              + (f"; {report['unknown'][0]['reason']}" if report["unknown"] else ""))
    return 0


# ──── names ───────────────────────────────────────────────────────────────────────────────────────────────
# 保存済み HTML の操作要素・画像に付く「名前」（アクセシブルネーム）を観測する。
#
# ボタン・リンク・入力・タブ・画像などについて、名前とその出どころ（aria-labelledby /
# aria-label / label / alt / title / 本文 / placeholder）、役割、絵文字だけの名前かどうか、
# aria-hidden の中にあるかを記録する。判断はしない。数えるだけ。
#
# 名前の計算は W3C accname の**近似**で、ブラウザの計算と同じではない（ACCNAME_APPROXIMATION）。
# CSS（::before / ::after の content、display:none）を評価しないため、CSS で付く装飾は名前に入らない。
# ブラウザで採った aria スナップショットとの突き合わせは compare_aria_snapshot() で行い、
# 一致・CSS 由来の差・不一致を分けて数える。ネットワークには出ない。
#
#     python accessible_names.py page.html [--json]
#     python accessible_names.py capture.json          # btk-browser-dom/1（aria_snapshot があれば突き合わせる）

_NAMES_SKIP = {"script", "style", "template", "noscript"}
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
        if self.skip or tag in _NAMES_SKIP:
            self.skip += tag in _NAMES_SKIP
            return
        node = _Node(tag, {k: (v or "") for k, v in attrs}, self.current)
        self.current.children.append(node)
        if tag not in _VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        if not self.skip:
            self.current.children.append(_Node(tag, {k: (v or "") for k, v in attrs}, self.current))

    def handle_endtag(self, tag):
        if tag in _NAMES_SKIP and self.skip:
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
    # Preserve DOM preorder without one Python generator frame per ancestor.
    stack = [iter(node.children)]
    while stack:
        try:
            child = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        if isinstance(child, _Node):
            yield child
            stack.append(iter(child.children))


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


def _names_observe(html: str, url: str | None = None) -> dict:
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


def _names_observe_capture(capture: dict) -> dict:
    """btk-browser-dom/1 または html-snapshot/1。aria_snapshot があれば突き合わせ結果も付ける。"""
    if capture.get("schema") not in ("btk-browser-dom/1", "html-snapshot/1") or not isinstance(capture.get("html"), str):
        raise ValueError("expected btk-browser-dom/1 or html-snapshot/1")
    report = _names_observe(capture["html"], capture.get("url"))
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


def _names_summarize(report: dict) -> dict:
    roles = Counter(r["role"] for r in report["records"])
    sources = Counter(r["name_source"] or "none" for r in report["records"])
    return {"controls": len(report["records"]), "roles": dict(roles), "name_sources": dict(sources),
            "flags": {k: v for k, v in report["counts"].items() if v}}


def _names_main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="blueprobe.py names", description="\U0001f3f7️ 保存済み HTML の操作要素・画像の名前を観測する（近似・ネットワークに出ない）")
    ap.add_argument("path", type=Path, help="HTML、または btk-browser-dom/1 / html-snapshot/1 の JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
        report = _names_observe_capture(json.loads(text)) if args.path.suffix == ".json" else _names_observe(text)
    except (OSError, ValueError) as error:
        print(f"accessible_names: {error}", file=sys.stderr)
        return 2
    summary = _names_summarize(report)
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


# ──── headings ────────────────────────────────────────────────────────────────────────────────────────────
# 保存済み HTML の見出し階層（<h1>〜<h6>）とランドマーク構造（<main>, <nav>, <header> 等）を観測する。
#
# 見出しのレベル、テキスト、要素の位置、包含するランドマーク、非表示状態、
# 構造上の不連続（階層のスキップ、空の見出し、複数の h1、メインランドマークの欠落、
# 未ラベルのランドマーク等）を記録する。判断はしない。数えるだけ。
#
# ネットワークには出ない。
#
#     python heading_observations.py page.html [--json]
#     python heading_observations.py capture.json          # btk-browser-dom/1 または html-snapshot/1

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


def _headings_observe(html: str, url: str | None = None) -> dict:
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


def _headings_observe_capture(capture: dict) -> dict:
    """btk-browser-dom/1 または html-snapshot/1 の JSON キャプチャを観測する。"""
    if capture.get("schema") not in ("btk-browser-dom/1", "html-snapshot/1") or not isinstance(capture.get("html"), str):
        raise ValueError("expected btk-browser-dom/1 or html-snapshot/1")
    return _headings_observe(capture["html"], capture.get("url"))


def _headings_summarize(report: dict) -> dict:
    headings = [r for r in report["records"] if r.get("type") == "heading"]
    landmarks = [r for r in report["records"] if r.get("type") == "landmark"]
    levels = Counter(f"h{r['level']}" for r in headings)
    return {"headings": len(headings), "landmarks": len(landmarks), "levels": dict(sorted(levels.items())),
            "flags": {k: v for k, v in report["counts"].items() if v}}


def _headings_main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="blueprobe.py headings", description="\U0001f9ed 保存済み HTML の見出し階層とランドマーク構造を観測する（ネットワークに出ない）")
    ap.add_argument("path", type=Path, help="HTML、または btk-browser-dom/1 / html-snapshot/1 の JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        text = args.path.read_text(encoding="utf-8")
        report = _headings_observe_capture(json.loads(text)) if args.path.suffix == ".json" else _headings_observe(text)
    except (OSError, ValueError) as error:
        print(f"heading_observations: {error}", file=sys.stderr)
        return 2
    summary = _headings_summarize(report)
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


# ──── web ─────────────────────────────────────────────────────────────────────────────────────────────────
# Read saved Web observations and source inventories, without a browser or SDK.
#
# This is an observation adapter, never a native-equivalence or integrity verifier.

WEB_SCHEMA = "web-portability-observations/1"
_WEB_LANGUAGES = {".dart": "dart", ".kt": "kotlin", ".swift": "swift"}
_WEB_EXCLUDED = {".git", ".dart_tool", ".venv", "node_modules", "build", "Pods", "vendor"}
_WEB_BUILD_FILES = {"pubspec.yaml", "pubspec.lock", "Podfile", "Podfile.lock",
               "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
               "gradle-wrapper.properties", "project.pbxproj", "Package.swift", "Package.resolved"}


def source_inventory(root: Path) -> list[dict]:
    """Hash source bytes; do not infer symbols, call graphs or executable behavior."""
    rows = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in _WEB_EXCLUDED for part in relative.parts) or path.is_symlink():
            continue
        if (path.suffix not in _WEB_LANGUAGES and path.name not in _WEB_BUILD_FILES) or not path.is_file():
            continue
        data = path.read_bytes()
        rows.append({"path": relative.as_posix(), "language": _WEB_LANGUAGES.get(path.suffix),
                     "kind": "build-config" if path.name in _WEB_BUILD_FILES else "source",
                     "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return rows


def _web_controls(value):
    if not isinstance(value, list) or not value:
        raise ValueError("missing control inventory")
    for control in value:
        if not isinstance(control, dict) or not isinstance(control.get("label"), str):
            raise ValueError("invalid control label")
        if not isinstance(control.get("visible"), bool):
            raise ValueError("invalid visibility")
        box = control.get("box", {})
        if not isinstance(box, dict):
            raise ValueError("invalid box")
        for name in ("x", "y", "width", "height"):
            number = box.get(name)
            if type(number) not in (int, float) or not math.isfinite(number):
                raise ValueError("invalid box coordinate")
        if box["width"] < 0 or box["height"] < 0:
            raise ValueError("negative box size")
    return value


def _web_nonfinite(value):
    raise ValueError(f"non-finite JSON number: {value}")


def _web_observe(root: Path, *, source_root: Path | None = None) -> dict:
    """Preserve receipts verbatim beside derived geometry and action records.

    Consumer-specific catalogue coverage and screenshot verification remain with
    the producer's existing verifier. Source hashes are not route bindings.
    """
    root = Path(root)
    if not root.is_dir():
        raise ValueError("observation root must be a directory")
    report = new_report()
    builds = set()
    for path in sorted(root.rglob("web-observation.json")):
        key = path.relative_to(root).as_posix()
        raw = None
        try:
            data = path.read_bytes()
            raw = data.decode("utf-8")
            raw = json.loads(raw, parse_constant=_web_nonfinite)
            if not isinstance(raw, dict) or raw.get("schema") != "flutter-web-observation/1":
                raise ValueError("unsupported observation schema")
            build = raw.get("build_sha")
            if not isinstance(build, str) or len(build) != 40 or any(c not in "0123456789abcdef" for c in build):
                raise ValueError("missing immutable build SHA")
            display = raw["runtime"]["display"]
            controls = _web_controls(display["controls"])
            if not isinstance(raw.get("url"), str) or not raw["url"]:
                raise ValueError("missing observed URL")
            exploration_path = path.with_name("exploration.json")
            exploration = None
            if exploration_path.exists():
                exploration = json.loads(exploration_path.read_text(encoding="utf-8"), parse_constant=_web_nonfinite)
                if exploration.get("schema") != "flutter-web-exploration/1" or not isinstance(exploration.get("actions"), list):
                    raise ValueError("unsupported exploration receipt")
            builds.add(build)
            report["records"].append({"key": key, "raw": raw,
                "raw_exploration": exploration,
                "derived": {"url": raw["url"], "reported_build_sha": build,
                    "controls": controls, "viewport": display.get("viewport"),
                    "actions": None if exploration is None else exploration["actions"],
                    "producer_status": raw.get("status"),
                    "capture_errors": raw.get("capture_errors"),
                    "evidence_sha256": hashlib.sha256(data).hexdigest()}})
            report["counts"]["observations"] += 1
            if raw.get("status") != "passed" or raw.get("capture_errors"):
                report["counts"]["producer_failed_or_incomplete"] += 1
            if exploration is None:
                report["counts"]["missing_action_receipts"] += 1
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            report["counts"]["invalid"] += 1
            report["unknown"].append({"key": key, "raw": raw, "reason": str(error)})
    if not report["records"]:
        report["counts"]["invalid"] += 1
        report["unknown"].append({"key": ".", "raw": None, "reason": "no usable observations"})
    if len(builds) > 1:
        report["counts"]["invalid"] += 1
        report["unknown"].append({"key": ".", "raw": sorted(builds), "reason": "mixed reported build SHAs"})
    if source_root is not None and not Path(source_root).is_dir():
        raise ValueError("source root must be a directory")
    return {"schema": WEB_SCHEMA, "scope": "saved-web-observations",
        "current_code_executed": False, "native_equivalence_verified": False,
        "report": report,
        "sources": source_inventory(Path(source_root)) if source_root is not None else [],
        "unobserved": ["backend request/response bodies and state transitions",
            "full DOM/accessibility hierarchy and per-action geometry/state changes",
            "OS permissions, native plugins and device side effects",
            "source-to-route bindings and source/build correspondence",
            "independent Python/Node implementation conformance"]}


def _web_main(argv=None):
    parser = argparse.ArgumentParser(prog="blueprobe.py web", description="\U0001f310 Read saved Web observations and source inventories, without a browser or SDK.")
    parser.add_argument("observations", type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args(argv)
    try:
        result = _web_observe(args.observations, source_root=args.source_root)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    return 2 if result["report"]["counts"]["invalid"] else 0


# ──── github ──────────────────────────────────────────────────────────────────────────────────────────────
# Extract repository-scoped issue and CI observations from a saved parent audit.

def _github_observe(snapshot: dict, repository: str) -> dict:
    """Observe the existing parent-audit/1 records without network access or diagnosis."""
    if not isinstance(snapshot, dict) or snapshot.get("schema") != "parent-audit/1":
        raise ValueError("expected parent-audit/1 snapshot")
    if not isinstance(repository, str) or not repository or "/" in repository:
        raise ValueError("repository must be the repository name in the snapshot")
    if not isinstance(snapshot.get("records"), list) or not isinstance(snapshot.get("repositories"), list):
        raise ValueError("snapshot records and repositories must be lists")
    report = new_report()
    generated_at = snapshot.get("generated_at")
    try:
        observed = datetime.datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        if observed.tzinfo is None:
            raise ValueError("observation time requires a timezone")
    except (AttributeError, TypeError, ValueError):
        report["unknown"].append({"key": repository, "reason": "snapshot observation time unavailable or invalid"})
    if not isinstance(snapshot.get("owner"), str) or not snapshot["owner"].strip():
        report["unknown"].append({"key": repository, "reason": "snapshot owner unavailable or invalid"})
    if repository not in snapshot["repositories"]:
        report["unknown"].append({"key": repository, "reason": "repository not listed in snapshot"})
    truncated = snapshot.get("truncated")
    if not isinstance(truncated, list) or not all(isinstance(name, str) for name in truncated):
        report["unknown"].append({"key": repository, "reason": "snapshot truncation list unavailable or invalid"})
    elif repository in truncated:
        report["unknown"].append({"key": repository, "reason": "repository observation truncated"})
    errors = snapshot.get("errors")
    if not isinstance(errors, list):
        report["unknown"].append({"key": repository, "reason": "snapshot error list unavailable"})
    elif any(not isinstance(error, dict) or not isinstance(error.get("repository"), str) for error in errors):
        report["unknown"].append({"key": repository, "reason": "invalid collection error entries"})
    else:
        relevant = [error for error in errors if error["repository"] == repository]
        if relevant:
            report["unknown"].append({"key": repository, "reason": "repository collection failed", "raw": relevant})
    for index, item in enumerate(snapshot["records"]):
        if not isinstance(item, dict):
            report["unknown"].append({"key": str(index), "reason": "invalid record", "raw": item})
            continue
        if item.get("repository") != repository:
            continue
        kind = item.get("kind")
        if kind not in ("issue", "pr") or not isinstance(item.get("id"), str):
            report["unknown"].append({"key": str(index), "reason": "unsupported record", "raw": item})
            continue
        if kind == "pr" and (not isinstance(item.get("ci"), str) or not item["ci"]
                             or not isinstance(item.get("head_sha"), str) or not item["head_sha"]):
            report["unknown"].append({"key": item["id"], "reason": "PR CI or head identity unavailable", "raw": item})
        report["records"].append({"key": item["id"], "raw": item,
                                  "derived": {"repository": repository, "kind": kind,
                                              "observed_ci": item.get("ci"),
                                              "labels": item.get("labels"),
                                              "head_sha": item.get("head_sha")}})
        report["counts"][kind] += 1
    return {"schema": "github-repository-observations/1", "generated_at": snapshot.get("generated_at"),
            "owner": snapshot.get("owner"), "repository": repository, "report": report}


def _github_main(argv=None):
    parser = argparse.ArgumentParser(prog="blueprobe.py github", description="\U0001f419 Extract repository-scoped issue and CI observations from a saved parent audit.")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("repository", help="repository name as listed in parent-audit/1")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = _github_observe(snapshot, args.repository)
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 2 if result["report"]["unknown"] else 0


# ──── tools: python blueprobe.py <tool> … / blueprobe.<tool>.observe(…) ──────────────────────────────
emoji = SimpleNamespace(observe=_emoji_observe, observe_snapshot=_emoji_observe_snapshot, summarize=_emoji_summarize, emoji_sequences=emoji_sequences, main=_emoji_main)
names = SimpleNamespace(observe=_names_observe, observe_capture=_names_observe_capture, summarize=_names_summarize, parse_aria_snapshot=parse_aria_snapshot, compare_aria_snapshot=compare_aria_snapshot, main=_names_main)
headings = SimpleNamespace(observe=_headings_observe, observe_capture=_headings_observe_capture, summarize=_headings_summarize, main=_headings_main)
web = SimpleNamespace(observe=_web_observe, source_inventory=source_inventory, main=_web_main)
github = SimpleNamespace(observe=_github_observe, main=_github_main)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tool = globals().get(argv[0]) if argv else None
    if isinstance(tool, SimpleNamespace):  # names / headings / emoji / web / github
        return tool.main(argv[1:])
    ap = argparse.ArgumentParser(description="\U0001f50e 取得済みページをオフラインで再解析する",
                                 epilog="\U0001f9f0 tools: \U0001f3f7️ names · \U0001f9ed headings · \U0001f600 emoji · \U0001f310 web · \U0001f419 github "
                                        "（python blueprobe.py <tool> --help）")
    ap.add_argument("url", nargs="?", help="HTTP(S) URL to fetch and classify with curl")
    ap.add_argument("--source", help="取得元モジュール名 (例: html_source)")
    patterns = ap.add_mutually_exclusive_group()
    patterns.add_argument("--pattern", help="html_source 専用の DOM パターンキー（一覧: --list-patterns）")
    ap.add_argument("--cache", type=Path, help="QueRyu のキャッシュディレクトリ")
    ap.add_argument("--out", type=Path, help="Markdown の出力先")
    ap.add_argument("--strict", action="store_true", help="未知の表記、または既知値と合わない group があれば終了コード1")
    patterns.add_argument("--list-patterns", action="store_true", help="利用可能な DOM パターンの一覧を表示する")
    patterns.add_argument("--classify", type=Path, metavar="HTML",
                          help="保存済み HTML ファイル1つを分類し、derived を JSON で表示する（ネットワークなし）")
    args = ap.parse_args(argv)

    if args.url:
        if args.source or args.pattern or args.list_patterns or args.classify or args.strict:
            ap.error("URL cannot be combined with source, pattern, classify, list-patterns or strict")
        return _observe_url(args.url, args.cache, args.out)

    if args.classify is not None:
        import json
        html = args.classify.read_text(encoding="utf-8", errors="replace")
        print(json.dumps(classify_document(html), ensure_ascii=False, indent=2))
        return 0

    if args.list_patterns:
        patterns = list_patterns()
        print("利用可能な DOM パターン一覧 (Dropdown / Preset 指定用):")
        for p in patterns:
            print(f"  - {p['key']:<20} [{p['category']}] {p['label']}")
            print(f"      selector: {p['selector']}")
            print(f"      desc: {p['description']}")
        return 0

    if not args.source or not args.cache:
        ap.error("--source and --cache are required unless --list-patterns is specified")

    if args.pattern is not None:
        if args.source != "html_source":
            ap.error("--pattern requires --source html_source")
        try:
            source = HtmlSource(pattern=args.pattern)
        except ValueError as exc:
            ap.error(f"--pattern: {exc}. Use --list-patterns to see available presets")
    else:
        source = load_source(args.source)

    manifest = args.cache / "manifest.jsonl"
    if not manifest.exists():
        print(f"no cache manifest: {manifest}", file=sys.stderr)
        return 1
    try:
        from queryu import Cache
    except ModuleNotFoundError as error:
        if error.name != "queryu":
            raise
        print("--cache requires QueRyu: run from Aoi (python aoi.py blueprobe …; aoi.py puts queryu/ on the path) "
              "or put queryu on PYTHONPATH", file=sys.stderr)
        return 2
    records: list = []
    rows = inspect_queryu_cache(source, Cache(args.cache), records_out=records)
    checks = source.check(records) if hasattr(source, "check") else None
    md = to_markdown(rows, f"{args.source}: 観測された構造", checks)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
    print(md)
    n_unknown = sum(r["unknown"] for r in rows)
    if n_unknown:
        print(f"unknown: {n_unknown} 件。表記の変化を疑う（上の表を参照）", file=sys.stderr)
    failed = [c["group"] for c in checks or [] if not c["ok"]]
    if failed:
        print(f"既知値と合わない group: {', '.join(failed)}（取りこぼし・混入を疑う）", file=sys.stderr)
    return 1 if (args.strict and (n_unknown or failed)) else 0


if __name__ == "__main__":
    # Colocated optional components are enabled only for an explicit cache request.
    if any(arg == "--cache" or arg.startswith("--cache=") for arg in sys.argv[1:]):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
