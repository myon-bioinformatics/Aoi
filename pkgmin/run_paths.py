#!/usr/bin/env python3
"""Run real Aoi entry points and write one JSON document.

These are project functions, not a synthetic requests/tqdm/Bio demo:

- NagoyAction ``show`` and ``doctor`` on the c001 pipeline
- BlueProbe ``classify_document`` on the hand-written fixtures its tests use
- QueRyu ``acquisition_plan`` and ``UrllibClient.get`` against 127.0.0.1
- Import of the R001 research modules (their ``main`` hits the network; not called)

``--inject min`` loads the stdlib stand-ins as ``requests``, ``tqdm``, and
``Bio`` before those imports. Nothing in the paths above imports those names,
so the JSON matches a run that can see the real packages.

    python pkgmin/run_paths.py --inject none out.json
    python pkgmin/run_paths.py --inject min  out.json
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN = {
    "requests": "requests_min.py",
    "tqdm": "tqdm_min.py",
    "Bio": "biopython_min.py",
}

# The same fragments blueprobe/tests/test_blueprobe_dom_classification.py classifies.
FIXTURES = {
    "social": "<main><div role=\"feed\"><article><p>first post body text</p></article></div></main>",
    "product": "<div itemscope itemtype=\"https://schema.org/Product\"><h1 itemprop=\"name\">Blue Mug</h1></div>",
    "forum": "<div itemscope itemtype=\"https://schema.org/QAPage\"><h1 itemprop=\"name\">How?</h1></div>",
    "plain": "<p>hi</p>",
}


def install_min() -> None:
    for name, filename in MIN.items():
        existing = sys.modules.get(name)
        path = ROOT / "pkgmin" / filename
        if existing is not None and Path(getattr(existing, "__file__", "") or "").resolve() != path.resolve():
            raise SystemExit(f"{name} is already imported from {getattr(existing, '__file__', None)}")
        spec = importlib.util.spec_from_file_location(name, path, submodule_search_locations=[])
        if spec is None or spec.loader is None:
            raise SystemExit(f"cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)


def _paths() -> None:
    sys.path[:0] = [
        str(ROOT / "nagoyaction"),
        str(ROOT / "blueprobe"),
        str(ROOT / "queryu"),
        str(ROOT / "research" / "gpt-r001-score-allocation"),
        str(ROOT),
    ]


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return None


def _urllib_get() -> dict:
    import urllib.request

    from queryu import UrllibClient

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        client = UrllibClient(headers={"User-Agent": "pkgmin-paths"}, timeout=5, opener=opener)
        response = client.get(f"http://127.0.0.1:{server.server_port}/ok")
        return {
            "body": response.content.decode("utf-8"),
            "content_type": response.headers.get("Content-Type"),
            "status": response.status_code,
        }
    finally:
        server.shutdown()
        thread.join(timeout=2)


def _try_import(name: str) -> dict:
    try:
        importlib.import_module(name)
    except Exception as exc:
        return {"error": type(exc).__name__, "module": name}
    return {"error": None, "module": name}


def build() -> dict:
    import datetime as dt

    import blueprobe
    import nagoyaction as na
    from queryu import Cache, acquisition_plan

    pipeline = na.load(ROOT / "cycles" / "c001-chunichi" / "pipeline.toml")
    shown = json.loads(na.show(pipeline, json_output=True))
    shown["root"] = str(Path(shown["root"]).resolve().relative_to(ROOT))
    checks = na.doctor(pipeline, offline=True, which=lambda _tool: None)
    # An empty directory: do not read or write the real NPB cache.
    cache = Cache(Path(tempfile.mkdtemp(prefix="pkgmin-cache-")), source_version="pkgmin")
    plan = acquisition_plan(
        [("k", "https://example.invalid/a", "g")],
        cache,
        live=set(),
        wait=3,
        today=dt.date(2012, 3, 30),
        frozen=set(),
        future=[],
        offline=False,
    )
    classified = []
    for key, html in FIXTURES.items():
        result = blueprobe.classify_document(html)
        top = result["patterns"][0]["pattern"]["key"] if result["patterns"] else None
        classified.append({"fixture": key, "status": result["status"], "top": top, "tables": len(result["tables"])})
    return {
        "acquisition_plan": plan,
        "classify": classified,
        "doctor": checks,
        "imports": [_try_import(name) for name in ("collect", "verify", "observe", "inning_pilot")],
        "pipeline": shown,
        "urllib_get": _urllib_get(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inject", choices=["none", "min"], required=True)
    parser.add_argument("out", type=Path)
    args = parser.parse_args(argv)
    _paths()
    if args.inject == "min":
        install_min()
    payload = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
