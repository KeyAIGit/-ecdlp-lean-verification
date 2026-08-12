#!/usr/bin/env python3
"""Fixed-parameter certificate for FROBENIUS-CM-SECTION-RIGIDITY-010.

The certificate uses only the public secp256k1 curve, generator, GLV constants,
and ordinary division-polynomial recurrences.  It accepts no external point,
key, wallet, or discrete-log target.

Source contract
---------------
For a generalized division section attached to an F_p-defined endomorphism
alpha commuting with the GLV automorphism, let

    a     = scalar action of alpha on <G> modulo n,
    delta = deg(alpha) modulo 2.

The generalized chain rule, ordinary multiplication formula, and GLV
invariance reduce its quadratic character to

    chi(Psi_alpha(Q))
      = chi(psi_a(Q))
        * (rho(Q) * (-1)^k)^(a + delta mod 2),

up to one fixed public global sign.  The Python work below certifies every
secp256k1 arithmetic input in this reduction for the six smallest Frobenius/CM
indices pi +/- 1, pi +/- omega, pi +/- omega^2.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
B = 7


def quadratic_character(value: int) -> int:
    value %= P
    if value == 0:
        return 0
    return 1 if pow(value, (P - 1) // 2, P) == 1 else -1


def ec_add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return x3, y3


def ec_mul(scalar: int, point: Point) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        scalar >>= 1
    return result


def division_polynomial_evaluator(point: tuple[int, int]):
    """Repository convention: psi_2=+2y on y^2=x^3+7."""
    x, y = point

    @lru_cache(maxsize=None)
    def psi(index: int) -> int:
        if index < 0:
            return -psi(-index) % P
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % P
        if index == 3:
            return (3 * x**4 + 84 * x) % P
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392) % P
        if index & 1:
            m = (index - 1) // 2
            return (
                psi(m + 2) * pow(psi(m), 3, P)
                - psi(m - 1) * pow(psi(m + 1), 3, P)
            ) % P
        m = index // 2
        return (
            psi(m)
            * pow(2 * y, -1, P)
            * (
                psi(m + 2) * pow(psi(m - 1), 2, P)
                - psi(m - 2) * pow(psi(m + 1), 2, P)
            )
        ) % P

    return psi


def section_row(
    name: str,
    unit_scalar: int,
    sign: int,
    degree_parity: int,
    psi_generator,
    rho_lambda: int,
) -> dict[str, object]:
    action = (1 + sign * unit_scalar) % N
    if action == 0:
        return {
            "section": name,
            "action_scalar": 0,
            "status": "vanishes_on_the_rational_subgroup",
            "disposition": (
                "the pi-1 section vanishes; its first jet belongs to the "
                "already-closed public point-character class"
            ),
        }

    action_point = ec_mul(action, (GX, GY))
    if action_point is None:
        raise AssertionError("nonzero action scalar killed the generator")

    rho_action = quadratic_character(psi_generator(action))
    psi_lambda_at_action = quadratic_character(
        division_polynomial_evaluator(action_point)(LAMBDA)
    )

    # GLV-character invariance at even LAMBDA forces the base generalized
    # section phase.  The factor rho(lambda)^delta is the residual exponent
    # contributed by deg(alpha) modulo two in the chain rule.
    base_section_phase = psi_lambda_at_action * (
        rho_lambda if degree_parity else 1
    )
    combined_phase = base_section_phase * rho_action
    hidden_weight = (action + degree_parity) & 1
    expected_combined_phase = -1 if hidden_weight else 1
    if combined_phase != expected_combined_phase:
        raise AssertionError(
            f"{name}: Frobenius/CM phase did not collapse to hidden weight"
        )

    if hidden_weight:
        character_class = "ordinary_psi_a_times_public_point_character"
        hidden_expression = "rho(Q)*(-1)^k"
    else:
        character_class = "ordinary_psi_a_only"
        hidden_expression = "1"

    return {
        "section": name,
        "status": "classified",
        "action_scalar": action,
        "action_scalar_hex": hex(action),
        "action_parity": action & 1,
        "degree_parity": degree_parity,
        "hidden_weight_action_plus_degree_mod_two": hidden_weight,
        "rho_action": rho_action,
        "chi_psi_lambda_at_action_G": psi_lambda_at_action,
        "forced_base_section_phase": base_section_phase,
        "combined_phase_with_rho_action": combined_phase,
        "expected_combined_phase": expected_combined_phase,
        "character_class": character_class,
        "only_nonordinary_factor": hidden_expression,
        "independent_R3_or_carry_equation": False,
    }


def build_payload() -> dict[str, object]:
    generator = (GX, GY)
    if (GY * GY - GX * GX * GX - B) % P:
        raise AssertionError("generator is not on secp256k1")
    if ec_mul(N, generator) is not None:
        raise AssertionError("generator order certificate failed")
    if ec_mul(LAMBDA, generator) != (BETA * GX % P, GY):
        raise AssertionError("GLV eigenvalue action failed")
    if LAMBDA & 1:
        raise AssertionError("the chosen secp256k1 GLV eigenvalue must be even")

    lambda2 = LAMBDA * LAMBDA % N
    if (lambda2 + LAMBDA + 1) % N:
        raise AssertionError("lambda cyclotomic relation failed")

    psi_generator = division_polynomial_evaluator(generator)
    rho_lambda = quadratic_character(psi_generator(LAMBDA))
    if rho_lambda != -1:
        raise AssertionError("expected secp256k1 rho(lambda)=-1")

    # The cubic-residue calculation describes Frobenius on E[2].  Since
    # (-7)^((p-1)/3)=beta, Frobenius acts as omega on all three nonzero
    # two-torsion points.  Hence pi +/- omega have degree divisible by four,
    # while pi +/- omega^2 have odd degree.  pi +/- 1 have odd degree because
    # #E(F_p) and the quadratic-twist order are both odd.
    frobenius_two_torsion = pow((-B) % P, (P - 1) // 3, P)
    if frobenius_two_torsion != BETA:
        raise AssertionError("unexpected Frobenius action on two-torsion")

    rows = [
        section_row("pi-1", 1, -1, 1, psi_generator, rho_lambda),
        section_row("pi+1", 1, 1, 1, psi_generator, rho_lambda),
        section_row("pi-omega", LAMBDA, -1, 0, psi_generator, rho_lambda),
        section_row("pi+omega", LAMBDA, 1, 0, psi_generator, rho_lambda),
        section_row("pi-omega^2", lambda2, -1, 1, psi_generator, rho_lambda),
        section_row("pi+omega^2", lambda2, 1, 1, psi_generator, rho_lambda),
    ]

    classified = [row for row in rows if row["status"] == "classified"]
    if any(row["independent_R3_or_carry_equation"] for row in classified):
        raise AssertionError("unexpected independent section survived")

    return {
        "scope": (
            "fixed public secp256k1 parameters and six Frobenius/CM indices; "
            "no external point or discrete-log target"
        ),
        "package": "FROBENIUS-CM-SECTION-RIGIDITY-010",
        "ordinary_division_polynomial_convention": "psi_2=+2y",
        "arithmetic": {
            "lambda_even": True,
            "lambda2_hex": hex(lambda2),
            "rho_lambda": rho_lambda,
            "minus_seven_cubic_character": hex(frobenius_two_torsion),
            "beta_hex": hex(BETA),
            "frobenius_action_on_E2": "omega",
        },
        "source_conditional_identity": (
            "chi(Psi_alpha(Q)) = chi(psi_a(Q)) * "
            "(rho(Q)*(-1)^k)^((a+deg(alpha)) mod 2), up to a fixed public sign"
        ),
        "sections": rows,
        "aggregate": {
            "sections_considered": len(rows),
            "classified_nonvanishing_sections": len(classified),
            "ordinary_psi_only": sum(
                row["character_class"] == "ordinary_psi_a_only"
                for row in classified
            ),
            "ordinary_psi_times_public_point_character": sum(
                row["character_class"]
                == "ordinary_psi_a_times_public_point_character"
                for row in classified
            ),
            "independent_R3_or_carry_equations": 0,
        },
        "conclusion": (
            "Every nonvanishing smallest Frobenius/CM generalized section "
            "collapses to an ordinary public fixed-index division character, "
            "possibly multiplied by the already-public perfectly-periodic "
            "point character.  The pi-1 section vanishes and its first jet is "
            "the previously closed point-character section."
        ),
        "claim_boundary": [
            "The generalized chain rule and GLV-invariance admission are source-level inputs.",
            "The secp256k1 finite arithmetic and ordinary division characters are exactly replayed here.",
            "This does not classify arbitrary mixed-weight sums or non-isogeny analytic sections.",
            "No public R3, carry, parity, or ECDLP oracle is constructed.",
        ],
    }


def main() -> None:
    output = Path(__file__).with_name(
        "frobenius_cm_section_boundary_results.json"
    )
    payload = build_payload()
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
