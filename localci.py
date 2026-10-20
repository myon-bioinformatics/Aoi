"""ローカル CI。GitHub Actions を待たずに、ワークフローとテストを手元で検査する。

  python localci.py run --repeat 10
  python localci.py run --repeat 10 --seed 7 --keep-going
  python localci.py run --self-tests
  python localci.py run --strict
  python localci.py resolve --github-output

`--repeat N` は同じ検査を N 回なぞらない。検査の一覧を seed でシャッフルし、
ほぼ等しい N 個のシャードに分け、1 ラウンドに 1 シャードだけ実行する。
全ラウンドが終わると各検査はちょうど一度だけ走る。失敗したラウンドで止まり、
ラウンド番号・シャードの中身・seed を出す。`--keep-going` で最後まで続ける。

既定の pytest は Aoi の `tests/` 全体。実行時に解決した SHA を `.localci/aoi`
に checkout し、HEAD がその SHA であることを確かめてから、このリポジトリの
tree を `nagoyaction/` に重ねる。`--self-tests` は Aoi を取らず
`tests/test_localci.py` だけを実行する。

特定の固定値で通る検査は `substitute` で、そのラウンドの seed から別の値に差し替える。
pytest では `-p localci_pytest` が同じ差し替えを monkeypatch する。

参照先（Aoi、myon-bioinformatics/myon-bioinformatics、vendor）の main SHA は
`git ls-remote` と GitHub API の repository id 照合で実行時に解決する。
SHA はソースに固定しない。`uses:` のピンが各アクションの最新リリースタグの
コミットと一致するかは、既定では報告だけする。`--strict` で失敗にする。

actionlint の版もソースに固定しない。実行のたびに最新リリースを解決し、
タグ・資産名・検証した sha256 を記録する。GitHub Actions では取得か検証に
失敗したら停止する。手元では、解決済みのタグだけ `go run ...@<tag>` に戻る。

標準ライブラリだけ（Python 3.11+）。
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


class LocalCIError(Exception):
    pass


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_USES = re.compile(r"^[ \t]*(?:-[ \t]*)?uses:[ \t]*(?P<value>.+?)[ \t]*$", re.M)

# repository id はコミット SHA ではなく、取り違えを防ぐための公開の数値 ID。
@dataclass(frozen=True)
class Source:
    key: str
    env: str
    repo: str
    repository_id: int | None


SOURCES = (
    Source("aoi", "AOI_SHA", "myon-bioinformatics/Aoi", 1402862784),
    Source("myon_bioinformatics", "MYON_BIOINFORMATICS_SHA", "myon-bioinformatics/myon-bioinformatics", 638801160),
    Source("markdown", "MARKDOWN_SHA", "myon-bioinformatics/markdown", 1374546518),
    Source("web_ui", "WEB_UI_SHA", "myon-bioinformatics/web-ui", 1382466695),
)

_OS = {"Linux": "linux", "Darwin": "darwin", "Windows": "windows"}
_ARCH = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64", "i386": "386", "i686": "386"}
_active_rng: random.Random | None = None
_substitutions: list[dict] = []


@dataclass(frozen=True)
class Check:
    id: str
    kind: str
    target: str
    file: str = ""
    ref: str = ""
    repo: str = ""


@dataclass
class Outcome:
    status: str
    detail: str
    inputs: list[dict]

    @property
    def ok(self) -> bool:
        return self.status == "pass"


@dataclass
class Resolved:
    source: Source
    sha: str
    how: str
    repository_id: int


@dataclass(frozen=True)
class ActionlintRecord:
    tag: str
    asset: str
    sha256: str
    binary: Path | None
    via: str


@dataclass
class RoundReport:
    number: int
    seed: int
    shard: list[str]
    passed: bool
    failed_check: str | None
    lines: list[str]


@dataclass
class PlanReport:
    master_seed: int
    rounds: list[RoundReport]
    stopped: bool

    @property
    def passed_rounds(self) -> int:
        return sum(1 for r in self.rounds if r.passed)


def substitute(name: str, value, draw):
    """固定値を返す。ラウンドの seed が有効なときは draw(rng) に差し替える。"""
    rng = _active_rng
    if rng is None:
        return value
    drawn = draw(rng)
    _substitutions.append({"name": name, "fixed": value, "value": drawn})
    return drawn


def take_substitutions() -> list[dict]:
    found = list(_substitutions)
    _substitutions.clear()
    return found


class use_seed:
    def __init__(self, seed: int):
        self.seed = seed
        self.previous = None

    def __enter__(self) -> random.Random:
        global _active_rng
        self.previous = _active_rng
        _substitutions.clear()
        _active_rng = random.Random(self.seed)
        return _active_rng

    def __exit__(self, *exc) -> None:
        global _active_rng
        _active_rng = self.previous


def mix_seed(master: int, *parts: object) -> int:
    material = ":".join([str(master), *map(str, parts)]).encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def split_shards(items: list, repeat: int, seed: int) -> list[list]:
    """seed でシャッフルし、各要素がちょうど一つのシャードに入るよう N 等分する。"""
    if repeat < 1:
        raise ValueError("repeat must be >= 1")
    ordered = list(items)
    random.Random(seed).shuffle(ordered)
    total = len(ordered)
    base, extra = divmod(total, repeat)
    shards: list[list] = []
    start = 0
    for i in range(repeat):
        size = base + (1 if i < extra else 0)
        shards.append(ordered[start:start + size])
        start += size
    return shards


def shard_for_round(items: list, repeat: int, round_no: int, seed: int) -> list:
    if not 1 <= round_no <= repeat:
        raise ValueError(f"round {round_no} is outside 1..{repeat}")
    return split_shards(items, repeat, seed)[round_no - 1]


def confidence_line(passed: int, total: int, completed: int, stopped: bool) -> str:
    text = f"confidence: {passed}/{total} rounds passed, {completed}/{total} completed"
    if stopped:
        return text + "; stopped"
    return text


def _strip_yaml_comment(text: str) -> str:
    if text[:1] in {"'", '"'}:
        quote = text[0]
        end = text.find(quote, 1)
        if end != -1:
            return text[1:end]
    mark = text.find(" #")
    if mark != -1:
        return text[:mark]
    return text


def parse_action_ref(value: str) -> dict | None:
    value = value.strip()
    if not value or value.startswith(("./", "docker://")) or "${{" in value:
        return None
    if "@" in value:
        left, ref = value.rsplit("@", 1)
    else:
        left, ref = value, ""
    parts = [p for p in left.split("/") if p]
    if len(parts) < 2:
        return None
    return {"repo": f"{parts[0]}/{parts[1]}", "path": "/".join(parts[2:]), "ref": ref.strip(), "raw": value}


def parse_uses(text: str) -> list[dict]:
    found = []
    for match in _USES.finditer(text):
        raw = _strip_yaml_comment(match.group("value").strip()).strip()
        parsed = parse_action_ref(raw)
        if parsed is None:
            continue
        parsed["line"] = text.count("\n", 0, match.start()) + 1
        found.append(parsed)
    return found


def classify_pin(ref: str, latest: tuple[str, str] | None) -> str:
    """latest は (tag, commit SHA)。リリースが無ければ None。

    SHA でないピンは unpinned。SHA でリリースが無ければ no-release。
    一致すれば match、違えば outdated。
    """
    if not SHA_RE.fullmatch(ref.lower()):
        return "unpinned"
    if latest is None:
        return "no-release"
    _tag, sha = latest
    if ref.lower() == sha.lower():
        return "match"
    return "outdated"


def pin_fails(status: str, strict: bool) -> bool:
    return strict and status in {"outdated", "unpinned"}


def github_token(env: dict | None = None) -> str:
    env = os.environ if env is None else env
    return env.get("GITHUB_TOKEN") or env.get("GH_TOKEN") or ""


def github_json(url: str, token: str, opener=urllib.request.urlopen, timeout: float = 60):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nagoyaction-localci"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise LocalCIError(f"GitHub API {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LocalCIError(f"GitHub API failed for {url}: {exc}") from exc


def fetch_bytes(url: str, token: str, opener=urllib.request.urlopen, timeout: float = 60) -> bytes:
    headers = {"User-Agent": "nagoyaction-localci"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise LocalCIError(f"download {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LocalCIError(f"download failed for {url}: {exc}") from exc


def git_env(base: dict | None = None) -> dict:
    env = dict(os.environ if base is None else base)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
    return env


def parse_ls_remote(listing: str, ref: str) -> str | None:
    want = ref
    for line in listing.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == want and SHA_RE.fullmatch(parts[0].lower()):
            return parts[0].lower()
    return None


def ls_remote(repo: str, ref: str, runner=subprocess.run) -> str:
    url = f"https://github.com/{repo}"
    try:
        out = runner(
            ["git", "ls-remote", url, ref],
            capture_output=True, text=True, check=False, timeout=60, env=git_env(),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise LocalCIError(f"git ls-remote failed for {repo} {ref}: {exc}") from exc
    if out.returncode != 0:
        detail = (out.stderr or out.stdout or "").strip()
        raise LocalCIError(f"git ls-remote failed for {repo} {ref}: {detail}")
    peeled = parse_ls_remote(out.stdout or "", ref + "^{}")
    direct = parse_ls_remote(out.stdout or "", ref)
    sha = peeled or direct
    if sha is None:
        raise LocalCIError(f"could not resolve {repo} {ref}")
    return sha


def verify_repository(repo: str, expected_id: int | None, data: dict) -> int:
    full = str(data.get("full_name", "")).lower()
    if full != repo.lower():
        raise LocalCIError(f"{repo}: repository id mismatch")
    got = data.get("id")
    if expected_id is not None and got != expected_id:
        raise LocalCIError(f"{repo}: repository id mismatch")
    if data.get("visibility") not in (None, "public") or data.get("private") is True:
        raise LocalCIError(f"{repo}: repository is not public")
    if type(got) is not int:
        raise LocalCIError(f"{repo}: repository id missing")
    return got


def resolve_ref(repo: str, ref_input: str, runner=subprocess.run) -> tuple[str, str]:
    """ref を SHA にする。40 桁の SHA はそのまま使う。戻り値は (sha, how)。"""
    text = ref_input.strip()
    if re.fullmatch(r"[0-9a-fA-F]{40}", text):
        return text.lower(), "workflow_dispatch input"
    if re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", text):
        return ls_remote(repo, text, runner), text
    if re.fullmatch(r"[A-Za-z0-9._/-]+", text):
        ref = "refs/heads/" + text
        return ls_remote(repo, ref, runner), ref
    raise LocalCIError("invalid aoi_ref")


def sources_for(root: Path) -> list[Source]:
    found = list(SOURCES)
    seen = {s.repo.lower() for s in found}
    lock = root / "vendor.lock.json"
    if not lock.is_file():
        return found
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LocalCIError(f"vendor.lock.json: {exc}") from exc
    repos: list[str] = []
    files = data.get("files", [])
    if isinstance(files, list):
        repos = [str(item.get("repository", "")) for item in files if isinstance(item, dict)]
    elif isinstance(files, dict):
        repos = [str(item.get("source_repo", "")) for item in files.values() if isinstance(item, dict)]
    for repo in repos:
        if repo and repo.lower() not in seen:
            key = re.sub(r"[^A-Za-z0-9]+", "_", repo).strip("_").upper()
            found.append(Source(key.lower(), key + "_SHA", repo, None))
            seen.add(repo.lower())
    return found


def resolve_source(source: Source, ref_input: str = "", *, token: str = "",
                   runner=subprocess.run, opener=urllib.request.urlopen) -> Resolved:
    data = github_json(f"https://api.github.com/repos/{source.repo}", token, opener)
    repository_id = verify_repository(source.repo, source.repository_id, data)
    if ref_input.strip():
        sha, how = resolve_ref(source.repo, ref_input, runner)
    else:
        how = "refs/heads/main"
        sha = ls_remote(source.repo, how, runner)
    return Resolved(source, sha, how, repository_id)


def resolve_sources(root: Path, aoi_ref: str = "", *, token: str = "",
                    runner=subprocess.run, opener=urllib.request.urlopen) -> list[Resolved]:
    resolved = []
    for source in sources_for(root):
        override = aoi_ref if source.key == "aoi" else ""
        resolved.append(resolve_source(source, override, token=token, runner=runner, opener=opener))
    return resolved


def provenance_mode(event_name: str, github_ref: str) -> str:
    if event_name == "schedule":
        return "strict"
    if event_name == "push" and github_ref == "refs/heads/main":
        return "strict"
    return "report-only"


def format_env(resolved: list[Resolved]) -> str:
    lines = ["# localci resolved refs. source: git ls-remote + repository id check"]
    for item in resolved:
        lines.append(f"{item.source.env}={item.sha}")
        lines.append(f"{item.source.env.removesuffix('_SHA')}_REPOSITORY_ID={item.repository_id}")
    return "\n".join(lines) + "\n"


def write_env_file(path: Path, resolved: list[Resolved]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_env(resolved), encoding="utf-8")


def format_github_output(resolved: list[Resolved]) -> str:
    lines = []
    for item in resolved:
        lines.append(f"{item.source.key}_sha={item.sha}")
        if item.source.key == "aoi":
            lines.append(f"sha={item.sha}")
    return "\n".join(lines) + ("\n" if lines else "")


def running_in_github_actions() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"


def format_actionlint_line(record: ActionlintRecord) -> str:
    sha = record.sha256 if record.sha256 else "unverified"
    via = f"go@{record.tag}" if record.via == "go" and record.tag else record.via
    return f"actionlint tag={record.tag} asset={record.asset} sha256={sha} via={via}"


def format_actionlint_env(record: ActionlintRecord) -> str:
    lines = [f"ACTIONLINT_TAG={record.tag}", f"ACTIONLINT_ASSET={record.asset}"]
    if record.sha256:
        lines.append(f"ACTIONLINT_SHA256={record.sha256}")
    return "\n".join(lines) + "\n"


def format_run_summary(resolved: list[Resolved], actionlint: ActionlintRecord | None) -> str:
    """解決した参照先 SHA と、その隣に actionlint の解決結果を書く。"""
    lines = ["## Resolved repositories"]
    if not resolved:
        lines.append("No repository SHA was resolved.")
    for item in resolved:
        lines.append(f"- `{item.source.repo}` `{item.sha}` ({item.how}), repository id `{item.repository_id}`")
    lines.append("")
    lines.append("## actionlint")
    if actionlint is None or not actionlint.tag:
        lines.append("actionlint was not resolved.")
    else:
        lines.append(f"- Tag: `{actionlint.tag}`")
        lines.append(f"- Asset: `{actionlint.asset}`")
        if actionlint.sha256:
            lines.append(f"- sha256: `{actionlint.sha256}`")
        else:
            lines.append("- sha256: not verified")
        via = f"go@{actionlint.tag}" if actionlint.via == "go" else actionlint.via
        lines.append(f"- via: `{via}`")
    return "\n".join(lines) + "\n"


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text)


def format_step_summary(resolved: list[Resolved], mode: str) -> str:
    aoi = next((item for item in resolved if item.source.key == "aoi"), None)
    lines = ["## Aoi source"]
    if aoi is None:
        lines.append("Aoi was not resolved.")
    else:
        lines.append(f"Resolved `{aoi.sha}` from `{aoi.how}`.")
        lines.append(f"Repository id `{aoi.repository_id}`.")
        lines.append(f"Source-hash provenance: {mode}.")
    lines.append("")
    lines.append("## Referenced repositories")
    for item in resolved:
        lines.append(f"- `{item.source.repo}` `{item.sha}` ({item.how}), repository id `{item.repository_id}`")
    return "\n".join(lines) + "\n"


def latest_release(repo: str, *, token: str = "", opener=urllib.request.urlopen,
                   runner=subprocess.run) -> tuple[str, str] | None:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nagoyaction-localci"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise LocalCIError(f"GitHub API {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LocalCIError(f"GitHub API failed for {url}: {exc}") from exc
    tag = str(data.get("tag_name", ""))
    if not tag:
        return None
    sha = ls_remote(repo, "refs/tags/" + tag, runner)
    return tag, sha


def workflow_files(root: Path) -> list[Path]:
    directory = root / ".github" / "workflows"
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))


def workflow_uses(root: Path) -> list[dict]:
    rows = []
    for path in workflow_files(root):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))
        for item in parse_uses(text):
            item = dict(item)
            item["file"] = rel
            rows.append(item)
    return rows


def actionlint_archive(version: str, system: str, machine: str) -> str:
    goos = _OS.get(system)
    goarch = _ARCH.get(machine)
    if not goos or not goarch:
        raise LocalCIError(f"unsupported platform {system}/{machine}")
    ext = "zip" if goos == "windows" else "tar.gz"
    return f"actionlint_{version}_{goos}_{goarch}.{ext}"


def checksum_for(text: str, filename: str) -> str:
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2 or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            continue
        name = parts[-1][1:] if parts[-1].startswith("*") else parts[-1]
        if name == filename:
            return parts[0].lower()
    raise LocalCIError(f"no checksum for {filename}")


def verify_bytes(data: bytes, expected: str, label: str) -> None:
    got = hashlib.sha256(data).hexdigest()
    if got != expected.lower():
        raise LocalCIError(f"checksum mismatch for {label}")


def _asset_digest(asset: dict) -> str | None:
    digest = str(asset.get("digest", ""))
    if digest.startswith("sha256:"):
        return digest.split(":", 1)[1].lower()
    return None


def extract_actionlint(archive: bytes, filename: str) -> bytes:
    name = "actionlint.exe" if filename.endswith(".zip") else "actionlint"
    if filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            member = next((info for info in zf.infolist() if Path(info.filename).name == name), None)
            if member is None or member.is_dir():
                raise LocalCIError("actionlint binary missing from archive")
            return zf.read(member)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        member = next((info for info in tar.getmembers() if Path(info.name).name == "actionlint" and info.isfile()), None)
        if member is None or member.issym() or member.islnk():
            raise LocalCIError("actionlint binary missing from archive")
        extracted = tar.extractfile(member)
        if extracted is None:
            raise LocalCIError("actionlint binary missing from archive")
        return extracted.read()


_ACTIONLINT_RECORD = "actionlint.record.json"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _read_actionlint_record(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    sha = str(data.get("sha256", "")).lower()
    if not _HEX64.fullmatch(sha):
        return None
    return {"tag": str(data.get("tag", "")), "asset": str(data.get("asset", "")), "sha256": sha}


def _install_actionlint(cache: Path, release: dict, tag: str, version: str, filename: str, *,
                        token: str, opener) -> ActionlintRecord:
    dest = cache / "actionlint" / version / ("actionlint.exe" if filename.endswith(".zip") else "actionlint")
    record_path = dest.parent / _ACTIONLINT_RECORD
    saved = _read_actionlint_record(record_path)
    if dest.is_file() and os.access(dest, os.X_OK) and saved and saved["tag"] == tag and saved["asset"] == filename:
        return ActionlintRecord(tag, filename, saved["sha256"], dest, "release")
    assets = {item.get("name"): item for item in release.get("assets", [])}
    archive_asset = assets.get(filename)
    checksum_name = f"actionlint_{version}_checksums.txt"
    checksum_asset = assets.get(checksum_name)
    if not archive_asset or not checksum_asset:
        raise LocalCIError(f"actionlint release is missing {filename}")
    archive = fetch_bytes(archive_asset["browser_download_url"], token, opener)
    checksum_bytes = fetch_bytes(checksum_asset["browser_download_url"], token, opener)
    archive_digest = _asset_digest(archive_asset)
    checksum_digest = _asset_digest(checksum_asset)
    if archive_digest:
        verify_bytes(archive, archive_digest, filename)
    if checksum_digest:
        verify_bytes(checksum_bytes, checksum_digest, checksum_name)
    expected = checksum_for(checksum_bytes.decode("utf-8", "replace"), filename).lower()
    verify_bytes(archive, expected, filename)
    payload = extract_actionlint(archive, filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(payload)
    dest.chmod(0o755)
    record_path.write_text(
        json.dumps({"tag": tag, "asset": filename, "sha256": expected}) + "\n",
        encoding="utf-8",
    )
    return ActionlintRecord(tag, filename, expected, dest, "release")


def ensure_actionlint(cache: Path, *, token: str = "", opener=urllib.request.urlopen,
                      system: str | None = None, machine: str | None = None) -> ActionlintRecord:
    """最新リリースを解決する。版はソースに固定しない。

    取得と checksum/digest の検証に成功した sha256 だけを記録する。
    GitHub Actions では失敗したらそこで止まる。手元では、タグを解決できたときだけ
    Go のそのタグへ戻す（`@latest` には戻さない）。
    """
    system = system or sys.platform
    if system == "linux":
        system = "Linux"
    elif system == "darwin":
        system = "Darwin"
    elif system in {"win32", "windows"}:
        system = "Windows"
    if machine is None:
        if system == "Windows":
            machine = os.environ.get("PROCESSOR_ARCHITECTURE", "amd64")
        else:
            machine = os.uname().machine
    release = github_json("https://api.github.com/repos/rhysd/actionlint/releases/latest", token, opener)
    tag = str(release.get("tag_name", ""))
    version = tag[1:] if tag.startswith("v") else tag
    if not version:
        raise LocalCIError("actionlint release has no tag")
    try:
        filename = actionlint_archive(version, system, machine)
        return _install_actionlint(cache, release, tag, version, filename, token=token, opener=opener)
    except (LocalCIError, OSError) as exc:
        if running_in_github_actions():
            raise LocalCIError(f"actionlint {tag}: {exc}") from exc
        asset = ""
        try:
            asset = actionlint_archive(version, system, machine)
        except LocalCIError:
            asset = ""
        return ActionlintRecord(tag, asset, "", None, "go")


def actionlint_argv(binary: Path | None, files: list[str], shellcheck: str | None,
                    go_ref: str | None = None) -> list[str]:
    if binary is not None:
        cmd = [str(binary)]
    elif go_ref and go_ref not in {"latest", "@latest"}:
        ref = go_ref[1:] if go_ref.startswith("@") else go_ref
        cmd = ["go", "run", f"github.com/rhysd/actionlint/cmd/actionlint@{ref}"]
    else:
        raise LocalCIError("actionlint tag was not resolved")
    if shellcheck:
        cmd.extend(["-shellcheck", shellcheck])
    else:
        cmd.append("-shellcheck=")
    cmd.extend(files)
    return cmd


def shellcheck_path(which=shutil.which) -> str | None:
    return which("shellcheck")


def parse_collect_only(stdout: str) -> list[str]:
    """`--collect-only -q` の各行を node id として読む。空白や括弧を含む id も切らない。"""
    nodeids = []
    for line in stdout.splitlines():
        text = line.strip()
        if "::" not in text or text.startswith(("=", "-", "ERROR", "collected", "warning", "!", "<")):
            continue
        if " collected in " in text or text.endswith(" collected"):
            continue
        nodeids.append(text)
    return nodeids


def collect_pytest(paths: list[str], root: Path, runner=subprocess.run) -> tuple[list[str], list[str]]:
    if importlib_pytest() is None:
        return [], ["pytest が見つからない"]
    try:
        out = runner(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "--continue-on-collection-errors", *paths],
            cwd=root, capture_output=True, text=True, check=False, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [], [f"pytest collection failed: {exc}"]
    nodeids = parse_collect_only(out.stdout or "")
    limits = []
    for line in ((out.stdout or "") + "\n" + (out.stderr or "")).splitlines():
        if "ERROR collecting" in line or line.startswith("ERROR "):
            limits.append(line.strip())
    if out.returncode != 0 and not nodeids and not limits:
        limits.append("pytest collection failed")
    return nodeids, limits


def importlib_pytest():
    import importlib.util
    return importlib.util.find_spec("pytest")


def _read_input_log(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        found.append({"name": parts[0], "fixed": parts[1], "value": parts[2]})
    return found


AOI_PYTEST_PREFIX = ["uv", "run", "--locked", "--python", "3.11", "pytest", "-c", "pyproject.toml"]
_FAILED_NODE = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.M)


def _git(runner, argv: list[str], *, cwd: Path, timeout: int, text: bool = True):
    try:
        out = runner(argv, cwd=cwd, capture_output=True, text=text, check=False, timeout=timeout, env=git_env())
    except (OSError, subprocess.SubprocessError) as exc:
        raise LocalCIError(f"{' '.join(argv)} failed: {exc}") from exc
    if out.returncode != 0:
        err = out.stderr or out.stdout or ""
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        raise LocalCIError(f"{' '.join(argv)} failed: {str(err).strip()}")
    return out


def checkout_aoi(root: Path, resolved: Resolved, *, runner=subprocess.run, remote: str | None = None) -> Path:
    """解決済み SHA を `.localci/aoi` に checkout し、HEAD が一致しなければ失敗する。"""
    if not SHA_RE.fullmatch(resolved.sha):
        raise LocalCIError(f"resolved Aoi SHA is not 40 hex digits: {resolved.sha}")
    dest = root / ".localci" / "aoi"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        if dest.exists():
            shutil.rmtree(dest)
        url = remote or f"https://github.com/{resolved.source.repo}"
        _git(runner, ["git", "clone", "--no-checkout", url, str(dest)], cwd=root, timeout=600)
    fetch = resolved.how if resolved.how.startswith("refs/") else resolved.sha
    _git(runner, ["git", "fetch", "--no-tags", "origin", fetch], cwd=dest, timeout=600)
    _git(runner, ["git", "checkout", "-f", "--detach", resolved.sha], cwd=dest, timeout=180)
    head = _git(runner, ["git", "rev-parse", "HEAD"], cwd=dest, timeout=60).stdout.strip().lower()
    if head != resolved.sha:
        raise LocalCIError(f"Aoi checkout {head} does not match resolved {resolved.sha}")
    return dest


def overlay_nagoyaction(aoi: Path, root: Path, *, runner=subprocess.run) -> None:
    """このリポジトリの commit 済み tree を Aoi の nagoyaction/ に重ね、tree が一致することを確かめる。"""
    dest = aoi / "nagoyaction"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    out = _git(runner, ["git", "archive", "HEAD"], cwd=root, timeout=120, text=False)
    blob = out.stdout if isinstance(out.stdout, bytes) else (out.stdout or "").encode()
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as tar:
            try:
                tar.extractall(dest, filter="data")
            except TypeError:
                tar.extractall(dest)
    except (tarfile.TarError, OSError) as exc:
        raise LocalCIError(f"git archive extract failed: {exc}") from exc
    _git(runner, ["git", "add", "-A", "nagoyaction"], cwd=aoi, timeout=120)
    tree = _git(runner, ["git", "write-tree", "--prefix=nagoyaction/"], cwd=aoi, timeout=60).stdout.strip()
    expected = _git(runner, ["git", "rev-parse", "HEAD^{tree}"], cwd=root, timeout=60).stdout.strip()
    if tree != expected:
        raise LocalCIError(f"nagoyaction overlay {tree} does not match HEAD^{{tree}} {expected}")


def pytest_env(cwd: Path) -> dict:
    env = git_env()
    plugin_root = cwd if (cwd / "localci.py").is_file() else cwd / "nagoyaction"
    env["PYTHONPATH"] = str(plugin_root) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def failed_pytest_nodes(text: str) -> list[str]:
    return _FAILED_NODE.findall(text)


def _batch_outcomes(checks: list[Check], returncode: int, detail: str, inputs: list[dict],
                    keep_going: bool) -> dict[str, Outcome]:
    nodeids = [check.target for check in checks]
    by_node: dict[str, Outcome] = {}
    def failed_detail(node: str, body: str) -> str:
        text = f"failed {node}"
        if body:
            return text + "\n" + body
        return text

    if returncode == 0:
        for index, check in enumerate(checks):
            by_node[check.id] = Outcome("pass", "", inputs if index == 0 else [])
        return by_node
    failed = [node for node in failed_pytest_nodes(detail) if node in nodeids]
    if not failed:
        for index, check in enumerate(checks):
            by_node[check.id] = Outcome(
                "fail", failed_detail(check.target, detail) if index == 0 else "failed", inputs if index == 0 else [],
            )
        return by_node
    if keep_going:
        attached = False
        failed_set = set(failed)
        for check in checks:
            if check.target in failed_set:
                by_node[check.id] = Outcome(
                    "fail", failed_detail(check.target, detail) if not attached else check.target, inputs if not attached else [],
                )
                attached = True
            else:
                by_node[check.id] = Outcome("pass", "", [])
        return by_node
    first = failed[0]
    seen = False
    for check in checks:
        if check.target == first:
            by_node[check.id] = Outcome("fail", failed_detail(first, detail), inputs)
            seen = True
        elif seen:
            by_node[check.id] = Outcome("fail", "not run", [])
        else:
            by_node[check.id] = Outcome("pass", "", [])
    return by_node


def run_pytest_batch(checks: list[Check], round_seed: int, *, cwd: Path, prefix: list[str],
                     keep_going: bool, runner=subprocess.run) -> dict[str, Outcome]:
    """同じシャードの pytest を 1 プロセスで実行し、ノードごとに round seed から差し替える。"""
    handle = tempfile.NamedTemporaryFile(prefix="localci-inputs-", suffix=".log", delete=False)
    log = Path(handle.name)
    handle.close()
    cmd = [*prefix, "-q", "--tb=line", "-p", "localci_pytest", "--localci-round-seed", str(round_seed)]
    if not keep_going:
        cmd.append("-x")
    cmd.extend(check.target for check in checks)
    try:
        out = runner(cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=900, env=pytest_env(cwd))
    except (OSError, subprocess.SubprocessError) as exc:
        inputs = _read_input_log(log)
        log.unlink(missing_ok=True)
        return {check.id: Outcome("fail", str(exc) if index == 0 else "not run", inputs if index == 0 else [])
                for index, check in enumerate(checks)}
    inputs = _read_input_log(log)
    log.unlink(missing_ok=True)
    detail = "\n".join(part for part in ((out.stdout or ""), (out.stderr or "")) if part).strip()
    return _batch_outcomes(checks, out.returncode, detail, inputs, keep_going)


def collect_aoi_tests(aoi: Path, runner=subprocess.run) -> list[str]:
    if shutil.which("uv") is None:
        raise LocalCIError(
            "uv が PATH に無いので Aoi の tests/ を実行できない。"
            "--self-tests で tests/test_localci.py だけ実行できる"
        )
    cmd = [*AOI_PYTEST_PREFIX, "--collect-only", "-q", "nagoyaction/tests"]
    try:
        out = runner(cmd, cwd=aoi, capture_output=True, text=True, check=False, timeout=300, env=pytest_env(aoi))
    except (OSError, subprocess.SubprocessError) as exc:
        raise LocalCIError(f"Aoi のテスト収集に失敗した: {exc}") from exc
    detail = "\n".join(part for part in ((out.stdout or ""), (out.stderr or "")) if part).strip()
    if out.returncode != 0:
        raise LocalCIError(f"Aoi のテスト収集に失敗した: {detail}")
    nodeids = parse_collect_only(out.stdout or "")
    if not nodeids:
        raise LocalCIError(f"Aoi のテスト収集が空だった: {detail}")
    return nodeids


def workflow_checks(root: Path) -> tuple[list[Check], list[str]]:
    limits: list[str] = []
    checks: list[Check] = []
    for source in sources_for(root):
        checks.append(Check(f"resolve:{source.repo}", "resolve", source.repo, repo=source.repo))
    files = workflow_files(root)
    if not files:
        limits.append("workflow ファイルがない")
    for path in files:
        rel = str(path.relative_to(root))
        checks.append(Check(f"actionlint:{rel}", "actionlint", rel, file=rel))
    for item in workflow_uses(root):
        ident = f"pin:{item['file']}:{item['line']}:{item['raw']}"
        checks.append(Check(ident, "pin", item["raw"], file=item["file"], ref=item["ref"], repo=item["repo"]))
    return checks, limits


def full_suite(pytest_paths: list[str] | None, skip_pytest: bool, self_tests: bool) -> bool:
    return not skip_pytest and not self_tests and not pytest_paths


def prepare_pytest(root: Path, *, pytest_paths: list[str] | None, skip_pytest: bool, self_tests: bool,
                   aoi_ref: str, token: str, runner, opener, emit) -> tuple[list[Check], list[str], Path, list[str], Resolved | None]:
    """検査一覧、pytest の cwd、コマンド前置、checkout 済みの Aoi 解決結果を返す。"""
    if not full_suite(pytest_paths, skip_pytest, self_tests):
        paths = pytest_paths
        if self_tests and not paths:
            paths = ["tests/test_localci.py"]
        checks, limits = build_checks(root, pytest_paths=paths, skip_pytest=skip_pytest, runner=runner)
        return checks, limits, root, [sys.executable, "-m", "pytest"], None
    source = next(item for item in SOURCES if item.key == "aoi")
    ref = aoi_ref or os.environ.get("AOI_REF_INPUT", "")
    resolved = resolve_source(source, ref, token=token, runner=runner, opener=opener)
    emit(f"Aoi {resolved.sha} from {resolved.how} (repository id {resolved.repository_id})")
    aoi = checkout_aoi(root, resolved, runner=runner)
    overlay_nagoyaction(aoi, root, runner=runner)
    emit(f"Aoi checkout {aoi} HEAD {resolved.sha}")
    nodeids = collect_aoi_tests(aoi, runner)
    checks, limits = workflow_checks(root)
    checks.extend(Check(f"pytest:{nodeid}", "pytest", nodeid) for nodeid in nodeids)
    return checks, limits, aoi, list(AOI_PYTEST_PREFIX), resolved


def build_checks(root: Path, *, pytest_paths: list[str] | None, skip_pytest: bool,
                 runner=subprocess.run) -> tuple[list[Check], list[str]]:
    checks, limits = workflow_checks(root)
    if not skip_pytest:
        paths = pytest_paths or ["tests"]
        existing = []
        for path in paths:
            candidate = Path(path)
            if not candidate.is_absolute():
                candidate = root / path
            if candidate.exists():
                existing.append(str(path))
            else:
                limits.append(f"pytest path がない: {path}")
        if existing:
            nodeids, extra = collect_pytest(existing, root, runner)
            limits.extend(extra)
            for nodeid in nodeids:
                checks.append(Check(f"pytest:{nodeid}", "pytest", nodeid))
    return checks, limits


class Session:
    def __init__(self, root: Path, *, token: str = "", strict: bool = False,
                 runner=subprocess.run, opener=urllib.request.urlopen,
                 actionlint: Path | None | str = "auto",
                 aoi_resolved: Resolved | None = None, aoi_ref: str = ""):
        self.root = root
        self.token = token
        self.strict = strict
        self.runner = runner
        self.opener = opener
        self.actionlint = actionlint
        self.aoi_resolved = aoi_resolved
        self.aoi_ref = aoi_ref
        self.resolved: dict[str, Resolved] = {}
        self.releases: dict[str, tuple[str, str] | None] = {}
        self.shellcheck = shellcheck_path()
        self.actionlint_record: ActionlintRecord | None = None

    def prepare_actionlint(self) -> ActionlintRecord | None:
        if self.actionlint_record is not None:
            return self.actionlint_record
        if self.actionlint is None:
            return None
        if isinstance(self.actionlint, Path):
            self.actionlint_record = ActionlintRecord("", "", "", self.actionlint, "path")
            return self.actionlint_record
        record = ensure_actionlint(self.root / ".localci", token=self.token, opener=self.opener)
        if record.via == "go":
            if not record.tag:
                raise LocalCIError("actionlint tag was not resolved")
            if shutil.which("go") is None:
                raise LocalCIError(f"actionlint {record.tag} の取得に失敗し、go も PATH に無い")
        self.actionlint_record = record
        return record

    def execute(self, check: Check) -> Outcome:
        if check.kind == "resolve":
            return self._resolve(check)
        if check.kind == "pin":
            return self._pin(check)
        if check.kind == "actionlint":
            return self._actionlint(check)
        raise LocalCIError(f"unknown check {check.kind}")

    def _resolve(self, check: Check) -> Outcome:
        source = next(s for s in sources_for(self.root) if s.repo == check.repo)
        if source.key == "aoi" and self.aoi_resolved is not None:
            item = self.aoi_resolved
        else:
            ref = ""
            if source.key == "aoi":
                ref = self.aoi_ref or os.environ.get("AOI_REF_INPUT", "")
            item = resolve_source(source, ref, token=self.token, runner=self.runner, opener=self.opener)
        self.resolved[source.repo] = item
        return Outcome("pass", f"{item.sha} from {item.how} (repository id {item.repository_id})", [])

    def _release(self, repo: str) -> tuple[str, str] | None:
        if repo not in self.releases:
            self.releases[repo] = latest_release(repo, token=self.token, opener=self.opener, runner=self.runner)
        return self.releases[repo]

    def _pin(self, check: Check) -> Outcome:
        latest = self._release(check.repo)
        status = classify_pin(check.ref, latest)
        probe = substitute("sha_probe", "0" * 40, lambda rng: f"{rng.getrandbits(160):040x}")
        latest_sha = latest[1] if latest else ""
        if latest_sha and probe == latest_sha:
            probe = substitute("sha_probe_retry", "f" * 40, lambda rng: f"{rng.getrandbits(160):040x}")
        if latest_sha and classify_pin(probe, latest) == "match":
            raise LocalCIError("random sha probe matched the latest release")
        if latest is None:
            detail = f"{check.repo}@{check.ref or '(none)'} has no release tag; not compared"
        elif status == "match":
            detail = f"{check.repo}@{check.ref} matches {latest[0]}"
        elif status == "outdated":
            detail = f"{check.repo}@{check.ref} is outdated; latest {latest[0]} is {latest[1]}"
        else:
            detail = f"{check.repo}@{check.ref or '(none)'} is not a SHA pin; latest {latest[0]} is {latest[1]}"
        failed = pin_fails(status, self.strict)
        return Outcome("fail" if failed else "pass", detail, [])

    def _actionlint(self, check: Check) -> Outcome:
        record = self.prepare_actionlint()
        binary = None if record is None else record.binary
        go_ref = record.tag if record is not None and record.via == "go" else None
        argv = actionlint_argv(binary, [str(self.root / check.target)], self.shellcheck, go_ref=go_ref)
        try:
            out = self.runner(argv, cwd=self.root, capture_output=True, text=True, check=False, timeout=180)
        except (OSError, subprocess.SubprocessError) as exc:
            return Outcome("fail", str(exc), [])
        detail = "\n".join(part for part in ((out.stdout or ""), (out.stderr or "")) if part).strip()
        tool = "shellcheck on" if self.shellcheck else "shellcheck off"
        if out.returncode == 0:
            return Outcome("pass", f"actionlint ok ({tool})", [])
        return Outcome("fail", detail or f"actionlint exit {out.returncode} ({tool})", [])


def iter_work(shard: list[Check], coalesce_pytest: bool):
    """非 pytest は 1 件ずつ。pytest はシャード内を 1 プロセスにまとめる。"""
    if not coalesce_pytest:
        for check in shard:
            yield [check]
        return
    pytest_checks = [check for check in shard if check.kind == "pytest"]
    emitted = False
    for check in shard:
        if check.kind == "pytest":
            if not emitted:
                yield pytest_checks
                emitted = True
            continue
        yield [check]


def run_plan(*, shards: list[list[Check]], master_seed: int, execute, keep_going: bool, emit,
             execute_pytest=None) -> PlanReport:
    reports: list[RoundReport] = []
    stopped = False
    total = len(shards)
    for number, shard in enumerate(shards, 1):
        rseed = mix_seed(master_seed, "round", number)
        ids = [c.id for c in shard]
        emit(f"=== round {number}/{total} seed={rseed} master={master_seed} checks={len(shard)} ===")
        for ident in ids:
            emit(f"  - {ident}")
        if not ids:
            emit("  (empty shard)")
        failed_check = None
        lines: list[str] = []

        def note(check: Check, outcome: Outcome) -> str | None:
            for item in outcome.inputs:
                text = f"    inputs: {item['name']} {item['fixed']} -> {item['value']}"
                lines.append(text)
                emit(text)
            mark = "pass" if outcome.ok else outcome.status
            line = f"    [{mark}] {outcome.detail.splitlines()[0] if outcome.detail else check.kind}"
            lines.append(line)
            emit(line)
            if outcome.ok:
                return None
            if outcome.detail and "\n" in outcome.detail:
                emit(outcome.detail)
            return check.id

        for group in iter_work(shard, execute_pytest is not None):
            if failed_check is not None and not keep_going:
                break
            if execute_pytest is not None and group and group[0].kind == "pytest":
                for check in group:
                    emit(f"  > {check.id}")
                try:
                    outcomes = execute_pytest(group, rseed, keep_going)
                except (LocalCIError, OSError, urllib.error.URLError, subprocess.SubprocessError) as exc:
                    outcomes = {check.id: Outcome("fail", str(exc) if index == 0 else "not run", [])
                                for index, check in enumerate(group)}
                for check in group:
                    outcome = outcomes.get(check.id) or Outcome("fail", "not run", [])
                    found = note(check, outcome)
                    if found is not None and failed_check is None:
                        failed_check = found
                    if failed_check is not None and not keep_going:
                        break
                continue
            check = group[0]
            emit(f"  > {check.id}")
            cseed = mix_seed(rseed, check.id)
            try:
                with use_seed(cseed):
                    outcome = execute(check, cseed)
                    inputs = take_substitutions()
                    inputs.extend(outcome.inputs)
                    outcome = Outcome(outcome.status, outcome.detail, inputs)
            except (LocalCIError, OSError, urllib.error.URLError, subprocess.SubprocessError) as exc:
                outcome = Outcome("fail", str(exc), take_substitutions())
            found = note(check, outcome)
            if found is not None and failed_check is None:
                failed_check = found
        passed = failed_check is None
        reports.append(RoundReport(number, rseed, ids, passed, failed_check, lines))
        if passed:
            emit(f"[pass] round {number}/{total}")
        else:
            emit(f"[fail] round {number}/{total} seed={rseed}")
            emit("shard:")
            for ident in ids:
                emit(f"  - {ident}")
        completed = len(reports)
        passed_n = sum(1 for r in reports if r.passed)
        emit(confidence_line(passed_n, total, completed, stopped=not passed and not keep_going))
        if not passed and not keep_going:
            stopped = True
            break
    return PlanReport(master_seed, reports, stopped)


def _emit_print(text: str) -> None:
    print(text, flush=True)


def run_local(root: Path, *, repeat: int, seed: int | None, keep_going: bool, strict: bool,
              pytest_paths: list[str] | None, skip_pytest: bool, env_file: Path | None,
              self_tests: bool = False, aoi_ref: str = "",
              token: str | None = None, runner=subprocess.run, opener=urllib.request.urlopen,
              emit=_emit_print) -> int:
    master = seed if seed is not None else random.SystemRandom().randrange(1, 2**31)
    token = github_token() if token is None else token
    emit(f"localci seed={master}")
    checks, limits, pytest_cwd, pytest_prefix, aoi_resolved = prepare_pytest(
        root, pytest_paths=pytest_paths, skip_pytest=skip_pytest, self_tests=self_tests,
        aoi_ref=aoi_ref, token=token, runner=runner, opener=opener, emit=emit,
    )
    shards = split_shards(checks, repeat, master)
    shellcheck = shellcheck_path()
    emit(f"localci seed={master} checks={len(checks)} rounds={repeat}")
    emit("shellcheck: " + (f"actionlint が {shellcheck} を使う" if shellcheck else "PATH に無いので使わない"))
    if limits:
        emit("limits:")
        for item in limits:
            emit(f"  - {item}")
    session = Session(
        root, token=token, strict=strict, runner=runner, opener=opener,
        aoi_resolved=aoi_resolved, aoi_ref=aoi_ref,
    )
    actionlint_record = None
    if any(check.kind == "actionlint" for check in checks):
        actionlint_record = session.prepare_actionlint()
        if actionlint_record is not None and actionlint_record.tag:
            emit(format_actionlint_line(actionlint_record))

    def execute(check: Check, cseed: int) -> Outcome:
        del cseed
        return session.execute(check)

    def execute_pytest(group: list[Check], rseed: int, going: bool) -> dict[str, Outcome]:
        return run_pytest_batch(group, rseed, cwd=pytest_cwd, prefix=pytest_prefix, keep_going=going, runner=runner)

    report = run_plan(
        shards=shards, master_seed=master, execute=execute, keep_going=keep_going, emit=emit,
        execute_pytest=None if skip_pytest else execute_pytest,
    )
    recorded = list(session.resolved.values())
    path = env_file or (root / ".localci" / "refs.env")
    if recorded:
        write_env_file(path, recorded)
        emit(f"refs: {path}")
        emit(format_env(recorded).rstrip())
    if actionlint_record is not None and actionlint_record.tag:
        append_text(path, format_actionlint_env(actionlint_record))
        emit(format_actionlint_line(actionlint_record))
    summary = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary and (recorded or (actionlint_record is not None and actionlint_record.tag)):
        append_text(Path(summary), format_run_summary(recorded, actionlint_record))
    passed = report.passed_rounds
    emit("=== summary ===")
    emit(f"seed: {master}")
    emit(confidence_line(passed, repeat, len(report.rounds), report.stopped))
    if report.stopped or any(not r.passed for r in report.rounds):
        return 1
    return 0


def run_resolve(root: Path, *, aoi_ref: str, env_file: Path | None, github_output: bool,
                token: str | None = None, runner=subprocess.run, opener=urllib.request.urlopen,
                emit=_emit_print) -> int:
    token = github_token() if token is None else token
    if not aoi_ref:
        aoi_ref = os.environ.get("AOI_REF_INPUT", "")
    resolved = resolve_sources(root, aoi_ref, token=token, runner=runner, opener=opener)
    path = env_file or (root / ".localci" / "refs.env")
    write_env_file(path, resolved)
    text = format_env(resolved).rstrip()
    emit(text)
    if github_output:
        output = os.environ.get("GITHUB_OUTPUT", "")
        if not output:
            raise LocalCIError("GITHUB_OUTPUT is not set")
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(format_github_output(resolved))
        summary = os.environ.get("GITHUB_STEP_SUMMARY", "")
        if summary:
            mode = provenance_mode(os.environ.get("EVENT_NAME", ""), os.environ.get("GITHUB_REF", ""))
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(format_step_summary(resolved, mode))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ワークフローとテストを手元で検査する（GitHub Actions と同じ解決）")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="actionlint、ピン検査、SHA 解決、pytest をシャードして実行する")
    run.add_argument("--repeat", type=_positive, default=1, help="シャード数。各検査は全ラウンドで一度だけ走る")
    run.add_argument("--seed", type=int, default=None, help="シャッフルと入力の差し替えを再現する")
    run.add_argument("--keep-going", action="store_true", help="失敗したあとも残りのラウンドを実行する")
    run.add_argument("--strict", action="store_true", help="古い uses: ピンや SHA でないピンを失敗にする")
    run.add_argument("--root", type=Path, default=None)
    run.add_argument("--pytest", dest="pytest_paths", action="append", default=None,
                     help="このリポジトリ内の pytest パス。指定すると Aoi は checkout しない")
    run.add_argument("--self-tests", action="store_true",
                     help="Aoi を checkout せず tests/test_localci.py だけ実行する")
    run.add_argument("--skip-pytest", action="store_true")
    run.add_argument("--aoi-ref", default="", help="Aoi の ref。空なら AOI_REF_INPUT、それも空なら main")
    run.add_argument("--env-file", type=Path, default=None)
    resolve = sub.add_parser("resolve", help="参照先リポジトリの main SHA を解決する")
    resolve.add_argument("--root", type=Path, default=None)
    resolve.add_argument("--env-file", type=Path, default=None)
    resolve.add_argument("--github-output", action="store_true")
    resolve.add_argument("--aoi-ref", default="", help="Aoi の ref。空なら AOI_REF_INPUT、それも空なら main")
    return parser


def _positive(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--repeat は 1 以上の整数") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("--repeat は 1 以上の整数")
    return value


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] not in {"run", "resolve", "-h", "--help"}:
        argv = ["run", *argv]
    args = _parser().parse_args(argv)
    root = (args.root or Path(__file__).resolve().parent).resolve()
    try:
        if args.cmd == "resolve":
            return run_resolve(root, aoi_ref=args.aoi_ref, env_file=args.env_file, github_output=args.github_output)
        return run_local(
            root, repeat=args.repeat, seed=args.seed, keep_going=args.keep_going, strict=args.strict,
            pytest_paths=args.pytest_paths, skip_pytest=args.skip_pytest, env_file=args.env_file,
            self_tests=args.self_tests, aoi_ref=args.aoi_ref,
        )
    except LocalCIError as exc:
        print(f"localci: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
