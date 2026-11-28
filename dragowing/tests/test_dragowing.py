"""dragowing.py（標準ライブラリだけの単一ファイル）: 要素の数え方、リポジトリなしでの実行、uv tool 化。"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dragowing.dragowing import count_elements

ROOT = Path(__file__).resolve().parents[1]


class StandaloneTest(unittest.TestCase):
    def test_file_and_stdin_without_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "dragowing.py"
            shutil.copy2(ROOT / "dragowing.py", script)
            result = subprocess.run([sys.executable, "-I", str(script), "--tag", "p"],
                                    input="<p>one</p><p>two</p><div></div>", text=True,
                                    capture_output=True, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"p": 2})
            missing = subprocess.run([sys.executable, "-I", str(script), "missing.html"],
                                     capture_output=True, text=True, cwd=tmp)
            self.assertEqual(missing.returncode, 1)
            self.assertIn("Cannot read HTML", missing.stderr)

    def test_generated_tool_project_has_single_module(self):
        # 🧰 ルートの pyproject がそのまま uv tool（uv tool install .）。入るのは dragowing.py 1 ファイルだけ（PythDRagoras #54 に倣う）
        import tomllib
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["scripts"], {"dragowing": "dragowing:main"})
        self.assertEqual((data["project"]["dependencies"], data["project"]["requires-python"]), ([], ">=3.11"))
        self.assertEqual(data["tool"]["setuptools"]["py-modules"], ["dragowing"])
        self.assertFalse((ROOT / "vendor/uv_tool_build.py").exists())


def test_count_elements_limits_tags():
    html = "<html><body><div><p>x</p><p>y</p><img></body></html>"
    assert count_elements(html, ("p", "img")) == {"p": 2, "img": 1}
    assert count_elements(html) == {
        "html": 1,
        "body": 1,
        "div": 1,
        "p": 2,
        "img": 1,
    }


# ==== 📊 FFSS の記録 → 静止の図（tests/ffss_records.jsonl は FFSS main a4e0c3f の run E30・E31・E32 --jsonl から図に使う run だけ）

FFSS_RECORDS = ROOT / "tests" / "ffss_records.jsonl"


def test_ffss_figures_lay_down_the_records():
    from dragowing.dragowing import FFSS_FIGURES, ffss_figures, read_ffss
    records = read_ffss(FFSS_RECORDS)
    figs = ffss_figures(records)
    assert list(figs) == [f"F{n:02d}_{name}" for n, (name, _needs) in enumerate(FFSS_FIGURES, 1)]
    for key, total in ((("E31", "energy:coal"), 100.0), (("E31", "energy:lng"), 100.0), (("E30", "blood"), 5.0)):
        rows = records[key]
        sinks = {r["target"] for r in rows} - {r["source"] for r in rows}
        assert abs(sum(r["value"] for r in rows if r["target"] in sinks) - total) < 1e-9  # 記録のまま閉じる
    sankey = figs["F01_energy-coal"]["data"][0]
    assert sankey["node"]["label"][0] == "燃料 100.0" and sankey["link"]["value"] == [r["value"] for r in records[("E31", "energy:coal")]]
    notes = [a["text"] for a in figs["F04_pinch-tq"]["layout"]["annotations"]]
    assert notes == ["低圧 ΔT 14.9 K", "中圧 ΔT 10.0 K", "高圧 ΔT 10.0 K"]
    tornado = figs["F07_sensitivity"]["data"]
    assert all(x <= 1.0 for x in tornado[1]["x"])  # 使った値ではどれも 🔮 のまま（FFSS の検証と同じ）
    assert tornado[0]["y"][-1].startswith("🧱 温め直し")  # いちばん効くのが上
    heat = figs["F08_rate-window"]["data"][0]
    assert (len(heat["z"]), len(heat["z"][0])) == (11, 47)
    only_e31 = {k: v for k, v in records.items() if k[0] == "E31"}
    assert set(ffss_figures(only_e31)) == set(figs) - {"F05_balance-point", "F09_blood-flow"}  # 無い記録の図は描かない


def test_ffss_svg_without_chrome_and_html():
    import xml.etree.ElementTree as ET
    from dragowing.dragowing import main, plotly_min, write_ffss
    pm = plotly_min()
    with tempfile.TemporaryDirectory() as tmp:
        written = write_ffss(FFSS_RECORDS, Path(tmp) / "a")
        again = write_ffss(FFSS_RECORDS, Path(tmp) / "b")
        svgs = [p for p in written if p.suffix == ".svg"]
        assert len(svgs) == 9
        for a, b in zip(svgs, (p for p in again if p.suffix == ".svg")):
            assert a.read_bytes() == b.read_bytes()  # 同じ記録なら同じバイト
            root = ET.fromstring(a.read_text(encoding="utf-8"))
            assert (root.get("width"), root.get("height")) == ("720", "448")
            assert {t.get("font-family") for t in root.iter("{http://www.w3.org/2000/svg}text")} == {pm.FONT}
        page = written[0].read_text(encoding="utf-8")
        assert f"https://cdn.plot.ly/plotly-{pm.PLOTLY_JS}.min.js" in page and page.count("<section>") == 9
        out = Path(tmp) / "cli"
        assert main(["--ffss", str(FFSS_RECORDS), "--out", str(out), "--no-svg"]) == 0
        assert [p.name for p in out.iterdir()] == ["ffss.html"]
        empty = Path(tmp) / "empty.jsonl"
        empty.write_text("", encoding="utf-8")
        with unittest.TestCase().assertRaises(SystemExit) as cm:
            main(["--ffss", str(empty), "--out", str(out)])
        assert cm.exception.code == 1


def test_forms_and_help_with_only_one_python_file(tmp_path):
    script = tmp_path / "dragowing.py"
    shutil.copy2(ROOT / "dragowing.py", script)
    records = tmp_path / "records"
    records.mkdir()
    items = [{"id": "P1", "posthoc": True},
             {"id": "P2", "preregistered": True},
             {"id": "P3", "posthoc": False}]
    (records / "propositions.jsonl").write_text(
        "".join(json.dumps(item) + "\n" for item in items), encoding="utf-8")
    for args, expected in [
        (["--help"], ["--forms", "--help"]),
        ([str(records), "--forms"], ["事後構成", "事前登録", "不明"]),
    ]:
        result = subprocess.run(
            [sys.executable, "-I", "-S", str(script), *args],
            cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert all(label in result.stdout for label in expected)
