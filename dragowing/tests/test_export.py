"""Config-driven export, including complete local Plotly figures offline."""
import hashlib
import json
import os
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from dataclasses import replace
from pathlib import Path

import pytest

from vendor import web_ui

from dragowing.export import MERMAID, PLOTLY, export_draw, mermaid_diagram_content, page_html, plotly_figure_content, plotlyjs_bundle_path
from dragowing.html_tag_count import count_elements
from dragowing.render import RenderSession, Timeouts


def test_page_html_builds_plotly_and_mermaid_without_browser(tmp_path):
    # Page assembly does not require Chrome.
    bundle = tmp_path / "plotly.min.js"
    bundle.write_text("window.Plotly={};", encoding="utf-8")
    config = replace(PLOTLY, local_scripts=(lambda: bundle,))
    page = page_html(config, plotly_figure_content({"data": [], "layout": {"title": {"text": "t"}}}))
    assert bundle.as_uri() in page
    assert 'src="https://' not in page
    assert "Plotly.newPlot" in page
    assert count_elements(page, ("script", "div")) == {"script": 3, "div": 1}
    mermaid = page_html(MERMAID, mermaid_diagram_content("graph TD\n  A-->B"))
    assert "mermaid.min.js" in mermaid
    assert "graph TD" in mermaid
    assert count_elements(mermaid, ("pre", "script")) == {"pre": 1, "script": 2}


def test_fmt_is_png_or_svg(tmp_path):
    with pytest.raises(ValueError, match="png or svg"):
        export_draw(PLOTLY, plotly_figure_content({"data": []}), tmp_path / "out.gif", "gif")


def test_plotly_text_cannot_close_inline_script():
    page = plotly_figure_content({"data": [], "layout": {"title": {"text": '</script><div id="oops">'}}})
    assert page.count("</script>") == 1
    assert "\\u003c/script>" in page


def test_bundle_copied_from_cdn_contract_and_lives_through_render(tmp_path):
    from dragowing import export
    source = tmp_path / "plotly.min.js"
    source.write_bytes(b"cdn-bundle-v1")
    config = replace(PLOTLY, local_scripts=(lambda: source,))
    copies = []
    class Session:
        def render(self, page, *args, **kwargs):
            from html.parser import HTMLParser
            class Scripts(HTMLParser):
                def handle_starttag(self, tag, attrs):
                    if tag == "script" and dict(attrs).get("src"):
                        from urllib.parse import unquote, urlparse
                        copies.append(Path(unquote(urlparse(dict(attrs)["src"]).path)))
            Scripts().feed(page)
            assert copies[-1] != source
            assert copies[-1].read_bytes() == source.read_bytes()
            return b"captured"
    for version in (b"cdn-bundle-v1", b"cdn-bundle-v2"):
        source.write_bytes(version)
        assert export.export_draw(config, "", tmp_path / "out.png", session=Session()) == b"captured"
        assert not copies[-1].exists()
    assert copies[0] != copies[1]


def test_missing_bundle_fails_without_writing_output(tmp_path):
    def missing():
        raise FileNotFoundError("plotly.min.js missing")
    out = tmp_path / "out.png"
    with pytest.raises(FileNotFoundError, match="plotly.min.js"):
        export_draw(replace(PLOTLY, local_scripts=(missing,)), "", out)
    assert not out.exists()


def _check_png(data, width, height):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset, compressed = 8, []
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        tag, payload = data[offset + 4:offset + 8], data[offset + 8:offset + 8 + length]
        crc = struct.unpack(">I", data[offset + 8 + length:offset + 12 + length])[0]
        assert zlib.crc32(tag + payload) == crc
        if tag == b"IHDR":
            assert struct.unpack(">II", payload[:8]) == (width, height)
        if tag == b"IDAT":
            compressed.append(payload)
        offset += length + 12
    # A blank/transparent page cannot provide this many distinct channel deltas.
    assert len(set(zlib.decompress(b"".join(compressed)))) > 32


def _page_targets(browser):
    # Full Chrome can start component extension service workers asynchronously.
    # Compare page identities, so a leaked render page cannot hide behind churn.
    return {t["targetId"] for t in browser.call("Target.getTargets")["targetInfos"] if t["type"] == "page"}


def test_export_draw_plotly_three_figures_in_one_session(tmp_path, plotly_chrome_executable):
    evidence = os.environ.get("DRAGOWING_EXPORT_EVIDENCE_DIR")
    if evidence:
        tmp_path = Path(evidence)
        tmp_path.mkdir(parents=True, exist_ok=True)
    figures = [
        {
            "data": [{"type": "scatter", "x": [1, 2, 3], "y": [index, 1, 4],
                      "mode": "lines+markers", "name": "series-%d" % index,
                      "marker": {"color": "red", "size": 12}}],
            "layout": {"width": 400, "height": 300, "showlegend": True,
                       "title": {"text": "title-%d" % index}},
        }
        for index in range(3)
    ]
    with RenderSession(chrome=plotly_chrome_executable, offline=True) as session:
        pid = session.browser._proc.pid
        baseline = _page_targets(session.browser)
        if evidence:
            (tmp_path / "runtime.json").write_text(json.dumps({
                "python": sys.version, "plotly_js": _js_version(),
                "chrome": session.browser.call("Browser.getVersion"),
                "network": "CDP offline; CI additionally runs in an isolated network namespace",
                "figure_count": 3, "formats": ["png", "svg"],
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        png_hashes = set()
        for index, fig in enumerate(figures):
            for fmt in ("png", "svg"):
                path = tmp_path / ("fig-%s.%s" % (index, fmt))
                data = export_draw(PLOTLY, plotly_figure_content(fig), path, fmt, session=session)
                assert data == path.read_bytes()
                assert session.browser._proc.pid == pid
                assert _page_targets(session.browser) == baseline
                if fmt == "svg":
                    root = ET.fromstring(data)
                    text = "".join(root.itertext())
                    assert root.tag == "{http://www.w3.org/2000/svg}svg"
                    assert "title-%d" % index in text
                    assert "series-%d" % index in text
                    points = [el for el in root.iter() if el.get("class") == "point"]
                    assert len(points) == 3
                else:
                    _check_png(data, 400, 300)
                    png_hashes.add(hashlib.sha256(data).hexdigest())
        assert len(png_hashes) == 3
        # CDP offline mode must actually reject network fetches, while the exact
        # bundled Plotly.js version still renders from the filesystem.
        probe = replace(PLOTLY, ready_expression=(
            "window.__dragowing_ready.then(async()=>{"
            "if(Plotly.version!==%s)throw Error('wrong Plotly.js');"
            "if(navigator.onLine!==false)throw Error('page still online');"
            "try{await fetch('https://example.invalid/offline-probe');}"
            "catch(e){return true;}throw Error('network unexpectedly available');})"
        ) % json.dumps(_js_version()))
        export_draw(probe, plotly_figure_content(figures[0]), tmp_path / "probe.svg", "svg", session=session)


def _js_version():
    return web_ui.PLOTLY_JS_VERSION


def test_plotlyjs_bundle_path_materializes_verified_cdn_bytes(tmp_path, monkeypatch):
    body = b"window.Plotly={version:'test'};"
    bundle = tmp_path / "plotly.min.js"
    bundle.write_bytes(body)
    monkeypatch.setenv("DRAGOWING_PINNED_PLOTLY_JS", str(bundle))
    assert plotlyjs_bundle_path() == bundle
    page = page_html(PLOTLY, plotly_figure_content({"data": [], "layout": {}}))
    assert bundle.as_uri() in page
    assert count_elements(page, ("script", "div")) == {"script": 3, "div": 1}


def test_export_failure_preserves_destination_and_releases_target(tmp_path, plotly_chrome_executable):
    out = tmp_path / "existing.png"
    out.write_bytes(b"previous-result")
    with RenderSession(chrome=plotly_chrome_executable, offline=True) as session:
        baseline = _page_targets(session.browser)
        bad = replace(PLOTLY, svg_expression="Promise.reject(new Error('capture failed'))")
        with pytest.raises(RuntimeError, match="capture failed"):
            export_draw(bad, plotly_figure_content({"data": []}), out, "svg", session=session)
        assert out.read_bytes() == b"previous-result"
        assert _page_targets(session.browser) == baseline
        export_draw(PLOTLY, plotly_figure_content({"data": []}), tmp_path / "after.svg", "svg", session=session)


@pytest.mark.skipif(os.environ.get("DRAGOWING_TEST_NETWORK") != "1", reason="Mermaid CDN test requires explicit network opt-in")
def test_export_draw_mermaid_svg_contains_labels(tmp_path, chrome_executable):
    out = tmp_path / "flow.svg"
    export_draw(MERMAID, mermaid_diagram_content("graph TD\n  Alpha-->Beta"), out, "svg",
                chrome=chrome_executable, timeouts=Timeouts(launch=45, load=45, ready=60, capture=20))
    text = out.read_text(encoding="utf-8")
    assert "Alpha" in text and "Beta" in text
    assert "<svg" in text


def test_pinned_embed_html_and_image_exports(tmp_path, chrome_executable):
    """Real fixed CDN bytes work in unchanged DRAgoWing JSON blocks and PNG/SVG."""
    import io
    from unittest.mock import patch
    from dragowing import plotly_cdn
    from dragowing.htmlout import figure_block, spec_from, standalone
    from vendor import web_ui

    source = os.environ.get('DRAGOWING_PINNED_PLOTLY_JS')
    if not source:
        if os.environ.get('DRAGOWING_REQUIRE_CHROME') == '1':
            pytest.fail('required pinned Plotly bundle not prepared')
        pytest.skip('real pinned CDN bytes supplied by Chrome CI')
    raw = web_ui.verify_plotly_js(Path(source).read_bytes())
    class Response(io.BytesIO):
        status = 200
    figures = [
        {'data': [{'type': 'scatter', 'x': [1, 2, 3], 'y': [2, 4, 3],
                   'mode': 'lines+markers', 'name': 'pinned-series'}],
         'layout': {'width': 400, 'height': 300, 'showlegend': True,
                    'title': {'text': 'Pinned scatter'}}},
        {'data': [{'type': 'heatmap', 'x': [2025, 2026], 'y': ['d', 'g'],
                   'z': [[-1.2, 0.3], [1.1, -0.4]], 'text': [['B', 'A'], ['A', 'B']],
                   'texttemplate': '%{text}'}],
         'layout': {'width': 400, 'height': 300, 'title': {'text': 'Pinned heatmap'}}},
    ]
    ready = ("new Promise((ok,bad)=>{let n=0;(function tick(){"
             "let g=document.getElementById('g');"
             "if(g&&g._fullLayout&&g.querySelector('.main-svg')){"
             "if(Plotly.version!==%s)return bad(Error('wrong version'));ok(true);}"
             "else if(++n>1000)bad(Error('render timeout'));else setTimeout(tick,20);})()})"
             % json.dumps(web_ui.PLOTLY_JS_VERSION))
    plotly_cdn.reset_plotly_js_cache()
    try:
        with RenderSession(chrome=chrome_executable, offline=True) as session:
            for index, spec in enumerate(figures):
                with patch('urllib.request.urlopen', return_value=Response(raw)):
                    page = standalone('DRAgoWing', figure_block(spec, 'g'), plotly=True, embed=True)
                assert spec_from(page, 'g') == spec
                config = replace(PLOTLY, local_scripts=(), template=page, ready_expression=ready)
                for fmt in ('png', 'svg'):
                    data = export_draw(config, '', tmp_path / f'pinned-{index}.{fmt}', fmt, session=session)
                    if fmt == 'png':
                        _check_png(data, 400, 300)
                    else:
                        root = ET.fromstring(data)
                        assert spec['layout']['title']['text'] in ''.join(root.itertext())
                        if index == 0:
                            assert 'pinned-series' in ''.join(root.itertext())
                        else:
                            assert {'A', 'B'} <= set(root.itertext())
    finally:
        plotly_cdn.reset_plotly_js_cache()
