#!/usr/bin/env python3
"""Exact C36 replay for the multi-argument shifted-Miller defect decoder.

The script uses only the five frozen public toy curves inherited from C35. It
never accepts an external point, key, wallet, or production target.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from uorc056_shifted_miller_core import (
    Ext,
    Fp2Field,
    INSTANCES,
    Instance,
    build_miller_section,
    smallest_nonsquare,
    twist_points,
    ExtCurve,
)
from uorc056_shifted_miller_eval import shifted_state


def sigma(value: int, order: int) -> int:
    return 1 if (value % order) % 2 == 0 else -1


def carry(left: int, right: int, order: int) -> int:
    a, b = left % order, right % order
    return 1 if a + b < order else -1


def total_degree_exponents(variables: int, degree: int) -> list[tuple[int, ...]]:
    return [
        exponents
        for exponents in itertools.product(range(degree + 1), repeat=variables)
        if sum(exponents) <= degree
    ]


def evaluate_monomials(
    field: Fp2Field,
    values: tuple[Ext, ...],
    exponents: list[tuple[int, ...]],
) -> list[Ext]:
    row: list[Ext] = []
    for exponent_vector in exponents:
        value = field.one
        for coordinate, exponent in zip(values, exponent_vector):
            if exponent:
                value = field.mul(value, field.pow(coordinate, exponent))
        row.append(value)
    return row


def matrix_rank(field: Fp2Field, matrix: list[list[Ext]]) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != field.zero),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = field.inv(work[rank][column])
        work[rank] = [field.mul(value, inverse) for value in work[rank]]
        for row in range(rank + 1, rows):
            if work[row][column] == field.zero:
                continue
            factor = work[row][column]
            work[row] = [
                field.sub(left, field.mul(factor, right))
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def augmented_consistent(
    field: Fp2Field,
    matrix: list[list[Ext]],
    target: list[Ext],
) -> tuple[bool, int]:
    work = [row[:] + [target[index]] for index, row in enumerate(matrix)]
    rows = len(work)
    columns = len(matrix[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] != field.zero),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = field.inv(work[rank][column])
        work[rank] = [field.mul(value, inverse) for value in work[rank]]
        for row in range(rank + 1, rows):
            if work[row][column] == field.zero:
                continue
            factor = work[row][column]
            work[row] = [
                field.sub(left, field.mul(factor, right))
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    for row in range(rank, rows):
        if (
            all(work[row][column] == field.zero for column in range(columns))
            and work[row][columns] != field.zero
        ):
            return False, rank
    return True, rank


def collision_profile(
    values: Iterable[object],
    targets: Iterable[int],
) -> tuple[int, int]:
    seen: dict[object, int] = {}
    mixed = 0
    for value, target in zip(values, targets):
        if value in seen and seen[value] != target:
            mixed += 1
        else:
            seen.setdefault(value, target)
    return len(seen), mixed


@dataclass(frozen=True)
class FrozenEnvironment:
    instance: Instance
    field: Fp2Field
    curve: ExtCurve
    section: object
    table: tuple[object, ...]
    shifts: tuple[object, ...]


def build_environment(instance: Instance) -> FrozenEnvironment:
    field = Fp2Field(instance.curve.p, smallest_nonsquare(instance.curve.p))
    curve = ExtCurve(instance.curve, field)
    section = build_miller_section(instance)
    table = tuple(
        curve.embed(instance.curve.mul(scalar, instance.G))
        for scalar in range(instance.n)
    )
    shifts = tuple(twist_points(instance, field))
    return FrozenEnvironment(instance, field, curve, section, table, shifts)


def shifted_values(environment: FrozenEnvironment, shift: object) -> list[Ext]:
    field = environment.field
    denominator = environment.section.eval_ext(shift, field)
    values = [field.one]
    for scalar in range(1, environment.instance.n):
        point = environment.curve.add(environment.table[scalar], shift)
        numerator = environment.section.eval_ext(point, field)
        values.append(field.div(numerator, denominator))
    return values


def c34_pairs(order: int) -> tuple[tuple[int, int], ...]:
    t = (order - 1) // 2
    a = 2
    b = (t - a) % order
    return (
        (1, a),
        (a, b),
        ((-t) % order, (-b) % order),
    )


def defect(field: Fp2Field, values: list[Ext], left: int, right: int, scalar: int, order: int) -> Ext:
    return field.div(
        values[((left + right) * scalar) % order],
        field.mul(values[(left * scalar) % order], values[(right * scalar) % order]),
    )


def defect_rows(
    environment: FrozenEnvironment,
    values: list[Ext],
) -> tuple[list[tuple[Ext, Ext, Ext]], list[int], list[tuple[list[Ext], list[int]]]]:
    order = environment.instance.n
    pairs = c34_pairs(order)
    rows: list[tuple[Ext, Ext, Ext]] = []
    parity: list[int] = []
    singles: list[tuple[list[Ext], list[int]]] = [([], []), ([], []), ([], [])]
    for scalar in range(1, order):
        coordinates = tuple(
            defect(environment.field, values, left, right, scalar, order)
            for left, right in pairs
        )
        rows.append(coordinates)  # type: ignore[arg-type]
        parity.append(sigma(scalar, order))
        for index, ((left, right), coordinate) in enumerate(zip(pairs, coordinates)):
            singles[index][0].append(coordinate)
            singles[index][1].append(carry(left * scalar, right * scalar, order))
    return rows, parity, singles


def verify_defect_cocycle(environment: FrozenEnvironment, values: list[Ext]) -> int:
    field = environment.field
    order = environment.instance.n
    checks = 0
    for scalar in range(1, order):
        p, q, r = scalar, 2 * scalar, 3 * scalar
        first = field.mul(
            defect(field, values, p, q, 1, order),
            defect(field, values, p + q, r, 1, order),
        )
        second = field.mul(
            defect(field, values, q, r, 1, order),
            defect(field, values, p, q + r, 1, order),
        )
        if first != second:
            raise AssertionError("field defect cocycle failed")
        checks += 1
    return checks


def low_degree_screen(
    environment: FrozenEnvironment,
    rows: list[tuple[Ext, Ext, Ext]],
    parity: list[int],
) -> dict[str, int | bool]:
    field = environment.field
    target = [field.e(value) for value in parity]

    polynomial_exponents = total_degree_exponents(3, 3)
    polynomial_matrix = [
        evaluate_monomials(field, row, polynomial_exponents)
        for row in rows
    ]
    polynomial_consistent, polynomial_rank = augmented_consistent(
        field, polynomial_matrix, target
    )

    rational_exponents = total_degree_exponents(3, 2)
    rational_matrix: list[list[Ext]] = []
    for row, sign in zip(rows, target):
        evaluations = evaluate_monomials(field, row, rational_exponents)
        rational_matrix.append(
            evaluations
            + [field.neg(field.mul(sign, value)) for value in evaluations]
        )
    rational_rank = matrix_rank(field, rational_matrix)
    rational_columns = 2 * len(rational_exponents)

    return {
        "polynomial_total_degree": 3,
        "polynomial_columns": len(polynomial_exponents),
        "polynomial_rank": polynomial_rank,
        "polynomial_decoder_exists": polynomial_consistent,
        "rational_total_degree": 2,
        "rational_columns": rational_columns,
        "rational_rank": rational_rank,
        "nonzero_rational_relation_exists": rational_rank < rational_columns,
    }


def first_polynomial_decoder(
    environment: FrozenEnvironment,
    rows: list[tuple[Ext, Ext, Ext]],
    parity: list[int],
    coordinates: int,
) -> dict[str, int]:
    field = environment.field
    target = [field.e(value) for value in parity]
    selected = [row[:coordinates] for row in rows]
    for degree in range(0, 32):
        exponents = total_degree_exponents(coordinates, degree)
        matrix = [evaluate_monomials(field, row, exponents) for row in selected]
        consistent, rank = augmented_consistent(field, matrix, target)
        if consistent:
            return {
                "degree": degree,
                "monomials": len(exponents),
                "rank": rank,
            }
    raise AssertionError("polynomial decoder threshold not found")


def first_rational_relation(
    environment: FrozenEnvironment,
    rows: list[tuple[Ext, Ext, Ext]],
    parity: list[int],
    coordinates: int,
) -> dict[str, int]:
    field = environment.field
    selected = [row[:coordinates] for row in rows]
    target = [field.e(value) for value in parity]
    for degree in range(0, 32):
        exponents = total_degree_exponents(coordinates, degree)
        matrix: list[list[Ext]] = []
        for row, sign in zip(selected, target):
            evaluations = evaluate_monomials(field, row, exponents)
            matrix.append(
                evaluations
                + [field.neg(field.mul(sign, value)) for value in evaluations]
            )
        rank = matrix_rank(field, matrix)
        columns = 2 * len(exponents)
        if rank < columns:
            return {
                "degree": degree,
                "monomials_per_side": len(exponents),
                "columns": columns,
                "rank": rank,
                "nullity": columns - rank,
            }
    raise AssertionError("rational relation threshold not found")


def curve_replay(instance: Instance) -> dict[str, object]:
    environment = build_environment(instance)
    order = instance.n
    all_shift_joint_injective = 0
    all_shift_joint_mixed = 0
    single_pure_counts = [0, 0, 0]
    low_degree_polynomial_survivors = 0
    low_degree_rational_relations = 0
    cocycle_checks = 0
    minimum_joint_distinct = order
    maximum_joint_distinct = 0
    canonical_rows: list[tuple[Ext, Ext, Ext]] | None = None
    canonical_parity: list[int] | None = None

    for shift_index, shift in enumerate(environment.shifts):
        values = shifted_values(environment, shift)
        rows, parity, singles = defect_rows(environment, values)
        distinct, mixed = collision_profile(rows, parity)
        all_shift_joint_injective += int(distinct == order - 1)
        all_shift_joint_mixed += int(mixed != 0)
        minimum_joint_distinct = min(minimum_joint_distinct, distinct)
        maximum_joint_distinct = max(maximum_joint_distinct, distinct)
        for index, (single_values, single_targets) in enumerate(singles):
            _, single_mixed = collision_profile(single_values, single_targets)
            single_pure_counts[index] += int(single_mixed == 0)

        screen = low_degree_screen(environment, rows, parity)
        low_degree_polynomial_survivors += int(screen["polynomial_decoder_exists"])
        low_degree_rational_relations += int(screen["nonzero_rational_relation_exists"])
        cocycle_checks += verify_defect_cocycle(environment, values)

        if shift_index == 0:
            canonical_rows = rows
            canonical_parity = parity

    assert canonical_rows is not None and canonical_parity is not None
    canonical_screen = low_degree_screen(environment, canonical_rows, canonical_parity)
    polynomial_thresholds = {
        str(coordinates): first_polynomial_decoder(
            environment, canonical_rows, canonical_parity, coordinates
        )
        for coordinates in (2, 3)
    }
    rational_thresholds = {
        str(coordinates): first_rational_relation(
            environment, canonical_rows, canonical_parity, coordinates
        )
        for coordinates in (2, 3)
    }

    return {
        "instance": instance.name,
        "p": instance.curve.p,
        "n": order,
        "twist_shifts": len(environment.shifts),
        "joint_state": {
            "injective_shifts": all_shift_joint_injective,
            "mixed_parity_shifts": all_shift_joint_mixed,
            "minimum_distinct_tuples": minimum_joint_distinct,
            "maximum_distinct_tuples": maximum_joint_distinct,
            "single_defect_pure_shift_counts": single_pure_counts,
        },
        "all_shift_low_degree_screen": {
            "polynomial_degree_le_3_survivors": low_degree_polynomial_survivors,
            "rational_degree_le_2_nonzero_relations": low_degree_rational_relations,
            "polynomial_columns": canonical_screen["polynomial_columns"],
            "rational_columns": canonical_screen["rational_columns"],
            "minimum_rank_in_both_declared_matrices": min(
                int(canonical_screen["polynomial_rank"]),
                int(canonical_screen["rational_rank"]),
            ),
        },
        "canonical_shift": {
            "two_coordinate_polynomial_threshold": polynomial_thresholds["2"],
            "three_coordinate_polynomial_threshold": polynomial_thresholds["3"],
            "two_coordinate_first_rational_relation": rational_thresholds["2"],
            "three_coordinate_first_rational_relation": rational_thresholds["3"],
        },
        "defect_cocycle_checks": cocycle_checks,
        "errors": 0,
    }


def build_payload() -> dict[str, object]:
    curves = [curve_replay(instance) for instance in INSTANCES]
    aggregate = {
        "curves": len(curves),
        "twist_shifts": sum(int(row["twist_shifts"]) for row in curves),
        "shift_query_tuples": sum(
            int(row["twist_shifts"]) * (int(row["n"]) - 1)
            for row in curves
        ),
        "joint_injective_shifts": sum(
            int(row["joint_state"]["injective_shifts"]) for row in curves
        ),
        "joint_mixed_parity_shifts": sum(
            int(row["joint_state"]["mixed_parity_shifts"]) for row in curves
        ),
        "polynomial_degree_le_3_survivors": sum(
            int(row["all_shift_low_degree_screen"]["polynomial_degree_le_3_survivors"])
            for row in curves
        ),
        "rational_degree_le_2_nonzero_relations": sum(
            int(row["all_shift_low_degree_screen"]["rational_degree_le_2_nonzero_relations"])
            for row in curves
        ),
        "defect_cocycle_checks": sum(int(row["defect_cocycle_checks"]) for row in curves),
        "errors": 0,
    }
    payload: dict[str, object] = {
        "profile_id": "UORC-056-MULTI-ARGUMENT-MILLER-DECODER-C36",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "field_defect": {
            "definition": "Delta_S(P,R)=M_S(P+R)/(M_S(P)M_S(R))",
            "cocycle": "Delta(P,R)Delta(P+R,T)=Delta(R,T)Delta(P,R+T)",
            "carry_analogy": "C_G(P,R) is the same multiplicative defect construction applied to sigma_G.",
            "shift_gauge": "Every shifted field defect differs from one base Miller defect by one common scalar and an explicit n-th-power line coboundary.",
        },
        "three_defect_state": {
            "pairs": "(Q,A), (A,B), (-T,-B), with A=2Q, T=-Q/2, B=T-A",
            "state": "D_S(Q)=(Delta_S(Q,A),Delta_S(A,B),Delta_S(-T,-B))",
            "cost": "A constant number of O(log n) shifted Miller evaluations and field operations.",
        },
        "curve_results": curves,
        "aggregate": aggregate,
        "decision": {
            "compact_public_three_defect_state_found": True,
            "joint_state_injective_on_every_frozen_shift": True,
            "arbitrary_lookup_decoder_exists_on_frozen_curves": True,
            "lookup_decoder_is_cost_acceptable": False,
            "polynomial_total_degree_le_3_decoder_found": False,
            "rational_total_degree_le_2_decoder_found": False,
            "canonical_early_interpolation_structure_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_evaluator_found": False,
            "sub_sqrt_ecdlp_found": False,
            "successor": "CUBICAL-MILLER-DEFECT-ELIMINATION-C37",
        },
        "claim_boundary": {
            "proved": [
                "the abstract multiplicative defect cocycle identity",
                "the defect-gauge normal form from the C35 shifted-state gauge",
                "exact all-shift collision and bounded-degree matrix replay",
                "maximal canonical evaluation rank until dimension count forces interpolation relations",
            ],
            "finite_screen_only": [
                "injectivity of the three-defect tuple on all 520 frozen shifts",
                "absence of total-degree at most three polynomial decoders",
                "absence of total-degree at most two rational relations",
            ],
            "not_claimed": [
                "nonexistence of every nonlinear decoder",
                "a multivariate circuit lower bound",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
    }
    digest_input = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(digest_input).hexdigest()
    return payload


def validate_payload(payload: dict[str, object]) -> None:
    aggregate = payload["aggregate"]
    assert aggregate["curves"] == 5
    assert aggregate["twist_shifts"] == 520
    assert aggregate["shift_query_tuples"] == 54192
    assert aggregate["joint_injective_shifts"] == 520
    assert aggregate["joint_mixed_parity_shifts"] == 0
    assert aggregate["polynomial_degree_le_3_survivors"] == 0
    assert aggregate["rational_degree_le_2_nonzero_relations"] == 0
    assert aggregate["defect_cocycle_checks"] == 54192
    assert aggregate["errors"] == 0

    expected = {
        "E7-P43-N31": (7, 4, 5, 3),
        "E7-P67-N79": (11, 6, 8, 5),
        "E7-P79-N67": (10, 6, 7, 4),
        "E7-P127-N127": (15, 8, 10, 6),
        "E7-P163-N139": (16, 8, 11, 6),
    }
    for row in payload["curve_results"]:
        two_poly, three_poly, two_rat, three_rat = expected[row["instance"]]
        canonical = row["canonical_shift"]
        assert canonical["two_coordinate_polynomial_threshold"]["degree"] == two_poly
        assert canonical["three_coordinate_polynomial_threshold"]["degree"] == three_poly
        assert canonical["two_coordinate_first_rational_relation"]["degree"] == two_rat
        assert canonical["three_coordinate_first_rational_relation"]["degree"] == three_rat
        assert row["joint_state"]["injective_shifts"] == row["twist_shifts"]
        assert row["joint_state"]["mixed_parity_shifts"] == 0
        assert row["all_shift_low_degree_screen"]["minimum_rank_in_both_declared_matrices"] == 20
        assert row["errors"] == 0
    decision = payload["decision"]
    assert decision["compact_public_three_defect_state_found"]
    assert not decision["lookup_decoder_is_cost_acceptable"]
    assert not decision["parity_oracle_found"]
    assert not decision["sub_sqrt_ecdlp_found"]
    assert len(payload["digest"]) == 64


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if args.check:
        validate_payload(payload)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("UORC056_MULTI_ARGUMENT_MILLER_DECODER_C36_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(f"digest={payload['digest']}")


if __name__ == "__main__":
    main()
