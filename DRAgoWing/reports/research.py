"""Render saved research manifests without rerunning the evaluator."""
import json
from pathlib import Path
from dragowing import render_report


def build(state: Path):
    manifest = state / "known/manifest.json"
    bank = json.loads(manifest.read_text()) if manifest.exists() else {}
    rows, discoveries = [], []
    for path in sorted((state / "jobs").glob("*/state.json")):
        s = json.loads(path.read_text())
        for candidate in s.get("found_preview", []):
            discoveries.append([candidate["id"], candidate["expr"], candidate.get("parent") or "登録済みの種",
                                ", ".join(candidate.get("motivated_by", [])), path.parent.name])
        rows.append([path.parent.name, s.get("status"), s.get("cursor", 0),
                     s.get("candidates_count", 0), s.get("found_count", 0), s.get("error", "")])
    spec = {"title": "Aoi 自動探索", "intro": f"既知の回答: {bank.get('questions', 0)}件 / {bank.get('targets', 0)}個の命題・式。",
            "notes": "探索候補は同じデータから見つけた仮説です。独立した確認済みの結論ではありません。入力が変われば別の探索として記録します。",
            "provenance": "aoi-research-state / known, jobs。各候補の式・反例・親候補は jobs 内の結果JSONを参照。",
            "controls": [], "default": "", "frames": {"": {"caption": f"保存済み探索 {len(rows)}件", "panels": [
                {"title": "探索の進捗", "note": "completed: 完了 / bounded: 件数上限 / running: 再開待ち / blocked・error: 詳細を確認",
                 "headers": ["探索ID", "状態", "処理済み", "候補総数", "条件を満たす候補", "エラー"], "rows": rows,
                 "data": [{"type": "bar", "x": [r[0] for r in rows], "y": [r[2] for r in rows], "name": "処理済み"}],
                 "layout": {"yaxis": {"title": {"text": "候補数"}}}}]}}}
    spec["frames"][""]["panels"].append({
        "title": "条件を満たした探索候補（各探索の先頭10件）", "note": "事後的に見つけた候補。全件と4つの形の判定は結果JSONに保存。",
        "headers": ["候補ID", "式", "親候補", "探索のきっかけになった単位", "探索ID"], "rows": discoveries,
        "data": [], "layout": {}})
    observations = state / "feedback/observations.json"
    if observations.exists():
        observed = json.loads(observations.read_text())
        spec["research_observations"] = {**observed, "discoveries": discoveries}
        pairs = observed["pairs"]
        spec["frames"][""]["panels"].append({
            "title": "指標が近く、A・Bが分かれた球団年", "note": observed["measurement"]["method"],
            "headers": ["球団年", "標準化距離", "反例に含まれる命題・式"],
            "rows": [[" / ".join(p["units"]), round(p["distance"], 4),
                      ", ".join(f["target"] for f in p["findings"])] for p in pairs],
            "data": [{"type": "bar", "x": [" / ".join(p["units"]) for p in pairs],
                      "y": [p["distance"] for p in pairs], "name": "距離（小さいほど近い）"}], "layout": {}})
    destination = state / "public/index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_report(spec), encoding="utf-8")
    return destination
