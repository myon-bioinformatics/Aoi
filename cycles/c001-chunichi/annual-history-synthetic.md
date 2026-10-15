# 年間チーム成績と、年→試合の架空リーグ検証

目的は「中日の長期的なCS不出場を、観測できる量と明示した仮定で調べる」ための入力と検証機構をそろえること。
個人成績は抽出しない。年単位の条件と整合する例・反例を先に作り、必要になった段階で試合単位へ進む。

## このPRの完了条件

- [x] NPBの1950〜2026年、両リーグの年度別チーム表を取得・保存・オフライン再解析できる。
- [x] 2005〜2026年の詳細な勝敗・打撃・投手・守備の全掲載列を取得できる。対戦相手別・ホーム/ロード・交流戦の表も保持する。
- [x] 古い年に未掲載の項目はnullまたは列なしとし、球団数・旧球団名を現行12球団へ無理に置き換えない。
- [x] 年表内の算術、別の公式表との共通列、既存の2012〜2025年成績との整数項目を照合し、結果と不一致を保存する。
- [x] 6球団・12球団の年成績を作り、年の勝敗・得失点・対戦数の制約を確認してから試合を生成する。
- [x] 生成した試合を独立に集計し、各球団のG/W/L/T/RF/RAが年成績と完全一致する。
- [x] 矛盾した年成績、対戦組み合わせ上の実現不能、改ざんした試合を拒否する。
- [x] 条件別・seed別の成功数・反例・再現用ハッシュを記録し、実測件数と架空件数を混ぜない。
- [ ] Python 3.11〜3.15のCIと既存のオフライン検証を通す。

## 取得範囲と同一性

BlueProbeの `npb_team_annual.py` をQueRyuの既存取得機構へ接続する。
二リーグ制の1950年を起点とする。1936〜1949年の一リーグ制・春秋期別記録は今回の範囲外。
2005年以降は詳細表4種類に加え、年度別要約表を独立した照合先として読む。
1950〜2004年は年度別要約ページに掲載されたチーム勝敗・打撃・投手の全列を読む。
「全指標」はこれらの公式チーム表の掲載列を指す。非掲載の守備列や、独自指標を取得済みと呼ばない。

ヘッダーの行・列結合を展開して読み、原文セル・列の順序・取得URLも保持する。
守備の併殺参加/球団は別項目。投球回の `.1` / `.2` は10進小数でなく1/2アウトとして整数化する。
旧球団名は原文のまま識別し、未検証の球団の系譜を自動推測しない。

実データは `data/raw/npb_annual` と `data/observations/npb_team_annual` に置く。
取得済み本文を再利用し、3秒の直列間隔と条件付きGETを使う。失敗したHTTP応答を成功として保存しない。

```bash
uv run python queryu/queryu.py --source npb_team_annual --years 1950-2026 \
  --cache data/raw/npb_annual --out data/observations/npb_team_annual/records.jsonl
# 同じコマンドに --offline を付けるとキャッシュのみで再現する。
uv run python blueprobe/blueprobe.py --source npb_team_annual \
  --cache data/raw/npb_annual --out data/observations/npb_team_annual/observed.md --strict
python -S sakanalytics/annual_audit.py \
  --observations data/observations/npb_team_annual/records.jsonl --years 1950-2026 \
  --baseline cycles/c001-chunichi/outputs/season.jsonl \
  --out data/observations/npb_team_annual/audit.json \
  --annual-out data/observations/npb_team_annual/annual.jsonl
```

整数は完全一致で照合する。打率・長打率・出塁率・防御率・守備率は、定義から再計算した値と公表桁で等値比較する。通常桁は四捨五入、順位比較のために拡張された桁は、実表で観測した切捨て表記を明示して適用する（例: 1961年巨人、958/4228→.2265）。許容誤差で通す処理は使わない。
詳細表と要約表で表示桁が異なる率は、原文の両方を残し、共通の公表桁へそろえた値を等値比較する。要約表の拡張防御率は、詳細表の自責点・アウト数からも再計算する。
二重計上しないよう、全体の保存則は詳細表と要約表で別々に確認する。
歴史的な勝率規則を未検証のまま現行規則へ置換しないため、2004年以前の勝率再計算は保留する。
掲載値は保持し、共通列の表間一致と、勝・敗・分の整数整合は古い年にも適用する。
独立の照合先を持たない一部列は「観測を保存した」範囲であり、全列を別ソースで二重検証したとは呼ばない。

## 年成績を先に作る

`synthetic_league.py` は標準ライブラリだけで動く。

1. 6球団×1/2リーグと、球団ペアごとの試合数を宣言する。
2. ペアごとの年間得点・失点予算から、球団の年RF/RAとピタゴラス期待勝率を計算する。
3. 年間ピタゴラス勝率のLog5を起点に、明示した配分仮定を適用し、年間期待勝利数を得る。
4. 年間の整数勝利数を決め、整数最大流で全ペアの対戦数と同時に実現できるか確認する。
5. 年成績・ペア別の勝敗/引分・得点予算を固定し、年全体の保存則を検証する。
6. 検証済みの年予算だけを試合の非負整数スコアへ展開する。
7. 試合集計から年成績を再計算し、G/W/L/T/RF/RAとペアごとの試合数を完全一致で照合する。

矛盾する年勝利数・合計は釣り合うがペアの容量制約に反する年成績・改ざん試合を、seedごとに負の対照として試す。成功例とは別の拒否件数を記録する。

既定の12球団モデルは、同リーグの各相手と25試合、他リーグの各相手と3試合で1球団143試合。
これは比較用の架空対戦数であり、特定年のNPB日程やホーム割・移動日・延長規則の再現ではない。
6球団だけなら1球団125試合。日付やイニング、打撃・守備のプレー明細は生成しない。
同率の順位は勝率→勝利数→架空球団IDという明示した架空規則。NPBのCS規則とは別に同率フラグを残す。

この生成族は各ペアに双方1勝以上を要求する。これに反する入力の拒否は、野球全体での不可能性の証明ではない。
一方、合計勝利数が正しくても、対戦相手間の容量制約に反するケースは最大流で検出できる。
ピタゴラス期待勝利数と実勝利数は一致を強制しない。残差を観察対象として保持する。

## 3つの生成条件

| 条件 | 変えるもの | 確かめること |
|---|---|---|
| aligned | 年間の得失点比に沿う勝敗配分 | 仮定した関係を持つ例を生成・照合できるか |
| same_totals | 年間RF/RAを固定して配分係数を動かす | 同じピタゴラス期待値でも違う勝敗が実現できるか |
| reversed | 年間の得失点比とは逆向きの勝敗配分 | 年全体の量だけでは排除できない反例を作れるか |

```bash
python -S sakanalytics/synthetic_league.py \
  --seeds 20 --leagues 2 --calibrate-annual data/observations/npb_team_annual/annual.jsonl \
  --calibration-years 2013-2026 --conversion 1.0 \
  --out data/synthetic/annual_leagues/experiment.json \
  --witness-dir data/synthetic/annual_leagues/witnesses
```

実データから使うのは指定期間のRF/Gの中央値で、共通得点予算の規模だけを合わせる。
球団間・年次の全分布や相関まで適合させたモデルではない。係数・確率・整数化・seed・年予算・試合データを保存する。
`same_totals` の `--conversion` を正負で変えれば、同じ年RF/RAのまま異なる勝敗の証人を作れる。

条件付き確率と成功件数は**宣言した生成モデル内**の集計。
意図して関係を作った条件で成功率が高くても、中日の実際の原因を確認した証拠にはならない。
架空例を増やしても実測の標本数は増えない。追加の根拠となるのは、仮定下での実現可能性、計算の整合、単純な命題に対する具体的な反例。
実データによる支持・反例とは別の欄に残す。

## 実行結果（2026-10-15）

- 実データ: 330ページ、1950〜2026年の939球団年、4,125件のカテゴリ別記録。
- BlueProbeの未知表記0件。HTTP 502で失敗した3ページは再取得し、キャッシュ330キーを確認。
- 年内・表間・既存年表・取得データのハッシュを含む19,943件の照合がすべて一致。不一致0件。
- 2013〜2026年の168球団年のRF/G中央値で、架空リーグの共通得点規模だけを調整。

| 架空リーグ | 条件×seed | 年成績検証 | 試合集計との完全一致 | 試合数 | 負の対照の拒否 |
|---|---:|---:|---:|---:|---:|
| 6球団 | 3×20 | 60/60 | 60/60 | 22,500 | 60/60 |
| 12球団 | 3×20 | 60/60 | 60/60 | 51,480 | 60/60 |

生成条件ごとの `P(上位半分 | ピタゴラス勝率 >= 0.5)` は、整合側1.0、同じ得失点合計側0.5、逆向き側0.0。
これは関係を意図して変えた生成モデル内の値であり、NPB実測の確率や中日の原因に対する支持率ではない。
同じRF/RAから異なるW/Lを実現できるという具体例が、得失点合計だけの説明の境界を示す。

集約証跡は [annual_history_synthetic_validation.json](outputs/annual_history_synthetic_validation.json)。
元HTML・抽出表・全照合行・年予算・試合結果は別の再利用用データ一式に保存し、gitには生データを追加しない。

集約証跡の再生成:

```bash
python -S nagoyaction/annual_history_report.py \
  --observations data/observations/npb_team_annual/records.jsonl \
  --audit data/observations/npb_team_annual/audit.json \
  --annual data/observations/npb_team_annual/annual.jsonl \
  --experiment data/synthetic/annual_leagues/6teams/experiment.json \
  --experiment data/synthetic/annual_leagues/12teams/experiment.json \
  --cache-manifest data/raw/npb_annual/manifest.jsonl \
  --out cycles/c001-chunichi/outputs/annual_history_synthetic_validation.json
```
