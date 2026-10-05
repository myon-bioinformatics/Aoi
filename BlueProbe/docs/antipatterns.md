# アンチパターン集

兄弟リポジトリ（markdown / ascii_artist / xprobe）と同じ運用にする。Aoi の原則（docs/principles.md）に対応するものは出典に書く。
繰り返しそうな失敗には安定したIDを付け、可能な限り回帰テストとセットにする。

| ID | アンチパターン | なぜ困るか | このリポジトリでの約束 | 出典 |
|---|---|---|---|---|
| `REPEATED_REMOTE_VERIFICATION` | 解析を直すたびに相手サイトへ取りに行く | 検証の回数がそのまま相手への負荷になる | 取得は一度だけ（QueRyu）。以降は `observe` / `inspect` でキャッシュを再解析する | Aoi |
| `SILENT_DROP` | 読めなかったリンクを黙って捨てる | 表記が変わっても「試合が少ない年」にしか見えない | `cancelled` / `non_regular` / `unknown` を必ず数え、`unknown` は原文を残す | xprobe: Silent partial scans |
| `OVERBROAD_SCORE_REGEX` | 部分一致や `\S+` でスコアを拾う | 付記つき・2試合連結・未知の略字を誤って採用する | 全体一致、略字は12文字、得点は `[0-9]{1,2}` | ascii_artist: OVERBROAD_SANITIZER_REGEX |
| `BROADEN_BEFORE_CASE` | 新しい表記を見て、先に正規表現を広げる | 何を受け入れたかが記録に残らない | 先に `BlueProbe/tests/cases/npb_score_text.jsonl` にケースを追加する | ascii_artist: Regex rules 4 |
| `HAPPY_PATH_ONLY_TESTS` | 正常系1件だけで表記揺れを「対応済み」とする | 揺れの大半が未検証のまま残る | 採用・中止・未知の各分類に5件以上。12×12の全略字、得点の境界、DOMの入力マトリクス | ascii_artist |
| `SUBSTRING_ONLY_ASSERTION` | 「どこかに含まれる」だけを確かめる | 構造が壊れていてもテストが通る | 返ってきたレコードを丸ごと比べる | markdown |
| `SILENT_NUL` | NULを素通し、または黙って削除する | 後段の処理が予測不能になる。削除すると本来の文字列と区別できない | U+FFFDに置換し、置換後は `unknown` に落とす | markdown: NUL sanitization |
| `INFERENCE_AS_MEASUREMENT` | 1年分の確認結果を全年に当てはめて書く | 確認していない年の構造変化を見落とす | `BlueProbe/docs/npb_calendar.md` で観測と未確認を分けて記録する | xprobe |
| `SYNTHETIC_FIXTURE_AS_REAL` | 合成したHTMLを実データとして扱う | 実際のDOMとの差が隠れる | フィクスチャの出どころを明記し、生HTML取得後は実ページを追加する | markdown: DOM_FIRST_WITH_THIN_CORPUS |
| `SCORE_IN_DOCS` | 診断用に生スコアをdocsやgitに残す | 掲載情報の転載にあたる | 生データは `data/`（git管理外）。docsの未知表記は数字を `#` に伏せる | Aoi |
| `SILENT_NORMALIZATION` | 正規化した結果だけを残す | 何を変えたかが記録単位で追えない（Aoi Principle 2） | 原文 `raw_text` と派生値を並べ、`normalized` で変化の有無を残す | Aoi |
| `UNRECORDED_PROVENANCE` | いつ・どこから・どのコードで取ったかを残さない | 再現も検証もできない（Aoi Principle 6, 8） | キャッシュの manifest.jsonl に URL・日時・ステータス・SHA-256・コードの版を追記する | Aoi |
