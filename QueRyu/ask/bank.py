"""Materialize the finite, unfiltered registered questions without an LLM."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from ask import ASKS, FORMS, Query, answer, load


def fingerprint(results: Path):
    files = [results / n for n in ("sets.jsonl", "propositions.jsonl")]
    files += [Path(__file__).with_name("ask.py"), Path(__file__)]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None for p in files}
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def query_key(query):
    return json.dumps(asdict(query), sort_keys=True, ensure_ascii=False)


def prepare(results: Path, destination: Path):
    version = fingerprint(results)
    manifest = destination / "manifest.json"
    if manifest.exists() and json.loads(manifest.read_text())["fingerprint"] == version:
        return json.loads(manifest.read_text())
    items = load(results)
    folder = destination / version
    folder.mkdir(parents=True, exist_ok=True)
    count = 0
    for target in sorted({it["id"] for it in items}):
        rows = [it for it in items if it["id"] == target]
        answers = {}
        for form in FORMS:
            for ask in ASKS:
                q = Query(target=target, form=form, ask=ask)
                answers[query_key(q)] = answer(q, rows)
        (folder / f"{target}.json").write_text(json.dumps(answers, ensure_ascii=False) + "\n")
        count += len(answers)
    record = {"fingerprint": version, "targets": len({it["id"] for it in items}), "questions": count,
              "scope": "登録済みID × 4つの形 × 4種類。追加条件のある質問は受付時に同じ判定結果から回答。"}
    temp = manifest.with_suffix(".tmp")
    temp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    temp.replace(manifest)
    return record


def lookup(query, results: Path, destination: Path):
    # Validate the current input identity, never serve an older snapshot.
    if not query.target:
        return None
    path = destination / fingerprint(results) / f"{query.target}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text()).get(query_key(query))
