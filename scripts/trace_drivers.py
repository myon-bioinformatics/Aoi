#!/usr/bin/env python3
"""Real call paths for scripts/trace_surface.py.

Each driver is a function the study runs with a package blocked, stubbed, or
wrapped. They call project code (or, where that code cannot start without
extra inputs, the same operations the project file performs). They are not
part of a pipeline.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_overlap() -> None:
    """DRAgoWing load_overlap on the c001 season file."""
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
    from dragowing.overlap import default_conditions, load_overlap as overlap
    from dragowing.records import read_jsonl

    season = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
    props = ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"
    rows = read_jsonl(season)
    result = overlap(season, default_conditions(read_jsonl(props), rows))
    if not result["regions"] or sum(region["count"] for region in result["regions"]) != len(rows):
        raise SystemExit("load_overlap regions do not cover the rows")
    print(f"load_overlap rows={len(rows)} regions={len(result['regions'])}")


def suggest_index() -> None:
    """QueRyu ask/suggest.Index, which calls numpy.linalg.svd."""
    sys.path[:0] = [str(ROOT / "queryu" / "ask")]
    from suggest import Index

    docs = [
        ("P1", "得点順位が低い球団は失点順位も低いか"),
        ("P2", "ピタゴラス勝率との差が残るか"),
        ("E3", "順位が上がった年の得点"),
    ]
    found = Index(docs, dim=8)
    if found.P.shape[0] < 1:
        raise SystemExit("suggest index has no projection")
    print(f"suggest_index vocab={len(found.vocab)} rank={found.P.shape[1]}")


def littlebit_svd() -> None:
    """PythDRagoras littlebit_prune.littlebit: svd, lstsq, norm."""
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
    import numpy as np
    from littlebit_prune import littlebit

    matrix = np.array([[(i * 5 + j) / 40 for j in range(5)] for i in range(8)], dtype=float)
    parts = littlebit(matrix, rank=2, stages=1, als_iters=1)
    if not parts:
        raise SystemExit("littlebit returned no parts")
    print(f"littlebit parts={len(parts)}")


def selectolax_css() -> None:
    """The Lexbor calls BlueProbe's parity tests make: css, text, attributes, tag."""
    from selectolax.lexbor import LexborHTMLParser

    html = "<table><tbody><tr><td><a id='n' href='/x'>A</a></td></tr></tbody></table>"
    parser = LexborHTMLParser(html)
    nodes = list(parser.css("a"))
    if len(nodes) != 1:
        raise SystemExit(f"expected one anchor, got {len(nodes)}")
    node = nodes[0]
    href = (node.attributes or {}).get("href")
    text = node.text(deep=True)
    if href != "/x" or text != "A" or node.tag != "a":
        raise SystemExit(f"unexpected node {href!r} {text!r} {node.tag!r}")
    if len(parser.css("tr")) != 1 or len(parser.css("tbody")) != 1:
        raise SystemExit("row or body selector missed")
    print("selectolax_css ok")


def httpx_get() -> None:
    """PoliteFetcher.get with an httpx.Client, against a local response."""
    import tempfile
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    sys.path[:0] = [str(ROOT), str(ROOT / "queryu")]
    import httpx
    from queryu import Cache, PoliteFetcher

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("ETag", "abc")
            self.send_header("Last-Modified", "Mon, 01 Jan 2024 00:00:00 GMT")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            with httpx.Client(headers={"User-Agent": "aoi-trace"}, timeout=5, follow_redirects=True) as client:
                fetcher = PoliteFetcher(Cache(Path(tmp)), wait=0, client=client)
                body = fetcher.get("k", f"http://127.0.0.1:{port}/page", "g")
            if body != "ok" or fetcher.requests != 1:
                raise SystemExit(f"httpx_get failed: {body!r} requests={fetcher.requests}")
    finally:
        server.shutdown()
    print("httpx_get ok")


def render_md() -> None:
    """DRAgoWing render_md, which loads Python-Markdown through import_module."""
    sys.path[:0] = [str(ROOT)]
    from dragowing.htmlout import render_md as render

    html = render("| a | b |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n")
    if "<table>" not in html or "<pre><code>" not in html:
        raise SystemExit("render_md did not render the table and code")
    print(f"render_md chars={len(html)}")


def ortools_import() -> None:
    """The optional exact solver imported inside sakanalytics.season_exact.solve."""
    import ortools
    from ortools.sat.python import cp_model

    if not hasattr(cp_model, "CpModel"):
        raise SystemExit("cp_model.CpModel is missing")
    print(f"ortools {ortools.__version__}")


def pandas_surface() -> None:
    """Operations from research/.../verify_prediction_independent.py, without its files.

    That script parses arguments and reads a season file at import time, so the
    trace runs the same method chain on a tiny frame instead of executing it.
    """
    import pandas as pd

    frame = pd.DataFrame({
        "season": [2013, 2013, 2014],
        "league": ["c", "c", "c"],
        "team": ["d", "g", "d"],
        "bat_iso": [0.1, 0.2, 0.15],
        "bat_obp": [0.3, 0.4, 0.35],
        "inn_R": [10.0, 12.0, 11.0],
        "inn_S": [20.0, 18.0, 19.0],
    })
    frame = frame[frame.season >= 2013].copy()
    grouped = frame.groupby(["season", "league"])
    size = grouped.team.transform("size")
    frame["iso"] = frame.bat_iso - (grouped.bat_iso.transform("sum") - frame.bat_iso) / (size - 1)
    values = frame.team.to_numpy()
    row = frame.iloc[0]
    if len(values) != 3 or row.team != "d":
        raise SystemExit("pandas_surface drifted from the research script's operations")
    print(f"pandas_surface rows={len(frame)}")


DRIVERS = {
    "load_overlap": load_overlap,
    "suggest_index": suggest_index,
    "littlebit_svd": littlebit_svd,
    "selectolax_css": selectolax_css,
    "httpx_get": httpx_get,
    "render_md": render_md,
    "ortools_import": ortools_import,
    "pandas_surface": pandas_surface,
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1 or argv[0] not in DRIVERS:
        names = ", ".join(sorted(DRIVERS))
        raise SystemExit(f"usage: trace_drivers.py <{'|'.join(sorted(DRIVERS))}>\nknown: {names}")
    DRIVERS[argv[0]]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
