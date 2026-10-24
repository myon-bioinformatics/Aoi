#!/usr/bin/env python3
"""仮想の主食（合成データ）を作り、既知の真値を回収できるか確認する。

SYNTHETIC: 生成したデータであり、観測値ではない。実データの結論として扱わない。
完了条件・合格条件には使わず、推奨条件（命題を試す前の足場）として用意する。
生成規則は下の PATTERNS に固定する（実データの結果を見て選ばない。値は構造を網羅する丸い格子）。
説明変数 E・M・ビッグマック価格は実データ、応答（主食の価格）だけが合成。詳細は SYNTHETIC.md。

  log b = log B0 + beta*(log E - 中央値) + gamma*(log M - 中央値) + eps,  eps ~ N(0, sigma^2)
  b = 主食の価格 / ビッグマック価格,  M = 1人あたり家計消費支出 / ビッグマック価格
  主食の価格(現地通貨) = b * ビッグマック価格

usage:
  python research/bigmac-ruler/synthetic_staples.py [SURVEY_CSV] [--out PATH] [--check] [--calibrate]
    --check      各パターンで gamma・beta・ばらつき(b と k)が真値どおりに出るか確認する
    --calibrate  国単位ブートストラップ95%CIが真値を含む割合を、国数を変えて確認する（数分かかる）
"""
import argparse
import collections
import csv
import sys

import numpy as np

DEFAULT_CSV = 'research/staple-price-survey/staple_survey_vertical.csv'
DEFAULT_OUT = 'research/bigmac-ruler/synthetic_staples_vertical.csv'
Y0, Y1 = 2021, 2025
SEED = 20261024
B0 = 0.5  # 中央のE・Mでの b（ビッグマック何個分/単位）。規模の仮置き

# (id, 名前, beta, gamma, sigma, jump)  jump: 中央値より大きい M で b を何倍にするか
PATTERNS = [
    ('S1', 'plausible_rice_like', 0.5, 0.5, 0.2, 1.0),        # ありえる
    ('S2', 'bigmac_tracking', 0.0, 0.0, 0.2, 1.0),            # ビッグマックだけに連動
    ('S3', 'household_tracking', 1.0, 1.0, 0.2, 1.0),         # 家計に連動（ビッグマックは約分される）
    ('S4', 'luxury', 0.0, 1.5, 0.2, 1.0),                     # 豊かな国ほど急に高い
    ('S5', 'inverse', 0.0, -0.5, 0.2, 1.0),                   # 豊かな国ほど安い（ありえない寄り）
    ('S6', 'noisy_measurement', 0.5, 0.5, 1.0, 1.0),          # S1と同じ構造でノイズ5倍
    ('S7', 'step_discontinuity', 0.5, 0.5, 0.2, 3.0),         # M が中央値を超えると3倍（連続性が切れる）
    ('S8', 'constant_nonexistent', 0.0, 0.0, 0.0, 1.0),       # どの国も常に B0（存在しない）
]
# 被覆率の確認に使う真値 (beta, gamma, sigma)
CAL_SCENARIOS = [(1.0, 1.0, 0.2), (0.0, 1.0, 0.5), (0.5, 0.5, 0.5), (0.0, 0.0, 0.2)]


def scaffold(path):
    """E・家計消費・人口・ビッグマック（年内2点）がそろう国×年を、観測値から読む。"""
    bm = collections.defaultdict(list)
    cur, E, C, POP = {}, {}, {}, {}
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            v, k = r['variable'], (r['country'], int(r['year']))
            if v == 'bigmac_local_price':
                bm[k].append(float(r['value']))
                cur[r['country']] = r['unit']
            elif v == 'engel_share_food':
                E[k] = float(r['value']) / 100
            elif v == 'household_consumption_total_lcu':
                C[k] = float(r['value'])
            elif v == 'population_total':
                POP[k] = float(r['value'])
    out = []
    for k in sorted(E):
        c, y = k
        if not (Y0 <= y <= Y1) or len(bm.get(k, [])) != 2 or k not in C or k not in POP:
            continue
        P = sum(bm[k]) / 2
        cpc = C[k] / POP[k]
        out.append(dict(country=c, year=y, cur=cur[c], P=P, E=E[k], Cpc=cpc, M=cpc / P))
    return out


def generate(sc, idx, pat):
    """パターン pat の b（ビッグマック何個分）を、国×年ごとに返す。seed は SEED + idx で固定。"""
    _pid, _name, beta, gamma, sigma, jump = pat
    rng = np.random.default_rng(SEED + idx)
    lE = np.log([r['E'] for r in sc])
    lM = np.log([r['M'] for r in sc])
    eps = rng.normal(0.0, sigma, len(sc)) if sigma > 0 else np.zeros(len(sc))
    lb = np.log(B0) + beta * (lE - np.median(lE)) + gamma * (lM - np.median(lM)) + eps
    if jump != 1.0:
        lb = lb + np.log(jump) * (lM > np.median(lM))
    return np.exp(lb)


def write_vertical(sc, path):
    """縦持ち形式で書く。観測値のファイルとは混ぜない（variable・unit・source に SYNTHETIC を残す）。"""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['country', 'date', 'year', 'variable', 'value', 'unit', 'source', 'note', 'estimated_value'])
        for i, pat in enumerate(PATTERNS):
            pid, name, beta, gamma, sigma, jump = pat
            b = generate(sc, i, pat)
            for r, bi in zip(sc, b):
                w.writerow([r['country'], '%d-01-01' % r['year'], r['year'],
                            'synthetic_staple:%s_%s' % (pid, name),
                            '%.6g' % (bi * r['P']), '%s per unit (synthetic)' % r['cur'],
                            'SYNTHETIC synthetic_staples.py seed=%d' % (SEED + i),
                            'beta=%s;gamma=%s;sigma=%s;jump=%s;b0=%s' % (beta, gamma, sigma, jump, B0), ''])


def _fit(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    tot = ((y - y.mean()) ** 2).sum()
    return coef, (float('nan') if tot < 1e-18 else float(1 - (res ** 2).sum() / tot))


def _design(sc):
    cs = np.array([r['country'] for r in sc])
    ucs = sorted(set(cs.tolist()))
    lE = np.log([r['E'] for r in sc])
    lM = np.log([r['M'] for r in sc])
    X = np.column_stack([np.ones(len(sc)), lE, lM])
    return cs, ucs, {c: np.where(cs == c)[0] for c in ucs}, lE, lM, X


def check(sc, boot=2000, verbose=True):
    """各パターンの gamma・beta を当てはめ、国単位ブートストラップの95%CIと真値を並べる。"""
    cs, ucs, idx_by, lE, lM, X = _design(sc)
    rows = []
    for i, pat in enumerate(PATTERNS):
        pid, name, beta_t, gamma_t, sigma, _jump = pat
        lb = np.log(generate(sc, i, pat))
        coef, r2 = _fit(X, lb)
        rng = np.random.default_rng(SEED + 100 + i)
        draws = []
        for _ in range(boot):
            pick = rng.choice(len(ucs), len(ucs), replace=True)
            ii = np.concatenate([idx_by[ucs[j]] for j in pick])
            draws.append(_fit(X[ii], lb[ii])[0])
        draws = np.array(draws)
        g_lo, g_hi = np.percentile(draws[:, 2], [2.5, 97.5])
        b_lo, b_hi = np.percentile(draws[:, 1], [2.5, 97.5])
        tol = 1e-9
        rows.append(dict(
            id=pid, name=name, beta_true=beta_t, gamma_true=gamma_t, sigma=sigma,
            gamma_hat=float(coef[2]), gamma_ci=(float(g_lo), float(g_hi)),
            gamma_covered=bool(g_lo - tol <= gamma_t <= g_hi + tol),
            beta_hat=float(coef[1]), beta_ci=(float(b_lo), float(b_hi)),
            beta_covered=bool(b_lo - tol <= beta_t <= b_hi + tol),
            r2=r2, sd_log_b=float(lb.std(ddof=1)), sd_log_k=float((lb - lE - lM).std(ddof=1))))
    if verbose:
        print('scaffold: %d rows, %d countries, years %d-%d' % (len(sc), len(ucs), Y0, Y1))
        print('%-3s %-22s %-14s %-24s %-24s %-5s %s' % (
            'id', 'name', 'true b,g,s', 'gamma_hat [95%]', 'beta_hat [95%]', 'R2', 'SD log b / log k'))
        for r in rows:
            print('%-3s %-22s %-14s %-24s %-24s %-5s %.3f / %.3f' % (
                r['id'], r['name'], '%g,%g,%g' % (r['beta_true'], r['gamma_true'], r['sigma']),
                '%.2f [%.2f,%.2f] %s' % (r['gamma_hat'], *r['gamma_ci'], 'Y' if r['gamma_covered'] else 'N'),
                '%.2f [%.2f,%.2f] %s' % (r['beta_hat'], *r['beta_ci'], 'Y' if r['beta_covered'] else 'N'),
                ('%.2f' % r['r2']) if r['r2'] == r['r2'] else 'nan', r['sd_log_b'], r['sd_log_k']))
    return rows


def calibrate(sc, clusters=(19, 49), reps=200, boot=400, verbose=True):
    """gamma の95%CIが真値を含んだ割合（目標 0.95）。国を無作為に選び直して reps 回くり返す。"""
    cs_all, uc, _idx, lE_all, lM_all, _X = _design(sc)
    out = {}
    for si, (beta, gamma, sigma) in enumerate(CAL_SCENARIOS):
        for ni, n_cl in enumerate(clusters):
            rng = np.random.default_rng(SEED + 7000 + 10 * si + ni)
            cover = 0
            for _ in range(reps):
                pick = rng.choice(len(uc), n_cl, replace=False)
                rows = np.concatenate([np.where(cs_all == uc[j])[0] for j in pick])
                cs, lE, lM = cs_all[rows], lE_all[rows], lM_all[rows]
                y = (np.log(B0) + beta * (lE - np.median(lE)) + gamma * (lM - np.median(lM))
                     + rng.normal(0, sigma, len(rows)))
                X = np.column_stack([np.ones(len(rows)), lE, lM])
                idx_by = {c: np.where(cs == c)[0] for c in set(cs.tolist())}
                cl = sorted(idx_by)
                g = np.empty(boot)
                for i in range(boot):
                    p = rng.choice(len(cl), len(cl), replace=True)
                    ii = np.concatenate([idx_by[cl[j]] for j in p])
                    g[i] = np.linalg.lstsq(X[ii], y[ii], rcond=None)[0][2]
                lo, hi = np.percentile(g, [2.5, 97.5])
                cover += bool(lo <= gamma <= hi)
            out[(si, n_cl)] = cover / reps
    if verbose:
        print('coverage of the 95%% CI for gamma (target 0.95), reps=%d boot=%d' % (reps, boot))
        print('%-24s %s' % ('true beta,gamma,sigma', '  '.join('clusters=%-3d' % n for n in clusters)))
        for si, sc_ in enumerate(CAL_SCENARIOS):
            print('%-24s %s' % ('%g, %g, %g' % sc_, '  '.join('%-12.3f' % out[(si, n)] for n in clusters)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('survey_csv', nargs='?', default=DEFAULT_CSV)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--calibrate', action='store_true')
    args = ap.parse_args(argv)
    sc = scaffold(args.survey_csv)
    if not sc:
        print('empty scaffold', file=sys.stderr)
        return 66
    write_vertical(sc, args.out)
    print('wrote %s: %d patterns x %d rows' % (args.out, len(PATTERNS), len(sc)))
    if args.check:
        check(sc)
    if args.calibrate:
        calibrate(sc)
    return 0


if __name__ == '__main__':
    sys.exit(main())
