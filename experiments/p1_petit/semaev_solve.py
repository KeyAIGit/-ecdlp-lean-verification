#!/usr/bin/env python3
"""Semaev S3 relation SOLVING (not enumeration) for HYP_GLV_SEMAEV_001, experiment P1.

WHAT THIS CLOSES vs P0
----------------------
P0 (`experiments/p0_glv_semaev/`) found 2-term relations by ENUMERATING every pair
sum ``P_i +- P_j`` of the factor base and hashing their x-coordinates -- ``Theta(|F|^2)``
group operations per factor base. That is not an index-calculus relation step; it is a
birthday table.

P1 does the REAL 2-term Semaev step: for a target ``R`` and each factor-base
x-coordinate ``x_i`` we SOLVE the third summation polynomial

    S3(x_i, X, x_R) = 0                      (a quadratic in the unknown X over F_p)

for ``X``. Each solve is O(1) field operations plus one modular square root
(Tonelli-Shanks). Cost is therefore ``O(|F|)`` field-solves per target, NOT ``O(|F|^2)``.
For every root ``X`` that is a factor-base x-coordinate we CONFIRM the relation by
ACTUAL elliptic-curve addition: some ``e_i P_i + e_j P_j = R`` with ``e in {+1,-1}``.
Only EC-confirmed relations are counted; roots whose sign-lift produces no real EC
relation are counted separately as SPURIOUS.

Third summation polynomial for ``E : y^2 = x^3 + b`` (a = 0). The general S3 is

    S3(X1,X2,X3) = (X1-X2)^2 X3^2 - 2[(X1+X2)(X1 X2 + a) + 2b] X3
                   + [(X1 X2 - a)^2 - 4b(X1+X2)].

Collected as a quadratic ``A X2^2 + B X2 + C`` in the middle variable (a = 0):

    A = (X1 - X3)^2
    B = -(2 X1 X3 (X1 + X3) + 4b)
    C = X1^2 X3^2 - 4b (X1 + X3)

Semaev's theorem: ``S3(x1,x2,x3) = 0`` iff there exist y_i with ``(x_i, y_i)`` on ``E``
and ``P1 + P2 + P3 = O`` for some sign choice. Hence for on-curve x-coordinates a
vanishing S3 ALWAYS lifts to a real EC relation; the measured spurious rate is a direct
empirical check of that theorem, not an assumption.

This module reuses the P0 curve family and EC arithmetic verbatim (imported, not
rewritten): ``find_toy_curve``, ``ec_add``, ``ec_mul``.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

# Reuse the corrected cofactor-1 curve generator and EC arithmetic from P0.
_P0 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "p0_glv_semaev")
if _P0 not in sys.path:
    sys.path.insert(0, _P0)

import sympy  # noqa: E402

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve  # noqa: E402

Point = tuple  # (x, y) or None


# ------------------------------------------------------------------ modular sqrt

def tonelli_shanks(n: int, p: int):
    """Return a square root of ``n`` mod prime ``p`` (or ``None`` if ``n`` is a non-residue).

    Fast path for ``p = 3 (mod 4)`` where ``sqrt(n) = n^{(p+1)/4}``. General Tonelli-Shanks
    otherwise. Deterministic given (n, p): the non-residue search walks 2,3,4,... so the
    same z is always chosen. This is our own implementation (the task asks for it); it is
    cross-checked against ``sympy.sqrt_mod`` in ``_selftest``.
    """
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    # Euler criterion: n must be a quadratic residue.
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        r = pow(n, (p + 1) // 4, p)
        return r
    # Write p - 1 = q * 2^s with q odd.
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Find a quadratic non-residue z (deterministic ascending search).
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
        # Find least i, 0 < i < m, with t^{2^i} = 1.
        i = 0
        t2i = t
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
            if i == m:
                return None  # should not happen for a genuine residue
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


# ------------------------------------------------------------------ S3 quadratic solve

def s3_coeffs(x1: int, x3: int, b: int, p: int):
    """Coefficients (A, B, C) of ``S3(x1, X, x3) = A X^2 + B X + C`` over F_p (a = 0)."""
    A = (x1 - x3) * (x1 - x3) % p
    B = -(2 * x1 * x3 * (x1 + x3) + 4 * b) % p
    C = (x1 * x1 * x3 * x3 - 4 * b * (x1 + x3)) % p
    return A % p, B % p, C % p


def s3_eval(x1: int, x2: int, x3: int, b: int, p: int) -> int:
    """Evaluate S3 directly (used as an independent check that a solved root vanishes)."""
    A, B, C = s3_coeffs(x1, x3, b, p)
    return (A * x2 * x2 + B * x2 + C) % p


def solve_quadratic(A: int, B: int, C: int, p: int):
    """All roots in F_p of ``A X^2 + B X + C = 0``.

    Returns a sorted list of 0, 1, or 2 distinct roots. The degenerate all-field-is-root
    case (A = B = C = 0) returns the sentinel ``None`` so callers can skip it rather than
    iterate over F_p.
    """
    A %= p
    B %= p
    C %= p
    if A == 0:
        if B == 0:
            if C == 0:
                return None  # every field element is a root; degenerate, caller skips
            return []
        return [(-C) * pow(B, -1, p) % p]
    disc = (B * B - 4 * A * C) % p
    r = tonelli_shanks(disc, p)
    if r is None:
        return []
    inv2A = pow(2 * A % p, -1, p)
    r1 = (-B + r) * inv2A % p
    r2 = (-B - r) * inv2A % p
    return sorted({r1, r2})


# ------------------------------------------------------------------ EC relation confirmation

def neg(P, p: int):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def confirm_relation(Pi, Pj, R, p: int):
    """Ground truth. Is there ``e_i, e_j in {+1,-1}`` with ``e_i Pi + e_j Pj = R``?

    Recomputes the four signed sums by ACTUAL ec_add and compares to R in the group.
    Returns (e_i, e_j) for the first match, else None.
    """
    for ei in (1, -1):
        A = Pi if ei == 1 else neg(Pi, p)
        for ej in (1, -1):
            Bp = Pj if ej == 1 else neg(Pj, p)
            if ec_add(A, Bp, 0, p) == R:
                return (ei, ej)
    return None


# ------------------------------------------------------------------ factor bases

def _canonical_point(x: int, b: int, p: int):
    """The on-curve point (x, y) with y the Tonelli-Shanks root, or None if x is off-curve."""
    rhs = (x * x * x + b) % p
    y = tonelli_shanks(rhs, p)
    if y is None:
        return None
    return (x, y)


@dataclass
class FactorBase:
    variant: str            # "plain" or "glv-orbit"
    points: list            # canonical (x, y) points, one per distinct x-coordinate
    xset: dict              # x-coordinate -> index into points
    n_distinct_x: int       # effective size (S3 solves iterate over these)
    n_orbits: int           # distinct GLV/x^3 orbits == distinct u = x^3 values
    storage_units: int      # points that must be STORED (seeds); orbit members are free


def build_plain_base(curve: ToyCurve, N: int) -> FactorBase:
    """The N on-curve points with the smallest x-coordinates (deterministic, like P0)."""
    p, b = curve.p, curve.b
    pts = []
    x = 0
    while len(pts) < N and x < p:
        P = _canonical_point(x, b, p)
        if P is not None:
            pts.append(P)
        x += 1
    if len(pts) < N:
        raise RuntimeError(f"only {len(pts)} points < requested N={N}")
    xset = {P[0]: i for i, P in enumerate(pts)}
    u = {(P[0] ** 3) % p for P in pts}
    return FactorBase("plain", pts, xset, len(pts), len(u), storage_units=len(pts))


def build_glv_base(curve: ToyCurve, N: int) -> FactorBase:
    """GLV-orbit-closed base with exactly N distinct x-coordinates in N/3 orbits.

    Take seed x-coordinates (smallest first) and close each under the order-3 GLV orbit
    ``{x, beta x, beta^2 x}`` (all on the curve because ``(beta x)^3 + b = x^3 + b``). The
    three orbit members share the invariant ``u = x^3``, so only ONE seed per orbit is
    stored; the other two are recovered for free by multiplying by beta. Effective size
    (the count the S3 solve iterates over) is matched to the plain base at N distinct x.
    """
    p, b, beta = curve.p, curve.b, curve.beta
    if N % 3 != 0:
        raise ValueError("glv base size N must be a multiple of 3 (orbit size)")
    pts = []
    seen = set()
    n_orbits = 0
    storage = 0
    x = 0
    while len(pts) < N and x < p:
        P = _canonical_point(x, b, p)
        if P is None or P[0] in seen:
            x += 1
            continue
        # this x is a fresh seed; emit its whole GLV orbit
        orbit = []
        xx = P[0]
        for _ in range(3):
            if xx not in seen:
                Q = _canonical_point(xx, b, p)
                if Q is not None:
                    orbit.append(Q)
                    seen.add(xx)
            xx = (xx * beta) % p
        if orbit:
            n_orbits += 1
            storage += 1  # one stored representative per orbit
            for Q in orbit:
                if len(pts) < N:
                    pts.append(Q)
                    seen.add(Q[0])
        x += 1
    if len(pts) < N:
        raise RuntimeError(f"only {len(pts)} orbit points < requested N={N}")
    xset = {P[0]: i for i, P in enumerate(pts)}
    u = {(P[0] ** 3) % p for P in pts}
    return FactorBase("glv-orbit", pts, xset, len(pts), len(u), storage_units=storage)


# ------------------------------------------------------------------ relation search per target

def search_relations(curve: ToyCurve, base: FactorBase, R):
    """Solve S3(x_i, X, x_R) = 0 over the base for one target R; confirm every root by EC.

    Returns a dict of counters for THIS target:
      solves          : number of quadratic solves performed (== n_distinct_x)
      roots_total     : total F_p roots returned by the solves
      roots_in_base   : roots that are factor-base x-coordinates (non-degenerate)
      confirmed_pairs : set of frozenset{i,j} that EC-confirm as e_i P_i + e_j P_j = R
      spurious        : roots-in-base that DO NOT lift to any real EC relation
      s3_nonzero      : sanity failures where a solved root does not actually zero S3 (must be 0)
      example         : one confirmed relation (dict) or None
    """
    p, b = curve.p, curve.b
    xR = R[0]
    base_x = base.xset
    pts = base.points
    solves = 0
    roots_total = 0
    roots_in_base = 0
    spurious = 0
    s3_nonzero = 0
    confirmed_pairs = set()
    example = None
    negR = neg(R, p)
    for i, Pi in enumerate(pts):
        xi = Pi[0]
        A, B, C = s3_coeffs(xi, xR, b, p)
        roots = solve_quadratic(A, B, C, p)
        solves += 1
        if roots is None:  # degenerate all-field case; do not enumerate F_p
            continue
        for X in roots:
            roots_total += 1
            # independent check that the solved root truly zeroes S3
            if (A * X * X + B * X + C) % p != 0:
                s3_nonzero += 1
                continue
            j = base_x.get(X)
            if j is None:
                continue  # root is a valid S3 solution but not a factor-base coordinate
            if j == i:
                continue  # doubling (single base element); excluded like P0's m=2 model
            Pj = pts[j]
            if Pj == R or Pj == negR or (X == xR):
                continue  # degenerate: base point coincides with +-R (trivial relation)
            roots_in_base += 1
            e = confirm_relation(Pi, Pj, R, p)
            if e is None:
                spurious += 1
                continue
            pair = frozenset((i, j))
            if pair not in confirmed_pairs and example is None:
                example = {
                    "i": i, "j": j, "e_i": e[0], "e_j": e[1],
                    "P_i": list(Pi), "P_j": list(Pj), "R": [R[0], R[1]],
                }
            confirmed_pairs.add(pair)
    return {
        "solves": solves,
        "roots_total": roots_total,
        "roots_in_base": roots_in_base,
        "confirmed_pairs": confirmed_pairs,
        "spurious": spurious,
        "s3_nonzero": s3_nonzero,
        "example": example,
    }


# ------------------------------------------------------------------ self-test

def _selftest() -> None:
    import random
    # 1) Tonelli-Shanks agrees with sympy on both p = 1 mod 4 and p = 3 mod 4 fields.
    for p in (65539, 1048609, 16777333):
        rng = random.Random(7)
        for _ in range(200):
            n = rng.randrange(p)
            r = tonelli_shanks(n, p)
            s = sympy.sqrt_mod(n, p)
            if s is None:
                assert r is None, f"TS found root where sympy found none: n={n} p={p}"
            else:
                assert r is not None and (r * r) % p == n % p, f"TS root wrong n={n} p={p}"
    # 2) On a real curve, every actual pair sum zeroes S3 and re-confirms by EC.
    C = find_toy_curve(16, seed=1, require_cofactor_one=True)
    fb = build_plain_base(C, 24)
    p, b = C.p, C.b
    checked = 0
    for i in range(len(fb.points)):
        for j in range(i + 1, len(fb.points)):
            for sgn in (1, -1):
                Pj = fb.points[j] if sgn == 1 else neg(fb.points[j], p)
                S = ec_add(fb.points[i], Pj, 0, p)
                if S is None:
                    continue
                assert s3_eval(fb.points[i][0], fb.points[j][0], S[0], b, p) == 0
                # and S3-solving for X given (x_i, x_S) recovers x_j
                A, B, Cc = s3_coeffs(fb.points[i][0], S[0], b, p)
                roots = solve_quadratic(A, B, Cc, p)
                assert roots is not None and fb.points[j][0] in roots
                checked += 1
    # 3) GLV base is orbit-closed: exactly N/3 distinct u = x^3 values.
    g = build_glv_base(C, 24)
    assert g.n_distinct_x == 24 and g.n_orbits == 8 and g.storage_units == 8
    print(f"semaev_solve self-test OK (TS vs sympy on 3 fields; {checked} pair-sums S3-verified; "
          f"glv base 24 x in {g.n_orbits} orbits, {g.storage_units} stored)")


if __name__ == "__main__":
    _selftest()
