import pytest
from annual_history_report import require_primary_years


def test_primary_report_rejects_mixed_historical_or_missing_years():
    assert require_primary_years(range(2013, 2027)) is None
    for years in (range(1950, 2027), range(2014, 2027), [2012]*14):
        with pytest.raises(ValueError, match='2013-2026'):require_primary_years(years)
