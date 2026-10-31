# CI

The run definition is `.github/workflows/ci.yml`.

- **Aoi**: at run time, resolves main's SHA with `git ls-remote https://github.com/myon-bioinformatics/Aoi refs/heads/main`, checks the repository id on the public page, then checks out to `.test-deps/aoi`. The resolved SHA is left in the job summary. The ref can be overridden with `aoi_ref` in `workflow_dispatch`. Commit SHAs are not pinned in files.
- **Parent vendor dispatch**: removed. `vendor.lock.json` had no registered rows, so the lock and the `vendor-dispatch` job that verified it (`pilot/vendor_dispatch.py --manifest vendor.lock.json`) were both removed.
- **mcp-toolcall-lab**: `LAB_SHA` is a snapshot for verifying past patterns. It is fetched by SHA and used as verification test data. This check fails on every event.
- **Source hashes**: if a floating source-hash check is added, it only reports on `pull_request` and fails on push to `main` and on `schedule`. Aoi's source hashes are not recorded.
- **JUnit XML**: `pytest -q --junitxml=reports/junit.xml`, artifact name `junit-py<python>`, retained 14 days. Aggregation is the org parent's `reusable-junit-identity.yml`.
- **lint**: ruff is not added. `python -m compileall` checks syntax only.
- **Runtime**: standard library only. No upper bounds on dependencies.
