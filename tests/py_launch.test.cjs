"use strict";
const assert = require("node:assert/strict");
const { spawn, spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { test } = require("node:test");
const launcher = require("../vendor/py_launch.cjs");

const LAUNCHER = path.join(__dirname, "..", "vendor", "py_launch.cjs");
const PYTHON = process.env.PY_LAUNCH_TEST_PYTHON || (process.platform === "win32" ? "python" : "python3");

test("the shared launcher keeps Node 24 as its minimum", () => {
  assert.deepEqual(launcher.MIN_NODE, [24, 0]);
  assert.throws(() => launcher.assertNodeVersion("23.9.0"), { code: "ENODEVERSION" });
  assert.doesNotThrow(() => launcher.assertNodeVersion("24.0.0"));
  assert.doesNotThrow(() => launcher.assertNodeVersion("26.0.0"));
});

function runWithSiteHook(mode, flags) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "aoi-launch-site-"));
  try {
    const marker = path.join(dir, "hook-ran");
    const script = path.join(dir, "echo.py");
    fs.writeFileSync(script, "import sys\nprint(sys.argv[1])\n");
    fs.writeFileSync(path.join(dir, "sitecustomize.py"),
      'import os\nwith open(os.environ["PY_LAUNCH_SITE_MARKER"], "w") as out:\n    out.write("ran")\nraise SystemExit(42)\n');
    const opts = JSON.stringify({ python: PYTHON, ...flags });
    const scriptArg = JSON.stringify(script);
    const calls = {
      resolve: `launcher.resolvePython(${opts}); console.log("safe");`,
      run: `process.stdout.write(launcher.run(${scriptArg}, ["safe"], ${opts}).stdout);`,
      main: `launcher.main(${scriptArg}, { ...${opts}, argv: ["safe"] });`,
    };
    const result = spawnSync(process.execPath,
      ["-e", `const launcher = require(${JSON.stringify(LAUNCHER)}); ${calls[mode]}`], {
        encoding: "utf8",
        env: { ...process.env, PYTHONPATH: dir, PY_LAUNCH_SITE_MARKER: marker },
        timeout: 10_000,
        killSignal: "SIGKILL",
      });
    return { result, hookRan: fs.existsSync(marker) };
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test("default interpreter discovery still enables site startup", () => {
  const { result, hookRan } = runWithSiteHook("resolve", {});
  assert.ifError(result.error);
  assert.equal(hookRan, true);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not suitable/);
});

for (const flags of [{ noSite: true }, { isolated: true }, { noSite: true, isolated: true }]) {
  for (const mode of ["resolve", "run", "main"]) {
    test(`${mode} suppresses sitecustomize during discovery and execution with ${JSON.stringify(flags)}`, () => {
      const { result, hookRan } = runWithSiteHook(mode, flags);
      assert.ifError(result.error);
      assert.equal(hookRan, false, "the interpreter probe must also suppress sitecustomize");
      assert.equal(result.status, 0, result.stderr);
      assert.equal(result.stdout.trim(), "safe");
    });
  }
}

test("discovery puts startup flags after interpreter prefixes and before -c", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "aoi-launch-prefix-"));
  try {
    const stub = path.join(dir, "probe.cjs");
    fs.writeFileSync(stub,
      'require("node:assert/strict").deepEqual(process.argv.slice(2, -1), ["-S", "-I", "-c"]);\nconsole.log("3.12");\n');
    const candidate = { cmd: process.execPath, prefix: [stub], label: "probe", strict: true };
    assert.equal(launcher.resolvePython({ candidates: [candidate], noSite: true, isolated: true }).cmd, process.execPath);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

for (const interrupts of [0, 2]) {
  for (const jsonErrors of [false, true]) {
    test(`forwards SIGTERM after ${interrupts} ignored SIGINTs (${jsonErrors ? "JSON" : "text"})`,
      { skip: process.platform === "win32", timeout: 15_000 }, async () => {
        const dir = fs.mkdtempSync(path.join(os.tmpdir(), "aoi-launch-signals-"));
        const script = path.join(dir, "ignore_sigint.py");
        fs.writeFileSync(script, [
          "import signal", "import time",
          "def ignore_interrupt(_signal, _frame):",
          '    print("IGNORED SIGINT", flush=True)',
          "signal.signal(signal.SIGINT, ignore_interrupt)",
          'print("READY", flush=True)',
          "while True:", "    time.sleep(60)", "",
        ].join("\n"));
        const opts = { python: PYTHON, jsonErrors, noSite: true };
        const child = spawn(process.execPath,
          ["-e", `require(${JSON.stringify(LAUNCHER)}).main(${JSON.stringify(script)}, ${JSON.stringify(opts)});`],
          { detached: true, stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, PY_LAUNCH_ERROR_FORMAT: "" } });
        let stdout = "";
        let stderr = "";
        let interruptsSent = 0;
        let sentTerm = false;
        let timedOut = false;
        let spawnError;
        const killGroup = () => {
          if (!child.pid) return;
          try { process.kill(-child.pid, "SIGKILL"); }
          catch (error) { if (error.code !== "ESRCH") throw error; }
        };
        const closed = new Promise((resolve) => child.once("close", (code, signal) => resolve({ code, signal })));
        const timer = setTimeout(() => { timedOut = true; killGroup(); }, 7_500);
        child.on("error", (error) => { spawnError = error; });
        child.stderr.on("data", (chunk) => { stderr += chunk; });
        child.stdout.on("data", (chunk) => {
          stdout += chunk;
          const acknowledged = (stdout.match(/IGNORED SIGINT\n/g) || []).length;
          if (!stdout.includes("READY\n") || sentTerm || acknowledged < interruptsSent) return;
          if (interruptsSent < interrupts) {
            interruptsSent += 1;
            child.kill("SIGINT");
          } else {
            sentTerm = true;
            child.kill("SIGTERM");
          }
        });
        try {
          const { code, signal } = await closed;
          assert.ifError(spawnError);
          assert.equal(timedOut, false, `launcher did not terminate; stdout=${stdout}; stderr=${stderr}`);
          assert.equal(interruptsSent, interrupts);
          assert.equal((stdout.match(/IGNORED SIGINT\n/g) || []).length, interrupts);
          assert.equal(sentTerm, true);
          assert.equal(code, 2);
          assert.equal(signal, null);
          if (jsonErrors) {
            const payload = JSON.parse(stderr);
            assert.equal(payload.ok, false);
            assert.equal(payload.code, "ESIGNAL");
            assert.equal(payload.exit_code, 2);
            assert.match(payload.message, /SIGTERM/);
          } else assert.match(stderr, /terminated by signal SIGTERM/);
        } finally {
          clearTimeout(timer);
          killGroup();
          fs.rmSync(dir, { recursive: true, force: true });
        }
      });
  }
}

// 親リポジトリ #185 の CLI テストを移植（パスは vendor/py_launch.cjs に合わせた）。
test("CLI: --site drops -S; default keeps -S; options work in any order before SCRIPT.py", () => {
  const { spawnSync } = require("node:child_process");
  const fs = require("node:fs");
  const os = require("node:os");
  const p = require("node:path");
  const dir = fs.mkdtempSync(p.join(os.tmpdir(), "pyl-site-"));
  const script = p.join(dir, "flags.py");
  fs.writeFileSync(script, "import sys\nprint(sys.flags.no_site, 'site' in sys.modules, ' '.join(sys.argv[1:]))\n");
  const launcher = LAUNCHER;
  const run = (argv, env) => spawnSync(process.execPath, [launcher, ...argv], { encoding: "utf8", env: env ?? process.env });
  const def = run([script, "x"]);
  assert.strictEqual(def.status, 0, def.stderr);
  assert.strictEqual(def.stdout.trim(), "1 False x");
  const site = run(["--site", script, "x"]);
  assert.strictEqual(site.status, 0, site.stderr);
  assert.strictEqual(site.stdout.trim(), "0 True x");
  const env = { ...process.env, MY_TOOL_PYTHON: PYTHON };
  for (const argv of [
    ["--env-var", "MY_TOOL_PYTHON", "--site", script],
    ["--site", "--env-var", "MY_TOOL_PYTHON", script],
    ["--site", "--env-var=MY_TOOL_PYTHON", script],
  ]) {
    const r = run(argv, env);
    assert.strictEqual(r.status, 0, `${argv.join(" ")}: ${r.stderr}`);
    assert.strictEqual(r.stdout.trim(), "0 True");
  }
  const strict = run(["--site", "--env-var", "MY_TOOL_PYTHON", script], { ...process.env, MY_TOOL_PYTHON: p.join(dir, "no-such-python") });
  assert.strictEqual(strict.status, 2);
  assert.match(strict.stderr, /MY_TOOL_PYTHON/);
  const after = run([script, "--site"]);
  assert.strictEqual(after.stdout.trim(), "1 False --site");
  const unknown = run(["--sites", script]);
  assert.strictEqual(unknown.status, 2);
  assert.match(unknown.stderr, /usage: node py_launch\.cjs \[--env-var NAME\] \[--site\] \[--\] SCRIPT\.py/);
  const missing = run(["--site", "--env-var"]);
  assert.strictEqual(missing.status, 2);
  assert.match(missing.stderr, /--env-var needs a variable name/);
  const noScript = run(["--site"]);
  assert.strictEqual(noScript.status, 2);
  assert.match(noScript.stderr, /usage:/);
});

test("CLI: lone -- ends options; repeated options: last wins; --site puts site-packages on sys.path", () => {
  const { spawnSync } = require("node:child_process");
  const fs = require("node:fs");
  const os = require("node:os");
  const p = require("node:path");
  const dir = fs.mkdtempSync(p.join(os.tmpdir(), "pyl-sep-"));
  const script = p.join(dir, "flags.py");
  fs.writeFileSync(script, "import sys\nprint(sys.flags.no_site, ' '.join(sys.argv[1:]))\n");
  const dash = p.join(dir, "-dash.py");
  fs.writeFileSync(dash, "print('dash')\n");
  const paths = p.join(dir, "paths.py");
  fs.writeFileSync(paths, "import os, sys, site\nn = os.path.normcase\nroots = {n(sys.prefix), n(sys.base_prefix)}\nprint(sum(1 for d in site.getsitepackages() if d in sys.path and n(d) not in roots))\n");
  const launcher = LAUNCHER;
  const run = (argv, env, cwd) => spawnSync(process.execPath, [launcher, ...argv], { encoding: "utf8", env: env ?? process.env, cwd });
  const sep = run(["--site", "--", script, "--", "x"]);
  assert.strictEqual(sep.status, 0, sep.stderr);
  assert.strictEqual(sep.stdout.trim(), "0 -- x");
  const sepDefault = run(["--", script]);
  assert.strictEqual(sepDefault.status, 0, sepDefault.stderr);
  assert.strictEqual(sepDefault.stdout.trim(), "1");
  const dashed = run(["--", "-dash.py"], process.env, dir);
  assert.strictEqual(dashed.status, 0, dashed.stderr);
  assert.strictEqual(dashed.stdout.trim(), "dash");
  const noDashScript = run(["--site", "--"]);
  assert.strictEqual(noDashScript.status, 2);
  assert.match(noDashScript.stderr, /usage: node py_launch\.cjs \[--env-var NAME\] \[--site\] \[--\] SCRIPT\.py/);
  const env = { ...process.env, GOOD_PY: PYTHON, BAD_PY: p.join(dir, "no-such-python") };
  const lastGood = run(["--env-var", "BAD_PY", "--env-var=GOOD_PY", script], env);
  assert.strictEqual(lastGood.status, 0, lastGood.stderr);
  const lastBad = run(["--env-var", "GOOD_PY", "--env-var", "BAD_PY", script], env);
  assert.strictEqual(lastBad.status, 2);
  assert.match(lastBad.stderr, /BAD_PY/);
  const twice = run(["--site", "--site", script]);
  assert.strictEqual(twice.status, 0, twice.stderr);
  assert.strictEqual(twice.stdout.trim(), "0");
  const withSite = run(["--site", paths]);
  assert.strictEqual(withSite.status, 0, withSite.stderr);
  assert.ok(Number(withSite.stdout.trim()) >= 1, withSite.stdout);
  const without = run([paths]);
  assert.strictEqual(without.status, 0, without.stderr);
  assert.strictEqual(without.stdout.trim(), "0");
});
