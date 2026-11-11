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
