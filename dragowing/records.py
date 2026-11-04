"""結果ディレクトリの JSONL を、記録の順のまま読む。"""
from __future__ import annotations

import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"結果が読めない: {path.name}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def select_items(items: list[dict], present: dict[str, bool], ids: list[str] | None) -> list[dict]:
    """--id の順。式 ID で sets.jsonl が無いときは、結果に無いとは書かない。"""
    if not ids:
        return list(items)
    chosen = []
    # Index only conventional string IDs, and only for batches of at least eight lookups.
    # Unusual record IDs keep the original equality-based behavior.
    index = None
    if len(ids) >= 8 and all(type(item.get("id")) in (str, type(None)) for item in items):
        index = {}
        for item in items:
            index.setdefault(item.get("id"), []).append(item)
    for ident in ids:
        needed = "sets.jsonl" if ident.startswith("E") else "propositions.jsonl" if ident.startswith("P") else None
        if needed and not present.get(needed):
            raise FileNotFoundError(f"結果が読めない: {needed}")
        hit = index.get(ident, []) if index is not None else [item for item in items if item.get("id") == ident]
        if not hit:
            raise ValueError(f"{ident} は判定済みの結果にない")
        chosen.extend(hit)
    return chosen
