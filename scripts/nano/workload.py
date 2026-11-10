"""Real Polars research slice; JSON protocol keeps timing out of semantic output."""
import importlib.util
import json
from pathlib import Path
import resource
import sys

root = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('nano_pythdragoras', root / 'pythdragoras/pythdragoras.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
import polars as pl


def evaluate(case):
    rows = [dict(team='A', team_name='Alpha', W=70, L=50, pythag_fixed=.55, pythag_var=.6),
            dict(team='A', team_name='Alpha', W=60, L=60, pythag_fixed=.5, pythag_var=.52),
            dict(team='B', team_name='Beta', W=40, L=80, pythag_fixed=.45, pythag_var=.4)]
    frame = pl.DataFrame(rows)
    if case == 'missing-column':
        frame = frame.drop('W')
    elif case == 'bad-type':
        frame = frame.with_columns(pl.lit('invalid').alias('W'))
    elif case == 'empty':
        frame = frame.head(0)
    elif case != 'valid':
        raise ValueError('unknown case')
    try:
        return {'output': module.cumulative_test(frame).to_dicts(), 'error': None}
    except Exception as exc:
        return {'output': None, 'error': {'type': type(exc).__name__, 'message': str(exc)}}


def resident(_):
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith('VmRSS:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('VmRSS unavailable')


def report():
    return {'cases': {c: evaluate(c) for c in ('valid', 'missing-column', 'bad-type', 'empty')},
            'resident_bytes': resident('self'),
            'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    print(json.dumps(report(), sort_keys=True, allow_nan=False), flush=True)
    # Hold all independently launched processes at the same post-workload barrier.
    if '--hold' in argv:
        sys.stdin.readline()


if __name__ == '__main__':
    raise SystemExit(main())
