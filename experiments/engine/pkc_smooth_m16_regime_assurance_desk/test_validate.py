#!/usr/bin/env python3
"""Fault injection for the independent M16 regime-assurance replay."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import time
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("m16_regime_validate", HERE / "validate.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent validator")
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)
ARTIFACT = json.loads((HERE / "artifact.json").read_text(encoding="utf-8"))


def wrong_fraction(numerator: int, denominator: int, template: dict[str, str]) -> dict[str, str]:
    return validate.fraction_record(
        numerator,
        denominator,
        formula=template["formula"],
        interpretation=template["interpretation"],
    )


def must_reject(
    name: str,
    replay: validate.Replay,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    document = deepcopy(ARTIFACT)
    mutate(document)
    try:
        validate.validate_document(document, replay, verify_upstream=False)
    except (validate.ValidationFailure, ValueError, TypeError, KeyError):
        return
    raise AssertionError(f"validator accepted mutation {name}")


def mutate_multiset_plus(document: dict[str, Any]) -> None:
    counts = document["yield_models"]["exact_combinatorial_counts"]
    model = document["yield_models"]["models"]["signed_multiset_uniform_nonidentity_null"]
    document["yield_models"]["models"]["signed_multiset_uniform_nonidentity_null"] = wrong_fraction(
        int(counts["signed_point_multisets"]) + int(counts["negation_fixed_multisets"]),
        validate.N - 1,
        model,
    )


def mutate_omit_fixed_distinct(document: dict[str, Any]) -> None:
    counts = document["yield_models"]["exact_combinatorial_counts"]
    model = document["yield_models"]["models"]["distinct_signed_uniform_nonidentity_null"]
    document["yield_models"]["models"]["distinct_signed_uniform_nonidentity_null"] = wrong_fraction(
        int(counts["distinct_signed_configurations"]), validate.N - 1, model
    )


def mutate_p_denominator(document: dict[str, Any]) -> None:
    model = document["yield_models"]["models"]["distinct_signed_uniform_nonidentity_null"]
    numerator = validate.comb(567_054, 16) - validate.comb(283_527, 8)
    document["yield_models"]["models"]["distinct_signed_uniform_nonidentity_null"] = wrong_fraction(
        numerator, validate.P, model
    )


def mutate_omit_sign_factor(document: dict[str, Any]) -> None:
    model = document["yield_models"]["models"]["distinct_x_signed_uniform_null"]
    document["yield_models"]["models"]["distinct_x_signed_uniform_null"] = wrong_fraction(
        validate.comb(283_527, 16), validate.N - 1, model
    )


def mutate_x_repeat_denominator(document: dict[str, Any]) -> None:
    model = document["yield_models"]["ordered_sampling_repeat_probability"]
    ordered = 283_527**16
    document["yield_models"]["ordered_sampling_repeat_probability"] = wrong_fraction(
        ordered - validate.falling_factorial(283_527, 16), ordered, model
    )


def mutate_generator_to_order_d_over_three(document: dict[str, Any]) -> None:
    generator = int(document["method"]["generator"])
    document["method"]["generator"] = str(pow(generator, 3, validate.P))


def mutate_kudo_boundary(document: dict[str, Any]) -> None:
    document["trust_boundary"]["excluded"][-1] = (
        "global novelty established after Kudo full-text review"
    )


def main() -> int:
    started = time.perf_counter()
    replay = validate.load_and_validate()
    replay_seconds = time.perf_counter() - started

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("character-sum", lambda value: value["factor_base_census"].__setitem__("character_sum_over_H", 2535)),
        ("chi-zero-count", lambda value: value["factor_base_census"].__setitem__("zero_rhs_x", 3)),
        ("generator-order", mutate_generator_to_order_d_over_three),
        ("signed-points-equals-U", lambda value: value["factor_base_census"].__setitem__("signed_affine_factor_points", 283_527)),
        ("glv-orbit-count", lambda value: value["factor_base_census"]["glv_orbits"].__setitem__("liftable_x_orbits", 94_510)),
        ("glv-fixed-point", lambda value: value["factor_base_census"]["glv_orbits"].__setitem__("orbit_action_verified_elementwise", False)),
        ("multiset-M-plus-F", mutate_multiset_plus),
        ("omit-C-U-8", mutate_omit_fixed_distinct),
        ("p-instead-of-n-minus-one", mutate_p_denominator),
        ("omit-two-power-sixteen", mutate_omit_sign_factor),
        ("repeat-on-x-not-signed-points", mutate_x_repeat_denominator),
        ("float-only-ratio", lambda value: value["yield_models"]["models"]["paper_source_heuristic"].pop("numerator")),
        ("proposal-binding-drift", lambda value: value["upstream_bindings"].__setitem__("experiments/engine/proposals/HGP-M16-SOLVER-SLOPE-001.json", "0" * 64)),
        ("upstream-binding-drift", lambda value: value["upstream_bindings"].__setitem__("Ecdlp/Secp256k1Verified.lean", "f" * 64)),
        ("cell-closure", lambda value: value["terminal"].__setitem__("cell_transition", "open_to_closed")),
        ("authorization", lambda value: value["terminal"].__setitem__("authorization", "authorized")),
        ("calibration", lambda value: value["terminal"].__setitem__("calibration", "included")),
        ("source-independence", lambda value: value["terminal"].__setitem__("source_independence", "independent")),
        ("novelty-kudo-overclaim", lambda value: value["terminal"].__setitem__("novelty_claimed", True)),
        ("kudo-boundary-removed", mutate_kudo_boundary),
    ]
    for name, mutation in mutations:
        must_reject(name, replay, mutation)

    print(
        "M16 regime-assurance validator mutation tests PASS: "
        f"{len(mutations)}/{len(mutations)}; independent replay "
        f"{replay_seconds:.3f}s (reused for all mutations)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
