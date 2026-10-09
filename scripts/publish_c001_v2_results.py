"""Publish V2 public IDs only after NagoyAction authenticates execution evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile

from c001_publication_policy import evaluate, gate

SCHEMA = "c001-v2-results/1"


def read_rows(path):
    return [gate.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def public_id(prefix: str, source_id: str) -> str:
    if prefix not in {"P", "E"} or not isinstance(source_id, str) or not re.fullmatch(prefix + r"[1-9][0-9]*", source_id):
        raise ValueError(f"unexpected source id for V2 publication: {source_id}")
    return f"V2-{source_id}"


def publish(audit: Path) -> dict:
    root = Path(audit).resolve()
    out = gate.safe_path(root, "v2/results")
    # A previous successful catalog must not survive a failed repeat invocation.
    if out.exists():
        if not out.is_dir() or any(p.name not in {"results.jsonl", "summary.json", "README.md"} or p.is_symlink() or not p.is_file() for p in out.iterdir()):
            raise ValueError("unexpected content in managed V2 results directory")
        shutil.rmtree(out)
    try:
        report, candidates = evaluate(root)
        gate.write_json(root / "publication-gate.json", report)
        if not report["allowed"]:
            return {"schema": SCHEMA, "published_results": 0, "publication_status": "blocked",
                    "failed_checks": report["failed_checks"], "exit_code": report["exit_code"]}
        published, seen = [], set()
        for kind, prefix, row in candidates:
            source_id = row["id"]
            pid = public_id(prefix, source_id)
            if pid in seen or row["data"].get("id") != source_id:
                raise ValueError(f"duplicate/mismatched V2 identity: {pid}")
            seen.add(pid)
            published.append({"schema": SCHEMA, "id": pid, "source_id": source_id,
                              "kind": kind, "data": row["data"], "verification": row["verification"],
                              "provenance": {"execution": report["identity"],
                                             "source_sha256": row["source_sha256"],
                                             "gate_sha256": gate.digest(root / "publication-gate.json")}})
        summary = {"schema": SCHEMA, "dataset_version": "V2", "published_results": len(published),
                   "by_kind": {k: sum(r["kind"] == k for r in published) for k in ("proposition", "expression")},
                   "publication_status": "published", "exit_code": 0,
                   "id_scheme": "V2-<source_id>", "source_ids_preserved": True,
                   "publication_rule": "NagoyAction same-execution evidence gate + c001 policy",
                   "verification_scope": "downstream_replay_on_V1_inputs"}
        out.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix=".v2-results-", dir=out.parent))
        try:
            (temp / "results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in published), encoding="utf-8")
            gate.write_json(temp / "summary.json", summary)
            (temp / "README.md").write_text(
                "# c001 V2 成果物\n\n"
                "公開IDはV2-P…/V2-E…、元IDはsource_idとdata.idに保持します。\n"
                "GHIで同定したrun/attempt・コード版と、NagoyActionが照合した入力・出力・比較証跡に基づく公開です。\n"
                "未解決差分・必須処理の失敗・証拠不足では、この通常カタログ全体を公開せず証跡を残します。\n"
                "反証・判断保留も正常な研究結果です。肯定的な結論だけを選別しません。\n"
                "保存済みV1入力での下流再判定であり、元rawまで独立検証した意味ではありません。\n"
                "公開時のゲート証跡は../../publication-gate.json、継承・スキップ情報は../annotated/です。\n",
                encoding="utf-8")
            temp.replace(out)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
        return summary
    except (OSError, ValueError, KeyError, TypeError) as exc:
        gate.write_json(root / "publication-gate.json", {"schema": "nagoyaction-publication-gate/1",
                        "allowed": False, "status": "invalid_evidence", "error": str(exc)})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = publish(args.audit)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(64, f"Invalid V2 publication evidence: {exc}\n")
    print(json.dumps(summary, ensure_ascii=False))
    return summary["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
