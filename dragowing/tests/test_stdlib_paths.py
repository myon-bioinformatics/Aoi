"""代替の入口は、numpy が入った環境では動かない。"""
import ctypes, ctypes.util, importlib.util, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stdlib_paths.py"


def load_vendored(name, relpath):
    """Load a vendored file by path under a repo-unique name (cli_args README: Loading a vendored copy)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / relpath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


_cli_args = load_vendored("dragowing_cli_args", "vendor/cli_args/cli_args.py")
run_cli = _cli_args.run_cli


def test_min_refuses_while_numpy_is_installed(tmp_path):
    proc = run_cli(RUNNER, "--deps", "min", str(tmp_path / "out.json"))
    assert proc.returncode != 0
    assert "numpy" in proc.stderr
    assert not (tmp_path / "out.json").exists()


import pytest


def _runner_module():
    spec = importlib.util.spec_from_file_location("stdlib_runner_under_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("previous", [None, "0", "1"])
def test_min_numpy_never_probes_or_loads_native_libraries(monkeypatch, previous):
    runner = _runner_module()
    for name in ("rule_search", "dragowing.overlap", "numpy"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    if previous is None:
        monkeypatch.delenv("NUMPY_MIN_PURE", raising=False)
    else:
        monkeypatch.setenv("NUMPY_MIN_PURE", previous)

    def forbidden(*args, **kwargs):
        raise AssertionError("stdlib substitute must not probe or load native libraries")

    monkeypatch.setattr(ctypes, "CDLL", forbidden)
    monkeypatch.setattr(ctypes.util, "find_library", forbidden)
    # Register restoration of the module inserted by the startup loader.
    monkeypatch.setitem(sys.modules, "numpy", None)
    module = runner._preload_numpy_min()
    assert module.BACKEND == "stdlib"
    assert module._lapack is None and module._blas is None
    assert os.environ.get("NUMPY_MIN_PURE") == previous


@pytest.mark.parametrize("previous", [None, "0", "1"])
def test_min_numpy_restores_environment_if_import_fails(monkeypatch, previous):
    runner = _runner_module()
    for name in ("rule_search", "dragowing.overlap"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    if previous is None:
        monkeypatch.delenv("NUMPY_MIN_PURE", raising=False)
    else:
        monkeypatch.setenv("NUMPY_MIN_PURE", previous)

    def fail(*args):
        assert os.environ["NUMPY_MIN_PURE"] == "1"
        raise RuntimeError("import failed")

    monkeypatch.setattr(runner, "_load_py", fail)
    with pytest.raises(RuntimeError, match="import failed"):
        runner._preload_numpy_min()
    assert os.environ.get("NUMPY_MIN_PURE") == previous
