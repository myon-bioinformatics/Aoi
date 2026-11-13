"""Run from repository root: python -S -m scripts.benchmark_neighbor_retention."""
import json, random, statistics, subprocess, sys, time, tracemalloc, types
import neighbors


def main():
    sha='95cfacd4f8aeb29eda0696a61f503e25a8789fce'
    old=types.ModuleType('baseline')
    exec(subprocess.check_output(['git','show',sha+':neighbors.py']),old.__dict__)
    rng=random.Random(20261104)
    rows=[{'team':str(i),'season':2024,'league':'L','upper_half':bool(i%2),
           'rf_adv':rng.randrange(100),'ra_adv':rng.randrange(100),'vs_lower_wpct':rng.random()}
          for i in range(200)]
    expected=old.discover(rows)
    funcs={'baseline':old.discover,'current':neighbors.discover}
    samples={k:[] for k in funcs}
    for repeat in range(4):
        for k in (list(funcs) if repeat%2 else list(reversed(funcs))):
            start=time.perf_counter_ns()
            result=funcs[k](rows)
            elapsed=time.perf_counter_ns()-start
            if result != expected:
                raise SystemExit(f"report mismatch: {k}")
            if repeat: samples[k].append(elapsed)
    peaks={}
    for k,fn in funcs.items():
        tracemalloc.start()
        if fn(rows) != expected:
            raise SystemExit(f"report mismatch during memory measurement: {k}")
        peaks[k]=tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
    for size in range(30):
        subset=rows[:size]
        if neighbors.discover(subset) != old.discover(subset):
            raise SystemExit(f"subset report mismatch: size={size}")
    print(json.dumps({'baseline_sha':sha,'seed':20261104,'python':sys.version,
        'rows':len(rows),'samples_ns':samples,'median_ns':{k:statistics.median(v) for k,v in samples.items()},
        'one_run_peak_bytes':peaks,'parity':'complete report equality including 30 smaller subsets'},indent=2))


if __name__=='__main__': main()
