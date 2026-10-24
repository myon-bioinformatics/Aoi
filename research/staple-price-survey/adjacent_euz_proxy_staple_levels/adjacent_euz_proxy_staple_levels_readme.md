# adjacent_euz_proxy_staple_levels — EA NSO absolute staple retail (EUZ gap proxies)

Retrieved: 2026-10-24 Asia/Tokyo

Sibling pack to `adjacent_hi_staple_levels`. These are **national** absolute average retail / unit-value staple prices used as **country ISO3 proxies for the euro-area (EUZ) Big Mac gap**. There is **no fake EUZ aggregate row**.

## Hard rules

- Absolute prices in **local currency as published** (EUR / historical IEP for Ireland CPM08).
- No FX conversion; no unit/pack homogenization; no gap-fill.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Every EA-country `note` states the series is a **national proxy for the EUZ gap**, not a euro-area aggregate.
- Never HICP/CPI indices; never PPP/PLI.

## Coverage (hits)

| ISO3 | Rows | Series (examples) | Source | Span (approx.) |
|------|------|-------------------|--------|----------------|
| **FRA** | 1821 | baguette_kg (monthly+annual), potato ware/new, pasta_500g (stopped), parisian bread (stopped) | INSEE BDM *Prix moyens de vente de détail* (SDMX) | ~1992–2026-09 |
| **IRL** | 2618 | bread 800g/400g, flour 2kg ×3, potato packs, spaghetti 500g | CSO PxStat CPM08 (IEP) + CPM04 + CPM12 (EUR) National Average Price | 1997–2026-09 |
| **NLD** | 86 | bread_loaf, rice_kg, potato_kg (+ 2024–25 supermarket potato) | CBS 80345eng (to 2018) + maatwerk Agro-Nutri Monitor xlsx | 1999–2018; potato 2024–2025 |
| **ESP** | 76 | rice_kg, bread_kg, flour_cereals_kg, pasta_couscous_kg, potato_kg | INE jaxiT3 **25169** (+ **73844** 2024–25 extension) household *valor unitario* | 2006–2025 |
| **FIN** | 1911 | rice 1kg, wheat flour 2kg, rye/mixed/wheat breads, baguette, macaroni 400g, spaghetti 500g, cooking potatoes | Statistics Finland StatFin_Passiivi **011** Average prices of commodities (EUR) | 2002–2018 (monthly + annual avg) |
| **PRT** | 606 | rice avg/carolino €/kg, wheat flour €/kg, spaghetti €/kg, potato €/kg, bread bolas carcaça €/unit | Observatório de Preços agroalimentar (Consumo stage; 4-week periods) | ~2019-P1–2026-P13 |
| **AUT** | 360 | rice_long_grain_kg, wheat_flour_kg, rye_bread_kg, wholemeal/white bread 500g, bread_roll_unit, pasta_500g, potato_kg | Statistik Austria **Preisradar** scanner mean (`data/ep/{id}.json` meanData) | 2023-01–2026-09 monthly |

**Total rows: 7478.** Build: `build_euz_proxy_staple_levels.py`. Stats: `_build_stats.json`.

New this turn (append): **AUT +360**. FRA/IRL/NLD/ESP/FIN/PRT unchanged.

## Misses / exhausted (this turn)

See `missing.md`. World Bank ICP public releases are PPP/PLI/expenditure only (documented under sibling `adjacent_icp_food_prices/` — **no** staple_price rows loaded). DEU/ITA remain exhausted (no new national open absolute retail bulk found). BEL skipped (fetched elsewhere). OGD Austria VPI/HVPI = indices; Preisradar absolute means used instead.

## Notes

- **FRA**: Metropolitan France average consumer prices from CPI price collection; pack sizes in `variable`/`unit`. Annual series emitted as `*_annual` so they do not overwrite monthly.
- **IRL**: Three NAP tables chained (IEP→EUR). CPM08 staples are IEP only through 2001-11; CPM04/CPM12 are Euro. Item labels kept as published.
- **NLD**: 80345eng unit is euro as published by CBS (includes CBS euro conversion of earlier guilder years); builder keeps **1999+** only. Maatwerk adds Regulier Unit Value potatoes 2024–2025.
- **ESP**: *Valor unitario* = expenditure/quantity from the household budget survey (EPF) — absolute EUR/kg, **not** a CPI store quote and **not** an index. Notes say so.
- **FIN**: NSO published average retail commodity prices (EUR) for named packs; not HBS unit values; current StatFin `khi` tree is index/fuel-only — food averages live in Passiivi archive table 011 through 2018.
- **PRT**: Observatório Consumo stage is consumer/retail absolute EUR; bread is **EUR per unit** (bolas carcaça) as published; date = 4-week period start. Not INE IPC and not HBS.
- **AUT**: Preisradar national scanner *Durchschnittspreise* (mean) since 2023-01 for ~100 CPI basket products; pack size in product title (kg / 500 g / 1 piece). Complementary index series in the same JSON are **not** loaded. French fries / potato chips skipped (not core staples).
- **Out of scope here**: Aoi lanes (`hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS, ABS CPI); StatCan/CAN/DNK/NOR retries; BEL redo.

## Files

- `adjacent_euz_proxy_staple_levels_vertical.csv` (+ `.gz`)
- `build_euz_proxy_staple_levels.py`
- `_build_stats.json`
- `raw/insee/`, `raw/cso/`, `raw/cbs/`, `raw/ine/`, `raw/statfin/`, `raw/ine_pt/`, `raw/statistik_at/`, `raw/eurostat_hbs/`, probes under `raw/destatis|istat|scb|misc/`
- Mirror: `/workspace/aoi-phase2/staple-price-survey/adjacent_euz_proxy_staple_levels/`
