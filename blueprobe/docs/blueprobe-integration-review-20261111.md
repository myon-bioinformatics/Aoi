# BlueProbe #50 + #51 integration review

Prepared locally on 2026-11-11. No GitHub mutations have been performed.

## Inputs and ancestry

- main: 9b9088a638413a59819eea87a4590b4e6a5e441b
- #50: 314482ce8904e232736f8b361000961498fbbd22, feat/github-repository-observations
- #51: b521602885bbe426315ccb07381103231d02b33e, feat/standalone-url-observation
- Local branch: review/blueprobe-integrated, based on #50 with #51 merged using a merge commit. README merged automatically; neither implementation was discarded.
- QueRyu main: a8f2247 (cache_core.py is used as an external component, not copied into BlueProbe).

## Real snapshot parity

Source: https://myon-bioinformatics.github.io/myon-bioinformatics/data.json

- schema: parent-audit/1
- generated_at: 2026-11-11T01:08:19+00:00 (10:08:19 JST)
- SHA-256: b2dd3816252bd414fd1cd8254b9ca9b364421ade943761c884ed050285a2ca37
- 26 repositories, 50 records, errors=[], truncated=[].
- Every repository's selected raw rows, Issue/PR counts and observation timestamp match the saved input.
- BlueProbe: 0 Issues, 2 PRs. Both saved CI values are INCOMPLETE; these are preserved and are not replaced by current successful CI results.
- The current PR-triggered CI runs for the same heads were separately checked: #50 run 42824870205 success; #51 run 42835652115 success.

Failed collection, truncation, missing collection metadata and missing target produce unknown and CLI exit 2. Added checks also mark missing/invalid observation time or owner, and missing PR CI/head identity unknown while retaining the raw records and counts. CI FAILED/INCOMPLETE is an observation, not an adapter transport failure or a successful CI claim.

## URL and cache validation

- A local HTTP server exercises HTTP 200, 404, JSON stdout and --out equality, isolated single-file execution, and missing cache component detection before acquisition.
- QueRyu cache generation is tested against its actual cache_core.py API.
- After stopping the local HTTP server, Cache.snapshot reads verified cached HTML and reproduces the original digest and classification. Damaged gzip content raises CacheIntegrityError.
- A live Pages fetch returned 5,140 bytes, SHA-256 3b0c421d7599fec32f942a4636bb9ead558385b785debc6234fa784e1062c120. JSON output and cache were saved and offline readback reproduced the classification and digest.
- BlueProbe URL mode always fetches. QueRyu offline readback is cache reuse; BlueProbe cache-hit reuse is not implemented.

## Checks and reproduction

Full suite with the real snapshot and QueRyu checkout: Python 3.11.18, 460 passed / 17 skipped. Earlier Python 3.12.14 run before the optional real-snapshot test was added: 459 passed / 17 skipped. Skips are existing fixture/optional checks, not the enabled QueRyu cache integration tests.

```sh
PARENT_AUDIT_SNAPSHOT=../parent-audit.json QUERYU_ROOT=../QueRyu uv run --python 3.11 --group dev pytest -q
python blueprobe.py github ../parent-audit.json BlueProbe
PYTHONPATH=../QueRyu python blueprobe.py https://myon-bioinformatics.github.io/myon-bioinformatics/ --cache ../review-cache --out ../url-observation.json
```

## Scope and constraints

BlueProbe acquires and observes structure, and generates cache entries through QueRyu's component. QueRyu owns cache verification/provenance/reuse and extraction; xprobe owns bounded searches; ErrorRoadRunner diagnoses failures. The parent remains the GitHub collector and dashboard owner. No new collector, diagnosis engine, extraction engine or runtime Python dependency is added.

Remaining limits: external curl required; HTTP 200/UTF-8/10 MiB limit; no JavaScript rendering, HTTP header preservation, conditional requests or BlueProbe URL cache-hit reuse. Content-Type is not validated, so decodable content alone does not prove an HTML response. Snapshot observation time is validated but no freshness threshold is imposed. The generated single-file tool now includes the github tool; it does not package cache_core.py. Dashboard and ErrorRoadRunner handoff remain unimplemented.

## Proposed GitHub actions AFTER explicit approval

1. Refresh main and both PR heads; stop and reassess if reviewed inputs changed. Integrate a newer main locally if needed and rerun relevant tests.
2. Push the prepared integration commit to existing #50 branch feat/github-repository-observations with a normal fast-forward push. No force-push or new PR.
3. Retarget #51 to feat/github-repository-observations so #50 is the sole main-targeting PR; update existing #50 title/body with the combined scope and validation.
4. Wait for CI on the exact new #50 head; inspect status checks and unresolved reviews. Local tests are not a substitute for this new CI run.
5. Merge #50 using a merge commit and the expected head SHA. Preserve #51 ancestry; do not squash the integration.
6. Verify #50 and #51 merge state and ancestry on main, final main CI, and remaining open PR count. If #51 remains open despite full ancestry inclusion, close it as integrated with a reference to the #50 merge; do not discard unintegrated changes.

Representative commands (HEAD must be resolved and checked immediately before merge):

```sh
git push origin review/blueprobe-integrated:feat/github-repository-observations
gh pr edit 51 --repo myon-bioinformatics/BlueProbe --base feat/github-repository-observations
gh pr checks 50 --repo myon-bioinformatics/BlueProbe --watch
gh pr merge 50 --repo myon-bioinformatics/BlueProbe --merge --match-head-commit REVIEWED_INTEGRATION_SHA
```
