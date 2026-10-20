#!/usr/bin/env python3
"""selectolax を使う研究コードを、本物か selectolax_min で走らせて JSON を書く（実験）。

    python mindeps/run_selectolax.py --impl real out.json
    python mindeps/run_selectolax.py --impl min  out.json   # selectolax が入っていない環境

--impl min では、本物の selectolax が import できる環境なら失敗する。
verify.py は import 時に httpx も読むので、httpx が無いときだけ httpx_min を先に置く。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "gpt-r001-score-allocation"
sys.path[:0] = [
    str(ROOT), str(ROOT / "mindeps"), str(ROOT / "scripts"),
    str(ROOT / "blueprobe"), str(ROOT / "queryu"), str(RESEARCH),
]


def install_httpx_min() -> None:
    if importlib.util.find_spec("httpx") is not None:
        return
    spec = importlib.util.spec_from_file_location("httpx", ROOT / "mindeps" / "httpx_min.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["httpx"] = module
    spec.loader.exec_module(module)


def install_selectolax_min() -> None:
    if importlib.util.find_spec("selectolax") is not None:
        raise SystemExit("selectolax が入っている。--impl min は selectolax なしの環境で動かす")
    install_httpx_min()
    spec = importlib.util.spec_from_file_location("selectolax.lexbor", ROOT / "mindeps" / "selectolax_min.py")
    module = importlib.util.module_from_spec(spec)
    package = types.ModuleType("selectolax")
    package.__path__ = []
    package.lexbor = module
    sys.modules["selectolax"] = package
    sys.modules["selectolax.lexbor"] = module
    spec.loader.exec_module(module)


def use_min_parser() -> None:
    """既に import 済みの研究モジュールの LexborHTMLParser を min に差し替える。"""
    import inning_pilot
    import observe
    import selectolax_min
    import verify

    observe.LexborHTMLParser = selectolax_min.LexborHTMLParser
    inning_pilot.LexborHTMLParser = selectolax_min.LexborHTMLParser
    verify.LexborHTMLParser = selectolax_min.LexborHTMLParser


def _jsonable(value):
    if isinstance(value, Counter):
        return dict(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _call(name, fn):
    try:
        return {"name": name, "value": _jsonable(fn())}
    except ValueError as exc:
        return {"name": name, "error": f"ValueError: {exc}"}


def _score_row(name, values):
    return '<tr><td class="gmscoreteam">' + name + "</td>" + "".join(
        '<td class="gmscore">' + value + "</td>" for value in values) + "</tr>"


def _cells(values):
    parts = []
    for index, value in enumerate(values):
        parts.append('<td class="gmscore">' + value + "</td>")
        if index in (2, 5):
            parts.append('<td class="gmscspan"><br /></td>')
    return "".join(parts)


def _annual_page() -> str:
    teams = [
        ("読売<br>ジャイアンツ", 143, 80, 60, 3, 520, 400),
        ("東京ヤクルトスワローズ", 143, 70, 70, 3, 500, 480),
        ("横浜DeNAベイスターズ", 143, 75, 65, 3, 510, 470),
        ("中日ドラゴンズ", 143, 60, 80, 3, 430, 560),
        ("阪神タイガース", 143, 88, 52, 3, 600, 390),
        ("広島東洋カープ", 143, 65, 75, 3, 470, 510),
    ]
    rows = []
    for name, games, wins, losses, draws, runs, runs_allowed in teams:
        rows.append(
            f"<tr><td>{name}</td><td>{games}</td><td>{wins}</td><td>{losses}</td><td>{draws}</td></tr>"
            f"<tr><td>{name}</td><td>.250</td><td>{games}</td><td>0</td><td>{runs}</td></tr>"
            f"<tr><td>{name}</td><td>0</td><td>{games}</td><td>{wins}</td><td>{losses}</td><td>{runs_allowed}</td></tr>"
        )
    return "<table>" + "".join(rows) + "</table>"


def outcomes() -> list:
    import inning_pilot
    import observe
    from verify import annual

    url = "https://npb.jp/bis/2013/calendar/index_10.html"
    observe_pages = {
        "label": '''<div class="stvsteam"><div class="tescheaten">CS ファーストS</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>
        <div class="stvsteam"><div><a href="/bis/2013/games/s2013101200002.html">楽 3 - 2 オ</a></div></div>''',
        "allstar": '''<div class="stvsteam"><div class="tescheaten">オールスター</div>
        <div><a href="/bis/2013/games/s2013071900001.html">パ 2 - 2 セ</a></div></div>''',
        "unknown_label": '''<div class="stvsteam"><div class="tescheaten">未知大会</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>''',
        "climax": '''<div class="stvsteam"><div class="tescheaten">クライマックスS</div>
        <div><a href="/bis/2020/games/s2020111400001.html">ソ 2 - 1 ロ</a></div></div>''',
        "calendar_fixture": (ROOT / "blueprobe/tests/fixtures/npb_calendar_sample.html").read_text(encoding="utf-8"),
    }
    inning_pages = {
        "wrong_total": (
            '<div id="gmdivresult"><table>'
            + _score_row("中日", ["0"] * 9 + ["-", "1", "0", "0"])
            + _score_row("東京ヤクルト", ["0"] * 8 + ["X", "-", "0", "0", "0"])
            + "</table></div>",
            {"away": "d", "home": "s", "as": 1, "hs": 0},
        ),
        "board": (
            '<div id="gmdivresult"><table>'
            '<tr><td class="gmscorettl" colspan="13"><br /></td><td class="gmscorettl">Ｒ</td></tr>'
            '<tr><td class="gmscoreteam">阪　神</td>' + _cells(["0"] * 9)
            + '<td align="center" class="gmscore">-</td><td align="center" class="gmscore">0</td>'
            '<td class="gmscore">4</td><td class="gmscore">0</td></tr>'
            '<tr><td class="gmscoreteam">読　売</td>' + _cells(["0", "0", "0", "0", "3", "0", "0", "1", "X"])
            + '<td align="center" class="gmscore">-</td><td align="center" class="gmscore">4</td>'
            '<td class="gmscore">10</td><td class="gmscore">1</td></tr></table></div>',
            {"away": "t", "home": "g", "as": 0, "hs": 4},
        ),
        "marked": (
            '<div id="gmdivresult"><table>'
            '<tr><td class="gmscoreteam">中　日</td>' + _cells([" 0 ", "\n1\n", "２", "0", "0", "0", "0", "0", "<span>0</span>"])
            + '<td class="gmscore">-</td><td class="gmscore">3</td><td class="gmscore">8</td><td class="gmscore">1</td></tr>'
            '<tr><td class="gmscoreteam"> 東京ヤクルト </td>' + _cells(["0"] * 8 + ["２ｘ"])
            + '<td class="gmscore">-</td><td class="gmscore">2</td><td class="gmscore">9</td><td class="gmscore">0</td></tr>'
            "</table></div>",
            {"away": "d", "home": "s", "as": 3, "hs": 2},
        ),
    }
    calls = [_call(name, lambda html=html: observe.parse(html, url)) for name, html in observe_pages.items()]
    calls += [
        _call(name, lambda html=html, game=game: inning_pilot.parse(html, game))
        for name, (html, game) in inning_pages.items()
    ]
    calls.append(_call("annual_synthetic", lambda: annual(_annual_page())))
    fixture = (ROOT / "blueprobe/tests/fixtures/npb_annual/2005_c_std.html").read_text(encoding="utf-8")
    calls.append(_call("annual_fixture", lambda: annual(fixture)))
    return calls


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--impl", choices=["real", "min"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.impl == "min":
        install_selectolax_min()
    elif importlib.util.find_spec("selectolax") is None:
        raise SystemExit("selectolax が無い。--impl real は selectolax のある環境で動かす")
    result = outcomes()
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"selectolax={args.impl} cases={len(result)} bytes={len(text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
