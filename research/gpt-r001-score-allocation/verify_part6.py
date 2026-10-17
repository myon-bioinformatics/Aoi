"""Check Part6 replay CSVs and calculate descriptive sensitivity checks (stdlib)."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compare_csv(a, b):
    af, ar = read_csv(a)
    bf, br = read_csv(b)
    require(af == bf and len(ar) == len(br), f'CSV shape: {a.name}')
    for i, (x, y) in enumerate(zip(ar, br)):
        for k in af:
            if x[k] == y[k]:
                continue
            try:
                u, v = float(x[k]), float(y[k])
            except ValueError:
                raise ValueError(f'CSV mismatch: {a.name} row {i} {k}')
            require(math.isclose(u, v, rel_tol=1e-10, abs_tol=1e-12),
                    f'CSV numeric mismatch: {a.name} row {i} {k}')
    return len(ar)


def corr(x, y):
    a, b = mean(x), mean(y)
    return sum((u-a)*(v-b) for u, v in zip(x, y)) / math.sqrt(
        sum((u-a)**2 for u in x) * sum((v-b)**2 for v in y))


def inverse(matrix):
    n = len(matrix)
    a = [list(row) + [float(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        a[j], a[pivot] = a[pivot], a[j]
        require(abs(a[j][j]) > 1e-14, 'singular design')
        scale = a[j][j]
        a[j] = [v / scale for v in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [u-scale*v for u, v in zip(a[i], a[j])]
    return [row[n:] for row in a]


def matvec(a, v):
    return [sum(x*y for x, y in zip(row, v)) for row in a]


def regression(rows):
    fields = ['off_lSR', 'off_lRPS', 'def_lSR', 'def_lRPS']
    x = [[1.0] + [float(r[k]) for k in fields] for r in rows]
    y = [float(r['win%']) for r in rows]
    n, p = len(x), 5
    bread = inverse([[sum(r[i]*r[j] for r in x) for j in range(p)] for i in range(p)])
    beta = matvec(bread, [sum(r[i]*v for r, v in zip(x, y)) for i in range(p)])
    error = [v-sum(a*b for a, b in zip(r, beta)) for r, v in zip(x, y)]
    # Contrast SR minus RPS; CR1 single-cluster sandwich, separately by team/year.
    c = [0.0, 1.0, -1.0, 0.0, 0.0]
    bc = matvec(bread, c)
    delta = beta[1]-beta[2]
    s2 = sum(v*v for v in error)/(n-p)
    se = math.sqrt(s2*sum(a*b for a, b in zip(c, bc)))
    out = dict(coefficient_order=['intercept']+fields, coefficients=beta,
               sr_minus_rps=delta, iid_se=se, iid_t=delta/se)
    for field in ['team', 'year']:
        groups = sorted({r[field] for r in rows})
        variance = 0.0
        for g in groups:
            score = [sum(xx[j]*ee for xx, ee, rr in zip(x, error, rows) if rr[field] == g)
                     for j in range(p)]
            variance += sum(a*b for a, b in zip(bc, score))**2
        se = math.sqrt(variance*len(groups)/(len(groups)-1)*(n-1)/(n-p))
        out[field+'_cluster'] = dict(clusters=len(groups), se=se, t=delta/se)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--part5', type=Path, required=True, help='extracted Part5 directory')
    ap.add_argument('--part6', type=Path, required=True, help='original extracted Part6 directory')
    ap.add_argument('--replay', type=Path, required=True, help='Part6 directory after replay of p6/p6b/p6c')
    ap.add_argument('--out', type=Path, default=Path(__file__).parent/'outputs/part6_verification.json')
    args = ap.parse_args()
    matched = {p.name:compare_csv(p, args.replay/p.name) for p in sorted(args.part6.glob('*.csv'))}
    require(len(matched) == 10, 'expected 10 CSVs')
    _, rows = read_csv(args.part5/'team_season_relative.csv')
    by_key = {(int(r['year']), r['team']):r for r in rows}
    require(len(rows) == len(by_key) == 156, 'team-year coverage')
    pairs = [(r, by_key[y+1, t]) for (y, t), r in sorted(by_key.items()) if (y+1, t) in by_key]
    correlations = []
    for omit in [False, True]:
        selected = [(a, b) for a, b in pairs if not omit or int(a['year']) not in [2019, 2020]]
        for exclude in [False, True]:
            q = [(a, b) for a, b in selected if not exclude or a['team'] != 'd']
            correlations.append(dict(omit_pairs_touching2020=omit, exclude_chunichi=exclude,
                n=len(q), off_lRPS=corr([float(a['off_lRPS']) for a, b in q],
                                      [float(b['off_lRPS']) for a, b in q])))
    require([r['n'] for r in correlations] == [144, 132, 120, 110], 'pair coverage')
    result = dict(part6_source_sha256={p.name:digest(p) for p in sorted(args.part6.iterdir()) if p.is_file()},
                  part5_team_season_sha256=digest(args.part5/'team_season_relative.csv'),
                  replay_csv_rows=matched, csv_tolerance=dict(rel=1e-10, abs=1e-12),
                  correlations=correlations, regression_sensitivity=regression(rows),
                  script_sha256=digest(__file__), exit_code=0,
                  scope='Replay comparison and descriptive sensitivity; no new raw HTML, causal effect, or calibrated hypothesis test.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(matched_csvs=len(matched), correlations=correlations,
                          regression_sensitivity=result['regression_sensitivity']), indent=2))


if __name__ == '__main__':
    main()
