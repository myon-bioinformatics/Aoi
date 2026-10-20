# What the third-party minimums can and cannot replace

This is the feasibility result for the dependencies that are not polars and not numpy linear algebra. Those two are handled separately. The method was an AST scan (`scripts/trace_third_party.py`) plus dynamic runs: importing the real modules with the package blocked, and proxying the real `selectolax` / `httpx` objects while the research code ran.

Nothing here edits the shared projects. The replacements are opt-in runners under `mindeps/`.

## Feasible, and implemented

### selectolax → `selectolax_min.py` (html.parser)

`selectolax` is a dev dependency (lexbor, a compiled extension). `fetch_module` rejects it: version 1.0.1 has no `py3-none-any` wheel.

The calls the research code actually makes, found by proxying `LexborHTMLParser` while `observe.parse`, `inning_pilot.parse`, and `verify.annual` ran:

- `LexborHTMLParser(html)`
- `css` / `css_first` on the document and on a node
- `attributes.get`
- `parent` and `prev` (including text nodes, used as booleans)
- `text()` with no arguments
- `decompose()`
- the `.html` property, which is then parsed again by `npb_calendar.parse`

On that surface — the competition-label HTML, the inning scoreboards, a six-team annual table, and the saved 2005 standings page — `selectolax_min` matches lexbor. `mindeps/run_selectolax.py` writes the JSON from those real functions.

It is not a lexbor replacement. html.parser does not do HTML5 recovery, and the parity tests already record the differences:

- a missing `tr` (`<table><td>`) — lexbor invents the row; html.parser does not
- an implied `tbody`
- nested `<a>` — lexbor closes the outer anchor; html.parser nests it, so the outer text is `AB` instead of `A`
- `<template>` contents stay in the html.parser tree and are dropped by lexbor

`selectolax_min.html` is also not byte-identical: lexbor wraps the fragment in `<html><head></head><body>` and inserts `<tbody>`. The calendar parser does not need those wrappers, which is why the function results still match.

### httpx → `httpx_min.py` (urllib)

`httpx` 0.28.1 is pure Python, but `fetch_module` rejects it because of runtime dependencies: `anyio`, `certifi`, `httpcore`, `idna`. Fetching the wheel alone cannot import it. There is no dependency resolver in `fetch_module`.

The only call sites are `collect.py`, `verify.py`, and `inning_pilot.py` (the last one only inside `main`, so a blocked import of the module succeeds). Each one is:

```python
with httpx.Client(headers={"User-Agent": UA}, timeout=45, follow_redirects=True) as client:
    fetcher = PoliteFetcher(cache, wait=..., client=client)
```

Proxying that client through `PoliteFetcher` touched only `Client` as a context manager, `get(url, headers=)`, `status_code`, `content`, `headers.get` (`etag`, `last-modified`), and `raise_for_status`. `httpx_min` covers that, including redirects, 404, 304, and 500, against a local server. QueRyu already speaks urllib; this is the same shape under the `httpx` name so those three scripts import.

Not covered, because nothing in the tree calls them: HTTP/2, streaming, auth, cookies, multipart, proxies as `httpx.Proxy` objects, and `httpx.Timeout` objects. `timeout=` has to be a number of seconds. Connection failures raise urllib's `URLError`, not `httpx.ConnectError`. The scripts do not catch either.

### coverage → `fetch_module` CDN

`coverage` is the other pure-Python dependency the tree actually imports (`tests/test_child_registry.py` measures `scripts/check_child_heads.py`). Its `py3-none-any` wheel has no C tracer and warns about it, but the Python tracer collects data. coverage 7.16.2 publishes one requirement, `tomli; python_full_version <= "3.11.0a6" and extra == "toml"`. The pre-release comparison is not evaluated, and no extra is selected, so `fetch_module` treats that `and` as false and fetches the wheel. `run_coverage.py --impl cdn` calls `resolve` with no extra allowance. A requirement that is not gated on an unselected extra is still rejected.

`mindeps/run_coverage.py` runs the real `validate_heads` and `failed` under `Coverage(branch=True)`, then compares `analysis2` and the `json_report` summary. The pure wheel's numbers match the installed C-tracer build of the same locked version.

This does not replace the mutation suite. That suite shells out to `python -m coverage` over the registry tests; the pure tracer is slower and was not run over that suite. The API those tests use (`load`, `analysis2`, `json_report`) is what the CDN run exercises, on the real module.

### markdown

Already done in the CDN experiment (`scripts/fetch_module.py`, `scripts/cdn_markdown_smoke.py`). `dragowing/htmlout.py` loads it with `importlib.import_module("markdown")`. Latest `markdown` still resolves to a `py3-none-any` wheel with no runtime dependencies. Not repeated here.

## Not feasible

### HTML5 selectolax

A stdlib `selectolax_min` cannot be the oracle in `blueprobe/tests/test_blueprobe_html_parity.py`. Those tests exist to show where html.parser and lexbor disagree. Matching them would mean reimplementing lexbor.

### httpx as a fetched wheel

`fetch_module` stops at `requires_dist`. The transitive pure wheels (`h11`, `certifi`, `idna`, `packaging`, `pluggy`, `iniconfig`, `colorama`, `typing-extensions`, `pygments`) do resolve, and `httpcore` / `anyio` do not (they have their own dependencies). Nothing in Aoi imports those transitive modules by name. Wiring them up would be a resolver, which `fetch_module` deliberately is not. `httpx_min` is the path that runs the real call.

### pandas

`research/gpt-r001-score-allocation/verify_prediction_independent.py` imports pandas and calls `numpy.linalg.lstsq` on grouped columns (`read_json`, `groupby`, `transform`, `to_numpy`). pandas 3.0.6 has no usable `fetch_module` result: it requires `numpy` and `python-dateutil`. The script is the linear-algebra verification, which is out of this change.

### ortools

`sakanalytics/season_exact.py` and `research/gpt-r001-score-allocation/preclinch_dates.py` build a CP-SAT model (`CpModel`, `CpSolver`, `OPTIMAL` / `FEASIBLE` / `INFEASIBLE`). ortools 9.15.6755 publishes no pure wheel (platform wheels only) and depends on `absl-py`, `numpy`, `pandas`, `protobuf`, and others. A stdlib subset cannot stand in for the native solver. It is also not declared in `sakanalytics/pyproject.toml`; the import is inside the function that solves.

### polars and numpy

Compiled. Polars 2.0.0 depends on `polars-runtime-32`. Numpy 2.5.4 has no pure wheel. The overlap subset already has `shrink/numpy_min.py`. The rest of polars, and numpy's linear algebra, are separate work.

### pytest

Dev-only. `fetch_module` rejects pytest 9.1.1 because it depends on `iniconfig`, `packaging`, `pluggy`, and `pygments` (plus platform markers). It is the test runner, not a product import to replace.

### mcp-toolcall-lab

`blueprobe/html_source.py` optionally imports `mcp_toolcall_lab`. It is not on PyPI under that name (the project JSON 404s). CI checks out a pinned git SHA. `fetch_module` does not apply.

### DRAgoWing

`research/gpt-r001-score-allocation/render_matched_comeback.py` imports `DRAgoWing.dragowing`, the old capitalized path. That is a local import path, not a third-party package.
