# adjacent_household_sku_levels — NSO named-retail household SKUs

Retrieved: 2026-10-25 Asia/Tokyo

## Hard rules

- Absolute retail average prices in **local currency as published** (not CPI indices).
- No FX conversion; no unit/pack homogenization; no gap-fill; `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Gender SKUs as distinct `variable` names only (none in this first pack).

## Lane scope

Season2 owns **NSO named-retail** household SKUs for Big Mac ISO3 (+ EUZ proxies where applicable): underwear, towels, napkins/tissue, toilet paper, soap/detergent, coffee/tea.

**Not collected here (Aoi keeps / already landed — do not duplicate into #118):**

| Panel | ISO3 | Families already covered |
|-------|------|--------------------------|
| `aoi-phase2/japan_rps_everyday_clothing_household_panel.csv` | JPN | towel, tissue, toilet paper, detergents/soaps, underwear (gender vars), sanitary napkin, shampoo, … |
| `aoi-phase2/japan_retail_price_oil_sugar_coffee_panel.csv` | JPN | instant coffee |
| `aoi-phase2/uk_ons_avg_retail_household_clothing_panel.csv` | GBR | tea bags, instant coffee, bath towel, kitchen roll, washing detergent, tissues, liquid soap, shampoo, bra, women's pants, … |
| `aoi-phase2/bls_us_everyday_product_prices_panel.csv` | USA | ground coffee (APU) |

This pack adds **other** NSO absolute retail series not in those panels.

## Coverage (this pack)

| ISO3 | Series (prefix `household_sku:`) | Source | Span (approx.) |
|------|----------------------------------|--------|----------------|
| **SGP** | `coffee_instant_200g`, `laundry_liquid_detergent_kg`, `toilet_paper_10rolls` | SingStat M213761 Average Retail Prices | coffee 2015-01–2026-09; detergent & toilet paper 2024-01–2026-09 |
| **MYS** | tea (Teh Boh / Lipton), coffee powder (Kapal Api / Hang Tuah / Tenom), dish soap, laundry powder, body soap, tissue (sparse) | DOSM PriceCatcher monthly premise **mean** | 2022-01–2026-09 (item-dependent) |
| **IRL** | `tea_bags_80` | CSO PxStat CPM12 National Average Price | 2012-01–2026-09 |
| **QAT** | bath soap Lux, instant coffee Nescafe, loose tea, tea bags Lipton, shampoo H&S, laundry detergent Ariel (2017 only) | data.gov.qa annual average consumer prices (selected commodities) | 2017–2023 annual |

Build stats: see `_build_stats.json` (911 rows; countries IRL, MYS, QAT, SGP).

## Files

- `adjacent_household_sku_levels_vertical.csv` (+ `.gz`)
- `build_household_sku_levels.py`
- `_build_stats.json`
- `raw/` — SingStat JSON, DOSM monthly means, CSO tea extract, Qatar annual extract
- `adjacent_household_sku_levels_missing.md` — probes / dead-ends / deferred

## Notes

- **MYS**: PriceCatcher is premise-level; pack uses monthly mean of positive prices for fixed `item_code`s. Not a CPI. Tissue Kleenex has only 1 month (kept, sparse).
- **SGP**: Detergent & toilet paper enter the published basket from 2024-01 (2024-based CPI basket note on table).
- **QAT**: Annual averages; commodity spelling variants collapsed by mean within year×variable.
- **IRL**: Tea bags only from CPM national average price tables; no toilet paper / detergent absolute series in CPM04/08/12.
