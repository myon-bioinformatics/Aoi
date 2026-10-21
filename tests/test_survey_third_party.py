"""Offline checks for scripts/survey_third_party.py."""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "scripts" / "survey_third_party.py"


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
    import survey_third_party as survey

    _project(tmp_path)
    data = survey.survey(tmp_path)
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
        [sys.executable, str(SURVEY), "--root", str(tmp_path), "--check", str(target)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1
    subprocess.run(
        [sys.executable, str(SURVEY), "--root", str(tmp_path), "--json", str(target)],
        check=True, capture_output=True, text=True,
    )
    proc = subprocess.run(
        [sys.executable, str(SURVEY), "--root", str(tmp_path), "--check", str(target)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    json.loads(target.read_text(encoding="utf-8"))


def test_pep701_fstring_quotes_parse_and_keep_import_counts(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import survey_third_party as survey

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
    data = survey.survey(tmp_path)
    assert data["unparsed"] == []
    assert data["packages"]["polars"]["attributes"] == {"col": 1}
    tree = survey.parse_source(nested, "nested.py")
    assert isinstance(tree, survey.ast.AST)


def test_committed_inventory_matches_the_tree():
    proc = subprocess.run(
        [sys.executable, str(SURVEY), "--check", str(ROOT / "docs" / "evidence" / "third-party-survey.json")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_selection_keeps_whole_root_classification(tmp_path):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import survey_third_party as survey
    _project(tmp_path)
    data = survey.survey(tmp_path, matches=['app.py', 'child/*'], excludes=['child/*'])
    assert {row['file'] for row in data['sites']} == {'app.py'}
    assert set(data['packages']) == {'polars'}  # excluded localmod is still local
    assert data['packages']['polars']['declared']
    assert data['selection']['files'] == 1
    assert data['selection']['declared_without_imports_scope'] == 'selected_sources'
    assert 'selected sources' in survey.render(data)


def test_list_does_not_read_source_or_declarations(tmp_path, monkeypatch, capsys):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import survey_third_party as survey
    _project(tmp_path)
    def forbidden(*a, **k):
        raise AssertionError('content was read')
    monkeypatch.setattr(Path, 'read_text', forbidden)
    assert survey.main(['--root', str(tmp_path), '--match', 'child/*', '--list']) == 0
    assert json.loads(capsys.readouterr().out) == ['child/use_pl.py']


def test_selection_errors_and_scoped_check(tmp_path):
    _project(tmp_path)
    base = [sys.executable, '-S', str(SURVEY), '--root', str(tmp_path)]
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
