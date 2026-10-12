"""Deterministic digest of research R*.md and current proposition judgements.

Read-only, offline, and deliberately NOT a confirmation evaluator. In particular,
a current cumulative exit code must not be described as a 2026 holdout result.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import importlib.util
import json
from pathlib import Path
import re
import sys
import tomllib

import polars as pl


_ROOT = Path(__file__).resolve().parents[1]
_MARKDOWN_PATH = _ROOT / "vendor" / "markdown.py"
_spec = importlib.util.spec_from_file_location("aoi_vendored_markdown", _MARKDOWN_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load pinned Markdown helper: {_MARKDOWN_PATH}")
_md = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _md  # dataclass decorators need the module registered
_spec.loader.exec_module(_md)

RESEARCH_FILE = re.compile(r"^R([1-9]\d*)-[^/]+\.md$")
HEADING = re.compile(r"^R([1-9]\d*):\s*(.+)$")
RECORDED = re.compile(r"^記録:\s*(\d{4}-\d{2}-\d{2})", re.M)
TABLE_ID = re.compile(r"^\|\s*(P[1-9]\d*)\s*\|", re.M)
ID = re.compile(r"(?<![A-Za-z0-9_])([RPECH][1-9]\d*)(?!\d)")
BULLET = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+)(.+)$")
EXIT_INLINE = re.compile(r"(P[1-9]\d*)(?:(?!P[1-9]\d*).){0,100}?\bexit\s+([0-6])\b", re.I)


class DigestError(ValueError):
    """Invalid input evidence (never silently interpreted as a valid judgement)."""


def _order(value: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-Z]+)(\d+)", value)
    return (match.group(1), int(match.group(2))) if match else (value, 0)


def _unique(values: list[str]) -> list[str]:
    return sorted(set(values), key=_order)


def _bullets(section: dict) -> list[str]:
    return [m.group(1).strip() for line in section["content"].splitlines()
            if (m := BULLET.match(line))]


def _table_criteria(section: dict) -> list[dict]:
    """Capture table reading rules verbatim, without interpreting numeric thresholds.

    Only rows with a proposition in the first cell are considered registered
    criteria. No inference is made from ordinary historical-result tables.
    """
    result = []
    for line in section["content"].splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if len(cells) < 2:
            continue
        ids = _unique(re.findall(r"P[1-9]\d*", cells[0]))
        # Header/separator rows, and cells without a reading, are not criteria.
        if not ids or not cells[-1] or re.fullmatch(r"[:\s-]+", cells[-1]):
            continue
        result.append({"proposition_ids": ids, "reading": cells[-1],
                       "section": section["title"]})
    return result


def _review(sections: list[dict]) -> dict:
    explicit = [s for s in sections if s["level"] == 2 and "見直す条件" in s["title"]]
    registered = [s for s in sections if s["level"] == 2
                  and ("先に決める" in s["title"] or "事前登録" in s["title"]
                       or "判定基準" in s["title"])]
    pre_items = [item for s in registered for item in _bullets(s)]
    criteria = [rule for s in registered for rule in _table_criteria(s)]
    if explicit:
        items = [item for s in explicit for item in _bullets(s)]
        return {"status": "explicit" if items else "unparsed",
                "headings": [s["title"] for s in explicit + registered],
                "items": items, "pre_registered_items": pre_items, "criteria": criteria}
    if registered:
        return {"status": "pre_registered" if pre_items or criteria else "unparsed",
                "headings": [s["title"] for s in registered],
                "items": pre_items, "pre_registered_items": [], "criteria": criteria}
    return {"status": "unknown", "headings": [], "items": [],
            "pre_registered_items": [], "criteria": []}


def parse_note(path: Path) -> dict:
    match = RESEARCH_FILE.fullmatch(path.name)
    if match is None:
        raise DigestError(f"Not a numbered research note: {path}")
    raw = path.read_text(encoding="utf-8")
    sections = _md.split_sections(raw)
    top = next((s for s in sections if s["level"] == 1), None)
    header = HEADING.fullmatch(top["title"]) if top else None
    if header is None or header.group(1) != match.group(1):
        raise DigestError(f"{path}: filename and R heading differ")
    recorded = RECORDED.search(raw)
    if not recorded:
        raise DigestError(f"{path}: missing recorded date")
    try:
        date.fromisoformat(recorded.group(1))
    except ValueError as exc:
        raise DigestError(f"{path}: invalid recorded date") from exc

    rid = "R" + match.group(1)
    is_confirmation = "2026年での確かめ" in header.group(2) and "事前登録" in header.group(2)
    table_ids = TABLE_ID.findall(raw)
    review = _review(sections)
    focus = _unique(pid for rule in review["criteria"] for pid in rule["proposition_ids"])
    references = _unique([ident for ident in ID.findall(raw)
                          if ident != rid and ident not in table_ids])
    state_evidence = [line.strip()[:200] for line in raw.splitlines()
                      if re.search(r"計算.*前|結果を見た後|事前登録|取り込む前", line)][:5]
    return {
        "id": rid, "title": header.group(2), "recorded": recorded.group(1),
        "path": "research/" + path.name, "role": "pre_registered_2026_confirmation_plan"
        if is_confirmation else "research_record",
        "proposition_ids": _unique(table_ids),  # all first-column table IDs
        "defines": [] if is_confirmation else _unique(table_ids),
        "confirmation_focus_ids": focus if is_confirmation else [],
        "duplicate_table_ids": _unique([pid for pid, n in Counter(table_ids).items() if n > 1]),
        "references": references, "review": review, "state_evidence": state_evidence,
        "missing_fields": (["no_table_propositions"] if not table_ids else [])
        + (["review_not_identified"] if review["status"] == "unknown" else [])
        + (["review_unparsed"] if review["status"] == "unparsed" else []),
        "chars": len(raw), "structure_chars": len(_md.strip_prose_keep_structure(raw)),
        "judgement_source": "cumulative_propositions_jsonl_not_2026_holdout",
    }


def _catalog(path: Path) -> set[str]:
    with path.open("rb") as stream:
        props = tomllib.load(stream).get("proposition", [])
    ids = [p["id"] for p in props]
    if len(ids) != len(set(ids)):
        raise DigestError("Duplicate proposition IDs in propositions.toml")
    return set(ids)


def _judgements(path: Path) -> dict[str, int]:
    codes: dict[str, int] = {}
    with path.open(encoding="utf-8") as stream:
        for lineno, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                pid = item["id"]
                code = item["judgement"]["code"]
            except (ValueError, KeyError, TypeError) as exc:
                raise DigestError(f"{path}:{lineno}: malformed judgement") from exc
            if not isinstance(pid, str) or not re.fullmatch(r"P[1-9]\d*", pid):
                raise DigestError(f"{path}:{lineno}: invalid proposition ID")
            if pid in codes:
                raise DigestError(f"{path}:{lineno}: duplicate proposition {pid}")
            if type(code) is not int or code not in range(0, 7):
                raise DigestError(f"{path}:{lineno}: invalid judgement code")
            codes[pid] = code
    if not codes:
        raise DigestError(f"{path}: no judgements")
    return codes


def collect(cycle: Path) -> tuple[list[dict], dict[str, int], set[str]]:
    paths = sorted((cycle / "research").glob("R*.md"),
                   key=lambda p: int(RESEARCH_FILE.fullmatch(p.name).group(1))
                   if RESEARCH_FILE.fullmatch(p.name) else -1)
    if not paths:
        raise DigestError(f"{cycle}: no research notes")
    notes = [parse_note(path) for path in paths]
    ids = [row["id"] for row in notes]
    if len(ids) != len(set(ids)):
        raise DigestError(f"Duplicate research IDs: {ids}")
    catalog = _catalog(cycle / "propositions.toml")
    codes = _judgements(cycle / "outputs" / "propositions.jsonl")

    # JSON projection avoids polymorphic fields of propositions.jsonl, which
    # pl.read_ndjson cannot reliably infer as a single column type.
    prop_frame = pl.DataFrame({"proposition_id": list(codes),
                               "exit_code": list(codes.values())})
    link_frame = pl.DataFrame([
        {"id": row["id"], "proposition_id":
         _unique(row["proposition_ids"] + row["confirmation_focus_ids"])}
        for row in notes
    ]).explode("proposition_id").filter(pl.col("proposition_id").is_not_null())
    joined = link_frame.join(prop_frame, on="proposition_id", how="left")
    by_note: dict[str, list[dict]] = {row["id"]: [] for row in notes}
    for link in joined.iter_rows(named=True):
        by_note[link["id"]].append({"id": link["proposition_id"],
                                    "exit_code": link["exit_code"]})
    for row in notes:
        row["current_judgements"] = sorted(by_note[row["id"]], key=lambda v: _order(v["id"]))
        present = set(row["proposition_ids"]) | set(row["confirmation_focus_ids"])
        mentioned_p = set(re.findall(r"P[1-9]\d*", " ".join(row["references"]))) | present
        row["unknown_ids"] = _unique(list(mentioned_p - catalog))
        row["missing_judgements"] = _unique(list(present - codes))
    return notes, codes, catalog


def audit_findings(path: Path, notes: list[dict], codes: dict[str, int],
                   catalog: set[str]) -> dict:
    text = path.read_text(encoding="utf-8")
    found = set(re.findall(r"(?<![A-Za-z0-9_])P[1-9]\d*(?!\d)", text))
    mentioned = {pid for row in notes for pid in row["proposition_ids"] + row["references"]
                 + row["confirmation_focus_ids"] if pid.startswith("P")}
    conflicts = []
    checks = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        matches = EXIT_INLINE.findall(line)
        if len(matches) == 1:
            pid, literal_code = matches[0]
            if pid in codes:
                checks += 1
                if codes[pid] != int(literal_code):
                    conflicts.append({"line": lineno, "id": pid, "written_exit": int(literal_code),
                                      "current_exit": codes[pid]})
    return {
        "unknown_findings_ids": _unique(list(found - catalog)),
        "not_in_research_notes": _unique(list(found - mentioned)),
        "checked_explicit_exit_labels": checks,
        "explicit_exit_mismatches": conflicts,
        "unverified_prose": True,  # no NLP inference from "supported" etc.
    }


def render_markdown(notes: list[dict], audit: dict) -> str:
    lines = [
        "# 研究ダイジェスト（機械生成）", "",
        "研究記録の抽出と現在の総合終了コードの参照。2026年の独立検証結果ではない。",
        "2026年の独立検証は confirmation.md の2026年単位だけを参照すること。", "",
        "| 研究 | 記録日 | 題名 | 表の命題ID | 現行終了コード | 見直し基準 |",
        "|---|---|---|---|---|---|",
    ]
    for row in notes:
        jid = ", ".join(v["id"] + ":" + (str(v["exit_code"])
                          if v["exit_code"] is not None else "unknown")
                          for v in row["current_judgements"]) or "—"
        links = ", ".join(row["proposition_ids"]) or "—"
        title = row["title"].replace("|", r"\|").replace("\n", " ")
        lines.append(f"| {row['id']} | {row['recorded']} | {title} | {links} | {jid} | {row['review']['status']} |")
    lines += ["", "## 診断（省略せず記録）", ""]
    for row in notes:
        failures = row["missing_fields"] + (
            ["duplicate_table_ids:" + ",".join(row["duplicate_table_ids"])]
            if row["duplicate_table_ids"] else []) + (
            ["unknown_ids:" + ",".join(row["unknown_ids"])]
            if row["unknown_ids"] else []) + (
            ["missing_judgements:" + ",".join(row["missing_judgements"])]
            if row["missing_judgements"] else [])
        if failures:
            lines.append("- " + row["id"] + ": " + "; ".join(failures))
    lines += ["", "## 事前登録・見直し条件の証跡", ""]
    for row in notes:
        if row["review"]["status"] not in {"pre_registered", "unparsed"} and not row["review"]["criteria"] and not row["review"]["pre_registered_items"]:
            continue
        lines.append("### " + row["id"] + " (" + row["review"]["status"] + ")")
        for item in row["review"]["items"]:
            lines.append("- " + item)
        for item in row["review"]["pre_registered_items"]:
            lines.append("- [事前登録] " + item)
        for criterion in row["review"]["criteria"]:
            lines.append("- " + ", ".join(criterion["proposition_ids"]) + ": " + criterion["reading"])
        if not row["review"]["items"] and not row["review"]["criteria"]:
            lines.append("- 抽出可能な条件なし（条件が存在しないとは断定しない）")
        lines.append("")
    lines += ["## FINDINGS.md の限定的な照合", "",
              "- 未登録ID: " + (", ".join(audit["unknown_findings_ids"]) or "なし"),
              "- 研究記録に現れないID: " + (", ".join(audit["not_in_research_notes"]) or "なし"),
              "- 明示的な同一行 exit 表記の照合: " + str(audit["checked_explicit_exit_labels"]) + "件",
              "- 終了コード不一致: " + (json.dumps(audit["explicit_exit_mismatches"], ensure_ascii=False)
                                 if audit["explicit_exit_mismatches"] else "なし"),
              "- その他の自然言語による支持・不支持の記述は未判定（数値の自動転記・自動修正はしない）。",
              ""]
    return "\n".join(lines)


def generate(cycle: Path, outdir: Path, *, check: bool = False) -> tuple[list[dict], dict]:
    notes, codes, catalog = collect(cycle)
    audit = audit_findings(cycle / "FINDINGS.md", notes, codes, catalog)
    jsonl = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in notes)
    files = {outdir / "research_digest.jsonl": jsonl,
             outdir / "research_digest.md": render_markdown(notes, audit)}
    for path, content in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise DigestError(f"Stale or absent generated output: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                path.write_text(content, encoding="utf-8")
    return notes, audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline R note digest (not a 2026 confirmation)")
    parser.add_argument("cycle", type=Path)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--check", action="store_true", help="fail on stale output without writing")
    args = parser.parse_args(argv)
    try:
        notes, audit = generate(args.cycle, args.outdir or args.cycle / "outputs",
                                check=args.check)
    except (DigestError, OSError, json.JSONDecodeError) as exc:
        print(f"research digest: {exc}", file=sys.stderr)
        return 1
    print(f"research digest: {len(notes)} notes, "
          f"{sum(len(r['proposition_ids']) for r in notes)} table proposition IDs, "
          f"{len(audit['explicit_exit_mismatches'])} explicit FINDINGS mismatches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
