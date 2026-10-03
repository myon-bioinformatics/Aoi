"""Compare calendar-derived W/L/D/R/RA with independent official annual tables."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "queryu")]
import httpx
from queryu import Cache, PoliteFetcher, UA
from selectolax.lexbor import LexborHTMLParser
from analyze import describe, sha, units

NAMES = {"読売ジャイアンツ": "g", "東京ヤクルトスワローズ": "s", "横浜DeNAベイスターズ": "db",
         "中日ドラゴンズ": "d", "阪神タイガース": "t", "広島東洋カープ": "c",
         "福岡ソフトバンクホークス": "h", "北海道日本ハムファイターズ": "f",
         "オリックス・バファローズ": "b", "東北楽天ゴールデンイーグルス": "e",
         "埼玉西武ライオンズ": "l", "千葉ロッテマリーンズ": "m"}


def annual(html):
    matches = {}
    for tr in LexborHTMLParser(html).css("tr"):
        cells = [re.sub(r"\s+", "", td.text()) for td in tr.css("td")]
        if cells and cells[0] in NAMES:
            matches.setdefault(NAMES[cells[0]], []).append(cells)
    result = {}
    for team, rows in matches.items():
        if len(rows) != 3:
            raise ValueError(f"expected standings/batting/pitching rows: {team}: {rows}")
        standing, batting, pitching = rows
        if not standing[1].isdigit() or not batting[1].startswith("."):
            raise ValueError(f"unexpected official row shape: {team}: {rows}")
        result[team] = dict(zip(("g", "w", "l", "d"), map(int, standing[1:5])))
        result[team].update(r=int(batting[4]), ra=int(pitching[-1]))
        if (int(batting[2]), int(pitching[2]), int(pitching[3]), int(pitching[4])) != (
                result[team]["g"], result[team]["g"], result[team]["w"], result[team]["l"]):
            raise ValueError("official tables internally inconsistent or parser columns incorrect")
    if len(result) != 6:
        raise ValueError(f"expected six official teams; found {result}")
    return result


def main():
    path = ROOT / "data/observations/r001/games.jsonl"
    observed = units([json.loads(line) for line in path.read_text().splitlines()])
    cache = Cache(ROOT / "data/raw/r001_official_annual")
    checks, receipts = [], []
    with httpx.Client(headers={"User-Agent": UA}, timeout=45, follow_redirects=True) as client:
        fetcher = PoliteFetcher(cache, wait=3.0, client=client)
        for year in range(2013, 2026):
            for league in ("central", "pacific"):
                key = f"{league}_{year}"
                url = f"https://npb.jp/bis/yearly/{league}league_{year}.html"
                html = fetcher.get(key, url, str(year))
                expected = annual(html)
                for team, values in expected.items():
                    actual = describe(observed[year, team])
                    differences = {k: {"calendar": actual[k], "annual": v} for k, v in values.items() if actual[k] != v}
                    checks.append({"year": year, "team": team, "fields": list(values), "match": not differences, "differences": differences})
                    if differences:
                        raise ValueError(f"official mismatch: {checks[-1]}")
                e = cache.latest()[key]
                receipts.append({k: e[k] for k in ("key", "url", "status", "sha256", "bytes", "fetched_at", "code_version")})
                print(key, "all six teams match G/W/L/D/R/RA", flush=True)
    output = Path(__file__).parent / "outputs"
    output.mkdir(exist_ok=True)
    (output / "official_verification.json").write_text(json.dumps({"games_sha256": sha(path), "checks": checks, "sources": receipts}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
