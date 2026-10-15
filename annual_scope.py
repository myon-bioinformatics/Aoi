"""Copy only the primary years from an annual cache; keep history as reference."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
from queryu import Cache

PRIMARY_YEARS = tuple(range(2013, 2027))


def primary_cache(source: Path, destination: Path):
    """Validate selected bodies before copying. No requests or source mutations."""
    source, destination = Path(source), Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('destination must be empty; never mix primary and reference caches')
    cache = Cache(source)
    entries = [json.loads(s) for s in cache.manifest.read_text(encoding='utf-8').splitlines() if s.strip()]
    selected = [e for e in entries if int(e['group']) in PRIMARY_YEARS]
    # A primary annual dataset has both leagues, four detailed tables and one archive each.
    expected = {f'{year}_{lg}_{cat}' for year in PRIMARY_YEARS for lg in ('c', 'p')
                for cat in ('std', 'tmb', 'tmp', 'tmf', 'archive')}
    latest = {e['key']: e for e in selected if e['status'] in (200, 404)}
    if set(latest) != expected or any(e['status'] != 200 for e in latest.values()):
        raise ValueError('primary cache must contain all 140 successful annual team pages')
    for e in selected:
        if e.get('file'):
            cache.body_bytes(e)
    destination.mkdir(parents=True, exist_ok=True)
    for name in {e['file'] for e in selected if e.get('file')}:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    (destination / 'manifest.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False)+'\n' for e in selected), encoding='utf-8')
    return len(latest)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    print('primary pages:', primary_cache(a.cache, a.out))


if __name__ == '__main__':
    main()
