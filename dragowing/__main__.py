import sys

if __package__:
    from .cli import main
else:
    # `python <このディレクトリ>/__main__.py` で動かしたとき（PYTHONPATH なし）。
    # このディレクトリをパッケージ dragowing として登録する（conftest.py と同じ。__init__.py は置かない）。
    import importlib.machinery, types
    from pathlib import Path

    _here = Path(__file__).resolve().parent
    if sys.path and Path(sys.path[0] or ".").resolve() == _here:
        del sys.path[0]  # -m と同じく、パッケージの中のモジュールを最上位として読まない
    if "dragowing" not in sys.modules:
        _pkg = types.ModuleType("dragowing")
        _pkg.__path__ = [str(_here)]
        _pkg.__package__ = "dragowing"
        _pkg.__spec__ = importlib.machinery.ModuleSpec("dragowing", loader=None, is_package=True)
        _pkg.__spec__.submodule_search_locations = _pkg.__path__
        sys.modules["dragowing"] = _pkg
    from dragowing.cli import main

sys.exit(main())
