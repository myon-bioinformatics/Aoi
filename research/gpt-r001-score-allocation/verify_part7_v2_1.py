"""Check supplied v2.1 audit tables against unchanged v2 inputs; emit aggregates only."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from verify_part7_v2 import read, require, sha


def verify(source, previous):
    source, previous = Path(source), Path(previous)
    old = {str(p.relative_to(previous)): p for p in previous.rglob('*') if p.is_file()}
    new = {str(p.relative_to(source)): p for p in source.rglob('*') if p.is_file()}
    added = {'v2/errata_v2_1.md', 'v2/audit_cspo_min_vs_rowlevel_v2.csv',
             'v2/audit_cspo_rows_v2_public.csv'}
    require(set(new) - set(old) == added and not set(old) - set(new), 'unexpected file inventory')
    require(all(sha(p) == sha(new[n]) for n, p in old.items()), 'v2 input changed')
    key = lambda r: tuple(r[k] for k in ('year', 'slug', 'inning', 'half'))
    halves = list(read(source/'v2/half_innings_v2_public.csv.gz'))
    bykey = {key(r): r for r in halves}
    require(len(bykey) == len(halves), 'duplicate half key')
    rows = list(read(source/'v2/audit_cspo_rows_v2_public.csv'))
    grouped = defaultdict(list)
    for r in rows:
        require(key(r) in bykey, 'unknown event half')
        require(r['type'] in ('CS', 'PO') and r['runner_out'] in ('0', '1'), 'unknown event classification')
        require(r['complete'] == bykey[key(r)]['complete'], 'complete flag mismatch')
        grouped[key(r)].append(r)
    for h in halves:
        rs = grouped[key(h)]
        for kind in ('CS', 'PO'):
            for flag, suffix in ((None, ''), ('1', '_out'), ('0', '_noout')):
                n = sum(r['type'] == kind and (flag is None or r['runner_out'] == flag) for r in rs)
                require(n == float(h[kind + suffix]), 'event aggregate mismatch: '+kind+suffix)
        require(float(h['CSPO_undet']) == 0, 'undetermined events not represented')
        require(sum(int(r['runner_out']) for r in rs) == float(h['CSPO_out_rowlevel']), 'row-level mismatch')
    mismatch = {key(h): h for h in halves if h['complete'] == 'True'
                and float(h['CSPO_out']) != float(h['CSPO_out_rowlevel'])}
    supplied = list(read(source/'v2/audit_cspo_min_vs_rowlevel_v2.csv'))
    require(len({key(r) for r in supplied}) == len(supplied), 'duplicate mismatch half')
    require({key(r) for r in supplied} == set(mismatch), 'mismatch case set differs')
    kinds, years = Counter(), Counter()
    for r in supplied:
        h = mismatch[key(r)]
        for col, value in r.items():
            require(value == h[col] or (col not in ('year','slug','team','inning','half')
                    and float(value) == float(h[col])), 'mismatch table cell differs: '+col)
        rs = grouped[key(r)]
        require(len(rs) == 1 and rs[0]['runner_out'] == '0', 'unexpected mismatch event')
        require(float(h['batter_outs']) == 2 and float(h['RO']) == 1
                and float(h['CSPO_out']) == 1 and float(h['RO_other']) == 0, 'unexpected allocation')
        kinds[rs[0]['type']] += 1
        years[h['year']] += 1
    return dict(schema='aoi-part7-v2.1-reception/1', status='provided_audit_tables_consistent',
                unchanged_v2_files=len(old), added_files=sorted(added),
                input_sha256={n: sha(p) for n,p in sorted(new.items())},
                event_rows=len(rows), event_counts=dict(Counter(r['type'] for r in rows)),
                event_runner_out_counts=dict(Counter(r['runner_out'] for r in rows)),
                event_complete_counts=dict(Counter(r['complete'] for r in rows)),
                half_rows_checked=len(halves), mismatch_halves=len(supplied),
                mismatch_event_types=dict(kinds), mismatch_year_counts=dict(years),
                monte_carlo_zero_exceedance_one_sided_95_upper=1-0.05**(1/200000),
                limitations=['internal consistency of provided derived tables, not independent raw-event validation',
                             'event rows lack sequential before/after states and non-CS/PO events',
                             'min assignment remains inferred; 2026 remains provisional',
                             'original v2 report and finite z at p=1 unchanged; errata takes precedence'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--previous', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    result = verify(a.source, a.previous)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('input_sha256','limitations')},ensure_ascii=False))


if __name__ == '__main__':
    main()
