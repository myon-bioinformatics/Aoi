"""Offline publication gate and same-execution evidence recorder (stdlib only).

Identity observation belongs to the GHI adapter; research rules belong to the
caller. A saved gate report is evidence, never a bearer token authorizing writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _constant(value):
    raise ValueError(f"non-finite JSON: {value}")


def loads(text):
    value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    # This also rejects overflow literals such as 1e999, including nested ones.
    json.dumps(value, allow_nan=False)
    return value


def read_json(path):
    return loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def safe_path(root, name):
    root = Path(root).resolve()
    rel = Path(name)
    if rel.is_absolute() or not rel.parts or any(p in {"..", "."} for p in rel.parts):
        raise ValueError(f"unsafe evidence path: {name}")
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"symlink evidence: {name}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"escaped evidence: {name}")
    return path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(root, env=None):
    value = read_json(safe_path(root, "execution-identity.json"))
    if not isinstance(value, dict) or value.get("schema") != "nagoyaction-execution/1":
        raise ValueError("missing execution identity schema")
    if value.get("mode") != "github_actions" or value.get("observer") != "gh_identity":
        raise ValueError("unobserved execution identity")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value.get("repository", "")):
        raise ValueError("invalid repository identity")
    for name in ("run_id", "run_attempt", "workflow_id"):
        if type(value.get(name)) is not int or value[name] < 1:
            raise ValueError(f"invalid identity {name}")
    for name in ("head_sha", "harness_sha", "research_sha", "ghi_sha"):
        if not re.fullmatch(r"[a-f0-9]{40}", value.get(name, "")):
            raise ValueError(f"invalid identity {name}")
    if value["head_sha"] != value["harness_sha"]:
        raise ValueError("run head does not match harness checkout")
    if not isinstance(value.get("workflow_path"), str) or not value["workflow_path"]:
        raise ValueError("missing workflow path")
    env = os.environ if env is None else env
    if env.get("GITHUB_ACTIONS") == "true":
        expected = {"repository": env.get("GITHUB_REPOSITORY"),
                    "run_id": int(env.get("GITHUB_RUN_ID", "0")),
                    "run_attempt": int(env.get("GITHUB_RUN_ATTEMPT", "0")),
                    "head_sha": env.get("GITHUB_SHA")}
        if any(value[key] != val for key, val in expected.items()):
            raise ValueError("stale execution identity: repository/run/attempt/SHA")
    return value


def seal(root, stage, names, returncode, env=None):
    """Called by record_command after the child, including on nonzero exit."""
    root = Path(root).resolve()
    identity(root, env)
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", stage) or type(returncode) is not int:
        raise ValueError("invalid stage receipt")
    files = {}
    for name in names:
        path = safe_path(root, name)
        files[name] = digest(path) if path.is_file() else None
    payload = {"schema": "nagoyaction-stage/1", "stage": stage,
               "identity_sha256": digest(root / "execution-identity.json"),
               "returncode": returncode, "files": files}
    dest = safe_path(root, f"stage-evidence/{stage}.json")
    if dest.exists():
        raise ValueError(f"stage evidence already exists: {stage}")
    write_json(dest, payload)
    return payload


def record_command(root, stage, names, command, runner=subprocess.run):
    identity(root)
    if safe_path(root, f"stage-evidence/{stage}.json").exists():
        raise ValueError("cannot overwrite a previous stage receipt")
    try:
        code = runner(command, check=False).returncode
    except OSError:
        seal(root, stage, names, 64)
        raise
    seal(root, stage, names, code)
    return code


def inspect(root, required_files, env=None):
    """Authenticate mandatory stage coverage, bytes and the execution binding."""
    root = Path(root).resolve()
    observed = identity(root, env)
    ident_hash = digest(root / "execution-identity.json")
    hashes, stages = {}, {}
    for stage, names in required_files.items():
        path = safe_path(root, f"stage-evidence/{stage}.json")
        receipt = read_json(path)
        if (not isinstance(receipt, dict) or receipt.get("schema") != "nagoyaction-stage/1" or receipt.get("stage") != stage
                or receipt.get("identity_sha256") != ident_hash):
            raise ValueError(f"stage identity mismatch: {stage}")
        if type(receipt.get("returncode")) is not int:
            raise ValueError(f"invalid return code: {stage}")
        files = receipt.get("files")
        if not isinstance(files, dict) or not set(names) <= files.keys():
            raise ValueError(f"incomplete evidence coverage: {stage}")
        for name, expected in files.items():
            path = safe_path(root, name)
            if not isinstance(expected, str) or not path.is_file() or digest(path) != expected:
                raise ValueError(f"evidence hash mismatch or missing file: {stage}/{name}")
            hashes[name] = expected
        stages[stage] = receipt["returncode"]
    return {"identity": observed, "identity_sha256": ident_hash,
            "stage_returncodes": stages, "evidence_sha256": hashes}


def decide(evidence, checks):
    """Generic fail-closed gate. All named checks must explicitly pass."""
    if not checks or any(type(v) is not bool for v in checks.values()):
        raise ValueError("gate checks must be explicit nonempty booleans")
    failed = [key for key, ok in checks.items() if not ok]
    return {"schema": "nagoyaction-publication-gate/1", "allowed": not failed,
            "status": "allowed" if not failed else "blocked",
            "failed_checks": failed, "checks": checks, **evidence}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["record"])
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--evidence", nargs="+", required=True)
    args, command = parser.parse_known_args(argv)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("child command required after --")
    try:
        return record_command(args.audit, args.stage, args.evidence, command)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(64, f"Invalid stage evidence: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
