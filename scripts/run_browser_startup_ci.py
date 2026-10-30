"""One-command runner for the real Chromium first-start regression.

Run inside a fresh CI job. Network isolation is established by the caller,
not by this wrapper, so normal and offline jobs stay independent.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/startup-context"))
    args = parser.parse_args(argv)
    if not os.environ.get("CHROME"):
        parser.error("CHROME must identify the selected Chromium executable")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["DRAGOWING_REQUIRE_CHROME"] = "1"
    env["DRAGOWING_EXPORT_EVIDENCE_DIR"] = str(output / "export-evidence")
    env.setdefault("DRAGOWING_PINNED_PLOTLY_JS", str(Path("build/test-assets/plotly.min.js").resolve()))
    command = [
        sys.executable, "-m", "pytest", "-c", "pyproject.toml", "-q",
        "-p", "scripts.observe_dragowing_startup",
        f"--browser-startup-evidence={output / 'actual-tests.json'}",
        "dragowing/tests/test_chrome_pipe.py",
        "dragowing/tests/test_render.py",
        "dragowing/tests/test_export.py",
        "dragowing/tests/test_plotly_cdn.py",
        f"--junitxml={output / 'actual-tests.xml'}",
    ]
    return subprocess.call(command, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
