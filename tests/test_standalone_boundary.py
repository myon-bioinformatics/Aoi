import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StandaloneBoundaryTest(unittest.TestCase):
    def test_detect_and_optionally_lift(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "tool"
            subprocess.run([sys.executable, str(ROOT / "scripts/build_stdlib_tool.py"), str(target)], check=True)
            script = target / "sakanalytics.py"
            def run(*args):
                return subprocess.run([sys.executable, "-I", str(script), *args], capture_output=True, text=True, cwd=temp)
            same = run("0", "--lo", "0")
            self.assertEqual(same.returncode, 0, same.stderr)
            self.assertEqual(json.loads(same.stdout), {"original": 0, "value": 0, "boundary": True})
            lifted = run("0", "--lo", "0", "--eps", "0.1")
            self.assertEqual(json.loads(lifted.stdout)["value"], 0.1)
            self.assertEqual(run("nan", "--lo", "0").returncode, 2)
            self.assertEqual(run("1", "--lo", "2", "--hi", "1").returncode, 2)
