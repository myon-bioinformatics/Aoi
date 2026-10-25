"""Offline completeness/provenance checks; not an independent live NPB replay."""

from copy import deepcopy
import hashlib
import json

import pytest

from scripts import reconcile_season_2026 as season


def inputs():
    return (
        json.loads(season.ORIGINAL.read_text(encoding="utf-8")),
        season.read_jsonl(season.DATA / "observed/game_updates.jsonl"),
        json.loads((season.DATA / "observed/annual_totals.json").read_text(encoding="utf-8"))["rows"],
    )


def test_committed_outputs_reproduce_exactly():
    for path, expected in season.outputs().items():
        assert path.read_text(encoding="utf-8") == expected


def test_original_is_unchanged_and_only_remaining_games_are_added():
    original, updates, annual = inputs()
    games, totals, report = season.reconcile(original, updates, annual)
    assert hashlib.sha256(season.ORIGINAL.read_bytes()).hexdigest() == season.ORIGINAL_SHA
    original_finals = {r["url"]: r for r in original if season.regular(r) and r["status"] == "final"}
    final = {r["url"]: r for r in games}
    assert len(original_finals) == 847
    assert all(final[url] == row for url, row in original_finals.items())
    assert len(games) == len(final) == 858
    assert len(totals) == 12 and all(row["G"] == 143 for row in totals)
    assert len(report["finalised_october_3_urls"]) == 2
    assert len(report["added_october_4_to_8_urls"]) == 9
    assert report["annual_values_matched"] == 72
    assert all(row["match"] for row in report["annual_comparisons"])
    assert min(row["date"] for row in games) == "20260327"
    assert max(row["date"] for row in games) == "20261008"


def test_acquisition_and_annual_provenance_exclude_full_html():
    _, updates, _ = inputs()
    acquisition = season.read_jsonl(season.DATA / "provenance/acquisition.jsonl")
    games = [row for row in acquisition if row.get("purpose") != "remaining_game_discovery"]
    assert {row["url"] for row in games} == {row["url"] for row in updates}
    assert len(games) == 11
    assert all(row["http_status"] == 200 and row["bytes"] > 0 and len(row["sha256"]) == 64 for row in acquisition)
    assert all(row["raw_html_published"] is False for row in acquisition)
    assert all("2026-10-25" in row["fetched_at"] for row in games)
    annual = json.loads((season.DATA / "observed/annual_totals.json").read_text(encoding="utf-8"))
    assert len(annual["source_archives"]) == 2
    assert annual["checks"]["cross_archive_annual_values_matched"] == 72
    assert not annual["checks"]["full_html_in_output"]
    assert not annual["checks"]["synthetic_rows_in_output"]
    assert not list(season.DATA.rglob("*.html"))
    assert not list(season.DATA.rglob("*.zip"))


def test_fresh_walkoff_cells_are_retained_without_changing_originals():
    _, updates, _ = inputs()
    game = next(row for row in updates if row["url"].endswith("/1004/db-t-25/"))
    assert game["home_inning_cells"][-1] == "1x"
    assert game["home_inn"][-1] == 1
    assert game["home_R"] == 2


@pytest.mark.parametrize("field,value", [
    ("status", "other:in-progress"), ("status", "cancelled"),
    ("title", "【日本シリーズ】 test"), ("title", "【オールスターゲーム】 test"),
    ("year", 2025), ("date", "20261010"), ("home", "unknown"),
    ("away", None), ("home_R", True), ("home_R", -1),
    ("away_R", 0.5), ("away_inn", [999] * 9),
    ("home_inn", [True] * 9), ("check", False), ("synthetic", True),
    ("url", "https://example.com/scores/2026/1003/e-b-25/"),
])
def test_invalid_game_fails_closed(field, value):
    _, updates, _ = inputs()
    row = deepcopy(updates[0])
    row[field] = value
    with pytest.raises(ValueError):
        season.validate_game(row)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "replace_final", "wrong_annual", "duplicate_team", "wrong_annual_year"])
def test_reconciliation_rejects_incomplete_or_conflicting_inputs(mutation):
    original, updates, annual = inputs()
    if mutation == "missing":
        updates.pop()
    elif mutation == "duplicate":
        updates[-1] = deepcopy(updates[0])
    elif mutation == "replace_final":
        updates[-1] = deepcopy(next(r for r in original if season.regular(r) and r["status"] == "final"))
    elif mutation == "wrong_annual":
        annual[0]["RF"] += 1
    elif mutation == "duplicate_team":
        annual[-1] = deepcopy(annual[0])
    elif mutation == "wrong_annual_year":
        annual[0]["season"] = 2025
    with pytest.raises(ValueError):
        season.reconcile(original, updates, annual)
