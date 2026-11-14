"""Aoi entry: decide where things are, then run a child project's Python file (stdlib only).

  python aoi.py queryu --source npb_calendar --years 2024 --cache data/raw/npb_calendar --offline --plan
  python aoi.py pythdragoras/season_sensitivity.py --season ... --config ...
  python aoi.py dragowing --help                        # dragowing/dragowing.py (element counter)
  python aoi.py dragowing/__main__.py RESULTS           # the DRAgoWing report, from any cwd
  python aoi.py -m dragowing                            # the package, only when Aoi is already on sys.path (cwd)
  eval "$(python aoi.py)"   # POSIX sh only. Supported: Ubuntu/POSIX. Windows: not supported yet / untested.
  import aoi                # AOI_ROOT and the sibling dirs, for this process

A child is a generic single file: it does not look for its siblings. This launcher passes
``AOI_ROOT``, ``AOI_RESEARCH_CYCLE``, and only the sibling directories that child imports
(``SIBLINGS``). Those directories are appended after the caller's ``PYTHONPATH`` (an externally
supplied BlueProbe stays ahead of Aoi's). Aoi's root and ``.`` are not put on ``PYTHONPATH``.
``dragowing/`` is not one of the directories: ``dragowing.py`` would win ``import dragowing``
and hide ``dragowing.render``. pytest's ``pythonpath`` is a different list and is not copied.
``python aoi.py -m dragowing`` keeps the cwd entry, as ``python -m`` does, and does not add
Aoi's root: from an Aoi checkout it runs the package report, and from another directory the
module is not on ``sys.path``. ``dragowing/__main__.py`` does not depend on the cwd.

``-I`` and ``-E`` do not apply ``PYTHONPATH`` (``-I`` also implies ``-P``, so the script
directory is omitted). The child is started through a one-shot bootstrap
(``python [the same flags] -c``) that inserts the sibling directories into ``sys.path`` and
sets ``AOI_ROOT`` and ``AOI_RESEARCH_CYCLE`` from its own arguments before ``runpy``. The
arguments are the fallback that does not depend on the process environment. CPython still
shows the environment to ``os.environ`` under ``-I`` and ``-E``; it only ignores ``PYTHON*``
while building ``sys.path``. ``-S`` skips site (``.pth`` files do not run) and still applies
``PYTHONPATH``. ``-P`` / ``PYTHONSAFEPATH`` omits the script directory and still applies
``PYTHONPATH``. The parent's ``isolated``, ``no_site``, ``ignore_environment`` and
``safe_path`` flags are forwarded.

Under ``-I`` and ``-P`` this file appends its own directory to its own ``sys.path`` so it can
import ``aoi_paths``. That entry is not copied onto the child.

===============  ================================  ==========  ==============  ===========================
flag             PYTHONPATH on the child's sys.path  script dir  site / .pth     AOI_ROOT
===============  ================================  ==========  ==============  ===========================
(none)           caller, then this child's dirs    yes         yes             environment and bootstrap
-S               caller, then this child's dirs    yes         no              environment and bootstrap
-P               caller, then this child's dirs    no          yes             environment and bootstrap
-E               not applied; dirs still inserted  yes         yes             visible; set from the arg
-I               not applied; dirs still inserted  no          no user site    visible; set from the arg
===============  ================================  ==========  ==============  ===========================

``-I`` and ``-E`` leave the caller's ``PYTHONPATH`` in the environment (CPython does not strip
it) and do not put it on ``sys.path``. ``-I`` and ``-P`` also omit the script directory, same
as CPython: a child that imports a neighbour from its own directory at import time, before it
adds that directory itself, fails the way ``python -I that_file.py`` fails.

Supported: Ubuntu/POSIX. Windows: not supported yet / untested. ``eval "$(python aoi.py)"``
prints POSIX ``export`` lines (``shlex.quote``); nothing is saved. No Windows launcher is provided.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# -I / -P omit the script directory. aoi_paths.py sits next to this file; the child does not
# inherit this entry (it is not written to PYTHONPATH).
if sys.flags.safe_path and str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import aoi_paths

# Sibling directories each child imports. Not the child itself, not ".", not Aoi's root.
# "dragowing" is absent on purpose: that directory holds dragowing.py, which would shadow the package.
SIBLINGS: dict[str, tuple[str, ...]] = {
    "blueprobe": ("queryu",),                 # --cache: from queryu import Cache
    "queryu": ("blueprobe",),                 # extraction; the caller's BlueProbe stays first
    "nagoyaction": (),                        # its scripts add their own paths from __file__
    "sakanalytics": ("pythdragoras",),        # import propositions
    "pythdragoras": (),                       # local modules only
    "dragowing": ("pythdragoras", "queryu/ask"),  # propositions, rule_search, ask
}
_UNION = tuple(dict.fromkeys(rel for name in SIBLINGS for rel in SIBLINGS[name]))
_BARE = object()

# argv: mode, target, AOI_ROOT, AOI_RESEARCH_CYCLE, sibling dirs..., "--", script args...
_BOOTSTRAP = """\
import os, sys, runpy
mode, target, root, cycle, *rest = sys.argv[1:]
siblings = []
while rest and rest[0] != "--":
    siblings.append(rest.pop(0))
if rest[:1] == ["--"]:
    rest = rest[1:]
os.environ["AOI_ROOT"] = root
os.environ["AOI_RESEARCH_CYCLE"] = cycle
# -I/-E already ignored PYTHONPATH. Do not put it back. Sibling dirs came in as arguments.
for directory in siblings:
    if directory and directory not in sys.path:
        sys.path.append(directory)
if mode == "script" and not sys.flags.safe_path:
    script_dir = os.path.dirname(os.path.abspath(target))
    if sys.path and sys.path[0] == "":
        del sys.path[0]
    if script_dir in sys.path:
        sys.path.remove(script_dir)
    sys.path.insert(0, script_dir)
elif mode == "script" and sys.path and sys.path[0] == "":
    del sys.path[0]
sys.argv = [target, *rest]
if mode == "module":
    runpy.run_module(target, run_name="__main__", alter_sys=True)
else:
    runpy.run_path(target, run_name="__main__")
"""


def _dirs(rels: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    root = str(ROOT)
    for rel in rels:
        path = str((ROOT / rel).resolve())
        if path != root and path not in found:
            found.append(path)
    return found


def environment(env=None, *, child=_BARE) -> dict[str, str]:
    """``AOI_ROOT``, the cycle name, and the caller's ``PYTHONPATH`` with this child's dirs after it.

    No ``child`` (the ``eval`` / ``import aoi`` form) uses the union of every child's dirs.
    ``child=None`` or an unknown name adds none. The caller's entries stay in front. Aoi's root
    is not added.
    """
    env = dict(os.environ if env is None else env)
    if child is _BARE:
        rels = _UNION
    elif isinstance(child, str) and child in SIBLINGS:
        rels = SIBLINGS[child]
    else:
        rels = ()
    env["AOI_ROOT"] = str(ROOT)
    env["AOI_RESEARCH_CYCLE"] = aoi_paths.cycle_name(env.get("AOI_RESEARCH_CYCLE"))
    caller = [entry for entry in env.get("PYTHONPATH", "").split(os.pathsep) if entry]
    merged: list[str] = []
    for entry in [*caller, *_dirs(rels)]:
        if entry not in merged:
            merged.append(entry)
    env["PYTHONPATH"] = os.pathsep.join(merged)
    return env


def activate(env=None, path=None) -> dict[str, str]:
    """Put the no-target settings into this process.

    ``AOI_ROOT`` goes into ``env``. The union of sibling directories is appended to ``path``,
    so whatever is already first (the caller's own checkout, or the cwd entry) still wins.
    The cycle name is left to ``aoi_paths`` (it only goes to child processes)."""
    env = os.environ if env is None else env
    path = sys.path if path is None else path
    settings = environment(env)
    env["AOI_ROOT"] = settings["AOI_ROOT"]
    for directory in _dirs(_UNION):
        if directory not in path:
            path.append(directory)
    return settings


def interpreter_flags() -> list[str]:
    """Flags to repeat so the child interpreter matches this one.

    ``-I`` already implies ``-E`` and ``-P``. ``-S`` is separate (``-I`` does not set
    ``sys.flags.no_site``): it skips site entirely, including ``.pth`` files.
    """
    flags: list[str] = []
    if sys.flags.isolated:
        flags.append("-I")
    else:
        if sys.flags.ignore_environment:
            flags.append("-E")
        if sys.flags.safe_path:
            flags.append("-P")
    if sys.flags.no_site:
        flags.append("-S")
    return flags


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


def _child_key(cmd: list[str]) -> str | None:
    if cmd[1] == "-m":
        name = cmd[2].split(".")[0].lower() if len(cmd) > 2 else ""
        return name if name in SIBLINGS else None
    try:
        rel = Path(cmd[1]).resolve().relative_to(ROOT)
    except ValueError:
        return None
    name = rel.parts[0] if rel.parts else ""
    return name if name in SIBLINGS else None


def launch(argv: list[str]) -> tuple[list[str], dict[str, str]]:
    """Child command line (bootstrap plus the parent's flags) and the environment to give it."""
    cmd = command(argv)
    key = _child_key(cmd)
    env = environment(child=key)
    if cmd[1] == "-m":
        if len(cmd) < 3:
            raise SystemExit("aoi.py: -m にはモジュール名が要る")
        mode, target, rest = "module", cmd[2], cmd[3:]
    else:
        mode, target, rest = "script", cmd[1], cmd[2:]
    siblings = _dirs(SIBLINGS[key]) if key in SIBLINGS else []
    launched = [
        sys.executable, *interpreter_flags(), "-c", _BOOTSTRAP,
        mode, target, env["AOI_ROOT"], env["AOI_RESEARCH_CYCLE"], *siblings, "--", *rest,
    ]
    return launched, env


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        env = environment()
        # POSIX sh (Ubuntu). Windows is not supported yet / untested.
        for key in ("AOI_ROOT", "AOI_RESEARCH_CYCLE", "PYTHONPATH"):
            print(f"export {key}={shlex.quote(env[key])}")
        return 0
    cmd, env = launch(argv)
    return subprocess.run(cmd, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
activate()  # import aoi: the in-process counterpart of eval "$(python aoi.py)"
