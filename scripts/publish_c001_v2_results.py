"""Publish the independently named c001 V2 replay results (stdlib only).

The V2 result catalog contains only outputs that were actually replayed
successfully. V1 fallbacks, skipped work, unavailable values, and failed
outputs stay in the verification/provenance artifact and are not promoted
into this catalog.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


SCHEMA = "c001-v2-results/1"
KINDS = (
    ("propositions.jsonl", "proposition", "P"),
    ("sets.jsonl", "expression", "E"),
)


def read_rows(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"not an object: {path}")
            rows.append(row)
    return rows


def public_id(prefix: str, source_id: str) -> str:
    if not isinstance(source_id, str) or not source_id:
        raise ValueError("missing source id")
    if not source_id.startswith(prefix) or not source_id[len(prefix):].isdigit():
        raise ValueError(f"unexpected source id for V2 publication: {source_id}")
    return f"V2-{source_id}"


def publish(audit: Path) -> dict:
    audit = audit.resolve()
    annotated = audit / "v2" / "annotated"
    out = audit / "v2" / "results"
    out.mkdir(parents=True, exist_ok=True)

    published = []
    seen_public = set()
    seen_source = set()
    by_kind = {}

    for filename, kind, prefix in KINDS:
        rows = read_rows(annotated / filename)
        count = 0
        for row in rows:
            source_id = row.get("id")
            verification = row.get("verification") or {}
            data = row.get("data")
            if verification.get("verification_status") != "replayed" or data is None:
                continue
            pid = public_id(prefix, source_id)
            if pid in seen_public or (kind, source_id) in seen_source:
                raise ValueError(f"duplicate V2 identity: {pid}")
            seen_public.add(pid)
            seen_source.add((kind, source_id))
            published.append({
                "schema": SCHEMA,
                "id": pid,
                "source_id": source_id,
                "kind": kind,
                "data": data,
                "verification": {
                    "verification_status": "replayed",
                    "verification_scope": verification.get("verification_scope"),
                    "source_validation": verification.get("source_validation"),
                    "input_verification": row.get("input_verification"),
                },
            })
            count += 1
        by_kind[kind] = count

    expected = sum(by_kind.values())
    if expected != len(published):
        raise ValueError("published result count mismatch")

    result_path = out / "results.jsonl"
    result_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in published),
        encoding="utf-8",
    )
    summary = {
        "schema": SCHEMA,
        "dataset_version": "V2",
        "published_results": len(published),
        "by_kind": by_kind,
        "id_scheme": "V2-<source_id>",
        "source_ids_preserved": True,
        "publication_rule": "only verification_status=replayed with non-null data",
        "excluded_from_v2_results": [
            "V1 inherited/skipped values",
            "unavailable values",
            "failed executions",
            "different/disappeared outputs",
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (out / "README.md").write_text(
        "# c001 V2 成果物\n\n"
        "このディレクトリは、保存済みV1入力を使って今回実際に再実行できた研究成果物だけを、"
        "V2用の公開IDで独立して並べたものです。\n\n"
        "- 命題: `V2-P1` のように公開し、元IDは `source_id=P1` として保持します。\n"
        "- 集合式: `V2-E1` のように公開し、元IDは `source_id=E1` として保持します。\n"
        "- V1継承・skip・値なし・失敗・不一致はこの一覧へ昇格させません。"
        "それらは `../annotated/` の検証来歴に残ります。\n"
        "- V2成果物であることは、元rawデータまで独立検証済みであることを意味しません。"
        "各行のverification_scopeを参照してください。\n",
        encoding="utf-8",
    )
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = publish(args.audit)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(64, f"Invalid V2 publication evidence: {exc}\n")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
