"""代替の入口は、markdown と numpy が入った環境では動かない。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stdlib_paths.py"


def test_min_refuses_while_markdown_and_numpy_are_installed(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--deps", "min", str(tmp_path / "out.json")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "markdown" in proc.stderr
    assert "numpy" in proc.stderr
    assert not (tmp_path / "out.json").exists()


import ctypes
import ctypes.util
import importlib.util
import os
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
