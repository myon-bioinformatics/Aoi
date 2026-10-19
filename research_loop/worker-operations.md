# Aoi research worker: offline implementation, activation deferred

The unsupported scheduled worker was removed on 2026-10-18 after failed runs.
The question inbox remains independently operational. This change implements the
missing worker in its owner repository, NagoyAction; **no research workflow,
manual Actions entry point or schedule is restored, and no variable is enabled**.

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
  dispatch on trusted main; there is no such live workflow in this PR.
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
  Persistence is durable local storage; cross-runner artifact restore/upload is
  still a requirement for any future Actions canary, not an implemented promise.
- Minimal child environment excludes credentials. Python audit hooks reject network,
  subprocesses and filesystem writes. This is trusted-code defense in depth, not
  an OS sandbox for hostile Python/native code or forged checkpoint artifacts.

## What continues unchanged

`.github/workflows/research-inbox.yml`, `pipelines/inbox.toml`, `intake`, the inbox
state branch, and its `/ask`, `/status`, `/explore`, `/stop` behavior are preserved.
The inbox `/stop` does not stop this worker; use its dedicated `STOP` file.

## Current c001 input blocker (observed during integration)

A real offline CLI probe on `c001-chunichi` with `--seed E1` refused to initialize:
`OFF_SHORT: from の命題がない: P147`. The root `sets.toml` references P147 and
other extended propositions, while the canonical `propositions.toml` ends at
P114. No checkpoint was created and no source/results file was modified.

The extended definitions and derived season columns are separately preserved in
`from-cycle-001/`, according to that directory's README. Do not silently combine
them with the fixed canonical holdout inputs or overwrite those inputs. A coherent,
explicitly selected research input bundle with matching sets/propositions/data is
a prerequisite for a real c001 canary. The subprocess replay tests use a coherent
isolated fixture; they do not establish that today's canonical c001 registry is
executable. This is an activation blocker, not a successful research run.

## Review and staged reactivation decision

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
