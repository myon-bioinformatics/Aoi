"""🧪 olnm tests — `python -m unittest discover`."""
import json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="olnm-"))
sys.path.insert(0, str(ROOT))
with mock.patch.dict(os.environ, OLNM_HOME=str(TMP / "home"), DIAL_FILE=str(TMP / "dial")):
    import local_forge as olnm  # noqa: E402
PORT = 3777


def git(*a, cwd):
    return subprocess.run(["git", *a], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def reset_forge():
    olnm.hub_down()
    shutil.rmtree(olnm.FORGE, ignore_errors=True)
    olnm.DIAL_FILE.unlink(missing_ok=True)


class HubBase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, GIT_CONFIG_GLOBAL=str(TMP / "gitconfig"))
        patcher.start()
        self.addCleanup(patcher.stop)
        reset_forge()
        olnm.BIN.parent.mkdir(parents=True)
        shutil.copy(ROOT / "tests" / "fake_forgejo.py", olnm.BIN); olnm.BIN.chmod(0o755)
        self.wt = TMP / "wt"; shutil.rmtree(self.wt, ignore_errors=True); self.wt.mkdir()
        git("init", "-q", "-b", "main", cwd=self.wt)
        (self.wt / "a").write_text("a"); git("add", ".", cwd=self.wt)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init", cwd=self.wt)

    def tearDown(self):
        olnm.hub_down()


class TestHubInit(HubBase):
    def test_init_writes_ini_token_dial_and_git_auth(self):
        st = olnm.hub_init(port=PORT, password="pw")
        ini = olnm.INI.read_text()
        for line in (f"HTTP_PORT = {PORT}", "HTTP_ADDR = 127.0.0.1", "DISABLE_SSH = true", "OFFLINE_MODE = true", "DB_TYPE = sqlite3"):
            self.assertIn(line, ini)
        self.assertTrue(st["token"].startswith("fake-token"))
        self.assertEqual(oct(olnm.FSTATE.stat().st_mode)[-3:], "600")
        self.assertEqual(olnm.read_dial(), 1)
        self.assertIn("Authorization: Basic", git("config", "--global", f"http.http://localhost:{PORT}/.extraHeader", cwd=TMP))

    def test_up_down_idempotent(self):
        olnm.hub_init(port=PORT, password="pw")
        pid = olnm.hub_up(); self.assertTrue(olnm._running())
        self.assertEqual(olnm.hub_up(), pid)
        olnm.hub_down(); self.assertFalse(olnm._running())

    def test_install_from_carried_file_checks_sidecar(self):
        src = TMP / "forgejo-9.9.9-linux-amd64"; src.write_bytes(b"binary")
        side = TMP / "forgejo-9.9.9-linux-amd64.sha256"
        side.write_text("deadbeef  x\n")
        with self.assertRaises(SystemExit):
            olnm.hub_install(src=str(src))
        side.write_text(olnm._sha256(src) + "  x\n")
        olnm.hub_install(src=str(src)); self.assertEqual(olnm.BIN.read_bytes(), b"binary")


    def test_bundle_flavor_urls_and_sha_check(self):
        seen = []
        def fake_fetch(url, dest=None, timeout=0):
            seen.append(url)
            data = b"bin" if not url.endswith(".sha256") else (olnm.hashlib.sha256(b"bin").hexdigest() + "  x\n").encode()
            if dest:
                dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
            return data
        with mock.patch.object(olnm, "_fetch", fake_fetch):
            path = olnm.hub_bundle(str(TMP / "carry"), version="1.2.3", flavor="gitea")
        self.assertEqual(seen[0], "https://github.com/go-gitea/gitea/releases/download/v1.2.3/gitea-1.2.3-linux-amd64")
        self.assertEqual(path.name, "gitea-1.2.3-linux-amd64")
        self.assertTrue((TMP / "carry" / "local_forge.py").exists())
        with mock.patch.object(olnm, "_fetch", lambda url, dest=None, timeout=0: b"bin" if not url.endswith(".sha256") else b"bad  x"):
            with self.assertRaises(SystemExit):
                olnm.hub_bundle(str(TMP / "carry2"), version="1.2.3")


    def test_latest_falls_back_to_verified(self):
        def blocked(*a, **k):
            raise olnm.urllib.error.URLError("blocked")
        with mock.patch.object(olnm, "_fetch", blocked), mock.patch.object(olnm, "_open", blocked):
            self.assertEqual(olnm._latest_version("gitea"), olnm.VERIFIED["gitea"])
            with self.assertRaises(SystemExit):
                olnm._latest_version("forgejo")

    def test_ini_pins_public_url(self):
        olnm.hub_init(port=PORT, password="pw")
        self.assertIn("PUBLIC_URL_DETECTION = legacy", olnm.INI.read_text())


class TestHub(HubBase):
    def setUp(self):
        super().setUp(); olnm.hub_init(port=PORT, password="pw"); olnm.hub_up()

    def test_repo_add_creates_forge_repo_and_remotes(self):
        olnm.hub_repo_add(str(self.wt), github="me/wt")
        self.assertEqual(set(git("remote", cwd=self.wt).split()), {"origin", "local", "bare", "github"})
        self.assertEqual([r["name"] for r in olnm.hub_api("GET", "/user/repos")], ["wt"])
        olnm.hub_repo_add(str(self.wt), github="me/wt")
        self.assertEqual(len(olnm.hub_api("GET", "/user/repos")), 1)

    def test_dial_moves_origin_and_forge(self):
        olnm.hub_repo_add(str(self.wt), github="me/wt")
        origin = lambda: git("remote", "get-url", "origin", cwd=self.wt)
        olnm.dial(0); self.assertEqual(origin(), str(olnm.BARE / "wt.git")); self.assertFalse(olnm._running())
        olnm.dial(1); self.assertIn(f"localhost:{PORT}/admin/wt.git", origin()); self.assertTrue(olnm._running())
        olnm.dial(3); self.assertEqual(origin(), "https://github.com/me/wt.git")
        self.assertEqual(olnm.read_dial(), 3)

    @mock.patch.object(olnm, "_github_token", return_value="ghtok")
    def test_dial2_push_mirror_once(self, _tok):
        olnm.hub_repo_add(str(self.wt), github="me/wt")
        olnm.dial(2); olnm.dial(2)
        mirrors = olnm.hub_api("GET", "/repos/admin/wt/push_mirrors")
        self.assertEqual(len(mirrors), 1)
        self.assertEqual(mirrors[0]["remote_address"], "https://github.com/me/wt.git")

    def test_labels_and_issues(self):
        olnm.hub_repo_add(str(self.wt))
        olnm.hub_labels(str(self.wt)); olnm.hub_labels(str(self.wt))
        names = [l["name"] for l in olnm.hub_api("GET", "/repos/admin/wt/labels")]
        self.assertIn("bug", names); self.assertEqual(len(names), len(set(names)))
        it = olnm.hub_issue_new("crash", labels=["bug", "nope"], path=str(self.wt))
        self.assertEqual([l["name"] for l in it["labels"]], ["bug"])
        self.assertEqual([i["title"] for i in olnm.hub_issue_ls(str(self.wt))], ["crash"])

    def test_pr_waits_for_branch_then_opens(self):
        olnm.hub_repo_add(str(self.wt))
        git("switch", "-qc", "fix", cwd=self.wt)
        bare = olnm.BARE / "wt.git"
        git("remote", "set-url", "local", str(bare), cwd=self.wt)  # fake forge has no git transport; push lands in bare
        pr = olnm.hub_pr_new("fix crash", path=str(self.wt))
        self.assertEqual((pr["number"], pr["head"]["ref"], pr["base"]["ref"]), (1, "fix", "main"))
        self.assertEqual([p["title"] for p in olnm.hub_pr_ls(str(self.wt))], ["fix crash"])

    def test_sync_bare_and_skip_github_below_dial2(self):
        olnm.hub_repo_add(str(self.wt), github="me/wt")
        res = olnm.hub_sync()
        self.assertTrue(res["wt:bare"]); self.assertNotIn("wt:github", res)
        self.assertEqual(git("--git-dir", str(olnm.BARE / "wt.git"), "rev-parse", "main", cwd=TMP), git("rev-parse", "main", cwd=self.wt))

    def test_bad_token(self):
        with self.assertRaises(SystemExit) as e:
            olnm.hub_api("GET", "/user/repos", token="wrong")
        self.assertIn("401", str(e.exception))



class TestDialNames(unittest.TestCase):
    """🎛️ People type names; the shared dial file keeps the digit (olnm reads the same file)."""

    def setUp(self):
        reset_forge()

    def test_names_digits_and_rejects(self):
        for given, level in (("offline", 0), ("Local", 1), (" mirror ", 2), ("github", 3), ("2", 2), (0, 0)):
            with self.subTest(given=given):
                self.assertEqual(olnm.dial_level(given), level)
        for bad in ("4", "mirorr", "", True, 7):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                olnm.dial_level(bad)

    def test_dial_by_name_stores_digit_and_shows_name_first(self):
        self.assertEqual(olnm.dial("mirror"), 2)
        self.assertEqual(olnm.DIAL_FILE.read_text().strip(), "2")
        self.assertEqual(olnm.dial_label(2), "🔁 mirror (2)")
        with self.assertRaises(SystemExit) as e:
            olnm.dial("mirorr")
        self.assertIn("offline, local, mirror, github", str(e.exception))
        self.assertEqual(olnm.read_dial(), 2)  # a rejected name changes nothing


def nagoyaction(*argv, home):
    env = dict(os.environ, OLNM_HOME=str(home), DIAL_FILE=str(home / "dial"))
    return subprocess.run([sys.executable, str(ROOT / "nagoyaction.py"), *argv], capture_output=True, text=True, env=env, timeout=60)


class TestNagoyactionHub(unittest.TestCase):
    """🏠 nagoyaction.py hub … hands every argument to local_forge (exit codes included)."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="nagoyaction-hub-"))
        self.addCleanup(shutil.rmtree, self.home, True)

    def test_dial_and_status_through_nagoyaction(self):
        self.assertIn("🔁 mirror (2)", nagoyaction("hub", "dial", "mirror", home=self.home).stdout)
        self.assertEqual((self.home / "dial").read_text().strip(), "2")
        shown = nagoyaction("hub", "dial", home=self.home)
        self.assertEqual(shown.returncode, 0)
        self.assertIn("🔁 mirror (2)", shown.stdout)
        self.assertIn("🔁 mirror (2) | ⚪ down", nagoyaction("hub", "status", home=self.home).stdout)

    def test_help_and_typos_reach_local_forge(self):
        helped = nagoyaction("hub", "dial", "--help", home=self.home)
        self.assertEqual(helped.returncode, 0)
        self.assertIn("usage: nagoyaction hub dial", helped.stdout)
        self.assertNotIn("hub hub", helped.stdout)  # local_forge's internal "hub" stays hidden
        typo = nagoyaction("hub", "dial", "mirorr", home=self.home)
        self.assertEqual(typo.returncode, 2)
        self.assertIn("invalid choice: 'mirorr'", typo.stderr)
        if sys.version_info >= (3, 14):
            self.assertIn("maybe you meant 'mirror'?", typo.stderr)
        self.assertFalse((self.home / "dial").exists())

    def test_python_callable_by_name(self):
        code = ("import os, sys; sys.path.insert(0, sys.argv[1]); import nagoyaction;"
                " sys.exit(nagoyaction.hub('dial', 'local'))")
        env = dict(os.environ, OLNM_HOME=str(self.home), DIAL_FILE=str(self.home / "dial"))
        run = subprocess.run([sys.executable, "-c", code, str(ROOT)], capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual((self.home / "dial").read_text().strip(), "1")
