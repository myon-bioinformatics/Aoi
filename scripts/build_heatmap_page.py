"""🌡️ The DRAgoWing heatmap editor as one page (``page()``; ``python -S scripts/build_heatmap_page.py`` writes it to stdout).

Its parts are PySaiyanWeBoo's, read from the vendored single file (vendor/pysaiyanweboo/, pinned in vendor.lock.json)
under ``python -S``: the stylesheet (``bundle_css``), the theme switch, the stat tiles and the browser modules (ui.js,
scroll.js, records.js for the drafts, imagestudio.js for PNG Base64 and heatmap colors). Only the heatmap controls,
axes, and other page-specific behavior live here; matrix parsing is dragowing.py's ``HEATMAP_MATRIX_JS``.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor" / "pysaiyanweboo")]
import pysaiyanweboo as ui  # noqa: E402
from dragowing import HEATMAP_MATRIX_JS, PALETTE  # noqa: E402

# 🎨 The heatmap's own rules, after PySaiyanWeBoo's sheet (every theme of the switch, scroll, records).
HEATMAP_CSS = """@layer components{
.hm-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-bottom:var(--ui-space)}
.hm-head .ui-title{margin:0 0 .25rem}
.hm-head .ui-muted{margin:0}
.hm-head .ui-layout-switch{display:inline-flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:0;border:0;padding:0}
.hm-source{width:100%;box-sizing:border-box;font-family:var(--ui-font-mono);min-height:7.5rem;resize:vertical}
.hm-mono{width:100%;box-sizing:border-box;font-family:var(--ui-font-mono)}
.hm-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));gap:.75rem;margin:.75rem 0}
.hm-grid label{display:block}
.hm-grid .ui-input,.hm-grid select{width:100%;box-sizing:border-box;margin-top:.25rem}
.hm-actions{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:.75rem 0}
.hm-checks{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1.25rem;margin:.75rem 0}
.hm-checks label{display:inline-flex;align-items:center;gap:.4rem;cursor:pointer;color:var(--ui-fg)}
.hm-range-row{display:grid;grid-template-columns:1fr auto;gap:.5rem;align-items:center;margin-top:.25rem}
.hm-range-row input[type=range]{width:100%;margin:0}
.hm-primary{border-color:var(--ui-accent);font-weight:700}
.hm-status{margin:.5rem 0;font-weight:600;overflow-wrap:anywhere}
.hm-status[data-error]{color:var(--ui-danger)}
.hm-legend{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem;margin:.75rem 0;padding:.5rem .75rem;border:1px solid var(--ui-border);border-radius:var(--ui-radius)}
.hm-bar{flex:1 1 180px;min-width:120px;height:16px;border:1px solid var(--ui-border);border-radius:var(--ui-radius);overflow:hidden;display:flex}
.hm-bar-grad{width:100%;height:100%}
.hm-bar-step{flex:1 1 0;height:100%}
.hm-cell-info{margin:.5rem 0;padding:.5rem .75rem;border-left:4px solid var(--ui-accent);background:var(--ui-bg);font-family:var(--ui-font-mono);font-size:.875rem;overflow-wrap:anywhere}
.hm-view-scroll{border:1px solid var(--ui-border);border-radius:var(--ui-radius);padding:.75rem;background:repeating-conic-gradient(color-mix(in srgb,var(--ui-border) 22%,transparent) 0 25%,transparent 0 50%) 0 0/16px 16px}
.hm-view-scroll svg{display:block;max-width:none;height:auto}
.hm-view-scroll rect[data-cell]{cursor:pointer}
.hm-view-scroll rect[data-selected]{stroke:var(--ui-accent);stroke-width:3}
.hm-details{margin:.75rem 0 0}
.hm-details summary{cursor:pointer;font-weight:600}
a.ui-button{display:inline-flex;align-items:center;text-decoration:none;box-sizing:border-box}
.hm-actions button,.hm-actions a.ui-button{min-height:44px}
[hidden]{display:none!important}
}"""


# 🧩 PySaiyanWeBoo browser modules and the names the page script takes from each (imagestudio.js sets
# globalThis.webUiImageStudio itself; scroll.js binds every [data-ui-scroll] on load).
MODULES = (("ui.js", ("copyText", "bindTheme")), ("scroll.js", ("refreshScroll",)), ("records.js", ("bindDrafts", "downloadText")),
           ("imagestudio.js", ("heatmapColor",)))

PAGE = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>🌡️ ヒートマップ | DRAgoWing</title>
<style>__STYLE_CSS__</style>
</head>
<body class="ui-elements" data-ui-theme="modern">
<main class="ui-page">
<header class="hm-head">
  <div>
    <h1 class="ui-title">🌡️ ヒートマップ</h1>
    <p class="ui-muted">数値行列・CSV/TSV・Plotly heatmap JSON から、端末内で SVG / PNG / Base64 / Image Studio のシーン JSON を作成します。</p>
  </div>
  __THEME_SWITCH__
</header>

<section class="ui-panel" aria-labelledby="input-heading">
  <h2 id="input-heading">データ入力</h2>
  <div class="ui-shell-scroll" data-ui-scroll="row" data-scroll-label="サンプルデータ">
    <button type="button" class="ui-button" data-sample="basic">サンプル: 基本 2×3</button>
    <button type="button" class="ui-button" data-sample="missing">サンプル: 欠測入り 4×6</button>
    <button type="button" class="ui-button" data-sample="plotly">サンプル: Plotly JSON</button>
    <button type="button" class="ui-button" data-sample="csv">サンプル: CSV（ラベル付き）</button>
  </div>
  <form id="heatmap-form">
    <label for="source">数値行列 / CSV / TSV / Plotly JSON</label>
    <textarea class="ui-input hm-source" id="source" data-ui-draft="source" rows="5" spellcheck="false">[[0,1,2],[3,null,4]]</textarea>
    <div class="hm-grid">
      <div>
        <label for="format">入力形式</label>
        <select class="ui-input" id="format" data-ui-draft="format">
          <option value="auto" selected>自動判定</option>
          <option value="json">JSON（行列 / Plotly）</option>
          <option value="csv">CSV（カンマ区切り）</option>
          <option value="tsv">TSV（タブ区切り）</option>
        </select>
      </div>
      <div>
        <label for="file">ファイルを開く（2 MB 以下）</label>
        <input class="ui-input" id="file" type="file" accept=".json,.csv,.tsv,.txt,application/json,text/csv,text/tab-separated-values">
      </div>
      <div id="trace-wrap" hidden>
        <label for="trace-index">Plotly トレース</label>
        <select class="ui-input" id="trace-index"></select>
      </div>
    </div>
    <div class="hm-grid">
      <div>
        <label for="palette">配色パレット</label>
        <select class="ui-input" id="palette" data-ui-draft="palette">
          <option value="viridis" selected>Viridis 風（既定・Image Studio と同じ）</option>
          <option value="cividis">Cividis 風（色覚多様性配慮）</option>
          <option value="plasma">Plasma 風</option>
          <option value="rdbu">青 – 白 – 赤（発散）</option>
          <option value="blues">青（単色階調）</option>
        </select>
      </div>
      <div>
        <label for="steps">色の段階（0 は連続、2〜256）</label>
        <div class="hm-range-row">
          <input id="steps-range" type="range" min="0" max="256" value="0" aria-label="色の段階スライダー">
          <input class="ui-input" id="steps" data-ui-draft="steps" type="number" min="0" max="256" value="0" style="width:5.5rem">
        </div>
      </div>
      <div>
        <label for="zmin">色の下限 zmin（空欄は自動）</label>
        <input class="ui-input" id="zmin" data-ui-draft="zmin" type="number" step="any" placeholder="自動">
      </div>
      <div>
        <label for="zmax">色の上限 zmax（空欄は自動）</label>
        <input class="ui-input" id="zmax" data-ui-draft="zmax" type="number" step="any" placeholder="自動">
      </div>
    </div>
    <div class="hm-checks">
      <label><input type="checkbox" id="labels" data-ui-draft="labels" checked> 値を表示</label>
      <label><input type="checkbox" id="reverse-palette" data-ui-draft="reverse"> 配色を反転</label>
      <label><input type="checkbox" id="transpose" data-ui-draft="transpose"> 転置（行⇄列）</label>
      <label><input type="checkbox" id="flip-y" data-ui-draft="flip-y"> 上下反転</label>
      <label><input type="checkbox" id="export-axes" data-ui-draft="export-axes" checked> SVG/PNG に軸ラベル・凡例を含める</label>
    </div>
    <div class="hm-actions">
      <button class="ui-button hm-primary" type="submit" id="draw-btn">描画</button>
      <button class="ui-button" type="button" id="continuous">連続色に戻す</button>
      <button class="ui-button" type="button" id="auto-range">範囲を自動に戻す</button>
      <button class="ui-button" type="button" id="reset-draft">既定に戻す</button>
    </div>
    <p class="ui-muted" id="draft-note">設定と入力内容はこのブラウザに一時保存されます（外部送信なし）。</p>
  </form>
</section>

<section class="ui-panel" aria-labelledby="preview-heading">
  <h2 id="preview-heading">プレビューと統計</h2>
  <p role="status" id="status" class="hm-status" aria-live="polite"></p>
  __STATS__
  <div class="hm-legend" id="legend" hidden>
    <span id="legend-low" class="ui-tag"></span>
    <div class="hm-bar" id="legend-bar" aria-hidden="true"></div>
    <span id="legend-high" class="ui-tag"></span>
    <span class="ui-muted" id="legend-note"></span>
  </div>
  <p class="hm-cell-info" id="cell-info" hidden>セルをクリックまたはカーソルを合わせると、行・列・元の値・表示色を確認できます。</p>
  <div class="ui-shell-scroll hm-view-scroll" data-ui-scroll="table" data-scroll-label="ヒートマップ">
    <div id="view"></div>
  </div>
  <details class="hm-details" id="table-details" hidden>
    <summary>数値テーブルを表示</summary>
    <div class="ui-shell-scroll" data-ui-scroll="table" data-scroll-label="数値テーブル" id="table-scroll">
      <table class="ui-table" id="data-table"></table>
    </div>
  </details>
</section>

<section class="ui-panel" aria-labelledby="export-heading">
  <h2 id="export-heading">エクスポート・Image Studio 連携</h2>
  <p id="downloads" class="hm-actions"></p>
  <div class="hm-actions" id="copy-actions" hidden>
    <button type="button" class="ui-button" id="copy-svg">SVG をコピー</button>
    <button type="button" class="ui-button" id="copy-scene">シーン JSON をコピー</button>
    <button type="button" class="ui-button" id="copy-csv">CSV をコピー</button>
    <span class="ui-muted" id="copy-status" role="status" aria-live="polite"></span>
  </div>
  <div id="raster" hidden>
    <div class="hm-actions">
      <label>PNG の長辺 <select class="ui-input" id="size" data-ui-draft="size"><option>512</option><option selected>1024</option><option>2048</option></select> px</label>
      <button type="button" class="ui-button hm-primary" id="png">PNG を保存</button>
      <button type="button" class="ui-button" id="base64">PNG を Base64 表示</button>
    </div>
    <details class="hm-details" id="b64panel">
      <summary>Base64（Image Studio や資料への貼り付け用）</summary>
      <div class="hm-actions">
        <label>形式 <select class="ui-input" id="b64mode"><option value="dataUri">PNG data URI</option><option value="base64">Base64 のみ</option></select></label>
        <button type="button" class="ui-button" id="b64copy">Base64 をコピー</button>
        <button type="button" class="ui-button" id="b64save">テキストで保存</button>
      </div>
      <textarea class="ui-input hm-mono" id="b64text" rows="4" readonly aria-label="PNG Base64"></textarea>
      <p class="ui-muted" id="b64status" role="status"></p>
    </details>
  </div>
  <div class="ui-card">
    <div class="hm-actions">
      <a class="ui-button" href="https://myon-bioinformatics.github.io/tools/image-studio/">🖼️ シーン JSON を Image Studio で開く ↗</a>
    </div>
    <p class="ui-muted">ダウンロードした <code>scene.json</code>（<code>ironmate-image-studio/1</code>）を Image Studio の「開く」で読み込み、図形や注釈を重ねられます。配色はシーンに保存され、配色対応の Image Studio で再現できます。CLI 生成: <code>python -S dragowing.py --heatmap matrix.json &gt; scene.json</code></p>
  </div>
</section>
</main>

__SCRIPTS__
</body>
</html>"""

SCRIPT = r"""(() => {
  const DEFAULT_PALETTE = __PALETTE__;
  const PALETTES = {
    viridis: { name: "Viridis 風", stops: DEFAULT_PALETTE },
    cividis: { name: "Cividis 風", stops: ["#00224E", "#414D6B", "#7C7B78", "#BBAE6F", "#FEE838"] },
    plasma: { name: "Plasma 風", stops: ["#0D0887", "#7E03A8", "#CC4778", "#F89540", "#F0F921"] },
    rdbu: { name: "青–白–赤", stops: ["#2166AC", "#92C5DE", "#F7F7F7", "#F4A582", "#B2182B"] },
    blues: { name: "青単色", stops: ["#F7FBFF", "#C6DBEF", "#6BAED6", "#2171B5", "#08306B"] },
  };
  let PALETTE = [...DEFAULT_PALETTE];
  const clone = structuredClone;
  function fail(message) { throw Error(message); }
__CORE__
  const ui = globalThis.PySaiyanWeBoo;
  const heatColor = (value, low, high, levels = 0) => ui.heatmapColor(value, low, high, levels, PALETTE);
  ui.bindTheme(document);

  const el = id => document.getElementById(id);
  const DEFAULT_SOURCE = "[[0,1,2],[3,null,4]]";
  const SAMPLES = {
    basic: { format: "json", source: DEFAULT_SOURCE },
    missing: { format: "json", source: "[[3,1,4,1,5,9],[2,6,5,3,5,8],[9,7,9,3,2,3],[8,4,6,null,6,4]]" },
    plotly: {
      format: "json",
      source: JSON.stringify({
        data: [{
          type: "heatmap",
          x: ["月", "火", "水", "木"],
          y: ["朝", "昼", "夜"],
          z: [[1, 2, 3, 4], [2, 4, 6, 8], [4, 3, 2, 1]],
        }],
      }),
    },
    csv: { format: "csv", source: "曜日,朝,昼,夜\n月,12,24,18\n火,15,,22\n水,9,30,14" },
  };

  const urls = [];
  let lastState = null;
  let lastPngPayload = null;

  function setStatus(text, isError = false) {
    const node = el("status");
    node.textContent = text;
    if (isError) node.setAttribute("data-error", "");
    else node.removeAttribute("data-error");
  }

  function clearOutput() {
    el("raster").hidden = true;
    el("stats").hidden = true;
    el("legend").hidden = true;
    el("cell-info").hidden = true;
    el("table-details").hidden = true;
    el("copy-actions").hidden = true;
    el("b64panel").open = false;
    el("b64text").value = "";
    el("b64status").textContent = "";
    el("copy-status").textContent = "";
    el("view").replaceChildren();
    el("downloads").replaceChildren();
    el("data-table").replaceChildren();
    lastState = null;
    lastPngPayload = null;
    for (const url of urls.splice(0)) URL.revokeObjectURL(url);
  }

  function download(name, blob) {
    const link = document.createElement("a");
    link.className = "ui-button";
    link.download = name;
    link.textContent = "⬇ " + name;
    link.href = URL.createObjectURL(blob);
    urls.push(link.href);
    el("downloads").append(link);
  }

  function fmtNum(n) {
    if (n === null || n === undefined) return "—";
    if (Number.isInteger(n)) return String(n);
    return Number(n.toPrecision(6)).toString();
  }

  function parseDelimitedLine(line, sep) {
    if (sep === "\t") return line.split("\t").map(s => s.trim());
    const out = [];
    let cur = "", inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQuotes) {
        if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
        else if (ch === '"') inQuotes = false;
        else cur += ch;
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === sep) {
        out.push(cur.trim());
        cur = "";
      } else {
        cur += ch;
      }
    }
    out.push(cur.trim());
    return out;
  }

  function parseCellToken(token) {
    const trimmed = token.trim();
    if (!trimmed || /^(?:null|na|n\/a)$/i.test(trimmed)) return { kind: "null", value: null };
    if (/^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(trimmed)) {
      const n = Number(trimmed);
      if (Number.isFinite(n) && (!Number.isInteger(n) || Number.isSafeInteger(n))) {
        return { kind: "number", value: n };
      }
    }
    return { kind: "label", value: trimmed };
  }

  function parseTableText(raw, mode) {
    const lines = raw.replace(/\r\n?/g, "\n").split("\n").filter(l => l.trim() !== "");
    if (!lines.length) fail("入力が空です");
    const sep = mode === "tsv" ? "\t" : (mode === "csv" ? "," : (lines.some(l => l.includes("\t")) ? "\t" : ","));
    const rows = lines.map(line => parseDelimitedLine(line, sep));
    const width = rows[0].length;
    if (!width || rows.some(r => r.length !== width)) fail("各行の列数が揃っていません");

    const parsed = rows.map(r => r.map(parseCellToken));
    const row0HasLabel = parsed[0].some(c => c.kind === "label");
    const col0HasLabel = rows.length > 1 && parsed.slice(1).every(r => r[0].kind === "label" || r[0].kind === "null")
      && parsed.slice(1).some(r => r[0].kind === "label");
    const col0AllLabel = rows.every(r => r[0].kind === "label");

    let xlabels, ylabels, dataRows;
    if (row0HasLabel && rows.length > 1) {
      if (col0HasLabel && width > 1) {
        xlabels = rows[0].slice(1);
        ylabels = rows.slice(1).map(r => r[0]);
        dataRows = parsed.slice(1).map(r => r.slice(1));
      } else {
        xlabels = rows[0];
        ylabels = rows.slice(1).map((_, i) => i);
        dataRows = parsed.slice(1);
      }
    } else if (col0AllLabel && width > 1) {
      xlabels = Array.from({ length: width - 1 }, (_, i) => i);
      ylabels = rows.map(r => r[0]);
      dataRows = parsed.map(r => r.slice(1));
    } else {
      xlabels = Array.from({ length: width }, (_, i) => i);
      ylabels = rows.map((_, i) => i);
      dataRows = parsed;
    }

    const z = dataRows.map(row => row.map(cell => {
      if (cell.kind === "label") fail(`数値として読めない値があります: ${cell.value}`);
      return cell.value;
    }));
    return { z, x: xlabels, y: ylabels };
  }

  function parseInputSource(rawText, mode, traceIdx) {
    const trimmed = rawText.trim();
    if (!trimmed) fail("数値を入力してください");
    const useJson = mode === "json" || (mode === "auto" && (trimmed.startsWith("[") || trimmed.startsWith("{")));
    if (!useJson) {
      el("trace-wrap").hidden = true;
      return { source: parseTableText(rawText, mode), traceCount: 0 };
    }
    const parsed = JSON.parse(trimmed);
    if (parsed && !Array.isArray(parsed) && Array.isArray(parsed.data)) {
      const traces = parsed.data.filter(t => t && t.type === "heatmap");
      if (!traces.length) fail("Plotly JSON に type: 'heatmap' のトレースが見つかりません");
      if (traces.length > 1) {
        const select = el("trace-index");
        const prev = Number.isInteger(traceIdx) ? traceIdx : 0;
        const chosen = Math.max(0, Math.min(traces.length - 1, prev));
        select.replaceChildren(...traces.map((t, i) => {
          const opt = document.createElement("option");
          opt.value = String(i);
          opt.textContent = t.name ? `${i + 1}: ${t.name}` : `トレース ${i + 1}`;
          return opt;
        }));
        select.value = String(chosen);
        el("trace-wrap").hidden = false;
        return { source: traces[chosen], traceCount: traces.length };
      }
      el("trace-wrap").hidden = true;
      return { source: parsed, traceCount: 1 };
    }
    el("trace-wrap").hidden = true;
    return { source: parsed, traceCount: 0 };
  }

  function transformData(data, transpose, flipY) {
    let z = clone(data.z);
    let xlabels = clone(data.xlabels);
    let ylabels = clone(data.ylabels);
    if (flipY) {
      z.reverse();
      ylabels.reverse();
    }
    if (transpose) {
      const rows = z.length, cols = xlabels.length;
      const tz = Array.from({ length: cols }, (_, c) => Array.from({ length: rows }, (_, r) => z[r][c]));
      z = tz;
      [xlabels, ylabels] = [ylabels, xlabels];
    }
    return { ...data, z, xlabels, ylabels };
  }

  function applyPalette() {
    const entry = PALETTES[el("palette").value] || PALETTES.viridis;
    PALETTE = el("reverse-palette").checked ? [...entry.stops].reverse() : [...entry.stops];
    return entry.name + (el("reverse-palette").checked ? "（反転）" : "");
  }

  function buildSVG(data, includeAxes) {
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    const rows = data.z.length, cols = data.xlabels.length;
    const cellW = 80, cellH = 40;
    const gridW = cols * cellW, gridH = rows * cellH;
    const maxYLen = Math.max(1, ...data.ylabels.map(v => String(v).length));
    const left = includeAxes ? Math.min(200, Math.max(56, maxYLen * 11 + 18)) : 0;
    const top = includeAxes ? 20 : 0;
    const right = includeAxes ? 24 : 0;
    const bottom = includeAxes ? 92 : 0;
    const vbW = left + gridW + right;
    const vbH = top + gridH + bottom;

    svg.setAttribute("xmlns", svgNS);
    svg.setAttribute("viewBox", `0 0 ${vbW} ${vbH}`);
    if (vbW <= 860) {
      svg.setAttribute("width", "100%");
      svg.style.maxWidth = `${Math.max(vbW, 480)}px`;
    } else {
      svg.setAttribute("width", String(vbW));
      svg.setAttribute("height", String(vbH));
    }

    function append(tag, attrs, parent = svg) {
      const node = document.createElementNS(svgNS, tag);
      for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, String(v));
      parent.append(node);
      return node;
    }

    if (includeAxes) {
      const defs = append("defs", {});
      const grad = append("linearGradient", { id: "hm-grad", x1: "0%", y1: "0%", x2: "100%", y2: "0%" }, defs);
      PALETTE.forEach((c, idx) => {
        append("stop", { offset: `${(idx / 4) * 100}%`, "stop-color": c }, grad);
      });
    }

    data.z.forEach((row, y) => row.forEach((value, x) => {
      const fill = heatColor(value, data.low, data.high, data.levels);
      const rect = append("rect", {
        x: left + x * cellW,
        y: top + y * cellH,
        width: cellW,
        height: cellH,
        fill,
        tabindex: "0",
        "data-cell": `${y},${x}`,
      });
      const yName = data.ylabels[y], xName = data.xlabels[x];
      const info = `${yName} / ${xName}: ${value === null ? "欠測 (null)" : value} (${fill === "none" ? "透明" : fill})`;
      append("title", {}, rect).textContent = `${yName} / ${xName} / ${value ?? "欠測"}`;
      const showInfo = () => {
        for (const prev of svg.querySelectorAll("rect[data-selected]")) prev.removeAttribute("data-selected");
        rect.setAttribute("data-selected", "");
        el("cell-info").textContent = `選択セル — 行: ${yName} / 列: ${xName} / 値: ${value === null ? "欠測 (null)" : value} / 色: ${fill === "none" ? "透明 (none)" : fill}`;
      };
      rect.addEventListener("click", showInfo);
      rect.addEventListener("focus", showInfo);
      rect.addEventListener("mouseenter", () => {
        if (!svg.querySelector("rect[data-selected]")) {
          el("cell-info").textContent = `カーソル位置 — ${info}`;
        }
      });

      if (data.labels && value !== null) {
        const label = append("text", {
          x: left + x * cellW + cellW / 2,
          y: top + y * cellH + cellH / 2,
          "text-anchor": "middle",
          "dominant-baseline": "central",
          "font-family": "Meiryo, メイリオ, sans-serif",
          "font-size": "14",
          fill: "#111827",
          stroke: "#FFFFFF",
          "stroke-width": "3",
          "paint-order": "stroke",
          "pointer-events": "none",
        });
        label.textContent = String(value);
      }
    }));

    if (includeAxes) {
      data.ylabels.forEach((yl, y) => {
        const t = append("text", {
          x: left - 10,
          y: top + (y + 0.5) * cellH,
          "text-anchor": "end",
          "dominant-baseline": "central",
          "font-family": "Meiryo, メイリオ, sans-serif",
          "font-size": "13",
          fill: "currentColor",
          "data-axis-text": "1",
        });
        t.textContent = String(yl);
      });
      const step = cols > 16 ? Math.ceil(cols / 16) : 1;
      data.xlabels.forEach((xl, x) => {
        if (x % step !== 0) return;
        const t = append("text", {
          x: left + (x + 0.5) * cellW,
          y: top + gridH + 20,
          "text-anchor": "middle",
          "font-family": "Meiryo, メイリオ, sans-serif",
          "font-size": "13",
          fill: "currentColor",
          "data-axis-text": "1",
        });
        t.textContent = String(xl);
      });

      const barY = top + gridH + 42;
      const barW = Math.min(240, Math.max(120, gridW));
      if (data.levels) {
        const count = Math.min(data.levels, 32);
        const sw = barW / count;
        for (let k = 0; k < count; k++) {
          const val = data.low + (data.high - data.low) * (count === 1 ? 0.5 : k / (count - 1));
          append("rect", {
            x: left + k * sw,
            y: barY,
            width: sw + 0.5,
            height: 14,
            fill: heatColor(val, data.low, data.high, data.levels),
          });
        }
      } else {
        append("rect", { x: left, y: barY, width: barW, height: 14, fill: "url(#hm-grad)" });
      }
      append("rect", {
        x: left,
        y: barY,
        width: barW,
        height: 14,
        fill: "none",
        stroke: "currentColor",
        "stroke-opacity": "0.45",
      });
      const legendText = append("text", {
        x: left,
        y: barY + 34,
        "font-family": "Meiryo, メイリオ, sans-serif",
        "font-size": "12",
        fill: "currentColor",
        "data-axis-text": "1",
      });
      legendText.textContent = `${fmtNum(data.low)} → ${fmtNum(data.high)} ・ ${data.levels ? data.levels + "段階" : "連続色"} ・ 欠測は透明`;
    }
    return svg;
  }

  function serializeSVGForExport(svg, { widthPx, heightPx } = {}) {
    const copy = svg.cloneNode(true);
    const vb = svg.viewBox.baseVal;
    copy.style.maxWidth = "";
    copy.setAttribute("width", String(widthPx ?? vb.width));
    copy.setAttribute("height", String(heightPx ?? vb.height));
    for (const node of copy.querySelectorAll("rect[data-selected]")) node.removeAttribute("data-selected");
    for (const node of copy.querySelectorAll("rect[tabindex]")) node.removeAttribute("tabindex");
    for (const node of copy.querySelectorAll("[data-axis-text]")) {
      node.setAttribute("fill", "#111827");
      node.setAttribute("stroke", "#FFFFFF");
      node.setAttribute("stroke-width", "2.5");
      node.setAttribute("paint-order", "stroke");
      node.removeAttribute("data-axis-text");
    }
    for (const node of copy.querySelectorAll("rect[stroke='currentColor']")) {
      node.setAttribute("stroke", "#4B5563");
    }
    return new XMLSerializer().serializeToString(copy);
  }

  function renderStatsAndLegend(data, paletteLabel) {
    const values = data.z.flat().filter(v => v !== null);
    const missing = data.z.length * data.xlabels.length - values.length;
    const sorted = [...values].sort((a, b) => a - b);
    const mean = values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
    const median = !sorted.length ? null : (
      sorted.length % 2 ? sorted[(sorted.length - 1) / 2] : (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
    );

    const [size, range, average, gaps] = el("stats").querySelectorAll(".ui-stat-value");   // stat_tiles() order
    size.textContent = `${data.z.length} × ${data.xlabels.length}`;
    range.textContent = `${fmtNum(data.low)} – ${fmtNum(data.high)}`;
    average.textContent = `${fmtNum(mean)} / ${fmtNum(median)}`;
    gaps.textContent = String(missing);
    el("stats").hidden = false;

    el("legend-low").textContent = `下限: ${fmtNum(data.low)}`;
    el("legend-high").textContent = `上限: ${fmtNum(data.high)}`;
    el("legend-note").textContent = `${paletteLabel} ・ ${data.levels ? data.levels + "段階" : "連続色"} ・ 欠測は透明`;
    const bar = el("legend-bar");
    bar.replaceChildren();
    if (data.levels) {
      const count = Math.min(data.levels, 24);
      for (let k = 0; k < count; k++) {
        const val = data.low + (data.high - data.low) * (count === 1 ? 0.5 : k / (count - 1));
        const swatch = document.createElement("span");
        swatch.className = "hm-bar-step";
        swatch.style.background = heatColor(val, data.low, data.high, data.levels);
        bar.append(swatch);
      }
    } else {
      const grad = document.createElement("div");
      grad.className = "hm-bar-grad";
      grad.style.background = `linear-gradient(to right, ${PALETTE.join(",")})`;
      bar.append(grad);
    }
    el("legend").hidden = false;
    el("cell-info").textContent = "セルをクリックまたはカーソルを合わせると、行・列・元の値・表示色を確認できます。";
    el("cell-info").hidden = false;
  }

  function renderTable(data) {
    const table = el("data-table");
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    const corner = document.createElement("th");
    corner.scope = "col";
    corner.textContent = "y \\ x";
    headRow.append(corner);
    for (const xl of data.xlabels) {
      const th = document.createElement("th");
      th.scope = "col";
      th.setAttribute("data-num", "");
      th.textContent = String(xl);
      headRow.append(th);
    }
    thead.append(headRow);

    const tbody = document.createElement("tbody");
    data.z.forEach((row, y) => {
      const tr = document.createElement("tr");
      const rh = document.createElement("th");
      rh.scope = "row";
      rh.textContent = String(data.ylabels[y]);
      tr.append(rh);
      row.forEach(val => {
        const td = document.createElement("td");
        td.setAttribute("data-num", "");
        if (val === null) {
          td.setAttribute("data-missing", "");
          td.textContent = "欠測";
        } else {
          td.textContent = String(val);
        }
        tr.append(td);
      });
      tbody.append(tr);
    });
    table.replaceChildren(thead, tbody);
    el("table-details").hidden = false;
  }

  function toCSV(data) {
    const esc = v => {
      const s = v === null || v === undefined ? "" : String(v);
      return /[",\n\r]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
    };
    const lines = [["" , ...data.xlabels].map(esc).join(",")];
    data.z.forEach((row, y) => {
      lines.push([data.ylabels[y], ...row].map(esc).join(","));
    });
    return lines.join("\n") + "\n";
  }

  // 📝 PySaiyanWeBoo's records.js keeps every [data-ui-draft] field under SCOPE (restored now, saved on input);
  // a draw also saves what the page itself changed (a sample, the defaults).
  const drafts = ui.bindDrafts(document, { scope: "dragowing-heatmap/2" });
  el("steps-range").value = el("steps").value;
  function saveDraft() {
    for (const field of drafts) field.dispatchEvent(new Event("input"));
  }

  async function renderPNGBlob(svg) {
    const { width, height } = svg.viewBox.baseVal;
    const scale = Number(el("size").value) / Math.max(width, height);
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(width * scale));
    canvas.height = Math.max(1, Math.round(height * scale));
    const source = serializeSVGForExport(svg, { widthPx: canvas.width, heightPx: canvas.height });
    const sourceURL = URL.createObjectURL(new Blob([source], { type: "image/svg+xml" }));
    try {
      const image = new Image();
      image.src = sourceURL;
      await image.decode();
      canvas.getContext("2d").drawImage(image, 0, 0);
      const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/png"));
      if (!blob) fail("PNGを生成できませんでした");
      return blob;
    } finally {
      URL.revokeObjectURL(sourceURL);
    }
  }

  el("png").onclick = async () => {
    const button = el("png");
    const svg = el("view").querySelector("svg");
    if (!svg || button.disabled) return;
    button.disabled = true;
    try {
      const blob = await renderPNGBlob(svg);
      if (!svg.isConnected) return;
      const link = document.createElement("a");
      link.download = "heatmap.png";
      link.href = URL.createObjectURL(blob);
      link.click();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    } catch (error) {
      if (svg.isConnected) setStatus(error.message, true);
    } finally {
      button.disabled = false;
    }
  };

  function updateBase64Text() {
    if (!lastPngPayload) return;
    el("b64text").value = el("b64mode").value === "base64" ? lastPngPayload.base64 : lastPngPayload.dataUri;
  }

  el("base64").onclick = async () => {
    const button = el("base64");
    const svg = el("view").querySelector("svg");
    if (!svg || button.disabled) return;
    button.disabled = true;
    try {
      const blob = await renderPNGBlob(svg);
      lastPngPayload = globalThis.webUiImageStudio.pngPayload(new Uint8Array(await blob.arrayBuffer()));   // 🔡 PySaiyanWeBoo
      updateBase64Text();
      el("b64status").textContent = `PNG ${bytes.length.toLocaleString("en-US")} bytes`;
      el("b64panel").open = true;
    } catch (error) {
      el("b64status").textContent = error.message;
    } finally {
      button.disabled = false;
    }
  };
  el("b64mode").onchange = updateBase64Text;

  async function doCopy(text, label) {
    if (!text) return;
    try {
      await ui.copyText(text);
      el("copy-status").textContent = `${label}をコピーしました。`;
    } catch {
      el("copy-status").textContent = `${label}をコピーできませんでした。`;
    }
  }
  el("copy-svg").onclick = () => lastState && doCopy(lastState.svgText, "SVG");
  el("copy-scene").onclick = () => lastState && doCopy(lastState.sceneText, "シーンJSON");
  el("copy-csv").onclick = () => lastState && doCopy(lastState.csvText, "CSV");
  el("b64copy").onclick = async () => {
    const text = el("b64text").value;
    if (!text) return;
    try {
      await ui.copyText(text);
      el("b64status").textContent = "コピーしました。";
    } catch {
      el("b64text").focus();
      el("b64text").select();
      el("b64status").textContent = "自動コピーできないため選択しました。手動でコピーしてください。";
    }
  };
  el("b64save").onclick = () => {
    const text = el("b64text").value;
    if (!text) return;
    ui.downloadText("heatmap.base64.txt", text, "text/plain");
  };

  function draw() {
    clearOutput();
    try {
      const paletteLabel = applyPalette();
      const { source } = parseInputSource(el("source").value, el("format").value, Number(el("trace-index").value || 0));
      let data = matrix(source);
      data = transformData(data, el("transpose").checked, el("flip-y").checked);

      const zminRaw = el("zmin").value.trim(), zmaxRaw = el("zmax").value.trim();
      if (zminRaw !== "") {
        const n = Number(zminRaw);
        if (!Number.isFinite(n)) fail("色の下限 (zmin) には有限の数値を指定してください");
        data.low = n;
      }
      if (zmaxRaw !== "") {
        const n = Number(zmaxRaw);
        if (!Number.isFinite(n)) fail("色の上限 (zmax) には有限の数値を指定してください");
        data.high = n;
      }
      if (data.low > data.high) fail("色の下限 (zmin) は上限 (zmax) 以下にしてください");

      const stepsVal = el("steps").valueAsNumber;
      data.levels = Number.isInteger(stepsVal) ? stepsVal : Number(el("steps").value);
      el("steps-range").value = String(Math.max(0, Math.min(256, Number.isFinite(data.levels) ? data.levels : 0)));
      data.labels = el("labels").checked;
      heatColor(data.low, data.low, data.high, data.levels);

      const includeAxes = el("export-axes").checked;
      const svg = buildSVG(data, includeAxes);
      el("view").append(svg);

      const rows = data.z.length, cols = data.xlabels.length;
      const layer = { id: "heatmap", kind: "heatmap", name: "Heatmap", x: 80, y: 90, w: 1120, h: 520, rotation: 0, opacity: 1, ...data, palette: [...PALETTE] };
      const scene = { schema: "ironmate-image-studio/1", width: 1280, height: 720, background: "#FFFFFF", layers: [layer], source };
      const sceneText = JSON.stringify(scene, null, 2);
      const svgText = serializeSVGForExport(svg);
      const csvText = toCSV(data);
      lastState = { sceneText, svgText, csvText };

      download("scene.json", new Blob([sceneText], { type: "application/json" }));
      download("heatmap.svg", new Blob([svgText], { type: "image/svg+xml" }));
      download("heatmap.csv", new Blob([csvText], { type: "text/csv;charset=utf-8" }));

      renderStatsAndLegend(data, paletteLabel);
      renderTable(data);
      el("copy-actions").hidden = false;
      el("raster").hidden = false;
      setStatus(`${rows}行 × ${cols}列 · ${paletteLabel} · ${data.levels ? data.levels + "段階" : "連続色"}`);
      saveDraft();
      ui.refreshScroll();
    } catch (error) {
      setStatus(error.message, true);
    }
  }

  document.querySelector("form").onsubmit = event => { event.preventDefault(); draw(); };
  el("steps").onchange = () => { el("steps-range").value = el("steps").value; draw(); };
  el("steps-range").oninput = () => { el("steps").value = el("steps-range").value; draw(); };
  el("continuous").onclick = () => { el("steps").value = "0"; el("steps-range").value = "0"; draw(); };
  el("auto-range").onclick = () => { el("zmin").value = ""; el("zmax").value = ""; draw(); };
  for (const id of ["format", "trace-index", "palette", "reverse-palette", "labels", "transpose", "flip-y", "export-axes", "zmin", "zmax"]) {
    el(id).onchange = draw;
  }

  for (const button of document.querySelectorAll("[data-sample]")) {
    button.onclick = () => {
      const sample = SAMPLES[button.dataset.sample];
      if (!sample) return;
      el("source").value = sample.source;
      el("format").value = sample.format;
      el("zmin").value = "";
      el("zmax").value = "";
      draw();
    };
  }

  el("reset-draft").onclick = () => {
    el("source").value = DEFAULT_SOURCE;
    el("format").value = "auto";
    el("palette").value = "viridis";
    el("reverse-palette").checked = false;
    el("steps").value = "0";
    el("steps-range").value = "0";
    el("zmin").value = "";
    el("zmax").value = "";
    el("labels").checked = true;
    el("transpose").checked = false;
    el("flip-y").checked = false;
    el("export-axes").checked = true;
    el("size").value = "1024";
    draw();
  };

  el("file").onchange = async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 2000000) fail("ファイルは2MB以下にしてください");
      const name = file.name.toLowerCase();
      if (name.endsWith(".csv")) el("format").value = "csv";
      else if (name.endsWith(".tsv")) el("format").value = "tsv";
      else if (name.endsWith(".json")) el("format").value = "json";
      else el("format").value = "auto";
      el("source").value = await file.text();
      draw();
    } catch (error) {
      clearOutput();
      setStatus(error.message, true);
    } finally {
      event.target.value = "";
    }
  };

  draw();
})();
"""

def page() -> str:
    """The whole page: PySaiyanWeBoo's sheet, theme switch, stat tiles and modules around the heatmap's own markup and script."""
    css = ui.bundle_css(theme="modern", extra_css="".join(ui.css_source(name) for name in (
        "themes/github-like.css", "themes/terminal.css", "scroll.css", "records.css")) + HEATMAP_CSS)
    stats = ui.stat_tiles((("サイズ", "—", "行 × 列"), ("色範囲", "—", "zmin – zmax"), ("平均 / 中央値", "—", "有限値のみ"),
                           ("欠測 (null)", "—", "透明セル")))
    modules = "".join(ui.module_script(ui.js_source(name) + (
        f"\nObject.assign(globalThis.PySaiyanWeBoo ??= {{}}, {{ {', '.join(names)} }});\n" if names else "")) for name, names in MODULES)
    script = SCRIPT.replace("__PALETTE__", json.dumps(PALETTE)).replace("__CORE__", HEATMAP_MATRIX_JS)
    return (PAGE.replace("__STYLE_CSS__", css)
            .replace("__THEME_SWITCH__", ui.theme_switch_html(control="select", legend="テーマ"))
            .replace("__STATS__", f'<div id="stats" hidden>{stats}</div>')
            .replace("__SCRIPTS__", modules + ui.module_script(script)))


if __name__ == "__main__":
    print(page())
