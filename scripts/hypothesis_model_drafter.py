#!/usr/bin/env python3
"""Bounded model-assisted drafting for the hypothesis review queue.

The deterministic funnel decides which question signatures are worth drafting.
This module only asks a model to fill an untrusted proposal fragment. It cannot
clear gates or mutate Research Engine lifecycle state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_MODEL_DRAFTER_V0.json"
USER_AGENT = "KeyAI-Research-Engine/0.1"
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
    "claim_boundary",
)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("status") != "shadow_non_executing":
        raise ValueError("model drafter must remain shadow_non_executing")
    safety = policy.get("safety", {})
    if (
        safety.get("live_calls_default") is not False
        or safety.get("all_outputs_executable") is not False
        or safety.get("admissible_count") != 0
        or safety.get("recommended_count") != 0
        or safety.get("authorized_count") != 0
        or safety.get("route_promotions") != 0
        or safety.get("exact_target_execution") is not False
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


def build_prompt(record: dict[str, Any], required_fields: list[str]) -> str:
    packet = {
        "scientific_identity": "research_question_seed",
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
        "system. Fill one proposal fragment for the supplied question seed. "
        "Do not claim novelty, proof, validation, authorization, route promotion, "
        "or a secp256k1 break. If no exact mechanism can be stated, set abstain=true "
        "and list the missing evidence. Return one strict JSON object with exactly "
        f"these keys: {required_fields}. Seed packet:\n"
        + json.dumps(packet, ensure_ascii=True, sort_keys=True)
    )


def build_request_packets(
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
    maximum = min(policy["limits"]["max_queue_items"], len(queue))
    if not 1 <= limit <= maximum:
        raise ValueError(f"limit must be within 1..{maximum}")
    required = policy["output_contract"]["required_fields"]
    source_digest = sha256_json(state)
    packets: list[dict[str, Any]] = []
    for record in queue[:limit]:
        prompt = build_prompt(record, required)
        identity = {
            "drafter_id": policy["drafter_id"],
            "source_state_sha256": source_digest,
            "semantic_signature_sha256": record[
                "semantic_signature_sha256"
            ],
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        }
        packets.append(
            {
                **identity,
                "request_sha256": sha256_json(identity),
                "seed_id": record["seed_id"],
                "prompt": prompt,
                "authorization": "none",
                "executable": False,
            }
        )
    return packets


def parse_fragment(
    text: str,
    required_fields: list[str],
    prohibited_claims: list[str] | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE
    )
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        return None, ["response_is_not_json"]
    if not isinstance(value, dict):
        return None, ["response_is_not_object"]
    problems: list[str] = []
    if set(value) != set(required_fields):
        problems.append("response_fields_do_not_match_contract")
    if not isinstance(value.get("abstain"), bool):
        problems.append("abstain_is_not_boolean")
    missing = value.get("missing_evidence")
    if not isinstance(missing, list):
        problems.append("missing_evidence_is_not_array")
    elif (
        not all(isinstance(item, str) and item.strip() for item in missing)
        or len(missing) != len(set(missing))
    ):
        problems.append("missing_evidence_items_are_invalid")
    for field in required_fields:
        if field in {"abstain", "missing_evidence"}:
            continue
        if not isinstance(value.get(field), str) or not value[field].strip():
            problems.append(f"{field}_is_not_nonempty_text")
    folded = json.dumps(value, ensure_ascii=True, sort_keys=True).casefold()
    for claim in prohibited_claims or []:
        if claim.casefold() in folded:
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


def call_openai_compatible(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Return only strict JSON. You cannot clear scientific gates.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.6,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
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
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        classification = classify_http_error(exc.code, body)
        raise RuntimeError(
            f"provider request failed: HTTP {exc.code} ({classification})"
        ) from exc
    parsed = json.loads(body)
    return parsed["choices"][0]["message"]["content"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="featherless")
    parser.add_argument("--model")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    policy = load_json(POLICY_PATH)
    validate_policy(policy)
    source_path = ROOT / policy["source_state"]
    state = load_json(source_path)
    packets = build_request_packets(policy, state, limit=args.limit)
    provider = policy["providers"].get(args.provider)
    if not isinstance(provider, dict):
        raise SystemExit(f"unknown provider: {args.provider}")
    model = args.model or provider["preferred_models"][0]
    if model not in provider["preferred_models"]:
        raise SystemExit(
            "model is not pinned in the selected provider policy"
        )

    output: dict[str, Any] = {
        "schema_version": "0.1-generated",
        "status": "untrusted_non_executing_draft_batch",
        "provider": args.provider,
        "model": model,
        "live": args.live,
        "request_count": len(packets),
        "requests": packets,
        "responses": [],
        "admissible": 0,
        "recommended": 0,
        "authorized": 0,
    }
    if args.live:
        if os.environ.get("HYPOTHESIS_DRAFTER_LIVE") != "1":
            raise SystemExit(
                "live drafting requires HYPOTHESIS_DRAFTER_LIVE=1"
            )
        if args.output is None:
            raise SystemExit("live drafting requires an explicit --output path")
        if len(packets) > policy["limits"]["max_live_calls"]:
            raise SystemExit("live call count exceeds policy")
        api_key = os.environ.get(provider["secret_env"], "").strip()
        if not api_key:
            raise SystemExit(f"missing provider secret {provider['secret_env']}")
        required = policy["output_contract"]["required_fields"]
        for packet in packets:
            raw = call_openai_compatible(
                base_url=provider["base_url"],
                api_key=api_key,
                model=model,
                prompt=packet["prompt"],
                max_tokens=policy["limits"]["max_completion_tokens"],
            )
            fragment, problems = parse_fragment(
                raw,
                required,
                policy["output_contract"]["prohibited_claims"],
            )
            output["responses"].append(
                {
                    "request_sha256": packet["request_sha256"],
                    "raw_response_sha256": hashlib.sha256(
                        raw.encode("utf-8")
                    ).hexdigest(),
                    "fragment": fragment,
                    "contract_problems": problems,
                    "authorization": "none",
                    "executable": False,
                }
            )

    rendered = json.dumps(output, ensure_ascii=True, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(
            f"wrote {len(packets)} non-executable draft request(s) to "
            f"{args.output}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
