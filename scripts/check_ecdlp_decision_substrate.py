#!/usr/bin/env python3
"""Validate the canonical secp256k1 ECDLP decision substrate.

This gate checks cross-registry identity, evidence paths, route/foundation
ownership, and the rule that no experiment is active before explicit route
selection. It validates project decisions; it does not validate mathematical
claims independently of their cited Lean or literature evidence.
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
TASKS = ROOT / "tasks" / "NEXT.md"

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
    "decision",
    "selected_route_ids",
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
        for name in ("direction", "status", "resume_after"):
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
    if data["phase_policy"].get("phase") != "monitored-candidate-intake":
        problems.append("the completed selection phase must be monitored-candidate-intake")
    if data["phase_policy"].get("experiments_authorized") is not False:
        problems.append("this phase must keep experiments_authorized=false")
    if data["phase_policy"].get("selected_attack_route") is not None:
        problems.append("the select-none decision must keep selected_attack_route=null")

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
    if selection.get("decision") != "select_none":
        problems.append("current route_selection.decision must be select_none")
    if selection.get("selected_route_ids") != []:
        problems.append("select_none requires selected_route_ids=[]")
    evaluated = selection.get("evaluated_route_ids")
    if not isinstance(evaluated, list) or len(evaluated) != len(set(evaluated)):
        problems.append("route_selection.evaluated_route_ids must be a unique array")
    elif set(evaluated) != route_ids:
        problems.append(
            "route_selection.evaluated_route_ids must contain every registered route"
        )
    if not re.fullmatch(r"RS-\d{4}-\d{2}-\d{2}-\d{3}", str(selection.get("decision_id", ""))):
        problems.append("route_selection.decision_id has an invalid format")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(selection.get("performed_on", ""))):
        problems.append("route_selection.performed_on must be YYYY-MM-DD")
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
    if next_gate.get("current_mode") != "monitor_without_experiment":
        problems.append(
            "next_phase_gate.current_mode must be monitor_without_experiment"
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
        if route["authorized_experiment"]:
            problems.append(f"{route_id}: experiments are not authorized in this phase")
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
            "experiment hypotheses must not be active in this phase: "
            + ", ".join(sorted(active_experiments))
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
    )
    for relative in required_foundation_files:
        if not (ROOT / relative).is_file():
            problems.append(f"completed build-now foundation is missing {relative}")

    tasks_text = TASKS.read_text(encoding="utf-8")
    for required_task in ("TASK-008", "TASK-009", "TASK-010"):
        if required_task not in tasks_text:
            problems.append(f"tasks/NEXT.md must contain {required_task}")
    for completed_task in ("TASK-005", "TASK-006", "TASK-007"):
        if re.search(rf"^### {completed_task}\b", tasks_text, flags=re.MULTILINE):
            problems.append(f"tasks/NEXT.md must not retain completed {completed_task}")
    active_hypotheses = [
        hypothesis_id
        for hypothesis_id, fields in hypotheses.items()
        if fields.get("status") == "active"
    ]
    for hypothesis_id in active_hypotheses:
        if hypothesis_id not in tasks_text:
            problems.append(
                f"active hypothesis {hypothesis_id} is not referenced by tasks/NEXT.md"
            )
    if re.search(r"(?i)\b(run|resume|launch)\b.{0,40}\bexperiment", tasks_text):
        problems.append("tasks/NEXT.md appears to authorize experiment execution")

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
        "0 authorized experiments."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
