"""Aoi entry for PythDRagoras; requires the corresponding Aoi child checkout."""
import os
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    target = root / 'pythdragoras' / 'pythdragoras.py'
    if not target.is_file():
        print(f"PythDRagoras backend not found: {target}. Use a complete Aoi checkout.", file=sys.stderr)
        return 2
    env = os.environ.copy()
    paths = [root, *(root / name for name in ("blueprobe", "queryu", "queryu/ask", "sakanalytics", "pythdragoras", "nagoyaction"))]
    env["PYTHONPATH"] = os.pathsep.join([*(str(path) for path in paths), env.get("PYTHONPATH", "")])
    return subprocess.run([sys.executable, str(target), *sys.argv[1:]], env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
