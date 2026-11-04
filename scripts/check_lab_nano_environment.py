"""Fail closed when the offline lab lane's installed dependency set drifts.

This is not an installer or test runner. The unchanged uv lock remains the
source of versions; both unexpected additions and missing test plugins fail.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path
import re
import sys
import tomllib

EXPECTED = frozenset({
    'aoi', 'anyio', 'coverage', 'idna', 'iniconfig', 'packaging', 'pluggy',
    'pygments', 'pytest', 'selectolax',
})
OMITTED = frozenset({
    'certifi', 'h11', 'httpcore', 'httpx', 'markdown', 'numpy', 'polars',
    'polars-runtime-32',
})


def canonical_name(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()


def inspect_environment(lock: dict, installed: list[tuple[str, str]]) -> dict:
    versions: dict[str, set[str]] = {}
    for package in lock['package']:
        versions.setdefault(canonical_name(package['name']), set()).add(package['version'])
    actual: dict[str, list[str]] = {}
    for name, version in installed:
        actual.setdefault(canonical_name(name), []).append(version)
    errors = []
    for name in sorted(EXPECTED - actual.keys()):
        errors.append(f'missing installed package: {name}')
    for name in sorted(actual.keys() - EXPECTED):
        errors.append(f'unexpected installed package: {name}')
    for name, values in sorted(actual.items()):
        if len(values) != 1:
            errors.append(f'duplicate installed package: {name}')
        for version in values:
            if version not in versions.get(name, set()):
                errors.append(f'installed version absent from lock: {name}=={version}')
    # Removing a reviewed omission from the lock requires revisiting the lane,
    # rather than silently retaining an ineffective flag forever.
    for name in sorted((EXPECTED | OMITTED) - versions.keys()):
        errors.append(f'reviewed package absent from lock: {name}')
    return {'valid': not errors, 'errors': errors,
            'expected': sorted(EXPECTED), 'omitted': sorted(OMITTED),
            'installed': [{'name': name, 'versions': values}
                          for name, values in sorted(actual.items())]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, default=Path('uv.lock'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    raw = args.lock.read_bytes()
    installed = [(d.metadata['Name'], d.version) for d in metadata.distributions()]
    report = inspect_environment(tomllib.loads(raw.decode('utf-8')), installed)
    if sys.platform != 'linux' or sys.version_info[:2] != (3, 15):
        report['errors'].append('this reviewed lane requires Linux and Python 3.15')
        report['valid'] = False
    report.update(python=sys.version, platform=sys.platform,
                  lock_sha256=hashlib.sha256(raw).hexdigest(),
                  environment_regular_file_bytes=sum(
                      p.stat().st_size for p in Path(sys.prefix).rglob('*')
                      if p.is_file() and not p.is_symlink()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
