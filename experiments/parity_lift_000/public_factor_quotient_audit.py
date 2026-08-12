#!/usr/bin/env python3
"""Cross-family admission audit for PUBLIC-FACTOR-QUOTIENT-AUDIT-021.

The audit consumes only JSON emitted by frozen toy screens. It does not accept
an external curve, point, key, wallet, or production-sized target.

An exact R3 match is classified only after quotienting the public normalized
C3 orbit factor. For point-scale sign s=+1, R3 is already public and the
quotient is constant. For s=-1, the quotient is the GLV carry and an exact R3
match is genuinely hard-branch positive.

The audit also enforces scale and repetition gates for exact carry matches,
matched-null exceedances, inverse-log Fourier coefficients, and held-out
higher-character lookup tables.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCALE_ORDER_FLOOR = 271
LARGE_ORDER_FLOOR = 500
REPEATED_CASES_REQUIRED = 2


@dataclass(frozen=True)
class FamilyCase:
    family: str
    p: int
    order: int
    point_scale_character: int
    exact_carry_decoder: str | None
    exact_r3_decoder: str | None
    exact_carry_classification: str
    exact_r3_classification: str
    carry_best_accuracy: float
    carry_null_q95: float
    carry_strictly_above_null_q95: bool
    r3_best_accuracy: float
    r3_null_q95: float
    r3_strictly_above_null_q95: bool
    best_spectral_candidate: str
    best_spectral_coefficient: float
    inverse_log_threshold: float
    spectral_ge_inverse_log: bool


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_case(family: str, case: dict[str, Any]) -> FamilyCase:
    order = int(case["order"])
    scale = int(case["point_scale_character"])
    exact_carry = case["exact_carry_decoder"]
    exact_r3 = case["exact_r3_decoder"]

    if exact_carry is None:
        carry_class = "none"
    elif order < SCALE_ORDER_FLOOR:
        carry_class = "small_order_resonance"
    else:
        carry_class = "scale_qualified_exact_carry"

    if exact_r3 is None:
        r3_class = "none"
    elif scale == 1:
        r3_class = "public_factor_tautology"
    elif scale == -1:
        r3_class = "hard_branch_carry_equivalent"
    else:
        raise AssertionError("point-scale character was not binary")

    carry_best = float(case["best_carry_accuracy"])
    carry_q95 = float(case["carry_null_q95"])
    r3_best = float(case["best_r3_accuracy"])
    r3_q95 = float(case["r3_null_q95"])
    spectral = float(case["best_spectral_coefficient"])
    inverse_log = 1.0 / math.log(order)

    return FamilyCase(
        family=family,
        p=int(case["p"]),
        order=order,
        point_scale_character=scale,
        exact_carry_decoder=exact_carry,
        exact_r3_decoder=exact_r3,
        exact_carry_classification=carry_class,
        exact_r3_classification=r3_class,
        carry_best_accuracy=carry_best,
        carry_null_q95=carry_q95,
        carry_strictly_above_null_q95=(
            order >= LARGE_ORDER_FLOOR and carry_best > carry_q95
        ),
        r3_best_accuracy=r3_best,
        r3_null_q95=r3_q95,
        r3_strictly_above_null_q95=(
            order >= LARGE_ORDER_FLOOR and r3_q95 > 0 and r3_best > r3_q95
        ),
        best_spectral_candidate=str(case["best_spectral_candidate"]),
        best_spectral_coefficient=spectral,
        inverse_log_threshold=inverse_log,
        spectral_ge_inverse_log=(
            order >= LARGE_ORDER_FLOOR and spectral >= inverse_log
        ),
    )


def family_summary(rows: list[FamilyCase]) -> dict[str, Any]:
    return {
        "cases": len(rows),
        "scale_qualified_exact_carry_orders": [
            row.order
            for row in rows
            if row.exact_carry_classification == "scale_qualified_exact_carry"
        ],
        "small_order_exact_carry_orders": [
            row.order
            for row in rows
            if row.exact_carry_classification == "small_order_resonance"
        ],
        "hard_branch_exact_r3_orders": [
            row.order
            for row in rows
            if row.exact_r3_classification == "hard_branch_carry_equivalent"
        ],
        "public_factor_exact_r3_orders": [
            row.order
            for row in rows
            if row.exact_r3_classification == "public_factor_tautology"
        ],
        "large_carry_null_exceedance_orders": [
            row.order for row in rows if row.carry_strictly_above_null_q95
        ],
        "large_r3_null_exceedance_orders": [
            row.order for row in rows if row.r3_strictly_above_null_q95
        ],
        "large_inverse_log_spectral_orders": [
            row.order for row in rows if row.spectral_ge_inverse_log
        ],
    }


def repeated_signal(summary: dict[str, Any]) -> bool:
    return any(
        len(summary[key]) >= REPEATED_CASES_REQUIRED
        for key in (
            "large_carry_null_exceedance_orders",
            "large_r3_null_exceedance_orders",
            "large_inverse_log_spectral_orders",
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-results", type=Path, required=True)
    parser.add_argument("--point-results", type=Path, required=True)
    parser.add_argument("--seventh-results", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "public_factor_quotient_audit_results.json"
        ),
    )
    args = parser.parse_args()

    trace_data = read_json(args.trace_results)
    point_data = read_json(args.point_results)
    seventh_data = read_json(args.seventh_results)

    trace_rows = [
        classify_case("trace_cm_index", case) for case in trace_data["cases"]
    ]
    point_rows = [
        classify_case("point_function_orientation", case)
        for case in point_data["cases"]
    ]
    rows = trace_rows + point_rows

    trace_summary = family_summary(trace_rows)
    point_summary = family_summary(point_rows)
    summaries = {
        "trace_cm_index": trace_summary,
        "point_function_orientation": point_summary,
    }

    scale_exact_carry = [
        row for row in rows
        if row.exact_carry_classification == "scale_qualified_exact_carry"
    ]
    hard_r3 = [
        row for row in rows
        if row.exact_r3_classification == "hard_branch_carry_equivalent"
    ]
    public_r3 = [
        row for row in rows
        if row.exact_r3_classification == "public_factor_tautology"
    ]
    small_carry = [
        row for row in rows
        if row.exact_carry_classification == "small_order_resonance"
    ]
    seventh_admitted = list(seventh_data["aggregate"]["admitted_variants"])

    admitted_routes: list[str] = []
    if scale_exact_carry:
        admitted_routes.append("scale_qualified_exact_carry")
    if hard_r3:
        admitted_routes.append("hard_branch_exact_r3")
    for family, summary in summaries.items():
        if repeated_signal(summary):
            admitted_routes.append(f"{family}:repeated_statistical_or_spectral_signal")
    if seventh_admitted:
        admitted_routes.append("held_out_seventh_character_lookup")

    trace_public_orders = set(trace_summary["public_factor_exact_r3_orders"])
    point_public_orders = set(point_summary["public_factor_exact_r3_orders"])
    plus_orders_trace = {
        row.order for row in trace_rows if row.point_scale_character == 1
    }
    plus_orders_point = {
        row.order for row in point_rows if row.point_scale_character == 1
    }

    payload = {
        "scope": (
            "frozen toy screens only; no external curve, point, key, wallet, "
            "or production-sized target"
        ),
        "package": "PUBLIC-FACTOR-QUOTIENT-AUDIT-021",
        "quotient_rule": (
            "for exact R3 candidates, divide by the public normalized C3 orbit "
            "factor before classification; s=+1 leaves the constant quotient, "
            "s=-1 leaves the GLV carry"
        ),
        "scale_order_floor": SCALE_ORDER_FLOOR,
        "large_order_floor": LARGE_ORDER_FLOOR,
        "repeated_cases_required": REPEATED_CASES_REQUIRED,
        "family_cases": [asdict(row) for row in rows],
        "family_summaries": summaries,
        "higher_character_summary": {
            "held_out_cases": seventh_data["aggregate"]["held_out_cases"],
            "largest_order": seventh_data["aggregate"]["largest_order"],
            "admitted_variants": seventh_admitted,
            "variant_summary": seventh_data["variant_summary"],
        },
        "aggregate": {
            "family_cases": len(rows),
            "scale_qualified_exact_carry_matches": len(scale_exact_carry),
            "hard_branch_exact_r3_matches": len(hard_r3),
            "public_factor_exact_r3_matches": len(public_r3),
            "small_order_exact_carry_matches": len(small_carry),
            "held_out_seventh_character_admitted_variants": len(
                seventh_admitted
            ),
            "trace_public_r3_orders_equal_scale_plus_orders": (
                trace_public_orders == plus_orders_trace
            ),
            "point_public_r3_orders_equal_scale_plus_orders": (
                point_public_orders == plus_orders_point
            ),
            "all_exact_r3_matches_explained_by_public_factor": all(
                row.exact_r3_classification
                in ("none", "public_factor_tautology")
                for row in rows
            ),
            "admitted_routes": admitted_routes,
        },
        "corrected_decision": (
            "No route survives the public-factor quotient, scale floor, "
            "repetition requirement, and held-out higher-character gate."
            if not admitted_routes
            else "At least one quotient-qualified route requires manual review."
        ),
        "remaining_frontier": [
            "integer orientations of the public point function Phi with growing algebraic conductor",
            "higher-order field characters not covered by the seventh-character held-out screen",
            "order-dependent public sections after explicit public-factor quotienting",
            "a direct public cyclotomic carry or hard-branch R3 decoder",
        ],
        "claim_boundary": [
            "The audit reclassifies outputs of finite screens; it is not an asymptotic lower bound.",
            "An s=+1 exact R3 match is not discarded numerically, but classified as an already-public factor identity.",
            "Small-order exact carry matches remain regression resonances, not scaling evidence.",
            "No public carry, EDS-residue, parity, or ECDLP oracle is constructed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
