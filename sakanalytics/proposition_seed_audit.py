"""Replay optional synthetic seed diagnostics for every compatible proposition.

No fitting, official verdict changes or extra real observations. Missing input
features/identity adapters are explicit None, not failed or invariant outcomes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pythdragoras'))
import polars as pl
import propositions as pr
import league_laboratory as lab

SCHEMA = 'aoi-proposition-seed-evaluation/1'
# Fixed design declared by synthetic_p96_provenance.json; never infer coverage
# from the rows that happen to be present (even if their file SHA is valid).
ANNUAL_UNITS = 2016
ANNUAL_COHORTS = frozenset(
    (seed, profile, conversion)
    for seed, conversion in ((0, 1.), (1, 1.), (2, 1.), (3, .5))
    for profile in ('aligned', 'same_totals', 'reversed'))


def support(prop, columns):
    conditions = [*prop.get('if', []), *(c for g in prop.get('if_any', []) for c in g),
                  *prop['then'], *prop.get('scope', {}).get('where', [])]
    missing = sorted({c['col'] for c in conditions} - set(columns))
    adapter = any(k in prop.get('scope', {}) for k in ('team', 'league')) or any(
        c['col'] in ('team', 'league') for c in conditions)
    return dict(supported=not missing and not adapter, missing_features=missing, needs_identity_adapter=adapter)


def measure(rows, prop):
    st = pl.DataFrame(rows, infer_schema_length=None)
    if pr.scope_unknown(st, prop.get('scope')):
        raise ValueError('unknown synthetic scope')
    st = pr.scope_filter(st, prop.get('scope'))
    flags = st.select(a=pr._antecedent(prop, st.columns), b=pr._cond(prop['then'], st.columns))
    if flags.null_count().row(0) != (0, 0):
        raise ValueError('unknown synthetic predicate')
    a, b = flags['a'], flags['b']
    counts = dict(tp=int((a & b).sum()), fp=int((a & ~b).sum()),
                  fn=int((~a & b).sum()), tn=int((~a & ~b).sum()))
    covariates = {}
    for key in ('RF', 'RA', 'rd', 'W', 'wins_vs_pythag', 'rank_tie', 'upper_half',
                'skill_attack', 'skill_defense', 'skill_conversion'):
        values = [r[key] for r in st.to_dicts() if r.get(key) is not None]
        covariates[key] = statistics.mean(values) if values else None
    return counts, covariates


def generate_plans(cfg, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as z:
            for loss in (0., cfg['evaluation_loss']):
                for seed in range(10):
                    for year in range(2023, 2027):
                        for allocation in lab.allocations(cfg['skill_budget']):
                            cid = f'seed-audit/loss{loss}/b{seed}/{year}/' + '-'.join(map(str, allocation))
                            p = lab.skill_plan(cfg, allocation=allocation, seed=seed * 10000 + year, loss=loss)
                            row = dict(seed=seed, loss=loss, season=year, allocation=allocation, case_id=cid, plan=p)
                            z.write((lab.canonical(row) + '\n').encode())


def build(cycle, plan_path):
    cfg = tomllib.loads((cycle / 'league-laboratory.toml').read_text())
    props, definition_file_sha = pr.load(cycle / 'propositions.toml')
    units = cycle / 'outputs/synthetic_p96_units.jsonl'
    provenance = json.loads((cycle / 'outputs/synthetic_p96_provenance.json').read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    if sha(units) != provenance['files'][units.name]:
        raise ValueError('saved synthetic features differ from checked provenance')
    if type(provenance.get('units')) is not int or provenance['units'] != ANNUAL_UNITS:
        raise ValueError('annual provenance must declare exactly 2016 units')
    annual = defaultdict(list)
    for line in units.read_text().splitlines():
        row = json.loads(line)
        if row.get('synthetic') is not True:
            raise ValueError('synthetic-only features required')
        annual[(row['batch_seed'], row['profile'], row['conversion'])].append(row)
    if set(annual) != ANNUAL_COHORTS:
        raise ValueError('missing or unexpected annual cohorts')
    if sum(map(len, annual.values())) != provenance['units']:
        raise ValueError('annual unit count differs from declared provenance')
    for key, rows in annual.items():
        if len(rows) != 168 or {r['season'] for r in rows} != set(range(2013, 2027)):
            raise ValueError('complete fixed annual cohort required')
        over = ['season', 'league']
        annual[key] = pl.DataFrame(rows).with_columns(
            rank_rf=pl.col('RF').rank('min', descending=True).over(over),
            rank_ra=pl.col('RA').rank('min').over(over),
            rank_pythag=pl.col('pythag_fixed').rank('min', descending=True).over(over),
            rank_rd=pl.col('rd').rank('min', descending=True).over(over)).with_columns(
                rank_gap=pl.col('rank') - pl.col('rank_pythag')).to_dicts()
    skill = defaultdict(list)
    seen = set()
    with gzip.open(plan_path, 'rt') as stream:
        for line in stream:
            case = json.loads(line)
            key = (case['seed'], case['loss'], case['season'], tuple(case['allocation']))
            if key in seen:
                raise ValueError('duplicate skill plan')
            seen.add(key)
            actual = lab.skill_plan(cfg, allocation=case['allocation'],
                                    seed=case['seed'] * 10000 + case['season'], loss=case['loss'])
            if lab.canonical(actual) != lab.canonical(case['plan']):
                raise ValueError('skill plan differs from settings/generator replay')
            for row in lab.annual_features(actual):
                row['season'] = case['season']
                a, d, c = actual['skills'][row['team']]
                row.update(skill_attack=a, skill_defense=d, skill_conversion=c)
                skill[(case['seed'], case['loss'])].append(row)
    expected = {(s, loss, year, tuple(a)) for s in range(10) for loss in (0., cfg['evaluation_loss'])
                for year in range(2023, 2027) for a in lab.allocations(cfg['skill_budget'])}
    if seen != expected:
        raise ValueError('missing or unexpected skill plans')
    registries = {'annual-score-witness': ANNUAL_COHORTS,
                  'skill-budget': {(seed, loss) for seed, loss, _, _ in expected}}
    result = dict(schema=SCHEMA, synthetic=True, real_sample_increment=0, propositions={},
                  inputs=dict(propositions_sha256=definition_file_sha, settings_sha256=sha(cycle / 'league-laboratory.toml'),
                              annual_features_sha256=sha(units), skill_plans_sha256=sha(plan_path)),
                  plan_count=len(seen), analysis_sha256=sha(Path(__file__)),
                  predicate_code_sha256=sha(Path(pr.__file__)), generator_sha256=sha(Path(lab.sl.__file__)),
                  interpretation='Fixed definitions; descriptive seed variation and covariates, no significance or causal verdict.')
    for prop in props:
        pid = prop['id']
        item = dict(definition_sha256=pr.definition_sha(prop), groups=None, reason=None, unavailable=[])
        collected = {}
        for dataset, source in [('annual-score-witness', annual), ('skill-budget', skill)]:
            available = support(prop, next(iter(source.values()))[0].keys())
            if not available['supported']:
                item['unavailable'].append(dict(dataset=dataset, **available))
                continue
            for key, rows in sorted(source.items()):
                condition = dict(proposition=pid, dataset=dataset, definition_sha256=item['definition_sha256'])
                if dataset == 'annual-score-witness':
                    seed, profile, conversion = key
                    condition.update(profile=profile, conversion=conversion, years=list(range(2013, 2027)))
                else:
                    seed, loss = key
                    condition.update(loss=loss, years=list(range(2023, 2027)),
                                     allocations=[list(a) for a in lab.allocations(cfg['skill_budget'])], settings_sha256=lab.digest(cfg))
                counts, covariates = measure(rows, prop)
                group = collected.setdefault(lab.canonical(condition), dict(
                    condition=condition,
                    expected_seeds=sorted(k[0] for k in registries[dataset] if k[1:] == key[1:]),
                    runs=[]))
                group['runs'].append(dict(seed=seed, condition=condition, counts=counts, covariates=covariates))
        if collected:
            item['groups'] = [group for _, group in sorted(collected.items())]
        else:
            item['reason'] = 'synthetic_inputs_or_identity_adapter_unavailable'
        result['propositions'][pid] = item
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cycle-dir', type=Path, required=True,
                        help='サイクルのフォルダ（呼び出し側が解決して渡す）')
    parser.add_argument('--generate-plans', action='store_true')
    args = parser.parse_args(argv)
    cycle = args.cycle_dir.resolve()
    out = cycle / 'outputs/exploratory/proposition-evaluation'
    plans = out / 'skill-seed-plans.jsonl.gz'
    if args.generate_plans:
        generate_plans(tomllib.loads((cycle / 'league-laboratory.toml').read_text()), plans)
    result = build(cycle, plans)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'seed-evaluation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(f"{len(result['propositions'])} propositions; {result['plan_count']} plans replayed")


if __name__ == '__main__':
    main()
