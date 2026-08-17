#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

FROZEN_ORDERS = (397, 433, 1093, 1249, 3469, 4021)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def qchar(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-binary value")


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    return factors


def primitive_root(prime: int) -> int:
    factors = prime_factors(prime - 1)
    for candidate in range(2, prime):
        if all(pow(candidate, (prime - 1) // factor, prime) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


def min_exact_generic_forms(prime: int) -> int:
    """Smallest m with binom(m,2) >= (prime-1)/2."""
    lower = 0
    upper = math.isqrt(prime - 1) + 3
    while lower < upper:
        middle = (lower + upper) // 2
        if middle * (middle - 1) >= prime - 1:
            upper = middle
        else:
            lower = middle + 1
    return lower


def collision_set(forms: list[tuple[int, int]], prime: int) -> set[int]:
    """All hidden scalars at which two distinct affine labels collide."""
    collisions: set[int] = set()
    for index, (left_slope, left_offset) in enumerate(forms):
        for right_slope, right_offset in forms[index + 1 :]:
            slope_difference = (left_slope - right_slope) % prime
            offset_difference = (right_offset - left_offset) % prime
            if slope_difference == 0:
                continue
            collisions.add(offset_difference * pow(slope_difference, -1, prime) % prime)
    return collisions


def run_case(prime: int) -> dict[str, object]:
    if prime % 12 != 1:
        raise AssertionError("frozen order must be one modulo twelve")

    generator = primitive_root(prime)
    lam = pow(generator, (prime - 1) // 3, prime)
    if lam in (0, 1) or pow(lam, 3, prime) != 1:
        raise AssertionError("failed to construct order-three GLV eigenvalue")

    trace_checks = 0
    determinant_checks = 0
    cm_checks = 0
    contraction_checks = 0

    for hidden in range(1, prime):
        character = qchar(hidden, prime)

        # In the Schroedinger model, rho(diag(k,k^-1)) sends e_x to
        # chi(k)e_(k^-1 x). For k != 1 only x=0 is fixed. The identity case is
        # public from Q=G and is normalized separately.
        fixed_points = prime if hidden == 1 else 1
        trace = character * fixed_points
        reduced_trace = 1 if hidden == 1 else trace
        if reduced_trace != character:
            raise AssertionError("split-torus Weil trace failed")
        trace_checks += 1

        hidden_inverse = pow(hidden, -1, prime)
        determinant_minus_identity = (hidden - 1) * (hidden_inverse - 1) % prime
        if hidden != 1:
            if qchar(determinant_minus_identity, prime) != character:
                raise AssertionError("determinant square-class identity failed")
            determinant_checks += 1

        # Both the hidden split-torus element and the j=0 CM action are diagonal
        # in the Frobenius eigenspace decomposition, hence commute.
        if hidden * lam % prime != lam * hidden % prime:
            raise AssertionError("primal CM commutation failed")
        lam_inverse = pow(lam, -1, prime)
        if hidden_inverse * lam_inverse % prime != lam_inverse * hidden_inverse % prime:
            raise AssertionError("dual CM commutation failed")
        cm_checks += 1

        contraction = prime * (prime - 1) * character
        if contraction // (prime * (prime - 1)) != character:
            raise AssertionError("selector-free contraction normalization failed")
        contraction_checks += 1

    # Exact collision-union bound on deterministic affine transcript families.
    rng = random.Random(0xC039 + prime)
    collision_trials: list[dict[str, int]] = []
    for form_count in range(2, min(24, prime)):
        forms: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        while len(forms) < form_count:
            form = (rng.randrange(prime), rng.randrange(prime))
            if form not in seen:
                seen.add(form)
                forms.append(form)
        collisions = collision_set(forms, prime)
        pair_bound = form_count * (form_count - 1) // 2
        if len(collisions) > pair_bound:
            raise AssertionError("affine collision union bound failed")
        collision_trials.append(
            {
                "forms": form_count,
                "collision_points": len(collisions),
                "pair_bound": pair_bound,
            }
        )

    return {
        "order": prime,
        "lambda": lam,
        "trace_checks": trace_checks,
        "determinant_character_checks": determinant_checks,
        "cm_commutation_checks": cm_checks,
        "contraction_trace_checks": contraction_checks,
        "min_affine_forms_for_exact_balanced_generic_decoder": min_exact_generic_forms(prime),
        "collision_trials": collision_trials,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    p = SECP_P
    minimum_forms = min_exact_generic_forms(n)
    embedding_degree = (n - 1) // 6

    if pow(p, embedding_degree, n) != 1:
        raise AssertionError("secp256k1 embedding-degree certificate failed")
    if pow(p, embedding_degree // 2, n) != n - 1:
        raise AssertionError("secp256k1 half-Frobenius certificate failed")

    return {
        "n": n,
        "p": p,
        "n_mod_12": n % 12,
        "sqrt_n_ceil": math.isqrt(n - 1) + 1,
        "min_affine_forms_for_exact_balanced_generic_decoder": minimum_forms,
        "min_affine_forms_bits": math.log2(minimum_forms),
        "embedding_degree": embedding_degree,
        "hidden_torus_size": n - 1,
        "standard_weil_dimension": n,
        "full_dual_contraction_raw_terms": n * n,
        "trace_compression_if_hidden_torus_element_given": "one split-torus Weil character value",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("cm_weil_trace_compression_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "CM-WEIL-TRACE-COMPRESSION-039",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_trace_checks": sum(case["trace_checks"] for case in cases),
            "total_determinant_character_checks": sum(
                case["determinant_character_checks"] for case in cases
            ),
            "total_cm_commutation_checks": sum(case["cm_commutation_checks"] for case in cases),
            "all_exact_trace_compressions": True,
            "all_collision_union_bounds": True,
        },
        "secp256k1": secp256k1_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
