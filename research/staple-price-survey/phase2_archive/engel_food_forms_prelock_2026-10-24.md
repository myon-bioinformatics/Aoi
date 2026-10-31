# Prelock: Engel × food-share forms (no estimation)

Date: 2026-10-24 (Asia/Tokyo). **Forms only — do not claim results.**

## Intent (from user)

Want ratio/product objects that “hold”: when Engel moves, related **food-near** parts also move but the product/ratio stays within a bounded band. Housing dropped. Prefer food combinations (外食シェア, 穀類/Bennett). FAO calorie track later.

## Primary series (locked for next estimation step)

| choice | lock |
|--------|------|
| Household | 二人以上の世帯（農林漁家含む, 2000+） |
| Region | 全国 |
| Frequency | **annual** first (`engel_food_panel_annual.csv`) |
| Classification | **用途分類** levels from e-Stat longtime youto (statInfId=000040270657) |
| Engel E | published E_pct / E_fraction (食料/消費支出) |
| 外食 | aggregate **外食** (=一般外食+学校給食) unless sensitivity says otherwise |
| 穀類 | 用途「穀類」/「食料」 |
| 米 | optional secondary: 米/食料 or 米/穀類 |
| Housing | **out** |
| FAO kcal | **later** (scout only in readme) |
| FX | none |

Panel path: `/workspace/aoi-phase2/engel_food_panel_annual.csv` (2000–2025).

## Proposed forms (2–4)

### F1 — bounded product: Engel × eating-out share of CE

\[
b^{\mathrm{EO}}_{\mathrm{CE},t} = E_t \times s^{\mathrm{eo}}_{\mathrm{CE},t}, \quad
s^{\mathrm{eo}}_{\mathrm{CE},t} = \frac{\text{外食}_t}{\text{消費支出}_t}
\]

Rationale: user phrasing “エンゲル係数かける外食シェア（外食費に使われるお金）”. Natural money share of CE spent on eating-out scaled by food pressure E. Hypothesis to test later: \(b^{\mathrm{EO}}_{\mathrm{CE}}\) moves less than E or \(s\) alone (bounded product).

### F2 — within-food product: Engel × eating-out share of food

\[
b^{\mathrm{EO}}_{\mathrm{F},t} = E_t \times s^{\mathrm{eo}}_{\mathrm{F},t}, \quad
s^{\mathrm{eo}}_{\mathrm{F},t} = \frac{\text{外食}_t}{\text{食料}_t}
\]

Same intent with food-budget share. Note \(E \times s^{\mathrm{eo}}_{\mathrm{F}} = \text{外食}/\text{消費支出} = s^{\mathrm{eo}}_{\mathrm{CE}}\) **identically** when E=食料/CE and shares use the same 用途 levels — so F2 collapses to F1 under this definition. **Keep F1 as primary product; treat F2 as alias check, not a second claim.**

If a non-collapsing variant is wanted later: use **一般外食/食料** (exclude school lunch) × E, or 品目分類 shares × 用途 E (mixed def — document heavily).

### F3 — Bennett (cereals share of food vs E)

\[
s^{\mathrm{cer}}_{\mathrm{F},t} = \frac{\text{穀類}_t}{\text{食料}_t}
\quad\text{vs}\quad E_t
\]

Bennett’s law: as income rises (Engel falls), cereals’ share of food falls. Form to test later: negative co-movement of \(s^{\mathrm{cer}}_{\mathrm{F}}\) with real income / positive with E; optional level relation \(s^{\mathrm{cer}}_{\mathrm{F}} \approx c_0 + c_1 E\) (not fit now).

Optional companion: \(s^{\mathrm{rice}}_{\mathrm{F}} = \text{米}/\text{食料}\) or \(s^{\mathrm{rice}}_{\mathrm{cer}} = \text{米}/\text{穀類}\).

### F4 — optional bounded product: Engel × cereals share of food

\[
b^{\mathrm{cer}}_{t} = E_t \times s^{\mathrm{cer}}_{\mathrm{F},t}
\]

Parallel to F1 for staples: if E up and cereals share of food also up in stress periods, product may overstate; if they offset, product is the “bounded” object. Pre-declare only; no fit.

## Explicit non-claims

- No coefficient estimates, no stability test, no “holds” conclusion this memo.
- No FAO join yet.
- No housing forms.
- No use of GohanTrust rice/approval panels in these forms.
- 2020 COVID dip in 外食 is a known level shock — flag before any stability claim later.

## Next step (out of scope here)

After user OK: plot F1 and F3 series, pre-register a stability metric (e.g. band width of \(b^{\mathrm{EO}}_{\mathrm{CE}}\), or corr(\(s^{\mathrm{cer}}_{\mathrm{F}}, E\))), then estimate. Monthly sheet available if annual n is thin.
