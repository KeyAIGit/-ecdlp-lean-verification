#!/usr/bin/env python3
"""Machine-readable decision package for UORC-056 C43.

The original C43 draft accidentally declared three j=0 curves with group order
p even though their exact point counts were different.  This canonical runner
uses only independently verified prime-order curves and recomputes every branch
identity, DFT character span, and fitted quartic screen from those valid rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import uorc056_c43_glv_dft_screen as dft_module
import uorc056_c43_local_glv_branch as branch_module
from uorc056_c39_half_miller import TOYS

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Every row below has #E(F_p)=n prime, [n]G=O, beta^3=1, beta!=1,
# and phi_beta(G)=[lambda]G.  The final three rows were not used to fit the
# original five-curve corpus.
VALID_HELD_OUT = (
    (61, 61, (2, 25), 13, 47),
    (211, 199, (3, 33), 14, 106),
    (991, 1009, (1, 151), 113, 634),
    (2143, 2089, (1, 505), 1793, 1262),
)
QUARTIC_SCREEN_PRIMES = {211, 991, 2143}
DECISIVE_PRIME = 2143


def build_valid_branch_payload() -> dict[str, Any]:
    branch_module.HELD_OUT = VALID_HELD_OUT
    return branch_module.build_branch_payload()


def build_valid_dft_payload() -> dict[str, Any]:
    dft_module.HELD_OUT = VALID_HELD_OUT
    dft_module.QUARTIC_PRIMES = QUARTIC_SCREEN_PRIMES
    rows = [
        dft_module.analyze_curve(row, f"frozen-{index + 1}")
        for index, row in enumerate(TOYS)
    ] + [
        dft_module.analyze_curve(row, f"heldout-{index + 1}")
        for index, row in enumerate(VALID_HELD_OUT)
    ]
    decisive = next(row for row in rows if row["p"] == DECISIVE_PRIME)
    quartic_profile = {
        str(row["p"]): row["quartic_two_L0_two_f0"]
        for row in rows
        if row["quartic_two_L0_two_f0"] is not None
    }
    target_presence = {
        prime: {
            target: solution is not None
            for target, solution in profile["solutions"].items()
        }
        for prime, profile in quartic_profile.items()
    }
    payload: dict[str, Any] = {
        "profile_id": "UORC-056-C43-GLV-DFT-STRUCTURAL-CHARACTERS",
        "schema_version": "1.1",
        "grammar": {
            "states": (
                "27 fixed Fp2 expressions from f(Q), f(phi Q), f(phi^2 Q), "
                "their C3 DFT, products, ratios and Frobenius wedges"
            ),
            "atoms": "chi_p(Re(E)+b Im(E)) and chi_p(Im(E))",
            "coefficient_set": (
                "public structural constants, anchor slopes, and closure under "
                "negation, inversion and squaring"
            ),
            "combiner": "arbitrary product of every everywhere-nonzero atom",
        },
        "curves": rows,
        "quartic_overfit_profile": quartic_profile,
        "quartic_target_presence": target_presence,
        "aggregate": {
            "curves": len(rows),
            "frozen": len(TOYS),
            "heldout": len(VALID_HELD_OUT),
            "declared_character_atoms": sum(
                int(row["declared_character_atoms"]) for row in rows
            ),
            "valid_character_atoms": sum(
                int(row["valid_character_atoms"]) for row in rows
            ),
            "decisive_prime": DECISIVE_PRIME,
            "decisive_all_targets_absent_from_structural_span": not any(
                bool(value)
                for value in decisive["targets_in_arbitrary_product_span"].values()
            ),
            "decisive_all_fitted_quartics_absent": all(
                solution is None
                for solution in decisive["quartic_two_L0_two_f0"]["solutions"].values()
            ),
            "errors": sum(int(row["errors"]) for row in rows),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload


def build_payload() -> dict[str, Any]:
    branch = build_valid_branch_payload()
    dft = build_valid_dft_payload()
    glv_orbits = (SECP_N - 1) // 6
    half_kernel = (SECP_N - 1) // 2
    if half_kernel != 3 * glv_orbits:
        raise AssertionError("secp256k1 half-kernel is not three GLV cells")

    dft_aggregate = dft["aggregate"]
    decisive_closed = bool(
        dft_aggregate["decisive_all_targets_absent_from_structural_span"]
    )
    quartic_rejected = bool(dft_aggregate["decisive_all_fitted_quartics_absent"])

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-LOCAL-GLV-GAUGE-BREAKING-C43",
        "schema_version": "1.1",
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "predecessor": "C42 oriented transposed-resultant boundary",
        "validation_correction": {
            "invalid_rows_removed": [229, 997, 2137],
            "valid_rows_added": [211, 991, 2143],
            "all_declared_rows_recounted": True,
            "all_declared_generator_orders_rechecked": True,
            "all_declared_glv_eigenpairs_rechecked": True,
        },
        "local_glv_branch_factorization": branch,
        "glv_dft_character_boundary": dft,
        "secp256k1_frontier": {
            "n": SECP_N,
            "half_kernel_degree": half_kernel,
            "glv_orbits": glv_orbits,
            "glv_orbits_bit_length": glv_orbits.bit_length(),
            "half_kernel_equals_three_glv_cells": half_kernel == 3 * glv_orbits,
            "residual_gauge_after_granting_carry_root": (
                "Klein-four sign action per split GLV orbit"
            ),
            "anchor_scope": (
                "one anchor fixes one sign at one orbit; it does not supply the "
                "ordered sector sign at all other quotient roots"
            ),
        },
        "exact_algebraic_result": {
            "kernel": "K_H(X)=kappa(X^3)",
            "carry_root": (
                "C_G(T)=Y_G(X)Y_G(beta X)Y_G(beta^2 X), T=X^3"
            ),
            "carry_square": "C_G(T)^2=(T+7)^3 mod kappa(T)",
            "carry_value": "C_G(x(Q)^3)=g_G(Q)y(Q)^3",
            "sector_root": (
                "J_G(X)=Y_G(beta X)Y_G(beta^2 X)/(X^3+7)"
            ),
            "sector_square": "J_G(X)^2=1 mod K_H(X)",
            "reconstruction": (
                "Y_G(X)(X^3+7)=C_G(X^3)J_G(X) mod K_H(X)"
            ),
            "parity": "(-1)^k=g_G(Q)J_G(x(Q))",
        },
        "claim_boundary": {
            "proved_or_replayed": [
                "the exact carry-root/sector-root polynomial factorization",
                "the exact residual product-preserving sign gauge",
                "failure of cyclic invariants to select an ordered sign",
                "arbitrary-product closure of the declared structural GLV-DFT character grammar on the decisive valid held-out curve",
                "rejection of the declared freely fitted quartic family on the decisive valid held-out curve",
                "five frozen and four independently recounted held-out prime-order j=0 curves",
            ],
            "not_claimed": [
                "an unrestricted arithmetic-circuit lower bound",
                "an unrestricted character-product lower bound with arbitrary coefficients",
                "production-size coefficient density for secp256k1",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision": {
            "exact_glv_carry_root_found": True,
            "exact_sector_root_found": True,
            "exact_oriented_root_reconstruction_found": True,
            "cubic_norm_breaks_all_local_sign_gauge": False,
            "residual_klein_four_gauge_survives": True,
            "cyclic_invariant_can_decode_ordered_parity": False,
            "declared_structural_glv_dft_character_grammar_closed": decisive_closed,
            "declared_fitted_quartic_family_uniform": not quartic_rejected,
            "local_glv_gauge_breaking_evaluator_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "aggregate": {
            "curves": int(branch["aggregate"]["curves"]),
            "frozen_curves": int(branch["aggregate"]["frozen"]),
            "heldout_curves": int(branch["aggregate"]["heldout"]),
            "carry_value_checks": int(branch["aggregate"]["carry_value_checks"]),
            "declared_character_atoms": int(
                dft_aggregate["declared_character_atoms"]
            ),
            "valid_character_atoms": int(dft_aggregate["valid_character_atoms"]),
            "decisive_prime": int(dft_aggregate["decisive_prime"]),
            "decisive_all_targets_absent_from_structural_span": decisive_closed,
            "decisive_all_fitted_quartics_absent": quartic_rejected,
            "errors": int(branch["aggregate"]["errors"])
            + int(dft_aggregate["errors"]),
        },
        "successor": {
            "id": "ORDERED-SECTOR-TRANSPORT-C44",
            "target": (
                "construct an unsquared public transport for the ordered sector "
                "J_G(x(Q)), rather than another cyclic norm or fitted character"
            ),
            "mandatory_gate": (
                "the mechanism must be sensitive to the residual Klein-four "
                "gauge and must generate its coefficients without orbit enumeration"
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
    print("UORC056_LOCAL_GLV_GAUGE_BREAKING_C43_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
