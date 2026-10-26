# Subscription observation contract (seven packs added in PR #128)

Netflix is outside this contract and unchanged.

The required observation key is `(country, date, variable, source)`.
`source` is the exact published URL in the CSV, including path, not just a domain.
Dates are reported snapshot dates; `note` carries retrieval and price provenance.
The archive capture URL is not uniformly present: historical observations are
third-party reports, not independently verified official historical quotes.
No source URL is silently normalized or preferred.

Use `subscription_contract.observations(rows)` to validate and obtain a stable
key-sorted list. Missing dimensions, nonpositive/nonfinite prices, empty units,
and any duplicate full key (even identical values) are errors. The seven packs
are deliberately enumerated, so this loader does not ingest Netflix or raw mirrors.

Use `cross_source_groups(rows)` to enumerate equal and conflicting multi-source
observations. Conflict means different numeric prices or units. Never sum or
average these as extra countries. Use `select_source(rows, exact_url)` for an
explicit single-source comparison, with no fallback for missing coverage. Report
the selected URL, dates, units and missing-country coverage alongside results.
Compare prices only within matching currencies/units; no FX or pooled currency
aggregation is provided. Row order cannot decide which price survives.

Run `python research/staple-price-survey/subscription_contract.py` for the full
reproducible audit. `subscription_source_audit.json` records its current output.
Original raw data is retained. YouTube's five quarantined observations are
excluded from the analysis CSV/gzip; see its missing note for evidence and gaps.
The other third-party values are reported observations, not confirmed official
checkout prices; inter-source disagreement remains explicit rather than resolved
by an invented canonical value.
