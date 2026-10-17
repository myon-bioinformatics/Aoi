"""子リポジトリの登録（child-heads.json / vendor-consumers.json）の形。オフライン。"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_child_heads as cch  # noqa: E402


def _load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_child_heads_shape_and_prefixes_exist():
    heads = cch.validate_heads(_load("child-heads.json"))
    assert heads["ref"] == "main"
    for name, entry in heads["heads"].items():
        prefix = entry["optional"]["subtree_prefix"]
        assert (ROOT / prefix).is_dir(), (name, prefix)


def test_pythdragoras_registered_with_exact_ids():
    entry = _load("child-heads.json")["heads"]["myon-bioinformatics/PythDRagoras"]
    assert entry["repository_id"] == 1423045231
    assert entry["optional"]["subtree_prefix"] == "pythdragoras"


def test_queryu_registered_with_exact_ids():
    entry = _load("child-heads.json")["heads"]["myon-bioinformatics/QueRyu"]
    assert entry["repository_id"] == 1423051557
    assert entry["optional"]["subtree_prefix"] == "queryu"


def test_vendor_consumers_shape_and_sources_exist_in_aoi():
    registry = cch.validate_consumers(_load("vendor-consumers.json"))
    heads = _load("child-heads.json")["heads"]
    for consumer in registry["consumers"]:
        assert consumer["repository"] in heads, consumer["repository"]
        for entry in consumer["entries"]:
            if entry["repository"] == "myon-bioinformatics/Aoi":
                assert (ROOT / entry["source"]).is_file(), entry["source"]


def test_offline_cli_passes():
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_child_heads.py"), "--offline"],
                         capture_output=True, text=True, check=False)
    assert out.returncode == 0, out.stderr
    report = json.loads(out.stdout)
    assert report["schema"] == "aoi-child-heads-check/1"
    assert [c["repository"] for c in report["children"]] == ["myon-bioinformatics/PythDRagoras", "myon-bioinformatics/QueRyu"]
