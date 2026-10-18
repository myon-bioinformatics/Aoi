# 供給元と snapshot 記録 v1

BlueProbe は取得もキャッシュもしない。保存済みの本文を**供給元**から受け取って読む。
QueRyu（`Aoi/queryu` の `Cache`）は供給元の一つで、`QueRyuCacheSource` で包む。
実装は [`snapshot_source.py`](../../../snapshot_source.py)。

## 供給元（SnapshotSupplier）

| メソッド | 約束 |
|---|---|
| `entries()` | 既定で読む行。各 entry は少なくとも `key`, `url`, `group` を持つ |
| `body(entry)` | 照合済みの本文（str）。照合できなければ例外で止める |
| `snapshot(entry)` | 下の `html-snapshot/1` 記録 |

- 照合の失敗を**再取得で隠さない**。ネットワークに出ない
- 本文が空の entry は「空のページ」として数えられ、parser は呼ばれない

## html-snapshot/1 記録

| 項目 | 必須 | 約束 |
|---|---|---|
| `schema` | ○ | `"html-snapshot/1"` |
| `html` | ○ | 保存した本文（decode 済み） |
| `url` | ○ | 取得した URL。分からなければ `null`（推測で埋めない） |
| `encoding` | ○ | 例: `"utf-8"` |
| `fetched_at` |  | 取得時刻。分からなければ `null` |
| `response_sha256` |  | 保存した元バイト列の SHA-256 |
| `content_sha256` |  | `html` を UTF-8 にした SHA-256 |
| `cache_entry` |  | 供給元の来歴行そのもの（QueRyu では manifest の1行） |

形の検証は mcp-toolcall-lab の `source_access.extract_snapshot` と揃える。
この記録は保存バイト列の一致を示すだけで、応答の真正性や URL・時刻の真偽は保証しない。

## 入口

```python
from blueprobe import inspect_snapshots, inspect_queryu_cache
rows = inspect_snapshots(source, supplier)            # 任意の供給元
rows = inspect_queryu_cache(source, Cache(path))      # QueRyu
```

`inspect_cache` は `inspect_queryu_cache` の旧名。v1 の間は残す（DeprecationWarning を出す）。
