# c001 clean replay comparison

This is a verification harness, not a new truth source.

## Goal

Keep the existing c001 outputs as a frozen V1 snapshot, regenerate V2 from the same
saved inputs without network acquisition, and compare every proposition/expression
and every logical form.  A difference means "investigate"; it does not mean V1 or
V2 wins automatically.

The first pass checks the deterministic calculation layer.  A later, separate pass
may reacquire source pages and compare acquisition/observation too.

## Compared fields

For every ID in `propositions.jsonl` and `sets.jsonl`:

- presence of the ID and each form;
- `definition_sha256` and `data_sha256` when present;
- registration/provenance fields such as `posthoc`, parent/change and held-out;
- each form's n, hold, undetermined, rate, verdict and code;
- the complete set of counterexample unit IDs.

Floating rates use only a 1e-12 absolute tolerance.  Counterexamples are compared as
sets of unit IDs so harmless ordering changes do not hide semantic equality.

## Safety

V1 is never overwritten. V2 must be written to a separate directory. The comparator
is read-only and exits non-zero on any semantic difference while also writing a JSON
difference report suitable for CI artifacts.

Do not call a differing V2 "correct" automatically. Classify the difference first:
input identity, definition drift, implementation drift, nondeterminism, metadata-only
drift, or an actual historical error.
