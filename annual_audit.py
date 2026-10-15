"""Annual team tables: exact integer checks and equality at published decimal precision.

No neural model and no inferred historical zeroes. All original columns are retained.
A mismatch is evidence to inspect; never repaired to make totals pass.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
import hashlib
import json
from pathlib import Path


def audit(records, *, expected_years=(), baseline=()):
    checks, units, grouped, seen = [], {}, defaultdict(list), set()
    def equal(name, observed, expected, unit):
        checks.append(dict(check=name,unit=unit,observed=observed,expected=expected,ok=observed==expected))
    def rate(name, numerator, denominator, published, digits, unit, raw=None):
        if denominator:
            token=''.join(str(raw if raw is not None else published).split())
            precision=max(digits,len(token.partition('.')[2]))
            # Extended ranking digits in the observed NPB summaries are truncated
            # (e.g. 1961 Giants .2265 for 958/4228), not rounded to the usual 3 dp.
            extended=precision>digits
            rounding=ROUND_DOWN if extended else ROUND_HALF_UP
            expected=Decimal(numerator)/Decimal(denominator)
            expected=expected.quantize(Decimal(10)**-precision,rounding=rounding)
            equal(name, str(Decimal(str(published)).quantize(Decimal(10)**-precision)), str(expected), unit)
            checks[-1].update(precision=precision,display_policy='observed_extended_truncation' if extended else 'standard_half_up')
    for rec in records:
        if rec['key'] in seen:
            raise ValueError(f"duplicate observation: {rec['key']}")
        seen.add(rec['key'])
        key=(rec['season'],rec['league'],rec['team'])
        if key not in units:
            units[key]=dict(season=key[0],league=key[1],team=key[2],team_name=rec['team_name'],tables={},raw_tables={})
        units[key]['tables'][f"{rec['source_kind']}_{rec['category']}"]=rec['values']
        units[key]['raw_tables'][f"{rec['source_kind']}_{rec['category']}"]=rec.get('raw_values',{})
        grouped[(rec['season'],rec['league'],rec['source_kind'],rec['category'])].append(rec)
    years=sorted(set(expected_years) or {r['season'] for r in records})
    for year in years:
        for lg in ('C','P'):
            kinds={'archive':['standings','batting','pitching']}
            if year>=2005:
                kinds['detail']=['standings','batting','pitching','fielding']
            for source,categories in kinds.items():
                reference={r['team'] for r in grouped[(year,lg,source,'standings')]}
                equal('standings_present',bool(reference),True,f'{year}/{lg}/{source}')
                for cat in categories:
                    teams=[r['team'] for r in grouped[(year,lg,source,cat)]]
                    equal('category_members',sorted(teams),sorted(reference),f'{year}/{lg}/{source}/{cat}')
                    equal('unique_members',len(teams),len(set(teams)),f'{year}/{lg}/{source}/{cat}')
            # No interleague until 2005: retain the actual historical member count.
            if year>=2005:
                equal('six_teams',len({r['team'] for r in grouped[(year,lg,'detail','standings')]}),6,f'{year}/{lg}')
    for key,unit in sorted(units.items()):
        ident='/'.join(map(str,key))
        tables=unit['tables']
        for source in ('detail','archive'):
            st,bat,pitch,field=[tables.get(source+'_'+cat,{}) for cat in ('standings','batting','pitching','fielding')]
            raw=lambda cat,col:unit['raw_tables'].get(source+'_'+cat,{}).get(col)
            if st:
                equal('G=W+L+T',st['試合'],st['勝利']+st['敗北']+st['引分'],ident+'/'+source)
                # Historical winning-percentage rules varied: no unverified modern rule applied before 2005.
                if key[0]>=2005:
                    rate('winning_percentage',st['勝利'],st['勝利']+st['敗北'],st['勝率'],3,ident+'/'+source,raw('standings','勝率'))
            for cat,table in [('batting',bat),('pitching',pitch),('fielding',field)]:
                if table and st:
                    equal('G:'+cat,table['試合'],st['試合'],ident+'/'+source)
            if pitch and st:
                for col in ('勝利','敗北'):
                    equal('pitching:'+col,pitch[col],st[col],ident+'/'+source)
            if bat:
                rate('batting_average',bat['安打'],bat['打数'],bat['打率'],3,ident+'/'+source,raw('batting','打率'))
                tb=bat['安打']+bat['二塁打']+2*bat['三塁打']+3*bat['本塁打']
                if '塁打' in bat: equal('total_bases',bat['塁打'],tb,ident+'/'+source)
                if '長打率' in bat: rate('slugging',tb,bat['打数'],bat['長打率'],3,ident+'/'+source,raw('batting','長打率'))
                if '出塁率' in bat:
                    rate('onbase',bat['安打']+bat['四球']+bat['死球'],bat['打数']+bat['四球']+bat['死球']+bat['犠飛'],bat['出塁率'],3,ident+'/'+source,raw('batting','出塁率'))
            if pitch and '自責点' in pitch:
                rate('ERA',pitch['自責点']*27,pitch['投球回アウト'],pitch['防御率'],2,ident+'/'+source,raw('pitching','防御率'))
            if field:
                equal('fielding_chances',field['守備機会'],field['刺殺']+field['補殺']+field['失策'],ident+'/'+source)
                rate('fielding_percentage',field['刺殺']+field['補殺'],field['守備機会'],field['守備率'],3,ident+'/'+source,raw('fielding','守備率'))
            # The home/road and head-to-head columns are also observations, not discarded text.
            if st and all(isinstance(st.get(c),dict) for c in ('ホーム','ロード')):
                for col,label in [('W','勝利'),('L','敗北'),('T','引分')]:
                    equal('home_road:'+col,st['ホーム'][col]+st['ロード'][col],st[label],ident+'/'+source)
        for cat in ('standings','batting','pitching'):
            a,b=tables.get('archive_'+cat,{}),tables.get('detail_'+cat,{})
            for col in sorted(a.keys() & b.keys()):
                # Literal source precision is preserved; IP outs has an exact integer counterpart.
                if col=='投球回':continue
                if col in {'打率','長打率','出塁率','防御率','勝率','守備率'}:
                    base=2 if col=='防御率' else 3
                    raw_a=unit['raw_tables'].get('archive_'+cat,{}).get(col,str(a[col]))
                    raw_b=unit['raw_tables'].get('detail_'+cat,{}).get(col,str(b[col]))
                    da=max(base,len(''.join(str(raw_a).split()).partition('.')[2]))
                    db=max(base,len(''.join(str(raw_b).split()).partition('.')[2]))
                    precision=min(da,db)
                    qa=Decimal(str(a[col])).quantize(Decimal(10)**-precision,rounding=ROUND_HALF_UP)
                    qb=Decimal(str(b[col])).quantize(Decimal(10)**-precision,rounding=ROUND_HALF_UP)
                    equal('cross_source:'+cat+':'+col,str(qa),str(qb),ident)
                    checks[-1].update(common_precision=precision,raw_observed=raw_a,raw_expected=raw_b)
                else:
                    equal('cross_source:'+cat+':'+col,a[col],b[col],ident)
            if cat=='pitching' and a and b and '自責点' in b:
                rate('cross_source:ERA_from_detail_counts',b['自責点']*27,a['投球回アウト'],a['防御率'],2,ident,
                     unit['raw_tables'].get('archive_pitching',{}).get('防御率'))
        chosen='detail' if 'detail_standings' in tables else 'archive'
        st,bat,pitch=[tables.get(chosen+'_'+cat,{}) for cat in ('standings','batting','pitching')]
        if st and bat and pitch:
            unit.update(G=st['試合'],W=st['勝利'],L=st['敗北'],T=st['引分'],RF=bat['得点'],RA=pitch['失点'])
            den=unit['RF']**1.83+unit['RA']**1.83
            unit['pythag_fixed']=unit['RF']**1.83/den if den else None
            unit['pythag_expected_wins']=(unit['W']+unit['L'])*unit['pythag_fixed'] if den else None
    for year in years:
        for source in ('archive','detail'):
            keys=['standings','batting','pitching','fielding']
            cats={cat:[r['values'] for r in records if r['season']==year and r['source_kind']==source and r['category']==cat] for cat in keys}
            st,bat,pitch,field=[cats[c] for c in keys]
            if st:
                equal('global_W=L',sum(r['勝利'] for r in st),sum(r['敗北'] for r in st),f'{year}/{source}')
                equal('global_draw_even',sum(r['引分'] for r in st)%2,0,f'{year}/{source}')
            if bat and pitch:
                equal('global_RF=RA',sum(r['得点'] for r in bat),sum(r['失点'] for r in pitch),f'{year}/{source}')
                for col in ('安打','本塁打','四球','死球','三振'):
                    if all(col in r and r[col] is not None for r in bat+pitch):
                        equal('global_bat=pitch:'+col,sum(r[col] for r in bat),sum(r[col] for r in pitch),f'{year}/{source}')
            if field and pitch:
                equal('global_outs',sum(r['刺殺'] for r in field),sum(r['投球回アウト'] for r in pitch),f'{year}/{source}')
    for r in baseline:
        u=units.get((r['season'],r['league'],r['team']))
        if u:
            for col in ('G','W','L','T','RF','RA'):
                equal('existing_season:'+col,u.get(col),r[col],f"{r['season']}/{r['league']}/{r['team']}")
    failures=[c for c in checks if not c['ok']]
    return {'schema':'aoi-annual-audit/1','years':years,'team_seasons':len(units),
            'checks':checks,'passed':len(checks)-len(failures),'failed':len(failures),'failures':failures,
            'annual':list(units.values()),'comparison_policy':'integers exact; normal rate digits ROUND_HALF_UP; observed extended digits truncated to source precision; historical win-percentage rules not guessed'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--observations',type=Path,required=True)
    p.add_argument('--years',required=True)
    p.add_argument('--baseline',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--annual-out',type=Path,required=True)
    a=p.parse_args()
    read=lambda path:[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
    start,end=map(int,a.years.split('-'))
    r=audit(read(a.observations),expected_years=range(start,end+1),baseline=read(a.baseline) if a.baseline else [])
    manifest=a.observations.with_suffix('.manifest.json')
    extras=[]
    if not manifest.exists():
        extras.append(dict(check='source_manifest_present',unit=str(a.observations),observed=False,expected=True,ok=False))
    else:
        metadata=json.loads(manifest.read_text(encoding='utf-8'))
        value=metadata.get('unknown')
        extras.append(dict(check='source_unknown_zero',unit=str(a.observations),observed=value,expected=0,ok=type(value) is int and value==0))
        digest=hashlib.sha256(a.observations.read_bytes()).hexdigest()
        extras.append(dict(check='source_dataset_sha256',unit=str(a.observations),observed=digest,expected=metadata.get('sha256'),ok=digest==metadata.get('sha256')))
        r['source_parser_sha256']=metadata.get('source_code_sha256')
    for extra in extras:
        r['checks'].append(extra)
        if extra['ok']:r['passed']+=1
        else:r['failed']+=1;r['failures'].append(extra)
    r['source_sha256']=hashlib.sha256(a.observations.read_bytes()).hexdigest()
    for path in (a.out,a.annual_out):path.parent.mkdir(parents=True,exist_ok=True)
    a.annual_out.write_text(''.join(json.dumps(s,ensure_ascii=False)+'\n' for s in r.pop('annual')),encoding='utf-8')
    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"annual audit: {r['team_seasons']} team-seasons, {r['passed']} passed, {r['failed']} failed")
    return int(bool(r['failed']))


if __name__=='__main__':
    raise SystemExit(main())
