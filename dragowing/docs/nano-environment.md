# Optional, pinned HTML-only environment

This opt-in recipe keeps DRAgoWing's real HTML implementation and existing
explicit `--overlap-backend stdlib` path in the pinned source. It installs only the locked Markdown 3.11.2
dependency for that feature, not the native NumPy/Polars backend, dev tools,
Chromium, or a replacement implementation. The repository's dependencies,
tests, CI and vendor registrations are unchanged.

Use this for supported JSONL inputs and HTML files only. Do not pass `--embed`,
`--png` or `--svg` in this environment. Generated HTML still references external
Plotly.js; producing the file without opening it is not browser-rendering proof.
The stdlib backend has a restricted input domain; see
[its supported inputs and limitations](overlap-stdlib.md). Do not silently fall
back to native when a value is unsupported.

## 1. Stage verified tools and complete source

The following Linux/POSIX-shell example creates a new private workspace outside
your current checkout. It needs already-installed Git, Python 3.11+, uv 0.13.4
and `sha256sum`; it does not provision or upgrade those tools. Git source reads
use the fixed public revisions below. Do not replace a revision with `main`.

The shared tool is pinned to the actual parent merge
[`3128b4019b9949a6ccc80c686cd84c93f04af119`](https://github.com/myon-bioinformatics/myon-bioinformatics/commit/3128b4019b9949a6ccc80c686cd84c93f04af119).
Its export receipt verifies **two manifest blobs only**, not a complete checkout
or its ancestry. The separate Git checkout checks below establish the source
revisions used by this example. Recheck a checkout if you modify its files.

Set `TMPDIR` to a writable directory outside every repository checkout. Relative
paths are resolved before changing directory; paths containing spaces are quoted.

```sh
set -eu
umask 077
PYTHON=$(command -v python3)
PYTHON=$("$PYTHON" -S -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$PYTHON")
UV=$("$PYTHON" -S -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$(command -v uv)")
GIT=$("$PYTHON" -S -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$(command -v git)")
TMPDIR=$("$PYTHON" -S -c 'import os; print(os.path.abspath(os.environ.get("TMPDIR") or "/tmp"))')
export TMPDIR
"$PYTHON" -S -c 'import sys; assert sys.version_info >= (3, 11)'
test "$("$UV" --version)" = 'uv 0.13.4'
WORK=$(mktemp -d "${TMPDIR:-/tmp}/dragowing-html-XXXXXXXX")
WORK=$(cd "$WORK" && pwd -P)
export WORK PYTHON UV GIT
cd "$WORK"

snapshot() {
  directory=$1 repository=$2 revision=$3
  "$GIT" init -q "$directory"
  "$GIT" -C "$directory" remote add origin "https://github.com/$repository.git"
  "$GIT" -C "$directory" fetch --depth=1 --no-tags origin "$revision"
  test "$("$GIT" -C "$directory" rev-parse FETCH_HEAD)" = "$revision"
  "$GIT" -C "$directory" -c core.autocrlf=false checkout -q --detach "$revision"
  test "$("$GIT" -C "$directory" rev-parse HEAD)" = "$revision"
  "$GIT" -C "$directory" diff --exit-code HEAD --
}

snapshot "$WORK/parent" myon-bioinformatics/myon-bioinformatics \
  3128b4019b9949a6ccc80c686cd84c93f04af119
(cd "$WORK/parent" && sha256sum -c <<'HASHES'
aa74cde16da7a33c4cc1398f78c4d0447179ea752d262e8592a11ddb8ce8c3e8  tools/nano_export.py
6b71651b3f361bc54bd921b557d3fc347bbd13e0b98035896c7fa11f2190e535  docs/stdlib-shrink-queue.json
HASHES
)

mkdir "$WORK/src" "$WORK/prepared"
snapshot "$WORK/src/dragowing" myon-bioinformatics/DRAgoWing \
  be2185b142aebcbedee97688fe08ee0092179472
snapshot "$WORK/src/queryu" myon-bioinformatics/QueRyu \
  4c59cb00ca2ba898573e4af95bc4a63492aa5eb9
snapshot "$WORK/src/aoi" myon-bioinformatics/Aoi \
  385e14a09ad56b69c57ec1cbae04c16299d387c5

test "$("$GIT" hash-object "$WORK/src/dragowing/pyproject.toml")" = \
  ca7cd1f307080d4c369a5a14031ee2cb4f93f14d
test "$("$GIT" hash-object "$WORK/src/dragowing/uv.lock")" = \
  2788b84741af5ec04d59e5074e4010e067495654
"$PYTHON" -S "$WORK/parent/tools/nano_export.py" \
  --feature dragowing-html --uv "$UV" \
  --source "$WORK/src/dragowing" --output-parent "$WORK/prepared" \
  > "$WORK/preparation.json"
FEATURE_DIR=$("$PYTHON" -S -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["directory"])' \
  "$WORK/preparation.json")
export FEATURE_DIR
cat "$FEATURE_DIR/receipt.json"
printf 'Workspace: %s\n' "$WORK"
```

The exporter uses locked, offline uv export, no default dev group, no project
installation, and `--prune numpy --prune polars`. It fails if either reviewed
manifest changed or the resulting selection is not Markdown-only. This step
does not install packages or run DRAgoWing. A new source/lock needs review and a
new explicit pin; do not edit the receipt or bypass the mismatch.

The complete `dragowing` directory name is intentional: it is a namespace
package, not an installed wheel. QueRyu's pinned `ask/ask.py` supplies
registration labels. Aoi supplies the real c001 fixture below, not an empty
placeholder. The native backend additionally needs PythDRagoras
`6985419e89b3c02415b92bcc271e892946feb41b`; it is not needed by this selected
stdlib path and is not silently included in the Markdown-only environment.

## 2. Install the selected dependencies explicitly

This is an optional package-download step, not part of preparation or CI.
Use a new venv and private package cache. It retains the exported versions and
hashes, uses official PyPI binary wheels only, and does not install this project.
If a wheel is unavailable or a network operation fails, stop; do not drop hashes,
upgrade dependencies or switch to source builds to make this recipe pass.

```sh
"$PYTHON" -S - "$FEATURE_DIR" <<'PY'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
r = json.loads((p / 'receipt.json').read_text())
assert r['recipe'] == 'dragowing-html'
assert hashlib.sha256((p / 'requirements.txt').read_bytes()).hexdigest() == r['requirements_sha256']
assert r['exported_package_names'] == ['markdown']
PY
"$PYTHON" -m venv --without-pip "$WORK/html-venv"
mkdir "$WORK/installer-home" "$WORK/installer-tmp" "$WORK/uv-cache"
env -i PATH="$PATH" HOME="$WORK/installer-home" TMPDIR="$WORK/installer-tmp" \
  UV_CACHE_DIR="$WORK/uv-cache" UV_HTTP_RETRIES=0 UV_HTTP_TIMEOUT=60 \
  "$UV" --no-config pip install --python "$WORK/html-venv/bin/python" \
  --index-url https://pypi.org/simple --require-hashes --only-binary :all: \
  --no-deps --link-mode copy -r "$FEATURE_DIR/requirements.txt"
```

## 3. Use the existing CLI, without opening a browser

Keep the variables from the same shell. These are real pinned sources, not a
modified `__main__` or a replacement `analyze` function. The source dependencies
and fixture are outside the venv and must remain available.

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="$WORK/src:$WORK/src/queryu/ask" \
  "$WORK/html-venv/bin/python" -m dragowing \
  --results "$WORK/src/aoi/cycles/c001-chunichi/outputs" \
  --out "$WORK/html-output" --overlap-backend stdlib
test -s "$WORK/html-output/index.html"
test -s "$WORK/html-output/propositions.html"
```

Use a new output directory for each independent job. Do not point concurrent
jobs at one output directory or interpret a venv as a resource quota/sandbox.
Viewing the generated HTML and its external resources is a separate operation.

## What this does not replace

- The [normal installation and complete test procedure](../README.md#tests)
  stays unchanged. Keep its native libraries, dev dependencies, PythDRagoras,
  Aoi test context and required CI Chromium; do not run the full suite in the
  Markdown-only venv or remove tests to accommodate it.
- The historical [source-pinned comparison and limits](https://github.com/myon-bioinformatics/myon-bioinformatics/blob/3128b4019b9949a6ccc80c686cd84c93f04af119/docs/nano-feature-environments.md)
  measured supported HTML outputs, not browser appearance or every input domain.
  Its two completed install pairs, third-trial timeout and selected trial 2
  remain historical; these instructions do not claim a new measurement.
- Docs-only adoption does not register a vendor, change automatic workflows,
  synchronize Aoi's subtree, or merge this child. Existing DRA docs CI still
  resolves Aoi/parent main and performs its vendor checks/temp Aoi package
  import; that is separate from this fixed-source feature recipe.
