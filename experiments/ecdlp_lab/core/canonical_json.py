"""Strict canonical JSON for ECDLP lab engineering fixtures.

The hashed semantic surface intentionally uses integers, strings, booleans,
null, arrays, and objects only. JSON floating-point literals are rejected;
non-integral semantic quantities must be decimal strings.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


class CanonicalJSONError(ValueError):
    """Raised when JSON is outside the lab canonical subset."""


_JSON_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _reject_duplicate_pairs(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CanonicalJSONError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise CanonicalJSONError(f"non-finite JSON number is forbidden: {token}")


def _reject_float(token: str) -> None:
    raise CanonicalJSONError(
        f"JSON floating-point literals are forbidden in hashed payloads: {token}"
    )


def _number_tokens_outside_strings(text: str) -> Iterable[str]:
    """Yield syntactically isolated JSON number tokens outside strings."""

    i = 0
    in_string = False
    escaped = False
    length = len(text)
    while i < length:
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            i += 1
            continue
        if ch == "-" or ch.isdigit():
            match = _JSON_NUMBER.match(text, i)
            if match is not None:
                yield match.group(0)
                i = match.end()
                continue
        i += 1


def _reject_negative_zero_lexemes(text: str) -> None:
    for token in _number_tokens_outside_strings(text):
        if not token.startswith("-"):
            continue
        unsigned = token[1:]
        mantissa = unsigned.split("e", 1)[0].split("E", 1)[0]
        digits = mantissa.replace(".", "")
        if digits and set(digits) == {"0"}:
            raise CanonicalJSONError(f"negative zero is forbidden: {token}")


def loads_strict(text: str) -> Any:
    """Parse the canonical JSON subset and reject duplicate keys and floats."""

    if not isinstance(text, str):
        raise TypeError("text must be str")
    _reject_negative_zero_lexemes(text)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
            parse_float=_reject_float,
        )
    except CanonicalJSONError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise CanonicalJSONError(str(exc)) from exc
    validate_canonical_types(value)
    return value


def load_strict(path: Path) -> Any:
    return loads_strict(path.read_text(encoding="utf-8"))


def validate_canonical_types(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, float):
        raise CanonicalJSONError(f"float at {path}; use an integer or decimal string")
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_canonical_types(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalJSONError(f"non-string object key at {path}")
            validate_canonical_types(item, f"{path}.{key}")
        return
    raise CanonicalJSONError(f"unsupported value type at {path}: {type(value).__name__}")


def dumps_canonical(value: Any) -> str:
    validate_canonical_types(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_bytes(value: Any) -> bytes:
    return dumps_canonical(value).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _HEX64.fullmatch(value) is not None
