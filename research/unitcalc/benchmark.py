#!/usr/bin/env python3
"""unitcalc の速さの目安。標準ライブラリのみ。時間の閾値は置かない（機械の負荷で変わる小規模測定）。

  python research/unitcalc/benchmark.py            # 表と生サンプル（JSON）を出す
各項目はウォームアップ後 7 回の中央値（1 回あたりの ns）。次元の積は、ビット詰め（d_mul）と
「スロットごとに取り出して足して詰め直す」素直な書き方（ref）を同じ入力で比べる。
"""
import json
import platform
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import unitcalc as u  # noqa: E402


def bench(name, fn, n, reps=7):
    fn()
    samples = []
    for _ in range(reps):
        t = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - t) / n)
    return {'name': name, 'ns_median': round(statistics.median(samples), 1), 'samples_ns': [round(x, 1) for x in samples]}


def main():
    reg = u.Reg()
    a, b = reg.dim(kg=1, m=2, s=-2), reg.dim(s=-1, A=-1)
    m3 = u.Q(u.F(3), u.Z, reg.dim(m=1))
    m7 = u.Q(u.F(7, 3), u.Z, reg.dim(m=1))
    two = u.Q(u.F(2))
    ref = lambda x, y: u.d_pack([p + q for p, q in zip(u.d_unpack(x), u.d_unpack(y))])   # noqa: E731
    assert ref(a, b) == u.d_mul(a, b)
    rows = [
        bench('d_mul（ビット詰め）', lambda: u.d_mul(a, b), 200000),
        bench('d_mul（ref: 取り出して足して詰め直す）', lambda: ref(a, b), 20000),
        bench('Q + Q（厳密）', lambda: m3 + m7, 100000),
        bench('Q * Q（厳密、次元も掛ける）', lambda: m3 * m7, 100000),
        bench('Q / Q（厳密）', lambda: m3 / m7, 100000),
        bench('√2（64 ビットの誤差球）', lambda: u._root(two, 2), 20000),
        bench("run('3 kW * 2 h -> kWh')（構文・計算・表示）", lambda: u.run('3 kW * 2 h -> kWh', reg), 5000),
        bench("run('10 J / 3 s -> W')（余りの δ つき）", lambda: u.run('10 J / 3 s -> W', reg), 5000),
    ]
    print(json.dumps({'python': platform.python_version(), 'machine': platform.machine(), 'system': platform.system(),
                      'rows': rows}, ensure_ascii=False))
    for r in rows:
        print('%-52s %10.0f ns/op' % (r['name'], r['ns_median']), file=sys.stderr)


if __name__ == '__main__':
    main()
