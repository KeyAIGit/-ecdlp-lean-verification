#!/usr/bin/env python3
"""UORC-056 division-polynomial and Miller frontier V9.

This package separates two questions that the V8 divisor barrier leaves open:

1. Does square-root odd-divisor support force square-root evaluation cost?
2. Do long Miller or division-polynomial chains evade the rational-character
   obstruction?

The answer to the first question is no in unrestricted straight-line programs.
The n-th division polynomial has quadratic odd-support growth but is evaluable
from the standard doubling recurrences with a logarithmic-size dependency DAG.

The answer for classical terminal Miller functions is much stronger: their
odd divisor support is at most two for every index. V8 therefore excludes one
terminal Miller function, and any product of too few independent terminal
Miller functions, regardless of Miller-loop length.

For division polynomials, negation covariance closes every odd index and every
even index over fields with chi(-1)=+1. The secp256k1-specific surviving case is
an even index over p=3 mod 4. The composition identity reduces it to a decimated
EDS residue sequence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

PROFILE_ID = "UORC-056-DIVISION-POLYNOMIAL-FRONTIER-V9"
SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
    16,
)
SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
    16,
)
SECP_V8_SUPPORT_LOWER_BOUND = (
    216543324404233567658511113820216134562
)

Point = tuple[int, int] | None
Curve = tuple[int, int, tuple[int, int]]


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def inv_mod(value: int, prime: int) -> int:
    return pow(value % prime, -1, prime)


def ec_add(left: Point, right: Point, prime: int, curve_a: int = 0) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x_left, y_left = left
    x_right, y_right = right
    if x_left == x_right and (y_left + y_right) % prime == 0:
        return None
    if left == right:
        if y_left % prime == 0:
            return None
        slope = (
            (3 * x_left * x_left + curve_a)
            * inv_mod(2 * y_left, prime)
        ) % prime
    else:
        slope = (
            (y_right - y_left)
            * inv_mod(x_right - x_left, prime)
        ) % prime
    x_result = (slope * slope - x_left - x_right) % prime
    y_result = (slope * (x_left - x_result) - y_left) % prime
    return x_result, y_result


def ec_mul(scalar: int, point: Point, prime: int, curve_a: int = 0) -> Point:
    if scalar < 0:
        assert point is not None
        return ec_mul(
            -scalar,
            (point[0], (-point[1]) % prime),
            prime,
            curve_a,
        )
    result: Point = None
    addend = point
    current = scalar
    while current:
        if current & 1:
            result = ec_add(result, addend, prime, curve_a)
        addend = ec_add(addend, addend, prime, curve_a)
        current >>= 1
    return result


def quadratic_character(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    return 1 if pow(residue, (prime - 1) // 2, prime) == 1 else -1


@dataclass
class DivisionPolynomialEvaluator:
    prime: int
    curve_a: int
    curve_b: int
    point: tuple[int, int]

    def __post_init__(self) -> None:
        x_value, y_value = self.point
        if y_value % self.prime == 0:
            raise ValueError("division recurrence requires non-2-torsion point")
        p = self.prime
        a = self.curve_a
        b = self.curve_b
        x = x_value % p
        y = y_value % p
        self.inverse_psi_two = inv_mod(2 * y, p)
        self.memo: dict[int, int] = {
            0: 0,
            1: 1,
            2: (2 * y) % p,
            3: (
                3 * pow(x, 4, p)
                + 6 * a * x * x
                + 12 * b * x
                - a * a
            ) % p,
            4: (
                4
                * y
                * (
                    pow(x, 6, p)
                    + 5 * a * pow(x, 4, p)
                    + 20 * b * pow(x, 3, p)
                    - 5 * a * a * x * x
                    - 4 * a * b * x
                    - 8 * b * b
                    - a**3
                )
            ) % p,
        }

    def value(self, index: int) -> int:
        if index < 0:
            return (-self.value(-index)) % self.prime
        cached = self.memo.get(index)
        if cached is not None or index in self.memo:
            return self.memo[index]
        p = self.prime
        if index & 1:
            half = (index - 1) // 2
            result = (
                self.value(half + 2) * pow(self.value(half), 3, p)
                - self.value(half - 1) * pow(self.value(half + 1), 3, p)
            ) % p
        else:
            half = index // 2
            result = (
                self.value(half)
                * self.inverse_psi_two
                * (
                    self.value(half + 2) * pow(self.value(half - 1), 2, p)
                    - self.value(half - 2) * pow(self.value(half + 1), 2, p)
                )
            ) % p
        self.memo[index] = result
        return result


def parse_curve(row: dict[str, Any]) -> Curve:
    return int(row["p"]), int(row["n"]), (int(row["G"][0]), int(row["G"][1]))


def load_corpora(grammar_path: Path) -> tuple[tuple[Curve, ...], tuple[Curve, ...]]:
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    discovery = tuple(parse_curve(row) for row in grammar["discovery_corpus"])
    holdout = tuple(parse_curve(row) for row in grammar["holdout_corpus"])
    return discovery, holdout


def division_polynomial_odd_support(index: int) -> int:
    if index <= 0:
        raise ValueError("index must be positive")
    return index * index - 1 if index & 1 else index * index


def miller_odd_support_slots(index: int) -> tuple[str, str]:
    if index <= 0:
        raise ValueError("index must be positive")
    if index & 1:
        return "P", "[m]P"
    return "[m]P", "O"


def miller_odd_support_upper_bound(index: int) -> int:
    miller_odd_support_slots(index)
    return 2


def dependency_closure(index: int) -> set[int]:
    if index <= 0:
        raise ValueError("index must be positive")
    seen: set[int] = set()

    def visit(current: int) -> None:
        current = abs(current)
        if current in seen:
            return
        seen.add(current)
        if current <= 4:
            return
        if current & 1:
            half = (current - 1) // 2
            dependencies = (half + 2, half, half - 1, half + 1)
        else:
            half = current // 2
            dependencies = (
                half,
                half + 2,
                half - 1,
                half - 2,
                half + 1,
                2,
            )
        for dependency in dependencies:
            visit(dependency)

    visit(index)
    return seen


def recurrence_cost(index: int) -> dict[str, int]:
    closure = dependency_closure(index)
    nonbase = sum(value > 4 for value in closure)
    return {
        "dependency_nodes": len(closure),
        "nonbase_recurrence_nodes": nonbase,
        "multiplication_upper_bound": 6 * nonbase + 32,
        "addition_subtraction_upper_bound": nonbase + 16,
        "field_inversions": 1,
    }


def minimum_even_index_for_support(required_support: int) -> int:
    if required_support <= 0:
        return 2
    candidate = math.isqrt(required_support)
    if candidate * candidate < required_support:
        candidate += 1
    if candidate & 1:
        candidate += 1
    return max(candidate, 2)


def parity_value(scalar: int) -> int:
    return -1 if scalar & 1 else 1


def screen_even_indices(
    curves: Iterable[Curve],
    maximum_index: int,
) -> dict[str, Any]:
    if maximum_index < 2:
        raise ValueError("maximum index must be at least two")
    even_indices = tuple(range(2, maximum_index + 1, 2))
    zero_counts = [0] * (maximum_index + 1)
    direct_matches = [0] * (maximum_index + 1)
    total_points = 0
    per_curve: list[dict[str, Any]] = []

    for prime, order, generator in curves:
        local_zero = [0] * (maximum_index + 1)
        local_matches = [0] * (maximum_index + 1)
        local_total = order - 1
        for scalar in range(1, order):
            point = ec_mul(scalar, generator, prime)
            if point is None:
                raise AssertionError("nonzero subgroup point became identity")
            evaluator = DivisionPolynomialEvaluator(prime, 0, 7, point)
            target = parity_value(scalar)
            for index in even_indices:
                sign = quadratic_character(evaluator.value(index), prime)
                if sign == 0:
                    zero_counts[index] += 1
                    local_zero[index] += 1
                else:
                    direct_matches[index] += int(sign == target)
                    local_matches[index] += int(sign == target)
        total_points += local_total

        local_limit = min(maximum_index, 8 * order)
        local_exact: list[dict[str, int]] = []
        local_best = {"matches": -1, "index": None, "output_phase": None}
        for index in range(2, local_limit + 1, 2):
            if local_zero[index]:
                continue
            direct = local_matches[index]
            best_matches = max(direct, local_total - direct)
            phase = 1 if direct >= local_total - direct else -1
            if best_matches > local_best["matches"]:
                local_best = {
                    "matches": best_matches,
                    "index": index,
                    "output_phase": phase,
                }
            if best_matches == local_total:
                local_exact.append({"index": index, "output_phase": phase})
        per_curve.append(
            {
                "p": prime,
                "n": order,
                "search_limit": local_limit,
                "exact_candidates": local_exact,
                "best": {
                    **local_best,
                    "total": local_total,
                    "accuracy": f"{local_best['matches'] / local_total:.9f}",
                },
            }
        )

    defined = 0
    exact: list[dict[str, int]] = []
    best = {"matches": -1, "index": None, "output_phase": None}
    for index in even_indices:
        if zero_counts[index]:
            continue
        defined += 1
        direct = direct_matches[index]
        best_matches = max(direct, total_points - direct)
        phase = 1 if direct >= total_points - direct else -1
        if best_matches > best["matches"]:
            best = {
                "matches": best_matches,
                "index": index,
                "output_phase": phase,
            }
        if best_matches == total_points:
            exact.append({"index": index, "output_phase": phase})

    return {
        "maximum_index": maximum_index,
        "even_indices_tested": len(even_indices),
        "everywhere_defined_indices": defined,
        "total_nonzero_points": total_points,
        "exact_candidates": exact,
        "best": {
            **best,
            "total": total_points,
            "accuracy": f"{best['matches'] / total_points:.9f}",
        },
        "per_curve": per_curve,
    }


def verify_composition_identity(curve: Curve) -> None:
    prime, order, generator = curve
    base = DivisionPolynomialEvaluator(prime, 0, 7, generator)
    for outer in range(2, 9):
        for inner in range(2, min(order, 10)):
            point = ec_mul(inner, generator, prime)
            if point is None:
                continue
            at_multiple = DivisionPolynomialEvaluator(prime, 0, 7, point)
            left = base.value(outer * inner)
            right = (
                at_multiple.value(outer)
                * pow(base.value(inner), outer * outer, prime)
            ) % prime
            if left != right:
                raise AssertionError(
                    f"composition identity failed p={prime}, m={outer}, k={inner}"
                )


def verify_negation_law(curve: Curve) -> None:
    prime, order, generator = curve
    point = ec_mul(2, generator, prime)
    if point is None:
        raise AssertionError("unexpected identity")
    negative = (point[0], (-point[1]) % prime)
    positive_eval = DivisionPolynomialEvaluator(prime, 0, 7, point)
    negative_eval = DivisionPolynomialEvaluator(prime, 0, 7, negative)
    for index in range(1, 33):
        expected = positive_eval.value(index)
        if index % 2 == 0:
            expected = (-expected) % prime
        if negative_eval.value(index) != expected:
            raise AssertionError(
                f"negation law failed p={prime}, m={index}"
            )


def run(grammar_path: Path, maximum_index: int) -> dict[str, Any]:
    discovery, holdout = load_corpora(grammar_path)
    for curve in discovery:
        verify_composition_identity(curve)
        verify_negation_law(curve)
        prime, order, generator = curve
        evaluator = DivisionPolynomialEvaluator(prime, 0, 7, generator)
        if evaluator.value(order) != 0:
            raise AssertionError("division polynomial did not detect subgroup order")

    screen = screen_even_indices(discovery, maximum_index)
    minimum_even_index = minimum_even_index_for_support(
        SECP_V8_SUPPORT_LOWER_BOUND
    )
    cost = recurrence_cost(minimum_even_index)
    minimum_terminal_miller_factors = (
        SECP_V8_SUPPORT_LOWER_BOUND + 1
    ) // 2

    return {
        "schema_version": "1.0",
        "experiment": PROFILE_ID,
        "review_status": (
            "the algebraic identities and executable checks are complete; "
            "literature source locking and formalization remain pending"
        ),
        "input_corpus_sha256": hashlib.sha256(
            stable_json(
                {
                    "discovery": discovery,
                    "holdout": holdout,
                }
            ).encode("utf-8")
        ).hexdigest(),
        "division_polynomial": {
            "divisor_formula": (
                "div(psi_m)=sum_{T in E[m] minus {O}}[T]-(m^2-1)[O], "
                "for char(F_q) not dividing m"
            ),
            "odd_support_formula": {
                "m_odd": "m^2-1",
                "m_even": "m^2",
            },
            "negation_formula": "psi_m(-Q)=(-1)^(m+1)*psi_m(Q)",
            "composition_formula": (
                "psi_(m*k)(G)=psi_m([k]G)*psi_k(G)^(m^2)"
            ),
            "quadratic_character_reduction": {
                "m_odd": "chi(psi_m([k]G))=rho_(mk)*rho_k",
                "m_even": "chi(psi_m([k]G))=rho_(mk)",
                "rho_j": "chi(psi_j(G))",
            },
        },
        "miller": {
            "divisor_formula": "div(f_(m,P))=m[P]-[mP]-(m-1)[O]",
            "odd_support_upper_bound_for_every_index": 2,
            "single_terminal_function_status": (
                "excluded by V8 whenever the required support lower bound exceeds two"
            ),
            "minimum_independent_terminal_functions_for_secp256k1": str(
                minimum_terminal_miller_factors
            ),
            "interpretation": (
                "Miller-loop length does not create odd support because the "
                "line divisors telescope to at most two odd slots"
            ),
        },
        "support_to_cost_separation": {
            "secp256k1_V8_required_support": str(
                SECP_V8_SUPPORT_LOWER_BOUND
            ),
            "minimum_even_division_index_meeting_support": str(
                minimum_even_index
            ),
            "minimum_even_index_bit_length": minimum_even_index.bit_length(),
            "division_polynomial_odd_support": str(
                division_polynomial_odd_support(minimum_even_index)
            ),
            "recurrence_DAG": cost,
            "decision": (
                "odd divisor support alone cannot imply square-root field-operation cost"
            ),
        },
        "covariance_classification": {
            "odd_index": (
                "x-only and invariant under Q -> -Q, so impossible for canonical parity on every odd cycle"
            ),
            "even_index_q_1_mod_4": (
                "psi_m changes sign but chi(-1)=+1, so the character remains invariant and is impossible"
            ),
            "even_index_q_3_mod_4": (
                "anti-invariant and symmetry-compatible; not solved by covariance alone"
            ),
            "uniform_mixed_mod4_transfer": (
                "a pure division-polynomial character cannot transfer unchanged across corpora containing both q=1 mod 4 and q=3 mod 4"
            ),
        },
        "bounded_discovery_screen": screen,
        "surviving_secp256k1_frontier": {
            "field_congruence": "p=3 mod 4",
            "index_parity": "even",
            "minimum_index_from_V8": str(minimum_even_index),
            "sequence_normal_form": "k -> rho_(m*k)",
            "status": (
                "open EDS-decimation problem; not an independent Miller route"
            ),
        },
        "holdout_observation": {
            "holdout_curve_count": len(holdout),
            "contains_q_1_mod_4": any(prime % 4 == 1 for prime, _, _ in holdout),
            "contains_q_3_mod_4": any(prime % 4 == 3 for prime, _, _ in holdout),
        },
        "claim_boundary": [
            "The Miller closure concerns quadratic characters of classical terminal Miller functions and finite products of them.",
            "The support-to-cost separation is a counterexample to unrestricted degree or support based circuit lower bounds, not a parity evaluator.",
            "Even-index division-polynomial characters over q=3 mod 4 remain open after the stated lower threshold.",
            "No external point, wallet, real key or unknown production scalar is used.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        ),
    )
    parser.add_argument("--maximum-index", type=int, default=4096)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/uorc056/division_polynomial_frontier_results.json"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar, args.maximum_index))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("division-polynomial frontier artifact drift")
        print("UORC056_DIVISION_POLYNOMIAL_FRONTIER_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
