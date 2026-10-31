# Grok 延長再走 — レガシー vs 延長 比較 handoff

**日付:** 2026-10-24（Asia/Tokyo）

**ロック:** `extend_rerun_prelock_2026-10-24.md`（18:49:30 JST）※数学・範囲は変更なし

**判断枠（追加併記）:** `judgment_rules_small_n_2026-10-24.md`（18:51:54 JST）
- 片側符号 p と **p_adj** を併記。数え方: **m=20（形ごと）**、最良形主張は **m_eff=100**（n_forms=5 は別フィールド）。旧表記 m=5 は誤り
- 除外 n=4 全年勝ち p=0.0625 は含む版より弱い、と明記
- 事前宣言指標族のみ；新指標は未検討リストへ（本ランでは走らせない）
- 政党・政権の因果物語は書かない（定義事実のみ備考）
- 止まる規則: 結果後に指標を足さない

**役割:** 数値 = Grok / 判定 = Claude。「政治項は通らなかった」とは書かない → **判断保留**。

---

## 0. 前提訂正・感度（再走前に完了）

- 訂正文書: `premise_corrections_extend_2026-10-24.md`（年次 A≥100=2013；A<50=2012 等）
- 緊急感度: `kinkyu_sensitivity_2008_2009.md`
  - 2008 ΔA（通常−緊急）≈ **−2.63**；ruling 変化なし（LDP 12）
  - 2009 ΔA ≈ **−6.33**；ruling 多数決は LDP のまま（8L/4D → 9L/3D）
  - 緊急優先は**構築ルール**（事前性を prelock で正式固定）。本線パネル未変更
- primary テスト除外（定義域）: 水準 **2013**；YoY **2013・2014**

## 1. 水準ローリング — 方向比較

| form | レガシー 含む (2019–25) | レガシー 除外 | 延長 含む (2010–25*) | 延長 除外 | 延長 sign_p / p_adj | 方向 |
|---|---|---|---|---|---|---|
| primary_100 | 1/7 | 0/6 | 3/15 | 2/14 | 0.996307 / 1.0 | 同じ（過半数未達） |
| alt200 | 2/7 | 2/6 | 4/16 | 4/15 | 0.989365 / 1.0 | 同じ（過半数未達） |
| exp_neg | 2/7 | 2/6 | 3/16 | 3/15 | 0.99791 / 1.0 | 同じ（過半数未達） |
| aoff | 4/7 | 4/6 | 5/16 | 5/15 | 0.961594 / 1.0 | 異なる |
| prop_A | 0/7 | 0/6 | 1/16 | 1/15 | 0.999985 / 1.0 | 同じ（過半数未達） |

\* primary 延長の分母は 2013 定義域除外後（含む n=15 / 除外 n=14）。他形は n=16 / 15。

### 水準の読み（数値）

- 延長でも全形が **wins > n/2 を満たさない**。レガシーでも aoff 以外は過半数未達（aoff レガシー 4/7 は >3.5 で過半数だが、延長では 5/16 に落ちる）。
- オーバーラップ年（2019–2025）で勝敗が変わった例: aoff の 2020–2022 はレガシー勝→延長負；alt200/exp_neg の 2022 も同様。訓練窓を 2005 まで伸ばした効果。
- 片側 p はいずれも大きく、p_adj(m=20 / m_eff=100) は 1。稀な勝ち方とは言えない。
- 政治項（primary/alt200/exp/prop_A）: **判断保留**（検出できず／過半数未達）。「通らなかった」とは書かない。

## 2. 前年比（YoY）ローリング — 方向比較

| form | レガシー 含む (2021–25) | p / p_adj | レガシー 除外 | p | 延長 含む (2011–25*) | p / p_adj | 延長 除外 | 連続読み(延・含) | 方向 |
|---|---|---|---|---|---|---|---|---|---|
| aoff_yoy | 5/5 | 0.0312/0.1562 | 4/4 | 0.0625 | 6/15 | 0.849121/1.0 | 5/14 | 検出できず | 異なる（レガシー過半数＋crit1、延長は過半数未達） |
| primary_yoy | 3/5 | 0.5000/1.0000 | 3/4 | 0.3125 | 4/13 | 0.953857/1.0 | 4/12 | 検出できず | 異なる |
| alt200_yoy | 3/5 | 0.5000/1.0000 | 3/4 | 0.3125 | 5/15 | 0.940765/1.0 | 4/14 | 検出できず | 異なる |
| exp_neg_yoy | 3/5 | 0.5000/1.0000 | 3/4 | 0.3125 | 5/15 | 0.940765/1.0 | 4/14 | 検出できず | 異なる |
| prop_A_yoy | 3/5 | 0.5000/1.0000 | 3/4 | 0.3125 | 4/15 | 0.982422/1.0 | 4/14 | モデルが悪い | 異なる |

\* primary_yoy 延長は 2013・2014 を NA（Δlog(100−A) 未定義）→ 含む n=13。

### YoY の読み（数値）

- **aoff_yoy:** レガシーは 5/5（p≈0.031、p_adj≈0.63（m=20）/ 1（m_eff=100））／除外 4/4（p=0.0625・弱い）。延長は **6/15**（p≈0.85、過半数未達）。連続も「検出できず」。**同じ方向とは言えない。**
- 政治項 YoY 4形: レガシーは 3/5 で過半数だが p=0.5（判断保留と両立）。延長でも過半数未達・p 大・連続は検出できずまたは prop_A のみ「モデルが悪い」。**判断保留。**
- 最良形を強調するなら aoff レガシーでも p_adj≈0.63（m=20）/ 1（m_eff=100） で有意とは言えない（judgment_rules §2）。
- 除外版の全年勝ちを結論に使う場合は p=0.0625 の弱さを本文に残す。

## 3. 構造変化の候補年（定義事実・並べるだけ）

| 年 | 定義事実（因果評価なし） |
|---:|---|
| 2009 | 年次 ruling_first=LDP（月数多数決 8 vs 4）。月次 A は 9–12 月 DPJ。緊急優先 Sep。感度で通常にすると Sep は LDP のまま |
| 2012 | 年次 A=44.17（50 未満）。ruling_first=DPJ。法則領域の単独検証には使わない（交絡注記） |
| 2013 | 年次 A=100.87（7/12 月 A≥100）。primary 定義域外（K NA；水準テスト・YoY primary の 2013/2014 NA） |

これらを「政権交代だから効く／効かない」とは書かない。数値テーブル上の区切り候補として並記。

## 4. E の狭さ（2005–2014）

- E ∈ [0.229, 0.240]（2005–2014）vs [0.250, 0.286]（2015–2025）
- ΔlogE も小さい → 延長前半だけの γ̂／順列は検出力が弱い。judgment_rules 未検討リスト: その区間での採択はしない（注記のみ）
- これが延長 YoY で aoff がレガシーほど勝てなく見える一因になり得るが、因果断定はしない

## 5. 延長テーブル用 p / p_adj 一覧（m=20 形ごと／m_eff=100 最良形；いずれも p_adj=1）

### 水準（延長）

| form | 含む wins | sign_p | p_adj | 除外 wins | sign_p | p_adj |
|---|---:|---:|---:|---:|---:|---:|
| primary_100 | 3/15 | 0.996307 | 1.0 | 2/14 | 0.999084 | 1.0 |
| alt200 | 4/16 | 0.989365 | 1.0 | 4/15 | 0.982422 | 1.0 |
| exp_neg | 3/16 | 0.99791 | 1.0 | 3/15 | 0.996307 | 1.0 |
| aoff | 5/16 | 0.961594 | 1.0 | 5/15 | 0.940765 | 1.0 |
| prop_A | 1/16 | 0.999985 | 1.0 | 1/15 | 0.999969 | 1.0 |

### YoY（延長）

| form | 含む wins | sign_p | p_adj | 除外 wins | sign_p | p_adj | 連続読み(含) |
|---|---:|---:|---:|---:|---:|---:|---|
| aoff_yoy | 6/15 | 0.849121 | 1.0 | 5/14 | 0.910217 | 1.0 | 検出できず |
| primary_yoy | 4/13 | 0.953857 | 1.0 | 4/12 | 0.927002 | 1.0 | 検出できず |
| alt200_yoy | 5/15 | 0.940765 | 1.0 | 4/14 | 0.971313 | 1.0 | 検出できず |
| exp_neg_yoy | 5/15 | 0.940765 | 1.0 | 4/14 | 0.971313 | 1.0 | 検出できず |
| prop_A_yoy | 4/15 | 0.982422 | 1.0 | 4/14 | 0.971313 | 1.0 | モデルが悪い |

## 6. 未検討リスト（本ランでは走らせない）

- softplus / 新規殻
- 遅れ ΔlogE_{t−1}
- マスク／エンコード・デコード近似族（別トラック）
- 政党・政権の因果ストーリー指標
- 延長前半だけの γ̂／順列を検出力ありとして採択すること

## 7. 新規ファイル一覧（レガシーは未変更）

- `extend_rerun_prelock_2026-10-24.md`
- `extend_rerun_prelock_timestamp.txt`
- `premise_corrections_extend_2026-10-24.md`
- `kinkyu_sensitivity_2008_2009.md`
- `kinkyu_sensitivity_2008_2009.csv`
- `kinkyu_sensitivity_month_detail.csv`
- `raw/bunken_2008.html`
- `raw/bunken_2009.html`
- `judgment_rules_small_n_2026-10-24.md`
- `_run_rolling_origin_extended.py`
- `rolling_origin_extended_year_wins.csv`
- `rolling_origin_extended_coeffs.csv`
- `rolling_origin_extended_summary.json`
- `report_rolling_origin_extended.md`
- `_run_yoy_rolling_extended.py`
- `yoy_rolling_extended_year_wins.csv`
- `yoy_rolling_extended_coeffs.csv`
- `yoy_rolling_extended_summary.json`
- `report_yoy_rolling_extended.md`
- `yoy_log_err_ratio_extended.csv`
- `yoy_log_err_ratio_extended_summary.json`
- `grok_extend_compare_handoff_2026-10-24.md`

**レガシー未変更（確認）:**

- `rolling_origin_year_wins.csv`
- `rolling_origin_coeffs.csv`
- `rolling_origin_summary.json`
- `report_rolling_origin.md`
- `yoy_rolling_year_wins.csv`
- `yoy_rolling_coeffs.csv`
- `yoy_rolling_summary.json`
- `report_yoy_rolling.md`
- `yoy_log_err_ratio.csv`
- `yoy_log_err_ratio_summary.json`
- `gohantrust_panel_aoki.csv`

## 8. Blockers

- なし（感度・水準延長・YoY延長・比較まで完了）
- softplus / 遅れ / エンコード近似は意図的に未実施（未検討リスト）
