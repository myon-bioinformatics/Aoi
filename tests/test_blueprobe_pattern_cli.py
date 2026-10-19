import sys
from unittest.mock import Mock

import pytest

import blueprobe
import dom_patterns


def test_list_patterns_needs_no_cache_or_queryu(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, 'queryu', None)
    load = Mock(side_effect=AssertionError('must not load a source'))
    monkeypatch.setattr(blueprobe, 'load_source', load)
    assert blueprobe.main(['--list-patterns']) == 0
    output = capsys.readouterr()
    assert output.err == ''
    for pattern in dom_patterns.list_patterns():
        assert pattern['key'] in output.out
        assert pattern['selector'] in output.out
    load.assert_not_called()


@pytest.mark.parametrize('pattern,message', [
    ('invalid_pattern_xyz', "unknown pattern key 'invalid_pattern_xyz'"),
    ('', 'must be a non-empty string'),
    ('   ', 'must be a non-empty string'),
])
def test_invalid_pattern_is_cli_error_before_cache_access(pattern, message, tmp_path, capsys):
    output = tmp_path / 'report.md'
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(['--source', 'html_source', '--pattern', pattern,
                        '--cache', str(tmp_path / 'missing'), '--out', str(output)])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '--pattern:' in captured.err
    assert message in captured.err
    assert '--list-patterns' in captured.err
    assert 'Traceback' not in captured.err
    assert 'no cache manifest' not in captured.err
    assert not output.exists()


@pytest.mark.parametrize('pattern', ['github_readme', 'invalid_pattern_xyz', ''])
@pytest.mark.parametrize('source', ['npb_calendar', 'does_not_exist'])
def test_pattern_rejects_other_sources_before_loading(source, pattern, tmp_path, monkeypatch, capsys):
    load = Mock(side_effect=AssertionError('must validate before source import'))
    monkeypatch.setattr(blueprobe, 'load_source', load)
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(['--source', source, '--pattern', pattern, '--cache', str(tmp_path)])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '--pattern requires --source html_source' in captured.err
    load.assert_not_called()


@pytest.mark.parametrize('args', [[], ['--source', 'html_source'], ['--cache', 'missing']])
def test_reanalysis_still_requires_source_and_cache(args, capsys):
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(args)
    assert exc.value.code == 2
    assert '--source and --cache are required' in capsys.readouterr().err


def test_listing_cannot_silently_ignore_pattern(capsys):
    with pytest.raises(SystemExit) as exc:
        blueprobe.main(['--list-patterns', '--pattern', 'github_readme'])
    assert exc.value.code == 2
    assert 'not allowed with argument' in capsys.readouterr().err
