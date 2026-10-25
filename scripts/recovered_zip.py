"""Read-only, stdlib-only member checks for the recovered input ZIPs.

Reject ambiguous paths rather than sanitizing them. This is not an extractor:
callers still choose fixed output paths and must not use extract/extractall.
"""

from contextlib import contextmanager
import stat
import unicodedata
from zipfile import ZipFile


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
