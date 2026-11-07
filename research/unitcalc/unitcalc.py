#!/usr/bin/env python3
"""unitcalc: 単位付き計算（青いプロジェクト第2弾の道具。標準ライブラリのみ・1 ファイル）。

量 = 中心 m ± 半径 r（どちらも厳密な有理数）と次元 d（ビット詰めの int 1 つ）。
  * + - * / // % と冪は有理数のまま厳密に計算する。float は受け付けない。r = 0 が厳密な値。
  * 近似が避けられないのは「根（√ など）」と「有限桁での表示」だけ。そこでは近似の途中式を残し、
    真の値との差 δ を丸めずに厳密な値で出す（根は [下限, 上限] の誤差球、表示は余りの分数）。
  * 次元は 8bit x 32 スロットを 1 つの int に詰める。掛け算 = 足し算、割り算 = 引き算、一致 = int の比較。
    入力（足し引き・冪・// %）でも出力（-> 単位）でも次元を守り、守れなければ止まる。
  * 単位は表（Reg）で持つ。SI 基本単位と、SI 2019 の定義値から厳密に決まる定数（R_gas, N_A, k_B …）で始め、
    SI 以外の単位や個数・金額のような次元は --dim / -D で足せる。足した単位も同じ仕組みで、別経路は置かない。

  python research/unitcalc/unitcalc.py "3 kW * 2 h -> kWh"     # 式は引用符で囲む（* のため）
  python research/unitcalc/unitcalc.py --steps "2 m^2 ^ (1/2)" # 近似の途中式も出す
  printf '1 kWh -> J\n7 h // 2 h\n' | python research/unitcalc/unitcalc.py   # 式が無ければ 1 行 1 式で標準入力

終了コード（docs/propositions.md の 64 以上＝システム側の失敗に合わせる）:
  0 = 計算できた（近似の δ は出力に出る。終了コードでは区別しない）
  65 = 入力の誤り（構文・未知の単位・次元違反・0 での割り算など）  66 = 式がない  70 = 内部の不変条件が破れた
"""
import argparse
import json
import math
import re
import sys
from fractions import Fraction as F

PREC = 64   # 根を求める有効ビット数。CLI の --bits が書き換える

# ---- 次元: 1 スロット 8bit x 32。指数 e は e+32 を 0..63 で持つ（-32..31）。bit7 は桁上がり防止のガード --------
W, SLOTS, E0 = 8, 32, 32
ONES = int.from_bytes(b'\x01' * SLOTS, 'little')
BIAS, GUARD = ONES * E0, ONES << 7
RANGE = GUARD | (GUARD >> 1)
DIM0 = BIAS                                  # 無次元（全スロットの指数 0）
Z = F(0)


class CalcError(Exception):
    """入力の誤り。終了コード 65。"""


class ParseError(CalcError):
    pass


class UnitError(CalcError):
    pass


class DomainError(CalcError):
    pass


class DimRange(CalcError):
    """指数が -32..31 を超えた。"""


class DimFrac(CalcError):
    """次元の指数が整数にならない（例: √m）。"""


class DimError(CalcError):
    def __init__(self, a, b, op):
        CalcError.__init__(self, 'dim mismatch')
        self.a, self.b, self.op = a, b, op


def _chk(t):
    # 全スロットで (bit7, bit6) = (1, 0) なら -32..31 に収まっている。bit7 が 0 なら下溢れ、bit6 が 1 なら上溢れ
    if t & RANGE != GUARD:
        raise DimRange('次元の指数が -32..31 を超えた')
    return t ^ GUARD


def d_mul(a, b):
    """次元の積 = スロットごとの足し算。ガードを立ててから BIAS を引くのでスロット間の借りが出ない。"""
    return _chk(((a + b) | GUARD) - BIAS)


def d_div(a, b):
    """次元の商 = スロットごとの引き算。"""
    return _chk(((a | GUARD) - b) + BIAS)


def d_unpack(d):
    return [((d >> (W * i)) & 255) - E0 for i in range(SLOTS)]


def d_pack(es):
    if any(not -E0 <= e < E0 for e in es):
        raise DimRange('次元の指数が -32..31 を超えた')
    return sum((e + E0) << (W * i) for i, e in enumerate(es))


def d_scale(d, p, q):
    """各指数を p/q 倍する。整数にならなければ DimFrac。"""
    out = []
    for e in d_unpack(d):
        x = e * p
        if x % q:
            raise DimFrac('次元の指数が整数にならない（%d/%d 倍）' % (p, q))
        out.append(x // q)
    return d_pack(out)


# ---- 量 --------------------------------------------------------------------------------------------------
def _nn(a, b):
    if not b:
        return a
    return a + tuple(x for x in b if x not in a) if a else b


def _q(x):
    if isinstance(x, Q):
        return x
    if isinstance(x, (int, F)):
        return Q(F(x))
    raise TypeError('float など厳密でない数は使えない: %r' % (x,))


class Q:
    """m ± r、次元 d、途中式 n（近似が入ったときだけ文字列が入る）。"""
    __slots__ = ('m', 'r', 'd', 'n')

    def __init__(s, m, r=Z, d=DIM0, n=()):
        s.m, s.r, s.d, s.n = m, r, d, n

    def __repr__(s):
        return 'Q(%s ± %s, d=%#x)' % (s.m, s.r, s.d)

    def __neg__(s):
        return Q(-s.m, s.r, s.d, s.n)

    def __add__(s, o):
        o = _q(o)
        if s.d != o.d:
            raise DimError(s.d, o.d, '+')
        return Q(s.m + o.m, s.r + o.r, s.d, _nn(s.n, o.n))
    __radd__ = __add__

    def __sub__(s, o):
        o = _q(o)
        if s.d != o.d:
            raise DimError(s.d, o.d, '-')
        return Q(s.m - o.m, s.r + o.r, s.d, _nn(s.n, o.n))

    def __rsub__(s, o):
        return _q(o) - s

    def __mul__(s, o):
        o = _q(o)
        d = d_mul(s.d, o.d)
        if not s.r and not o.r:
            return Q(s.m * o.m, Z, d, _nn(s.n, o.n))
        return Q(s.m * o.m, abs(s.m) * o.r + abs(o.m) * s.r + s.r * o.r, d, _nn(s.n, o.n))
    __rmul__ = __mul__

    def __truediv__(s, o):
        o = _q(o)
        if not s.r and not o.r:
            d = d_div(s.d, o.d)
            if not o.m:
                raise ZeroDivisionError('0 で割る')
            return Q(s.m / o.m, Z, d, _nn(s.n, o.n))
        return s * _inv(o)

    def __rtruediv__(s, o):
        return _q(o) / s

    def __floordiv__(s, o):
        """切り捨ての商。次元は s/o。厳密な量どうしだけ（近似値は切り捨ての境が決まらない）。"""
        o = _q(o)
        _exact(s, o)
        return Q(F(s.m // o.m), Z, d_div(s.d, o.d))

    def __mod__(s, o):
        """余り = s − (s // o) x o。次元は s のまま（o が 円/個 のような割合でもよい）。"""
        o = _q(o)
        _exact(s, o)
        return Q(s.m - (s.m // o.m) * o.m, Z, s.d)

    def __pow__(s, e):
        e = F(e)
        p, q = e.numerator, e.denominator
        if abs(p) > 10000 or q > 64:
            raise DomainError('冪が大きすぎる')
        d = d_scale(s.d, p, q)
        return _ipow(_root(s, q) if q > 1 else s, p, d)


def _exact(s, o):
    if s.r or o.r:
        raise DomainError('近似値には // % を使えない')
    if not o.m:
        raise ZeroDivisionError('0 で割る')


def _inv(o):
    if abs(o.m) <= o.r:
        raise ZeroDivisionError('0 を含む範囲で割る')
    d = d_div(DIM0, o.d)
    if not o.r:
        return Q(1 / o.m, Z, d, o.n)
    t = o.m * o.m - o.r * o.r                 # 1/(m±r) は m/(m²−r²) ± r/(m²−r²) に含まれる
    return Q(o.m / t, o.r / t, d, o.n)


def _ipow(x, p, d):
    if not x.r:
        return Q(x.m ** p, Z, d, x.n)
    res, b, k = Q(F(1), Z, DIM0, x.n), (x if p >= 0 else _inv(x)), abs(p)
    while k:                                  # 二乗の繰り返し（指数のビットを下から見る）
        if k & 1:
            res = res * b
        k >>= 1
        if k:
            b = b * b
    return res


def _iroot(n, q):
    """⌊n^(1/q)⌋（n ≥ 0）。q=2 は math.isqrt、それ以外はビット長から始める整数 Newton。"""
    if q == 2:
        return math.isqrt(n)
    if n < 2:
        return n
    x = 1 << -(-n.bit_length() // q)          # 2^⌈bits/q⌉ ≥ 根
    while True:
        y = ((q - 1) * x + n // x ** (q - 1)) // q
        if y >= x:
            return x
        x = y


def _scaled(z, sh):
    """⌊z · 2^sh⌋（シフトだけで、割り算は 1 回）。"""
    n, d = z.numerator, z.denominator
    return (n << sh) // d if sh >= 0 else n // (d << -sh)


def _root(x, q):
    """x の q 乗根。完全冪なら厳密、そうでなければ誤差球（途中式つき）。"""
    d = d_scale(x.d, 1, q)
    neg = False
    if x.m < 0 and not x.r:
        if q % 2 == 0:
            raise DomainError('負の数の %d 乗根' % q)
        neg, x = True, Q(-x.m, Z, x.d, x.n)
    lo, hi = x.m - x.r, x.m + x.r
    if lo < 0:
        raise DomainError('負を含む範囲の根')
    if not x.r:
        a, b = _iroot(lo.numerator, q), _iroot(lo.denominator, q)
        if a ** q == lo.numerator and b ** q == lo.denominator:
            return Q(F(-a if neg else a, b), Z, d, x.n)
    e2 = hi.numerator.bit_length() - hi.denominator.bit_length()    # ≈ log2(hi)（±1）
    k = PREC - e2 // q                                              # 根が約 PREC ビットになるずらし幅
    sh = q * k
    nlo, nhi = _scaled(lo, sh), _scaled(hi, sh)
    rlo, rhi = _iroot(nlo, q), _iroot(nhi, q)
    note = '%s(%s): N=⌊x·2^%d⌋=%d  r=⌊N^(1/%d)⌋=%d  N−r^%d=%d  → 真の値 ∈ [%d, %d]/2^%d' % (
        '√' if q == 2 else '∛' if q == 3 else '%d乗根' % q, hi if x.r else x.m, sh, nhi, q, rhi, q,
        nhi - rhi ** q, rlo, rhi + 1, k)
    sc = F(1, 1 << (k + 1)) if k >= -1 else F(1 << -(k + 1))
    m, r = (rlo + rhi + 1) * sc, (rhi + 1 - rlo) * sc
    return Q(-m if neg else m, r, d, _nn(x.n, (note,)))


class Eq:
    """左辺 = 右辺（式の形だけ。次元と値の確認は run が行う）。"""
    __slots__ = ('l', 'r')

    def __init__(s, l, r):
        s.l, s.r = l, r


# ---- 単位表 ----------------------------------------------------------------------------------------------
BASE = ['kg', 'm', 's', 'A', 'K', 'mol', 'cd']
PREFIX = {'y': F(1, 10 ** 24), 'z': F(1, 10 ** 21), 'a': F(1, 10 ** 18), 'f': F(1, 10 ** 15), 'p': F(1, 10 ** 12),
          'n': F(1, 10 ** 9), '\u00b5': F(1, 10 ** 6), '\u03bc': F(1, 10 ** 6), 'u': F(1, 10 ** 6), 'm': F(1, 10 ** 3), 'c': F(1, 10 ** 2),
          'd': F(1, 10), 'da': F(10), 'h': F(100), 'k': F(10 ** 3), 'M': F(10 ** 6), 'G': F(10 ** 9),
          'T': F(10 ** 12), 'P': F(10 ** 15), 'E': F(10 ** 18), 'Z': F(10 ** 21), 'Y': F(10 ** 24)}
_J, _PA = dict(kg=1, m=2, s=-2), dict(kg=1, m=-1, s=-2)
# (記号, SI 組立値に対する倍率, 基本単位の指数, 接頭辞を付けられるか)。倍率はすべて厳密な定義値
TABLE = [
    ('m', 1, dict(m=1), 1), ('g', F(1, 1000), dict(kg=1), 1), ('s', 1, dict(s=1), 1), ('A', 1, dict(A=1), 1),
    ('K', 1, dict(K=1), 1), ('mol', 1, dict(mol=1), 1), ('cd', 1, dict(cd=1), 1),
    ('N', 1, dict(kg=1, m=1, s=-2), 1), ('Pa', 1, _PA, 1), ('J', 1, _J, 1), ('W', 1, dict(kg=1, m=2, s=-3), 1),
    ('C', 1, dict(A=1, s=1), 1), ('V', 1, dict(kg=1, m=2, s=-3, A=-1), 1), ('F', 1, dict(kg=-1, m=-2, s=4, A=2), 1),
    ('ohm', 1, dict(kg=1, m=2, s=-3, A=-2), 1), ('S', 1, dict(kg=-1, m=-2, s=3, A=2), 1),
    ('Wb', 1, dict(kg=1, m=2, s=-2, A=-1), 1), ('T', 1, dict(kg=1, s=-2, A=-1), 1),
    ('H', 1, dict(kg=1, m=2, s=-2, A=-2), 1), ('Hz', 1, dict(s=-1), 1), ('rad', 1, {}, 1), ('sr', 1, {}, 1),
    ('L', F(1, 1000), dict(m=3), 1), ('t', 1000, dict(kg=1), 1), ('eV', F('1.602176634e-19'), _J, 1),
    ('cal', F('4.184'), _J, 1), ('Wh', 3600, _J, 1), ('bar', 100000, _PA, 1), ('atm', 101325, _PA, 0),
    ('Torr', F(101325, 760), _PA, 0), ('mmHg', F('133.322387415'), _PA, 0), ('pct', F(1, 100), {}, 0),
    ('ppm', F(1, 10 ** 6), {}, 0),
    ('min', 60, dict(s=1), 0), ('h', 3600, dict(s=1), 0), ('d', 86400, dict(s=1), 0),
    ('in', F('0.0254'), dict(m=1), 0), ('ft', F('0.3048'), dict(m=1), 0), ('yd', F('0.9144'), dict(m=1), 0),
    ('mi', F('1609.344'), dict(m=1), 0), ('lb', F('0.45359237'), dict(kg=1), 0),
]
# SI 2019 の定義値（厳密）。名前は単位と衝突しないよう添字つき。R_gas と F_Far は定義値の積で、これも厳密
CONSTS = [
    ('c_0', F(299792458), dict(m=1, s=-1)), ('h_P', F('6.62607015e-34'), dict(kg=1, m=2, s=-1)),
    ('k_B', F('1.380649e-23'), dict(kg=1, m=2, s=-2, K=-1)), ('N_A', F('6.02214076e23'), dict(mol=-1)),
    ('q_e', F('1.602176634e-19'), dict(A=1, s=1)), ('g_n', F('9.80665'), dict(m=1, s=-2)),
    ('T_0', F('273.15'), dict(K=1)),                              # 0 °C の定義（温度の値。差ではない）
]
SYN = {'\u03a9': 'ohm', '\u2126': 'ohm', 'l': 'L'}
AFFINE = ('degC', '°C', '℃', 'degF', '°F', '℉')
ALIAS_ORDER = ('J', 'N', 'Pa', 'W', 'C', 'V', 'F', 'ohm', 'S', 'Wb', 'T', 'H', 'Hz')   # 次元の呼び名（同じ次元は先勝ち）
SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def sup(n):
    return str(n).translate(SUP)


class Reg:
    """単位表と次元スロットの名前。テストで汚し合わないよう、インスタンスごとに持つ。"""

    def __init__(s):
        s.names = list(BASE)
        s.t = {}
        for sym, k, ex, pre in TABLE:
            s.t[sym] = (Q(F(k), Z, s.dim(**ex)), bool(pre))
        for sym, k, ex in CONSTS:
            s.t[sym] = (Q(k, Z, s.dim(**ex)), False)
        s.t['R_gas'] = (s.t['N_A'][0] * s.t['k_B'][0], False)
        s.t['F_Far'] = (s.t['N_A'][0] * s.t['q_e'][0], False)
        s.alias = {}
        for sym in ALIAS_ORDER:
            s.alias.setdefault(s.t[sym][0].d, sym)

    def dim(s, /, **ex):
        es = [0] * SLOTS
        for name, e in ex.items():
            es[s.names.index(name)] = e
        return d_pack(es)

    def add_dim(s, name):
        """新しい基本次元（個数・金額など）。同名の単位（倍率 1）も同時にできる。"""
        s._free(name)
        if len(s.names) >= SLOTS:
            raise CalcError('次元スロットが満杯（%d）' % SLOTS)
        s.names.append(name)
        s.t[name] = (Q(F(1), Z, s.dim(**{name: 1})), False)

    def define(s, name, q, prefixable=False):
        s._free(name)
        if q.r or not q.m:
            raise CalcError('単位の定義は 0 でない厳密な値だけ: %s' % name)
        s.t[name] = (Q(q.m, Z, q.d), prefixable)

    def _free(s, name):
        """足したい名前が空いているか。接頭辞つきで読める名前（kg, mm など）も使用済みとして断る。"""
        try:
            s.unit(name)
        except UnitError:
            if name not in AFFINE:
                return
        raise CalcError('すでにある名前: %s' % name)

    def unit(s, name):
        name = SYN.get(name, name)
        if name in s.t:
            return s.t[name][0]
        for n in (2, 1):                                   # 'da' を 'd' より先に見る
            p, rest = name[:n], name[n:]
            if p in PREFIX and rest in s.t and s.t[rest][1]:
                return Q(PREFIX[p]) * s.t[rest][0]
        if name in AFFINE:
            raise UnitError('%s は原点がずれる単位（倍率だけでは換算できない）。差は K で書く' % name)
        raise UnitError('未知の単位: %s' % name)

    def dim_str(s, d):
        parts = [s.names[i] + (sup(e) if e != 1 else '') for i, e in enumerate(d_unpack(d)) if e and i < len(s.names)]
        return '·'.join(parts) or '無次元'


# ---- 構文 ------------------------------------------------------------------------------------------------
_TOK = re.compile(r'\s*(?:(?P<n>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|(?P<i>[^\W\d][\w°]*)'
                  r'|(?P<o>->|//|==|[-+*/^%(),=]))')
_SUPD = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
FUNCS = {'sqrt': F(1, 2), 'cbrt': F(1, 3)}


def tokenize(text):
    text = text.translate({ord('×'): '*', ord('·'): '*', ord('⋅'): '*', ord('÷'): '/', ord('−'): '-', ord('→'): '->'})
    text = re.sub('(⁻?)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', lambda m: '^' + ('-' if m.group(1) else '') + m.group(2).translate(_SUPD), text)
    out, pos = [], 0
    while text[pos:].strip():
        m = _TOK.match(text, pos)
        if not m:
            raise ParseError('読めない文字: %r' % text[pos:pos + 8].strip())
        pos = m.end()
        out.append((m.lastgroup, m.group(m.lastgroup)))
    return out


class Parser:
    def __init__(s, text, reg):
        s.reg, s.t, s.i = reg, tokenize(text), 0

    def peek(s, k=0):
        return s.t[s.i + k] if s.i + k < len(s.t) else (None, None)

    def take(s):
        tok = s.peek()
        s.i += 1
        return tok

    def want(s, v):
        if s.take()[1] != v:
            raise ParseError("'%s' が必要" % v)

    def stmt(s):
        """式 [-> 単位 | to 単位]、または 左辺 = 右辺。戻り値は (量 か Eq, 目標の単位 Q か None, 目標の表記)。"""
        x, tgt, label = s.expr(), None, ''
        if s.peek()[1] in ('=', '=='):
            s.take()
            x = Eq(x, s.expr())
        elif s.peek()[1] in ('->', 'to'):
            s.take()
            a = s.i
            if s.peek()[0] != 'i':
                raise ParseError('-> の後に単位が必要')
            tgt = s.unit_chain()
            label = ''.join(v for _, v in s.t[a:s.i])
        if s.peek()[0] is not None:
            raise ParseError('余分な入力: %s' % s.peek()[1])
        return x, tgt, label

    def expr(s):
        x = s.term()
        while s.peek()[1] in ('+', '-'):
            op = s.take()[1]
            y = s.term()
            x = x + y if op == '+' else x - y
        return x

    def term(s):
        x = s.factor()
        while s.peek()[1] in ('*', '/', '//', '%'):
            op = s.take()[1]
            y = s.factor()
            x = x * y if op == '*' else x / y if op == '/' else x // y if op == '//' else x % y
        return x

    def factor(s):
        if s.peek()[1] in ('-', '+'):
            op = s.take()[1]
            x = s.factor()
            return -x if op == '-' else x
        x = s.atom()
        if s.peek()[1] == '^':
            s.take()
            x = x ** s.exponent()
        return x

    def exponent(s):
        sign = -1 if s.peek()[1] == '-' else 1
        if s.peek()[1] in ('-', '+'):
            s.take()
        k, v = s.take()
        if k == 'n':
            return sign * s.num(v)
        if v != '(':
            raise ParseError('^ の後に数が必要')
        x = s.expr()
        s.want(')')
        if x.r or x.d != DIM0:
            raise ParseError('指数は厳密な無次元の数でなければならない')
        return sign * x.m

    @staticmethod
    def num(v):
        m = re.search('[eE]([+-]?\\d+)$', v)
        if m and abs(int(m.group(1))) > 1000:
            raise ParseError('10 の冪が大きすぎる: %s' % v)
        return F(v)

    def atom(s):
        k, v = s.peek()
        if k == 'n':
            s.take()
            return s.then_unit(Q(s.num(v)))
        if k == 'i':
            if v in FUNCS and s.peek(1)[1] == '(':
                s.take()
                s.take()
                x = s.expr()
                s.want(')')
                return s.then_unit(x ** FUNCS[v])
            return s.unit_chain()
        if v == '(':
            s.take()
            x = s.expr()
            s.want(')')
            return s.then_unit(x)
        raise ParseError('式が途中で終わった' if k is None else '予期しない: %s' % v)

    def then_unit(s, x):
        """無次元の値（数・括弧・関数の結果）の直後に単位名が続けば、その単位を掛ける。"""
        if x.d == DIM0 and s.peek()[0] == 'i' and s.peek()[1] != 'to':
            return x * s.unit_chain()
        return x

    def unit_chain(s):
        """単位名 [^冪] (* | /) 単位名 ...。演算子の次が単位名（または単位名で始まる括弧）のときだけ続く。
        '10 m / 2 s' や '10 m / (2 s)' は数で始まるので 10 m と 2 s に分かれ、'J/(mol*K)' は 1 つの単位になる。"""
        u = s.unit_term()
        while s.peek()[1] in ('*', '/') and s.unit_next():
            op = s.take()[1]
            v = s.unit_term()
            u = u * v if op == '*' else u / v
        return u

    def unit_next(s):
        k, v = s.peek(1)
        if v == '(':
            k, v = s.peek(2)
        return k == 'i' and v not in FUNCS and v != 'to'

    def unit_term(s):
        k, v = s.take()
        if v == '(':
            u = s.unit_chain()
            s.want(')')
        elif k == 'i':
            u = s.reg.unit(v)
        else:
            raise ParseError('単位名が必要')
        if s.peek()[1] == '^':
            s.take()
            u = u ** s.exponent()
        return u


def evaluate(text, reg):
    """式を評価する。戻り値は (量, 目標の単位 Q か None, 目標の表記)。"""
    try:
        return Parser(text, reg).stmt()
    except DimError as e:
        raise CalcError('🧭 %s ≠ %s  (%s)' % (reg.dim_str(e.a), reg.dim_str(e.b), e.op)) from None
    except ZeroDivisionError as e:
        raise CalcError(str(e)) from None


# ---- 出力 ------------------------------------------------------------------------------------------------
def _e10(a):
    """⌊log10 a⌋（a > 0）。ビット長で見当をつけ、±1 だけ直す。"""
    e = ((a.numerator.bit_length() - a.denominator.bit_length()) * 1233) >> 12     # log10(2) ≈ 1233/4096
    while a >= F(10) ** (e + 1):
        e += 1
    while a < F(10) ** e:
        e -= 1
    return e


def _cut(a, sig):
    """a > 0 を有効 sig 桁で切り捨てる。a = (q + frac) x 10^-s、0 ≤ frac < 1、q は sig 桁の整数。"""
    s = sig - 1 - _e10(a)
    x = a * F(10) ** s
    q = x.numerator // x.denominator
    return q, s, x - q


def _fmt(q, s, strip):
    """q x 10^-s を文字列にする。strip なら末尾の 0 を落とす（値は変わらない）。"""
    ds = str(q)
    if strip and q:
        t = len(ds) - len(ds.rstrip('0'))
        ds, s = ds[:len(ds) - t], s - t
    e = len(ds) - 1 - s
    if -5 < e < 15:
        if s <= 0:
            return ds + '0' * -s
        return ds[:-s] + '.' + ds[-s:] if len(ds) > s else '0.' + '0' * (s - len(ds)) + ds
    return ds[0] + ('.' + ds[1:] if len(ds) > 1 else '') + '×10' + sup(e)


def _fs(f):
    return str(f.numerator) if f.denominator == 1 else '%d/%d' % (f.numerator, f.denominator)


def _bound(a, up):
    """a を有効 3 桁に外向きに丸めた文字列（up なら上へ、そうでなければ下へ）。δ の範囲の表示用。"""
    if a == 0:
        return '0'
    neg = a < 0
    q, s, frac = _cut(abs(a), 3)
    if frac and up != neg:
        q += 1
    return ('-' if neg else '') + _fmt(q, s, False)


def render(x, label, sig, steps):
    """目標の単位に直した無次元の量 x を行にする。戻り値は (行のリスト, 機械向けの辞書)。"""
    rec = {'unit': label, 'mid': _fs(x.m), 'rad': _fs(x.r), 'exact': not x.r, 'notes': list(x.n)}
    lines = []
    if not x.r:
        if x.m == 0:
            shown, delta, frac, s = F(0), F(0), F(0), 0
            text = '0'
        else:
            sg = -1 if x.m < 0 else 1
            q, s, frac = _cut(abs(x.m), sig)
            shown = sg * q * F(10) ** -s
            delta = x.m - shown
            text = ('-' if sg < 0 else '') + _fmt(q, s, not frac)
        mark = '=' if not frac else '≈'
        lines.append(('%s %s %s' % (mark, text, label)).rstrip())
        rec.update(shown=text, delta=_fs(delta))
        if frac:
            lines.append('δ %s%s×10%s  (≈%s) %s' % (
                '-' if x.m < 0 else '+', _fs(frac), sup(-s), _bound(delta, delta > 0), label))
            if steps:
                lines.append('🪜 (%s)×10^%d = %d + %s' % (_fs(abs(x.m)), s, q, _fs(frac)))
    else:
        rho = x.r / abs(x.m) if x.m else None
        n_ok = min(sig, max(1, -_e10(rho))) if rho else sig       # 誤差半径で保証できる桁まで
        if x.m == 0:
            shown, text = F(0), '0'
        else:
            sg = -1 if x.m < 0 else 1
            q, s, _ = _cut(abs(x.m), n_ok)
            shown, text = sg * q * F(10) ** -s, ('-' if sg < 0 else '') + _fmt(q, s, False)
        lo, hi = x.m - x.r - shown, x.m + x.r - shown
        lines.append('≈ %s %s' % (text, label))
        lines.append('δ ∈ [%s, %s] %s' % (_bound(lo, False), _bound(hi, True), label))
        rec.update(shown=text, delta_lo=_fs(lo), delta_hi=_fs(hi))
    return [ln.rstrip() for ln in lines], rec


def _run_eq(e, text, reg, sig, steps):
    """左辺 = 右辺: 次元の一致（両辺とも無次元ならそれも知らせる）と、値が等しいか・どちらが大きいか。"""
    dl, dr = reg.dim_str(e.l.d), reg.dim_str(e.r.d)
    if e.l.d != e.r.d:
        raise CalcError('🧭 左辺 %s ≠ 右辺 %s' % (dl, dr))
    free = e.l.d == DIM0
    diff = e.l - e.r
    equal = (diff.m == 0) if not diff.r else (False if abs(diff.m) > diff.r else None)   # None = 範囲が重なり判定できない
    order = None if equal is None else 0 if equal else 1 if diff.m > 0 else -1             # 1: 左辺 > 右辺、-1: 左辺 < 右辺
    lines = ['🧭 左辺 %s  右辺 %s  ✅' % (dl, dr) + ('（両辺とも単位なし）' if free else '')]
    if equal:
        lines.append('✅ 左辺 = 右辺' + ('（厳密）' if not diff.r else ''))
    else:
        lines.append('❓ 誤差の範囲が重なり、等しいか判定できない' if equal is None else '≠ 左辺 %s 右辺（差 = 左辺 − 右辺）' % '><'[order < 0])
        label = '' if free else reg.alias.get(e.l.d) or dl
        lines.extend(render(Q(diff.m, diff.r, DIM0, diff.n), label, sig, steps)[0])
    if steps:
        lines.extend('🪜 ' + n for n in diff.n)
    rec = {'ok': True, 'expr': text, 'kind': 'eq', 'dim_left': dl, 'dim_right': dr, 'dimensionless': free,
           'equal': equal, 'order': order, 'diff_mid': _fs(diff.m), 'diff_rad': _fs(diff.r), 'notes': list(diff.n)}
    return lines, rec


def run(text, reg, sig=15, steps=False):
    """1 つの式を計算して (行, 辞書) を返す。入力の誤りは CalcError。"""
    x, tgt, label = evaluate(text, reg)
    if isinstance(x, Eq):
        return _run_eq(x, text, reg, sig, steps)
    if tgt is not None:
        if x.d != tgt.d:
            raise CalcError('🧭 出力の次元が合わない: 結果 %s ≠ 単位 %s' % (reg.dim_str(x.d), reg.dim_str(tgt.d)))
        v = x / tgt
        dstr = reg.dim_str(x.d)
    else:
        v, dstr = Q(x.m, x.r, DIM0, x.n), reg.dim_str(x.d)
        label = reg.alias.get(x.d) or ('' if x.d == DIM0 else dstr)
    lines, rec = render(v, label, sig, steps)
    free = x.d == DIM0
    lines.append('🧭 %s ✅' % dstr + ('（単位なし）' if free else ''))
    if steps:
        lines.extend('🪜 ' + n for n in x.n)
    rec.update(ok=True, expr=text, dim=dstr, dimensionless=free)
    if rec['exact'] and F(rec['mid']) != v.m:
        raise AssertionError('内部の不変条件: mid が値と一致しない')
    return lines, rec


def main(argv=None, stdin=None):
    ap = argparse.ArgumentParser(description='単位付きの厳密計算（式は引用符で囲む）')
    ap.add_argument('expr', nargs='*')
    ap.add_argument('--dim', action='append', default=[], metavar='NAME', help='基本次元を足す（個数・金額など）')
    ap.add_argument('-D', '--define', action='append', default=[], metavar='NAME=式', help="単位を足す 例: -D 'dozen=12 item'")
    ap.add_argument('--digits', type=int, default=15, help='表示の有効桁（既定 15）')
    ap.add_argument('--bits', type=int, default=64, help='根の有効ビット（既定 64）')
    ap.add_argument('--steps', action='store_true', help='近似の途中式を出す')
    ap.add_argument('--json', action='store_true', help='1 式 1 行の JSON')
    a = ap.parse_args(argv)
    global PREC
    PREC = a.bits
    reg, code = Reg(), 0
    try:
        for name in a.dim:
            reg.add_dim(name)
        for d in a.define:
            name, _, text = d.partition('=')
            x, tgt, _l = evaluate(text, reg)
            reg.define(name.strip(), x)
    except CalcError as e:
        print('❌ %s' % e)
        return 65
    exprs = [' '.join(a.expr).strip()] if a.expr else [ln.strip() for ln in (stdin or sys.stdin) if ln.strip() and not ln.lstrip().startswith('#')]
    exprs = [e for e in exprs if e]
    if not exprs:
        print('❌ 式がない')
        return 66
    for text in exprs:
        try:
            lines, rec = run(text, reg, a.digits, a.steps)
        except CalcError as e:
            lines, rec, code = ['❌ %s' % e], {'ok': False, 'expr': text, 'error': str(e)}, 65
        except AssertionError as e:
            lines, rec, code = ['💥 %s' % e], {'ok': False, 'expr': text, 'error': str(e)}, 70
        if a.json:
            print(json.dumps(rec, ensure_ascii=False))
        else:
            if not a.expr:
                print('▸ %s' % text)
            print('\n'.join(lines))
    return code


if __name__ == '__main__':
    sys.exit(main())
