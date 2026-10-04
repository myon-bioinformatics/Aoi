"""DRAgoWing: render aggregate Plotly figures, without doing research statistics."""
import html
import json

PLOTLY_URL = 'https://cdn.plot.ly/plotly-3.6.0.min.js'


def render_report(spec):
    """Return a portable HTML report. Spec contains options and keyed figure frames."""
    if not spec['frames'] or spec['default'] not in spec['frames']:
        raise ValueError('Missing default frame')
    payload = json.dumps(spec, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return TEMPLATE.replace('@@TITLE@@', html.escape(spec['title'])).replace('@@URL@@', PLOTLY_URL).replace('@@DATA@@', payload)


TEMPLATE = '''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#182b43;font:16px/1.65 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:32px 20px}h1{font-size:clamp(25px,4vw,38px);line-height:1.3}h2{font-size:20px}.eyebrow{color:#1669a5;font-weight:750;letter-spacing:.12em}.controls{display:flex;gap:24px;flex-wrap:wrap;padding:18px 0}select{font:inherit;padding:8px;border:1px solid #8193a9;border-radius:6px;background:white}section{background:white;padding:20px;margin:22px 0;border:1px solid #dce4ed;border-radius:12px}.plot{height:390px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:right;border-bottom:1px solid #ddd;padding:7px}th:first-child,td:first-child{text-align:left}.scroll{overflow-x:auto}details{margin-top:14px}summary{cursor:pointer;color:#176197}footer{font-size:13px;overflow-wrap:anywhere}.notice{border-left:4px solid #c08125;padding:10px 15px;background:#fff6e6}#status{font-weight:650}@media(max-width:600px){main{padding:20px 10px}section{padding:12px}.plot{height:380px}}
</style>
<main><div class="eyebrow">AOI / DRAgoWing</div><h1>@@TITLE@@</h1><p id="intro"></p><div class="controls" id="controls"></div><p id="status" aria-live="polite"></p><div class="notice" id="notes"></div><div id="panels"></div><footer id="provenance"></footer></main>
<script id="report-data" type="application/json">@@DATA@@</script>
<script src="@@URL@@"></script>
<script>
const spec=JSON.parse(document.getElementById('report-data').textContent);
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};
document.getElementById('intro').textContent=spec.intro;
document.getElementById('notes').textContent=spec.notes;
document.getElementById('provenance').textContent=spec.provenance;
const choices=[];
spec.controls.forEach((c,i)=>{const label=el('label',c.label+' '),s=el('select');s.id=c.id;c.options.forEach(o=>{const opt=el('option',o.label);opt.value=o.value;s.append(opt)});s.value=spec.default.split('|')[i];s.addEventListener('change',draw);label.append(s);document.getElementById('controls').append(label);choices.push(s)});
let generation=0;
async function draw(){
 const current=++generation;
 const key=choices.map(s=>s.value).join('|'),frame=spec.frames[key];
 document.getElementById('status').textContent=frame.caption;
 const host=document.getElementById('panels');host.querySelectorAll('.plot').forEach(p=>{if(window.Plotly)Plotly.purge(p)});host.replaceChildren();
 for(const p of frame.panels){if(current!==generation)return;const sec=el('section');sec.append(el('h2',p.title),el('p',p.note));const plot=el('div');plot.className='plot';sec.append(plot);
 const details=el('details'),summary=el('summary','数値と分母を表示');details.append(summary);const sc=el('div');sc.className='scroll';const table=el('table'),head=el('thead'),hr=el('tr');p.headers.forEach(h=>hr.append(el('th',h)));head.append(hr);table.append(head);const body=el('tbody');p.rows.forEach(r=>{const tr=el('tr');r.forEach(v=>tr.append(el('td',v)));body.append(tr)});table.append(body);sc.append(table);details.append(sc);sec.append(details);host.append(sec);
 if(window.Plotly){await Plotly.newPlot(plot,p.data,{font:{family:'system-ui,sans-serif',color:'#182b43'},margin:{l:60,r:20,t:20,b:85},legend:{orientation:'h',y:-.20},paper_bgcolor:'white',plot_bgcolor:'white',...p.layout},{responsive:true,displaylogo:false});}else{plot.textContent='グラフを読み込めません。インターネット接続を確認してください。数値表は利用できます。';plot.style.height='auto'}
 }if(current===generation)window.reportReady=key;
}
draw();
</script></html>'''
