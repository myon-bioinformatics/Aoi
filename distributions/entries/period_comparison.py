"""Explicit period comparisons; no domain columns, imputation or rounding."""
import math


def finite(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def fields(values):
    values = tuple(values)
    if not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
        raise ValueError('distinct nonempty field names required')
    return values


def compare_periods(rows, *, entity, period, metrics, before, after):
    """Compare explicitly named periods per entity, retaining gaps and raw values.

    delta = after - before; relative_delta = delta / before (None at zero).
    Period labels must be strings or integers; ordering/adjacency is not guessed.
    """
    metrics = fields(metrics)
    fields((entity, period))
    if any(type(v) not in (str, int) for v in (before, after)) or before == after:
        raise ValueError('two distinct string or integer periods required')
    index, units = {}, set()
    for row in rows:
        ident, when = row.get(entity), row.get(period)
        if not isinstance(ident, str) or not ident or type(when) not in (str, int):
            raise ValueError('nonempty entity and string or integer period required')
        key = (ident, when)
        if key in index:
            raise ValueError('duplicate entity-period')
        index[key] = row
        if when in (before, after):
            units.add(ident)
    result = []
    for ident in sorted(units):
        left, right = index.get((ident, before)), index.get((ident, after))
        values = {}
        for name in metrics:
            a, b = (left.get(name) if left else None), (right.get(name) if right else None)
            reasons = []
            for label, record, value in (('before', left, a), ('after', right, b)):
                if record is None:
                    reasons.append(label + ':missing_period')
                elif not finite(value):
                    reasons.append(label + ':missing_or_nonfinite_metric')
            delta = b - a if not reasons else None
            relative = delta / a if delta is not None and a != 0 else None
            if delta is not None and a == 0:
                reasons.append('relative_delta:zero_baseline')
            values[name] = {'before': a, 'after': b, 'delta': delta,
                            'relative_delta': relative, 'reasons': reasons}
        result.append({'entity': ident, 'metrics': values})
    return {'before': before, 'after': after, 'comparisons': result}
