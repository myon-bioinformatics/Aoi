"""条件集合と B クラスの重なり。マスクは rule_search のビット行列。

空の比較（JSON の null）は真に数えない。rule_search._mask と同じである。
件数は bool 行列の和で、丸めない。
"""
from __future__ import annotations

import json
from pathlib import Path

import operator

OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}

from .forms import _atom
from .records import read_jsonl

B_COND = {"col": "upper_half", "op": "==", "value": False}


def _engines():
    import sys

    if "propositions" not in sys.modules:
        here = Path(__file__).resolve()
        for root in (here.parent, *here.parents):
            logic = root / "pythdragoras"
            if (logic / "propositions.py").is_file():
                path = str(logic)
                if path not in sys.path:
                    sys.path.insert(0, path)
                break
    import propositions
    import rule_search

    return rule_search, propositions


def is_b(cond: dict) -> bool:
    return cond.get("col") == "upper_half" and cond.get("op") == "==" and cond.get("value") is False


def label_of(cond: dict) -> str:
    if is_b(cond):
        return "B (upper_half==false)"
    return _atom(cond)


def _key(cond: dict) -> tuple:
    return (cond["col"], cond["op"], json.dumps(cond["value"], ensure_ascii=False, sort_keys=True))


def parse_cond(text: str) -> dict:
    try:
        col, op, raw = text.split(",", 2)
    except ValueError:
        raise ValueError(f"条件の書き方は col,op,値（JSON）。例: rd,>,0 。受け取ったもの: {text}") from None
    if op not in OPS:
        raise ValueError(f"演算子が条件にない: {op}")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"値は JSON: {text}") from exc
    return {"col": col, "op": op, "value": value}


def default_conditions(items: list[dict], rows: list[dict]) -> list[dict]:
    """propositions の if をファイル順に見て、列がある原子を 2 個まで。最後に B クラスを足す。"""
    have = set(rows[0]) if rows else set()
    chosen: list[dict] = []
    seen = set()
    for item in items:
        for cond in item.get("if") or []:
            if not isinstance(cond, dict) or cond.get("col") not in have or cond.get("op") not in OPS:
                continue
            if "value" not in cond:
                continue
            key = _key(cond)
            if key in seen:
                continue
            seen.add(key)
            chosen.append({"col": cond["col"], "op": cond["op"], "value": cond["value"]})
            if len(chosen) == 2:
                break
        if len(chosen) == 2:
            break
    if not any(is_b(cond) for cond in chosen):
        if "upper_half" not in have:
            raise ValueError("upper_half が season.jsonl にない")
        chosen.append(dict(B_COND))
    if not 2 <= len(chosen) <= 3:
        raise ValueError("条件集合は 2 個か 3 個にする（B クラスを含む）")
    return chosen


def finalize_conditions(user: list[dict] | None, items: list[dict], rows: list[dict]) -> list[dict]:
    if not user:
        return default_conditions(items, rows)
    chosen = [{"col": c["col"], "op": c["op"], "value": c["value"]} for c in user]
    if not any(is_b(cond) for cond in chosen):
        if not rows or "upper_half" not in rows[0]:
            raise ValueError("upper_half が season.jsonl にない")
        chosen.append(dict(B_COND))
    if not 2 <= len(chosen) <= 3:
        raise ValueError("条件集合は 2 個か 3 個にする（B クラスを含む）")
    return chosen


def _patterns(n_sets: int):
    for bits in range(2**n_sets):
        yield tuple(bool(bits & (1 << i)) for i in range(n_sets))


def load_overlap(path: Path, conds: list[dict], *, backend: str = "native") -> dict:
    """条件行列と領域の件数。backend="stdlib" だけがライブラリ不要の限定経路。"""
    if backend not in ("native", "stdlib"):
        raise ValueError(f"overlap backend は native か stdlib: {backend}")
    path = Path(path)
    labeled = [{**cond, "label": label_of(cond)} for cond in conds]
    if backend == "stdlib":
        from ._overlap_stdlib import condition_bits, read_rows

        rows = read_rows(path)
        bits = condition_bits(rows, labeled)
    else:
        import numpy as np
        import polars as pl

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
    columns = []
    for cond in labeled:
        if cond["col"] not in columns:
            columns.append(cond["col"])
    if "upper_half" not in columns:
        columns.append("upper_half")
    units = []
    for index, row in enumerate(rows):
        units.append(
            {
                "index": index,
                "unit": f"{row['team']}-{row['season']}",
                "league": row["league"],
                "team": row["team"],
                "team_name": row["team_name"],
                "season": row["season"],
                "upper_half": row["upper_half"],
                "in_set": [bits[i][index] for i in range(len(labeled))],
                "values": {col: row.get(col) for col in columns},
            }
        )
    regions = []
    if backend == "native":
        arr = np.asarray(bits, dtype=bool)
    for pattern in _patterns(len(labeled)):
        if backend == "stdlib":
            indexes = [j for j in range(len(rows)) if all(bits[i][j] == on for i, on in enumerate(pattern))]
        else:
            selected = np.ones(len(rows), dtype=bool)
            for i, on in enumerate(pattern):
                selected &= arr[i] if on else ~arr[i]
            indexes = [int(i) for i in np.flatnonzero(selected)]
        name = "外" if not any(pattern) else " ∧ ".join(
            labeled[i]["label"] if on else f"¬({labeled[i]['label']})" for i, on in enumerate(pattern)
        )
        regions.append(
            {
                "name": name,
                "bits": list(pattern),
                "count": len(indexes),
                "unit_index": indexes,
            }
        )
    if sum(region["count"] for region in regions) != len(rows):
        raise ValueError("領域の件数の和が行数と合わない")
    return {"conditions": labeled, "columns": columns, "units": units, "regions": regions, "matrix": bits}
