#!/usr/bin/env python3
"""Exact C3/GLV decomposition of the UORC-056 oriented root.

For the j=0 frozen toys, the half-kernel polynomial is K_H(X)=kappa(X^3).
Every oriented root therefore decomposes uniquely as

    Y(X)=A(T)+X*B(T)+X^2*C(T),  T=X^3.

This replay verifies the quotient-ring equations, the four-branch selector
polynomial, exact C3 projectors on every marked root, identification of the
three-sign orbit product with the already-known GLV carry, and a direct
field-valued reconstruction formula for canonical parity.

No external point/scalar is accepted and no production-sized DLP is attempted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from uorc056_toy_factory import (
    DEFAULT_INSTANCES,
    build_fixture,
    poly_add,
    poly_eval,
    poly_mod,
    poly_mul,
    poly_scale,
    poly_sub,
)

PROFILE_ID = "UORC-056-CM-THREEFOLD-ROOT-DECOMPOSITION-V14"
DEFAULT_OUTPUT = Path("experiments/uorc056/cm_threefold_root_decomposition_results.json")


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def trim(poly: Sequence[int], p: int) -> list[int]:
    out = [int(c) % p for c in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def decompose_mod_three(poly: Sequence[int], p: int) -> tuple[list[int], list[int], list[int]]:
    pieces = []
    for residue in range(3):
        pieces.append(trim([poly[i] for i in range(residue, len(poly), 3)], p))
    return pieces[0], pieces[1], pieces[2]


def extract_kappa(kernel: Sequence[int], p: int) -> list[int]:
    for degree, coefficient in enumerate(kernel):
        if degree % 3 and coefficient % p:
            raise AssertionError("kernel is not in F_p[X^3]")
    return trim([kernel[i] for i in range(0, len(kernel), 3)], p)


def cube(poly: Sequence[int], p: int) -> list[int]:
    return poly_mul(poly_mul(poly, poly, p), poly, p)


def quotient_equations(
    A: Sequence[int], B: Sequence[int], C: Sequence[int], kappa: Sequence[int], p: int
) -> dict[str, bool]:
    T = [0, 1]
    F = [7, 1]
    eq0 = poly_mod(
        poly_sub(
            poly_add(poly_mul(A, A, p), poly_scale(poly_mul(poly_mul(T, B, p), C, p), 2, p), p),
            F,
            p,
        ),
        kappa,
        p,
    )
    eq1 = poly_mod(
        poly_add(poly_scale(poly_mul(A, B, p), 2, p), poly_mul(T, poly_mul(C, C, p), p), p),
        kappa,
        p,
    )
    eq2 = poly_mod(
        poly_add(poly_mul(B, B, p), poly_scale(poly_mul(A, C, p), 2, p), p),
        kappa,
        p,
    )

    # Denominator-free form of r*(T*r^3+8)=0 for r=B/A.
    quartic = poly_mod(
        poly_mul(
            B,
            poly_add(poly_mul(T, cube(B, p), p), poly_scale(cube(A, p), 8, p), p),
            p,
        ),
        kappa,
        p,
    )

    A2 = poly_mul(A, A, p)
    # A/y is always one of +/-1, +/-1/3 on the C3 orbits.
    majority_scale = poly_mod(
        poly_mul(
            poly_sub(A2, F, p),
            poly_sub(poly_scale(A2, 9, p), F, p),
            p,
        ),
        kappa,
        p,
    )

    return {
        "weight0_square_equation": eq0 == [0],
        "weight1_square_equation": eq1 == [0],
        "weight2_square_equation": eq2 == [0],
        "denominator_free_selector_quartic": quartic == [0],
        "A_four_value_equation": majority_scale == [0],
    }


def sign_to_field(sign: int, p: int) -> int:
    return 1 if sign == 1 else p - 1


def point_sign(k: int) -> int:
    return -1 if k & 1 else 1


def marker_record(instance, marker: int, fixture: dict, kappa: Sequence[int]) -> dict[str, Any]:
    p = instance.curve.p
    n = instance.subgroup_order
    beta = int(instance.cm_beta)
    lam = int(instance.glv_lambda)
    root = fixture["marked_roots"][str(marker)]["coefficients_low_to_high"]
    A, B, C = decompose_mod_three(root, p)
    equations = quotient_equations(A, B, C, kappa, p)
    if not all(equations.values()):
        raise AssertionError(f"quotient equation failed for marker {marker}")

    marked_generator = instance.curve.mul(marker, instance.generator)
    if marked_generator is None:
        raise AssertionError("marked generator became infinity")

    branch_counts = {"uniform": 0, "minority_0": 0, "minority_1": 0, "minority_2": 0}
    gamma_counts = {"1": 0, "2": 0}
    scalar_checks = 0
    for k in range(1, n):
        Q = instance.curve.mul(k, marked_generator)
        if Q is None:
            raise AssertionError("nonzero marked multiple became infinity")
        x, y = Q
        t = pow(x, 3, p)
        s0 = point_sign(k)
        k1 = lam * k % n
        k2 = lam * k1 % n
        s1 = point_sign(k1)
        s2 = point_sign(k2)
        signs = (s0, s1, s2)

        # The three evaluations are the exact C3 transform of A,xB,x^2C.
        for j, sj in enumerate(signs):
            xj = pow(beta, j, p) * x % p
            ratio = poly_eval(root, xj, p) * pow(y, -1, p) % p
            if ratio != sign_to_field(sj, p):
                raise AssertionError("C3 root evaluation disagrees with parity")

        Aval = poly_eval(A, t, p)
        Bval = poly_eval(B, t, p)
        Cval = poly_eval(C, t, p)
        if Aval == 0:
            raise AssertionError("A vanished on a subgroup C3 orbit")
        inv_y = pow(y, -1, p)
        if 3 * Aval * inv_y % p != (s0 + s1 + s2) % p:
            raise AssertionError("A projector failed")
        if 3 * x * Bval * inv_y % p != (s0 + beta * beta * s1 + beta * s2) % p:
            raise AssertionError("B projector failed")
        if 3 * x * x * Cval * inv_y % p != (s0 + beta * s1 + beta * beta * s2) % p:
            raise AssertionError("C projector failed")

        u = x * Bval * pow(Aval, -1, p) % p
        if s0 == s1 == s2:
            branch_counts["uniform"] += 1
            if u != 0:
                raise AssertionError("uniform orbit must have u=0")
            minority = None
        else:
            if s1 == s2:
                minority = 0
            elif s0 == s2:
                minority = 1
            else:
                minority = 2
            branch_counts[f"minority_{minority}"] += 1
            expected_u = -2 * pow(beta, (-minority) % 3, p) % p
            if u != expected_u:
                raise AssertionError("minority sector selector failed")
            if pow(u, 3, p) != (-8) % p:
                raise AssertionError("mixed selector must satisfy u^3=-8")

        # Direct field-valued reconstruction from A and B only.
        numerator = (2 * Aval * Aval + 2 * Aval * x * Bval - x * x * Bval * Bval) % p
        denominator = 2 * y * Aval % p
        reconstructed = numerator * pow(denominator, -1, p) % p
        if reconstructed != sign_to_field(s0, p):
            raise AssertionError("A,B field-valued parity reconstruction failed")

        # The C3 sign product is the already-known GLV carry, not a new observable.
        scalar_sum = k + k1 + k2
        if scalar_sum % n:
            raise AssertionError("GLV orbit representatives did not sum to a multiple of n")
        gamma = scalar_sum // n
        if gamma not in (1, 2):
            raise AssertionError("unexpected GLV carry digit")
        gamma_counts[str(gamma)] += 1
        orbit_product = s0 * s1 * s2
        expected_carry = -1 if gamma & 1 else 1
        if orbit_product != expected_carry:
            raise AssertionError("C3 sign product != existing GLV carry")
        scalar_checks += 1

    return {
        "marker": marker,
        "degrees": {"A": len(A) - 1, "B": len(B) - 1, "C": len(C) - 1},
        "quotient_equations": equations,
        "scalar_checks": scalar_checks,
        "branch_counts": branch_counts,
        "gamma_counts": gamma_counts,
    }


def run() -> dict[str, Any]:
    total_roots = 0
    total_scalar_checks = 0
    aggregate_branches = {"uniform": 0, "minority_0": 0, "minority_1": 0, "minority_2": 0}
    aggregate_gamma = {"1": 0, "2": 0}
    curve_rows = []

    for instance in DEFAULT_INSTANCES:
        p = instance.curve.p
        n = instance.subgroup_order
        if n % 6 != 1:
            raise AssertionError("V14 frozen instance needs n=1 mod 6")
        fixture = build_fixture(instance, include_all_markers=True)
        kernel = fixture["kernel_coefficients_low_to_high"]
        kappa = extract_kappa(kernel, p)
        if len(kappa) - 1 != (n - 1) // 6:
            raise AssertionError("kappa degree is not (n-1)/6")

        max_degrees = {"A": -1, "B": -1, "C": -1}
        min_degrees = {"A": 10**9, "B": 10**9, "C": 10**9}
        curve_branches = {key: 0 for key in aggregate_branches}
        curve_gamma = {"1": 0, "2": 0}
        for marker in range(1, n):
            row = marker_record(instance, marker, fixture, kappa)
            total_roots += 1
            total_scalar_checks += row["scalar_checks"]
            for key in max_degrees:
                max_degrees[key] = max(max_degrees[key], row["degrees"][key])
                min_degrees[key] = min(min_degrees[key], row["degrees"][key])
            for key, value in row["branch_counts"].items():
                curve_branches[key] += value
                aggregate_branches[key] += value
            for key, value in row["gamma_counts"].items():
                curve_gamma[key] += value
                aggregate_gamma[key] += value

        curve_rows.append(
            {
                "id": instance.instance_id,
                "p": p,
                "n": n,
                "kernel_degree": (n - 1) // 2,
                "kappa_degree": len(kappa) - 1,
                "marked_roots": n - 1,
                "min_component_degrees": min_degrees,
                "max_component_degrees": max_degrees,
                "branch_counts": curve_branches,
                "gamma_counts": curve_gamma,
            }
        )

    if total_roots != 438:
        raise AssertionError("marked-root total drifted")
    if sum(aggregate_branches.values()) != total_scalar_checks:
        raise AssertionError("branch partition did not cover all scalar checks")

    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "exact_algebra": {
            "kernel": "K_H(X)=kappa(X^3)",
            "root_decomposition": "Y_G(X)=A(X^3)+X*B(X^3)+X^2*C(X^3)",
            "quotient_equations": [
                "A^2+2*T*B*C=T+7",
                "2*A*B+T*C^2=0",
                "B^2+2*A*C=0",
            ],
            "A_four_value_equation": "(A^2-F)*(9*A^2-F)=0 mod kappa, F=T+7",
            "selector_equation": "B*(T*B^3+8*A^3)=0 mod kappa",
            "selector_ratio": "r=B/A; r*(T*r^3+8)=0 on every kappa root",
            "sector_variable": "u=x*B/A is 0 or one of {-2,-2*beta,-2*beta^2}",
            "direct_parity_reconstruction": (
                "sigma(Q)=(2*A^2+2*A*x*B-x^2*B^2)/(2*y*A), T=x^3"
            ),
        },
        "interpretation": {
            "A_over_y": "GLV-orbit majority sign scaled by 1 or 1/3",
            "u_zero": "all three canonical parity signs on the GLV orbit agree",
            "u_nonzero": "the cube-root sector identifies which of Q,alpha(Q),alpha^2(Q) is the unique minority sign",
            "orbit_product": (
                "sigma(Q)*sigma(alpha Q)*sigma(alpha^2 Q)=(-1)^gamma is the already-known GLV carry; it is not a new observable"
            ),
            "dense_representation": (
                "C is determined from A,B by B^2+2*A*C=0 because A is nonzero on every subgroup orbit, "
                "but dense A,B construction still has linear-in-n coefficient cost"
            ),
        },
        "exact_replay": {
            "curves": len(DEFAULT_INSTANCES),
            "marked_roots": total_roots,
            "scalar_evaluations": total_scalar_checks,
            "branch_counts": aggregate_branches,
            "gamma_counts": aggregate_gamma,
            "curve_rows": curve_rows,
        },
        "decision": "central_oriented_root_has_exact_threefold_CM_branch_decomposition_but_short_branch_evaluator_remains_open",
        "next_frontier": [
            "seek a compact evaluator for the invariant A(T) majority/carry component",
            "seek a compact evaluator for the four-branch selector r(T)=B(T)/A(T)",
            "test whether r is a rational function of existing public CM/Miller states before introducing any new observable",
            "exploit C=-B^2/(2A) to search only two independent CM-weight components",
            "keep all representation and branch-selection costs charged",
        ],
        "scientific_boundary": (
            "V14 is an exact normal form and a one-third dense representation reduction, not a sub-square-root evaluator."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V14 C3 decomposition artifact drift")
        print("UORC056_CM_THREEFOLD_ROOT_DECOMPOSITION_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
