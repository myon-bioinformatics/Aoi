"""Named entry files dispatch to Aoi children without requiring external libraries."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = {
    "BlueProbe": ("blueprobe", "blueprobe.py"),
    "QueRyu": ("queryu", "queryu.py"),
    "NagoyAction": ("nagoyaction", "nagoyaction.py"),
    "SakAnalytics": ("sakanalytics", "sakanalytics.py"),
    "PythDRagoras": ("pythdragoras", "pythdragoras.py"),
    "DRAgoWing": ("dragowing", "__main__.py"),
}


class NamedChildEntriesTest(unittest.TestCase):
    def test_forwards_argv_cwd_and_exit_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "aoi"
            root.mkdir()
            work = Path(temp) / "work"
            work.mkdir()
            for name, (directory, filename) in ENTRIES.items():
                with self.subTest(entry=name):
                    shutil.copy2(ROOT / (name + ".py"), root / (name + ".py"))
                    target = root / directory / filename
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text('import json, os, sys\nprint(json.dumps({"args": sys.argv[1:], "cwd": os.getcwd()}))\nsys.exit(7)\n')
                    env = dict(os.environ, PYTHONPATH="")
                    result = subprocess.run([sys.executable, str(root / (name + ".py")), "x y", "--option"],
                                            cwd=work, env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 7, result.stderr)
                    self.assertEqual(json.loads(result.stdout), {"args": ["x y", "--option"], "cwd": str(work)})

    def test_missing_child_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as temp:
            entry = Path(temp) / "BlueProbe.py"
            shutil.copy2(ROOT / "BlueProbe.py", entry)
            result = subprocess.run([sys.executable, str(entry), "--help"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("complete Aoi checkout", result.stderr)
