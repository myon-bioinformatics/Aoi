"""Research regressions: held-out year leakage and unknown provisional units."""
import importlib.util
import json
from pathlib import Path
import polars as pl

ROOT = Path(__file__).resolve().parents[2]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'cycles/c001-chunichi/research'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_r66_2012_does_not_change_training_bands(tmp_path, capsys):
    m = script('r66_indicator_lines')
    m.INDICATORS = [('value', 'fixture', 1, 0)]
    rows = [{'season': year, 'team': str(i), 'league': 'C', 'upper_half': i < 3,
             'value': 6-i, 'RF': 10, 'RA': 9, 'G': 2}
            for year in (2012, 2013, 2014) for i in range(6)]
    path = tmp_path/'season.jsonl'
    path.write_text('\n'.join(map(json.dumps, rows)))
    assert m.main([str(path)]) == 0
    before = capsys.readouterr().out
    for r in rows:
        if r['season'] == 2012:
            r['value'] = -100 if r['upper_half'] else 100
    path.write_text('\n'.join(map(json.dumps, rows)))
    m.main([str(path)])
    assert capsys.readouterr().out == before
    m.main([str(path), '--season', '2012'])
    assert '範囲: 6 単位' in capsys.readouterr().out


def test_r75_nulls_are_not_counterexamples_or_nonmembers():
    m = script('r75_provisional')
    flags = pl.DataFrame({'team': ['d','t','g','s','c'],
                          'x': [True, True, True, None, False], 'y': [None, False, True, True, None]})
    assert m.classify(flags) == (2, 1, ['t'], 3, '判定不能')
