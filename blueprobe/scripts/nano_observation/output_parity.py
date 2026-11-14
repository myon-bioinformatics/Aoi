import json
from pathlib import Path
from blueprobe import names, emoji, headings
rows=[]
for p in sorted(Path('tests/cases/pages').glob('*.json')):
    data=json.loads(p.read_text())
    if 'html' not in data:
        raise RuntimeError(f'missing html in {p}')
    for label, m in (("accessible_names", names), ("emoji_observations", emoji), ("heading_observations", headings)):
        rows.append({'input':str(p),'observer':label,'output':m.observe(data['html'],data.get('url'))})
print(json.dumps(rows,sort_keys=True,ensure_ascii=False,allow_nan=False))
