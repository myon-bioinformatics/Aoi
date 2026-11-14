import json
from pathlib import Path
import accessible_names, emoji_observations, heading_observations
rows=[]
for p in sorted(Path('tests/cases/pages').glob('*.json')):
    data=json.loads(p.read_text())
    if 'html' not in data:
        raise RuntimeError(f'missing html in {p}')
    for m in (accessible_names,emoji_observations,heading_observations):
        rows.append({'input':str(p),'observer':m.__name__,'output':m.observe(data['html'],data.get('url'))})
print(json.dumps(rows,sort_keys=True,ensure_ascii=False,allow_nan=False))
