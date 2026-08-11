"""Fail-closed dependency-free validator for the lab's JSON Schema subset."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .canonical import canonical_json_bytes, load_json
from .issues import Issue

SUPPORTED_KEYWORDS = frozenset(
    {
        "$schema",
        "$id",
        "$defs",
        "$ref",
        "title",
        "description",
        "type",
        "const",
        "enum",
        "oneOf",
        "allOf",
        "not",
        "if",
        "then",
        "else",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "prefixItems",
        "minItems",
        "maxItems",
        "uniqueItems",
        "pattern",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minProperties",
        "maxProperties",
    }
)


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        # The lab's parsed semantic domain contains no floats. ``number`` is kept
        # only so schemas can describe integer-valued numeric constraints.
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _pointer_component(value: str) -> str:
    return value.replace("~1", "/").replace("~0", "~")


def _resolve_local_ref(root: dict[str, Any], reference: Any) -> Any | None:
    if reference == "#":
        return root
    if not isinstance(reference, str) or not reference.startswith("#/"):
        return None
    target: Any = root
    for raw in reference[2:].split("/"):
        component = _pointer_component(raw)
        if not isinstance(target, dict) or component not in target:
            return None
        target = target[component]
    return target if isinstance(target, (dict, bool)) else None


def schema_definition_issues(
    schema: Any,
    *,
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
    ref_stack: tuple[str, ...] = (),
) -> list[Issue]:
    if isinstance(schema, bool):
        return []
    if not isinstance(schema, dict):
        return [Issue("schema.definition.type", path, "schema node must be an object")]
    root = schema if root_schema is None else root_schema
    issues = [
        Issue("schema.keyword.unsupported", f"{path}.{key}", f"unsupported keyword {key}")
        for key in sorted(set(schema) - SUPPORTED_KEYWORDS)
    ]
    reference = schema.get("$ref")
    if reference is not None:
        resolved = _resolve_local_ref(root, reference)
        if resolved is None:
            issues.append(
                Issue(
                    "schema.ref.invalid",
                    f"{path}.$ref",
                    "only resolvable local '#/' references are allowed",
                )
            )
        elif reference in ref_stack:
            issues.append(Issue("schema.ref.cycle", f"{path}.$ref", "cyclic reference"))
        else:
            issues.extend(
                schema_definition_issues(
                    resolved,
                    root_schema=root,
                    path=f"{path}.$ref({reference})",
                    ref_stack=(*ref_stack, reference),
                )
            )
    for container in ("$defs", "properties"):
        children = schema.get(container)
        if children is not None and not isinstance(children, dict):
            issues.append(
                Issue("schema.definition.type", f"{path}.{container}", "must be an object")
            )
        elif isinstance(children, dict):
            for key, child in children.items():
                issues.extend(
                    schema_definition_issues(
                        child, root_schema=root, path=f"{path}.{container}.{key}"
                    )
                )
    for keyword in ("oneOf", "allOf", "prefixItems"):
        branches = schema.get(keyword)
        if branches is not None and not isinstance(branches, list):
            issues.append(
                Issue("schema.definition.type", f"{path}.{keyword}", "must be an array")
            )
        elif isinstance(branches, list):
            if keyword in {"oneOf", "allOf"} and not branches:
                issues.append(
                    Issue(
                        "schema.definition.empty",
                        f"{path}.{keyword}",
                        "must contain at least one schema",
                    )
                )
            for index, child in enumerate(branches):
                issues.extend(
                    schema_definition_issues(
                        child,
                        root_schema=root,
                        path=f"{path}.{keyword}[{index}]",
                    )
                )
    for keyword in ("if", "then", "else"):
        child = schema.get(keyword)
        if child is not None:
            issues.extend(
                schema_definition_issues(
                    child, root_schema=root, path=f"{path}.{keyword}"
                )
            )
    negated = schema.get("not")
    if negated is not None:
        issues.extend(
            schema_definition_issues(
                negated, root_schema=root, path=f"{path}.not"
            )
        )
    if ("then" in schema or "else" in schema) and "if" not in schema:
        issues.append(
            Issue(
                "schema.conditional.orphan",
                path,
                "then/else requires an if schema in the same object",
            )
        )
    for key in ("items", "additionalProperties"):
        child = schema.get(key)
        if isinstance(child, dict):
            issues.extend(
                schema_definition_issues(child, root_schema=root, path=f"{path}.{key}")
            )
        elif child is not None and not isinstance(child, bool):
            issues.append(
                Issue(
                    "schema.definition.type",
                    f"{path}.{key}",
                    "must be boolean or object",
                )
            )
    return issues


def _equal_json(left: Any, right: Any) -> bool:
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except ValueError:
        return False


def _pattern_matches(pattern: str, value: str) -> bool:
    """Apply JSON-Schema search semantics with a strict terminal ``$``.

    Python's ``$`` also matches immediately before a final newline, which would
    otherwise admit newline-suffixed digests and identifiers.  Draft schemas in
    this package use a terminal unescaped ``$`` to mean the actual end of the
    JSON string, so translate that one anchor to Python's strict ``\\Z`` while
    preserving search semantics for all other patterns.
    """

    trailing_backslashes = 0
    for character in reversed(pattern[:-1]) if pattern.endswith("$") else ():
        if character != "\\":
            break
        trailing_backslashes += 1
    if pattern.endswith("$") and trailing_backslashes % 2 == 0:
        pattern = pattern[:-1] + r"\Z"
    return re.search(pattern, value) is not None


def validate_schema(
    value: Any,
    schema: dict[str, Any] | bool,
    *,
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
    ref_stack: tuple[str, ...] = (),
) -> list[Issue]:
    """Validate a value only after the caller has linted the schema definition."""

    if schema is True:
        return []
    if schema is False:
        return [Issue("schema.false", path, "value is forbidden by a false schema")]
    if not isinstance(schema, dict):
        return [Issue("schema.definition.type", path, "schema node must be an object or boolean")]

    root = schema if root_schema is None else root_schema
    issues: list[Issue] = []
    reference = schema.get("$ref")
    if reference is not None:
        resolved = _resolve_local_ref(root, reference)
        if resolved is None:
            return [Issue("schema.ref.invalid", path, "unresolvable or external reference")]
        if reference in ref_stack:
            return [Issue("schema.ref.cycle", path, "cyclic reference")]
        issues.extend(
            validate_schema(
                value,
                resolved,
                root_schema=root,
                path=path,
                ref_stack=(*ref_stack, reference),
            )
        )

    if "oneOf" in schema:
        branch_results = [
            validate_schema(value, branch, root_schema=root, path=path)
            for branch in schema["oneOf"]
        ]
        matches = sum(not result for result in branch_results)
        if matches != 1:
            issues.append(
                Issue(
                    "schema.one_of",
                    path,
                    f"value must match exactly one branch, matched {matches}",
                )
            )

    for branch in schema.get("allOf", []):
        issues.extend(validate_schema(value, branch, root_schema=root, path=path))

    if "not" in schema and not validate_schema(
        value, schema["not"], root_schema=root, path=path
    ):
        issues.append(Issue("schema.not", path, "value matches a forbidden schema"))

    condition = schema.get("if")
    if condition is not None:
        condition_matches = not validate_schema(
            value, condition, root_schema=root, path=path
        )
        selected = schema.get("then") if condition_matches else schema.get("else")
        if selected is not None:
            issues.extend(validate_schema(value, selected, root_schema=root, path=path))

    expected = schema.get("type")
    if expected is not None:
        types = [expected] if isinstance(expected, str) else expected
        if not isinstance(types, list) or not types or not all(isinstance(item, str) for item in types):
            return [Issue("schema.type.definition", path, "invalid type declaration")]
        if not any(_type_matches(value, item) for item in types):
            return [Issue("schema.type", path, f"expected {expected!r}")]

    if "const" in schema and not _equal_json(value, schema["const"]):
        issues.append(Issue("schema.const", path, "value differs from required constant"))
    if "enum" in schema:
        choices = schema["enum"]
        if not isinstance(choices, list) or not any(_equal_json(value, item) for item in choices):
            issues.append(Issue("schema.enum", path, "value is not an allowed enum member"))

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            issues.append(Issue("schema.string.min_length", path, "string is too short"))
        maximum = schema.get("maxLength")
        if isinstance(maximum, int) and len(value) > maximum:
            issues.append(Issue("schema.string.max_length", path, "string is too long"))
        pattern = schema.get("pattern")
        if isinstance(pattern, str):
            try:
                matches = _pattern_matches(pattern, value)
            except re.error as error:
                issues.append(Issue("schema.pattern.invalid", path, str(error)))
            else:
                if not matches:
                    issues.append(Issue("schema.pattern", path, "string does not match pattern"))

    if isinstance(value, int) and not isinstance(value, bool):
        for key, comparison, code in (
            ("minimum", lambda a, b: a < b, "schema.number.minimum"),
            ("maximum", lambda a, b: a > b, "schema.number.maximum"),
            ("exclusiveMinimum", lambda a, b: a <= b, "schema.number.exclusive_minimum"),
            ("exclusiveMaximum", lambda a, b: a >= b, "schema.number.exclusive_maximum"),
        ):
            bound = schema.get(key)
            if isinstance(bound, int) and not isinstance(bound, bool) and comparison(value, bound):
                issues.append(Issue(code, path, f"number violates {key}"))

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            issues.append(Issue("schema.array.min_items", path, "array has too few items"))
        maximum = schema.get("maxItems")
        if isinstance(maximum, int) and len(value) > maximum:
            issues.append(Issue("schema.array.max_items", path, "array has too many items"))
        if schema.get("uniqueItems") is True:
            seen: set[bytes] = set()
            for item in value:
                encoded = canonical_json_bytes(item)
                if encoded in seen:
                    issues.append(Issue("schema.array.unique", path, "array items are not unique"))
                    break
                seen.add(encoded)
        prefix_schemas = schema.get("prefixItems", [])
        if isinstance(prefix_schemas, list):
            for index, child_schema in enumerate(prefix_schemas[: len(value)]):
                issues.extend(
                    validate_schema(
                        value[index],
                        child_schema,
                        root_schema=root,
                        path=f"{path}[{index}]",
                    )
                )
        item_schema = schema.get("items")
        prefix_count = len(prefix_schemas) if isinstance(prefix_schemas, list) else 0
        if item_schema is False and isinstance(prefix_schemas, list):
            # The lab uses prefixItems+items:false solely for fixed-size tuples.
            # Enforcing both lower and upper bounds prevents truncated EC points.
            if len(value) != prefix_count:
                issues.append(
                    Issue(
                        "schema.array.tuple_length",
                        path,
                        f"array must contain exactly {prefix_count} tuple items",
                    )
                )
        elif item_schema is False and len(value) > 0:
            issues.append(Issue("schema.array.items", path, "array items are forbidden"))
        elif isinstance(item_schema, (dict, bool)):
            for index, item in enumerate(value[prefix_count:], start=prefix_count):
                issues.extend(
                    validate_schema(
                        item, item_schema, root_schema=root, path=f"{path}[{index}]"
                    )
                )

    if isinstance(value, dict):
        minimum = schema.get("minProperties")
        maximum = schema.get("maxProperties")
        if isinstance(minimum, int) and len(value) < minimum:
            issues.append(Issue("schema.object.min_properties", path, "too few properties"))
        if isinstance(maximum, int) and len(value) > maximum:
            issues.append(Issue("schema.object.max_properties", path, "too many properties"))
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    issues.append(
                        Issue("schema.required", f"{path}.{key}", "required property is missing")
                    )
        if isinstance(properties, dict):
            if schema.get("additionalProperties") is False:
                for key in value:
                    if key not in properties:
                        issues.append(
                            Issue("schema.additional_property", f"{path}.{key}", "unknown property")
                        )
            additional = schema.get("additionalProperties")
            if isinstance(additional, dict):
                for key, child in value.items():
                    if key not in properties:
                        issues.extend(
                            validate_schema(
                                child,
                                additional,
                                root_schema=root,
                                path=f"{path}.{key}",
                            )
                        )
            for key, child_schema in properties.items():
                if key in value and isinstance(child_schema, dict):
                    issues.extend(
                        validate_schema(
                            value[key],
                            child_schema,
                            root_schema=root,
                            path=f"{path}.{key}",
                        )
                    )
    return issues


def load_and_validate_schema(
    value: Any, schema_path: Path | str
) -> tuple[dict[str, Any], list[Issue]]:
    schema = load_json(schema_path)
    if not isinstance(schema, dict):
        return {}, [Issue("schema.root", "$", "schema document must be an object")]
    definition = schema_definition_issues(schema)
    if definition:
        return schema, definition
    return schema, validate_schema(value, schema)
