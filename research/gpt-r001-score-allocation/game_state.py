"""Late-game score-state frequencies and subsequent outcomes, descriptive only."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from inning_features import read_input, require
from matched_comeback import INPUT_SHA, SEASON_BLOB

FIELDS=('G','W','L','T','late_RF','late_RA','off_innings','def_innings')
BINS=('-3+','-2','-1','0','1','2','3+')


def bucket(m):
    return '-3+' if m<=-3 else '3+' if m>=3 else str(m)


def total(rows):
    return {f:sum(r[f] for r in rows) for f in FIELDS}


def describe(c, denominator):
    return dict(**c,share=c['G']/denominator if denominator else None,
                win_fraction=c['W']/c['G'] if c['G'] else None,
                win_rate=c['W']/(c['W']+c['L']) if c['W']+c['L'] else None)


def summarize(rows):
    all_=total(rows);n=all_['G']
    bins={b:describe(total([r for r in rows if bucket(r['margin'])==b]),n) for b in BINS}
    states={name:describe(total([r for r in rows if (r['margin']>0)-(r['margin']<0)==sign]),n)
            for name,sign in [('trail',-1),('tie',0),('lead',1)]}
    for f in FIELDS:
        require(sum(b[f] for b in bins.values())==all_[f], 'bin partition')
        require(sum(b[f] for b in states.values())==all_[f], 'state partition')
    return dict(all=describe(all_,n),bins=bins,states=states)


def contrast(own,peer):
    output={}
    for name,state,metric,sign in [('S1','trail','share',1),('S2','lead','share',-1),('S3','lead','win_fraction',-1)]:
        a,b=own['states'][state],peer['states'][state]
        dena=own['all']['G'] if metric=='share' else a['G']
        denb=peer['all']['G'] if metric=='share' else b['G']
        numa=a['G'] if metric=='share' else a['W'];numb=b['G'] if metric=='share' else b['W']
        d=numa/dena-numb/denb if dena and denb else None
        supports=(numa*denb-numb*dena)*sign>0 if d is not None else None
        output[name]=dict(own=[numa,dena],peer=[numb,denb],difference=d,
                          verdict='supports_direction' if supports else 'counterexample' if supports is False else 'unavailable')
    return output


def build(innings,season):
    require(hashlib.sha256(innings.read_bytes()).hexdigest()==INPUT_SHA,'inning hash mismatch')
    raw=season.read_bytes();require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==SEASON_BLOB,'season blob mismatch')
    st={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    games,input_rows=read_input(innings);annual=defaultdict(Counter);cells=defaultdict(Counter);excluded=Counter()
    for g in games:
        if g['year']>2025:continue
        for home in (True,False):
            team=g['home'] if home else g['away'];own,opp=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            d=sum(own)-sum(opp);y=g['year'];league=st[y,team]['league']
            annual[y,team].update(G=1,RF=sum(own),RA=sum(opp),W=int(d>0),L=int(d<0),T=int(d==0))
            for cut in (6,7):
                if min(len(own),len(opp))<cut or len(g['away_runs'])<=cut:
                    excluded[y,team,cut]+=1;continue
                margin=sum(own[:cut])-sum(opp[:cut])
                cells[y,team,league,cut,home,margin].update(G=1,W=int(d>0),L=int(d<0),T=int(d==0),
                    late_RF=sum(own[cut:]),late_RA=sum(opp[cut:]),off_innings=len(own)-cut,def_innings=len(opp)-cut)
    require(len(annual)==156,'coverage')
    for k,v in annual.items():require(dict(v)=={f:st[k][f] for f in v},'annual mismatch')
    rows=[dict(year=y,team=t,league=l,cutoff=c,home=h,margin=m,**{f:v[f] for f in FIELDS})
          for (y,t,l,c,h,m),v in sorted(cells.items())]
    for r in rows:require(r['W']+r['L']+r['T']==r['G'],'outcome partition')
    return rows,[dict(year=y,team=t,cutoff=c,excluded=n) for (y,t,c),n in sorted(excluded.items())],input_rows


def analyze(rows):
    comparisons=[]
    periods=[(str(y),{y}) for y in range(2013,2026)]+[('no2020',set(range(2013,2026))-{2020}),('with2020',set(range(2013,2026)))]
    for period,years in periods:
        for cut in (6,7):
            for venue in ('all','home','away'):
                subset=[r for r in rows if r['year'] in years and r['cutoff']==cut and (venue=='all' or r['home']==(venue=='home'))]
                for team,league in sorted({(r['team'],r['league']) for r in rows}):
                    own=summarize([r for r in subset if r['team']==team])
                    peer=summarize([r for r in subset if r['league']==league and r['team']!=team])
                    comparisons.append(dict(period=period,team=team,league=league,cutoff=cut,venue=venue,own=own,peer=peer,propositions=contrast(own,peer)))
    cases=[dict(year=int(r['period']),team=r['team'],**r['propositions']) for r in comparisons
           if r['period'].isdigit() and r['period']!='2020' and r['cutoff']==7 and r['venue']=='all']
    return comparisons,cases


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('innings','season','out','csv'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--plan-commit',required=True)
    a=p.parse_args();rows,excluded,n=build(a.innings,a.season);comparisons,cases=analyze(rows)
    result=dict(schema='aoi-game-state/1',plan_commit=a.plan_commit,input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,input_rows=n,
                annual_checks=936,excluded=excluded,comparisons=comparisons,primary_cases=cases,
                scope='descriptive all-team score-state distributions; no causal or opponent-strength adjustment')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'),sort_keys=True)+'\n')
    with a.csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    for r in comparisons:
        if r['team']=='d' and r['venue']=='all' and r['cutoff']==7:
            print(r['period'],r['propositions'])


if __name__=='__main__':main()
