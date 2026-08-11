"""Strict JSON parsing and canonical content identities for the lab.

Semantic lab payloads deliberately contain no JSON floating-point values. Values
that are not integers are represented by contract-validated decimal strings.
This makes negative zero and platform-dependent float rendering impossible in a
hashed payload.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

DEFAULT_MAX_JSON_BYTES = 8 * 1024 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class StrictJSONError(ValueError):
    """Raised when bytes are not in the lab's strict JSON value domain."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_int(token: str) -> int:
    if token == "-0":
        raise StrictJSONError("negative zero is forbidden")
    return int(token, 10)


def _reject_float(token: str) -> float:
    raise StrictJSONError(f"JSON floating-point values are forbidden: {token}")


def _reject_constant(token: str) -> None:
    raise StrictJSONError(f"non-finite JSON number is forbidden: {token}")


def strict_loads(payload: str | bytes, *, label: str = "JSON payload") -> Any:
    """Parse JSON while retaining errors ordinary ``json.loads`` erases."""

    if isinstance(payload, bytes):
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise StrictJSONError(f"{label} is not UTF-8: {error}") from error
    elif isinstance(payload, str):
        text = payload
    else:
        raise TypeError("strict_loads accepts str or bytes")
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_int=_parse_int,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except StrictJSONError:
        raise
    except (json.JSONDecodeError, UnicodeError) as error:
        raise StrictJSONError(f"{label} is invalid JSON: {error}") from error


def load_json(
    path: Path | str, *, max_bytes: int = DEFAULT_MAX_JSON_BYTES
) -> Any:
    """Read one bounded UTF-8 JSON file through :func:`strict_loads`."""

    candidate = Path(path)
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("max_bytes must be a positive integer")
    try:
        size = candidate.stat().st_size
    except OSError as error:
        raise StrictJSONError(f"{candidate}: cannot stat JSON file: {error}") from error
    if size > max_bytes:
        raise StrictJSONError(
            f"{candidate}: JSON file exceeds {max_bytes} byte input limit"
        )
    try:
        payload = candidate.read_bytes()
    except OSError as error:
        raise StrictJSONError(f"{candidate}: cannot read JSON file: {error}") from error
    return strict_loads(payload, label=str(candidate))


def _assert_canonical_domain(value: Any, *, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise StrictJSONError(f"{path}: floating-point values are forbidden")
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_canonical_domain(child, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise StrictJSONError(f"{path}: JSON object key is not a string")
            _assert_canonical_domain(child, path=f"{path}.{key}")
        return
    raise StrictJSONError(f"{path}: unsupported JSON value type {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    """Return compact, sorted-key UTF-8 JSON with no trailing newline."""

    _assert_canonical_domain(value)
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return rendered.encode("utf-8", errors="strict")
    except (UnicodeError, ValueError, TypeError) as error:
        raise StrictJSONError(f"value cannot be canonically encoded: {error}") from error


def sha256_bytes(payload: bytes) -> str:
    if not isinstance(payload, bytes):
        raise TypeError("sha256_bytes requires bytes")
    return hashlib.sha256(payload).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_without(value: dict[str, Any], excluded: Iterable[str]) -> dict[str, Any]:
    excluded_set = set(excluded)
    return {key: child for key, child in value.items() if key not in excluded_set}


def derive_id(
    prefix: str,
    value: dict[str, Any],
    *,
    excluded: Iterable[str] = (),
    digest_hex_chars: int = 32,
) -> str:
    """Derive a stable semantic identifier without a self-reference."""

    if not isinstance(prefix, str) or re.fullmatch(r"[A-Z][A-Z0-9-]*-", prefix) is None:
        raise ValueError("identifier prefix must be uppercase ASCII and end in '-'")
    if (
        isinstance(digest_hex_chars, bool)
        or not isinstance(digest_hex_chars, int)
        or not 8 <= digest_hex_chars <= 64
    ):
        raise ValueError("digest_hex_chars must be an integer in [8, 64]")
    digest = sha256_json(payload_without(value, excluded))
    return prefix + digest[:digest_hex_chars].upper()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None
