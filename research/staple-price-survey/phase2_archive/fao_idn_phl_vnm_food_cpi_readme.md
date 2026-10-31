# FAOSTAT CP — Indonesia / Philippines / Viet Nam monthly food CPI

Built: 2026-10-24 (Asia/Tokyo). Companion Engel/staple collect.

## Deliverable

- Panel: `fao_idn_phl_vnm_food_cpi_panel.csv`
- Rows: **1872**
- Geography: IDN, PHL, VNM
- Span: monthly **2000-01-01 – 2026-06-01**
- Series:
  - `food_cpi_index_fao_cp` — Food Indices, 2015=100
  - `food_cpi_yoy_fao_cp` — Food price inflation, % YoY
- **Richer than** `asia_national_food_cpi_panel` for these ISO3 (ADB annual CP01 only, 26 rows each).

## Provenance

| field | value |
|-------|-------|
| source | FAOSTAT Consumer Price Indices (domain CP) |
| bulk | `ConsumerPriceIndices_E_All_Data_(Normalized).zip` |
| page | https://www.fao.org/faostat/en/#data/CP |
| raw | `raw/asia_food_subgroups/idn_bps/fao_cpi/` |
| retrieval_date | 2026-10-24 |

## Notes / gaps

1. Aggregate **Food** index only — FAO CP domain has no COICOP mid-tree (cereals/meat/…) subgroups.
2. BPS Indonesia web/API 403; PSA OpenSTAT 403; GSO Vietnam TLS EOF — national NSO subgroup trees not landed.
3. **Non-exclusive:** Season2 owns FAO country CPI bulk lane; this is a narrow companion tidy for three ASEAN ISO3 asked this turn.
4. No FX. Flags retained in note when present (often `X` = base-year linked).
5. Distinct from global FFPI panel (`fao_food_price_index_panel.csv`).
