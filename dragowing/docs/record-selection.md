# Batched result selection

`records.select_items` builds a temporary ID index for batches of eight or more
lookups when record IDs are strings or absent/None. Smaller batches retain the
original scan path. Unusual record IDs retain equality-based scanning.
Duplicate records, duplicate requested IDs, input order within each ID, object
identity and the sequential missing-file/missing-ID errors are preserved.
No dependencies or public API changes.

The threshold is a conservative heuristic, not a universal crossover. Indexing
trades memory for fewer repeated scans: typical indexed work is O(rows + IDs +
output) rather than O(rows times IDs), using O(rows) temporary references.

```sh
python -S -m unittest discover -s tests -p test_record_selection_index.py -v
python -S scripts/benchmark_record_selection.py
```

Two tests cover fixed-seed records, duplicates, identity, empty selection,
unusual IDs and error ordering. The benchmark compares the pinned git baseline
with seven alternating timing samples after warmup; a separate single traced
run measures temporary peak. CPython 3.12.14/Linux, 10000 synthetic records.
Raw samples and the baseline SHA are in `record-selection-measurement.json`.

100 requested IDs: median 27.292 → 1.831 ms; temporary peak 8576 → 214056 bytes.
One/two-ID scans showed small timing variation (0.209/0.445 ms baseline versus
0.244/0.479 ms current), without indexing. No memory reduction, build-time benefit,
CI acceleration or general rendering speedup is claimed.
