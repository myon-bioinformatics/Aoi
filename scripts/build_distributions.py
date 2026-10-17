"""Build/check Aoi's frozen stdlib API bundles with the parent-owned minpy tool."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def git(root, *args):
    out = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if out.returncode:
        raise ValueError(out.stderr.strip() or 'git failed')
    return out.stdout.strip()


def path(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(ord(c) < 32 for c in value) or value.startswith('/')
            or any(p in ('', '.', '..') for p in value.split('/'))):
        raise ValueError('unsafe relative path')
    return value


def load_tool(filename, expected):
    filename = Path(filename).resolve()
    if hashlib.sha256(filename.read_bytes()).hexdigest() != expected:
        raise ValueError('minpy tool SHA-256 mismatch')
    spec = importlib.util.spec_from_file_location('_aoi_distribution_minpy', filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build(root, manifest, tool_path, *, check, sources=None):
    if manifest.get('schema') != 'aoi-distributions/1':
        raise ValueError('expected aoi-distributions/1')
    source = manifest['source']
    if not isinstance(source, str) or not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('source must be a full commit SHA')
    tool = load_tool(tool_path, manifest['tool']['sha256'])
    if manifest['python'] != f'{sys.version_info.major}.{sys.version_info.minor}':
        raise ValueError('use the Python major.minor recorded in distributions.json')
    license_path = path(manifest['license'])
    projects = manifest['projects']
    if not isinstance(projects, dict) or not projects:
        raise ValueError('projects must be a nonempty object')
    watched = [license_path]
    outputs = set()
    for name, item in projects.items():
        if not re.fullmatch('[a-z][a-z0-9_]*', name):
            raise ValueError('invalid project name')
        for key in ('entry', 'prefix', 'output'):
            path(item[key])
        if not item['output'].startswith('dist/') or not item['output'].endswith('_min.py'):
            raise ValueError('bundle output must be dist/*_min.py')
        if item['output'].casefold() in outputs:
            raise ValueError('duplicate output')
        outputs.add(item['output'].casefold())
        if 'repository' not in item:
            watched.extend([item['prefix'], item['entry']])
    if git(root, 'diff', '--name-only', source, '--', *watched):
        raise ValueError('distribution source changed; commit it and update the source pin')
    if git(root, 'ls-files', '--others', '--exclude-standard', '--', *watched):
        raise ValueError('distribution source contains uncommitted files')
    generated = {}
    with tempfile.TemporaryDirectory(prefix='aoi-minpy-') as tmp:
        snapshots = {}
        def snapshot_for(repository_root, revision):
            if not re.fullmatch('[0-9a-f]{40}', revision):
                raise ValueError('source must be a full commit SHA')
            key = (str(repository_root), revision)
            if key not in snapshots:
                snapshot = Path(tmp) / str(len(snapshots))
                subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout',
                                str(repository_root), str(snapshot)], check=True)
                git(snapshot, 'checkout', '-q', '--detach', revision)
                snapshots[key] = snapshot
            return snapshots[key]
        aoi = snapshot_for(root, source)
        notice = aoi / license_path
        if not notice.is_file() or notice.is_symlink():
            raise ValueError('license must be a regular file in the frozen source')
        generated['dist/LICENSE'] = notice.read_bytes()
        for name, item in projects.items():
            repository = item.get('repository', 'myon-bioinformatics/Aoi')
            revision = item.get('commit', source)
            source_root = (sources / name).resolve() if 'repository' in item and sources else root
            if 'repository' in item:
                if sources is None:
                    raise ValueError('external source checkout required: ' + name)
                if git(source_root, 'diff', '--name-only', revision) or git(source_root, 'ls-files', '--others', '--exclude-standard'):
                    raise ValueError('external source checkout must match its recorded commit')
            snapshot = snapshot_for(source_root, revision)
            # Keep every origin's notice. A shared one-line license path is valid only
            # while the complete bytes are equal; never silently drop differing text.
            child_notice = snapshot / license_path
            if not child_notice.is_file() or child_notice.is_symlink() or child_notice.read_bytes() != generated['dist/LICENSE']:
                raise ValueError('license differs: ' + name + '; preserve a separate notice before publishing')
            text = tool.bundle(root=str(snapshot), entry=item['entry'], repository=repository,
                               commit=revision, search_paths=item['paths'], require_clean=True)
            header = tool.parse_header(text)
            if header['allow']:
                raise ValueError('only stdlib distributions are allowed')
            generated[item['output']] = text.encode('utf-8')
    # Generate everything before publishing anything. Check mode never writes artifacts.
    mismatch = []
    for relative in generated:
        target = root / relative
        if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != root.parent):
            raise ValueError('output must not traverse symlinks')
    for relative, data in generated.items():
        target = root / relative
        if check:
            if not target.is_file() or target.is_symlink() or target.read_bytes() != data:
                mismatch.append(relative)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if mismatch:
        raise ValueError('distribution mismatch: ' + ', '.join(mismatch))
    return {'schema': 'aoi-distribution-check/1', 'source': source, 'ok': True,
            'mode': 'check' if check else 'build', 'files': list(generated)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--minpy', required=True, type=Path)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--sources', type=Path, help='directory of explicit external source checkouts named by project')
    args = ap.parse_args(argv)
    root = args.root.resolve()
    try:
        manifest = json.loads((root / 'distributions.json').read_text(encoding='utf-8'))
        result = build(root, manifest, args.minpy, check=args.check, sources=args.sources)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print('distributions: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
