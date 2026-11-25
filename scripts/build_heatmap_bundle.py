"""Regenerate the heatmap stylesheet and PySaiyanWeBoo helpers in heatmap_bundle.py.

    uv run python scripts/build_heatmap_bundle.py          # rewrite STYLE_CSS, PSWB_HTML, PSWB_JS
    uv run python scripts/build_heatmap_bundle.py --check  # exit 1 when stale
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

BUNDLE_PY = Path(__file__).with_name("heatmap_bundle.py")
NOTE = "build_heatmap_bundle.py"
THEME = "modern"
PSWB_JS_MODULES = ("ui.js", "scroll.js")
PSWB_EXPORTS = (
    "setText",
    "prettyJson",
    "copyText",
    "bindTheme",
    "pageTheme",
    "bindToggles",
    "bindScroll",
    "refreshScroll",
)

HEATMAP_RULES = """@layer components{
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


def css_options() -> dict:
    """Options passed to pysaiyanweboo.write_bundle / check_bundle."""
    import pysaiyanweboo

    extra = "\n".join(
        [
            pysaiyanweboo.css_source("themes/github-like.css"),
            pysaiyanweboo.css_source("scroll.css"),
            pysaiyanweboo.css_source("records.css"),
            HEATMAP_RULES,
        ]
    )
    return {"theme": THEME, "extra_css": extra}


def pswb_parts() -> dict[str, str]:
    """Extract PSWB theme switcher HTML and classic-script JS helpers from the pinned commit."""
    import pysaiyanweboo

    modules = "\n".join(pysaiyanweboo.js_source(name) for name in PSWB_JS_MODULES)
    classic = re.sub(r"^export\s+(?=(?:async\s+)?function\b)", "", modules, flags=re.M)
    assert not re.search(r"^\s*(import|export)\b", classic, flags=re.M), (
        "PySaiyanWeBoo module uses an unsupported import/export form"
    )
    commit = pysaiyanweboo.source_commit() or "unknown"
    exports = ", ".join(PSWB_EXPORTS)
    js = (
        f"/* ⬇️ pysaiyanweboo {commit[:8]} ({', '.join(PSWB_JS_MODULES)}): written by {NOTE}; --check fails when stale */\n"
        f"(() => {{\n{classic}\nglobalThis.PySaiyanWeBoo = {{ {exports} }};\n}})();\n"
        f"/* ⬆️ pysaiyanweboo */"
    )
    return {
        "theme_switch": pysaiyanweboo.theme_switch_html(control="select", legend="テーマ"),
        "js": js,
    }


def render_bundle_module() -> str:
    """Return the complete Python source for scripts/heatmap_bundle.py."""
    import pysaiyanweboo

    options = css_options()
    parts = pswb_parts()
    with tempfile.TemporaryDirectory() as tmp:
        css_path = Path(tmp) / "heatmap.css"
        pysaiyanweboo.write_bundle(css_path, note=NOTE, **options)
        css_text = css_path.read_text(encoding="utf-8")
    for literal in (css_text, parts["theme_switch"], parts["js"]):
        assert '"""' not in literal, "bundle literal cannot contain triple double-quotes"
    return (
        '"""Bundled PySaiyanWeBoo CSS, HTML controls, and JS helpers for the standalone heatmap page."""\n\n'
        f'STYLE_CSS = r"""{css_text}"""\n\n'
        f'PSWB_HTML = {{\n    "theme_switch": {parts["theme_switch"]!r},\n}}\n\n'
        f'PSWB_JS = r"""{parts["js"]}"""\n'
    )


def check_bundle_module(bundle_path: Path = BUNDLE_PY) -> list[str]:
    """Return a list of staleness/provenance problems for the committed bundle module."""
    import pysaiyanweboo

    if not bundle_path.is_file():
        return [f"{bundle_path.name}: missing; run {NOTE}"]
    src = bundle_path.read_text(encoding="utf-8")
    marker = 'STYLE_CSS = r"""'
    if marker not in src:
        return [f"{bundle_path.name}: missing STYLE_CSS; run {NOTE}"]
    start = src.index(marker) + len(marker)
    end = src.index('"""', start)
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        css_path = Path(tmp) / "heatmap.css"
        css_path.write_text(src[start:end], encoding="utf-8")
        problems.extend(pysaiyanweboo.check_bundle(css_path, **css_options()))
    expected = render_bundle_module()
    if src != expected:
        problems.append(f"{bundle_path.name}: bundle contents differ from {NOTE}; run {NOTE}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 when heatmap_bundle.py is stale")
    args = parser.parse_args(argv)
    if args.check:
        problems = check_bundle_module()
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1 if problems else 0
    BUNDLE_PY.write_text(render_bundle_module(), encoding="utf-8")
    print(f"wrote {BUNDLE_PY.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
