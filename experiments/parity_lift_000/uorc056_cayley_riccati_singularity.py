#!/usr/bin/env python3
"""Exact finite-field replay for the Cayley-Riccati singularity boundary.

No curve, point, key, wallet, hidden scalar, or production-sized target is
accepted. The executable checks only projective algebra over frozen small prime
fields and canonical parity under the public +2 step on frozen odd cycles.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FIELD_PRIMES = (5, 7, 11, 13, 17, 19, 23, 29, 31)
CYCLE_ORDERS = (7, 11, 13, 17, 19, 23, 31)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def riccati_pair(c: int, r: int, p: int) -> tuple[int, int]:
    numerator = ((c - 1) + (c + 1) * r) % p
    denominator = ((c + 1) + (c - 1) * r) % p
    return numerator, denominator


def run_field_case(p: int) -> dict[str, object]:
    projective_identity_checks = 0
    rational_update_checks = 0
    fixed_branch_checks = 0

    for c in range(p):
        for r in range(p):
            expected_numerator = (c * (1 + r) - (1 - r)) % p
            expected_denominator = (c * (1 + r) + (1 - r)) % p
            actual = riccati_pair(c, r, p)
            if actual != (expected_numerator, expected_denominator):
                raise AssertionError("Cayley projective identity failed")
            projective_identity_checks += 1

    for c in range(1, p):
        plus_pair = riccati_pair(c, 1, p)
        minus_pair = riccati_pair(c, p - 1, p)
        if plus_pair[0] != plus_pair[1] or plus_pair[0] == 0:
            raise AssertionError("regular multiplier did not fix +1 projectively")
        if plus_pair[0] == (-plus_pair[1]) % p:
            raise AssertionError("regular multiplier swapped +1 to -1")
        if minus_pair[0] != (-minus_pair[1]) % p or minus_pair[1] == 0:
            raise AssertionError("regular multiplier did not fix -1 projectively")
        if minus_pair[0] == minus_pair[1]:
            raise AssertionError("regular multiplier swapped -1 to +1")
        fixed_branch_checks += 2

        for r in range(p):
            cayley_denominator = (1 - r) % p
            if cayley_denominator == 0:
                continue
            z = (1 + r) * pow(cayley_denominator, -1, p) % p
            updated_z = c * z % p
            inverse_cayley_denominator = (updated_z + 1) % p
            if inverse_cayley_denominator == 0:
                continue
            direct_update = (
                (updated_z - 1) * pow(inverse_cayley_denominator, -1, p)
            ) % p
            numerator, denominator = riccati_pair(c, r, p)
            if denominator == 0:
                raise AssertionError("projective denominator mismatch")
            riccati_update = numerator * pow(denominator, -1, p) % p
            if direct_update != riccati_update:
                raise AssertionError("rational Cayley conjugacy failed")
            rational_update_checks += 1

    degenerate_plus_pair = riccati_pair(0, 1, p)
    if degenerate_plus_pair != (0, 0):
        raise AssertionError("zero multiplier did not expose the +1 degeneracy")

    return {
        "field_prime": p,
        "projective_identity_checks": projective_identity_checks,
        "rational_update_checks": rational_update_checks,
        "fixed_branch_checks": fixed_branch_checks,
        "zero_multiplier_plus_pair": list(degenerate_plus_pair),
        "all_regular_multipliers_fix_both_selector_branches": True,
        "regular_branch_swap_found": False,
    }


def run_cycle_case(order: int) -> dict[str, object]:
    transitions = 0
    parity_preserving = 0
    parity_flips: list[int] = []

    for scalar in range(1, order):
        next_scalar = (scalar + 2) % order
        if next_scalar == 0:
            continue
        transitions += 1
        if scalar % 2 == next_scalar % 2:
            parity_preserving += 1
        else:
            parity_flips.append(scalar)

    if parity_flips != [order - 1]:
        raise AssertionError("the public +2 step did not have one canonical wrap flip")

    return {
        "order": order,
        "nonidentity_transitions": transitions,
        "parity_preserving_transitions": parity_preserving,
        "parity_flip_transitions": len(parity_flips),
        "unique_flip_scalar": parity_flips[0],
        "unique_flip_is_canonical_wrap": parity_flips[0] == order - 1,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "translation_step": 2,
        "nonidentity_wrap_flip_scalar": n - 1,
        "regular_cayley_multiplier_preserves_plus_branch": True,
        "regular_cayley_multiplier_preserves_minus_branch": True,
        "branch_flip_requires_zero_pole_or_undefined_step": True,
        "riccati_recurrence_is_cayley_conjugate_to_multiplication": True,
        "local_singularity_location_evaluator_found": False,
        "nonlocal_algebraic_seed_propagation_remains_open": True,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "public_parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    field_cases = [run_field_case(p) for p in FIELD_PRIMES]
    cycle_cases = [run_cycle_case(order) for order in CYCLE_ORDERS]
    aggregate = {
        "field_cases": len(field_cases),
        "cycle_cases": len(cycle_cases),
        "projective_identity_checks": sum(
            case["projective_identity_checks"] for case in field_cases
        ),
        "rational_update_checks": sum(
            case["rational_update_checks"] for case in field_cases
        ),
        "fixed_branch_checks": sum(
            case["fixed_branch_checks"] for case in field_cases
        ),
        "cycle_nonidentity_transitions": sum(
            case["nonidentity_transitions"] for case in cycle_cases
        ),
        "cycle_parity_preserving_transitions": sum(
            case["parity_preserving_transitions"] for case in cycle_cases
        ),
        "cycle_parity_flip_transitions": sum(
            case["parity_flip_transitions"] for case in cycle_cases
        ),
        "all_regular_multipliers_fix_both_branches": all(
            case["all_regular_multipliers_fix_both_selector_branches"]
            for case in field_cases
        ),
        "all_cycles_have_one_wrap_flip": all(
            case["unique_flip_is_canonical_wrap"] for case in cycle_cases
        ),
    }
    payload = {
        "package": "UORC056-CAYLEY-RICCATI-SINGULARITY-B19",
        "field_cases": field_cases,
        "cycle_cases": cycle_cases,
        "aggregate": aggregate,
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The natural Möbius/Riccati selector recurrence is exactly Cayley-"
            "conjugate to multiplicative cocycle transport. Every regular "
            "nonzero multiplier fixes selector branches +1 and -1, while the "
            "canonical +2 parity sequence has one wrap flip. Hence the useful "
            "information is concentrated in a zero, pole, or undefined cut; "
            "regular nonlinear propagation does not remove the endpoint problem."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
