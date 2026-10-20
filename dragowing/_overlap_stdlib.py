"""load_overlap 専用の行評価。numpy/polars の代用品や import の差し替えではない。

Polars read_ndjson の先頭100行の型推論で結果が変わらない、同型のスカラー列だけ。
未対応の入力は native を明示的に選び直す。暗黙のフォールバックはしない。
"""
from __future__ import annotations

import json
from pathlib import Path

import math
import operator

_OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}


def read_rows(path: Path) -> list[dict]:
    """重複キーは標準 JSON decoder と NDJSON parser で解釈が違いうるので拒否。"""
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"stdlib overlap は重複キーを扱わない: {key}")
            obj[key] = value
        return obj

    return [json.loads(line, object_pairs_hook=unique)
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _kind(value):
    if value is None:
        return None
    if type(value) not in (bool, int, float, str):
        raise ValueError("stdlib overlap は bool/int/float/str/null の列だけ")
    if type(value) is str and any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError("stdlib overlap は Unicode surrogate を扱わない")
    if type(value) is int and not -(1 << 63) <= value < (1 << 63):
        raise ValueError("stdlib overlap の整数は Int64 の範囲だけ")
    if type(value) is float and not math.isfinite(value):
        raise ValueError("stdlib overlap は有限の数だけ")
    return type(value)


def _schema(rows):
    if not rows:
        raise ValueError("空の season.jsonl から型を推論できない")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("stdlib overlap は JSON オブジェクトの行だけ")
    schema = {}
    # native の既定 infer_schema_length=100 を越えて新しい列・型を受け入れない。
    for index, row in enumerate(rows):
        for col, value in row.items():
            if col not in schema:
                _kind(col)
            kind = _kind(value)
            if index < 100:
                kinds = schema.setdefault(col, set())
                if kind is not None:
                    kinds.add(kind)
            elif col not in schema or (kind is not None and kind not in schema[col]):
                raise ValueError(f"stdlib overlap の先頭100行以降で列・型が変わる: {col}")
    for col, kinds in schema.items():
        if not (len(kinds) <= 1 or kinds <= {int, float}):
            raise ValueError(f"stdlib overlap の列に異なる型がある: {col}")
    # native の team/season 順序確認が型変換で不一致にならない範囲。
    for row in rows:
        if type(row.get("team")) is not str or type(row.get("season")) is not int:
            raise ValueError("stdlib overlap は team が文字列、season が整数の行だけ")
    return schema


def condition_bits(rows: list[dict], conds: list[dict]) -> list[list[bool]]:
    """null / 欠損セルとの比較は全演算子で偽（!= null も偽）。"""
    schema = _schema(rows)
    bits = []
    for cond in conds:
        col, op, value = cond["col"], cond["op"], cond["value"]
        if col not in schema:
            raise ValueError(f"存在しない列: {col}（黙って偽にはしない）")
        if op not in _OPS:
            raise ValueError(f"演算子が条件にない: {op}")
        literal = _kind(value)
        kinds = schema[col]
        if literal is not None and kinds and not (
            kinds <= {int, float} and literal in (int, float)
            or kinds == {bool} and literal is bool
            or kinds == {str} and literal is str
        ):
            raise ValueError(f"stdlib overlap は比較の型変換を扱わない: {col}")
        floating = float in kinds or literal is float
        values = [row.get(col) for row in rows]
        if floating:
            # Float64 に丸めた巨大整数の境界は限定経路では扱わない。
            if any(type(v) is int and abs(v) > 2**53 for v in [value, *values]):
                raise ValueError("stdlib overlap の浮動小数比較は整数の絶対値が 2**53 以下だけ")
            values = [float(v) if v is not None else None for v in values]
            value = float(value) if value is not None else None
        compare = _OPS[op]
        bits.append([False if v is None or value is None else compare(v, value) for v in values])
    return bits
