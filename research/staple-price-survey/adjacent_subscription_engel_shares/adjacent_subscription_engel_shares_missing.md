# Gaps / caveats
- The BLS CE detailed item tables for 2013–2023 returned HTTP 403, so the streaming and audio line items exist for 2024 only. The broad entertainment and AV panels contain 39 observed years spanning 1984–2024; 1994 and 1995 are absent. Endpoints do not imply complete coverage.
- No source measures SVOD-only spending as a share of spending across countries. Eurostat HBS fees also include licence fees and pay-TV.
- The Eurostat isoc figures are prevalence, not spending.
- The Japan figure covers the internet-shopping channel only, so it understates SVOD billed through other channels.
- The Canada figure is a national aggregate.
- Statista, Ofcom and ONS item detail were not used because they are paywalled or were skipped.

- Four HBS country-years (NLD 2010; NOR, PRT and ROU 2020) have blank published values for all three exported measures (12 missing values). Two BLS percent-reporting values are `n.a.`. All 14 remain explicit blank-valued observations, with raw tokens and record provenance in `note`; none are imputed.
- Three USA 2024 entertainment keys disagree between BLS Table 2500 and the BLS API panel: mean 3609.38 vs 3609.0; spending share 4.5959 vs 4.595; income share 3.4637 vs 3.463. Both alternatives are retained without choosing a winner or assuming a rounding explanation. Consumers must not sum alternatives as distinct spending.
- `_quality_report.json` lists conflicting alternatives, explicit missing values, and per-source observed years and internal absent years. Internal gaps are descriptive, not assertions that every series is annual. Wholly absent rows outside observed endpoints are not inferred.
