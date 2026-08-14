#!/usr/bin/env python3
"""Exact Paley-tournament obstruction for the surviving UORC-056 EDS route.

This package closes a single pure division-polynomial character evaluator

    delta * chi(psi_m([k]G)) = (-1)^k

for every even index m over prime fields q = 3 (mod 4), whenever the marked odd
subgroup order n satisfies ((n-1)/2)^2 > 3q+1.  The proof uses only division-
polynomial composition, the standard x-coordinate difference identity, and the
quadratic-character correlation matrix over F_q.  It does not assume a bound on
m and does not enumerate m.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROFILE_ID = "UORC-056-EDS-PALEY-OBSTRUCTION-V10"
SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)

Point = tuple[int, int] | None
Curve = tuple[int, int, tuple[int, int]]


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def inv_mod(value: int, prime: int) -> int:
    return pow(value % prime, -1, prime)


def quadratic_character(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    return 1 if pow(residue, (prime - 1) // 2, prime) == 1 else -1


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
            (3 * x_left * x_left + curve_a) * inv_mod(2 * y_left, prime)
        ) % prime
    else:
        slope = (
            (y_right - y_left) * inv_mod(x_right - x_left, prime)
        ) % prime
    x_result = (slope * slope - x_left - x_right) % prime
    y_result = (slope * (x_left - x_result) - y_left) % prime
    return x_result, y_result


def ec_mul(scalar: int, point: Point, prime: int, curve_a: int = 0) -> Point:
    if scalar < 0:
        if point is None:
            return None
        return ec_mul(-scalar, (point[0], (-point[1]) % prime), prime, curve_a)
    result: Point = None
    addend = point
    current = scalar
    while current:
        if current & 1:
            result = ec_add(result, addend, prime, curve_a)
        addend = ec_add(addend, addend, prime, curve_a)
        current >>= 1
    return result


@dataclass
class DivisionPolynomialEvaluator:
    prime: int
    curve_a: int
    curve_b: int
    point: tuple[int, int]

    def __post_init__(self) -> None:
        x_value, y_value = self.point
        if y_value % self.prime == 0:
            raise ValueError("division recurrence requires a non-2-torsion point")
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
        if index in self.memo:
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


def load_corpora(base_grammar_path: Path) -> tuple[tuple[Curve, ...], tuple[Curve, ...]]:
    grammar = json.loads(base_grammar_path.read_text(encoding="utf-8"))
    discovery = tuple(parse_curve(row) for row in grammar["discovery_corpus"])
    holdout = tuple(parse_curve(row) for row in grammar["holdout_corpus"])
    return discovery, holdout


def verify_composition_identity(curve: Curve) -> int:
    prime, order, generator = curve
    base = DivisionPolynomialEvaluator(prime, 0, 7, generator)
    checked = 0
    for outer in range(2, 9):
        for inner in range(1, min(order, 10)):
            point = ec_mul(inner, generator, prime)
            if point is None:
                raise AssertionError("unexpected identity in composition replay")
            at_multiple = DivisionPolynomialEvaluator(prime, 0, 7, point)
            left = base.value(outer * inner)
            right = (
                at_multiple.value(outer)
                * pow(base.value(inner), outer * outer, prime)
            ) % prime
            if left != right:
                raise AssertionError(
                    f"composition identity failed p={prime}, a={outer}, b={inner}"
                )
            checked += 1
    return checked


def verify_difference_identity(curve: Curve) -> int:
    """Replay x([a]G)-x([b]G) through division polynomials."""
    prime, order, generator = curve
    half = (order - 1) // 2
    evaluator = DivisionPolynomialEvaluator(prime, 0, 7, generator)
    points = [None] + [ec_mul(index, generator, prime) for index in range(1, half + 1)]
    checked = 0
    for larger in range(2, half + 1):
        larger_point = points[larger]
        if larger_point is None:
            raise AssertionError("nonzero multiple became identity")
        for smaller in range(1, larger):
            smaller_point = points[smaller]
            if smaller_point is None:
                raise AssertionError("nonzero multiple became identity")
            psi_larger = evaluator.value(larger)
            psi_smaller = evaluator.value(smaller)
            denominator = (
                psi_larger * psi_larger * psi_smaller * psi_smaller
            ) % prime
            if denominator == 0:
                raise AssertionError("difference identity denominator vanished")
            right = (
                -evaluator.value(larger + smaller)
                * evaluator.value(larger - smaller)
                * inv_mod(denominator, prime)
            ) % prime
            left = (larger_point[0] - smaller_point[0]) % prime
            if left != right:
                raise AssertionError(
                    f"difference identity failed p={prime}, a={larger}, b={smaller}"
                )
            checked += 1
    return checked


def verify_paley_correlation(prime: int) -> int:
    """Verify sum_z chi(z)chi(z+1)=-1, which gives MM^T=qI-J."""
    total = sum(
        quadratic_character(value, prime)
        * quadratic_character(value + 1, prime)
        for value in range(prime)
    )
    if total != -1:
        raise AssertionError(f"Paley correlation failed for p={prime}: {total}")
    return total


def phase_normalization_truth_table() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for output_phase in (1, -1):
        rho_m = -output_phase
        for parity in (1, 0):
            scalar = 1 if parity else 2
            rho_mk = output_phase * (-1 if scalar & 1 else 1)
            sign_at_r = rho_mk * pow(rho_m, scalar * scalar)
            negation_factor = 1 if scalar & 1 else -1
            normalized = (
                sign_at_r
                if output_phase == 1
                else sign_at_r * negation_factor
            )
            if normalized != 1:
                raise AssertionError("global phase normalization failed")
            rows.append(
                {
                    "output_phase": output_phase,
                    "scalar_parity": parity,
                    "chi_psi_k_at_R": sign_at_r,
                    "chi_psi_k_at_phase_normalized_R": normalized,
                }
            )
    return rows


def curve_certificate(curve: Curve) -> dict[str, Any]:
    prime, order, generator = curve
    if order % 2 == 0:
        raise AssertionError("V10 requires odd subgroup order")
    if ec_mul(order, generator, prime) is not None:
        raise AssertionError("declared subgroup order is invalid")
    composition_checks = verify_composition_identity(curve)

    result: dict[str, Any] = {
        "p": prime,
        "n": order,
        "G": list(generator),
        "field_mod_4": prime % 4,
        "composition_checks": composition_checks,
    }
    if prime % 4 == 1:
        result.update(
            {
                "status": "excluded_by_even_index_negation_covariance",
                "reason": (
                    "psi_m(-Q)=-psi_m(Q) for even m but chi(-1)=+1, "
                    "so the character is invariant while parity is anti-invariant"
                ),
            }
        )
        return result
    if prime % 4 != 3:
        raise AssertionError("prime field must be 1 or 3 modulo 4")

    half = (order - 1) // 2
    left = half * half
    right = 3 * prime + 1
    difference_checks = verify_difference_identity(curve)
    paley_correlation = verify_paley_correlation(prime)
    excluded = left > right
    result.update(
        {
            "half_orbit_x_count": half,
            "paley_necessary_left": left,
            "paley_necessary_right": right,
            "strict_margin": left - right,
            "difference_identity_checks": difference_checks,
            "paley_correlation": paley_correlation,
            "status": (
                "excluded_by_paley_tournament_bound"
                if excluded
                else "not_excluded_by_paley_tournament_bound"
            ),
        }
    )
    return result


def secp256k1_certificate() -> dict[str, Any]:
    half = (SECP256K1_N - 1) // 2
    left = half * half
    right = 3 * SECP256K1_P + 1
    return {
        "p": str(SECP256K1_P),
        "n": str(SECP256K1_N),
        "p_mod_4": SECP256K1_P % 4,
        "half_orbit_x_count": str(half),
        "paley_necessary_left": str(left),
        "paley_necessary_right": str(right),
        "strict_margin": str(left - right),
        "left_bit_length": left.bit_length(),
        "right_bit_length": right.bit_length(),
        "excluded": left > right,
        "equivalent_integer_test": "(n-1)^2 > 12p+4",
    }


def run(grammar_path: Path) -> dict[str, Any]:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    if grammar["profile_id"] != PROFILE_ID:
        raise AssertionError("unexpected V10 grammar")
    base_grammar_path = Path(grammar["base_corpus_grammar"])
    discovery, holdout = load_corpora(base_grammar_path)
    certificates = [curve_certificate(curve) for curve in discovery + holdout]
    unresolved = [
        row for row in certificates if row["status"].startswith("not_excluded")
    ]
    secp = secp256k1_certificate()
    if not secp["excluded"]:
        raise AssertionError("secp256k1 Paley certificate unexpectedly failed")

    q3_rows = [row for row in certificates if row["field_mod_4"] == 3]
    q1_rows = [row for row in certificates if row["field_mod_4"] == 1]
    return {
        "schema_version": "1.0",
        "experiment": PROFILE_ID,
        "grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "decision": (
            "all_single_pure_division_polynomial_character_evaluators_closed_"
            "on_the_18_curve_corpus_and_secp256k1"
            if not unresolved
            else "some_declared_curves_remain_open"
        ),
        "theorem": {
            "target": "delta*chi(psi_m([k]G))=(-1)^k for every 1<=k<n",
            "assumptions": [
                "q is an odd prime with q=3 mod 4",
                "H=<G> has odd order n",
                "m is even and the character is defined on every nonzero subgroup point",
                "delta is one global sign phase",
            ],
            "necessary_condition": "((n-1)/2)^2 <= 3q+1",
            "contrapositive": (
                "if ((n-1)/2)^2 > 3q+1 then no even index m and no global "
                "phase delta can realize canonical parity"
            ),
            "proof_chain": [
                "composition makes chi(psi_k(R'))=+1 for every 1<=k<n after at most replacing R=[m]G by -R",
                "the division-polynomial difference identity makes chi(x([i]R')-x([j]R'))=+1 for 1<=i<j<=(n-1)/2",
                "these distinct x-coordinates form a transitive subtournament in the Paley tournament",
                "the Paley character matrix M satisfies MM^T=qI-J and has operator norm sqrt(q)",
                "the transitive sign matrix T obeys ||T||^2 >= (t^2-1)/3 for t=(n-1)/2",
                "therefore t^2<=3q+1",
            ],
        },
        "phase_normalization_truth_table": phase_normalization_truth_table(),
        "corpus": {
            "discovery_curves": len(discovery),
            "holdout_curves": len(holdout),
            "total_curves": len(certificates),
            "q_1_mod_4_closed_by_covariance": len(q1_rows),
            "q_3_mod_4_tested_by_paley": len(q3_rows),
            "q_3_mod_4_closed_by_paley": sum(
                row["status"] == "excluded_by_paley_tournament_bound"
                for row in q3_rows
            ),
            "unresolved_curves": len(unresolved),
        },
        "curve_certificates": certificates,
        "secp256k1": secp,
        "review_status": (
            "self-contained mathematical proof and executable identity certificates complete; "
            "independent peer review and formal-assistant transcription remain pending"
        ),
        "claim_boundary": [
            "V10 closes one pure factor delta*chi(psi_m(Q)) for every index m; it does not close products or ratios of several division-polynomial factors.",
            "The theorem is an algebraic impossibility result, not an evaluator and not an ECDLP algorithm.",
            "The Paley argument applies to q=3 mod 4; q=1 mod 4 was already closed by negation covariance.",
            "No external target point, wallet, real key or unknown production scalar is used.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path("experiments/uorc056/eds_paley_obstruction_grammar.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/eds_paley_obstruction_results.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("EDS Paley obstruction artifact drift")
        print("UORC056_EDS_PALEY_OBSTRUCTION_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
