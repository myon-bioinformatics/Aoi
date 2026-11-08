import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).parent
WORKFLOW = (ROOT / '.github/workflows/cache-keepalive.yml').read_text()
SCRIPT = WORKFLOW.split('        run: |\n', 1)[1]
SCRIPT = '\n'.join(line[10:] for line in SCRIPT.splitlines())

class KeepaliveTests(unittest.TestCase):
    def run_report(self, key, manifests):
        with tempfile.TemporaryDirectory() as directory:
            for name, value in manifests.items():
                path = Path(directory) / 'data/raw' / name / 'manifest.jsonl'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
            return subprocess.run(['bash', '-e', '-c', SCRIPT], cwd=directory,
                env={**os.environ, 'MATCHED_KEY': key}, capture_output=True, text=True)

    def test_miss_fails_explicitly(self):
        result = self.run_report('', {})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('cache not found; no refetch performed', result.stdout)

    def test_hit_without_manifests_fails(self):
        self.assertNotEqual(self.run_report('aoi-data-c001-1', {}).returncode, 0)

    def test_empty_manifest_fails(self):
        self.assertNotEqual(self.run_report('aoi-data-c001-1', {'empty': ''}).returncode, 0)

    def test_valid_manifest_and_trailing_empty_succeed(self):
        result = self.run_report('aoi-data-c001-1', {'a': '{}\n', 'z': ''})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('1 entries', result.stdout)

    def test_key_is_data_not_shell_code(self):
        result = self.run_report('$(exit 77)', {'a': '{}\n'})
        self.assertEqual(result.returncode, 0)
        self.assertIn('$(exit 77)', result.stdout)

if __name__ == '__main__':
    unittest.main()
