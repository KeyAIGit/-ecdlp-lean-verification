#!/usr/bin/env python3
"""Corrected UORC-056 EDS-decimation audit V10.

The first V10 no-go attempt was false.  Exact even EDS decimations actually
exist on small q=3 mod 4 prime-order examples.  This replay verifies both the
correct Silverman/Ward normalization and explicit exact parity witnesses, while
keeping the secp256k1 arbitrary-index question open.

The script checks only frozen/public toy curves.  It accepts no external point
or scalar and does not attempt a production-sized discrete log.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from uorc056_division_polynomial_frontier import (
    DivisionPolynomialEvaluator,
    ec_mul,
    load_corpora,
    quadratic_character,
    stable_json,
)

PROFILE_ID = "UORC-056-EDS-DECIMATION-AUDIT-V10"
DEFAULT_GRAMMAR = Path("experiments/uorc056/divisor_aware_rational_grammar.json")
DEFAULT_OUTPUT = Path("experiments/uorc056/eds_decimation_closure_results.json")

# Each tuple is (p,n,G,m,P=[m]G).  In both cases m=2 is an exact parity
# decimation and P has an all-residue nonzero EDS row.
EXACT_DECIMATION_EXAMPLES = (
    (59, 5, (22, 25), 2, (31, 11)),
    (83, 7, (70, 36), 2, (74, 5)),
)


def ward_constants(evaluator: DivisionPolynomialEvaluator, order: int) -> tuple[int, int]:
    """Silverman Theorem 8 normalization from the r+1 and r+2 terms."""
    p = evaluator.prime
    psi_2 = evaluator.value(2)
    psi_np1 = evaluator.value(order + 1)
    psi_np2 = evaluator.value(order + 2)
    if 0 in (psi_2, psi_np1, psi_np2):
        raise AssertionError("Ward constants require nonzero neighboring terms")
    a = psi_np2 * pow(psi_2 * psi_np1 % p, -1, p) % p
    b = psi_2 * psi_np1 * psi_np1 % p
    b = b * pow(psi_np2, -1, p) % p
    return a, b


def check_ward(evaluator: DivisionPolynomialEvaluator, order: int) -> dict[str, Any]:
    p = evaluator.prime
    a, b = ward_constants(evaluator, order)
    checks = 0
    for s in (1, 2):
        for k in range(1, min(order, 8)):
            lhs = evaluator.value(s * order + k)
            rhs = pow(a, k * s, p) * pow(b, s * s, p) % p
            rhs = rhs * evaluator.value(k) % p
            if lhs != rhs:
                raise AssertionError(
                    f"corrected Ward formula failed: n={order}, s={s}, k={k}"
                )
            checks += 1
    return {
        "a": a,
        "b": b,
        "chi_a": quadratic_character(a, p),
        "chi_b": quadratic_character(b, p),
        "exact_checks": checks,
    }


def residue_row(evaluator: DivisionPolynomialEvaluator, order: int) -> list[int]:
    result = []
    for k in range(1, order):
        sign = quadratic_character(evaluator.value(k), evaluator.prime)
        if sign == 0:
            raise AssertionError("nonzero row term vanished before the point order")
        result.append(sign)
    return result


def exact_decimation_record(
    prime: int,
    order: int,
    generator: tuple[int, int],
    m: int,
    expected_remarked: tuple[int, int],
) -> dict[str, Any]:
    if ec_mul(order, generator, prime, 0) is not None:
        raise AssertionError("witness generator does not have declared order")
    remarked = ec_mul(m, generator, prime, 0)
    if remarked != expected_remarked:
        raise AssertionError("re-marked witness point drifted")

    generator_eval = DivisionPolynomialEvaluator(prime, 0, 7, generator)
    rho_m = quadratic_character(generator_eval.value(m), prime)
    if rho_m != -1:
        raise AssertionError("exact witness must have rho_m=-1")

    outputs = []
    for k in range(1, order):
        query = ec_mul(k, generator, prime, 0)
        assert query is not None
        evaluator = DivisionPolynomialEvaluator(prime, 0, 7, query)
        sign = quadratic_character(evaluator.value(m), prime)
        target = -1 if k & 1 else 1
        if sign != target:
            raise AssertionError("small exact EDS decimation witness drifted")
        outputs.append(sign)

    remarked_eval = DivisionPolynomialEvaluator(prime, 0, 7, remarked)
    row = residue_row(remarked_eval, order)
    if not all(sign == 1 for sign in row):
        raise AssertionError("re-marked witness row is no longer all-residue")
    ward = check_ward(remarked_eval, order)

    lhs = remarked_eval.value(2 * order + 1)
    rhs = (
        -pow(remarked_eval.value(order + 1), 3, prime)
        * remarked_eval.value(order - 1)
    ) % prime
    if lhs != rhs:
        raise AssertionError("specialized EDS recurrence failed")

    return {
        "p": prime,
        "n": order,
        "G": list(generator),
        "m": m,
        "P_equals_mG": list(remarked),
        "p_mod_4": prime % 4,
        "chi_minus_one": quadratic_character(-1, prime),
        "rho_m_at_G": rho_m,
        "decimation_outputs": outputs,
        "target_parity": [(-1 if k & 1 else 1) for k in range(1, order)],
        "exact_parity_decimation": True,
        "remarked_residue_row": row,
        "remarked_row_all_residue": True,
        "ward_at_remarked_generator": ward,
        "specialized_recurrence_exact": True,
    }


def screen_even_decimations(prime: int, order: int, generator: tuple[int, int]) -> dict[str, Any]:
    evaluators: dict[int, DivisionPolynomialEvaluator] = {}
    for k in range(1, order):
        point = ec_mul(k, generator, prime, 0)
        if point is None:
            raise AssertionError("nonzero subgroup point became infinity")
        evaluators[k] = DivisionPolynomialEvaluator(prime, 0, 7, point)

    exact: list[int] = []
    tested = 0
    best_m = None
    best_matches = -1
    for m in range(2, 2 * order, 2):
        if m % order == 0:
            continue
        tested += 1
        matches = 0
        defined = True
        for k in range(1, order):
            sign = quadratic_character(evaluators[k].value(m), prime)
            if sign == 0:
                defined = False
                break
            matches += int(sign == (-1 if k & 1 else 1))
        if defined and matches == order - 1:
            exact.append(m)
        if defined and matches > best_matches:
            best_matches = matches
            best_m = m
    return {
        "tested_even_classes_mod_2n": tested,
        "exact_candidates": exact,
        "best_m": best_m,
        "best_matches": best_matches,
        "total_nonzero_points": order - 1,
    }


def run(grammar_path: Path) -> dict[str, Any]:
    discovery, _ = load_corpora(grammar_path)
    witnesses = [exact_decimation_record(*row) for row in EXACT_DECIMATION_EXAMPLES]

    screens = []
    exact_total = 0
    for prime, order, generator in discovery:
        screen = screen_even_decimations(prime, order, generator)
        exact_total += len(screen["exact_candidates"])
        screens.append({"p": prime, "n": order, **screen})
    if exact_total:
        raise AssertionError("base discovery corpus unexpectedly acquired an exact candidate")

    return {
        "schema_version": "1.2",
        "profile_id": PROFILE_ID,
        "status": "universal_closure_refuted_by_exact_small_curve_witnesses",
        "exact_equivalence": (
            "for even m with n not dividing m: chi(psi_m([k]G))=(-1)^k for all k "
            "iff rho_m(G)=-1 and the re-marked generator P=[m]G has "
            "chi(psi_k(P))=+1 for every 1<=k<n"
        ),
        "normalization_correction": (
            "Silverman Theorem 8 uses the n+1 and n+2 terms for the Ward "
            "constants; the earlier n-1/n-2 inference was invalid"
        ),
        "exact_small_curve_witnesses": witnesses,
        "bounded_base_discovery_screen": {
            "curves": screens,
            "exact_candidates": exact_total,
        },
        "decision": "even_eds_decimation_is_a_real_mechanism_on_small_curves_secp_case_open",
        "next_frontier": [
            "derive generator-change laws for Ward sign invariants and the all-residue property",
            "use character-sum bounds to rule out an all-residue row in the large-order secp256k1 regime if constants can be made explicit",
            "otherwise seek secp-specific constraints from CM/GLV on all-residue generators",
            "direct field-valued Y_G and compact global Miller-cocycle integration remain open",
        ],
        "sources": [
            "Silverman, p-adic properties of division polynomials and elliptic divisibility sequences, Theorem 8",
            "Shparlinski-Stange, Character Sums with Division Polynomials",
            "Stange, Division polynomials for arbitrary isogenies (2026), recurrence and chain rule",
            "Bhakta, Character sums of division polynomials twisted by multiplicative functions (2026), Lemma 2.3",
        ],
        "scientific_boundary": (
            "V10 proves small exact witnesses and an exact re-marking equivalence. "
            "It does not decide whether any even decimation exists for secp256k1."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grammar", type=Path, default=DEFAULT_GRAMMAR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("EDS decimation V10 audit artifact drift")
        print("UORC056_EDS_DECIMATION_AUDIT_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
