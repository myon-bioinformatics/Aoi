# NagoyAction の質問・探索受付

専用Issueの通常コメントで、人・AIエージェントのどちらからでも受け付ける。
受付Issueはリポジトリ変数 `AOI_INBOX_ISSUE` で指定する。

| コメント | 動作 |
|---|---|
| `/ask E25 に阪神 2015 以外の判例はある？` | 保存済みの結果から回答 |
| `/ask {"ask":"has_counterexample","target":"E25"}` | 型を指定して回答。AIエージェントにも同じ入口 |
| `/explore E25` | E25の前件に使われている集合で、Bクラスへの式を探索 |
| `/explore {"sets":["OFF_SHORT","DEF_WORSE"],"max_depth":2}` | 登録済み集合を指定して探索 |
| `/explore all` | 登録済み全集合を候補とする |
| `/status` | 受付件数と直近10 jobの進捗 |
| `/stop 123456789` | 依頼のコメントIDで停止 |

通常の会話には反応しない。1コメントに1コマンド、4000文字まで。
コメント編集は再実行しない。修正した依頼は新しいコメントで投稿する。
質問文の未対応条件・不明なID・不足した結果を「反例なし」にしない。
成立率と除外後の反例一覧は別の値で、`exclude` によって成立率を再計算しない。

## 起動と保存

実行管理はNagoyAction、問い合わせの型と読み取りはQueRyu、式の探索と判定はPythDRagorasが担当する。
ActionsのYAMLは既存の `nagoyaction.py run` を呼ぶ。Dockerの起動・待機・終了も
`NagoyAction/pipelines/inbox.toml` に記載し、Compose設定は `NagoyAction/containers/llama.compose.yml` に置く。
ローカルでも同じ定義を使い、実行した手順は `--receipt` に記録する。

- `research-inbox.yml`: コメント投稿時、および15分間隔で受付を読む。
  `GITHUB_TOKEN` で別のActionsが投稿したコメントも、定期読取りで拾う。
- `research-worker.yml`: 15分間隔で保存された探索依頼を読む。探索は同時に1ジョブ。
  質問受付は別のconcurrency groupで動くので、探索終了を待たない。
- 両方とも既定ブランチのコードをcheckoutする。PRのコードをコメントから実行しない。
- 初回受付時に `aoi-research-state` を空の履歴から作る。そこに依頼・回答・途中結果を保存する。
  取得元へアクセスせず、既存の `season.jsonl` と命題・集合定義だけで計算する。
- 1回のworkerは5時間で新しい処理を止める。workflowは330分で打ち切る。
  30秒または100候補を目安に小分けし、各区切りでgitへ保存する。
  単一候補の処理中は中断しないので、5時間は開始を止める期限。
  候補・結果は100件ずつのファイルへ分割し、1つの巨大な状態ファイルを作らない。
- 次回はcursorから再開。同じ計画・入力指紋は同じjobにまとめる。
  質問の回答も、問い合わせ型・結果ファイル・回答コードの指紋で再利用する。
- 依頼追加と結果保存が重なった場合は、状態ブランチの新しいコミットをrebaseしてからpushする。
  pushに失敗したチェックポイントはActions artifactにも残す。
- 停止は依頼者か管理側が行う。同じjobを別の人も依頼していたら、そちらは継続する。
  停止コメントは受付処理後、workerの次の区切りで反映する。

GitHubの定期実行は遅延・停止することがあるため、常駐サービスの即時性は保証しない。
手動のworkflow dispatchでも再開できる。Botの回答は返信マーカー付きで、再度依頼として読まれない。

## 探索の範囲

既存の `PythDRagoras/logic/sets.py` と `propositions.py` を使用する。
元・逆・裏・対偶、反例、判定不能、焦点球団の覆いを残す。
反例のある式には登録済み集合を `&` で足し、覆えない単位がある式には `|` で道筋を足す。
集合の否定も使う。境界値・新しい列・実行コードは生成しない。

最初に集合名・深さ・候補数上限・入力指紋を保存してから計算する。
既定深さ3（seedを1と数える）、最大5万候補で、上限に達した場合は `bounded` と表示する。
この探索規則で生成する候補を調べるもので、任意の論理式すべての全探索ではない。
未対応の自然文テーマは勝手に全集合へ置き換えず、集合名・式IDの指定を求める。

候補は独立した `X...` IDを持ち、親ときっかけになった単位を記録する。
親の反例・覆えなかった単位は `motivated_by` に累積し、それらを除いた評価も残す。
探索結果を既存の `propositions.toml` / `sets.toml` に自動採用しない。
同じデータから選んだ候補なので、独立データで確認済みとはしない。

入力データ・設定・判定コードの指紋が依頼時と異なる場合は `blocked` とする。
旧データの途中結果を新データと混ぜず、新しいコメントで依頼し直す。

## 導入

1. この実装と、依存するQueRyu/PythDRagorasの変更を既定ブランチへ統合する。
2. 受付専用のIssueを作り、リポジトリ変数 `AOI_INBOX_ISSUE` にその番号を設定する。
3. `Aoi question inbox` を手動実行し、状態ブランチ作成と質問への返信を確認する。
4. `/explore E25` を投稿し、`Aoi bounded research worker` を実行する。

`contents: write` は状態ブランチ、`issues: write` は回答用。
変数が未設定なら両workflowとも処理しない。mainへの統合前はコメント受付も定期実行も稼働しない。

## ローカルLLM

`inbox.py` は `AOI_USE_LOCAL_LLM=1` のとき、規則で読めない `/ask` を
`http://127.0.0.1:8080/v1/chat/completions` のllama.cppへ渡せる。
JSON SchemaでQueryと未対応条件を返させ、Python側でも型を検証する。
この設定は質問の読み取りだけに使い、計算と回答の根拠は保存済み結果のまま。
モデルの解釈は完全ではないため、返信には読み取ったQueryも表示する。

既定のActions受付はモデルなし。リポジトリ変数 `AOI_USE_LOCAL_LLM=1` と以下を設定すると、
NagoyActionが同じrunnerでモデル確認・Docker起動・起動待ち・受付・終了を順に実行する。

- `AOI_LLAMA_IMAGE`: 公式 `ghcr.io/ggml-org/llama.cpp:server@sha256:...`（digest固定）
- `AOI_LLAMA_MODEL_URL`: 小型GGUFモデルのHTTPS URL
- `AOI_LLAMA_MODEL_SHA256`: そのモデルのSHA-256

モデルは `.models/model.gguf` に置き、既存ファイルのSHAが一致すれば再取得しない。
イメージdigestとモデルSHAは `.models/identity.json` に記録する。
`when_env` はその環境変数が1のときだけ手順を実行し、`always` の終了手順は先行手順が失敗しても実行する。
Docker Compose自体の機能を使い、別のコンテナ実行エンジンは作らない。
外部LLMのAPIキーは不要。LLMを起動しない場合も、対応する日本語と型付きJSONで利用できる。

## 検証

`uv run --frozen pytest QueRyu/tests/test_ask.py NagoyAction/tests/test_inbox.py PythDRagoras/tests/test_sets.py -q`

架空データによる実評価の中断・再開一致、候補数制限、未知条件、不完全な反例一覧、
人/Botの受付、返信の重複防止、実Gitでの並行保存を確かめる。
