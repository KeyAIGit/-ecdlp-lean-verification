# ECDLP lab P01 contracts

These nine contract families describe candidate-neutral engineering fixtures only.
Every record has:

```text
record_kind = lab_engineering_fixture
hypothesis_id = null
candidate_id = null
authorization_id = null
native_research_outcome = false
route_effect = none
retention_class = engineering_only
```

`contract_kind` selects one of the nine schemas in `contract_index.json`.
The JSON Schema files document the syntax. The dependency-free semantic gate is
`../core/contract_validation.py`; it additionally enforces digest-bound toy
inputs, the non-configurable 32-bit subgroup ceiling, anti-cheat separation,
source-independent validation, safe relative paths, deterministic identities,
and the prohibition on Engine conversion.

Canonical semantic JSON is UTF-8 with sorted keys and compact separators.
Duplicate keys, floating-point literals, NaN, infinity, and negative zero are
rejected. Non-integral hashed values use unsigned decimal strings.
