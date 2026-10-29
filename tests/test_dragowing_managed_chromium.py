"""Managed dependency tests use synthetic ZIPs; no network or browser launches."""
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import warnings

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('install_ci_chromium', ROOT / 'scripts/install_ci_chromium.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def archive_bytes(extra=(), executable=True):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as archive:
        item = zipfile.ZipInfo('chrome-linux/chrome')
        item.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
        archive.writestr(item, b'synthetic executable, never run')
        for name, mode, content in extra:
            item = zipfile.ZipInfo(name)
            item.external_attr = mode << 16
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                archive.writestr(item, content)
    return out.getvalue()


class ManagedChromiumTests(unittest.TestCase):
    def test_success_installs_once_without_executing(self):
        data = archive_bytes([('chrome-linux/resources.pak', stat.S_IFREG | 0o6755, b'data')])
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(installer, 'ARCHIVE_BYTES', len(data)), \
             patch.object(installer, 'SHA256', hashlib.sha256(data).hexdigest()), \
             patch.object(installer.urllib.request, 'urlopen', return_value=io.BytesIO(data)) as fetch:
            target = Path(tmp) / 'browser'
            executable = installer.install(target)
            self.assertEqual(executable.read_bytes(), b'synthetic executable, never run')
            self.assertEqual(executable.stat().st_mode & 0o7777, 0o755)
            self.assertEqual((target / 'chrome-linux/resources.pak').stat().st_mode & 0o7777, 0o755)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ['browser'])
            fetch.assert_called_once_with(installer.URL, timeout=30)

    def test_wrong_size_or_hash_never_publishes(self):
        data = archive_bytes()
        for size, digest in ((len(data)-1, hashlib.sha256(data).hexdigest()),
                             (len(data)+1, hashlib.sha256(data).hexdigest()),
                             (len(data), '0'*64)):
            with self.subTest(size=size, digest=digest), tempfile.TemporaryDirectory() as tmp, \
                 patch.object(installer, 'ARCHIVE_BYTES', size), \
                 patch.object(installer, 'SHA256', digest), \
                 patch.object(installer.urllib.request, 'urlopen', return_value=io.BytesIO(data)) as fetch:
                with self.assertRaises(ValueError):
                    installer.install(Path(tmp) / 'browser')
                self.assertEqual(list(Path(tmp).iterdir()), [])
                fetch.assert_called_once()

    def test_network_failure_has_no_retry_or_fallback(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(installer.urllib.request, 'urlopen', side_effect=TimeoutError) as fetch:
            with self.assertRaises(TimeoutError):
                installer.install(Path(tmp) / 'browser')
            self.assertEqual(list(Path(tmp).iterdir()), [])
            fetch.assert_called_once()

    def test_transfer_deadline_does_not_retry(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(installer.time, 'monotonic', side_effect=[0, 301]), \
             patch.object(installer.urllib.request, 'urlopen', return_value=io.BytesIO(b'')) as fetch:
            with self.assertRaises(TimeoutError):
                installer.install(Path(tmp) / 'browser')
            self.assertEqual(list(Path(tmp).iterdir()), [])
            fetch.assert_called_once()

    def test_invalid_zip_does_not_publish_installation(self):
        data = b'not a ZIP'
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(installer, 'ARCHIVE_BYTES', len(data)), \
             patch.object(installer, 'SHA256', hashlib.sha256(data).hexdigest()), \
             patch.object(installer.urllib.request, 'urlopen', return_value=io.BytesIO(data)):
            with self.assertRaises(zipfile.BadZipFile):
                installer.install(Path(tmp) / 'browser')
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_existing_destination_or_symlink_never_fetches(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(installer, 'download') as fetch:
            directory = Path(tmp) / 'browser'
            directory.mkdir()
            link = Path(tmp) / 'link'
            link.symlink_to(Path(tmp) / 'absent')
            for target in (directory, link):
                with self.assertRaises(ValueError):
                    installer.install(target)
            fetch.assert_not_called()

    def test_unsafe_members_rejected_before_extraction(self):
        bad = [('../escape', stat.S_IFREG | 0o644),
               ('/absolute', stat.S_IFREG | 0o644),
               ('chrome-linux/../escape', stat.S_IFREG | 0o644),
               ('chrome-linux//double', stat.S_IFREG | 0o644),
               ('chrome-linux/./dot', stat.S_IFREG | 0o644),
               ('chrome-linux\\escape', stat.S_IFREG | 0o644),
               ('other-root/file', stat.S_IFREG | 0o644),
               ('chrome-linux/link', stat.S_IFLNK | 0o777),
               ('chrome-linux/fifo', stat.S_IFIFO | 0o644),
               ('chrome-linux/chrome/child', stat.S_IFREG | 0o644),
               ('chrome-linux/chrome/', stat.S_IFDIR | 0o755),
               ('chrome-linux/not-dir', stat.S_IFDIR | 0o755)]
        for name, mode in bad:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                archive = Path(tmp) / 'input.zip'
                archive.write_bytes(archive_bytes([(name, mode, b'bad')]))
                target = Path(tmp) / 'output'
                target.mkdir()
                with self.assertRaises(ValueError):
                    installer.extract(archive, target)
                self.assertEqual(list(target.iterdir()), [])

    def test_limits_missing_executable_and_duplicates(self):
        for content in (archive_bytes(), archive_bytes([('chrome-linux/chrome', stat.S_IFREG | 0o755, b'duplicate')])):
            with zipfile.ZipFile(io.BytesIO(content)) as archive, patch.object(installer, 'MAX_EXPANDED_BYTES', 1):
                with self.assertRaises(ValueError):
                    installer.validate_members(archive)
        with zipfile.ZipFile(io.BytesIO(archive_bytes())) as archive, patch.object(installer, 'MAX_MEMBERS', 0):
            with self.assertRaises(ValueError):
                installer.validate_members(archive)
        empty = io.BytesIO()
        with zipfile.ZipFile(empty, 'w') as archive:
            archive.writestr('chrome-linux/not-browser', b'data')
        with zipfile.ZipFile(empty) as archive:
            with self.assertRaisesRegex(ValueError, 'lacks'):
                installer.validate_members(archive)
        duplicate = archive_bytes([('chrome-linux/chrome', stat.S_IFREG | 0o755, b'duplicate')])
        with zipfile.ZipFile(io.BytesIO(duplicate)) as archive:
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                installer.validate_members(archive)

    def test_executable_permission_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'input.zip'
            archive.write_bytes(archive_bytes(executable=False))
            with self.assertRaisesRegex(ValueError, 'not executable'):
                installer.extract(archive, Path(tmp) / 'output')

    def test_ci_version_gate_and_no_fallback(self):
        text = (ROOT / '.github/workflows/ci.yml').read_text()
        marker = '      - name: Select and verify the installed Chromium without fallback\n'
        block = text.split(marker, 1)[1].split('\n      - name:', 1)[0]
        script = '\n'.join(line.removeprefix('          ') for line in block.split('        run: |\n',1)[1].splitlines())
        for version, expected in [('Chromium 156.0.8078.0', 0), ('Chromium 156.0.8078.0 ', 0),
                                  ('Chromium 156.0.8078.01', 1), ('Google Chrome 156.0.8078.0', 1)]:
            with self.subTest(version=version), tempfile.TemporaryDirectory() as tmp:
                binary = Path(tmp) / 'dragowing-chromium/chrome-linux/chrome'
                binary.parent.mkdir(parents=True)
                binary.write_text('#!/bin/sh\n[ "$1" = --version ] || exit 99\nprintf "%s\\n" "'+version+'"\n')
                binary.chmod(0o755)
                env = Path(tmp) / 'env'
                result = subprocess.run(['bash', '-c', script], env={**os.environ,'RUNNER_TEMP':tmp,'GITHUB_ENV':str(env)},capture_output=True)
                self.assertEqual(result.returncode, expected)
                self.assertEqual(env.exists(), expected == 0)
        self.assertNotIn('command -v chromium', block)
        self.assertIn('DRAGOWING_REQUIRE_CHROME=1', block)
        self.assertIn('runs-on: ubuntu-24.04', text)
        self.assertIn('python: ["3.11", "3.12", "3.13", "3.14", "3.15"]', text)


if __name__ == '__main__':
    unittest.main()
