# 問い合わせ（`queryu/ask/ask.py`）

日本語の問い（「E25 に阪神 2015 以外の判例はある？」）を決まった型（`Query`）に直し、PythDRagoras が判定済みの結果（`propositions.jsonl`・`sets.jsonl`）から答える。ネットワークに出ない。モデルも API キーも使わない。

## 考え方（Jev の「型で縛った選択」から拾ったもの）

| Jev | ここ |
|---|---|
| 戻り値の型が問いの種類になる（はい・いいえ、選択肢、点数） | `Query` の各項目が、選べる値の決まった選択（`ask`・`kind`・`form` は enum、ID と単位は形の決まった文字列） |
| 許した値の中からしか答えない | 読み取りは登録済みの値（命題・式の ID、球団名、4つの形、問いの種類）だけを選ぶ。読めなかった語は `unread` に返す（黙って捨てない） |
| 数え上げ・算術は苦手 | 数（%・年）は正規表現で読む。判例の有無・数・成立率は数え直さず、判定済みの結果を引く |

役割: **読み取り**（問い → Query）と**答え**（Query → 判定済みの結果）を分ける。読み取りは取り替えられる:

1. いま: 古典的な読み取り（正規表現と語の一覧）
2. あとで: `--schema` の JSON Schema を llama.cpp（`json_schema` で出力を縛る）や MCP のツールの引数に渡し、ローカルの LLM に Query を選ばせる。選んだ Query は `--query` で直接渡す。答えは同じ関数が出すので、同じ Query なら同じ答え

## Query

| 項目 | 値 |
|---|---|
| `ask` | `has_counterexample`（はい・いいえ）・`counterexamples`（一覧）・`unique_exception`（判例がちょうど1つ）・`rate`（成立率の条件） |
| `target` | `P96`・`E25` など。なければすべて |
| `kind` | `any`・`proposition`（「命題」）・`expression`（「式」） |
| `form` | `original`・`contrapositive`（対偶）・`converse`（逆。「逆に」は形として読まない）・`inverse`（裏） |
| `exclude` | 判例から除く単位（「阪神 2015 以外」→ `t-2015`） |
| `about` | この単位・球団が判例にいるものだけ（`t-2015`・`d`） |
| `min_rate`・`max_rate` | 成立率（「95% 以上」「8割以上」） |

## 使い方

```
python queryu/ask/ask.py "判例がただ1つの式は？"
python queryu/ask/ask.py "P96 の対偶の判例" --json
python queryu/ask/ask.py --query '{"ask": "has_counterexample", "target": "E26"}'
python queryu/ask/ask.py --schema
python queryu/ask/ask.py "中日が判例の命題" --results <結果フォルダ> --teams <球団表.json> --log <ログ.jsonl>
```

「式」を含む問いは `sets.jsonl` がある結果ディレクトリで実行する。main の `outputs` だけを渡すと、そのファイルが無いので `結果が読めない` になる。

- `--log` は問いの原文と読み取った Query を1行ずつ残す（再現のため）
- 判例の一覧が判定の出力で省かれている場合は「一覧は一部」と出す
- `--results` は必須。サイクルの `pipeline.toml` や結果 ref からの解決は Aoi の `aoi_paths.py` がして、決まったフォルダを渡す
- `--teams` は球団名 → コードの JSON。渡さなければ球団名は読まず unread に返す（Aoi は NPB の表を渡す）
- `--cycle-dir` があればその `ask.toml` を、なければ結果フォルダの親の `ask.toml` を読む
- 終了コード: 0 = 答えた、1 = 判定不能（結果が読めない、ID が結果にない、読めなかった語）、2 = `--query` が型の外

未対応の語・条件が残った場合も終了コード1で解釈確認を求め、条件を捨てて回答しない。

### 未解釈入力の証跡（Issue #30）

`parse_input()` は読み取り用の NFKC・空白正規化と、保存する原文を分ける。
`parse()` の既存の `(Query, unread)` 契約は維持する。
CLI の JSON・`--log` の JSONL・受付の受領記録には同じ証跡を持たせる。

| 項目 | 意味 |
|---|---|
| `raw_text` | 正規化前の問い全体。受付では `/ask` の引数（コマンド本文全体は受領記録の `body`） |
| `unread_spans` | 未解釈の範囲の `start`・`end`・`raw_text`。0始まり、終了位置を含まない Python Unicode code point 単位。常に `raw_text[start:end]` が範囲の原文と一致する。UTF-8 byte・UTF-16 offset ではない |
| `parse_status` | 機械値 `parsed` / `undetermined`。`parsed` は構文が読めたという意味で、研究上の成立判定ではない |
| `parse_diagnostics` | 安定した `code` と人間向けの `explanation`。説明文で機械判定しない |
| `unread` | 互換性のための人間向け表示。原文・span の正本ではない |

Q5 `P121 は 2026 年で確かめられた？` は `parse_status=undetermined`。
`unread_spans` は `{start: 7, end: 20, raw_text: "2026 年で確かめられた"}` を保持する。
理由コードは `unrecognized_ask`・`unsupported_text`。回答は引き続き「判定不能」で、
P121 の既存結果・2026 年の暫定結果には対応付けない。
未解釈入力を止めた回答は機械値 `status=undetermined` と `reason_codes` を持ち、
日本語の `answer`・`error`・`unread` は表示として別に保持する。

助詞は残った範囲全体が既知の接続表現の場合か、空白で区切られた先頭の助詞の場合に限って扱う。
未知語の途中の「か」「で」等は削らない。「とか」等の未知の条件も、文字を消して空にしない。
未解釈入力は既知回答・回答キャッシュの読取りと書込みを迂回し、候補は候補としてだけ提示する。
新しい証跡も `ask.py` 内に置くため、既存の回答コード hash で古いキャッシュを無効にする。
取得計画・正式評価器・研究データは変更しない。

結果なし・該当する形なし・判定不能単位が残る場合には、反例が確認できないことを
「いいえ」と断定しない。不完全な反例一覧を使った除外や球団指定も同様に扱う。
反例数は `n - hold`。`undetermined` は `n` の外に数えられているため二重に引かない。

コメント受付・探索の運用は [NagoyAction](../../nagoyaction/docs/inbox.md)。

## 候補の提示（`queryu/ask/suggest.py`）

ID が書いていない問いについて、登録済みの命題・式の文に近いものを最大5件出す。文字 1〜3-gram の TF-IDF を SVD で落とし、任意で符号と次元スケールに圧縮した索引も使える。

これは答えではない。`ask.py` の読み取り（`parse`）も答え（`answer`）も呼ばない。1位の類似度が閾値未満なら「判定不能」で、候補は確定しない。閾値以上でも status は「要確認」で、選ばれた ID は置かない。1位を `ask.py` に渡して自動で答えない。

閾値の既定値はない。試作では、手書きの範囲外の問いの最高類似度のすぐ上に置いた。その小さな集合に合わせた値で、過学習の恐れがある。隣り合う ID（内容の近い命題・式）を取り違えることもある。問いに ID が書いてあるときは索引を使わず、その ID を返す。書いてある ID と、問いが指しているものが違うこともある。

補足: 類似度が同じ候補は文書の並び順で出す（安定ソート）。問いに書いてある ID が読み込んだ命題・式に無いときは、`known: false` と note で知らせる（`selected` は書いてある ID のまま）。

## 判定不能のときの候補（もしかして）

読めなかった語があるとき、または指定した ID が読めた結果の中に無いとき、返信の末尾に最大 5 件を足す。

```text
もしかして: P46 / P47（候補。答えではない）
```

### 観測

- 候補は `queryu/ask/suggest.py` の類似度から取る。問いに書いてある ID は、その ID を繰り返すためではなく、文の残りで近い ID を並べるために外す。
- 類似度の閾値は `cycles/<cycle>/ask.toml` の `suggest_threshold`。`--suggest-threshold` を渡したときはその数。
- c001 の `ask.toml` には、このキーを置いていない。

### 解釈

- この行は候補の一覧であり、判定ではない。`answer` も `Query.target` も、候補では書き換えない。
- キーが無いあいだは、どの候補も「閾値を超えた」とは扱わない。試作で手書きの問いに合わせた類似度は、サイクルの設定に写さない。
- 必要な結果ファイルが無いときは「結果が読めない」とし、候補は出さない。ID が無い、とは分けて書く。未対応語のため解釈確認になった問いでも、読み取った Query に必要なファイルが不足していれば候補を出さない。

## 結果が読めない

`E25` のように式の ID は `sets.jsonl` を必要とする。命題の ID は `propositions.jsonl` を必要とする。ID のない「命題と式」の問いは両方を必要とする。

### 観測

- main の `cycles/c001-chunichi/outputs` には `propositions.jsonl` があり、`sets.jsonl` は無い。
- 必要なファイルが無いときのエラーは `結果が読めない: sets.jsonl` のように、ファイル名を含む。
- ファイルはあり、その中に ID が無いときだけ `判定済みの結果にない` になる。

### 解釈

- ファイルが無いことを「その ID は判定済みでない」とは読まない。式の結果は、Issue #9 のとおり結果 ref の checkout（`.aoi-results/<cycle>/outputs`）から読む。
- 指定した結果フォルダが無いとき、別のフォルダへは切り替えない。`sets.jsonl` をこのリポジトリに作って埋めもしない。

四つの形の表と条件の記号は [DRAgoWing](../../dragowing/docs/forms.md)。
