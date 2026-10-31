# BlueProbe

<p align="center">
  <img src="docs/brand/icon.png" alt="BlueProbe icon" width="160" />
</p>

[Icon](docs/brand/icon.png) · [Favicon](docs/brand/favicon.png)

> Observe first, interpret later.
>
> HTML/CSS/DOM structure observation and extraction for NPB baseball pages (split out from Aoi/blueprobe).

![BlueProbe](docs/images/blueprobe.webp)

*Concept image (a figure for sharing the idea; not the actual data or HTML structure)*

## Role in Aoi

**Observation and detection.**

| Challenges | Approach | Outcomes & value |
|---|---|---|
| Researching information on the web is inefficient | 1. Make discovery a regular routine | Find the information you need |
| The whole picture of an analysis target is hard to see | 2. Read the fetched sources | A more efficient research process |
| Unknown information is hard to find | 3. Shape the findings into reports | Leads toward the unknown |

Topics: web crawling, information gathering, research support

## Overview

BlueProbe is an observation and extraction tool that reads fetched web pages (HTML/CSS/DOM) and records **what is there**. It does not judge wins, losses, or causes.

- Parts independent of the source (notation normalization, the report contract, offline reparsing that reads only the cache) live in `blueprobe.py`.
- How to read each source is split into separate modules (`<name>.py`); writing `pages()` and `parse()` is enough to use it (see "Adding a source" below).
- It returns not only what was accepted, but also counts of what wasn't, and the source text that matched no category (`unknown`).
- Reparsing does not access the network. Fetching is handled by [QueRyu](https://github.com/myon-bioinformatics/QueRyu); BlueProbe reads its saved bodies.

The entry point for organizing coordinates and interaction history of saved web screens without a browser is
[`web_observations.py`](docs/web-portability.md). It can also build a hash list of Dart/Kotlin/Swift sources and
build settings. Parsing saved observations is kept distinct from verifying execution of the current implementation.

This repository was split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) (see "Relationship with Aoi" below).

## Installation and usage

Uses Python 3.11+ and [uv](https://docs.astral.sh/uv/). There are no runtime dependencies (`pyproject.toml`). `selectolax` is only for cross-checking during development, comparing the standard library's HTML tree with Lexbor's results.

```bash
git clone https://github.com/myon-bioinformatics/BlueProbe.git
cd BlueProbe
uv sync
uv run python blueprobe.py --source <source module name> --cache <QueRyu cache> --out observed.md
```

It reads only the cache and does not access the network. If there are unknown notations, it shows the count (exit code 1 with `--strict`).

## Layout

| File | Role |
|---|---|
| `blueprobe.py` | Source-independent parts: normalization, the report contract, offline reparsing (`inspect`), the DOM pattern table (`--list-patterns`), document classification (`classify_document` / `--classify`), and the `html.parser` HTML tree. Details in [docs/dom_patterns.md](docs/dom_patterns.md) |
| `html_source.py` | A generic source (`HtmlSource`) that passes saved HTML to a trusted offline extraction function |
| `snapshot_source.py` | The contract for suppliers of saved bodies (`SnapshotSupplier`) and the QueRyu adapter (`QueRyuCacheSource`) |
| `heading_observations.py` | Observing the heading hierarchy (`<h1>`–`<h6>`) and landmark structure of saved HTML |
| `web_observations.py` | Organizing observations of saved web screens and source lists (no browser or SDK) |
| `docs/contract/v1/` | Contracts for reports and snapshot records (additions stay in v1; breaking changes go to v2) |
| `docs/boundaries.md` | Boundaries of responsibility between BlueProbe / QueRyu / web-ui (proposal) |
| `docs/antipatterns.md` | Failures likely to recur, and the commitments against them |
| `tests/cases/*.jsonl` | Corpus of notation variants (same id / category / value / reason format as xprobe) |

Sources for NPB (Nippon Professional Baseball) are collected in "NPB (professional baseball) sources" later on.

## Adding a source

Write the following two in `<name>.py` (`blueprobe/<name>.py` in Aoi), and it can be used directly from QueRyu and `inspect`.

```python
def pages(scope) -> list[tuple[str, str, str]]: ...   # (key, url, group)
def parse(html: str, url: str) -> dict: ...          # return in the new_report() shape
def check(records) -> list[str]: ...                 # optional; check against known values
```

Write regexes narrowly, as full matches. When you find a new notation, add a case to the corpus before widening.

## Report contract

The result of reading one page returns not only what was accepted, but also what wasn't.

```text
records : accepted observations (source text and derived values side by side)
counts  : counts per category of what wasn't accepted (e.g. cancelled, non_regular)
unknown : what matched no category; keep the source text → suspect a notation change
```

## Tests

```bash
PYTHONPATH=<Aoi root>/queryu uv run pytest -q
```

Cache integration tests use QueRyu (`Aoi/queryu`). CI (`.github/workflows/ci.yml`, Python 3.11–3.15) resolves Aoi's main at run time, checks it out to `.test-deps/aoi`, and leaves the resolved SHA in the job summary. The ref can be overridden with `aoi_ref` in `workflow_dispatch`.
Add `queryu` to `PYTHONPATH`. The optional lab integration tests are in "Reproducing offline integration tests with a snapshot of past patterns" later on.

## Relationship with Aoi

This repository was split out, preserving history, from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject
[`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe).
It keeps syncing with Aoi's `blueprobe/` via `git subtree` (a change made on either side is reflected to the other).
Like the other subtree children, it is registered in [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json) at the top of [Aoi](https://github.com/myon-bioinformatics/Aoi). It is not registered in the parent [myon-bioinformatics](https://github.com/myon-bioinformatics/myon-bioinformatics)'s `child-heads.json`. No vendor lock is used between Aoi and BlueProbe (the list and procedure are in Aoi's [docs/child-repositories.md#blueprobe](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md#blueprobe)).

The purpose of splitting out is to gather here, across repositories, the know-how for observing and extracting by looking at HTML/CSS/DOM structure.
BlueProbe's runtime code does not depend on other repositories' implementations; needed information is handled by aligning references and contracts.
Each repository may refactor on its own side.

### Syncing

```bash
# BlueProbe → Aoi (at Aoi's root; brings the child's main into `blueprobe/`)
git subtree pull --prefix=blueprobe https://github.com/myon-bioinformatics/BlueProbe.git main
```

Aoi → BlueProbe and updating the registered `sha` follow the BlueProbe section of child-repositories above.

`pyproject.toml`, `conftest.py`, `docs/images/`, and `.github/` exist only on the standalone repository side.

## Related subprojects

Each subproject of the parent [Aoi](https://github.com/myon-bioinformatics/Aoi) is its own repository. They are listed with their location in Aoi (subtree). The list and registration details are in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md).

| Repository | Location in Aoi | Role |
|---|---|---|
| **BlueProbe** (this repository) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | Observation and extraction (reads saved HTML/CSS/DOM and records what is there) |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | Fetching and building observation datasets (caches with provenance) |
| [SakAnalytics](https://github.com/myon-bioinformatics/SakAnalytics) | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | Metrics and statistics from observation data (team × season metrics, outlook for remaining games) |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | Verifying explanations (propositions, counterexamples, objections) |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | Pipeline execution and automation (the same definition locally and on GitHub Actions) |
| [DRAgoWing](https://github.com/myon-bioinformatics/DRAgoWing) | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | Figures and reports (Plotly.js HTML, the four-forms table) |

## Related repositories referenced and aligned with

| Repository | Where to look | Contents |
|---|---|---|
| [mcp-toolcall-lab](https://github.com/myon-bioinformatics/mcp-toolcall-lab) | `src/mcp_toolcall_lab/adapters/html_snapshot.py`, `css_inspect.py`, `source_access.py`, `docs/source-access.md` | Offline extraction of saved HTML, CSS inspection, source access (a snapshot of past patterns fetched by SHA, connected optionally) |
| [browser-test-kit](https://github.com/myon-bioinformatics/browser-test-kit) | `scripts/page_text.py`, `examples/capture_browser_dom.py`, `docs/dom-capture.md`, `fixtures/page_text/` | Page body text extraction and browser DOM capture |
| [web-ui](https://github.com/myon-bioinformatics/web-ui) | `docs/local-dom-lab.md`, `tool/serve_dom_lab.py`, `tests/integration/test_gradio_dom.py` | Local DOM lab and DOM evidence |
| [flutter_navigation_basic](https://github.com/myon-bioinformatics/flutter_navigation_basic) | `e2e/tests/*.spec.ts` | DOM observation of Flutter Web screens (Playwright) |

How to align: when you find a new extraction technique or failure in a referenced repository, first record it as an observation here in the corpus (`tests/cases/`) or `docs/antipatterns.md`, then align the implementation.

## License

MIT License ([LICENSE](LICENSE)). Same contents as Aoi's `LICENSE`.

## Future considerations

Other repositories might place only BlueProbe's core notation normalization and extraction functions as a minimal single-file module.
Even then, this whole repository will not be vendored. Undecided for now.

---

# Detailed usage and NPB-specific content

## Connecting to shared extraction of saved HTML

`html_source.HtmlSource(selector=..., extractor=...)` passes fetched HTML to a trusted
offline extraction function and converts the result into the existing `inspect()` report format.
Fetching, caching, and NPB-specific observation continue to be handled by the existing modules.
Structures that can't be extracted are kept as `extraction_failed` and `unknown` with source text.
Changing extraction conditions or rerunning on the same page makes no network requests, including for linked resources and CSS.

```python
from html_source import HtmlSource
from mcp_toolcall_lab.adapters.html_snapshot import extract

source = HtmlSource(selector="main#calendar > .day", extractor=extract)
rows = inspect(source, saved_pages, records_out)
```

The above is an optional connection example using the extraction functions from the merged lab PRs [#110](https://github.com/myon-bioinformatics/mcp-toolcall-lab/pull/110) and
[#111](https://github.com/myon-bioinformatics/mcp-toolcall-lab/pull/111).
BlueProbe does not install that package automatically. Normal NPB parsing has no new dependencies.
`--source html_source` does generic extraction in environments where lab's extraction module is available.
The selector is a limited syntax of tags, `#id`, `.class`, child `>`, and descendants;
it does not imply CSS rendering, JavaScript execution, or HTML5 browser DOM reconstruction.
Support for all CSS syntax and Python execution on Pages are not guaranteed.

### Reusing snapshots from a verified cache

The supplier is replaceable (the contract is [docs/contract/v1/snapshot.md](docs/contract/v1/snapshot.md)).
Any supplier uses `inspect_snapshots(source, supplier)`; QueRyu uses `inspect_queryu_cache`.
The old name `inspect_cache` is kept for compatibility (deprecated).

`inspect_queryu_cache(source, cache, entries=None, records_out=None)` reads QueRyu's verified
bodies. By default it uses the latest rows; specifying `entries` uses rows from the selected fetch points.
NPB parsers are passed the source HTML as is. A snapshot-aware `HtmlSource` is passed
the `Cache.snapshot()` envelope, which is verified and extracted with the existing
`mcp_toolcall_lab.source_access.extract_snapshot`.
No custom validator or HTML parser is added.
Reparsing here means extracting HTML structure and reading observed values. Aggregation and metric calculation are handled by
[SakAnalytics](https://github.com/myon-bioinformatics/SakAnalytics), and hypothesis evaluation by
[PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras).

```python
from blueprobe import inspect_queryu_cache
from html_source import HtmlSource
from queryu import Cache

records = []
rows = inspect_queryu_cache(HtmlSource(selector=".calendar a"), Cache("data/raw/npb_calendar"),
                     records_out=records)
```

The `--source html_source --cache ...` CLI also uses this path.
`derived` keeps the conventional extraction result, `snapshot` keeps the attributes returned by shared verification,
and `cache_entry` keeps the original provenance. An optional injected function is
specified explicitly with `HtmlSource(snapshot_extractor=...)`. Its arguments are the snapshot dict and extraction conditions,
and its return value is a `snapshot` / `extraction` dict, the same as lab's.
The conventional `parse(html, url)` / `extractor=...` are kept for raw HTML,
and are not counted as having verified saved bytes.

QueRyu hash/length mismatches stop with an error before extraction, and missing past bodies are not fetched automatically.
lab checks schema, URL format, maximum size, and decoded content hash,
but does not verify the truth of the URL or fetch time, or the authenticity of the response. Unknown provenance stays unknown.
Execution management of source checkouts and CI runner identity is NagoyAction's responsibility;
no checkout verification or runner is added to the BlueProbe runtime.

### Reading CSS and comparing with existing NPB parsing

`HtmlSource(include_css=True, stylesheets={saved_url: saved_css}, extractor=extract)`
reads declarations from embedded, inline, and explicitly given saved CSS. Color values, CSS variables, important flags,
conditional rules, and matches between selectors and HTML elements are kept on the derived side.
External stylesheets and @import are not fetched and are kept as unread references. Per-CSS hashes are kept too.
Unsupported selectors are distinguished as unsupported, and no matches as unmatched.
Display colors, inheritance, specificity, variable resolution, and screen-size conditions are not computed; computed_styles is false.
Being able to read CSS is not treated as being able to reproduce the screen.

`html_compare.compare_calendar()` compares the links read by selector from saved HTML with
the game URLs accepted by the existing `npb_calendar.parse()`.
It returns missing accepted games, duplicate links, and extraction failures. The source HTML is passed as is to the NPB parser, so
judgement of tournament headings, cancellations, and unknown notations stays with the existing processing.
`complete_for_adopted_games` means only coverage of the games the existing parser accepted;
it is not proof that the parser itself didn't miss unknown games.
The comparison uses the saved NPB fixture's 4 games, 1 cancellation, and 1 non-official game.
Reparsing the same source text any number of times makes no new GETs. Normal NPB tests without lab work as before.

### Reproducing offline integration tests with a snapshot of past patterns

CI's `Offline lab integration (Python 3.14)` fetches lab's merge commit
`6a3fe3aac7e5ae939d2fe2720dfae002d5f0dd90` by SHA as verification test data for past patterns, and checks it out to `.test-deps/lab`.
It adds `src` to `PYTHONPATH` at test time, and a pre-check verifies the SHA and the import origins of
`html_snapshot`, `css_inspect`, and `source_access`. Import origins are
also checked inside the actual tests. No single-file copies, automatic lab installation, or fetching at run time.
The normal Python 3.11–3.15 test matrix stays without lab, and integration tests run only on 3.14.
This does not mean lab integration was verified on all Python versions.

Run at this repository's root (in Aoi, at Aoi's root, prefixing test paths with `blueprobe/`) (the clone is preparation before testing, not network access during extraction).

```bash
git clone https://github.com/myon-bioinformatics/mcp-toolcall-lab.git .test-deps/lab
git -C .test-deps/lab checkout --detach 6a3fe3aac7e5ae939d2fe2720dfae002d5f0dd90
test "$(git -C .test-deps/lab rev-parse HEAD)" = 6a3fe3aac7e5ae939d2fe2720dfae002d5f0dd90
export AOI_LAB_SOURCE_ROOT="$PWD/.test-deps/lab/src"
export PYTHONPATH="$AOI_LAB_SOURCE_ROOT"
uv run --python 3.14 python - <<'PY'
import os
from pathlib import Path
from mcp_toolcall_lab.adapters import css_inspect, html_snapshot
from mcp_toolcall_lab import source_access
root = Path(os.environ['AOI_LAB_SOURCE_ROOT']).resolve()
for module in (html_snapshot, css_inspect):
    expected = root / 'mcp_toolcall_lab/adapters' / (module.__name__.rsplit('.', 1)[1] + '.py')
    assert Path(module.__file__).resolve() == expected, module.__file__
assert Path(source_access.__file__).resolve() == root / 'mcp_toolcall_lab/source_access.py'
PY
uv run --python 3.14 pytest -q --require-lab-integration \
  tests/test_blueprobe_html_source.py::test_optional_real_lab_extractor_reuses_all_calendar_rows \
  tests/test_blueprobe_html_compare.py::test_real_saved_npb_fixture_coverage_and_css \
  tests/test_blueprobe_html_source.py::test_verified_cache_real_lab_snapshot_replay \
  --junitxml=build/test-results/lab-integration-3.14.xml
# all tests with lab
uv run --python 3.14 pytest -q --require-lab-integration
# normal tests without lab. Run in an environment where lab is not installed separately.
unset PYTHONPATH AOI_LAB_SOURCE_ROOT
uv run --python 3.14 pytest -q
```

`--require-lab-integration` makes the 3 real-extractor tests mandatory, and does not treat not-collected, skip,
or import failure as success. In normal mode, the 3 optional integration tests are skipped only when lab is absent.
These tests block socket connections and verify extraction of 31 rows, coverage of 4 games in saved NPB HTML,
duplicates, 1 cancellation and 1 non-official game, saved external CSS, unsupported selectors, and identical reruns.
They also confirm that external CSS links and `@import` are not fetched automatically.
The integration JUnit is saved even on failure, and the aggregator requires 6 reports in total: 5 normal and 1 integration.

The following is past local verification as of PR #15 (2026-10-09, Python 3.14.8, lab snapshot of past patterns, Aoi's locked dependencies):

- The 2 mandatory real-extractor tests: 2 passed / 0 skipped
- All tests with lab: 533 passed / 24 skipped
- All tests without lab: 531 passed / 26 skipped

The common 24 skips are due to missing optional season simulator dependencies, unrelated to this integration.
Without lab at that time, the 2 real-extractor tests were also skipped. The `284 passed` in the first PR body is
a past verification record and is not treated as the current total test count. Check CI results in
the latest run of [PR #15](https://github.com/myon-bioinformatics/Aoi/pull/15).

## NPB (professional baseball) sources

| File | Role |
|---|---|
| `npb_calendar.py` | Source: npb.jp's monthly official game calendar |
| `docs/npb_calendar.md` | What was checked for which year in that source (observed and unconfirmed kept separate) |
| `npb_team_annual.py` | Source: npb.jp's annual team tables (summaries from 1950, detailed tables from 2005) |
| `npb_team_batting.py` | Source: npb.jp's annual team batting stats ([docs/npb_team_batting.md](docs/npb_team_batting.md)) |
| `npb_team_fielding.py` | Source: npb.jp's annual team fielding stats ([docs/npb_team_fielding.md](docs/npb_team_fielding.md)) |
| `npb_game_linescore.py` | Source: npb.jp's game page line scores (R, H, E) ([docs/npb_game_linescore.md](docs/npb_game_linescore.md)) |
| `npb_schedule_current.py` | Source: npb.jp's current-season monthly schedule and results ([docs/npb_schedule_current.md](docs/npb_schedule_current.md)) |
| `html_compare.py` | Structural coverage of saved HTML, and comparison with existing NPB observations (offline) |

```bash
uv run python blueprobe.py --source npb_calendar --cache data/raw/npb_calendar --out observed.md
```

### NPB annual team tables

`npb_team_annual.py` reads both leagues' annual summary tables from 1950, and detailed win/loss, batting, pitching, and fielding tables from 2005.
Individual tables are not extracted. Old items that weren't published are not filled with 0, and unknown columns are kept in `unknown`. Observation only; no recomputing rates or checking agreement between tables.

## Emoji observation in saved HTML (`emoji_observations.py`)

```sh
python emoji_observations.py page.html            # counts, forms, and locations per identity
python emoji_observations.py page.html --json     # records (one row per occurrence) and summary
```

Emoji in the body, `<title>`, descriptive `<meta>`, and attributes (`aria-label`, `title`, `alt`, `placeholder`, etc.) are recorded
with the element's position (`html > body > nav > button`), 30 characters of source text before and after, whether it is inside a control, that control's label, and `aria-hidden`.
Contents of `script`, `style`, `template`, `noscript`, `svg` and input values (`value`) are not displayed text, so they aren't read.
Anything over the limit is kept in `unknown` (not silently discarded). No judgement of good or bad (e.g. emoji inside a button without a label are just counted as `unlabelled_control`).
`observe_snapshot()` accepts QueRyu's `html-snapshot/1` and carries `response_sha256` and `fetched_at` into each record.

Detection uses UTS #51 forms and Extended_Pictographic (Unicode 16.0), the same contract as xprobe's `emoji_sequences`.
No code from other repositories is imported; alignment is via `tests/cases/emoji_corpus.txt` and expected values built with xprobe
(`emoji_corpus.expected.json`, recording the xprobe commit). Naming is on QueRyu's `emoji_names.json` side.

## Observing names of controls and images (`accessible_names.py`)

```sh
python accessible_names.py page.html                         # counts of names, origins, and categories
python accessible_names.py tests/cases/pages/github-io-html-import.json   # btk-browser-dom/1: also checks against the aria snapshot
```

Names of buttons, links, inputs, tabs, images, etc. are recorded with their origin (`aria-labelledby` / `aria-label` / `label` / `value` / `alt` / body text / `title` / `placeholder`),
and `empty_name`, `emoji_only_name`, `aria_hidden_control`, `image_without_alt`, `placeholder_only`, and `ambiguous_link_name` (links with the same name but different destinations) are counted.
Name computation is an **approximation** of W3C accname (`ACCNAME_APPROXIMATION_AS_SPEC`), and CSS is not evaluated. 100% agreement is not the goal; discrepancies are added to the antipatterns as observations.

`tests/cases/pages/` holds DOM and aria snapshots of 5 real pages from github.io (`myon-bioinformatics.github.io`) and web-ui, served over local HTTP from each repository's commit,
rendered in Chromium, and captured with browser-test-kit's `capture()` (`btk-browser-dom/1`).
Provenance (repository, commit, path, public URL, blocked external requests) is in each JSON's `provenance`. They are renders from commits rather than the public sites themselves,
so the same thing can be reproduced in environments that can't reach `*.github.io`. The check results are 49 matches, 6 CSS-derived differences, 0 mismatches (pinned in tests).

## Observing heading hierarchy and landmark structure (`heading_observations.py`)

```sh
python heading_observations.py page.html                        # heading levels, landmarks, flag counts
python heading_observations.py tests/cases/pages/web-ui-examples-index.json --json
```

Observes headings (`<h1>`–`<h6>`) and landmark regions (`<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, named `<section>`, and explicit ARIA roles) in HTML.
Besides level, text, DOM path, containing landmark, and hidden state, it records structural categories: `empty_heading`, `skipped_heading_level`, `multiple_h1`, `missing_main_landmark`, `unlabelled_landmark`, and `heading_outside_landmark`.
It does not access the network, and makes no judgements or changes.

This is static structural observation, not a reproduction of the browser's whole accessibility tree. `article` and unnamed `section` are not counted as landmarks, and `header` / `footer` inside `main` / `article` / `aside` / `nav` / `section` are not counted as page-wide landmarks ([HTML-AAM](https://www.w3.org/TR/html-aam-1.0/)). `aria-level` is used only when it is an integer of 1 or more; otherwise (empty, 0, negative, invalid) it falls back to the HTML heading level (h1–h6), or to the ARIA default of 2 for `role="heading"`. Tree structure and name computation are shared with `accessible_names.py`. `missing_main_landmark` is also kept as a page-level record (`type: "page"`).
