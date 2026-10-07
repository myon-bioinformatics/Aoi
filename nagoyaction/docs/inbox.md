# NagoyAction の質問受付

#10 では、main に **質問受付だけ** を入れる。探索ワーカー、HTML フィードバック、ローカル LLM のモデル取得・Docker 起動はこの PR の対象外とし、main の構成に合わせた後続 PR へ分ける。

## 使えるコマンド

| コメント | 動作 |
|---|---|
| `/ask E25 に阪神 2015 以外の判例はある？` | 保存済みの結果から回答 |
| `/ask {"ask":"has_counterexample","target":"E25"}` | 型付き JSON で質問 |
| `/status` | 受付件数、回答キャッシュ、返信再送待ちを表示 |
| `/explore ...` | #10 では未導入と明示して終了 |
| `/stop ...` | #10 では探索未導入のため停止対象なしと返す |

通常の会話には反応しない。1 コメント 1 コマンド、4000 文字まで。コメント編集は再実行しない。修正した依頼は新しいコメントで投稿する。

## コードと結果を分離する

実行コードは既定ブランチ（main）から checkout する。結果は `AOI_RESULTS_REF` で指定した ref を別ディレクトリへ checkout し、`.aoi-results/<cycle>/` にコピーして **データとしてだけ** 読む。結果側の Python を import したり実行したりしない。

受付が fingerprint に含めるのは、main に実在する次のコードと、実際に読む結果 JSONL だけである。

- `queryu/ask/ask.py`
- `queryu/ask/bank.py`
- `nagoyaction/inbox/inbox.py`
- `outputs/sets.jsonl`（存在する場合）
- `outputs/propositions.jsonl`（存在する場合）

`sets.jsonl` と `propositions.jsonl` の両方がない場合は、「ID がない」とは扱わず「結果が読めない」として受付を止める。

## 状態と重複防止

状態ブランチはサイクルごとに `aoi-research-state-<cycle>` を使う。受領記録、回答キャッシュ、返信再送待ちを保存する。

同じコメント ID の受領記録がすでにあれば計算し直さない。返信が失われた場合は同じ marker を使って再送し、GitHub 上ですでに bot の marker が確認できれば二重投稿しない。

受付中の 1 コメントで通常の `Exception` が起きても、そのコメントを「判定不能」として記録し、後続コメントの処理は続ける。`KeyboardInterrupt` / `SystemExit` などは飲み込まない。

## 初回の本番確認

Issue #9 に受付開始前から置かれている次の 4 コメントを、初回受付の対象にする。

1. `/ask E25 に阪神 2015 以外の判例はある？`
2. `/ask {"ask":"has_counterexample","target":"E25"}`
3. `/ask 判例がただ1つの式は？`
4. `/status`

受領記録と返信数を照合し、同じ受付を再実行しても返信が増えないことまで確認する。NPB の再取得は行わない。

## 必要な設定

- `AOI_INBOX_ISSUE`: 受付 Issue 番号
- `AOI_RESEARCH_CYCLE`: 例 `c001-chunichi`
- `AOI_RESULTS_REF`: 例 `cycle-001/chunichi`
- `AOI_INBOX_ALLOWED_ACTORS`: 任意。追加で許可する GitHub login の JSON 配列

workflow は `contents: write`（状態ブランチ）と `issues: write`（返信）を使う。

受付を止めるには `AOI_INBOX_ISSUE` を空にする。

## 後続 PR

- 探索（`/explore`、worker、停止、途中保存）
- DRAgoWing / BlueProbe の HTML フィードバック
- ローカル LLM のモデル取得、Docker 起動、`when_env` 相当の実行制御
- 1 コメントに複数コマンドをまとめる機能

これらは main の実ディレクトリ構成・既存 NagoyAction の契約に合わせて別々に導入する。
