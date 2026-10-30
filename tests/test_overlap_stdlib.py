"""明示的 stdlib backend の native との一致・境界と import 分離。"""
import json
import os
from pathlib import Path
import random
import subprocess
import sys

import pytest

from dragowing.overlap import B_COND, default_conditions, load_overlap, parse_cond
from dragowing.records import read_jsonl

REPO = Path(__file__).resolve().parents[1]
OPS = ('<', '<=', '>', '>=', '==', '!=')


def row(i, **values):
    return dict(team=f't{i}', team_name=f'球団{i}', season=2020, league='C',
                upper_half=bool(i % 2), **values)


def write(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, allow_nan=False) + '\n' for r in rows), encoding='utf-8')
    return path


def payload(result):
    return json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False)


def assert_parity(path, conds):
    native = load_overlap(path, conds)
    light = load_overlap(path, conds, backend='stdlib')
    assert payload(light) == payload(native)
    assert payload(load_overlap(path, conds, backend='stdlib')) == payload(light)
    assert sum(r['count'] for r in light['regions']) == len(light['units'])
    return light


def test_c001_bytes_and_numeric_conditions(aoi_root):
    out = aoi_root / 'cycles/c001-chunichi/outputs'
    path = out / 'season.jsonl'
    rows = read_jsonl(path)
    conds = default_conditions(read_jsonl(out / 'propositions.jsonl'), rows)
    result = assert_parity(path, conds)
    assert len(result['units']) == 168
    assert len(result['regions']) == 8
    for col in ("rd", "rank_pythag", "wins_vs_pythag", "season", "RF"):
        for op in OPS:
            assert_parity(path, [{"col": col, "op": op, "value": rows[0][col]}, B_COND])


@pytest.mark.parametrize('n', [1, 7, 8, 9, 99, 100, 101, 255, 256, 257])
@pytest.mark.parametrize('op', OPS)
def test_missing_null_and_byte_boundaries(tmp_path, n, op):
    rows = [row(i, x=[None, -1, 0, 1, 1.5][i % 5]) for i in range(n)]
    for r in rows[::7]:
        r.pop('x')
    if n == 1:
        rows[0]['x'] = None
    path = write(tmp_path / 'season.jsonl', rows)
    # x is absent in some rows but remains a known column; nulls are false even for !=.
    assert_parity(path, [{'col': 'x', 'op': op, 'value': 0.5}, B_COND])


@pytest.mark.parametrize('values,literal', [
    ([False, True, None], False), (['a', '日本', None, ''], 'a'),
    ([-2**63, 0, 2**63-1], 2**63-1),
    ([-2**53, 0, 2**53], 0.5),
    ([0, -0.0, 1e-300, -1e300], 0.0), ([None, None], None),
    ([None, None], 1), ([1, 2, None], None),
])
@pytest.mark.parametrize('op', OPS)
def test_scalar_edges(tmp_path, values, literal, op):
    path = write(tmp_path / 's.jsonl', [row(i, x=v) for i, v in enumerate(values)])
    assert_parity(path, [{'col': 'x', 'op': op, 'value': literal}, B_COND])


def test_deterministic_random_masks(tmp_path):
    rng = random.Random(20261021)
    rows = [row(i, x=rng.choice([None, -2, -1, 0, 1, 2]), y=rng.choice([None, 0.0, 0.5, 1.0])) for i in range(257)]
    path = write(tmp_path / 's.jsonl', rows)
    for _ in range(20):
        conds = [{'col': 'x', 'op': rng.choice(OPS), 'value': rng.randint(-2, 2)},
                 {'col': 'y', 'op': rng.choice(OPS), 'value': rng.choice([None, 0.0, 0.5, 1.0])}, B_COND]
        assert_parity(path, conds)
    assert_parity(path, [])
    assert_parity(path, [B_COND, B_COND])


@pytest.mark.parametrize('text', ['', '\n  \n', '{bad', 'null\n'])
def test_empty_and_invalid_are_rejected_by_both(tmp_path, text):
    path = tmp_path / 's.jsonl'
    path.write_text(text, encoding='utf-8')
    for backend in ('native', 'stdlib'):
        with pytest.raises(Exception):
            load_overlap(path, [B_COND], backend=backend)


@pytest.mark.parametrize('values,literal', [
    ([1, '1'], 1), ([True, 1], True), ([[1]], 1), ([{'a': 1}], 1),
    ([2**63], 1), ([1], 2**63), ([2**53+1], 1.0), ([1], True),
    ([True], 'true'), (['a'], 1),
])
def test_unsupported_coercion_fails_explicitly(tmp_path, values, literal):
    path = write(tmp_path / 's.jsonl', [row(i, x=v) for i, v in enumerate(values)])
    with pytest.raises(ValueError, match='stdlib overlap'):
        load_overlap(path, [{'col': 'x', 'op': '==', 'value': literal}], backend='stdlib')


def test_late_schema_change_and_unknown_column(tmp_path):
    path = write(tmp_path / 's.jsonl', [row(i, x=None) for i in range(100)] + [row(100, x=1)])
    with pytest.raises(ValueError, match='100行'):
        load_overlap(path, [B_COND], backend='stdlib')
    path = write(path, [row(i, x=1) for i in range(100)] + [row(100, x=1, late=1)])
    with pytest.raises(ValueError, match='100行'):
        load_overlap(path, [B_COND], backend='stdlib')
    path = write(path, [row(1, x=1)])
    for backend in ('native', 'stdlib'):
        with pytest.raises(ValueError, match='存在しない列'):
            load_overlap(path, [{'col': 'no_such_column', 'op': '==', 'value': 1}], backend=backend)


def test_duplicate_keys_and_nonfinite_are_rejected(tmp_path):
    path = tmp_path / 's.jsonl'
    for text in ['{"team":"a","season":2020,"x":1,"x":2}',
                 '{"team":"a","season":2020,"x":NaN}',
                 '{"team":"a","season":2020,"x":Infinity}']:
        path.write_text(text, encoding='utf-8')
        with pytest.raises(ValueError, match='stdlib overlap'):
            load_overlap(path, [B_COND], backend='stdlib')


def test_explicit_selection_preserves_installed_modules(tmp_path):
    import numpy
    import polars
    path = write(tmp_path / 's.jsonl', [row(1, x=1)])
    load_overlap(path, [B_COND])
    rule_search = sys.modules["rule_search"]
    before = {name: sys.modules[name] for name in ('numpy', 'polars', 'propositions', 'rule_search')}
    assert_parity(path, [B_COND])
    assert all(sys.modules[name] is module for name, module in before.items())
    assert rule_search.np is numpy and rule_search.pl is polars
    with pytest.raises(ValueError, match='backend'):
        load_overlap(path, [], backend='auto')


def test_stdlib_in_fresh_process_with_all_third_party_imports_blocked(tmp_path, aoi_root):
    # Use an isolated -S interpreter; block the entire library + engine import graph.
    code = '''
import importlib.abc, importlib.machinery, json, sys, types
from pathlib import Path
root, data = map(Path, sys.argv[1:])
pkg = types.ModuleType('dragowing'); pkg.__path__ = [str(root)]; sys.modules['dragowing'] = pkg
blocked = {'numpy', 'polars', 'propositions', 'rule_search'}
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in blocked:
            raise AssertionError('unexpected import: ' + fullname)
sys.meta_path.insert(0, Block())
from dragowing.overlap import default_conditions, finalize_conditions, load_overlap, parse_cond
from dragowing.records import read_jsonl
from dragowing.cli import build_parser
before = list(sys.path)
rows = read_jsonl(data / 'season.jsonl')
conds = default_conditions(read_jsonl(data / 'propositions.jsonl'), rows)
assert parse_cond('rd,>,0') == {'col': 'rd', 'op': '>', 'value': 0}
assert finalize_conditions(conds, [], rows) == conds
assert build_parser().parse_args(['--results', str(data), '--out', 'unused', '--overlap-backend', 'stdlib']).overlap_backend == 'stdlib'
assert build_parser().parse_args(['--results', str(data), '--out', 'unused']).overlap_backend == 'native'
result = load_overlap(data / 'season.jsonl', conds, backend='stdlib')
assert sys.path == before
assert not blocked.intersection(sys.modules)
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
'''
    data = aoi_root / 'cycles/c001-chunichi/outputs'
    outputs = [subprocess.run([sys.executable, '-S', '-c', code, str(REPO), str(data)],
               env={**os.environ, 'PYTHONHASHSEED': seed}, capture_output=True, text=True, check=True).stdout
               for seed in ('1', '6789')]
    assert outputs[0] == outputs[1]
    expected = load_overlap(data / 'season.jsonl', default_conditions(read_jsonl(data / 'propositions.jsonl'), read_jsonl(data / 'season.jsonl')))
    assert outputs[0].rstrip('\n') == payload(expected)


@pytest.mark.parametrize('target', ['value', 'literal', 'key'])
def test_unicode_surrogates_are_outside_supported_domain(tmp_path, target):
    rows = [row(1, x='a')]
    cond = {'col': 'x', 'op': '==', 'value': 'a'}
    if target == 'value':
        rows[0]['x'] = '\ud800'
    elif target == 'literal':
        cond['value'] = '\udfff'
    else:
        rows[0]['\ud800'] = 1
    path = tmp_path / 's.jsonl'
    path.write_text(json.dumps(rows[0], ensure_ascii=True), encoding='utf-8')
    with pytest.raises(ValueError, match='surrogate'):
        load_overlap(path, [cond], backend='stdlib')


def test_cli_stdlib_writes_same_html(tmp_path, aoi_root):
    from dragowing.cli import main
    data = aoi_root / 'cycles/c001-chunichi/outputs'
    native, light = tmp_path / 'native', tmp_path / 'stdlib'
    assert main(['--results', str(data), '--out', str(native), '--id', 'P1']) == 0
    assert main(['--results', str(data), '--out', str(light), '--id', 'P1', '--overlap-backend', 'stdlib']) == 0
    for name in ('index.html', 'propositions.html'):
        assert (light / name).read_bytes() == (native / name).read_bytes()
