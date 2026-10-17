import os
from pathlib import Path

import aoi_paths


def test_resolve_aoi_root_from_subproject_anchor():
    anchor = Path(__file__).resolve().parent.parent / "queryu" / "ask" / "ask.py"
    root = aoi_paths.resolve_aoi_root(anchor=anchor)
    assert (root / "cycles" / aoi_paths.DEFAULT_CYCLE).is_dir()


def test_aoi_root_env_overrides_inference(monkeypatch, tmp_path):
    fake = tmp_path / "fake-aoi"
    (fake / "cycles" / "c9").mkdir(parents=True)
    monkeypatch.setenv("AOI_ROOT", str(fake))
    got = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
    assert got == fake.resolve()


def test_resolve_cycle_path_accepts_name_or_relative(tmp_path):
    root = tmp_path / "repo"
    (root / "cycles" / "c001-chunichi").mkdir(parents=True)
    assert aoi_paths.resolve_cycle_path(root, "c001-chunichi") == (root / "cycles" / "c001-chunichi").resolve()
    assert aoi_paths.resolve_cycle_path(root, Path("cycles/c001-chunichi")) == (root / "cycles" / "c001-chunichi").resolve()


def test_cycle_name_env(monkeypatch):
    monkeypatch.setenv("AOI_RESEARCH_CYCLE", "c9")
    assert aoi_paths.cycle_name() == "c9"
    monkeypatch.delenv("AOI_RESEARCH_CYCLE", raising=False)
    assert aoi_paths.cycle_name() == aoi_paths.DEFAULT_CYCLE
