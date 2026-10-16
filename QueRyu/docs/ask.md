# 問い合わせ（`QueRyu/ask/ask.py`）

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
python QueRyu/ask/ask.py "判例がただ1つの式は？"
python QueRyu/ask/ask.py "P96 の対偶の判例" --json
python QueRyu/ask/ask.py --query '{"ask": "has_counterexample", "target": "E26"}'
python QueRyu/ask/ask.py --schema
python QueRyu/ask/ask.py "中日が判例の命題" --log cycles/c001-chunichi/outputs/asked.jsonl
```

- `--log` は問いの原文と読み取った Query を1行ずつ残す（再現のため）
- 判例の一覧が判定の出力で省かれている場合は「一覧は一部」と出す
- 終了コード: 0 = 答えた、1 = 指定した ID が結果にない、2 = `--query` が型の外

未対応の語・条件が残った場合も終了コード1で解釈確認を求め、条件を捨てて回答しない。
結果なし・該当する形なし・判定不能単位が残る場合には、反例が確認できないことを
「いいえ」と断定しない。不完全な反例一覧を使った除外や球団指定も同様に扱う。
反例数は `n - hold`。`undetermined` は `n` の外に数えられているため二重に引かない。

コメント受付・探索の運用は [NagoyAction](../../NagoyAction/docs/inbox.md)。
