"""保存済みページの供給元（snapshot supplier）の契約と、QueRyu 用アダプタ。

BlueProbe は取得もキャッシュもしない。保存済みの本文を「供給元」から受け取り、
読むだけにする。QueRyu はその供給元の一つ。契約は docs/contract/v1/snapshot.md。

供給元（SnapshotSupplier）が持つもの:
  entries()        -> [entry]  既定で読む行。各 entry は少なくとも key / url / group を持つ
  body(entry)      -> str      照合済みの本文（HTML）。照合できなければ例外で止める
  snapshot(entry)  -> dict     html-snapshot/1 の記録（下の SNAPSHOT_FIELDS）

供給元は再取得で失敗を隠してはならない。ネットワークにも出ない。
"""
from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

SNAPSHOT_SCHEMA = "html-snapshot/1"
# 必須: schema, html, url, encoding。任意だが値を推測で埋めない: fetched_at, response_sha256, content_sha256, cache_entry
SNAPSHOT_FIELDS = ("schema", "html", "url", "fetched_at", "response_sha256",
                   "content_sha256", "encoding", "cache_entry")
ENTRY_FIELDS = ("key", "url", "group")


@runtime_checkable
class SnapshotSupplier(Protocol):
    def entries(self) -> Iterable[dict]: ...
    def body(self, entry: dict) -> str: ...
    def snapshot(self, entry: dict) -> dict: ...


class QueRyuCacheSource:
    """QueRyu の `Cache`（Aoi/queryu）を供給元として包む。

    既定の entries() は key ごとの最新行（key の昇順）。照合は Cache 側が行う
    （sha256 と bytes の照合、失敗は CacheIntegrityError）。
    """

    def __init__(self, cache):
        self.cache = cache

    def entries(self) -> list[dict]:
        return [entry for _, entry in sorted(self.cache.latest().items())]

    def body(self, entry: dict) -> str:
        return self.cache.body(entry)

    def snapshot(self, entry: dict) -> dict:
        return self.cache.snapshot(entry)
