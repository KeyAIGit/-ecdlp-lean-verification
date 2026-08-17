#!/usr/bin/env python3
"""UORC-056 C51 differential/Fay gauge decision package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from uorc056_c51_differential_core import (
    ANOMALOUS_CONTROLS, FROZEN, HELD_OUT, SECP_G, SECP_N, SECP_P,
    Curve, DivisionSeries, NetLineSeries, logarithmic_derivatives,
    period_shift_coefficients, period_shift_eta_coefficient,
    quadratic_character, regularized_torsion_jet,
)
from uorc056_c51_differential_analysis import analyze_curve

def ward_constants_at_generator(
    prime: int, order: int, generator: tuple[int, int]
) -> tuple[int, int]:
    sequence = DivisionSeries(prime, generator[0], generator[1], 1)
    w2 = sequence.psi(2).coefficients[0]
    wn1 = sequence.psi(order + 1).coefficients[0]
    wn2 = sequence.psi(order + 2).coefficients[0]
    ward_a = wn2 * pow(w2 * wn1 % prime, -1, prime) % prime
    ward_b = wn1 * wn1 % prime * w2 % prime * pow(wn2, -1, prime) % prime
    return ward_a, ward_b


def secp256k1_certificate() -> dict[str, Any]:
    curve = Curve(SECP_P)
    if curve.mul(SECP_N, SECP_G) is not None:
        raise AssertionError("secp256k1 generator order check failed")
    ward_a, ward_b = ward_constants_at_generator(SECP_P, SECP_N, SECP_G)
    if quadratic_character(ward_a, SECP_P) != 1:
        raise AssertionError("Ward a must be a square")
    if quadratic_character(ward_b, SECP_P) != -1:
        raise AssertionError("Ward b certificate drifted")

    public_scalars = (
        1,
        2,
        3,
        5,
        7,
        8,
        17,
        31,
        127,
        255,
        (SECP_N - 1) // 2,
        (SECP_N + 1) // 2,
        SECP_N - 2,
        SECP_N - 1,
    )
    h_values: dict[int, int] = {}
    for scalar in public_scalars:
        point = curve.mul(scalar, SECP_G, SECP_N)
        if point is None:
            raise AssertionError("unexpected secp identity")
        h_values[scalar] = regularized_torsion_jet(
            SECP_P, SECP_N, point
        )[0]

    differential_checks = 0
    second_checks = 0
    third_checks = 0
    for scalar in (2, 3, 5, 7, 8, 17, 31, 127, 255):
        query = curve.mul(scalar, SECP_G, SECP_N)
        query_plus = curve.add(query, SECP_G)
        net = NetLineSeries(SECP_P, SECP_G, query, 4).value(SECP_N)
        first, second, third = logarithmic_derivatives(SECP_P, query, net)
        h_query = regularized_torsion_jet(SECP_P, SECP_N, query)[0]
        h_next = regularized_torsion_jet(SECP_P, SECP_N, query_plus)[0]
        h_anchor = h_values[1]
        if first != (-h_anchor + (SECP_N - 1) * h_query + h_next) % SECP_P:
            raise AssertionError("secp first differential identity failed")
        if second != (
            -SECP_N * SECP_N * SECP_G[0]
            + (SECP_N * SECP_N - SECP_N) * query[0]
            + SECP_N * query_plus[0]
        ) % SECP_P:
            raise AssertionError("secp second differential identity failed")
        if third != (
            -2 * SECP_N**3 * SECP_G[1]
            + 2 * (SECP_N * SECP_N - SECP_N) * query[1]
            + 2 * SECP_N * query_plus[1]
        ) % SECP_P:
            raise AssertionError("secp third differential identity failed")
        differential_checks += 1
        second_checks += 1
        third_checks += 1

    return {
        "p": SECP_P,
        "n": SECP_N,
        "p_not_equal_n": SECP_P != SECP_N,
        "n_invertible_mod_p": SECP_N % SECP_P != 0,
        "ward_a": ward_a,
        "ward_b": ward_b,
        "chi_ward_a": quadratic_character(ward_a, SECP_P),
        "chi_ward_b": quadratic_character(ward_b, SECP_P),
        "H_at_G": h_values[1],
        "public_H_samples": len(h_values),
        "first_differential_checks": differential_checks,
        "second_differential_checks": second_checks,
        "third_differential_checks": third_checks,
        "state_cost": (
            "O(log n) truncated-series division/net recurrence; decoder absent"
        ),
    }


def anomalous_control_certificate() -> list[dict[str, Any]]:
    rows = []
    for prime, order, generator in ANOMALOUS_CONTROLS:
        curve = Curve(prime)
        if prime != order:
            raise AssertionError("control is not anomalous")
        point = curve.mul(1, generator, order)
        series = DivisionSeries(prime, point[0], point[1], 4).psi(order)
        rows.append({
            "p": prime,
            "n": order,
            "psi_n_local_coefficients": list(series.coefficients),
            "separable_first_jet_available": any(series.coefficients),
            "excluded_reason": "characteristic divides n; psi_p is inseparable/degenerate",
        })
    return rows


def build_payload() -> dict[str, Any]:
    curves = [
        analyze_curve(row, f"frozen-{index + 1}")
        for index, row in enumerate(FROZEN)
    ] + [
        analyze_curve(row, f"heldout-{index + 1}")
        for index, row in enumerate(HELD_OUT)
    ]
    secp = secp256k1_certificate()
    anomalous = anomalous_control_certificate()

    aggregate = {
        "curves": len(curves),
        "frozen": len(FROZEN),
        "heldout": len(HELD_OUT),
        "torsion_jet_rows": sum(int(row["rows"]) for row in curves),
        "first_derivative_checks": sum(
            int(row["first_derivative_checks"]) for row in curves
        ),
        "second_derivative_checks": sum(
            int(row["second_derivative_checks"]) for row in curves
        ),
        "third_derivative_checks": sum(
            int(row["third_derivative_checks"]) for row in curves
        ),
        "eta_cancellation_checks": sum(
            int(row["eta_cancellation_checks"]) for row in curves
        ),
        "all_affine_character_survivors_zero": all(
            all(value == 0 for value in row["affine_character_survivors"].values())
            for row in curves
        ),
        "all_H_have_mixed_parity_collisions": all(
            int(row["H_query_mixed_parity_collisions"]) > 0 for row in curves
        ),
        "all_cm_quotients_dense": all(
            bool(row["cm_quotient"]["dense"]) for row in curves
        ),
        "max_cm_degree_deficit_from_interpolation_ceiling": max(
            (int(row["cm_quotient"]["roots"]) - 1)
            - int(row["cm_quotient"]["degree"])
            for row in curves
        ),
        "anomalous_controls": len(anomalous),
        "errors": sum(int(row["errors"]) for row in curves),
    }

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-DIFFERENTIAL-FAY-GAUGE-C51",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "predecessor": "C50 Ward phase gauge correction",
        "exact_normal_form": {
            "net_section": (
                "Psi_(a,b)(z,w)=sigma(az+bw)/(sigma(z)^(a^2-ab) "
                "sigma(w)^(b^2-ab) sigma(z+w)^(ab))"
            ),
            "periodic_jet": "H(j)=j*eta-n*zeta(jz), H(j+n)=H(j)",
            "period_shift": (
                "dlog Psi_(a+rn,b+sn)-dlog Psi_(a,b)="
                "-s H(a+bk)+A1 H(k)+A2 H(k+1)"
            ),
            "A1": "2bs-as-rb+n(s^2-rs)",
            "A2": "as+rb+nrs",
            "high_index_specialization": (
                "dlog_Q Psi_(1,n)(G,Q)=-H(G)+(n-1)H(Q)+H(Q+G)"
            ),
            "second_derivative": (
                "d_Q^2 log Psi_(1,n)=-n^2 x(G)+(n^2-n)x(Q)+n x(Q+G)"
            ),
            "third_derivative": (
                "d_Q^3 log Psi_(1,n)=-2n^3 y(G)+2(n^2-n)y(Q)+2n y(Q+G)"
            ),
        },
        "curves": curves,
        "anomalous_controls": anomalous,
        "secp256k1": secp,
        "aggregate": aggregate,
        "claim_boundary": {
            "proved_or_replayed": [
                "quasiperiod eta cancels from every declared first period-shift differential",
                "the high-index first derivative reduces to three regularized torsion jets",
                "the second and third logarithmic derivatives reduce to public coordinate functions",
                "H_n is odd, generator-blind, and has GLV weight beta^2",
                "the CM quotient representation of H_n is dense and within nine degrees of the interpolation ceiling on the declared corpus",
                "no affine quadratic-character decoder of H_n, dlog Psi_(1,n), or Psi_(1,n) survives on any declared curve",
                "two p=n anomalous controls are excluded from the separable-jet claim",
                "public secp256k1 sample identities with O(log n) truncated recurrences",
            ],
            "not_claimed": [
                "an unrestricted differential-circuit lower bound",
                "an unrestricted Fay or theta lower bound",
                "nonexistence of a decoder from arbitrary nonlinear combinations of H values",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision": {
            "fast_regularized_torsion_jet_found": True,
            "fast_anchor_mixed_net_derivative_found": True,
            "first_differential_exposes_integer_lift": False,
            "higher_differentials_break_section_gauge": False,
            "declared_differential_fay_grammar_reduces_to_periodic_public_states": True,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "NONHORIZONTAL-DEFORMATION-GAUGE-C52",
            "target": (
                "test a functorial curve/moduli deformation whose derivative is "
                "not a descended elliptic differential and determine whether the "
                "required torsion lift already injects k or a dual phase"
            ),
            "mandatory_gate": (
                "the deformation must preserve Q=[k]G without receiving k, must "
                "specify its connection/trivialization, and must charge p-adic or "
                "extension precision, advice, memory, and branch normalization"
            ),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("UORC056_DIFFERENTIAL_FAY_GAUGE_C51_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
