"""Aoi-side NPB config and layout that the children no longer hold.

旧 test_annual_scope.py もここにまとめた（節の頭に旧ファイルの名前を書いた）。
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import aoi_npb
import aoi_paths
import pytest
from annual_scope import primary_cache, PRIMARY_YEARS
from npb_team_annual import pages
from queryu import Cache


# ==== npb（旧 test_aoi_npb.py）

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


def test_aoi_entry_appends_only_the_siblings_a_child_needs(tmp_path):
    import shlex
    import aoi
    root = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
    assert aoi.SIBLINGS == {
        "blueprobe": ("queryu",),
        "queryu": ("blueprobe",),
        "nagoyaction": (),
        "sakanalytics": ("pythdragoras",),
        "pythdragoras": (),
        "dragowing": ("pythdragoras", "queryu/ask"),
    }
    assert "dragowing" not in {rel for rels in aoi.SIBLINGS.values() for rel in rels}
    assert "." not in {rel for rels in aoi.SIBLINGS.values() for rel in rels}
    env = aoi.environment({"PYTHONPATH": "kept"}, child="queryu")
    assert env["PYTHONPATH"].split(os.pathsep) == ["kept", str((root / "blueprobe").resolve())]
    bare = aoi.environment({"PYTHONPATH": "kept"})
    assert bare["PYTHONPATH"].split(os.pathsep)[0] == "kept"
    assert str(root) not in bare["PYTHONPATH"].split(os.pathsep)
    assert str((root / "dragowing").resolve()) not in bare["PYTHONPATH"].split(os.pathsep)
    assert (env["AOI_ROOT"], env["AOI_RESEARCH_CYCLE"]) == (str(root), aoi_paths.DEFAULT_CYCLE)
    assert "POSIX" in aoi.__doc__ and "Windows" in aoi.__doc__
    assert aoi.command(["QueRyu", "--help"]) == [sys.executable, str(root / "queryu/queryu.py"), "--help"]
    assert aoi.command(["-m", "dragowing"]) == [sys.executable, "-m", "dragowing"]
    with pytest.raises(SystemExit):
        aoi.command(["no_such_child"])
    # 子プロセス: 別の作業フォルダから、PYTHONPATH なしで起動しても兄弟（blueprobe）を import できる
    clean = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "AOI_RESEARCH_CYCLE", "PYTHONSAFEPATH")}
    run = subprocess.run([sys.executable, str(root / "aoi.py"), "queryu", "--source", "npb_calendar", "--years", "2024",
                          "--cache", str(tmp_path / "cache"), "--offline", "--plan"],
                         cwd=tmp_path, env=clean, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    # 引数なし: このシェルだけに効く POSIX の export を出す（保存はしない）。Aoi の根と dragowing/ は入れない
    shown = subprocess.run([sys.executable, str(root / "aoi.py")], env=clean, capture_output=True, text=True, check=True).stdout
    assert shown.splitlines()[0] == f"export AOI_ROOT={shlex.quote(str(root))}"
    exported = dict(item.split("=", 1) for item in (shlex.split(line)[1] for line in shown.splitlines()))
    exported_paths = [entry for entry in exported["PYTHONPATH"].split(os.pathsep) if entry]
    assert str(root) not in exported_paths
    assert str((root / "dragowing").resolve()) not in exported_paths
    assert str((root / "blueprobe").resolve()) in exported_paths
    assert str((root / "pythdragoras").resolve()) in exported_paths


def test_import_aoi_does_not_shadow_the_dragowing_package():
    """Putting dragowing/ on sys.path makes dragowing.py win and hides dragowing.render."""
    root = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
    code = (
        "import sys\n"
        "first = sys.path[0]\n"
        "import aoi, dragowing.render\n"
        "import dragowing\n"
        "assert sys.path[0] == first, sys.path[0]\n"
        "assert getattr(dragowing, '__path__', None), getattr(dragowing, '__file__', None)\n"
        f"assert {str(root / 'dragowing')!r} not in sys.path\n"
        "print(dragowing.render.__file__)\n"
    )
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "PYTHONSAFEPATH")}
    run = subprocess.run([sys.executable, "-c", code], cwd=root, env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == str(root / "dragowing" / "render.py")


def test_dragowing_script_path_is_the_report_and_the_name_is_the_element_counter(tmp_path):
    root = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "AOI_RESEARCH_CYCLE", "PYTHONSAFEPATH")}
    report = subprocess.run([sys.executable, str(root / "aoi.py"), "dragowing/__main__.py", "--help"],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert report.returncode == 0, report.stderr
    assert "記録された結果を HTML" in report.stdout
    assert "Count HTML elements" not in report.stdout
    counter = subprocess.run([sys.executable, str(root / "aoi.py"), "dragowing", "--help"],
                             cwd=tmp_path, env=env, capture_output=True, text=True)
    assert counter.returncode == 0, counter.stderr
    assert "Count HTML elements" in counter.stdout


@pytest.mark.parametrize("flag", ["-I", "-S", "-E", "-P"])
def test_launcher_flags_still_run_the_element_counter(flag):
    root = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "AOI_ROOT", "AOI_RESEARCH_CYCLE", "PYTHONSAFEPATH")}
    run = subprocess.run([sys.executable, flag, str(root / "aoi.py"), "dragowing", "--help"],
                         cwd=root, env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert "Count HTML elements" in run.stdout


# ==== scope（旧 test_annual_scope.py）

def test_only_primary_cache_is_copied_and_reference_input_is_unchanged(tmp_path):
    cache = Cache(tmp_path/'reference')
    for year in (2012, *PRIMARY_YEARS):
        for lg in ('c', 'p'):
            for cat in ('std', 'tmb', 'tmp', 'tmf', 'archive'):
                key=f'{year}_{lg}_{cat}'
                url=next(url for k,url,_ in pages([year]) if k==key)
                cache.put(key,url,str(year),200,b'<html>team</html>',{})
    original = cache.manifest.read_bytes()
    out = tmp_path/'primary'
    assert primary_cache(cache.root, out) == 140
    assert cache.manifest.read_bytes() == original
    selected = Cache(out).latest()
    assert len(selected) == 140
    assert all(int(e['group']) in PRIMARY_YEARS for e in selected.values())
    for entry in selected.values():assert Cache(out).body_bytes(entry) == b'<html>team</html>'
    with pytest.raises(ValueError, match='empty'):primary_cache(cache.root, out)


def test_missing_primary_year_is_not_filled_from_reference_years(tmp_path):
    cache = Cache(tmp_path/'reference')
    cache.put('2012_c_std', 'https://npb.jp/2012', '2012', 200, b'<html></html>', {})
    with pytest.raises(ValueError, match='140'):primary_cache(cache.root, tmp_path/'primary')
