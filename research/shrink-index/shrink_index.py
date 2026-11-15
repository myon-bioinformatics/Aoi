#!/usr/bin/env python3
"""縮む商品の「総量」指標（青いプロジェクト第2弾 ②: カントリーマアム指標）。

総量 q = 枚数 n x 1枚の重さ w（g）。総量が g で直接書かれていればそれを使う。
同じ年に両方がわかる年だけ q を出す。補間も、前の年の持ち越しもしない（出典が「2014年〜」のように
期間で述べている場合は、その期間の行を出典の側で明示して置く）。1枚の重さが無い年は、
--assume-weight で仮置きでき、その年は ASSUMED と表示する（観測値が仮置きに勝つ）。

  s_t = q_t / q_ref                          水準（ref は q がわかる最初の年）
  r   = (log1p(q_j) - log1p(q_i)) / (j - i)  q がわかる隣り合う2点の間の年あたり変化（区間。段か傾きかは分けない）
  m_t = log1p(q_t) - log1p(q_d)              危険水準 q_d との差（正なら上、0 以下なら危険域）
  D_t = 1 / (1 + exp(m_t))                   危険への近さ (0,1)。q_d で 0.5。q_t = 0 でも定義できる
  u_t = (p_t / q_t) / (p_ref / q_ref)        単価の水準（値段が据え置きで q が減ると上がる）

q_d（人が食べられない大きさ）はデータから決めない。--danger-total で人が置く。
仮置きを除き、観測から総量がわかる年が MIN_POINTS に満たないときは「判断材料が足りない」と表示する。
予測は出さない。--whatif は「この割合が続いたら」の計算で、予測ではない（WHAT-IF と表示する）。
直線回帰も、丸めた数字での結論も、ここには置かない。

ゼロ・NaN・無限大・空欄は、読み込み時（load）と計算結果（compute）で、出なかったときも含めて必ず
'[zero/NaN log] ...' として出力する。値は変えず、ε への置き換えもしない（0 が出た所には、置くならどうするかを
'[ε] ...' の行で知らせる。ε の決め方は ZeroNaNLog の説明）。
  ZERO / NaN / INF: 記録して値はそのまま使う / BLANK: 数として読めない行は使わず記録する
  SKIPPED: ゼロのため出さなかった（水準・単価）

usage:
  python research/shrink-index/shrink_index.py [CSV] --product shrink:countrymaam_family_vanilla_cocoa
      [--danger-total G] [--assume-weight YEAR:G,YEAR:G] [--whatif]

終了コード: 0 = 実行できた / 65 = 同じ年に値が食い違う / 66 = その商品の行がない
"""
import argparse
import collections
import csv
import math
import random
import sys

DEFAULT_CSV = 'research/shrink-index/countrymaam_observed_vertical.csv'
MIN_POINTS = 5   # 仮置きを除く観測総量の年がこれより少ないと判断を保留する（先に宣言。結果を見て変えない）


def kind_of(x):
    """'NaN' / 'INF' / 'ZERO'、どれでもなければ None。"""
    if x is None:
        return None
    if x != x:
        return 'NaN'
    if x in (math.inf, -math.inf):
        return 'INF'
    return 'ZERO' if x == 0 else None


class ZeroNaNLog:
    """ゼロ・NaN・無限大・空欄・ゼロでのスキップが出たことを数え、必ず出力する。値は変えない。
    （research/bigmac-ruler/staple_bigmac_check.py もここから読む。ε の置き方を変えるときは、ここ 1 か所で変える）

    ε の決め方（2026-11-14）: 0 < ε < 1 の小さな値で、0 の代わりに置く。
      - 置き換えるのは 0 だけ。NaN・無限大・空欄は「欠けている」ので置き換えない
      - 大きさが 1 前後の量（確率・0〜1 の比・基準年に対する水準）には ε のまま。単位や桁のある量（g・円・個・%）には
        「典型値 × ε」か、log(1+x) の後に置く（定規の最小目盛りは定規の長さで決まるのと同じ）
      - 符号のある量（変化率・係数・相関）は置き換えない（+ε にすると向きが付く）
      - 値は決め打ちしない。A×10^-N の A と N を乱数で選んで何通りか試し、結論が変わらないことを確かめる
        （research/epsilon-generality の仕組み）
    ここでは置き換えず、0 が出た所に「[ε]」の行で置き方を知らせるだけ。この 2 本は log(1+x) で最初から 0 を
    避けているので、置き換えは要らない。"""

    EPS_PLAIN = 'ε のまま（大きさが 1 前後の量）'
    EPS_SCALED = '典型値×ε（単位や桁のある量。log(1+x) の後なら ε のまま）'
    EPS_SIGNED = '置き換えない（符号のある量。+ε にすると向きが付く）'

    def __init__(self):
        self.count = collections.Counter()
        self.examples = collections.defaultdict(list)
        self.eps = collections.Counter()          # (stage, name, 置き方) -> 0 の数

    def add(self, stage, name, kind, where='', scaled=False, signed=False):
        """scaled: 単位や桁のある量か。signed: 符号のある量か（0 の置き方を知らせるのに使う。値は変えない）。"""
        key = (stage, name, kind)
        self.count[key] += 1
        if len(self.examples[key]) < 3:
            self.examples[key].append(where if isinstance(where, str) else ' '.join(map(str, where)))
        if kind == 'ZERO':
            self.eps[(stage, name, self.EPS_SIGNED if signed else self.EPS_SCALED if scaled else self.EPS_PLAIN)] += 1

    def scan(self, stage, name, values, scaled=False, signed=False):
        """{場所: 値} か値のリストを調べて、ゼロ・NaN・無限大を記録する。signed は真偽か、場所を受けて真偽を返す関数。"""
        for where, x in (values.items() if isinstance(values, dict) else enumerate(values)):
            kind = kind_of(x)
            if kind:
                self.add(stage, name, kind, str(where), scaled, signed(str(where)) if callable(signed) else signed)

    def lines(self, stage):
        rows = [(k, n) for k, n in sorted(self.count.items()) if k[0] == stage]
        if not rows:
            return ['[zero/NaN log] %s: none' % stage]
        return ['[zero/NaN log] %s: %s %s x%d  e.g. %s' % (stage, k[1], k[2], n, ', '.join(self.examples[k]))
                for k, n in rows] + ['[ε] %s: %s ZERO x%d -> %s' % (stage, k[1], n, k[2])
                                     for k, n in sorted(self.eps.items()) if k[0] == stage]


def load(path, log=None):
    """縦持ちCSV -> {商品: {測定: {年: 値}}}。variable は '<商品>:<測定>'。同じ年の値が食い違えば ValueError。
    ゼロ・NaN・無限大は log に記録して値はそのまま読む。数として読めない値（空欄など）は BLANK として記録し、その行は使わない。"""
    log = ZeroNaNLog() if log is None else log
    out = collections.defaultdict(lambda: collections.defaultdict(dict))
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            product, measure = r['variable'].rsplit(':', 1)
            y = int(r['year'])
            try:
                v = float(r['value'])
            except (TypeError, ValueError):
                log.add('load', r['variable'], 'BLANK', str(y))
                continue
            kind = kind_of(v)
            if kind:
                log.add('load', r['variable'], kind, str(y), scaled=True)     # 枚数・g・円
            old = out[product][measure].get(y)
            if old is not None and old != v and not (old != old and v != v):   # NaN 同士は食い違いにしない
                raise ValueError('conflict %s:%s %d: %g vs %g' % (product, measure, y, old, v))
            out[product][measure][y] = v
    return out


def totals(m, assume=None):
    """({年: 総量 g}, 仮置きを使った年の集合)。観測された 1枚の重さが、仮置きより優先される。"""
    observed = m.get('grams_per_piece', {})
    w = dict(assume or {})
    w.update(observed)
    q = {y: n * w[y] for y, n in m.get('pieces', {}).items() if y in w}
    q.update(m.get('total_g', {}))
    assumed = {y for y in q if y in (assume or {}) and y not in observed and y not in m.get('total_g', {})}
    return dict(sorted(q.items())), assumed


def level(q):
    """q がわかる最初の年を 1 とした水準。基準が 0 なら None。"""
    if not q:
        return {}
    base = q[min(q)]
    return None if base == 0 else {y: v / base for y, v in q.items()}


def rates(q):
    """[(年i, 年j, 年あたり変化)]。q がわかる隣り合う2点だけを結ぶ（間の年は作らない）。log1p でゼロを避ける。"""
    ys = sorted(q)
    return [(a, b, (math.log1p(q[b]) - math.log1p(q[a])) / (b - a)) for a, b in zip(ys, ys[1:])]


def margin(x, x_d):
    return math.log1p(x) - math.log1p(x_d)


def danger(x, x_d):
    return 1.0 / (1.0 + math.exp(margin(x, x_d)))


def evidence(q, min_points=MIN_POINTS):
    """渡された観測総量の年数による点数判定。呼出し側で仮置きを除く。"""
    return 'sufficient' if len(q) >= min_points else 'insufficient'


def whatif_years(x, x_d, rate):
    """年あたり rate (< 0) の変化が続いたら、x が x_d 以下になるまでの年数。予測ではない。減っていなければ None。"""
    if rate >= 0:
        return None
    if x <= x_d:
        return 0.0
    return (math.log1p(x) - math.log1p(x_d)) / -rate


def unit_price_index(price, q):
    """{年: 単価の水準}。値段と総量が両方わかる最初の年が基準。総量が 0 の年は出さない。"""
    ys = [y for y in sorted(price) if y in q and q[y] > 0]
    if not ys:
        return {}
    base = price[ys[0]] / q[ys[0]]
    return {y: (price[y] / q[y]) / base for y in ys}


def _r(d, nd=4):
    return {k: round(v, nd) for k, v in d.items()}


def report(product, m, assume=None, danger_total=None, whatif=False, log=None):
    log = ZeroNaNLog() if log is None else log
    q, assumed = totals(m, assume)
    pieces = dict(sorted(m.get('pieces', {}).items()))
    print(product)
    print('pieces        ', pieces)
    print('g per piece   ', dict(sorted(m.get('grams_per_piece', {}).items())))
    print('total g       ', _r(q, 2), ('  ASSUMED g/piece in %s' % sorted(assumed)) if assumed else '')
    log.scan('compute', 'total g', q, scaled=True)
    observed_q = {y: v for y, v in q.items() if y not in assumed}
    print('evidence      %s (%d observed points, MIN_POINTS=%d)' % (
        evidence(observed_q), len(observed_q), MIN_POINTS))
    if pieces:
        pl = level(pieces)
        print('pieces level  ', _r(pl) if pl else None, '(pieces only)')
        if pl is None:
            log.add('compute', 'pieces level', 'SKIPPED', 'base is 0 in %d' % min(pieces))
        else:
            log.scan('compute', 'pieces level', pl)
    sl = level(q)
    print('total level   ', _r(sl) if sl else None)
    if q and sl is None:
        log.add('compute', 'total level', 'SKIPPED', 'base q is 0 in %d' % min(q))
    elif sl:
        log.scan('compute', 'total level', sl)
    rs = rates(q)
    print('rate per year ', [(a, b, round(r, 5)) for a, b, r in rs])
    log.scan('compute', 'rate per year', {'%d-%d' % (a, b): r for a, b, r in rs}, signed=True)
    if danger_total is not None:
        dd = {y: danger(v, danger_total) for y, v in q.items()}
        print('danger D_t    ', _r(dd), '(q_d=%g g, set by hand)' % danger_total)
        log.scan('compute', 'danger D_t', dd)
    if m.get('price'):
        up = unit_price_index(m['price'], q)
        print('unit price    ', _r(up))
        for y in sorted(m['price']):
            if y in q and q[y] == 0:
                log.add('compute', 'unit price', 'SKIPPED', 'total q is 0 in %d' % y)
        log.scan('compute', 'unit price', up)
    if whatif:
        if danger_total is None:
            print('WHAT-IF: needs --danger-total')
        else:
            last = max(q) if q else None
            for a, b, r in rates(q):
                yrs = whatif_years(q[last], danger_total, r)
                print('WHAT-IF (not a forecast): if the %d-%d rate (%.4f/yr) continued from %d: %s' % (
                    a, b, r, last, 'q is not falling' if yrs is None else '%.1f years to q_d' % yrs))
    print('\n'.join(log.lines('compute')))
    return q, assumed


# ==== 合成データ（--synthetic）
# 仮想の縮む商品（合成データ）を作り、指標が既知の真値どおりに動くか確認する。
#
# SYNTHETIC: 生成したデータであり、観測値ではない。実データの結論として扱わない。
# 完了条件・合格条件には使わず、推奨条件（命題を試す前の足場）として用意する。
# 生成規則は下の PATTERNS に固定する（実データの結果を見て選ばない。値は構造を網羅する丸い格子）。
# 規則を直したくなったら、直さずに新しい ID で足す。詳細は SHRINK.md。
#
# usage:
#   python research/shrink-index/shrink_index.py --synthetic [OUT] [--check]
#     --check   各パターンの指標（総量・水準・危険への近さ・単価・判断材料）を表示する


SYNTHETIC_DEFAULT_OUT = 'research/shrink-index/synthetic_shrink_vertical.csv'
SYNTHETIC_SEED = 20261024
SYNTHETIC_Y0, SYNTHETIC_Y1 = 1992, 2024
SYNTHETIC_Q_DANGER = 60.0   # check() の例示用の危険水準（g）。人が食べられない大きさの推定ではない
SYNTHETIC_PATTERNS = [      # (ID, 名前, ねらい)
    ('M1', 'gradual_slide', '枚数は一定、1枚の重さが年2%ずつ縮む（ありえる）'),
    ('M2', 'stepwise_pieces', '1枚は一定、枚数が6年ごとに2枚ずつ減る（段）'),
    ('M3', 'accelerating', '1枚の重さの縮みが加速する。q_d を割る年がある'),
    ('M4', 'pieces_nonmonotone', '枚数は増減をくり返し、1枚の重さは縮む。枚数だけで見ると誤る'),
    ('M5', 'price_fixed_quantity_down', 'M1と同じ縮み方で値段は据え置き。単価が上がる'),
    ('M6', 'growth_impossible', '1枚の重さが増える（縮む商品ではない）'),
    ('M7', 'hits_zero_nonexistent', '1枚の重さが最終年に 0 になる（存在しない）'),
    ('M8', 'rounded_noisy_sparse', 'M1にノイズ、1枚の重さを0.5gに丸め、4点だけ観測'),
]


def synthetic_generate(idx, pid):
    """({測定: {年: 値}}, 説明)。乱数を使うのは M8 だけ（seed = SEED + idx）。"""
    n, w, p = {}, {}, {}
    rng = random.Random(SYNTHETIC_SEED + idx)
    years = [1992, 2002, 2012, 2024] if pid == 'M8' else range(SYNTHETIC_Y0, SYNTHETIC_Y1 + 1)
    for y in years:
        t = y - SYNTHETIC_Y0
        if pid == 'M1':
            n[y], w[y] = 30, 10 * math.exp(-0.02 * t)
        elif pid == 'M2':
            n[y], w[y] = 30 - 2 * (t // 6), 10.0
        elif pid == 'M3':
            n[y], w[y] = 30, 10 * math.exp(-0.002 * t * t)
        elif pid == 'M4':
            n[y], w[y] = 30 + 3 * ((t // 8) % 2), 10 * math.exp(-0.015 * t)
        elif pid == 'M5':
            n[y], w[y], p[y] = 30, 10 * math.exp(-0.02 * t), 300.0
        elif pid == 'M6':
            n[y], w[y] = 30, 10 * math.exp(0.01 * t)
        elif pid == 'M7':
            n[y], w[y] = 30, 10 * (1 - t / (SYNTHETIC_Y1 - SYNTHETIC_Y0))
        elif pid == 'M8':
            n[y], w[y] = 30, round(10 * math.exp(-0.02 * t + rng.gauss(0, 0.05)) * 2) / 2
        else:
            raise ValueError(pid)
    out = {'pieces': n, 'grams_per_piece': w}
    if p:
        out['price'] = p
    return out


SYNTHETIC_UNITS = {'pieces': 'pieces per bag (synthetic)', 'grams_per_piece': 'g per piece (synthetic)',
         'price': 'JPY per bag (synthetic)'}


def synthetic_write_vertical(path):
    """縦持ち形式で書く。観測値のファイルとは混ぜない（country・variable・unit・source に SYNTHETIC を残す）。"""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['country', 'date', 'year', 'variable', 'value', 'unit', 'source', 'note', 'estimated_value'])
        for i, (pid, name, aim) in enumerate(SYNTHETIC_PATTERNS):
            for measure, series in synthetic_generate(i, pid).items():
                for y, v in series.items():
                    # source の旧ファイル名は、既存 CSV とバイト一致させるための記録名（今は --synthetic が作る）
                    w.writerow(['SYN', '%d-01-01' % y, y, 'synthetic_shrink:%s_%s:%s' % (pid, name, measure),
                                '%.6g' % v, SYNTHETIC_UNITS[measure], 'SYNTHETIC synthetic_shrink.py seed=%d' % (SYNTHETIC_SEED + i),
                                aim, ''])


def synthetic_check(verbose=True):
    """各パターンを指標に通した行を返す。"""
    rows = []
    for i, (pid, name, _aim) in enumerate(SYNTHETIC_PATTERNS):
        m = synthetic_generate(i, pid)
        q, _ = totals(m)
        lv, pl = level(q), level(m['pieces'])
        d = {y: danger(v, SYNTHETIC_Q_DANGER) for y, v in q.items()}
        up = unit_price_index(m['price'], q) if 'price' in m else {}
        rs = [r for _a, _b, r in rates(q)]
        rows.append(dict(
            id=pid, name=name, points=len(q), evidence=evidence(q),
            total_last=lv[max(lv)] if lv else None, pieces_last=pl[max(pl)] if pl else None,
            rate_min=min(rs) if rs else None, rate_max=max(rs) if rs else None,
            d_last=d[max(d)], first_year_in_zone=next((y for y in sorted(d) if d[y] >= 0.5), None),
            unit_price_last=up[max(up)] if up else None))
    if verbose:
        print('q_d=%g g (illustrative), MIN_POINTS=%d' % (SYNTHETIC_Q_DANGER, MIN_POINTS))
        print('%-3s %-26s %-4s %-13s %-12s %-12s %-6s %-9s %s' % (
            'id', 'name', 'pts', 'evidence', 'total last', 'pieces last', 'D last', 'in zone', 'unit price last'))
        for r in rows:
            f = lambda x, nd=3: '-' if x is None else ('%.*f' % (nd, x))
            print('%-3s %-26s %-4d %-13s %-12s %-12s %-6s %-9s %s' % (
                r['id'], r['name'], r['points'], r['evidence'], f(r['total_last']), f(r['pieces_last']),
                f(r['d_last'], 2), r['first_year_in_zone'] or '-', f(r['unit_price_last'])))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('csv', nargs='?', default=DEFAULT_CSV)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--product', help='例: shrink:countrymaam_family_vanilla_cocoa')
    mode.add_argument('--synthetic', nargs='?', const=SYNTHETIC_DEFAULT_OUT, metavar='OUT',
                      help='🧪 合成データを OUT に書く（既定 %s）' % SYNTHETIC_DEFAULT_OUT)
    ap.add_argument('--check', action='store_true', help='🧪 --synthetic: 各パターンの指標を出す')
    ap.add_argument('--danger-total', type=float, default=None, metavar='G')
    ap.add_argument('--assume-weight', default=None, metavar='YEAR:G,YEAR:G')
    ap.add_argument('--whatif', action='store_true')
    args = ap.parse_args(argv)
    if args.synthetic:
        synthetic_write_vertical(args.synthetic)
        print('wrote %s: %d patterns' % (args.synthetic, len(SYNTHETIC_PATTERNS)))
        if args.check:
            synthetic_check()
        return 0
    log = ZeroNaNLog()
    try:
        data = load(args.csv, log)
    except ValueError as e:
        print('\n'.join(log.lines('load')))
        print(e, file=sys.stderr)
        return 65
    print('\n'.join(log.lines('load')))      # 読み込み直後に出す（後の計算で止まっても残る）
    if args.product not in data:
        print('no rows for %s' % args.product, file=sys.stderr)
        return 66
    assume = None
    if args.assume_weight:
        assume = {int(a): float(b) for a, b in (p.split(':') for p in args.assume_weight.split(','))}
    report(args.product, data[args.product], assume, args.danger_total, args.whatif, log)
    return 0


if __name__ == '__main__':
    sys.exit(main())
