"""Recovered entry points must work without pytest's injected import paths."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from queryu import Cache

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd):
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, env=env,
                          text=True, capture_output=True, timeout=30)


def test_recovered_fielding_source_runs_through_real_offline_cli(tmp_path):
    head = ['チーム', '守備率', '試合', '守備機会', '刺殺', '補殺', '失策', '併殺・参加', '併殺・球団', '捕逸']
    row = ['中日', '.991', '143', '5488', '3788', '1648', '52', '328', '122', '10']
    html = '<table>' + ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in [head, row]) + '</table>'
    cache = tmp_path / 'cache'
    Cache(cache).put('2025_c', 'https://npb.jp/bis/2025/stats/tmf_c.html', '2025', 200,
                     html.encode(), {})
    out = tmp_path / 'observed.md'
    result = run([ROOT/'blueprobe/blueprobe.py', '--source', 'npb_team_fielding',
                  '--cache', cache, '--out', out], tmp_path)
    assert result.returncode == 0, result.stderr
    assert 'npb_team_fielding' in out.read_text() and '要確認' in out.read_text()
    # Incomplete six-team data is visible, and strict mode must reject it.
    strict = run([ROOT/'blueprobe/blueprobe.py', '--source', 'npb_team_fielding',
                  '--cache', cache, '--strict'], tmp_path)
    assert strict.returncode == 1 and '取りこぼし' in strict.stderr


def test_recovered_next_cli_reads_frozen_results_from_another_directory(tmp_path):
    result = run([ROOT/'pythdragoras/next_seeds.py', 'next',
                  ROOT/'cycles/c001-chunichi/outputs/propositions.jsonl', '--id', 'P1'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert 'P1 ' in result.stdout and '道筋' in result.stdout


@pytest.mark.parametrize('script', ['render_score_report.py', 'render_game_state.py', 'render_preclinch_flow.py'])
def test_recovered_renderers_import_without_pytest_paths(tmp_path, script):
    result = run([ROOT/'research/gpt-r001-score-allocation'/script, '--help'], tmp_path)
    assert result.returncode == 0, result.stderr
    assert '--output' in result.stdout


def test_research_loop_and_dragowing_package_coexist_in_clean_process():
    code = '''
import research_loop.feedback
import dragowing.export
import dragowing.chrome_pipe
from dragowing.research_report import render_report
assert callable(render_report)
'''
    result = run(['-c', code], ROOT)
    assert result.returncode == 0, result.stderr
