# Stdlib replacement: where the line is

Survey of third-party imports across Aoi and the six child subtrees, plus live traces of the call paths an AST count cannot see. This note does not add `<pkg>_min.py` modules and does not change a pipeline. Shrinks that the classification marks as worth trying are separate changes.

Observed on 2026-10-20 against the locked environment (Python 3.12): polars 2.0.0, numpy 2.5.4, httpx 0.28.1, markdown 3.11.2, selectolax 1.0.1. PyPI wheel class below is what `scripts/fetch_module.py resolve` said about the current release of each distribution.

## The three classes

**(a) Fetch as-is.** A `py3-none-any` wheel with no runtime dependencies outside extras. `scripts/fetch_module.py` already refuses anything else. Put the wheel on `sys.path` and import it. No rewrite.

**(b) Shrink to a `<pkg>_min.py`.** The package is compiled, or it has dependencies, but one entry point uses a small surface that standard-library code can reproduce and check against the real package.

**(c) Not feasible** as a stdlib replacement of that package. The reason is the native library, the size of the surface, or both. A neighboring path that is already stdlib does not make the package itself shrinkable.

Counts come from `scripts/survey_third_party.py`. That count is static: `import` / `from`, string literals passed to `importlib.import_module` or `__import__`, and `alias.attr` chains. A method on a returned value (`frame.height`, `node.css(...)`, `a > b`) is invisible to it. `scripts/trace_surface.py` runs the call in three ways:

- **absent** blocks the import. The traceback is the `ModuleNotFoundError` a missing wheel raises, at the project's import line.
- **stub** lets the import succeed and returns another stub for every attribute. The first operation that needs a real value raises `StubGap`. The events are the prefix of the surface; the traceback is the first hole.
- **wrap** delegates to the installed package and logs attribute access whose nearest caller is project code. Names in that log but not in the AST count are the ones the survey missed.

The study's own harness (`scripts/survey_third_party.py`, `scripts/trace_surface.py`, `scripts/trace_drivers.py`, and their tests) is excluded from the counts. Inventory: `docs/evidence/third-party-survey.json`. Traces: `docs/evidence/trace-surfaces.json`.

```sh
python scripts/survey_third_party.py
python scripts/survey_third_party.py --check docs/evidence/third-party-survey.json
python scripts/trace_surface.py wrap polars -- python scripts/trace_drivers.py load_overlap
python scripts/trace_surface.py collect --check --out docs/evidence/trace-surfaces.json
```

## Inventory

| Package | Files | Import sites | AST attribute uses | Distinct AST names | PyPI, via fetch_module | Class |
|---|---:|---:|---:|---:|---|---|
| polars | 31 | 37 | 933 | 25 | rejected: depends on `polars-runtime-32` | **(b)** for DRAgoWing `load_overlap` only. **(c)** for the package |
| numpy | 14 | 14 | 239 | 65 | rejected: no pure-Python wheel (2.5.4) | **(b)** for `load_overlap` (already generated). **(c)** for `linalg` and the surrounding ndarray use |
| pytest | 83 | 84 (+1 dynamic) | 798 | 15 | rejected: runtime dependencies | test runner, not a target |
| selectolax | 4 | 4 | 11 | 1 (`lexbor.LexborHTMLParser`) | rejected: no pure-Python wheel (1.0.1) | **(c)** |
| httpx | 3 | 3 | 3 (`Client`) | 1 | rejected: `anyio`, `certifi`, `httpcore`, `idna` | **(b)** for the duck type QueRyu already implements in urllib. **(c)** for httpx itself |
| ortools | 2 | 4 | 2 (`__version__`) | 1 | rejected: absl, numpy, pandas, protobuf, … | **(c)** |
| markdown | 1 | 0 static, 1 dynamic | 0 | 0 | **pure wheel** markdown 3.11.2, no runtime deps | **(a)** |
| pandas | 1 | 1 | 1 (`read_json`) | 1 | rejected: numpy, python-dateutil, … | **(c)** |
| coverage | 1 | 1 | 1 (`Coverage`) | 1 | a pure wheel exists (7.16.2) | test tool, not a target |
| DRAgoWing | 1 | 1 | 1 | 1 | not a PyPI distribution | stale import of the pre-subtree package name |
| mcp_toolcall_lab | 1 | 2 | 2 | 2 | not a PyPI distribution | optional lab checkout, env-gated |

No declared dependency is completely unimported. Eight `import_module` / `__import__` calls take a non-literal argument (f-strings); they are listed in the inventory and are not extra packages.

AST names, heaviest first:

- **polars** (933): `col` 419, `DataFrame` 226, `Float64` 69, `Int64` 38, `Int32` 30, `lit` 27, `Utf8` 22, `read_ndjson` 18, `when` 14, `Series` 14, `concat` 11, `len` 10, `Expr` 10, `Boolean` 8, plus `first`, `sum`, `concat_str`, `__version__`, `any_horizontal`, `max_horizontal`, `read_csv`, `concat_list`, `int_range`, `exceptions.PolarsError`, `Config.set_tbl_rows`.
- **numpy** (239, 65 names): the `load_overlap` set is `asarray`, `ones`, `flatnonzero`, `frombuffer`, `uint8`, `unpackbits`, `zeros`. The heavy set is `linalg.svd` (2), `linalg.lstsq` (2), `linalg.norm` (6), `linalg.pinv` (1), plus `ndarray` 22, `float64` 24, `where` 9, `maximum` 7, `abs` 7, `sign` 6, and the rest of the table in the JSON.
- By tree, polars attribute uses are SakAnalytics 677 (4 files), PythDRagoras 223 (17), cycles 22, DRAgoWing 3, NagoyAction 3, research_loop 2, research 2, root tests 1. Numpy attribute uses are PythDRagoras 192 (9 files), QueRyu 35 (2), research 7, DRAgoWing 3, and 2 in `shrink/run_overlap.py` (the existing harness).

## markdown — (a)

`dragowing/htmlout.py` loads it with `importlib.import_module("markdown")` and calls `.markdown(source, extensions=...)`. There is no static `import markdown`, so the AST survey records a dynamic import and **zero** attributes. A wrap of `render_md` on a table plus a fenced code block is the missing name: `markdown`. Absent mode raises `ModuleNotFoundError` at that `import_module`.

`fetch_module.resolve("markdown")` returns `markdown-3.11.2-py3-none-any.whl` and no runtime dependencies. That is the case #87 already runs in `.github/workflows/cdn-module-experiment.yml`, including DRAgoWing's real `render_md`. Nothing further to shrink. Markdown is not part of the stdlib, so a page that calls `render_md` still needs the wheel on `sys.path`.

`vendor/markdown.py` is a different, stdlib-only helper. `htmlout._markdown_library` refuses it if it wins the import. NagoyAction's digest loads that file by path on purpose. The two must not be confused with each other.

## polars — (b) for one DRAgoWing path, (c) otherwise

The distribution depends on `polars-runtime-32`. There is no pure-Python wheel to fetch.

**DRAgoWing's production use is one call.** `dragowing/overlap.py` is the only package module that imports polars: `pl.read_ndjson`, then the frame is handed to `rule_search._mask`. The tests add `read_ndjson` (`test_figures.py`) and `DataFrame` (`test_forms_review.py`, which calls `propositions.evaluate`). AST on `overlap.py` sees only `read_ndjson`.

Live `load_overlap` on `cycles/c001-chunichi/outputs/season.jsonl` (168 rows, 8 regions):

| Mode | What happened |
|---|---|
| absent | `ModuleNotFoundError` at `import polars as pl` inside `load_overlap` |
| stub | logged `read_ndjson`, `height`, `__ne__`, then `StubGap` on the truth of `frame.height != len(rows)`. It never reached `_mask` |
| wrap | finished on real polars 2.0.0. Dynamic names: `read_ndjson`, `height`, `columns`, `select`, `to_list`, `__getitem__`, `col`, `lit`, `__gt__`, `__le__`, `__eq__`. AST had already counted only `read_ndjson`, `col`, `lit` |

So the AST missed `height`, `columns`, `select`, `to_list`, indexing, and the comparison operators. Those operators are not written in the source: `_cond` does `OPS[c["op"]](pl.col(...), pl.lit(...))` with `OPS` holding all six of `< <= > >= == !=`. This run's default conditions only evaluated `>`, `<=`, and `==`. A shrink of this path still has to implement all six, plus Polars nulls (comparison with null is null, and `False & null` is false). The trace cannot see an operator the chosen rows do not use.

That surface is small enough to be a `polars_min` for **this entry**. It is not a shrink of Polars.

**Everywhere else the surface is the expression engine.** SakAnalytics accounts for 677 of the 933 alias uses (`col` 340, `DataFrame` 130, dtypes, `when`, `concat`, …) across `sakanalytics.py`, `proposition_seed_audit.py`, `synthetic_rule_discovery.py`, and tests. The method calls on those frames (filter, rank, over, group_by, join) are not in the 677. PythDRagoras is 223 alias uses in 17 files: `evaluate` builds expressions, filters, drops nulls, casts, and walks `iter_rows`. NagoyAction's digest is the clearest AST miss: the survey counts `DataFrame` twice and `col` once in `nagoyaction/research_digest.py`, and the same function calls `.explode`, `.filter`, `.join`, and `.iter_rows`. Reimplementing that is a dataframe library. Class **(c)** for the package.

`dist/dragowing_min.py` does not import polars. The managed copy described below never reaches `load_overlap`.

## numpy — (b) on `load_overlap`, (c) on the linalg paths

No pure-Python wheel (numpy 2.5.4). #89 already generates `shrink/numpy_min.py` for `dragowing/overlap.py:load_overlap` and checks it byte-for-byte with numpy uninstalled.

The new trace is a check on that boundary, not a new shrink. Wrap of the same c001 `load_overlap` saw:

`asarray`, `ones`, `flatnonzero`, `frombuffer`, `uint8`, `unpackbits`, `reshape`, `astype`, `sum`, `shape`, `__getitem__`, `__and__`, `__invert__`, `__iter__`

AST on that path had counted `asarray`, `ones`, `flatnonzero`, `frombuffer`, `uint8`, `unpackbits` (and `zeros`, which this non-empty file does not call). The live run's extra names are exactly the ndarray methods the generator always emits: reshape, astype, sum, indexing, `&`, `~`, iteration. `shape` is a spelling the repo also uses as `np.shape` elsewhere, so the "missed" set hides it; the event log still has it. No name outside `numpy_min` appeared on this path.

**QueRyu `ask/suggest.py:Index` is the other side of the line.** AST: `linalg.svd` once, `linalg.norm` four times, plus `float32`, `log`, `divide`, `packbits`, `sign`, `argsort`, `nan_to_num`, `zeros`. Wrap of `Index` on three short documents also ran `svd` and `norm`, and the methods the AST does not tie to that call: `.T`, `.mean`, `.astype`, `__matmul__`, `__getitem__`, `__setitem__`, in-place arithmetic. The projection is a real SVD. A stdlib rewrite is not going to match OpenBLAS, and the ndarray operations around it are most of a numeric array library. Class **(c)** for this path.

**PythDRagoras `littlebit_prune.littlebit` is the same class.** One wrap (8×5 matrix, rank 2, one stage) called `linalg.svd` and `linalg.lstsq`, plus `einsum`, `sign`, `abs`, `maximum`, `sum`, `.T`, and `__matmul__`. `linalg.norm` and `linalg.pinv` are in the AST (norm in `littlebit_prune.overlap_bounds` and in suggest; pinv in `littlebit_holdout.fit`) and were not on this particular call. Together that is LAPACK (SVD, least squares, pseudoinverse) plus broadcasting and reductions. 192 of the 239 numpy attribute uses sit in PythDRagoras. Class **(c)**. `queryu/tests/test_id_suggest.py` adds `full_like`, `ones_like`, `sqrt` on top of the same Index.

`shrink/run_overlap.py` only touches `numpy.__file__` and `numpy.__version__` while proving which implementation ran.

## selectolax — (c)

Compiled Lexbor. `fetch_module` finds no pure wheel (1.0.1). Every import is `from selectolax.lexbor import LexborHTMLParser`: eight in `blueprobe/tests/test_blueprobe_html_parity.py`, one each in the R001 research scripts `verify.py`, `observe.py`, `inning_pilot.py`. `blueprobe.py` parses with `html.parser`. selectolax is the test oracle, which is why a parity test exists: the two parsers are not the same function.

Wrap of the same calls the parity test makes (`css`, `text(deep=True)`, `attributes`, `tag`) logged those four methods and nothing else that would make a smaller wrapper. The stub died earlier, at `list(parser.css("a"))`, with `StubGap` on iteration: the AST name `LexborHTMLParser` never mentioned `css`. A stdlib file can wrap `html.parser`. It cannot be Lexbor, and the production path does not need it to be.

## httpx — (b) only for a duck type the repo already has

The wheel is pure Python, and `fetch_module` still rejects it: runtime dependencies are anyio, certifi, httpcore, idna. Class **(a)** does not apply. Fetching httpx without those does not import.

All three import sites are research scripts (`collect.py`, `verify.py`, `inning_pilot.py`). Each one builds `httpx.Client(headers=..., timeout=..., follow_redirects=True)` and passes it to QueRyu's `PoliteFetcher`. The fetcher's own default is `UrllibClient` in `queryu/queryu.py`, which is stdlib and already returns the same `status_code` / `content` / `headers` / `raise_for_status` object.

Wrap of `PoliteFetcher.get` against a local server, with a real httpx client, logged `Client`, `__enter__`, `__exit__`, `get`, `status_code`, `content`, `headers`. The stub died on the truth of `status_code == 200` after logging `get` and `status_code`. That is the whole used surface. It is the `UrllibClient` surface. A new `httpx_min` would duplicate that client for the three research scripts; it would not be httpx (HTTP/2, streaming, auth, custom transports). Class **(b)** for the duck type, and only because those scripts insist on constructing `httpx.Client`. Class **(c)** for the library. QueRyu's production fetcher does not import httpx. httpx is declared on Aoi's root `pyproject.toml`, not on QueRyu's.

## pandas — (c)

One script, `research/gpt-r001-score-allocation/verify_prediction_independent.py`, and it is not a locked dependency. AST sees `pd.read_json` only. The rest is method syntax (`groupby`, `transform`, boolean indexing, `.iloc`, `.to_numpy`). Pandas is not installed here, so there is no wrap. Absent mode raises `ModuleNotFoundError` at `import pandas`. The stub, driven through the same operations on a three-row frame, logged `DataFrame`, `groupby`, `transform`, `__getitem__`, `__setitem__`, `__ge__`, `__sub__`, `__truediv__`, `copy`, and the column names, then `StubGap` on item assignment. That is a dataframe engine plus the numpy `lstsq` the same script calls. `fetch_module` rejects pandas for its numpy and python-dateutil dependencies. Not a shrink candidate.

## ortools — (c)

Optional. `sakanalytics/season_exact.py` and `research/gpt-r001-score-allocation/preclinch_dates.py` import `ortools.sat.python.cp_model` inside the solver function. Forecasts in `season_simulator.py` are stdlib; the requirements file says the exact solver is optional. ortools is not installed in the lock. Absent mode fails at `import ortools`. The stub walks `ortools.sat.python.cp_model.CpModel` and `__version__` without ever building a model, which is as far as a stub can go: the next real step is CP-SAT. `fetch_module` rejects the distribution (absl, numpy, pandas, protobuf, …). A pure-Python CP-SAT is not a min module.

## pytest and coverage

pytest is the test runner (83 files). coverage is imported once, in `tests/test_child_registry.py`. coverage's pure wheel is real, and it is still the wrong target: the project uses it to measure tests, not to compute a result. Neither is a candidate for a stdlib replacement of the research code.

## Not distributions

`research/gpt-r001-score-allocation/render_matched_comeback.py` does `from DRAgoWing.dragowing import render_report`. That is the package name from before the subtree move. The module is `dragowing.research_report`. It is not on PyPI.

`blueprobe/html_source.py` imports `mcp_toolcall_lab` inside a function, gated by an environment variable and a checkout path. It is an optional lab, not a dependency of the runtime parser.

## DRAgoWing on the standard library

Of the package modules under `dragowing/`, only two import a third-party library: `overlap.py` (numpy and polars) and `htmlout.py` (markdown, dynamically). Figures, records, forms, the HTML shell, the Plotly **JSON** spec, and the CDN URL are stdlib. Plotly itself is the browser's plotly.js, not a Python package. Chrome export needs a browser. Those two are outside this question.

`load_overlap` does not run on the stdlib alone today. The numpy half does: #89 runs this same function with numpy uninstalled. The polars half is the surface in the table above (`read_ndjson`, `height`, `columns`, `select`, `to_list`, `col`, `lit`, the six comparisons, nulls). Until a `polars_min` for that surface exists and is checked the way `numpy_min` is, the claim stops there. `render_md` runs without installing markdown only by fetching the wheel (#87), which is class (a), not stdlib.

## A managed `min.py` and downstream callers

`dist/dragowing_min.py` (and the other four files next to it) is already the managed stdlib copy. The survey finds no third-party import under `dist/`. It also does not include `load_overlap` or `render_md`. A downstream caller of `dragowing_min` never imports polars, numpy, or markdown. That contract is the one in `docs/distributions.md`, and this study does not change it.

A caller of the **full** package hits `import polars` inside `load_overlap` and `import numpy` at the top of `overlap.py`. The injection point already used for numpy is process-wide and does not edit production code: `shrink/run_overlap.py` puts `shrink/numpy_min.py` in `sys.modules["numpy"]` before the import. The same seam is what a `polars_min` would use (`sys.modules["polars"]` before `dragowing.overlap` is imported). It works for a caller that owns the process. It does not work if polars was already imported, and it does not apply to someone who only received `dist/dragowing_min.py`, because that file never calls `load_overlap`.

## What the traces do not prove

A wrap records the path that ran. c001's default conditions never evaluated `<`, `>=`, or `!=`, and never took the empty-mask branch that calls `np.zeros`. The stub stops at the first real value, so the polars stub never reached `select`. Names the AST already counted are not listed as missed, even when the live object used them as methods (`sum`, `shape`, `svd`). The event log in `docs/evidence/trace-surfaces.json` is the place to see those.

## Reproduce

The counts and the missed-name sets are checked in CI (`.github/workflows/stdlib-feasibility-survey.yml`) on Python 3.12 with the lockfile. Unit tests of both tools do not need the third-party packages. The collect job does, and it fails if a fresh wrap/absent/stub run disagrees with `docs/evidence/trace-surfaces.json`.
