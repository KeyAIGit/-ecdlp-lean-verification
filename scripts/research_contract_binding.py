#!/usr/bin/env python3
"""Canonical bindings between reviewed proposal contracts and lifecycle snapshots."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


VALIDATOR_DESIGN_KEYS = (
    "raw_artifact_format",
    "recomputed_decisive_claim",
    "prohibited_producer_fields",
    "source_review_requirements",
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


def validator_design_projection(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        key: copy.deepcopy(contract.get(key))
        for key in VALIDATOR_DESIGN_KEYS
    }


def scientific_contract_digests(
    mechanism_contract: Any,
    prediction_contract: Any,
    cost_contract: Any,
    validator_contract: Any,
) -> dict[str, str]:
    """Hash reviewed scientific content while allowing validator implementation maturity."""

    return {
        "mechanism_contract_sha256": sha256_json(mechanism_contract),
        "prediction_contract_sha256": sha256_json(prediction_contract),
        "cost_contract_sha256": sha256_json(cost_contract),
        "validator_design_contract_sha256": sha256_json(
            validator_design_projection(validator_contract)
        ),
    }
