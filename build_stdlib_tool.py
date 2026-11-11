"""Prepare an installable stdlib-only DRAgoWing HTML inspection tool."""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYPROJECT = '''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "dragowing-stdlib"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
dragowing-html = "dragowing:main"

[tool.setuptools]
py-modules = ["dragowing"]
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path, help="new directory for the generated uv tool project")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ROOT / "dragowing.py", args.out / "dragowing.py")
    (args.out / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")


if __name__ == "__main__":
    main()
