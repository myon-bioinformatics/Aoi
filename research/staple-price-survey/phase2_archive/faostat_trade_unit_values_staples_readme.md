# FAOSTAT Trade — derived unit values (staples & fibre)

## Panel
- File: `faostat_trade_unit_values_staples_panel.csv`
- Rows: 197,865
- ISO3: 184
- Span: 1961–2024 annual
- Measures: Import & export unit values USD/tonne for selected food staples + cotton/rubber

## Source
- FAOSTAT TCL bulk; UV = value/quantity
- Retrieved: 2026-10-25 (Asia/Tokyo)

## Notes
- Simple trade unit prices. Manageable item extract (~17 codes), not full BACI/TCL dump. Derived.
- No fabricate. No FX fills.

- QC: dropped 12 rows with UV > 500,000 USD/t (likely qty/value errors); remaining 197,853 rows.
