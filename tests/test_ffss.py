"""FFSS #32 records, numeric preservation, and SVG through the parent's plotly_min (#308)."""
import hashlib
import json
import math
import os
import subprocess
import importlib.util
import sys
from pathlib import Path

import pytest

from dragowing.dragowing import ffss_figures
from dragowing.dragowing import read_ffss, read_jsonl
from dragowing.dragowing import figure_svg, plotly_min


def load_vendored(name, relpath):
    """Load a vendored file by path under a repo-unique name (cli_args README: Loading a vendored copy)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / relpath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


_cli_args = load_vendored("dragowing_cli_args", "vendor/cli_args/cli_args.py")
run_cli = _cli_args.run_cli

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "ffss_records.source.json"
RECORDS = ROOT / "tests" / "ffss_records.jsonl"


def test_fixture_receipt_and_pinned_renderer():
    receipt = json.loads(SOURCE.read_text())
    rows = read_jsonl(RECORDS)
    assert hashlib.sha256(RECORDS.read_bytes()).hexdigest() == receipt["sha256"]
    assert len(rows) == receipt["rows"]
    assert sorted([list(k) for k in read_ffss(RECORDS)]) == receipt["selected_runs"]
    lock = json.loads((ROOT / "vendor.lock.json").read_text())
    entry = next(e for e in lock["files"] if e["source"] == "tools/stdlib_min/plotly_min.py")
    assert entry["ref"] == "main"  # 🔁 own sources follow main
    data = (ROOT / entry["destination"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == entry["blob_sha"]


def test_every_ffss_numeric_series_matches_records():
    records = read_ffss(RECORDS)
    figs = ffss_figures(records)
    for name, key in (("F01_energy-coal", ("E31", "energy:coal")),
                      ("F02_energy-gtcc", ("E31", "energy:lng")),
                      ("F09_blood-flow", ("E30", "blood"))):
        trace = figs[name]["data"][0]
        rows = records[key]
        names = list(dict.fromkeys(n for r in rows for n in (r["source"], r["target"])))
        assert trace["link"]["value"] == [r["value"] for r in rows]
        assert trace["link"]["source"] == [names.index(r["source"]) for r in rows]
        assert trace["link"]["target"] == [names.index(r["target"]) for r in rows]
    for trace, key in zip(figs["F03_losses"]["data"], ("energy:coal", "energy:lng")):
        rows = records[("E31", key)]
        assert trace["y"] == [100.0, *(-r["value"] for r in rows if r["target_group"] == "loss"),
                              next(r["value"] for r in rows if r["target"] == "送電端")]
    tq = records[("E31", "tq")]
    for trace, stream in zip(figs["F04_pinch-tq"]["data"], ("gas", "water")):
        assert trace["x"] == [r["q_mw"] for r in tq if r["stream"] == stream]
        assert trace["y"] == [r["t_c"] for r in tq if r["stream"] == stream]
    for shape, row in zip(figs["F04_pinch-tq"]["layout"]["shapes"], (r for r in tq if r["stream"] == "pinch")):
        assert (shape["x0"], shape["y0"], shape["y1"]) == (row["q_mw"], row["t_c"], row["t_gas_c"])
    balance = records[("E32", "balance")]
    curve = [r for r in balance if r["kind"] == "curve"]
    for trace, field in zip(figs["F05_balance-point"]["data"], ("max_kw", "load_jis_kw", "load_iso_kw")):
        assert trace["x"] == [r["t_out"] for r in curve]
        assert trace["y"] == [r[field] for r in curve]
    assert figs["F05_balance-point"]["layout"]["shapes"][0]["x0"] == next(
        r["t_out"] for r in balance if r["kind"] == "balance" and not r["iso"])
    for trace, phase in zip(figs["F06_startup"]["data"], ("steps", "warmup", "ramp")):
        rows = [next(r for r in records[("E31", "startup")] if (r["plant"], r["start"], r["phase"]) == (p, s, phase))
                for p in ("lng", "coal") for s in ("cold", "hot")]
        assert trace["base"] == [r["from_min"] for r in rows]
        assert trace["x"] == [r["to_min"] - r["from_min"] for r in rows]
    sensitivity = records[("E31", "sensitivity")]
    spans = [[r for r in sensitivity if r["assumption"] == name] for name in dict.fromkeys(r["assumption"] for r in sensitivity)]
    spans.sort(key=lambda rows: max(r["metric"] for r in rows) - min(r["metric"] for r in rows))
    bar, marker = figs["F07_sensitivity"]["data"]
    assert bar["base"] == [min(r["metric"] for r in rows if not r["use"]) for rows in spans]
    assert bar["x"] == [max(r["metric"] for r in rows if not r["use"]) - a for rows, a in zip(spans, bar["base"])]
    assert marker["x"] == [next(r["metric"] for r in rows if r["use"]) for rows in spans]
    heat = figs["F08_rate-window"]["data"][0]
    grid = {(r["tau_h"], r["rate_k_min"]): r["metric"] for r in records[("E31", "rate-window")]}
    assert heat["z"] == [[grid[(y, x)] for x in heat["x"]] for y in heat["y"]]
    assert max(map(max, heat["z"])) > heat["zmax"]  # Saturate colour only; preserve the measured value.


def test_window_marker_is_recorded_and_grid_must_be_complete():
    records = read_ffss(RECORDS)
    for row in records[("E31", "sensitivity")]:
        if row["use"] and row["assumption"] == "metal-rate":
            row["x"] = 2.3
    assert ffss_figures(records)["F08_rate-window"]["data"][1]["x"] == [2.3]
    del records[("E31", "sensitivity")]
    assert len(ffss_figures(records)["F08_rate-window"]["data"]) == 1
    records[("E31", "rate-window")].pop()
    with pytest.raises(ValueError, match="complete grid"):
        ffss_figures(records)


@pytest.mark.parametrize("row", [[], {"id": "E31"}, {"id": 31, "run": "tq"}])
def test_invalid_envelopes_report_input_contract(tmp_path, row):
    path = tmp_path / "input.jsonl"
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError, match="id and run must be strings"):
        read_ffss(path)


def test_invalid_run_reports_figure_and_nan_is_rejected():
    with pytest.raises(ValueError, match="F04_pinch-tq"):
        ffss_figures({("E31", "tq"): [{"stream": "gas"}]})
    records = read_ffss(RECORDS)
    records[("E31", "tq")][0]["t_c"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        ffss_figures(records)


def test_ffss_entry_uses_only_stdlib(tmp_path):
    result = run_cli(ROOT / "dragowing.py", "--ffss", str(RECORDS), "--out", str(tmp_path), python_options=("-S",))
    assert result.returncode == 0, result.stderr
    assert len(list((tmp_path / "svg").glob("*.svg"))) == 9


@pytest.mark.parametrize("spec", [
    {"data": [{"type": "scatter", "xaxis": "x2"}], "layout": {}},
    {"data": [], "layout": {"xaxis2": {}}},
    {"data": [], "layout": {"barmode": "stack"}},
    {"data": [{"type": "heatmap", "z": [[1.5]], "text": [["1.5"]], "texttemplate": "%{text}"}], "layout": {}},
])
def test_parent308_draws_subplots_stacks_and_cell_text(spec):
    """🖼️ #308 の plotly_min v2 は、野球の図に要る形（2 つ目の軸・積み上げ・マスの文字）も描く。"""
    assert figure_svg(spec).startswith(b"<svg")


def test_ffss_json_with_real_plotly():
    real = pytest.importorskip("plotly.graph_objects", reason="reference only: install plotly to validate JSON")
    pm = plotly_min()
    for spec in ffss_figures(read_ffss(RECORDS)).values():
        # Plotly adds its default template. Compare the explicit layout and
        # complete traces after removing only that unspecified default.
        reference = real.Figure(spec).to_dict()
        reference["layout"].pop("template", None)
        assert reference == pm.Figure(spec).to_dict()


@pytest.mark.skipif(not os.environ.get("FFSS_ROOT"), reason="set FFSS_ROOT to the pinned FFSS #32 checkout")
def test_fixture_matches_ffss_actual_cli_output(tmp_path):
    receipt = json.loads(SOURCE.read_text())
    ffss = Path(os.environ["FFSS_ROOT"]).resolve()
    commit = subprocess.check_output(["git", "-C", str(ffss), "rev-parse", "HEAD"], text=True).strip()
    assert commit == receipt["commit"]
    subprocess.run(["git", "-C", str(ffss), "diff", "--exit-code", "HEAD"], check=True, capture_output=True)
    selected = {tuple(key) for key in receipt["selected_runs"]}
    rows = []
    for experiment in ("E30", "E31", "E32"):
        output = tmp_path / f"{experiment}.jsonl"
        subprocess.run([sys.executable, "-S", str(ffss / "fluidfullspeedsimulation.py"), "run", experiment,
                        "--jsonl", str(output)], check=True, capture_output=True, timeout=120)
        rows.extend(r for r in read_jsonl(output) if (r["id"], r["run"]) in selected)
    expected = read_jsonl(RECORDS)
    assert len(rows) == len(expected)
    for actual, saved in zip(rows, expected):
        assert actual.keys() == saved.keys()
        for field, value in saved.items():
            if isinstance(value, float):
                # CPython 3.11 and 3.12+ can differ in FFSS's float reductions.
                assert math.isclose(actual[field], value, rel_tol=1e-12, abs_tol=1e-12), (field, actual, saved)
            else:
                assert actual[field] == value
