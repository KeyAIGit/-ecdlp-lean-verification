#!/usr/bin/env python3
"""Verify that the canonical Eisenstein cube-root lift is an inverse 3-isogeny.

This bounded script reuses the frozen toy cases and arithmetic from
`eisenstein_root_phase_screen.py`. It accepts no external input except an
output path and does not target secp256k1.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from eisenstein_root_phase_screen import (
    B,
    FROZEN_CASES,
    Fp2,
    canonical_cube_root_y_minus_c,
    ec_mul,
    orbit,
)


def source_to_target(point: tuple[int, int], p: int) -> tuple[int, int]:
    """Dual 3-isogeny E_b -> E_{-27b}."""
    x, y = point
    x3 = x**3 % p
    return (
        (x3 + 4 * B) * pow(x * x % p, -1, p) % p,
        y * (x3 - 8 * B) * pow(x3, -1, p) % p,
    )


def target_to_source(point: tuple[int, int], p: int) -> tuple[int, int]:
    """Normalized dual map E_{-27b} -> E_b; composition is -[3]."""
    X, Y = point
    X3 = X**3 % p
    return (
        (X3 - 108 * B) * pow(9 * X * X % p, -1, p) % p,
        -Y * (X3 + 216 * B) * pow(27 * X3 % p, -1, p) % p,
    )


def corrected_root_lift(
    point: tuple[int, int], p: int
) -> tuple[tuple[int, int], int]:
    """Return the canonical rational inverse-isogeny point and its GLV phase."""
    x, y = point
    root = canonical_cube_root_y_minus_c(y, p)
    conjugate = root.frobenius()
    norm = root * conjugate
    if norm.b % p:
        raise AssertionError("root norm left the base field")
    delta = norm.a * pow(x, -1, p) % p
    if pow(delta, 3, p) != 1:
        raise AssertionError("root norm phase is not in mu_3")

    corrected = Fp2(delta * root.a, delta * root.b, p)
    corrected_conjugate = corrected.frobenius()
    corrected_norm = corrected * corrected_conjugate
    if corrected_norm != Fp2(x, 0, p):
        raise AssertionError("corrected root norm is not x")

    s = (corrected.a + corrected_conjugate.a) % p
    d = 2 * corrected.b % p
    if (B * d**3 + 3 * s * s * d + 8) % p:
        raise AssertionError("descended cubic-cover equation failed")
    if d == 0:
        raise AssertionError("unexpected zero anti-trace")

    X = -6 * pow(d, -1, p) % p
    Y = 9 * s * pow(d, -1, p) % p
    if (Y * Y - X**3 + 27 * B) % p:
        raise AssertionError("lifted point is off E_{-27b}")
    return (X, Y), delta


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    base_generator: tuple[int, int]
    nonzero_points: int
    root_phase_checks: int
    cover_equation_checks: int
    target_curve_checks: int
    forward_map_checks: int
    inverse_isogeny_checks: int
    composition_checks: int
    distinct_mu3_phases: int


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    inverse_three = pow(3, -1, order)
    phases: set[int] = set()
    count = 0

    for point in points[1:]:
        if point is None:
            raise AssertionError("unexpected identity")
        lifted, delta = corrected_root_lift(point, p)
        phases.add(delta)

        if target_to_source(lifted, p) != point:
            raise AssertionError("cover map does not recover the source point")

        dual_value = source_to_target(point, p)
        inverse_value = ec_mul((-inverse_three) % order, dual_value, p)
        if inverse_value != lifted:
            raise AssertionError("root lift differs from public inverse isogeny")

        composed = target_to_source(dual_value, p)
        minus_triple = ec_mul(order - 3, point, p)
        if composed != minus_triple:
            raise AssertionError("dual composition is not -[3]")
        count += 1

    return CaseResult(
        p=p,
        order=order,
        base_generator=generator,
        nonzero_points=count,
        root_phase_checks=count,
        cover_equation_checks=count,
        target_curve_checks=count,
        forward_map_checks=count,
        inverse_isogeny_checks=count,
        composition_checks=count,
        distinct_mu3_phases=len(phases),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("eisenstein_cover_isogeny_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "scope": "fifteen frozen j=0 toy subgroups only; no secp256k1 target",
        "cover": "u^3=y-c with c^2=7",
        "descent": "s=u+u^p, d=(u-u^p)/c, then X=-6/d, Y=9s/d",
        "target_curve": "E': Y^2=X^3-27*7",
        "isogenies": {
            "dual": "E_b -> E_-27b: ((x^3+4b)/x^2, y(x^3-8b)/x^3)",
            "forward": "E_-27b -> E_b: ((X^3-108b)/(9X^2), -Y(X^3+216b)/(27X^3))",
            "composition": "forward o dual = -[3]",
            "subgroup_inverse": "root lift = [-3^(-1) mod r] * dual(Q)",
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "total_nonzero_points": sum(case.nonzero_points for case in cases),
            "all_checks_passed": True,
        },
        "conclusion": (
            "After the public mu_3 norm correction, the canonical cube-root "
            "lift is exactly the rational inverse of a degree-three isogeny on "
            "every frozen subgroup. It is a structured reparameterization, not "
            "an independent hidden-bit source."
        ),
        "claim_boundary": [
            "Bounded exact replay of explicit identities, not a universal ECDLP lower bound.",
            "No external point, wallet, key, or production target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
