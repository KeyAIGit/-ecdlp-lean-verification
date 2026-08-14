#!/usr/bin/env python3
"""Exact frozen replay for UORC056 Hilbert-90 integration B13.

No external curve, point, key, wallet, unknown scalar, or production-sized DLP
input is accepted. Production constants are used only for public cost counts.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from uorc056_oriented_principal_pell_core import SECP_N, SECP_P, Point, ec_add, inv
from uorc056_hilbert90_integration_core import (
    COSET_CASES,
    affine_point_count,
    construct_factor,
    factor_value,
    neg,
    scalar_mul,
)
from uorc056_hilbert90_integration_miller import projective_cocycle


def build_case(
    p: int,
    order: int,
    generator: tuple[int, int],
    coset_base: tuple[int, int],
    group_order: int,
) -> dict[str, object]:
    if affine_point_count(p) + 1 != group_order:
        raise AssertionError("frozen group order mismatch")
    points, polynomial_a, polynomial_b, sum_scalar, anchor_scalar = construct_factor(
        p, order, generator
    )
    subgroup = set(points)
    if coset_base in subgroup:
        raise AssertionError("coset base lies in H")

    translation = points[2]
    minus_translation = points[order - 2]
    minus_generator = points[order - 1]
    if scalar_mul((order + 1) // 2, minus_translation, p) != minus_generator:
        raise AssertionError("N(-T)=-G failed")

    coset: list[tuple[int, int]] = []
    current: Point = coset_base
    for _ in range(order):
        if current is None or current in subgroup:
            raise AssertionError("outside coset hit H")
        coset.append(current)
        current = ec_add(current, translation, p)
    if current != coset_base or len(set(coset)) != order:
        raise AssertionError("translation orbit does not have length n")

    factor = [factor_value(polynomial_a, polynomial_b, point, p) for point in coset]
    if any(value == 0 for value in factor):
        raise AssertionError("factor vanished outside H")

    exact: list[int] = []
    projective: list[int] = []
    step_counts: list[int] = []
    ratios: list[int] = []
    for index, point in enumerate(coset):
        exact_value = factor[(index + 1) % order] * inv(factor[index], p) % p
        projective_value, steps = projective_cocycle(
            point, p, order, points, anchor_scalar
        )
        exact.append(exact_value)
        projective.append(projective_value)
        step_counts.append(steps)
        ratios.append(exact_value * inv(projective_value, p) % p)
    if len(set(ratios)) != 1 or len(set(step_counts)) != 1:
        raise AssertionError("compact representative is not projectively constant")
    scalar = ratios[0]

    exact_norm = math.prod(exact) % p
    projective_norm = math.prod(projective) % p
    if exact_norm != 1 or projective_norm != pow(inv(scalar, p), order, p):
        raise AssertionError("cyclic norm identity failed")
    if math.gcd(order, p - 1) != 1:
        raise AssertionError("normalization root is not unique")
    scalar_from_norm = pow(inv(projective_norm, p), pow(order, -1, p - 1), p)
    if scalar_from_norm != scalar:
        raise AssertionError("norm normalization failed")
    if [scalar * value % p for value in projective] != exact:
        raise AssertionError("normalized cocycle mismatch")

    trace = sum(factor) % p
    if trace == 0:
        raise AssertionError("frozen Hilbert-90 trace vanished")
    hilbert_values: list[int] = []
    for start in range(order):
        cumulative = 1
        hilbert_sum = 0
        for offset in range(order):
            hilbert_sum = (hilbert_sum + cumulative) % p
            cumulative = cumulative * exact[(start + offset) % order] % p
        if cumulative != 1 or hilbert_sum != trace * inv(factor[start], p) % p:
            raise AssertionError("explicit Hilbert-90 sum failed")
        hilbert_values.append(hilbert_sum)
    for index in range(order):
        if hilbert_values[(index + 1) % order] != hilbert_values[index] * inv(exact[index], p) % p:
            raise AssertionError("Hilbert-90 recurrence failed")
        if inv(hilbert_values[index], p) != factor[index] * inv(trace, p) % p:
            raise AssertionError("Hilbert-90 reconstruction failed")

    neg_generator = neg(generator, p)
    if neg_generator is None:
        raise AssertionError("generator negation failed")
    _, neg_a, neg_b, _, _ = construct_factor(p, order, neg_generator)
    neg_factor = [factor_value(neg_a, neg_b, neg(point, p), p) for point in coset]
    neg_cocycle = [
        neg_factor[(index + 1) % order] * inv(neg_factor[index], p) % p
        for index in range(order)
    ]
    if neg_cocycle != exact:
        raise AssertionError("generator-negation covariance failed")

    return {
        "field_prime": p,
        "group_order": group_order,
        "subgroup_order": order,
        "cofactor": group_order // order,
        "generator": generator,
        "coset_base": coset_base,
        "coset_length": order,
        "sum_scalar": sum_scalar,
        "anchor_scalar": anchor_scalar,
        "projective_scalar": scalar,
        "projective_norm": projective_norm,
        "exact_norm": exact_norm,
        "gcd_n_p_minus_one": math.gcd(order, p - 1),
        "miller_line_steps_plus_two": step_counts[0],
        "hilbert90_terms_per_value": order,
        "projective_cocycle_exact_mod_constants": True,
        "norm_normalization_exact": True,
        "hilbert90_reconstruction_exact_up_to_invariant_scale": True,
        "generator_negation_covariance_exact": True,
    }


def secp_certificate() -> dict[str, object]:
    half_plus_one = (SECP_N + 1) // 2
    doublings = half_plus_one.bit_length() - 1
    additions = half_plus_one.bit_count() - 1
    return {
        "p": SECP_P,
        "n": SECP_N,
        "gcd_n_p_minus_one": math.gcd(SECP_N, SECP_P - 1),
        "half_plus_one": half_plus_one,
        "miller_multiplier_bit_length": half_plus_one.bit_length(),
        "miller_doubling_steps": doublings,
        "miller_addition_steps": additions,
        "miller_line_steps": doublings + additions,
        "extra_line_factors": 2,
        "projective_cocycle_slp_class": "O(log n)",
        "naive_cyclic_norm_terms": SECP_N,
        "standard_hilbert90_terms": SECP_N,
        "compact_hilbert90_lift_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = [build_case(*case) for case in COSET_CASES]
    aggregate = {
        "cases": len(cases),
        "total_coset_points": sum(case["coset_length"] for case in cases),
        "all_exact_coboundary_norms_one": all(case["exact_norm"] == 1 for case in cases),
        "all_projective_cocycles_valid": all(case["projective_cocycle_exact_mod_constants"] for case in cases),
        "all_norm_normalizations_exact": all(case["norm_normalization_exact"] for case in cases),
        "all_hilbert90_reconstructions_exact": all(case["hilbert90_reconstruction_exact_up_to_invariant_scale"] for case in cases),
        "all_generator_negation_covariances_exact": all(case["generator_negation_covariance_exact"] for case in cases),
    }
    payload = {
        "package": "UORC056-HILBERT90-INTEGRATION-B13",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "The oriented principal factor has an O(log n) projective cocycle. "
            "Exact normalization is a cyclic norm and the standard global "
            "Hilbert-90 lift has n terms. No compact lift or parity oracle is found."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
