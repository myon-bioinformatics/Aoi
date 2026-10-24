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
q がわかる点が MIN_POINTS に満たないときは「判断材料が足りない」と表示する。
予測は出さない。--whatif は「この割合が続いたら」の計算で、予測ではない（WHAT-IF と表示する）。
直線回帰も、丸めた数字での結論も、ここには置かない。

usage:
  python research/shrink-index/shrink_index.py [CSV] --product shrink:countrymaam_family_vanilla_cocoa
      [--danger-total G] [--assume-weight YEAR:G,YEAR:G] [--whatif]

終了コード: 0 = 実行できた / 65 = 同じ年に値が食い違う / 66 = その商品の行がない
"""
import argparse
import collections
import csv
import math
import sys

DEFAULT_CSV = 'research/shrink-index/countrymaam_observed_vertical.csv'
MIN_POINTS = 5   # q がわかる年がこれより少ないと判断を保留する（先に宣言。結果を見て変えない）


def load(path):
    """縦持ちCSV -> {商品: {測定: {年: 値}}}。variable は '<商品>:<測定>'。同じ年の値が食い違えば ValueError。"""
    out = collections.defaultdict(lambda: collections.defaultdict(dict))
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            product, measure = r['variable'].rsplit(':', 1)
            y, v = int(r['year']), float(r['value'])
            old = out[product][measure].get(y)
            if old is not None and old != v:
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


def report(product, m, assume=None, danger_total=None, whatif=False):
    q, assumed = totals(m, assume)
    pieces = dict(sorted(m.get('pieces', {}).items()))
    print(product)
    print('pieces        ', pieces)
    print('g per piece   ', dict(sorted(m.get('grams_per_piece', {}).items())))
    print('total g       ', _r(q, 2), ('  ASSUMED g/piece in %s' % sorted(assumed)) if assumed else '')
    print('evidence      %s (%d known points, MIN_POINTS=%d)' % (evidence(q), len(q), MIN_POINTS))
    if pieces:
        pl = level(pieces)
        print('pieces level  ', _r(pl) if pl else None, '(pieces only)')
    sl = level(q)
    print('total level   ', _r(sl) if sl else None)
    print('rate per year ', [(a, b, round(r, 5)) for a, b, r in rates(q)])
    if danger_total is not None:
        print('danger D_t    ', _r({y: danger(v, danger_total) for y, v in q.items()}), '(q_d=%g g, set by hand)' % danger_total)
    if m.get('price'):
        print('unit price    ', _r(unit_price_index(m['price'], q)))
    if whatif:
        if danger_total is None:
            print('WHAT-IF: needs --danger-total')
        else:
            last = max(q) if q else None
            for a, b, r in rates(q):
                yrs = whatif_years(q[last], danger_total, r)
                print('WHAT-IF (not a forecast): if the %d-%d rate (%.4f/yr) continued from %d: %s' % (
                    a, b, r, last, 'q is not falling' if yrs is None else '%.1f years to q_d' % yrs))
    return q, assumed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('csv', nargs='?', default=DEFAULT_CSV)
    ap.add_argument('--product', required=True, help='例: shrink:countrymaam_family_vanilla_cocoa')
    ap.add_argument('--danger-total', type=float, default=None, metavar='G')
    ap.add_argument('--assume-weight', default=None, metavar='YEAR:G,YEAR:G')
    ap.add_argument('--whatif', action='store_true')
    args = ap.parse_args(argv)
    try:
        data = load(args.csv)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 65
    if args.product not in data:
        print('no rows for %s' % args.product, file=sys.stderr)
        return 66
    assume = None
    if args.assume_weight:
        assume = {int(a): float(b) for a, b in (p.split(':') for p in args.assume_weight.split(','))}
    report(args.product, data[args.product], assume, args.danger_total, args.whatif)
    return 0


if __name__ == '__main__':
    sys.exit(main())
