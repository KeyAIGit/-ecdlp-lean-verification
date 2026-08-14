#!/usr/bin/env python3
"""Exact replay for the UORC-056 pure EDS-decimation closure V10.

This script checks only frozen/public toy curves.  It does not accept an
external point or scalar and does not attempt a production-sized discrete log.

The theorem-level argument is:

* odd division-polynomial indices fail parity negation covariance;
* even indices over q=1 mod 4 fail for the same reason;
* for even m over q=3 mod 4, exact parity would force the complete EDS residue
  row of P=[m]G to be +1 by the division-polynomial chain rule;
* Ward torsion quasi-periodicity plus the EDS recurrence forbids even the three
  simultaneous signs rho_2=rho_(n-2)=rho_(n-1)=+1.

The executable replay verifies the Ward and recurrence identities with the
same normalization as the V9 division-polynomial evaluator and exhaustively
screens even m modulo 2n on the five discovery curves.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from uorc056_division_polynomial_frontier import (
    DivisionPolynomialEvaluator,
    ec_mul,
    load_corpora,
    quadratic_character,
    stable_json,
)

PROFILE_ID = "UORC-056-EDS-DECIMATION-CLOSURE-V10"
DEFAULT_GRAMMAR = Path("experiments/uorc056/divisor_aware_rational_grammar.json")
DEFAULT_OUTPUT = Path("experiments/uorc056/eds_decimation_closure_results.json")


def ward_constants(evaluator: DivisionPolynomialEvaluator, order: int) -> tuple[int, int]:
    p = evaluator.prime
    psi_2 = evaluator.value(2)
    psi_nm2 = evaluator.value(order - 2)
    psi_nm1 = evaluator.value(order - 1)
    if 0 in (psi_2, psi_nm2, psi_nm1):
        raise AssertionError("Ward constants require nonzero neighboring EDS terms")
    a = psi_nm2 * pow(psi_nm1 * psi_2 % p, -1, p) % p
    b = psi_nm1 * psi_nm1 % p
    b = b * psi_2 % p
    b = b * pow(psi_nm2, -1, p) % p
    return a, b


def check_generator(prime: int, order: int, point: tuple[int, int]) -> dict[str, Any]:
    evaluator = DivisionPolynomialEvaluator(prime, 0, 7, point)
    if evaluator.value(order) != 0:
        raise AssertionError("marked point does not have the declared order")

    a, b = ward_constants(evaluator, order)
    psi_1 = evaluator.value(1)
    psi_nm1 = evaluator.value(order - 1)
    psi_np1 = evaluator.value(order + 1)
    psi_2np1 = evaluator.value(2 * order + 1)

    ward_1_rhs = a * b % prime
    ward_1_rhs = ward_1_rhs * psi_1 % prime
    if psi_np1 != ward_1_rhs:
        raise AssertionError("Ward formula failed at (s,k)=(1,1)")

    ward_2_rhs = pow(a, 2, prime) * pow(b, 4, prime) % prime
    ward_2_rhs = ward_2_rhs * psi_1 % prime
    if psi_2np1 != ward_2_rhs:
        raise AssertionError("Ward formula failed at (s,k)=(2,1)")

    recurrence_rhs = (-pow(psi_np1, 3, prime) * psi_nm1) % prime
    if psi_2np1 != recurrence_rhs:
        raise AssertionError("EDS recurrence failed at h=n+1,i=n,j=1")

    rho_2 = quadratic_character(evaluator.value(2), prime)
    rho_nm2 = quadratic_character(evaluator.value(order - 2), prime)
    rho_nm1 = quadratic_character(psi_nm1, prime)
    if 0 in (rho_2, rho_nm2, rho_nm1):
        raise AssertionError("neighboring residues unexpectedly vanished")

    triple_all_residue = rho_2 == rho_nm2 == rho_nm1 == 1
    if prime % 4 == 3 and triple_all_residue:
        raise AssertionError(
            "q=3 mod 4 generator violates Ward-recurrence three-sign obstruction"
        )

    return {
        "rho_2": rho_2,
        "rho_n_minus_2": rho_nm2,
        "rho_n_minus_1": rho_nm1,
        "triple_all_residue": triple_all_residue,
        "chi_minus_one": quadratic_character(-1, prime),
    }


def screen_even_decimations(
    prime: int, order: int, generator: tuple[int, int]
) -> dict[str, Any]:
    evaluators: dict[int, DivisionPolynomialEvaluator] = {}
    for k in range(1, order):
        point = ec_mul(k, generator, prime, 0)
        if point is None:
            raise AssertionError("nonzero subgroup point became infinity")
        evaluators[k] = DivisionPolynomialEvaluator(prime, 0, 7, point)

    exact: list[int] = []
    tested = 0
    invalid_multiples_of_order = 0
    best_m = None
    best_matches = -1
    for m in range(2, 2 * order, 2):
        if m % order == 0:
            invalid_multiples_of_order += 1
            continue
        tested += 1
        matches = 0
        defined = True
        for k in range(1, order):
            value = evaluators[k].value(m)
            sign = quadratic_character(value, prime)
            if sign == 0:
                defined = False
                break
            target = -1 if k & 1 else 1
            matches += int(sign == target)
        if defined and matches == order - 1:
            exact.append(m)
        if defined and matches > best_matches:
            best_matches = matches
            best_m = m

    return {
        "tested_even_residue_classes_mod_2n": tested,
        "invalid_multiples_of_n": invalid_multiples_of_order,
        "exact_candidates": exact,
        "best_m": best_m,
        "best_matches": best_matches,
        "total_nonzero_points": order - 1,
    }


def run(grammar_path: Path) -> dict[str, Any]:
    discovery, holdout = load_corpora(grammar_path)
    all_curves = discovery + holdout

    generator_checks = 0
    q3_generator_checks = 0
    q1_generator_checks = 0
    q3_three_sign_obstruction_violations = 0
    q1_all_residue_triples = 0
    curve_summaries: list[dict[str, Any]] = []

    for prime, order, generator in all_curves:
        q3 = prime % 4 == 3
        triple_all_count = 0
        for multiplier in range(1, order):
            point = ec_mul(multiplier, generator, prime, 0)
            if point is None:
                raise AssertionError("marked generator multiple became infinity")
            row = check_generator(prime, order, point)
            generator_checks += 1
            if q3:
                q3_generator_checks += 1
                q3_three_sign_obstruction_violations += int(row["triple_all_residue"])
            else:
                q1_generator_checks += 1
                q1_all_residue_triples += int(row["triple_all_residue"])
            triple_all_count += int(row["triple_all_residue"])
        curve_summaries.append(
            {
                "p": prime,
                "n": order,
                "p_mod_4": prime % 4,
                "generator_rows_checked": order - 1,
                "all_residue_three_sign_rows": triple_all_count,
            }
        )

    bounded_screens = []
    total_even_classes = 0
    total_exact = 0
    for prime, order, generator in discovery:
        screen = screen_even_decimations(prime, order, generator)
        total_even_classes += int(screen["tested_even_residue_classes_mod_2n"])
        total_exact += len(screen["exact_candidates"])
        bounded_screens.append({"p": prime, "n": order, **screen})

    if q3_three_sign_obstruction_violations:
        raise AssertionError("exact q=3 mod 4 Ward-recurrence obstruction failed")
    if total_exact:
        raise AssertionError("bounded discovery screen found an exact even decimation")

    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "theorem_status": "exact_algebraic_closure_with_primary_source_lock",
        "theorem": {
            "odd_m": "closed_by_negation_covariance",
            "even_m_q_1_mod_4": "closed_by_negation_covariance",
            "even_m_q_3_mod_4": (
                "closed_by_chain_rule_to_all_residue_generator_row_then_"
                "Ward_quasiperiodicity_plus_EDS_recurrence_contradiction"
            ),
            "stronger_three_sign_corollary": (
                "for every generator P of odd prime order over q=3 mod 4, "
                "at least one of chi(psi_2(P)), chi(psi_(n-2)(P)), "
                "chi(psi_(n-1)(P)) equals -1"
            ),
        },
        "exact_replay": {
            "corpus_curves": len(all_curves),
            "generator_rows_checked": generator_checks,
            "q3_generator_rows_checked": q3_generator_checks,
            "q1_generator_rows_checked": q1_generator_checks,
            "q3_three_sign_obstruction_violations": q3_three_sign_obstruction_violations,
            "q1_all_residue_three_sign_rows": q1_all_residue_triples,
            "ward_checks_per_generator": 2,
            "eds_recurrence_checks_per_generator": 1,
            "curve_summaries": curve_summaries,
        },
        "bounded_discovery_even_decimation_screen": {
            "curves": bounded_screens,
            "total_even_classes_tested": total_even_classes,
            "exact_candidates": total_exact,
        },
        "sources": [
            "Shparlinski-Stange, Character Sums with Division Polynomials, Canadian Math. Bulletin 55 (2012), Lemmas 1-3",
            "Stange, Division polynomials for arbitrary isogenies, Research in Number Theory 12:53 (2026), equations (1.1)-(1.3) and chain rule",
            "Bhakta, Character sums of division polynomials twisted by multiplicative functions, Canadian Math. Bulletin FirstView (2026), Lemma 2.3",
        ],
        "decision": "pure_single_division_polynomial_character_route_closed_for_all_indices",
        "next_frontier": [
            "direct field-valued Y_G evaluation",
            "compact distinguished global integration of the oriented Miller cocycle",
            "theta or elliptic-unit formulas",
            "transposed or modular-composition representations",
            "adaptive non-character outputs",
        ],
        "scientific_boundary": (
            "This closes the pure single-division-polynomial quadratic-character "
            "family, not unrestricted arithmetic circuits."
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
            raise SystemExit("EDS decimation closure artifact drift")
        print("UORC056_EDS_DECIMATION_CLOSURE_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
