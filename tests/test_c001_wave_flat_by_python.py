"""一定の線に当てはめる式が Python のバージョンで変わるかの確認（cycles/c001-chunichi/exploratory/wave_flat_by_python.py）。"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLORATORY = ROOT / "cycles" / "c001-chunichi" / "exploratory"
RESULTS = EXPLORATORY / "wave_tie_noise_results"


def _load():
    spec = importlib.util.spec_from_file_location("c001_wave_flat_by_python", EXPLORATORY / "wave_flat_by_python.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


flat = _load()


def results():
    return json.loads((RESULTS / "wave_flat_by_python.json").read_text(encoding="utf-8"))


def test_sum_of_floats_changed_in_python_3_12_which_is_the_cause_named_in_the_readme():
    # 0.1 を 10 回足す: 3.11 は 0.9999999999999999、3.12 以降は 1.0（足し方が補正つきに変わった）
    assert (sum([0.1] * 10) == 1.0) == (sys.version_info >= (3, 12))


def test_flat_forms_covers_the_declared_lines_and_each_value_is_a_decay_and_a_period():
    forms = flat.flat_forms(flat.load_sa())
    assert len(forms) == len(flat.LENGTHS) * len(flat.LEVELS) == 32
    for k, (decay, period) in forms.items():
        assert k.startswith("n=") and decay > 0 and (period is None or period > 0)


def test_the_results_json_has_the_five_interpreters_and_the_same_32_lines():
    r = results()
    assert [v.split(".")[:2] for v in r["runs"]] == [["3", "11"], ["3", "12"], ["3", "13"], ["3", "14"], ["3", "15"]]
    assert r["lengths"] == list(flat.LENGTHS) and r["levels"] == list(flat.LEVELS)
    for forms in r["runs"].values():
        assert len(forms) == 32


def test_the_readme_table_is_the_json_comparison_against_3_12():
    r, md = results(), (RESULTS / "README.md").read_text(encoding="utf-8")
    ref = next(f for v, f in r["runs"].items() if v.startswith("3.12."))
    diffs = {v: sorted(k for k in f if f[k] != ref[k]) for v, f in r["runs"].items()}
    assert {v.split(".")[1]: len(d) for v, d in diffs.items()} == {"11": 6, "12": 0, "13": 0, "14": 0, "15": 0}
    for v, d in diffs.items():
        assert f"| {v} | {len(d)}" in md or f"| {v} | {len(d)} 本" in md
    # 3.11 だけが違う線の名前を、n ごとにまとめた形（n=60 c=5、n=100 c=4・5・6、…）で README が書いている
    by_n = {}
    for k in diffs["3.11.17"]:
        n, c = (part.split("=")[1] for part in k.split())
        by_n.setdefault(int(n), []).append(float(c))
    text = "、".join(f"n={n} c={'・'.join(f'{c:g}' for c in sorted(cs))}" for n, cs in sorted(by_n.items()))
    assert f"6 本（{text}）" in md
    assert "3.12 以降の 4 つは 32 本すべてで同じ式を選び、3.11 だけが 6 本で違いました" in md
