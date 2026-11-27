# Aoi の自動 seed 選択の形式検証

[`RequestSelection.lean`](RequestSelection.lean) は Aoi 自身が持つ
[`research_loop/autonomous.py::next_request`](../research_loop/autonomous.py) の
「登録済み候補から、停止済み・終端状態の仕事を除いて、先頭を選ぶ」規則を検証する。
Lean 4.36.0 の標準ライブラリだけを使い、通常の Python 実行には Lean を要求しない。
子リポジトリが持つ判定・測定・worker の実装は、それぞれの正本で検証する。

## 実装との対応

モデルの入力は、同じ入力スナップショットについて `next_request` が読む状態を
固定し、登録・feedback の順序を反映した `List SeedJob` とする。

| Python の値・操作 | Lean の表現 | 対応の範囲 |
|---|---|---|
| `sets.toml` の式 ID と末尾の `all` | `SeedJob.seed : Nat` | ID は抽象的な識別子として扱う。TOML 構文はモデル外 |
| 登録済み ID だけを含む feedback 順序 | `ordered : List SeedJob` | 順序変更後の列を入力とする。重複があっても定理は成立 |
| request と同名の stop ファイルから求めた job 集合 | `SeedJob.stopped : Bool` | 選択中にファイルが変わらないスナップショット |
| `completed`, `bounded`, `blocked`, `error` | `JobStatus` の同名の値 | この 4 値だけが `terminal = true` |
| 状態ファイルがない、または上記以外の `status` | `JobStatus.retryable` | 現行実装では `running`・未知の文字列も選択対象になり得る |
| `continue` による除外後の最初の `return` | `List.find? runnable` | 停止・終端状態を除いた最初の候補、なければ `none` |

`retryable` はこの選択器で除外されないという意味であり、実際に worker を再実行して
よいという追加の許可ではない。状態 JSON の破損や `status` 欠落はこの抽象化の前提を
満たさず、Python 実装では例外になる。

| 定理 | 保証する性質 | 実装に接続するテスト |
|---|---|---|
| `Aoi.selected_registered` | 返された候補は入力列に含まれる | 登録された 3 seed の全状態組合せ、未知の priority ID の排除 |
| `Aoi.selected_runnable` | 選択結果は停止済みでも終端状態でもない | 3 seed × 6 状態の組合せを 2 順序で確認 |
| `Aoi.stopped_not_selected` | 列中の位置にかかわらず停止済み候補を返さない | stop ファイルと priority の組合せ、選択後の停止 |
| `Aoi.terminal_not_selected` | 4 種類すべての終端状態を返さない | 各終端状態を個別に保存した実ファイルの組合せ |
| `Aoi.exhausted_iff` | `none` と「選択可能な候補がない」が同値 | 全候補の停止・終端化、選択してから順次終了させるケース |
| `Aoi.selected_prefix_stable` | 既に選べる接頭部分の後ろへの追加は選択結果を変えない | 選ばれる式より後ろに登録式を追加するケース |

最後の定理は、選択前の順序と状態を維持した追加についての性質である。
feedback で先頭に割り込ませる場合や、従来選ばれていた `all` の前に新しい式を入れる
場合には、この前提を適用しない。

## Python 側の接続テスト

[`tests/test_formal_request_selection.py`](../tests/test_formal_request_selection.py)
は実際の `plan`・`digest`・`next_request` を呼ぶ。入力・状態ファイルは一時ディレクトリ
内の合成データであり、外部サービスや実際の研究データを使わない。

```sh
python -S -m unittest discover -s tests -p test_formal_request_selection.py -v
```

停止または 4 種類の終端状態、未保存の 6 状態について、3 seed の全組合せを
通常順・逆順で調べる（`6^3 × 2 = 432` ケース）。期待値は実装の `TERMINAL` 定数を
再利用せず、テストが指定した利用可能な候補と順位から決める。
未知の priority ID、重複、非終端状態、候補の追加、入力スナップショットの変更、
状態ファイルの破損も調べ、選択だけではファイルを書き換えないことを確認する。
これらは普通の回帰テストとして pytest からも実行できる。

## Lean の実行

親リポジトリの
[`lean_verify.py`](https://github.com/myon-bioinformatics/myon-bioinformatics/blob/6c2558c4251698c50bc07bad86fb49f902b2738f/lean_verify.py)
を共通ラッパーとして使う。Aoi のルートから、手元の親リポジトリのパスを指定して実行する。

```sh
python -S /path/to/myon-bioinformatics/lean_verify.py \
  --cwd formal --required \
  --theorem Aoi.selected_registered \
  --theorem Aoi.selected_runnable \
  --theorem Aoi.stopped_not_selected \
  --theorem Aoi.terminal_not_selected \
  --theorem Aoi.exhausted_iff \
  --theorem Aoi.selected_prefix_stable \
  --json-output build/aoi-lean-verification.json \
  RequestSelection.lean
```

`formal/lean-toolchain` が Lean のバージョンを固定する。全定理名を渡すことで、
コンパイル結果に加えて各定理の公理依存を監査する。Lean 専用 CI では `--required` を
使い、Lean 不在・証明失敗・監査失敗を失敗として扱う。任意のローカル実行で
`--required` を省いた場合も、Lean 不在はレポート上 `unverified` であり、証明成功とは区別する。

## 保証の境界

Lean が証明するのは上記の抽象モデルの性質であり、Python 全体との同値性ではない。
接続部分は実際のファイルを使う回帰テストで補う。TOML/JSON パーサー、job ID のハッシュ
衝突耐性、同時書き込み下の競合、研究上の命題の真偽はこの証明の対象に含まない。
各候補の job ID と保存状態が対応していることを前提とする。

複数 seed の自動選択と worker の接続は、引き続き
[`research_loop/README.md`](../research_loop/README.md) に記載した状態とする。
この検証の追加によって worker を有効化したり、停止・再開の権限を変更したりはしない。
