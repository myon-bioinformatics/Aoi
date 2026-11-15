# DRAgoWing

<p align="center">
  <img src="docs/brand/icon.png" alt="DRAgoWing icon" width="160" />
</p>

[Icon](docs/brand/icon.png) · [Favicon](docs/brand/favicon.png)

> Lay down the record without re-judging it.
>
> Renders baseball research records as Plotly.js HTML reports, proposition tables and optional headless-Chromium PNG/SVG exports without Python plotting libraries. Split out from Aoi's dragowing/ (git subtree).

![DRAgoWing](https://github.com/myon-bioinformatics/Aoi/raw/main/docs/images/dragowing.webp)

*Concept image (a figure for sharing the idea; not the actual data or HTML structure)*

## Role in Aoi

**Visualization and reports.**

| Challenges | Approach | Outcomes & value |
|---|---|---|
| Records are scattered and hard to reproduce | 1. Read the records | Easy-to-read reports |
| Aggregated information is hard to summarize | 2. Render them as figures and tables | Sharing through HTML |
| Reports need continuous updating | 3. Convert them to HTML | Continuous report generation |

Topics: reports, HTML, visualization

## Overview

Turns recorded results (`season.jsonl` and `propositions.jsonl`) into figures and tables without redoing the judgment. No fitting, smoothing, or rounding into bins.

The text table of the four forms is in [docs/forms.md](docs/forms.md). HTML (trajectories, team × year, condition overlap, list of propositions) is in [docs/figures.md](docs/figures.md). The concept figure is [docs/images/dragowing.webp](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/images/dragowing.webp).

It produces `index.html` and `propositions.html` in `--out` (a new temporary directory when omitted; the printed links open them). The trajectories, team × year, and condition overlap (grid and breakdown) in `index.html` are drawn from Plotly JSON specs with the browser's plotly.js (the latest dist on jsDelivr). The Python `plotly` package is not used. `propositions.html` is a list and Markdown tables, without Plotly. Add `--embed` to embed Plotly.js into `index.html`. Page text is converted from Markdown to HTML.

PNG / SVG are optional. With `--png` or `--svg`, they are exported via Chromium by default. Install `chromium` / `chromium-browser` or set `CHROMIUM` to its executable. Explicit Chrome overrides remain supported; automatic selection does not fall back to Chrome. See [browser selection and compatibility](docs/export.md).

This repository was split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) (see "Relationship with Aoi" below).

## Installation and usage

### Standalone HTML inspection

`dragowing.py` is a standalone standard-library tool for counting elements in any saved UTF-8 HTML document; it does not render reports or replace the full DRAgoWing application.

```bash
python dragowing.py page.html --tag p --tag img
cat page.html | python dragowing.py --tag p
python vendor/aoi/vendor/uv_tool_build.py dragowing.py --out build/dragowing-tool
uv tool install ./build/dragowing-tool
dragowing page.html --tag p
```

The tool project contains only `dragowing.py` and build metadata, and its runtime has no external Python dependencies. The repository's existing rendering entry and its dependencies remain separate. Rebuild the tool project after changing `dragowing.py`.

For example, after installing the tool:

```bash
printf '<p>one</p><p>two</p><img src="x">' | dragowing
# {"img": 1, "p": 2}
printf '<p>one</p><p>two</p><img src="x">' | dragowing --tag p
# {"p": 2}
dragowing missing.html  # reports a read error; exit 1
```

Without installation, replace `dragowing` with `python dragowing.py`. This counts opening tags in saved HTML; to render reports or export figures, use the full DRAgoWing application below.

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). Runtime dependencies are polars, numpy, and markdown. Figures use the browser's plotly.js; neither matplotlib nor Python plotly is installed. HTTP uses only the standard library's urllib (no httpx).

```bash
git clone https://github.com/myon-bioinformatics/DRAgoWing.git
cd DRAgoWing
uv sync
```

```bash
python -m dragowing RESULTS [--out DIR] [--id ID ...] [--column COLUMN] [--cond col,op,VALUE ...] [--breakdown COLUMN] [--breakdown-keep VALUE ...] [--png] [--svg] [--embed]
```

- `RESULTS` is a directory containing `season.jsonl` and `propositions.jsonl`. Without `--out`, HTML goes to a new temporary directory. Each written file is printed as a `file://` link with its size (📄), after the Markdown version (📦). `--id` narrows propositions, and `--column` chooses the numeric column for team × year (default `wins_vs_pythag`).
- Repeat `--cond` to display 2–8 sets including class B. `--breakdown` selects the breakdown column (default `team`); repeat `--breakdown-keep` to keep values separate from “Other”. See [docs/figures.md](docs/figures.md).
- Condition overlap (`overlap.py`) uses `propositions` and `rule_search` from [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras), and the four-forms table (`forms.py`) uses `ask` (registration status) from [QueRyu](https://github.com/myon-bioinformatics/QueRyu). DRAgoWing does not look for them: the caller puts them on the import path, and in Aoi that is `aoi.py` (`python aoi.py dragowing/__main__.py RESULTS`, `import aoi`, or `eval "$(python aoi.py)"` for one shell). When one is missing, the error names `aoi.py`.
- This directory is the contents of the `dragowing` package, so run `python -m dragowing` from a parent where the directory appears as `dragowing` (see the example under "Tests"), or run the file directly: `python aoi.py dragowing/__main__.py RESULTS` inside Aoi, or `eval "$(python /path/to/Aoi/aoi.py)"` and then `python /path/to/dragowing/__main__.py RESULTS` for a standalone checkout (`__main__.py` registers its directory as the `dragowing` package). `python aoi.py -m dragowing` is not the report: Aoi's import path includes this directory, so `dragowing` there is `dragowing.py`.

## Optional HTML-only environment

[Prepare the pinned HTML-only environment](docs/nano-environment.md) with the
shared parent exporter. It keeps the existing stdlib overlap path and real
Markdown dependency; native/image-export modes and the full test environment
remain separate and unchanged.

## Making only the overlap computation lightweight

`load_overlap(path, conds, backend="stdlib")` selects a limited path that does not load NumPy or Polars.
The CLI uses it by default, so its supported scalar inputs need only the standard library and Python-Markdown.
Use `--overlap-backend native` explicitly for the broader native input domain (NumPy/Polars required).
The legacy `--results DIR` spelling and `--overlap-backend stdlib` remain accepted.
Do not supply both `RESULTS` and `--results`. With no explicit backend, positional `RESULTS` selects stdlib, while legacy `--results DIR` retains native. An explicit `--overlap-backend` overrides either default.
`native` remains the `load_overlap` API default (NumPy, Polars and PythDRagoras's `rule_search`); the API is unchanged.
Supported input, limitations, and comparison measurements are in [docs/overlap-stdlib.md](docs/overlap-stdlib.md).
Markdown for HTML, Chromium for image export, and so on are still needed.

## Layout

| File | Contents | ➡️ Planned place |
|---|---|---|
| `dragowing.py` | The single file (stdlib only): counts HTML elements without a browser (`python dragowing.py PAGE`, `count_elements()`) | stays at the top, and takes in the generic stdlib parts below |
| `plotly_cdn.py` | Plotly.js (jsDelivr) | into `dragowing.py` |
| `chrome_pipe.py`, `render.py`, `export.py` | Optional PNG / SVG export with headless Chromium ([docs/export.md](docs/export.md)) | into `dragowing.py` |
| `records.py` | Reads the results directory's JSONL in record order | into `dragowing.py` |
| `venn.py`, `_overlap_stdlib.py` | Condition-overlap grids for 2–8 sets in Gray-code order and per-region stacked bars (`venn_figures`); the stdlib row evaluation behind `load_overlap(..., backend="stdlib")` | `core/` |
| `cli.py`, `__main__.py` | `python -m dragowing RESULTS [--out DIR]` | `cli.py` → `npb/`; `__main__.py` stays (package entry) |
| `figures.py` | Plotly figure JSON (data / layout) of recorded values (trajectories, team × year) | `npb/` |
| `htmlout.py` | HTML. Text and tables are built from Markdown (Plotly for trajectories, team × year, and condition overlap) | `npb/` |
| `forms.py` | 2×2 of the four forms and logic notation for conditions ([docs/forms.md](docs/forms.md)); uses QueRyu's `ask` | `npb/` |
| `overlap.py` | Overlap of condition sets and the B class (masks are rule_search bit matrices); uses PythDRagoras | `npb/` |
| `research_report.py`, `reports/` | Research summary figures and Markdown report rendering (called from Aoi's workflow) | `npb/` |
| `docs/`, `vendor/aoi/`, `vendor.lock.json`, `tests/` | Docs; the Aoi shared tools (`fetch_module.py`, `numpy_min.py`); pytest | as is |

➡️ The moves happen when DRAgoWing is next synced into Aoi, together with Aoi's side. Aoi names these modules by package path in more than 60 places (`dragowing.overlap`, `dragowing.research_report`, `dragowing.export`, `dragowing.records`, `dragowing.plotly_cdn`, `from dragowing import chrome_pipe, render` in workflows, scripts, tests, `distributions/entries/dragowing_api.py` and provenance records), so moving them here first would break Aoi's CI. Relative imports inside the package (`from .forms import …`) change with them.

## Tests

Cycle data (outputs in `cycles/`), [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) (`propositions` and `rule_search`), and [QueRyu](https://github.com/myon-bioinformatics/QueRyu) (`ask`) stay in Aoi. They are not copied; Aoi's main is checked out and passed in.

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout main   # CI resolves main's SHA at run time and checks it out
AOI_ROOT=$PWD/.test-deps/aoi uv run --locked pytest -q --junitxml=reports/junit.xml
```

- DRAgoWing does not know Aoi's layout. It takes the results directory and (if needed) `--team-order` explicitly. Tests use `aoi_paths.py` from the Aoi at `AOI_ROOT` to locate data.
- If `AOI_ROOT` does not point to Aoi (no `cycles/`), pytest stops first and prints the reason.
- This directory is the contents of the `dragowing` package (no `__init__.py`; `export.py` and `cli.py` use relative imports like `from .plotly_cdn`). Tests use `from dragowing.xxx` and `python -m dragowing`. pytest's `pythonpath` is `["."]`, and the top-level `conftest.py` registers this directory as `sys.modules["dragowing"]` (with `__path__` set to this directory) only when `dragowing` cannot yet be imported from the same directory. In Aoi the parent is on pythonpath and the same directory is already `dragowing`, so this registration does nothing.
- To run the CLI outside pytest, run Aoi's `aoi.py` first (it exports `AOI_ROOT` and the import paths for this shell only), then `__main__.py`. `__main__.py` registers its directory as the `dragowing` package whatever the checkout is named.

```bash
eval "$(python .test-deps/aoi/aoi.py)"
uv run --locked python __main__.py "$AOI_ROOT/cycles/c001-chunichi/outputs"
```

- In addition, the tests use the following from the Aoi at `AOI_ROOT`:
  - Output in `cycles/` (`cycles/c001-chunichi/outputs`).
  - `aoi.py`: `conftest.py` appends the import paths it gives (`aoi.environment()`, the same list as Aoi's pytest `pythonpath`) after this repository, so PythDRagoras's `propositions` / `rule_search` and QueRyu's `ask` import by name. DRAgoWing names neither directory.
  - `tests/test_no_sibling_imports.py` checks that no other Aoi sibling subprojects or `scripts/` are used (imports of `propositions`, `rule_search` and `ask` in the tests are known exceptions).
- `reports/build_reports.py` is an Aoi-side tool (Aoi's DRAgoWing reports workflow checks out `myon-bioinformatics/markdown` and calls it). This repository's CI does not run that workflow.
- The Python matrix explicitly selects Chromium and requires real-browser tests. Missing Chromium fails CI rather than silently falling back to Chrome or skipping. Locally, real-browser tests remain optional unless `DRAGOWING_REQUIRE_CHROME=1` is set.

CI (`.github/workflows/ci.yml`) runs pytest on Python 3.11–3.15. Python is provisioned with `astral-sh/setup-uv`; the fixed lanes (`vendor-lock`, `vendor-dispatch`) run on 3.15 and the matrix keeps the compatibility range. `vendor.lock.json` (`vendor-lock/1`) records repository, ref, commit, source, destination, blob_sha, and sha256, and the copies are in `vendor/aoi/`. CI resolves Aoi's main with `git ls-remote` (overridable with `workflow_dispatch`'s `aoi-ref`), checks repository id `1402862784`, and then compares the copies. A mismatch is a warning on pull requests and a failure on pushes to main and on schedule. In parallel, it resolves the main of the parent myon-bioinformatics/myon-bioinformatics with `git ls-remote` (repository id `638801160`) and verifies that SHA's `pilot/vendor_dispatch.py` against `vendor.lock.json`. `--record` is not passed. Skips are recorded, and it fails if the recorded commit's digest differs.

## Relationship with Aoi

This repository was split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing).
Its parent is Aoi (Aoi's parent is [myon-bioinformatics](https://github.com/myon-bioinformatics/myon-bioinformatics)). It is registered in Aoi's [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json), and its tree is the same as Aoi's `dragowing/` at the time of registration (including `.github/`, `pyproject.toml`, `uv.lock`, `conftest.py`, `.gitignore`, `LICENSE`, and this README). It is synced with `git subtree` (see "Syncing with Aoi" below; the full procedure is in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md)).
This README starts from the same file as Aoi's `dragowing/README.md`. Links to documents and data inside Aoi are written as GitHub URLs so they open from either place.

### Syncing with Aoi

This repository is a subtree of Aoi's `dragowing/`. No files are excluded, and the tree of Aoi's `dragowing/` is the same as this repository's tree. Inside Aoi, `dragowing/.github/` does not run (GitHub reads only the repository's top-level `.github/`), and `dragowing/conftest.py` checks `AOI_ROOT` in Aoi's pytest the same way and does no package registration.

- History was split out, preserving history, from `dragowing/` at Aoi `a8dc4997f43236b24a23df56e21f143fa0e233d8` (main) (main `c789da2e30b33144f3110506f90f91ea579b9a6b`; the tree at split time, `70424b5a2768f43633766435cc9552f77c1b2ba7`, is the same as Aoi's `dragowing/`).
- This history is not connected to Aoi's history, so a join is added to Aoi once. A squash commit with this repository's main commit in `git-subtree-split:` (tree the same as this repository) becomes the second parent of a merge that does not change Aoi's tree. After the join, `git subtree` uses it as the starting point.
- The join must remain as the second parent. Aoi PRs containing the join are merged with a merge commit, not squashed (squashing drops the second parent, and `git subtree pull` and `split` stop working).
- The `git-subtree-split:` commit must be on this repository's main. Merge this repository's PRs with a merge commit too, not squash (squashing changes main's sha, so the sha written in `git-subtree-split:` doesn't stay on main).

Child → Aoi (on a branch created from Aoi's main):

```bash
git subtree pull --prefix=dragowing https://github.com/myon-bioinformatics/DRAgoWing.git main --squash
test "$(git rev-parse HEAD:dragowing)" = "$(git rev-parse FETCH_HEAD^{tree})"   # when Aoi has no unsynced changes
```

Aoi → child (on Aoi's main):

```bash
git fetch https://github.com/myon-bioinformatics/DRAgoWing.git main   # have the split's starting commit locally
git subtree split --prefix=dragowing -b sync/dragowing
test "$(git rev-parse sync/dragowing^{tree})" = "$(git rev-parse HEAD:dragowing)"
git push https://github.com/myon-bioinformatics/DRAgoWing.git sync/dragowing:refs/heads/<new-branch>
```

- Open a PR in this repository from the pushed branch. After merging, do the "Child → Aoi" pull in Aoi to re-anchor Aoi's starting point to this repository's main (a squash merge would not keep the split commit on main).
- Aoi's `scripts/check_child_heads.py --fail-on-diff` compares the tree of the sha registered in Aoi's `child-heads.json` with Aoi's `dragowing/`.

## Related subprojects

Each subproject of the parent [Aoi](https://github.com/myon-bioinformatics/Aoi) is its own repository. They are listed with their location in Aoi (subtree). The list and registration details are in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md).

| Repository | Location in Aoi | Role |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | Observation and extraction (reads saved HTML/CSS/DOM and records what is there) |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | Fetching and building observation datasets (caches with provenance) |
| [SakAnalytics](https://github.com/myon-bioinformatics/SakAnalytics) | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | Metrics and statistics from observation data (team × season metrics, outlook for remaining games) |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | Verifying explanations (propositions, counterexamples, objections) |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | Pipeline execution and automation (the same definition locally and on GitHub Actions) |
| **DRAgoWing** (this repository) | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | Figures and reports (Plotly.js HTML, the four-forms table) |

## License

MIT License ([LICENSE](LICENSE)). `LICENSE` has the same contents as the MIT LICENSE at Aoi's root (blob `4ec4989b801bf1a3df6184d21f79e6e7ed5931f6`, 1061 bytes; Copyright (c) 2026 myon).

---

# Using it in Aoi's research cycle (Chunichi, NPB)

An example of building HTML from the c001 (Chunichi) output at Aoi's root.

```bash
python DRAgoWing.py cycles/c001-chunichi/outputs \
  --team-order d,g,s,db,t,c,h,f,b,e,l,m   # order is Aoi's setting (TEAM_ORDER in aoi_npb.py)
```

## Connecting with the existing Markdown implementation

The [DRAgoWing reports workflow](https://github.com/myon-bioinformatics/Aoi/blob/main/.github/workflows/dragowing.yml) checks out the latest main of `myon-bioinformatics/markdown` once on PRs, main updates, and manual runs, then renders research documents with `dragowing/reports/build_reports.py`. The docs-only skip for regular pytest is kept, and report generation runs even for docs-only changes.

Local example (point the output at an empty directory):

```sh
git clone https://github.com/myon-bioinformatics/markdown.git .deps/markdown
python -S dragowing/reports/build_reports.py --markdown-root .deps/markdown --output build/dragowing --previous-ref HEAD~1
```

## Focused test discovery

See [standard-library discovery commands](docs/unittest-discovery.md) for
validated `python -S -m unittest discover` recipes, filename/name filtering,
and the boundary with the full pytest suite.
