"""Bundled PySaiyanWeBoo CSS, HTML controls, and JS helpers for the standalone heatmap page."""

STYLE_CSS = r"""/* web-ui-bundle/1 commit=a55e8504d351c7f58bb13096ef1abae3ce5fcc8a sha256=a6d9284cbc81ca0665680f983c0d457dccf22b0001e0a4d435a44e2e6bc800fa build_heatmap_bundle.py*/
@layer base,components,theme;
/* css/tokens.css */
:root{--ui-bg:#0d1117;--ui-panel:#101820;--ui-fg:#d1f7c4;--ui-muted:#8b949e;--ui-border:#58a6ff;--ui-accent:#7ee787;--ui-danger:#cf222e;--ui-radius:0;--ui-text:16px;--ui-space:1rem;--ui-max:960px;--ui-font:Meiryo,メイリオ,sans-serif;--ui-font-mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace}
/* auto: dark (the :root palette) unless the browser prefers light, then the github-like palette. */
body[data-ui-theme="auto"]{color-scheme:dark light}@media(prefers-color-scheme:light){body[data-ui-theme="auto"]{--ui-bg:#ffffff;--ui-panel:#f6f8fa;--ui-fg:#1f2328;--ui-muted:#59636e;--ui-border:#d0d7de;--ui-accent:#0969da}}
/* Candidate themes, token-only: palettes, no theme files (see theme_palettes()). */
body[data-ui-theme="green"]{--ui-bg:#edf0ec;--ui-panel:#ffffff;--ui-fg:#163b3b;--ui-muted:#546a61;--ui-border:#ccdcd4;--ui-accent:#126d66;--ui-danger:#a73528;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="red"]{--ui-bg:#f6eeee;--ui-panel:#fdfcfc;--ui-fg:#6c4141;--ui-muted:#7e6363;--ui-border:#d4bfbf;--ui-accent:#c43131;--ui-danger:#d02525;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="blue"]{--ui-bg:#eef1f6;--ui-panel:#fcfcfd;--ui-fg:#41526c;--ui-muted:#636e7e;--ui-border:#bfc7d4;--ui-accent:#316cc4;--ui-danger:#d02525;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="purple"]{--ui-bg:#fffbfe;--ui-panel:#f7f2fa;--ui-fg:#1c1b1f;--ui-muted:#49454f;--ui-border:#cac4d0;--ui-accent:#6750a4;--ui-danger:#b3261e;--ui-radius:.5rem;color-scheme:light}
body[data-ui-theme="terminal"]{--ui-bg:#0a0e10;--ui-panel:#11171a;--ui-fg:#d5dee0;--ui-muted:#7c8a8d;--ui-border:#2b3436;--ui-accent:#5fd7a7;--ui-danger:#ff8080;--ui-radius:0;--ui-font:var(--ui-font-mono);color-scheme:dark}
/* css/base.css */
@layer base{*{box-sizing:border-box}body{margin:0;background:var(--ui-bg);color:var(--ui-fg);font:var(--ui-text)/1.6 var(--ui-font)}pre,code,kbd,samp{font-family:var(--ui-font-mono)!important}.ui-page{max-width:var(--ui-max);margin:auto;padding:var(--ui-space)}.ui-title{overflow-wrap:anywhere}a{color:inherit}.ui-print-only{display:none}@media print{body{background:#fff;color:#000}.ui-page{max-width:none;padding:0}.ui-no-print{display:none}.ui-print-only{display:block}a{text-decoration:none}}@media(prefers-reduced-motion:reduce){*,::before,::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}}
/* css/components.css */
@layer components{.ui-panel,.ui-card{background:var(--ui-panel);border:1px solid var(--ui-border);padding:var(--ui-space);margin:var(--ui-space) 0;border-radius:var(--ui-radius)}.ui-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:.75rem}.ui-tag{display:inline-block;border:1px solid var(--ui-border);padding:.1rem .4rem}.ui-button,.ui-input,.ui-elements button,.ui-elements select,.ui-elements textarea,.ui-elements input:not([type=checkbox],[type=radio],[type=range],[type=color],[type=file]){font:inherit;background:var(--ui-panel);color:var(--ui-fg);border:1px solid var(--ui-border);padding:.6rem;border-radius:var(--ui-radius)}.ui-button,.ui-elements button{cursor:pointer}.ui-button:hover,.ui-elements button:hover{border-color:var(--ui-accent)}.ui-button:disabled,.ui-elements button:disabled{opacity:.4;cursor:default}.ui-elements input[type=range],.ui-elements input[type=checkbox],.ui-elements input[type=radio]{accent-color:var(--ui-accent)}.ui-elements label{color:var(--ui-muted)}.ui-muted{color:var(--ui-muted)}.ui-back{margin:0 0 8px;font-size:.875rem}.ui-back .ui-links{margin:0}.ui-back a{color:var(--ui-muted);text-decoration:none}.ui-back a:hover,.ui-back a:focus-visible{color:var(--ui-accent);text-decoration:underline}.ui-output{font:inherit;white-space:pre-wrap;overflow:auto;background:#d8dee4;color:#161b22;border:1px solid #8c959f;border-radius:4px;padding:.75rem}pre code,.ui-output code{font-family:inherit;color:inherit}pre.ui-output code{background:transparent}@media(max-width:480px){.ui-page{padding:.75rem}.ui-grid{grid-template-columns:1fr}.ui-card,.ui-panel{margin:.75rem 0;padding:.75rem}}.ui-lightbox{border:1px solid var(--ui-border);background:var(--ui-panel);color:var(--ui-fg);padding:1rem;max-width:min(96vw,960px);max-height:96vh;border-radius:var(--ui-radius)}.ui-lightbox::backdrop{background:rgba(0,0,0,.72)}.ui-lightbox img{display:block;max-width:100%;max-height:calc(96vh - 8rem);margin:auto}.ui-lightbox-bar{display:flex;gap:.5rem;justify-content:space-between;margin-top:.75rem}body:has(.ui-lightbox[open]){overflow:hidden}.ui-table,.ui-elements table{border-collapse:collapse;width:100%}.ui-table th,.ui-table td,.ui-elements th,.ui-elements td{border-bottom:1px solid var(--ui-border);padding:.25rem .5rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}.ui-table th,.ui-elements th{color:var(--ui-muted);font-weight:500}.ui-table caption,.ui-elements caption{text-align:left;color:var(--ui-muted);padding:.25rem 0}.ui-pass{color:var(--ui-accent)}.ui-fail{color:var(--ui-danger)}.ui-changed{background:color-mix(in srgb,var(--ui-accent) 18%,transparent)}.ui-tag.ui-pass{border-color:var(--ui-accent)}.ui-tag.ui-fail{border-color:var(--ui-danger)}}
/* css/themes/modern.css */
@layer theme{body[data-ui-theme="modern"]{color-scheme:dark}body[data-ui-theme="modern"] .ui-title::before,body[data-ui-theme="modern"] .ui-card>h2::before{content:"> ";color:var(--ui-accent)}body[data-ui-theme="modern"] .ui-panel,body[data-ui-theme="modern"] .ui-card{background:var(--ui-panel);box-shadow:4px 4px 0 rgba(88,166,255,.16)}body[data-ui-theme="modern"] .ui-tag:not(.ui-pass,.ui-fail)::before{content:"#";color:var(--ui-accent)}}
/* GitHub-like prioritizes familiar light GitHub visual cues while remaining a generic light theme. */
@layer theme{
body[data-ui-theme="github-like"]{
  --ui-bg:#ffffff;
  --ui-panel:#f6f8fa;
  --ui-fg:#1f2328;
  --ui-muted:#59636e;
  --ui-border:#d0d7de;
  --ui-accent:#0969da;
}
body[data-ui-theme="github-like"] .ui-panel,
body[data-ui-theme="github-like"] .ui-card{
  background:var(--ui-panel);
  border-radius:.375rem;
  box-shadow:none;
}
body[data-ui-theme="github-like"] .ui-button,
body[data-ui-theme="github-like"] .ui-input{
  background:#ffffff;
}
body[data-ui-theme="github-like"] .ui-title{
  border-bottom:1px solid var(--ui-border);
  padding-bottom:.5rem;
}
body[data-ui-theme="github-like"] .ui-tag{
  border-radius:999px;
  color:var(--ui-accent);
}
}

@layer components{.ui-scroll{min-width:0;max-width:100%;position:relative}.ui-scroll-row{display:flex;align-items:center;gap:8px;width:100%}.ui-scroll-row>[data-ui-scroll]{display:flex;flex:1 1 auto;min-width:0;max-width:100%;overflow-x:auto;overflow-y:hidden;flex-wrap:nowrap;gap:8px;white-space:nowrap;overscroll-behavior-x:contain;scrollbar-width:thin;scrollbar-color:var(--ui-muted) var(--ui-bg)}.ui-scroll-row>[data-ui-scroll]>*{flex:0 0 auto}.ui-scroll-arrow{flex:0 0 32px;width:32px;height:40px;min-height:40px;padding:0;font-size:24px;line-height:1;color:var(--ui-accent);background:var(--ui-panel);border:1px solid var(--ui-border);border-radius:var(--ui-radius);cursor:pointer}.ui-scroll-arrow:disabled{opacity:.35;cursor:default}.ui-scroll-row.ui-scroll-left::before,.ui-scroll-row.ui-scroll-right::after{content:"";pointer-events:none;position:absolute;top:0;bottom:0;width:16px;z-index:1}.ui-scroll-row.ui-scroll-left::before{left:40px;background:linear-gradient(to right,var(--ui-bg),transparent)}.ui-scroll-row.ui-scroll-right::after{right:40px;background:linear-gradient(to left,var(--ui-bg),transparent)}.ui-scroll-table>[data-ui-scroll]{max-height:64vh;max-height:64dvh;overflow:auto;overscroll-behavior-x:contain;scrollbar-gutter:stable}.ui-scroll-table>[data-ui-scroll] thead th{position:sticky;top:0;z-index:2;box-shadow:0 1px 0 var(--ui-border)}.ui-scroll-bar{display:flex;align-items:center;gap:8px;padding:8px;background:var(--ui-panel);border:1px solid var(--ui-border);border-bottom:0;border-radius:var(--ui-radius) var(--ui-radius) 0 0}.ui-scroll-over>[data-ui-scroll]{border-top-left-radius:0;border-top-right-radius:0}.ui-scroll-bar .ui-scroll-arrow{height:32px;min-height:32px}.ui-scroll-hint{font-size:.75rem;white-space:nowrap;color:var(--ui-muted)}.ui-scroll-top{flex:1 1 auto;min-width:0;height:24px;overflow-x:scroll;overflow-y:hidden;overscroll-behavior-x:contain;scrollbar-color:var(--ui-muted) var(--ui-bg)}.ui-scroll-spacer{height:1px}.ui-scroll :focus-visible{outline:2px solid var(--ui-accent);outline-offset:-2px}@media(max-width:700px){.ui-scroll-hint{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}}@media(prefers-reduced-motion:reduce){[data-ui-scroll],.ui-scroll-top{scroll-behavior:auto}}}
@layer components{.ui-records table.ui-table{margin:8px 0}.ui-records .ui-table th,.ui-records .ui-table td{border:thin solid var(--ui-border);padding:8px}.ui-records .ui-table caption{font-weight:600;padding:8px 0}.ui-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin:8px 0}.ui-stat .ui-stat-value{display:block;font-size:32px;line-height:40px}.ui-stat .ui-stat-label{display:block;color:var(--ui-muted)}.ui-stat .ui-stat-hint{display:block;font-size:.75rem;color:var(--ui-muted)}.ui-records-bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:8px 0}.ui-records-bar .ui-input{flex:1 1 240px}.ui-records-io{display:inline-flex;gap:8px}.ui-records [data-ui-draft]{width:100%;box-sizing:border-box}.ui-notice{border-left:8px solid var(--ui-border);padding:8px 16px;margin:8px 0;background:var(--ui-panel)}.ui-notice[data-tone=warn]{border-left-color:var(--ui-accent)}.ui-notice[data-tone=block]{border-left-color:var(--ui-danger)}.ui-code{position:relative;margin:8px 0}.ui-code pre{margin:0;padding:16px;padding-right:112px;white-space:pre-wrap;overflow-wrap:anywhere}.ui-code [data-ui-copy]{position:absolute;top:8px;right:8px}.ui-steps{display:grid;gap:16px}.ui-step[hidden]{display:none}.ui-step-head{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between}.ui-step-head h3{margin:0}.ui-step[data-status=doing] [data-ui-status-tag]{border-style:dashed;color:var(--ui-accent)}.ui-step[data-status=pass] [data-ui-status-tag]{color:var(--ui-accent)}.ui-step[data-status=block] [data-ui-status-tag]{color:var(--ui-danger)}.ui-step[data-status=todo] [data-ui-status-tag]{color:var(--ui-muted)}.ui-step[data-status=hold] [data-ui-status-tag]{border-style:dashed}.ui-facts{display:grid;grid-template-columns:minmax(96px,max-content) 1fr;gap:8px 16px;margin:8px 0}.ui-facts dt{color:var(--ui-muted)}.ui-facts dd{margin:0;white-space:pre-line}.ui-step-record{display:grid;gap:8px;margin-top:8px}.ui-step-record h4{margin:0}.ui-heading{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;justify-content:space-between;margin:8px 0 16px}.ui-heading h1{margin:0}.ui-eyebrow{color:var(--ui-muted);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;margin:0 0 8px}.ui-heading-lead{margin:8px 0 0;color:var(--ui-muted)}.ui-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}.ui-chips>*{border:thin solid var(--ui-border);border-radius:var(--ui-radius);padding:0 8px;color:var(--ui-fg);text-decoration:none}.ui-chips>a:hover{border-color:var(--ui-accent)}.ui-stamp{display:grid;gap:8px;min-width:160px;border:thin dashed var(--ui-border);border-radius:var(--ui-radius);padding:8px 16px;background:var(--ui-panel)}.ui-stamp b{font-size:1.25rem;color:var(--ui-accent)}.ui-stamp small{color:var(--ui-muted);white-space:pre-line}.ui-table tr[hidden]{display:none}@media(max-width:640px){.ui-facts{grid-template-columns:1fr}.ui-code pre{padding-right:16px;padding-top:56px}}}
@layer components{
.hm-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-bottom:var(--ui-space)}
.hm-head .ui-title{margin:0 0 .25rem}
.hm-head .ui-muted{margin:0}
.ui-layout-switch{display:inline-flex;flex-wrap:wrap;align-items:center;gap:.5rem;margin:0}
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

PSWB_HTML = {
    "theme_switch": '<label class="ui-layout-switch">テーマ <select data-ui-theme-switch><option value="modern" selected>🎨 modern</option><option value="github-like">🎨 github-like</option><option value="green">⬜ green</option><option value="red">⬜ red</option><option value="blue">⬜ blue</option><option value="purple">⬜ purple</option><option value="terminal">⬛ terminal</option></select></label>',
}

PSWB_JS = r"""/* ⬇️ pysaiyanweboo a55e8504 (ui.js, scroll.js): written by build_heatmap_bundle.py; --check fails when stale */
(() => {
/** Set text-only content. User-controlled values are never interpreted as HTML. */
function setText(target,value){const node=typeof target==="string"?document.querySelector(target):target;if(node)node.textContent=String(value)}
/** Serialize a value for human-readable text output. */
function prettyJson(value){return JSON.stringify(value,null,2)}
/** Copy a value as text; falls back to a hidden textarea where the async clipboard is missing (plain http, old WebViews). */
async function copyText(value){const text=String(value);try{await navigator.clipboard.writeText(text)}catch(error){const box=document.createElement("textarea");box.value=text;box.setAttribute("readonly","");box.style.cssText="position:fixed;opacity:0";try{document.body.append(box);box.select();if(typeof document.execCommand!=="function"||!document.execCommand("copy"))throw error}finally{box.remove()}}}
/** [data-ui-copy] copies the <pre> of its .ui-code box with copyText; the button shows data-ui-copied (or data-ui-copy-failed) for a moment. Returns the buttons. */
function bindCopy(root=document){const buttons=[...root.querySelectorAll("[data-ui-copy]")];for(const button of buttons){const box=button.closest(".ui-code"),pre=box&&box.querySelector("pre");if(!pre)continue;const label=button.textContent;button.addEventListener("click",async()=>{let ok=true;try{await copyText(pre.textContent)}catch{ok=false}button.textContent=(ok?button.dataset.uiCopied:button.dataset.uiCopyFailed)||label;setTimeout(()=>{button.textContent=label},1600)})}return buttons}
/** Buttons with data-ui-toggle flip aria-pressed on click (memory only: nothing is saved); data-label-on / data-label-off, when present, rename the button. */
function bindToggles(root=document){return[...root.querySelectorAll("[data-ui-toggle]")].map(b=>{const sync=()=>{const label=b.getAttribute("aria-pressed")==="true"?b.dataset.labelOn:b.dataset.labelOff;if(label){b.setAttribute("aria-label",label);b.title=label}};b.addEventListener("click",()=>{b.setAttribute("aria-pressed",String(b.getAttribute("aria-pressed")!=="true"));sync()});sync();return b})}
/** Switch data-ui-theme on <body> with no reload: controls are <select data-ui-theme-switch> or radios named ui-theme. The choice is remembered (localStorage, best effort) and marked on <body> as data-ui-theme-chosen. An empty-valued option means "the page's own theme" (data-ui-theme-page, by default the theme at bind time; see pageTheme): choosing it forgets the choice. Returns the theme in effect. */
function bindTheme(root=document,{key="web-ui-theme"}={}){const body=document.body,controls=[...root.querySelectorAll("[data-ui-theme-switch],input[name=ui-theme]")];const known=name=>controls.some(c=>c.tagName==="SELECT"?[...c.options].some(o=>o.value===name):c.value===name);if(body.dataset.uiThemePage===undefined)body.dataset.uiThemePage=body.dataset.uiTheme||"";const sync=()=>{const chosen=body.dataset.uiThemeChosen;for(const c of controls){if(c.tagName==="SELECT")c.value=chosen===undefined&&[...c.options].some(o=>o.value==="")?"":body.dataset.uiTheme;else c.checked=c.value===body.dataset.uiTheme}};const choose=name=>{if(name){body.dataset.uiThemeChosen=name;body.dataset.uiTheme=name}else{delete body.dataset.uiThemeChosen;body.dataset.uiTheme=body.dataset.uiThemePage}};let saved=null;try{saved=localStorage.getItem(key)}catch{}if(saved&&known(saved))choose(saved);sync();for(const c of controls)c.addEventListener("change",()=>{if(!known(c.value))return;choose(c.value);sync();try{if(c.value)localStorage.setItem(key,c.value);else localStorage.removeItem(key)}catch{}});return body.dataset.uiTheme}
/** Tell bindTheme which theme is the page's own (a page whose own look changes, such as display modes): it shows unless the visitor chose one. Returns the theme in effect. */
function pageTheme(name){const body=document.body;body.dataset.uiThemePage=name;if(body.dataset.uiThemeChosen===undefined)body.dataset.uiTheme=name;return body.dataset.uiTheme}
/** Mark on-screen elements with data-lit (IntersectionObserver); CSS decides what lit looks like. Without IntersectionObserver every element counts as lit. Returns a stop function. */
function observeLit(targets,{threshold=0.4,root=null}={}){const nodes=typeof targets==="string"?[...document.querySelectorAll(targets)]:[...targets];if(typeof IntersectionObserver==="undefined"){for(const n of nodes)n.dataset.lit="";return()=>{}}const io=new IntersectionObserver(entries=>{for(const e of entries){if(e.isIntersecting)e.target.dataset.lit="";else delete e.target.dataset.lit}},{threshold,root});for(const n of nodes)io.observe(n);return()=>io.disconnect()}
/** Click-to-enlarge for <a href="full.png"><img alt="..."></a> items inside [data-ui-lightbox]: one <dialog>; Esc, the backdrop and the close button shut it, arrows, buttons and a 48px swipe step through. Returns {open, close, dialog}, or null without items or <dialog>. */
function bindLightbox(root=document){const items=[...root.querySelectorAll("[data-ui-lightbox] a[href]")];if(!items.length||typeof HTMLDialogElement==="undefined")return null;const dialog=document.createElement("dialog");dialog.className="ui-lightbox";dialog.setAttribute("aria-label","Image viewer");dialog.innerHTML='<img alt=""><p class="ui-muted"></p><div class="ui-lightbox-bar"><button class="ui-button" type="button" data-step="-1" aria-label="Previous">\u2190</button><button class="ui-button" type="button" data-step="1" aria-label="Next">\u2192</button><button class="ui-button" type="button" data-step="0" aria-label="Close">\u00d7</button></div>';const img=dialog.querySelector("img"),note=dialog.querySelector("p");let at=0,x=null;const show=i=>{at=(i+items.length)%items.length;const a=items[at],t=a.querySelector("img");img.src=a.href;img.alt=note.textContent=t?t.alt:""};const open=i=>{show(i);if(!dialog.open)dialog.showModal()};items.forEach((a,i)=>a.addEventListener("click",e=>{e.preventDefault();open(i)}));dialog.addEventListener("click",e=>{const b=e.target.closest("[data-step]");if(b){const s=Number(b.dataset.step);if(s)show(at+s);else dialog.close()}else if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});dialog.addEventListener("keydown",e=>{if(e.key==="ArrowLeft")show(at-1);if(e.key==="ArrowRight")show(at+1)});dialog.addEventListener("pointerdown",e=>{x=e.clientX});dialog.addEventListener("pointerup",e=>{if(x!==null&&Math.abs(e.clientX-x)>=48)show(at+(e.clientX<x?1:-1));x=null});document.body.append(dialog);return{open,close:()=>dialog.close(),dialog}}

/* web-ui scroll: ‹ › buttons, edge fades and (tables) a top scrollbar for every [data-ui-scroll="row"|"table"] (scroll_html). No dependencies, nothing stored or sent; scroll.css draws it. */
const mounted=new WeakSet(),states=new Set();
let identity=0,scheduled=false,watching=false;
const LABELS={row:"横スクロール",table:"表",suffix:"（横スクロール）",hint:"表を横に移動",top:"表ヘッダーの横スクロール",left:"を左へスクロール",right:"を右へスクロール"};
function refreshScroll(){
  scheduled=false;
  for(const state of states){
    if(!state.viewport.isConnected){state.observer?.disconnect();states.delete(state);continue}
    const {viewport,shell,toolbar,top,spacer,previous,next}=state;
    const maximum=Math.max(0,viewport.scrollWidth-viewport.clientWidth),overflow=maximum>1;
    shell.classList.toggle("ui-scroll-over",overflow);
    shell.classList.toggle("ui-scroll-left",overflow&&viewport.scrollLeft>1);
    shell.classList.toggle("ui-scroll-right",overflow&&viewport.scrollLeft<maximum-1);
    previous.disabled=!overflow||viewport.scrollLeft<=1;
    next.disabled=!overflow||viewport.scrollLeft>=maximum-1;
    if(previous.hidden!==!overflow)previous.hidden=!overflow;
    if(next.hidden!==!overflow)next.hidden=!overflow;
    if(toolbar){
      if(toolbar.hidden!==!overflow)toolbar.hidden=!overflow;
      // Both scrollbars need the same range, even though the toolbar also holds the buttons.
      spacer.style.width=`${maximum+top.clientWidth}px`;
      if(Math.abs(top.scrollLeft-viewport.scrollLeft)>1)top.scrollLeft=viewport.scrollLeft;
    }
  }
}
const schedule=()=>{if(!scheduled){scheduled=true;requestAnimationFrame(refreshScroll)}};
function bindKeys(control,viewport){
  control.addEventListener("keydown",event=>{
    // Text fields, selects and other children keep their own arrow / Home / End keys.
    if(event.target!==control||event.altKey||event.ctrlKey||event.metaKey||event.shiftKey)return;
    if(event.key==="ArrowLeft"||event.key==="ArrowRight")viewport.scrollLeft+=event.key==="ArrowLeft"?-100:100;
    else if(event.key==="Home")viewport.scrollLeft=0;
    else if(event.key==="End")viewport.scrollLeft=viewport.scrollWidth;
    else return;
    event.preventDefault();
    if(control!==viewport)control.scrollLeft=viewport.scrollLeft;
    schedule();
  });
}
function enhance(viewport,labels){
  if(mounted.has(viewport))return;
  mounted.add(viewport);
  const table=viewport.dataset.uiScroll==="table",label=viewport.dataset.scrollLabel||(table?labels.table:labels.row);
  const shell=document.createElement("div");
  shell.className=table?"ui-scroll ui-scroll-table":"ui-scroll ui-scroll-row";
  viewport.before(shell);shell.append(viewport);
  if(!viewport.id)viewport.id=`ui-scroll-${++identity}`;
  if(!viewport.hasAttribute("tabindex"))viewport.tabIndex=0;
  if(!viewport.hasAttribute("aria-label"))viewport.setAttribute("aria-label",label+labels.suffix);
  if(table)viewport.setAttribute("role","region");
  const state={viewport,shell};
  const arrow=direction=>{
    const button=document.createElement("button");
    button.type="button";button.className="ui-scroll-arrow";button.textContent=direction<0?"‹":"›";
    button.setAttribute("aria-label",label+(direction<0?labels.left:labels.right));
    button.setAttribute("aria-controls",viewport.id);
    button.addEventListener("click",()=>viewport.scrollBy({left:direction*Math.max(120,viewport.clientWidth*.7),behavior:"auto"}));
    return button;
  };
  state.previous=arrow(-1);state.next=arrow(1);
  if(table){
    const toolbar=document.createElement("div"),hint=document.createElement("span"),top=document.createElement("div"),spacer=document.createElement("div");
    toolbar.className="ui-scroll-bar";hint.className="ui-scroll-hint";hint.textContent=labels.hint;
    top.className="ui-scroll-top";top.tabIndex=0;top.setAttribute("role","region");top.setAttribute("aria-label",labels.top);top.setAttribute("aria-controls",viewport.id);
    spacer.className="ui-scroll-spacer";top.append(spacer);
    toolbar.append(hint,state.previous,top,state.next);shell.prepend(toolbar);
    Object.assign(state,{toolbar,top,spacer});
    top.addEventListener("scroll",()=>{if(Math.abs(viewport.scrollLeft-top.scrollLeft)>1)viewport.scrollLeft=top.scrollLeft;schedule()},{passive:true});
    bindKeys(top,viewport);
  }else{shell.prepend(state.previous);shell.append(state.next)}
  viewport.addEventListener("scroll",schedule,{passive:true});
  viewport.addEventListener("focusin",event=>{
    if(event.target===viewport)return;
    const bounds=viewport.getBoundingClientRect(),target=event.target.getBoundingClientRect();
    if(target.left<bounds.left)viewport.scrollLeft+=target.left-bounds.left;
    else if(target.right>bounds.right)viewport.scrollLeft+=target.right-bounds.right;
    schedule();
  });
  bindKeys(viewport,viewport);
  if(typeof ResizeObserver!=="undefined"){
    state.observer=new ResizeObserver(schedule);state.observer.observe(viewport);
    for(const child of viewport.children)state.observer.observe(child);
  }
  states.add(state);
}
/* Enhance every region under root, now and as the page adds more (one observer per page). labels overrides LABELS (another language). */
function bindScroll(root=document,options={}){
  const labels={...LABELS,...(options.labels||{})};
  const mount=()=>{root.querySelectorAll('[data-ui-scroll="row"],[data-ui-scroll="table"]').forEach(v=>enhance(v,labels));schedule()};
  if(!watching){
    watching=true;
    new MutationObserver(mutations=>{if(mutations.some(m=>m.type==="childList"))mount();else schedule()})
      .observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:["open","hidden"]});
    window.addEventListener("resize",schedule,{passive:true});
    document.addEventListener("toggle",schedule,true);
    document.addEventListener("load",schedule,true);
  }
  mount();
  return {mount,refresh:refreshScroll};
}
if(typeof document!=="undefined")bindScroll();

globalThis.PySaiyanWeBoo = { setText, prettyJson, copyText, bindTheme, pageTheme, bindToggles, bindScroll, refreshScroll };
})();
/* ⬆️ pysaiyanweboo */"""
