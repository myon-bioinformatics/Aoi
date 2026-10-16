"""リポジトリの構成の決まり（ユーザーの方針、2026-10-06）。

- サブプロジェクトのフォルダ名はサブプロジェクト名（頭大文字の区切り、BlueProbe など）。検索で引っかかるように
- トップに置く .py は、同じ名前のメインファイル（小文字、blueprobe.py など）だけ
- それ以外の .py は用途のフォルダ（子・孫。baseball/ = 野球、logic/ = 命題と集合 など）か tests/ に置く
- .py のファイル名は小文字
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBPROJECTS = {"BlueProbe": "blueprobe.py", "QueRyu": "queryu.py", "SakAnalytics": "sakanalytics.py",
               "PythDRagoras": "pythdragoras.py", "NagoyAction": "nagoyaction.py", "DRAgoWing": "dragowing.py"}


def test_subproject_folders_use_the_subproject_names():
    for name in SUBPROJECTS:
        assert (ROOT / name).is_dir(), name
        assert not (ROOT / name.lower()).exists() or (ROOT / name.lower()).samefile(ROOT / name), f"{name.lower()}/ が残っている"


def test_only_the_main_file_sits_at_the_top_of_each_subproject():
    for name, main in SUBPROJECTS.items():
        top = sorted(f.name for f in (ROOT / name).glob("*.py"))
        assert top == [main], (name, top)


def test_other_modules_live_in_purpose_folders_and_are_lowercase():
    for name in SUBPROJECTS:
        for f in (ROOT / name).rglob("*.py"):
            rel = f.relative_to(ROOT / name)
            assert f.name == f.name.lower(), rel
            if len(rel.parts) > 1:
                assert rel.parts[0] != "__pycache__" and rel.parts[0] == rel.parts[0].lower(), rel   # 用途のフォルダも小文字
