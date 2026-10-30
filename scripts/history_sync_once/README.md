# One-off Aoi history repair (local review packet)

Publication plan: create `automation/aoi-history-sync-20261030` from exact Aoi
`9f72b00e954cde61ab2c50cff4d5f41a709379ef`, adding only the reviewed workflow at
`.github/workflows/history-sync-once.yml` and this script, guard tests, patch and
README under `scripts/history_sync_once/`. The first branch creation push is the
single authorized execution. No manual rerun, token provisioning, permission
setting changes, direct research push or main push.

The runner separately checks out the exact base and makes genuine subtree pulls
of DRA a71ad693 and NagoyAction c763cc80. The operational files are NOT copied to
the resulting branch. The wrapper test correction, exact Nagoy registry/assertion
pin and generated output/inventory updates are the only parent content changes.
Existing research, cycles, inputs, outputs, startup workflows and budgets remain
untouched. Both actual upstream histories must be ancestors and exact subtree
trees. It publishes ONLY the absent `repair/aoi-subtree-history-20261030` branch.
A changed base or an existing destination stops publication; no fallback.

Owner explicitly approved this new code-writing CI route by current thumbs-up
on message Sentinel_a524a25cf258819197dc81197e29f0ac, verified by root at05:53UTC.
This is separate from the denied direct `research/shrink-index` update. Root
review is still required before staging publication.

Credential handling: checkout persist-credentials false. Only final publish step
receives GitHub's ephemeral repository token, passes HTTP auth via GIT_CONFIG_*
environment, never writes credential config/files. Artifacts only result.json
and test JUnit. No environment dump, token output, repository/archive artifacts.
The integration tests do not receive publication credential environment.

Official action refs verified by native public ls-remote:
- checkout v7 3d3c42e5aac5ba805825da76410c181273ba90b1
- setup-python v7.0.0 5fda3b95a4ea91299a34e894583c3862153e4b97
- setup-node v7.1.0 949feb2413d6458794dcd2491c4babbbce0c15c1
- setup-uv v10.3.0 1c37ad07a6a961277cf70c0d37d6f313000f5884
- upload-artifact v7 cf430e030ddbb5b0abf93d22962f4752f3646cd9

Review evidence: eight guard tests pass; YAML/Bash syntax pass. Independent peer
found no blocking issue. Actual local nonsquash imports succeeded: DRA merge has
zero content changes and real a71 second parent; Nagoy merge has real c763 second
parent and exact subtree. Combined Nagoy+wrapper tests307pass/23subtests;
registry tests additionally run with per-case mutation cleanup (not skipped).
Compiler and source pins are checked; distribution regeneration succeeds.

After successful runner publication, root must inspect the actual head/ancestry,
then create an authorized Draft PR through the connector. A GITHUB_TOKEN push
does NOT establish ordinary push CI. The Draft PR's complete exact-head CI,
including real startup8s/export jobs, remains required. No merge/label cleanup on
repair-job success alone. Current browser export intermittency remains separate.

Staging branch is operational-only and must never be merged. After validation,
remove its operational files in a cleanup commit or remove the staging branch
with explicit root authorization. The repair branch contains no new workflow,
so it cannot trigger this branch-filtered operational job itself.

Full build-only validation (fresh exact base) succeeded: local head ac03255f759bdd431d2fe2c912a8b6f81bb16373, 408 JUnit cases including23subtests, zero failures/errors/skips. Tracked-only staging uses git add -u -- so existing ignored distribution paths are updated without forcing untracked files. The first local build caught this operational staging issue after all tests passed; its log is retained separately. No hosted run yet.
