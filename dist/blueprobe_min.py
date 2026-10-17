#!/usr/bin/env python3
# minpy-bundle/1
# tool: minpy/0.1.0
# python: 3.12
# repository: myon-bioinformatics/Aoi
# commit: 2bf96800b682c9b58b438e1d274267e3fcf832a3
# entry: blueprobe/blueprobe.py
# entry-module: blueprobe
# search-paths: blueprobe
# allow: 
# allow-cycles: no
# cycles: 
# modules: blueprobe,snapshot_source
# prefix: _minpy_85570bbfb8db89e7
# content-sha256: f30a4ecd4a98d26d2accbd108cb0ff28757a6f8e078b0209da806f6ae4927c09
# content-sha256-rule: sha256-utf8-with-content-sha256-hex-replaced-by-64-zeros

import importlib.machinery
import sys

_MINPY_PREFIX = "_minpy_85570bbfb8db89e7"
_MINPY_ENTRY = "blueprobe"
_MINPY_PACKAGES = ()
_MINPY_SOURCES = {
    "blueprobe": "\"\"\"BlueProbe \u2014 \u89b3\u6e2c\u3059\u308b\u3002\u89e3\u91c8\u306f\u3042\u3068\u3067\u3002\n\n\u53d6\u5f97\u5143\uff08source\uff09\u306b\u4f9d\u5b58\u3057\u306a\u3044\u90e8\u5206\u3060\u3051\u3092\u7f6e\u304f\u3002\n  - normalize(): \u8868\u8a18\u63fa\u308c\u306e\u5438\u53ce\u3002\u4f55\u3092\u3057\u305f\u304b\u306f\u8a18\u9332\u5358\u4f4d\u3067\u6b8b\u3059\n  - Report: 1\u30da\u30fc\u30b8\u3092\u8aad\u3093\u3060\u7d50\u679c\u306e\u5951\u7d04\u3002\u63a1\u7528\u3057\u305f\u3082\u306e\u4ee5\u5916\u3082\u5fc5\u305a\u6570\u3048\u308b\n  - inspect(): \u53d6\u5f97\u6e08\u307f\u306e\u30da\u30fc\u30b8\u3092\u518d\u89e3\u6790\u3057\u3066\u96c6\u8a08\u3059\u308b\u3002\u30cd\u30c3\u30c8\u30ef\u30fc\u30af\u306b\u306f\u51fa\u306a\u3044\n\n\u53d6\u5f97\u5143\u3054\u3068\u306e\u8aad\u307f\u65b9\u306f\u5225\u30e2\u30b8\u30e5\u30fc\u30eb\uff08\u4f8b: npb_calendar.py\uff09\u306b\u7f6e\u304d\u3001\u6b21\u306e2\u3064\u3092\u6301\u305f\u305b\u308b:\n  pages(scope)        -> [(key, url, group)]   \u53d6\u5f97\u3059\u3079\u304d\u30da\u30fc\u30b8\u306e\u4e00\u89a7\n  parse(html, url)    -> Report               1\u30da\u30fc\u30b8\u306e\u89b3\u6e2c\u7d50\u679c\n\nAoi \u306e\u539f\u5247\u3068\u306e\u5bfe\u5fdc:\n  Observe Before Explaining  \u2026 \u539f\u6587(raw)\u3068\u8aad\u307f\u53d6\u3063\u305f\u5024(derived)\u3092\u540c\u3058\u8a18\u9332\u306b\u4e26\u3079\u308b\n  Never Hide Unknowns        \u2026 unknown \u306f\u4ef6\u6570\u3068\u539f\u6587\u3092\u6b8b\u3059\n  Separate Facts From Explanations \u2026 \u3053\u3053\u3067\u306f\u52dd\u6557\u3082\u70b9\u5dee\u3082\u8a08\u7b97\u3057\u306a\u3044\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport importlib\nimport re\nimport sys\nimport unicodedata\nfrom collections import Counter\nfrom collections.abc import Iterable\nfrom pathlib import Path\n\nNORMALIZATION = \"nul->U+FFFD, NFKC, collapse-whitespace\"\n\n\ndef normalize(text: str) -> str:\n    \"\"\"NUL \u306f U+FFFD \u306b\u7f6e\u304d\u63db\u3048\uff08\u9ed9\u3063\u3066\u6d88\u3055\u306a\u3044\uff09\u3001NFKC\u3001\u9023\u7d9a\u7a7a\u767d\u30921\u3064\u306b\u3002\"\"\"\n    text = unicodedata.normalize(\"NFKC\", text.replace(\"\\x00\", \"\ufffd\"))\n    return \" \".join(text.split())\n\n\ndef new_report() -> dict:\n    \"\"\"1\u30da\u30fc\u30b8\uff08\u307e\u305f\u306f\u8907\u6570\u30da\u30fc\u30b8\u306e\u5408\u8a08\uff09\u306e\u89b3\u6e2c\u7d50\u679c\u3002\n\n    records : \u63a1\u7528\u3057\u305f\u89b3\u6e2c\u3002key \u3067\u4e00\u610f\n    counts  : \u63a1\u7528\u3057\u306a\u304b\u3063\u305f\u3082\u306e\u306e\u533a\u5206\u3054\u3068\u306e\u4ef6\u6570\uff08\u4f8b: cancelled, non_regular\uff09\n    unknown : \u3069\u306e\u533a\u5206\u306b\u3082\u5f53\u305f\u3089\u306a\u304b\u3063\u305f\u3082\u306e\u3002\u539f\u6587\u3092\u6b8b\u3059\n    \"\"\"\n    return {\"records\": [], \"counts\": Counter(), \"unknown\": []}\n\n\ndef merge(total: dict, part: dict, key: str = \"key\") -> dict:\n    \"\"\"\u7d50\u679c\u3092\u8db3\u3057\u5408\u308f\u305b\u308b\u3002\u540c\u3058 key \u306e\u8a18\u9332\u306f\u6700\u521d\u306e\u3082\u306e\u3092\u6b8b\u3059\u3002\"\"\"\n    seen = {r[key] for r in total[\"records\"]}\n    total[\"records\"] += [r for r in part[\"records\"] if r[key] not in seen]\n    total[\"counts\"].update(part[\"counts\"])\n    total[\"unknown\"] += part[\"unknown\"]\n    return total\n\n\ndef load_source(name: str):\n    \"\"\"\u53d6\u5f97\u5143\u30e2\u30b8\u30e5\u30fc\u30eb\u3092\u540d\u524d\u3067\u8aad\u307f\u8fbc\u3080\uff08blueprobe/ \u76f4\u4e0b\u306e <name>.py\uff09\u3002\"\"\"\n    if not re.fullmatch(r\"[a-z][a-z0-9_]*\", name):\n        raise ValueError(f\"invalid source name: {name!r}\")\n    return importlib.import_module(name)\n\n\ndef mask_digits(text: str) -> str:\n    \"\"\"docs \u306b\u672a\u77e5\u8868\u8a18\u306e\u300c\u5f62\u300d\u3060\u3051\u6b8b\u3059\u305f\u3081\u3001\u6570\u5b57\u3092 # \u306b\u4f0f\u305b\u308b\u3002\"\"\"\n    return re.sub(r\"[0-9\uff10-\uff19]\", \"#\", text)\n\n\ndef inspect(source, pages: Iterable[tuple[str, str, str, str]], records_out: list | None = None) -> list[dict]:\n    \"\"\"\u53d6\u5f97\u6e08\u307f\u30da\u30fc\u30b8 (key, url, group, html) \u3092\u518d\u89e3\u6790\u3057\u3001group \u3054\u3068\u306b\u96c6\u8a08\u3059\u308b\u3002\n\n    \u30cd\u30c3\u30c8\u30ef\u30fc\u30af\u306b\u306f\u51fa\u306a\u3044\u3002\u89e3\u6790\u30eb\u30fc\u30eb\u3092\u76f4\u3057\u305f\u3089\u3001\u3053\u308c\u3060\u3051\u3092\u4f55\u5ea6\u3067\u3082\u56de\u3059\u3002\n    \"\"\"\n    return _inspect(source.parse, pages, records_out)\n\n\ndef inspect_snapshots(source, supplier, entries=None, records_out=None) -> list[dict]:\n    \"\"\"\u4f9b\u7d66\u5143\uff08snapshot_source.SnapshotSupplier\uff09\u306e\u4fdd\u5b58\u6e08\u307f\u672c\u6587\u3092\u3001\u30aa\u30d5\u30e9\u30a4\u30f3\u3067\u518d\u89e3\u6790\u3059\u308b\u3002\n\n    entries \u3092\u7701\u304f\u3068 supplier.entries()\uff08\u65e2\u5b9a\u306e\u884c\uff09\u3092\u8aad\u3080\u3002\u6307\u5b9a\u3059\u308c\u3070\u3001\u305d\u306e\u53d6\u5f97\u6642\u70b9\u306e\u884c\u3092\u8aad\u3080\u3002\n    parse_snapshot \u3092\u6301\u3064 source \u306b\u306f html-snapshot/1 \u306e\u8a18\u9332\u3092\u3001\u305d\u308c\u4ee5\u5916\u306b\u306f\u672c\u6587\u3092\u6e21\u3059\u3002\n    \u7167\u5408\u306e\u5931\u6557\u306f parser \u3092\u547c\u3076\u524d\u306b\u6b62\u307e\u308a\u3001\u518d\u53d6\u5f97\u3067\u7f6e\u304d\u63db\u3048\u306a\u3044\u3002\n    \"\"\"\n    snapshot_parser = getattr(source, 'parse_snapshot', None)\n    if entries is None:\n        entries = list(supplier.entries())\n\n    def pages():\n        for entry in entries:\n            if snapshot_parser is not None:\n                snapshot = supplier.snapshot(entry)\n                payload = snapshot if snapshot['html'] else ''\n            else:\n                payload = supplier.body(entry)\n            yield entry['key'], entry['url'], entry['group'], payload\n\n    parser = (lambda snapshot, url: snapshot_parser(snapshot)) if snapshot_parser is not None else source.parse\n    return _inspect(parser, pages(), records_out)\n\n\ndef inspect_queryu_cache(source, cache, entries=None, records_out=None) -> list[dict]:\n    \"\"\"QueRyu \u306e Cache \u3092\u4f9b\u7d66\u5143\u3068\u3057\u3066\u518d\u89e3\u6790\u3059\u308b\uff08QueRyuCacheSource \u7d4c\u7531\uff09\u3002\"\"\"\n    from _minpy_85570bbfb8db89e7.snapshot_source import QueRyuCacheSource\n    return inspect_snapshots(source, QueRyuCacheSource(cache), entries, records_out)\n\n\ndef inspect_cache(source, cache, entries=None, records_out=None) -> list[dict]:\n    \"\"\"\u975e\u63a8\u5968: inspect_queryu_cache \u306e\u65e7\u540d\u3002Aoi/QueRyu \u5074\u306e\u4e92\u63db\u306e\u305f\u3081\u306b\u6b8b\u3059\uff08\u5951\u7d04 v1 \u306e\u9593\u306f\u524a\u9664\u3057\u306a\u3044\uff09\u3002\"\"\"\n    import warnings\n    warnings.warn(\"inspect_cache is deprecated; use inspect_queryu_cache\", DeprecationWarning, stacklevel=2)\n    return inspect_queryu_cache(source, cache, entries, records_out)\n\n\ndef _inspect(parser, pages, records_out):\n    groups: dict[str, dict] = {}\n    for key, url, group, html in pages:\n        g = groups.setdefault(group, {\"pages\": 0, \"empty\": 0, \"report\": new_report()})\n        if not html:\n            g[\"empty\"] += 1\n            continue\n        g[\"pages\"] += 1\n        merge(g[\"report\"], parser(html, url))\n    rows = []\n    for group, g in sorted(groups.items()):\n        r = g[\"report\"]\n        if records_out is not None:\n            records_out += r[\"records\"]\n        rows.append({\n            \"group\": group, \"pages\": g[\"pages\"], \"empty_pages\": g[\"empty\"],\n            \"records\": len(r[\"records\"]), **{f\"n_{k}\": v for k, v in sorted(r[\"counts\"].items())},\n            \"unknown\": len(r[\"unknown\"]),\n            \"unknown_shapes\": sorted({mask_digits(u[\"raw\"]) for u in r[\"unknown\"]})[:5],\n        })\n    return rows\n\n\ndef to_markdown(rows: list[dict], title: str, checks: list[dict] | None = None) -> str:\n    \"\"\"checks \u306f source.check() \u306e\u8fd4\u308a\u5024\uff08{\"group\", \"ok\", \"text\"} \u306e\u4e26\u3073\uff09\u3002\"\"\"\n    cols = sorted({k for r in rows for k in r if k != \"unknown_shapes\"}, key=lambda k: (k != \"group\", k))\n    lines = [f\"# {title}\", \"\", \"\u53d6\u5f97\u6e08\u307f\u30da\u30fc\u30b8\u306e\u518d\u89e3\u6790\u7d50\u679c\uff08\u81ea\u52d5\u751f\u6210\uff09\u3002\u30cd\u30c3\u30c8\u30ef\u30fc\u30af\u306b\u306f\u51fa\u3066\u3044\u306a\u3044\u3002\", \"\",\n             \"| \" + \" | \".join(cols) + \" |\", \"|\" + \"---|\" * len(cols)]\n    lines += [\"| \" + \" | \".join(str(r.get(c, 0)) for c in cols) + \" |\" for r in rows]\n    if checks:\n        lines += [\"\", \"## \u53d6\u308a\u3053\u307c\u3057\u306e\u78ba\u8a8d\uff08\u65e2\u77e5\u5024\u3068\u306e\u7167\u5408\uff09\", \"\", *[f\"- {c['text']}\" for c in checks]]\n    shapes = [(r[\"group\"], r[\"unknown_shapes\"]) for r in rows if r[\"unknown_shapes\"]]\n    if shapes:\n        lines += [\"\", \"## \u672a\u77e5\u306e\u8868\u8a18\uff08\u6570\u5b57\u306f # \u306b\u4f0f\u305b\u305f\u5f62\uff09\", \"\"]\n        lines += [f\"- {g}: \" + \", \".join(f\"`{s!r}`\" for s in ss) for g, ss in shapes]\n    return \"\\n\".join(lines) + \"\\n\"\n\n\ndef main(argv=None) -> int:\n    ap = argparse.ArgumentParser(description=\"\u53d6\u5f97\u6e08\u307f\u30da\u30fc\u30b8\u3092\u30aa\u30d5\u30e9\u30a4\u30f3\u3067\u518d\u89e3\u6790\u3059\u308b\")\n    ap.add_argument(\"--source\", required=True)\n    ap.add_argument(\"--cache\", type=Path, required=True, help=\"QueRyu \u306e\u30ad\u30e3\u30c3\u30b7\u30e5\u30c7\u30a3\u30ec\u30af\u30c8\u30ea\")\n    ap.add_argument(\"--out\", type=Path, help=\"Markdown \u306e\u51fa\u529b\u5148\")\n    ap.add_argument(\"--strict\", action=\"store_true\", help=\"\u672a\u77e5\u306e\u8868\u8a18\u3001\u307e\u305f\u306f\u65e2\u77e5\u5024\u3068\u5408\u308f\u306a\u3044 group \u304c\u3042\u308c\u3070\u7d42\u4e86\u30b3\u30fc\u30c91\")\n    args = ap.parse_args(argv)\n\n    source = load_source(args.source)\n    manifest = args.cache / \"manifest.jsonl\"\n    if not manifest.exists():\n        print(f\"no cache manifest: {manifest}\", file=sys.stderr)\n        return 1\n    raise ImportError(\"queryu is not included in the stdlib minpy bundle. Use the original blueprobe.py with the companion tool.\")\n    records: list = []\n    rows = inspect_queryu_cache(source, Cache(args.cache), records_out=records)\n    checks = source.check(records) if hasattr(source, \"check\") else None\n    md = to_markdown(rows, f\"{args.source}: \u89b3\u6e2c\u3055\u308c\u305f\u69cb\u9020\", checks)\n    if args.out:\n        args.out.parent.mkdir(parents=True, exist_ok=True)\n        args.out.write_text(md, encoding=\"utf-8\")\n    print(md)\n    n_unknown = sum(r[\"unknown\"] for r in rows)\n    if n_unknown:\n        print(f\"unknown: {n_unknown} \u4ef6\u3002\u8868\u8a18\u306e\u5909\u5316\u3092\u7591\u3046\uff08\u4e0a\u306e\u8868\u3092\u53c2\u7167\uff09\", file=sys.stderr)\n    failed = [c[\"group\"] for c in checks or [] if not c[\"ok\"]]\n    if failed:\n        print(f\"\u65e2\u77e5\u5024\u3068\u5408\u308f\u306a\u3044 group: {', '.join(failed)}\uff08\u53d6\u308a\u3053\u307c\u3057\u30fb\u6df7\u5165\u3092\u7591\u3046\uff09\", file=sys.stderr)\n    return 1 if (args.strict and (n_unknown or failed)) else 0\n\n\nif __name__ == \"__main__\":\n    sys.path[:0] = [str(Path(__file__).resolve().parent),\n                    str(Path(__file__).resolve().parents[1] / \"queryu\")]\n    raise SystemExit(main())\n",
    "snapshot_source": "\"\"\"\u4fdd\u5b58\u6e08\u307f\u30da\u30fc\u30b8\u306e\u4f9b\u7d66\u5143\uff08snapshot supplier\uff09\u306e\u5951\u7d04\u3068\u3001QueRyu \u7528\u30a2\u30c0\u30d7\u30bf\u3002\n\nBlueProbe \u306f\u53d6\u5f97\u3082\u30ad\u30e3\u30c3\u30b7\u30e5\u3082\u3057\u306a\u3044\u3002\u4fdd\u5b58\u6e08\u307f\u306e\u672c\u6587\u3092\u300c\u4f9b\u7d66\u5143\u300d\u304b\u3089\u53d7\u3051\u53d6\u308a\u3001\n\u8aad\u3080\u3060\u3051\u306b\u3059\u308b\u3002QueRyu \u306f\u305d\u306e\u4f9b\u7d66\u5143\u306e\u4e00\u3064\u3002\u5951\u7d04\u306f docs/contract/v1/snapshot.md\u3002\n\n\u4f9b\u7d66\u5143\uff08SnapshotSupplier\uff09\u304c\u6301\u3064\u3082\u306e:\n  entries()        -> [entry]  \u65e2\u5b9a\u3067\u8aad\u3080\u884c\u3002\u5404 entry \u306f\u5c11\u306a\u304f\u3068\u3082 key / url / group \u3092\u6301\u3064\n  body(entry)      -> str      \u7167\u5408\u6e08\u307f\u306e\u672c\u6587\uff08HTML\uff09\u3002\u7167\u5408\u3067\u304d\u306a\u3051\u308c\u3070\u4f8b\u5916\u3067\u6b62\u3081\u308b\n  snapshot(entry)  -> dict     html-snapshot/1 \u306e\u8a18\u9332\uff08\u4e0b\u306e SNAPSHOT_FIELDS\uff09\n\n\u4f9b\u7d66\u5143\u306f\u518d\u53d6\u5f97\u3067\u5931\u6557\u3092\u96a0\u3057\u3066\u306f\u306a\u3089\u306a\u3044\u3002\u30cd\u30c3\u30c8\u30ef\u30fc\u30af\u306b\u3082\u51fa\u306a\u3044\u3002\n\"\"\"\nfrom __future__ import annotations\n\nfrom typing import Iterable, Protocol, runtime_checkable\n\nSNAPSHOT_SCHEMA = \"html-snapshot/1\"\n# \u5fc5\u9808: schema, html, url, encoding\u3002\u4efb\u610f\u3060\u304c\u5024\u3092\u63a8\u6e2c\u3067\u57cb\u3081\u306a\u3044: fetched_at, response_sha256, content_sha256, cache_entry\nSNAPSHOT_FIELDS = (\"schema\", \"html\", \"url\", \"fetched_at\", \"response_sha256\",\n                   \"content_sha256\", \"encoding\", \"cache_entry\")\nENTRY_FIELDS = (\"key\", \"url\", \"group\")\n\n\n@runtime_checkable\nclass SnapshotSupplier(Protocol):\n    def entries(self) -> Iterable[dict]: ...\n    def body(self, entry: dict) -> str: ...\n    def snapshot(self, entry: dict) -> dict: ...\n\n\nclass QueRyuCacheSource:\n    \"\"\"QueRyu \u306e `Cache`\uff08Aoi/queryu\uff09\u3092\u4f9b\u7d66\u5143\u3068\u3057\u3066\u5305\u3080\u3002\n\n    \u65e2\u5b9a\u306e entries() \u306f key \u3054\u3068\u306e\u6700\u65b0\u884c\uff08key \u306e\u6607\u9806\uff09\u3002\u7167\u5408\u306f Cache \u5074\u304c\u884c\u3046\n    \uff08sha256 \u3068 bytes \u306e\u7167\u5408\u3001\u5931\u6557\u306f CacheIntegrityError\uff09\u3002\n    \"\"\"\n\n    def __init__(self, cache):\n        self.cache = cache\n\n    def entries(self) -> list[dict]:\n        return [entry for _, entry in sorted(self.cache.latest().items())]\n\n    def body(self, entry: dict) -> str:\n        return self.cache.body(entry)\n\n    def snapshot(self, entry: dict) -> dict:\n        return self.cache.snapshot(entry)\n",
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
