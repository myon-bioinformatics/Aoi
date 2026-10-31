"""scripts/shrink_polars.py の trace / absent が動かす仕事（Aoi の c001 で load_overlap を 1 回走らせる）。"""
from __future__ import annotations

from pathlib import Path


def run(root: Path) -> dict:
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    season = root / "cycles/c001-chunichi/outputs/season.jsonl"
    props = root / "cycles/c001-chunichi/outputs/propositions.jsonl"
    return load_overlap(season, default_conditions(read_jsonl(props), read_jsonl(season)))
