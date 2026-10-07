"""Resumable, bounded exploration using registered sets and PythDRagoras.

No acquisition, arbitrary Python, thresholds, or official proposition edits.
The plan is persisted before evaluation; descendants record motivating units.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "PythDRagoras"), str(ROOT / "PythDRagoras/logic")]


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def save_state(path: Path, state: dict):
    """Keep large searches below GitHub's per-file size limit.

    Only the current shard changes on append; state.json is the commit manifest.
    The git commit makes all shards and their manifest visible together.
    """
    meta = {k: v for k, v in state.items() if k not in ("candidates", "results", "seen")}
    for name in ("candidates", "results"):
        rows = state[name]
        meta[name + "_count"] = len(rows)
        meta[name + "_shards"] = (len(rows) + 99) // 100
        for start in range(0, len(rows), 100):
            shard = path.parent / name / f"{start // 100:06d}.json"
            content = json.dumps(rows[start:start + 100], ensure_ascii=False, allow_nan=False) + "\n"
            if not shard.exists() or shard.read_text(encoding="utf-8") != content:
                shard.parent.mkdir(parents=True, exist_ok=True)
                shard.write_text(content, encoding="utf-8")
    found = [r for r in state["results"] if r.get("passes")]
    meta.update(storage="sharded/1", found_count=len(found), found_preview=found[:10])
    atomic_json(path, meta)


def read_state(path: Path) -> dict:
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("storage") != "sharded/1":
        return state
    for name in ("candidates", "results"):
        state[name] = []
        for i in range(state.pop(name + "_shards")):
            state[name].extend(json.loads((path.parent / name / f"{i:06d}.json").read_text(encoding="utf-8")))
        if len(state[name]) != state.pop(name + "_count"):
            raise ValueError("探索チェックポイントの件数が一致しません")
    state["seen"] = {r["signature"]: r["id"] for r in state["results"] if "signature" in r}
    for key in ("storage", "found_count", "found_preview"):
        state.pop(key)
    return state


def snapshot(root: Path, cycle: Path) -> dict:
    files = [cycle / "analysis.toml", cycle / "propositions.toml", cycle / "sets.toml", cycle / "outputs/season.jsonl",
             root / "PythDRagoras/pythdragoras.py", root / "pythdragoras/sets.py",
             root / "pythdragoras/propositions.py", root / "pythdragoras/exploration.py"]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def plan(text: str, cycle: Path) -> dict:
    registry = tomllib.loads((cycle / "sets.toml").read_text(encoding="utf-8"))
    known = {s["id"] for s in registry["set"]}
    exprs = {e["id"]: e for e in registry["expr"]}
    if text.startswith("{"):
        spec = json.loads(text)
    elif text in exprs:
        spec = {"sets": sorted(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", exprs[text]["expr"]))), "seed": text}
    elif text in ("登録済み集合で中日のBクラスを説明する式を探して", "all"):
        spec = {"sets": sorted(known)}
    else:
        raise ValueError('探索対象を指定してください: /explore E25 または /explore {"sets":["OFF_SHORT","DEF_WORSE"]}。全集合は /explore all')
    if not isinstance(spec, dict) or set(spec) - {"sets", "seed", "max_depth"}:
        raise ValueError("探索の項目は sets / seed / max_depth")
    names = spec.get("sets")
    if not isinstance(names, list) or not names or any(not isinstance(s, str) or s not in known for s in names):
        raise ValueError("sets は登録済み集合名の空でない配列")
    depth = spec.get("max_depth", 3)
    if type(depth) is not int or not 1 <= depth <= 3:
        raise ValueError("max_depth は1〜3")
    seed = spec.get("seed")
    if seed is not None and seed not in exprs:
        raise ValueError("seed は登録済み式の ID")
    if seed and not set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", exprs[seed]["expr"])) <= set(names):
        raise ValueError("seed の集合をすべて sets に含めてください")
    return {"sets": sorted(set(names)), "seed": seed, "max_depth": depth,
            "max_candidates": 50000, "target": "B", "strength": "usually",
            "focus": tomllib.loads((cycle / "analysis.toml").read_text(encoding="utf-8")).get("focus", {}).get("team")}


class Explorer:
    def __init__(self, cycle: Path, spec: dict):
        import polars as pl
        import propositions as pr
        import sets as st
        from pythdragoras import apply_exclusions

        self.pr, self.st, self.spec = pr, st, spec
        props, _ = pr.load(cycle / "propositions.toml")
        self.sets, expressions, _ = st.load_sets(cycle / "sets.toml", props)
        self.expressions = {e["id"]: e for e in expressions}
        cfg = tomllib.loads((cycle / "analysis.toml").read_text(encoding="utf-8"))
        full = pl.read_ndjson(cycle / "outputs/season.jsonl", infer_schema_length=None)
        self.included, exclusions = apply_exclusions(full, cfg.get("exclude", []))
        self.excluded = full.filter(pl.col("season").is_in([int(e["season"]) for e in exclusions]))

    def initial(self, inputs: dict) -> dict:
        seeds = ([self.expressions[self.spec["seed"]]["expr"]] if self.spec["seed"] else
                 [s for name in self.spec["sets"] for s in (name, "~" + name)])
        return {"version": 1, "plan": self.spec, "inputs": inputs, "status": "queued", "cursor": 0,
                "candidates": [{"expr": s, "depth": 1, "parent": None, "motivated_by": []} for s in seeds],
                "seen": {}, "results": [], "bounded": False}

    def step(self, state: dict):
        candidate = state["candidates"][state["cursor"]]
        # Stable candidate IDs are local to this exploratory plan, never P/E IDs.
        cid = "X" + digest({"plan": state["plan"], "expr": candidate["expr"]})[:20]
        try:
            p = self.st.compile_expr({"id": cid, "expr": candidate["expr"], "strength": self.spec["strength"]}, self.sets)
            signature = self.pr.identity(p)["signature"]
            if signature in state["seen"]:
                state["cursor"] += 1
                return
            self.pr.validate(p)
            p["parent"] = candidate["parent"]
            p["motivated_by"] = candidate["motivated_by"]
            p["change"] = "登録済み集合で反例を絞る / 覆えていない単位への経路を追加"
            result = self.pr.evaluate(p, self.included, self.excluded, self.spec["focus"])
            cov = self.st.coverage(p, self.included, self.spec["focus"])
            forms = [{k: f[k] for k in ("form", "n", "hold", "undetermined", "rate", "code", "verdict")} |
                     {"counterexamples": [c["unit"] for c in f["counterexamples"]]} for f in result["forms"]]
            original = next(f for f in forms if f["form"] == "original")
            record = {"id": cid, **candidate, "definition_sha256": self.pr.definition_sha(p), "signature": signature,
                      "forms": forms, "coverage": cov,
                      "held_out": result["held_out"], "judgement": result["judgement"],
                      "passes": original["code"] == 0 and cov["n"] > 0 and cov["n"] == cov["covered"],
                      "exploratory": True, "independently_confirmed": False}
            state["seen"][signature] = cid
            state["results"].append(record)
            # Expand only within the predeclared sets/depth. The reason and all
            # units observed along the lineage travel with the descendant.
            if candidate["depth"] < self.spec["max_depth"] and original["n"]:
                motivated = sorted(set(candidate["motivated_by"] + original["counterexamples"] + cov["missed"]))
                operators = (["&"] if original["counterexamples"] else []) + (["|"] if cov["missed"] else [])
                for name in self.spec["sets"]:
                    for atom in (name, "~" + name):
                        for op in operators:
                            if len(state["candidates"]) >= self.spec["max_candidates"]:
                                state["bounded"] = True
                                break
                            state["candidates"].append({"expr": f"({candidate['expr']}) {op} {atom}",
                                                        "depth": candidate["depth"] + 1, "parent": cid,
                                                        "motivated_by": motivated})
        except (self.st.SetError, self.pr.PropositionError) as e:
            state["results"].append({"id": cid, **candidate, "error": str(e), "exploratory": True})
        state["cursor"] += 1
        state["status"] = ("bounded" if state["bounded"] else "completed") if state["cursor"] == len(state["candidates"]) else "running"

    def advance(self, state: dict, seconds=30, max_steps=100) -> dict:
        deadline = time.monotonic() + seconds
        for _ in range(max_steps):
            if state["cursor"] >= len(state["candidates"]) or time.monotonic() >= deadline:
                break
            self.step(state)
        if state["cursor"] >= len(state["candidates"]):
            state["status"] = "bounded" if state["bounded"] else "completed"
        return state


def summary(state: dict) -> str:
    found = state.get("found_preview", [r for r in state.get("results", []) if r.get("passes")])
    total = state.get("candidates_count", len(state.get("candidates", [])))
    count = state.get("found_count", len(found))
    lines = [f"状態: {state['status']} / 処理 {state['cursor']}/{total} / 条件を満たす候補 {count}件",
             "対象データ内の探索結果です。独立データでの確認・数学的な一般証明ではありません。"]
    for r in found[:10]:
        lines.append(f"- `{r['id']}` `{r['expr']}`: 反例0、焦点の覆い {r['coverage']['covered']}/{r['coverage']['n']}")
    if state["bounded"]:
        lines.append("候補数の上限に達しました。未生成の組み合わせがあり、全探索完了ではありません。")
    if state.get("error"):
        lines.append(state["error"])
    return "\n".join(lines)
