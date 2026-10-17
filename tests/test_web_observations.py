import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from web_observations import observe, source_inventory


def receipt():
    return {"schema": "flutter-web-observation/1", "build_sha": "a" * 40,
        "url": "https://example.test/#/tools/media/photo-studio", "status": "passed",
        "capture_errors": [], "extra_provenance": {"keep": True},
        "runtime": {"display": {"viewport": {"width": 800, "height": 600},
            "controls": [{"label": "📷 写真", "visible": True,
                          "box": {"x": -1, "y": 20, "width": 80, "height": 30}}]}}}


def save(root, data, name="page"):
    directory = root / name
    directory.mkdir()
    (directory / "web-observation.json").write_text(json.dumps(data), encoding="utf-8")
    return directory


def test_preserves_raw_geometry_actions_and_reports_missing_capabilities(tmp_path):
    raw = receipt()
    page = save(tmp_path, raw)
    actions = {"schema": "flutter-web-exploration/1", "actions": [
        {"kind": "press", "label": "📷 写真", "after_url": raw["url"]}]}
    (page / "exploration.json").write_text(json.dumps(actions), encoding="utf-8")
    result = observe(tmp_path)
    record = result["report"]["records"][0]
    assert record["raw"] == raw and record["raw_exploration"] == actions
    assert record["derived"]["controls"][0]["box"]["x"] == -1
    assert record["derived"]["actions"] == actions["actions"]
    assert result["report"]["counts"]["invalid"] == 0
    assert not result["current_code_executed"] and not result["native_equivalence_verified"]
    assert "backend" in result["unobserved"][0]


@pytest.mark.parametrize("bad", [None, True, float("nan"), "20"])
def test_invalid_coordinates_are_retained_as_unknown(tmp_path, bad):
    raw = receipt()
    raw["runtime"]["display"]["controls"][0]["box"]["x"] = bad
    save(tmp_path, raw)
    result = observe(tmp_path)["report"]
    assert not result["records"] and result["counts"]["invalid"]
    assert result["unknown"][0]["key"] == "page/web-observation.json"


def test_mixed_builds_are_incomplete_and_missing_actions_not_invented(tmp_path):
    raw = receipt()
    save(tmp_path, raw)
    other = copy.deepcopy(raw)
    other["build_sha"] = "b" * 40
    save(tmp_path, other, "other")
    result = observe(tmp_path)["report"]
    assert result["counts"]["invalid"] == 1
    assert result["unknown"][0]["reason"] == "mixed reported build SHAs"
    assert result["counts"]["missing_action_receipts"] == 2
    assert all(row["derived"]["actions"] is None for row in result["records"])


def test_empty_directory_never_becomes_successful_evidence(tmp_path):
    assert observe(tmp_path)["report"]["counts"]["invalid"]


def test_failed_producer_receipt_is_observed_without_becoming_a_pass(tmp_path):
    raw = receipt()
    raw.update(status="failed", capture_errors=["screenshot unavailable"])
    save(tmp_path, raw)
    result = observe(tmp_path)["report"]
    assert result["counts"]["producer_failed_or_incomplete"] == 1
    assert result["records"][0]["derived"]["producer_status"] == "failed"


def test_cli_preserves_unicode_on_legacy_console(tmp_path):
    save(tmp_path, receipt())
    script = Path(__file__).resolve().parents[1] / "web_observations.py"
    result = subprocess.run([sys.executable, "-S", str(script), str(tmp_path)],
        text=True, capture_output=True, encoding="ascii",
        env={**os.environ, "PYTHONIOENCODING": "cp1252"})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["report"]["records"][0]["derived"]["controls"][0]["label"] == "📷 写真"


def test_source_inventory_hashes_bytes_without_claiming_route_binding(tmp_path):
    for name in ("view.dart", "View.kt", "View.swift", "ignored.py", "build/cached.dart", "pubspec.lock"):
        path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b"// source\r\n")
    rows = source_inventory(tmp_path)
    assert {row["language"] for row in rows if row["kind"] == "source"} == {"dart", "kotlin", "swift"}
    assert len(rows) == 4
    assert next(row for row in rows if row["path"] == "pubspec.lock")["kind"] == "build-config"
    assert all(row["sha256"] == hashlib.sha256(b"// source\r\n").hexdigest() for row in rows)


def test_documented_directory_cli_with_source_root(tmp_path):
    observations = tmp_path / "saved pages"
    observations.mkdir()
    save(observations, receipt())
    sources = tmp_path / "flutter sources"
    sources.mkdir()
    (sources / "view.dart").write_text("// inventory only\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "web_observations.py"
    result = subprocess.run([sys.executable, "-S", str(script), str(observations),
        "--source-root", str(sources)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert len(report["report"]["records"]) == 1
    assert report["sources"][0]["path"] == "view.dart"
    assert not report["current_code_executed"]
