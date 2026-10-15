# 年間チーム成績と、年→試合の架空リーグ検証

目的は「中日の長期的なCS不出場を、観測できる量と明示した仮定で調べる」ための入力と検証機構をそろえること。
個人成績は抽出しない。年単位の条件と整合する例・反例を先に作り、必要な段階で試合単位へ進む。

## 主対象と合格ライン

**主対象は2013〜2026年の14年間。実測・合成の両方で、この期間の条件を満たせば合格とする。**
過去年を網羅すること、生成件数を増やすことは完了条件にしない。
2013年以前の実データは任意の参考資料であり、通常の解析・較正・合格判定には使わない。

- [x] 2013〜2026年の両リーグ・年間チーム表を取得・保存・オフライン再解析できる。
- [x] 勝敗・打撃・投手・守備の全掲載列、相手別・ホーム/ロード・交流戦を保持する。非掲載項目を0で補わない。
- [x] 年内の算術・公式表間・既存年表の共通部分・取得SHAを照合する。
- [x] 12球団の架空年成績を先に固定し、対戦容量を満たすと確認してから試合結果へ展開する。
- [x] 各条件の14年すべてで、年成績と独立の試合集計のG/W/L/T/RF/RAが完全一致する。
- [x] 矛盾する勝利数、合計は合うが対戦上実現不能な条件、改ざん試合を拒否する。
- [x] 年の欠落・重複・期間外への置換・負の対照の欠落を合格にしない。
- [x] 条件・年・seed・仮定・ハッシュ・反例を記録し、実測件数と架空件数を混ぜない。
- [x] Python 3.11以上、追加の実行時依存なしで計算する。

## 通常データと参考データの分離

| 区分 | 保存先 | 通常の利用 |
|---|---|---|
| 主対象の元HTML | `data/raw/npb_annual/` | 2013〜2026年の140ページのみ |
| 主対象の観測・照合・年表 | `data/observations/npb_team_annual/` | 14年間の解析・較正・合格判定 |
| 主対象の合成データ | `data/synthetic/annual_leagues/12teams/` | 3条件×各1組の14年間 |
| 取得時の全履歴と旧単年実験 | `data/reference/annual_history_1950_2026/` | 任意の参考保管。通常コマンドから読まない |

以前の1950〜2026年の取得一式は参考側へ移した。そこには2013年以降の重複分も来歴保存のため残るが、合算しない。
参考一式がなくても、主対象だけで取得・検証・合格判定を完了できる。
BlueProbeの歴史的な表を読む能力や来歴fixtureは保持するが、それらは取得範囲を広げる義務ではない。

新規取得は次のコマンドだけでよい。既存の全履歴入りキャッシュ・観測がある場合は先に参考側へ移し、空の主対象ディレクトリで実行する。
QueRyuは別年の既存行をマージして保持するため、全履歴の観測ファイルへ上書きして期間を縮めようとしない。

```bash
uv run python queryu/queryu.py --source npb_team_annual --years 2013-2026 \
  --cache data/raw/npb_annual --out data/observations/npb_team_annual/records.jsonl
# 再実行時は --offline でネットワークなしに復元する。
uv run python blueprobe/blueprobe.py --source npb_team_annual \
  --cache data/raw/npb_annual --out data/observations/npb_team_annual/observed.md --strict
python -S sakanalytics/annual_audit.py \
  --observations data/observations/npb_team_annual/records.jsonl --years 2013-2026 \
  --baseline cycles/c001-chunichi/outputs/season.jsonl \
  --out data/observations/npb_team_annual/audit.json \
  --annual-out data/observations/npb_team_annual/annual.jsonl
```

参考キャッシュが既にある場合だけ、最初の取得の代わりに次で140ページを選択・SHA検証してコピーできる。
コピー先は空でなければ拒否する。元の参考キャッシュには書き込まない。

```bash
python -S queryu/annual_scope.py \
  --cache data/reference/annual_history_1950_2026/raw --out data/raw/npb_annual
```

「全指標」は詳細な公式チーム表と年度別要約表の全掲載列。独自指標や非掲載列を取得済みとは呼ばない。
原文セル・列順・URLを残し、守備の併殺参加/球団を区別する。投球回の`.1`/`.2`は1/2アウトとして整数化する。
整数は完全一致、率は定義から再計算して公表桁で等値比較する。通常桁は四捨五入、順位比較の拡張桁は観測した切捨て表記を明示する。
詳細表と要約表で表示桁が違えば両原文を残し、共通桁で比較する。許容誤差で通さない。
独立の照合先がない一部列は観測保存の範囲であり、全列を二重検証したとは呼ばない。
2020年も年成績の照合対象に含む。上位半分という架空順位を、その年の公式CS開催・出場というラベルには置き換えない。

## 年成績を先に作り、14年単位で確かめる

`synthetic_league.py`は標準ライブラリだけで動く。既定は12球団・3条件・各条件1組の14年間。
単年生成APIと6球団モデルは小さな機構テストにも使えるが、通常の完了条件はこの14年間の組で判定する。

1. ペア別試合数と年間得失点予算を宣言し、球団のRF/RAとピタゴラス期待勝率を得る。
2. 年間期待勝率のLog5を起点に条件と配分係数を適用し、整数の年間勝利数を決める。
3. 整数最大流で全ペアの対戦容量と同時に実現できるか確認し、年成績を固定する。
4. 年成績の保存則を通した後だけ、非負整数の試合スコアへ展開する。
5. 試合を独立に集計して年成績と完全一致を照合し、14年すべてで成功した組を合格とする。

| 条件 | 変えるもの | 確かめること |
|---|---|---|
| aligned | 得失点比に沿う勝敗配分 | 仮定した関係を持つ例を生成・照合できるか |
| same_totals | RF/RAを固定して配分係数を動かす | 同じ期待値でも違う勝敗が実現できるか |
| reversed | 得失点比と逆向きの配分 | 年の量だけでは排除できない反例を作れるか |

```bash
python -S sakanalytics/synthetic_league.py \
  --leagues 2 --calibrate-annual data/observations/npb_team_annual/annual.jsonl \
  --out data/synthetic/annual_leagues/12teams/experiment.json \
  --witness-dir data/synthetic/annual_leagues/12teams/witnesses
```

`--seeds`は条件ごとの14年間の組数で、既定1。合格のために20組・過去年・大量生成を要求しない。
実測から使うのは2013〜2026年のRF/G中央値だけで、共通得点予算の規模を合わせる。
年ラベル・年成績・試合・seed・SHAを保存する。各年は独立の架空モデルであり、年をまたぐ組織特性や14年連続のCS不出場を再現したとは扱わない。
球団間・年次の全分布を適合させたモデルでもない。`same_totals`の配分係数を変えると、同じRF/RAから異なるW/Lを実現できる。

比較用の架空対戦数は同リーグ25試合×5相手、他リーグ3試合×6相手で143試合/球団。
2020年など個々の年の実際の日程、ホーム割、日付、イニング、延長規則は再現しない。
順位は勝率→勝利数→架空球団ID、同率フラグ付き。生成族は各対戦ペア双方1勝以上を条件とする。
この族での入力拒否を野球全体の不可能性の証明とは呼ばない。期待勝利数と実勝利数の残差は保持する。

## 主対象の実行結果（2026-10-15）

- 実測: 2013〜2026年、140ページ、168球団年、1,332件のカテゴリ別記録。未知表記0件。
- 照合: 9,814件一致、不一致0件。参考側の年・件数はこの数字に含めない。
- 合成: 3条件×各14年、42球団群年、36,036試合。年成績と試合集計は42/42一致。
- 14年単位の合格: aligned、same_totals、reversedがそれぞれ14/14、計3/3組。
- 負の対照: 14年×3種類の42/42件を拒否。条件間で共通の機構テストとして数える。

条件内の`P(上位半分 | ピタゴラス勝率 >= 0.5)`は順に1.0/0.5/0.0。
これは仮定下の整合・境界検証であり、NPB実測の確率や中日の原因の支持率ではない。
架空データは実測標本数に足さない。仮定下の実現可能性と具体的な反例を、実データの支持・反例とは別欄に残す。

集約証跡は[annual_history_synthetic_validation.json](outputs/annual_history_synthetic_validation.json)。
通常の集約は期間外の実測や不完全な14年組を拒否する。参考側の検証成功は合格の前提にしない。

```bash
python -S nagoyaction/annual_history_report.py \
  --observations data/observations/npb_team_annual/records.jsonl \
  --audit data/observations/npb_team_annual/audit.json \
  --annual data/observations/npb_team_annual/annual.jsonl \
  --experiment data/synthetic/annual_leagues/12teams/experiment.json \
  --cache-manifest data/raw/npb_annual/manifest.jsonl \
  --out cycles/c001-chunichi/outputs/annual_history_synthetic_validation.json
```
