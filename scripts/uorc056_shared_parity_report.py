#!/usr/bin/env python3
"""Machine-readable V19 research report."""
from __future__ import annotations

from typing import Any

from uorc056_shared_parity_cauchy_core import verify_exhaustive_cauchy_minors
from uorc056_shared_parity_records import (
    EXHAUSTIVE_CAUCHY_ORDERS,
    FROZEN_INSTANCES,
    cycle_record,
    secp256k1_record,
)

PROFILE_ID = "UORC-056-SHARED-PARITY-CAUCHY-BARRIER-V19"


def run() -> dict[str, Any]:
    exhaustive = [verify_exhaustive_cauchy_minors(n) for n in EXHAUSTIVE_CAUCHY_ORDERS]
    rows = [cycle_record(*instance) for instance in FROZEN_INSTANCES]
    exhaustive_total = sum(row["minors_checked"] for row in exhaustive)
    sampled_total = sum(row["sampled_cauchy"]["sampled_minors"] for row in rows)
    if exhaustive_total != 6895 or sampled_total != 160 or len(rows) != 5:
        raise AssertionError("frozen replay totals drifted")
    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_identity": "sigma_G(Q)=g_G(Q)*J_G(x(Q))=(-1)^k for Q=[k]G",
        "direct_parity_spectrum": {
            "formula": "sigmahat(r)=2/(1+zeta^(-r)) for odd n",
            "free_identity_formula": "Fhat(r)=2/(1+zeta^(-r))+d",
            "lower_bound": "|supp(Fhat)|>=n-1",
            "exact_witness": "F(0)=0 and F(k)=(-1)^k for k!=0",
        },
        "one_bilinear_gate": {
            "model": "F=A*B for sparse additive-character sums A,B",
            "separate_support": "|S_A|*|S_B|>=n-1",
            "leaf_sum": "|S_A|+|S_B|>=ceil(2*sqrt(n-1))",
            "shared_dictionary": "|T|(|T|+1)/2>=n-1",
        },
        "direct_sparse_rational": {
            "model": "A(k)/B(k)=(-1)^k and B(k)!=0 for every k!=0",
            "defect": "A=sigma*B+d*delta_0",
            "Fourier_system": "Ahat(r)=(1/n)*sum_s 2*Bhat(s)/(1+zeta^(s-r))+d",
            "Cauchy_nodes": "x_r=zeta^(-r), y_s=zeta^s, defect column y=0",
            "free_identity_result": "|S_A|+|S_B|>=n",
            "exact_witness": "B=1; A(0)=0 and A(k)=(-1)^k for k!=0",
            "canonical_identity_result": "|S_A|+|S_B|>=n+1",
            "shared_union_result": "|S_A union S_B|>=ceil(n/2)",
        },
        "secp256k1": secp256k1_record(),
        "finite_field_replay": {
            "exhaustive_cauchy_minors": exhaustive_total,
            "sampled_cauchy_minors_on_frozen_orders": sampled_total,
            "canonical_and_free_identity_DFT_checks": len(rows),
            "failures": 0,
            "exhaustive": exhaustive,
            "frozen": [
                {
                    "id": row["id"],
                    "n": row["n"],
                    "canonical_support": row["canonical_parity_spectrum_support"],
                    "free_identity_support": row["free_identity_parity_support"],
                    "rational_total_bound": row["direct_rational_total_support_lower_bound"],
                    "rational_union_bound": row["direct_rational_shared_union_lower_bound"],
                    "bilinear_leaf_sum_bound": row["bilinear_leaf_sum_lower_bound"],
                    "sampled_minors": row["sampled_cauchy"]["sampled_minors"],
                }
                for row in rows
            ],
        },
        "closed_classes": [
            "one bilinear product with o(sqrt(n)) expanded leaf support",
            "one sparse character quotient with o(n) separate or union support",
        ],
        "remaining_frontier": [
            "deeper nonlinear implicit-spectrum circuits",
            "modular composition and transposed evaluation",
            "recurrence-compressed GLV-Kummer objects",
            "p-adic, theta, elliptic-unit, and other non-spectral representations",
        ],
        "scientific_boundary": (
            "No public parity evaluator, sub-square-root ECDLP algorithm, or "
            "unrestricted arithmetic-circuit lower bound is claimed."
        ),
    }
