#!/usr/bin/env python3
"""Exact toy replay for ORIENTED-PARITY-DIVISOR-CIRCUIT-046.

The package replaces the vague search for a short parity-divisor circuit by one
specific generator-sensitive object.

For an odd prime-order subgroup H=<G> of E/F_p with

    E: y^2 = x^3 + 7,
    |H| = n,
    M = (n-1)/2,

let K_H(X) contain one x-coordinate from every pair {P,-P} in H\{O}.  There is
a unique polynomial Y_G(X), deg(Y_G)<M, whose value above each Kummer root is
the y-coordinate of the even canonical scalar in that pair.  It satisfies

    Y_G(X)^2 = X^3 + 7 mod K_H(X),

and on every nonzero P=[k]G,

    Y_G(x(P))/y(P) = (-1)^k.

Thus scalar parity is exactly one oriented square root in the split Kummer
algebra F_p[X]/(K_H).  The symmetric kernel data determines the square but not
the branch.  The replay also verifies the scalar-label half-root factorization,
the 2^M branch count certificate, the n-1 distinct generator orientations, and
restricted product-tree/determinant degree-cost bounds.

Only frozen toy subgroups and public secp256k1 constants are processed.  The
script accepts no external point, key, wallet, or production-sized DLP target.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nonlocal_odd_anchor_screen import orbit

CURVE_B = 7
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# A bounded deterministic subset of the existing frozen j=0 corpus.  The
# selected orders keep exact interpolation inexpensive while covering different
# congruence classes and steadily increasing Kummer degrees.
FROZEN_CASES = (
    (151, 19, (70, 122)),
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (1087, 271, (1017, 688)),
    (2851, 397, (2276, 1015)),
    (1663, 433, (126, 1375)),
)


def trim(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_add(
    left: list[int], right: list[int], modulus: int, right_scale: int = 1
) -> list[int]:
    result = [0] * max(len(left), len(right))
    for index in range(len(result)):
        left_value = left[index] if index < len(left) else 0
        right_value = right[index] if index < len(right) else 0
        result[index] = (left_value + right_scale * right_value) % modulus
    return trim(result)


def poly_mul(left: list[int], right: list[int], modulus: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] = (
                result[left_index + right_index] + left_value * right_value
            ) % modulus
    return trim(result)


def poly_eval(poly: list[int], value: int, modulus: int) -> int:
    result = 0
    for coefficient in reversed(poly):
        result = (result * value + coefficient) % modulus
    return result


def poly_from_roots(roots: list[int], modulus: int) -> list[int]:
    result = [1]
    for root in roots:
        result = poly_mul(result, [(-root) % modulus, 1], modulus)
    return result


def poly_negate_argument(poly: list[int], modulus: int) -> list[int]:
    return [
        coefficient if index % 2 == 0 else (-coefficient) % modulus
        for index, coefficient in enumerate(poly)
    ]


def divide_by_linear(
    poly: list[int], root: int, modulus: int
) -> tuple[list[int], int]:
    degree = len(poly) - 1
    if degree < 1:
        raise AssertionError("cannot divide a constant by a linear polynomial")
    quotient = [0] * degree
    quotient[-1] = poly[-1]
    for index in range(degree - 1, 0, -1):
        quotient[index - 1] = (
            poly[index] + root * quotient[index]
        ) % modulus
    remainder = (poly[0] + root * quotient[0]) % modulus
    return trim(quotient), remainder


def poly_mod(poly: list[int], divisor: list[int], modulus: int) -> list[int]:
    if not divisor or divisor[-1] != 1:
        raise AssertionError("the replay expects a monic divisor")
    result = trim(poly[:])
    divisor_degree = len(divisor) - 1
    while len(result) - 1 >= divisor_degree and result != [0]:
        leading = result[-1]
        shift = len(result) - len(divisor)
        for index, coefficient in enumerate(divisor):
            result[index + shift] = (
                result[index + shift] - leading * coefficient
            ) % modulus
        trim(result)
    return result


def interpolate(
    xs: list[int], ys: list[int], modulus: int
) -> tuple[list[int], list[int]]:
    if len(xs) != len(ys) or len(xs) != len(set(xs)):
        raise AssertionError("interpolation nodes must be distinct")
    kernel = poly_from_roots(xs, modulus)
    result = [0]
    for x_value, y_value in zip(xs, ys, strict=True):
        quotient, remainder = divide_by_linear(kernel, x_value, modulus)
        if remainder != 0:
            raise AssertionError("kernel did not vanish at interpolation node")
        denominator = poly_eval(quotient, x_value, modulus)
        if denominator == 0:
            raise AssertionError("kernel was not squarefree")
        scale = y_value * pow(denominator, -1, modulus) % modulus
        result = poly_add(
            result,
            [scale * coefficient % modulus for coefficient in quotient],
            modulus,
        )
    return trim(result), kernel


def scalar_half_root_check(order: int) -> dict[str, int | bool]:
    middle = (order - 1) // 2
    even_roots = list(range(2, order, 2))
    odd_roots = list(range(1, order, 2))
    even_poly = poly_from_roots(even_roots, order)
    odd_poly = poly_from_roots(odd_roots, order)

    # The two canonical parity classes partition F_n^*.
    full_product = poly_mul(even_poly, odd_poly, order)
    expected_product = [order - 1] + [0] * (order - 2) + [1]
    if full_product != expected_product:
        raise AssertionError("oriented half-root factorization failed")

    # Negation swaps the classes: B(X)=(-1)^M A(-X).
    reflected_even = poly_negate_argument(even_poly, order)
    expected_odd = [
        ((-1) ** middle) * coefficient % order
        for coefficient in reflected_even
    ]
    if odd_poly != trim(expected_odd):
        raise AssertionError("negation did not swap the half-root factors")

    decoder_checks = 0
    for scalar in range(1, order):
        even_value = poly_eval(even_poly, scalar, order)
        odd_value = poly_eval(odd_poly, scalar, order)
        denominator = (even_value + odd_value) % order
        if denominator == 0:
            raise AssertionError("scalar parity decoder denominator vanished")
        decoded = (odd_value - even_value) * pow(denominator, -1, order) % order
        expected = 1 if scalar % 2 == 0 else order - 1
        if decoded != expected:
            raise AssertionError("scalar half-root decoder failed")
        decoder_checks += 1

    return {
        "even_polynomial_degree": len(even_poly) - 1,
        "odd_polynomial_degree": len(odd_poly) - 1,
        "decoder_checks": decoder_checks,
        "factorization_verified": True,
        "negation_swap_verified": True,
    }


def generator_orientation_vectors(order: int) -> tuple[int, bool]:
    middle = (order - 1) // 2
    vectors: set[tuple[int, ...]] = set()
    for generator_scalar in range(1, order):
        inverse = pow(generator_scalar, -1, order)
        # At the base pair represented by [j]G, this bit is the parity of its
        # scalar label relative to [generator_scalar]G.
        vector = tuple(
            ((pair_index * inverse) % order) & 1
            for pair_index in range(1, middle + 1)
        )
        vectors.add(vector)

    base = tuple(pair_index & 1 for pair_index in range(1, middle + 1))
    minus_generator_inverse = pow(order - 1, -1, order)
    negated_generator = tuple(
        ((pair_index * minus_generator_inverse) % order) & 1
        for pair_index in range(1, middle + 1)
    )
    global_negation = tuple(1 - bit for bit in base)
    return len(vectors), negated_generator == global_negation


def run_case(
    field_prime: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    if order < 5 or order % 2 == 0:
        raise AssertionError("the subgroup order must be odd and at least five")

    points = orbit(generator, order, field_prime)
    middle = (order - 1) // 2
    scalar_check = scalar_half_root_check(order)

    x_nodes: list[int] = []
    oriented_y_values: list[int] = []
    for pair_index in range(1, middle + 1):
        point = points[pair_index]
        if point is None:
            raise AssertionError("nonzero subgroup index produced the identity")
        x_value, y_value = point
        if y_value % field_prime == 0:
            raise AssertionError("odd-order subgroup contained a two-torsion point")
        x_nodes.append(x_value)
        # The pair {j,n-j} contains exactly one even canonical representative.
        oriented_y_values.append(
            y_value if pair_index % 2 == 0 else (-y_value) % field_prime
        )

    if len(set(x_nodes)) != middle:
        raise AssertionError("Kummer pair representatives were not distinct")

    oriented_sqrt, kernel = interpolate(
        x_nodes, oriented_y_values, field_prime
    )
    if len(kernel) - 1 != middle or len(oriented_sqrt) - 1 >= middle:
        raise AssertionError("interpolation degree contract failed")

    curve_rhs = [CURVE_B, 0, 0, 1]
    square_error = poly_add(
        poly_mul(oriented_sqrt, oriented_sqrt, field_prime),
        curve_rhs,
        field_prime,
        right_scale=-1,
    )
    if poly_mod(square_error, kernel, field_prime) != [0]:
        raise AssertionError("oriented square root congruence failed")

    parity_checks = 0
    for scalar in range(1, order):
        point = points[scalar]
        if point is None:
            raise AssertionError("nonzero scalar produced the identity")
        x_value, y_value = point
        decoded = (
            poly_eval(oriented_sqrt, x_value, field_prime)
            * pow(y_value, -1, field_prime)
            % field_prime
        )
        expected = 1 if scalar % 2 == 0 else field_prime - 1
        if decoded != expected:
            raise AssertionError("oriented Kummer square root lost parity")
        parity_checks += 1

    orientation_count, negation_flips_globally = generator_orientation_vectors(order)
    if orientation_count != order - 1:
        raise AssertionError("distinct generators did not give distinct orientations")
    if not negation_flips_globally:
        raise AssertionError("G -> -G did not globally negate the orientation")

    determinant_rows = {
        str(entry_degree): (middle + entry_degree - 1) // entry_degree
        for entry_degree in (1, 2, 4, 8, 16, 32, 64)
    }

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "kummer_pairs": middle,
        "kernel_degree": len(kernel) - 1,
        "oriented_sqrt_degree": len(oriented_sqrt) - 1,
        "oriented_sqrt_has_maximal_interpolation_degree": (
            len(oriented_sqrt) - 1 == middle - 1
        ),
        "square_root_choices_log2": middle,
        "generator_oriented_roots": orientation_count,
        "negating_generator_negates_orientation": negation_flips_globally,
        "parity_checks": parity_checks,
        "explicit_oriented_leaf_count": middle,
        "binary_product_multiplications_per_half": max(0, middle - 1),
        "bounded_entry_determinant_row_lower_bounds": determinant_rows,
        "scalar_half_root": scalar_check,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    middle = (n - 1) // 2
    pollard = 1 << 128
    determinant_rows = []
    for entry_degree_bits in (0, 32, 64, 96, 128):
        entry_degree = 1 << entry_degree_bits
        rows = (middle + entry_degree - 1) // entry_degree
        determinant_rows.append(
            {
                "entry_degree_bits": entry_degree_bits,
                "minimum_rows": rows,
                "minimum_rows_bits": rows.bit_length(),
            }
        )

    return {
        "n": n,
        "bit_length": n.bit_length(),
        "kummer_pairs": middle,
        "kernel_degree": middle,
        "orientation_square_root_choices": f"2^{middle}",
        "orientation_square_root_choices_log2": middle,
        "distinct_generator_orientations": n - 1,
        "materialized_orientation_coefficients": middle,
        "explicit_product_tree_multiplications": middle - 1,
        "pollard_scale": pollard,
        "bounded_entry_determinant_tradeoff": determinant_rows,
        "selected_successor": "ELLIPTIC-NET-ORIENTED-SQUARE-ROOT-047",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "oriented_parity_divisor_circuit_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "ORIENTED-PARITY-DIVISOR-CIRCUIT-046",
        "scope": (
            "exact scalar half-root and Kummer-oriented-square-root identities "
            "on frozen toy subgroups, plus public secp256k1 size certificates"
        ),
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_kummer_pairs": sum(case["kummer_pairs"] for case in cases),
            "total_parity_checks": sum(case["parity_checks"] for case in cases),
            "total_generator_orientations": sum(
                case["generator_oriented_roots"] for case in cases
            ),
            "total_scalar_decoder_checks": sum(
                case["scalar_half_root"]["decoder_checks"] for case in cases
            ),
            "all_square_root_congruences_passed": True,
            "all_parity_decoders_exact": True,
            "all_generator_orbits_distinct": all(
                case["generator_oriented_roots"] == case["order"] - 1
                for case in cases
            ),
            "all_negations_global": all(
                case["negating_generator_negates_orientation"] for case in cases
            ),
            "all_scalar_factorizations_exact": all(
                case["scalar_half_root"]["factorization_verified"]
                for case in cases
            ),
            "all_toy_oriented_sqrts_maximal_degree": all(
                case["oriented_sqrt_has_maximal_interpolation_degree"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Canonical scalar parity is exactly the ratio Y_G(x(P))/y(P), where "
            "Y_G is one generator-oriented square root of the curve equation "
            "modulo the subgroup Kummer kernel polynomial. Symmetric kernel "
            "data fixes Y_G^2 but leaves 2^((n-1)/2) componentwise branches; "
            "the n-1 possible marked generators select n-1 distinct branches. "
            "Coefficient tables, explicit oriented product trees, and bounded-"
            "degree determinant constructions are too large. A genuinely short "
            "implicit high-degree circuit remains open."
        ),
        "claim_boundary": [
            "The interpolation and square-root identities are exact on the frozen cases.",
            "The 2^M count is the split-algebra branch count, not a general circuit lower bound.",
            "The product-tree and determinant bounds apply only to the declared representations.",
            "Maximal interpolation degree on the toy cases is bounded evidence, not a secp256k1 theorem.",
            "No parity oracle, EDS-residue decoder, or sub-square-root ECDLP algorithm is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
