#!/usr/bin/env python3
"""Generate the exact secp256k1 M16 factor-base census.

This is a deterministic structural/applicability calculation. It enumerates
the 13441-smooth subgroup of F_p^* through its cube orbits, but it does not
construct a Semaev system, run a solver, or compute a discrete logarithm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any


P = (1 << 256) - (1 << 32) - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
B = 7
D = 564_522
ARITY = 16
D_FACTORS = (2, 3, 7, 13_441)
LARGE_COFACTOR = (P - 1) // D
BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE",
    16,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

UPSTREAM_BINDINGS = {
    "Ecdlp/Secp256k1Verified.lean": (
        "f0ddddc4a890d9b9eab350ae7374e4f0e0bef62d3ec75adaee1f166ade2c3037"
    ),
    "experiments/engine/outcomes/REO-2026-07-31-001.json": (
        "340ce99d4cb87f63212d9e298cdf2fd7da8c171ffce5d23132f862a5df792d02"
    ),
    "experiments/engine/pkc_smooth_desk_screen/artifact.json": (
        "7d2338eadefd7b531b83fc77a4e944a32aef5ab8646cacef5eb3b26191c7f78e"
    ),
    "experiments/engine/pkc_smooth_m16_fixed_target_yield/artifact.json": (
        "21a95ea4ea71c02d0199c331e549ca2e4ec2fbf7c1d8d70fe6651bea292d6413"
    ),
    "experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json": (
        "59596c3c59f5389c49742ba4a26d500445557ee6398d6aaad63c7995a93242f7"
    ),
    "experiments/engine/proposals/HGP-M16-SOLVER-SLOPE-001.json": (
        "14bfab1eb68f6e6b03e5754302fbe888f250121d1125e1202167d5af35e455c9"
    ),
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_upstream_bindings() -> None:
    problems: list[str] = []
    for relative, expected in UPSTREAM_BINDINGS.items():
        path = ROOT / relative
        if not path.is_file():
            problems.append(f"missing upstream file: {relative}")
            continue
        observed = file_sha256(path)
        if observed != expected:
            problems.append(
                f"upstream hash drift for {relative}: {observed} != {expected}"
            )
    if problems:
        raise RuntimeError("; ".join(problems))


def find_subgroup_generator() -> tuple[int, int]:
    """Return the first base and its projection of exact order D."""
    for base in range(2, 10_000):
        generator = pow(base, LARGE_COFACTOR, P)
        if generator == 1 or pow(generator, D, P) != 1:
            continue
        if all(pow(generator, D // prime, P) != 1 for prime in D_FACTORS):
            return base, generator
    raise RuntimeError("no deterministic exact-order-D generator found")


def legendre(value: int) -> int:
    value %= P
    if value == 0:
        return 0
    result = pow(value, (P - 1) // 2, P)
    if result == 1:
        return 1
    if result == P - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-character value")


def reduced_fraction(numerator: int, denominator: int) -> tuple[int, int]:
    if denominator <= 0:
        raise ValueError("fraction denominator must be positive")
    common = math.gcd(numerator, denominator)
    return numerator // common, denominator // common


def decimal_ratio(numerator: int, denominator: int) -> str:
    with localcontext() as context:
        context.prec = 42
        return format(Decimal(numerator) / Decimal(denominator), ".36E")


def fraction_record(
    numerator: int,
    denominator: int,
    *,
    formula: str,
    interpretation: str,
) -> dict[str, str]:
    reduced_numerator, reduced_denominator = reduced_fraction(
        numerator, denominator
    )
    return {
        "decimal_display": decimal_ratio(reduced_numerator, reduced_denominator),
        "denominator": str(reduced_denominator),
        "formula": formula,
        "interpretation": interpretation,
        "numerator": str(reduced_numerator),
    }


def falling_factorial(value: int, count: int) -> int:
    result = 1
    for offset in range(count):
        result *= value - offset
    return result


def factor_base_census(generator: int) -> dict[str, Any]:
    beta_from_generator = pow(generator, D // 3, P)
    if BETA not in {beta_from_generator, pow(beta_from_generator, 2, P)}:
        raise AssertionError("public beta is not the generator's order-three element")
    if pow(BETA, 3, P) != 1 or BETA == 1:
        raise AssertionError("public beta is not a nontrivial cube root")

    positive = negative = zero = character_sum = 0
    liftable_orbits = nonliftable_orbits = zero_orbits = 0
    x = 1
    beta2 = pow(BETA, 2, P)
    orbit_count = D // 3

    for _ in range(orbit_count):
        orbit = (x, (BETA * x) % P, (beta2 * x) % P)
        if len(set(orbit)) != 3:
            raise AssertionError("a nonzero GLV x-orbit is not free")
        cubes = {pow(member, 3, P) for member in orbit}
        if len(cubes) != 1:
            raise AssertionError("GLV orbit members do not share their cube")
        if any(pow(member, D, P) != 1 for member in orbit):
            raise AssertionError("GLV orbit escaped H")

        character = legendre(next(iter(cubes)) + B)
        character_sum += 3 * character
        if character == 1:
            positive += 3
            liftable_orbits += 1
        elif character == -1:
            negative += 3
            nonliftable_orbits += 1
        else:
            zero += 3
            zero_orbits += 1
        x = (x * generator) % P

    if x != pow(generator, orbit_count, P):
        raise AssertionError("orbit representative progression drifted")
    if positive + negative + zero != D:
        raise AssertionError("factor-base census does not partition H")
    if positive != 283_527 or negative != 280_995:
        raise AssertionError("unexpected secp256k1 factor-base census")

    signed_points = 2 * positive
    return {
        "character_sum_over_H": character_sum,
        "glv_orbits": {
            "all_x_orbits": orbit_count,
            "orbit_classes_modulo_negation_and_glv": liftable_orbits,
            "liftable_signed_point_orbits": signed_points // 3,
            "liftable_x_orbits": liftable_orbits,
            "nonliftable_x_orbits": nonliftable_orbits,
            "orbit_action_verified_elementwise": True,
            "orbit_size": 3,
            "zero_rhs_x_orbits": zero_orbits,
        },
        "liftable_x": positive,
        "nonliftable_x": negative,
        "signed_affine_factor_points": signed_points,
        "subgroup_x_total": D,
        "zero_rhs_x": zero,
    }


def build_yield_models(census: dict[str, Any]) -> dict[str, Any]:
    usable_x = census["liftable_x"]
    signed_points = census["signed_affine_factor_points"]
    group_nonidentity = N - 1

    multiset_count = math.comb(signed_points + ARITY - 1, ARITY)
    negation_fixed_multisets = math.comb(usable_x + ARITY // 2 - 1, ARITY // 2)
    distinct_signed_count = math.comb(signed_points, ARITY)
    negation_fixed_distinct = math.comb(usable_x, ARITY // 2)
    distinct_x_signed_count = (1 << ARITY) * math.comb(usable_x, ARITY)
    ordered_signed_count = signed_points**ARITY
    ordered_distinct_signed = falling_factorial(signed_points, ARITY)

    return {
        "notation": {
            "A_signed_affine_points": signed_points,
            "D_source_coordinate_subgroup": D,
            "U_liftable_x": usable_x,
            "k_arity": ARITY,
            "p_base_field_order": str(P),
            "q_curve_group_order": str(N),
        },
        "exact_combinatorial_counts": {
            "distinct_signed_configurations": str(distinct_signed_count),
            "distinct_x_with_sign_configurations": str(distinct_x_signed_count),
            "negation_fixed_distinct_configurations": str(
                negation_fixed_distinct
            ),
            "negation_fixed_multisets": str(negation_fixed_multisets),
            "signed_point_multisets": str(multiset_count),
        },
        "source_heuristic": fraction_record(
            D**ARITY,
            math.factorial(ARITY) * P,
            formula="D^16/(16!*p)",
            interpretation=(
                "The PKC 2016 source-level coordinate-root heuristic, "
                "retained as a comparator rather than target truth."
            ),
        ),
        "conditioned_null_comparators": {
            "distinct_signed_conditioned_nonidentity": fraction_record(
                distinct_signed_count - negation_fixed_distinct,
                group_nonidentity,
                formula="(C(A,16)-C(U,8))/(q-1)",
                interpretation=(
                    "Counterfactual comparator after removing exactly the "
                    "negation-fixed distinct subsets, then conditioning every "
                    "remaining configuration on a nonidentity sum uniform over "
                    "q-1 targets. Other zero-sum configurations may exist."
                ),
            ),
            "distinct_x_signed_conditioned_nonidentity": fraction_record(
                distinct_x_signed_count,
                group_nonidentity,
                formula="2^16*C(U,16)/(q-1)",
                interpretation=(
                    "Counterfactual distinct-x signed comparator conditioned "
                    "on a nonidentity sum uniform over q-1 targets. The exact "
                    "numerator can still contain non-pairwise zero sums."
                ),
            ),
            "signed_multiset_conditioned_nonidentity": fraction_record(
                multiset_count - negation_fixed_multisets,
                group_nonidentity,
                formula="(C(A+15,16)-C(U+7,8))/(q-1)",
                interpretation=(
                    "Counterfactual comparator after removing exactly the "
                    "negation-fixed signed multisets, then conditioning every "
                    "remaining configuration on a nonidentity sum uniform over "
                    "q-1 targets. Other cancellation relations may exist."
                ),
            ),
        },
        "conditioned_null_boundary": [
            "A=567054 signed affine factor points, U=283527 liftable x values, q is the prime curve-group order, D=564522, and k=16.",
            "The q-1 denominators define counterfactual conditioning; they do not establish the actual group-sum distribution.",
            "Only explicitly counted negation-fixed cancellations are removed. Additional zero-sum or dependent configurations are neither counted nor excluded.",
        ],
        "ordered_sampling_repeat_probability": fraction_record(
            ordered_signed_count - ordered_distinct_signed,
            ordered_signed_count,
            formula="1-(A)_16/A^16",
            interpretation=(
                "Collision probability for sixteen iid signed affine factor "
                "points; this is not the distinct-x collision probability."
            ),
        ),
    }


def build_artifact() -> dict[str, Any]:
    assert_upstream_bindings()
    proposal = json.loads(
        (ROOT / "experiments/engine/proposals/HGP-M16-SOLVER-SLOPE-001.json")
        .read_text(encoding="utf-8")
    )
    toy_scope = proposal.get("toy_scope", {})
    if toy_scope.get("max_field_bits") != 24:
        raise AssertionError("proposal max_field_bits is not the frozen value 24")
    if "calibration only" not in toy_scope.get("curve_family", ""):
        raise AssertionError("proposal lost its calibration-only boundary")
    if "secp256k1" not in toy_scope.get("forbidden_targets", []):
        raise AssertionError("proposal lost its secp256k1 execution ban")

    generator_base, generator = find_subgroup_generator()
    census = factor_base_census(generator)
    return {
        "artifact_id": "PKC-SMOOTH-M16-REGIME-ASSURANCE-DESK-001",
        "artifact_kind": "structural_applicability_desk_certificate",
        "inputs": {
            "D": D,
            "arity": ARITY,
            "b": B,
            "beta": str(BETA),
            "n": str(N),
            "p": str(P),
            "small_prime_factors": list(D_FACTORS),
        },
        "method": {
            "algorithm": (
                "Find the first exact-order-D subgroup generator, enumerate "
                "D/3 explicit GLV orbit representatives, verify all three "
                "members and evaluate Euler's criterion on their shared cube."
            ),
            "generator": str(generator),
            "generator_search_base": generator_base,
            "generator_order": D,
            "large_cofactor": str(LARGE_COFACTOR),
            "representatives_enumerated": D // 3,
        },
        "factor_base_census": census,
        "yield_models": build_yield_models(census),
        "proposal_regime": {
            "classification": "INAPPLICABLE_UNDER_CURRENT_MAX24",
            "frozen_max_field_bits": 24,
            "reason": (
                "The immutable proposal states that its <=24-bit ladder is "
                "calibration-only and cannot support the M16 exponent claim."
            ),
            "scope": "proposal_execution_regime_only",
        },
        "terminal": {
            "M16_mechanism_falsified": False,
            "authorization": "none",
            "calibration": "excluded_nonexperimental",
            "cell_transition": "open_to_open",
            "census": "confirmed",
            "classification": "INAPPLICABLE_UNDER_CURRENT_MAX24",
            "novelty_claimed": False,
            "route_status": "open_parked",
            "scope": "proposal_execution_regime_only",
            "source_independence": "not_established",
        },
        "trust_boundary": {
            "excluded": [
                "Semaev system construction or solver execution",
                "relation independence, rank, solving-degree, or fill-in claim",
                "asymptotic or secp256k1 ECDLP improvement",
                "route rejection, route promotion, or experiment authorization",
                "global novelty or Kudo full-text claim",
            ],
            "interpretation": (
                "Exact subgroup and combinatorial arithmetic update target "
                "properties and conditioned null comparators only. They do not "
                "measure a solver or validate the M16 attack mechanism."
            ),
        },
        "upstream_bindings": dict(sorted(UPSTREAM_BINDINGS.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        artifact_bytes = canonical_bytes(build_artifact())
    except (AssertionError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    hash_bytes = f"{digest}  artifact.json\n".encode("ascii")

    if not args.check:
        ARTIFACT_PATH.write_bytes(artifact_bytes)
        HASH_PATH.write_bytes(hash_bytes)
        print(f"wrote {ARTIFACT_PATH}")
        print(f"sha256 {digest}")
        return 0

    problems: list[str] = []
    if not ARTIFACT_PATH.is_file() or ARTIFACT_PATH.read_bytes() != artifact_bytes:
        problems.append("artifact.json differs from deterministic output")
    if not HASH_PATH.is_file() or HASH_PATH.read_bytes() != hash_bytes:
        problems.append("artifact.sha256 differs from deterministic output")
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    print("M16 regime-assurance desk artifact matches deterministic output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
