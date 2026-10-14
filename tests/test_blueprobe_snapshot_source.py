import warnings

from blueprobe import inspect_cache, inspect_queryu_cache, inspect_snapshots, new_report
from snapshot_source import SNAPSHOT_SCHEMA, QueRyuCacheSource, SnapshotSupplier


class MemorySupplier:
    """QueRyu 以外の供給元の最小例。契約だけ満たせば inspect_snapshots で読める。"""

    def __init__(self, pages):
        self.pages = pages

    def entries(self):
        return [{"key": k, "url": u, "group": g} for k, u, g, _ in self.pages]

    def _html(self, entry):
        return next(h for k, _, _, h in self.pages if k == entry["key"])

    def body(self, entry):
        return self._html(entry)

    def snapshot(self, entry):
        return {"schema": SNAPSHOT_SCHEMA, "html": self._html(entry), "url": entry["url"],
                "fetched_at": None, "response_sha256": None, "content_sha256": None,
                "encoding": "utf-8", "cache_entry": None}


class Html:
    def parse(self, html, url):
        r = new_report()
        r["records"].append({"key": url, "raw": html})
        return r


class Snap:
    def parse_snapshot(self, snapshot):
        r = new_report()
        r["records"].append({"key": snapshot["url"], "schema": snapshot["schema"]})
        return r


PAGES = [("a", "u:a", "g1", "<p>a</p>"), ("b", "u:b", "g1", ""), ("c", "u:c", "g2", "<p>c</p>")]


def test_generic_supplier_body_and_snapshot():
    supplier = MemorySupplier(PAGES)
    assert isinstance(supplier, SnapshotSupplier)
    rows = inspect_snapshots(Html(), supplier)
    assert [(r["group"], r["pages"], r["empty_pages"]) for r in rows] == [("g1", 1, 1), ("g2", 1, 0)]
    out = []
    inspect_snapshots(Snap(), supplier, records_out=out)
    assert [r["schema"] for r in out] == [SNAPSHOT_SCHEMA] * 2


class FakeCache:
    def latest(self):
        return {k: {"key": k, "url": u, "group": g} for k, u, g, _ in PAGES}

    def body(self, entry):
        return MemorySupplier(PAGES).body(entry)

    def snapshot(self, entry):
        return MemorySupplier(PAGES).snapshot(entry)


def test_queryu_adapter_and_deprecated_alias_agree():
    assert isinstance(QueRyuCacheSource(FakeCache()), SnapshotSupplier)
    new = inspect_queryu_cache(Html(), FakeCache())
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        old = inspect_cache(Html(), FakeCache())
    assert old == new
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
