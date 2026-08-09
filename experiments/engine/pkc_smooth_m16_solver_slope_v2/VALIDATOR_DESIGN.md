# TASK-029 M16 solver-slope validator design

Date: 2026-08-09

Status: `DESIGN ONLY / UNIMPLEMENTED / NOT EXECUTABLE`

The current task needs no runtime validator because it authorizes zero compute.
This note defines the independent evidence that a future successor would need
before any solver authorization could be considered.

## Proposal integrity

A desk validator first recomputes:

- the current seed id and typed evidence digest;
- every source-commit evidence digest;
- the mechanism and validator design digests;
- the canonical prompt and evidence-context digests;
- the lexical premise fingerprint and structured mechanism signature;
- duplicate-mechanism and near-duplicate groups;
- all four mechanism assurance bindings.

It must reject the current design sentinels as executable identities and must
not reinterpret `specified_unproved` as evidence.

## Future primitive records

If a distinct proposal ever obtains dated authorization, one immutable record
per curve block, arm, fixed target, seed, and attempted relation must contain:

- curve, subgroup, generator, order, target, and primality certificates;
- committed `alpha_j, beta_j, R_j` and commitment ordering;
- the literal four-stage source chain for all 16 leaves;
- the target-specialized direct `S17` equation and canonical monomial order;
- every exceptional or identity-target branch;
- solver bytes, invocation, trace, failures, timeouts, matrices, and raw
  assignments;
- every lift, sign, multiplicity, rejection, and normalized relation row;
- independent rank, sparse-linear-algebra, candidate `z`, and `[z]G = Q`
  transcripts;
- exact primitive-operation vectors, peak memory, storage, total worker work,
  and preprocessing receipts;
- matched-control and generic square-root baseline records at equal success.

Producer summary fields such as `claimed_outcome`, `claimed_exponent`,
`claimed_relation`, `claimed_rank`, and `claimed_speedup` are non-authoritative.

## Independent recomputation

A future validator must be separately authored and must not import the producer
transformation or recovery implementation. From primitive records it must:

1. reconstruct every finite field, curve, subgroup, generator, and fixed `Q`;
2. verify each committed `R_j = [alpha_j]G + [beta_j]Q`;
3. evaluate all 48 transition, 16 terminal, and one `S17` equation members;
4. distinguish the literal source chain from any pointwise-equivalent circuit;
5. enumerate or otherwise certify every admitted exceptional branch;
6. recover signed base-field points and replay the target-bound group relation;
7. canonicalize rows and verify
   `sum_i c_ij lambda_i - beta_j z = alpha_j (mod q)`;
8. recompute duplicate collapse, rank, sparse linear algebra, and `[z]G = Q`;
9. expand every attack and baseline action into one frozen primitive-operation
   accounting system;
10. recompute relation-yield, censoring, and all causal-control comparisons;
11. mechanically apply a preregistered outcome matrix without deleting sizes,
    seeds, attempts, failures, timeouts, or controls.

Path, artifact, and source independence require separate evidence. None is
established by this design.

## Current deterministic disposition

The current package cannot reach a runtime decision because:

- no producer, direct-System-(4) solver, baseline, or validator exists;
- complete direct-system recovery equivalence is unproved;
- exceptional-complement orchestration is incomplete;
- relation independence, rank, sparse linear algebra, and recovery cost are
  unpriced;
- no exact generalized-root cost bound changes the complete asymptotic term;
- the permitted at-most-24-bit regime cannot identify an M16 exponent;
- the mechanism identity duplicates the immutable historical proposal;
- novelty is explicitly false.

The validator-facing result for this cycle is therefore a scoped abstention.
Review may classify the proposal as duplicate, missing an assured exact
mechanism, and blocked on complete cost. Those are scientific blockers, not
validation defects.

## Failure precedence for a future successor

1. `INVALID_IMPLEMENTATION`: exact replay disagrees; issue no scientific
   outcome.
2. `INAPPLICABLE`: no source-faithful safe regime and complete contract can be
   frozen.
3. `RESOURCE_EXHAUSTED`: a separately authorized immutable cap ends first.
4. `INCONCLUSIVE/ARTIFACT`: leakage, conditioning, or accounting breaks causal
   interpretation.
5. `FALSIFIED/KNOWN_REPRESENTATION_EFFECT`: matched controls reproduce the
   claimed effect with adequate precision.
6. `SUPPORTED/SUPPORTED_TOY_ONLY`: every exact gate and preregistered scaling
   criterion passes in an authorized toy scope.
7. `BOUNDED_NEGATIVE`: a complete cost or causal threshold fails with adequate
   precision.
8. `INCONCLUSIVE`: any other valid but underpowered result.

This file supplies no executable validator, candidate cap, or authorization.
