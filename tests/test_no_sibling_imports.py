"""SakAnalytics は Aoi の兄弟サブプロジェクト（pythdragoras など）と Aoi の scripts/ を import しない。

使ってよいのは、標準ライブラリ、pyproject の依存（polars）と pytest、任意の ortools
（season-requirements.txt。入っていなければ exact のテストは skip）、このリポジトリの
モジュールだけ。既知の例外は KNOWN_EXCEPTIONS に (ファイル, 対象) で書く。
例外が使われなくなったら、このテストが落ちるので消す。Aoi の sakanalytics/ でも同じ結果になる。
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", ".test-deps", "build", "reports", "__pycache__"}
THIRD_PARTY = {"polars", "pytest", "ortools"}
# Aoi の pyproject の pythonpath にある兄弟と、Aoi の scripts/
SIBLING_DIRS = ("blueprobe", "queryu", "pythdragoras", "nagoyaction", "dragowing", "scripts")
# Aoi のルートの aoi_paths.py（AOI_ROOT から読む。このリポジトリには置かない）。
# テストのデータの場所と、出力の証跡を固定した proposition_seed_audit の CLI が使う aoi_layout.py だけが読む
AOI_PROVIDED = {"aoi_paths"}
KNOWN_EXCEPTIONS = {
    # PythDRagoras の propositions。PYTHONPATH で渡す
    ("proposition_seed_audit.py", "import:propositions"),
    ("synthetic_rule_discovery.py", "import:propositions"),
    # proposition_seed_audit は親ディレクトリの pythdragoras/ も探す
    ("proposition_seed_audit.py", "path:pythdragoras"),
}


def _sources():
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        # このファイルは検出用の名前を文字列で持つので、自分は対象にしない
        if not SKIP_DIRS.intersection(rel.parts[:-1]) and path != Path(__file__).resolve():
            yield rel.as_posix(), path


def _local_modules():
    return {p.stem for p in ROOT.glob("*.py")} | {p.stem for p in (ROOT / "tests").glob("*.py")}


def _uses(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield "import:" + alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield "import:" + node.module.split(".")[0]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.strip("/")
            if any(value == d or value.startswith(d + "/") for d in SIBLING_DIRS):
                yield "path:" + value


def find_uses():
    allowed = set(sys.stdlib_module_names) | THIRD_PARTY | AOI_PROVIDED | _local_modules()
    found = set()
    for rel, path in _sources():
        for use in _uses(ast.parse(path.read_text(encoding="utf-8"), filename=rel)):
            if use.startswith("path:") or use[len("import:"):] not in allowed:
                found.add((rel, use))
    return found


def test_no_sibling_subproject_imports():
    unexpected = find_uses() - KNOWN_EXCEPTIONS
    assert not unexpected, f"Aoi の兄弟サブプロジェクトか scripts/ を使っている: {sorted(unexpected)}"


def test_known_exceptions_are_still_used():
    stale = KNOWN_EXCEPTIONS - find_uses()
    assert not stale, f"使われなくなった例外を KNOWN_EXCEPTIONS から消す: {sorted(stale)}"


def test_detector_catches_imports_and_paths():
    code = ("import sakanalytics.x\nfrom queryu import a\nfrom . import b\nimport json\n"
            "p = 'scripts/x.py'\nq = '/dragowing/'\nr = 'cycles/c001'\ns = 'scriptsx'\n")
    uses = set(_uses(ast.parse(code)))
    assert {"import:sakanalytics", "import:queryu", "import:json", "path:scripts/x.py", "path:dragowing"} == uses
