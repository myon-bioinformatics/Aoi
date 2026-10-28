#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: 334b7f5fd49e0547f97079a37668637b2ad78276
# entry: distributions/entries/dragowing_api.py
# entry-module: dragowing_api
# search-paths: distributions/entries,dragowing
# allow: 
# allow-cycles: no
# cycles: 
# modules: dragowing_api,plot_specs,records,research_report
# prefix: _minpy_4e8031d4a916fe91
# content-sha256: 4d277372d74521c41166a1029dd0d873dd558971313aa912b3bf0b48a5214190
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_4e8031d4a916fe91"
_MINPY_ENTRY = "dragowing_api"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "dragowing_api": "\"\"\"DRAgoWing min: figure specifications, aggregate HTML reports and JSONL records.\n\nPlotly.js remains a browser runtime dependency of rendered reports, outside Python.\n\"\"\"\nfrom _minpy_4e8031d4a916fe91.plot_specs import series_figure, matrix_figure\nfrom _minpy_4e8031d4a916fe91.records import read_jsonl\nfrom _minpy_4e8031d4a916fe91.research_report import render_report\n\n__all__ = ['series_figure', 'matrix_figure', 'read_jsonl', 'render_report']\n",
    "plot_specs": "\"\"\"Small domain-neutral Plotly specifications; preserve order and missing points.\"\"\"\nfrom copy import deepcopy\nimport json\n\n\ndef series_figure(x, y, *, name='', title='', x_title='', y_title='', mode='lines+markers'):\n    x, y = list(x), list(y)\n    if len(x) != len(y):\n        raise ValueError('aligned x and y required')\n    if mode not in ('lines', 'markers', 'lines+markers'):\n        raise ValueError('unsupported mode')\n    spec = {'data': [{'type': 'scatter', 'x': deepcopy(x), 'y': deepcopy(y),\n                      'name': name, 'mode': mode, 'connectgaps': False}],\n            'layout': {'template': {}, 'title': {'text': title},\n                       'xaxis': {'title': {'text': x_title}},\n                       'yaxis': {'title': {'text': y_title}}}}\n    json.dumps(spec, allow_nan=False)\n    return spec\n\n\ndef matrix_figure(x, y, z, *, title='', x_title='', y_title=''):\n    x, y, z = list(x), list(y), [list(row) for row in z]\n    if len(z) != len(y) or any(len(row) != len(x) for row in z):\n        raise ValueError('matrix shape must match axis labels')\n    spec = {'data': [{'type': 'heatmap', 'x': deepcopy(x), 'y': deepcopy(y),\n                      'z': deepcopy(z), 'zsmooth': False, 'hoverongaps': False}],\n            'layout': {'template': {}, 'title': {'text': title},\n                       'xaxis': {'type': 'category', 'title': {'text': x_title}},\n                       'yaxis': {'type': 'category', 'categoryorder': 'array',\n                                 'categoryarray': deepcopy(y), 'title': {'text': y_title}}}}\n    json.dumps(spec, allow_nan=False)\n    return spec\n",
    "records": "\"\"\"\u7d50\u679c\u30c7\u30a3\u30ec\u30af\u30c8\u30ea\u306e JSONL \u3092\u3001\u8a18\u9332\u306e\u9806\u306e\u307e\u307e\u8aad\u3080\u3002\"\"\"\nfrom __future__ import annotations\n\nimport json\nfrom pathlib import Path\n\n\ndef read_jsonl(path: Path) -> list[dict]:\n    path = Path(path)\n    if not path.is_file():\n        raise FileNotFoundError(f\"\u7d50\u679c\u304c\u8aad\u3081\u306a\u3044: {path.name}\")\n    rows = []\n    for line in path.read_text(encoding=\"utf-8\").splitlines():\n        if line.strip():\n            rows.append(json.loads(line))\n    return rows\n\n\ndef select_items(items: list[dict], present: dict[str, bool], ids: list[str] | None) -> list[dict]:\n    \"\"\"--id \u306e\u9806\u3002\u5f0f ID \u3067 sets.jsonl \u304c\u7121\u3044\u3068\u304d\u306f\u3001\u7d50\u679c\u306b\u7121\u3044\u3068\u306f\u66f8\u304b\u306a\u3044\u3002\"\"\"\n    if not ids:\n        return list(items)\n    chosen = []\n    for ident in ids:\n        needed = \"sets.jsonl\" if ident.startswith(\"E\") else \"propositions.jsonl\" if ident.startswith(\"P\") else None\n        if needed and not present.get(needed):\n            raise FileNotFoundError(f\"\u7d50\u679c\u304c\u8aad\u3081\u306a\u3044: {needed}\")\n        hit = [item for item in items if item.get(\"id\") == ident]\n        if not hit:\n            raise ValueError(f\"{ident} \u306f\u5224\u5b9a\u6e08\u307f\u306e\u7d50\u679c\u306b\u306a\u3044\")\n        chosen.extend(hit)\n    return chosen\n",
    "research_report": "\"\"\"DRAgoWing: render aggregate Plotly figures, without doing research statistics.\n\n#48 \u3067\u6d88\u3048\u305f `DRAgoWing/dragowing.py` \u306e\u4e2d\u8eab\u3092\u305d\u306e\u307e\u307e\u623b\u3057\u305f\u3082\u306e\uff08render_report\uff09\u3002\n\u4eca\u306e `dragowing/` \u306f `dragowing.export` \u306a\u3069\u3092\u6301\u3064\u30d1\u30c3\u30b1\u30fc\u30b8\u306a\u306e\u3067\u3001`dragowing/dragowing.py` \u3068\u3044\u3046\u540d\u524d\u306b\u623b\u3059\u3068\n`dragowing` \u306e import \u304c\u3053\u306e\u30d5\u30a1\u30a4\u30eb\u306b\u53d6\u3089\u308c\u3066\u3001\u30d1\u30c3\u30b1\u30fc\u30b8\u5074\uff08chrome_pipe\u30fbexport\u30fbplotly_cdn\uff09\u304c\u8aad\u3081\u306a\u304f\u306a\u308b\u3002\n\u305d\u306e\u305f\u3081 `dragowing.research_report` \u306b\u3057\u305f\u3002\u4f7f\u3046\u5074: `dragowing/reports/research.py`\u3001\n`research/gpt-r001-score-allocation/render_*.py`\u3001`research_loop/feedback.py`\uff08research.build \u7d4c\u7531\uff09\u3002\nPlotly.js \u306e URL\uff083.6.0\u3001SRI \u306a\u3057\uff09\u306f\u5f53\u6642\u306e\u307e\u307e\u3002web-ui \u306e\u56fa\u5b9a\uff08plotly_cdn\uff09\u306b\u5bc4\u305b\u308b\u304b\u306f\u5225\u306b\u6c7a\u3081\u308b\u3002\n\"\"\"\nimport html\nimport json\n\nPLOTLY_URL = 'https://cdn.plot.ly/plotly-3.6.0.min.js'\n\n\ndef render_report(spec):\n    \"\"\"Return a portable HTML report. Spec contains options and keyed figure frames.\"\"\"\n    if not spec['frames'] or spec['default'] not in spec['frames']:\n        raise ValueError('Missing default frame')\n    payload = json.dumps(spec, ensure_ascii=False, allow_nan=False).replace('<', '\\\\u003c').replace('>', '\\\\u003e').replace('&', '\\\\u0026')\n    return TEMPLATE.replace('@@TITLE@@', html.escape(spec['title'])).replace('@@URL@@', PLOTLY_URL).replace('@@DATA@@', payload)\n\n\nTEMPLATE = '''<!doctype html>\n<html lang=\"ja\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>@@TITLE@@</title>\n<style>\n*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#182b43;font:16px/1.65 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:32px 20px}h1{font-size:clamp(25px,4vw,38px);line-height:1.3}h2{font-size:20px}.eyebrow{color:#1669a5;font-weight:750;letter-spacing:.12em}.controls{display:flex;gap:24px;flex-wrap:wrap;padding:18px 0}select{font:inherit;padding:8px;border:1px solid #8193a9;border-radius:6px;background:white}section{background:white;padding:20px;margin:22px 0;border:1px solid #dce4ed;border-radius:12px}.plot{height:390px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:right;border-bottom:1px solid #ddd;padding:7px}th:first-child,td:first-child{text-align:left}.scroll{overflow-x:auto}details{margin-top:14px}summary{cursor:pointer;color:#176197}footer{font-size:13px;overflow-wrap:anywhere}.notice{border-left:4px solid #c08125;padding:10px 15px;background:#fff6e6}#status{font-weight:650}@media(max-width:600px){main{padding:20px 10px}section{padding:12px}.plot{height:380px}}\n</style>\n<main><div class=\"eyebrow\">AOI / DRAgoWing</div><h1>@@TITLE@@</h1><p id=\"intro\"></p><div class=\"controls\" id=\"controls\"></div><p id=\"status\" aria-live=\"polite\"></p><div class=\"notice\" id=\"notes\"></div><div id=\"panels\"></div><footer id=\"provenance\"></footer></main>\n<script id=\"report-data\" type=\"application/json\">@@DATA@@</script>\n<script src=\"@@URL@@\"></script>\n<script>\nconst spec=JSON.parse(document.getElementById('report-data').textContent);\nconst el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n};\ndocument.getElementById('intro').textContent=spec.intro;\ndocument.getElementById('notes').textContent=spec.notes;\ndocument.getElementById('provenance').textContent=spec.provenance;\nconst choices=[];\nspec.controls.forEach((c,i)=>{const label=el('label',c.label+' '),s=el('select');s.id=c.id;c.options.forEach(o=>{const opt=el('option',o.label);opt.value=o.value;s.append(opt)});s.value=spec.default.split('|')[i];s.addEventListener('change',draw);label.append(s);document.getElementById('controls').append(label);choices.push(s)});\nlet generation=0;\nasync function draw(){\n const current=++generation;\n const key=choices.map(s=>s.value).join('|'),frame=spec.frames[key];\n document.getElementById('status').textContent=frame.caption;\n const host=document.getElementById('panels');host.querySelectorAll('.plot').forEach(p=>{if(window.Plotly)Plotly.purge(p)});host.replaceChildren();\n for(const p of frame.panels){if(current!==generation)return;const sec=el('section');sec.append(el('h2',p.title),el('p',p.note));const plot=el('div');plot.className='plot';sec.append(plot);\n const details=el('details'),summary=el('summary','\u6570\u5024\u3068\u5206\u6bcd\u3092\u8868\u793a');details.append(summary);const sc=el('div');sc.className='scroll';const table=el('table'),head=el('thead'),hr=el('tr');p.headers.forEach(h=>hr.append(el('th',h)));head.append(hr);table.append(head);const body=el('tbody');p.rows.forEach(r=>{const tr=el('tr');r.forEach(v=>tr.append(el('td',v)));body.append(tr)});table.append(body);sc.append(table);details.append(sc);sec.append(details);host.append(sec);\n if(window.Plotly){await Plotly.newPlot(plot,p.data,{font:{family:'system-ui,sans-serif',color:'#182b43'},margin:{l:60,r:20,t:20,b:85},legend:{orientation:'h',y:-.20},paper_bgcolor:'white',plot_bgcolor:'white',...p.layout},{responsive:true,displaylogo:false});}else{plot.textContent='\u30b0\u30e9\u30d5\u3092\u8aad\u307f\u8fbc\u3081\u307e\u305b\u3093\u3002\u30a4\u30f3\u30bf\u30fc\u30cd\u30c3\u30c8\u63a5\u7d9a\u3092\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u6570\u5024\u8868\u306f\u5229\u7528\u3067\u304d\u307e\u3059\u3002';plot.style.height='auto'}\n }if(current===generation)window.reportReady=key;\n}\ndraw();\n</script></html>'''\n",
}
_MINPY_SKIP = (
    "__builtins__",
    "__cached__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__path__",
    "__spec__",
)


def _minpy_original(fullname):
    if fullname == _MINPY_PREFIX:
        return ""
    prefix = _MINPY_PREFIX + "."
    if fullname.startswith(prefix):
        return fullname[len(prefix):]
    return None


class _MinpyLoader:
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        original = _minpy_original(module.__name__)
        if original is None:
            raise ImportError(module.__name__)
        if original == "":
            module.__path__ = []
            return
        source = _MINPY_SOURCES[original]
        filename = "minpy://" + original + ".py"
        module.__file__ = filename
        exec(compile(source, filename, "exec"), module.__dict__)


class _MinpyFinder:
    def __init__(self):
        self._minpy_sources = _MINPY_SOURCES

    def find_spec(self, fullname, path, target=None):
        original = _minpy_original(fullname)
        if original is None:
            return None
        if original == "":
            is_package = True
        elif original not in _MINPY_SOURCES:
            return None
        else:
            is_package = original in _MINPY_PACKAGES
        return importlib.machinery.ModuleSpec(
            fullname,
            _MinpyLoader(),
            origin="minpy://" + (original or _MINPY_PREFIX),
            is_package=is_package,
        )


def _minpy_install():
    for finder in sys.meta_path:
        if getattr(finder, "_minpy_sources", None) is _MINPY_SOURCES:
            return
    sys.meta_path.insert(0, _MinpyFinder())


def _minpy_run_entry_as_main():
    import types

    original = _MINPY_ENTRY
    full = _MINPY_PREFIX + "." + original
    module = types.ModuleType("__main__")
    origin = "minpy://" + original + ".py"
    module.__file__ = globals().get("__file__") or origin
    if original in _MINPY_PACKAGES:
        module.__package__ = full
        module.__path__ = []
    elif "." in original:
        module.__package__ = full.rpartition(".")[0]
    else:
        module.__package__ = _MINPY_PREFIX
    sys.modules["__main__"] = module
    sys.modules[full] = module
    exec(compile(_MINPY_SOURCES[original], origin, "exec"), module.__dict__)


def _minpy_export_entry(namespace):
    import importlib

    module = importlib.import_module(_MINPY_PREFIX + "." + _MINPY_ENTRY)
    for key, value in module.__dict__.items():
        if key not in _MINPY_SKIP:
            namespace[key] = value


_minpy_install()
if __name__ == "__main__":
    _minpy_run_entry_as_main()
else:
    _minpy_export_entry(globals())
