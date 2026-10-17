# Aoi research worker: deferred activation

As of 2026-10-18, **the autonomous research worker is not connected to the
question inbox**. Aoi's scheduled `research-worker.yml` was removed after
three failed runs on 2026-10-17 (39040261209, 39040998282, 39041854188).

## Failure and containment

- The former worker workflow ran if `AOI_RESEARCH_ENABLED == '1'` **or**
  `AOI_INBOX_ISSUE` was set. The latter exists for the question inbox and
  must never activate autonomous exploration.
- `nagoyaction/pipelines/research.toml` calls
  `nagoyaction/inbox/inbox.py worker --seconds 18000`, but the current
  `inbox.py` accepts only `intake`. It fails with argparse exit code 2.
- The unsupported pipeline is retained in the separately managed NagoyAction
  subtree as historical/integration work; it is **not an executable worker**.
  Do not run it in Actions until its entry point is actually implemented.
- Remove the scheduled workflow, rather than marking unsupported exploration
  successful or enabling it merely because the inbox Issue is configured.
  `AOI_RESEARCH_ENABLED` alone does not activate anything in this deferred
  state. There is also no manual Actions path to the unsupported worker.

## What continues to run

`.github/workflows/research-inbox.yml` remains intact. It uses
`AOI_INBOX_ISSUE`, `nagoyaction/pipelines/inbox.toml`, and the `intake`
CLI to service `/ask` and `/status`. `/explore` explicitly says it has not
been introduced; `/stop` has nothing to stop. No changes are made to its
trusted-main code checkout, data-only results checkout, or state branch.

`research_loop/autonomous.py`, `exploration.py`, `feedback.py`,
`neighbor_checks.py`, and `dragowing_inspect.py` have offline component
implementations and tests. See `research_loop/README.md`. They are **not**
end-to-end orchestration, persistent worker scheduling, or a working `worker`
CLI. Restored modules must not be confused with a production-safe worker.

## Before considering reactivation

1. Design and implement an explicit worker entry point in the owner repository
   (NagoyAction), and bring its subtree changes into Aoi using the existing
   subtree synchronization process; do not edit the child copy in Aoi ad hoc.
2. Add bounded execution, durable checkpoints, idempotent restart, safe
   permissions and actor gating, reproducibility checks, and offline tests for
   the whole integration (not just research_loop units).
3. Keep inbox enablement separate: use explicit opt-in for research, not
   `AOI_INBOX_ISSUE`. Test absent/disabled/enabled combinations, including
   manual and scheduled triggers; keep the question inbox operational.
4. Update `tests/test_research_worker_gate.py` in the same PR, review its CI
   and Actions behavior, and only then add back scheduling.

Regression checks: `python -m pytest -q tests/test_research_worker_gate.py
nagoyaction/tests/test_inbox.py tests/test_research_loop.py`.
