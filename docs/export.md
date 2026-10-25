# PNG / SVG export with Chromium

The image export API uses neither the Python `plotly` package nor kaleido. Plotly.js is fetched from the same jsDelivr URL as the HTML (`PLOTLY_JS_CDN` in `dragowing/plotly_cdn.py`), copied into a temporary directory for each export, and loaded via a `file:` URL. The CLI's `--png` uses the same `export_draw` path.

The changes from the original PRs #44, #43, and #42 were brought into the same combined branch during PR cleanup. The existing default HTML output, research records, integer scores, and the official judge are not touched.

```python
from dragowing.export import PLOTLY, export_draw, plotly_figure_content
from dragowing.render import RenderSession

fig = {"data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}],
       "layout": {"width": 640, "height": 480, "title": {"text": "Example"}}}
with RenderSession(offline=True) as session:
    for fmt in ("png", "svg"):
        export_draw(PLOTLY, plotly_figure_content(fig), f"example.{fmt}", fmt, session=session)
```

`PLOTLY` is a generic `DrawConfig` that draws with browser-side JS, like Mermaid. For offline verification, a pre-verified `plotly.min.js` can be supplied via the `DRAGOWING_PINNED_PLOTLY_JS` environment variable. The figure data must also be available locally (this is not a feature that automatically fetches maps, images, fonts, etc. from external URLs).

The HTML's external tag and `--embed` also use the same jsDelivr distribution (no SRI / SHA-256 pinning; the web-ui side is a separate PR).

It waits for the `Plotly.newPlot` Promise to complete. PNG takes a screenshot of the whole figure container, and SVG serializes all layers with the local `Plotly.toImage`. This includes titles and legends that would be missing if only the first `svg.main-svg` were taken. Handling of WebGL parts in SVG follows the Plotly.js spec.

Pipe communication uses only the Python standard library. It uses POSIX Chromium; Windows pipes are not supported. Automatic discovery searches `chromium`, then `chromium-browser` on PATH. It never silently falls back to Google Chrome. If Chromium is absent, image export raises an error explaining how to install or select it. HTML-only output does not require a browser.

Explicit selection remains backward compatible: `chrome=` takes precedence; otherwise nonempty `CHROME` and `CHROMIUM` variables are tried in that order. If an explicit selection is present, PATH defaults are not tried. An explicit Google Chrome executable is still supported for compatibility and comparison. The `Chrome` / `find_chrome` names, `chrome=` argument, and `DRAGOWING_REQUIRE_CHROME` flag remain unchanged. Files without execute permission are an error. Kaleido / choreographer are not needed for this API.

This standardizes browser selection, not startup timing. Launch flags, D-Bus isolation, timeouts, retry behavior, and cleanup are unchanged. Chromium can still have slow cold starts; changing the browser does not establish that a previous timeout is fixed.

The launched Chrome is not allowed to use D-Bus. The child process's `DBUS_SESSION_BUS_ADDRESS` and `DBUS_SYSTEM_BUS_ADDRESS` are `unix:path=` pointing at a unix socket that is never created, so `connect` returns immediately with `ENOENT`. `disabled:` is an address type libdbus doesn't know; it may print only `Unknown address type` and then sit silent with the process alive until the launch limit. If the variables are removed, Chrome itself writes `disabled:` for the session bus and still connects to the system bus. Keyring, crashpad, portals, and AT-SPI are also stopped. Drawing figures does not need D-Bus. When the process is alive but not responding, the timeout carries that fact and stderr.

`Timeouts(launch=30, load=30, ready=30, capture=15)` sets the limit for each stage. The sending side of communication also stays within the limits and sends partial writes to completion. `Browser.getVersion` is checked at launch. Invalid JSON, EOF, and launch failures raise exceptions. Timeouts and capture failures are never treated as success or an empty image. The target is closed after each drawing, whether it succeeds or fails, and the destroy event is awaited. If close fails, the whole browser is shut down.

`RenderSession(offline=True)` disables CDP networking for the drawing page. The default generic renderer's network behavior is unchanged. `MERMAID` remains a sample config that uses the CDN; offline support targets `PLOTLY`.

## Verification

```bash
CHROMIUM=/path/to/chromium DRAGOWING_REQUIRE_CHROME=1 uv run --locked --python 3.14 pytest -q dragowing/tests
```

In a normal environment without Chromium or an explicit browser override, real-browser tests are skipped with a reason. With `DRAGOWING_REQUIRE_CHROME=1` they fail instead of skipping. Only the Mermaid CDN test requires explicitly setting `DRAGOWING_TEST_NETWORK=1`.

DRAgoWing's Python 3.11–3.15 CI matrix explicitly selects `chromium` / `chromium-browser`, records its version, and sets `DRAGOWING_REQUIRE_CHROME=1`. Missing Chromium fails the selection step. Aoi has a separate network-isolated export job; its historical `chrome-export` job and artifact identifiers are retained for report consumers.

The tests check, with the network cut off, the bundled JS version, the same PID across 3 figures × 2 formats, PNG dimensions, CRC, and non-blank decoded data, SVG XML, title, legend, and point count, and that the target count does not grow. They also check missing Chrome, no execute permission, launch failure, no response, a blocked send, early exit, invalid JSON, partial writes, large responses, early events, ready timeouts, and release and reuse after a capture failure. Byte equality of images is not a pass criterion.
