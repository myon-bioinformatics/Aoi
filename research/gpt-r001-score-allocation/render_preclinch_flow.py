"""DRAgoWing / Plotly Sankey views of pooled pre-clinch game counts."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from DRAgoWing.dragowing import render_report

LABELS={'lead':'リード','tie':'同点','trail':'ビハインド','unavailable':'切点対象外',
        'no_runs':'以後無得点','never_level':'得点・未到達','level_never_led':'同点のみ','led':'リード到達'}


def panel(title,groups,total):
    names=list(groups);labels=['対象 '+str(total)]+[LABELS[k]+' '+str(groups[k]['G']) for k in names]+['勝','敗','分']
    sources=[];targets=[];values=[];rows=[]
    for i,k in enumerate(names,1):
        r=groups[k];sources.append(0);targets.append(i);values.append(r['G'])
        for j,f in enumerate(('W','L','T'),len(names)+1):
            if r[f]:sources.append(i);targets.append(j);values.append(r[f])
        rows.append([LABELS[k],r['G'],total,f"{100*r['G']/total:.2f}" if total else '—',r['W'],r['L'],r['T']])
    return dict(title=title,note='線の幅は試合数。割合の分母は表に併記。',headers=['状態','試合','分母','%','勝','敗','分'],rows=rows,
                data=[dict(type='sankey',arrangement='snap',node=dict(label=labels,pad=20,thickness=14),
                           link=dict(source=sources,target=targets,value=values))],
                layout=dict(font=dict(size=11),margin=dict(l=5,r=5,t=10,b=10)))


def build(x):
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


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(render_report(build(json.loads(a.input.read_text()))))


if __name__=='__main__':main()
