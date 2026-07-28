#!/usr/bin/env python3
"""Validate the narrow TASK-021 projective witness-chain certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-FROZEN-PROJECTIVE-WITNESS-001"
ARTIFACT_KIND = "non_run_kernel_binding_certificate"
SOURCE_PATH = "Ecdlp/Proved/FrozenRecursiveProjectiveWitness.lean"
FROZEN_PATH = "Ecdlp/Proved/FrozenRecursiveProjectiveSemaev.lean"
TASK020_PATH = (
    "experiments/engine/pkc_smooth_m16_frozen_cr_specialization/artifact.json"
)
EXPECTED_DIGESTS = {
    TASK020_PATH:
        "d025053b9f882c88086fd5f04bcbd9627c72987e263e9b55af6024794305acbe",
    FROZEN_PATH:
        "194e03cb6ddcb8f539229b4c3c7639b138f90fcdcd1d44295c16bc58c7514320",
    SOURCE_PATH:
        "5cffb444d95f7691f92bfbd094d945be7e97069edb244d5234fa06f359a852b9",
}

EXPECTED_THEOREMS = {
    "C16_chain":
        "Ecdlp.FrozenProjectiveSemaev."
        "specializeOver_frozenC16_eq_zero_iff_projectiveChain",
    "all_stage_chain":
        "Ecdlp.FrozenProjectiveSemaev."
        "specializeOver_frozenC_eq_zero_iff_projectiveChain",
    "chain_definition":
        "Ecdlp.FrozenProjectiveSemaev.FrozenProjectiveChain",
    "local_affine_fixture":
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_localSliceAt_affine",
    "local_eval_bridge":
        "Ecdlp.FrozenProjectiveSemaev.eval_homogenize_localSliceAt",
    "local_form_identity":
        "Ecdlp.FrozenProjectiveSemaev.homogenize_localSliceAt",
    "local_infinity_fixture":
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_localSliceAt_infinity",
    "output_homogeneity":
        "Ecdlp.FrozenProjectiveSemaev."
        "projectiveOutputAtOver_frozenC_isHomogeneous",
    "predecessor_affine_fixture":
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_previousSliceAtOver_frozenC_affine",
    "predecessor_eval_bridge":
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_previousSliceAtOver_frozenC",
    "predecessor_form_identity":
        "Ecdlp.FrozenProjectiveSemaev."
        "homogenize_previousSliceAtOver_frozenC",
    "predecessor_infinity_fixture":
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_previousSliceAtOver_frozenC_infinity",
}

EXPECTED_ASSUMPTIONS = {
    "coefficient_map":
        "the source is a CommRing k and phi is an explicit ring "
        "homomorphism k ->+* K",
    "main_target":
        "the recursive extraction theorem uses a Field K with IsAlgClosed K",
    "normalization":
        "declared homogenization degrees are retained; no primitive, "
        "content, monic, sign, actual-degree, or variable-dependent "
        "normalization",
    "projective_domain":
        "each ProjectivePair satisfies u!=0 or v!=0; [0:0] is excluded and "
        "[1:0] is allowed",
    "witness_field":
        "all intermediate witnesses live in the algebraically closed target "
        "K; no descent to k or another smaller field is claimed",
    "zero_forms_and_degree_drops":
        "included by exact declared-degree homogeneity and projective "
        "evaluation",
}

EXPECTED_PROOF_STATUS = {
    "base_field_descent": "not_claimed",
    "direct_S17_equivalence": "not_claimed",
    "local_projective_evaluation_bridge": "kernel_checked",
    "predecessor_projective_evaluation_bridge": "kernel_checked",
    "projective_infinity_at_every_stage": "kernel_checked",
    "solving_rank_yield_cost_claim": "not_claimed",
    "universal_C16_to_C2_projective_witness_chain": "kernel_checked",
    "universal_all_stage_chain_equivalence": "kernel_checked",
    "universal_output_homogeneity": "kernel_checked",
}

EXPECTED_CHAIN = {
    "C16_stage": 14,
    "base_equation": "HValue (q 0).coord (q 1).coord y.coord = 0",
    "base_stage": 0,
    "family_index": "frozenC k s = C_(s+2)",
    "infinity_point": "[1:0]",
    "infinity_point_allowed": True,
    "internal_projective_witness_count_at_C16": 14,
    "leaf_count_at_C16": 16,
    "leaf_index_end_at_C16": 15,
    "leaf_index_start": 0,
    "successor_equation":
        "exists z, Chain q s z and HValue z.coord (q (s+2)).coord "
        "y.coord = 0",
    "zero_pair": "[0:0]",
    "zero_pair_excluded": True,
}

EXPECTED_PROJECTIVE = {
    "affine_fixture_theorems": [
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_previousSliceAtOver_frozenC_affine",
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_localSliceAt_affine",
    ],
    "infinity_fixture_theorems": [
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_previousSliceAtOver_frozenC_infinity",
        "Ecdlp.FrozenProjectiveSemaev."
        "eval_homogenize_localSliceAt_infinity",
    ],
    "local_declared_degree": 2,
    "predecessor_declared_degree": "2^(s+1)",
    "universal_pair": "[U:V]",
    "valid_pair_condition": "U!=0 or V!=0",
    "zero_pair_excluded": True,
}

EXPECTED_PRODUCER = {
    "C16_evaluated": False,
    "C16_expanded": False,
    "M16_system_materialized": False,
    "S17_materialized": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
    "parameter_sweep_executed": False,
    "solver_executed": False,
}

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "barrier_effect": "narrowed_open",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "experiment_permission": "none",
    "hypothesis_effect": "none",
    "rank_status": "unpriced",
    "remaining_blocker":
        "complete S17 representation, materialization, rank, yield, solving, "
        "and recovery-cost bridge",
    "retention_disposition": "zero_retention_success",
    "route_effect": "none",
    "solving_cost_status": "unpriced",
    "yield_status": "unpriced",
}


class ValidationError(RuntimeError):
    """Raised when a certificate binding or semantic invariant is invalid."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_document(document: dict[str, Any]) -> None:
    require(document.get("artifact_id") == ARTIFACT_ID, "wrong artifact id")
    require(document.get("schema_version") == 1, "wrong schema version")
    require(document.get("kind") == ARTIFACT_KIND, "wrong artifact kind")
    require(
        document.get("assumption_contract") == EXPECTED_ASSUMPTIONS,
        "assumption contract drift",
    )
    require(
        document.get("projective_evaluation_contract") == EXPECTED_PROJECTIVE,
        "projective evaluation contract drift",
    )
    require(
        document.get("witness_chain_contract") == EXPECTED_CHAIN,
        "witness-chain contract drift",
    )
    require(
        document.get("proof_status") == EXPECTED_PROOF_STATUS,
        "proof-status drift",
    )
    require(
        document.get("producer_checks") == EXPECTED_PRODUCER,
        "producer or non-execution contract drift",
    )
    require(
        document.get("terminal_disposition") == EXPECTED_TERMINAL,
        "terminal disposition drift",
    )

    dependencies = document.get("depends_on")
    require(isinstance(dependencies, list), "dependencies must be a list")
    require(
        [item.get("path") for item in dependencies]
        == list(EXPECTED_DIGESTS),
        "dependency path or order drift",
    )
    for item in dependencies:
        path = item["path"]
        expected = EXPECTED_DIGESTS[path]
        require(item.get("required_sha256") == expected,
                f"required digest drift for {path}")
        require(item.get("observed_sha256") == expected,
                f"observed digest drift for {path}")
        require(item.get("digest_match") is True,
                f"digest match not asserted for {path}")
        actual = sha256(REPO_ROOT / path)
        require(actual == expected, f"repository digest mismatch for {path}")

    bindings = document.get("theorem_bindings")
    require(isinstance(bindings, dict), "theorem bindings must be an object")
    require(set(bindings) == set(EXPECTED_THEOREMS),
            "theorem-binding key drift")
    source_text = (REPO_ROOT / SOURCE_PATH).read_text(encoding="utf-8")
    for key, declaration in EXPECTED_THEOREMS.items():
        binding = bindings[key]
        require(binding.get("declaration") == declaration,
                f"declaration drift for {key}")
        require(binding.get("source_path") == SOURCE_PATH,
                f"source drift for {key}")
        require(binding.get("kernel_status") == "kernel_checked",
                f"kernel status drift for {key}")
        short_name = declaration.rsplit(".", 1)[-1]
        require(
            re.search(
                rf"^(?:noncomputable )?(?:def|theorem) "
                rf"{re.escape(short_name)}\b",
                source_text,
                flags=re.MULTILINE,
            ) is not None,
            f"declaration {short_name} is absent from digest-bound source",
        )

    forbidden = re.compile(r"\b(?:sorry|admit|axiom|unsafe)\b")
    require(
        forbidden.search(source_text) is None,
        "forbidden Lean trust token in TASK-021 source",
    )
    required_source_fragments = (
        "[IsAlgClosed K]",
        "(2 ^ (s + 1))",
        "HValue z.coord (q (s + 2)).coord y.coord = 0",
        "specializeOver φ q y (frozenC k 14) = 0",
        "FrozenProjectiveChain q 14 y",
        "ProjectivePair.infinity",
        "ProjectivePair.affine",
    )
    for fragment in required_source_fragments:
        require(fragment in source_text,
                f"required source fragment missing: {fragment}")

    kernel = document.get("kernel_contract", {})
    require(
        kernel.get("allowed_axioms")
        == ["propext", "Classical.choice", "Quot.sound"],
        "allowed axiom set drift",
    )
    require(kernel.get("forbidden_axioms") == ["sorryAx"],
            "forbidden axiom set drift")
    require(
        kernel.get("build_targets")
        == ["Ecdlp.Proved.FrozenRecursiveProjectiveWitness"],
        "build target drift",
    )
    require(kernel.get("build_status") == "passed",
            "build status is not passed")
    require(kernel.get("no_sorry_status") == "passed",
            "no-sorry status is not passed")
    require(kernel.get("validator_invokes_lean") is False,
            "validator must remain independent of Lean")

    scope = document.get("scope", {})
    require(scope.get("task") == "TASK-021", "wrong task scope")
    require(scope.get("barrier") == "B-PKC-M16-COMPLETE-COST-BRIDGE",
            "wrong barrier")
    require(scope.get("cost_quantity") == "CQ-SEMAEV-S17-SYSTEM-COST",
            "wrong cost quantity")
    boundary = document.get("downstream_open_boundary", {})
    require(
        "complete S17 representation" in boundary.get("remaining_blocker", ""),
        "remaining complete-cost blocker was removed",
    )


def validate_artifact_hash() -> None:
    line = HASH_PATH.read_text(encoding="utf-8").strip()
    expected_line = f"{sha256(ARTIFACT_PATH)}  artifact.json"
    require(line == expected_line, "artifact.sha256 does not bind artifact.json")


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
        print(f"TASK-021 certificate validation failed: {error}", file=sys.stderr)
        return 1
    print(
        "TASK-021 certificate valid: all-stage projective chain and C16 "
        "corollary are digest-bound; execution and complete-cost claims "
        "remain absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
