# Research digest (compaction-pattern / Aoi #20)

対象は `cycles/c001-chunichi/research/R*.md`。全体の R 記録を省略せず走査する、ネットワーク不要・LLM不要の索引である。研究上の結論を再判定しない。

## 実行

```bash
uv run python nagoyaction/research_digest.py cycles/c001-chunichi
uv run python nagoyaction/research_digest.py cycles/c001-chunichi --check
uv run pytest -q nagoyaction/tests/test_research_digest.py
```

`pipeline.toml` の `digest` ステップは `judge` の後で実行する。既存の `--offline` フル実行時には取得済みキャッシュが必要だが、このスクリプト単体はキャッシュ不要。CI は同じ入力から2度生成（2度目は `--check`）し、生成された2ファイルを artifact として保存する。

## データの読み方

- `research_digest.jsonl`: R 1件を1行とし、ID・表題・記録日・参照先・Markdown内の表先頭セルの命題ID・見直し条件・現行終了コードを記録する。`duplicate_table_ids`、`unknown_ids`、`missing_judgements`、`missing_fields` は欠落させない。
- `research_digest.md`: 人間向け一覧と、未知/未解析の項目、登録された判定基準、FINDINGSの限定的な照合を表示する。
- `proposition_ids` は表の第一列で見えたID。`defines` はこのうち研究記録で扱う命題だが、**R18の表は過去に立てた命題の再検証計画なので `defines=[]`** として `confirmation_focus_ids` を別記する。表行がないRでは `proposition_ids=[]` と診断する（自動で「研究がない」とは結論しない）。
- `review.status`: `explicit` は `見直す条件` の箇条書きが取れた、`pre_registered` は別見出しの事前登録基準が取れた、`unparsed` は対応する見出しはあるが規則を抽出できない、`unknown` は対象見出しを識別できない状態。最後の2つはいずれも「条件なし」ではない。
- `review.criteria`: 読み方表の先頭セルに命題IDを持つ行から、**読み方の文字列を変更せず**保存する。R18のP52は『逆の判例2件以上』『判例3件以上』という別々の閾値を保持する。新しい表記に対応できない場合は抽出を改善し、判定を推測して埋めない。
- `current_judgements`: Polarsで `propositions.jsonl` の `judgement.code` だけを投影して結合する。JSONL内の複合型・数値混在カラムをNDJSONとしてPolarsへ丸読みしない。総合判定は後から増えた観測を含み得るため、**2026年の独立検証の合否ではない**。
- **2026年の独立検証**はR18に事前登録した読み方と、別の `outputs/confirmation.md` の2026年の単位で行う。歴史データを使った条件探索、結果を見た後の仮説、通常の総合判定を流用して『独立検証で支持』とは書かない。

## FINDINGSとの照合の限界

`FINDINGS.md` の命題IDを登録簿・研究記録のIDと突き合わせる。終了コードの数値比較は、同じ行に `Pnn` と `exit N` が明示されている場合だけ実施する。文章による『支持』『異議』をキーワードで推測しないため、`unverified_prose=true`。数値や文章の転記を勝手に更新しない。

固定したMarkdownヘルパーは `vendor/markdown.py`、出所とSHA-256は `vendor.lock.json`、MITライセンスは `vendor/markdown-LICENSE`。依存を上流最新へ暗黙に動かさない。
