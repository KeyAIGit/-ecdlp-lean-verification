#!/usr/bin/env python3
"""UORC-056 C52 nonhorizontal deformation gauge decision package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from uorc056_c52_deformation_core import (
    Curve, DualCurve, SECP_G, SECP_N, SECP_P, invariant_tangent_scalar,
    lift_point, quadratic_character, torsion_lift_basis, vertical_tangent_point,
)
from uorc056_c52_deformation_analysis import build_analysis_payload

SECP_BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE",
    16,
)
SECP_LAMBDA = int(
    "5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72",
    16,
)


def secp256k1_certificate() -> dict[str, Any]:
    curve = Curve(SECP_P)
    if curve.mul(SECP_N, SECP_G) is not None:
        raise AssertionError("secp generator order mismatch")
    if pow(SECP_BETA, 3, SECP_P) != 1 or SECP_BETA == 1:
        raise AssertionError("secp beta mismatch")
    if (SECP_LAMBDA * SECP_LAMBDA + SECP_LAMBDA + 1) % SECP_N:
        raise AssertionError("secp lambda mismatch")
    if curve.mul(SECP_LAMBDA, SECP_G, SECP_N) != (
        SECP_BETA * SECP_G[0] % SECP_P,
        SECP_G[1],
    ):
        raise AssertionError("secp GLV action mismatch")

    tangent_a_g, tangent_b_g, _ = torsion_lift_basis(curve, SECP_N, SECP_G)
    dual_a = DualCurve(curve, 1, 0)
    dual_b = DualCurve(curve, 0, 1)
    dual_scaling = DualCurve(curve, 0, 6 * curve.b)
    lift_g_a = lift_point(curve, SECP_N, SECP_G, 1, 0)
    lift_g_b = lift_point(curve, SECP_N, SECP_G, 0, 1)
    lift_g_scaling = lift_point(curve, SECP_N, SECP_G, 0, 6 * curve.b)
    vertical_g = vertical_tangent_point(curve, SECP_G, 1)
    dual_fixed = DualCurve(curve)

    public_scalars = (
        1, 2, 3, 5, 7, 8, 17, 31, 127, 255,
        (SECP_N - 1) // 2,
        (SECP_N + 1) // 2,
        SECP_N - 2,
        SECP_N - 1,
    )
    horizontal_checks = scaling_checks = vertical_checks = cm_checks = 0
    samples = []
    for scalar in public_scalars:
        query = curve.mul(scalar, SECP_G, SECP_N)
        if query is None:
            raise AssertionError("unexpected secp identity")
        tangent_a, tangent_b, _ = torsion_lift_basis(curve, SECP_N, query)
        expected_a = lift_point(curve, SECP_N, query, 1, 0)
        expected_b = lift_point(curve, SECP_N, query, 0, 1)
        expected_scale = lift_point(curve, SECP_N, query, 0, 6 * curve.b)
        if dual_a.mul(scalar, lift_g_a, SECP_N) != expected_a:
            raise AssertionError("secp a transport failed")
        if dual_b.mul(scalar, lift_g_b, SECP_N) != expected_b:
            raise AssertionError("secp b transport failed")
        if dual_scaling.mul(scalar, lift_g_scaling, SECP_N) != expected_scale:
            raise AssertionError("secp scale transport failed")
        horizontal_checks += 3
        if expected_scale[0].epsilon != 2 * query[0] % SECP_P:
            raise AssertionError("secp scale x failed")
        if expected_scale[1].epsilon != 3 * query[1] % SECP_P:
            raise AssertionError("secp scale y failed")
        scaling_checks += 2

        vertical_q = dual_fixed.mul(scalar, vertical_g, SECP_N)
        if vertical_q is None or invariant_tangent_scalar(vertical_q) != scalar % SECP_P:
            raise AssertionError("secp vertical scalar recovery failed")
        vertical_checks += 1

        phi_query = curve.mul(SECP_LAMBDA * scalar, SECP_G, SECP_N)
        if phi_query != (SECP_BETA * query[0] % SECP_P, query[1]):
            raise AssertionError("secp CM point failed")
        tangent_a_phi, tangent_b_phi, _ = torsion_lift_basis(curve, SECP_N, phi_query)
        ua, va = tangent_a
        ub, vb = tangent_b
        if tangent_a_phi != (
            SECP_BETA * SECP_BETA * ua % SECP_P,
            SECP_BETA * va % SECP_P,
        ):
            raise AssertionError("secp a CM tangent failed")
        if tangent_b_phi != (SECP_BETA * ub % SECP_P, vb):
            raise AssertionError("secp b CM tangent failed")
        cm_checks += 1
        omega_a = ua * pow(2 * query[1], -1, SECP_P) % SECP_P
        omega_b = ub * pow(2 * query[1], -1, SECP_P) % SECP_P
        samples.append({
            "scalar": scalar,
            "omega_a": omega_a,
            "omega_b": omega_b,
            "chi_omega_a": quadratic_character(omega_a, SECP_P),
            "chi_omega_b": quadratic_character(omega_b, SECP_P),
        })

    return {
        "p": SECP_P,
        "n": SECP_N,
        "p_greater_than_n": SECP_P > SECP_N,
        "p_minus_n": SECP_P - SECP_N,
        "beta": SECP_BETA,
        "lambda": SECP_LAMBDA,
        "anchor_tangent_a": tangent_a_g,
        "anchor_tangent_b": tangent_b_g,
        "public_samples": len(public_scalars),
        "horizontal_transport_checks": horizontal_checks,
        "weierstrass_scaling_checks": scaling_checks,
        "vertical_scalar_recovery_checks": vertical_checks,
        "cm_covariance_checks": cm_checks,
        "vertical_recovery_formula": (
            "k=omega_Q(dot Q)/omega_G(dot G); since 0<k<n<p, this is the full canonical scalar"
        ),
        "sample_states": samples,
        "state_cost": "O(log n) first-jet recurrence; decoder absent",
    }


def build_payload() -> dict[str, Any]:
    analysis = build_analysis_payload()
    curves = analysis["curves"]
    secp = secp256k1_certificate()
    aggregate = {
        "curves": len(curves),
        "frozen": sum(row["label"].startswith("frozen") for row in curves),
        "heldout": sum(row["label"].startswith("heldout") for row in curves),
        "torsion_rows": sum(int(row["rows"]) for row in curves),
        "horizontal_transport_checks": sum(int(row["horizontal_transport_checks"]) for row in curves),
        "weierstrass_scaling_checks": sum(int(row["weierstrass_scaling_checks"]) for row in curves),
        "vertical_scalar_recovery_checks": sum(int(row["vertical_scalar_recovery_checks"]) for row in curves),
        "negation_covariance_checks": sum(int(row["negation_covariance_checks"]) for row in curves),
        "cm_covariance_checks": sum(int(row["cm_covariance_checks"]) for row in curves),
        "all_projective_direction_character_survivors_zero": all(
            not row["projective_direction_character_survivors"] for row in curves
        ),
        "all_single_feature_affine_character_survivors_zero": all(
            all(not status["affine_character_survivors"] for status in row["feature_status"].values())
            for row in curves
        ),
        "max_cm_quotient_degree_deficit": max(
            (int(row["cm_quotient"]["roots"]) - 1)
            - int(row["cm_quotient"]["R_x_times_ua"]["degree"])
            for row in curves
        ),
        "max_cm_quotient_zero_coefficients": max(
            int(row["cm_quotient"]["R_x_times_ua"]["zeros"]) for row in curves
        ),
        "uniform_structural_atoms": int(
            analysis["uniform_structural_character_screen"]["declared_atoms"]
        ),
        "uniform_structural_valid_atoms": int(
            analysis["uniform_structural_character_screen"]["valid_atoms"]
        ),
        "uniform_structural_span_rank": int(
            analysis["uniform_structural_character_screen"]["span_rank"]
        ),
        "uniform_structural_target_in_span": bool(
            analysis["uniform_structural_character_screen"]["target_in_arbitrary_product_span"]
        ),
        "complete_p43_pair_affine_atoms": int(
            analysis["complete_small_curve_pair_affine_screen"]["declared_projective_atoms"]
        ),
        "complete_p43_single_survivors": len(
            analysis["complete_small_curve_pair_affine_screen"]["exact_single_survivors"]
        ),
        "errors": sum(int(row["errors"]) for row in curves),
    }

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-NONHORIZONTAL-DEFORMATION-GAUGE-C52",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "predecessor": "C51 differential/Fay gauge boundary",
        "exact_deformation_trichotomy": {
            "finite_etale_horizontal": (
                "when n is invertible, E[n] is etale; torsion lifts uniquely and Q_t=[k]G_t is preserved"
            ),
            "fixed_curve_vertical": (
                "omega(dot Q)=k*omega(dot G); a nonzero public tangent pair reveals full k"
            ),
            "coordinate_or_connection_gauge": (
                "Weierstrass scaling is pure gauge; connection changes add chosen gauge data"
            ),
        },
        "universal_weierstrass_torsion_lift": {
            "x_tangent": "dot x=-(dot a*partial_a psi_n+dot b*partial_b psi_n)/partial_x psi_n",
            "y_tangent": "dot y=((3x^2+a)dot x+dot a*x+dot b)/(2y)",
            "j0_scaling_direction": "(4 alpha a,6 alpha b) gives (2 alpha x,3 alpha y)",
            "j0_genuine_a_direction_cm_weights": "dot x_a(phi P)=beta^2 dot x_a(P), dot y_a(phi P)=beta dot y_a(P)",
            "j0_cm_quotient": "R=x dot x_a, S=x^2 dot y_a/y, 2(T+7)S=T(3R+1)",
        },
        "analysis": analysis,
        "secp256k1": secp,
        "aggregate": aggregate,
        "claim_boundary": {
            "proved_or_replayed": [
                "unique prime-to-characteristic torsion lifting in the declared first-order model",
                "preservation of Q_t=[k]G_t under two curve directions and scaling",
                "full-scalar recovery from a nonzero fixed-fibre vertical tangent pair",
                "pure-gauge b-direction and scaling",
                "negation and GLV covariance of the genuine a-deformation tangent",
                "CM quotient relation 2(T+7)S=T(3R+1)",
                "declared held-out character screens",
                "public secp256k1 sample certificates",
            ],
            "not_claimed": [
                "an unrestricted deformation or connection lower bound",
                "nonexistence of arbitrary nonlinear tangent-state decoders",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision": {
            "public_finite_etale_torsion_lift_compiler_found": True,
            "functorial_curve_deformation_is_horizontal_on_torsion_labels": True,
            "nonzero_fixed_curve_vertical_deformation_reveals_full_scalar": True,
            "weierstrass_scaling_breaks_quadratic_gauge": False,
            "genuine_moduli_tangent_state_found": True,
            "declared_deformation_character_grammar_closed": True,
            "nonhorizontal_public_deformation_with_endpoint_charge_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "CONNECTION-DEFECT-AND-MODULI-TANGENT-DECODER-C53",
            "target": (
                "classify connection defects and nonlinear decoders of the genuine a-deformation torsion jet"
            ),
            "mandatory_gate": (
                "no k through tangent advice; charge preprocessing, advice, tables, precision, memory and online cost"
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
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("UORC056_NONHORIZONTAL_DEFORMATION_GAUGE_C52_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + payload["digest"])


if __name__ == "__main__":
    main()
