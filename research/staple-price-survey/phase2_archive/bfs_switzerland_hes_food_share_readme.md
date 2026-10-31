# Swiss BFS HABE — national food share of consumption expenditure

## Panel
- File: `bfs_switzerland_hes_food_share_panel.csv`
- Rows: 18
- ISO3: CHE
- Years: 2006–2023 (continuous annual)
- Primary variable: food_share_of_total_consumption_expenditure (%) = COICOP 51 / 50 Konsumausgaben

## Values
 year   value  food_chf_per_hh_month  consumption_chf_per_hh_month  food_share_of_gross_income_pct
 2006 12.2174                 627.37                       5135.04                          7.3368
 2007 11.8659                 638.03                       5377.02                          7.0257
 2008 12.3481                 655.78                       5310.77                          7.2038
 2009 12.2579                 658.79                       5374.39                          7.0316
 2010 11.9705                 658.17                       5498.24                          6.8424
 2011 12.0233                 648.54                       5393.98                          6.7527
 2012 11.5766                 638.02                       5511.31                          6.3402
 2013 11.7663                 644.90                       5480.90                          6.4158
 2014 11.8117                 641.58                       5431.74                          6.3655
 2015 12.2064                 617.24                       5056.66                          6.6623
 2016 12.1161                 612.72                       5057.06                          6.5030
 2017 12.2872                 622.61                       5067.14                          6.5869
 2018 12.2248                 616.00                       5038.96                          6.4433
 2019 12.6314                 621.79                       4922.56                          6.4948
 2020 14.2346                 665.05                       4672.06                          6.7504
 2021 14.3130                 663.74                       4637.32                          6.7858
 2022 12.7150                 629.21                       4948.53                          6.3381
 2023 12.6319                 637.76                       5048.77                          6.1674

## Source
- BFS Household Budget Survey (Haushaltsbudgeterhebung / HABE)
- Table T20.02.01.02.01 — Detaillierte Haushaltsausgaben sämtlicher Haushalte nach Jahr
- DAM asset https://dam-api.bfs.admin.ch/hub/api/dam/assets/36192843/master
- CHF monthly means; no FX

## Notes
- BFS published %-of-gross-income retained in `food_share_of_gross_income_pct`.
- Distinct from `swiss_bfs_food_cpi_panel` and `hi_staple_levels_alt` FOAG bread/flour.
- Income-class / region tables not pulled (Season2 food×income).
- Retrieved: 2026-10-24 (Asia/Tokyo)
