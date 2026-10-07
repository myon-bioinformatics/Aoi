"""Coverage labels must not promote inherited values, skipped work or failures."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "annotate_c001_replay.py"
spec = importlib.util.spec_from_file_location("c001_annotations", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "v1").mkdir()
        (self.root / "v2").mkdir()
        row = {"season": 2019, "team": "d", "team_name": "中日", "league": "C",
               "W": 60, "L": 70, "T": 13, "RF": 500, "RA": 520,
               "early_only_metric": 1.25, "missing_detail": None}
        metrics = mod.formulas(row)
        row.update({k: metrics[k] for k in ("G", "wpct", "rd", "pythag_fixed", "resid_fixed", "wins_vs_pythag")})
        self.original = row
        for version in ("v1", "v2"):
            self.rows(f"{version}/season.jsonl", [row])
            self.rows(f"{version}/propositions.jsonl", [{"id": "P1", "verdict": "Refined"}])
            self.rows(f"{version}/sets.jsonl", [{"id": "E1", "verdict": "Supported"}])
        self.rows("annual-recalculated.jsonl", [{"season": 2019, "team": "d", **metrics}])
        self.js("annual-formula-audit.json", {"differences": 0, "input_units": 1})
        self.rows("replay-receipt.jsonl", [{"step": "question", "returncode": 0}, {"step": "sets", "returncode": 0}])
        self.manifest = {"mode": "saved_annual_input_replay", "raw_source_replayed": False,
                         "harness_sha": "a" * 40, "research_sha": "b" * 40, "initialization_status": "complete"}
        self.rehash()

    def js(self, name, value):
        mod.write_json(self.root / name, value)

    def rows(self, name, values):
        mod.write_rows(self.root / name, values)

    def rehash(self):
        self.manifest["inputs"] = {p.name: mod.sha(p) for p in (self.root / "v1").iterdir() if p.is_file()}
        self.js("input-manifest.json", self.manifest)

    def output(self, name):
        return [json.loads(line) for line in (self.root / "v2" / "annotated" / name).read_text(encoding="utf-8").splitlines()]

    def run_audit(self):
        return mod.annotate(self.root)

    def test_verified_formula_does_not_promote_input_origin(self):
        summary = self.run_audit()
        field = self.output("season.jsonl")[0]["fields"]["wpct"]
        self.assertEqual((field["equivalent"], field["value_origin"], field["verification_status"]), ("V2", "V1", "verified"))
        self.assertEqual(field["source_validation"], "skipped")
        self.assertEqual(summary["annual_field_counts"]["verified"], 6)
        self.assertEqual(summary["verification_coverage"], "partial")

    def test_early_only_metric_is_retained_as_unverified_V1(self):
        self.run_audit()
        row = self.output("season.jsonl")[0]
        self.assertEqual(row["data"]["early_only_metric"], 1.25)
        field = row["fields"]["early_only_metric"]
        self.assertEqual((field["equivalent"], field["verification_status"]), ("V1", "skipped"))
        self.assertTrue(field["reason"])

    def test_missing_legacy_value_stays_null_not_zero(self):
        self.run_audit()
        row = self.output("season.jsonl")[0]
        self.assertIsNone(row["data"]["missing_detail"])
        self.assertEqual(row["fields"]["missing_detail"]["verification_status"], "unavailable")
        self.assertNotIn("never_saved_column", row["data"])

    def test_new_calculations_are_V2_but_source_unvalidated(self):
        self.run_audit()
        row = self.output("annual-recalculated.jsonl")[0]
        self.assertEqual(row["verification"]["value_origin"], "V2")
        self.assertEqual(row["verification"]["verification_status"], "recomputed")
        self.assertEqual(row["verification"]["source_validation"], "skipped")
        self.assertAlmostEqual(row["data"]["RF_per_game"], 500 / 143)

    def test_skipped_question_retains_V1_not_stale_V2(self):
        self.rows("v2/propositions.jsonl", [{"id": "P1", "verdict": "different partial output"}])
        self.rows("replay-receipt.jsonl", [{"step": "question", "skipped": True, "reason": "legacy_input_not_saved"}, {"step": "sets", "returncode": 0}])
        summary = self.run_audit()
        row = self.output("propositions.jsonl")[0]
        self.assertEqual(row["data"]["verdict"], "Refined")
        self.assertEqual(row["verification"]["equivalent"], "V1")
        self.assertEqual(row["verification"]["reason"], "legacy_input_not_saved")
        self.assertEqual(summary["outputs"]["sets.jsonl"]["execution_status"], "replayed")

    def test_failure_is_not_reclassified_as_successful_skip(self):
        self.rows("replay-receipt.jsonl", [{"step": "question", "returncode": 64}])
        summary = self.run_audit()
        row = self.output("propositions.jsonl")[0]
        self.assertEqual(row["verification"]["verification_status"], "failed")
        self.assertEqual(row["verification"]["value_origin"], "V1")
        self.assertEqual(summary["outputs"]["propositions.jsonl"]["counts"], {"failed": 1})

    def test_without_receipt_identical_V2_output_does_not_count_as_replayed(self):
        (self.root / "replay-receipt.jsonl").unlink()
        self.run_audit()
        row = self.output("propositions.jsonl")[0]
        self.assertEqual(row["verification"]["equivalent"], "V1")
        self.assertEqual(row["verification"]["reason"], "no_execution_receipt")

    def test_missing_baseline_and_no_execution_produce_no_invented_result(self):
        (self.root / "v1/propositions.jsonl").unlink()
        self.rows("replay-receipt.jsonl", [{"step": "question", "skipped": True, "reason": "no_input"}])
        self.rehash()
        self.run_audit()
        row = self.output("propositions.jsonl")[0]
        self.assertIsNone(row["data"])
        self.assertEqual(row["verification"]["verification_status"], "unavailable")

    def test_replayed_result_remains_conditional_on_V1_inputs(self):
        self.run_audit()
        row = self.output("propositions.jsonl")[0]
        self.assertEqual(row["verification"]["verification_scope"], "downstream_replay_on_V1_inputs")
        self.assertEqual(row["data"]["verdict"], "Refined")
        self.assertEqual(row["verification"]["verification_status"], "replayed")

    def test_disappeared_id_is_not_silently_filled_after_success(self):
        self.rows("v2/propositions.jsonl", [{"id": "P2", "verdict": "Supported"}])
        self.run_audit()
        old = self.output("propositions.jsonl")[0]
        self.assertEqual(old["id"], "P1")
        self.assertIsNone(old["data"])
        self.assertEqual(old["previous"]["verdict"], "Refined")
        self.assertEqual(old["verification"]["verification_status"], "different")

    def test_success_receipt_without_output_fails_closed(self):
        (self.root / "v2/propositions.jsonl").unlink()
        with self.assertRaisesRegex(ValueError, "without generated output"):
            self.run_audit()

    def test_frozen_input_hash_mismatch_fails_closed(self):
        self.rows("v1/propositions.jsonl", [{"id": "P1", "verdict": "changed"}])
        with self.assertRaisesRegex(ValueError, "hash missing or mismatched"):
            self.run_audit()

    def test_unexpected_mutation_of_inherited_V2_input_fails(self):
        self.rows("v2/season.jsonl", [{**self.original, "early_only_metric": 123}])
        with self.assertRaisesRegex(ValueError, "season input changed"):
            self.run_audit()

    def test_missing_annual_evidence_keeps_old_values_unverified(self):
        (self.root / "annual-recalculated.jsonl").unlink()
        summary = self.run_audit()
        row = self.output("season.jsonl")[0]
        self.assertEqual(row["fields"]["wpct"]["verification_status"], "skipped")
        self.assertEqual(summary["recomputed_annual_units"], 0)
        self.assertNotIn("verified", summary["annual_field_counts"])

    def test_all_annual_computations_skipped_can_retain_V1(self):
        row = {**self.original, "RF": None}
        self.rows("v1/season.jsonl", [row]); self.rows("v2/season.jsonl", [row]); self.rehash()
        self.rows("annual-recalculated.jsonl", [])
        self.js("annual-formula-audit.json", {"recomputed_units": 0, "differences": 0})
        summary = self.run_audit()
        self.assertEqual(summary["recomputed_annual_units"], 0)
        self.assertNotIn("verified", summary["annual_field_counts"])
        self.assertEqual(self.output("season.jsonl")[0]["data"]["early_only_metric"], 1.25)

    def test_missing_report_does_not_claim_executed_verification(self):
        (self.root / "annual-formula-audit.json").unlink()
        self.run_audit()
        self.assertEqual(self.output("season.jsonl")[0]["fields"]["G"]["verification_status"], "skipped")

    def test_invalid_recalculation_evidence_is_not_skip(self):
        self.rows("annual-recalculated.jsonl", [{"season": 2019, "team": "d", "G": 999}])
        with self.assertRaisesRegex(ValueError, "Invalid recalculation"):
            self.run_audit()

    def test_valid_recalculation_mismatch_preserves_both_values(self):
        changed = {**self.original, "wpct": 0.123}
        self.rows("v1/season.jsonl", [changed]); self.rows("v2/season.jsonl", [changed]); self.rehash()
        summary = self.run_audit()
        self.assertEqual(len(summary["formula_mismatches"]), 1)
        row = self.output("season.jsonl")[0]
        self.assertEqual(row["data"]["wpct"], 0.123)
        self.assertEqual(row["fields"]["wpct"]["verification_status"], "different")

    def test_duplicate_id_and_empty_file_are_errors(self):
        for rows in ([], [{"id": "P1"}, {"id": "P1"}]):
            self.rows("v2/propositions.jsonl", rows)
            with self.assertRaises(ValueError):
                self.run_audit()

    def test_nonfinite_json_is_rejected(self):
        (self.root / "v2/propositions.jsonl").write_text('{"id":"P1","value":NaN}\n')
        with self.assertRaisesRegex(ValueError, "Non-finite"):
            self.run_audit()

    def test_all_inputs_unchanged_and_annotated_report_has_banner(self):
        (self.root / "v2/summary.md").write_text("# 以前の研究結果\n", encoding="utf-8")
        paths = [p for p in self.root.rglob("*") if p.is_file()]
        before = {p: mod.sha(p) for p in paths}
        self.run_audit()
        self.assertEqual(before, {p: mod.sha(p) for p in paths})
        text = (self.root / "v2/annotated/summary.md").read_text(encoding="utf-8")
        self.assertIn("検証範囲は部分的", text)
        self.assertIn("# 以前の研究結果", text)
        self.assertEqual(self.output("season.jsonl")[0]["data"]["team_name"], "中日")

    def test_python_S_cli_really_generates_annotation_artifact(self):
        child = subprocess.run([sys.executable, "-S", str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertIn('"verification_coverage": "partial"', child.stdout)
        self.assertTrue((self.root / "v2/annotated/verification-summary.json").is_file())


if __name__ == "__main__":
    unittest.main()
