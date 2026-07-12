#!/usr/bin/env python3
"""Semaev S4 (3-term) relation RECONNAISSANCE for HYP_GLV_SEMAEV_001, experiment P1-m3.

WHAT THIS EXTENDS
-----------------
P1 (`experiments/p1_petit/semaev_solve.py`) does the REAL 2-term Semaev step: for a
target ``R`` it solves the third summation polynomial ``S3(x_i, X, x_R) = 0`` (a quadratic)
over each factor-base coordinate ``x_i``, then confirms every root by actual EC addition.

This module does the analogous MEASURED 3-term step. A 3-term relation is
``R = P_i + P_j + P_k`` (equivalently ``P_i + P_j + P_k + (-R) = O``), characterised by the
FOURTH summation polynomial vanishing:

    S4(x_i, x_j, x_k, x_R) = 0.

We use the resultant structure formalised in this repo's Lean layer as the NUMERIC
definition of S4 over F_p:

    S4(x1, x2, x3, x4) = Res_Y( S3(x1, x2, Y),  S3(x3, x4, Y) ).

Because S3 is symmetric in its three arguments, ``s3_coeffs(u, w, b, p)`` (reused verbatim
from P1) already returns the quadratic ``A Y^2 + B Y + C = S3(u, w, Y)`` in the *middle*
variable ``Y``. So for a fixed target ``R`` and each ORDERED pair ``(x_i, x_j)``:

    S4(x_i, x_j, X, x_R) = Res_Y( S3(x_i, x_j, Y),  S3(X, x_R, Y) )

is a polynomial of degree <= 4 in the unknown ``X = x_k``. We build its coefficients in
closed form and find its exact F_p roots (custom degree-<=4 root finder, cross-checked
against sympy). For every root that is a factor-base x-coordinate we CONFIRM by ACTUAL
``ec_add`` that some sign choice ``e_i P_i + e_j P_j + e_k P_k = R`` (the 8 = 2^3 sign
combinations). Only EC-confirmed relations are counted; in-base roots that fail every
sign-lift are counted separately as SPURIOUS.

HONEST COST STATEMENT
---------------------
For a base of ``N`` distinct x-coordinates and one target we solve one degree-<=4
polynomial per unordered pair: ``Theta(N^2)`` pair-solves (S4 is symmetric in x_i, x_j so
the two orders are redundant; the cost is O(|F|^2) as stated). Each pair-solve is a fixed
number of field operations plus a root extraction. This is NOT a subexponential index
calculus: it is an O(|F|^2 . deg-4-solve) reconnaissance whose relation set is verified,
by an independent O(|F|^3) brute force, to be exactly the true 3-term relation set.

Reuses P1/P0 verbatim (imported, not rewritten): ``s3_coeffs``, ``solve_quadratic``,
``tonelli_shanks``, ``neg`` (from p1_petit.semaev_solve); ``build_plain_base``,
``build_glv_base``, ``FactorBase`` (from p1_petit.semaev_solve); ``ec_add``, ``ec_mul``,
``find_toy_curve`` (from p0_glv_semaev.toy_curves).
"""
from __future__ import annotations

import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_EXP = os.path.dirname(_HERE)
_P0 = os.path.join(_EXP, "p0_glv_semaev")
_P1 = os.path.join(_EXP, "p1_petit")
for _d in (_P0, _P1):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import sympy  # noqa: E402

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve  # noqa: E402
from semaev_solve import (  # noqa: E402
    s3_coeffs, solve_quadratic, tonelli_shanks, neg,
    build_plain_base, build_glv_base, FactorBase,
)

Point = tuple  # (x, y) or None

# A single module-level RNG for the (result-independent) randomness of equal-degree
# splitting in the root finder. The factorisation is deterministic in OUTCOME; the random
# choices only affect how fast a split is found. Seeded for reproducible timing.
_ROOT_RNG = random.Random(0xC0FFEE)


# ================================================================= resultant of 2 quadratics

def resultant_quadratics(q1: tuple, q2: tuple, p: int) -> int:
    """Res_Y of two quadratics ``q1 = A1 Y^2 + B1 Y + C1`` and ``q2 = A2 Y^2 + B2 Y + C2``.

    Closed form (the Sylvester 4x4 determinant expanded):

        Res = (A1 C2 - C1 A2)^2 - (A1 B2 - B1 A2)(B1 C2 - C1 B2).

    ``resultant_sylvester`` computes the same value straight from the 4x4 Sylvester matrix;
    ``_selftest`` asserts the two agree with ``sympy.resultant`` and with the direct
    root-product ``(A1 A2)^2 prod (r1 - r2)`` on random inputs.
    """
    A1, B1, C1 = (c % p for c in q1)
    A2, B2, C2 = (c % p for c in q2)
    P = (A1 * C2 - C1 * A2) % p
    Q = (A1 * B2 - B1 * A2) % p
    R = (B1 * C2 - C1 * B2) % p
    return (P * P - Q * R) % p


def resultant_sylvester(q1: tuple, q2: tuple, p: int) -> int:
    """Res_Y via the explicit 4x4 Sylvester determinant (Laplace expansion), mod p.

    Sylvester matrix of two quadratics::

        | A1 B1 C1  0 |
        |  0 A1 B1 C1 |
        | A2 B2 C2  0 |
        |  0 A2 B2 C2 |
    """
    A1, B1, C1 = (c % p for c in q1)
    A2, B2, C2 = (c % p for c in q2)
    M = [
        [A1, B1, C1, 0],
        [0, A1, B1, C1],
        [A2, B2, C2, 0],
        [0, A2, B2, C2],
    ]
    return _det_mod(M, p)


def _det_mod(M: list, p: int) -> int:
    """Determinant of a small integer matrix mod prime p by fraction-free elimination."""
    n = len(M)
    A = [[x % p for x in row] for row in M]
    det = 1
    for col in range(n):
        piv = next((r for r in range(col, n) if A[r][col] % p != 0), None)
        if piv is None:
            return 0
        if piv != col:
            A[col], A[piv] = A[piv], A[col]
            det = (-det) % p
        inv = pow(A[col][col], -1, p)
        det = (det * A[col][col]) % p
        for r in range(col + 1, n):
            f = (A[r][col] * inv) % p
            if f:
                A[r] = [(A[r][c] - f * A[col][c]) % p for c in range(n)]
    return det % p


# ================================================================= S4 as a quartic in x3

def s4_poly_in_x3(xi: int, xj: int, xR: int, b: int, p: int) -> list:
    """Coefficients (low -> high) of ``X -> S4(xi, xj, X, xR)`` over F_p, degree <= 4.

    ``S4(xi, xj, X, xR) = Res_Y( S3(xi, xj, Y),  S3(X, xR, Y) )``. The first quadratic
    ``S3(xi, xj, Y) = A1 Y^2 + B1 Y + C1`` has constant coefficients; the second,
    ``S3(X, xR, Y) = A2(X) Y^2 + B2(X) Y + C2(X)``, has coefficients that are themselves
    degree-2 polynomials in ``X`` (obtained from ``s3_coeffs`` with the first argument
    symbolic; for ``a = 0``):

        A2(X) = (X - xR)^2                      = xR^2  - 2 xR X + X^2
        B2(X) = -(2 xR X^2 + 2 xR^2 X + 4 b)
        C2(X) =  xR^2 X^2 - 4 b X - 4 b xR

    The resultant closed form ``(A1 C2 - C1 A2)^2 - (A1 B2 - B1 A2)(B1 C2 - C1 B2)`` is then
    evaluated with polynomial (coefficient-list) arithmetic in ``X``. ``_selftest`` checks
    this quartic, evaluated at any ``x3``, equals the scalar ``resultant_quadratics`` with
    ``x3`` substituted -- so the quartic and the scalar resultant cannot silently disagree.
    """
    A1, B1, C1 = s3_coeffs(xi, xj, b, p)
    A2 = [(xR * xR) % p, (-2 * xR) % p, 1 % p]
    B2 = [(-4 * b) % p, (-2 * xR * xR) % p, (-2 * xR) % p]
    C2 = [(-4 * b * xR) % p, (-4 * b) % p, (xR * xR) % p]
    P = _p_sub(_p_scale(C2, A1, p), _p_scale(A2, C1, p), p)   # A1 C2 - C1 A2
    Q = _p_sub(_p_scale(B2, A1, p), _p_scale(A2, B1, p), p)   # A1 B2 - B1 A2
    R = _p_sub(_p_scale(C2, B1, p), _p_scale(B2, C1, p), p)   # B1 C2 - C1 B2
    return _p_trim(_p_sub(_p_mul(P, P, p), _p_mul(Q, R, p), p), p)


# ------------------------------------------------------------------ tiny F_p[X] helpers

def _p_trim(f: list, p: int) -> list:
    f = [c % p for c in f] or [0]
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    return f


def _p_scale(f: list, k: int, p: int) -> list:
    return [(k * c) % p for c in f]


def _p_sub(a: list, b: list, p: int) -> list:
    n = max(len(a), len(b))
    return _p_trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p
                    for i in range(n)], p)


def _p_mul(a: list, b: list, p: int) -> list:
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                r[i + j] = (r[i + j] + ai * bj) % p
    return _p_trim(r, p)


def _p_divmod(a: list, b: list, p: int):
    a = _p_trim(a, p)
    b = _p_trim(b, p)
    if b == [0]:
        raise ZeroDivisionError("division by zero polynomial")
    inv = pow(b[-1], -1, p)
    q = [0] * max(1, len(a) - len(b) + 1)
    r = list(a)
    while len(r) >= len(b) and _p_trim(r, p) != [0]:
        r = _p_trim(r, p)
        if len(r) < len(b):
            break
        d = len(r) - len(b)
        coef = (r[-1] * inv) % p
        q[d] = coef
        for i, bi in enumerate(b):
            r[d + i] = (r[d + i] - coef * bi) % p
    return _p_trim(q, p), _p_trim(r, p)


def _p_gcd(a: list, b: list, p: int) -> list:
    a = _p_trim(a, p)
    b = _p_trim(b, p)
    while b != [0]:
        _, r = _p_divmod(a, b, p)
        a, b = b, r
    if a != [0]:
        inv = pow(a[-1], -1, p)
        a = [(c * inv) % p for c in a]
    return a


def _p_powmod(base: list, e: int, mod: list, p: int) -> list:
    result = [1]
    b = _p_divmod(base, mod, p)[1]
    while e > 0:
        if e & 1:
            result = _p_divmod(_p_mul(result, b, p), mod, p)[1]
        e >>= 1
        if e:
            b = _p_divmod(_p_mul(b, b, p), mod, p)[1]
    return _p_trim(result, p)


# ================================================================= exact F_p root finding

def fp_roots(coeffs: list, p: int):
    """All distinct roots in F_p of the polynomial with coefficients ``coeffs`` (low->high).

    Returns a sorted list of roots, or the sentinel ``None`` when the polynomial is
    identically zero (every field element is a root -- callers must handle that degenerate
    case without enumerating F_p). Method:

      1. distinct-root part ``g = gcd(f, X^p - X)`` (product of ``(X - r)`` over all F_p
         roots, squarefree, degree <= deg f);
      2. extract the roots of ``g`` by Cantor-Zassenhaus equal-degree splitting into linear
         factors (direct formulas for degree <= 2).

    ``X^p mod f`` is computed by fast modular exponentiation, so the whole solve is a fixed
    number of field/polynomial operations independent of |F| (the honest "deg-4 solve").
    Cross-checked against brute-force evaluation and ``sympy`` in ``_selftest``.
    """
    f = _p_trim(coeffs, p)
    if f == [0]:
        return None            # identically zero: degenerate, caller decides
    if len(f) == 1:
        return []              # nonzero constant: no roots
    # squarefree product of all F_p linear factors
    xp = _p_powmod([0, 1], p, f, p)           # X^p mod f
    g = _p_gcd(f, _p_sub(xp, [0, 1], p), p)   # gcd(f, X^p - X)
    if len(g) == 1:
        return []
    roots: list = []
    _extract_linear_roots(g, roots, p)
    return sorted(set(roots))


def _extract_linear_roots(g: list, out: list, p: int) -> None:
    """Append the roots of a squarefree ``g`` that splits completely over F_p."""
    g = _p_trim(g, p)
    d = len(g) - 1
    if d <= 0:
        return
    if d == 1:                                  # c1 X + c0
        out.append((-g[0]) * pow(g[1], -1, p) % p)
        return
    if d == 2:                                  # quadratic: closed form (reuse TS)
        A, B, C = g[2], g[1], g[0]
        for r in solve_quadratic(A, B, C, p):
            out.append(r)
        return
    # d >= 3: Cantor-Zassenhaus split (all irreducible factors are linear here)
    while True:
        c = _ROOT_RNG.randrange(p)
        h = _p_powmod([c, 1], (p - 1) // 2, g, p)     # (X + c)^((p-1)/2) mod g
        t = _p_gcd(g, _p_sub(h, [1], p), p)           # gcd(g, (X+c)^((p-1)/2) - 1)
        dt = len(t) - 1
        if 0 < dt < d:
            _extract_linear_roots(t, out, p)
            _extract_linear_roots(_p_divmod(g, t, p)[0], out, p)
            return


# ================================================================= 8-sign EC confirmation

def confirm_relation3(Pi, Pj, Pk, R, p: int):
    """Ground truth. Is there ``(e_i, e_j, e_k) in {+1,-1}^3`` with ``e_i Pi + e_j Pj + e_k Pk = R``?

    Recomputes the 8 signed sums by ACTUAL ec_add and compares to R in the group. Returns
    the first matching sign triple, else None. (Checking the 8 combinations against ``R`` is
    complete: a sum equal to ``-R`` corresponds to the negated sign triple, which is also
    among the 8, so ``-R`` need not be tested separately.)
    """
    for ei in (1, -1):
        Ai = Pi if ei == 1 else neg(Pi, p)
        for ej in (1, -1):
            Aj = Pj if ej == 1 else neg(Pj, p)
            AiAj = ec_add(Ai, Aj, 0, p)
            for ek in (1, -1):
                Ak = Pk if ek == 1 else neg(Pk, p)
                if ec_add(AiAj, Ak, 0, p) == R:
                    return (ei, ej, ek)
    return None


# ================================================================= relation search per target

def search_relations3(curve: ToyCurve, base: FactorBase, R):
    """Solve ``S4(x_i, x_j, X, x_R) = 0`` over the base for one target R; EC-confirm each root.

    Loops unordered pairs ``i < j`` (S4 is symmetric in x_i, x_j, so the reverse order is
    redundant -- the reported field-solve cost is still O(|F|^2)). For each pair it builds
    the degree-<=4 quartic in the unknown ``x_k``, finds its exact F_p roots, and for every
    root that is a base coordinate ``k`` distinct from ``i, j`` it runs the 8-sign EC lift.

    Returns per-target counters:
      pair_solves      : number of quartic solves (== number of i<j pairs)
      roots_total      : total F_p roots returned across all quartics
      roots_in_base    : (i,j,k) candidates whose solved x_k is a distinct base coordinate
      confirmed_triples: set of frozenset{i,j,k} that EC-confirm as a 3-term relation
      spurious         : roots_in_base candidates that lift to NO real EC relation
      s4_nonzero       : sanity failures where a solved root does not zero S4 (must be 0)
      degenerate_pairs : pairs whose quartic was identically zero (handled by full scan)
      example          : one confirmed relation (dict) or None
    """
    p, b = curve.p, curve.b
    xR = R[0]
    xset = base.xset
    pts = base.points
    n = len(pts)

    pair_solves = 0
    roots_total = 0
    roots_in_base = 0
    spurious = 0
    s4_nonzero = 0
    degenerate_pairs = 0
    confirmed = set()
    example = None

    for i in range(n):
        Pi = pts[i]
        xi = Pi[0]
        for j in range(i + 1, n):
            Pj = pts[j]
            xj = Pj[0]
            poly = s4_poly_in_x3(xi, xj, xR, b, p)
            pair_solves += 1
            roots = fp_roots(poly, p)
            if roots is None:
                # S4 vanishes for every x3: degenerate. Fall back to scanning the base so
                # the search stays complete (keeps the brute-force cross-check exact).
                degenerate_pairs += 1
                roots = [Pk[0] for Pk in pts]
            for X in roots:
                roots_total += 1
                k = xset.get(X)
                if k is None or k == i or k == j:
                    continue
                # independent sanity: the reported root must actually zero S4
                val = 0
                for e, ce in enumerate(poly):
                    val = (val + ce * pow(X, e, p)) % p
                if val != 0 and poly != [0]:
                    s4_nonzero += 1
                    continue
                roots_in_base += 1
                Pk = pts[k]
                e = confirm_relation3(Pi, Pj, Pk, R, p)
                if e is None:
                    spurious += 1
                    continue
                triple = frozenset((i, j, k))
                if triple not in confirmed and example is None:
                    example = {
                        "i": i, "j": j, "k": k,
                        "e_i": e[0], "e_j": e[1], "e_k": e[2],
                        "P_i": list(Pi), "P_j": list(Pj), "P_k": list(Pk),
                        "R": [R[0], R[1]],
                    }
                confirmed.add(triple)

    return {
        "pair_solves": pair_solves,
        "roots_total": roots_total,
        "roots_in_base": roots_in_base,
        "confirmed_triples": confirmed,
        "spurious": spurious,
        "s4_nonzero": s4_nonzero,
        "degenerate_pairs": degenerate_pairs,
        "example": example,
    }


# ================================================================= self-test

def _selftest() -> None:
    rng = random.Random(2024)

    # (1) Resultant: closed form == Sylvester determinant == sympy.resultant, and both ==
    #     the direct root-product (A1 A2)^2 prod (r1 - r2) on quadratics with prescribed roots.
    from sympy import Poly, resultant, symbols
    Xs = symbols("X")
    p = 1_000_003
    for _ in range(1500):
        A1, B1, C1, A2, B2, C2 = (rng.randrange(p) for _ in range(6))
        q1, q2 = (A1, B1, C1), (A2, B2, C2)
        closed = resultant_quadratics(q1, q2, p)
        sylv = resultant_sylvester(q1, q2, p)
        ref = int(resultant(Poly([A1, B1, C1], Xs), Poly([A2, B2, C2], Xs))) % p
        assert closed == sylv == ref, (closed, sylv, ref)
    # root-product form on prescribed-root quadratics
    for _ in range(1500):
        A1, A2 = rng.randrange(1, p), rng.randrange(1, p)
        r1 = [rng.randrange(p) for _ in range(2)]
        r2 = [rng.randrange(p) for _ in range(2)]
        q1 = (A1, (-A1 * (r1[0] + r1[1])) % p, (A1 * r1[0] * r1[1]) % p)
        q2 = (A2, (-A2 * (r2[0] + r2[1])) % p, (A2 * r2[0] * r2[1]) % p)
        prod = (A1 * A1 % p) * (A2 * A2 % p) % p
        for a in r1:
            for c in r2:
                prod = prod * ((a - c) % p) % p
        assert resultant_quadratics(q1, q2, p) == prod
        assert resultant_sylvester(q1, q2, p) == prod
    print("  [1] Res(closed) == Res(Sylvester) == sympy.resultant == root-product  (3000 random) OK")

    # (2) The quartic X -> S4(xi,xj,X,xR) evaluated at any x3 equals the scalar Res_Y with
    #     x3 substituted (ties the polynomial builder to the scalar resultant).
    b = 7
    for _ in range(3000):
        xi, xj, xR, x3 = (rng.randrange(p) for _ in range(4))
        poly = s4_poly_in_x3(xi, xj, xR, b, p)
        val = 0
        for e, ce in enumerate(poly):
            val = (val + ce * pow(x3, e, p)) % p
        ref = resultant_quadratics(s3_coeffs(xi, xj, b, p), s3_coeffs(x3, xR, b, p), p)
        assert val == ref, (val, ref)
    print("  [2] S4 quartic(x3) == scalar Res_Y(S3(xi,xj),S3(x3,xR))  (3000 random) OK")

    # (3) Root finder: agrees with brute-force evaluation and with sympy on random polys.
    for pp in (65_539, 1_048_609, 16_777_333):
        for _ in range(400):
            deg = rng.randrange(0, 5)
            coeffs = [rng.randrange(pp) for _ in range(deg + 1)]
            if coeffs and coeffs[-1] == 0:
                coeffs[-1] = 1
            got = fp_roots(coeffs, pp)
            if got is None:
                assert all(c % pp == 0 for c in coeffs)
                continue
            brute = sorted(x for x in range(min(pp, 4000))
                           if sum(c * pow(x, e, pp) for e, c in enumerate(coeffs)) % pp == 0)
            # compare on the scanned window only (pp large; roots are few)
            got_win = [r for r in got if r < min(pp, 4000)]
            assert got_win == brute, (coeffs, got_win, brute)
            for r in got:
                assert sum(c * pow(r, e, pp) for e, c in enumerate(coeffs)) % pp == 0
    print("  [3] fp_roots == brute-force evaluation on 3 fields  (1200 random polys) OK")

    # (4) On a real curve: every actual signed 3-term sum P_i (+/-) P_j (+/-) P_k = R zeroes
    #     S4(x_i,x_j,x_R) at x_k, and the S4-solve recovers x_k as a root.
    C = find_toy_curve(16, seed=1, require_cofactor_one=True)
    fb = build_plain_base(C, 10)
    p, b = C.p, C.b
    checked = 0
    for ai in range(len(fb.points)):
        for aj in range(len(fb.points)):
            for ak in range(len(fb.points)):
                if len({ai, aj, ak}) < 3:
                    continue
                Pi, Pj, Pk = fb.points[ai], fb.points[aj], fb.points[ak]
                for si in (1, -1):
                    for sj in (1, -1):
                        for sk in (1, -1):
                            R = ec_add(ec_add(
                                (Pi[0], si * Pi[1] % p),
                                (Pj[0], sj * Pj[1] % p), 0, p),
                                (Pk[0], sk * Pk[1] % p), 0, p)
                            if R is None:
                                continue
                            poly = s4_poly_in_x3(Pi[0], Pj[0], R[0], b, p)
                            val = 0
                            for e, ce in enumerate(poly):
                                val = (val + ce * pow(Pk[0], e, p)) % p
                            assert val == 0, "S4 nonzero for a real 3-term relation"
                            rts = fp_roots(poly, p)
                            assert rts is None or Pk[0] in rts, "S4-solve missed x_k"
                            checked += 1
    print(f"  [4] real signed 3-term sums: S4 vanishes and x_k is recovered  ({checked} sums) OK")

    # (5) GLV base is orbit-closed (sanity, reused P1 builder).
    g = build_glv_base(C, 24)
    assert g.n_distinct_x == 24 and g.n_orbits == 8 and g.storage_units == 8
    print("  [5] GLV base 24 x-coords in 8 orbits, 8 stored  OK")
    print("semaev4_solve self-test OK")


if __name__ == "__main__":
    _selftest()
