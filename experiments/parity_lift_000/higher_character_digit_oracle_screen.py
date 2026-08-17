#!/usr/bin/env python3
"""Toy-only search for scalar radix digits from public point-function phases.

An exact oracle for k mod q, with q >= 2 fixed and gcd(q,n)=1, recovers the
canonical scalar by radix peeling:

    r = k mod q,
    Q <- [q^{-1}] (Q - [r]G),
    k <- (k-r)/q.

This package tests whether the q-th character of the raw public point function,
combined with small public orientation bits, determines k mod q.  The lookup is
calibrated only on known public multiples G,2G,... and then checked on the full
frozen toy orbit.  It tests q=3 on the established frozen family and q=7 on the
deterministic p=43 mod 84 family.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)
from seventh_character_point_function_screen import (
    canonical_mu7_root,
    generate_cases as generate_seventh_cases,
)

CALIBRATION_MULTIPLIER = 100


def raw_point_function(point: tuple[int, int], order: int, p: int) -> int:
    evaluator = division_polynomial_evaluator(point, p)
    numerator = evaluator(p-1)
    denominator = evaluator(p-1+order)
    if numerator == 0 or denominator == 0:
        raise AssertionError("point-function defining ratio vanished")
    if math.gcd(order*order, p-1) != 1:
        raise AssertionError("point-function root was not unique")
    exponent = pow((order*order) % (p-1), -1, p-1)
    return pow(numerator * pow(denominator, -1, p) % p, exponent, p)


def phase_index(value: int, q: int, root: int, p: int) -> int:
    phase = pow(value, (p-1)//q, p)
    current = 1
    for exponent in range(q):
        if current == phase:
            return exponent
        current = current*root % p
    raise AssertionError("power-residue phase left declared roots")


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if 2*value < modulus else -1


def field_carry_sign(value: int, beta: int, p: int) -> int:
    a0 = value % p
    a1 = beta*a0 % p
    a2 = beta*a1 % p
    total = a0+a1+a2
    if total == p:
        return -1
    if total == 2*p:
        return 1
    raise AssertionError("field carry failed")


@dataclass(frozen=True)
class FormulaResult:
    formula: str
    state_count: int
    exact_digit_function: bool
    calibration_points: int
    calibration_covers_all_states: bool
    calibrated_exact_oracle: bool
    majority_accuracy: float
    conflicting_states: int
    radix_recovery_trials: int
    radix_recovery_successes: int


@dataclass(frozen=True)
class CaseResult:
    family: str
    q: int
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    phase_root: int
    phi_generator: int
    formulas: tuple[FormulaResult, ...]
    exact_calibrated_formulas: tuple[str, ...]
    best_majority_formula: str
    best_majority_accuracy: float


def evaluate_formula(
    formula: str,
    states: list[tuple[int, ...]],
    digits: list[int],
    q: int,
    order: int,
) -> FormulaResult:
    state_digits: dict[tuple[int, ...], set[int]] = {}
    state_counts: dict[tuple[int, ...], list[int]] = {}
    for state, digit in zip(states, digits):
        state_digits.setdefault(state, set()).add(digit)
        counts = state_counts.setdefault(state, [0]*q)
        counts[digit] += 1

    exact = all(len(values) == 1 for values in state_digits.values())
    conflicting = sum(len(values) > 1 for values in state_digits.values())
    correct = sum(max(counts) for counts in state_counts.values())
    majority_accuracy = correct/len(digits)

    calibration_limit = min(order-1, CALIBRATION_MULTIPLIER*q)
    lookup: dict[tuple[int, ...], int] = {}
    calibration_consistent = True
    for index in range(calibration_limit):
        state = states[index]
        digit = digits[index]
        if state in lookup and lookup[state] != digit:
            calibration_consistent = False
            break
        lookup[state] = digit
    covers = set(state_digits).issubset(lookup)
    calibrated_exact = exact and calibration_consistent and covers

    recovery_trials = 0
    recovery_successes = 0
    if calibrated_exact:
        # The exact state->digit map is enough for radix peeling.  Simulate a
        # deterministic sample of canonical scalars using the already checked
        # full-orbit state table.
        state_by_scalar = {k: states[k-1] for k in range(1, order)}
        state_by_scalar[0] = states[0]  # never queried once scalar reaches zero
        samples = sorted({
            1, 2, 3, order//7, order//5, order//3,
            order//2, order-3, order-2, order-1,
        })
        for original in samples:
            if not 1 <= original < order:
                continue
            current = original
            recovered = 0
            place = 1
            steps = 0
            while current:
                digit = lookup[state_by_scalar[current]]
                if digit != current % q:
                    break
                recovered += digit*place
                current = (current-digit)//q
                place *= q
                steps += 1
                if steps > math.ceil(math.log(order, q))+2:
                    break
            recovery_trials += 1
            recovery_successes += recovered == original and current == 0

    return FormulaResult(
        formula=formula,
        state_count=len(state_digits),
        exact_digit_function=exact,
        calibration_points=calibration_limit,
        calibration_covers_all_states=covers,
        calibrated_exact_oracle=calibrated_exact,
        majority_accuracy=majority_accuracy,
        conflicting_states=conflicting,
        radix_recovery_trials=recovery_trials,
        radix_recovery_successes=recovery_successes,
    )


def run_case(
    family: str,
    q: int,
    p: int,
    order: int,
    generator: tuple[int, int],
) -> CaseResult:
    if (p-1) % q:
        raise AssertionError("declared character order did not divide p-1")
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta*generator[0] % p, generator[1])]

    root = beta if q == 3 else canonical_mu7_root(p)
    phi_g = raw_point_function(generator, order, p)
    psi_g = division_polynomial_evaluator(generator, p)

    phases = []
    orientation_rows: dict[str, list[tuple[int, ...]]] = {
        "phase": [],
        "phase+half_y": [],
        "phase+chi_y": [],
        "phase+half_phi": [],
        "phase+chi_phi": [],
        "phase+field_carry_phi": [],
        "phase+half_y+chi_phi": [],
        "phase+half_phi+chi_y": [],
    }
    digits = []

    for k in range(1, order):
        phi_value = pow(phi_g, k*k, p)*psi_g(k) % p
        phase = phase_index(phi_value, q, root, p)
        point = points[k]
        assert point is not None
        y = point[1]
        row = {
            "phase": (phase,),
            "phase+half_y": (phase, half_sign(y, p)),
            "phase+chi_y": (phase, quadratic_character(y, p)),
            "phase+half_phi": (phase, half_sign(phi_value, p)),
            "phase+chi_phi": (phase, quadratic_character(phi_value, p)),
            "phase+field_carry_phi": (phase, field_carry_sign(phi_value, beta, p)),
            "phase+half_y+chi_phi": (
                phase, half_sign(y, p), quadratic_character(phi_value, p)
            ),
            "phase+half_phi+chi_y": (
                phase, half_sign(phi_value, p), quadratic_character(y, p)
            ),
        }
        phases.append(phase)
        digits.append(k % q)
        for name, state in row.items():
            orientation_rows[name].append(state)

    results = tuple(
        evaluate_formula(name, states, digits, q, order)
        for name, states in orientation_rows.items()
    )
    exact = tuple(
        result.formula for result in results if result.calibrated_exact_oracle
    )
    best = max(results, key=lambda result: (result.majority_accuracy, result.formula))
    return CaseResult(
        family=family,
        q=q,
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        phase_root=root,
        phi_generator=phi_g,
        formulas=results,
        exact_calibrated_formulas=exact,
        best_majority_formula=best.formula,
        best_majority_accuracy=best.majority_accuracy,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "higher_character_digit_oracle_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case("frozen_q3", 3, *case) for case in FROZEN_CASES]
    seventh_cases = generate_seventh_cases()
    cases.extend(run_case("generated_q7", 7, *case) for case in seventh_cases)

    by_family = {}
    for family in ("frozen_q3", "generated_q7"):
        rows = [case for case in cases if case.family == family]
        formulas = sorted({result.formula for case in rows for result in case.formulas})
        by_family[family] = {
            "q": rows[0].q,
            "cases": len(rows),
            "largest_order": max(case.order for case in rows),
            "formulas_exact_on_every_case": [
                formula for formula in formulas
                if all(formula in case.exact_calibrated_formulas for case in rows)
            ],
            "cases_with_any_exact_calibrated_oracle": sum(
                bool(case.exact_calibrated_formulas) for case in rows
            ),
            "minimum_best_majority_accuracy": min(
                case.best_majority_accuracy for case in rows
            ),
            "largest_order_best_majority_accuracy": max(
                rows, key=lambda case: case.order
            ).best_majority_accuracy,
        }

    payload = {
        "scope": (
            "q=3 on fifteen frozen j=0 prime-order toy subgroups and q=7 on "
            "fourteen deterministic p=43 mod 84 toy subgroups; no external "
            "point, key, wallet, or production target"
        ),
        "package": "HIGHER-CHARACTER-DIGIT-ORACLE-021",
        "radix_reduction": (
            "an exact public k mod q oracle recovers k by repeated "
            "Q <- [q^{-1}](Q-[r]G)"
        ),
        "cases": [asdict(case) for case in cases],
        "family_summary": by_family,
        "aggregate": {
            "cases": len(cases),
            "families_with_universal_exact_formula": [
                family for family, summary in by_family.items()
                if summary["formulas_exact_on_every_case"]
            ],
            "largest_order": max(case.order for case in cases),
        },
        "claim_boundary": [
            "Calibration uses only known public multiples and is capped at 100q points.",
            "A toy exact formula still needs an algebraic proof before secp256k1 use.",
            "Majority accuracy is an upper-bound diagnostic, not a noisy radix-recovery theorem.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
