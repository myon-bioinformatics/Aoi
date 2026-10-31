"""scripts/shrink_polars.py と shrink/polars_min.py。本物の polars が無いテストは同値比較を飛ばす。"""
import importlib.util
import json
import operator
import random
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shrink_module as sm  # noqa: E402
import shrink_polars as sp  # noqa: E402

ENTRY = ["dragowing/overlap.py:load_overlap", "pythdragoras/propositions.py:_cond"]
SEASON = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"


def _min():
    spec = importlib.util.spec_from_file_location("polars_min_under_test", ROOT / "shrink" / "polars_min.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def test_analyze_does_not_follow_imported_cond():
    used, visited = sm.analyze("polars", ["dragowing/overlap.py:load_overlap"])
    assert "pythdragoras/propositions.py:_cond" not in visited
    assert "col" not in used
    assert {"read_ndjson", "DataFrame"} <= set(used)
    used, visited = sm.analyze("polars", ENTRY)
    assert "pythdragoras/propositions.py:_cond" in visited
    assert {"read_ndjson", "DataFrame", "Expr", "col", "lit"} <= set(used)


def test_generated_file_is_current():
    out = subprocess.run(
        [sys.executable, "scripts/shrink_polars.py", "generate", *ENTRY, "--out", "shrink/polars_min.py", "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr


def test_generate_refuses_unknown_names():
    with pytest.raises(SystemExit, match="concat_str"):
        sp.generate_polars(["concat_str"], ["x.py:f"])


def test_nulls_comparisons_and_kleene_and(tmp_path):
    """c001 が踏む比較と、_cond が複数条件のとき使う &。"""
    mini = _min()
    path = tmp_path / "t.ndjson"
    _write(path, [
        {"n": 1, "f": 1.5, "b": True, "s": "a"},
        {"n": None, "f": None, "b": None, "s": None},
        {"n": 3, "f": 0, "b": False, "s": "巨人"},
    ])
    frame = mini.read_ndjson(path)
    assert frame.height == 3
    assert frame.columns == ["n", "f", "b", "s"]
    assert frame["n"].to_list() == [1, None, 3]
    assert frame["f"].to_list() == [1.5, None, 0.0]
    ops = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
           "==": operator.eq, "!=": operator.ne}
    got = frame.select(x=ops[">"](mini.col("n"), mini.lit(1)))["x"].to_list()
    assert got == [False, None, True]
    assert frame.select(x=ops["=="](mini.col("b"), mini.lit(False)))["x"].to_list() == [False, None, True]
    assert frame.select(x=ops["!="](mini.col("n"), mini.lit(None)))["x"].to_list() == [None, None, None]
    assert frame.select(x=ops["<"](mini.col("s"), mini.lit("b")))["x"].to_list()[0] is True
    both = ops[">"](mini.col("n"), mini.lit(0)) & ops["=="](mini.col("b"), mini.lit(True))
    assert frame.select(x=both)["x"].to_list() == [True, None, False]
    assert frame.select(x=mini.col("b") & mini.lit(False))["x"].to_list() == [False, False, False]
    assert frame.select(x=mini.col("b") & mini.lit(True))["x"].to_list() == [True, None, False]
    assert frame.select(x=mini.lit(True)).height == 1
    with pytest.raises(TypeError):
        frame.select(x=ops["=="](mini.col("s"), mini.lit(1)))
    with pytest.raises(NotImplementedError, match="~"):
        ~mini.col("b")


def test_read_ndjson_upcasts_mixed_numbers_and_rejects_the_rest(tmp_path):
    mini = _min()
    path = tmp_path / "t.ndjson"
    _write(path, [{"a": 1, "z": None}, {"b": "x", "a": 2.5, "z": None}])
    frame = mini.read_ndjson(path)
    assert frame.columns == ["a", "z", "b"]
    assert frame["a"].to_list() == [1.0, 2.5]
    assert frame["z"].to_list() == [None, None]
    assert frame["b"].to_list() == [None, "x"]
    _write(path, [{"a": True}, {"a": 1}])
    with pytest.raises(TypeError):
        mini.read_ndjson(path)
    _write(path, [{"a": {"b": 1}}])
    with pytest.raises(NotImplementedError):
        mini.read_ndjson(path)
    path.write_text("\n\n", encoding="utf-8")
    with pytest.raises(ValueError):
        mini.read_ndjson(path)


def test_min_mode_refuses_when_a_real_package_is_installed():
    if importlib.util.find_spec("numpy") is None and importlib.util.find_spec("polars") is None:
        pytest.skip("numpy も polars も入っていない")
    out = subprocess.run(
        [sys.executable, "shrink/run_overlap_stdlib.py", "--deps", "min", "out.json"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert out.returncode != 0
    assert "入っている" in out.stderr


def test_managed_dragowing_copy_does_not_offer_polars():
    """dist/dragowing_min.py は minpy の stdlib 束ね。load_overlap も polars も入っていない。"""
    text = (ROOT / "dist" / "dragowing_min.py").read_text(encoding="utf-8")
    assert "polars" not in text
    assert "def load_overlap" not in text
    modules = next(line for line in text.splitlines() if line.startswith("# modules:"))
    allow = next(line for line in text.splitlines() if line.startswith("# allow:"))
    assert "overlap" not in modules
    assert allow.strip() == "# allow:"


def test_absent_discovers_only_the_c001_surface():
    pytest.importorskip("numpy")
    out = subprocess.run([sys.executable, "scripts/shrink_polars.py", "absent"], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    for key in (
        "polars.read_ndjson", "DataFrame.height", "DataFrame.columns", "DataFrame.__getitem__",
        "DataFrame.select", "Series.to_list", "polars.col", "polars.lit", "Expr.__gt__", "Expr.__le__", "Expr.__eq__",
    ):
        assert key in out.stdout
    assert "Expr.__and__" not in out.stdout
    assert "succeeded regions=8" in out.stdout
    lines = (ROOT / "dragowing/overlap.py").read_text(encoding="utf-8").splitlines()
    read_line = next(i for i, line in enumerate(lines, 1) if "frame = pl.read_ndjson(path)" in line)
    assert f"dragowing/overlap.py:{read_line}:load_overlap" in out.stdout


def test_trace_names_methods_the_ast_misses():
    pytest.importorskip("polars")
    out = subprocess.run([sys.executable, "scripts/shrink_polars.py", "trace"], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr + out.stdout
    missed = out.stdout.split("missed by ast: ", 1)[1]
    for name in ("DataFrame.height", "DataFrame.columns", "DataFrame.select", "DataFrame.__getitem__", "Series.to_list", "Expr.__eq__"):
        assert name in missed
    assert "regions=8" in out.stdout


def _polars():
    return pytest.importorskip("polars")


def _pair(tmp_path, rows):
    polars = _polars()
    path = tmp_path / "t.ndjson"
    _write(path, rows)
    mini = _min()
    return polars.read_ndjson(path), mini.read_ndjson(path), mini, polars


def _expr(mod, col, op, value):
    return {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
            "==": operator.eq, "!=": operator.ne}[op](mod.col(col), mod.lit(value))


def test_small_frame_matches_polars_including_column_order(tmp_path):
    real, mini, mod, pl = _pair(tmp_path, [{"z": 1, "a": "あ", "m": True}, {"b": 1.5, "z": None, "m": None}])
    assert list(mini.columns) == list(real.columns) == ["z", "a", "m", "b"]
    for name in real.columns:
        assert mini[name].to_list() == real[name].to_list()
    for col, op, value in (("z", ">", 0), ("z", "==", None), ("a", "<", "ん"), ("m", "==", True), ("m", ">", 0), ("b", "<=", 2)):
        assert mini.select(x=_expr(mod, col, op, value))["x"].to_list() == real.select(x=_expr(pl, col, op, value))["x"].to_list()
    both_real = (_expr(pl, "z", ">", 0)) & (_expr(pl, "m", "==", True))
    both_mini = (_expr(mod, "z", ">", 0)) & (_expr(mod, "m", "==", True))
    assert mini.select(x=both_mini)["x"].to_list() == real.select(x=both_real)["x"].to_list()
    assert real.select(x=pl.lit(True)).height == mini.select(x=mod.lit(True)).height == 1


@pytest.mark.parametrize("seed", range(12))
def test_random_frames_match_polars(tmp_path, seed):
    rnd = random.Random(seed)
    rows = []
    for _ in range(rnd.randint(1, 25)):
        row = {"n": None if rnd.random() < 0.3 else rnd.randint(-3, 4)}
        if rnd.random() < 0.7:
            row["f"] = None if rnd.random() < 0.3 else rnd.choice([0.0, 1.0, -1.5, 2.5])
        if rnd.random() < 0.7:
            row["b"] = None if rnd.random() < 0.3 else rnd.choice([True, False])
        if rnd.random() < 0.7:
            row["s"] = None if rnd.random() < 0.3 else rnd.choice(["", "a", "b", "巨人"])
        rows.append(row)
    real, mini, mini_mod, pl = _pair(tmp_path, rows)
    assert set(mini.columns) == set(real.columns)
    for name in real.columns:
        assert mini[name].to_list() == real[name].to_list()
    for name in ("n", "f", "b", "s"):
        if name not in real.columns:
            continue
        for op in ("<", "<=", ">", ">=", "==", "!="):
            for value in (None, 0, 1, 1.5, False, True, "", "a", "巨人"):
                try:
                    expect = real.select(x=_expr(pl, name, op, value))["x"].to_list()
                except Exception:
                    with pytest.raises(Exception):
                        mini.select(x=_expr(mini_mod, name, op, value))
                else:
                    assert mini.select(x=_expr(mini_mod, name, op, value))["x"].to_list() == expect


def test_two_null_literals_are_not_polars(tmp_path):
    """定数 null 同士の & は polars が型エラーにする。load_overlap はここを通らない。"""
    real, mini, mod, pl = _pair(tmp_path, [{"n": 1}, {"n": 2}])
    with pytest.raises(Exception):
        real.select(x=pl.lit(None) & pl.lit(None))
    assert mini.select(x=mod.lit(None) & mod.lit(None))["x"].to_list() == [None]


def test_c001_columns_match_polars_by_name():
    mini = _min().read_ndjson(SEASON)
    real = _polars().read_ndjson(SEASON)
    assert mini.height == real.height == 168
    seen = []
    for line in SEASON.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        for key in json.loads(line):
            if key not in seen:
                seen.append(key)
    assert mini.columns == seen
    assert set(mini.columns) == set(real.columns)
    for name in real.columns:
        assert mini[name].to_list() == real[name].to_list()


def test_load_overlap_bytes_match_with_both_mins(tmp_path):
    pytest.importorskip("numpy")
    reference = tmp_path / "reference.json"
    minimal = tmp_path / "minimal.json"
    real = subprocess.run(
        [sys.executable, "shrink/run_overlap_stdlib.py", "--deps", "real", str(reference)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert real.returncode == 0, real.stderr
    injected = r"""
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(sys.argv[1])
def inject(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
inject("numpy", "shrink/numpy_min.py")
inject("polars", "shrink/polars_min.py")
sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
from dragowing.overlap import default_conditions, load_overlap
from dragowing.records import read_jsonl
season = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
rows = read_jsonl(season)
result = load_overlap(season, default_conditions(read_jsonl(ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"), rows))
Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False, sort_keys=True), encoding="utf-8")
"""
    child = subprocess.run([sys.executable, "-c", injected, str(ROOT), str(minimal)], cwd=ROOT, capture_output=True, text=True)
    assert child.returncode == 0, child.stderr
    assert minimal.read_bytes() == reference.read_bytes()


def test_collect_chain_matches_polars():
    """NagoyAction #13 の collect が踏む explode / filter / join / iter_rows。"""
    pl = _polars()
    mini = _min()

    def rows(mod, links, props):
        prop = mod.DataFrame({
            "proposition_id": [key for key, _ in props],
            "exit_code": [value for _, value in props],
        })
        link = mod.DataFrame(links).explode("proposition_id").filter(mod.col("proposition_id").is_not_null())
        return list(link.join(prop, on="proposition_id", how="left").iter_rows(named=True))

    links = [
        {"id": "R1", "proposition_id": ["P2", "P10", "P999"]},
        {"id": "R2", "proposition_id": []},
        {"id": "R3", "proposition_id": [None, "P2"]},
    ]
    props = [("P10", 4), ("P2", 1)]
    assert rows(mini, links, props) == rows(pl, links, props)
    null_list = [
        {"id": "R1", "proposition_id": ["P1"]},
        {"id": "R2", "proposition_id": None},
    ]
    assert rows(mini, null_list, [("P1", 3)]) == rows(pl, null_list, [("P1", 3)])
    empty = [{"id": "R1", "proposition_id": []}, {"id": "R2", "proposition_id": []}]
    for mod in (mini, pl):
        with pytest.raises(Exception):
            rows(mod, empty, [("P1", 1)])
    with pytest.raises(TypeError):
        mini.DataFrame({"exit_code": [1, True]})


def test_evaluate_stops_before_the_subset_runs_out():
    code = r"""
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("polars", ROOT / "shrink" / "polars_min.py")
module = importlib.util.module_from_spec(spec)
sys.modules["polars"] = module
spec.loader.exec_module(module)
sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
import os
import tempfile
import polars as pl
import propositions
fd, name = tempfile.mkstemp(suffix=".ndjson")
os.close(fd)
path = Path(name)
path.write_text(json.dumps({"p": True, "q": False, "team": "d", "team_name": "中日", "season": 2000}) + "\n", encoding="utf-8")
frame = pl.read_ndjson(path)
definition = {"id": "P1", "statement": "probe", "strength": "always", "min_n": 1,
              "if": [{"col": "p", "op": "==", "value": True}],
              "then": [{"col": "q", "op": "==", "value": True}]}
try:
    propositions.evaluate(definition, frame)
except NotImplementedError as exc:
    path.unlink(missing_ok=True)
    print(exc)
    raise SystemExit(0)
finally:
    if path.exists():
        path.unlink()
raise SystemExit("evaluate returned")
"""
    out = subprocess.run([sys.executable, "-c", code, str(ROOT)], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "polars_min に ~ はない" in out.stdout


def test_load_config_does_not_reread_the_same_file_and_run_workload_does_not_repeat_sys_path(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"entries": ["a.py:f"], "sys_path": ["", ""], "workload": "json:dumps"}), encoding="utf-8")
    try:
        assert sp.load_config(cfg)["entries"] == ["a.py:f"]
        cfg.write_text(json.dumps({"entries": ["b.py:g"]}), encoding="utf-8")
        assert sp.load_config(cfg)["entries"] == ["a.py:f"]          # 同じファイルは読み直さない
        monkeypatch.setattr(sys, "path", [p for p in sys.path if p != str(ROOT)])
        monkeypatch.setattr(sp, "importlib", type("I", (), {"import_module": staticmethod(lambda name: type("M", (), {"dumps": staticmethod(lambda root: {})}))}))
        sp._run_workload()
        sp._run_workload()
        assert sys.path.count(str(ROOT)) == 1
    finally:
        sp.load_config(sp.CONFIG_PATH)
