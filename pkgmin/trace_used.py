#!/usr/bin/env python3
"""Run a real entry point with requests, tqdm, and Bio blocked, stubbed, or wrapped.

Same three observations as ``scripts/trace_surface.py`` on draft PR #93:

absent
    A meta-path finder raises ``ModuleNotFoundError``. The traceback is the
    import failure a missing wheel gives. PR #93 treats "no traceback" as a
    failed driver. Here it is a result: these packages are not imported.
stub
    ``import`` succeeds and every attribute is another stub. The first use is
    logged. A project path that never imports the package logs nothing.
wrap
    The installed package is delegated to. Attribute reads whose caller is
    project code are logged. Requires the real package.

    python pkgmin/trace_used.py absent -- python pkgmin/run_paths.py --inject none out.json
    python pkgmin/trace_used.py expect-unused
    python pkgmin/trace_used.py collect --check pkgmin/evidence/used-surface.json
"""
from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import os
import runpy
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = Path(__file__).resolve()
PACKAGES = ("requests", "tqdm", "Bio", "biopython")
DRIVER = [sys.executable, "pkgmin/run_paths.py", "--inject", "none"]


class StubGap(TypeError):
    """The stub was asked for a real value."""


class Log:
    def __init__(self, root: Path):
        self.root = str(root)
        self.hits: list[str] = []
        self.events: list[dict] = []
        self._seen: set[tuple] = set()

    def project_caller(self) -> str | None:
        frame = sys._getframe(1)
        while frame is not None:
            filename = frame.f_code.co_filename
            if filename == str(TOOL) or filename.startswith("<") or "importlib" in filename:
                frame = frame.f_back
                continue
            if "site-packages" in filename:
                return None
            if filename.startswith(self.root):
                rel = os.path.relpath(filename, self.root)
                return f"{rel}:{frame.f_lineno}"
            return None
        return None

    def hit(self, fullname: str) -> None:
        where = self.project_caller()
        if where is None:
            return
        if fullname not in self.hits:
            self.hits.append(fullname)

    def attr(self, qual: str, name: str) -> None:
        where = self.project_caller()
        if where is None:
            return
        key = (qual, name)
        if key in self._seen:
            return
        self._seen.add(key)
        file, line = where.rsplit(":", 1)
        self.events.append({"qual": qual, "name": name, "file": file, "line": int(line)})


class Stub:
    def __init__(self, qual: str, log: Log):
        object.__setattr__(self, "_qual", qual)
        object.__setattr__(self, "_log", log)

    def __getattr__(self, name):
        self._log.attr(self._qual, name)
        return Stub(f"{self._qual}.{name}", self._log)

    def __call__(self, *args, **kwargs):
        self._log.attr(self._qual, "()")
        return Stub(f"{self._qual}()", self._log)

    def __bool__(self):
        raise StubGap(self._qual)

    def __iter__(self):
        raise StubGap(self._qual)


class _Loader:
    def __init__(self, fullname: str, log: Log, mode: str, real=None):
        self.fullname = fullname
        self.log = log
        self.mode = mode
        self.real = real

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        if self.mode == "absent":
            raise ModuleNotFoundError(
                f"No module named {self.fullname!r} (pkgmin trace absent: import blocked)"
            )
        if self.mode == "stub":
            log = self.log

            def __getattr__(name, _qual=module.__name__, _log=log):
                _log.attr(_qual, name)
                return Stub(f"{_qual}.{name}", _log)

            module.__getattr__ = __getattr__
            return
        assert self.real is not None
        self.real.exec_module(module)
        log = self.log
        origin = module.__class__

        class Logged(origin):
            def __getattribute__(self, name, _log=log):
                value = super().__getattribute__(name)
                if name.startswith("_"):
                    return value
                where = _log.project_caller()
                if where is not None:
                    _log.attr(self.__name__, name)
                return value

        try:
            module.__class__ = Logged
        except TypeError:
            pass


class Finder:
    def __init__(self, mode: str, packages: tuple[str, ...], log: Log):
        self.mode = mode
        self.packages = packages
        self.log = log
        self._busy: set[str] = set()

    def find_spec(self, fullname, path, target=None):
        top = fullname.split(".", 1)[0]
        if top not in self.packages or fullname in self._busy:
            return None
        self.log.hit(fullname)
        if self.mode in {"absent", "stub"}:
            return importlib.machinery.ModuleSpec(fullname, _Loader(fullname, self.log, self.mode))
        self._busy.add(fullname)
        try:
            spec = None
            for finder in sys.meta_path:
                if finder is self:
                    continue
                find = getattr(finder, "find_spec", None)
                if find is None:
                    continue
                spec = find(fullname, path, target)
                if spec is not None:
                    break
        finally:
            self._busy.discard(fullname)
        if spec is None or spec.loader is None:
            return None
        spec.loader = _Loader(fullname, self.log, "wrap", spec.loader)
        return spec


def install(mode: str, packages: tuple[str, ...], root: Path) -> Log:
    log = Log(root)
    for name in list(sys.modules):
        if name in packages or any(name.startswith(pkg + ".") for pkg in packages):
            del sys.modules[name]
    sys.meta_path.insert(0, Finder(mode, packages, log))
    return log


def _result(mode: str, packages: tuple[str, ...], log: Log, status: int, error: str | None) -> dict:
    return {
        "mode": mode,
        "packages": list(packages),
        "status": status,
        "exception": (error.splitlines()[-1] if error else None),
        "traceback": error,
        "hits": list(log.hits),
        "dynamic_attributes": [f"{event['qual']}.{event['name']}" for event in log.events],
        "events": log.events,
    }


def _split(argv: list[str]) -> tuple[list[str], list[str]]:
    if "--" not in argv:
        return argv, []
    index = argv.index("--")
    return argv[:index], argv[index + 1:]


def apply_main(argv: list[str]) -> int:
    left, command = _split(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("mode", choices=["absent", "stub", "wrap"])
    parser.add_argument("--packages", default=",".join(PACKAGES))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(left)
    packages = tuple(part for part in args.packages.split(",") if part)
    if not command:
        raise SystemExit("trace_used: command is missing (use -- python script.py)")
    parts = list(command)
    if Path(parts[0]).name.startswith("python"):
        parts = parts[1:]
    script = str(Path(parts[0]).resolve())
    sys.argv = [script, *parts[1:]]
    script_dir = str(Path(script).resolve().parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    log = install(args.mode, packages, args.root)
    status = 0
    error = None
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        status = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except BaseException:
        status = 1
        error = traceback.format_exc()
    args.out.write_text(
        json.dumps(_result(args.mode, packages, log, status, error), indent=2) + "\n",
        encoding="utf-8",
    )
    return status


def launch(mode: str, command: list[str], out: Path, root: Path, packages: tuple[str, ...] = PACKAGES) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            sys.executable, str(TOOL), "--apply", mode,
            "--packages", ",".join(packages),
            "--out", str(out),
            "--root", str(root),
            "--", *command,
        ],
        cwd=root,
        check=False,
    )
    if not out.exists():
        raise SystemExit(f"trace_used: no output from {mode} (status {proc.returncode})")
    data = json.loads(out.read_text(encoding="utf-8"))
    data["launcher_status"] = proc.returncode
    return data


def summary(data: dict) -> dict:
    return {
        "dynamic_attributes": data["dynamic_attributes"],
        "exception": data["exception"],
        "hits": data["hits"],
        "mode": data["mode"],
        "packages": data["packages"],
        "status": data["status"],
    }


def collect(root: Path, out_dir: Path | None = None) -> list[dict]:
    work = out_dir or Path(tempfile.mkdtemp(prefix="pkgmin-trace-"))
    out_path = work / "paths-out.json"
    command = [*DRIVER, str(out_path)]
    rows = []
    for mode in ("absent", "stub"):
        data = launch(mode, command, work / f"{mode}.json", root)
        rows.append(summary(data))
    return rows


def expect_unused(root: Path) -> int:
    """Wrap the real packages. Exit 1 if project code touches them."""
    missing = [name for name in ("requests", "tqdm", "Bio") if importlib.util.find_spec(name) is None]
    if missing:
        print("wrap trace needs the real packages installed: " + ", ".join(missing), file=sys.stderr)
        return 2
    work = Path(tempfile.mkdtemp(prefix="pkgmin-wrap-"))
    command = [*DRIVER, str(work / "paths-out.json")]
    data = launch("wrap", command, work / "wrap.json", root)
    print(json.dumps(summary(data), indent=2))
    if data["status"] != 0:
        print(data.get("traceback") or "", file=sys.stderr)
        return data["status"] or 1
    if data["hits"] or data["dynamic_attributes"]:
        print("project code touched requests, tqdm, or Bio", file=sys.stderr)
        return 1
    print("wrap: no project use of requests, tqdm, or Bio")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--apply"]:
        return apply_main(argv)
    left, command = _split(argv)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["absent", "stub", "wrap", "collect", "expect-unused"])
    parser.add_argument("--check", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--packages", default=",".join(PACKAGES))
    args = parser.parse_args(left)
    if args.mode == "expect-unused":
        return expect_unused(args.root)
    if args.mode == "collect":
        rows = collect(args.root)
        if args.check:
            previous = json.loads(args.check.read_text(encoding="utf-8"))
            if previous.get("traces") != rows:
                print(f"{args.check} traces do not match a fresh collect.", file=sys.stderr)
                print(json.dumps(rows, indent=2), file=sys.stderr)
                return 1
            print(f"{args.check} traces ok ({len(rows)} runs, no imports)")
            return 0
        print(json.dumps(rows, indent=2))
        return 0
    if not command:
        raise SystemExit("command is required after --")
    packages = tuple(part for part in args.packages.split(",") if part)
    out = args.root / "pkgmin" / "evidence" / f"trace-{args.mode}.json"
    data = launch(args.mode, command, out, args.root, packages)
    print(json.dumps(summary(data), indent=2))
    if data.get("traceback"):
        print(data["traceback"], file=sys.stderr)
    return 0 if data["status"] == 0 or args.mode in {"absent", "stub"} else data["status"]


if __name__ == "__main__":
    raise SystemExit(main())
