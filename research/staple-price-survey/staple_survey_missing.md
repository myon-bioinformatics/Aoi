# Missing-data report — staple survey (青いプロジェクト第2弾)

Retrieval: 2026-10-24 Asia/Tokyo

Country universe: user-supplied `bigmac_vertical.csv` (56 ISO3 codes including EUZ).

## A. Staple prices
- **Countries with ≥1 staple row:** 40 / 56
- **No staple prices obtained:** ARE, AUS, BHR, CAN, CHE, DNK, EUZ, HKG, KWT, MYS, NOR, NZL, OMN, QAT, SGP, TWN
- Reasons for gaps (typical): WFP/FPMA focus on food-security monitoring markets — many high-income Big Mac countries (e.g. ARE, AUS, BHR, CAN, CHE, DNK, HKG, KWT, NZL, OMN, QAT, SGP, SWE, TWN) have little or no domestic staple retail series in those dumps; USA covered via BLS; Japan via e-Stat + FPMA/WFP fragments.
- Units/currencies left as published (no FX, no unit homogenization).
- FPMA/WFP series thinned to **one market per (country, commodity, unit, price_type)** (longest series) to keep file usable; other markets exist upstream.

## B. Engel / food expenditure share
- **USDA ERS 2021–2025 food share:** 53 countries in universe
- **Not in USDA file (among universe):** EUZ, MDA, NIC
- Japan **is included** in USDA sheets (confirmed).
- USDA food column includes **nonalcoholic beverages**; title/definition = **consumed at home**.
- Longer Japan national household-survey Engel added separately as `engel_share_food_national_hh_survey` (definition break vs USDA — do not splice).
- USD expenditure columns in USDA file intentionally **not** used.

## C. Household consumption (LCU) + population
- **NE.CON.PRVT.CN:** 54 countries
- **SP.POP.TOTL:** 54 countries
- **Missing HH consumption:** EUZ, TWN
- EUZ (Euro area): present in Big Mac file; World Bank ISO3 country tables have no EUZ row — skipped for NE.CON.PRVT.CN / SP.POP.TOTL.
- Some economies (e.g. TWN, VEN in recent years) may have sparse WB values — empty cells not fabricated.

## Big Mac
- All rows from user `bigmac_vertical.csv` included as-is (`variable=bigmac_local_price`).

## Row counts (output)
- staple: 61157
- engel*: 554
- household_consumption_total_lcu: 1344
- population_total: 1404
- bigmac_local_price: 2056
- **total data rows:** 66515

## Notes on currencies appearing as USD outside USA
Some WFP/FPMA series for CRI, HND, NIC, VEN publish prices in **USD** (dollarized markets or WFP reporting currency). These were recorded as published — not converted by this survey.
