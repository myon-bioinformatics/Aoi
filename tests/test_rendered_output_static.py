"""Browser-free layer: drawn output is checked against the figure spec before any browser test.

The browser tests (dragowing export, startup validation) answer "can Chromium start and draw".
These tests answer "is what was drawn, and what the browser was given, the figure we asked for",
using saved PNG/SVG from a real Chromium (tests/fixtures/rendered_plotly) and the page builder.
They start no browser, run no JavaScript and need no network. They also prove the checks can fail:
each corruption below must be rejected, and each figure's output must match only its own spec.
"""
from __future__ import annotations

import hashlib
import json
import random
import struct
import xml.etree.ElementTree as ET
import zlib
from dataclasses import replace
from pathlib import Path

import pytest

from dragowing.export import PLOTLY, plotly_figure_content
from scripts import diagnose_dragowing_browser as diagnostic
from scripts import rendered_output_checks as checks
from scripts.rendered_output_checks import OutputMismatch

FIXTURES = Path(__file__).parent / "fixtures" / "rendered_plotly"
FIGURES = diagnostic._figures()
INDEXES = range(len(FIGURES))
SVG = "{http://www.w3.org/2000/svg}"
CHECK = {"png": checks.check_png, "svg": checks.check_svg}


def saved(index: int, fmt: str) -> bytes:
    return (FIXTURES / ("figure-%d.%s" % (index, fmt))).read_bytes()


# --- the saved output belongs to the current figures ---------------------------------------------

def test_manifest_matches_the_current_figures_and_files():
    manifest = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "aoi-rendered-plotly-fixtures/1"
    assert manifest["figures_sha256"] == checks.figures_digest(FIGURES), \
        "the synthetic figures changed: run scripts/render_static_fixtures.py"
    on_disk = {p.name for p in FIXTURES.iterdir()} - {"manifest.json"}
    assert on_disk == set(manifest["files"]) == {"figure-%d.%s" % (i, f) for i in INDEXES for f in CHECK}
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest, name


@pytest.mark.parametrize("fmt", sorted(CHECK))
@pytest.mark.parametrize("index", INDEXES)
def test_saved_output_matches_its_own_figure(index, fmt):
    CHECK[fmt](saved(index, fmt), FIGURES[index])


@pytest.mark.parametrize("fmt", sorted(CHECK))
@pytest.mark.parametrize("index", INDEXES)
def test_saved_output_matches_only_its_own_figure(index, fmt):
    for other in INDEXES:
        if other != index:
            with pytest.raises(OutputMismatch):
                CHECK[fmt](saved(index, fmt), FIGURES[other])


@pytest.mark.parametrize("fmt", sorted(CHECK))
@pytest.mark.parametrize("index", INDEXES)
def test_the_validator_of_the_browser_run_accepts_the_saved_output(index, fmt):
    diagnostic._validate_image(saved(index, fmt), fmt, FIGURES[index])


# --- PNG: what the check rejects -----------------------------------------------------------------

def _chunk(tag: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body))


def _png(width, height, rows, *, channels=3, kinds=(0,), header=None) -> bytes:
    """A PNG built with the given row filter kinds (cycled), the encoder side of the decoder."""
    def paeth(a, b, c):
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        return a if pa <= pb and pa <= pc else b if pb <= pc else c

    data, previous = b"", bytes(width * channels)
    for y, line in enumerate(rows):
        kind = kinds[y % len(kinds)]
        out = bytearray([kind])
        for i, value in enumerate(line):
            a = line[i - channels] if i >= channels else 0
            b = previous[i]
            c = previous[i - channels] if i >= channels else 0
            out.append((value - {0: 0, 1: a, 2: b, 3: (a + b) // 2, 4: paeth(a, b, c)}[kind]) & 255)
        data += bytes(out)
        previous = line
    header = header or struct.pack(">IIBBBBB", width, height, 8, 2 if channels == 3 else 6, 0, 0, 0)
    return (checks.PNG_SIGNATURE + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(data))
            + _chunk(b"IEND", b""))


def _picture(width, height, paint) -> list[bytes]:
    return [b"".join(bytes(paint(x, y)) for x in range(width)) for y in range(height)]


@pytest.mark.parametrize("channels", [3, 4])
@pytest.mark.parametrize("kinds", [(0,), (1,), (2,), (3,), (4,), (0, 1, 2, 3, 4)], ids=str)
def test_png_decoder_restores_every_row_filter(kinds, channels):
    rng = random.Random(7)
    rows = [bytes(rng.randrange(256) for _ in range(7 * channels)) for _ in range(6)]
    assert checks.decode_png(_png(7, 6, rows, channels=channels, kinds=kinds)) == (7, 6, channels, rows)


def test_png_decoder_reads_the_chromium_png():
    width, height, channels, rows = checks.decode_png(saved(0, "png"))
    assert (width, height) == (400, 300)
    assert rows[0][:3] == b"\xff\xff\xff"  # Plotly's white paper in the top-left corner


def _chunks(data):
    pos, out = 8, []
    while pos < len(data):
        size = int.from_bytes(data[pos:pos + 4], "big")
        out.append((data[pos + 4:pos + 8], data[pos + 8:pos + 8 + size]))
        pos += size + 12
    return out


def _flip(data, tag):
    where = data.index(tag) + 6
    return data[:where] + bytes([data[where] ^ 1]) + data[where + 1:]


def _lying_size(data):
    chunks = _chunks(data)
    chunks[0] = (b"IHDR", struct.pack(">II", 401, 300) + chunks[0][1][8:])
    return checks.PNG_SIGNATURE + b"".join(_chunk(*c) for c in chunks)


def _drop_idat(data):
    return checks.PNG_SIGNATURE + b"".join(_chunk(*c) for c in _chunks(data) if c[0] != b"IDAT")


RED_MARKERS = lambda x, y: (255, 0, 0) if x % 90 < 12 and y % 90 < 12 else (x % 256, y % 256, 90)  # noqa: E731
NO_RED = lambda x, y: (x % 200 + 1, y % 200 + 1, 90)  # noqa: E731
PNG_REJECTED = {
    "no signature": (lambda d: b"x" + d[1:], "signature"),
    "truncated": (lambda d: d[:-5], "truncated"),
    "trailing bytes": (lambda d: d + b"x", "after IEND"),
    "bad crc": (lambda d: _flip(d, b"IDAT"), "CRC"),
    "size lies about the pixels": (_lying_size, "pixel data"),
    "no pixel data": (_drop_idat, "incomplete"),
    "other layout size": (lambda d: _png(200, 150, _picture(200, 150, RED_MARKERS)), "200x150"),
    "blank": (lambda d: _png(400, 300, _picture(400, 300, lambda x, y: (255, 255, 255))), "blank"),
    "marker colour missing": (lambda d: _png(400, 300, _picture(400, 300, NO_RED)), "marker colour"),
}


@pytest.mark.parametrize("case", sorted(PNG_REJECTED))
def test_png_check_rejects(case):
    corrupt, message = PNG_REJECTED[case]
    with pytest.raises(OutputMismatch, match=message):
        checks.check_png(corrupt(saved(0, "png")), FIGURES[0])


def test_png_check_accepts_a_synthetic_image_with_the_marker_colour():
    checks.check_png(_png(400, 300, _picture(400, 300, RED_MARKERS), kinds=(0, 1, 2, 3, 4)), FIGURES[0])


# --- SVG: what the check rejects -----------------------------------------------------------------

def _edit(data, change):
    ET.register_namespace("", SVG[1:-1])
    root = ET.fromstring(data)
    change(root)
    return ET.tostring(root)


def _with_class(root, name, tag="path"):
    return [e for e in root.iter(SVG + tag) if name in (e.get("class") or "").split()]


def _move(points, order):
    spots = [p.get("transform") for p in points]
    for point, source in zip(points, order):
        point.set("transform", spots[source])


def _set_attr(name, value):
    return lambda root: root.set(name, value)


def _text_of(cls, text):
    return lambda root: setattr(_with_class(root, cls, "text")[0], "text", text)


def _fill_red_as_blue(root):
    for point in _with_class(root, "point"):
        point.set("style", point.get("style").replace("rgb(255, 0, 0)", "rgb(0, 0, 255)"))


def _hide_title(root):
    for element in _with_class(root, "gtitle", "text"):
        element.set("class", "not-a-title")


def _drop_point(root):
    for parent in root.iter():
        for child in list(parent):
            if child.tag == SVG + "path" and "point" in (child.get("class") or "").split():
                parent.remove(child)
                return


def _rename_trace(root):
    for group in _with_class(root, "trace", "g"):
        group.set("class", "not-a-trace")


SVG_REJECTED = {
    "not xml": (lambda d: d[:-6], "well-formed"),
    "not an svg": (lambda d: b"<html xmlns='http://www.w3.org/1999/xhtml'/>", "SVG root"),
    "other width": (lambda d: _edit(d, _set_attr("width", "401")), "401x300"),
    "other height": (lambda d: _edit(d, _set_attr("height", "299")), "400x299"),
    "other title": (lambda d: _edit(d, _text_of("gtitle", "other title")), "title"),
    "title missing": (lambda d: _edit(d, _hide_title), "title"),
    "other legend": (lambda d: _edit(d, _text_of("legendtext", "other series")), "legend"),
    "no trace group": (lambda d: _edit(d, _rename_trace), "trace groups"),
    "point removed": (lambda d: _edit(d, _drop_point), "2 points"),
    "points swapped in x": (lambda d: _edit(d, lambda r: _move(_with_class(r, "point"), [1, 0, 2])), "x order"),
    "points reversed": (lambda d: _edit(d, lambda r: _move(_with_class(r, "point"), [2, 1, 0])), "x order"),
    "marker colour": (lambda d: _edit(d, _fill_red_as_blue), "filled"),
}


@pytest.mark.parametrize("case", sorted(SVG_REJECTED))
def test_svg_check_rejects(case):
    corrupt, message = SVG_REJECTED[case]
    with pytest.raises(OutputMismatch, match=message):
        checks.check_svg(corrupt(saved(0, "svg")), FIGURES[0])


def test_svg_check_rejects_a_flipped_y_axis():
    def flip_y(root):  # keep x order, reverse which point is higher
        points = _with_class(root, "point")
        spots = [p.get("transform") for p in points]
        xs = [s[s.index("(") + 1:s.index(",")] for s in spots]
        ys = [s[s.index(",") + 1:s.index(")")] for s in spots]
        for point, x, y in zip(points, xs, reversed(ys)):
            point.set("transform", "translate(%s,%s)" % (x, y))
    with pytest.raises(OutputMismatch, match="y order"):
        checks.check_svg(_edit(saved(0, "svg"), flip_y), FIGURES[0])


# --- the page the browser is given -----------------------------------------------------------------

@pytest.fixture
def page_of(tmp_path):
    library = tmp_path / "plotly.min.js"
    library.write_text("/* stand-in; the page is parsed, never run */", encoding="utf-8")
    config = replace(PLOTLY, local_scripts=(lambda: library,))
    return lambda figure: config.page(plotly_figure_content(figure))


@pytest.mark.parametrize("index", INDEXES)
def test_page_holds_the_library_then_the_div_then_the_exact_spec(page_of, index):
    checks.check_page(page_of(FIGURES[index]), FIGURES[index])


def test_page_keeps_markup_in_a_name_inert_and_equal(page_of):
    figure = json.loads(json.dumps(FIGURES[0]))
    figure["data"][0]["name"] = "</script><script>alert(1)</script> & <b>"
    page = page_of(figure)
    assert page.count("<script") == 3  # preamble config, the library, the spec: nothing injected
    checks.check_page(page, figure)


PAGE_REJECTED = {
    "no library": (lambda p: p.replace('<script src="', '<link rel="x" href="'), "library script"),
    "library twice": (lambda p: p.replace("<div", '<script src="file:///x/plotly.min.js"></script><div'), "library script"),
    "other library": (lambda p: p.replace("plotly.min.js", "other.js"), "library script"),
    "no div": (lambda p: p.replace("<div id=g></div>", ""), "order"),
    "other div id": (lambda p: p.replace("<div id=g>", "<div id=h>"), "order"),
    "spec before the div": (lambda p: p.replace("<div id=g></div>", "") + "<div id=g></div>", "order"),
    "other spec": (lambda p: p.replace("diagnostic-figure-0", "diagnostic-figure-9"), "differs"),
    "broken spec": (lambda p: p.replace('"data":', '"data" '), "JSON"),
}


@pytest.mark.parametrize("case", sorted(PAGE_REJECTED))
def test_page_check_rejects(page_of, case):
    corrupt, message = PAGE_REJECTED[case]
    with pytest.raises(OutputMismatch, match=message):
        checks.check_page(corrupt(page_of(FIGURES[0])), FIGURES[0])
