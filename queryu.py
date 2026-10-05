"""QueRyu — 再現できる取得が、確かな理解をつくる。

  Cache         : 生のページを gzip で保存し、取得ごとの来歴を manifest.jsonl に追記する
  PoliteFetcher : 取得元への負荷を抑えて取りに行く（キャッシュ優先・条件付きGET・間隔・直列）
  build()       : 取得元（BlueProbe の source）のページを集め、観測データセット(JSONL)を作る

来歴（manifest.jsonl の1行）:
  key, url, group, status, file, sha256, bytes, fetched_at, last_modified, etag, code_version
  304（更新なし）や 404（ページなし）も1行として残す。「確認した」こと自体が記録になる。

データセットは data/observations/<source>/<entity>.jsonl に置き、隣に .manifest.json を置く。
生のスコアを含むので data/ は git に入れない。

一度だけ取る（ユーザーの方針、2026-10-05）:
  - 生の HTML は1ページ1回だけ取り、gzip のまま保存する（Cache）。解析の規則を直すときは保存したページから作り直す（--offline）
  - 取得台帳（--ledger）: 取ったページの来歴だけ（key, url, group, status, sha256, bytes, fetched_at）を git に残す。中身は残さない
  - 台帳にある過去シーズンのページがキャッシュから消えていたら、黙って取り直さずに止まる（RefetchRefused）。
    取り直すかは人が決め、--allow-refetch（または環境変数 AOI_ALLOW_REFETCH=1）のときだけ取る。
    取り直したページの sha256 が台帳と違えば、その数を表示する（ページが後から変わったことの記録）
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

UA = "Aoi-QueRyu/0.1 (+https://github.com/myon-bioinformatics/Aoi; personal research)"


def code_version() -> str | None:
    """このコードの版（git のコミット）。測れなければ None（推測で埋めない）。"""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                             cwd=Path(__file__).resolve().parent, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


class Cache:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.manifest = self.root / "manifest.jsonl"

    def latest(self) -> dict[str, dict]:
        """ページごとの最新の来歴。本文を持つ取得（200/404）だけを対象にする。"""
        out = {}
        if self.manifest.exists():
            for line in self.manifest.read_text(encoding="utf-8").splitlines():
                e = json.loads(line)
                if e["status"] in (200, 404):
                    out[e["key"]] = e
        return out

    def body(self, entry: dict) -> str:
        return gzip.decompress((self.root / entry["file"]).read_bytes()).decode("utf-8")

    def record(self, entry: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with self.manifest.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def put(self, key: str, url: str, group: str, status: int, content: bytes, headers) -> dict:
        file = f"{key}.html.gz"
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / file).write_bytes(gzip.compress(content))
        entry = {
            "key": key, "url": url, "group": group, "status": status, "file": file,
            "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "fetched_at": now(),
            "last_modified": headers.get("last-modified"), "etag": headers.get("etag"),
            "code_version": code_version(),
        }
        self.record(entry)
        return entry


class OfflineMiss(RuntimeError):
    """オフラインモードで、キャッシュにないページを要求した。"""


class RefetchRefused(RuntimeError):
    """取得台帳にある（一度取った）ページがキャッシュになく、許可なく取り直そうとした。"""


LEDGER_FIELDS = ("key", "url", "group", "status", "sha256", "bytes", "fetched_at")


def load_ledger(path: Path | None) -> dict[str, dict]:
    if path is None or not Path(path).exists():
        return {}
    return {e["key"]: e for e in map(json.loads, Path(path).read_text(encoding="utf-8").splitlines())}


def write_ledger(path: Path, cache: Cache) -> int:
    """キャッシュにあるページの来歴（中身なし）を台帳に合わせて書く。台帳にだけある行も残す（消えたキャッシュの記録）。"""
    merged = load_ledger(path)
    for key, e in cache.latest().items():
        merged[key] = {k: e.get(k) for k in LEDGER_FIELDS}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(merged[k], ensure_ascii=False) + "\n" for k in sorted(merged)), encoding="utf-8")
    return len(merged)


class PoliteFetcher:
    def __init__(self, cache: Cache, wait: float = 3.0, *, offline: bool = False, client=None,
                 known: dict | None = None, allow_refetch: bool = False):
        self.cache, self.wait, self.offline = cache, wait, offline
        self._client = client
        self.requests = 0
        self._latest = cache.latest()
        self.known, self.allow_refetch = known or {}, allow_refetch   # 取得台帳（一度取ったページ）
        self.refetched, self.changed = [], []

    @property
    def client(self):
        if self._client is None:
            import httpx  # オフライン実行では読み込まない
            # transport= を渡すと環境変数のプロキシ設定が使われなくなるので渡さない
            self._client = httpx.Client(headers={"User-Agent": UA}, timeout=30, follow_redirects=True)
        return self._client

    def get(self, key: str, url: str, group: str, *, live: bool = False) -> str:
        cached = self._latest.get(key)
        if cached and not live:
            return self.cache.body(cached)
        if self.offline:
            if cached:
                return self.cache.body(cached)
            raise OfflineMiss(f"{key} はキャッシュにない（オフライン）")
        if not cached and not live and key in self.known:
            if not self.allow_refetch:
                raise RefetchRefused(f"{key} は取得台帳にある（{self.known[key].get('fetched_at')} に取得）のにキャッシュにない。"
                                     "取り直すかは人が決める（--allow-refetch / AOI_ALLOW_REFETCH=1）")
            self.refetched.append(key)

        headers = {}
        if cached and cached.get("last_modified"):
            headers["If-Modified-Since"] = cached["last_modified"]
        if cached and cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        if self.requests:
            time.sleep(self.wait)
        self.requests += 1
        r = self.client.get(url, headers=headers)

        if r.status_code == 304 and cached:
            self.cache.record({"key": key, "url": url, "group": group, "status": 304,
                               "fetched_at": now(), "code_version": code_version()})
            return self.cache.body(cached)
        if r.status_code not in (200, 404):
            r.raise_for_status()
        content = r.content if r.status_code == 200 else b""  # 存在しないページも「空」として覚える
        self._latest[key] = self.cache.put(key, url, group, r.status_code, content, r.headers)
        if key in self.known and self.known[key].get("sha256") != self._latest[key]["sha256"]:
            self.changed.append(key)
        return content.decode("utf-8")


def build(source, page_list, fetcher: PoliteFetcher, live_groups=()) -> dict:
    """ページを集めて BlueProbe の source で読み、group ごとの結果を返す。"""
    from blueprobe import merge, new_report

    by_group: dict[str, dict] = {}
    for key, url, group in page_list:
        html = fetcher.get(key, url, group, live=group in live_groups)
        merge(by_group.setdefault(group, new_report()), source.parse(html, url) if html else new_report())
    return by_group


def write_dataset(path: Path, records: list[dict], meta: dict, rebuilt=None) -> None:
    """記録を key でマージして書き出し、隣に manifest を置く（同じ key は新しい方を採用）。

    rebuilt(record) -> bool: 今回すべて作り直した範囲か。既存の記録のうち、この範囲にあって今回の記録にないものは
    消す（解析ルールを直したあと、前の規則で採用した記録が残らないように）。消した件数は manifest の removed に残す。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    merged, new_keys, removed = {}, {r["key"] for r in records}, 0
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if rebuilt is not None and rebuilt(r) and r["key"] not in new_keys:
                removed += 1
                continue
            merged[r["key"]] = r
    for r in records:
        merged[r["key"]] = r
    rows = sorted(merged.values(), key=lambda r: (r.get("date", ""), r["key"]))
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    body = path.read_bytes()
    meta = {**meta, "records": len(rows), "removed": removed, "sha256": hashlib.sha256(body).hexdigest(),
            "generated_at": now(), "code_version": code_version()}
    path.with_suffix(".manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _years(spec: str) -> list[int]:
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main(argv=None) -> int:
    from blueprobe import NORMALIZATION, load_source

    ap = argparse.ArgumentParser(description="取得元からページを集め、観測データセットを作る")
    ap.add_argument("--source", required=True)
    ap.add_argument("--years", required=True, help="例: 2012-2025")
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--wait", type=float, default=3.0, help="リクエスト間隔（秒）")
    ap.add_argument("--offline", action="store_true", help="キャッシュだけで作る。ネットワークに出ない")
    ap.add_argument("--ledger", type=Path, help="取得台帳（来歴だけ、中身なし。git に残す）。ここにあるページは取り直さない")
    ap.add_argument("--allow-refetch", action="store_true",
                    help="台帳にあるのにキャッシュにないページの取り直しを許す（人が決めたときだけ。AOI_ALLOW_REFETCH=1 でも同じ）")
    args = ap.parse_args(argv)

    source = load_source(args.source)
    years = _years(args.years)
    live = {str(y) for y in years if y >= dt.date.today().year}  # 進行中のシーズンだけ更新を確認
    import os

    allow = args.allow_refetch or os.environ.get("AOI_ALLOW_REFETCH") == "1"
    fetcher = PoliteFetcher(Cache(args.cache), args.wait, offline=args.offline, known=load_ledger(args.ledger), allow_refetch=allow)
    try:
        groups = build(source, source.pages(years), fetcher, live)
    finally:
        if args.ledger:   # 止まったときも、それまでに取ったページは台帳に残す
            n = write_ledger(args.ledger, fetcher.cache)
            print(f"ledger: {n} pages, refetched={len(fetcher.refetched)}, changed={len(fetcher.changed)}")

    records, counts, unknown = [], {}, 0
    for g, r in sorted(groups.items()):
        parts = [f"records={len(r['records'])}", *(f"{k}={v}" for k, v in sorted(r["counts"].items())),
                 f"unknown={len(r['unknown'])}"]
        print(f"{g}: " + " ".join(parts))
        records += r["records"]
        for k, v in r["counts"].items():
            counts[k] = counts.get(k, 0) + v
        unknown += len(r["unknown"])
    print(f"HTTP requests: {fetcher.requests}")
    if hasattr(source, "check"):
        for row in source.check(records):
            print(row["text"])

    # 指定した年はキャッシュからすべて作り直している。範囲を記録から言えない取得元なら、ファイル全体を作り直す
    scope = {str(y) for y in years}
    rebuilt = (lambda r: source.group(r) in scope) if hasattr(source, "group") else (lambda r: True)
    write_dataset(args.out, records, {
        "source": args.source, "scope": {"years": [years[0], years[-1]]},
        "normalization": NORMALIZATION, "dropped": counts, "unknown": unknown,
        "cache_manifest": str(args.cache / "manifest.jsonl"),
    }, rebuilt=rebuilt)
    return 0


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    sys.path[:0] = [str(here), str(here.parent / "blueprobe")]
    raise SystemExit(main())
