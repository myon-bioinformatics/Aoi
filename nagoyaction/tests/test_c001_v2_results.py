"""Same-attempt evidence and research/publication statuses are separate axes."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "nagoyaction"))
import c001_publication_policy as policy
import publication_gate as gate
import publish_c001_v2_results as publisher
import ghi_execution as adapter


class PublicationTests(unittest.TestCase):
    def setUp(self):
        # Fixture identities must not borrow the CI worker's real identity.
        patcher = mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "false"})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.identity = {"schema": "nagoyaction-execution/1", "mode": "github_actions", "observer": "gh_identity",
                         "repository": "owner/repo", "run_id": 123, "run_attempt": 2, "workflow_id": 42,
                         "head_sha": "a"*40, "harness_sha": "a"*40, "research_sha": "b"*40,
                         "ghi_sha": adapter.GHI_COMMIT, "workflow_path": ".github/workflows/replay.yml"}
        self.write("execution-identity.json", self.identity)
        for name in policy.DEFINITIONS:
            p = self.root / "definitions" / name
            p.parent.mkdir(exist_ok=True); p.write_text("# fixture\n", encoding="utf-8")
        props = [{"id": "P1", "forms": [{"form": "implication", "verdict": "Refuted"}], "meta": {"code_version": "c"*40}},
                 {"id": "P2", "forms": [{"form": "implication", "verdict": "Inconclusive"}], "meta": {"code_version": "c"*40}}]
        for side in ("v1", "v2"):
            pp = copy.deepcopy(props)
            if side == "v2":
                for row in pp:
                    row["meta"]["code_version"] = self.identity["research_sha"]
            self.rows(f"{side}/propositions.jsonl", pp)
            self.rows(f"{side}/sets.jsonl", [{"id": "E1", "forms": [{"form": "implication", "verdict": "Supported"}]}])
            self.rows(f"{side}/season.jsonl", [{"season": 2019, "team": "d", "RF": 500}])
            self.rows(f"{side}/trajectory_sensitivity_units.jsonl", [{"season": 2019, "team": "d", "x": 1}])
        manifest = {"mode": "saved_annual_input_replay", "raw_source_replayed": False,
                    "initialization_status": "complete", "harness_sha": "a"*40, "research_sha": "b"*40,
                    "inputs": {name: gate.digest(self.root / ("v1" if name in policy.FROZEN else "definitions") / name)
                               for name in policy.FROZEN + policy.DEFINITIONS}}
        self.write("input-manifest.json", manifest)
        self.rows("annual-recalculated.jsonl", [{"season": 2019, "team": "d", "rd": 0}])
        self.write("annual-formula-audit.json", {"differences": 0, "items": []})
        self.rows("replay-receipt.jsonl", [{"step": name, "returncode": 0} for name in ("question", "sets", "judge")])
        self.write("c001-replay-diff.json", {"mode": "saved_annual_input_replay", "raw_source_replayed": False,
                    "comparison_status": "complete", "replay_outcome": "success", "differences": 0,
                    "items": [], "annual_formula_differences": 0})
        self.write("v2/annotated/verification-summary.json", {"dataset_version": "V2", "source_validation": "skipped",
                    "harness_sha": "a"*40, "research_sha": "b"*40})
        self.annotations()
        for name in policy.STAGES:
            self.reseal(name)

    def write(self, name, value):
        gate.write_json(self.root / name, value)

    def rows(self, name, values):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(v, ensure_ascii=False, allow_nan=False) + "\n" for v in values), encoding="utf-8")

    def load(self, name):
        return gate.read_json(self.root / name)

    def annotations(self):
        for filename, _, _ in policy.KINDS:
            items = []
            for row in publisher.read_rows(self.root / "v2" / filename):
                items.append({"id": row["id"], "data": row, "verification": {
                    "verification_status": "replayed", "value_origin": "V2", "equivalent": "V2",
                    "verification_scope": "downstream_replay_on_V1_inputs", "source_validation": "skipped"},
                    "source_sha256": gate.digest(self.root / "v2" / filename)})
            self.rows(f"v2/annotated/{filename}", items)

    def reseal(self, stage, code=0):
        # Test-only construction of producer evidence, not a production retry API.
        (self.root / f"stage-evidence/{stage}.json").unlink(missing_ok=True)
        gate.seal(self.root, stage, policy.STAGES[stage], code, env={})

    def result_rows(self):
        return publisher.read_rows(self.root / "v2/results/results.jsonl")

    def assert_no_catalog(self):
        self.assertFalse((self.root / "v2/results/results.jsonl").exists())
        self.assertFalse(self.load("publication-gate.json")["allowed"])

    def mutate_report(self, name, key, value, stage):
        row = self.load(name); row[key] = value; self.write(name, row); self.reseal(stage)

    def test_only_replayed_outputs_get_v2_public_ids(self):
        summary = publisher.publish(self.root)
        self.assertEqual(summary["published_results"], 3)
        self.assertEqual(summary["by_kind"], {"proposition": 2, "expression": 1})
        self.assertEqual([r["id"] for r in self.result_rows()], ["V2-P1", "V2-P2", "V2-E1"])

    def test_source_ids_and_data_are_not_rewritten(self):
        publisher.publish(self.root)
        for row in self.result_rows():
            self.assertEqual(row["id"], "V2-" + row["source_id"])
            self.assertEqual(row["source_id"], row["data"]["id"])

    def test_refuted_and_inconclusive_are_valid_research_results(self):
        publisher.publish(self.root)
        self.assertEqual([r["data"]["forms"][0]["verdict"] for r in self.result_rows()], ["Refuted", "Inconclusive", "Supported"])

    def test_scope_remains_on_v1_inputs(self):
        publisher.publish(self.root)
        for row in self.result_rows():
            self.assertEqual(row["verification"]["source_validation"], "skipped")
            self.assertEqual(row["verification"]["verification_scope"], "downstream_replay_on_V1_inputs")
            self.assertEqual(row["provenance"]["execution"]["run_attempt"], 2)

    def test_public_id_rejects_unexpected_shapes(self):
        for value in ("P", "P1a", "P01", "P١", "P１", "P-1", "V2-P1", "P1\n", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                publisher.public_id("P", value)

    def test_duplicate_source_ids_rejected_even_when_skipped(self):
        path = "v2/annotated/propositions.jsonl"
        rows = publisher.read_rows(self.root / path); rows.append(rows[0]); self.rows(path, rows); self.reseal("annotate")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            publisher.publish(self.root)
        self.assert_no_catalog()

    def test_explicit_skips_and_differences_are_not_promoted(self):
        for status in ("skipped", "different", "unavailable", "failed"):
            rows = publisher.read_rows(self.root / "v2/annotated/propositions.jsonl")
            rows[0]["verification"]["verification_status"] = status
            self.rows("v2/annotated/propositions.jsonl", rows); self.reseal("annotate")
            self.assertEqual(publisher.publish(self.root)["published_results"], 2)

    def test_reported_difference_holds_the_catalog(self):
        self.write("c001-replay-diff.json", {"comparison_status": "complete", "replay_outcome": "success",
                   "differences": 1, "items": [{"id": "P1", "field": "verdict"}], "annual_formula_differences": 0})
        self.reseal("compare", 1)
        self.assertEqual(publisher.publish(self.root)["exit_code"], 1)
        self.assert_no_catalog()

    def test_unreported_full_field_difference_is_detected(self):
        rows = publisher.read_rows(self.root / "v2/propositions.jsonl")
        rows[0]["forms"][0]["verdict"] = "Supported"
        self.rows("v2/propositions.jsonl", rows); self.annotations(); self.reseal("replay"); self.reseal("annotate")
        self.assertEqual(publisher.publish(self.root)["published_results"], 0)
        self.assertEqual(self.load("publication-gate.json")["unresolved_differences"], 1)

    def test_only_execution_revision_drift_is_allowed(self):
        publisher.publish(self.root)
        report = self.load("publication-gate.json")
        self.assertEqual((report["full_field_differences"], report["provenance_differences"], report["unresolved_differences"]), (2, 2, 0))

    def test_wrong_research_revision_in_output_is_not_ignored(self):
        rows = publisher.read_rows(self.root / "v2/propositions.jsonl"); rows[0]["meta"]["code_version"] = "d"*40
        self.rows("v2/propositions.jsonl", rows); self.annotations(); self.reseal("replay"); self.reseal("annotate")
        self.assertEqual(publisher.publish(self.root)["published_results"], 0)

    def test_final_judge_failure_blocks_and_returns_failure(self):
        self.rows("replay-receipt.jsonl", [{"step": "question", "returncode": 0}, {"step": "sets", "returncode": 0}, {"step": "judge", "returncode": 64}])
        self.reseal("replay", 64)
        self.assertEqual(publisher.publish(self.root)["exit_code"], 64)
        self.assert_no_catalog()

    def test_missing_required_judge_is_not_success(self):
        self.rows("replay-receipt.jsonl", [{"step": "question", "returncode": 0}, {"step": "sets", "returncode": 0}]); self.reseal("replay")
        self.assertEqual(publisher.publish(self.root)["published_results"], 0)
        self.assert_no_catalog()

    def test_conflicting_skip_receipt_rejected(self):
        self.rows("replay-receipt.jsonl", [{"step": "judge", "skipped": True, "returncode": 64}]); self.reseal("replay")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            publisher.publish(self.root)

    def test_boolean_zero_does_not_prove_success(self):
        self.rows("replay-receipt.jsonl", [{"step": name, "returncode": False} for name in ("question", "sets", "judge")]); self.reseal("replay")
        self.assertEqual(publisher.publish(self.root)["published_results"], 0)

    def test_incomplete_comparison_is_not_zero_differences(self):
        self.mutate_report("c001-replay-diff.json", "comparison_status", "not_run", "compare")
        self.assertEqual(publisher.publish(self.root)["published_results"], 0)

    def test_difference_count_must_match_items(self):
        self.mutate_report("c001-replay-diff.json", "differences", 1, "compare")
        with self.assertRaisesRegex(ValueError, "difference report"):
            publisher.publish(self.root)

    def test_missing_identity_blocks_and_removes_stale_catalog(self):
        publisher.publish(self.root)
        (self.root / "execution-identity.json").unlink()
        with self.assertRaises(OSError):
            publisher.publish(self.root)
        self.assert_no_catalog()

    def test_denied_retry_removes_previous_catalog(self):
        publisher.publish(self.root)
        self.mutate_report("c001-replay-diff.json", "comparison_status", "not_run", "compare")
        publisher.publish(self.root)
        self.assert_no_catalog()

    def test_saved_gate_report_is_not_a_bypass(self):
        self.write("publication-gate.json", {"allowed": True})
        (self.root / "stage-evidence/replay.json").unlink()
        with self.assertRaises(OSError):
            publisher.publish(self.root)
        self.assert_no_catalog()

    def test_different_attempt_receipt_rejected(self):
        self.mutate_report("stage-evidence/replay.json", "identity_sha256", "d"*64, "compare")
        with self.assertRaisesRegex(ValueError, "stage identity"):
            publisher.publish(self.root)

    def test_current_environment_must_match_repository_run_attempt_and_sha(self):
        env = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "owner/repo", "GITHUB_RUN_ID": "123",
               "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "a"*40}
        self.assertTrue(policy.evaluate(self.root, env=env)[0]["allowed"])
        for key, value in (("GITHUB_REPOSITORY", "other/repo"), ("GITHUB_RUN_ID", "124"), ("GITHUB_RUN_ATTEMPT", "1"), ("GITHUB_SHA", "f"*40)):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "stale execution"):
                policy.evaluate(self.root, env={**env, key: value})

    def test_manually_modified_result_fails_hash_check(self):
        p = self.root / "v2/propositions.jsonl"; p.write_text(p.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            publisher.publish(self.root)

    def test_seal_coverage_cannot_drop_mandatory_file(self):
        value = self.load("stage-evidence/replay.json"); value["files"].pop("replay-receipt.jsonl"); self.write("stage-evidence/replay.json", value)
        with self.assertRaisesRegex(ValueError, "incomplete evidence"):
            publisher.publish(self.root)

    def test_annotated_data_and_origin_must_match_replayed_raw_data(self):
        rows = publisher.read_rows(self.root / "v2/annotated/propositions.jsonl")
        rows[0]["verification"]["value_origin"] = "V1"
        self.rows("v2/annotated/propositions.jsonl", rows); self.reseal("annotate")
        with self.assertRaisesRegex(ValueError, "annotation/raw"):
            publisher.publish(self.root)

    def test_manifest_code_identity_mismatch_is_error(self):
        self.mutate_report("input-manifest.json", "research_sha", "f"*40, "freeze")
        with self.assertRaisesRegex(ValueError, "manifest/identity"):
            publisher.publish(self.root)

    def test_strict_json_rejects_duplicates_and_nonfinite(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                gate.loads(text)

    def test_symlink_and_traversal_are_rejected(self):
        target = self.root / "v2/propositions.jsonl"
        moved = target.with_suffix(".saved"); target.rename(moved); target.symlink_to(moved)
        with self.assertRaisesRegex(ValueError, "symlink"):
            publisher.publish(self.root)
        with self.assertRaises(ValueError):
            gate.safe_path(self.root, "../outside")

    def test_empty_checks_are_never_green(self):
        with self.assertRaises(ValueError):
            gate.decide({}, {})

    def test_original_evidence_bytes_remain_unchanged(self):
        paths = [p for p in self.root.rglob("*") if p.is_file()]
        before = {p: gate.digest(p) for p in paths}
        publisher.publish(self.root)
        self.assertEqual(before, {p: gate.digest(p) for p in paths})

    def test_real_python_S_publisher_exit_on_success_and_failure(self):
        command = [sys.executable, "-S", str(ROOT / "scripts/publish_c001_v2_results.py"), str(self.root)]
        child = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.rows("replay-receipt.jsonl", [{"step": "judge", "returncode": 64}]); self.reseal("replay", 64)
        child = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(child.returncode, 64, child.stderr)
        self.assert_no_catalog()

    def test_real_child_recording_and_nonzero_preservation(self):
        command = [sys.executable, "-S", str(ROOT / "nagoyaction/publication_gate.py"), "record",
                   "--audit", str(self.root), "--stage", "probe", "--evidence", "probe.json", "--", sys.executable, "-S", "-c",
                   f"from pathlib import Path; Path({str(self.root/'probe.json')!r}).write_text('{{}}'); raise SystemExit(7)"]
        child = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(child.returncode, 7, child.stderr)
        self.assertEqual(self.load("stage-evidence/probe.json")["returncode"], 7)
        repeat = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(repeat.returncode, 64)


class GHIAdapterTests(unittest.TestCase):
    def setUp(self):
        self.env = {"GITHUB_REPOSITORY": "owner/repo", "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "a"*40}
        self.api = {"id": 123, "run_attempt": 2, "repository": {"full_name": "owner/repo"},
                    "head_sha": "a"*40, "workflow_id": 42, "path": ".github/workflows/replay.yml"}
        self.g = mock.Mock()
        self.g.repo.side_effect = lambda value: value
        self.g.local_identity.side_effect = [{"sha": "a"*40}, {"sha": "b"*40}]
        self.g.request.return_value = self.api

    def test_uses_GHI_readonly_and_actual_separate_checkouts(self):
        result = adapter.observe(self.g, Path("harness"), Path("research"), self.env)
        self.assertEqual(result["research_sha"], "b"*40)
        self.g.request.assert_called_once_with("GET", "repos/owner/repo/actions/runs/123/attempts/2", transport="auto", timeout=30)
        self.assertEqual(self.g.local_identity.call_args_list, [mock.call(cwd="harness", env={}), mock.call(cwd="research", env={})])

    def test_GHI_wrong_attempt_rejected(self):
        self.api["run_attempt"] = 1
        with self.assertRaisesRegex(ValueError, "observation"):
            adapter.observe(self.g, Path("h"), Path("r"), self.env)

    def test_GHI_permission_error_does_not_fall_back_to_success(self):
        self.g.request.side_effect = RuntimeError("permission_denied")
        with self.assertRaises(RuntimeError):
            adapter.observe(self.g, Path("h"), Path("r"), self.env)

    def test_GHI_PIN_is_checked_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "gh_identity.py").write_text("raise RuntimeError('must not import')")
            with self.assertRaisesRegex(ValueError, "source blob"):
                adapter.load_ghi(directory)


if __name__ == "__main__":
    unittest.main()
