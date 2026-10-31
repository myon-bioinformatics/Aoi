# Feature-scoped research environment benchmark

This opt-in Linux experiment runs the actual
`pythdragoras/pythdragoras.py:cumulative_test` implementation with Polars. It is
not another stdlib replacement, nor a benchmark of the whole Aoi research suite.
Existing dependencies, lock, full development/oracle tests and CI remain intact.
Parent PR #195 is separate and stays Draft.

## Reproduce

Use Linux, a trusted installed uv, and Python 3.12 (compatible lock wheels required):

```sh
python scripts/nano/benchmark.py --output /tmp/aoi-nano-comparison --repeats 3 --workers 4
/tmp/aoi-nano-comparison/development/venv/bin/python -m unittest discover -s tests -p test_nano_benchmark.py
/tmp/aoi-nano-comparison/development/venv/bin/python -m pytest -x -q pythdragoras/tests/test_pythdragoras.py
```

The output directory must not exist. Each side gets its own fresh uv cache and
venv. Locked offline export does not download packages; the subsequent explicit
wheel installation does. Feature export selects runtime and prunes NumPy, HTTPX
and Markdown and their unneeded dependency trees; development uses the existing
default dev + runtime groups. Both omit installation of the local Aoi package:
the same checkout's source is loaded directly. No new manifest, lock resolution,
upgrade, source build, optional solver or dependency deletion is performed.
Installation uses exported hashes and binary wheels only. Failure is recorded
with null unmeasured values, logs and a failing exit; it never falls back to
another version. Input SHA-256 values are checked again after execution.

## Definitions and limits

- Install seconds: one wall-time sample per environment, including network,
  wheel extraction and installation; excludes venv creation and export.
  Environments run sequentially, feature first; this is not a randomized network
  performance experiment. Fresh uv caches do not imply cold host filesystem or
  proxy caches. `installed_bytes` sums apparent regular-file bytes in the venv,
  excludes symlinks (including base Python), and is not allocated disk blocks.
  Cache bytes are reported separately; hardlinks may share storage with caches.
- Interpreter startup: fresh isolated Python `-c pass`, three raw samples.
  Startup plus research: fresh interpreter, module/native imports, four inputs,
  serialization and barrier readiness; three samples and median. There is no
  claim of cold filesystem startup, throughput gain or statistical significance.
- RSS: Linux `/proc/self/status` VmRSS reported by each child after all inputs.
  Single-process ru_maxrss is also recorded (Linux KiB converted to bytes).
  For parallel memory, N independent processes hold at the same post-workload
  barrier and their self-reported RSS values are summed. These stable-point
  readings are not a synchronized peak sampler. Sum RSS double-counts shared
  pages; it is not PSS, cgroup memory, whole-host memory or sum of process peaks.
- `POLARS_MAX_THREADS`, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` are fixed to 1
  on both sides. Four workers measure this small slice, not scalability of all
  research workloads. Unused installed packages need not affect resident memory.
- Same fixture rows test valid, missing-column, invalid-type and typed-empty
  inputs. Parsed complete outputs and structured exception type/message are
  compared exactly across repeats, environments and parallel workers. This
  comparison is limited to these inputs. Scalar arithmetic/erfc assertions and
  the existing 25 research tests remain an independent correctness check.

Dedicated `nano-benchmark.yml` runs this comparison and oracle tests on PRs that
change the experiment, workload or lock, and supports manual dispatch. It uploads
JSON, exported requirements and logs even after failure. No timing/RSS regression
threshold is imposed on shared GitHub runners; semantic mismatch fails CI.

## Local evidence (2026-11-01)

See `docs/evidence/nano-cumulative-local.json` for source/manifest identities,
versions, raw samples, packages, outputs/errors and any unmeasured fields.
The local execution environment is not a GitHub runner. GitHub measurements
are separate workflow artifacts, not inferred from local results.
