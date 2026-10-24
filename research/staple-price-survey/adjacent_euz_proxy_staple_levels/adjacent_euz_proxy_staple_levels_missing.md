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
| DEU | **Exhausted (incl. HBS path).** Destatis open food CSV / GENESIS = CPI indices or branch price index. Public EVS tables publish **mean expenditure only** (no quantities → no unit values). Eurostat public HBS same (see below). |
| ITA | **Exhausted (incl. HBS path).** Istat Data Browser = NIC/FOI/IPCA indices; public HBS microdata exists but is restricted-use / not a published unit-value table. No national open absolute retail staple bulk. |
| SWE | **Exhausted deepen.** SCB PR0101 = KPI/HICP; Kap8T02 wrong products. |
| BEL | **Not secured.** BeStat lists “Prix moyens des produits… 13 derniers mois” (view `f303f73f-…`) but CSV/zip open-data URLs returned HTML/ fortification pages; no usable bulk download this turn. |
| AUT | **Not secured.** statistik.at search / open.data probe did not yield absolute retail staple download (CPI/HICP pages). |

## Eurostat HBS (goal 1) — MISS for unit values

Public Eurostat HBS datasets under `hbs_exp_*` / `hbs_str_*` / `hbs_car_*` are **mean expenditure / structure / household characteristics only**. TOC scan: **0** quantity or unit-value HBS tables. COICOP in `hbs_exp_t121` is expenditure (national currency / EUR / PPS), not kg. Scientific-use microdata (2010/2015/2020) is restricted — not used. Therefore **cannot** compute mean expenditure ÷ quantity from the public API for DEU/ITA/BEL/AUT/FIN/PRT.

## URLs tried (selected, this turn + prior)

- Eurostat HBS TOC: https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en
- Eurostat HBS DB: https://ec.europa.eu/eurostat/web/household-budget-surveys/database
- Eurostat `hbs_exp_t121` JSON: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hbs_exp_t121
- HBS ESMS: https://ec.europa.eu/eurostat/cache/metadata/en/hbs_esms.htm
- StatFin 011: https://statfin.stat.fi/PXWeb/api/v1/en/StatFin_Passiivi/khi/statfinpas_khi_pxt_011_201812.px
- StatFin current khi list: https://pxdata.stat.fi/PXWeb/api/v1/en/StatFin/khi/
- Observatório: https://observatorioagroalimentar.gov.pt/setor/{arroz,batata,trigo}/
- Observatório ajax: https://observatorioagroalimentar.gov.pt/wp-admin/admin-ajax.php (`get_periodo`, `get_produto_graph`)
- INE PT IPC search: https://www.ine.pt/xportal/xmain (IPC — index only)
- Destatis EVS food expenditure: https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Einkommen-Konsum-Lebensbedingungen/Konsumausgaben-Lebenshaltungskosten/Tabellen/pk-ngt-evs_D.html
- Statbel BeStat views + Prix moyens open-data paths (HTML/blocked)
- Statistik Austria search: Durchschnittspreise Lebensmittel
- Prior: INSEE / CSO / CBS / INE ES / Destatis GENESIS / Istat / SCB

## Intentionally skipped

- Eurostat `prc_fpmt_m` / HICP / PPP food PLI (indices)
- Farm-gate / agricultural unit values `aact_uv*` / `apri_ap` (not retail)
- Restricted HBS / Istat MFR microdata processing
- Aoi lanes and CAN/DNK/NOR/StatCan retries
- Redo of FRA/IRL/NLD/ESP
