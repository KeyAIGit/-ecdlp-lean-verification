#!/usr/bin/env python3
"""Corrected UORC-056 EDS-decimation audit V10.

The valid conclusion is narrower than the first V10 attempt.  An exact even
EDS decimation on q=3 mod 4 would force the EDS residue row of the re-marked
generator P=[m]G to be all +1.  Such rows are NOT impossible: this replay
verifies explicit counterexamples and the correct Silverman/Ward torsion
quasi-period normalization.

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
COUNTEREXAMPLES = (
    (59, 5, (31, 11)),
    (83, 7, (74, 5)),
)


def ward_constants(evaluator: DivisionPolynomialEvaluator, order: int) -> tuple[int, int]:
    """Silverman Theorem 8 normalization from F_(r+1), F_(r+2)."""
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


def counterexample_record(prime: int, order: int, point: tuple[int, int]) -> dict[str, Any]:
    if ec_mul(order, point, prime, 0) is not None:
        raise AssertionError("counterexample point does not have declared order")
    if any(ec_mul(k, point, prime, 0) is None for k in range(1, order)):
        raise AssertionError("counterexample order is not exact")
    evaluator = DivisionPolynomialEvaluator(prime, 0, 7, point)
    row = residue_row(evaluator, order)
    if not all(sign == 1 for sign in row):
        raise AssertionError("counterexample no longer has an all-residue row")
    ward = check_ward(evaluator, order)
    # Specialized recurrence: psi_(2n+1) = -psi_(n+1)^3 psi_(n-1).
    lhs = evaluator.value(2 * order + 1)
    rhs = (-pow(evaluator.value(order + 1), 3, prime) * evaluator.value(order - 1)) % prime
    if lhs != rhs:
        raise AssertionError("specialized EDS recurrence failed")
    return {
        "p": prime,
        "n": order,
        "P": list(point),
        "p_mod_4": prime % 4,
        "chi_minus_one": quadratic_character(-1, prime),
        "residue_row": row,
        "all_nonzero_terms_are_residues": True,
        "ward": ward,
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
    counterexamples = [counterexample_record(*row) for row in COUNTEREXAMPLES]
    screens = []
    exact_total = 0
    for prime, order, generator in discovery:
        screen = screen_even_decimations(prime, order, generator)
        exact_total += len(screen["exact_candidates"])
        screens.append({"p": prime, "n": order, **screen})
    if exact_total:
        raise AssertionError("bounded V10 discovery screen found an exact candidate")

    return {
        "schema_version": "1.1",
        "profile_id": PROFILE_ID,
        "status": "closure_attempt_retracted_after_primary_normalization_check",
        "valid_reduction": (
            "if even m over q=3 mod 4 gives parity, then for P=[m]G the row "
            "chi(psi_k(P)), 1<=k<n, is identically +1"
        ),
        "invalid_step": (
            "all-residue generator rows were claimed impossible using an incorrect "
            "Ward-constant normalization; the primary Silverman normalization uses "
            "the n+1 and n+2 terms and permits chi(a)=+1, chi(b)=-1"
        ),
        "counterexamples": counterexamples,
        "bounded_discovery_even_decimation_screen": {
            "curves": screens,
            "exact_candidates": exact_total,
        },
        "decision": "even_eds_decimation_frontier_remains_open",
        "next_frontier": [
            "classify Ward sign invariants under generator change P=[m]G",
            "test compatibility of an all-residue re-marked row with rho_m=-1 relative to G",
            "derive an exact generator-change cocycle for EDS residue signs",
            "direct field-valued Y_G and compact global Miller-cocycle integration remain open",
        ],
        "sources": [
            "Silverman, p-adic properties of division polynomials and elliptic divisibility sequences, Theorem 8",
            "Stange, Division polynomials for arbitrary isogenies (2026), recurrence and chain rule",
            "Bhakta, Character sums of division polynomials twisted by multiplicative functions (2026), Lemma 2.3",
        ],
        "scientific_boundary": (
            "V10 corrects a failed no-go argument. It neither finds nor rules out "
            "an arbitrary even secp256k1 EDS decimation."
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
