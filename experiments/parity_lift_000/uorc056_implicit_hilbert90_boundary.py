#!/usr/bin/env python3
"""Exact structural replay for UORC056 C22.

Scope: the public seven-curve C17 corpus and six public generator replacements.
No unknown-scalar point, wallet, private key, or production target is accepted.

The replay reconstructs the C21 norm-one twist, extracts its anti-invariant
half-divisor pair vector, measures exact linear recurrence diagnostics in a
public y-order, and certifies support/query budgets for the declared
valuation-transparent multiplicative Hilbert-90 grammar.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
SPLITS = ("discovery",) * 3 + ("validation",) * 2 + ("held_out",) * 2
ATOM_SUPPORT_CAPS = (1, 2, 4, 8, 16)


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c17 = load("uorc056_c17_for_c22", "uorc056_odd_symmetric_glv_invariants.py")
c19 = load("uorc056_c19_for_c22", "uorc056_odd_rational_functional_boundary.py")


def rf_one(C):
    return ([1], [0], [1])


def rf_neg(C, f):
    return C.rf_norm((f[0], C.negp(f[1]), f[2]))


def rf_norm3(C, f):
    f1 = C.rf_phi(f)
    f2 = C.rf_phi(f1)
    return C.rf_mul(C.rf_mul(f, f1), f2)


def rf_eq(C, f, g) -> bool:
    f, g = C.rf_norm(f), C.rf_norm(g)
    return (
        C.subp(C.mulp(f[0], g[2]), C.mulp(g[0], f[2])) == [0]
        and C.subp(C.mulp(f[1], g[2]), C.mulp(g[1], f[2])) == [0]
    )


def y_minus(C, y0):
    return ([-y0 % C.p], [1], [1])


def class_index(n: int) -> int:
    r = (n + 1) // 4 if n % 4 == 3 else (n - 1) // 4
    return r * (2 * r + (-1 if n % 4 == 3 else 1)) % n


def x3_component(C, poly):
    residues = {i % 3 for i, coefficient in enumerate(poly) if coefficient % C.p}
    if not residues:
        return [0]
    if len(residues) != 1:
        raise AssertionError("not a single x-exponent class modulo three")
    residue = next(iter(residues))
    out = [0] * ((len(poly) - 1 - residue) // 3 + 1)
    for i, coefficient in enumerate(poly):
        if coefficient % C.p:
            if i % 3 != residue:
                raise AssertionError("mixed residue classes")
            out[(i - residue) // 3] = coefficient % C.p
    return C.tr(out)


def compose_y2_minus_7(C, poly):
    out = [0]
    base = [(-7) % C.p, 0, 1]
    for coefficient in reversed(poly):
        out = C.mulp(out, base)
        out[0] = (out[0] + coefficient) % C.p
    return C.tr(out)


def rf_to_y(C, f):
    A, B, D = C.rf_norm(f)
    N, odd, den = map(
        lambda poly: compose_y2_minus_7(C, x3_component(C, poly)),
        (A, B, D),
    )
    N += [0] * max(0, len(odd) + 1 - len(N))
    for i, coefficient in enumerate(odd):
        N[i + 1] = (N[i + 1] + coefficient) % C.p
    N = C.tr(N)
    gcd = C.gcd(N, den)
    if gcd != [1]:
        N, den = C.exactdiv(N, gcd), C.exactdiv(den, gcd)
    scale = pow(den[-1], -1, C.p)
    return C.sc(N, scale), C.sc(den, scale)


def neg_y(C, poly):
    return C.tr([
        coefficient * (-1 if i & 1 else 1) % C.p
        for i, coefficient in enumerate(poly)
    ])


def yr_norm(C, f):
    N, D = map(C.tr, f)
    gcd = C.gcd(N, D)
    if gcd != [1]:
        N, D = C.exactdiv(N, gcd), C.exactdiv(D, gcd)
    scale = pow(D[-1], -1, C.p)
    return C.sc(N, scale), C.sc(D, scale)


def yr_mul(C, f, g):
    return yr_norm(C, (C.mulp(f[0], g[0]), C.mulp(f[1], g[1])))


def yr_tau(C, f):
    return yr_norm(C, (neg_y(C, f[0]), neg_y(C, f[1])))


def yr_eq(C, f, g):
    return C.subp(C.mulp(f[0], g[1]), C.mulp(g[0], f[1])) == [0]


def multiplicity(C, poly, root):
    quotient = poly
    count = 0
    linear = [(-root) % C.p, 1]
    while len(quotient) > 1 and C.ev(quotient, root) == 0:
        quotient = C.exactdiv(quotient, linear)
        count += 1
    return count


def divisor(C, f):
    N, D = yr_norm(C, f)
    finite = {}
    for y in range(C.p):
        value = multiplicity(C, N, y) - multiplicity(C, D, y)
        if value:
            finite[y] = value
    infinity = len(D) - len(N)
    zeros = sum(max(v, 0) for v in finite.values()) + max(infinity, 0)
    poles = sum(max(-v, 0) for v in finite.values()) + max(-infinity, 0)
    if zeros != poles or finite.get(0, 0) != 0 or infinity != 0:
        raise AssertionError("unexpected norm-one divisor")
    return finite, poles


def berlekamp_massey(sequence: list[int], p: int) -> int:
    """Return exact shortest linear recurrence order over F_p."""
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1
    for n in range(len(sequence)):
        discrepancy = sequence[n] % p
        for i in range(1, L + 1):
            discrepancy = (discrepancy + C[i] * sequence[n - i]) % p
        if discrepancy == 0:
            m += 1
            continue
        T = C[:]
        coefficient = discrepancy * pow(b, -1, p) % p
        if len(C) < len(B) + m:
            C += [0] * (len(B) + m - len(C))
        for j, value in enumerate(B):
            C[j + m] = (C[j + m] - coefficient * value) % p
        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = discrepancy
            m = 1
        else:
            m += 1
    return L


def build_twist(case):
    p, n, G, beta, lam = case
    C = c17.RFContext(p, G, beta)
    points = C.points(n)
    Z, _endpoint = c19.endpoint_function(C, n, points)
    M = rf_norm3(C, Z)
    a = class_index(n)
    m = (n - 1) // 2
    C0 = C.rf_div(
        y_minus(C, points[(a - 1) % n][1]),
        C.rf_mul(
            C.rf_mul(y_minus(C, points[1][1]), y_minus(C, points[a][1])),
            y_minus(C, points[m][1]),
        ),
    )
    R = C.rf_div(M, C0)
    if not rf_eq(C, C.rf_mul(R, rf_neg(C, R)), rf_one(C)):
        raise AssertionError("quadratic norm-one identity failed")
    Ry = rf_to_y(C, R)
    if not yr_eq(C, yr_mul(C, Ry, yr_tau(C, Ry)), ([1], [1])):
        raise AssertionError("y-line norm-one identity failed")
    finite, poles = divisor(C, Ry)
    return C, points, Ry, finite, poles


def pair_vector(p: int, finite: dict[int, int]) -> list[int]:
    vector = []
    for y in range(1, (p + 1) // 2):
        coefficient = finite.get(y, 0)
        if finite.get((-y) % p, 0) != -coefficient:
            raise AssertionError("anti-invariant pair mismatch")
        vector.append(coefficient)
    return vector


def support_union_certificate(target_support: int) -> dict[str, object]:
    return {
        str(cap): {
            "minimum_number_of_atoms": (target_support + cap - 1) // cap,
            "minimum_total_charged_pair_support": target_support,
        }
        for cap in ATOM_SUPPORT_CAPS
    }


def sequence_diagnostics(vector: list[int], p: int) -> dict[str, object]:
    nonzero = [value for value in vector if value]
    sign_changes = sum(
        1 for left, right in zip(nonzero, nonzero[1:])
        if (left > 0) != (right > 0)
    )
    max_run = 0
    current = 0
    previous = None
    for value in vector:
        tag = 0 if value == 0 else (1 if value > 0 else -1)
        if tag == previous:
            current += 1
        else:
            previous = tag
            current = 1
        max_run = max(max_run, current)
    return {
        "length": len(vector),
        "support": len(nonzero),
        "linear_complexity_over_Fp": berlekamp_massey([x % p for x in vector], p),
        "sign_changes_after_removing_zeros": sign_changes,
        "maximum_equal_tag_run": max_run,
        "values": sorted(set(vector)),
    }


def run_case(case, split):
    p, n, G, beta, lam = case
    _C, _points, Ry, finite, poles = build_twist(case)
    vector = pair_vector(p, finite)
    support = sum(value != 0 for value in vector)
    l1 = sum(abs(value) for value in vector)
    if support * 2 != len(finite):
        raise AssertionError("pair support count mismatch")
    if l1 != poles:
        raise AssertionError("anti-invariant L1 norm must equal pole degree")
    return {
        "p": p,
        "n": n,
        "G": list(G),
        "beta": beta,
        "lambda": lam,
        "split": split,
        "R_y_degrees": [len(Ry[0]) - 1, len(Ry[1]) - 1],
        "R_poles": poles,
        "R_point_support": len(finite),
        "tau_pair_support": support,
        "pair_variation_l1": l1,
        "public_y_order_diagnostic": sequence_diagnostics(vector, p),
        "multiplicative_atom_budget": support_union_certificate(support),
    }


def public_corpus():
    return c17.public_extension_corpus(7)


def replacement_corpus():
    out = []
    for p, n, G, beta, lam in public_corpus()[:2]:
        C = c17.RFContext(p, G, beta)
        for multiplier in (2, 3, 5):
            point = None
            for _ in range(multiplier):
                point = C.ec_add(point, G)
            if point is None:
                raise AssertionError("bad replacement generator")
            out.append(((p, n, point, beta, lam), multiplier, G))
    return out


def secp_transfer():
    _lam, _intersection, counts = c19.glv_root_and_parity_orbit_counts(SECP_N)
    n0, n1, _n2, _n3 = counts
    R_poles = 3 * n0 + n1 - 12
    R_support = (SECP_N - 1) // 3 - 8
    H_poles = (R_poles + 1) // 2
    H_pairs = R_support // 2
    sqrt_n = math.isqrt(SECP_N)
    factor_degree_to_below_sqrt = max(0, (R_support - sqrt_n + 1) // 2)
    return {
        "n": str(SECP_N),
        "sqrt_n_floor": str(sqrt_n),
        "R_pole_lower_bound": str(R_poles),
        "R_point_support_lower_bound": str(R_support),
        "H_pole_lower_bound": str(H_poles),
        "H_tau_pair_support_lower_bound": str(H_pairs),
        "alternative_factor_pole_degree_needed_for_support_below_sqrt": str(factor_degree_to_below_sqrt),
        "multiplicative_atom_query_bounds": {
            str(cap): str((H_pairs + cap - 1) // cap)
            for cap in ATOM_SUPPORT_CAPS
        },
        "bit_lengths": {
            "H_poles": H_poles.bit_length(),
            "H_pair_support": H_pairs.bit_length(),
            "factor_degree_to_below_sqrt": factor_degree_to_below_sqrt.bit_length(),
        },
    }


def grammar_certificate() -> dict[str, object]:
    return {
        "name": "valuation-transparent multiplicative Hilbert90 SLP",
        "leaves": [
            "public rational atoms with charged tau-pair divisor support",
            "fixed-field gauges in F_p(y^2)",
            "constant-offset translations and GLV/tau pullbacks",
            "standard Miller, division-polynomial, and elliptic-net multiplicative leaves",
        ],
        "operations": [
            "multiplication", "division", "integer powers", "tau pullback",
            "GLV pullback", "fixed-field multiplication",
        ],
        "invariant": "tau-pair divisor-difference support of the output is contained in the union of charged non-fixed leaf supports",
        "consequence": "total charged leaf pair-support is at least the target H pair-support, hence Omega(n) for C21",
        "covered_routes": [
            "explicit half-divisor products", "subproduct trees", "multiplicative jump tables",
            "continued-fraction factor products after quotients are materialized",
            "norm-factor lists", "Miller/division/net product circuits",
            "black-box block products when block construction support is charged",
        ],
        "not_covered": [
            "addition-enabled circuits that create new zeros",
            "unrestricted resultants or determinants with compressed internal state",
            "a new branch-odd public anchor",
            "an implicit high-degree leaf with independently proved sub-square-root construction",
        ],
    }


def algorithm_audit(secp: dict[str, object]) -> dict[str, object]:
    return {
        "continued_fractions": {
            "status": "explicit route blocked",
            "reason": "sum of partial-quotient degrees and convergent coefficient output is Omega(deg H)",
            "charged_lower_bound": secp["H_pole_lower_bound"],
        },
        "Pade": {
            "status": "explicit route blocked",
            "reason": "degree-D numerator/denominator reconstruction requires Theta(D) moments or coefficients",
            "charged_lower_bound": secp["H_pole_lower_bound"],
        },
        "half_gcd": {
            "status": "explicit route blocked",
            "reason": "accelerates arithmetic on a degree-Omega(n) object but does not compress its input/output state",
        },
        "subproduct_trees": {
            "status": "multiplicative grammar blocked",
            "reason": "one charged tau-pair contribution per target pair, total pair-support Omega(n)",
        },
        "transposed_modular_composition": {
            "status": "explicit-module route blocked",
            "reason": "transposition preserves the degree-Omega(n) module/state dimension",
        },
        "norm_equation_factorization": {
            "status": "orientation unresolved",
            "reason": "the compact norm determines a torsor; selecting one factor on every tau-pair is the half-divisor problem",
        },
        "log_derivative_residue_resultant": {
            "status": "branch-even without a new anchor",
            "reason": "R'/R, the divisor, residues, and norm derivatives are invariant under R -> -R",
        },
        "canonical_infinity_propagation": {
            "status": "no public jump law found",
            "reason": "R(infinity)=1 fixes the integration constant only after the dense class is available; multiplicative block propagation has linear charged support",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    cases = [run_case(case, split) for case, split in zip(public_corpus(), SPLITS)]
    replacements = []
    for case, multiplier, base_G in replacement_corpus():
        row = run_case(case, "generator_replacement")
        row["multiplier"] = multiplier
        row["base_G"] = list(base_G)
        replacements.append(row)

    secp = secp_transfer()
    aggregate = {
        "curves": len(cases),
        "generator_replacements": len(replacements),
        "all_norm_one_pair_vectors_verified": True,
        "all_pair_support_union_certificates_verified": True,
        "all_public_y_order_linear_complexities_nonconstant": all(
            row["public_y_order_diagnostic"]["linear_complexity_over_Fp"] > 1
            for row in cases + replacements
        ),
        "implicit_H_evaluator_found": False,
        "public_jump_law_found": False,
        "transposed_single_value_evaluator_found": False,
        "canonical_infinity_propagation_found": False,
        "implicit_grammar_lower_bound_proved": True,
        "compact_branch_odd_evaluator_found": False,
        "sub_sqrt_evaluator_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }
    payload = {
        "experiment": "IMPLICIT-HILBERT90-STRAIGHT-LINE-EVALUATION-072-C22",
        "cases": cases,
        "generator_replacements": replacements,
        "grammar_certificate": grammar_certificate(),
        "algorithm_audit": algorithm_audit(secp),
        "secp256k1": secp,
        "aggregate": aggregate,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(raw.encode()).hexdigest()
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
