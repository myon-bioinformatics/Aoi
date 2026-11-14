"""R001 の集計（試合の観測から、得点の配分・回ごとの特徴・優勝の決まる時期などを数える。記述）。

    python research/gpt-r001-score-allocation/analyses.py <処理> [その処理の引数]

処理: analyze, batting_prediction, batting_size, clinch_interval, compare_external, early_scoring, game_state, home_away, hypothesis_followup, inning_cutoff, inning_features, inning_placement, iso_counterexamples, late_reaction, loss_tail, matched_comeback, preclinch_dates, preclinch_flow, run_loss_tail, same_score, scoring, scoring_spread

1 つの処理が 1 つのサブコマンド（旧 analyze.py, batting_prediction.py, batting_size.py … の 1 本が 1 つ）。引数と説明は各関数の説明（旧ファイルの冒頭）にある。
どれも手元の data/observations/r001/ と outputs/ だけを読み、ネットワークを使わない。
season_simulator（sakanalytics/）と、loss_tail の命題の判定（pythdragoras/）を使うので、その 2 つを sys.path に足す。
同じ中身の補助は 1 つにし、処理ごとに中身が違う名前には処理の名前を付けた。旧ファイルの HERE・ROOT・sys.path の行は、この冒頭の 1 か所にまとめた。
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import random
import re
import statistics
import statistics as st
import subprocess
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
from statistics import mean, median, pvariance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "sakanalytics"), str(ROOT / "pythdragoras")]

from season_simulator import Game, Snapshot  # noqa: E402


# ==== analyze（旧 analyze.py）

ANALYZE_DOC = """Exploratory score-pairing diagnostic; see PROTOCOL.md. Standard library only."""

ANALYZE_CL = {"g", "s", "db", "d", "t", "c"}
ANALYZE_TEAMS = ANALYZE_CL | {"h", "f", "b", "e", "l", "m"}
YEARS = range(2013, 2026)


def analyze_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def units(games):
    out = defaultdict(list)
    seen = set()
    for g in games:
        if g["key"] in seen:
            raise ValueError("duplicate game ID")
        seen.add(g["key"])
        year = int(g["date"][:4])
        if year not in YEARS or g["home"] not in ANALYZE_TEAMS or g["away"] not in ANALYZE_TEAMS:
            raise ValueError("unexpected scope")
        if g["home"] == g["away"]:
            raise ValueError("same team on both sides")
        for x in ("hs", "as"):
            if type(g[x]) is not int or g[x] < 0:
                raise ValueError("invalid score")
        out[year, g["home"]].append((g["hs"], g["as"], "home", g["away"]))
        out[year, g["away"]].append((g["as"], g["hs"], "away", g["home"]))
    for year in YEARS:
        expected = 144 if year < 2015 else 120 if year == 2020 else 143
        for team in ANALYZE_TEAMS:
            if len(out[year, team]) != expected:
                raise ValueError(f"incomplete {year} {team}: {len(out[year, team])}")
    return out


def win_equiv(scores):
    return sum(1 if a > b else 0.5 if a == b else 0 for a, b in scores)


def quantile(xs, p):
    at = (len(xs) - 1) * p
    lo, hi = math.floor(at), math.ceil(at)
    return xs[lo] + (xs[hi] - xs[lo]) * (at - lo)


def shuffle_reference(games, mode, replicates, seed):
    blocks = defaultdict(list)
    for scored, allowed, side, opponent in games:
        blocks[(side, opponent) if mode == "side_opponent" else (side,)].append((scored, allowed))
    groups = [(list(a), list(b)) for pairs in blocks.values() for a, b in [zip(*pairs)]]
    rng = random.Random(seed)
    samples = []
    for _ in range(replicates):
        total = 0.0
        for scored, allowed in groups:
            permuted = allowed.copy()
            rng.shuffle(permuted)
            total += win_equiv(zip(scored, permuted))
        samples.append(total)
    samples.sort()
    mean = statistics.mean(samples)
    actual = win_equiv((g[0], g[1]) for g in games)
    return {
        "shuffle_mean_we": mean,
        "shuffle_low_we": quantile(samples, .025),
        "shuffle_high_we": quantile(samples, .975),
        "shuffle_mean_mcse": statistics.stdev(samples) / math.sqrt(replicates),
        "excess_we": actual - mean,
        "excess_rate": (actual - mean) / len(games),
        "reference_position": "below" if actual < quantile(samples, .025) else
                              "above" if actual > quantile(samples, .975) else "inside",
    }


def analyze_describe(games):
    w = sum(a > b for a, b, *_ in games)
    l = sum(a < b for a, b, *_ in games)
    d = len(games) - w - l
    sides = {}
    for side in ("home", "away"):
        gg = [g for g in games if g[2] == side]
        sides[f"{side}_g"] = len(gg)
        sides[f"{side}_rd_g"] = sum(a - b for a, b, *_ in gg) / len(gg)
    return {"g": len(games), "w": w, "l": l, "d": d,
            "r": sum(g[0] for g in games), "ra": sum(g[1] for g in games),
            "npb_win_rate": w / (w + l) if w + l else None,
            "actual_we": w + .5 * d, "actual_we_rate": (w + .5 * d) / len(games),
            **sides, "home_away_gap": sides["home_rd_g"] - sides["away_rd_g"]}


def lag_summary(rows, exclude_2020=False):
    indexed = {(r["year"], r["team"]): r["excess_rate"] for r in rows
               if not exclude_2020 or r["year"] != 2020}
    pairs = [(v, indexed[y + 1, t]) for (y, t), v in indexed.items() if (y + 1, t) in indexed]
    if len(pairs) < 2:
        return {"n": len(pairs), "pearson_r": None}
    x, y = zip(*pairs)
    try:
        r = statistics.correlation(x, y)
    except statistics.StatisticsError:
        r = None
    return {"n": len(pairs), "pearson_r": r}


def analyze_main(argv=None):
    ap = argparse.ArgumentParser(description=ANALYZE_DOC)
    ap.add_argument("--games", type=Path, required=True)
    ap.add_argument("--replicates", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=20261003)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--verification", type=Path, default=Path(__file__).parent / "outputs/official_verification.json")
    args = ap.parse_args(argv)
    if args.replicates < 2:
        ap.error("at least two replicates required")
    meta_path = args.games.with_suffix(".manifest.json")
    meta = json.loads(meta_path.read_text())
    if meta["unknown"] != 0 or meta["sha256"] != analyze_sha(args.games):
        raise ValueError("unknown records or dataset hash mismatch")
    verification = json.loads(args.verification.read_text())
    expected_units = {(y, t) for y in YEARS for t in ANALYZE_TEAMS}
    checked_units = {(r["year"], r["team"]) for r in verification["checks"] if r["match"]}
    if verification["games_sha256"] != analyze_sha(args.games) or checked_units != expected_units:
        raise ValueError("independent official verification missing or mismatched")
    source = [json.loads(s) for s in args.games.read_text().splitlines()]
    grouped = units(source)
    summaries = {k: analyze_describe(v) for k, v in grouped.items()}
    rows = []
    for mode in ("side", "side_opponent"):
        for (year, team), games in sorted(grouped.items()):
            derived_seed = int.from_bytes(hashlib.sha256(f"{args.seed}/{mode}/{year}/{team}".encode()).digest()[:8], "big")
            r = {"mode": mode, "year": year, "team": team, "league": "C" if team in ANALYZE_CL else "P",
                 **summaries[year, team], **shuffle_reference(games, mode, args.replicates, derived_seed)}
            if team in ANALYZE_CL:
                others = [summaries[year, t]["home_away_gap"] for t in ANALYZE_CL - {team}]
                r["home_away_gap_minus_other_cl"] = r["home_away_gap"] - statistics.mean(others)
            else:
                r["home_away_gap_minus_other_cl"] = None
            rows.append(r)
            print(f"{mode} {year} {team} complete", flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "team_seasons.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lag = {}
    for mode in ("side", "side_opponent"):
        for league in ("C", "P"):
            subset = [r for r in rows if r["mode"] == mode and r["league"] == league]
            lag[f"{mode}/{league}/all"] = lag_summary(subset)
            lag[f"{mode}/{league}/without2020"] = lag_summary(subset, True)
    result = {"replicates": args.replicates, "seed": args.seed, "game_count": len(source),
              "team_seasons": len(grouped), "games_sha256": analyze_sha(args.games),
              "dataset_manifest_sha256": analyze_sha(meta_path), "script_sha256": analyze_sha(__file__),
              "verification_sha256": analyze_sha(args.verification),
              "protocol_sha256": analyze_sha(Path(__file__).with_name("PROTOCOL.md")),
              "lag_correlations_descriptive_only": lag,
              "note": "Exploratory reference distributions; no causal or significance claim."}
    (args.out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


def analyze(argv=None):
    """analyze.py の入口（説明は ANALYZE_DOC）。
    """
    analyze_main(argv)


# ==== batting_prediction（旧 batting_prediction.py）

BATTING_PREDICTION_DOC = """Fixed ISO/OBP models with grouped retrospective evaluation (stdlib)."""

MODELS = {'zero': [], 'mean': [], 'iso': ['iso'], 'obp': ['obp'], 'both': ['iso', 'obp']}


def normalize(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r['year'],r['league']), []).append(r)
    result = []
    for r in rows:
        peers = groups[r['year'],r['league']]
        assert len(peers)>=5
        others = [p for p in peers if p['team']!=r['team']]
        ref = sum(p['runs'] for p in peers)/sum(p['scoring'] for p in peers)
        result.append(dict(r,iso=r['raw_iso']-mean(p['raw_iso'] for p in others),
            obp=r['raw_obp']-mean(p['raw_obp'] for p in others),y=math.log(r['rps']/ref)))
    return result


def fit(rows, fields):
    ybar = mean(r['y'] for r in rows)
    if not fields:
        return [ybar]
    means = [mean(r[k] for r in rows) for k in fields]
    xy = [sum((r[k]-a)*(r['y']-ybar) for r in rows) for k,a in zip(fields,means)]
    xx = [[sum((r[k]-a)*(r[l]-b) for r in rows) for l,b in zip(fields,means)] for k,a in zip(fields,means)]
    if len(fields)==1:
        assert xx[0][0]>0
        betas=[xy[0]/xx[0][0]]
    else:
        determinant=xx[0][0]*xx[1][1]-xx[0][1]*xx[1][0]
        assert determinant>1e-16
        betas=[(xy[0]*xx[1][1]-xy[1]*xx[0][1])/determinant,
               (xy[1]*xx[0][0]-xy[0]*xx[1][0])/determinant]
    return [ybar-sum(a*b for a,b in zip(means,betas)),*betas]


def predict(row, fields, coefficients):
    return coefficients[0]+sum(row[k]*b for k,b in zip(fields,coefficients[1:]))


def evaluate(rows, mode):
    normalized = normalize(rows)
    cache, predictions = {}, []
    for r in normalized:
        key = (r['year'],) if mode=='year' else (r['team'],) if mode=='team' else (r['year'],r['team'])
        if key not in cache:
            train = [p for p in rows if (mode=='team' or p['year']!=r['year']) and (mode=='year' or p['team']!=r['team'])]
            normalized_train=normalize(train)
            cache[key]={name:([0.] if name=='zero' else fit(normalized_train,fields)) for name,fields in MODELS.items()}
        estimates={name:predict(r,fields,cache[key][name]) for name,fields in MODELS.items()}
        predictions.append(dict(year=r['year'],team=r['team'],actual=r['y'],low_iso=r['iso']<0,predictions=estimates))
    metrics={name:dict(rmse=math.sqrt(mean((r['predictions'][name]-r['actual'])**2 for r in predictions)),
                       mae=mean(abs(r['predictions'][name]-r['actual']) for r in predictions)) for name in MODELS}
    differences={}
    for grouping in ['year','team']:
        differences[grouping]=[]
        for value in sorted({r[grouping] for r in predictions}):
            group=[r for r in predictions if r[grouping]==value]
            differences[grouping].append(dict(group=value,n=len(group),
                mse_both_minus_obp=mean((r['predictions']['both']-r['actual'])**2-(r['predictions']['obp']-r['actual'])**2 for r in group)))
    subset=[r for r in predictions if r['low_iso'] and r['actual']>=0]
    coefficients={name:[dict(min=min(c[name][i] for c in cache.values()),mean=mean(c[name][i] for c in cache.values()),max=max(c[name][i] for c in cache.values()))
                         for i in range(len(next(iter(cache.values()))[name]))] for name in MODELS}
    return dict(n=len(rows),folds=len(cache),metrics=metrics,group_differences=differences,coefficient_ranges=coefficients,
        low_iso_nonlow_rps=dict(n=len(subset),metrics={name:dict(rmse=math.sqrt(mean((r['predictions'][name]-r['actual'])**2 for r in subset))) for name in MODELS}),
        predictions=predictions)


def batting_prediction_main(argv=None):
    ap=argparse.ArgumentParser(description=BATTING_PREDICTION_DOC)
    ap.add_argument('--season',type=Path,required=True)
    ap.add_argument('--part5',type=Path,required=True)
    ap.add_argument('--previous-batting',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(argv)
    raw=args.season.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!='fd76d410b7d8d9438237abc751820dcbf95c05e4':raise ValueError('season blob mismatch')
    previous=json.loads(args.previous_batting.read_text())
    if hashlib.sha256(args.part5.read_bytes()).hexdigest()!=previous['source_sha256']['part5']:raise ValueError('Part5 hash mismatch')
    source=[json.loads(line) for line in raw.decode().splitlines()]
    sm={(r['season'],r['team']):r for r in source}
    assert len(sm)==len(source)==168
    with args.part5.open(encoding='utf-8-sig',newline='') as f:part5=list(csv.DictReader(f))
    rows=[]
    for p in part5:
        s=sm[int(p['year']),p['team']]
        for a,b in [('G','G'),('W','W'),('L','L'),('T','T'),('RF','R'),('RA','RA')]:assert s[a]==int(p[b])
        assert s['inn_R']==s['RF'] and s['inn_S']>0
        assert math.isclose(s['bat_iso'],s['bat_slg']-s['bat_avg'],abs_tol=1e-12)
        rows.append(dict(year=s['season'],team=s['team'],league=s['league'],runs=s['inn_R'],scoring=s['inn_S'],
                         rps=s['inn_R']/s['inn_S'],raw_iso=s['bat_iso'],raw_obp=s['bat_obp']))
    assert len(rows)==156 and len({(r['year'],r['team']) for r in rows})==156
    pm={(int(p['year']),p['team']):p for p in part5}
    for r in normalize(rows):
        p=pm[r['year'],r['team']];s=sm[r['year'],r['team']]
        assert math.isclose(r['y'],float(p['off_lRPS']),abs_tol=1e-12)
        assert math.isclose(r['rps'],float(p['off_runs_per_scoring_inn']),abs_tol=1e-12)
        for k in ['iso','obp']:assert math.isclose(r[k],s['bat_d_'+k],abs_tol=1e-12)
    results={}
    for scope,q in [('without2020',[r for r in rows if r['year']!=2020]),('including2020',rows)]:
        results[scope]={mode:evaluate(q,mode) for mode in ['year','team','double']}
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    output=dict(plan_commit='1a83cc1a2a6b5a82c911aaff3c2aaffbaa443b04',season_blob=blob,
                sha256=dict(season=sha(args.season),part5=sha(args.part5),script=sha(Path(__file__))),
                results=results,interpretation='Retrospective grouped evaluation; hypothesis chosen after observing the period. Team-excluded training uses reduced reference populations. No causal or future-year claim.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({scope:{mode:r['metrics'] for mode,r in v.items()} for scope,v in results.items()},indent=2))


def batting_prediction(argv=None):
    """batting_prediction.py の入口（説明は BATTING_PREDICTION_DOC）。
    """
    batting_prediction_main(argv)


# ==== batting_size（旧 batting_size.py）

BATTING_SIZE_DOC = """Descriptive batting/RPS association; no causal or significance verdict (stdlib)."""

BATTING_SIZE_METRICS = ['iso', 'hr_pa', 'xbh_h', 'obp', 'bb_pa', 'avg']


def corr(x, y):
    a, b = mean(x), mean(y)
    xx, yy = sum((v-a)**2 for v in x), sum((v-b)**2 for v in y)
    return sum((u-a)*(v-b) for u, v in zip(x, y))/math.sqrt(xx*yy) if xx*yy else None


def partial(x, y, z):
    xy, xz, yz = corr(x, y), corr(x, z), corr(y, z)
    return (xy-xz*yz)/math.sqrt((1-xz*xz)*(1-yz*yz))


def center(rows, field):
    groups = {}
    for r in rows:
        groups.setdefault(r['team'], []).append(r[field])
    return [r[field]-mean(groups[r['team']]) for r in rows]


def batting_size_main(argv=None):
    ap = argparse.ArgumentParser(description=BATTING_SIZE_DOC)
    ap.add_argument('--season', type=Path, required=True)
    ap.add_argument('--part5', type=Path, required=True, help='team_season_relative.csv')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--season-blob', help='expected Git blob SHA of the season input')
    args = ap.parse_args(argv)
    season = [json.loads(s) for s in args.season.read_text().splitlines()]
    raw = args.season.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if args.season_blob:assert blob == args.season_blob, 'season Git blob mismatch'
    with args.part5.open(encoding='utf-8-sig', newline='') as f:
        part5 = list(csv.DictReader(f))
    sm = {(r['season'], r['team']):r for r in season}
    assert len(sm) == len(season) == 168
    rows = []
    for p in part5:
        s = sm[int(p['year']), p['team']]
        for a, b in [('G','G'), ('W','W'), ('L','L'), ('T','T'), ('RF','R'), ('RA','RA')]:
            assert s[a] == int(p[b]), (p['year'],p['team'],a)
        assert math.isclose(s['bat_iso'], s['bat_slg']-s['bat_avg'], abs_tol=1e-12)
        assert s['inn_R'] == s['RF'] and math.isclose(s['inn_R']/s['inn_S'],float(p['off_runs_per_scoring_inn']),abs_tol=1e-12)
        r=dict(year=s['season'],team=s['team'],name=s['team_name'],league=s['league'],
               rps_log=float(p['off_lRPS']),rps=s['inn_R']/s['inn_S'],runs_rank=int(float(p['R/G_CL/PL順位'])))
        for k in BATTING_SIZE_METRICS:r[k]=s['bat_d_'+k]
        rows.append(r)
    assert len(rows)==156
    # Independently verify the existing other-five-team relative batting values.
    for r in rows:
        peers=[s for s in season if s['season']==r['year'] and s['league']==r['league'] and s['team']!=r['team']]
        assert len(peers)==5
        for k in BATTING_SIZE_METRICS:assert math.isclose(r[k],sm[r['year'],r['team']]['bat_'+k]-mean(s['bat_'+k] for s in peers),abs_tol=1e-12)
    results=[]
    for scope,selected in [('all',rows),('without2020',[r for r in rows if r['year']!=2020]),
                           ('without_chunichi',[r for r in rows if r['team']!='d']),
                           ('C',[r for r in rows if r['league']=='C']),('P',[r for r in rows if r['league']=='P']),
                           ('chunichi',[r for r in rows if r['team']=='d'])]:
        for k in BATTING_SIZE_METRICS:
            results.append(dict(scope=scope,metric=k,n=len(selected),pearson=corr([r[k] for r in selected],[r['rps_log'] for r in selected]),
                within_team=corr(center(selected,k),center(selected,'rps_log')),
                partial_obp=partial([r[k] for r in selected],[r['rps_log'] for r in selected],[r['obp'] for r in selected]) if k!='obp' else None))
    bykey={(r['year'],r['team']):r for r in rows}
    changes=[]
    for omit in [False,True]:
        pairs=[(r,bykey[r['year']+1,r['team']]) for r in rows if (r['year']+1,r['team']) in bykey and (not omit or r['year'] not in [2019,2020])]
        for k in BATTING_SIZE_METRICS:changes.append(dict(omit_pairs_touching2020=omit,metric=k,n=len(pairs),
            first_difference_r=corr([b[k]-a[k] for a,b in pairs],[b['rps_log']-a['rps_log'] for a,b in pairs])))
    tables=[]
    for omit in [False,True]:
        q=[r for r in rows if not omit or r['year']!=2020]
        for k in BATTING_SIZE_METRICS:
            low=[r for r in q if r[k]<0]
            tables.append(dict(omit2020=omit,metric=k,n=len(q),low_n=len(low),low_and_low_rps=sum(r['rps_log']<0 for r in low),
                               low_rps_base_rate=mean(r['rps_log']<0 for r in q)))
    failures=[dict(r,direction='low_iso_nonlow_rps' if r['iso']<0 else 'nonlow_iso_low_rps') for r in rows if (r['iso']<0)!=(r['rps_log']<0)]
    d=[r for r in rows if r['team']=='d']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(source_sha256=dict(season=sha(args.season),part5=sha(args.part5)),season_git_blob=blob,
        validated_team_years=len(rows),checked_annual_fields=6*len(rows),correlations=results,changes=changes,tables=tables,
        chunichi=d,counterexamples=failures,script_sha256=sha(Path(__file__)),
        scope='Descriptive fixed-metric exploration from existing derived inputs; not raw batting-page verification or a causal effect.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(correlations=results[:6],changes=changes[:6],tables=tables[:6],
        chunichi_iso_below=sum(r['iso']<0 for r in d),chunichi_obp_below=sum(r['obp']<0 for r in d),counterexamples=len(failures)),indent=2))


def batting_size(argv=None):
    """batting_size.py の入口（説明は BATTING_SIZE_DOC）。
    """
    batting_size_main(argv)


# ==== inning_features（旧 inning_features.py）

INNING_FEATURES_CL = set('gtcds') | {'db'}
INNING_FEATURES_TEAMS = INNING_FEATURES_CL | set('hlmfbe')
INNING_FEATURES_FIELDS = ['year', 'team', 'league', 'batting_home', 'side', 'inning', 'runs', 'url']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ratio(a, b):
    return a / b if b else None


def inning_features_write_csv(path, rows):
    with Path(path).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def read_input(path):
    games = defaultdict(dict)
    rows = 0
    with gzip.open(path, 'rt', newline='') as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == INNING_FEATURES_FIELDS, 'unexpected CSV schema')
        for r in reader:
            rows += 1
            y, inning, runs = (int(r[k]) for k in ['year', 'inning', 'runs'])
            t, side, home = r['team'], r['side'], r['batting_home']
            require(2013 <= y <= 2026 and t in INNING_FEATURES_TEAMS, 'unknown year/team')
            require(r['league'] == ('CL' if t in INNING_FEATURES_CL else 'PL'), 'league mismatch')
            require(side in {'off', 'def'} and home in {'True', 'False'}, 'unknown side/home')
            require(inning >= 1 and runs >= 0, 'invalid inning/runs')
            u = r['url']
            require(u.startswith(f'https://npb.jp/bis/{y}/games/') or
                    u.startswith(f'https://npb.jp/scores/{y}/'), 'URL/year mismatch')
            key = (t, side, inning)
            require(key not in games[u], f'duplicate row {u} {key}')
            games[u][key] = (y, home == 'True', runs)
    records = []
    for url, cells in sorted(games.items()):
        teams = {k[0] for k in cells}
        require(len(teams) == 2, f'not two teams {url}')
        require(len({v[0] for v in cells.values()}) == 1, 'inconsistent years')
        off = {}
        for t in sorted(teams):
            opp, = teams - {t}
            a = {i: v for (tt, s, i), v in cells.items() if tt == t and s == 'off'}
            mirror = {i: v for (tt, s, i), v in cells.items() if tt == opp and s == 'def'}
            require(a == mirror, f'off/def mirror mismatch {url}')
            require(a and sorted(a) == list(range(1, max(a) + 1)), f'noncontiguous innings {url}')
            require(len({v[1] for v in a.values()}) == 1, 'mixed home flags')
            off[t] = (a[1][1], [a[i][2] for i in sorted(a)])
        require(sorted(v[0] for v in off.values()) == [False, True], 'home sides mismatch')
        h = next(t for t in off if off[t][0])
        a = next(t for t in off if not off[t][0])
        require(len(off[a][1]) - len(off[h][1]) in (0, 1), f'top/bottom length mismatch {url}')
        records.append(dict(url=url, year=next(iter(cells.values()))[0], home=h, away=a,
                            home_runs=off[h][1], away_runs=off[a][1]))
    return records, rows


def verify(records, base_path, official_path):
    base = [json.loads(s) for s in Path(base_path).read_text().splitlines()]
    bm = {g['href']: g for g in base}
    require(len(bm) == len(base) == 11028, 'invalid baseline cardinality')
    old = [g for g in records if g['year'] <= 2025]
    require({g['url'] for g in old} == set(bm), 'baseline URL set mismatch')
    totals = defaultdict(Counter)
    for g in old:
        b = bm[g['url']]
        require((g['year'], g['home'], g['away'], sum(g['home_runs']), sum(g['away_runs'])) ==
                (int(b['date'][:4]), b['home'], b['away'], b['hs'], b['as']),
                f'baseline game mismatch {g["url"]}')
        for side, other in [('home', 'away'), ('away', 'home')]:
            r, ra = sum(g[side + '_runs']), sum(g[other + '_runs'])
            totals[g['year'], g[side]].update(dict(G=1, W=int(r > ra), L=int(r < ra),
                                                  T=int(r == ra), R=r, RA=ra))
    official = list(csv.DictReader(Path(official_path).open()))
    require(len(official) == 156, 'official row count')
    seen = set()
    for r in official:
        k = int(r['year']), r['team']
        require(k not in seen and k in totals, 'official duplicate/unknown')
        seen.add(k)
        for v in ['G', 'W', 'L', 'T', 'R', 'RA']:
            require(totals[k][v] == int(r['o' + v]) == int(r[v]), f'official mismatch {k} {v}')
    require(seen == set(totals), 'official coverage mismatch')
    return dict(baseline_games=len(old), baseline_mismatches=0,
                official_team_seasons=len(seen), official_field_comparisons=len(seen)*6,
                official_mismatches=0)


def longest(flags):
    best = current = 0
    for v in flags:
        current = current + 1 if v else 0
        best = max(best, current)
    return best


def features(xs):
    require(bool(xs), 'empty innings')
    n, r = len(xs), sum(xs)
    z = [x > 0 for x in xs]
    s = sum(z)
    positive = [i + 1 for i, x in enumerate(xs) if x]
    return dict(innings=n, runs=r, scoring_innings=s,
                max_zero_run=longest([not b for b in z]), max_scoring_run=longest(z),
                leading_zeros=positive[0]-1 if positive else n,
                trailing_zeros=n-positive[-1] if positive else n,
                scoring_clusters=sum(b and (i == 0 or not z[i-1]) for i, b in enumerate(z)),
                first_scoring_inning=positive[0] if positive else None,
                last_scoring_inning=positive[-1] if positive else None,
                max_inning_runs=max(xs), max_inning_share=ratio(max(xs), r),
                inning_run_hhi=ratio(sum(x*x for x in xs), r*r),
                transitions=Counter((int(a), int(b)) for a, b in zip(z, z[1:])))


def zero_probability(total, scoring, slots):
    """P(no scoring labels in slots) under fixed-count uniform placement."""
    require(0 <= scoring <= total and 0 <= slots <= total, 'invalid hypergeometric sizes')
    if slots > total-scoring:
        return 0.0
    return math.prod((total-scoring-j)/(total-j) for j in range(slots))


def inning_features_aggregate(sequences):
    fs = [features(x) for x in sequences]
    g = len(fs)
    I, R, S = (sum(f[k] for f in fs) for k in ['innings', 'runs', 'scoring_innings'])
    counts = Counter(x for xs in sequences for x in xs)
    scored = [f for f in fs if f['runs']]
    result = dict(games=g, innings=I, runs=R, scoring_innings=S,
                  innings_per_game=I/g, runs_per_game=R/g, runs_per_inning=R/I,
                  score_rate=S/I, zero_rate=counts[0]/I,
                  single_run_inning_rate=counts[1]/I, two_run_inning_rate=counts[2]/I,
                  big_inning_rate=sum(v for k,v in counts.items() if k>=3)/I,
                  runs_per_scoring_inning=ratio(R,S), single_share_scoring=ratio(counts[1],S),
                  extra_runs_per_game=(R-S)/g, scoring_innings_per_game=S/g,
                  scoring_innings_variance=pvariance(f['scoring_innings'] for f in fs),
                  zero_scoring_game_rate=sum(f['scoring_innings']==0 for f in fs)/g,
                  one_scoring_game_rate=sum(f['scoring_innings']==1 for f in fs)/g,
                  multi_scoring_game_rate=sum(f['scoring_innings']>=2 for f in fs)/g,
                  threeplus_scoring_game_rate=sum(f['scoring_innings']>=3 for f in fs)/g,
                  scored_games=len(scored),
                  one_scoring_given_scored=ratio(sum(f['scoring_innings']==1 for f in fs),len(scored)))
    for key in ['max_zero_run', 'max_scoring_run', 'leading_zeros', 'trailing_zeros',
                'scoring_clusters', 'max_inning_runs']:
        result['mean_'+key] = mean(f[key] for f in fs)
    result['zero_run_ge6_game_rate'] = sum(f['max_zero_run']>=6 for f in fs)/g
    result['consecutive_scoring_game_rate'] = sum(f['max_scoring_run']>=2 for f in fs)/g
    for key in ['first_scoring_inning', 'last_scoring_inning', 'max_inning_share', 'inning_run_hhi']:
        result['mean_'+key+'_given_scored'] = mean(f[key] for f in scored) if scored else None
    transitions = sum((f['transitions'] for f in fs), Counter())
    for a in [0,1]:
        den = transitions[a,0]+transitions[a,1]
        result[f'transition_from_{a}_n'] = den
        for b in [0,1]:
            result[f'transition_{a}{b}_n'] = transitions[a,b]
            result[f'transition_{a}{b}_rate'] = ratio(transitions[a,b],den)
    for end in [3,6]:
        eligible = [xs for xs in sequences if len(xs)>=end]
        result[f'first{end}_eligible_games'] = len(eligible)
        result[f'first{end}_scoreless_rate'] = ratio(sum(sum(xs[:end])==0 for xs in eligible),len(eligible))
    for name, lo, hi in [('early',1,3),('middle',4,6),('late',7,9),('extra',10,1000)]:
        slots = [x for xs in sequences for i,x in enumerate(xs,1) if lo<=i<=hi]
        result[name+'_innings'] = len(slots)
        result[name+'_score_rate'] = ratio(sum(x>0 for x in slots),len(slots))
        result[name+'_runs_per_inning'] = ratio(sum(slots),len(slots))
    expected = sum(zero_probability(I,S,len(xs)) for xs in sequences)
    result['zero_games_uniform_expected'] = expected
    result['zero_game_rate_uniform_expected'] = expected/g
    result['zero_game_rate_excess_uniform'] = result['zero_scoring_game_rate']-expected/g
    require(math.isclose(result['zero_rate']+result['score_rate'],1), 'rate partition')
    require(math.isclose(result['zero_scoring_game_rate']+result['one_scoring_game_rate']+
                         result['multi_scoring_game_rate'],1), 'game partition')
    if S:
        require(math.isclose(result['runs_per_game'],result['innings_per_game']*
                             result['score_rate']*result['runs_per_scoring_inning']), 'identity failed')
    return result


def inning_features_main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--share', type=Path, required=True)
    p.add_argument('--out', type=Path, default=HERE/'outputs/inning_features')
    args = p.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    source = args.share/'team_half_innings.csv.gz'
    official = args.share/'official_check.csv'
    base = ROOT/'data/observations/r001/games.jsonl'
    records, nrows = read_input(source)
    receipt = verify(records, base, official)
    receipt.update(input_rows=nrows, input_games=len(records),
                   excluded_2026_games=sum(g['year']==2026 for g in records),
                   input_sha256=digest(source), baseline_sha256=digest(base),
                   shared_files_sha256={f.name:digest(f) for f in sorted(args.share.iterdir()) if f.is_file()},
                   script_sha256=digest(__file__), exit_code=0)
    groups = defaultdict(list)
    feature_rows = []
    for g in records:
        if g['year']==2026:
            continue
        for venue, opp in [('home','away'),('away','home')]:
            for role, bat in [('off',venue),('def',opp)]:
                xs = g[bat+'_runs']
                for side in ['all',venue]:
                    groups[g['year'],g[venue],side,role,'all'].append(xs)
                    if min(len(g['home_runs']),len(g['away_runs']))>=6:
                        groups[g['year'],g[venue],side,role,'first6'].append(xs[:6])
                f = features(xs)
                del f['transitions']
                feature_rows.append(dict(year=g['year'],team=g[venue],venue=venue,role=role,url=g['url'],**f))
    rows=[]
    for (y,t,v,role,window),xs in sorted(groups.items()):
        rows.append(dict(year=y,team=t,league='CL' if t in INNING_FEATURES_CL else 'PL',venue=v,role=role,window=window,
                         **inning_features_aggregate(xs)))
    indexed={(r['year'],r['team'],r['venue'],r['role'],r['window']):r for r in rows}
    for r in rows:
        if r['venue']=='all':
            expected=sum(indexed[r['year'],r['team'],v,r['role'],r['window']]['zero_games_uniform_expected']
                         for v in ['home','away'])
            r['zero_games_uniform_expected']=expected
            r['zero_game_rate_uniform_expected']=expected/r['games']
            r['zero_game_rate_excess_uniform']=r['zero_scoring_game_rate']-expected/r['games']
    inning_features_write_csv(args.out/'team_year_metrics.csv',rows)
    # Game-level features remain local, matching this research branch's data policy.
    local=ROOT/'data/observations/r001_inning_features'
    local.mkdir(parents=True,exist_ok=True)
    inning_features_write_csv(local/'team_game_features.csv',feature_rows)
    summary=[]
    metrics=[k for k in rows[0] if k not in ['year','team','league','venue','role','window']]
    for omit in [False,True]:
        for label,teams in [('chunichi',{'d'}),('other_cl',INNING_FEATURES_CL-{'d'}),('cl',INNING_FEATURES_CL),('npb',INNING_FEATURES_TEAMS)]:
            for venue in ['all','home','away']:
                for role in ['off','def']:
                    for window in ['all','first6']:
                        selected=[r for r in rows if r['team'] in teams and r['venue']==venue and
                                  r['role']==role and r['window']==window and (not omit or r['year']!=2020)]
                        summary.append(dict(scope='without2020' if omit else 'all',group=label,
                                            venue=venue,role=role,window=window,team_years=len(selected),
                                            **{k:mean(r[k] for r in selected if r[k] is not None)
                                               if any(r[k] is not None for r in selected) else None for k in metrics}))
    inning_features_write_csv(args.out/'group_summary.csv',summary)
    # All same-year peer differences, no selected-metric filtering.
    comparisons=[]
    for r in rows:
        if r['team']!='d':continue
        peers=[s for s in rows if s['year']==r['year'] and s['team'] in INNING_FEATURES_CL-{'d'} and
               all(s[k]==r[k] for k in ['venue','role','window'])]
        require(len(peers)==5,'peer count')
        for k in metrics:
            valid=[s[k] for s in peers if s[k] is not None]
            pmean=mean(valid) if valid else None
            comparisons.append(dict(year=r['year'],venue=r['venue'],role=r['role'],window=r['window'],
                                    metric=k,chunichi=r[k],other_cl_mean=pmean,peer_n=len(valid),
                                    difference=r[k]-pmean if r[k] is not None and pmean is not None else None))
    inning_features_write_csv(args.out/'chunichi_peer_differences.csv',comparisons)
    for name in ['team_year_metrics.csv','chunichi_peer_differences.csv']:
        (args.out/(name+'.gz')).write_bytes(gzip.compress((args.out/name).read_bytes(),mtime=0))
    receipt.update(metric_columns=len(metrics), team_year_metric_rows=len(rows),
                   local_game_feature_rows=len(feature_rows), group_rows=len(summary),
                   output_sha256={f.name:digest(f) for f in sorted(args.out.iterdir())
                                  if f.suffix in {'.csv','.gz'}})
    (args.out/'validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


def inning_features(argv=None):
    """Validate an external inning CSV and derive descriptive features, offline.
    """
    try:
        inning_features_main(argv)
    except FileNotFoundError as e:
        print(str(e),file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError) as e:
        print(str(e),file=sys.stderr);sys.exit(65)


# ==== clinch_interval（旧 clinch_interval.py）

CLINCH_INTERVAL_DOC = """Descriptive 2022 clinch cutoff and Wilson-z sensitivity from fixed inputs."""

INPUT_SHA='0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb'
OBJECT_BLOB='e22e9253126a21128af55863e4fb3654470cbc61'
CUT='2022-09-27'
CLINCH_INTERVAL_CL=['d','c','db','g','s','t']


def wilson(k,n,z):
    if n==0:return [0.,1.]
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]


def stat(k,n):
    if not 0<=k<=n:raise ValueError('invalid n,k')
    intervals=[]
    for z in [1,1.959963984540054,2,3]:
        lo,hi=wilson(k,n,z)
        intervals.append(dict(z=z,coverage_normal=math.erf(z/math.sqrt(2)),lo=lo,hi=hi,
                              relation='no_data' if n==0 else 'above' if lo>=.5 else 'below' if hi<.5 else 'includes'))
    return dict(n=n,k=k,rate=k/n if n else None,intervals=intervals,
                binomial_upper_p=sum(math.comb(n,i) for i in range(k,n+1))/2**n if n else None)


def intervals(text):
    b=text.encode();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if blob!=OBJECT_BLOB:raise ValueError('objections input blob mismatch')
    out=[]
    for block in re.split(r'(?=^## P\d+:)',text,flags=re.M):
        m=re.match(r'## (P\d+):',block)
        if not m or not re.search(r'強さ:.*?基準 0\.50',block):continue
        pid=m[1]
        for line in block.splitlines():
            row=re.match(r'\| (元の命題|対偶|逆|裏) \| (\d+) \| (\d+) \|',line)
            if row:
                cells=[v.strip() for v in line.strip('|').split('|')]
                out.append(dict(proposition=pid,form=row[1],undetermined=int(cells[7]),reported_verdict=cells[8],**stat(int(row[3]),int(row[2]))))
            if line.startswith('**きっかけ以外での判定**'):
                held=re.search(r'n=(\d+) 成立=(\d+)',line)
                if not held:raise ValueError('unknown held-out schema')
                out.append(dict(proposition=pid,form='きっかけ以外',undetermined=None,reported_verdict=None,**stat(int(held[2]),int(held[1]))))
    if not out:raise ValueError('no interval rows')
    p78=[r for r in out if r['proposition']=='P78' and r['form']=='きっかけ以外']
    if len(p78)!=1 or (p78[0]['n'],p78[0]['k'])!=(7,6):raise ValueError('P78 mismatch')
    return out


def date(url):
    match=re.search(r'/s(\d{4})(\d{2})(\d{2})\d+\.html$',url)
    if match:return '-'.join(match.groups())
    match=re.search(r'/scores/(\d{4})/(\d{2})(\d{2})/',url)
    if match:return '-'.join(match.groups())
    raise ValueError('unknown date URL')


def scoring(path):
    if digest(path)!=INPUT_SHA:raise ValueError('inning input hash mismatch')
    games,input_rows=read_input(path)
    totals=defaultdict(Counter);windows=defaultdict(Counter)
    for g in games:
        if g['year']!=2022:continue
        phase='before' if date(g['url'])<=CUT else 'after'
        for side,opp in [('home','away'),('away','home')]:
            team=g[side]
            if team not in CLINCH_INTERVAL_CL:continue
            runs=g[side+'_runs'];allowed=g[opp+'_runs'];rf=sum(runs);ra=sum(allowed)
            outcome='W' if rf>ra else 'L' if rf<ra else 'T'
            c=totals[phase,team];c.update(G=1,RF=rf,RA=ra);c[outcome]+=1
            for cut in [6,7]:
                w=windows[phase,team,cut]
                if min(len(runs),len(allowed))<cut:w['excluded']+=1;continue
                early=sum(runs[:cut]);late=sum(runs[cut:9]);extra=sum(runs[9:])
                w.update(G=1,early_RF=early,zero=int(early==0),three_plus=int(early>=3))
                w.update({f'{outcome}_G':1,f'{outcome}_reg_RF':late,f'{outcome}_reg_innings':max(0,min(9,len(runs))-cut),f'{outcome}_extra_RF':extra})
    # Check entry cut against independently reported games remaining.
    if totals['before','d']['G']!=139 or totals['after','d']['G']!=4:raise ValueError('reported 139/4 split mismatch')
    rows=[]
    for phase in ['before','after','full']:
        for name,teams in [('中日',['d']),('他セ5球団',CLINCH_INTERVAL_CL[1:])]:
            phases=['before','after'] if phase=='full' else [phase]
            ann=Counter();ws={c:Counter() for c in [6,7]}
            for ph in phases:
                for t in teams:
                    ann.update(totals[ph,t])
                    for c in [6,7]:ws[c].update(windows[ph,t,c])
            for c in [6,7]:
                w=ws[c]
                rows.append(dict(phase=phase,group=name,cut=c,annual=dict(ann),counts=dict(w),early_mean=w['early_RF']/w['G'] if w['G'] else None,
                                 zero_rate=w['zero']/w['G'] if w['G'] else None,three_plus_rate=w['three_plus']/w['G'] if w['G'] else None))
    return rows,input_rows


def clinch_interval_main(argv=None):
    p=argparse.ArgumentParser(description=CLINCH_INTERVAL_DOC)
    p.add_argument('--inning',type=Path,required=True);p.add_argument('--objections',type=Path,required=True)
    p.add_argument('--plan-commit',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(argv);rows,raw=scoring(a.inning)
    out=dict(plan_commit=a.plan_commit,cutoff_date=CUT,input_sha256=INPUT_SHA,objections_blob=OBJECT_BLOB,
             input_rows=raw,scoring_rows=rows,interval_rows=intervals(a.objections.read_text(encoding='utf-8')))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scoring_rows':len(rows),'interval_rows':len(out['interval_rows'])}))


def clinch_interval(argv=None):
    """clinch_interval.py の入口（説明は CLINCH_INTERVAL_DOC）。
    """
    clinch_interval_main(argv)


# ==== compare_external（旧 compare_external.py）

DATA = ROOT / 'data/observations/r001/games.jsonl'
EXPECTED_SHA = '7b1b6dfdd41cafbdf851cdb8bcd2cae981adb338570dd66de75881bfe35ee8d9'


def compare_external_main():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA
    games = [json.loads(s) for s in DATA.read_text().splitlines()]
    values = {}
    for year in range(2013, 2026):
        units = []
        for g in games:
            if not g['date'].startswith(str(year)) or 'd' not in (g['home'], g['away']):
                continue
            home = g['home'] == 'd'
            r, ra = (g['hs'], g['as']) if home else (g['as'], g['hs'])
            units.append((home, r, ra))
        def wpct(subset):
            decisive = [(r, ra) for _, r, ra in subset if r != ra]
            return sum(r > ra for r, ra in decisive) / len(decisive)
        w = sum(r > ra for _, r, ra in units)
        l = sum(r < ra for _, r, ra in units)
        r = sum(r for _, r, _ in units)
        ra = sum(ra for _, _, ra in units)
        values[year] = {
            'R/G': r / len(units), 'RA/G': ra / len(units),
            'RD/G': (r - ra) / len(units),
            'pythW_diff': w - r**1.83 / (r**1.83 + ra**1.83) * (w + l),
            'one_run_win_rate': wpct([u for u in units if abs(u[1] - u[2]) == 1]),
            'three_plus_win_rate': wpct([u for u in units if abs(u[1] - u[2]) >= 3]),
            'home_win_rate': wpct([u for u in units if u[0]]),
            'away_win_rate': wpct([u for u in units if not u[0]]),
            'wins_one_run_share': sum(r - ra == 1 for _, r, ra in units) / w,
            'wins_four_plus_share': sum(r - ra >= 4 for _, r, ra in units) / w,
        }
    supplied = {'R/G': 3.338, 'RA/G': 3.805, 'RD/G': -0.467,
                'pythW_diff': 1.693, 'one_run_win_rate': 0.495,
                'three_plus_win_rate': 0.421, 'home_win_rate': 0.517,
                'away_win_rate': 0.389, 'wins_one_run_share': 0.330,
                'wins_four_plus_share': 0.290}
    checks = {k: {'supplied': v, 'computed': statistics.mean(y[k] for y in values.values()),
                  'matches_display_rounding': round(statistics.mean(y[k] for y in values.values()), 3) == v}
              for k, v in supplied.items()}
    result = {'source': 'User-supplied Grok Part2 update, received 2026-10-03',
              'data_sha256': EXPECTED_SHA, 'aggregation': 'unweighted mean of 13 annual metrics',
              'checks': checks,
              'negative_pythagorean_residual_years': [y for y, v in values.items() if v['pythW_diff'] < 0],
              'not_checked': ['inning trajectories', '2026', 'all-team ranks', 'standardized differences', 'official rank tie-breaks']}
    target = Path(__file__).parent / 'outputs/external_comparison.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


def compare_external(argv=None):
    """Reconcile selected supplied-report claims against the frozen final-score data.
    """
    compare_external_main()


# ==== early_scoring（旧 early_scoring.py）

EARLY_SCORING_DOC = """Describe runs reached by innings six/seven, before interpreting outcomes."""
SEASON_BLOB='fd76d410b7d8d9438237abc751820dcbf95c05e4'


def counts(games,cutoff):
    hist=Counter(sum(g['ours'][:cutoff]) for g in games)
    n=len(games);rf=sum(k*v for k,v in hist.items())
    si=sum(v>0 for g in games for v in g['ours'][:cutoff])
    result=dict(G=n,RF=rf,scoring_innings=si,innings=n*cutoff,
        histogram={str(k):v for k,v in sorted(hist.items())},
        buckets={str(k):hist[k] for k in range(5)}|{'5+':sum(v for k,v in hist.items() if k>=5)},
        zero=hist[0],three_plus=sum(v for k,v in hist.items() if k>=3),
        mean_runs=rf/n if n else None,zero_rate=hist[0]/n if n else None,
        three_plus_rate=sum(v for k,v in hist.items() if k>=3)/n if n else None,
        scoring_rate=si/(n*cutoff) if n else None,rps=rf/si if si else None)
    assert sum(result['buckets'].values())==n
    if si:assert abs(result['mean_runs']-cutoff*result['scoring_rate']*result['rps'])<1e-12
    return result


def early_scoring_window(games,cutoff):
    gs=[g for g in games if min(len(g['ours']),len(g['theirs']))>=cutoff]
    by={v:counts([g for g in gs if v=='all' or g['home']==(v=='home')],cutoff) for v in ['all','home','away']}
    for k in ['G','RF','scoring_innings','innings','zero','three_plus']:
        assert by['all'][k]==by['home'][k]+by['away'][k]
    return dict(excluded=len(games)-len(gs),by_venue=by)


def paired_seventh(games):
    gs=[g for g in games if min(len(g['ours']),len(g['theirs']))>=7]
    n=len(gs);six=sum(sum(g['ours'][:6]) for g in gs);seven=sum(g['ours'][6] for g in gs)
    rf7=sum(sum(g['ours'][:7]) for g in gs);assert six+seven==rf7
    return dict(G=n,first6_RF=six,seventh_RF=seven,first7_RF=rf7,
        first6_mean=six/n if n else None,seventh_mean=seven/n if n else None,first7_mean=rf7/n if n else None,
        seventh_scoring_games=sum(g['ours'][6]>0 for g in gs),
        newly_reached_three=sum(sum(g['ours'][:6])<3<=sum(g['ours'][:7]) for g in gs))


def early_scoring_main(argv=None):
    p=argparse.ArgumentParser(description=EARLY_SCORING_DOC)
    for k in ['innings','season','out']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--csv',type=Path)
    a=p.parse_args(argv)
    if hashlib.sha256(a.innings.read_bytes()).hexdigest()!=INPUT_SHA:raise ValueError('inning hash mismatch')
    raw=a.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SEASON_BLOB:raise ValueError('season blob mismatch')
    sm={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    records,nrows=read_input(a.innings);groups=defaultdict(list)
    for g in records:
        if not 2013<=g['year']<=2025:continue
        for home in [True,False]:
            ours,theirs=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            groups[g['year'],g['home'] if home else g['away']].append(dict(home=home,ours=ours,theirs=theirs))
    rows=[]
    for (year,team),games in sorted(groups.items()):
        s=sm[year,team]
        check=dict(G=len(games),RF=sum(sum(g['ours']) for g in games),RA=sum(sum(g['theirs']) for g in games),
            W=sum(sum(g['ours'])>sum(g['theirs']) for g in games),L=sum(sum(g['ours'])<sum(g['theirs']) for g in games),T=sum(sum(g['ours'])==sum(g['theirs']) for g in games))
        if check!={k:s[k] for k in check}:raise ValueError(('annual mismatch',year,team))
        rows.append(dict(year=year,team=team,league=s['league'],annual=check,windows={str(c):early_scoring_window(games,c) for c in [6,7]},paired7=paired_seventh(games)))
    assert len(rows)==156
    for row in rows:
        peers=[r for r in rows if r['year']==row['year'] and r['league']==row['league'] and r['team']!=row['team']]
        assert len(peers)==5
        row['comparison']={}
        for c in ['6','7']:
            ours=row['windows'][c]['by_venue']['all'];ps=[r['windows'][c]['by_venue']['all'] for r in peers]
            g=sum(r['G'] for r in ps)
            peer=dict(G=g,RF=sum(r['RF'] for r in ps),zero=sum(r['zero'] for r in ps),three_plus=sum(r['three_plus'] for r in ps))
            peer.update(mean_runs=peer['RF']/g,zero_rate=peer['zero']/g,three_plus_rate=peer['three_plus']/g)
            gaps={k:ours[k]-peer[k] for k in ['mean_runs','zero_rate','three_plus_rate']}
            row['comparison'][c]=dict(other5_pooled=peer,gaps=gaps,
                mean_runs_rank=1+sum(r['RF']*ours['G']>ours['RF']*r['G'] for r in ps),
                lower_mean=ours['RF']*g<peer['RF']*ours['G'],
                higher_zero=ours['zero']*g>peer['zero']*ours['G'],
                lower_three_plus=ours['three_plus']*g<peer['three_plus']*ours['G'])
    d=[r for r in rows if r['team']=='d' and r['year']!=2020]
    main={}
    for c in ['6','7']:
        main[c]={}
        for condition in ['lower_mean','higher_zero','lower_three_plus']:
            main[c][condition]=dict(yes_years=[r['year'] for r in d if r['comparison'][c][condition]],
                no_years=[r['year'] for r in d if not r['comparison'][c][condition]])
        main[c]['mean_annual_gaps']={k:sum(r['comparison'][c]['gaps'][k] for r in d)/len(d) for k in ['mean_runs','zero_rate','three_plus_rate']}
    result=dict(plan_commit='96f8205b0647c4fcf811d18ed7afa0417b7f9943',input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,
        helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input_rows=nrows,annual_checks=936,main_team_years=144,rows=rows,chunichi_without2020=main)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    if a.csv:
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        with a.csv.open('w',newline='') as f:
            fields=['year','team','league','cutoff','excluded','G','RF','mean_runs','zero','zero_rate','three_plus','three_plus_rate','n0','n1','n2','n3','n4','n5_plus','mean_runs_rank','other5_mean_runs','other5_zero_rate','other5_three_plus_rate']
            writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
            for row in rows:
                for c in ['6','7']:
                    v=row['windows'][c]['by_venue']['all'];comp=row['comparison'][c]
                    out={k:v[k] for k in ['G','RF','mean_runs','zero','zero_rate','three_plus','three_plus_rate']}
                    out.update(year=row['year'],team=row['team'],league=row['league'],cutoff=c,excluded=row['windows'][c]['excluded'],mean_runs_rank=comp['mean_runs_rank'])
                    out.update({'n'+k.replace('+','_plus'):val for k,val in v['buckets'].items()})
                    out.update({'other5_'+k:comp['other5_pooled'][k] for k in ['mean_runs','zero_rate','three_plus_rate']})
                    writer.writerow(out)
    print('156 team-years / 936 annual checks; fixed-window and seventh-inning identities verified')
    print(json.dumps(main,ensure_ascii=False))
    for r in rows:
        if r['year']==2022 and r['league']=='C':
            print(r['team'],json.dumps({k:r[k] for k in ['windows','comparison','paired7']},ensure_ascii=False))


def early_scoring(argv=None):
    """early_scoring.py の入口（説明は EARLY_SCORING_DOC）。
    """
    early_scoring_main(argv)


# ==== late_reaction（旧 late_reaction.py）

LATE_REACTION_DOC = """Late runs, outcome-conditioned gradients, and whether a losing comeback reached parity."""
COLUMNS=['G','W','L','T','early_RF','early_RA','reg_RF','reg_RA','extra_RF','extra_RA',
         'reg_off_innings','reg_def_innings','extra_off_innings','extra_def_innings',
         'reg_zero','reg_one','reg_two','reg_three_plus','all_late_positive']
CLASSES=['no_late_runs','scored_never_tied','tied_never_led','led_then_lost']


def annotate(g,c):
    o,t=g['ours'],g['theirs'];early_o,early_t=sum(o[:c]),sum(t[:c]);delta=early_o-early_t
    state='lead' if delta>0 else 'tie' if delta==0 else 'trail'
    reg_o,reg_t=sum(o[c:9]),sum(t[c:9]);extra_o,extra_t=sum(o[9:]),sum(t[9:])
    rf_late=reg_o+extra_o;ra_late=reg_t+extra_t
    assert early_o+rf_late==sum(o) and early_t+ra_late==sum(t)
    category=None
    if state=='trail' and g['outcome']=='L':
        if rf_late==0:category='no_late_runs'
        else:
            # At the end of our top half the opponent's same-inning bottom is unplayed.
            differences=[sum(o[:i+1])-sum(t[:i+1 if g['home'] else i]) for i in range(c,len(o))]
            category='led_then_lost' if any(d>0 for d in differences) else 'tied_never_led' if any(d==0 for d in differences) else 'scored_never_tied'
    return dict(**g,state=state,early_RF=early_o,early_RA=early_t,reg_RF=reg_o,reg_RA=reg_t,
        extra_RF=extra_o,extra_RA=extra_t,reg_off_innings=len(o[c:9]),reg_def_innings=len(t[c:9]),
        extra_off_innings=len(o[9:]),extra_def_innings=len(t[9:]),category=category)


def late_reaction_summary(gs):
    n=len(gs)
    result=dict(G=n,W=sum(g['outcome']=='W' for g in gs),L=sum(g['outcome']=='L' for g in gs),T=sum(g['outcome']=='T' for g in gs))
    for k in COLUMNS[4:14]:result[k]=sum(g[k] for g in gs)
    for k,predicate in [('reg_zero',lambda n:n==0),('reg_one',lambda n:n==1),('reg_two',lambda n:n==2),('reg_three_plus',lambda n:n>=3)]:
        result[k]=sum(predicate(g['reg_RF']) for g in gs)
    result['all_late_positive']=sum(g['reg_RF']+g['extra_RF']>0 for g in gs)
    assert sum(result[k] for k in ['reg_zero','reg_one','reg_two','reg_three_plus'])==n
    return [result[k] for k in COLUMNS]


def categories(gs):
    out={}
    for margin in ['all','1','2','3+']:
        subset=[g for g in gs if g['category'] is not None and (margin=='all' or str(min(g['early_RA']-g['early_RF'],3))+('+' if g['early_RA']-g['early_RF']>=3 else '')==margin)]
        out[margin]={}
        for label in CLASSES:
            selected=[g for g in subset if g['category']==label]
            out[margin][label]=[len(selected),sum(g['early_RA']-g['early_RF'] for g in selected),
                sum(g['reg_RF']+g['extra_RF'] for g in selected),sum(g['reg_RA']+g['extra_RA'] for g in selected)]
        assert sum(v[0] for v in out[margin].values())==len(subset)
    for label in CLASSES:
        assert out['all'][label]==[sum(out[m][label][i] for m in ['1','2','3+']) for i in range(4)]
    return out


def late_reaction_window(gs,c):
    selected=[annotate(g,c) for g in gs if min(len(g['ours']),len(g['theirs']))>=c]
    result={'excluded':len(gs)-len(selected),'by_venue':{}}
    for venue in ['all','home','away']:
        vs=[g for g in selected if venue=='all' or g['home']==(venue=='home')]
        v=dict(all=late_reaction_summary(vs),by_outcome={o:late_reaction_summary([g for g in vs if g['outcome']==o]) for o in ['W','L','T']},
            by_state={s:late_reaction_summary([g for g in vs if g['state']==s]) for s in ['lead','tie','trail']},
            cross={s+'|'+o:late_reaction_summary([g for g in vs if g['state']==s and g['outcome']==o]) for s in ['lead','tie','trail'] for o in ['W','L','T']},
            losing_comeback=categories(vs),joint_by_outcome={})
        for outcome in ['W','L','T']:
            cells={}
            for early in ['0','1-2','3+']:
                for late in ['0','1','2','3+']:
                    cells[early+'|'+late]=sum(('0' if g['early_RF']==0 else '1-2' if g['early_RF']<=2 else '3+')==early and ('3+' if g['reg_RF']>=3 else str(g['reg_RF']))==late for g in vs if g['outcome']==outcome)
            assert sum(cells.values())==v['by_outcome'][outcome][0]
            v['joint_by_outcome'][outcome]=cells
        for dim in ['by_outcome','by_state','cross']:
            assert [sum(a[i] for a in v[dim].values()) for i in range(len(COLUMNS))]==v['all']
        assert sum(a[0] for a in v['losing_comeback']['all'].values())==v['cross']['trail|L'][0]
        result['by_venue'][venue]=v
    for i in range(len(COLUMNS)):
        assert result['by_venue']['all']['all'][i]==sum(result['by_venue'][v]['all'][i] for v in ['home','away'])
    return result


def late_reaction_main(argv=None):
    p=argparse.ArgumentParser(description=LATE_REACTION_DOC)
    for k in ['innings','season','out']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--plan-commit',required=True)
    p.add_argument('--csv',type=Path)
    a=p.parse_args(argv)
    if hashlib.sha256(a.innings.read_bytes()).hexdigest()!=INPUT_SHA:raise ValueError('inning hash mismatch')
    raw=a.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SEASON_BLOB:raise ValueError('season blob mismatch')
    sm={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    records,nrows=read_input(a.innings);groups=defaultdict(list)
    for g in records:
        if not 2013<=g['year']<=2025:continue
        for home in [True,False]:
            o,t=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            d=sum(o)-sum(t)
            groups[g['year'],g['home'] if home else g['away']].append(dict(home=home,ours=o,theirs=t,outcome='W' if d>0 else 'L' if d<0 else 'T'))
    rows=[]
    for (year,team),gs in sorted(groups.items()):
        s=sm[year,team]
        annual=dict(G=len(gs),RF=sum(sum(g['ours']) for g in gs),RA=sum(sum(g['theirs']) for g in gs),
            W=sum(g['outcome']=='W' for g in gs),L=sum(g['outcome']=='L' for g in gs),T=sum(g['outcome']=='T' for g in gs))
        if annual!={k:s[k] for k in annual}:raise ValueError(('annual mismatch',year,team))
        rows.append(dict(year=year,team=team,league=s['league'],annual=annual,cutoffs={str(c):late_reaction_window(gs,c) for c in [6,7]}))
    assert len(rows)==156
    dcomparisons=[]
    for r in rows:
        if r['team']!='d':continue
        result=dict(year=r['year'],cutoffs={})
        for c in ['6','7']:
            own=r['cutoffs'][c]['by_venue']['all'];peers=[p['cutoffs'][c]['by_venue']['all'] for p in rows if p['year']==r['year'] and p['league']=='C' and p['team']!='d']
            n=own['cross']['trail|L'][0];yes=own['losing_comeback']['all']['scored_never_tied'][0]
            pn=sum(v['cross']['trail|L'][0] for v in peers);py=sum(v['losing_comeback']['all']['scored_never_tied'][0] for v in peers)
            result['cutoffs'][c]=dict(behind_then_lost_G=n,scored_never_tied_G=yes,rate=yes/n if n else None,
                other5_G=pn,other5_scored_never_tied_G=py,other5_rate=py/pn if pn else None,
                higher_than_other5=yes*pn>py*n if n and pn else None)
        dcomparisons.append(result)
    result=dict(plan_commit=a.plan_commit,input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,
        helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input_rows=nrows,annual_checks=936,main_team_years=144,columns=COLUMNS,
        category_columns=['G','early_deficit_sum','all_late_RF','all_late_RA'],rows=rows,chunichi_comparisons=dcomparisons)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    if a.csv:
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        with a.csv.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['year','team','league','cutoff','outcome']+COLUMNS,lineterminator='\n');writer.writeheader()
            for row in rows:
                for c in ['6','7']:
                    for outcome,values in row['cutoffs'][c]['by_venue']['all']['by_outcome'].items():
                        writer.writerow(dict(year=row['year'],team=row['team'],league=row['league'],cutoff=c,outcome=outcome,**dict(zip(COLUMNS,values))))
    print('156 team-years / 936 annual checks; outcome, state, venue and comeback partitions verified')
    for r in rows:
        if r['year']==2022 and r['team'] in ['d','c']:
            for c in ['6','7']:
                v=r['cutoffs'][c]['by_venue']['all']
                print(r['team'],c,'outcomes',v['by_outcome'],'comeback',v['losing_comeback'])


def late_reaction(argv=None):
    """late_reaction.py の入口（説明は LATE_REACTION_DOC）。
    """
    late_reaction_main(argv)


# ==== matched_comeback（旧 matched_comeback.py）

MATCHED_COMEBACK_DOC = """Descriptive late-comeback comparison on common year/deficit/venue strata."""

CATEGORIES = ('no_runs', 'never_level', 'level_never_led', 'led')
MATCHED_COMEBACK_METRICS = ('level_or_better', 'led', 'W')
MATCHED_COMEBACK_FIELDS = ('G', 'level_or_better', 'led', 'W', 'L', 'T', 'no_runs', 'never_level',
          'level_never_led', 'late_RF', 'late_RA', 'off_innings')


def trajectory(home_runs, away_runs, home, cutoff):
    """Requires play beyond cutoff; detects parity-or-better, not exact tie visits."""
    if min(len(home_runs), len(away_runs)) < cutoff or len(away_runs) <= cutoff:
        return None
    own, opp = (home_runs, away_runs) if home else (away_runs, home_runs)
    deficit = sum(opp[:cutoff]) - sum(own[:cutoff])
    if deficit <= 0:
        return None
    differences = [sum(own[:i+1]) - sum(opp[:i+1 if home else i])
                   for i in range(cutoff, len(own))]
    level = any(d >= 0 for d in differences)
    lead = any(d > 0 for d in differences)
    rf, ra = sum(own[cutoff:]), sum(opp[cutoff:])
    final = sum(own)-sum(opp)
    category = 'led' if lead else 'level_never_led' if level else 'never_level' if rf else 'no_runs'
    result = {k: 0 for k in MATCHED_COMEBACK_FIELDS}
    result.update(G=1, level_or_better=int(level), led=int(lead), W=int(final>0),
                  L=int(final<0), T=int(final==0), late_RF=rf, late_RA=ra,
                  off_innings=len(own)-cutoff)
    result[category] = 1
    return deficit, result


def matched_comeback_build(innings, season):
    require(hashlib.sha256(innings.read_bytes()).hexdigest() == INPUT_SHA, 'inning hash mismatch')
    raw = season.read_bytes()
    require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == SEASON_BLOB, 'season blob mismatch')
    seasons = {(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    games, input_rows = read_input(innings)
    annual = defaultdict(Counter)
    cells = defaultdict(Counter)
    eligibility = defaultdict(Counter)
    for g in games:
        if g['year'] > 2025:
            continue
        for home in (False, True):
            team = g['home'] if home else g['away']
            own, opp = (g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            final = sum(own)-sum(opp)
            annual[g['year'],team].update(G=1,RF=sum(own),RA=sum(opp),W=int(final>0),L=int(final<0),T=int(final==0))
            for cutoff in (6,7):
                e = eligibility[g['year'],team,cutoff]
                e['all_games'] += 1
                if min(len(own),len(opp)) < cutoff:
                    e['cutoff_not_both_present'] += 1
                    continue
                if len(g['away_runs']) <= cutoff:
                    e['no_next_top'] += 1
                    continue
                e['continued'] += 1
                t = trajectory(g['home_runs'],g['away_runs'],home,cutoff)
                if t is not None:
                    deficit, values = t
                    e['behind'] += 1
                    cells[g['year'],team,seasons[g['year'],team]['league'],cutoff,home,deficit].update(values)
    require(len(annual)==156, 'team-year coverage')
    for k, a in annual.items():
        require(dict(a)=={f:seasons[k][f] for f in a}, 'annual count mismatch')
    rows=[]
    for (year,team,league,cutoff,home,deficit), c in sorted(cells.items()):
        require(sum(c[k] for k in CATEGORIES)==c['G'], 'category partition')
        require(c['W']+c['L']+c['T']==c['G'], 'outcome partition')
        require(c['W']<=c['led']<=c['level_or_better']<=c['G'], 'arrival ordering')
        rows.append(dict(year=year,team=team,league=league,cutoff=cutoff,home=home,deficit=deficit,**{f:c[f] for f in MATCHED_COMEBACK_FIELDS}))
    eligible=[dict(year=y,team=t,cutoff=c,**v) for (y,t,c),v in sorted(eligibility.items())]
    return rows, eligible, input_rows


def compare(rows, team, league, years, cutoff, venue='all', margin='exact'):
    selected=[r for r in rows if r['year'] in years and r['league']==league and r['cutoff']==cutoff
              and (venue=='all' or r['home']==(venue=='home'))]
    ours, peers=defaultdict(Counter),defaultdict(Counter)
    for r in selected:
        key=(r['year'],r['home'],r['deficit'] if margin=='exact' else min(r['deficit'],3))
        target=ours if r['team']==team else peers
        target[key].update({f:r[f] for f in MATCHED_COMEBACK_FIELDS})
    common=[k for k in ours if peers[k]['G']]
    own_all=sum(c['G'] for c in ours.values()); peer_all=sum(c['G'] for c in peers.values())
    n=sum(ours[k]['G'] for k in common)
    results={}
    for metric in MATCHED_COMEBACK_METRICS:
        own=sum(ours[k][metric] for k in common)
        expected=sum((Fraction(ours[k]['G']*peers[k][metric],peers[k]['G']) for k in common),Fraction())
        delta=Fraction(own,n)-expected/n if n else None
        results[metric]=dict(own_count=own,own_rate=own/n if n else None,
            peer_expected_count=float(expected),peer_standardized_rate=float(expected/n) if n else None,
            difference=float(delta) if delta is not None else None,
            difference_fraction=[delta.numerator,delta.denominator] if delta is not None else None,
            direction='lower' if delta is not None and delta<0 else 'not_lower' if delta is not None else 'unavailable',
            own_unadjusted_count=sum(c[metric] for c in ours.values()),
            own_unadjusted_rate=sum(c[metric] for c in ours.values())/own_all if own_all else None,
            peer_unadjusted_count=sum(c[metric] for c in peers.values()),
            peer_unadjusted_rate=sum(c[metric] for c in peers.values())/peer_all if peer_all else None)
    return dict(team=team,league=league,years=sorted(years),cutoff=cutoff,venue=venue,margin=margin,
                own_G=own_all,peer_G=peer_all,common_own_G=n,
                own_coverage=n/own_all if own_all else None,common_strata=len(common),
                unmatched_own_G=own_all-n,
                unmatched_strata=[dict(year=k[0],home=k[1],deficit=k[2],G=ours[k]['G']) for k in sorted(ours) if k not in common],
                common_own_categories={f:sum(ours[k][f] for k in common) for f in CATEGORIES},metrics=results)


def matched_comeback_analyze(rows):
    teams=sorted({(r['team'],r['league']) for r in rows})
    yearly=[]
    for team,league in teams:
        for year in range(2013,2026):
            for cutoff in (6,7):
                yearly.append(dict(period=str(year),**compare(rows,team,league,{year},cutoff)))
    pooled=[]
    for period,years in [('no2020',set(range(2013,2026))-{2020}),('with2020',set(range(2013,2026)))]:
        for team,league in teams:
            for cutoff in (6,7):
                for venue in ('all','home','away'):
                    for margin in ('exact','1_2_3plus'):
                        pooled.append(dict(period=period,**compare(rows,team,league,years,cutoff,venue,margin)))
    cases=[dict(year=r['years'][0],team=r['team'],league=r['league'],G=r['common_own_G'],
                difference=r['metrics']['level_or_better']['difference'],direction=r['metrics']['level_or_better']['direction'])
           for r in yearly if r['cutoff']==7 and r['years']!=[2020]]
    return yearly,pooled,cases


def matched_comeback_main(argv=None):
    p=argparse.ArgumentParser(description=MATCHED_COMEBACK_DOC)
    for name in ('innings','season','out','csv'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--plan-commit',required=True)
    a=p.parse_args(argv)
    rows,eligible,n=matched_comeback_build(a.innings,a.season)
    yearly,pooled,cases=matched_comeback_analyze(rows)
    result=dict(schema='aoi-matched-comeback/1',plan_commit=a.plan_commit,
                input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,input_rows=n,annual_checks=936,
                helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                eligibility=eligible,cells=rows,yearly=yearly,pooled=pooled,primary_team_year_cases=cases,
                interpretation='descriptive target-weighted comparison; no opponent-strength or causal adjustment')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    with a.csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps([r for r in pooled if r['team']=='d' and r['cutoff']==7 and r['venue']=='all' and r['margin']=='exact'],ensure_ascii=False))


def matched_comeback(argv=None):
    """matched_comeback.py の入口（説明は MATCHED_COMEBACK_DOC）。
    """
    matched_comeback_main(argv)


# ==== game_state（旧 game_state.py）

GAME_STATE_DOC = """Late-game score-state frequencies and subsequent outcomes, descriptive only."""

GAME_STATE_FIELDS=('G','W','L','T','late_RF','late_RA','off_innings','def_innings')
BINS=('-3+','-2','-1','0','1','2','3+')


def bucket(m):
    return '-3+' if m<=-3 else '3+' if m>=3 else str(m)


def total(rows):
    return {f:sum(r[f] for r in rows) for f in GAME_STATE_FIELDS}


def game_state_describe(c, denominator):
    return dict(**c,share=c['G']/denominator if denominator else None,
                win_fraction=c['W']/c['G'] if c['G'] else None,
                win_rate=c['W']/(c['W']+c['L']) if c['W']+c['L'] else None)


def game_state_summarize(rows):
    all_=total(rows);n=all_['G']
    bins={b:game_state_describe(total([r for r in rows if bucket(r['margin'])==b]),n) for b in BINS}
    states={name:game_state_describe(total([r for r in rows if (r['margin']>0)-(r['margin']<0)==sign]),n)
            for name,sign in [('trail',-1),('tie',0),('lead',1)]}
    for f in GAME_STATE_FIELDS:
        require(sum(b[f] for b in bins.values())==all_[f], 'bin partition')
        require(sum(b[f] for b in states.values())==all_[f], 'state partition')
    return dict(all=game_state_describe(all_,n),bins=bins,states=states)


def contrast(own,peer):
    output={}
    for name,state,metric,sign in [('S1','trail','share',1),('S2','lead','share',-1),('S3','lead','win_fraction',-1)]:
        a,b=own['states'][state],peer['states'][state]
        dena=own['all']['G'] if metric=='share' else a['G']
        denb=peer['all']['G'] if metric=='share' else b['G']
        numa=a['G'] if metric=='share' else a['W'];numb=b['G'] if metric=='share' else b['W']
        d=numa/dena-numb/denb if dena and denb else None
        supports=(numa*denb-numb*dena)*sign>0 if d is not None else None
        output[name]=dict(own=[numa,dena],peer=[numb,denb],difference=d,
                          verdict='supports_direction' if supports else 'counterexample' if supports is False else 'unavailable')
    return output


def game_state_build(innings,season):
    require(hashlib.sha256(innings.read_bytes()).hexdigest()==INPUT_SHA,'inning hash mismatch')
    raw=season.read_bytes();require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==SEASON_BLOB,'season blob mismatch')
    st={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    games,input_rows=read_input(innings);annual=defaultdict(Counter);cells=defaultdict(Counter);excluded=Counter()
    for g in games:
        if g['year']>2025:continue
        for home in (True,False):
            team=g['home'] if home else g['away'];own,opp=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            d=sum(own)-sum(opp);y=g['year'];league=st[y,team]['league']
            annual[y,team].update(G=1,RF=sum(own),RA=sum(opp),W=int(d>0),L=int(d<0),T=int(d==0))
            for cut in (6,7):
                if min(len(own),len(opp))<cut or len(g['away_runs'])<=cut:
                    excluded[y,team,cut]+=1;continue
                margin=sum(own[:cut])-sum(opp[:cut])
                cells[y,team,league,cut,home,margin].update(G=1,W=int(d>0),L=int(d<0),T=int(d==0),
                    late_RF=sum(own[cut:]),late_RA=sum(opp[cut:]),off_innings=len(own)-cut,def_innings=len(opp)-cut)
    require(len(annual)==156,'coverage')
    for k,v in annual.items():require(dict(v)=={f:st[k][f] for f in v},'annual mismatch')
    rows=[dict(year=y,team=t,league=l,cutoff=c,home=h,margin=m,**{f:v[f] for f in GAME_STATE_FIELDS})
          for (y,t,l,c,h,m),v in sorted(cells.items())]
    for r in rows:require(r['W']+r['L']+r['T']==r['G'],'outcome partition')
    return rows,[dict(year=y,team=t,cutoff=c,excluded=n) for (y,t,c),n in sorted(excluded.items())],input_rows


def game_state_analyze(rows):
    comparisons=[]
    periods=[(str(y),{y}) for y in range(2013,2026)]+[('no2020',set(range(2013,2026))-{2020}),('with2020',set(range(2013,2026)))]
    for period,years in periods:
        for cut in (6,7):
            for venue in ('all','home','away'):
                subset=[r for r in rows if r['year'] in years and r['cutoff']==cut and (venue=='all' or r['home']==(venue=='home'))]
                for team,league in sorted({(r['team'],r['league']) for r in rows}):
                    own=game_state_summarize([r for r in subset if r['team']==team])
                    peer=game_state_summarize([r for r in subset if r['league']==league and r['team']!=team])
                    comparisons.append(dict(period=period,team=team,league=league,cutoff=cut,venue=venue,own=own,peer=peer,propositions=contrast(own,peer)))
    cases=[dict(year=int(r['period']),team=r['team'],**r['propositions']) for r in comparisons
           if r['period'].isdigit() and r['period']!='2020' and r['cutoff']==7 and r['venue']=='all']
    return comparisons,cases


def game_state_main(argv=None):
    p=argparse.ArgumentParser(description=GAME_STATE_DOC)
    for k in ('innings','season','out','csv'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--plan-commit',required=True)
    a=p.parse_args(argv);rows,excluded,n=game_state_build(a.innings,a.season);comparisons,cases=game_state_analyze(rows)
    result=dict(schema='aoi-game-state/1',plan_commit=a.plan_commit,input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,input_rows=n,
                annual_checks=936,excluded=excluded,comparisons=comparisons,primary_cases=cases,
                scope='descriptive all-team score-state distributions; no causal or opponent-strength adjustment')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'),sort_keys=True)+'\n')
    with a.csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    for r in comparisons:
        if r['team']=='d' and r['venue']=='all' and r['cutoff']==7:
            print(r['period'],r['propositions'])


def game_state(argv=None):
    """game_state.py の入口（説明は GAME_STATE_DOC）。
    """
    game_state_main(argv)


# ==== home_away（旧 home_away.py）

def components(games):
    h = [g for g in games if g[2] == 'home']
    a = [g for g in games if g[2] == 'away']
    if not h or not a:
        raise ValueError('both sides required')
    hr, ar = st.mean(g[0] for g in h), st.mean(g[0] for g in a)
    hra, ara = st.mean(g[1] for g in h), st.mean(g[1] for g in a)
    result = dict(home_r=hr, away_r=ar, home_ra=hra, away_ra=ara,
                  scoring=hr-ar, prevention=ara-hra, gap=(hr-hra)-(ar-ara))
    if not math.isclose(result['gap'], result['scoring']+result['prevention'], abs_tol=1e-12):
        raise ValueError('decomposition mismatch')
    return result


def home_away_main():
    data = ROOT / 'data/observations/r001/games.jsonl'
    check = json.loads((HERE / 'outputs/official_verification.json').read_text())
    if analyze_sha(data) != check['games_sha256'] or len(check['checks']) != 156 or not all(c['match'] for c in check['checks']):
        raise ValueError('official verification does not cover input')
    grouped = units([json.loads(s) for s in data.read_text().splitlines()])
    rows, pairs = [], []
    for (year, team), games in sorted(grouped.items()):
        if team not in ANALYZE_CL:
            continue
        cl = [g for g in games if g[3] in ANALYZE_CL]
        pair = []
        for opp in sorted(ANALYZE_CL - {team}):
            selected = [g for g in cl if g[3] == opp]
            row = dict(year=year, team=team, opponent=opp,
                       home_n=sum(g[2]=='home' for g in selected),
                       away_n=sum(g[2]=='away' for g in selected), **components(selected))
            pairs.append(row)
            pair.append(row)
        balanced = {k: st.mean(r[k] for r in pair) for k in components(cl)}
        for mode, values in [('all_raw', components(games)), ('cl_raw', components(cl)), ('cl_balanced', balanced)]:
            rows.append(dict(mode=mode, year=year, team=team, **values))
    for row in rows:
        others = [r for r in rows if r['year']==row['year'] and r['mode']==row['mode'] and r['team']!=row['team']]
        for key in ['home_r','away_r','home_ra','away_ra','scoring','prevention','gap']:
            row[key+'_minus_others'] = row[key] - st.mean(r[key] for r in others)
    out = HERE / 'outputs'
    for name, records in [('home_away_team_years.csv', rows), ('home_away_opponent_cells.csv', pairs)]:
        with (out/name).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
            writer.writeheader(); writer.writerows(records)
    summary = {}
    for mode in ['all_raw','cl_raw','cl_balanced']:
        for omit in [False, True]:
            selected = [r for r in rows if r['mode']==mode and r['team']=='d' and (not omit or r['year']!=2020)]
            keys = [k for k in selected[0] if k not in ['mode','year','team']]
            summary[mode+('/without2020' if omit else '/all')] = {
                'n':len(selected), 'means':{k:st.mean(r[k] for r in selected) for k in keys},
                'positive_gap_minus_others_years':[r['year'] for r in selected if r['gap_minus_others']>0]}
    result = dict(data_sha256=analyze_sha(data), script_sha256=analyze_sha(__file__),
                  protocol_sha256=analyze_sha(HERE/'HOME_AWAY_PROTOCOL.md'), summaries=summary,
                  note='Descriptive opponent weighting, not park-adjusted or causal.')
    (out/'home_away_summary.json').write_text(json.dumps(result, indent=2)+'\n')
    for k,v in summary.items():
        print(k, json.dumps({m:round(v['means'][m],4) for m in ['scoring','prevention','gap','scoring_minus_others','prevention_minus_others','gap_minus_others']}), 'positive years:', len(v['positive_gap_minus_others_years']))
    for opp in sorted(ANALYZE_CL-{'d'}):
        sel=[r for r in pairs if r['team']=='d' and r['opponent']==opp]
        print('opponent',opp,{k:round(st.mean(r[k] for r in sel),4) for k in ['scoring','prevention','gap']})


def home_away(argv=None):
    """Descriptive decomposition; see HOME_AWAY_PROTOCOL.md. No network calls.
    """
    home_away_main()


# ==== hypothesis_followup（旧 hypothesis_followup.py）

HYPOTHESIS_FOLLOWUP_DOC = """Counterexample-led fixed-condition exploration; stdlib, retrospective."""

EXPECTED_BLOB = 'fd76d410b7d8d9438237abc751820dcbf95c05e4'


def classify(rows, predicate):
    cells = {k: [] for k in ['tp', 'fp', 'fn', 'tn']}
    for r in rows:
        a, b = predicate(r), not r['upper_half']
        cells['tp' if a and b else 'fp' if a else 'fn' if b else 'tn'].append([r['season'], r['team']])
    tp, fp, fn, tn = (len(cells[k]) for k in ['tp', 'fp', 'fn', 'tn'])
    denominator = math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
    return dict(n=len(rows), counts=dict(tp=tp, fp=fp, fn=fn, tn=tn),
                precision=tp/(tp+fp) if tp+fp else None, recall=tp/(tp+fn) if tp+fn else None,
                mcc=(tp*tn-fp*fn)/denominator if denominator else None,
                cases=cells)


def hypothesis_followup_main(argv=None):
    ap = argparse.ArgumentParser(description=HYPOTHESIS_FOLLOWUP_DOC)
    ap.add_argument('--season', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    raw = args.season.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob != EXPECTED_BLOB:
        raise ValueError('season Git blob mismatch')
    source = [json.loads(line) for line in raw.decode().splitlines()]
    bykey = {(r['season'],r['team']):r for r in source}
    assert len(bykey)==len(source)==168
    ranked = {}
    for r in source:
        if r['inn_R'] is None or r['inn_S'] is None:
            continue
        assert r['inn_R']==r['RF'] and r['inn_S']>0
        peers = [p for p in source if p['season']==r['season'] and p['league']==r['league']]
        assert len(peers)==6 and all(p['inn_S'] for p in peers)
        rps = Fraction(r['inn_R'], r['inn_S'])
        ranked[r['season'],r['team']] = 1+sum(Fraction(p['inn_R'],p['inn_S'])>rps for p in peers)
    paired, dropped = [], []
    for r in source:
        year, team = r['season'], r['team']
        if year<2013 or year==2020:
            continue
        if year-1==2020:
            dropped.append(dict(year=year,team=team,reason='previous year excluded'))
            continue
        if (year-1,team) not in ranked:
            dropped.append(dict(year=year,team=team,reason='previous RPS missing'))
            continue
        paired.append(dict(r,rps_rank=ranked[year,team],previous_rps_rank=ranked[year-1,team]))
    low = lambda r:r['rps_rank']>=5
    persistent = lambda r:low(r) and r['previous_rps_rank']>=5
    scopes = {'all':paired,'without_chunichi':[r for r in paired if r['team']!='d']}
    persistence = {scope:dict(single=classify(rows,low),persistent=classify(rows,persistent)) for scope,rows in scopes.items()}
    persistence['teams']={team:dict(n=len(rows),persistent_n=sum(persistent(r) for r in rows),
        persistent_b=sum(persistent(r) and not r['upper_half'] for r in rows))
        for team in sorted({r['team'] for r in paired})
        for rows in [[r for r in paired if r['team']==team]]}
    persistence['dropped']=dropped
    persistence['paired_rows']=[dict(year=r['season'],team=r['team'],rank=r['rps_rank'],previous_rank=r['previous_rps_rank'],
        persistent=persistent(r),upper_half=r['upper_half']) for r in paired]
    population=[r for r in source if r['season']>=2013 and r['season']!=2020]
    assert len(population)==144 and len(paired)==120
    baseline=lambda r:r['sim_p_upper']<0.4 or r['alloc_z_strat']< -1
    comparisons={}
    for limit in ['0.10','0.25','0.50']:
        threshold=Fraction(limit)
        close=lambda r:abs(Fraction(r['RF']-r['RA'],r['G']))<=threshold and r['one_run_net']<0
        standalone=classify(population,close)
        combined=classify(population,lambda r:baseline(r) or close(r))
        comparisons[limit]=dict(standalone=standalone,combined=combined,
            new_a_counterexamples=[[r['season'],r['team']] for r in population if r['upper_half'] and close(r) and not baseline(r)],
            new_b_covered=[[r['season'],r['team']] for r in population if not r['upper_half'] and close(r) and not baseline(r)])
    exceptions=[]
    for r in source:
        if r['season']!=2020:
            continue
        prior=ranked.get((2019,r['team']))
        exceptions.append(dict(year=2020,team=r['team'],upper_half=r['upper_half'],rps_rank=ranked[2020,r['team']],
            previous_rank=prior,persistent=ranked[2020,r['team']]>=5 and prior>=5,
            close=abs(Fraction(r['RF']-r['RA'],r['G']))<=Fraction('0.25') and r['one_run_net']<0))
    result=dict(plan_commit='cd8ccdee09ee827e6c3c8e3ae1a45780022e9d5a',source_git_blob=blob,
        source_sha256=hashlib.sha256(raw).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        population='2013-2025 excluding2020; consecutive pairs omit missing2012 and pairs touching2020',
        persistence=persistence,baseline=classify(population,baseline),close=comparisons,excluded2020=exceptions,
        chunichi=[dict(year=r['season'],rank=r['rank'],rps_rank=ranked.get((r['season'],r['team'])),
            previous_rps_rank=ranked.get((r['season']-1,r['team'])),rd_per_game=(r['RF']-r['RA'])/r['G'],one_run_net=r['one_run_net'])
            for r in source if r['team']=='d'],
        interpretation='Fixed definitions after hypothesis-generation data were observed; no causal attribution or independent validation.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(persistence={k:v for k,v in persistence.items() if k in scopes},close=comparisons),ensure_ascii=False))


def hypothesis_followup(argv=None):
    """hypothesis_followup.py の入口（説明は HYPOTHESIS_FOLLOWUP_DOC）。
    """
    hypothesis_followup_main(argv)


# ==== inning_cutoff（旧 inning_cutoff.py）

INNING_CUTOFF_DOC = """End-of-inning conditional outcomes; scoreline walkoff opportunity diagnostics."""


def inning_cutoff_describe(games, cutoff):
    n = len(games)
    w = sum(g['outcome'] == 'W' for g in games)
    l = sum(g['outcome'] == 'L' for g in games)
    t = n-w-l
    rf = sum(sum(g['ours'][cutoff:]) for g in games)
    ra = sum(sum(g['theirs'][cutoff:]) for g in games)
    oi = sum(len(g['ours'][cutoff:]) for g in games)
    ai = sum(len(g['theirs'][cutoff:]) for g in games)
    net = [sum(g['ours'][cutoff:])-sum(g['theirs'][cutoff:]) for g in games]
    return dict(G=n,W=w,L=l,T=t,win_rate=w/(w+l) if w+l else None,
                draw_rate=t/n if n else None,win_equivalent=(w+0.5*t)/n if n else None,
                late_RF=rf,late_RA=ra,late_off_innings=oi,late_def_innings=ai,
                late_RF_per_inning=rf/oi if oi else None,late_RA_per_inning=ra/ai if ai else None,
                late_net_mean=mean(net) if n else None,late_net_variance=pvariance(net) if n else None,
                late_net_sum=sum(net),late_net_sum_squares=sum(v*v for v in net),
                late_net_positive=sum(v>0 for v in net),late_net_zero=sum(v==0 for v in net),
                late_net_negative=sum(v<0 for v in net))


def cutoff_cells(games, cutoff):
    eligible = [g for g in games if min(len(g['ours']),len(g['theirs']))>=cutoff]
    out = {'excluded_short_games':len(games)-len(eligible),'by_venue':{}}
    for venue in ['all','home','away']:
        subset=[g for g in eligible if venue=='all' or g['home']==(venue=='home')]
        def run_bin(g):
            r=sum(g['ours'][:cutoff])
            return '0' if r==0 else '1-2' if r<=2 else '3+'
        def state(g):
            d=sum(g['ours'][:cutoff])-sum(g['theirs'][:cutoff])
            return 'lead' if d>0 else 'tie' if d==0 else 'trail'
        cells={'all':inning_cutoff_describe(subset,cutoff), 'runs':{},'state':{},'cross':{}}
        for r in ['0','1-2','3+']:
            cells['runs'][r]=inning_cutoff_describe([g for g in subset if run_bin(g)==r],cutoff)
            for s in ['lead','tie','trail']:
                cells['cross'][r+'|'+s]=inning_cutoff_describe([g for g in subset if run_bin(g)==r and state(g)==s],cutoff)
        for s in ['lead','tie','trail']:
            cells['state'][s]=inning_cutoff_describe([g for g in subset if state(g)==s],cutoff)
        for dimension in ['runs','state','cross']:
            for field in ['G','W','L','T','late_RF','late_RA','late_off_innings','late_def_innings']:
                assert sum(c[field] for c in cells[dimension].values())==cells['all'][field]
        out['by_venue'][venue]=cells
    for field in ['G','W','L','T','late_RF','late_RA','late_off_innings','late_def_innings']:
        assert sum(out['by_venue'][v]['all'][field] for v in ['home','away'])==out['by_venue']['all']['all'][field]
    return out


def walkoffs(games):
    result={}
    for venue in ['home','away']:
        subset=[g for g in games if g['home']==(venue=='home')]
        count=sum(g['walkoff'] for g in subset)
        opportunities=sum(g['opportunity_innings']>0 for g in subset)
        innings=sum(g['opportunity_innings'] for g in subset)
        assert count<=opportunities
        result[venue]=dict(G=len(subset),walkoff_condition_games=count,
            opportunity_games=opportunities,opportunity_innings=innings,
            per_all_games=count/len(subset) if subset else None,
            per_opportunity_game=count/opportunities if opportunities else None,
            per_opportunity_inning=count/innings if innings else None)
    return result


def inning_cutoff_main(argv=None):
    p=argparse.ArgumentParser(description=INNING_CUTOFF_DOC)
    for name in ['innings','season','out']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(argv)
    if hashlib.sha256(a.innings.read_bytes()).hexdigest()!=INPUT_SHA:raise ValueError('inning hash mismatch')
    raw=a.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SEASON_BLOB:raise ValueError('season blob mismatch')
    seasons={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    records,row_count=read_input(a.innings)
    groups=defaultdict(list)
    total_walkoffs=0
    for g in records:
        if not 2013<=g['year']<=2025:continue
        hr,ar=g['home_runs'],g['away_runs']
        walkoff=len(hr)==len(ar) and len(hr)>=9 and sum(hr)>sum(ar) and sum(hr[:-1])<=sum(ar)
        opportunity=sum(i>=8 and sum(hr[:i])<=sum(ar[:i+1]) for i in range(len(hr)))
        assert not walkoff or opportunity>0
        total_walkoffs+=walkoff
        for home in [True,False]:
            ours,theirs=(hr,ar) if home else (ar,hr)
            d=sum(ours)-sum(theirs)
            groups[g['year'],g['home'] if home else g['away']].append(dict(home=home,ours=ours,theirs=theirs,
                outcome='W' if d>0 else 'L' if d<0 else 'T',walkoff=walkoff,opportunity_innings=opportunity))
    rows=[]
    for (year,team),games in sorted(groups.items()):
        s=seasons[year,team]
        actual=dict(G=len(games),W=sum(g['outcome']=='W' for g in games),L=sum(g['outcome']=='L' for g in games),
            T=sum(g['outcome']=='T' for g in games),RF=sum(sum(g['ours']) for g in games),RA=sum(sum(g['theirs']) for g in games))
        if actual!={k:s[k] for k in actual}:raise ValueError(('annual mismatch',year,team))
        rows.append(dict(year=year,team=team,league=s['league'],annual=actual,
            cutoffs={str(c):cutoff_cells(games,c) for c in [6,7]},walkoff=walkoffs(games)))
    assert len(rows)==156
    assert sum(r['walkoff']['home']['walkoff_condition_games'] for r in rows)==total_walkoffs
    assert sum(r['walkoff']['away']['walkoff_condition_games'] for r in rows)==total_walkoffs
    main_games=[g for (y,t),gs in groups.items() if y!=2020 for g in gs]
    result=dict(input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        plan_commit='9035ab67e7c70efb71c0a21a03ac8088f5bf18a5',input_rows=row_count,annual_checks=936,
        main_team_years=144,excluded_year=2020,rows=rows,
        main_pooled=dict(cutoffs={str(c):cutoff_cells(main_games,c) for c in [6,7]},walkoff=walkoffs(main_games)))
    # Publish sufficient aggregated counts, not duplicated derived rates or game rows.
    columns = ['G','W','L','T','late_RF','late_RA','late_off_innings','late_def_innings',
               'late_net_sum','late_net_sum_squares','late_net_positive','late_net_zero','late_net_negative']
    result['cell_columns'] = columns
    for row in result['rows']:
        for cut in row['cutoffs'].values():
            for cells in cut['by_venue'].values():
                for dim in ['all','runs','state','cross']:
                    if dim == 'all':
                        cells[dim] = [cells[dim][k] for k in columns]
                    else:
                        cells[dim] = {label:[cell[k] for k in columns] for label,cell in cells[dim].items()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    print('156 annual rows / 936 annual checks; partitions and walkoff mirror verified')


def inning_cutoff(argv=None):
    """inning_cutoff.py の入口（説明は INNING_CUTOFF_DOC）。
    """
    inning_cutoff_main(argv)


# ==== inning_placement（旧 inning_placement.py）

INNING_PLACEMENT_DOC = """Scoring-inning placement diagnostics; no baserunner-event inference."""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inning_placement_describe(values):
    counts=Counter(values);s=sum(v>0 for v in values);runs=sum(values)
    result=dict(innings=len(values),runs=runs,scoring=s,zero=counts[0],one=counts[1],two=counts[2],three=counts[3],
                four_plus=sum(n for k,n in counts.items() if k>=4))
    if s:
        result.update(rps=runs/s,one_share=counts[1]/s,big_share=sum(v>=3 for v in values)/s,
            two_extra=counts[2]/s,three_extra=2*counts[3]/s,
            four_plus_extra=sum(v-1 for v in values if v>=4)/s,
            big_runs_share=sum(v for v in values if v>=3)/runs)
        assert math.isclose(result['rps'],1+result['two_extra']+result['three_extra']+result['four_plus_extra'],abs_tol=1e-12)
    else:
        result.update({k:None for k in ['rps','one_share','big_share','two_extra','three_extra','four_plus_extra','big_runs_share']})
    return result


def inning_placement_summary(games):
    result={}
    for label,home_filter,inning_filter in [('all',None,lambda i:True),('home',True,lambda i:True),
        ('away',False,lambda i:True),('first6',None,lambda i:i<=6),('after6',None,lambda i:i>=7)]:
        vals=[r for g in games if home_filter is None or g['home']==home_filter for i,r in enumerate(g['innings'],1) if inning_filter(i)]
        result[label]=inning_placement_describe(vals)
    concentration=[]
    for g in games:
        total=sum(g['innings'])
        if total>=3:
            concentration.append(dict(total=total,hhi=sum((v/total)**2 for v in g['innings']),maximum_share=max(g['innings'])/total))
    result['three_plus_games']=dict(n=len(concentration),mean_hhi=mean(p['hhi'] for p in concentration),
                                  mean_maximum_share=mean(p['maximum_share'] for p in concentration)) if concentration else dict(n=0)
    score_groups={}
    for total in [3,4,5]:
        q=[p for p in concentration if p['total']==total]
        score_groups[str(total)]=dict(n=len(q),hhi=mean(p['hhi'] for p in q) if q else None,
                                    maximum_share=mean(p['maximum_share'] for p in q) if q else None)
    result['same_score']=score_groups
    result['equal_weight_3_4_5_hhi']=mean(p['hhi'] for p in score_groups.values()) if all(p['n'] for p in score_groups.values()) else None
    result['equal_weight_3_4_5_maximum_share']=mean(p['maximum_share'] for p in score_groups.values()) if all(p['n'] for p in score_groups.values()) else None
    return result


def inning_placement_main(argv=None):
    ap=argparse.ArgumentParser(description=INNING_PLACEMENT_DOC)
    ap.add_argument('--innings',type=Path,required=True)
    ap.add_argument('--season',type=Path,required=True)
    ap.add_argument('--prediction',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(argv)
    if sha(args.innings)!='0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb':raise ValueError('inning input hash mismatch')
    raw=args.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!='fd76d410b7d8d9438237abc751820dcbf95c05e4':raise ValueError('season input blob mismatch')
    source=[json.loads(line) for line in raw.decode().splitlines()]
    sm={(s['season'],s['team']):s for s in source}
    if sha(args.prediction)!='0b76e0f0cc5e0a11dd4c949fedfacbc66009546d4064d9f614397a5f53fb8b04':raise ValueError('prediction input hash mismatch')
    pred=json.loads(args.prediction.read_text())
    assert pred['season_blob']=='fd76d410b7d8d9438237abc751820dcbf95c05e4'
    pm={(p['year'],p['team']):p for p in pred['results']['without2020']['year']['predictions']}
    assert len(pm)==144
    records,row_count=read_input(args.innings)
    team_games=defaultdict(list)
    for g in records:
        if g['year']>2025:continue
        for home in [True,False]:
            ours=g['home_runs'] if home else g['away_runs'];theirs=g['away_runs'] if home else g['home_runs']
            team=g['home'] if home else g['away']
            team_games[g['year'],team].append(dict(home=home,innings=ours,ra=sum(theirs)))
    rows=[]
    for key,games in sorted(team_games.items()):
        year,team=key;s=sm[key]
        w=sum(sum(g['innings'])>g['ra'] for g in games);l=sum(sum(g['innings'])<g['ra'] for g in games);t=len(games)-w-l
        checks=[len(games)==s['G'],w==s['W'],l==s['L'],t==s['T'],sum(sum(g['innings']) for g in games)==s['RF'],sum(g['ra'] for g in games)==s['RA']]
        assert all(checks),(year,team)
        r=dict(year=year,team=team,name=s['team_name'],league=s['league'],games=len(games),**inning_placement_summary(games))
        assert r['all']['runs']==s['inn_R'] and r['all']['scoring']==s['inn_S']
        if year!=2020:
            p=pm[key];r['rps_log_actual']=p['actual'];r['rps_log_predicted']=p['predictions']['both']
            r['residual']=p['actual']-p['predictions']['both']
        rows.append(r)
    assert len(rows)==156
    population=[r for r in rows if r['year']!=2020]
    cells={k:[] for k in ['tp','fp','fn','tn']}
    for r in population:
        peers=[p for p in population if p['year']==r['year'] and p['league']==r['league'] and p['team']!=r['team']]
        assert len(peers)==5
        r['peer_one_share']=sum(p['all']['one'] for p in peers)/sum(p['all']['scoring'] for p in peers)
        a=r['all']['one_share']>r['peer_one_share'];b=r['residual']<0
        cells['tp' if a and b else 'fp' if a else 'fn' if b else 'tn'].append([r['year'],r['team']])
    result=dict(plan_commit='ead424f40492ef5b2dd30da11734d03705247109',sha256=dict(innings=sha(args.innings),season=sha(args.season),prediction=sha(args.prediction),script=sha(Path(__file__)),inning_features_helper=sha(Path(__file__))),
        checked_team_years=len(rows),checked_annual_fields=len(rows)*6,input_rows=row_count,input_games=len(records),
        diagnostic=dict(n=len(population),condition='one_share > other-five pooled one_share',conclusion='observed - estimated RPS log < 0',
                        counts={k:len(v) for k,v in cells.items()},cases=cells),
        team_years=rows,interpretation='Score-only accounting and placement diagnostics. No hits/walks/LOB/steal events observed; not an independent predictor test or causal attribution.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps(dict(diagnostic=result['diagnostic'],focus=[r for r in rows if r['year']==2022 and r['league']=='C']),ensure_ascii=False,indent=2))


def inning_placement(argv=None):
    """inning_placement.py の入口（説明は INNING_PLACEMENT_DOC）。
    """
    inning_placement_main(argv)


# ==== iso_counterexamples（旧 iso_counterexamples.py）

ISO_COUNTEREXAMPLES_DOC = """Fixed-threshold descriptive follow-up of low-ISO counterexamples (stdlib)."""


def iso_counterexamples_summarize(rows):
    low = [r for r in rows if r['iso'] < 0]
    groups = {}
    for name, group in [('nonlow_rps', [r for r in low if r['rps_log'] >= 0]),
                        ('low_rps', [r for r in low if r['rps_log'] < 0])]:
        groups[name] = dict(n=len(group), stats={k: dict(mean=mean(r[k] for r in group), median=median(r[k] for r in group)) if group else None
                          for k in ['iso', 'obp', 'sr_log', 'rps_log', 'rg_log']})
    tables = {}
    for k in ['obp', 'sr_log']:
        tp = sum(r[k] >= 0 and r['rps_log'] >= 0 for r in low)
        fp = sum(r[k] >= 0 and r['rps_log'] < 0 for r in low)
        fn = sum(r[k] < 0 and r['rps_log'] >= 0 for r in low)
        tn = sum(r[k] < 0 and r['rps_log'] < 0 for r in low)
        tables[k] = dict(tp=tp, fp=fp, fn=fn, tn=tn,
                         precision=tp/(tp+fp) if tp+fp else None,
                         recall=tp/(tp+fn) if tp+fn else None)
    contrasts = []
    for year, league in sorted({(r['year'], r['league']) for r in low}):
        q = [r for r in low if (r['year'], r['league']) == (year, league)]
        a = [r for r in q if r['rps_log'] >= 0]
        b = [r for r in q if r['rps_log'] < 0]
        if a and b:
            contrasts.append(dict(year=year, league=league, nonlow_n=len(a), low_n=len(b),
                **{k: mean(r[k] for r in a)-mean(r[k] for r in b) for k in ['iso','obp','sr_log']}))
    obp_low = [r for r in low if r['obp'] < 0]
    return dict(n=len(rows),low_iso_n=len(low), groups=groups, tables=tables,
                same_year_league_contrasts=contrasts,
                contrast_summary={k:dict(n=len(contrasts),mean=mean(c[k] for c in contrasts),
                    positive=sum(c[k]>0 for c in contrasts)) if contrasts else None for k in ['iso','obp','sr_log']},
                low_iso_low_obp=dict(n=len(obp_low),low_rps=sum(r['rps_log']<0 for r in obp_low),
                                    counterexamples=sum(r['rps_log']>=0 for r in obp_low)))


def iso_counterexamples_main(argv=None):
    ap = argparse.ArgumentParser(description=ISO_COUNTEREXAMPLES_DOC)
    ap.add_argument('--season', type=Path, required=True)
    ap.add_argument('--batting-result', type=Path, required=True)
    ap.add_argument('--part5', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    previous = json.loads(args.batting_result.read_text())
    assert sha(args.part5) == previous['source_sha256']['part5'], 'Part5 input hash mismatch'
    with args.part5.open(encoding='utf-8-sig',newline='') as f:
        source = list(csv.DictReader(f))
    failures = {(r['year'],r['team']):r for r in previous['counterexamples']}
    rows=[]
    for p in source:
        r=dict(year=int(p['year']),team=p['team'],name=p['name'],league=p['league'],
               sr_log=float(p['off_lSR']),rps_log=float(p['off_lRPS']),
               ig_log=float(p['off_lIG']),rg_log=float(p['off_lRG']))
        assert math.isclose(r['sr_log']+r['rps_log']+r['ig_log'],r['rg_log'],abs_tol=1e-12)
        rows.append(r)
    assert len(rows)==156 and len({(r['year'],r['team']) for r in rows})==156
    return args,previous,rows,failures


def run(argv=None):
    args,previous,rows,failures=iso_counterexamples_main(argv)
    season_path=args.season
    assert sha(season_path)==previous['source_sha256']['season'], 'season input hash mismatch'
    season=[json.loads(s) for s in season_path.read_text().splitlines()]
    sm={(s['season'],s['team']):s for s in season}
    for r in rows:
        s=sm[r['year'],r['team']]
        r.update(league=s['league'],iso=s['bat_d_iso'],obp=s['bat_d_obp'])
        if (r['iso']<0)!=(r['rps_log']<0):
            old=failures[r['year'],r['team']]
            assert r['iso']==old['iso'] and r['obp']==old['obp'] and r['rps_log']==old['rps_log']
    assert sum(r['iso']<0 and r['rps_log']>=0 for r in rows)==32
    scopes={'all':rows,'without2020':[r for r in rows if r['year']!=2020],
            'without_chunichi':[r for r in rows if r['team']!='d'],
            'C':[r for r in rows if r['league']=='C'],'P':[r for r in rows if r['league']=='P'],
            '2013_2019':[r for r in rows if r['year']<=2019],
            '2021_2025':[r for r in rows if r['year']>=2021]}
    result=dict(source_sha256=dict(season=sha(season_path),part5=sha(args.part5),batting_result=sha(args.batting_result)),
                script_sha256=sha(Path(__file__)),thresholds=dict(iso=0,obp=0,sr_log=0,rps_log=0),
                scopes={k:iso_counterexamples_summarize(q) for k,q in scopes.items()},
                low_iso_rows=[r for r in rows if r['iso']<0],
                interpretation='Descriptive post-hoc exploration; no blind holdout, causal attribution, or calibrated inference.')
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'iso_counterexamples.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (args.out/'iso_counterexamples.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader();w.writerows(result['low_iso_rows'])
    print(json.dumps(result['scopes'],ensure_ascii=False,indent=2))


def iso_counterexamples(argv=None):
    """iso_counterexamples.py の入口（説明は ISO_COUNTEREXAMPLES_DOC）。
    """
    run(argv)


# ==== loss_tail（旧 loss_tail.py）

LOSS_TAIL_DOC = """Offline final-score distribution and existing PythDRAgoraS judgement."""


def split(home, away, cap):
    if not home or not away:
        raise ValueError('home and away observations required')
    gap = st.mean(away)-st.mean(home)
    body = st.mean(min(x, cap) for x in away)-st.mean(min(x, cap) for x in home)
    tail = st.mean(max(x-cap, 0) for x in away)-st.mean(max(x-cap, 0) for x in home)
    if not math.isclose(gap, body+tail, abs_tol=1e-12):
        raise AssertionError('mean decomposition failed')
    return gap, body, tail


def loss_tail_write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def loss_tail_analyze(args):
    meta = json.loads(args.games.with_suffix('.manifest.json').read_text())
    verify = json.loads(args.verification.read_text())
    digest = analyze_sha(args.games)
    expected = {(y,t) for y in YEARS for t in ANALYZE_TEAMS}
    if (meta['unknown'] != 0 or meta['sha256'] != digest or verify['games_sha256'] != digest
        or len(verify['checks']) != len(expected)
        or {(c['year'],c['team']) for c in verify['checks'] if c['match']} != expected):
        raise ValueError('input manifest/official verification mismatch')
    games = [json.loads(s) for s in args.games.read_text().splitlines()]
    grouped = units(games)
    maximum = max(max(g['hs'],g['as']) for g in games)
    frequencies, thresholds, seasons = [], [], []
    for (year, team), gg in sorted(grouped.items()):
        if team not in ANALYZE_CL:
            continue
        sides = {side:[g[1] for g in gg if g[2]==side] for side in ['home','away']}
        for side, vals in sides.items():
            counts = Counter(vals)
            for x in range(maximum+1):
                frequencies.append(dict(season=year, team=team, side=side, runs=x, count=counts[x], n=len(vals), frequency=counts[x]/len(vals)))
        survival_gap = 0
        for k in range(maximum+1):
            gap, body, tail = split(sides['home'], sides['away'], k)
            hp = sum(x>=k for x in sides['home'])/len(sides['home'])
            ap = sum(x>=k for x in sides['away'])/len(sides['away'])
            if k:
                survival_gap += ap-hp
            thresholds.append(dict(season=year, team=team, cap=k, home_survival=hp, away_survival=ap,
                                   survival_gap=ap-hp, gap=gap, body_gap=body, tail_gap=tail))
            if k==6:
                seasons.append(dict(season=year, team=team, team_name=team, gap=gap, body_gap=body, tail_gap=tail,
                                    away_more=gap>0, tail_dominates=tail>body))
        if not math.isclose(survival_gap, gap, abs_tol=1e-12):
            raise AssertionError('survival sum does not reconstruct mean gap')
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in [('loss_frequencies.csv',frequencies),('loss_thresholds.csv',thresholds),('loss_tail_seasons.csv',seasons)]:
        loss_tail_write_csv(args.out/name, rows)
    summaries = {}
    for label, teams in [('chunichi',{'d'}),('other_cl',ANALYZE_CL-{'d'})]:
        for omit in [False,True]:
            selected=[r for r in seasons if r['team'] in teams and (not omit or r['season']!=2020)]
            summaries[label+('/without2020' if omit else '/all')] = {k:st.mean(r[k] for r in selected) for k in ['gap','body_gap','tail_gap']}
    result=dict(data_sha256=digest,script_sha256=analyze_sha(__file__),protocol_sha256=analyze_sha(HERE/'TAIL_PROTOCOL.md'),
                proposition_sha256=analyze_sha(args.propositions), table_sha256=analyze_sha(args.out/'loss_tail_seasons.csv'), maximum_runs=maximum, units=len(seasons), summaries=summaries,
                passed=['input provenance','156 official team-years','unique games and season completeness','body + tail identity','survival sum identity'],exit_code=0)
    (args.out/'loss_tail_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    return 0


def judge(args):
    import polars as pl
    import propositions as pr
    props, digest=pr.load(args.propositions)
    receipt=json.loads((args.out/'loss_tail_receipt.json').read_text())
    if receipt['table_sha256']!=analyze_sha(args.out/'loss_tail_seasons.csv'):
        raise ValueError('analysis table hash mismatch')
    if receipt['proposition_sha256']!=digest:
        raise ValueError('proposition differs from analysis receipt')
    rows=[]
    for r in csv.DictReader((args.out/'loss_tail_seasons.csv').open()):
        rows.append({**r,'season':int(r['season']),**{k:float(r[k]) for k in ['gap','body_gap','tail_gap']},
                     **{k:r[k]=='True' for k in ['away_more','tail_dominates']}})
    results=[pr.evaluate(p,pl.DataFrame(rows),focus='d') for p in props]
    # Process all propositions sequentially; preserve every judgement. First nonzero is the process exit.
    code=next((r['judgement']['code'] for r in results if r['judgement']['code']),0)
    (args.out/'loss_tail_judgements.json').write_text(json.dumps(dict(results=results,exit_code=code,proposition_sha256=digest, engine_sha256=analyze_sha(ROOT/'pythdragoras/propositions.py'), table_sha256=receipt['table_sha256']),ensure_ascii=False,indent=2)+'\n')
    for r in results:
        print(json.dumps({'id':r['id'],'judgement':r['judgement']},ensure_ascii=False))
    return code


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(64, json.dumps(dict(exit_code=64,error=message))+"\n")


def loss_tail(argv=None):
    ap=Parser(description=LOSS_TAIL_DOC)
    ap.add_argument('stage',choices=['analyze','judge'])
    ap.add_argument('--games',type=Path,default=ROOT/'data/observations/r001/games.jsonl')
    ap.add_argument('--verification',type=Path,default=HERE/'outputs/official_verification.json')
    ap.add_argument('--propositions',type=Path,default=HERE/'tail_propositions.toml')
    ap.add_argument('--out',type=Path,default=HERE/'outputs')
    args=ap.parse_args(argv)
    try:
        return loss_tail_analyze(args) if args.stage=='analyze' else judge(args)
    except FileNotFoundError as e:
        code=66; message=str(e)
    except (ValueError,KeyError,TypeError) as e:
        # Existing proposition exceptions subclass ValueError; retain their contract.
        code=64 if type(e).__name__=='PropositionError' else 65; message=str(e)
    except OSError as e:
        code=74; message=str(e)
    except Exception as e:
        code=70; message=f'{type(e).__name__}: {e}'
    print(json.dumps(dict(exit_code=code,error=message),ensure_ascii=False),file=sys.stderr)
    return code


# ==== preclinch_dates（旧 preclinch_dates.py）

PRECLINCH_DATES_DOC = """Schedule-consistent A/B clinch bounds without assuming yearly tie-break rules."""

PRECLINCH_DATES_CL=tuple(sorted(['d','g','t','c','db','s']))


def possible(snapshot, members, target, inside, favorable, seconds=10):
    """Existential top-3 (inside) or bottom (outside), with ties assigned to target."""
    from ortools.sat.python import cp_model
    snapshot.validate();teams=snapshot.teams;n=len(teams);ti=teams.index(target)
    wins=[sum(r) for r in snapshot.wins];losses=[sum(r[i] for r in snapshot.wins) for i in range(n)]
    pairs=Counter(tuple(sorted((teams.index(g.home),teams.index(g.away)))) for g in snapshot.remaining)
    # In top-k feasibility, replacing a target draw/loss with win cannot worsen rank.
    # In outside feasibility, replacing a target draw/win with loss cannot improve rank.
    forced=[]
    for (i,j),count in list(pairs.items()):
        if ti not in (i,j):continue
        other=j if i==ti else i;winner=ti if inside else other;loser=other if inside else ti
        wins[winner]+=count;losses[loser]+=count
        forced.append(dict(teams=[teams[i],teams[j]],wins=[count if winner==i else 0,count if winner==j else 0],draws=0))
        del pairs[i,j]
    tw,td=wins[ti],max(1,wins[ti]+losses[ti]);m=cp_model.CpModel();fw={};fl={};variables={}
    for (i,j),count in pairs.items():
        a=m.new_int_var(0,count,'');b=m.new_int_var(0,count,'');m.add(a+b<=count)
        variables[i,j]=(a,b,count)
        fw.setdefault(i,[]).append(a);fl.setdefault(j,[]).append(a)
        fw.setdefault(j,[]).append(b);fl.setdefault(i,[]).append(b)
    ahead=[]
    for t in members:
        if t==target:continue
        i=teams.index(t);w=wins[i]+sum(fw.get(i,[]));l=losses[i]+sum(fl.get(i,[]))
        denom=m.new_int_var(1,1000,'');m.add_max_equality(denom,[w+l,1])
        delta=w*td-tw*denom;v=m.new_bool_var('')
        if favorable:m.add(delta>0).only_enforce_if(v);m.add(delta<=0).only_enforce_if(~v)
        else:m.add(delta>=0).only_enforce_if(v);m.add(delta<0).only_enforce_if(~v)
        ahead.append(v)
    m.add(sum(ahead)<=2 if inside else sum(ahead)>=3)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=0
    status=solver.solve(m)
    if status==cp_model.MODEL_INVALID:raise RuntimeError(solver.solution_info())
    feasible=True if status in (cp_model.FEASIBLE,cp_model.OPTIMAL) else False if status==cp_model.INFEASIBLE else None
    witness=None
    if feasible:
        witness=list(forced)
        for (i,j),(a,b,count) in variables.items():
            va,vb=solver.value(a),solver.value(b);wins[i]+=va;losses[j]+=va;wins[j]+=vb;losses[i]+=vb
            witness.append(dict(teams=[teams[i],teams[j]],wins=[va,vb],draws=count-va-vb))
        target_pct=Fraction(wins[ti],max(1,wins[ti]+losses[ti]))
        count=0
        for t in members:
            if t==target:continue
            i=teams.index(t);pct=Fraction(wins[i],max(1,wins[i]+losses[i]))
            count+=pct>target_pct if favorable else pct>=target_pct
        require((count<=2)==inside,'rational witness failed')
    return dict(feasible=feasible,status=solver.status_name(status),target_ties='favorable' if favorable else 'unfavorable',witness=witness)


def snapshot(games,day):
    teams=tuple(sorted({g['home'] for g in games}|{g['away'] for g in games}));n=len(teams);w=[[0]*n for _ in teams];d=[[0]*n for _ in teams];remaining=[]
    for g in games:
        when=date(g['url']);i=teams.index(g['home']);j=teams.index(g['away'])
        if when>day:remaining.append(Game(g['url'],when,g['home'],g['away']))
        else:
            delta=sum(g['home_runs'])-sum(g['away_runs'])
            if delta>0:w[i][j]+=1
            elif delta<0:w[j][i]+=1
            else:d[i][j]+=1;d[j][i]+=1
    return Snapshot(teams,w,d,tuple(remaining),day,'retrospective realized complete regular-season schedule; future results hidden')


def boundary(games,year,inside,favorable):
    days=sorted({date(g['url']) for g in games});cache={}
    def query(i):
        if i not in cache:
            cache[i]=possible(snapshot(games,days[i]),PRECLINCH_DATES_CL,'d',inside,favorable)
            require(cache[i]['feasible'] is not None,'solver timeout')
        return cache[i]
    lo=-1;hi=len(days)-1
    require(query(hi)['feasible'] is False,'end of season not clinched')
    while hi-lo>1:
        mid=(hi+lo)//2
        if query(mid)['feasible']:lo=mid
        else:hi=mid
    require(lo>=0,'unexpected first-date clinch')
    return dict(date=days[hi],previous_date=days[lo],at=query(hi),before=query(lo),queries=len(cache),year=year)


def small_check():
    # Exhaust all outcomes for a small four-team round-robin, with draws.
    teams=('d','a','b','c');games=[Game(str(i),'2025-09-02',a,b) for i,(a,b) in enumerate([('d','a'),('d','b'),('a','c'),('b','c')])]
    matrices=[[[0,1,0,1],[1,0,1,0],[1,0,0,1],[0,1,1,0]],
              [[0,9,9,9],[0,0,1,0],[0,0,0,1],[0,1,0,0]],
              [[0,0,0,0],[9,0,1,0],[9,0,0,1],[9,1,0,0]],
              [[0]*4 for _ in teams]]
    checks=0;seen=set()
    for w in matrices:
        s=Snapshot(teams,w,[[0]*4 for _ in teams],tuple(games),'2025-09-01','synthetic')
        for inside,fav in product((True,False),repeat=2):
            exists=False
            for outcomes in product((0,1,2),repeat=len(games)):
                totals=[sum(r) for r in w];ls=[sum(r[i] for r in w) for i in range(4)]
                for g,o in zip(games,outcomes):
                    i,j=teams.index(g.home),teams.index(g.away)
                    if o==0:totals[i]+=1;ls[j]+=1
                    elif o==1:totals[j]+=1;ls[i]+=1
                ps=[Fraction(t,max(1,t+l)) for t,l in zip(totals,ls)]
                ahead=sum(p>ps[0] if fav else p>=ps[0] for p in ps[1:])
                exists|=(ahead<3)==inside
            require(possible(s,teams,'d',inside,fav)['feasible']==exists,'enumeration mismatch');checks+=1;seen.add(exists)
    require(seen=={True,False},'enumeration must cover feasible and infeasible')
    return checks


def preclinch_dates_main(argv=None):
    p=argparse.ArgumentParser(description=PRECLINCH_DATES_DOC)
    for k in ('innings','season','out'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--plan-commit',required=True);a=p.parse_args(argv)
    game_state_build(a.innings,a.season) # pinned hashes and 936 annual checks before date calculation
    test_count=small_check();games,_=read_input(a.innings);results=[]
    for year in range(2013,2026):
        gs=[g for g in games if g['year']==year];inside=year!=2020
        bounds=[boundary(gs,year,inside,fav) for fav in (True,False)]
        ds=sorted(b['date'] for b in bounds)
        r=dict(year=year,kind='B_class' if inside else 'top3_no_CS',earliest=ds[0],latest=ds[1],exact=ds[0]==ds[1],bounds=bounds)
        if not r['exact'] and year==2016:
            from season_simulator import Rules
            from season_exact import solve
            rules=Rules(PRECLINCH_DATES_CL,('s','g','t','c','d','db'),True,3,'NPB-2016-CL',
                        'https://npb.jp/games/2016/info_cscl.html',False)
            previous=max(date(g['url']) for g in gs if date(g['url'])<ds[0])
            checks={day:solve(snapshot(gs,day),rules,'d',top_k=3,seconds=10) for day in (previous,ds[0])}
            require(checks[previous]['feasible'] is True and checks[ds[0]]['feasible'] is False,'2016 boundary not resolved')
            r.update(exact=True,date=ds[0],official_resolution=dict(source=rules.source,
                previous_order_source='https://npb.jp/bis/2015/stats/std_c.html',league_pct_tiebreak=False,checks=checks))
        elif r['exact']:r['date']=ds[0]
        results.append(r);print(year,r['kind'],r.get('date',ds),flush=True)
    g26=[g for g in games if g['year']==2026]
    import ortools
    result=dict(plan_commit=a.plan_commit,solver='ortools-'+ortools.__version__,small_enumeration_checks=test_count,annual_checks=936,years=results,
                year2026=dict(status='not_evaluable_incomplete_schedule',games=len(g26),last_observed_date=max((date(g['url']) for g in g26),default=None)),
                scope='end-of-day first clinch conditional on complete realized schedule; ties bounded, not assumed')
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')


def preclinch_dates(argv=None):
    """preclinch_dates.py の入口（説明は PRECLINCH_DATES_DOC）。
    """
    preclinch_dates_main(argv)


# ==== preclinch_flow（旧 preclinch_flow.py）

PRECLINCH_FLOW_DOC = """Pool game-state transitions through each Chunichi clinch date, inclusive."""

PRECLINCH_FLOW_CL={'d','g','t','c','db','s'}
STATES=('lead','tie','trail','unavailable')


def preclinch_flow_aggregate(games, dates):
    cells=defaultdict(Counter)
    for g in games:
        y=g['year']
        if y not in dates or date(g['url'])>dates[y]:continue
        for home in (True,False):
            team=g['home'] if home else g['away']
            if team not in PRECLINCH_FLOW_CL:continue
            own,opp=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            final=sum(own)-sum(opp);outcome='W' if final>0 else 'L' if final<0 else 'T'
            for cut in (6,7):
                state='unavailable';category='not_trailing'
                if min(len(own),len(opp))>=cut and len(g['away_runs'])>cut:
                    margin=sum(own[:cut])-sum(opp[:cut])
                    state='lead' if margin>0 else 'trail' if margin<0 else 'tie'
                    if state=='trail':
                        t=trajectory(g['home_runs'],g['away_runs'],home,cut)
                        category=next(k for k in CATEGORIES if t[1][k])
                cells[y,team,cut,state,category].update(G=1,**{outcome:1})
    return [dict(year=y,team=t,cutoff=c,state=s,category=k,**{f:v[f] for f in ('G','W','L','T')})
            for (y,t,c,s,k),v in sorted(cells.items())]


def preclinch_flow_summarize(rows):
    def total(rs):return {f:sum(r[f] for r in rs) for f in ('G','W','L','T')}
    result=dict(total=total(rows),states={s:total([r for r in rows if r['state']==s]) for s in STATES},
                trailing={c:total([r for r in rows if r['category']==c]) for c in CATEGORIES})
    for f in ('G','W','L','T'):
        require(sum(r[f] for r in result['states'].values())==result['total'][f],'state partition')
        require(sum(r[f] for r in result['trailing'].values())==result['states']['trail'][f],'trajectory partition')
    require(result['total']['G']==sum(result['total'][f] for f in ('W','L','T')),'outcome partition')
    return result


def preclinch_flow_analyze(rows):
    periods=[('no2020',set(range(2013,2026))-{2020}),('with2020',set(range(2013,2026)))]+[(str(y),{y}) for y in range(2013,2026)]
    return [dict(period=p,cutoff=c,own=preclinch_flow_summarize([r for r in rows if r['year'] in ys and r['cutoff']==c and r['team']=='d']),
                 peer=preclinch_flow_summarize([r for r in rows if r['year'] in ys and r['cutoff']==c and r['team']!='d']))
            for p,ys in periods for c in (6,7)]


def preclinch_flow_main(argv=None):
    p=argparse.ArgumentParser(description=PRECLINCH_FLOW_DOC)
    for k in ('innings','season','dates','out','csv'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args(argv);game_state_build(a.innings,a.season)
    ds=json.loads(a.dates.read_text());require(all(y['exact'] for y in ds['years']),'unresolved dates')
    dates={y['year']:y['date'] for y in ds['years']}
    games,n=read_input(a.innings);rows=preclinch_flow_aggregate(games,dates)
    result=dict(schema='aoi-preclinch-flow/1',plan_commit=ds['plan_commit'],input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,
                annual_checks=936,input_rows=n,dates=dates,year2026=ds['year2026'],comparisons=preclinch_flow_analyze(rows))
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    with a.csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps(result['comparisons'][1],ensure_ascii=False))


def preclinch_flow(argv=None):
    """preclinch_flow.py の入口（説明は PRECLINCH_FLOW_DOC）。
    """
    preclinch_flow_main(argv)


# ==== run_loss_tail（旧 run_loss_tail.py）

def run_loss_tail_main():
    steps=[('tests',[sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py']),
           ('analysis',[sys.executable,str(HERE/'analyses.py'),'loss_tail','analyze']),
           ('judgement',[sys.executable,str(HERE/'analyses.py'),'loss_tail','judge'])]
    records=[]
    for name,cmd in steps:
        result=subprocess.run(cmd,cwd=HERE.parents[1],text=True,capture_output=True)
        records.append(dict(stage=name,command=cmd,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
        print(f'{name}: exit={result.returncode}',flush=True)
        if result.returncode and name!='judgement':
            break
    code=records[-1]['exit_code']
    out=HERE/'outputs';out.mkdir(exist_ok=True)
    (out/'loss_tail_sequential.json').write_text(json.dumps(dict(stages=records,exit_code=code),ensure_ascii=False,indent=2)+'\n')
    return code


def run_loss_tail(argv=None):
    """Sequential tests -> analysis -> judgement; preserve actual child exit codes.
    """
    sys.exit(run_loss_tail_main())


# ==== same_score（旧 same_score.py）

def metrics(games):
    n=len(games);w=sum(a>b for a,b,*_ in games);l=sum(a<b for a,b,*_ in games);d=n-w-l
    return dict(g=n,w=w,l=l,d=d,win_rate=w/(w+l) if w+l else None,we_rate=(w+.5*d)/n if n else None)


def same_score_main():
    data=ROOT/'data/observations/r001/games.jsonl'
    meta=json.loads(data.with_suffix('.manifest.json').read_text())
    verify=json.loads((HERE/'outputs/official_verification.json').read_text())
    digest=analyze_sha(data)
    if (meta['sha256']!=digest or meta['unknown']!=0 or verify['games_sha256']!=digest or len(verify['checks'])!=156
        or {(c['year'],c['team']) for c in verify['checks'] if c['match']}!={(y,t) for y in YEARS for t in ANALYZE_TEAMS}):
        raise ValueError('source or verification mismatch')
    raw=[json.loads(s) for s in data.read_text().splitlines()]
    grouped=units(raw)
    maximum=max(max(g['hs'],g['as']) for g in raw)
    rows=[];totals={}
    for (year,team),gg in sorted(grouped.items()):
        if team not in ANALYZE_CL:continue
        for side in ['home','away']:
            selected=[g for g in gg if g[2]==side]
            cells=[]
            for score in range(maximum+1):
                r=dict(year=year,team=team,side=side,score=score,**metrics([g for g in selected if g[0]==score]))
                cells.append(r);rows.append(r)
            target=metrics(selected)
            if any(sum(r[k] for r in cells)!=target[k] for k in ['g','w','l','d']):
                raise AssertionError('score cells do not reconstruct outcomes')
            totals[year,team,side]=target['g']
    pooled=[]
    for omit in [False,True]:
        for label,teams in [('chunichi',{'d'}),('other_cl',ANALYZE_CL-{'d'})]:
            for side in ['home','away']:
                selected=[g for (y,t),gg in grouped.items() if t in teams and (not omit or y!=2020) for g in gg if g[2]==side]
                for score in range(8):
                    gg=[g for g in selected if (g[0]==score if score<7 else g[0]>=7)]
                    pooled.append(dict(scope='without2020' if omit else 'all',group=label,side=side,score=str(score) if score<7 else '7+',
                                       frequency=len(gg)/len(selected),**metrics(gg)))
    matched=[]
    for side in ['home','away']:
        for score in range(7):
            comparisons=[];missing=[]
            for y in YEARS:
                a=next(r for r in rows if r['year']==y and r['team']=='d' and r['side']==side and r['score']==score)
                other=[r for r in rows if r['year']==y and r['team']!='d' and r['side']==side and r['score']==score]
                ow=sum(r['w'] for r in other);ol=sum(r['l'] for r in other)
                if a['win_rate'] is None or ow+ol==0:missing.append(y)
                else:comparisons.append(dict(year=y,chunichi=a['win_rate'],other_cl=ow/(ow+ol),difference=a['win_rate']-ow/(ow+ol)))
            matched.append(dict(side=side,score=score,years=comparisons,missing_years=missing))
    with (HERE/'outputs/same_score_cells.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    result=dict(input_sha256=digest,script_sha256=analyze_sha(__file__),protocol_sha256=analyze_sha(HERE/'SAME_SCORE_PROTOCOL.md'),
                aggregation='pooled games; annual cells and same-year comparisons retained',pooled=pooled,matched_years=matched,exit_code=0)
    (HERE/'outputs/same_score_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for side in ['home','away']:
        print(side)
        for score in [str(k) for k in range(7)]+['7+']:
            a,b=[next(r for r in pooled if r['scope']=='all' and r['side']==side and r['score']==score and r['group']==group) for group in ['chunichi','other_cl']]
            print(score,f"d={a['w']}-{a['l']}-{a['d']} {a['win_rate']:.3f} other={b['win_rate']:.3f}")
    return 0


def same_score(argv=None):
    """Descriptive outcomes conditional on final runs; see SAME_SCORE_PROTOCOL.md.
    """
    try:sys.exit(same_score_main())
    except FileNotFoundError as e:print(str(e),file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError,TypeError) as e:print(str(e),file=sys.stderr);sys.exit(65)
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(70)


# ==== scoring（旧 scoring.py）

def scoring_main():
    data=ROOT/'data/observations/r001/games.jsonl'
    manifest=json.loads(data.with_suffix('.manifest.json').read_text())
    verify=json.loads((HERE/'outputs/official_verification.json').read_text())
    digest=analyze_sha(data)
    if (digest!=manifest['sha256'] or manifest['unknown']!=0 or digest!=verify['games_sha256']
        or len(verify['checks'])!=156
        or {(r['year'],r['team']) for r in verify['checks'] if r['match']}!={(y,t) for y in YEARS for t in ANALYZE_TEAMS}):
        raise ValueError('input provenance or official checks mismatch')
    games=[json.loads(s) for s in data.read_text().splitlines()]
    grouped=units(games)
    maximum=max(max(g['hs'],g['as']) for g in games)
    rows=[]
    for (year,team),gg in sorted(grouped.items()):
        if team not in ANALYZE_CL:
            continue
        for side in ['home','away']:
            scores=[g[0] for g in gg if g[2]==side]
            n=len(scores)
            counts=Counter(scores)
            vector=[counts[k] for k in range(maximum+1)]
            if sum(vector)!=n or sum(k*c for k,c in enumerate(vector))!=sum(scores):
                raise AssertionError('score frequency reconstruction failed')
            rows.append(dict(year=year,team=team,side=side,n=n,r=sum(scores),mean=st.mean(scores),
                             zero=counts[0]/n,up_to_two=sum(x<=2 for x in scores)/n,
                             five_plus=sum(x>=5 for x in scores)/n,counts=vector,
                             cumulative=[sum(vector[:k+1])/n for k in range(maximum+1)]))
    summaries={}
    for label,teams in [('chunichi',{'d'}),('other_cl',ANALYZE_CL-{'d'})]:
        for side in ['home','away']:
            for omit in [False,True]:
                selected=[r for r in rows if r['team'] in teams and r['side']==side and (not omit or r['year']!=2020)]
                summaries[f'{label}/{side}/'+('without2020' if omit else 'all')]={k:st.mean(r[k] for r in selected) for k in ['mean','zero','up_to_two','five_plus']}
    annual=[]
    for y in YEARS:
        d={r['side']:r for r in rows if r['team']=='d' and r['year']==y}
        other={side:st.mean(r['mean'] for r in rows if r['team']!='d' and r['year']==y and r['side']==side) for side in ['home','away']}
        annual.append(dict(year=y,home_mean=d['home']['mean'],away_mean=d['away']['mean'],
                           away_minus_home=d['away']['mean']-d['home']['mean'],
                           home_minus_others=d['home']['mean']-other['home'],away_minus_others=d['away']['mean']-other['away']))
    output=dict(data_sha256=digest,script_sha256=analyze_sha(__file__),protocol_sha256=analyze_sha(HERE/'SCORING_PROTOCOL.md'),
                maximum_runs=maximum,summaries=summaries,annual_chunichi=annual,rows=rows,exit_code=0)
    (HERE/'outputs/scoring_distribution.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(summaries=summaries,annual_chunichi=annual,exit_code=0),ensure_ascii=False,indent=2))
    return 0


def scoring(argv=None):
    """Observe scoring distributions, without attributing causes. See SCORING_PROTOCOL.md.
    """
    try:
        code=scoring_main()
    except FileNotFoundError as e:
        code=66; print(str(e),file=sys.stderr)
    except (ValueError,KeyError,TypeError) as e:
        code=65; print(str(e),file=sys.stderr)
    except Exception as e:
        code=70; print(f'{type(e).__name__}: {e}',file=sys.stderr)
    sys.exit(code)


# ==== scoring_spread（旧 scoring_spread.py）

def scoring_spread_main():
    source=HERE/'outputs/scoring_distribution.json'
    payload=json.loads(source.read_text())
    rows=[]
    for r in payload['rows']:
        counts=r['counts'];n=sum(counts)
        if n!=r['n'] or sum(k*c for k,c in enumerate(counts))!=r['r']:
            raise ValueError('invalid scoring frequency totals')
        mean=r['r']/n
        var=sum(c*(k-mean)**2 for k,c in enumerate(counts))/n
        rows.append(dict(year=r['year'],team=r['team'],side=r['side'],mean=mean,variance=var,sd=math.sqrt(var),
                         zero=counts[0]/n,one=counts[1]/n,two=counts[2]/n,up_to_one=sum(counts[:2])/n))
    summary={}
    for team in sorted({r['team'] for r in rows}):
        for side in ['home','away']:
            for omit in [False,True]:
                selected=[r for r in rows if r['team']==team and r['side']==side and (not omit or r['year']!=2020)]
                summary[f'{team}/{side}/'+('without2020' if omit else 'all')]={k:st.mean(r[k] for r in selected) for k in ['mean','variance','sd','zero','one','two','up_to_one']}
    result=dict(source_sha256=analyze_sha(source),games_sha256=payload['data_sha256'],script_sha256=analyze_sha(__file__),
                protocol_sha256=analyze_sha(HERE/'SCORING_SPREAD_PROTOCOL.md'),summaries=summary,rows=rows,
                note='Means of annual population variances and annual SDs are separate quantities; not pooled.',exit_code=0)
    (HERE/'outputs/scoring_spread.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k.endswith('/all')},indent=2))


def scoring_spread(argv=None):
    """Finite-season scoring variance and exact-score frequencies; no causal attribution.
    """
    scoring_spread_main()


# ==== 入口
COMMANDS = {
    "analyze": analyze,
    "batting_prediction": batting_prediction,
    "batting_size": batting_size,
    "clinch_interval": clinch_interval,
    "compare_external": compare_external,
    "early_scoring": early_scoring,
    "game_state": game_state,
    "home_away": home_away,
    "hypothesis_followup": hypothesis_followup,
    "inning_cutoff": inning_cutoff,
    "inning_features": inning_features,
    "inning_placement": inning_placement,
    "iso_counterexamples": iso_counterexamples,
    "late_reaction": late_reaction,
    "loss_tail": loss_tail,
    "matched_comeback": matched_comeback,
    "preclinch_dates": preclinch_dates,
    "preclinch_flow": preclinch_flow,
    "run_loss_tail": run_loss_tail,
    "same_score": same_score,
    "scoring": scoring,
    "scoring_spread": scoring_spread,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="analyses.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"analyses.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
