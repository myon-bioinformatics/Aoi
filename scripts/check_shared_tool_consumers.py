#!/usr/bin/env python3
"""Offline consumer inventory and integrity check, respecting each child's lock.

A child's recorded hash can legitimately differ from Aoi's current source.
This checks bytes against the child's own lock, not against today's Aoi.
Commit provenance and subtree equality remain separate checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from check_shared_tools_lock import SOURCE, HEX64, problems as source_problems

ROOT = Path(__file__).resolve().parents[1]


def relative(value):
    return (isinstance(value, str) and bool(value) and not value.startswith('/')
            and all(p not in ('', '.', '..') for p in value.split('/')))


def inside(root, value):
    return relative(value) and (root / value).resolve().is_relative_to(root.resolve())


def has_symlink(root, value):
    path = root
    for part in value.split('/'):
        path = path / part
        if path.is_symlink():
            return True
    return False


def problems(root: Path) -> list[str]:
    # Invalid local metadata must remain an ordinary diagnostic, including --warn.
    try:
        return _problems(root)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
        return [f'invalid shared-tool metadata: {exc}']


def _problems(root: Path) -> list[str]:
    heads = json.loads((root / 'child-heads.json').read_text())['heads']
    if not isinstance(heads, dict):
        return ['child-heads.json: heads must be an object']
    for repo, head in heads.items():
        if not isinstance(head, dict) or not isinstance(head.get('optional'), dict):
            return [f'child-heads.json: {repo}: expected head and optional objects']
    found = source_problems(root)
    if found:
        return found
    shared = {e['path']: e for e in json.loads((root / 'shared-tools.lock.json').read_text())['files']}
    heads = json.loads((root / 'child-heads.json').read_text())['heads']
    actual = {path: set() for path in shared}
    for repo, head in heads.items():
        prefix = head.get('optional', {}).get('subtree_prefix')
        if not inside(root, prefix) or has_symlink(root, prefix):
            found.append(f'{repo}: invalid subtree_prefix')
            continue
        child = root / prefix
        registered = set()
        for filename in ('vendor.lock.json', 'shared-tools.lock.json'):
            lockfile = child / filename
            if not lockfile.exists() and not lockfile.is_symlink():
                continue
            if not inside(child, filename) or has_symlink(child, filename):
                found.append(f'{prefix}/{filename}: lock resolves outside child or is a symlink')
                continue
            try:
                document = json.loads(lockfile.read_text())
                if not isinstance(document, dict) or document.get('schema') != 'vendor-lock/1' or not isinstance(document.get('files'), list):
                    raise ValueError('expected vendor-lock/1 files')
                for entry in document['files']:
                    if not isinstance(entry, dict):
                        raise ValueError('entry must be an object')
                    if filename == 'vendor.lock.json':
                        if entry.get('repository') != SOURCE:
                            continue
                        source, destination = entry.get('source'), entry.get('destination')
                    else:
                        if entry.get('source') != SOURCE:
                            continue
                        destination = entry.get('path')
                        if not isinstance(destination, str) or not destination.startswith('vendor/aoi/'):
                            raise ValueError('shared destination must be under vendor/aoi/')
                        source = destination[len('vendor/aoi/'):]
                    if not relative(source) or not inside(child, destination):
                        raise ValueError('unsafe source/destination')
                    # A provenance lock can also register LICENSE or other assets.
                    # Account for them in the directory inventory, without inventing
                    # a shared-tool consumer declaration for a non-tool source.
                    if source in shared:
                        actual[source].add(repo)
                    elif filename == 'shared-tools.lock.json':
                        found.append(f'{prefix}/{destination}: source absent from shared tools: {source}')
                    if destination in registered:
                        found.append(f'{prefix}/{destination}: duplicate child lock destination')
                    registered.add(destination)
                    sha = entry.get('sha256')
                    file = child / destination
                    if not isinstance(sha, str) or not HEX64.fullmatch(sha):
                        found.append(f'{prefix}/{destination}: invalid child sha256')
                    elif has_symlink(child, destination):
                        found.append(f'{prefix}/{destination}: symlink child copy')
                    elif not file.is_file():
                        found.append(f'{prefix}/{destination}: missing child copy')
                    elif hashlib.sha256(file.read_bytes()).hexdigest() != sha:
                        found.append(f'{prefix}/{destination}: child lock sha256 mismatch')
            except (OSError, ValueError, TypeError) as exc:
                found.append(f'{prefix}/{filename}: {exc}')
        for file in (child / 'vendor/aoi').rglob('*'):
            if (file.is_file() or file.is_symlink()) and '__pycache__' not in file.parts and file.suffix != '.pyc':
                destination = file.relative_to(child).as_posix()
                if destination not in registered:
                    found.append(f'{prefix}/{destination}: copy missing from child shared-tool locks')
    for path, entry in shared.items():
        for repo in sorted(actual[path] - set(entry['consumers'])):
            found.append(f'{path}: missing consumer {repo}')
        for repo in sorted(set(entry['consumers']) - actual[path]):
            found.append(f'{path}: consumer without locked copy {repo}')
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--warn', action='store_true')
    args = parser.parse_args(argv)
    errors = problems(args.root.resolve())
    for error in errors:
        print(('::warning::' if args.warn else '') + error, file=sys.stderr)
    if not errors:
        print('shared tool consumers ok')
    return int(bool(errors) and not args.warn)


if __name__ == '__main__':
    sys.exit(main())
