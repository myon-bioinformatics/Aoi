"""Count HTML elements with html.parser (no browser), and 📊 draw FluidFullSpeedSimulation's still figures.

The element counter works when this file is copied alone. FFSS uses this repository's
records / figures modules, all with standard-library imports only.

📊 FFSS draws flows that change over time as GIFs; the still figures (Sankey, waterfall, T–Q, balance point,
start-up Gantt, sensitivity tornado, window heatmap) are drawn here from its ``--jsonl`` records, without
re-judging them: ``ffss_figures`` builds plotly figure JSON, ``write_ffss`` writes an HTML page (plotly.js) and
SVG files (the parent's stdlib ``plotly_min``, no Chrome).
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


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


# --- 📊 FluidFullSpeedSimulation (FFSS) records → still figures ----------------------------------------

def _ffss_module(name):
    # The element counter remains usable after copying this single file elsewhere.
    # Only --ffss needs the repository modules, including their relative imports.
    import importlib, sys, types
    package = __package__ or "_dragowing_ffss"
    if package not in sys.modules:
        module = types.ModuleType(package)
        module.__path__ = [str(Path(__file__).resolve().parent)]
        sys.modules[package] = module
    return importlib.import_module(f"{package}.{name}")


def read_ffss(path):
    return _ffss_module("records").read_ffss(path)


def ffss_figures(records):
    return _ffss_module("figures").ffss_figures(records)


def plotly_min():
    return _ffss_module("figures").plotly_min()


def write_ffss(records_path, out_dir, *, svg=True):
    return _ffss_module("figures").write_ffss(records_path, out_dir, svg=svg)


def __getattr__(name):
    if name == "FFSS_FIGURES":
        return _ffss_module("figures").FFSS_FIGURES
    raise AttributeError(name)


def main(argv=None) -> int:
    """Count elements in a saved HTML document or stdin, or 📊 draw FFSS records (``--ffss``)."""
    import argparse
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Count HTML elements in a saved document (stdlib only).")
    parser.add_argument("file", nargs="?", help="HTML file; omit or use - to read stdin")
    parser.add_argument("--tag", action="append", default=[], help="Limit to a tag; may be repeated")
    parser.add_argument("--ffss", type=Path, metavar="RECORDS",
                        help="📊 FFSS の --jsonl の記録から ffss.html と svg/F<NN>_*.svg を書く（Chrome なし）")
    parser.add_argument("--out", type=Path, default=Path("build/ffss"), help="📊 --ffss の書き出し先")
    parser.add_argument("--no-svg", action="store_true", help="📊 --ffss で HTML だけ")
    args = parser.parse_args(argv)
    if args.ffss is not None:
        try:
            written = write_ffss(args.ffss, args.out, svg=not args.no_svg)
        except (OSError, ValueError, KeyError) as exc:
            parser.exit(1, f"Cannot draw FFSS records: {exc}\n")
        for path in written:
            print(f"{'🖼️' if path.suffix == '.svg' else '📄'} {path.resolve().as_uri()} {path.stat().st_size} B")
        return 0
    try:
        html = sys.stdin.read() if not args.file or args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"Cannot read HTML: {exc}\n")
    print(json.dumps(count_elements(html, tuple(tag.lower() for tag in args.tag)), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
