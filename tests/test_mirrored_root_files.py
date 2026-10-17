"""子の prefix の下の aoi_paths.py などが、Aoi 直下の原本と同じ git blob であること（scripts/mirrored_root_files.py）。

subtree add の前でコピーがまだない子（例: QueRyu の queryu/aoi_paths.py）は skip する。
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mirrored_root_files as mrf  # noqa: E402

HEADS = json.loads((ROOT / "child-heads.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name,copy,original", mrf.mirror_pairs(HEADS), ids=lambda v: str(v))
def test_mirrored_copy_has_the_same_blob_as_the_aoi_original(name, copy, original):
    row = mrf.compare(ROOT, copy, original)
    if row["state"] == "absent":
        pytest.skip(f"{copy} はまだない（{name} を subtree add する前）")
    assert row["state"] == "identical", row


def test_git_blob_matches_git_hash_object():
    out = subprocess.run(["git", "hash-object", str(ROOT / "aoi_paths.py")], capture_output=True, text=True, check=True)
    assert mrf.git_blob(ROOT / "aoi_paths.py") == out.stdout.strip()


def test_pairs_cover_every_child_with_the_default_and_registered_mirrors():
    pairs = mrf.mirror_pairs({"heads": {
        "o/A": {"optional": {"subtree_prefix": "a"}},
        "o/B": {"optional": {"subtree_prefix": "b/", "mirrored_from_parent": {"x/y.py": "y.py"}}},
    }})
    assert pairs == [("o/A", "a/aoi_paths.py", "aoi_paths.py"),
                     ("o/B", "b/aoi_paths.py", "aoi_paths.py"), ("o/B", "b/x/y.py", "y.py")]


def test_states_absent_identical_different_and_original_missing(tmp_path):
    (tmp_path / "aoi_paths.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "child").mkdir()
    assert mrf.compare(tmp_path, "child/aoi_paths.py", "aoi_paths.py")["state"] == "absent"
    (tmp_path / "child" / "aoi_paths.py").write_text("x = 1\n", encoding="utf-8")
    assert mrf.compare(tmp_path, "child/aoi_paths.py", "aoi_paths.py")["state"] == "identical"
    (tmp_path / "child" / "aoi_paths.py").write_text("x = 2\n", encoding="utf-8")
    assert mrf.compare(tmp_path, "child/aoi_paths.py", "aoi_paths.py")["state"] == "different"
    assert mrf.compare(tmp_path, "child/aoi_paths.py", "nope.py")["state"] == "original_missing"


def test_cli_exit_codes(tmp_path):
    (tmp_path / "aoi_paths.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "c").mkdir()
    heads = {"schema": "child-heads/1", "ref": "main", "heads": {"o/C": {"optional": {"subtree_prefix": "c"}}}}
    (tmp_path / "child-heads.json").write_text(json.dumps(heads), encoding="utf-8")
    run = lambda: subprocess.run([sys.executable, "-S", str(ROOT / "scripts" / "mirrored_root_files.py"),
                                  "--root", str(tmp_path)], capture_output=True, text=True)
    assert run().returncode == 0  # コピーがない（subtree add の前）は失敗にしない
    (tmp_path / "c" / "aoi_paths.py").write_text("x = 2\n", encoding="utf-8")
    out = run()
    assert out.returncode == 1 and json.loads(out.stdout)["files"][0]["state"] == "different"
