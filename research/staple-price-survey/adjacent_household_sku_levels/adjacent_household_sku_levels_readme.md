# adjacent_household_sku_levels — NSO named-retail household SKUs

Retrieved: 2026-10-25 Asia/Tokyo (hygiene sync; densify PAUSED)

## Hard rules

- Absolute retail average prices in **local currency as published** (not CPI indices).
- No FX conversion; no unit/pack homogenization; no gap-fill; `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Gender SKUs as distinct `variable` names only (none in this pack outside Aoi JPN/GBR panels).

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
| **FIN** | coffee 500g, tea bags 50g, machine dishwashing detergent 1kg, laundry detergent 1l, washing-up liquid 1l, general cleanser 1l, kitchen towel 4 rolls, toilet paper 8 rolls, sanitary towels 20 pcs | StatFin Passiivi / Average prices of commodities **011** (monthly) | ~2002–2018 monthly (item-dependent; laundry detergent shorter) |
| **AUT** | `coffee_beans` (500g), `coffee_pads_capsules`, `coffee_instant`, `tea_bags` | Statistik Austria Preisradar product `meanData` | 2023-01–2026-09 monthly |
| **NLD** | `coffee`, `tea` | CBS opendata 80345eng Consumer prices of food (Coffee_5, Tea_14) | 1999–2018 annual |
| **FRA** | `coffee_ground_250g_non_decaf`, `coffee_ground_250g_arabica` | INSEE BDM Prix moyens de vente de détail (idbank 000442545 / 000442546; série arrêtée) | 2012-01–2019-12 monthly (kept ≥2012; series run 1992–2019) |

Build stats: see `_build_stats.json` (3015 rows; AUT, FIN, FRA, IRL, MYS, NLD, QAT, SGP).

## Files

- `adjacent_household_sku_levels_vertical.csv` (+ `.gz`)
- `build_household_sku_levels.py`
- `_build_stats.json`
- `raw/` — SingStat, DOSM, CSO, Qatar, StatFin 011, AUT Preisradar, CBS 80345eng, INSEE BDM extracts
- `adjacent_household_sku_levels_missing.md` — probes / dead-ends / deferred

## Notes

- **MYS**: PriceCatcher is premise-level; pack uses monthly mean of positive prices for fixed `item_code`s. Not a CPI. Tissue Kleenex has only 1 month (kept, sparse).
- **SGP**: Detergent & toilet paper enter the published basket from 2024-01 (2024-based CPI basket note on table).
- **QAT**: Annual averages; commodity spelling variants collapsed by mean within year×variable.
- **IRL**: Tea bags only from CPM national average price tables; no toilet paper / detergent absolute series in CPM04/08/12.
- **FIN**: Monthly cells only (annual `M01-M12` averages dropped to avoid double-counting). Series ends 2018 with Passiivi table close.
- **AUT**: Preisradar catalogue has coffee/tea household SKUs only (no TP/detergent/towels/underwear in product list). Uses `price.meanData` (ms epoch, EUR).
- **NLD**: Food average-price table only; coffee/tea among household lane; series ends 2018.
- **FRA**: Ground coffee absolute retail only among lane families still in BDM; laundry powder / dishwasher powder séries arrêtées end 1998–99 (not loaded). No TP/tissue/tea/towels/underwear in famille Prix moyens.

## Tip hygiene / status (2026-10-25 Asia/Tokyo)

- **PAUSED** for further household SKU densify (tip ~7275b3c era; pack frozen at **3015** rows / **8** ISO3: AUT 180, FIN 1692, FRA 192, IRL 177, MYS 491, NLD 40, QAT 36, SGP 207).
- Schema header verified: `country,date,year,variable,value,unit,source,note,estimated_value`; all `estimated_value` empty; csv/gz match; **0** duplicate keys.
- Do **not** re-panel Aoi JPN RPS / UK ONS towels/underwear into this pack.
- No new country digs in this hygiene pass.
