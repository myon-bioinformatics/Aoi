"""Execute one bounded c001 stage and seal its evidence under this execution ID."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import sys

from c001_publication_policy import STAGES, DEFINITIONS, FROZEN, gate


def freeze(audit, research):
    observed = gate.identity(audit)
    source = research / "cycles/c001-chunichi/outputs"
    v1, v2 = audit / "v1", audit / "v2"
    v1.mkdir(); v2.mkdir()
    manifest = {"mode": "saved_annual_input_replay", "raw_source_replayed": False,
                "harness_sha": observed["harness_sha"], "research_sha": observed["research_sha"],
                "execution_identity_sha256": gate.digest(audit / "execution-identity.json"),
                "inputs": {}, "initialization_status": "in_progress",
                "not_recomputed": {"acquisition_and_raw_parsing": "saved inputs; no NPB requests",
                                   "game_to_season_aggregation": "V1 inherited",
                                   "daily_trajectory_and_game_detail_features": "V1 inherited",
                                   "2026_provisional_and_rule_search": "outside bounded replay"}}
    gate.write_json(audit / "input-manifest.json", manifest)
    for name in FROZEN:
        src = source / name
        if not src.is_file() or src.stat().st_size == 0:
            raise ValueError(f"missing/empty frozen file: {name}")
        shutil.copy2(src, v1 / name)
        manifest["inputs"][name] = gate.digest(src)
    for name in ("season.jsonl", "trajectory_sensitivity_units.jsonl"):
        shutil.copy2(v1 / name, v2 / name)
    if (source / "fetched").is_dir():
        shutil.copytree(source / "fetched", v2 / "fetched")
    (audit / "definitions").mkdir()
    for name in DEFINITIONS:
        src = source.parent / name
        shutil.copy2(src, audit / "definitions" / name)
        manifest["inputs"][name] = gate.digest(src)
    data = [gate.loads(line) for line in (v1 / "season.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    units = [(r["season"], r["team"]) for r in data]
    if not data or len(set(units)) != len(units):
        raise ValueError("empty/duplicate annual units")
    computed, differences, skipped = [], [], []
    compared = 0
    for row in data:
        unit = {"season": row["season"], "team": row["team"]}
        keys = ("W", "L", "T", "RF", "RA")
        if any(row.get(key) is None for key in keys):
            skipped.append({**unit, "reason": "missing_annual_counts"}); continue
        values = [row[key] for key in keys]
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0 or int(v) != v for v in values):
            raise ValueError("invalid annual counts")
        w, loss, ties, rf, ra = values
        games, decisions = w + loss + ties, w + loss
        if row.get("G") is not None and row["G"] != games:
            raise ValueError("G != W+L+T")
        wpct = w / decisions if decisions else None
        denom = rf ** 1.83 + ra ** 1.83
        pythag = rf ** 1.83 / denom if denom else None
        metrics = {"G": games, "wpct": wpct, "RF_per_game": rf / games if games else None,
                   "RA_per_game": ra / games if games else None, "rd": rf - ra,
                   "pythag_fixed": pythag,
                   "resid_fixed": wpct - pythag if wpct is not None and pythag is not None else None,
                   "wins_vs_pythag": w - decisions * pythag if pythag is not None else None}
        computed.append({**unit, **metrics})
        for field, value in metrics.items():
            if row.get(field) is None or value is None:
                continue
            compared += 1
            if not math.isclose(float(row[field]), value, rel_tol=0, abs_tol=1e-12):
                differences.append({**unit, "field": field, "v1": row[field], "recomputed": value})
    (audit / "annual-recalculated.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in computed), encoding="utf-8")
    gate.write_json(audit / "annual-formula-audit.json", {
        "source": "frozen season aggregates; not independently source validated", "fixed_exponent": 1.83,
        "input_units": len(data), "recomputed_units": len(computed), "comparable_fields": compared,
        "skipped": skipped, "differences": len(differences), "items": differences})
    manifest.update(initialization_status="complete", input_units=len(data),
                    seasons=sorted({r["season"] for r in data}),
                    inherited_columns=sorted(set().union(*(r.keys() for r in data))))
    gate.write_json(audit / "input-manifest.json", manifest)
    return 0


def replay(audit, research):
    import nagoyaction
    pipeline = nagoyaction.load(research / "cycles/c001-chunichi/pipeline.toml")
    by_name = {s["name"]: s for s in pipeline["step"]}
    pipeline["step"] = [by_name[name] for name in ("question", "sets", "judge")]
    if any(s.get("network") for s in pipeline["step"]):
        raise ValueError("network step in saved-input replay")
    pipeline["vars"]["out"] = str(audit / "v2")
    return nagoyaction.run(pipeline, offline=True, receipt=audit / "replay-receipt.jsonl")


def compare(audit, research):
    import compare_c001_replay as comparator
    from c001_publication_policy import rows
    report = {"mode": "saved_annual_input_replay", "raw_source_replayed": False,
              "comparison_status": "not_run", "differences": None}
    try:
        execution = gate.read_json(audit / "stage-evidence/replay.json")
        if execution["returncode"] != 0:
            raise ValueError("replay did not complete; no semantic difference count")
        for side in ("v1", "v2"):
            for name in ("propositions.jsonl", "sets.jsonl"):
                if not rows(audit / side / name):
                    raise ValueError("empty output is not successful comparison")
        differences = comparator.compare_dirs(audit / "v1", audit / "v2")
        annual = gate.read_json(audit / "annual-formula-audit.json")
        report.update(replay_outcome="success", comparison_status="complete",
                      differences=len(differences), items=differences,
                      annual_formula_differences=annual["differences"])
        code = 1 if differences or annual["differences"] else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report.update(comparison_status="failed", replay_outcome="incomplete", error=str(exc))
        code = 64
    gate.write_json(audit / "c001-replay-diff.json", report)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--research", type=Path, default=Path("research"))
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    audit, research = args.audit.resolve(), args.research.resolve()
    try:
        if args.child:
            if args.stage == "annotate":
                import annotate_c001_replay
                return annotate_c001_replay.main([str(audit)])
            return {"freeze": freeze, "replay": replay, "compare": compare}[args.stage](audit, research)
        command = [sys.executable, "-S", str(Path(__file__).resolve()), args.stage,
                   "--audit", str(audit), "--research", str(research), "--child"]
        return gate.record_command(audit, args.stage, STAGES[args.stage], command)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(64, f"Invalid c001 stage: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
