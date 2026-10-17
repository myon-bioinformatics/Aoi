#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: 2bf96800b682c9b58b438e1d274267e3fcf832a3
# entry: distributions/entries/sakanalytics_api.py
# entry-module: sakanalytics_api
# search-paths: distributions/entries,sakanalytics
# allow: 
# allow-cycles: no
# cycles: 
# modules: annual_audit,neighbors,sakanalytics_api
# prefix: _minpy_558097f6c30b18b6
# content-sha256: fff1bc39112866ff85e775d6c21dc61b708549379d3efe423be25b21c8d793a1
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_558097f6c30b18b6"
_MINPY_ENTRY = "sakanalytics_api"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "annual_audit": "\"\"\"Annual team tables: exact integer checks and equality at published decimal precision.\n\nNo neural model and no inferred historical zeroes. All original columns are retained.\nA mismatch is evidence to inspect; never repaired to make totals pass.\n\"\"\"\nfrom __future__ import annotations\n\nimport argparse\nfrom collections import Counter, defaultdict\nfrom decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN\nimport hashlib\nimport json\nfrom pathlib import Path\n\nOPPONENTS = dict(zip(('\u5bfe\u5de8','\u5bfe\u4e2d','\u5bfe\u795e','\u5bfe\u30c7','\u5bfe\u30e4','\u5bfe\u5e83','\u5bfe\u30bd','\u5bfe\u65e5','\u5bfe\u30aa','\u5bfe\u697d','\u5bfe\u897f','\u5bfe\u30ed'),\n                     ('g','d','t','db','s','c','h','f','b','e','l','m')))\n\n\ndef audit(records, *, expected_years=(), baseline=()):\n    records=list(records)\n    expected_years=tuple(expected_years)\n    checks, units, grouped, seen, identities = [], {}, defaultdict(list), set(), set()\n    def equal(name, observed, expected, unit):\n        checks.append(dict(check=name,unit=unit,observed=observed,expected=expected,ok=observed==expected))\n    def rate(name, numerator, denominator, published, digits, unit, raw=None):\n        if denominator:\n            token=''.join(str(raw if raw is not None else published).split())\n            precision=max(digits,len(token.partition('.')[2]))\n            # Extended ranking digits in the observed NPB summaries are truncated\n            # (e.g. 1961 Giants .2265 for 958/4228), not rounded to the usual 3 dp.\n            extended=precision>digits\n            rounding=ROUND_DOWN if extended else ROUND_HALF_UP\n            expected=Decimal(numerator)/Decimal(denominator)\n            expected=expected.quantize(Decimal(10)**-precision,rounding=rounding)\n            equal(name, str(Decimal(str(published)).quantize(Decimal(10)**-precision)), str(expected), unit)\n            checks[-1].update(precision=precision,display_policy='observed_extended_truncation' if extended else 'standard_half_up')\n    for rec in records:\n        if rec['key'] in seen:\n            raise ValueError(f\"duplicate observation: {rec['key']}\")\n        seen.add(rec['key'])\n        key=(rec['season'],rec['league'],rec['team'])\n        identity=(*key,rec['source_kind'],rec['category'])\n        if identity in identities:\n            raise ValueError(f'duplicate observation identity: {identity}')\n        identities.add(identity)\n        if key not in units:\n            units[key]=dict(season=key[0],league=key[1],team=key[2],team_name=rec['team_name'],tables={},raw_tables={})\n        units[key]['tables'][f\"{rec['source_kind']}_{rec['category']}\"]=rec['values']\n        units[key]['raw_tables'][f\"{rec['source_kind']}_{rec['category']}\"]=rec.get('raw_values',{})\n        grouped[(rec['season'],rec['league'],rec['source_kind'],rec['category'])].append(rec)\n    years=sorted(set(expected_years) or {r['season'] for r in records})\n    if expected_years:\n        equal('observation_years',sorted({r['season'] for r in records}),years,'dataset')\n    for year in years:\n        for lg in ('C','P'):\n            kinds={'archive':['standings','batting','pitching']}\n            if year>=2005:\n                kinds['detail']=['standings','batting','pitching','fielding']\n            for source,categories in kinds.items():\n                reference={r['team'] for r in grouped[(year,lg,source,'standings')]}\n                equal('standings_present',bool(reference),True,f'{year}/{lg}/{source}')\n                for cat in categories:\n                    teams=[r['team'] for r in grouped[(year,lg,source,cat)]]\n                    equal('category_members',sorted(teams),sorted(reference),f'{year}/{lg}/{source}/{cat}')\n                    equal('unique_members',len(teams),len(set(teams)),f'{year}/{lg}/{source}/{cat}')\n            # No interleague until 2005: retain the actual historical member count.\n            if year>=2005:\n                equal('six_teams',len({r['team'] for r in grouped[(year,lg,'detail','standings')]}),6,f'{year}/{lg}')\n                equal('cross_source_members',sorted(r['team'] for r in grouped[(year,lg,'archive','standings')]),\n                      sorted(r['team'] for r in grouped[(year,lg,'detail','standings')]),f'{year}/{lg}')\n            for source in kinds:\n                extra=grouped[(year,lg,source,'interleague')]\n                if extra:\n                    equal('interleague_members',sorted(r['team'] for r in extra),\n                          sorted(r['team'] for r in grouped[(year,lg,source,'standings')]),f'{year}/{lg}/{source}')\n    for key,unit in sorted(units.items()):\n        ident='/'.join(map(str,key))\n        tables=unit['tables']\n        for source in ('detail','archive'):\n            st,bat,pitch,field=[tables.get(source+'_'+cat,{}) for cat in ('standings','batting','pitching','fielding')]\n            raw=lambda cat,col:unit['raw_tables'].get(source+'_'+cat,{}).get(col)\n            if st:\n                equal('G=W+L+T',st['\u8a66\u5408'],st['\u52dd\u5229']+st['\u6557\u5317']+st['\u5f15\u5206'],ident+'/'+source)\n                # Historical winning-percentage rules varied: no unverified modern rule applied before 2005.\n                if key[0]>=2005:\n                    rate('winning_percentage',st['\u52dd\u5229'],st['\u52dd\u5229']+st['\u6557\u5317'],st['\u52dd\u7387'],3,ident+'/'+source,raw('standings','\u52dd\u7387'))\n            for cat,table in [('batting',bat),('pitching',pitch),('fielding',field)]:\n                if table and st:\n                    equal('G:'+cat,table['\u8a66\u5408'],st['\u8a66\u5408'],ident+'/'+source)\n            if pitch and st:\n                for col in ('\u52dd\u5229','\u6557\u5317'):\n                    equal('pitching:'+col,pitch[col],st[col],ident+'/'+source)\n            if bat:\n                rate('batting_average',bat['\u5b89\u6253'],bat['\u6253\u6570'],bat['\u6253\u7387'],3,ident+'/'+source,raw('batting','\u6253\u7387'))\n                tb=bat['\u5b89\u6253']+bat['\u4e8c\u5841\u6253']+2*bat['\u4e09\u5841\u6253']+3*bat['\u672c\u5841\u6253']\n                if '\u5841\u6253' in bat: equal('total_bases',bat['\u5841\u6253'],tb,ident+'/'+source)\n                if '\u9577\u6253\u7387' in bat: rate('slugging',tb,bat['\u6253\u6570'],bat['\u9577\u6253\u7387'],3,ident+'/'+source,raw('batting','\u9577\u6253\u7387'))\n                if '\u51fa\u5841\u7387' in bat:\n                    rate('onbase',bat['\u5b89\u6253']+bat['\u56db\u7403']+bat['\u6b7b\u7403'],bat['\u6253\u6570']+bat['\u56db\u7403']+bat['\u6b7b\u7403']+bat['\u72a0\u98db'],bat['\u51fa\u5841\u7387'],3,ident+'/'+source,raw('batting','\u51fa\u5841\u7387'))\n            if pitch and '\u81ea\u8cac\u70b9' in pitch:\n                rate('ERA',pitch['\u81ea\u8cac\u70b9']*27,pitch['\u6295\u7403\u56de\u30a2\u30a6\u30c8'],pitch['\u9632\u5fa1\u7387'],2,ident+'/'+source,raw('pitching','\u9632\u5fa1\u7387'))\n            if field:\n                equal('fielding_chances',field['\u5b88\u5099\u6a5f\u4f1a'],field['\u523a\u6bba']+field['\u88dc\u6bba']+field['\u5931\u7b56'],ident+'/'+source)\n                rate('fielding_percentage',field['\u523a\u6bba']+field['\u88dc\u6bba'],field['\u5b88\u5099\u6a5f\u4f1a'],field['\u5b88\u5099\u7387'],3,ident+'/'+source,raw('fielding','\u5b88\u5099\u7387'))\n            # The home/road and head-to-head columns are also observations, not discarded text.\n            if st and all(isinstance(st.get(c),dict) for c in ('\u30db\u30fc\u30e0','\u30ed\u30fc\u30c9')):\n                for col,label in [('W','\u52dd\u5229'),('L','\u6557\u5317'),('T','\u5f15\u5206')]:\n                    equal('home_road:'+col,st['\u30db\u30fc\u30e0'][col]+st['\u30ed\u30fc\u30c9'][col],st[label],ident+'/'+source)\n            inter=tables.get(source+'_interleague',{})\n            if inter:\n                equal('interleague:G=W+L+T',inter['\u8a66\u5408'],sum(inter[k] for k in ('\u52dd\u5229','\u6557\u5317','\u5f15\u5206')),ident+'/'+source)\n                rate('interleague:winning_percentage',inter['\u52dd\u5229'],inter['\u52dd\u5229']+inter['\u6557\u5317'],inter['\u52dd\u7387'],3,ident+'/'+source)\n                if isinstance(st.get('\u4ea4\u6d41\u6226'),dict):\n                    for col,label in [('W','\u52dd\u5229'),('L','\u6557\u5317'),('T','\u5f15\u5206')]:\n                        equal('interleague:season:'+col,inter[label],st['\u4ea4\u6d41\u6226'][col],ident+'/'+source)\n            for cat,table in [('standings',st),('interleague',inter)]:\n                opponents={h:v for h,v in table.items() if h in OPPONENTS and isinstance(v,dict)}\n                if not opponents:continue\n                for col,label in [('W','\u52dd\u5229'),('L','\u6557\u5317'),('T','\u5f15\u5206')]:\n                    total=sum(v[col] for v in opponents.values())\n                    if cat=='standings' and isinstance(table.get('\u4ea4\u6d41\u6226'),dict):total+=table['\u4ea4\u6d41\u6226'][col]\n                    equal('opponent_sum:'+cat+':'+col,total,table[label],ident+'/'+source)\n                for header,value in opponents.items():\n                    other=next((u for (y,lg,t),u in units.items() if y==key[0] and t==OPPONENTS[header]),None)\n                    own=next((h for h,t in OPPONENTS.items() if t==key[2]),None)\n                    reverse=other['tables'].get(source+'_'+cat,{}).get(own) if other else None\n                    for col,opposite in [('W','L'),('L','W'),('T','T')]:\n                        equal('opponent_reciprocal:'+cat+':'+col,value[col],reverse.get(opposite) if isinstance(reverse,dict) else None,ident+'/'+source+'/'+header)\n        for cat in ('standings','batting','pitching'):\n            a,b=tables.get('archive_'+cat,{}),tables.get('detail_'+cat,{})\n            for col in sorted(a.keys() & b.keys()):\n                # Literal source precision is preserved; IP outs has an exact integer counterpart.\n                if col=='\u6295\u7403\u56de':continue\n                if col in {'\u6253\u7387','\u9577\u6253\u7387','\u51fa\u5841\u7387','\u9632\u5fa1\u7387','\u52dd\u7387','\u5b88\u5099\u7387'}:\n                    base=2 if col=='\u9632\u5fa1\u7387' else 3\n                    raw_a=unit['raw_tables'].get('archive_'+cat,{}).get(col,str(a[col]))\n                    raw_b=unit['raw_tables'].get('detail_'+cat,{}).get(col,str(b[col]))\n                    da=max(base,len(''.join(str(raw_a).split()).partition('.')[2]))\n                    db=max(base,len(''.join(str(raw_b).split()).partition('.')[2]))\n                    precision=min(da,db)\n                    qa=Decimal(str(a[col])).quantize(Decimal(10)**-precision,rounding=ROUND_HALF_UP)\n                    qb=Decimal(str(b[col])).quantize(Decimal(10)**-precision,rounding=ROUND_HALF_UP)\n                    equal('cross_source:'+cat+':'+col,str(qa),str(qb),ident)\n                    checks[-1].update(common_precision=precision,raw_observed=raw_a,raw_expected=raw_b)\n                else:\n                    equal('cross_source:'+cat+':'+col,a[col],b[col],ident)\n            if cat=='pitching' and a and b and '\u81ea\u8cac\u70b9' in b:\n                rate('cross_source:ERA_from_detail_counts',b['\u81ea\u8cac\u70b9']*27,a['\u6295\u7403\u56de\u30a2\u30a6\u30c8'],a['\u9632\u5fa1\u7387'],2,ident,\n                     unit['raw_tables'].get('archive_pitching',{}).get('\u9632\u5fa1\u7387'))\n        chosen='detail' if 'detail_standings' in tables else 'archive'\n        st,bat,pitch=[tables.get(chosen+'_'+cat,{}) for cat in ('standings','batting','pitching')]\n        if st and bat and pitch:\n            unit.update(G=st['\u8a66\u5408'],W=st['\u52dd\u5229'],L=st['\u6557\u5317'],T=st['\u5f15\u5206'],RF=bat['\u5f97\u70b9'],RA=pitch['\u5931\u70b9'])\n            den=unit['RF']**1.83+unit['RA']**1.83\n            unit['pythag_fixed']=unit['RF']**1.83/den if den else None\n            unit['pythag_expected_wins']=(unit['W']+unit['L'])*unit['pythag_fixed'] if den else None\n    for year in years:\n        for source in ('archive','detail'):\n            keys=['standings','batting','pitching','fielding']\n            cats={cat:[r['values'] for r in records if r['season']==year and r['source_kind']==source and r['category']==cat] for cat in keys}\n            st,bat,pitch,field=[cats[c] for c in keys]\n            if st:\n                equal('global_W=L',sum(r['\u52dd\u5229'] for r in st),sum(r['\u6557\u5317'] for r in st),f'{year}/{source}')\n                equal('global_draw_even',sum(r['\u5f15\u5206'] for r in st)%2,0,f'{year}/{source}')\n            if bat and pitch:\n                equal('global_RF=RA',sum(r['\u5f97\u70b9'] for r in bat),sum(r['\u5931\u70b9'] for r in pitch),f'{year}/{source}')\n                for col in ('\u5b89\u6253','\u672c\u5841\u6253','\u56db\u7403','\u6b7b\u7403','\u4e09\u632f'):\n                    if all(col in r and r[col] is not None for r in bat+pitch):\n                        equal('global_bat=pitch:'+col,sum(r[col] for r in bat),sum(r[col] for r in pitch),f'{year}/{source}')\n            if field and pitch:\n                equal('global_outs',sum(r['\u523a\u6bba'] for r in field),sum(r['\u6295\u7403\u56de\u30a2\u30a6\u30c8'] for r in pitch),f'{year}/{source}')\n    for r in baseline:\n        u=units.get((r['season'],r['league'],r['team']))\n        if u:\n            for col in ('G','W','L','T','RF','RA'):\n                equal('existing_season:'+col,u.get(col),r[col],f\"{r['season']}/{r['league']}/{r['team']}\")\n    failures=[c for c in checks if not c['ok']]\n    return {'schema':'aoi-annual-audit/1','years':years,'team_seasons':len(units),\n            'checks':checks,'passed':len(checks)-len(failures),'failed':len(failures),'failures':failures,\n            'annual':list(units.values()),'comparison_policy':'integers exact; normal rate digits ROUND_HALF_UP; observed extended digits truncated to source precision; historical win-percentage rules not guessed'}\n\n\ndef audit_files(observations, expected_years, baseline=None):\n    \"\"\"Recompute the complete saved audit, including optional baseline evidence.\"\"\"\n    read=lambda path:[json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]\n    r=audit(read(observations),expected_years=expected_years,baseline=read(baseline) if baseline else [])\n    manifest=observations.with_suffix('.manifest.json')\n    extras=[]\n    if not manifest.exists():\n        extras.append(dict(check='source_manifest_present',unit=str(observations),observed=False,expected=True,ok=False))\n    else:\n        metadata=json.loads(manifest.read_text(encoding='utf-8'))\n        value=metadata.get('unknown')\n        extras.append(dict(check='source_unknown_zero',unit=str(observations),observed=value,expected=0,ok=type(value) is int and value==0))\n        digest=hashlib.sha256(observations.read_bytes()).hexdigest()\n        extras.append(dict(check='source_dataset_sha256',unit=str(observations),observed=digest,expected=metadata.get('sha256'),ok=digest==metadata.get('sha256')))\n        r['source_parser_sha256']=metadata.get('source_code_sha256')\n    for extra in extras:\n        r['checks'].append(extra)\n        if extra['ok']:r['passed']+=1\n        else:r['failed']+=1;r['failures'].append(extra)\n    r['source_sha256']=hashlib.sha256(observations.read_bytes()).hexdigest()\n    r['baseline_sha256']=hashlib.sha256(baseline.read_bytes()).hexdigest() if baseline else None\n    return r\n\n\ndef main():\n    p=argparse.ArgumentParser(description=__doc__)\n    p.add_argument('--observations',type=Path,required=True)\n    p.add_argument('--years',required=True)\n    p.add_argument('--baseline',type=Path)\n    p.add_argument('--out',type=Path,required=True)\n    p.add_argument('--annual-out',type=Path,required=True)\n    a=p.parse_args()\n    start,end=map(int,a.years.split('-'))\n    r=audit_files(a.observations,range(start,end+1),a.baseline)\n    for path in (a.out,a.annual_out):path.parent.mkdir(parents=True,exist_ok=True)\n    a.annual_out.write_text(''.join(json.dumps(s,ensure_ascii=False)+'\\n' for s in r.pop('annual')),encoding='utf-8')\n    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')\n    print(f\"annual audit: {r['team_seasons']} team-seasons, {r['passed']} passed, {r['failed']} failed\")\n    return int(bool(r['failed']))\n\n\nif __name__=='__main__':\n    raise SystemExit(main())\n",
    "neighbors": "\"\"\"Deterministic descriptive neighbors; no outcome-derived distance features.\"\"\"\nimport math\nimport statistics\n\nFEATURES = (\"rf_adv\", \"ra_adv\", \"vs_lower_wpct\")\n\n\ndef discover(rows, excluded=(), limit=20):\n    usable, skipped = [], []\n    for row in rows:\n        unit = f\"{row['team']}-{row['season']}\"\n        if row['season'] in excluded or row.get('rank_tie') or type(row.get('upper_half')) is not bool:\n            skipped.append(unit)\n            continue\n        if any(type(row.get(k)) not in (int, float) or not math.isfinite(row[k]) for k in FEATURES):\n            skipped.append(unit)\n            continue\n        usable.append(row)\n    scales = {k: statistics.pstdev([r[k] for r in usable]) if usable else 0 for k in FEATURES}\n    features = [k for k in FEATURES if scales[k] > 0]\n    pairs = {}\n    if features:\n        for left in usable:\n            options = []\n            for right in usable:\n                if left['league'] != right['league'] or left['upper_half'] == right['upper_half']:\n                    continue\n                ids = sorted([f\"{left['team']}-{left['season']}\", f\"{right['team']}-{right['season']}\"])\n                distance = math.sqrt(sum(((left[k]-right[k])/scales[k])**2 for k in features)/len(features))\n                options.append((distance, ids, right))\n            if options:\n                distance, ids, right = min(options, key=lambda x: (x[0], x[1]))\n                pairs[tuple(ids)] = {'units': ids, 'distance': distance,\n                    'values': {f\"{r['team']}-{r['season']}\": {k: r[k] for k in features} for r in (left, right)},\n                    'upper_half': {f\"{r['team']}-{r['season']}\": r['upper_half'] for r in (left, right)}}\n    return {'features': features, 'scales': scales, 'skipped': sorted(skipped),\n            'pairs': sorted(pairs.values(), key=lambda p: (p['distance'], p['units']))[:limit],\n            'method': '\u540c\u30ea\u30fc\u30b0\u30fbA/B\u304c\u7570\u306a\u308b\u6700\u8fd1\u508d\u3002\u5168\u5bfe\u8c61\u306e\u6a19\u6e96\u504f\u5dee\u3067\u6a19\u6e96\u5316\u3057\u305f\u8ddd\u96e2\u3002\u985e\u4f3c\u306e\u7d76\u5bfe\u57fa\u6e96\u30fb\u56e0\u679c\u5224\u5b9a\u3067\u306f\u306a\u3044\u3002\u76f8\u624b\u533a\u5206\u306f\u6700\u7d42\u9806\u4f4d\u306b\u4f9d\u5b58\u3002'}\n",
    "sakanalytics_api": "\"\"\"SakAnalytics min: exact annual table audits and descriptive neighbors.\"\"\"\nfrom _minpy_558097f6c30b18b6.annual_audit import audit as audit_annual\nfrom _minpy_558097f6c30b18b6.neighbors import FEATURES, discover\n\n__all__ = ['audit_annual', 'FEATURES', 'discover']\n",
}
_MINPY_SKIP = (
    "__builtins__",
    "__cached__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__path__",
    "__spec__",
)


def _minpy_original(fullname):
    if fullname == _MINPY_PREFIX:
        return ""
    prefix = _MINPY_PREFIX + "."
    if fullname.startswith(prefix):
        return fullname[len(prefix):]
    return None


class _MinpyLoader:
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        original = _minpy_original(module.__name__)
        if original is None:
            raise ImportError(module.__name__)
        if original == "":
            module.__path__ = []
            return
        source = _MINPY_SOURCES[original]
        filename = "minpy://" + original + ".py"
        module.__file__ = filename
        exec(compile(source, filename, "exec"), module.__dict__)


class _MinpyFinder:
    def __init__(self):
        self._minpy_sources = _MINPY_SOURCES

    def find_spec(self, fullname, path, target=None):
        original = _minpy_original(fullname)
        if original is None:
            return None
        if original == "":
            is_package = True
        elif original not in _MINPY_SOURCES:
            return None
        else:
            is_package = original in _MINPY_PACKAGES
        return importlib.machinery.ModuleSpec(
            fullname,
            _MinpyLoader(),
            origin="minpy://" + (original or _MINPY_PREFIX),
            is_package=is_package,
        )


def _minpy_install():
    for finder in sys.meta_path:
        if getattr(finder, "_minpy_sources", None) is _MINPY_SOURCES:
            return
    sys.meta_path.insert(0, _MinpyFinder())


def _minpy_run_entry_as_main():
    import types

    original = _MINPY_ENTRY
    full = _MINPY_PREFIX + "." + original
    module = types.ModuleType("__main__")
    origin = "minpy://" + original + ".py"
    module.__file__ = globals().get("__file__") or origin
    if original in _MINPY_PACKAGES:
        module.__package__ = full
        module.__path__ = []
    elif "." in original:
        module.__package__ = full.rpartition(".")[0]
    else:
        module.__package__ = _MINPY_PREFIX
    sys.modules["__main__"] = module
    sys.modules[full] = module
    exec(compile(_MINPY_SOURCES[original], origin, "exec"), module.__dict__)


def _minpy_export_entry(namespace):
    import importlib

    module = importlib.import_module(_MINPY_PREFIX + "." + _MINPY_ENTRY)
    for key, value in module.__dict__.items():
        if key not in _MINPY_SKIP:
            namespace[key] = value


_minpy_install()
if __name__ == "__main__":
    _minpy_run_entry_as_main()
else:
    _minpy_export_entry(globals())
