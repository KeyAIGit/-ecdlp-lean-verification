# Candidate evaluation framework

This directory is neutral infrastructure, not an active cryptanalytic
experiment. It is the completed `F-BENCHMARK-ORACLE` foundation and implements
the acceptance gate in `repo/ECDLP_DECISION_SUBSTRATE.json`.

## Contract

`candidate_run.schema.json` fixes the record shape. The dependency-free
`candidate_contract.py` adds semantic checks that JSON Schema alone cannot
express:

- route and threat-model identifiers resolve against the decision substrate;
- a real `candidate_run` is rejected unless its route explicitly authorizes it;
- plain single-target records cannot hide auxiliary inputs, interval promises,
  multiple targets, or reusable precomputation;
- online and offline work, memory, parallelism, amortization, and success
  probability are separate;
- target, result, environment, and whole research-record hashes match canonical
  JSON payloads; the whole-record hash also covers command, seed, validation,
  and every non-hash research field;
- undeclared fields, route/threat-model mismatches, and hypotheses not bound to
  their declared route are rejected;
- a small independent affine-curve oracle verifies the claimed scalar;
- the validator cannot claim independence while sharing decisive logic;
- subgeneric and practical claims require stronger fields and disclosure scope.

`framework_fixture` records exist only to test the gate. The v1 oracle is
deliberately limited to at most 32-bit prime fields, checks the exact base-point
order, requires `toy-*` curves, cannot claim a secp256k1 break, and does not
authorize a hypothesis run. A future exact-target validator must bind to the
verified secp256k1 parameters rather than silently widening this toy oracle.

## Commands

```text
python experiments/framework/check_candidate_run.py experiments/framework/fixtures/valid.json
python experiments/framework/test_framework.py
```

The EC oracle exposes verification only. It intentionally does not provide a
discrete-log search routine that candidate code could reuse.
