"""Aoi entry for BlueProbe; requires the corresponding Aoi child checkout."""
import os
from pathlib import Path
import subprocess
import sys

# Drop the Aoi checkout from the child sys.path. `uv run` puts it there (editable
# install), so a folder such as blueprobe/ would be imported as a namespace
# package and aoi_sibling_path would skip the real module. Sibling lookup uses
# AOI_ROOT instead of a constructed PYTHONPATH. The child's own directory is
# then put on sys.path, as `python child/file.py` would do.
_STARTER = 'import sys\nfrom pathlib import Path\nroot = Path(sys.argv[1]).resolve()\ntarget = Path(sys.argv[2])\nsys.argv = [str(target), *sys.argv[3:]]\nsys.path[:] = [p for p in sys.path if p and Path(p).resolve() != root]\nsys.path.insert(0, str(target.parent.resolve()))\nimport runpy\nrunpy.run_path(str(target), run_name="__main__")\n'


def main():
    root = Path(__file__).resolve().parent.parent
    target = root / 'blueprobe' / 'blueprobe.py'
    if not target.is_file():
        print(f"BlueProbe backend not found: {target}. Use a complete Aoi checkout.", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["AOI_ROOT"] = str(root)
    return subprocess.run(
        [sys.executable, "-c", _STARTER, str(root), str(target), *sys.argv[1:]],
        env=env,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
