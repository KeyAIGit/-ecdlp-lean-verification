#!/usr/bin/env python3
"""Validate and materialize the claim-level Research Engine truth state."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "RESEARCH_CLAIMS_V0.json"
DECISIONS_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
STATE_PATH = ROOT / "data" / "research_claim_state.json"

TOP_FIELDS = {
    "schema_version",
    "claim_model_id",
    "status",
    "purpose",
    "primary_threat_model",
    "trust_boundary",
    "research_questions",
    "mechanism_variants",
    "claims",
    "evidence_events",
}
QUESTION_FIELDS = {
    "research_question_id",
    "route_id",
    "hypothesis_ids",
    "statement",
    "status",
    "threat_model",
    "reopening_conditions",
}
VARIANT_FIELDS = {
    "mechanism_variant_id",
    "research_question_id",
    "kind",
    "description",
    "mechanism_status",
    "proposal_seed_eligible",
}
CLAIM_FIELDS = {
    "claim_id",
    "route_id",
    "research_question_id",
    "statement",
    "threat_model",
    "mechanism_variant_id",
    "scope",
    "claim_disposition",
    "supersedes",
    "reopening_conditions",
    "evidence_event_ids",
    "assurance",
}
EVENT_FIELDS = {
    "evidence_event_id",
    "event_class",
    "assurance",
    "outcome",
    "evidence_refs",
    "calibration_eligible",
    "authorization",
}
DISPOSITIONS = {
    "confirmed",
    "falsified",
    "bounded_negative",
    "inconclusive",
    "inapplicable",
}
ASSURANCE = {
    "lean_kernel",
    "certificate_replayed",
    "independent_reproduction",
    "empirical_native",
    "historical_migration",
    "literature_only",
}
CALIBRATION_EVENT_CLASSES = {"native_empirical"}
OPEN_ROUTE_STATUSES = {"open", "open_parked", "conditional_open"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _exact_keys(
    value: Any,
    expected: set[str],
    label: str,
    problems: list[str],
) -> bool:
    if not isinstance(value, dict):
        problems.append(f"{label} must be an object")
        return False
    observed = set(value)
    if observed != expected:
        problems.append(
            f"{label} fields differ: missing={sorted(expected - observed)}, "
            f"extra={sorted(observed - expected)}"
        )
        return False
    return True


def _text(value: Any, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def _unique_text_list(
    value: Any,
    label: str,
    problems: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        problems.append(f"{label} must be an array")
        return []
    if nonempty and not value:
        problems.append(f"{label} must not be empty")
    if any(not _text(item) for item in value):
        problems.append(f"{label} entries must be nonempty text")
        return []
    if len(value) != len(set(value)):
        problems.append(f"{label} entries must be unique")
    return value


def validate_and_build(
    policy: dict[str, Any],
    decisions: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    problems: list[str] = []
    if not _exact_keys(policy, TOP_FIELDS, "claim policy", problems):
        return problems, {}
    if policy.get("schema_version") != "0.2":
        problems.append("claim policy schema_version must be 0.2")
    if policy.get("status") != "implementation_non_executable":
        problems.append("claim policy must remain implementation_non_executable")
    if policy.get("primary_threat_model") != (
        "classical-single-target-plain"
    ):
        problems.append("claim policy threat model drifted")

    route_index = {
        route["id"]: route
        for route in decisions.get("routes", [])
        if isinstance(route, dict) and isinstance(route.get("id"), str)
    }
    questions = policy.get("research_questions")
    if not isinstance(questions, list) or not questions:
        problems.append("research_questions must be nonempty")
        questions = []
    question_index: dict[str, dict[str, Any]] = {}
    for index, question in enumerate(questions):
        label = f"research_questions[{index}]"
        if not _exact_keys(question, QUESTION_FIELDS, label, problems):
            continue
        question_id = question.get("research_question_id")
        if not _text(question_id):
            problems.append(f"{label}.research_question_id is invalid")
            continue
        if question_id in question_index:
            problems.append(f"{label}.research_question_id is duplicated")
        question_index[question_id] = question
        route = route_index.get(question.get("route_id"))
        if route is None:
            problems.append(f"{label}.route_id does not resolve")
        elif question.get("status") != route.get("status"):
            problems.append(
                f"{label}.status must be derived from the canonical route"
            )
        if question.get("threat_model") != policy["primary_threat_model"]:
            problems.append(f"{label}.threat_model drifted")
        _unique_text_list(
            question.get("hypothesis_ids"),
            f"{label}.hypothesis_ids",
            problems,
            nonempty=True,
        )
        _unique_text_list(
            question.get("reopening_conditions"),
            f"{label}.reopening_conditions",
            problems,
            nonempty=True,
        )
        if not _text(question.get("statement"), 20):
            problems.append(f"{label}.statement is not substantive")

    variants = policy.get("mechanism_variants")
    if not isinstance(variants, list) or not variants:
        problems.append("mechanism_variants must be nonempty")
        variants = []
    variant_index: dict[str, dict[str, Any]] = {}
    for index, variant in enumerate(variants):
        label = f"mechanism_variants[{index}]"
        if not _exact_keys(variant, VARIANT_FIELDS, label, problems):
            continue
        variant_id = variant.get("mechanism_variant_id")
        if not _text(variant_id):
            problems.append(f"{label}.mechanism_variant_id is invalid")
            continue
        if variant_id in variant_index:
            problems.append(f"{label}.mechanism_variant_id is duplicated")
        variant_index[variant_id] = variant
        if variant.get("research_question_id") not in question_index:
            problems.append(f"{label}.research_question_id does not resolve")
        if not _text(variant.get("description"), 20):
            problems.append(f"{label}.description is not substantive")
        if not isinstance(variant.get("proposal_seed_eligible"), bool):
            problems.append(f"{label}.proposal_seed_eligible must be boolean")
        if (
            variant.get("kind") == "desired_property_only"
            and variant.get("proposal_seed_eligible") is not False
        ):
            problems.append(
                f"{label}: desired properties cannot become proposal seeds"
            )

    events = policy.get("evidence_events")
    if not isinstance(events, list) or not events:
        problems.append("evidence_events must be nonempty")
        events = []
    event_index: dict[str, dict[str, Any]] = {}
    for index, event in enumerate(events):
        label = f"evidence_events[{index}]"
        if not _exact_keys(event, EVENT_FIELDS, label, problems):
            continue
        event_id = event.get("evidence_event_id")
        if not _text(event_id):
            problems.append(f"{label}.evidence_event_id is invalid")
            continue
        if event_id in event_index:
            problems.append(f"{label}.evidence_event_id is duplicated")
        event_index[event_id] = event
        if event.get("assurance") not in ASSURANCE:
            problems.append(f"{label}.assurance is invalid")
        if event.get("authorization") != "none":
            problems.append(f"{label} must not authorize work")
        refs = _unique_text_list(
            event.get("evidence_refs"),
            f"{label}.evidence_refs",
            problems,
            nonempty=True,
        )
        for relative in refs:
            if not (ROOT / relative).is_file():
                problems.append(f"{label}: evidence ref does not resolve: {relative}")
        calibration_eligible = event.get("calibration_eligible")
        expected_calibration = (
            event.get("event_class") in CALIBRATION_EVENT_CLASSES
            and event.get("assurance") == "empirical_native"
        )
        if calibration_eligible is not expected_calibration:
            problems.append(
                f"{label}.calibration_eligible contradicts event class/assurance"
            )
        if event_id.startswith("REO-"):
            if len(refs) != 1:
                problems.append(
                    f"{label}: historical event must bind exactly one event file"
                )
            elif (ROOT / refs[0]).is_file():
                historical = load_json(ROOT / refs[0])
                if historical.get("event_id") != event_id:
                    problems.append(f"{label}: historical event id mismatch")
                if historical.get("outcome") != event.get("outcome"):
                    problems.append(f"{label}: historical outcome mismatch")
            if event.get("event_class") != "historical_migration":
                problems.append(
                    f"{label}: historical outcome must remain a migration"
                )

    claims = policy.get("claims")
    if not isinstance(claims, list) or not claims:
        problems.append("claims must be nonempty")
        claims = []
    claim_ids: list[str] = []
    for index, claim in enumerate(claims):
        label = f"claims[{index}]"
        if not _exact_keys(claim, CLAIM_FIELDS, label, problems):
            continue
        claim_id = claim.get("claim_id")
        if not _text(claim_id):
            problems.append(f"{label}.claim_id is invalid")
            continue
        claim_ids.append(claim_id)
        question = question_index.get(claim.get("research_question_id"))
        if question is None:
            problems.append(f"{label}.research_question_id does not resolve")
        elif claim.get("route_id") != question.get("route_id"):
            problems.append(f"{label}.route_id differs from parent question")
        variant = variant_index.get(claim.get("mechanism_variant_id"))
        if variant is None:
            problems.append(f"{label}.mechanism_variant_id does not resolve")
        elif (
            claim.get("research_question_id")
            != variant.get("research_question_id")
        ):
            problems.append(
                f"{label}.mechanism_variant_id belongs to another question"
            )
        if claim.get("claim_disposition") not in DISPOSITIONS:
            problems.append(f"{label}.claim_disposition is invalid")
        if claim.get("threat_model") != policy["primary_threat_model"]:
            problems.append(f"{label}.threat_model drifted")
        for field in ("statement", "scope"):
            if not _text(claim.get(field), 20):
                problems.append(f"{label}.{field} is not substantive")
        _unique_text_list(
            claim.get("supersedes"), f"{label}.supersedes", problems
        )
        _unique_text_list(
            claim.get("reopening_conditions"),
            f"{label}.reopening_conditions",
            problems,
            nonempty=True,
        )
        evidence_ids = _unique_text_list(
            claim.get("evidence_event_ids"),
            f"{label}.evidence_event_ids",
            problems,
            nonempty=True,
        )
        assurances = _unique_text_list(
            claim.get("assurance"),
            f"{label}.assurance",
            problems,
            nonempty=True,
        )
        if any(item not in ASSURANCE for item in assurances):
            problems.append(f"{label}.assurance contains an invalid value")
        resolved_events = [
            event_index[event_id]
            for event_id in evidence_ids
            if event_id in event_index
        ]
        missing_events = sorted(set(evidence_ids) - set(event_index))
        if missing_events:
            problems.append(
                f"{label}.evidence_event_ids do not resolve: {missing_events}"
            )
        event_assurance = {
            event["assurance"] for event in resolved_events
        }
        unexplained_assurance = set(assurances) - event_assurance
        if unexplained_assurance:
            problems.append(
                f"{label}.assurance lacks matching evidence: "
                f"{sorted(unexplained_assurance)}"
            )
        if claim.get("claim_disposition") in {
            "falsified",
            "bounded_negative",
            "inapplicable",
        }:
            route = route_index.get(claim.get("route_id"), {})
            if route.get("status") not in OPEN_ROUTE_STATUSES:
                problems.append(
                    f"{label}: child disposition must not silently close route"
                )

    if len(claim_ids) != len(set(claim_ids)):
        problems.append("claim ids must be unique")
    claim_id_set = set(claim_ids)
    for index, claim in enumerate(claims):
        for superseded in claim.get("supersedes", []):
            if superseded not in claim_id_set:
                problems.append(
                    f"claims[{index}].supersedes does not resolve: {superseded}"
                )

    generated_questions = []
    for question in sorted(
        question_index.values(),
        key=lambda item: item["research_question_id"],
    ):
        route = route_index[question["route_id"]]
        generated_questions.append(
            {
                **question,
                "route_status": route["status"],
                "route_authorized_experiment": route[
                    "authorized_experiment"
                ],
                "route_priority": route["priority"],
            }
        )
    sorted_claims = sorted(claims, key=lambda item: item["claim_id"])
    state = {
        "schema_version": "0.2-generated",
        "claim_model_id": policy["claim_model_id"],
        "status": "non_executable_truth_state",
        "source_hashes": {
            "claim_policy_sha256": sha256_json(policy),
            "decision_substrate_sha256": sha256_json(decisions),
        },
        "counts": {
            "routes_represented": len(
                {question["route_id"] for question in questions}
            ),
            "research_questions": len(questions),
            "claims": len(claims),
            "closed_child_claims": sum(
                claim["claim_disposition"]
                in {"falsified", "bounded_negative", "inapplicable"}
                for claim in claims
            ),
            "inconclusive_claims": sum(
                claim["claim_disposition"] == "inconclusive"
                for claim in claims
            ),
            "confirmed_claims": sum(
                claim["claim_disposition"] == "confirmed"
                for claim in claims
            ),
            "mechanism_variants": len(variants),
            "proposal_seed_eligible_variants": sum(
                item["proposal_seed_eligible"] for item in variants
            ),
            "evidence_events": len(events),
            "calibration_eligible_events": sum(
                item["calibration_eligible"] for item in events
            ),
        },
        "research_questions": generated_questions,
        "mechanism_variants": sorted(
            variants, key=lambda item: item["mechanism_variant_id"]
        ),
        "claims": sorted_claims,
        "evidence_events": sorted(
            events, key=lambda item: item["evidence_event_id"]
        ),
        "open_routes": sorted(
            {
                question["route_id"]
                for question in questions
                if route_index[question["route_id"]]["status"]
                in OPEN_ROUTE_STATUSES
            }
        ),
        "authorization": {
            "experiments": 0,
            "route_promotions": 0,
            "exact_target_runs": 0,
        },
    }
    return sorted(set(problems)), state


def render(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"


def load_and_build() -> tuple[list[str], dict[str, Any]]:
    return validate_and_build(load_json(POLICY_PATH), load_json(DECISIONS_PATH))


def main() -> int:
    check = "--check" in sys.argv
    problems, state = load_and_build()
    if problems:
        print("research-claim check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    expected = render(state)
    if check:
        if not STATE_PATH.is_file():
            print(f"research-claim check FAILED: missing {STATE_PATH}")
            return 1
        if STATE_PATH.read_text(encoding="utf-8") != expected:
            print(
                "research-claim check FAILED: generated state is stale; "
                "run scripts/research_claims.py"
            )
            return 1
        print(
            "research-claim check passed: "
            f"{state['counts']['claims']} claims, "
            f"{state['counts']['closed_child_claims']} closed child, "
            "0 authorized."
        )
        return 0
    STATE_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(
        f"wrote {STATE_PATH.relative_to(ROOT)}: "
        f"{state['counts']['claims']} claims, "
        f"{state['counts']['calibration_eligible_events']} calibration events."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
