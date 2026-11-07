"""Consume Ironmate Layer 21 through its stdlib JSON bridge; no vendored copy."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def verify(root):
    root = Path(root).resolve()
    if not (root / 'scripts/instance_scene.py').is_file():
        raise ValueError('Ironmate instance_scene.py is required')
    def detection(x):
        return dict(class_name='same-archetype', fingerprint=63, x=x, y=0)
    payload = dict(max_distance=5, frames=[
        [detection(0), detection(10)],
        [detection(3), detection(7)],
        [detection(4), detection(6)],
        [], [detection(9)]])
    result = subprocess.run([sys.executable, '-S', '-m', 'scripts.instance_scene'],
                            input=json.dumps(payload), text=True,
                            capture_output=True, cwd=root, timeout=30, check=True)
    actual = json.loads(result.stdout)
    expected = {'track_ids': [[0, 1], [0, 1], [1, 0], [], [2]]}
    if actual != expected:
        raise SystemExit(f'trajectory contract mismatch: {actual!r}')
    return actual


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ironmate-root', required=True)
    print(json.dumps(verify(parser.parse_args(argv).ironmate_root)))


if __name__ == '__main__':
    raise SystemExit(main())
