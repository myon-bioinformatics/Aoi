"""Aoi の兄弟サブプロジェクト（QueRyu の ask、PythDRagoras の propositions / rule_search）を AOI_ROOT から探す。

形は QueRyu の ``aoi_sibling_path`` と同じ。PYTHONPATH は要らない。
"""
from __future__ import annotations

import importlib, importlib.util, os, sys
from pathlib import Path

AOI_ROOT_HINT = "AOI_ROOT=<Aoi のルート> を渡す（.github/workflows/ci.yml と同じ）"


def aoi_sibling_path(module: str, sibling: str, *, here: Path | None = None, env=None) -> None:
    """``module`` が import できないときだけ、Aoi の checkout の ``sibling/`` を ``sys.path`` に足す。

    Aoi の場所は ``AOI_ROOT``（pyproject.toml と cycles/ がある）で受け取る。``AOI_ROOT`` がないときは、
    このパッケージの親が Aoi の checkout（Aoi に subtree として入っている）のときだけ使う（QueRyu と同じ）。
    単独の DRAgoWing では隣を読まない。PYTHONPATH などで import できるものは上書きしない。
    """
    if module in sys.modules or importlib.util.find_spec(module) is not None:
        return
    env = os.environ if env is None else env
    value = env.get("AOI_ROOT")
    root = Path(value).expanduser().resolve() if value else Path(here or __file__).resolve().parent.parent
    candidate = root / sibling
    if (root / "pyproject.toml").is_file() and (root / "cycles").is_dir() and candidate.is_dir():
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


def import_aoi_sibling(module: str, sibling: str):
    """``aoi_sibling_path`` のあとで ``module`` を import する。無ければ AOI_ROOT の案内つきで止める。"""
    aoi_sibling_path(module, sibling)
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError as error:
        if error.name != module:
            raise
        raise ModuleNotFoundError(f"{module} が見つからない（Aoi の {sibling}/）。{AOI_ROOT_HINT}", name=module) from None
