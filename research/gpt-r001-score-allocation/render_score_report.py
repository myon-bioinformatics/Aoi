"""R001 の結果を DRAgoWing の研究レポート（dragowing.research_report）で 1 枚のページにする（4 種類）。

    python research/gpt-r001-score-allocation/render_score_report.py <処理> [その処理の引数]

処理: game_state, matched_comeback, preclinch_flow, score_report

1 つの処理が 1 つのサブコマンド（旧 render_game_state.py, render_matched_comeback.py, render_preclinch_flow.py … の 1 本が 1 つ）。引数と説明は各関数の説明（旧ファイルの冒頭）にある。
リポジトリの直下（dragowing/ を含む）を sys.path に足す。
ファイル名は旧 render_score_report.py のまま（DRAgoWing の検査 test_real_aggregate_mapping がこのファイルの build_spec を読む）。
同じ中身の補助は 1 つにし、処理ごとに中身が違う名前には処理の名前を付けた。旧ファイルの HERE・ROOT・sys.path の行は、この冒頭の 1 か所にまとめた。
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT)]

from dragowing.research_report import render_report  # noqa: E402


# ==== game_state（旧 render_game_state.py）

GAME_STATE_DOC = """DRAgoWing adapter: late-game state composition and wins by score margin."""


def game_state_build(x):
    bins=['-3+','-2','-1','0','1','2','3+']
    labels=['3点以上負け','2点負け','1点負け','同点','1点リード','2点リード','3点以上リード']
    colors=['#a84444','#d17464','#e6ac83','#9aa9b9','#85b6d0','#4089b2','#175b85']
    frames={}
    for r in x['comparisons']:
        if r['team']!='d' or r['venue']!='all' or r['period']=='with2020':continue
        year=r['period'];cut=r['cutoff'];names=['中日','他セ5（合算）'];sides=['own','peer']
        rows=[];traces=[]
        for b,label,color in zip(bins,labels,colors):
            vals=[r[s]['bins'][b] for s in sides]
            traces.append(dict(type='bar',name=label,x=names,y=[v['share']*100 for v in vals],marker=dict(color=color)))
            rows.extend([name,label,v['G'],r[s]['all']['G'],f"{v['share']*100:.2f}",v['W'],v['L'],v['T']] for name,s,v in zip(names,sides,vals))
        wins=[];winrows=[]
        for name,s,color in zip(names,sides,['#176197','#b75a2c']):
            vals=[r[s]['bins'][b] for b in bins]
            wins.append(dict(type='scatter',mode='markers',name=name,x=labels,y=[v['win_fraction']*100 if v['G'] else None for v in vals],marker=dict(size=10,color=color)))
            winrows.extend([name,label,v['W'],v['L'],v['T'],v['G'],f"{v['win_fraction']*100:.2f}" if v['G'] else '—'] for label,v in zip(labels,vals))
        frames[f'{year}|{cut}']=dict(caption=('2013–2025（2020除外）' if year=='no2020' else year+'年')+f' / {cut}回終了時'+('（2020は参考）' if year=='2020' else ''),panels=[
            dict(title='どの状態で終盤を迎えたか',note='分母は切点まで両軍が攻撃し、次回表がある全試合。',headers=['対象','状態','該当試合','全対象','割合 %','勝','敗','分'],rows=rows,data=traces,
                 layout=dict(barmode='stack',yaxis=dict(title=dict(text='全対象に占める割合 (%)'),range=[0,100]),legend=dict(orientation='h',y=-.25,font=dict(size=10)),margin=dict(l=55,r=15,t=15,b=130))),
            dict(title='その点差から最終的に勝った割合',note='W/G。引分を含む分母で、勝・敗・分を表に併記。少数例の100%を安定した能力差と読まない。',headers=['対象','状態','勝','敗','分','試合','W/G %'],rows=winrows,data=wins,
                 layout=dict(yaxis=dict(title=dict(text='W/G (%)'),range=[0,100]),xaxis=dict(tickangle=-45),margin=dict(l=55,r=15,t=15,b=130)))])
    return dict(title='中日はどの状態で終盤を迎えるか',intro='リード・同点・ビハインドの頻度と、その後の勝敗を分母付きで並べる。2019年を入口に全年度を比較。',
        notes='同年セ他5球団との合算比較。交流戦・引分を含み、以後の延長も含む。相手強度・投手起用は未調整。2020は参考。図の差は因果関係や有意差の判定ではない。',
        provenance='計画 '+x['plan_commit']+' / 入力SHA-256 '+x['input_sha256']+' / 保存集約 game_state.jsonをDRAgoWingで描画。',
        controls=[dict(id='period',label='期間',options=[dict(value='no2020',label='全期間（2020除外）')]+[dict(value=str(y),label=str(y)+('（参考）' if y==2020 else '')) for y in range(2013,2026)]),
                  dict(id='cutoff',label='切点',options=[dict(value=str(c),label=str(c)+'回') for c in (6,7)])],default='2019|7',frames=frames)


def game_state_main(argv=None):
    p=argparse.ArgumentParser(description=GAME_STATE_DOC);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(argv);a.output.write_text(render_report(game_state_build(json.loads(a.input.read_text()))))


def game_state(argv=None):
    """render_game_state.py の入口（説明は GAME_STATE_DOC）。
    """
    game_state_main(argv)


# ==== matched_comeback（旧 render_matched_comeback.py）

MATCHED_COMEBACK_DOC = """DRAgoWing adapter for fixed matched-comeback aggregates (Plotly, no recomputation)."""


def matched_comeback_build(result):
    frames={}
    labels={'level_or_better':'同点以上への到達','led':'リードへの到達','W':'最終勝利'}
    for cutoff in (6,7):
        rs=[r for r in result['yearly'] if r['team']=='d' and r['cutoff']==cutoff]
        for metric,label in labels.items():
            years=[r['period']+('*' if r['period']=='2020' else '') for r in rs]
            own=[100*r['metrics'][metric]['own_rate'] for r in rs]
            peer=[100*r['metrics'][metric]['peer_standardized_rate'] for r in rs]
            delta=[x-y for x,y in zip(own,peer)]
            table=[[y,r['common_own_G'],r['metrics'][metric]['own_count'],f'{o:.2f}',f'{p:.2f}',f'{d:+.2f}',r['unmatched_own_G']]
                   for y,r,o,p,d in zip(years,rs,own,peer,delta)]
            frames[f'{cutoff}|{metric}']=dict(caption=f'{cutoff}回終了時ビハインドからの{label}。2020年は参考表示。',panels=[
                dict(title=label+'の年別比較',note='同年度・同じ点差・同じ会場区分の他5球団の率を、中日の試合構成で重み付け。',
                     headers=['年','共通条件の試合数','中日該当数','中日 %','他5標準化 %','差 pt','比較不能数'],rows=table,
                     data=[dict(type='scatter',mode='markers',name='中日',x=years,y=own,marker=dict(size=10,color='#176197')),
                           dict(type='scatter',mode='markers',name='他セ5球団（標準化）',x=years,y=peer,marker=dict(size=10,symbol='diamond',color='#b75a2c'))],
                     layout=dict(yaxis=dict(title=dict(text='割合 (%)'),rangemode='tozero'),xaxis=dict(type='category'))),
                dict(title='中日 − 比較先：反例を探す',note='0以上の年は「中日の到達率が低い」という年別の表現への反例。差の符号は有意差の判定ではありません。',
                     headers=['年','差 (ポイント)'],rows=[[y,f'{d:+.2f}'] for y,d in zip(years,delta)],
                     data=[dict(type='bar',x=years,y=delta,marker=dict(color=['#23826b' if d>=0 else '#b55b54' for d in delta]))],
                     layout=dict(yaxis=dict(title=dict(text='差 (ポイント)'),zeroline=True),xaxis=dict(type='category'),showlegend=False))])
    return dict(title='同じ点差・会場からの終盤到達',
                intro='2013–2025年、中日と同年セ他5球団の比較。最終敗戦だけに限定せず、切点でビハインドの全対象試合を使用。',
                notes='次の回の表がある試合に限定。延長を含む。比較先がない層は標準化から除外し件数を表示。相手強度・投手交代は未調整。原因や能力差の確定には使わない。',
                provenance='計画commit '+result['plan_commit']+' / 入力SHA-256 '+result['input_sha256']+' / 出典 matched_comeback.json。図はPlotly.jsを取得して描画。数値表はオフラインでも利用可能。',
                default='7|level_or_better',controls=[dict(id='cutoff',label='切点',options=[dict(value=str(c),label=str(c)+'回終了') for c in (6,7)]),
                dict(id='metric',label='経過',options=[dict(value=k,label=v) for k,v in labels.items()])],frames=frames)


def matched_comeback_main(argv=None):
    p=argparse.ArgumentParser(description=MATCHED_COMEBACK_DOC)
    p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args(argv);a.output.write_text(render_report(matched_comeback_build(json.loads(a.input.read_text()))))


def matched_comeback(argv=None):
    """render_matched_comeback.py の入口（説明は MATCHED_COMEBACK_DOC）。
    """
    matched_comeback_main(argv)


# ==== preclinch_flow（旧 render_preclinch_flow.py）

PRECLINCH_FLOW_DOC = """DRAgoWing / Plotly Sankey views of pooled pre-clinch game counts."""

PRECLINCH_FLOW_LABELS={'lead':'リード','tie':'同点','trail':'ビハインド','unavailable':'切点対象外',
        'no_runs':'以後無得点','never_level':'得点・未到達','level_never_led':'同点のみ','led':'リード到達'}


def panel(title,groups,total):
    names=list(groups);labels=['対象 '+str(total)]+[PRECLINCH_FLOW_LABELS[k]+' '+str(groups[k]['G']) for k in names]+['勝','敗','分']
    sources=[];targets=[];values=[];rows=[]
    for i,k in enumerate(names,1):
        r=groups[k];sources.append(0);targets.append(i);values.append(r['G'])
        for j,f in enumerate(('W','L','T'),len(names)+1):
            if r[f]:sources.append(i);targets.append(j);values.append(r[f])
        rows.append([PRECLINCH_FLOW_LABELS[k],r['G'],total,f"{100*r['G']/total:.2f}" if total else '—',r['W'],r['L'],r['T']])
    return dict(title=title,note='線の幅は試合数。割合の分母は表に併記。',headers=['状態','試合','分母','%','勝','敗','分'],rows=rows,
                data=[dict(type='sankey',arrangement='snap',node=dict(label=labels,pad=20,thickness=14),
                           link=dict(source=sources,target=targets,value=values))],
                layout=dict(font=dict(size=11),margin=dict(l=5,r=5,t=10,b=10)))


def preclinch_flow_build(x):
    frames={}
    for r in x['comparisons']:
        for side,name in (('own','中日'),('peer','他セ5・球団試合合算')):
            a=r[side];period=r['period'];label={'no2020':'2013–2025・2020除外','with2020':'2013–2025・2020含む参考'}.get(period,period)
            frames[f'{period}|{r["cutoff"]}|{side}']=dict(caption=f'{label} / {name} / {r["cutoff"]}回終了',panels=[
                panel('確定日までの全試合 → 終盤の状態 → 最終勝敗',a['states'],a['total']['G']),
                panel('ビハインド → その後の到達状態 → 最終勝敗',a['trailing'],a['states']['trail']['G'])])
    return dict(title='確定するまでに、何が起きていたか',intro='各年の中日のA/B区分確定日当日までを合算。年別割合の平均ではなく、試合数を足した分子・分母。',
        notes='他セ5も同じ年の同じ日まで。球団試合単位なので対戦する両球団を別に数える。交流戦・引分・延長込み。切点対象外は当該回までの両軍攻撃か次回表がない試合。到達は各攻撃半回終了時の同点以上。2020はCS非開催の3位以内確定として参考。2026は残り日程未確認のため対象外。相手・点差・年構成は未調整で、因果効果や有意差を表さない。',
        provenance='計画 '+x['plan_commit']+' / 入力 SHA-256 '+x['input_sha256']+' / preclinch_dates.json + preclinch_flow.json',
        controls=[dict(id='period',label='期間',options=[dict(value='no2020',label='合算（2020除外）'),dict(value='with2020',label='合算（2020含む参考）')]+[dict(value=str(y),label=str(y)) for y in range(2013,2026)]),
                  dict(id='cutoff',label='切点',options=[dict(value=str(c),label=str(c)+'回') for c in (7,6)]),
                  dict(id='side',label='対象',options=[dict(value='own',label='中日'),dict(value='peer',label='他セ5')])],
        default='no2020|7|own',frames=frames)


def preclinch_flow_main(argv=None):
    p=argparse.ArgumentParser(description=PRECLINCH_FLOW_DOC);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(argv);a.output.write_text(render_report(preclinch_flow_build(json.loads(a.input.read_text()))))


def preclinch_flow(argv=None):
    """render_preclinch_flow.py の入口（説明は PRECLINCH_FLOW_DOC）。
    """
    preclinch_flow_main(argv)


# ==== score_report（旧 render_score_report.py）

SCORE_REPORT_DOC = """Map verified aggregate outputs to DRAgoWing; no raw observations included."""

COLORS = ['#1265a8', '#d58a2b']
NAMES = ['中日', '他セ5球団（合算）']
CATEGORIES = ['no_late_runs', 'scored_never_tied', 'tied_never_led', 'led_then_lost']
SCORE_REPORT_LABELS = ['以後無得点', '得点したが同点なし', '同点・リードなし', 'リード後に敗戦']


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
                counts.append((ns,g));table.extend([[NAMES[j],label,n,g,f'{n/g:.1%}' if g else '—'] for label,n in zip(SCORE_REPORT_LABELS,ns)])
            traces=[bar(label,NAMES,[ratio(ns[i],g) for ns,g in counts],color,[f'{ns[i]} / {g}試合' for ns,g in counts]) for i,(label,color) in enumerate(zip(SCORE_REPORT_LABELS,['#b9c6d4','#1265a8','#e6ad4c','#b75c56']))]
            panels.append(dict(title='負け試合の反撃は、どこまで届いたか',note=f'分母は「{cut}回終了時に負けていて、最終的にも敗戦」。延長を含む以後の攻撃終了時点で分類。得点しても同点に届かなかった割合であり、意図や原因の判定ではない。',data=traces,layout={'barmode':'stack','yaxis':{'tickformat':'.0%','range':[0,1]},'legend':{'orientation':'h','y':-.2,'font':{'size':11}}},headers=['対象','経過','該当試合','分母','割合'],rows=table))
            frames[f'{year}|{cut}']=dict(caption=f'{year}年 / {cut}回終了を切点'+(' — 2020年は参考（主解析除外）' if year==2020 else ''),panels=panels)
    return dict(title='中日の得点は、いつ生まれるか',intro='序盤から6・7回までの得点と、その後の反撃を、同年の他セ5球団と比べる。初期表示は2022年・7回終了。',notes='既存の検証済み集計を可視化。2020年は参考、2026年は対象外。他5球団は分子・分母を合算。先発交代は観測していないため、回の区切りを先発・救援の効果とは解釈しない。',controls=[dict(id='year',label='年',options=[dict(value=str(y),label=str(y)+('（参考）' if y==2020 else '')) for y in range(2013,2026)]),dict(id='cutoff',label='切点',options=[dict(value=str(c),label=f'{c}回終了') for c in [6,7]])],default='2022|7',frames=frames,provenance='')


def score_report_main(argv=None):
    parser=argparse.ArgumentParser(description=SCORE_REPORT_DOC)
    parser.add_argument('--inputs',type=Path,default=Path(__file__).parent/'outputs')
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'outputs'/'score_timing.html')
    args=parser.parse_args(argv)
    paths=[args.inputs/f'{name}.json' for name in ['early_scoring','late_reaction']]
    spec=build_spec(*(json.loads(p.read_text()) for p in paths))
    spec['provenance']=' | '.join(f'{p.name} SHA-256: {hashlib.sha256(p.read_bytes()).hexdigest()}' for p in paths)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(render_report(spec),encoding='utf-8')
    print(args.output)


def score_report(argv=None):
    """render_score_report.py の入口（説明は SCORE_REPORT_DOC）。
    """
    score_report_main(argv)


# ==== 入口
COMMANDS = {
    "game_state": game_state,
    "matched_comeback": matched_comeback,
    "preclinch_flow": preclinch_flow,
    "score_report": score_report,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="render_score_report.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"render_score_report.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
