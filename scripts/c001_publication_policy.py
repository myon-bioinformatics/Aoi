"""c001-specific publication conditions; research verdicts are NOT gate statuses."""
from __future__ import annotations

from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "nagoyaction"))
import publication_gate as gate

KINDS = (("propositions.jsonl", "proposition", "P"), ("sets.jsonl", "expression", "E"))
DEFINITIONS = ("pipeline.toml", "analysis.toml", "claims.toml", "hypotheses.toml",
               "propositions.toml", "sets.toml", "rule_candidates.toml", "rule_candidates_r21.toml")
FROZEN = ("season.jsonl", "propositions.jsonl", "sets.jsonl", "trajectory_sensitivity_units.jsonl")
STAGES = {
    "freeze": ("input-manifest.json", "annual-recalculated.jsonl", "annual-formula-audit.json",
               *(f"v1/{name}" for name in FROZEN), *(f"definitions/{name}" for name in DEFINITIONS)),
    "replay": ("replay-receipt.jsonl", *(f"v2/{name}" for name in FROZEN)),
    "compare": ("c001-replay-diff.json",),
    "annotate": ("v2/annotated/verification-summary.json", "v2/annotated/propositions.jsonl", "v2/annotated/sets.jsonl"),
}


def rows(path, key="id"):
    result = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = gate.loads(line)
        if not isinstance(row, dict) or not isinstance(row.get(key), str) or not row[key]:
            raise ValueError(f"invalid {key} in {path}")
        if row[key] in result:
            raise ValueError(f"duplicate {key}: {row[key]}")
        result[row[key]] = row
    return result


def same(a, b):
    return (gate.json.dumps(a, sort_keys=True, ensure_ascii=False, allow_nan=False)
            == gate.json.dumps(b, sort_keys=True, ensure_ascii=False, allow_nan=False))


def full_diff(old, new, path=()):
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(old.keys() | new.keys()):
            if key not in old or key not in new:
                yield {"path": [*path, key], "change": "presence"}
            else:
                yield from full_diff(old[key], new[key], (*path, key))
    elif isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            yield {"path": list(path), "change": "length"}
        else:
            for idx, (a, b) in enumerate(zip(old, new)):
                yield from full_diff(a, b, (*path, idx))
    elif not same(old, new):
        yield {"path": list(path), "v1": old, "v2": new}


def evaluate(audit, env=None):
    """Require a complete bounded replay; any unresolved difference holds all IDs.

    This deliberately does not infer unaffected research dependencies. Evidence
    is retained on a hold. Normal Refuted/Inconclusive verdicts remain eligible.
    """
    root = Path(audit).resolve()
    evidence = gate.inspect(root, STAGES, env)
    ident = evidence["identity"]
    manifest = gate.read_json(root / "input-manifest.json")
    if (not isinstance(manifest, dict) or manifest.get("mode") != "saved_annual_input_replay" or manifest.get("raw_source_replayed") is not False
            or manifest.get("initialization_status") != "complete"
            or any(manifest.get(k) != ident[k] for k in ("harness_sha", "research_sha"))):
        raise ValueError("frozen manifest/identity mismatch")
    for name in FROZEN + DEFINITIONS:
        subdir = "v1" if name in FROZEN else "definitions"
        if manifest.get("inputs", {}).get(name) != gate.digest(root / subdir / name):
            raise ValueError(f"frozen manifest hash mismatch: {name}")
    summary = gate.read_json(root / "v2/annotated/verification-summary.json")
    if (not isinstance(summary, dict) or summary.get("dataset_version") != "V2" or summary.get("source_validation") != "skipped"
            or any(summary.get(k) != ident[k] for k in ("harness_sha", "research_sha"))):
        raise ValueError("annotation summary identity/scope mismatch")
    receipts = rows(root / "replay-receipt.jsonl", "step")
    checks = {f"stage:{name}": code == 0 for name, code in evidence["stage_returncodes"].items()}
    for name in ("question", "sets", "judge"):
        row = receipts.get(name, {})
        if "skipped" in row and type(row["skipped"]) is not bool:
            raise ValueError("invalid skipped receipt")
        if row.get("skipped") is True and row.get("returncode") is not None:
            raise ValueError("conflicting receipt")
        checks[f"step:{name}"] = (type(row.get("returncode")) is int
                                  and row["returncode"] == 0 and not row.get("skipped", False))
    for name in ("season.jsonl", "trajectory_sensitivity_units.jsonl"):
        checks[f"inherited:{name}"] = gate.digest(root / "v1" / name) == gate.digest(root / "v2" / name)
    comparison = gate.read_json(root / "c001-replay-diff.json")
    annual = gate.read_json(root / "annual-formula-audit.json")
    for name, report in (("comparison", comparison), ("annual", annual)):
        if (not isinstance(report, dict) or type(report.get("differences")) is not int or report["differences"] < 0
                or not isinstance(report.get("items"), list) or len(report["items"]) != report["differences"]):
            raise ValueError(f"invalid {name} difference report")
        checks[f"zero_differences:{name}"] = report["differences"] == 0
    checks["comparison_complete"] = (comparison.get("comparison_status") == "complete"
                                     and comparison.get("replay_outcome") == "success")
    if comparison.get("annual_formula_differences") != annual["differences"]:
        raise ValueError("comparison/annual report conflict")
    differences, candidates = [], []
    for filename, kind, prefix in KINDS:
        old, new = (rows(root / side / filename) for side in ("v1", "v2"))
        annotated = rows(root / "v2/annotated" / filename)
        checks[f"nonempty:{kind}"] = bool(old and new)
        checks[f"same_ids:{kind}"] = old.keys() == new.keys() == annotated.keys()
        for ident_ in sorted(old.keys() & new.keys()):
            for difference in full_diff(old[ident_], new[ident_]):
                allowed = (kind == "proposition" and difference["path"] == ["meta", "code_version"]
                           and isinstance(difference.get("v1"), str)
                           and re.fullmatch(r"[a-f0-9]{40}", difference["v1"]) is not None
                           and difference.get("v2") == ident["research_sha"])
                differences.append({"kind": kind, "source_id": ident_, **difference,
                                    "category": "execution_revision" if allowed else "unresolved"})
        for source_id, row in annotated.items():
            verification = row.get("verification")
            if not isinstance(verification, dict):
                raise ValueError("missing annotation verification")
            status = verification.get("verification_status")
            if status in {"skipped", "unavailable", "failed", "different"}:
                continue
            if (status != "replayed" or verification.get("value_origin") != "V2"
                    or verification.get("verification_scope") != "downstream_replay_on_V1_inputs"
                    or verification.get("source_validation") != "skipped"
                    or source_id not in new or not same(row.get("data"), new[source_id])
                    or row.get("source_sha256") != gate.digest(root / "v2" / filename)):
                raise ValueError(f"annotation/raw output mismatch: {source_id}")
            candidates.append((kind, prefix, row))
    unresolved = sum(d["category"] == "unresolved" for d in differences)
    checks["no_unresolved_full_field_differences"] = unresolved == 0
    checks["nonempty_candidates"] = bool(candidates)
    report = gate.decide(evidence, checks)
    report.update(policy="c001-complete-saved-input-replay/1",
                  full_field_differences=len(differences), unresolved_differences=unresolved,
                  provenance_differences=len(differences) - unresolved, difference_items=differences,
                  scope="downstream_replay_on_V1_inputs", candidate_results=len(candidates),
                  exit_code=0 if report["allowed"] else (64 if any(
                      code != 0 and not (name == "compare" and code == 1)
                      for name, code in evidence["stage_returncodes"].items()) or not all(
                      checks[f"step:{name}"] for name in ("question", "sets", "judge")) else 1))
    return report, candidates
