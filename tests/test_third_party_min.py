"""selectolax_min / httpx_min / coverage の pure wheel を、本物のパッケージと比べる。"""
import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "mindeps"), str(ROOT / "scripts"), str(ROOT / "blueprobe"), str(ROOT / "queryu")]

import run_httpx  # noqa: E402
import run_selectolax  # noqa: E402
import trace_third_party as trace  # noqa: E402

selectolax_lexbor = pytest.importorskip("selectolax.lexbor")
httpx = pytest.importorskip("httpx")


def test_ast_surface_is_the_calls_the_mins_implement():
    found = trace.survey()
    assert set(found["imports"]) >= {"selectolax", "httpx", "pandas", "polars", "numpy", "pytest", "coverage"}
    assert found["attrs"]["selectolax"]["call LexborHTMLParser()"] >= 1
    assert "Client" in found["attrs"]["httpx"]
    assert any("markdown" in item for item in found["dynamic"])
    absent = trace.absent_traces()
    assert "selectolax" in absent["selectolax:research/gpt-r001-score-allocation/observe.py"]
    assert "httpx" in absent["httpx:research/gpt-r001-score-allocation/collect.py"]
    # inning_pilot は httpx を main() の中でだけ import する。
    assert absent["httpx:research/gpt-r001-score-allocation/inning_pilot.py"] == "imported"


def test_selectolax_min_matches_real_research_functions():
    real = run_selectolax.outcomes()
    run_selectolax.use_min_parser()
    minimal = run_selectolax.outcomes()
    assert minimal == real


def test_html5_recovery_is_not_the_same_as_lexbor():
    """html.parser では再現できない。selectolax_min を全称の互換にはしない。"""
    from selectolax.lexbor import LexborHTMLParser as Real

    from selectolax_min import LexborHTMLParser as Mini

    missing_row = "<table><td>cell</td></table>"
    assert [node.text() for node in Real(missing_row).css("tr")] == ["cell"]
    assert Mini(missing_row).css("tr") == []

    implied = "<table><tr><td>A</td></tr></table>"
    assert len(Real(implied).css("tbody")) == 1
    assert Mini(implied).css("tbody") == []

    nested = '<a href="1">A<a href="2">B</a></a>'
    real_links = [(node.attributes.get("href"), node.text()) for node in Real(nested).css("a")]
    mini_links = [(node.attributes.get("href"), node.text()) for node in Mini(nested).css("a")]
    assert real_links == [("1", "A"), ("2", "B")]
    assert mini_links == [("1", "AB"), ("2", "B")]

    template = "<template><main id='hidden'>H</main></template><main id='shown'>S</main>"
    assert [node.attributes.get("id") for node in Real(template).css("main")] == ["shown"]
    assert [node.attributes.get("id") for node in Mini(template).css("main")] == ["hidden", "shown"]


def test_httpx_min_matches_real_client_on_the_fetcher():
    real_httpx = httpx.Client
    try:
        real = run_httpx.outcomes()
        httpx.Client = __import__("httpx_min").Client
        # outcomes() は関数内で import httpx する。sys.modules のクラスを差し替える。
        sys.modules["httpx"].Client = httpx.Client
        minimal = run_httpx.outcomes()
    finally:
        sys.modules["httpx"].Client = real_httpx
        httpx.Client = real_httpx
    assert minimal == real
    assert real["pages"]["ok"] == "<p>ok</p>"
    assert real["pages"]["redir"] == "<p>ok</p>"
    assert real["pages"]["missing"] == ""
    assert real["pages"]["conditional"] == "<p>ok</p>"
    assert real["error_status"] == 500
    assert real["requests"] == 5
    assert real["etag"] == '"v1"'
    assert real["last_modified"] == "Mon, 01 Jan 2024 00:00:00 GMT"


def test_httpx_min_follow_redirects_false_returns_the_redirect():
    import httpx_min
    from run_httpx import _Handler

    server = run_httpx.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = run_httpx.threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/redir"
        with httpx.Client(timeout=5, follow_redirects=False) as real:
            real_response = real.get(url)
        with httpx_min.Client(timeout=5, follow_redirects=False) as minimal:
            mini_response = minimal.get(url)
        assert real_response.status_code == mini_response.status_code == 302
        with pytest.raises(httpx.HTTPStatusError):
            real_response.raise_for_status()
        with pytest.raises(httpx_min.HTTPStatusError):
            mini_response.raise_for_status()
    finally:
        server.shutdown()
        thread.join(timeout=2)


def test_min_cli_refuses_when_the_real_package_is_installed(tmp_path):
    for script, impl in (("run_selectolax.py", "min"), ("run_httpx.py", "min")):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "mindeps" / script), "--impl", impl, str(tmp_path / "out.json")],
            capture_output=True, text=True,
        )
        assert proc.returncode != 0, proc.stdout + proc.stderr


def test_client_call_shape_is_shared_by_the_research_scripts():
    """実行している Client(...) が、3本の研究スクリプトの呼び出しと同じである。"""
    expected = {"headers", "timeout", "follow_redirects"}
    for rel in (
        "research/gpt-r001-score-allocation/collect.py",
        "research/gpt-r001-score-allocation/verify.py",
        "research/gpt-r001-score-allocation/inning_pilot.py",
    ):
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        calls = []
        for node in ast.walk(tree):
            func = getattr(node, "func", None)
            if not isinstance(node, ast.Call) or not isinstance(func, ast.Attribute) or func.attr != "Client":
                continue
            if not isinstance(func.value, ast.Name) or func.value.id != "httpx":
                continue
            keys = {kw.arg for kw in node.keywords}
            constants = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords if kw.arg != "headers"}
            calls.append((keys, constants))
        assert calls == [(expected, {"timeout": 45, "follow_redirects": True})], rel


def test_coverage_cdn_ignores_only_an_unselected_extra_marker():
    import run_coverage

    marker = 'tomli; python_full_version <= "3.11.0a6" and extra == "toml"'
    assert run_coverage._unselected_extra(marker)
    assert run_coverage._unselected_extra('tomli; (extra == "toml")')
    assert not run_coverage._unselected_extra("tomli")
    assert not run_coverage._unselected_extra('foo; python_version >= "3.11" or extra == "toml"')
    assert not run_coverage._unselected_extra('foo; python_full_version <= "3.11.0a6"')


def test_coverage_exercise_shape(tmp_path):
    coverage = pytest.importorskip("coverage")
    assert importlib.util.find_spec("coverage") is not None
    out = tmp_path / "coverage.json"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "mindeps" / "run_coverage.py"), "--impl", "real", str(out)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["missing_lines"] == len(data["missing"])
    assert data["summary"]["num_statements"] == len(data["statements"])
    assert "check_child_heads" in proc.stdout or data["statements"]
    del coverage
