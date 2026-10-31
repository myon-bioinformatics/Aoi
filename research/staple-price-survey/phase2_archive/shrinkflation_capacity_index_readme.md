# Shrinkflation capacity index panel

Built: 2026-10-24 (Asia/Tokyo). Derived from `shrinkflation_capacity_panel.csv` only — **no new wiki scrape**, no invented capacities.

## Rule

For each **product × capacity_unit** series (never mix `g` / `ml` / `count` within a ratio):

1. **Base** = undated baseline row if present; else earliest dated observation.
2. `capacity_index = 100 × capacity_value / base_capacity` (base → 100).
3. Series with **&lt; 2** observations in that unit are skipped (no meaningful ratio path).
4. No FX, no fills, no unit conversion.

## Files

| File | Description |
|---|---|
| `shrinkflation_capacity_index_panel.csv` | Event-level index rows |
| `shrinkflation_capacity_index_annual_median.csv` | Optional cross-section: annual median index across product×unit series that have a dated observation that year |
| `raw/shrinkflation/capacity_index_build_summary.json` | Build stats |

## Coverage (this build)

- Indexed rows: **2476**
- Product×unit series: **515** (products: **507**)
- Skipped series (&lt;2 obs or bad base): **7**
- Base kinds: {'first_dated': 335, 'undated_baseline': 180}
- Units in index panel: {'g': 1965, 'ml': 345, 'count': 166}
- Dated year span (annual median file): **1973–2026**

## Sparsity (annual median)

The annual median is **not** a dense CPI-like index. Most years have few product×unit series with an event date that year (wiki events are sparse). See `n_product_unit_series` and `sparsity_note` in the annual-median CSV. Prefer product-level `capacity_index` paths for analysis; use the cross-section only as a rough cohort signal.

## Columns (index panel)

`product_slug, product_name, manufacturer, category, date, year, capacity_value, capacity_unit, capacity_index, base_capacity, base_kind, base_date, base_year, pack_note, source_url, wiki_page, is_base`

- `base_kind`: `undated_baseline` | `first_dated`
- `is_base`: 1 for the observation that defines 100
