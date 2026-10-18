"""保存済み HTML に出てくる絵文字を観測する。意味づけ・良し悪しの判断はしない。

どこに（本文・属性・要素）、どの表記で（U+FE0F の有無）、どの文脈で（ボタン・リンク・
aria-hidden・ラベルの有無）出ているかを、原文の抜粋とともに記録する。ネットワークにも
キャッシュにも触れない。保存本文は QueRyu などの供給元から受け取る（docs/contract/v1/snapshot.md）。

判定の文法は UTS #51 の形（ZWJ・肌の色・国旗・キーキャップ・タグ）と Extended_Pictographic
（Unicode 16.0）。xprobe の emoji_sequences と同じ契約で、tests/cases/emoji_corpus の期待値で揃える
（他リポジトリのコードは import しない）。identity は U+FE0F を除いた形。

    python emoji_observations.py page.html [--url URL] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from blueprobe import new_report

__all__ = ["emoji_sequences", "observe", "observe_snapshot", "summarize"]

EXT_PICT_UNICODE = "16.0"
_EXT_PICT = ("a9 ae 203c 2049 2122 2139 2194-2199 21a9-21aa 231a-231b 2328 2388 23cf 23e9-23f3 "
             "23f8-23fa 24c2 25aa-25ab 25b6 25c0 25fb-25fe 2600-2605 2607-2612 2614-2685 2690-2705 "
             "2708-2712 2714 2716 271d 2721 2728 2733-2734 2744 2747 274c 274e 2753-2755 2757 "
             "2763-2767 2795-2797 27a1 27b0 27bf 2934-2935 2b05-2b07 2b1b-2b1c 2b50 2b55 3030 303d "
             "3297 3299 1f000-1f0ff 1f10d-1f10f 1f12f 1f16c-1f171 1f17e-1f17f 1f18e 1f191-1f19a "
             "1f1ad-1f1e5 1f201-1f20f 1f21a 1f22f 1f232-1f23a 1f23c-1f23f 1f249-1f3fa 1f400-1f53d "
             "1f546-1f64f 1f680-1f6ff 1f774-1f77f 1f7d5-1f7ff 1f80c-1f80f 1f848-1f84f 1f85a-1f85f "
             "1f888-1f88f 1f8ae-1f8ff 1f90c-1f93a 1f93c-1f945 1f947-1faff 1fc00-1fffd")


def _class():
    parts = []
    for item in _EXT_PICT.split():
        lo, _, hi = item.partition("-")
        parts.append("\\U%08x" % int(lo, 16) + ("-\\U%08x" % int(hi, 16) if hi else ""))
    return "[" + "".join(parts) + "]"


_ELEMENT = _class() + "(?:\uFE0F|[\U0001F3FB-\U0001F3FF])?"
_EMOJI = re.compile("[\U0001F1E6-\U0001F1FF]{2}|[0-9#*]\uFE0F?\u20E3"
                    "|\U0001F3F4[\U000E0020-\U000E007E]+\U000E007F"
                    "|" + _ELEMENT + "(?:\u200D" + _ELEMENT + ")*")
_TEXT_ATTRIBUTES = ("aria-label", "title", "alt", "placeholder", "aria-description", "data-tooltip")
_META = ("description", "og:title", "og:description", "twitter:title", "twitter:description")
_SKIP = {"script", "style", "template", "noscript", "svg", "math"}
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
_CONTROLS = {"a", "button", "summary", "label", "option"}


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


class _Observer(HTMLParser):
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
                        if t in _CONTROLS or a.get("role") in ("button", "link", "tab", "menuitem")), None)
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
        if tag in _SKIP:
            self.skip += tag not in _VOID
        if not self.skip or tag in _SKIP:
            if tag == "meta" and (attrs.get("name") or attrs.get("property")) in _META:
                self.stack.append((tag, attrs))
                self._add("meta:" + (attrs.get("name") or attrs.get("property")), attrs.get("content", ""))
                self.stack.pop()
            elif not self.skip:
                self.stack.append((tag, attrs))
                for name in _TEXT_ATTRIBUTES:
                    if attrs.get(name):
                        self._add("attr:" + name, attrs[name])
                if tag in _VOID:
                    self.stack.pop()

    def handle_endtag(self, tag):
        if tag in _SKIP and self.skip:
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


def observe(html: str, url: str | None = None, *, max_records: int = 5000) -> dict:
    """1ページの絵文字観測。records は 1 出現 1 行、counts は identity ごとの出現数。

    raw_text は前後30文字の抜粋（空白は詰める）。script・style・template・noscript・svg の
    中身は読まない（表示される文字ではないため）が、読まなかったことは数えない。
    max_records を超えたら unknown に truncated を1件残す（黙って捨てない）。
    """
    if not isinstance(html, str):
        raise TypeError("html must be str")
    parser = _Observer(max_records)
    parser.feed(html)
    parser.close()
    report = new_report()
    for index, row in enumerate(parser.rows):
        report["records"].append({"key": f"{url or ''}#{index}", "url": url, **row})
        report["counts"][row["identity"]] += 1
    if parser.truncated:
        report["unknown"].append({"url": url, "reason": f"truncated after {max_records} emoji"})
    return report


def observe_snapshot(snapshot: dict, **kwargs) -> dict:
    """html-snapshot/1（QueRyu Cache.snapshot など）を観測する。来歴は records に引き継ぐ。"""
    if snapshot.get("schema") != "html-snapshot/1" or not isinstance(snapshot.get("html"), str):
        raise ValueError("expected an html-snapshot/1 record")
    report = observe(snapshot["html"], snapshot.get("url"), **kwargs)
    for row in report["records"]:
        row["response_sha256"] = snapshot.get("response_sha256")
        row["fetched_at"] = snapshot.get("fetched_at")
    return report


def summarize(report: dict) -> list[dict]:
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="保存済み HTML の絵文字を観測する（ネットワークに出ない）")
    ap.add_argument("html", type=Path)
    ap.add_argument("--url")
    ap.add_argument("--json", action="store_true", help="records と summary を JSON で出す")
    args = ap.parse_args(argv)
    try:
        report = observe(args.html.read_text(encoding="utf-8"), args.url)
    except (OSError, UnicodeDecodeError) as error:
        print(f"emoji_observations: {error}", file=sys.stderr)
        return 2
    summary = summarize(report)
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


if __name__ == "__main__":
    raise SystemExit(main())
