# Repository guidance

<!-- Canonical cross-repository template. Repository-local AGENTS.md may add only project-specific deltas. -->

## Scope

- Read the relevant documentation, source, and existing workflows before changing anything.
- Keep changes scoped to the request. Do not refactor unrelated code or upgrade dependencies without an explicit request.
- Preserve existing CI, deployment, and GitHub Pages configuration unless the task specifically requires a change.
- Repository-local rules may override a shared rule only when the difference is intentional; document the reason next to the local override.

## Workflow changes

- When modifying `.github/workflows/`, ensure actionlint passes.
- Quote YAML scalar values that contain `: ` or special characters.
- Do not broaden workflow permissions or alter deployment settings without a clear need.
- Prefer reusable workflows from `myon-bioinformatics/myon-bioinformatics/.github/workflows/` when a shared workflow already covers the requirement.

## Shared data

- Do not duplicate profile, repository, project, or public endpoint facts when a canonical source already exists.
- Canonical public data lives in `myon-bioinformatics/myon-bioinformatics.github.io` (`profile.json`, `api/repos.json`, `projects.json`, `services.json`).
- Repository-specific configuration may override shared defaults only when the difference is intentional and documented.

## Validation and delivery

- Run the smallest relevant checks already supported by the repository.
- Work on a feature branch and open a pull request; do not merge without explicit approval.
- In each PR, summarize the change, verification performed, and any known limitations.

## Aoi sub-project

- This repository is an independent copy of one subtree of `myon-bioinformatics/Aoi` (its prefix is listed in Aoi's `child-heads.json`). Aoi is the source of truth: change the files in Aoi first, then sync them here with a non-squash `git subtree` merge (see `docs/child-repositories.md` in Aoi).
- Aoi's `docs/` are the master rules (philosophy, principles, propositions). Read the relevant ones before changing logic; additions are welcome as long as they keep the intent.
- Judgement logic returns exit codes, and tests compare those numbers, never display text. The meaning of each code is fixed in Aoi's `docs/propositions.md` (Exit Codes).
- Do not leave syntax errors on main; CI runs `compileall`.
- Aoi itself has no root-level `AGENTS.md` or `CLAUDE.md`; these files exist for the standalone sub-project repositories.
