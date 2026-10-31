"""Browser-free checks of drawn Plotly output against the figure spec that was drawn.

Nothing here starts a browser, runs JavaScript or touches the network (standard library only).
It reads what the browser-based export produces (the page it was given, the SVG, the PNG) and
compares it with the spec by equality conditions, so a failure in the browser tests can be told
apart from a failure in the output itself:

* ``check_page``  the HTML given to the browser: library script before ``div#g`` before the
  inline script, and the JSON spec in that script equal to the figure.
* ``check_svg``   the SVG: size, one trace group per trace, title, legend, one point per x value,
  marker colour, and point order following the data (x increases to the right, y upwards).
* ``check_png``   the PNG: a valid 8-bit RGB/RGBA image of the layout size whose pixels contain
  each trace's marker colour.

``decode_png`` is the decoder the PNG check uses (all five row filters, CRC and size checks).
Every check raises ``OutputMismatch`` with a message that names what differs.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
import zlib
from html.parser import HTMLParser

__all__ = ["OutputMismatch", "check_page", "check_png", "check_svg", "decode_png", "figures_digest"]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SVG_NS = "{http://www.w3.org/2000/svg}"
NAMED_COLOURS = {"red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 128, 0)}
MIN_MARKER_PIXELS = 50  # a size-12 marker is about 110 pixels; three of them are ~300


class OutputMismatch(ValueError):
    """The drawn output differs from the spec (or is not a valid file of its kind)."""


def figures_digest(figures) -> str:
    """Stable digest of figure specs, used to tie saved output to the spec it was drawn from."""
    text = json.dumps(figures, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _marker_rgb(trace) -> tuple[int, int, int] | None:
    colour = (trace.get("marker") or {}).get("color")
    return NAMED_COLOURS[colour] if isinstance(colour, str) and colour in NAMED_COLOURS else None


def _sign(value) -> int:
    return (value > 0) - (value < 0)


# --- PNG -------------------------------------------------------------------------------------

def decode_png(data: bytes) -> tuple[int, int, int, list[bytes]]:
    """Return ``(width, height, channels, rows)`` for an 8-bit, non-interlaced RGB/RGBA PNG."""
    if data[:8] != PNG_SIGNATURE:
        raise OutputMismatch("PNG has no valid signature")
    pos, header, compressed, ended = 8, None, [], False
    while pos < len(data):
        if ended:
            raise OutputMismatch("PNG has data after IEND")
        if pos + 12 > len(data):
            raise OutputMismatch("PNG has a truncated chunk")
        length = int.from_bytes(data[pos:pos + 4], "big")
        end = pos + length + 12
        if end > len(data):
            raise OutputMismatch("PNG has a truncated chunk")
        tag, body = data[pos + 4:pos + 8], data[pos + 8:end - 4]
        if zlib.crc32(tag + body) != int.from_bytes(data[end - 4:end], "big"):
            raise OutputMismatch("PNG has an invalid chunk CRC")
        if header is None and tag != b"IHDR":
            raise OutputMismatch("PNG does not start with IHDR")
        if tag == b"IHDR":
            if len(body) != 13:
                raise OutputMismatch("PNG has an invalid IHDR")
            header = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            compressed.append(body)
        elif tag == b"IEND":
            if length:
                raise OutputMismatch("PNG has an invalid IEND")
            ended = True
        pos = end
    if header is None or not ended or not compressed:
        raise OutputMismatch("PNG is incomplete")
    width, height, depth, colour, method, filtering, interlace = header
    if width < 1 or height < 1 or depth != 8 or colour not in (2, 6) or (method, filtering, interlace) != (0, 0, 0):
        raise OutputMismatch("PNG uses an unexpected pixel format")
    channels = 3 if colour == 2 else 4
    stride = width * channels
    expected = (stride + 1) * height
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(b"".join(compressed), expected + 1)
    except zlib.error as exc:
        raise OutputMismatch("PNG pixel data cannot be decompressed: %s" % exc) from exc
    if len(raw) != expected or not inflater.eof or inflater.unused_data:
        raise OutputMismatch("PNG has incomplete or oversized pixel data")
    rows, previous = [], bytearray(stride)
    for y in range(height):
        kind = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if kind == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 255
        elif kind == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 255
        elif kind == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + (left + previous[i]) // 2) & 255
        elif kind == 4:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                corner = previous[i - channels] if i >= channels else 0
                up = previous[i]
                estimate = left + up - corner
                da, db, dc = abs(estimate - left), abs(estimate - up), abs(estimate - corner)
                predictor = left if da <= db and da <= dc else up if db <= dc else corner
                line[i] = (line[i] + predictor) & 255
        elif kind != 0:
            raise OutputMismatch("PNG row %d uses unknown filter %d" % (y, kind))
        rows.append(bytes(line))
        previous = line
    return width, height, channels, rows


def _count_colour(rows, channels, rgb) -> int:
    wanted = bytes(rgb)
    return sum(1 for row in rows for i in range(0, len(row), channels) if row[i:i + 3] == wanted)


def check_png(data: bytes, figure: dict) -> None:
    """The PNG is a valid image of the layout size and shows each trace's marker colour."""
    width, height, channels, rows = decode_png(data)
    layout = figure["layout"]
    if (width, height) != (layout["width"], layout["height"]):
        raise OutputMismatch("PNG is %dx%d, the layout says %dx%d" % (width, height, layout["width"], layout["height"]))
    if len({row[i:i + 3] for row in rows for i in range(0, len(row), channels)}) < 4:
        raise OutputMismatch("PNG is blank or nearly one colour")
    for trace in figure["data"]:
        rgb = _marker_rgb(trace)
        if rgb is not None and _count_colour(rows, channels, rgb) < MIN_MARKER_PIXELS:
            raise OutputMismatch("PNG does not show the marker colour %s of trace %r" % (rgb, trace.get("name")))


# --- SVG -------------------------------------------------------------------------------------

def _classes(element) -> set[str]:
    return set((element.get("class") or "").split())


def _text(element) -> str:
    return "".join(element.itertext())


_TRANSLATE = re.compile(r"translate\(\s*(-?[0-9.]+(?:e-?\d+)?)\s*[, ]\s*(-?[0-9.]+(?:e-?\d+)?)\s*\)")
_FILL = re.compile(r"fill:\s*rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def svg_facts(data: bytes) -> dict:
    """What the SVG draws: size, traces with their points, title and legend texts."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise OutputMismatch("SVG is not well-formed XML: %s" % exc) from exc
    if root.tag != SVG_NS + "svg":
        raise OutputMismatch("SVG has no SVG root")
    traces = []
    for element in root.iter(SVG_NS + "g"):
        if "trace" in _classes(element):
            points = []
            for point in element.iter(SVG_NS + "path"):
                if "point" in _classes(point):
                    at, fill = _TRANSLATE.search(point.get("transform") or ""), _FILL.search(point.get("style") or "")
                    points.append({"x": float(at.group(1)) if at else None, "y": float(at.group(2)) if at else None,
                                   "fill": tuple(int(v) for v in fill.groups()) if fill else None})
            traces.append(points)
    texts = lambda name: [_text(e) for e in root.iter(SVG_NS + "text") if name in _classes(e)]  # noqa: E731
    return {"width": root.get("width"), "height": root.get("height"), "traces": traces,
            "title": texts("gtitle"), "legend": texts("legendtext")}


def check_svg(data: bytes, figure: dict) -> None:
    """The SVG draws exactly this figure: size, title, legend, points, marker colours, point order."""
    facts, layout = svg_facts(data), figure["layout"]
    if (facts["width"], facts["height"]) != (str(layout["width"]), str(layout["height"])):
        raise OutputMismatch("SVG is %sx%s, the layout says %sx%s" % (facts["width"], facts["height"],
                                                                      layout["width"], layout["height"]))
    if facts["title"] != [layout["title"]["text"]]:
        raise OutputMismatch("SVG title %r differs from %r" % (facts["title"], layout["title"]["text"]))
    names = [trace["name"] for trace in figure["data"]]
    if facts["legend"] != names:
        raise OutputMismatch("SVG legend %r differs from the trace names %r" % (facts["legend"], names))
    if len(facts["traces"]) != len(figure["data"]):
        raise OutputMismatch("SVG has %d trace groups for %d traces" % (len(facts["traces"]), len(figure["data"])))
    for trace, points in zip(figure["data"], facts["traces"]):
        label = trace.get("name")
        if len(points) != len(trace["x"]):
            raise OutputMismatch("trace %r has %d points in the SVG for %d values" % (label, len(points), len(trace["x"])))
        if any(p["x"] is None or p["fill"] is None for p in points):
            raise OutputMismatch("trace %r has a point without a position or fill" % label)
        rgb = _marker_rgb(trace)
        if rgb is not None and any(p["fill"] != rgb for p in points):
            raise OutputMismatch("trace %r markers are not filled %s" % (label, rgb))
        for a in range(len(points) - 1):
            dx, dy = trace["x"][a + 1] - trace["x"][a], trace["y"][a + 1] - trace["y"][a]
            if _sign(dx) != _sign(points[a + 1]["x"] - points[a]["x"]):
                raise OutputMismatch("trace %r: points %d and %d are not in x order" % (label, a, a + 1))
            if _sign(dy) != -_sign(points[a + 1]["y"] - points[a]["y"]):  # SVG y grows downwards
                raise OutputMismatch("trace %r: points %d and %d are not in y order" % (label, a, a + 1))


# --- the page given to the browser -------------------------------------------------------------

class _Events(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.events: list[tuple[str, str]] = []
        self._inline = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            if attrs.get("src"):
                self.events.append(("script-src", attrs["src"]))
            else:
                self._inline = []
        elif tag == "div" and attrs.get("id"):
            self.events.append(("div", attrs["id"]))

    def handle_data(self, data):
        if self._inline is not None:
            self._inline.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._inline is not None:
            self.events.append(("script-inline", "".join(self._inline)))
            self._inline = None


_SPEC_CALL = re.compile(r"const spec=(.*);return Plotly\.newPlot\('g',spec\.data,spec\.layout,", re.S)


def check_page(html: str, figure: dict, library: str = "plotly.min.js") -> None:
    """The page equals what the browser needs: library, then ``div#g``, then the spec script."""
    parser = _Events()
    parser.feed(html)
    parser.close()
    sources = [value for kind, value in parser.events if kind == "script-src"]
    if len(sources) != 1 or not sources[0].endswith("/" + library):
        raise OutputMismatch("expected one library script ending in %s, found %r" % (library, sources))
    order, calls = [], []
    for kind, value in parser.events:
        if kind == "script-src":
            order.append("library")
        elif kind == "div" and value == "g":
            order.append("div#g")
        elif kind == "script-inline" and _SPEC_CALL.search(value):
            order.append("spec script")
            calls.append(_SPEC_CALL.search(value).group(1))
    if order != ["library", "div#g", "spec script"]:
        raise OutputMismatch("expected library, div#g, spec script in that order, found %r" % order)
    try:
        spec = json.loads(calls[0])
    except ValueError as exc:
        raise OutputMismatch("the spec in the page is not valid JSON: %s" % exc) from exc
    if spec != figure:
        raise OutputMismatch("the spec in the page differs from the figure")
