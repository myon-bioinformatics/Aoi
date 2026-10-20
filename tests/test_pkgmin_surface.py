"""Used surface of requests, tqdm, and biopython, and the stdlib stand-ins.

The stand-ins export nothing: the tree does not call those packages. When the
real packages are installed (``PKGMIN_REQUIRE_REAL=1`` in the CI job), the
tests show that their usual entry points work and that the stand-ins still
refuse those names.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pkgmin.survey as survey  # noqa: E402
import pkgmin.trace_used as trace  # noqa: E402

EVIDENCE = ROOT / "pkgmin" / "evidence" / "used-surface.json"
WORKFLOW = ROOT / ".github" / "workflows" / "pkgmin-stdlib.yml"
MIN_FILES = {
    "requests": ROOT / "pkgmin" / "requests_min.py",
    "tqdm": ROOT / "pkgmin" / "tqdm_min.py",
    "Bio": ROOT / "pkgmin" / "biopython_min.py",
}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path, submodule_search_locations=[])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _real(name: str):
    if os.environ.get("PKGMIN_REQUIRE_REAL") == "1":
        return importlib.import_module(name)
    return pytest.importorskip(name)


def test_committed_surface_matches_the_tree():
    fresh = survey.scan(ROOT)
    saved = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert saved["packages"] == fresh["packages"]
    assert saved["dynamic_nonliteral"] == fresh["dynamic_nonliteral"]
    assert fresh["files_scanned"] > 200
    for dist, info in fresh["packages"].items():
        assert info["import_sites"] == []
        assert info["attributes"] == {}
        assert info["declared"] == []
        assert dist in {"requests", "tqdm", "biopython"}


def test_survey_sees_a_declared_dependency(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.1.0"\ndependencies = ["requests>=2"]\n',
        encoding="utf-8",
    )
    (tmp_path / "extra-requirements.txt").write_text("biopython>=1.83\n# tqdm>=4\n", encoding="utf-8")
    found = survey.scan(tmp_path)
    assert found["packages"]["requests"]["declared"] == [
        {"file": "pyproject.toml", "kind": "runtime", "name": "requests"}
    ]
    assert found["packages"]["biopython"]["declared"] == [
        {"file": "extra-requirements.txt", "kind": "requirements", "name": "biopython"}
    ]
    assert found["packages"]["tqdm"]["declared"] == []


def test_survey_sees_a_synthetic_import(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "import requests\n"
        "from tqdm import tqdm\n"
        "from Bio.SeqIO import parse\n"
        "def use(rows):\n"
        "    return requests.get(rows), tqdm(rows), parse(rows)\n",
        encoding="utf-8",
    )
    found = survey.scan(tmp_path)
    assert found["packages"]["requests"]["import_sites"][0]["module"] == "requests"
    assert "get" in found["packages"]["requests"]["attributes"]
    assert "tqdm" in found["packages"]["tqdm"]["attributes"]
    assert "SeqIO.parse" in found["packages"]["biopython"]["attributes"]


def test_absent_traceback_names_the_import(tmp_path: Path):
    script = tmp_path / "use_requests.py"
    script.write_text("import requests\n", encoding="utf-8")
    data = trace.launch("absent", [str(script)], tmp_path / "absent.json", tmp_path, ("requests",))
    assert data["status"] == 1
    assert data["hits"] == ["requests"]
    assert "ModuleNotFoundError" in (data["traceback"] or "")
    assert "use_requests.py" in (data["traceback"] or "")


def test_stub_logs_the_attribute_the_ast_would_miss_on_a_returned_value(tmp_path: Path):
    script = tmp_path / "use_stub.py"
    script.write_text(
        "import requests\n"
        "response = requests.get('http://127.0.0.1/nope')\n"
        "response.status_code\n",
        encoding="utf-8",
    )
    data = trace.launch("stub", [str(script)], tmp_path / "stub.json", tmp_path, ("requests",))
    assert data["status"] == 0, data.get("traceback")
    assert "requests.get" in data["dynamic_attributes"]
    assert "requests.get().status_code" in data["dynamic_attributes"]


def test_project_paths_do_not_import_the_packages():
    saved = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    fresh = trace.collect(ROOT)
    assert fresh == saved["traces"]
    for row in fresh:
        assert row["hits"] == []
        assert row["dynamic_attributes"] == []
        assert row["status"] == 0
        assert row["exception"] is None


def test_real_paths_match_when_the_standins_are_injected(tmp_path: Path):
    none = tmp_path / "none.json"
    injected = tmp_path / "min.json"
    for label, path in (("none", none), ("min", injected)):
        proc = subprocess.run(
            [sys.executable, "pkgmin/run_paths.py", "--inject", label, str(path)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, proc.stderr
    assert none.read_bytes() == injected.read_bytes()


def test_standins_are_stdlib_and_cover_only_the_empty_surface():
    for name, path in MIN_FILES.items():
        proc = subprocess.run(
            [sys.executable, "-S", "-c", textwrap.dedent(f"""
                import importlib.util
                spec = importlib.util.spec_from_file_location({name!r}, {str(path)!r}, submodule_search_locations=[])
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                assert module.SURFACE == ()
                try:
                    getattr(module, "get" if {name!r} != "tqdm" else "tqdm")
                except AttributeError as exc:
                    assert type(exc).__name__ == "UsedSurfaceError"
                else:
                    raise SystemExit("unused name was exported")
            """)],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, proc.stderr
        import ast
        imported: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        assert not imported & {"requests", "tqdm", "Bio", "biopython"}


def test_workflow_absence_check_is_a_conditional_not_a_bare_negation():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "if .venv/bin/python -c 'import requests' >/dev/null 2>&1; then" in text
    assert "if .venv/bin/python -c 'import tqdm' >/dev/null 2>&1; then" in text
    assert "if .venv/bin/python -c 'import Bio' >/dev/null 2>&1; then" in text
    for line in text.splitlines():
        stripped = line.strip()
        assert not stripped.startswith("!"), stripped


def test_real_entry_points_work_and_are_not_the_used_surface():
    """The usual calls succeed on the real packages and are absent from the stand-ins.

    A one-shot GET, ``tqdm`` over three integers, and ``SeqIO.parse`` of a
    two-base FASTA are the shapes a shrink would have copied. They are not
    calls in this tree, so the stand-ins raise instead of answering them.
    """
    requests = _real("requests")
    tqdm = _real("tqdm")
    bio = _real("Bio.SeqIO")
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import threading
    from io import StringIO

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return None

    sys.path.insert(0, str(ROOT / "queryu"))
    import urllib.request
    from queryu import UrllibClient

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/ok"
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, timeout=5)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        urllib_body = UrllibClient(timeout=5, opener=opener).get(url).content
    finally:
        server.shutdown()
        thread.join(timeout=2)
    assert response.status_code == 200
    assert response.content == urllib_body == b"ok"
    assert list(tqdm.tqdm(range(3), disable=True)) == [0, 1, 2]
    record = next(bio.parse(StringIO(">a\nAT\n"), "fasta"))
    assert record.id == "a"
    assert str(record.seq) == "AT"

    requests_min = _load("requests_min_under_test", MIN_FILES["requests"])
    tqdm_min = _load("tqdm_min_under_test", MIN_FILES["tqdm"])
    bio_min = _load("bio_min_under_test", MIN_FILES["Bio"])
    with pytest.raises(requests_min.UsedSurfaceError):
        requests_min.get
    with pytest.raises(requests_min.UsedSurfaceError):
        requests_min.Session
    with pytest.raises(tqdm_min.UsedSurfaceError):
        tqdm_min.tqdm
    with pytest.raises(bio_min.UsedSurfaceError):
        bio_min.SeqIO
    saved = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert saved["packages"]["requests"]["import_sites"] == []
    assert saved["packages"]["tqdm"]["import_sites"] == []
    assert saved["packages"]["biopython"]["import_sites"] == []
