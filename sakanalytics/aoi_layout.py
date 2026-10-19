"""Bind ``aoi_paths`` when the repository root is not on ``sys.path``."""
from __future__ import annotations

from pathlib import Path
import sys


def bind(anchor: Path | str):
    here = Path(anchor).resolve()
    if here.is_file():
        here = here.parent
    for root in (here, *here.parents):
        if (root / "aoi_paths.py").is_file():
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            import aoi_paths

            return aoi_paths
    raise ImportError(f"aoi_paths.py not found above {anchor}")
