#!/usr/bin/env python3
"""UORC-056 C53 decision package.

Only fixed public test curves and public secp256k1 constants are used.  No
external target, unknown scalar, private key, wallet or scalar-dependent tangent
advice is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from uorc056_c52_deformation_core import (
    Curve, SECP_G, SECP_N, SECP_P, torsion_lift_basis,
)
from uorc056_c53_connection_core import (
    connection_defect,
    gauge_changed_defect,
    moduli_covariant_derivatives,
    recover_scalar_from_known_defect,
)
from uorc056_c53_moduli_analysis import build_analysis_payload

SECP_BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
SECP_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72


def connection_classification_certificate() -> dict[str, Any]:
    p = 101
    checks = 0
    for scalar in range(1, 29):
        anchor = 7
        query = scalar * anchor % p
        functorial = connection_defect(query, scalar, anchor, p)
        if functorial != 0:
            raise AssertionError("functorial defect did not vanish")
        checks += 1

        old = (11 * scalar + 3) % p
        gauge_anchor = 13
        gauge_query = (17 * scalar + 5) % p
        changed = gauge_changed_defect(
            old, gauge_query, scalar, gauge_anchor, p
        )
        if changed != (old + gauge_query - scalar * gauge_anchor) % p:
            raise AssertionError("gauge coboundary identity failed")
        checks += 1

        desired = (scalar * scalar + 9) % p
        endpoint_gauge = (desired - old) % p
        if gauge_changed_defect(old, endpoint_gauge, scalar, 0, p) != desired:
            raise AssertionError("anchor-zero gauge freedom failed")
        checks += 1

        defect = (19 * scalar + 4) % p
        connection_query = (scalar * anchor + defect) % p
        if recover_scalar_from_known_defect(
            connection_query, defect, anchor, p
        ) != scalar:
            raise AssertionError("known defect did not recover scalar")
        checks += 1
    return {
        "field_prime": p,
        "scalars": 28,
        "checks": checks,
        "functorial_defect_zero": True,
        "gauge_change_is_endpoint_coboundary": True,
        "one_anchor_does_not_fix_componentwise_gauge": True,
        "known_defect_with_nonzero_anchor_reveals_scalar": True,
    }


def secp256k1_certificate() -> dict[str, Any]:
    curve = Curve(SECP_P)
    if curve.mul(SECP_N, SECP_G) is not None:
        raise AssertionError("bad secp generator")
    samples = (1, 2, 3, 5, 7, 17, 127, (SECP_N - 1) // 2)
    scalar_set = set(samples)
    scalar_set.update(SECP_N - scalar for scalar in samples)
    scalar_set.update(SECP_LAMBDA * scalar % SECP_N for scalar in samples)
    values = {}
    cross_checks = 0
    for scalar in sorted(scalar_set):
        point = curve.mul(scalar, SECP_G, SECP_N)
        if point is None:
            raise AssertionError("unexpected secp identity")
        derivatives, ua = moduli_covariant_derivatives(
            curve, SECP_N, point, 7
        )
        tangent_a, _tangent_b, _jet = torsion_lift_basis(
            curve, SECP_N, point
        )
        if ua != tangent_a[0] or derivatives[0] != point[0] * ua % SECP_P:
            raise AssertionError("secp first-jet cross-check failed")
        values[scalar] = (point, derivatives)
        cross_checks += 1

    negation = glv = 0
    for scalar in samples:
        point, derivatives = values[scalar]
        opposite_point, opposite = values[SECP_N - scalar]
        image_point, image = values[SECP_LAMBDA * scalar % SECP_N]
        if opposite_point != curve.neg(point):
            raise AssertionError("secp negation point mismatch")
        expected_negation = (
            derivatives[0], -derivatives[1] % SECP_P,
            derivatives[2], -derivatives[3] % SECP_P,
        )
        if opposite != expected_negation:
            raise AssertionError("secp derivative negation mismatch")
        negation += 1
        if image_point != (SECP_BETA * point[0] % SECP_P, point[1]):
            raise AssertionError("secp GLV point mismatch")
        expected_image = (
            derivatives[0],
            SECP_BETA * SECP_BETA % SECP_P * derivatives[1] % SECP_P,
            SECP_BETA * derivatives[2] % SECP_P,
            derivatives[3],
        )
        if image != expected_image:
            raise AssertionError("secp derivative GLV mismatch")
        glv += 1
    return {
        "p": SECP_P,
        "n": SECP_N,
        "samples": len(samples),
        "distinct_evaluations": len(values),
        "first_jet_cross_checks": cross_checks,
        "negation_checks": negation,
        "glv_checks": glv,
        "builder_index_cost": "O(log n) for fixed derivative order",
    }


def build_payload() -> dict[str, Any]:
    analysis = build_analysis_payload()
    connection = connection_classification_certificate()
    secp = secp256k1_certificate()
    aggregate = dict(analysis["aggregate"])
    aggregate.update({
        "connection_classification_checks": connection["checks"],
        "secp_samples": secp["samples"],
        "secp_distinct_evaluations": secp["distinct_evaluations"],
        "secp_negation_checks": secp["negation_checks"],
        "secp_glv_checks": secp["glv_checks"],
    })

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-CONNECTION-DEFECT-MODULI-DECODER-C53",
        "schema_version": "1.0",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "predecessor": "C52 nonhorizontal deformation gauge boundary",
        "connection_defect_normal_form": {
            "definition": "Delta_k^nabla(G)=nabla([k]G)-k*nabla(G) in invariant-tangent scalar coordinates",
            "functorial_connection": "Delta=0",
            "gauge_change": "Delta^(nabla+h)=Delta^nabla+h(Q)-k*h(G)",
            "anchor_zero_freedom": "if h(G)=0, h(Q) can shift the endpoint defect arbitrarily",
            "known_defect_leakage": "if nabla(G)!=0 and Delta is known, k=(nabla(Q)-Delta)/nabla(G)",
        },
        "new_differential_orbit_state": {
            "base_state": "R(P)=x(P)*dot x_a(P)",
            "derivative_operator": "D_omega=2y*d/dx",
            "U": "U(P)=D_omega R(P)/x(P)^2",
            "V": "V(P)=D_omega^2 R(P)/x(P)",
            "symmetry": {
                "U_negation": "U(-P)=-U(P)",
                "V_negation": "V(-P)=V(P)",
                "U_GLV": "U(phi P)=U(P)",
                "V_GLV": "V(phi P)=V(P)",
            },
            "set_theoretic_result": (
                "(U,V) identifies the target GLV orbit on every declared curve; "
                "anchor/query (U,V) identifies g_G on every marked-generator frozen replay"
            ),
            "not_a_compressed_decoder": (
                "the first exact polynomial and rational decoders appear at the generic interpolation threshold"
            ),
        },
        "carry_root_reduction": {
            "assume": "R(P)=F(T), T=x(P)^3, U=6yF'(T), C_G(T)=g_G(P)y(P)^3",
            "cross_multiplied_identity": "U*C_G(T)=6*g_G(P)*(T+7)^2*F'(T)",
            "consequence": (
                "decoding g from the public differential state still requires the generator-marked carry-root section C_G, up to public normalization"
            ),
        },
        "analysis": analysis,
        "connection_certificate": connection,
        "secp256k1": secp,
        "aggregate": aggregate,
        "claim_boundary": {
            "proved_or_replayed": [
                "the connection-defect gauge and scalar-leakage normal forms",
                "a public fixed-order O(log n) covariant-derivative compiler",
                "negation and GLV covariance through the third derivative",
                "set-theoretic determination of g by anchor/query (U,V) on every marked frozen generator",
                "generic-threshold polynomial and rational interpolation degrees on twelve curves",
                "declared character, field-carry, representation-bit, mu6 and bounded determinant screens",
                "public secp256k1 covariance samples",
            ],
            "not_claimed": [
                "an unrestricted connection or nonlinear-circuit lower bound",
                "a cheap g decoder",
                "a cheap J decoder",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision": {
            "functorial_connection_defect_is_zero": True,
            "connection_defect_is_gauge_coboundary_without_extra_normalization": True,
            "known_nonzero_anchor_defect_reveals_full_scalar": True,
            "public_covariant_derivative_state_found": True,
            "anchor_query_uv_state_determines_g_set_theoretically": True,
            "bounded_declared_decoder_grammars_closed": True,
            "cheap_g_decoder_found": False,
            "cheap_J_decoder_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "DIFFERENTIAL-ORBIT-CARRY-ROOT-COMPILER-C54",
            "target": (
                "construct or exclude a short generator-marked compiler for the normalization converting U(P) into g_G(P), equivalently the carry-root section C_G(T)"
            ),
            "mandatory_gate": (
                "must beat generic interpolation, work for all marked generators, and include all preprocessing, advice, representation, memory and online cost"
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
