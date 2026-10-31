# Engel × food-shares panel — Japan **単身世帯** (annual)

Built: 2026-10-24 (Asia/Tokyo). Distinct from `engel_food_panel_annual.csv` / monthly (二人以上の世帯).

## Deliverable

- Panel: `engel_food_panel_single_annual.csv`
- Coverage: **2001–2024** (24 continuous calendar years), 単身世帯・全国
- Classification: **用途分類** (yearbook 表1-1 実数), 年平均1か月間・円/世帯
- E: computed as 食料/消費支出（用途）. `E_pct_published` filled only when the sheet prints エンゲル係数.

## Why not the same longtime Excel as 二人以上?

e-Stat **長期時系列表** table 2（用途・月/四半期/年）is **二人以上の世帯 only**.  
For 単身世帯, longtime table 6 is **品目分類・年次** only (`statInfId=000040270666`, kept under `raw/engel_food/single/` as reference — **not** merged into this 用途 panel).  
単身の家計収支は統計局方針どおり **四半期・年**が主（月次の用途長表なし）→ **annual** deliverable.

## Sources (stitched; newer yearbook wins on overlap)

| file | statInfId | years in file |
|---|---|---|
| `raw/engel_food/single/youto_yb2008_1-1.xls` | 000002945656 | 2001–2008 |
| `raw/engel_food/single/youto_yb2012_1-1.xls` | 000021171428 | 2005–2012 |
| `raw/engel_food/single/youto_yb2016_1-1.xls` | 000031586385 | 2009–2016 |
| `raw/engel_food/single/youto_yb2020_1-1.xls` | 000032106661 | 2013–2020 |
| `raw/engel_food/single/youto_yearbook2024_1-1.xls` | 000040297558 | 2017–2024 |

Listing roots: 家計調査 / 家計収支編 / 単身世帯 / 年報；長期時系列一覧は `raw/engel_food/single/longtime_list.html`.

## Columns

Aligned in spirit with the 二人以上 annual panel: E, eat-out / cereals / rice shares, yen levels, household=`単身世帯`.  
Extra: `bread_yen_month`, `noodles_yen_month`, `E_pct_published`, `source_label`, `statInfId`, `eatout_construction`.

No FX, no fills. Gaps in a component (e.g. school lunch) stay null; eat-out total is published 外食 when present, else sum of 一般外食+学校給食 only if **both** parts exist.

## Monthly lane

**Stopped / not built:** no continuous monthly 用途 series for 単身 on e-Stat longtime (unlike 二人以上 `statInfId=000040270657`). Quarterly exists in detailed results but was out of this annual companion scope.
