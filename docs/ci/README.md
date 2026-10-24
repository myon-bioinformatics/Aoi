# CI

The run definition is `.github/workflows/ci.yml`.

- **Aoi**: at run time, resolves main's SHA with `git ls-remote https://github.com/myon-bioinformatics/Aoi refs/heads/main`, checks the repository id on the public page, then checks out to `.test-deps/aoi`. The resolved SHA is left in the job summary. The ref can be overridden with `aoi_ref` in `workflow_dispatch`. Commit SHAs are not pinned in files.
- **Parent vendor dispatch**: `vendor-dispatch` runs in parallel with the test matrix. It resolves the parent main's SHA with `git ls-remote`, checks the repository id `638801160` on the public page, then checks out to `.vendor-dispatch-tools`. The resolved SHA is left in the job summary. Checking is `pilot/vendor_dispatch.py --manifest vendor.lock.json` (verify; CI doesn't record). Skips are only reported; a mismatch with a recorded digest fails. This repository has no `python -S` `vendor_sync.py` check. `vendor.lock.json` is `vendor-lock/1`, and its registered rows are currently empty.
- **mcp-toolcall-lab**: `LAB_SHA` is a snapshot for verifying past patterns. It is fetched by SHA and used as verification test data. This check fails on every event.
- **Source hashes**: if a floating source-hash check is added, it only reports on `pull_request` and fails on push to `main` and on `schedule`. Aoi's source hashes are not recorded.
- **JUnit XML**: `pytest -q --junitxml=reports/junit.xml`, artifact name `junit-py<python>`, retained 14 days. Aggregation is the org parent's `reusable-junit-identity.yml`.
- **lint**: ruff is not added. `python -m compileall` checks syntax only.
- **Runtime**: standard library only. No upper bounds on dependencies.
