# NagoyAction

📘 [利用ガイド / Usage guide](https://myon-bioinformatics.github.io/NagoyAction/) (GitHub Pages)

<p align="center">
  <img src="docs/brand/icon.png" alt="NagoyAction icon" width="160" />
</p>

[Icon](docs/brand/icon.png) · [Favicon](docs/brand/favicon.png)

> Turning research into a system you can keep running.
>
> Define a research pipeline once in TOML and run it with the same stdlib-only command locally and on GitHub Actions, with run receipts, Markdown link checking and publication gates for Aoi's NPB baseball research (split out from Aoi/nagoyaction).

![NagoyAction](https://github.com/myon-bioinformatics/Aoi/raw/main/docs/images/nagoyaction.webp)

*Concept image (a figure for sharing the idea; not the actual data or HTML structure)*

## Role in Aoi

**Automation and orchestration.**

| Challenges | Approach | Outcomes & value |
|---|---|---|
| Research is hard to automate and keep running | 1. Describe the flow once in TOML | Support for automating research |
| Local runs and GitHub need to stay in sync | 2. Run the same command everywhere | Easy reproduction and sharing |
| Data processing needs to run on a schedule | 3. Keep a receipt for every run | Continuous analysis |

Topics: GitHub Actions, automation, workflow

## Overview

Write a pipeline once in TOML and run it with **the same command locally and on GitHub Actions**.
For projects whose data can't leave the machine, just run the same definition locally.

- `doctor`: checks the Python version, required tools (e.g. git, uv), optional tools (e.g. gh), and whether the artifacts needed for offline runs exist. If anything is missing it exits 1 and stops before running. Warnings only give 0
- `show`: displays the pipeline structure (variables, steps, commands, outputs, network requirements) (`--json` gives `nagoyaction-pipeline/1`)
- `run`: runs the steps in order after doctor and leaves a receipt (JSONL) at `--receipt`. Returns the failing step's exit code as-is
- Usage, TOML, pipeline definition, and file loading errors exit 2. With `--json`, failures are `nagoyaction-error/1` on stderr. `error.code` is `doctor` / `step` / `pipeline` / `usage` / `toml` / `io`. A step that itself exits 2 is distinguished from a definition error by this `error.code`
- Flag descriptions and exit codes are in `python nagoyaction.py --help` and each `--help` of `doctor` / `show` / `run`. `--json` works the same before or after the subcommand
- `localci`: checks workflows and tests locally without waiting for GitHub Actions to finish ("Local CI" below)
- Steps run as argument arrays, not through a shell
- Standard library only (Python 3.11+). Copy this one file to use it in other repositories

A repository split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) (see "Relationship with Aoi" below).

## Installation and usage

### Local forge (migration in progress)

`local_forge.py` provides the local Gitea/Forgejo management functions extracted from OneLinearNumerousMemo. It uses the existing `OLNM_HOME` and `DIAL_FILE` locations so that a local forge can be found during migration. It is a standard-library module invoked as `nagoyaction hub …`; it does not implement GitHub Actions runners.

Prepare an isolated uv tool project with `python vendor/uv_tool_build.py nagoyaction.py --module local_forge.py --module localci.py --out build/nagoyaction-tool`, then install it with `uv tool install ./build/nagoyaction-tool`. This installs the `nagoyaction` command only (`nagoyaction hub …` covers local forge operations; there is no `local-forge` command). The bundled modules have no third-party runtime dependencies. Pipeline definitions and project-specific inputs remain separate files. The builder itself is the vendored shared copy from Aoi (`vendor/uv_tool_build.py`).

```bash
nagoyaction hub --help          # or: python nagoyaction.py hub --help
nagoyaction hub status
nagoyaction hub dial mirror     # 🎛️  → 🔁 mirror (2)
nagoyaction hub repo ls
```

`nagoyaction hub …` passes every argument to `local_forge.py` (replacing the former `local-forge …` command). `python local_forge.py …` still runs the same module directly, and OneLinearNumerousMemo's `olnm hub …` forwards here. From Python, `nagoyaction.hub("dial", "local")` does the same and returns the exit code. `local_forge.py` is imported only for `hub`, so pipeline commands never load it.

The dial takes a name: `offline` (no network), `local` (local forge only), `mirror` (local forge that mirrors GitHub) or `github` (GitHub directly). Output shows the name first and the stored digit after it, for example `🔁 mirror (2)`. The dial file keeps the digit 0–3, so older readers of `DIAL_FILE` keep working, and `dial 2` is still accepted. A mistyped name is rejected with a suggestion (`maybe you meant 'mirror'?` on Python 3.14+) and leaves the dial unchanged.

OneLinearNumerousMemo forwards `olnm hub …` and `olnm dial …` here once its handover change is merged. The BlueProbe/QueRyu launchers are not yet migrated. Do not run both managers concurrently against the same forge.

A newly started forge must pass its health check before startup reports success. Failed startup stops only the child created by that invocation; if cleanup fails, its PID is retained for inspection. A dial change saves its new value only after applying the forge and repository changes. This is not a transaction: earlier process, remote, repository, or mirror changes are not automatically rolled back if a later operation fails. Inspect the forge and repository remotes before retrying; the retained previous dial does not prove every side effect was reverted.

CI's `real-local-forge` job downloads and checksum-verifies Gitea 1.27.3, starts it on localhost in temporary state, and exercises repository creation, push, issue, and pull request operations. The test has no dependency on a real GitHub account or a persistent user configuration. Forgejo remains covered by the fake-server tests only.

No installation needed. It runs on the Python 3.11+ standard library alone.

```bash
python nagoyaction.py doctor <pipeline.toml>            # pre-run check
python nagoyaction.py show   <pipeline.toml>            # show pipeline structure (--json also works)
python nagoyaction.py show   <pipeline.toml> -v x=val   # show with a variable overridden
python nagoyaction.py run    <pipeline.toml>            # run
python nagoyaction.py run    <pipeline.toml> --offline  # don't fetch
python nagoyaction.py run    <pipeline.toml> --from a --until b  # run only the given range of steps
python nagoyaction.py run    <pipeline.toml> -v x=val   # override a variable from the command line
python nagoyaction.py run    <pipeline.toml> --dry-run  # only show what would be done
```

A pipeline TOML has `name`, `root`, `[requires]` (Python version, tools), and `[[step]]` (`name`, argument array `run`, `network`, `outputs`). Examples are `pipelines/research.toml` and `pipelines/inbox.toml`.

Steps inherit the runner's environment. NagoyAction never puts other projects on the import path itself: inside Aoi, start it with `python aoi.py nagoyaction run <pipeline.toml>` so that steps such as `queryu/queryu.py` and `inbox/inbox.py` find QueRyu, BlueProbe, SakAnalytics and Aoi's `aoi_npb` by name (`aoi.py` passes Aoi's pytest `pythonpath`). The same goes for `python aoi.py nagoyaction/annual_history_report.py …`.

GitHub Actions workflows only call this command (e.g. `.github/workflows/cycle-c001.yml`).
Org-wide reusable workflows (actionlint, etc.) come from `myon-bioinformatics/myon-bioinformatics`.
To bring in shared modules from other repositories, use that repository's `vendor_sync.py` (SHA-pinned).

## Layout

| File | Contents | ➡️ Planned place |
|---|---|---|
| `nagoyaction.py` | The single file (stdlib only): pipeline pre-checks (`doctor`), structure display (`show`), execution (`run`), and 🔗 `linkcheck` ("Link checking" below). `actionlint` / `hub` hand over to `localci` / `local_forge` | stays at the top |
| `localci.py`, `localci_pytest.py` | Workflow checks repeated locally (actionlint, resolving referenced SHAs, `uses:` pins). "Local CI" below | `core/` |
| `local_forge.py` | Local Gitea / Forgejo (`nagoyaction hub`) | `core/` |
| `publication_gate.py`, `ghi_execution.py`, `PUBLICATION.md` | Pre-publication evidence checks (offline) and matching against running GitHub Actions | `core/` |
| `research_digest.py`, `docs/research-digest.md` | Index of research records (R*.md) and proposition judgements (no network or LLM needed) | `npb/` |
| `annual_history_report.py` | Lists annual audit results and synthetic model verification results side by side, kept separate | `npb/` |
| `pipelines/` | Pipeline definitions (`research.toml`, `inbox.toml`) | as is |
| `inbox/inbox.py`, `docs/inbox.md` | Question intake | as is |
| `containers/` | Local LLM container (not connected. "Local LLM container" below) | as is |
| `tests/` | pytest (run inside Aoi. "Tests" below) | as is |

➡️ The modules marked `core/` / `npb/` move when NagoyAction is next synced into Aoi, together with Aoi's side: the tests run inside Aoi's tree with Aoi's pytest `pythonpath` (`nagoyaction` only), and Aoi calls them by path (`links.yml` → `nagoyaction.py linkcheck`, `ci.yml` and `cycles/c001-chunichi/pipeline.toml` → `research_digest.py`, `c001-replay-audit.yml` → `ghi_execution.py`, `scripts/c001_publication_policy.py` → `publication_gate`, DRAgoWing's `tests/test_export.py` → `localci`). Aoi's `pythonpath` then gains `nagoyaction/core` and `nagoyaction/npb`, and `nagoyaction.py` adds its own `core/` for `actionlint` / `hub`.

## Local CI (`localci.py`)

Checks workflows and tests locally without waiting for GitHub Actions to finish.

`nagoyaction actionlint` runs only actionlint and the `uses:` pin checks on the current directory's `.github/workflows` (`--root` to choose another): no SHA resolution, no pytest, no Aoi checkout. It reports every failure in one pass, and `--strict` makes stale SHA pins fail. The actionlint binary and its record stay in `~/.cache/nagoyaction/localci`, so linting another repository writes nothing into it.

actionlint itself is a Go program, but Go is not needed: localci downloads the prebuilt release binary and verifies its checksum. Where that is not possible (a closed network, a blocked or rate-limited GitHub API), `nagoyaction actionlint` works best effort instead of stopping:

| What it can reach | actionlint | `uses:` pins |
|---|---|---|
| GitHub | latest release, verified (`go run` at that tag if only the download fails and Go exists) | compared with the latest release |
| no GitHub, an earlier run's download in `~/.cache/nagoyaction/localci` | that cached, verified version | `[skip]`: SHA pin or not is shown, staleness is not compared |
| no GitHub, `actionlint` on PATH (carried in) | that binary | `[skip]` as above |
| none of these | `[skip]`: not linted | `[skip]` as above |

A `[skip]` is not a failure: the exit code stays 0 and the summary ends with `⚠️ best effort: N 件は検査できず [skip]` (plus `何も確かめていない` when nothing could be checked). Real findings still fail with exit code 1. Once GitHub does not answer, the remaining checks do not ask again, so the run does not wait for one timeout per action. `--strict` turns best effort off: anything that cannot be checked fails, as does a stale pin. Inside GitHub Actions best effort is always off. `python localci.py run` (and `--all`) is unchanged and still requires GitHub. `nagoyaction actionlint --all …` is `python localci.py run …` (options included). From Python, `nagoyaction.actionlint("--strict")` returns the exit code. `python localci.py lint` is the same check without nagoyaction.

`python localci.py run` checks `.github/workflows` with actionlint. If shellcheck is on PATH, actionlint also uses it for `run:` blocks. actionlint resolves the latest rhysd/actionlint release on every run and verifies the published checksums and GitHub's digest. The version is not pinned in source. The resolved tag, asset name, and verified sha256 are left in the output and `.localci/refs.env`, and written next to the resolved referenced SHAs if `GITHUB_STEP_SUMMARY` exists. On GitHub Actions it stops if fetching or verification fails and does not fall back to Go. Locally, only when the tag could be resolved, it falls back to `go run github.com/rhysd/actionlint/cmd/actionlint@<tag>`. At the same time it resolves the main SHA of referenced repositories with `git ls-remote` plus a GitHub API repository id check, and writes them to `.localci/refs.env`. Whether `uses:` pins match the commit of each action's latest release tag is only reported by default. Setup actions (`actions/setup-python`, `actions/setup-node`, `astral-sh/setup-uv`) use the release's 40-character SHA and `# vX.Y.Z`. Other `actions/*` use the moving major tag `vN`.

```bash
python localci.py run                         # one pass over all of Aoi's tests/ (one shard)
python localci.py run --repeat 10             # one pass over all of it split into 10 rounds
python localci.py run --repeat 10 --seed 7    # reproduce the same split and input substitutions
python localci.py run --repeat 10 --keep-going
python localci.py run --self-tests            # only tests/test_localci.py (no Aoi)
python localci.py run --strict                # fail on stale SHA pins; vN for non-setup actions/* is allowed
python localci.py resolve                     # only resolve SHAs; CI's resolve job uses this too
nagoyaction actionlint                        # actionlint + uses: pins only (= python localci.py lint)
nagoyaction actionlint --strict --all --repeat 10   # = python localci.py run --strict --repeat 10
```

`--repeat N` does not trace the same checks N times. It shuffles the check list (resolving references, actionlint, each `uses:`, the pytest tests) by seed and splits it into N nearly equal shards. Each round runs only one shard, and once all rounds finish every check has run exactly once. It stops at a failing round and prints the round number, shard contents, and seed. `--keep-going` continues. After each round it prints the number of rounds passed and completed against N. Getting deep without failures is a confidence signal that the remaining shards will pass too.

Checks that pass with fixed values are switched to other values from that round's seed with `substitute(name, value, draw)`. In pytest, `-p localci_pytest` does the same via monkeypatch. Rounds can also be chosen with the plugin alone.

```bash
uv run --with pytest pytest -p localci_pytest --localci-repeat 10 --localci-round 3 --localci-seed 7
```

The references resolved are Aoi, `myon-bioinformatics/myon-bioinformatics`, the vendored `markdown` and `web-ui`, and the repositories listed in the repository root's `vendor.lock.json`. SHAs are not written in source. The GitHub Actions resolve job calls `python localci.py resolve --github-output` and passes the job output `sha` (Aoi) to checkout. Reusable workflow `uses:` can't be expressions, so they stay as pins in the file and localci compares them with the latest release.

The pytest suite checks out the Aoi SHA resolved at run time into `.localci/aoi` and collects from there. After confirming HEAD is that SHA, it overlays this repository's tree on `nagoyaction/` and splits all of `tests/` into `--repeat` shards. Each shard's pytest runs in one process. When uv is missing, or to run only this repository's checks without fetching Aoi, use `--self-tests` (only `tests/test_localci.py`). `--pytest PATH` also doesn't check out Aoi. CI's local-ci job uses `--repeat 10 --strict`, uses `github.run_id` as the seed, and prints `localci seed=` at start. `--strict` fails stale SHA pins and `uses:` of setup actions or reusable workflows that are not SHAs. Major tags `vN` of non-setup `actions/*` such as checkout, upload-artifact, download-artifact, and cache are not failed.

```bash
python localci.py run --self-tests
python localci.py run --pytest tests/test_localci.py
```

## Link checking (`nagoyaction.py linkcheck`)

```bash
python nagoyaction/nagoyaction.py linkcheck --help                                 # all flags and exit codes
python nagoyaction/nagoyaction.py linkcheck --root .                               # before push: match against git-tracked files, case-sensitive
python nagoyaction/nagoyaction.py linkcheck --remote OWNER/REPO --ref BRANCH       # after push: exists on that branch? (gh api)
python nagoyaction/nagoyaction.py linkcheck --external                             # also check http(s) (only 404/410 fail)
python nagoyaction/nagoyaction.py linkcheck --external --strict                    # unverified also fails (exit code 3)
python nagoyaction/nagoyaction.py linkcheck --json                                 # stdout is nagoyaction-linkcheck/1
```

`--root` is the base for git ls-files and Markdown loading (default: current directory). `--remote` requires `--ref`. `--external` checks http and https with HEAD. `--json` writes `nagoyaction-linkcheck/1` (`counts` and `results`) to stdout when scanning succeeded, and `nagoyaction-error/1` to stderr when the exit code is nonzero. Failures before scanning (usage, git) use the same error object, with exit code 2.

Exit codes:

- `0` — nothing broken. Unverified (external timeouts or 403, gh api errors other than 404) does not fail
- `1` — one or more broken. Broken takes precedence even with `--strict`
- `2` — usage error, or `git ls-files` failed
- `3` — only with `--strict`: nothing broken, one or more unverified (`status` or `remote`)

By default unverified gives 0. Aoi's Links workflow runs local and `--remote` without `--strict`. Failing on unreachable external links or transient gh failures would break that job. Add `--strict` only to calls that should fail on unverified.

GitHub is case-sensitive, so something that opens locally can 404 on GitHub (e.g. `genesis.md` vs `GENESIS.md`).
Files you forgot to `git add` exist locally but not on GitHub, so they fail too. CI runs both local and `--remote`, without `--strict`.

## Local LLM container (not connected)

`containers/llama.py` and `containers/llama.compose.yml` restore `NagoyAction/containers/`, which was removed in #48.
They use the official llama.cpp server image (digest-pinned) and a model verified by SHA-256, listening only on 127.0.0.1.
They are not called from the current `pipelines/inbox.toml` or `inbox/inbox.py` (local LLM integration was left out of the first rollout to main).
Tests are in `tests/test_llama_container.py` (no network).

## Tests

For the independent `localci.py` self-tests only, an [optional locked pytest-only environment](docs/nano-localci-tests.md) avoids installing Aoi research dependencies. It does not replace the complete Aoi-integrated suite below.

Steps and tests use Aoi's top level (`cycles/`, `queryu/`, `sakanalytics/`, `blueprobe/`, `vendor/`, `scripts/`, `docs/`) by relative path. They are not tested standalone. On every run CI resolves main's SHA with `git ls-remote https://github.com/myon-bioinformatics/Aoi refs/heads/main`, checks it out, replaces its `nagoyaction/` with this repository's tree, and runs `nagoyaction/tests` with Aoi's settings. The resolved SHA is left in the job summary. A ref can be given via `aoi_ref` in `workflow_dispatch`. With the same SHA, the bytes of `vendor/aoi/` are checked against Aoi's originals. A mismatch is a warning on pull requests and a failure on push to main and on schedule.

```sh
git clone https://github.com/myon-bioinformatics/Aoi.git ../Aoi
git -C ../Aoi checkout main
rm -rf ../Aoi/nagoyaction && mkdir ../Aoi/nagoyaction && git archive HEAD | tar -x -C ../Aoi/nagoyaction
git -C ../Aoi add -A nagoyaction
cd ../Aoi && uv run --locked pytest -q -c pyproject.toml nagoyaction/tests
```

CI does the same on Python 3.11–3.15. Python is provisioned with `astral-sh/setup-uv` (not `actions/setup-python`); fixed lanes run on 3.15, the matrix keeps the compatibility range.

The existing real/minimal Polars comparison job uses a [smaller locked environment](docs/polars-min-ci-environment.md), while retaining the real baseline and byte-comparison gates. The full matrix above is unchanged.

## Relationship with Aoi

A repository split out from [Aoi](https://github.com/myon-bioinformatics/Aoi)'s [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction). Its direct parent is Aoi, and differences from `nagoyaction/` are checked on the Aoi side.
The first 49 commits are `nagoyaction/` from Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd`, split out with its history using `git filter-branch --subdirectory-filter nagoyaction` (head `b35707b877a92fd088db06f15b87d0e72158fc27`, tree `1537879773093a5350a17ca657fbdf89f6a57e72`).
It is registered in Aoi's [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json) (the full procedure is in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md)).

- `min.py` is not kept here (Aoi provides it)
- Syncing with Aoi: Aoi does `git subtree add` once to connect the histories, and after that syncs via subtree. `vendor-consumers.json` is not used for subtree matching. Only the stdlib-shrink tools NagoyAction uses (`scripts/shrink_module.py`, `scripts/shrink_polars.py`, `shrink/polars_min.py`) are placed byte-identical in `vendor/aoi/` and pinned in `shared-tools.lock.json` (`vendor-lock/1` path, sha256, source). numpy and `fetch_module` are not used here
- `nagoyaction/…` and `cycles/…` in this README's command examples refer to locations seen from Aoi's root (links to documents inside Aoi are written as GitHub URLs)

## Related subprojects

Each subproject of the parent [Aoi](https://github.com/myon-bioinformatics/Aoi) is its own repository. They are listed with their location in Aoi (subtree). The list and registration details are in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md).

| Repository | Location in Aoi | Role |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | Observation and extraction (reads saved HTML/CSS/DOM and records what is there) |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | Fetching and building observation datasets (caches with provenance) |
| [SakAnalytics](https://github.com/myon-bioinformatics/SakAnalytics) | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | Metrics and statistics from observation data (team × season metrics, outlook for remaining games) |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | Verifying explanations (propositions, counterexamples, objections) |
| **NagoyAction** (this repository) | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | Pipeline execution and automation (the same definition locally and on GitHub Actions) |
| [DRAgoWing](https://github.com/myon-bioinformatics/DRAgoWing) | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | Figures and reports (Plotly.js HTML, the four-forms table) |

## License

MIT License ([LICENSE](LICENSE)). Same contents as Aoi's `LICENSE`.

---

# Usage in Aoi's research cycle (Chunichi / NPB)

An example of running the c001 (Chunichi) pipeline from Aoi's root.

```bash
python nagoyaction/nagoyaction.py doctor cycles/c001-chunichi/pipeline.toml            # pre-run check
python nagoyaction/nagoyaction.py show   cycles/c001-chunichi/pipeline.toml            # show structure
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml            # run
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --offline  # don't fetch
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --dry-run  # only show what would be done
```

## Node entry (Node 26+)

`node vendor/py_launch.cjs --env-var NAGOYACTION_PYTHON -- nagoyaction.py <args>` runs `nagoyaction.py`
through the vendored shared launcher `vendor/py_launch.cjs` (there is no per-tool `.cjs` wrapper), taken byte-identical from Aoi's `vendor/py_launch.cjs` (parent → Aoi → NagoyAction; no generation is skipped) together with Aoi's `LICENSE` as `vendor/aoi-LICENSE`, both pinned to one Aoi main merge commit in `vendor.lock.json`. The shared uv tool builder `vendor/uv_tool_build.py` is taken the same way from Aoi and pinned separately in that lock. Arguments, stdin/stdout/stderr and the
exit code are passed through unchanged; Python runs with `-S`, including interpreter discovery.
`NAGOYACTION_PYTHON` picks the interpreter (via `--env-var`). The launcher forwards repeated SIGINT/SIGTERM
until the Python child exits. Launcher failures (no Python 3.9+, spawn error, signal) exit 2, as does a Node older than 26;
set `PY_LAUNCH_ERROR_FORMAT=json` for a structured launcher error on stderr (independent of
the tool's `--json` flag).

The launcher and license are pinned to Aoi's accepting main merge commit
[`827387a`](https://github.com/myon-bioinformatics/Aoi/commit/9e0147a17695ce63fa73daf75d8195a4f49095bb),
not to the root repository or an unmerged PR head. The builder is pinned to Aoi's later main
first-parent commit
[`3d8dcc70`](https://github.com/myon-bioinformatics/Aoi/commit/3d8dcc70a9c4e6c4f4b7de05868f54acd3901ce7)
(#181, which vendors parent #251 including `--module`). `shared-tools.lock.json` remains the separate
lock for the polars shrink tools under `vendor/aoi/`.

The launcher's CLI is `node vendor/py_launch.cjs [--env-var NAME] [--site] [--] SCRIPT.py [ARGS...]`.
It defaults to `-S`; `--site` explicitly enables site-packages, which this tool does not need.
