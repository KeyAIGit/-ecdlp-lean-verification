#!/usr/bin/env python3
"""Cross-check canonical scientific assertions across independently owned files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from research_claims import validate_and_build as validate_claim_policy

ROOT = Path(__file__).resolve().parent.parent

M16_PROJECTIVE_CLAIM_ID = "SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT"
M16_PROJECTIVE_ARTIFACT_PATH = (
    "experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json"
)
M16_PROJECTIVE_ARTIFACT_SHA256 = (
    "3164cb89adac7622b4d08d781061ea386dc64e754236e48c838a3dac23040715"
)
M16_RESULTANT_KERNEL_CLAIM_ID = (
    "SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT"
)
M16_RESULTANT_KERNEL_ARTIFACT_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_projective_resultant_kernel/artifact.json"
)
M16_RESULTANT_KERNEL_ARTIFACT_SHA256 = (
    "0b9d8b48953aae2defa28ade67992084cecca3a01b43490bc338a0fd5ce97c5a"
)
M16_FROZEN_CR_CLAIM_ID = "SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT"
M16_FROZEN_CR_ARTIFACT_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_frozen_cr_specialization/artifact.json"
)
M16_FROZEN_CR_ARTIFACT_SHA256 = (
    "d025053b9f882c88086fd5f04bcbd9627c72987e263e9b55af6024794305acbe"
)
M16_WITNESS_CLAIM_ID = (
    "SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT"
)
M16_WITNESS_ARTIFACT_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_frozen_projective_witness/artifact.json"
)
M16_WITNESS_ARTIFACT_SHA256 = (
    "89c645545d89334473d51654a41ff7ec2364857d034c64ce08d505337fa1e2d4"
)
M16_GUARDED_CLAIM_ID = (
    "SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT"
)
M16_GUARDED_ARTIFACT_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_guarded_projective_system/artifact.json"
)
M16_GUARDED_ARTIFACT_SHA256 = (
    "3445da55b44a71d0f40ee60206c90f2ef1798c28abd125542ce3acbeeb8e1d46"
)
M16_CHART_CLAIM_ID = "SC-PKC-M16-EXACT-CHART-COVER-RESULT"
M16_CHART_ARTIFACT_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_exact_chart_cover/artifact.json"
)
M16_CHART_ARTIFACT_SHA256 = (
    "934809fabbb8c98c5ed9356a0a1f3367a23f8fbc1bc86239069942537fd678ed"
)
M16_STRATA_CLAIM_ID = "SC-PKC-M16-INFINITY-STRATA-RESULT"
M16_STRATA_ARTIFACT_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_infinity_strata/artifact.json"
)
M16_STRATA_ARTIFACT_SHA256 = (
    "54b0f3c5f2f1880b1f805911df21b72e5427b18871f14907ac17a1d8b48bdd39"
)

PETIT_WEIL_CONTRADICTIONS = (
    re.compile(
        r"faithful petit.{0,120}"
        r"(?:fails|impossible|excluded|ruled out).{0,120}weil descent"
    ),
    re.compile(
        r"weil descent.{0,120}"
        r"(?:required|necessary).{0,120}faithful petit"
    ),
    re.compile(
        r"absence of weil descent.{0,120}"
        r"(?:excludes|rules out|makes.{0,40}impossible)"
    ),
)


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _index(items: Any, key: str = "id") -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        item[key]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get(key), str)
    }


def validate_semantics(
    decisions: dict[str, Any],
    attacks: dict[str, Any],
    source_registry: dict[str, Any],
    typed_state: dict[str, Any],
    claim_state: dict[str, Any],
    engine_state: dict[str, Any],
    lifecycle_state: dict[str, Any],
    shadow_intake: dict[str, Any],
) -> list[str]:
    problems: list[str] = []
    routes = _index(decisions.get("routes"))
    attack_index = _index(attacks.get("attacks"))
    sources = _index(source_registry.get("sources"))
    cells = _index(typed_state.get("cells"), "cell_id")
    typed_claims = _index(typed_state.get("source_claims"))
    typed_barriers = _index(typed_state.get("barriers"))
    claims = _index(claim_state.get("claims"), "claim_id")

    glv_route = routes.get("R-GLV-SEMAEV", {})
    if glv_route.get("status") != "open_parked":
        problems.append("R-GLV-SEMAEV must remain open_parked")
    if glv_route.get("authorized_experiment") is not False:
        problems.append("R-GLV-SEMAEV must not authorize an experiment")

    cube_claim = claims.get(
        "CLM-GLV-INDEPENDENT-CUBES-FIXED-TARGET", {}
    )
    if cube_claim.get("claim_disposition") != "bounded_negative":
        problems.append(
            "independent-cube child claim must remain bounded_negative"
        )
    if cube_claim.get("route_id") != "R-GLV-SEMAEV":
        problems.append("independent-cube child claim lost its parent route")

    covariance_claim = claims.get("CLM-GLV-SEMAEV-COVARIANCE", {})
    if covariance_claim.get("assurance") != ["lean_kernel"]:
        problems.append("GLV covariance assurance must be lean_kernel only")
    stabilizer_claim = claims.get(
        "CLM-GLV-SEMAEV-COORDINATEWISE-STABILIZER", {}
    )
    stabilizer_assurance = stabilizer_claim.get("assurance", [])
    if (
        "certificate_replayed" not in stabilizer_assurance
        or "lean_kernel" in stabilizer_assurance
    ):
        problems.append(
            "full GLV stabilizer classification must remain certificate-backed, "
            "not Lean-kernel classified"
        )

    cube_cell = cells.get("CELL-M-GLV-INDEPENDENT-CUBES", {})
    if cube_cell.get("status") != "decided_closed":
        problems.append("typed independent-cube cell must remain decided_closed")
    faithful_cell = cells.get(
        "CELL-M-GLV-FAITHFUL-PHASE-QUOTIENT", {}
    )
    if faithful_cell.get("status") != "open":
        problems.append("faithful GLV boundary cell must remain open")
    if faithful_cell.get("seed_eligible") is not False:
        problems.append(
            "desired faithful GLV properties cannot be emitted as a mechanism seed"
        )

    typed_counts = typed_state.get("counts", {})
    expected_typed_counts = {
        "source_claims": 29,
        "cells": 7,
        "seed_eligible_cells": 2,
        "desk_decisions": 3,
    }
    for field, expected in expected_typed_counts.items():
        if typed_counts.get(field) != expected:
            problems.append(
                f"typed evidence {field} must remain {expected}"
            )
    m16_cell = cells.get("CELL-M-PKC-SMOOTH-M16", {})
    if m16_cell.get("status") != "open":
        problems.append("M16 scoped blocker must leave the cell open")
    if m16_cell.get("seed_eligible") is not True:
        problems.append("M16 scoped blocker must leave the cell seed-eligible")
    if m16_cell.get("cost_quantity_status") != "partial":
        problems.append("M16 semantic result must leave cost status partial")
    if m16_cell.get("barrier_ids") != [
        "B-PKC-M16-COMPLETE-COST-BRIDGE"
    ]:
        problems.append("M16 cell must retain its open complete-cost barrier")
    for claim_id, label in (
        (
            "SC-PKC-M16-SYMBOLIC-DESK-RESULT",
            "symbolic desk certificate",
        ),
        (
            "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT",
            "semantic bridge certificate",
        ),
        (
            "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT",
            "exceptional-fiber certificate",
        ),
        (
            M16_PROJECTIVE_CLAIM_ID,
            "projective-S17 bridge certificate",
        ),
        (
            M16_RESULTANT_KERNEL_CLAIM_ID,
            "projective-resultant kernel certificate",
        ),
        (
            M16_FROZEN_CR_CLAIM_ID,
            "frozen-Cr specialization kernel certificate",
        ),
        (
            M16_WITNESS_CLAIM_ID,
            "frozen projective witness kernel certificate",
        ),
        (
            M16_GUARDED_CLAIM_ID,
            "guarded projective-system kernel certificate",
        ),
        (
            M16_CHART_CLAIM_ID,
            "exact chart-cover kernel certificate",
        ),
    ):
        if claim_id not in m16_cell.get("source_claim_ids", []):
            problems.append(f"M16 cell must retain its {label}")
    semantic_claim = typed_claims.get(
        "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT", {}
    )
    if semantic_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 semantic bridge assurance must remain certificate_replayed"
        )
    if semantic_claim.get("artifact_sha256") != (
        "963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19"
    ):
        problems.append("M16 semantic bridge artifact hash drifted")
    if semantic_claim.get("evidence_path") != (
        "experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json"
    ):
        problems.append("M16 semantic bridge evidence path drifted")
    if "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT" not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its semantic bridge certificate"
        )
    exceptional_claim = typed_claims.get(
        "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT", {}
    )
    if exceptional_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 exceptional-fiber assurance must remain certificate_replayed"
        )
    if exceptional_claim.get("artifact_sha256") != (
        "578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf"
    ):
        problems.append("M16 exceptional-fiber artifact hash drifted")
    if exceptional_claim.get("evidence_path") != (
        "experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json"
    ):
        problems.append("M16 exceptional-fiber evidence path drifted")
    exceptional_statement = exceptional_claim.get("statement", "")
    if (
        "nonsingular curve y^2=x^3+7" not in exceptional_statement
        or "characteristic not in {2,3,7}" not in exceptional_statement
    ):
        problems.append(
            "M16 exceptional-fiber claim must retain its nonsingular "
            "characteristic boundary"
        )
    exceptional_boundary = exceptional_claim.get("boundary", "")
    for token, label in (
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost quantity"),
        ("solving cost is unpriced", "unpriced solving cost"),
        ("barrier narrowed but open", "narrowed-open barrier"),
    ):
        if token not in exceptional_boundary:
            problems.append(
                f"M16 exceptional-fiber claim must retain {label}"
            )
    if "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT" not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its exceptional-fiber certificate"
        )
    projective_claim = typed_claims.get(M16_PROJECTIVE_CLAIM_ID, {})
    if projective_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 projective-S17 assurance must remain certificate_replayed"
        )
    if projective_claim.get(
        "artifact_sha256"
    ) != M16_PROJECTIVE_ARTIFACT_SHA256:
        problems.append("M16 projective-S17 artifact hash drifted")
    if projective_claim.get("evidence_path") != M16_PROJECTIVE_ARTIFACT_PATH:
        problems.append("M16 projective-S17 evidence path drifted")
    projective_statement = projective_claim.get("statement", "")
    for token, label in (
        ("recursive projective S17", "frozen recursive predicate"),
        ("fixed-degree", "fixed-degree resultant convention"),
        ("reverse projection", "reverse-projection boundary"),
    ):
        if token not in projective_statement:
            problems.append(
                f"M16 projective-S17 claim must retain {label}"
            )
    projective_boundary = projective_claim.get("boundary", "")
    for token, label in (
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost quantity"),
        ("solving cost is unpriced", "unpriced solving cost"),
        ("rank is unpriced", "unpriced rank"),
        ("yield is unpriced", "unpriced yield"),
        (
            "generic C16 forward implication is not computationally replayed or kernel checked",
            "generic-forward assurance boundary",
        ),
        ("barrier narrowed but open", "narrowed-open barrier"),
        ("no experiment authorization", "no-authorization boundary"),
    ):
        if token not in projective_boundary:
            problems.append(
                f"M16 projective-S17 claim must retain {label}"
            )
    if M16_PROJECTIVE_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its projective-S17 certificate"
        )
    resultant_kernel_claim = typed_claims.get(
        M16_RESULTANT_KERNEL_CLAIM_ID, {}
    )
    if resultant_kernel_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 projective-resultant assurance must remain "
            "certificate_replayed"
        )
    if resultant_kernel_claim.get(
        "artifact_sha256"
    ) != M16_RESULTANT_KERNEL_ARTIFACT_SHA256:
        problems.append("M16 projective-resultant artifact hash drifted")
    if resultant_kernel_claim.get(
        "evidence_path"
    ) != M16_RESULTANT_KERNEL_ARTIFACT_PATH:
        problems.append("M16 projective-resultant evidence path drifted")
    resultant_statement = resultant_kernel_claim.get("statement", "")
    for token, label in (
        ("fixed-degree resultant", "fixed-degree theorem"),
        ("literal TASK-018 Sylvester matrix", "literal matrix bridge"),
        ("coefficient unit 1", "unit-one convention"),
        ("zero forms", "zero-form coverage"),
        ("output [1:0]", "projective-infinity coverage"),
    ):
        if token not in resultant_statement:
            problems.append(
                f"M16 projective-resultant claim must retain {label}"
            )
    resultant_boundary = resultant_kernel_claim.get("boundary", "")
    for token, label in (
        (
            "kernel_bound_non_run_certificate",
            "kernel-bound non-run assurance",
        ),
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        (
            "recursive frozen C_r specialization",
            "recursive-specialization blocker",
        ),
        ("formal degrees (2^(r-2),2)", "frozen formal degrees"),
        ("universal C16-to-C2 induction", "universal-induction blocker"),
        ("open_exact_blocker", "exact-blocker status"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost quantity"),
        ("solving cost is unpriced", "unpriced solving cost"),
        ("rank is unpriced", "unpriced rank"),
        ("yield is unpriced", "unpriced yield"),
        ("zero_retention_success", "zero retention"),
        ("experiment authorization", "no-authorization boundary"),
        ("route promotion", "no-promotion boundary"),
    ):
        if token not in resultant_boundary:
            problems.append(
                f"M16 projective-resultant claim must retain {label}"
            )
    if M16_RESULTANT_KERNEL_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its projective-resultant "
            "kernel certificate"
        )
    frozen_cr_claim = typed_claims.get(M16_FROZEN_CR_CLAIM_ID, {})
    if frozen_cr_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 frozen-Cr specialization assurance must remain "
            "certificate_replayed"
        )
    if frozen_cr_claim.get(
        "artifact_sha256"
    ) != M16_FROZEN_CR_ARTIFACT_SHA256:
        problems.append("M16 frozen-Cr specialization artifact hash drifted")
    if frozen_cr_claim.get(
        "evidence_path"
    ) != M16_FROZEN_CR_ARTIFACT_PATH:
        problems.append("M16 frozen-Cr specialization evidence path drifted")
    frozen_cr_statement = frozen_cr_claim.get("statement", "")
    for token, label in (
        ("actual frozenC", "actual frozen family"),
        ("explicit coefficient map", "explicit coefficient map"),
        ("formal degrees (2^(s+1),2)", "fixed formal degrees"),
        ("coefficient unit 1", "unit-one convention"),
        ("affine output [y:1]", "affine-output branch"),
        ("infinity output [1:0]", "infinity-output branch"),
        ("uniformly at most 2^(s+1)", "universal output-degree bound"),
        (
            "without a residual degree hypothesis",
            "unconditional one-step common-root interface",
        ),
    ):
        if token not in frozen_cr_statement:
            problems.append(
                f"M16 frozen-Cr specialization claim must retain {label}"
            )
    frozen_cr_boundary = frozen_cr_claim.get("boundary", "")
    for token, label in (
        (
            "kernel_bound_non_run_certificate",
            "kernel-bound non-run assurance",
        ),
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        (
            "universal C16-to-C2 projective witness extraction",
            "universal witness-extraction blocker",
        ),
        ("full fourteen-node internal projective tree", "full witness tree"),
        ("open_exact_blocker", "exact-blocker status"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost quantity"),
        ("solving cost is unpriced", "unpriced solving cost"),
        ("rank is unpriced", "unpriced rank"),
        ("yield is unpriced", "unpriced yield"),
        ("zero_retention_success", "zero retention"),
        ("experiment authorization", "no-authorization boundary"),
        ("route promotion", "no-promotion boundary"),
    ):
        if token not in frozen_cr_boundary:
            problems.append(
                f"M16 frozen-Cr specialization claim must retain {label}"
            )
    if M16_FROZEN_CR_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its frozen-Cr specialization "
            "kernel certificate"
        )
    witness_claim = typed_claims.get(M16_WITNESS_CLAIM_ID, {})
    if witness_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 frozen projective witness assurance must remain "
            "certificate_replayed"
        )
    if witness_claim.get("artifact_sha256") != M16_WITNESS_ARTIFACT_SHA256:
        problems.append("M16 frozen projective witness artifact hash drifted")
    if witness_claim.get("evidence_path") != M16_WITNESS_ARTIFACT_PATH:
        problems.append(
            "M16 frozen projective witness evidence path drifted"
        )
    witness_statement = witness_claim.get("statement", "")
    for token, label in (
        ("declared-degree output homogeneity", "exact output homogeneity"),
        (
            "projective homogenization/evaluation bridges",
            "projective evaluation bridges",
        ),
        ("every explicit coefficient map", "explicit coefficient map"),
        ("FrozenProjectiveChain", "minimal witness chain"),
        ("stage 14", "C16 stage"),
        (
            "fourteen valid intermediate projective slots",
            "fourteen intermediate slots",
        ),
        ("[1:0] is allowed", "projective infinity"),
        ("[0:0] is excluded", "zero-pair exclusion"),
    ):
        if token not in witness_statement:
            problems.append(
                f"M16 frozen projective witness claim must retain {label}"
            )
    witness_boundary = witness_claim.get("boundary", "")
    for token, label in (
        (
            "kernel_bound_non_run_certificate",
            "kernel-bound non-run assurance",
        ),
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        ("algebraically closed target", "target-field scope"),
        ("no descent", "no base-field descent"),
        ("no direct RecS17 iff GeoCat", "no direct-S17 claim"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost quantity"),
        (
            "solving cost, rank, and yield remain unpriced",
            "unpriced cost boundary",
        ),
        ("zero_retention_success", "zero retention"),
        ("experiment authorization", "no-authorization boundary"),
        ("route promotion", "no-promotion boundary"),
    ):
        if token not in witness_boundary:
            problems.append(
                f"M16 frozen projective witness claim must retain {label}"
            )
    if M16_WITNESS_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its frozen projective witness "
            "kernel certificate"
        )
    guarded_claim = typed_claims.get(M16_GUARDED_CLAIM_ID, {})
    if guarded_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 guarded projective-system assurance must remain "
            "certificate_replayed"
        )
    if guarded_claim.get("artifact_sha256") != M16_GUARDED_ARTIFACT_SHA256:
        problems.append(
            "M16 guarded projective-system artifact hash binding drifted"
        )
    if guarded_claim.get("evidence_path") != M16_GUARDED_ARTIFACT_PATH:
        problems.append(
            "M16 guarded projective-system evidence path drifted"
        )
    guarded_statement = guarded_claim.get("statement", "")
    for token, label in (
        ("exact literal finite MvPolynomial family", "exact finite family"),
        ("frozen stage-14 predicate", "frozen stage-14 scope"),
        ("injective coefficient map", "injective coefficient map"),
        ("source Field k", "source-field scope"),
        ("algebraically closed target Field K", "target-field scope"),
        ("∃ assignment : GuardVar → K", "one GuardVar assignment"),
        ("∀ e : GuardedEquation", "every guarded equation"),
        ("MvPolynomial.eval assignment", "literal polynomial evaluation"),
        ("Four raw scalars U,V,A,B", "raw slot coordinates"),
        ("fourteen projective witness slots", "fourteen witness slots"),
        ("56 variables", "raw variable count"),
        ("fifteen literal H equations", "literal H-equation count"),
        ("fourteen guards", "guard count"),
        ("29 equation-family members", "raw equation-family count"),
        ("total degree at most four", "degree upper bound"),
        ("exclude [0:0]", "zero-pair exclusion"),
        ("retain [1:0]", "projective infinity"),
    ):
        if token not in guarded_statement:
            problems.append(
                f"M16 guarded projective-system claim must retain {label}"
            )
    guarded_boundary = guarded_claim.get("boundary", "")
    for token, label in (
        (
            "kernel_bound_non_run_certificate",
            "kernel-bound non-run assurance",
        ),
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        ("not a parallel recursive syntax", "no parallel recursive syntax"),
        ("no base-field descent", "no base-field descent"),
        ("raw representation counts", "raw-count boundary"),
        (
            "not independent dimensions or relations",
            "no-independence boundary",
        ),
        ("upper bound, not an exact-degree claim", "degree-bound scope"),
        ("compiler_trusted_native_decide", "native-decide disclosure"),
        ("Lean.ofReduceBool", "compiler-trust marker"),
        ("open_non_executable", "open non-executable cell"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost"),
        ("solving cost, rank, and yield remain unpriced", "unpriced costs"),
        ("no expanded direct S17 polynomial", "no direct-S17 claim"),
        ("solver input or run", "no solver input or run"),
        ("chart/gauge reduction", "no chart or gauge reduction"),
        ("relation independence", "no relation independence"),
        ("recovery or total-cost result", "no recovery or total cost"),
        ("hypothesis retention", "no hypothesis retention"),
        ("exact-target search", "no exact-target search"),
        ("experiment authorization", "no experiment authorization"),
        ("route promotion", "no route promotion"),
        ("zero_retention_success", "zero retention"),
    ):
        if token not in guarded_boundary:
            problems.append(
                f"M16 guarded projective-system claim must retain {label}"
            )
    if M16_GUARDED_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its guarded projective-system "
            "kernel certificate"
        )
    chart_claim = typed_claims.get(M16_CHART_CLAIM_ID, {})
    if chart_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 exact chart-cover assurance must remain certificate_replayed"
        )
    if chart_claim.get("artifact_sha256") != M16_CHART_ARTIFACT_SHA256:
        problems.append("M16 exact chart-cover artifact hash binding drifted")
    if chart_claim.get("evidence_path") != M16_CHART_ARTIFACT_PATH:
        problems.append("M16 exact chart-cover evidence path drifted")
    chart_statement = chart_claim.get("statement", "")
    for token, label in (
        ("exact affine/infinity chart-polynomial cover", "exact chart cover"),
        ("frozen stage-14 predicate", "frozen stage-14 scope"),
        ("injective coefficient map", "injective coefficient map"),
        ("source Field k", "source-field scope"),
        ("algebraically closed target Field K", "target-field scope"),
        ("InfinityMask : Finset (Fin 14)", "infinity-mask type"),
        ("[1:0]", "projective infinity"),
        ("[X_i:1]", "affine representative"),
        ("14 - I.card variables", "fixed-mask variable count"),
        ("exactly fifteen literal H equations", "fixed-mask equation count"),
        ("one base equation", "base family"),
        ("thirteen internal step equations", "step family"),
        ("one final equation", "final family"),
        ("degree at most two", "endpoint degree ceiling"),
        ("degree at most four", "internal degree ceiling"),
        ("FrozenProjectiveChain", "projective-chain equivalence"),
        ("prior guarded projective system", "guarded-system equivalence"),
        ("never introduces [0:0]", "zero-pair exclusion"),
    ):
        if token not in chart_statement:
            problems.append(
                f"M16 exact chart-cover claim must retain {label}"
            )
    chart_boundary = chart_claim.get("boundary", "")
    for token, label in (
        (
            "kernel_bound_non_run_certificate",
            "kernel-bound non-run assurance",
        ),
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        ("no base-field descent", "no base-field descent"),
        ("2^14 logical masks are not enumerated or materialized", "no mask sweep"),
        ("representation inventory", "representation-count boundary"),
        (
            "not independent dimensions or relations",
            "no-independence boundary",
        ),
        (
            "upper bounds rather than exact-degree claims",
            "degree-bound scope",
        ),
        ("card_chartEquation is compiler_trusted_native_decide", "native trust"),
        ("Lean.ofReduceBool", "compiler-trust marker"),
        ("card_chartVar", "ordinary variable-count proof"),
        ("open_non_executable", "open non-executable cell"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost"),
        ("solving cost, rank, and yield remain unpriced", "unpriced costs"),
        ("no expanded direct S17 polynomial", "no direct-S17 claim"),
        ("production mask sweep", "no production mask sweep"),
        ("solver input or run", "no solver input or run"),
        ("relation independence", "no relation independence"),
        ("recovery or total-cost result", "no recovery or total cost"),
        ("hypothesis retention", "no hypothesis retention"),
        ("exact-target search", "no exact-target search"),
        ("experiment authorization", "no experiment authorization"),
        ("route rejection", "no route rejection"),
        ("route promotion", "no route promotion"),
        ("zero_retention_success", "zero retention"),
    ):
        if token not in chart_boundary:
            problems.append(
                f"M16 exact chart-cover claim must retain {label}"
            )
    if M16_CHART_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its exact chart-cover "
            "kernel certificate"
        )
    strata_claim = typed_claims.get(M16_STRATA_CLAIM_ID, {})
    if strata_claim.get("read_status") != "certificate_replayed":
        problems.append(
            "M16 infinity-stratum assurance must remain certificate_replayed"
        )
    if strata_claim.get("artifact_sha256") != M16_STRATA_ARTIFACT_SHA256:
        problems.append("M16 infinity-stratum artifact hash binding drifted")
    if strata_claim.get("evidence_path") != M16_STRATA_ARTIFACT_PATH:
        problems.append("M16 infinity-stratum evidence path drifted")
    strata_statement = strata_claim.get("statement", "")
    for token, label in (
        ("TASK-023 stage-14 chart cover", "upstream exact chart cover"),
        ("squared projective determinants", "local infinity identities"),
        ("H([1:0],b,[1:0]) = b.v^2", "double-infinity identity"),
        ("AffineInputFamily", "affine-input assumption"),
        ("adjacent infinity slots are impossible", "separation necessity"),
        ("endpoint determinant equations", "endpoint conditions"),
        ("q.u / q.v", "forced-neighbor coordinate"),
        ("AdmissibleInfinityMask", "necessary mask predicate"),
        ("16384 total masks", "full logical mask count"),
        ("987 separated masks", "separated mask count"),
        ("both endpoint determinants are nonzero", "endpoint assumptions"),
        ("377 masks", "interior mask count"),
    ):
        if token not in strata_statement:
            problems.append(
                f"M16 infinity-stratum claim must retain {label}"
            )
    strata_boundary = strata_claim.get("boundary", "")
    for token, label in (
        ("kernel_bound_non_run_certificate", "kernel-bound assurance"),
        ("source_independence is not_established", "source independence"),
        ("calibration is excluded_nonexperimental", "calibration"),
        ("requires affine external inputs", "affine-input scope"),
        (
            "additionally requires both endpoint determinants",
            "conditional endpoint scope",
        ),
        ("necessary, not sufficient or unique", "necessity boundary"),
        ("not enumerated or materialized", "no production enumeration"),
        ("logical cover inventory", "logical-count boundary"),
        ("card_infinityMask", "full-count trust disclosure"),
        ("card_separatedInfinityMask", "separated-count trust disclosure"),
        (
            "card_interiorSeparatedInfinityMask",
            "interior-count trust disclosure",
        ),
        ("compiler_trusted_native_decide", "native trust"),
        ("Lean.ofReduceBool", "compiler-trust marker"),
        ("open_non_executable", "open non-executable cell"),
        ("CQ-SEMAEV-S17-SYSTEM-COST remains partial", "partial cost"),
        ("sufficient mask orchestration", "remaining mask blocker"),
        ("no sufficient mask-selection algorithm", "no sufficiency overclaim"),
        ("solver input or run", "no solver input or run"),
        ("relation independence", "no relation independence"),
        ("recovery or total-cost result", "no recovery or total cost"),
        ("hypothesis retention", "no hypothesis retention"),
        ("exact-target search", "no exact-target search"),
        ("experiment authorization", "no experiment authorization"),
        ("route rejection", "no route rejection"),
        ("route promotion", "no route promotion"),
        ("zero_retention_success", "zero retention"),
    ):
        if token not in strata_boundary:
            problems.append(
                f"M16 infinity-stratum claim must retain {label}"
            )
    if M16_STRATA_CLAIM_ID not in m16_cell.get(
        "cost_quantity", {}
    ).get("source_claim_ids", []):
        problems.append(
            "M16 cost quantity must retain its infinity-stratum "
            "kernel certificate"
        )
    if M16_STRATA_CLAIM_ID not in m16_cell.get("source_claim_ids", []):
        problems.append(
            "M16 cell must retain its infinity-stratum kernel certificate"
        )
    m16_barrier = typed_barriers.get(
        "B-PKC-M16-COMPLETE-COST-BRIDGE", {}
    )
    if m16_barrier.get("disposition") != "open":
        problems.append("M16 complete-cost barrier must remain open")
    if "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT" not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its semantic bridge certificate"
        )
    if "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT" not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its exceptional-fiber certificate"
        )
    if M16_PROJECTIVE_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its projective-S17 certificate"
        )
    if M16_RESULTANT_KERNEL_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its projective-resultant "
            "kernel certificate"
        )
    if M16_FROZEN_CR_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its frozen-Cr "
            "specialization kernel certificate"
        )
    if M16_WITNESS_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its frozen projective "
            "witness kernel certificate"
        )
    if M16_GUARDED_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its guarded "
            "projective-system kernel certificate"
        )
    if M16_CHART_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its exact chart-cover "
            "kernel certificate"
        )
    if M16_STRATA_CLAIM_ID not in m16_barrier.get(
        "source_claim_ids", []
    ):
        problems.append(
            "M16 complete-cost barrier must retain its infinity-stratum "
            "kernel certificate"
        )
    m16_scope = m16_barrier.get("exact_scope", "")
    for token, label in (
        ("TASK-019 kernel-checks", "TASK-019 kernel result"),
        ("zero forms", "zero-form coverage"),
        ("TASK-020 kernel-checks", "TASK-020 specialization result"),
        ("actual frozenC family", "actual frozen family"),
        ("formal degrees (2^(s+1),2)", "frozen formal degrees"),
        ("universal output-degree bound", "universal output-degree bound"),
        (
            "unconditional one-step common-projective-root equivalence",
            "unconditional one-step common-root interface",
        ),
        ("TASK-021 kernel-checks", "TASK-021 kernel result"),
        (
            "all-stage frozen projective witness-chain equivalence",
            "universal witness extraction",
        ),
        (
            "fourteen intermediate projective slots",
            "fourteen intermediate slots",
        ),
        (
            "TASK-022 kernel-checks",
            "TASK-022 guarded representation",
        ),
        (
            "56 scalar variables",
            "raw variable count",
        ),
        (
            "29 equation-family members",
            "raw equation-family count",
        ),
        (
            "total degree at most four",
            "degree upper bound",
        ),
        (
            "counts do not establish dimension",
            "raw-count independence boundary",
        ),
        (
            "TASK-023 kernel-checks",
            "TASK-023 chart-cover result",
        ),
        (
            "exact affine/infinity chart-polynomial cover",
            "exact chart-cover representation",
        ),
        (
            "14 - I.card variables",
            "fixed-mask variable count",
        ),
        (
            "fifteen H equations",
            "fixed-mask equation count",
        ),
        (
            "degree ceilings 2, 4, and 2",
            "family degree ceilings",
        ),
        (
            "2^14 logical masks are not enumerated or materialized",
            "no production mask enumeration",
        ),
        (
            "TASK-024 kernel-checks",
            "TASK-024 infinity-stratum result",
        ),
        (
            "necessary infinity-stratum pruning",
            "necessary mask pruning",
        ),
        (
            "16384 masks to 987 separated masks",
            "separated mask reduction",
        ),
        (
            "377 interior masks",
            "conditional interior mask count",
        ),
        (
            "necessary, not sufficient or unique",
            "necessity-only boundary",
        ),
        (
            "mask selection or finite-cover orchestration",
            "remaining finite-cover blocker",
        ),
    ):
        if token not in m16_scope:
            problems.append(f"M16 complete-cost barrier must retain {label}")
    if (
        "pending a kernel-checked fixed-degree projective resultant "
        "common-root theorem"
    ) in m16_scope:
        problems.append(
            "M16 complete-cost barrier cannot reopen the kernel-checked "
            "fixed-degree theorem"
        )
    if (
        "open only on the exact recursive frozen C_r specialization"
        in m16_scope
    ):
        problems.append(
            "M16 complete-cost barrier cannot reopen the kernel-checked "
            "frozen-Cr specialization"
        )
    reopening_text = " ".join(
        item
        for item in m16_barrier.get("reopening_conditions", [])
        if isinstance(item, str)
    )
    for token in (
        "exact TASK-023 affine/infinity chart-polynomial cover",
        "completed TASK-024 necessary infinity-stratum filter",
        "mask selection or finite-cover orchestration",
        "without enumerating all 2^14 masks by default",
        "without sweeping all 987 separated masks by default",
        "usable yield and rank",
        "solving, recovery, and sparse-linear-algebra costs",
        "matched generic baseline",
    ):
        if token not in reopening_text:
            problems.append(
                f"M16 complete-cost reopening must require {token}"
            )
    if (
        "Kernel-check a fixed-degree projective resultant common-root theorem"
        in reopening_text
    ):
        problems.append(
            "M16 complete-cost reopening cannot require an already "
            "kernel-checked theorem"
        )
    if "Kernel-check the exact recursive frozen C_r specialization" in reopening_text:
        problems.append(
            "M16 complete-cost reopening cannot require the already "
            "kernel-checked frozen-Cr specialization"
        )
    for field, token, label in (
        (
            "relation_action",
            "remaining mechanism gap",
            "narrowed mechanism gap",
        ),
        (
            "relation_action",
            "TASK-020 kernel-checks",
            "TASK-020 specialization result",
        ),
        (
            "relation_action",
            "actual frozenC family",
            "actual frozen family",
        ),
        (
            "relation_action",
            "universal all-stage frozen witness-chain equivalence",
            "universal witness extraction",
        ),
        (
            "relation_action",
            "TASK-022 kernel-checks",
            "TASK-022 guarded representation",
        ),
        (
            "relation_action",
            "56 scalar variables",
            "raw variable count",
        ),
        (
            "relation_action",
            "TASK-023 kernel-checks",
            "TASK-023 chart-cover result",
        ),
        (
            "relation_action",
            "14 - I.card affine scalar variables",
            "fixed-mask variable count",
        ),
        (
            "relation_action",
            "degree ceilings 2/4/2",
            "chart degree ceilings",
        ),
        (
            "relation_action",
            "TASK-024 kernel-checks",
            "TASK-024 infinity-stratum result",
        ),
        (
            "relation_action",
            "16384 masks to 987 separated masks",
            "separated mask reduction",
        ),
        (
            "relation_action",
            "377 interior masks",
            "conditional interior mask count",
        ),
        (
            "relation_action",
            "mask selection or finite-cover orchestration",
            "open finite-cover blocker",
        ),
        (
            "boundary",
            "all-stage frozen projective witness chain",
            "universal all-stage witness chain",
        ),
        (
            "boundary",
            "exact literal finite MvPolynomial family",
            "exact literal finite family",
        ),
        (
            "boundary",
            "not an expanded direct S17 polynomial",
            "no direct-S17 overclaim",
        ),
        (
            "boundary",
            "exact affine/infinity chart-polynomial cover",
            "exact chart-cover result",
        ),
        (
            "boundary",
            "2^14 logical masks are not enumerated or materialized",
            "no production mask enumeration",
        ),
        (
            "boundary",
            "exact necessary infinity-stratum pruning",
            "exact infinity-stratum result",
        ),
        (
            "boundary",
            "16384 masks to 987 separated masks",
            "separated mask reduction",
        ),
        (
            "boundary",
            "377 interior masks",
            "conditional interior mask count",
        ),
        (
            "boundary",
            "not a sufficient or unique mask-selection algorithm",
            "no sufficiency overclaim",
        ),
        (
            "boundary",
            "counts do not establish independent dimensions or relations",
            "no raw-count independence overclaim",
        ),
        ("boundary", "zero_retention_success", "zero retention"),
        ("boundary", "hypothesis retention", "no hypothesis retention"),
        ("boundary", "experiment authorization", "no experiment authorization"),
        ("boundary", "route promotion", "no route promotion"),
    ):
        if token not in str(m16_cell.get(field, "")):
            problems.append(f"M16 cell must retain {label}")
    if m16_cell.get("authorization") != "none":
        problems.append("M16 semantic result cannot authorize execution")
    if any(
        decision.get("cell_id") == "CELL-M-PKC-SMOOTH-M16"
        for decision in typed_state.get("desk_decisions", [])
    ):
        problems.append("M16 scoped blocker cannot be stored as a desk closure")

    petit_route = routes.get("R-PETIT-COMPOSED-MAPS", {})
    petit_attack = attack_index.get("IC-4-petit-composed-map", {})
    if petit_route.get("status") != "open_parked":
        problems.append("faithful Petit route must remain open_parked")
    if petit_attack.get("verdict_class") != "open-zone":
        problems.append("faithful Petit registry entry must remain an open-zone")
    petit_assertions = " ".join(
        str(petit_attack.get(field, ""))
        for field in (
            "one_line",
            "secp256k1_constants",
            "verdict",
            "blocked_on",
        )
    ).casefold()
    if "prime-field" not in petit_assertions:
        problems.append("Petit registry must state the prime-field construction")
    if "implements neither" not in petit_assertions:
        problems.append(
            "Petit registry must state that historical P4 implements neither "
            "PKC 2016 construction"
        )
    if "absence of weil descent does not exclude" not in petit_assertions:
        problems.append(
            "Petit registry must separate prime-field constructions from "
            "the Weil-descent boundary"
        )
    petit_route_text = " ".join(
        str(petit_route.get(field, ""))
        for field in ("applicability", "current_evidence", "anti_overclaim")
    ).casefold()
    if (
        "faithful prime-field" not in petit_route_text
        or "did not implement either" not in petit_route_text
    ):
        problems.append(
            "decision substrate contradicts faithful Petit/P4 semantics"
        )
    petit_semantic_surface = f"{petit_assertions} {petit_route_text}"
    if any(
        pattern.search(petit_semantic_surface)
        for pattern in PETIT_WEIL_CONTRADICTIONS
    ):
        problems.append(
            "faithful Petit cannot be rejected by the absence of Weil descent"
        )
    weil_route = routes.get("R-WEIL-DESCENT", {})
    if (
        weil_route.get("status") != "ruled_out_for_target"
        or set(weil_route.get("attack_registry_ids", []))
        & set(petit_route.get("attack_registry_ids", []))
    ):
        problems.append(
            "Weil descent and faithful Petit must remain distinct route assertions"
        )

    kudo = sources.get("kudo_yokota_takahashi_yasuda2018", {})
    if kudo.get("full_text_status") != "full_text_unread":
        problems.append("Kudo CANS 2018 must remain full_text_unread")
    wcc = sources.get("yokota_kudo_yasuda2017_wcc", {})
    if wcc.get("full_text_status") != "full_text_inspected":
        problems.append("WCC 2017 must retain its inspected full-text status")
    if (
        wcc.get("title")
        == kudo.get("title")
        or wcc.get("authors") == kudo.get("authors")
    ):
        problems.append("WCC 2017 and CANS 2018 must remain distinct sources")
    petit_source = sources.get("petit_kosters_messeng2016", {})
    if petit_source.get("full_text_status") != "full_text_inspected":
        problems.append("PKC 2016 must retain its inspected full-text status")

    phase = decisions.get("phase_policy", {})
    execution = decisions.get("execution_gates", {})
    if phase.get("phase") != "evidence-bounded-desk-priority":
        problems.append("current phase must remain evidence-bounded desk priority")
    if phase.get("bounded_exploration_authorized") is not False:
        problems.append("current phase must authorize zero bounded experiments")
    if execution.get("exploration", {}).get("authorized") is not False:
        problems.append("current execution gate must keep exploration closed")
    if any(route.get("authorized_experiment") for route in routes.values()):
        problems.append("no route may authorize an experiment")
    if claim_state.get("authorization") != {
        "experiments": 0,
        "route_promotions": 0,
        "exact_target_runs": 0,
    }:
        problems.append("claim state authorization boundary drifted")
    generation = engine_state.get("hypothesis_generation", {})
    if any(
        seed.get("authorization") != "none"
        for seed in generation.get("generated_seeds", [])
    ):
        problems.append("generated research-question seeds must be non-executable")
    if generation.get("research_claims", {}).get("state_sha256") != (
        engine_state.get("source_hashes", {}).get(
            "research_claim_state_sha256"
        )
    ):
        problems.append("engine claim-state digest binding is inconsistent")
    if lifecycle_state.get("authorization") != {
        "experiments": 0,
        "route_promotions": 0,
        "exact_target_runs": 0,
    }:
        problems.append("v0.2 lifecycle authorization boundary drifted")
    shadow_counts = shadow_intake.get("counts", {})
    if any(
        shadow_counts.get(key) != 0
        for key in (
            "admissible",
            "recommended",
            "authorized",
            "route_promotions",
            "exact_target_experiments",
        )
    ):
        problems.append("shadow intake must remain non-executable")
    if any(
        stub.get("executable") is not False
        or stub.get("authorized") is not False
        for stub in shadow_intake.get("proposal_stubs", [])
    ):
        problems.append("shadow proposal stubs cannot become executable")
    if any(
        stub.get("route_id") == "R-GLV-SEMAEV"
        for stub in shadow_intake.get("proposal_stubs", [])
    ):
        problems.append(
            "unspecified phase-preserving GLV properties cannot enter intake"
        )
    m16_stubs = [
        stub
        for stub in shadow_intake.get("proposal_stubs", [])
        if stub.get("anchor_id") == "CELL-M-PKC-SMOOTH-M16"
    ]
    if (
        len(m16_stubs) != 1
        or m16_stubs[0].get("stub_id") != "RSI-D8BBA6340789"
    ):
        problems.append("M16 must retain exactly its canonical shadow stub")

    maintenance = decisions.get("maintenance_cycle", {})
    if (
        maintenance.get("task_id") != "TASK-010"
        or maintenance.get("status") != "completed_accepted"
        or maintenance.get("authorizes_experiment") is not False
        or maintenance.get("promotes_route") is not False
    ):
        problems.append("TASK-010 maintenance cycle boundary drifted")
    return sorted(set(problems))


def main() -> int:
    decisions = load_json("repo/ECDLP_DECISION_SUBSTRATE.json")
    claim_policy_problems, _ = validate_claim_policy(
        load_json("repo/RESEARCH_CLAIMS_V0.json"),
        decisions,
    )
    problems = claim_policy_problems + validate_semantics(
        decisions,
        load_json("data/attack_registry.json"),
        load_json("data/source_registry.json"),
        load_json("data/typed_evidence_state.json"),
        load_json("data/research_claim_state.json"),
        load_json("data/research_engine_state.json"),
        load_json("data/research_engine_v02_state.json"),
        load_json("data/research_engine_shadow_intake.json"),
    )
    problems = sorted(set(problems))
    if problems:
        print("scientific-semantic gate FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(
        "scientific-semantic gate passed: Petit/Weil, GLV child/route, "
        "assurance, source read status, shadow intake, and zero authorization agree."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
