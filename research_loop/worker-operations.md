# Aoi research worker: activation deferred

The unsupported scheduled worker was removed on 2026-10-18 after failed runs.
The question inbox remains independently operational. This change implements the
missing worker in its owner repository, NagoyAction. A separate manual checkpoint
canary workflow is now implemented with two disabled-by-default gates; **no
variable is enabled, no research run is dispatched and no schedule is restored**.
See [checkpoint protocol](../docs/research-checkpoint-canary.md) for transport,
review requirements, offline evidence and remaining live-validation limits.

## Implementation and ownership

NagoyAction PR #3 implements `inbox/inbox.py worker`, which dispatches separately
from `intake`. Aoi imports that exact child history using a non-squash subtree
pull. `nagoyaction/` must remain byte/tree-identical to the registered child SHA.
Do not patch the child copy in Aoi. Merge the owner PR first, repin to its final
main SHA if it differs, and merge this integration with a merge commit (not
squash/rebase) so the second parent remains reachable.

The fixed pipeline now runs an offline 60-second worker rather than the stale
`worker --seconds 18000` command. It installs no dependencies and fetches no data.
The implemented scope is registered-set Explorer expansion, not LLM orchestration,
feedback generation, automatic seed selection or publication.

## Safety and restart contract

See [NagoyAction worker operations](../nagoyaction/docs/worker.md) for commands
and the complete threat model. Key points:

- `AOI_RESEARCH_ENABLED=1` plus a separate allowed actor is required. Inbox
  configuration/actors never enable exploration. Actions accepts only manual
  dispatch on trusted main. The manual canary additionally requires the repository
  owner as both original/rerun actor and a false-by-default dispatch opt-in.
- Public CLI watchdog bounds the whole process group to 1–300 seconds, including
  input hashing and checkpoint I/O. Deadline exits 124; TERM/INT are forwarded,
  and descendants are killed/reaped on exit.
- A single atomic, fsynced, checksummed checkpoint stores the plan, candidates,
  cursor, dedup table and results together. Interrupted units are retried without
  duplicate commits; completed reruns do nothing. Local locks exclude overlap.
- Code, cycle data/configuration, lockfile and runtime fingerprints must match on
  resume. Each unit checks inputs again before committing results. Source data and
  official propositions remain read only. Results remain exploratory/unconfirmed.
- Worker state is `.research-worker/`, separate from inbox `.research-state/`.
  The disabled manual canary adds explicit source-run/attempt/artifact restore and
  upload, with API provenance and input/code/workflow checks before state writes.
- Minimal child environment excludes credentials. Python audit hooks reject network,
  subprocesses and filesystem writes. This is trusted-code defense in depth, not
  an OS sandbox for hostile Python/native code or forged checkpoint artifacts.

## What continues unchanged

`.github/workflows/research-inbox.yml`, `pipelines/inbox.toml`, `intake`, the inbox
state branch, and its `/ask`, `/status`, `/explore`, `/stop` behavior are preserved.
The inbox `/stop` does not stop this worker; use its dedicated `STOP` file.

## Explicit c001 research input bundle

The canonical c001 holdout inputs remain unchanged and are not repaired by
replacing them with later research files. Their shared set registry still cannot
initialize with canonical P1–P114. Use an explicit selection:
`--cycle c001-chunichi --input-bundle extended-v1`.

The [versioned bundle](../cycles/c001-chunichi/input-bundles/README.md) selects the
preserved extended history's 210 propositions, derived season data and complete
analysis configuration, plus the explicitly pinned cycle-level registry. All 32
set references, 31 expressions, 211 required columns, 168 unique units, configuration
and exclusions are preflighted before an initial checkpoint. It records hashes
of all selected files and the bundle manifest and refuses changed inputs on resume.
The 2020 exclusion retains its reason and removes 12 rows (156 included).

Real offline c001 CLI regressions now exercise initialization and evaluation,
unchanged source hashes, and equality between five uninterrupted units and two
plus three resumed units. These are bounded integration probes, not completed
research or independent hypothesis confirmation. Literal null observations remain
unknown; missing columns, invalid scalar types and nonfinite values are refused.

Issue #71's **Actions activation gate remains open**. PR #72 completed the input
correction. The next transport stage implements the disabled manual workflow and
provenance binding; live artifact/canary verification remains pending separate
approval. No repository variables or live execution settings are changed.

## Review and staged reactivation decision

Input bundle review is a prerequisite, not authorization to reactivate Actions.

1. NagoyAction exact-head CI and independent safety review must pass first.
2. Check subtree parent history and tree equality; run Aoi CI and inbox regressions.
3. Keep research disabled through both PRs. Next stage, only after review: a short
   explicit manual canary with contents:read, no Issue permissions, trusted-main
   code, and durable checkpoint artifact upload/restore bound to trusted runs.
4. Inspect interrupted/resumed replay evidence before proposing longer execution.
   Scheduling is a separate decision; this PR does not reintroduce it.

Validation command:

```bash
uv run --frozen pytest -q tests/test_research_worker_gate.py \
  nagoyaction/tests/test_worker.py nagoyaction/tests/test_inbox.py tests/test_research_loop.py
```
