#!/usr/bin/env python3
"""Selection-audited wrapper for the true multiregister DAG engine V10.

V10 correctly implements shared-register DAG accounting, but its original final
summary selected among the CEGIS-guiding candidates rather than independently
selecting the lowest-error node discovered in every synthesis run. V10A keeps
those roles separate:

* `cegis_candidate` supplies counterexamples for the next round;
* `best_training_candidate` is selected only by complete training error and
  charged DAG cost;
* neither frozen nor external holdout data participates in selection.

The audit also computes formula-tree expansion with memoized node costs. This
preserves duplicate parent contributions, so `(x*y)+(x*y)` has tree cost three
and DAG cost two, while avoiding exponential recomputation on 254-step square
ladders.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import uorc056_hrpcx_true_multiregister_dag_cegis_v10 as v10


PROFILE_ID = "UORC-056-HRPCX-TRUE-MULTIREGISTER-DAG-CEGIS-V10A"


def memo_formula_tree_cost(
    state: v10.SearchState, node_id: int, cache: dict[int, int]
) -> int:
    """Return expanded formula-tree cost in O(number of DAG nodes).

    A cached child cost is still added once for every parent occurrence. Thus
    common subexpressions are duplicated in the formula-tree comparison but are
    charged only once in the DAG support ledger.
    """
    if node_id in cache:
        return cache[node_id]
    node = state.nodes[node_id]
    if node.operation == "base":
        value = 0
    else:
        value = node.gate_weight + sum(
            memo_formula_tree_cost(state, parent, cache) for parent in node.parents
        )
    cache[node_id] = value
    return value


def serialized_dag_with_memo(
    output: int, state: v10.SearchState
) -> dict[str, object]:
    """Reuse V10 serialization while replacing its recursive cost query."""
    cache: dict[int, int] = {}
    original = state.formula_tree_cost
    state.formula_tree_cost = lambda node_id: memo_formula_tree_cost(  # type: ignore[method-assign]
        state, node_id, cache
    )
    try:
        return state.serialize_dag(output)
    finally:
        state.formula_tree_cost = original  # type: ignore[method-assign]


def holdout_metrics(output: int, state: v10.SearchState) -> dict[str, object]:
    node = state.nodes[output]
    frozen_errors = v10.errors_on(node.semantic, v10.FROZEN_HOLDOUT_INDICES)
    try:
        _, external_errors = v10.evaluate_node_on_curve(
            output, state.nodes, v10.EXTERNAL_HOLDOUT
        )
        external_exception = None
    except (ZeroDivisionError, AssertionError) as error:
        external_errors = None
        external_exception = repr(error)
    return {
        "frozen_holdout_errors": frozen_errors,
        "external_holdout_errors": external_errors,
        "external_holdout_exception": external_exception,
    }


def describe(output: int, state: v10.SearchState) -> dict[str, object]:
    node = state.nodes[output]
    metrics = holdout_metrics(output, state)
    return {
        "node": output,
        "active_errors": node.active_errors,
        "training_errors": node.train_errors,
        "expanded_cost": node.expanded_cost,
        **metrics,
        "dag": serialized_dag_with_memo(output, state),
    }


def run() -> dict[str, object]:
    active: list[int] = []
    for curve_index in range(v10.TRAIN_CURVE_COUNT):
        active.extend((v10.OFFSETS[curve_index], v10.OFFSETS[curve_index] + 1))

    history: list[dict[str, object]] = []
    best_state: v10.SearchState | None = None
    best_output: int | None = None
    best_key: tuple[int, int] | None = None

    for cegis_round in range(1, v10.CEGIS_ROUNDS + 1):
        state, cegis_output, layers = v10.search_once(tuple(active))
        training_output = min(
            range(len(state.nodes)),
            key=lambda node_id: (
                state.nodes[node_id].train_errors,
                state.nodes[node_id].expanded_cost,
                node_id,
            ),
        )

        training_node = state.nodes[training_output]
        key = (training_node.train_errors, training_node.expanded_cost)
        if best_key is None or key < best_key:
            best_key = key
            best_state = state
            best_output = training_output

        cegis_node = state.nodes[cegis_output]
        counterexamples = v10.choose_counterexamples(
            cegis_node.semantic, tuple(active)
        )
        history.append(
            {
                "cegis_round": cegis_round,
                "active_points": len(active),
                "cegis_candidate": describe(cegis_output, state),
                "best_training_node_in_round": describe(training_output, state),
                "counterexamples_added": counterexamples,
                "synthesis_layers": layers,
            }
        )
        if training_node.train_errors == 0 or not counterexamples:
            break
        active.extend(counterexamples)

    if best_state is None or best_output is None:
        raise AssertionError("no best training node")

    best = describe(best_output, best_state)
    exact_training = best["training_errors"] == 0
    exact_all = (
        exact_training
        and best["frozen_holdout_errors"] == 0
        and best["external_holdout_errors"] == 0
    )

    tree_cost_cache: dict[int, int] = {}
    nodes_with_sharing = 0
    best_shared: tuple[int, int, int] | None = None
    best_shared_output: int | None = None
    maximum_sharing_savings = 0
    for node_id, node in enumerate(best_state.nodes):
        if node.operation == "base":
            continue
        tree_cost = memo_formula_tree_cost(best_state, node_id, tree_cost_cache)
        savings = tree_cost - node.expanded_cost
        maximum_sharing_savings = max(maximum_sharing_savings, savings)
        if savings > 0:
            nodes_with_sharing += 1
            shared_key = (node.train_errors, node.expanded_cost, node_id)
            if best_shared is None or shared_key < best_shared:
                best_shared = shared_key
                best_shared_output = node_id

    return {
        "profile_id": PROFILE_ID,
        "status": "selection_audited_true_DAG_screen_not_exhaustive",
        "selection_rule": {
            "cegis_candidate": "chosen by active constraints and then complete training error; used only to add counterexamples",
            "best_training_candidate": "chosen independently over every node by complete training error and charged DAG cost",
            "holdout_used_for_selection": False,
        },
        "sharing_self_test": v10.sharing_self_test(),
        "cegis_history": history,
        "best_training_candidate": best,
        "sharing_statistics_in_best_round": {
            "nodes_with_positive_DAG_savings": nodes_with_sharing,
            "maximum_formula_tree_minus_DAG_cost": maximum_sharing_savings,
            "best_shared_node": (
                describe(best_shared_output, best_state)
                if best_shared_output is not None
                else None
            ),
        },
        "decision": {
            "parity_algorithm_found": exact_all,
            "exact_training_candidate_found": exact_training,
            "negative_result_is_exhaustive": False,
            "true_multiregister_DAG_accounting_verified": True,
            "holdouts_remained_unseen_during_selection": True,
            "symbolic_proof_required_before_secp256k1_claim": True,
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
