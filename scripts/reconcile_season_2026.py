"""Offline reconciliation of the preserved 2026 regular-season observations.

No network, inference, synthetic games, or changes to the original source ZIPs.
This separate dataset is not a QueRyu observation-format migration or a rerun
of the 409-column c001 research/model panel.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "cycles/c001-chunichi/season-2026"
ORIGINAL = ROOT / "cycles/c001-chunichi/recovered-inputs/observed/games_raw.json"
ORIGINAL_SHA = "dc75aff5f5f0898716539f2be8f38e0c5aa59f22c994b439c2381fb650c92cdb"
TEAMS = frozenset({"g", "s", "db", "d", "t", "c", "h", "f", "b", "e", "l", "m"})
FIELDS = ("G", "W", "L", "T", "RF", "RA")
LABELS = ("【JERA セ・リーグ公式戦】", "【パーソル パ・リーグ公式戦】", "【日本生命セ・パ交流戦】")
GAME_URL = re.compile(r"https://npb\.jp/scores/2026/(?P<md>\d{4})/(?P<home>[a-z]+)-(?P<away>[a-z]+)-(?P<round>\d+)/")


def jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def regular(row):
    return row.get("year") == 2026 and row.get("title", "").startswith(LABELS)


def validate_game(row):
    if (not regular(row) or row.get("status") != "final" or row.get("check") is not True
            or row.get("synthetic") is True):
        raise ValueError("Not a checked final regular-season game")
    match = GAME_URL.fullmatch(row.get("url", ""))
    if (not match or row.get("date") != "2026" + match["md"]
            or not "20260327" <= row["date"] <= "20261008"
            or row.get("home") != match["home"] or row.get("away") != match["away"]
            or row["home"] not in TEAMS or row["away"] not in TEAMS or row["home"] == row["away"]):
        raise ValueError("Invalid game identity or season boundary")
    for side in ("away", "home"):
        score, innings = row.get(side + "_R"), row.get(side + "_inn")
        if type(score) is not int or score < 0 or not isinstance(innings, list) or not 5 <= len(innings) <= 12:
            raise ValueError("Invalid score or innings")
        if any(not (type(v) is int and v >= 0) and v not in (None, "X") for v in innings):
            raise ValueError("Invalid inning cell")
        if sum(v for v in innings if type(v) is int) != score:
            raise ValueError("Innings and score disagree")
    return row


def reconcile(original, updates, annual):
    source = [row for row in original if regular(row)]
    if len({row["url"] for row in source}) != len(source):
        raise ValueError("Duplicate original game URL")
    finals = {row["url"]: row for row in source if row["status"] == "final"}
    pending = {row["url"] for row in source if row["status"].startswith("other:")}
    if len(finals) != 847 or len(pending) != 2:
        raise ValueError("Unexpected original snapshot")
    if len(updates) != 11 or len({row["url"] for row in updates}) != 11:
        raise ValueError("Expected eleven unique final updates")
    finalised, added = [], []
    for row in updates:
        validate_game(row)
        url = row["url"]
        if url in finals:
            raise ValueError("Refusing to replace an already final original game")
        if url in pending:
            if row["date"] != "20261003":
                raise ValueError("Unexpected unfinished-game date")
            finalised.append(url)
        elif "20261004" <= row["date"] <= "20261008":
            added.append(url)
        else:
            raise ValueError("Update outside the approved remaining dates")
        finals[url] = row
    if set(finalised) != pending or len(added) != 9 or len(finals) != 858:
        raise ValueError("Regular-season completion mismatch")
    games = sorted(finals.values(), key=lambda row: (row["date"], row["url"]))
    totals = {t: dict(season=2026, team=t, **dict.fromkeys(FIELDS, 0)) for t in TEAMS}
    for row in games:
        validate_game(row)
        for side, opponent in (("home", "away"), ("away", "home")):
            item = totals[row[side]]
            rf, ra = row[side + "_R"], row[opponent + "_R"]
            item["G"] += 1
            item["RF"] += rf
            item["RA"] += ra
            item["W" if rf > ra else "L" if rf < ra else "T"] += 1
    official = {row["team"]: row for row in annual}
    if len(annual) != 12 or set(official) != TEAMS:
        raise ValueError("Expected twelve unique annual teams")
    comparisons = []
    for team in sorted(TEAMS):
        item = totals[team]
        if item["G"] != 143 or item["G"] != sum(item[k] for k in ("W", "L", "T")):
            raise ValueError("Incomplete team schedule")
        if official[team].get("season") != 2026:
            raise ValueError("Wrong annual season")
        for field in FIELDS:
            value = official[team].get(field)
            if type(value) is not int or item[field] != value:
                raise ValueError(f"Annual mismatch: {team} {field}")
            comparisons.append(dict(team=team, field=field, games_value=item[field], annual_value=value, match=True))
    result = {
        "schema": "aoi-2026-regular-season-reconciliation/1",
        "original_final_regular_games": 847,
        "finalised_october_3_urls": sorted(finalised),
        "added_october_4_to_8_urls": sorted(added),
        "games": len(games), "teams": len(totals), "games_per_team": 143,
        "games_by_update_date": dict(sorted(Counter(row["date"] for row in updates).items())),
        "annual_values_matched": len(comparisons), "annual_comparisons": comparisons,
        "raw_html_published": False, "postseason_included": False, "synthetic_included": False,
        "original_source_rewritten": False, "research_panel_recomputed": False,
    }
    return games, [totals[team] for team in sorted(totals)], result


def outputs():
    payload = ORIGINAL.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ORIGINAL_SHA:
        raise ValueError("Original snapshot hash mismatch")
    annual = json.loads((DATA / "observed/annual_totals.json").read_text(encoding="utf-8"))
    games, totals, report = reconcile(json.loads(payload), read_jsonl(DATA / "observed/game_updates.jsonl"), annual["rows"])
    report["input_sha256"] = {"original_games_raw.json": ORIGINAL_SHA}
    for name in ("observed/game_updates.jsonl", "observed/annual_totals.json", "provenance/acquisition.jsonl"):
        report["input_sha256"][name] = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
    return {
        DATA / "observed/games.jsonl": jsonl(games),
        DATA / "derived/team_totals.jsonl": jsonl(totals),
        DATA / "provenance/reconciliation.json": json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare without writing")
    args = parser.parse_args()
    for path, content in outputs().items():
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale output: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print("858 regular-season games; 12 teams x 143; 72 annual values matched")


if __name__ == "__main__":
    main()
