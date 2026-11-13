#!/usr/bin/env python3
"""monthly_run.py とは別の書き方（標準ライブラリだけ、math.fsum と中心化した和の最小二乗、
条件の判定も手書き）で単位と 4 つの形の件数を作り直し、outputs/ と照合する。

  python3 -I cycles/c002-gohantrust/monthly/monthly_verify.py
"""
import csv
import gzip
import hashlib
import json
import math
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[2] / "research" / "staple-price-survey" / "phase2_archive"
OUT = HERE / "outputs"


def read():
    P, H, C = {}, {}, {}
    with gzip.open(ARCHIVE / "japan_retail_price_rice_panel.csv.gz", "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["item_code"] == "1002" and r["variable"].endswith("_mean_city_yen_per_5kg"):
                P[(int(r["year"]), int(r["month"]))] = float(r["value"])
    with gzip.open(ARCHIVE / "engel_food_panel_monthly.csv.gz", "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            H[(int(r["year"]), int(r["month"]))] = r
    with gzip.open(ARCHIVE / "japan_cpi_food_cereals_panel.csv.gz", "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["frequency"] == "monthly":
                C[(r["series_id"], int(r["year"]), int(r["month"]))] = float(r["index_value"])
    return P, H, C


def back(ym, n):
    y, m = ym
    i = y * 12 + (m - 1) - n
    return (i // 12, i % 12 + 1)


def months(a, b):
    y, m = a
    while (y, m) <= b:
        yield (y, m)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def E(H, ym):
    return float(H[ym]["food_yen_month"]) / float(H[ym]["ce_yen_month"])


def ols(rows):
    """y = a + Σ b_j z_j を、中心化した和の正規方程式（クラメルの公式）で解く。z は 1 個か 2 個。"""
    n = len(rows)
    k = len(rows[0]) - 1
    my = math.fsum(r[0] for r in rows) / n
    mz = [math.fsum(r[1 + j] for r in rows) / n for j in range(k)]
    S = [[math.fsum((r[1 + i] - mz[i]) * (r[1 + j] - mz[j]) for r in rows) for j in range(k)] for i in range(k)]
    T = [math.fsum((r[1 + i] - mz[i]) * (r[0] - my) for r in rows) for i in range(k)]
    if k == 1:
        b = [T[0] / S[0][0]]
    else:
        det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
        b = [(T[0] * S[1][1] - S[0][1] * T[1]) / det, (S[0][0] * T[1] - S[1][0] * T[0]) / det]
    return my - sum(b[j] * mz[j] for j in range(k)), b


def units_a(P, H):
    def pair(s):
        p1 = back(s, 1)
        return (math.log(P[s] / P[p1]), math.log(P[p1] / P[back(s, 2)]), math.log(E(H, p1) / E(H, back(s, 13))))
    allm = list(months((2001, 2), (2025, 12)))
    pr = {s: pair(s) for s in allm}
    out = {}
    for i, t in enumerate(allm):
        if t < (2006, 2):
            continue
        tr = [pr[s] for s in allm[:i]]
        y, m, x = pr[t]
        f1 = math.fsum(r[0] for r in tr) / len(tr)
        a2, (r2,) = ols([(r[0], r[1]) for r in tr])
        a3, (r3, g3) = ols(tr)
        f2, f3 = a2 + r2 * m, a3 + r3 * m + g3 * x
        e = [abs(y), abs(y - f1), abs(y - f2), abs(y - f3)]
        tau = 0.001 / E(H, back(t, 1))
        out[t] = {"family": "A", "ax": abs(x) / tau, "a1": e[1] < e[0], "a2": e[2] < e[1], "a3": e[3] < e[2],
                  "gains": (e[0] - e[1], e[1] - e[2], e[2] - e[3]), "y": y, "x": x}
    return out


def units_b(P, H, C):
    out = {}
    for t in months((2001, 1), (2025, 12)):
        b = back(t, 12)
        e0 = E(H, b)
        food = float(H[b]["food_yen_month"])
        sr, sc = float(H[b]["rice_yen_month"]) / food, float(H[b]["cereals_yen_month"]) / food
        rel = {s: C[(s, *t)] / C[(s, *b)] for s in ("cereals", "food", "all_items")}

        def share_effect(s, ratio):  # F → F(1 + s(ratio−1))、C → C(1 + e0 s (ratio−1))
            return math.log((1 + s * (ratio - 1)) / (1 + e0 * s * (ratio - 1)))

        c = [share_effect(sr, P[t] / P[b]), share_effect(sc, rel["cereals"]), share_effect(1.0, rel["food"]),
             math.log(rel["food"] / rel["all_items"])]
        ye = math.log(E(H, t) / e0)
        tau = 0.001 / e0
        res = [abs(ye)] + [abs(ye - v) for v in c]
        row = {"family": "B", "yE": ye}
        for i in range(4):
            row[f"c{i + 1}"], row[f"ac{i + 1}"], row[f"l{i + 1}"] = c[i], abs(c[i]) / tau, res[i + 1] < res[i]
        out[t] = row
    return out


def holds(row, conds):
    ops = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b,
           "<=": lambda a, b: a <= b, "==": lambda a, b: a == b, "!=": lambda a, b: a != b}
    return all(ops[c["op"]](row[c["col"]], c["value"]) for c in conds)


def forms(p, U):
    y0, _, y1 = p["scope"]["seasons"].partition("-")
    rows = {t: r for t, r in U.items() if int(y0) <= t[0] <= int(y1) and holds(r, p["scope"]["where"])}
    A = {t: holds(r, p.get("if", [])) for t, r in rows.items()}
    B = {t: holds(r, p["then"]) for t, r in rows.items()}
    f = {"original": (A, B), "contrapositive": ({t: not B[t] for t in B}, {t: not A[t] for t in A})}
    if p.get("if"):
        f["converse"] = (B, A)
        f["inverse"] = ({t: not A[t] for t in A}, {t: not B[t] for t in B})
    res = {}
    for name, (X, Y) in f.items():
        n = sum(X.values())
        res[name] = (n, sum(X[t] and Y[t] for t in X), sorted(f"m{t[1]:02d}-{t[0]}" for t in X if X[t] and not Y[t]))
    return res


def main():
    P, H, C = read()
    U = {**{("A",) + t: r for t, r in units_a(P, H).items()}, **{("B",) + t: r for t, r in units_b(P, H, C).items()}}
    bad = 0
    # 単位の値（monthly_run.py の units.jsonl と）
    got = {}
    for line in (OUT / "units.jsonl").read_text(encoding="utf-8").splitlines():
        u = json.loads(line)
        got[(u["family"], u["season"], u["month"])] = u
    if set(got) != set(U):
        print("NG: 単位の集合が違う")
        bad += 1
    ties = 0
    for key, r in U.items():
        g = got[key]
        for c in ("ax", "yE", "c1", "c2", "c3", "c4", "ac1", "ac2", "ac3", "ac4", "y", "x"):
            if c in r and not math.isclose(r[c], g[c], rel_tol=1e-9, abs_tol=1e-12):
                print(f"NG: {key} {c} {r[c]} vs {g[c]}")
                bad += 1
        for i, c in enumerate(("a1", "a2", "a3")):
            if c in r and r[c] != g[c]:
                if abs(r["gains"][i]) < 1e-12:
                    ties += 1           # 誤差がほぼ同じで、浮動小数の差で入れ替わりうる
                else:
                    print(f"NG: {key} {c}")
                    bad += 1
        for c in ("l1", "l2", "l3", "l4"):
            if c in r and r[c] != g[c]:
                print(f"NG: {key} {c}")
                bad += 1
    print(f"units: {len(U)}（A {sum(k[0] == 'A' for k in U)}、B {sum(k[0] == 'B' for k in U)}）、"
          f"値と真偽の照合 {'OK' if bad == 0 else 'NG'}、同点に近くて照合を外したもの {ties}")
    # 4 つの形の件数と判例（propositions.jsonl と）
    props = tomllib.loads((HERE / "monthly_propositions.toml").read_text(encoding="utf-8"))["proposition"]
    res = {json.loads(x)["id"]: json.loads(x) for x in (OUT / "propositions.jsonl").read_text(encoding="utf-8").splitlines()}
    for p in props:
        fam = p["scope"]["where"][0]["value"]
        mine = forms(p, {k[1:]: v for k, v in U.items() if k[0] == fam})
        theirs = {f["form"]: (f["n"], f["hold"], sorted(c["unit"] for c in f["counterexamples"])) for f in res[p["id"]]["forms"]}
        ok = mine == theirs
        bad += not ok
        print(f"{p['id']:7s} forms {'OK' if ok else 'NG'}  " + "  ".join(f"{k}:{v[1]}/{v[0]}" for k, v in mine.items()))
    sha = hashlib.sha256((HERE / "monthly_propositions.toml").read_bytes()).hexdigest()
    sha2 = hashlib.sha256((HERE / "monthly_prelock_2026-11-13.md").read_bytes()).hexdigest()
    stamp = (HERE / "monthly_prelock_timestamp.txt").read_text(encoding="utf-8")
    fixed = sha in stamp and sha2 in stamp
    bad += not fixed
    print(f"prelock / propositions sha256 は固定時と同じ: {'OK' if fixed else 'NG'}")
    print("VERIFY:", "ALL OK" if bad == 0 else f"{bad} NG")
    return bad


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
