"""V2 public result IDs must be separate from V1/source IDs."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "publish_c001_v2_results.py"
spec = importlib.util.spec_from_file_location("c001_v2_results", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class V2ResultPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        annotated = self.root / "v2" / "annotated"
        annotated.mkdir(parents=True)
        self.rows(annotated / "propositions.jsonl", [
            self.row("P1", "replayed", {"id": "P1", "verdict": "Supported"}),
            self.row("P2", "skipped", {"id": "P2", "verdict": "Refined"}, origin="V1"),
            self.row("P3", "different", None, origin="unavailable"),
        ])
        self.rows(annotated / "sets.jsonl", [
            self.row("E1", "replayed", {"id": "E1", "verdict": "Supported"}),
        ])

    def row(self, ident, status, data, origin="V2"):
        return {
            "id": ident,
            "data": data,
            "verification": {
                "value_origin": origin,
                "verification_status": status,
                "verification_scope": "downstream_replay_on_V1_inputs" if status == "replayed" else "none",
                "source_validation": "skipped",
            },
            "input_verification": "V1 inherited inputs",
        }

    def rows(self, path, values):
        path.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values), encoding="utf-8")

    def result_rows(self):
        return mod.read_rows(self.root / "v2" / "results" / "results.jsonl")

    def test_only_replayed_outputs_get_v2_public_ids(self):
        summary = mod.publish(self.root)
        self.assertEqual(summary["published_results"], 2)
        self.assertEqual(summary["by_kind"], {"proposition": 1, "expression": 1})
        rows = self.result_rows()
        self.assertEqual([r["id"] for r in rows], ["V2-P1", "V2-E1"])
        self.assertEqual([r["source_id"] for r in rows], ["P1", "E1"])
        self.assertNotIn("V2-P2", [r["id"] for r in rows])
        self.assertNotIn("V2-P3", [r["id"] for r in rows])

    def test_source_data_id_is_not_rewritten(self):
        mod.publish(self.root)
        row = self.result_rows()[0]
        self.assertEqual(row["id"], "V2-P1")
        self.assertEqual(row["source_id"], "P1")
        self.assertEqual(row["data"]["id"], "P1")

    def test_scope_stays_explicitly_on_v1_inputs(self):
        mod.publish(self.root)
        for row in self.result_rows():
            self.assertEqual(row["verification"]["verification_status"], "replayed")
            self.assertEqual(row["verification"]["verification_scope"], "downstream_replay_on_V1_inputs")
            self.assertEqual(row["verification"]["source_validation"], "skipped")

    def test_public_id_rejects_unexpected_source_id_shapes(self):
        for prefix, value in (("P", "PX"), ("P", "P1a"), ("E", "OFF_SHORT"), ("E", "")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    mod.public_id(prefix, value)

    def test_duplicate_source_id_is_rejected(self):
        annotated = self.root / "v2" / "annotated"
        self.rows(annotated / "propositions.jsonl", [
            self.row("P1", "replayed", {"id": "P1"}),
            self.row("P1", "replayed", {"id": "P1"}),
        ])
        with self.assertRaisesRegex(ValueError, "duplicate V2 identity"):
            mod.publish(self.root)


if __name__ == "__main__":
    unittest.main()
