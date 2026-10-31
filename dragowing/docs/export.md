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

DRAgoWing's Python 3.11–3.15 CI matrix installs a reviewed Chromium snapshot with the standard-library setup script `scripts/install_ci_chromium.py`, checks its version, and sets `CHROME` and `DRAGOWING_REQUIRE_CHROME=1` explicitly. Download, integrity, extraction or version failures stop the job; there is no fallback to the runner's preinstalled browser or Google Chrome. Local automatic discovery and production runtime dependencies are unchanged. Aoi has a separate network-isolated export job; its historical `chrome-export` identifiers remain independent of this CI setup.

### Managed CI browser provenance and first-start scope

- Chromium version: **156.0.8078.0**, snapshot revision **1706520**.
- Source commit: [`23b351114f0570483d619b05db197bbc5594dc5a`](https://chromium.googlesource.com/chromium/src/+/23b351114f0570483d619b05db197bbc5594dc5a); its `chrome/VERSION` and commit position match the snapshot's official `REVISIONS`.
- [Official generation-pinned ZIP](https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1706520%2Fchrome-linux.zip?generation=1790642197733749&alt=media), generation `1790642197733749`, **248486630 bytes**.
- SHA256: `6b62846a868ea3ee675f77600790877a428dfb2428c940f8eff99db1038f9815`.
- Locally verified official metadata MD5: `gAHURDw3hLwHmZglzqJUIw==`; all ZIP CRCs passed. 483 members, 702789127 expanded bytes. This is a fixed Chromium snapshot, **not** a stable-channel release.

The installer performs one ordinary archive download, archive integrity verification and safe extraction into a fresh job-owned destination. It rejects unsafe paths, duplicate members, links/special files and excess sizes, strips special permission bits, and never executes Chromium. It refuses to overwrite an existing installation. No package, system configuration, runtime dependency or privilege changes are made.

The existing `--version` selection check remains; the first full browser startup is still the real test, using a fresh process/profile. There is no browser warmup, executable-tree pre-read, retry or timeout increase. The production 30-second launch budget and all existing test assertions remain unchanged. Installation naturally changes file placement/cache state, so results describe **first startup after managed installation**, not an empty OS page cache. This does not establish a fix to the earlier preinstalled-image file-page wait. The version matches the failed runner's logged version; byte identity with its executable is unverified because no historical binary hash was captured. Keep prior failure evidence separate from this provisioning condition.

To prepare the same dependency without launching it:

```bash
python3 scripts/install_ci_chromium.py --destination /path/to/new/chromium-install
```

Use the returned `chrome-linux/chrome` path explicitly. The setup script does not download dependencies at library import or runtime. Updating the snapshot requires reviewing the official revision, source version, archive size/hash and regression tests together.


The tests check, with the network cut off, the bundled JS version, the same PID across 3 figures × 2 formats, PNG dimensions, CRC, and non-blank decoded data, SVG XML, title, legend, and point count, and that the target count does not grow. They also check missing Chrome, no execute permission, launch failure, no response, a blocked send, early exit, invalid JSON, partial writes, large responses, early events, ready timeouts, and release and reuse after a capture failure. Byte equality of images is not a pass criterion.
