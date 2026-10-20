# requests, tqdm, biopython: the used surface is empty

Draft PR #93's description lists `requests`, `tqdm`, and `biopython` as class (b): shrink the used surface to a stdlib module. The inventory that PR actually measured (`docs/evidence/third-party-survey.json` on that branch) does not contain them. They are not declared in any `pyproject.toml` or requirements file, and no file in Aoi or the six child subtrees imports them.

This change measures that again, with an AST walk plus the same three dynamic modes as `scripts/trace_surface.py` (absent, stub, wrap). It does not edit `shrink/` or `scripts/`. Those directories are already touched by open PRs #91, #92, #93, and #94.

## What was run

AST (`pkgmin/survey.py`), every `.py` file except this harness:

- `import` / `from`, including `import requests.sessions` and `from Bio.SeqIO import parse`
- string literals passed to `import_module` or `__import__`
- `alias.attr` chains and uses of names brought in with `from pkg import`

Dynamic (`pkgmin/trace_used.py`), on `pkgmin/run_paths.py`:

- **absent** blocks `requests`, `tqdm`, `Bio`, and `biopython`. A real import raises `ModuleNotFoundError` at the project's line. The c001 / BlueProbe / QueRyu / R001 paths finish with no hit and no traceback.
- **stub** lets the import succeed. The first attribute is logged. Those paths never import, so the log stays empty.
- **wrap** (CI, after the real wheels are installed) delegates to the installed packages. Project code does not touch them.

`run_paths.py` calls NagoyAction `show` and `doctor` on `cycles/c001-chunichi/pipeline.toml`, BlueProbe `classify_document` on the hand-written fixtures, QueRyu `acquisition_plan` plus `UrllibClient.get` against `127.0.0.1`, and imports the R001 modules (`collect`, `verify`, `observe`, `inning_pilot`) without calling `main` (that hits the network).

The committed result is `pkgmin/evidence/used-surface.json`. Import sites, attributes, and declarations are empty for all three. Eight `import_module` / `__import__` calls take a non-literal argument (`blueprobe.py`, the five `dist/*_min.py` bundles, `queryu/conftest.py`, `scripts/fetch_module.py`). None of them is these packages. A non-literal import inside a function this driver does not call would still be invisible; the AST would see it if the module name were a literal.

## The modules

| File | Loaded as | Exports |
|---|---|---|
| `pkgmin/requests_min.py` | `requests` | nothing |
| `pkgmin/tqdm_min.py` | `tqdm` | nothing |
| `pkgmin/biopython_min.py` | `Bio` (the import name; the wheel is `biopython`) | nothing |

Reading any attribute raises `UsedSurfaceError`. That is the whole stand-in: the used surface is the empty tuple `SURFACE`. Putting a `get` or a FASTA parser in these files would be a new API, not a shrink of a call.

`--inject min` loads them before the real paths. The JSON matches a run where the real packages import successfully, because those paths never ask for the names.

## Infeasible, and why

**There is no call to be equivalent to.** Class (b) in the #93 note means one entry point uses a small surface the standard library can reproduce and check against the real package. The precondition is the entry point. It is missing for all three. The CI job still installs the real wheels, runs the paths, uninstalls the wheels, runs the paths on the stand-ins, and compares the bytes. The bytes match because both runs are the project's own stdlib code.

**requests.** A shrink would be `urllib.request`, which QueRyu already uses as `UrllibClient`. With the wheels installed, a local `200` returns the same body from `requests.get` (`trust_env` off) and from `UrllibClient`. Observed on 2026-10-20, Python 3.12: requests 2.34.2, tqdm 4.70.1, biopython 1.88. The CI job does not pin those versions; the lower bounds are `requests>=2.31.0`, `tqdm>=4.66.0`, `biopython>=1.83`. That one GET is not a call site. Not reproduced, because nothing calls them: `Session`, cookies, auth, adapters, multipart, streaming, retries, `PreparedRequest`, timeout tuples, and `requests`-specific exceptions. Connection errors would be `urllib.error.URLError`, not `requests.exceptions.ConnectionError`. `fetch_module` would also reject the wheel: requests depends on urllib3, certifi, charset-normalizer, and idna.

**tqdm.** A shrink of a result-bearing progress wrapper is an iterator:

```python
def tqdm(iterable, **_unused):
    yield from iterable
```

There is no loop wrapped in `tqdm`, so there is no project output to compare. Terminal width, nested bars, `notebook`, and the pandas accessors are display, not a result. The real `tqdm.tqdm(range(3), disable=True)` yields `0, 1, 2` in the equivalence test. The stand-in does not define `tqdm`, because defining it would not be covering a used surface.

**biopython.** The import name is `Bio`. No file imports `Bio` or `biopython`, and no sequence file is parsed by project code. `Bio.SeqIO.parse` of a two-base FASTA works on the real wheel in the equivalence test (`id == "a"`, sequence `AT`). Copying that into `biopython_min.py` would be a new parser. SeqIO's other formats, `Align` (C aligners), SearchIO, Phylo, PDB, and Entrez are not on any call. The C extensions are not a stdlib subset. Entrez is network. There is no output to diff.

**PR #93's tracer, used as-is, rejects this result.** Its absent mode exits non-zero when the driver finishes without a traceback, because its drivers are supposed to import the package. These paths do not. `pkgmin/trace_used.py` keeps the absent / stub / wrap hooks and records "no hit" as the observation. It does not import `scripts/trace_surface.py`, which is not on `main`.

**Uninstall does not scrub the dependency tree.** The absence check is `import requests`, `import tqdm`, and `import Bio`. urllib3, certifi, and idna can remain; httpx from the lock uses certifi and idna. Removing those would change the locked environment and make the second run differ for a reason that is not these three packages.

## CI

`.github/workflows/pkgmin-stdlib.yml` is one job. It syncs the lock, runs the tests, installs `requests>=2.31.0`, `tqdm>=4.66.0`, and `biopython>=1.83` (lower bounds only, not added to `pyproject.toml`), checks the real entry points and the wrap trace, uninstalls the three distributions, checks they do not import, reruns `run_paths.py --inject min`, and `cmp`s the JSON. The absence check is `if cmd; then exit 1; fi`.
