# DRAgoWing

<p align="center">
  <img src="docs/brand/icon.png" alt="DRAgoWing icon" width="160" />
</p>

[Icon](docs/brand/icon.png) · [Favicon](docs/brand/favicon.png)

> Lay down the record without re-judging it.
>
> Renders baseball research records as Plotly.js HTML reports, proposition tables and optional headless-Chrome PNG/SVG exports without Python plotting libraries. Split out from Aoi's dragowing/ (git subtree).

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

It produces `build/dragowing/index.html` and `propositions.html`. The trajectories and team × year in `index.html` are drawn from Plotly JSON specs with the browser's plotly.js (the latest dist on jsDelivr). The Python `plotly` package is not used. `propositions.html` is a list and Markdown tables, without Plotly. Add `--embed` to embed Plotly.js into `index.html`. Page text is converted from Markdown to HTML.

PNG / SVG are optional. With `--png` or `--svg`, they are exported via Chrome. Without Chrome, only HTML is produced, and the tests look only at that.

This repository was split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) (see "Relationship with Aoi" below).

## Installation and usage

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). Runtime dependencies are polars, numpy, and markdown. Figures use the browser's plotly.js; neither matplotlib nor Python plotly is installed. HTTP uses only the standard library's urllib (no httpx).

```bash
git clone https://github.com/myon-bioinformatics/DRAgoWing.git
cd DRAgoWing
uv sync
```

```bash
python -m dragowing --results <DIR> --out build/dragowing [--id ID ...] [--column COLUMN] [--cond col,op,VALUE] [--png] [--svg] [--embed]
```

- `--results` is a directory containing `season.jsonl` and `propositions.jsonl`. `--id` narrows propositions, and `--column` chooses the numeric column for team × year (default `wins_vs_pythag`).
- Condition overlap (`overlap.py`) uses `propositions` and `rule_search` from [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras), and the four-forms table (`forms.py`) uses `ask` (registration status) from [QueRyu](https://github.com/myon-bioinformatics/QueRyu). Put them on `PYTHONPATH` to run (same as "Tests" below).
- This directory is the contents of the `dragowing` package, so run `python -m dragowing` from a parent where the directory appears as `dragowing` (see the example under "Tests").

## Making only the overlap computation lightweight

`load_overlap(path, conds, backend="stdlib")` or `--overlap-backend stdlib` selects
a limited path that does not load NumPy or Polars. The default is the existing `native`.
Supported input, limitations, and comparison measurements are in [docs/overlap-stdlib.md](docs/overlap-stdlib.md).
Markdown for HTML, Chrome for image export, and so on are still needed.

## Layout

| File | Contents |
|---|---|
| `cli.py`, `__main__.py` | `python -m dragowing --results DIR --out DIR` |
| `records.py` | Reads the results directory's JSONL in record order |
| `figures.py` | Plotly figure JSON (data / layout) of recorded values |
| `htmlout.py` | HTML. Text and tables are built from Markdown (Plotly only for trajectories and team × year) |
| `forms.py` | 2×2 of the four forms and logic notation for conditions ([docs/forms.md](docs/forms.md)) |
| `overlap.py` | Overlap of condition sets and the B class (masks are rule_search bit matrices) |
| `plotly_cdn.py` | Plotly.js (jsDelivr) |
| `chrome_pipe.py`, `render.py`, `export.py` | Optional PNG / SVG export with headless Chrome ([docs/export.md](docs/export.md)) |
| `html_tag_count.py` | Counts HTML elements without a browser |
| `research_report.py`, `reports/` | Research summary figures and Markdown report rendering (called from Aoi's workflow) |
| `docs/` | `forms.md`, `figures.md`, `export.md` |
| `vendor/aoi/`, `vendor.lock.json` | The Aoi shared tools this repository uses: `fetch_module.py` and `numpy_min.py` |
| `tests/` | pytest |

## Tests

Cycle data (outputs in `cycles/`), [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) (`propositions` and `rule_search`), and [QueRyu](https://github.com/myon-bioinformatics/QueRyu) (`ask`) stay in Aoi. They are not copied; Aoi's main is checked out and passed in.

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout main   # CI resolves main's SHA at run time and checks it out
AOI_ROOT=$PWD/.test-deps/aoi \
  PYTHONPATH=$PWD/.test-deps/aoi/pythdragoras:$PWD/.test-deps/aoi/queryu/ask \
  uv run --locked pytest -q --junitxml=reports/junit.xml
```

- DRAgoWing does not know Aoi's layout. It takes `--results` and (if needed) `--team-order` explicitly. Tests use `aoi_paths.py` from the Aoi at `AOI_ROOT` to locate data.
- If `AOI_ROOT` does not point to Aoi (no `cycles/`), pytest stops first and prints the reason.
- This directory is the contents of the `dragowing` package (no `__init__.py`; `export.py` and `cli.py` use relative imports like `from .plotly_cdn`). Tests use `from dragowing.xxx` and `python -m dragowing`. pytest's `pythonpath` is `["."]`, and the top-level `conftest.py` registers this directory as `sys.modules["dragowing"]` (with `__path__` set to this directory) only when `dragowing` cannot yet be imported from the same directory. In Aoi the parent is on pythonpath and the same directory is already `dragowing`, so this registration does nothing.
- To run `python -m dragowing` outside pytest, run it from the parent if the directory is named `dragowing`.

```bash
# From inside the repository, when the checkout directory is named dragowing (same for dragowing/ inside Aoi)
cd ..
AOI_ROOT=$PWD/dragowing/.test-deps/aoi \
  PYTHONPATH=$PWD/dragowing/.test-deps/aoi/pythdragoras:$PWD/dragowing/.test-deps/aoi/queryu/ask \
  uv run --project dragowing --locked python -m dragowing \
  --results "$PWD/dragowing/.test-deps/aoi/cycles/c001-chunichi/outputs" --out dragowing/build/dragowing
```

When the directory is not named `dragowing` (for example, when this repository is cloned as `DRAgoWing`), expose it to a parent under the name `dragowing`.

```bash
mkdir -p /tmp/dragowing-run
ln -sfn "$PWD" /tmp/dragowing-run/dragowing
AOI_ROOT=$PWD/.test-deps/aoi \
  PYTHONPATH="/tmp/dragowing-run:$PWD/.test-deps/aoi/pythdragoras:$PWD/.test-deps/aoi/queryu/ask" \
  uv run --locked python -m dragowing \
  --results "$PWD/.test-deps/aoi/cycles/c001-chunichi/outputs" --out build/dragowing
```

- In addition, the tests use the following from the Aoi at `AOI_ROOT`:
  - Output in `cycles/` (`cycles/c001-chunichi/outputs`).
  - PythDRagoras's `propositions` and `rule_search` (`pythdragoras` on `PYTHONPATH`; `overlap.py` reaches into `pythdragoras`).
  - QueRyu's `ask` (`queryu/ask` on `PYTHONPATH`; `forms.py` reaches into `queryu`).
  - `tests/test_no_sibling_imports.py` checks that no other Aoi sibling subprojects or `scripts/` are used (`propositions`, `rule_search`, `ask`, plus the `queryu` and `pythdragoras` paths, are known exceptions).
- `reports/build_reports.py` is an Aoi-side tool (Aoi's DRAgoWing reports workflow checks out `myon-bioinformatics/markdown` and calls it). This repository's CI does not run that workflow.
- There is no Chrome job. Without Chrome, tests that use Chrome are skipped.

CI (`.github/workflows/ci.yml`) runs pytest on Python 3.11–3.15. `vendor.lock.json` (`vendor-lock/1`) records repository, ref, commit, source, destination, blob_sha, and sha256, and the copies are in `vendor/aoi/`. CI resolves Aoi's main with `git ls-remote` (overridable with `workflow_dispatch`'s `aoi-ref`), checks repository id `1402862784`, and then compares the copies. A mismatch is a warning on pull requests and a failure on pushes to main and on schedule. In parallel, it resolves the main of the parent myon-bioinformatics/myon-bioinformatics with `git ls-remote` (repository id `638801160`) and verifies that SHA's `pilot/vendor_dispatch.py` against `vendor.lock.json`. `--record` is not passed. Skips are recorded, and it fails if the recorded commit's digest differs.

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
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing \
  --team-order d,g,s,db,t,c,h,f,b,e,l,m   # order is Aoi's setting (TEAM_ORDER in aoi_npb.py)
```

## Connecting with the existing Markdown implementation

The [DRAgoWing reports workflow](https://github.com/myon-bioinformatics/Aoi/blob/main/.github/workflows/dragowing.yml) checks out the latest main of `myon-bioinformatics/markdown` once on PRs, main updates, and manual runs, then renders research documents with `dragowing/reports/build_reports.py`. The docs-only skip for regular pytest is kept, and report generation runs even for docs-only changes.

Local example (point the output at an empty directory):

```sh
git clone https://github.com/myon-bioinformatics/markdown.git .deps/markdown
python -S dragowing/reports/build_reports.py --markdown-root .deps/markdown --output build/dragowing --previous-ref HEAD~1
```
