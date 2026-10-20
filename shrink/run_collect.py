#!/usr/bin/env python3
"""Run research_digest.collect and write canonical bytes.

``--deps real`` requires the installed polars package. ``--deps min`` refuses to start
when that import succeeds, then loads shrink/polars_min.py as ``sys.modules['polars']``
before importing research_digest. The two modes write the same bytes when the min
surface matches.

This file is stdlib-only. It has to live inside an Aoi checkout (``vendor/markdown.py``
next to ``nagoyaction/``) because research_digest loads that helper at import.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

NAGOYA = Path(__file__).resolve().parents[1]
AOI = NAGOYA.parent
DEFAULT_CYCLE = AOI / "cycles" / "c001-chunichi"
MIN_PATH = NAGOYA / "shrink" / "polars_min.py"


def canonical(notes, codes, catalog) -> bytes:
    payload = {
        "schema": "nagoyaction-collect/1",
        "catalog": sorted(catalog),
        "codes": {key: codes[key] for key in sorted(codes)},
        "notes": notes,
    }
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def _real_polars_imports() -> bool:
    try:
        importlib.import_module("polars")
    except ModuleNotFoundError:
        sys.modules.pop("polars", None)
        return False
    return True


def _install_min() -> None:
    spec = importlib.util.spec_from_file_location("polars", MIN_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {MIN_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["polars"] = module
    spec.loader.exec_module(module)
    try:
        module.Series  # type: ignore[attr-defined]
    except AttributeError:
        return
    raise SystemExit("polars_min rejected the stand-in check: Series is a real polars name")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--deps", choices=("real", "min"), required=True)
    parser.add_argument("--cycle", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args(argv)
    markdown = AOI / "vendor" / "markdown.py"
    if not markdown.is_file():
        print(f"research_digest needs {markdown}; overlay this tree onto Aoi/nagoyaction", file=sys.stderr)
        return 1
    cycle = (args.cycle or DEFAULT_CYCLE).resolve()
    if not (cycle / "research").is_dir():
        print(f"no research notes under {cycle}", file=sys.stderr)
        return 1
    installed = _real_polars_imports()
    if args.deps == "real":
        if not installed:
            print("real collect needs polars installed", file=sys.stderr)
            return 1
        loaded = sys.modules["polars"]
        origin = getattr(loaded, "__file__", "") or ""
        if origin.endswith("polars_min.py"):
            print("real collect found polars_min, not polars", file=sys.stderr)
            return 1
    else:
        if installed:
            print("min collect refuses to run while `import polars` succeeds", file=sys.stderr)
            return 1
        _install_min()
    sys.path.insert(0, str(NAGOYA))
    import research_digest

    origin = Path(research_digest.pl.__file__ or "").resolve()
    if args.deps == "min" and origin != MIN_PATH.resolve():
        print(f"research_digest loaded {origin}, not {MIN_PATH}", file=sys.stderr)
        return 1
    if args.deps == "real" and origin == MIN_PATH.resolve():
        print("research_digest loaded polars_min in real mode", file=sys.stderr)
        return 1
    notes, codes, catalog = research_digest.collect(cycle)
    data = canonical(notes, codes, catalog)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(
        f"deps={args.deps} notes={len(notes)} "
        f"sha256={hashlib.sha256(data).hexdigest()} bytes={len(data)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
