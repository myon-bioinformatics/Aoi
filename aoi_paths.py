"""Aoi's repository layout (stdlib only). The single place that knows it.

Child projects (QueRyu, DRAgoWing, PythDRagoras, SakAnalytics) do not resolve the Aoi root,
cycle names or result refs; Aoi resolves them here and passes explicit paths and NPB config
(``aoi_npb.py``) to the children. ``python aoi_paths.py ask "問い" [ask.py の引数]`` runs QueRyu's
ask with the resolved ``--results`` / ``--cycle-dir`` and the NPB team table.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

DEFAULT_CYCLE = "c001-chunichi"


def infer_aoi_root(anchor: Path) -> Path:
    """Walk upward from a file or directory to the Aoi repository root."""
    here = anchor.resolve()
    if here.is_file():
        here = here.parent
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "cycles").is_dir():
            return candidate
    if len(here.parents) >= 2:
        return here.parents[1]
    return here


def resolve_aoi_root(explicit: Path | str | None = None, *, anchor: Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("AOI_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    if anchor is None:
        anchor = Path.cwd()
    return infer_aoi_root(anchor)


def cycle_name(explicit: str | None = None) -> str:
    return explicit or os.environ.get("AOI_RESEARCH_CYCLE") or DEFAULT_CYCLE


def resolve_cycle_path(root: Path, cycle: str | Path | None = None) -> Path:
    """Return the cycle directory under ``root`` (or an absolute cycle path)."""
    if cycle is None:
        return (root / "cycles" / cycle_name()).resolve()
    path = Path(cycle)
    if path.is_absolute():
        return path.resolve()
    if path.parts[:1] == ("cycles",):
        return (root / path).resolve()
    if len(path.parts) == 1:
        return (root / "cycles" / path).resolve()
    return (root / path).resolve()


def default_cycle_outputs(root: Path | None = None, *, cycle: str | None = None) -> Path:
    base = root or resolve_aoi_root()
    return resolve_cycle_path(base, cycle) / "outputs"


def pipeline_out(root: Path, cycle: str) -> Path:
    """The ``out`` folder declared in ``cycles/<cycle>/pipeline.toml``."""
    if not isinstance(cycle, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", cycle):
        raise FileNotFoundError(f"結果が読めない: サイクル名が不正 ({cycle})")
    config = root / "cycles" / cycle / "pipeline.toml"
    if not config.is_file():
        raise FileNotFoundError(f"結果が読めない: サイクル設定がない {config}")
    match = re.search(r'(?m)^out\s*=\s*"([^"]+)"', config.read_text(encoding="utf-8"))
    if not match:
        raise FileNotFoundError(f"結果が読めない: {config} に out がない")
    return root / match.group(1)


def resolve_results_dir(root: Path, *, explicit: Path | None = None, cycle: str | None = None,
                        results_ref: str | None = None, results_dir: str | None = None) -> Path:
    """Pick the results directory from the explicit path or the cycle configuration.

    When a results ref or ``AOI_RESULTS_DIR`` is set, only that location is used.
    """
    if explicit is not None:
        return explicit
    if results_dir:
        path = Path(results_dir)
        if not path.is_dir():
            raise FileNotFoundError(f"結果が読めない: {path}")
        return path
    if results_ref:
        if not cycle or not re.fullmatch(r"[A-Za-z0-9._-]+", cycle):
            raise FileNotFoundError("結果が読めない: 結果 ref にはサイクル名が必要")
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", results_ref) or ".." in results_ref:
            raise FileNotFoundError(f"結果が読めない: 結果 ref が不正 ({results_ref})")
        path = root / ".aoi-results" / cycle / "outputs"
        if not path.is_dir():
            raise FileNotFoundError(f"結果が読めない: {results_ref} の {path} がない")
        return path
    return pipeline_out(root, cycle_name(cycle))


def ask_main(argv: list[str], *, root: Path | None = None) -> int:
    """Run QueRyu's ask with Aoi's resolved results, cycle folder and NPB team table."""
    root = resolve_aoi_root(root, anchor=Path(__file__))
    cycle = cycle_name()
    try:
        results = resolve_results_dir(root, cycle=cycle, results_ref=os.environ.get("AOI_RESULTS_REF"),
                                      results_dir=os.environ.get("AOI_RESULTS_DIR"))
    except FileNotFoundError as error:
        if "--results" not in argv and "--schema" not in argv:
            print(str(error), file=sys.stderr)
            return 1
        results = None
    for path in (root, root / "queryu" / "ask"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    import aoi_npb
    import ask

    ask.set_teams(aoi_npb.TEAMS)
    defaults = ["--cycle-dir", str(resolve_cycle_path(root, cycle))]
    if results is not None:
        defaults += ["--results", str(results)]
    # 呼び出し側の --results・--cycle-dir が後ろにあれば、そちらが勝つ
    return ask.main([*defaults, *argv])


if __name__ == "__main__":
    if sys.argv[1:2] != ["ask"]:
        raise SystemExit("usage: python aoi_paths.py ask \"問い\" [ask.py の引数]")
    raise SystemExit(ask_main(sys.argv[2:]))
