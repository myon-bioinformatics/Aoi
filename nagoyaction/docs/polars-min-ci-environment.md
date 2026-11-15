# Smaller dependencies for the existing Polars comparison job

The `polars-min` job in `.github/workflows/ci.yml` still runs the same real-Polars
reference, the six existing vendor tests, the installed-Polars absence check,
the vendored-minimal collect, and the final byte comparison. It does not replace
the real baseline with a stub or reduce the ordinary Python 3.11–3.15 test matrix.

Only this job's environment setup changes:

1. Sync the resolved Aoi checkout's **unchanged lock**, omitting five unused
   direct packages: NumPy, httpx, coverage, selectolax and PyPI Markdown.
2. Run the same pytest and real-collect commands with `--no-sync`, so uv does not
   silently restore the omitted packages. Real Polars and its compiled runtime
   remain installed for the reference.
3. Sync with `--no-default-groups --no-install-project` for the minimal collect.
   In the measured Aoi revision this leaves no installed distributions. The
   existing explicit import-absence check still fails if Polars is importable.

The selected tests use pytest, real Polars and stdlib/vendored helpers.
`research_digest.py` explicitly loads Aoi's vendored `markdown.py`, not PyPI
Markdown. Anyio and the HTTP transport dependencies are deliberately retained
in the real phase to preserve pytest's plugin environment. This is a conservative
five-package omission, not a claim to the smallest possible dependency closure.
No dependency versions, Aoi files, source algorithms, vendor pins, source
provenance checks, full test jobs or local-ci gates are changed.

## Commands

After the existing workflow has verified the resolved Aoi SHA and overlaid
NagoyAction, run from the Aoi root:

```sh
(
set -eu
comparison_dir="$(mktemp -d)"
uv sync --locked --python 3.15 \
  --no-install-package numpy --no-install-package httpx \
  --no-install-package coverage --no-install-package selectolax \
  --no-install-package markdown
uv run --locked --no-sync --python 3.15 pytest -q -c pyproject.toml nagoyaction/tests/test_vendor_aoi.py
uv run --locked --no-sync --python 3.15 python nagoyaction/scripts/collect_with_polars_min.py --deps real "$comparison_dir/reference.json"
uv sync --locked --no-default-groups --no-install-project --python 3.15
# The workflow explicitly fails if this import succeeds.
if .venv/bin/python -c 'import polars'; then exit 1; fi
.venv/bin/python nagoyaction/scripts/collect_with_polars_min.py --deps min "$comparison_dir/minimal.json"
cmp "$comparison_dir/reference.json" "$comparison_dir/minimal.json"
printf 'Reports: %s\n' "$comparison_dir"
)
```

The workflow remains the authoritative executable sequence, including the
checkout/tree/hash guards and vendored-file existence checks omitted above.
Use the unchanged full README command for all tests. This environment is not
suitable for unrelated Aoi workloads. If future Aoi base dependencies or the
selected tests change, validate both phases again rather than suppressing
imports, skipping tests, or weakening the comparison.

## Local comparison, 2026-11-04

- NagoyAction: `da68f374ad1ae7c786f926190b98c94920d91420`.
- Aoi: `157c67ce8b6f49008ad1063f1727f433d7ce4ab3`.
- Linux x86_64, CPython 3.15.1, uv 0.13.5, pytest 9.1.1, Polars 2.0.0.
- Three alternating pairs, each with a fresh venv and separate empty uv cache.

| Measurement | Existing setup | Proposed setup |
| --- | ---: | ---: |
| Installed distributions, real phase | 18 | 13 |
| Venv logical bytes, real phase | 265,828,362 | 199,856,780 |
| Installed distributions, minimal phase | 9 | 0 |
| Venv logical bytes, minimal phase | 58,666,081 | 30,313 |
| Initial cache logical bytes | 266,802,909 | 200,831,375 |
| Install seconds, trials 1/2/3 | 13.289 / 6.440 / 17.156 | 6.488 / 5.390 / 5.297 |
| Install median seconds | 13.289 | 5.390 |
| Pipeline process seconds, trials 1/2/3 | 16.489 / 9.736 / 20.653 | 9.839 / 9.107 / 8.824 |
| Pipeline process median seconds | 16.489 | 9.107 |

The real-phase venv is about **24.8% smaller**, and the minimal phase about
**99.9% smaller**. The local install and measured-process medians were lower,
but six variable local samples do not establish hosted CI speed or cost savings.
The real Polars oracle still accounts for most of the real-phase environment.

All six samples passed the **same six tests with zero skips**. Collection IDs,
all 18 setup/call/teardown outcomes and pytest configuration matched, with the
same `anyio==4.15.1` plugin and normal plugin autoloading. Both phases passed
`uv pip check --offline`. Initial inventories were unchanged after the tests.

Each reference and minimal output was **56,638 bytes**, with SHA-256
`7dc308a31d969d3f410f100737613e2073586a3e041cc15c41429272086ead35`.
All twelve files were byte-identical. These are deterministic reports of the
same pinned research records, not new observations or additional scientific
validation. All samples and package inventories are in
[the measurement JSON](polars-min-ci-environment.json).

## Final local validation

- Replayed the five affected workflow run blocks verbatim against the final
  patch: six vendor tests passed, both collect phases succeeded, Polars was
  absent for the minimal phase, and `cmp` passed. Installed inventories were
  13 distributions before the transition and zero afterward.
- Complete NagoyAction suite on the original tree: **296 passed, 23 subtests
  passed, zero skipped**. Final patch: **297 passed, 23 subtests passed, zero
  skipped**. All original JUnit test identities and outcomes matched; only the
  new workflow contract test was added. Node-entry tests used Node 26.13.0.
- The new contract test accepts the proposed workflow and rejects the original
  broad-install configuration. It retains the real oracle, absence guard,
  minimal collect, byte comparison and full-test command.
- Actionlint 1.7.12 and `git diff --check` passed. Aoi's `pyproject.toml` and
  `uv.lock` stayed byte-identical throughout. Workflow jobs other than
  `polars-min` are byte-identical to the original.

## Measurement limits

Sizes sum regular-file logical lengths without following symlinks. Shared
Python/stdlib, source checkouts, OS packages and generated reports are excluded.
Venv/cache may share hardlinks, so do not add their sizes as physical disk
savings. Acquisition of dependencies is included; source/interpreter provisioning
is not. Pipeline time sums the two syncs, pytest, both collects and the expected
failed Polars import. Observer, inventory, pip checks and hashing were not used
to alter the tested behavior. OS/CDN caching and unrelated host load were not
controlled. No measured sample was discarded or retried.

Hosted CI has not been run for this local change. The rest of the CI workflow
and its matrix remain unchanged; no new job is added.
