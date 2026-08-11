"""Dependency-free contract core for the synthetic ECDLP engineering lab."""

from .canonical import (
    StrictJSONError,
    canonical_json_bytes,
    derive_id,
    load_json,
    sha256_bytes,
    sha256_file,
    sha256_json,
    strict_loads,
)
from .contracts import (
    ContractIssue,
    ValidationContext,
    derive_campaign_id,
    derive_target_vector_id,
    validate_contract,
    validate_cross_record_bundle,
)

__all__ = [
    "ContractIssue",
    "StrictJSONError",
    "ValidationContext",
    "canonical_json_bytes",
    "derive_campaign_id",
    "derive_id",
    "derive_target_vector_id",
    "load_json",
    "sha256_bytes",
    "sha256_file",
    "sha256_json",
    "strict_loads",
    "validate_contract",
    "validate_cross_record_bundle",
]
