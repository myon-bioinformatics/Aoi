#!/usr/bin/env python3
"""仮想の縮む商品（合成データ）を作り、指標が既知の真値どおりに動くか確認する。

SYNTHETIC: 生成したデータであり、観測値ではない。実データの結論として扱わない。
完了条件・合格条件には使わず、推奨条件（命題を試す前の足場）として用意する。
生成規則は下の PATTERNS に固定する（実データの結果を見て選ばない。値は構造を網羅する丸い格子）。
規則を直したくなったら、直さずに新しい ID で足す。詳細は SHRINK.md。

usage:
  python research/shrink-index/synthetic_shrink.py [--out PATH] [--check]
    --check   各パターンの指標（総量・水準・危険への近さ・単価・判断材料）を表示する
"""
import argparse
import csv
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # python -I でも隣の shrink_index.py を読む
import shrink_index as si  # noqa: E402

DEFAULT_OUT = 'research/shrink-index/synthetic_shrink_vertical.csv'
SEED = 20261024
Y0, Y1 = 1992, 2024
Q_DANGER = 60.0   # check() の例示用の危険水準（g）。人が食べられない大きさの推定ではない
PATTERNS = [      # (ID, 名前, ねらい)
    ('M1', 'gradual_slide', '枚数は一定、1枚の重さが年2%ずつ縮む（ありえる）'),
    ('M2', 'stepwise_pieces', '1枚は一定、枚数が6年ごとに2枚ずつ減る（段）'),
    ('M3', 'accelerating', '1枚の重さの縮みが加速する。q_d を割る年がある'),
    ('M4', 'pieces_nonmonotone', '枚数は増減をくり返し、1枚の重さは縮む。枚数だけで見ると誤る'),
    ('M5', 'price_fixed_quantity_down', 'M1と同じ縮み方で値段は据え置き。単価が上がる'),
    ('M6', 'growth_impossible', '1枚の重さが増える（縮む商品ではない）'),
    ('M7', 'hits_zero_nonexistent', '1枚の重さが最終年に 0 になる（存在しない）'),
    ('M8', 'rounded_noisy_sparse', 'M1にノイズ、1枚の重さを0.5gに丸め、4点だけ観測'),
]


def generate(idx, pid):
    """({測定: {年: 値}}, 説明)。乱数を使うのは M8 だけ（seed = SEED + idx）。"""
    n, w, p = {}, {}, {}
    rng = random.Random(SEED + idx)
    years = [1992, 2002, 2012, 2024] if pid == 'M8' else range(Y0, Y1 + 1)
    for y in years:
        t = y - Y0
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
            n[y], w[y] = 30, 10 * (1 - t / (Y1 - Y0))
        elif pid == 'M8':
            n[y], w[y] = 30, round(10 * math.exp(-0.02 * t + rng.gauss(0, 0.05)) * 2) / 2
        else:
            raise ValueError(pid)
    out = {'pieces': n, 'grams_per_piece': w}
    if p:
        out['price'] = p
    return out


UNITS = {'pieces': 'pieces per bag (synthetic)', 'grams_per_piece': 'g per piece (synthetic)',
         'price': 'JPY per bag (synthetic)'}


def write_vertical(path):
    """縦持ち形式で書く。観測値のファイルとは混ぜない（country・variable・unit・source に SYNTHETIC を残す）。"""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['country', 'date', 'year', 'variable', 'value', 'unit', 'source', 'note', 'estimated_value'])
        for i, (pid, name, aim) in enumerate(PATTERNS):
            for measure, series in generate(i, pid).items():
                for y, v in series.items():
                    w.writerow(['SYN', '%d-01-01' % y, y, 'synthetic_shrink:%s_%s:%s' % (pid, name, measure),
                                '%.6g' % v, UNITS[measure], 'SYNTHETIC synthetic_shrink.py seed=%d' % (SEED + i),
                                aim, ''])


def check(verbose=True):
    """各パターンを指標に通した行を返す。"""
    rows = []
    for i, (pid, name, _aim) in enumerate(PATTERNS):
        m = generate(i, pid)
        q, _ = si.totals(m)
        lv, pl = si.level(q), si.level(m['pieces'])
        d = {y: si.danger(v, Q_DANGER) for y, v in q.items()}
        up = si.unit_price_index(m['price'], q) if 'price' in m else {}
        rs = [r for _a, _b, r in si.rates(q)]
        rows.append(dict(
            id=pid, name=name, points=len(q), evidence=si.evidence(q),
            total_last=lv[max(lv)] if lv else None, pieces_last=pl[max(pl)] if pl else None,
            rate_min=min(rs) if rs else None, rate_max=max(rs) if rs else None,
            d_last=d[max(d)], first_year_in_zone=next((y for y in sorted(d) if d[y] >= 0.5), None),
            unit_price_last=up[max(up)] if up else None))
    if verbose:
        print('q_d=%g g (illustrative), MIN_POINTS=%d' % (Q_DANGER, si.MIN_POINTS))
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
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args(argv)
    write_vertical(args.out)
    print('wrote %s: %d patterns' % (args.out, len(PATTERNS)))
    if args.check:
        check()
    return 0


if __name__ == '__main__':
    sys.exit(main())
