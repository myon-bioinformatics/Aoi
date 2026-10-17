"""PythDRagoras 単独リポジトリ用。サイクルデータ・scripts/・sakanalytics は Aoi に残す（AOI_ROOT）。"""
from pathlib import Path

import pytest

import aoi_paths


def _root() -> Path:
    # Aoi の conftest.py と同じ解決順（AOI_ROOT → このファイルからの推定）
    return aoi_paths.resolve_aoi_root(anchor=Path(__file__))


def pytest_configure(config):
    root = _root()
    if not (root / "cycles").is_dir():
        raise pytest.UsageError(
            f"Aoi のデータが見つからない（{root} に cycles/ がない）。"
            "Aoi を checkout して AOI_ROOT=<Aoi のルート>、"
            "PYTHONPATH=<Aoi のルート>/sakanalytics を渡す（docs/ci/ci.yml.proposed と同じ）"
        )


def pytest_report_header(config):
    return f"AOI_ROOT={_root()}"


@pytest.fixture(scope="session")
def aoi_root() -> Path:
    return _root()
