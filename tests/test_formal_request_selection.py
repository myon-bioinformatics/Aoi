"""Connect the Lean request-selection model to Aoi's actual file-based selector.

All inputs are synthetic. No worker is activated, no network is used, and Lean
is not required for these ordinary Python regression tests.
"""

import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "aoi_formal_autonomous", ROOT / "research_loop" / "autonomous.py"
)
AUTONOMOUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTONOMOUS)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class RequestSelectionBridge(unittest.TestCase):
    SEEDS = ("E1", "E2", "all")
    FINISHED = ("completed", "bounded", "blocked", "error")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cycle = self.root / "cycle"
        self.cycle.mkdir()
        (self.cycle / "sets.toml").write_text(
            '[[set]]\nid="A"\n[[set]]\nid="B"\n'
            '[[expr]]\nid="E1"\nexpr="A"\n'
            '[[expr]]\nid="E2"\nexpr="B"\n', encoding="utf-8"
        )
        (self.cycle / "analysis.toml").write_text(
            '[focus]\nteam="synthetic"\n', encoding="utf-8"
        )
        self.inputs = {"fixture": "request-selection", "revision": 1}
        # Use the real public plan/digest helpers to address persisted jobs;
        # selection expectations below come from independently supplied ranks.
        self.jobs = {
            seed: AUTONOMOUS.digest({"inputs": self.inputs,
                                    "plan": AUTONOMOUS.plan(seed, self.cycle)})[:24]
            for seed in self.SEEDS
        }

    def persist(self, state, assignments):
        for index, (seed, condition) in enumerate(zip(self.SEEDS, assignments)):
            if condition == "STOP":
                write_json(state / "requests" / f"{index}.json", {"job": self.jobs[seed]})
                write_json(state / "stops" / f"{index}.json", {"fixture": True})
            elif condition is not None:
                write_json(state / "jobs" / self.jobs[seed] / "state.json", {"status": condition})

    def test_all_stop_and_terminal_combinations_respect_order(self):
        # 6^3 states × 2 orders. Terminal states are tested individually rather
        # than obtaining the expected answer from the implementation's set.
        conditions = (None, "STOP", *self.FINISHED)
        for number, assignments in enumerate(itertools.product(conditions, repeat=3)):
            for ordering in (self.SEEDS, tuple(reversed(self.SEEDS))):
                with self.subTest(assignments=assignments, ordering=ordering):
                    state = self.root / f"case-{number}-{ordering[0]}"
                    self.persist(state, assignments)
                    write_json(state / "feedback" / "priority.json", {"targets": ordering})
                    available = {
                        seed for seed, condition in zip(self.SEEDS, assignments) if condition is None
                    }
                    ranked = {seed: rank for rank, seed in enumerate(ordering)}
                    expected = min(available, key=ranked.__getitem__) if available else None
                    actual = AUTONOMOUS.next_request(self.cycle, self.inputs, state)
                    if expected is None:
                        self.assertIsNone(actual)
                    else:
                        self.assertEqual(actual["seed"], expected)
                        self.assertIn(actual["seed"], self.SEEDS)
                        self.assertEqual(actual["job"], self.jobs[expected])
                        self.assertEqual(actual["origin"], "automatic")
                        self.assertEqual(actual["inputs"], self.inputs)

    def test_nonterminal_states_and_unknown_priority_remain_explicit(self):
        # The selector only excludes its four declared terminal values. It is
        # not an arbitrary-status validator; missing/other states are retryable.
        for status in (None, "queued", "running", "cancelled", "unrecognized"):
            with self.subTest(status=status):
                state = self.root / str(status)
                self.persist(state, (status, "completed", "STOP"))
                write_json(state / "feedback" / "priority.json",
                           {"targets": ["UNREGISTERED", "all", "all", "E2"]})
                before = {p.relative_to(state): p.read_bytes() for p in state.rglob("*") if p.is_file()}
                result = AUTONOMOUS.next_request(self.cycle, self.inputs, state)
                self.assertEqual(result["seed"], "E1")
                after = {p.relative_to(state): p.read_bytes() for p in state.rglob("*") if p.is_file()}
                self.assertEqual(after, before, "selection must not write jobs or activate a worker")

    def test_retiring_selected_jobs_exhausts_the_registry(self):
        state = self.root / "retire"
        write_json(state / "feedback" / "priority.json", {"targets": ["E2", "all", "E1"]})
        seen = []
        for retirement in ("completed", "bounded", "STOP"):
            selected = AUTONOMOUS.next_request(self.cycle, self.inputs, state)
            self.assertIsNotNone(selected)
            self.assertNotIn(selected["job"], seen)
            seen.append(selected["job"])
            if retirement == "STOP":
                write_json(state / "requests" / "retired.json", {"job": selected["job"]})
                write_json(state / "stops" / "retired.json", {})
            else:
                write_json(state / "jobs" / selected["job"] / "state.json", {"status": retirement})
        self.assertEqual(set(seen), set(self.jobs.values()))
        self.assertIsNone(AUTONOMOUS.next_request(self.cycle, self.inputs, state))

    def test_later_registered_candidate_does_not_displace_a_selection(self):
        for first_status in (None, "completed", "STOP"):
            with self.subTest(first_status=first_status):
                state = self.root / f"suffix-{first_status}"
                self.persist(state, (first_status, None, None))
                before = AUTONOMOUS.next_request(self.cycle, self.inputs, state)
                registry = self.cycle / "sets.toml"
                original = registry.read_text(encoding="utf-8")
                registry.write_text(original + '[[expr]]\nid="E3"\nexpr="A | B"\n', encoding="utf-8")
                try:
                    after = AUTONOMOUS.next_request(self.cycle, self.inputs, state)
                    self.assertEqual(after, before)
                finally:
                    registry.write_text(original, encoding="utf-8")

    def test_new_input_snapshot_is_a_distinct_request(self):
        state = self.root / "snapshot"
        self.persist(state, ("STOP", "completed", "error"))
        self.assertIsNone(AUTONOMOUS.next_request(self.cycle, self.inputs, state))
        changed = {**self.inputs, "revision": 2}
        result = AUTONOMOUS.next_request(self.cycle, changed, state)
        self.assertEqual(result["seed"], "E1")
        self.assertNotIn(result["job"], self.jobs.values())
        self.assertEqual(result["inputs"], changed)

    def test_malformed_saved_state_does_not_return_a_request(self):
        for number, content in enumerate(("not JSON", "{}")):
            with self.subTest(content=content):
                state = self.root / f"malformed-{number}"
                path = state / "jobs" / self.jobs["E1"] / "state.json"
                path.parent.mkdir(parents=True)
                path.write_text(content, encoding="utf-8")
                with self.assertRaises((json.JSONDecodeError, KeyError)):
                    AUTONOMOUS.next_request(self.cycle, self.inputs, state)
                self.assertEqual(path.read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
