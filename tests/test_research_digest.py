"""Regression checks for the Issue #20 deterministic research digest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import research_digest as digest


ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "cycles" / "c001-chunichi"


def _test_cycle(tmp_path: Path, note: str, *, prop_id="P52", code=1) -> Path:
    cycle = tmp_path / "cycle"
    (cycle / "research").mkdir(parents=True)
    (cycle / "outputs").mkdir()
    (cycle / "research" / "R18-example.md").write_text(note, encoding="utf-8")
    (cycle / "propositions.toml").write_text(
        f'[[proposition]]\nid = "{prop_id}"\n', encoding="utf-8"
    )
    (cycle / "outputs" / "propositions.jsonl").write_text(
        json.dumps({"id": prop_id, "judgement": {"code": code}}) + "\n", encoding="utf-8"
    )
    (cycle / "FINDINGS.md").write_text(
        "# Findings\n\nP52: exit 1\n", encoding="utf-8"
    )
    return cycle


R18_SAMPLE = """# R18: 2026年での確かめ（手順の事前登録）

記録: 2026-10-04。計算を始める前に書いた。

## 主に見る命題と、読み方（先に決める）

| 命題 | 内容 | 読み方 |
|---|---|---|
| **P52**（式1） | 条件 | 逆の判例が**2件以上**、判例が**3件以上** |
"""


@pytest.fixture(scope="module")
def real_notes():
    return digest.collect(CYCLE)


def test_real_26_notes_101_table_references_and_catalog_match(real_notes):
    notes, codes, catalog = real_notes
    assert [n["id"] for n in notes] == [f"R{i}" for i in range(1, 27)]
    assert len(notes) == 26
    assert sum(len(n["proposition_ids"]) for n in notes) == 101
    assert len(codes) >= 114
    assert not {p for n in notes for p in n["proposition_ids"]} - catalog
    assert not {p for n in notes for p in n["proposition_ids"]} - codes
    assert all(n["recorded"] and n["title"] for n in notes)


def test_real_r18_preregistered_vs_cumulative(real_notes):
    notes, _, _ = real_notes
    note = next(n for n in notes if n["id"] == "R18")
    assert note["role"] == "pre_registered_2026_confirmation_plan"
    assert note["review"]["status"] == "pre_registered"
    p52 = [c for c in note["review"]["criteria"]
           if "P52" in c["proposition_ids"]]
    assert len(p52) == 1
    assert "2件以上" in p52[0]["reading"]
    assert "3件以上" in p52[0]["reading"]
    assert note["defines"] == []  # R18 monitors older discoveries, does not redefine them
    assert "P52" in note["confirmation_focus_ids"]
    assert note["judgement_source"] == "cumulative_propositions_jsonl_not_2026_holdout"
    assert note["review"]["status"] != "unknown"


def test_real_explicit_and_unknown_statuses_remain_distinct(real_notes):
    notes, _, _ = real_notes
    r2 = next(n for n in notes if n["id"] == "R2")
    assert r2["review"]["status"] == "explicit"
    assert r2["review"]["items"]
    assert "review_not_identified" not in r2["missing_fields"]
    assert all(n["review"]["status"] in
               {"explicit", "pre_registered", "unknown", "unparsed"} for n in notes)


def test_generate_idempotence_and_judgement_refresh(tmp_path):
    cycle = _test_cycle(tmp_path, R18_SAMPLE)
    out = tmp_path / "out"
    notes, audit = digest.generate(cycle, out)
    before = (out / "research_digest.jsonl").read_bytes()
    assert len(notes) == 1
    assert notes[0]["current_judgements"] == [{"id": "P52", "exit_code": 1}]
    assert audit["checked_explicit_exit_labels"] == 1
    digest.generate(cycle, out, check=True)
    (cycle / "outputs" / "propositions.jsonl").write_text(
        json.dumps({"id": "P52", "judgement": {"code": 3}}) + "\n", encoding="utf-8"
    )
    with pytest.raises(digest.DigestError, match="Stale"):
        digest.generate(cycle, out, check=True)
    notes, audit = digest.generate(cycle, out)
    assert before != (out / "research_digest.jsonl").read_bytes()
    assert notes[0]["current_judgements"][0]["exit_code"] == 3
    assert audit["explicit_exit_mismatches"][0]["written_exit"] == 1
    assert audit["explicit_exit_mismatches"][0]["current_exit"] == 3
    digest.generate(cycle, out, check=True)


def test_missing_heading_and_date(tmp_path):
    path = tmp_path / "R18-example.md"
    path.write_text("no heading\n記録: 2026-10-04", encoding="utf-8")
    with pytest.raises(digest.DigestError, match="heading"):
        digest.parse_note(path)
    path.write_text("# R18: title\n\nmissing date\n", encoding="utf-8")
    with pytest.raises(digest.DigestError, match="date"):
        digest.parse_note(path)
    path.write_text("# R19: title\n\n記録: 2026-10-04", encoding="utf-8")
    with pytest.raises(digest.DigestError, match="differ"):
        digest.parse_note(path)


def test_pre_registration_without_extracted_criteria_is_not_absence(tmp_path):
    path = tmp_path / "R18-example.md"
    path.write_text(
        "# R18: 2026年での確かめ（手順の事前登録）\n記録: 2026-10-04\n"
        "## 読み方（先に決める）\n\nまだ表にしない\n", encoding="utf-8"
    )
    row = digest.parse_note(path)
    assert row["review"]["status"] == "unparsed"
    assert "review_unparsed" in row["missing_fields"]
    assert "review_not_identified" not in row["missing_fields"]


def test_unknown_prop_is_reported_and_not_fabricated(tmp_path):
    cycle = _test_cycle(tmp_path, R18_SAMPLE + "\n| P999 | unknown | 判例を記録 |\n")
    notes, _, _ = digest.collect(cycle)
    assert notes[0]["unknown_ids"] == ["P999"]
    assert notes[0]["missing_judgements"] == ["P999"]
    assert {"id": "P999", "exit_code": None} in notes[0]["current_judgements"]



def test_explicit_and_pre_registered_sections_are_both_retained(tmp_path):
    path = tmp_path / "R18-example.md"
    path.write_text(
        "# R18: title\n記録: 2026-10-04\n"
        "## 読み方（先に決める）\n- 先に比較する\n"
        "## 見直す条件（反証）\n- 判例を再点検する\n",
        encoding="utf-8",
    )
    row = digest.parse_note(path)
    assert row["review"]["status"] == "explicit"
    assert row["review"]["items"] == ["判例を再点検する"]
    assert row["review"]["pre_registered_items"] == ["先に比較する"]


def test_duplicate_registry_ids_rejected(tmp_path):
    cycle = _test_cycle(tmp_path, R18_SAMPLE)
    (cycle / "propositions.toml").write_text(
        '[[proposition]]\nid = "P52"\n[[proposition]]\nid = "P52"\n',
        encoding="utf-8",
    )
    with pytest.raises(digest.DigestError, match="Duplicate proposition"):
        digest.collect(cycle)

def test_duplicate_table_rows_remain_visible(tmp_path):
    path = tmp_path / "R18-example.md"
    path.write_text(
        "# R18: title\n記録: 2026-10-04\n"
        "| P52 | one |\n| P52 | two |\n", encoding="utf-8"
    )
    row = digest.parse_note(path)
    assert row["duplicate_table_ids"] == ["P52"]
    assert row["proposition_ids"] == ["P52"]


def test_duplicate_research_ids_fail(tmp_path):
    cycle = _test_cycle(tmp_path, R18_SAMPLE)
    (cycle / "research" / "R18-another.md").write_text(R18_SAMPLE, encoding="utf-8")
    with pytest.raises(digest.DigestError, match="Duplicate research"):
        digest.collect(cycle)


@pytest.mark.parametrize("payload,match", [
    ({"id": "P52", "judgement": {"code": True}}, "invalid judgement"),
    ({"id": "P52", "judgement": {"code": 64}}, "invalid judgement"),
    ({"id": "P52", "judgement": {}}, "malformed"),
])
def test_invalid_proposition_judgements_fail(tmp_path, payload, match):
    cycle = _test_cycle(tmp_path, R18_SAMPLE)
    (cycle / "outputs" / "propositions.jsonl").write_text(
        json.dumps(payload) + "\n", encoding="utf-8"
    )
    with pytest.raises(digest.DigestError, match=match):
        digest.collect(cycle)


def test_duplicate_judgements_fail(tmp_path):
    cycle = _test_cycle(tmp_path, R18_SAMPLE)
    line = json.dumps({"id": "P52", "judgement": {"code": 1}})
    (cycle / "outputs" / "propositions.jsonl").write_text(
        line + "\n" + line + "\n", encoding="utf-8"
    )
    with pytest.raises(digest.DigestError, match="duplicate"):
        digest.collect(cycle)


def test_vendor_pin_matches_bytes_and_license():
    lock = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))
    assert lock["schema"] == "vendor-lock/1"
    assert {entry["destination"] for entry in lock["files"]} == {
        "vendor/markdown.py", "vendor/markdown-LICENSE"
    }
    for entry in lock["files"]:
        raw = (ROOT / entry["destination"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        assert hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["blob_sha"]
        assert entry["commit"] == "aa5bccfcaf11f17473c7f1ff502509dfa1547660"


def test_explicit_findings_conflict_requires_same_line_id_and_code(tmp_path):
    cycle = _test_cycle(tmp_path, R18_SAMPLE)
    findings = cycle / "FINDINGS.md"
    findings.write_text("# F\nP52: exit 3\nP52 is supported in prose\n"
                        "P999 unknown\n", encoding="utf-8")
    notes, codes, catalog = digest.collect(cycle)
    audit = digest.audit_findings(findings, notes, codes, catalog)
    assert audit["explicit_exit_mismatches"] == [
        {"line": 2, "id": "P52", "written_exit": 3, "current_exit": 1}
    ]
    assert audit["unknown_findings_ids"] == ["P999"]
    assert audit["unverified_prose"] is True
