"""Opt-in offline Aoi explorer. No Issue writes, fetching, LLMs or publication.

The supervisor owns checkpoints; disposable children evaluate one deterministic
unit. Only trusted Aoi code may be used. See docs/worker.md for the threat model.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import tempfile
import time

MAX_BYTES = 32 * 1024 * 1024
MAX_SECONDS = 300
TERMINAL = {"completed", "bounded"}


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def authorize(env):
    if env.get("AOI_RESEARCH_ENABLED") != "1":
        raise ValueError("worker disabled: AOI_RESEARCH_ENABLED=1 is required")
    repo = env.get("GITHUB_REPOSITORY", "")
    actor = env.get("GITHUB_ACTOR") or env.get("AOI_RESEARCH_ACTOR", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("GITHUB_REPOSITORY is required")
    allowed = json.loads(env.get("AOI_RESEARCH_ALLOWED_ACTORS") or "[]")
    if not isinstance(allowed, list) or any(not isinstance(a, str) or not a for a in allowed):
        raise ValueError("AOI_RESEARCH_ALLOWED_ACTORS must be a JSON login array")
    if not actor or actor.casefold() not in {repo.split('/')[0].casefold(), *(a.casefold() for a in allowed)}:
        raise ValueError("research actor is not allowed")
    if env.get("GITHUB_ACTIONS") == "true":
        if (env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
                or env.get("GITHUB_REF") != "refs/heads/main"):
            raise ValueError("worker requires manual dispatch on trusted main")
    return {"repository": repo, "actor": actor}


def snapshot(root, cycle, seed):
    files = [cycle / name for name in
             ("analysis.toml", "propositions.toml", "sets.toml", "outputs/season.jsonl")]
    files += [root / "uv.lock", root / "pyproject.toml"]
    for folder in ("research_loop", "pythdragoras"):
        files += sorted((root / folder).glob("*.py"))
    result = {}
    for path in files:
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f"missing or unsafe research input: {path}")
        # Hash in chunks; large data are never loaded into the supervisor at once.
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        result[path.relative_to(root).as_posix()] = h.hexdigest()
    return {"schema": 1, "files": result, "cycle": cycle.relative_to(root).as_posix(),
            "seed": seed, "worker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(),
            "polars": importlib.metadata.version("polars"), "platform": platform.platform()}


def atomic_checkpoint(path, value):
    data = encode({"payload": value, "sha256": digest(value)}) + b"\n"
    if len(data) > MAX_BYTES:
        raise ValueError("checkpoint exceeds 32 MiB; previous checkpoint retained")
    fd, name = tempfile.mkstemp(prefix=".checkpoint-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def load_checkpoint(path):
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("oversized checkpoint")
    record = json.loads(path.read_bytes())
    value = record["payload"]
    if record["sha256"] != digest(value):
        raise ValueError("checkpoint checksum mismatch")
    return value


@contextlib.contextmanager
def lock_state(path):
    # Fail closed outside POSIX. A local lock is released by the kernel on crash.
    import fcntl
    fd = os.open(path / "LOCK", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("another worker owns this state directory") from exc
        yield
    finally:
        os.close(fd)


def child_env():
    # No GH_TOKEN, credential helpers, proxy, PYTHONPATH or user site settings.
    env = {"PATH": os.defpath, "HOME": "/nonexistent", "PYTHONHASHSEED": "0",
           "PYTHONDONTWRITEBYTECODE": "1", "POLARS_MAX_THREADS": "1", "LANG": "C.UTF-8"}
    for key in ("AOI_RESEARCH_ENABLED", "AOI_RESEARCH_ACTOR", "AOI_RESEARCH_ALLOWED_ACTORS",
                "GITHUB_REPOSITORY", "GITHUB_ACTOR", "GITHUB_ACTIONS", "GITHUB_EVENT_NAME", "GITHUB_REF"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def evaluate(root, cycle, seed, state, timeout):
    request = encode({"seed": seed, "state": state})
    # A regular temporary output avoids an unbounded PIPE allocation.
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "_step",
             "--root", str(root), "--cycle", cycle.name],
            input=request, stdout=output, stderr=errors,
            cwd=root, env=child_env(), timeout=timeout, check=False,
        )
        if result.returncode:
            errors.seek(0)
            raise RuntimeError("evaluation failed: " + errors.read(4000).decode("utf-8", errors="replace"))
        if output.tell() > MAX_BYTES:
            raise ValueError("evaluation exceeds checkpoint limit")
        output.seek(0)
        return json.load(output)


def _readonly_audit(event, args):
    if event.startswith("socket.") or event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.fork"):
        raise PermissionError("offline evaluator forbids network and child processes")
    if event == "open":
        mode, flags = args[1:3]
        if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
            raise PermissionError("offline evaluator forbids file writes")
    if event in ("os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.link", "os.symlink", "os.chmod", "os.truncate"):
        raise PermissionError("offline evaluator forbids filesystem mutation")


def step(root, cycle):
    # Internal protocol. It never writes a checkpoint; parent remains the sole writer.
    request = json.load(sys.stdin)
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(root / "research_loop"), str(root / "pythdragoras")]
    sys.addaudithook(_readonly_audit)
    from exploration import Explorer, plan
    spec = plan(request["seed"], cycle)
    state = request["state"]
    explorer = Explorer(cycle, spec)
    if state is None:
        state = explorer.initial({})
    else:
        if state["plan"] != spec:
            raise ValueError("checkpoint plan mismatch")
        explorer.advance(state, seconds=MAX_SECONDS, max_steps=1)
    sys.stdout.write(encode(state).decode("utf-8"))


def run(args, *, evaluate_unit=evaluate, clock=time.monotonic):
    started = clock()
    identity = authorize(os.environ)
    if not 0 < args.seconds <= MAX_SECONDS or not 1 <= args.max_steps <= 1000:
        raise ValueError("seconds must be 1..300 and max-steps 1..1000")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.cycle):
        raise ValueError("invalid cycle")
    root = args.root.resolve()
    cycle = root / "cycles" / args.cycle
    raw_state_dir = args.state_dir.absolute()
    state_dir = raw_state_dir.resolve()
    # Never allow state paths to overwrite source, results or cycle definitions.
    if state_dir.is_relative_to(root) and state_dir != root / ".research-worker":
        raise ValueError("in-tree state must be .research-worker")
    if any(p.is_symlink() for p in (raw_state_dir, *raw_state_dir.parents, cycle, cycle.parent)):
        raise ValueError("symlinked state/cycle directory")
    state_dir.mkdir(parents=True, exist_ok=True)
    if any(p.is_symlink() for p in state_dir.rglob("*")):
        raise ValueError("symlink in worker state")
    checkpoint = state_dir / "checkpoint.json"
    deadline = started + args.seconds
    stop = [False]
    previous = {}
    def request_stop(signum, frame):
        stop[0] = True
    for sig in (signal.SIGTERM, signal.SIGINT):
        previous[sig] = signal.signal(sig, request_stop)
    try:
        with lock_state(state_dir):
            inputs = snapshot(root, cycle, args.seed)
            payload = load_checkpoint(checkpoint) if checkpoint.exists() else None
            if payload and payload["manifest"] != inputs:
                raise ValueError("research inputs/runtime changed; use a new state directory")
            state = payload["state"] if payload else None
            units = 0
            reason = "step_limit"
            while units < args.max_steps:
                if stop[0] or (state_dir / "STOP").exists():
                    reason = "stopped"
                    break
                if state and state["status"] in TERMINAL:
                    reason = "completed"
                    break
                remaining = deadline - clock()
                if remaining <= 0:
                    reason = "deadline"
                    break
                try:
                    updated = evaluate_unit(root, cycle, args.seed, state, remaining)
                except subprocess.TimeoutExpired:
                    reason = "deadline"
                    break
                # Detect changes during evaluation before committing any output.
                if snapshot(root, cycle, args.seed) != inputs:
                    raise ValueError("research inputs changed during evaluation")
                atomic_checkpoint(checkpoint, {"manifest": inputs, "state": updated})
                state = updated
                units += 1
            report = {"reason": reason, "units": units, "cursor": state["cursor"] if state else 0,
                      "status": state["status"] if state else "not_started",
                      "manifest_sha256": digest(inputs), "authorized": identity}
            print(json.dumps(report, ensure_ascii=False))
            return report
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def supervise(argv, seconds):
    """Hard wall-clock watchdog includes hashing, JSON encoding and fsync.

    Kill the entire process group, including an uncooperative evaluator. Atomic
    rename leaves either the previous checkpoint or the complete new one.
    """
    child = subprocess.Popen([sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                              "_run", *argv[1:]], start_new_session=True)
    previous = {}
    def forward(signum, frame):
        try:
            child.send_signal(signum)
        except ProcessLookupError:
            pass
    for sig in (signal.SIGTERM, signal.SIGINT):
        previous[sig] = signal.signal(sig, forward)
    try:
        try:
            child.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:
            print("worker wall-clock deadline reached; resume the last committed checkpoint", file=sys.stderr)
            return 124
        return child.returncode
    finally:
        # Also clean up after unexpected supervisor exceptions. A separate process
        # group must never outlive the watchdog that enforces its wall-clock limit.
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait()
        for sig, handler in previous.items():
            signal.signal(sig, handler)



def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("worker", "_step", "_run"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--cycle", default=os.environ.get("AOI_RESEARCH_CYCLE", ""))
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument("--seed", default="all", help="registered expression ID or all")
    parser.add_argument("--state-dir", type=Path)
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argv)
    try:
        if args.mode == "_step":
            authorize(os.environ)
            step(args.root.resolve(), args.root.resolve() / "cycles" / args.cycle)
        else:
            authorize(os.environ)
            if not 0 < args.seconds <= MAX_SECONDS or not 1 <= args.max_steps <= 1000:
                raise ValueError("seconds must be 1..300 and max-steps 1..1000")
            if os.name != "posix":
                raise ValueError("worker currently requires POSIX process groups and file locks")
            if args.mode == "worker":
                return supervise(argv, args.seconds)
            args.state_dir = args.state_dir or args.root / ".research-worker"
            run(args)
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        parser.exit(1, f"worker refused/failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
