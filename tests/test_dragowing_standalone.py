import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StandaloneTest(unittest.TestCase):
    def test_file_and_stdin_without_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "dragowing.py"
            shutil.copy2(ROOT / "dragowing.py", script)
            result = subprocess.run([sys.executable, "-I", str(script), "--tag", "p"],
                                    input="<p>one</p><p>two</p><div></div>", text=True,
                                    capture_output=True, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"p": 2})
            missing = subprocess.run([sys.executable, "-I", str(script), "missing.html"],
                                     capture_output=True, text=True, cwd=tmp)
            self.assertEqual(missing.returncode, 1)
            self.assertIn("Cannot read HTML", missing.stderr)

    def test_generated_tool_project_has_single_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tool"
            subprocess.run([sys.executable, str(ROOT / "build_stdlib_tool.py"), str(target)], check=True)
            self.assertEqual((target / "dragowing.py").read_bytes(), (ROOT / "dragowing.py").read_bytes())
            self.assertIn('dragowing-html = "dragowing:main"', (target / "pyproject.toml").read_text())
