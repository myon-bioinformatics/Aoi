#!/usr/bin/env python3
"""保存済みの観測から、sakanalytics の入力（key, date, home, away, hs, as）の試合表を作る（探索用）。

標準ライブラリのみ。ネットワークは使わない。QueRyu 側の変換として採用するものではなく、波の試し（wave_eps_*）と
2026年の確かめ（r18_partial_confirmation.py）の入力を、リポジトリの中身だけで作り直せるようにするためのもの。

  - 2013〜2025年: recovered-inputs/observed/games_raw.json（PR #127）。終了（final）で両球団の ID がある試合を、
    日付と URL の順に数え、両球団とも「その年の試合数」に届くまでの試合だけを採る（ポストシーズンは試合数の上限で外れる）。
    その年の試合数は、確定済み season.jsonl の G（--season-jsonl）。key は URL の末尾（拡張子なし）。
  - 2026年: season-2026/observed/games.jsonl（確定した 858 試合）をそのまま変換する。key は URL から `s<年><月日>-<ホーム>-<ビジター>-<回戦>`。
    2026年は games_raw.json の最後が 10月3日までなので、こちらを使う。

作った表の球団年ごとの G/W/L/T/RF/RA は、確定済みの値（2013〜2025年は season.jsonl、2026年は season-2026/derived/team_totals.jsonl）と
全部一致しなければ、書き出さずに止まる（--check-totals を渡したとき）。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/games_table_from_observed.py \\
      --games-raw cycles/c001-chunichi/recovered-inputs/observed/games_raw.json \\
      --season-jsonl cycles/c001-chunichi/outputs/season.jsonl \\
      --season-2026 cycles/c001-chunichi/season-2026/observed/games.jsonl \\
      --totals-2026 cycles/c001-chunichi/season-2026/derived/team_totals.jsonl --out /tmp/games.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

URL_2026 = re.compile(r"https://npb\.jp/scores/(\d{4})/(\d{4})/([a-z]+)-([a-z]+)-(\d+)/")
FIRST, LAST = 2013, 2025


def _score(v, where: str) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise ValueError(f"{where}: 得点が 0 以上の整数でない: {v!r}")
    return v


def _row(key: str, date8: str, home: str, away: str, hs, as_, where: str) -> dict:
    if not re.fullmatch(r"\d{8}", str(date8)):
        raise ValueError(f"{where}: 日付が YYYYMMDD でない: {date8!r}")
    d = str(date8)
    return {"key": key, "date": f"{d[:4]}-{d[4:6]}-{d[6:]}", "home": home, "away": away,
            "hs": _score(hs, where), "as": _score(as_, where)}


def games_per_team(season_rows: list[dict]) -> dict:
    """確定済み season.jsonl の {(season, team): G}。"""
    out = {}
    for r in season_rows:
        out[(int(r["season"]), r["team"])] = int(r["G"])
    return out


def from_games_raw(raw: list[dict], g: dict, first: int = FIRST, last: int = LAST) -> list[dict]:
    """games_raw.json から first〜last 年の公式戦を採る。g は {(年, 球団): 試合数}。"""
    rows = [x for x in raw if x.get("status") == "final" and first <= x["year"] <= last and x.get("home") and x.get("away")]
    rows.sort(key=lambda x: (x["date"], x["url"]))
    seen, taken, out = Counter(), set(), []
    for x in rows:
        y, h, a = x["year"], x["home"], x["away"]
        if (y, h) not in g or (y, a) not in g:
            raise ValueError(f"{x['url']}: {y} 年の {h if (y, h) not in g else a} の試合数（G）が確定済みの表にない")
        if seen[(y, h)] >= g[(y, h)] or seen[(y, a)] >= g[(y, a)]:
            continue
        key = x["url"].rsplit("/", 1)[-1].removesuffix(".html")
        if key in taken:
            raise ValueError(f"{x['url']}: key が重複している: {key}")
        taken.add(key)
        seen[(y, h)] += 1
        seen[(y, a)] += 1
        out.append(_row(key, x["date"], h, a, x["home_R"], x["away_R"], x["url"]))
    short = sorted(k for k, n in g.items() if first <= k[0] <= last and seen[k] != n)
    if short:
        raise ValueError(f"試合数に届かない球団年がある: {short[:5]}（{len(short)} 件）")
    return out


def from_season_games(rows: list[dict]) -> list[dict]:
    """season-2026/observed/games.jsonl（確定した公式戦）を試合表の形にする。"""
    out, taken = [], set()
    for x in rows:
        if x.get("status") != "final":
            raise ValueError(f"{x.get('url')}: 終了（final）でない: {x.get('status')!r}")
        m = URL_2026.fullmatch(x["url"])
        if not m:
            raise ValueError(f"{x['url']}: URL が想定の形でない")
        year, md, h, a, n = m.groups()
        if h != x["home"] or a != x["away"] or str(year) + md != str(x["date"]):
            raise ValueError(f"{x['url']}: URL と home/away/date が合わない")
        key = f"s{year}{md}-{h}-{a}-{n}"
        if key in taken:
            raise ValueError(f"{x['url']}: key が重複している: {key}")
        taken.add(key)
        out.append(_row(key, x["date"], x["home"], x["away"], x["home_R"], x["away_R"], x["url"]))
    out.sort(key=lambda r: (r["date"], r["key"]))
    return out


def team_totals(games: list[dict]) -> dict:
    """試合表から球団年ごとの {G, W, L, T, RF, RA}。"""
    t: dict = {}
    for r in games:
        y = int(r["date"][:4])
        for team, rf, ra in ((r["home"], r["hs"], r["as"]), (r["away"], r["as"], r["hs"])):
            c = t.setdefault((y, team), Counter())
            c["G"] += 1
            c["RF"] += rf
            c["RA"] += ra
            c["W" if rf > ra else "L" if rf < ra else "T"] += 1
    return {k: {f: v[f] for f in ("G", "W", "L", "T", "RF", "RA")} for k, v in t.items()}


def check_totals(games: list[dict], expected: dict) -> list[str]:
    """expected: {(年, 球団): {G, W, L, T, RF, RA}}。games に出てくる年の球団年だけを比べ、違いを文字で返す。"""
    got = team_totals(games)
    years = {k[0] for k in got}
    problems = [f"{k}: 確定済みの表にない" for k in sorted(got) if k not in expected]
    problems += [f"{k}: 試合表にない" for k in sorted(expected) if k[0] in years and k not in got]
    for k in sorted(set(got) & set(expected)):
        for f, v in got[k].items():
            if int(expected[k][f]) != v:
                problems.append(f"{k} {f}: 試合表 {v} ≠ 確定済み {expected[k][f]}")
    return problems


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games-raw", type=Path, help="recovered-inputs/observed/games_raw.json（2013〜2025年を採る）")
    ap.add_argument("--season-jsonl", type=Path, help="確定済みの season.jsonl（--games-raw のとき、年ごとの試合数 G と照合に使う）")
    ap.add_argument("--season-2026", type=Path, help="season-2026/observed/games.jsonl")
    ap.add_argument("--totals-2026", type=Path, help="season-2026/derived/team_totals.jsonl（あれば 2026年の G/W/L/T/RF/RA と照合する）")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if not args.games_raw and not args.season_2026:
        print("--games-raw か --season-2026 のどちらかが要る", file=sys.stderr)
        return 2
    if args.games_raw and not args.season_jsonl:
        print("--games-raw には --season-jsonl（年ごとの試合数 G）が要る", file=sys.stderr)
        return 2
    try:
        games, expected = [], {}
        if args.games_raw:
            season = _jsonl(args.season_jsonl)
            g = games_per_team(season)
            games += from_games_raw(json.loads(args.games_raw.read_text(encoding="utf-8")), g)
            expected |= {(int(r["season"]), r["team"]): r for r in season if FIRST <= int(r["season"]) <= LAST}
        if args.season_2026:
            games += from_season_games(_jsonl(args.season_2026))
            if args.totals_2026:
                expected |= {(int(r["season"]), r["team"]): r for r in _jsonl(args.totals_2026)}
        problems = check_totals(games, expected)
        if problems:
            raise ValueError("球団年の G/W/L/T/RF/RA が確定済みの値と合わない:\n  " + "\n  ".join(problems[:10]))
        text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in games)
    except (ValueError, KeyError) as exc:
        print(exc, file=sys.stderr)
        return 2
    args.out.write_text(text, encoding="utf-8")
    print(f"書き出し: {args.out}（{len(games)} 試合、{len(team_totals(games))} 球団年）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
