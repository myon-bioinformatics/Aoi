# Nearest-candidate retention

`neighbors.discover` retains only the best opposite-group candidate for each row,
using the same (distance, sorted unit IDs) ordering as the original `min` call.
Equal keys keep the first encountered candidate. Candidate eligibility, distance
formula, scales, output sorting and descriptive limitations are unchanged.
This reduces temporary candidate retention, not O(N squared) distance computation.
No dependencies or public API changes.

```sh
python -S -m unittest discover -s tests -p test_neighbor_retention.py
python -S -m scripts.benchmark_neighbor_retention
```

The regression tests exercise ties, exclusions, empty input, limit and unchanged
input. The benchmark verifies complete report equality against the pinned git
baseline for a seeded 200-row dataset and 30 smaller subsets.

CPython 3.12.14/Linux, one warmup plus three alternating timing repetitions:
median 25.401 ms baseline versus 25.819 ms current. Separate single-run traced
peak: 216288 versus 191770 bytes (about 11% lower, including report allocations).
Input construction excluded. Raw evidence is in neighbor-retention-measurement.json.
The small timing regression and single memory sample do not establish a general
speedup; this is a modest temporary-memory improvement. No build-time or CI
improvement is claimed. Full integration tests remain in CI.

## Optimized Python guard

Benchmark parity checks use explicit conditions and `SystemExit`, so they remain
active under `python -O`. A subprocess regression test injects incorrect results
and verifies a nonzero exit with a mismatch diagnostic and no success JSON:

```sh
python -S -m unittest discover -s tests -p test_benchmark_optimization_guard.py -v
```
