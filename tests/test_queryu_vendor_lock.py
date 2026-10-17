"""vendor.lock.json（vendor-lock/1）と、置いてあるファイルのバイト列が一致すること。"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vendor_lock_matches_checked_in_bytes() -> None:
    lock = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))
    assert lock["schema"] == "vendor-lock/1"
    assert lock["files"], "vendor.lock.json に登録がない"
    for entry in lock["files"]:
        assert re.fullmatch(r"[0-9a-f]{40}", entry["ref"]), entry["destination"]
        assert entry["ref"] == entry["commit"], entry["destination"]
        data = (ROOT / entry["destination"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert blob == entry["blob_sha"], entry["destination"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["destination"]


def test_direct_parent_is_aoi() -> None:
    # 直接の親は Aoi（myon-bioinformatics → Aoi と同じ関係）。Aoi 以外から取り込むときは登録を見直す
    lock = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))
    assert {entry["repository"] for entry in lock["files"]} == {"myon-bioinformatics/Aoi"}
