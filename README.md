# NagoyAction

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

GitHub Actions workflows only call this command (e.g. `.github/workflows/cycle-c001.yml`).
Org-wide reusable workflows (actionlint, etc.) come from `myon-bioinformatics/myon-bioinformatics`.
To bring in shared modules from other repositories, use that repository's `vendor_sync.py` (SHA-pinned).

## Layout

| File | Contents |
|---|---|
| `nagoyaction.py` | Pipeline pre-checks (`doctor`), structure display (`show`), and execution (`run`) |
| `localci.py` | Workflow checks repeated locally (actionlint, resolving referenced SHAs, `uses:` pins). "Local CI" below |
| `pipelines/` | Pipeline definitions (`research.toml`, `inbox.toml`) |
| `linkcheck.py` | Checks Markdown link and image targets ("Link checking" below) |
| `inbox/inbox.py`, `docs/inbox.md` | Question intake |
| `research_digest.py`, `docs/research-digest.md` | Index of research records (R*.md) and proposition judgements (no network or LLM needed) |
| `publication_gate.py`, `ghi_execution.py`, `PUBLICATION.md` | Pre-publication evidence checks (offline) and matching against running GitHub Actions |
| `annual_history_report.py` | Lists annual audit results and synthetic model verification results side by side, kept separate |
| `containers/` | Local LLM container (not connected. "Local LLM container" below) |
| `tests/` | pytest (run inside Aoi. "Tests" below) |

## Local CI (`localci.py`)

Checks workflows and tests locally without waiting for GitHub Actions to finish.

`python localci.py run` checks `.github/workflows` with actionlint. If shellcheck is on PATH, actionlint also uses it for `run:` blocks. actionlint resolves the latest rhysd/actionlint release on every run and verifies the published checksums and GitHub's digest. The version is not pinned in source. The resolved tag, asset name, and verified sha256 are left in the output and `.localci/refs.env`, and written next to the resolved referenced SHAs if `GITHUB_STEP_SUMMARY` exists. On GitHub Actions it stops if fetching or verification fails and does not fall back to Go. Locally, only when the tag could be resolved, it falls back to `go run github.com/rhysd/actionlint/cmd/actionlint@<tag>`. At the same time it resolves the main SHA of referenced repositories with `git ls-remote` plus a GitHub API repository id check, and writes them to `.localci/refs.env`. Whether `uses:` pins match the commit of each action's latest release tag is only reported by default. Setup actions (`actions/setup-python`, `actions/setup-node`, `astral-sh/setup-uv`) use the release's 40-character SHA and `# vX.Y.Z`. Other `actions/*` use the moving major tag `vN`.

```bash
python localci.py run                         # one pass over all of Aoi's tests/ (one shard)
python localci.py run --repeat 10             # one pass over all of it split into 10 rounds
python localci.py run --repeat 10 --seed 7    # reproduce the same split and input substitutions
python localci.py run --repeat 10 --keep-going
python localci.py run --self-tests            # only tests/test_localci.py (no Aoi)
python localci.py run --strict                # fail on stale SHA pins; vN for non-setup actions/* is allowed
python localci.py resolve                     # only resolve SHAs; CI's resolve job uses this too
```

`--repeat N` does not trace the same checks N times. It shuffles the check list (resolving references, actionlint, each `uses:`, the pytest tests) by seed and splits it into N nearly equal shards. Each round runs only one shard, and once all rounds finish every check has run exactly once. It stops at a failing round and prints the round number, shard contents, and seed. `--keep-going` continues. After each round it prints the number of rounds passed and completed against N. Getting deep without failures is a confidence signal that the remaining shards will pass too.

Checks that pass with fixed values are switched to other values from that round's seed with `substitute(name, value, draw)`. In pytest, `-p localci_pytest` does the same via monkeypatch. Rounds can also be chosen with the plugin alone.

```bash
pytest -p localci_pytest --localci-repeat 10 --localci-round 3 --localci-seed 7
```

The references resolved are Aoi, `myon-bioinformatics/myon-bioinformatics`, the vendored `markdown` and `web-ui`, and the repositories listed in the repository root's `vendor.lock.json`. SHAs are not written in source. The GitHub Actions resolve job calls `python localci.py resolve --github-output` and passes the job output `sha` (Aoi) to checkout. Reusable workflow `uses:` can't be expressions, so they stay as pins in the file and localci compares them with the latest release.

The pytest suite checks out the Aoi SHA resolved at run time into `.localci/aoi` and collects from there. After confirming HEAD is that SHA, it overlays this repository's tree on `nagoyaction/` and splits all of `tests/` into `--repeat` shards. Each shard's pytest runs in one process. When uv is missing, or to run only this repository's checks without fetching Aoi, use `--self-tests` (only `tests/test_localci.py`). `--pytest PATH` also doesn't check out Aoi. CI's local-ci job uses `--repeat 10 --strict`, uses `github.run_id` as the seed, and prints `localci seed=` at start. `--strict` fails stale SHA pins and `uses:` of setup actions or reusable workflows that are not SHAs. Major tags `vN` of non-setup `actions/*` such as checkout, upload-artifact, download-artifact, and cache are not failed.

```bash
python localci.py run --self-tests
python localci.py run --pytest tests/test_localci.py
```

## Link checking (`linkcheck.py`)

```bash
python nagoyaction/linkcheck.py --help                                 # all flags and exit codes
python nagoyaction/linkcheck.py --root .                               # before push: match against git-tracked files, case-sensitive
python nagoyaction/linkcheck.py --remote OWNER/REPO --ref BRANCH       # after push: exists on that branch? (gh api)
python nagoyaction/linkcheck.py --external                             # also check http(s) (only 404/410 fail)
python nagoyaction/linkcheck.py --external --strict                    # unverified also fails (exit code 3)
python nagoyaction/linkcheck.py --json                                 # stdout is nagoyaction-linkcheck/1
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

Steps and tests use Aoi's top level (`cycles/`, `queryu/`, `sakanalytics/`, `blueprobe/`, `vendor/`, `scripts/`, `docs/`) by relative path. They are not tested standalone. On every run CI resolves main's SHA with `git ls-remote https://github.com/myon-bioinformatics/Aoi refs/heads/main`, checks it out, replaces its `nagoyaction/` with this repository's tree, and runs `nagoyaction/tests` with Aoi's settings. The resolved SHA is left in the job summary. A ref can be given via `aoi_ref` in `workflow_dispatch`. With the same SHA, the bytes of `vendor/aoi/` are checked against Aoi's originals. A mismatch is a warning on pull requests and a failure on push to main and on schedule.

```sh
git clone https://github.com/myon-bioinformatics/Aoi.git ../Aoi
git -C ../Aoi checkout main
rm -rf ../Aoi/nagoyaction && mkdir ../Aoi/nagoyaction && git archive HEAD | tar -x -C ../Aoi/nagoyaction
git -C ../Aoi add -A nagoyaction
cd ../Aoi && uv run --locked pytest -q -c pyproject.toml nagoyaction/tests
```

CI does the same on Python 3.11–3.15.

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
