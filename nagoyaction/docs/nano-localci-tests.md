# Optional locked localci self-test environment

`tools/localci-env` is an opt-in environment for the existing
`tests/test_localci.py` file. It installs the real pytest runner and its complete
locked dependency closure. It does not replace a dependency with a stub or
remove any tests. The full Aoi-integrated matrix and the existing Polars
real/minimal comparison stay unchanged.

## Run from this repository's root

Python 3.11 or later and uv are required. Use an explicit writable cache path if
uv's default cache is unavailable. The first sync may download packages from
PyPI; subsequent use can be offline once all required wheels are cached.

```sh
uv sync --project tools/localci-env --locked --python 3.12
PYTHONPATH="$PWD" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  uv run --project tools/localci-env --locked --no-sync python -m pytest \
  -q tests/test_localci.py tests/test_localci_nano_profile.py
```

The new three profile-contract tests are separate from the original 39 self-test
cases. The command checks 42 cases. Third-party plugin autoload is disabled
explicitly; the unchanged subprocess tests still load `localci_pytest` to check
seed substitution, disjoint sharding and complete coverage. This setting does
not disable built-in pytest assertions or fixtures.

This command runs pytest directly. It does **not** run `localci.py run
--self-tests`, which also resolves external references and runs workflow checks.
Git is required by the local temporary-repository tests. Tests mock external
network responses; no model, browser, Docker or production service is started.
The test command is not a security or egress sandbox.

## Measured comparison (2026-11-05)

- NagoyAction source: `fb92e04eeb70acf99f3aa3935bcff7d486f25b03`.
- Baseline dependency source: Aoi `301b6844b74ad5938b8d32aaa55d8478a9421e3b`,
  its exact `uv.lock`, default `dev` and `runtime` groups, `--no-install-project`.
  This is the complete third-party dependency environment, **not** an installed
  Aoi application or a measurement of its complete CI job.
- One Linux x86_64 host, CPython 3.12.15, uv 0.13.5; identical interpreter and
  the same repository and unchanged `tests/test_localci.py` in both arms.
- All five installed candidate distribution names and versions match the
  baseline. Colorama is a Windows-only lock record, not an installed Linux
  package.
- Both arms use `PYTHONPATH` set to the same source and
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`; `PYTEST_ADDOPTS` is unset.
- Three sequential pairs, alternating full/nano, nano/full, full/nano. All six
  executions have the same 39 ordered test identities and **39 passed, zero
  skipped/failed/errors**. The fixtures exercise local Git and child pytest.

Installed third-party distributions: **18 → 5**.
Virtual-environment regular-file apparent bytes, after tests:
**267,981,866 → 8,667,505** (about 96.8% smaller).
These are logical file lengths, counting each regular-file path, not filesystem
allocation or total disk savings. The Python interpreter symlinks, shared uv
cache, repository source and external dependencies are not included. uv may
hardlink cached files, so this is not a claim of physical storage reclaimed.

Test subprocess wall seconds (includes Python/pytest startup):

- Full: 1.713, 1.701, 1.656; median **1.701**.
- Nano: 1.873, 1.755, 1.684; median **1.755**.

There is **no measured speedup**. The value here is avoiding unused research
packages for this narrowly defined workload. These are three runs on a shared
host, not a statistical performance guarantee. Dependency preparation used a
partially warm shared cache and is not reported as a cold/warm install benchmark.

Exact inventories, test-source hash, each test identity/outcome and all six
sample timings are retained in `nano-localci-measurement.json`.

## Reproduction and boundaries

For the baseline, check out the named Aoi commit separately and sync its lock
with the same Python, `uv sync --locked --no-install-project`, using an explicit
`UV_PROJECT_ENVIRONMENT` to avoid changing an existing environment. For the
candidate, sync `tools/localci-env` to a different environment. From this
NagoyAction checkout run each environment's absolute Python with:

```sh
PYTHONPATH="$PWD" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /absolute/path/to/environment/bin/python -m pytest -q tests/test_localci.py \
  --junitxml=/absolute/path/to/unique-result.xml
```

Unset `PYTEST_ADDOPTS` in both arms. Compare JUnit classname/name pairs and
outcomes, including skips and failures, before interpreting timings. Retain all
samples, including failures. Do not use a reduced collection to claim a full
suite pass. Do not infer Windows/macOS or other Python-version compatibility
from this Linux/Python 3.12 measurement. The profile lock is cross-platform;
only this platform/interpreter combination was executed here.

The exact pytest pin matches the measured Aoi baseline. When refreshing it,
update the lock, profile-contract expectations and measurements together.
The application source, vendor locks, workflow files and default installation
behavior are unchanged. No hosted workflow was dispatched for this experiment.
