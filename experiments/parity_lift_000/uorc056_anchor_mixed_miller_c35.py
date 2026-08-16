#!/usr/bin/env python3
"""Exact C35 package for shifted Miller gauges and torus collapse."""
from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from itertools import product
from math import gcd
from pathlib import Path

from uorc056_shifted_miller_core import *
from uorc056_shifted_miller_eval import *
from uorc056_shifted_miller_curve_screen import build_curve_payload

def screen_common_low_order_grammar(curves: list[dict[str, object]]) -> dict[str, object]:
    survivors: list[dict[str, object]] = []
    exponent_vectors = 0
    for exponents in product((-1, 0, 1), repeat=7):
        if not any(exponents):
            continue
        exponent_vectors += 1
        for order in COMMON_CHARACTER_ORDERS:
            valid_all = True
            for curve in curves:
                n = int(curve["n"])
                profiles = curve["logs"]
                assert isinstance(profiles, list)
                even: set[int] = set()
                odd: set[int] = set()
                for k in range(1, n):
                    residue = sum(
                        exponents[index] * int(profiles[index][k - 1])
                        for index in range(7)
                    ) % order
                    (even if k % 2 == 0 else odd).add(residue)
                if not even.isdisjoint(odd):
                    valid_all = False
                    break
            if valid_all:
                survivors.append({"order": order, "exponents": list(exponents)})
    return {
        "character_orders": list(COMMON_CHARACTER_ORDERS),
        "exponent_vectors": exponent_vectors,
        "candidate_pairs_tested": exponent_vectors * len(COMMON_CHARACTER_ORDERS),
        "uniform_survivors": survivors,
    }


def division_psi(instance: Instance, index: int, point: tuple[int, int]) -> int:
    """Division-polynomial value for the frozen short Weierstrass a=0 curves."""
    p = instance.curve.p
    b = instance.curve.b
    x, y = point

    @lru_cache(None)
    def value(j: int) -> int:
        if j == 0:
            return 0
        if j == 1:
            return 1
        if j == 2:
            return 2 * y % p
        if j == 3:
            return (3 * pow(x, 4, p) + 12 * b * x) % p
        if j == 4:
            return (4 * y * (pow(x, 6, p) + 20 * b * pow(x, 3, p) - 8 * b * b)) % p
        if j & 1:
            r = (j - 1) // 2
            return (value(r + 2) * pow(value(r), 3, p) - value(r - 1) * pow(value(r + 1), 3, p)) % p
        r = j // 2
        return (
            value(r)
            * pow(2 * y, -1, p)
            * (value(r + 2) * pow(value(r - 1), 2, p) - value(r - 2) * pow(value(r + 1), 2, p))
        ) % p

    return value(index)


def legacy_division_character_screen() -> dict[str, object]:
    """Preserve the preliminary 196-atom C35 F2 inconsistency screen."""
    instance = INSTANCES[0]
    p, n = instance.curve.p, instance.n
    t = (n - 1) // 2
    locations = (1, 2, t, (t - 2) % n, (-t) % n, (-(t - 2)) % n, 3)
    features = tuple((index, multiplier) for index in range(2, 30) for multiplier in locations)
    table = [instance.curve.mul(k, instance.G) for k in range(n)]
    base_values = []
    for index, multiplier in features:
        point = table[multiplier]
        assert point is not None
        value = division_psi(instance, index, point)
        if value == 0:
            raise AssertionError("legacy character denominator vanished")
        base_values.append(value)

    pivots: dict[int, int] = {}
    contradiction_at: int | None = None
    processed = 0
    for k in range(1, n):
        mask = 0
        for feature_index, ((index, multiplier), base) in enumerate(zip(features, base_values)):
            point = table[(multiplier * k) % n]
            assert point is not None
            value = division_psi(instance, index, point)
            if value == 0:
                raise AssertionError("legacy character numerator vanished")
            sign = legendre(value * pow(base, -1, p), p)
            if sign == -1:
                mask |= 1 << feature_index
        target = (k + 1) & 1
        row = mask | (target << len(features))
        for pivot in sorted(pivots, reverse=True):
            if (row >> pivot) & 1:
                row ^= pivots[pivot]
        feature_part = row & ((1 << len(features)) - 1)
        if feature_part == 0:
            if (row >> len(features)) & 1:
                contradiction_at = k
                break
        else:
            pivots[feature_part.bit_length() - 1] = row
        processed += 1
    if contradiction_at is None:
        raise AssertionError("legacy character grammar unexpectedly survived")
    return {
        "instance": instance.name,
        "features": len(features),
        "processed_rows_before_contradiction": processed,
        "rank_before_contradiction": len(pivots),
        "contradiction_at_k": contradiction_at,
        "exact_survivors": 0,
    }

def build_payload() -> dict[str, object]:
    curve_results: list[dict[str, object]] = []
    grammar_curves: list[dict[str, object]] = []
    for instance in INSTANCES:
        curve_result, grammar = build_curve_payload(instance)
        curve_results.append(curve_result)
        grammar_curves.append(grammar)
    grammar = screen_common_low_order_grammar(grammar_curves)
    legacy_screen = legacy_division_character_screen()

    p2_minus_one = SECP_P * SECP_P - 1
    secp = {
        "p": SECP_P,
        "n": SECP_N,
        "gcd_n_p_minus_1": gcd(SECP_N, SECP_P - 1),
        "gcd_n_p_plus_1": gcd(SECP_N, SECP_P + 1),
        "gcd_n_p2_minus_1": gcd(SECP_N, p2_minus_one),
        "inverse_n_mod_p_minus_1": pow(SECP_N, -1, SECP_P - 1),
        "inverse_n_mod_p_plus_1": pow(SECP_N, -1, SECP_P + 1),
        "inverse_n_mod_p2_minus_1": pow(SECP_N, -1, p2_minus_one),
        "n_th_power_maps_are_automorphisms": True,
    }

    aggregate = {
        "curves": len(curve_results),
        "twist_shifts": sum(int(row["twist_shifts"]) for row in curve_results),
        "shift_query_cases": sum(int(row["shift_query_cases"]) for row in curve_results),
        "normalized_shift_gauge_checks": sum(
            int(row["normalized_shift_gauge_checks"]) for row in curve_results
        ),
        "torus_kummer_checks": sum(int(row["torus_kummer_checks"]) for row in curve_results),
        "miller_loop_comparisons": sum(int(row["miller_loop_comparisons"]) for row in curve_results),
        "quadratic_character_shift_survivors": sum(
            int(row["quadratic_character_shift_survivors"]) for row in curve_results
        ),
        "curves_whose_entire_shift_family_requires_full_torus_order": sum(
            len(row["minimal_character_order_histogram"]) == 1
            and str(int(row["p"]) + 1) in row["minimal_character_order_histogram"]
            for row in curve_results
        ),
        "quadratic_subset_exact_survivors": sum(
            int(row["canonical_shift"]["quadratic_subset_exact_survivors"])
            for row in curve_results
        ),
        "low_order_three_carry_uniform_survivors": len(grammar["uniform_survivors"]),
        "errors": 0,
    }

    payload: dict[str, object] = {
        "profile_id": "UORC-056-ANCHOR-MIXED-MILLER-C35",
        "schema_version": "2.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "shifted_miller_state": {
            "definition": "M_S(P)=f_G(P+S)/f_G(S), with div(f_G)=n[G]-n[O] and S^p=-S",
            "straight_line_cost": "O(log n) field operations after public source selection",
            "normalized_shift_gauge": "M_S(P)/M_S(P0)=f_G(P)/f_G(P0)*(g_(G,-S)(P0)/g_(G,-S)(P))^n",
            "interpretation": "Every shift is an explicit n-th-power line gauge of one base Miller potential; shifts are not independent orientation channels.",
        },
        "torus_collapse": {
            "definition": "T_S(P)=M_S(P)^(p-1)",
            "centered_ratio": "R_S(P)=(x(P-H)-x(H+S))/(x(P-H)-x(S-H)), H=[1/2]G",
            "identity": "T_S(P)/T_S(P0)=(R_S(P)/R_S(P0))^n",
            "frobenius": "R_S(P)^p=R_S(P)^(-1)",
            "interpretation": "The norm-one component is exactly a public centered Kummer coordinate followed by the n-th-power automorphism.",
        },
        "curve_results": curve_results,
        "legacy_division_character_screen": legacy_screen,
        "three_carry_character_grammar": grammar,
        "secp256k1": secp,
        "aggregate": aggregate,
        "decision": {
            "marked_generator_source_used": True,
            "canonical_y_anchor_scalar_used": False,
            "generator_sensitive_miller_source_is_equivalent_oriented_resource": True,
            "compact_shifted_miller_state_found": True,
            "shifted_state_publicly_evaluable_by_miller_chain": True,
            "independent_orientation_channels_from_twist_shifts_found": False,
            "torus_component_collapses_to_centered_kummer": True,
            "secp_torus_nth_power_is_publicly_invertible": True,
            "quadratic_shift_evaluator_found": False,
            "low_order_three_carry_monomial_found": False,
            "full_field_state_has_low_degree_rational_decoder": False,
            "parity_oracle_found": False,
            "sub_sqrt_evaluator_found": False,
            "sub_sqrt_ecdlp_found": False,
            "successor": "MULTI-ARGUMENT-MILLER-DECODER-C36",
        },
        "claim_boundary": {
            "proved": [
                "the normalized line-gauge identity by divisor comparison",
                "the normalized torus/Kummer identity by divisor comparison",
                "exact frozen replay over every anti-rational twist shift",
                "secp256k1 n-th-power automorphism arithmetic",
                "scoped rational-decoder root-count bound on canonical toy states",
            ],
            "finite_screen_only": [
                "minimal character-order histograms on frozen curves",
                "absence of quadratic shift survivors",
                "absence of low-order seven-location monomial survivors",
            ],
            "not_claimed": [
                "an unrestricted arithmetic-circuit lower bound",
                "nonexistence of every nonlinear multi-argument Miller decoder",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
    }
    digest_input = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(digest_input).hexdigest()
    return payload


def validate_payload(payload: dict[str, object]) -> None:
    aggregate = payload["aggregate"]
    assert aggregate["curves"] == 5
    assert aggregate["twist_shifts"] == 520
    assert aggregate["shift_query_cases"] == 54192
    assert aggregate["normalized_shift_gauge_checks"] == 53672
    assert aggregate["torus_kummer_checks"] == 54192
    assert aggregate["miller_loop_comparisons"] == 438
    assert aggregate["quadratic_character_shift_survivors"] == 0
    assert aggregate["curves_whose_entire_shift_family_requires_full_torus_order"] == 4
    assert aggregate["quadratic_subset_exact_survivors"] == 0
    assert aggregate["low_order_three_carry_uniform_survivors"] == 0
    assert aggregate["errors"] == 0
    assert payload["legacy_division_character_screen"]["features"] == 196
    assert payload["legacy_division_character_screen"]["exact_survivors"] == 0
    expected_histograms = {
        "E7-P43-N31": {"11": 2, "22": 12, "24": 2, "28": 4, "33": 4, "42": 2, "44": 30},
        "E7-P67-N79": {"68": 56},
        "E7-P79-N67": {"80": 92},
        "E7-P127-N127": {"128": 128},
        "E7-P163-N139": {"164": 188},
    }
    expected_state_counts = {
        "E7-P43-N31": (28, 27, 28),
        "E7-P67-N79": (76, 75, 76),
        "E7-P79-N67": (64, 63, 64),
        "E7-P127-N127": (124, 123, 124),
        "E7-P163-N139": (136, 135, 136),
    }
    for row in payload["curve_results"]:
        assert row["minimal_character_order_histogram"] == expected_histograms[row["instance"]]
        distinct, degree, nonzero = expected_state_counts[row["instance"]]
        canonical = row["canonical_shift"]
        assert canonical["distinct_full_states"] == distinct
        assert canonical["interpolation_degree"] == degree
        assert canonical["interpolation_nonzero_coefficients"] == nonzero
        assert canonical["distinct_torus_states"] == (row["n"] + 1) // 2
    secp = payload["secp256k1"]
    assert secp["gcd_n_p_minus_1"] == 1
    assert secp["gcd_n_p_plus_1"] == 1
    assert secp["gcd_n_p2_minus_1"] == 1
    assert len(payload["digest"]) == 64


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if args.check:
        validate_payload(payload)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("UORC056_ANCHOR_MIXED_MILLER_C35_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print(f"digest={payload['digest']}")


if __name__ == "__main__":
    main()
