"""docs/ の直下はマスターファイル（docs/README.md）。一覧に載せずに直下へ置くこと、載せたまま消すことを止める。"""

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2] / "docs"


def test_every_file_directly_under_docs_is_listed_as_a_master_file():
    listed = set(re.findall(r"^\| \[([^\]]+\.md)\]\(\1\) \|", (DOCS / "README.md").read_text(encoding="utf-8"), re.M))
    present = {p.name for p in DOCS.iterdir() if p.is_file() and p.name != "README.md"}
    assert present - listed == set(), "docs/ の直下にあるのに、マスターファイルの一覧（docs/README.md）にない"
    assert listed - present == set(), "マスターファイルの一覧にあるのに、docs/ の直下にない"
