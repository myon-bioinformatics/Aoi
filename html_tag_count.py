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
