"""Frozen, descriptive year/exact-deficit/venue matched stage transitions.

Raw inputs stay local. Imports the existing validated off/def reader; a second
parser/replay below independently checks all published aggregate counts.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

from analyses import read_input, require

PLAN = '7297ef7ef660ecd65152b784d9eb03955be183a7'
SOURCE_HEAD = 'd03b8968b5bdc274d9140590771793e16ef79691'
INPUT_SHA = '0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb'
OFFICIAL_SHA = '730dd865b1de325360736a3a2872fbc97ab5f3dffd923c1350e9e2bfc94bbc12'
DATES_BLOB = '8d55ad8b58928f9013c7e3dde09cf6ccfaa92fd9'
# Frozen projection of PRECLINCH_FLOW_RESULTS.md, same source head as dates blob.
DATES = dict(zip((2013,2014,2015,2016,2017,2018,2019,2021,2022,2023,2024,2025),
    ('2013-09-25','2014-09-23','2015-09-21','2016-09-16','2017-09-20',
     '2018-09-28','2019-09-24','2021-10-13','2022-09-27','2023-09-10',
     '2024-09-20','2025-09-19')))
CL = {'d','g','t','c','db','s'}
COUNTS = ('B','A','L','W','loss','draw')
STAGES = (('B_to_A','B','A'), ('A_to_L','A','L'), ('L_to_W','L','W'),
          ('B_to_L','B','L'), ('B_to_W','B','W'))
ELIGIBLE = ('all_games','cutoff_missing','no_next_top','continued','behind')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def game_date(url):
    match = re.search(r'/s(\d{4})(\d{2})(\d{2})\d+\.html$', url)
    require(match is not None, 'unexpected historical game URL')
    return date(*map(int, match.groups())).isoformat()


def arrivals(home_runs, away_runs, home):
    """Parity-or-better, NOT a separately observed exact-tie visit.

    Same cumulative half-inning convention as matched_comeback.trajectory.
    A direct lead counts as simultaneous A and L. No missing bottom is padded.
    """
    if min(len(home_runs),len(away_runs)) < 7 or len(away_runs) <= 7:
        return None
    own,opp = (home_runs,away_runs) if home else (away_runs,home_runs)
    deficit = sum(opp[:7])-sum(own[:7])
    if deficit <= 0:
        return None
    margins = [sum(own[:i+1])-sum(opp[:i+1 if home else i])
               for i in range(7,len(own))]
    final = sum(own)-sum(opp)
    values = dict(B=1,A=int(any(m>=0 for m in margins)),
                  L=int(any(m>0 for m in margins)),W=int(final>0),
                  loss=int(final<0),draw=int(final==0))
    check_counts(values)
    return deficit,values


def check_counts(c):
    require(all(type(c[f]) is int and c[f]>=0 for f in COUNTS), 'invalid counts')
    require(c['W']<=c['L']<=c['A']<=c['B'], 'arrival ordering')
    require(c['W']+c['loss']+c['draw']==c['B'], 'final outcome partition')


def aggregate(games):
    cells,eligibility = defaultdict(Counter),defaultdict(Counter)
    for g in games:
        y=g['year']
        if y not in DATES:
            continue
        scopes=['full_season']
        if game_date(g['url'])<=DATES[y]:
            scopes.append('preclinch')
        for home in (False,True):
            team=g['home'] if home else g['away']
            if team not in CL:
                continue
            venue='home' if home else 'away'
            own,opp=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            for scope in scopes:
                e=eligibility[scope,y,team,venue]
                e['all_games']+=1
                if min(len(own),len(opp))<7:
                    e['cutoff_missing']+=1
                    continue
                if len(g['away_runs'])<=7:
                    e['no_next_top']+=1
                    continue
                e['continued']+=1
                result=arrivals(g['home_runs'],g['away_runs'],home)
                if result is not None:
                    deficit,values=result
                    e['behind']+=1
                    cells[scope,y,team,venue,deficit].update(values)
    for c in cells.values():
        check_counts(c)
    for e in eligibility.values():
        require(e['all_games']==e['cutoff_missing']+e['no_next_top']+e['continued'],
                'eligibility partition')
    return dict(cells),dict(eligibility)


def replay_input(path):
    """Independent off-only parsing and running top/bottom score replay.

    Does not call read_input, arrivals or aggregate. It verifies the same data,
    not an independent source or a play-by-play reconstruction.
    """
    games=defaultdict(dict)
    with gzip.open(path,'rt',newline='') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or int(r['year']) not in DATES:
                continue
            k=(r['team'],int(r['inning']))
            require(k not in games[r['url']], 'duplicate reference off row')
            games[r['url']][k]=(r['batting_home']=='True',int(r['runs']))
    cells,eligible=defaultdict(Counter),defaultdict(Counter)
    for url,rows in sorted(games.items()):
        year=int(url.split('/')[4]); ds=game_date(url)
        away=next(t for (t,i),(h,r) in rows.items() if not h)
        home=next(t for (t,i),(h,r) in rows.items() if h)
        by_team={t:[rows[t,i][1] for i in range(1,1+max(j for tt,j in rows if tt==t))]
                 for t in (away,home)}
        totals={t:sum(v) for t,v in by_team.items()}
        available=min(map(len,by_team.values()))>=7 and len(by_team[away])>7
        start={t:sum(v[:7]) for t,v in by_team.items()}
        flags={t:[False,False] for t in by_team}
        running=dict(start)
        if available:
            for inning in range(8,1+len(by_team[away])):
                for t,other in ((away,home),(home,away)):
                    if (t,inning) not in rows:
                        continue
                    running[t]+=rows[t,inning][1]
                    if running[t]>=running[other]:flags[t][0]=True
                    if running[t]>running[other]:flags[t][1]=True
        for t,other in ((away,home),(home,away)):
            if t not in CL:continue
            venue='home' if t==home else 'away'
            for scope in ('preclinch','full_season'):
                if scope=='preclinch' and ds>DATES[year]:continue
                e=eligible[scope,year,t,venue];e['all_games']+=1
                if min(map(len,by_team.values()))<7:e['cutoff_missing']+=1
                elif len(by_team[away])<=7:e['no_next_top']+=1
                else:
                    e['continued']+=1
                    deficit=start[other]-start[t]
                    if deficit<=0:continue
                    e['behind']+=1
                    c=cells[scope,year,t,venue,deficit]
                    c['B']+=1;c['A']+=int(flags[t][0]);c['L']+=int(flags[t][1])
                    c['W']+=int(totals[t]>totals[other])
                    c['loss']+=int(totals[t]<totals[other])
                    c['draw']+=int(totals[t]==totals[other])
    return dict(cells),dict(eligible)


def verify_cells(primary,reference,fields):
    require(primary.keys()==reference.keys(), 'reference stratum mismatch')
    for k in primary:
        require(all(primary[k][f]==reference[k][f] for f in fields),
                'reference count mismatch: '+str(k))
    return len(primary)*len(fields)


def verify_annual(games,path):
    totals=defaultdict(Counter)
    for g in games:
        if g['year']>2025:continue
        for t,other in (('home','away'),('away','home')):
            r,ra=sum(g[t+'_runs']),sum(g[other+'_runs'])
            totals[g['year'],g[t]].update(G=1,W=int(r>ra),L=int(r<ra),T=int(r==ra),R=r,RA=ra)
    with Path(path).open(newline='') as f:official=list(csv.DictReader(f))
    require(len(official)==len(totals)==156,'annual coverage')
    seen=set()
    for r in official:
        k=(int(r['year']),r['team'])
        require(k not in seen and k in totals,'annual duplicate/unknown')
        seen.add(k)
        for field in ('G','W','L','T','R','RA'):
            require(totals[k][field]==int(r[field])==int(r['o'+field]),'annual mismatch')
    return len(seen)*6


def fraction_text(value):
    return None if value is None else f'{value.numerator}/{value.denominator}'


def compare(cells,scope,years,venue,den,num):
    ours,peers=defaultdict(Counter),defaultdict(Counter)
    for (p,y,t,v,d),c in cells.items():
        if p!=scope or y not in years or (venue!='all' and v!=venue):continue
        (ours if t=='d' else peers)[y,v,d].update(c)
    common=sorted(k for k in ours if ours[k][den]>0 and peers[k][den]>0)
    unsupported=sorted(k for k in ours if ours[k][den]>0 and peers[k][den]==0)
    n=sum(ours[k][den] for k in common);x=sum(ours[k][num] for k in common)
    pn=sum(peers[k][den] for k in common);px=sum(peers[k][num] for k in common)
    expected=sum((Fraction(ours[k][den]*peers[k][num],peers[k][den]) for k in common),Fraction())
    own=Fraction(x,n) if n else None;peer=expected/n if n else None
    delta=own-peer if n else None
    own_n=sum(c[den] for c in ours.values());own_x=sum(c[num] for c in ours.values())
    return dict(own_all_x=own_x,own_all_n=own_n,
        peer_all_x=sum(c[num] for c in peers.values()),peer_all_n=sum(c[den] for c in peers.values()),
        own_x=x,own_n=n,peer_common_x=px,peer_common_n=pn,
        own_unmatched_x=sum(ours[k][num] for k in unsupported),
        own_unmatched_n=sum(ours[k][den] for k in unsupported),
        common_strata=len(common),unsupported_strata=len(unsupported),
        unsupported_keys=';'.join(f'{y}:{v}:{d}' for y,v,d in unsupported),
        own_coverage=n/own_n if own_n else None,
        peer_expected_x=float(expected) if n else None,
        peer_expected_fraction=fraction_text(expected) if n else None,
        own_rate=float(own) if own is not None else None,
        peer_rate=float(peer) if peer is not None else None,
        difference=float(delta) if delta is not None else None,
        difference_fraction=fraction_text(delta),
        direction='unavailable' if delta is None else 'lower' if delta<0 else 'equal' if delta==0 else 'higher')


def analyze(cells):
    scenarios=[('pooled',set(DATES),v) for v in ('all','home','away')]
    scenarios += [(str(y),{y},'all') for y in DATES]
    return [dict(scope=p,period=period,venue=v,stage=label,denominator=den,numerator=num,
                 **compare(cells,p,ys,v,den,num))
            for p in ('preclinch','full_season') for period,ys,v in scenarios
            for label,den,num in STAGES]


def verify_comparisons(cells,results):
    """Second direct standardization via per-success unit fractions."""
    checks=0
    for r in results:
        ys=set(DATES) if r['period']=='pooled' else {int(r['period'])}
        grouped=defaultdict(lambda:[Counter(),Counter()])
        for (p,y,t,v,d),c in cells.items():
            if p==r['scope'] and y in ys and (r['venue']=='all' or v==r['venue']):
                grouped[y,v,d][int(t!='d')].update(c)
        den,num=r['denominator'],r['numerator'];own_n=own_x=peer_n=peer_x=0
        expectation=Fraction()
        for own,peer in grouped.values():
            if own[den] and peer[den]:
                own_n+=own[den];own_x+=own[num];peer_n+=peer[den];peer_x+=peer[num]
                # Explicit replicated success weights, not the primary product formula.
                expectation+=sum((Fraction(own[den],peer[den]) for _ in range(peer[num])),Fraction())
        require((own_n,own_x,peer_n,peer_x)==(r['own_n'],r['own_x'],r['peer_common_n'],r['peer_common_x']),
                'comparison counts mismatch')
        value=Fraction(own_x,own_n)-expectation/own_n if own_n else None
        require(fraction_text(value)==r['difference_fraction'],'comparison fraction mismatch')
        checks+=5
    return checks


def verify_prior(cells):
    expected={'d':(773,99,58,53),'peer':(3457,480,324,296)}
    for group,values in expected.items():
        actual=tuple(sum(c[f] for (p,y,t,v,d),c in cells.items()
                         if p=='preclinch' and ((t=='d')==(group=='d'))) for f in ('B','A','L','W'))
        require(actual==values, 'prior unadjusted preclinch mismatch')
    return 8


def dump_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('innings','official','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--dates',type=Path,help='Optional original preclinch_dates.json; verify immutable blob/projection')
    a=p.parse_args()
    require(sha(a.innings)==INPUT_SHA,'inning hash mismatch')
    require(sha(a.official)==OFFICIAL_SHA,'official hash mismatch')
    dates_checked=False
    if a.dates:
        raw=a.dates.read_bytes()
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==DATES_BLOB,'date blob mismatch')
        ds=json.loads(raw);ys=[r for r in ds['years'] if r['year'] in DATES]
        require(len(ys)==len(DATES) and all(r['exact'] for r in ys),'date coverage/unresolved')
        require({r['year']:r['date'] for r in ys}==DATES,'date projection mismatch');dates_checked=True
    games,n=read_input(a.innings)
    annual=verify_annual(games,a.official)
    cells,eligibility=aggregate(games)
    ref,eligible_ref=replay_input(a.innings)
    checks=verify_cells(cells,ref,COUNTS)
    eligibility_checks=verify_cells(eligibility,eligible_ref,ELIGIBLE)
    prior=verify_prior(cells)
    results=analyze(cells)
    comparison_checks=verify_comparisons(ref,results)
    cases=[r for r in results if r['period']!='pooled' and r['stage'] in {'B_to_A','A_to_L','L_to_W'}]
    evidence=dict(schema='aoi-stage-transitions/1',plan_commit=PLAN,source_head=SOURCE_HEAD,
        input_sha256=INPUT_SHA,official_sha256=OFFICIAL_SHA,source_dates_git_blob=DATES_BLOB,
        source_dates_blob_checked_locally=dates_checked,dates=DATES,
        date_projection_sha256=hashlib.sha256(json.dumps(DATES,sort_keys=True).encode()).hexdigest(),
        date_provenance='Frozen projection from PRECLINCH_FLOW_RESULTS.md at source_head; original blob identified through connector metadata. No clinch solver rerun.',
        input_rows=n,annual_checks=annual,stage_integer_checks=checks,
        eligibility_integer_checks=eligibility_checks,comparison_checks=comparison_checks,prior_checks=prior,
        cell_count=len(cells),comparison_count=len(results),
        pooled=[r for r in results if r['period']=='pooled'],
        annual_cases=cases,
        counterexamples=[dict(scope=r['scope'],year=int(r['period']),stage=r['stage'],direction=r['direction'],
                              own_x=r['own_x'],own_n=r['own_n'],difference=r['difference'])
                         for r in cases if r['direction'] in {'equal','higher'}],
        interpretation='Descriptive conditional rates. Stage-specific risk sets and weights differ. Do not multiply primary rates or infer cause, ability, or failure to finish.')
    cell_rows=[dict(scope=p,year=y,team=t,venue=v,deficit=d,**{f:c[f] for f in COUNTS})
               for (p,y,t,v,d),c in sorted(cells.items())]
    eligibility_rows=[dict(scope=p,year=y,team=t,venue=v,**{f:c[f] for f in ELIGIBLE})
                      for (p,y,t,v),c in sorted(eligibility.items())]
    # All input, aggregate and comparison validations have passed before any output.
    a.out.mkdir(parents=True,exist_ok=True)
    dump_csv(a.out/'stage_transition_cells.csv',cell_rows)
    dump_csv(a.out/'stage_transition_comparisons.csv',results)
    dump_csv(a.out/'stage_transition_eligibility.csv',eligibility_rows)
    (a.out/'stage_transitions.json').write_text(json.dumps(evidence,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    packed={k:v for k,v in evidence.items() if k not in {'pooled','annual_cases','counterexamples'}}
    for name,rows in (('cells',cell_rows),('comparisons',results),('eligibility',eligibility_rows)):
        packed[name]=dict(columns=list(rows[0]),rows=[list(r.values()) for r in rows])
    raw=json.dumps(packed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()+b'\n'
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0) as stream:
        stream.write(raw)
    (a.out/'stage_transition_evidence.json.gz').write_bytes(buffer.getvalue())
    print(json.dumps(dict(annual_checks=annual,stage_checks=checks,eligibility_checks=eligibility_checks,
                         comparison_checks=comparison_checks,cells=len(cells),comparisons=len(results))))
    for r in results:
        if r['period']=='pooled' and r['venue']=='all':
            print(r['scope'],r['stage'],f"{r['own_x']}/{r['own_n']}",r['peer_rate'],r['difference'],
                  'unmatched',r['own_unmatched_n'],'peer',f"{r['peer_common_x']}/{r['peer_common_n']}")


if __name__=='__main__':main()
