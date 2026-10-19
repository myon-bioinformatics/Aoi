# c001 research inputs

The worker selects a bundle only with `--input-bundle extended-v1`. The cycle's
canonical LittleBit holdout files and historical outputs remain byte-for-byte
unchanged. An omitted selector still uses the old canonical paths and does not
repair their incompatible set registry by inference.

`extended-v1.json` selects one preserved history, `from-cycle-001/`, for all of:

- `analysis.toml`: complete analysis configuration, including the original 2020
  exclusion reason and extended confirmation proposition IDs;
- `propositions.toml`: 210 definitions, including all 32 references from the
  shared cycle `sets.toml` (31 registered expressions);
- `outputs/season.jsonl`: 168 team-seasons, 2012–2025, with the derived columns
  required by the extended definitions.

The cycle-level `sets.toml` is explicitly pinned as the shared registry. These
four files have SHA-256 pins; the worker fingerprints the manifest itself too.
Per-role path overrides and silent fallback are forbidden. Updating source data
requires a deliberately reviewed bundle version and a fresh state directory.
The input fingerprint also includes canonical inputs, implementation, runtime and
lockfiles, so a resumed state never silently switches histories.

Aoi validates the entire registry, not just E1's selected sets: proposition
lineage/definitions, every set reference and expression, required columns in
every raw row (conditions, scope, context, surprise, and evaluation metadata),
scalar types, finite numbers, unique unit identities, expected counts and unit
hash, all analysis settings, confirmation IDs, focus/team/league, exclusion
seasons and reasons. Every proposition/expression predicate is compiled and run
before initialization. The 211 required columns are reported in checkpoint
`state.input_validation`. Existing explicit null observations remain unknown,
with per-column null counts; a missing key/column is rejected. The 2020 exclusion
removes 12 rows, leaving 156 included rows.

Local offline probe (POSIX, dependencies from Aoi's locked environment):

```bash
AOI_RESEARCH_ENABLED=1 \
AOI_RESEARCH_ACTOR=local-offline-test \
AOI_RESEARCH_ALLOWED_ACTORS='["local-offline-test"]' \
GITHUB_REPOSITORY=myon-bioinformatics/Aoi \
uv run --frozen python nagoyaction/inbox/inbox.py worker \
  --cycle c001-chunichi --input-bundle extended-v1 --seed E1 \
  --seconds 30 --max-steps 3 --state-dir /tmp/aoi-c001-extended-probe
```

These environment assignments apply only to this local process. They do not set
repository variables. Use a fresh external state directory for each input/code
version. The first unit validates and initializes; subsequent units evaluate
candidates. Candidate contradictions can produce an exploratory empty-set
diagnostic; this differs from missing input/configuration errors, which refuse
initialization and produce no checkpoint.

`tests/test_research_input_bundle.py` runs the real public CLI, confirms bounded
startup/evaluation, compares five units in one invocation with two plus three
units across restart, checks source hashes are unchanged, and rejects corrupted
hashes and semantically invalid re-pinned inputs before checkpoint creation.
This is offline input/integration evidence, not confirmation of the hypotheses,
completed exhaustive exploration, or a safe Actions canary. Issue #71 remains open
for the separate reviewed trusted-main manual execution and durable transport
gates. No autonomous workflow or schedule is enabled here.

Recorded local evidence: [c001-input-bundle-v1.json](../../../docs/evidence/c001-input-bundle-v1.json).
