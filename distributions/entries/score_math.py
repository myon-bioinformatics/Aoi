"""Generic numerical kernels extracted from PythDRagoras season_sensitivity.

The original research adapter remains in Aoi. Threshold sweep sorting costs
O(n log n); subsequent updates cost O(n + t), rather than O(n*t) recounts.
No model fitting, sport-specific scores or significance verdicts are included.
"""
import math
from period_comparison import finite


def validate_grid(values, name):
    if not values or not all(finite(v) for v in values) or any(a >= b for a, b in zip(values, values[1:])):
        raise ValueError(f'{name}: finite, strictly increasing grid required')


def counts_metrics(tp, fp, fn, tn):
    if any(type(v) is not int or v < 0 for v in (tp, fp, fn, tn)):
        raise ValueError("nonnegative integer counts required")
    n = tp + fp + fn + tn
    den = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    yes, no = tp + fp, fn + tn
    p_yes, p_no = (tp / yes if yes else None), (fn / no if no else None)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'n': n,
            'mcc': (tp*tn-fp*fn)/math.sqrt(den) if den else None,
            'p_outcome_given_high': p_yes, 'p_outcome_given_low': p_no,
            'probability_gap': p_yes-p_no if p_yes is not None and p_no is not None else None}


def threshold_curve(scores, outcomes, thresholds):
    """Exact sweep: start with every row high, remove rows as the threshold advances."""
    validate_grid(thresholds, 'thresholds')
    if len(scores) != len(outcomes) or not all(finite(s) for s in scores) or not all(type(y) is bool for y in outcomes):
        raise ValueError('finite scores and aligned Boolean outcomes required')
    ordered = sorted(zip(scores, outcomes))
    tp, fp, fn, tn = sum(outcomes), len(outcomes)-sum(outcomes), 0, 0
    result, cursor = [], 0
    for threshold in thresholds:
        changed = 0
        while cursor < len(ordered) and ordered[cursor][0] < threshold:
            _, y = ordered[cursor]
            tp -= y
            fn += y
            fp -= not y
            tn += not y
            cursor += 1
            changed += 1
        result.append({'threshold': threshold, 'crossed_units': changed, **counts_metrics(tp, fp, fn, tn)})
    return result


def shape(points, x='threshold', y='mcc'):
    """Finite differences/trapezoids on sampled values; never a smooth derivative claim."""
    validate_grid([p[x] for p in points], x)
    if any(p[y] is not None and not finite(p[y]) for p in points):
        raise ValueError("finite ordinates or None required")
    slopes, area, span = [], 0.0, 0.0
    for left, right in zip(points, points[1:]):
        dx = right[x]-left[x]
        valid = left[y] is not None and right[y] is not None
        slopes.append({'left': left[x], 'right': right[x],
                       'slope': (right[y]-left[y])/dx if valid else None})
        if valid:
            area += dx*(left[y]+right[y])/2
            span += dx
    bends = []
    for a, b in zip(slopes, slopes[1:]):
        if a['slope'] is not None and b['slope'] is not None:
            dx = (b['left']+b['right']-a['left']-a['right'])/2
            bends.append({'at': a['right'], 'slope_change_per_unit': (b['slope']-a['slope'])/dx})
    valid = [p for p in points if p[y] is not None]
    best = max((p[y] for p in valid), default=None)
    # Consecutive equal maxima are represented as intervals, including one-point peaks.
    plateaus = []
    for i, p in enumerate(points):
        if best is not None and p[y] == best:
            if i and points[i-1][y] == best:
                plateaus[-1]['end'] = p[x]
            else:
                plateaus.append({'start': p[x], 'end': p[x]})
    extrema = []
    for a, b, c in zip(points, points[1:], points[2:]):
        if all(p[y] is not None for p in (a, b, c)):
            if b[y] > a[y] and b[y] > c[y]:
                extrema.append({'at': b[x], 'kind': 'sampled_max'})
            if b[y] < a[y] and b[y] < c[y]:
                extrema.append({'at': b[x], 'kind': 'sampled_min'})
    return {'finite_slopes': slopes, 'slope_changes': bends, 'sampled_extrema': extrema,
            'max_intervals': plateaus, 'trapezoid_area': area if span else None,
            'covered_span': span, 'mean_over_grid': area/span if span else None}
