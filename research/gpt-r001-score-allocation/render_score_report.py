"""Map verified aggregate outputs to DRAgoWing; no raw observations included."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'dragowing'))
from dragowing import render_report

COLORS = ['#1265a8', '#d58a2b']
NAMES = ['中日', '他セ5球団（合算）']
CATEGORIES = ['no_late_runs', 'scored_never_tied', 'tied_never_led', 'led_then_lost']
LABELS = ['以後無得点', '得点したが同点なし', '同点・リードなし', 'リード後に敗戦']


def ratio(n, d):
    return n / d if d else None


def bar(name, x, y, color, counts):
    return dict(type='bar', name=name, x=x, y=y, marker={'color': color}, customdata=counts,
                hovertemplate='%{x}<br>%{y:.3f}<br>%{customdata}<extra>%{fullData.name}</extra>')


def build_spec(early, late):
    er = {(r['year'], r['team']): r for r in early['rows']}
    lr = {(r['year'], r['team']): r for r in late['rows']}
    expected = {(y, t) for y in range(2013, 2026) for t in ['d','c','db','g','s','t','b','e','f','h','l','m']}
    if set(er) != expected or set(lr) != expected or len(early['rows']) != 156 or len(late['rows']) != 156:
        raise ValueError('Expected unique 156 team-years')
    if early['input_sha256'] != late['input_sha256']:
        raise ValueError('Different source inputs')
    columns = late['columns']
    def pool(rows):
        return {k: sum(a[i] for a in rows) for i,k in enumerate(columns)}
    frames = {}
    for year in range(2013, 2026):
        for cut in ['6','7']:
            peers = ['c','db','g','s','t']
            groups = [['d'], peers]
            panels=[]
            traces=[]; table=[]
            for j,teams in enumerate(groups):
                values=[]; denominators=[]
                for y in range(2013,2026):
                    a=[er[y,t]['windows'][cut]['by_venue']['all'] for t in teams]
                    g=sum(v['G'] for v in a); rf=sum(v['RF'] for v in a)
                    values.append(ratio(rf,g));denominators.append(f'{rf}点 / {g}球団試合')
                    table.append([y,NAMES[j],rf,g,f'{rf/g:.3f}','参考（主解析除外）' if y==2020 else '主解析'])
                traces.append(dict(type='scatter',mode='lines+markers',name=NAMES[j],x=list(range(2013,2026)),y=[v if y!=2020 else None for y,v in zip(range(2013,2026),values)],line={'color':COLORS[j]},customdata=denominators,hovertemplate='%{x}年: %{y:.3f}<br>%{customdata}<extra>%{fullData.name}</extra>'))
                traces.append(dict(type='scatter',mode='markers',name=NAMES[j]+' 2020参考',x=[2020],y=[values[7]],marker={'symbol':'circle-open','size':11,'color':COLORS[j]},showlegend=False))
            panels.append(dict(title=f'1–{cut}回の平均得点：年ごとの比較',note='2020年は白抜きの参考値。線を接続せず主解析から除外。',data=traces,layout={'yaxis':{'title':{'text':'点 / 試合'},'rangemode':'tozero'},'xaxis':{'dtick':2}},headers=['年','対象','得点','試合','点/試合','扱い'],rows=table))
            traces=[];table=[];buckets=['0','1','2','3','4','5+']
            for j,teams in enumerate(groups):
                a=[er[year,t]['windows'][cut]['by_venue']['all'] for t in teams];g=sum(v['G'] for v in a)
                ns=[sum(v['buckets'][b] for v in a) for b in buckets]
                if sum(ns)!=g: raise ValueError('Histogram denominator mismatch')
                traces.append(bar(NAMES[j],buckets,[n/g for n in ns],COLORS[j],[f'{n} / {g}試合' for n in ns]))
                table.extend([[NAMES[j],b,n,g,f'{n/g:.1%}'] for b,n in zip(buckets,ns)])
            panels.append(dict(title=f'1–{cut}回に何点取ったか',note='同じ切点まで両チームが実際に攻撃した試合。未実施回を0点で補わない。',data=traces,layout={'barmode':'group','yaxis':{'tickformat':'.0%','title':{'text':'対象試合に占める割合'}},'xaxis':{'type':'category','title':{'text':'得点'}}},headers=['対象','得点','該当試合','分母','割合'],rows=table))
            traces=[];table=[];window='7–9' if cut=='6' else '8–9'
            for j,teams in enumerate(groups):
                vals=[pool([lr[year,t]['cutoffs'][cut]['by_venue']['all']['by_outcome'][o] for t in teams]) for o in ['W','L','T']]
                traces.append(bar(NAMES[j],['勝ち','負け','引分'],[ratio(v['reg_RF'],v['G']) for v in vals],COLORS[j],[f"{v['reg_RF']}点 / {v['G']}試合" for v in vals]))
                for o,v in zip(['勝ち','負け','引分'],vals):
                    table.append([NAMES[j],o,v['G'],v['reg_RF'],v['reg_off_innings'],f"{v['reg_RF']/v['G']:.3f}" if v['G'] else '—',f"{v['reg_RF']/v['reg_off_innings']:.3f}" if v['reg_off_innings'] else '—',v['extra_RF']])
            panels.append(dict(title=f'{window}回の得点：最終勝敗別',note='勝敗を知った後の記述比較。ホームの9回裏省略など攻撃機会が違うため、実攻撃回数と回あたり得点も表に併記。延長得点は別欄。',data=traces,layout={'barmode':'group','yaxis':{'title':{'text':'点 / 試合'},'rangemode':'tozero'}},headers=['対象','勝敗','試合','終盤得点','実攻撃回','点/試合','点/回','延長得点'],rows=table))
            counts=[];table=[]
            for j,teams in enumerate(groups):
                ns=[sum(lr[year,t]['cutoffs'][cut]['by_venue']['all']['losing_comeback']['all'][c][0] for t in teams) for c in CATEGORIES]
                g=sum(ns);cross=pool([lr[year,t]['cutoffs'][cut]['by_venue']['all']['cross']['trail|L'] for t in teams])
                if g!=cross['G']:raise ValueError('Comeback denominator mismatch')
                counts.append((ns,g));table.extend([[NAMES[j],label,n,g,f'{n/g:.1%}' if g else '—'] for label,n in zip(LABELS,ns)])
            traces=[bar(label,NAMES,[ratio(ns[i],g) for ns,g in counts],color,[f'{ns[i]} / {g}試合' for ns,g in counts]) for i,(label,color) in enumerate(zip(LABELS,['#b9c6d4','#1265a8','#e6ad4c','#b75c56']))]
            panels.append(dict(title='負け試合の反撃は、どこまで届いたか',note=f'分母は「{cut}回終了時に負けていて、最終的にも敗戦」。延長を含む以後の攻撃終了時点で分類。得点しても同点に届かなかった割合であり、意図や原因の判定ではない。',data=traces,layout={'barmode':'stack','yaxis':{'tickformat':'.0%','range':[0,1]},'legend':{'orientation':'h','y':-.2,'font':{'size':11}}},headers=['対象','経過','該当試合','分母','割合'],rows=table))
            frames[f'{year}|{cut}']=dict(caption=f'{year}年 / {cut}回終了を切点'+(' — 2020年は参考（主解析除外）' if year==2020 else ''),panels=panels)
    return dict(title='中日の得点は、いつ生まれるか',intro='序盤から6・7回までの得点と、その後の反撃を、同年の他セ5球団と比べる。初期表示は2022年・7回終了。',notes='既存の検証済み集計を可視化。2020年は参考、2026年は対象外。他5球団は分子・分母を合算。先発交代は観測していないため、回の区切りを先発・救援の効果とは解釈しない。',controls=[dict(id='year',label='年',options=[dict(value=str(y),label=str(y)+('（参考）' if y==2020 else '')) for y in range(2013,2026)]),dict(id='cutoff',label='切点',options=[dict(value=str(c),label=f'{c}回終了') for c in [6,7]])],default='2022|7',frames=frames,provenance='')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=Path(__file__).parent/'outputs')
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'outputs'/'score_timing.html')
    args=parser.parse_args()
    paths=[args.inputs/f'{name}.json' for name in ['early_scoring','late_reaction']]
    spec=build_spec(*(json.loads(p.read_text()) for p in paths))
    spec['provenance']=' | '.join(f'{p.name} SHA-256: {hashlib.sha256(p.read_bytes()).hexdigest()}' for p in paths)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(render_report(spec),encoding='utf-8')
    print(args.output)


if __name__=='__main__':main()
