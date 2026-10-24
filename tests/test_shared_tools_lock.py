"""shared-tools.lock.json と scripts/check_shared_tools_lock.py。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_shared_tools_lock as lock  # noqa: E402


def test_lock_matches_shared_tool_bytes():
    assert lock.problems(ROOT) == []
    document = lock.load_lock(ROOT)
    assert document["schema"] == "vendor-lock/1"
    paths = [entry["path"] for entry in document["files"]]
    assert paths == sorted(paths)
    assert paths == [
        "scripts/fetch_module.py",
        "scripts/shrink_module.py",
        "scripts/shrink_polars.py",
        "shrink/numpy_linalg_min.py",
        "shrink/numpy_min.py",
        "shrink/polars_min.py",
        "vendor/py_launch.cjs",
    ]


def test_hash_mismatch_is_reported():
    document = lock.load_lock(ROOT)
    document["files"][0]["sha256"] = "0" * 64
    found = lock.problems(ROOT, document)
    assert any("sha256 が違う" in item for item in found)


def test_warn_exits_zero_when_the_lock_disagrees(capsys):
    document = json.loads((ROOT / "shared-tools.lock.json").read_text(encoding="utf-8"))
    document["files"][0]["sha256"] = "0" * 64
    original = lock.load_lock

    def fake(root):
        return document

    lock.load_lock = fake
    try:
        assert lock.main(["--warn", "--root", str(ROOT)]) == 0
    finally:
        lock.load_lock = original
    assert "sha256 が違う" in capsys.readouterr().err


def test_strict_exits_one_when_the_lock_disagrees(capsys):
    document = json.loads((ROOT / "shared-tools.lock.json").read_text(encoding="utf-8"))
    document["schema"] = "other"
    original = lock.problems

    def fake(root, parsed=None):
        return ["broken"]

    lock.problems = fake
    try:
        assert lock.main(["--root", str(ROOT)]) == 1
    finally:
        lock.problems = original
    assert "broken" in capsys.readouterr().err
    assert document["schema"] == "other"


def test_py_launch_is_shared_from_the_vendored_parent_copy():
    """vendor/py_launch.cjs は vendor.lock.json で親から取り込んだバイトを子へ配る。"""
    shared = {e["path"]: e for e in lock.load_lock(ROOT)["files"]}
    vendored = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))["files"]
    parent = [e for e in vendored if e["destination"] == "vendor/py_launch.cjs"]
    assert len(parent) == 1
    assert parent[0]["repository"] == "myon-bioinformatics/myon-bioinformatics"
    assert shared["vendor/py_launch.cjs"]["sha256"] == parent[0]["sha256"]
    assert "myon-bioinformatics/SakAnalytics" in shared["vendor/py_launch.cjs"]["consumers"]
    assert "myon-bioinformatics/PythDRagoras" in shared["vendor/py_launch.cjs"]["consumers"]


def test_vendor_path_mismatch_is_reported():
    document = lock.load_lock(ROOT)
    for entry in document["files"]:
        if entry["path"] == "vendor/py_launch.cjs":
            entry["sha256"] = "0" * 64
    found = lock.problems(ROOT, document)
    assert any(item.startswith("vendor/py_launch.cjs: sha256 が違う") for item in found)
