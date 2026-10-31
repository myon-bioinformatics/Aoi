# Statistics Iceland HES — national food share of total expenditure

## Panel
- File: `hagstofa_iceland_hes_food_share_panel.csv`
- Rows: 14
- ISO3: ISL
- Periods: 2000-2002 → 2013-2016 (14 rolling windows)
- Variable: food_share_of_total_expenditure (percent), Unit=Per cent from source

## Values
   period  year_start  year_end  value
2000-2002        2000      2002   15.9
2001-2003        2001      2003   15.2
2002-2004        2002      2004   14.4
2003-2005        2003      2005   12.9
2004-2006        2004      2006   12.8
2005-2007        2005      2007   11.8
2006-2008        2006      2008   12.9
2007-2009        2007      2009   13.9
2008-2010        2008      2010   14.1
2009-2011        2009      2011   14.7
2010-2012        2010      2012   14.9
2011-2014        2011      2014   15.4
2012-2015        2012      2015   15.6
2013-2016        2013      2016   13.1

## Source
- Statistics Iceland PxWeb VIS05302 — Average household expenditure and size by residence from 2002-2016
- Residence = Total; COICOP = 01 Food and non-alcoholic beverages; Unit = Per cent

## Notes
- Survey HES (neyslarannsókn), not national-accounts HFCE.
- ISL HFCE food share already covered in `eurostat_nama_food_share_hfce_panel.csv` — not re-pulled (THJ02103 skipped as duplicate).
- VIS05304 (by disposable income) not pulled — Season2 food×income.
- No FX. Retrieved: 2026-10-24 (Asia/Tokyo)
