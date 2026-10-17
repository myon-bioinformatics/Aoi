"""Read saved Web observations and source inventories, without a browser or SDK.

This is an observation adapter, never a native-equivalence or integrity verifier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from blueprobe import new_report

SCHEMA = "web-portability-observations/1"
LANGUAGES = {".dart": "dart", ".kt": "kotlin", ".swift": "swift"}
EXCLUDED = {".git", ".dart_tool", ".venv", "node_modules", "build", "Pods", "vendor"}
BUILD_FILES = {"pubspec.yaml", "pubspec.lock", "Podfile", "Podfile.lock",
               "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
               "gradle-wrapper.properties", "project.pbxproj", "Package.swift", "Package.resolved"}


def source_inventory(root: Path) -> list[dict]:
    """Hash source bytes; do not infer symbols, call graphs or executable behavior."""
    rows = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts) or path.is_symlink():
            continue
        if (path.suffix not in LANGUAGES and path.name not in BUILD_FILES) or not path.is_file():
            continue
        data = path.read_bytes()
        rows.append({"path": relative.as_posix(), "language": LANGUAGES.get(path.suffix),
                     "kind": "build-config" if path.name in BUILD_FILES else "source",
                     "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return rows


def _controls(value):
    if not isinstance(value, list) or not value:
        raise ValueError("missing control inventory")
    for control in value:
        if not isinstance(control, dict) or not isinstance(control.get("label"), str):
            raise ValueError("invalid control label")
        if not isinstance(control.get("visible"), bool):
            raise ValueError("invalid visibility")
        box = control.get("box", {})
        if not isinstance(box, dict):
            raise ValueError("invalid box")
        for name in ("x", "y", "width", "height"):
            number = box.get(name)
            if type(number) not in (int, float) or not math.isfinite(number):
                raise ValueError("invalid box coordinate")
        if box["width"] < 0 or box["height"] < 0:
            raise ValueError("negative box size")
    return value


def _nonfinite(value):
    raise ValueError(f"non-finite JSON number: {value}")


def observe(root: Path, *, source_root: Path | None = None) -> dict:
    """Preserve receipts verbatim beside derived geometry and action records.

    Consumer-specific catalogue coverage and screenshot verification remain with
    the producer's existing verifier. Source hashes are not route bindings.
    """
    root = Path(root)
    if not root.is_dir():
        raise ValueError("observation root must be a directory")
    report = new_report()
    builds = set()
    for path in sorted(root.rglob("web-observation.json")):
        key = path.relative_to(root).as_posix()
        raw = None
        try:
            data = path.read_bytes()
            raw = data.decode("utf-8")
            raw = json.loads(raw, parse_constant=_nonfinite)
            if not isinstance(raw, dict) or raw.get("schema") != "flutter-web-observation/1":
                raise ValueError("unsupported observation schema")
            build = raw.get("build_sha")
            if not isinstance(build, str) or len(build) != 40 or any(c not in "0123456789abcdef" for c in build):
                raise ValueError("missing immutable build SHA")
            display = raw["runtime"]["display"]
            controls = _controls(display["controls"])
            if not isinstance(raw.get("url"), str) or not raw["url"]:
                raise ValueError("missing observed URL")
            exploration_path = path.with_name("exploration.json")
            exploration = None
            if exploration_path.exists():
                exploration = json.loads(exploration_path.read_text(encoding="utf-8"), parse_constant=_nonfinite)
                if exploration.get("schema") != "flutter-web-exploration/1" or not isinstance(exploration.get("actions"), list):
                    raise ValueError("unsupported exploration receipt")
            builds.add(build)
            report["records"].append({"key": key, "raw": raw,
                "raw_exploration": exploration,
                "derived": {"url": raw["url"], "reported_build_sha": build,
                    "controls": controls, "viewport": display.get("viewport"),
                    "actions": None if exploration is None else exploration["actions"],
                    "producer_status": raw.get("status"),
                    "capture_errors": raw.get("capture_errors"),
                    "evidence_sha256": hashlib.sha256(data).hexdigest()}})
            report["counts"]["observations"] += 1
            if raw.get("status") != "passed" or raw.get("capture_errors"):
                report["counts"]["producer_failed_or_incomplete"] += 1
            if exploration is None:
                report["counts"]["missing_action_receipts"] += 1
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            report["counts"]["invalid"] += 1
            report["unknown"].append({"key": key, "raw": raw, "reason": str(error)})
    if not report["records"]:
        report["counts"]["invalid"] += 1
        report["unknown"].append({"key": ".", "raw": None, "reason": "no usable observations"})
    if len(builds) > 1:
        report["counts"]["invalid"] += 1
        report["unknown"].append({"key": ".", "raw": sorted(builds), "reason": "mixed reported build SHAs"})
    if source_root is not None and not Path(source_root).is_dir():
        raise ValueError("source root must be a directory")
    return {"schema": SCHEMA, "scope": "saved-web-observations",
        "current_code_executed": False, "native_equivalence_verified": False,
        "report": report,
        "sources": source_inventory(Path(source_root)) if source_root is not None else [],
        "unobserved": ["backend request/response bodies and state transitions",
            "full DOM/accessibility hierarchy and per-action geometry/state changes",
            "OS permissions, native plugins and device side effects",
            "source-to-route bindings and source/build correspondence",
            "independent Python/Node implementation conformance"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args(argv)
    try:
        result = observe(args.observations, source_root=args.source_root)
    except (OSError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 2 if result["report"]["counts"]["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
