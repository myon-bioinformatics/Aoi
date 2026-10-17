#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: 2bf96800b682c9b58b438e1d274267e3fcf832a3
# entry: distributions/entries/pythdragoras_api.py
# entry-module: pythdragoras_api
# search-paths: distributions/entries,pythdragoras
# allow: 
# allow-cycles: no
# cycles: 
# modules: pythdragoras_api,registration_audit,score_sensitivity
# prefix: _minpy_624012f88b54f537
# content-sha256: 0d2aee0bb66c060fe616e9d78b8688d3941be0e357a947f25502b5d6a34cca80
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_624012f88b54f537"
_MINPY_ENTRY = "pythdragoras_api"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "pythdragoras_api": "\"\"\"PythDRagoras min: exact score sensitivity and research provenance checks.\"\"\"\nfrom _minpy_624012f88b54f537.score_sensitivity import ScoreState, team_games, sweep, analyze\nfrom _minpy_624012f88b54f537.registration_audit import Provenance, classify, audit_record\n\n__all__ = ['ScoreState', 'team_games', 'sweep', 'analyze', 'Provenance', 'classify', 'audit_record']\n",
    "registration_audit": "\"\"\"Audit provenance labels without guessing preregistration from posthoc=false.\n\nThis module is deliberately stdlib-only.  It validates metadata contracts; it does\nnot rewrite research results.\n\"\"\"\nfrom __future__ import annotations\n\nfrom dataclasses import dataclass\nfrom pathlib import Path\nimport re\nimport tomllib\n\n\n@dataclass(frozen=True)\nclass Provenance:\n    status: str\n    evidence: str | None = None\n\n\ndef _has_text_evidence(value: object) -> bool:\n    \"\"\"Require a named record, not a truthy value coerced to text.\"\"\"\n    return isinstance(value, str) and bool(value.strip())\n\n\ndef classify(record: dict) -> Provenance:\n    \"\"\"Return only statuses supported by explicit machine-readable evidence.\"\"\"\n    if record.get(\"posthoc\") is True:\n        return Provenance(\"posthoc\", \"posthoc=true\")\n    prereg = record.get(\"preregistration\")\n    if isinstance(prereg, dict) and prereg.get(\"recorded_before_evaluation\") is True and _has_text_evidence(prereg.get(\"evidence\")):\n        return Provenance(\"preregistered\", prereg[\"evidence\"])\n    # Missing or false posthoc is deliberately not evidence of preregistration.\n    return Provenance(\"unknown\")\n\n\ndef audit_record(record: dict) -> list[str]:\n    errors = []\n    if record.get(\"posthoc\") is True and record.get(\"preregistration\"):\n        errors.append(\"posthoc and preregistration cannot both be asserted\")\n    prereg = record.get(\"preregistration\")\n    if prereg is not None:\n        if not isinstance(prereg, dict):\n            errors.append(\"preregistration must be a table\")\n        else:\n            if prereg.get(\"recorded_before_evaluation\") is not True:\n                errors.append(\"preregistration requires recorded_before_evaluation=true\")\n            if not _has_text_evidence(prereg.get(\"evidence\")):\n                errors.append(\"preregistration requires non-blank text evidence\")\n    return errors\n\n\ndef load_exprs(path: Path) -> list[dict]:\n    data = tomllib.loads(path.read_text(encoding=\"utf-8\"))\n    return list(data.get(\"expr\", []))\n\n\ndef narrative_candidates(path: Path) -> dict[str, str]:\n    \"\"\"Find comments claiming an expression family was written before evaluation.\n\n    These are audit leads only.  A comment never upgrades a record automatically.\n    \"\"\"\n    current = None\n    leads: dict[str, str] = {}\n    for raw in path.read_text(encoding=\"utf-8\").splitlines():\n        line = raw.strip()\n        if line.startswith(\"#\") and (\"\u8a08\u7b97\u524d\u306b\u66f8\u3044\u305f\" in line or \"\u5224\u5b9a\u306f\u307e\u3060\" in line):\n            current = line.lstrip(\"#\").strip()\n            continue\n        m = re.fullmatch(r'id\\s*=\\s*\"(E\\d+)\"', line)\n        if m and current:\n            leads[m.group(1)] = current\n        if line.startswith(\"#\") and current and not (\"\u8a08\u7b97\u524d\u306b\u66f8\u3044\u305f\" in line or \"\u5224\u5b9a\u306f\u307e\u3060\" in line):\n            current = None\n    return leads\n",
    "score_sensitivity": "\"\"\"One-coordinate score counterfactuals with exact incremental sufficient statistics.\n\nThis is an exploratory sensitivity calculation, not an NNUE network or causal model.\nOnly final scores change; opponents' scores in the same game change consistently.\nNo standings, inning sequence, or downstream game decisions are simulated.\n\"\"\"\nfrom __future__ import annotations\n\nimport argparse\nfrom dataclasses import dataclass\nfrom datetime import date\nimport json\nfrom pathlib import Path\nimport tomllib\n\n\n@dataclass\nclass ScoreState:\n    RF: int = 0\n    RA: int = 0\n    W: int = 0\n    L: int = 0\n    T: int = 0\n\n    def update(self, rf: int, ra: int, sign: int = 1) -> None:\n        self.RF += sign * rf\n        self.RA += sign * ra\n        self.W += sign * (rf > ra)\n        self.L += sign * (rf < ra)\n        self.T += sign * (rf == ra)\n\n    def metrics(self) -> dict:\n        decided = self.W + self.L\n        total = self.RF ** 1.83 + self.RA ** 1.83\n        p = self.RF ** 1.83 / total if total else None\n        return {**vars(self), \"wpct\": self.W / decided if decided else None,\n                \"pythag_fixed\": p,\n                \"expected_wins\": decided * p if p is not None else None}\n\n\ndef _delta(now: dict, before: dict) -> dict:\n    return {k: now[k] - before[k] if now[k] is not None and before[k] is not None else None\n            for k in now}\n\n\ndef team_games(games: list[dict], team: str) -> list[dict]:\n    \"\"\"Validate the complete observation input before selecting a team.\"\"\"\n    seen, out = set(), []\n    for g in games:\n        key = g[\"key\"]\n        if not isinstance(key, str) or not key or key in seen:\n            raise ValueError(f\"duplicate/invalid game key: {key!r}\")\n        seen.add(key)\n        day = date.fromisoformat(g[\"date\"])\n        if not isinstance(g[\"home\"], str) or not isinstance(g[\"away\"], str) or g[\"home\"] == g[\"away\"]:\n            raise ValueError(f\"invalid teams: {key}\")\n        for col in (\"hs\", \"as\"):\n            if type(g[col]) is not int or g[col] < 0:\n                raise ValueError(f\"nonnegative integer score required: {key}/{col}\")\n        if team in (g[\"home\"], g[\"away\"]):\n            home = team == g[\"home\"]\n            out.append({\"key\": key, \"date\": day.isoformat(), \"season\": day.year,\n                        \"rf\": g[\"hs\"] if home else g[\"as\"],\n                        \"ra\": g[\"as\"] if home else g[\"hs\"]})\n    if not out:\n        raise ValueError(f\"no observations for team: {team}\")\n    return sorted(out, key=lambda g: (g[\"date\"], g[\"key\"]))\n\n\ndef sweep(games: list[dict], axis: str, max_step: int = 3) -> dict:\n    \"\"\"Increase RF or decrease RA by 0..max_step runs per game.\n\n    Each step starts from the preceding state; remove the old game contribution,\n    add the new one. RA has an explicit zero floor. Every game remains in sample.\n    Timeline records the cumulative intervention over chronological games, holding\n    all not-yet-edited games at their preceding-step values (not a forecast).\n    \"\"\"\n    if axis not in (\"RF\", \"RA\") or type(max_step) is not int or max_step < 1:\n        raise ValueError(\"axis must be RF/RA and max_step a positive integer\")\n    state = ScoreState()\n    scores = [(g[\"rf\"], g[\"ra\"]) for g in games]\n    for rf, ra in scores:\n        state.update(rf, ra)\n    baseline = state.metrics()\n    curve = [{\"step\": 0, \"changed_runs\": 0, \"metrics\": baseline,\n              \"delta\": _delta(baseline, baseline)}]\n    timeline, budget = [], 0\n    for step in range(1, max_step + 1):\n        for i, g in enumerate(games):\n            old_rf, old_ra = scores[i]\n            rf = g[\"rf\"] + step if axis == \"RF\" else g[\"rf\"]\n            ra = max(0, g[\"ra\"] - step) if axis == \"RA\" else g[\"ra\"]\n            if (rf, ra) == scores[i]:\n                continue\n            before = state.metrics()\n            state.update(old_rf, old_ra, -1)\n            state.update(rf, ra)\n            scores[i] = (rf, ra)\n            budget += abs(rf - old_rf) + abs(ra - old_ra)\n            now = state.metrics()\n            timeline.append({\"step\": step, \"key\": g[\"key\"], \"date\": g[\"date\"],\n                             \"old\": [old_rf, old_ra], \"new\": [rf, ra],\n                             \"changed_runs\": budget, \"metrics\": now,\n                             \"local_delta\": _delta(now, before), \"delta\": _delta(now, baseline)})\n        now = state.metrics()\n        curve.append({\"step\": step, \"changed_runs\": budget, \"metrics\": now,\n                      \"delta\": _delta(now, baseline)})\n    return {\"axis\": axis, \"baseline\": baseline, \"curve\": curve, \"timeline\": timeline}\n\n\ndef analyze(games: list[dict], team: str, *, max_step: int = 3,\n            excluded: list[dict] = (), holdout: list[int] = (), min_seasons: int = 3) -> dict:\n    if type(min_seasons) is not int or min_seasons < 1:\n        raise ValueError(\"min_seasons must be positive\")\n    if any(not str(e.get(\"reason\", \"\")).strip() for e in excluded):\n        raise ValueError(\"exclusions require reasons\")\n    rows = team_games(games, team)\n    excluded_years = {e[\"season\"] for e in excluded}\n    seasons = sorted({g[\"season\"] for g in rows} - excluded_years)\n    results, candidates = [], []\n    for axis in (\"RF\", \"RA\"):\n        training = []\n        for season in seasons:\n            result = sweep([g for g in rows if g[\"season\"] == season], axis, max_step)\n            result.update(season=season, role=\"holdout\" if season in holdout else \"exploration\")\n            results.append(result)\n            if season not in holdout:\n                training.append(result)\n        # Compare at the preregistered first step; larger steps are sensitivity only.\n        changed = sum(r[\"curve\"][1][\"changed_runs\"] for r in training)\n        net = sum(r[\"curve\"][1][\"delta\"][\"W\"] - r[\"curve\"][1][\"delta\"][\"L\"] for r in training)\n        positive = sum(r[\"curve\"][1][\"delta\"][\"W\"] - r[\"curve\"][1][\"delta\"][\"L\"] > 0 for r in training)\n        eligible = len(training) >= min_seasons and positive == len(training) and changed > 0\n        candidates.append({\"axis\": axis, \"step\": 1, \"seasons\": len(training),\n                           \"positive_seasons\": positive, \"changed_runs\": changed,\n                           \"net_wins_delta\": net, \"net_wins_per_changed_run\": net / changed if changed else None,\n                           \"status\": \"exploratory_candidate\" if eligible else \"insufficient_evidence\",\n                           \"proposition\": f\"{team}: {axis}\u3092\u5404\u8a66\u54081\u70b9\u6539\u5584\u3059\u308b\u53cd\u5b9f\u4eee\u60f3\u3067\u306f\u52dd\u3061\u8d8a\u3057\u6570\u304c\u5897\u3048\u308b\"})\n    candidates.sort(key=lambda c: (c[\"status\"] == \"exploratory_candidate\",\n                                   c[\"net_wins_per_changed_run\"] or 0), reverse=True)\n    return {\"schema\": \"aoi-score-sensitivity/1\", \"team\": team,\n            \"policy\": {\"max_step\": max_step, \"min_seasons\": min_seasons,\n                       \"selection_step\": 1, \"excluded\": list(excluded), \"holdout\": list(holdout),\n                       \"RA_floor\": 0, \"ranking\": \"net wins delta / actual changed runs\",\n                       \"candidate_rule\": \"at least min_seasons exploration years; positive net wins delta in every year\",\n                       \"interpretation\": \"\u63a2\u7d22\u7528\u306e\u5f97\u5931\u70b9\u611f\u5ea6\u3002\u5b9f\u884c\u53ef\u80fd\u6027\u30fb\u56e0\u679c\u52b9\u679c\u30fb\u9806\u4f4d\u30fbA\u30af\u30e9\u30b9\u78ba\u7387\u306f\u793a\u3055\u306a\u3044\u3002\u5019\u88dc\u306e\u652f\u6301\u5224\u5b9a\u306b\u306f\u72ec\u7acb\u691c\u8a3c\u304c\u5fc5\u8981\u3002\"},\n            \"results\": results, \"candidates\": candidates}\n\n\ndef main() -> None:\n    parser = argparse.ArgumentParser(description=__doc__)\n    parser.add_argument(\"--games\", type=Path, required=True)\n    parser.add_argument(\"--config\", type=Path, required=True)\n    parser.add_argument(\"--team\")\n    parser.add_argument(\"--max-step\", type=int, default=3)\n    parser.add_argument(\"--min-seasons\", type=int, default=3)\n    parser.add_argument(\"--out\", type=Path, required=True)\n    args = parser.parse_args()\n    config = tomllib.loads(args.config.read_text(encoding=\"utf-8\"))\n    team = args.team or config[\"focus\"][\"team\"]\n    if team not in config[\"teams\"]:\n        parser.error(f\"undefined team: {team}\")\n    games = [json.loads(line) for line in args.games.read_text(encoding=\"utf-8\").splitlines() if line.strip()]\n    result = analyze(games, team, max_step=args.max_step, min_seasons=args.min_seasons,\n                     excluded=config.get(\"exclude\", []), holdout=config.get(\"confirm\", {}).get(\"seasons\", []))\n    args.out.parent.mkdir(parents=True, exist_ok=True)\n    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + \"\\n\", encoding=\"utf-8\")\n\n\nif __name__ == \"__main__\":\n    main()\n",
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
