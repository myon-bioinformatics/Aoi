# Engel companion QC — integrity pass

**Date:** 2026-10-25 (Asia/Tokyo)  
**Root:** `/workspace/aoi-phase2/`  
**Scope:** existing tidy panels only — **no new collects**

## Counts
| set | n |
|-----|--:|
| `*_panel.csv` | 85 |
| Japan engel extras (`engel_food_panel_*` / `engel_annual_*` outside glob) | 5 |
| **Total checked** | 90 |
| Integrity OK (header + ≥1 data row + time col; geo or by-design) | 90 |
| Hard anomalies | 0 |
| Soft notes (commodity/product panels, no country by design) | 8 |

## Hard anomalies
_None._ All checked files have a header and ≥1 data row; time dimension present.

## Soft notes (not failures)
Commodity / product / Japan domestic series without a country column — expected.
| file | note | data rows |
|------|------|----------:|
| `gohantrust_panel.csv` | no_geo_by_design | 11 |
| `pink_sheet_coffee_sugar_panel.csv` | no_geo_by_design | 4005 |
| `pink_sheet_food_extras_panel.csv` | no_geo_by_design | 12392 |
| `pink_sheet_vegetable_oils_panel.csv` | no_geo_by_design | 4961 |
| `pink_sheet_wheat_maize_panel.csv` | no_geo_by_design | 2175 |
| `rice_international_price_panel.csv` | no_geo_by_design | 2038 |
| `shrinkflation_capacity_index_panel.csv` | no_geo_by_design | 2476 |
| `shrinkflation_capacity_panel.csv` | no_geo_by_design | 2485 |

## Inventory cross-check (sample)
Inventory: `engel_companion_inventory_2026-10-24.md` table `| \`file\` | … | N |` claims vs actual data-row counts (CSV rows excluding header).

| file | actual rows | inventory claim | status |
|------|------------:|----------------:|--------|
| `faostat_food_trade_indices_panel.csv` | 197280 | 197280 | MATCH |
| `wdi_food_imports_pct_merchandise_panel.csv` | 8116 | 8116 | MATCH |
| `japan_retail_price_miso_shoyu_panel.csv` | 504 | 504 | MATCH |
| `faostat_food_production_index_qi_panel.csv` | 53421 | 53421 | MATCH |
| `wdi_cereal_yield_panel.csv` | 10632 | 10632 | MATCH |
| `wdi_food_production_index_panel.csv` | 11516 | 11516 | MATCH |
| `japan_retail_price_oil_sugar_coffee_panel.csv` | 696 | 696 | MATCH |
| `japan_retail_price_rice_panel.csv` | 720 | 720 | MATCH |
| `engel_food_panel_annual.csv` | 26 | 26 | MATCH |
| `engel_food_panel_monthly.csv` | 320 | 320 | MATCH |
| `engel_food_panel_single_annual.csv` | 24 | 24 | MATCH |
| `usda_psd_grains_panel.csv` | 29790 | 29790 | MATCH |
| `scb_sweden_food_cpi_panel.csv` | 43443 | 43443 | MATCH |
| `swiss_bfs_food_cpi_panel.csv` | 34323 | 34323 | MATCH |
| `insee_france_food_cpi_panel.csv` | 32874 | 32874 | MATCH |
| `pink_sheet_wheat_maize_panel.csv` | 2175 | 2175 | MATCH |

### Full inventory vs disk (among checked files)
- Count mismatches requiring correction: **0**
_None — all inventory row counts for files present on disk match actual data rows._

### Inventory table names not in this QC glob
(Not necessarily wrong — may be non-`*_panel.csv` companions or renamed; listed for awareness, n=5.)
| file (inventory) | claimed rows |
|------------------|-------------:|
| `country_maam_shrinkflation_series.csv` | 12 |
| `engel_global_ref_panel_stub.csv` | 6154 |
| `faostat_producer_prices_staples.csv` | 36627 |
| `shrinkflation_capacity_index_annual_median.csv` | 43 |
| `shrinkflation_capacity_products.csv` | 508 |

## Inventory update this pass
**None.** No clear count mismatch on disk panels vs inventory table claims.

## Verdict
**PASS** — integrity pass on 90 files; 0 hard anomalies; 0 inventory count mismatches.

## Method
- Encoding: UTF-8 with replace; `csv.reader` for header + row count
- Time required: column name contains year/date/period/month/time/ym
- Geo required unless Japan `japan_*`/`engel_*` or known commodity/product panel (Pink Sheet, rice intl, shrinkflation, gohantrust)
- No downloads; no schema rewrite
