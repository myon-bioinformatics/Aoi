"""Publish V2 evidence with per-value V1/V2 verification labels (stdlib only).

Raw comparator inputs are never rewritten. Annotated rows live in v2/annotated/;
replayed on V1 inputs is not independently source-validated. Missing evidence
never promotes a value. A failed step remains failed, even when V1 is retained.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "c001-verification/1"
IDENTITY = {"season", "team", "team_name", "league"}
FORMULAS = {
    "G": "W + L + T", "wpct": "W / (W + L)",
    "RF_per_game": "RF / (W + L + T)", "RA_per_game": "RA / (W + L + T)",
    "rd": "RF - RA", "pythag_fixed": "RF**1.83 / (RF**1.83 + RA**1.83)",
    "resid_fixed": "wpct - pythag_fixed", "wins_vs_pythag": "W - (W + L) * pythag_fixed",
}


def _reject_constant(value):
    raise ValueError(f"Non-finite JSON constant: {value}")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)


def read_rows(path: Path, keys: tuple[str, ...], *, allow_empty=False) -> dict:
    """An absent optional file is not an empty successful dataset."""
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line, parse_constant=_reject_constant)
        key = tuple(row[k] for k in keys)
        if any(v is None for v in key) or key in result:
            raise ValueError(f"Missing/duplicate identity in {path.name}: {key}")
        if not isinstance(row, dict):
            raise ValueError(f"Not an object in {path.name}")
        result[key] = row
    if not result and not allow_empty:
        raise ValueError(f"Empty evidence file: {path}")
    return result


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_rows(path: Path, values):
    path.write_text("".join(json.dumps(v, ensure_ascii=False, allow_nan=False) + "\n" for v in values), encoding="utf-8")


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def numeric(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def equal(a, b):
    return numeric(a) and numeric(b) and math.isclose(a, b, abs_tol=1e-12, rel_tol=0)


def formulas(row):
    values = [row.get(k) for k in ("W", "L", "T", "RF", "RA")]
    if any(v is None for v in values):
        return None
    if not all(numeric(v) and v >= 0 and int(v) == v for v in values):
        raise ValueError("Invalid annual counts; corruption is not a missing-input skip")
    w, loss, ties, rf, ra = values
    games, decisions = w + loss + ties, w + loss
    wpct = w / decisions if decisions else None
    denom = rf ** 1.83 + ra ** 1.83
    pythag = rf ** 1.83 / denom if denom else None
    return {"G": games, "wpct": wpct, "RF_per_game": rf / games if games else None,
            "RA_per_game": ra / games if games else None, "rd": rf - ra,
            "pythag_fixed": pythag,
            "resid_fixed": wpct - pythag if wpct is not None and pythag is not None else None,
            "wins_vs_pythag": w - decisions * pythag if pythag is not None else None}


def label(origin, status, scope, reason):
    return {"value_origin": origin,
            "equivalent": "V2" if status in {"verified", "recomputed", "replayed"} else ("V1" if origin == "V1" else "unavailable"),
            "verification_status": status, "verification_scope": scope,
            "reason": reason, "source_validation": "skipped"}


def step_state(receipts, step):
    row = receipts.get((step,))
    if row is None:
        return "skipped", "no_execution_receipt"
    if row.get("skipped"):
        return "skipped", row.get("reason") or "step_not_executed"
    if row.get("returncode") == 0 and not isinstance(row.get("returncode"), bool):
        return "replayed", "successful_execution_on_saved_V1_inputs"
    return "failed", f"execution_failed_or_incomplete: {row.get('returncode')}"


def annotate(audit: Path) -> dict:
    audit = audit.resolve()
    manifest = read_json(audit / "input-manifest.json")
    if manifest.get("mode") != "saved_annual_input_replay" or manifest.get("raw_source_replayed") is not False:
        raise ValueError("This annotator requires an explicitly bounded saved-input replay")
    v1, v2 = audit / "v1", audit / "v2"
    annual_path = audit / "annual-recalculated.jsonl"
    originals = read_rows(v1 / "season.jsonl", ("season", "team"))
    current = read_rows(v2 / "season.jsonl", ("season", "team"))
    if current and current != originals:
        raise ValueError("The inherited V2 season input changed; do not silently relabel it")
    # Authenticate the frozen inputs used by this annotation against the run manifest.
    inputs = manifest.get("inputs", {})
    for name in ("season.jsonl", "propositions.jsonl", "sets.jsonl", "trajectory_sensitivity_units.jsonl"):
        actual = sha(v1 / name)
        if actual is not None and inputs.get(name) != actual:
            raise ValueError(f"Frozen input hash missing or mismatched: {name}")
    annual = read_rows(annual_path, ("season", "team"), allow_empty=True)
    if set(annual) - set(originals):
        raise ValueError("Annual evidence has unknown team-years")
    annual_report_path = audit / "annual-formula-audit.json"
    annual_report = read_json(annual_report_path) if annual_report_path.exists() else None
    annual_executed = (manifest.get("initialization_status") == "complete" and annual_report is not None)
    receipts = read_rows(audit / "replay-receipt.jsonl", ("step",))
    out = v2 / "annotated"
    out.mkdir(parents=True, exist_ok=True)
    states, season_rows, computed_rows = Counter(), [], []
    season_sha = sha(v1 / "season.jsonl")
    mismatches = []
    for key, row in originals.items():
        checks = {}
        expected = formulas(row)
        measured = annual.get(key, {})
        if measured and expected is None:
            raise ValueError(f"Annual evidence despite missing counts: {key}")
        for field, value in measured.items():
            if field in {"season", "team"}:
                continue
            if field not in FORMULAS or not ((value is None and expected[field] is None) or equal(value, expected[field])):
                raise ValueError(f"Invalid recalculation evidence: {key}/{field}")
        for field, value in row.items():
            if field in IDENTITY:
                continue
            meta = label("V1", "skipped", "not_reaggregated", "outside_recomputed_annual_formulas")
            if value is None:
                meta = label("V1", "unavailable", "none", "missing_legacy_value")
            elif field in FORMULAS:
                if not annual_executed or field not in measured:
                    meta = label("V1", "skipped", "none", "missing_recalculation_evidence")
                elif measured[field] is None:
                    meta = label("V1", "skipped", "annual_formula_on_V1_totals", "undefined_formula")
                elif equal(value, measured[field]):
                    meta = label("V1", "verified", "annual_formula_on_V1_totals", "matched_independent_formula")
                else:
                    meta = label("V1", "different", "annual_formula_on_V1_totals", "formula_mismatch_keep_both_values")
                    mismatches.append({"season": key[0], "team": key[1], "field": field,
                                       "v1": value, "recomputed": measured[field]})
            checks[field] = meta
            states[meta["verification_status"]] += 1
        season_rows.append({"schema": SCHEMA, "data": row, "fields": checks,
                            "identity_fields": sorted(IDENTITY), "source_sha256": season_sha})
        if measured and annual_executed:
            computed_rows.append({"schema": SCHEMA, "data": measured,
                                  "verification": label("V2", "recomputed", "annual_formula_on_V1_totals", "saved_totals_are_unvalidated_inputs"),
                                  "unavailable_fields": sorted(k for k, v in measured.items() if v is None),
                                  "source_sha256": season_sha})
    write_rows(out / "season.jsonl", season_rows)
    write_rows(out / "annual-recalculated.jsonl", computed_rows)
    result_counts = {}
    for name, step in (("propositions.jsonl", "question"), ("sets.jsonl", "sets")):
        old = read_rows(v1 / name, ("id",))
        new = read_rows(v2 / name, ("id",))
        status, reason = step_state(receipts, step)
        if status == "replayed" and not new:
            raise ValueError(f"Successful receipt without generated output: {name}")
        records, counts = [], Counter()
        for key in sorted(old.keys() | new.keys()):
            if status == "replayed" and key in new:
                data = new[key]
                meta = label("V2", "replayed", "downstream_replay_on_V1_inputs", reason)
            elif status == "replayed":
                # A disappeared ID is a difference, NOT permission to promote a V1 fallback.
                data = None
                meta = label("unavailable", "different", "none", "not_emitted_by_successful_replay")
            else:
                data = old.get(key)
                meta = label("V1" if data is not None else "unavailable", status if data is not None else "unavailable", "none", reason)
            records.append({"schema": SCHEMA, "id": key[0], "data": data, "verification": meta,
                            "previous": old.get(key) if data is None else None,
                            "input_verification": "V1 inherited inputs; see annotated/season.jsonl",
                            "source_sha256": sha((v2 if meta["value_origin"] == "V2" else v1) / name)})
            counts[meta["verification_status"]] += 1
        write_rows(out / name, records)
        result_counts[name] = {"execution_status": status, "reason": reason, "rows": len(records), "counts": dict(counts)}
    for path in sorted(v2.glob("*.md")):
        # The adjacent original reports are unchanged; only the explicitly annotated copies carry this banner.
        (out / path.name).write_text(
            "> **V2保存版：検証範囲は部分的です。** 年次入力・日次／明細由来列はV1を継承しています。\n"
            "> 再判定と元データの再検証は別です。スキップ・失敗・未取得はverification-summary.jsonを参照してください。\n\n"
            + path.read_text(encoding="utf-8"), encoding="utf-8")
    sources = {str(p.relative_to(audit)): sha(p) for p in
               (audit / "input-manifest.json", annual_report_path, annual_path, audit / "replay-receipt.jsonl",
                v1 / "season.jsonl", v2 / "season.jsonl", v1 / "propositions.jsonl", v2 / "propositions.jsonl",
                v1 / "sets.jsonl", v2 / "sets.jsonl")}
    summary = {"schema": SCHEMA, "dataset_version": "V2", "verification_coverage": "partial",
               "source_validation": "skipped", "research_sha": manifest.get("research_sha"),
               "harness_sha": manifest.get("harness_sha"), "annual_input_units": len(originals),
               "annual_field_counts": dict(states), "formula_mismatches": mismatches,
               "recomputed_annual_units": len(computed_rows), "outputs": result_counts,
               "inherited_input_files": {n: {"verification_status": "skipped" if sha(v2 / n) else "unavailable",
                                                "reason": "source_reaggregation_not_performed", "sha256": sha(v2 / n)}
                                         for n in ("season.jsonl", "trajectory_sensitivity_units.jsonl")},
               "evidence_sha256": sources, "formula_definitions": FORMULAS,
               "notes": ["V2 is a container version, not blanket verification.",
                         "V1 is retained for skipped/failed work; failures are not converted to successful skips.",
                         "Replayed verdicts may still depend on inherited unvalidated V1 features.",
                         "Null/missing values are never fabricated or replaced with zero."]}
    write_json(out / "verification-summary.json", summary)
    (out / "README.md").write_text(
        "# V2保存版の検証範囲\n\n"
        "V2は保存先の版です。全データがV2相当に検証された、という意味ではありません。\n\n"
        "- `season.jsonl`: `data`はV1入力のままです。`fields`に各指標の出所・検証範囲・スキップ理由を記録しています。\n"
        "- `annual-recalculated.jsonl`: 今回再計算したV2の値です。ただし元の年間合計はV1を信頼した入力です。\n"
        "- `propositions.jsonl` / `sets.jsonl`: 成功receiptがある出力だけV2再判定と記録します。スキップ・失敗はV1を注釈付きで保持します。\n"
        "- `verification-summary.json`: 検証・継承・欠損の件数、入力と証拠のSHA-256、実行版、式を確認できます。\n\n"
        "`equivalent=V2`は記載されたverification_scope内だけです。元データの正しさや命題の成立を保証しません。\n"
        "`value_origin=V1, verification_status=verified`は、旧値を残したまま年間式の整合性を確認した状態です。\n"
        "`skipped`は未検証の継承、`unavailable`は値なし、`failed`は実行不具合、`different`は不一致です。\n"
        "いずれも検証成功の件数には足しません。V1にもない値は推定して埋めません。\n\n"
        "このディレクトリのdata+verificationを一緒に利用してください。親ディレクトリのJSONLは比較用の未注釈原本です。\n",
        encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = annotate(args.audit)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(64, f"Invalid replay evidence: {exc}\n")
    print(json.dumps({k: summary[k] for k in ("verification_coverage", "annual_field_counts", "outputs")}, ensure_ascii=False))
    return 1 if summary["formula_mismatches"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
