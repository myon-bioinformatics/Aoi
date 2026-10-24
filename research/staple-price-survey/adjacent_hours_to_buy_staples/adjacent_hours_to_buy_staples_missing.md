# missing — adjacent_hours_to_buy_staples

## Hits: 2 ISO3 · 240 rows

| ISO3 | rows | source |
|------|-----:|--------|
| DEU | 48 | BMEL-Statistik 5050900 (rye bread + potato minutes/kg) |
| BRA | 192 | DIEESE PNCBA São Paulo tempo de trabalho → min/kg (rice, flour, potato, bread) |

See `readme.md` and `_coverage_by_country.csv`.

## Probed / missed (no open official labour-minutes staple table loaded)

| ISO3 / source | status | notes |
|---------------|--------|-------|
| AUT Statistik Austria / OeNB Kaufkraftrechner | **MISS** | Search/landing pages open; no bulk «Arbeitsminuten je kg Brot» table. WIFO press / interactive calculators only — not a published NSO minutes series |
| CHE | **MISS** | No BFS open «Arbeitsminuten» staple table found this run |
| POL GUS | **MISS** | Prices-trade pages open; no minutes-of-work-to-buy staple table |
| CZE CZSO | **MISS** | Prices pages open; no labour-minutes staple indicator |
| FRA INSEE | **MISS** | No «minutes de travail pour acheter» bread/rice open table loaded |
| MEX INEGI | **MISS** | Direct temas URL failed from this egress; no open «tiempo de trabajo para adquirir» kg staple table |
| JPN e-Stat | **MISS / skip** | Query `購買力 分` returns no minutes-to-buy staple dataset; Japan **numeraire** lane is Aoi-owned — not DIY from wages÷prices |
| ILO October Inquiry / ILOSTAT | **MISS** | Historical inquiry is wage/price levels; absolute labour-minutes staple indicator not published as a ready table here (DIY out of scope). Old description PDF 404 |
| UBS Prices & Earnings / Statista | **SKIP** | Private / press compilations; not NSO; often DIY-style |
| GovData DEU «Preise und Löhne» | **SKIP** | Separate wage and price CSVs — not the designed minutes indicator (BMEL 5050900 used instead) |
| BRA IBGE | **N/A** | IBGE does not publish this indicator; DIEESE PNCBA used with clear non-NSO note |
| BRA DIEESE post-2015/2018 | **partial** | Product-level public HTML largely ends ~2015–2018 (403/404); later city summaries lack per-product tempo in open HTML |

## Intentional Aoi / Season2 skips

food CPI indexes, housing share, SGP/HKG CPI, USDA FPO, `hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS retail, CoAHD, KOR/TWN quintiles, Japan numeraire, food-share-by-income, eating-out packs.

## Rule reminder

Do **not** invent `hours_to_buy` by dividing an external wage series by an external price series unless both come from the **same official publication designed as that indicator** (BMEL 5050900 and DIEESE PNCBA tempo columns qualify).
