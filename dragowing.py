"""Count HTML elements with html.parser (no browser). Useful for page-weight checks."""

from __future__ import annotations

from html.parser import HTMLParser


class _Counter(HTMLParser):
    def __init__(self, names: set[str] | None):
        super().__init__()
        self.names = names
        self.counts: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.names is not None and tag not in self.names:
            return
        self.counts[tag] = self.counts.get(tag, 0) + 1


def count_elements(html: str, tag_names: tuple[str, ...] | None = None) -> dict[str, int]:
    """Return a map of tag name to open-tag count. ``tag_names`` limits which tags are counted."""
    names = set(tag_names) if tag_names else None
    parser = _Counter(names)
    parser.feed(html)
    parser.close()
    return parser.counts


def main(argv=None) -> int:
    """Count elements in a saved HTML document or stdin."""
    import argparse
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Count HTML elements in a saved document (stdlib only).")
    parser.add_argument("file", nargs="?", help="HTML file; omit or use - to read stdin")
    parser.add_argument("--tag", action="append", default=[], help="Limit to a tag; may be repeated")
    args = parser.parse_args(argv)
    try:
        html = sys.stdin.read() if not args.file or args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"Cannot read HTML: {exc}\n")
    print(json.dumps(count_elements(html, tuple(tag.lower() for tag in args.tag)), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
