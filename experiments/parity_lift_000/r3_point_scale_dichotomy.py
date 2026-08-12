#!/usr/bin/env python3
"""Exact frozen triage for R3-POINT-SCALE-DICHOTOMY-018.

The normalization-aware public point-function character is

    C(k) = s^k * rho(k),

where rho(k)=chi(psi_k(G)) and s in {+1,-1} is public.  For canonical GLV
representatives k0,k1,k2 with k0+k1+k2=gamma*n and odd n,

    C(k0) C(k1) C(k2) = s^gamma * R3(k),
    R3(k) = rho(k0) rho(k1) rho(k2).

Therefore:
  * s=+1: R3 is already the public C3 orbit norm;
  * s=-1: R3 equals carry_sign times the public C3 orbit norm.

The script recomputes this identity on every nonzero scalar of the frozen toy
family and classifies the exact R3 matches reported by
TRACE-CM-INDEX-SECTIONS-015. It accepts no external curve, point, key, wallet,
or production-sized target.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)


def sign_power(sign: int, exponent: int) -> int:
    if sign not in (-1, 1):
        raise AssertionError("non-binary sign")
    return sign if exponent & 1 else 1


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    lam: int
    lam_squared: int
    point_scale_character: int
    rho_kummer_invariant: bool
    identity_checks: int
    public_tautology_checks: int
    carry_equivalence_checks: int
    trace_exact_r3_decoder: str | None
    trace_exact_r3_classification: str
    exact_decoder_expected_from_scale: bool


def run_case(
    frozen: tuple[int, int, tuple[int, int]],
    trace_case: dict,
) -> CaseResult:
    p, order, generator = frozen
    if int(trace_case["p"]) != p or int(trace_case["order"]) != order:
        raise AssertionError("trace result did not align with frozen case")

    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam_squared = lam * lam % order
    if int(trace_case["lam"]) != lam:
        raise AssertionError("trace result used a different GLV eigenvalue")

    psi_g = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi_g(k), p) for k in range(1, order)]
    if any(value not in (-1, 1) for value in rho[1:]):
        raise AssertionError("EDS residue vanished off the identity")

    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order - 1] * rho[1] * chi_minus_one
    if point_scale not in (-1, 1):
        raise AssertionError("point-scale character was not binary")
    if int(trace_case["point_scale_character"]) != point_scale:
        raise AssertionError("trace point-scale character disagreed")

    public_character = [0] + [
        sign_power(point_scale, k) * rho[k]
        for k in range(1, order)
    ]
    rho_kummer = all(rho[order - k] == rho[k] for k in range(1, order))
    if bool(trace_case["rho_kummer_invariant"]) != rho_kummer:
        raise AssertionError("trace Kummer flag disagreed")

    identity_checks = 0
    public_checks = 0
    carry_checks = 0
    for k in range(1, order):
        k1 = lam * k % order
        k2 = lam_squared * k % order
        total = k + k1 + k2
        if total not in (order, 2 * order):
            raise AssertionError("canonical GLV representatives lost their carry")
        gamma = total // order
        carry_sign = -1 if gamma == 1 else 1
        if carry_sign != sign_power(-1, gamma):
            raise AssertionError("carry sign convention failed")

        r3 = rho[k] * rho[k1] * rho[k2]
        public_norm = (
            public_character[k]
            * public_character[k1]
            * public_character[k2]
        )
        expected_public_norm = sign_power(point_scale, gamma) * r3
        if public_norm != expected_public_norm:
            raise AssertionError("point-scale R3 identity failed")
        identity_checks += 1

        if point_scale == 1:
            if r3 != public_norm:
                raise AssertionError("s=+1 R3 was not already public")
            public_checks += 1
        else:
            if r3 != carry_sign * public_norm:
                raise AssertionError("s=-1 R3 was not carry-equivalent")
            carry_checks += 1

    exact_decoder = trace_case["exact_r3_decoder"]
    if exact_decoder is None:
        classification = "none"
    elif point_scale == 1:
        classification = "public_tautology"
    else:
        classification = "carry_equivalent_nontrivial"

    expected_exact = point_scale == 1
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        lam=lam,
        lam_squared=lam_squared,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        identity_checks=identity_checks,
        public_tautology_checks=public_checks,
        carry_equivalence_checks=carry_checks,
        trace_exact_r3_decoder=exact_decoder,
        trace_exact_r3_classification=classification,
        exact_decoder_expected_from_scale=expected_exact,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-results", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "r3_point_scale_dichotomy_results.json"
        ),
    )
    args = parser.parse_args()

    trace_data = json.loads(args.trace_results.read_text())
    trace_cases = trace_data["cases"]
    if len(trace_cases) != len(FROZEN_CASES):
        raise AssertionError("trace result case count changed")
    cases = [
        run_case(frozen, trace_case)
        for frozen, trace_case in zip(FROZEN_CASES, trace_cases)
    ]

    exact_cases = [case for case in cases if case.trace_exact_r3_decoder is not None]
    plus_cases = [case for case in cases if case.point_scale_character == 1]
    minus_cases = [case for case in cases if case.point_scale_character == -1]
    unexplained = [
        case for case in exact_cases
        if case.trace_exact_r3_classification not in (
            "public_tautology",
            "carry_equivalent_nontrivial",
        )
    ]
    carry_breakthroughs = [
        case for case in exact_cases
        if case.trace_exact_r3_classification == "carry_equivalent_nontrivial"
    ]

    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; no external point, "
            "key, wallet, or production-sized target"
        ),
        "package": "R3-POINT-SCALE-DICHOTOMY-018",
        "public_character": "C(k)=s^k*rho(k)",
        "exact_identity": (
            "C(k)C(lambda*k)C(lambda^2*k)=s^gamma*R3(k), "
            "where canonical representatives sum to gamma*n"
        ),
        "dichotomy": {
            "s=+1": "R3 is the already-public C3 orbit norm",
            "s=-1": "R3 is carry_sign times the public C3 orbit norm",
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "point_scale_plus_one_cases": len(plus_cases),
            "point_scale_minus_one_cases": len(minus_cases),
            "identity_checks": sum(case.identity_checks for case in cases),
            "public_tautology_checks": sum(
                case.public_tautology_checks for case in cases
            ),
            "carry_equivalence_checks": sum(
                case.carry_equivalence_checks for case in cases
            ),
            "trace_exact_r3_matches": len(exact_cases),
            "trace_exact_r3_public_tautologies": sum(
                case.trace_exact_r3_classification == "public_tautology"
                for case in exact_cases
            ),
            "trace_exact_r3_carry_equivalent_breakthroughs": len(carry_breakthroughs),
            "trace_exact_r3_unexplained": len(unexplained),
            "exact_match_orders": [case.order for case in exact_cases],
            "exact_matches_iff_point_scale_plus_one": (
                {case.order for case in exact_cases}
                == {case.order for case in plus_cases}
            ),
            "all_point_scale_minus_one_cases_have_no_exact_r3_match": all(
                case.trace_exact_r3_decoder is None for case in minus_cases
            ),
        },
        "corrected_decision": (
            "All seven exact R3 matches from TRACE-CM-INDEX-SECTIONS-015 occur "
            "in s=+1 cases, where R3 is already the public C3 orbit norm. No "
            "s=-1 carry-equivalent exact R3 decoder was found."
        ),
        "gate_rule": (
            "An exact R3 match is research-positive only when s=-1, because only "
            "then it supplies the missing carry sign after division by the public norm."
        ),
        "claim_boundary": [
            "The point-scale orbit identity is exact and checked for every nonzero frozen scalar.",
            "The classification corrects the automated interpretation of package 015; it does not invalidate its raw finite matches.",
            "No public carry, parity, EDS-residue, or ECDLP oracle is constructed.",
            "No statement is made about arbitrary order-dependent sections outside the tested family.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
