# CI label completion allowlist audit (2026-11-03)

Reviewed PR head `f5cf51ea2665da8fc43f6693bd0432be7522e88b` and main
`94fd7c8c6ccefd4a2e2227606a6f51ced36862a6`. Their workflow inventories
and upstream trigger definitions agree (only the label workflow differs).

`workflow_run.workflows` now lists 23 exact workflow names. Self completion
and question-inbox completion are excluded; all other current workflows are
included, including manual/scheduled-only workflows. Completion is only a
wake-up: the scanner still validates Actions provenance and the latest PR head
twice, then rechecks the head before an ADD. No removal operation is introduced.

## Inventory and upstream triggers

Path filters and branch filters in upstream files remain unchanged.
The table lists event types, not a claim that every upstream run concerns a PR.

| Workflow | Upstream events | Completion wake-up |
| --- | --- | --- |
| Action uses | pull_request, push, schedule | allowed |
| Browser startup validation | pull_request, workflow_dispatch | allowed |
| c001 offline replay audit | workflow_dispatch, push | allowed |
| cache keepalive | schedule, workflow_dispatch | allowed |
| CDN module experiment | pull_request, workflow_dispatch | allowed |
| CI failure label (add only) | schedule, workflow_run, pull_request_target, workflow_dispatch | excluded |
| CI | push, pull_request, workflow_dispatch | allowed |
| cycle c001 (chunichi) | push, workflow_dispatch | allowed |
| DRAgoWing reports | push, pull_request, workflow_dispatch | allowed |
| Links | push, pull_request, workflow_dispatch | allowed |
| LittleBit holdout drift | pull_request, push, workflow_dispatch | allowed |
| Minimal stdlib distributions | pull_request, push, workflow_dispatch | allowed |
| Nano research environment comparison | pull_request, workflow_dispatch | allowed |
| numpy_min backends | pull_request, workflow_dispatch | allowed |
| requests tqdm biopython surface | pull_request, workflow_dispatch | allowed |
| Shared Python launcher | pull_request, push | allowed |
| Aoi manual research checkpoint canary | workflow_dispatch | allowed |
| Aoi question inbox | issue_comment, schedule, workflow_dispatch | excluded |
| Season simulator | push, pull_request, workflow_dispatch | allowed |
| Shared tool lock | pull_request, push, schedule | allowed |
| Shrink linalg experiment | pull_request, workflow_dispatch | allowed |
| Shrink module experiment | pull_request, workflow_dispatch | allowed |
| Shrink polars experiment | pull_request, workflow_dispatch | allowed |
| Stdlib feasibility survey | pull_request, workflow_dispatch | allowed |
| Third-party min experiment | pull_request, workflow_dispatch | allowed |

## Validation and limits

- `python tests/test_ci_status_label.py`: 19 passed; standard library only.
- Exact workflow security contract plus independent name/inventory comparison
  rejects self/inbox entries, duplicates, missing names and wildcard notation.
- actionlint 1.7.12: label workflow configuration passed (shellcheck/pyflakes disabled).
- `git diff --check`: passed.
- Six-hour cron, PR target types, default-branch checkout, failure conclusions,
  permissions and ADD/HOLD implementation are unchanged by this repair.

These checks validate configuration and offline safety behavior only. The
workflow_run listener must exist on the default branch before its corrected
completion filter can be observed in production. After an approved merge,
correlate an allowed upstream completed run with a label run whose event is
workflow_run and inspect SCAN/ADD/HOLD logs; record both run IDs and timestamps.
Do not treat PR CI success or manual dispatch as proof of completion delivery.
The six-hour scan remains the fallback for excluded workflows, missed events,
and workflow_run chain limits; GitHub schedules do not guarantee a hard deadline.

Reference: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run
