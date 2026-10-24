# adjacent_euz_proxy_staple_levels — missing / blocked

Retrieved: 2026-10-24 Asia/Tokyo

## Priority targets

| ISO3 | Status |
|------|--------|
| **FRA** | **HIT** — INSEE BDM Prix moyens (baguette, potatoes, pasta/parisian stopped). |
| **IRL** | **HIT** — CSO CPM08/CPM04/CPM12 National Average Price. |
| **NLD** | **HIT** — CBS 80345eng (to 2018) + 2024–25 maatwerk potatoes. |
| **ESP** | **HIT** — INE valor unitario tables 25169 + 73844 extension. |
| **FIN** | **HIT** — StatFin_Passiivi table 011 Average prices of commodities (EUR), 2002–2018 monthly+annual; rice/flour/breads/pasta/potatoes. Current StatFin `khi` has no post-2018 food average-price table (indices + liquid fuels only). |
| **PRT** | **HIT** — Observatório de Preços agroalimentar Consumo absolute € (rice, flour, spaghetti, potato, bread unit), ~2019–2026 4-week periods via admin-ajax. INE Portugal open DB is IPC/index-only for food. |
| **AUT** | **HIT** — Statistik Austria Preisradar scanner mean EUR (`https://www.statistik.at/preisradar/data/ep/{id}.json`); rice/flour/breads/pasta/potato; 2023-01–2026-09 monthly. Open Data portal food holdings remain VPI/HVPI **indices** (exhausted as absolute). |
| DEU | **HIT** — BMEL-Statistik 5050850 annual consumer EUR (Vollkornbrot/Roggenmischbrot/Weizenmehl/Speisekartoffeln) + 5051000 Alle LEH bread/potato; rice/pasta absent; Destatis www ERR_CONNECTION_CLOSED; GENESIS no food Durchschnittspreise. |
| ITA | **Exhausted.** ISTAT esploradati/dati.gov.it/istat.it prices theme = NIC/FOI/IPCA indices or expenditure; Genova city-only skipped; osservaprezzi.it cert fail (fuel observatory); MIMIT ERR_CONNECTION_CLOSED. No national absolute EUR staple retail open bulk (2026-10-24). |
| SWE | **Exhausted deepen.** SCB PR0101 = KPI/HICP; Kap8T02 wrong products. |
| BEL | **Skipped this turn** (browser fetch elsewhere). Prior open-data path: CPI/HICP only. |

## World Bank ICP — MISS for staple_price (sibling pack)

Public ICP DataBank / API (sources 62=2011, 78=2017, 90=2021) and the published ICP 2011 results workbook expose **PPP, PLI, expenditure** at basic-heading level (e.g. Bread and cereals). **No** national annual average item prices in LCU are in the open release. Item-level average prices require a formal World Bank ICP data request — **not** loaded as `staple_price`. See `/workspace/staple-price-survey/adjacent_icp_food_prices/` (docs + raw probes only; zero vertical rows).

## Eurostat HBS — MISS for unit values

Public Eurostat HBS datasets under `hbs_exp_*` / `hbs_str_*` / `hbs_car_*` are **mean expenditure / structure / household characteristics only**. TOC scan: **0** quantity or unit-value HBS tables. Scientific-use microdata restricted — not used.

## URLs (selected)

- Preisradar app: https://www.statistik.at/preisradar/
- Preisradar products: https://www.statistik.at/preisradar/data/ep/products.json
- Preisradar series: https://www.statistik.at/preisradar/data/ep/{id}.json (e.g. 001900 rice, 002000 flour, 000600 rye bread, 011800 potatoes, 002100 pasta)
- Statistik Austria OGD catalog (VPI/HVPI indices only for food)
- WB ICP data: https://www.worldbank.org/en/programs/icp/data
- WB API sources: `https://api.worldbank.org/v2/indicator?source={62,78,90}&format=json&per_page=100`
- ICP 2011 results xlsx (PPP/PLI/expenditure tables): archived WB download (local `adjacent_icp_food_prices/raw/ICP_2011_results.xlsx`)
- Eurostat HBS TOC / `hbs_exp_t121`
- StatFin 011 / Observatório / INSEE / CSO / CBS / INE ES (prior hits)
- Destatis EVS / GENESIS; Istat prezzi; govdata.de

## Intentionally skipped

- Eurostat `prc_fpmt_m` / HICP / PPP food PLI (indices)
- Farm-gate / agricultural unit values `aact_uv*` / `apri_ap` (not retail)
- Restricted HBS / Istat MFR microdata; ICP item-price application workflow
- Aoi lanes; BEL redo; city-only DEU/ITA regional quotes; French fries / chips from Preisradar
