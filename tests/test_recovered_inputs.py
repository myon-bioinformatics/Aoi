"""復元した入力と入口の検査（旧 5 本をまとめた。節の頭に旧ファイルの名前を書いた）。

標準ライブラリだけで走らせる検査（python -S -m unittest）は test_research_inputs.py に置き、こちらは pytest で走らせる。
"""

import hashlib
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import warnings
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZipInfo

import polars as pl
import pytest
from queryu import Cache
from research_loop.exploration import Explorer, plan
from scripts import research_inputs as season
from scripts.research_inputs import validate_member_path, validated_zip, verify_source


# ==== zip（旧 test_recovered_zip.py）
# Malformed archives stay in memory; validation never extracts their members.


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "cycles/c001-chunichi/recovered-inputs/README.md"


def _archive(entries):
    buffer = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # intentional duplicate fixtures
        with ZipFile(buffer, "w") as archive:
            for name, attributes, content in entries:
                member = ZipInfo(name)
                member.external_attr = attributes
                archive.writestr(member, content)
    buffer.seek(0)
    return buffer


def _no_extraction(*args, **kwargs):
    pytest.fail("Validation must not extract ZIP members")


@pytest.fixture(autouse=True)
def forbid_extraction(monkeypatch):
    monkeypatch.setattr(ZipFile, "extract", _no_extraction)
    monkeypatch.setattr(ZipFile, "extractall", _no_extraction)


@pytest.mark.parametrize("name", [
    "", "/absolute", "//server/share", "../escape", "a/../escape", "./file",
    "a/./file", "a//file", "a//", "a/..", "C:/escape", "C:escape",
    "a/C:escape", "a/file:stream", "\\\\server\\share", "a\\..\\escape",
    "a\\file", "file\x00hidden", "line\nfeed", "tab\tname", "delete\x7f",
    "a/CON", "nul.txt", "con .txt", "COM1.txt", "LPT9", "COM¹", "LPT².txt",
    "a/conin$", "a/CONOUT$", "trailing.", "trailing ", "a. /file",
    "a?.txt", "a*.txt", 'a".txt', "a|b", "a<b", "a>b",
    "data/synthetic/../../escape",
])
def test_reject_unsafe_original_paths(name):
    with pytest.raises(ValueError):
        validate_member_path(name)


@pytest.mark.parametrize("name", [
    "../escape", "/absolute", "//server/share", "C:escape", "a/file:stream",
    "a\\..\\escape", "a//b", "a/./b", "a/../b", "nul.json", "trailing.",
    "data/synthetic/../../escape",
])
def test_reject_bad_archive_before_any_member_read(name, monkeypatch):
    archive = _archive([("safe.json", 0, b"safe"), (name, 0, b"bad")])
    monkeypatch.setattr(ZipFile, "read", _no_extraction)
    with pytest.raises(ValueError):
        with validated_zip(archive):
            pytest.fail("Unsafe archive was yielded to the caller")


def test_nul_hidden_by_zipinfo_filename_is_rejected():
    # Writing ZipInfo('a\0b') would already truncate it. Patch both local and
    # central names, without changing their lengths, to model an input archive.
    content = _archive([("safeXhidden", 0, b"data")]).getvalue()
    content = content.replace(b"safeXhidden", b"safe\x00hidden")
    with ZipFile(io.BytesIO(content)) as archive:
        member = archive.infolist()[0]
        assert member.filename == "safe"
        assert member.orig_filename == "safe\x00hidden"
    with pytest.raises(ValueError):
        with validated_zip(io.BytesIO(content)):
            pytest.fail("NUL-containing name was accepted")


@pytest.mark.parametrize("kind", [stat.S_IFLNK, stat.S_IFIFO, stat.S_IFCHR,
                                       stat.S_IFBLK, stat.S_IFSOCK])
@pytest.mark.parametrize("creator", [0, 3, 19])
def test_reject_special_types_regardless_of_creator(kind, creator):
    buffer = io.BytesIO()
    member = ZipInfo("data/synthetic/link")
    member.create_system = creator
    member.external_attr = (kind | 0o644) << 16
    with ZipFile(buffer, "w") as archive:
        archive.writestr(member, b"../../outside")
    buffer.seek(0)
    with pytest.raises(ValueError, match="Special ZIP member type"):
        with validated_zip(buffer):
            pytest.fail("Special member was accepted")


@pytest.mark.parametrize("name, attributes, content", [
    ("directory", (stat.S_IFDIR | 0o755) << 16, b""),
    ("file/", (stat.S_IFREG | 0o644) << 16, b""),
    ("directory", 0x10, b""),
    ("directory/", 0x10, b"data"),
    ("volume", 0x08, b""),
    ("junction/", 0x410, b""),
    ("file", (stat.S_IFREG | stat.S_ISUID | 0o755) << 16, b""),
    ("file", (stat.S_IFREG | stat.S_ISGID | 0o755) << 16, b""),
    ("directory/", (stat.S_IFDIR | stat.S_ISVTX | 0o755) << 16, b""),
])
def test_reject_conflicting_or_dangerous_attributes(name, attributes, content):
    with pytest.raises(ValueError):
        with validated_zip(_archive([(name, attributes, content)])):
            pytest.fail("Conflicting member was accepted")


@pytest.mark.parametrize("names", [
    ["same", "same"], ["same/", "same/"], ["a", "a/"], ["A.json", "a.json"],
    ["caf\u00e9", "cafe\u0301"], ["a", "a/b"], ["a/b", "a"],
    ["a/b/", "A"], ["a/b", "A/B/"],
])
def test_reject_duplicates_aliases_and_file_parent_conflicts(names):
    with pytest.raises(ValueError):
        with validated_zip(_archive([(name, 0, b"") for name in names])):
            pytest.fail("Ambiguous archive was accepted")


def test_accept_regular_files_and_deliberate_directory_forms():
    entries = [
        ("unix/", (stat.S_IFDIR | 0o755) << 16, b""),
        ("unix/run.sh", (stat.S_IFREG | 0o755) << 16, b"script"),
        ("dos/", 0x10, b""),
        ("dos/file.txt", 0x20, b"dos"),
        ("unspecified/", 0o755 << 16, b""),
        ("unspecified/data.json", 0o600 << 16, b"{}"),
        ("ordinary/\u65e5\u672c\u8a9e.json", 0, b"{}"),
        ("ordinary/COM10.txt", 0, b"not reserved"),
    ]
    with validated_zip(_archive(entries)) as archive:
        assert [archive.read(name) for name, _, _ in entries] == [
            content for _, _, content in entries
        ]


def _restore_fixture(tmp_path, unsafe_index=None):
    members = ["data/part2/games_raw.json", "v2/season.jsonl"]
    catalog = {"archives": []}
    for index, member in enumerate(members):
        payload = b"[]" if index == 0 else b'{"season": 2025}\n'
        entries = [(member, 0, payload)]
        if unsafe_index == index:
            entries.append(("../outside", 0, b"must not be written"))
        content = _archive(entries).getvalue()
        path = tmp_path / f"source-{index}.zip"
        path.write_bytes(content)
        catalog["archives"].append({
            "repository_path": str(path), "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "selected_member": {"bytes": len(payload),
                                "sha256": hashlib.sha256(payload).hexdigest()},
        })
    manifest = tmp_path / "cycles/c001-chunichi/recovered-inputs/manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps(catalog))
    return README.read_text(encoding="utf-8").split("```python\n", 1)[1].split("```", 1)[0]


@pytest.mark.parametrize("unsafe_index", [0, 1])
def test_documented_restore_validates_all_members_before_copy(tmp_path, monkeypatch, unsafe_index):
    code = _restore_fixture(tmp_path, unsafe_index)
    sentinel = tmp_path / "outside"
    sentinel.write_bytes(b"unchanged")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="Unsafe ZIP member path"):
        exec(compile(code, str(README), "exec"), {})
    output = ("observed/games_raw.json" if unsafe_index == 0
              else "derived-annual/season.jsonl")
    assert not (tmp_path / "data/recovered-inputs" / output).exists()
    assert sentinel.read_bytes() == b"unchanged"


def test_documented_restore_is_repeatable_and_refuses_different_data(tmp_path, monkeypatch):
    code = _restore_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)
    exec(compile(code, str(README), "exec"), {})
    exec(compile(code, str(README), "exec"), {})
    output = tmp_path / "data/recovered-inputs/observed/games_raw.json"
    assert output.read_bytes() == b"[]"
    output.write_bytes(b"keep this")
    with pytest.raises(ValueError, match="Refusing to overwrite different data"):
        exec(compile(code, str(README), "exec"), {})
    assert output.read_bytes() == b"keep this"


@pytest.mark.parametrize("directory, dangling", [(False, False), (False, True),
                                                (True, False), (True, True)])
def test_documented_restore_refuses_output_symlinks(tmp_path, monkeypatch, directory, dangling):
    code = _restore_fixture(tmp_path)
    output = tmp_path / "data/recovered-inputs/observed/games_raw.json"
    link = output.parent if directory else output
    target = tmp_path / "outside-target"
    link.parent.mkdir(parents=True)
    if not dangling:
        if directory:
            target.mkdir()
            (target / "games_raw.json").write_bytes(b"[]")
        else:
            target.write_bytes(b"[]")
    link.symlink_to(target, target_is_directory=directory)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="Refusing symlink output path"):
        exec(compile(code, str(README), "exec"), {})
    assert sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*")) == before
    assert target.exists() is not dangling
    if not dangling:
        assert (target / "games_raw.json" if directory else target).read_bytes() == b"[]"


def test_helper_imports_without_site_packages():
    result = subprocess.run(
        [sys.executable, "-S", "-c",
         "from scripts.research_inputs import validate_member_path; "
         "validate_member_path('data/synthetic/safe.json')"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


# ==== provenance（旧 test_recovery_provenance.py）
# A self-consistent hash rewrite must still fail against independent history.


def test_provenance_rejects_consistent_rebaseline(tmp_path):
    source = tmp_path / 'source.py'
    source.write_bytes(b'changed CLI')
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    # Both the recorded hash and current file agree, but history says otherwise.
    with pytest.raises(ValueError, match='pinned history'):
        verify_source(tmp_path, 'source.py', current, [], b'original CLI')


def test_provenance_requires_both_historical_and_current_bytes(tmp_path):
    old, current = b'original CLI', b'changed CLI'
    (tmp_path / 'source.py').write_bytes(current)
    recorded = hashlib.sha256(old).hexdigest()
    row = dict(path='source.py', evidence_sha256=recorded,
               current_sha256=hashlib.sha256(current).hexdigest(),
               artifacts_regenerated=False, inputs_regenerated=False, reason='CLI-only change')
    verify_source(tmp_path, 'source.py', recorded, [row], old)
    for rows in ([], [row, row], [{**row, 'current_sha256': '0'*64}],
                 [{**row, 'artifacts_regenerated': True}], [{**row, 'reason': ''}]):
        with pytest.raises(ValueError):
            verify_source(tmp_path, 'source.py', recorded, rows, old)
    (tmp_path / 'source.py').write_bytes(old)
    with pytest.raises(ValueError, match='stale'):
        verify_source(tmp_path, 'source.py', recorded, [row], old)


# ==== entrypoints（旧 test_recovery_entrypoints.py）
# Recovered entry points must work without pytest's injected import paths.


def run(args, cwd):
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, env=env,
                          text=True, capture_output=True, timeout=30)


def test_recovered_fielding_source_runs_through_real_offline_cli(tmp_path):
    head = ['チーム', '守備率', '試合', '守備機会', '刺殺', '補殺', '失策', '併殺・参加', '併殺・球団', '捕逸']
    row = ['中日', '.991', '143', '5488', '3788', '1648', '52', '328', '122', '10']
    html = '<table>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in [head, row]) + '</table>'
    cache = tmp_path / 'cache'
    Cache(cache).put('2025_c', 'https://npb.jp/bis/2025/stats/tmf_c.html', '2025', 200,
                     html.encode(), {})
    out = tmp_path / 'observed.md'
    result = run([ROOT/'blueprobe/blueprobe.py', '--source', 'npb_team_fielding',
                  '--cache', cache, '--out', out], tmp_path)
    assert result.returncode == 0, result.stderr
    assert 'npb_team_fielding' in out.read_text() and '要確認' in out.read_text()
    # Incomplete six-team data is visible, and strict mode must reject it.
    strict = run([ROOT/'blueprobe/blueprobe.py', '--source', 'npb_team_fielding',
                  '--cache', cache, '--strict'], tmp_path)
    assert strict.returncode == 1 and '取りこぼし' in strict.stderr


def test_recovered_next_cli_reads_frozen_results_from_another_directory(tmp_path):
    result = run([ROOT/'pythdragoras/next_seeds.py', 'next',
                  ROOT/'cycles/c001-chunichi/outputs/propositions.jsonl', '--id', 'P1'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert 'P1 ' in result.stdout and '道筋' in result.stdout


@pytest.mark.parametrize('command', ['score_report', 'game_state', 'preclinch_flow'])   # 旧 render_<command>.py
def test_recovered_renderers_import_without_pytest_paths(tmp_path, command):
    result = run([ROOT/'research/gpt-r001-score-allocation/render_score_report.py', command, '--help'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert '--output' in result.stdout


def test_research_loop_and_dragowing_package_coexist_in_clean_process():
    code = '''
import research_loop.feedback
import dragowing.export
import dragowing.chrome_pipe
from dragowing.research_report import render_report
assert callable(render_report)
'''
    result = run(['-c', code], ROOT)
    assert result.returncode == 0, result.stderr


# ==== season（旧 test_season_2026.py）
# Offline completeness/provenance checks; not an independent live NPB replay.


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


# ==== bundle（旧 test_research_input_bundle.py）
# Real c001 bundle contracts: no acquisition, publication, or live activation.


# Integration always uses the imported owner tree. During development the owner
# checkout can be selected without patching Aoi's child subtree.
ENGINE = Path(os.environ.get('AOI_BUNDLE_WORKER', ROOT / 'nagoyaction/inbox/worker.py'))
spec = importlib.util.spec_from_file_location('bundle_worker', ENGINE)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


@pytest.fixture
def selected(tmp_path):
    root = tmp_path / 'aoi'
    cycle = root / 'cycles/c001-chunichi'
    shutil.copytree(ROOT / 'cycles/c001-chunichi/input-bundles', cycle / 'input-bundles')
    for name in ('analysis.toml', 'propositions.toml', 'sets.toml', 'outputs/season.jsonl'):
        dest = cycle / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'cycles/c001-chunichi' / name, dest)
    for name in ('analysis.toml', 'propositions.toml', 'outputs/season.jsonl'):
        dest = cycle / 'from-cycle-001' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'cycles/c001-chunichi/from-cycle-001' / name, dest)
    return root, cycle


def load(root, cycle):
    bundle = w.resolve_bundle(root, cycle, 'extended-v1')
    return Explorer(cycle, plan('E1', cycle, inputs=bundle), inputs=bundle)


def edit(selected, role, change):
    root, cycle = selected
    bundle = w.resolve_bundle(root, cycle, 'extended-v1')
    path = bundle['paths'][role]
    change(path)
    # Deliberately repin changed files: semantic checks must also reject broken
    # inputs when an editor has updated the manifest hashes.
    manifest = bundle['manifest']
    data = json.loads(manifest.read_text())
    data['sha256'][role] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))


def test_real_c001_validates_every_reference_and_keeps_canonical_bytes(selected):
    root, cycle = selected
    before = {str(p): p.read_bytes() for p in cycle.rglob('*') if p.is_file()}
    explorer = load(root, cycle)
    report = explorer.input_validation
    assert (report['propositions'], report['sets'], report['expressions'], report['rows']) == (210, 32, 31, 168)
    assert explorer.included.height == 156 and explorer.excluded.height == 12
    assert report['excluded_rows'] == 12
    assert report['null_counts']  # explicit unknown observations are retained
    assert len(report['required_columns']) > 100
    assert before == {str(p): p.read_bytes() for p in cycle.rglob('*') if p.is_file()}


@pytest.mark.parametrize('mutation,match', [
    ('canonical_season', 'missing columns'), ('canonical_props', '命題がない'),
    ('canonical_analysis', 'configuration'), ('missing_row_column', 'missing columns'),
    ('missing_all_column', 'missing columns'), ('missing_reference', '命題がない'),
    ('missing_confirmation', 'configuration'), ('exclusion', 'configuration'),
    ('duplicate_unit', 'units mismatch'), ('type', 'incompatible type'),
    ('bool_metric', 'incompatible type'), ('nonfinite', 'nonfinite|JSON|json|TapeError'),
    ('unselected_expression', '集合|unknown|存在|定義'), ('missing_context', 'missing columns'),
])
def test_broken_re_pinned_bundles_fail_before_initial_state(selected, mutation, match):
    root, cycle = selected
    def rewrite_rows(path, fn):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        fn(rows)
        path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    if mutation.startswith('canonical_'):
        role = {'canonical_season': 'season', 'canonical_props': 'propositions', 'canonical_analysis': 'analysis'}[mutation]
        canonical = {'season': 'outputs/season.jsonl', 'propositions': 'propositions.toml', 'analysis': 'analysis.toml'}[role]
        edit(selected, role, lambda p: shutil.copyfile(cycle / canonical, p))
    elif mutation in ('missing_row_column', 'missing_all_column', 'type', 'duplicate_unit', 'missing_context', 'bool_metric', 'nonfinite'):
        def change(rows):
            if mutation == 'missing_row_column':
                del rows[0]['upper_half']
            elif mutation == 'missing_all_column':
                for row in rows:
                    del row['upper_half']
            elif mutation == 'missing_context':
                # Required by P1 even though E1 does not use it.
                del rows[0]['rank_pythag']
            elif mutation in ('type', 'bool_metric', 'nonfinite'):
                for row in rows:
                    row['rd'] = {'type': 'incompatible', 'bool_metric': True, 'nonfinite': float('nan')}[mutation]
            else:
                rows[0] = rows[1]
        edit(selected, 'season', lambda p: rewrite_rows(p, change))
    elif mutation == 'missing_reference':
        edit(selected, 'sets', lambda p: p.write_text(p.read_text().replace('from = "P147"', 'from = "P9999"')))
    elif mutation == 'unselected_expression':
        edit(selected, 'sets', lambda p: p.write_text(p.read_text().replace('expr = "F52"', 'expr = "NO_SUCH_SET"')))
    elif mutation == 'missing_confirmation':
        edit(selected, 'analysis', lambda p: p.write_text(p.read_text().replace('"P52",', '"P9999",')))
    else:
        edit(selected, 'analysis', lambda p: p.write_text(p.read_text().replace('season = 2020', 'season = 2019')))
    with pytest.raises((ValueError, pl.exceptions.PolarsError), match=match):
        load(root, cycle)


def cli(state, steps):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('GITHUB_', 'AOI_RESEARCH_'))}
    env.update(AOI_RESEARCH_ENABLED='1', AOI_RESEARCH_ACTOR='local-offline-test',
               AOI_RESEARCH_ALLOWED_ACTORS='["local-offline-test"]', GITHUB_REPOSITORY='myon-bioinformatics/Aoi')
    result = subprocess.run([sys.executable, str(ENGINE), 'worker', '--root', str(ROOT),
        '--cycle', 'c001-chunichi', '--input-bundle', 'extended-v1', '--seed', 'E1',
        '--seconds', '30', '--max-steps', str(steps), '--state-dir', str(state)],
        env=env, capture_output=True, text=True, timeout=35)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_real_c001_offline_worker_resumes_without_mixing_or_source_writes(tmp_path):
    cycle = ROOT / 'cycles/c001-chunichi'
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in cycle.rglob('*') if p.is_file()}
    whole, resumed = tmp_path / 'whole', tmp_path / 'resumed'
    report = cli(whole, 5)
    cli(resumed, 2)
    cli(resumed, 3)
    a, b = w.load_checkpoint(whole / 'checkpoint.json'), w.load_checkpoint(resumed / 'checkpoint.json')
    assert a == b and report['cursor'] == 4
    assert a['state']['input_validation']['sets'] == 32
    assert any('coverage' in r for r in a['state']['results'])
    assert all('error' not in r or '空集合の式' in r['error'] for r in a['state']['results'])
    assert all(r['exploratory'] and not r.get('independently_confirmed', False) for r in a['state']['results'])
    assert a['manifest']['input_bundle'] == 'extended-v1'
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in cycle.rglob('*') if p.is_file()}


@pytest.mark.parametrize("corruption", ["hash", "semantic"])
def test_real_cli_rejects_bad_bundle_without_checkpoint(selected, tmp_path, corruption):
    root, cycle = selected
    for folder in ("research_loop", "pythdragoras"):
        shutil.copytree(ROOT / folder, root / folder, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for name in ("uv.lock", "pyproject.toml"):
        shutil.copyfile(ROOT / name, root / name)
    if corruption == "hash":
        p = cycle / "from-cycle-001/analysis.toml"
        p.write_text(p.read_text() + "\n# changed")
    else:
        edit(selected, "sets", lambda p: p.write_text(p.read_text().replace('from = "P147"', 'from = "P9999"')))
    state = tmp_path / "refused"
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "AOI_RESEARCH_"))}
    env.update(AOI_RESEARCH_ENABLED="1", AOI_RESEARCH_ACTOR="local-offline-test",
               AOI_RESEARCH_ALLOWED_ACTORS='["local-offline-test"]', GITHUB_REPOSITORY="myon-bioinformatics/Aoi")
    result = subprocess.run([sys.executable, str(ENGINE), "worker", "--root", str(root),
        "--cycle", "c001-chunichi", "--input-bundle", "extended-v1", "--seed", "E1",
        "--seconds", "30", "--max-steps", "1", "--state-dir", str(state)],
        env=env, capture_output=True, text=True, timeout=35)
    assert result.returncode == 1 and ("hash mismatch" in result.stderr or "P9999" in result.stderr)
    assert not (state / "checkpoint.json").exists()
