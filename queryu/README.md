# QueRyu

> 再現できる取得が、確かな理解をつくる。

![QueRyu](../docs/images/queryu.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

取得と、観測データセットの作成を担う。取得元への負荷を抑え、いつ・どこから・どのコードで取ったかを必ず残す。

## 取得元への配慮

- 取得済みのページは再取得しない。進行中の期間（例: 今年のシーズン）だけ、条件付きGET（`If-Modified-Since` / `If-None-Match`）で更新を確認する
- 存在しないページ（404）も「空」として記録し、二度と問い合わせない
- 直列で、既定3秒の間隔を空ける。5xx は保存しない
- `--offline` ではネットワークに一切出ない（キャッシュにないページは止まる）

## 来歴

キャッシュの `manifest.jsonl` に、取得ごとに1行を追記する。304（更新なし）も「確認した」記録として残す。

```text
key, url, group, status, file, sha256, bytes, fetched_at, last_modified, etag, code_version
```

`code_version` は git のコミット。測れなければ `null` のまま（推測で埋めない）。

## データセット

`data/observations/<source>/<entity>.jsonl`（1記録1行、`key` で一意）と、隣の `.manifest.json`（取得元・範囲・正規化の内容・採用しなかった件数・未知の件数・SHA-256・コードの版）。
生の観測を含むので `data/` は git に入れない。

```bash
uv run python queryu/queryu.py --source npb_calendar --years 2012-2025 \
  --cache data/raw/npb_calendar --out data/observations/npb_calendar/games.jsonl [--offline]
```


## 保存本文の照合と履歴

新しい `Cache.put()` は本文を `blobs/<sha256>.html.gz` に保存する。同じ本文は
共有するが、取得ごとの manifest 行（URL・時刻・ETag など）は毎回残す。
一時ファイルの完成後に既存ファイルを上書きしない形で公開し、その後に来歴を追記する。
同じ key を更新しても、以前の行が指す本文は残る。key はファイル名に使わない。
既存 blob が壊れている場合は再保存で修復せず、エラーで止める。
自動削除・保持期限・既存キャッシュの一括移行は実装していない。
中断で来歴のない blob が残る場合も、勝手に削除しない。

`Cache.body_bytes(entry)` は gzip 展開後の**保存した元バイト列**を、来歴に既にある
`sha256` と `bytes` の両方に照合する。`Cache.body(entry)` はその後で UTF-8 を
厳密に decode する。照合失敗を再取得で隠さず、ネットワークへ取りに行かない。
絶対パス・親ディレクトリ参照・キャッシュ外への symlink は拒否する。
ファイルと来歴を同時に書き換えられる攻撃者に対する署名・真正性の保証ではない。

旧形式の `<key>.html.gz` と manifest は変更しない。保存済みの hash と長さがあり、
現在の本文と一致する行はそのまま読める。hash/長さがない・不正な行は明示的に拒否する。
読み込み時に新しい hash を作って「検証済み」に昇格させない。旧方式で既に上書きされた
過去の本文は復元できず、対応する古い行は照合失敗になる場合がある。
新方式導入後の保存でも旧ファイルを上書きしない。履歴を使うときは、その取得の
manifest 行を選んで `body()` または `snapshot()` に渡す。

`Cache.snapshot(entry)` は元バイト列の照合後に `html-snapshot/1` へ変換する。
`response_sha256` は保存した元バイト列、`content_sha256` は decode 済みHTMLを
UTF-8 にした値の hash。現行の厳密な UTF-8 保存では一致するが、意味は別々に扱う。
元の `url`・`fetched_at` を引き継ぎ、取得時刻が不明なら `null` のままにする。
独自項目を含む元の行全体は `cache_entry` に保存し、補完した来歴と混同しない。
これだけでは URL・取得時刻の真実性や HTTP 応答の真正性は証明しない。

責務は、取得・保存本文・照合・履歴が QueRyu、保存データの観測・結果検証と
共有抽出への接続が BlueProbe、実行元やソースの identity 確認・CI runner・証跡の
実行管理が NagoyAction。この変更では新しい runner や実行証明を追加しない。
