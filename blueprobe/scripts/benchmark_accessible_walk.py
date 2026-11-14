"""Seven alternating traversal comparisons; no HTML parsing in timed region."""
import json, statistics, sys, time, tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import blueprobe as names  # _Node・_Tree・_walk は blueprobe.py にある


def recursive(node):
    for child in node.children:
        if isinstance(child,names._Node):
            yield child
            yield from recursive(child)


def main():
    records=[]
    for depth in (16,512):
        tree=names._Tree()
        tree.feed('<div>'*depth+'text'+'</div>'*depth)
        funcs={'recursive':recursive,'iterative':names._walk}
        samples={k:[] for k in funcs}
        expected=list(recursive(tree.root))
        for repeat in range(8):
            for k in (list(funcs) if repeat%2 else list(reversed(funcs))):
                start=time.perf_counter_ns()
                result=list(funcs[k](tree.root))
                elapsed=time.perf_counter_ns()-start
                if result != expected:
                    raise SystemExit(f"traversal mismatch: {k}, depth={depth}")
                if repeat: samples[k].append(elapsed)
        peaks={}
        for k,fn in funcs.items():
            tracemalloc.start()
            result = list(fn(tree.root))
            if result != expected:
                raise SystemExit(f"traversal mismatch during memory measurement: {k}")
            peaks[k]=tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        records.append({'depth':depth,'samples_ns':samples,
            'median_ns':{k:statistics.median(v) for k,v in samples.items()},'one_run_peak_bytes':peaks})
    print(json.dumps({'python':sys.version,'records':records},indent=2))


if __name__=='__main__': main()
