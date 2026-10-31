# Malaysia DOSM — CPI food & beverages subgroup tree

Built: 2026-10-24 (Asia/Tokyo). Companion Engel/staple collect; **price indexes**.

## Deliverable

- Panel: `mys_dosm_food_cpi_subgroup_panel.csv`
- Rows: **14553**
- Codes: **73** MCOICOP food-branch codes (division/group/class/subclass)
- Span: **1980-01 – 2026-09** (2d division 01 from 1980; 3d/4d/5d from 2010)
- Base: **2010=100**
- Levels: class_4d, division_2d, group_3d, subclass_5d

Richer than `asia_national_food_cpi_panel.csv` MYS coverage (div01 aggregate only + ADB annual CP01).

## Provenance

| field | value |
|-------|-------|
| source | DOSM Open Data CPI via storage.dosm.gov.my |
| datasets | cpi_2d / cpi_3d / cpi_4d / cpi_5d (food branch codes starting `01`) |
| labels | MCOICOP lookup (`mcoicop.csv` → `desc_en` / `desc_bm`) |
| catalogue | https://open.dosm.gov.my/data-catalogue/cpi_3d |
| raw | `raw/asia_food_subgroups/mys_dosm/` |
| retrieval_date | 2026-10-24 |

## Notes / gaps

1. Filter keeps MCOICOP codes starting with **01** (Food & Beverages). Alcohol (02) excluded.
2. No FX, no gap-fill, no rebasing.
3. Thailand MOC landed separately as **partial** tree (`tha_moc_food_cpi_subgroup_*`) after API 500/timeouts on most mid-codes.
