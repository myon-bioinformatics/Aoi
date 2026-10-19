# Opt-in offline research worker (first stage)

`inbox/inbox.py worker` dispatches to `inbox/worker.py` **before** importing the
question reader. `intake`, the inbox state branch, `/ask`, `/explore` and `/stop`
keep their existing behavior. The worker has no Issue API or publication path.
It automatically expands registered sets through Aoi's trusted
`research_loop/exploration.py` and PythDRagoras. Feedback/HTML generation, LLMs,
new data acquisition and arbitrary research tasks are not connected.

## Explicit enablement

POSIX (Linux/macOS) and Python 3.11+ are required. Install Aoi's locked dependencies
first, then run from the trusted Aoi checkout (NagoyAction lives at `nagoyaction/`):

```bash
uv sync --frozen
export GITHUB_REPOSITORY=myon-bioinformatics/Aoi
export AOI_RESEARCH_ACTOR=myon-bioinformatics
export AOI_RESEARCH_ENABLED=1
uv run --frozen --offline python nagoyaction/inbox/inbox.py worker \
  --cycle c001-chunichi --seed E1 --seconds 30 --max-steps 5
```

The actor must be the repository owner or appear in the separate JSON-array
`AOI_RESEARCH_ALLOWED_ACTORS`. Neither `AOI_INBOX_ISSUE` nor the inbox allowlist
activates research. Environment settings are an operator interlock on a local
machine, not authentication against a hostile local user. On Actions, only
`workflow_dispatch` on `refs/heads/main` is accepted; do not run PR code or copy
executable code from a results/state ref. Repository settings and the reviewed
workflow enforce the trust boundary. No live schedule is introduced here.

## Bounds and checkpoints

The CLI watchdog places all work (including input hashing and checkpoint I/O) in
a separate process group with a hard wall-clock timeout. `--seconds` is 1–300;
the default is 60. At the deadline the group is killed, the CLI exits 124, and the
last committed checkpoint remains resumable. Process launch/OS scheduling adds
small overhead. Each disposable evaluator initializes a plan or advances exactly
one candidate. `--max-steps` is 1–1000 (default 20, including initialization).
The existing plan limits depth to 3 and candidates to 50,000. A 32 MiB checkpoint
limit fails closed without replacing the previous checkpoint.

The supervisor writes a single self-contained `checkpoint.json`: temporary file,
file fsync, atomic rename, directory fsync. Its SHA-256 detects accidental
corruption; it is not a signature. Keep the state directory on a durable local
filesystem with atomic rename/fsync semantics. A local `flock` excludes concurrent
writers and releases automatically on crash. No network persistence is implied:
CI artifacts must be uploaded and explicitly restored by an independent trusted
workflow. Never mix this directory with the inbox state branch.

Rerun the same command and state directory to resume. The default is Aoi's
`.research-worker/`; other state directories must be outside the source tree.
A completed checkpoint is a no-op. A unit interrupted before commit is evaluated
again; no partial candidate or duplicate result is appended. Create `STOP` in the
state directory to stop between units; delete it to resume. SIGTERM/SIGINT request
the same cooperative stop (a running unit may last until the watchdog deadline).
The inbox `/stop` command remains unrelated and does not stop this worker.

## Reproducibility and authority

The checkpoint records hashes of cycle definitions and `season.jsonl`, every
Python file in `research_loop/` and `pythdragoras/`, this worker, `uv.lock`, and
`pyproject.toml`, plus Python/Polars versions and the platform. Seed, plan,
candidates, cursor, semantic deduplication table and results are persisted.
Inputs are checked again after each evaluation before commit. A changed input,
worker, runtime or platform refuses resume; retain the old state and use a new
directory for a new experiment. Compare results only under the recorded manifest.
Outputs retain `exploratory: true` and `independently_confirmed: false`.

Child processes receive a minimal environment without tokens, proxies or user
Python paths, use isolated Python and one Polars thread, and install an audit hook
rejecting Python networking, subprocesses and file writes. Only fixed, reviewed
Aoi modules are imported; checkpoints contain data, never commands or module
paths. This is defense in depth for trusted code, **not an OS security sandbox**
for malicious Python/native libraries. Do not accept untrusted source trees or
untrusted checkpoint artifacts. Official propositions and inputs are read only.

## Reactivation stages

1. Owner tests against a pinned Aoi checkout, CI on the exact reviewed head, and
   independent safety review. Keep autonomous execution disabled.
2. Import NagoyAction into Aoi with non-squash subtree history, verify tree equality,
   run inbox regressions and real restart/timeout/immutability integration tests.
3. Only after both PRs pass review: enable a short manually dispatched canary with
   read-only repository permissions and durable checkpoint artifact handling.
4. Inspect checkpoint/replay evidence before considering longer runs or scheduling.

A successful offline test or PR merge does not enable autonomous execution.
