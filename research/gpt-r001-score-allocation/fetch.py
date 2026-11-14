"""R001 の取得と公式ページでの照合（npb.jp の日程・試合のページ。キャッシュを先に見る）。

    python research/gpt-r001-score-allocation/fetch.py <処理> [その処理の引数]

処理: collect, observe, verify, inning_pilot

1 つの処理が 1 つのサブコマンド（旧 collect.py, observe.py, verify.py … の 1 本が 1 つ）。引数と説明は各関数の説明（旧ファイルの冒頭）にある。
BlueProbe（npb_calendar・blueprobe）と QueRyu（Cache・PoliteFetcher）を使うので、その 2 つを sys.path に足す。
httpx と selectolax が無い環境では mindeps/ の httpx_min・selectolax_min を先に置く（mindeps/run_*.py）。
同じ中身の補助は 1 つにし、処理ごとに中身が違う名前には処理の名前を付けた。旧ファイルの HERE・ROOT・sys.path の行は、この冒頭の 1 か所にまとめた。
"""

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "blueprobe"), str(ROOT / "queryu")]

import httpx  # noqa: E402
import npb_calendar  # noqa: E402
from analyses import analyze_describe as describe, analyze_sha as sha, units  # noqa: E402
from blueprobe import merge, new_report, NORMALIZATION  # noqa: E402
from queryu import Cache, PoliteFetcher, UA, write_dataset  # noqa: E402
from selectolax.lexbor import LexborHTMLParser  # noqa: E402


# ==== collect（旧 collect.py）

def collect_main():
    cache = Cache(ROOT / "data/raw/npb_calendar")
    # PR #2's explicit HTTPTransport bypasses proxy settings in this environment.
    # Inject a proxy-aware client; do not alter the upstream acquisition module.
    with httpx.Client(headers={"User-Agent": UA}, timeout=45, follow_redirects=True) as client:
        fetcher = PoliteFetcher(cache, wait=3.0, client=client)
        for year in range(2013, 2026):
            for key, url, group in npb_calendar.pages([year]):
                fetcher.get(key, url, group)
            print(year, "calendar pages cached", flush=True)
        print("HTTP requests:", fetcher.requests)


def collect(argv=None):
    """Acquire R001 data with the existing cache/parser; respect environment proxies.
    """
    collect_main()


# ==== observe（旧 observe.py）

NON_REGULAR = {"CS ファーストS", "CS ファイナルS", "クライマックスS", "日本シリーズ", "オールスター", "アジアシリーズ"}


def observe_parse(html, url):
    dom = LexborHTMLParser(html)
    excluded = []
    for link in dom.css('a'):
        href = link.attributes.get("href", "")
        if "/games/s" not in href:
            continue
        node = link
        while node.parent and "stvsteam" not in node.parent.attributes.get("class", "").split():
            node = node.parent
        if not node.parent:
            raise ValueError(f"game link outside known calendar structure: {href}")
        prev, label = node.prev, None
        while prev:
            if "tescheaten" in prev.attributes.get("class", "").split():
                label = prev.text().strip()
                break
            prev = prev.prev
        if label is not None:
            if label not in NON_REGULAR:
                raise ValueError(f"unclassified competition label: {label}")
            excluded.append({"href": href, "raw_text": link.text(), "label": label, "source_url": url})
            link.decompose()
    report = npb_calendar.parse(dom.html, url)
    return report, excluded


def observe_main():
    cache = Cache(ROOT / "data/raw/npb_calendar")
    latest = cache.latest()
    total, excluded = new_report(), []
    receipts = []
    for key, url, group in npb_calendar.pages(range(2013, 2026)):
        e = latest[key]
        body = cache.body(e)
        if hashlib.sha256(body.encode()).hexdigest() != e["sha256"]:
            raise ValueError(f"cache hash mismatch: {key}")
        report, exclusions = observe_parse(body, url) if e["status"] == 200 else (new_report(), [])
        merge(total, report)
        excluded += exclusions
        receipts.append({k: e[k] for k in ("key", "url", "status", "sha256", "bytes", "fetched_at", "code_version")})
    out = ROOT / "data/observations/r001/games.jsonl"
    if out.exists():
        previous = [json.loads(line) for line in out.read_text().splitlines()]
        if sorted(previous, key=lambda g: g["key"]) != sorted(total["records"], key=lambda g: g["key"]):
            raise ValueError("observations changed: explicitly archive existing dataset before rebuilding")
    write_dataset(out, total["records"], {"source": "npb_calendar+r001-explicit-competition-labels",
                  "scope": {"years": [2013, 2025]}, "normalization": NORMALIZATION,
                  "dropped": dict(total["counts"]), "unknown": len(total["unknown"]),
                  "competition_exclusions": dict(Counter(e["label"] for e in excluded)),
                  "cache_manifest": str(cache.manifest)})
    (out.parent / "excluded.json").write_text(json.dumps(excluded, ensure_ascii=False, indent=2))
    (out.parent / "unknown.json").write_text(json.dumps(total["unknown"], ensure_ascii=False, indent=2))
    output = Path(__file__).parent / "outputs"
    output.mkdir(exist_ok=True)
    (output / "source_receipts.json").write_text(json.dumps(receipts, ensure_ascii=False, indent=2) + "\n")
    checks = npb_calendar.check(total["records"])
    print("\n".join(checks))
    print("excluded:", dict(Counter(e["label"] for e in excluded)))
    print("unknown:", len(total["unknown"]))
    if total["unknown"] or any("要確認" in c for c in checks):
        raise ValueError("observation gate failed")


def observe(argv=None):
    """Offline study adapter: preserve explicit NPB competition labels as exclusions.
    """
    observe_main()


# ==== verify（旧 verify.py）

VERIFY_NAMES = {"読売ジャイアンツ": "g", "東京ヤクルトスワローズ": "s", "横浜DeNAベイスターズ": "db",
         "中日ドラゴンズ": "d", "阪神タイガース": "t", "広島東洋カープ": "c",
         "福岡ソフトバンクホークス": "h", "北海道日本ハムファイターズ": "f",
         "オリックス・バファローズ": "b", "東北楽天ゴールデンイーグルス": "e",
         "埼玉西武ライオンズ": "l", "千葉ロッテマリーンズ": "m"}


def annual(html):
    matches = {}
    for tr in LexborHTMLParser(html).css("tr"):
        cells = [re.sub(r"\s+", "", td.text()) for td in tr.css("td")]
        if cells and cells[0] in VERIFY_NAMES:
            matches.setdefault(VERIFY_NAMES[cells[0]], []).append(cells)
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


def verify_main():
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


def verify(argv=None):
    """Compare calendar-derived W/L/D/R/RA with independent official annual tables.
    """
    verify_main()


# ==== inning_pilot（旧 inning_pilot.py）

INNING_PILOT_DOC = """Three-game acquisition feasibility only, not a team-comparison sample."""

INNING_PILOT_NAMES={'中日':'d','東京ヤクルト':'s','巨人':'g','読売':'g','阪神':'t','広島':'c','広島東洋':'c','横浜DeNA':'db','DeNA':'db'}


def norm(s):
    return ''.join(unicodedata.normalize('NFKC',s).split())


def cell(raw,side,last):
    value=norm(raw)
    if value=='X':
        if side!='home' or not last:
            raise ValueError('unplayed cell at unexpected position')
        return dict(runs=None,played=False,completed=False)
    m=re.fullmatch(r'(\d+)([xX]?)',value)
    if not m or (m[2] and (side!='home' or not last)):
        raise ValueError(f'unknown inning cell: {raw!r}')
    return dict(runs=int(m[1]),played=True,completed=not bool(m[2]))


def inning_pilot_parse(html,g):
    root=LexborHTMLParser(html)
    candidates=[r for r in root.css('#gmdivresult tr') if r.css_first('.gmscoreteam')]
    if len(candidates)!=2:
        raise ValueError('expected exactly two score rows')
    result=[]
    for row,side,totalkey in zip(candidates,['away','home'],['as','hs']):
        name=norm(row.css_first('.gmscoreteam').text())
        if INNING_PILOT_NAMES.get(name)!=g[side]:
            raise ValueError(f'team identity mismatch: {name}')
        vals=[norm(c.text()) for c in row.css('td.gmscore')]
        if len(vals)!=13 or vals[9]!='-':
            raise ValueError('pilot supports exactly nine innings and R/H/E columns')
        parsed=[cell(v,side,i==8) for i,v in enumerate(vals[:9])]
        if not vals[10].isdigit() or sum(c['runs'] or 0 for c in parsed)!=int(vals[10]) or int(vals[10])!=g[totalkey]:
            raise ValueError('inning total does not match verified final score')
        result.append(dict(team=g[side],side=side,cells=parsed))
    return result


def inning_pilot_main(argv=None):
    ap=argparse.ArgumentParser(description=INNING_PILOT_DOC);ap.add_argument('--fetch',action='store_true');args=ap.parse_args(argv)
    data=ROOT/'data/observations/r001/games.jsonl'
    expected='7b1b6dfdd41cafbdf851cdb8bcd2cae981adb338570dd66de75881bfe35ee8d9'
    if sha(data)!=expected:
        raise ValueError('pilot source dataset changed')
    games=[json.loads(s) for s in data.read_text().splitlines()]
    selected=[g for g in games if g['date']=='2024-03-29' and g['home'] in {'g','s','db'}]
    if len(selected)!=3:
        raise ValueError('pilot selection changed')
    cache=Cache(ROOT/'data/raw/r001_inning_pilot')
    if args.fetch:
        import httpx
        with httpx.Client(headers={'User-Agent':UA},timeout=45,follow_redirects=True) as client:
            fetch=PoliteFetcher(cache,wait=3,client=client)
            for g in selected:
                fetch.get(g['key'],g['href'],'2024')
    latest=cache.latest();rows=[];receipts=[];unknown=[]
    for g in selected:
        e=latest[g['key']];html=cache.body(e)
        if e['status']!=200 or hashlib.sha256(html.encode()).hexdigest()!=e['sha256']:
            raise ValueError('cached response mismatch')
        try:
            rows.extend(dict(game=g['key'],**r) for r in inning_pilot_parse(html,g))
        except ValueError as err:
            unknown.append(dict(game=g['key'],error=str(err)))
        receipts.append({k:e[k] for k in ['key','url','status','sha256','bytes','fetched_at','code_version']})
    local=ROOT/'data/observations/r001_inning_pilot';local.mkdir(parents=True,exist_ok=True)
    (local/'unknown.json').write_text(json.dumps(unknown,ensure_ascii=False,indent=2)+'\n')
    if unknown:
        raise ValueError('unknown records saved; pilot stopped')
    (local/'innings.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    played=[c for r in rows for c in r['cells'] if c['played']]
    result=dict(purpose='format feasibility only; no team trend inference',games=len(selected),team_games=len(rows),
                played_half_innings=len(played),unplayed_cells=sum(not c['played'] for r in rows for c in r['cells']),
                incomplete_played_cells=sum(not c['completed'] for c in played),unknown=0,all_final_scores_match=True,
                sources=receipts,input_sha256=expected,script_sha256=sha(__file__),
                protocol_sha256=sha(HERE/'SCORING_SPREAD_PROTOCOL.md'),exit_code=0)
    (HERE/'outputs/inning_pilot_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='sources'},ensure_ascii=False))


def inning_pilot(argv=None):
    """inning_pilot.py の入口（説明は INNING_PILOT_DOC）。
    """
    try:
        inning_pilot_main(argv)
    except (FileNotFoundError,KeyError) as e:
        print(str(e),file=sys.stderr);sys.exit(66)
    except ValueError as e:
        print(str(e),file=sys.stderr);sys.exit(65)


# ==== 入口
COMMANDS = {
    "collect": collect,
    "observe": observe,
    "verify": verify,
    "inning_pilot": inning_pilot,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="fetch.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"fetch.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
