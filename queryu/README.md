# QueRyu

> 再現できる取得が、確かな理解をつくる。

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
