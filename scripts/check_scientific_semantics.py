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
        "source_claims": 24,
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
    m16_scope = m16_barrier.get("exact_scope", "")
    for token, label in (
        ("TASK-019 kernel-checks", "TASK-019 kernel result"),
        ("zero forms", "zero-form coverage"),
        (
            "recursive frozen C_r specialization",
            "recursive-specialization blocker",
        ),
        ("formal degrees (2^(r-2),2)", "frozen formal degrees"),
        ("universal C16-to-C2 induction", "universal-induction blocker"),
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
    reopening_text = " ".join(
        item
        for item in m16_barrier.get("reopening_conditions", [])
        if isinstance(item, str)
    )
    if (
        "recursive frozen C_r specialization" not in reopening_text
        or "universal C16-to-C2 induction" not in reopening_text
    ):
        problems.append(
            "M16 complete-cost reopening must require recursive "
            "specialization and universal induction"
        )
    if (
        "Kernel-check a fixed-degree projective resultant common-root theorem"
        in reopening_text
    ):
        problems.append(
            "M16 complete-cost reopening cannot require an already "
            "kernel-checked theorem"
        )
    for field, token, label in (
        (
            "relation_action",
            "remaining exact mechanism gap",
            "narrowed mechanism gap",
        ),
        (
            "relation_action",
            "recursive frozen C_r specialization",
            "recursive specialization",
        ),
        (
            "relation_action",
            "universal C16-to-C2 induction",
            "universal induction",
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
