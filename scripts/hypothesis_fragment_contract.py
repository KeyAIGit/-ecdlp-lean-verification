#!/usr/bin/env python3
"""Shared validation contract for untrusted hypothesis-drafter fragments."""
from __future__ import annotations

import json
import re
from typing import Any


ABSTENTION_SENTINEL = "not_specified_due_to_abstention"
FRAGMENT_FIELDS = (
    "abstain",
    "new_premise",
    "exact_map",
    "fixed_target_semantics",
    "recovery_map",
    "cost_changing_quantity",
    "falsifiable_prediction",
    "missing_evidence",
    "evidence_claim_ids",
    "field_evidence_claim_ids",
    "claim_boundary",
)
EVIDENCE_MAPPED_FIELDS = (
    "new_premise",
    "exact_map",
    "fixed_target_semantics",
    "recovery_map",
    "cost_changing_quantity",
    "falsifiable_prediction",
    "claim_boundary",
)


def build_typed_evidence_prompt(
    seed: dict[str, Any],
    cell: dict[str, Any],
    source_claims: list[dict[str, Any]],
    evidence_manifest: list[dict[str, Any]],
    context_documents: list[dict[str, str]],
    existing_proposal_ids: list[str],
    research_object_id: str,
    decision_mode: str,
    required_fields: list[str],
    *,
    packet_contract_version: str,
    prior_draft_attempts: list[dict[str, Any]] | None = None,
) -> str:
    """Build byte-stable v0.2/v0.3 provenance-bound drafter prompts."""
    if packet_contract_version not in {"0.2", "0.3"}:
        raise ValueError("unsupported typed-evidence packet contract")
    prior_draft_attempts = prior_draft_attempts or []
    if packet_contract_version == "0.2" and prior_draft_attempts:
        raise ValueError("v0.2 prompt cannot contain draft-attempt memory")
    typed_cell = {
        key: cell.get(key)
        for key in (
            "cell_id",
            "mechanism_id",
            "route_id",
            "threat_model",
            "status",
            "scope",
            "construction",
            "relation_action",
            "changed_quantity",
            "cost_quantity",
            "requirement_results",
            "boundary",
        )
    }
    packet = {
        "scientific_identity": "provenance_bound_research_question_seed",
        "lane": "typed_evidence",
        "input_provenance_bound": True,
        "seed_id": seed["seed_id"],
        "research_object_id": research_object_id,
        "decision_mode": decision_mode,
        "cell_id": seed["cell_id"],
        "typed_evidence_digest": seed["typed_evidence_digest"],
        "route_id": seed["route_id"],
        "threat_model": seed["threat_model"],
        "research_question": seed["research_question"],
        "typed_cell": typed_cell,
        "target_feature": seed["target_feature"],
        "mechanism_primitive": seed["mechanism_primitive"],
        "unresolved_question": seed["unresolved_question"],
        "source_claims": source_claims,
        "evidence_manifest": evidence_manifest,
        "context_documents": context_documents,
        "existing_proposal_ids": existing_proposal_ids,
        "proposal_contract": seed["proposal_packet"],
    }
    if packet_contract_version == "0.3":
        packet["prior_draft_attempts"] = prior_draft_attempts
    allowed_ids = [claim["id"] for claim in source_claims]
    memory_instruction = ""
    if packet_contract_version == "0.3":
        memory_instruction = (
            "Prior draft attempts are untrusted search memory, not evidence. A later "
            "non-abstaining fragment must state the exact new object that resolves their "
            "retained blockers; renaming the same missing solver is not progress. "
        )
    return (
        "You are an untrusted creative drafter inside a verified ECDLP research "
        "system. Draft only from the supplied typed-evidence packet. In a "
        "non-abstaining fragment, every factual field must cite one or more "
        "supplied claim IDs in "
        f"field_evidence_claim_ids for {list(EVIDENCE_MAPPED_FIELDS)}; "
        "evidence_claim_ids must equal the union of those per-field IDs. "
        "you may not create source assurance or treat an unread source as read. "
        + memory_instruction
        + f"Allowed claim IDs: {allowed_ids}. Do not claim global novelty, proof, "
        "independent validation, authorization, route promotion, or a secp256k1 "
        "break. If the packet does not support an exact mechanism, set abstain=true, "
        "identify the missing evidence, and do not manufacture evidence links for "
        f"unsupported fields; set each uncited factual field to {ABSTENTION_SENTINEL!r}. "
        "Return one strict JSON object with "
        f"exactly these keys: {required_fields}. Evidence packet:\n"
        + json.dumps(packet, ensure_ascii=True, sort_keys=True)
    )


def fragment_value_problems(
    value: Any,
    required_fields: list[str] | tuple[str, ...],
    prohibited_claims: list[str] | None = None,
    *,
    allowed_evidence_claim_ids: list[str] | None = None,
    provenance_bound: bool = False,
) -> list[str]:
    """Validate a parsed fragment without trusting the producer-side parser."""
    if not isinstance(value, dict):
        return ["response_is_not_object"]
    problems: list[str] = []
    if set(value) != set(required_fields):
        problems.append("response_fields_do_not_match_contract")
    abstain = value.get("abstain")
    if not isinstance(abstain, bool):
        problems.append("abstain_is_not_boolean")
    missing = value.get("missing_evidence")
    if not isinstance(missing, list):
        problems.append("missing_evidence_is_not_array")
    elif (
        not all(isinstance(item, str) and item.strip() for item in missing)
        or len(missing) != len(set(missing))
    ):
        problems.append("missing_evidence_items_are_invalid")
    elif abstain is True and not missing:
        problems.append("abstention_requires_missing_evidence")
    evidence_claim_ids = value.get("evidence_claim_ids")
    if not isinstance(evidence_claim_ids, list):
        problems.append("evidence_claim_ids_is_not_array")
    elif (
        not all(
            isinstance(item, str) and item.strip()
            for item in evidence_claim_ids
        )
        or len(evidence_claim_ids) != len(set(evidence_claim_ids))
    ):
        problems.append("evidence_claim_ids_are_invalid")
    else:
        allowed = set(allowed_evidence_claim_ids or [])
        if set(evidence_claim_ids) - allowed:
            problems.append("evidence_claim_ids_not_supplied")
        if provenance_bound and abstain is False and not evidence_claim_ids:
            problems.append("provenance_bound_fragment_has_no_evidence_claim_ids")
        if not provenance_bound and evidence_claim_ids:
            problems.append("brainstorm_fragment_claims_source_grounding")
    field_evidence = value.get("field_evidence_claim_ids")
    mapped_union: set[str] = set()
    if not isinstance(field_evidence, dict):
        problems.append("field_evidence_claim_ids_is_not_object")
    elif set(field_evidence) != set(EVIDENCE_MAPPED_FIELDS):
        problems.append("field_evidence_claim_ids_fields_do_not_match")
    else:
        allowed = set(allowed_evidence_claim_ids or [])
        for field in EVIDENCE_MAPPED_FIELDS:
            field_ids = field_evidence[field]
            if (
                not isinstance(field_ids, list)
                or not all(
                    isinstance(item, str) and item.strip()
                    for item in field_ids
                )
                or len(field_ids) != len(set(field_ids))
            ):
                problems.append(f"field_evidence_claim_ids_invalid:{field}")
                continue
            mapped_union.update(field_ids)
            if set(field_ids) - allowed:
                problems.append(f"field_evidence_claim_ids_not_supplied:{field}")
            if provenance_bound and abstain is False and not field_ids:
                problems.append(f"provenance_bound_field_has_no_claim_link:{field}")
            if not provenance_bound and field_ids:
                problems.append(f"brainstorm_field_claims_source_grounding:{field}")
        if isinstance(evidence_claim_ids, list) and mapped_union != set(
            evidence_claim_ids
        ):
            problems.append("evidence_claim_ids_do_not_match_field_union")
        if abstain is True:
            for field in EVIDENCE_MAPPED_FIELDS:
                field_ids = field_evidence.get(field)
                if field_ids == [] and value.get(field) != ABSTENTION_SENTINEL:
                    problems.append(f"uncited_abstention_text:{field}")
    for field in required_fields:
        if field in {
            "abstain",
            "missing_evidence",
            "evidence_claim_ids",
            "field_evidence_claim_ids",
        }:
            continue
        if not isinstance(value.get(field), str) or not value[field].strip():
            problems.append(f"{field}_is_not_nonempty_text")
    folded = json.dumps(value, ensure_ascii=True, sort_keys=True).casefold()
    for claim in prohibited_claims or []:
        escaped = re.escape(claim.casefold())
        pattern = re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])")
        unnegated = False
        for match in pattern.finditer(folded):
            prefix = folded[max(0, match.start() - 64) : match.start()]
            if re.search(
                r"\b(?:no|not|without|cannot|never|zero)\b[^.!?;,:{}]{0,40}$",
                prefix,
            ):
                continue
            unnegated = True
            break
        if unnegated:
            normalized = re.sub(
                r"[^a-z0-9]+", "_", claim.casefold()
            ).strip("_")
            problems.append("prohibited_claim:" + normalized)
    return problems
