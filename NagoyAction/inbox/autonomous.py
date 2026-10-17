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
    priority = state_path / "feedback/priority.json"
    if priority.exists():
        preferred = json.loads(priority.read_text()).get("targets", [])
        seeds = [s for s in preferred if s in seeds] + [s for s in seeds if s not in preferred]
    stopped = {json.loads(p.read_text())["job"] for p in (state_path / "requests").glob("*.json")
               if (state_path / "stops" / f"{p.stem}.json").exists()}
    for seed in seeds:
        spec = plan(seed, cycle)
        job = digest({"inputs": inputs, "plan": spec})[:24]
        if job in stopped:
            continue
        path = state_path / "jobs" / job / "state.json"
        if path.exists() and json.loads(path.read_text())["status"] in TERMINAL:
            continue
        return {"job": job, "inputs": inputs, "plan": spec, "origin": "automatic", "seed": seed}
    return None
