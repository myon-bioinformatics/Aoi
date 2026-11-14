"""研究の入力の検査（取得しない。手元に保存した入力・回収した ZIP・git の履歴だけを読む。標準ライブラリだけ）。

    python -S scripts/research_inputs.py <処理> [その処理の引数]

処理:
  saved_inputs  c001 の保存した年次の入力と、2026年の合計の作り直し（旧 check_c001_saved_inputs.py）
  season_2026   保存した 2026年の公式戦の観測の突き合わせ。--check なら書かずに比べる（旧 reconcile_season_2026.py）
  provenance    回収した証跡を、変えられない git の履歴と照合する（旧 audit_recovery_provenance.py）
  food_share    食費の割合のスナップショットの検査（旧 check_food_share_data.py）
部品: 回収した入力の ZIP の中身の検査（validate_member_path・validated_zip。旧 recovered_zip.py）。
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import stat
import subprocess
import sys
import unicodedata
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZipFile


# ==== season_2026（旧 reconcile_season_2026.py）

SEASON_2026_DOC = """Offline reconciliation of the preserved 2026 regular-season observations.

No network, inference, synthetic games, or changes to the original source ZIPs.
This separate dataset is not a QueRyu observation-format migration or a rerun
of the 409-column c001 research/model panel.
"""

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


def season_2026_main(argv=None):
    parser = argparse.ArgumentParser(description=SEASON_2026_DOC)
    parser.add_argument("--check", action="store_true", help="compare without writing")
    args = parser.parse_args(argv)
    for path, content in outputs().items():
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale output: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print("858 regular-season games; 12 teams x 143; 72 annual values matched")


def season_2026(argv=None):
    """reconcile_season_2026.py の入口（説明は SEASON_2026_DOC）。
    """
    season_2026_main(argv)


# ==== saved_inputs（旧 check_c001_saved_inputs.py）

def verify_payload(path, expected):
    payload = path.read_bytes()
    if len(payload) != expected['bytes'] or hashlib.sha256(payload).hexdigest() != expected['sha256']:
        raise ValueError(f'Saved input identity mismatch: {path}')
    return payload


def check(root=ROOT):
    root = Path(root)
    catalog = json.loads((root / 'cycles/c001-chunichi/recovered-inputs/manifest.json').read_text(encoding='utf-8'))
    observed, annual = [item['selected_member'] for item in catalog['archives']]
    verify_payload(root / observed['repository_path'], observed)
    panel = verify_payload(root / annual['existing_repository_path'], annual)
    rows = [json.loads(line) for line in panel.splitlines()]
    units = {(row['season'], row['team']) for row in rows}
    if len(rows) != annual['records'] or len(units) != len(rows):
        raise ValueError('Incomplete or duplicate annual panel')
    expected = outputs()
    for path, content in expected.items():
        if path.read_text(encoding='utf-8') != content:
            raise ValueError(f'Stale saved-data replay output: {path}')
    return {'mode': 'saved_input_verification', 'raw_source_replayed': False,
            'annual_units': len(rows), 'regular_season_2026_games': 858,
            'annual_values_matched': 72, 'source_requests': 0}


def saved_inputs_main():
    print(json.dumps(check(), sort_keys=True))


def saved_inputs(argv=None):
    """Check preserved annual inputs and replay 2026 totals without fetching data.

    No cache restoration, source HTML parsing, or research-model recomputation.
    """
    saved_inputs_main()


# ==== provenance（旧 audit_recovery_provenance.py）

HOLDOUT_REF = '50f508d44b1d13ce820dcdd3d5bd9ab837503512'
EXPERIMENT_REF = 'db15d3a33af701a1317871b80c63340cfcb33786'
OUT = 'cycles/c001-chunichi/outputs/exploratory'


def historical_bytes(root, ref, path):
    return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=root,
                          check=True, capture_output=True).stdout


def verify_source(root, path, recorded, rows, historical):
    """A divergence declaration cannot replace verification of original bytes."""
    if hashlib.sha256(historical).hexdigest() != recorded:
        raise ValueError(f'{path}: recorded hash does not match pinned history')
    current = hashlib.sha256((root / path).read_bytes()).hexdigest()
    matching = [r for r in rows if r['path'] == path]
    if current == recorded:
        if matching:
            raise ValueError(f'{path}: stale divergence')
        return
    if len(matching) != 1:
        raise ValueError(f'{path}: missing or duplicate divergence')
    row = matching[0]
    if (row['evidence_sha256'] != recorded or row['current_sha256'] != current
            or row['artifacts_regenerated'] is not False
            or row['inputs_regenerated'] is not False
            or not isinstance(row['reason'], str) or not row['reason'].strip()):
        raise ValueError(f'{path}: invalid divergence')


def audit(root=ROOT, read_history=historical_bytes):
    root = Path(root)
    manifest = json.loads((root / OUT / 'littlebit-holdout/holdout.provenance.json').read_text())
    if manifest['source_reference'] != HOLDOUT_REF:
        raise ValueError('holdout source_reference changed')
    rows = manifest.get('source_divergence', [])
    if set(r['path'] for r in rows) - set(manifest['source_sha256']):
        raise ValueError('unexpected holdout divergence path')
    for path, recorded in manifest['source_sha256'].items():
        verify_source(root, path, recorded, rows, read_history(root, HOLDOUT_REF, path))
    for group in ('inputs_sha256', 'artifacts_sha256'):
        for path, recorded in manifest[group].items():
            if hashlib.sha256((root / path).read_bytes()).hexdigest() != recorded:
                raise ValueError(f'{path}: frozen input/artifact changed')
    checked = len(manifest['source_sha256'])
    for folder, artifact, source, field in (
        ('league-laboratory', 'results.json', 'league_laboratory.py', 'inputs.analysis_sha256'),
        ('proposition-evaluation', 'seed-evaluation.json', 'proposition_seed_audit.py', 'analysis_sha256'),
    ):
        rel = f'{OUT}/{folder}/{artifact}'
        data = (root / rel).read_bytes()
        if data != read_history(root, EXPERIMENT_REF, rel):
            raise ValueError(f'{rel}: frozen experiment bytes differ from pinned history')
        sidecar = json.loads((root / OUT / folder / 'source-divergence.json').read_text())
        if sidecar['schema'] != 'aoi-source-divergence/1' or sidecar['artifact'] != artifact:
            raise ValueError(f'{rel}: incorrect sidecar identity')
        rows = sidecar['source_divergence']
        path = f'sakanalytics/{source}'
        if len(rows) != 1 or rows[0]['path'] != path or rows[0]['field'] != field:
            raise ValueError(f'{rel}: incorrect divergence coverage')
        recorded = json.loads(data)
        for key in field.split('.'):
            recorded = recorded[key]
        verify_source(root, path, recorded, rows, read_history(root, EXPERIMENT_REF, path))
        checked += 1
    return {'verified_sources': checked, 'frozen_experiments': 2,
            'holdout_reference': HOLDOUT_REF, 'experiment_reference': EXPERIMENT_REF}


def provenance(argv=None):
    """Verify recovery evidence against immutable Git history, without rewriting it.

    Requires the two pinned commits locally (CI checks out full history). No network,
    regeneration, fitting, rounding, or updates to any evidence file are performed.
    """
    print(json.dumps(audit(), sort_keys=True))


# ==== food_share（旧 check_food_share_data.py）

BASE = Path(__file__).resolve().parents[1] / 'research/staple-price-survey'


def coverage(rows):
    countries = sorted({r['country'] for r in rows})
    years = [int(r['year']) for r in rows]
    return (f'**{len(rows)} vertical rows** · **{len(countries)} ISO3** · '
            f'year span **{min(years)}–{max(years)}**.\n\nISO3: '
            + ', '.join(countries) + '.')


def validate_rows(rows, manifest):
    seen = set()
    groups = {}
    restored = []
    partial = {tuple(x['key']): set(x['indices']) for x in manifest['partial_series']}
    for r in rows:
        key = tuple(r[k] for k in ('country', 'date', 'variable', 'unit'))
        if key in seen:
            raise ValueError(f'duplicate observation: {key}')
        seen.add(key)
        match = re.fullmatch(r'(engel_share:food(?:_at_home)?)_([qd])(\d+)', r['legacy_variable'])
        if not match:
            raise ValueError('invalid legacy variable')
        metric, letter, index = match.groups()
        contract_key = json.dumps([r['country'], r['source'], letter], ensure_ascii=False, separators=(',', ':'))
        contract = manifest['source_contracts'].get(contract_key)
        if contract is None:
            raise ValueError(f'unreviewed source: {contract_key}')
        for field in ('stratifier', 'bucket_type', 'bucket_count'):
            if str(contract[field]) != r[field]:
                raise ValueError(f'source classification mismatch: {field}: {key}')
        if r['bucket_index'] != index or not 1 <= int(index) <= int(r['bucket_count']):
            raise ValueError('invalid bucket index')
        metric += "_" + contract["series_variant"] if contract["series_variant"] else ""
        canonical = f"{metric}_{r['stratifier']}_{r['bucket_type']}_{index}"
        if r['variable'] != canonical:
            raise ValueError('noncanonical variable')
        group = (r['country'], r['date'], r['source'], canonical.rsplit('_', 1)[0])
        indices, count = groups.setdefault(group, (set(), int(r['bucket_count'])))
        if int(index) in indices:
            raise ValueError('duplicate group bucket')
        indices.add(int(index))
        restored.append({f: r['legacy_variable'] if f == 'variable' else r[f]
                         for f in manifest['original_fields']})
    for key, (indices, count) in groups.items():
        if indices != partial.get(key, set(range(1, count + 1))):
            raise ValueError(f'incomplete or unexpected series: {key}')
    if not set(partial) <= set(groups):
        raise ValueError('missing partial series')
    digest = hashlib.sha256(json.dumps(restored, ensure_ascii=False, sort_keys=True,
                                      separators=(',', ':')).encode()).hexdigest()
    if digest != manifest['original_rows_sha256']:
        raise ValueError('original observations/source records changed')


def validate(base=BASE):
    for pack in ('adjacent_food_share_by_income', 'adjacent_food_share_urban_rural'):
        directory = base / pack
        path = directory / f'{pack}_vertical.csv'
        if gzip.decompress(path.with_suffix('.csv.gz').read_bytes()) != path.read_bytes():
            raise ValueError(f'CSV/gzip mismatch: {pack}')
        with path.open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        readme = (directory / f'{pack}_readme.md').read_text()
        expected = '<!-- coverage:start -->\n' + coverage(rows) + '\n<!-- coverage:end -->'
        if expected not in readme:
            raise ValueError(f'stale README coverage: {pack}')
        with (directory / '_coverage_by_country.csv').open(newline='') as stream:
            recorded = list(csv.DictReader(stream))
        actual = []
        for country in sorted({r['country'] for r in rows}):
            subset = [r for r in rows if r['country'] == country]
            years = [int(r['year']) for r in subset]
            actual.append({'country': country, 'n_rows': str(len(subset)),
                           'min_year': str(min(years)), 'max_year': str(max(years))})
        if actual != recorded:
            raise ValueError(f'stale coverage CSV: {pack}')
        if pack.endswith('by_income'):
            validate_rows(rows, json.loads((directory / 'classification.json').read_text()))
    return True


def food_share(argv=None):
    """Validate the food-share snapshot using only the Python standard library.
    """
    validate()
    print('Food-share classification, preservation, gzip and coverage: OK')


# ==== recovered_zip（旧 recovered_zip.py）

_DEVICES = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    prefix + digit for prefix in ("COM", "LPT") for digit in "123456789¹²³"
}


def validate_member_path(name):
    """Require an unambiguous relative POSIX name; allow one directory slash."""
    if not name or any(char in name for char in '\\:<>"|?*'):
        raise ValueError(f"Unsafe ZIP member path: {name!r}")
    if any(ord(char) < 32 or ord(char) == 127 for char in name):
        raise ValueError(f"Control character in ZIP member path: {name!r}")
    parts = (name[:-1] if name.endswith("/") else name).split("/")
    for part in parts:
        if (part in ("", ".", "..") or part.endswith((".", " "))
                or part.split(".", 1)[0].rstrip(" ").upper() in _DEVICES):
            raise ValueError(f"Unsafe ZIP member path: {name!r}")


def validate_zip_members(archive):
    """Validate every central-directory member before any payload is read.

    Missing Unix type bits are normal for ZipFile.writestr and DOS producers.
    Explicit types may only be regular files or slash-terminated directories.
    DOS directory bits, if present, must agree; special modes/types are rejected
    regardless of the creator OS. NFC/casefold aliases and file/parent conflicts
    are rejected so the same archive is unambiguous on common host filesystems.
    """
    names = {}
    files = set()
    for member in archive.infolist():
        # ZipInfo truncates filename at NUL (and can replace backslashes on
        # Windows). Inspect the original name before accepting that projection.
        name = member.orig_filename
        validate_member_path(name)
        if name != member.filename:
            raise ValueError(f"Normalized ZIP member name: {name!r}")
        is_dir = name.endswith("/")
        mode = member.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ValueError(f"Special ZIP member type: {name!r}")
        if mode & (stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX):
            raise ValueError(f"Special ZIP member permissions: {name!r}")
        if kind and (kind == stat.S_IFDIR) != is_dir:
            raise ValueError(f"Conflicting ZIP member type: {name!r}")
        dos_attributes = member.external_attr & 0xFFFF
        if dos_attributes & (0x08 | 0x400):  # volume label or reparse point
            raise ValueError(f"Special DOS ZIP member type: {name!r}")
        if dos_attributes & 0x10 and not is_dir:
            raise ValueError(f"Conflicting DOS directory member: {name!r}")
        if is_dir and member.file_size:
            raise ValueError(f"ZIP directory contains data: {name!r}")
        key = unicodedata.normalize("NFC", name.rstrip("/")).casefold()
        if key in names:
            raise ValueError(f"Duplicate or aliased ZIP members: {names[key]!r}, {name!r}")
        names[key] = name
        if not is_dir:
            files.add(key)
    for key, name in names.items():
        parts = key.split("/")
        if any("/".join(parts[:end]) in files for end in range(1, len(parts))):
            raise ValueError(f"ZIP file used as a parent directory: {name!r}")


@contextmanager
def validated_zip(source):
    """Open a ZIP for reading only and validate all members before yielding it."""
    with ZipFile(source) as archive:
        validate_zip_members(archive)
        yield archive


# ==== 入口
COMMANDS = {
    "saved_inputs": saved_inputs,
    "season_2026": season_2026,
    "provenance": provenance,
    "food_share": food_share,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="research_inputs.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"research_inputs.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
