"""🧮 α: 重なりの native の経路（numpy・polars と、兄弟 PythDRagoras の rule_search）。

dragowing.py は標準ライブラリだけで動く。ここは内部解析用で、numpy・polars（dev グループ）を読む。
マスクは rule_search のビット行列。空の比較（JSON の null）は真に数えない（rule_search._mask と同じ）。
件数は bool 行列の和で、丸めない。

``load_overlap`` は今までどおり native が既定（Aoi の shrink の入口 ``dragowing/overlap.py:load_overlap``）。
backend="stdlib" は dragowing.py の標準ライブラリの経路に渡す。条件の名前・既定の条件などは
dragowing.py のものをそのまま出す（``from dragowing.overlap import default_conditions`` も読める）。
"""
from __future__ import annotations

from pathlib import Path

from .dragowing import (  # noqa: F401  - 旧 dragowing.overlap の名前もここから読める
    B_COND,
    MAX_SETS,
    OPS,
    _overlap_region,
    _overlap_result,
    _patterns,
    _sibling,
    default_conditions,
    finalize_conditions,
    is_b,
    label_of,
    parse_cond,
    read_jsonl,
)
from .dragowing import load_overlap as _stdlib_overlap


def _engines():
    # PythDRagoras の propositions と rule_search。場所は呼び出し側（Aoi の aoi.py）が入れる
    propositions = _sibling("propositions", "PythDRagoras")
    rule_search = _sibling("rule_search", "PythDRagoras")
    return rule_search, propositions


def load_overlap(path: Path, conds: list[dict], *, backend: str = "native") -> dict:
    """条件行列と領域の件数。backend="stdlib" だけがライブラリ不要の限定経路（dragowing.py）。"""
    if backend == "stdlib":
        return _stdlib_overlap(path, conds, backend="stdlib")
    if backend != "native":
        raise ValueError(f"overlap backend は native か stdlib: {backend}")
    path = Path(path)
    labeled = [{**cond, "label": label_of(cond)} for cond in conds]
    try:
        import numpy as np
        import polars as pl
    except ImportError as exc:
        # 🧮 native は PythDRagoras の rule_search 用。numpy・polars は dev グループにある
        # 足りないのはパッケージなので ModuleNotFoundError のまま（読み込みの検査が import の行として数えられる）
        raise ModuleNotFoundError(f"native の重なりには numpy・polars が要る（uv sync --group dev）。既定は stdlib の経路: {exc}",
                                  name=exc.name) from exc

    rows = read_jsonl(path)
    rule_search, _ = _engines()
    frame = pl.read_ndjson(path)
    if frame.height != len(rows):
        raise ValueError("season.jsonl の行数が揃わない")
    teams, seasons = frame["team"].to_list(), frame["season"].to_list()
    for index, row in enumerate(rows):
        if teams[index] != row["team"] or seasons[index] != row["season"]:
            raise ValueError("season.jsonl の行の順が揃わない")
    masks = [rule_search._mask(frame, [cond]) for cond in labeled]
    matrix = rule_search._masks_to_matrix(masks, frame.height)
    if matrix.shape != (len(labeled), len(rows)):
        raise ValueError("ビット行列の形が条件数と行数に合わない")
    bits = [[bool(matrix[i, j]) for j in range(len(rows))] for i in range(len(labeled))]
    arr = np.asarray(bits, dtype=bool)
    regions = []
    for pattern in _patterns(len(labeled)):
        selected = np.ones(len(rows), dtype=bool)
        for i, on in enumerate(pattern):
            selected &= arr[i] if on else ~arr[i]
        regions.append(_overlap_region(pattern, labeled, [int(i) for i in np.flatnonzero(selected)]))
    return _overlap_result(rows, labeled, bits, regions)
