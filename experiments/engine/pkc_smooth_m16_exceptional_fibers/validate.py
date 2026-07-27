#!/usr/bin/env python3
"""Independently validate the TASK-017 exceptional-fiber certificate.

This module intentionally imports no producer code.  It reconstructs the
decisive finite-field, elliptic-curve, projective S3, recovery, topology, and
GLV facts from constants and compares them with the committed artifact.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
import re
import sys
from functools import cache
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]

D = 564_522
M = 16

CONTROL_P = 564_523
CONTROL_A = 0
CONTROL_B = 7
CONTROL_CURVE_ORDER = 564_469
CONTROL_N = 3_463
CONTROL_COFACTOR = 163
CONTROL_SEED = (2, 100_588)
CONTROL_BASE = (555_781, 547_362)
CONTROL_REPEATED = (169_010, 177_754)
CONTROL_TARGET = (442_919, 534_774)

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
SECP_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
SECP_SOURCE_Y = (
    29_896_722_852_569_046_015_560_700_294_576_055_776_214_335_159_245_303_116_488_692_907_525_646_231_534
)

TASK016_PATH = (
    "experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json"
)
TASK016_SHA256 = (
    "963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19"
)
PRIMARY_CLAIM_EXTRACT = (
    "data/source_claim_extracts/petit_kosters_messeng2016.json"
)
PRIMARY_CLAIM_EXTRACT_SHA256 = (
    "f8839553f6935ed5cd331369cc13d91124373750c757b28eeca3ee773835f14f"
)
SOURCE_CLAIM_IDS = [
    "SC-PKC-SMOOTH-SUBGROUP",
    "SC-SEMAEV-RELATION-SEMANTICS",
    "SC-SECP-NO-TWO-TORSION",
    "SC-GLV-ENDOMORPHISM",
    "SC-GLV-ENDOMORPHISM-NONTRIVIAL",
    "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT",
]
EXCLUDED_CHARACTERISTICS = [2, 3, 7]

Point = tuple[int, int] | None
Kummer = tuple[int, int]

HOMOGENEOUS_S3_TERMS = {
    (2, 0, 2, 0, 0, 2): 1,
    (2, 0, 0, 2, 2, 0): 1,
    (0, 2, 2, 0, 2, 0): 1,
    (2, 0, 1, 1, 1, 1): -2,
    (1, 1, 2, 0, 1, 1): -2,
    (1, 1, 1, 1, 2, 0): -2,
    (1, 1, 0, 2, 0, 2): -28,
    (0, 2, 1, 1, 0, 2): -28,
    (0, 2, 0, 2, 1, 1): -28,
}


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def expect(self, path: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.fail(
                f"{path}: expected {expected!r}, observed {actual!r}"
            )

    def expect_exact(
        self, path: str, actual: Any, expected: Any
    ) -> None:
        if actual != expected:
            self.fail(f"{path}: value differs from independent replay")

    def require_dict(self, path: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.fail(f"{path}: expected object")
            return {}
        return value

    def require_list(self, path: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.fail(f"{path}: expected array")
            return []
        return value

    def require_string(self, path: str, value: Any) -> str:
        if not isinstance(value, str):
            self.fail(f"{path}: expected string")
            return ""
        return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def exact_prime_check(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    for divisor in range(3, math.isqrt(value) + 1, 2):
        if value % divisor == 0:
            return False
    return True


def inverse_mod(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def on_curve(point: Point, prime: int, a: int = 0, b: int = 7) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - x**3 - a * x - b) % prime == 0


def negate(point: Point, prime: int) -> Point:
    if point is None:
        return None
    return point[0], (-point[1]) % prime


def add(
    left: Point,
    right: Point,
    prime: int,
    a: int = 0,
    b: int = 7,
) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    if not on_curve(left, prime, a, b) or not on_curve(
        right, prime, a, b
    ):
        raise ValueError("off-curve input")
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        denominator = 2 * y1 % prime
        if denominator == 0:
            return None
        slope = (3 * x1 * x1 + a) * inverse_mod(
            denominator, prime
        )
    else:
        slope = (y2 - y1) * inverse_mod(x2 - x1, prime)
    slope %= prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    result = (x3, y3)
    if not on_curve(result, prime, a, b):
        raise AssertionError("group operation left the curve")
    return result


def multiply(
    scalar: int,
    point: Point,
    prime: int,
    a: int = 0,
    b: int = 7,
) -> Point:
    if scalar < 0:
        return multiply(-scalar, negate(point, prime), prime, a, b)
    result: Point = None
    addend = point
    value = scalar
    while value:
        if value & 1:
            result = add(result, addend, prime, a, b)
        addend = add(addend, addend, prime, a, b)
        value >>= 1
    return result


def point_sum(
    points: Iterable[Point],
    prime: int,
    a: int = 0,
    b: int = 7,
) -> Point:
    result: Point = None
    for point in points:
        result = add(result, point, prime, a, b)
    return result


def point_record(point: Point) -> dict[str, Any]:
    if point is None:
        return {"kind": "identity"}
    return {"kind": "affine", "x": point[0], "y": point[1]}


def kummer(point: Point) -> Kummer:
    if point is None:
        return (1, 0)
    return (point[0], 1)


def kummer_record(value: Kummer) -> dict[str, int]:
    return {"X": value[0], "Z": value[1]}


def s3_homogeneous(
    prime: int,
    left: Kummer,
    right: Kummer,
    parent: Kummer,
) -> int:
    values = (*left, *right, *parent)
    return sum(
        coefficient
        * math.prod(
            value**exponent
            for value, exponent in zip(
                values, exponents, strict=True
            )
        )
        for exponents, coefficient in HOMOGENEOUS_S3_TERMS.items()
    ) % prime


Monomial = tuple[int, int, int, int, int, int]
Polynomial = dict[Monomial, int]
POLY_ZERO_MONOMIAL: Monomial = (0, 0, 0, 0, 0, 0)


def poly_constant(value: int) -> Polynomial:
    return {} if value == 0 else {POLY_ZERO_MONOMIAL: value}


def poly_variable(index: int) -> Polynomial:
    exponents = [0] * len(POLY_ZERO_MONOMIAL)
    exponents[index] = 1
    return {tuple(exponents): 1}  # type: ignore[return-value]


def poly_add(*values: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for value in values:
        for monomial, coefficient in value.items():
            result[monomial] = (
                result.get(monomial, 0) + coefficient
            )
            if result[monomial] == 0:
                del result[monomial]
    return result


def poly_scale(value: Polynomial, coefficient: int) -> Polynomial:
    if coefficient == 0:
        return {}
    return {
        monomial: coefficient * current
        for monomial, current in value.items()
        if coefficient * current
    }


def poly_subtract(left: Polynomial, right: Polynomial) -> Polynomial:
    return poly_add(left, poly_scale(right, -1))


def poly_multiply(*values: Polynomial) -> Polynomial:
    result = poly_constant(1)
    for value in values:
        product: Polynomial = {}
        for left_monomial, left_coefficient in result.items():
            for right_monomial, right_coefficient in value.items():
                monomial = tuple(
                    left + right
                    for left, right in zip(
                        left_monomial,
                        right_monomial,
                        strict=True,
                    )
                )
                product[monomial] = (
                    product.get(monomial, 0)
                    + left_coefficient * right_coefficient
                )
                if product[monomial] == 0:
                    del product[monomial]
        result = product
    return result


def poly_power(value: Polynomial, exponent: int) -> Polynomial:
    if exponent < 0:
        raise ValueError("negative polynomial exponent")
    result = poly_constant(1)
    base = value
    current = exponent
    while current:
        if current & 1:
            result = poly_multiply(result, base)
        base = poly_multiply(base, base)
        current >>= 1
    return result


def substitute_homogeneous_s3(
    coordinates: tuple[
        Polynomial,
        Polynomial,
        Polynomial,
        Polynomial,
        Polynomial,
        Polynomial,
    ],
) -> Polynomial:
    result: Polynomial = {}
    for exponents, coefficient in HOMOGENEOUS_S3_TERMS.items():
        term = poly_constant(coefficient)
        for coordinate, exponent in zip(
            coordinates, exponents, strict=True
        ):
            term = poly_multiply(
                term,
                poly_power(coordinate, exponent),
            )
        result = poly_add(result, term)
    return result


def reduce_curve_relations(value: Polynomial) -> Polynomial:
    """Reduce by y1^2=x1^3+7 and y2^2=x2^3+7."""
    variables = [poly_variable(index) for index in range(6)]
    x1, x2, y1, y2, u, v = variables
    f1 = poly_add(poly_power(x1, 3), poly_constant(7))
    f2 = poly_add(poly_power(x2, 3), poly_constant(7))
    result: Polynomial = {}
    for monomial, coefficient in value.items():
        x1_power, x2_power, y1_power, y2_power, u_power, v_power = (
            monomial
        )
        term = poly_constant(coefficient)
        term = poly_multiply(
            term,
            poly_power(x1, x1_power),
            poly_power(x2, x2_power),
            poly_power(y1, y1_power % 2),
            poly_power(y2, y2_power % 2),
            poly_power(u, u_power),
            poly_power(v, v_power),
            poly_power(f1, y1_power // 2),
            poly_power(f2, y2_power // 2),
        )
        result = poly_add(result, term)
    return result


@cache
def replay_symbolic_local_identities() -> dict[str, Any]:
    """Prove the general local formulas by sparse integer polynomials."""
    x1, x2, y1, y2, u, v = [
        poly_variable(index) for index in range(6)
    ]
    one = poly_constant(1)
    zero = poly_constant(0)
    sum_x = poly_add(x1, x2)
    product_x = poly_multiply(x1, x2)
    difference_x = poly_subtract(x1, x2)
    leading = poly_power(difference_x, 2)
    linear = poly_scale(
        poly_add(
            poly_multiply(sum_x, product_x),
            poly_constant(14),
        ),
        -2,
    )
    constant = poly_subtract(
        poly_power(product_x, 2),
        poly_scale(sum_x, 28),
    )
    expected_affine = poly_add(
        poly_multiply(leading, poly_power(u, 2)),
        poly_multiply(linear, u, v),
        poly_multiply(constant, poly_power(v, 2)),
    )
    actual_affine = substitute_homogeneous_s3(
        (x1, one, x2, one, u, v)
    )
    if actual_affine != expected_affine:
        raise AssertionError("symbolic affine H coefficients failed")

    f1 = poly_add(poly_power(x1, 3), poly_constant(7))
    f2 = poly_add(poly_power(x2, 3), poly_constant(7))
    discriminant = poly_subtract(
        poly_power(linear, 2),
        poly_scale(poly_multiply(leading, constant), 4),
    )
    expected_discriminant = poly_scale(
        poly_multiply(f1, f2),
        16,
    )
    if discriminant != expected_discriminant:
        raise AssertionError("symbolic H discriminant failed")

    repeated = substitute_homogeneous_s3(
        (x1, one, x1, one, u, v)
    )
    expected_repeated = poly_multiply(
        v,
        poly_add(
            poly_scale(poly_multiply(f1, u), -4),
            poly_multiply(
                poly_subtract(
                    poly_power(x1, 4),
                    poly_scale(x1, 56),
                ),
                v,
            ),
        ),
    )
    if repeated != expected_repeated:
        raise AssertionError("symbolic repeated-input H formula failed")

    identity = substitute_homogeneous_s3(
        (one, zero, x1, x2, u, v)
    )
    expected_identity = poly_power(
        poly_subtract(
            poly_multiply(x1, v),
            poly_multiply(x2, u),
        ),
        2,
    )
    if identity != expected_identity:
        raise AssertionError("symbolic identity-input H formula failed")

    slope_denominator = poly_subtract(x2, x1)
    denominator_squared = poly_power(slope_denominator, 2)
    x_sum = poly_add(x1, x2)
    plus_numerator = poly_subtract(
        poly_power(poly_subtract(y2, y1), 2),
        poly_multiply(denominator_squared, x_sum),
    )
    minus_numerator = poly_subtract(
        poly_power(poly_add(y2, y1), 2),
        poly_multiply(denominator_squared, x_sum),
    )
    root_linear_identity = reduce_curve_relations(
        poly_subtract(
            poly_scale(
                poly_add(plus_numerator, minus_numerator),
                -1,
            ),
            linear,
        )
    )
    root_constant_identity = reduce_curve_relations(
        poly_subtract(
            poly_multiply(plus_numerator, minus_numerator),
            poly_multiply(denominator_squared, constant),
        )
    )
    if root_linear_identity or root_constant_identity:
        raise AssertionError(
            "symbolic distinct-point factorization failed"
        )

    two_torsion_coefficient = poly_subtract(
        poly_power(x1, 4),
        poly_scale(x1, 56),
    )
    doubling_numerator = poly_subtract(
        poly_scale(poly_power(x1, 4), 9),
        poly_scale(poly_multiply(x1, f1), 8),
    )
    if doubling_numerator != two_torsion_coefficient:
        raise AssertionError(
            "symbolic repeated root is not the doubling x-coordinate"
        )
    coefficient_mod_curve = poly_subtract(
        poly_multiply(x1, f1),
        poly_scale(x1, 63),
    )
    if two_torsion_coefficient != coefficient_mod_curve:
        raise AssertionError(
            "symbolic two-torsion double-root coefficient failed"
        )
    if 63 != 3**2 * 7:
        raise AssertionError("two-torsion coefficient factorization failed")
    two_torsion_nonzero_logic = {
        "x_nonzero": (
            "f(x)=0 and x=0 would force 7=0, excluded by char!=7"
        ),
        "coefficient": (
            "x^4-56*x=-63*x on f(x)=0"
        ),
        "coefficient_nonzero": (
            "-63*x is nonzero because x!=0 and char not in {3,7}"
        ),
    }

    curve_discriminant = -16 * 27 * 7**2
    if (
        abs(curve_discriminant) != 2**4 * 3**3 * 7**2
        or any(
            curve_discriminant % characteristic
            for characteristic in EXCLUDED_CHARACTERISTICS
        )
        or any(
            curve_discriminant % characteristic == 0
            for characteristic in (5, 11, 13)
        )
    ):
        raise AssertionError("curve characteristic domain failed")
    f7_singular = (
        curve_rhs(0, 7) == 0
        and (-3 * 0**2) % 7 == 0
        and (2 * 0) % 7 == 0
    )
    if not f7_singular:
        raise AssertionError("F7 singular witness disappeared")

    return {
        "affine_coefficients": "exact_integer_polynomial_identity",
        "distinct_discriminant": "exact_integer_polynomial_identity",
        "distinct_factorization": (
            "exact_mod_curve_relations_after_cross_multiplication"
        ),
        "repeated_specialization": (
            "exact_integer_polynomial_identity"
        ),
        "repeated_doubling_root": (
            "9*x^4-8*x*f(x)=x^4-56*x over denominator 4*f(x)"
        ),
        "identity_specialization": (
            "exact_integer_polynomial_identity"
        ),
        "two_torsion_specialization": (
            "nonzero_under_declared_characteristic_domain"
        ),
        "two_torsion_nonzero_logic": two_torsion_nonzero_logic,
        "excluded_characteristics": EXCLUDED_CHARACTERISTICS,
        "f7_singular_witness": [0, 0],
    }


def legendre(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    symbol = pow(residue, (prime - 1) // 2, prime)
    if symbol == 1:
        return 1
    if symbol == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned an invalid value")


def even_y_lifts(x: int, prime: int, a: int = 0, b: int = 7) -> list[Point]:
    rhs = (x**3 + a * x + b) % prime
    if rhs == 0:
        return [(x, 0)]
    if legendre(rhs, prime) != 1:
        return []
    # Both certificate fields are 3 mod 4.
    if prime % 4 != 3:
        raise AssertionError("unexpected square-root field")
    root = pow(rhs, (prime + 1) // 4, prime)
    roots = sorted({root, (-root) % prime})
    even = [value for value in roots if value % 2 == 0]
    if len(even) != 1:
        raise AssertionError("even-y lift is not unique")
    return [(x, even[0])]


def curve_rhs(x: int, prime: int, a: int = 0, b: int = 7) -> int:
    return (x**3 + a * x + b) % prime


def projective_record(value: Kummer) -> dict[str, Any]:
    x, z = value
    if x == 0 and z == 0:
        return {"X": 0, "Z": 0, "kind": "invalid"}
    if z == 0:
        return {"X": 1, "Z": 0, "kind": "identity"}
    return {"X": x, "Z": 1, "kind": "finite", "x": x}


def output_binary_coefficients(
    left: Kummer,
    right: Kummer,
    prime: int,
) -> tuple[int, int, int]:
    coefficient_u2 = s3_homogeneous(
        prime, left, right, (1, 0)
    )
    coefficient_v2 = s3_homogeneous(
        prime, left, right, (0, 1)
    )
    coefficient_uv = (
        s3_homogeneous(prime, left, right, (1, 1))
        - coefficient_u2
        - coefficient_v2
    ) % prime
    return coefficient_u2, coefficient_uv, coefficient_v2


def projective_roots(
    coefficients: tuple[int, int, int],
    prime: int,
) -> list[dict[str, Any]]:
    coefficient_u2, coefficient_uv, coefficient_v2 = coefficients
    roots: list[dict[str, Any]] = []
    for value in range(prime):
        if (
            coefficient_u2 * value * value
            + coefficient_uv * value
            + coefficient_v2
        ) % prime:
            continue
        derivative = (
            2 * coefficient_u2 * value + coefficient_uv
        ) % prime
        roots.append(
            {
                "coordinate": projective_record((value, 1)),
                "multiplicity": 2 if derivative == 0 else 1,
            }
        )
    if coefficient_u2 == 0:
        roots.append(
            {
                "coordinate": projective_record((1, 0)),
                "multiplicity": 2 if coefficient_uv == 0 else 1,
            }
        )
    return roots


def small_leaf_type(value: Kummer, prime: int) -> str:
    if value == (0, 0):
        return "invalid_projective"
    if value[1] == 0:
        return "identity"
    symbol = legendre(curve_rhs(value[0], prime), prime)
    if symbol == 1:
        return "finite_base_pair"
    if symbol == -1:
        return "finite_extension_pair"
    return "finite_rational_two_torsion"


def small_transition_type(
    left: Kummer,
    right: Kummer,
    prime: int,
) -> str:
    if left == (0, 0) or right == (0, 0):
        return "invalid_projective_input"
    if left[1] == 0 or right[1] == 0:
        return "identity_input_duplicate"
    x1 = left[0]
    x2 = right[0]
    if x1 == x2:
        if curve_rhs(x1, prime) == 0:
            return "repeated_two_torsion_duplicate"
        return "repeated_tangent"
    product = curve_rhs(x1, prime) * curve_rhs(x2, prime)
    symbol = legendre(product, prime)
    if symbol == 0:
        return "distinct_two_torsion_duplicate"
    if symbol == 1:
        return "distinct_rational_split"
    return "distinct_extension_only"


def named_small_transition(
    prime: int,
    left: Kummer,
    right: Kummer,
) -> dict[str, Any]:
    coefficients = output_binary_coefficients(left, right, prime)
    return {
        "input": [
            projective_record(left),
            projective_record(right),
        ],
        "type": small_transition_type(left, right, prime),
        "output_binary_coefficients_U2_UV_V2": list(coefficients),
        "fp_roots": projective_roots(coefficients, prime),
    }


@cache
def replay_small_field(prime: int) -> dict[str, Any]:
    if prime not in {11, 13} or not exact_prime_check(prime):
        raise AssertionError("unsupported small replay field")
    coordinates = [(1, 0), *[(value, 1) for value in range(prime)]]
    leaf_records = [
        {
            "coordinate": projective_record(value),
            "rhs": (
                None
                if value[1] == 0
                else curve_rhs(value[0], prime)
            ),
            "type": small_leaf_type(value, prime),
        }
        for value in coordinates
    ]
    transition_records: list[dict[str, Any]] = []
    type_counts: Counter[str] = Counter()
    root_profile: Counter[str] = Counter()
    for left in coordinates:
        for right in coordinates:
            kind = small_transition_type(left, right, prime)
            coefficients = output_binary_coefficients(
                left, right, prime
            )
            roots = projective_roots(coefficients, prime)
            type_counts[kind] += 1
            root_profile[
                f"{len(roots)}_fp_roots_"
                f"{sum(root['multiplicity'] for root in roots)}_multiplicity"
            ] += 1
            transition_records.append(
                {
                    "left": projective_record(left),
                    "right": projective_record(right),
                    "type": kind,
                    "coefficients": list(coefficients),
                    "roots": roots,
                }
            )

            if left[1] == 0 or right[1] == 0:
                other = right if left[1] == 0 else left
                expected_roots = [
                    {
                        "coordinate": projective_record(other),
                        "multiplicity": 2,
                    }
                ]
                if roots != expected_roots:
                    raise AssertionError(
                        "identity transition lost its double root"
                    )
            elif left[0] == right[0]:
                x = left[0]
                for output in coordinates:
                    u, v = output
                    expected = (
                        v
                        * (
                            -4 * curve_rhs(x, prime) * u
                            + (x**4 - 56 * x) * v
                        )
                    ) % prime
                    if (
                        s3_homogeneous(
                            prime, left, right, output
                        )
                        != expected
                    ):
                        raise AssertionError(
                            "repeated-input projective formula failed"
                        )
            else:
                discriminant = (
                    coefficients[1] ** 2
                    - 4 * coefficients[0] * coefficients[2]
                ) % prime
                expected_discriminant = (
                    16
                    * curve_rhs(left[0], prime)
                    * curve_rhs(right[0], prime)
                ) % prime
                if discriminant != expected_discriminant:
                    raise AssertionError(
                        "distinct-input discriminant formula failed"
                    )

            for output in coordinates:
                if left[1] == 0:
                    expected = (
                        right[0] * output[1]
                        - right[1] * output[0]
                    ) ** 2 % prime
                    if (
                        s3_homogeneous(
                            prime, left, right, output
                        )
                        != expected
                    ):
                        raise AssertionError(
                            "left identity formula failed"
                        )
                if right[1] == 0:
                    expected = (
                        left[0] * output[1]
                        - left[1] * output[0]
                    ) ** 2 % prime
                    if (
                        s3_homogeneous(
                            prime, left, right, output
                        )
                        != expected
                    ):
                        raise AssertionError(
                            "right identity formula failed"
                        )

    if prime == 13:
        examples = {
            "base_base_split": named_small_transition(
                prime, (7, 1), (8, 1)
            ),
            "twist_twist_split": named_small_transition(
                prime, (1, 1), (2, 1)
            ),
            "base_twist_extension_only": named_small_transition(
                prime, (7, 1), (1, 1)
            ),
            "base_repeated_tangent": named_small_transition(
                prime, (7, 1), (7, 1)
            ),
            "twist_repeated_tangent": named_small_transition(
                prime, (1, 1), (1, 1)
            ),
            "identity_input": named_small_transition(
                prime, (1, 0), (7, 1)
            ),
        }
    else:
        examples = {
            "repeated_two_torsion": named_small_transition(
                prime, (5, 1), (5, 1)
            ),
            "two_torsion_with_base_point": named_small_transition(
                prime, (5, 1), (2, 1)
            ),
            "two_torsion_with_twist_point": named_small_transition(
                prime, (5, 1), (1, 1)
            ),
            "ordinary_split": named_small_transition(
                prime, (2, 1), (3, 1)
            ),
            "ordinary_extension_only": named_small_transition(
                prime, (2, 1), (8, 1)
            ),
            "identity_identity": named_small_transition(
                prime, (1, 0), (1, 0)
            ),
        }
    return {
        "field": f"F_{prime}",
        "p": prime,
        "field_scope": (
            "char(F_p) not in {2,3,7}; curve discriminant is nonzero"
        ),
        "curve": f"y^2 = x^3 + 7 over F_{prime}",
        "curve_discriminant_nonzero": (
            -16 * 27 * 7**2
        )
        % prime
        != 0,
        "projective_coordinate_count": prime + 1,
        "leaf_type_counts": dict(
            sorted(
                Counter(
                    record["type"] for record in leaf_records
                ).items()
            )
        ),
        "leaf_records_sha256": digest(leaf_records),
        "ordered_transition_count": len(transition_records),
        "transition_type_counts": dict(sorted(type_counts.items())),
        "fp_root_profile": dict(sorted(root_profile.items())),
        "transition_records_sha256": digest(transition_records),
        "named_examples": examples,
        "checks": {
            "all_valid_input_pairs_classified_once": True,
            "identity_formula_all_coordinates": True,
            "repeated_formula_all_coordinates": True,
            "distinct_discriminant_formula_all_pairs": True,
            "root_multiplicity_replayed": True,
        },
    }


def canonical_scalar(value: int) -> int:
    residue = value % CONTROL_N
    return min(residue, (-residue) % CONTROL_N)


def sign_from_mask(mask: int, position: int) -> int:
    if position == 0:
        return 1
    return 1 if mask & (1 << (position - 1)) else -1


def transition_kind(left: Point, right: Point, parent: Point) -> str:
    if left is None and right is None:
        return "two_identity"
    if left is None or right is None:
        return "one_identity"
    if left == right:
        if parent is None:
            return "two_torsion_identity"
        return "tangent"
    if left == negate(right, CONTROL_P):
        return "opposite_identity"
    return "distinct_chord"


@cache
def replay_control_preimages() -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    per_rank: list[dict[str, int]] = []
    topology_fibers: dict[
        tuple[tuple[int, ...], tuple[int, ...]], int
    ] = {}
    affine_fibers: set[
        tuple[tuple[int, ...], tuple[int, ...]]
    ] = set()
    signed_multisets: Counter[tuple[tuple[int, int], ...]] = Counter()
    raw_aggregates: Counter[tuple[int, int]] = Counter()
    normalized_aggregates: Counter[tuple[int, int]] = Counter()

    for rank, repeated_positions in enumerate(
        itertools.combinations(range(M), 2)
    ):
        scalars = [1] * M
        for position in repeated_positions:
            scalars[position] = 50

        right_masks: dict[int, list[int]] = {}
        for right_mask in range(1 << 8):
            value = sum(
                (
                    1 if right_mask & (1 << offset) else -1
                )
                * scalars[8 + offset]
                for offset in range(8)
            )
            right_masks.setdefault(value, []).append(right_mask)

        rank_records: list[dict[str, Any]] = []
        for left_mask in range(1 << 7):
            left_value = scalars[0] + sum(
                (
                    1 if left_mask & (1 << offset) else -1
                )
                * scalars[1 + offset]
                for offset in range(7)
            )
            for sigma in (-1, 1):
                needed = sigma * 14 - left_value
                for right_mask in right_masks.get(needed, []):
                    mask = left_mask | (right_mask << 7)
                    signs = [
                        sign_from_mask(mask, position)
                        for position in range(M)
                    ]
                    running = 0
                    prefix_classes: list[int] = []
                    identity_prefixes: list[int] = []
                    for index, (scalar, sign) in enumerate(
                        zip(scalars, signs, strict=True), 1
                    ):
                        running = (
                            running + scalar * sign
                        ) % CONTROL_N
                        if 2 <= index <= 15:
                            cls = canonical_scalar(running)
                            prefix_classes.append(cls)
                            if cls == 0:
                                identity_prefixes.append(index)

                    raw_coeff_base = sum(
                        sign
                        for scalar, sign in zip(
                            scalars, signs, strict=True
                        )
                        if scalar == 1
                    )
                    raw_coeff_repeated = sum(
                        sign
                        for scalar, sign in zip(
                            scalars, signs, strict=True
                        )
                        if scalar == 50
                    )
                    normalized = (
                        sigma * raw_coeff_base,
                        sigma * raw_coeff_repeated,
                    )

                    signed_key = tuple(
                        sorted(
                            Counter(
                                scalar * sign
                                for scalar, sign in zip(
                                    scalars, signs, strict=True
                                )
                            ).items()
                        )
                    )
                    signed_multisets[signed_key] += 1
                    raw_aggregates[
                        (raw_coeff_base, raw_coeff_repeated)
                    ] += 1
                    normalized_aggregates[normalized] += 1

                    fiber_key = (
                        tuple(scalars),
                        tuple(prefix_classes),
                    )
                    topology_fibers[fiber_key] = (
                        topology_fibers.get(fiber_key, 0) + 1
                    )
                    if not identity_prefixes:
                        affine_fibers.add(fiber_key)

                    signed_points = [
                        multiply(
                            scalar * sign,
                            CONTROL_BASE,
                            CONTROL_P,
                        )
                        for scalar, sign in zip(
                            scalars, signs, strict=True
                        )
                    ]
                    raw_check = add(
                        point_sum(signed_points, CONTROL_P),
                        multiply(
                            -sigma,
                            CONTROL_TARGET,
                            CONTROL_P,
                        ),
                        CONTROL_P,
                    )
                    if raw_check is not None:
                        raise AssertionError(
                            "control raw relation check failed"
                        )

                    record = {
                        "identity_prefix_sizes": identity_prefixes,
                        "normalized_coefficients": list(normalized),
                        "permutation_rank": rank,
                        "prefix_scalar_classes": prefix_classes,
                        "repeated_positions_zero_based": list(
                            repeated_positions
                        ),
                        "sign_mask_tail_15": mask,
                        "target_orientation_sigma": sigma,
                    }
                    rank_records.append(record)
                    records.append(record)

        per_rank.append(
            {
                "affine_preimages": sum(
                    not item["identity_prefix_sizes"]
                    for item in rank_records
                ),
                "direct_preimages": len(rank_records),
                "identity_preimages": sum(
                    bool(item["identity_prefix_sizes"])
                    for item in rank_records
                ),
                "permutation_rank": rank,
                "projective_topology_fibers": len(
                    {
                        tuple(item["prefix_scalar_classes"])
                        for item in rank_records
                    }
                ),
            }
        )

    records.sort(
        key=lambda item: (
            item["permutation_rank"],
            item["sign_mask_tail_15"],
            item["target_orientation_sigma"],
        )
    )
    identity_records = [
        item for item in records if item["identity_prefix_sizes"]
    ]
    affine_records = [
        item for item in records if not item["identity_prefix_sizes"]
    ]
    identity_fibers = [
        key
        for key in topology_fibers
        if 0 in key[1]
    ]

    expected_row = {
        "factor_coefficients": {
            "base_P": 14,
            "repeated_50P": 0,
        },
        "target_coefficient_mod_order": CONTROL_N - 1,
    }
    compressed_check = add(
        multiply(14, CONTROL_BASE, CONTROL_P),
        negate(CONTROL_TARGET, CONTROL_P),
        CONTROL_P,
    )
    if compressed_check is not None:
        raise AssertionError("control compressed relation failed")

    return {
        "affine_preimages": len(affine_records),
        "affine_topology_fibers": len(affine_fibers),
        "coordinate_multisets": 1,
        "direct_preimages": len(records),
        "identity_preimages": len(identity_records),
        "identity_topology_fibers": len(identity_fibers),
        "normalized_duplicate_aggregates": len(normalized_aggregates),
        "normalized_row": expected_row,
        "normalized_rows": len(normalized_aggregates),
        "ordered_coordinate_tuples": len(per_rank),
        "per_rank_sha256": digest(per_rank),
        "projective_topology_fibers": len(topology_fibers),
        "raw_duplicate_aggregates": len(raw_aggregates),
        "record_sha256": digest(records),
        "signed_point_multisets": len(signed_multisets),
        "signed_point_multiset_counts": sorted(
            signed_multisets.values()
        ),
        "topology_fiber_multiplicities": sorted(
            Counter(topology_fibers.values()).items()
        ),
    }


@cache
def replay_identity_dp() -> dict[str, Any]:
    required: dict[int, Kummer] = {2: (1, 0)}
    for prefix_size in range(3, 16):
        point = multiply(
            prefix_size - 2,
            CONTROL_BASE,
            CONTROL_P,
        )
        required[prefix_size] = kummer(point)
    required[16] = kummer(CONTROL_TARGET)

    states: dict[Point, set[int]] = {CONTROL_REPEATED: {0}}
    layers = [
        {
            "incoming_edge_count": 0,
            "prefix_size": 1,
            "preimage_count": 1,
            "required_kummer": None,
            "state_count": 1,
            "state_points": [point_record(CONTROL_REPEATED)],
        }
    ]
    all_edges: list[dict[str, Any]] = []

    leaves = [CONTROL_REPEATED] + [CONTROL_BASE] * 14
    for prefix_size, leaf in enumerate(leaves, 2):
        next_states: dict[Point, set[int]] = {}
        edges: list[dict[str, Any]] = []
        for prior, masks in states.items():
            for sign in (-1, 1):
                signed_leaf = (
                    leaf
                    if sign == 1
                    else negate(leaf, CONTROL_P)
                )
                parent = add(prior, signed_leaf, CONTROL_P)
                if s3_homogeneous(
                    CONTROL_P,
                    kummer(prior),
                    kummer(signed_leaf),
                    kummer(parent),
                ) != 0:
                    raise AssertionError(
                        "projective S3 transition did not vanish"
                    )
                if kummer(parent) != required[prefix_size]:
                    continue
                for mask in masks:
                    next_mask = mask
                    if sign == 1:
                        next_mask |= 1 << (prefix_size - 2)
                    next_states.setdefault(parent, set()).add(
                        next_mask
                    )
                edge = {
                    "leaf_sign": sign,
                    "parent": point_record(parent),
                    "preimage_count": len(masks),
                    "prior": point_record(prior),
                    "transition_kind": transition_kind(
                        prior, signed_leaf, parent
                    ),
                }
                edges.append(edge)
                all_edges.append(
                    {"prefix_size": prefix_size, **edge}
                )
        states = next_states
        masks = sorted(
            set().union(*states.values()) if states else set()
        )
        layers.append(
            {
                "incoming_edge_count": len(edges),
                "prefix_size": prefix_size,
                "preimage_count": len(masks),
                "required_kummer": kummer_record(
                    required[prefix_size]
                ),
                "sign_mask_sha256": digest(masks),
                "state_count": len(states),
                "state_points": sorted(
                    (point_record(point) for point in states),
                    key=lambda item: canonical_bytes(item),
                ),
            }
        )

    accepted: list[dict[str, int]] = []
    for point, masks in states.items():
        if point == CONTROL_TARGET:
            sigma = 1
        elif point == negate(CONTROL_TARGET, CONTROL_P):
            sigma = -1
        else:
            raise AssertionError("DP root is not the target orbit")
        accepted.extend(
            {
                "sign_mask_tail_15": mask,
                "target_orientation_sigma": sigma,
            }
            for mask in masks
        )
    accepted.sort(
        key=lambda item: (
            item["sign_mask_tail_15"],
            item["target_orientation_sigma"],
        )
    )

    return {
        "accepted_preimages": accepted,
        "accepted_preimages_sha256": digest(accepted),
        "affine_preimages": 0,
        "backpointer_edges_sha256": digest(all_edges),
        "layer_sha256": digest(layers),
        "layers": layers,
        "projective_preimages": len(accepted),
        "supplied_u": [
            {
                "kummer": kummer_record(required[prefix_size]),
                "prefix_size": prefix_size,
            }
            for prefix_size in range(2, 16)
        ],
    }


def control_token(scalar: int) -> str | int:
    point = multiply(
        scalar % CONTROL_N,
        CONTROL_BASE,
        CONTROL_P,
    )
    return "O" if point is None else point[0]


def control_token_record(token: str | int) -> dict[str, Any]:
    if token == "O":
        return projective_record((1, 0))
    if not isinstance(token, int):
        raise AssertionError("invalid finite control token")
    return projective_record((token, 1))


def enumerate_control_records() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    orders: list[dict[str, Any]] = []
    preimages: list[dict[str, Any]] = []
    for order_index, repeated_positions in enumerate(
        itertools.combinations(range(M), 2)
    ):
        scalars = [1] * M
        for position in repeated_positions:
            scalars[position] = 50
        orders.append(
            {
                "ordering_index": order_index,
                "repeated_positions_zero_based": list(
                    repeated_positions
                ),
                "leaf_scalars_on_P": scalars,
            }
        )

        right_sums: dict[int, list[int]] = defaultdict(list)
        for mask in range(1 << 8):
            total = sum(
                (1 if mask & (1 << offset) else -1)
                * scalars[8 + offset]
                for offset in range(8)
            )
            right_sums[total].append(mask)

        for left_mask in range(1 << 7):
            left_total = scalars[0] + sum(
                (1 if left_mask & (1 << offset) else -1)
                * scalars[1 + offset]
                for offset in range(7)
            )
            for orientation in (-1, 1):
                for right_mask in right_sums.get(
                    orientation * 14 - left_total, []
                ):
                    mask = left_mask | (right_mask << 7)
                    signs = [
                        sign_from_mask(mask, position)
                        for position in range(M)
                    ]
                    prefix = 0
                    tokens: list[str | int] = []
                    identity_sizes: list[int] = []
                    for prefix_size, (scalar, sign) in enumerate(
                        zip(scalars, signs, strict=True), 1
                    ):
                        prefix = (
                            prefix + scalar * sign
                        ) % CONTROL_N
                        if 2 <= prefix_size <= 15:
                            token = control_token(prefix)
                            tokens.append(token)
                            if token == "O":
                                identity_sizes.append(prefix_size)
                    preimages.append(
                        {
                            "identity_prefix_sizes": identity_sizes,
                            "internal_tokens": tokens,
                            "ordering_index": order_index,
                            "repeated_positions_zero_based": list(
                                repeated_positions
                            ),
                            "sign_mask_tail_15": mask,
                            "target_orientation": orientation,
                        }
                    )
    preimages.sort(
        key=lambda item: (
            item["ordering_index"],
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    return orders, preimages


def replay_supplied_tokens(
    scalars: list[int],
    tokens: list[str | int],
) -> dict[str, Any]:
    states: dict[int, list[int]] = {
        scalars[0] % CONTROL_N: [0]
    }
    layers: list[dict[str, Any]] = [
        {
            "after_leaf_count": 1,
            "backpointer_path_count": 1,
            "state_scalars": sorted(states),
        }
    ]
    edges: list[dict[str, Any]] = []
    for leaf_index in range(1, M - 1):
        next_states: dict[int, list[int]] = defaultdict(list)
        for parent_scalar in sorted(states):
            for parent_mask in sorted(states[parent_scalar]):
                for sign in (-1, 1):
                    child_scalar = (
                        parent_scalar + sign * scalars[leaf_index]
                    ) % CONTROL_N
                    if control_token(child_scalar) != tokens[
                        leaf_index - 1
                    ]:
                        continue
                    child_mask = parent_mask
                    if sign == 1:
                        child_mask |= 1 << (leaf_index - 1)
                    next_states[child_scalar].append(child_mask)
                    edges.append(
                        {
                            "child_scalar": child_scalar,
                            "leaf_index_zero_based": leaf_index,
                            "parent_mask": parent_mask,
                            "parent_scalar": parent_scalar,
                            "sign": sign,
                            "tail_mask": child_mask,
                        }
                    )
        states = {
            scalar: sorted(masks)
            for scalar, masks in sorted(next_states.items())
        }
        layers.append(
            {
                "after_leaf_count": leaf_index + 1,
                "backpointer_path_count": sum(
                    len(masks) for masks in states.values()
                ),
                "state_scalars": sorted(states),
            }
        )

    accepted: list[dict[str, int]] = []
    last_index = M - 1
    for parent_scalar in sorted(states):
        for parent_mask in sorted(states[parent_scalar]):
            for sign in (-1, 1):
                child_scalar = (
                    parent_scalar + sign * scalars[last_index]
                ) % CONTROL_N
                if child_scalar not in {14, CONTROL_N - 14}:
                    continue
                child_mask = parent_mask
                if sign == 1:
                    child_mask |= 1 << (last_index - 1)
                orientation = 1 if child_scalar == 14 else -1
                accepted.append(
                    {
                        "sign_mask_tail_15": child_mask,
                        "target_orientation": orientation,
                        "terminal_scalar": child_scalar,
                    }
                )
                edges.append(
                    {
                        "child_scalar": child_scalar,
                        "leaf_index_zero_based": last_index,
                        "parent_mask": parent_mask,
                        "parent_scalar": parent_scalar,
                        "sign": sign,
                        "tail_mask": child_mask,
                    }
                )
    accepted.sort(
        key=lambda item: (
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    return {
        "accepted": accepted,
        "backpointer_edges": edges,
        "layers": layers,
    }


@cache
def replay_control_certificate() -> dict[str, Any]:
    if (
        2 * 3 * 7 * 13_441 != D
        or CONTROL_P != D + 1
        or not exact_prime_check(CONTROL_P)
        or multiply(CONTROL_COFACTOR, CONTROL_SEED, CONTROL_P)
        != CONTROL_BASE
        or multiply(CONTROL_N, CONTROL_BASE, CONTROL_P)
        is not None
    ):
        raise AssertionError("control field or subgroup contract failed")
    if not all(
        on_curve(point, CONTROL_P)
        for point in (
            CONTROL_SEED,
            CONTROL_BASE,
            CONTROL_REPEATED,
            CONTROL_TARGET,
        )
    ):
        raise AssertionError("control point is off curve")
    if multiply(50, CONTROL_BASE, CONTROL_P) != CONTROL_REPEATED:
        raise AssertionError("control repeated point changed")
    if multiply(14, CONTROL_BASE, CONTROL_P) != CONTROL_TARGET:
        raise AssertionError("control target changed")
    if any(
        point[0] == 0 or pow(point[0], D, CONTROL_P) != 1
        for point in (
            CONTROL_BASE,
            CONTROL_REPEATED,
            CONTROL_TARGET,
        )
    ):
        raise AssertionError("control coordinate left the factor base")
    curve_order = 1
    rational_two_torsion: list[int] = []
    for x in range(CONTROL_P):
        rhs = curve_rhs(x, CONTROL_P)
        symbol = legendre(rhs, CONTROL_P)
        curve_order += 1 + symbol
        if symbol == 0:
            rational_two_torsion.append(x)
    if (
        curve_order != CONTROL_CURVE_ORDER
        or rational_two_torsion
        or CONTROL_COFACTOR * CONTROL_N != curve_order
        or not exact_prime_check(CONTROL_COFACTOR)
        or not exact_prime_check(CONTROL_N)
    ):
        raise AssertionError("control curve order contract failed")

    orders, preimages = enumerate_control_records()
    order_index = {
        record["ordering_index"]: record for record in orders
    }
    fibers: dict[
        tuple[int, tuple[str | int, ...]],
        list[dict[str, Any]],
    ] = defaultdict(list)
    for record in preimages:
        fibers[
            (
                record["ordering_index"],
                tuple(record["internal_tokens"]),
            )
        ].append(record)

    summaries: list[dict[str, Any]] = []
    all_edges: list[dict[str, Any]] = []
    accepted_records: list[dict[str, int]] = []
    identity_full: dict[str, Any] | None = None
    exact_checks = 0
    ordered_fibers = sorted(
        fibers.items(),
        key=lambda item: (
            item[0][0],
            tuple(str(token) for token in item[0][1]),
        ),
    )
    for fiber_index, (fiber_key, source_records) in enumerate(
        ordered_fibers
    ):
        current_order_index, token_tuple = fiber_key
        order = order_index[current_order_index]
        recovered = replay_supplied_tokens(
            order["leaf_scalars_on_P"],
            list(token_tuple),
        )
        expected_accepted = sorted(
            (
                {
                    "sign_mask_tail_15": record[
                        "sign_mask_tail_15"
                    ],
                    "target_orientation": record[
                        "target_orientation"
                    ],
                    "terminal_scalar": (
                        14
                        if record["target_orientation"] == 1
                        else CONTROL_N - 14
                    ),
                }
                for record in source_records
            ),
            key=lambda item: (
                item["sign_mask_tail_15"],
                item["target_orientation"],
            ),
        )
        if recovered["accepted"] != expected_accepted:
            raise AssertionError("supplied-u recovery mismatch")

        identity_sizes = sorted(
            {
                size
                for record in source_records
                for size in record["identity_prefix_sizes"]
            }
        )
        for edge in recovered["backpointer_edges"]:
            all_edges.append({"fiber_index": fiber_index, **edge})
        for accepted in recovered["accepted"]:
            accepted_records.append(
                {
                    "ordering_index": current_order_index,
                    "sign_mask_tail_15": accepted[
                        "sign_mask_tail_15"
                    ],
                    "target_orientation": accepted[
                        "target_orientation"
                    ],
                }
            )

        scalars = order["leaf_scalars_on_P"]
        for source in source_records:
            signs = [
                sign_from_mask(
                    source["sign_mask_tail_15"], position
                )
                for position in range(M)
            ]
            raw_points = [
                multiply(sign * scalar, CONTROL_BASE, CONTROL_P)
                for sign, scalar in zip(
                    signs, scalars, strict=True
                )
            ]
            raw = point_sum(raw_points, CONTROL_P)
            orientation = source["target_orientation"]
            expected_target = (
                CONTROL_TARGET
                if orientation == 1
                else negate(CONTROL_TARGET, CONTROL_P)
            )
            normalized = point_sum(
                [
                    multiply(
                        orientation * sign * scalar,
                        CONTROL_BASE,
                        CONTROL_P,
                    )
                    for sign, scalar in zip(
                        signs, scalars, strict=True
                    )
                ],
                CONTROL_P,
            )
            if raw != expected_target or normalized != CONTROL_TARGET:
                raise AssertionError(
                    "control raw or normalized group check failed"
                )
            exact_checks += 1

        summary = {
            "accepted_masks": [
                item["sign_mask_tail_15"]
                for item in recovered["accepted"]
            ],
            "affine_admissible": not identity_sizes,
            "backpointer_edge_count": len(
                recovered["backpointer_edges"]
            ),
            "fiber_index": fiber_index,
            "identity_prefix_sizes": identity_sizes,
            "internal_coordinates_sha256": digest(
                [
                    control_token_record(token)
                    for token in token_tuple
                ]
            ),
            "layer_backpointer_path_counts": [
                layer["backpointer_path_count"]
                for layer in recovered["layers"]
            ],
            "layer_state_widths": [
                len(layer["state_scalars"])
                for layer in recovered["layers"]
            ],
            "ordering_index": current_order_index,
            "preimage_count": len(source_records),
            "target_orientations": [
                item["target_orientation"]
                for item in recovered["accepted"]
            ],
        }
        summaries.append(summary)
        if identity_sizes:
            if identity_full is not None:
                raise AssertionError("more than one identity fiber")
            identity_full = {
                **summary,
                "backpointer_edges": recovered[
                    "backpointer_edges"
                ],
                "internal_coordinates": [
                    control_token_record(token)
                    for token in token_tuple
                ],
                "layers": recovered["layers"],
                "repeated_positions_zero_based": order[
                    "repeated_positions_zero_based"
                ],
            }

    accepted_records.sort(
        key=lambda item: (
            item["ordering_index"],
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    if identity_full is None:
        raise AssertionError("identity fiber is missing")
    affine_count = sum(
        summary["affine_admissible"] for summary in summaries
    )
    identity_count = sum(
        bool(summary["identity_prefix_sizes"])
        for summary in summaries
    )
    profile = Counter(
        summary["preimage_count"] for summary in summaries
    )

    direct = replay_control_preimages()
    if (
        len(orders) != 120
        or len(preimages) != 240
        or len(fibers) != 239
        or affine_count != 238
        or identity_count != 1
        or identity_full["accepted_masks"] != [0, 32_766]
        or identity_full["identity_prefix_sizes"] != [2]
        or profile != Counter({1: 238, 2: 1})
        or len(all_edges) != 3_599
        or exact_checks != 240
        or direct["projective_topology_fibers"] != len(fibers)
        or direct["affine_topology_fibers"] != affine_count
        or direct["identity_preimages"]
        != identity_full["preimage_count"]
        or direct["signed_point_multisets"] != 2
        or direct["raw_duplicate_aggregates"] != 2
        or direct["normalized_duplicate_aggregates"] != 1
        or direct["normalized_rows"] != 1
        or direct["signed_point_multiset_counts"] != [15, 225]
    ):
        raise AssertionError("control fiber accounting failed")

    normalized_rows: set[tuple[int, int, int]] = set()
    for record in preimages:
        order = order_index[record["ordering_index"]]
        repeated_positions = set(
            order["repeated_positions_zero_based"]
        )
        signs = [
            sign_from_mask(record["sign_mask_tail_15"], position)
            for position in range(M)
        ]
        orientation = record["target_orientation"]
        normalized_rows.add(
            (
                orientation
                * sum(
                    signs[position]
                    for position in range(M)
                    if position not in repeated_positions
                )
                % CONTROL_N,
                orientation
                * sum(
                    signs[position]
                    for position in repeated_positions
                )
                % CONTROL_N,
                CONTROL_N - 1,
            )
        )
    if normalized_rows != {(14, 0, CONTROL_N - 1)}:
        raise AssertionError("control normalized row is not unique")
    compressed = add(
        multiply(14, CONTROL_BASE, CONTROL_P),
        negate(CONTROL_TARGET, CONTROL_P),
        CONTROL_P,
    )
    if compressed is not None:
        raise AssertionError("control compressed row failed")

    return {
        "field": {
            "p": CONTROL_P,
            "D": D,
            "factor_chain": [2, 3, 7, 13_441],
            "p_minus_one_equals_D": True,
            "curve": "y^2 = x^3 + 7",
            "curve_order": curve_order,
            "curve_order_factors": [
                CONTROL_COFACTOR,
                CONTROL_N,
            ],
            "rational_two_torsion_x": rational_two_torsion,
        },
        "subgroup": {
            "order": CONTROL_N,
            "cofactor": CONTROL_COFACTOR,
            "seed": point_record(CONTROL_SEED),
            "P": point_record(CONTROL_BASE),
            "repeated_50P": point_record(CONTROL_REPEATED),
            "target_R_14P": point_record(CONTROL_TARGET),
            "order_check": "[3463]P = O",
        },
        "coordinate_multiset": [
            {
                "basis": "P",
                "multiplicity": 14,
                "scalar_on_P": 1,
                "x": CONTROL_BASE[0],
            },
            {
                "basis": "50P",
                "multiplicity": 2,
                "scalar_on_P": 50,
                "x": CONTROL_REPEATED[0],
            },
        ],
        "ordered_topologies": {
            "unique_orders": len(orders),
            "definition": (
                "lexicographic choices of the two zero-based positions "
                "occupied by 50P"
            ),
            "records_sha256": digest(orders),
            "first": orders[0],
            "last": orders[-1],
        },
        "supplied_internal_dp": {
            "first_leaf_sign_normalization": "+1",
            "leaf_state_rule": (
                "start at the positive lift of leaf 1; for each later "
                "leaf try both lifts"
            ),
            "supplied_coordinate_rule": (
                "after leaves 2 through 15 retain a point state exactly "
                "when its Kummer coordinate equals the supplied [U_i:V_i]"
            ),
            "identity_state_rule": (
                "retain O as [1:0] in projective mode"
            ),
            "terminal_rule": (
                "accept exactly R or -R after leaf 16"
            ),
            "all_projective_fibers_replayed": True,
            "backpointer_edge_count": len(all_edges),
            "backpointer_edges_sha256": digest(all_edges),
            "fiber_summaries_sha256": digest(summaries),
            "accepted_terminal_records_sha256": digest(
                accepted_records
            ),
            "ordinary_layer_state_widths": [1] * 15,
            "ordinary_backpointer_edges_per_fiber": 15,
            "identity_fiber": identity_full,
        },
        "fiber_accounting": {
            "unique_orders": len(orders),
            "normalized_preimages": len(preimages),
            "preimage_records_sha256": digest(preimages),
            "projective_fibers": len(fibers),
            "affine_fibers": affine_count,
            "identity_fibers": identity_count,
            "identity_fiber_masks": identity_full[
                "accepted_masks"
            ],
            "fiber_preimage_multiplicity_profile": {
                str(key): value
                for key, value in sorted(profile.items())
            },
        },
        "normalized_row": {
            "basis_coefficients_mod_3463": {
                "P": 14,
                "50P": 0,
            },
            "target": "R",
            "target_coefficient_mod_3463": CONTROL_N - 1,
            "display": "14P - R = O",
            "preimage_count": len(preimages),
            "duplicate_aggregation": (
                "the two 50P coefficients sum to zero"
            ),
        },
        "exact_group_checks": {
            "all_240_raw_leaf_sums_equal_oriented_target": True,
            "all_240_target_normalized_leaf_sums_equal_R": True,
            "normalized_row_sum": point_record(compressed),
        },
        "hashes": {
            "fiber_summaries": digest(summaries),
            "backpointer_edges": digest(all_edges),
            "normalized_row": digest(
                {"P": 14, "50P": 0, "R": CONTROL_N - 1}
            ),
        },
    }


@cache
def replay_glv() -> dict[str, Any]:
    root = pow(8, (SECP_P + 1) // 4, SECP_P)
    if root * root % SECP_P != 8:
        raise AssertionError("x=1 has no secp256k1 lift")
    y = root if root % 2 == 0 else SECP_P - root
    if y != SECP_SOURCE_Y:
        raise AssertionError("the even-y source lift changed")
    point = (1, y)
    beta2 = SECP_BETA * SECP_BETA % SECP_P
    phi = (SECP_BETA, y)
    phi2 = (beta2, y)
    lambda2 = SECP_LAMBDA * SECP_LAMBDA % SECP_N
    if (
        not all(on_curve(item, SECP_P) for item in (point, phi, phi2))
        or len({point, phi, phi2}) != 3
        or pow(SECP_BETA, 3, SECP_P) != 1
        or SECP_BETA == 1
        or (beta2 + SECP_BETA + 1) % SECP_P != 0
        or pow(SECP_LAMBDA, 3, SECP_N) != 1
        or SECP_LAMBDA == 1
        or (lambda2 + SECP_LAMBDA + 1) % SECP_N != 0
    ):
        raise AssertionError("GLV field orbit contract failed")
    if (
        multiply(SECP_N, point, SECP_P) is not None
        or multiply(SECP_LAMBDA, point, SECP_P) != phi
        or multiply(lambda2, point, SECP_P) != phi2
    ):
        raise AssertionError("GLV subgroup transport failed")
    orbit_sum = point_sum((point, phi, phi2), SECP_P)
    signed_orbit = {
        point,
        phi,
        phi2,
        negate(point, SECP_P),
        negate(phi, SECP_P),
        negate(phi2, SECP_P),
    }
    if orbit_sum is not None or len(signed_orbit) != 6:
        raise AssertionError("GLV orbit cardinality or sum failed")

    leaves: list[dict[str, Any]] = []
    selected_points: list[Point] = []
    for index in range(14):
        epsilon = 1 if index < 7 else -1
        leaves.append(
            {
                "epsilon": epsilon,
                "index_one_based": index + 1,
                "point": "P0",
                "x": 1,
            }
        )
        selected_points.append(multiply(epsilon, point, SECP_P))
    for label, orbit_point in (
        ("phi(P0)", phi),
        ("phi^2(P0)", phi2),
    ):
        leaves.append(
            {
                "epsilon": -1,
                "index_one_based": len(leaves) + 1,
                "point": label,
                "x": orbit_point[0],
            }
        )
        selected_points.append(negate(orbit_point, SECP_P))
    if len(leaves) != M:
        raise AssertionError("GLV row is not M16")
    raw_leaf_sum = point_sum(selected_points, SECP_P)
    raw_relation = add(
        raw_leaf_sum,
        negate(point, SECP_P),
        SECP_P,
    )
    if raw_leaf_sum != point or raw_relation is not None:
        raise AssertionError("raw GLV M16 row failed")
    membership = [
        {
            "index_one_based": leaf["index_one_based"],
            "x": leaf["x"],
            "x_to_D_mod_p": pow(leaf["x"], D, SECP_P),
        }
        for leaf in leaves
    ]
    if D % 3 or any(
        item["x_to_D_mod_p"] != 1 for item in membership
    ):
        raise AssertionError("GLV factor membership failed")

    representative = negate(point, SECP_P)
    signed_rows = [
        {
            "base_point": "P0",
            "epsilon_counts": {"+1": 7, "-1": 7},
            "eta": -1,
            "j": 0,
            "relation_to_representative": "P0 = -phi^0(-P0)",
            "coefficient_contribution_mod_n": 0,
        },
        {
            "base_point": "phi(P0)",
            "epsilon": -1,
            "eta": -1,
            "j": 1,
            "relation_to_representative": "phi(P0) = -phi^1(-P0)",
            "coefficient_contribution_mod_n": SECP_LAMBDA,
        },
        {
            "base_point": "phi^2(P0)",
            "epsilon": -1,
            "eta": -1,
            "j": 2,
            "relation_to_representative": "phi^2(P0) = -phi^2(-P0)",
            "coefficient_contribution_mod_n": lambda2,
        },
    ]
    contributions = []
    for row in signed_rows:
        eta = row["eta"]
        phase = row["j"]
        if "epsilon" in row:
            contribution = (
                row["epsilon"]
                * eta
                * pow(SECP_LAMBDA, phase, SECP_N)
            ) % SECP_N
        else:
            counts = row["epsilon_counts"]
            signed_count = counts["+1"] - counts["-1"]
            contribution = (
                signed_count
                * eta
                * pow(SECP_LAMBDA, phase, SECP_N)
            ) % SECP_N
        if contribution != row["coefficient_contribution_mod_n"]:
            raise AssertionError("GLV eta transport failed")
        contributions.append(contribution)
    if not any(row["eta"] == -1 for row in signed_rows):
        raise AssertionError("GLV replay lacks an eta=-1 case")
    compressed_coefficient = sum(contributions) % SECP_N
    if compressed_coefficient != SECP_N - 1:
        raise AssertionError("GLV compressed coefficient is not -1")
    compressed_leaf = multiply(
        compressed_coefficient,
        representative,
        SECP_P,
    )
    compressed_relation = add(
        compressed_leaf,
        negate(point, SECP_P),
        SECP_P,
    )
    if compressed_leaf != point or compressed_relation is not None:
        raise AssertionError("compressed GLV row failed")

    return {
        "field_and_curve": {
            "p": SECP_P,
            "n": SECP_N,
            "curve": "y^2 = x^3 + 7",
            "D": D,
            "D_divisible_by_3": True,
            "beta": SECP_BETA,
            "lambda": SECP_LAMBDA,
            "beta_polynomial_check_mod_p": 0,
            "lambda_polynomial_check_mod_n": 0,
        },
        "P0": {
            **point_record(point),
            "definition": "the even-y lift of x=1",
            "rhs": 8,
            "n_multiple": point_record(
                multiply(SECP_N, point, SECP_P)
            ),
        },
        "phi_orbit": {
            "positive": [
                {
                    "j": phase,
                    "point": point_record(orbit_point),
                    "x_rule": (
                        "1"
                        if phase == 0
                        else f"beta^{phase} mod p"
                    ),
                    "y_is_even": orbit_point[1] % 2 == 0,
                }
                for phase, orbit_point in enumerate(
                    (point, phi, phi2)
                )
            ],
            "negative": [
                {
                    "j": phase,
                    "point": point_record(
                        negate(orbit_point, SECP_P)
                    ),
                }
                for phase, orbit_point in enumerate(
                    (point, phi, phi2)
                )
            ],
            "positive_orbit_size": 3,
            "signed_orbit_size": 6,
            "orbit_sum": point_record(orbit_sum),
        },
        "m16_membership_row": {
            "leaf_count": len(leaves),
            "leaves": leaves,
            "membership_checks": membership,
            "target": "P0",
            "target_coefficient": -1,
            "semantic_identity": (
                "seven P0 minus seven P0 minus phi(P0) minus "
                "phi^2(P0) minus P0 = O"
            ),
            "construction": (
                "fixed theorem identity with no target search"
            ),
        },
        "representative": {
            "label": "-P0",
            "point": point_record(representative),
            "selection": (
                "fixed deterministic signed-orbit representative"
            ),
        },
        "signed_lift_rows": signed_rows,
        "coefficient_replay": {
            "rule": (
                "a signed occurrence epsilon*Q with "
                "Q=eta*phi^j(representative) contributes "
                "epsilon*eta*lambda^j modulo n"
            ),
            "lambda_squared_mod_n": lambda2,
            "eta_minus_one_rows": 3,
            "leaf_coefficient_on_representative_mod_n": (
                compressed_coefficient
            ),
            "leaf_coefficient_display": "-1",
            "target_coefficient": -1,
            "compressed_row": "-(-P0) - P0 = O",
        },
        "exact_group_checks": {
            "lambda_P0_equals_phi_P0": True,
            "lambda_squared_P0_equals_phi_squared_P0": True,
            "raw_leaf_sum": point_record(raw_leaf_sum),
            "raw_relation_sum": point_record(raw_relation),
            "compressed_leaf_term": point_record(compressed_leaf),
            "compressed_relation_sum": point_record(
                compressed_relation
            ),
            "raw_and_compressed_close": True,
        },
        "theorem_bindings": {
            "whole_group_membership": (
                "Ecdlp.Curve.secp256k1_mem_zmultiples"
            ),
            "glv_eigenvalue": (
                "Ecdlp.Curve."
                "secp256k1_glvPoint_eq_lam_on_zmultiples"
            ),
            "glv_orbit": (
                "Ecdlp.Curve."
                "secp256k1_glvPoint_orbit_three_distinct"
            ),
            "curve_cardinality": (
                "Ecdlp.Curve.secp256k1_card_point_eq_n"
            ),
            "no_nonzero_two_torsion": (
                "Ecdlp.Curve.secp256k1_no_nonzero_two_torsion"
            ),
        },
    }


def check_hash(
    artifact_bytes: bytes,
    hash_path: Path,
    replay: Replay,
) -> None:
    try:
        text = hash_path.read_text(encoding="ascii")
    except (FileNotFoundError, UnicodeDecodeError) as error:
        replay.fail(f"artifact.sha256 unreadable: {error}")
        return
    match = re.fullmatch(r"([0-9a-f]{64})  artifact\.json\n", text)
    if match is None:
        replay.fail("artifact.sha256 has noncanonical format")
        return
    replay.expect(
        "artifact.sha256",
        match.group(1),
        hashlib.sha256(artifact_bytes).hexdigest(),
    )


def require_unique_ids(
    path: str,
    records: list[Any],
    replay: Replay,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(records):
        record = replay.require_dict(f"{path}[{index}]", value)
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            replay.fail(f"{path}[{index}].id: expected nonempty string")
            continue
        if identifier in indexed:
            replay.fail(f"{path}: duplicate stratum id {identifier!r}")
            continue
        indexed[identifier] = record
    return indexed


def flatten_strings(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, str):
        result.append(value)
    elif isinstance(value, list):
        for item in value:
            result.extend(flatten_strings(item))
    elif isinstance(value, dict):
        for key, item in value.items():
            result.append(str(key))
            result.extend(flatten_strings(item))
    return result


def check_scope(document: dict[str, Any], replay: Replay) -> None:
    expected_top_level = {
        "artifact_id",
        "bridge_theorem",
        "claim_boundaries",
        "control_recovery_replay",
        "depends_on",
        "frobenius_classification",
        "frozen_predicates",
        "kind",
        "leaf_lift_types",
        "local_transition_types",
        "producer_checks",
        "projective_s3",
        "recovery_dispositions",
        "schema_version",
        "scope",
        "secp256k1_glv_replay",
        "small_field_replays",
        "source_scope",
        "terminal_disposition",
        "unresolved_fields",
    }
    replay.expect("top-level keys", set(document), expected_top_level)
    replay.expect("schema_version", document.get("schema_version"), "1.0")
    replay.expect(
        "artifact_id",
        document.get("artifact_id"),
        "PKC-SMOOTH-M16-EXCEPTIONAL-FIBERS-001",
    )
    replay.expect(
        "kind",
        document.get("kind"),
        (
            "deterministic_nonexperimental_set_theoretic_"
            "exceptional_fiber_certificate"
        ),
    )

    expected_scope = {
        "included": [
            "homogeneous projective S3 left-fold semantics",
            "finite-field lift and local-root classification",
            "supplied-internal-coordinate point recovery",
            "ordered topology and duplicate accounting",
            "fixed secp256k1 GLV sign replay",
        ],
        "excluded": [
            "S17 expansion or evaluation",
            "any materialized polynomial system",
            "Sage, msolve, F4, Groebner, or solver execution",
            "exact-target relation search",
            "discrete-log computation",
            "rank, yield, or cost accounting",
            "experiment authorization",
            "hypothesis retention",
            "route promotion",
        ],
    }
    replay.expect_exact("scope", document.get("scope"), expected_scope)

    expected_boundaries = {
        "coordinate_difference_saturation": "forbidden",
        "global_s17_equivalence": "not_claimed",
        "multiplicity_equality": "not_claimed",
        "radicality": "not_claimed",
        "result_scope": "set_theoretic",
        "scheme_equivalence": "not_claimed",
    }
    replay.expect_exact(
        "claim_boundaries",
        document.get("claim_boundaries"),
        expected_boundaries,
    )

    equations = ["H(Q_1,Q_2,W_2)=0"]
    equations.extend(
        f"H(W_{index - 1},Q_{index},W_{index})=0"
        for index in range(3, M)
    )
    equations.append("H(W_15,Q_16,Q_T)=0")
    expected_frozen = {
        "algebraic_closure_projective_semantics": {
            "name": "GeoCat_kbar",
            "field_scope": (
                "nonsingular E:y^2=x^3+7 with "
                "char(k) not in {2,3,7}"
            ),
            "external_domain": "Q_1,...,Q_16,Q_T in P1(k)",
            "internal_domain": (
                "W_2,...,W_15 in P1(algebraic_closure(k))"
            ),
            "equations": equations,
            "internal_variables": [
                f"W_{index}=[U_{index}:V_{index}]"
                for index in range(2, M)
            ],
            "status": "frozen",
        },
        "fp_rational_projective_internals": {
            "name": "RatCat_Fp",
            "field_scope": (
                "p not in {2,3,7}; discriminant(E) is nonzero"
            ),
            "external_domain": "Q_1,...,Q_16,Q_T in P1(F_p)",
            "internal_domain": "W_2,...,W_15 in P1(F_p)",
            "equations": equations,
            "status": "frozen",
        },
        "affine_chart": {
            "name": "AffCat_Fp",
            "parent": "RatCat_Fp",
            "field_scope": (
                "p not in {2,3,7}; discriminant(E) is nonzero"
            ),
            "localization": "V_2*...*V_15 != 0",
            "dehomogenization": "W_i=[u_i:1]",
            "identity_excluded": True,
            "status": "frozen",
        },
        "base_recovery": {
            "name": "Recover_Fp",
            "field_scope": (
                "p not in {2,3,7}; discriminant(E) is nonzero"
            ),
            "inputs": (
                "ordered leaf coordinates, supplied projective "
                "internals, and full target point R"
            ),
            "leaf_requirement": (
                "every finite leaf has an E(F_p) lift"
            ),
            "method": (
                "exact point-state DP with retained backpointers"
            ),
            "terminal_requirement": (
                "the final state is R or -R"
            ),
            "status": "frozen",
        },
        "direct_S17": {
            "name": "DirectS17",
            "predicate_defined": False,
            "polynomial_frozen": False,
            "status": "unresolved_not_frozen",
            "reason": (
                "the repository has no frozen recursive projective "
                "definition and no reverse theorem above S4"
            ),
        },
    }
    replay.expect_exact(
        "frozen_predicates",
        document.get("frozen_predicates"),
        expected_frozen,
    )

    coordinate_ideals = [
        *[
            f"<X_{index},Z_{index}>"
            for index in range(1, M + 1)
        ],
        "<X_T,Z_T>",
        *[
            f"<U_{index},V_{index}>"
            for index in range(2, M)
        ],
    ]
    expected_projective_s3 = {
        "name": "H=S3h",
        "curve": (
            "nonsingular E:y^2=x^3+7 over k with "
            "char(k) not in {2,3,7}"
        ),
        "field_scope": (
            "char(k) not in {2,3,7}, equivalently the "
            "discriminant -16*27*7^2 is nonzero in k"
        ),
        "kummer_coordinate": {
            "identity": "kappa(O)=[1:0]",
            "affine": "kappa((x,y))=[x:1]",
        },
        "homogeneous_polynomial": (
            "X1^2*X2^2*Z3^2 + X1^2*Z2^2*X3^2 + "
            "Z1^2*X2^2*X3^2 - 2*X1^2*X2*Z2*X3*Z3 - "
            "2*X1*Z1*X2^2*X3*Z3 - "
            "2*X1*Z1*X2*Z2*X3^2 - "
            "28*(X1*Z1*Z2^2*Z3^2 + "
            "Z1^2*X2*Z2*Z3^2 + Z1^2*Z2^2*X3*Z3)"
        ),
        "multidegree": [2, 2, 2],
        "affine_coefficients_z2_z_1": [
            "(x1-x2)^2",
            "-2*((x1+x2)*(x1*x2)+14)",
            "(x1*x2)^2-28*(x1+x2)",
        ],
        "exact_local_formulas": {
            "distinct_factorization": (
                "H(kappa(P),kappa(Q),[U:V])="
                "(x(P)-x(Q))^2*(U-x(P+Q)*V)*"
                "(U-x(P-Q)*V)"
            ),
            "distinct_discriminant": (
                "Disc_U/V H=16*f(x(P))*f(x(Q)), f(x)=x^3+7"
            ),
            "repeated": (
                "H([x:1],[x:1],[U:V])="
                "V*(-4*f(x)*U+(x^4-56*x)*V)"
            ),
            "identity": (
                "H([1:0],[X:Z],[U:V])=(X*V-Z*U)^2"
            ),
        },
        "projective_validity": (
            "every coordinate pair must differ from [0:0]"
        ),
        "saturation_policy": (
            "remove only components supported on a projective "
            "coordinate pair [0:0]; never remove coordinate-equality "
            "loci"
        ),
        "irrelevant_ideal_saturation": {
            "coordinate_pair_ideals": coordinate_ideals,
            "irrelevant_ideal_B": (
                "product of all 31 listed coordinate-pair ideals"
            ),
            "saturated_ideal": "I_cat : B^infinity",
            "set_theoretic_effect": (
                "exclude the union of loci on which any projective "
                "coordinate pair is [0:0]"
            ),
            "forbidden_extra_saturands": [
                "X_i*Z_j-X_j*Z_i",
                "U_i*V_j-U_j*V_i",
                "all coordinate differences",
            ],
        },
        "scheme_claim": (
            "none; every bridge claim is set-theoretic"
        ),
    }
    replay.expect_exact(
        "projective_s3",
        document.get("projective_s3"),
        expected_projective_s3,
    )
    symbolic_local = replay_symbolic_local_identities()
    replay.expect(
        "symbolic_local.excluded_characteristics",
        symbolic_local["excluded_characteristics"],
        EXCLUDED_CHARACTERISTICS,
    )
    replay.expect(
        "symbolic_local.f7_singular_witness",
        symbolic_local["f7_singular_witness"],
        [0, 0],
    )

    expected_bridge = {
        "local_lemma": (
            "for P,Q over the algebraic closure of such a field, "
            "H(kappa(P),kappa(Q),W)=0 iff W=kappa(P+Q) "
            "or W=kappa(P-Q)"
        ),
        "assumptions": [
            "E/k is the nonsingular curve y^2=x^3+7",
            "char(k) not in {2,3,7}",
            (
                "the curve discriminant -16*27*7^2 "
                "is nonzero in k"
            ),
        ],
        "local_case_split": [
            "distinct finite inputs",
            "repeated finite non-two-torsion inputs",
            "repeated finite two-torsion inputs",
            "at least one identity input",
        ],
        "global_projective_tree": (
            "induction over the 15 left-fold vertices gives "
            "GeoCat_kbar iff the chosen external Kummer coordinates "
            "admit a signed-point relation over the algebraic closure"
        ),
        "fp_projective_tree": (
            "when every external coordinate has an E(F_p) lift, "
            "RatCat_Fp iff a base-field signed relation exists"
        ),
        "affine_chart": (
            "AffCat_Fp iff such a relation exists with every "
            "fixed-order prefix of sizes 2 through 15 nonidentity"
        ),
        "proof_method": (
            "exact local formulas followed by induction"
        ),
        "status": "exact_set_theoretic_bridge",
        "direct_S17_bridge": "unresolved_not_frozen",
    }
    replay.expect_exact(
        "bridge_theorem",
        document.get("bridge_theorem"),
        expected_bridge,
    )

    expected_frobenius = {
        "field_scope": (
            "E/F_p is nonsingular and p not in {2,3,7}"
        ),
        "plus_space": "E_plus=ker(pi-1)=E(F_p)",
        "minus_space": "E_minus=ker(pi+1)",
        "prefix_decomposition": (
            "A=B+T with B in E_plus and T in E_minus"
        ),
        "rational_kummer_criterion": (
            "kappa(A) in P1(F_p) iff pi(A)=A or pi(A)=-A "
            "iff 2T=O or 2B=O"
        ),
        "secp256k1_specialization": (
            "absence of rational two-torsion reduces the criterion "
            "to T=O or B=O"
        ),
        "topology_consequence": (
            "an order is projectively F_p-admissible exactly when "
            "every prefix satisfies the criterion; affine "
            "admissibility also requires every prefix to differ from O"
        ),
    }
    replay.expect_exact(
        "frobenius_classification",
        document.get("frobenius_classification"),
        expected_frobenius,
    )


def check_source_scope(document: dict[str, Any], replay: Replay) -> None:
    expected_source = {
        "all_listed_paths_exist": True,
        "canonical_policy_or_generated_files_hashed": False,
        "curve_cardinality": (
            "Ecdlp/Proved/CurveCardinalityExact.lean"
        ),
        "curve_full_group": "Ecdlp/Proved/CurveFullGroup.lean",
        "glv_eigenvalue": (
            "Ecdlp/Proved/GlvSubgroupEigenvalue.lean"
        ),
        "glv_orbit": "Ecdlp/Proved/GlvOrbit.lean",
        "primary_claim_extract": PRIMARY_CLAIM_EXTRACT,
        "primary_claim_extract_digest_match": True,
        "primary_claim_extract_observed_sha256": (
            PRIMARY_CLAIM_EXTRACT_SHA256
        ),
        "primary_claim_extract_sha256": (
            PRIMARY_CLAIM_EXTRACT_SHA256
        ),
        "semaev_four": "Ecdlp/Proved/SemaevFour.lean",
        "semaev_three": "Ecdlp/Proved/SemaevThree.lean",
        "source_claim_ids": SOURCE_CLAIM_IDS,
        "task016_artifact": TASK016_PATH,
        "task016_artifact_sha256": TASK016_SHA256,
        "task_contract_anchor": "tasks/ECDLP_RESEARCH.md#task-017",
    }
    replay.expect_exact(
        "source_scope",
        document.get("source_scope"),
        expected_source,
    )

    expected_dependency = {
        "artifact": TASK016_PATH,
        "required_sha256": TASK016_SHA256,
        "observed_sha256": TASK016_SHA256,
        "digest_match": True,
    }
    replay.expect_exact(
        "depends_on",
        document.get("depends_on"),
        expected_dependency,
    )

    task016 = REPO_ROOT / TASK016_PATH
    if not task016.is_file():
        replay.fail("TASK-016 artifact is missing")
    else:
        replay.expect(
            "TASK-016 artifact sha256",
            hashlib.sha256(task016.read_bytes()).hexdigest(),
            TASK016_SHA256,
        )
    path_fields = (
        "curve_cardinality",
        "curve_full_group",
        "glv_eigenvalue",
        "glv_orbit",
        "primary_claim_extract",
        "semaev_four",
        "semaev_three",
        "task016_artifact",
    )
    for field in path_fields:
        relative_path = expected_source[field]
        if not (REPO_ROOT / relative_path).is_file():
            replay.fail(
                f"source_scope.{field}: referenced file missing"
            )
    primary_extract = REPO_ROOT / PRIMARY_CLAIM_EXTRACT
    if primary_extract.is_file():
        replay.expect(
            "primary claim extract sha256",
            hashlib.sha256(primary_extract.read_bytes()).hexdigest(),
            PRIMARY_CLAIM_EXTRACT_SHA256,
        )
    task_contract = REPO_ROOT / "tasks/ECDLP_RESEARCH.md"
    if not task_contract.is_file():
        replay.fail("source_scope.task_contract: referenced file missing")
    else:
        contract_text = task_contract.read_text(encoding="utf-8")
        if "TASK-017" not in contract_text:
            replay.fail("task contract has no TASK-017 section")
    typed_evidence = REPO_ROOT / "repo/ECDLP_TYPED_EVIDENCE_V0.json"
    if not typed_evidence.is_file():
        replay.fail("typed evidence registry is missing")
    else:
        try:
            evidence_document = json.loads(
                typed_evidence.read_bytes()
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            replay.fail(f"typed evidence registry unreadable: {error}")
        else:
            evidence_strings = set(flatten_strings(evidence_document))
            for claim_id in SOURCE_CLAIM_IDS:
                if claim_id not in evidence_strings:
                    replay.fail(
                        f"source claim id is absent: {claim_id}"
                    )
    theorem_symbols = {
        "Ecdlp/Proved/CurveCardinalityExact.lean": [
            "secp256k1_card_point_eq_n",
            "secp256k1_no_nonzero_two_torsion",
        ],
        "Ecdlp/Proved/CurveFullGroup.lean": [
            "secp256k1_mem_zmultiples",
        ],
        "Ecdlp/Proved/GlvSubgroupEigenvalue.lean": [
            "secp256k1_glvPoint_eq_lam_on_zmultiples",
        ],
        "Ecdlp/Proved/GlvOrbit.lean": [
            "secp256k1_glvPoint_orbit_three_distinct",
        ],
    }
    for relative_path, symbols in theorem_symbols.items():
        path = REPO_ROOT / relative_path
        if not path.is_file():
            continue
        source_text = path.read_text(encoding="utf-8")
        for symbol in symbols:
            declaration = re.compile(
                rf"\b(?:theorem|lemma)\s+{re.escape(symbol)}\b"
            )
            if declaration.search(source_text) is None:
                replay.fail(
                    f"{relative_path}: theorem symbol missing: {symbol}"
                )


def check_strata(document: dict[str, Any], replay: Replay) -> None:
    expected_leaves = {
        "exhaustive_nonoverlapping": True,
        "field_scope": (
            "nonsingular E:y^2=x^3+7 over F_p with "
            "p not in {2,3,7}"
        ),
        "normalization": (
            "a valid finite [X:Z] has x=X/Z; a valid Z=0 "
            "coordinate normalizes to O=[1:0]"
        ),
        "types": [
            {
                "id": "invalid_projective",
                "condition": "[X:Z]=[0:0]",
                "geometric_lifts": 0,
                "frobenius_type": "undefined",
                "base_recovery": "reject INVALID_PROJECTIVE",
            },
            {
                "id": "identity",
                "condition": "Z=0 and X!=0",
                "normalized_coordinate": "[1:0]",
                "geometric_lifts": 1,
                "lift": "O",
                "frobenius_type": "plus",
                "base_recovery": "retain the identity point",
            },
            {
                "id": "finite_base_pair",
                "condition": "Z!=0 and chi(x^3+7)=+1",
                "geometric_lifts": 2,
                "lifts": "P and -P in E(F_p)",
                "frobenius_type": "plus",
                "base_recovery": "retain both signed lifts",
            },
            {
                "id": "finite_extension_pair",
                "condition": "Z!=0 and chi(x^3+7)=-1",
                "geometric_lifts": 2,
                "lifts": "P and -P in E(F_(p^2))",
                "frobenius_equation": "pi(P)=-P",
                "frobenius_type": "minus",
                "base_recovery": "reject EXTERNAL_NONLIFT",
            },
            {
                "id": "finite_rational_two_torsion",
                "condition": "Z!=0 and x^3+7=0",
                "geometric_lifts": 1,
                "lift": "T=(x,0)=-T in E(F_p)[2]",
                "frobenius_type": "plus",
                "base_recovery": (
                    "retain one lift and collapse sign aliases"
                ),
            },
        ],
    }
    replay.expect_exact(
        "leaf_lift_types",
        document.get("leaf_lift_types"),
        expected_leaves,
    )

    transition_ids = [
        "invalid_projective_input",
        "identity_input_duplicate",
        "repeated_two_torsion_duplicate",
        "repeated_tangent",
        "distinct_two_torsion_duplicate",
        "distinct_rational_split",
        "distinct_extension_only",
    ]
    expected_transitions = {
        "exhaustive_nonoverlapping_for_valid_inputs": True,
        "field_scope": (
            "nonsingular E:y^2=x^3+7 over F_p with "
            "p not in {2,3,7}"
        ),
        "priority": transition_ids,
        "types": [
            {
                "id": "invalid_projective_input",
                "condition": "one input is [0:0]",
                "root_structure": "undefined",
                "disposition": "reject INVALID_PROJECTIVE",
            },
            {
                "id": "identity_input_duplicate",
                "condition": "at least one valid input is O",
                "formula": (
                    "H(O,[X:Z],[U:V])=(X*V-Z*U)^2"
                ),
                "root_structure": (
                    "the other coordinate, multiplicity 2"
                ),
                "disposition": (
                    "retain one point state, not two aliases"
                ),
            },
            {
                "id": "repeated_two_torsion_duplicate",
                "condition": "finite a=b and f(a)=a^3+7=0",
                "formula": (
                    "H([a:1],[a:1],[U:V])=c*V^2 with c!=0"
                ),
                "root_structure": "O, multiplicity 2",
                "disposition": (
                    "retain O and collapse the two local signs"
                ),
            },
            {
                "id": "repeated_tangent",
                "condition": "finite a=b and f(a)!=0",
                "formula": (
                    "H([a:1],[a:1],[U:V])="
                    "V*(-4*f(a)*U+(a^4-56*a)*V)"
                ),
                "root_structure": (
                    "O and kappa(2P), each multiplicity 1"
                ),
                "disposition": (
                    "keep both projective branches; affine mode "
                    "keeps only kappa(2P)"
                ),
            },
            {
                "id": "distinct_two_torsion_duplicate",
                "condition": "finite a!=b and f(a)*f(b)=0",
                "discriminant": "16*f(a)*f(b)=0",
                "root_structure": (
                    "one finite F_p coordinate, multiplicity 2"
                ),
                "disposition": (
                    "retain one state and collapse sign aliases"
                ),
            },
            {
                "id": "distinct_rational_split",
                "condition": (
                    "finite a!=b and chi(f(a)*f(b))=+1"
                ),
                "discriminant": (
                    "16*f(a)*f(b), a nonzero square"
                ),
                "root_structure": (
                    "two distinct roots in P1(F_p)"
                ),
                "disposition": (
                    "retain both exact point branches"
                ),
            },
            {
                "id": "distinct_extension_only",
                "condition": (
                    "finite a!=b and chi(f(a)*f(b))=-1"
                ),
                "discriminant": "16*f(a)*f(b), a nonsquare",
                "root_structure": (
                    "two conjugate simple roots in P1(F_(p^2)); "
                    "no root in P1(F_p)"
                ),
                "disposition": (
                    "reject INTERNAL_EXTENSION_ONLY in F_p mode"
                ),
            },
        ],
        "duplicate_root_sources": [
            "identity_input_duplicate",
            "repeated_two_torsion_duplicate",
            "distinct_two_torsion_duplicate",
        ],
        "duplicate_policy": (
            "algebraic multiplicity never creates another point "
            "state, backpointer, or relation row"
        ),
    }
    replay.expect_exact(
        "local_transition_types",
        document.get("local_transition_types"),
        expected_transitions,
    )

    expected_dispositions = {
        "partition_rule": (
            "apply the first matching row in priority order"
        ),
        "exhaustive_nonoverlapping": True,
        "field_scope": (
            "nonsingular E:y^2=x^3+7 over F_p with "
            "p not in {2,3,7}"
        ),
        "rows": [
            {
                "priority": 1,
                "id": "INVALID_PROJECTIVE",
                "condition": (
                    "some coordinate pair is [0:0]"
                ),
                "geometric_projective": "excluded",
                "fp_projective": "excluded",
                "affine": "excluded",
                "base_recovery": "reject",
            },
            {
                "priority": 2,
                "id": "EXTERNAL_NONLIFT",
                "condition": (
                    "all coordinates are valid and some finite leaf "
                    "has chi(f(x))=-1"
                ),
                "geometric_projective": "allowed",
                "fp_projective": "may be allowed",
                "affine": "may be allowed",
                "base_recovery": (
                    "reject before row emission"
                ),
            },
            {
                "priority": 3,
                "id": "INTERNAL_EXTENSION_ONLY",
                "condition": (
                    "all finite leaves lift over F_p, but a "
                    "required local root is present only over an "
                    "extension"
                ),
                "geometric_projective": "allowed",
                "fp_projective": "absent",
                "affine": "absent",
                "base_recovery": "reject",
            },
            {
                "priority": 4,
                "id": "IDENTITY_PREFIX",
                "condition": (
                    "base recovery succeeds and at least one "
                    "supplied internal coordinate has V_i=0"
                ),
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "reject",
                "base_recovery": (
                    "accept with an explicit O state"
                ),
            },
            {
                "priority": 5,
                "id": "RATIONAL_TWO_TORSION",
                "condition": (
                    "no earlier row matches and some retained lift "
                    "has y=0"
                ),
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": (
                    "accept if every internal V_i!=0"
                ),
                "base_recovery": (
                    "accept after sign-alias collapse"
                ),
            },
            {
                "priority": 6,
                "id": "REPEATED_TANGENT",
                "condition": (
                    "no earlier row matches and a repeated finite "
                    "input uses its tangent output"
                ),
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "accept",
                "base_recovery": (
                    "accept with exact branch backpointer"
                ),
            },
            {
                "priority": 7,
                "id": "ORDINARY_RATIONAL",
                "condition": "none of the earlier rows matches",
                "geometric_projective": "accept",
                "fp_projective": "accept",
                "affine": "accept",
                "base_recovery": (
                    "accept after both exact curve checks"
                ),
            },
        ],
        "post_acceptance_normalizations": {
            "topology_permutations": (
                "keep the ordered leaf tuple, coordinate multiset, "
                "signed point multiset, and normalized row as "
                "distinct objects; replay each order because prefix "
                "admissibility depends on it"
            ),
            "glv_lift_signs": (
                "retain eta in Q=eta*phi^j(P0) and use "
                "epsilon*eta*lambda^j modulo n"
            ),
        },
    }
    replay.expect_exact(
        "recovery_dispositions",
        document.get("recovery_dispositions"),
        expected_dispositions,
    )

    small_fields = replay.require_dict(
        "small_field_replays",
        document.get("small_field_replays"),
    )
    replay.expect(
        "small_field_replays.keys",
        set(small_fields),
        {
            "F13_no_rational_two_torsion",
            "F11_with_rational_two_torsion",
        },
    )
    replay.expect_exact(
        "small_field_replays.F13_no_rational_two_torsion",
        small_fields.get("F13_no_rational_two_torsion"),
        replay_small_field(13),
    )
    replay.expect_exact(
        "small_field_replays.F11_with_rational_two_torsion",
        small_fields.get("F11_with_rational_two_torsion"),
        replay_small_field(11),
    )


def check_recovery(document: dict[str, Any], replay: Replay) -> None:
    expected_control = replay_control_certificate()
    replay.expect_exact(
        "control_recovery_replay",
        document.get("control_recovery_replay"),
        expected_control,
    )

    expected_identity = replay_identity_dp()
    actual_identity = replay.require_dict(
        "control_recovery_replay.supplied_internal_dp.identity_fiber",
        replay.require_dict(
            "control_recovery_replay.supplied_internal_dp",
            replay.require_dict(
                "control_recovery_replay",
                document.get("control_recovery_replay"),
            ).get("supplied_internal_dp"),
        ).get("identity_fiber"),
    )
    replay.expect(
        "identity_fiber.accepted_masks",
        actual_identity.get("accepted_masks"),
        [
            record["sign_mask_tail_15"]
            for record in expected_identity["accepted_preimages"]
        ],
    )
    replay.expect(
        "identity_fiber.internal_coordinates",
        actual_identity.get("internal_coordinates"),
        expected_control["supplied_internal_dp"][
            "identity_fiber"
        ]["internal_coordinates"],
    )

    expected_glv = replay_glv()
    replay.expect_exact(
        "secp256k1_glv_replay",
        document.get("secp256k1_glv_replay"),
        expected_glv,
    )

    producer_checks = {
        "prior_digest_bound": True,
        "primary_claim_extract_digest_bound": True,
        "all_source_paths_exist": True,
        "nonsingular_curve_scope_enforced": True,
        "excluded_characteristics": EXCLUDED_CHARACTERISTICS,
        "small_fields_exhaustive": [11, 13],
        "control_projective_fibers_replayed": (
            expected_control["fiber_accounting"][
                "projective_fibers"
            ]
        ),
        "control_normalized_preimages_replayed": (
            expected_control["fiber_accounting"][
                "normalized_preimages"
            ]
        ),
        "control_backpointer_edges_replayed": (
            expected_control["supplied_internal_dp"][
                "backpointer_edge_count"
            ]
        ),
        "secp_m16_leaf_count": expected_glv[
            "m16_membership_row"
        ]["leaf_count"],
        "secp_raw_group_check": (
            expected_glv["exact_group_checks"][
                "raw_relation_sum"
            ]
            == {"kind": "identity"}
        ),
        "secp_compressed_group_check": (
            expected_glv["exact_group_checks"][
                "compressed_relation_sum"
            ]
            == {"kind": "identity"}
        ),
        "direct_S17_materialized": False,
    }
    replay.expect_exact(
        "producer_checks",
        document.get("producer_checks"),
        producer_checks,
    )


def check_terminal(document: dict[str, Any], replay: Replay) -> None:
    expected_terminal = {
        "scientific_disposition": "scoped_blocker",
        "completed_scope": (
            "exact set-theoretic homogeneous projective-tree to "
            "signed-point bridge, including all named local strata "
            "and base-recovery normalization"
        ),
        "remaining_blocker": (
            "the direct S17 predicate is not frozen, and no reverse "
            "theorem above S4 is present"
        ),
        "next_mathematical_step": (
            "freeze a recursive projective definition of S17 with "
            "declared resultant degrees, then test a projective "
            "resultant induction against the frozen tree predicate"
        ),
        "cell_status": "open_non_executable",
        "experiment_permission": "none",
        "retention_disposition": "zero_retention_success",
        "cost_quantity_transition": "partial_to_partial",
        "barrier_transition": "open_to_open",
        "cell_transition": "open_to_open",
        "authorization": "none",
        "route_effect": "none",
        "hypothesis_effect": "none",
        "rank_status": "unpriced",
        "yield_status": "unpriced",
        "cost_quantity_status": "partial",
        "solving_cost_status": "unpriced",
        "barrier_effect": "narrowed_open",
        "assurance": "certificate_replayed",
        "source_independence": "not_established",
        "calibration": "excluded_nonexperimental",
    }
    replay.expect_exact(
        "terminal_disposition",
        document.get("terminal_disposition"),
        expected_terminal,
    )
    replay.expect_exact(
        "unresolved_fields",
        document.get("unresolved_fields"),
        [
            "a frozen direct S17 definition",
            "a reverse direct-S17 theorem above S4",
            "radicality or scheme-level multiplicity comparison",
        ],
    )

    terminal = replay.require_dict(
        "terminal_disposition",
        document.get("terminal_disposition"),
    )
    for field in (
        "rank_status",
        "yield_status",
        "solving_cost_status",
    ):
        if terminal.get(field) != "unpriced":
            replay.fail(f"terminal_disposition.{field}: must be unpriced")
    if terminal.get("cost_quantity_status") != "partial":
        replay.fail(
            "terminal_disposition.cost_quantity_status: must be partial"
        )
    if "cost_status" in terminal:
        replay.fail("terminal_disposition.cost_status is obsolete")
    replay.expect(
        "terminal_disposition.assurance",
        terminal.get("assurance"),
        "certificate_replayed",
    )
    replay.expect(
        "terminal_disposition.source_independence",
        terminal.get("source_independence"),
        "not_established",
    )
    replay.expect(
        "terminal_disposition.calibration",
        terminal.get("calibration"),
        "excluded_nonexperimental",
    )
    replay.expect(
        "terminal_disposition.barrier_effect",
        terminal.get("barrier_effect"),
        "narrowed_open",
    )
    if terminal.get("barrier_transition") != "open_to_open":
        replay.fail("TASK-017 cannot close the wider barrier")
    if terminal.get("cell_transition") != "open_to_open":
        replay.fail("TASK-017 cannot close the cell")
    if (
        terminal.get("authorization") != "none"
        or terminal.get("experiment_permission") != "none"
    ):
        replay.fail("TASK-017 cannot authorize execution")
    if (
        terminal.get("route_effect") != "none"
        or terminal.get("hypothesis_effect") != "none"
    ):
        replay.fail("TASK-017 cannot promote a route or hypothesis")


def validate_document(
    document: dict[str, Any],
    artifact_bytes: bytes,
    hash_path: Path,
) -> list[str]:
    replay = Replay()
    if artifact_bytes != canonical_bytes(document):
        replay.fail("artifact.json is not canonical JSON")
    check_hash(artifact_bytes, hash_path, replay)
    check_scope(document, replay)
    check_source_scope(document, replay)
    check_strata(document, replay)
    check_recovery(document, replay)
    check_terminal(document, replay)
    return replay.failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact", type=Path, default=HERE / "artifact.json"
    )
    parser.add_argument(
        "--hash-file", type=Path, default=HERE / "artifact.sha256"
    )
    args = parser.parse_args()
    try:
        artifact_bytes = args.artifact.read_bytes()
        document = json.loads(artifact_bytes)
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"ERROR: artifact unreadable: {error}", file=sys.stderr)
        return 1
    if not isinstance(document, dict):
        print("ERROR: artifact root must be an object", file=sys.stderr)
        return 1
    try:
        failures = validate_document(
            document, artifact_bytes, args.hash_file
        )
    except (AssertionError, ValueError, ZeroDivisionError) as error:
        print(f"ERROR: independent replay failed: {error}", file=sys.stderr)
        return 1
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("independent TASK-017 exceptional-fiber replay passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
