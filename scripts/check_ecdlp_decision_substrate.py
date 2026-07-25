#!/usr/bin/env python3
"""Validate the canonical secp256k1 ECDLP decision substrate.

This gate checks cross-registry identity, evidence paths, route/foundation
ownership, and the split between bounded exploration and promotion. It
validates project decisions; it does not validate mathematical claims
independently of their cited Lean or literature evidence.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
ATTACKS = ROOT / "data" / "attack_registry.json"
FORMAL = ROOT / "repo" / "FORMAL_SUBSTRATE.json"
RESULTS = ROOT / "data" / "result_registry.json"
SOURCES = ROOT / "data" / "source_registry.json"
HYPOTHESES = ROOT / "experiments" / "HYPOTHESES.yaml"
TASKS = ROOT / "tasks" / "ECDLP_RESEARCH.md"
NEXT_TASKS = ROOT / "tasks" / "NEXT.md"
ENGINE_POLICY = ROOT / "repo" / "RESEARCH_ENGINE_V0.json"
ENGINE_STATE = ROOT / "data" / "research_engine_state.json"

STRUCTURAL_DECISION_ID = "RS-2026-07-24-001"
STRUCTURAL_SUPERSEDES = "RS-2026-07-22-001"
STRUCTURAL_ITERATION_ID = "GLV-SEMAEV-ITER-001"
STRUCTURAL_ROUTE_ID = "R-GLV-SEMAEV"
STRUCTURAL_HYPOTHESIS_ID = "HYP_GLV_SEMAEV_001"
STRUCTURAL_TASK_ID = "TASK-009"
STRUCTURAL_FOUNDATION_ID = "F-SEMAEV-ELIMINATION"

ROUTE_STATUSES = {
    "guardrail",
    "baseline",
    "ruled_out_for_target",
    "constant_factor_only",
    "open_parked",
    "conditional_only",
    "separate_threat_model",
    "monitor",
}
FOUNDATION_DECISIONS = {
    "build_now",
    "build_if_selected",
    "retain_frontier",
    "monitor_only",
}
FOUNDATION_STATUSES = {"complete", "partial", "not_started"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
REQUIRED_ROUTE_FIELDS = {
    "id",
    "title",
    "threat_models",
    "attack_registry_ids",
    "status",
    "priority",
    "applicability",
    "assumptions",
    "known_cost",
    "current_evidence",
    "success_gate",
    "stop_condition",
    "next_action",
    "authorized_experiment",
    "foundation_ids",
    "formal_node_ids",
    "lean_anchors",
    "evidence_files",
    "source_ids",
    "anti_overclaim",
}
REQUIRED_FOUNDATION_FIELDS = {
    "id",
    "title",
    "decision",
    "priority",
    "build_now",
    "implementation_status",
    "needed_by_route_ids",
    "formal_node_ids",
    "mathlib_status",
    "deliverable",
    "resume_condition",
}
REQUIRED_SELECTION_FIELDS = {
    "decision_id",
    "performed_on",
    "completed_on",
    "supersedes",
    "decision",
    "selection_scope",
    "iteration_id",
    "selected_route_ids",
    "promoted_route_ids",
    "hypothesis_id",
    "task_id",
    "foundation_ids",
    "outcome",
    "kernel_acceptance",
    "ledger_acceptance",
    "evaluated_route_ids",
    "gate_result",
    "rationale",
    "reconsideration_triggers",
    "operational_effects",
}
STALE_ACTIVE_PHRASES = (
    "Hypothesis remains ACTIVE",
    "hypothesis remains ACTIVE",
    "HYP_GLV_SEMAEV_001 ACTIVE",
)
STALE_STATUS_FILES = (
    "BARRIERS.md",
    "experiments/README.md",
    "experiments/p0_glv_semaev/README.md",
    "experiments/p0_glv_semaev/RESULTS.md",
    "experiments/p1_petit/README.md",
    "experiments/p1_petit/RESULTS.md",
    "experiments/p1_petit_m3/README.md",
    "experiments/p1_petit_m3/RESULTS.md",
    "experiments/p3_sm_system/README.md",
    "experiments/p3_sm_system/RESULTS.md",
    "experiments/p4_petit/README.md",
    "experiments/p4_petit/RESULTS.md",
    "notes/RESEARCH_MAP.md",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ids_are_unique(items: list[dict], label: str, problems: list[str]) -> set[str]:
    ids = [item.get("id") for item in items]
    if None in ids:
        problems.append(f"{label}: item missing id")
    if len(ids) != len(set(ids)):
        problems.append(f"{label}: duplicate ids")
    return {item for item in ids if item is not None}


def parse_hypotheses() -> dict[str, dict[str, str]]:
    text = HYPOTHESES.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^  - id: (?P<id>[A-Z0-9_]+)\s*$"
        r"(?P<body>.*?)(?=^  - id: [A-Z0-9_]+\s*$|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    parsed: dict[str, dict[str, str]] = {}
    for match in pattern.finditer(text):
        fields: dict[str, str] = {}
        for name in (
            "direction",
            "status",
            "resume_after",
            "structural_lane",
            "structural_decision_id",
            "structural_iteration_id",
            "structural_route_id",
            "structural_task_id",
            "structural_foundation_id",
        ):
            field = re.search(
                rf"^    {name}:\s*(?:\"(?P<quoted>[^\"]*)\"|(?P<plain>.+))$",
                match.group("body"),
                flags=re.MULTILINE,
            )
            if field:
                fields[name] = (field.group("quoted") or field.group("plain")).strip()
        parsed[match.group("id")] = fields
    return parsed


def validate() -> list[str]:
    problems: list[str] = []
    data = load_json(DECISIONS)
    attack_data = load_json(ATTACKS)
    formal_data = load_json(FORMAL)
    result_data = load_json(RESULTS)
    source_data = load_json(SOURCES)
    engine_policy = load_json(ENGINE_POLICY)
    engine_state = load_json(ENGINE_STATE)

    routes = data.get("routes", [])
    foundations = data.get("foundations", [])
    route_ids = ids_are_unique(routes, "routes", problems)
    foundation_ids = ids_are_unique(foundations, "foundations", problems)
    attack_ids = {attack["id"] for attack in attack_data["attacks"]}
    formal_ids = {node["id"] for node in formal_data["critical_nodes"]}
    declaration_ids = set(result_data["declarations"])
    source_ids = {source["id"] for source in source_data["sources"]}
    threat_ids = ids_are_unique(data.get("threat_models", []), "threat_models", problems)
    hypotheses = parse_hypotheses()

    primary_models = [
        model["id"] for model in data["threat_models"] if model.get("primary")
    ]
    if primary_models != ["classical-single-target-plain"]:
        problems.append(
            "exactly classical-single-target-plain must be the primary threat model"
        )
    if data["phase_policy"].get("phase") != "research-engine-v0":
        problems.append("the current phase must be research-engine-v0")
    if data["phase_policy"].get("experiments_authorized") is not False:
        problems.append("experiments_authorized must remain false")
    if data["phase_policy"].get("bounded_exploration_authorized") is not False:
        problems.append(
            "bounded_exploration_authorized must be false after the structural iteration"
        )
    if data["phase_policy"].get("promotion_experiments_authorized") is not False:
        problems.append("promotion experiments must remain unauthorized")
    if data["phase_policy"].get("selected_attack_route") is not None:
        problems.append("completed structural selection must keep selected_attack_route=null")
    execution_gates = data.get("execution_gates", {})
    if execution_gates.get("exploration", {}).get("authorized") is not False:
        problems.append(
            "execution_gates.exploration must remain closed after the structural iteration"
        )
    if execution_gates.get("promotion", {}).get("authorized") is not False:
        problems.append("execution_gates.promotion must remain closed")
    if execution_gates.get("exploration", {}).get("policy_source") != (
        "repo/RESEARCH_ENGINE_V0.json"
    ):
        problems.append("exploration gate must point at RESEARCH_ENGINE_V0.json")
    structural_gate = execution_gates.get("structural")
    if not isinstance(structural_gate, dict):
        problems.append("execution_gates.structural must be an object")
        structural_gate = {}
    expected_structural_gate = {
        "authorized": False,
        "status": "completed",
        "kind": "non_experiment",
        "authorizes_experiment": False,
        "promotes_route": False,
        "decision_id": STRUCTURAL_DECISION_ID,
        "iteration_id": STRUCTURAL_ITERATION_ID,
        "selected_route_ids": [STRUCTURAL_ROUTE_ID],
        "hypothesis_id": STRUCTURAL_HYPOTHESIS_ID,
        "task_id": STRUCTURAL_TASK_ID,
        "foundation_ids": [STRUCTURAL_FOUNDATION_ID],
    }
    for field, expected in expected_structural_gate.items():
        if structural_gate.get(field) != expected:
            problems.append(
                f"execution_gates.structural.{field} must be {expected!r}"
            )
    if engine_policy.get("gates", {}).get("exploration", {}).get(
        "authorized"
    ) is not True:
        problems.append("Research Engine must retain its bounded-exploration capability")
    if engine_policy.get("gates", {}).get("promotion", {}).get(
        "authorized"
    ) is not False:
        problems.append("Research Engine policy must keep promotion closed")
    engine_gate_status = engine_state.get("gate_status", {})
    if engine_gate_status.get("promotion_authorized") is not False:
        problems.append("generated engine state must keep promotion closed")
    selected_count = engine_state.get("counts", {}).get("selected_explorations")
    authorized_count = engine_state.get("counts", {}).get(
        "authorized_exploration_candidates"
    )
    ready_count = engine_state.get("counts", {}).get("ready_explorations")
    max_selected = engine_policy.get("gates", {}).get("exploration", {}).get(
        "max_selected_per_cycle"
    )
    if (
        not isinstance(selected_count, int)
        or not isinstance(max_selected, int)
        or selected_count > max_selected
    ):
        problems.append("generated selected sequence exceeds the exploration gate")
    if selected_count != 0 or authorized_count != 0 or ready_count != 0:
        problems.append(
            "the completed structural decision requires zero selected, authorized, and ready "
            "Research Engine explorations"
        )

    selection = data.get("route_selection")
    if not isinstance(selection, dict):
        problems.append("route_selection must be an object")
        selection = {}
    missing_selection = REQUIRED_SELECTION_FIELDS - set(selection)
    extra_selection = set(selection) - REQUIRED_SELECTION_FIELDS
    if missing_selection:
        problems.append(
            f"route_selection: missing fields {sorted(missing_selection)}"
        )
    if extra_selection:
        problems.append(
            f"route_selection: unknown fields {sorted(extra_selection)}"
        )
    expected_selection = {
        "decision_id": STRUCTURAL_DECISION_ID,
        "performed_on": "2026-07-24",
        "completed_on": "2026-07-24",
        "supersedes": STRUCTURAL_SUPERSEDES,
        "decision": "select_one_bounded_structural",
        "selection_scope": "bounded_structural_non_experiment",
        "iteration_id": STRUCTURAL_ITERATION_ID,
        "selected_route_ids": [STRUCTURAL_ROUTE_ID],
        "promoted_route_ids": [],
        "hypothesis_id": STRUCTURAL_HYPOTHESIS_ID,
        "task_id": STRUCTURAL_TASK_ID,
        "foundation_ids": [STRUCTURAL_FOUNDATION_ID],
        "outcome": "diagonal_only_bounded_negative",
    }
    for field, expected in expected_selection.items():
        if selection.get(field) != expected:
            problems.append(f"route_selection.{field} must be {expected!r}")
    selected_structural = selection.get("selected_route_ids")
    if not isinstance(selected_structural, list) or len(selected_structural) != 1:
        problems.append("exactly one bounded structural route must be selected")
    promoted = selection.get("promoted_route_ids")
    if not isinstance(promoted, list) or promoted:
        problems.append("route_selection.promoted_route_ids must be an empty array")
    evaluated = selection.get("evaluated_route_ids")
    if not isinstance(evaluated, list) or len(evaluated) != len(set(evaluated)):
        problems.append("route_selection.evaluated_route_ids must be a unique array")
    elif set(evaluated) != route_ids:
        problems.append(
            "route_selection.evaluated_route_ids must contain every registered route"
        )
    if not re.fullmatch(
        r"RS-\d{4}-\d{2}-\d{2}-\d{3}", str(selection.get("decision_id", ""))
    ):
        problems.append("route_selection.decision_id has an invalid format")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(selection.get("performed_on", ""))):
        problems.append("route_selection.performed_on must be YYYY-MM-DD")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(selection.get("completed_on", ""))):
        problems.append("route_selection.completed_on must be YYYY-MM-DD")
    kernel_acceptance = selection.get("kernel_acceptance")
    if not isinstance(kernel_acceptance, dict):
        problems.append("route_selection.kernel_acceptance must be an object")
    else:
        expected_kernel_acceptance = {
            "commit": "1bba09ff1d8682187365996d9b190044aea333f9",
            "workflow_run": 30142661986,
            "lean": "v4.31.0",
            "mathlib": "fabf563a7c95a166b8d7b6efca11c8b4dc9d911f",
        }
        for field, expected in expected_kernel_acceptance.items():
            if kernel_acceptance.get(field) != expected:
                problems.append(
                    f"route_selection.kernel_acceptance.{field} must be {expected!r}"
                )
    ledger_acceptance = selection.get("ledger_acceptance")
    expected_ledger_acceptance = {
        "status": "accepted",
        "commit": "9b77dd109306fa677fed5feab7bef830049e0c55",
        "workflow_run": 30143606761,
        "job": 89641332798,
        "lean": "v4.31.0",
        "mathlib": "fabf563a7c95a166b8d7b6efca11c8b4dc9d911f",
    }
    if ledger_acceptance != expected_ledger_acceptance:
        problems.append(
            "route_selection.ledger_acceptance must match the accepted closure "
            "commit and expanded ledger axiom-audit run"
        )
    for field in (
        "gate_result",
        "rationale",
        "reconsideration_triggers",
        "operational_effects",
    ):
        value = selection.get(field)
        if field == "gate_result":
            valid = isinstance(value, str) and bool(value)
        else:
            valid = (
                isinstance(value, list)
                and bool(value)
                and all(isinstance(item, str) and item for item in value)
            )
        if not valid:
            problems.append(f"route_selection.{field} must be nonempty")
    next_gate = data.get("next_phase_gate", {})
    if next_gate.get("current_mode") != "proposal_intake_promotion_closed":
        problems.append(
            "next_phase_gate.current_mode must be proposal_intake_promotion_closed"
        )
    reopen = next_gate.get("reopen_requirements")
    if not isinstance(reopen, list) or not reopen:
        problems.append("next_phase_gate.reopen_requirements must be nonempty")

    target_anchors = data["target_problem"].get("formal_anchors", [])
    for anchor in target_anchors:
        if anchor not in declaration_ids:
            problems.append(f"target problem: unknown Lean anchor {anchor}")
    for source_id in data["target_problem"].get("standards_sources", []):
        if source_id not in source_ids:
            problems.append(f"target problem: unknown source {source_id}")

    reverse_foundations = {foundation_id: set() for foundation_id in foundation_ids}
    completed_structural_routes: list[str] = []
    for route in routes:
        route_id = route.get("id", "?")
        missing = REQUIRED_ROUTE_FIELDS - set(route)
        if missing:
            problems.append(f"{route_id}: missing fields {sorted(missing)}")
            continue
        if route["status"] not in ROUTE_STATUSES:
            problems.append(f"{route_id}: invalid status {route['status']}")
        if route["priority"] not in PRIORITIES:
            problems.append(f"{route_id}: invalid priority {route['priority']}")
        if not route["assumptions"]:
            problems.append(f"{route_id}: assumptions must not be empty")
        if route["authorized_experiment"] is not False:
            problems.append(
                f"{route_id}: route-level promotion experiments are not authorized"
            )
        structural_lane = route.get("structural_lane")
        if (
            isinstance(structural_lane, dict)
            and structural_lane.get("status") == "completed"
        ):
            completed_structural_routes.append(route_id)
            expected_route_lane = {
                "decision_id": STRUCTURAL_DECISION_ID,
                "iteration_id": STRUCTURAL_ITERATION_ID,
                "route_id": STRUCTURAL_ROUTE_ID,
                "hypothesis_id": STRUCTURAL_HYPOTHESIS_ID,
                "task_id": STRUCTURAL_TASK_ID,
                "foundation_ids": [STRUCTURAL_FOUNDATION_ID],
                "promotes_route": False,
                "authorizes_experiment": False,
            }
            for field, expected in expected_route_lane.items():
                if structural_lane.get(field) != expected:
                    problems.append(
                        f"{route_id}: structural_lane.{field} must be {expected!r}"
                    )
        if not set(route["threat_models"]) <= threat_ids:
            unknown = set(route["threat_models"]) - threat_ids
            problems.append(f"{route_id}: unknown threat models {sorted(unknown)}")
        if not set(route["attack_registry_ids"]) <= attack_ids:
            unknown = set(route["attack_registry_ids"]) - attack_ids
            problems.append(f"{route_id}: unknown attack registry ids {sorted(unknown)}")
        if not set(route["foundation_ids"]) <= foundation_ids:
            unknown = set(route["foundation_ids"]) - foundation_ids
            problems.append(f"{route_id}: unknown foundations {sorted(unknown)}")
        if not set(route["formal_node_ids"]) <= formal_ids:
            unknown = set(route["formal_node_ids"]) - formal_ids
            problems.append(f"{route_id}: unknown formal nodes {sorted(unknown)}")
        if not set(route["lean_anchors"]) <= declaration_ids:
            unknown = set(route["lean_anchors"]) - declaration_ids
            problems.append(f"{route_id}: unknown Lean anchors {sorted(unknown)}")
        if not set(route["source_ids"]) <= source_ids:
            unknown = set(route["source_ids"]) - source_ids
            problems.append(f"{route_id}: unknown sources {sorted(unknown)}")
        if not (
            route["attack_registry_ids"]
            or route["lean_anchors"]
            or route["source_ids"]
            or route["evidence_files"]
        ):
            problems.append(
                f"{route_id}: no repository, registry, Lean, or literature evidence"
            )
        for evidence_file in route["evidence_files"]:
            path = ROOT / evidence_file
            if not path.is_file():
                problems.append(f"{route_id}: missing evidence file {evidence_file}")
        for foundation_id in route["foundation_ids"]:
            if foundation_id in reverse_foundations:
                reverse_foundations[foundation_id].add(route_id)
        for hypothesis_id in route.get("hypothesis_ids", []):
            if hypothesis_id not in hypotheses:
                problems.append(f"{route_id}: unknown hypothesis {hypothesis_id}")
                continue
            status = hypotheses[hypothesis_id].get("status")
            if status != "parked":
                problems.append(
                    f"{route_id}: {hypothesis_id} must be parked, found {status!r}"
                )

    if completed_structural_routes != [STRUCTURAL_ROUTE_ID]:
        problems.append(
            "exactly R-GLV-SEMAEV must own the completed structural route lane; "
            f"found {completed_structural_routes}"
        )

    completed_structural_foundations: list[str] = []
    for foundation in foundations:
        foundation_id = foundation.get("id", "?")
        missing = REQUIRED_FOUNDATION_FIELDS - set(foundation)
        if missing:
            problems.append(f"{foundation_id}: missing fields {sorted(missing)}")
            continue
        if foundation["decision"] not in FOUNDATION_DECISIONS:
            problems.append(
                f"{foundation_id}: invalid decision {foundation['decision']}"
            )
        if foundation["priority"] not in PRIORITIES:
            problems.append(
                f"{foundation_id}: invalid priority {foundation['priority']}"
            )
        if foundation["build_now"] != (foundation["decision"] == "build_now"):
            problems.append(
                f"{foundation_id}: build_now must agree with decision=build_now"
            )
        if foundation["build_now"] and foundation["priority"] != "P0":
            problems.append(f"{foundation_id}: build-now work must be P0")
        if foundation["implementation_status"] not in FOUNDATION_STATUSES:
            problems.append(
                f"{foundation_id}: invalid implementation status "
                f"{foundation['implementation_status']}"
            )
        if foundation["build_now"] and foundation["implementation_status"] != "complete":
            problems.append(
                f"{foundation_id}: build-now foundation must be complete before "
                "route selection"
            )
        if not set(foundation["needed_by_route_ids"]) <= route_ids:
            unknown = set(foundation["needed_by_route_ids"]) - route_ids
            problems.append(
                f"{foundation_id}: unknown dependent routes {sorted(unknown)}"
            )
        declared = set(foundation["needed_by_route_ids"])
        observed = reverse_foundations.get(foundation_id, set())
        if declared != observed:
            problems.append(
                f"{foundation_id}: needed_by_route_ids differs from route references; "
                f"declared={sorted(declared)}, observed={sorted(observed)}"
            )
        if not set(foundation["formal_node_ids"]) <= formal_ids:
            unknown = set(foundation["formal_node_ids"]) - formal_ids
            problems.append(
                f"{foundation_id}: unknown formal nodes {sorted(unknown)}"
            )
        structural_lane = foundation.get("structural_lane")
        if (
            isinstance(structural_lane, dict)
            and structural_lane.get("status") == "completed_bounded_slice"
        ):
            completed_structural_foundations.append(foundation_id)
            expected_foundation_lane = {
                "decision_id": STRUCTURAL_DECISION_ID,
                "iteration_id": STRUCTURAL_ITERATION_ID,
                "route_id": STRUCTURAL_ROUTE_ID,
                "hypothesis_id": STRUCTURAL_HYPOTHESIS_ID,
                "task_id": STRUCTURAL_TASK_ID,
                "promotes_foundation": False,
                "build_now": False,
            }
            for field, expected in expected_foundation_lane.items():
                if structural_lane.get(field) != expected:
                    problems.append(
                        f"{foundation_id}: structural_lane.{field} must be "
                        f"{expected!r}"
                    )

    if completed_structural_foundations != [STRUCTURAL_FOUNDATION_ID]:
        problems.append(
            "exactly F-SEMAEV-ELIMINATION must own the completed bounded foundation "
            f"slice; found {completed_structural_foundations}"
        )

    experiment_hypotheses = {
        hypothesis_id: fields
        for hypothesis_id, fields in hypotheses.items()
        if fields.get("direction") == "experiment"
    }
    active_experiments = [
        hypothesis_id
        for hypothesis_id, fields in experiment_hypotheses.items()
        if fields.get("status") == "active"
    ]
    if active_experiments:
        problems.append(
            "experiment hypotheses must remain parked at the promotion level: "
            + ", ".join(sorted(active_experiments))
        )
    completed_structural_hypotheses = [
        hypothesis_id
        for hypothesis_id, fields in experiment_hypotheses.items()
        if fields.get("structural_lane") == "completed"
    ]
    if completed_structural_hypotheses != [STRUCTURAL_HYPOTHESIS_ID]:
        problems.append(
            "exactly HYP_GLV_SEMAEV_001 must own the completed structural hypothesis "
            f"lane; found {completed_structural_hypotheses}"
        )
    expected_hypothesis_binding = {
        "status": "parked",
        "structural_lane": "completed",
        "structural_decision_id": STRUCTURAL_DECISION_ID,
        "structural_iteration_id": STRUCTURAL_ITERATION_ID,
        "structural_route_id": STRUCTURAL_ROUTE_ID,
        "structural_task_id": STRUCTURAL_TASK_ID,
        "structural_foundation_id": STRUCTURAL_FOUNDATION_ID,
    }
    structural_hypothesis = hypotheses.get(STRUCTURAL_HYPOTHESIS_ID, {})
    for field, expected in expected_hypothesis_binding.items():
        if structural_hypothesis.get(field) != expected:
            problems.append(
                f"{STRUCTURAL_HYPOTHESIS_ID}.{field} must be {expected!r}"
            )
    for required_parked in ("HYP_GLV_SEMAEV_001", "HYP_WARD_EDS_001"):
        status = hypotheses.get(required_parked, {}).get("status")
        if status != "parked":
            problems.append(f"{required_parked} must remain parked, found {status!r}")
    if hypotheses.get("H7_ECDLP_DECISION_SUBSTRATE", {}).get("status") != "closed":
        problems.append("H7_ECDLP_DECISION_SUBSTRATE must be closed after selection")

    required_foundation_files = (
        "scripts/build_ecdlp_decision_view.py",
        "scripts/check_ecdlp_decision_substrate.py",
        "experiments/framework/candidate_run.schema.json",
        "experiments/framework/candidate_contract.py",
        "experiments/framework/ec_oracle.py",
        "experiments/framework/test_framework.py",
        "experiments/framework/fixtures/valid.json",
        "experiments/framework/fixtures/invalid_hidden_precomputation.json",
        "experiments/framework/fixtures/invalid_self_validation.json",
        "experiments/framework/fixtures/invalid_wrong_output.json",
        "experiments/framework/fixtures/invalid_missing_provenance.json",
        "repo/RESEARCH_ENGINE_V0.json",
        "data/research_engine_state.json",
        "experiments/engine/outcome.schema.json",
        "experiments/engine/run.schema.json",
        "experiments/engine/instance_result.schema.json",
        "experiments/engine/instance_validation.schema.json",
        "experiments/engine/validator_request.schema.json",
        "experiments/engine/validator_output.schema.json",
        "experiments/engine/runs/README.md",
        "scripts/build_research_engine_state.py",
        "scripts/check_research_engine.py",
        "scripts/test_research_engine.py",
    )
    for relative in required_foundation_files:
        if not (ROOT / relative).is_file():
            problems.append(f"completed build-now foundation is missing {relative}")

    tasks_text = TASKS.read_text(encoding="utf-8")
    for required_task in ("TASK-008", "TASK-009", "TASK-010", "TASK-013"):
        if required_task not in tasks_text:
            problems.append(f"tasks/ECDLP_RESEARCH.md must contain {required_task}")
    for completed_task in ("TASK-005", "TASK-006", "TASK-007"):
        if re.search(rf"^### {completed_task}\b", tasks_text, flags=re.MULTILINE):
            problems.append(
                f"tasks/ECDLP_RESEARCH.md must not retain completed {completed_task}"
            )
    task_sections = {
        match.group("id"): match.group("body")
        for match in re.finditer(
            r"^### (?P<id>TASK-\d{3})\b(?P<body>.*?)(?=^### TASK-\d{3}\b|\Z)",
            tasks_text,
            flags=re.MULTILINE | re.DOTALL,
        )
    }
    task_009 = task_sections.get(STRUCTURAL_TASK_ID, "")
    expected_task_lines = (
        "Status: completed_bounded_structural",
        "Structural lane: completed",
        f"Decision: {STRUCTURAL_DECISION_ID}",
        f"Iteration: {STRUCTURAL_ITERATION_ID}",
        f"Route: {STRUCTURAL_ROUTE_ID}",
        f"Hypothesis: {STRUCTURAL_HYPOTHESIS_ID}",
        f"Foundation: {STRUCTURAL_FOUNDATION_ID}",
    )
    for line in expected_task_lines:
        if not re.search(rf"^{re.escape(line)}$", task_009, flags=re.MULTILINE):
            problems.append(f"{STRUCTURAL_TASK_ID} must contain {line!r}")
    structural_task_ids = [
        task_id
        for task_id, body in task_sections.items()
        if re.search(r"^Structural lane: completed$", body, flags=re.MULTILINE)
    ]
    if structural_task_ids != [STRUCTURAL_TASK_ID]:
        problems.append(
            "exactly TASK-009 must be the completed bounded structural task; "
            f"found {structural_task_ids}"
        )
    active_hypotheses = [
        hypothesis_id
        for hypothesis_id, fields in hypotheses.items()
        if fields.get("status") == "active"
    ]
    for hypothesis_id in active_hypotheses:
        if hypothesis_id not in tasks_text:
            problems.append(
                f"active hypothesis {hypothesis_id} is not referenced by "
                "tasks/ECDLP_RESEARCH.md"
            )
    if "Promotion and exact-target work remain disabled." not in tasks_text:
        problems.append(
            "tasks/ECDLP_RESEARCH.md must preserve the promotion boundary"
        )
    next_tasks_text = NEXT_TASKS.read_text(encoding="utf-8")
    if "Current central task: `TASK-008`" not in next_tasks_text:
        problems.append("tasks/NEXT.md must route current work to TASK-008")
    for binding_id in (
        STRUCTURAL_DECISION_ID,
        STRUCTURAL_ITERATION_ID,
        STRUCTURAL_ROUTE_ID,
        STRUCTURAL_HYPOTHESIS_ID,
        STRUCTURAL_TASK_ID,
    ):
        if binding_id not in next_tasks_text:
            problems.append(f"tasks/NEXT.md is missing structural binding {binding_id}")

    for relative in STALE_STATUS_FILES:
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in STALE_ACTIVE_PHRASES:
            if phrase in text:
                problems.append(f"{relative}: stale active phrase {phrase!r}")

    decisions_log = (ROOT / "data" / "research_decisions.md").read_text(
        encoding="utf-8"
    )
    if selection.get("decision_id") not in decisions_log:
        problems.append("route-selection decision is missing from research_decisions.md")

    return problems


def main() -> int:
    try:
        problems = validate()
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"decision-substrate check FAILED: malformed source: {error}", file=sys.stderr)
        return 1

    if problems:
        print("decision-substrate check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    data = load_json(DECISIONS)
    print(
        "decision-substrate check OK: "
        f"{len(data['routes'])} routes, {len(data['foundations'])} foundations, "
        "1 completed bounded structural route, 0 hypothesis experiments, "
        "0 promoted routes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
