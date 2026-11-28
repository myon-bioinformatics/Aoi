import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from dragowing.dragowing import xyz_figure


REPO = Path(__file__).resolve().parents[1]


def test_csv():
    figure = xyz_figure(
        "a,b,c,name\n1,2,3,alpha\n4,5,6,beta\n",
        ("a", "b", "c"),
        label="name",
    )
    trace = figure["data"][0]
    assert trace["type"] == "scatter3d"
    assert trace["x"] == [1, 4]
    assert trace["y"] == [2, 5]
    assert trace["z"] == [3, 6]
    assert trace["text"] == ["alpha", "beta"]


def test_tsv():
    figure = xyz_figure("x\ty\tz\n1\t2\t3\n", delimiter="\t")
    assert figure["data"][0]["z"] == [3]


@pytest.mark.parametrize("data", ["x,y,z\n", "x,y\n1,2\n", "x,x,y,z\n1,2,3,4\n"])
def test_invalid(data):
    with pytest.raises(ValueError):
        xyz_figure(data)


def run_cli(entry, *args, cwd, stdin=None):
    return subprocess.run(
        [sys.executable, "-I", "-S", *entry, *args],
        cwd=cwd,
        input=stdin,
        capture_output=True,
        encoding="utf-8",
        check=False,
        timeout=20,
    )


def read_figure(result):
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("<!DOCTYPE html>")
    match = re.search(r'<script type="application/json" id="xyz-data">(.*?)</script>', result.stdout)
    assert match is not None
    return json.loads(match[1])


@pytest.mark.parametrize(("suffix", "delimiter", "flags"), [("csv", ",", ()), ("tsv", "\t", ("--tsv",))])
def test_standalone_cli_file(tmp_path, suffix, delimiter, flags):
    table = tmp_path / f"points.{suffix}"
    table.write_text(
        delimiter.join(("name", "east", "up", "north")) + "\n"
        + delimiter.join(("alpha", "1", "3", "2")) + "\n",
        encoding="utf-8",
    )
    result = run_cli(
        [str(REPO / "dragowing.py")],
        "--csv", str(table), "--x", "east", "--y", "north", "--z", "up",
        "--point-label", "name", *flags,
        cwd=tmp_path,
    )
    figure = read_figure(result)
    trace = figure["data"][0]
    assert trace["type"] == "scatter3d"
    assert (trace["x"], trace["y"], trace["z"], trace["text"]) == ([1], [2], [3], ["alpha"])
    assert figure["layout"]["scene"]["aspectmode"] == "data"


@pytest.mark.parametrize(("stdin", "flags"), [("x,y,z\n1,2,3\n", ()), ("x\ty\tz\n1\t2\t3\n", ("--tsv",))])
def test_standalone_cli_stdin(tmp_path, stdin, flags):
    result = run_cli([str(REPO / "dragowing.py")], "--csv", "-", *flags, cwd=tmp_path, stdin=stdin)
    assert read_figure(result)["data"][0]["z"] == [3]


@pytest.mark.parametrize("row", ["NaN,2,3", "1,inf,3", "1,2,-inf", "1,2,1e999"])
def test_cli_rejects_nonfinite_coordinates(tmp_path, row):
    result = run_cli(
        [str(REPO / "dragowing.py")], "--csv", "-", cwd=tmp_path, stdin=f"x,y,z\n{row}\n",
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "expected finite XYZ coordinates" in result.stderr


def test_aoi_subtree_cli(tmp_path, aoi_root):
    # Use Aoi's real launcher with the DRAgoWing files under test.
    for name in ("aoi.py", "aoi_paths.py"):
        shutil.copyfile(aoi_root / name, tmp_path / name)
    subtree = tmp_path / "dragowing"
    subtree.mkdir()
    for name in ("__main__.py", "dragowing.py"):
        shutil.copyfile(REPO / name, subtree / name)

    result = run_cli(
        ["aoi.py", "dragowing/__main__.py"], "--csv", "-",
        cwd=tmp_path, stdin="x,y,z\n4,5,6\n",
    )
    trace = read_figure(result)["data"][0]
    assert (trace["x"], trace["y"], trace["z"]) == ([4], [5], [6])
