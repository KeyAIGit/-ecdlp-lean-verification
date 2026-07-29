#!/usr/bin/env python3
"""Independent validator for the TASK-024 infinity-stratum certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
SIDECAR_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-INFINITY-STRATA-001"
SOURCE_PATH = "Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean"
SOURCE_SHA256 = (
    "1314477f9821da87d2017837abca4fec957ae9998390a231e93532230129a22c"
)
TASK023_ARTIFACT_PATH = (
    "experiments/engine/pkc_smooth_m16_exact_chart_cover/artifact.json"
)
TASK023_ARTIFACT_SHA256 = (
    "934809fabbb8c98c5ed9356a0a1f3367a23f8fbc1bc86239069942537fd678ed"
)
TASK023_SOURCE_PATH = "Ecdlp/Proved/FrozenProjectiveChartSystem.lean"
TASK023_SOURCE_SHA256 = (
    "4f7b95453d8fafba3ec9cae0a9bbad5d8f782c6c0202f6e7cf37e17981b63019"
)

EXPECTED_TOP_LEVEL = {
    "artifact_id",
    "binding_state",
    "depends_on",
    "downstream_open_boundary",
    "kind",
    "local_identity_fixture",
    "mask_pruning_contract",
    "producer_checks",
    "proof_status",
    "schema_version",
    "scope",
    "terminal_disposition",
    "theorem_bindings",
}

EXPECTED_CONTRACT = {
    "adjacent_infinity_consequence": "q(i+2).v^2 = 0",
    "affine_input_assumption": "forall n, (q n).v != 0",
    "boundary_conditions": {
        "slot_0_infinity_implies": "det(q0,q1)=0",
        "slot_13_infinity_implies": "det(q15,y)=0",
    },
    "endpoint_nonzero_assumptions_required_for_377": True,
    "full_mask_count": 16384,
    "full_mask_count_formula": "2^14",
    "interior_separated_mask_count": 377,
    "interior_slot_count": 12,
    "neighbor_forcing": (
        "isolated infinity forces adjacent affine coordinate to q.u/q.v"
    ),
    "production_mask_family_materialized": False,
    "projective_slot_count": 14,
    "separated_mask_count": 987,
    "separated_mask_definition": "no adjacent slots are both in I",
    "stage": 14,
}

EXPECTED_FIXTURE = {
    "fields": [5, 7],
    "full_production_mask_enumeration_executed": False,
    "identity_checks": [
        "H(a,b,infinity)=det(a,b)^2",
        "H(infinity,b,c)=det(b,c)^2",
        "H(a,infinity,c)=det(a,c)^2",
        "H(infinity,b,infinity)=b.v^2",
    ],
    "mask_counts_derived_by_path_recurrence": True,
    "neighbor_coordinate_fixture_exhaustive": True,
    "projective_zero_pair_admitted": False,
}

EXPECTED_PRODUCER = {
    "discrete_log_executed": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
    "full_production_mask_family_enumerated": False,
    "parameter_sweep_executed": False,
    "rank_estimated": False,
    "relation_yield_estimated": False,
    "solver_executed": False,
}

EXPECTED_PROOF_STATUS = {
    "card_infinityMask": "compiler_trusted_native_decide",
    "card_interiorSeparatedInfinityMask": "compiler_trusted_native_decide",
    "card_separatedInfinityMask": "compiler_trusted_native_decide",
    "cover_equivalences": "kernel_checked",
    "forced_neighbor_theorems": "kernel_checked",
    "infinity_identities": "kernel_checked",
    "mask_necessity_theorems": "kernel_checked",
    "solver_rank_yield_cost_claim": "not_claimed",
}

EXPECTED_SCOPE = {
    "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
    "cell": "CELL-M-PKC-SMOOTH-M16",
    "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
    "task": "TASK-024",
}

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "barrier_effect": "necessary_infinity_mask_pruning_closed_only",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "experiment_permission": "none",
    "hypothesis_effect": "none",
    "mask_orchestration_status": "necessary_filter_only",
    "rank_status": "unpriced",
    "retention_disposition": "zero_retention_success",
    "route_effect": "none",
    "route_status": "open_parked",
    "solving_cost_status": "unpriced",
    "yield_status": "unpriced",
}

EXPECTED_THEOREMS = {
    "HValue_first_infinity",
    "HValue_first_third_infinity",
    "HValue_middle_infinity",
    "HValue_third_infinity",
    "card_infinityMask",
    "card_interiorSeparatedInfinityMask",
    "card_separatedInfinityMask",
    "frozenChartCover_iff_admissibleChartCover",
    "frozenChartCover_iff_interiorChartCover",
    "frozenChartSystem_leftInfinity_forces_rightCoordinate",
    "frozenChartSystem_rightInfinity_forces_leftCoordinate",
    "frozenChartSystem_separatedInfinityMask",
    "frozenProjectiveChain_iff_admissibleChartPolynomialCover",
}


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_independent_set_count(length: int) -> int:
    end_affine, end_infinity = 1, 0
    for _ in range(length):
        end_affine, end_infinity = (
            end_affine + end_infinity,
            end_affine,
        )
    return end_affine + end_infinity


def det(a: tuple[int, int], b: tuple[int, int], p: int) -> int:
    return (a[0] * b[1] - a[1] * b[0]) % p


def h_value(
    a: tuple[int, int],
    b: tuple[int, int],
    c: tuple[int, int],
    p: int,
) -> int:
    au, av = a
    bu, bv = b
    cu, cv = c
    value = (
        au**2 * bu**2 * cv**2
        + au**2 * bv**2 * cu**2
        + av**2 * bu**2 * cu**2
        - 2 * au**2 * bu * bv * cu * cv
        - 2 * au * av * bu**2 * cu * cv
        - 2 * au * av * bu * bv * cu**2
        - 28
        * (
            au * av * bv**2 * cv**2
            + av**2 * bu * bv * cv**2
            + av**2 * bv**2 * cu * cv
        )
    )
    return value % p


def validate_local_fixture() -> None:
    require(path_independent_set_count(14) == 987, "14-slot count drift")
    require(path_independent_set_count(12) == 377, "12-slot count drift")
    require(2**14 == 16384, "powerset count drift")
    infinity = (1, 0)
    for p in (5, 7):
        points = [(x, 1) for x in range(p)] + [infinity]
        for a in points:
            for b in points:
                require(
                    h_value(a, b, infinity, p) == det(a, b, p) ** 2 % p,
                    f"third-infinity identity failed over F{p}",
                )
                require(
                    h_value(infinity, a, b, p) == det(a, b, p) ** 2 % p,
                    f"first-infinity identity failed over F{p}",
                )
                require(
                    h_value(a, infinity, b, p) == det(a, b, p) ** 2 % p,
                    f"middle-infinity identity failed over F{p}",
                )
            require(
                h_value(infinity, a, infinity, p) == a[1] ** 2 % p,
                f"double-infinity identity failed over F{p}",
            )
        for u in range(p):
            q = (u, 1)
            right_zeros = [
                t for t in range(p)
                if h_value(infinity, q, (t, 1), p) == 0
            ]
            left_zeros = [
                t for t in range(p)
                if h_value((t, 1), q, infinity, p) == 0
            ]
            require(right_zeros == [u], f"right neighbor drift over F{p}")
            require(left_zeros == [u], f"left neighbor drift over F{p}")


def validate_source(root: Path) -> None:
    source = root / SOURCE_PATH
    require(source.is_file(), "bound Lean source missing")
    require(sha256(source) == SOURCE_SHA256, "bound Lean source SHA drift")
    text = source.read_text(encoding="utf-8")
    require(not re.search(r"\b(?:sorry|admit)\b", text), "proof placeholder")
    require(not re.search(r"(?m)^\s*axiom\b", text), "custom axiom")
    require(not re.search(r"(?m)^\s*unsafe\b", text), "unsafe declaration")
    for theorem in EXPECTED_THEOREMS:
        require(
            re.search(rf"\btheorem\s+{re.escape(theorem)}\b", text)
            is not None,
            f"missing theorem {theorem}",
        )


def validate_document(
    document: dict[str, Any],
    root: Path = ROOT,
    require_final_source_binding: bool = True,
) -> None:
    require(set(document) == EXPECTED_TOP_LEVEL, "top-level schema drift")
    require(document["schema_version"] == 1, "schema version drift")
    require(document["artifact_id"] == ARTIFACT_ID, "artifact id drift")
    require(
        document["kind"] == "source_bound_non_run_certificate",
        "artifact kind drift",
    )
    expected_binding = {
        "artifact_sidecar": "artifact.sha256",
        "digest_match": True,
        "source_path": SOURCE_PATH,
        "source_sha256": SOURCE_SHA256,
        "source_status": "final",
    }
    require(document["binding_state"] == expected_binding, "binding drift")
    expected_dependencies = [
        {
            "digest_match": True,
            "path": TASK023_ARTIFACT_PATH,
            "required_sha256": TASK023_ARTIFACT_SHA256,
        },
        {
            "digest_match": True,
            "path": TASK023_SOURCE_PATH,
            "required_sha256": TASK023_SOURCE_SHA256,
        },
    ]
    require(document["depends_on"] == expected_dependencies, "dependency drift")
    require(document["mask_pruning_contract"] == EXPECTED_CONTRACT, "contract drift")
    require(document["local_identity_fixture"] == EXPECTED_FIXTURE, "fixture drift")
    require(document["producer_checks"] == EXPECTED_PRODUCER, "producer drift")
    require(document["proof_status"] == EXPECTED_PROOF_STATUS, "proof drift")
    require(document["scope"] == EXPECTED_SCOPE, "scope drift")
    require(document["terminal_disposition"] == EXPECTED_TERMINAL, "terminal drift")
    bindings = document["theorem_bindings"]
    require(set(bindings) == EXPECTED_THEOREMS, "theorem binding set drift")
    for name, declaration in bindings.items():
        require(
            declaration == f"Ecdlp.FrozenProjectiveSemaev.{name}",
            f"declaration drift for {name}",
        )
    boundary = document["downstream_open_boundary"]
    require(len(boundary["closed_here"]) == 7, "closed-here drift")
    require(len(boundary["not_claimed"]) == 5, "nonclaim drift")
    require(
        boundary["remaining_blocker"]
        == (
            "necessary mask pruning is closed, but sufficient orchestration, "
            "relation yield and rank, solving, recovery, and complete cost "
            "remain open"
        ),
        "remaining blocker drift",
    )
    validate_local_fixture()
    for dependency in expected_dependencies:
        path = root / dependency["path"]
        require(path.is_file(), f"dependency missing: {dependency['path']}")
        require(
            sha256(path) == dependency["required_sha256"],
            f"dependency SHA drift: {dependency['path']}",
        )
    if require_final_source_binding:
        validate_source(root)


def validate_sidecar() -> None:
    require(SIDECAR_PATH.is_file(), "artifact sidecar missing")
    expected = f"{sha256(ARTIFACT_PATH)}  artifact.json"
    require(SIDECAR_PATH.read_text(encoding="utf-8").strip() == expected,
            "artifact sidecar drift")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-final-source-binding", action="store_true")
    args = parser.parse_args()
    try:
        document = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        validate_document(
            document,
            require_final_source_binding=args.require_final_source_binding,
        )
        validate_sidecar()
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"TASK-024 infinity-stratum certificate FAILED: {exc}", file=sys.stderr)
        return 1
    print("TASK-024 infinity-stratum certificate PASSED")
    print("mask counts: full=16384 affine-separated=987 endpoint-pruned=377")
    print("F5/F7 identities and forced-neighbor fixtures: PASS")
    print(
        "solver, rank, yield, recovery, cost, authorization, retention, "
        "and promotion remain absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
