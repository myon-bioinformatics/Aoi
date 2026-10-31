# Cost of a Healthy Diet (CoAHD) panel

Date: **2026-10-24 Asia/Tokyo**

| Field | Detail |
|---|---|
| Panel | `coa_healthy_diet_panel.csv` |
| Raw | `raw/coa_fpn/Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).zip` |
| Source | FAOSTAT domain **CAHD** (Food Prices for Nutrition / CoAHD); July 2026 SOFI release |
| Bulk URL | https://bulks-faostat.fao.org/production/Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).zip |
| Landing | https://www.fao.org/faostat/en/#data/CAHD |
| Rows | 9,442 |
| Countries (ISO3) | 161 mapped; aggregates/unmapped kept with blank `iso3` |
| Years | 2017–2025 |
| Schema | iso3, year, indicator, value, unit, source_url, note |
| Key indicators | `cohd_lcu_per_cap_day`, `cohd_ppp_int_per_cap_day`, `pua_*`, `nua_*`, six food-group costs (LCU + PPP) |
| Rules | No FX by us; LCU and PPP kept as **separate published series**; missing stays missing |
| Big Mac universe | 52/56 ISO3 present (missing: EUZ, SGP, UKR, VEN) |

Companion Hub: World Bank https://www.worldbank.org/foodpricesfornutrition (Databank CSV blob missing at pull; FAOSTAT bulk preferred).
