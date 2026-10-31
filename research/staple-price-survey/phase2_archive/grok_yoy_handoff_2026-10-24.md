# Grok → Claude ハンドオフ：前年比（YoY）ローリング（修正版）

**日付:** 2026-10-24（Asia/Tokyo）  
**役割:** 数値 = Grok / 判定・解釈 = Claude  
**ロック:** `yoy_prelock_2026-10-24.md`（計算前固定・タイムスタンプ `yoy_prelock_timestamp.txt` = 2026-10-24 18:30:37 JST）  
**本版:** Claude指摘（文言・縮小・ブートストラップ・過半数・除外表）を反映した handoff。

**パネル:** 本YoYは **2015–2025** で固定。2005–2025 延長は別作業済みだが、**YoYの再走はしていない**。

---

## ロック内容（要約）

- Target \(y_t=\log(P_t/P_{t-1})\)；Baseline \(\hat y=0\)
- Min train ≥5 YoY ⇒ テスト **2021–2025**（含む n=5 / 除外 n=4）
- 5形: aoff_yoy / primary_yoy / alt200_yoy / exp_neg_yoy / prop_A_yoy（softplus なし）
- 基準1: 全年勝；基準2: 本ランでは ≥3/5・≥3/4（＝暗黙の **wins > n/2**）
- 2025除外: 価格事実指定どおり（exclusion_applies=True）
- 連続: log_err_ratio、B=2000 seed=20261024、両窓。採用規則は未ロック

---

## 言語規則（修正・曖昧さ回避）

\(\mathrm{log\_err\_ratio}=\log(|e_m|/|e_n|)\)。**負 ⇒ モデル誤差が小さい ⇒ モデルが良い。**

| 条件 | 読み（これだけ使う） |
|---|---|
| median < 0 かつ CIが0を除外 | **モデルが良い** |
| median > 0 かつ CIが0を除外 | **モデルが悪い** |
| CIが0を含む | **検出できず／判断保留** |

旧ラベル「naiveより良い／悪い」は主語が曖昧なため廃止。水準連続表も同規則に直済み（`report_rolling_continuous.md`）。

---

## 年勝カウント（含む n=5 / 除外 n=4 を両方）

| form | include 2025 | **exclude 2025** | crit1 含む | crit1 除外 | crit2 含む | crit2 除外 |
|---|---|---|---|---|---|---|
| **aoff_yoy** | **5/5** | **4/4** | Y | Y | Y | Y |
| primary_yoy | 3/5 | **3/4** | N | N | Y | Y |
| alt200_yoy | 3/5 | **3/4** | N | N | Y | Y |
| exp_neg_yoy | 3/5 | **3/4** | N | N | Y | Y |
| prop_A_yoy | 3/5 | **3/4** | N | N | Y | Y |

- **aoff:** 含むでも全年勝 → 結果は2025除外に**依存しない**。
- **政治項4形:** 勝ちは主に2022–2024。2025は負け。除外版では負け年が消える。連続CIは両窓とも0を含む → **判断保留**（「通らなかった」とは書かない）。片側符号 p(3/5)=0.5。

---

## 連続指標 CI（両窓）

| form | CI含0 含む | CI含0 除外 | median符号一致 | 読み（両窓） |
|---|---|---|---|---|
| **aoff_yoy** | **N**（med≈−0.097） | **N**（med≈−0.126） | Y | **モデルが良い**（ただし下記ブートストラップ注意） |
| primary_yoy | Y | Y | Y | 検出できず／判断保留 |
| alt200_yoy | Y | Y | Y | 検出できず／判断保留 |
| exp_neg_yoy | Y | Y | Y | 検出できず／判断保留 |
| prop_A_yoy | Y | Y | Y | 検出できず／判断保留 |

### ブートストラップ注意（Claude指摘3）

aoff の含む版は **5点すべて負**。このときブートストラップ中央値CIが0を除外するのは**自動的**で、符号検定以上の情報はほぼ足さない。CIが追加情報になるのは符号が混ざる形（primary 等）。

---

## 過半数規則の穴と一般形（記録）

- 水準 prelock は「7→≥4、6→≥4」と n 固有で、n=5/4 を定義していなかった。
- 本YoYは ≥3/5・≥3/4 を使った＝暗黙の **wins > n/2**。
- 今後のロックは一般形 **wins > n/2**（strict majority）。詳細: `majority_rule_general_2026-10-24.md`。
- 水準側の既存ロック数字・表は変更していない（文書化のみ）。

---

## aoff_yoy：γ̂表・定数ドリフト・順列（Claude指摘2）

詳細表: `aoff_yoy_gamma_table.csv` / `aoff_yoy_permutation.json`  
スクリプト: `_run_aoff_yoy_diagnostics.py`

### γ̂ と \|ŷ\|（要約）

| t | γ̂ | ŷ | \|ŷ\| | y | vs 0 | train mean ΔlogP | drift vs 0 | aoff beats drift |
|---:|---:|---:|---:|---:|---|---:|---|---|
| 2021 | 0.262 | -0.0029 | 0.0029 | -0.031 | Y | 0.033 | N | Y |
| 2022 | 0.316 | -0.0071 | 0.0071 | -0.049 | Y | 0.022 | N | Y |
| 2023 | 0.468 | 0.0207 | 0.0207 | 0.036 | Y | 0.012 | Y | Y |
| 2024 | 0.552 | 0.0098 | 0.0098 | 0.261 | Y | 0.015 | Y | N |
| 2025 | 1.081 | 0.0114 | 0.0114 | 0.538 | Y | 0.042 | Y | N |

- γ̂ は **≈0 ではない**（0.26–1.08）。
- それでも \|ŷ\|≪\|y\|（弱い同符号縮小でゼロに勝ちやすい見た目）。
- 定数ドリフトのゼロ勝: 3/5・2/4（aoff の 5/5・4/4 より弱い）。aoff がドリフトより \|e\| で勝つのは 3/5・3/4。

### 順列検定（B=2000, seed=20261024）

ΔlogE を 2016–2025 でシャッフルし、同じローリングを繰り返す。

| | include ≥5/5 | exclude ≥4/4 |
|---|---|---|
| シャッフル達成割合 = 片側 p | **0.0065** | **0.021** |
| 観測パーセンタイル | 99.35 | 97.9 |
| null 中央値 | 2/5 | 2/4 |

**解釈（数値）:** 純粋な γ̂=0 縮小ではない。順列上 5/5 は稀 → ΔlogE 系列にいくらか情報がある材料。一方 \|ŷ\| は小さく縮小懸念は残る。  
**次（未実施）:** 遅れ \(\Delta\log E_{t-1}\) を同じ検定で比較。softplus は後回し。

---

## 本ランに含めていないもの

- softplus
- 延長パネル（2005–）での YoY 再走
- 遅れ ΔlogE_{t−1} の本検定
- 水準ローリングの min-train≥5 再走（t=2019落とし）

---

## 成果物パス

- `yoy_prelock_2026-10-24.md` / `yoy_prelock_timestamp.txt`
- `_run_yoy_rolling.py` / `_run_aoff_yoy_diagnostics.py`
- `yoy_rolling_year_wins.csv` / `yoy_rolling_coeffs.csv` / `yoy_rolling_summary.json`
- `yoy_log_err_ratio.csv` / `yoy_log_err_ratio_summary.json`
- `aoff_yoy_gamma_table.csv` / `aoff_yoy_permutation.json`
- `report_yoy_rolling.md` / `report_rolling_continuous.md`（文言修正）
- `majority_rule_general_2026-10-24.md`
- 本ファイル `grok_yoy_handoff_2026-10-24.md`
