# CI label wake-up audit (2026-11-03 JST)

Base: 94fd7c8c6ccefd4a2e2227606a6f51ced36862a6.

## Observed history
Latest repository Actions page (100 records), captured on 2026-11-03 JST:
2026-11-02 11:12:57–23:32:54 UTC. 50 label schedules and 50 question-inbox schedules.
The latest 12 label jobs (20:47:46–23:32:54 UTC) were individually inspected.
All succeeded, executed add_ci_label.py, and emitted no numbered ADD/HOLD lines:
0 runs inspected a PR, 12 runs had no open PR targets. This follows from the
successful script's complete open_pulls() enumeration and unconditional per-PR
output; workflow_runs.pull_requests=[] alone is NOT evidence of no targets.
The remaining 38 label runs were not log-audited; do not classify them as empty.

Audited run IDs:
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41546270807
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41544225975
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41542487851
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41540236036
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41538201386
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41536031391
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41534075473
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41531584382
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41529380771
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41526942491
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41524988457
- https://github.com/myon-bioinformatics/Aoi/actions/runs/41522460839

## Alternatives and selection
| Mode | Scheduled starts/day (configuration) | Detection after failure becomes visible |
| --- | ---: | --- |
| Existing polling | 96 | nominal 0–15 min + scheduler/runner/API delay |
| pull_request only | 0 | misses failures completing after PR event; fork write token unsuitable |
| workflow_run only | 0 | completion wake-up; misses failures already present on reopened PR, event chain limits |
| Selected hybrid | 4 + event starts | completion or PR wake-up normally; fallback nominal 0–6 h + platform delay |

Use completed workflow_run (including reruns) and opened/reopened/synchronize/
ready_for_review pull_request_target as wake-ups. Always checkout the default
branch; never execute PR code, consume run artifacts, or trust event conclusions
as authorization. All open PRs are rescanned, so empty fork association arrays
do not drop a PR. Existing double latest-head observations, Actions app/suite/run/
workflow provenance, final head read, ADD-only POST and all HOLD rules stay intact.

Exclude the label workflow from its own completion subscription to avoid loops.
Exclude the high-frequency question-inbox workflow from this subscription to
avoid replacing empty polling with empty inbox wake-ups. Its file is unchanged.
Any relevant failure from that workflow, deep workflow chains, suppressed PR
events, or missed/delayed API visibility is still covered by the full six-hour
scan and manual dispatch. This preserves eventual coverage, but exceptional
fallback-only detection is slower than the old nominal 15 minutes.
No finite upper latency bound is claimed for GitHub schedules.

## Historical replay versus live measurement
For the same 100-record observation window, new schedule slots would be
12:23 and 18:23 UTC (2 versus 50 old label starts, 96% fewer).
There were no non-inbox/non-label completions on that page, hence no
workflow_run wake-ups in this replay. This is a deterministic counterfactual,
not an observed production reduction; PR activity events were not reconstructed.
For an idle full day, 96 -> 4 scheduled starts is a 95.83% reduction.
Total starts on active days = 4 scheduled + matching workflow completions +
selected PR events + manual dispatches; success completions create skipped
workflow runs, not label runner jobs. Do not report all starts as runner jobs.

No failure occurred in the audited sample, so no observed before/after detection
latency is available. Event-path detection waits for the whole workflow to
complete (a failed job in a still-running workflow may first be seen by fallback).
The new SCAN open_prs=N output supports direct future empty/nonempty counts.
After merge, compare equal-duration windows using run created_at, label job
started_at, first confirmed failing completion, and label timeline timestamp.
Do not infer latency from run success or workflow_run.updated_at alone.

Validation: python tests/test_ci_status_label.py (18 tests), including existing
provenance/head/rerun races and new empty/nonempty scanner and workflow trust
boundary tests.

References:
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

