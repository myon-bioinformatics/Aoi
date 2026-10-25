"""Malformed archives stay in memory; validation never extracts their members."""

import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import warnings
from zipfile import ZipFile, ZipInfo

import pytest

from scripts.recovered_zip import validate_member_path, validated_zip


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
         "from scripts.recovered_zip import validate_member_path; "
         "validate_member_path('data/synthetic/safe.json')"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
