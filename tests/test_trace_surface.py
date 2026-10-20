"""Offline checks for scripts/trace_surface.py, using a tiny stand-in package."""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "scripts" / "trace_surface.py"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")


def _tree(tmp: Path) -> None:
    _write(tmp / "fakeutil.py", """
        class Box:
            def __init__(self, n):
                self.n = n
            def beta(self):
                return self.n
        def alpha(n):
            return Box(n)
    """)
    _write(tmp / "driver.py", """
        import fakeutil
        box = fakeutil.alpha(2)
        got = box.beta()
        if got != 2:
            raise SystemExit("bad value")
    """)
    _write(tmp / "pyproject.toml", """
        [project]
        name = "sample"
        version = "0"
        dependencies = ["fakeutil"]
    """)


def _run(tmp: Path, mode: str, out: Path):
    return subprocess.run(
        [sys.executable, str(TRACE), mode, "fakeutil", "--root", str(tmp), "--out", str(out),
         "--", sys.executable, str(tmp / "driver.py")],
        cwd=tmp, capture_output=True, text=True,
    )


def test_absent_blocks_an_installed_module_and_keeps_the_traceback(tmp_path):
    _tree(tmp_path)
    out = tmp_path / "absent.json"
    proc = _run(tmp_path, "absent", out)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == 1
    assert "ModuleNotFoundError" in data["traceback"]
    assert "driver.py" in data["traceback"]
    assert data["missed_by_ast"] == []


def test_stub_records_the_attribute_chain_until_it_needs_a_real_value(tmp_path):
    _tree(tmp_path)
    out = tmp_path / "stub.json"
    proc = _run(tmp_path, "stub", out)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "StubGap" in data["traceback"]
    names = set(data["dynamic_attributes"])
    assert {"alpha", "beta", "__ne__"} <= names or {"alpha", "beta", "__eq__"} <= names
    assert "beta" in data["missed_by_ast"]
    assert "alpha" not in data["missed_by_ast"]


def test_wrap_delegates_and_reports_methods_the_ast_did_not_count(tmp_path):
    _tree(tmp_path)
    out = tmp_path / "wrap.json"
    proc = _run(tmp_path, "wrap", out)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == 0
    assert data["traceback"] is None
    assert "beta" in data["missed_by_ast"]
    assert "alpha" in data["ast_attributes"]
    assert any(event["name"] == "beta" and event["file"] == "driver.py" for event in data["events"])


def test_committed_traces_keep_the_names_the_report_cites():
    """The live re-run is the workflow. This locks the names that note depends on."""
    data = json.loads((ROOT / "docs" / "evidence" / "trace-surfaces.json").read_text(encoding="utf-8"))
    runs = {(row["mode"], row["package"], row["driver"]): row for row in data["runs"]}

    polars = runs[("wrap", "polars", "load_overlap")]
    assert {"height", "columns", "select", "to_list", "__gt__"} <= set(polars["missed_by_ast"])
    assert polars["status"] == 0

    numpy_overlap = runs[("wrap", "numpy", "load_overlap")]
    assert {"reshape", "astype", "__and__", "__invert__"} <= set(numpy_overlap["missed_by_ast"])
    assert "svd" in runs[("wrap", "numpy", "suggest_index")]["dynamic_attributes"]
    assert "lstsq" in runs[("wrap", "numpy", "littlebit_svd")]["dynamic_attributes"]

    assert {"css", "text", "attributes", "tag"} <= set(runs[("wrap", "selectolax", "selectolax_css")]["missed_by_ast"])
    assert {"get", "status_code", "content", "headers"} <= set(runs[("wrap", "httpx", "httpx_get")]["missed_by_ast"])
    assert runs[("wrap", "markdown", "render_md")]["missed_by_ast"] == ["markdown"]
    assert "ModuleNotFoundError" in runs[("absent", "polars", "load_overlap")]["exception"]
    assert "StubGap" in runs[("stub", "polars", "load_overlap")]["exception"]
