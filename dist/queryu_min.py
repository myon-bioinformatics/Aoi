#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/QueRyu
# commit: f1a91e5c6b0a09ec5aac6a19ce1e60abde3f80d6
# entry: cache_core.py
# entry-module: cache_core
# search-paths: .
# allow: 
# allow-cycles: no
# cycles: 
# modules: cache_core
# prefix: _minpy_c7d0aa896185c8d7
# content-sha256: 85d3b9fea1b7654d6f6cc3f9bbe18a97bfead910a21fe06d3f311964c24eda31
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_c7d0aa896185c8d7"
_MINPY_ENTRY = "cache_core"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "cache_core": "\"\"\"QueRyu's offline cache/snapshot API: stdlib only, no implicit checkout or data paths.\n\nA caller may supply source_version; unknown provenance stays None.\nNo HTTP client, acquisition planner, frozen-season file or Aoi layout is required.\n\"\"\"\nfrom __future__ import annotations\n\nimport copy\nimport datetime as dt\nimport gzip\nimport hashlib\nimport json\nimport os\nimport re\nimport tempfile\nimport zlib\nfrom pathlib import Path\n\n__all__ = [\"Cache\", \"CacheIntegrityError\"]\n\n\nclass CacheIntegrityError(ValueError):\n    \"\"\"A cached body cannot be verified against its recorded acquisition.\"\"\"\n\n\nclass Cache:\n    def __init__(self, root: Path, *, source_version: str | None = None):\n        self.source_version = source_version\n        self.root = Path(root)\n        self.manifest = self.root / \"manifest.jsonl\"\n\n    def _version(self) -> str | None:\n        return self.source_version\n\n    def _now(self) -> str:\n        return dt.datetime.now(dt.UTC).isoformat(timespec=\"seconds\")\n\n    def latest(self) -> dict[str, dict]:\n        \"\"\"\u30da\u30fc\u30b8\u3054\u3068\u306e\u6700\u65b0\u306e\u6765\u6b74\u3002\u672c\u6587\u3092\u6301\u3064\u53d6\u5f97\uff08200/404\uff09\u3060\u3051\u3092\u5bfe\u8c61\u306b\u3059\u308b\u3002\"\"\"\n        out = {}\n        if self.manifest.exists():\n            for line in self.manifest.read_text(encoding=\"utf-8\").splitlines():\n                e = json.loads(line)\n                if e[\"status\"] in (200, 404):\n                    out[e[\"key\"]] = e\n        return out\n\n    def _body_path(self, file: str) -> Path:\n        \"\"\"Resolve only relative paths that stay inside this cache root.\"\"\"\n        if not isinstance(file, str) or not file or \"\\\\\" in file or \"\\x00\" in file:\n            raise CacheIntegrityError(\"cache file must be a safe relative path\")\n        relative = Path(file)\n        if relative.is_absolute() or \"..\" in relative.parts or \":\" in file:\n            raise CacheIntegrityError(\"cache file must be a safe relative path\")\n        try:\n            root = self.root.resolve()\n            path = (root / relative).resolve()\n            path.relative_to(root)\n        except (OSError, RuntimeError, ValueError) as exc:\n            raise CacheIntegrityError(\"cache file escapes the cache root or cannot be resolved\") from exc\n        if path == root:\n            raise CacheIntegrityError(\"cache file must name a body inside the cache root\")\n        # Preserve the final directory entry for no-overwrite publication: a\n        # dangling symlink must count as an existing (invalid) blob, not be repaired.\n        return root / relative\n\n    def body_bytes(self, entry: dict) -> bytes:\n        \"\"\"Verify recorded metadata against decompressed bytes before decoding.\"\"\"\n        digest = entry.get(\"sha256\")\n        size = entry.get(\"bytes\")\n        if not isinstance(digest, str) or re.fullmatch(r\"[0-9a-f]{64}\", digest) is None:\n            raise CacheIntegrityError(\"cache entry requires sha256 as 64 lowercase hexadecimal characters\")\n        if type(size) is not int or size < 0:\n            raise CacheIntegrityError(\"cache entry requires bytes as a nonnegative integer\")\n        path = self._body_path(entry.get(\"file\"))\n        try:\n            content = gzip.decompress(path.read_bytes())\n        except (OSError, EOFError, zlib.error) as exc:\n            raise CacheIntegrityError(f\"cannot read cached gzip body: {entry.get('file')!r}\") from exc\n        if len(content) != size:\n            raise CacheIntegrityError(f\"cache body bytes mismatch: recorded {size}, found {len(content)}\")\n        if hashlib.sha256(content).hexdigest() != digest:\n            raise CacheIntegrityError(\"cache body sha256 mismatch\")\n        return content\n\n    def body(self, entry: dict) -> str:\n        return self.body_bytes(entry).decode(\"utf-8\", errors=\"strict\")\n\n    def snapshot(self, entry: dict) -> dict:\n        \"\"\"Export verified evidence, without guessing missing acquisition metadata.\"\"\"\n        provenance = copy.deepcopy(entry)\n        content = self.body_bytes(provenance)\n        html = content.decode(\"utf-8\", errors=\"strict\")\n        return {\n            \"schema\": \"html-snapshot/1\", \"html\": html,\n            \"url\": provenance.get(\"url\"), \"fetched_at\": provenance.get(\"fetched_at\"),\n            \"response_sha256\": hashlib.sha256(content).hexdigest(),\n            \"content_sha256\": hashlib.sha256(html.encode(\"utf-8\")).hexdigest(),\n            \"encoding\": \"utf-8\", \"cache_entry\": provenance,\n        }\n\n    def record(self, entry: dict) -> None:\n        self.root.mkdir(parents=True, exist_ok=True)\n        with self.manifest.open(\"a\", encoding=\"utf-8\") as f:\n            f.write(json.dumps(entry, ensure_ascii=False) + \"\\n\")\n\n    def put(self, key: str, url: str, group: str, status: int, content: bytes, headers) -> dict:\n        digest = hashlib.sha256(content).hexdigest()\n        file = f\"blobs/{digest}.html.gz\"\n        self.root.mkdir(parents=True, exist_ok=True)\n        path = self._body_path(file)\n        path.parent.mkdir(parents=True, exist_ok=True)\n        # Publish a fully written gzip atomically, never replacing an existing blob.\n        # If another acquisition wins the race, verify its bytes instead of repairing it.\n        temporary = None\n        try:\n            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=\".blob-\", delete=False) as f:\n                temporary = Path(f.name)\n                f.write(gzip.compress(content, mtime=0))\n                f.flush()\n                os.fsync(f.fileno())\n            try:\n                os.link(temporary, path)\n            except FileExistsError:\n                pass\n            verified = self.body_bytes({\"file\": file, \"sha256\": digest, \"bytes\": len(content)})\n            if verified != content:\n                raise CacheIntegrityError(\"cache blob content differs despite matching hash and length\")\n        finally:\n            if temporary is not None:\n                temporary.unlink(missing_ok=True)\n        entry = {\n            \"key\": key, \"url\": url, \"group\": group, \"status\": status, \"file\": file,\n            \"sha256\": digest, \"bytes\": len(content), \"fetched_at\": self._now(),\n            \"last_modified\": headers.get(\"last-modified\"), \"etag\": headers.get(\"etag\"),\n            \"code_version\": self._version(),\n        }\n        self.record(entry)\n        return entry\n\n\n",
}
_MINPY_SKIP = (
    "__builtins__",
    "__cached__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__path__",
    "__spec__",
)


def _minpy_original(fullname):
    if fullname == _MINPY_PREFIX:
        return ""
    prefix = _MINPY_PREFIX + "."
    if fullname.startswith(prefix):
        return fullname[len(prefix):]
    return None


class _MinpyLoader:
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        original = _minpy_original(module.__name__)
        if original is None:
            raise ImportError(module.__name__)
        if original == "":
            module.__path__ = []
            return
        source = _MINPY_SOURCES[original]
        filename = "minpy://" + original + ".py"
        module.__file__ = filename
        exec(compile(source, filename, "exec"), module.__dict__)


class _MinpyFinder:
    def __init__(self):
        self._minpy_sources = _MINPY_SOURCES

    def find_spec(self, fullname, path, target=None):
        original = _minpy_original(fullname)
        if original is None:
            return None
        if original == "":
            is_package = True
        elif original not in _MINPY_SOURCES:
            return None
        else:
            is_package = original in _MINPY_PACKAGES
        return importlib.machinery.ModuleSpec(
            fullname,
            _MinpyLoader(),
            origin="minpy://" + (original or _MINPY_PREFIX),
            is_package=is_package,
        )


def _minpy_install():
    for finder in sys.meta_path:
        if getattr(finder, "_minpy_sources", None) is _MINPY_SOURCES:
            return
    sys.meta_path.insert(0, _MinpyFinder())


def _minpy_run_entry_as_main():
    import types

    original = _MINPY_ENTRY
    full = _MINPY_PREFIX + "." + original
    module = types.ModuleType("__main__")
    origin = "minpy://" + original + ".py"
    module.__file__ = globals().get("__file__") or origin
    if original in _MINPY_PACKAGES:
        module.__package__ = full
        module.__path__ = []
    elif "." in original:
        module.__package__ = full.rpartition(".")[0]
    else:
        module.__package__ = _MINPY_PREFIX
    sys.modules["__main__"] = module
    sys.modules[full] = module
    exec(compile(_MINPY_SOURCES[original], origin, "exec"), module.__dict__)


def _minpy_export_entry(namespace):
    import importlib

    module = importlib.import_module(_MINPY_PREFIX + "." + _MINPY_ENTRY)
    for key, value in module.__dict__.items():
        if key not in _MINPY_SKIP:
            namespace[key] = value


_minpy_install()
if __name__ == "__main__":
    _minpy_run_entry_as_main()
else:
    _minpy_export_entry(globals())
