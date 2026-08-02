#!/usr/bin/env python3
"""Fault-injection tests for the PKC M16 source-mechanism validator."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

import validate


Mutation = Callable[[dict[str, Any]], None]


def leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    if isinstance(value, dict):
        return [
            path
            for key in sorted(value)
            for path in leaf_paths(value[key], prefix + (key,))
        ]
    if isinstance(value, list):
        return [
            path
            for index, item in enumerate(value)
            for path in leaf_paths(item, prefix + (index,))
        ]
    return [prefix]


def replace_leaf(value: Any, path: tuple[Any, ...]) -> None:
    parent = value
    for key in path[:-1]:
        parent = parent[key]
    key = path[-1]
    current = parent[key]
    if isinstance(current, bool):
        parent[key] = not current
    elif isinstance(current, int):
        parent[key] = current + 1
    elif isinstance(current, str):
        parent[key] = current + " [fault]"
    elif current is None:
        parent[key] = "fault"
    else:
        raise TypeError(f"unsupported leaf type at {path}: {type(current)}")


def exhaustive_leaf_fault_sweep(baseline: dict[str, Any]) -> int:
    accepted: list[str] = []
    paths = leaf_paths(baseline)
    for path in paths:
        candidate = copy.deepcopy(baseline)
        replace_leaf(candidate, path)
        try:
            validate.validate_document(candidate)
        except validate.ValidationFailure:
            continue
        accepted.append("/".join(str(item) for item in path))
    if accepted:
        raise AssertionError(
            "validator accepted scalar leaf mutations: " + ", ".join(accepted)
        )
    return len(paths)


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
            "pointwise-root-equivalence",
            lambda value: value["source_map_chain"].__setitem__(
                "pointwise_root_equivalence", "all nonzero x are roots"
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
            "affine-target-precondition",
            lambda value: value["system4_specialization"].__setitem__(
                "affine_target_required", False
            ),
        ),
        (
            "target-definition",
            lambda value: value["system4_specialization"].__setitem__(
                "target_definition", "R=aP+bQ"
            ),
        ),
        (
            "identity-target-policy",
            lambda value: value["system4_specialization"].__setitem__(
                "identity_target_policy", "assume X always exists"
            ),
        ),
        (
            "circuit-complexity-equivalence",
            lambda value: value["representation_boundary"].__setitem__(
                "same_solving_complexity_claimed", True
            ),
        ),
        (
            "representation-warning",
            lambda value: value["representation_boundary"].__setitem__(
                "warning", "the circuit preserves solving complexity"
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
            "source-solution-quotient",
            lambda value: value["recovery_contract"]["source_exact"].__setitem__(
                "solutions_quotiented_by", "all signed lift choices"
            ),
        ),
        (
            "completion-target-unbound",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__("bind_sampled_target", False),
        ),
        (
            "completion-assurance-upgrade",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__("assurance", "proved_complete_recovery"),
        ),
        (
            "direct-recovery-completeness-upgrade",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__("direct_system4_recovery_completeness", "proved"),
        ),
        (
            "exceptional-fiber-overclaim",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__(
                "exceptional_and_infinity_fibers", "complete recovery is proved"
            ),
        ),
        (
            "acceptance-filter-overclaim",
            lambda value: value["recovery_contract"][
                "repository_completion"
            ].__setitem__("soundness_scope", "all solutions are recovered"),
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
            "cost-ledger-replaced",
            lambda value: value["cost_contract"]["unresolved"].__setitem__(
                3, "complete recovery theorem"
            ),
        ),
        (
            "cost-ledger-duplicate",
            lambda value: value["cost_contract"]["unresolved"].__setitem__(
                3, value["cost_contract"]["unresolved"][0]
            ),
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

    leaf_count = exhaustive_leaf_fault_sweep(baseline)

    print(
        "PKC M16 source mechanism mutation tests PASS: "
        f"{len(mutations)}/{len(mutations)} targeted; "
        f"{leaf_count}/{leaf_count} scalar leaves"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
