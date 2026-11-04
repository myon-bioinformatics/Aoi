# Iterative accessible-name DOM traversal

The internal `_walk` uses an explicit stack of child iterators instead of nested
Python generators. DOM preorder and node identity remain unchanged; text children
are skipped. This removes traversal dependence on Python's recursion limit without
copying all siblings into a second stack. Extra iterator storage is O(depth).
Public report schema, naming approximation, `_text` depth limit and parsing behavior
are unchanged. `observe` still holds the DOM and node list; this is not streaming HTML.

```sh
python -S -m unittest discover -s tests -p test_accessible_iterative_walk.py -v
python -S scripts/benchmark_accessible_walk.py
```

Two tests pass: 30 seeded mixed-depth documents yield identical preorder and full
reports against the original recursive definition; a document deeper than the
current recursion limit raises RecursionError under that definition and succeeds
under the new walker, including the public observe result and DOM-index key.

CPython 3.12.14/Linux, parsing excluded, one warmup and seven alternating timings:

| Nested depth | Recursive median | Iterative median | Traced temporary peak old / new |
|---:|---:|---:|---:|
| 16 | 3,836 ns | 4,077 ns | 4,672 / 1,768 B |
| 512 | 2,411,915 ns | 117,437 ns | 139,648 / 33,576 B |

Peak allocations are separate single traced runs; timing samples are untraced.
Raw evidence is in `accessible-walk-measurement.json`. Small trees may be slightly
slower. These results concern isolated traversal, not full parsing/observation,
build time or CI duration. No dependencies added.

## Optimized Python guard

Benchmark parity checks use explicit conditions and `SystemExit`, so they remain
active under `python -O`. A subprocess regression test injects incorrect results
and verifies a nonzero exit with a mismatch diagnostic and no success JSON:

```sh
python -S -m unittest discover -s tests -p test_benchmark_optimization_guard.py -v
```
