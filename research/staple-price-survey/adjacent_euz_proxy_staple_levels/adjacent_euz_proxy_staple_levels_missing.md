# adjacent_euz_proxy_staple_levels — missing / blocked

Retrieved: 2026-10-24 Asia/Tokyo

## Priority targets

| ISO3 | Status |
|------|--------|
| **FRA** | **HIT** — INSEE BDM Prix moyens (baguette, potatoes, pasta/parisian stopped). |
| **IRL** | **HIT** — CSO CPM08/CPM04/CPM12 National Average Price. |
| **NLD** | **HIT** — CBS 80345eng (to 2018) + 2024–25 maatwerk potatoes. |
| **ESP** | **HIT** — INE valor unitario tables 25169 + 73844 extension. |
| DEU | **Exhausted this turn.** Destatis open food CSV / GENESIS retail pages are **CPI indices (2020=100)** or retail *price index* by branch — not absolute €/kg staples. GENESIS REST `catalogue/find` returned SPA HTML without guest absolute-price tables. Tried: `sonderauswertung-nahrungsmittel`, `verbraucherpreisindex_nahrungsmittel_getraenke_bv41.csv`, genesis find “average price food”. |
| ITA | **Exhausted this turn.** Istat Data Browser / HVD pages expose **NIC/FOI/IPCA indices** and producer prices; no national open absolute retail staple bulk found. Comune di Genova “Media prezzi al dettaglio” is **city-level only** (not used as national ITA). Tried: istat.it prezzi-al-consumo-dati; dati.istat.it redirect to esploradati. |
| SWE | **Exhausted deepen.** SCB PR0101 tree is KPI/HICP family only. Historical JO1901I/Kap8T02 “Konsumentpriser kr/100 kg” products are feed/milk/margarine — **not** rice/bread/flour/potato. No current Medelpriser food absolute open bulk. |
| BEL | **Not secured.** STATBEL open-data search probe returned catalogue HTML without an obvious absolute staple average-price dataset (2026-10-24). |
| AUT | **Not secured.** statistik.at CPI/HCI page 404/HTML without absolute retail staple download. |
| FIN / PRT | **Not pursued beyond priority** — no quick open absolute bulk identified this turn. |

## URLs tried (selected)

- INSEE family: https://www.insee.fr/fr/plan-du-site/famille-bdm/103157792
- INSEE SDMX: https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/{idbanks}
- CSO: https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/CPM12/CSV/1.0/en (also CPM04, CPM08)
- CBS: https://opendata.cbs.nl/ODataApi/OData/80345eng
- CBS maatwerk xlsx: https://www.cbs.nl/-/media/_excel/2026/25/consumentenprijzen_voor_agro-nutri_monitor_2026.xlsx
- INE: https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/25169.csv ; `73844.csv`
- Destatis: https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Verbraucherpreisindex/Tabellen/sonderauswertung-nahrungsmittel.html
- SCB: https://api.scb.se/OV0104/v1/doris/en/ssd/START/PR/PR0101 ; Kap8T02 under JO1901I
- Istat: https://www.istat.it/tavole-di-dati/prezzi-al-consumo-dati/

## Intentionally skipped

- Eurostat `prc_fpmt_m` / HICP / PPP food PLI (indices or comparatives — already documented in HI pack)
- Farm-gate `apri_ap`
- Aoi lanes and CAN/DNK/NOR/StatCan retries
