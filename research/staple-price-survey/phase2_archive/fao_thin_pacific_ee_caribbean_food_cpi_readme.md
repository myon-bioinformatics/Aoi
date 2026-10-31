# FAOSTAT monthly Food CPI — Pacific / Europe-thin / Caribbean leftovers

## Panel
- File: `fao_thin_pacific_ee_caribbean_food_cpi_panel.csv`
- Rows: 11,754
- ISO3 (37): ALB, ATG, AUS, BHS, BIH, BLR, BLZ, BRB, CYP, DMA, EST, FJI, GRD, HRV, ISL, KIR, KNA, LCA, LTU, LVA, MDA, MKD, MLT, MNE, NCL, NZL, PNG, PYF, SLB, SUR, SVK, SVN, TLS, TON, VCT, VUT, WSM
- Span: 2000-01-01 → 2026-06-01
- Series: Consumer Prices, Food Indices (2015 = 100)

## Coverage by region_group
      region_group iso3                          country   n
caribbean_leftover  ATG              Antigua and Barbuda 318
caribbean_leftover  BHS                          Bahamas 318
caribbean_leftover  BLZ                           Belize 318
caribbean_leftover  BRB                         Barbados 318
caribbean_leftover  DMA                         Dominica 318
caribbean_leftover  GRD                          Grenada 318
caribbean_leftover  KNA            Saint Kitts and Nevis 318
caribbean_leftover  LCA                      Saint Lucia 318
caribbean_leftover  SUR                         Suriname 318
caribbean_leftover  VCT Saint Vincent and the Grenadines 318
       europe_thin  ALB                          Albania 318
       europe_thin  BIH           Bosnia and Herzegovina 318
       europe_thin  BLR                          Belarus 318
       europe_thin  CYP                           Cyprus 318
       europe_thin  EST                          Estonia 318
       europe_thin  HRV                          Croatia 318
       europe_thin  ISL                          Iceland 318
       europe_thin  LTU                        Lithuania 318
       europe_thin  LVA                           Latvia 318
       europe_thin  MDA              Republic of Moldova 318
       europe_thin  MKD                  North Macedonia 318
       europe_thin  MLT                            Malta 318
       europe_thin  MNE                       Montenegro 318
       europe_thin  SVK                         Slovakia 318
       europe_thin  SVN                         Slovenia 318
           pacific  AUS                        Australia 318
           pacific  FJI                             Fiji 318
           pacific  KIR                         Kiribati 318
           pacific  NCL                    New Caledonia 318
           pacific  NZL                      New Zealand 318
           pacific  PNG                 Papua New Guinea 306
           pacific  PYF                 French Polynesia 318
           pacific  SLB                  Solomon Islands 318
           pacific  TLS                      Timor-Leste 318
           pacific  TON                            Tonga 318
           pacific  VUT                          Vanuatu 318
           pacific  WSM                            Samoa 318

## Source
- FAOSTAT domain CP bulk (local reuse of open Normalized CSV)
- Non-exclusive companion tidy vs Season2 FAO country CPI bulk
- Excludes ISO3 already in asia / africa_mena / china / fao_idn / fao_thin / fao_latam_casia packs
- **Curated to** Pacific + Caribbean leftovers + Europe-thin; other leftover Africa/MENA/Asia Food Indices deferred (not fabricated)

## Notes
- No FX. No fabrication.
- Includes AUS/NZL FAO Food Indices as thin Pacific companions (distinct from ABS/NZ CPI index packs and HES share panels).
- Retrieved: 2026-10-24 (Asia/Tokyo)
