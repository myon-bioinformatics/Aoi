#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: 6934ec96fce1768c08a26f6ca786f7c962904663
# entry: distributions/entries/sakanalytics_api.py
# entry-module: sakanalytics_api
# search-paths: distributions/entries,sakanalytics
# allow: 
# allow-cycles: no
# cycles: 
# modules: neighbor_comparison,period_comparison,sakanalytics_api
# prefix: _minpy_7f28cbab3ee597f3
# content-sha256: 44ac24a73dff9b10fc480f4726e7d6ce9fe3eacab006b685c461f7e091573ef2
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_7f28cbab3ee597f3"
_MINPY_ENTRY = "sakanalytics_api"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "neighbor_comparison": "\"\"\"Descriptive nearest pairs with explicit identifiers and numerical features.\n\nGeneralizes SakAnalytics' population-standardized distance. No outcome or rank\nis required. Scales use all complete, non-excluded rows; optional groups only\nrestrict pair eligibility. Distance is descriptive, not a causal conclusion.\n\"\"\"\nimport math\nimport statistics\n\nfrom _minpy_7f28cbab3ee597f3.period_comparison import fields, finite\n\n\ndef discover(rows, *, features, identifier, group=None, excluded=(), limit=20):\n    features = fields(features)\n    if not isinstance(identifier, str) or not identifier or (group is not None and (not isinstance(group, str) or not group)):\n        raise ValueError('identifier/group field names required')\n    if type(limit) is not int or limit < 0:\n        raise ValueError('nonnegative integer limit required')\n    usable, skipped, seen = [], [], set()\n    excluded = set(excluded)\n    for row in rows:\n        ident = row.get(identifier)\n        if not isinstance(ident, str) or not ident or ident in seen:\n            raise ValueError('distinct nonempty identifiers required')\n        seen.add(ident)\n        reason = ('excluded' if ident in excluded else\n                  'missing_group' if group is not None and row.get(group) is None else\n                  'missing_or_nonfinite_feature' if any(not finite(row.get(k)) for k in features) else None)\n        if reason:\n            skipped.append({'id': ident, 'reason': reason})\n        else:\n            usable.append(row)\n    scales = {k: statistics.pstdev([r[k] for r in usable]) if usable else 0 for k in features}\n    active = [k for k in features if scales[k] > 0]\n    pairs = {}\n    if active:\n        for left in usable:\n            candidates = []\n            for right in usable:\n                if right is left or (group is not None and left[group] != right[group]):\n                    continue\n                ids = tuple(sorted((left[identifier], right[identifier])))\n                distance = math.hypot(*[(left[k]-right[k])/scales[k] for k in active]) / math.sqrt(len(active))\n                candidates.append((distance, ids))\n            if candidates:\n                distance, ids = min(candidates)\n                pairs[ids] = {'units': list(ids), 'distance': distance}\n    return {'features': active, 'scales': scales,\n            'skipped': sorted(skipped, key=lambda r: r['id']),\n            'pairs': sorted(pairs.values(), key=lambda p: (p['distance'], p['units']))[:limit]}\n",
    "period_comparison": "\"\"\"Explicit period comparisons; no domain columns, imputation or rounding.\"\"\"\nimport math\n\n\ndef finite(value):\n    if type(value) not in (int, float):\n        return False\n    try:\n        return math.isfinite(value)\n    except OverflowError:\n        return False\n\n\ndef fields(values):\n    values = tuple(values)\n    if not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):\n        raise ValueError('distinct nonempty field names required')\n    return values\n\n\ndef compare_periods(rows, *, entity, period, metrics, before, after):\n    \"\"\"Compare explicitly named periods per entity, retaining gaps and raw values.\n\n    delta = after - before; relative_delta = delta / before (None at zero).\n    Period labels must be strings or integers; ordering/adjacency is not guessed.\n    \"\"\"\n    metrics = fields(metrics)\n    fields((entity, period))\n    if any(type(v) not in (str, int) for v in (before, after)) or before == after:\n        raise ValueError('two distinct string or integer periods required')\n    index, units = {}, set()\n    for row in rows:\n        ident, when = row.get(entity), row.get(period)\n        if not isinstance(ident, str) or not ident or type(when) not in (str, int):\n            raise ValueError('nonempty entity and string or integer period required')\n        key = (ident, when)\n        if key in index:\n            raise ValueError('duplicate entity-period')\n        index[key] = row\n        if when in (before, after):\n            units.add(ident)\n    result = []\n    for ident in sorted(units):\n        left, right = index.get((ident, before)), index.get((ident, after))\n        values = {}\n        for name in metrics:\n            a, b = (left.get(name) if left else None), (right.get(name) if right else None)\n            reasons = []\n            for label, record, value in (('before', left, a), ('after', right, b)):\n                if record is None:\n                    reasons.append(label + ':missing_period')\n                elif not finite(value):\n                    reasons.append(label + ':missing_or_nonfinite_metric')\n            delta = b - a if not reasons else None\n            relative = delta / a if delta is not None and a != 0 else None\n            if delta is not None and a == 0:\n                reasons.append('relative_delta:zero_baseline')\n            values[name] = {'before': a, 'after': b, 'delta': delta,\n                            'relative_delta': relative, 'reasons': reasons}\n        result.append({'entity': ident, 'metrics': values})\n    return {'before': before, 'after': after, 'comparisons': result}\n",
    "sakanalytics_api": "\"\"\"SakAnalytics min: explicit period comparisons and descriptive nearest pairs.\"\"\"\nfrom _minpy_7f28cbab3ee597f3.period_comparison import compare_periods\nfrom _minpy_7f28cbab3ee597f3.neighbor_comparison import discover\n\n__all__ = ['compare_periods', 'discover']\n",
}
_MINPY_SKIP = (
    "__builtins__",
    "__cached__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__path__",
    "__spec__",
)


def _minpy_original(fullname):
    if fullname == _MINPY_PREFIX:
        return ""
    prefix = _MINPY_PREFIX + "."
    if fullname.startswith(prefix):
        return fullname[len(prefix):]
    return None


class _MinpyLoader:
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        original = _minpy_original(module.__name__)
        if original is None:
            raise ImportError(module.__name__)
        if original == "":
            module.__path__ = []
            return
        source = _MINPY_SOURCES[original]
        filename = "minpy://" + original + ".py"
        module.__file__ = filename
        exec(compile(source, filename, "exec"), module.__dict__)


class _MinpyFinder:
    def __init__(self):
        self._minpy_sources = _MINPY_SOURCES

    def find_spec(self, fullname, path, target=None):
        original = _minpy_original(fullname)
        if original is None:
            return None
        if original == "":
            is_package = True
        elif original not in _MINPY_SOURCES:
            return None
        else:
            is_package = original in _MINPY_PACKAGES
        return importlib.machinery.ModuleSpec(
            fullname,
            _MinpyLoader(),
            origin="minpy://" + (original or _MINPY_PREFIX),
            is_package=is_package,
        )


def _minpy_install():
    for finder in sys.meta_path:
        if getattr(finder, "_minpy_sources", None) is _MINPY_SOURCES:
            return
    sys.meta_path.insert(0, _MinpyFinder())


def _minpy_run_entry_as_main():
    import types

    original = _MINPY_ENTRY
    full = _MINPY_PREFIX + "." + original
    module = types.ModuleType("__main__")
    origin = "minpy://" + original + ".py"
    module.__file__ = globals().get("__file__") or origin
    if original in _MINPY_PACKAGES:
        module.__package__ = full
        module.__path__ = []
    elif "." in original:
        module.__package__ = full.rpartition(".")[0]
    else:
        module.__package__ = _MINPY_PREFIX
    sys.modules["__main__"] = module
    sys.modules[full] = module
    exec(compile(_MINPY_SOURCES[original], origin, "exec"), module.__dict__)


def _minpy_export_entry(namespace):
    import importlib

    module = importlib.import_module(_MINPY_PREFIX + "." + _MINPY_ENTRY)
    for key, value in module.__dict__.items():
        if key not in _MINPY_SKIP:
            namespace[key] = value


_minpy_install()
if __name__ == "__main__":
    _minpy_run_entry_as_main()
else:
    _minpy_export_entry(globals())
