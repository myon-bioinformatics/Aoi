import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/missing":
            self.send_error(404)
            return
        body = b"<!doctype html><html><body><main><h1>Hello</h1></main></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("curl"), "curl unavailable")
class UrlStandaloneTest(unittest.TestCase):
    def test_url_and_missing_page(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "blueprobe.py"
            shutil.copy2(ROOT / "blueprobe.py", script)
            url = f"http://127.0.0.1:{server.server_port}/"
            out = Path(tmp) / "result.json"
            result = subprocess.run([sys.executable, "-I", str(script), url, "--out", str(out)],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["url"], url)
            self.assertGreater(report["classification"]["landmarks"].get("main", 0), 0)
            self.assertEqual(json.loads(out.read_text()), report)
            missing = subprocess.run([sys.executable, "-I", str(script), url + "missing"],
                                     capture_output=True, text=True, timeout=10)
            self.assertNotEqual(missing.returncode, 0)

    def test_cache_requires_component_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "blueprobe.py"
            shutil.copy2(ROOT / "blueprobe.py", script)
            result = subprocess.run([sys.executable, "-I", str(script), "http://127.0.0.1:1/", "--cache", str(Path(tmp) / "cache")],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("cache_core.py", result.stderr)
            self.assertFalse((Path(tmp) / "cache").exists())

    def test_cache_with_queryu_component(self):
        queryu = os.environ.get("QUERYU_ROOT")
        if not queryu:
            self.skipTest("set QUERYU_ROOT to a QueRyu checkout")
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy2(ROOT / "blueprobe.py", root / "blueprobe.py")
            shutil.copy2(Path(queryu) / "cache_core.py", root / "cache_core.py")
            cache, url = root / "cache", f"http://127.0.0.1:{server.server_port}/"
            result = subprocess.run([sys.executable, "-I", str(root / "blueprobe.py"), url, "--cache", str(cache)],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads((cache / "manifest.jsonl").read_text())
            self.assertEqual(entry["url"], url)
            self.assertEqual(entry["sha256"], json.loads(result.stdout)["sha256"])
            self.assertTrue((cache / entry["file"]).is_file())
