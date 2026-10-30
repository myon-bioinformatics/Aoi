"""vendor.lock.json と scripts の照合。ネットワークには出ない。"""
import hashlib
import importlib.util
import json
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


def test_lock_matches_vendored_bytes():
    assert lock.problems(ROOT) == []
    document = lock.load_lock(ROOT)
    assert document["schema"] == "vendor-lock/1"
    names = [Path(entry["source"]).name for entry in document["files"]]
    assert names == ["fetch_module.py", "numpy_min.py"]
    unused = {"shrink_module.py", "shrink_polars.py", "numpy_linalg_min.py", "polars_min.py"}
    assert unused.isdisjoint(names)
    for entry in document["files"]:
        assert set(entry) == {
            "repository", "ref", "commit", "source", "destination", "blob_sha", "sha256",
        }
        assert entry["repository"] == SOURCE
        assert entry["ref"] == entry["commit"]
        assert len(entry["commit"]) == 40
        vendored = ROOT / entry["destination"]
        data = vendored.read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert lock.git_blob_sha(data) == entry["blob_sha"]
        assert entry["destination"] == "vendor/aoi/" + entry["source"]


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
