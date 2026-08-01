#!/usr/bin/env python3
"""Generate the source-faithful PKC M16 mechanism desk artifact.

This generator performs exact structural arithmetic only. It does not build a
Semaev system, run a polynomial solver, or compute a discrete logarithm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


P = (1 << 256) - (1 << 32) - 977
D = 564_522
ARITY = 16
FACTORS = (2, 3, 7, 13_441)
PREFIX_EXPONENTS = (2, 6, 42)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

UPSTREAM_BINDINGS = {
    "data/source_claim_extracts/petit_kosters_messeng2016_task028.json": (
        "4687da1bd3e87f2adfb0379b3336c8f4c19057350ae425f49df6f36da3ed30ea"
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

SOURCE_CLAIM_IDS = (
    "SC-PKC-SYSTEM4-EXACT",
    "SC-PKC-PMINUS1-MAP-EXACT",
    "SC-PKC-PARTIAL-COST-EXACT",
)


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


def assert_upstream_bindings() -> None:
    problems: list[str] = []
    for relative, expected in UPSTREAM_BINDINGS.items():
        path = ROOT / relative
        if not path.is_file():
            problems.append(f"missing upstream file: {relative}")
            continue
        observed = file_sha256(path)
        if observed != expected:
            problems.append(
                f"upstream hash drift for {relative}: {observed} != {expected}"
            )
    if problems:
        raise RuntimeError("; ".join(problems))


def assert_source_extract() -> None:
    path = (
        ROOT
        / "data/source_claim_extracts/petit_kosters_messeng2016_task028.json"
    )
    source = json.loads(path.read_text(encoding="utf-8"))
    claims = {
        claim["claim_id"]: claim
        for claim in source.get("claims", [])
        if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str)
    }
    missing = sorted(set(SOURCE_CLAIM_IDS) - set(claims))
    if missing:
        raise RuntimeError(f"source extract lacks exact claims: {missing}")
    if "sum_i P_i=0" not in claims["SC-PKC-SYSTEM4-EXACT"]["boundary"]:
        raise RuntimeError("source recovery ambiguity is not retained")
    if "13441" not in claims["SC-PKC-PMINUS1-MAP-EXACT"]["boundary"]:
        raise RuntimeError("large terminal component boundary is not retained")
    if "leaves the complexity open" not in claims[
        "SC-PKC-PARTIAL-COST-EXACT"
    ]["boundary"]:
        raise RuntimeError("open solver-cost boundary is not retained")


def build_artifact() -> dict[str, Any]:
    assert_upstream_bindings()
    assert_source_extract()

    if D != 2 * 3 * 7 * 13_441:
        raise AssertionError("factor product drifted")
    if (P - 1) % D != 0:
        raise AssertionError("D no longer divides p-1")

    components = [
        {"index": 1, "factor": 2, "map": "L1(x)=x^2", "degree": 2},
        {"index": 2, "factor": 3, "map": "L2(x)=x^3", "degree": 3},
        {"index": 3, "factor": 7, "map": "L3(x)=x^7", "degree": 7},
        {
            "index": 4,
            "factor": 13_441,
            "map": "L4(x)=1-x^13441",
            "degree": 13_441,
        },
    ]

    source_chain_variables = ARITY * len(FACTORS)
    transition_equations = ARITY * (len(FACTORS) - 1)
    terminal_equations = ARITY

    return {
        "artifact_id": "PKC-M16-SOURCE-FAITHFUL-MECHANISM-RECOVERY-001",
        "kind": "deterministic_nonexperimental_source_mechanism_desk",
        "schema_version": "1.0",
        "task_id": "TASK-028",
        "source_binding": {
            "artifact_sha256": (
                "2958155e2c0a379b79490be7c2dab6658bda896cce2c1b517634b4cb6892d943"
            ),
            "claim_extract_path": (
                "data/source_claim_extracts/petit_kosters_messeng2016_task028.json"
            ),
            "claim_extract_sha256": UPSTREAM_BINDINGS[
                "data/source_claim_extracts/petit_kosters_messeng2016_task028.json"
            ],
            "claim_ids": list(SOURCE_CLAIM_IDS),
            "review_status": "full_text_obtained",
            "source_id": "petit_kosters_messeng2016",
            "source_independence": "not_established",
            "url": "https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf",
        },
        "specialization": {
            "arity": ARITY,
            "divides_p_minus_one": True,
            "factorization": list(FACTORS),
            "p": str(P),
            "smooth_divisor": D,
        },
        "source_map_chain": {
            "components": components,
            "composed_polynomial": "L(x)=1-x^564522",
            "composition_convention": "L=L4 o L3 o L2 o L1",
            "maximum_component_degree": max(FACTORS),
            "pointwise_root_equivalence": (
                "For x in F_p, L(x)=0 iff x^564522=1."
            ),
            "prefix_exponents": list(PREFIX_EXPONENTS),
            "root_count_in_f_p": D,
            "root_set": "the unique order-564522 subgroup H of F_p^*",
        },
        "system4_specialization": {
            "direct_relation": "S17(x_11,...,x_16, X)=0",
            "direct_relation_per_leaf_degree": 32_768,
            "direct_relation_target_specialized_total_degree_upper_bound": 524_288,
            "equation_members": 1 + transition_equations + terminal_equations,
            "factor_coordinates": source_chain_variables,
            "sampled_target_precedes_system": True,
            "target_definition": "R=(X,Y)=aP+bQ",
            "terminal_equations": terminal_equations,
            "transition_equations": transition_equations,
        },
        "representation_boundary": {
            "quadratic_circuit_pointwise_equivalent": True,
            "same_polynomial_ideal_claimed": False,
            "same_solving_complexity_claimed": False,
            "source_factor_chain_maximum_degree": 13_441,
            "warning": (
                "Replacing the source chain by an addition-chain circuit preserves "
                "pointwise membership only; it does not transfer solving-degree, "
                "fill-in, multiplicity, saturation, or complexity claims."
            ),
        },
        "recovery_contract": {
            "source_exact": {
                "solutions_quotiented_by": "permutations of x_i1",
                "printed_acceptance": "sum_i P_i = O",
                "printed_target_binding_explicit": False,
                "status": "internally_ambiguous_with_target_dependent_system",
            },
            "repository_completion": {
                "assurance": "derived_from_summation_semantics_and_replayed_artifacts",
                "bind_sampled_target": True,
                "enumerate_f_p_curve_lifts": True,
                "exceptional_and_infinity_fibers": (
                    "bound to the existing projective and exceptional-fiber artifacts"
                ),
                "final_acceptance": (
                    "Accept only a recovered signed relation "
                    "sum_i epsilon_i P_i + epsilon_R R = O, with every point "
                    "and coefficient checked by independent elliptic-curve arithmetic."
                ),
                "permutation_and_duplicate_accounting_required": True,
                "target_sign_recorded_in_relation": True,
            },
        },
        "cost_contract": {
            "known_source_formula": (
                "P(p,16) + (16!*p/D^15)*T(E,16,L) + D^omega"
            ),
            "known_source_yield_heuristic": "D^16/(16!*p)",
            "source_solver_status": (
                "No dedicated generalized-root algorithm or cost theorem is "
                "provided; the source leaves asymptotic complexity open."
            ),
            "unresolved": [
                "generalized-root solving degree and fill-in",
                "usable regular-locus probability and exceptional-complement orchestration",
                "independent-relation probability and rank",
                "recovery multiplicity and online cost",
                "preprocessing and amortization",
                "sparse linear-algebra time, memory, and storage",
                "common-unit equal-success comparison with Pollard rho",
            ],
        },
        "assurance_matrix": {
            "primary_source_map_and_system": "source_exact",
            "m16_factor_base_census": "certificate_replayed",
            "pointwise_chain_arithmetic": "derived_arithmetic",
            "projective_semantics": "lean_kernel_and_certificate_replayed",
            "printed_recovery_target_binding": "source_ambiguous",
            "repository_recovery_completion": "derived_and_replay_bound",
            "solver_and_complete_cost": "unknown",
        },
        "upstream_bindings": dict(UPSTREAM_BINDINGS),
        "terminal": {
            "authorization": "none",
            "calibration": "excluded_nonexperimental",
            "cell_transition": "open_to_open",
            "hypothesis_effect": "none",
            "novelty_claimed": False,
            "retention": "zero",
            "route_effect": "none",
            "scientific_disposition": "mechanism_specified_cost_unresolved",
            "source_independence": "not_established",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    artifact = build_artifact()
    payload = canonical_bytes(artifact)
    digest = hashlib.sha256(payload).hexdigest()
    sidecar = f"{digest}  artifact.json\n".encode("ascii")

    if args.check:
        if not ARTIFACT_PATH.is_file() or ARTIFACT_PATH.read_bytes() != payload:
            raise SystemExit("artifact.json drifted; run generate.py")
        if not HASH_PATH.is_file() or HASH_PATH.read_bytes() != sidecar:
            raise SystemExit("artifact.sha256 drifted; run generate.py")
        print(f"PKC M16 source mechanism artifact OK sha256={digest}")
        return 0

    ARTIFACT_PATH.write_bytes(payload)
    HASH_PATH.write_bytes(sidecar)
    print(f"wrote {ARTIFACT_PATH.relative_to(ROOT)} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
