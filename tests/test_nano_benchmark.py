"""Independent arithmetic oracle plus protocol and measurement checks."""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location('nano_' + name, ROOT / 'scripts/nano' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MeasurementTests(unittest.TestCase):
    def test_disk_bytes_exclude_base_interpreter_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'file').write_bytes(b'abc')
            (path / 'link').symlink_to(path / 'file')
            self.assertEqual(load('benchmark').directory_bytes(path), 3)

    def test_rss_is_actual_resident_memory(self):
        import os
        self.assertGreater(load('benchmark').resident('self'), 0)


class ResearchOracleTests(unittest.TestCase):
    def test_real_polars_agrees_with_independent_scalar_math(self):
        worker = load('workload')
        rows = worker.evaluate('valid')['output']
        self.assertEqual(len(rows), 4)
        for row in rows:
            if row['team'] == 'A':
                probabilities = [.55, .5] if row['model'] == 'fixed' else [.6, .52]
                wins = [70, 60]
            else:
                probabilities = [.45] if row['model'] == 'fixed' else [.4]
                wins = [40]
            excess = sum(w - 120*p for w, p in zip(wins, probabilities))
            variance = sum(120*p*(1-p) for p in probabilities)
            z = excess / math.sqrt(variance)
            self.assertAlmostEqual(row['excess_wins'], excess)
            self.assertAlmostEqual(row['z'], z)
            self.assertAlmostEqual(row['p_two_sided'], math.erfc(abs(z)/math.sqrt(2)))

    def test_invalid_inputs_produce_errors_and_empty_is_valid(self):
        worker = load('workload')
        for case in ('missing-column', 'bad-type'):
            self.assertIsNone(worker.evaluate(case)['output'])
            self.assertTrue(worker.evaluate(case)['error']['message'])
        self.assertEqual(worker.evaluate('empty'), {'output': [], 'error': None})


if __name__ == '__main__':
    unittest.main()
