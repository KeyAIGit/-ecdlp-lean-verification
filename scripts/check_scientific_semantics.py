#!/usr/bin/env python3
"""Cross-check canonical scientific assertions across independently owned files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from research_claims import validate_and_build as validate_claim_policy

ROOT = Path(__file__).resolve().parent.parent

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
        "source_claims": 20,
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
        problems.append("M16 symbolic result must leave cost status partial")
    if m16_cell.get("barrier_ids") != [
        "B-PKC-M16-COMPLETE-COST-BRIDGE"
    ]:
        problems.append("M16 cell must retain its open complete-cost barrier")
    if "SC-PKC-M16-SYMBOLIC-DESK-RESULT" not in m16_cell.get(
        "source_claim_ids", []
    ):
        problems.append("M16 cell must retain its symbolic desk certificate")
    if m16_cell.get("authorization") != "none":
        problems.append("M16 symbolic result cannot authorize execution")
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
