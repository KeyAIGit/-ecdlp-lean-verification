#!/usr/bin/env python3
"""Toy-only screen for the GLV carry half-kernel section.

For each C6 orbit of a j=0 prime-order subgroup, the scalar GLV carry chooses
one of the two horizontal C3 orbits y=+/-r.  The chosen roots define an exact
half-kernel polynomial H of degree (n-1)/6.  The full public orbit polynomial

    P(Y) = H(Y) * (-1)^deg(H) H(-Y)

is even.  Its derivative P'(Y) is odd, so chi(P'(y(Q))) has exactly the C3 and
negation symmetries of the carry.  This script tests that canonical derivative,
its y-twist for R3, and the circuit proxies of the exact half factor.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    berlekamp_massey_complexity,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

NULL_TRIALS = 120


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % p
    return result


def poly_from_roots(roots: list[int], p: int) -> list[int]:
    result = [1]
    for root in roots:
        result = poly_mul(result, [(-root) % p, 1], p)
    return result


def poly_eval(coefficients: list[int], value: int, p: int) -> int:
    result = 0
    for coefficient in reversed(coefficients):
        result = (result * value + coefficient) % p
    return result


def poly_derivative(coefficients: list[int], p: int) -> list[int]:
    return [(index * coefficient) % p for index, coefficient in enumerate(coefficients)][1:]


def scalar_carry(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("GLV carry sum failed")


def best_accuracy(values: list[int], target: list[int]) -> float:
    raw = sum(a == b for a, b in zip(values, target))
    return max(raw, len(target) - raw) / len(target)


def coefficient_linear_complexity(coefficients: list[int], p: int) -> int:
    """Berlekamp-Massey over F_p for a finite coefficient sequence."""
    sequence = [value % p for value in coefficients]
    connection = [1]
    previous = [1]
    length = 0
    shift = 1
    discrepancy_scale = 1

    for index in range(len(sequence)):
        discrepancy = sequence[index]
        for offset in range(1, length + 1):
            if offset < len(connection):
                discrepancy = (discrepancy + connection[offset] * sequence[index - offset]) % p
        if discrepancy == 0:
            shift += 1
            continue

        factor = discrepancy * pow(discrepancy_scale, -1, p) % p
        old = connection[:]
        required = len(previous) + shift
        if len(connection) < required:
            connection.extend([0] * (required - len(connection)))
        for offset, value in enumerate(previous):
            connection[offset + shift] = (connection[offset + shift] - factor * value) % p

        if 2 * length <= index:
            length = index + 1 - length
            previous = old
            discrepancy_scale = discrepancy
            shift = 1
        else:
            shift += 1
    return length


def random_half_roots(root_pairs: list[tuple[int, int]], rng: random.Random) -> list[int]:
    return [pair[rng.getrandbits(1)] for pair in root_pairs]


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    c6_orbits: int
    half_kernel_degree: int
    full_orbit_polynomial_degree: int
    full_polynomial_even: bool
    factorization_passed: bool
    exact_zero_membership_decoder: bool
    derivative_nonzero_checks: int
    derivative_carry_accuracy: float
    derivative_exact_carry_decoder: bool
    derivative_r3_accuracy: float
    derivative_exact_r3_decoder: bool
    half_nonzero_coefficients: int
    half_coefficient_density: float
    half_linear_complexity: int
    half_linear_complexity_ratio: float
    null_trials: int
    null_median_density: float
    null_q05_density: float
    null_median_complexity_ratio: float
    null_q05_complexity_ratio: float
    density_empirical_lower_percentile: float
    complexity_empirical_lower_percentile: float


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    psi = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi(k), p) for k in range(1, order)]
    if any(value not in (-1, 1) for value in rho[1:]):
        raise AssertionError("EDS residue vanished")

    visited: set[int] = set()
    positive_roots: list[int] = []
    root_pairs: list[tuple[int, int]] = []

    for k in range(1, order):
        if k in visited:
            continue
        positive_c3 = {k, lam * k % order, lam2 * k % order}
        negative_c3 = {order - member for member in positive_c3}
        orbit6 = positive_c3 | negative_c3
        if len(orbit6) != 6:
            raise AssertionError("nontrivial C6 orbit had wrong size")
        visited.update(orbit6)

        sign = scalar_carry(k, lam, order)
        point = points[k]
        assert point is not None
        y = point[1]
        if any(points[member][1] != y for member in positive_c3):
            raise AssertionError("C3 orbit did not share y")
        if any(points[member][1] != (-y) % p for member in negative_c3):
            raise AssertionError("negative C3 orbit did not share -y")

        if sign == 1:
            chosen = y
        else:
            chosen = (-y) % p
        positive_roots.append(chosen)
        root_pairs.append((y, (-y) % p))

    expected_degree = (order - 1) // 6
    if len(positive_roots) != expected_degree:
        raise AssertionError("half-kernel root count failed")

    half = poly_from_roots(positive_roots, p)
    negative_half = poly_from_roots([(-root) % p for root in positive_roots], p)
    full = poly_mul(half, negative_half, p)
    all_roots = [root for pair in root_pairs for root in pair]
    direct_full = poly_from_roots(all_roots, p)
    factorization = full == direct_full
    even = all(coefficient == 0 for index, coefficient in enumerate(full) if index & 1)
    derivative = poly_derivative(full, p)

    target_carry: list[int] = []
    target_r3: list[int] = []
    derivative_signs: list[int] = []
    derivative_y_signs: list[int] = []
    exact_membership = True
    derivative_checks = 0

    for k in range(1, order):
        point = points[k]
        assert point is not None
        y = point[1]
        carry = scalar_carry(k, lam, order)
        target_carry.append(carry)
        target_r3.append(rho[k] * rho[lam * k % order] * rho[lam2 * k % order])
        exact_membership &= (poly_eval(half, y, p) == 0) == (carry == 1)

        value = poly_eval(derivative, y, p)
        if value == 0:
            raise AssertionError("full orbit polynomial had a repeated root")
        derivative_checks += 1
        derivative_signs.append(quadratic_character(value, p))
        derivative_y_signs.append(quadratic_character(y * value, p))

    carry_accuracy = best_accuracy(derivative_signs, target_carry)
    r3_accuracy = best_accuracy(derivative_y_signs, target_r3)

    nonzero = sum(value != 0 for value in half)
    density = nonzero / len(half)
    complexity = coefficient_linear_complexity(half, p)
    complexity_ratio = complexity / len(half)

    rng = random.Random(20260812 + 31 * p + order)
    null_density: list[float] = []
    null_complexity_ratio: list[float] = []
    for _ in range(NULL_TRIALS):
        random_half = poly_from_roots(random_half_roots(root_pairs, rng), p)
        null_density.append(sum(value != 0 for value in random_half) / len(random_half))
        null_complexity_ratio.append(
            coefficient_linear_complexity(random_half, p) / len(random_half)
        )
    null_density.sort()
    null_complexity_ratio.sort()
    q05_index = math.ceil(0.05 * NULL_TRIALS) - 1

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        c6_orbits=len(root_pairs),
        half_kernel_degree=len(half) - 1,
        full_orbit_polynomial_degree=len(full) - 1,
        full_polynomial_even=even,
        factorization_passed=factorization,
        exact_zero_membership_decoder=exact_membership,
        derivative_nonzero_checks=derivative_checks,
        derivative_carry_accuracy=carry_accuracy,
        derivative_exact_carry_decoder=carry_accuracy == 1.0,
        derivative_r3_accuracy=r3_accuracy,
        derivative_exact_r3_decoder=r3_accuracy == 1.0,
        half_nonzero_coefficients=nonzero,
        half_coefficient_density=density,
        half_linear_complexity=complexity,
        half_linear_complexity_ratio=complexity_ratio,
        null_trials=NULL_TRIALS,
        null_median_density=statistics.median(null_density),
        null_q05_density=null_density[q05_index],
        null_median_complexity_ratio=statistics.median(null_complexity_ratio),
        null_q05_complexity_ratio=null_complexity_ratio[q05_index],
        density_empirical_lower_percentile=(
            sum(value <= density for value in null_density) / NULL_TRIALS
        ),
        complexity_empirical_lower_percentile=(
            sum(value <= complexity_ratio for value in null_complexity_ratio) / NULL_TRIALS
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("carry_half_kernel_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "CARRY-HALF-KERNEL-012",
        "exact_section": (
            "H_G(Y)=product over carry-positive C3 orbits of (Y-y_orbit); "
            "degree (n-1)/6"
        ),
        "public_full_polynomial": "P_G(Y)=constant*H_G(Y)H_G(-Y)",
        "canonical_derivative_candidates": {
            "carry": "chi(P_G'(y(Q)))",
            "R3": "chi(y(Q) P_G'(y(Q)))",
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "all_factorizations_passed": all(case.factorization_passed for case in cases),
            "all_full_polynomials_even": all(case.full_polynomial_even for case in cases),
            "all_exact_zero_membership_decoders_passed": all(
                case.exact_zero_membership_decoder for case in cases
            ),
            "exact_derivative_carry_decoders": sum(
                case.derivative_exact_carry_decoder for case in cases
            ),
            "exact_derivative_r3_decoders": sum(
                case.derivative_exact_r3_decoder for case in cases
            ),
            "large_order_mean_derivative_carry_accuracy": sum(
                case.derivative_carry_accuracy for case in large
            ) / len(large),
            "large_order_mean_derivative_r3_accuracy": sum(
                case.derivative_r3_accuracy for case in large
            ) / len(large),
            "large_order_mean_half_coefficient_density": sum(
                case.half_coefficient_density for case in large
            ) / len(large),
            "large_order_mean_half_linear_complexity_ratio": sum(
                case.half_linear_complexity_ratio for case in large
            ) / len(large),
            "largest_order": max(case.order for case in cases),
            "secp256k1_half_kernel_degree": (
                0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 - 1
            ) // 6,
        },
        "interpretation_rule": (
            "The zero-membership section is exact by construction but useful only if "
            "H has a sub-square-root public evaluation circuit. Low coefficient density, "
            "low recurrence complexity, or an exact derivative decoder would be positive evidence."
        ),
        "claim_boundary": [
            "The exact half factor depends on the carry labeling and is not yet publicly computable.",
            "Coefficient sparsity and Berlekamp-Massey complexity are circuit diagnostics, not lower bounds.",
            "The full polynomial is public in principle as the subgroup orbit polynomial, but no sub-square-root representation is claimed.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
