#!/usr/bin/env python3
"""Fault-injection tests for the PKC M16 source-mechanism validator."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

import validate


Mutation = Callable[[dict[str, Any]], None]


def must_reject(name: str, baseline: dict[str, Any], mutation: Mutation) -> None:
    candidate = copy.deepcopy(baseline)
    mutation(candidate)
    try:
        validate.validate_document(candidate)
    except validate.ValidationFailure:
        return
    raise AssertionError(f"validator accepted mutation: {name}")


def main() -> int:
    baseline = validate.load_and_validate()
    mutations: list[tuple[str, Mutation]] = [
        (
            "source-extract-hash",
            lambda value: value["source_binding"].__setitem__(
                "claim_extract_sha256", "0" * 64
            ),
        ),
        (
            "source-claim-omitted",
            lambda value: value["source_binding"]["claim_ids"].pop(),
        ),
        (
            "factorization",
            lambda value: value["specialization"].__setitem__(
                "factorization", [2, 3, 7, 13_439]
            ),
        ),
        (
            "terminal-map-degree",
            lambda value: value["source_map_chain"]["components"][-1].__setitem__(
                "degree", 13_440
            ),
        ),
        (
            "composition-order",
            lambda value: value["source_map_chain"].__setitem__(
                "composition_convention", "L=L1 o L2 o L3 o L4"
            ),
        ),
        (
            "composed-sign",
            lambda value: value["source_map_chain"].__setitem__(
                "composed_polynomial", "L(x)=x^564522-1"
            ),
        ),
        (
            "system-equation-count",
            lambda value: value["system4_specialization"].__setitem__(
                "equation_members", 64
            ),
        ),
        (
            "target-chronology",
            lambda value: value["system4_specialization"].__setitem__(
                "sampled_target_precedes_system", False
            ),
        ),
        (
            "circuit-complexity-equivalence",
            lambda value: value["representation_boundary"].__setitem__(
                "same_solving_complexity_claimed", True
            ),
        ),
        (
            "printed-target-binding",
            lambda value: value["recovery_contract"]["source_exact"].__setitem__(
                "printed_target_binding_explicit", True
            ),
        ),
        (
            "source-ambiguity-erased",
            lambda value: value["recovery_contract"]["source_exact"].__setitem__(
                "status", "source_exact_target_recovery"
            ),
        ),
        (
            "completion-target-unbound",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__("bind_sampled_target", False),
        ),
        (
            "independent-curve-check-removed",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__("final_acceptance", "accept producer summary"),
        ),
        (
            "solver-gap-erased",
            lambda value: value["cost_contract"].__setitem__(
                "source_solver_status", "solver complexity established"
            ),
        ),
        (
            "cost-ledger-shortened",
            lambda value: value["cost_contract"]["unresolved"].pop(),
        ),
        (
            "solver-assurance-upgrade",
            lambda value: value["assurance_matrix"].__setitem__(
                "solver_and_complete_cost", "proved"
            ),
        ),
        (
            "cell-closure",
            lambda value: value["terminal"].__setitem__(
                "cell_transition", "open_to_closed"
            ),
        ),
        (
            "authorization",
            lambda value: value["terminal"].__setitem__(
                "authorization", "authorized"
            ),
        ),
        (
            "calibration",
            lambda value: value["terminal"].__setitem__(
                "calibration", "included"
            ),
        ),
        (
            "novelty",
            lambda value: value["terminal"].__setitem__(
                "novelty_claimed", True
            ),
        ),
        (
            "route-promotion",
            lambda value: value["terminal"].__setitem__(
                "route_effect", "promoted"
            ),
        ),
        (
            "source-independence",
            lambda value: value["terminal"].__setitem__(
                "source_independence", "independent"
            ),
        ),
    ]

    for name, mutation in mutations:
        must_reject(name, baseline, mutation)

    print(
        "PKC M16 source mechanism mutation tests PASS: "
        f"{len(mutations)}/{len(mutations)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
