#!/usr/bin/env python3
"""P4 -- a COMPOSED low-degree rational-map factor base for the Semaev relation
system, built directly on top of P3, for HYP_GLV_SEMAEV_001.

WHAT THIS ASKS (built on P3)
----------------------------
P3 (`experiments/p3_sm_system/`) measured the concrete relation-generation barrier:
for a RAW x-coordinate factor base ``F`` the m=2 Semaev system
``{ S3(X1,X2,x_R)=0, f_F(X1)=0, f_F(X2)=0 }`` has degree of regularity (solving
degree) exactly ``2|F| + 1``, driven by the fact that the factor base's ONLY
defining polynomial ``f_F(X) = prod_{a in F}(X - a)`` has degree ``|F|``.

Petit's idea (Petit et al., prime-field ECDLP; Weil-descent / composed maps) is to
choose the factor base NOT as a raw point set but as the IMAGE/FIBRE of a COMPOSED
LOW-DEGREE (rational) map, so that the factor base is cut out by LOWER-degree
equations in auxiliary variables -- which could, in principle, lower the degree of
regularity of the relation system.

THE QUESTION P4 measures: does a composed low-degree map factor base give a degree
of regularity BELOW the raw ``2|F| + 1`` of P3, or not?

FAITHFULNESS (read this; it is the honest scope -- see RESULTS.md, rule 1)
--------------------------------------------------------------------------
This is NOT literally Petit's prime-field algorithm. Petit/Weil-descent get their
low-degree factor-base description from a genuine field/structure (e.g. a subfield or
an F_2-linear subspace under Weil restriction). Over a PRIME field there is no Weil
descent, so we build the closest HONEST approximation the task requests: a factor base
that really is the image of a COMPOSED low-degree polynomial map from auxiliary
variables, and whose defining SYSTEM has lower per-equation degree than the raw
degree-|F| polynomial. Two composed maps are built and measured:

  (A) product_2aux  -- X = rho(sigma(t1, t2)),  sigma(t1,t2) = t1 + kappa*t2   (deg 1),
      rho(s) = s^2 + c  (deg 2).  A GENUINELY COMPOSED map (linear form then square)
      of TWO auxiliary variables.  Factor base = { X = rho(sigma(t1,t2)) : t1,t2 in B }
      restricted to on-curve x, so |F| ~ |B|^2, while each defining equation has degree
      <= max(2, |B|) ~ sqrt(|F|).  This is the candidate that could BEAT the raw
      degree-|F| description: the product structure trades one degree-|F| equation for
      several degree-~sqrt(|F|) equations in more variables. It is the prime-field,
      polynomial-map ANALOGUE of the Weil-descent "small pieces" idea -- an
      approximation, not the real thing.

  (B) single_aux_composed -- X = r2(r1(t)),  r1(t) = t^2 + a1,  r2(w) = w^2 + a2*w + a3
      (both degree 2, so the composed map has degree 4), realised as the CHAINED
      low-degree system { X - r2(w) = 0, w - r1(t) = 0, g(t) = 0 }.  Here the auxiliary
      domain still needs |T| >= |F| points, so g(t) has degree ~|F|: the high degree is
      RELOCATED to the t-defining polynomial, not removed.  This variant is the honest
      contrast showing that COMPOSITION ALONE (without the multi-variable product
      structure of (A)) does not lower the defining degree.

Every relation returned by the solver is RE-VERIFIED by actual elliptic-curve addition
(sum_i e_i P_i = R). Solver outputs that do not EC-verify are counted SEPARATELY as
spurious. No asymptotic / advantage / no-go-proof conclusion is drawn; any fit is
DESCRIPTIVE-ONLY. The independent anti-overclaim gate is ``validate.py``, which
re-derives the relation set by brute-force EC enumeration and imports NOTHING from the
solver's derivation path.

ENGINE REUSE (the SAME independent Macaulay engine as P3)
--------------------------------------------------------
The degree-of-regularity / Macaulay-matrix measurement, the summation polynomial
S3, the lex-Groebner variety solver, and the EC re-verification are IMPORTED VERBATIM
from ``experiments/p3_sm_system/semaev_system.py`` (the P3-validated engine). P4 adds
ONLY the composed-map factor-base construction and the composed-map relation-system
builders on top. Because the engine is shared, the P4 vs P3 comparison is on identical
measurement machinery; correctness of the *relations* is still checked independently by
``validate.py`` (brute-force EC), so no conclusion depends on the engine being right.
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_P0 = os.path.join(os.path.dirname(_HERE), "p0_glv_semaev")
_P1 = os.path.join(os.path.dirname(_HERE), "p1_petit")
_P3 = os.path.join(os.path.dirname(_HERE), "p3_sm_system")
for _d in (_P0, _P1, _P3):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import sympy  # noqa: E402
from sympy import symbols, Poly  # noqa: E402

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve  # noqa: E402
from semaev_solve import neg, _canonical_point  # noqa: E402

# ---- the P3-validated engine, imported verbatim (same Macaulay/Groebner machinery) ----
from semaev_system import (  # noqa: E402
    summation_poly, factor_base_poly, poly_to_terms,
    degree_of_regularity, variety_from_system, confirm_relation_m,
    build_plain_system, SystemBuild, grevlex_gb_max_degree,
)


# ============================================================ composed-map specification

@dataclass
class PetitMap:
    """A COMPOSED low-degree polynomial map used to define the factor base.

    kind == "product_2aux":       X = (t1 + kappa*t2)**2 + c,   t1,t2 in B = {0..b0-1}.
                                  Composed as rho(sigma(t1,t2)), sigma deg 1, rho deg 2.
    kind == "single_aux_composed": X = r2(r1(t)),  r1(t)=t^2+a1, r2(w)=w^2+a2*w+a3,
                                  t in T = {0..nt-1}.  Chained low-degree system.
    """
    kind: str
    # product_2aux params
    b0: int = 0
    kappa: int = 0
    c: int = 0
    # single_aux_composed params
    nt: int = 0
    a1: int = 0
    a2: int = 0
    a3: int = 0

    def describe(self) -> str:
        if self.kind == "product_2aux":
            return (f"product_2aux X=(t1+{self.kappa}*t2)^2+{self.c}, "
                    f"B={{0..{self.b0-1}}} (composed deg-1 then deg-2)")
        return (f"single_aux_composed X=r2(r1(t)), r1=t^2+{self.a1}, "
                f"r2=w^2+{self.a2}*w+{self.a3}, T={{0..{self.nt-1}}} (composed deg-4)")


def _pick_product_params(curve, b0):
    """Deterministically choose (kappa, c) maximising the number of DISTINCT on-curve
    image points of X=(t1+kappa*t2)^2+c over B={0..b0-1}. Fixed ascending search, so the
    choice is reproducible and reported in the manifest."""
    p, b = curve.p, curve.b
    best = None  # (n_oncurve, kappa, c)
    for kappa in range(1, 64):
        for c in range(0, 12):
            imgs = {((t1 + kappa * t2) ** 2 + c) % p for t1 in range(b0) for t2 in range(b0)}
            noc = sum(1 for X in imgs if _canonical_point(X, b, p) is not None)
            if best is None or noc > best[0]:
                best = (noc, kappa, c)
    return best[1], best[2]


def _pick_single_aux_params(curve, nt):
    """Deterministically choose (a1,a2,a3) maximising distinct on-curve image points of
    X=r2(r1(t)) over T={0..nt-1}. Reproducible ascending search."""
    p, b = curve.p, curve.b
    best = None
    for a1 in range(0, 8):
        for a2 in range(0, 8):
            for a3 in range(0, 8):
                imgs = set()
                for t in range(nt):
                    w = (t * t + a1) % p
                    X = (w * w + a2 * w + a3) % p
                    imgs.add(X)
                noc = sum(1 for X in imgs if _canonical_point(X, b, p) is not None)
                if best is None or noc > best[0]:
                    best = (noc, a1, a2, a3)
    return best[1], best[2], best[3]


def make_map(curve, kind, size) -> PetitMap:
    """Build a reproducible PetitMap. `size` = b0 (product) or nt (single-aux)."""
    if kind == "product_2aux":
        kappa, c = _pick_product_params(curve, size)
        return PetitMap(kind=kind, b0=size, kappa=kappa, c=c)
    elif kind == "single_aux_composed":
        a1, a2, a3 = _pick_single_aux_params(curve, size)
        return PetitMap(kind=kind, nt=size, a1=a1, a2=a2, a3=a3)
    raise ValueError(f"unknown map kind {kind}")


# ============================================================ composed-map factor base (REAL EC points)

@dataclass
class PetitBase:
    """Factor base = ON-CURVE image points of a composed map. `points`/`xset` are the
    genuine elliptic-curve points the brute-force validator and EC-verifier use."""
    mapspec: PetitMap
    points: list            # canonical (x, y) EC points, one per distinct on-curve image x
    xset: dict              # x -> index into points
    n_distinct_x: int       # |F| (effective factor-base size, matched to P3's |F|)
    n_image_total: int      # distinct algebraic image x-values (incl. off-curve)
    aux_domain_size: int    # |B| (product) or |T| (single-aux): the auxiliary set size


def build_petit_base(curve: ToyCurve, mapspec: PetitMap) -> PetitBase:
    """Compute the composed-map image over the auxiliary domain, keep the on-curve subset
    as a REAL factor base of EC points (deterministic, smallest-x first)."""
    p, b = curve.p, curve.b
    if mapspec.kind == "product_2aux":
        b0 = mapspec.b0
        imgs = {((t1 + mapspec.kappa * t2) ** 2 + mapspec.c) % p
                for t1 in range(b0) for t2 in range(b0)}
        aux_dom = b0
    elif mapspec.kind == "single_aux_composed":
        imgs = set()
        for t in range(mapspec.nt):
            w = (t * t + mapspec.a1) % p
            imgs.add((w * w + mapspec.a2 * w + mapspec.a3) % p)
        aux_dom = mapspec.nt
    else:
        raise ValueError(mapspec.kind)
    n_image_total = len(imgs)
    pts = []
    for X in sorted(imgs):
        P = _canonical_point(X, b, p)
        if P is not None:
            pts.append(P)
    xset = {P[0]: i for i, P in enumerate(pts)}
    return PetitBase(mapspec, pts, xset, len(pts), n_image_total, aux_dom)


# ============================================================ composed-map relation systems

def build_product_system(m, mapspec, xR, b, p):
    """Composed product-map relation system, m terms:
        { S3(X_1..X_m, x_R) = 0,
          X_i - (t1_i + kappa*t2_i)^2 - c = 0,   (degree 2, the composed map)
          g(t1_i) = 0,  g(t2_i) = 0 }            (degree b0, the auxiliary domain)
    Variables: X_1..X_m, t1_1,t2_1,...,t1_m,t2_m  (3m variables). g(t)=prod_{j in B}(t-j)."""
    b0, kappa, c = mapspec.b0, mapspec.kappa, mapspec.c
    xvars = list(symbols(f"X1:{m+1}"))
    t1vars = list(symbols(f"S1:{m+1}"))   # t1 for each slot
    t2vars = list(symbols(f"T1:{m+1}"))   # t2 for each slot
    # lex elimination order: aux variables first, X-variables LAST (so X ends univariate).
    allv = t1vars + t2vars + xvars
    gens = [Poly(summation_poly(m, xvars, int(xR), b, p).as_expr(), *allv, modulus=p)]
    B = list(range(b0))
    for xv, s1, s2 in zip(xvars, t1vars, t2vars):
        gens.append(Poly(xv - (s1 + kappa * s2) ** 2 - c, *allv, modulus=p))
        gens.append(Poly(factor_base_poly(B, s1, p).as_expr(), *allv, modulus=p))
        gens.append(Poly(factor_base_poly(B, s2, p).as_expr(), *allv, modulus=p))
    gen_terms = [poly_to_terms(g) for g in gens]
    return SystemBuild("product_2aux", m, xvars, allv, gens, gen_terms, 3 * m,
                       fb_poly_degree=b0, n_fb_elements=b0 * b0)


def build_single_aux_system(m, mapspec, xR, b, p):
    """Composed single-aux relation system, m terms:
        { S3(X_1..X_m, x_R) = 0,
          X_i - (w_i^2 + a2*w_i + a3) = 0,       (degree 2)
          w_i - (t_i^2 + a1) = 0,                (degree 2, chained composition)
          g(t_i) = 0 }                           (degree nt: the RELOCATED high degree)
    Variables: X_1..X_m, w_1..w_m, t_1..t_m  (3m variables). g(t)=prod_{j in T}(t-j)."""
    nt, a1, a2, a3 = mapspec.nt, mapspec.a1, mapspec.a2, mapspec.a3
    xvars = list(symbols(f"X1:{m+1}"))
    wvars = list(symbols(f"W1:{m+1}"))
    tvars = list(symbols(f"T1:{m+1}"))
    allv = tvars + wvars + xvars
    gens = [Poly(summation_poly(m, xvars, int(xR), b, p).as_expr(), *allv, modulus=p)]
    T = list(range(nt))
    for xv, wv, tv in zip(xvars, wvars, tvars):
        gens.append(Poly(xv - (wv ** 2 + a2 * wv + a3), *allv, modulus=p))
        gens.append(Poly(wv - (tv ** 2 + a1), *allv, modulus=p))
        gens.append(Poly(factor_base_poly(T, tv, p).as_expr(), *allv, modulus=p))
    gen_terms = [poly_to_terms(g) for g in gens]
    return SystemBuild("single_aux_composed", m, xvars, allv, gens, gen_terms, 3 * m,
                       fb_poly_degree=nt, n_fb_elements=nt)


def build_raw_baseline_system(m, base: PetitBase, xR, b, p):
    """The P3 RAW baseline on the SAME on-curve factor base: {S_{m+1}=0, f_F(X_i)=0},
    f_F of degree |F|. Reuses P3's build_plain_system verbatim so the comparison is
    against the identical P3 construction at matched |F|."""
    F = [P[0] for P in base.points]
    return build_plain_system(m, F, xR, b, p)


# ============================================================ relation search (composed map)

def search_relations_petit(curve, base: PetitBase, m, R, variant,
                           measure_dreg=True, dreg_max=40):
    """Build and Groebner-solve the composed-map m-term relation SYSTEM for one target R;
    EC-verify every candidate. Returns measured quantities. `variant` in
    {"product_2aux","single_aux_composed","raw_baseline"}."""
    p, b = curve.p, curve.b
    xR = R[0]
    xset = base.xset

    t0 = time.perf_counter()
    if variant == "product_2aux":
        sysb = build_product_system(m, base.mapspec, xR, b, p)
    elif variant == "single_aux_composed":
        sysb = build_single_aux_system(m, base.mapspec, xR, b, p)
    elif variant == "raw_baseline":
        sysb = build_raw_baseline_system(m, base, xR, b, p)
    else:
        raise ValueError(variant)
    t_build = time.perf_counter() - t0

    # --- solve the variety (candidate relation tuples) ---
    t0 = time.perf_counter()
    sols = variety_from_system(sysb.gens, sysb.solve_vars, p)
    t_solve = time.perf_counter() - t0

    # --- degree of regularity / Macaulay matrices (same independent engine as P3) ---
    dreg = None
    t_linalg = 0.0
    if measure_dreg:
        t0 = time.perf_counter()
        dreg = degree_of_regularity(sysb.gen_terms, sysb.nvars, p, max_deg=dreg_max)
        t_linalg = time.perf_counter() - t0

    # --- EC re-verification (ground truth). Dedup X-tuples first (the composed map can
    #     produce several auxiliary pre-images of the same X), so aux multiplicity does
    #     not inflate the spurious count. ---
    t0 = time.perf_counter()
    seen_xtuples = set()
    confirmed = set()
    spurious = 0
    example = None
    for sol in sols:
        xs = tuple(int(sol[v]) % p for v in sysb.xvars)
        if xs in seen_xtuples:
            continue
        seen_xtuples.add(xs)
        idxs = []
        ok = True
        for x in xs:
            j = xset.get(x)
            if j is None:          # off-curve image point: not a real factor-base element
                ok = False
                break
            idxs.append(j)
        if not ok:
            spurious += 1          # solver produced an x not on the on-curve factor base
            continue
        if len(set(idxs)) != m:
            continue               # repeated factor-base element: not an m-distinct relation
        pts = [base.points[j] for j in idxs]
        signs = confirm_relation_m(pts, R, p)
        if signs is None:
            spurious += 1
            continue
        key = frozenset(idxs)
        if key not in confirmed and example is None:
            example = {"idxs": list(idxs), "P": [list(pts[t]) for t in range(m)],
                       "signs": list(signs), "R": [R[0], R[1]]}
        confirmed.add(key)
    t_ecverify = time.perf_counter() - t0

    return {
        "variant": variant, "m": m,
        "n_solutions_raw": len(sols),
        "confirmed_relations": sorted(sorted(k) for k in confirmed),
        "n_confirmed": len(confirmed),
        "spurious": spurious,
        "fb_poly_degree": sysb.fb_poly_degree,
        "n_fb_elements": base.n_distinct_x,
        "nvars": sysb.nvars,
        "d_reg": dreg,
        "t_build": t_build, "t_solve": t_solve,
        "t_linalg": t_linalg, "t_ecverify": t_ecverify,
        "example": example,
    }


# ============================================================ self-test

def _brute_force_tuples(points, R, m, p):
    """Independent EC ground truth used by the self-test only."""
    from itertools import combinations, product as iproduct
    found = set()
    for combo in combinations(range(len(points)), m):
        pts = [points[i] for i in combo]
        for signs in iproduct((1, -1), repeat=m):
            acc = None
            for P, s in zip(pts, signs):
                acc = ec_add(acc, P if s == 1 else neg(P, p), 0, p)
            if acc == R:
                found.add(frozenset(combo))
                break
    return found


def _selftest():
    import random
    print("== semaev_petit self-test ==")
    C = find_toy_curve(16, seed=1, require_cofactor_one=True)
    p = C.p
    rng = random.Random(7)

    for kind, size in (("product_2aux", 3), ("single_aux_composed", 6)):
        mp = make_map(C, kind, size)
        base = build_petit_base(C, mp)
        assert base.n_distinct_x >= 2, f"{kind}: factor base too small ({base.n_distinct_x})"
        # every factor-base point is really on the curve
        for P in base.points:
            assert C.on_curve(P), f"{kind}: factor-base point off curve"
        print(f"  [{kind}] {mp.describe()} -> |F|={base.n_distinct_x} "
              f"(image_total={base.n_image_total}, aux_dom={base.aux_domain_size})")

        # constructed targets R = e_i P_i + e_j P_j: composed-map solver must recover {i,j}
        # and MATCH an independent brute-force EC enumeration (spurious=0), and equal the
        # raw-baseline solver on the SAME factor base.
        hits = 0
        for _ in range(12):
            i, j = rng.sample(range(len(base.points)), 2)
            e = [rng.choice([1, -1]), rng.choice([1, -1])]
            R = ec_add(base.points[i] if e[0] == 1 else neg(base.points[i], p),
                       base.points[j] if e[1] == 1 else neg(base.points[j], p), 0, p)
            if R is None:
                continue
            res = search_relations_petit(C, base, 2, R, kind, measure_dreg=False)
            raw = search_relations_petit(C, base, 2, R, "raw_baseline", measure_dreg=False)
            bf = _brute_force_tuples(base.points, R, 2, p)
            got = {frozenset(t) for t in res["confirmed_relations"]}
            gotraw = {frozenset(t) for t in raw["confirmed_relations"]}
            assert res["spurious"] == 0, f"{kind}: spurious>0"
            assert got == bf, f"{kind}: composed solver != brute force {got} vs {bf}"
            assert gotraw == bf, f"{kind}: raw baseline != brute force {gotraw} vs {bf}"
            assert frozenset((i, j)) in got, f"{kind}: missing constructed relation"
            hits += len(bf)
        print(f"    m=2 composed solver == raw baseline == brute-force EC "
              f"({hits} relations, spurious=0): OK")

    # d_reg engine sanity: the raw baseline reproduces P3's 2|F|+1 on the composed base.
    mp = make_map(C, "product_2aux", 2)
    base = build_petit_base(C, mp)
    R = ec_add(base.points[0], base.points[1], 0, p)
    raw = search_relations_petit(C, base, 2, R, "raw_baseline", measure_dreg=True, dreg_max=20)
    expected = 2 * base.n_distinct_x + 1
    print(f"  raw baseline d_reg on |F|={base.n_distinct_x} composed base = "
          f"{raw['d_reg']['d_reg']} (P3 predicts 2|F|+1={expected})")
    assert raw["d_reg"]["d_reg"] == expected, "raw baseline did not reproduce P3's 2|F|+1"
    print("self-test OK")


if __name__ == "__main__":
    _selftest()
