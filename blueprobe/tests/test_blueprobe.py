"""🧱 blueprobe.py: normalization, the report contract, offline reparsing and the main CLI.

- core: 取得元に依存しない部分: 正規化、報告の契約、オフライン再解析。
- cli: --list-patterns / --pattern / --source + --cache are checked before any source or cache is touched.
- url: `python blueprobe.py URL [--cache DIR]` against a local HTTP server (curl); QueRyu cache cases need QUERYU_ROOT.
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import Mock

import pytest

import blueprobe
import npb_calendar
from blueprobe import inspect, load_source, mask_digits, normalize, to_markdown


# ──── core ────────────────────────────────────────────────────────

P = "/bis/2024/games/s2024040201097.html"


@pytest.mark.parametrize("text,expected", [
    ("", ""), (" ", ""), ("\n", ""), ("a\r\nb", "a b"), ("a b", "a b"), ("a　b", "a b"),
    ("４", "4"), ("\x00", "�"), ("日本語🙂", "日本語🙂"), ("ﾔ", "ヤ"),
])
def test_normalize_matrix(text, expected):
    assert normalize(text) == expected


def test_normalize_is_idempotent():
    for s in ["中 ４　-　3 巨", "\x00x", " a  b "]:
        assert normalize(normalize(s)) == normalize(s)


@pytest.mark.parametrize("name", ["", "../x", "Npb", "a-b", "a b"])
def test_load_source_rejects_odd_names(name):
    with pytest.raises(ValueError):
        load_source(name)


def test_mask_digits():
    assert mask_digits("中 4x - 3 巨 ４") == "中 #x - # 巨 #"


def test_inspect_groups_counts_and_unknown_shapes():
    pages = [
        ("2024_03", "u", "2024", ""),  # 存在しない月（空）
        ("2024_04", "u", "2024", f'<a href="{P}">中 4 - 3 巨</a><a href="/cs/">神 1 - 3 デ</a>'),
        ("2024_05", "u", "2024", f'<a href="{P.replace("1097", "1200")}">中 4x - 3 巨</a>'),
    ]
    rows = inspect(npb_calendar, pages)
    assert rows == [{"group": "2024", "pages": 2, "empty_pages": 1, "records": 1,
                     "n_non_regular": 1, "unknown": 1, "unknown_shapes": ["中 #x - # 巨"]}]
    md = to_markdown(rows, "t")
    assert "中 #x - # 巨" in md and "中 4x" not in md  # 生の得点は docs に残さない


def test_inspect_can_hand_back_records_and_markdown_shows_checks():
    recs = []
    inspect(npb_calendar, [("2024_04", "u", "2024", f'<a href="{P}">中 4 - 3 巨</a>')], recs)
    assert [r["key"] for r in recs] == ["2024040201097"]
    checks = npb_calendar.check(recs)
    assert [(c["group"], c["ok"]) for c in checks] == [("2024", False)]
    assert "取りこぼしの確認" in to_markdown([], "t", checks)


# ──── cli ─────────────────────────────────────────────────────────

def test_list_patterns_needs_no_cache_or_queryu(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, 'queryu', None)
    load = Mock(side_effect=AssertionError('must not load a source'))
    monkeypatch.setattr(blueprobe, 'load_source', load)
    assert blueprobe.main(['--list-patterns']) == 0
    output = capsys.readouterr()
    assert output.err == ''
    for pattern in blueprobe.list_patterns():
        assert pattern['key'] in output.out
        assert pattern['selector'] in output.out
    load.assert_not_called()


@pytest.mark.parametrize('pattern,message', [
    ('invalid_pattern_xyz', "unknown pattern key 'invalid_pattern_xyz'"),
    ('', 'must be a non-empty string'),
    ('   ', 'must be a non-empty string'),
])
def test_invalid_pattern_is_cli_error_before_cache_access(pattern, message, tmp_path, capsys):
    output = tmp_path / 'report.md'
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(['--source', 'html_source', '--pattern', pattern,
                        '--cache', str(tmp_path / 'missing'), '--out', str(output)])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '--pattern:' in captured.err
    assert message in captured.err
    assert '--list-patterns' in captured.err
    assert 'Traceback' not in captured.err
    assert 'no cache manifest' not in captured.err
    assert not output.exists()


@pytest.mark.parametrize('pattern', ['github_readme', 'invalid_pattern_xyz', ''])
@pytest.mark.parametrize('source', ['npb_calendar', 'does_not_exist'])
def test_pattern_rejects_other_sources_before_loading(source, pattern, tmp_path, monkeypatch, capsys):
    load = Mock(side_effect=AssertionError('must validate before source import'))
    monkeypatch.setattr(blueprobe, 'load_source', load)
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(['--source', source, '--pattern', pattern, '--cache', str(tmp_path)])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '--pattern requires --source html_source' in captured.err
    load.assert_not_called()


@pytest.mark.parametrize('args', [[], ['--source', 'html_source'], ['--cache', 'missing']])
def test_reanalysis_still_requires_source_and_cache(args, capsys):
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(args)
    assert exc.value.code == 2
    assert '--source and --cache are required' in capsys.readouterr().err


def test_listing_cannot_silently_ignore_pattern(capsys):
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(['--list-patterns', '--pattern', 'github_readme'])
    assert exc.value.code == 2
    assert 'not allowed with argument' in capsys.readouterr().err


# ──── url ─────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]
_cli_spec = importlib.util.spec_from_file_location("blueprobe_cli_args", ROOT / "vendor/cli_args.py")
_cli_args = importlib.util.module_from_spec(_cli_spec)
sys.modules[_cli_spec.name] = _cli_args
_cli_spec.loader.exec_module(_cli_args)


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
            result = _cli_args.run_cli(script, url, "--out", str(out), python_options=("-I",), timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = result.json()
            self.assertEqual(report["url"], url)
            self.assertGreater(report["classification"]["landmarks"].get("main", 0), 0)
            self.assertEqual(json.loads(out.read_text()), report)
            missing = _cli_args.run_cli(script, url + "missing", python_options=("-I",), timeout=10)
            self.assertNotEqual(missing.returncode, 0)

    def test_the_single_file_is_the_uv_tool(self):
        # 🧰 ルートの pyproject がそのまま uv tool（uv tool install .）。入るのは blueprobe.py 1 ファイルだけ（PythDRagoras #54 に倣う）
        import tomllib
        config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project = config["project"]
        self.assertEqual((project["dependencies"], project["scripts"]), ([], {"blueprobe": "blueprobe:main"}))
        self.assertEqual((project["requires-python"], config["tool"]["setuptools"]["py-modules"]), (">=3.11", ["blueprobe"]))

    def test_cache_requires_component_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "blueprobe.py"
            shutil.copy2(ROOT / "blueprobe.py", script)
            # This test deliberately has no QueRyu component (-I ignores PYTHONPATH). BlueProbe does not
            # look for it; the caller (Aoi's aoi.py) supplies the path.
            result = _cli_args.run_cli(script, "http://127.0.0.1:1/", "--cache", str(Path(tmp) / "cache"),
                                       python_options=("-I",), timeout=10)
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
            result = _cli_args.run_cli(Path(tmp) / "blueprobe.py", "--source", "html_source", "--cache", str(cache),
                                       python_options=("-I",), cwd=tmp, timeout=10)
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
            result = _cli_args.run_cli(root / "blueprobe.py", url, "--cache", str(cache),
                                       python_options=("-I",), timeout=10)
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
                result = _cli_args.run_cli(root / 'blueprobe.py', url, '--cache', str(cache),
                                           python_options=('-I',), timeout=10)
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
