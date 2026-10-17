import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
ap=argparse.ArgumentParser(description='Independent grouped prediction verification; requires numpy and pandas')
ap.add_argument('--season',type=Path,required=True)
ap.add_argument('--result',type=Path,required=True)
args=ap.parse_args()
z=json.loads(args.result.read_text())
s=pd.read_json(args.season,lines=True)
s=s[s.season>=2013].copy()
s['rps']=s.inn_R/s.inn_S
fields={'zero':[], 'mean':[], 'iso':['iso'], 'obp':['obp'], 'both':['iso','obp']}
def independent_normalize(df):
 d=df.copy();g=d.groupby(['season','league']);n=g.team.transform('size')
 d['iso']=d.bat_iso-(g.bat_iso.transform('sum')-d.bat_iso)/(n-1)
 d['obp']=d.bat_obp-(g.bat_obp.transform('sum')-d.bat_obp)/(n-1)
 d['y']=np.log(d.rps/(g.inn_R.transform('sum')/g.inn_S.transform('sum')))
 return d
maxdiff=0
checks=0
for scope,modes in z['results'].items():
 source=s[s.season!=2020] if scope=='without2020' else s
 tests=independent_normalize(source)
 for mode,result in modes.items():
  cache={}
  for pred in result['predictions']:
   year,team=pred['year'],pred['team']
   key=(year,) if mode=='year' else (team,) if mode=='team' else (year,team)
   if key not in cache:
    mask=np.ones(len(source),dtype=bool)
    if mode!='team':mask &= source.season.to_numpy()!=year
    if mode!='year':mask &= source.team.to_numpy()!=team
    train=independent_normalize(source.loc[mask])
    cache[key]={}
    for model,f in fields.items():
     x=np.column_stack([np.ones(len(train)),*[train[k].to_numpy() for k in f]])
     cache[key][model]=np.array([0.]) if model=='zero' else np.linalg.lstsq(x,train.y.to_numpy(),rcond=None)[0]
   row=tests[(tests.season==year)&(tests.team==team)].iloc[0]
   assert abs(row.y-pred['actual'])<1e-12
   for model,f in fields.items():
    estimate=np.array([1.,*[row[k] for k in f]])@cache[key][model]
    diff=abs(estimate-pred['predictions'][model]);maxdiff=max(maxdiff,diff);checks+=1
    assert diff<1e-12
print('Independent pandas reference transforms + NumPy lstsq:',checks,'predictions agree; max abs diff',maxdiff)
