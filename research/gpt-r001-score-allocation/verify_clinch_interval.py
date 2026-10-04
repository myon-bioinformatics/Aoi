"""Cross-check the new split against previously verified full-season aggregates."""
import argparse
from collections import Counter
import json
from pathlib import Path
from statistics import NormalDist


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True);p.add_argument('--prior-dir',type=Path,required=True)
    a=p.parse_args();d=json.loads(a.result.read_text());early=json.loads((a.prior_dir/'early_scoring.json').read_text());late=json.loads((a.prior_dir/'late_reaction.json').read_text())
    er={(v['year'],v['team']):v for v in early['rows']};lr={(v['year'],v['team']):v for v in late['rows']};checks=0
    rows={(v['phase'],v['group'],v['cut']):v for v in d['scoring_rows']}
    for group,teams in [('中日',['d']),('他セ5球団',['c','db','g','s','t'])]:
        for cut in [6,7]:
            full=rows['full',group,cut]
            for name in ['annual','counts']:
                summed=Counter(rows['before',group,cut][name]);summed.update(rows['after',group,cut][name])
                assert summed==Counter(full[name]);checks+=1
            prior=Counter()
            for t in teams:prior.update(er[2022,t]['annual'])
            assert prior==Counter(full['annual']);checks+=1
            ps=[er[2022,t]['windows'][str(cut)]['by_venue']['all'] for t in teams]
            for target,key in [('G','G'),('early_RF','RF'),('zero','zero'),('three_plus','three_plus')]:
                assert full['counts'][target]==sum(v[key] for v in ps);checks+=1
            for outcome in ['W','L','T']:
                for target,key in [('G','G'),('reg_RF','reg_RF'),('reg_innings','reg_off_innings'),('extra_RF','extra_RF')]:
                    i=late['columns'].index(key)
                    assert full['counts'].get(outcome+'_'+target,0)==sum(lr[2022,t]['cutoffs'][str(cut)]['by_venue']['all']['by_outcome'][outcome][i] for t in teams);checks+=1
    # Wilson endpoints invert the score-z test: check using independent residual form.
    for r in d['interval_rows']:
        n,k=r['n'],r['k']
        if not n:continue
        for ci in r['intervals']:
            z=ci['z']
            for bound in [ci['lo'],ci['hi']]:
                if 0<bound<1:
                    residual=(k/n-bound)**2-z*z*bound*(1-bound)/n
                    assert abs(residual)<1e-12;checks+=1
            assert abs(ci['coverage_normal']-(2*NormalDist().cdf(z)-1))<1e-14;checks+=1
    print(json.dumps({'checks':checks,'all_match':True}))


if __name__=='__main__':main()
