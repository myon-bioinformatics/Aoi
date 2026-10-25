# adjacent_netflix_subscription_levels — missing / deferred

## Big Mac ISO3 with no rows

| ISO3 | Status | Note |
|------|--------|------|
| CHN | MISS | Not present in tompec country list (clone efa54e3). Burger Parity has a “Netflix proxy avg” cross-section cell — **not** copied as history. |
| EUZ | MISS | Big Mac euro-area aggregate. Netflix list prices are national; no official EUZ Netflix SKU. Member-state series exist upstream (DE, FR, ES, …) but those ISO3 are outside `countries_iso3.txt`. |
| RUS | MISS | Not present in tompec country list this clone. |

## Intentionally not loaded

- tompec `price_usd` (source FX) — Season2 no-FX rule.
- Null / unavailable plans (`price: null`) — omitted, not gap-filled.
- Non–Big Mac ISO3 (192+ other tompec countries) — filtered out.
- Burger Parity `prices_all.csv` / `burger_netflix.csv` as panel history — snapshot cross-check only.
- iPhone / Mac / iPad files under `numeraire_hist_2026-10-25/` — Aoi lane; untouched.
- Spotify / gym / Starbucks / Uber Burger Parity products — out of scope.

## Probes deferred

| Path | Why deferred |
|------|----------------|
| Official Netflix help/plan pages per country | Not needed; tompec already gives easy multi-date LCU history |
| Reconstruct EUZ as mean of euro members | Invented aggregate — disallowed |
| Force-align Burger Parity cells onto nearest tompec date | Would mix sources into one series — cross-check JSON only |

## Cross-check summary

See `_crosscheck_burgerparity.json`. Exact standard-plan LCU matches on at least one tompec date for 10 of 30 Burger Parity Netflix countries that also sit in the Big Mac universe; remaining BM∩BP cells are near-misses (date/definition drift) or CHN miss.
