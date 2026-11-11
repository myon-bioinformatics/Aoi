import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class StandaloneExamples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        target = Path(self.temp.name) / "tool"
        subprocess.run([sys.executable, str(ROOT / "build_stdlib_tool.py"), str(target)], check=True)
        self.script = target / "sakanalytics.py"

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(self.script), *args], cwd=self.temp.name, text=True, capture_output=True)

    def call(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

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
        result = subprocess.run([sys.executable, "-I", str(self.script), "describe", "-"], input="1,2,3\n4,5,6\n", text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mean"], 3.5)
        path = Path(self.temp.name) / "data.csv"
        path.write_text("label,value\na,10\nb,20\n", encoding="utf-8")
        self.assertEqual(self.call("describe", "--file", str(path), "--column", "value")["mean"], 15)
        self.assertIn("column not found", self.run_cli("describe", "--file", str(path), "--column", "missing").stderr)
        path.write_text("label,value\na,10\nb,\n", encoding="utf-8")
        self.assertIn("missing value", self.run_cli("describe", "--file", str(path), "--column", "value").stderr)

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
