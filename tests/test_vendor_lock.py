"""CI の vendor-lock ジョブが動かす check_vendor_lock.py（scripts/）の検査。ネットワークには出ない。"""
import hashlib, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "myon-bioinformatics/Aoi"


def _load():
    matches = sorted(ROOT.glob("*/check_vendor_lock.py"))
    assert len(matches) == 1
    spec = importlib.util.spec_from_file_location("check_vendor_lock_under_test", matches[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lock = _load()


def test_checker_accepts_this_repository():
    """写しと lock の行の照合そのものは tests/test_fleet.py（親の fleet_check.check_lock）。"""
    assert lock.problems(ROOT) == []


def test_parent_row_is_checked_by_bytes_and_not_against_aoi(tmp_path):
    assert lock.problems(ROOT, tmp_path) != []  # 空の Aoi: Aoi の行は「Aoi にファイルがない」
    assert not any("fleet_check.py" in item for item in lock.problems(ROOT, tmp_path))


def _tree(tmp_path: Path, payload: bytes, sha: str | None = None) -> Path:
    root = tmp_path / "repo"
    dest = root / "vendor" / "aoi" / "shrink"
    dest.mkdir(parents=True)
    (dest / "numpy_min.py").write_bytes(payload)
    document = {
        "schema": "vendor-lock/1",
        "files": [
            {
                "path": "shrink/numpy_min.py",
                "sha256": sha if sha is not None else hashlib.sha256(payload).hexdigest(),
                "source": SOURCE,
            }
        ],
    }
    (root / "vendor.lock.json").write_text(json.dumps(document), encoding="utf-8")
    return root


def test_hash_mismatch_is_reported(tmp_path):
    root = _tree(tmp_path, b"vendored", sha="0" * 64)
    found = lock.problems(root)
    assert any("sha256 が違う" in item for item in found)


def test_aoi_mismatch_is_reported(tmp_path):
    payload = b"vendored"
    root = _tree(tmp_path, payload)
    aoi = tmp_path / "aoi" / "shrink"
    aoi.mkdir(parents=True)
    (aoi / "numpy_min.py").write_bytes(b"upstream")
    found = lock.problems(root, tmp_path / "aoi")
    assert any("Aoi の sha256 が違う" in item for item in found)
    (aoi / "numpy_min.py").write_bytes(payload)
    assert lock.problems(root, tmp_path / "aoi") == []


def test_warn_exits_zero_when_the_lock_disagrees(tmp_path, capsys):
    root = _tree(tmp_path, b"vendored", sha="0" * 64)
    assert lock.main(["--warn", "--root", str(root)]) == 0
    assert "sha256 が違う" in capsys.readouterr().err


def test_strict_exits_one_when_the_lock_disagrees(tmp_path, capsys):
    root = _tree(tmp_path, b"vendored", sha="0" * 64)
    assert lock.main(["--root", str(root)]) == 1
    assert "sha256 が違う" in capsys.readouterr().err
