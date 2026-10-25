#!/usr/bin/env python3
"""主食の価格を「ビッグマックの物差し」で見る検証（青いプロジェクト第2弾）。

  b = 主食の価格 / ビッグマック価格      ビッグマック何個分か。通貨が約分されるので為替は使わない
  M = 1人あたり家計消費支出 / ビッグマック価格
  E = 食費割合（USDA ERS）

  log b = a + beta*log E + gamma*log M  を当てはめる。
  gamma = 1 なら b = k*E*M^1 で価格 = k*E*C_pc となり、ビッグマック価格は約分されて意味を持たない。
  gamma < 1 なら、ビッグマックは家計消費支出とは別の情報を持つ。

入力は staple_price_survey の縦持ちCSV（観測値のみ）。換算・補間・単位の統一はしない。
単位は 'per kg' の表記ゆれ（KG / Kg）だけ同一視する。包装単位（5 kg, 1.5 kg など）は使わない。
結果は暫定の読みであり、判定ではない（点数が少ないうちは判断を保留する）。

系列は (国, variable, 単位, source, note) で1本と数える。note には市場・価格種別・品種が入っているので、
別の市場や別の品種は別の系列になり、月をまたいで混ぜない。年平均に必要な月数（MIN_MONTHS）は1本の系列の中で数え、
国ごとに使う系列は1本（年数が最多、同数なら行数が多いもの、なお同数なら系列の文字列が大きいもの）。

ゼロ・NaN・無限大・空欄は、読み込み時（load）と計算結果（compute）で、出なかったときも含めて必ず
'[zero/NaN log]' として出力する。値は変えず、ε への置き換えもしない（置き方は別に決める）。
  ZERO / NaN / INF: 記録して値はそのまま持つ / BLANK: 数として読めない行は使わず記録する
  SKIPPED: 割り算・対数・回帰に渡す前の検査で、0 以下・NaN・inf のため使わなかった入力（どれかを必ず出す）
           ／ゼロのため比を出さなかった / DROPPED: 失敗して捨てた（ブートストラップ）
検査（precheck）は派生計算の前に行う。使えない入力を持ち込んだまま割り算や回帰で止まることはない。

usage:
  python research/bigmac-ruler/staple_bigmac_check.py [SURVEY_CSV] --prefix staple_price:rice
      [--exclude-inflation 2.0] [--panel-out PATH]

終了コード: 0 = 実行できた / 65 = 検査後のパネルでも計算できなかった（docs/propositions.md の 65「データの誤り」。
  compute のログと理由を出してから終わる）/ 66 = パネルが空（同じく 66「入力がない」）
"""
import argparse
import collections
import csv
import math
import sys

import numpy as np

DEFAULT_CSV = 'research/staple-price-survey/staple_survey_vertical.csv'
Y0, Y1 = 2021, 2025
MIN_MONTHS = 6          # 年平均に必要な月数（先に宣言。結果を見て変えない）
SEED, BOOT = 20261024, 4000


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
    （同じ 40 行を research/shrink-index/shrink_index.py にも置いている。共通部品にするかは ε の扱いが決まってから）"""

    def __init__(self):
        self.count = collections.Counter()
        self.examples = collections.defaultdict(list)

    def add(self, stage, name, kind, where=''):
        key = (stage, name, kind)
        self.count[key] += 1
        if len(self.examples[key]) < 3:
            self.examples[key].append(where if isinstance(where, str) else ' '.join(map(str, where)))

    def scan(self, stage, name, values):
        """{場所: 値} か値のリストを調べて、ゼロ・NaN・無限大を記録する。"""
        for where, x in (values.items() if isinstance(values, dict) else enumerate(values)):
            kind = kind_of(x)
            if kind:
                self.add(stage, name, kind, str(where))

    def lines(self, stage):
        rows = [(k, n) for k, n in sorted(self.count.items()) if k[0] == stage]
        if not rows:
            return ['[zero/NaN log] %s: none' % stage]
        return ['[zero/NaN log] %s: %s %s x%d  e.g. %s' % (stage, k[1], k[2], n, ', '.join(self.examples[k]))
                for k, n in rows]


def usable(x):
    """割り算・対数に渡してよい値か。有限で 0 より大きいときだけ True。"""
    return x is not None and math.isfinite(x) and x > 0


def _num(raw, log, name, where):
    """値の文字列 -> float。数として読めなければ BLANK を記録して None（その行は使わない）。
    ゼロ・NaN・無限大は記録して、値はそのまま返す。"""
    try:
        x = float(raw)
    except (TypeError, ValueError):
        log.add('load', name, 'BLANK', where)
        return None
    kind = kind_of(x)
    if kind:
        log.add('load', name, kind, where)
    return x


def load_survey(path, log=None):
    """縦持ちCSVから、ビッグマック・E・家計消費・人口と、主食の行を読む。ゼロ・NaN・空欄は log に記録する。"""
    log = ZeroNaNLog() if log is None else log
    bm = collections.defaultdict(list)
    cur, E, C, POP, staple = {}, {}, {}, {}, []
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            v = r['variable']
            if v.startswith('staple_price'):
                if _num(r['value'], log, 'staple_price', (r['country'], r['year'], v)) is not None:
                    staple.append(r)
                continue
            k = (r['country'], int(r['year']))
            if v == 'bigmac_local_price':
                x = _num(r['value'], log, v, k)
                if x is not None:
                    bm[k].append(x)
                    cur[r['country']] = r['unit']
            elif v == 'engel_share_food':
                x = _num(r['value'], log, v, k)
                if x is not None:
                    E[k] = x / 100
            elif v == 'household_consumption_total_lcu':
                x = _num(r['value'], log, v, k)
                if x is not None:
                    C[k] = x
            elif v == 'population_total':
                x = _num(r['value'], log, v, k)
                if x is not None:
                    POP[k] = x
    BM = {k: sum(v) / len(v) for k, v in bm.items() if len(v) == 2}   # 年内の2点がそろう年のみ
    return dict(BM=BM, BMpts=dict(bm), cur=cur, E=E, C=C, POP=POP, staple=staple)


def _is_per_kg(unit):
    u = unit.lower()
    return u.endswith(' per kg') and u.split(' per ')[-1].strip() == 'kg'


def precheck(S, log=None, y0=Y0, y1=Y1, prefix=''):
    """割り算・対数・回帰に渡す前の検査。0 以下・NaN・inf の入力を使わない（値は変えず、置き換えもしない）。
    解析に使う入力（対象年 y0〜y1、prefix で始まる per kg の主食の行）だけを調べ、外したものは SKIPPED として compute に必ず記録する
    （使わない行は調べない。読み込み時のログ load には、年や品目に関わらず出ている）。外したあとの S を新しく返し、渡された S は変えない。
    ビッグマックは年内の2点がそろっていても、どちらかが使えなければその年は使わない（0 と 100 の平均 50 を作らない）。"""
    log = ZeroNaNLog() if log is None else log
    out = dict(S)

    def keep(name, d):
        good = {}
        for k, x in d.items():
            if not y0 <= k[1] <= y1 or usable(x):
                good[k] = x
            else:
                log.add('compute', 'input.' + name, 'SKIPPED', '%s %s (%g)' % (k[0], k[1], x))
        return good

    staple = []
    for r in S['staple']:
        x = float(r['value'])
        used = y0 <= int(r['year']) <= y1 and r['variable'].startswith(prefix) and _is_per_kg(r['unit'])
        if not used or usable(x):
            staple.append(r)
        else:
            log.add('compute', 'input.staple_price', 'SKIPPED', '%s %s %s (%s)' % (r['country'], r['date'], r['variable'], r['value']))
    out['staple'] = staple
    out['E'] = keep('engel_share_food', S['E'])
    out['C'] = keep('household_consumption_total_lcu', S['C'])
    out['POP'] = keep('population_total', S['POP'])
    if 'BMpts' in S:
        BM, good_pts = {}, {}
        for k, pts in S['BMpts'].items():
            if len(pts) == 2 and not (y0 <= k[1] <= y1 and not all(usable(x) for x in pts)):
                BM[k] = sum(pts) / len(pts)
                good_pts[k] = pts
            elif len(pts) != 2:
                good_pts[k] = pts             # 年内の2点がそろわない年は、これまでどおり使わない（異常値ではない）
            else:
                log.add('compute', 'input.bigmac_local_price', 'SKIPPED', '%s %s (%s)' % (k[0], k[1], ', '.join('%g' % x for x in pts)))
        out['BM'], out['BMpts'] = BM, good_pts      # 外した年は点も残さない（もう一度検査しても同じ記録を重ねない）
    else:
        out['BM'] = keep('bigmac_local_price', S['BM'])
    return out


def series_key(r):
    """系列の識別。国・variable・単位（大文字小文字は同一視）・source・note。note には市場・価格種別・品種が入る。"""
    return (r['country'], r['variable'], r['unit'].lower(), r.get('source', ''), r.get('note', ''))


def build_panel(S, prefix, y0=Y0, y1=Y1, min_months=MIN_MONTHS, log=None):
    """国ごとに1系列（年数が最多、同数なら行数が多いもの、なお同数なら系列の文字列が大きいもの）を選び、国×年のパネルを作る。
    月数は1本の系列の中で数える（別の市場・別の品種の月を足して6か月にしない）。同じ系列の同じ日付が重なれば1か月として平均する。
    パネルに入る数は、すべて有限で 0 より大きい（precheck と、割り算のあとの確認で外す）。"""
    log = ZeroNaNLog() if log is None else log
    S = precheck(S, log, y0, y1, prefix)
    vals = collections.defaultdict(lambda: collections.defaultdict(list))     # (系列, 年) -> {日付: [値]}
    for r in S['staple']:
        if not r['variable'].startswith(prefix) or not _is_per_kg(r['unit']):
            continue
        y = int(r['year'])
        if not y0 <= y <= y1:
            continue
        vals[(series_key(r), y)][r['date']].append(float(r['value']))
    ann = {}
    for k, by_date in vals.items():
        if len(by_date) >= min_months:
            monthly = [sum(xs) / len(xs) for xs in by_date.values()]
            ann[k] = sum(monthly) / len(monthly)
    years, nrows = collections.Counter(), collections.Counter()
    for (sk, _y) in ann:
        years[sk] += 1
    for (sk, _y), by_date in vals.items():
        nrows[sk] += sum(len(xs) for xs in by_date.values())
    cands = collections.defaultdict(list)
    for sk, n in years.items():
        cands[sk[0]].append((n, nrows[sk], sk[1], sk[2], sk[3], sk[4]))
    chosen = {c: max(cs) for c, cs in cands.items()}
    panel, dropped = [], collections.Counter()
    if len(years) > len(chosen):
        dropped['other_series_not_used'] = len(years) - len(chosen)            # 同じ国の別系列（別の市場など）は混ぜず、使わない
    for c, cs in sorted(cands.items()):
        if sum(1 for x in cs if x[:2] == chosen[c][:2]) > 1:
            dropped['series_tie_broken_by_text:%s' % c] += 1                   # 年数も行数も同じ別系列があり、文字列の順で選んだ国
    for c, (_n, _rs, v, u, src, note) in sorted(chosen.items()):
        if S['cur'].get(c) != u.split(' ')[0].upper():
            dropped['currency_mismatch:%s' % c] += 1     # 通貨がビッグマックと違う系列は換算せず除く
            continue
        sk = (c, v, u, src, note)
        for y in range(y0, y1 + 1):
            k = (sk, y)
            if k not in ann:
                continue
            if (c, y) not in S['BM']:
                dropped['no_bigmac_pair'] += 1
            elif (c, y) not in S['E']:
                dropped['no_engel:%s' % c] += 1
            elif (c, y) not in S['C'] or (c, y) not in S['POP']:
                dropped['no_C_or_pop'] += 1
            else:
                p, P, e = ann[k], S['BM'][(c, y)], S['E'][(c, y)]
                cpc = S['C'][(c, y)] / S['POP'][(c, y)]
                try:
                    k_ = (p / P) / (e * cpc / P)
                except ArithmeticError:                  # 分母が 0 に潰れた。下の確認で外す
                    k_ = math.nan
                row = dict(country=c, year=y, series=v, price=p, bigmac=P, E=e, C_pc=cpc,
                           b=p / P, M=cpc / P, k=k_)
                bad = [n for n in ('price', 'bigmac', 'E', 'C_pc', 'b', 'M', 'k') if not usable(row[n])]
                if bad:                                  # 割り算でゼロ・無限大・NaN になった行は回帰に渡さない
                    dropped['unusable_derived:%s' % c] += 1
                    log.add('compute', 'panel.' + bad[0], 'SKIPPED', '%s %d (%g)' % (c, y, row[bad[0]]))
                    continue
                panel.append(row)
    return panel, dropped


def bigmac_ratio(S, country, y0=Y0, y1=Y1, log=None):
    """ビッグマックの現地通貨価格の y1 / y0。どちらかの年がなければ None（除外の対象にしない）。
    どちらかが 0 のときも比は作らない（以前は黙って None にしていた。今は SKIPPED として log に記録する）。"""
    a, b = S['BM'].get((country, y0)), S['BM'].get((country, y1))
    if a is None or b is None:
        return None
    if a == 0 or b == 0:
        if log is not None:
            log.add('compute', 'bigmac_ratio', 'SKIPPED', '%s (%s: %g, %s: %g)' % (country, y0, a, y1, b))
        return None
    return b / a


def _decomp(x, cs, ucs):
    pooled = x.std(ddof=1)
    between = np.array([x[cs == c].mean() for c in ucs]).std(ddof=1)
    resid = np.concatenate([x[cs == c] - x[cs == c].mean() for c in ucs])
    within = float(np.sqrt((resid ** 2).sum() / (len(x) - len(ucs))))
    return float(pooled), float(between), within


def _fit(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    tot = ((y - y.mean()) ** 2).sum()
    return coef, (float('nan') if tot < 1e-18 else float(1 - (res ** 2).sum() / tot))


def analyze(panel, boot=BOOT, seed=SEED):
    """①ばらつき比較 ②log b = a + beta*log E + gamma*log M ③国単位ブートストラップ。"""
    cs = np.array([r['country'] for r in panel])
    ucs = sorted(set(cs.tolist()))
    col = lambda k: np.array([r[k] for r in panel], dtype=float)
    lb, lE, lM, lp, lC = (np.log(col(k)) for k in ('b', 'E', 'M', 'price', 'C_pc'))
    X = np.column_stack([np.ones(len(panel)), lE, lM])
    coef, r2 = _fit(X, lb)
    rng = np.random.default_rng(seed)
    idx_by = {c: np.where(cs == c)[0] for c in ucs}
    draws = []
    for _ in range(boot):
        pick = rng.choice(len(ucs), len(ucs), replace=True)
        ii = np.concatenate([idx_by[ucs[j]] for j in pick])
        try:
            draws.append(_fit(X[ii], lb[ii])[0])
        except np.linalg.LinAlgError:
            pass
    draws = np.array(draws)
    if len(draws) == 0:                    # 1回も当てはめられなかったときは、区間と確率を NaN にして先へ進む（compute に DROPPED が出る）
        ci = {name: (float('nan'), float('nan')) for name in ('beta', 'gamma')}
        p_ge_1 = float('nan')
    else:
        ci = {name: tuple(float(v) for v in np.percentile(draws[:, i], [2.5, 97.5]))
              for name, i in (('beta', 1), ('gamma', 2))}
        p_ge_1 = float((draws[:, 2] >= 1).mean())
    yr = np.array([r['year'] for r in panel], dtype=int)
    by_year = {}
    for y in sorted(set(yr.tolist())):
        m = yr == y
        if m.sum() >= 8:
            c_y, r2_y = _fit(X[m], lb[m])
            by_year[y] = dict(n=int(m.sum()), beta=float(c_y[1]), gamma=float(c_y[2]), r2=r2_y)
    return dict(
        n=len(panel), countries=ucs,
        obs_per_country=dict(collections.Counter(cs.tolist())),
        sd=dict(log_b=_decomp(lb, cs, ucs), log_k=_decomp(lb - lE - lM, cs, ucs),
                log_price_over_cpc=_decomp(lp - lC, cs, ucs)),
        a=float(coef[0]), beta=float(coef[1]), gamma=float(coef[2]), r2=r2,
        corr_E_M=float(np.corrcoef(lE, lM)[0, 1]),
        ci=ci, p_gamma_ge_1=p_ge_1, draws=len(draws), by_year=by_year)


def log_computed(log, panel, res, boot):
    """パネルと推定の結果にゼロ・NaN・無限大がないか調べて記録する（値は変えない）。
    ブートストラップで失敗して捨てた回数も記録する（以前は黙って捨てていた）。"""
    for k in ('price', 'bigmac', 'E', 'C_pc', 'b', 'M', 'k'):
        log.scan('compute', 'panel.' + k, {'%s %s' % (r['country'], r['year']): r[k] for r in panel})
    log.scan('compute', 'fit', {n: res[n] for n in ('a', 'beta', 'gamma', 'r2', 'corr_E_M', 'p_gamma_ge_1')})
    for n, xs in res['sd'].items():
        log.scan('compute', 'sd.' + n, dict(zip(('pooled', 'between', 'within'), xs)))
    for n, xs in res['ci'].items():
        log.scan('compute', 'ci.' + n, dict(zip(('lo', 'hi'), xs)))
    for y, v in res['by_year'].items():
        log.scan('compute', 'by_year', {'%d %s' % (y, n): v[n] for n in ('beta', 'gamma', 'r2')})
    if res['draws'] < boot:
        log.add('compute', 'bootstrap', 'DROPPED', '%d of %d draws failed (LinAlgError)' % (boot - res['draws'], boot))


def report(prefix, panel, dropped, excluded, res):
    print('%s | panel rows %d, countries %d' % (prefix, res['n'], len(res['countries'])))
    print('dropped:', dict(dropped))
    if excluded is not None:
        print('excluded (Big Mac ratio >= threshold):', excluded)
    print('obs per country:', res['obs_per_country'])
    print('[F1] SD of log (pooled, between-country, within-country)')
    for name, label in (('log_b', 'log b  (price/BigMac)'), ('log_k', 'log k  (price/(E*C_pc))'),
                        ('log_price_over_cpc', 'log price/C_pc')):
        print('  %-26s %s' % (label, ['%.3f' % v for v in res['sd'][name]]))
    print('[F2] log b = a + beta*logE + gamma*logM : a=%.3f beta=%.3f gamma=%.3f R2=%.3f'
          % (res['a'], res['beta'], res['gamma'], res['r2']))
    print('     gamma=1 means the Big Mac cancels out. corr(logE, logM)=%.3f' % res['corr_E_M'])
    for name in ('beta', 'gamma'):
        print('[F3] %-5s 95%% CI [%.2f, %.2f]  (draws %d)' % (name, *res['ci'][name], res['draws']))
    print('     P(gamma>=1) = %.2f' % res['p_gamma_ge_1'])
    for y, v in res['by_year'].items():
        print('[ref] %d n=%d beta=%.2f gamma=%.2f R2=%.2f' % (y, v['n'], v['beta'], v['gamma'], v['r2']))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('survey_csv', nargs='?', default=DEFAULT_CSV)
    ap.add_argument('--prefix', required=True, help='例: staple_price:rice / staple_price:wheat_flour')
    ap.add_argument('--exclude-inflation', type=float, default=None, metavar='RATIO',
                    help='ビッグマック現地通貨価格の2025年/2021年がこの値以上の国を除く（指定と結果を出力する）')
    ap.add_argument('--panel-out', default=None)
    ap.add_argument('--boot', type=int, default=BOOT)
    args = ap.parse_args(argv)

    log = ZeroNaNLog()
    S = load_survey(args.survey_csv, log)
    print('\n'.join(log.lines('load')))      # 読み込み直後に出す（後の計算で止まっても残る）
    S = precheck(S, log, prefix=args.prefix)           # 使えない入力は、割り算・回帰・除外の判定より前に外して SKIPPED を記録する
    panel, dropped = build_panel(S, args.prefix, log=log)
    excluded = None
    if args.exclude_inflation is not None:
        ratios = {c: bigmac_ratio(S, c, log=log) for c in {r['country'] for r in panel}}
        log.scan('compute', 'bigmac_ratio', ratios)
        excluded = sorted(c for c, x in ratios.items() if x is not None and x >= args.exclude_inflation)
        panel = [r for r in panel if r['country'] not in excluded]
    if not panel:
        print('\n'.join(log.lines('compute')))
        print('empty panel', file=sys.stderr)
        return 66
    if args.panel_out:
        with open(args.panel_out, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(panel[0].keys()))
            w.writeheader()
            w.writerows(panel)
    try:
        res = analyze(panel, boot=args.boot)
        log_computed(log, panel, res, args.boot)
        report(args.prefix, panel, dropped, excluded, res)
    except (ArithmeticError, ValueError) as e:          # 検査のあとでも計算できなかった（LinAlgError は ValueError）。ログを出してから終える
        print('\n'.join(log.lines('compute')))
        print('cannot compute: %s: %s' % (type(e).__name__, e), file=sys.stderr)
        return 65
    print('\n'.join(log.lines('compute')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
