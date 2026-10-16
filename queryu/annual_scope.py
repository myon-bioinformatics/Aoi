"""Copy only the primary years from an annual cache; keep history as reference."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import hashlib
import sys
from queryu import Cache

PRIMARY_YEARS = tuple(range(2013, 2027))


def primary_entries(entries):
    """Require the exact official key/URL/year mapping, not just 140 labels."""
    expected={}
    for year in PRIMARY_YEARS:
        for lg,league in (('c','centralleague'),('p','pacificleague')):
            for cat in ('std','tmb','tmp','tmf','archive'):
                path=f'yearly/{league}_{year}.html' if cat=='archive' else f'{year}/stats/{cat}_{lg}.html'
                expected[f'{year}_{lg}_{cat}']=(str(year),'https://npb.jp/bis/'+path)
    latest={e['key']:e for e in entries if e['status'] in (200,404)}
    if set(latest)!=set(expected) or any(e['status']!=200 for e in latest.values()):
        raise ValueError('primary cache must contain all 140 successful annual team pages')
    for entry in entries:
        if (str(entry['group']),entry['url'])!=expected.get(entry['key']):
            raise ValueError('primary cache key/URL/year mismatch')
    return latest


def primary_cache(source: Path, destination: Path):
    """Validate selected bodies before copying. No requests or source mutations."""
    source, destination = Path(source), Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('destination must be empty; never mix primary and reference caches')
    cache = Cache(source)
    entries = [json.loads(s) for s in cache.manifest.read_text(encoding='utf-8').splitlines() if s.strip()]
    selected = [e for e in entries if int(e['group']) in PRIMARY_YEARS]
    # A primary annual dataset has both leagues, four detailed tables and one archive each.
    latest = primary_entries(selected)
    for e in selected:
        if e.get('file'):
            cache.body_bytes(e)
    for e in latest.values():cache.body_bytes(e)
    destination.mkdir(parents=True, exist_ok=True)
    for name in {e['file'] for e in selected if e.get('file')}:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    (destination / 'manifest.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False)+'\n' for e in selected), encoding='utf-8')
    return len(latest)


def verify_observations(cache_root, observations):
    """Replay saved official bytes; no live requests and no cache mutations."""
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'blueprobe'))
    import npb_team_annual as source
    cache=Cache(cache_root)
    entries=[json.loads(s) for s in cache.manifest.read_text(encoding='utf-8').splitlines() if s.strip()]
    latest=primary_entries(entries)
    for entry in entries:
        if entry.get('file'):cache.body_bytes(entry)
    observed=Path(observations)
    metadata=json.loads(observed.with_suffix('.manifest.json').read_text(encoding='utf-8'))
    parser_sha=hashlib.sha256(Path(source.__file__).read_bytes()).hexdigest()
    if metadata.get('source_code_sha256')!=parser_sha or metadata.get('sha256')!=hashlib.sha256(observed.read_bytes()).hexdigest() or type(metadata.get('unknown')) is not int or metadata['unknown']!=0:
        raise ValueError('observation/parser manifest mismatch')
    replayed=[]
    for entry in latest.values():
        report=source.parse(cache.body(entry),entry['url'])
        if report['unknown']:raise ValueError('unknown values in source replay')
        replayed.extend(report['records'])
    rows=[json.loads(s) for s in observed.read_text(encoding='utf-8').splitlines() if s.strip()]
    if sorted(replayed,key=lambda r:r['key'])!=sorted(rows,key=lambda r:r['key']):
        raise ValueError('observation records differ from official cache replay')
    return dict(pages=len(latest),records=len(rows),parser_sha256=parser_sha)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--out', type=Path)
    p.add_argument('--verify-observations',type=Path,help='replay primary HTML into this saved dataset; requires existing BlueProbe dependencies')
    a = p.parse_args()
    if a.verify_observations:
        if a.out:p.error('choose verification or copying')
        print('primary source replay:',verify_observations(a.cache,a.verify_observations))
    else:
        if not a.out:p.error('--out or --verify-observations required')
        print('primary pages:', primary_cache(a.cache, a.out))


if __name__ == '__main__':
    main()
