#!/usr/bin/env python3
"""UORC-056 C53 decision package.

C53 classifies connection defects and attacks nonlinear decoders of the public
moduli-tangent state.  It accepts no external target, hidden scalar, private
key, wallet, tangent advice, or signed branch table.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from uorc056_c52_deformation_core import Curve, torsion_lift_basis
from uorc056_c53_connection_core import (
    ALL_CURVES, C52_CURVES, NEW_HELD_OUT, SECP_G, SECP_N, SECP_P,
    defect, normalized, recover_multiplier_from_defect,
)
from uorc056_c53_analysis import (
    analyze_curve, complete_p43_nonlinear_screen, public_curve_result,
    uniform_character_screen,
)

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

    (ua_g, va_g), (ub_g, vb_g), _ = torsion_lift_basis(curve, SECP_N, SECP_G)
    xg, yg = SECP_G
    omega_a_g = ua_g * pow(2 * yg, -1, SECP_P) % SECP_P
    omega_b_g = ub_g * pow(2 * yg, -1, SECP_P) % SECP_P
    r_g = xg * ua_g % SECP_P
    if not all((omega_a_g, omega_b_g, r_g)):
        raise AssertionError("singular secp anchor chart")

    public_scalars = (
        1, 2, 3, 5, 7, 8, 17, 31, 127, 255,
        (SECP_N - 1) // 2,
        (SECP_N + 1) // 2,
        SECP_N - 2,
        SECP_N - 1,
    )
    recovery_checks = factorization_checks = cm_checks = 0
    samples = []
    for scalar in public_scalars:
        query = curve.mul(scalar, SECP_G, SECP_N)
        if query is None:
            raise AssertionError("unexpected secp identity")
        (ua, va), (ub, vb), _ = torsion_lift_basis(curve, SECP_N, query)
        x, y = query
        omega_a = ua * pow(2 * y, -1, SECP_P) % SECP_P
        omega_b = ub * pow(2 * y, -1, SECP_P) % SECP_P
        delta = defect(omega_a, scalar, omega_a_g, SECP_P)
        recovered = recover_multiplier_from_defect(
            omega_a, delta, omega_a_g, SECP_P
        )
        if recovered != scalar:
            raise AssertionError("secp connection defect did not recover full scalar")
        recovery_checks += 1

        oa = normalized(omega_a, omega_a_g, SECP_P)
        ob = normalized(omega_b, omega_b_g, SECP_P)
        t = x**3 % SECP_P
        r = x * ua % SECP_P
        neutral = (
            r * pow(r_g, -1, SECP_P)
            * (pow(xg, 3, SECP_P) + 7)
            * pow(t + 7, -1, SECP_P)
        ) % SECP_P
        if oa * ob % SECP_P != neutral:
            raise AssertionError("secp charged-neutral factorization failed")
        factorization_checks += 1

        phi_query = curve.mul(SECP_LAMBDA * scalar, SECP_G, SECP_N)
        if phi_query != (SECP_BETA * x % SECP_P, y):
            raise AssertionError("secp GLV point mismatch")
        (ua_phi, va_phi), _, _ = torsion_lift_basis(curve, SECP_N, phi_query)
        if (ua_phi, va_phi) != (
            SECP_BETA * SECP_BETA * ua % SECP_P,
            SECP_BETA * va % SECP_P,
        ):
            raise AssertionError("secp GLV tangent mismatch")
        cm_checks += 1
        samples.append({
            "scalar": scalar,
            "connection_defect": delta,
            "charged_OA": oa,
            "charged_OB": ob,
            "neutral_product": neutral,
        })

    return {
        "p": SECP_P,
        "n": SECP_N,
        "p_greater_than_n": SECP_P > SECP_N,
        "public_samples": len(public_scalars),
        "full_scalar_connection_recovery_checks": recovery_checks,
        "charged_neutral_factorization_checks": factorization_checks,
        "cm_covariance_checks": cm_checks,
        "classification": (
            "an exact public nonzero-anchor defect oracle yields the full scalar; "
            "the public torsion lift alone does not provide that defect"
        ),
        "samples": samples,
    }


def build_payload() -> dict[str, Any]:
    curve_data = []
    for index, row in enumerate(ALL_CURVES):
        if index < 4:
            label = f"frozen-{index + 1}"
        elif index < len(C52_CURVES):
            label = f"heldout-c52-{index - 3}"
        else:
            label = f"heldout-c53-{index - len(C52_CURVES) + 1}"
        degree_bound = 16 if row[1] <= 400 else 10
        curve_data.append(analyze_curve(row, label, degree_bound))

    uniform = uniform_character_screen(curve_data)
    complete = complete_p43_nonlinear_screen(
        curve_data[0]["rows"], curve_data[0]["context"], curve_data[0]["columns"]
    )
    secp = secp256k1_certificate()
    public_curves = [public_curve_result(data) for data in curve_data]

    aggregate = {
        "curves": len(curve_data),
        "frozen": 4,
        "c52_heldout": len(C52_CURVES) - 4,
        "new_c53_heldout": len(NEW_HELD_OUT),
        "rows": sum(len(data["rows"]) for data in curve_data),
        "connection_recovery_checks": sum(
            data["connection"]["nonzero_anchor_recovery_checks"]
            for data in curve_data
        ),
        "anchor_zero_checks": sum(
            data["connection"]["anchor_zero_direct_state_checks"]
            for data in curve_data
        ),
        "gauge_coboundary_checks": sum(
            data["connection"]["gauge_coboundary_checks"]
            for data in curve_data
        ),
        "connection_cocycle_checks": sum(
            data["connection"]["multiplier_cocycle_checks"]
            for data in curve_data
        ),
        "quotient_invariance_checks": sum(
            data["covariance"]["quotient_invariance_checks"]
            for data in curve_data
        ),
        "charged_neutral_factorization_checks": sum(
            data["covariance"]["charged_neutral_factorization_checks"]
            for data in curve_data
        ),
        "all_quotient_states_have_opposite_parity_collisions": all(
            data["covariance"][
                "quotient_state_has_exact_opposite_parity_collision"
            ]
            for data in curve_data
        ),
        "uniform_character_atoms": uniform["declared_atoms"],
        "uniform_valid_character_atoms": uniform["valid_atoms"],
        "uniform_character_span_rank": uniform["span_rank"],
        "uniform_target_in_span": uniform[
            "target_in_arbitrary_product_span"
        ],
        "complete_p43_nonlinear_atoms": complete["declared_atoms"],
        "complete_p43_exact_single_survivors": len(
            complete["exact_single_survivors"]
        ),
        "errors": sum(data["errors"] for data in curve_data),
    }

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-CONNECTION-DEFECT-MODULI-DECODER-C53",
        "schema_version": "1.0",
        "central_target": "Q=[k]G -> (-1)^k",
        "predecessor": "C52 nonhorizontal deformation gauge boundary",
        "exact_connection_classification": {
            "defect": "delta_m^c(P)=c([m]P)-m c(P)",
            "multiplier_cocycle": (
                "delta_ab(P)=delta_a([b]P)+a delta_b(P)"
            ),
            "gauge_change": (
                "delta_m^(c+f)-delta_m^c=f([m]P)-m f(P)"
            ),
            "functorial_connection": "delta=0",
            "anchor_zero": (
                "c(G)=0 implies delta_k(G)=c(Q); the connection wrapper adds no information"
            ),
            "nonzero_anchor": (
                "c(G)!=0 and exact delta_k(G) imply k=(c(Q)-delta_k(G))/c(G)"
            ),
        },
        "charged_neutral_normal_form": {
            "OA": "omega_a(Q)/omega_a(G)",
            "OB": "omega_b(Q)/omega_b(G)=x(Q)y(G)/(x(G)y(Q))",
            "neutral_product": (
                "OA*OB=(R(Q)/R(G))*((T(G)+7)/(T(Q)+7))"
            ),
            "interpretation": (
                "the moduli tangent contributes a sign-neutral factor; endpoint charge is carried by the ordinary x/y coordinate ratio"
            ),
        },
        "arbitrary_decoder_no_go": {
            "state": "(T,R,S) with 2(T+7)S=T(3R+1)",
            "reason": (
                "the state is identical at Q and -Q while parity changes sign"
            ),
            "glv_triple": (
                "R(Q)=R(phi Q)=R(phi^2 Q), and likewise for S,T"
            ),
        },
        "curves": public_curves,
        "uniform_nonlinear_character_screen": uniform,
        "complete_p43_nonlinear_screen": complete,
        "secp256k1": secp,
        "aggregate": aggregate,
        "decision": {
            "connection_defect_is_independent_parity_mechanism": False,
            "functorial_connection_defect_zero": True,
            "anchor_zero_defect_is_direct_public_state": True,
            "nonzero_anchor_defect_oracle_reveals_full_scalar": True,
            "arbitrary_decoder_from_glv_quotient_state_possible": False,
            "charged_neutral_factorization_found": True,
            "declared_bounded_nonlinear_grammar_closed": True,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "claim_boundary": {
            "proved_or_replayed": [
                "the exact connection-defect cocycle and gauge formulas",
                "the zero/direct-state/full-scalar trichotomy",
                "arbitrary-decoder impossibility for the GLV quotient state by Q/-Q collision",
                "the exact charged-neutral factorization of OA and OB",
                "bounded polynomial and nonlinear character screens on 16 curves",
                "four held-out curves not used by C52",
            ],
            "not_claimed": [
                "an unrestricted lower bound for every nonlinear function of the charged pair",
                "an unrestricted arithmetic-circuit lower bound",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "successor": {
            "id": "CHARGED-MODULI-TANGENT-TRANSFER-C54",
            "target": (
                "analyze the addition, orbit-factor, and short-resultant complexity of the surviving charged pair (OA,OB), after quotienting the exact neutral factor"
            ),
            "mandatory_gate": (
                "a candidate must add numerical endpoint charge beyond the public x/y ratio and may not use a scalar-labelled connection defect"
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
    print("UORC056_CONNECTION_DEFECT_MODULI_DECODER_C53_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + payload["digest"])


if __name__ == "__main__":
    main()
