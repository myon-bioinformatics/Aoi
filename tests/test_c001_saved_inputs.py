import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import check_c001_saved_inputs as saved


class SavedInputTests(unittest.TestCase):
    def test_saved_inputs_replay_without_network(self):
        with patch('socket.socket', side_effect=AssertionError('network forbidden')):
            result = saved.check()
        self.assertEqual(result['annual_units'], 168)
        self.assertEqual(result['annual_values_matched'], 72)
        self.assertFalse(result['raw_source_replayed'])

    def test_missing_input_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                saved.verify_payload(Path(directory) / 'missing', {})

    def test_corrupt_input_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'saved.json'
            path.write_bytes(b'{}')
            expected = {'bytes': 2, 'sha256': hashlib.sha256(b'[]').hexdigest()}
            with self.assertRaises(ValueError):
                saved.verify_payload(path, expected)

    def test_stale_outputs_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'output'
            path.write_text('stale')
            with patch.object(saved.season, 'outputs', return_value={path: 'expected'}):
                with self.assertRaisesRegex(ValueError, 'Stale'):
                    saved.check()


if __name__ == '__main__':
    unittest.main()
