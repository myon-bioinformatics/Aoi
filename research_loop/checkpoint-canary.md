# Manual checkpoint canary (disabled)

Related to Issue #71; this stage adds transport and offline regression evidence.
It does **not** enable repository variables, dispatch a research run, or add a
schedule. Live canary approval and scheduling remain separate decisions. The
question inbox is unchanged. NagoyAction's pinned subtree is unchanged.

## Gates and limits

`.github/workflows/research-canary.yml` has only `workflow_dispatch`. Its job
requires the exact `myon-bioinformatics/Aoi` repository, main, both original and
rerun actor equal to the repository owner, repository variable
`AOI_RESEARCH_ENABLED == '1'`, and dispatch input `enable_research: true`
(default **false**). This PR sets no variable and performs no dispatch.
The Python preflight independently checks these conditions, API repository ID,
default branch, workflow ID/path, run ID/attempt, and exact workflow/code SHA.
Checkout uses the event commit, checks tracked-tree cleanliness, and persists no
credentials. All external Actions are pinned by full commit SHA.

Permissions are `contents: read` and `actions: read`. The latter is necessary to
verify run/attempt/artifact metadata and download an artifact. No Issue, branch,
PR or repository writes are granted. Upload uses the Actions artifact service.
The worker subprocess receives only a minimal environment without API/artifact
credentials, user config or PYTHONPATH. Dependencies are installed from uv.lock
before the worker starts; the worker itself remains offline.

Canary choices are intentionally fixed: c001-chunichi, extended-v1, E1,
1–60 seconds and 1–5 committed units per dispatch. The public CLI's process-group
watchdog bounds hashing/evaluation/checkpoint I/O. The wrapper accepts watchdog
exit 124 only so an already committed checkpoint can be sealed. A first run
that times out before any checkpoint exists fails closed at sealing. Workflow
timeout is eight minutes, with two-minute step limits. Concurrency queues manual
canaries and does not automatically cancel an active one.

## Artifact protocol

Fresh runs leave all three source inputs blank. For an approved later resume,
the operator must specify **all three**: `source_run_id`, `source_attempt`, and
`source_artifact_id`. There is no newest-artifact search or cache fallback.

The source must be a successful, completed, owner-dispatched main run of the
same workflow and **exact same code commit**. Original and rerun actors must
both be the owner. Artifact API metadata must bind that run, repository ID,
head repository, main branch, code SHA, and the attempt-specific name
`research-checkpoint-<run_id>-<attempt>`. Expired/oversized artifacts or missing
GitHub SHA-256 digests are rejected before download. A source cannot be the
current run. API requests and downloads have time/byte limits and no retries.
Signed download redirects use a fresh request without the GitHub token.

The downloaded ZIP must match its GitHub API digest and contain exactly two
regular, unencrypted files: `checkpoint.json` (at most 32 MiB) and
`provenance.json` (at most 64 KiB). Paths, symlinks, duplicate members, code files,
oversized members, corrupted compressed data, duplicate JSON keys and nonfinite
constants are refused. Nothing is extracted, imported or executed from the ZIP.
The provenance record must match the verified source run/attempt, code/workflow
identity, workflow file hash, checkpoint file hash and current input manifest
hash. The checkpoint's own checksum and full manifest must also match. Only then
is its payload atomically written into a fresh state directory in RUNNER_TEMP.

The existing worker manifest additionally binds the selected bundle and its
input hashes, canonical cycle inputs, research implementation, lockfile,
pyproject, Python/Polars and platform. Exact runtime/platform drift is a refusal,
including different runner kernels; it is never normalized away. Cross-code or
cross-runtime migration is outside this protocol. Resume requires a new manual
fresh run after such drift. No downloaded code or dependency lockfile is used.

After a successful bounded worker step (or watchdog expiry with a valid committed
checkpoint), sealing rechecks current trust and inputs. Only the two verified
JSON files are uploaded, retained for 14 days. Runtime context/API tokens and
LOCK/STOP files are not included. Hard job cancellation, runner loss, or an upload
failure can lose progress since the last successful artifact; resume uses an
explicit earlier successful artifact. The protocol does not promise upload from
a killed runner and deliberately refuses artifacts from failed/cancelled runs.

## Offline verification

`tests/test_research_checkpoint.py` uses fixed GitHub API fixtures; it does not
contact GitHub or enable Actions. The real c001 public CLI is run for five units
continuously and for two units followed by seal/ZIP/download-validation/atomic
restore into a fresh directory plus three units. Checkpoint bytes must match.
It then completes the real E1 plan, transports that terminal checkpoint and
checks that a rerun commits zero units and changes neither bytes nor mtime.
Cycle-file hashes must remain unchanged. These are exploratory integration
results, not hypothesis confirmation or a live Actions canary.

Negative fixtures cover untrusted run/repository/actor/event/branch/code/workflow,
wrong source attempt, artifact identity/name/expiry/digest/size/origin, altered
provenance/manifest/checksum and unsafe/corrupt ZIP/JSON. Preflight gates,
credential stripping, bounds, redirect token handling and workflow restrictions
have separate regressions. Existing owner watchdog/atomic-write/inbox and Aoi
input-bundle regressions remain part of verification.

```bash
uv run --frozen pytest -q tests/test_research_checkpoint.py \
  tests/test_research_input_bundle.py tests/test_research_worker_gate.py \
  nagoyaction/tests/test_worker.py nagoyaction/tests/test_inbox.py
```

GitHub API references:
- https://docs.github.com/en/rest/actions/artifacts
- https://docs.github.com/en/rest/actions/workflow-runs

Before a live canary: review this PR and exact-head CI, then make a separate
enablement decision. Do not close Issue #71 on offline evidence alone. Proposed
live validation would be separate fresh 5-unit and 2+3-unit dispatches under the
same code/input/runtime, inspection of both checkpoint payloads, a terminal
rerun no-op, and a deliberate invalid source-ID rejection. Scheduling remains
absent even after any manual canary.
