"""Draw the three synthetic diagnostic figures once and save them as the browser-free test fixtures.

    python scripts/render_static_fixtures.py --chrome /path/to/chromium --plotly-js /path/to/plotly.min.js

The output (PNG and SVG per figure plus ``manifest.json``) goes to ``tests/fixtures/rendered_plotly``.
It is a saved observation, not a reference to reproduce byte for byte: the PNG bytes depend on the
Chromium build and the SVG on the Plotly.js version. ``tests/test_rendered_output_static.py`` only
compares them with the figure spec (``scripts/rendered_output_checks.py``), so regenerate them when
the synthetic figures change or the checks need a newer Plotly, and review the manifest diff.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dragowing.export import PLOTLY, export_draw, plotly_figure_content  # noqa: E402
from dragowing.render import RenderSession  # noqa: E402
from scripts import diagnose_dragowing_browser as diagnostic  # noqa: E402
from scripts.rendered_output_checks import check_png, check_svg, figures_digest  # noqa: E402

DEFAULT_OUT = ROOT / "tests" / "fixtures" / "rendered_plotly"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--chrome", required=True, help="absolute path of Chrome or Chromium")
    parser.add_argument("--plotly-js", required=True, type=Path, help="local plotly.min.js to draw with")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    bundle = args.plotly_js.resolve()
    version = re.search(r"plotly\.js v([0-9][0-9A-Za-z.\-]*)", bundle.read_text(encoding="utf-8")[:2000])
    browser = subprocess.run([args.chrome, "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
    figures = diagnostic._figures()
    config = replace(PLOTLY, local_scripts=(lambda: bundle,))
    args.out.mkdir(parents=True, exist_ok=True)
    files = {}
    with RenderSession(chrome=args.chrome) as session:
        for index, figure in enumerate(figures):
            for fmt, check in (("png", check_png), ("svg", check_svg)):
                name = "figure-%d.%s" % (index, fmt)
                data = export_draw(config, plotly_figure_content(figure), args.out / name, fmt, session=session)
                check(data, figure)  # never save output the checks would reject
                files[name] = hashlib.sha256(data).hexdigest()
    manifest = {
        "schema": "aoi-rendered-plotly-fixtures/1",
        "figures_sha256": figures_digest(figures),
        "plotly_js": version.group(1) if version else None,
        "browser": browser,
        "files": files,
        "regenerate": "python scripts/render_static_fixtures.py --chrome <chromium> --plotly-js <plotly.min.js>",
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote %d files to %s" % (len(files) + 1, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
