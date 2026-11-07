#!/usr/bin/env python3
"""子（BlueProbe・QueRyu・SakAnalytics・PythDRagoras・DRAgoWing・NagoyAction）が各自の
conftest.py / tests に同じ中身で持っている検査の本体。Aoi が原本で、shared-tools.lock.json
で子の vendor/aoi/scripts/child_checks.py に配る（numpy_min・py_launch.cjs と同じ契約）。

標準ライブラリだけ。pytest は import しない（conftest.py からも tests からも読めるように）。
子の側に残るのは、子ごとに違う値（PIN、兄弟の名前、許可する第三者、既知の例外、
Node の入口名）と、それをここに渡す数行だけ。

    python -S scripts/child_checks.py pins   <root>            # 親ワークフローの pin を列挙
    python -S scripts/child_checks.py uses   <root> [兄弟...]  # 兄弟・scripts/ への参照を列挙
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PARENT = "myon-bioinformatics/myon-bioinformatics"
CHILDREN = ("blueprobe", "queryu", "sakanalytics", "pythdragoras", "nagoyaction", "dragowing")
SKIP_DIRS = frozenset({".git", ".venv", ".test-deps", ".parent-dispatch", "build", "reports", "__pycache__"})
AOI_ROOT_HINT = "AOI_ROOT=<Aoi のルート> を渡す（.github/workflows/ci.yml と同じ）"
NODE_MIN_MAJOR = 26


# --- conftest.py: AOI_ROOT と import 経路 --------------------------------------------------

def aoi_root_from_env(env=None) -> Path:
    """AOI_ROOT を Aoi のルートとして返す。推定はしない（子は Aoi の場所を引数でしか知らない）。"""
    env = os.environ if env is None else env
    value = env.get("AOI_ROOT")
    if not value:
        raise ValueError(AOI_ROOT_HINT)
    root = Path(value).expanduser().resolve()
    if not (root / "pyproject.toml").is_file() or not (root / "cycles").is_dir():
        raise ValueError(f"AOI_ROOT={root} は Aoi のルートではない。{AOI_ROOT_HINT}")
    return root


def export_path(path: Path, env=None) -> None:
    """sys.path と PYTHONPATH の両方に入れる（子プロセスにも同じ経路を渡す）。"""
    env = os.environ if env is None else env
    text = str(path)
    if text not in sys.path:
        sys.path.insert(0, text)
    current = env.get("PYTHONPATH", "")
    if text not in current.split(os.pathsep):
        env["PYTHONPATH"] = text if not current else text + os.pathsep + current


# --- tests/test_*_parent_workflow_pins.py ------------------------------------------------

def parent_workflow_pins(root: Path, parent: str = PARENT) -> list:
    """.github/workflows/ 内の親リポジトリ参照（uses の @ref と checkout の repository/ref）を集める。
    可変参照（``${{ steps.x.outputs.sha }}`` のような式も含む）や短縮 SHA も捨てずに返すので、
    呼ぶ側が set(pins) == {PIN} で見るか、許す式だけを先に除く。"""
    pins = []
    for path in sorted((root / ".github/workflows").glob("*")):
        if path.suffix not in (".yml", ".yaml"):
            continue
        text = path.read_text(encoding="utf-8")
        pins.extend(re.findall(r"uses:\s*['\"]?" + re.escape(parent) + r"/[^\s@'\"]+@([^\s'\"]+)", text))
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.fullmatch(r"\s+repository:\s*['\"]?" + re.escape(parent) + r"['\"]?\s*", line):
                refs = [re.fullmatch(r"\s+ref:\s*(.+?)\s*", item) for item in lines[i + 1:i + 12]]
                pins.append(next((m.group(1).strip("'\"") for m in refs if m), None))
    return pins


# --- tests/test_no_sibling_imports.py ------------------------------------------------------

def _sources(root: Path, skip_dirs, exclude: Path | None):
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if skip_dirs.intersection(rel.parts[:-1]) or path == exclude:
            continue
        yield rel.as_posix(), path


def _uses(tree, sibling_dirs):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield "import:" + alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield "import:" + node.module.split(".")[0]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.strip("/")
            if any(value == d or value.startswith(d + "/") for d in sibling_dirs):
                yield "path:" + value


def sibling_uses(root: Path, *, me: str, third_party=(), aoi_provided=("aoi_paths",),
                 extra_local=(), skip_dirs=SKIP_DIRS, exclude: Path | None = None) -> set:
    """許可外の import（標準ライブラリ・third_party・aoi_provided・自分のモジュール以外）と、
    ``me`` 以外の兄弟や Aoi の scripts/ を指すパス文字列を (相対パス, 対象) で返す。
    空なら違反なし。既知の例外は呼ぶ側が差し引く。自分がパッケージ名で import される子
    （dragowing）は extra_local にその名前を足す。"""
    sibling_dirs = tuple(c for c in CHILDREN if c != me) + ("scripts",)
    local = {p.stem for p in root.glob("*.py")} | {p.stem for p in (root / "tests").glob("*.py")}
    allowed = set(sys.stdlib_module_names) | set(third_party) | set(aoi_provided) | set(extra_local) | local
    found = set()
    for rel, path in _sources(root, frozenset(skip_dirs), exclude):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        for use in _uses(tree, sibling_dirs):
            if use.startswith("path:") or use[len("import:"):] not in allowed:
                found.add((rel, use))
    return found


# --- tests/test_*_node_entry.py: Node 入口と Python の一致 --------------------------------

def find_node(min_major: int = NODE_MIN_MAJOR, env=None) -> str | None:
    env = os.environ if env is None else env
    node = env.get("NODE") or shutil.which("node")
    if not node:
        return None
    try:
        result = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.match(r"v(\d+)", result.stdout.strip())
    return node if result.returncode == 0 and match and int(match.group(1)) >= min_major else None


def launch_env(tool: str, python: str = sys.executable, env=None) -> dict:
    """py_launch.cjs が読む <TOOL>_PYTHON を立て、エラー書式の上書きは外す。"""
    env = dict(os.environ if env is None else env)
    env[f"{tool.upper()}_PYTHON"] = python
    env.pop("PY_LAUNCH_ERROR_FORMAT", None)
    return env


def run(argv: list, cwd: Path, env: dict, timeout: int = 120) -> tuple:
    p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def parity(node: str, root: Path, tool: str, args: list, *, python: str = sys.executable) -> tuple:
    """同じ引数を Node 入口 (<tool>.cjs) と Python 本体 (<tool>.py) に渡した結果の組。"""
    env = launch_env(tool, python)
    via_node = run([node, str(root / f"{tool}.cjs"), *args], root, env)
    via_python = run([python, "-S", str(root / f"{tool}.py"), *args], root, env)
    return via_node, via_python


# --- CLI ----------------------------------------------------------------------------------

def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2 or argv[0] not in ("pins", "uses"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    if argv[0] == "pins":
        rows = parent_workflow_pins(root)
    else:
        rows = sorted(f"{rel}\t{use}" for rel, use in sibling_uses(root, me=root.name))
    for row in rows:
        print(row)
    return 0 if rows or argv[0] == "uses" else 1


if __name__ == "__main__":
    raise SystemExit(main())
