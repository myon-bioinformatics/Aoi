# adjacent_euz_proxy_staple_levels — EA NSO absolute staple retail (EUZ gap proxies)

Retrieved: 2026-10-24 Asia/Tokyo

Sibling pack to `adjacent_hi_staple_levels`. These are **national** absolute average retail / unit-value staple prices used as **country ISO3 proxies for the euro-area (EUZ) Big Mac gap**. There is **no fake EUZ aggregate row**.

## Hard rules

- Absolute prices in **local currency as published** (EUR / historical IEP for Ireland CPM08).
- No FX conversion; no unit/pack homogenization; no gap-fill.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Every EA-country `note` states the series is a **national proxy for the EUZ gap**, not a euro-area aggregate.
- Never HICP/CPI indices.

## Coverage (hits)

| ISO3 | Rows | Series (examples) | Source | Span (approx.) |
|------|------|-------------------|--------|----------------|
| **FRA** | 1821 | baguette_kg (monthly+annual), potato ware/new, pasta_500g (stopped), parisian bread (stopped) | INSEE BDM *Prix moyens de vente de détail* (SDMX) | ~1992–2026-09 |
| **IRL** | 2618 | bread 800g/400g, flour 2kg ×3, potato packs, spaghetti 500g | CSO PxStat CPM08 (IEP) + CPM04 + CPM12 (EUR) National Average Price | 1997–2026-09 |
| **NLD** | 86 | bread_loaf, rice_kg, potato_kg (+ 2024–25 supermarket potato) | CBS 80345eng (to 2018) + maatwerk Agro-Nutri Monitor xlsx | 1999–2018; potato 2024–2025 |
| **ESP** | 76 | rice_kg, bread_kg, flour_cereals_kg, pasta_couscous_kg, potato_kg | INE jaxiT3 **25169** (+ **73844** 2024–25 extension) household *valor unitario* | 2006–2025 |

**Total rows: 4601.** Build: `build_euz_proxy_staple_levels.py`. Stats: `_build_stats.json`.

## Misses / exhausted (this turn)

See `missing.md`: DEU, ITA, SWE (deepen), BEL, AUT, FIN, PRT — open absolute retail bulk not secured (CPI/HICP or login/SPA only).

## Notes

- **FRA**: Metropolitan France average consumer prices from CPI price collection; pack sizes in `variable`/`unit`. Annual series emitted as `*_annual` so they do not overwrite monthly.
- **IRL**: Three NAP tables chained (IEP→EUR). CPM08 staples are IEP only through 2001-11; CPM04/CPM12 are Euro. Item labels kept as published.
- **NLD**: 80345eng unit is euro as published by CBS (includes CBS euro conversion of earlier guilder years); builder keeps **1999+** only. Maatwerk adds Regulier Unit Value potatoes 2024–2025.
- **ESP**: *Valor unitario* = expenditure/quantity from the household budget survey (EPF) — absolute EUR/kg, **not** a CPI store quote and **not** an index. Notes say so.
- **Out of scope here**: Aoi lanes (`hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS, ABS CPI); StatCan/CAN/DNK/NOR retries.

## Files

- `adjacent_euz_proxy_staple_levels_vertical.csv` (+ `.gz`)
- `build_euz_proxy_staple_levels.py`
- `_build_stats.json`
- `raw/insee/`, `raw/cso/`, `raw/cbs/`, `raw/ine/`, probes under `raw/destatis|istat|scb|misc/`
- Mirror: `/workspace/aoi-phase2/staple-price-survey/adjacent_euz_proxy_staple_levels/`
