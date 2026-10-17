"""Repository layout helpers for Aoi and split child repos (stdlib only)."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_CYCLE = "c001-chunichi"


def infer_aoi_root(anchor: Path) -> Path:
    """Walk upward from a file or directory to the Aoi repository root."""
    here = anchor.resolve()
    if here.is_file():
        here = here.parent
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "cycles").is_dir():
            return candidate
    if len(here.parents) >= 2:
        return here.parents[1]
    return here


def resolve_aoi_root(explicit: Path | str | None = None, *, anchor: Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("AOI_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    if anchor is None:
        anchor = Path.cwd()
    return infer_aoi_root(anchor)


def cycle_name(explicit: str | None = None) -> str:
    return explicit or os.environ.get("AOI_RESEARCH_CYCLE") or DEFAULT_CYCLE


def resolve_cycle_path(root: Path, cycle: str | Path | None = None) -> Path:
    """Return the cycle directory under ``root`` (or an absolute cycle path)."""
    if cycle is None:
        return (root / "cycles" / cycle_name()).resolve()
    path = Path(cycle)
    if path.is_absolute():
        return path.resolve()
    if path.parts[:1] == ("cycles",):
        return (root / path).resolve()
    if len(path.parts) == 1:
        return (root / "cycles" / path).resolve()
    return (root / path).resolve()


def default_cycle_outputs(root: Path | None = None, *, cycle: str | None = None) -> Path:
    base = root or resolve_aoi_root()
    return resolve_cycle_path(base, cycle) / "outputs"
