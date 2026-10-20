"""Aoi-side NPB config and layout that the children no longer hold."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import aoi_npb
import aoi_paths


def test_npb_rules_presets_live_in_aoi():
    with pytest.raises(ValueError):
        aoi_npb.npb_rules(2020, 'CL', tuple('ABCDEF'), tuple('ABCDEF'))
    assert aoi_npb.npb_rules(2022, 'PL', tuple('ABCDEF'), tuple('ABCDEF')).wins_before_h2h is False
    assert aoi_npb.npb_rules(2025, 'CL', tuple('ABCDEF'), tuple('ABCDEF')).cs_slots == 3


def test_team_table_order_and_month_key_cover_the_same_codes():
    import re
    codes = set(aoi_npb.TEAMS.values())
    assert codes == set(aoi_npb.TEAM_ORDER) and len(aoi_npb.TEAM_ORDER) == 12
    assert aoi_npb.TEAM_ORDER[0] == "d"
    assert {"year", "month"} <= set(re.compile(aoi_npb.CALENDAR_MONTH_KEY).groupindex)
    assert set(aoi_npb.ANNUAL_AUDIT_RULES["opponents"].values()) == codes


def test_write_json_for_child_clis(tmp_path):
    path = aoi_npb.write_json("teams", tmp_path / "teams.json")
    assert json.loads(path.read_text(encoding="utf-8")) == aoi_npb.TEAMS
    rules = json.loads(aoi_npb.write_json("annual-audit-rules", tmp_path / "rules.json").read_text(encoding="utf-8"))
    assert rules["fixed_members"] == 6 and rules["extended_rounding"] == "truncate"


def test_results_ref_is_not_replaced_by_another_directory(tmp_path):
    root = tmp_path / "repo"
    configured = root / "cycles" / "c001-chunichi"
    configured.mkdir(parents=True)
    (configured / "pipeline.toml").write_text('out = "cycles/c001-chunichi/outputs"\n', encoding="utf-8")
    (root / "cycles" / "c001-chunichi" / "outputs").mkdir()
    with pytest.raises(FileNotFoundError, match="結果が読めない"):
        aoi_paths.resolve_results_dir(root, cycle="c001-chunichi", results_ref="cycle-001/chunichi")
    isolated = root / ".aoi-results" / "c001-chunichi" / "outputs"
    isolated.mkdir(parents=True)
    got = aoi_paths.resolve_results_dir(root, cycle="c001-chunichi", results_ref="cycle-001/chunichi")
    assert got == isolated
    explicit = tmp_path / "explicit"
    explicit.mkdir()
    assert aoi_paths.resolve_results_dir(root, explicit=explicit, cycle="other", results_ref="cycle-001/chunichi") == explicit
    assert aoi_paths.resolve_results_dir(root, cycle="c001-chunichi") == root / "cycles/c001-chunichi/outputs"


def test_ask_wrapper_passes_results_cycle_and_teams(capsys, monkeypatch):
    monkeypatch.delenv("AOI_RESULTS_REF", raising=False)
    monkeypatch.delenv("AOI_RESULTS_DIR", raising=False)
    code = aoi_paths.ask_main(["中日が判例の命題", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert "d" in payload["query"]["about"]
    assert code in (0, 1)


def test_npb_child_commands_receive_parent_defaults_and_keep_exit_status(monkeypatch):
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        if "--rules" in argv:
            rules = Path(argv[argv.index("--rules") + 1])
            assert json.loads(rules.read_text())["fixed_members"] == 6
        return subprocess.CompletedProcess(argv, 7)

    monkeypatch.setattr(aoi_npb.subprocess, "run", run)
    assert aoi_npb.main(["calendar", "--years", "2026", "--plan"]) == 7
    assert calls[-1][0][2:] == ["--source", "npb_calendar", "--month-key",
                                  aoi_npb.CALENDAR_MONTH_KEY, "--years", "2026", "--plan"]
    assert aoi_npb.main(["draw", "--results", "saved", "--out", "build"]) == 7
    argv, kwargs = calls[-1]
    assert argv[1:5] == ["-m", "dragowing", "--team-order", ",".join(aoi_npb.TEAM_ORDER)]
    assert kwargs["env"]["PYTHONPATH"].split(os.pathsep)[0] == str(aoi_npb.ROOT)
    assert aoi_npb.main(["annual-audit", "--years", "2026-2026"]) == 7
    assert not Path(calls[-1][0][3]).exists()  # temporary rules removed after the child exits


def test_npb_annual_cli_enforces_leagues_that_generic_cli_does_not(tmp_path):
    """An empty year must fail the NPB standings checks, even under python -S."""
    observed = tmp_path / "records.jsonl"
    observed.write_text("")
    observed.with_suffix(".manifest.json").write_text(json.dumps({
        "unknown": 0, "sha256": hashlib.sha256(b"").hexdigest(),
    }))
    out, annual = tmp_path / "audit.json", tmp_path / "annual.jsonl"
    result = subprocess.run([
        sys.executable, "-I", "-S", str(aoi_npb.ROOT / "aoi_npb.py"), "annual-audit",
        "--observations", str(observed), "--years", "2026-2026",
        "--out", str(out), "--annual-out", str(annual),
    ], cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 1, result.stdout + result.stderr
    audit = json.loads(out.read_text())
    assert sum(c["check"] == "standings_present" for c in audit["failures"]) == 4


def test_parent_calendar_pipeline_uses_shared_npb_settings():
    import tomllib

    pipeline = tomllib.loads((aoi_npb.ROOT / "cycles/c001-chunichi/pipeline.toml").read_text())
    for step in pipeline["step"]:
        if step["name"] in ("fetch", "observe"):
            assert step["run"][3:5] == ["aoi_npb.py", "calendar"]
            assert "--month-key" not in step["run"]
