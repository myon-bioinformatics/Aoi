"""Data-only checkpoint transport for the disabled, manual trusted-main canary.

GitHub API metadata is the trust anchor; self-reported provenance is not one.
No downloaded files are imported or extracted. Only two bounded JSON records
are read and a verified checkpoint is atomically installed outside the checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib

REPOSITORY = "myon-bioinformatics/Aoi"
WORKFLOW = ".github/workflows/research-canary.yml"
CYCLE, BUNDLE, SEED = "c001-chunichi", "extended-v1", "E1"
MAX_CHECKPOINT = 32 * 1024 * 1024
MAX_ARCHIVE = MAX_CHECKPOINT + 1024 * 1024
MAX_META = 64 * 1024
ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode()


def decode(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("nonfinite JSON number")
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def positive(value):
    require(isinstance(value, str) and re.fullmatch(r"[1-9][0-9]{0,18}", value),
            "expected positive decimal ID")
    return int(value)


def worker(root=ROOT):
    spec = importlib.util.spec_from_file_location("canary_worker", root / "nagoyaction/inbox/worker.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(root=ROOT):
    return worker(root).bundle_snapshot(root, root / "cycles" / CYCLE, SEED, BUNDLE)


def checkpoint(data, expected):
    require(len(data) <= MAX_CHECKPOINT, "oversized checkpoint")
    record = decode(data)
    require(isinstance(record, dict) and set(record) == {"payload", "sha256"}, "checkpoint envelope")
    payload = record["payload"]
    require(isinstance(payload, dict) and set(payload) == {"manifest", "state"}, "checkpoint payload")
    require(record["sha256"] == sha(encode(payload)), "checkpoint checksum")
    require(payload["manifest"] == expected, "input/code/runtime manifest mismatch")
    require(isinstance(payload["state"], dict), "checkpoint state must be data")
    return payload


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    def __init__(self, token):
        require(bool(token), "read-only GitHub token required")
        self.token = token
        self.deadline = time.monotonic() + 100
        self.opener = urllib.request.build_opener(NoRedirect)

    def request(self, url, *, authenticated, limit):
        remaining = self.deadline - time.monotonic()
        require(remaining > 0, "transport deadline")
        headers = {"User-Agent": "Aoi-checkpoint-canary", "Accept": "application/vnd.github+json"}
        if authenticated:
            require(url.startswith("https://api.github.com/repos/" + REPOSITORY + "/"), "API origin")
            headers["Authorization"] = "Bearer " + self.token
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        request = urllib.request.Request(url, headers=headers)
        with self.opener.open(request, timeout=min(20, remaining)) as response:
            require(int(response.headers.get("Content-Length", "0")) <= limit, "response size")
            data = response.read(limit + 1)
            require(len(data) <= limit, "response size")
            return data

    def get(self, path):
        return decode(self.request("https://api.github.com/repos/" + REPOSITORY + "/" + path,
                                   authenticated=True, limit=1024 * 1024))

    def archive(self, artifact_id):
        url = f"https://api.github.com/repos/{REPOSITORY}/actions/artifacts/{artifact_id}/zip"
        try:
            return self.request(url, authenticated=True, limit=MAX_ARCHIVE)
        except urllib.error.HTTPError as exc:
            if exc.code != 302:
                raise
            location = exc.headers.get("Location", "")
            parsed = urllib.parse.urlsplit(location)
            require(parsed.scheme == "https" and parsed.hostname and not parsed.username
                    and not parsed.password and parsed.port in (None, 443), "unsafe artifact redirect")
            # A fresh unauthenticated request, with redirects disabled, never
            # forwards the repository token to the signed blob URL.
            return self.request(location, authenticated=False, limit=MAX_ARCHIVE)


def verify_run(run, context, *, source=False):
    repo = run["repository"]
    require(repo["full_name"] == REPOSITORY and repo["id"] == context["repository_id"]
            and run["head_repository"]["id"] == repo["id"], "run repository/fork")
    require(run["event"] == "workflow_dispatch" and run["head_branch"] == "main"
            and run["head_sha"] == context["head_sha"], "run event/branch/code")
    require(run["workflow_id"] == context["workflow_id"]
            and run["path"] == WORKFLOW, "run workflow")
    owner = REPOSITORY.split("/")[0]
    require(run["actor"]["login"] == owner and run["triggering_actor"]["login"] == owner,
            "run actor")
    if source:
        require(run["status"] == "completed" and run["conclusion"] == "success", "source not successful")


def current_context(api, env, root=ROOT):
    owner = REPOSITORY.split("/")[0]
    require(env.get("GITHUB_ACTIONS") == "true" and env.get("GITHUB_REPOSITORY") == REPOSITORY,
            "trusted Actions repository required")
    require(env.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
            and env.get("GITHUB_REF") == "refs/heads/main", "manual trusted-main required")
    require(env.get("AOI_RESEARCH_ENABLED") == "1" and env.get("CANARY_ENABLE") == "true",
            "explicit repository and dispatch enablement required")
    require(env.get("GITHUB_ACTOR") == owner and env.get("GITHUB_TRIGGERING_ACTOR") == owner,
            "owner-only canary")
    code = env.get("GITHUB_SHA", "")
    require(re.fullmatch(r"[0-9a-f]{40}", code), "code SHA")
    require(env.get("GITHUB_WORKFLOW_REF") == f"{REPOSITORY}/{WORKFLOW}@refs/heads/main"
            and env.get("GITHUB_WORKFLOW_SHA") == code, "workflow revision")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=10).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                    cwd=root, text=True, timeout=10)
    require(head == code and not dirty, "checkout must equal trusted code")
    repo = api.get("")
    require(repo["full_name"] == REPOSITORY and not repo["fork"] and repo["default_branch"] == "main"
            and repo["id"] == positive(env["GITHUB_REPOSITORY_ID"]), "repository identity")
    flow = api.get("actions/workflows/research-canary.yml")
    require(flow["path"] == WORKFLOW and flow["state"] == "active", "workflow identity")
    context = {"repository": REPOSITORY, "repository_id": repo["id"], "head_sha": code,
               "workflow_id": flow["id"], "workflow_path": WORKFLOW,
               "workflow_sha256": sha((root / WORKFLOW).read_bytes()),
               "run_id": positive(env["GITHUB_RUN_ID"]),
               "run_attempt": positive(env["GITHUB_RUN_ATTEMPT"])}
    run = api.get(f"actions/runs/{context['run_id']}/attempts/{context['run_attempt']}")
    verify_run(run, context)
    require(run["id"] == context["run_id"] and run["run_attempt"] == context["run_attempt"], "current attempt")
    return context


def artifact_name(run_id, attempt):
    return f"research-checkpoint-{run_id}-{attempt}"


def verify_artifact(metadata, source, context, artifact_id):
    verify_run(source, context, source=True)
    origin = metadata["workflow_run"]
    require(metadata["id"] == artifact_id and metadata["expired"] is False
            and 0 < metadata["size_in_bytes"] <= MAX_ARCHIVE, "artifact identity/size/expiry")
    require(metadata["name"] == artifact_name(source["id"], source["run_attempt"]), "artifact attempt/name")
    for key, value in {"id": source["id"], "repository_id": context["repository_id"],
                       "head_repository_id": context["repository_id"], "head_branch": "main",
                       "head_sha": context["head_sha"]}.items():
        require(origin[key] == value, "artifact origin")
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", metadata.get("digest", "")), "artifact digest missing")


def seal(data, context, expected):
    checkpoint(data, expected)
    return encode({"schema": 1, "origin": context, "checkpoint_sha256": sha(data),
                   "manifest_sha256": sha(encode(expected))})


def open_archive(data, metadata, source, context, expected):
    verify_artifact(metadata, source, context, metadata["id"])
    require(len(data) == metadata["size_in_bytes"] and len(data) <= MAX_ARCHIVE
            and "sha256:" + sha(data) == metadata["digest"], "archive digest mismatch")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        require(len(entries) == 2 and {p.filename for p in entries} == {"checkpoint.json", "provenance.json"},
                "archive must contain only checkpoint and provenance")
        for entry in entries:
            limit = MAX_CHECKPOINT if entry.filename == "checkpoint.json" else MAX_META
            kind = stat.S_IFMT(entry.external_attr >> 16)
            require(not entry.is_dir() and kind in (0, stat.S_IFREG) and not entry.flag_bits & 1
                    and entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                    and 0 < entry.file_size <= limit, "unsafe archive member/size")
        # Explicit read bounds constrain decompressor allocation even when a
        # forged directory understates file_size. Never call unbounded read().
        def read_member(name):
            entry = archive.getinfo(name)
            with archive.open(entry) as member:
                value = member.read(entry.file_size + 1)
            require(len(value) == entry.file_size, "archive member length mismatch")
            return value
        try:
            record = read_member("checkpoint.json")
            provenance = decode(read_member("provenance.json"))
        except (zipfile.BadZipFile, zlib.error) as exc:
            raise ValueError("corrupt archive member") from exc
    origin = {**context, "run_id": source["id"], "run_attempt": source["run_attempt"]}
    require(provenance == decode(seal(record, origin, expected)), "provenance mismatch")
    return record


def restore(api, context, expected, state, run_id, attempt, artifact_id):
    require(run_id != context["run_id"], "cannot restore own run")
    source = api.get(f"actions/runs/{run_id}/attempts/{attempt}")
    require(source["id"] == run_id and source["run_attempt"] == attempt, "source attempt")
    metadata = api.get(f"actions/artifacts/{artifact_id}")
    verify_artifact(metadata, source, context, artifact_id)
    record = open_archive(api.archive(artifact_id), metadata, source, context, expected)
    require(not state.exists(), "restore destination already exists")
    state.mkdir(mode=0o700)
    # All metadata, archive and record validation precede the first state write.
    worker().atomic_checkpoint(state / "checkpoint.json", checkpoint(record, expected))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run", "seal"))
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    env = os.environ
    # State/output are fixed RUNNER_TEMP children, never artifact-selected paths.
    temp = Path(env["RUNNER_TEMP"]).resolve()
    require(args.state == temp / "aoi-research-state" and args.output == temp / "aoi-research-export",
            "unexpected state/output directory")
    require(not any(p.is_symlink() for p in (args.state, args.output, temp)), "symlinked transport path")
    if args.mode in ("prepare", "seal"):
        api = GitHub(env.get("GH_TOKEN"))
        context = current_context(api, env)
        expected = manifest()
        if args.mode == "prepare":
            require(not args.state.exists() and not args.output.exists(), "fresh transport directories required")
            source = [env.get(name, "") for name in ("SOURCE_RUN_ID", "SOURCE_ATTEMPT", "SOURCE_ARTIFACT_ID")]
            require(all(source) or not any(source), "supply all three source IDs or none")
            if all(source):
                restore(api, context, expected, args.state, *(positive(s) for s in source))
        else:
            require(not args.output.exists(), "export already exists")
            path = args.state / "checkpoint.json"
            require(not path.is_symlink() and path.is_file() and path.stat().st_size <= MAX_CHECKPOINT,
                    "missing/unsafe checkpoint")
            data = path.read_bytes()
            provenance = seal(data, context, expected)
            args.output.mkdir(mode=0o700)
            (args.output / "checkpoint.json").write_bytes(data)
            (args.output / "provenance.json").write_bytes(provenance)
    else:
        # No API credential, runtime artifact credential or inherited user config
        # reaches the supervisor/evaluator. Authorization is checked in prepare.
        seconds, steps = positive(env["CANARY_SECONDS"]), positive(env["CANARY_STEPS"])
        require(seconds <= 60 and steps <= 5, "canary limit: 60 seconds / 5 units")
        clean = {"PATH": os.defpath, "HOME": "/nonexistent", "LANG": "C.UTF-8",
                 "PYTHONDONTWRITEBYTECODE": "1", "POLARS_MAX_THREADS": "1"}
        for key in ("AOI_RESEARCH_ENABLED", "GITHUB_ACTIONS", "GITHUB_REPOSITORY", "GITHUB_ACTOR",
                    "GITHUB_EVENT_NAME", "GITHUB_REF"):
            clean[key] = env.get(key, "")
        result = subprocess.run([sys.executable, str(ROOT / "nagoyaction/inbox/worker.py"), "worker",
            "--root", str(ROOT), "--cycle", CYCLE, "--input-bundle", BUNDLE, "--seed", SEED,
            "--seconds", str(seconds), "--max-steps", str(steps), "--state-dir", str(args.state)],
            env=clean, cwd=ROOT, timeout=seconds + 10, check=False)
        require(result.returncode in (0, 124), "worker failed; do not publish state")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError,
            zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"checkpoint transport refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
