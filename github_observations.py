"""Extract repository-scoped issue and CI observations from a saved parent audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from blueprobe import new_report


def observe(snapshot: dict, repository: str) -> dict:
    """Observe the existing parent-audit/1 records without network access or diagnosis."""
    if not isinstance(snapshot, dict) or snapshot.get("schema") != "parent-audit/1":
        raise ValueError("expected parent-audit/1 snapshot")
    if not isinstance(repository, str) or not repository or "/" in repository:
        raise ValueError("repository must be the repository name in the snapshot")
    if not isinstance(snapshot.get("records"), list) or not isinstance(snapshot.get("repositories"), list):
        raise ValueError("snapshot records and repositories must be lists")
    report = new_report()
    if repository not in snapshot["repositories"]:
        report["unknown"].append({"key": repository, "reason": "repository not listed in snapshot"})
    truncated = snapshot.get("truncated")
    if not isinstance(truncated, list) or not all(isinstance(name, str) for name in truncated):
        report["unknown"].append({"key": repository, "reason": "snapshot truncation list unavailable or invalid"})
    elif repository in truncated:
        report["unknown"].append({"key": repository, "reason": "repository observation truncated"})
    errors = snapshot.get("errors")
    if not isinstance(errors, list):
        report["unknown"].append({"key": repository, "reason": "snapshot error list unavailable"})
    elif any(not isinstance(error, dict) or not isinstance(error.get("repository"), str) for error in errors):
        report["unknown"].append({"key": repository, "reason": "invalid collection error entries"})
    else:
        relevant = [error for error in errors if error["repository"] == repository]
        if relevant:
            report["unknown"].append({"key": repository, "reason": "repository collection failed", "raw": relevant})
    for index, item in enumerate(snapshot["records"]):
        if not isinstance(item, dict):
            report["unknown"].append({"key": str(index), "reason": "invalid record", "raw": item})
            continue
        if item.get("repository") != repository:
            continue
        kind = item.get("kind")
        if kind not in ("issue", "pr") or not isinstance(item.get("id"), str):
            report["unknown"].append({"key": str(index), "reason": "unsupported record", "raw": item})
            continue
        report["records"].append({"key": item["id"], "raw": item,
                                  "derived": {"repository": repository, "kind": kind,
                                              "observed_ci": item.get("ci"),
                                              "labels": item.get("labels"),
                                              "head_sha": item.get("head_sha")}})
        report["counts"][kind] += 1
    return {"schema": "github-repository-observations/1", "generated_at": snapshot.get("generated_at"),
            "owner": snapshot.get("owner"), "repository": repository, "report": report}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("repository", help="repository name as listed in parent-audit/1")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = observe(snapshot, args.repository)
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 2 if result["report"]["unknown"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
