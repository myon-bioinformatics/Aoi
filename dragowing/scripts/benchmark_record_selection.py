"""Pinned-baseline selection time/memory; input construction excluded."""
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
import tracemalloc
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import records


def main():
    sha='7aade656bd427254ad4e567c04739cce1c9a3bc8'
    old=types.ModuleType('baseline_records')
    exec(subprocess.check_output(['git','show',sha+':records.py'],cwd=ROOT),old.__dict__)
    rows=[{'id':str(i % 1000), 'value':i} for i in range(10000)]
    results=[]
    for count in (1,2,100):
        ids=[str(i) for i in range(count)]
        expected=old.select_items(rows,{},ids)
        functions={'baseline':old.select_items,'indexed':records.select_items}
        samples={name:[] for name in functions}
        for repeat in range(8):
            for name in (list(functions) if repeat%2 else list(reversed(functions))):
                start=time.perf_counter_ns()
                got=functions[name](rows,{},ids)
                elapsed=time.perf_counter_ns()-start
                if got != expected:
                    raise SystemExit("selection mismatch")
                if repeat:
                    samples[name].append(elapsed)
        peaks={}
        for name,fn in functions.items():
            tracemalloc.start()
            fn(rows,{},ids)
            peaks[name]=tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        results.append({'ids':count,'samples_ns':samples,
            'median_ns':{k:statistics.median(v) for k,v in samples.items()},'one_run_peak_bytes':peaks})
    print(json.dumps({'python':sys.version,'baseline_sha':sha,'rows':10000,'results':results},indent=2))


if __name__=='__main__':
    main()
