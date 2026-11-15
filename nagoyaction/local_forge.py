#!/usr/bin/env python3
"""Local Gitea/Forgejo control, extracted from OneLinearNumerousMemo."""
from __future__ import annotations
import argparse, base64, contextlib, hashlib, json, os, secrets, shutil, signal, subprocess, sys, time
import urllib.error, urllib.request
from pathlib import Path
PY = Path(__file__).resolve()
OLNM_HOME = Path(os.environ.get("OLNM_HOME", Path.home() / ".olnm"))
DIAL_FILE = Path(os.environ.get("DIAL_FILE", OLNM_HOME / "dial"))
DIALS = {0: "🔌 offline", 1: "🏠 local", 2: "🔁 mirror", 3: "☁️ github"}
DIAL_NAMES = {"offline": 0, "local": 1, "mirror": 2, "github": 3}  # the file keeps the digit; names are for people


def dial_level(value: int | str) -> int:
    """offline|local|mirror|github (or 0-3) → 0-3. Raises ValueError for anything else."""
    if isinstance(value, int) and not isinstance(value, bool) and value in DIALS:
        return value
    text = str(value).strip().lower()
    if text in DIAL_NAMES:
        return DIAL_NAMES[text]
    if text.isdigit() and int(text) in DIALS:
        return int(text)
    raise ValueError(f"dial must be one of {', '.join(DIAL_NAMES)} (or 0-3), not {value!r}")


def dial_label(level: int) -> str:
    """'🔁 mirror (2)': the name first, the stored digit after it."""
    return f"{DIALS[level]} ({level})"

def read_dial(default: int = 3) -> int:
    """Current dial (0..3); unset = 3 (plain online box)."""
    try:
        return int(DIAL_FILE.read_text().strip())
    except (OSError, ValueError):
        return default


def _write_dial(level: int) -> None:
    DIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    DIAL_FILE.write_text(f"{level}\n")


def dial(level: int | str | None = None) -> int:
    """Show or set the dial (offline|local|mirror|github or 0-3). When the local forge exists, also start/stop it and re-point every repo's origin."""
    if level is None:
        lv = read_dial()
        print(f"🎛️  {dial_label(lv)}  ({DIAL_FILE})")
        return lv
    try:
        level = dial_level(level)
    except ValueError as error:
        raise SystemExit(f"❌ {error}") from None
    try:
        if FSTATE.exists():
            _hub_apply(level)
        _write_dial(level)
    except (Exception, SystemExit):
        print("❌ dial change did not complete; inspect forge and repository remotes before retrying. "
              "Earlier side effects are not automatically rolled back.", file=sys.stderr)
        raise
    print(f"🎛️  → {dial_label(level)}" + ("  🌍 one-liners stubbed" if level <= 1 else ""))
    return level


# ───────────────────────── 🏠 hub: local GitHub-like forge (Gitea / Forgejo) ─────────────────────────
FORGE = OLNM_HOME / "forge"
BIN, DATA, BARE, LOG = FORGE / "bin" / "forge", FORGE / "data", FORGE / "bare", FORGE / "log"
INI, PID, FSTATE = FORGE / "app.ini", FORGE / "forge.pid", FORGE / "state.json"
# 🧬 flavors: Gitea (default: since 2016, MIT, released on GitHub) or Forgejo (its 2022 fork, GPLv3+, released on Codeberg). Same CLI + API.
FLAVORS = {
    "forgejo": {"urls": ("https://codeberg.org/forgejo/forgejo/releases/download/v{v}/forgejo-{v}-linux-{arch}", "https://code.forgejo.org/forgejo/forgejo/releases/download/v{v}/forgejo-{v}-linux-{arch}"),
                "latest": ("https://codeberg.org/api/v1/repos/forgejo/forgejo/releases/latest", "https://code.forgejo.org/api/v1/repos/forgejo/forgejo/releases/latest")},
    "gitea": {"urls": ("https://github.com/go-gitea/gitea/releases/download/v{v}/gitea-{v}-linux-{arch}", "https://dl.gitea.com/gitea/{v}/gitea-{v}-linux-{arch}"),
              "latest": ("https://api.github.com/repos/go-gitea/gitea/releases/latest", "https://github.com/go-gitea/gitea/releases/latest")},
}
VERIFIED = {"gitea": "1.27.3"}  # ✅ end-to-end checked with olnm; used when the "latest" lookup is blocked but downloads are not
GH_LABELS = {"bug": "d73a4a", "enhancement": "a2eeef", "documentation": "0075ca", "question": "d876e3", "help wanted": "008672", "good first issue": "7057ff", "wontfix": "ffffff", "duplicate": "cfd3d7"}
APP_INI = """\
APP_NAME = olnm hub
RUN_MODE = prod
WORK_PATH = {home}
[server]
PROTOCOL = http
HTTP_ADDR = 127.0.0.1
HTTP_PORT = {port}
ROOT_URL = http://localhost:{port}/
PUBLIC_URL_DETECTION = legacy
DISABLE_SSH = true
OFFLINE_MODE = true
[database]
DB_TYPE = sqlite3
PATH = {data}/forge.db
[repository]
ROOT = {data}/repos
DEFAULT_BRANCH = main
[security]
INSTALL_LOCK = true
SECRET_KEY = {secret}
[service]
DISABLE_REGISTRATION = true
REQUIRE_SIGNIN_VIEW = false
[mailer]
ENABLED = false
[log]
MODE = file
ROOT_PATH = {log}
[actions]
ENABLED = true
[mirror]
ENABLED = true
DEFAULT_INTERVAL = 1h
"""
_NOPROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _sh(*cmd: str, cwd: Path | None = None, check: bool = True) -> str:
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and r.returncode:
        raise SystemExit(f"❌ {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def _open(req: urllib.request.Request | str, timeout: int):
    url = req.full_url if isinstance(req, urllib.request.Request) else req
    opener = _NOPROXY if url.startswith(("http://127.0.0.1", "http://localhost")) else urllib.request.build_opener()
    return opener.open(req, timeout=timeout)


def _fetch(url: str, dest: Path | None = None, timeout: int = 120) -> bytes:
    with _open(urllib.request.Request(url, headers={"User-Agent": "olnm"}), timeout) as r:
        data = r.read()
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return data


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fstate() -> dict:
    return json.loads(FSTATE.read_text()) if FSTATE.exists() else {"port": 3000, "user": "admin", "repos": {}}


def _fsave(st: dict) -> None:
    FORGE.mkdir(parents=True, exist_ok=True)
    FSTATE.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n")
    FSTATE.chmod(0o600)


def _forge(*args: str, check: bool = True) -> str:
    if not BIN.exists():
        raise SystemExit("❌ forge binary missing → hubdial install")
    return _sh(str(BIN), "--config", str(INI), *args, check=check)


def _running() -> int:
    if PID.exists():
        try:
            pid = int(PID.read_text() or 0)
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            PID.unlink(missing_ok=True)
    return 0


def hub_port() -> int:
    """Port of the local forge."""
    return _fstate()["port"]


def _latest_version(flavor: str = "gitea") -> str:
    for url in FLAVORS[flavor]["latest"]:
        try:
            if url.startswith("https://github.com/"):  # release page redirects to /tag/vX.Y.Z
                with _open(urllib.request.Request(url, headers={"User-Agent": "olnm"}), 20) as r:
                    return r.geturl().rsplit("/v", 1)[1]
            return json.loads(_fetch(url, timeout=20))["tag_name"].lstrip("v")
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError, TimeoutError):
            continue
    if v := VERIFIED.get(flavor):
        print(f"↪️  latest {flavor} unknown (lookup blocked) → verified {v}")
        return v
    other = "gitea" if flavor == "forgejo" else "forgejo"
    raise SystemExit(f"❌ cannot reach {flavor} releases → try --flavor {other}, or install --from FILE")


def hub_bundle(dest: str = "carry", version: str = "latest", arch: str = "amd64", flavor: str = "gitea") -> Path:
    """🌍 Download the forge binary + .sha256 into DEST and copy local_forge.py beside it — carry DEST into a closed network."""
    if flavor not in FLAVORS:
        raise SystemExit(f"❌ flavor must be one of {', '.join(FLAVORS)}")
    v = _latest_version(flavor) if version == "latest" else version
    out = Path(dest)
    name = f"{flavor}-{v}-linux-{arch}"
    for tmpl in FLAVORS[flavor]["urls"]:
        url = tmpl.format(v=v, arch=arch)
        try:
            print(f"⬇️  {url}")
            binary = _fetch(url, out / name, timeout=900)
            want = _fetch(url + ".sha256", out / f"{name}.sha256", timeout=60).split()[0].decode()
            break
        except urllib.error.URLError as e:
            print(f"⚠️  {url.split('/')[2]}: {e}")
    else:
        raise SystemExit(f"❌ download failed on all hosts → try --flavor {'gitea' if flavor == 'forgejo' else 'forgejo'}")
    if hashlib.sha256(binary).hexdigest() != want:
        raise SystemExit("❌ sha256 mismatch")
    shutil.copy2(PY, out / "local_forge.py")
    print(f"✅ sha256 ok → 🎒 {out}/  (offline: python3 local_forge.py install --from {out}/{name})")
    return out / name


def hub_install(version: str = "latest", src: str | None = None, sha: str | None = None, flavor: str = "gitea") -> Path:
    """Place the forge binary at ~/.olnm/forge/bin/forge. Online: download+verify. Offline: --from carried file (checked against sha or sidecar .sha256)."""
    if src:
        path = Path(src)
        if not path.is_file():
            raise SystemExit(f"❌ no such file: {src}")
        side = path.with_name(path.name + ".sha256")
        want = sha or (side.read_text().split()[0] if side.exists() else None)
        if want and _sha256(path) != want:
            raise SystemExit("❌ sha256 mismatch for carried binary")
    else:
        path = hub_bundle(str(FORGE / "bundle"), version, flavor=flavor)
    BIN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, BIN)
    BIN.chmod(0o755)
    print(f"📦 {BIN} ← {path.name}")
    try:
        print(f"🔖 {_forge('--version', check=False) or 'installed'}")
    except OSError as e:
        print(f"⚠️  binary not runnable here: {e}")
    return BIN


def hub_init(port: int = 3000, user: str = "admin", password: str | None = None, email: str = "admin@localhost") -> dict:
    """Write app.ini (sqlite, 127.0.0.1 only, no SSH/mail/sign-up), migrate, create admin + API token, set git auth."""
    for d in (DATA, BARE, LOG):
        d.mkdir(parents=True, exist_ok=True)
    st = _fstate()
    if not INI.exists():
        INI.write_text(APP_INI.format(home=FORGE, port=port, data=DATA, log=LOG, secret=secrets.token_urlsafe(48)))
        INI.chmod(0o600)
    _forge("migrate")
    pw = password or secrets.token_urlsafe(16)
    out = _forge("admin", "user", "create", "--admin", "--username", user, "--password", pw, "--email", email, "--must-change-password=false", check=False)
    created = "already exists" not in out.lower()
    tok = _forge("admin", "user", "generate-access-token", "--username", user, "--token-name", f"olnm-{int(time.time())}", "--scopes", "all", "--raw")
    st.update(port=port, user=user, token=tok.strip().splitlines()[-1])
    if created:
        st["password"] = pw
    _fsave(st)
    if not DIAL_FILE.exists():
        _write_dial(1)
    basic = base64.b64encode(f"{user}:{st['token']}".encode()).decode()
    _sh("git", "config", "--global", "--replace-all", f"http.http://localhost:{port}/.extraHeader", f"Authorization: Basic {basic}")
    print(f"🏗️  http://localhost:{port}  user={user}" + (f"  password={pw}" if created else "  (user existed)"))
    print(f"🔑 token → {FSTATE}   🔐 git auth → ~/.gitconfig")
    return st


def hub_up() -> int:
    """Start the forge in the background."""
    if pid := _running():
        print(f"🏠 already up pid={pid}")
        return pid
    if os.geteuid() == 0:
        print("⚠️  running as root: Gitea / Forgejo refuse to serve as root → run olnm as a normal user")
    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / "web.out").open("a") as output:
        p = subprocess.Popen([str(BIN), "--config", str(INI), "web"], stdout=output,
                             stderr=subprocess.STDOUT, start_new_session=True)
    try:
        PID.write_text(str(p.pid))
        port = hub_port()
        for _ in range(60):
            if p.poll() is not None:
                raise SystemExit(f"❌ forge exited before becoming healthy → {LOG / 'web.out'}")
            try:
                _fetch(f"http://127.0.0.1:{port}/api/healthz", timeout=2)
                if p.poll() is not None:
                    raise SystemExit(f"❌ forge exited during startup → {LOG / 'web.out'}")
                print(f"🏠 up pid={p.pid} → http://localhost:{port}")
                return p.pid
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(0.5)
        raise SystemExit(f"❌ forge health check timed out → {LOG / 'web.out'}")
    except BaseException:
        # Only stop the child created by this call, never a PID read from shared state.
        stopped = p.poll() is not None
        try:
            if not stopped:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=5)
                stopped = True
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"⚠️  failed to stop startup child {p.pid}: {exc}; inspect {LOG / 'web.out'}",
                  file=sys.stderr)
        # A different manager may have replaced the PID file during startup.
        if stopped and PID.exists() and PID.read_text().strip() == str(p.pid):
            PID.unlink()
        raise


def hub_down() -> None:
    """Stop the forge."""
    if pid := _running():
        os.kill(pid, signal.SIGTERM)
        PID.unlink(missing_ok=True)
        print(f"🛑 stopped pid={pid}")


def hub_status() -> dict:
    """Dial, forge state, repo count."""
    st, pid, lv = _fstate(), _running(), read_dial()
    print(f"🎛️  {dial_label(lv)} | {'🟢 pid=' + str(pid) if pid else '⚪ down'} | 📚 {len(st['repos'])} | http://localhost:{st['port']}")
    return {"dial": lv, "pid": pid, "repos": st["repos"]}


def hub_logs(n: int = 40) -> str:
    """Tail the forge web log."""
    f = LOG / "web.out"
    out = "\n".join(f.read_text(errors="replace").splitlines()[-n:]) if f.exists() else "(no log yet)"
    print(out)
    return out


def hub_api(method: str, path: str, data: dict | None = None, token: str | None = None, base: str | None = None):
    """Gitea / Forgejo REST v1 (GitHub-shaped): hub_api('GET', '/user/repos')."""
    st = _fstate()
    url = (base or f"http://127.0.0.1:{st['port']}/api/v1") + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method.upper(), headers={"Authorization": f"token {token or st.get('token', '')}", "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with _open(req, 30) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"❌ {method} {path} → {e.code} {e.read().decode(errors='replace')[:300]}")


def _github_token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok and shutil.which("gh"):
        tok = _sh("gh", "auth", "token", check=False)
    if not tok:
        raise SystemExit("❌ dial 2 mirroring needs GITHUB_TOKEN or `gh auth login`")
    return tok


def _ensure_forge_repo(name: str, private: bool = True) -> None:
    if name not in {r["name"] for r in (hub_api("GET", "/user/repos?limit=200") or [])}:
        hub_api("POST", "/user/repos", {"name": name, "private": private, "default_branch": "main", "auto_init": False})
        print(f"  🆕 forge repo {name}")


def _point_origin(p: Path, level: int, st: dict) -> str:
    r = st["repos"][str(p)]
    target = "bare" if level == 0 else ("github" if level == 3 and r.get("github") else "local")
    url = _sh("git", "remote", "get-url", target, cwd=p, check=False) or _sh("git", "remote", "get-url", "bare", cwd=p)
    _sh("git", "remote", "remove", "origin", cwd=p, check=False)
    _sh("git", "remote", "add", "origin", url, cwd=p)
    print(f"  🎯 {r['name']}: origin → {target}")
    return target


def _ensure_push_mirror(r: dict, st: dict) -> None:
    if not r.get("github"):
        return
    orp, gh_url = f"{st['user']}/{r['name']}", f"https://github.com/{r['github']}.git"
    if any(m.get("remote_address", "").rstrip("/") == gh_url for m in hub_api("GET", f"/repos/{orp}/push_mirrors") or []):
        return
    hub_api("POST", f"/repos/{orp}/push_mirrors", {"remote_address": gh_url, "remote_username": r["github"].split("/")[0], "remote_password": _github_token(), "interval": "1h", "sync_on_commit": True})
    print(f"  🔁 push-mirror → {r['github']}")


def _hub_apply(level: int) -> None:
    st = _fstate()
    if level == 0:
        hub_down()
    elif BIN.exists() and INI.exists():
        hub_up()
    for path, r in st["repos"].items():
        p = Path(path)
        if not p.exists():
            continue
        _point_origin(p, level, st)
        if level >= 1 and _running():
            _ensure_forge_repo(r["name"], r.get("private", True))
            if level == 2:
                _ensure_push_mirror(r, st)


def hub_repo_add(path: str = ".", github: str | None = None, private: bool = True) -> dict:
    """Register a working tree: forge repo + bare backup, remotes `local` `bare` (`github`), origin by dial."""
    p = Path(path).resolve()
    if not (p / ".git").exists():
        _sh("git", "init", "-q", "-b", "main", cwd=p)
    st, name = _fstate(), p.name
    bare = BARE / f"{name}.git"
    if not bare.exists():
        bare.parent.mkdir(parents=True, exist_ok=True)
        _sh("git", "init", "-q", "--bare", "-b", "main", str(bare))
    if _running():
        _ensure_forge_repo(name, private)
    else:
        print("⚠️  forge down; repo is created on next `olnm_dial 1` / `hubdial up`")
    remotes = {"local": f"http://localhost:{st['port']}/{st['user']}/{name}.git", "bare": str(bare)}
    if github:
        remotes["github"] = f"https://github.com/{github}.git"
    for rname, url in remotes.items():
        _sh("git", "remote", "remove", rname, cwd=p, check=False)
        _sh("git", "remote", "add", rname, url, cwd=p)
    st["repos"][str(p)] = {"name": name, "github": github, "private": private}
    _fsave(st)
    print(f"📚 {name}  " + "  ".join(f"{k}={v}" for k, v in remotes.items()))
    _point_origin(p, read_dial(), st)
    return st["repos"][str(p)]


def hub_repo_ls() -> dict:
    """Registered repos."""
    repos = _fstate()["repos"]
    for path, r in repos.items():
        print(f"📚 {r['name']:24} {path}  {('☁️ ' + r['github']) if r.get('github') else ''}")
    return repos


def hub_repo_rm(path: str = ".") -> None:
    """Unregister a working tree (nothing deleted)."""
    st = _fstate()
    st["repos"].pop(str(Path(path).resolve()), None)
    _fsave(st)
    print("🗑️  unregistered")


def hub_sync() -> dict:
    """Push every registered repo to bare / local / github (github only at dial ≥2)."""
    st, lv, res = _fstate(), read_dial(), {}
    for path, r in st["repos"].items():
        p = Path(path)
        if not p.exists():
            continue
        for rem in ("bare", "local", "github"):
            if (rem == "local" and not _running()) or (rem == "github" and lv < 2):
                continue
            if _sh("git", "remote", "get-url", rem, cwd=p, check=False):
                ok = subprocess.run(["git", "push", "-q", "--all", rem], cwd=p, capture_output=True).returncode == 0
                res[f"{r['name']}:{rem}"] = ok
                print(f"  {'✅' if ok else '⚠️ '} {r['name']} → {rem}")
    return res


def _owner_repo(path: str = ".") -> str:
    st = _fstate()
    r = st["repos"].get(str(Path(path).resolve()))
    if not r:
        raise SystemExit("❌ not a registered repo → hubadd")
    return f"{st['user']}/{r['name']}"


def hub_issue_ls(path: str = ".", state: str = "open") -> list:
    """Issues of the current repo."""
    items = hub_api("GET", f"/repos/{_owner_repo(path)}/issues?state={state}&type=issues") or []
    for i in items:
        print(f"🐛 #{i['number']:<4} {i['title']}  {' '.join('🏷️' + l['name'] for l in i.get('labels', []))}")
    return items


def hub_issue_new(title: str, body: str = "", labels: list[str] | None = None, path: str = ".") -> dict:
    """New issue; labels by name (unknown names are skipped)."""
    orp = _owner_repo(path)
    have = {l["name"]: l["id"] for l in hub_api("GET", f"/repos/{orp}/labels") or []} if labels else {}
    it = hub_api("POST", f"/repos/{orp}/issues", {"title": title, "body": body, "labels": [have[n] for n in labels or [] if n in have]})
    print(f"🐛 #{it['number']} {it['html_url']}")
    return it


def hub_pr_ls(path: str = ".") -> list:
    """Open pull requests."""
    items = hub_api("GET", f"/repos/{_owner_repo(path)}/pulls?state=open") or []
    for p in items:
        print(f"🔀 #{p['number']:<4} {p['head']['ref']} → {p['base']['ref']}  {p['title']}")
    return items


def hub_pr_new(title: str, head: str | None = None, base: str = "main", body: str = "", path: str = ".") -> dict:
    """PR from the current branch (pushed to `local` first)."""
    p = Path(path).resolve()
    head = head or _sh("git", "branch", "--show-current", cwd=p)
    _sh("git", "push", "-q", "-u", "local", head, cwd=p)
    orp = _owner_repo(path)
    for _ in range(30):  # the forge indexes pushed branches asynchronously
        with contextlib.suppress(SystemExit):
            hub_api("GET", f"/repos/{orp}/branches/{head}")
            break
        time.sleep(0.5)
    pr = hub_api("POST", f"/repos/{orp}/pulls", {"title": title, "head": head, "base": base, "body": body})
    print(f"🔀 #{pr['number']} {pr['html_url']}")
    return pr


def hub_labels(path: str = ".") -> None:
    """GitHub's default labels (bug, enhancement, …) in the current repo."""
    orp = _owner_repo(path)
    have = {l["name"] for l in hub_api("GET", f"/repos/{orp}/labels") or []}
    for name, color in GH_LABELS.items():
        if name not in have:
            hub_api("POST", f"/repos/{orp}/labels", {"name": name, "color": "#" + color})
    print(f"🏷️  labels ready in {orp}")


def hub_doctor() -> dict:
    """Binary, config, token, forge, git, gh, GitHub reachability."""
    st = _fstate()
    checks = {"binary": BIN.exists(), "app.ini": INI.exists(), "token": bool(st.get("token")), "forge up": bool(_running()), "git": bool(shutil.which("git")), "gh": bool(shutil.which("gh"))}
    try:
        _fetch("https://api.github.com", timeout=5)
        checks["github 🌍"] = True
    except Exception:
        checks["github 🌍"] = False
    print(" ".join(("✅ " if v else "❌ ") + k for k, v in checks.items()))
    return checks



def build_parser(prog: str = "local_forge"):
    ap = argparse.ArgumentParser(prog=prog)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("hub", prog=prog, help="🏠 local GitHub-like forge"); h = s.add_subparsers(dest="sub", required=True)  # main() adds "hub"; keep it out of usage
    x = h.add_parser("install", help="📦 🌍 download or --from carried binary"); x.add_argument("--version", default="latest"); x.add_argument("--from", dest="src"); x.add_argument("--sha256", dest="sha"); x.add_argument("--flavor", choices=sorted(FLAVORS), default="gitea")
    x = h.add_parser("bundle", help="🎒 🌍 binary + .sha256 + olnm.py into DIR"); x.add_argument("dir"); x.add_argument("--version", default="latest"); x.add_argument("--flavor", choices=sorted(FLAVORS), default="gitea")
    x = h.add_parser("init", help="🏗️ config, db, admin, token"); x.add_argument("--port", type=int, default=3000); x.add_argument("--user", default="admin"); x.add_argument("--password")
    for name, hp in (("up", "🟢 start"), ("down", "🛑 stop"), ("status", "📊 status"), ("doctor", "🩺 checks"), ("sync", "🔄 push to all remotes"), ("labels", "🏷️ GitHub default labels")):
        h.add_parser(name, help=hp)
    x = h.add_parser("logs", help="📜 tail log"); x.add_argument("-n", type=int, default=40)
    x = h.add_parser("dial", help="🎛️ show / set: offline · local · mirror · github (0-3 also work)"); x.add_argument("level", nargs="?", choices=[*DIAL_NAMES, *map(str, DIALS)], metavar="level", help="offline | local | mirror | github (0-3 also work); omit to show")
    x = h.add_parser("repo", help="📚 register working trees"); r = x.add_subparsers(dest="repo_cmd", required=True)
    y = r.add_parser("add"); y.add_argument("path", nargs="?", default="."); y.add_argument("--github", help="owner/name"); y.add_argument("--public", action="store_true")
    r.add_parser("ls"); y = r.add_parser("rm"); y.add_argument("path", nargs="?", default=".")
    x = h.add_parser("api", help="🌐 raw REST"); x.add_argument("method", choices=["GET", "POST", "PATCH", "PUT", "DELETE"]); x.add_argument("path"); x.add_argument("--data", help="JSON body")
    x = h.add_parser("issue", help="🐛 issues"); i = x.add_subparsers(dest="issue_cmd", required=True)
    y = i.add_parser("ls"); y.add_argument("--state", default="open", choices=["open", "closed", "all"])
    y = i.add_parser("new"); y.add_argument("title"); y.add_argument("--body", default=""); y.add_argument("--label", action="append", default=[])
    x = h.add_parser("pr", help="🔀 pull requests"); p = x.add_subparsers(dest="pr_cmd", required=True)
    p.add_parser("ls"); y = p.add_parser("new"); y.add_argument("title"); y.add_argument("--head"); y.add_argument("--base", default="main"); y.add_argument("--body", default="")
    _suggest(ap)
    return ap


def _suggest(parser: argparse.ArgumentParser) -> None:
    # 🤔 argparse 3.14+: "maybe you meant 'mirror'?" for choices and subcommands at every level; older Pythons ignore it
    parser.suggest_on_error = True
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for child in action.choices.values():
                _suggest(child)

def _hub_main(a: argparse.Namespace) -> None:
    match a.sub:
        case "install": hub_install(a.version, a.src, a.sha, a.flavor)
        case "bundle": hub_bundle(a.dir, a.version, flavor=a.flavor)
        case "init": hub_init(a.port, a.user, a.password)
        case "up": hub_up()
        case "down": hub_down()
        case "status": hub_status()
        case "doctor": hub_doctor()
        case "sync": hub_sync()
        case "labels": hub_labels()
        case "logs": hub_logs(a.n)
        case "dial": dial(a.level)
        case "repo": {"add": lambda: hub_repo_add(a.path, a.github, not a.public), "ls": hub_repo_ls, "rm": lambda: hub_repo_rm(a.path)}[a.repo_cmd]()
        case "api": print(json.dumps(hub_api(a.method, a.path, json.loads(a.data) if a.data else None), indent=2, ensure_ascii=False))
        case "issue": hub_issue_ls(state=a.state) if a.issue_cmd == "ls" else hub_issue_new(a.title, a.body, a.label)
        case "pr": hub_pr_ls() if a.pr_cmd == "ls" else hub_pr_new(a.title, a.head, a.base, a.body)



def main(argv=None, prog: str = "local_forge"):
    args = build_parser(prog).parse_args(["hub", *(sys.argv[1:] if argv is None else argv)])
    _hub_main(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
