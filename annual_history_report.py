"""Join real annual audit and explicitly separate synthetic model-check evidence."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def summary(observations,audit_file,annual_file,experiment_files,cache_manifest):
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    audit=read(audit_file)
    if audit['source_sha256']!=digest(observations):raise ValueError('audit refers to a different observation dataset')
    rows=[json.loads(s) for s in observations.read_text(encoding='utf-8').splitlines() if s.strip()]
    cache=[json.loads(s) for s in cache_manifest.read_text(encoding='utf-8').splitlines() if s.strip()]
    inventory=defaultdict(set)
    derived=defaultdict(set)
    for r in rows:
        key=r['source_kind']+'/'+r['category']
        inventory[key].update(set(r['raw_values'])-{'チーム'})
        derived[key].update(set(r['values'])-set(r['raw_values']))
    checks=defaultdict(Counter)
    for c in audit['checks']:checks[c['check']]['passed' if c['ok'] else 'failed']+=1
    synthetic=[]
    for path in experiment_files:
        e=read(path)
        if e.get('synthetic') is not True:raise ValueError('experiment must declare synthetic identity')
        if not e.get('calibration') or e['calibration']['sha256']!=digest(annual_file):raise ValueError('experiment calibration does not match the audited annual table')
        controls=e['negative_controls']
        synthetic.append(dict(leagues=e['leagues'],cases=len(e['cases']),groups=e['groups'],
                              games=sum(c['games'] for c in e['cases']),negative_controls=len(controls),
                              rejected_controls=sum(c['rejected'] for c in controls),
                              control_types=dict(Counter(c['kind'] for c in controls)),
                              calibration=e['calibration'],generator_sha256=e['generator_sha256'],
                              python_version=e['python_version'],sha256=digest(path)))
    return dict(schema='aoi-annual-history-validation/1',
                real=dict(years=audit['years'],team_seasons=audit['team_seasons'],records=len(rows),
                          cached_pages=len({r['key'] for r in cache}),acquisition_events=len(cache),
                          checks_passed=audit['passed'],checks_failed=audit['failed'],
                          failures=audit['failures'],checks_by_kind=dict(checks),
                          observed_columns={k:sorted(v) for k,v in sorted(inventory.items())},
                          derived_columns={k:sorted(v) for k,v in sorted(derived.items()) if v},
                          observations_sha256=digest(observations),annual_sha256=digest(annual_file),
                          parser_sha256=audit['source_parser_sha256'],comparison_policy=audit['comparison_policy']),
                synthetic=synthetic,
                interpretation='Synthetic success counts are model-conditional consistency checks, not additional observed NPB samples or a causal verdict about Chunichi.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--observations',type=Path,required=True)
    p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--annual',type=Path,required=True)
    p.add_argument('--experiment',type=Path,action='append',required=True)
    p.add_argument('--cache-manifest',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    result=summary(a.observations,a.audit,a.annual,a.experiment,a.cache_manifest)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('real',result['real']['checks_passed'],'passed',result['real']['checks_failed'],'failed')
    print('synthetic',sum(s['cases'] for s in result['synthetic']),'cases',sum(s['games'] for s in result['synthetic']),'games')
    return int(bool(result['real']['checks_failed']))


if __name__=='__main__':raise SystemExit(main())
