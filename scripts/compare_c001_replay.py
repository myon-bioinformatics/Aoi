"""Compare a frozen c001 output snapshot with a clean replay, field by field.

The comparator is intentionally independent from the pipeline.  It never decides
which side is correct; any difference is evidence to investigate.
"""
from __future__ import annotations
import argparse, json, math, shutil
from pathlib import Path

FORM_FIELDS = ("n", "hold", "undetermined", "rate", "verdict", "code")
ROW_FIELDS = ("definition_sha256", "data_sha256", "posthoc", "parent", "change", "held_out")


def read_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def by_id(path: Path):
    return {r["id"]: r for r in read_jsonl(path)}


def cx_units(form):
    return sorted(c["unit"] if isinstance(c, dict) else c for c in form.get("counterexamples", []))


def same(a, b):
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-12)
    return a == b


def compare_rows(kind, old, new):
    diffs = []
    for ident in sorted(set(old) | set(new)):
        if ident not in old or ident not in new:
            diffs.append({"kind": kind, "id": ident, "field": "presence", "v1": ident in old, "v2": ident in new})
            continue
        a, b = old[ident], new[ident]
        for field in ROW_FIELDS:
            if field in a or field in b:
                if not same(a.get(field), b.get(field)):
                    diffs.append({"kind": kind, "id": ident, "field": field, "v1": a.get(field), "v2": b.get(field)})
        af = {f["form"]: f for f in a.get("forms", [])}
        bf = {f["form"]: f for f in b.get("forms", [])}
        for form in sorted(set(af) | set(bf)):
            if form not in af or form not in bf:
                diffs.append({"kind": kind, "id": ident, "form": form, "field": "presence", "v1": form in af, "v2": form in bf})
                continue
            for field in FORM_FIELDS:
                if field in af[form] or field in bf[form]:
                    if not same(af[form].get(field), bf[form].get(field)):
                        diffs.append({"kind": kind, "id": ident, "form": form, "field": field, "v1": af[form].get(field), "v2": bf[form].get(field)})
            ca, cb = cx_units(af[form]), cx_units(bf[form])
            if ca != cb:
                diffs.append({"kind": kind, "id": ident, "form": form, "field": "counterexamples", "v1": ca, "v2": cb})
    return diffs


def compare_dirs(v1: Path, v2: Path):
    diffs = []
    for kind, name in (("proposition", "propositions.jsonl"), ("expression", "sets.jsonl")):
        a, b = v1 / name, v2 / name
        if not a.exists() or not b.exists():
            diffs.append({"kind": kind, "field": "file_presence", "v1": a.exists(), "v2": b.exists(), "file": name})
            continue
        diffs += compare_rows(kind, by_id(a), by_id(b))
    return diffs


def prepare_v2(v1: Path, v2: Path):
    """Seed only non-regenerated evidence needed by downstream steps.

    Never copy the two semantic outputs under comparison.
    """
    if v2.exists():
        shutil.rmtree(v2)
    v2.mkdir(parents=True)
    for name in ("fetched",):
        src = v1 / name
        if src.exists():
            shutil.copytree(src, v2 / name)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("v1", type=Path)
    p.add_argument("v2", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    diffs = compare_dirs(args.v1, args.v2)
    payload = {"differences": len(diffs), "items": diffs}
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if diffs else 0


if __name__ == "__main__":
    raise SystemExit(main())
