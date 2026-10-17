#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: 2bf96800b682c9b58b438e1d274267e3fcf832a3
# entry: distributions/entries/dragowing_api.py
# entry-module: dragowing_api
# search-paths: distributions/entries,dragowing
# allow: 
# allow-cycles: no
# cycles: 
# modules: dragowing_api,figures,records,research_report
# prefix: _minpy_5327c5960c0f06e9
# content-sha256: f0c28699255cb9ba3fe104579b69a1fdb389fbd1c5dbe737858ff2ddd104ed9f
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_5327c5960c0f06e9"
_MINPY_ENTRY = "dragowing_api"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "dragowing_api": "\"\"\"DRAgoWing min: figure specifications, aggregate HTML reports and JSONL records.\n\nPlotly.js remains a browser runtime dependency of rendered reports, outside Python.\n\"\"\"\nfrom _minpy_5327c5960c0f06e9.figures import class_mark, heatmap_figure, trajectory_figure\nfrom _minpy_5327c5960c0f06e9.records import read_jsonl, select_items\nfrom _minpy_5327c5960c0f06e9.research_report import render_report\n\n__all__ = ['class_mark', 'heatmap_figure', 'trajectory_figure', 'read_jsonl', 'select_items', 'render_report']\n",
    "figures": "\"\"\"\u8a18\u9332\u3055\u308c\u305f\u5024\u306e Plotly \u56f3 JSON\uff08data / layout\uff09\u3002\u3042\u3066\u306f\u3081\u3001\u5e73\u6ed1\u5316\u3001\u968e\u7d1a\u3078\u306e\u4e38\u3081\u306f\u3057\u306a\u3044\u3002\"\"\"\nfrom __future__ import annotations\n\nimport json\n\nA_COLOR = \"#1f77b4\"\nB_COLOR = \"#d62728\"\nLINE_COLOR = \"#9aa0a6\"\nFONT = \"Noto Sans JP, Yu Gothic, Meiryo, sans-serif\"\n\n# Plotly \u306e Viridis \u3092 ``to_dict()`` \u3057\u305f\u3068\u304d\u3068\u540c\u3058\u6bb5\u3002\n_VIRIDIS_SCALE = [\n    [0.0, \"#440154\"],\n    [0.1111111111111111, \"#482878\"],\n    [0.2222222222222222, \"#3e4989\"],\n    [0.3333333333333333, \"#31688e\"],\n    [0.4444444444444444, \"#26828e\"],\n    [0.5555555555555556, \"#1f9e89\"],\n    [0.6666666666666666, \"#35b779\"],\n    [0.7777777777777778, \"#6ece58\"],\n    [0.8888888888888888, \"#b5de2b\"],\n    [1.0, \"#fde725\"],\n]\n\n\ndef class_mark(upper) -> tuple[str, str]:\n    \"\"\"upper_half \u306e true/false \u3092 A/B \u3068\u8272\u306b\u3059\u308b\u3002null \u306f B \u306b\u3057\u306a\u3044\u3002\"\"\"\n    if upper is True:\n        return A_COLOR, \"A\"\n    if upper is False:\n        return B_COLOR, \"B\"\n    return \"#888888\", \"\"\n\n\ndef _base_layout(**extra):\n    layout = dict(\n        template={},\n        paper_bgcolor=\"#ffffff\",\n        plot_bgcolor=\"#ffffff\",\n        font=dict(family=FONT, size=13, color=\"#1a1a1a\"),\n        margin=dict(l=60, r=30, t=88, b=50),\n    )\n    layout.update(extra)\n    return layout\n\n\ndef _team_label(league: str, team_name: str, team: str) -> str:\n    return f\"{league} {team_name} ({team})\"\n\n\ndef _subplot_domains(ncols: int, spacing: float = 0.08) -> list[tuple[float, float]]:\n    if ncols < 1:\n        raise ValueError(\"ncols\")\n    width = (1.0 - spacing * (ncols - 1)) / ncols\n    return [(index * (width + spacing), index * (width + spacing) + width) for index in range(ncols)]\n\n\ndef _axis_names(col_index: int) -> tuple[str, str]:\n    \"\"\"1-based column index \u2192 trace xaxis/yaxis refs and layout axis keys.\"\"\"\n    if col_index == 1:\n        return \"x\", \"y\"\n    suffix = str(col_index)\n    return f\"x{suffix}\", f\"y{suffix}\"\n\n\ndef _layout_axis_key(axis_ref: str) -> str:\n    return \"xaxis\" if axis_ref == \"x\" else f\"{axis_ref}axis\"\n\n\ndef trajectory_figure(rows: list[dict]) -> dict:\n    \"\"\"C3. \u5f97\u70b9\u9806\u4f4d \u00d7 \u5931\u70b9\u9806\u4f4d\u3002\u70b9\u306e\u8272\u306f upper_half\u3002\u7dda\u306f\u8a18\u9332\u306e\u9806\u3092\u3064\u306a\u3050\u3060\u3051\u3002\"\"\"\n    for key in (\"league\", \"team\", \"team_name\", \"season\", \"rank_rf\", \"rank_ra\", \"upper_half\"):\n        if rows and key not in rows[0]:\n            raise ValueError(f\"\u5217\u304c\u306a\u3044: {key}\")\n    grouped: dict[tuple, list] = {}\n    for index, row in enumerate(rows):\n        if row.get(\"rank_rf\") is None or row.get(\"rank_ra\") is None:\n            continue\n        grouped.setdefault((row[\"league\"], row[\"team\"]), []).append((row[\"season\"], index, row))\n    leagues = sorted({league for league, _ in grouped})\n    if not leagues:\n        raise ValueError(\"\u8ecc\u8de1\u306b\u3059\u308b\u884c\u304c\u306a\u3044\")\n    domains = _subplot_domains(len(leagues))\n    traces: list[dict] = []\n    points = []\n    layout = _base_layout(\n        title=dict(\n            text=\"\u5f97\u70b9\u9806\u4f4d rank_rf \u00d7 \u5931\u70b9\u9806\u4f4d rank_ra<br>\u70b9\u306e\u8272: A \u306f upper_half==true\u3001B \u306f upper_half==false<br>\u7dda\u306f\u540c\u3058 league\u30fbteam \u306e\u8a18\u9332\u3092 season \u306e\u6607\u9806\u306b\u3064\u306a\u3044\u3060\u3082\u306e\"\n        ),\n        height=640,\n        width=1040,\n        legend=dict(font=dict(size=11)),\n        meta={\"kind\": \"trajectory\", \"source\": \"season.jsonl\", \"points\": points},\n    )\n    annotations = []\n    for col, league in enumerate(leagues, start=1):\n        x_ref, y_ref = _axis_names(col)\n        x_key = _layout_axis_key(x_ref)\n        y_key = _layout_axis_key(y_ref)\n        lo, hi = domains[col - 1]\n        layout[x_key] = dict(\n            anchor=y_ref,\n            domain=[lo, hi],\n            title=dict(text=\"\u5f97\u70b9\u9806\u4f4d rank_rf\"),\n            dtick=1,\n        )\n        layout[y_key] = dict(\n            anchor=x_ref,\n            domain=[0.0, 1.0],\n            title=dict(text=\"\u5931\u70b9\u9806\u4f4d rank_ra\"),\n            dtick=1,\n            scaleanchor=x_ref,\n            scaleratio=1,\n        )\n        annotations.append(\n            dict(\n                font=dict(size=16),\n                showarrow=False,\n                text=f\"league={league}\",\n                x=(lo + hi) / 2,\n                xanchor=\"center\",\n                xref=\"paper\",\n                y=1.0,\n                yanchor=\"bottom\",\n                yref=\"paper\",\n            )\n        )\n        teams = sorted(team for lg, team in grouped if lg == league)\n        for team in teams:\n            series = sorted(grouped[(league, team)], key=lambda item: (item[0], item[1]))\n            team_name = series[0][2][\"team_name\"]\n            custom, colors, xs, ys = [], [], [], []\n            for season, _index, row in series:\n                color, klass = class_mark(row.get(\"upper_half\"))\n                xs.append(row[\"rank_rf\"])\n                ys.append(row[\"rank_ra\"])\n                colors.append(color)\n                custom.append(\n                    {\n                        \"season\": row[\"season\"],\n                        \"league\": row[\"league\"],\n                        \"team\": row[\"team\"],\n                        \"team_name\": row[\"team_name\"],\n                        \"rank_rf\": row[\"rank_rf\"],\n                        \"rank_ra\": row[\"rank_ra\"],\n                        \"upper_half\": row[\"upper_half\"],\n                        \"class\": klass,\n                    }\n                )\n                points.append(custom[-1])\n            trace = dict(\n                type=\"scatter\",\n                x=xs,\n                y=ys,\n                mode=\"lines+markers\",\n                name=_team_label(league, team_name, team),\n                line=dict(color=LINE_COLOR, width=1, shape=\"linear\"),\n                marker=dict(color=colors, size=10, line=dict(width=0)),\n                customdata=custom,\n                connectgaps=False,\n                hovertemplate=(\n                    \"season=%{customdata.season}<br>\"\n                    \"league=%{customdata.league} %{customdata.team_name} (%{customdata.team})<br>\"\n                    \"rank_rf=%{customdata.rank_rf}<br>\"\n                    \"rank_ra=%{customdata.rank_ra}<br>\"\n                    \"upper_half=%{customdata.upper_half}<br>\"\n                    \"class=%{customdata.class}<extra></extra>\"\n                ),\n                meta={\"role\": \"trajectory\", \"league\": league, \"team\": team, \"team_name\": team_name},\n            )\n            trace[\"xaxis\"] = x_ref\n            trace[\"yaxis\"] = y_ref\n            traces.append(trace)\n    layout[\"annotations\"] = annotations\n    traces.extend(\n        [\n            dict(\n                type=\"scatter\",\n                x=[],\n                y=[],\n                mode=\"markers\",\n                marker=dict(color=A_COLOR, size=10),\n                name=\"A (upper_half==true)\",\n                meta={\"role\": \"legend\"},\n            ),\n            dict(\n                type=\"scatter\",\n                x=[],\n                y=[],\n                mode=\"markers\",\n                marker=dict(color=B_COLOR, size=10),\n                name=\"B (upper_half==false)\",\n                meta={\"role\": \"legend\"},\n            ),\n        ]\n    )\n    return {\"data\": traces, \"layout\": layout}\n\n\ndef _numeric_column(rows: list[dict], column: str) -> None:\n    if not rows or column not in rows[0]:\n        raise ValueError(f\"\u5217\u304c\u306a\u3044: {column}\")\n    for row in rows:\n        value = row.get(column)\n        if value is None:\n            continue\n        if isinstance(value, bool) or not isinstance(value, (int, float)):\n            raise ValueError(f\"\u5217 {column} \u306f\u6570\u5024\u3067\u306f\u306a\u3044\")\n\n\n# \u4e0a\u304b\u3089\u4e0b\u3002\u4e2d\u65e5 d \u3092\u6700\u4e0a\u6bb5\u306b\u3059\u308b\u3002\u62ec\u5f27\u5185\u306e\u4e26\u3073\u306f\u8a18\u9332\u306b\u3042\u308b\u8a18\u53f7\u3067\u3001d \u3092\u5148\u982d\u306b\u7e70\u308a\u4e0a\u3052\u305f\u3082\u306e\u3002\n_TEAM_TOP_DOWN = (\"d\", \"g\", \"s\", \"db\", \"t\", \"c\", \"h\", \"f\", \"b\", \"e\", \"l\", \"m\")\n\n\ndef _exact_text(value) -> str:\n    if value is None:\n        return \"null\"\n    return json.dumps(value, ensure_ascii=False)\n\n\ndef _heatmap_order(teams: list[tuple]) -> list[tuple]:\n    rank = {code: index for index, code in enumerate(_TEAM_TOP_DOWN)}\n\n    def key(item):\n        code = item[1]\n        if code in rank:\n            return (0, rank[code], item[0])\n        return (1, code, item[0])\n\n    return sorted(teams, key=key)\n\n\ndef heatmap_figure(rows: list[dict], column: str = \"wins_vs_pythag\") -> dict:\n    \"\"\"C4. \u7403\u56e3 \u00d7 \u5e74\u3002\u8272\u306f\u5217\u306e\u5024\u3002\u30de\u30b9\u306e\u6587\u5b57\u306f A/B \u3060\u3051\u3002\u6570\u306f\u30db\u30d0\u30fc\u3002\"\"\"\n    _numeric_column(rows, column)\n    teams = _heatmap_order(list({(row[\"league\"], row[\"team\"], row[\"team_name\"]) for row in rows}))\n    seasons = sorted({row[\"season\"] for row in rows})\n    index = {(row[\"league\"], row[\"team\"], row[\"season\"]): row for row in rows}\n    codes = [team for _league, team, _name in teams]\n    clash = len(codes) != len(set(codes))\n    labels = [f\"{league}:{team}\" if clash else team for league, team, _name in teams]\n    z, text, marks, records, custom = [], [], [], [], []\n    for (league, team, name), label in zip(teams, labels):\n        z_row, text_row, mark_row, custom_row = [], [], [], []\n        for season in seasons:\n            row = index.get((league, team, season))\n            if row is None:\n                value, upper, rank = None, None, None\n            else:\n                value, upper = row.get(column), row.get(\"upper_half\")\n                rank = row.get(\"rank\") if \"rank\" in row else None\n            _color, klass = class_mark(upper)\n            z_row.append(value)\n            text_row.append(klass)\n            mark_row.append(klass)\n            custom_row.append(\n                {\n                    \"league\": league,\n                    \"team\": team,\n                    \"team_name\": name,\n                    \"season\": season,\n                    \"class\": klass,\n                    \"rank\": rank,\n                    \"rank_text\": _exact_text(rank),\n                    \"value\": value,\n                    \"value_text\": _exact_text(value),\n                }\n            )\n            records.append(custom_row[-1] | {\"column\": column, \"upper_half\": upper, \"mark\": klass})\n        z.append(z_row)\n        text.append(text_row)\n        marks.append(mark_row)\n        custom.append(custom_row)\n    finite = [value for row in z for value in row if isinstance(value, (int, float))]\n    zmin = min(finite) if finite else None\n    zmax = max(finite) if finite else None\n    layout = _base_layout(\n        title=dict(text=\"\u7403\u56e3 \u00d7 \u5e74\"),\n        height=640,\n        width=980,\n        meta={\n            \"kind\": \"heatmap\",\n            \"source\": \"season.jsonl\",\n            \"column\": column,\n            \"x\": seasons,\n            \"y\": labels,\n            \"z\": z,\n            \"marks\": marks,\n            \"records\": records,\n        },\n        xaxis=dict(type=\"category\", title=dict(text=\"season\"), automargin=True),\n        yaxis=dict(\n            type=\"category\",\n            categoryorder=\"array\",\n            categoryarray=list(reversed(labels)),\n            title=dict(text=\"team\"),\n            automargin=True,\n        ),\n    )\n    trace = dict(\n        type=\"heatmap\",\n        x=seasons,\n        y=labels,\n        z=z,\n        text=text,\n        texttemplate=\"%{text}\",\n        textfont=dict(family=FONT, size=14, color=\"#1a1a1a\"),\n        customdata=custom,\n        colorscale=_VIRIDIS_SCALE,\n        zmin=zmin,\n        zmax=zmax,\n        zsmooth=False,\n        hoverongaps=False,\n        showlegend=False,\n        colorbar=dict(title=dict(text=column)),\n        hovertemplate=(\n            \"team=%{customdata.team} %{customdata.team_name}<br>\"\n            \"season=%{customdata.season}<br>\"\n            \"class=%{customdata.class}<br>\"\n            \"rank=%{customdata.rank_text}<br>\"\n            f\"{column}=%{{customdata.value_text}}<extra></extra>\"\n        ),\n    )\n    return {\"data\": [trace], \"layout\": layout}\n",
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
