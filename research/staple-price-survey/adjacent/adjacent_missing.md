# adjacent_missing.md

Retrieved: 2026-10-24 Asia/Tokyo

## A. ICP

- No ICP rows for **RUS**, **VEN** in source=90 pull (2017/2021).
- **EUZ**: no euro-area aggregate code accepted by ICP API (`EMU`/`EA`/`EUZ` failed).
- Some `AICZS` cells null (e.g. JPN 2021 FOOD 1101100) — dropped, not imputed.
- TWN: present in ICP pull (PLI / shares available).

## B. FAO CPI

- **No cereals / bread CPI** item in FAOSTAT CP domain (only Food Indices + Food price inflation + General).
- Use `adjacent_extra` NSO pack (`cpi_bread_cereals_nso`) for national bread/cereals CPI where needed.
- Some universe countries may lack Food CPI in FAOSTAT.

## C. Japan quintile

- Years ingested: **2018–2024** (年報 Excel). Pre-2018 not pulled this round (IDs/layout differ).
- Single-person households / 勤労者世帯-only tables not used (二人以上の世帯).
- Definition break vs Eurostat reinforcement quintile shares (see readme).

## D. FBSH / FBS Japan

- **FBS (2010–) Japan still absent** from FAOSTAT FBS bulk (0 rows for Area Japan / M49 392) — same gap as reinforcement.
- FBSH covers Japan **1961–2013** (included here).
- Post-2013 Japan Bennett kcal share needs another source (FBS gap).

## E. PIP / normative multipliers

- PIP has **no food-share / Engel** indicator — only poverty/welfare distributions.
- Interpolated PIP rows excluded (`is_interpolated=true`).
- **Normative poverty food-basket multipliers** (Orshansky-style N):
  - **USA**: already in `reinforcement/` (`orshansky` 3 and 3.7) — not duplicated here.
  - **Other countries**: no single clearly published official N found suitable to encode as rows without invention.
    Research notes (not data rows):
    - Historical US Orshansky: food share ≈1/3 → multiplier 3 (1960s); later USDA food plans imply ~3.7 for some updates.
    - Many high-income NSOs now use absolute baskets / AROP (60% median) rather than a food×N rule — no comparable N.
    - Japan public assistance (生活保護) uses a calculated minimum living cost, **not** a simple food×3 Engel inverse published as N.
    - If a country-specific official N is later confirmed with URL, add `poverty_food_multiplier` rows with note containing `NORMATIVE`.

## F. OECD / Eurostat long Engel

- OECD COICOP pull **missing JPN** (and several Big Mac Asia codes not in DF_TABLE5_T501 extract).
- Eurostat PC_TOT covers European geos + EA→EUZ; not global.
- Do not merge these with USDA ERS at-home food shares in the main survey without a definition note.

## Cross-cutting

- EUZ only when source has euro-area aggregate.
- No FX, no unit unify, no gap-fill.

### Countries with zero rows — A ICP

3: EUZ, RUS, VEN

### Countries with zero rows — B FAO CPI

2: EUZ, TWN

### Countries with zero rows — C Japan quintile

55: ARE, ARG, AUS, AZE, BHR, BRA, CAN, CHE, CHL, CHN, COL, CRI, CZE, DNK, EGY, EUZ, GBR, GTM, HKG, HND, HUN, IDN, IND, ISR, JOR, KOR, KWT, LBN, LKA, MDA, MEX, MYS, NIC, NOR, NZL, OMN, PAK, PER, PHL, POL, QAT, ROU, RUS, SAU, SGP, SWE, THA, TUR, TWN, UKR, URY, USA, VEN, VNM, ZAF

### Countries with zero rows — D FBSH

4: BHR, EUZ, QAT, SGP

### Countries with zero rows — E PIP

9: ARG, BHR, EUZ, HKG, KWT, NZL, OMN, SAU, SGP

### Countries with zero rows — F Engel TS

34: ARE, ARG, AZE, BHR, BRA, CHN, EGY, GTM, HKG, HND, IND, JOR, JPN, KOR, KWT, LBN, LKA, MDA, MYS, NIC, OMN, PAK, PER, PHL, QAT, SAU, SGP, THA, TWN, UKR, URY, VEN, VNM, ZAF

