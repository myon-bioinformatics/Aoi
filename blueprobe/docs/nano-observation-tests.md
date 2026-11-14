# Optional saved-observation test environment

BlueProbe's runtime is already standard-library-only. This opt-in environment
reduces **test-tool installation** for the existing saved-observation tests; it
does not replace a parser or remove an independent comparison.

## Reproduce

Use Python 3.11+ and uv from the repository root. The measurement below used
CPython 3.12.14 and uv 0.13.5 on Linux x86_64.

```sh
UV_PROJECT_ENVIRONMENT=build/observation-test/.venv \
  uv sync --locked --only-group observation-test
UV_PROJECT_ENVIRONMENT=build/observation-test/.venv \
  uv run --locked --no-sync python -m pytest -q \
  tests/test_blueprobe_accessible_names.py \
  tests/test_blueprobe_emoji_observations.py \
  tests/test_blueprobe_heading_observations.py \
  tests/test_blueprobe_snapshot_source.py \
  tests/test_web_observations.py \
  tests/test_accessible_iterative_walk.py
```

`--only-group` omits the default dev group; `--no-sync` prevents a later `uv run`
from reinstalling it. Use the same explicit environment for both commands.
This selection includes comparisons with the repository's saved Chromium
observations, but does not launch Chromium or prove current browser equivalence.

For parser changes, use the unchanged default `uv sync --locked` environment,
including real selectolax/Lexbor, and the full existing test suite. Full integration
also requires the Aoi and historical lab source checkouts described in CI. The
new group does not change CI, its required-integration guard, conftest, runtime
source, default dev dependencies, or any existing test. Do not present these
49 tests as the full suite. Explicitly collecting `test_blueprobe_html_parity.py`
without selectolax must fail rather than silently count the oracle as tested.

## Measurements and boundaries

Base: `c4137406f93c30b01f2720977f9923ab9b8813d4`.
All seven third-party lock records, versions, sources, dependency edges and
hashes are unchanged. Only BlueProbe's group metadata was added to the lock.
An initial offline lock attempt with an empty cache failed; online lock resolution
then succeeded without changing third-party records.

Each sample used a new venv and separate initially empty uv cache. Order:
full/nano, nano/full, full/nano. Python and repository acquisition were excluded.
Installation includes package downloads and uv synchronization, measured as
subprocess wall time. Test process wall time is separate. No build-time reduction
is claimed. Raw samples, distributions, collection IDs, phase outcomes and plugin
inventory are in [nano-observation-tests.json](nano-observation-tests.json).

| Metric | Full dev | observation-test |
| --- | ---: | ---: |
| Installed distributions | 6 | 5 |
| Venv regular-file logical bytes | 14,691,433 | 6,616,866 |
| Cache regular-file logical bytes | 14,663,805 | 6,588,723 |
| Install seconds, all three samples | 3.168 / 3.682 / 2.666 | 4.679 / 2.351 / 3.337 |
| Install median seconds | 3.168 | 3.337 |
| Selected-test process median seconds | 0.725 | 0.633 |

Size was recorded immediately after installation, before tests created bytecode.
Venv logical size decreased by about 55.0%, but installation did not become
faster. These small local test timings do not establish general performance or
CI speedup. Host load and OS/CDN caches were not controlled; another repository's
installation may overlap the final nano sample. All samples are retained without
retrying for a better result. Preparation and source acquisition occurred outside
the timing boundary. Logical sizes omit symlink targets, the shared Python runtime,
stdlib, sources and system libraries; venv/cache can share hardlinks and must not
be added as physical disk consumption. No container security isolation or CPU/RAM
quota is introduced. Other Python versions and OSes are not measured here.

## Verification

- All six environments passed the same 49 existing tests, 294 executions total,
  with zero skips. Collection IDs, setup/call/teardown outcomes, root config and
  external pytest distribution plugin inventory matched exactly. Plugin autoload was not disabled.
- All six offline `uv pip check` runs passed.
- Full default dev suite: **465 passed, zero skips**, with the unchanged
  `--require-blueprobe-lab-integration` guard enabled. Aoi source was fixed at
  `157c67ce8b6f49008ad1063f1727f433d7ce4ab3`; lab source at
  `81b1150d633d5c6aaedc893c951c8f584ba877e3`. This includes the real Lexbor
  comparisons and all three required offline lab integration tests.
- Across all six environments, accessible-name, emoji and heading observers
  produced byte-identical JSON for every saved page fixture (15 observer outputs).
  SHA-256: `60af60e6c2f643589fd88d2ad6f96e8c4bc40fb7809c820a47b58a12d5650f4a`.
  The raw evidence describes the deterministic serialization recipe. These are
  saved inputs, not a fresh browser capture.
- The nano environment fails explicit Lexbor oracle collection with missing
  `selectolax`, exit 2. A deliberately narrowed command with the full environment's
  required-integration guard fails with exit 1 for the three missing cases.
- The documented `uv run --locked --offline --no-sync` selected-test command
  passed all 49 tests without restoring selectolax. Offline lock check and
  `git diff --check` passed. Hosted CI has not been run for this local patch.

No push, PR, workflow dispatch, merge, or deployment was performed for this local
implementation.

## Measurement harness

The small [measurement runner](../scripts/nano_observation/run.py),
[receipt plugin](../scripts/nano_observation/receipt_plugin.py) and
[output comparison input](../scripts/nano_observation/output_parity.py) preserve
how the local evidence was collected. From a fresh checkout with uv on PATH:

```sh
python scripts/nano_observation/run.py
for sample in build/experiment/[1-6]-*; do
  PYTHONPATH="$PWD" "$sample/venv/bin/python" \
    scripts/nano_observation/output_parity.py > "$sample/outputs.json"
done
sha256sum build/experiment/[1-6]-*/outputs.json
for sample in build/experiment/[2-6]-*; do
  cmp build/experiment/1-full/outputs.json "$sample/outputs.json" || exit 1
done
```

The runner deliberately refuses existing sample directories and stops on a failed
installation/test/check rather than retrying. It captures failed installation
attempts before stopping. Do not mix repeated runs or remove slow samples. It
retains package caches/environments under build for inspection; they are ignored
by Git. Use the same interpreter for all samples. The receipt plugin inventories
external pytest distributions only, not pytest built-ins or the local receipt
plugin. The harness's own receipt plugin is loaded identically for all samples.
The harness was retained after the recorded run, with failure recording and
receipt-equality enforcement hardened; no successful sample was rerun.

To reproduce the full-suite check at the same external source revisions (these
are test inputs, not new vendor pins), in a fresh checkout:

```sh
mkdir -p .test-deps
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout 157c67ce8b6f49008ad1063f1727f433d7ce4ab3
git clone https://github.com/myon-bioinformatics/mcp-toolcall-lab.git .test-deps/lab
git -C .test-deps/lab checkout 81b1150d633d5c6aaedc893c951c8f584ba877e3
uv sync --locked
PYTHONPATH="$PWD/.test-deps/aoi/queryu:$PWD/.test-deps/lab/src" \
AOI_LAB_SOURCE_ROOT="$PWD/.test-deps/lab/src" \
  uv run --locked --no-sync python -m pytest -q --require-blueprobe-lab-integration
```

The recorded full-suite run reused a separate local checkout of that exact Aoi
SHA and the first full sample's environment, rather than cloning/installing again.
No external NPB service or browser was used.
