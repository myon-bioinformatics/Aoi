# PNG / SVG export with Chrome

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

Pipe communication uses only the Python standard library. It uses POSIX Chrome/Chromium; Windows pipes are not supported. It searches the `chrome=` argument, the `CHROME` / `CHROMIUM` environment variables, then PATH, in that order. Files without execute permission are also an error. Kaleido / choreographer are not needed for this API.

The launched Chrome is not allowed to use D-Bus. The child process's `DBUS_SESSION_BUS_ADDRESS` and `DBUS_SYSTEM_BUS_ADDRESS` are `unix:path=` pointing at a unix socket that is never created, so `connect` returns immediately with `ENOENT`. `disabled:` is an address type libdbus doesn't know; it may print only `Unknown address type` and then sit silent with the process alive until the launch limit. If the variables are removed, Chrome itself writes `disabled:` for the session bus and still connects to the system bus. Keyring, crashpad, portals, and AT-SPI are also stopped. Drawing figures does not need D-Bus. When the process is alive but not responding, the timeout carries that fact and stderr.

`Timeouts(launch=30, load=30, ready=30, capture=15)` sets the limit for each stage. The sending side of communication also stays within the limits and sends partial writes to completion. `Browser.getVersion` is checked at launch. Invalid JSON, EOF, and launch failures raise exceptions. Timeouts and capture failures are never treated as success or an empty image. The target is closed after each drawing, whether it succeeds or fails, and the destroy event is awaited. If close fails, the whole browser is shut down.

`RenderSession(offline=True)` disables CDP networking for the drawing page. The default generic renderer's network behavior is unchanged. `MERMAID` remains a sample config that uses the CDN; offline support targets `PLOTLY`.

## Verification

```bash
CHROME=/path/to/chrome DRAGOWING_REQUIRE_CHROME=1 uv run --locked --python 3.14 pytest -q dragowing/tests
```

In a normal environment without Chrome, real-browser tests are skipped with a reason. With `DRAGOWING_REQUIRE_CHROME=1` they fail instead of skipping. Only the Mermaid CDN test requires explicitly setting `DRAGOWING_TEST_NETWORK=1`.

After installing dependencies, CI's dedicated job isolates the network with `sudo unshare --net` and runs the pipe and PNG/SVG tests with real Chrome required. JUnit is saved as `junit-chrome-export-py3.14`. The regular Python 3.11–3.15 matrix is kept as well.

The tests check, with the network cut off, the bundled JS version, the same PID across 3 figures × 2 formats, PNG dimensions, CRC, and non-blank decoded data, SVG XML, title, legend, and point count, and that the target count does not grow. They also check missing Chrome, no execute permission, launch failure, no response, a blocked send, early exit, invalid JSON, partial writes, large responses, early events, ready timeouts, and release and reuse after a capture failure. Byte equality of images is not a pass criterion.
