# adjacent_hi_staple_levels — absolute staple retail prices (HI Big Mac gaps)

Retrieved: 2026-10-24 Asia/Tokyo

## Hard rules

- Absolute retail average prices in **local currency as published** (not CPI / HICP indices).
- No foreign-exchange conversion.
- No unit/pack homogenization (pack size kept in `variable` and/or `unit`).
- No gap-filling / interpolation.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value` (`estimated_value` empty).

## Lane scope (this pack)

**Active lane (this bot):** ARE, BHR, KWT, OMN, QAT, TWN, EUZ (+ keep HKG, MYS, NZL, SGP).

**Handed to Aoi** (`hi_staple_levels_alt`): AUS, CAN, CHE, DNK, NOR.

Original gap-16 universe still listed in `missing.md` for cross-lane tracking.

## Coverage (countries with ≥1 absolute staple series in this pack)

| ISO3 | Series | Source | Span (approx.) |
|------|--------|--------|----------------|
| **HKG** | `staple_price:rice_long_grain_kg`, `staple_price:rice_short_grain_kg` | HK C&SD Monthly Digest of Statistics Table 5.8 | annual + monthly through 2026-06 |
| **MYS** | rice_10kg, wheat_flour_kg, potato_kg, bread_400g, maize_flour_400g | DOSM PriceCatcher (monthly mean across premises) | 2022-01–2026-09 |
| **NZL** | rice_kg, wheat_flour_1_5kg, potato_kg, bread_700g, wheatmeal_bread_700g, pasta_500g | Stats NZ FPI weighted average retail (via figure.nz) | ~2006–2026 |
| **SGP** | rice_5kg, bread_400g | SingStat M213761 Average Retail Prices of Selected Items | 2015-01 onward |
| **QAT** | bread_700g, lebanese_bread_5pcs, wheat_flour_kg, wheat_flour_no1_kg, rice_5kg, rice_basmati_tilda_5kg, potato_kg | Qatar NPC / data.gov.qa annual average consumer prices (selected commodities) | 2017–2023 (as published) |
| **TWN** | rice_3kg, wheat_flour_kg, white_toast_loaf, potato_catty | NDC e-invoice midpoints (monthly); Taipei potato 元/台斤 | recent monthly (see notes) |

**Hit in this pack: 6** (HKG, MYS, NZL, QAT, SGP, TWN).  
**Active-lane closed this turn: QAT, TWN.**  
**Active-lane exhausted/blocked: ARE, BHR, KWT, OMN, EUZ.** See `missing.md`.

Build stats: `2385` rows; countries_with_series=['HKG', 'MYS', 'NZL', 'QAT', 'SGP', 'TWN'].

## Files

- `adjacent_hi_staple_levels_vertical.csv` (+ `.gz`)
- `build_hi_staple_levels.py`
- `_build_stats.json`
- `raw/` — SingStat JSON, DOSM months + lookup, HK MDS, NZ figure.nz, Qatar CSV, NDC/Taipei, Eurostat/GCC probes
- Mirror: `/workspace/aoi-phase2/staple-price-survey/adjacent_hi_staple_levels/` (light raw; full DOSM only in primary path)

## Eurostat (attempted; EUZ)

Open bulk for **absolute** retail food product prices was **not found**.  
`prc_fpmt_m` (Food Price Monitoring Tool) downloads successfully but units are only `I25` (index) / `RCH_*` (rates) — **not LCU levels**.  
Historical one-off Detailed Average Prices (`prc_dap*`, ~2008–2015) is discontinued and not an ongoing euro-area series — not loaded.  
`prc_fsc_*` codes 404 on the SDMX API; HICP annual is index/rates only.  
Agricultural absolute prices (`apri_ap`) are farm-gate, not retail — excluded.

## Notes on secured series

- **MYS**: PriceCatcher is premise-level; pack uses monthly **mean** of positive prices for fixed SKUs chosen by observation count. Not a CPI.
- **NZL**: figure.nz republishes Stats NZ “selected monthly weighted average prices”; values kept as NZD per published pack.
- **HKG**: rice only from Table 5.8 ($/kg).
- **SGP**: Premium Thai Rice per 5 kg; Wholemeal Bread per 400 g.
- **QAT**: Annual averages in QAR as published; pack sizes kept in `variable`/`unit` (700 g bread, 5-piece Lebanese bread, 1 kg flour/potato, 5 kg rice). Commodity spelling variants collapsed by substring match.
- **TWN**: NDC e-invoice midpoint monthly for rice 3 kg / flour kg / white toast; Taipei potato in 元 per 台斤 (catty). MOA RicepriceData still TLS-blocked (not used).
