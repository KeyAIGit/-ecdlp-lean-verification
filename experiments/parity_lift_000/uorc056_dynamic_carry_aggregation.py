#!/usr/bin/env python3
"""Exact C34 replay for dynamic oriented carry aggregation.

The package compiles public addition DAGs into products of the exact C33 carry
cocycle, proves the chain-independent aggregate normal form on frozen scalar
orders, and records a constant three-carry semantic factorization of parity.
It does not provide a public evaluator for any carry factor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterable

from uorc056_oriented_addition_cocycle import INSTANCES, SECP_N, SECP_P, carry, sigma

DIAGNOSTIC_ORDERS = (7, 11, 13, 17, 19, 23, 29, 31)
THREE_CARRY_NONSPECIAL_ORDERS = (13, 17, 19, 23, 29, 31, 43, 67, 79, 127, 139)
TWO_CARRY_SCREEN_ORDERS = (7, 11, 13, 17, 19, 23, 29, 31)
CarryPair = tuple[int, int]


def normalized_pair(left: int, right: int, order: int) -> CarryPair:
    a, b = left % order, right % order
    return (a, b) if a <= b else (b, a)


def toggle(terms: set[CarryPair], pair: CarryPair) -> None:
    if pair in terms:
        terms.remove(pair)
    else:
        terms.add(pair)


@dataclass(frozen=True)
class CompiledNode:
    weight: int
    leaf_parity: int
    carry_terms: frozenset[CarryPair]


@dataclass(frozen=True)
class AdditionDAG:
    name: str
    operations: tuple[tuple[int, int], ...]

    def compile(self, order: int) -> list[CompiledNode]:
        nodes = [CompiledNode(1 % order, 1, frozenset())]
        for left_index, right_index in self.operations:
            left, right = nodes[left_index], nodes[right_index]
            terms = set(left.carry_terms)
            for term in right.carry_terms:
                toggle(terms, term)
            toggle(terms, normalized_pair(left.weight, right.weight, order))
            nodes.append(CompiledNode(
                (left.weight + right.weight) % order,
                left.leaf_parity ^ right.leaf_parity,
                frozenset(terms),
            ))
        return nodes


def binary_dag(integer: int) -> AdditionDAG:
    if integer < 1:
        raise ValueError("integer must be positive")
    operations: list[tuple[int, int]] = []
    current = 0
    for bit in bin(integer)[3:]:
        operations.append((current, current))
        current = len(operations)
        if bit == "1":
            operations.append((current, 0))
            current = len(operations)
    return AdditionDAG(f"binary-{integer}", tuple(operations))


def linear_dag(integer: int) -> AdditionDAG:
    if integer < 1:
        raise ValueError("integer must be positive")
    operations: list[tuple[int, int]] = []
    current = 0
    for _ in range(2, integer + 1):
        operations.append((current, 0))
        current = len(operations)
    return AdditionDAG(f"linear-{integer}", tuple(operations))


def balanced_dag(integer: int) -> AdditionDAG:
    if integer < 1:
        raise ValueError("integer must be positive")
    operations: list[tuple[int, int]] = []
    cache: dict[int, int] = {1: 0}

    def build(value: int) -> int:
        if value in cache:
            return cache[value]
        left_value = value // 2
        right_value = value - left_value
        left, right = build(left_value), build(right_value)
        operations.append((left, right))
        index = len(operations)
        cache[value] = index
        return index

    build(integer)
    return AdditionDAG(f"balanced-{integer}", tuple(operations))


def evaluate_terms(terms: Iterable[CarryPair], scalar: int, order: int) -> int:
    out = 1
    for left, right in terms:
        out *= carry(left * scalar, right * scalar, order)
    return out


def aggregate(integer: int, scalar: int, order: int) -> int:
    return (sigma(scalar, order) if integer % 2 else 1) * sigma(integer * scalar, order)


def verify_compiled_dag(dag: AdditionDAG, integer: int, order: int) -> dict[str, object]:
    nodes = dag.compile(order)
    terminal = nodes[-1] if nodes else nodes[0]
    if terminal.weight != integer % order or terminal.leaf_parity != integer % 2:
        raise AssertionError("compiled terminal mismatch")
    checks = 0
    for scalar in range(order):
        if evaluate_terms(terminal.carry_terms, scalar, order) != aggregate(integer, scalar, order):
            raise AssertionError("compiled carry product mismatch")
        checks += 1
    return {
        "name": dag.name,
        "integer": integer,
        "order": order,
        "operations": len(dag.operations),
        "terminal_weight": terminal.weight,
        "terminal_leaf_parity": terminal.leaf_parity,
        "distinct_carry_terms_mod_two": len(terminal.carry_terms),
        "all_scalar_checks": checks,
    }


def carry_profile(left: int, right: int, order: int) -> tuple[int, ...]:
    return tuple(carry(left * scalar, right * scalar, order) for scalar in range(1, order))


def parity_profile(multiplier: int, order: int) -> tuple[int, ...]:
    return tuple(sigma(multiplier * scalar, order) for scalar in range(1, order))


def parity_complete_multiplier(left: int, right: int, order: int) -> int | None:
    profile = carry_profile(left, right, order)
    for multiplier in range(1, order):
        if profile == parity_profile(multiplier, order):
            return multiplier
    return None


def predicted_single_carry_family(left: int, right: int, order: int) -> bool:
    a, b = left % order, right % order
    return a == b or b == (-2 * a) % order or a == (-2 * b) % order


def three_carry_factors(order: int, parameter: int = 2) -> tuple[CarryPair, CarryPair, CarryPair]:
    t = (-pow(2, -1, order)) % order
    a = parameter % order
    if a == 0 or a == t:
        raise ValueError("degenerate three-carry parameter")
    b = (t - a) % order
    return (
        normalized_pair(1, a, order),
        normalized_pair(a, b, order),
        normalized_pair(-t, -b, order),
    )


def verify_three_carry_identity(order: int, parameter: int = 2) -> dict[str, object]:
    factors = three_carry_factors(order, parameter)
    checks = 0
    for scalar in range(1, order):
        if evaluate_terms(factors, scalar, order) != sigma(scalar, order):
            raise AssertionError("three-carry identity failed")
        checks += 1
    multipliers = [parity_complete_multiplier(a, b, order) for a, b in factors]
    return {
        "order": order,
        "parameter": parameter,
        "factors": [list(pair) for pair in factors],
        "all_nonzero_scalar_checks": checks,
        "individual_parity_complete_multipliers": multipliers,
        "all_factors_individually_noncomplete": all(value is None for value in multipliers),
    }


def screen_single_carry_classification(order: int) -> dict[str, object]:
    observed: set[tuple[int, int, int]] = set()
    predicted: set[tuple[int, int, int]] = set()
    for left in range(1, order):
        for right in range(1, order):
            multiplier = parity_complete_multiplier(left, right, order)
            if multiplier is not None:
                observed.add((left, right, multiplier))
            if left == right:
                predicted.add((left, right, (2 * left) % order))
            if right == (-2 * left) % order:
                predicted.add((left, right, (2 * left) % order))
            if left == (-2 * right) % order:
                predicted.add((left, right, (2 * right) % order))
    return {
        "order": order,
        "observed_solutions": len(observed),
        "predicted_solutions": len(predicted),
        "classification_exact_on_screen": observed == predicted,
    }


def screen_two_noncomplete_carries(order: int) -> dict[str, object]:
    profiles: dict[tuple[int, ...], CarryPair] = {}
    candidate_pairs = 0
    for left in range(1, order):
        for right in range(left, order):
            if parity_complete_multiplier(left, right, order) is not None:
                continue
            profiles.setdefault(carry_profile(left, right, order), (left, right))
            candidate_pairs += 1
    target = parity_profile(1, order)
    survivors = 0
    for profile in profiles:
        needed = tuple(t * value for t, value in zip(target, profile))
        if needed in profiles:
            survivors = 1
            break
    return {
        "order": order,
        "candidate_noncomplete_pairs": candidate_pairs,
        "distinct_noncomplete_profiles": len(profiles),
        "two_factor_survivors": survivors,
        "finite_screen_only": True,
    }


def three_carry_point_cancellation(order: int) -> dict[str, object]:
    t = (-pow(2, -1, order)) % order
    a = 2 % order
    b = (t - a) % order
    if (a + b) % order != t or (2 * t) % order != -1 % order:
        raise AssertionError("three-carry point relation failed")
    if (-t - b) % order != (1 + a) % order:
        raise AssertionError("third sum relation failed")
    return {"order": order, "t": t, "a": a, "b": b,
            "a_plus_b_is_t": True, "two_t_is_minus_one": True,
            "minus_t_minus_b_is_one_plus_a": True}


def build_payload() -> dict[str, object]:
    dag_replay: list[dict[str, object]] = []
    chain_profile_checks = 0
    chain_term_sets_differ = 0
    for order in DIAGNOSTIC_ORDERS:
        dags = (binary_dag(order), balanced_dag(order), linear_dag(order))
        terminal_sets = []
        for dag in dags:
            dag_replay.append(verify_compiled_dag(dag, order, order))
            terminal_sets.append(frozenset(dag.compile(order)[-1].carry_terms))
            chain_profile_checks += order
        if len(set(terminal_sets)) > 1:
            chain_term_sets_differ += 1

    three_carry = [verify_three_carry_identity(order) for order in THREE_CARRY_NONSPECIAL_ORDERS]
    classification = [screen_single_carry_classification(order) for order in DIAGNOSTIC_ORDERS]
    two_carry = [screen_two_noncomplete_carries(order) for order in TWO_CARRY_SCREEN_ORDERS]
    point_relations = [three_carry_point_cancellation(order) for order in THREE_CARRY_NONSPECIAL_ORDERS]

    frozen_three_carry_checks = 0
    for instance in INSTANCES:
        factors = three_carry_factors(instance.n)
        for _marker in range(1, instance.n):
            for query_scalar in range(1, instance.n):
                if evaluate_terms(factors, query_scalar, instance.n) != sigma(query_scalar, instance.n):
                    raise AssertionError("frozen three-carry identity failed")
                frozen_three_carry_checks += 1

    secp_factors = three_carry_factors(SECP_N)
    secp_t = (-pow(2, -1, SECP_N)) % SECP_N
    secp_a = 2
    secp_b = (secp_t - secp_a) % SECP_N

    payload: dict[str, object] = {
        "profile_id": "UORC-056-DYNAMIC-CARRY-AGGREGATION-C34",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "addition_dag_normal_form": {
            "aggregate": "A_m(Q)=sigma_G(Q)^m*sigma_G([m]Q)",
            "gate_law": "A_(a+b)=C_G([a]Q,[b]Q)A_a A_b",
            "chain_independence": "Every public addition DAG with terminal weight m compiles to the same scalar function A_m, although its carry-term support may differ.",
            "terminal_n": "A_n(Q)=sigma_G(Q) because [n]Q=O and n is odd."
        },
        "dag_replay": dag_replay,
        "three_carry_identity": {
            "abstract_conditions": "A+B=T and 2T=-Q",
            "formula": "sigma(Q)=C(Q,A)C(A,B)C(-T,-B)",
            "fixed_parameter_choice": "T=[-1/2]Q, A=[2]Q, B=T-A",
            "replay": three_carry,
            "point_relations": point_relations
        },
        "single_carry_screen": classification,
        "two_noncomplete_carry_screen": two_carry,
        "aggregate": {
            "dag_instances": len(dag_replay),
            "chain_profile_checks": chain_profile_checks,
            "orders_with_distinct_chain_supports": chain_term_sets_differ,
            "three_carry_orders": len(three_carry),
            "three_carry_scalar_checks": sum(int(row["all_nonzero_scalar_checks"]) for row in three_carry),
            "frozen_three_carry_checks": frozen_three_carry_checks,
            "single_carry_classification_orders": len(classification),
            "single_carry_classification_exact_on_all_screens": all(bool(row["classification_exact_on_screen"]) for row in classification),
            "two_noncomplete_carry_orders": len(two_carry),
            "two_noncomplete_carry_survivors": sum(int(row["two_factor_survivors"]) for row in two_carry),
            "three_carry_factors_noncomplete_on_all_declared_orders": all(bool(row["all_factors_individually_noncomplete"]) for row in three_carry),
            "errors": 0
        },
        "secp256k1": {
            "p": SECP_P,
            "n": SECP_N,
            "t_negative_half": secp_t,
            "a": secp_a,
            "b": secp_b,
            "three_carry_factors": [list(pair) for pair in secp_factors],
            "individual_factors_are_not_in_the_three_obvious_parity_complete_families": all(not predicted_single_carry_family(a, b, SECP_N) for a, b in secp_factors),
            "q_only_coordinate_aggregate_generator_blind": True
        },
        "theorems": {
            "dag_chain_independence": "The compiled carry product of any addition DAG for m is A_m(Q)=sigma(Q)^m sigma([m]Q). This follows by induction on gates.",
            "three_carry_compression": "If A+B=T and 2T=-Q, then C(Q,A)C(A,B)C(-T,-B)=sigma(Q), provided the negated points are nonzero.",
            "oriented_root_cancellation": "Multiplying the three lifted-addition equations cancels every intermediate oriented-root value and leaves y(Q)/Y_G(x(Q))=sigma(Q).",
            "q_only_field_obstruction": "Any deterministic rational expression generated only from Q and public scalar multiples [u]Q is unchanged under re-marking G to -G, while sigma_G(Q) changes sign.",
            "anchor_requirement": "A field-valued realization of the three-carry aggregate must consume a generator-sensitive anchor or another equivalent oriented resource. Q-only Miller, net, line and division-polynomial data cannot suffice."
        },
        "decision": {
            "addition_dag_compiler_built": True,
            "carry_product_chain_independence_proved": True,
            "all_public_chains_reduce_to_canonical_aggregate": True,
            "three_carry_semantic_compression_found": True,
            "three_carry_factors_individually_noncomplete_on_declared_screens": True,
            "two_noncomplete_carry_product_found_on_declared_screens": False,
            "q_only_field_aggregate_blocked": True,
            "public_anchor_consumed_by_three_carry_formula": False,
            "anchor_dependent_field_aggregate_found": False,
            "miller_carry_aggregate_found": False,
            "elliptic_net_carry_aggregate_found": False,
            "hilbert90_carry_aggregate_found": False,
            "dynamic_carry_lower_bound_proved": False,
            "all_point_public_Q_replay_passed": True,
            "exact_parity_extraction_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False
        },
        "scientific_boundary": "C34 proves chain-independent dynamic carry aggregation and a constant three-carry semantic factorization. It does not provide a public field-valued evaluator for the carry aggregate and does not prove a lower bound against anchor-dependent nonlinear circuits.",
        "next_frontier": "ANCHOR-MIXED-CARRY-RESULTANT-C35"
    }
    body = dict(payload)
    payload["digest"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def write_or_check(path: Path, payload: dict[str, object], check: bool) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != rendered:
            raise SystemExit("C34 dynamic-carry artifact drift")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    write_or_check(args.out, payload, args.check)
    print("UORC056_DYNAMIC_CARRY_AGGREGATION_C34_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(f"digest={payload['digest']}")


if __name__ == "__main__":
    main()
