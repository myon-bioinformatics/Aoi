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



def _cache_core(queryu):
    """QueRyu の cache_core.py（core/ にある。前の配置では直下）。"""
    return next(p for p in (Path(queryu) / "core" / "cache_core.py", Path(queryu) / "cache_core.py") if p.is_file())

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
            # This test deliberately has no QueRyu component (-I ignores PYTHONPATH). BlueProbe does not
            # look for it; the caller (Aoi's aoi.py) supplies the path.
            result = subprocess.run([sys.executable, "-I", str(script), "http://127.0.0.1:1/", "--cache", str(Path(tmp) / "cache")],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("cache_core.py", result.stderr)
            self.assertIn("aoi.py", result.stderr)
            self.assertFalse((Path(tmp) / "cache").exists())

    def test_source_cache_without_queryu_names_aoi_py(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in ROOT.glob("*.py"):
                shutil.copy2(path, Path(tmp) / path.name)
            cache = Path(tmp) / "cache"
            cache.mkdir()
            (cache / "manifest.jsonl").write_text("", encoding="utf-8")
            result = subprocess.run([sys.executable, "-I", str(Path(tmp) / "blueprobe.py"), "--source", "html_source",
                                     "--cache", str(cache)], cwd=tmp, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("aoi.py", result.stderr)

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
            shutil.copy2(_cache_core(queryu), root / "cache_core.py")
            cache, url = root / "cache", f"http://127.0.0.1:{server.server_port}/"
            result = subprocess.run([sys.executable, "-I", str(root / "blueprobe.py"), url, "--cache", str(cache)],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = json.loads((cache / "manifest.jsonl").read_text())
            self.assertEqual(entry["url"], url)
            self.assertEqual(entry["sha256"], json.loads(result.stdout)["sha256"])
            self.assertTrue((cache / entry["file"]).is_file())

    def test_generated_cache_can_be_reused_offline_by_queryu(self):
        queryu = os.environ.get("QUERYU_ROOT")
        if not queryu:
            self.skipTest("set QUERYU_ROOT to a QueRyu checkout")
        import importlib.util
        spec = importlib.util.spec_from_file_location('review_cache_core', _cache_core(queryu))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy2(ROOT / "blueprobe.py", root / "blueprobe.py")
            shutil.copy2(_cache_core(queryu), root / "cache_core.py")
            cache, url = root / "cache", f"http://127.0.0.1:{server.server_port}/"
            try:
                result = subprocess.run([sys.executable, '-I', str(root / 'blueprobe.py'), url, '--cache', str(cache)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
            finally:
                server.shutdown()
            store = module.Cache(cache)
            entry = store.latest()[url]
            saved = store.snapshot(entry)
            from blueprobe import classify_document
            self.assertEqual(saved['response_sha256'], json.loads(result.stdout)['sha256'])
            self.assertEqual(classify_document(saved['html']), json.loads(result.stdout)['classification'])
            self.assertIsNone(entry['etag'])
            self.assertIsNone(entry['last_modified'])
            # Reuse verifies integrity, rather than accepting a damaged body.
            (cache / entry['file']).write_bytes(b'broken gzip')
            with self.assertRaises(module.CacheIntegrityError):
                store.snapshot(entry)
