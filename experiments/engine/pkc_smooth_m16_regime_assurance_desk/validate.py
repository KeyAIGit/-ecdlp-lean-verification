#!/usr/bin/env python3
"""Independent replay for the secp256k1 M16 regime-assurance artifact.

The producer is deliberately not imported.  This validator constructs the
subgroup from independent prime-order components, enumerates every one of its
564522 elements, and recomputes the decisive arithmetic from exact integers.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


P = (1 << 256) - (1 << 32) - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
B = 7
D = 564_522
ARITY = 16
PRIME_ORDERS = (2, 3, 7, 13_441)
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


class ValidationFailure(Exception):
    """The artifact or one of its provenance bindings failed replay."""


class Replay:
    """Cache of the expensive independent census and exact null models."""

    def __init__(self, census: dict[str, Any], yields: dict[str, Any]) -> None:
        self.census = census
        self.yields = yields


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def exact(label: str, actual: Any, expected: Any) -> None:
    require(actual == expected, f"{label}: {actual!r} != {expected!r}")


def exact_keys(label: str, value: Any, expected: set[str]) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    exact(f"{label} keys", set(value), expected)
    return value


def strict_int(label: str, value: Any) -> int:
    require(
        isinstance(value, int) and not isinstance(value, bool),
        f"{label} must be an integer",
    )
    return value


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


def gcd(left: int, right: int) -> int:
    left = abs(left)
    right = abs(right)
    while right:
        left, right = right, left % right
    return left


def reduced_fraction(numerator: int, denominator: int) -> tuple[int, int]:
    require(denominator > 0, "fraction denominator must be positive")
    common = gcd(numerator, denominator)
    return numerator // common, denominator // common


def decimal_ratio(numerator: int, denominator: int) -> str:
    with localcontext() as context:
        context.prec = 42
        return format(Decimal(numerator) / Decimal(denominator), ".36E")


def comb(total: int, selected: int) -> int:
    """Exact binomial coefficient without math.comb."""
    require(total >= 0 and selected >= 0, "comb arguments must be nonnegative")
    if selected > total:
        return 0
    selected = min(selected, total - selected)
    result = 1
    for index in range(1, selected + 1):
        result = result * (total - selected + index) // index
    return result


def factorial(value: int) -> int:
    require(value >= 0, "factorial argument must be nonnegative")
    result = 1
    for factor in range(2, value + 1):
        result *= factor
    return result


def falling_factorial(value: int, count: int) -> int:
    require(value >= count >= 0, "invalid falling-factorial arguments")
    result = 1
    for offset in range(count):
        result *= value - offset
    return result


def fraction_record(
    numerator: int,
    denominator: int,
    *,
    formula: str,
    interpretation: str,
) -> dict[str, str]:
    numerator, denominator = reduced_fraction(numerator, denominator)
    return {
        "decimal_display": decimal_ratio(numerator, denominator),
        "denominator": str(denominator),
        "formula": formula,
        "interpretation": interpretation,
        "numerator": str(numerator),
    }


def find_prime_order_component(order: int) -> tuple[int, int]:
    """Find a nonidentity element of the requested prime order."""
    require(order in PRIME_ORDERS, f"unsupported prime order {order}")
    exponent = (P - 1) // order
    for base in range(2, 10_000):
        component = pow(base, exponent, P)
        if component != 1:
            require(pow(component, order, P) == 1, "component order escaped")
            return base, component
    raise ValidationFailure(f"no component of order {order} found")


def legendre(value: int) -> int:
    value %= P
    if value == 0:
        return 0
    result = pow(value, (P - 1) // 2, P)
    if result == 1:
        return 1
    if result == P - 1:
        return -1
    raise ValidationFailure("Euler criterion returned a non-character value")


def independent_census() -> dict[str, Any]:
    """Construct H componentwise and enumerate all D elements."""
    components: dict[int, int] = {}
    component_bases: dict[int, int] = {}
    generator = 1
    for order in PRIME_ORDERS:
        base, component = find_prime_order_component(order)
        component_bases[order] = base
        components[order] = component
        generator = generator * component % P

    require(pow(generator, D, P) == 1, "component product is not in H")
    for order in PRIME_ORDERS:
        require(
            pow(generator, D // order, P) != 1,
            f"component product lacks order-{order} part",
        )
    require(components[3] == BETA, "independent order-three component drifted")
    require(pow(BETA, 3, P) == 1 and BETA != 1, "invalid public beta")

    beta2 = BETA * BETA % P
    character_sum = 0
    positive = negative = zero = 0
    all_representatives: set[int] = set()
    positive_representatives: set[int] = set()
    negative_representatives: set[int] = set()
    zero_representatives: set[int] = set()
    fixed_point_seen = False

    value = 1
    for _ in range(D):
        rhs = (value * value % P * value + B) % P
        character = legendre(rhs)
        character_sum += character
        orbit = (value, BETA * value % P, beta2 * value % P)
        if len(set(orbit)) != 3:
            fixed_point_seen = True
        representative = min(orbit)
        all_representatives.add(representative)
        if character == 1:
            positive += 1
            positive_representatives.add(representative)
        elif character == -1:
            negative += 1
            negative_representatives.add(representative)
        else:
            zero += 1
            zero_representatives.add(representative)
        value = value * generator % P

    require(value == 1, "full H enumeration did not close")
    exact("census partition", positive + negative + zero, D)
    require(not fixed_point_seen, "nonzero GLV orbit has a fixed point")
    exact("all GLV x-orbits", len(all_representatives), D // 3)
    exact("liftable GLV x-orbits", 3 * len(positive_representatives), positive)
    exact("nonliftable GLV x-orbits", 3 * len(negative_representatives), negative)
    exact("zero GLV x-orbits", 3 * len(zero_representatives), zero)

    signed_points = 2 * positive + zero
    return {
        "component_bases": {str(key): value for key, value in component_bases.items()},
        "generator": generator,
        "generator_order": D,
        "character_sum_over_H": character_sum,
        "glv_orbits": {
            "all_x_orbits": len(all_representatives),
            "factor_log_columns_modulo_negation_and_glv": len(
                positive_representatives
            ),
            "liftable_signed_point_orbits": signed_points // 3,
            "liftable_x_orbits": len(positive_representatives),
            "nonliftable_x_orbits": len(negative_representatives),
            "orbit_action_verified_elementwise": not fixed_point_seen,
            "orbit_size": 3,
            "zero_rhs_x_orbits": len(zero_representatives),
        },
        "liftable_x": positive,
        "nonliftable_x": negative,
        "signed_affine_factor_points": signed_points,
        "subgroup_x_total": D,
        "zero_rhs_x": zero,
    }


def independent_yield_models(census: dict[str, Any]) -> dict[str, Any]:
    usable_x = census["liftable_x"]
    signed_points = census["signed_affine_factor_points"]
    group_nonidentity = N - 1
    multiset_count = comb(signed_points + ARITY - 1, ARITY)
    fixed_multisets = comb(usable_x + ARITY // 2 - 1, ARITY // 2)
    distinct_signed = comb(signed_points, ARITY)
    fixed_distinct = comb(usable_x, ARITY // 2)
    distinct_x_signed = (1 << ARITY) * comb(usable_x, ARITY)
    ordered = signed_points**ARITY
    ordered_distinct = falling_factorial(signed_points, ARITY)
    return {
        "exact_combinatorial_counts": {
            "distinct_signed_configurations": str(distinct_signed),
            "distinct_x_with_sign_configurations": str(distinct_x_signed),
            "negation_fixed_distinct_configurations": str(fixed_distinct),
            "negation_fixed_multisets": str(fixed_multisets),
            "signed_point_multisets": str(multiset_count),
        },
        "models": {
            "distinct_signed_uniform_nonidentity_null": fraction_record(
                distinct_signed - fixed_distinct,
                group_nonidentity,
                formula="(C(N,16)-C(U,8))/(n-1)",
                interpretation=(
                    "Expected count under a uniform-nonidentity null after "
                    "removing exactly negation-fixed distinct subsets."
                ),
            ),
            "distinct_x_signed_uniform_null": fraction_record(
                distinct_x_signed,
                group_nonidentity,
                formula="2^16*C(U,16)/(n-1)",
                interpretation=(
                    "A distinct-x signed null model. It does not assert that "
                    "all configurations are independent or nonzero-sum."
                ),
            ),
            "paper_source_heuristic": fraction_record(
                D**ARITY,
                factorial(ARITY) * P,
                formula="D^16/(16!*p)",
                interpretation=(
                    "The PKC 2016 source-level coordinate-root heuristic, "
                    "retained as a comparator rather than target truth."
                ),
            ),
            "signed_multiset_uniform_nonidentity_null": fraction_record(
                multiset_count - fixed_multisets,
                group_nonidentity,
                formula="(C(N+15,16)-C(U+7,8))/(n-1)",
                interpretation=(
                    "Expected count under a uniform-nonidentity null after "
                    "removing exactly negation-fixed signed multisets."
                ),
            ),
        },
        "ordered_sampling_repeat_probability": fraction_record(
            ordered - ordered_distinct,
            ordered,
            formula="1-(N)_16/N^16",
            interpretation=(
                "Collision probability for sixteen iid signed affine factor "
                "points; this is not the distinct-x collision probability."
            ),
        ),
    }


def build_replay() -> Replay:
    census = independent_census()
    return Replay(census, independent_yield_models(census))


def check_inputs(document: dict[str, Any]) -> None:
    inputs = exact_keys(
        "inputs",
        document.get("inputs"),
        {"D", "arity", "b", "beta", "n", "p", "small_prime_factors"},
    )
    exact("inputs", inputs, {
        "D": D,
        "arity": ARITY,
        "b": B,
        "beta": str(BETA),
        "n": str(N),
        "p": str(P),
        "small_prime_factors": list(PRIME_ORDERS),
    })


def check_method(document: dict[str, Any]) -> None:
    method = exact_keys(
        "method",
        document.get("method"),
        {
            "algorithm", "generator", "generator_order", "generator_search_base",
            "large_cofactor", "representatives_enumerated",
        },
    )
    generator = int(method.get("generator", "0"))
    exact("method.generator_order", strict_int("generator_order", method.get("generator_order")), D)
    require(generator != 1 and pow(generator, D, P) == 1, "producer generator is not in H")
    for order in PRIME_ORDERS:
        require(pow(generator, D // order, P) != 1, "producer generator is not exact-order D")
    exact("method.large_cofactor", method.get("large_cofactor"), str((P - 1) // D))
    exact("method.representatives_enumerated", method.get("representatives_enumerated"), D // 3)
    require(isinstance(method.get("generator_search_base"), int), "generator base must be integer")
    require(isinstance(method.get("algorithm"), str) and method["algorithm"], "algorithm missing")


def check_proposal_and_terminal(document: dict[str, Any]) -> None:
    regime = exact_keys(
        "proposal_regime",
        document.get("proposal_regime"),
        {"classification", "frozen_max_field_bits", "reason", "scope"},
    )
    exact("proposal_regime.classification", regime["classification"], "INAPPLICABLE_UNDER_CURRENT_MAX24")
    exact("proposal_regime.frozen_max_field_bits", regime["frozen_max_field_bits"], 24)
    exact("proposal_regime.scope", regime["scope"], "proposal_execution_regime_only")
    require("calibration-only" in regime["reason"], "proposal regime reason overstates the evidence")

    terminal = exact_keys(
        "terminal",
        document.get("terminal"),
        {
            "M16_mechanism_falsified", "authorization", "calibration",
            "cell_transition", "census", "classification", "novelty_claimed",
            "route_status", "scope", "source_independence",
        },
    )
    exact("terminal", terminal, {
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
    })

    boundary = exact_keys(
        "trust_boundary",
        document.get("trust_boundary"),
        {"excluded", "interpretation"},
    )
    exact("trust_boundary.excluded", boundary["excluded"], [
        "Semaev system construction or solver execution",
        "relation independence, rank, solving-degree, or fill-in claim",
        "asymptotic or secp256k1 ECDLP improvement",
        "route rejection, route promotion, or experiment authorization",
        "global novelty or Kudo full-text claim",
    ])
    exact(
        "trust_boundary.interpretation",
        boundary["interpretation"],
        (
            "Exact subgroup and combinatorial arithmetic update target "
            "properties and null-model comparators only. They do not "
            "measure a solver or validate the M16 attack mechanism."
        ),
    )


def check_upstream(
    document: dict[str, Any], root: Path, *, verify_files: bool
) -> None:
    bindings = exact_keys(
        "upstream_bindings",
        document.get("upstream_bindings"),
        set(UPSTREAM_BINDINGS),
    )
    exact("upstream_bindings", bindings, UPSTREAM_BINDINGS)
    if not verify_files:
        return
    for relative, expected in UPSTREAM_BINDINGS.items():
        path = root / relative
        require(path.is_file(), f"missing upstream file: {relative}")
        exact(f"upstream hash {relative}", file_sha256(path), expected)

    proposal = json.loads(
        (root / "experiments/engine/proposals/HGP-M16-SOLVER-SLOPE-001.json")
        .read_text(encoding="utf-8")
    )
    scope = proposal.get("toy_scope", {})
    exact("proposal max_field_bits", scope.get("max_field_bits"), 24)
    require("calibration only" in scope.get("curve_family", ""), "proposal calibration boundary drifted")
    require("secp256k1" in scope.get("forbidden_targets", []), "proposal exact-target ban drifted")


def validate_document(
    document: Any,
    replay: Replay,
    *,
    root: Path = ROOT,
    verify_upstream: bool = True,
) -> None:
    top = exact_keys(
        "artifact",
        document,
        {
            "artifact_id", "artifact_kind", "factor_base_census", "inputs",
            "method", "proposal_regime", "terminal", "trust_boundary",
            "upstream_bindings", "yield_models",
        },
    )
    exact("artifact_id", top["artifact_id"], "PKC-SMOOTH-M16-REGIME-ASSURANCE-DESK-001")
    exact("artifact_kind", top["artifact_kind"], "structural_applicability_desk_certificate")
    check_inputs(top)
    check_method(top)

    expected_census = dict(replay.census)
    expected_census.pop("component_bases")
    expected_census.pop("generator")
    expected_census.pop("generator_order")
    exact("factor_base_census", top["factor_base_census"], expected_census)
    exact("yield_models", top["yield_models"], replay.yields)
    check_proposal_and_terminal(top)
    check_upstream(top, root, verify_files=verify_upstream)


def load_and_validate(
    artifact_path: Path = ARTIFACT_PATH,
    hash_path: Path = HASH_PATH,
    *,
    root: Path = ROOT,
    replay: Replay | None = None,
) -> Replay:
    try:
        artifact_bytes = artifact_path.read_bytes()
        document = json.loads(artifact_bytes)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationFailure(f"artifact unreadable: {error}") from error
    exact("canonical artifact bytes", artifact_bytes, canonical_bytes(document))
    expected_sidecar = (
        f"{hashlib.sha256(artifact_bytes).hexdigest()}  artifact.json\n"
    ).encode("ascii")
    try:
        sidecar_bytes = hash_path.read_bytes()
    except OSError as error:
        raise ValidationFailure(f"hash sidecar unreadable: {error}") from error
    exact("artifact.sha256", sidecar_bytes, expected_sidecar)
    replay = replay or build_replay()
    validate_document(document, replay, root=root, verify_upstream=True)
    return replay


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=ARTIFACT_PATH)
    parser.add_argument("--hash-file", type=Path, default=HASH_PATH)
    args = parser.parse_args()
    try:
        replay = load_and_validate(args.artifact, args.hash_file)
    except (ValidationFailure, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "independent M16 regime-assurance replay passed: "
        f"{replay.census['subgroup_x_total']} subgroup elements"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
