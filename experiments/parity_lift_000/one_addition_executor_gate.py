#!/usr/bin/env python3
"""Exact toy replay for ONE-ADDITION-EXECUTOR-GATE-OA1.

This script accepts no external point or production-sized target.  It:

1. verifies the exact public identity

   chi(1-x([k]G)^3/x(G)^3)
     = chi(x(G)) product_j chi(psi_(k-lambda^j)(G))
                              chi(psi_(k+lambda^j)(G));

2. exhausts a declared one-addition monomial-binomial square-class grammar
   against both GLV carry and the hard odd EDS aggregate R3 on frozen toy
   curves.
"""

from __future__ import annotations

import argparse
import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]
B = 7

FROZEN_CASES = (
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (151, 19, (70, 122)),
    (547, 547, (2, 62)),
    (907, 967, (2, 165)),
    (1051, 1093, (3, 385)),
    (1087, 271, (1017, 688)),
    (1303, 1249, (1, 201)),
    (1663, 433, (126, 1375)),
    (2347, 571, (2107, 1535)),
    (2671, 367, (83, 2009)),
    (2851, 397, (2276, 1015)),
    (3319, 811, (177, 298)),
    (3571, 3469, (4, 1706)),
    (3931, 4021, (4, 1427)),
)

# The two anchor cases screen every x-exponent class.  The remaining cases
# impose the exact function-level GLV gate a == 0 mod 3.
SCREEN_CASES = (
    (547, 547, (2, 62), True),
    (907, 967, (2, 165), True),
    (1051, 1093, (3, 385), False),
    (1087, 271, (1017, 688), False),
    (1303, 1249, (1, 201), False),
)


def inv(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 % p == 0:
            return None
        slope = 3 * x1 * x1 * inv(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None] * order
    point: Point = None
    for scalar in range(order):
        points[scalar] = point
        point = ec_add(point, generator, p)
    if point is not None:
        raise AssertionError("generator does not have the declared order")
    return points


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def nontrivial_cube_root(p: int) -> int:
    for beta in range(2, p):
        if pow(beta, 3, p) == 1:
            return beta
    raise AssertionError("no nontrivial cube root found")


def glv_lambda(
    generator: tuple[int, int], points: list[Point], beta: int, p: int
) -> int:
    image = beta * generator[0] % p, generator[1]
    for scalar, point in enumerate(points):
        if point == image:
            return scalar
    raise AssertionError("GLV image is not on the declared cyclic line")


def division_polynomial_values(generator: tuple[int, int], p: int):
    x, y = generator
    inv_2y = inv(2 * y, p)

    @lru_cache(maxsize=None)
    def psi_nonnegative(index: int) -> int:
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % p
        if index == 3:
            return (3 * pow(x, 4, p) + 12 * B * x) % p
        if index == 4:
            return (
                4
                * y
                * (pow(x, 6, p) + 20 * B * pow(x, 3, p) - 8 * B * B)
            ) % p
        if index % 2 == 1:
            m = (index - 1) // 2
            return (
                psi_nonnegative(m + 2) * pow(psi_nonnegative(m), 3, p)
                - psi_nonnegative(m - 1) * pow(psi_nonnegative(m + 1), 3, p)
            ) % p
        m = index // 2
        return (
            psi_nonnegative(m)
            * inv_2y
            * (
                psi_nonnegative(m + 2) * pow(psi_nonnegative(m - 1), 2, p)
                - psi_nonnegative(m - 2) * pow(psi_nonnegative(m + 1), 2, p)
            )
        ) % p

    def psi(index: int) -> int:
        if index >= 0:
            return psi_nonnegative(index)
        # The division-polynomial/EDS extension is odd in the index.
        return -psi_nonnegative(-index) % p

    return psi


def carry_values(order: int, lam: int) -> list[int]:
    values = [0] * order
    lam2 = lam * lam % order
    for k in range(1, order):
        representative_sum = k + lam * k % order + lam2 * k % order
        if representative_sum not in (order, 2 * order):
            raise AssertionError("unexpected GLV carry value")
        values[k] = -1 if representative_sum == order else 1
    return values


def factor_integer(number: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            factors.append(divisor)
            while number % divisor == 0:
                number //= divisor
        divisor += 1
    if number > 1:
        factors.append(number)
    return factors


def primitive_root(p: int) -> int:
    factors = factor_integer(p - 1)
    for candidate in range(2, p):
        if all(pow(candidate, (p - 1) // factor, p) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


def log_tables(p: int) -> tuple[list[int], list[int]]:
    root = primitive_root(p)
    exponent = [1] * (p - 1)
    logarithm = [-1] * p
    value = 1
    for index in range(p - 1):
        exponent[index] = value
        logarithm[value] = index
        value = value * root % p
    return exponent, logarithm


def constant_masks(p: int) -> tuple[list[int], list[int]]:
    """Bit masks of nonzero c with chi(1+c*t)=+1 or -1."""
    positive = [0] * p
    negative = [0] * p
    for t in range(1, p):
        pos_mask = 0
        neg_mask = 0
        for c in range(1, p):
            value = legendre(1 + c * t, p)
            if value == 1:
                pos_mask |= 1 << (c - 1)
            elif value == -1:
                neg_mask |= 1 << (c - 1)
        positive[t] = pos_mask
        negative[t] = neg_mask
    return positive, negative


def replay_executor_identity(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, int | bool]:
    points = orbit(generator, order, p)
    beta = nontrivial_cube_root(p)
    lam = glv_lambda(generator, points, beta, p)
    if (lam * lam + lam + 1) % order != 0:
        raise AssertionError("invalid order-three GLV scalar")

    psi = division_polynomial_values(generator, p)
    if psi(order) != 0:
        raise AssertionError("division polynomial does not vanish at the order")

    x_generator = generator[0]
    inverse_x_generator_cube = inv(pow(x_generator, 3, p), p)
    field_checks = 0
    character_checks = 0
    zero_scalars: list[int] = []

    for k in range(1, order):
        point = points[k]
        if point is None:
            raise AssertionError("unexpected identity point")
        x_value = point[0]

        product_of_differences = 1
        residue_product = 1
        for j in range(3):
            r = pow(lam, j, order)
            orbit_point = points[r]
            if orbit_point is None:
                raise AssertionError("zero GLV orbit point")

            difference = (x_value - orbit_point[0]) % p
            product_of_differences = product_of_differences * difference % p

            denominator = psi(k) ** 2 * psi(r) ** 2 % p
            ward_value = -psi(k + r) * psi(k - r) * inv(denominator, p) % p
            if ward_value != difference:
                raise AssertionError("Ward difference identity failed")

            residue_product *= legendre(psi(k - r), p)
            residue_product *= legendre(psi(k + r), p)
            field_checks += 1

        cubic_difference = (pow(x_value, 3, p) - pow(x_generator, 3, p)) % p
        if product_of_differences != cubic_difference:
            raise AssertionError("cubic GLV factorization failed")

        public_factor = (1 - pow(x_value, 3, p) * inverse_x_generator_cube) % p
        if public_factor == 0:
            zero_scalars.append(k)
            continue

        right_character = legendre(x_generator, p) * residue_product
        if legendre(public_factor, p) != right_character:
            raise AssertionError("one-addition EDS character identity failed")
        character_checks += 1

    expected_zeros = {
        pow(lam, j, order) for j in range(3)
    } | {
        (-pow(lam, j, order)) % order for j in range(3)
    }
    if set(zero_scalars) != expected_zeros:
        raise AssertionError("unexpected zero set")

    return {
        "p": p,
        "order": order,
        "lambda": lam,
        "field_checks": field_checks,
        "character_checks": character_checks,
        "zero_count": len(zero_scalars),
        "passed": True,
    }


def screen_one_addition_case(
    p: int,
    order: int,
    generator: tuple[int, int],
    unrestricted_x_exponent: bool,
) -> dict[str, object]:
    started = time.monotonic()
    points = orbit(generator, order, p)
    beta = nontrivial_cube_root(p)
    lam = glv_lambda(generator, points, beta, p)
    lam2 = lam * lam % order

    carry = carry_values(order, lam)
    psi = division_polynomial_values(generator, p)
    rho = [0] * order
    for k in range(1, order):
        rho[k] = legendre(psi(k), p)
    r3 = [0] * order
    for k in range(1, order):
        r3[k] = rho[k] * rho[lam * k % order] * rho[lam2 * k % order]

    target_sequences = {"carry": carry, "R3": r3}
    exponent_table, logarithm = log_tables(p)
    positive_masks, negative_masks = constant_masks(p)

    scalars = list(range(1, order))
    x_logs: list[int] = []
    y_logs: list[int] = []
    x_characters: list[int] = []
    y_characters: list[int] = []
    for k in scalars:
        point = points[k]
        if point is None or point[0] == 0 or point[1] == 0:
            raise AssertionError("screen requires nonzero affine coordinates")
        x_logs.append(logarithm[point[0]])
        y_logs.append(logarithm[point[1]])
        x_characters.append(legendre(point[0], p))
        y_characters.append(legendre(point[1], p))

    target_arrays = {
        name: [sequence[k] for k in scalars]
        for name, sequence in target_sequences.items()
    }

    modulus = p - 1
    all_constants = (1 << (p - 1)) - 1
    sample_indices = list(range(min(18, len(scalars))))
    x_exponents = range(modulus) if unrestricted_x_exponent else range(0, modulus, 3)

    branches = (
        # For p == 3 mod 4, an even-y innovation is negation-even, so the
        # prefactor must contain one y to match the anti-invariant carry.
        (
            "even_y_innovation",
            range(0, modulus, 2),
            tuple((x_parity, 1, sign) for x_parity in (0, 1) for sign in (-1, 1)),
        ),
        (
            "odd_y_innovation",
            range(1, modulus, 2),
            tuple(
                (x_parity, y_parity, sign)
                for x_parity in (0, 1)
                for y_parity in (0, 1)
                for sign in (-1, 1)
            ),
        ),
    )

    exact_hits: dict[str, list[dict[str, int | str]]] = {
        name: [] for name in target_sequences
    }
    sampled_survivors = {name: 0 for name in target_sequences}
    exponent_pairs = 0

    for branch_name, y_exponents, prefactors in branches:
        for x_exponent in x_exponents:
            x_part = [x_exponent * value % modulus for value in x_logs]
            for y_exponent in y_exponents:
                exponent_pairs += 1
                sample_logs = [
                    (x_part[index] + y_exponent * y_logs[index]) % modulus
                    for index in sample_indices
                ]

                for x_parity, y_parity, global_sign in prefactors:
                    for target_name in target_sequences:
                        target = target_arrays[target_name]
                        candidate_constants = all_constants

                        for sample_position, point_index in enumerate(sample_indices):
                            desired = target[point_index] * global_sign
                            if x_parity:
                                desired *= x_characters[point_index]
                            if y_parity:
                                desired *= y_characters[point_index]
                            monomial_value = exponent_table[sample_logs[sample_position]]
                            candidate_constants &= (
                                positive_masks[monomial_value]
                                if desired == 1
                                else negative_masks[monomial_value]
                            )
                            if candidate_constants == 0:
                                break

                        if candidate_constants == 0:
                            continue

                        sampled_survivors[target_name] += candidate_constants.bit_count()
                        remaining = candidate_constants
                        while remaining:
                            bit = remaining & -remaining
                            constant = bit.bit_length()
                            remaining -= bit

                            exact = True
                            for point_index in range(len(scalars)):
                                monomial_log = (
                                    x_part[point_index]
                                    + y_exponent * y_logs[point_index]
                                ) % modulus
                                monomial_value = exponent_table[monomial_log]
                                observed = legendre(1 + constant * monomial_value, p)

                                desired = target[point_index] * global_sign
                                if x_parity:
                                    desired *= x_characters[point_index]
                                if y_parity:
                                    desired *= y_characters[point_index]

                                if observed != desired:
                                    exact = False
                                    break

                            if exact:
                                exact_hits[target_name].append(
                                    {
                                        "branch": branch_name,
                                        "x_exponent": x_exponent,
                                        "y_exponent": y_exponent,
                                        "prefactor_x_parity": x_parity,
                                        "prefactor_y_parity": y_parity,
                                        "global_sign": global_sign,
                                        "constant": constant,
                                    }
                                )

    return {
        "p": p,
        "order": order,
        "lambda": lam,
        "unrestricted_x_exponent": unrestricted_x_exponent,
        "exponent_pairs": exponent_pairs,
        "sampled_survivors": sampled_survivors,
        "exact_hits": exact_hits,
        "elapsed_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    identity_results = [
        replay_executor_identity(p, order, generator)
        for p, order, generator in FROZEN_CASES
    ]

    screen_results = [
        screen_one_addition_case(p, order, generator, unrestricted)
        for p, order, generator, unrestricted in SCREEN_CASES
    ]

    aggregate = {
        "identity_cases": len(identity_results),
        "identity_field_checks": sum(int(row["field_checks"]) for row in identity_results),
        "identity_character_checks": sum(
            int(row["character_checks"]) for row in identity_results
        ),
        "all_identity_cases_passed": all(bool(row["passed"]) for row in identity_results),
        "all_identity_zero_counts_equal_six": all(
            int(row["zero_count"]) == 6 for row in identity_results
        ),
        "screen_cases": len(screen_results),
        "unrestricted_x_exponent_cases": sum(
            bool(row["unrestricted_x_exponent"]) for row in screen_results
        ),
        "exact_carry_decoders": sum(
            len(row["exact_hits"]["carry"]) for row in screen_results
        ),
        "exact_R3_decoders": sum(
            len(row["exact_hits"]["R3"]) for row in screen_results
        ),
    }

    output = {
        "schema_version": 1,
        "package": "ONE-ADDITION-EXECUTOR-GATE-OA1",
        "aggregate": aggregate,
        "identity_results": identity_results,
        "screen_results": screen_results,
        "claim_boundary": (
            "Exact frozen replay and declared finite screen only; no universal "
            "one-addition lower bound and no secp256k1 ECDLP algorithm."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(aggregate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
