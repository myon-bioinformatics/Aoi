#!/usr/bin/env python3
"""fetch_module.py で取った Python-Markdown で DRAgoWing の render_md を動かす（実験）。

pip/uv で markdown を入れていない環境で、wheel を sys.path に載せて使う。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import fetch_module  # noqa: E402


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    cache = argv[0] if argv else ".cdn-cache"
    markdown = fetch_module.ensure("markdown", cache)
    origin = Path(markdown.__file__).as_posix()
    assert ".whl/markdown/" in origin, f"wheel 以外の markdown を読んだ: {origin}"

    from dragowing.htmlout import render_md  # noqa: E402

    html = render_md("| a | b |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n\nText\n{: .provenance}\n")
    assert "<table>" in html and "<pre><code>" in html and 'class="provenance"' in html, html
    page = render_md((ROOT / "dragowing" / "README.md").read_text(encoding="utf-8"))
    assert "<h1" in page and "<table>" in page, page[:200]
    print(f"markdown {markdown.__version__} from {origin}")
    print(f"render_md ok ({len(html)} + {len(page)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
