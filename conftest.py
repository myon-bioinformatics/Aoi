"""DRAgoWing 単独リポジトリ用。サイクルデータと PythDRagoras・QueRyu は Aoi に残す（AOI_ROOT）。

このディレクトリはパッケージ dragowing の中身（__init__.py は置かない）。
Aoi では同じディレクトリがすでに dragowing として import できるので、登録は何もしない。
"""
import importlib.machinery
import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent


def _dragowing_importable_from_same_dir(root: Path) -> bool:
    """True when `import dragowing` already searches this directory (Aoi)."""
    spec = importlib.util.find_spec("dragowing")
    if spec is None:
        return False
    return any(Path(path).resolve() == root for path in spec.submodule_search_locations or [])


def _register_dragowing_package(root: Path) -> None:
    if _dragowing_importable_from_same_dir(root):
        return
    pkg = types.ModuleType("dragowing")
    pkg.__path__ = [str(root)]
    pkg.__package__ = "dragowing"
    spec = importlib.machinery.ModuleSpec("dragowing", loader=None, is_package=True)
    spec.submodule_search_locations = pkg.__path__
    pkg.__spec__ = spec
    sys.modules["dragowing"] = pkg


_register_dragowing_package(_REPO)


def _root() -> Path:
    # Aoi の場所は AOI_ROOT で受け取る（Aoi の中では Aoi の conftest.py が入れる）。ここでは推定しない
    value = os.environ.get("AOI_ROOT")
    here = Path(__file__).resolve().parent
    if not value and (here.parent / "aoi_paths.py").is_file():
        # Aoi に subtree として埋め込まれ、子のディレクトリだけで pytest を動かしたとき（rootdir が子になる）
        value = str(here.parent)
    if not value:
        raise pytest.UsageError("AOI_ROOT=<Aoi のルート> を渡す（.github/workflows/ci.yml と同じ）")
    root = Path(value).expanduser().resolve()
    # テストのデータの場所（既定のサイクル）は Aoi の aoi_paths.py に聞く。DRAgoWing には置かない
    if str(root) not in sys.path:
        sys.path.append(str(root))
    return root


_root()


def pytest_configure(config):
    root = _root()
    if not (root / "cycles").is_dir():
        raise pytest.UsageError(
            f"Aoi のデータが見つからない（{root} に cycles/ がない）。"
            "Aoi を checkout して AOI_ROOT=<Aoi のルート>、"
            "PYTHONPATH=<Aoi のルート>/pythdragoras:<Aoi のルート>/queryu/ask を渡す"
            "（.github/workflows/ci.yml と同じ）"
        )


def pytest_report_header(config):
    return f"AOI_ROOT={_root()}"


@pytest.fixture(scope="session")
def aoi_root() -> Path:
    return _root()
