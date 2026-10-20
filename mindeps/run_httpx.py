#!/usr/bin/env python3
"""collect.py / verify.py / inning_pilot.py と同じ httpx.Client で PoliteFetcher を動かす（実験）。

    python mindeps/run_httpx.py --impl real out.json
    python mindeps/run_httpx.py --impl min  out.json   # httpx が入っていない環境

外のネットワークには出ない。127.0.0.1 の一時サーバーだけを使う。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "mindeps"), str(ROOT / "blueprobe"), str(ROOT / "queryu"),
                str(ROOT / "research" / "gpt-r001-score-allocation")]


def install_httpx_min() -> None:
    if importlib.util.find_spec("httpx") is not None:
        raise SystemExit("httpx が入っている。--impl min は httpx なしの環境で動かす")
    spec = importlib.util.spec_from_file_location("httpx", ROOT / "mindeps" / "httpx_min.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["httpx"] = module
    spec.loader.exec_module(module)


class _Handler(BaseHTTPRequestHandler):
    seen: list[str] = []

    def do_GET(self):
        type(self).seen.append(self.headers.get("User-Agent") or "")
        if self.path.startswith("/redir"):
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
            return
        if self.path.startswith("/missing"):
            self.send_response(404)
            self.send_header("ETag", '"no"')
            self.end_headers()
            self.wfile.write(b"missing")
            return
        if self.path.startswith("/err"):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"boom")
            return
        if self.headers.get("If-None-Match") == '"v1"':
            self.send_response(304)
            self.send_header("ETag", '"v1"')
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("ETag", '"v1"')
        self.send_header("Last-Modified", "Mon, 01 Jan 2024 00:00:00 GMT")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<p>ok</p>".encode())

    def log_message(self, fmt, *args):
        return None


def outcomes() -> dict:
    """collect.py の with httpx.Client(...) as client を、ローカル URL に対して実行する。"""
    import httpx
    from queryu import Cache, PoliteFetcher, UA

    # 研究スクリプトの import が、この Client で通ることを確かめる。main は npb.jp へ行くので呼ばない。
    import collect  # noqa: F401

    _Handler.seen = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        import tempfile
        cache = Cache(Path(tempfile.mkdtemp(prefix="httpx-min-")))
        # collect.py / verify.py / inning_pilot.py と同じ引数。
        with httpx.Client(headers={"User-Agent": UA}, timeout=45, follow_redirects=True) as client:
            fetcher = PoliteFetcher(cache, wait=0, client=client)
            pages = {
                "ok": fetcher.get("k", base + "/ok", "g"),
                "redir": fetcher.get("r", base + "/redir", "g"),
                "missing": fetcher.get("m", base + "/missing", "g"),
            }
            try:
                fetcher.get("e", base + "/err", "g")
                raised = None
            except Exception as exc:
                response = getattr(exc, "response", None)
                raised = getattr(response, "status_code", None)
            pages["conditional"] = fetcher.get("k", base + "/ok", "g", live=True)
        entry = cache.latest()["k"]
        return {
            "pages": pages,
            "requests": fetcher.requests,
            "error_status": raised,
            "etag": entry.get("etag"),
            "last_modified": entry.get("last_modified"),
            "user_agents": sorted(set(_Handler.seen)),
            "collect_imports": True,
        }
    finally:
        server.shutdown()
        thread.join(timeout=2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--impl", choices=["real", "min"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.impl == "min":
        install_httpx_min()
    elif importlib.util.find_spec("httpx") is None:
        raise SystemExit("httpx が無い。--impl real は httpx のある環境で動かす")
    result = outcomes()
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"httpx={args.impl} requests={result['requests']} error={result['error_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
