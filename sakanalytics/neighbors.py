"""Deterministic descriptive neighbors; no outcome-derived distance features."""
import math
import statistics

FEATURES = ("rf_adv", "ra_adv", "vs_lower_wpct")


def discover(rows, excluded=(), limit=20):
    usable, skipped = [], []
    for row in rows:
        unit = f"{row['team']}-{row['season']}"
        if row['season'] in excluded or row.get('rank_tie') or type(row.get('upper_half')) is not bool:
            skipped.append(unit)
            continue
        if any(type(row.get(k)) not in (int, float) or not math.isfinite(row[k]) for k in FEATURES):
            skipped.append(unit)
            continue
        usable.append(row)
    scales = {k: statistics.pstdev([r[k] for r in usable]) if usable else 0 for k in FEATURES}
    features = [k for k in FEATURES if scales[k] > 0]
    pairs = {}
    if features:
        for left in usable:
            options = []
            for right in usable:
                if left['league'] != right['league'] or left['upper_half'] == right['upper_half']:
                    continue
                ids = sorted([f"{left['team']}-{left['season']}", f"{right['team']}-{right['season']}"])
                distance = math.sqrt(sum(((left[k]-right[k])/scales[k])**2 for k in features)/len(features))
                options.append((distance, ids, right))
            if options:
                distance, ids, right = min(options, key=lambda x: (x[0], x[1]))
                pairs[tuple(ids)] = {'units': ids, 'distance': distance,
                    'values': {f"{r['team']}-{r['season']}": {k: r[k] for k in features} for r in (left, right)},
                    'upper_half': {f"{r['team']}-{r['season']}": r['upper_half'] for r in (left, right)}}
    return {'features': features, 'scales': scales, 'skipped': sorted(skipped),
            'pairs': sorted(pairs.values(), key=lambda p: (p['distance'], p['units']))[:limit],
            'method': '同リーグ・A/Bが異なる最近傍。全対象の標準偏差で標準化した距離。類似の絶対基準・因果判定ではない。相手区分は最終順位に依存。'}
