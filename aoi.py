"""Aoi entry: decide where things are, then run a child project's Python file (stdlib only).

  python aoi.py queryu --source npb_calendar --years 2024 --cache data/raw/npb_calendar --offline --plan
  python aoi.py pythdragoras/npb/season_sensitivity.py --season ... --config ...
  python aoi.py -m dragowing cycles/c001-chunichi/outputs
  eval "$(python aoi.py)"      # the same settings for this shell only (nothing is saved)
  import aoi                   # the same settings for this Python process (sys.path and AOI_ROOT)

The run-time mirror of conftest.py: conftest.py sets AOI_ROOT and the import paths for pytest, and this
file sets them for a child process, a shell or the importing process. The layout itself stays in
aoi_paths.py, NPB tables in aoi_npb.py. A child (the file named after its project) is a generic single
file: it does not look for its siblings itself. Where it works with one (QueRyu with BlueProbe, DRAgoWing
with PythDRagoras and QueRyu, ...), the import path comes from here.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import aoi_paths

ROOT = Path(__file__).resolve().parent


def environment(env=None) -> dict[str, str]:
    """AOI_ROOT, the cycle name and the import paths pytest uses (pyproject.toml), for a child process."""
    env = dict(os.environ if env is None else env)
    paths = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["pytest"]["ini_options"]["pythonpath"]
    env["AOI_ROOT"] = str(ROOT)
    env["AOI_RESEARCH_CYCLE"] = aoi_paths.cycle_name(env.get("AOI_RESEARCH_CYCLE"))
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [*(str((ROOT / p).resolve()) for p in paths), env.get("PYTHONPATH")]))
    return env


def activate(env=None, path=None) -> dict[str, str]:
    """Put the same settings into this process: AOI_ROOT into ``env`` and the import paths onto the end of
    ``path``, so whatever is already first (the caller's own checkout) still wins. The cycle name is left to
    aoi_paths (it only goes to child processes)."""
    env = os.environ if env is None else env
    path = sys.path if path is None else path
    settings = environment(env)
    env["AOI_ROOT"] = settings["AOI_ROOT"]
    path.extend(p for p in settings["PYTHONPATH"].split(os.pathsep) if p and p not in path)
    return settings


def command(argv: list[str]) -> list[str]:
    """``queryu`` -> queryu/queryu.py; a path under Aoi -> that file; ``-m name`` -> the module."""
    target, *rest = argv
    if target == "-m":
        return [sys.executable, *argv]
    path = ROOT / target if target.endswith(".py") else ROOT / target.lower() / f"{target.lower()}.py"
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise SystemExit("aoi.py: target must be a Python file under Aoi")
    if not path.is_file():
        raise SystemExit(f"aoi.py: {path} がない。子の名前（queryu など）か Aoi の中の .py を渡す")
    return [sys.executable, str(path), *rest]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    env = environment()
    if not argv:
        for key in ("AOI_ROOT", "AOI_RESEARCH_CYCLE", "PYTHONPATH"):
            print(f"export {key}={shlex.quote(env[key])}")
        return 0
    return subprocess.run(command(argv), env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
activate()  # import aoi: the in-process counterpart of eval "$(python aoi.py)"
