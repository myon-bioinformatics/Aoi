#!/usr/bin/env python3
"""同じ入力を fresh process で比較し、canonical JSON 一致・時間・メモリを記録する。

python scripts/benchmark_overlap.py --results /path/to/Aoi/cycles/c001-chunichi/outputs
stdout だけに記録する。入力ファイルは変更しない。Linux/macOS の RSS は OS の peak。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.machinery
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import types


def worker(args):
    import resource
    import tracemalloc

    tracemalloc.start()
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[1]
    pkg = types.ModuleType('dragowing')
    pkg.__path__ = [str(root)]
    pkg.__spec__ = importlib.machinery.ModuleSpec('dragowing', loader=None, is_package=True)
    sys.modules['dragowing'] = pkg
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    rows = read_jsonl(args.results / 'season.jsonl')
    conds = default_conditions(read_jsonl(args.results / 'propositions.jsonl'), rows)
    cold = load_overlap(args.results / 'season.jsonl', conds, backend=args.worker)
    cold_seconds = time.perf_counter() - started
    _, cold_traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    durations = []
    for _ in range(args.warm_repeats):
        started = time.perf_counter()
        result = load_overlap(args.results / 'season.jsonl', conds, backend=args.worker)
        durations.append(time.perf_counter() - started)
        assert result == cold
    text = json.dumps(cold, ensure_ascii=False, sort_keys=True, allow_nan=False)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(dict(
        backend=args.worker, canonical_sha256=hashlib.sha256(text.encode()).hexdigest(),
        rows=len(rows), regions=len(cold['regions']), cold_seconds=cold_seconds,
        warm_median_seconds=statistics.median(durations),
        python_peak_bytes=cold_traced_peak,
        process_peak_rss_bytes=rss if sys.platform == 'darwin' else rss * 1024,
        imported_libraries={name: getattr(sys.modules[name], '__version__', None)
                            for name in ('numpy', 'polars') if name in sys.modules},
    )))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--warm-repeats', type=int, default=7)
    parser.add_argument('--worker', choices=('native', 'stdlib'), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.repeats < 1 or args.warm_repeats < 1:
        parser.error('repeats must be positive')
    if args.worker:
        return worker(args)
    measurements = []
    for _ in range(args.repeats):
        for backend in ('native', 'stdlib'):
            started = time.perf_counter()
            proc = subprocess.run([
                sys.executable, str(Path(__file__).resolve()), '--results', str(args.results.resolve()),
                '--worker', backend, '--warm-repeats', str(args.warm_repeats),
            ], capture_output=True, text=True, check=True)
            measurement = json.loads(proc.stdout)
            measurement['process_wall_seconds'] = time.perf_counter() - started
            measurements.append(measurement)
    assert len({m['canonical_sha256'] for m in measurements}) == 1, 'backend JSON differs'
    metrics = ('cold_seconds', 'warm_median_seconds', 'python_peak_bytes',
               'process_peak_rss_bytes', 'process_wall_seconds')
    print(json.dumps(dict(
        python=sys.version, platform=platform.platform(), repeats=args.repeats,
        warm_repeats=args.warm_repeats,
        input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                      (args.results / 'season.jsonl', args.results / 'propositions.jsonl')},
        medians={backend: {key: statistics.median(m[key] for m in measurements if m['backend'] == backend)
                          for key in metrics} for backend in ('native', 'stdlib')},
        samples=measurements,
        memory_note='RSS includes native allocations and process overhead; tracemalloc peak covers Python-tracked cold allocations only. Cold timing includes tracemalloc overhead; warm timing does not.',
    ), ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
