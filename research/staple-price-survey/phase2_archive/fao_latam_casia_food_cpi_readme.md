# FAOSTAT monthly Food CPI — LatAm / Central Asia / MENA-thin companion

## Panel
- File: `fao_latam_casia_food_cpi_panel.csv`
- Rows: 10,444
- ISO3 (33): ARG, ARM, AZE, BOL, BRA, CHL, COL, CRI, DOM, DZA, ECU, GEO, GTM, HND, HTI, IRN, IRQ, JAM, JOR, KAZ, KGZ, LBN, MEX, NIC, PAN, PER, PRY, SLV, TJK, TTO, URY, UZB, VEN
- Span: 2000-01-01 → 2026-06-01 (monthly)
- Series: Food Indices (2015=100), FAOSTAT domain CP

## Coverage
         region_group iso3                            country   n       dmin       dmax
central_asia_caucasus  ARM                            Armenia 318 2000-01-01 2026-06-01
central_asia_caucasus  AZE                         Azerbaijan 318 2000-01-01 2026-06-01
central_asia_caucasus  GEO                            Georgia 318 2000-01-01 2026-06-01
central_asia_caucasus  KAZ                         Kazakhstan 318 2000-01-01 2026-06-01
central_asia_caucasus  KGZ                         Kyrgyzstan 318 2000-01-01 2026-06-01
central_asia_caucasus  TJK                         Tajikistan 318 2000-01-01 2026-06-01
central_asia_caucasus  UZB                         Uzbekistan 318 2000-01-01 2026-06-01
      latam_caribbean  ARG                          Argentina 318 2000-01-01 2026-06-01
      latam_caribbean  BOL   Bolivia (Plurinational State of) 318 2000-01-01 2026-06-01
      latam_caribbean  BRA                             Brazil 318 2000-01-01 2026-06-01
      latam_caribbean  CHL                              Chile 318 2000-01-01 2026-06-01
      latam_caribbean  COL                           Colombia 318 2000-01-01 2026-06-01
      latam_caribbean  CRI                         Costa Rica 318 2000-01-01 2026-06-01
      latam_caribbean  DOM                 Dominican Republic 318 2000-01-01 2026-06-01
      latam_caribbean  ECU                            Ecuador 318 2000-01-01 2026-06-01
      latam_caribbean  GTM                          Guatemala 318 2000-01-01 2026-06-01
      latam_caribbean  HND                           Honduras 318 2000-01-01 2026-06-01
      latam_caribbean  HTI                              Haiti 318 2000-01-01 2026-06-01
      latam_caribbean  JAM                            Jamaica 318 2000-01-01 2026-06-01
      latam_caribbean  MEX                             Mexico 318 2000-01-01 2026-06-01
      latam_caribbean  NIC                          Nicaragua 288 2000-01-01 2023-12-01
      latam_caribbean  PAN                             Panama 318 2000-01-01 2026-06-01
      latam_caribbean  PER                               Peru 318 2000-01-01 2026-06-01
      latam_caribbean  PRY                           Paraguay 318 2000-01-01 2026-06-01
      latam_caribbean  SLV                        El Salvador 318 2000-01-01 2026-06-01
      latam_caribbean  TTO                Trinidad and Tobago 318 2000-01-01 2026-06-01
      latam_caribbean  URY                            Uruguay 318 2000-01-01 2026-06-01
      latam_caribbean  VEN Venezuela (Bolivarian Republic of) 298 2000-01-01 2024-10-01
            mena_thin  DZA                            Algeria 318 2000-01-01 2026-06-01
            mena_thin  IRN         Iran (Islamic Republic of) 318 2000-01-01 2026-06-01
            mena_thin  IRQ                               Iraq 318 2000-01-01 2026-06-01
            mena_thin  JOR                             Jordan 318 2000-01-01 2026-06-01
            mena_thin  LBN                            Lebanon 318 2000-01-01 2026-06-01

## Source
- Bulk: https://fenixservices.fao.org/faostat/static/bulkdownloads/ConsumerPriceIndices_E_All_Data_(Normalized).zip
- Portal: https://www.fao.org/faostat/en/#data/CP
- Local raw (reused): `raw/asia_food_subgroups/idn_bps/fao_cpi/ConsumerPriceIndices_E_All_Data_(Normalized).csv`
- Retrieved (tidy): 2026-10-24

## Non-overlap / lane notes
- Excludes ISO3 already in asia_national / africa_mena / china / fao_idn_phl_vnm / fao_thin_asia_africa packs.
- **Non-exclusive** companion tidy of the same open FAOSTAT CP bulk. Season2 owns LatAm CPI *holes* (Banxico/INEGI avoided) and FAO country CPI *bulk* — this is a documented Aoi companion extract, not those lanes.
- No COICOP mid-tree. No FX. No fabrication.
