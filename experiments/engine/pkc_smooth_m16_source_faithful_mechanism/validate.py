#!/usr/bin/env python3
"""Independent replay for the PKC M16 source-mechanism desk artifact.

The producer is not imported. This validator reconstructs the specialization
from exact integers and checks the curated source claims and upstream artifacts.
Source-review independence is deliberately not claimed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


P = (1 << 256) - (1 << 32) - 977
D = 564_522
ARITY = 16
FACTORS = (2, 3, 7, 13_441)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

EXPECTED_UPSTREAM = {
    "data/source_claim_extracts/petit_kosters_messeng2016_task028.json": (
        "a1af4d460f6677d449ba99eae4d3b79c75b265ea8c53f740de28d85e948b942a"
    ),
    "experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json": (
        "59596c3c59f5389c49742ba4a26d500445557ee6398d6aaad63c7995a93242f7"
    ),
    "experiments/engine/pkc_smooth_m16_regime_assurance_desk/artifact.json": (
        "dc514544bf388562a3ebed312aef56bc87b00527f32ce6d131a2f5371dba2744"
    ),
    "experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json": (
        "578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf"
    ),
    "experiments/engine/pkc_smooth_m16_frozen_projective_witness/artifact.json": (
        "89c645545d89334473d51654a41ff7ec2364857d034c64ce08d505337fa1e2d4"
    ),
    "Ecdlp/Proved/SemaevThree.lean": (
        "b469c41b89a5e1522fa7bdf5f9264a5fc50a45910929c1da9432298be8da4d9d"
    ),
}


class ValidationFailure(Exception):
    """The artifact or one of its provenance bindings failed replay."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def exact(label: str, actual: Any, expected: Any) -> None:
    require(actual == expected, f"{label}: {actual!r} != {expected!r}")


def exact_keys(label: str, value: Any, expected: set[str]) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    exact(f"{label} keys", set(value), expected)
    return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} must contain an object")
    return value


def validate_upstream(document: dict[str, Any]) -> None:
    bindings = document["upstream_bindings"]
    exact("upstream bindings", bindings, EXPECTED_UPSTREAM)
    for relative, expected in EXPECTED_UPSTREAM.items():
        path = ROOT / relative
        require(path.is_file(), f"missing upstream file: {relative}")
        exact(f"upstream hash {relative}", file_sha256(path), expected)


def validate_source_binding(document: dict[str, Any]) -> None:
    binding = exact_keys(
        "source_binding",
        document["source_binding"],
        {
            "artifact_sha256",
            "claim_extract_path",
            "claim_extract_sha256",
            "claim_ids",
            "review_status",
            "source_id",
            "source_independence",
            "url",
        },
    )
    exact("source id", binding["source_id"], "petit_kosters_messeng2016")
    exact(
        "source URL",
        binding["url"],
        "https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf",
    )
    exact("source review status", binding["review_status"], "full_text_obtained")
    exact("source independence", binding["source_independence"], "not_established")
    exact(
        "source artifact",
        binding["artifact_sha256"],
        "2958155e2c0a379b79490be7c2dab6658bda896cce2c1b517634b4cb6892d943",
    )
    exact(
        "source extract path",
        binding["claim_extract_path"],
        "data/source_claim_extracts/petit_kosters_messeng2016_task028.json",
    )
    exact(
        "source extract hash",
        binding["claim_extract_sha256"],
        EXPECTED_UPSTREAM[binding["claim_extract_path"]],
    )
    expected_ids = [
        "SC-PKC-SYSTEM4-EXACT",
        "SC-PKC-PMINUS1-MAP-EXACT",
        "SC-PKC-PARTIAL-COST-EXACT",
    ]
    exact("source claim ids", binding["claim_ids"], expected_ids)

    source = load_json(ROOT / binding["claim_extract_path"])
    exact("source extract id", source["source_id"], binding["source_id"])
    exact("source extract URL", source["source_url"], binding["url"])
    exact("source extract artifact hash", source["source_artifact_sha256"], binding["artifact_sha256"])
    exact("source extract review", source["review_status"], "full_text_obtained")
    claims = {claim["claim_id"]: claim for claim in source["claims"]}
    for claim_id in expected_ids:
        require(claim_id in claims, f"missing exact source claim {claim_id}")
    exact(
        "System (4) locator",
        claims["SC-PKC-SYSTEM4-EXACT"]["locator"],
        {
            "kind": "section",
            "value": "Section 3.1, Algorithm 1, System (4), published p. 9",
        },
    )
    exact(
        "p-minus-one map locator",
        claims["SC-PKC-PMINUS1-MAP-EXACT"]["locator"],
        {"kind": "section", "value": "Section 3.3, published p. 10"},
    )
    exact(
        "partial-cost locator",
        claims["SC-PKC-PARTIAL-COST-EXACT"]["locator"],
        {"kind": "section", "value": "Section 3.2, published p. 10"},
    )
    require(
        "sum_i P_i=0" in claims["SC-PKC-SYSTEM4-EXACT"]["boundary"]
        and "does not explicitly bind" in claims["SC-PKC-SYSTEM4-EXACT"]["boundary"]
        and "does not prove complete recovery" in claims[
            "SC-PKC-SYSTEM4-EXACT"
        ]["boundary"]
        and "R=O requires resampling" in claims[
            "SC-PKC-SYSTEM4-EXACT"
        ]["boundary"],
        "source recovery ambiguity was weakened",
    )
    require(
        "degree-13441" in claims["SC-PKC-PMINUS1-MAP-EXACT"]["boundary"],
        "source map degree boundary was weakened",
    )
    require(
        "leaves the complexity open" in claims["SC-PKC-PARTIAL-COST-EXACT"]["boundary"]
        and "does not prove relation independence" in claims[
            "SC-PKC-PARTIAL-COST-EXACT"
        ]["boundary"],
        "source cost boundary was weakened",
    )


def validate_specialization(document: dict[str, Any]) -> None:
    specialization = exact_keys(
        "specialization",
        document["specialization"],
        {"arity", "divides_p_minus_one", "factorization", "p", "smooth_divisor"},
    )
    exact("arity", specialization["arity"], ARITY)
    exact("p", specialization["p"], str(P))
    exact("D", specialization["smooth_divisor"], D)
    exact("factorization", specialization["factorization"], list(FACTORS))
    exact("factor product", 2 * 3 * 7 * 13_441, D)
    require((P - 1) % D == 0, "D does not divide p-1")
    exact("divisibility flag", specialization["divides_p_minus_one"], True)

    chain = exact_keys(
        "source_map_chain",
        document["source_map_chain"],
        {
            "components",
            "composed_polynomial",
            "composition_convention",
            "maximum_component_degree",
            "pointwise_root_equivalence",
            "prefix_exponents",
            "root_count_in_f_p",
            "root_set",
        },
    )
    expected_components = [
        {"degree": 2, "factor": 2, "index": 1, "map": "L1(x)=x^2"},
        {"degree": 3, "factor": 3, "index": 2, "map": "L2(x)=x^3"},
        {"degree": 7, "factor": 7, "index": 3, "map": "L3(x)=x^7"},
        {
            "degree": 13_441,
            "factor": 13_441,
            "index": 4,
            "map": "L4(x)=1-x^13441",
        },
    ]
    exact("map components", chain["components"], expected_components)
    exact("prefix exponents", chain["prefix_exponents"], [2, 6, 42])
    exact("composition", chain["composition_convention"], "L=L4 o L3 o L2 o L1")
    exact("composed polynomial", chain["composed_polynomial"], "L(x)=1-x^564522")
    exact("maximum source component degree", chain["maximum_component_degree"], 13_441)
    exact("root count", chain["root_count_in_f_p"], D)
    exact("root set", chain["root_set"], "the unique order-564522 subgroup H of F_p^*")
    exact(
        "pointwise root equivalence",
        chain["pointwise_root_equivalence"],
        "For x in F_p, L(x)=0 iff x^564522=1.",
    )

    system = exact_keys(
        "system4_specialization",
        document["system4_specialization"],
        {
            "affine_target_required",
            "direct_relation",
            "direct_relation_per_leaf_degree",
            "direct_relation_target_specialized_total_degree_upper_bound",
            "equation_members",
            "factor_coordinates",
            "identity_target_policy",
            "sampled_target_precedes_system",
            "target_definition",
            "terminal_equations",
            "transition_equations",
        },
    )
    exact("direct relation", system["direct_relation"], "S17(x_11,...,x_16, X)=0")
    exact("factor coordinates", system["factor_coordinates"], 64)
    exact("transitions", system["transition_equations"], 48)
    exact("terminals", system["terminal_equations"], 16)
    exact("equation members", system["equation_members"], 65)
    exact("per-leaf degree", system["direct_relation_per_leaf_degree"], 32_768)
    exact(
        "target-specialized total-degree ceiling",
        system["direct_relation_target_specialized_total_degree_upper_bound"],
        524_288,
    )
    exact("target chronology", system["sampled_target_precedes_system"], True)
    exact("affine target precondition", system["affine_target_required"], True)
    exact("target definition", system["target_definition"], "R=(X,Y)=aP+bQ with R != O")
    exact(
        "identity target policy",
        system["identity_target_policy"],
        "If R=O, the affine target coordinate X is undefined; resample "
        "(a,b) or process that case outside this affine specialization.",
    )

    symbolic = load_json(
        ROOT / "experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json"
    )
    direct = symbolic["representations"]["direct_s17_with_source_factor_chain"]
    exact("symbolic direct equation count", direct["equation_count"], 65)
    exact("symbolic direct variables", direct["variable_count"], 64)
    exact("symbolic map degrees", direct["membership"]["map_degrees"], list(FACTORS))
    exact("symbolic per-leaf degree", direct["relation"]["per_leaf_variable_degree"], 32_768)
    exact(
        "symbolic total-degree ceiling",
        direct["relation"]["target_specialized_total_degree_upper_bound"],
        524_288,
    )


def validate_boundaries(document: dict[str, Any]) -> None:
    representation = exact_keys(
        "representation_boundary",
        document["representation_boundary"],
        {
            "quadratic_circuit_pointwise_equivalent",
            "same_polynomial_ideal_claimed",
            "same_solving_complexity_claimed",
            "source_factor_chain_maximum_degree",
            "warning",
        },
    )
    exact("circuit pointwise equivalence", representation["quadratic_circuit_pointwise_equivalent"], True)
    exact("ideal nonclaim", representation["same_polynomial_ideal_claimed"], False)
    exact("complexity nonclaim", representation["same_solving_complexity_claimed"], False)
    exact("source max degree", representation["source_factor_chain_maximum_degree"], 13_441)
    exact(
        "representation warning",
        representation["warning"],
        "Replacing the source chain by an addition-chain circuit preserves "
        "pointwise membership only; it does not transfer solving-degree, "
        "fill-in, multiplicity, saturation, or complexity claims.",
    )

    recovery = exact_keys(
        "recovery_contract",
        document["recovery_contract"],
        {"repository_completion", "source_exact"},
    )
    source_exact = exact_keys(
        "recovery_contract.source_exact",
        recovery["source_exact"],
        {
            "printed_acceptance",
            "printed_target_binding_explicit",
            "solutions_quotiented_by",
            "status",
        },
    )
    exact("printed acceptance", source_exact["printed_acceptance"], "sum_i P_i = O")
    exact(
        "source solution quotient",
        source_exact["solutions_quotiented_by"],
        "permutations of x_i1",
    )
    exact("printed target binding", source_exact["printed_target_binding_explicit"], False)
    exact(
        "source recovery status",
        source_exact["status"],
        "internally_ambiguous_with_target_dependent_system",
    )
    completion = exact_keys(
        "recovery_contract.repository_completion",
        recovery["repository_completion"],
        {
            "assurance",
            "bind_sampled_target",
            "direct_system4_recovery_completeness",
            "enumerate_f_p_curve_lifts",
            "exceptional_and_infinity_fibers",
            "final_acceptance",
            "permutation_and_duplicate_accounting_required",
            "soundness_scope",
            "target_sign_recorded_in_relation",
        },
    )
    exact("target-bound completion", completion["bind_sampled_target"], True)
    exact(
        "acceptance-filter assurance",
        completion["assurance"],
        "derived_sound_acceptance_filter_only",
    )
    exact(
        "direct recovery completeness",
        completion["direct_system4_recovery_completeness"],
        "unproved",
    )
    exact("F_p lift recovery", completion["enumerate_f_p_curve_lifts"], True)
    exact("duplicate accounting", completion["permutation_and_duplicate_accounting_required"], True)
    exact("target sign", completion["target_sign_recorded_in_relation"], True)
    exact(
        "exceptional-fiber boundary",
        completion["exceptional_and_infinity_fibers"],
        "referenced upstream but do not establish direct-System-(4) "
        "recovery completeness",
    )
    exact(
        "acceptance-filter soundness scope",
        completion["soundness_scope"],
        "Passing this filter validates a candidate relation; it does not "
        "prove that every direct-System-(4) solution is recovered.",
    )
    exact(
        "target-bound independent recovery check",
        completion["final_acceptance"],
        "Accept only a recovered signed relation "
        "sum_i epsilon_i P_i + epsilon_R R = O, with every point "
        "and coefficient checked by independent elliptic-curve arithmetic.",
    )

    cost = exact_keys(
        "cost_contract",
        document["cost_contract"],
        {
            "known_source_formula",
            "known_source_yield_heuristic",
            "source_solver_status",
            "unresolved",
        },
    )
    exact(
        "source formula",
        cost["known_source_formula"],
        "P(p,16) + (16!*p/D^15)*T(E,16,L) + D^omega",
    )
    exact("source yield", cost["known_source_yield_heuristic"], "D^16/(16!*p)")
    exact(
        "source solver boundary",
        cost["source_solver_status"],
        "No dedicated generalized-root algorithm or cost theorem is provided; "
        "the source leaves asymptotic complexity open.",
    )
    exact(
        "unresolved cost ledger",
        cost["unresolved"],
        [
            "generalized-root solving degree and fill-in",
            "usable regular-locus probability and exceptional-complement orchestration",
            "independent-relation probability and rank",
            "direct-System-(4) recovery completeness, multiplicity, and online cost",
            "preprocessing and amortization",
            "sparse linear-algebra time, memory, and storage",
            "common-unit equal-success comparison with Pollard rho",
        ],
    )

    assurance = document["assurance_matrix"]
    exact(
        "assurance matrix",
        assurance,
        {
            "m16_factor_base_census": "certificate_replayed",
            "pointwise_chain_arithmetic": "derived_arithmetic",
            "primary_source_map_and_system": "source_exact",
            "printed_recovery_target_binding": "source_ambiguous",
            "projective_semantics": "lean_kernel_and_certificate_replayed",
            "repository_recovery_completion": (
                "derived_sound_filter_completeness_unproved"
            ),
            "solver_and_complete_cost": "unknown",
        },
    )

    terminal = exact_keys(
        "terminal",
        document["terminal"],
        {
            "authorization",
            "calibration",
            "cell_transition",
            "hypothesis_effect",
            "novelty_claimed",
            "retention",
            "route_effect",
            "scientific_disposition",
            "source_independence",
        },
    )
    exact("terminal authorization", terminal["authorization"], "none")
    exact("terminal calibration", terminal["calibration"], "excluded_nonexperimental")
    exact("cell transition", terminal["cell_transition"], "open_to_open")
    exact("hypothesis effect", terminal["hypothesis_effect"], "none")
    exact("novelty", terminal["novelty_claimed"], False)
    exact("retention", terminal["retention"], "zero")
    exact("route effect", terminal["route_effect"], "none")
    exact(
        "scientific disposition",
        terminal["scientific_disposition"],
        "mechanism_specified_cost_unresolved",
    )
    exact("terminal source independence", terminal["source_independence"], "not_established")

    regime = load_json(
        ROOT / "experiments/engine/pkc_smooth_m16_regime_assurance_desk/artifact.json"
    )
    census = regime["factor_base_census"]
    exact("liftable x", census["liftable_x"], 283_527)
    exact("nonliftable x", census["nonliftable_x"], 280_995)
    exact("signed points", census["signed_affine_factor_points"], 567_054)


def validate_document(document: dict[str, Any]) -> None:
    exact_keys(
        "artifact",
        document,
        {
            "artifact_id",
            "assurance_matrix",
            "cost_contract",
            "kind",
            "recovery_contract",
            "representation_boundary",
            "schema_version",
            "source_binding",
            "source_map_chain",
            "specialization",
            "system4_specialization",
            "task_id",
            "terminal",
            "upstream_bindings",
        },
    )
    exact(
        "artifact id",
        document["artifact_id"],
        "PKC-M16-SOURCE-FAITHFUL-MECHANISM-RECOVERY-001",
    )
    exact("schema", document["schema_version"], "1.0")
    exact("task", document["task_id"], "TASK-028")
    exact(
        "kind",
        document["kind"],
        "deterministic_nonexperimental_source_mechanism_desk",
    )
    validate_upstream(document)
    validate_source_binding(document)
    validate_specialization(document)
    validate_boundaries(document)


def load_and_validate() -> dict[str, Any]:
    require(ARTIFACT_PATH.is_file(), "artifact.json is missing")
    require(HASH_PATH.is_file(), "artifact.sha256 is missing")
    document = load_json(ARTIFACT_PATH)
    payload = canonical_bytes(document)
    exact("canonical artifact bytes", ARTIFACT_PATH.read_bytes(), payload)
    digest = hashlib.sha256(payload).hexdigest()
    exact("artifact sidecar", HASH_PATH.read_text(encoding="ascii"), f"{digest}  artifact.json\n")
    validate_document(document)
    return document


def main() -> int:
    document = load_and_validate()
    print(
        "PKC M16 source mechanism replay PASS: "
        f"{document['terminal']['scientific_disposition']}; "
        "authorization=none; source_independence=not_established"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
