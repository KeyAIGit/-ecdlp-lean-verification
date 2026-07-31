# TORUS-PRIME-TRACE-CAUSALITY-001 preregistration

Status: `FROZEN / NOT YET EXECUTED`

Parent: `HYP-PPLUS1-TRACE-RELATION-001`

Active enabling hypothesis: `HYP-TORUS-CIRCUIT-FIDELITY-001`

Model: classical representation-aware, single target, synthetic/toy inputs.

## Claim

An odd-order norm-one trace factor base has a reduced, division-free,
bounded-fiber `O(log H)` circuit whose solver-relevant structural metrics
show a growing advantage over matched representations and controls.

## Competing explanations

- `H_NEW`: source coefficients create a growing causal structural gap.
- `H_KNOWN`: the circuit is an exact compact representation only.
- `H_ARTIFACT`: repeated roots, spurious auxiliary roots, selected
  parameters, or unmatched controls create the gap.
- `H_NULL`: exactness survives, but degree/width/yield costs erase the gap.

## Frozen inputs and controls

- public secp256k1 modulus and the divisors `7,322,137` and
  `45,422,601,869,677`;
- at least five frozen `p=3 mod 4` toy families with odd torus divisors;
- raw `D_H(X)-2`;
- explicit squarefree root polynomial;
- WCC-style power-of-two circuit;
- same-DAG randomized coefficients with seeds `0..19`;
- equal-cardinality matched root histograms;
- `j=0` and non-`j=0` curve-lift controls.

No real key, wallet, third-party target, Semaev solver, Groebner/F4 run, or
production key-recovery attempt is allowed.

## Metrics

- exact root mismatch and multiplicities;
- trace, auxiliary-witness, and curve-lift fiber histograms;
- gates, depth, fan-out, and primal-graph width;
- multihomogeneous/BKK proxy and eliminated degree;
- construction PFPO, time, and peak memory.

## Decision rules

Kill the current allocation if exactness fails, the circuit needs a
division/branch oracle, auxiliary fibers are not explicitly bounded, the
reduced circuit is not logarithmic, or no solver-relevant structural proxy
separates from every matched control.

Promote only to one separately preregistered toy-solver pilot if all exact
gates pass and at least one causal metric has a growing control-separated
gap on five or more sizes.  Promotion is not an attack claim.

Budget before review: four CPU-hours, 8 GiB peak RAM, zero GPU-hours, zero
production solver runs.

Required terminal states:

- `KILLED_IN_SCOPE`;
- `PAUSED_NO_CAUSAL_GAP`;
- `REJECTED_AS_ARTIFACT`;
- `PROMOTED_TO_TOY_SOLVER_PROPOSAL`.

Every terminal state must retain raw rows and the independent replay.
