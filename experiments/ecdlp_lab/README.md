# ECDLP engineering lab

`experiments.ecdlp_lab` is a bounded, offline laboratory for testing ECDLP
implementations on generated toy fixtures. Its records are engineering
fixtures, not scientific outcomes, hypotheses, candidates, authorizations, or
evidence of a secp256k1 shortcut.

## Boundary

Every lab record uses `schema_version: 1`,
`record_kind: lab_engineering_fixture`, one of the nine registered
`contract_kind` values, `native_research_outcome: false`,
`route_effect: none`, and `retention_class: engineering_only`. Candidate,
hypothesis, and authorization identifiers are null. A clean, independently
validated run may retain an engineering artifact; it still cannot be converted
to an Engine run or written below Engine, scientific-data, route-state,
hypothesis-registry, proof-ledger, or formal-source destinations.

The hard safety ceiling is a toy subgroup order of at most 32 bits. The
validators reject larger subgroups, the exact secp256k1 field/order constants,
external targets, unknown catalog/vector digests, target secrets in method
requests, shared target/algorithm seeds, and hidden precomputation. No
configuration field can raise that ceiling.

Artifact references are repository-relative POSIX paths. Absolute paths,
backslashes, `..`, symlink escapes, and protected destinations are rejected
before any artifact is opened or created.

## Contracts

The version-1 schema corpus covers:

- `campaign_config_v1`
- `target_vector_v1`
- `work_unit_v1`
- `method_request_v1`
- `method_result_v1`
- `telemetry_v1`
- `validation_receipt_v1`
- `analysis_summary_v1`
- `artifact_ref_v1`

JSON is parsed strictly and encoded canonically: UTF-8, sorted keys, compact
separators, and no duplicate keys, floating-point values, non-finite values, or
negative zero. Unknown fields are rejected. Semantic identifiers and hashes are
derived from canonical semantic bytes; observational telemetry is kept outside
those digests.

## Offline verification

Run the dependency-free P01 checks from the repository root:

```bash
python3 -m unittest discover -s experiments/ecdlp_lab/tests -p 'test_*.py'
python3 -m experiments.ecdlp_lab.core.capabilities --json
python3 -m experiments.ecdlp_lab.core.validate --offline
python3 experiments/framework/test_framework.py
python3 scripts/check_automation_inventory.py
```

The path-scoped `lab-ci.yml` workflow runs only these bounded Python checks. It
does not install packages, contact services, run Lean or Sage, compile native
backends, spend external budget, schedule experiments, or authorize scientific
work. Optional Sage and native backends must report an unavailable/error state
until their real, separately gated tests run; missing capability is never a
synthetic pass.
