"""Exploratory score-pairing diagnostic; see PROTOCOL.md. Standard library only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

CL = {"g", "s", "db", "d", "t", "c"}
TEAMS = CL | {"h", "f", "b", "e", "l", "m"}
YEARS = range(2013, 2026)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def units(games):
    out = defaultdict(list)
    seen = set()
    for g in games:
        if g["key"] in seen:
            raise ValueError("duplicate game ID")
        seen.add(g["key"])
        year = int(g["date"][:4])
        if year not in YEARS or g["home"] not in TEAMS or g["away"] not in TEAMS:
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
        for team in TEAMS:
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


def describe(games):
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=Path, required=True)
    ap.add_argument("--replicates", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=20261003)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.replicates < 2:
        ap.error("at least two replicates required")
    meta_path = args.games.with_suffix(".manifest.json")
    meta = json.loads(meta_path.read_text())
    if meta["unknown"] != 0 or meta["sha256"] != sha(args.games):
        raise ValueError("unknown records or dataset hash mismatch")
    source = [json.loads(s) for s in args.games.read_text().splitlines()]
    grouped = units(source)
    summaries = {k: describe(v) for k, v in grouped.items()}
    rows = []
    for mode in ("side", "side_opponent"):
        for (year, team), games in sorted(grouped.items()):
            derived_seed = int.from_bytes(hashlib.sha256(f"{args.seed}/{mode}/{year}/{team}".encode()).digest()[:8], "big")
            r = {"mode": mode, "year": year, "team": team, "league": "C" if team in CL else "P",
                 **summaries[year, team], **shuffle_reference(games, mode, args.replicates, derived_seed)}
            if team in CL:
                others = [summaries[year, t]["home_away_gap"] for t in CL - {team}]
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
              "team_seasons": len(grouped), "games_sha256": sha(args.games),
              "dataset_manifest_sha256": sha(meta_path), "script_sha256": sha(__file__),
              "protocol_sha256": sha(Path(__file__).with_name("PROTOCOL.md")),
              "lag_correlations_descriptive_only": lag,
              "note": "Exploratory reference distributions; no causal or significance claim."}
    (args.out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
