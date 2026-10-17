"""Offline study adapter: preserve explicit NPB competition labels as exclusions."""
import json
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "BlueProbe"), str(ROOT / "BlueProbe/baseball"), str(ROOT / "QueRyu")]
import npb_calendar
from blueprobe import NORMALIZATION, merge, new_report
from queryu import Cache, write_dataset
from selectolax.lexbor import LexborHTMLParser

NON_REGULAR = {"CS ファーストS", "CS ファイナルS", "クライマックスS", "日本シリーズ", "オールスター", "アジアシリーズ"}


def parse(html, url):
    dom = LexborHTMLParser(html)
    excluded = []
    for link in dom.css('a'):
        href = link.attributes.get("href", "")
        if "/games/s" not in href:
            continue
        node = link
        while node.parent and "stvsteam" not in node.parent.attributes.get("class", "").split():
            node = node.parent
        if not node.parent:
            raise ValueError(f"game link outside known calendar structure: {href}")
        prev, label = node.prev, None
        while prev:
            if "tescheaten" in prev.attributes.get("class", "").split():
                label = prev.text().strip()
                break
            prev = prev.prev
        if label is not None:
            if label not in NON_REGULAR:
                raise ValueError(f"unclassified competition label: {label}")
            excluded.append({"href": href, "raw_text": link.text(), "label": label, "source_url": url})
            link.decompose()
    report = npb_calendar.parse(dom.html, url)
    return report, excluded


def main():
    cache = Cache(ROOT / "data/raw/npb_calendar")
    latest = cache.latest()
    total, excluded = new_report(), []
    receipts = []
    for key, url, group in npb_calendar.pages(range(2013, 2026)):
        e = latest[key]
        body = cache.body(e)
        if hashlib.sha256(body.encode()).hexdigest() != e["sha256"]:
            raise ValueError(f"cache hash mismatch: {key}")
        report, exclusions = parse(body, url) if e["status"] == 200 else (new_report(), [])
        merge(total, report)
        excluded += exclusions
        receipts.append({k: e[k] for k in ("key", "url", "status", "sha256", "bytes", "fetched_at", "code_version")})
    out = ROOT / "data/observations/r001/games.jsonl"
    if out.exists():
        previous = [json.loads(line) for line in out.read_text().splitlines()]
        if sorted(previous, key=lambda g: g["key"]) != sorted(total["records"], key=lambda g: g["key"]):
            raise ValueError("observations changed: explicitly archive existing dataset before rebuilding")
    write_dataset(out, total["records"], {"source": "npb_calendar+r001-explicit-competition-labels",
                  "scope": {"years": [2013, 2025]}, "normalization": NORMALIZATION,
                  "dropped": dict(total["counts"]), "unknown": len(total["unknown"]),
                  "competition_exclusions": dict(Counter(e["label"] for e in excluded)),
                  "cache_manifest": str(cache.manifest)})
    (out.parent / "excluded.json").write_text(json.dumps(excluded, ensure_ascii=False, indent=2))
    (out.parent / "unknown.json").write_text(json.dumps(total["unknown"], ensure_ascii=False, indent=2))
    output = Path(__file__).parent / "outputs"
    output.mkdir(exist_ok=True)
    (output / "source_receipts.json").write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n")
    checks = npb_calendar.check(total["records"])
    print("\n".join(checks))
    print("excluded:", dict(Counter(e["label"] for e in excluded)))
    print("unknown:", len(total["unknown"]))
    if total["unknown"] or any("要確認" in c for c in checks):
        raise ValueError("observation gate failed")


if __name__ == "__main__":
    main()
