# Explicit lightweight path for load_overlap

`load_overlap(path, conds)` uses NumPy, Polars, and PythDRagoras's
`rule_search` as before. Only with `load_overlap(path, conds, backend="stdlib")` does it
return a dict of the same shape using dedicated row evaluation. The CLI option is `--overlap-backend stdlib`.
Unspecified means `native`, and an unknown backend is an error. Unsupported input is never silently sent back to native.

```python
from pathlib import Path
from dragowing.overlap import default_conditions, load_overlap
from dragowing.records import read_jsonl

results = Path("cycles/c001-chunichi/outputs")
conditions = default_conditions(read_jsonl(results / "propositions.jsonl"),
                                read_jsonl(results / "season.jsonl"))
result = load_overlap(results / "season.jsonl", conditions, backend="stdlib")
```

```sh
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --overlap-backend stdlib
```

It works whether or not NumPy and Polars are installed. They are not loaded when the module is
imported; they are lazily imported only when native is called.
`parse_cond`, `default_conditions`, and `finalize_conditions` also run on the standard library alone.
There is no library swapping in `sys.modules` and no change to `sys.path`.

## Supported scope

- JSONL of non-empty JSON objects. Row order, condition order, column order, region order, and unit_index are kept.
- Column values are bool / Int64 integers / finite floats / valid Unicode strings / null.
  A column has one type; only mixing int and float is allowed. A missing cell is the same as null.
- `< <= > >= == !=`. Only number-to-number, bool-to-bool, and string-to-string comparisons.
  Comparisons with null are false for every operator (`!= null` is false too).
- In Float64 comparisons, integers are limited to absolute value `2**53` or less. Integer-only comparisons cover the full Int64 range.
- To stay consistent with native's default `infer_schema_length=100`, a new column or new non-null type
  appearing after the first 100 rows is rejected. Mixed heterogeneous types within 100 rows are rejected too.
- `team` is a string and `season` an integer. Other existing metadata (league, team_name, upper_half) is also required.

Empty input cannot produce a result, same as native (matching exception class and message is not part of the contract).
Duplicate JSON keys, surrogates, NaN/Infinity, list or object cells, huge integers,
and implicit conversion between bool and numbers/strings are explicitly rejected. This is not a replacement for the full
range of input native can handle. For unsupported cases, the user chooses `native`.

Output keys and value types are shared, and no backend marker is added. To check JSON determinism,
use `json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False)`.
The existing API's positional arguments are unchanged and the added argument is keyword-only. Normal pipeline settings are unchanged too.

## Migration decision from the experiment

Aoi's `shrink/run_overlap_stdlib.py --deps min` replaces the process-wide `numpy` and `polars` with
minimal versions. Mixed with libraries already loaded, the same name points to different implementations,
affecting other analyses and imports inside libraries. It also assumes the libraries are not installed.
Production switching does not use it; it calls the limited row evaluation in `_overlap_stdlib.py`.
The experimental artifacts and injection runner remain as a comparison experiment.

## Verification and measurement

`tests/test_overlap_stdlib.py` verifies the real c001 data (168 rows, 8 regions), all operators, empty input,
null/missing, identical conditions, no conditions, 1/7/8/9/99/100/101/255/256/257 rows,
Int64 and Float64 boundaries, the type-inference window, unknown columns, duplicate keys, and invalid Unicode.
It also checks that it succeeds in a fresh `python -S` with library and research-engine imports forbidden,
that existing modules are not swapped even when installed, that canonical JSON matches across different PYTHONHASHSEED values,
and that the CLI's HTML matches native byte for byte.

Medians comparing 5 pairs of fresh processes and 7 warm calls each, on Linux / CPython 3.14.8, NumPy 2.5.4, Polars 2.0.0, with the same c001 input.
The canonical JSON SHA-256 of every sample is
`12037df38eb301300768e0ef172e2e16e8e956dc7669aa08fd355414b7619e35`.
Input SHAs and raw samples are in the [measurement JSON](evidence/overlap-stdlib-benchmark.json).

| Metric | native | stdlib |
|---|---:|---:|
| Process max RSS | 159.46 MiB | 63.03 MiB |
| Cold Python-tracked allocation peak | 30.03 MiB | 20.43 MiB |
| Whole fresh-process time | 1.256 s | 0.871 s |
| First call (tracemalloc on) | 0.802 s | 0.458 s |
| Warm call (tracemalloc off) | 34.75 ms | 52.92 ms |

RSS dropped by about 60%. In this environment the first startup was also shorter, but warm repeated computation is about 1.52× slower.
It is an option for reading small inputs with fewer dependencies and less memory, not a speedup for large-scale analysis.
RSS includes native memory, while tracemalloc covers only Python-tracked objects. This is one example including measurement overhead and
shared-environment load, not a guarantee across all OSes and input sizes.

```sh
PYTHONPATH=/path/to/Aoi/pythdragoras python scripts/benchmark_overlap.py \
  --results /path/to/Aoi/cycles/c001-chunichi/outputs --repeats 5 --warm-repeats 7
```

The benchmark's RSS measurement is for Linux/macOS. The product's lightweight path itself has no OS-dependent processing.
HTML generation still needs Markdown, PNG/SVG needs Chrome, and the registration-status display needs QueRyu.
The public surface and dependency declarations of `dist/dragowing_min.py` are unchanged.
Nothing is written to research inputs, holdout history, or research result files.
