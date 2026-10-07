# Registration metadata audit

This follow-up records the rule learned from the #9/#10 production test before changing any research data.

## Contract

A result has three display states:

- **posthoc / 事後構成** — only when machine-readable metadata explicitly has `posthoc = true`.
- **preregistered / 事前登録** — only when a structured `preregistration` table says it was recorded before evaluation **and** names evidence for that record.
- **unknown / 不明** — everything else, including missing `posthoc` and `posthoc = false`.

Therefore `posthoc = false` is not an alias for preregistration.

Narrative comments such as 「計算前に書いた式」 are useful audit leads, but they do not silently upgrade metadata.  They must be checked against a durable record before adding a `preregistration` table.

## First c001 audit leads

The current cycle file says R72 and R73 were written before evaluation.  E20 is under R72; E24/E25 are under R73.  E26 is explicitly `posthoc = true`.  R76 is also described as written before evaluation while E29–E32 are explicitly posthoc.  Those combinations must be investigated rather than normalized mechanically.

The production inbox therefore correctly renders E25 as **unknown** with the current machine-readable data.  Changing E25 is deferred until the evidence behind R73 is identified.

## Tests first

`test_registration_audit.py` locks these rules:
- false/missing posthoc stays unknown;
- explicit posthoc is posthoc;
- preregistration needs both a pre-evaluation assertion and evidence;
- conflicting posthoc+preregistration assertions fail audit;
- narrative comments are audit leads only.

No c001 research result or metadata value is changed by this PR.


## Replay against historical c001 data

The audit contract was replayed against the concrete R72/R73/R76 metadata pattern from
`cycle-001/chunichi@0723d1137fc8448fbabb7bbe5fc14333ddfaabe2`.

- R72 narrative says the family was written before evaluation; E20 has no explicit registration field.
- R73 says the same; E25 has no explicit registration field, while E26 is explicitly posthoc.
- R76 says the family was written before evaluation, while E29-E32 are explicitly posthoc.

This is exactly why narrative text and a single `posthoc` boolean must not be collapsed
into one inferred truth.  The regression fixture preserves this historical tension:
E20/E25 remain unknown; E26/E29-E32 remain posthoc.  No record is promoted to
preregistered until the durable pre-evaluation evidence is identified.

The #9 production replies independently exercise the consumer side: E25 rendered
`［不明］`, while E26 and E30 rendered `［事後構成］`.  Those observations agree
with this conservative classification and do not themselves rewrite the source data.
