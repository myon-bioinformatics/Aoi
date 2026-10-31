# DST Denmark HES — national food share of total expenditure

## Panel
- File: `dst_denmark_hes_food_share_panel.csv`
- Rows: 10
- ISO3: DNK
- Years: 2015–2024
- Variable: food_share_of_total_expenditure (percent)
- Formula: COICOP 01 / 00 FORBRUG I ALT × 100 (current prices, DKK per household)

## Values
 year   value  food_dkk_per_hh  total_dkk_per_hh
 2015 11.8613            36602            308583
 2016 12.1354            36299            299116
 2017 12.0531            36898            306129
 2018 11.9980            38602            321737
 2019 11.7434            37961            323254
 2020 12.2461            39029            318706
 2021 11.5278            38427            333341
 2022 11.6187            41354            355926
 2023 11.2455            42086            374247
 2024 11.1001            41851            377034

## Source
- Statistics Denmark StatBank FU12 — Husstandenes gennemsnitlige forbrug
- API https://api.statbank.dk/v1/data ; table https://www.statbank.dk/FU12
- Price unit AARPRIS (løbende priser)

## Notes
- Share % is the Engel companion; DKK levels retained as provenance (no FX).
- Distinct from `dst_denmark_food_cpi_panel.csv` (CPI indexes).
- FU15 income bands not pulled (Season2 food×income).
- Retrieved: 2026-10-24 (Asia/Tokyo)
