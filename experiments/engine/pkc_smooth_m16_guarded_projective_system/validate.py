#!/usr/bin/env python3
"""Validate the narrow TASK-022 guarded projective-system certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-GUARDED-PROJECTIVE-SYSTEM-001"
ARTIFACT_KIND = "non_run_kernel_binding_certificate"
SOURCE_PATH = "Ecdlp/Proved/FrozenProjectiveGuardSystem.lean"
TASK021_PATH = (
    "experiments/engine/pkc_smooth_m16_frozen_projective_witness/artifact.json"
)
PENDING_SOURCE_SHA256 = "__TASK022_" + "LEAN_SHA256__"
SOURCE_SHA256 = (
    "37feeef48e77437b44b6ae6dd4750782e19ecd824e3ea2e73b657e2fb8296fb9"
)

EXPECTED_DEPENDENCIES = {
    TASK021_PATH:
        "89c645545d89334473d51654a41ff7ec2364857d034c64ce08d505337fa1e2d4",
    SOURCE_PATH: SOURCE_SHA256,
}

EXPECTED_ASSUMPTIONS = {
    "coefficient_map": "phi : k ->+* K is injective",
    "guard_semantics":
        "A*U+B*V-1=0 has a solution (A,B) exactly when U!=0 or V!=0",
    "no_base_field_descent":
        "all guarded witness variables live in K; no descent to k is claimed",
    "projective_domain":
        "[0:0] is excluded and [1:0] is retained at every guarded slot",
    "source_coefficients": "the source uses a Field k",
    "system_semantics":
        "FrozenGuardedProjectiveSystem is directly an existential GuardVar "
        "assignment making every indexed guardedEquation polynomial vanish, "
        "not a parallel recursive syntax",
    "target_coefficients":
        "the target uses a Field K with IsAlgClosed K",
}

EXPECTED_SYSTEM = {
    "equation_families": {
        "H": {
            "count": 15,
            "degree_upper_bound": 4,
        },
        "guard": {
            "count": 14,
            "degree_upper_bound": 2,
        },
    },
    "exact_total_degree_claimed": False,
    "guard_equation": "A*U+B*V-1=0",
    "leaf_count": 16,
    "projective_slot_count": 14,
    "stage": 14,
    "total_degree_upper_bound": 4,
    "total_equation_count": 29,
    "total_variable_count": 56,
    "variable_coordinates_per_slot": ["U", "V", "A", "B"],
    "variables_per_projective_slot": 4,
}

EXPECTED_FIXTURE = {
    "assignment_order": ["U", "V", "A", "B"],
    "distinguished_infinity_pair": [1, 0],
    "distinguished_infinity_pair_allowed": True,
    "exhaustive_assignment_count": 625,
    "field_prime": 5,
    "guard_equation": "A*U+B*V-1=0",
    "guard_solution_count": 120,
    "nonzero_coordinate_pair_count": 24,
    "solutions_per_nonzero_coordinate_pair": 5,
    "zero_pair": [0, 0],
    "zero_pair_rejected": True,
}

EXPECTED_PROOF_STATUS = {
    "base_field_descent": "not_claimed",
    "card_guardVar_fourteen": "compiler_trusted_native_decide",
    "card_guarded_equations_fourteen": "compiler_trusted_native_decide",
    "expanded_S17_polynomial": "not_claimed",
    "frozenProjectiveChain_iff_guardedProjectiveSystem": "kernel_checked",
    "frozenRecS17_iff_guardedProjectiveSystem_over": "kernel_checked",
    "FrozenGuardedProjectiveSystem": "kernel_checked_definition",
    "guardEquation": "kernel_checked_definition",
    "guardedEquation": "kernel_checked_definition",
    "guardedEquation_totalDegree_le_four": "kernel_checked",
    "literal_polynomial_family_direct_vanishing_semantics":
        "kernel_checked",
    "parallel_recursive_syntax_as_system_definition": "not_used",
    "solving_rank_yield_cost_claim": "not_claimed",
}

EXPECTED_PRODUCER = {
    "C16_evaluated": False,
    "S17_expanded": False,
    "discrete_log_executed": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
    "guarded_scalar_representation_materialized": True,
    "parameter_sweep_executed": False,
    "solver_input_emitted": False,
    "solver_executed": False,
}

EXPECTED_CLOSED_HERE = [
    "stage-14 frozen RecS17 is equivalent, after an injective coefficient "
    "map into an algebraically closed target, to the guarded scalar "
    "projective system",
    "FrozenGuardedProjectiveSystem is directly the vanishing locus of the "
    "literal finite guardedEquation family under an existential scalar "
    "assignment, not a parallel recursive syntax",
    "the stage-14 guarded scalar projective system is equivalent to "
    "FrozenProjectiveChain",
    "four scalar variables for each of fourteen projective witness slots "
    "give 56 variables",
    "fifteen H equations and fourteen guard equations give 29 equations",
    "every guarded equation has total degree at most four",
    "the guard equation excludes [0:0] and retains [1:0]",
]

EXPECTED_NOT_CLAIMED = [
    "base-field descent or rationality of intermediate witnesses",
    "an expanded or evaluated S17 polynomial",
    "independence of the 29 equations or removal of projective and guard "
    "redundancy",
    "relation yield, rank, solving degree, fill-in, memory, recovery cost, "
    "or total work",
    "a solver run, parameter sweep, exact-target search, or discrete-log "
    "execution",
    "experiment authorization, hypothesis retention, or route promotion",
]

EXPECTED_REMAINING_BLOCKER = (
    "solver-ready chart or gauge handling without counting guard and "
    "projective redundancy as independent relations, followed by yield, "
    "rank, solving, recovery, and total-cost validation"
)

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "barrier_effect":
        "literal_finite_polynomial_representation_materialized_"
        "cost_bridge_open",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "experiment_permission": "none",
    "hypothesis_effect": "none",
    "rank_status": "unpriced",
    "remaining_blocker":
        "solver-ready chart or gauge handling, relation yield and rank, "
        "solving and recovery behavior, and complete end-to-end cost",
    "representation_status":
        "literal_finite_polynomial_vanishing_family_closed",
    "retention_disposition": "zero_retention_success",
    "route_effect": "none",
    "route_status": "open_parked",
    "solving_cost_status": "unpriced",
    "yield_status": "unpriced",
}

EXPECTED_THEOREMS = {
    "card_guardVar_fourteen": (
        "Ecdlp.FrozenProjectiveSemaev.card_guardVar_fourteen",
        "compiler_trusted_native_decide",
        "theorem",
    ),
    "card_guarded_equations_fourteen": (
        "Ecdlp.FrozenProjectiveSemaev.card_guarded_equations_fourteen",
        "compiler_trusted_native_decide",
        "theorem",
    ),
    "frozenProjectiveChain_iff_guardedProjectiveSystem": (
        "Ecdlp.FrozenProjectiveSemaev."
        "frozenProjectiveChain_iff_guardedProjectiveSystem",
        "kernel_checked",
        "theorem",
    ),
    "frozenRecS17_iff_guardedProjectiveSystem_over": (
        "Ecdlp.FrozenProjectiveSemaev."
        "frozenRecS17_iff_guardedProjectiveSystem_over",
        "kernel_checked",
        "theorem",
    ),
    "guardEquation": (
        "Ecdlp.FrozenProjectiveSemaev.guardEquation",
        "kernel_checked",
        "def",
    ),
    "guarded_equation_family": (
        "Ecdlp.FrozenProjectiveSemaev.guardedEquation",
        "kernel_checked",
        "def",
    ),
    "guardedEquation_totalDegree_le_four": (
        "Ecdlp.FrozenProjectiveSemaev."
        "guardedEquation_totalDegree_le_four",
        "kernel_checked",
        "theorem",
    ),
    "guarded_projective_system": (
        "Ecdlp.FrozenProjectiveSemaev.FrozenGuardedProjectiveSystem",
        "kernel_checked",
        "def",
    ),
}

EXPECTED_TOP_LEVEL_KEYS = {
    "artifact_id",
    "assumption_contract",
    "depends_on",
    "downstream_open_boundary",
    "finite_field_fixture",
    "guarded_system_contract",
    "kernel_contract",
    "kind",
    "producer_checks",
    "proof_status",
    "schema_version",
    "scope",
    "terminal_disposition",
    "theorem_bindings",
}


class ValidationError(RuntimeError):
    """Raised when a certificate binding or semantic invariant is invalid."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    )


def enumerate_f5_guard() -> dict[str, Any]:
    prime = 5
    assignments = 0
    solutions: list[tuple[int, int, int, int]] = []
    completions: dict[tuple[int, int], int] = {}
    for u, v, a, b in itertools.product(range(prime), repeat=4):
        assignments += 1
        if (a * u + b * v - 1) % prime == 0:
            solutions.append((u, v, a, b))
            completions[(u, v)] = completions.get((u, v), 0) + 1
    infinity_allowed = any(u == 1 and v == 0 for u, v, _, _ in solutions)
    zero_rejected = not any(u == 0 and v == 0 for u, v, _, _ in solutions)
    return {
        "assignments": assignments,
        "solutions": len(solutions),
        "nonzero_pairs": len(completions),
        "completion_counts": set(completions.values()),
        "infinity_allowed": infinity_allowed,
        "zero_rejected": zero_rejected,
    }


def validate_f5_fixture(fixture: dict[str, Any]) -> None:
    require(fixture == EXPECTED_FIXTURE, "F5 fixture metadata drift")
    observed = enumerate_f5_guard()
    require(observed["assignments"] == 625,
            "F5 exhaustive assignment count is not 625")
    require(observed["solutions"] == 120,
            "F5 guard solution count is not 120")
    require(observed["nonzero_pairs"] == 24,
            "F5 nonzero coordinate-pair count is not 24")
    require(observed["completion_counts"] == {5},
            "F5 guard must have five completions per nonzero pair")
    require(observed["infinity_allowed"] is True,
            "F5 guard rejected [1:0]")
    require(observed["zero_rejected"] is True,
            "F5 guard accepted [0:0]")


def validate_document(document: dict[str, Any]) -> None:
    require(set(document) == EXPECTED_TOP_LEVEL_KEYS,
            "top-level certificate field drift")
    require(document.get("artifact_id") == ARTIFACT_ID,
            "wrong artifact id")
    require(document.get("schema_version") == 1,
            "wrong schema version")
    require(document.get("kind") == ARTIFACT_KIND,
            "wrong artifact kind")
    require(document.get("assumption_contract") == EXPECTED_ASSUMPTIONS,
            "assumption contract drift")
    require(document.get("guarded_system_contract") == EXPECTED_SYSTEM,
            "guarded system contract drift")
    validate_f5_fixture(document.get("finite_field_fixture", {}))
    require(document.get("proof_status") == EXPECTED_PROOF_STATUS,
            "proof-status drift")
    require(document.get("producer_checks") == EXPECTED_PRODUCER,
            "producer or non-execution contract drift")
    require(document.get("terminal_disposition") == EXPECTED_TERMINAL,
            "terminal disposition or nonauthorization drift")

    boundary = document.get("downstream_open_boundary")
    require(isinstance(boundary, dict),
            "downstream boundary must be an object")
    require(boundary.get("closed_here") == EXPECTED_CLOSED_HERE,
            "closed_here drift")
    require(boundary.get("not_claimed") == EXPECTED_NOT_CLAIMED,
            "not_claimed boundary drift")
    require(boundary.get("remaining_blocker") == EXPECTED_REMAINING_BLOCKER,
            "remaining blocker drift")
    require(set(boundary) == {"closed_here", "not_claimed",
                              "remaining_blocker"},
            "downstream boundary field drift")

    dependencies = document.get("depends_on")
    require(isinstance(dependencies, list),
            "dependencies must be a list")
    require(
        [item.get("path") for item in dependencies]
        == list(EXPECTED_DEPENDENCIES),
        "dependency path or order drift",
    )
    require(SOURCE_SHA256 != PENDING_SOURCE_SHA256,
            "canonical TASK-022 source binding is still pending")
    require(is_sha256(SOURCE_SHA256),
            "canonical TASK-022 source digest is malformed")
    for item in dependencies:
        path = item["path"]
        expected = EXPECTED_DEPENDENCIES[path]
        require(item.get("required_sha256") == expected,
                f"required digest drift for {path}")
        require(item.get("observed_sha256") == expected,
                f"observed digest drift for {path}")
        require(item.get("digest_match") is True,
                f"digest match not asserted for {path}")
        actual = sha256(REPO_ROOT / path)
        require(actual == expected,
                f"repository digest mismatch for {path}")

    bindings = document.get("theorem_bindings")
    require(isinstance(bindings, dict),
            "theorem bindings must be an object")
    require(set(bindings) == set(EXPECTED_THEOREMS),
            "theorem-binding key drift")
    source_text = (REPO_ROOT / SOURCE_PATH).read_text(encoding="utf-8")
    for key, (declaration, status, shape) in EXPECTED_THEOREMS.items():
        binding = bindings[key]
        require(
            binding == {
                "declaration": declaration,
                "kernel_status": status,
                "source_path": SOURCE_PATH,
                "source_shape": shape,
            },
            f"theorem binding drift for {key}",
        )
        short_name = declaration.rsplit(".", 1)[-1]
        require(
            re.search(
                rf"^(?:noncomputable )?{re.escape(shape)} "
                rf"{re.escape(short_name)}\b",
                source_text,
                flags=re.MULTILINE,
            ) is not None,
            f"declaration {short_name} is absent from digest-bound source",
        )

    forbidden = re.compile(r"\b(?:sorry|admit|axiom|unsafe)\b")
    require(
        forbidden.search(source_text) is None,
        "forbidden Lean trust token in TASK-022 source",
    )
    required_source_fragments = (
        "import Ecdlp.Proved.FrozenRecursiveProjectiveWitness",
        "namespace Ecdlp.FrozenProjectiveSemaev",
        "[Field k]",
        "[Field K]",
        "[IsAlgClosed K]",
        "Function.Injective",
        "frozenRecS17",
        "FrozenProjectiveChain",
        "∃ x : GuardVar → K,",
        "∀ e : GuardedEquation,",
        "MvPolynomial.eval x (guardedEquation q y e) = 0",
        "totalDegree",
    )
    for fragment in required_source_fragments:
        require(fragment in source_text,
                f"required source fragment missing: {fragment}")

    kernel = document.get("kernel_contract")
    require(isinstance(kernel, dict), "kernel contract must be an object")
    require(
        kernel.get("allowed_axioms")
        == ["propext", "Classical.choice", "Quot.sound"],
        "allowed axiom set drift",
    )
    require(kernel.get("forbidden_axioms") == ["sorryAx"],
            "forbidden axiom set drift")
    require(
        kernel.get("build_targets")
        == ["Ecdlp.Proved.FrozenProjectiveGuardSystem"],
        "build target drift",
    )
    require(
        kernel.get("compiler_trusted_declarations")
        == [
            "Ecdlp.FrozenProjectiveSemaev.card_guardVar_fourteen",
            "Ecdlp.FrozenProjectiveSemaev."
            "card_guarded_equations_fourteen",
        ],
        "native_decide disclosure drift",
    )
    require(kernel.get("compiler_trust_marker") == "Lean.ofReduceBool",
            "native_decide trust marker drift")
    require(kernel.get("build_status") == "passed",
            "build status is not passed")
    require(kernel.get("no_sorry_status") == "passed",
            "no-sorry status is not passed")
    require(kernel.get("validator_invokes_lean") is False,
            "validator must remain independent of Lean")

    scope = document.get("scope")
    require(isinstance(scope, dict), "scope must be an object")
    require(scope.get("task") == "TASK-022", "wrong task scope")
    require(scope.get("barrier") == "B-PKC-M16-COMPLETE-COST-BRIDGE",
            "wrong barrier")
    require(scope.get("cost_quantity") == "CQ-SEMAEV-S17-SYSTEM-COST",
            "wrong cost quantity")


def validate_artifact_hash() -> None:
    line = HASH_PATH.read_text(encoding="utf-8").strip()
    expected_line = f"{sha256(ARTIFACT_PATH)}  artifact.json"
    require(line == expected_line,
            "artifact.sha256 does not bind artifact.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=ARTIFACT_PATH)
    parser.add_argument(
        "--skip-artifact-hash",
        action="store_true",
        help="used only by rehashed semantic fault tests",
    )
    args = parser.parse_args()
    try:
        document = json.loads(args.artifact.read_text(encoding="utf-8"))
        validate_document(document)
        if args.artifact.resolve() == ARTIFACT_PATH.resolve():
            require(not args.skip_artifact_hash,
                    "canonical validation may not skip artifact hash")
            validate_artifact_hash()
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"TASK-022 certificate validation failed: {error}",
              file=sys.stderr)
        return 1

    print("TASK-022 guarded-projective validation PASSED")
    print(
        "stage=14 leaves=16 witnesses=14 variables=56 "
        "equations=29 degree_ceiling=4"
    )
    print(
        "F5 exhaustive guard fixture: assignments=625 solutions=120; "
        "[1:0] allowed and [0:0] rejected"
    )
    print(
        "source-bound non-run certificate; solver, rank, yield, cost, "
        "authorization, retention, and promotion remain absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
