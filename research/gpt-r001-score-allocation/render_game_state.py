"""DRAgoWing adapter: late-game state composition and wins by score margin."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from DRAgoWing.dragowing import render_report


def build(x):
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


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(render_report(build(json.loads(a.input.read_text()))))


if __name__=='__main__':main()
