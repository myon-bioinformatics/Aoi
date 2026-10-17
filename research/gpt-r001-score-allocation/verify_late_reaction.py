"""Cross-check all cutoff totals and independently replay comeback paths from CSV."""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['innings','result','cutoff']:ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args();x=json.loads(a.result.read_text());old=json.loads(a.cutoff.read_text())
    om={(r['year'],r['team']):r for r in old['rows']};cells=0
    for r in x['rows']:
        for c in ['6','7']:
            v=r['cutoffs'][c];prior=om[r['year'],r['team']]['cutoffs'][c]
            assert v['excluded']==prior['excluded_short_games']
            for venue in ['all','home','away']:
                p=prior['by_venue'][venue];n=v['by_venue'][venue]
                pairs=[(n['all'],p['all'])]+[(n['by_state'][k],vals) for k,vals in p['state'].items()]
                for new,previous in pairs:
                    assert new[:4]==previous[:4]
                    assert [new[6]+new[8],new[7]+new[9],new[10]+new[12],new[11]+new[13]]==previous[4:8]
                    cells+=1
                for state in ['lead','tie','trail']:
                    for idx,outcome in [(1,'W'),(2,'L'),(3,'T')]:
                        assert n['cross'][state+'|'+outcome][0]==p['state'][state][idx]
                for idx,outcome in [(1,'W'),(2,'L'),(3,'T')]:
                    assert n['by_outcome'][outcome][0]==p['all'][idx]
                for runbin,previous in p['runs'].items():
                    for idx,outcome in [(1,'W'),(2,'L'),(3,'T')]:
                        assert sum(val for key,val in n['joint_by_outcome'][outcome].items() if key.split('|')[0]==runbin)==previous[idx]
    pages=defaultdict(dict)
    with gzip.open(a.innings,'rt') as f:
        for row in csv.DictReader(f):
            year=int(row['year']);team=row['team']
            if row['side']!='off' or not 2013<=year<=2025:continue
            r=pages[year,row['url']].setdefault(team,{'home':row['batting_home'] in ['1','True','true'],'runs':{}})
            r['runs'][int(row['inning'])]=int(row['runs'])
    # Independent chronology: update scoreboard top then bottom, recording own-half endpoints.
    direct=defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:[0,0,0,0])))
    direct_outcome=defaultdict(lambda:[0]*19)
    targeted=set((r['year'],r['team']) for r in x['rows'] if r['team']=='d' or (r['year']==2022 and r['league']=='C'))
    for (year,url),teams in pages.items():
        assert len(teams)==2
        home=next((t,v) for t,v in teams.items() if v['home']);away=next((t,v) for t,v in teams.items() if not v['home'])
        h,a0=home[1]['runs'],away[1]['runs'];score_h=score_a=0;states={home[0]:{},away[0]:{}}
        cutoff_scores={}
        for inning in range(1,max(h.keys()|a0.keys())+1):
            if inning in a0:
                score_a+=a0[inning];states[away[0]][inning]=score_a-score_h
            if inning in h:
                score_h+=h[inning];states[home[0]][inning]=score_h-score_a
            if inning in [6,7] and inning in h and inning in a0:cutoff_scores[inning]=(score_h,score_a)
        for team,ours,theirs,homeflag in [(home[0],h,a0,True),(away[0],a0,h,False)]:
            if (year,team) not in targeted:continue
            outcome='W' if sum(ours.values())>sum(theirs.values()) else 'L' if sum(ours.values())<sum(theirs.values()) else 'T'
            for c,(sh,sa) in cutoff_scores.items():
                eo,et=(sh,sa) if homeflag else (sa,sh)
                ro=sum(v for i,v in ours.items() if c<i<=9);rt=sum(v for i,v in theirs.items() if c<i<=9)
                xo=sum(v for i,v in ours.items() if i>9);xt=sum(v for i,v in theirs.items() if i>9)
                counts=[1,int(outcome=='W'),int(outcome=='L'),int(outcome=='T'),eo,et,ro,rt,xo,xt,
                    sum(c<i<=9 for i in ours),sum(c<i<=9 for i in theirs),sum(i>9 for i in ours),sum(i>9 for i in theirs),
                    int(ro==0),int(ro==1),int(ro==2),int(ro>=3),int(ro+xo>0)]
                for venue in ['all','home' if homeflag else 'away']:
                    key=(year,team,str(c),venue,outcome)
                    direct_outcome[key]=[v+n for v,n in zip(direct_outcome[key],counts)]
                if eo>=et or outcome!='L':continue
                rf=sum(v for i,v in ours.items() if i>c);ra=sum(v for i,v in theirs.items() if i>c)
                deltas=[d for i,d in states[team].items() if i>c]
                if not rf:label='no_late_runs'
                elif max(deltas)>0:label='led_then_lost'
                elif max(deltas)==0:label='tied_never_led'
                else:label='scored_never_tied'
                margin=str(et-eo) if et-eo<=2 else '3+'
                for venue in ['all','home' if homeflag else 'away']:
                    for m in ['all',margin]:
                        key=(year,team,str(c),venue,m)
                        v=direct[key][label]['value']
                        direct[key][label]['value']=[v[0]+1,v[1]+et-eo,v[2]+rf,v[3]+ra]
    checked=0;outcome_checked=0
    for r in x['rows']:
        if (r['year'],r['team']) not in targeted:continue
        for c in ['6','7']:
            for venue,v in r['cutoffs'][c]['by_venue'].items():
                for outcome,values in v['by_outcome'].items():
                    assert values==direct_outcome[r['year'],r['team'],c,venue,outcome]
                    outcome_checked+=1
                for margin,classes in v['losing_comeback'].items():
                    for label,values in classes.items():
                        assert values==direct[r['year'],r['team'],c,venue,margin][label]['value'],(r['year'],r['team'],c,venue,margin,label)
                        checked+=1
    print(f'Prior cutoff cross-check: {cells} cells match; independent top/bottom chronology: {len(targeted)} team-years / {checked} classification cells and {outcome_checked} outcome totals match')

if __name__=='__main__':main()
