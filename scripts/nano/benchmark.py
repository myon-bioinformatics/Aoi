#!/usr/bin/env python3
"""Linux opt-in locked-wheel benchmark. Never resolve upgrades or edit manifests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import selectors
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORKLOAD = Path(__file__).with_name('workload.py')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv, **kw):
    return subprocess.run(argv, check=True, text=True, capture_output=True, timeout=600, **kw)


def directory_bytes(path):
    # Apparent bytes of regular files, excludes symlinked base interpreter.
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())


def resident(pid):
    for line in Path(f'/proc/{pid}/status').read_text().splitlines():
        if line.startswith('VmRSS:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('VmRSS unavailable')


def observe(python, workers, env):
    procs = []
    started = time.perf_counter()
    try:
        for _ in range(workers):
            procs.append(subprocess.Popen([str(python), '-I', str(WORKLOAD), '--hold'],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, env=env))
        # communicate is not used until release: each child emits one small JSON line.
        # External watchdog (CLI alarm/CI timeout) also bounds a stalled barrier.
        reports = []
        for p in procs:
            with selectors.DefaultSelector() as selector:
                selector.register(p.stdout, selectors.EVENT_READ)
                if not selector.select(timeout=60):
                    raise RuntimeError('worker readiness timeout')
                reports.append(json.loads(p.stdout.readline()))
        elapsed = time.perf_counter() - started
        rss = sum(r['resident_bytes'] for r in reports)
        for p in procs:
            p.stdin.write('\n')
            p.stdin.flush()
        for p in procs:
            _, stderr = p.communicate(timeout=60)
            if p.returncode or stderr:
                raise RuntimeError(f'worker failed: {p.returncode}: {stderr}')
        if any(r['cases'] != reports[0]['cases'] for r in reports):
            raise ValueError('parallel semantic mismatch')
        return {'wall_seconds': elapsed, 'sum_resident_bytes_at_barrier': rss,
                'process_peak_rss_bytes': [r['peak_rss_bytes'] for r in reports],
                'cases': reports[0]['cases']}
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
            p.wait()


def benchmark(output, uv, repeats=3, workers=4):
    if repeats < 1 or workers < 1:
        raise ValueError('repeats and workers must be positive')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    pins = {n: digest(ROOT / n) for n in ('uv.lock', 'pyproject.toml')}
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('UV_', 'PIP_', 'PYTHON')) and k not in ('VIRTUAL_ENV', 'CONDA_PREFIX')}
    env.update(POLARS_MAX_THREADS='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    result = {'schema': 'aoi-nano-benchmark/1', 'input_sha256': pins,
              'source_commit': run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).stdout.strip(),
              'workload_sha256': digest(WORKLOAD), 'platform': platform.platform(),
              'python': sys.version, 'uv': run([uv, '--version']).stdout.strip(),
              'workers': workers, 'repeats': repeats, 'environments': {}, 'equivalent': None}
    try:
        for name in ('feature', 'development'):
            folder = output / name
            folder.mkdir()
            local_env = dict(env, UV_CACHE_DIR=str(folder / 'cache'))
            req = folder / 'requirements.txt'
            args = [uv, '--no-config', 'export', '--project', str(ROOT), '--locked', '--offline',
                    '--no-python-downloads', '--python', sys.executable, '--no-emit-project',
                    '--no-header', '--format', 'requirements.txt']
            if name == 'feature':
                args += ['--no-default-groups', '--group', 'runtime']
                for package in ('numpy', 'httpx', 'markdown'):
                    args += ['--prune', package]
            req.write_text(run(args, env=local_env).stdout)
            venv = folder / 'venv'
            run([uv, '--no-config', 'venv', '--python', sys.executable, '--no-python-downloads', str(venv)], env=local_env)
            python = venv / 'bin/python'
            entry = {'requirements_sha256': digest(req), 'install_seconds': None,
                     'installed_bytes': None, 'startup_workload_seconds_median': None,
                     'single': None, 'parallel': None, 'status': 'pending'}
            result['environments'][name] = entry
            start = time.perf_counter()
            try:
                install = run([uv, '--no-config', 'pip', 'install', '--python', str(python),
                               '--require-hashes', '--only-binary', ':all:', '-r', str(req)], env=local_env)
                entry['install_seconds'] = time.perf_counter() - start
                (folder / 'install.log').write_text(install.stderr)
                entry['installed_bytes'] = directory_bytes(venv)
                entry['cache_bytes_after_install'] = directory_bytes(folder / 'cache')
                entry['packages'] = json.loads(run([uv, 'pip', 'list', '--python', str(python), '--format', 'json'], env=local_env).stdout)
                trials = [observe(python, 1, local_env) for _ in range(repeats)]
                if any(t['cases'] != trials[0]['cases'] for t in trials):
                    raise ValueError('repeat semantic mismatch')
                entry['single'] = trials
                startup = []
                for _ in range(repeats):
                    began = time.perf_counter()
                    run([str(python), '-I', '-c', 'pass'], env=local_env)
                    startup.append(time.perf_counter() - began)
                entry['interpreter_startup_seconds'] = startup
                entry['startup_workload_seconds_median'] = statistics.median(t['wall_seconds'] for t in trials)
                entry['parallel'] = observe(python, workers, local_env)
                entry['status'] = 'measured'
            except (subprocess.SubprocessError, OSError, ValueError, RuntimeError) as exc:
                entry['status'] = 'not_measured'
                entry['reason'] = str(exc)
                if isinstance(exc, subprocess.CalledProcessError):
                    (folder / 'failure.log').write_text(exc.stderr or '')
        a, b = result['environments'].values()
        if all(e['status'] == 'measured' for e in (a, b)):
            result['equivalent'] = a['single'][0]['cases'] == b['single'][0]['cases'] == a['parallel']['cases'] == b['parallel']['cases']
    finally:
        result['inputs_unchanged'] = pins == {n: digest(ROOT / n) for n in pins}
        (output / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    return result


if __name__ == '__main__':
    import signal
    signal.alarm(1800)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--uv', default='uv')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    report = benchmark(args.output, args.uv, args.repeats, args.workers)
    print(json.dumps({'result': str(args.output / 'result.json'), 'equivalent': report['equivalent']}))
    sys.exit(0 if report['equivalent'] and report['inputs_unchanged'] else 1)
