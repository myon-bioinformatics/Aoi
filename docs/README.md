# docs: Master Files

A file placed directly under `docs/` is a **master file**. Every agent working on Aoi (human or AI) should read the master files before working, and they apply to every cycle and every domain. Cycle 2 and later may not be about baseball.

Master files may be improved and extended, but only in ways that keep their intent.

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
