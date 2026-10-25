# adjacent_extra_latam — gaps / missing

Retrieved: 2026-10-24 Asia/Tokyo

## Target gaps (food CPI)

| ISO3 | Status | Notes |
|------|--------|-------|
| GTM | closed | National División 01 (INE Empalme); product rice/pan short series 2025– |
| HND | closed | National Alimentos (BCH división Dic.2025=100); no open bread/cereals class in division file |
| NIC | closed | National Alimentos (INIDE); pan/cereales + arroz only through Jul 2019 in BCN Serie_Indice |
| PER | closed (regional) | **Lima Metropolitana** food & beverages via BCRP PN39445PM — not a national aggregate; national INEI Excel downloads were general CPI only |
| URY | closed | National División 01; 0111 + arroz from Oct 2022 detail file |

## Not collected (by design)

- Asia emerging CPI (IDN/THA/PHL/VNM/IND/KOR) — Aoi lane
- Japan CPI / Engel / rice retail — Aoi
- CoAHD, FAOSTAT producer prices, Pink Sheet, FFPI, IMF PCPS, USDA FES, OWID tidy — Aoi done
- Re-download of OECD/Eurostat already in `adjacent_extra/`
- FAOSTAT CPI bulk — other executor
- Existing LatAm deepen (ARG/BRA/CHL/COL/CRI/MEX bread) — left for a later pass

## Thin spots

- PER: no open bulk bread/cereals series found under BCRP PN39445 neighborhood; Lima food only
- HND: BCH rubros long file (LIBSERIE IPC RUBROS) returned HTTP 401; division series used instead (food only)
- NIC: bread/cereals and rice stop Jul 2019 in BCN file; post-2019 class breakouts only in monthly Cuadros (not bulk long panel)
- GTM: bread/cereals class not in Empalme División file; product DB starts 2025
