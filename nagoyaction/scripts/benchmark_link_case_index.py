"""Run from repo root with python -S -m scripts.benchmark_link_case_index."""
import json, statistics, subprocess, tempfile, time, types
from pathlib import Path
from nagoyaction import linkcheck  # linkcheck は nagoyaction.py の中


def main():
    sha='da68f374ad1ae7c786f926190b98c94920d91420'
    old=types.ModuleType('baseline')
    exec(subprocess.check_output(['git','show',sha+':linkcheck.py']),old.__dict__)
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        files=['README.md']+[f'Target{i}.txt' for i in range(2000)]
        (root/'README.md').write_text(' '.join(f'[link](target{i}.txt)' for i in range(500)),encoding='utf-8')
        expected=old.check_local(root,files)
        samples={'baseline':[],'indexed':[]}
        for repeat in range(4):
            for name in (list(samples) if repeat%2 else list(reversed(samples))):
                fn=old.check_local if name=='baseline' else linkcheck.check_local
                start=time.perf_counter_ns()
                got=fn(root,files)
                elapsed=time.perf_counter_ns()-start
                if got != expected:
                    raise SystemExit("link report mismatch")
                if repeat:samples[name].append(elapsed)
    print(json.dumps({'baseline_sha':sha,'files':2001,'links':500,'samples_ns':samples,
                     'median_ns':{k:statistics.median(v) for k,v in samples.items()}},indent=2))


if __name__=='__main__':main()
