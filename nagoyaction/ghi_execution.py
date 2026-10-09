"""Read-only GHI adapter: bind this Actions attempt and both actual checkouts.

GHI is loaded from a pinned separate checkout, not copied or reimplemented.
This observer runs in setup; replay, evidence checking and publication are offline.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path

from publication_gate import write_json, identity

GHI_COMMIT = "fc2c527257b12eb99c00637bbae74f8988fd6bf4"
GHI_BLOB = "57f96181fecaef0a6f19bf5052b93d9bdcab69c5"


def load_ghi(directory):
    path = Path(directory).resolve() / "gh_identity.py"
    if path.is_symlink():
        raise ValueError("GHI source must be a regular file")
    raw = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != GHI_BLOB:
        raise ValueError("GHI source blob differs from reviewed pin")
    spec = importlib.util.spec_from_file_location("_aoi_pinned_ghi", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.local_identity(cwd=str(path.parent), env={})["sha"] != GHI_COMMIT:
        raise ValueError("GHI checkout differs from reviewed pin")
    return module


def observe(ghi, harness, research, env):
    repository = ghi.repo(env["GITHUB_REPOSITORY"])
    run, attempt = int(env["GITHUB_RUN_ID"]), int(env["GITHUB_RUN_ATTEMPT"])
    if run < 1 or attempt < 1:
        raise ValueError("invalid Actions run/attempt")
    # Do not let GITHUB_SHA mask the separate research checkout's actual SHA.
    h = ghi.local_identity(cwd=str(harness), env={})
    r = ghi.local_identity(cwd=str(research), env={})
    endpoint = f"repos/{repository}/actions/runs/{run}/attempts/{attempt}"
    data = ghi.request("GET", endpoint, transport="auto", timeout=30)
    if (type(data.get("id")) is not int or type(data.get("run_attempt")) is not int
            or data["id"] != run or data["run_attempt"] != attempt
            or data.get("repository", {}).get("full_name") != repository
            or data.get("head_sha") != h["sha"] or h["sha"] != env["GITHUB_SHA"]):
        raise ValueError("GHI observation does not match this run/attempt/checkout")
    return {"schema": "nagoyaction-execution/1", "mode": "github_actions",
            "observer": "gh_identity", "ghi_sha": GHI_COMMIT, "ghi_blob": GHI_BLOB,
            "repository": repository, "run_id": run, "run_attempt": attempt,
            "workflow_id": data.get("workflow_id"), "workflow_path": data.get("path"),
            "event": data.get("event"), "head_sha": data["head_sha"],
            "harness_sha": h["sha"], "research_sha": r["sha"],
            "observation_scope": "identity_only_not_final_workflow_success"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghi", type=Path, required=True)
    parser.add_argument("--harness", type=Path, default=Path.cwd())
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.audit.exists():
            raise ValueError("audit directory must be new for each execution")
        ghi = load_ghi(args.ghi)
        result = observe(ghi, args.harness.resolve(), args.research.resolve(), os.environ)
        args.audit.mkdir(parents=True)
        write_json(args.audit / "execution-identity.json", result)
        identity(args.audit)
    except Exception as exc:
        parser.exit(64, f"Execution identity unavailable: {exc}\n")
    print("GHI execution identity captured; no research source was fetched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
