#!/usr/bin/env python3
"""Run a command with a third-party import blocked, stubbed, or wrapped.

AST surveys only see ``pkg.attr`` written on the import alias. This tool runs
the real call and records what that survey cannot see.

absent
    A meta-path finder raises ``ModuleNotFoundError`` for the package and its
    submodules. The traceback is the same import failure a missing wheel gives.
stub
    ``import pkg`` succeeds. Every attribute is another stub. The first
    operation that needs a real value (truth, length, iteration, a number)
    raises ``StubGap``. The events are the prefix of the surface; the
    traceback is the first hole.
wrap
    The installed package is delegated to. Attribute access is logged only
    when the nearest caller outside this file is project code, and only
    objects that belong to the package stay wrapped. The command can finish.
    Names logged here but absent from ``survey_third_party.py`` are the ones
    the AST missed (methods and operators on returned objects).

    python scripts/trace_surface.py absent polars -- python scripts/trace_drivers.py load_overlap
    python scripts/trace_surface.py stub polars -- python scripts/trace_drivers.py load_overlap
    python scripts/trace_surface.py wrap polars -- python scripts/trace_drivers.py load_overlap
    python scripts/trace_surface.py collect --out docs/evidence/trace-surfaces.json

``--apply`` is the in-process hook used by the commands above. Exit status of
``wrap`` is the command's status. ``absent`` and ``stub`` exit 0 when they
captured a traceback.
"""
from __future__ import annotations

import argparse
import importlib.machinery
import inspect
import json
import os
import runpy
import subprocess
import sys
import tempfile
import traceback
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = Path(__file__).resolve()

# Drivers the summary report re-runs. Each entry is one live observation.
COLLECT = [
    ("absent", "polars", "load_overlap"),
    ("stub", "polars", "load_overlap"),
    ("wrap", "polars", "load_overlap"),
    ("wrap", "numpy", "load_overlap"),
    ("wrap", "numpy", "suggest_index"),
    ("wrap", "numpy", "littlebit_svd"),
    ("absent", "selectolax", "selectolax_css"),
    ("stub", "selectolax", "selectolax_css"),
    ("wrap", "selectolax", "selectolax_css"),
    ("absent", "httpx", "httpx_get"),
    ("stub", "httpx", "httpx_get"),
    ("wrap", "httpx", "httpx_get"),
    ("absent", "markdown", "render_md"),
    ("wrap", "markdown", "render_md"),
    ("absent", "ortools", "ortools_import"),
    ("stub", "ortools", "ortools_import"),
    ("absent", "pandas", "pandas_surface"),
    ("stub", "pandas", "pandas_surface"),
]


class StubGap(TypeError):
    """The stub proxy was asked for a real value."""


class Log:
    def __init__(self, package: str, root: Path):
        self.package = package
        self.root = str(root)
        self.counts: Counter = Counter()
        self.first: list[dict] = []
        self._seen: set[tuple] = set()

    def project_caller(self) -> str | None:
        """Nearest frame that is neither this tool nor an import bootstrap."""
        frame = sys._getframe(1)
        while frame is not None:
            filename = frame.f_code.co_filename
            if filename == str(TOOL) or filename.startswith("<"):
                frame = frame.f_back
                continue
            if filename.startswith(self.root) and "site-packages" not in filename:
                rel = os.path.relpath(filename, self.root)
                return f"{rel}:{frame.f_lineno}"
            return None
        return None

    def record(self, op: str, qual: str, name: str) -> None:
        where = self.project_caller()
        if where is None:
            return
        key = (op, qual, name)
        self.counts[key] += 1
        if key in self._seen:
            return
        self._seen.add(key)
        file, line = where.rsplit(":", 1)
        self.first.append({"op": op, "qual": qual, "name": name, "file": file, "line": int(line)})

    def payload(self) -> list[dict]:
        rows = []
        for row in self.first:
            key = (row["op"], row["qual"], row["name"])
            rows.append({**row, "count": self.counts[key]})
        return rows


def _from_package(obj, package: str) -> bool:
    if isinstance(obj, (bool, int, float, str, bytes, type(None))):
        return False
    module = getattr(obj, "__module__", None)
    if not isinstance(module, str):
        module = getattr(type(obj), "__module__", "") or ""
    if not (module == package or module.startswith(package + ".")):
        return False
    # A numpy 0-d scalar stays bare so ``1 + np.log(x)`` does not need a proxy.
    # Do not probe ``ndim`` on other packages: a Polars Expr treats ``==`` as data.
    if package == "numpy":
        try:
            ndim = getattr(obj, "ndim", None)
        except Exception:
            ndim = None
        if ndim == 0:
            return False
    return True


class Proxy:
    """Delegates to a real package object and logs project-side access."""

    __slots__ = ("_obj", "_qual", "_log")

    def __init__(self, obj, qual: str, log: Log):
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_qual", qual)
        object.__setattr__(self, "_log", log)

    def __getattr__(self, name):
        self._log.record("getattr", self._qual, name)
        value = getattr(self._obj, name)
        # Bound methods of extension types often report a non-package __module__.
        # Wrap every callable so the call still unwraps proxies before delegation.
        if callable(value):
            return Proxy(value, f"{self._qual}.{name}", self._log)
        return expose(value, f"{self._qual}.{name}", self._log)

    def __call__(self, *args, **kwargs):
        self._log.record("call", self._qual, "")
        out = self._obj(*[_unwrap(arg) for arg in args], **{key: _unwrap(value) for key, value in kwargs.items()})
        return expose(out, f"{self._qual}()", self._log)

    def __repr__(self):
        return repr(self._obj)

    def __str__(self):
        return str(self._obj)


def _bind(name: str):
    def op(self, *args, **kwargs):
        self._log.record("dunder", self._qual, name)
        fn = getattr(self._obj, name)
        out = fn(*[_unwrap(arg) for arg in args], **{key: _unwrap(value) for key, value in kwargs.items()})
        if name in {"__bool__", "__int__", "__float__", "__index__", "__len__", "__hash__", "__exit__"}:
            return out
        return expose(out, f"{self._qual}.{name}", self._log)

    op.__name__ = name
    return op


for _name in (
    "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__add__", "__radd__", "__sub__", "__rsub__", "__mul__", "__rmul__",
    "__truediv__", "__rtruediv__", "__floordiv__", "__rfloordiv__",
    "__mod__", "__rmod__", "__matmul__", "__rmatmul__", "__pow__", "__rpow__",
    "__and__", "__rand__", "__or__", "__ror__", "__xor__", "__rxor__",
    "__invert__", "__neg__", "__pos__", "__abs__",
    "__getitem__", "__setitem__", "__contains__",
    "__len__", "__bool__", "__int__", "__float__", "__index__",
    "__enter__", "__exit__",
):
    setattr(Proxy, _name, _bind(_name))


def __iter__(self):
    self._log.record("dunder", self._qual, "__iter__")
    for item in self._obj:
        yield expose(item, f"{self._qual}[]", self._log)


Proxy.__iter__ = __iter__  # type: ignore[method-assign]


def _unwrap(obj):
    if isinstance(obj, Proxy):
        return obj._obj
    if type(obj) is list:
        return [_unwrap(item) for item in obj]
    if type(obj) is tuple:
        return tuple(_unwrap(item) for item in obj)
    if type(obj) is dict:
        return {key: _unwrap(value) for key, value in obj.items()}
    return obj


_CACHE: dict[int, Proxy] = {}
_ARMED: set[int] = set()


def expose(obj, qual: str, log: Log):
    if type(obj) is list:
        return [expose(item, qual, log) for item in obj]
    if type(obj) is tuple:
        return tuple(expose(item, qual, log) for item in obj)
    if isinstance(obj, Proxy) or not _from_package(obj, log.package):
        return obj
    if inspect.ismodule(obj):
        return arm_module(obj, log)
    cached = _CACHE.get(id(obj))
    if cached is None:
        cached = Proxy(obj, qual, log)
        _CACHE[id(obj)] = cached
    return cached


def arm_module(module, log: Log):
    if id(module) in _ARMED:
        return module
    _ARMED.add(id(module))
    package = log.package
    origin = module.__class__

    class Logged(origin):
        def __getattribute__(self, name, _log=log, _pkg=package):
            value = super().__getattribute__(name)
            if name.startswith("_") or not _log.project_caller():
                return value
            _log.record("getattr", self.__name__, name)
            return expose(value, f"{self.__name__}.{name}", _log)

    try:
        module.__class__ = Logged
    except TypeError:
        for key, value in list(vars(module).items()):
            if key.startswith("_"):
                continue
            wrapped = expose(value, f"{module.__name__}.{key}", log)
            if wrapped is not value:
                try:
                    setattr(module, key, wrapped)
                except (AttributeError, TypeError):
                    pass
    return module


class AbsentLoader:
    def __init__(self, fullname: str):
        self.fullname = fullname

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise ModuleNotFoundError(
            f"No module named {self.fullname!r} (trace_surface absent: import blocked)"
        )


class Stub:
    def __init__(self, qual: str, log: Log):
        object.__setattr__(self, "_qual", qual)
        object.__setattr__(self, "_log", log)

    def __getattr__(self, name):
        self._log.record("getattr", self._qual, name)
        return Stub(f"{self._qual}.{name}", self._log)

    def __call__(self, *args, **kwargs):
        self._log.record("call", self._qual, "")
        return Stub(f"{self._qual}()", self._log)

    def __getitem__(self, key):
        self._log.record("dunder", self._qual, "__getitem__")
        return Stub(f"{self._qual}[]", self._log)

    def __setitem__(self, key, value):
        self._log.record("dunder", self._qual, "__setitem__")
        raise StubGap(f"stub proxy cannot perform __setitem__ on {self._qual}")

    def __iter__(self):
        self._log.record("dunder", self._qual, "__iter__")
        raise StubGap(f"stub proxy cannot iterate {self._qual}")

    def __enter__(self):
        self._log.record("dunder", self._qual, "__enter__")
        return self

    def __exit__(self, *args):
        self._log.record("dunder", self._qual, "__exit__")
        return False

    def __repr__(self):
        return f"Stub({self._qual})"

    def __str__(self):
        return self._qual


def _stub_gap(name: str):
    def op(self, *args, **kwargs):
        self._log.record("dunder", self._qual, name)
        raise StubGap(f"stub proxy cannot perform {name} on {self._qual}")

    return op


def _stub_chain(name: str):
    def op(self, *args, **kwargs):
        self._log.record("dunder", self._qual, name)
        return Stub(f"{self._qual}.{name}", self._log)

    return op


for _name in ("__bool__", "__len__", "__int__", "__float__", "__index__", "__hash__"):
    setattr(Stub, _name, _stub_gap(_name))
for _name in (
    "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__add__", "__radd__", "__sub__", "__rsub__", "__mul__", "__rmul__",
    "__truediv__", "__matmul__", "__and__", "__rand__", "__or__", "__ror__",
    "__invert__", "__neg__", "__contains__",
):
    setattr(Stub, _name, _stub_chain(_name))


class StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name in {"_log", "_qual"}:
            raise AttributeError(name)
        log = self.__dict__["_log"]
        qual = self.__dict__["_qual"]
        log.record("getattr", qual, name)
        return Stub(f"{qual}.{name}", log)


class StubLoader:
    def __init__(self, log: Log):
        self.log = log

    def create_module(self, spec):
        module = StubModule(spec.name)
        module.__dict__["_log"] = self.log
        module.__dict__["_qual"] = spec.name
        # Submodule imports (``selectolax.lexbor``, ``ortools.sat``) require a package.
        module.__path__ = []
        module.__package__ = spec.name.rpartition(".")[0] or spec.name
        return module

    def exec_module(self, module):
        return None


class WrapLoader:
    def __init__(self, real, log: Log):
        self.real = real
        self.log = log

    def create_module(self, spec):
        create = getattr(self.real, "create_module", None)
        return None if create is None else create(spec)

    def exec_module(self, module):
        self.real.exec_module(module)
        name = module.__name__
        if name == self.log.package or name.startswith(self.log.package + "."):
            arm_module(module, self.log)


class Finder:
    def __init__(self, mode: str, package: str, log: Log):
        self.mode = mode
        self.package = package
        self.log = log
        self._busy: set[str] = set()

    def find_spec(self, fullname, path, target=None):
        if fullname != self.package and not fullname.startswith(self.package + "."):
            return None
        if fullname in self._busy:
            return None
        if self.mode == "absent":
            return importlib.machinery.ModuleSpec(fullname, AbsentLoader(fullname))
        if self.mode == "stub":
            return importlib.machinery.ModuleSpec(fullname, StubLoader(self.log))
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
        spec.loader = WrapLoader(spec.loader, self.log)
        return spec


def install(mode: str, package: str, root: Path) -> Log:
    log = Log(package, root)
    for name in list(sys.modules):
        if name == package or name.startswith(package + "."):
            del sys.modules[name]
    sys.meta_path.insert(0, Finder(mode, package, log))
    return log


def surface_names(events: list[dict], package: str) -> list[str]:
    """Attribute and operator names touched from project code.

    Call paths (``read_ndjson().select``) stay in the event log. The name set
    is the attribute itself, which is what an AST survey would have to count.
    """
    del package
    names = {event["name"] for event in events if event["op"] in {"getattr", "dunder"} and event["name"]}
    return sorted(names)


_AST_CACHE: dict[tuple[str, str], list[str]] = {}


def ast_names(package: str, root: Path) -> list[str]:
    key = (package, str(root))
    if key in _AST_CACHE:
        return _AST_CACHE[key]
    sys.path.insert(0, str(root / "scripts"))
    import survey_third_party as survey

    data = survey.survey(root)
    pkg = data["packages"].get(package)
    found = sorted(pkg["attributes"]) if pkg else []
    _AST_CACHE[key] = found
    return found


def _explained(token: str, known: set[str]) -> bool:
    """``svd`` is already counted when the AST saw ``linalg.svd``."""
    if token in known:
        return True
    return any(key == token or key.endswith("." + token) or key.startswith(token + ".") for key in known)


def missed(events: list[dict], package: str, root: Path) -> list[str]:
    known = set(ast_names(package, root))
    return [name for name in surface_names(events, package) if not _explained(name, known)]


def _result(mode: str, package: str, command: list[str], log: Log, status: int, error: str | None, root: Path) -> dict:
    events = log.payload()
    return {
        "mode": mode,
        "package": package,
        "command": command,
        "status": status,
        "exception": (error.splitlines()[-1] if error else None),
        "traceback": error,
        "events": events,
        "dynamic_attributes": surface_names(events, package),
        "ast_attributes": ast_names(package, root),
        "missed_by_ast": missed(events, package, root),
    }


def _split_dd(argv: list[str]) -> tuple[list[str], list[str]]:
    """Options stay on the left of ``--``. argparse REMAINDER swallows them."""
    if "--" not in argv:
        return argv, []
    index = argv.index("--")
    return argv[:index], argv[index + 1:]


def apply_main(argv: list[str]) -> int:
    left, command = _split_dd(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("mode", choices=["absent", "stub", "wrap"])
    parser.add_argument("package")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(left)
    kind, target, rest = _split_command(command)
    log = install(args.mode, args.package, args.root)
    status = 0
    error = None
    try:
        if kind == "c":
            sys.argv = ["-c", *rest]
            exec(compile(target, "<trace>", "exec"), {"__name__": "__main__"})
        elif kind == "m":
            sys.argv = [target, *rest]
            runpy.run_module(target, run_name="__main__")
        else:
            sys.argv = [target, *rest]
            # ``python script.py`` puts the script directory on sys.path. runpy does not.
            script_dir = str(Path(target).resolve().parent)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            runpy.run_path(target, run_name="__main__")
    except SystemExit as exc:
        status = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except BaseException:
        status = 1
        error = traceback.format_exc()
    args.out.write_text(json.dumps(_result(args.mode, args.package, command, log, status, error, args.root), indent=2) + "\n", encoding="utf-8")
    return status


def _split_command(command: list[str]) -> tuple[str, str, list[str]]:
    if not command:
        raise SystemExit("trace_surface: command is missing (use -- python script.py)")
    parts = list(command)
    if Path(parts[0]).name.startswith("python"):
        parts = parts[1:]
    if not parts:
        raise SystemExit("trace_surface: command is missing")
    if parts[0] == "-c":
        return "c", parts[1], parts[2:]
    if parts[0] == "-m":
        return "m", parts[1], parts[2:]
    return "path", str(Path(parts[0]).resolve()), parts[1:]


def _launch(mode: str, package: str, command: list[str], out: Path, root: Path) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--apply", mode, package, "--out", str(out), "--root", str(root), "--", *command],
        cwd=root,
    )
    if not out.exists():
        raise SystemExit(f"trace_surface: no output from {mode} {package} (status {proc.returncode})")
    data = json.loads(out.read_text(encoding="utf-8"))
    data["launcher_status"] = proc.returncode
    if mode == "wrap" and proc.returncode != 0:
        tail = (data.get("traceback") or "")[-1500:]
        print(tail, file=sys.stderr)
        raise SystemExit(proc.returncode)
    if mode == "absent" and not data.get("traceback"):
        print(f"absent {package} finished without a traceback", file=sys.stderr)
        raise SystemExit(proc.returncode or 1)
    if mode == "stub" and not data.get("traceback") and not data.get("events"):
        print(f"stub {package} recorded neither events nor a traceback", file=sys.stderr)
        raise SystemExit(proc.returncode or 1)
    _print_summary(data)
    return data


def _print_summary(data: dict) -> None:
    missed_names = ", ".join(data.get("missed_by_ast") or []) or "(none)"
    print(
        f"{data['mode']} {data['package']}: status={data['status']} "
        f"events={len(data['events'])} missed_by_ast={missed_names}"
    )
    if data.get("exception"):
        print(f"  {data['exception']}")


def _summary(data: dict) -> dict:
    """Drop per-event rows so the committed evidence stays a surface, not a log."""
    command = list(data["command"])
    if command and Path(command[0]).name.startswith("python"):
        command = ["python", *command[1:]]
    return {
        "mode": data["mode"],
        "package": data["package"],
        "command": command,
        "status": data["status"],
        "exception": data["exception"],
        "dynamic_attributes": data["dynamic_attributes"],
        "ast_attributes": data["ast_attributes"],
        "missed_by_ast": data["missed_by_ast"],
        "first_events": [
            {"op": event["op"], "qual": event["qual"], "name": event["name"], "file": event["file"], "line": event["line"]}
            for event in data["events"]
        ],
    }


def _comparable(payload: dict) -> list[dict]:
    rows = []
    for run in payload["runs"]:
        exception = run.get("exception") or ""
        rows.append({
            "driver": run["driver"],
            "dynamic_attributes": run["dynamic_attributes"],
            "exception_type": exception.split(":", 1)[0],
            "missed_by_ast": run["missed_by_ast"],
            "mode": run["mode"],
            "package": run["package"],
            "status": run["status"],
        })
    return rows


def collect(out: Path, root: Path, check: bool = False) -> int:
    runs = []
    work = Path(tempfile.mkdtemp(prefix="trace-surface-"))
    for mode, package, driver in COLLECT:
        target = work / f"{mode}-{package}-{driver}.json"
        command = [sys.executable, "scripts/trace_drivers.py", driver]
        data = _launch(mode, package, command, target, root)
        runs.append({"driver": driver, **_summary(data)})
    payload = {"schema": 1, "runs": runs}
    if check:
        previous = json.loads(out.read_text(encoding="utf-8"))
        if _comparable(previous) != _comparable(payload):
            print(f"{out} does not match a fresh collect. Re-run without --check.", file=sys.stderr)
            return 1
        print(f"{out} ok ({len(runs)} runs)")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(runs)} runs)")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--apply"]:
        return apply_main(argv)
    left, command = _split_dd(argv)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["absent", "stub", "wrap", "collect"])
    parser.add_argument("package", nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="re-run collect and compare surfaces to --out")
    args = parser.parse_args(left)
    if args.mode == "collect":
        return collect(args.out or (args.root / "docs" / "evidence" / "trace-surfaces.json"), args.root, check=args.check)
    if not args.package:
        raise SystemExit("package is required")
    out = args.out or (args.root / "docs" / "evidence" / f"trace-{args.mode}-{args.package}.json")
    _launch(args.mode, args.package, command, out, args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
