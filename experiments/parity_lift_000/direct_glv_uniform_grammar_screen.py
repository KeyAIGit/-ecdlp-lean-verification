#!/usr/bin/env python3
"""Exact toy-only screen for DIRECT-GLV-UNIFORM-GRAMMAR-012.

The same symbolic expression is evaluated on every frozen field. Coefficients
come only from a small public constant grammar built from B=7, beta, lambda,
n, and fixed small constants. No external point, key, wallet, curve, or
production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from direct_glv_carry_descent_screen import (
    FROZEN_CASES,
    quadratic_character,
    quotient_data,
)

BINARY_MUL_COST_LIMIT = 7
TINY_INDICES = (0, 1, 2)
TRAIN_INDICES = (6, 10, 11, 8, 3, 9, 12, 4)
VALIDATION_INDICES = (5, 7)
TEST_INDICES = (13, 14)
NONTRIVIAL_INDICES = (*TRAIN_INDICES, *VALIDATION_INDICES, *TEST_INDICES)
ATOM_NAMES = (
    "zero", "one", "neg_one", "B", "neg_B", "beta", "beta_sq",
    "n", "neg_n", "lambda", "neg_lambda", "lambda_sq",
    "neg_lambda_sq",
)


@dataclass(frozen=True)
class FrozenCase:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    z: tuple[int, ...]
    target: tuple[int, ...]


@dataclass(frozen=True)
class ConstantProgram:
    expr: str
    values: tuple[int, ...]
    cost: int


def build_cases() -> list[FrozenCase]:
    result: list[FrozenCase] = []
    for p, order, generator in FROZEN_CASES:
        data = quotient_data(p, order, generator)
        result.append(FrozenCase(
            p=p,
            order=order,
            generator=generator,
            beta=data["beta"],
            lam=data["lam"],
            z=tuple(data["z"]),
            target=tuple(data["target"]),
        ))
    return result


CASES = build_cases()


def atom_values(name: str) -> tuple[int, ...]:
    values: list[int] = []
    for case in CASES:
        raw = {
            "zero": 0,
            "one": 1,
            "neg_one": -1,
            "B": 7,
            "neg_B": -7,
            "beta": case.beta,
            "beta_sq": case.beta * case.beta,
            "n": case.order,
            "neg_n": -case.order,
            "lambda": case.lam,
            "neg_lambda": -case.lam,
            "lambda_sq": case.lam * case.lam,
            "neg_lambda_sq": -(case.lam * case.lam),
        }[name]
        values.append(raw % case.p)
    return tuple(values)


def generate_constant_programs() -> list[ConstantProgram]:
    programs: dict[tuple[int, ...], ConstantProgram] = {}
    for name in ATOM_NAMES:
        program = ConstantProgram(name, atom_values(name), 0)
        programs.setdefault(program.values, program)

    def add(expr: str, values: list[int], cost: int) -> None:
        signature = tuple(values)
        candidate = ConstantProgram(expr, signature, cost)
        current = programs.get(signature)
        candidate_key = (candidate.cost, len(candidate.expr), candidate.expr)
        if current is None:
            programs[signature] = candidate
            return
        current_key = (current.cost, len(current.expr), current.expr)
        if candidate_key < current_key:
            programs[signature] = candidate

    for total_cost in (1, 2):
        snapshot = list(programs.values())
        for left in snapshot:
            if left.cost + 1 != total_cost or not all(left.values):
                continue
            add(
                f"inv({left.expr})",
                [pow(value, -1, case.p) for value, case in zip(left.values, CASES)],
                total_cost,
            )

        snapshot = list(programs.values())
        for left in snapshot:
            for right in snapshot:
                if left.cost + right.cost + 1 != total_cost:
                    continue
                if (left.cost, left.expr) <= (right.cost, right.expr):
                    add(
                        f"({left.expr}+{right.expr})",
                        [(a + b) % case.p for a, b, case in zip(
                            left.values, right.values, CASES
                        )],
                        total_cost,
                    )
                    add(
                        f"({left.expr}*{right.expr})",
                        [(a * b) % case.p for a, b, case in zip(
                            left.values, right.values, CASES
                        )],
                        total_cost,
                    )
                add(
                    f"({left.expr}-{right.expr})",
                    [(a - b) % case.p for a, b, case in zip(
                        left.values, right.values, CASES
                    )],
                    total_cost,
                )

    return sorted(programs.values(), key=lambda program: (
        program.cost, program.expr
    ))


CONSTANT_PROGRAMS = generate_constant_programs()
COEFFICIENT_PROGRAMS = [
    program for program in CONSTANT_PROGRAMS if program.cost <= 1
]
COEFFICIENT_INDEX = {
    program.values: index for index, program in enumerate(COEFFICIENT_PROGRAMS)
}


def build_coefficient_pairs() -> list[tuple[ConstantProgram, ConstantProgram]]:
    pairs: list[tuple[ConstantProgram, ConstantProgram]] = []
    seen: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    for left in COEFFICIENT_PROGRAMS:
        for right in COEFFICIENT_PROGRAMS:
            if left.cost + right.cost > 1:
                continue
            signature = (left.values, right.values)
            if signature in seen:
                continue
            seen.add(signature)
            pairs.append((left, right))
    return pairs


COEFFICIENT_PAIRS = build_coefficient_pairs()
PAIR_LEFT_INDEX = np.array([
    COEFFICIENT_INDEX[left.values] for left, _ in COEFFICIENT_PAIRS
], dtype=np.int32)
PAIR_RIGHT_INDEX = np.array([
    COEFFICIENT_INDEX[right.values] for _, right in COEFFICIENT_PAIRS
], dtype=np.int32)


def binary_mul_cost(exponent: int) -> int:
    if exponent < 1:
        raise ValueError("positive exponent required")
    return exponent.bit_length() - 1 + exponent.bit_count() - 1


EXPONENTS = tuple(
    exponent
    for exponent in range(1, 2**BINARY_MUL_COST_LIMIT + 1)
    if binary_mul_cost(exponent) <= BINARY_MUL_COST_LIMIT
)
NONLINEAR_EXPONENTS = tuple(exponent for exponent in EXPONENTS if exponent >= 2)


def subset_offsets(indices: tuple[int, ...]) -> tuple[dict[int, int], int]:
    offsets: dict[int, int] = {}
    total = 0
    for index in indices:
        offsets[index] = total
        total += len(CASES[index].z)
    return offsets, total


SOURCE_OFFSETS, ALL_NONTRIVIAL_BITS = subset_offsets(NONTRIVIAL_INDICES)


def target_mask(indices: tuple[int, ...]) -> tuple[int, int]:
    offsets, total = subset_offsets(indices)
    result = 0
    for index in indices:
        for position, sign in enumerate(CASES[index].target):
            if sign < 0:
                result |= 1 << (offsets[index] + position)
    return result, total


def project_mask(mask: int, indices: tuple[int, ...]) -> tuple[int, int]:
    result = 0
    position = 0
    for index in indices:
        width = len(CASES[index].z)
        source = SOURCE_OFFSETS[index]
        local = (mask >> source) & ((1 << width) - 1)
        result |= local << position
        position += width
    return result, position


def constant_sign_mask(
    program: ConstantProgram,
    indices: tuple[int, ...],
) -> int | None:
    offsets, _ = subset_offsets(indices)
    result = 0
    for index in indices:
        sign = quadratic_character(program.values[index], CASES[index].p)
        if sign == 0:
            return None
        if sign < 0:
            result |= ((1 << len(CASES[index].z)) - 1) << offsets[index]
    return result


def leading_pattern_map(indices: tuple[int, ...]) -> dict[int, ConstantProgram]:
    result: dict[int, ConstantProgram] = {}
    for program in CONSTANT_PROGRAMS:
        mask = constant_sign_mask(program, indices)
        if mask is not None:
            result.setdefault(mask, program)
    return result


def legendre_table(p: int) -> np.ndarray:
    return np.array([
        quadratic_character(value, p) for value in range(p)
    ], dtype=np.int8)


LEGENDRE_TABLES = {
    index: legendre_table(CASES[index].p) for index in NONTRIVIAL_INDICES
}
COEFFICIENT_VALUES = {
    index: np.array([
        program.values[index] for program in COEFFICIENT_PROGRAMS
    ], dtype=np.int64)
    for index in NONTRIVIAL_INDICES
}
PAIR_LEFT_VALUES = {
    index: COEFFICIENT_VALUES[index][PAIR_LEFT_INDEX, None]
    for index in NONTRIVIAL_INDICES
}
PAIR_RIGHT_VALUES = {
    index: COEFFICIENT_VALUES[index][PAIR_RIGHT_INDEX, None]
    for index in NONTRIVIAL_INDICES
}


def modular_power_matrix(base: np.ndarray, exponent: int, p: int) -> np.ndarray:
    result = np.ones_like(base, dtype=np.int64)
    power = base.copy()
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = result * power % p
        remaining //= 2
        if remaining:
            power = power * power % p
    return result


def power_affine_patterns(
    indices: tuple[int, ...],
) -> list[tuple[tuple[int, ConstantProgram], int]]:
    offsets, _ = subset_offsets(indices)
    labels = [
        (exponent, program)
        for exponent in EXPONENTS
        for program in COEFFICIENT_PROGRAMS
    ]
    masks = [0] * len(labels)
    valid = np.ones(len(labels), dtype=bool)

    for index in indices:
        case = CASES[index]
        z = np.array(case.z, dtype=np.int64)
        table = legendre_table(case.p)
        constants = np.array([
            program.values[index] for program in COEFFICIENT_PROGRAMS
        ], dtype=np.int64)[:, None]
        width = len(z)
        for exponent_position, exponent in enumerate(EXPONENTS):
            base = np.array([
                pow(int(value), exponent, case.p) for value in z
            ], dtype=np.int64)[None, :]
            signs = table[(base + constants) % case.p]
            row_valid = np.all(signs != 0, axis=1)
            packed = np.packbits(signs < 0, axis=1, bitorder="little")
            start = exponent_position * len(COEFFICIENT_PROGRAMS)
            previous = valid[start : start + len(COEFFICIENT_PROGRAMS)]
            for row in np.nonzero(row_valid & previous)[0].tolist():
                candidate = start + row
                local = int.from_bytes(
                    packed[row].tobytes(), "little"
                ) & ((1 << width) - 1)
                masks[candidate] |= local << offsets[index]
            invalid = np.nonzero(~row_valid)[0]
            valid[start + invalid] = False

    return [
        (labels[index], masks[index])
        for index in np.nonzero(valid)[0].tolist()
    ]


def sparse_patterns_for_exponent(
    exponent: int,
) -> list[tuple[tuple[ConstantProgram, ConstantProgram], int]]:
    offsets, _ = subset_offsets(NONTRIVIAL_INDICES)
    masks = [0] * len(COEFFICIENT_PAIRS)
    valid = np.ones(len(COEFFICIENT_PAIRS), dtype=bool)

    for index in NONTRIVIAL_INDICES:
        case = CASES[index]
        z = np.array(case.z, dtype=np.int64)
        base = np.array([
            pow(int(value), exponent, case.p) for value in z
        ], dtype=np.int64)[None, :]
        values = (
            base
            + PAIR_LEFT_VALUES[index] * z[None, :]
            + PAIR_RIGHT_VALUES[index]
        ) % case.p
        signs = LEGENDRE_TABLES[index][values]
        row_valid = np.all(signs != 0, axis=1)
        packed = np.packbits(signs < 0, axis=1, bitorder="little")
        width = len(z)
        for row in np.nonzero(row_valid & valid)[0].tolist():
            local = int.from_bytes(
                packed[row].tobytes(), "little"
            ) & ((1 << width) - 1)
            masks[row] |= local << offsets[index]
        valid &= row_valid

    return [
        (COEFFICIENT_PAIRS[index], masks[index])
        for index in np.nonzero(valid)[0].tolist()
    ]


def shifted_patterns_for_exponent(
    exponent: int,
) -> list[tuple[tuple[ConstantProgram, ConstantProgram], int]]:
    offsets, _ = subset_offsets(NONTRIVIAL_INDICES)
    masks = [0] * len(COEFFICIENT_PAIRS)
    valid = np.ones(len(COEFFICIENT_PAIRS), dtype=bool)

    for index in NONTRIVIAL_INDICES:
        case = CASES[index]
        z = np.array(case.z, dtype=np.int64)
        bases = (
            COEFFICIENT_VALUES[index][:, None] + z[None, :]
        ) % case.p
        powers = modular_power_matrix(bases, exponent, case.p)
        values = (
            powers[PAIR_LEFT_INDEX]
            + COEFFICIENT_VALUES[index][PAIR_RIGHT_INDEX, None]
        ) % case.p
        signs = LEGENDRE_TABLES[index][values]
        row_valid = np.all(signs != 0, axis=1)
        packed = np.packbits(signs < 0, axis=1, bitorder="little")
        width = len(z)
        for row in np.nonzero(row_valid & valid)[0].tolist():
            local = int.from_bytes(
                packed[row].tobytes(), "little"
            ) & ((1 << width) - 1)
            masks[row] |= local << offsets[index]
        valid &= row_valid

    return [
        (COEFFICIENT_PAIRS[index], masks[index])
        for index in np.nonzero(valid)[0].tolist()
    ]


def label_key(label: tuple) -> tuple:
    if len(label) == 2:
        exponent, constant = label
        return exponent, constant.expr
    exponent, left, right = label
    return exponent, left.expr, right.expr


def exact_power_up_to_two(
    target: int,
    items: list[tuple[tuple[int, ConstantProgram], int]],
    leading: dict[int, ConstantProgram],
) -> dict | None:
    pattern_to_label: dict[int, tuple[int, ConstantProgram]] = {}
    for label, mask in items:
        current = pattern_to_label.get(mask)
        if current is None or label_key(label) < label_key(current):
            pattern_to_label[mask] = label

    for leading_mask, leading_program in sorted(
        leading.items(), key=lambda item: item[1].expr
    ):
        wanted = target ^ leading_mask
        if wanted == 0:
            return {"leading_constant": leading_program.expr, "factors": []}
        if wanted in pattern_to_label:
            exponent, constant = pattern_to_label[wanted]
            return {
                "leading_constant": leading_program.expr,
                "factors": [{
                    "exponent": exponent,
                    "constant": constant.expr,
                }],
            }
        for mask, first in pattern_to_label.items():
            second_mask = wanted ^ mask
            if second_mask == mask:
                continue
            second = pattern_to_label.get(second_mask)
            if second is None:
                continue
            factors = sorted((first, second), key=label_key)
            return {
                "leading_constant": leading_program.expr,
                "factors": [{
                    "exponent": exponent,
                    "constant": constant.expr,
                } for exponent, constant in factors],
            }
    return None


def exact_single(
    target: int,
    items: list[tuple[tuple, int]],
    leading: dict[int, ConstantProgram],
) -> dict | None:
    best: tuple[str, tuple, tuple] | None = None
    for label, mask in items:
        leading_program = leading.get(target ^ mask)
        if leading_program is None:
            continue
        candidate = (leading_program.expr, label_key(label), label)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        return None
    leading_expr, _, label = best
    exponent, left, right = label
    return {
        "leading_constant": leading_expr,
        "exponent": exponent,
        "a": left.expr,
        "b": right.expr,
    }


def expression_info(family: str, label: tuple) -> tuple[dict, str]:
    if family == "power_affine":
        exponent, constant = label
        return (
            {"exponent": exponent, "constant": constant.expr},
            f"z^{exponent}+({constant.expr})",
        )

    exponent, left, right = label
    if family == "sparse_trinomial":
        return (
            {"exponent": exponent, "a": left.expr, "b": right.expr},
            f"z^{exponent}+({left.expr})*z+({right.expr})",
        )
    if family == "shifted_power":
        return (
            {"exponent": exponent, "a": left.expr, "b": right.expr},
            f"(z+({left.expr}))^{exponent}+({right.expr})",
        )
    raise ValueError(f"unknown family: {family}")


def evaluate_prediction(prediction_all: int, indices: tuple[int, ...]) -> dict:
    prediction, width = project_mask(prediction_all, indices)
    target, _ = target_mask(indices)
    correct = width - (prediction ^ target).bit_count()
    return {"correct": correct, "total": width, "accuracy": correct / width}


def family_diagnostics(
    items: list[tuple[tuple, int]],
    family: str,
    leading_train: dict[int, ConstantProgram],
) -> tuple[dict, dict]:
    target_train, train_width = target_mask(TRAIN_INDICES)
    leading_items = sorted(
        leading_train.items(), key=lambda item: item[1].expr
    )
    records: list[tuple] = []

    for label, mask_all in items:
        mask_train, _ = project_mask(mask_all, TRAIN_INDICES)
        best_correct = -1
        best_leading: ConstantProgram | None = None
        for leading_mask, leading_program in leading_items:
            correct = train_width - (
                mask_train ^ leading_mask ^ target_train
            ).bit_count()
            if (
                correct > best_correct
                or (
                    correct == best_correct
                    and best_leading is not None
                    and leading_program.expr < best_leading.expr
                )
                or best_leading is None
            ):
                best_correct = correct
                best_leading = leading_program
        assert best_leading is not None
        _, rendered = expression_info(family, label)
        records.append((
            best_correct,
            rendered,
            best_leading.expr,
            label,
            mask_all,
            best_leading,
        ))

    records.sort(key=lambda record: (-record[0], record[1], record[2]))
    top = records[:20]

    def payload(record: tuple) -> dict:
        _, rendered, leading_expr, label, mask_all, leading_program = record
        leading_all = constant_sign_mask(
            leading_program, NONTRIVIAL_INDICES
        )
        assert leading_all is not None
        prediction = mask_all ^ leading_all
        info, _ = expression_info(family, label)
        return {
            "leading_constant": leading_expr,
            "expression": info,
            "rendered": f"({leading_expr})*({rendered})",
            "train": evaluate_prediction(prediction, TRAIN_INDICES),
            "validation": evaluate_prediction(prediction, VALIDATION_INDICES),
            "test": evaluate_prediction(prediction, TEST_INDICES),
            "all_nontrivial": evaluate_prediction(
                prediction, NONTRIVIAL_INDICES
            ),
        }

    top_payloads = [payload(record) for record in top]
    means = {
        split: statistics.mean(item[split]["accuracy"] for item in top_payloads)
        for split in ("train", "validation", "test", "all_nontrivial")
    }
    return top_payloads[0], means


def random_union_gate(
    width: int,
    nominal_classes: int,
    alpha: float = 0.05,
) -> dict:
    denominator = 2**width
    tail = 0.0
    tails = [0.0] * (width + 1)
    for correct in range(width, -1, -1):
        tail += math.comb(width, correct) / denominator
        tails[correct] = tail
    for correct in range((width + 1) // 2, width + 1):
        union_bound = nominal_classes * tails[correct]
        if union_bound <= alpha:
            return {
                "correct": correct,
                "total": width,
                "accuracy": correct / width,
                "union_bound": union_bound,
            }
    return {
        "correct": width,
        "total": width,
        "accuracy": 1.0,
        "union_bound": nominal_classes / denominator,
    }


def case_metadata() -> list[dict]:
    split: dict[int, str] = {
        index: "tiny_diagnostic" for index in TINY_INDICES
    }
    split.update({index: "train" for index in TRAIN_INDICES})
    split.update({index: "validation" for index in VALIDATION_INDICES})
    split.update({index: "test" for index in TEST_INDICES})
    return [{
        "p": case.p,
        "order": case.order,
        "generator": list(case.generator),
        "beta": case.beta,
        "lambda": case.lam,
        "quotient_orbits": len(case.z),
        "target_positive": sum(sign == 1 for sign in case.target),
        "target_negative": sum(sign == -1 for sign in case.target),
        "split": split[index],
    } for index, case in enumerate(CASES)]


def build_payload() -> dict:
    target_all, all_width = target_mask(NONTRIVIAL_INDICES)
    target_train, train_width = target_mask(TRAIN_INDICES)
    target_tiny, tiny_width = target_mask(TINY_INDICES)

    leading_all = leading_pattern_map(NONTRIVIAL_INDICES)
    leading_train: dict[int, ConstantProgram] = {}
    for mask, program in leading_all.items():
        projected, _ = project_mask(mask, TRAIN_INDICES)
        leading_train.setdefault(projected, program)
    leading_tiny = leading_pattern_map(TINY_INDICES)

    power_all = power_affine_patterns(NONTRIVIAL_INDICES)
    power_train = [
        (label, project_mask(mask, TRAIN_INDICES)[0])
        for label, mask in power_all
    ]
    power_tiny = power_affine_patterns(TINY_INDICES)

    sparse_all: list[tuple[tuple, int]] = []
    shifted_all: list[tuple[tuple, int]] = []
    for exponent in NONLINEAR_EXPONENTS:
        sparse_all.extend(
            ((exponent, left, right), mask)
            for (left, right), mask in sparse_patterns_for_exponent(exponent)
        )
        shifted_all.extend(
            ((exponent, left, right), mask)
            for (left, right), mask in shifted_patterns_for_exponent(exponent)
        )

    sparse_train = [
        (label, project_mask(mask, TRAIN_INDICES)[0])
        for label, mask in sparse_all
    ]
    shifted_train = [
        (label, project_mask(mask, TRAIN_INDICES)[0])
        for label, mask in shifted_all
    ]

    power_patterns_all = len({mask for _, mask in power_all})
    power_patterns_train = len({mask for _, mask in power_train})
    sparse_patterns_all = len({mask for _, mask in sparse_all})
    sparse_patterns_train = len({mask for _, mask in sparse_train})
    shifted_patterns_all = len({mask for _, mask in shifted_all})
    shifted_patterns_train = len({mask for _, mask in shifted_train})

    power_train_classes = len(leading_train) * (
        1
        + power_patterns_train
        + power_patterns_train * (power_patterns_train - 1) // 2
    )
    power_all_classes = len(leading_all) * (
        1
        + power_patterns_all
        + power_patterns_all * (power_patterns_all - 1) // 2
    )
    sparse_train_classes = len(leading_train) * sparse_patterns_train
    sparse_all_classes = len(leading_all) * sparse_patterns_all
    shifted_train_classes = len(leading_train) * shifted_patterns_train
    shifted_all_classes = len(leading_all) * shifted_patterns_all

    exact_power_train = exact_power_up_to_two(
        target_train, power_train, leading_train
    )
    exact_power_all = exact_power_up_to_two(target_all, power_all, leading_all)
    exact_power_tiny = exact_power_up_to_two(
        target_tiny, power_tiny, leading_tiny
    )
    exact_sparse_train = exact_single(
        target_train, sparse_train, leading_train
    )
    exact_sparse_all = exact_single(target_all, sparse_all, leading_all)
    exact_shifted_train = exact_single(
        target_train, shifted_train, leading_train
    )
    exact_shifted_all = exact_single(target_all, shifted_all, leading_all)

    best_power, top20_power = family_diagnostics(
        power_all, "power_affine", leading_train
    )
    best_sparse, top20_sparse = family_diagnostics(
        sparse_all, "sparse_trinomial", leading_train
    )
    best_shifted, top20_shifted = family_diagnostics(
        shifted_all, "shifted_power", leading_train
    )

    nonzero_leading_programs = sum(
        constant_sign_mask(program, NONTRIVIAL_INDICES) is not None
        for program in CONSTANT_PROGRAMS
    )

    return {
        "package": "DIRECT-GLV-UNIFORM-GRAMMAR-012",
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external or production target"
        ),
        "target": "chi(R(z(Q))) = h(Q), z=x^3, h=g*chi(y)",
        "uniformity_rule": (
            "one symbolic expression is evaluated unchanged on every field; "
            "instance-specific fitted constants are forbidden"
        ),
        "constant_grammar": {
            "atoms": list(ATOM_NAMES),
            "operations": [
                "addition", "subtraction", "multiplication",
                "inversion when defined",
            ],
            "semantic_constant_programs_cost_at_most_two": len(
                CONSTANT_PROGRAMS
            ),
            "coefficient_programs_cost_at_most_one": len(
                COEFFICIENT_PROGRAMS
            ),
            "ordered_coefficient_pairs_total_cost_at_most_one": len(
                COEFFICIENT_PAIRS
            ),
            "nonzero_leading_programs_on_all_nontrivial_cases": (
                nonzero_leading_programs
            ),
            "distinct_leading_sign_patterns_on_all_nontrivial_cases": len(
                leading_all
            ),
            "distinct_leading_sign_patterns_on_train": len(leading_train),
            "interpretation": (
                "B=7; beta is the public field cube root; lambda and n are "
                "their public integer representatives reduced modulo the "
                "current field"
            ),
        },
        "exponent_grammar": {
            "cost": (
                "ordinary left-to-right binary exponentiation multiplications"
            ),
            "cost_limit": BINARY_MUL_COST_LIMIT,
            "exponents": list(EXPONENTS),
            "count": len(EXPONENTS),
            "nonlinear_count": len(NONLINEAR_EXPONENTS),
            "maximum_exponent": max(EXPONENTS),
        },
        "split": {
            "tiny_diagnostic_orders": [
                CASES[index].order for index in TINY_INDICES
            ],
            "train_orders": [
                CASES[index].order for index in TRAIN_INDICES
            ],
            "validation_orders": [
                CASES[index].order for index in VALIDATION_INDICES
            ],
            "test_orders": [
                CASES[index].order for index in TEST_INDICES
            ],
            "train_bits": train_width,
            "validation_bits": sum(
                len(CASES[index].z) for index in VALIDATION_INDICES
            ),
            "test_bits": sum(
                len(CASES[index].z) for index in TEST_INDICES
            ),
            "all_nontrivial_bits": all_width,
            "selection_rule": (
                "maximize training accuracy only; validation and test are "
                "never used to choose the expression"
            ),
        },
        "cases": case_metadata(),
        "families": {
            "power_affine_up_to_two": {
                "form": "u*product(z^e+c), zero to two factors",
                "valid_primitive_expressions_on_all_nontrivial_cases": len(
                    power_all
                ),
                "distinct_primitive_patterns_all_nontrivial": (
                    power_patterns_all
                ),
                "distinct_primitive_patterns_train": power_patterns_train,
                "nominal_train_classes": power_train_classes,
                "nominal_all_nontrivial_classes": power_all_classes,
                "exact_train_solution": exact_power_train,
                "exact_all_nontrivial_solution": exact_power_all,
                "joint_tiny_diagnostic_solution": exact_power_tiny,
                "log2_random_exact_union_bound_train": (
                    math.log2(power_train_classes) - train_width
                ),
                "log2_random_exact_union_bound_all_nontrivial": (
                    math.log2(power_all_classes) - all_width
                ),
                "single_factor_diagnostic": {
                    "nominal_train_classes": (
                        power_patterns_train * len(leading_train)
                    ),
                    "five_percent_random_union_gate": random_union_gate(
                        train_width,
                        power_patterns_train * len(leading_train),
                    ),
                    "best_train_selected": best_power,
                    "top20_mean_accuracy": top20_power,
                },
            },
            "sparse_trinomial": {
                "form": "u*(z^e+a*z+b)",
                "coefficient_pair_cost_rule": "cost(a)+cost(b)<=1",
                "valid_expressions_on_all_nontrivial_cases": len(sparse_all),
                "distinct_patterns_all_nontrivial": sparse_patterns_all,
                "distinct_patterns_train": sparse_patterns_train,
                "nominal_train_classes": sparse_train_classes,
                "nominal_all_nontrivial_classes": sparse_all_classes,
                "exact_train_solution": exact_sparse_train,
                "exact_all_nontrivial_solution": exact_sparse_all,
                "log2_random_exact_union_bound_train": (
                    math.log2(sparse_train_classes) - train_width
                ),
                "log2_random_exact_union_bound_all_nontrivial": (
                    math.log2(sparse_all_classes) - all_width
                ),
                "five_percent_random_union_gate": random_union_gate(
                    train_width, sparse_train_classes
                ),
                "best_train_selected": best_sparse,
                "top20_mean_accuracy": top20_sparse,
            },
            "shifted_power": {
                "form": "u*((z+a)^e+b)",
                "coefficient_pair_cost_rule": "cost(a)+cost(b)<=1",
                "valid_expressions_on_all_nontrivial_cases": len(shifted_all),
                "distinct_patterns_all_nontrivial": shifted_patterns_all,
                "distinct_patterns_train": shifted_patterns_train,
                "nominal_train_classes": shifted_train_classes,
                "nominal_all_nontrivial_classes": shifted_all_classes,
                "exact_train_solution": exact_shifted_train,
                "exact_all_nontrivial_solution": exact_shifted_all,
                "log2_random_exact_union_bound_train": (
                    math.log2(shifted_train_classes) - train_width
                ),
                "log2_random_exact_union_bound_all_nontrivial": (
                    math.log2(shifted_all_classes) - all_width
                ),
                "five_percent_random_union_gate": random_union_gate(
                    train_width, shifted_train_classes
                ),
                "best_train_selected": best_shifted,
                "top20_mean_accuracy": top20_shifted,
            },
        },
        "aggregate": {
            "uniform_families": 3,
            "exact_train_decoders": sum(
                solution is not None
                for solution in (
                    exact_power_train,
                    exact_sparse_train,
                    exact_shifted_train,
                )
            ),
            "exact_all_nontrivial_decoders": sum(
                solution is not None
                for solution in (
                    exact_power_all,
                    exact_sparse_all,
                    exact_shifted_all,
                )
            ),
            "best_observed_train_accuracy": max(
                best_power["train"]["accuracy"],
                best_sparse["train"]["accuracy"],
                best_shifted["train"]["accuracy"],
            ),
            "best_selected_test_accuracy": max(
                best_power["test"]["accuracy"],
                best_sparse["test"]["accuracy"],
                best_shifted["test"]["accuracy"],
            ),
            "maximum_top20_mean_test_accuracy": max(
                top20_power["test"],
                top20_sparse["test"],
                top20_shifted["test"],
            ),
            "all_observed_best_train_scores_below_familywise_random_union_gate": (
                best_power["train"]["correct"]
                < random_union_gate(
                    train_width,
                    power_patterns_train * len(leading_train),
                )["correct"]
                and best_sparse["train"]["correct"]
                < random_union_gate(
                    train_width, sparse_train_classes
                )["correct"]
                and best_shifted["train"]["correct"]
                < random_union_gate(
                    train_width, shifted_train_classes
                )["correct"]
            ),
        },
        "conclusion": (
            "No expression in any declared uniform grammar fits even the "
            "frozen training curves exactly, hence none transfers exactly to "
            "validation or the two largest held-out curves. The best "
            "training-selected formulas reach about 59.8% on training but "
            "return to about chance on held-out data; the top-20 mean test "
            "accuracies are approximately 50%. The same grammar can fit the "
            "combined nineteen-bit tiny diagnostic, demonstrating why fixed "
            "cross-curve transfer is the relevant gate rather than finite "
            "interpolation."
        ),
        "claim_boundary": [
            "The result is exact only for the declared constant and expression grammars.",
            "Semantic deduplication is performed on the fifteen frozen fields; it is an implementation reduction, not a symbolic identity theorem.",
            "The random union gates are capacity diagnostics for independent random signs, not p-values for the structured carry target.",
            "No general arithmetic circuit, three-factor power-affine product, canonical p-adic output, or asymptotic lower bound is covered.",
            "The lambda atom is the public integer representative reduced into each base field; no claim is made that it is a canonical geometric field invariant.",
            "No secp256k1 unknown point, private key, wallet, or external target is accepted or evaluated."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "direct_glv_uniform_grammar_results.json"
        ),
    )
    args = parser.parse_args()
    rendered = json.dumps(build_payload(), indent=2, sort_keys=True)
    args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
