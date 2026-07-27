#!/usr/bin/env python3
"""Generate the deterministic M16 affine-semantic bridge certificate.

This is a non-experimental exact-arithmetic certificate.  It does not expand
S17, materialize a polynomial system, run a solver, or target secp256k1.  It
records the exact domain on which a left-fold affine S3 presentation has the
intended signed-point meaning and gives two finite witnesses showing why an
unconditional direct/recursive equivalence needs identity strata.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any


D = 564_522
M = 16
FACTOR_CHAIN = (2, 3, 7, 13_441)

CONTROL_P = D + 1
CONTROL_CURVE_A = 0
CONTROL_CURVE_B = 7
CONTROL_CURVE_ORDER = 564_469
CONTROL_CURVE_ORDER_FACTORS = (163, 3_463)
CONTROL_SUBGROUP_ORDER = 3_463
CONTROL_COFACTOR = 163
CONTROL_SEED = (2, 100_588)

BASE_SCALAR = 1
REPEATED_SCALAR = 50
DOUBLED_REPEATED_SCALAR = 100
TARGET_SCALAR = 14
EXTENSION_TARGET_SCALAR = 12

SMALL_P = 13
SMALL_P_POINT = (7, 5)
SMALL_Q_POINT = (8, 5)

EXTENSION_P = 5
EXTENSION_CURVE_A = 0
EXTENSION_CURVE_B = 2
EXTENSION_INPUTS = (1, 4)

M16_DESK_ARTIFACT = (
    "experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json"
)
M16_DESK_SHA256 = (
    "59596c3c59f5389c49742ba4a26d500445557ee6398d6aaad63c7995a93242f7"
)

HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

Point = tuple[int, int] | None


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def is_prime_trial(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def legendre_symbol(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    power = pow(residue, (prime - 1) // 2, prime)
    if power == 1:
        return 1
    if power == prime - 1:
        return -1
    raise AssertionError("Euler criterion produced a non-Legendre value")


def curve_order(prime: int, a: int, b: int) -> int:
    return prime + 1 + sum(
        legendre_symbol(x**3 + a * x + b, prime)
        for x in range(prime)
    )


def curve_discriminant(prime: int, a: int, b: int) -> int:
    return (-16 * (4 * a**3 + 27 * b**2)) % prime


def on_curve(point: Point, prime: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - (x**3 + a * x + b)) % prime == 0


def point_neg(point: Point, prime: int) -> Point:
    if point is None:
        return None
    return point[0], (-point[1]) % prime


def point_add(
    left: Point, right: Point, prime: int, a: int, b: int
) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    if not on_curve(left, prime, a, b) or not on_curve(
        right, prime, a, b
    ):
        raise ValueError("point_add received an off-curve point")
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if left == right:
        denominator = (2 * y1) % prime
        if denominator == 0:
            return None
        slope = (3 * x1 * x1 + a) * pow(
            denominator, prime - 2, prime
        )
    else:
        denominator = (x2 - x1) % prime
        slope = (y2 - y1) * pow(denominator, prime - 2, prime)
    slope %= prime
    x3 = (slope * slope - x1 - x2) % prime
    y3 = (slope * (x1 - x3) - y1) % prime
    result = (x3, y3)
    if not on_curve(result, prime, a, b):
        raise AssertionError("point addition left the curve")
    return result


def scalar_mul(
    scalar: int, point: Point, prime: int, a: int, b: int
) -> Point:
    if scalar < 0:
        return scalar_mul(-scalar, point_neg(point, prime), prime, a, b)
    result: Point = None
    addend = point
    value = scalar
    while value:
        if value & 1:
            result = point_add(result, addend, prime, a, b)
        addend = point_add(addend, addend, prime, a, b)
        value >>= 1
    return result


def point_record(point: Point) -> dict[str, Any]:
    if point is None:
        return {"kind": "identity"}
    return {"kind": "affine", "x": point[0], "y": point[1]}


def s3_coefficients(
    prime: int, a: int, b: int, x1: int, x2: int
) -> list[int]:
    """Coefficients [z^2, z, 1] of S3(a,b,x1,x2,z)."""
    return [
        (x1 - x2) ** 2 % prime,
        (
            -2
            * ((x1 + x2) * (x1 * x2 + a) + 2 * b)
        )
        % prime,
        ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % prime,
    ]


def eval_quadratic(coefficients: list[int], value: int, prime: int) -> int:
    a2, a1, a0 = coefficients
    return (a2 * value * value + a1 * value + a0) % prime


def sylvester_2_2(
    left: list[int], right: list[int]
) -> list[list[int]]:
    a2, a1, a0 = left
    b2, b1, b0 = right
    return [
        [a2, a1, a0, 0],
        [0, a2, a1, a0],
        [b2, b1, b0, 0],
        [0, b2, b1, b0],
    ]


def determinant_integer(matrix: list[list[int]]) -> int:
    total = 0
    size = len(matrix)
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        product = math.prod(
            matrix[row][permutation[row]] for row in range(size)
        )
        total += (-1 if inversions % 2 else 1) * product
    return total


def canonical_scalar(scalar: int, order: int) -> int:
    residue = scalar % order
    return min(residue, (-residue) % order)


def reachable_layers(
    initial_scalar: int, repeated_addend: int, additions: int, order: int
) -> list[list[int]]:
    states = {canonical_scalar(initial_scalar, order)}
    layers = [sorted(states)]
    for _ in range(additions):
        states = {
            canonical_scalar(state + sign * repeated_addend, order)
            for state in states
            for sign in (-1, 1)
        }
        states.discard(0)
        layers.append(sorted(states))
    return layers


def verify_control_transition_exhaustion(
    base: Point,
    repeated: Point,
    layers: list[list[int]],
) -> tuple[int, int]:
    if base is None or repeated is None:
        raise AssertionError("control subgroup points must be affine")
    checked_parents = 0
    checked_roots = 0
    base_x = base[0]
    for layer in layers[:-1]:
        for scalar in layer:
            parent = scalar_mul(
                scalar,
                base,
                CONTROL_P,
                CONTROL_CURVE_A,
                CONTROL_CURVE_B,
            )
            plus = scalar_mul(
                scalar + 1,
                base,
                CONTROL_P,
                CONTROL_CURVE_A,
                CONTROL_CURVE_B,
            )
            minus = scalar_mul(
                scalar - 1,
                base,
                CONTROL_P,
                CONTROL_CURVE_A,
                CONTROL_CURVE_B,
            )
            if parent is None or plus is None or minus is None:
                raise AssertionError("transition unexpectedly reached identity")
            if parent[0] == base_x:
                raise AssertionError("transition unexpectedly hit repeated-x fiber")
            coefficients = s3_coefficients(
                CONTROL_P,
                CONTROL_CURVE_A,
                CONTROL_CURVE_B,
                parent[0],
                base_x,
            )
            if coefficients[0] == 0:
                raise AssertionError("distinct transition lost quadratic degree")
            roots = {plus[0], minus[0]}
            if len(roots) != 2:
                raise AssertionError("quadratic transition roots collided")
            if any(
                eval_quadratic(coefficients, root, CONTROL_P) != 0
                for root in roots
            ):
                raise AssertionError("group-predicted S3 root failed")
            checked_parents += 1
            checked_roots += 2
    return checked_parents, checked_roots


def enumerate_recovery_preimages() -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []
    per_rank: list[dict[str, int]] = []
    position_pairs = list(itertools.combinations(range(M), 2))
    for rank, repeated_positions in enumerate(position_pairs):
        scalars = [BASE_SCALAR] * M
        for position in repeated_positions:
            scalars[position] = REPEATED_SCALAR

        right_by_sum: dict[int, list[int]] = {}
        for right_mask in range(1 << 8):
            right_sum = sum(
                (1 if (right_mask >> offset) & 1 else -1)
                * scalars[8 + offset]
                for offset in range(8)
            )
            right_by_sum.setdefault(right_sum, []).append(right_mask)

        rank_records: list[dict[str, Any]] = []
        for left_mask in range(1 << 7):
            left_sum = scalars[0] + sum(
                (1 if (left_mask >> offset) & 1 else -1)
                * scalars[1 + offset]
                for offset in range(7)
            )
            for target_orientation in (-1, 1):
                required_right = (
                    target_orientation * TARGET_SCALAR - left_sum
                )
                for right_mask in right_by_sum.get(required_right, []):
                    sign_mask = left_mask | (right_mask << 7)
                    signs = [1] + [
                        1 if (sign_mask >> (index - 1)) & 1 else -1
                        for index in range(1, M)
                    ]
                    prefix = 0
                    identity_prefix_sizes: list[int] = []
                    for index, (sign, scalar) in enumerate(
                        zip(signs, scalars, strict=True), start=1
                    ):
                        prefix += sign * scalar
                        if (
                            2 <= index <= M - 1
                            and prefix % CONTROL_SUBGROUP_ORDER == 0
                        ):
                            identity_prefix_sizes.append(index)
                    record = {
                        "identity_prefix_sizes": identity_prefix_sizes,
                        "permutation_rank": rank,
                        "repeated_positions_zero_based": list(
                            repeated_positions
                        ),
                        "sign_mask_tail_15": sign_mask,
                        "target_orientation": target_orientation,
                    }
                    rank_records.append(record)
                    accepted.append(record)
        per_rank.append(
            {
                "affine_admissible": sum(
                    not record["identity_prefix_sizes"]
                    for record in rank_records
                ),
                "direct": len(rank_records),
                "identity_blocked": sum(
                    bool(record["identity_prefix_sizes"])
                    for record in rank_records
                ),
                "rank": rank,
            }
        )

    accepted.sort(
        key=lambda item: (
            item["permutation_rank"],
            item["sign_mask_tail_15"],
            item["target_orientation"],
        )
    )
    admissible = [
        record for record in accepted if not record["identity_prefix_sizes"]
    ]
    blocked = [
        record for record in accepted if record["identity_prefix_sizes"]
    ]
    derived_rows: set[tuple[int, int]] = set()
    for record in accepted:
        repeated_positions = set(
            record["repeated_positions_zero_based"]
        )
        mask = record["sign_mask_tail_15"]
        signs = [1] + [
            1 if (mask >> (index - 1)) & 1 else -1
            for index in range(1, M)
        ]
        orientation = record["target_orientation"]
        base_coefficient = orientation * sum(
            signs[index]
            for index in range(M)
            if index not in repeated_positions
        )
        repeated_coefficient = orientation * sum(
            signs[index] for index in repeated_positions
        )
        derived_rows.add((base_coefficient, repeated_coefficient))
    if (
        len(position_pairs) != 120
        or len(accepted) != 240
        or len(admissible) != 238
        or len(blocked) != 2
        or sorted(
            {record["permutation_rank"] for record in blocked}
        )
        != [0]
        or any(record["identity_prefix_sizes"] != [2] for record in blocked)
        or derived_rows != {(TARGET_SCALAR, 0)}
    ):
        raise AssertionError("recovery permutation audit count mismatch")

    normalized_row = {
        "dropped_zero_coefficients": [
            {
                "basis": "repeated_50P",
                "coefficient_mod_order": 0,
            }
        ],
        "factor_coefficients": [
            {
                "basis": "base_P",
                "coefficient_mod_order": TARGET_SCALAR,
            }
        ],
        "target_coefficient_mod_order": CONTROL_SUBGROUP_ORDER - 1,
        "verification": "[14]P - R = identity",
    }
    return {
        "accepted_record_sha256": hashlib.sha256(
            canonical_bytes(accepted)
        ).hexdigest(),
        "affine_admissible_preimages": len(admissible),
        "affine_admissible_record_sha256": hashlib.sha256(
            canonical_bytes(admissible)
        ).hexdigest(),
        "blocked_records": blocked,
        "coordinate_multiset": [
            {"multiplicity": 14, "scalar_on_P": BASE_SCALAR},
            {"multiplicity": 2, "scalar_on_P": REPEATED_SCALAR},
        ],
        "direct_preimages": len(accepted),
        "derived_point_basis_coefficients": {
            "base_P": TARGET_SCALAR,
            "repeated_50P": 0,
        },
        "identity_blocked_preimages": len(blocked),
        "ordering_rank_definition": (
            "lexicographic combinations of the two zero-based positions "
            "occupied by repeated_50P"
        ),
        "per_rank_counts_sha256": hashlib.sha256(
            canonical_bytes(per_rank)
        ).hexdigest(),
        "relative_sign_convention": (
            "the first leaf sign is +1; bit i-1 of sign_mask_tail_15 "
            "selects +1 for leaf i and 0 selects -1"
        ),
        "normalized_row": normalized_row,
        "normalized_row_preimages": len(accepted),
        "normalized_row_sha256": hashlib.sha256(
            canonical_bytes(normalized_row)
        ).hexdigest(),
        "unique_orderings": len(position_pairs),
    }


def build_artifact() -> dict[str, Any]:
    if math.prod(FACTOR_CHAIN) != D:
        raise AssertionError("factor chain does not multiply to D")
    if not is_prime_trial(CONTROL_P):
        raise AssertionError("control field modulus is not prime")
    if CONTROL_P - 1 != D:
        raise AssertionError("control multiplicative group does not have order D")
    if curve_discriminant(
        CONTROL_P, CONTROL_CURVE_A, CONTROL_CURVE_B
    ) == 0:
        raise AssertionError("control curve is singular")

    point_count = curve_order(
        CONTROL_P, CONTROL_CURVE_A, CONTROL_CURVE_B
    )
    if point_count != CONTROL_CURVE_ORDER:
        raise AssertionError("unexpected control curve order")
    if math.prod(CONTROL_CURVE_ORDER_FACTORS) != point_count:
        raise AssertionError("control curve factorization mismatch")
    if not all(is_prime_trial(item) for item in CONTROL_CURVE_ORDER_FACTORS):
        raise AssertionError("control curve-order factors must be prime")

    two_torsion_x = [
        x
        for x in range(CONTROL_P)
        if (x**3 + CONTROL_CURVE_B) % CONTROL_P == 0
    ]
    if two_torsion_x:
        raise AssertionError("control curve unexpectedly has rational 2-torsion")

    if not on_curve(
        CONTROL_SEED, CONTROL_P, CONTROL_CURVE_A, CONTROL_CURVE_B
    ):
        raise AssertionError("control seed is off curve")
    base = scalar_mul(
        CONTROL_COFACTOR,
        CONTROL_SEED,
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    if base is None or scalar_mul(
        CONTROL_SUBGROUP_ORDER,
        base,
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    ) is not None:
        raise AssertionError("control base does not have the certified order")

    repeated = scalar_mul(
        REPEATED_SCALAR,
        base,
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    doubled_repeated = scalar_mul(
        DOUBLED_REPEATED_SCALAR,
        base,
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    target = scalar_mul(
        TARGET_SCALAR,
        base,
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    if repeated is None or doubled_repeated is None or target is None:
        raise AssertionError("control witness point is identity")
    witness_points = (base, repeated, doubled_repeated, target)
    if any(point is None or point[0] == 0 for point in witness_points):
        raise AssertionError("control witness has a zero x-coordinate")
    if any(pow(point[0], D, CONTROL_P) != 1 for point in witness_points):
        raise AssertionError("control witness left the source root set")

    repeated_coefficients = s3_coefficients(
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
        repeated[0],
        repeated[0],
    )
    if repeated_coefficients[0] != 0 or repeated_coefficients[1] == 0:
        raise AssertionError("repeated-x S3 slice is not a nonzero linear form")
    repeated_root = (
        -repeated_coefficients[2]
        * pow(repeated_coefficients[1], CONTROL_P - 2, CONTROL_P)
    ) % CONTROL_P
    if repeated_root != doubled_repeated[0]:
        raise AssertionError("repeated-x S3 root is not x(2A)")

    layers = reachable_layers(
        DOUBLED_REPEATED_SCALAR,
        BASE_SCALAR,
        M - 2,
        CONTROL_SUBGROUP_ORDER,
    )
    checked_parents, checked_roots = verify_control_transition_exhaustion(
        base, repeated, layers
    )
    terminal_states = layers[-1]
    target_class = canonical_scalar(
        TARGET_SCALAR, CONTROL_SUBGROUP_ORDER
    )
    if target_class in terminal_states:
        raise AssertionError("recursive affine chain reaches the target")

    signed_relation: Point = None
    signed_leaves = [
        repeated,
        point_neg(repeated, CONTROL_P),
        *([base] * (M - 2)),
    ]
    for point in signed_leaves:
        signed_relation = point_add(
            signed_relation,
            point,
            CONTROL_P,
            CONTROL_CURVE_A,
            CONTROL_CURVE_B,
        )
    signed_relation = point_add(
        signed_relation,
        point_neg(target, CONTROL_P),
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    if signed_relation is not None:
        raise AssertionError("direct signed relation witness does not close")
    recovery_preimage_audit = enumerate_recovery_preimages()
    normalized_relation = point_add(
        scalar_mul(
            TARGET_SCALAR,
            base,
            CONTROL_P,
            CONTROL_CURVE_A,
            CONTROL_CURVE_B,
        ),
        point_neg(target, CONTROL_P),
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    if normalized_relation is not None:
        raise AssertionError("normalized recovery row does not close")

    small_f = s3_coefficients(
        SMALL_P, 0, 7, SMALL_P_POINT[0], SMALL_P_POINT[0]
    )
    small_g = s3_coefficients(
        SMALL_P, 0, 7, SMALL_Q_POINT[0], SMALL_Q_POINT[0]
    )
    small_f_roots = [
        value
        for value in range(SMALL_P)
        if eval_quadratic(small_f, value, SMALL_P) == 0
    ]
    small_g_roots = [
        value
        for value in range(SMALL_P)
        if eval_quadratic(small_g, value, SMALL_P) == 0
    ]
    small_matrix = sylvester_2_2(small_f, small_g)
    small_resultant = determinant_integer(small_matrix) % SMALL_P
    small_relation: Point = None
    for point in (
        SMALL_P_POINT,
        point_neg(SMALL_P_POINT, SMALL_P),
        SMALL_Q_POINT,
        point_neg(SMALL_Q_POINT, SMALL_P),
    ):
        small_relation = point_add(small_relation, point, SMALL_P, 0, 7)
    if (
        small_resultant != 0
        or set(small_f_roots) & set(small_g_roots)
        or small_relation is not None
    ):
        raise AssertionError("small S4 boundary witness failed")

    extension_membership_roots = [
        value
        for value in range(1, EXTENSION_P)
        if pow(value, D, EXTENSION_P) == 1
    ]
    extension_lifts = []
    for x in EXTENSION_INPUTS:
        rhs = (
            x**3 + EXTENSION_CURVE_A * x + EXTENSION_CURVE_B
        ) % EXTENSION_P
        y_roots = [
            y for y in range(EXTENSION_P) if y * y % EXTENSION_P == rhs
        ]
        extension_lifts.append(
            {"rhs": rhs, "x": x, "y_roots": y_roots}
        )
    extension_f = s3_coefficients(
        EXTENSION_P,
        EXTENSION_CURVE_A,
        EXTENSION_CURVE_B,
        *EXTENSION_INPUTS,
    )
    extension_roots = [
        value
        for value in range(EXTENSION_P)
        if eval_quadratic(extension_f, value, EXTENSION_P) == 0
    ]
    extension_discriminant = (
        extension_f[1] ** 2
        - 4 * extension_f[0] * extension_f[2]
    ) % EXTENSION_P
    extension_matrix = sylvester_2_2(extension_f, extension_f)
    extension_resultant = (
        determinant_integer(extension_matrix) % EXTENSION_P
    )
    if (
        extension_membership_roots != [1, 4]
        or extension_lifts
        != [
            {"rhs": 3, "x": 1, "y_roots": []},
            {"rhs": 1, "x": 4, "y_roots": [1, 4]},
        ]
        or extension_f != [4, 2, 1]
        or extension_discriminant != 3
        or extension_roots
        or extension_resultant != 0
    ):
        raise AssertionError("extension-only membership witness failed")

    control_extension_inputs = (1, CONTROL_P - 1)
    control_extension_f = s3_coefficients(
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
        *control_extension_inputs,
    )
    control_extension_discriminant = (
        control_extension_f[1] ** 2
        - 4 * control_extension_f[0] * control_extension_f[2]
    ) % CONTROL_P
    control_extension_matrix = sylvester_2_2(
        control_extension_f, control_extension_f
    )
    control_extension_resultant = (
        determinant_integer(control_extension_matrix) % CONTROL_P
    )
    control_extension_target = scalar_mul(
        EXTENSION_TARGET_SCALAR,
        base,
        CONTROL_P,
        CONTROL_CURVE_A,
        CONTROL_CURVE_B,
    )
    if control_extension_target is None:
        raise AssertionError("control extension target is identity")
    control_extension_leaf_x = [
        1,
        CONTROL_P - 1,
        1,
        CONTROL_P - 1,
        *([base[0]] * (M - 4)),
    ]
    if (
        control_extension_f != [4, CONTROL_P - 28, 1]
        or control_extension_discriminant != 768
        or legendre_symbol(control_extension_discriminant, CONTROL_P) != -1
        or legendre_symbol(8, CONTROL_P) != -1
        or legendre_symbol(6, CONTROL_P) != 1
        or control_extension_resultant != 0
        or len(control_extension_leaf_x) != M
        or any(
            value == 0 or pow(value, D, CONTROL_P) != 1
            for value in [
                *control_extension_leaf_x,
                control_extension_target[0],
            ]
        )
    ):
        raise AssertionError("same-parameter extension fiber witness failed")

    internal_variables = [f"u_{index}" for index in range(2, M)]
    recursive_equations = ["S3(x_1, x_2, u_2) = 0"]
    recursive_equations.extend(
        f"S3(u_{index - 1}, x_{index}, u_{index}) = 0"
        for index in range(3, M)
    )
    recursive_equations.append("S3(u_15, x_16, x_target) = 0")

    return {
        "artifact_id": "PKC-SMOOTH-M16-SEMANTIC-BRIDGE-001",
        "conditional_bridge": {
            "affine_left_fold_exact_domain": [
                "every leaf x-coordinate has an F_p curve lift",
                "for the fixed leaf order, a sign assignment exists whose prefix sums of sizes 2 through 15 are not the identity",
                "every internal u_k is the x-coordinate of the corresponding finite prefix sum",
                "distinct-input S3 roots use the proved chord iff semantics",
                "repeated-input S3 roots use the localized tangent identity with 4*y^2 nonzero",
                "the final recovered signed curve relation is checked exactly",
            ],
            "forward": (
                "A signed relation with all fixed-order prefixes finite projects "
                "to the affine left-fold S3 equations."
            ),
            "reverse": (
                "After exact base-field lift and local-root recovery, an affine "
                "left-fold solution glues to a signed curve relation."
            ),
            "missing_global_stratum": (
                "If a required prefix sum is the identity, it has no affine "
                "x-coordinate. The repeated-x S3 slice retains only the tangent "
                "branch, so a pure affine u_k chain is not globally complete."
            ),
            "status": "exact_only_after_nonidentity_localization",
        },
        "control_field_m16_counterexample": {
            "curve": {
                "a": CONTROL_CURVE_A,
                "b": CONTROL_CURVE_B,
                "discriminant_mod_p": curve_discriminant(
                    CONTROL_P, CONTROL_CURVE_A, CONTROL_CURVE_B
                ),
                "equation": "y^2 = x^3 + 7",
                "order": CONTROL_CURVE_ORDER,
                "order_factorization": list(CONTROL_CURVE_ORDER_FACTORS),
                "rational_two_torsion_x": two_torsion_x,
            },
            "direct_relation_witness": {
                "leaf_scalars": [
                    REPEATED_SCALAR,
                    REPEATED_SCALAR,
                    *([BASE_SCALAR] * (M - 2)),
                ],
                "leaf_signs": [1, -1, *([1] * (M - 2))],
                "signed_scalar_sum_before_target": TARGET_SCALAR,
                "target_scalar": TARGET_SCALAR,
                "target_sign": -1,
                "verified_group_sum": "identity",
                "scope": (
                    "Exact intended signed-point relation semantics. S17 is "
                    "not expanded or evaluated in this certificate."
                ),
            },
            "field": {
                "D": D,
                "factor_chain": list(FACTOR_CHAIN),
                "multiplicative_group_order": D,
                "p": CONTROL_P,
                "p_equals_D_plus_one": True,
                "p_is_prime": True,
                "source_root_set": "H = F_p^*",
            },
            "membership_checks": {
                "all_witness_x_nonzero": True,
                "base_x_to_D": pow(base[0], D, CONTROL_P),
                "doubled_repeated_x_to_D": pow(
                    doubled_repeated[0], D, CONTROL_P
                ),
                "repeated_x_to_D": pow(repeated[0], D, CONTROL_P),
                "target_x_to_D": pow(target[0], D, CONTROL_P),
            },
            "points": {
                "base_P": point_record(base),
                "doubled_repeated_100P": point_record(doubled_repeated),
                "repeated_50P": point_record(repeated),
                "seed_T": point_record(CONTROL_SEED),
                "target_14P": point_record(target),
            },
            "recursive_affine_obstruction": {
                "checked_layer_indexed_parent_occurrences": checked_parents,
                "checked_layer_indexed_root_evaluations": checked_roots,
                "first_slice_coefficients_z2_z1_z0": repeated_coefficients,
                "first_slice_unique_root": repeated_root,
                "first_state_modulo_global_sign": (
                    DOUBLED_REPEATED_SCALAR
                ),
                "reachable_scalar_classes_after_each_base_leaf": layers,
                "target_scalar_class": target_class,
                "terminal_intersection_with_target": sorted(
                    set(terminal_states) & {target_class}
                ),
                "terminal_scalar_classes": terminal_states,
                "unique_parent_scalar_classes": len(
                    set().union(*(set(layer) for layer in layers[:-1]))
                ),
                "root_evaluations_for_unique_parent_classes": (
                    2
                    * len(
                        set().union(
                            *(set(layer) for layer in layers[:-1])
                        )
                    )
                ),
            },
            "scope": (
                "This is a fixed labeled-topology structural witness at the "
                "same m, D, source factor chain, and exact x^D=1 membership "
                "layer. It is not the secp256k1 target field and makes no "
                "attack-cost claim."
            ),
            "subgroup": {
                "base_construction": "P = [163]T",
                "base_scalar": BASE_SCALAR,
                "cofactor": CONTROL_COFACTOR,
                "order": CONTROL_SUBGROUP_ORDER,
                "order_is_prime": True,
                "verified_order_multiple": "[3463]P = identity",
            },
        },
        "extension_field_membership_witness": {
            "curve": {
                "a": EXTENSION_CURVE_A,
                "b": EXTENSION_CURVE_B,
                "discriminant_nonzero": (
                    curve_discriminant(
                        EXTENSION_P,
                        EXTENSION_CURVE_A,
                        EXTENSION_CURVE_B,
                    )
                    != 0
                ),
                "equation": "y^2 = x^3 + 2 over F_5",
                "liftability": extension_lifts,
            },
            "field": {
                "D": D,
                "D_mod_multiplicative_group_order": D % (EXTENSION_P - 1),
                "characteristic_greater_than_three": True,
                "gcd_D_multiplicative_group_order": math.gcd(
                    D, EXTENSION_P - 1
                ),
                "membership_equation": "x^564522 = 1",
                "membership_roots": extension_membership_roots,
                "p": EXTENSION_P,
            },
            "meaning": (
                "The exact x^D=1 membership layer admits x=1 even though "
                "x=1 has no F_5 curve lift. The two identical "
                "S3(1,4,z) slices share roots over F_25 but have no root "
                "in F_5, so base-field liftability and extension-only "
                "fibers require separate recovery checks."
            ),
            "s3_slice": {
                "base_field_roots": extension_roots,
                "coefficients_z2_z1_z0": extension_f,
                "discriminant": extension_discriminant,
                "fixed_size_self_resultant": extension_resultant,
                "inputs": list(EXTENSION_INPUTS),
                "quadratic_residues": sorted(
                    {value * value % EXTENSION_P for value in range(EXTENSION_P)}
                ),
                "s4_coordinates": [1, 4, 1, 4],
                "sylvester_matrix": extension_matrix,
            },
            "scope": (
                "Exact membership-layer and resultant-fiber witness only; "
                "it is not an on-curve signed relation."
            ),
        },
        "control_field_extension_fiber_witness": {
            "direct_extension_relation": {
                "cancellation_pairs": [
                    "the two x=1 leaves use opposite F_(p^2) lifts",
                    "the two x=-1 leaves use opposite F_p lifts",
                ],
                "remaining_leaf_points": "twelve copies of P",
                "semantic_sum": (
                    "two opposite-lift pairs cancel and twelve P sum to R"
                ),
                "target_point": point_record(control_extension_target),
                "target_scalar": EXTENSION_TARGET_SCALAR,
            },
            "field_and_membership": {
                "D": D,
                "all_leaf_and_target_x_to_D": True,
                "leaf_x_coordinates": control_extension_leaf_x,
                "p": CONTROL_P,
                "source_root_set": "H = F_p^*",
                "target_x": control_extension_target[0],
            },
            "first_affine_slice": {
                "base_field_roots": [],
                "coefficients_z2_z1_z0": control_extension_f,
                "discriminant": control_extension_discriminant,
                "discriminant_legendre_symbol": legendre_symbol(
                    control_extension_discriminant, CONTROL_P
                ),
                "fixed_size_self_resultant": control_extension_resultant,
                "inputs": list(control_extension_inputs),
                "sylvester_matrix": control_extension_matrix,
            },
            "liftability": [
                {
                    "legendre_symbol": legendre_symbol(8, CONTROL_P),
                    "rhs": 8,
                    "status": "extension_only",
                    "x": 1,
                },
                {
                    "legendre_symbol": legendre_symbol(6, CONTROL_P),
                    "rhs": 6,
                    "status": "base_field_lift",
                    "x": CONTROL_P - 1,
                    "y_roots": [163_761, 400_762],
                },
            ],
            "meaning": (
                "At the exact m, D, control field, factor chain, and "
                "membership layer, the direct algebraic signed relation "
                "exists over F_(p^2), while the first affine recursive "
                "equation has no F_p root."
            ),
            "scope": (
                "Recovery rejects this tuple because x=1 has no F_p lift. "
                "This is a base-field recursive-recovery semantics blocker, "
                "not a usable base-field relation and not an S17 evaluation."
            ),
        },
        "kind": "deterministic_nonexperimental_semantic_counterexample",
        "local_s3_semantics": {
            "distinct_inputs": {
                "source_theorem": (
                    "Ecdlp.Semaev.secp256k1_semaev_three_iff"
                ),
                "meaning": (
                    "For lifted inputs with x1 != x2, the two roots are the "
                    "x-coordinates of the sum and difference."
                ),
            },
            "identity_branch": {
                "condition": "the two lifted points are negatives",
                "affine_parent": None,
                "consequence": (
                    "The identity has no affine x-coordinate and cannot be "
                    "stored in u_k."
                ),
            },
            "repeated_inputs": {
                "cleared_doubling_identity": (
                    "4*y^2*x(2P) = x^4 - 56*x"
                ),
                "localization": "4*y^2 != 0",
                "specialization": (
                    "S3(x,x,z) = -4*y^2 * (z - x(2P))"
                ),
                "unique_affine_root": "x(2P)",
            },
        },
        "m16_presentation_contract": {
            "direct_relation": {
                "polynomial": "S_17(x_1,...,x_16,x_target)",
                "polynomial_materialized": False,
                "semantic_target": (
                    "there exist signs epsilon_i and epsilon_target in "
                    "{-1,+1} with sum epsilon_i*P_i + "
                    "epsilon_target*R = identity"
                ),
            },
            "membership": {
                "artifact": M16_DESK_ARTIFACT,
                "artifact_sha256": M16_DESK_SHA256,
                "circuit_gate_count_per_coordinate": 24,
                "equation": "x_i^564522 = 1",
                "status": "exact_pointwise",
            },
            "recursive_affine_left_fold": {
                "equation_count": M - 1,
                "equations": recursive_equations,
                "internal_variable_count": M - 2,
                "internal_variables": internal_variables,
                "leaf_variable_count": M,
                "projection": (
                    "drop u_2,...,u_15 and every membership-circuit auxiliary"
                ),
                "target_x": "fixed constant",
                "variable_order": [
                    *[f"x_{index}" for index in range(1, M + 1)],
                    *internal_variables,
                    "membership auxiliaries in coordinate-major gate order",
                ],
            },
        },
        "recovery_contract": {
            "acceptance": [
                "lift every leaf x_i in F_p and reject non-lifts",
                "enumerate or meet-in-the-middle the 2^15 relative sign classes",
                "combine duplicate signed points before emitting a relation row",
                "canonicalize coordinate permutations so they do not count as independent relations",
                "if Q=eta*phi^j(P0), map an occurrence epsilon*Q to coefficient epsilon*eta*lambda^j modulo n only under the proved eigenvalue and full-group membership theorems",
                "verify the full elliptic-curve relation and target coefficient exactly",
            ],
            "canonical_relation_row": {
                "duplicate_aggregation": (
                    "sum all signed occurrences of the same recovered point "
                    "before GLV projection"
                ),
                "final_verification": (
                    "reconstruct the normalized sparse row on the curve and "
                    "verify that its exact group sum is the identity"
                ),
                "status": "required_before_rank_accounting",
                "steps": [
                    "ordered lifted leaf tuple",
                    "exact signed point tuple with target",
                    "duplicate-aggregated point row",
                    "GLV-normalized sparse coefficient row",
                    "exact curve re-verification",
                ],
                "target_normalization": (
                    "use global sign to set the target coefficient to -1; "
                    "accept exactly when the signed leaf sum equals R"
                ),
            },
            "direct_sign_search": {
                "meet_in_the_middle_list_sizes": [128, 256],
                "raw_assignments": 65_536,
                "relative_classes": 32_768,
            },
            "glv_normalization": {
                "coefficient_rule": (
                    "if Q=eta*phi^j(P0), an occurrence epsilon*Q "
                    "contributes epsilon*eta*lambda^j modulo n to P0"
                ),
                "eigenvalue_theorem": (
                    "Ecdlp.Curve."
                    "secp256k1_glvPoint_eq_lam_on_zmultiples"
                ),
                "full_group_membership_path": (
                    "Ecdlp/Proved/CurveFullGroup.lean"
                ),
                "full_group_membership_theorem": (
                    "Ecdlp.Curve.secp256k1_mem_zmultiples"
                ),
                "orbit_path": "Ecdlp/Proved/GlvOrbit.lean",
                "representative_rule": (
                    "choose the minimum canonical encoding modulo point sign "
                    "among P, phi(P), and phi^2(P), and retain eta in "
                    "Q=eta*phi^j(P0)"
                ),
                "status": "future_requirement_not_replayed",
                "subgroup_eigenvalue_path": (
                    "Ecdlp/Proved/GlvSubgroupEigenvalue.lean"
                ),
            },
            "identity_prefix_policy": (
                "Direct leaf-point recovery may accept an identity prefix, but "
                "the affine recursive presentation cannot use it as u_k. Such "
                "rows belong to a separate projective/identity stratum."
            ),
            "multiplicity_policy": (
                "Repeated coordinates, opposite signs, permutations, and GLV "
                "orbit aliases are canonicalized before rank accounting."
            ),
            "ordered_tree_dynamic_program": {
                "backpointers": (
                    "retain child-state backpointers and exact multiplicities "
                    "for every surviving parent state"
                ),
                "identity_state": (
                    "route A+B=identity to the named non-affine stratum; "
                    "do not encode it as an affine u_k"
                ),
                "leaf_states": (
                    "{P_i,-P_i} after exact F_p lift; reject an empty lift set"
                ),
                "parent_transition": (
                    "form every exact A+B, retain it only when nonidentity "
                    "and x(A+B) equals the supplied internal coordinate"
                ),
                "root_acceptance": (
                    "accept exactly the surviving root states R or -R, then "
                    "apply target normalization"
                ),
                "state_bound_per_supplied_x": 2,
            },
            "permutation_accounting": {
                "direct_coordinate_orbit_count": (
                    "16! / product_x multiplicity(x)!"
                ),
                "levels": [
                    "ordered leaf tuple and fixed tree topology",
                    "sorted coordinate multiset",
                    "normalized sparse GLV row",
                ],
                "recursive_warning": (
                    "permutation admissibility is topology dependent and "
                    "must be replayed rather than inferred from the direct "
                    "coordinate orbit count"
                ),
            },
            "permutation_recovery_audit": recovery_preimage_audit,
            "recursive_solution_policy": (
                "Reject a raw polynomial solution unless every internal value "
                "lifts to the exact recovered finite prefix point and all "
                "local signs glue to the final exact group relation."
            ),
        },
        "schema_version": "1.0",
        "scope": {
            "excluded": [
                "S17 expansion or evaluation at the M16 witness",
                "materialized recursive or membership polynomial system",
                "Sage, msolve, F4, Groebner, or parameter sweep",
                "exact-target secp256k1 relation search",
                "discrete-log computation",
                "solving-degree, rank, runtime, or security claim",
                "hypothesis retention, experiment authorization, or route promotion",
            ],
            "included": [
                "exact finite-field and elliptic-curve arithmetic",
                "source-faithful x^D=1 membership witness at m=16 and D=564522",
                "conditional affine S3 semantic contract",
                "base-field liftability and extension-only resultant fibers",
                "identity-prefix obstruction and recovery requirements",
            ],
        },
        "small_no_rational_two_torsion_resultant_boundary_witness": {
            "curve": {
                "equation": "y^2 = x^3 + 7 over F_13",
                "p": SMALL_P,
                "rational_two_torsion_x": [],
            },
            "direct_signed_points": [
                point_record(SMALL_P_POINT),
                point_record(point_neg(SMALL_P_POINT, SMALL_P)),
                point_record(SMALL_Q_POINT),
                point_record(point_neg(SMALL_Q_POINT, SMALL_P)),
            ],
            "fixed_size_s4_resultant": small_resultant,
            "left_slice_coefficients_z2_z1_z0": small_f,
            "left_slice_roots": small_f_roots,
            "recursive_common_roots": sorted(
                set(small_f_roots) & set(small_g_roots)
            ),
            "right_slice_coefficients_z2_z1_z0": small_g,
            "right_slice_roots": small_g_roots,
            "signed_group_sum": "identity",
            "sylvester_matrix": small_matrix,
            "meaning": (
                "The fixed 2-by-2 S4 resultant vanishes because both padded "
                "quadratic leading coefficients vanish, while the two affine "
                "S3 slices have no common root."
            ),
        },
        "projective_completion_candidate": {
            "affine_restriction": (
                "V != 0 removes the identity root and recovers the "
                "repeated-input affine specialization"
            ),
            "exact_local_identities": {
                "affine_chart": (
                    "S3^h([x1:1],[x2:1],[x3:1]) = S3(x1,x2,x3)"
                ),
                "one_infinity": (
                    "S3^h([X1:Z1],[X2:Z2],[1:0]) = "
                    "(X1*Z2-X2*Z1)^2"
                ),
                "two_infinities": (
                    "S3^h([X1:Z1],[1:0],[1:0]) = Z1^2"
                ),
            },
            "homogeneous_polynomial": (
                "X1^2*X2^2*Z3^2 + X1^2*Z2^2*X3^2 + "
                "Z1^2*X2^2*X3^2 - 2*X1^2*X2*Z2*X3*Z3 - "
                "2*X1*Z1*X2^2*X3*Z3 - "
                "2*X1*Z1*X2*Z2*X3^2 - "
                "28*(X1*Z1*Z2^2*Z3^2 + "
                "Z1^2*X2*Z2*Z3^2 + Z1^2*Z2^2*X3*Z3)"
            ),
            "kummer_coordinate": {
                "affine_point": "[x(P):1]",
                "identity": "[1:0]",
            },
            "repeated_input_homogeneous_slice": (
                "S3^h(x,x;U,V) = V * "
                "(-4*y^2*U + (x^4 - 56*x)*V)"
            ),
            "root_meanings": [
                "[1:0] is the identity branch",
                "[x(2P):1] is the tangent branch",
            ],
            "status": "next_task_requires_independent_proof",
            "saturation_policy": (
                "exclude only projective zero coordinates [0:0]; do not "
                "saturate by coordinate differences because tangent and "
                "duplicate strata are valid"
            ),
            "tree_bridge_candidate": (
                "the affine tree is the homogeneous projective tree "
                "localized to nonidentity tree-cut partial sums"
            ),
            "warning": (
                "This candidate is not used as a proved global bridge in "
                "the current terminal disposition."
            ),
        },
        "source_scope": {
            "curve_full_group": "Ecdlp/Proved/CurveFullGroup.lean",
            "glv_eigenvalue": "Ecdlp/Proved/GlvSubgroupEigenvalue.lean",
            "glv_orbit": "Ecdlp/Proved/GlvOrbit.lean",
            "m16_desk_artifact": M16_DESK_ARTIFACT,
            "m16_desk_artifact_sha256": M16_DESK_SHA256,
            "primary_claim_extract": (
                "data/source_claim_extracts/petit_kosters_messeng2016.json"
            ),
            "semaev_four": "Ecdlp/Proved/SemaevFour.lean",
            "semaev_three": "Ecdlp/Proved/SemaevThree.lean",
            "source_claim_ids": [
                "SC-GLV-ENDOMORPHISM",
                "SC-GLV-ENDOMORPHISM-NONTRIVIAL",
                "SC-PKC-SMOOTH-SUBGROUP",
                "SC-SECP-NO-TWO-TORSION",
                "SC-SEMAEV-RELATION-SEMANTICS",
                "SC-PKC-M16-SYMBOLIC-DESK-RESULT",
            ],
        },
        "terminal_disposition": {
            "authorization": "none",
            "barrier_effect": "narrowed_open",
            "cell_transition": "open_to_open",
            "cost_quantity_transition": "partial_to_partial",
            "hypothesis_effect": "none",
            "retention_disposition": "zero_retention_success",
            "route_effect": "none",
            "scientific_disposition": "scoped_blocker",
            "source_independence": "not_established",
        },
        "unresolved_fields": [
            "target-field occurrence and frequency of identity-prefix strata",
            "projective or explicitly stratified recursive presentation",
            "distinct-coordinate localization and its relation-yield effect",
            "complete liftability and exceptional-fiber classification",
            "duplicate, permutation, GLV-orbit, and rank multiplicities",
            "direct S17 semantics and recursive projection on every remaining stratum",
            "solving degree, fill-in, preprocessing, sparse linear algebra, and total cost",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()

    artifact_bytes = canonical_bytes(build_artifact())
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    hash_bytes = f"{digest}  artifact.json\n".encode("ascii")

    if args.write:
        ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_PATH.write_bytes(artifact_bytes)
        HASH_PATH.write_bytes(hash_bytes)
        print(
            "wrote "
            + str(ARTIFACT_PATH.relative_to(HERE.parent.parent.parent))
        )
        print(f"sha256 {digest}")
        return 0

    problems: list[str] = []
    try:
        committed_artifact = ARTIFACT_PATH.read_bytes()
    except FileNotFoundError:
        problems.append("artifact.json is missing")
    else:
        if committed_artifact != artifact_bytes:
            problems.append("artifact.json differs from deterministic output")
    try:
        committed_hash = HASH_PATH.read_bytes()
    except FileNotFoundError:
        problems.append("artifact.sha256 is missing")
    else:
        if committed_hash != hash_bytes:
            problems.append("artifact.sha256 differs from deterministic output")
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    print("M16 semantic bridge artifact matches deterministic output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
