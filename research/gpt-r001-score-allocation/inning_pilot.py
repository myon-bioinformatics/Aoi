"""Three-game acquisition feasibility only, not a team-comparison sample."""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from selectolax.parser import HTMLParser
from analyze import sha

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'queryu'))
from queryu import Cache,PoliteFetcher,UA

NAMES={'中日':'d','東京ヤクルト':'s','巨人':'g','読売':'g','阪神':'t','広島':'c','広島東洋':'c','横浜DeNA':'db','DeNA':'db'}

def norm(s):
    return ''.join(unicodedata.normalize('NFKC',s).split())


def cell(raw,side,last):
    value=norm(raw)
    if value=='X':
        if side!='home' or not last:
            raise ValueError('unplayed cell at unexpected position')
        return dict(runs=None,played=False,completed=False)
    m=re.fullmatch(r'(\d+)([xX]?)',value)
    if not m or (m[2] and (side!='home' or not last)):
        raise ValueError(f'unknown inning cell: {raw!r}')
    return dict(runs=int(m[1]),played=True,completed=not bool(m[2]))


def parse(html,g):
    root=HTMLParser(html)
    candidates=[r for r in root.css('#gmdivresult tr') if r.css_first('.gmscoreteam')]
    if len(candidates)!=2:
        raise ValueError('expected exactly two score rows')
    result=[]
    for row,side,totalkey in zip(candidates,['away','home'],['as','hs']):
        name=norm(row.css_first('.gmscoreteam').text())
        if NAMES.get(name)!=g[side]:
            raise ValueError(f'team identity mismatch: {name}')
        vals=[norm(c.text()) for c in row.css('td.gmscore')]
        if len(vals)!=13 or vals[9]!='-':
            raise ValueError('pilot supports exactly nine innings and R/H/E columns')
        parsed=[cell(v,side,i==8) for i,v in enumerate(vals[:9])]
        if not vals[10].isdigit() or sum(c['runs'] or 0 for c in parsed)!=int(vals[10]) or int(vals[10])!=g[totalkey]:
            raise ValueError('inning total does not match verified final score')
        result.append(dict(team=g[side],side=side,cells=parsed))
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--fetch',action='store_true');args=ap.parse_args()
    data=ROOT/'data/observations/r001/games.jsonl'
    expected='7b1b6dfdd41cafbdf851cdb8bcd2cae981adb338570dd66de75881bfe35ee8d9'
    if sha(data)!=expected:
        raise ValueError('pilot source dataset changed')
    games=[json.loads(s) for s in data.read_text().splitlines()]
    selected=[g for g in games if g['date']=='2024-03-29' and g['home'] in {'g','s','db'}]
    if len(selected)!=3:
        raise ValueError('pilot selection changed')
    cache=Cache(ROOT/'data/raw/r001_inning_pilot')
    if args.fetch:
        import httpx
        with httpx.Client(headers={'User-Agent':UA},timeout=45,follow_redirects=True) as client:
            fetch=PoliteFetcher(cache,wait=3,client=client)
            for g in selected:
                fetch.get(g['key'],g['href'],'2024')
    latest=cache.latest();rows=[];receipts=[];unknown=[]
    for g in selected:
        e=latest[g['key']];html=cache.body(e)
        if e['status']!=200 or hashlib.sha256(html.encode()).hexdigest()!=e['sha256']:
            raise ValueError('cached response mismatch')
        try:
            rows.extend(dict(game=g['key'],**r) for r in parse(html,g))
        except ValueError as err:
            unknown.append(dict(game=g['key'],error=str(err)))
        receipts.append({k:e[k] for k in ['key','url','status','sha256','bytes','fetched_at','code_version']})
    local=ROOT/'data/observations/r001_inning_pilot';local.mkdir(parents=True,exist_ok=True)
    (local/'unknown.json').write_text(json.dumps(unknown,ensure_ascii=False,indent=2)+'\n')
    if unknown:
        raise ValueError('unknown records saved; pilot stopped')
    (local/'innings.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    played=[c for r in rows for c in r['cells'] if c['played']]
    result=dict(purpose='format feasibility only; no team trend inference',games=len(selected),team_games=len(rows),
                played_half_innings=len(played),unplayed_cells=sum(not c['played'] for r in rows for c in r['cells']),
                incomplete_played_cells=sum(not c['completed'] for c in played),unknown=0,all_final_scores_match=True,
                sources=receipts,input_sha256=expected,script_sha256=sha(__file__),
                protocol_sha256=sha(HERE/'SCORING_SPREAD_PROTOCOL.md'),exit_code=0)
    (HERE/'outputs/inning_pilot_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='sources'},ensure_ascii=False))

if __name__=='__main__':
    try:
        main()
    except (FileNotFoundError,KeyError) as e:
        print(str(e),file=sys.stderr);sys.exit(66)
    except ValueError as e:
        print(str(e),file=sys.stderr);sys.exit(65)
