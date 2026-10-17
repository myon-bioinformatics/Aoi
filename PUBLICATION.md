# c001 publication evidence gate

GHI observes which GitHub execution is running. NagoyAction binds producer
receipts to that execution and checks evidence bytes offline. c001 owns the
research-specific release rules; the publisher does not invent a second gate.

## Identity and trust boundary

`ghi_execution.py` imports the canonical single file from a separate checkout at
`gh_identity@fc2c527257b12eb99c00637bbae74f8988fd6bf4`. Its Git blob is checked before
import. No GitHub HTTP transport is copied into Aoi. The adapter uses GHI
`request()` for a GET of the current run attempt, and `local_identity(env={})`
for the two actual checkouts. The harness SHA and research SHA are intentionally
different. The Actions environment must match repository, run ID, attempt and
harness SHA; missing observation is not success. Only `actions: read` is added.

Observation runs during setup, before the offline research stages. It does not
claim that an in-progress workflow has already succeeded. GHI source acquisition,
checkout and dependency installation are network setup; NPB acquisition is not
rerun. The gate and publisher require no network or GHI installation themselves.

`execution-identity.json` and `stage-evidence/{stage}.json` bind the same execution
to the exact files emitted by freeze, replay, compare and annotate. Every stage
is recorded around the real child invocation, with its actual exit code. A retry
cannot overwrite a producer receipt. Mandatory file coverage, SHA-256, missing
files, symlinks, stale attempts and contradictory receipts fail closed. The gate
checks all mandatory stages, not just whichever observations happened to exist.

These hashes are consistency/provenance checks within a trusted runner, not a
cryptographic attestation against an attacker who can rewrite the entire bundle.
Offline inspection of an exported bundle establishes internal consistency, not
that the bundle belongs to a new/current Actions execution. In Actions the live
environment is also checked. Do not fabricate an execution identity to upgrade
an old artifact into a new replay.

## c001 release rule

The current bounded policy requires question, sets and judge to have succeeded,
complete comparison, zero selected semantic/annual formula differences, and
matching annotation/raw values. It also compares every structured field. Only
proposition `meta.code_version` drift to the declared research checkout, from a
valid earlier SHA, is classified as execution-revision provenance; it is counted
and preserved, not erased. All other full-field drift holds publication.

The first gate is deliberately conservative: one unresolved difference or failed
required stage holds the **entire normal catalog**. It does not yet compute a
dependency graph to certify unrelated subsets. Original values, failed outputs,
annotations and the gate explanation remain in the evidence artifact. Explicit
V1/skipped/unavailable/failed/different annotation rows are never promoted.

`Refuted`, `Inconclusive` and other negative research verdicts are still normal
research results. Release eligibility is not a vote on whether a proposition is
true. The public IDs remain `V2-P…` / `V2-E…`, with unchanged `source_id` and
`data.id`. Successful release still means downstream replay on saved V1 inputs,
not independent validation of all original raw data.

The publisher always evaluates the gate itself. Merely supplying a saved
`publication-gate.json` with `allowed: true` does not authorize publication.
A failed repeated invocation removes its previous managed normal catalog so
stale success files cannot survive in the uploaded artifact. Only that dedicated
three-file catalog is managed; original research and annotated evidence are not
rewritten. Gate errors return 64; unresolved differences return 1; success is 0.

## Evidence and tests

The workflow preserves `publication-gate.json` even on failure, together with
execution identity, stage receipts, V1/V2 and the annotated evidence. On success
`v2/results/` additionally contains the public catalog, per-result evidence hashes
and a summary. Artifact retention and upload are independent of release approval.

Run the offline contract tests with:

```sh
python -S -m unittest discover -s nagoyaction/tests -p 'test_c001_*.py' -v
```

The workflow additionally imports the pinned real GHI module and runs its help
smoke before observing the actual run. Unit tests mock only GHI observations;
they do not count a mock as a live GitHub verification or a research replay.
