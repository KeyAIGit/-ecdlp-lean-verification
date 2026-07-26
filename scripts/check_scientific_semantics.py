#!/usr/bin/env python3
"""Cross-check canonical scientific assertions across independently owned files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


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
    petit_source = sources.get("petit_kosters_messeng2016", {})
    if petit_source.get("full_text_status") != "full_text_inspected":
        problems.append("PKC 2016 must retain its inspected full-text status")

    phase = decisions.get("phase_policy", {})
    execution = decisions.get("execution_gates", {})
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

    maintenance = decisions.get("maintenance_cycle", {})
    if (
        maintenance.get("task_id") != "TASK-010"
        or maintenance.get("authorizes_experiment") is not False
        or maintenance.get("promotes_route") is not False
    ):
        problems.append("TASK-010 maintenance cycle boundary drifted")
    return sorted(set(problems))


def main() -> int:
    problems = validate_semantics(
        load_json("repo/ECDLP_DECISION_SUBSTRATE.json"),
        load_json("data/attack_registry.json"),
        load_json("data/source_registry.json"),
        load_json("data/typed_evidence_state.json"),
        load_json("data/research_claim_state.json"),
        load_json("data/research_engine_state.json"),
        load_json("data/research_engine_v02_state.json"),
        load_json("data/research_engine_shadow_intake.json"),
    )
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
