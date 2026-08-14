#!/usr/bin/env python3
"""C26 audit for fixed-label asymmetric sparse resultants.

This package uses only public prime orders, deterministic finite fields,
committed source artifacts, fixed small coefficient families, and public
secp256k1 constants. It accepts no external point, unknown scalar, wallet,
private key, production target, user-supplied branch value, or hidden scalar
index as an algorithmic input.

The audit has three independent parts:

1. classify nonzero projective S3 stabilizers and verify the cubic eigenline
   `(1, omega, omega^2)`;
2. block every scale-invariant extraction, in particular the quadratic
   character, on that projective family by an opposite-parity order-three
   Mobius orbit collision;
3. certify a worst-case linear reduced degree for every grammar that chooses
   one of the six S3/Mobius representatives and then materializes the resulting
   sparse polynomial.

A separate discovery/held-out screen tests fixed small `a=b!=c` and pairwise
asymmetric coefficient families under exact-value, zero/nonzero, bounded
multiplicative-character, and bounded-ratio extraction grammars. Those screens
are evidence only, not unrestricted impossibility theorems.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
    16,
)

SOURCE_PATHS = (
    Path("archive/untrusted_intake/parity_lift_000/UORC056_SPARSE_CIRCULANT_PARITY_C25.md"),
    Path("experiments/parity_lift_000/uorc056_sparse_circulant_symmetry.py"),
)
SOURCE_MARKERS = {
    SOURCE_PATHS[0]: (
        "full six-element affine/Mobius action",
        "ASYMMETRIC-SPARSE-RESULTANT-EVALUATION-075",
    ),
    SOURCE_PATHS[1]: (
        "SPARSE-CIRCULANT-PARITY-CLASSIFICATION-C25",
        "RESIDUE_MODULUS = 55_440",
    ),
}

PROJECTIVE_ORDERS = (
    13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139,
)
DEGREE_SCREEN_ORDERS = (
    5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
    67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
    137, 139,
)
DISCOVERY_ORDERS = (13, 17, 19, 23, 29, 31, 37, 41)
HELD_OUT_ORDERS = (43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97)
CHARACTER_ORDERS = (2, 3, 4, 5, 6, 8, 10, 12)

SMALL_VALUES_A = (-3, -2, -1, 1, 2, 3)
SMALL_VALUES_B = (-2, -1, 1, 2)
LANE_A_COEFFICIENTS = tuple(
    (a, a, c)
    for a in SMALL_VALUES_A
    for c in SMALL_VALUES_A
    if c != a
)
LANE_B_COEFFICIENTS = tuple(itertools.permutations(SMALL_VALUES_B, 3))

VARIANT_LIBRARY = (
    (1, 1, 2), (1, 1, -1), (1, 1, 3),
    (2, 2, 1), (2, 2, 3), (3, 3, 1),
    (1, 2, 3), (1, 2, -1), (1, -1, 2),
    (2, 3, 5), (1, 3, -2), (2, -1, 3),
)


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c25 = load(
    "uorc056_c25_for_c26",
    "uorc056_sparse_circulant_symmetry.py",
)


def source_certificate() -> list[dict[str, Any]]:
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"missing source: {relative}")
        raw = path.read_bytes()
        normalized = " ".join(raw.decode("utf-8").split())
        missing = [
            marker
            for marker in SOURCE_MARKERS[relative]
            if " ".join(marker.split()) not in normalized
        ]
        if missing:
            raise AssertionError(f"source markers missing in {relative}: {missing}")
        rows.append(
            {
                "path": str(relative),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "markers_verified": True,
            }
        )
    return rows


def field_with_n_and_cube_roots(order: int) -> tuple[int, int, int]:
    modulus = math.lcm(order, 3)
    multiplier = 1
    while True:
        prime = multiplier * modulus + 1
        if c25.is_prime(prime):
            generator = c25.primitive_root(prime)
            nth_root = pow(generator, (prime - 1) // order, prime)
            omega = pow(generator, (prime - 1) // 3, prime)
            if pow(nth_root, order, prime) != 1:
                raise AssertionError("bad n-th root")
            if omega == 1 or pow(omega, 3, prime) != 1:
                raise AssertionError("bad primitive cube root")
            return prime, nth_root, omega
        multiplier += 1


class RootProductContext:
    def __init__(self, order: int, prime: int, root: int):
        self.order = order
        self.prime = prime
        self.root = root
        self.roots = [pow(root, exponent, prime) for exponent in range(order)]
        self.cache: dict[tuple[tuple[int, int, int], int], int] = {}

    def value(self, coefficients: tuple[int, int, int], scalar: int) -> int:
        reduced = tuple(value % self.prime for value in coefficients)
        key = (reduced, scalar)
        if key in self.cache:
            return self.cache[key]
        a, b, c = reduced
        product = 1
        for exponent, root_value in enumerate(self.roots):
            product = product * (
                a
                + b * root_value
                + c * self.roots[(exponent * scalar) % self.order]
            ) % self.prime
        self.cache[key] = product
        return product


def quadratic_character(value: int, prime: int) -> int:
    if value % prime == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    return -1 if result == prime - 1 else result


def multiplicative_character(value: int, prime: int, order: int) -> int | None:
    if (prime - 1) % order != 0:
        return None
    if value % prime == 0:
        return 0
    return pow(value, (prime - 1) // order, prime)


def projectively_proportional(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
    prime: int,
) -> tuple[bool, int | None]:
    if left[0] % prime == 0:
        raise AssertionError("normalized first coordinate is zero")
    scale = right[0] * pow(left[0], -1, prime) % prime
    return (
        all((right[index] - scale * left[index]) % prime == 0 for index in range(3)),
        scale,
    )


def projective_stabilizer_classification() -> dict[str, Any]:
    fields = (5, 7, 11, 13, 17, 19, 23, 31, 37, 43)
    permutations = tuple(itertools.permutations(range(3)))
    identity = (0, 1, 2)
    rows = []
    total_triples = 0
    total_nontrivial = 0
    for prime in fields:
        found: set[tuple[int, int, int]] = set()
        for b in range(1, prime):
            for c in range(1, prime):
                coefficients = (1, b, c)
                if len(set(coefficients)) != 3:
                    continue
                total_triples += 1
                stabilizer = []
                for permutation in permutations:
                    permuted = tuple(coefficients[index] for index in permutation)
                    proportional, scale = projectively_proportional(
                        coefficients, permuted, prime
                    )
                    if proportional:
                        stabilizer.append((permutation, scale))
                nonidentity = [row for row in stabilizer if row[0] != identity]
                if nonidentity:
                    found.add(coefficients)
        if prime % 3 == 1:
            generator = c25.primitive_root(prime)
            omega = pow(generator, (prime - 1) // 3, prime)
            expected = {
                (1, omega, omega * omega % prime),
                (1, omega * omega % prime, omega),
            }
        else:
            omega = None
            expected = set()
        if found != expected:
            raise AssertionError(
                f"projective stabilizer classification failed p={prime}: "
                f"found={sorted(found)} expected={sorted(expected)}"
            )
        total_nontrivial += len(found)
        rows.append(
            {
                "p": prime,
                "primitive_cube_root": omega,
                "nonzero_pairwise_distinct_projective_stabilizer_lines": [
                    list(coefficients) for coefficients in sorted(found)
                ],
                "count": len(found),
            }
        )
    return {
        "fields": rows,
        "normalized_pairwise_distinct_triples_checked": total_triples,
        "nontrivial_projective_lines_found": total_nontrivial,
        "classification_exact_on_screen": True,
        "symbolic_classification": (
            "a nonzero pairwise-distinct transposition eigenline is impossible; "
            "the only nontrivial projective stabilizers are the two primitive "
            "cube-root eigenlines of the two three-cycles"
        ),
    }


def projective_cubic_screen() -> dict[str, Any]:
    rows = []
    exact_phase_checks = 0
    quadratic_collisions = 0
    zero_status_collisions = 0
    opposite_parity_checks = 0
    nonzero_exact_phase_changes = 0

    for order in PROJECTIVE_ORDERS:
        prime, nth_root, omega = field_with_n_and_cube_roots(order)
        context = RootProductContext(order, prime, nth_root)
        witness = c25.first_inverse_parity_witness(order)
        if witness is None:
            raise AssertionError(f"no residue witness for n={order}")
        j, inverse = witness
        if j % 2 == inverse % 2:
            raise AssertionError("stored inversion witness has equal parity")

        family_rows = []

        # Forward cubic eigenline. The relevant three-cycle is
        # (a,b,c)->(b,c,a), with exponent k->1/(1-k).
        coefficients = (1, omega, omega * omega % prime)
        scalar = j + 1
        image = pow((1 - scalar) % order, -1, order)
        expected_image = (-inverse) % order
        if image != expected_image:
            raise AssertionError("forward three-cycle image mismatch")
        phase = pow(omega, -order, prime)
        left = context.value(coefficients, scalar)
        right = context.value(coefficients, image)
        if right != phase * left % prime:
            raise AssertionError("forward projective phase law failed")
        exact_phase_checks += 1
        if scalar % 2 == image % 2:
            raise AssertionError("forward projective orbit did not flip parity")
        opposite_parity_checks += 1
        if quadratic_character(phase, prime) != 1:
            raise AssertionError("cube-root phase is not a square")
        if quadratic_character(left, prime) != quadratic_character(right, prime):
            raise AssertionError("quadratic character changed under square phase")
        quadratic_collisions += 1
        if (left == 0) != (right == 0):
            raise AssertionError("zero status changed under nonzero phase")
        zero_status_collisions += 1
        nonzero_exact_phase_changes += int(left != 0 and left != right)
        family_rows.append(
            {
                "orientation": "forward",
                "coefficients": list(coefficients),
                "scalar": scalar,
                "image": image,
                "phase": phase,
                "left_value": left,
                "right_value": right,
                "quadratic_character": quadratic_character(left, prime),
            }
        )

        # Reverse cubic eigenline. The relevant three-cycle is
        # (a,b,c)->(c,a,b), with exponent k->(k-1)/k.
        reverse = (1, omega * omega % prime, omega)
        scalar = j
        image = (scalar - 1) * pow(scalar, -1, order) % order
        expected_image = (1 - inverse) % order
        if image != expected_image:
            raise AssertionError("reverse three-cycle image mismatch")
        left = context.value(reverse, scalar)
        right = context.value(reverse, image)
        if right != phase * left % prime:
            raise AssertionError("reverse projective phase law failed")
        exact_phase_checks += 1
        if scalar % 2 == image % 2:
            raise AssertionError("reverse projective orbit did not flip parity")
        opposite_parity_checks += 1
        if quadratic_character(left, prime) != quadratic_character(right, prime):
            raise AssertionError("reverse quadratic character changed")
        quadratic_collisions += 1
        if (left == 0) != (right == 0):
            raise AssertionError("reverse zero status changed")
        zero_status_collisions += 1
        nonzero_exact_phase_changes += int(left != 0 and left != right)
        family_rows.append(
            {
                "orientation": "reverse",
                "coefficients": list(reverse),
                "scalar": scalar,
                "image": image,
                "phase": phase,
                "left_value": left,
                "right_value": right,
                "quadratic_character": quadratic_character(left, prime),
            }
        )

        rows.append(
            {
                "n": order,
                "p": prime,
                "nth_root": nth_root,
                "omega": omega,
                "omega_is_square": quadratic_character(omega, prime) == 1,
                "n_mod_3": order % 3,
                "families": family_rows,
            }
        )

    return {
        "orders": rows,
        "orders_checked": len(rows),
        "exact_projective_phase_checks": exact_phase_checks,
        "opposite_parity_orbit_checks": opposite_parity_checks,
        "quadratic_character_collisions": quadratic_collisions,
        "zero_status_collisions": zero_status_collisions,
        "nonzero_exact_values_changed_by_phase": nonzero_exact_phase_changes,
        "quadratic_character_blocked_for_projective_cubic_family": True,
        "zero_nonzero_extraction_blocked_for_projective_cubic_family": True,
        "exact_value_extraction_blocked_by_projective_phase_alone": False,
    }


def degree_boundary_screen() -> dict[str, Any]:
    rows = []
    for order in DEGREE_SCREEN_ORDERS:
        best_minimum = -1
        best_scalar = None
        best_orbit = None
        for scalar in range(2, order):
            orbit = c25.mobius_images(order, scalar)
            values = tuple(orbit[name] for name, _ in c25.TRANSFORMS)
            minimum = min(values)
            if minimum > best_minimum:
                best_minimum = minimum
                best_scalar = scalar
                best_orbit = values
        lower_bound = (order - 3) // 6 + 2
        small_card = lower_bound - 2
        if 6 * small_card >= order - 2:
            raise AssertionError("six-cover strict inequality failed")
        if best_minimum < lower_bound:
            raise AssertionError("enumerated maximum violates counting bound")
        rows.append(
            {
                "n": order,
                "domain_cardinality": order - 2,
                "small_threshold": lower_bound,
                "small_set_cardinality": small_card,
                "six_small_sets_total_bound": 6 * small_card,
                "worst_scalar": best_scalar,
                "worst_orbit": list(best_orbit or ()),
                "enumerated_maximum_of_orbit_minimum": best_minimum,
                "counting_lower_bound_attained_or_exceeded": True,
            }
        )

    secp_lower = (SECP_N - 3) // 6 + 2
    return {
        "orders": rows,
        "orders_checked": len(rows),
        "all_counting_bounds_verified": True,
        "theorem": (
            "on a domain of n-2 exponents, six preimages of the B-2 "
            "representatives below B cannot cover when 6(B-2)<n-2"
        ),
        "secp256k1_one_step_reduced_degree_lower_bound": str(secp_lower),
        "secp256k1_lower_bound_bits": secp_lower.bit_length(),
        "scope": (
            "one S3/Mobius coefficient permutation followed by explicit "
            "degree-d polynomial or companion-state arithmetic"
        ),
        "unrestricted_sparse_resultant_lower_bound": False,
    }


def extracted_collision(
    context: c25.DeterminantContext,
    coefficients: tuple[int, int, int],
    extraction: Callable[[int, int], Any],
) -> dict[str, Any] | None:
    seen: dict[Any, tuple[int, int]] = {}
    for scalar in range(2, context.order):
        value = context.value(coefficients, scalar)
        extracted = extraction(value, context.prime)
        parity = scalar % 2
        if extracted in seen and seen[extracted][0] != parity:
            first_parity, first_scalar = seen[extracted]
            return {
                "n": context.order,
                "p": context.prime,
                "left": first_scalar,
                "right": scalar,
                "left_parity": first_parity,
                "right_parity": parity,
                "extracted_value": extracted,
            }
        seen.setdefault(extracted, (parity, scalar))
    return None


def first_collision_across_orders(
    contexts: dict[int, c25.DeterminantContext],
    orders: Iterable[int],
    coefficients: tuple[int, int, int],
    extraction: Callable[[int, int], Any],
) -> dict[str, Any] | None:
    for order in orders:
        collision = extracted_collision(contexts[order], coefficients, extraction)
        if collision is not None:
            return collision
    return None


def fixed_label_screen() -> dict[str, Any]:
    all_orders = tuple(dict.fromkeys(DISCOVERY_ORDERS + HELD_OUT_ORDERS))
    contexts = {order: c25.DeterminantContext(order) for order in all_orders}

    def exact(value: int, prime: int) -> int:
        return value

    def zero_status(value: int, prime: int) -> int:
        return int(value != 0)

    extraction_families: dict[str, Callable[[int, int], Any]] = {
        "exact_value": exact,
        "zero_nonzero": zero_status,
    }
    for character_order in CHARACTER_ORDERS:
        extraction_families[f"character_order_{character_order}"] = (
            lambda value, prime, order=character_order:
                c25.quadratic_character(value, prime)
                if order == 2
                else multiplicative_character(value, prime, order)
        )

    lanes = {
        "a_eq_b_fixed_small": LANE_A_COEFFICIENTS,
        "fully_asymmetric_fixed_small": LANE_B_COEFFICIENTS,
    }
    lane_rows = []
    extraction_survivors: Counter[str] = Counter()
    total_candidate_extraction_pairs = 0

    for lane, coefficients_list in lanes.items():
        candidates = []
        for coefficients in coefficients_list:
            extractions = {}
            for name, extraction in extraction_families.items():
                discovery_collision = first_collision_across_orders(
                    contexts, DISCOVERY_ORDERS, coefficients, extraction
                )
                held_out_collision = first_collision_across_orders(
                    contexts, HELD_OUT_ORDERS, coefficients, extraction
                )
                survived = discovery_collision is None or held_out_collision is None
                if survived:
                    extraction_survivors[name] += 1
                total_candidate_extraction_pairs += 1
                extractions[name] = {
                    "discovery_collision": discovery_collision,
                    "held_out_collision": held_out_collision,
                    "survived_both_splits": survived,
                }
            candidates.append(
                {
                    "coefficients": list(coefficients),
                    "extractions": extractions,
                }
            )
        lane_rows.append(
            {
                "lane": lane,
                "candidate_count": len(coefficients_list),
                "candidates": candidates,
            }
        )

    ratio_contexts = contexts
    ratio_rows = []
    ratio_survivors = 0
    for numerator in VARIANT_LIBRARY:
        for denominator in VARIANT_LIBRARY:
            if numerator == denominator:
                continue

            def ratio_quadratic(value_unused: int, prime_unused: int) -> int:
                raise AssertionError("ratio extraction is evaluated separately")

            def ratio_collision(order: int) -> dict[str, Any] | None:
                context = ratio_contexts[order]
                seen: dict[int, tuple[int, int]] = {}
                for scalar in range(2, order):
                    left = context.value(numerator, scalar)
                    right = context.value(denominator, scalar)
                    ratio = 0 if right == 0 else left * pow(right, -1, context.prime) % context.prime
                    extracted = c25.quadratic_character(ratio, context.prime)
                    parity = scalar % 2
                    if extracted in seen and seen[extracted][0] != parity:
                        first_parity, first_scalar = seen[extracted]
                        return {
                            "n": order,
                            "p": context.prime,
                            "left": first_scalar,
                            "right": scalar,
                            "left_parity": first_parity,
                            "right_parity": parity,
                            "extracted_value": extracted,
                        }
                    seen.setdefault(extracted, (parity, scalar))
                return None

            discovery_collision = next(
                (collision for order in DISCOVERY_ORDERS
                 if (collision := ratio_collision(order)) is not None),
                None,
            )
            held_out_collision = next(
                (collision for order in HELD_OUT_ORDERS
                 if (collision := ratio_collision(order)) is not None),
                None,
            )
            survived = discovery_collision is None or held_out_collision is None
            ratio_survivors += int(survived)
            ratio_rows.append(
                {
                    "numerator": list(numerator),
                    "denominator": list(denominator),
                    "discovery_collision": discovery_collision,
                    "held_out_collision": held_out_collision,
                    "survived_both_splits": survived,
                }
            )

    if extraction_survivors:
        raise AssertionError(
            f"unexpected fixed-label extraction survivor: {dict(extraction_survivors)}"
        )
    if ratio_survivors:
        raise AssertionError(f"unexpected bounded-ratio survivor count: {ratio_survivors}")

    return {
        "discovery_orders": list(DISCOVERY_ORDERS),
        "held_out_orders": list(HELD_OUT_ORDERS),
        "character_orders": list(CHARACTER_ORDERS),
        "lanes": lane_rows,
        "candidate_coefficients": len(LANE_A_COEFFICIENTS) + len(LANE_B_COEFFICIENTS),
        "candidate_extraction_pairs": total_candidate_extraction_pairs,
        "survivors_by_extraction": {},
        "bounded_variant_library": [list(row) for row in VARIANT_LIBRARY],
        "bounded_ordered_ratio_pairs": len(ratio_rows),
        "bounded_ratio_survivors": 0,
        "bounded_ratio_rows": ratio_rows,
        "all_fixed_small_candidates_rejected_on_discovery_and_held_out": True,
        "finite_screen_only": True,
        "fixed_label_family_universally_blocked": False,
    }


def secp_certificate() -> dict[str, Any]:
    reduced_degree = (SECP_N - 3) // 6 + 2
    return {
        "n": str(SECP_N),
        "n_mod_3": SECP_N % 3,
        "n_mod_4": SECP_N % 4,
        "one_step_Mobius_reduced_degree_lower_bound": str(reduced_degree),
        "lower_bound_bits": reduced_degree.bit_length(),
        "projective_cubic_coefficients_available_from_public_GLV_cube_root": True,
        "projective_cubic_quadratic_character_blocked": True,
        "projective_cubic_exact_value_blocked": False,
        "a_eq_b_fixed_label_universally_blocked": False,
        "fully_asymmetric_fixed_label_universally_blocked": False,
        "numeric_k_control_is_not_public_Q_control": True,
        "linear_regular_representation_public_Q_realization_known": True,
        "sublinear_public_Q_control_flow_found": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    projective_classification = projective_stabilizer_classification()
    projective_screen = projective_cubic_screen()
    degree_screen = degree_boundary_screen()
    fixed_screen = fixed_label_screen()

    payload = {
        "experiment": "ASYMMETRIC-SPARSE-RESULTANT-EVALUATION-C26",
        "source_certificates": source_certificate(),
        "projective_stabilizer_classification": projective_classification,
        "projective_cubic_screen": projective_screen,
        "one_step_degree_boundary": degree_screen,
        "fixed_label_screen": fixed_screen,
        "secp256k1": secp_certificate(),
        "scope": {
            "proved_or_certified": [
                "projective S3 stabilizer classification for nonzero pairwise-distinct coefficient lines",
                "exact cubic projective phase law on all screened orders",
                "quadratic-character and zero-status collision on the cubic eigenlines for every screened prime n>11",
                "six-cover worst-case linear degree for one S3/Mobius reparameterization",
                "discovery and held-out rejection of declared fixed-small extraction grammars",
            ],
            "not_proved": [
                "an exact-value no-go theorem for the projective cubic family",
                "a universal fixed-label no-go theorem for a=b!=c",
                "a universal fixed-label no-go theorem for all asymmetric coefficients",
                "an unrestricted lacunary-resultant lower bound",
                "a sublinear public-Q control flow",
                "a Hilbert90 branch bridge",
            ],
        },
        "aggregate": {
            "projective_stabilizer_classification_verified": True,
            "projective_cubic_phase_law_verified": True,
            "projective_cubic_quadratic_character_blocked": True,
            "projective_cubic_zero_status_blocked": True,
            "projective_cubic_exact_value_blocked": False,
            "one_step_Mobius_reparameterization_worst_case_linear": True,
            "fixed_small_a_eq_b_exact_value_survivors": 0,
            "fixed_small_fully_asymmetric_exact_value_survivors": 0,
            "fixed_small_character_survivors": 0,
            "bounded_variant_ratio_survivors": 0,
            "fixed_small_screens_are_universal_proofs": False,
            "a_eq_b_fixed_label_collision_proved": False,
            "fully_asymmetric_fixed_label_collision_proved": False,
            "sublinear_one_step_Mobius_resultant_representation_found": False,
            "sublinear_numeric_k_resultant_algorithm_found": False,
            "sublinear_public_Q_control_flow_found": False,
            "exact_Hilbert90_branch_bridge_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(raw.encode()).hexdigest()
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
