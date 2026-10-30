# docs: Master Files

A file placed directly under `docs/` is a **master file**. Every agent working on Aoi (human or AI) should read the master files before working, and they apply to every cycle and every domain. Cycle 2 and later may not be about baseball.

Master files may be improved and extended, but only in ways that keep their intent.

## Ecosystem Diagrams And Reading Guide

[ecosystem.md](ecosystem.md) brings the existing project illustrations together with their responsibilities, handoffs, and design principles. Read it for the whole-system view; use each child's documentation for supported APIs and commands.

| Project | Parent-side explanation and diagram | Implementation documentation |
|---|---|---|
| BlueProbe | [Observe, discover and preserve evidence](ecosystem.md#blueprobe) | [BlueProbe README](../blueprobe/README.md) |
| QueRyu | [Retrieve reproducibly with provenance](ecosystem.md#queryu) | [QueRyu README](../queryu/README.md) |
| SakAnalytics | [Measure patterns and preserve uncertainty](ecosystem.md#sakanalytics) | [SakAnalytics README](../sakanalytics/README.md) |
| DRAgoWing | [Make recorded structures visible](ecosystem.md#dragowing) | [DRAgoWing README](../dragowing/README.md) |
| NagoyAction | [Repeat and trace the research process](ecosystem.md#nagoyaction) | [NagoyAction README](../nagoyaction/README.md) |

The artwork is kept in Aoi's `docs/images/` and reused without adding copies to child repositories. It illustrates the concept, not measured results, actual source HTML, or feature availability. [PythDRagoras](PythDRagoras.md) supplies the hypothesis and validation role that closes the loop.

## What Counts As A Master File

A document belongs directly under `docs/` only if **all four** hold:

1. **General**: it holds for any cycle and any domain. Domain examples (baseball) may appear, but only as examples.
2. **Rule or definition**: it says how Aoi works (principles, definitions, procedures), not what a cycle found.
3. **Stable**: new data does not change it. It changes only by deliberate revision that keeps its intent.
4. **Must read**: an agent who skipped it would likely do the work wrong.

The same check applies to a new **section** added to an existing master file.

## Where Everything Else Goes

| Content | Place |
|---|---|
| What a cycle found: results, findings, summaries | `cycles/<cycle>/` (for example `FINDINGS.md`, `research/`) |
| Proposition files, claims, analysis settings of a cycle | `cycles/<cycle>/` |
| How one sub-project works in detail (a parser contract, a data source) | `<sub-project>/docs/` |
| A proposed master file that is not settled yet | `docs/drafts/` (create it when needed) |
| Images used by master files | `docs/images/` |

## Master Files

The list is checked by a test (`nagoyaction/tests/test_docs_masters.py`): a file directly under `docs/` that is not listed here, or a listed file that does not exist, fails the check. Adding a master file therefore always comes with an explicit check against the four criteria above.

| File | What it defines |
|---|---|
| [GENESIS.md](GENESIS.md) | Why Aoi exists. Read before anything else |
| [philosophy.md](philosophy.md) | What Aoi believes: observation first, residuals as evidence, doubt, mirrors, routes |
| [principles.md](principles.md) | The numbered principles that decisions are checked against |
| [observation.md](observation.md) | The role of observation, the foundation of everything that follows |
| [hypothesis.md](hypothesis.md) | How hypotheses are generated, evaluated, preserved and evolved |
| [validation.md](validation.md) | How evidence is evaluated, hypotheses are tested and explanations are challenged |
| [propositions.md](propositions.md) | The proposition engine: forms, strength, verdicts, exit codes, identity, scope, restating |
| [PythDRagoras.md](PythDRagoras.md) | The hypothesis and validation engine |
| [residuals.md](residuals.md) | The role of residuals |
| [research-method.md](research-method.md) | The standard research workflow |
| [data-policy.md](data-policy.md) | How data is collected, stored, transformed, preserved and interpreted |
| [registration-metadata-audit.md](registration-metadata-audit.md) | How registration provenance is classified conservatively and audited before correction |
| [ecosystem.md](ecosystem.md) | The structure of the ecosystem: independent projects, each answering a different type of question |
| [child-repositories.md](child-repositories.md) | Subprojects split into their own repositories (git subtree): registration, drift and diff checks |
| [distributions.md](distributions.md) | Minimal stdlib API registration, frozen-source regeneration, license notices and subtree boundaries |

重なり計算の軽量経路: [DRAgoWing の backend 契約・検証・測定](../dragowing/docs/overlap-stdlib.md)。明示指定時のみ有効。

ブラウザ起動の切り分け: [Chrome / Chromium の検証手順](diagnostics/browser-startup-validation.md)。検証専用で、マスターファイルではありません。
