"""BlueProbe — 観測する。解釈はあとで。

取得元（source）に依存しない部分だけを置く。
  - normalize(): 表記揺れの吸収。何をしたかは記録単位で残す
  - Report: 1ページを読んだ結果の契約。採用したもの以外も必ず数える
  - inspect(): 取得済みのページを再解析して集計する。ネットワークには出ない

取得元ごとの読み方は別モジュール（例: npb_calendar.py）に置き、次の2つを持たせる:
  pages(scope)        -> [(key, url, group)]   取得すべきページの一覧
  parse(html, url)    -> Report               1ページの観測結果

DOM パターン表と、その判定に使う HTML 木もここにある。木は html.parser で組み立てる。

Aoi の原則との対応:
  Observe Before Explaining  … 原文(raw)と読み取った値(derived)を同じ記録に並べる
  Never Hide Unknowns        … unknown は件数と原文を残す
  Separate Facts From Explanations … ここでは勝敗も点差も計算しない
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
import unicodedata
from collections import Counter
from collections.abc import Iterable, Iterator
from html.parser import HTMLParser
from pathlib import Path
from typing import TypedDict

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
    """取得元モジュールを名前で読み込む（blueprobe/ 直下の <name>.py）。"""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(f"invalid source name: {name!r}")
    return importlib.import_module(name)


def mask_digits(text: str) -> str:
    """docs に未知表記の「形」だけ残すため、数字を # に伏せる。"""
    return re.sub(r"[0-9０-９]", "#", text)


def inspect(source, pages: Iterable[tuple[str, str, str, str]], records_out: list | None = None) -> list[dict]:
    """取得済みページ (key, url, group, html) を再解析し、group ごとに集計する。

    ネットワークには出ない。解析ルールを直したら、これだけを何度でも回す。
    """
    return _inspect(source.parse, pages, records_out)


def inspect_snapshots(source, supplier, entries=None, records_out=None) -> list[dict]:
    """供給元（snapshot_source.SnapshotSupplier）の保存済み本文を、オフラインで再解析する。

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
    from snapshot_source import QueRyuCacheSource
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
    """html.parser tree with the CSS subset the pattern table and NPB readers use.

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
    {"key": "npb_sports", "label": "NPB（プロ野球）公式日程・成績表"},
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="取得済みページをオフラインで再解析する")
    ap.add_argument("--source", help="取得元モジュール名 (例: npb_calendar, html_source)")
    patterns = ap.add_mutually_exclusive_group()
    patterns.add_argument("--pattern", help="html_source 専用の DOM パターンキー（一覧: --list-patterns）")
    ap.add_argument("--cache", type=Path, help="QueRyu のキャッシュディレクトリ")
    ap.add_argument("--out", type=Path, help="Markdown の出力先")
    ap.add_argument("--strict", action="store_true", help="未知の表記、または既知値と合わない group があれば終了コード1")
    patterns.add_argument("--list-patterns", action="store_true", help="利用可能な DOM パターンの一覧を表示する")
    args = ap.parse_args(argv)

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
        from html_source import HtmlSource
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
    from queryu import Cache
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
    sys.path[:0] = [str(Path(__file__).resolve().parent),
                    str(Path(__file__).resolve().parents[1] / "queryu")]
    raise SystemExit(main())
