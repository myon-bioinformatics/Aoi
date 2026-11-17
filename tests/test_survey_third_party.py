"""Offline checks for `scripts/stdlib_min.py survey`.

旧 test_trace_surface.py もここにまとめた（節の頭に旧ファイルの名前を書いた）。
"""

import json
import subprocess
import sys
import textwrap
from pathlib import Path


# ==== survey（旧 test_survey_third_party.py）

ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "scripts" / "stdlib_min.py"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")


def _project(tmp: Path) -> None:
    _write(tmp / "pyproject.toml", """
        [project]
        name = "sample"
        version = "0"
        dependencies = ["polars>=1", "Markdown>=3"]
        [dependency-groups]
        dev = ["pytest>=8"]
    """)
    _write(tmp / "app.py", """
        import polars as pl
        import localmod

        def build(frame):
            return frame.select(pl.col("a") > 1)
    """)
    _write(tmp / "localmod.py", """
        def ready():
            return True
    """)
    _write(tmp / "markdown.py", """
        # A project file that happens to share the distribution's import name.
        def local():
            return "not-the-pypi-package"
    """)
    _write(tmp / "dyn.py", """
        import importlib
        markdown = importlib.import_module("markdown")
        def render(text):
            return markdown.markdown(text)
    """)
    _write(tmp / "child" / "use_pl.py", """
        import polars as pl
        pl.read_ndjson("x.jsonl")
    """)
    _write(tmp / "odd.py", """
        import importlib
        importlib.import_module(module_name)
    """)


def test_survey_counts_aliases_dynamic_imports_and_declared_names(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import stdlib_min as survey

    _project(tmp_path)
    data = survey.survey_survey(tmp_path)
    assert set(data["packages"]) == {"polars", "markdown"}
    polars = data["packages"]["polars"]
    assert polars["files"] == 2
    assert polars["import_sites"] == 2
    assert polars["attributes"] == {"col": 1, "read_ndjson": 1}
    assert polars["by_tree"]["child"]["attributes"] == {"read_ndjson": 1}
    assert polars["by_tree"]["aoi"]["attributes"] == {"col": 1}
    assert data["packages"]["markdown"]["dynamic_import_sites"] == 1
    # ``markdown = import_module("markdown"); markdown.markdown`` is not an import alias.
    assert data["packages"]["markdown"]["attributes"] == {}
    assert data["packages"]["markdown"]["declared"][0]["name"] == "Markdown"
    assert any(row["name"] == "pytest" for row in data["declared_without_imports"])
    assert [row["file"] for row in data["dynamic_nonliteral"]] == ["odd.py"]
    assert "localmod" not in data["packages"]


def test_check_fails_when_the_inventory_is_stale(tmp_path):
    _project(tmp_path)
    target = tmp_path / "inventory.json"
    target.write_text("{}\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SURVEY), "survey", "--root", str(tmp_path), "--check", str(target)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    subprocess.run(
        [sys.executable, str(SURVEY), "survey", "--root", str(tmp_path), "--json", str(target)],
        check=True, capture_output=True, text=True,
    )
    proc = subprocess.run(
        [sys.executable, str(SURVEY), "survey", "--root", str(tmp_path), "--check", str(target)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    json.loads(target.read_text(encoding="utf-8"))


def test_pep701_fstring_quotes_parse_and_keep_import_counts(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import stdlib_min as survey

    nested = "shown = f'{row['team']}-{row['season']}'\n"
    same_line = (
        "print(f\"（{', '.join(f'{r['team']}-{r['season']}' for r in big if r['upper_half'])}）\")\n"
    )
    relaxed_nested = survey.relax_fstring_quotes(nested)
    relaxed_line = survey.relax_fstring_quotes(same_line)
    untouched = survey.relax_fstring_quotes("label = f\"{r['team']}\"\n")
    assert relaxed_nested == "shown = f'''{row['team']}-{row['season']}'''\n"
    assert "f'''{r['team']}-{r['season']}'''" in relaxed_line
    assert "r['upper_half']" in relaxed_line
    assert untouched == "label = f\"{r['team']}\"\n"
    for source in (relaxed_nested, relaxed_line, untouched):
        survey.ast.parse(source)

    _write(tmp_path / "pyproject.toml", """
        [project]
        name = "sample"
        version = "0"
        dependencies = ["polars>=1"]
    """)
    _write(tmp_path / "nested.py", """
        import polars as pl

        def label(row):
            shown = f'{row['team']}-{row['season']}'
            return pl.col(shown)
    """)
    data = survey.survey_survey(tmp_path)
    assert data["unparsed"] == []
    assert data["packages"]["polars"]["attributes"] == {"col": 1}
    tree = survey.parse_source(nested, "nested.py")
    assert isinstance(tree, survey.ast.AST)


def test_committed_inventory_matches_the_tree():
    proc = subprocess.run(
        [sys.executable, str(SURVEY), "survey", "--check", str(ROOT / "docs" / "evidence" / "third-party-survey.json")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_selection_keeps_whole_root_classification(tmp_path):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import stdlib_min as survey
    _project(tmp_path)
    data = survey.survey_survey(tmp_path, matches=['app.py', 'child/*'], excludes=['child/*'])
    assert {row['file'] for row in data['sites']} == {'app.py'}
    assert set(data['packages']) == {'polars'}  # excluded localmod is still local
    assert data['packages']['polars']['declared']
    assert data['selection']['files'] == 1
    assert data['selection']['declared_without_imports_scope'] == 'selected_sources'
    assert 'selected sources' in survey.render(data)


def test_list_does_not_read_source_or_declarations(tmp_path, monkeypatch, capsys):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import stdlib_min as survey
    _project(tmp_path)
    def forbidden(*a, **k):
        raise AssertionError('content was read')
    monkeypatch.setattr(Path, 'read_text', forbidden)
    assert survey.survey(['--root', str(tmp_path), '--match', 'child/*', '--list']) == 0
    assert json.loads(capsys.readouterr().out) == ['child/use_pl.py']


def test_selection_errors_and_scoped_check(tmp_path):
    _project(tmp_path)
    base = [sys.executable, '-S', str(SURVEY), "survey", '--root', str(tmp_path)]
    for args in (['--match', 'missing*'], ['--exclude', '*.py'], ['--match', ''],
                 ['--list', '--json', str(tmp_path / 'never.json')]):
        proc = subprocess.run(base + args, capture_output=True, text=True)
        assert proc.returncode == 2, proc.stderr
    target = tmp_path / 'selected.json'
    args = ['--match', 'app.py']
    subprocess.run(base + args + ['--json', str(target)], check=True, capture_output=True)
    proc = subprocess.run(base + args + ['--check', str(target)], capture_output=True)
    assert proc.returncode == 0, proc.stderr
    proc = subprocess.run(base + ['--check', str(target)], capture_output=True)
    assert proc.returncode == 1


def test_list_ignores_directories_with_python_suffix(tmp_path, capsys):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import stdlib_min as survey
    (tmp_path / 'directory.py').mkdir()
    assert survey.survey(['--root', str(tmp_path), '--list']) == 0
    assert json.loads(capsys.readouterr().out) == []
    assert survey.survey(['--root', str(tmp_path), '--match', '*.py', '--list']) == 2


# ==== trace（旧 test_trace_surface.py）
# Offline checks for `scripts/stdlib_min.py trace-surface`, using a tiny stand-in package.


TRACE = ROOT / "scripts" / "stdlib_min.py"


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
        [sys.executable, str(TRACE), "trace-surface", mode, "fakeutil", "--root", str(tmp), "--out", str(out),
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
    suggest = runs[("wrap", "numpy", "suggest_index")]
    assert suggest["status"] == 0 and suggest["exception"] is None
    assert suggest["dynamic_attributes"] == [] and suggest["first_events"] == []
    history = json.loads((ROOT / "docs/evidence/suggest-numpy-trace-history.json").read_text())
    assert "svd" in history["runs"][0]["dynamic_attributes"]
    assert "lstsq" in runs[("wrap", "numpy", "littlebit_svd")]["dynamic_attributes"]

    assert {"css", "text", "attributes", "tag"} <= set(runs[("wrap", "selectolax", "selectolax_css")]["missed_by_ast"])
    assert {"get", "status_code", "content", "headers"} <= set(runs[("wrap", "httpx", "httpx_get")]["missed_by_ast"])
    assert "ModuleNotFoundError" in runs[("absent", "polars", "load_overlap")]["exception"]
    assert "StubGap" in runs[("stub", "polars", "load_overlap")]["exception"]
