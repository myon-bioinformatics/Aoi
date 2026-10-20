import json
from pathlib import Path
import pytest
from annual_scope import PRIMARY_YEARS, primary_cache
from queryu import Cache
from npb_team_annual import pages


def test_only_primary_cache_is_copied_and_reference_input_is_unchanged(tmp_path):
    cache = Cache(tmp_path/'reference')
    for year in (2012, *PRIMARY_YEARS):
        for lg in ('c', 'p'):
            for cat in ('std', 'tmb', 'tmp', 'tmf', 'archive'):
                key=f'{year}_{lg}_{cat}'
                url=next(url for k,url,_ in pages([year]) if k==key)
                cache.put(key,url,str(year),200,b'<html>team</html>',{})
    original = cache.manifest.read_bytes()
    out = tmp_path/'primary'
    assert primary_cache(cache.root, out) == 140
    assert cache.manifest.read_bytes() == original
    selected = Cache(out).latest()
    assert len(selected) == 140
    assert all(int(e['group']) in PRIMARY_YEARS for e in selected.values())
    for entry in selected.values():assert Cache(out).body_bytes(entry) == b'<html>team</html>'
    with pytest.raises(ValueError, match='empty'):primary_cache(cache.root, out)


def test_missing_primary_year_is_not_filled_from_reference_years(tmp_path):
    cache = Cache(tmp_path/'reference')
    cache.put('2012_c_std', 'https://npb.jp/2012', '2012', 200, b'<html></html>', {})
    with pytest.raises(ValueError, match='140'):primary_cache(cache.root, tmp_path/'primary')
