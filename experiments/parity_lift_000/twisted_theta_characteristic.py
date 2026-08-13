#!/usr/bin/env python3
"""Exact replay for TWISTED-THETA-CHARACTERISTIC-052.

On a genus-one curve, theta characteristics are two-torsion line bundles.  For
E_b: y^2=x^3+b, the nontrivial geometric characteristics are indexed by the
three points T_i=(r_i,0), where r_i^3+b=0.  Their characteristic functions
f_i(P)=x(P)-r_i satisfy

    product_i f_i(P) = x(P)^3+b = y(P)^2.

Thus the Frobenius-orbit norm of the three nontrivial characteristics is an
ordinary square and loses the signed branch required by the generator-oriented
root Y_G.

The script uses frozen toy subgroups and fixed public secp256k1 parameters only.
No external point, private key, wallet, or production-sized discrete-log target
is accepted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nonlocal_odd_anchor_screen import orbit, quadratic_character

B = 7
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (151, 19, (70, 122)),
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (1087, 271, (1017, 688)),
    (2851, 397, (2276, 1015)),
    (1663, 433, (126, 1375)),
)


def two_torsion_roots(field_prime: int) -> list[int]:
    return [
        x for x in range(field_prime) if (pow(x, 3, field_prime) + B) % field_prime == 0
    ]


def run_case(
    field_prime: int,
    order: int,
    generator: tuple[int, int],
) -> dict[str, object]:
    points = orbit(generator, order, field_prime)
    roots = two_torsion_roots(field_prime)
    if len(roots) not in (0, 3):
        raise AssertionError("two-torsion cubic had an unexpected splitting type")

    curve_checks = 0
    negation_invariance_checks = 0
    split_norm_checks = 0
    normalized_norm_checks = 0
    characteristic_checks = 0
    characteristic_matches = 0
    characteristic_mismatches = 0
    exact_characteristic_parity_decoders = 0

    x_generator, y_generator = generator
    generator_curve_value = (pow(x_generator, 3, field_prime) + B) % field_prime
    if generator_curve_value != pow(y_generator, 2, field_prime):
        raise AssertionError("generator is not on the curve")

    candidate_stats: list[dict[str, object]] = []
    for root in roots:
        denominator = (x_generator - root) % field_prime
        if denominator == 0:
            raise AssertionError("odd-order generator was a two-torsion point")
        matches = 0
        mismatches = 0
        for scalar in range(1, order):
            point = points[scalar]
            if point is None:
                raise AssertionError("nonzero scalar produced the identity")
            x_query, _ = point
            normalized = (
                (x_query - root) * pow(denominator, -1, field_prime)
            ) % field_prime
            sign = quadratic_character(normalized, field_prime)
            if sign == 0:
                raise AssertionError("characteristic function vanished on odd subgroup")
            parity = 1 if scalar % 2 == 0 else -1
            if sign == parity:
                matches += 1
            else:
                mismatches += 1
            characteristic_checks += 1
        if matches in (0, order - 1):
            exact_characteristic_parity_decoders += 1
        characteristic_matches += matches
        characteristic_mismatches += mismatches
        candidate_stats.append(
            {
                "root": root,
                "matches_parity": matches,
                "mismatches_parity": mismatches,
                "exact_up_to_global_sign": matches in (0, order - 1),
            }
        )

    for scalar in range(1, order):
        point = points[scalar]
        opposite = points[order - scalar]
        if point is None or opposite is None:
            raise AssertionError("nonzero point missing")
        x_query, y_query = point
        x_opposite, y_opposite = opposite
        if (pow(x_query, 3, field_prime) + B) % field_prime != pow(
            y_query, 2, field_prime
        ):
            raise AssertionError("curve equation failed")
        curve_checks += 1
        if x_query != x_opposite or (y_query + y_opposite) % field_prime != 0:
            raise AssertionError("point negation law failed")
        negation_invariance_checks += 1

        if roots:
            orbit_product = 1
            generator_product = 1
            for root in roots:
                orbit_product = orbit_product * (x_query - root) % field_prime
                generator_product = (
                    generator_product * (x_generator - root) % field_prime
                )
            if orbit_product != pow(y_query, 2, field_prime):
                raise AssertionError("characteristic orbit norm did not equal y^2")
            split_norm_checks += 1
            normalized_product = orbit_product * pow(
                generator_product, -1, field_prime
            ) % field_prime
            expected_ratio = pow(y_query, 2, field_prime) * pow(
                pow(y_generator, 2, field_prime), -1, field_prime
            ) % field_prime
            if normalized_product != expected_ratio:
                raise AssertionError("normalized characteristic norm failed")
            normalized_norm_checks += 1

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "nontrivial_rational_two_torsion_roots": roots,
        "base_field_theta_characteristics": 1 + len(roots),
        "nontrivial_characteristic_orbit_degree": 1 if roots else 3,
        "curve_checks": curve_checks,
        "negation_invariance_checks": negation_invariance_checks,
        "split_norm_checks": split_norm_checks,
        "normalized_norm_checks": normalized_norm_checks,
        "characteristic_checks": characteristic_checks,
        "characteristic_matches_parity": characteristic_matches,
        "characteristic_mismatches_parity": characteristic_mismatches,
        "exact_characteristic_parity_decoders": exact_characteristic_parity_decoders,
        "candidate_stats": candidate_stats,
        "orbit_norm": "product_i(x-r_i)=x^3+7=y^2",
        "normalized_orbit_norm": "product_i((x(Q)-r_i)/(x(G)-r_i))=y(Q)^2/y(G)^2",
        "standard_twist_selects_oriented_root": False,
    }


def secp256k1_certificate() -> dict[str, object]:
    if SECP_N % 2 != 1:
        raise AssertionError("secp256k1 order is not odd")
    if (SECP_P - 1) % 3 != 0:
        raise AssertionError("unexpected secp256k1 cube-root arithmetic")
    return {
        "p": SECP_P,
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "cofactor": 1,
        "group_order_is_odd": True,
        "nontrivial_rational_two_torsion": False,
        "base_field_theta_characteristics": 1,
        "geometric_theta_characteristics": 4,
        "nontrivial_characteristic_frobenius_orbit_degree": 3,
        "orbit_norm": "product_i(x-r_i)=x^3+7=y^2",
        "normalized_orbit_norm": "y(Q)^2/y(G)^2",
        "does_standard_twisted_characteristic_select_oriented_sqrt": False,
        "selected_successor": "METAPLECTIC-THETA-INTERTWINER-053",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("twisted_theta_characteristic_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "TWISTED-THETA-CHARACTERISTIC-052",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "split_two_torsion_cases": sum(
                bool(case["nontrivial_rational_two_torsion_roots"]) for case in cases
            ),
            "nonsplit_two_torsion_cases": sum(
                not bool(case["nontrivial_rational_two_torsion_roots"])
                for case in cases
            ),
            "total_curve_checks": sum(case["curve_checks"] for case in cases),
            "total_negation_invariance_checks": sum(
                case["negation_invariance_checks"] for case in cases
            ),
            "total_split_norm_checks": sum(
                case["split_norm_checks"] for case in cases
            ),
            "total_normalized_norm_checks": sum(
                case["normalized_norm_checks"] for case in cases
            ),
            "total_characteristic_checks": sum(
                case["characteristic_checks"] for case in cases
            ),
            "total_characteristic_matches_parity": sum(
                case["characteristic_matches_parity"] for case in cases
            ),
            "total_characteristic_mismatches_parity": sum(
                case["characteristic_mismatches_parity"] for case in cases
            ),
            "exact_characteristic_parity_decoders": sum(
                case["exact_characteristic_parity_decoders"] for case in cases
            ),
            "all_standard_twists_reject_oriented_root": all(
                not case["standard_twist_selects_oriented_root"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Distinct theta characteristics differ by two-torsion. secp256k1 "
            "has no nontrivial rational two-torsion, and the Frobenius norm of "
            "the three geometric nontrivial characteristics is y(P)^2. The "
            "normalized norm y(Q)^2/y(G)^2 is generator-blind and cannot select "
            "the marked Kummer square root Y_G."
        ),
        "claim_boundary": [
            "The orbit-norm identity is exact.",
            "The absence of rational nontrivial theta characteristics follows from the odd cofactor-one group order.",
            "The split-control character screen is bounded toy evidence only.",
            "The package does not close arbitrary metaplectic intertwiners or p-adic branch selection.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
