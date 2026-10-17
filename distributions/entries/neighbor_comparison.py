"""Descriptive nearest pairs with explicit identifiers and numerical features.

Generalizes SakAnalytics' population-standardized distance. No outcome or rank
is required. Scales use all complete, non-excluded rows; optional groups only
restrict pair eligibility. Distance is descriptive, not a causal conclusion.
"""
import math
import statistics

from period_comparison import fields, finite


def discover(rows, *, features, identifier, group=None, excluded=(), limit=20):
    features = fields(features)
    if not isinstance(identifier, str) or not identifier or (group is not None and (not isinstance(group, str) or not group)):
        raise ValueError('identifier/group field names required')
    if type(limit) is not int or limit < 0:
        raise ValueError('nonnegative integer limit required')
    usable, skipped, seen = [], [], set()
    excluded = set(excluded)
    for row in rows:
        ident = row.get(identifier)
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError('distinct nonempty identifiers required')
        seen.add(ident)
        reason = ('excluded' if ident in excluded else
                  'missing_group' if group is not None and row.get(group) is None else
                  'missing_or_nonfinite_feature' if any(not finite(row.get(k)) for k in features) else None)
        if reason:
            skipped.append({'id': ident, 'reason': reason})
        else:
            usable.append(row)
    scales = {k: statistics.pstdev([r[k] for r in usable]) if usable else 0 for k in features}
    active = [k for k in features if scales[k] > 0]
    pairs = {}
    if active:
        for left in usable:
            candidates = []
            for right in usable:
                if right is left or (group is not None and left[group] != right[group]):
                    continue
                ids = tuple(sorted((left[identifier], right[identifier])))
                distance = math.hypot(*[(left[k]-right[k])/scales[k] for k in active]) / math.sqrt(len(active))
                candidates.append((distance, ids))
            if candidates:
                distance, ids = min(candidates)
                pairs[ids] = {'units': list(ids), 'distance': distance}
    return {'features': active, 'scales': scales,
            'skipped': sorted(skipped, key=lambda r: r['id']),
            'pairs': sorted(pairs.values(), key=lambda p: (p['distance'], p['units']))[:limit]}
