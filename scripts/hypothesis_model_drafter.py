#!/usr/bin/env python3
"""Bounded model-assisted drafting for hypothesis review queues.

The default lane resolves typed-evidence seeds and binds each request to exact
source claims and evidence files. A separate broad brainstorm lane carries no
source assurance. Both only ask a model to fill an untrusted proposal fragment;
neither can clear gates or mutate Research Engine lifecycle state.
"""

from __future__ import annotations

import argparse
import base64
import functools
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hypothesis_generation_lib import sha256_json
from research_engine_lib import validate_all as rebuild_research_engine_state


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_MODEL_DRAFTER_V0.json"
USER_AGENT = "KeyAI-Research-Engine/0.2"
SYSTEM_MESSAGE = "Return only strict JSON. You cannot clear scientific gates."
API_PATH = "/chat/completions"
TEMPERATURE = 0.6
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 50000
MAX_ERROR_MESSAGE_BYTES = 4096
ABSTENTION_SENTINEL = "not_specified_due_to_abstention"
ALLOWED_PROVIDER_IDENTITIES = {
    "featherless": (
        "https://api.featherless.ai/v1",
        "FEATHERLESS_API_KEY",
    ),
    "deepseek_direct": (
        "https://api.deepseek.com",
        "DEEPSEEK_API_KEY",
    ),
    "moonshot_direct": (
        "https://api.moonshot.ai/v1",
        "KIMI_API_KEY",
    ),
}
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
LANE_IDS = ("typed_evidence", "brainstorm_queue")


class StrictJSONError(ValueError):
    pass


class ProviderHTTPFailure(RuntimeError):
    """Bounded HTTP failure whose classification can be replayed from output."""

    def __init__(
        self,
        *,
        status: int,
        classification: str,
        raw_body: bytes,
        body_truncated: bool,
    ) -> None:
        super().__init__(
            f"provider request failed: HTTP {status} ({classification})"
        )
        self.status = status
        self.classification = classification
        self.body = raw_body.decode("utf-8", errors="replace")
        self.body_base64 = base64.b64encode(raw_body).decode("ascii")
        self.body_sha256 = hashlib.sha256(raw_body).hexdigest()
        self.body_size_bytes = len(raw_body)
        self.body_truncated = body_truncated


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise StrictJSONError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise StrictJSONError(f"non-finite JSON constant: {value}")


def _strict_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise StrictJSONError("non-finite JSON number")
    return parsed


def _strict_json_int(value: str) -> int:
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > 1024:
        raise StrictJSONError("JSON integer digit bound exceeded")
    return int(value)


def strict_json_loads(text: str) -> Any:
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_pairs,
            parse_constant=_reject_json_constant,
            parse_float=_strict_json_float,
            parse_int=_strict_json_int,
        )
    except StrictJSONError:
        raise
    except (ValueError, RecursionError, UnicodeError) as exc:
        raise StrictJSONError("invalid strict JSON") from exc
    stack: list[tuple[Any, int]] = [(value, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise StrictJSONError("JSON node bound exceeded")
        if depth > MAX_JSON_DEPTH:
            raise StrictJSONError("JSON depth bound exceeded")
        if isinstance(current, str):
            try:
                current.encode("utf-8", errors="strict")
            except UnicodeEncodeError as exc:
                raise StrictJSONError("JSON contains a Unicode surrogate") from exc
        elif isinstance(current, dict):
            for key, item in current.items():
                stack.append((key, depth + 1))
                stack.append((item, depth + 1))
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return value


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except StrictJSONError as exc:
        raise ValueError(f"{path}: invalid strict JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("status") != "shadow_non_executing":
        raise ValueError("model drafter must remain shadow_non_executing")
    if policy.get("required_environment_attestation") != "protected-main-v1":
        raise ValueError("GitHub environment attestation contract drifted")
    safety = policy.get("safety", {})
    if (
        safety.get("live_calls_default") is not False
        or safety.get("all_outputs_executable") is not False
        or safety.get("any_output_executable") is not False
        or safety.get("admissible_count") != 0
        or safety.get("recommended_count") != 0
        or safety.get("authorized_count") != 0
        or safety.get("scientific_outcome_count") != 0
        or safety.get("ranker_label_count") != 0
        or safety.get("route_promotions") != 0
        or safety.get("exact_target_execution") is not False
        or safety.get("submitted_seed_live_replay") is not False
        or safety.get("live_requires_clean_protected_main_ancestor") is not True
        or safety.get("typed_evidence_bytes_read_from_source_commit_git_blobs")
        is not True
        or safety.get("partial_provider_failure_exit_nonzero") is not True
        or safety.get("output_single_writer_lease") is not True
        or safety.get("provider_transport_cryptographically_attested") is not False
        or safety.get("external_host_is_credential_trusted") is not True
        or safety.get("self_review_satisfies_independence") is not False
    ):
        raise ValueError("model drafter safety boundary drifted")
    limits = policy.get("limits", {})
    if not 1 <= limits.get("max_queue_items", 0) <= 30:
        raise ValueError("max_queue_items must remain within 1..30")
    if not 1 <= limits.get("max_live_calls", 0) <= 30:
        raise ValueError("max_live_calls must remain within 1..30")
    if limits.get("max_concurrency") != 1:
        raise ValueError("model drafter concurrency must remain one")
    if not 1 <= limits.get("max_completion_tokens", 0) <= 2000:
        raise ValueError("max_completion_tokens must remain within 1..2000")
    if not 1 <= limits.get("max_source_claims_per_request", 0) <= 128:
        raise ValueError("source-claim request bound must remain within 1..128")
    if not 1 <= limits.get("max_evidence_files_per_request", 0) <= 128:
        raise ValueError("evidence-file request bound must remain within 1..128")
    if not 1048576 <= limits.get("max_evidence_file_bytes", 0) <= 67108864:
        raise ValueError("evidence per-file byte bound escaped 1..64 MiB")
    if not 1048576 <= limits.get("max_evidence_total_bytes", 0) <= 268435456:
        raise ValueError("evidence total byte bound escaped 1..256 MiB")
    if not 4096 <= limits.get("max_context_bytes_per_request", 0) <= 524288:
        raise ValueError("context byte bound must remain within 4096..524288")
    if not 4096 <= limits.get("max_prompt_bytes", 0) <= 1048576:
        raise ValueError("prompt byte bound must remain within 4096..1048576")
    if not 65536 <= limits.get("max_provider_response_bytes", 0) <= 4194304:
        raise ValueError(
            "provider response byte bound must remain within 65536..4194304"
        )
    if policy.get("default_lane") != "typed_evidence":
        raise ValueError("typed_evidence must remain the default drafting lane")
    lanes = policy.get("lanes")
    if not isinstance(lanes, dict) or set(lanes) != set(LANE_IDS):
        raise ValueError("drafter lanes are not the pinned ordered contract")
    typed_lane = lanes["typed_evidence"]
    if (
        typed_lane.get("scientific_identity")
        != "provenance_bound_untrusted_fragment"
        or typed_lane.get("source_state") != "data/research_engine_state.json"
        or typed_lane.get("typed_evidence_state")
        != "data/typed_evidence_state.json"
        or typed_lane.get("decision_state")
        != "repo/ECDLP_DECISION_SUBSTRATE.json"
        or not isinstance(typed_lane.get("required_decision_mode"), str)
        or re.fullmatch(
            r"[0-9a-f]{64}",
            str(typed_lane.get("required_decision_sha256", "")),
        )
        is None
        or typed_lane.get("input_provenance_bound") is not True
        or typed_lane.get("skip_submitted_seeds_by_default") is not True
    ):
        raise ValueError("typed-evidence lane contract drifted")
    admissions = typed_lane.get("admissions")
    if (
        not isinstance(admissions, list)
        or not admissions
        or not all(
            isinstance(item, dict)
            and isinstance(item.get("seed_id"), str)
            and item["seed_id"].strip()
            and isinstance(item.get("research_object_id"), str)
            and item["research_object_id"].strip()
            and item.get("scope") == "non_executable_proposal_only"
            for item in admissions
        )
        or len({item["seed_id"] for item in admissions}) != len(admissions)
        or len({item["research_object_id"] for item in admissions})
        != len(admissions)
    ):
        raise ValueError("typed-evidence admissions are invalid")
    brainstorm_lane = lanes["brainstorm_queue"]
    if (
        brainstorm_lane.get("scientific_identity")
        != "untrusted_brainstorm_fragment"
        or brainstorm_lane.get("source_state")
        != "data/hypothesis_space_state.json"
        or brainstorm_lane.get("input_provenance_bound") is not False
        or brainstorm_lane.get("skip_submitted_seeds_by_default") is not False
    ):
        raise ValueError("brainstorm lane contract drifted")
    providers = policy.get("providers")
    if not isinstance(providers, dict) or set(providers) != set(
        ALLOWED_PROVIDER_IDENTITIES
    ):
        raise ValueError("provider set is not the pinned allowlist")
    for provider_id, (base_url, secret_env) in ALLOWED_PROVIDER_IDENTITIES.items():
        provider = providers[provider_id]
        if not isinstance(provider, dict):
            raise ValueError(f"provider {provider_id} must be an object")
        if (
            provider.get("base_url") != base_url
            or provider.get("secret_env") != secret_env
        ):
            raise ValueError(
                f"provider {provider_id} identity is not pinned"
            )
        models = provider.get("preferred_models")
        if (
            not isinstance(models, list)
            or not 1 <= len(models) <= 4
            or not all(
                isinstance(model, str) and model.strip()
                for model in models
            )
            or len(models) != len(set(models))
        ):
            raise ValueError(f"provider {provider_id} model allowlist is invalid")

    output_contract = policy.get("output_contract", {})
    if output_contract.get("abstention_sentinel") != ABSTENTION_SENTINEL:
        raise ValueError("abstention sentinel drifted")
    required = output_contract.get("required_fields")
    if required != list(FRAGMENT_FIELDS):
        raise ValueError("output contract fields are not the pinned contract")
    prohibited = output_contract.get("prohibited_claims")
    if (
        not isinstance(prohibited, list)
        or not prohibited
        or not all(isinstance(item, str) and item.strip() for item in prohibited)
        or len(prohibited) != len(set(prohibited))
    ):
        raise ValueError("prohibited claims must be a nonempty unique list")
    grounding = output_contract.get("claim_linking", {})
    if any(
        grounding.get(key) is not True
        for key in (
            "non_abstaining_typed_claim_ids_must_be_nonempty",
            "claim_ids_must_be_a_subset_of_the_supplied_packet",
            "per_field_claim_link_map_required",
            "brainstorm_claim_ids_must_be_empty",
            "model_output_cannot_create_source_assurance",
            "claim_links_are_not_semantic_support",
        )
    ):
        raise ValueError("claim-linking output contract drifted")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob_bytes(
    source_commit: str, normalized_path: str, *, max_bytes: int
) -> bytes:
    object_name = f"{source_commit}:{normalized_path}"
    size_result = subprocess.run(
        ["git", "cat-file", "-s", object_name],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if size_result.returncode != 0:
        raise ValueError(
            f"evidence path is not a blob at source commit: {normalized_path}"
        )
    try:
        size_bytes = int(size_result.stdout.strip())
    except ValueError as exc:
        raise ValueError("git returned an invalid evidence blob size") from exc
    if size_bytes < 0 or size_bytes > max_bytes:
        raise ValueError("evidence bytes exceed the policy bound")
    blob_result = subprocess.run(
        ["git", "cat-file", "blob", object_name],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if blob_result.returncode != 0 or len(blob_result.stdout) != size_bytes:
        raise ValueError(
            f"cannot read exact evidence blob at source commit: {normalized_path}"
        )
    return blob_result.stdout


def load_json_from_source_commit(
    source_commit: str, raw_path: str, *, max_bytes: int = 134217728
) -> dict[str, Any]:
    normalized, _ = resolve_repository_file(raw_path)
    raw = _git_blob_bytes(source_commit, normalized, max_bytes=max_bytes)
    try:
        text = raw.decode("utf-8")
        value = strict_json_loads(text)
    except (UnicodeDecodeError, StrictJSONError) as exc:
        raise ValueError(
            f"{normalized}: invalid strict JSON at source commit"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(f"{normalized}: expected object at source commit")
    return value


def build_repository_snapshot(
    paths: list[str],
    *,
    max_file_bytes: int,
    max_total_bytes: int,
    source_commit: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Read each source once, optionally from an immutable commit tree."""

    if not paths or not all(isinstance(item, str) and item for item in paths):
        raise ValueError("source-grounded evidence paths must be nonempty strings")
    resolved: dict[str, Path] = {}
    for raw_path in paths:
        normalized, candidate = resolve_repository_file(raw_path)
        if normalized in resolved and resolved[normalized] != candidate:
            raise ValueError("evidence paths have an ambiguous normalized identity")
        resolved[normalized] = candidate
    snapshot: dict[str, dict[str, Any]] = {}
    total_bytes = 0
    for normalized, candidate in sorted(resolved.items()):
        if source_commit is None:
            size_bytes = candidate.stat().st_size
            if size_bytes > max_file_bytes:
                raise ValueError("evidence bytes exceed the policy bound")
            with candidate.open("rb") as handle:
                raw = handle.read(max_file_bytes + 1)
            if len(raw) != size_bytes or candidate.stat().st_size != size_bytes:
                raise ValueError("evidence file changed while it was read")
        else:
            raw = _git_blob_bytes(
                source_commit, normalized, max_bytes=max_file_bytes
            )
            size_bytes = len(raw)
        total_bytes += size_bytes
        if total_bytes > max_total_bytes:
            raise ValueError("evidence bytes exceed the policy bound")
        snapshot[normalized] = {
            "path": normalized,
            "raw": raw,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": size_bytes,
        }
    return snapshot


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def resolve_repository_file(raw_path: str) -> tuple[str, Path]:
    normalized = raw_path.replace("\\", "/")
    candidate = (ROOT / normalized).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            f"evidence path escapes repository root: {raw_path}"
        ) from exc
    if not candidate.is_file():
        raise ValueError(f"evidence path does not resolve: {raw_path}")
    return normalized, candidate


def build_evidence_manifest(
    paths: list[str],
    *,
    max_file_bytes: int,
    max_total_bytes: int,
    source_commit: str | None = None,
) -> list[dict[str, Any]]:
    snapshot = build_repository_snapshot(
        paths,
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
        source_commit=source_commit,
    )
    return [
        {
            "path": item["path"],
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
        }
        for item in snapshot.values()
    ]


def build_context_documents(
    paths: list[str],
    *,
    max_total_bytes: int,
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    if not isinstance(paths, list) or not all(
        isinstance(item, str) and item for item in paths
    ):
        raise ValueError("context paths must be an array of nonempty strings")
    documents: list[dict[str, str]] = []
    total_bytes = 0
    if snapshot is None and paths:
        bounded_total = 0
        for raw_path in sorted(set(paths)):
            _, candidate = resolve_repository_file(raw_path)
            bounded_total += candidate.stat().st_size
            if bounded_total > max_total_bytes:
                raise ValueError("context documents exceed the policy byte bound")
        snapshot = build_repository_snapshot(
            paths,
            max_file_bytes=max_total_bytes,
            max_total_bytes=max_total_bytes,
        )
    for raw_path in sorted(set(paths)):
        normalized = raw_path.replace("\\", "/")
        item = (snapshot or {}).get(normalized)
        if item is None:
            raise ValueError(f"context path is absent from source snapshot: {raw_path}")
        raw = item["raw"]
        size_bytes = item["size_bytes"]
        if total_bytes + size_bytes > max_total_bytes:
            raise ValueError("context documents exceed the policy byte bound")
        total_bytes += len(raw)
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                f"context document is not UTF-8 text: {raw_path}"
            ) from exc
        documents.append(
            {
                "path": normalized,
                "sha256": item["sha256"],
                "content": content,
            }
        )
    return documents


def build_brainstorm_prompt(
    record: dict[str, Any], required_fields: list[str]
) -> str:
    packet = {
        "scientific_identity": "research_question_seed",
        "lane": "brainstorm_queue",
        "input_provenance_bound": False,
        "semantic_signature_sha256": record["semantic_signature_sha256"],
        "type": record["type"],
        "family": record["family"],
        "research_question": record["short_claim"],
        "mechanism_obligation": record["mechanism_obligation"],
        "cost_bridge": record["cost_bridge"],
        "decisive_test": record["decisive_test"],
        "adversarial_challenge": record.get("adversarial_challenge"),
        "scope": record["scope"],
        "warnings": record["warnings"],
    }
    return (
        "You are an untrusted creative drafter inside a verified ECDLP research "
        "system. This brainstorm seed has no provenance-bound evidence. Fill one "
        "proposal fragment, set evidence_claim_ids=[], set every value in "
        f"field_evidence_claim_ids for {list(EVIDENCE_MAPPED_FIELDS)} to [], "
        "and do not invent source "
        "assurance. Do not claim novelty, proof, validation, authorization, route "
        "promotion, or a secp256k1 break. If no exact mechanism can be stated, set "
        "abstain=true, list the missing evidence, and set every uncited factual "
        f"field to {ABSTENTION_SENTINEL!r}. Return one strict JSON object "
        f"with exactly these keys: {required_fields}. Seed packet:\n"
        + json.dumps(packet, ensure_ascii=True, sort_keys=True)
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
) -> str:
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
    allowed_ids = [claim["id"] for claim in source_claims]
    return (
        "You are an untrusted creative drafter inside a verified ECDLP research "
        "system. Draft only from the supplied typed-evidence packet. In a "
        "non-abstaining fragment, every factual field must cite one or more "
        "supplied claim IDs in "
        f"field_evidence_claim_ids for {list(EVIDENCE_MAPPED_FIELDS)}; "
        "evidence_claim_ids must equal the union of those per-field IDs. "
        "you may not create source assurance or treat an unread source as read. "
        f"Allowed claim IDs: {allowed_ids}. Do not claim global novelty, proof, "
        "independent validation, authorization, route promotion, or a secp256k1 "
        "break. If the packet does not support an exact mechanism, set abstain=true, "
        "identify the missing evidence, and do not manufacture evidence links for "
        f"unsupported fields; set each uncited factual field to {ABSTENTION_SENTINEL!r}. "
        "Return one strict JSON object with "
        f"exactly these keys: {required_fields}. Evidence packet:\n"
        + json.dumps(packet, ensure_ascii=True, sort_keys=True)
    )


def _validate_limit(policy: dict[str, Any], limit: int) -> None:
    maximum = policy["limits"]["max_queue_items"]
    if not 1 <= limit <= maximum:
        raise ValueError(f"limit must be within 1..{maximum}")


@functools.lru_cache(maxsize=1)
def canonical_research_engine_snapshot() -> tuple[bytes, str]:
    problems, rebuilt_state = rebuild_research_engine_state()
    if problems:
        raise ValueError(
            "canonical Research Engine rebuild failed: " + "; ".join(problems)
        )
    expected_typed_digest = rebuilt_state.get(
        "hypothesis_generation", {}
    ).get("source_hashes", {}).get("typed_evidence_state_sha256")
    if not isinstance(expected_typed_digest, str):
        raise ValueError("canonical Research Engine lacks typed-evidence digest")
    return canonical_json_bytes(rebuilt_state), expected_typed_digest


def validate_canonical_typed_sources(
    policy: dict[str, Any],
    state: dict[str, Any],
    typed_evidence_state: dict[str, Any],
    decision_state: dict[str, Any],
) -> None:
    rebuilt_bytes, expected_typed_digest = canonical_research_engine_snapshot()
    if canonical_json_bytes(state) != rebuilt_bytes:
        raise ValueError("Research Engine source state is stale or tampered")
    if sha256_json(typed_evidence_state) != expected_typed_digest:
        raise ValueError("typed-evidence state is stale or tampered")


def build_brainstorm_request_packets(
    policy: dict[str, Any],
    state: dict[str, Any],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    if state.get("status") != "shadow_non_executing":
        raise ValueError("source funnel state is not shadow_non_executing")
    queue = state.get("review_queue")
    if not isinstance(queue, list):
        raise ValueError("source funnel review_queue is missing")
    required = policy["output_contract"]["required_fields"]
    policy_digest = sha256_json(policy)
    source_digest = sha256_json(state)
    packets: list[dict[str, Any]] = []
    for record in queue[:limit]:
        prompt = build_brainstorm_prompt(record, required)
        if len(prompt.encode("utf-8")) > policy["limits"]["max_prompt_bytes"]:
            raise ValueError("brainstorm prompt exceeds the policy byte bound")
        identity = {
            "drafter_id": policy["drafter_id"],
            "policy_sha256": policy_digest,
            "lane": "brainstorm_queue",
            "input_provenance_bound": False,
            "source_state_sha256": source_digest,
            "semantic_signature_sha256": record[
                "semantic_signature_sha256"
            ],
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        }
        packets.append(
            {
                **identity,
                "scientific_packet_sha256": sha256_json(identity),
                "seed_id": record["seed_id"],
                "allowed_evidence_claim_ids": [],
                "prompt": prompt,
                "authorization": "none",
                "executable": False,
            }
        )
    return packets


def build_typed_evidence_request_packets(
    policy: dict[str, Any],
    state: dict[str, Any],
    typed_evidence_state: dict[str, Any],
    decision_state: dict[str, Any],
    *,
    limit: int,
    include_submitted: bool,
    source_commit: str | None = None,
) -> list[dict[str, Any]]:
    validate_canonical_typed_sources(
        policy, state, typed_evidence_state, decision_state
    )
    generation = state.get("hypothesis_generation")
    if not isinstance(generation, dict):
        raise ValueError("Research Engine hypothesis_generation state is missing")
    seeds = generation.get("generated_seeds")
    proposals = generation.get("proposal_intake")
    cells = typed_evidence_state.get("cells")
    claims = typed_evidence_state.get("source_claims")
    if not isinstance(seeds, list) or not isinstance(proposals, list):
        raise ValueError("typed-evidence seed or proposal intake is missing")
    if not isinstance(cells, list) or not isinstance(claims, list):
        raise ValueError("typed-evidence cells or source claims are missing")

    next_phase_gate = decision_state.get("next_phase_gate")
    required_mode = policy["lanes"]["typed_evidence"][
        "required_decision_mode"
    ]
    if (
        not isinstance(next_phase_gate, dict)
        or next_phase_gate.get("current_mode") != required_mode
    ):
        raise ValueError("typed-evidence drafting decision mode drifted")
    admissions = {
        item["seed_id"]: item
        for item in policy["lanes"]["typed_evidence"]["admissions"]
    }
    if sha256_json(decision_state) != policy["lanes"]["typed_evidence"][
        "required_decision_sha256"
    ]:
        raise ValueError(
            "current decision digest does not match the reviewed drafter "
            "admission policy"
        )

    seed_ids = [seed.get("seed_id") for seed in seeds]
    if (
        not all(isinstance(seed_id, str) and seed_id for seed_id in seed_ids)
        or len(seed_ids) != len(set(seed_ids))
    ):
        raise ValueError("generated typed-evidence seed identities are invalid")
    admitted_seed_ids = set(admissions)
    missing_admitted = sorted(admitted_seed_ids - set(seed_ids))
    if missing_admitted:
        raise ValueError(
            f"admitted typed-evidence seeds do not resolve: {missing_admitted}"
        )

    cell_index = {cell.get("cell_id"): cell for cell in cells}
    claim_index = {claim.get("id"): claim for claim in claims}
    if None in cell_index or len(cell_index) != len(cells):
        raise ValueError("typed-evidence cell identities are invalid")
    if None in claim_index or len(claim_index) != len(claims):
        raise ValueError("typed-evidence source-claim identities are invalid")

    current_seed_ids = set(seed_ids)
    current_seed_by_cell = {
        seed.get("cell_id"): seed.get("seed_id") for seed in seeds
    }
    if None in current_seed_by_cell or len(current_seed_by_cell) != len(seeds):
        raise ValueError("generated typed-evidence seed cells are not unique")
    proposals_by_seed: dict[str, list[str]] = {}
    for proposal in proposals:
        seed_id = proposal.get("seed_id")
        proposal_id = proposal.get("proposal_id")
        if not isinstance(seed_id, str) or not isinstance(proposal_id, str):
            raise ValueError("proposal intake lacks stable seed/proposal identity")
        resolution = proposal.get("seed_resolution")
        if seed_id in current_seed_ids and resolution == "current_scoped_identity":
            resolved_seed_id = seed_id
        elif resolution == "frozen_alias_current_scoped_identity":
            resolved_seed_id = current_seed_by_cell.get(proposal.get("cell_id"))
            if not isinstance(resolved_seed_id, str):
                raise ValueError(
                    "compatible frozen proposal has no current scoped seed"
                )
        elif resolution == "frozen_historical_only":
            continue
        else:
            raise ValueError("proposal intake seed resolution is invalid")
        proposals_by_seed.setdefault(resolved_seed_id, []).append(proposal_id)

    required = policy["output_contract"]["required_fields"]
    policy_digest = sha256_json(policy)
    source_digest = sha256_json(state)
    typed_state_digest = sha256_json(typed_evidence_state)
    decision_state_digest = sha256_json(decision_state)
    packets: list[dict[str, Any]] = []
    for seed in sorted(seeds, key=lambda item: item.get("seed_id", "")):
        seed_id = seed.get("seed_id")
        if seed_id not in admitted_seed_ids:
            continue
        existing_proposal_ids = sorted(proposals_by_seed.get(seed_id, []))
        if existing_proposal_ids and not include_submitted:
            continue
        cell = cell_index.get(seed.get("cell_id"))
        if not isinstance(cell, dict):
            raise ValueError(f"{seed_id}: typed-evidence cell does not resolve")
        seed_cell = seed.get("typed_cell")
        expected_seed_status = f"{cell.get('intake_mode')}_required"
        if (
            seed.get("authorization") != "none"
            or cell.get("authorization") != "none"
            or cell.get("seed_eligible") is not True
            or seed.get("status") != expected_seed_status
            or seed.get("route_id") != cell.get("route_id")
            or seed.get("threat_model") != cell.get("threat_model")
            or seed.get("typed_evidence_digest") != cell.get("evidence_digest")
            or not isinstance(seed_cell, dict)
            or seed_cell.get("mechanism_id") != cell.get("mechanism_id")
            or seed_cell.get("status") != cell.get("status")
            or seed_cell.get("intake_mode") != cell.get("intake_mode")
        ):
            raise ValueError(f"{seed_id}: typed-evidence binding drifted")
        claim_ids = cell.get("source_claim_ids")
        if (
            not isinstance(claim_ids, list)
            or not claim_ids
            or len(claim_ids) != len(set(claim_ids))
        ):
            raise ValueError(f"{seed_id}: source claim IDs are invalid")
        missing_claim_ids = sorted(set(claim_ids) - set(claim_index))
        if missing_claim_ids:
            raise ValueError(
                f"{seed_id}: source claims do not resolve: {missing_claim_ids}"
            )
        if len(claim_ids) > policy["limits"]["max_source_claims_per_request"]:
            raise ValueError(f"{seed_id}: source-claim request bound exceeded")
        evidence_paths = cell.get("evidence_paths", [])
        context_paths = seed.get("evidence_inputs", [])
        if (
            not isinstance(evidence_paths, list)
            or not isinstance(context_paths, list)
            or not all(
                isinstance(item, str) and item
                for item in evidence_paths + context_paths
            )
            or len(set(evidence_paths) | set(context_paths))
            > policy["limits"]["max_evidence_files_per_request"]
        ):
            raise ValueError(f"{seed_id}: evidence-file request bound exceeded")
        source_claims = [claim_index[claim_id] for claim_id in sorted(claim_ids)]
        all_evidence_paths = sorted(set(evidence_paths) | set(context_paths))
        source_snapshot = build_repository_snapshot(
            all_evidence_paths,
            max_file_bytes=policy["limits"]["max_evidence_file_bytes"],
            max_total_bytes=policy["limits"]["max_evidence_total_bytes"],
            source_commit=source_commit,
        )
        evidence_manifest = [
            {
                "path": item["path"],
                "sha256": item["sha256"],
                "size_bytes": item["size_bytes"],
            }
            for item in source_snapshot.values()
        ]
        context_documents = build_context_documents(
            context_paths,
            max_total_bytes=policy["limits"][
                "max_context_bytes_per_request"
            ],
            snapshot=source_snapshot,
        )
        manifest_paths = {entry["path"] for entry in evidence_manifest}
        claim_evidence_paths = {
            claim.get("evidence_path") for claim in source_claims
        }
        if (
            None in claim_evidence_paths
            or not claim_evidence_paths <= manifest_paths
        ):
            raise ValueError(
                f"{seed_id}: evidence manifest does not cover every source claim"
            )
        prompt = build_typed_evidence_prompt(
            seed,
            cell,
            source_claims,
            evidence_manifest,
            context_documents,
            existing_proposal_ids,
            admissions[seed_id]["research_object_id"],
            required_mode,
            required,
        )
        if len(prompt.encode("utf-8")) > policy["limits"]["max_prompt_bytes"]:
            raise ValueError(f"{seed_id}: prompt exceeds the policy byte bound")
        identity = {
            "drafter_id": policy["drafter_id"],
            "policy_sha256": policy_digest,
            "lane": "typed_evidence",
            "input_provenance_bound": True,
            "source_state_sha256": source_digest,
            "typed_evidence_state_sha256": typed_state_digest,
            "decision_state_sha256": decision_state_digest,
            "decision_mode": required_mode,
            "research_object_id": admissions[seed_id]["research_object_id"],
            "typed_evidence_digest": seed["typed_evidence_digest"],
            "source_claim_packet_sha256": sha256_json(source_claims),
            "evidence_manifest_sha256": sha256_json(evidence_manifest),
            "context_documents_sha256": sha256_json(context_documents),
            "seed_id": seed_id,
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        }
        packets.append(
            {
                **identity,
                "scientific_packet_sha256": sha256_json(identity),
                "cell_id": seed["cell_id"],
                "allowed_evidence_claim_ids": sorted(claim_ids),
                "evidence_manifest": evidence_manifest,
                "context_document_manifest": [
                    {"path": item["path"], "sha256": item["sha256"]}
                    for item in context_documents
                ],
                "existing_proposal_ids": existing_proposal_ids,
                "prompt": prompt,
                "authorization": "none",
                "executable": False,
            }
        )
        if len(packets) == limit:
            break
    return packets


def build_request_packets(
    policy: dict[str, Any],
    state: dict[str, Any],
    *,
    limit: int,
    lane_id: str | None = None,
    typed_evidence_state: dict[str, Any] | None = None,
    decision_state: dict[str, Any] | None = None,
    include_submitted: bool = False,
    source_commit: str | None = None,
) -> list[dict[str, Any]]:
    _validate_limit(policy, limit)
    selected_lane = lane_id or policy["default_lane"]
    if selected_lane == "brainstorm_queue":
        if include_submitted:
            raise ValueError("include_submitted is not defined for brainstorm lane")
        return build_brainstorm_request_packets(
            policy, state, limit=limit
        )
    if selected_lane == "typed_evidence":
        if typed_evidence_state is None:
            raise ValueError("typed_evidence lane requires typed evidence state")
        if decision_state is None:
            decision_state = load_json(
                ROOT
                / policy["lanes"]["typed_evidence"]["decision_state"]
            )
        return build_typed_evidence_request_packets(
            policy,
            state,
            typed_evidence_state,
            decision_state,
            limit=limit,
            include_submitted=include_submitted,
            source_commit=source_commit,
        )
    raise ValueError(f"unknown drafting lane: {selected_lane}")


def parse_fragment(
    text: str,
    required_fields: list[str],
    prohibited_claims: list[str] | None = None,
    *,
    allowed_evidence_claim_ids: list[str] | None = None,
    provenance_bound: bool = False,
) -> tuple[dict[str, Any] | None, list[str]]:
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE
    )
    try:
        value = strict_json_loads(cleaned)
    except StrictJSONError:
        return None, ["response_is_not_strict_json"]
    if not isinstance(value, dict):
        return None, ["response_is_not_object"]
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
        unknown = sorted(set(evidence_claim_ids) - allowed)
        if unknown:
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
        pattern = re.compile(
            rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
        )
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
            problems.append(
                "prohibited_claim:" + normalized
            )
    return value, problems


def classify_http_error(status: int, body: str) -> str:
    folded = body.casefold()
    if status == 403 and ("1010" in folded or "cloudflare" in folded):
        return "network_policy_blocked"
    if status in {401, 403}:
        return "authentication_or_plan_rejected"
    if status == 429:
        return "rate_limited"
    if status >= 500:
        return "provider_unavailable"
    return "provider_request_rejected"


def build_api_payload(
    *, model: str, prompt: str, max_tokens: int
) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": max_tokens,
    }


def inspect_git_source_state(requested_commit: str | None) -> dict[str, Any]:
    """Bind a declared source commit to the checkout used to build the packet."""

    try:
        head = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD^{commit}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("cannot establish git source provenance") from exc
    if re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise ValueError("git HEAD is not a full lowercase commit SHA")
    if requested_commit is not None and requested_commit != head:
        raise ValueError("source commit does not match the checked-out git HEAD")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", head, "origin/main"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if ancestry.returncode not in {0, 1}:
        raise ValueError("cannot establish protected-main ancestry")
    return {
        "source_commit": head,
        "source_tree_clean": not bool(status.strip()),
        "source_main_ancestor": ancestry.returncode == 0,
    }


def prepare_inference_packets(
    policy: dict[str, Any],
    packets: list[dict[str, Any]],
    *,
    provider_id: str,
    provider: dict[str, Any],
    model: str,
    source_commit: str,
    source_tree_clean: bool,
    source_main_ancestor: bool,
) -> list[dict[str, Any]]:
    drafter_source_sha256 = sha256_file(Path(__file__).resolve())
    prepared: list[dict[str, Any]] = []
    for packet in packets:
        payload = build_api_payload(
            model=model,
            prompt=packet["prompt"],
            max_tokens=policy["limits"]["max_completion_tokens"],
        )
        inference_identity = {
            "scientific_packet_sha256": packet[
                "scientific_packet_sha256"
            ],
            "source_commit": source_commit,
            "source_tree_clean": source_tree_clean,
            "source_main_ancestor": source_main_ancestor,
            "drafter_source_sha256": drafter_source_sha256,
            "provider": provider_id,
            "base_url": provider["base_url"],
            "endpoint": provider["base_url"].rstrip("/") + API_PATH,
            "user_agent": USER_AGENT,
            "http_referer": (
                "https://github.com/KeyAIGit/-ecdlp-lean-verification"
            ),
            "x_title": "KeyAI Hypothesis Model Drafter",
            "payload": payload,
        }
        prepared.append(
            {
                **packet,
                "source_commit": source_commit,
                "source_tree_clean": source_tree_clean,
                "source_main_ancestor": source_main_ancestor,
                "provider": provider_id,
                "model": model,
                "drafter_source_sha256": drafter_source_sha256,
                "inference_request_sha256": sha256_json(
                    inference_identity
                ),
            }
        )
    return prepared


def call_openai_compatible(
    *,
    base_url: str,
    api_key: str,
    payload: dict[str, Any],
    max_response_bytes: int,
) -> dict[str, Any]:
    request = urllib.request.Request(
        base_url.rstrip("/") + API_PATH,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "HTTP-Referer": "https://github.com/KeyAIGit/-ecdlp-lean-verification",
            "X-Title": "KeyAI Hypothesis Model Drafter",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw_body = response.read(max_response_bytes + 1)
            if len(raw_body) > max_response_bytes:
                raise RuntimeError("provider response exceeds the byte bound")
            try:
                body = raw_body.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise RuntimeError("provider response is not UTF-8") from exc
    except urllib.error.HTTPError as exc:
        raw_body = exc.read(max_response_bytes + 1)
        body = raw_body.decode("utf-8", errors="replace")
        oversized = len(raw_body) > max_response_bytes
        classification = (
            "provider_response_too_large"
            if oversized
            else classify_http_error(exc.code, body)
        )
        raise ProviderHTTPFailure(
            status=exc.code,
            classification=classification,
            raw_body=raw_body,
            body_truncated=oversized,
        ) from exc
    content, metadata = parse_provider_response_body(body)
    return {
        "content": content,
        "body": body,
        "provider_response_sha256": hashlib.sha256(
            body.encode("utf-8")
        ).hexdigest(),
        "metadata": metadata,
    }


def parse_provider_response_body(body: str) -> tuple[str, dict[str, Any]]:
    """Recompute the decisive provider content and metadata from raw bytes."""

    try:
        parsed = strict_json_loads(body)
        if not isinstance(parsed, dict):
            raise TypeError("provider response is not an object")
        choices = parsed["choices"]
        if not isinstance(choices, list) or len(choices) != 1:
            raise TypeError("provider response must contain exactly one choice")
        choice = choices[0]
        if not isinstance(choice, dict):
            raise TypeError("provider choice is not an object")
        message = choice["message"]
        if not isinstance(message, dict):
            raise TypeError("provider message is not an object")
        content = message["content"]
        if not isinstance(content, str):
            raise TypeError("provider response content is not text")
    except (KeyError, IndexError, TypeError, StrictJSONError) as exc:
        raise RuntimeError("provider response does not match the pinned shape") from exc
    return content, {
        "response_id": parsed.get("id"),
        "created": parsed.get("created"),
        "reported_model": parsed.get("model"),
        "system_fingerprint": parsed.get("system_fingerprint"),
        "finish_reason": choice.get("finish_reason"),
        "usage": parsed.get("usage"),
    }


def provider_metadata_problems(
    metadata: dict[str, Any], *, requested_model: str
) -> list[str]:
    problems: list[str] = []
    if metadata.get("reported_model") != requested_model:
        problems.append("provider_reported_model_mismatch")
    if metadata.get("finish_reason") != "stop":
        problems.append("provider_completion_not_complete")
    if not isinstance(metadata.get("response_id"), str) or not metadata[
        "response_id"
    ].strip():
        problems.append("provider_response_id_missing")
    return problems


def atomic_write_output(path: Path, output: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(output, ensure_ascii=True, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def acquire_output_lease(path: Path) -> tuple[int, Path]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lease_path = path.with_name(path.name + ".lock")
    try:
        descriptor = os.open(
            lease_path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError as exc:
        raise RuntimeError(f"output path already has a writer lease: {path}") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
    except Exception:
        try:
            os.close(descriptor)
        finally:
            lease_path.unlink(missing_ok=True)
        raise
    return descriptor, lease_path


def release_output_lease(descriptor: int, lease_path: Path) -> None:
    try:
        os.close(descriptor)
    finally:
        lease_path.unlink(missing_ok=True)


def bounded_error_message(exc: Exception) -> str:
    raw = str(exc).encode("utf-8", errors="replace")
    if len(raw) > MAX_ERROR_MESSAGE_BYTES:
        raw = raw[:MAX_ERROR_MESSAGE_BYTES]
    return raw.decode("utf-8", errors="replace")


def classify_provider_failure_message(message: str) -> str:
    match = re.search(r"\(([a-z_]+)\)$", message)
    if match:
        return match.group(1)
    if "byte bound" in message.casefold():
        return "provider_response_too_large"
    if "pinned shape" in message.casefold():
        return "provider_response_malformed"
    return "provider_call_failed"


def provider_failure_classification(exc: Exception) -> str:
    if isinstance(exc, ProviderHTTPFailure):
        return exc.classification
    return classify_provider_failure_message(bounded_error_message(exc))


def provider_error_record(
    packet: dict[str, Any],
    *,
    attempted: bool,
    classification: str,
    error_type: str,
    provider_error: Exception | None = None,
) -> dict[str, Any]:
    http_failure = (
        provider_error if isinstance(provider_error, ProviderHTTPFailure) else None
    )
    error_message = (
        bounded_error_message(provider_error) if provider_error is not None else None
    )
    encoded_message = (
        error_message.encode("utf-8") if error_message is not None else None
    )
    return {
        "scientific_packet_sha256": packet["scientific_packet_sha256"],
        "inference_request_sha256": packet["inference_request_sha256"],
        "attempted": attempted,
        "classification": classification,
        "error_type": error_type,
        "error_message": error_message,
        "error_message_sha256": (
            hashlib.sha256(encoded_message).hexdigest()
            if encoded_message is not None
            else None
        ),
        "error_message_size_bytes": (
            len(encoded_message) if encoded_message is not None else None
        ),
        "http_status": http_failure.status if http_failure else None,
        "error_body": http_failure.body if http_failure else None,
        "error_body_base64": (
            http_failure.body_base64 if http_failure else None
        ),
        "error_body_sha256": (
            http_failure.body_sha256 if http_failure else None
        ),
        "error_body_size_bytes": (
            http_failure.body_size_bytes if http_failure else None
        ),
        "error_body_truncated": (
            http_failure.body_truncated if http_failure else False
        ),
        "authorization": "none",
        "executable": False,
    }


def execute_batch(
    *,
    args: argparse.Namespace,
    policy: dict[str, Any],
    provider: dict[str, Any],
    model: str,
    source_state: dict[str, Any],
    packets: list[dict[str, Any]],
    output: dict[str, Any],
) -> int:
    if args.live:
        if os.environ.get("HYPOTHESIS_DRAFTER_LIVE") != "1":
            raise SystemExit(
                "live drafting requires HYPOTHESIS_DRAFTER_LIVE=1"
            )
        if args.output is None:
            raise SystemExit("live drafting requires an explicit --output path")
        if args.source_commit is None:
            raise SystemExit("live drafting requires --source-commit")
        if source_state["source_tree_clean"] is not True:
            raise SystemExit("live drafting requires a clean source tree")
        if source_state["source_main_ancestor"] is not True:
            raise SystemExit("live drafting requires protected-main ancestry")
        if args.include_submitted:
            raise SystemExit("submitted-seed replay is dry-only")
        if not packets:
            raise SystemExit("no eligible seed is available in the selected lane")
        if len(packets) > policy["limits"]["max_live_calls"]:
            raise SystemExit("live call count exceeds policy")
        api_key = os.environ.get(provider["secret_env"], "").strip()
        if not api_key:
            raise SystemExit(f"missing provider secret {provider['secret_env']}")
        required = policy["output_contract"]["required_fields"]
        output["completion_status"] = "running"
        atomic_write_output(args.output, output)
        for index, packet in enumerate(packets):
            try:
                provider_response = call_openai_compatible(
                    base_url=provider["base_url"],
                    api_key=api_key,
                    payload=build_api_payload(
                        model=model,
                        prompt=packet["prompt"],
                        max_tokens=policy["limits"]["max_completion_tokens"],
                    ),
                    max_response_bytes=policy["limits"][
                        "max_provider_response_bytes"
                    ],
                )
            except (RuntimeError, urllib.error.URLError, TimeoutError) as exc:
                output["errors"].append(
                    provider_error_record(
                        packet,
                        attempted=True,
                        classification=provider_failure_classification(exc),
                        error_type=type(exc).__name__,
                        provider_error=exc,
                    )
                )
                for remaining in packets[index + 1 :]:
                    output["errors"].append(
                        provider_error_record(
                            remaining,
                            attempted=False,
                            classification="not_attempted_after_prior_failure",
                            error_type="NotAttemptedAfterPriorFailure",
                        )
                    )
                output["error_count"] = len(output["errors"])
                output["completion_status"] = "partial_provider_failure"
                atomic_write_output(args.output, output)
                break
            raw = provider_response["content"]
            fragment, problems = parse_fragment(
                raw,
                required,
                policy["output_contract"]["prohibited_claims"],
                allowed_evidence_claim_ids=packet[
                    "allowed_evidence_claim_ids"
                ],
                provenance_bound=packet["input_provenance_bound"],
            )
            provider_problems = provider_metadata_problems(
                provider_response["metadata"], requested_model=model
            )
            problems.extend(provider_problems)
            output["responses"].append(
                {
                    "scientific_packet_sha256": packet[
                        "scientific_packet_sha256"
                    ],
                    "inference_request_sha256": packet[
                        "inference_request_sha256"
                    ],
                    "raw_response_sha256": hashlib.sha256(
                        raw.encode("utf-8")
                    ).hexdigest(),
                    "raw_response": raw,
                    "provider_response_sha256": provider_response[
                        "provider_response_sha256"
                    ],
                    "provider_response_body": provider_response["body"],
                    "provider_metadata": provider_response["metadata"],
                    "provider_problems": provider_problems,
                    "provider_transport_attested": False,
                    "fragment": fragment,
                    "schema_problems": problems,
                    "authorization": "none",
                    "executable": False,
                }
            )
            output["completed_response_count"] = len(output["responses"])
            atomic_write_output(args.output, output)
        else:
            output["completion_status"] = "complete"
            atomic_write_output(args.output, output)

    rendered = json.dumps(output, ensure_ascii=True, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        atomic_write_output(args.output, output)
        print(
            f"wrote {len(packets)} non-executable draft request(s) to "
            f"{args.output}"
        )
    return 2 if output["completion_status"] == "partial_provider_failure" else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="featherless")
    parser.add_argument("--model")
    parser.add_argument("--lane", choices=LANE_IDS)
    parser.add_argument("--include-submitted", action="store_true")
    parser.add_argument("--source-commit")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.source_commit is not None and re.fullmatch(
        r"[0-9a-f]{40}", args.source_commit
    ) is None:
        raise SystemExit("source commit must be a lowercase 40-hex SHA")
    try:
        source_state = inspect_git_source_state(args.source_commit)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    commit_bound_inputs = source_state["source_tree_clean"] is True

    def load_source_json(relative_path: str) -> dict[str, Any]:
        if commit_bound_inputs:
            return load_json_from_source_commit(
                source_state["source_commit"], relative_path
            )
        return load_json(ROOT / relative_path)

    policy = load_source_json("repo/HYPOTHESIS_MODEL_DRAFTER_V0.json")
    validate_policy(policy)
    lane_id = args.lane or policy["default_lane"]
    lane = policy["lanes"][lane_id]
    state = load_source_json(lane["source_state"])
    typed_evidence_state = None
    decision_state = None
    if lane_id == "typed_evidence":
        typed_evidence_state = load_source_json(lane["typed_evidence_state"])
        decision_state = load_source_json(lane["decision_state"])
    packets = build_request_packets(
        policy,
        state,
        limit=args.limit,
        lane_id=lane_id,
        typed_evidence_state=typed_evidence_state,
        decision_state=decision_state,
        include_submitted=args.include_submitted,
        source_commit=source_state["source_commit"],
    )
    provider = policy["providers"].get(args.provider)
    if not isinstance(provider, dict):
        raise SystemExit(f"unknown provider: {args.provider}")
    model = args.model or provider["preferred_models"][0]
    if model not in provider["preferred_models"]:
        raise SystemExit(
            "model is not pinned in the selected provider policy"
        )
    try:
        source_state_after = inspect_git_source_state(args.source_commit)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if source_state_after != source_state:
        raise SystemExit("git source state changed while building the request plan")
    packets = prepare_inference_packets(
        policy,
        packets,
        provider_id=args.provider,
        provider=provider,
        model=model,
        source_commit=source_state["source_commit"],
        source_tree_clean=source_state["source_tree_clean"],
        source_main_ancestor=source_state["source_main_ancestor"],
    )

    output: dict[str, Any] = {
        "schema_version": "0.2-generated",
        "status": "untrusted_non_executing_draft_batch",
        "lane": lane_id,
        "input_provenance_bound": lane["input_provenance_bound"],
        "provider": args.provider,
        "model": model,
        "source_commit": source_state["source_commit"],
        "source_tree_clean": source_state["source_tree_clean"],
        "source_main_ancestor": source_state["source_main_ancestor"],
        "provider_transport_attested": False,
        "live": args.live,
        "request_count": len(packets),
        "requests": packets,
        "responses": [],
        "errors": [],
        "completion_status": "dry_plan",
        "completed_response_count": 0,
        "error_count": 0,
        "scientific_outcomes": 0,
        "ranker_labels": 0,
        "admissible": 0,
        "recommended": 0,
        "authorized": 0,
        "route_promotions": 0,
        "exact_target_execution": False,
        "any_output_executable": False,
    }
    lease: tuple[int, Path] | None = None
    if args.output is not None:
        lease = acquire_output_lease(args.output)
    try:
        return execute_batch(
            args=args,
            policy=policy,
            provider=provider,
            model=model,
            source_state=source_state,
            packets=packets,
            output=output,
        )
    finally:
        if lease is not None:
            release_output_lease(*lease)


if __name__ == "__main__":
    raise SystemExit(main())
