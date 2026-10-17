"""QueRyu 単独リポジトリ用。サイクルデータ・blueprobe の fixture・nagoyaction/inbox は Aoi に残す（AOI_ROOT）。

BlueProbe（抽出）は固定 SHA の BlueProbe checkout を PYTHONPATH で渡す。Aoi の blueprobe/ は使わない。
"""
from pathlib import Path
import sys

import pytest

import aoi_paths

HERE = Path(__file__).resolve().parent
# 取り違えると Aoi 側のコピーを黙ってテストしてしまうので、出どころを最後に確かめる
OWN_MODULES = ("queryu", "annual_scope", "ask", "bank", "suggest", "aoi_layout")


def _root() -> Path:
    # Aoi の conftest.py と同じ解決順（AOI_ROOT → このファイルからの推定）
    return aoi_paths.resolve_aoi_root(anchor=Path(__file__))


def _blueprobe_origin_is_allowed(origin: Path, root: Path, here: Path = HERE) -> bool:
    """Embedded subtree uses Aoi/blueprobe; standalone must use an external checkout."""
    if here == root / "queryu":
        return origin.parent == root / "blueprobe"
    return root not in origin.parents


def pytest_configure(config):
    root = _root()
    if not (root / "cycles").is_dir() or not (root / "nagoyaction" / "inbox").is_dir():
        raise pytest.UsageError(
            f"Aoi のデータが見つからない（{root} に cycles/ か nagoyaction/inbox/ がない）。"
            "Aoi を checkout して AOI_ROOT=<Aoi のルート> を渡す（.github/workflows/ci.yml と同じ）"
        )
    # nagoyaction/inbox/inbox.py は Aoi の queryu/ask を sys.path の先頭に足す。
    # 先に QueRyu 側の ask・bank・suggest を読み込んでおき、Aoi 側のコピーが使われないようにする
    for name in ("ask", "bank", "suggest"):
        __import__(name)
    inbox_dir = str(root / "nagoyaction" / "inbox")
    if inbox_dir not in sys.path:
        sys.path.append(inbox_dir)
    try:
        import blueprobe
    except ImportError as error:
        raise pytest.UsageError(
            f"blueprobe を import できない（{error}）。BlueProbe を checkout して PYTHONPATH に渡す"
        ) from None
    origin = Path(blueprobe.__file__).resolve()
    if not _blueprobe_origin_is_allowed(origin, root):
        raise pytest.UsageError(f"blueprobe の出どころが不正（{origin}）。単独では外部 checkout、Aoi 内では Aoi/blueprobe を使う")


def pytest_report_header(config):
    import blueprobe
    return [f"AOI_ROOT={_root()}", f"blueprobe={Path(blueprobe.__file__).resolve()}"]


def pytest_sessionfinish(session, exitstatus):
    wrong = {}
    for name in OWN_MODULES:
        module = sys.modules.get(name)
        origin = getattr(module, "__file__", None)
        if origin is not None and HERE not in Path(origin).resolve().parents:
            wrong[name] = origin
    if wrong:
        if exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        if terminal is not None:
            terminal.write_sep("=", "QueRyu のモジュールが別の場所から読まれた")
            for name, origin in sorted(wrong.items()):
                terminal.write_line(f"{name}: {origin}")


@pytest.fixture(scope="session")
def aoi_root() -> Path:
    return _root()
