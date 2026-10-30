# adjacent_icp_food_prices — World Bank ICP probe (MISS for staple_price)

Retrieved: 2026-10-24 Asia/Tokyo

## Result

**No vertical `staple_price` rows loaded.** Public World Bank ICP releases (2011 / 2017 / 2021) provide **PPPs, price level indexes (PLI), and expenditures** at basic-heading / class level (e.g. Bread and cereals). They do **not** publish national annual average retail item prices in LCU for bread/rice/flour/potato.

Per Season2 rules: PPP/PLI (index vs numeraire) must **not** be loaded as `staple_price`. This sibling pack therefore holds **documentation + raw probes only** (no `*_vertical.csv`).

## What was checked

| Source | Content | Absolute LCU item/BH average prices? |
|--------|---------|--------------------------------------|
| WB API source **62** (ICP 2011) | 47 COICOP-ish heading indicators | No — headings for PPP/exp/PLI series |
| WB API source **78** (ICP 2017) | 47 headings incl. `1101110:Bread and cereals` | No — indicator unit empty; DataBank series are PPP/PLI/expenditure |
| WB API source **90** (ICP 2021) | 48 headings (same pattern) | No |
| ICP 2011 results workbook | Tables R*/D*/S*: expenditure, PPP (US$=1), PLI (world=100), real/nominal expenditures | **No** average price tables |
| WB ICP data portal | Public DataBank + publications | Item average prices require formal ICP data access request |

## Raw artifacts

- `raw/wb_ind{62,78,90}.json` — indicator lists from `api.worldbank.org/v2/indicator?source=`
- `raw/ICP_2011_results.xlsx` — published results (PPP/PLI/expenditure)
- `raw/icp_data_access.html`, `raw/icp_2017_databank.html` — portal snapshots

## URLs

- https://www.worldbank.org/en/programs/icp/data
- https://databank.worldbank.org/source/icp-2017
- https://databank.worldbank.org/source/icp-2021
- https://api.worldbank.org/v2/sources?format=json
- https://api.worldbank.org/v2/indicator?source=78&format=json&per_page=100

## Mirror

`/workspace/aoi-phase2/staple-price-survey/adjacent_icp_food_prices/`
