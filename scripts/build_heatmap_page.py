"""Write the standalone DRAgoWing heatmap editor to stdout."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dragowing import HEATMAP_JS, PALETTE

PAGE = """<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ヒートマップ | DRAgoWing</title><main><h1>ヒートマップ</h1>
<form><label>数値行列 / Plotly JSON<br><textarea id="source" rows="4" cols="32">[[0,1,2],[3,null,4]]</textarea></label>
<label>JSONファイル <input type="file" id="file" accept=".json"></label>
<label>色の段階（0は連続）<input id="steps" type="number" min="0" max="256" value="0"></label>
<label><input type="checkbox" id="labels" checked>値を表示</label>
<button>描画</button></form><p role="status" id="status"></p>
<div id="view"></div><p id="downloads"></p>
<a href="https://myon-bioinformatics.github.io/Ironmate/">シーンJSONをIronmateで開く</a></main>
<script>
const PALETTE = __PALETTE__;
const clone = structuredClone;
function fail(message) { throw Error(message); }
__CORE__
const el = id => document.getElementById(id);
const urls = [];
function clearOutput() {
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
    print(PAGE.replace("__PALETTE__", json.dumps(PALETTE)).replace("__CORE__", HEATMAP_JS))
