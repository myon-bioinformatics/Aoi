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
