"""All published annual *team* tables, 1950 onward; no individual records.

2005+: detailed standings/batting/pitching/fielding plus yearly summary as a
cross-source check. 1950-2004: the team tables actually published in the yearly
summary. Missing historical columns are absent/null, never invented as zero.
"""
from __future__ import annotations

from collections import defaultdict
import re
import unicodedata
from urllib.parse import urlsplit

from selectolax.lexbor import LexborHTMLParser
from blueprobe import new_report, normalize

NAME = 'npb_team_annual'
DETAIL = re.compile(r'/bis/(\d{4})/stats/(std|tmb|tmp|tmf)_([cp])\.html')
ARCHIVE = re.compile(r'/bis/yearly/(centralleague|pacificleague)_(\d{4})\.html')
KNOWN = set('チーム 試合 勝利 敗北 引分 勝率 差 ゲーム差 ホーム ロード 交流戦 半期順位 打率 打席 打数 得点 安打 二塁打 三塁打 本塁打 塁打 打点 盗塁 盗塁刺 犠打 犠飛 四球 故意四 故意四球 死球 三振 併殺打 長打率 出塁率 防御率 セーブ ホールド HP 完投 完封勝 無四球 打者 投球回 奪三振 暴投 ボーク 失点 自責点 守備率 守備機会 刺殺 補殺 失策 併殺/参加 併殺/球団 捕逸'.split())
ALIASES = {
    'g': ['巨人','読売','読売ジャイアンツ'], 'd':['中日','中日ドラゴンズ'],
    't':['阪神','阪神タイガース'], 'db':['横浜','DeNA','横浜ベイスターズ','横浜DeNAベイスターズ'],
    's':['ヤクルト','ヤクルトスワローズ','東京ヤクルトスワローズ'], 'c':['広島','広島東洋カープ'],
    'h':['ソフトバンク','福岡ソフトバンクホークス'], 'f':['日本ハム','北海道日本ハムファイターズ'],
    'b':['オリックス','オリックスバファローズ'], 'e':['楽天','東北楽天ゴールデンイーグルス'],
    'l':['西武','西武ライオンズ','埼玉西武ライオンズ'], 'm':['ロッテ','千葉ロッテマリーンズ'],
}


def compact(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s)).replace('・','')


def team_id(name):
    token = compact(name)
    for key, aliases in ALIASES.items():
        if token in aliases:
            return key
    # Historical names are source identities, not guessed franchise continuity.
    return 'historical:' + token


def pages(years):
    out = []
    for year in years:
        if not 1950 <= year <= 9999:
            raise ValueError('two-league annual source starts at 1950')
        for lg, league in [('c','centralleague'),('p','pacificleague')]:
            if year >= 2005:
                for cat in ['std','tmb','tmp','tmf']:
                    out.append((f'{year}_{lg}_{cat}',f'https://npb.jp/bis/{year}/stats/{cat}_{lg}.html',str(year)))
            out.append((f'{year}_{lg}_archive',f'https://npb.jp/bis/yearly/{league}_{year}.html',str(year)))
    return out


def _rows(table):
    for child in table.iter():
        if child.tag == 'tr':
            yield child
        elif child.tag in ('tbody','thead','tfoot'):
            yield from (r for r in child.iter() if r.tag == 'tr')


def _grid(table):
    """Expand physical spans before interpreting headers; nested tables stay in a cell."""
    grid = {}
    width = 0
    row_count = 0
    for i, row in enumerate(_rows(table)):
        row_count = i+1
        col = 0
        for cell in row.iter():
            if cell.tag not in ('td','th'):
                continue
            while (i,col) in grid:
                col += 1
            rs, cs = int(cell.attributes.get('rowspan','1')), int(cell.attributes.get('colspan','1'))
            if not 1 <= rs <= 100 or not 1 <= cs <= 100:
                raise ValueError('unbounded table span')
            value = normalize(cell.text(deep=True))
            for a in range(rs):
                for b in range(cs):
                    if (i+a,col+b) in grid:
                        raise ValueError('overlapping table span')
                    grid[i+a,col+b] = value
            col += cs
            width = max(width,col)
    return [[grid.get((i,c),'') for c in range(width)] for i in range(row_count)]


def _header(value):
    token = compact(value).replace('｜','ー').replace('|','ー').replace('守機備会','守備機会')
    return {'ホール': 'ホールド', '併殺参加':'併殺/参加', '併殺球団':'併殺/球団', '順位前後期期':'半期順位'}.get(token, token)


def _value(raw):
    token = compact(raw)
    if token in ('','-','--','---','***'):
        return None
    if re.fullmatch(r'\d+',token):
        return int(token)
    if re.fullmatch(r'(?:\d+)?\.\d+',token):
        return float(token)
    if re.fullmatch(r'\d+-\d+(?:\(\d+\))?',token):
        a,b,t = re.fullmatch(r'(\d+)-(\d+)(?:\((\d+)\))?',token).groups()
        return dict(W=int(a),L=int(b),T=int(t or 0))
    return token


def parse(html, url=''):
    out = new_report()
    if urlsplit(url).hostname != 'npb.jp':
        raise ValueError('expected official npb.jp source URL')
    path = urlsplit(url).path
    detail, archive = DETAIL.fullmatch(path), ARCHIVE.fullmatch(path)
    if not detail and not archive:
        raise ValueError('not an annual team source URL')
    year = int(detail[1] if detail else archive[2])
    lg = detail[3].upper() if detail else ('C' if archive[1]=='centralleague' else 'P')
    source = 'detail' if detail else 'archive'
    category_count = defaultdict(int)
    for table in LexborHTMLParser(html).css('table'):
        grid = _grid(table)
        if not grid or not grid[0] or compact(grid[0][0]) != 'チーム':
            continue
        header_rows = 1
        while header_rows < len(grid) and compact(grid[header_rows][0]) == 'チーム':
            header_rows += 1
        headers = []
        for c in range(len(grid[0])):
            labels = []
            for row in grid[:header_rows]:
                token = _header(row[c])
                if token and token not in labels:
                    labels.append(token)
            headers.append('/'.join(labels))
        labels = set(headers)
        cat = ('batting' if '打率' in labels else 'pitching' if '防御率' in labels else
               'fielding' if '守備率' in labels else 'standings' if {'勝利','敗北','引分'} <= labels else None)
        if not cat:
            out['unknown'].append(dict(key=f'{year}:{lg}:header',raw=' | '.join(headers)))
            continue
        category_count[cat] += 1
        if cat == 'standings' and category_count[cat] > 1:
            cat = 'interleague'
        unknown = [h for h in headers if h and h not in KNOWN and not h.startswith('対')]
        if unknown:
            out['unknown'].append(dict(key=f'{year}:{lg}:{cat}:header',raw=' | '.join(unknown)))
        if len([h for h in headers if h]) != len(set(h for h in headers if h)):
            out['unknown'].append(dict(key=f'{year}:{lg}:{cat}:duplicate_header',raw=' | '.join(headers)))
            continue
        for ordinal, row in enumerate(grid[header_rows:],1):
            if not row[0]:
                continue
            values, raw_values = {}, {}
            try:
                for i,h in enumerate(headers):
                    if not h:
                        if i and headers[i-1] == '投球回':
                            continue  # included as an outs fraction below
                        if row[i].strip():
                            raise ValueError('nonempty unnamed column')
                        continue
                    raw_values[h] = row[i]
                    if h == '半期順位':
                        halves=re.fullmatch(r'(\d+)/(\d+)',compact(row[i]))
                        if not halves:raise ValueError('invalid split-season ranks')
                        values[h]=dict(first_half=int(halves[1]),second_half=int(halves[2]))
                    elif h == '投球回':
                        text = compact(row[i])
                        if i+1 < len(headers) and not headers[i+1]:
                            text += compact(row[i+1])
                        if not re.fullmatch(r'\d+(?:\.[012])?',text):
                            raise ValueError(f'invalid innings: {text}')
                        whole, _, fraction = text.partition('.')
                        values['投球回アウト'] = int(whole)*3+int(fraction or 0)
                        values[h] = text
                    else:
                        values[h] = _value(row[i])
                        if h in KNOWN-{'チーム','差','ゲーム差','ホーム','ロード','交流戦'} and isinstance(values[h],str):
                            raise ValueError(f'unrecognised numeric value for {h}: {row[i]}')
                        integers=KNOWN-{'チーム','差','ゲーム差','ホーム','ロード','交流戦','半期順位','打率','勝率','防御率','長打率','出塁率','守備率'}
                        if h in integers and values[h] is not None and type(values[h]) is not int:
                            raise ValueError(f'integer value required for {h}: {row[i]}')
                name = str(values.pop('チーム'))
                team = team_id(name)
                out['records'].append(dict(key=f'{year}-{lg}-{team}-{source}-{cat}',season=year,
                    league=lg,team=team,team_name=name,source_kind=source,category=cat,
                    source_order=ordinal,values=values,raw_values=raw_values,headers=headers,
                    raw_cells=row,source_url=url))
            except (ValueError,TypeError) as exc:
                out['unknown'].append(dict(key=f'{year}:{lg}:{cat}:{ordinal}',raw=' | '.join(row),error=str(exc)))
    expected = {'standings','batting','pitching'} if archive else {dict(std='standings',tmb='batting',tmp='pitching',tmf='fielding')[detail[2]]}
    missing = expected-set(category_count)
    if missing:
        out['unknown'].append(dict(key=f'{year}:{lg}:missing_tables',raw=','.join(sorted(missing))))
    return out


def group(record):
    return str(record['season'])


def check(records):
    groups = defaultdict(list)
    for r in records:
        groups[(r['season'],r['league'],r['source_kind'],r['category'])].append(r)
    result=[]
    for (year,lg,kind,cat),rows in sorted(groups.items()):
        names=[r['team'] for r in rows]
        ok=len(names)==len(set(names)) and (len(names)==6 if kind=='detail' else len(names)>=6)
        result.append(dict(group=str(year),ok=ok,text=f'{year}/{lg}/{kind}/{cat}: {len(names)} teams '+('OK' if ok else '要確認')))
    return result
