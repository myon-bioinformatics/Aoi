"""DRAgoWing adapter for fixed matched-comeback aggregates (Plotly, no recomputation)."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from DRAgoWing.dragowing import render_report


def build(result):
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


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();a.output.write_text(render_report(build(json.loads(a.input.read_text()))))


if __name__=='__main__':main()
