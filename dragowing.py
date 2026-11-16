"""Count HTML elements with html.parser (no browser), and 📊 draw FluidFullSpeedSimulation's still figures.

➡️ DRAgoWing's single file (stdlib only). The generic stdlib parts of the package (plotly_cdn, chrome_pipe /
render / export, records) move in here at the next Aoi sync; NPB-specific report modules go to npb/ and the
generic overlap internals to core/ (README "Layout").

📊 FFSS draws flows that change over time as GIFs; the still figures (Sankey, waterfall, T–Q, balance point,
start-up Gantt, sensitivity tornado, window heatmap) are drawn here from its ``--jsonl`` records, without
re-judging them: ``ffss_figures`` builds plotly figure JSON, ``write_ffss`` writes an HTML page (plotly.js) and
SVG files (the parent's stdlib ``plotly_min``, no Chrome).
"""

from __future__ import annotations

import importlib.util, json
from html import escape
from html.parser import HTMLParser
from pathlib import Path


class _Counter(HTMLParser):
    def __init__(self, names: set[str] | None):
        super().__init__()
        self.names = names
        self.counts: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.names is not None and tag not in self.names:
            return
        self.counts[tag] = self.counts.get(tag, 0) + 1


def count_elements(html: str, tag_names: tuple[str, ...] | None = None) -> dict[str, int]:
    """Return a map of tag name to open-tag count. ``tag_names`` limits which tags are counted."""
    names = set(tag_names) if tag_names else None
    parser = _Counter(names)
    parser.feed(html)
    parser.close()
    return parser.counts


# --- 📊 FluidFullSpeedSimulation (FFSS) records → still figures ----------------------------------------

# (F<NN> identifier, the FFSS (experiment, run) rows it reads). The order is the F number.
FFSS_FIGURES = (("energy-coal", (("E31", "energy:coal"),)), ("energy-gtcc", (("E31", "energy:lng"),)),
                ("losses", (("E31", "energy:coal"), ("E31", "energy:lng"))), ("pinch-tq", (("E31", "tq"),)),
                ("balance-point", (("E32", "balance"),)), ("startup", (("E31", "startup"),)),
                ("sensitivity", (("E31", "sensitivity"),)), ("rate-window", (("E31", "rate-window"),)),
                ("blood-flow", (("E30", "blood"),)))
_COLORS = {"heat": "#FFA15A", "water": "#19d3f3", "power": "#00cc96", "loss": "#9aa0a6", "heart": "#EF553B",
           "organ": "#FF6692", "vein": "#636efa", "lung": "#ab63fa"}
_PLANT = {"coal": "🪨", "lng": "🌀"}


def read_ffss(path) -> dict[tuple[str, str], list[dict]]:
    """FFSS の ``run`` / ``verify --jsonl`` の記録を (実験 ID, run) ごとの行に（記録の順のまま）。"""
    out: dict[tuple[str, str], list[dict]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out.setdefault((row["id"], row["run"]), []).append(row)
    return out


def _rgba(color: str, alpha: float) -> str:
    h = color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha:g})"


def _fig(title: str, data: list, **layout) -> dict:
    """720×448 px（8 の倍数）、余白も 8 の倍数。文字は plotly_min の既定（メイリオ）。"""
    layout = {"title": {"text": title}, "width": 720, "height": 448,
              "margin": layout.pop("margin", {"l": 72, "r": 32, "t": 64, "b": 64}), **layout}
    return {"data": data, "layout": layout}


def _sankey(title: str, rows: list[dict]) -> dict:
    """リンクの行（source・target・組・value・unit）からサンキー図。ノードは出てきた順、ラベルは 名前 + 入りと出の大きい方。"""
    names: dict[str, str] = {}
    for r in rows:
        names.setdefault(r["source"], r["source_group"])
        names.setdefault(r["target"], r["target_group"])
    order = list(names)
    size = {n: max(sum(r["value"] for r in rows if r["source"] == n), sum(r["value"] for r in rows if r["target"] == n))
            for n in order}
    return _fig(title, [{"type": "sankey",  # 単位（% ・L/min）は題に書く
                         "node": {"label": [f"{n} {size[n]:.1f}" for n in order],
                                  "color": [_COLORS[names[n]] for n in order], "pad": 16, "thickness": 16},
                         "link": {"source": [order.index(r["source"]) for r in rows],
                                  "target": [order.index(r["target"]) for r in rows],
                                  "value": [r["value"] for r in rows],
                                  "color": [_rgba(_COLORS[r["target_group"]], 0.35) for r in rows]}}],
                margin={"l": 16, "r": 16, "t": 64, "b": 24})


def _losses(coal: list[dict], lng: list[dict]) -> dict:
    data = []
    for icon, rows in (("🪨", coal), ("🌀", lng)):
        loss = [r for r in rows if r["target_group"] == "loss"]
        grid = next(r["value"] for r in rows if r["target"] == "送電端")
        steps = [100.0, *(-r["value"] for r in loss), grid]
        data.append({"type": "waterfall", "name": icon, "x": [f"{icon} {n}" for n in ("燃料", *(r["target"] for r in loss), "送電端")],
                     "y": steps, "measure": ["absolute", *["relative"] * len(loss), "total"],
                     "text": [f"{abs(v):.1f}" for v in steps]})
    return _fig("🪜 燃料 100 から送電端まで（損を順に引く）", data, showlegend=False, yaxis={"title": {"text": "燃料 100 に対する割合"}, "range": [0, 112]},
                xaxis={"tickangle": -30}, margin={"l": 72, "r": 32, "t": 64, "b": 104})


def _pinch(rows: list[dict]) -> dict:
    gas = [r for r in rows if r["stream"] == "gas"]
    water = [r for r in rows if r["stream"] == "water"]
    fig = _fig("🌡️ 🌀 排熱回収ボイラの T–Q 線図（3 圧・再熱）", [
        {"type": "scatter", "mode": "lines", "name": "ガス（GT の排気）", "x": [r["q_mw"] for r in gas],
         "y": [r["t_c"] for r in gas], "line": {"color": "#EF553B", "width": 3}},
        {"type": "scatter", "mode": "lines", "name": "水・蒸気（3 圧の合成）", "x": [r["q_mw"] for r in water],
         "y": [r["t_c"] for r in water], "line": {"color": "#636efa", "width": 3}}],
        xaxis={"title": {"text": "煙突の側から渡した熱 [MW]"}}, yaxis={"title": {"text": "温度 [°C]"}, "range": [0, 650]})
    names = {"lp": "低圧", "ip": "中圧", "hp": "高圧"}
    for r in (r for r in rows if r["stream"] == "pinch"):
        fig["layout"].setdefault("shapes", []).append({"type": "line", "x0": r["q_mw"], "x1": r["q_mw"], "y0": r["t_c"],
                                                       "y1": r["t_gas_c"], "line": {"color": "#444", "width": 1, "dash": "dot"}})
        fig["layout"].setdefault("annotations", []).append({"x": r["q_mw"], "y": r["t_gas_c"] + 28, "showarrow": False,
                                                            "text": f"{names[r['drum']]} ΔT {r['dt_k']:.1f} K"})
    return fig


def _balance(rows: list[dict]) -> dict:
    curve = [r for r in rows if r["kind"] == "curve"]
    cat = [r for r in rows if r["kind"] == "catalog"]
    bal = next(r["t_out"] for r in rows if r["kind"] == "balance" and not r["iso"])
    ts = [r["t_out"] for r in curve]
    fig = _fig("✖️ 🏠 最大暖房出力と家の暖房負荷（交点 = バランス点）", [
        {"type": "scatter", "mode": "lines", "name": "最大暖房出力（× 除霜）", "x": ts, "y": [r["max_kw"] for r in curve],
         "line": {"color": "#EF553B", "width": 3}},
        {"type": "scatter", "mode": "lines", "name": "家の負荷（JIS）", "x": ts, "y": [r["load_jis_kw"] for r in curve],
         "line": {"color": "#636efa"}},
        {"type": "scatter", "mode": "lines", "name": "家の負荷（ISO 16358-2）", "x": ts, "y": [r["load_iso_kw"] for r in curve],
         "line": {"color": "#636efa", "dash": "dash"}},
        {"type": "scatter", "mode": "markers", "name": "カタログの低温の最大能力", "x": [r["t_out"] for r in cat],
         "y": [r["max_kw"] for r in cat], "marker": {"color": "#444", "size": 10, "symbol": "diamond"}}],
        xaxis={"title": {"text": "外気 [°C]"}}, yaxis={"title": {"text": "暖房 [kW]"}, "range": [0, 10]})
    fig["layout"]["shapes"] = [{"type": "line", "x0": bal, "x1": bal, "xref": "x", "y0": 0, "y1": 1, "yref": "y domain",
                                "line": {"color": "#444", "width": 1, "dash": "dot"}}]
    fig["layout"]["annotations"] = [{"x": bal, "y": 9.3, "showarrow": False, "xanchor": "left",
                                     "text": f"バランス点 {bal:.1f} °C".replace("-", "−")}]
    return fig


def _startup(rows: list[dict]) -> dict:
    keys = [(p, s) for p in ("lng", "coal") for s in ("cold", "hot")]
    labels = [f"{_PLANT[p]} {s}" for p, s in keys]
    phase = {(r["plant"], r["start"], r["phase"]): r for r in rows}
    names = {"steps": ("手順", _COLORS["loss"]), "warmup": ("🧱 暖機", "#EF553B"), "ramp": ("負荷上げ", _COLORS["power"])}
    data = [{"type": "bar", "orientation": "h", "name": name, "y": labels, "marker": {"color": color},
             "base": [phase[(p, s, k)]["from_min"] for p, s in keys],
             "x": [phase[(p, s, k)]["to_min"] - phase[(p, s, k)]["from_min"] for p, s in keys]}
            for k, (name, color) in names.items()]
    for i, (p, s) in enumerate(keys):
        r = phase[(p, s, "steps")]
        data.append({"type": "scatter", "mode": "markers", "name": "Agora の起動時間（並列まで）", "showlegend": i == 0,
                     "x": [r["agora_lo_min"], r["agora_hi_min"]], "y": [labels[i]] * 2,
                     "marker": {"color": "#444", "size": 10, "symbol": "diamond"}})
    at = rows[0]["at"] if rows else 0.5
    return _fig(f"📅 🌅 起動の手順と時間（出典の範囲の at = {at:g}）", data, barmode="overlay",
                xaxis={"title": {"text": "止めてからの時間 [分]"}})


def _assumption(r: dict) -> str:
    icon, name = {"pinch": ("📍", "pinch"), "metal-rate": ("🧱", "温め直し"), "metal-tau": ("🧱", "τ"),
                  "compressor-eta": ("🫧", "圧縮機の効率"), "boiler": ("🪨", "ボイラ")}.get(r["assumption"], ("🎚️", r["assumption"]))
    lo, hi, unit = r["lo"], r["hi"], r["unit"]
    span = f"{lo * 100:g}〜{hi * 100:g} %" if r["assumption"] == "boiler" else f"{lo:g}〜{hi:g}" + (f" {unit}" if unit else "")
    return f"{icon} {name} {span}" + ("" if r["source_range"] else "（幅は仮）")


def _tornado(rows: list[dict]) -> dict:
    spans: dict[str, list[dict]] = {}
    for r in rows:
        spans.setdefault(r["assumption"], []).append(r)
    items = sorted(spans.values(), key=lambda v: max(r["metric"] for r in v) - min(r["metric"] for r in v))
    names = [_assumption(v[0]) for v in items]
    lo = [min(r["metric"] for r in v if not r["use"]) for v in items]
    hi = [max(r["metric"] for r in v if not r["use"]) for v in items]
    use = [next(r["metric"] for r in v if r["use"]) for v in items]
    fig = _fig("🌪️ 🎚️ 仮定を振ったときの 🔮 のずれ（1 を超えると外れる）", [
        {"type": "bar", "orientation": "h", "name": "幅の中", "y": names, "base": lo, "x": [b - a for a, b in zip(lo, hi)],
         "marker": {"color": [_COLORS["power"] if b <= 1.0 else _COLORS["heat"] for b in hi]}},
        {"type": "scatter", "mode": "markers", "name": "使った値", "x": use, "y": names,
         "marker": {"color": "#444", "size": 10, "symbol": "diamond"}}],
        xaxis={"title": {"text": "ずれ ÷ 許容"}}, showlegend=False, margin={"l": 216, "r": 32, "t": 64, "b": 64})
    fig["layout"]["shapes"] = [{"type": "line", "x0": 1.0, "x1": 1.0, "xref": "x", "y0": 0, "y1": 1, "yref": "y domain",
                                "line": {"color": "#EF553B", "width": 2, "dash": "dash"}}]
    return fig


def _window(rows: list[dict], use: tuple[float, float] = (2.0, 70.0)) -> dict:
    rates = sorted({r["rate_k_min"] for r in rows})
    taus = sorted({r["tau_h"] for r in rows})
    z = {(r["tau_h"], r["rate_k_min"]): min(r["metric"], 3.0) for r in rows}
    return _fig("🧱 cold の起動が Agora の範囲に入る窓（1 以下 = 中）", [
        {"type": "heatmap", "x": rates, "y": taus, "z": [[z[(t, x)] for x in rates] for t in taus], "zmin": 0.0, "zmax": 3.0,
         "colorbar": {"title": {"text": "ずれ ÷ 半幅"}},
         "colorscale": [[0.0, "#2166ac"], [1 / 3, "#f7f7f7"], [1.0, "#b2182b"]]},
        {"type": "scatter", "mode": "markers", "name": "使った値", "x": [use[0]], "y": [use[1]],
         "marker": {"color": "#444", "size": 12, "symbol": "diamond"}}],
        xaxis={"title": {"text": "温め直しの速さ [K/min]"}}, yaxis={"title": {"text": "τ [h]"}}, showlegend=False,
        margin={"l": 72, "r": 96, "t": 64, "b": 64})


def ffss_figures(records: dict[tuple[str, str], list[dict]]) -> dict[str, dict]:
    """F<NN>_<識別子> → plotly の図 JSON（data・layout）。記録の値を並べるだけで、判定はやり直さない。"""
    get = records.get
    build = {"energy-coal": lambda: _sankey("🔀 🪨 石炭火力（USC）: 燃料 100 の行き先（1 段目の割合）", get(("E31", "energy:coal"))),
             "energy-gtcc": lambda: _sankey("🔀 🌀 LNG 複合（GTCC）: 燃料 100 の行き先（1 段目の割合）", get(("E31", "energy:lng"))),
             "losses": lambda: _losses(get(("E31", "energy:coal")), get(("E31", "energy:lng"))),
             "pinch-tq": lambda: _pinch(get(("E31", "tq"))), "balance-point": lambda: _balance(get(("E32", "balance"))),
             "startup": lambda: _startup(get(("E31", "startup"))), "sensitivity": lambda: _tornado(get(("E31", "sensitivity"))),
             "rate-window": lambda: _window(get(("E31", "rate-window"))),
             "blood-flow": lambda: _sankey("🔀 🫀 心拍出量の行き先（L/min）", get(("E30", "blood")))}
    out = {}
    for n, (name, needs) in enumerate(FFSS_FIGURES, 1):
        if all(records.get(k) for k in needs):  # 記録に無い図は描かない（run E31 だけの記録でもよい）
            out[f"F{n:02d}_{name}"] = build[name]()
    return out


def plotly_min():
    """vendor/tools/stdlib_min/plotly_min.py（親の stdlib_min を vendor.lock.json で固定）。名前は子どうしでぶつからないように。"""
    path = Path(__file__).resolve().parent / "vendor" / "tools" / "stdlib_min" / "plotly_min.py"
    if not path.is_file():
        raise FileNotFoundError(f"plotly_min が無い: {path}（DRAgoWing のリポジトリから動かす）")
    spec = importlib.util.spec_from_file_location("dragowing_plotly_min", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_ffss(records_path, out_dir, *, svg: bool = True) -> list[Path]:
    """📊 FFSS の記録から ffss.html（plotly.js）と svg/F<NN>_<識別子>.svg（plotly_min、Chrome なし）を書く。"""
    pm = plotly_min()
    figs = ffss_figures(read_ffss(records_path))
    if not figs:
        raise ValueError("FFSS の図にする記録が無い（run E30・E31・E32 か verify の --jsonl）")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blocks = "".join(f'<section><h2>{escape(name)}</h2>{pm.Figure(spec).to_html(include_plotlyjs=False, full_html=False, div_id=name)}</section>'
                     for name, spec in figs.items())
    page = (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>📊 FFSS の図</title>'
            f'<script src="https://cdn.plot.ly/plotly-{pm.PLOTLY_JS}.min.js" charset="utf-8"></script>'
            f'<style>body{{font-family:{pm.FONT};margin:16px}}h2{{font-size:16px}}</style></head>'
            f'<body><h1>📊 FFSS の図（記録から）</h1>{blocks}</body></html>\n')
    written = [out / "ffss.html"]
    written[0].write_text(page, encoding="utf-8")
    if svg:
        (out / "svg").mkdir(exist_ok=True)
        for name, spec in figs.items():
            path = out / "svg" / f"{name}.svg"
            path.write_bytes(pm.Figure(spec).to_image("svg"))
            written.append(path)
    return written


def main(argv=None) -> int:
    """Count elements in a saved HTML document or stdin, or 📊 draw FFSS records (``--ffss``)."""
    import argparse
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Count HTML elements in a saved document (stdlib only).")
    parser.add_argument("file", nargs="?", help="HTML file; omit or use - to read stdin")
    parser.add_argument("--tag", action="append", default=[], help="Limit to a tag; may be repeated")
    parser.add_argument("--ffss", type=Path, metavar="RECORDS",
                        help="📊 FFSS の --jsonl の記録から ffss.html と svg/F<NN>_*.svg を書く（Chrome なし）")
    parser.add_argument("--out", type=Path, default=Path("build/ffss"), help="📊 --ffss の書き出し先")
    parser.add_argument("--no-svg", action="store_true", help="📊 --ffss で HTML だけ")
    args = parser.parse_args(argv)
    if args.ffss is not None:
        try:
            written = write_ffss(args.ffss, args.out, svg=not args.no_svg)
        except (OSError, ValueError, KeyError) as exc:
            parser.exit(1, f"Cannot draw FFSS records: {exc}\n")
        for path in written:
            print(f"{'🖼️' if path.suffix == '.svg' else '📄'} {path.resolve().as_uri()} {path.stat().st_size} B")
        return 0
    try:
        html = sys.stdin.read() if not args.file or args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"Cannot read HTML: {exc}\n")
    print(json.dumps(count_elements(html, tuple(tag.lower() for tag in args.tag)), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
