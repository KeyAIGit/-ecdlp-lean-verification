#!/usr/bin/env python3
"""UORC-056 C28 nonlinear rational-state pole-budget boundary.

This package builds a small exact pole-budget compiler, proves the zero-count
and translation-defect lower bounds at the mathematical-note level, and replays
finite rational-function controls over prime fields. It accepts no unknown
production point, private key, wallet, hidden scalar, or target-dependent
advice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

PROFILE_ID = "UORC-056-NONLINEAR-POLE-BUDGET-C28"
DEFAULT_OUTPUT = Path(
    "experiments/parity_lift_000/uorc056_nonlinear_pole_budget_result.json"
)

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_HALF = (SECP_N - 1) // 2
SECP_AB_STATE_POLE_LOWER = (SECP_HALF - 9 + 6) // 7
SECP_AB_POLY_DEGREE_LOWER = (SECP_HALF - 9 + 41) // 42

# q > n, with q prime, so the scalar-index controls live in F_q.
INTERPOLATION_CASES = (
    (11, 5),
    (17, 7),
    (23, 11),
    (29, 13),
    (67, 31),
)


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def digest_without_digest(value: dict[str, Any]) -> str:
    copy = dict(value)
    copy.pop("digest", None)
    return hashlib.sha256(stable_json(copy).encode("utf-8")).hexdigest()


def trim(poly: Sequence[int], p: int) -> list[int]:
    out = [int(value) % p for value in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def degree(poly: Sequence[int], p: int) -> int:
    normalized = trim(poly, p)
    return -1 if normalized == [0] else len(normalized) - 1


def poly_add(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    return trim(
        [
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
            for index in range(size)
        ],
        p,
    )


def poly_neg(poly: Sequence[int], p: int) -> list[int]:
    return trim([-value for value in poly], p)


def poly_sub(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    return poly_add(left, poly_neg(right, p), p)


def poly_scale(poly: Sequence[int], scalar: int, p: int) -> list[int]:
    return trim([scalar * value for value in poly], p)


def poly_mul(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = (out[i + j] + a * b) % p
    return trim(out, p)


def poly_pow(poly: Sequence[int], exponent: int, p: int) -> list[int]:
    if exponent < 0:
        raise ValueError("polynomial exponent must be nonnegative")
    result = [1]
    base = trim(poly, p)
    power = exponent
    while power:
        if power & 1:
            result = poly_mul(result, base, p)
        base = poly_mul(base, base, p)
        power >>= 1
    return result


def poly_eval(poly: Sequence[int], x: int, p: int) -> int:
    value = 0
    for coefficient in reversed(poly):
        value = (value * x + coefficient) % p
    return value


def poly_divmod(
    numerator: Sequence[int], denominator: Sequence[int], p: int
) -> tuple[list[int], list[int]]:
    num = trim(numerator, p)
    den = trim(denominator, p)
    if den == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if degree(num, p) < degree(den, p):
        return [0], num
    quotient = [0] * (degree(num, p) - degree(den, p) + 1)
    inverse = pow(den[-1], -1, p)
    while num != [0] and degree(num, p) >= degree(den, p):
        shift = degree(num, p) - degree(den, p)
        factor = num[-1] * inverse % p
        quotient[shift] = factor
        for index, coefficient in enumerate(den):
            num[index + shift] = (
                num[index + shift] - factor * coefficient
            ) % p
        num = trim(num, p)
    return trim(quotient, p), num


def poly_gcd(left: Sequence[int], right: Sequence[int], p: int) -> list[int]:
    a = trim(left, p)
    b = trim(right, p)
    while b != [0]:
        _, remainder = poly_divmod(a, b, p)
        a, b = b, remainder
    if a == [0]:
        return [0]
    return poly_scale(a, pow(a[-1], -1, p), p)


def poly_shift(poly: Sequence[int], constant: int, p: int) -> list[int]:
    """Return f(X+constant) by Horner composition."""
    result = [0]
    linear = [constant % p, 1]
    for coefficient in reversed(trim(poly, p)):
        result = poly_mul(result, linear, p)
        result[0] = (result[0] + coefficient) % p
    return trim(result, p)


def product_linear_roots(roots: Iterable[int], p: int) -> list[int]:
    result = [1]
    for root in roots:
        result = poly_mul(result, [(-root) % p, 1], p)
    return result


def interpolate(nodes: Sequence[int], values: Sequence[int], p: int) -> list[int]:
    if len(nodes) != len(values):
        raise ValueError("node/value length mismatch")
    if len(set(node % p for node in nodes)) != len(nodes):
        raise ValueError("interpolation nodes must be distinct")
    result = [0]
    for index, node in enumerate(nodes):
        basis = [1]
        denominator = 1
        for other_index, other in enumerate(nodes):
            if index == other_index:
                continue
            basis = poly_mul(basis, [(-other) % p, 1], p)
            denominator = denominator * (node - other) % p
        basis = poly_scale(basis, values[index] * pow(denominator, -1, p), p)
        result = poly_add(result, basis, p)
    return trim(result, p)


@dataclass(frozen=True)
class RationalFunction:
    numerator: tuple[int, ...]
    denominator: tuple[int, ...]
    p: int

    @staticmethod
    def make(
        numerator: Sequence[int], denominator: Sequence[int], p: int
    ) -> "RationalFunction":
        num = trim(numerator, p)
        den = trim(denominator, p)
        if den == [0]:
            raise ZeroDivisionError("zero rational denominator")
        common = poly_gcd(num, den, p)
        if common != [0] and degree(common, p) > 0:
            num, remainder_num = poly_divmod(num, common, p)
            den, remainder_den = poly_divmod(den, common, p)
            if remainder_num != [0] or remainder_den != [0]:
                raise AssertionError("gcd did not divide rational function")
        leading_inverse = pow(den[-1], -1, p)
        num = poly_scale(num, leading_inverse, p)
        den = poly_scale(den, leading_inverse, p)
        return RationalFunction(tuple(num), tuple(den), p)

    @staticmethod
    def constant(value: int, p: int) -> "RationalFunction":
        return RationalFunction.make([value], [1], p)

    @property
    def pole_degree(self) -> int:
        return max(degree(self.numerator, self.p), degree(self.denominator, self.p))

    def __add__(self, other: "RationalFunction") -> "RationalFunction":
        self._same_field(other)
        return RationalFunction.make(
            poly_add(
                poly_mul(self.numerator, other.denominator, self.p),
                poly_mul(other.numerator, self.denominator, self.p),
                self.p,
            ),
            poly_mul(self.denominator, other.denominator, self.p),
            self.p,
        )

    def __neg__(self) -> "RationalFunction":
        return RationalFunction.make(
            poly_neg(self.numerator, self.p), self.denominator, self.p
        )

    def __sub__(self, other: "RationalFunction") -> "RationalFunction":
        return self + (-other)

    def __mul__(self, other: "RationalFunction") -> "RationalFunction":
        self._same_field(other)
        return RationalFunction.make(
            poly_mul(self.numerator, other.numerator, self.p),
            poly_mul(self.denominator, other.denominator, self.p),
            self.p,
        )

    def inverse(self) -> "RationalFunction":
        if list(self.numerator) == [0]:
            raise ZeroDivisionError("inverse of zero rational function")
        return RationalFunction.make(self.denominator, self.numerator, self.p)

    def __truediv__(self, other: "RationalFunction") -> "RationalFunction":
        return self * other.inverse()

    def __pow__(self, exponent: int) -> "RationalFunction":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        return RationalFunction.make(
            poly_pow(self.numerator, exponent, self.p),
            poly_pow(self.denominator, exponent, self.p),
            self.p,
        )

    def evaluate(self, x: int) -> int:
        denominator = poly_eval(self.denominator, x, self.p)
        if denominator == 0:
            raise ZeroDivisionError("evaluation at a pole")
        return (
            poly_eval(self.numerator, x, self.p)
            * pow(denominator, -1, self.p)
            % self.p
        )

    def _same_field(self, other: "RationalFunction") -> None:
        if self.p != other.p:
            raise ValueError("rational functions belong to different fields")


@dataclass(frozen=True)
class PoleBudget:
    value: int
    expression: str

    @staticmethod
    def leaf(value: int, name: str) -> "PoleBudget":
        if value < 0:
            raise ValueError("pole budget must be nonnegative")
        return PoleBudget(value, name)

    @staticmethod
    def constant() -> "PoleBudget":
        return PoleBudget(0, "const")

    def add(self, other: "PoleBudget") -> "PoleBudget":
        return PoleBudget(self.value + other.value, f"({self.expression}+{other.expression})")

    def multiply(self, other: "PoleBudget") -> "PoleBudget":
        return PoleBudget(self.value + other.value, f"({self.expression}*{other.expression})")

    def inverse(self) -> "PoleBudget":
        return PoleBudget(self.value, f"inv({self.expression})")

    def power(self, exponent: int) -> "PoleBudget":
        if exponent < 0:
            return self.inverse().power(-exponent)
        return PoleBudget(exponent * self.value, f"({self.expression}^{exponent})")


def compiled_ab_decoder_budget(a_budget: int, b_budget: int) -> dict[str, Any]:
    """Compile the direct A/B parity decoder with degree-only pole rules."""
    a = PoleBudget.leaf(a_budget, "A")
    b = PoleBudget.leaf(b_budget, "B")
    x = PoleBudget.leaf(2, "x")
    y = PoleBudget.leaf(3, "y")
    a2 = a.power(2)
    axb = a.multiply(x).multiply(b)
    x2b2 = x.power(2).multiply(b.power(2))
    numerator = a2.add(axb).add(x2b2)
    denominator = y.multiply(a)
    quotient = numerator.multiply(denominator.inverse())
    expected = 4 * a_budget + 3 * b_budget + 9
    if quotient.value != expected:
        raise AssertionError("compiled A/B budget drifted")
    return {
        "a_budget": a_budget,
        "b_budget": b_budget,
        "numerator_budget": numerator.value,
        "denominator_budget": denominator.value,
        "decoder_budget": quotient.value,
        "closed_form": "4*a+3*b+9",
    }


def parity_interpolation_case(field_prime: int, order: int) -> dict[str, Any]:
    nodes = list(range(1, order))
    values = [1 if scalar % 2 == 0 else field_prime - 1 for scalar in nodes]
    polynomial = interpolate(nodes, values, field_prime)
    f = RationalFunction.make(polynomial, [1], field_prime)
    one = RationalFunction.constant(1, field_prime)
    residual = f**2 - one
    if list(residual.numerator) == [0]:
        raise AssertionError("parity square residual became identically zero")
    residual_roots = [scalar for scalar in nodes if residual.evaluate(scalar) == 0]
    if len(residual_roots) != order - 1:
        raise AssertionError("square residual lost a marked parity root")
    if f.pole_degree < (order - 1) // 2:
        raise AssertionError("interpolated parity violated pole lower bound")

    shifted = RationalFunction.make(poly_shift(polynomial, 1, field_prime), [1], field_prime)
    defect = shifted + f
    if list(defect.numerator) == [0]:
        raise AssertionError("odd-cycle translation defect became zero")
    defect_roots = [
        scalar
        for scalar in range(1, order - 1)
        if defect.evaluate(scalar) == 0
    ]
    if len(defect_roots) != order - 2:
        raise AssertionError("translation defect lost a marked edge root")
    if defect.pole_degree < order - 2:
        raise AssertionError("translation defect degree violated zero count")

    return {
        "field_prime": field_prime,
        "order": order,
        "half": (order - 1) // 2,
        "interpolating_polynomial_degree": degree(polynomial, field_prime),
        "parity_function_pole_degree": f.pole_degree,
        "square_residual_pole_degree": residual.pole_degree,
        "square_residual_marked_roots": len(residual_roots),
        "translation_defect_pole_degree": defect.pole_degree,
        "translation_defect_marked_roots": len(defect_roots),
    }


def rational_budget_controls() -> dict[str, Any]:
    """Check the budget algebra on deterministic rational functions."""
    fields = (101, 103, 107)
    checks = 0
    for p in fields:
        samples = [
            RationalFunction.make([1, 2], [3, 1], p),
            RationalFunction.make([2, 0, 1], [4, 1], p),
            RationalFunction.make([5, 1], [1, 0, 1], p),
            RationalFunction.make([7, 3, 0, 1], [2, 1], p),
        ]
        for left in samples:
            for right in samples:
                if (left + right).pole_degree > left.pole_degree + right.pole_degree:
                    raise AssertionError("addition exceeded pole budget")
                if (left * right).pole_degree > left.pole_degree + right.pole_degree:
                    raise AssertionError("multiplication exceeded pole budget")
                if left.inverse().pole_degree != left.pole_degree:
                    raise AssertionError("inversion changed total pole degree")
                checks += 3
        for value in samples:
            for exponent in range(5):
                if (value**exponent).pole_degree > exponent * value.pole_degree:
                    raise AssertionError("power exceeded pole budget")
                checks += 1
    return {
        "fields": len(fields),
        "deterministic_rational_functions_per_field": 4,
        "exact_budget_checks": checks,
        "all_checks_passed": True,
    }


def minimum_binary_gate_count(target_budget: int, initial_budget: int) -> int:
    if target_budget < 0 or initial_budget <= 0:
        raise ValueError("invalid gate-bound arguments")
    gates = 0
    capacity = initial_budget
    while capacity < target_budget:
        capacity *= 2
        gates += 1
    return gates


def build_result() -> dict[str, Any]:
    controls = [parity_interpolation_case(*case) for case in INTERPOLATION_CASES]
    budget_controls = rational_budget_controls()
    ab_equal = compiled_ab_decoder_budget(
        SECP_AB_STATE_POLE_LOWER, SECP_AB_STATE_POLE_LOWER
    )
    predecessor_budget = 7 * (SECP_AB_STATE_POLE_LOWER - 1) + 9
    current_budget = 7 * SECP_AB_STATE_POLE_LOWER + 9
    if not predecessor_budget < SECP_HALF <= current_budget:
        raise AssertionError("A/B state lower bound is not minimal")
    poly_predecessor = 42 * (SECP_AB_POLY_DEGREE_LOWER - 1) + 9
    poly_current = 42 * SECP_AB_POLY_DEGREE_LOWER + 9
    if not poly_predecessor < SECP_HALF <= poly_current:
        raise AssertionError("A/B polynomial degree lower bound is not minimal")

    leaf_gate_bounds = {
        str(initial): minimum_binary_gate_count(SECP_HALF, initial)
        for initial in (1, 5, 7, 10, 100, 256)
    }

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "pole_zero_theorem": {
            "hypotheses": (
                "f is a nonconstant rational function on a smooth projective "
                "curve, regular on the n-1 marked nonzero subgroup points, "
                "char != 2, and f([k]G)=(-1)^k"
            ),
            "residual": "h=f^2-1 is nonzero and has at least n-1 marked zeros",
            "pole_transfer": "deg_poles(h)=2*deg_poles(f)",
            "conclusion": "deg_poles(f)>=(n-1)/2",
            "secp256k1_lower_bound": SECP_HALF,
            "secp256k1_lower_bound_bits": SECP_HALF.bit_length(),
        },
        "translation_defect_theorem": {
            "defect": "Delta_f(P)=f(P+G)+f(P)",
            "nonzero_reason": (
                "if Delta_f were identically zero, n odd iterations would give "
                "f=-f, hence f=0 in characteristic not 2"
            ),
            "marked_zeros": "at least n-2 consecutive non-wrap subgroup edges",
            "pole_transfer": "deg_poles(Delta_f)<=2*deg_poles(f)",
            "conclusion": "deg_poles(f)>=(n-1)/2",
        },
        "pole_budget_compiler": {
            "rules": {
                "constant": 0,
                "negation": "B(-f)=B(f)",
                "addition": "B(f+g)<=B(f)+B(g)",
                "multiplication": "B(fg)<=B(f)+B(g)",
                "inversion": "B(1/f)=B(f) for nonzero f",
                "power": "B(f^m)=m*B(f)",
            },
            "rational_function_controls": budget_controls,
            "ab_decoder_compilation": ab_equal,
        },
        "ab_state_boundary": {
            "decoder": (
                "(2A^2+2AxB-x^2B^2)/(2yA), with B(x)=2 and B(y)=3"
            ),
            "compiled_pole_upper_bound": "4*a+3*b+9",
            "equal_coordinate_bound": "7*delta+9",
            "secp256k1_minimum_coordinate_pole_budget": SECP_AB_STATE_POLE_LOWER,
            "minimum_coordinate_pole_budget_bits": SECP_AB_STATE_POLE_LOWER.bit_length(),
            "predecessor_budget": predecessor_budget,
            "minimum_budget": current_budget,
            "polynomial_in_T_rule": (
                "T=x^3 has pole degree 6; if deg A,deg B<=d, decoder budget<=42d+9"
            ),
            "secp256k1_minimum_common_polynomial_degree": SECP_AB_POLY_DEGREE_LOWER,
            "minimum_common_polynomial_degree_bits": SECP_AB_POLY_DEGREE_LOWER.bit_length(),
            "polynomial_predecessor_budget": poly_predecessor,
            "polynomial_minimum_budget": poly_current,
        },
        "straight_line_program_boundary": {
            "general_bound": (
                "with total initial pole budget B0 and s binary arithmetic "
                "gates, the degree-only compiler gives output budget<=2^s*B0"
            ),
            "minimum_gate_counts_for_secp_half": leaf_gate_bounds,
            "interpretation": (
                "degree/pole arguments force only logarithmically many gates; "
                "they do not exclude a high-degree low-size nonlinear recurrence"
            ),
        },
        "finite_controls": {
            "cases": controls,
            "all_square_residual_zero_counts_passed": True,
            "all_translation_defect_counts_passed": True,
        },
        "closed_classes": [
            "ordinary rational parity functions with pole degree below (n-1)/2",
            "bounded-pole rational states whose declared decoder compiles below the half-order budget",
            "A/B CM state with both coordinate pole budgets below the exact C28 threshold",
            "polynomial-in-T A/B states below the exact common-degree threshold",
        ],
        "not_closed": [
            "high-degree low-size arithmetic circuits",
            "implicit modular composition",
            "nonrational algebraic correspondences without a declared pole budget",
            "theta, p-adic, elliptic-unit, or Hilbert-90 branch-sensitive states",
            "unrestricted arithmetic circuits",
        ],
        "decision": {
            "pole_budget_tool_built": True,
            "translation_defect_bound_proved": True,
            "low_degree_algebraic_state_blocked": True,
            "joint_A_B_recurrence_found": False,
            "modular_composition_state_found": False,
            "high_degree_low_size_state_blocked": False,
            "bounded_dimensional_nonlinear_state_found": False,
            "public_branch_sensitive_seed_found": False,
            "all_point_public_Q_replay_passed": False,
            "exact_parity_extraction_found": False,
            "exact_Hilbert90_branch_bridge_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": (
            "HIGH-DEGREE-LOW-SIZE-BRANCH-STATE-078: search or bound a uniform "
            "nonlocal nonlinear recurrence whose pole degree grows exponentially "
            "while its branch-sensitive public seed and full circuit remain compact"
        ),
    }
    payload["digest"] = digest_without_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(build_result())
    if args.check:
        if not args.out.exists():
            raise SystemExit(f"missing frozen C28 result: {args.out}")
        if args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("C28 nonlinear pole-budget artifact drift")
        print("UORC056_NONLINEAR_POLE_BUDGET_C28_OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
