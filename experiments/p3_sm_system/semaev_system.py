#!/usr/bin/env python3
"""P3 -- the ACTUAL Semaev relation SYSTEM, Groebner-solved, for HYP_GLV_SEMAEV_001.

WHAT THIS CLOSES vs P0 / P1 / P1-m3
-----------------------------------
P0 enumerated pair sums (a birthday table). P1 solved ONE univariate quadratic
S3(x_i, X, x_R)=0 per factor-base coordinate. P1-m3 solved ONE quartic S4 per
factor-base PAIR. None of them built or solved the index-calculus relation
SYSTEM -- so none measured a degree of regularity or a Groebner/Macaulay matrix.

P3 builds the REAL relation system for m-term point decomposition R = P_1+...+P_m
over a factor base F (a set of x-coordinates), exactly as in Semaev/Gaudry/Diem
index calculus:

    { S_{m+1}(X_1, ..., X_m, x_R) = 0,
      f_F(X_1) = 0,  ...,  f_F(X_m) = 0 }               (plain, x-coordinates)

where f_F(X) = prod_{x in F}(X - x) is the factor-base polynomial (encodes X_i in F)
and S_{m+1} is the (m+1)-th summation polynomial. The whole SYSTEM is solved with a
real Groebner engine (sympy over GF(p), lex elimination + GF(p) root finding via
galois) to FIND relations -- not by enumerating EC pair/triple sums -- and its
degree of regularity / Macaulay matrix dimensions are measured directly with an
independent graded Macaulay-matrix linear-algebra engine (grevlex, GF(p) row
reduction via galois; Lazard's degree-graded view).

Two coordinate systems are compared (the HYP_GLV_SEMAEV_001 question):
  * PLAIN     : variables X_1..X_m, factor-base poly of degree |F|.
  * INVARIANT : the GLV automorphism phi(x,y)=(beta x, y) has invariant u = x^3
                (for E: y^2=x^3+b the curve is y^2 = u + b, so an orbit {x,bx,b^2x}
                collapses to ONE u). Factor base becomes |F|/3 u-values with a
                factor-base poly of degree |F|/3, but the summation polynomial S_{m+1}
                genuinely lives in x, so u is coupled back by U_i = X_i^3. The faithful
                invariant system is
                  { S_{m+1}(X_1..X_m,x_R)=0, U_i - X_i^3 = 0, f_{F,u}(U_i)=0 }.
                Because f_F(X) = f_{F,u}(X^3) for an orbit-closed base, this is
                algebraically the SAME variety in the X_i; the measurement asks whether
                the u-description nonetheless changes the degree of regularity.

HONESTY: every relation returned by the solver is RE-VERIFIED by actual elliptic-curve
addition (P_1 +- ... +- P_m = R). Solver outputs that do not EC-verify are counted as
SPURIOUS, separately. No asymptotic/advantage claim is made anywhere; any exponent fit
is DESCRIPTIVE-ONLY and labelled as such in RESULTS.md. The independent anti-overclaim
gate is validate.py, which re-derives the relation set by brute-force EC enumeration and
imports NOTHING from this module.

Reuses verbatim (imported, not rewritten): P0 toy_curves (ec_add, ec_mul, find_toy_curve,
ToyCurve) and P1 semaev_solve (build_plain_base, build_glv_base, neg, FactorBase).
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from itertools import product as iproduct

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.join(os.path.dirname(_HERE), "p0_glv_semaev")
_P1 = os.path.join(os.path.dirname(_HERE), "p1_petit")
for _d in (_P0, _P1):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import sympy  # noqa: E402
from sympy import symbols, Poly, groebner  # noqa: E402
import galois  # noqa: E402

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve  # noqa: E402
from semaev_solve import build_plain_base, build_glv_base, neg, FactorBase  # noqa: E402


# ============================================================ summation polynomials

def s3_expr(v1, v2, v3, b):
    """Third summation polynomial S3 for E: y^2 = x^3 + b (a = 0), as a sympy expression.

    S3(X1,X2,X3) = (X1-X2)^2 X3^2 - 2[(X1+X2) X1 X2 + 2b] X3 + [(X1 X2)^2 - 4b(X1+X2)].
    Vanishes iff exists y_i with (x_i,y_i) on E and P1 +- P2 +- P3 = O (Semaev).
    """
    return ((v1 - v2) ** 2 * v3 ** 2
            - 2 * ((v1 + v2) * v1 * v2 + 2 * b) * v3
            + ((v1 * v2) ** 2 - 4 * b * (v1 + v2)))


def summation_poly(m, xvars, xR, b, p):
    """S_{m+1}(X_1,...,X_m, x_R) as a sympy Poly over GF(p).

    m=2 -> S3(X1,X2,x_R).
    m=3 -> S4(X1,X2,X3,x_R) = Res_Y(S3(X1,X2,Y), S3(X3,x_R,Y)).
    m=4 -> S5(X1,X2,X3,X4,x_R) = Res_Y(S4(X1,X2,X3,Y), S3(X4,x_R,Y)).
    Built by the standard Semaev resultant recursion (share the eliminated variable Y).
    """
    Y = symbols("Y_elim")
    if m == 2:
        expr = s3_expr(xvars[0], xvars[1], xR, b)
    elif m == 3:
        e = sympy.resultant(s3_expr(xvars[0], xvars[1], Y, b),
                            s3_expr(xvars[2], xR, Y, b), Y)
        expr = sympy.expand(e)
    elif m == 4:
        Z = symbols("Z_elim")
        s4 = sympy.expand(sympy.resultant(s3_expr(xvars[0], xvars[1], Z, b),
                                          s3_expr(xvars[2], Y, Z, b), Z))
        e = sympy.resultant(sympy.Poly(s4, Y),
                            sympy.Poly(s3_expr(xvars[3], xR, Y, b), Y))
        expr = sympy.expand(e)
    else:
        raise ValueError(f"m={m} not implemented (m in 2,3,4)")
    return Poly(expr, *xvars, modulus=p)


def factor_base_poly(fvals, var, p):
    """f_F(var) = prod_{a in fvals}(var - a) as a sympy Poly over GF(p)."""
    expr = sympy.prod([var - int(a) for a in fvals])
    return Poly(sympy.expand(expr), var, modulus=p)


# ============================================================ Macaulay degree-of-regularity engine
#
# Independent graded linear-algebra measurement of the solving degree (a.k.a. the
# degree of regularity reached by a degree-graded Groebner computation, in the sense
# of Lazard: the Macaulay matrix at the solving degree already contains a Groebner
# basis of the graded ideal). We build the Macaulay matrix M_D of all monomial-shifts
# t*g_i with deg(t*g_i) <= D, row-reduce over GF(p) (galois), read off the leading
# monomials (grevlex), and report the smallest D at which the degree-<=D leading-term
# set is stable (no new leading monomials appear at D+1). Matrix dimensions are recorded.

def poly_to_terms(poly):
    """sympy Poly -> dict {exponent-tuple: int coeff (already reduced mod p)}."""
    out = {}
    mod = int(poly.get_modulus())
    for monom, coeff in poly.terms():
        out[tuple(int(e) for e in monom)] = int(coeff) % mod
    return out


def _grevlex_key(exp):
    """Sort key so that ``sorted(monos, key=_grevlex_key)`` lists monomials in DESCENDING
    grevlex order (largest monomial first = column 0, so RREF pivots are leading terms).

    grevlex: a > b iff deg(a) > deg(b), or (equal degree and the RIGHTMOST nonzero entry of
    a-b is negative, i.e. a has the smaller last-variable exponent). Ascending sort on this
    key therefore yields largest-first: -total puts higher degree first; among equal degree,
    tuple(reversed(exp)) ascending puts the smaller trailing exponent (the larger monomial)
    first.
    """
    return (-sum(exp), tuple(reversed(exp)))


def _monomials_upto(nvars, D):
    """All exponent tuples in nvars variables with total degree <= D."""
    if nvars == 1:
        return [(d,) for d in range(D + 1)]
    res = []
    for first in range(D + 1):
        for rest in _monomials_upto(nvars - 1, D - first):
            res.append((first,) + rest)
    return res


def _mono_mul(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _divides(lead, mono, nvars):
    return all(lead[i] <= mono[i] for i in range(nvars))


def _quotient_dimension(lead_gens, nvars):
    """Dimension of F[x]/LT-ideal (count of standard monomials) if the leading-term ideal
    is 0-dimensional (a pure power of every variable is present), else None."""
    pure = [None] * nvars
    for L in lead_gens:
        nz = [i for i in range(nvars) if L[i] > 0]
        if len(nz) == 1:
            i = nz[0]
            pure[i] = L[i] if pure[i] is None else min(pure[i], L[i])
    if any(a is None for a in pure):
        return None
    count = 0
    for exps in iproduct(*[range(a) for a in pure]):
        if not any(_divides(L, exps, nvars) for L in lead_gens):
            count += 1
    return count


def degree_of_regularity(gen_terms, nvars, p, max_deg=40):
    """Measure the solving degree and Macaulay matrix sizes for a 0-dim graded ideal.

    Degree-graded Macaulay approach (Lazard). At each degree D we build the Macaulay
    matrix M_D of all monomial shifts t*g_i with deg(t*g_i) <= D, row-reduce over GF(p)
    (grevlex column order), and read the leading (pivot) monomials. We accumulate the
    minimal generators of the leading-term ideal as D grows. The SOLVING DEGREE / degree
    of regularity is the largest degree at which a NEW minimal leading-term generator is
    discovered before the leading-term ideal becomes 0-dimensional and stops growing --
    i.e. "the max degree reached in the (graded) Groebner computation".

    Returns dict with d_reg, largest matrix dimensions, per-degree records, whether the
    measurement was capped at max_deg, and the final quotient dimension (# solutions with
    multiplicity) when 0-dimensional.
    """
    GFp = galois.GF(p)
    gen_degs = [max(sum(e) for e in g) for g in gen_terms]
    d0 = min(gen_degs)
    max_gen_deg = max(gen_degs)
    per_degree = []
    lead_gens = []                 # minimal generators of the leading-term ideal
    max_rows = max_cols = 0
    last_new_degree = None
    quotient_dim = None
    patience = 2                   # require this many consecutive new-gen-free degrees
    clear = 0
    D = d0
    while D <= max_deg:
        cols = sorted(_monomials_upto(nvars, D), key=_grevlex_key)
        col_index = {m: i for i, m in enumerate(cols)}
        rows = []
        for g, gd in zip(gen_terms, gen_degs):
            for t in _monomials_upto(nvars, D - gd):
                row = [0] * len(cols)
                for e, c in g.items():
                    row[col_index[_mono_mul(t, e)]] = c % p
                rows.append(row)
        M = GFp(rows)
        max_rows = max(max_rows, M.shape[0])
        max_cols = max(max_cols, M.shape[1])
        R = M.row_reduce()
        leads = set()
        for r in range(R.shape[0]):
            rowv = R[r, :]
            nz = next((j for j in range(len(cols)) if int(rowv[j]) != 0), -1)
            if nz >= 0:
                leads.add(cols[nz])
        # new minimal generators of the leading-term ideal discovered at this degree
        new_gens = [m for m in leads if not any(_divides(L, m, nvars) for L in lead_gens)]
        if new_gens:
            last_new_degree = D
            for m in new_gens:
                lead_gens.append(m)
            clear = 0
        else:
            clear += 1
        quotient_dim = _quotient_dimension(lead_gens, nvars)
        zero_dim = quotient_dim is not None
        per_degree.append({"D": D, "rows": int(M.shape[0]), "cols": int(M.shape[1]),
                           "n_lead_gens": len(lead_gens), "quotient_dim": quotient_dim})
        # Terminate only after (a) every input generator has entered the matrix
        # (D >= max input generator degree), (b) the ideal is 0-dimensional, and (c) no new
        # leading generator has appeared for `patience` consecutive degrees. This avoids the
        # premature stop where high-degree generators (e.g. S4/S5) have not yet been included.
        if D >= max_gen_deg and zero_dim and clear >= patience:
            break
        D += 1
    reached_max = (D > max_deg)
    return {
        "d_reg": last_new_degree,
        "max_matrix_rows": int(max_rows),
        "max_matrix_cols": int(max_cols),
        "per_degree": per_degree,
        "reached_max": reached_max,
        "min_gen_degree": d0,
        "gen_degrees": gen_degs,
        "quotient_dim": quotient_dim,
        "n_lead_gens": len(lead_gens),
    }


# ============================================================ grevlex GB max-degree (cheap proxy)

def grevlex_gb_max_degree(gens, solve_vars, p, timeout_polys=None):
    """Cheap complementary degree measurement: the max total degree of a reduced grevlex
    Groebner basis (sympy's Buchberger over GF(p)). This is "the highest degree of a basis
    element produced by the Groebner computation" -- a proxy for the degree of regularity
    that is feasible where the full graded Macaulay reduction is not. Returns
    (max_degree, n_basis_elements, wall_time).
    """
    t0 = time.perf_counter()
    G = groebner([g.as_expr() for g in gens], *solve_vars, order="grevlex", modulus=p)
    polys = list(G.polys)
    md = max((gp.total_degree() for gp in polys), default=0)
    return int(md), len(polys), time.perf_counter() - t0


# ============================================================ variety solver (Groebner + elimination)

def _roots_gfp(poly_univar, var, p):
    """All GF(p) roots of a univariate sympy Poly, via galois."""
    GFp = galois.GF(p)
    # coefficients high-degree first
    d = poly_univar.degree()
    coeffs = [int(poly_univar.coeff_monomial(var ** k)) % p for k in range(d, -1, -1)]
    if all(c == 0 for c in coeffs):
        return None  # zero polynomial: not 0-dim in this variable
    f = galois.Poly(coeffs, field=GFp)
    if f.degree == 0:
        return []
    return [int(r) for r in f.roots()]


def variety_from_system(gens, xvars, p, max_solutions=100000):
    """All F_p solutions of a 0-dimensional system via lex Groebner + triangular back-sub.

    gens  : list of sympy Poly (any generators of the ideal).
    xvars : the X-variables to solve for (order matters for lex).
    Returns a list of dicts {var: value}. Uses ONLY commutative algebra (Groebner
    elimination + GF(p) univariate root finding) -- no elliptic-curve arithmetic.
    """
    G = groebner([g.as_expr() for g in gens], *xvars, order="lex", modulus=p)
    gb = [g for g in G.polys]
    if any(g.total_degree() == 0 and g.as_expr() != 0 for g in gb):
        return []  # ideal is (1): no solutions
    sols = []
    _extend(gb, list(xvars), {}, p, sols, max_solutions)
    return sols


def _extend(gb, xvars, assign, p, out, cap):
    if len(out) > cap:
        return
    remaining = [v for v in xvars if v not in assign]
    if not remaining:
        out.append(dict(assign))
        return
    # substitute the partial assignment, look for a poly univariate in some remaining var
    for target in remaining:
        univ_polys = []
        for g in gb:
            e = g.as_expr().subs(assign)
            fs = e.free_symbols & set(remaining)
            if fs == {target}:
                pe = Poly(e, target, modulus=p)
                if pe.total_degree() >= 1:
                    univ_polys.append(pe)
        if univ_polys:
            # gcd of all univariate constraints on `target` => exact root set
            g0 = univ_polys[0]
            for q in univ_polys[1:]:
                g0 = g0.gcd(q)
            roots = _roots_gfp(g0, target, p)
            if roots is None:
                continue
            for r in roots:
                _extend(gb, xvars, {**assign, target: r}, p, out, cap)
            return
    # no univariate constraint found: leave remaining free (should not happen for 0-dim
    # factor-base-pinned systems). Record nothing to stay honest.
    return


# ============================================================ EC re-verification (ground truth)

def confirm_relation_m(points, R, p):
    """Is there a sign vector e in {+1,-1}^m with sum e_i P_i = R? Return e or None.

    ACTUAL elliptic-curve addition on E: y^2 = x^3 + b (a=0). This is the ground-truth
    verifier every solver-produced relation must pass to be counted.
    """
    m = len(points)
    for signs in iproduct((1, -1), repeat=m):
        acc = None
        for P, s in zip(points, signs):
            acc = ec_add(acc, P if s == 1 else neg(P, p), 0, p)
        if acc == R:
            return signs
    return None


# ============================================================ system builders (plain / invariant)

@dataclass
class SystemBuild:
    coord: str
    m: int
    xvars: list                # X-variables to report solutions for
    solve_vars: list           # all variables passed to the Groebner engine
    gens: list                 # sympy Polys (for Groebner)
    gen_terms: list            # dicts for the Macaulay engine
    nvars: int
    fb_poly_degree: int        # degree of the factor-base defining polynomial
    n_fb_elements: int         # |F| (plain) or #orbits (invariant u-count)


def build_plain_system(m, F, xR, b, p):
    """Plain relation system in x: {S_{m+1}=0, f_F(X_i)=0}. F = list of x-coords."""
    xvars = list(symbols(f"X1:{m+1}"))
    S = summation_poly(m, xvars, int(xR), b, p)
    gens = [S]
    for v in xvars:
        gens.append(Poly(factor_base_poly(F, v, p).as_expr(), *xvars, modulus=p))
    gen_terms = [poly_to_terms(g) for g in gens]
    return SystemBuild("plain", m, xvars, xvars, gens, gen_terms, m,
                       fb_poly_degree=len(F), n_fb_elements=len(F))


def build_invariant_system(m, F, uvals, xR, b, p):
    """Invariant (u=x^3) relation system, faithful coupled form:
        { S_{m+1}(X_1..X_m, x_R)=0, U_i - X_i^3 = 0, f_{F,u}(U_i)=0 }.
    uvals = distinct u=x^3 values of the (orbit-closed) factor base F.
    Variables: X_1..X_m, U_1..U_m (2m variables).
    """
    xvars = list(symbols(f"X1:{m+1}"))
    uvars = list(symbols(f"U1:{m+1}"))
    # lex elimination order: eliminate U first (list U before X so X ends up univariate).
    allv = uvars + xvars
    S = Poly(summation_poly(m, xvars, int(xR), b, p).as_expr(), *allv, modulus=p)
    gens = [S]
    for xv, uv in zip(xvars, uvars):
        gens.append(Poly((uv - xv ** 3), *allv, modulus=p))
        gens.append(Poly(factor_base_poly(uvals, uv, p).as_expr(), *allv, modulus=p))
    gen_terms = [poly_to_terms(g) for g in gens]
    return SystemBuild("invariant", m, xvars, allv, gens, gen_terms, 2 * m,
                       fb_poly_degree=len(uvals), n_fb_elements=len(uvals))


# ============================================================ full relation search for one target

def search_relations_system(curve, base, m, R, coord, measure_dreg=True, dreg_max=40):
    """Build and Groebner-solve the m-term Semaev SYSTEM for one target R; EC-verify.

    Returns a dict of measured quantities (timings, d_reg, matrix dims, relations,
    spurious). `coord` in {"plain","invariant"}. `base` is a P1 FactorBase.
    """
    p, b = curve.p, curve.b
    F = [P[0] for P in base.points]
    xR = R[0]
    xset = base.xset

    t0 = time.perf_counter()
    if coord == "plain":
        sysb = build_plain_system(m, F, xR, b, p)
    else:
        uvals = sorted({(x ** 3) % p for x in F})
        sysb = build_invariant_system(m, F, uvals, xR, b, p)
    t_build = time.perf_counter() - t0

    # --- solve the variety (find candidate relation tuples) ---
    t0 = time.perf_counter()
    sols = variety_from_system(sysb.gens, sysb.solve_vars, p)
    t_solve = time.perf_counter() - t0

    # --- degree of regularity / Macaulay matrices (independent graded linear algebra) ---
    dreg = None
    t_linalg = 0.0
    if measure_dreg:
        t0 = time.perf_counter()
        dreg = degree_of_regularity(sysb.gen_terms, sysb.nvars, p, max_deg=dreg_max)
        t_linalg = time.perf_counter() - t0

    # --- EC re-verification of every solver-produced tuple ---
    t0 = time.perf_counter()
    confirmed = set()
    spurious = 0
    example = None
    for sol in sols:
        xs = [int(sol[v]) % p for v in sysb.xvars]
        # each x must be a factor-base coordinate (guaranteed by f_F=0, but re-check)
        idxs = []
        ok = True
        for x in xs:
            j = xset.get(x)
            if j is None:
                ok = False
                break
            idxs.append(j)
        if not ok:
            spurious += 1
            continue
        if len(set(idxs)) != m:
            continue  # repeated factor-base element: not an m-distinct relation
        pts = [base.points[j] for j in idxs]
        signs = confirm_relation_m(pts, R, p)
        if signs is None:
            spurious += 1
            continue
        key = frozenset(idxs)
        if key not in confirmed and example is None:
            # P, signs, and idxs are kept in the SAME order (the order the signs align to),
            # so the recorded relation replays as sum_i signs_i * P_i = R.
            example = {"idxs": list(idxs),
                       "P": [list(pts[t]) for t in range(m)],
                       "signs": list(signs), "R": [R[0], R[1]]}
        confirmed.add(key)
    t_ecverify = time.perf_counter() - t0

    return {
        "coord": coord,
        "m": m,
        "n_solutions_raw": len(sols),
        "confirmed_relations": sorted(sorted(k) for k in confirmed),
        "n_confirmed": len(confirmed),
        "spurious": spurious,
        "fb_poly_degree": sysb.fb_poly_degree,
        "n_fb_elements": sysb.n_fb_elements,
        "nvars": sysb.nvars,
        "d_reg": dreg,
        "t_build": t_build,
        "t_solve": t_solve,
        "t_linalg": t_linalg,
        "t_ecverify": t_ecverify,
        "example": example,
    }


# ============================================================ self-test

def _brute_force_tuples(points, R, m, p):
    """Independent EC ground truth: all size-m index sets with some sign-sum == R."""
    from itertools import combinations
    found = set()
    for combo in combinations(range(len(points)), m):
        if confirm_relation_m([points[i] for i in combo], R, p) is not None:
            found.add(frozenset(combo))
    return found


def _selftest():
    print("== semaev_system self-test ==")
    import random
    C = find_toy_curve(16, seed=1, require_cofactor_one=True)
    p, b = C.p, C.b

    # 1) m=3 system: S4 built by resultant vanishes exactly on real 3-term relations.
    #    Decisive test: constructed targets R = e_i P_i + e_j P_j + e_k P_k, the solver
    #    must recover {i,j,k} and match a brute-force EC enumeration (spurious = 0).
    fb8 = build_plain_base(C, 8)
    rng = random.Random(2)
    rel3 = 0
    for _ in range(20):
        i, j, k = rng.sample(range(len(fb8.points)), 3)
        es = [rng.choice([1, -1]) for _ in range(3)]
        R = None
        for idx, e in zip((i, j, k), es):
            P = fb8.points[idx]
            R = ec_add(R, P if e == 1 else neg(P, p), 0, p)
        if R is None:
            continue
        res = search_relations_system(C, fb8, 3, R, "plain", measure_dreg=False)
        got = {frozenset(t) for t in res["confirmed_relations"]}
        bf = _brute_force_tuples(fb8.points, R, 3, p)
        assert res["spurious"] == 0, "spurious in m=3"
        assert got == bf and frozenset((i, j, k)) in got, f"m=3 solve != brute {got} {bf}"
        rel3 += len(bf)
    print(f"  m=3 S4-system Groebner solve == brute-force EC, constructed targets "
          f"({rel3} relations, spurious=0): OK")

    # 2) m=2 system solve reproduces P1's known 2-term relations (constructed targets
    #    guarantee some relations are present) and the invariant (u=x^3) system agrees.
    from semaev_solve import search_relations as p1_search
    fb = build_plain_base(C, 10)
    fbg = build_glv_base(C, 12)  # orbit-closed base for the invariant comparison
    hits_sys = 0
    for _ in range(20):
        i, j = rng.sample(range(len(fb.points)), 2)
        e = [rng.choice([1, -1]), rng.choice([1, -1])]
        R = ec_add(fb.points[i] if e[0] == 1 else neg(fb.points[i], p),
                   fb.points[j] if e[1] == 1 else neg(fb.points[j], p), 0, p)
        if R is None:
            continue
        res = search_relations_system(C, fb, 2, R, "plain", measure_dreg=False)
        p1 = p1_search(C, fb, R)
        got_sys = {frozenset(t) for t in res["confirmed_relations"]}
        got_p1 = set(p1["confirmed_pairs"])
        assert res["spurious"] == 0, "spurious in m=2"
        assert got_sys == got_p1 and frozenset((i, j)) in got_sys, \
            f"m=2 system != P1: {got_sys} vs {got_p1}"
        hits_sys += len(got_sys)
    print(f"  m=2 Groebner-system relations == P1 S3-solve relations "
          f"({hits_sys} relations, constructed targets, spurious=0): OK")

    # 2b) invariant (u=x^3) coupled system finds the same relations as plain, m=2.
    inv_hits = 0
    for _ in range(15):
        i, j = rng.sample(range(len(fbg.points)), 2)
        R = ec_add(fbg.points[i], fbg.points[j], 0, p)
        if R is None:
            continue
        rp = search_relations_system(C, fbg, 2, R, "plain", measure_dreg=False)
        ri = search_relations_system(C, fbg, 2, R, "invariant", measure_dreg=False)
        gp = {frozenset(t) for t in rp["confirmed_relations"]}
        gi = {frozenset(t) for t in ri["confirmed_relations"]}
        assert ri["spurious"] == 0 and gp == gi, f"invariant != plain m=2: {gp} vs {gi}"
        inv_hits += len(gi)
    print(f"  invariant (u=x^3) system == plain system, m=2 "
          f"({inv_hits} relations, spurious=0): OK")

    # 3) degree-of-regularity engine sanity on a trivial diagonal system.
    d = degree_of_regularity(
        [poly_to_terms(Poly((symbols('X1')-2)*(symbols('X1')-5),
                            symbols('X1'), symbols('X2'), modulus=p)),
         poly_to_terms(Poly((symbols('X2')-3)*(symbols('X2')-7),
                            symbols('X1'), symbols('X2'), modulus=p))],
        2, p, max_deg=12)
    print(f"  d_reg engine on split system: d_reg={d['d_reg']} "
          f"max_matrix={d['max_matrix_rows']}x{d['max_matrix_cols']}: OK")
    print("self-test OK")


if __name__ == "__main__":
    _selftest()
