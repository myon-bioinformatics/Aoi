# 前年比（YoY）ローリング検証 — 実行前ロック

**固定日時:** 2026-10-24（Asia/Tokyo）※本ファイル作成時点。計算はこの後に実行する。  
**入力パネル:** `/workspace/aoi-phase2/gohantrust_panel_aoki.csv`  
**役割:** 数値・係数一覧・年次勝敗表 = Grok / 基準判定と解釈 = Claude  
**前段:** 水準ローリングは判断保留。本ロックは結果を見る前に固定する。

---

## 1. 目的変数とベースライン

| 項目 | 定義 |
|---|---|
| **Target** | \(y_t = \log(P_t / P_{t-1})\) |
| **Baseline** | \(\hat y = 0\)（変化ゼロ。水準の前年ナイーブと同義） |
| **年勝** | \(\lvert\hat y_t - y_t\rvert < \lvert y_t\rvert\) |

---

## 2. 訓練最小点数（結果非依存・実行前固定）

- **Min train:** YoY 訓練点 ≥ **5**
- 最初の YoY 年は 2016（2015 ラグが必要）
- 訓練 YoY 年 ⊆ [2016, \(t-1\)]、点数 ≥5 ⇒ **最初のテスト年 t = 2021**
- 水準側の「訓練最小≥5 → t=2019 を落とす」方針と整合（水準の t=2019 は訓練2015–2018の4点）

**テスト年:**
- **含む版:** 2021–2025（n=5）
- **除外版:** 2021–2024（n=4）
- 両建てで集計する

---

## 3. 比較する形（今回固定・5形・試行数=5）

いずれも切片なし OLS（原点通し）。訓練期のみで係数推定。

| id | 式 | 推定 |
|---|---|---|
| `aoff_yoy` | \(\hat y = \hat\gamma \cdot \Delta\log E\) | \(\gamma = \sum y\,\Delta\log E / \sum(\Delta\log E)^2\)；分母≈0なら γ=0 |
| `primary_yoy` | \(\hat y = \hat\alpha\cdot\Delta\log(100-A) + \hat\gamma\cdot\Delta\log E\) | 2回帰子・切片なし lstsq / 正規方程式 |
| `alt200_yoy` | 同上で \(\Delta\log(200-A)\) | 同上 |
| `exp_neg_yoy` | \(\hat y = \hat\alpha\cdot(-\Delta A) + \hat\gamma\cdot\Delta\log E\) | \(\Delta A = A_t-A_{t-1}\)；α が β役 |
| `prop_A_yoy` | \(\hat y = \hat\alpha\cdot\Delta\log A + \hat\gamma\cdot\Delta\log E\) | 同上 |

**今回入れない:** softplus（前年比結果を見てから）。  
**エッジ:** パネルで A≈57–87 のため 100−A・A > 0。`math.log`。ラグ欠落年はスキップ。

---

## 4. 2025の扱い

`rolling_prelock_2026-10-24.md` §4 の価格事実指定をそのまま適用（既に検証済みで exclusion_applies）。  
両建て: 含む版 n=5 / 除外版 n=4。除外版の集計から2025を外す。「モデル誤差が大きいから外す」は禁止。

---

## 5. 判定（集計の数え方・実行前固定・暫定）

| 基準 | 定義 | 含む版 (n=5) | 除外版 (n=4) |
|---|---|---|---|
| **基準1（主）** | OOS 点の**全年**で年勝 | 5/5 | 4/4 |
| **基準2（補助）** | **過半数**で年勝 | **≥3/5** | **≥3/4** |

- MAE 合計は参考のみ。基準2だけで式を採用しない。
- 連続併記: log_err_ratio = log(|e_m|/|e_n|) で e_n = |y|（ゼロベースライン）。中央値ブートストラップ95% CI（B=2000, seed=20261024）。両窓。CIが0を含めば検出できず／判断保留。
- 本ロックを計算後に書き換えない。変更は別メモ。

---

## 6. Grok の成果物（このロックの後に作成）

1. `yoy_rolling_year_wins.csv`
2. `yoy_rolling_coeffs.csv`（α, γ per t, form）
3. `yoy_rolling_summary.json`
4. `yoy_log_err_ratio.csv` + `yoy_log_err_ratio_summary.json`
5. `report_yoy_rolling.md`（数値のみ。検出できず vs 負けた。政治項は通らなかった、とは書かない）
6. `grok_yoy_handoff_2026-10-24.md`

softplus および古い年次の実データ追加は本ラン外。
