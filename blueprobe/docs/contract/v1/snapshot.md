# Suppliers and snapshot records v1

BlueProbe neither fetches nor caches. It receives saved bodies from a **supplier** and reads them.
QueRyu (the `Cache` in `Aoi/queryu`) is one supplier, wrapped by `QueRyuCacheSource`.
The implementation is [`snapshot_source.py`](../../../snapshot_source.py).

## Supplier (SnapshotSupplier)

| Method | Promise |
|---|---|
| `entries()` | Rows read by default. Each entry has at least `key`, `url`, `group` |
| `body(entry)` | The verified body (str). If it can't be verified, stop with an exception |
| `snapshot(entry)` | The `html-snapshot/1` record below |

- Verification failures are **not hidden by refetching**. No network access
- Entries with an empty body are counted as "empty pages", and the parser isn't called

## html-snapshot/1 record

| Item | Required | Promise |
|---|---|---|
| `schema` | ○ | `"html-snapshot/1"` |
| `html` | ○ | The saved body (decoded) |
| `url` | ○ | The fetched URL. `null` if unknown (not filled in by guessing) |
| `encoding` | ○ | e.g. `"utf-8"` |
| `fetched_at` |  | Fetch time. `null` if unknown |
| `response_sha256` |  | SHA-256 of the saved original bytes |
| `content_sha256` |  | SHA-256 of `html` as UTF-8 |
| `cache_entry` |  | The supplier's provenance row itself (one manifest line in QueRyu) |

Shape validation matches mcp-toolcall-lab's `source_access.extract_snapshot`.
This record only shows that the saved bytes match; it doesn't guarantee the authenticity of the response or the truth of the URL or time.

## Entry points

```python
from blueprobe import inspect_snapshots, inspect_queryu_cache
rows = inspect_snapshots(source, supplier)            # any supplier
rows = inspect_queryu_cache(source, Cache(path))      # QueRyu
```

`inspect_cache` is the old name of `inspect_queryu_cache`. It stays during v1 (emitting a DeprecationWarning).
