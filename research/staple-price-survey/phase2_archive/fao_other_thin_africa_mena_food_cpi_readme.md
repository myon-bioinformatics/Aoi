# FAOSTAT monthly Food CPI — other_thin Africa / MENA / Asia leftovers

## Panel
- File: `fao_other_thin_africa_mena_food_cpi_panel.csv`
- Rows: 14,914
- ISO3 (49): AFG, AGO, ARE, BDI, BEN, BFA, BHR, BRN, BTN, CAF, COD, COG, COM, CPV, DJI, GAB, GIN, GMB, GNB, GNQ, KWT, LBR, LBY, LSO, MDG, MDV, MLI, MRT, MUS, MWI, NAM, NER, OMN, PSE, QAT, RWA, SDN, SLE, SOM, SSD, STP, SWZ, SYC, SYR, TCD, TGO, YEM, ZMB, ZWE
- Span: 2000-01-01 → 2026-06-01
- Series: Consumer Prices, Food Indices (2015 = 100)

## Coverage
   region_group iso3                          country   n
africa_leftover  AGO                           Angola 318
africa_leftover  BDI                          Burundi 318
africa_leftover  BEN                            Benin 318
africa_leftover  BFA                     Burkina Faso 317
africa_leftover  CAF         Central African Republic  78
africa_leftover  COD Democratic Republic of the Congo 206
africa_leftover  COG                            Congo 318
africa_leftover  COM                          Comoros 318
africa_leftover  CPV                       Cabo Verde 318
africa_leftover  DJI                         Djibouti 318
africa_leftover  GAB                            Gabon 318
africa_leftover  GIN                           Guinea 318
africa_leftover  GMB                           Gambia 318
africa_leftover  GNB                    Guinea-Bissau 318
africa_leftover  GNQ                Equatorial Guinea 318
africa_leftover  LBR                          Liberia 318
africa_leftover  LSO                          Lesotho 318
africa_leftover  MDG                       Madagascar 316
africa_leftover  MLI                             Mali 318
africa_leftover  MRT                       Mauritania 318
africa_leftover  MUS                        Mauritius 318
africa_leftover  MWI                           Malawi 318
africa_leftover  NAM                          Namibia 318
africa_leftover  NER                            Niger 318
africa_leftover  RWA                           Rwanda 318
africa_leftover  SDN                            Sudan 222
africa_leftover  SLE                     Sierra Leone 318
africa_leftover  SOM                          Somalia 318
africa_leftover  SSD                      South Sudan 222
africa_leftover  STP            Sao Tome and Principe 318
africa_leftover  SWZ                         Eswatini 318
africa_leftover  SYC                       Seychelles 318
africa_leftover  TCD                             Chad 318
africa_leftover  TGO                             Togo 317
africa_leftover  ZMB                           Zambia 318
africa_leftover  ZWE                         Zimbabwe 318
  asia_leftover  AFG                      Afghanistan 318
  asia_leftover  BRN                Brunei Darussalam 318
  asia_leftover  BTN                           Bhutan 318
  asia_leftover  MDV                         Maldives 318
  mena_leftover  ARE             United Arab Emirates 318
  mena_leftover  BHR                          Bahrain 318
  mena_leftover  KWT                           Kuwait 318
  mena_leftover  LBY                            Libya 318
  mena_leftover  OMN                             Oman 318
  mena_leftover  PSE                        Palestine 318
  mena_leftover  QAT                            Qatar 318
  mena_leftover  SYR             Syrian Arab Republic 306
  mena_leftover  YEM                            Yemen 210

## Source
- FAOSTAT CP bulk (local reuse)
- Deferred from `fao_thin_pacific_ee_caribbean` turn (other_thin slice)
- Excludes ISO3 already in asia / africa_mena / china / fao_idn / fao_thin / fao_latam / fao_thin_pacific packs
- Non-exclusive vs Season2 FAO country CPI bulk

## Notes
- No FX. No fabrication. Geos with &lt;24 monthly observations dropped.
- Retrieved: 2026-10-24 (Asia/Tokyo)
