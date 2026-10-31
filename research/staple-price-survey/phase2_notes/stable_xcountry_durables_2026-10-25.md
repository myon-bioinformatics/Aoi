# Stable cross-country durables / numéraire screen

Date: **2026-10-25 Asia/Tokyo**. Aoi lane (Numbeo/COL + branded/product indices).

## Question

Which internationally available **absolute** price series vary little across countries,
and could sit beside the Big Mac as a parity / numéraire alternative?
Focus: electronics/appliances, cars/motorcycles, and other goods with sticky cross-country USD levels.
Public transit fares deferred. Furnishings deprioritized. CPI/HICP **indices** excluded from the ranking
(they do not show level parity). No FX invented when the source lacks USD.

## Method

- Unit of comparison: source-published **USD** (Numbeo display USD; Burger Parity `usd_price`).
- Dispersion: **CV** = σ/μ and **p90/p10** on positive country observations (one price per country).
- Lower CV / p90/p10 ⇒ more Big-Mac-like level stability.
- Crowd Numbeo labeled clearly. Easy paths only.

## Ranking (absolute multi-country series)

| Rank | Family | Series | n | ISO3 | median USD | CV | p90/p10 | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | Electronics | iPhone 15 (Burger Parity) | 30 | 30 | 966.605 | 0.1914 | 1.413 | NEW panel iphone_15_burgerparity |
| 2 | Food service | Starbucks Tall Latte (Burger Parity) | 30 | 30 | 4.550 | 0.2122 | 1.664 | already starbucks_latte_burgerparity |
| 3 | Digital sub | Netflix standard (Burger Parity) | 30 | 30 | 11.850 | 0.2291 | 1.926 | NEW panel netflix_standard_burgerparity |
| 4 | Food service | Big Mac (Burger Parity ref) | 30 | 30 | 5.075 | 0.2317 | 1.864 | Season2 owns Big Mac — not duplicated |
| 5 | Apparel | Numbeo Nike mid-range shoes | 102 | 102 | 94.560 | 0.2457 | 1.812 | NEW focused numbeo_nike_shoes_crowd |
| 6 | Apparel | Numbeo Zara/H&M summer dress | 102 | 102 | 41.980 | 0.2777 | 2.041 | NEW focused numbeo_zara_hm_dress_crowd |
| 7 | Energy | Gasoline (Burger Parity) | 30 | 30 | 1.340 | 0.3014 | 2.196 | overlap Numbeo gasoline; not new panel |
| 8 | Vehicles | Numbeo Toyota Corolla equiv (ex-Singapore) | 101 | 101 | 29855.870 | 0.3027 | 1.861 | same panel; tax/COE outlier removed for screen |
| 9 | Vehicles | Numbeo VW Golf equiv (ex-Singapore) | 101 | 101 | 29927.020 | 0.3253 | 2.006 | same panel; tax/COE outlier removed for screen |
| 10 | Food/service | Numbeo Milk (regular), (1 liter) | 102 | 101 | 1.425 | 0.3461 | 2.387 | already numbeo_staples_restaurant_crowd |
| 11 | Service | Gym membership (Burger Parity) | 30 | 30 | 33.450 | 0.3760 | 2.488 | SKIP — not durable / higher CV |
| 12 | Food/service | Numbeo McMeal at McDonalds (or Equivalent Combo | 102 | 101 | 8.360 | 0.3994 | 2.647 | already numbeo_staples_restaurant_crowd |
| 13 | Food/service | Numbeo Cappuccino (regular) | 102 | 101 | 2.885 | 0.4048 | 2.968 | already numbeo_staples_restaurant_crowd |
| 14 | Food | Coca-Cola 330ml (Burger Parity) | 30 | 30 | 1.460 | 0.4076 | 3.830 | already coca_cola_330ml_burgerparity |
| 15 | Energy | Numbeo Gasoline 1L | 102 | 102 | 1.475 | 0.4104 | 3.327 | parent clothing panel; energy |
| 16 | Apparel | Numbeo Levi's 501 jeans | 102 | 102 | 62.350 | 0.4278 | 4.071 | parent clothing panel only |
| 17 | Food | Bread (Burger Parity) | 30 | 30 | 1.450 | 0.4745 | 3.820 | Season2/food lane; higher CV |
| 18 | Vehicles | Numbeo Toyota Corolla equiv | 102 | 102 | 30117.475 | 0.4766 | 1.902 | already numbeo_new_car_crowd |
| 19 | Digital sub | Spotify (Burger Parity) | 30 | 30 | 8.295 | 0.4888 | 5.651 | SKIP land — high CV (regional pricing) |
| 20 | Vehicles | Numbeo VW Golf equiv | 102 | 102 | 29939.685 | 0.4926 | 2.067 | already numbeo_new_car_crowd |
| 21 | Transit | Uber 5km (Burger Parity) | 30 | 30 | 7.540 | 0.5140 | 4.789 | SKIP — transit deferred |

Non-multi-country companions (no cross-country CV): hblok USB / DRAM global USD/MB — already landed.

## Takeaways

1. **Best new electronics numéraire:** Burger Parity **iPhone 15** (CV≈0.19, p90/p10≈1.41, 30 countries) —
   tighter than Big Mac in the same reference file (CV≈0.23).
2. **Best new digital standardized price:** **Netflix** (CV≈0.23) — close to Big Mac; global menu pricing.
3. **Best Numbeo branded “durable/apparel”:** **Nike mid-range shoes** (CV≈0.25, 102 countries) and
   **Zara/H&M dress** (CV≈0.28) — both tighter than Numbeo cars or McMeal.
4. **Cars:** Numbeo VW Golf / Corolla crowd levels are usable but **not** especially stable (CV≈0.48);
   Singapore (and similar tax/COE regimes) inflate the right tail — ex-SGP CV falls to ~0.30–0.33.
   Still absolute multi-country levels; keep as vehicle companion, not top numéraire.
5. **Starbucks latte** (already landed) remains a strong food-service companion (CV≈0.21).
6. **Spotify** looks worse than Netflix (CV≈0.49) — regional pricing; do not treat as stable numéraire.
7. **USB/DRAM (hblok)** are global USD technology curves, **not** cross-country parity series.

## New panels landed this pass (+4 → 130 top-level `*_panel.csv`)

| Panel | Rows | ISO3 | CV | p90/p10 |
|---|---:|---:|---:|---:|
| `iphone_15_burgerparity_panel.csv` | 30 | 30 | 0.191 | 1.413 |
| `netflix_standard_burgerparity_panel.csv` | 30 | 30 | 0.229 | 1.926 |
| `numbeo_nike_shoes_crowd_panel.csv` | 102 | 102 | 0.246 | 1.812 |
| `numbeo_zara_hm_dress_crowd_panel.csv` | 102 | 102 | 0.278 | 2.041 |

Machine-readable copy of the ranking table: `notes/stable_xcountry_durables_dispersion_2026-10-25.csv`.

## SKIP / not opened

| Item | Why |
|---|---|
| Numbeo refrigerator / TV / motorcycle / generic appliances | **Absent** from public `country_price_rankings` catalog (55 items; vehicles stop at Golf/Corolla) |
| Public transit fares (Numbeo ticket/pass; Uber 5km) | User deferred — high country-specific variation |
| Eurostat `PRC_HICP_AP` average prices | Dataset **not available** for dissemination (404) |
| Eurostat/OECD HICP·CPI durables indices | Already landed earlier; **indices ≠ level parity** — excluded from CV ranking |
| iPhone continuous multi-year MSRP | Forced dig; prior product-pass SKIP stands |
| IKEA Billy | Prior SKIP |
| Spotify panel | Screened; high CV from regional pricing — not a “stable” land |
| Cinema / gym Numbeo | CV≈0.48–0.49 — not competitive as numéraire |
| World Bank ICP PLI durables/machinery | Leave to Season2 unless already in Aoi gaps |
| NSO named-retail household SKUs | Season2 #118 |
| Big Mac absolute pack | Season2 |
| FX fills for local-only series | Policy: skip rather than invent FX |

## Season2 handoffs

- If **NSO absolute** prices for named appliances (fridge, washer, TV), motorcycles, or new-car MSRP
  (non-crowd) are wanted next: Season2 lane on #118-style named-retail — Aoi will not start those digs.
- ICP 2021 PLI for machinery/equipment / durable goods: Season2 if pursued.
- Food staple / Big Mac absolute densify: remains Season2.

## Provenance

- Burger Parity bulk CSV: `raw/stable_durables_2026-10-25/burgerparity_all.csv`
- Numbeo catalog: `raw/stable_durables_2026-10-25/numbeo_rankings_main.html`
- Nike/dress rows: extracts from prior `raw/specific_products_2026-10-25/numbeo/item_{64,62}.html`



## Follow-up 2026-10-25 (user chose ranks 1–5)

- Core inventory: `notes/numeraire_core_1to5_2026-10-25.md` (#4 Big Mac = Season2).
- **iPhone historical / multi-model** landed (Aoi): see `notes/iphone_historical_coverage_2026-10-25.md`
  and `iphone_models_xcountry_panel.csv` (+ companions). Prior SKIP on continuous MSRP stands for
  login-gated weekly series; easy multi-model snapshots + launch tables taken instead.
- **Netflix plan historical:** Season2 owns after split update — Aoi does not land plan-history panels.
