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
uv run python nagoyaction/annual_history_report.py \
  --observations data/observations/npb_team_annual/records.jsonl \
  --audit data/observations/npb_team_annual/audit.json \
  --baseline cycles/c001-chunichi/outputs/season.jsonl \
  --annual data/observations/npb_team_annual/annual.jsonl \
  --experiment data/synthetic/annual_leagues/12teams/experiment.json \
  --cache-manifest data/raw/npb_annual/manifest.jsonl \
  --out cycles/c001-chunichi/outputs/annual_history_synthetic_validation.json
```

## 合格推奨の参考検証：既存命題から新しい命題へ

合成データへの既存命題の適用は、合格推奨の参考検証とする。成立率の低下、反例、取りこぼしを理由にPRや合成データを不合格にはしない。
年成績と試合集計の完全一致などの機構上の必須条件とは分けて扱う。命題が全条件で成立することは要求しない。

反例や取りこぼしは、新しい命題・条件分岐・指標を見つける材料として残す。
成立率が保たれる結果は、宣言した仮定の中で説明の方向性が保たれたという補助材料になる。
どちらの結果も探索の成果として扱い、実データによる支持・独立した年での確認へつなぐ。
合成データの成立率だけで現実の原因や命題の正しさを確定せず、結果に合わせて既存IDの定義を変更しない。

### 参考実行（2026-10-15）

既存の`propositions.py`の定義・判定を使い、3セット各168球団年でP2・P50・P52・P96を試した。
試合の最終スコアから必要な分布・配分指標を既存の`rank_probability`・`allocation_table`で計算した。
イニングや日付・試合順の情報を必要とする命題は今回の対象にしない。実測の台帳・合格判定には加算しない。

| 命題 | aligned | same_totals | reversed |
|---|---:|---:|---:|
| P2：期待順位が上位なら実順位も上位 | 84/84 | 84/168 | 0/84 |
| P50：得失点分布から上位の見込みが高ければ上位 | 63/65 | 81/89 | 24/81 |
| P52：分布の見込みが低い、または配分が不利なら下位 | 79/91 | 83/83 | 66/102 |
| P96：複数条件で下位を説明する式 | 53/66 | 84/84 | 30/30 |

分子は成立数、分母は前提条件に当たる球団年。全168件に対する分類正解率ではない。
P96が拾った下位は順に53/84・84/84・30/84で、取りこぼしは31・0・54件。
reversedの30/30という成立率と54件の取りこぼしを両方残し、説明できる範囲を探す材料にする。
same_totalsのP2は期待勝率が全チーム同率になり、既存の同率最上位（rank min）の扱いで全168件が前提に入る。
これらの差を、命題が使う情報の範囲や新しい分岐を検討するきっかけとして扱う。

## PR #39の独立レビュー後の再検証

[レビュー記録](annual-history-review39.md)と[追加検証の集約証跡](outputs/annual_history_review39.json)を参照。
従来の9,814件・42球団群年の記録は取得時点の結果として保持する。
追加した検証項目による件数を、実測標本数の増加とは扱わない。

集約時は保存済みの元HTML140ページをSHA・バイト数・公式URL・年の対応まで確認して再解析し、原文セルを含む全観測記録と比較する。
年表と監査全項目（既存年表を使う場合はそのSHAも含む）を再計算し、較正値・168個の一意な球団年・全合成ケース・試合SHA・負の対照・集約値を照合する。
旧監査は新しい項目を含まないため、上記のannual_auditを先に再実行する。--baselineは両コマンドで同じファイルを指定する。
合成生成と算術監査は標準ライブラリだけで動く。元HTML再解析を含む集約は既存BlueProbeのselectolaxを使うためuv runで実行する。新しい依存パッケージは追加しない。

元HTMLと観測台帳の再解析照合だけを行う場合:

```bash
uv run python queryu/annual_scope.py --cache data/raw/npb_annual \
  --verify-observations data/observations/npb_team_annual/records.jsonl
```
