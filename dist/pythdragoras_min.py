#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: b0825894c24a443b77308e29eb489442f41cb0ff
# entry: distributions/entries/pythdragoras_api.py
# entry-module: pythdragoras_api
# search-paths: distributions/entries,pythdragoras
# allow: 
# allow-cycles: no
# cycles: 
# modules: period_comparison,pythdragoras_api,registration_audit,score_math
# prefix: _minpy_a2da5d2bfd8409ca
# content-sha256: 7705bcb2c1dfd9bbd006c54baa48b4901c030fdd835d7bf45980b16542d457de
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_a2da5d2bfd8409ca"
_MINPY_ENTRY = "pythdragoras_api"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "period_comparison": "\"\"\"Explicit period comparisons; no domain columns, imputation or rounding.\"\"\"\nimport math\n\n\ndef finite(value):\n    if type(value) not in (int, float):\n        return False\n    try:\n        return math.isfinite(value)\n    except OverflowError:\n        return False\n\n\ndef fields(values):\n    values = tuple(values)\n    if not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):\n        raise ValueError('distinct nonempty field names required')\n    return values\n\n\ndef compare_periods(rows, *, entity, period, metrics, before, after):\n    \"\"\"Compare explicitly named periods per entity, retaining gaps and raw values.\n\n    delta = after - before; relative_delta = delta / before (None at zero).\n    Period labels must be strings or integers; ordering/adjacency is not guessed.\n    \"\"\"\n    metrics = fields(metrics)\n    fields((entity, period))\n    if any(type(v) not in (str, int) for v in (before, after)) or before == after:\n        raise ValueError('two distinct string or integer periods required')\n    index, units = {}, set()\n    for row in rows:\n        ident, when = row.get(entity), row.get(period)\n        if not isinstance(ident, str) or not ident or type(when) not in (str, int):\n            raise ValueError('nonempty entity and string or integer period required')\n        key = (ident, when)\n        if key in index:\n            raise ValueError('duplicate entity-period')\n        index[key] = row\n        if when in (before, after):\n            units.add(ident)\n    result = []\n    for ident in sorted(units):\n        left, right = index.get((ident, before)), index.get((ident, after))\n        values = {}\n        for name in metrics:\n            a, b = (left.get(name) if left else None), (right.get(name) if right else None)\n            reasons = []\n            for label, record, value in (('before', left, a), ('after', right, b)):\n                if record is None:\n                    reasons.append(label + ':missing_period')\n                elif not finite(value):\n                    reasons.append(label + ':missing_or_nonfinite_metric')\n            delta = b - a if not reasons else None\n            relative = delta / a if delta is not None and a != 0 else None\n            if delta is not None and a == 0:\n                reasons.append('relative_delta:zero_baseline')\n            values[name] = {'before': a, 'after': b, 'delta': delta,\n                            'relative_delta': relative, 'reasons': reasons}\n        result.append({'entity': ident, 'metrics': values})\n    return {'before': before, 'after': after, 'comparisons': result}\n",
    "pythdragoras_api": "\"\"\"PythDRagoras min: numerical threshold sweeps and provenance checks.\"\"\"\nfrom _minpy_a2da5d2bfd8409ca.score_math import counts_metrics, threshold_curve, shape\nfrom _minpy_a2da5d2bfd8409ca.registration_audit import Provenance, classify, audit_record\n\n__all__ = ['counts_metrics', 'threshold_curve', 'shape', 'Provenance', 'classify', 'audit_record']\n",
    "registration_audit": "\"\"\"Audit provenance labels without guessing preregistration from posthoc=false.\n\nThis module is deliberately stdlib-only.  It validates metadata contracts; it does\nnot rewrite research results.\n\"\"\"\nfrom __future__ import annotations\n\nfrom dataclasses import dataclass\nfrom pathlib import Path\nimport re\nimport tomllib\n\n\n@dataclass(frozen=True)\nclass Provenance:\n    status: str\n    evidence: str | None = None\n\n\ndef _has_text_evidence(value: object) -> bool:\n    \"\"\"Require a named record, not a truthy value coerced to text.\"\"\"\n    return isinstance(value, str) and bool(value.strip())\n\n\ndef classify(record: dict) -> Provenance:\n    \"\"\"Return only statuses supported by explicit machine-readable evidence.\"\"\"\n    if record.get(\"posthoc\") is True:\n        return Provenance(\"posthoc\", \"posthoc=true\")\n    prereg = record.get(\"preregistration\")\n    if isinstance(prereg, dict) and prereg.get(\"recorded_before_evaluation\") is True and _has_text_evidence(prereg.get(\"evidence\")):\n        return Provenance(\"preregistered\", prereg[\"evidence\"])\n    # Missing or false posthoc is deliberately not evidence of preregistration.\n    return Provenance(\"unknown\")\n\n\ndef audit_record(record: dict) -> list[str]:\n    errors = []\n    if record.get(\"posthoc\") is True and record.get(\"preregistration\"):\n        errors.append(\"posthoc and preregistration cannot both be asserted\")\n    prereg = record.get(\"preregistration\")\n    if prereg is not None:\n        if not isinstance(prereg, dict):\n            errors.append(\"preregistration must be a table\")\n        else:\n            if prereg.get(\"recorded_before_evaluation\") is not True:\n                errors.append(\"preregistration requires recorded_before_evaluation=true\")\n            if not _has_text_evidence(prereg.get(\"evidence\")):\n                errors.append(\"preregistration requires non-blank text evidence\")\n    return errors\n\n\ndef load_exprs(path: Path) -> list[dict]:\n    data = tomllib.loads(path.read_text(encoding=\"utf-8\"))\n    return list(data.get(\"expr\", []))\n\n\ndef narrative_candidates(path: Path) -> dict[str, str]:\n    \"\"\"Find comments claiming an expression family was written before evaluation.\n\n    These are audit leads only.  A comment never upgrades a record automatically.\n    \"\"\"\n    current = None\n    leads: dict[str, str] = {}\n    for raw in path.read_text(encoding=\"utf-8\").splitlines():\n        line = raw.strip()\n        if line.startswith(\"#\") and (\"\u8a08\u7b97\u524d\u306b\u66f8\u3044\u305f\" in line or \"\u5224\u5b9a\u306f\u307e\u3060\" in line):\n            current = line.lstrip(\"#\").strip()\n            continue\n        m = re.fullmatch(r'id\\s*=\\s*\"(E\\d+)\"', line)\n        if m and current:\n            leads[m.group(1)] = current\n        if line.startswith(\"#\") and current and not (\"\u8a08\u7b97\u524d\u306b\u66f8\u3044\u305f\" in line or \"\u5224\u5b9a\u306f\u307e\u3060\" in line):\n            current = None\n    return leads\n",
    "score_math": "\"\"\"Generic numerical kernels extracted from PythDRagoras season_sensitivity.\n\nThe original research adapter remains in Aoi. Threshold sweep sorting costs\nO(n log n); subsequent updates cost O(n + t), rather than O(n*t) recounts.\nNo model fitting, sport-specific scores or significance verdicts are included.\n\"\"\"\nimport math\nfrom _minpy_a2da5d2bfd8409ca.period_comparison import finite\n\n\ndef validate_grid(values, name):\n    if not values or not all(finite(v) for v in values) or any(a >= b for a, b in zip(values, values[1:])):\n        raise ValueError(f'{name}: finite, strictly increasing grid required')\n\n\ndef counts_metrics(tp, fp, fn, tn):\n    if any(type(v) is not int or v < 0 for v in (tp, fp, fn, tn)):\n        raise ValueError(\"nonnegative integer counts required\")\n    n = tp + fp + fn + tn\n    den = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)\n    yes, no = tp + fp, fn + tn\n    p_yes, p_no = (tp / yes if yes else None), (fn / no if no else None)\n    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'n': n,\n            'mcc': (tp*tn-fp*fn)/math.sqrt(den) if den else None,\n            'p_outcome_given_high': p_yes, 'p_outcome_given_low': p_no,\n            'probability_gap': p_yes-p_no if p_yes is not None and p_no is not None else None}\n\n\ndef threshold_curve(scores, outcomes, thresholds):\n    \"\"\"Exact sweep: start with every row high, remove rows as the threshold advances.\"\"\"\n    validate_grid(thresholds, 'thresholds')\n    if len(scores) != len(outcomes) or not all(finite(s) for s in scores) or not all(type(y) is bool for y in outcomes):\n        raise ValueError('finite scores and aligned Boolean outcomes required')\n    ordered = sorted(zip(scores, outcomes))\n    tp, fp, fn, tn = sum(outcomes), len(outcomes)-sum(outcomes), 0, 0\n    result, cursor = [], 0\n    for threshold in thresholds:\n        changed = 0\n        while cursor < len(ordered) and ordered[cursor][0] < threshold:\n            _, y = ordered[cursor]\n            tp -= y\n            fn += y\n            fp -= not y\n            tn += not y\n            cursor += 1\n            changed += 1\n        result.append({'threshold': threshold, 'crossed_units': changed, **counts_metrics(tp, fp, fn, tn)})\n    return result\n\n\ndef shape(points, x='threshold', y='mcc'):\n    \"\"\"Finite differences/trapezoids on sampled values; never a smooth derivative claim.\"\"\"\n    validate_grid([p[x] for p in points], x)\n    if any(p[y] is not None and not finite(p[y]) for p in points):\n        raise ValueError(\"finite ordinates or None required\")\n    slopes, area, span = [], 0.0, 0.0\n    for left, right in zip(points, points[1:]):\n        dx = right[x]-left[x]\n        valid = left[y] is not None and right[y] is not None\n        slopes.append({'left': left[x], 'right': right[x],\n                       'slope': (right[y]-left[y])/dx if valid else None})\n        if valid:\n            area += dx*(left[y]+right[y])/2\n            span += dx\n    bends = []\n    for a, b in zip(slopes, slopes[1:]):\n        if a['slope'] is not None and b['slope'] is not None:\n            dx = (b['left']+b['right']-a['left']-a['right'])/2\n            bends.append({'at': a['right'], 'slope_change_per_unit': (b['slope']-a['slope'])/dx})\n    valid = [p for p in points if p[y] is not None]\n    best = max((p[y] for p in valid), default=None)\n    # Consecutive equal maxima are represented as intervals, including one-point peaks.\n    plateaus = []\n    for i, p in enumerate(points):\n        if best is not None and p[y] == best:\n            if i and points[i-1][y] == best:\n                plateaus[-1]['end'] = p[x]\n            else:\n                plateaus.append({'start': p[x], 'end': p[x]})\n    extrema = []\n    for a, b, c in zip(points, points[1:], points[2:]):\n        if all(p[y] is not None for p in (a, b, c)):\n            if b[y] > a[y] and b[y] > c[y]:\n                extrema.append({'at': b[x], 'kind': 'sampled_max'})\n            if b[y] < a[y] and b[y] < c[y]:\n                extrema.append({'at': b[x], 'kind': 'sampled_min'})\n    return {'finite_slopes': slopes, 'slope_changes': bends, 'sampled_extrema': extrema,\n            'max_intervals': plateaus, 'trapezoid_area': area if span else None,\n            'covered_span': span, 'mean_over_grid': area/span if span else None}\n",
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
