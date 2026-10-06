"""Deterministic automatic seeds; completed work is never submitted again."""
import json
import tomllib
from exploration import digest, plan

TERMINAL = {"completed", "bounded", "blocked", "error"}


def next_request(cycle, inputs, state_path):
    registry = tomllib.loads((cycle / "sets.toml").read_text())
    # Existing expressions first; then combinations of all registered sets.
    # Expansion itself follows counterexamples / uncovered units in Explorer.
    seeds = [e["id"] for e in registry.get("expr", [])] + ["all"]
    for seed in seeds:
        spec = plan(seed, cycle)
        job = digest({"inputs": inputs, "plan": spec})[:24]
        path = state_path / "jobs" / job / "state.json"
        if path.exists() and json.loads(path.read_text())["status"] in TERMINAL:
            continue
        return {"job": job, "inputs": inputs, "plan": spec, "origin": "automatic", "seed": seed}
    return None
