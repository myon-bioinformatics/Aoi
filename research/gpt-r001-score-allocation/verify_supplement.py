"""Offline reconciliation of the user-supplied supplemental evidence package."""
import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from inning_features import CL, TEAMS, ROOT, HERE, digest, read_input, require, write_csv


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--share',type=Path,required=True)
    args=ap.parse_args();p=args.share
    manifest={}
    for line in (p/'MANIFEST.sha256').read_text().splitlines():
        m=re.fullmatch(r'([0-9a-f]{64})  (.+)  \((\d+) bytes\)',line)
        require(m is not None,'manifest format')
        h,name,size=m.groups();f=p/name
        require(f.resolve().is_relative_to(p.resolve()),'manifest path')
        require(name not in manifest and f.stat().st_size==int(size) and digest(f)==h,'manifest mismatch')
        manifest[name]=h
    require(set(manifest)=={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}-{'MANIFEST.sha256'},
            'manifest coverage')
    prior=json.loads((HERE/'outputs/inning_features/validation.json').read_text())
    require(digest(p/'data/part4/team_half_innings.csv.gz')==prior['input_sha256'],'inning CSV changed')
    records,nrows=read_input(p/'data/part4/team_half_innings.csv.gz')
    kept={g['url']:g for g in records}
    base={g['href']:g for g in map(json.loads,(ROOT/'data/observations/r001/games.jsonl').read_text().splitlines())}
    require(digest(ROOT/'data/observations/r001/games.jsonl')==prior['baseline_sha256'],'baseline changed')
    require(set(base)=={u for u,g in kept.items() if g['year']<=2025},'baseline URL mismatch')
    raw_rows=json.loads((p/'data/part2/games_raw.json').read_text())
    raw={g['url']:g for g in raw_rows};require(len(raw)==len(raw_rows),'raw duplicates')
    games=read(p/'data/game_list.csv');gm={g['url']:g for g in games}
    ex=read(p/'data/excluded_reasons.csv');em={g['url']:g for g in ex}
    require(len(gm)==len(games) and len(em)==len(ex),'duplicate source/exclusion')
    require(set(gm)==set(kept)|set(em) and not(set(kept)&set(em)),'not a partition')
    for u in em:require(gm[u]['usage']==em[u]['reason'],'reason mismatch')
    for u,g in kept.items():
        require(gm[u]['usage']=='used_regular_season','kept usage mismatch')
        rg=raw[u];require(rg['status']=='final','kept nonfinal')
        for side in ['home','away']:
            seq=rg[side+'_inn']
            require(all(type(x) is int or x in (None,'X') for x in seq),'unknown parsed inning')
            require([x for x in seq if type(x) is int]==g[side+'_runs'],'parsed/CSV inning mismatch')
            require(sum(g[side+'_runs'])==rg[side+'_R'],'parsed sum mismatch')
    # Independently reproduce each team's count cutoff from the supplied parsed games.
    candidates=defaultdict(list)
    for g in raw_rows:
        if g['status']!='final' or any(s in g['title'] for s in ['クライマックス','日本シリーズ','オールスター']):continue
        for side in ['home','away']:
            t='b' if g[side]=='bs' else g[side]
            require(t in TEAMS,'unknown candidate team')
            candidates[g['year'],t].append(g)
    selected=Counter();trimmed=Counter()
    for (y,t),gg in candidates.items():
        cap=120 if y==2020 else 144 if y in (2013,2014) else 143
        for i,g in enumerate(sorted(gg,key=lambda g:(g['date'],g['url']))):
            (selected if i<cap else trimmed)[g['url']]+=1
    require(set(selected)==set(kept) and set(selected.values())=={2},'count-cut selection mismatch')
    require(set(trimmed)=={u for u,g in em.items() if g['reason']=='postseason_trimmed'} and
            set(trimmed.values())=={2},'count-cut exclusion mismatch')
    detail=read(p/'data/part2/trim_check_detail.csv');dm={g['url']:g for g in detail}
    require(len(dm)==len(detail) and set(dm)==set(kept)|set(trimmed),'detail coverage')
    pairs=defaultdict(list)
    for u,b in base.items():
        y=int(b['date'][:4]);pair=tuple(sorted([b['home'],b['away']]))
        pairs[y,pair].append(u)
    for (y,pair),uu in pairs.items():
        inter=(pair[0] in CL)!=(pair[1] in CL)
        expected=(0 if y==2020 else 4 if y in (2013,2014) else 3) if inter else (24 if y in (2013,2014,2020) else 25)
        require(len(uu)==expected,'card count mismatch')
        for n,u in enumerate(sorted(uu,key=lambda u:(base[u]['date'],u)),1):
            require(dm[u]['kind']=='kept' and int(float(dm[u]['label']))==n and
                    int(float(gm[u]['h2h_label']))==n,'provided label mismatch')
    flags=read(p/'data/walkoff_innings.csv');seen=set();counts=Counter();yearcounts=Counter()
    annotations=[]
    for f in flags:
        u=f['url'];side=f['batting_side'];i=int(f['inning']);g=kept[u]
        t='b' if f['batting_team']=='bs' else f['batting_team'];key=(u,t,i)
        require(key not in seen,'duplicate x flag');seen.add(key)
        require(side in ['home','away'] and t==g[side] and int(f['year'])==g['year'],'flag identity')
        require(i==len(g[side+'_runs']) and g[side+'_runs'][i-1]==int(f['runs']),'flag not terminal / score mismatch')
        require(re.fullmatch(r'\d+[xX]',f['raw']) and int(f['raw'][:-1])==int(f['runs']),'raw flag syntax')
        is_walkoff=side=='home' and i>=9 and sum(g['home_runs'])>sum(g['away_runs'])
        kind='walkoff' if is_walkoff else 'incomplete_other'
        require(f['kind'].split('(')[0]==kind,'kind rule mismatch')
        counts[kind]+=1;yearcounts[g['year'],t,kind]+=1
        annotations.append(dict(url=u,year=g['year'],batting_team=t,batting_side=side,inning=i,
                                runs=int(f['runs']),kind=kind,source='supplement_walkoff_innings.csv'))
    fail={u for u,g in raw.items() if not g['check']}
    require(fail<=set(em),'unaccounted sumcheck failure')
    dates=sorted({gm[u]['date'] for u in trimmed}&{gm[u]['date'] for u in base})
    receipt=dict(manifest_files=len(manifest),manifest_sha256=digest(p/'MANIFEST.sha256'),
                 manifest_verified=True,input_csv_unchanged=True,input_rows=nrows,
                 source_urls=len(gm),kept_games=len(kept),excluded=len(em),
                 exclusions=dict(Counter(g['reason'] for g in ex)),
                 cutoff_kept_games=len(selected),cutoff_trimmed_games=len(trimmed),
                 cutoff_two_sided=True,parsed_csv_matched_games=len(kept),
                 pair_count=len(pairs),provided_labels_matched_games=len(base),
                 simultaneous_dates=dates,sumcheck_failures=len(fail),
                 sumcheck_failure_reasons=dict(Counter(em[u]['reason'] for u in fail)),
                 x_flags=len(flags),x_kinds=dict(counts),x_join_mismatches=0,
                 x_flags_2013_2025=sum(f['year']<=2025 for f in annotations),
                 script_sha256=digest(__file__),exit_code=0,
                 limits=['No raw HTML supplied; Nth-game labels and x markers are provided extractions.',
                         'incomplete_other is a classification rule, not an independently verified termination cause.'])
    out=HERE/'outputs';(out/'supplement_validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    write_csv(out/'partial_innings_by_year.csv',[dict(year=y,team=t,kind=k,count=n)
                                               for (y,t,k),n in sorted(yearcounts.items())])
    local=ROOT/'data/observations/r001_inning_features';local.mkdir(parents=True,exist_ok=True)
    write_csv(local/'partial_inning_annotations.csv',annotations)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':
    try:main()
    except FileNotFoundError as e:print(e,file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError) as e:print(e,file=sys.stderr);sys.exit(65)
