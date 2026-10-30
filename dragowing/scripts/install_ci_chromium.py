"""Install a reviewed Chromium snapshot for CI; never execute the browser.

Standard-library setup only. No runtime dependency, fallback, retry, prefetch,
privilege changes or existing-install refresh. See docs/export.md for provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
import time
import urllib.request
import zipfile

REVISION = '1706520'
VERSION = '156.0.8078.0'
GENERATION = '1790642197733749'
SHA256 = '6b62846a868ea3ee675f77600790877a428dfb2428c940f8eff99db1038f9815'
ARCHIVE_BYTES = 248486630
URL = ('https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/'
       f'Linux_x64%2F{REVISION}%2Fchrome-linux.zip?generation={GENERATION}&alt=media')
MAX_MEMBERS = 10000
MAX_EXPANDED_BYTES = 1024 * 1024 * 1024


def download(archive: Path) -> None:
    digest = hashlib.sha256()
    count = 0
    deadline = time.monotonic() + 300
    # One download; per-read network timeout plus a bounded transfer deadline.
    with urllib.request.urlopen(URL, timeout=30) as response, archive.open('xb') as out:
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError('Chromium download exceeded its transfer budget')
            block = response.read(1024 * 1024)
            if not block:
                break
            count += len(block)
            if count > ARCHIVE_BYTES:
                raise ValueError('Chromium archive exceeds its pinned size')
            digest.update(block)
            out.write(block)
    if count != ARCHIVE_BYTES or digest.hexdigest() != SHA256:
        raise ValueError('Chromium archive size or SHA256 mismatch')


def validate_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    members = archive.infolist()
    if not members or len(members) > MAX_MEMBERS:
        raise ValueError('Invalid Chromium archive member count')
    names = set()
    total = 0
    for item in members:
        name = item.filename
        parts = name.rstrip('/').split('/')
        mode = stat.S_IFMT(item.external_attr >> 16)
        if (item.orig_filename != name or '\\' in name or '\0' in name or name.startswith('/')
                or any(part in ('', '.', '..') for part in parts)
                or parts[0] != 'chrome-linux' or name in names
                or item.flag_bits & 1
                or mode not in (0, stat.S_IFREG, stat.S_IFDIR)
                or (mode == stat.S_IFDIR and not item.is_dir())
                or (item.is_dir() and mode == stat.S_IFREG)):
            raise ValueError('Unsafe Chromium archive member')
        names.add(name)
        total += item.file_size
        if item.file_size < 0 or total > MAX_EXPANDED_BYTES:
            raise ValueError('Chromium archive expanded size exceeds limit')
    if 'chrome-linux/chrome' not in names:
        raise ValueError('Chromium archive lacks its executable')
    # Reject file/directory aliases and a file used as an ancestor before writing.
    files = {item.filename for item in members if not item.is_dir()}
    for item in members:
        path = PurePosixPath(item.filename.rstrip('/'))
        if item.is_dir() and str(path) in files:
            raise ValueError('Chromium archive file/directory collision')
        if any(str(parent) in files for parent in path.parents):
            raise ValueError('Chromium archive file used as directory')
    return members


def extract(archive_path: Path, target: Path) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        members = validate_members(archive)
        for item in members:
            path = target.joinpath(*PurePosixPath(item.filename).parts)
            if item.is_dir():
                path.mkdir(parents=True, exist_ok=True)
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            written = 0
            with archive.open(item) as source, path.open('xb') as out:
                while block := source.read(1024 * 1024):
                    written += len(block)
                    if written > item.file_size:
                        raise ValueError('Chromium member exceeds declared size')
                    out.write(block)
            if written != item.file_size:
                raise ValueError('Truncated Chromium archive member')
            # Only normal executable bits survive; never setuid/setgid/sticky.
            path.chmod(0o755 if (item.external_attr >> 16) & 0o111 else 0o644)
    executable = target / 'chrome-linux/chrome'
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError('Chromium executable is missing or not executable')


def install(destination: Path) -> Path:
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError('Destination already exists; refusing to refresh an installation')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.chromium-install-', dir=destination.parent) as work:
        work = Path(work)
        archive = work / 'chromium.zip'
        target = work / 'installed'
        target.mkdir()
        download(archive)
        extract(archive, target)
        if destination.exists() or destination.is_symlink():
            raise ValueError('Destination appeared during installation')
        target.rename(destination)
    return destination / 'chrome-linux/chrome'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    executable = install(args.destination)
    print(json.dumps({'revision': REVISION, 'expected_version': VERSION,
                      'archive_sha256': SHA256, 'generation': GENERATION,
                      'executable': str(executable)}, sort_keys=True))


if __name__ == '__main__':
    main()
