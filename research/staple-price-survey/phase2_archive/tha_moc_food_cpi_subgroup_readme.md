# Thailand MOC — CPI food subgroup indexes (partial)

Built: 2026-10-24 (Asia/Tokyo). Companion Engel/staple collect; **price indexes**.

## Deliverable

- Panel: `tha_moc_food_cpi_subgroup_panel.csv`
- Rows: **780**
- Series: all_items, food_nab, cereals_flour (3)
- Span: **2000-01 – 2024-12** monthly
- Base: as published (`base_year` field, typically 2019=100)
- Region: national (region_id=5)

Richer **frequency** than `asia_national_food_cpi_panel.csv` THA (ADB annual CP01 only, 26 rows). **Not** a full MOC food tree — API failures documented below.

## Provenance

| field | value |
|-------|-------|
| source | Thailand MOC Open Data `dataapi.moc.go.th/cpig-indexes` |
| index list | https://data.moc.go.th/Download/CPIIndex.csv |
| raw | `raw/asia_food_subgroups/tha_moc/` |
| retrieval_date | 2026-10-24 |

## Notes / gaps

1. Full food index list has ~food-branch codes (rice, meat, eggs, veg, meals-away, etc.) but most mid-code pulls returned **HTTP 500** or **timeouts** after food + cereals/flour succeeded. No fabrication / no gap-fill from other sources.
2. PSA Philippines OpenSTAT CPI folder **403**; not landed.
3. No FX.
