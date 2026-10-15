#!/usr/bin/env python3
"""Verify workflow pins to the organization parent repository are unified."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PARENT_REPOSITORY = "myon-bioinformatics/myon-bioinformatics"
PARENT_PIN = "9cc33f08f225eaf67d9a00489a1bf15977ebee25"

USES_RE = re.compile(
    rf"myon-bioinformatics/myon-bioinformatics/[^\s@]+@([0-9a-f]{{40}})",
    re.IGNORECASE,
)
CHECKOUT_BLOCK_RE = re.compile(
    rf"repository:\s*{re.escape(PARENT_REPOSITORY)}\s*\n\s*ref:\s*([0-9a-f]{{40}})",
    re.IGNORECASE,
)
WORKFLOW_GLOBS = (
    ".github/workflows/*.yml",
    "blueprobe/.github/workflows/*.yml",
)


def _workflow_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in WORKFLOW_GLOBS:
        files.extend(sorted(root.glob(pattern)))
    return files


def collect_pins(root: Path) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in _workflow_files(root):
        text = path.read_text(encoding="utf-8")
        pins: set[str] = set()
        pins.update(USES_RE.findall(text))
        pins.update(CHECKOUT_BLOCK_RE.findall(text))
        if pins:
            found[str(path.relative_to(root))] = pins
    return found


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    pins_by_file = collect_pins(root)
    if not pins_by_file:
        print("no parent workflow pins found", file=sys.stderr)
        return 1
    mismatches: list[str] = []
    for rel_path, pins in sorted(pins_by_file.items()):
        extra = pins - {PARENT_PIN}
        if extra:
            mismatches.append(f"{rel_path}: {', '.join(sorted(extra))}")
    if mismatches:
        print("parent pin mismatch (expected unified pin):", file=sys.stderr)
        for line in mismatches:
            print("  " + line, file=sys.stderr)
        return 1
    print(f"ok: {len(pins_by_file)} workflow file(s) pin {PARENT_PIN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
