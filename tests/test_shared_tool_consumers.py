"""Independent synthetic cases: no child imports, network or Git needed."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_shared_tool_consumers as checker


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = 'myon-bioinformatics/Example'
        self.source = 'scripts/tool.py'
        self.dest = 'vendor/aoi/scripts/tool.py'
        self.write(self.source, b'new version\n')
        self.write('child/' + self.dest, b'old pinned version\n')
        self.shared = {'schema': 'vendor-lock/1', 'files': [dict(path=self.source,
            sha256=self.digest(b'new version\n'), source=checker.SOURCE, consumers=[self.repo])]}
        self.child = {'schema': 'vendor-lock/1', 'files': [dict(path=self.dest,
            sha256=self.digest(b'old pinned version\n'), source=checker.SOURCE)]}
        self.save('shared-tools.lock.json', self.shared)
        self.save('child/shared-tools.lock.json', self.child)
        self.save('child-heads.json', {'heads': {self.repo: {'optional': {'subtree_prefix': 'child'}}}})

    def digest(self, raw):
        return hashlib.sha256(raw).hexdigest()

    def write(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def save(self, path, value):
        self.write(path, json.dumps(value).encode())

    def test_old_pin_is_valid(self):
        self.assertEqual(checker.problems(self.root), [])

    def test_corrupt_copy(self):
        self.write('child/' + self.dest, b'corrupt')
        self.assertTrue(any('sha256 mismatch' in x for x in checker.problems(self.root)))

    def test_missing_copy(self):
        (self.root / 'child' / self.dest).unlink()
        self.assertTrue(any('missing child copy' in x for x in checker.problems(self.root)))

    def test_missing_consumer(self):
        self.shared['files'][0]['consumers'] = []
        self.save('shared-tools.lock.json', self.shared)
        self.assertTrue(any('missing consumer' in x for x in checker.problems(self.root)))

    def test_unlocked_copy(self):
        (self.root / 'child/shared-tools.lock.json').unlink()
        errors = checker.problems(self.root)
        self.assertTrue(any('copy missing from' in x for x in errors))
        self.assertTrue(any('consumer without locked copy' in x for x in errors))

    def test_commit_lock_variant(self):
        (self.root / 'child/shared-tools.lock.json').unlink()
        self.save('child/vendor.lock.json', {'schema': 'vendor-lock/1', 'files': [dict(
            repository=checker.SOURCE, source=self.source, destination=self.dest,
            sha256=self.digest(b'old pinned version\n'), commit='a' * 40)]})
        self.assertEqual(checker.problems(self.root), [])

    def test_extra_copy(self):
        self.write('child/vendor/aoi/untracked.py', b'extra')
        self.assertTrue(any('copy missing from' in x for x in checker.problems(self.root)))

    def test_invalid_child_json(self):
        self.write('child/shared-tools.lock.json', b'{')
        self.assertTrue(any('child/shared-tools.lock.json' in x for x in checker.problems(self.root)))

    def test_path_escape(self):
        self.child['files'][0]['path'] = 'vendor/aoi/../../../escape'
        self.save('child/shared-tools.lock.json', self.child)
        self.assertTrue(any('unsafe source/destination' in x for x in checker.problems(self.root)))

    def test_cli_strict_and_warn(self):
        self.write('child/' + self.dest, b'corrupt')
        self.assertEqual(checker.main(['--root', str(self.root)]), 1)
        self.assertEqual(checker.main(['--root', str(self.root), '--warn']), 0)

    def test_license_registered_under_vendor_aoi_is_not_a_tool(self):
        self.write('child/vendor/aoi/LICENSE', b'license')
        self.save('child/vendor.lock.json', {'schema': 'vendor-lock/1', 'files': [dict(
            repository=checker.SOURCE, source='LICENSE', destination='vendor/aoi/LICENSE',
            sha256=self.digest(b'license'), commit='a' * 40)]})
        self.assertEqual(checker.problems(self.root), [])
        self.write('child/vendor/aoi/LICENSE', b'corrupt')
        self.assertTrue(any('sha256 mismatch' in x for x in checker.problems(self.root)))

    def test_child_lock_symlink_outside_child_is_rejected(self):
        self.save('outside.json', self.child)
        path = self.root / 'child/shared-tools.lock.json'
        path.unlink()
        path.symlink_to('../outside.json')
        self.assertTrue(any('lock resolves outside child' in x for x in checker.problems(self.root)))
        self.assertEqual(checker.main(['--root', str(self.root)]), 1)
        self.assertEqual(checker.main(['--root', str(self.root), '--warn']), 0)

    def test_null_child_head_is_diagnostic(self):
        self.save('child-heads.json', {'heads': {self.repo: None}})
        self.assertTrue(any('child-heads.json' in x for x in checker.problems(self.root)))
        self.assertEqual(checker.main(['--root', str(self.root)]), 1)
        self.assertEqual(checker.main(['--root', str(self.root), '--warn']), 0)

    def test_null_heads_is_diagnostic(self):
        self.save('child-heads.json', {'heads': None})
        self.assertTrue(checker.problems(self.root))
        self.assertEqual(checker.main(['--root', str(self.root), '--warn']), 0)

    def test_null_optional_is_diagnostic(self):
        self.save('child-heads.json', {'heads': {self.repo: {'optional': None}}})
        self.assertTrue(checker.problems(self.root))
        self.assertEqual(checker.main(['--root', str(self.root), '--warn']), 0)

    def test_unused_tool(self):
        self.shared['files'].append(dict(path='scripts/unused.py', sha256=self.digest(b'unused'), source=checker.SOURCE, consumers=[]))
        self.write('scripts/unused.py', b'unused')
        self.save('shared-tools.lock.json', self.shared)
        self.assertEqual(checker.problems(self.root), [])


if __name__ == '__main__':
    unittest.main()
