"""Write the standalone DRAgoWing heatmap editor to stdout."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dragowing import HEATMAP_JS, PALETTE

SHARED_UI_CSS = """@layer base,components,theme;
/* tokens.css */
:root{--ui-bg:#0d1117;--ui-panel:#101820;--ui-fg:#d1f7c4;--ui-muted:#8b949e;--ui-border:#58a6ff;--ui-accent:#7ee787;--ui-danger:#cf222e;--ui-radius:0;--ui-text:16px;--ui-space:1rem;--ui-max:960px;--ui-font:Meiryo,メイリオ,sans-serif;--ui-font-mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace}
body[data-ui-theme="auto"]{color-scheme:dark light}@media(prefers-color-scheme:light){body[data-ui-theme="auto"]{--ui-bg:#ffffff;--ui-panel:#f6f8fa;--ui-fg:#1f2328;--ui-muted:#59636e;--ui-border:#d0d7de;--ui-accent:#0969da}}
body[data-ui-theme="green"]{--ui-bg:#edf0ec;--ui-panel:#ffffff;--ui-fg:#163b3b;--ui-muted:#546a61;--ui-border:#ccdcd4;--ui-accent:#126d66;--ui-danger:#a73528;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="red"]{--ui-bg:#f6eeee;--ui-panel:#fdfcfc;--ui-fg:#6c4141;--ui-muted:#7e6363;--ui-border:#d4bfbf;--ui-accent:#c43131;--ui-danger:#d02525;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="blue"]{--ui-bg:#eef1f6;--ui-panel:#fcfcfd;--ui-fg:#41526c;--ui-muted:#636e7e;--ui-border:#bfc7d4;--ui-accent:#316cc4;--ui-danger:#d02525;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="purple"]{--ui-bg:#fffbfe;--ui-panel:#f7f2fa;--ui-fg:#1c1b1f;--ui-muted:#49454f;--ui-border:#cac4d0;--ui-accent:#6750a4;--ui-danger:#b3261e;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="terminal"]{--ui-bg:#0a0e10;--ui-panel:#11171a;--ui-fg:#d5dee0;--ui-muted:#7c8a8d;--ui-border:#2b3436;--ui-accent:#5fd7a7;--ui-danger:#ff8080;--ui-radius:0;--ui-font:var(--ui-font-mono);color-scheme:dark}
/* base.css */
@layer base{*{box-sizing:border-box}body{margin:0;background:var(--ui-bg);color:var(--ui-fg);font:var(--ui-text)/1.6 var(--ui-font)}pre,code,kbd,samp{font-family:var(--ui-font-mono)!important}.ui-page{max-width:var(--ui-max);margin:auto;padding:var(--ui-space)}.ui-title{overflow-wrap:anywhere}a{color:inherit}.ui-print-only{display:none}@media print{body{background:#fff;color:#000}.ui-page{max-width:none;padding:0}.ui-no-print{display:none}.ui-print-only{display:block}a{text-decoration:none}}@media(prefers-reduced-motion:reduce){*,::before,::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}}
/* components.css */
@layer components{.ui-panel,.ui-card{background:var(--ui-panel);border:1px solid var(--ui-border);padding:var(--ui-space);margin:var(--ui-space) 0;border-radius:var(--ui-radius)}.ui-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:.75rem}.ui-tag{display:inline-block;border:1px solid var(--ui-border);padding:.1rem .4rem}.ui-button,.ui-input,.ui-elements button,.ui-elements select,.ui-elements textarea,.ui-elements input:not([type=checkbox],[type=radio],[type=range],[type=color],[type=file]){font:inherit;background:var(--ui-panel);color:var(--ui-fg);border:1px solid var(--ui-border);padding:.6rem;border-radius:var(--ui-radius)}.ui-button,.ui-elements button{cursor:pointer}.ui-button:hover,.ui-elements button:hover{border-color:var(--ui-accent)}.ui-button:disabled,.ui-elements button:disabled{opacity:.4;cursor:default}.ui-elements input[type=range],.ui-elements input[type=checkbox],.ui-elements input[type=radio]{accent-color:var(--ui-accent)}.ui-elements label{color:var(--ui-muted)}.ui-muted{color:var(--ui-muted)}.ui-back{margin:0 0 8px;font-size:.875rem}.ui-back .ui-links{margin:0}.ui-back a{color:var(--ui-muted);text-decoration:none}.ui-back a:hover,.ui-back a:focus-visible{color:var(--ui-accent);text-decoration:underline}}
/* themes/github-like.css */
@layer theme{body[data-ui-theme="github-like"]{--ui-bg:#ffffff;--ui-panel:#f6f8fa;--ui-fg:#1f2328;--ui-muted:#59636e;--ui-border:#d0d7de;--ui-accent:#0969da}body[data-ui-theme="github-like"] .ui-panel,body[data-ui-theme="github-like"] .ui-card{background:var(--ui-panel);border-radius:.375rem;box-shadow:none}body[data-ui-theme="github-like"] .ui-button,body[data-ui-theme="github-like"] .ui-input{background:#ffffff}body[data-ui-theme="github-like"] .ui-title{border-bottom:1px solid var(--ui-border);padding-bottom:.5rem}}
/* themes/modern.css */
@layer theme{body[data-ui-theme="modern"]{color-scheme:dark}body[data-ui-theme="modern"] .ui-title::before{content:"> ";color:var(--ui-accent)}body[data-ui-theme="modern"] .ui-panel,body[data-ui-theme="modern"] .ui-card{background:var(--ui-panel);box-shadow:4px 4px 0 rgba(88,166,255,.16)}}
/* themes/terminal.css */
@layer theme{body[data-ui-theme="terminal"] .ui-title::before{content:"# ";color:var(--ui-accent)}body[data-ui-theme="terminal"] .ui-button::before{content:"> ";color:var(--ui-accent)}body[data-ui-theme="terminal"] .ui-button:hover{border-color:var(--ui-accent)}body[data-ui-theme="terminal"] .ui-panel,body[data-ui-theme="terminal"] .ui-card{box-shadow:none}}
.heatmap-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.75rem;margin-bottom:.75rem}
.heatmap-head h1{margin:0}
.heatmap-theme{display:inline-flex;align-items:center;gap:.5rem}
.heatmap-form{display:grid;gap:.75rem}
.heatmap-form textarea{width:100%;font-family:var(--ui-font-mono)}
.heatmap-controls{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1rem}
.heatmap-controls label{display:inline-flex;align-items:center;gap:.5rem;margin:0}
#view svg{display:block;max-width:100%;height:auto;background:#ffffff;border:1px solid var(--ui-border)}
#downloads{display:flex;flex-wrap:wrap;gap:.5rem 1rem}
#downloads a{color:var(--ui-accent)}
"""

PAGE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ヒートマップ | DRAgoWing</title><style>__CSS__</style></head>
<body class="ui-elements" data-ui-theme="modern"><main class="ui-page">
<div class="heatmap-head"><h1 class="ui-title">🌡️ ヒートマップ</h1>
<label class="heatmap-theme">テーマ <select id="theme" class="ui-input" aria-label="テーマ"><option value="modern">modern</option><option value="auto">auto</option><option value="github-like">github-like</option><option value="green">green</option><option value="red">red</option><option value="blue">blue</option><option value="purple">purple</option><option value="terminal">terminal</option></select></label></div>
<section class="ui-panel"><form class="heatmap-form"><label>数値行列 / Plotly JSON<br><textarea id="source" class="ui-input" rows="4" cols="32">[[0,1,2],[3,null,4]]</textarea></label>
<div class="heatmap-controls"><label>JSONファイル <input type="file" id="file" accept=".json"></label>
<label>色の段階（0は連続）<input id="steps" class="ui-input" type="number" min="0" max="256" value="0"></label>
<label><input type="checkbox" id="labels" checked>値を表示</label>
<button class="ui-button">描画</button></div></form></section>
<section class="ui-panel"><p role="status" id="status" class="ui-muted"></p>
<div id="view"></div><p id="downloads"></p>
<p id="raster" hidden><label>PNGの長辺 <select id="size" class="ui-input"><option>512</option><option selected>1024</option><option>2048</option></select> px</label>
<button type="button" id="png" class="ui-button">PNGを保存</button></p>
<p><a href="https://myon-bioinformatics.github.io/tools/ironmate/">シーンJSONをIronmateで開く</a></p></section></main>
<script>
const PALETTE = __PALETTE__;
const clone = structuredClone;
function fail(message) { throw Error(message); }
__CORE__
const el = id => document.getElementById(id);
const THEME_KEY = "dragowing-heatmap-theme";
const themeSelect = el("theme");
function applyTheme(name) {
  const valid = ["modern","auto","github-like","green","red","blue","purple","terminal"];
  const chosen = valid.includes(name) ? name : "modern";
  document.body.dataset.uiTheme = chosen;
  if (themeSelect) themeSelect.value = chosen;
  try { localStorage.setItem(THEME_KEY, chosen); } catch {}
}
try { applyTheme(localStorage.getItem(THEME_KEY) || "modern"); } catch { applyTheme("modern"); }
if (themeSelect) themeSelect.onchange = () => applyTheme(themeSelect.value);
const urls = [];
function clearOutput() {
  el("raster").hidden = true;
  el("view").replaceChildren();
  el("downloads").replaceChildren();
  for (const url of urls.splice(0)) URL.revokeObjectURL(url);
}
function download(name, blob) {
  const link = document.createElement("a");
  link.download = name;
  link.textContent = name;
  link.href = URL.createObjectURL(blob);
  urls.push(link.href);
  el("downloads").append(link, " ");
}
el("png").onclick = async () => {
  const button = el("png");
  const svg = el("view").querySelector("svg");
  if (!svg || button.disabled) return;
  button.disabled = true;
  let sourceURL;
  try {
    const {width, height} = svg.viewBox.baseVal;
    const scale = Number(el("size").value) / Math.max(width, height);
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(width * scale));
    canvas.height = Math.max(1, Math.round(height * scale));
    const copy = svg.cloneNode(true);
    copy.setAttribute("width", canvas.width);
    copy.setAttribute("height", canvas.height);
    const source = new XMLSerializer().serializeToString(copy);
    sourceURL = URL.createObjectURL(new Blob([source], {type:"image/svg+xml"}));
    const image = new Image();
    image.src = sourceURL;
    await image.decode();
    canvas.getContext("2d").drawImage(image, 0, 0);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/png"));
    if (!blob) fail("PNGを生成できませんでした");
    if (!svg.isConnected) return;
    const link = document.createElement("a");
    link.download = "heatmap.png";
    link.href = URL.createObjectURL(blob);
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  } catch (error) {
    if (svg.isConnected) el("status").textContent = error.message;
  } finally {
    if (sourceURL) URL.revokeObjectURL(sourceURL);
    button.disabled = false;
  }
};
function draw() {
  clearOutput();
  try {
    const source = JSON.parse(el("source").value);
    const data = matrix(source);
    data.levels = el("steps").valueAsNumber;
    data.labels = el("labels").checked;
    heatColor(data.low, data.low, data.high, data.levels);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    const rows = data.z.length, cols = data.xlabels.length;
    svg.setAttribute("viewBox", `0 0 ${cols*80} ${rows*40}`);
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", Math.min(520,rows*40));
    function append(tag, attrs, parent = svg) {
      const node = document.createElementNS(svg.namespaceURI,tag);
      for (const [k,v] of Object.entries(attrs)) node.setAttribute(k,v);
      parent.append(node);
      return node;
    }
    data.z.forEach((row,y) => row.forEach((value,x) => {
      const cell = append("rect",{x:x*80,y:y*40,width:80,height:40,fill:heatColor(value,data.low,data.high,data.levels)});
      append("title",{},cell).textContent = [data.ylabels[y],data.xlabels[x],value ?? "欠測"].join(" / ");
      if (data.labels && value !== null) {
        const label = append("text",{x:x*80+40,y:y*40+25,"text-anchor":"middle",stroke:"white","paint-order":"stroke"});
        label.textContent = value;
      }
    }));
    el("view").append(svg);
    const layer = {id:"heatmap",kind:"heatmap",name:"Heatmap",x:80,y:90,w:1120,h:520,rotation:0,opacity:1,...data};
    const scene = {schema:"ironmate-image-studio/1",width:1280,height:720,background:"#FFFFFF",layers:[layer],source};
    download("scene.json",new Blob([JSON.stringify(scene)],{type:"application/json"}));
    download("heatmap.svg",new Blob([new XMLSerializer().serializeToString(svg)],{type:"image/svg+xml"}));
    el("raster").hidden = false;
    el("status").textContent = rows+"行 × "+cols+"列";
  } catch (error) { el("status").textContent = error.message; }
}
document.querySelector("form").onsubmit = event => { event.preventDefault(); draw(); };
el("steps").onchange = draw;
el("labels").onchange = draw;
el("file").onchange = async event => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (file.size > 2000000) fail("行列JSONは2MB以下にしてください");
    el("source").value = await file.text();
    draw();
  } catch (error) { clearOutput(); el("status").textContent = error.message; }
};
draw();
</script></html>"""

if __name__ == "__main__":
    print(PAGE.replace("__CSS__", SHARED_UI_CSS).replace("__PALETTE__", json.dumps(PALETTE)).replace("__CORE__", HEATMAP_JS))
