# Case-mismatch link lookup

Local link checking lazily builds a lowercase-path index after the first missing
exact path. Subsequent mismatches reuse it, including directory references.
Exact-path checks, missing-path errors and output order remain unchanged. The
first candidate encountered in the same tracked-path union remains the diagnostic
for case-colliding names. No dependency/API changes or network requests added.

```sh
python -S -m unittest discover -s tests -p test_link_case_index.py
python -S -m scripts.benchmark_link_case_index
```

The regression covers exact, case-mismatched, directory, absent and repeated links.
The pinned-baseline benchmark verifies complete result equality on 2001 synthetic
tracked files / 500 mismatched links. CPython 3.12.14/Linux, one warmup plus three
alternating samples: median 90.235 → 2.709 ms. Raw samples are in
link-case-index-measurement.json. This stresses repeated mismatches, not ordinary
all-valid documents. The lazy index costs O(files) additional references/strings
when needed; memory and full CI/build improvements are not measured or claimed.
