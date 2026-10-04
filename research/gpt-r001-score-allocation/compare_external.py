"""Reconcile selected supplied-report claims against the frozen final-score data."""
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/observations/r001/games.jsonl'
EXPECTED_SHA = '7b1b6dfdd41cafbdf851cdb8bcd2cae981adb338570dd66de75881bfe35ee8d9'


def main():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA
    games = [json.loads(s) for s in DATA.read_text().splitlines()]
    values = {}
    for year in range(2013, 2026):
        units = []
        for g in games:
            if not g['date'].startswith(str(year)) or 'd' not in (g['home'], g['away']):
                continue
            home = g['home'] == 'd'
            r, ra = (g['hs'], g['as']) if home else (g['as'], g['hs'])
            units.append((home, r, ra))
        def wpct(subset):
            decisive = [(r, ra) for _, r, ra in subset if r != ra]
            return sum(r > ra for r, ra in decisive) / len(decisive)
        w = sum(r > ra for _, r, ra in units)
        l = sum(r < ra for _, r, ra in units)
        r = sum(r for _, r, _ in units)
        ra = sum(ra for _, _, ra in units)
        values[year] = {
            'R/G': r / len(units), 'RA/G': ra / len(units),
            'RD/G': (r - ra) / len(units),
            'pythW_diff': w - r**1.83 / (r**1.83 + ra**1.83) * (w + l),
            'one_run_win_rate': wpct([u for u in units if abs(u[1] - u[2]) == 1]),
            'three_plus_win_rate': wpct([u for u in units if abs(u[1] - u[2]) >= 3]),
            'home_win_rate': wpct([u for u in units if u[0]]),
            'away_win_rate': wpct([u for u in units if not u[0]]),
            'wins_one_run_share': sum(r - ra == 1 for _, r, ra in units) / w,
            'wins_four_plus_share': sum(r - ra >= 4 for _, r, ra in units) / w,
        }
    supplied = {'R/G': 3.338, 'RA/G': 3.805, 'RD/G': -0.467,
                'pythW_diff': 1.693, 'one_run_win_rate': 0.495,
                'three_plus_win_rate': 0.421, 'home_win_rate': 0.517,
                'away_win_rate': 0.389, 'wins_one_run_share': 0.330,
                'wins_four_plus_share': 0.290}
    checks = {k: {'supplied': v, 'computed': statistics.mean(y[k] for y in values.values()),
                  'matches_display_rounding': round(statistics.mean(y[k] for y in values.values()), 3) == v}
              for k, v in supplied.items()}
    result = {'source': 'User-supplied Grok Part2 update, received 2026-10-03',
              'data_sha256': EXPECTED_SHA, 'aggregation': 'unweighted mean of 13 annual metrics',
              'checks': checks,
              'negative_pythagorean_residual_years': [y for y, v in values.items() if v['pythW_diff'] < 0],
              'not_checked': ['inning trajectories', '2026', 'all-team ranks', 'standardized differences', 'official rank tie-breaks']}
    target = Path(__file__).parent / 'outputs/external_comparison.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
