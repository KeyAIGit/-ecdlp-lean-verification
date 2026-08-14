#!/usr/bin/env python3
"""Exact C25 audit for sparse-circulant determinant parity symmetries.

The audited family is

    D_(a,b,c)(k) = det(a I + b T + c T^k)
                 = product_{zeta^n=1} (a+b*zeta+c*zeta^k).

All computations use public prime orders, public finite fields, and fixed
coefficient samples. No external point, unknown scalar, wallet, private key, or
production target is accepted.

The replay proves exact S3/Mobius covariance on the finite screens, certifies
all zero-coefficient strata as k-independent in the nondegenerate range,
classifies the three repeated-coefficient stabilizers, and gives a finite
residue-class certificate showing that inversion and k/(k-1) have an
opposite-parity witness of size at most 12 for every prime order n>11.

The remaining fixed-label families are a=b!=c and fully asymmetric
coefficients. A coefficient-permutation-invariant extraction from the full S3
tuple is nevertheless blocked by the same orbit collision.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PATH = ROOT / "archive/untrusted_intake/parity_lift_000/UORC056_SPARSE_TWO_TRANSLATION_RESULTANT_C5.md"
SOURCE_MARKERS = (
    "The unresolved minimal object is",
    "D_(a,b,c)(k)",
    "A degree-`n` resultant, an `n`-dimensional state",
)

SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
    16,
)

SCREEN_ORDERS = (
    5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
    137, 139,
)
PUBLIC_SUBGROUP_ORDERS = (31, 61, 67, 79, 127, 139)
INVERSION_WITNESSES = (2, 3, 4, 5, 7, 8, 9, 10, 11, 12)
RESIDUE_MODULUS = 55_440

COEFFICIENT_SAMPLES = {
    "zero_a": ((0, 1, 2), (0, 2, 5)),
    "zero_b": ((1, 0, 2), (3, 0, 5)),
    "zero_c": ((1, 2, 0), (3, 5, 0)),
    "all_equal": ((1, 1, 1), (2, 2, 2)),
    "a_eq_b": ((1, 1, 2), (2, 2, 5)),
    "a_eq_c": ((1, 2, 1), (2, 5, 2)),
    "b_eq_c": ((2, 1, 1), (5, 2, 2)),
    "fully_asymmetric": ((1, 2, 3), (2, 3, 5), (1, 3, 7)),
}

TRANSFORMS = (
    ("k", (0, 1, 2)),
    ("inverse", (0, 2, 1)),
    ("one_minus", (1, 0, 2)),
    ("inverse_one_minus", (1, 2, 0)),
    ("k_minus_one_over_k", (2, 0, 1)),
    ("k_over_k_minus_one", (2, 1, 0)),
)


def is_prime(value: int) -> bool:
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


def prime_factors(value: int) -> tuple[int, ...]:
    factors: list[int] = []
    divisor = 2
    remaining = value
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            factors.append(divisor)
            while remaining % divisor == 0:
                remaining //= divisor
        divisor += 1 if divisor == 2 else 2
    if remaining > 1:
        factors.append(remaining)
    return tuple(factors)


def primitive_root(prime: int) -> int:
    factors = prime_factors(prime - 1)
    for candidate in range(2, prime):
        if all(pow(candidate, (prime - 1) // factor, prime) != 1 for factor in factors):
            return candidate
    raise AssertionError(f"no primitive root modulo {prime}")


def screen_field(order: int) -> tuple[int, int]:
    multiplier = 1
    while True:
        prime = multiplier * order + 1
        if is_prime(prime):
            generator = primitive_root(prime)
            root = pow(generator, (prime - 1) // order, prime)
            if pow(root, order, prime) != 1:
                raise AssertionError("root does not have order dividing n")
            if any(pow(root, order // factor, prime) == 1 for factor in prime_factors(order)):
                raise AssertionError("root order is smaller than n")
            return prime, root
        multiplier += 1


def mobius_images(order: int, scalar: int) -> dict[str, int]:
    if not (1 < scalar < order):
        raise ValueError("the nondegenerate cross-ratio range is 1<k<n")
    inverse = pow(scalar, -1, order)
    one_minus = (1 - scalar) % order
    return {
        "k": scalar,
        "inverse": inverse,
        "one_minus": one_minus,
        "inverse_one_minus": pow(one_minus, -1, order),
        "k_minus_one_over_k": (scalar - 1) * inverse % order,
        "k_over_k_minus_one": scalar * pow(scalar - 1, -1, order) % order,
    }


def permute_coefficients(coefficients: tuple[int, int, int],
                         permutation: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(coefficients[index] for index in permutation)  # type: ignore[return-value]


class DeterminantContext:
    def __init__(self, order: int):
        self.order = order
        self.prime, self.root = screen_field(order)
        self.roots = [pow(self.root, exponent, self.prime) for exponent in range(order)]
        self.cache: dict[tuple[tuple[int, int, int], int], int] = {}

    def value(self, coefficients: tuple[int, int, int], scalar: int) -> int:
        reduced = tuple(value % self.prime for value in coefficients)
        key = (reduced, scalar)
        if key in self.cache:
            return self.cache[key]
        a, b, c = reduced
        product = 1
        for exponent, root_value in enumerate(self.roots):
            factor = (
                a
                + b * root_value
                + c * self.roots[(exponent * scalar) % self.order]
            ) % self.prime
            product = product * factor % self.prime
        self.cache[key] = product
        return product

    def coefficient_orbit_multiset(
        self, coefficients: tuple[int, int, int], scalar: int
    ) -> tuple[int, ...]:
        permutations = {permutation for _, permutation in TRANSFORMS}
        return tuple(sorted(
            self.value(permute_coefficients(coefficients, permutation), scalar)
            for permutation in permutations
        ))


def first_inverse_parity_witness(order: int) -> tuple[int, int] | None:
    for scalar in INVERSION_WITNESSES:
        if scalar >= order:
            continue
        inverse = pow(scalar, -1, order)
        if scalar % 2 != inverse % 2:
            return scalar, inverse
    return None


def residue_certificate() -> dict[str, object]:
    unit_residues = 0
    stable_inverse_parities = 0
    inversion_witness_frequency: Counter[int] = Counter()
    shifted_witness_frequency: Counter[int] = Counter()
    uncovered: list[int] = []

    for residue in range(1, RESIDUE_MODULUS):
        if math.gcd(residue, RESIDUE_MODULUS) != 1:
            continue
        unit_residues += 1
        representative = residue + RESIDUE_MODULUS
        second_representative = representative + RESIDUE_MODULUS
        selected: tuple[int, int] | None = None
        for scalar in INVERSION_WITNESSES:
            inverse = pow(scalar, -1, representative)
            second_inverse = pow(scalar, -1, second_representative)
            if inverse % 2 != second_inverse % 2:
                raise AssertionError("inverse parity changed inside one residue class")
            stable_inverse_parities += 1
            if selected is None and scalar % 2 != inverse % 2:
                selected = scalar, inverse
        if selected is None:
            uncovered.append(residue)
            continue
        scalar, inverse = selected
        inversion_witness_frequency[scalar] += 1

        shifted_scalar = scalar + 1
        shifted_image = (
            shifted_scalar * pow(shifted_scalar - 1, -1, representative)
        ) % representative
        expected_shifted_image = (1 + inverse) % representative
        if shifted_image != expected_shifted_image:
            raise AssertionError("k/(k-1) is not one plus the inverse of k-1")
        if shifted_scalar % 2 == shifted_image % 2:
            raise AssertionError("shifted Mobius witness did not flip parity")
        shifted_witness_frequency[shifted_scalar] += 1

    if uncovered:
        raise AssertionError(f"uncovered invertible residue classes: {uncovered[:10]}")
    if unit_residues != 11_520:
        raise AssertionError(f"unexpected unit residue count: {unit_residues}")

    small_prime_exceptions = {}
    for order in (3, 5, 7, 11):
        witness = first_inverse_parity_witness(order)
        small_prime_exceptions[str(order)] = (
            None if witness is None else [witness[0], witness[1]]
        )

    return {
        "modulus": RESIDUE_MODULUS,
        "unit_residues": unit_residues,
        "witness_scalars": list(INVERSION_WITNESSES),
        "stable_inverse_parity_checks": stable_inverse_parities,
        "all_unit_residues_covered": True,
        "inversion_witness_frequency": {
            str(key): value for key, value in sorted(inversion_witness_frequency.items())
        },
        "shifted_k_over_k_minus_one_witness_frequency": {
            str(key): value for key, value in sorted(shifted_witness_frequency.items())
        },
        "prime_order_consequence": (
            "every prime n>11 is coprime to 55440 and has an opposite-parity "
            "inversion witness j<=12; k=j+1 gives the corresponding "
            "k/(k-1) witness"
        ),
        "small_prime_exceptions": small_prime_exceptions,
        "only_prime_without_a_screened_inversion_witness": 7,
    }


def parity_decodable_from_exact_values(
    context: DeterminantContext, coefficients: tuple[int, int, int]
) -> bool:
    observed: dict[int, int] = {}
    for scalar in range(2, context.order):
        value = context.value(coefficients, scalar)
        parity = scalar % 2
        if value in observed and observed[value] != parity:
            return False
        observed[value] = parity
    return True


def quadratic_character(value: int, prime: int) -> int:
    if value % prime == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    return -1 if result == prime - 1 else result


def parity_decodable_from_character(
    context: DeterminantContext, coefficients: tuple[int, int, int]
) -> bool:
    observed: dict[int, int] = {}
    for scalar in range(2, context.order):
        character = quadratic_character(context.value(coefficients, scalar), context.prime)
        parity = scalar % 2
        if character in observed and observed[character] != parity:
            return False
        observed[character] = parity
    return True


def screen_order(order: int) -> dict[str, object]:
    context = DeterminantContext(order)
    symmetry_checks = 0
    one_minus_parity_checks = 0
    zero_independence_checks = 0
    repeated_opposite_parity_collisions = 0
    symmetric_extraction_collisions = 0
    finite_exact_value_possible: list[str] = []
    finite_character_possible: list[str] = []

    flattened_samples = [
        (stratum, coefficients)
        for stratum, samples in COEFFICIENT_SAMPLES.items()
        for coefficients in samples
    ]

    for stratum, coefficients in flattened_samples:
        for scalar in range(2, order):
            images = mobius_images(order, scalar)
            base = context.value(coefficients, scalar)
            for name, permutation in TRANSFORMS:
                transformed_coefficients = permute_coefficients(coefficients, permutation)
                transformed_scalar = images[name]
                transformed = context.value(
                    transformed_coefficients, transformed_scalar
                )
                if transformed != base:
                    raise AssertionError(
                        f"S3 covariance failed n={order} coeff={coefficients} "
                        f"k={scalar} transform={name}"
                    )
                symmetry_checks += 1

            canonical_one_minus = images["one_minus"]
            if canonical_one_minus != order + 1 - scalar:
                raise AssertionError("wrong canonical representative of 1-k")
            if canonical_one_minus % 2 != scalar % 2:
                raise AssertionError("1-k changed parity for odd order")
            one_minus_parity_checks += 1

        if stratum.startswith("zero_"):
            values = {
                context.value(coefficients, scalar)
                for scalar in range(2, order)
            }
            if len(values) != 1:
                raise AssertionError(
                    f"zero-coefficient stratum depends on k: n={order}, {coefficients}"
                )
            zero_independence_checks += order - 2

        label = f"{stratum}:{coefficients}"
        if parity_decodable_from_exact_values(context, coefficients):
            finite_exact_value_possible.append(label)
        if parity_decodable_from_character(context, coefficients):
            finite_character_possible.append(label)

    witness = first_inverse_parity_witness(order)
    repeated_status: dict[str, object]
    if witness is None:
        repeated_status = {
            "inversion_witness": None,
            "b_eq_c_blocked_by_stabilizer": False,
            "a_eq_c_blocked_by_stabilizer": False,
            "all_equal_blocked_by_stabilizer": False,
        }
    else:
        scalar, inverse = witness
        if scalar % 2 == inverse % 2:
            raise AssertionError("stored inversion witness has equal parity")
        shifted_scalar = scalar + 1
        shifted_image = mobius_images(order, shifted_scalar)["k_over_k_minus_one"]
        if shifted_scalar % 2 == shifted_image % 2:
            raise AssertionError("shifted repeated-coefficient witness has equal parity")

        for coefficients in COEFFICIENT_SAMPLES["b_eq_c"]:
            if context.value(coefficients, scalar) != context.value(coefficients, inverse):
                raise AssertionError("b=c inversion collision failed")
            repeated_opposite_parity_collisions += 1
        for coefficients in COEFFICIENT_SAMPLES["a_eq_c"]:
            if context.value(coefficients, shifted_scalar) != context.value(
                coefficients, shifted_image
            ):
                raise AssertionError("a=c k/(k-1) collision failed")
            repeated_opposite_parity_collisions += 1
        for coefficients in COEFFICIENT_SAMPLES["all_equal"]:
            if context.value(coefficients, scalar) != context.value(coefficients, inverse):
                raise AssertionError("all-equal inversion collision failed")
            repeated_opposite_parity_collisions += 1

        for coefficients in COEFFICIENT_SAMPLES["fully_asymmetric"]:
            left = context.coefficient_orbit_multiset(coefficients, scalar)
            right = context.coefficient_orbit_multiset(coefficients, inverse)
            if left != right:
                raise AssertionError("coefficient-symmetric S3 extraction changed orbit")
            symmetric_extraction_collisions += 1

        repeated_status = {
            "inversion_witness": [scalar, inverse],
            "shifted_k_over_k_minus_one_witness": [
                shifted_scalar, shifted_image
            ],
            "b_eq_c_blocked_by_stabilizer": True,
            "a_eq_c_blocked_by_stabilizer": True,
            "all_equal_blocked_by_stabilizer": True,
        }

    for coefficients in COEFFICIENT_SAMPLES["a_eq_b"]:
        for scalar in range(2, order):
            image = mobius_images(order, scalar)["one_minus"]
            if context.value(coefficients, scalar) != context.value(coefficients, image):
                raise AssertionError("a=b one-minus collision failed")
            if scalar % 2 != image % 2:
                raise AssertionError("a=b stabilizer unexpectedly flipped parity")

    return {
        "n": order,
        "screen_field": context.prime,
        "nth_root": context.root,
        "symmetry_checks": symmetry_checks,
        "one_minus_parity_checks": one_minus_parity_checks,
        "zero_independence_checks": zero_independence_checks,
        "repeated_opposite_parity_collisions": (
            repeated_opposite_parity_collisions
        ),
        "coefficient_symmetric_extraction_collisions": (
            symmetric_extraction_collisions
        ),
        "repeated_status": repeated_status,
        "a_eq_b_stabilizer": {
            "transform": "k -> 1-k mod n, canonical n+1-k",
            "parity_preserving": True,
            "blocked_by_stabilizer_alone": False,
        },
        "finite_exact_value_decoder_possible_samples": (
            finite_exact_value_possible
        ),
        "finite_quadratic_character_decoder_possible_samples": (
            finite_character_possible
        ),
        "finite_screen_is_not_asymptotic_proof": True,
    }


def secp_certificate() -> dict[str, object]:
    witness = first_inverse_parity_witness(SECP_N)
    if witness is None:
        raise AssertionError("secp256k1 order lacks the residue witness")
    scalar, inverse = witness
    shifted_scalar = scalar + 1
    shifted_image = (
        shifted_scalar * pow(shifted_scalar - 1, -1, SECP_N)
    ) % SECP_N
    if scalar % 2 == inverse % 2:
        raise AssertionError("secp inversion witness did not flip parity")
    if shifted_scalar % 2 == shifted_image % 2:
        raise AssertionError("secp shifted witness did not flip parity")
    return {
        "n": str(SECP_N),
        "n_mod_4": SECP_N % 4,
        "n_coprime_to_residue_modulus": math.gcd(SECP_N, RESIDUE_MODULUS) == 1,
        "b_eq_c_inversion_witness": [scalar, str(inverse)],
        "a_eq_c_k_over_k_minus_one_witness": [
            shifted_scalar, str(shifted_image)
        ],
        "zero_coefficient_strata_blocked": True,
        "b_eq_c_stratum_blocked": True,
        "a_eq_c_stratum_blocked": True,
        "all_equal_stratum_blocked": True,
        "a_eq_b_stratum_blocked_by_stabilizer": False,
        "coefficient_symmetric_full_S3_extraction_blocked": True,
        "fully_asymmetric_fixed_label_extraction_blocked": False,
        "explicit_regular_representation_dimension": str(SECP_N),
        "explicit_root_product_terms": str(SECP_N),
        "sublinear_public_Q_operator_realization_found": False,
    }


def source_certificate() -> dict[str, object]:
    if not SOURCE_PATH.is_file():
        raise AssertionError(f"missing source artifact: {SOURCE_PATH}")
    raw = SOURCE_PATH.read_bytes()
    normalized = " ".join(raw.decode("utf-8").split())
    missing = [
        marker for marker in SOURCE_MARKERS
        if " ".join(marker.split()) not in normalized
    ]
    if missing:
        raise AssertionError(f"source markers missing: {missing}")
    return {
        "path": str(SOURCE_PATH.relative_to(ROOT)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "markers_verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    residue = residue_certificate()
    screens = [screen_order(order) for order in SCREEN_ORDERS]

    aggregate = {
        "screen_orders": len(screens),
        "public_subgroup_orders_included": all(
            order in SCREEN_ORDERS for order in PUBLIC_SUBGROUP_ORDERS
        ),
        "full_S3_Mobius_action_verified": True,
        "S3_covariance_checks": sum(row["symmetry_checks"] for row in screens),
        "one_minus_parity_checks": sum(
            row["one_minus_parity_checks"] for row in screens
        ),
        "zero_coefficient_independence_checks": sum(
            row["zero_independence_checks"] for row in screens
        ),
        "repeated_opposite_parity_collisions": sum(
            row["repeated_opposite_parity_collisions"] for row in screens
        ),
        "coefficient_symmetric_extraction_collisions": sum(
            row["coefficient_symmetric_extraction_collisions"] for row in screens
        ),
        "all_zero_coefficient_strata_blocked": True,
        "all_repeated_coefficient_strata_classified": True,
        "b_eq_c_blocked_for_all_primes_gt_11": True,
        "a_eq_c_blocked_for_all_primes_gt_11": True,
        "all_equal_blocked_for_all_primes_gt_11": True,
        "a_eq_b_stabilizer_parity_preserving": True,
        "a_eq_b_repeated_stratum_fully_blocked": False,
        "coefficient_symmetric_extraction_blocked_for_all_primes_gt_11": True,
        "fully_asymmetric_parity_collision_proved": False,
        "finite_exception_n7_retained": True,
        "sublinear_sparse_resultant_representation_found": False,
        "linear_regular_representation_public_Q_realization_known": True,
        "sublinear_public_Q_operator_realization_found": False,
        "exact_parity_extraction_found": False,
        "exact_Hilbert90_branch_bridge_found": False,
        "complete_cost_gate_passed": False,
        "compact_branch_odd_evaluator_found": False,
        "sub_sqrt_evaluator_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }

    payload = {
        "experiment": "SPARSE-CIRCULANT-PARITY-CLASSIFICATION-C25",
        "source_certificate": source_certificate(),
        "transform_table": [
            {"name": name, "coefficient_permutation": list(permutation)}
            for name, permutation in TRANSFORMS
        ],
        "residue_certificate": residue,
        "screens": screens,
        "secp256k1": secp_certificate(),
        "scope": {
            "proved_or_certified": [
                "exact finite-field S3 covariance on all screens",
                "zero-coefficient k-independence for 2<=k<n",
                "opposite-parity stabilizer collision for b=c and a=c for every prime n>11",
                "all-equal repeated stratum collision for every prime n>11",
                "coefficient-permutation-invariant full-S3 extraction collision for every prime n>11",
                "a=b stabilizer k->1-k preserves parity",
            ],
            "not_proved": [
                "a parity collision for every fixed-label a=b family",
                "a parity collision for every fully asymmetric fixed-label family",
                "an unrestricted sparse-resultant lower bound",
                "a sublinear public-Q realization",
                "a Hilbert90 branch bridge",
            ],
        },
        "aggregate": aggregate,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(raw.encode()).hexdigest()
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
