"""Replay *unregistered* C001 exploration candidates on pinned V1 annual rows.

No network calls, no registered proposition changes, no source-data validation.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import tomllib
from zipfile import ZipFile

RESEARCH_SHA = "0723d1137fc8448fbabb7bbe5fc14333ddfaabe2"
ARTIFACT_ID = 11611346346
ZIP_SHA256 = "789f1b5ca457727120171032c023ec214319fe6a42c2d90f314a0c66cb97edfa"
SHAS = {
    "v1/season.jsonl": "20466c46628f4657233ef6289c628f076a0c665a2129594f5651d29a0d05d350",
    "definitions/propositions.toml": "20ebf739caa0f2b14c2ae8c3662d178a6694aaa43a3f0ad9a475b84ebcf6acf0",
    "definitions/sets.toml": "c72179713973ebe58d7a78eed4888fe7ff65eaf166ede8e549d61a08cdf813c3",
}
PROPOSITION_IDS = ("P62", "P138", "P189", "P196", "P96", "P147", "P144", "P191")
SET_IDS = ("F96", "OFF_SHORT", "TOP_WIN", "Q3_LOW", "Q3_MID", "Q4_POS")
EXPR_IDS = ("E7", "E22")
CANDIDATES = {
    "OR_A": "P62 | P138 | P196",
    "OR_B": "P62 | P189 | P196",
    "E7_AND_E22": "E7 & E22",
}
KEYS = ("season", "team", "team_name", "league", "rank", "upper_half",
        "inn_size_low_streak", "rf_adv", "course_rank_q3", "rf_state2", "ra_state2",
        "rd", "sim_p_upper", "wins_vs_pythag", "alloc_z_strat", "rf_zone_se",
        "vs_top_wpct", "q_wl_4")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def locked_definitions(props, sets):
    p = {x["id"]: x for x in props["proposition"] if x["id"] in PROPOSITION_IDS}
    s = {x["id"]: x for x in sets["set"] if x["id"] in SET_IDS}
    e = {x["id"]: x for x in sets["expr"] if x["id"] in EXPR_IDS}
    if set(p) != set(PROPOSITION_IDS) or set(s) != set(SET_IDS) or set(e) != set(EXPR_IDS):
        raise ValueError("pinned definitions are incomplete")
    return {"propositions": {k: {field: v[field] for field in ("scope", "if", "if_any", "then") if field in v}
                              for k, v in p.items()},
            "sets": {k: {field: v[field] for field in ("from", "part") if field in v} for k, v in s.items()},
            "expressions": {k: {"expr": v["expr"]} for k, v in e.items()}}


def from_artifact(path):
    if digest(path.read_bytes()) != ZIP_SHA256:
        raise ValueError("artifact ZIP SHA-256 mismatch")
    with ZipFile(path) as z:
        raw = {name: z.read(name) for name in SHAS}
        for name, expected in SHAS.items():
            if digest(raw[name]) != expected:
                raise ValueError(f"pinned input SHA-256 mismatch: {name}")
        manifest = json.loads(z.read("input-manifest.json"))
        if manifest.get("research_sha") != RESEARCH_SHA or manifest.get("raw_source_replayed") is not False:
            raise ValueError("unexpected replay provenance")
        for name, expected in SHAS.items():
            if manifest["inputs"].get(Path(name).name) != expected:
                raise ValueError(f"manifest input mismatch: {name}")
    rows = [json.loads(line) for line in raw["v1/season.jsonl"].splitlines() if line.strip()]
    definitions = locked_definitions(tomllib.loads(raw["definitions/propositions.toml"].decode()),
                                      tomllib.loads(raw["definitions/sets.toml"].decode()))
    return {"schema": "c001-exploration-snapshot/1", "research_sha": RESEARCH_SHA,
            "artifact_id": ARTIFACT_ID, "input_sha256": SHAS,
            "definitions": definitions,
            "rows": [{k: row.get(k) for k in KEYS} for row in rows]}


def read_snapshot(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("schema") != "c001-exploration-snapshot/1" or
            data.get("research_sha") != RESEARCH_SHA or
            data.get("artifact_id") != ARTIFACT_ID or
            data.get("input_sha256") != SHAS):
        raise ValueError("snapshot provenance mismatch")
    if data.get("columns") != list(KEYS) or not isinstance(data.get("rows"), list):
        raise ValueError("unexpected snapshot projection")
    data["rows"] = [dict(zip(KEYS, values, strict=True)) for values in data["rows"]]
    return data


def compact_snapshot(snapshot):
    return {**snapshot, "columns": list(KEYS),
            "rows": [[row[k] for k in KEYS] for row in snapshot["rows"]]}


def tri_and(items):
    items = list(items)
    return False if False in items else None if None in items else True


def tri_or(items):
    items = list(items)
    return True if True in items else None if None in items else False


def predicate(row, condition):
    field, op, expected = condition["col"], condition["op"], condition["value"]
    value = row.get(field)
    if value is None:
        return None
    if op == "==":
        return type(value) is type(expected) and value == expected
    if op == "!=":
        return type(value) is not type(expected) or value != expected
    if isinstance(value, bool) or not isinstance(value, (int, float)) or isinstance(expected, bool) or not isinstance(expected, (int, float)):
        raise ValueError(f"invalid numeric comparison: {field}")
    ops = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
           ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
    if op not in ops:
        raise ValueError(f"unknown operator {op}")
    return ops[op](value, expected)


def conditions(row, values):
    return tri_and(predicate(row, item) for item in values)


def premise(row, spec, part="if"):
    if part == "where":
        return conditions(row, spec.get("scope", {}).get("where", []))
    if part != "if":
        raise ValueError(f"unknown set part: {part}")
    required = conditions(row, spec.get("if", []))
    alternatives = spec.get("if_any", [])
    return tri_and((required, tri_or(conditions(row, branch) for branch in alternatives))) if alternatives else required


def evaluate(expression, resolve):
    """Parse only names, parentheses, &, | and ~. Never evaluate Python code."""
    tree = ast.parse(expression, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Name):
            return resolve(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            value = walk(node.operand)
            return None if value is None else not value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitAnd):
            return tri_and((walk(node.left), walk(node.right)))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return tri_or((walk(node.left), walk(node.right)))
        raise ValueError("unsupported expression AST")
    return walk(tree)


def verdict(row, expression, defs):
    p, sets, exprs = defs["propositions"], defs["sets"], defs["expressions"]
    def resolve(name):
        if name in p:
            return premise(row, p[name])
        if name in sets:
            spec = sets[name]
            return premise(row, p[spec["from"]], spec.get("part", "if"))
        if name in exprs:
            return evaluate(exprs[name]["expr"], resolve)
        raise ValueError(f"unknown definition: {name}")
    return evaluate(expression, resolve)


def calculate(snapshot, include_2020=False):
    rows = snapshot["rows"]
    units = [(row["season"], row["team"]) for row in rows]
    if len(units) != 168 or len(set(units)) != 168 or {y for y, _ in units} != set(range(2012, 2026)):
        raise ValueError("expected 168 unique saved team-years from 2012 to 2025")
    for year in range(2012, 2026):
        subset = [row for row in rows if row["season"] == year]
        if len(subset) != 12 or sorted(x["league"] for x in subset) != ["C"] * 6 + ["P"] * 6:
            raise ValueError(f"incomplete league/year: {year}")
    filtered = [row for row in rows if row["season"] >= 2013 and (include_2020 or row["season"] != 2020)]
    expected_count = 156 if include_2020 else 144
    if len(filtered) != expected_count:
        raise ValueError("cohort cardinality mismatch")
    focus = {x["season"] for x in filtered if x["team"] == "d" and x["upper_half"] is False}
    if focus != (set(range(2013, 2026)) - {2020}):
        raise ValueError("unexpected Chunichi B-class years")
    result = {}
    for name, expression in CANDIDATES.items():
        matches, unknown, counterexamples, focus_covered, focus_paths = [], [], [], [], {}
        for row in filtered:
            if type(row.get("upper_half")) is not bool:
                raise ValueError("undefined outcome")
            matched = verdict(row, expression, snapshot["definitions"])
            unit = f'{row["team"]}-{row["season"]}'
            if matched is None:
                unknown.append(unit)
            elif matched:
                matches.append(row)
                if row["upper_half"]:
                    counterexamples.append({"unit": unit, "rank": row["rank"], "upper_half": True})
                if row["team"] == "d" and row["season"] in focus:
                    focus_covered.append(row["season"])
                    focus_paths[str(row["season"])] = [p for p in ("P62", "P138", "P189", "P196")
                                                      if p in expression and verdict(row, p, snapshot["definitions"])] if name != "E7_AND_E22" else ["E7", "E22"]
        result[name] = {"hold": len(matches) - len(counterexamples), "n": len(matches),
                        "undetermined": len(unknown), "undefined_units": sorted(unknown),
                        "counterexamples": counterexamples,
                        "focus_covered": sorted(focus_covered), "focus_coverage": f"{len(focus_covered)}/{len(focus)}",
                        "focus_paths": focus_paths,
                        "focus_not_covered": sorted(focus - set(focus_covered))}
    return {"cohort": {"years": "2013-2025", "exclude": [] if include_2020 else [2020],
                       "units": expected_count, "outcome": "final rank >= 4 (B); not CS participation"},
            "candidates": result}


def report(snapshot):
    return {"status": "unregistered_posthoc_exploration", "independently_validated": False,
            "causally_explained": False, "source_validation": "not_performed_saved_V1_input",
            "origin": "Aoi issue #9 comment 6079868287; candidates selected after observing outcomes",
            "research_sha": RESEARCH_SHA, "artifact_id": ARTIFACT_ID,
            "artifact_zip_sha256": ZIP_SHA256, "input_sha256": SHAS,
            "definitions": {"candidates": CANDIDATES,
                            "propositions": {k: {f: v for f, v in x.items() if f in ("scope", "if", "if_any", "then")}
                                             for k, x in snapshot["definitions"]["propositions"].items()},
                            "sets": snapshot["definitions"]["sets"],
                            "expressions": snapshot["definitions"]["expressions"]},
            "main": calculate(snapshot), "include_2020": calculate(snapshot, True)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--artifact", type=Path, help="original Actions artifact ZIP; verify its full SHA-256")
    source.add_argument("--snapshot", type=Path, help="tracked projection of pinned V1 input")
    parser.add_argument("--write-snapshot", type=Path, help="create tracked fixture from the pinned ZIP")
    parser.add_argument("--out", type=Path, help="write JSON report instead of printing")
    args = parser.parse_args(argv)
    if args.write_snapshot and not args.artifact:
        parser.error("--write-snapshot requires --artifact")
    snapshot = from_artifact(args.artifact) if args.artifact else read_snapshot(args.snapshot)
    if args.write_snapshot:
        args.write_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.write_snapshot.write_text(json.dumps(compact_snapshot(snapshot), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    output = json.dumps(report(snapshot), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
