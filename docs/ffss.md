# FFSS の記録から静止図を生成する

```bash
python -S dragowing.py --ffss tests/ffss_records.jsonl --out build/ffss
```

`ffss.html` と SVG 9枚を生成する。`--no-svg` は HTML だけを生成する。
実行に追加パッケージは不要。HTML の表示は CDN の plotly.js を使い、SVG 生成はネットワークも Chrome も使わない。
単一ファイルとしてコピーした要素カウンターは引き続き使えるが、`--ffss` はリポジトリ一式が必要。

| 図 | FFSS の id / run | 数値と単位 |
|---|---|---|
| F01 / F02 サンキー | E31 / energy:coal, energy:lng | source, target, source_group, target_group, value, unit（燃料100に対する%） |
| F03 損失の滝 | 同上 | target_group=loss の value と送電端の value |
| F04 T–Q | E31 / tq | stream=gas, water の q_mw [MW], t_c [°C]。pinch 行の q_mw, t_c, t_gas_c, dt_k |
| F05 バランス点 | E32 / balance | kind=curve の t_out [°C], max_kw, load_jis_kw, load_iso_kw [kW]。catalog の t_out, max_kw。balance の t_out, iso |
| F06 起動工程 | E31 / startup | plant, start, phase ごとの from_min, to_min, agora_lo_min, agora_hi_min [分], at |
| F07 感度分析 | E31 / sensitivity | assumption, x, unit, metric, use, lo, hi, source_range |
| F08 ヒートマップ | E31 / rate-window | tau_h [h] × rate_k_min [K/min] の metric。採用値マーカーは sensitivity の metal-rate / metal-tau の use=true 行から取得 |
| F09 血流サンキー | E30 / blood | F01 と同じリンク形式、単位 L/min |

各行は JSON オブジェクトで、文字列の `id` と `run` を持つ。FFSS の `slug` と未使用フィールドは保持する。
`records.read_ffss` が既存の `read_jsonl` で読み、`figures.ffss_figures` が図JSONに変換し、`render.write_ffss` が保存する。
入口の `dragowing.py` はこれらを呼び出す。元の `read_jsonl` と既存図の入力形式は変更しない。

図に必要な run がなければその図だけを省略する。存在する run の必須フィールド不足・非有限数値・不完全なヒートマップ格子はエラーにする。
実験の判定は再実行しない。図JSONは元の数値を保持し、表示ラベルだけを丸める。
F08 の色は `zmax=3` で飽和するが、`z` の値は切り捨てない。sensitivity がなければ採用値マーカーを省略する。

## 固定したソース

- FFSS #32: `a4e0c3f1a72746115a39d1c12ead98eef82d4049`
- 親 #308（plotly_min v2）: `3dbb1c6b8a8b069c6955d0b09a5280ab6e92fb32`（main の first-parent にあるマージコミット）
- `vendor/tools/stdlib_min/plotly_min.py` は親の `tools/stdlib_min/plotly_min.py` とバイト一致。
  `vendor.lock.json` に ref=commit、Git blob SHA、SHA-256 を記録する。
- fixture の生成コマンド、抽出する run、823行の SHA-256 は `tests/ffss_records.source.json` に記録する。
  FFSS の `run E30`, `run E31`, `run E32 --jsonl PATH` で出力した1,284行から、対象の8 runを順に抽出した。

## 検証の実行条件

```bash
python scripts/check_vendor_lock.py
AOI_ROOT=/path/to/Aoi FFSS_ROOT=/path/to/FFSS python -m pytest -q tests/test_ffss.py tests/test_dragowing.py
```

pytest の既存設定は Aoi を必要とする。通常の全テストはリポジトリの開発環境で実行する。
本家 Plotly は比較用にだけ追加インストールする。実行時依存と uv.lock は増やさない。

| 検証 | 条件・確認範囲 |
|---|---|
| 図の数値 | fixture のリンク、曲線、pinch、工程の開始と長さ、感度の範囲と採用値、全517格子点を照合 |
| fixture 再生成 | `FFSS_ROOT` 指定時に固定SHA・追跡ファイルの未変更を確認し、実際のCLIを3回実行。未指定時は理由付き skip |
| Python 間の差 | 再生成比較は相対・絶対誤差ともに1e-12。3.11と3.12で差があったのは metric 5値、最大絶対差7.55e-15。記録から図JSONへの転記は完全一致で検証 |
| 本家 Plotly | `plotly` 導入時に全9図の data と明示した layout を `plotly.graph_objects.Figure` と比較。指定していない既定 template だけを比較から除外。未導入時は理由付き skip |
| SVG | Python `-S` で9枚を生成。XML、寸法、同一入力からのバイト再現性を確認 |
| 既存図 | 野球の 4 枚（軌跡・球団×年・重なりの格子・内訳）も `--svg` で plotly_min が描く。Chrome は使わない |

2026-11-16 のローカル検証では Python 3.11.18 / 3.12.14、pytest 9.2.0、Plotly 7.1.0 を使用した。
全テストは各324件成功、11件skip、subtest 27件成功。Aoi は `c992ddb27c04de79d7d8d45d56fa0e597ff3972e`。
FFSS実出力の比較と9図の本家Plotly比較は両Pythonで実行済み。
Chromiumはソケット作成が `Operation not permitted` で起動できなかったため、
`CHROME=/unavailable/chromium` を指定してブラウザ依存テストをskipした。Mermaid CDNとCI専用Plotly bundleの検証もskip。
ブラウザを必要としない既存回帰は成功した。Python 3.13〜3.15はローカル未実行で、既存CIの3.11〜3.15 matrixで確認する。

## 描画の境界

plotly_min v2（親 #308）はサブプロット・積み上げ棒・ヒートマップのマスの文字まで描く。配置、文字幅、サンキーのノード位置は本家 Plotly と同一ではない。
JSON互換性の成功は、SVGの画素・配置の一致やKaleidoとの一致を意味しない。これらの一致は未検証。

親 #307 の汎用比較テストもPlotly 7.1.0で実行したところ、名前付き `colorscale="viridis"` の辞書比較が失敗した。
本家は配色名を色配列へ展開し、plotly_minは名前のまま保持するためである。
FFSSのF08は明示的な色配列を使い、全9図の比較は成功している。固定したvendorのバイトは変更していない。

🖼️ SVG は野球の図も FFSS の図も `figures.figure_svg`（plotly_min）の 1 本の道で描く。PNG は書かない（スクショは browser-test-kit の持ち物）。
既存図全体を plotly_min へ移行するか、未対応図を自動振分けするかは別の判断とし、この変更では固定SHAを #308 等へ進めない。
