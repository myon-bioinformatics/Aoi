"""Aoi のリポジトリの検査（標準ライブラリだけ。python -S で走る）。

    python -S scripts/repo_checks.py <処理> [その処理の引数]

処理: action_uses（GitHub Actions の uses を親の書き方と照合）、shared_tools_lock（shared-tools.lock.json の sha256 と共有ツールのバイト）、
shared_tool_consumers（子が使う共有ツールの写しと各子のロック）、lab_nano_environment（オフラインのラボの依存の集合）。
旧 check_<処理>.py の 1 本が 1 つのサブコマンド。説明と引数は各関数の説明（旧ファイルの冒頭）にある。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from importlib import metadata
from pathlib import Path
from urllib.parse import quote


# ==== action_uses（旧 check_action_uses.py）

ACTION_USES_DOC = """Aoi の GitHub Actions uses を親リポジトリの書き方と照合する。

検査するのは Aoi 自身の .github/workflows と、child-heads.json に登録した子（prefix）の
.github/workflows。子は独立したリポジトリにもなるので、同じ書き方に揃える。

親 myon-bioinformatics/myon-bioinformatics の active workflow（2026-10-20）:

- actions/*（checkout、setup-*、cache、upload/download-artifact などすべて）は、
  そのリリースの 40 桁 commit SHA と `# vX.Y.Z`（2026-10-31 myon さんの判断で統一）。
  例: checkout v7.0.1、setup-python v7.1.0、setup-node v7.1.0。
- 同じリポジトリの reusable workflow は相対パス。
- 他リポジトリの reusable workflow は 40 桁 SHA。
- 更新は Dependabot の github-actions（毎月、Asia/Tokyo、PR は 5 件まで）。
  action の uses を書き換える autofix workflow は無い。
- 親の parent_pin_check は action のタグと SHA を見ない。親リポジトリ自身の
  40 桁ピンの統一と鮮度だけを見る。schedule と main への push は失敗、
  pull_request とそれ以外の push は警告。

astral-sh/setup-uv は親に無い。v10 の動くメジャータグも無いので、公式の
setup アクションと同じく最新リリースの SHA と `# vX.Y.Z` にする。

--check-hashes は、そのコメントのリリースタグが指す commit と SHA が
一致するかを見る。--warn のとき不一致は警告で終了 0。既定は終了 1。
API 自体が失敗したときは --warn でも終了 2。
"""

ROOT = Path(__file__).resolve().parents[1]
ACTION_USES_HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
PATCH = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
USES_LINE = re.compile(r"^[ \t]*(?:-[ \t]*)?uses:[ \t]*(?P<value>\S.*?)\s*$")
SETUP_SHA = (
    "actions/setup-python",
    "actions/setup-node",
    "astral-sh/setup-uv",
)
PARENT_PREFIX = "myon-bioinformatics/myon-bioinformatics/"


class HashCheckError(RuntimeError):
    """GitHub のタグ解決に失敗した。"""


def _split_uses(value: str) -> tuple[str, str]:
    text = value.strip()
    if text[:1] in {"'", '"'}:
        quote_char = text[0]
        end = text.find(quote_char, 1)
        if end == -1:
            return text, ""
        raw = text[1:end].strip()
        rest = text[end + 1 :].strip()
        if rest.startswith("#"):
            return raw, rest[1:].strip()
        return raw, ""
    if " #" in text:
        raw, comment = text.split(" #", 1)
        return raw.strip(), comment.strip()
    return text, ""


def _workflow_dirs(root: Path):
    """Aoi 自身と、child-heads.json の子（subtree の prefix）の workflow ディレクトリ。"""
    yield root / ".github" / "workflows"
    heads = root / "child-heads.json"
    if heads.is_file():
        for entry in json.loads(heads.read_text(encoding="utf-8"))["heads"].values():
            yield root / entry["optional"]["subtree_prefix"] / ".github" / "workflows"


def _iter_uses(root: Path):
    paths = [
        path
        for workflow_dir in _workflow_dirs(root)
        if workflow_dir.is_dir()
        for path in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))
    ]
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, 1):
            if line.lstrip().startswith("#"):
                continue
            match = USES_LINE.match(line)
            if match is None:
                continue
            raw, comment = _split_uses(match.group("value"))
            yield path, lineno, raw, comment


def _needs_sha(action: str) -> bool:
    return action in SETUP_SHA or action == "actions" or action.startswith("actions/")


def _style_problem(raw: str, comment: str) -> str | None:
    if raw.startswith("./") or raw.startswith("docker://"):
        return None
    if "@" not in raw:
        return "ref が無い"
    action, rev = raw.rsplit("@", 1)
    if action.startswith(PARENT_PREFIX):
        entry = action[len(PARENT_PREFIX) :]
        if (
            entry.startswith(".github/workflows/")
            and entry.endswith((".yml", ".yaml"))
            and ACTION_USES_HEX40.fullmatch(rev)
        ):
            return None
        return "親の reusable workflow は .github/workflows/*.yml@40桁SHA"
    if _needs_sha(action):
        if not ACTION_USES_HEX40.fullmatch(rev) or not PATCH.fullmatch(comment):
            return "actions/* と setup は 40 桁 SHA と # vX.Y.Z"
        return None
    return "親の active workflow に無い action"


def style_problems(root: Path) -> list[str]:
    found: list[str] = []
    for path, lineno, raw, comment in _iter_uses(root):
        problem = _style_problem(raw, comment)
        if problem:
            rel = path.relative_to(root).as_posix()
            found.append(f"{rel}:{lineno}: {problem} ({raw})")
    return found


def _github_json(url: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "aoi-action-uses",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise HashCheckError(f"GitHub API HTTP {exc.code} for {url}") from exc
    except urllib.error.URLError as exc:
        raise HashCheckError(f"GitHub API に到達できない: {exc.reason}") from exc
    if not isinstance(payload, dict):
        raise HashCheckError(f"GitHub API の応答が object でない: {url}")
    return payload


def github_tag_commit(repository: str, tag: str) -> str:
    """リリースタグが指す commit SHA。注釈タグは中の commit まで辿る。"""
    data = _github_json(
        f"https://api.github.com/repos/{repository}/git/ref/tags/{quote(tag, safe='')}"
    )
    obj = data.get("object")
    if not isinstance(obj, dict):
        raise HashCheckError(f"{repository}@{tag} の object が無い")
    kind = obj.get("type")
    sha = obj.get("sha")
    if kind == "commit" and isinstance(sha, str) and ACTION_USES_HEX40.fullmatch(sha):
        return sha.lower()
    if kind == "tag" and isinstance(obj.get("url"), str):
        tagged = _github_json(obj["url"])
        inner = tagged.get("object")
        if isinstance(inner, dict) and inner.get("type") == "commit":
            inner_sha = inner.get("sha")
            if isinstance(inner_sha, str) and ACTION_USES_HEX40.fullmatch(inner_sha):
                return inner_sha.lower()
    raise HashCheckError(f"{repository}@{tag} の commit を解決できない")


def hash_problems(root: Path, resolve=github_tag_commit) -> list[str]:
    """actions/* と setup の SHA が、コメントのリリースタグの commit と一致するか。"""
    found: list[str] = []
    resolved: dict[tuple[str, str], str] = {}
    for path, lineno, raw, comment in _iter_uses(root):
        if "@" not in raw:
            continue
        action, rev = raw.rsplit("@", 1)
        if not _needs_sha(action):
            continue
        if not ACTION_USES_HEX40.fullmatch(rev) or not PATCH.fullmatch(comment):
            continue
        # A subaction such as actions/cache/restore shares its repository tag.
        repository = "/".join(action.split("/")[:2])
        key = (repository, comment)
        if key not in resolved:
            resolved[key] = resolve(repository, comment).lower()
        if resolved[key] != rev.lower():
            rel = path.relative_to(root).as_posix()
            found.append(
                f"{rel}:{lineno}: {action}@{rev} は {comment} の commit {resolved[key]} と違う"
            )
    return found


def action_uses(argv: list[str] | None = None, resolve=github_tag_commit) -> int:
    parser = argparse.ArgumentParser(description=ACTION_USES_DOC.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--warn", action="store_true", help="不一致を警告にして終了コード 0")
    parser.add_argument(
        "--check-hashes",
        action="store_true",
        help="actions/* と setup の SHA をリリースタグの commit と照合する",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    found = style_problems(root)
    hash_error = None
    if args.check_hashes:
        try:
            found.extend(hash_problems(root, resolve))
        except HashCheckError as exc:
            hash_error = exc
    if hash_error is not None and not args.warn:
        for item in found:
            print(item, file=sys.stderr)
        print(f"::error::{hash_error}", file=sys.stderr)
        return 2
    if hash_error is not None:
        print(f"::warning::{hash_error}", file=sys.stderr)
        if not found:
            print("action uses のハッシュ照合は pull request では警告", file=sys.stderr)
            return 0
    if not found:
        print("action uses ok")
        return 0
    for item in found:
        if args.warn:
            print(f"::warning::{item}", file=sys.stderr)
        else:
            print(item, file=sys.stderr)
    if args.warn:
        print("action uses の不一致は pull request では警告", file=sys.stderr)
        return 0
    return 1


# ==== shared_tools_lock（旧 check_shared_tools_lock.py）

SHARED_TOOLS_LOCK_DOC = """shared-tools.lock.json の sha256 を、Aoi に置いた共有ツールのバイトと照合する。

schema は vendor-lock/1。各エントリは path、sha256、source（Aoi）、実際に使っている子（consumers、空も可）。
子の main の SHA は lock に書かない。--resolve-consumers のときだけ git ls-remote で
取り、child-heads.json の repository_id と GitHub の id を照合して、SHA を出す。
"""
LOCK_NAME = "shared-tools.lock.json"
SOURCE = "myon-bioinformatics/Aoi"
HEX64 = re.compile(r"[0-9a-f]{64}")
SHARED_TOOLS_LOCK_HEX40 = re.compile(r"[0-9a-f]{40}")
ENTRY_KEYS = {"path", "sha256", "source", "consumers"}


def _git_env() -> dict:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    return env


def load_lock(root: Path) -> dict:
    return json.loads((root / LOCK_NAME).read_text(encoding="utf-8"))


def shared_tools_lock_problems(root: Path, lock: dict | None = None) -> list[str]:
    """lock とファイルの不一致。空なら一致。"""
    found: list[str] = []
    if lock is None:
        try:
            lock = load_lock(root)
        except (OSError, json.JSONDecodeError) as exc:
            return [f"{LOCK_NAME} を読めない: {exc}"]
    if not isinstance(lock, dict) or lock.get("schema") != "vendor-lock/1" or set(lock) != {"schema", "files"}:
        return [f"{LOCK_NAME} は vendor-lock/1 の schema と files だけ"]
    files = lock["files"]
    if not isinstance(files, list) or not files:
        return [f"{LOCK_NAME} の files が空"]
    heads_path = root / "child-heads.json"
    try:
        heads = json.loads(heads_path.read_text(encoding="utf-8"))["heads"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        return [f"child-heads.json を読めない: {exc}"]
    paths = []
    for index, entry in enumerate(files):
        where = f"files[{index}]"
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            found.append(f"{where} のキーは path, sha256, source, consumers")
            continue
        path = entry["path"]
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in path.split("/"):
            found.append(f"{where} の path が相対パスでない")
            continue
        paths.append(path)
        if entry["source"] != SOURCE:
            found.append(f"{path}: source は {SOURCE}")
        consumers = entry["consumers"]
        if (not isinstance(consumers, list) or len(set(consumers)) != len(consumers)
                or not set(consumers) <= set(heads) or consumers != sorted(consumers)):
            found.append(f"{path}: consumers は child-heads.json の子から重複なしで昇順")
        sha = entry["sha256"]
        if not isinstance(sha, str) or not HEX64.fullmatch(sha):
            found.append(f"{path}: sha256 は 64 桁の hex")
            continue
        file = root / path
        if not file.is_file():
            found.append(f"{path}: ファイルがない")
            continue
        got = hashlib.sha256(file.read_bytes()).hexdigest()
        if got != sha:
            found.append(f"{path}: sha256 が違う {got} != {sha}")
    if paths != sorted(paths):
        found.append("files は path の昇順")
    if len(paths) != len(set(paths)):
        found.append("path が重複している")
    return found


def _ls_remote(repository: str) -> str:
    url = f"https://github.com/{repository}.git"
    out = subprocess.run(
        ["git", "ls-remote", url, "refs/heads/main"],
        capture_output=True, text=True, timeout=120, env=_git_env(), stdin=subprocess.DEVNULL,
    )
    if out.returncode:
        raise RuntimeError(f"git ls-remote {repository} failed: {out.stderr.strip()[:200]}")
    for line in out.stdout.splitlines():
        sha, ref = line.split()
        if ref == "refs/heads/main" and SHARED_TOOLS_LOCK_HEX40.fullmatch(sha):
            return sha
    raise RuntimeError(f"git ls-remote {repository} に refs/heads/main がない")


def _repository_id(repository: str) -> tuple[int, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "aoi-shared-tools"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(f"https://api.github.com/repos/{repository}", headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return int(data["id"]), str(data.get("full_name", ""))


def resolve_consumers(root: Path) -> str:
    """子の最新 main を解決し、repository id を照合して Markdown を返す。"""
    lock = load_lock(root)
    heads = json.loads((root / "child-heads.json").read_text(encoding="utf-8"))["heads"]
    consumers = sorted({name for entry in lock["files"] for name in entry["consumers"]})
    checkout = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, env=_git_env(),
    ).stdout.strip()
    lines = ["## Shared tool consumers", "", f"Aoi checkout `{checkout}`", ""]
    for name in consumers:
        expected = heads[name]["repository_id"]
        live_id, full_name = _repository_id(name)
        if live_id != expected or full_name.lower() != name.lower():
            raise SystemExit(f"repository id mismatch: {name} live={live_id} {full_name} expected={expected}")
        sha = _ls_remote(name)
        lines.append(f"- `{name}` `{sha}` (repository id `{expected}`)")
    lines.append("")
    return "\n".join(lines)


def shared_tools_lock(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=SHARED_TOOLS_LOCK_DOC.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--warn", action="store_true", help="不一致を警告にして終了コード 0")
    parser.add_argument("--resolve-consumers", action="store_true", help="子の main を ls-remote で解決する")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.resolve_consumers:
        print(resolve_consumers(root))
        return 0
    found = shared_tools_lock_problems(root)
    if not found:
        print(f"{LOCK_NAME} ok")
        return 0
    stream = sys.stderr
    for item in found:
        if args.warn:
            print(f"::warning::{item}", file=stream)
        else:
            print(item, file=stream)
    if args.warn:
        print(f"{LOCK_NAME} の不一致は pull request では警告", file=stream)
        return 0
    return 1


# ==== shared_tool_consumers（旧 check_shared_tool_consumers.py）

SHARED_TOOL_CONSUMERS_DOC = """Offline consumer inventory and integrity check, respecting each child's lock.

A child's recorded hash can legitimately differ from Aoi's current source.
This checks bytes against the child's own lock, not against today's Aoi.
Commit provenance and subtree equality remain separate checks.
"""


def relative(value):
    return (isinstance(value, str) and bool(value) and not value.startswith('/')
            and all(p not in ('', '.', '..') for p in value.split('/')))


def inside(root, value):
    return relative(value) and (root / value).resolve().is_relative_to(root.resolve())


def has_symlink(root, value):
    path = root
    for part in value.split('/'):
        path = path / part
        if path.is_symlink():
            return True
    return False


def shared_tool_consumers_problems(root: Path) -> list[str]:
    # Invalid local metadata must remain an ordinary diagnostic, including --warn.
    try:
        return _problems(root)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
        return [f'invalid shared-tool metadata: {exc}']


def _problems(root: Path) -> list[str]:
    heads = json.loads((root / 'child-heads.json').read_text())['heads']
    if not isinstance(heads, dict):
        return ['child-heads.json: heads must be an object']
    for repo, head in heads.items():
        if not isinstance(head, dict) or not isinstance(head.get('optional'), dict):
            return [f'child-heads.json: {repo}: expected head and optional objects']
    found = shared_tools_lock_problems(root)
    if found:
        return found
    shared = {e['path']: e for e in json.loads((root / 'shared-tools.lock.json').read_text())['files']}
    heads = json.loads((root / 'child-heads.json').read_text())['heads']
    actual = {path: set() for path in shared}
    for repo, head in heads.items():
        prefix = head.get('optional', {}).get('subtree_prefix')
        if not inside(root, prefix) or has_symlink(root, prefix):
            found.append(f'{repo}: invalid subtree_prefix')
            continue
        child = root / prefix
        registered = set()
        for filename in ('vendor.lock.json', 'shared-tools.lock.json'):
            lockfile = child / filename
            if not lockfile.exists() and not lockfile.is_symlink():
                continue
            if not inside(child, filename) or has_symlink(child, filename):
                found.append(f'{prefix}/{filename}: lock resolves outside child or is a symlink')
                continue
            try:
                document = json.loads(lockfile.read_text())
                if not isinstance(document, dict) or document.get('schema') != 'vendor-lock/1' or not isinstance(document.get('files'), list):
                    raise ValueError('expected vendor-lock/1 files')
                for entry in document['files']:
                    if not isinstance(entry, dict):
                        raise ValueError('entry must be an object')
                    if filename == 'vendor.lock.json':
                        if entry.get('repository') != SOURCE:
                            continue
                        source, destination = entry.get('source'), entry.get('destination')
                    else:
                        if entry.get('source') != SOURCE:
                            continue
                        destination = entry.get('path')
                        if not isinstance(destination, str) or not destination.startswith('vendor/aoi/'):
                            raise ValueError('shared destination must be under vendor/aoi/')
                        source = destination[len('vendor/aoi/'):]
                    if not relative(source) or not inside(child, destination):
                        raise ValueError('unsafe source/destination')
                    # A provenance lock can also register LICENSE or other assets.
                    # Account for them in the directory inventory, without inventing
                    # a shared-tool consumer declaration for a non-tool source.
                    if source in shared:
                        actual[source].add(repo)
                    elif filename == 'shared-tools.lock.json':
                        found.append(f'{prefix}/{destination}: source absent from shared tools: {source}')
                    if destination in registered:
                        found.append(f'{prefix}/{destination}: duplicate child lock destination')
                    registered.add(destination)
                    sha = entry.get('sha256')
                    file = child / destination
                    if not isinstance(sha, str) or not HEX64.fullmatch(sha):
                        found.append(f'{prefix}/{destination}: invalid child sha256')
                    elif has_symlink(child, destination):
                        found.append(f'{prefix}/{destination}: symlink child copy')
                    elif not file.is_file():
                        found.append(f'{prefix}/{destination}: missing child copy')
                    elif hashlib.sha256(file.read_bytes()).hexdigest() != sha:
                        found.append(f'{prefix}/{destination}: child lock sha256 mismatch')
            except (OSError, ValueError, TypeError) as exc:
                found.append(f'{prefix}/{filename}: {exc}')
        for file in (child / 'vendor/aoi').rglob('*'):
            if (file.is_file() or file.is_symlink()) and '__pycache__' not in file.parts and file.suffix != '.pyc':
                destination = file.relative_to(child).as_posix()
                if destination not in registered:
                    found.append(f'{prefix}/{destination}: copy missing from child shared-tool locks')
    for path, entry in shared.items():
        for repo in sorted(actual[path] - set(entry['consumers'])):
            found.append(f'{path}: missing consumer {repo}')
        for repo in sorted(set(entry['consumers']) - actual[path]):
            found.append(f'{path}: consumer without locked copy {repo}')
    return found


def shared_tool_consumers(argv=None):
    parser = argparse.ArgumentParser(description=SHARED_TOOL_CONSUMERS_DOC)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--warn', action='store_true')
    args = parser.parse_args(argv)
    errors = shared_tool_consumers_problems(args.root.resolve())
    for error in errors:
        print(('::warning::' if args.warn else '') + error, file=sys.stderr)
    if not errors:
        print('shared tool consumers ok')
    return int(bool(errors) and not args.warn)


# ==== lab_nano_environment（旧 check_lab_nano_environment.py）

LAB_NANO_ENVIRONMENT_DOC = """Fail closed when the offline lab lane's installed dependency set drifts.

This is not an installer or test runner. The unchanged uv lock remains the
source of versions; both unexpected additions and missing test plugins fail.
"""

EXPECTED = frozenset({
    'aoi', 'anyio', 'coverage', 'idna', 'iniconfig', 'packaging', 'pluggy',
    'pygments', 'pytest', 'selectolax',
})
OMITTED = frozenset({
    'certifi', 'h11', 'httpcore', 'httpx', 'markdown', 'numpy', 'polars',
    'polars-runtime-32',
})


def canonical_name(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()


def inspect_environment(lock: dict, installed: list[tuple[str, str]]) -> dict:
    versions: dict[str, set[str]] = {}
    for package in lock['package']:
        versions.setdefault(canonical_name(package['name']), set()).add(package['version'])
    actual: dict[str, list[str]] = {}
    for name, version in installed:
        actual.setdefault(canonical_name(name), []).append(version)
    errors = []
    for name in sorted(EXPECTED - actual.keys()):
        errors.append(f'missing installed package: {name}')
    for name in sorted(actual.keys() - EXPECTED):
        errors.append(f'unexpected installed package: {name}')
    for name, values in sorted(actual.items()):
        if len(values) != 1:
            errors.append(f'duplicate installed package: {name}')
        for version in values:
            if version not in versions.get(name, set()):
                errors.append(f'installed version absent from lock: {name}=={version}')
    # Removing a reviewed omission from the lock requires revisiting the lane,
    # rather than silently retaining an ineffective flag forever.
    for name in sorted((EXPECTED | OMITTED) - versions.keys()):
        errors.append(f'reviewed package absent from lock: {name}')
    return {'valid': not errors, 'errors': errors,
            'expected': sorted(EXPECTED), 'omitted': sorted(OMITTED),
            'installed': [{'name': name, 'versions': values}
                          for name, values in sorted(actual.items())]}


def lab_nano_environment(argv=None) -> int:
    parser = argparse.ArgumentParser(description=LAB_NANO_ENVIRONMENT_DOC)
    parser.add_argument('--lock', type=Path, default=Path('uv.lock'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    raw = args.lock.read_bytes()
    installed = [(d.metadata['Name'], d.version) for d in metadata.distributions()]
    report = inspect_environment(tomllib.loads(raw.decode('utf-8')), installed)
    if sys.platform != 'linux' or sys.version_info[:2] != (3, 15):
        report['errors'].append('this reviewed lane requires Linux and Python 3.15')
        report['valid'] = False
    report.update(python=sys.version, platform=sys.platform,
                  lock_sha256=hashlib.sha256(raw).hexdigest(),
                  environment_regular_file_bytes=sum(
                      p.stat().st_size for p in Path(sys.prefix).rglob('*')
                      if p.is_file() and not p.is_symlink()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['valid'] else 1


# ==== 入口
COMMANDS = {
    "action_uses": action_uses,
    "shared_tools_lock": shared_tools_lock,
    "shared_tool_consumers": shared_tool_consumers,
    "lab_nano_environment": lab_nano_environment,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="repo_checks.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"repo_checks.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
