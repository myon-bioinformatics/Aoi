"""📐 sakanalytics.py（汎用版・標準ライブラリだけ・この 1 ファイルで動く）のテスト。

旧 test_epsilon.py・test_standalone_boundary.py・test_standalone_examples.py をここにまとめた（節の頭に旧ファイルの名前を書いた）。

- epsilon: ε を記号のまま扱う check_eps / lift（関数として呼ぶ）
- standalone: 1 ファイルだけを一時ディレクトリに写し、python -I で CLI（describe / compare / boundary / scale）を動かす
- uv tool: ルートの pyproject.toml で、この 1 ファイルがそのまま uv tool になる（`uv tool install .`、ビルダーの写しは要らない）
"""
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

import sakanalytics as ep


def load_vendored(name, relpath):
    """Load a vendored file by path under a repo-unique name (cli_args README: Loading a vendored copy)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / relpath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


ROOT = Path(__file__).resolve().parents[1]
_cli_args = load_vendored("sakanalytics_cli_args", "vendor/cli_args.py")


# ==== epsilon（旧 test_epsilon.py）

@pytest.mark.parametrize("bad", [0, 0.0, -1e-9, float("nan"), float("inf"), True, False, "1e-6", [1e-6]])
def test_eps_must_be_none_or_a_positive_finite_number(bad):
    with pytest.raises(ep.EpsilonError, match="greater than 0"):
        ep.check_eps(bad)


def test_eps_is_never_defaulted_and_none_means_off():
    assert ep.check_eps(None) is None
    assert ep.check_eps(1e-6) == 1e-6 and ep.check_eps(2) == 2.0 and isinstance(ep.check_eps(2), float)
    import inspect
    assert inspect.signature(ep.lift).parameters["eps"].default is inspect.Parameter.empty  # the caller always says it


def test_a_value_exactly_on_the_lower_bound_is_lifted_inside_by_eps():
    assert ep.lift(0.0, 1e-6, lo=0.0) == (1e-6, True)
    assert ep.lift(0, 0.25, lo=0) == (0.25, True)
    assert ep.lift(5, 0.5, lo=5) == (5.5, True)


def test_a_value_exactly_on_the_upper_bound_is_lifted_inside_by_eps():
    assert ep.lift(1.0, 1e-6, hi=1.0) == (1.0 - 1e-6, True)
    assert ep.lift(1.0, 0.25, lo=0.0, hi=1.0) == (0.75, True)


def test_without_eps_the_boundary_is_detected_and_the_value_is_untouched():
    assert ep.lift(0.0, None, lo=0.0) == (0.0, True)
    assert ep.lift(1.0, None, hi=1.0) == (1.0, True)


@pytest.mark.parametrize("x", [1e-300, 0.5, 1 - 1e-16, -0.0000001, 2.0])
def test_anything_not_exactly_on_a_bound_passes_through_and_is_not_a_hit(x):
    # exact equality only: a near-zero is the business of the named tolerances, not of ε
    assert ep.lift(x, 1e-6, lo=0.0, hi=1.0) == (x, False)
    assert ep.lift(x, None, lo=0.0, hi=1.0) == (x, False)


def test_negative_zero_is_zero():
    assert ep.lift(-0.0, 1e-3, lo=0.0) == (1e-3, True)


def test_a_bound_is_required_and_eps_must_fit_inside_two_bounds():
    with pytest.raises(ep.EpsilonError, match="needs a bound"):
        ep.lift(0.0, 1e-6)
    with pytest.raises(ep.EpsilonError, match="does not fit"):
        ep.lift(0.0, 0.5, lo=0.0, hi=1.0)
    with pytest.raises(ep.EpsilonError, match="greater than 0"):
        ep.lift(0.0, 0, lo=0.0)
    assert ep.lift(0.0, 0.49, lo=0.0, hi=1.0) == (0.49, True)


def test_the_lifted_value_is_strictly_inside_and_moves_with_eps():
    for eps in (1e-3, 1e-6, 1e-9):
        v, hit = ep.lift(0.0, eps, lo=0.0, hi=1.0)
        assert hit and 0 < v < 1 and math.isclose(v, eps)


# ==== standalone（旧 test_standalone_examples.py と test_standalone_boundary.py の StandaloneBoundaryTest）

class StandaloneExamples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        target = Path(self.temp.name) / "tool"
        target.mkdir()
        shutil.copy2(ROOT / "sakanalytics.py", target / "sakanalytics.py")  # 汎用版はこの 1 ファイルだけで動く
        self.script = target / "sakanalytics.py"

    def run_cli(self, *args):
        return _cli_args.run_cli(self.script, *args, python_options=("-I",), cwd=self.temp.name)

    def call(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.json()

    def test_examples(self):

        data = self.call("describe", "45", "52", "48", "61", "50")
        self.assertEqual((data["count"], data["mean"], data["median"]), (5, 51.2, 50))
        self.assertIsNone(self.call("compare", "--before", "0", "--after", "1")["mean_relative_change"])
        self.assertEqual(self.run_cli("describe", "nan").returncode, 2)

    def test_comma_and_whitespace_input(self):
        self.assertEqual(self.call("describe", "10,20,30")["mean"], 20)
        self.assertEqual(self.call("describe", "10,", "20,", "30")["mean"], 20)
        self.assertEqual(self.call("compare", "--before", "1,2", "--after", "3,4")["mean_difference"], 2)

    def test_stdin_and_files(self):
        result = _cli_args.run_cli(self.script, "describe", "-", python_options=("-I",), stdin="1,2,3\n4,5,6\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mean"], 3.5)
        path = Path(self.temp.name) / "data.csv"
        path.write_text("label,value\na,10\nb,20\n", encoding="utf-8")
        self.assertEqual(self.call("describe", "--file", str(path), "--column", "value")["mean"], 15)
        self.assertIn("column not found", self.run_cli("describe", "--file", str(path), "--column", "missing").stderr)
        path.write_text("label,value\na,10\nb,\n", encoding="utf-8")
        self.assertIn("missing value", self.run_cli("describe", "--file", str(path), "--column", "value").stderr)

    def test_csv_pipe_matches_file_bytes(self):
        args = [sys.executable, "-I", str(self.script), "describe", "--file", "-", "--column", "値"]
        path = Path(self.temp.name) / "input.csv"
        data = '\ufeff"値",label\r\n10,"one\r\ntwo"\r\n20,three\r\n'.encode()
        path.write_bytes(data)
        result = subprocess.run(args, input=data, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), self.call("describe", "--file", str(path), "--column", "値"))
        bad = subprocess.run(args, input="値,値\n1,2".encode(), capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertIn(b"duplicate", bad.stderr)
        plain = subprocess.run(args[:-2], input=b"1,2,3", capture_output=True, check=True)
        self.assertEqual(json.loads(plain.stdout)["mean"], 2)

    def test_invalid_numbers_are_not_silently_skipped(self):
        for value in ("1,,2", "1,bad,3", "1,nan", "1,inf"):
            self.assertEqual(self.run_cli("describe", value).returncode, 2)
        self.assertEqual(self.run_cli("describe", "--column", "value").returncode, 2)

    def test_negative_comma_values_and_exponents(self):
        self.assertEqual(self.call("describe", "-1,-2")["mean"], -1.5)
        self.assertEqual(self.call("describe", "-1,", "-2")["mean"], -1.5)
        self.assertEqual(self.call("describe", "-1e3", "2e3")["mean"], 500)
        self.assertEqual(self.call("compare", "--before", "-1,-2", "--after", "3,4")["mean_difference"], 5)
        self.assertEqual(self.call("boundary", "-1e3", "--lo", "-1e3")["value"], -1000)
        self.assertEqual(self.run_cli("describe", "--unknown").returncode, 2)
        self.assertEqual(self.run_cli("describe", "-x").returncode, 2)

    def test_csv_column_selection_and_invalid_structure(self):
        path = Path(self.temp.name) / "data.csv"
        path.write_text("label,value,unused\na,1,ignored\nb,2,also ignored\n", encoding="utf-8")
        self.assertEqual(self.call("describe", "--file", str(path), "--column", "value")["mean"], 1.5)
        for content, error in (
            ("value,value\n1,2\n", "duplicate"),
            ("label,value\na\n", "missing"),
            ("label,value\na,nan\n", "non-finite"),
        ):
            path.write_text(content, encoding="utf-8")
            result = self.run_cli("describe", "--file", str(path), "--column", "value")
            self.assertEqual(result.returncode, 2)
            self.assertIn(error, result.stderr)
        self.assertEqual(self.run_cli("describe", "1e308", "1e308").returncode, 2)

    def test_detect_and_optionally_lift(self):
        same = self.run_cli("0", "--lo", "0")
        self.assertEqual(same.returncode, 0, same.stderr)
        self.assertEqual(json.loads(same.stdout), {"original": 0, "value": 0, "boundary": True})
        lifted = self.run_cli("0", "--lo", "0", "--eps", "0.1")
        self.assertEqual(json.loads(lifted.stdout)["value"], 0.1)
        self.assertEqual(self.run_cli("nan", "--lo", "0").returncode, 2)
        self.assertEqual(self.run_cli("1", "--lo", "2", "--hi", "1").returncode, 2)

    def test_scale_log_and_linear_on_the_copied_file(self):
        data = self.call("scale", "26235991", "500501", "--anchor", "26235991")
        self.assertEqual(data, {"mode": "log", "scores": [90, 70]})
        data = self.call("scale", "--linear", "--factor", ".97", "3", "4")
        self.assertEqual(data, {"mode": "linear", "scores": [.97 * 3, .97 * 4]})
        bad = self.run_cli("scale", "-1", "2")
        self.assertEqual(bad.returncode, 2)
        self.assertIn("nonnegative", bad.stderr)


# ==== uv tool（旧 test_standalone_boundary.py の SharedUvToolBuildTest。PythDRagoras #54 に倣い、ルートの pyproject がそのまま uv tool）

class SharedUvToolBuildTest(unittest.TestCase):
    def test_the_generic_file_is_the_uv_tool(self):
        import tomllib
        config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project = config["project"]
        self.assertEqual((project["dependencies"], project["scripts"]), ([], {"sakanalytics": "sakanalytics:main"}))
        self.assertEqual(project["requires-python"], ">=3.11")
        self.assertEqual(config["tool"]["setuptools"]["py-modules"], ["sakanalytics"])   # 入るのはこの 1 ファイルだけ
        self.assertFalse((ROOT / "vendor" / "uv_tool_build.py").exists())


def test_sakanalytics_imports_only_the_standard_library():
    import ast
    tree = ast.parse((ROOT / "sakanalytics.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    assert "polars" not in names and "npb" not in names
    assert names <= set(sys.stdlib_module_names)

