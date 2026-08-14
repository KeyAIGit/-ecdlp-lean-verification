#!/usr/bin/env python3
"""Exact cyclic-model replay for UORC056 endpoint/factorial equivalence B14.

This is an abstract finite-field replay of the algebra shared by the concrete
B13 Miller cocycle, endpoint segment products, cyclic elliptic factorials, and
multiplicative Hilbert-90 lifts. It accepts no external point, key, wallet,
unknown scalar, or production-sized DLP target.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TOY_CASES = (
    (31, 7),
    (53, 13),
    (103, 17),
    (191, 19),
    (311, 31),
)

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def inv(value: int, modulus: int) -> int:
    return pow(value, -1, modulus)


def choose_potential(modulus: int, order: int) -> tuple[list[int], int, int]:
    """Choose one deterministic dense nonzero potential on the cyclic orbit."""
    for linear in range(1, modulus):
        for constant in range(1, modulus):
            values = [
                (index**3 + linear * index + constant) % modulus
                for index in range(order)
            ]
            if (
                all(values)
                and len(set(values)) > 2
                and sum(values) % modulus != 0
            ):
                return values, linear, constant
    raise AssertionError("failed to choose a nonzero frozen potential")


def matrix_rank_mod(matrix: list[list[int]], modulus: int) -> int:
    work = [[entry % modulus for entry in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, rows)
                if work[row][column] % modulus != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = inv(work[rank][column], modulus)
        work[rank] = [entry * scale % modulus for entry in work[rank]]
        for row in range(rows):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                (work[row][index] - factor * work[rank][index]) % modulus
                for index in range(columns)
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def minimum_two_level_cost(length: int) -> tuple[int, int]:
    best_width = 1
    best_cost = length + 1
    for width in range(1, length + 1):
        cost = width + math.ceil(length / width)
        if cost < best_cost:
            best_width = width
            best_cost = cost
    return best_width, best_cost


def build_case(modulus: int, order: int) -> dict[str, object]:
    potential, linear, constant = choose_potential(modulus, order)
    local = [
        potential[(index + 1) % order] * inv(potential[index], modulus) % modulus
        for index in range(order)
    ]
    if math.prod(local) % modulus != 1:
        raise AssertionError("cyclic coboundary norm did not telescope")

    endpoint = [
        [
            potential[target] * inv(potential[source], modulus) % modulus
            for target in range(order)
        ]
        for source in range(order)
    ]

    composition_checks = 0
    for first in range(order):
        for middle in range(order):
            for last in range(order):
                if (
                    endpoint[first][middle] * endpoint[middle][last] % modulus
                    != endpoint[first][last]
                ):
                    raise AssertionError("endpoint groupoid composition failed")
                composition_checks += 1

    segment_checks = 0
    for start in range(order):
        running = 1
        for length in range(order + 1):
            if running != endpoint[start][(start + length) % order]:
                raise AssertionError("local product did not equal endpoint ratio")
            segment_checks += 1
            if length < order:
                running = running * local[(start + length) % order] % modulus

    reconstructed = endpoint[0]
    reconstructed_endpoint = [
        [
            reconstructed[target] * inv(reconstructed[source], modulus) % modulus
            for target in range(order)
        ]
        for source in range(order)
    ]
    if reconstructed_endpoint != endpoint:
        raise AssertionError("one anchor row did not reconstruct all endpoints")

    gauge = 2
    while gauge % modulus == 0:
        gauge += 1
    gauged = [gauge * value % modulus for value in potential]
    gauged_local = [
        gauged[(index + 1) % order] * inv(gauged[index], modulus) % modulus
        for index in range(order)
    ]
    if gauged_local != local:
        raise AssertionError("constant potential gauge changed the local cocycle")

    recurrence_matrix = [[0] * order for _ in range(order)]
    for index in range(order):
        recurrence_matrix[index][index] = (-local[index]) % modulus
        recurrence_matrix[index][(index + 1) % order] = 1
    recurrence_rank = matrix_rank_mod(recurrence_matrix, modulus)
    if recurrence_rank != order - 1:
        raise AssertionError("cyclic Hilbert-90 recurrence did not have nullity one")
    if not all(
        sum(
            recurrence_matrix[row][column] * potential[column]
            for column in range(order)
        )
        % modulus
        == 0
        for row in range(order)
    ):
        raise AssertionError("potential did not span the recurrence kernel")
    if any(value == 0 for value in potential):
        raise AssertionError("frozen recurrence kernel vector was not dense")

    trace = sum(potential) % modulus
    if trace == 0:
        raise AssertionError("frozen Hilbert-90 trace vanished")
    hilbert_checks = 0
    for start in range(order):
        cumulative = 1
        hilbert_sum = 0
        for offset in range(order):
            hilbert_sum = (hilbert_sum + cumulative) % modulus
            cumulative = cumulative * local[(start + offset) % order] % modulus
        if cumulative != 1:
            raise AssertionError("Hilbert-90 cumulative norm was not one")
        if hilbert_sum != trace * inv(potential[start], modulus) % modulus:
            raise AssertionError("standard Hilbert-90 sum did not recover potential")
        hilbert_checks += 1

    midpoint = (order - 1) // 2
    block_width, block_cost = minimum_two_level_cost(midpoint)
    if block_cost * block_cost < 4 * midpoint:
        raise AssertionError("two-level product width violated AM-GM boundary")

    return {
        "field_prime": modulus,
        "orbit_order": order,
        "potential_polynomial": {
            "linear_coefficient": linear,
            "constant": constant,
        },
        "endpoint_composition_checks": composition_checks,
        "segment_product_checks": segment_checks,
        "hilbert90_checks": hilbert_checks,
        "cyclic_norm": math.prod(local) % modulus,
        "recurrence_rank": recurrence_rank,
        "recurrence_nullity": order - recurrence_rank,
        "kernel_vector_support": sum(value != 0 for value in potential),
        "anchor_row_reconstructs_all_endpoints": True,
        "constant_gauge_leaves_cocycle_unchanged": True,
        "midpoint_length": midpoint,
        "best_two_level_block_width": block_width,
        "best_two_level_charged_cost": block_cost,
        "four_length_le_cost_square": 4 * midpoint <= block_cost * block_cost,
    }


def secp_certificate() -> dict[str, object]:
    midpoint = (SECP_N - 1) // 2
    width, cost = minimum_two_level_cost(1 << 20)
    lower = math.isqrt(4 * midpoint)
    if lower * lower < 4 * midpoint:
        lower += 1
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "midpoint_length": midpoint,
        "explicit_hilbert90_state": SECP_N,
        "explicit_endpoint_orbit_row": SECP_N,
        "two_level_cost_square_lower_bound": 4 * midpoint,
        "two_level_cost_lower_bound_ceiling_sqrt": lower,
        "two_level_cost_lower_bound_bit_length": lower.bit_length(),
        "diagnostic_small_length": 1 << 20,
        "diagnostic_best_block_width": width,
        "diagnostic_best_block_cost": cost,
        "endpoint_evaluator_and_global_factor_are_equivalent": True,
        "standard_explicit_trace_or_circulant_state_is_linear": True,
        "standard_two_level_product_is_strict_subroot": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-CYCLIC-FACTORIAL-STANDARD-BOUNDARY-B15",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [build_case(*case) for case in TOY_CASES]
    aggregate = {
        "cases": len(cases),
        "endpoint_composition_checks": sum(
            case["endpoint_composition_checks"] for case in cases
        ),
        "segment_product_checks": sum(
            case["segment_product_checks"] for case in cases
        ),
        "hilbert90_checks": sum(case["hilbert90_checks"] for case in cases),
        "all_anchor_rows_reconstruct_endpoints": all(
            case["anchor_row_reconstructs_all_endpoints"] for case in cases
        ),
        "all_recurrence_nullities_one": all(
            case["recurrence_nullity"] == 1 for case in cases
        ),
        "all_kernel_vectors_dense": all(
            case["kernel_vector_support"] == case["orbit_order"] for case in cases
        ),
        "all_two_level_bounds_hold": all(
            case["four_length_le_cost_square"] for case in cases
        ),
    }
    payload = {
        "package": "UORC056-ENDPOINT-FACTORIAL-EQUIVALENCE-B14",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "An exact endpoint segment evaluator and a global cyclic-factorial "
            "potential are the same object up to one anchor scalar. Standard "
            "explicit Hilbert-90/circulant representations have n-state vectors, "
            "while standard two-level block products meet the square-root frontier. "
            "No strict sub-square-root endpoint evaluator is obtained."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
