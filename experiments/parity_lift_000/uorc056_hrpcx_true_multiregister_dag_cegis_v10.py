#!/usr/bin/env python3
"""True multiregister DAG synthesis screen for UORC-056 H-RPCX V10.

Unlike the corrected V5 formula-tree census, this engine stores every computed
register once and permits later gates to reuse it without paying for its ancestry
a second time.  A node therefore denotes a genuine DAG, not an expanded formula.

The search is still heuristic: it uses a retained library, deterministic beam
selection, public powering/readout macros, and counterexample-guided refinement.
It is not an exhaustive circuit lower bound and it does not claim a parity
algorithm if no candidate is found.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from uorc056_hrpcx_structured_high_degree_dag_screen_v9 import (
    BASE_DEFINITIONS,
    CURVES,
    OFFSETS,
    ORBITS,
    TARGET,
    Curve,
    beta,
    binary_power_cost,
    scalar_mul,
)


PROFILE_ID = "UORC-056-HRPCX-TRUE-MULTIREGISTER-DAG-CEGIS-V10"
Point = Optional[tuple[int, int]]
TRAIN_CURVE_COUNT = 4
TRAIN_END = OFFSETS[TRAIN_CURVE_COUNT]
TRAIN_INDICES = tuple(range(TRAIN_END))
FROZEN_HOLDOUT_INDICES = tuple(range(TRAIN_END, len(TARGET)))
EXTERNAL_HOLDOUT = Curve(61, 61, (2, 25))

SQUARE_SEED_BASE_IDS = (0, 1, 2, 3, 4, 5, 14, 15, 18, 19, 20, 21)
MAX_SQUARE_DEPTH = 254
CEGIS_ROUNDS = 4
SYNTHESIS_ROUNDS = 2
POOL_LIMIT = 128
RETAIN_PER_ROUND = 384
COUNTEREXAMPLES_PER_ROUND = 8

CONSTANT_DEFINITIONS = [
    ("const", "0"),
    ("const", "1"),
    ("const", "-1"),
    ("const", "7"),
    ("const", "gx"),
    ("const", "gy"),
    ("const", "beta"),
]
ALL_BASE_DEFINITIONS = list(BASE_DEFINITIONS) + CONSTANT_DEFINITIONS


def split_blocks(semantic: bytes) -> tuple[bytes, ...]:
    return tuple(
        semantic[OFFSETS[index] : OFFSETS[index + 1]]
        for index in range(len(CURVES))
    )


def constant_value(curve: Curve, name: str) -> int:
    gx, gy = curve.generator
    return {
        "0": 0,
        "1": 1,
        "-1": curve.p - 1,
        "7": 7 % curve.p,
        "gx": gx,
        "gy": gy,
        "beta": beta(curve.p),
    }[name]


def base_values_on_curve(
    definition: tuple, curve: Curve, orbit: tuple[tuple[int, int], ...]
) -> bytes:
    p = curve.p
    gx, gy = curve.generator
    cube_root = beta(p)
    values: list[int] = []
    for point in orbit:
        x, y = point
        if definition[0] == "coord":
            _, axis, multiplier = definition
            multiple = scalar_mul(multiplier, point, p)
            if multiple is None:
                raise AssertionError((curve, definition, point, "unexpected infinity"))
            value = multiple[0 if axis == "x" else 1]
        elif definition[0] == "expr":
            kind = definition[1]
            value = {
                "x-gx": x - gx,
                "y-gy": y - gy,
                "x+gx": x + gx,
                "y+gy": y + gy,
                "x+y": x + y,
                "x-y": x - y,
                "x3": x**3,
                "beta*x": cube_root * x,
            }[kind]
        elif definition[0] == "const":
            value = constant_value(curve, definition[1])
        else:
            raise ValueError(definition)
        values.append(value % p)
    return bytes(values)


def base_semantic(definition: tuple) -> bytes:
    return b"".join(
        base_values_on_curve(definition, curve, orbit)
        for curve, orbit in zip(CURVES, ORBITS)
    )


BASE_SEMANTICS = [base_semantic(definition) for definition in ALL_BASE_DEFINITIONS]


def binary_semantic(left: bytes, right: bytes, operation: str) -> bytes | None:
    output: list[bytes] = []
    for curve, left_block, right_block in zip(
        CURVES, split_blocks(left), split_blocks(right)
    ):
        p = curve.p
        values: list[int] = []
        for a, b in zip(left_block, right_block):
            if operation == "add":
                value = a + b
            elif operation == "sub":
                value = a - b
            elif operation in ("mul", "square"):
                value = a * b
            elif operation == "div":
                if b == 0:
                    return None
                value = a * pow(b, -1, p)
            else:
                raise ValueError(operation)
            values.append(value % p)
        output.append(bytes(values))
    return b"".join(output)


def unary_weight(operation: str) -> int:
    if operation in ("neg", "inv"):
        return 1
    exponent = {
        "chi2": lambda curve: (curve.p - 1) // 2,
        "chi3": lambda curve: (curve.p - 1) // 3,
        "chi6": lambda curve: (curve.p - 1) // 6,
    }[operation]
    return max(binary_power_cost(exponent(curve)) for curve in CURVES)


def unary_semantic(semantic: bytes, operation: str) -> bytes | None:
    output: list[bytes] = []
    for curve, block in zip(CURVES, split_blocks(semantic)):
        p = curve.p
        values: list[int] = []
        for value in block:
            if operation == "neg":
                result = -value
            elif operation == "inv":
                if value == 0:
                    return None
                result = pow(value, -1, p)
            elif operation == "chi2":
                result = pow(value, (p - 1) // 2, p)
            elif operation == "chi3":
                result = pow(value, (p - 1) // 3, p)
            elif operation == "chi6":
                result = pow(value, (p - 1) // 6, p)
            else:
                raise ValueError(operation)
            values.append(result % p)
        output.append(bytes(values))
    return b"".join(output)


def errors_on(semantic: bytes, indices: tuple[int, ...]) -> int:
    return sum(semantic[index] != TARGET[index] for index in indices)


@dataclass(frozen=True)
class Node:
    node_id: int
    semantic: bytes
    operation: str
    parents: tuple[int, ...]
    definition: tuple | None
    gate_id: int | None
    gate_weight: int
    support: frozenset[int]
    expanded_cost: int
    active_errors: int
    train_errors: int


class SearchState:
    def __init__(self, active_indices: tuple[int, ...]):
        self.active_indices = active_indices
        self.nodes: list[Node] = []
        self.gate_weights: dict[int, int] = {}
        self.next_gate_id = 0
        for definition, semantic in zip(ALL_BASE_DEFINITIONS, BASE_SEMANTICS):
            self.nodes.append(
                Node(
                    node_id=len(self.nodes),
                    semantic=semantic,
                    operation="base",
                    parents=(),
                    definition=definition,
                    gate_id=None,
                    gate_weight=0,
                    support=frozenset(),
                    expanded_cost=0,
                    active_errors=errors_on(semantic, active_indices),
                    train_errors=errors_on(semantic, TRAIN_INDICES),
                )
            )

    def support_cost(self, support: frozenset[int] | set[int]) -> int:
        return sum(self.gate_weights[gate] for gate in support)

    def prospective_cost(self, parents: tuple[int, ...], weight: int) -> int:
        support: set[int] = set()
        for parent in parents:
            support.update(self.nodes[parent].support)
        return self.support_cost(support) + weight

    def add_node(
        self,
        operation: str,
        parents: tuple[int, ...],
        semantic: bytes | None,
        weight: int,
    ) -> int | None:
        if semantic is None:
            return None
        gate_id = self.next_gate_id
        self.next_gate_id += 1
        self.gate_weights[gate_id] = weight
        support: set[int] = {gate_id}
        for parent in parents:
            support.update(self.nodes[parent].support)
        frozen_support = frozenset(support)
        node_id = len(self.nodes)
        self.nodes.append(
            Node(
                node_id=node_id,
                semantic=semantic,
                operation=operation,
                parents=parents,
                definition=None,
                gate_id=gate_id,
                gate_weight=weight,
                support=frozen_support,
                expanded_cost=self.support_cost(frozen_support),
                active_errors=errors_on(semantic, self.active_indices),
                train_errors=errors_on(semantic, TRAIN_INDICES),
            )
        )
        return node_id

    def build_square_ladders(self) -> list[int]:
        created: list[int] = []
        for seed in SQUARE_SEED_BASE_IDS:
            current = seed
            seen = {self.nodes[current].semantic}
            for _ in range(MAX_SQUARE_DEPTH):
                semantic = binary_semantic(
                    self.nodes[current].semantic,
                    self.nodes[current].semantic,
                    "square",
                )
                if semantic is None or semantic in seen:
                    break
                node = self.add_node("square", (current, current), semantic, 1)
                if node is None:
                    break
                created.append(node)
                seen.add(semantic)
                current = node
        return created

    def add_unary_nodes(
        self, source_ids: list[int], operations: tuple[str, ...]
    ) -> list[int]:
        created: list[int] = []
        best_cost: dict[bytes, int] = {}
        for node in self.nodes:
            previous = best_cost.get(node.semantic)
            if previous is None or node.expanded_cost < previous:
                best_cost[node.semantic] = node.expanded_cost
        for source in source_ids:
            for operation in operations:
                semantic = unary_semantic(self.nodes[source].semantic, operation)
                if semantic is None:
                    continue
                weight = unary_weight(operation)
                cost = self.nodes[source].expanded_cost + weight
                if best_cost.get(semantic, 1 << 60) <= cost:
                    continue
                node = self.add_node(operation, (source,), semantic, weight)
                if node is not None:
                    created.append(node)
                    best_cost[semantic] = self.nodes[node].expanded_cost
        return created

    def select_pool(self) -> list[int]:
        ranked = sorted(
            range(len(self.nodes)),
            key=lambda node_id: (
                self.nodes[node_id].active_errors,
                self.nodes[node_id].train_errors,
                self.nodes[node_id].expanded_cost,
                self.nodes[node_id].semantic,
            ),
        )
        selected: list[int] = []
        seen: set[int] = set()
        for node_id in list(range(len(ALL_BASE_DEFINITIONS))) + ranked:
            if node_id not in seen:
                selected.append(node_id)
                seen.add(node_id)
            if len(selected) >= POOL_LIMIT:
                break
        return selected

    def binary_round(self, pool: list[int]) -> tuple[list[int], int]:
        candidates: dict[bytes, tuple] = {}
        for left_position, left in enumerate(pool):
            for right_position, right in enumerate(pool):
                operations: list[str] = []
                if left_position <= right_position:
                    operations.extend(("add", "mul"))
                operations.append("sub")
                if left != right:
                    operations.append("div")
                for operation in operations:
                    semantic = binary_semantic(
                        self.nodes[left].semantic,
                        self.nodes[right].semantic,
                        operation,
                    )
                    if semantic is None:
                        continue
                    cost = self.prospective_cost((left, right), 1)
                    active_direct = errors_on(semantic, self.active_indices)
                    train_direct = errors_on(semantic, TRAIN_INDICES)
                    character = unary_semantic(semantic, "chi2")
                    active_character = (
                        errors_on(character, self.active_indices)
                        if character is not None
                        else len(self.active_indices) + 1
                    )
                    train_character = (
                        errors_on(character, TRAIN_INDICES)
                        if character is not None
                        else len(TRAIN_INDICES) + 1
                    )
                    rank = (
                        min(active_direct, active_character),
                        min(train_direct, train_character),
                        cost,
                        active_direct,
                        train_direct,
                        semantic,
                    )
                    record = (rank, operation, left, right, semantic)
                    previous = candidates.get(semantic)
                    if previous is None or rank < previous[0]:
                        candidates[semantic] = record

        retained = sorted(candidates.values(), key=lambda record: record[0])[
            :RETAIN_PER_ROUND
        ]
        best_existing: dict[bytes, int] = {}
        for node in self.nodes:
            previous = best_existing.get(node.semantic)
            if previous is None or node.expanded_cost < previous:
                best_existing[node.semantic] = node.expanded_cost

        created: list[int] = []
        for _, operation, left, right, semantic in retained:
            cost = self.prospective_cost((left, right), 1)
            if best_existing.get(semantic, 1 << 60) <= cost:
                continue
            node = self.add_node(operation, (left, right), semantic, 1)
            if node is not None:
                created.append(node)
                best_existing[semantic] = self.nodes[node].expanded_cost
        return created, len(candidates)

    def formula_tree_cost(self, node_id: int) -> int:
        node = self.nodes[node_id]
        if node.operation == "base":
            return 0
        return node.gate_weight + sum(
            self.formula_tree_cost(parent) for parent in node.parents
        )

    def serialize_dag(self, output_id: int) -> dict[str, object]:
        required: set[int] = set()

        def visit(node_id: int) -> None:
            if node_id in required:
                return
            required.add(node_id)
            for parent in self.nodes[node_id].parents:
                visit(parent)

        visit(output_id)
        ordered = sorted(required)
        names: dict[int, str] = {}
        gates: list[dict[str, object]] = []
        for node_id in ordered:
            node = self.nodes[node_id]
            if node.operation == "base":
                names[node_id] = f"b{ALL_BASE_DEFINITIONS.index(node.definition)}"
            else:
                name = f"r{len(gates)}"
                names[node_id] = name
                gates.append(
                    {
                        "output": name,
                        "operation": node.operation,
                        "parents": [names[parent] for parent in node.parents],
                        "charged_weight": node.gate_weight,
                    }
                )
        node = self.nodes[output_id]
        tree_cost = self.formula_tree_cost(output_id)
        return {
            "output": names[output_id],
            "base_definitions": [list(definition) for definition in ALL_BASE_DEFINITIONS],
            "gates": gates,
            "distinct_computed_nodes": len(node.support),
            "expanded_arithmetic_cost": node.expanded_cost,
            "expanded_formula_tree_cost": tree_cost,
            "sharing_savings": tree_cost - node.expanded_cost,
            "active_errors": node.active_errors,
            "training_errors": node.train_errors,
        }


def evaluate_node_on_curve(
    output_id: int, nodes: list[Node], curve: Curve
) -> tuple[bytes, int]:
    orbit = tuple(scalar_mul(k, curve.generator, curve.p) for k in range(1, curve.n))
    if any(point is None for point in orbit):
        raise AssertionError((curve, "early orbit closure"))
    if scalar_mul(curve.n, curve.generator, curve.p) is not None:
        raise AssertionError((curve, "generator order mismatch"))

    memo: dict[int, bytes] = {}

    def evaluate(node_id: int) -> bytes:
        if node_id in memo:
            return memo[node_id]
        node = nodes[node_id]
        if node.operation == "base":
            value = base_values_on_curve(node.definition, curve, orbit)  # type: ignore[arg-type]
        elif node.operation in ("add", "sub", "mul", "square", "div"):
            left = evaluate(node.parents[0])
            right = evaluate(node.parents[1])
            values: list[int] = []
            for a, b in zip(left, right):
                if node.operation == "add":
                    result = a + b
                elif node.operation == "sub":
                    result = a - b
                elif node.operation in ("mul", "square"):
                    result = a * b
                else:
                    if b == 0:
                        raise ZeroDivisionError((curve, node_id))
                    result = a * pow(b, -1, curve.p)
                values.append(result % curve.p)
            value = bytes(values)
        else:
            parent = evaluate(node.parents[0])
            values = []
            for entry in parent:
                if node.operation == "neg":
                    result = -entry
                elif node.operation == "inv":
                    if entry == 0:
                        raise ZeroDivisionError((curve, node_id))
                    result = pow(entry, -1, curve.p)
                elif node.operation == "chi2":
                    result = pow(entry, (curve.p - 1) // 2, curve.p)
                elif node.operation == "chi3":
                    result = pow(entry, (curve.p - 1) // 3, curve.p)
                elif node.operation == "chi6":
                    result = pow(entry, (curve.p - 1) // 6, curve.p)
                else:
                    raise ValueError(node.operation)
                values.append(result % curve.p)
            value = bytes(values)
        memo[node_id] = value
        return value

    semantic = evaluate(output_id)
    target = bytes(
        1 if k % 2 == 0 else curve.p - 1 for k in range(1, curve.n)
    )
    return semantic, sum(a != b for a, b in zip(semantic, target))


def choose_counterexamples(
    semantic: bytes, active_indices: tuple[int, ...]
) -> list[int]:
    active = set(active_indices)
    by_curve: list[list[int]] = []
    for curve_index in range(TRAIN_CURVE_COUNT):
        start, stop = OFFSETS[curve_index], OFFSETS[curve_index + 1]
        by_curve.append(
            [
                index
                for index in range(start, stop)
                if index not in active and semantic[index] != TARGET[index]
            ]
        )
    selected: list[int] = []
    while len(selected) < COUNTEREXAMPLES_PER_ROUND:
        progressed = False
        for group in by_curve:
            if group:
                selected.append(group.pop(0))
                progressed = True
                if len(selected) == COUNTEREXAMPLES_PER_ROUND:
                    break
        if not progressed:
            break
    return selected


def sharing_self_test() -> dict[str, int | bool]:
    # u=x*y is one gate.  v=u+u reuses u, so the DAG costs two gates,
    # while the expanded formula (x*y)+(x*y) contains three gates.
    state = SearchState((0,))
    product = state.add_node(
        "mul",
        (0, 1),
        binary_semantic(state.nodes[0].semantic, state.nodes[1].semantic, "mul"),
        1,
    )
    if product is None:
        raise AssertionError("sharing test product failed")
    doubled = state.add_node(
        "add",
        (product, product),
        binary_semantic(
            state.nodes[product].semantic, state.nodes[product].semantic, "add"
        ),
        1,
    )
    if doubled is None:
        raise AssertionError("sharing test sum failed")
    dag_cost = state.nodes[doubled].expanded_cost
    tree_cost = state.formula_tree_cost(doubled)
    if (dag_cost, tree_cost) != (2, 3):
        raise AssertionError((dag_cost, tree_cost))
    return {
        "true_register_reuse_verified": True,
        "dag_cost": dag_cost,
        "expanded_tree_cost": tree_cost,
        "saved_gates": tree_cost - dag_cost,
    }


def search_once(active_indices: tuple[int, ...]) -> tuple[SearchState, int, list[dict[str, object]]]:
    state = SearchState(active_indices)
    square_nodes = state.build_square_ladders()
    state.add_unary_nodes(
        list(range(len(state.nodes))), ("chi2", "chi3", "chi6")
    )

    layers: list[dict[str, object]] = []
    for synthesis_round in range(1, SYNTHESIS_ROUNDS + 1):
        pool = state.select_pool()
        new_nodes, raw_candidates = state.binary_round(pool)
        unary_nodes = state.add_unary_nodes(
            new_nodes, ("chi2", "chi3", "chi6", "inv", "neg")
        )
        layers.append(
            {
                "round": synthesis_round,
                "pool": len(pool),
                "raw_binary_semantics": raw_candidates,
                "retained_binary_nodes": len(new_nodes),
                "new_unary_nodes": len(unary_nodes),
                "total_nodes": len(state.nodes),
                "best_active_errors": min(node.active_errors for node in state.nodes),
                "best_training_errors": min(node.train_errors for node in state.nodes),
            }
        )

    ranked = sorted(
        range(len(state.nodes)),
        key=lambda node_id: (
            state.nodes[node_id].active_errors,
            state.nodes[node_id].train_errors,
            state.nodes[node_id].expanded_cost,
        ),
    )
    active_perfect = [
        node_id for node_id in ranked if state.nodes[node_id].active_errors == 0
    ]
    candidate = (
        min(
            active_perfect,
            key=lambda node_id: (
                state.nodes[node_id].train_errors,
                state.nodes[node_id].expanded_cost,
            ),
        )
        if active_perfect
        else ranked[0]
    )
    return state, candidate, [
        {
            "square_ladder_nodes": len(square_nodes),
            "initial_nodes_after_readouts": layers[0]["total_nodes"]
            - layers[0]["retained_binary_nodes"]
            - layers[0]["new_unary_nodes"],
        },
        *layers,
    ]


def run() -> dict[str, object]:
    active: list[int] = []
    for curve_index in range(TRAIN_CURVE_COUNT):
        active.extend((OFFSETS[curve_index], OFFSETS[curve_index] + 1))

    history: list[dict[str, object]] = []
    best_record: tuple | None = None
    best_state: SearchState | None = None
    best_output: int | None = None

    for cegis_round in range(1, CEGIS_ROUNDS + 1):
        state, output, layers = search_once(tuple(active))
        node = state.nodes[output]
        frozen_holdout_errors = errors_on(node.semantic, FROZEN_HOLDOUT_INDICES)
        external_error: int | None
        external_exception: str | None = None
        try:
            _, external_error = evaluate_node_on_curve(output, state.nodes, EXTERNAL_HOLDOUT)
        except (ZeroDivisionError, AssertionError) as error:
            external_error = None
            external_exception = repr(error)

        key = (
            node.train_errors,
            frozen_holdout_errors,
            EXTERNAL_HOLDOUT.n if external_error is None else external_error,
            node.expanded_cost,
        )
        if best_record is None or key < best_record:
            best_record = key
            best_state = state
            best_output = output

        counterexamples = choose_counterexamples(node.semantic, tuple(active))
        history.append(
            {
                "cegis_round": cegis_round,
                "active_points": len(active),
                "candidate_node": output,
                "candidate_active_errors": node.active_errors,
                "candidate_training_errors": node.train_errors,
                "candidate_frozen_holdout_errors": frozen_holdout_errors,
                "candidate_external_holdout_errors": external_error,
                "candidate_external_exception": external_exception,
                "candidate_expanded_cost": node.expanded_cost,
                "counterexamples_added": counterexamples,
                "synthesis_layers": layers,
            }
        )
        if node.train_errors == 0 or not counterexamples:
            break
        active.extend(counterexamples)

    if best_state is None or best_output is None:
        raise AssertionError("no candidate state")

    best_node = best_state.nodes[best_output]
    best_frozen_holdout = errors_on(best_node.semantic, FROZEN_HOLDOUT_INDICES)
    try:
        _, best_external_holdout = evaluate_node_on_curve(
            best_output, best_state.nodes, EXTERNAL_HOLDOUT
        )
        best_external_exception = None
    except (ZeroDivisionError, AssertionError) as error:
        best_external_holdout = None
        best_external_exception = repr(error)

    exact_training = best_node.train_errors == 0
    exact_all_declared = (
        exact_training
        and best_frozen_holdout == 0
        and best_external_holdout == 0
    )

    return {
        "profile_id": PROFILE_ID,
        "status": "deterministic_true_DAG_CEGIS_screen_not_exhaustive",
        "sharing_self_test": sharing_self_test(),
        "corpus": {
            "training_curves": [
                {
                    "p": curve.p,
                    "n": curve.n,
                    "generator": list(curve.generator),
                }
                for curve in CURVES[:TRAIN_CURVE_COUNT]
            ],
            "frozen_holdout": {
                "p": CURVES[-1].p,
                "n": CURVES[-1].n,
                "generator": list(CURVES[-1].generator),
            },
            "external_holdout": {
                "p": EXTERNAL_HOLDOUT.p,
                "n": EXTERNAL_HOLDOUT.n,
                "generator": list(EXTERNAL_HOLDOUT.generator),
            },
            "training_points": len(TRAIN_INDICES),
            "frozen_holdout_points": len(FROZEN_HOLDOUT_INDICES),
            "external_holdout_points": EXTERNAL_HOLDOUT.n - 1,
        },
        "search_contract": {
            "true_multiregister_DAG": True,
            "each_new_binary_gate_may_use_any_two_nodes_in_retained_pool": True,
            "shared_ancestry_charged_once": True,
            "square_ladders_expose_intermediate_registers": True,
            "maximum_exposed_square_depth": MAX_SQUARE_DEPTH,
            "public_readout_macros_are_charged_but_internal_registers_not_exposed": True,
            "semantic_deduplication_may_discard_overlap_useful_variants": True,
            "pool_limit": POOL_LIMIT,
            "retained_per_round": RETAIN_PER_ROUND,
            "synthesis_rounds": SYNTHESIS_ROUNDS,
            "cegis_rounds": CEGIS_ROUNDS,
            "search_is_exhaustive": False,
        },
        "cegis_history": history,
        "best_candidate": {
            "training_errors": best_node.train_errors,
            "frozen_holdout_errors": best_frozen_holdout,
            "external_holdout_errors": best_external_holdout,
            "external_holdout_exception": best_external_exception,
            "exact_training": exact_training,
            "exact_all_declared_curves": exact_all_declared,
            "dag": best_state.serialize_dag(best_output),
        },
        "decision": {
            "parity_algorithm_found": exact_all_declared,
            "candidate_requires_symbolic_proof_before_any_secp_claim": True,
            "negative_result_is_exhaustive": False,
            "general_arithmetic_circuit_lower_bound_proved": False,
            "true_DAG_infrastructure_completed": True,
            "next_if_no_exact_candidate": "add multiregister templates with CM/Miller states and exact symbolic lifting",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
